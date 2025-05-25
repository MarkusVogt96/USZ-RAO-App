import sqlite3
import json
import logging
from pathlib import Path
from datetime import datetime
from .database_utils import TumorboardDatabase

class DashboardDataExporter:
    """Export database data for interactive dashboard"""
    
    def __init__(self):
        self.db = TumorboardDatabase()
    
    def export_dashboard_data(self, output_path=None):
        """Export all data needed for dashboard as JSON"""
        if output_path is None:
            output_path = Path.home() / "tumorboards" / "dashboard_data.json"
        
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
                
                # ICD code data
                icd_data = self._get_icd_data(conn)
                
                # Patient flow data
                patient_flow = self._get_patient_flow_data(conn)
                
                dashboard_data = {
                    'generated_at': datetime.now().isoformat(),
                    'key_metrics': key_metrics,
                    'tumorboard_stats': tumorboard_stats,
                    'temporal_data': temporal_data,
                    'radiotherapy_data': radiotherapy_data,
                    'icd_data': icd_data,
                    'patient_flow': patient_flow
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
    
    def _get_icd_data(self, conn):
        """Get ICD code statistics"""
        cursor = conn.cursor()
        
        # Top ICD codes
        cursor.execute('''
            SELECT 
                icd_code,
                COUNT(DISTINCT unique_key) as total_cases,
                COUNT(DISTINCT patient_number) as unique_patients
            FROM patients 
            WHERE icd_code IS NOT NULL AND icd_code != '' AND icd_code != '-'
            GROUP BY icd_code
            ORDER BY total_cases DESC
            LIMIT 15
        ''')
        
        top_icd_results = cursor.fetchall()
        
        # ICD codes by tumorboard
        cursor.execute('''
            SELECT 
                e.name as tumorboard_type,
                p.icd_code,
                COUNT(DISTINCT p.unique_key) as total_cases
            FROM patients p
            JOIN tumorboard_sessions s ON p.session_id = s.id
            JOIN tumorboard_entities e ON s.entity_id = e.id
            WHERE p.icd_code IS NOT NULL AND p.icd_code != '' AND p.icd_code != '-'
            GROUP BY e.name, p.icd_code
            ORDER BY e.name, total_cases DESC
        ''')
        
        icd_by_tb_results = cursor.fetchall()
        
        return {
            'top_codes': [
                {
                    'icd_code': row[0],
                    'total_cases': row[1],
                    'unique_patients': row[2]
                }
                for row in top_icd_results
            ],
            'by_tumorboard': [
                {
                    'tumorboard_type': row[0],
                    'icd_code': row[1],
                    'total_cases': row[2]
                }
                for row in icd_by_tb_results
            ]
        }
    
    def _get_patient_flow_data(self, conn):
        """Get patient flow data for Sankey diagram"""
        cursor = conn.cursor()
        
        # Patient flow: Tumorboard -> Radiotherapy Decision
        cursor.execute('''
            SELECT 
                e.name as tumorboard_type,
                CASE 
                    WHEN p.radiotherapy_indicated = '-' OR p.radiotherapy_indicated IS NULL OR p.radiotherapy_indicated = '' 
                    THEN 'Nicht besprochen'
                    ELSE p.radiotherapy_indicated 
                END as radiotherapy_decision,
                COUNT(DISTINCT p.unique_key) as count
            FROM patients p
            JOIN tumorboard_sessions s ON p.session_id = s.id
            JOIN tumorboard_entities e ON s.entity_id = e.id
            GROUP BY e.name, radiotherapy_decision
            HAVING count > 0
            ORDER BY e.name, count DESC
        ''')
        
        flow_results = cursor.fetchall()
        
        return [
            {
                'source': row[0],
                'target': row[1],
                'value': row[2]
            }
            for row in flow_results
        ]


def generate_dashboard_data():
    """Generate dashboard data JSON file"""
    exporter = DashboardDataExporter()
    return exporter.export_dashboard_data() 