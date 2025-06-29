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
    
    def __init__(self, tumorboard_base_path=None):
        # Determine correct database path based on tumorboard base path
        if tumorboard_base_path is not None:
            db_path = tumorboard_base_path / "__SQLite_database" / "master_tumorboard.db"
        else:
            db_path = None  # Use default user home path
        
        self.db = TumorboardDatabase(db_path=db_path)
        self.tumorboard_base_path = tumorboard_base_path
    
    def export_dashboard_data(self, output_path=None):
        """Export all data needed for dashboard as JSON"""
        if output_path is None:
            # Use tumorboard base path if available, otherwise fall back to user home
            if self.tumorboard_base_path is not None:
                output_path = self.tumorboard_base_path / "__SQLite_database" / "dashboard_data.json"
            else:
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
                
                # Aufgebot data
                aufgebot_data = self._get_aufgebot_data(conn)
                
                dashboard_data = {
                    'generated_at': datetime.now().isoformat(),
                    'key_metrics': key_metrics,
                    'tumorboard_stats': tumorboard_stats,
                    'temporal_data': temporal_data,
                    'radiotherapy_data': radiotherapy_data,
                    'study_enrollment_data': study_enrollment_data,
                    'icd_data': icd_analysis_data,
                    'aufgebot_data': aufgebot_data
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
    
    def _get_aufgebot_data(self, conn):
        """Get Aufgebot (call type) statistics"""
        cursor = conn.cursor()
        
        # All patients with radiotherapy = "Ja" and aufgebot data
        cursor.execute('''
            SELECT 
                CASE 
                    WHEN aufgebot_type = '-' OR aufgebot_type IS NULL OR aufgebot_type = '' 
                    THEN 'Nicht spezifiziert'
                    ELSE aufgebot_type 
                END as category,
                COUNT(*) as count
            FROM patients 
            WHERE radiotherapy_indicated = 'Ja'
            GROUP BY 
                CASE 
                    WHEN aufgebot_type = '-' OR aufgebot_type IS NULL OR aufgebot_type = '' 
                    THEN 'Nicht spezifiziert'
                    ELSE aufgebot_type 
                END
            ORDER BY count DESC
        ''')
        
        all_results = cursor.fetchall()
        
        # Only patients with specified aufgebot type
        cursor.execute('''
            SELECT 
                aufgebot_type as category,
                COUNT(*) as count
            FROM patients 
            WHERE radiotherapy_indicated = 'Ja' 
            AND aufgebot_type IS NOT NULL 
            AND aufgebot_type NOT IN ('-', '')
            GROUP BY aufgebot_type
            ORDER BY 
                CASE aufgebot_type
                    WHEN 'Kat I' THEN 1
                    WHEN 'Kat II' THEN 2
                    WHEN 'Kat III' THEN 3
                    ELSE 4
                END
        ''')
        
        specified_results = cursor.fetchall()
        
        # Aufgebot by tumorboard type
        cursor.execute('''
            SELECT 
                e.name as tumorboard_type,
                CASE 
                    WHEN p.aufgebot_type = '-' OR p.aufgebot_type IS NULL OR p.aufgebot_type = '' 
                    THEN 'Nicht spezifiziert'
                    ELSE p.aufgebot_type 
                END as category,
                COUNT(*) as count
            FROM patients p
            JOIN tumorboard_sessions s ON p.session_id = s.id
            JOIN tumorboard_entities e ON s.entity_id = e.id
            WHERE p.radiotherapy_indicated = 'Ja'
            GROUP BY e.name, 
                CASE 
                    WHEN p.aufgebot_type = '-' OR p.aufgebot_type IS NULL OR p.aufgebot_type = '' 
                    THEN 'Nicht spezifiziert'
                    ELSE p.aufgebot_type 
                END
            ORDER BY e.name, count DESC
        ''')
        
        by_tumorboard_results = cursor.fetchall()
        
        return {
            'all_patients': [
                {'category': row[0], 'count': row[1]}
                for row in all_results
            ],
            'specified_only': [
                {'category': row[0], 'count': row[1]}
                for row in specified_results
            ],
            'by_tumorboard': [
                {
                    'tumorboard_type': row[0],
                    'category': row[1],
                    'count': row[2]
                }
                for row in by_tumorboard_results
            ]
        }


def generate_dashboard_data(tumorboard_base_path=None):
    """Generate dashboard data JSON file"""
    # Determine correct tumorboard base path if not provided
    if tumorboard_base_path is None:
        # Try K: first, fall back to user home
        k_path = Path("K:/RAO_Projekte/App/tumorboards")
        if k_path.exists() and k_path.is_dir():
            tumorboard_base_path = k_path
        else:
            tumorboard_base_path = Path.home() / "tumorboards"
    
    exporter = DashboardDataExporter(tumorboard_base_path)
    return exporter.export_dashboard_data()


def test_aufgebot_mapping():
    """Test function to validate Aufgebot data mapping"""
    try:
        from .database_utils import TumorboardDatabase
        
        db = TumorboardDatabase()
        
        # Test the normalize function
        test_values = [
            "Kat I: In 1-3 Tagen ohne Konsil",
            "Kat II: In 5-7 Tagen ohne Konsil", 
            "Kat III: Nach Eingang des Konsils",
            "Kat I",
            "Kat II",
            "Kat III",
            "-",
            "",
            None,
            "Invalid Value"
        ]
        
        print("Testing Aufgebot normalization:")
        for value in test_values:
            normalized = db._normalize_aufgebot_type(value)
            print(f"'{value}' -> '{normalized}'")
        
        # Test dashboard data export
        exporter = DashboardDataExporter()
        data = exporter.export_dashboard_data()
        
        if data:
            import json
            with open(data, 'r', encoding='utf-8') as f:
                dashboard_data = json.load(f)
            
            print("\nAufgebot data in dashboard:")
            if 'aufgebot_data' in dashboard_data:
                print(json.dumps(dashboard_data['aufgebot_data'], indent=2, ensure_ascii=False))
            else:
                print("No aufgebot_data found in dashboard")
        
        return True
        
    except Exception as e:
        print(f"Test failed: {e}")
        return False


if __name__ == "__main__":
    test_aufgebot_mapping() 