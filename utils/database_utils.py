import sqlite3
import pandas as pd
import logging
from pathlib import Path
from datetime import datetime
import os

class TumorboardDatabase:
    """Central database for all tumorboard data"""
    
    def __init__(self, db_path=None):
        if db_path is None:
            self.db_path = Path.home() / "tumorboards" / "master_tumorboard.db"
        else:
            self.db_path = Path(db_path)
        
        # Ensure tumorboards directory exists
        self.db_path.parent.mkdir(exist_ok=True)
        
        self.init_database()
    
    def init_database(self):
        """Initialize database with required tables"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create tumorboard entities table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS tumorboard_entities (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT UNIQUE NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create tumorboard sessions table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS tumorboard_sessions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        entity_id INTEGER NOT NULL,
                        session_date DATE NOT NULL,
                        finalized_at TIMESTAMP,
                        finalized_by TEXT,
                        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (entity_id) REFERENCES tumorboard_entities(id),
                        UNIQUE(entity_id, session_date)
                    )
                ''')
                
                # Create patients table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS patients (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        unique_key TEXT UNIQUE NOT NULL,
                        session_id INTEGER NOT NULL,
                        patient_number TEXT,
                        name TEXT,
                        birth_date DATE,
                        age_at_session TEXT,
                        diagnosis TEXT,
                        icd_code TEXT,
                        radiotherapy_indicated TEXT,
                        aufgebot_type TEXT,
                        study_enrollment TEXT,
                        remarks TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (session_id) REFERENCES tumorboard_sessions(id)
                    )
                ''')
                
                # Create indexes for better performance
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_patients_session ON patients(session_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_patients_number ON patients(patient_number)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_patients_unique_key ON patients(unique_key)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_sessions_date ON tumorboard_sessions(session_date)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_sessions_entity ON tumorboard_sessions(entity_id)')
                
                conn.commit()
                logging.info(f"Database initialized successfully: {self.db_path}")
                
        except Exception as e:
            logging.error(f"Error initializing database: {e}")
            raise e
    
    def get_or_create_entity(self, entity_name):
        """Get entity ID or create new entity"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Try to get existing entity
                cursor.execute('SELECT id FROM tumorboard_entities WHERE name = ?', (entity_name,))
                result = cursor.fetchone()
                
                if result:
                    return result[0]
                
                # Create new entity
                cursor.execute(
                    'INSERT INTO tumorboard_entities (name) VALUES (?)',
                    (entity_name,)
                )
                conn.commit()
                return cursor.lastrowid
                
        except Exception as e:
            logging.error(f"Error getting/creating entity {entity_name}: {e}")
            raise e
    
    def import_collection_excel(self, tumorboard_name, collection_excel_path):
        """Import data from a collection Excel file into the database"""
        try:
            if not Path(collection_excel_path).exists():
                logging.error(f"Collection Excel file not found: {collection_excel_path}")
                return False
            
            # Get or create entity
            entity_id = self.get_or_create_entity(tumorboard_name)
            
            # Read Excel file
            excel_file = pd.ExcelFile(collection_excel_path)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                imported_sessions = 0
                imported_patients = 0
                
                # Process each sheet (except overview)
                for sheet_name in excel_file.sheet_names:
                    if sheet_name.lower() in ['übersicht', 'overview', 'tabelle1']:
                        continue
                    
                    # Convert sheet name back to date format
                    try:
                        # Sheet names are in format DD_MM_YYYY
                        date_parts = sheet_name.split('_')
                        if len(date_parts) == 3:
                            session_date = f"{date_parts[0]}.{date_parts[1]}.{date_parts[2]}"
                            # Convert to SQL date format
                            date_obj = datetime.strptime(session_date, "%d.%m.%Y")
                            sql_date = date_obj.strftime("%Y-%m-%d")
                        else:
                            logging.warning(f"Skipping sheet with invalid date format: {sheet_name}")
                            continue
                    except Exception as e:
                        logging.warning(f"Error parsing date from sheet name {sheet_name}: {e}")
                        continue
                    
                    # Read sheet data
                    df = pd.read_excel(collection_excel_path, sheet_name=sheet_name)
                    
                    if df.empty:
                        continue
                    
                    # Get or create session
                    cursor.execute('''
                        INSERT OR REPLACE INTO tumorboard_sessions 
                        (entity_id, session_date, last_updated) 
                        VALUES (?, ?, CURRENT_TIMESTAMP)
                    ''', (entity_id, sql_date))
                    
                    session_id = cursor.lastrowid
                    if session_id == 0:  # If it was an update, get the existing ID
                        cursor.execute(
                            'SELECT id FROM tumorboard_sessions WHERE entity_id = ? AND session_date = ?',
                            (entity_id, sql_date)
                        )
                        session_id = cursor.fetchone()[0]
                    
                    imported_sessions += 1
                    
                    # Import patients with unique key logic
                    for _, row in df.iterrows():
                        # Skip empty rows
                        if pd.isna(row.get('Name', '')) or str(row.get('Name', '')).strip() == '':
                            continue
                        
                        # Clean and prepare data
                        patient_number = self._clean_value(row.get('Patientennummer', ''))
                        if not patient_number:
                            logging.warning(f"Skipping patient without patient number in {tumorboard_name} {session_date}")
                            continue
                        
                        # Create unique key: DATUM_PATIENTENNUMMER_TUMORBOARD
                        # Convert date back to DD-MM-YYYY format for unique key
                        date_for_key = date_obj.strftime("%d-%m-%Y")
                        unique_key = f"{date_for_key}_{patient_number}_{tumorboard_name}"
                        
                        patient_data = {
                            'unique_key': unique_key,
                            'session_id': session_id,
                            'patient_number': patient_number,
                            'name': self._clean_value(row.get('Name', '')),
                            'birth_date': self._clean_date(row.get('Geburtsdatum', '')),
                            'age_at_session': self._clean_value(row.get('Alter', '')),
                            'diagnosis': self._clean_value(row.get('Diagnose', '')),
                            'icd_code': self._clean_value(row.get('ICD-Code', '') or row.get('ICD-10', '') or row.get('ICD Code', '')),
                            'radiotherapy_indicated': self._clean_value(row.get('Radiotherapie indiziert', '')),
                            'aufgebot_type': self._clean_value(row.get('Art des Aufgebots', '')),
                            'study_enrollment': self._clean_value(row.get('Vormerken für Studie', '')),
                            'remarks': self._clean_value(row.get('Bemerkung/Procedere', ''))
                        }
                        
                        # Use INSERT OR REPLACE to handle duplicates
                        cursor.execute('''
                            INSERT OR REPLACE INTO patients (
                                unique_key, session_id, patient_number, name, birth_date, age_at_session,
                                diagnosis, icd_code, radiotherapy_indicated, aufgebot_type,
                                study_enrollment, remarks, updated_at
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                        ''', (
                            patient_data['unique_key'], patient_data['session_id'], patient_data['patient_number'],
                            patient_data['name'], patient_data['birth_date'], patient_data['age_at_session'],
                            patient_data['diagnosis'], patient_data['icd_code'], patient_data['radiotherapy_indicated'],
                            patient_data['aufgebot_type'], patient_data['study_enrollment'], patient_data['remarks']
                        ))
                        
                        imported_patients += 1
                
                conn.commit()
                logging.info(f"Successfully imported {imported_sessions} sessions and {imported_patients} patients from {tumorboard_name}")
                return True
                
        except Exception as e:
            logging.error(f"Error importing collection Excel for {tumorboard_name}: {e}")
            return False
    
    def _clean_value(self, value):
        """Clean and normalize values for database storage"""
        if pd.isna(value) or value == '' or str(value).lower() == 'nan':
            return None
        
        cleaned = str(value).strip()
        
        # Remove .0 from patient numbers
        if cleaned.endswith('.0') and cleaned[:-2].isdigit():
            cleaned = cleaned[:-2]
        
        return cleaned if cleaned != '' else None
    
    def _clean_date(self, date_value):
        """Clean and normalize date values"""
        if pd.isna(date_value) or date_value == '' or str(date_value).lower() == 'nan':
            return None
        
        date_str = str(date_value).strip()
        
        # Try to parse different date formats
        for fmt in ["%d.%m.%Y", "%d/%m/%Y", "%Y-%m-%d"]:
            try:
                date_obj = datetime.strptime(date_str, fmt)
                return date_obj.strftime("%Y-%m-%d")  # Store in SQL format
            except ValueError:
                continue
        
        return None  # Could not parse date
    
    def export_to_excel(self, output_path=None):
        """Export entire database to Excel for analysis"""
        if output_path is None:
            output_path = Path.home() / "tumorboards" / f"master_database_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Query all data with joins
                query = '''
                    SELECT 
                        p.unique_key as "Unique_Key",
                        e.name as "Tumorboard_Entität",
                        s.session_date as "Datum",
                        p.patient_number as "Patientennummer",
                        p.name as "Name",
                        p.birth_date as "Geburtsdatum",
                        p.age_at_session as "Alter",
                        p.diagnosis as "Diagnose",
                        p.icd_code as "ICD_Code",
                        p.radiotherapy_indicated as "Radiotherapie_indiziert",
                        p.aufgebot_type as "Art_des_Aufgebots",
                        p.study_enrollment as "Vormerken_für_Studie",
                        p.remarks as "Bemerkung_Procedere",
                        s.finalized_at as "Abgeschlossen_am",
                        s.finalized_by as "Abgeschlossen_von",
                        p.created_at as "Erstellt_am",
                        p.updated_at as "Aktualisiert_am"
                    FROM patients p
                    JOIN tumorboard_sessions s ON p.session_id = s.id
                    JOIN tumorboard_entities e ON s.entity_id = e.id
                    ORDER BY e.name, s.session_date, p.name
                '''
                
                df = pd.read_sql_query(query, conn)
                
                # Export to Excel
                with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                    # Main data sheet
                    df.to_excel(writer, sheet_name='Alle_Daten', index=False)
                    
                    # Summary sheet
                    summary_data = []
                    
                    # Count by tumorboard entity
                    entity_counts = df.groupby('Tumorboard_Entität').agg({
                        'Datum': 'nunique',
                        'Name': 'count'
                    }).rename(columns={'Datum': 'Anzahl_Sessions', 'Name': 'Anzahl_Patienten'})
                    
                    summary_df = entity_counts.reset_index()
                    summary_df.to_excel(writer, sheet_name='Zusammenfassung', index=False)
                
                logging.info(f"Database exported to Excel: {output_path}")
                return str(output_path)
                
        except Exception as e:
            logging.error(f"Error exporting database to Excel: {e}")
            return None
    
    def get_statistics(self):
        """Get basic statistics from the database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Total counts
                cursor.execute('SELECT COUNT(*) FROM tumorboard_entities')
                total_entities = cursor.fetchone()[0]
                
                cursor.execute('SELECT COUNT(*) FROM tumorboard_sessions')
                total_sessions = cursor.fetchone()[0]
                
                cursor.execute('SELECT COUNT(*) FROM patients')
                total_patients = cursor.fetchone()[0]
                
                # Recent activity
                cursor.execute('''
                    SELECT e.name, COUNT(s.id) as session_count
                    FROM tumorboard_entities e
                    LEFT JOIN tumorboard_sessions s ON e.id = s.entity_id
                    GROUP BY e.id, e.name
                    ORDER BY session_count DESC
                ''')
                entity_stats = cursor.fetchall()
                
                return {
                    'total_entities': total_entities,
                    'total_sessions': total_sessions,
                    'total_patients': total_patients,
                    'entity_statistics': entity_stats
                }
                
        except Exception as e:
            logging.error(f"Error getting database statistics: {e}")
            return None


def sync_all_collection_files():
    """Sync all collection Excel files to the central database"""
    try:
        db = TumorboardDatabase()
        tumorboards_dir = Path.home() / "tumorboards"
        
        if not tumorboards_dir.exists():
            logging.warning("Tumorboards directory not found")
            return False
        
        synced_count = 0
        
        # Find all collection Excel files
        for entity_dir in tumorboards_dir.iterdir():
            if entity_dir.is_dir():
                # Look for collection Excel file
                collection_pattern = f"alle_tumorboards_{entity_dir.name.lower()}.xlsx"
                collection_file = entity_dir / collection_pattern
                
                if collection_file.exists():
                    logging.info(f"Syncing collection file: {collection_file}")
                    success = db.import_collection_excel(entity_dir.name, collection_file)
                    if success:
                        synced_count += 1
                    else:
                        logging.warning(f"Failed to sync: {collection_file}")
        
        logging.info(f"Successfully synced {synced_count} collection files to database")
        return synced_count > 0
        
    except Exception as e:
        logging.error(f"Error syncing collection files: {e}")
        return False