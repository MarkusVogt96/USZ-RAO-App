import pandas as pd
import sqlite3
import logging
from pathlib import Path
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns
from .database_utils import TumorboardDatabase

class TumorboardAnalyzer:
    """Data analysis tool for tumorboard database"""
    
    def __init__(self):
        self.db = TumorboardDatabase()
    
    def get_patient_statistics(self):
        """Get comprehensive patient statistics"""
        try:
            with sqlite3.connect(self.db.db_path) as conn:
                # Basic counts
                basic_stats = pd.read_sql_query('''
                    SELECT 
                        COUNT(DISTINCT e.name) as total_tumorboard_types,
                        COUNT(DISTINCT s.id) as total_sessions,
                        COUNT(DISTINCT p.patient_number) as unique_patients,
                        COUNT(DISTINCT p.unique_key) as total_patient_cases
                    FROM tumorboard_entities e
                    LEFT JOIN tumorboard_sessions s ON e.id = s.entity_id
                    LEFT JOIN patients p ON s.id = p.session_id
                ''', conn)
                
                # Patients by tumorboard type
                by_tumorboard = pd.read_sql_query('''
                    SELECT 
                        e.name as tumorboard_type,
                        COUNT(DISTINCT s.id) as sessions_count,
                        COUNT(DISTINCT p.patient_number) as unique_patients,
                        COUNT(DISTINCT p.unique_key) as total_patient_cases
                    FROM tumorboard_entities e
                    LEFT JOIN tumorboard_sessions s ON e.id = s.entity_id
                    LEFT JOIN patients p ON s.id = p.session_id
                    GROUP BY e.id, e.name
                    ORDER BY total_patient_cases DESC
                ''', conn)
                
                # Radiotherapy statistics
                radiotherapy_stats = pd.read_sql_query('''
                    SELECT 
                        CASE 
                            WHEN radiotherapy_indicated = '-' OR radiotherapy_indicated IS NULL OR radiotherapy_indicated = '' 
                            THEN 'Nicht besprochen'
                            ELSE radiotherapy_indicated 
                        END as status,
                        COUNT(*) as count,
                        ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM patients), 2) as percentage_of_all
                    FROM patients 
                    GROUP BY 
                        CASE 
                            WHEN radiotherapy_indicated = '-' OR radiotherapy_indicated IS NULL OR radiotherapy_indicated = '' 
                            THEN 'Nicht besprochen'
                            ELSE radiotherapy_indicated 
                        END
                    ORDER BY count DESC
                ''', conn)
                
                # Additional stats for discussed patients only
                discussed_radiotherapy_stats = pd.read_sql_query('''
                    SELECT 
                        radiotherapy_indicated as status,
                        COUNT(*) as count,
                        ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM patients WHERE radiotherapy_indicated NOT IN ('-', '') AND radiotherapy_indicated IS NOT NULL), 2) as percentage_of_discussed
                    FROM patients 
                    WHERE radiotherapy_indicated NOT IN ('-', '') AND radiotherapy_indicated IS NOT NULL
                    GROUP BY radiotherapy_indicated
                    ORDER BY count DESC
                ''', conn)
                
                # Study enrollment statistics
                study_stats = pd.read_sql_query('''
                    SELECT 
                        study_enrollment,
                        COUNT(*) as count
                    FROM patients 
                    WHERE study_enrollment IS NOT NULL AND study_enrollment != '' AND study_enrollment != '-'
                    GROUP BY study_enrollment
                    ORDER BY count DESC
                ''', conn)
                
                return {
                    'basic_statistics': basic_stats,
                    'by_tumorboard_type': by_tumorboard,
                    'radiotherapy_statistics': radiotherapy_stats,
                    'discussed_radiotherapy_statistics': discussed_radiotherapy_stats,
                    'study_enrollment_statistics': study_stats
                }
                
        except Exception as e:
            logging.error(f"Error getting patient statistics: {e}")
            return None
    
    def get_temporal_analysis(self, months_back=12):
        """Get temporal analysis of tumorboard activity"""
        try:
            cutoff_date = datetime.now() - timedelta(days=months_back * 30)
            cutoff_str = cutoff_date.strftime('%Y-%m-%d')
            
            with sqlite3.connect(self.db.db_path) as conn:
                # Sessions over time
                sessions_over_time = pd.read_sql_query('''
                    SELECT 
                        strftime('%Y-%m', s.session_date) as month,
                        e.name as tumorboard_type,
                        COUNT(DISTINCT s.id) as sessions_count,
                        COUNT(DISTINCT p.patient_number) as unique_patients,
                        COUNT(DISTINCT p.unique_key) as total_patient_cases
                    FROM tumorboard_sessions s
                    JOIN tumorboard_entities e ON s.entity_id = e.id
                    LEFT JOIN patients p ON s.id = p.session_id
                    WHERE s.session_date >= ?
                    GROUP BY strftime('%Y-%m', s.session_date), e.name
                    ORDER BY month, tumorboard_type
                ''', conn, params=[cutoff_str])
                
                # Monthly totals
                monthly_totals = pd.read_sql_query('''
                    SELECT 
                        strftime('%Y-%m', s.session_date) as month,
                        COUNT(DISTINCT s.id) as total_sessions,
                        COUNT(DISTINCT p.patient_number) as unique_patients,
                        COUNT(DISTINCT p.unique_key) as total_patient_cases
                    FROM tumorboard_sessions s
                    LEFT JOIN patients p ON s.id = p.session_id
                    WHERE s.session_date >= ?
                    GROUP BY strftime('%Y-%m', s.session_date)
                    ORDER BY month
                ''', conn, params=[cutoff_str])
                
                return {
                    'sessions_over_time': sessions_over_time,
                    'monthly_totals': monthly_totals
                }
                
        except Exception as e:
            logging.error(f"Error getting temporal analysis: {e}")
            return None
    
    def get_diagnosis_analysis(self):
        """Analyze ICD code patterns"""
        try:
            with sqlite3.connect(self.db.db_path) as conn:
                # ICD code analysis
                icd_analysis = pd.read_sql_query('''
                    SELECT 
                        icd_code,
                        COUNT(DISTINCT unique_key) as total_cases,
                        COUNT(DISTINCT patient_number) as unique_patients
                    FROM patients 
                    WHERE icd_code IS NOT NULL AND icd_code != '' AND icd_code != '-'
                    GROUP BY icd_code
                    ORDER BY total_cases DESC
                    LIMIT 20
                ''', conn)
                
                # ICD codes by tumorboard type
                icd_by_tb = pd.read_sql_query('''
                    SELECT 
                        e.name as tumorboard_type,
                        p.icd_code,
                        COUNT(DISTINCT p.unique_key) as total_cases,
                        COUNT(DISTINCT p.patient_number) as unique_patients
                    FROM patients p
                    JOIN tumorboard_sessions s ON p.session_id = s.id
                    JOIN tumorboard_entities e ON s.entity_id = e.id
                    WHERE p.icd_code IS NOT NULL AND p.icd_code != '' AND p.icd_code != '-'
                    GROUP BY e.name, p.icd_code
                    ORDER BY e.name, total_cases DESC
                ''', conn)
                
                return {
                    'icd_analysis': icd_analysis,
                    'icd_by_tumorboard': icd_by_tb
                }
                
        except Exception as e:
            logging.error(f"Error getting diagnosis analysis: {e}")
            return None
    
    def export_comprehensive_report(self, output_path=None):
        """Export a comprehensive analysis report to Excel"""
        if output_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = Path.home() / "tumorboards" / f"tumorboard_analysis_report_{timestamp}.xlsx"
        
        try:
            # Get all analysis data
            patient_stats = self.get_patient_statistics()
            temporal_analysis = self.get_temporal_analysis()
            diagnosis_analysis = self.get_diagnosis_analysis()
            
            if not all([patient_stats, temporal_analysis, diagnosis_analysis]):
                logging.error("Failed to gather analysis data")
                return None
            
            # Export to Excel with multiple sheets
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                # Overview sheet
                overview_data = {
                    'Metrik': [
                        'Anzahl Tumorboard-Typen',
                        'Gesamte Sessions',
                        'Eindeutige Patienten',
                        'Gesamte Patientenfälle',
                        'Bericht erstellt am'
                    ],
                    'Wert': [
                        patient_stats['basic_statistics'].iloc[0]['total_tumorboard_types'],
                        patient_stats['basic_statistics'].iloc[0]['total_sessions'],
                        patient_stats['basic_statistics'].iloc[0]['unique_patients'],
                        patient_stats['basic_statistics'].iloc[0]['total_patient_cases'],
                        datetime.now().strftime('%d.%m.%Y %H:%M')
                    ]
                }
                pd.DataFrame(overview_data).to_excel(writer, sheet_name='Übersicht', index=False)
                
                # Patient statistics
                patient_stats['by_tumorboard_type'].to_excel(writer, sheet_name='Statistik_nach_Tumorboard', index=False)
                patient_stats['radiotherapy_statistics'].to_excel(writer, sheet_name='Radiotherapie_Alle', index=False)
                patient_stats['discussed_radiotherapy_statistics'].to_excel(writer, sheet_name='Radiotherapie_Besprochen', index=False)
                patient_stats['study_enrollment_statistics'].to_excel(writer, sheet_name='Studien_Statistik', index=False)
                
                # Temporal analysis
                temporal_analysis['monthly_totals'].to_excel(writer, sheet_name='Monatliche_Entwicklung', index=False)
                temporal_analysis['sessions_over_time'].to_excel(writer, sheet_name='Sessions_nach_Typ_Zeit', index=False)
                
                # ICD analysis (no more diagnosis analysis)
                diagnosis_analysis['icd_analysis'].to_excel(writer, sheet_name='ICD_Codes', index=False)
                diagnosis_analysis['icd_by_tumorboard'].to_excel(writer, sheet_name='ICD_nach_Tumorboard', index=False)
                
                # Raw data export with calculated age
                raw_data_query = '''
                    SELECT 
                        p.unique_key as "Unique_Key",
                        e.name as "Tumorboard_Typ",
                        s.session_date as "Session_Datum",
                        p.patient_number as "Patientennummer",
                        p.name as "Patient_Name",
                        p.birth_date as "Geburtsdatum",
                        CASE 
                            WHEN p.birth_date IS NOT NULL AND p.birth_date != '' AND p.birth_date != '-'
                            THEN CAST((julianday(s.session_date) - julianday(p.birth_date)) / 365.25 AS INTEGER) || ' Jahre'
                            ELSE '-'
                        END as "Alter_bei_Session",
                        p.diagnosis as "Diagnose",
                        p.icd_code as "ICD_Code",
                        p.radiotherapy_indicated as "Radiotherapie_indiziert",
                        p.aufgebot_type as "Art_des_Aufgebots",
                        p.study_enrollment as "Studie",
                        p.remarks as "Bemerkungen",
                        s.finalized_at as "Abgeschlossen_am",
                        s.finalized_by as "Abgeschlossen_von"
                    FROM patients p
                    JOIN tumorboard_sessions s ON p.session_id = s.id
                    JOIN tumorboard_entities e ON s.entity_id = e.id
                    ORDER BY e.name, s.session_date DESC, p.name
                '''
                
                with sqlite3.connect(self.db.db_path) as conn:
                    raw_data = pd.read_sql_query(raw_data_query, conn)
                    raw_data.to_excel(writer, sheet_name='Rohdaten', index=False)
            
            logging.info(f"Comprehensive analysis report exported to: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logging.error(f"Error exporting comprehensive report: {e}")
            return None
    
    def create_visualization_report(self, output_dir=None):
        """Create visualization charts and save as images"""
        if output_dir is None:
            output_dir = Path.home() / "tumorboards" / "analysis_charts"
        
        output_dir = Path(output_dir)
        output_dir.mkdir(exist_ok=True)
        
        try:
            # Set style for better looking plots
            plt.style.use('seaborn-v0_8')
            
            # Get data
            patient_stats = self.get_patient_statistics()
            temporal_analysis = self.get_temporal_analysis()
            
            if not all([patient_stats, temporal_analysis]):
                logging.error("Failed to gather data for visualizations")
                return None
            
            # 1. Patient cases by tumorboard type
            plt.figure(figsize=(12, 8))
            tb_data = patient_stats['by_tumorboard_type']
            plt.bar(tb_data['tumorboard_type'], tb_data['total_patient_cases'])
            plt.title('Anzahl Patientenfälle nach Tumorboard-Typ')
            plt.xlabel('Tumorboard-Typ')
            plt.ylabel('Anzahl Patientenfälle')
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            plt.savefig(output_dir / 'patientenfaelle_nach_tumorboard.png', dpi=300, bbox_inches='tight')
            plt.close()
            
            # 2. Monthly activity
            plt.figure(figsize=(14, 6))
            monthly_data = temporal_analysis['monthly_totals']
            plt.plot(monthly_data['month'], monthly_data['unique_patients'], marker='o', linewidth=2, label='Eindeutige Patienten')
            plt.plot(monthly_data['month'], monthly_data['total_patient_cases'], marker='s', linewidth=2, label='Gesamte Patientenfälle')
            plt.title('Monatliche Entwicklung')
            plt.xlabel('Monat')
            plt.ylabel('Anzahl')
            plt.xticks(rotation=45)
            plt.legend()
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            plt.savefig(output_dir / 'monatliche_entwicklung.png', dpi=300, bbox_inches='tight')
            plt.close()
            
            # 3. Radiotherapy distribution
            if not patient_stats['radiotherapy_statistics'].empty:
                plt.figure(figsize=(8, 8))
                radio_data = patient_stats['radiotherapy_statistics']
                plt.pie(radio_data['count'], labels=radio_data['status'], autopct='%1.1f%%')
                plt.title('Verteilung Radiotherapie-Indikation')
                plt.savefig(output_dir / 'radiotherapie_verteilung.png', dpi=300, bbox_inches='tight')
                plt.close()
            
            logging.info(f"Visualization charts saved to: {output_dir}")
            return str(output_dir)
            
        except Exception as e:
            logging.error(f"Error creating visualization report: {e}")
            return None


def generate_full_analysis_report():
    """Generate a complete analysis report with all data and visualizations"""
    try:
        analyzer = TumorboardAnalyzer()
        
        # Generate Excel report
        excel_report = analyzer.export_comprehensive_report()
        
        # Generate visualizations
        charts_dir = analyzer.create_visualization_report()
        
        results = {
            'excel_report': excel_report,
            'charts_directory': charts_dir,
            'success': excel_report is not None
        }
        
        if results['success']:
            logging.info("Full analysis report generated successfully")
        else:
            logging.error("Failed to generate analysis report")
        
        return results
        
    except Exception as e:
        logging.error(f"Error generating full analysis report: {e}")
        return {'success': False, 'error': str(e)} 