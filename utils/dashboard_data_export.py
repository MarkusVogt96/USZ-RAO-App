import sqlite3
import json
import logging
from pathlib import Path
from datetime import datetime
import sys
import os

# Add parent directory to Python path for imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from utils.database_utils import TumorboardDatabase

class DashboardDataExporter:
    """Export database data for interactive dashboard"""
    
    def __init__(self):
        self.db = TumorboardDatabase()
    
    def export_dashboard_data(self, output_path=None):
        """Export all data needed for dashboard as JSON"""
        if output_path is None:
            output_path = Path.home() / "tumorboards" / "__SQLite_database" / "dashboard_data.json"
        
        try:
            with sqlite3.connect(self.db.db_path) as conn:
                # Key metrics
                key_metrics = self._get_key_metrics(conn)
                
                # Tumorboard statistics
                tumorboard_stats = self._get_tumorboard_stats(conn)
                
                # Temporal data
                temporal_data = self._get_temporal_data(conn)
                
                # Radiotherapy data
                radiotherapy_data = self._get_radiotherapy_data(conn)
                
                # Study enrollment data
                study_enrollment_data = self._get_study_enrollment_data(conn)
                
                # ICD analysis data
                icd_analysis_data = self._get_icd_analysis_data(conn)
                
                dashboard_data = {
                    'generated_at': datetime.now().isoformat(),
                    'key_metrics': key_metrics,
                    'tumorboard_stats': tumorboard_stats,
                    'temporal_data': temporal_data,
                    'radiotherapy_data': radiotherapy_data,
                    'study_enrollment_data': study_enrollment_data,
                    'icd_data': icd_analysis_data
                }
                
                # Write JSON file
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(dashboard_data, f, ensure_ascii=False, indent=2)
                
                logging.info(f"Dashboard data exported to: {output_path}")
                return str(output_path)
                
        except Exception as e:
            logging.error(f"Error exporting dashboard data: {e}")
            return None
    
    def _get_key_metrics(self, conn):
        """Get key metrics for dashboard header"""
        cursor = conn.cursor()
        
        # Basic counts
        cursor.execute('''
            SELECT 
                COUNT(DISTINCT e.name) as tumorboard_types,
                COUNT(DISTINCT s.id) as total_sessions,
                COUNT(DISTINCT p.patient_number) as unique_patients,
                COUNT(DISTINCT p.unique_key) as total_cases
            FROM tumorboard_entities e
            LEFT JOIN tumorboard_sessions s ON e.id = s.entity_id
            LEFT JOIN patients p ON s.id = p.session_id
        ''')
        
        result = cursor.fetchone()
        return {
            'tumorboard_types': result[0] or 0,
            'total_sessions': result[1] or 0,
            'unique_patients': result[2] or 0,
            'total_cases': result[3] or 0
        }
    
    def _get_tumorboard_stats(self, conn):
        """Get statistics by tumorboard type"""
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                e.name as tumorboard_type,
                COUNT(DISTINCT s.id) as sessions,
                COUNT(DISTINCT p.patient_number) as unique_patients,
                COUNT(DISTINCT p.unique_key) as total_cases
            FROM tumorboard_entities e
            LEFT JOIN tumorboard_sessions s ON e.id = s.entity_id
            LEFT JOIN patients p ON s.id = p.session_id
            GROUP BY e.id, e.name
            ORDER BY total_cases DESC
        ''')
        
        results = cursor.fetchall()
        return [
            {
                'name': row[0],
                'sessions': row[1],
                'unique_patients': row[2],
                'total_cases': row[3]
            }
            for row in results if row[3] > 0  # Only include tumorboards with cases
        ]
    
    def _get_temporal_data(self, conn):
        """Get temporal data for time series charts"""
        cursor = conn.cursor()
        
        # Monthly data for last 12 months
        cursor.execute('''
            SELECT 
                strftime('%Y-%m', s.session_date) as month,
                COUNT(DISTINCT s.id) as sessions,
                COUNT(DISTINCT p.patient_number) as unique_patients,
                COUNT(DISTINCT p.unique_key) as total_cases
            FROM tumorboard_sessions s
            LEFT JOIN patients p ON s.id = p.session_id
            WHERE s.session_date >= date('now', '-12 months')
            GROUP BY strftime('%Y-%m', s.session_date)
            ORDER BY month
        ''')
        
        monthly_results = cursor.fetchall()
        
        # Weekly data for last 8 weeks
        cursor.execute('''
            SELECT 
                strftime('%Y-W%W', s.session_date) as week,
                COUNT(DISTINCT s.id) as sessions,
                COUNT(DISTINCT p.patient_number) as unique_patients,
                COUNT(DISTINCT p.unique_key) as total_cases
            FROM tumorboard_sessions s
            LEFT JOIN patients p ON s.id = p.session_id
            WHERE s.session_date >= date('now', '-8 weeks')
            GROUP BY strftime('%Y-W%W', s.session_date)
            ORDER BY week
        ''')
        
        weekly_results = cursor.fetchall()
        
        return {
            'monthly': [
                {
                    'month': row[0],
                    'sessions': row[1],
                    'unique_patients': row[2],
                    'total_cases': row[3]
                }
                for row in monthly_results
            ],
            'weekly': [
                {
                    'week': row[0],
                    'sessions': row[1],
                    'unique_patients': row[2],
                    'total_cases': row[3]
                }
                for row in weekly_results
            ]
        }
    
    def _get_radiotherapy_data(self, conn):
        """Get radiotherapy statistics"""
        cursor = conn.cursor()
        
        # All patients
        cursor.execute('''
            SELECT 
                CASE 
                    WHEN radiotherapy_indicated = '-' OR radiotherapy_indicated IS NULL OR radiotherapy_indicated = '' 
                    THEN 'Nicht besprochen'
                    ELSE radiotherapy_indicated 
                END as status,
                COUNT(*) as count
            FROM patients 
            GROUP BY 
                CASE 
                    WHEN radiotherapy_indicated = '-' OR radiotherapy_indicated IS NULL OR radiotherapy_indicated = '' 
                    THEN 'Nicht besprochen'
                    ELSE radiotherapy_indicated 
                END
            ORDER BY count DESC
        ''')
        
        all_results = cursor.fetchall()
        
        # Only discussed patients
        cursor.execute('''
            SELECT 
                radiotherapy_indicated as status,
                COUNT(*) as count
            FROM patients 
            WHERE radiotherapy_indicated NOT IN ('-', '') AND radiotherapy_indicated IS NOT NULL
            GROUP BY radiotherapy_indicated
            ORDER BY count DESC
        ''')
        
        discussed_results = cursor.fetchall()
        
        return {
            'all_patients': [
                {'status': row[0], 'count': row[1]}
                for row in all_results
            ],
            'discussed_only': [
                {'status': row[0], 'count': row[1]}
                for row in discussed_results
            ]
        }
    
    def _get_study_enrollment_data(self, conn):
        """Get study enrollment data"""
        cursor = conn.cursor()
        
        # Study enrollment data
        cursor.execute('''
            SELECT 
                study_enrollment as status,
                COUNT(*) as count
            FROM patients 
            WHERE study_enrollment IS NOT NULL
            GROUP BY study_enrollment
            ORDER BY count DESC
        ''')
        
        results = cursor.fetchall()
        
        return [
            {'status': row[0], 'count': row[1]}
            for row in results
        ]
    
    def _get_icd_analysis_data(self, conn):
        """Get ICD analysis data using families instead of individual codes"""
        from utils.icd10_mapping import get_icd_family_description
        
        cursor = conn.cursor()
        
        # Top ICD families (aggregated from individual codes)
        cursor.execute('''
            SELECT 
                icd_family,
                COUNT(DISTINCT unique_key) as total_cases,
                COUNT(DISTINCT patient_number) as unique_patients
            FROM patients 
            WHERE icd_family IS NOT NULL AND icd_family != '' AND icd_family != '-'
            GROUP BY icd_family
            ORDER BY total_cases DESC
            LIMIT 20
        ''')
        
        top_families_results = cursor.fetchall()
        
        # ICD families by tumorboard
        cursor.execute('''
            SELECT 
                e.name as tumorboard_type,
                p.icd_family,
                COUNT(DISTINCT p.unique_key) as total_cases,
                COUNT(DISTINCT p.patient_number) as unique_patients
            FROM patients p
            JOIN tumorboard_sessions s ON p.session_id = s.id
            JOIN tumorboard_entities e ON s.entity_id = e.id
            WHERE p.icd_family IS NOT NULL AND p.icd_family != '' AND p.icd_family != '-'
            GROUP BY e.name, p.icd_family
            ORDER BY e.name, total_cases DESC
        ''')
        
        by_tumorboard_results = cursor.fetchall()
        
        return {
            'top_codes': [
                {
                    'icd_family': row[0],
                    'description': get_icd_family_description(row[0]),
                    'total_cases': row[1],
                    'unique_patients': row[2]
                }
                for row in top_families_results
            ],
            'by_tumorboard': [
                {
                    'tumorboard_type': row[0],
                    'icd_family': row[1],
                    'description': get_icd_family_description(row[1]),
                    'total_cases': row[2],
                    'unique_patients': row[3]
                }
                for row in by_tumorboard_results
            ]
        }


def generate_dashboard_data():
    """Generate dashboard data JSON file"""
    exporter = DashboardDataExporter()
    return exporter.export_dashboard_data() 