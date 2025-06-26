import sqlite3
import pandas as pd
import logging
from pathlib import Path
from datetime import datetime
import os
import re

class TumorboardDatabase:
    """Central database for all tumorboard data"""
    
    def __init__(self, db_path=None):
        if db_path is None:
            self.db_path = Path.home() / "tumorboards" / "__SQLite_database" / "master_tumorboard.db"
        else:
            self.db_path = Path(db_path)
        
        # Ensure tumorboards directory exists
        self.db_path.parent.mkdir(exist_ok=True)
        
        self.init_database()
    
    def close_all_connections(self):
        """Force close all database connections"""
        try:
            # Force close any remaining connections by connecting and immediately closing
            conn = sqlite3.connect(self.db_path)
            conn.close()
            logging.info("Database connections closed")
        except Exception as e:
            logging.warning(f"Error closing database connections: {e}")
    
    def init_database(self):
        """Initialize database with required tables"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create tumorboard entities table (removed last_updated as it's never updated)
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS tumorboard_entities (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT UNIQUE NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
                        last_edited_at TIMESTAMP,
                        last_edited_by TEXT,
                        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (entity_id) REFERENCES tumorboard_entities(id),
                        UNIQUE(entity_id, session_date)
                    )
                ''')
                
                # Create patients table with icd_family column
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS patients (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        unique_key TEXT UNIQUE NOT NULL,
                        session_id INTEGER NOT NULL,
                        patient_number TEXT,
                        name TEXT,
                        birth_date DATE,
                        age_at_session INTEGER,
                        diagnosis TEXT,
                        icd_code TEXT,
                        icd_family TEXT,
                        radiotherapy_indicated TEXT,
                        aufgebot_type TEXT,
                        study_enrollment TEXT,
                        remarks TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (session_id) REFERENCES tumorboard_sessions(id)
                    )
                ''')
                
                # Create indexes for better performance (added ICD indexes)
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_patients_session ON patients(session_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_patients_number ON patients(patient_number)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_patients_unique_key ON patients(unique_key)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_sessions_date ON tumorboard_sessions(session_date)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_sessions_entity ON tumorboard_sessions(entity_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_patients_icd_code ON patients(icd_code)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_patients_icd_family ON patients(icd_family)')
                
                # Migration: Add icd_family column if it doesn't exist
                cursor.execute("PRAGMA table_info(patients)")
                columns = [column[1] for column in cursor.fetchall()]
                if 'icd_family' not in columns:
                    cursor.execute('ALTER TABLE patients ADD COLUMN icd_family TEXT')
                    logging.info("Added icd_family column to patients table")
                
                # Migration: Change age_at_session to INTEGER if it's still TEXT
                cursor.execute("PRAGMA table_info(patients)")
                columns = {column[1]: column[2] for column in cursor.fetchall()}
                if columns.get('age_at_session') == 'TEXT':
                    # Create new table with correct schema
                    cursor.execute('''
                        CREATE TABLE patients_new (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            unique_key TEXT UNIQUE NOT NULL,
                            session_id INTEGER NOT NULL,
                            patient_number TEXT,
                            name TEXT,
                            birth_date DATE,
                            age_at_session INTEGER,
                            diagnosis TEXT,
                            icd_code TEXT,
                            icd_family TEXT,
                            radiotherapy_indicated TEXT,
                            aufgebot_type TEXT,
                            study_enrollment TEXT,
                            remarks TEXT,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            FOREIGN KEY (session_id) REFERENCES tumorboard_sessions(id)
                        )
                    ''')
                    
                    # Copy data, converting age values
                    cursor.execute('''
                        INSERT INTO patients_new 
                        SELECT 
                            id, unique_key, session_id, patient_number, name, birth_date,
                            CASE 
                                WHEN age_at_session IS NULL OR age_at_session = '' OR age_at_session = '-' 
                                THEN NULL
                                ELSE CAST(REPLACE(REPLACE(age_at_session, ' Jahre', ''), ' Jahre', '') AS INTEGER)
                            END as age_at_session,
                            diagnosis, icd_code, icd_family, radiotherapy_indicated, aufgebot_type,
                            study_enrollment, remarks, created_at, updated_at
                        FROM patients
                    ''')
                    
                    # Replace old table
                    cursor.execute('DROP TABLE patients')
                    cursor.execute('ALTER TABLE patients_new RENAME TO patients')
                    logging.info("Migrated age_at_session from TEXT to INTEGER")
                
                # Migration: Remove last_updated from tumorboard_entities if it exists
                cursor.execute("PRAGMA table_info(tumorboard_entities)")
                columns = [column[1] for column in cursor.fetchall()]
                if 'last_updated' in columns:
                    # Create new table without last_updated
                    cursor.execute('''
                        CREATE TABLE tumorboard_entities_new (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            name TEXT UNIQUE NOT NULL,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    ''')
                    
                    # Copy data
                    cursor.execute('''
                        INSERT INTO tumorboard_entities_new (id, name, created_at)
                        SELECT id, name, created_at FROM tumorboard_entities
                    ''')
                    
                    # Replace old table
                    cursor.execute('DROP TABLE tumorboard_entities')
                    cursor.execute('ALTER TABLE tumorboard_entities_new RENAME TO tumorboard_entities')
                    logging.info("Removed last_updated column from tumorboard_entities")
                
                # Migration: Add last_edited fields if they don't exist
                cursor.execute("PRAGMA table_info(tumorboard_sessions)")
                columns = [column[1] for column in cursor.fetchall()]
                if 'last_edited_at' not in columns:
                    cursor.execute('ALTER TABLE tumorboard_sessions ADD COLUMN last_edited_at TIMESTAMP')
                    logging.info("Added last_edited_at column to tumorboard_sessions table")
                if 'last_edited_by' not in columns:
                    cursor.execute('ALTER TABLE tumorboard_sessions ADD COLUMN last_edited_by TEXT')
                    logging.info("Added last_edited_by column to tumorboard_sessions table")
                
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
                    
                    # Get or create session - PRESERVE finalized_at and finalized_by
                    cursor.execute('''
                        INSERT INTO tumorboard_sessions 
                        (entity_id, session_date, last_updated) 
                        VALUES (?, ?, CURRENT_TIMESTAMP)
                        ON CONFLICT(entity_id, session_date) DO UPDATE SET
                        last_updated = CURRENT_TIMESTAMP
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
                        
                        # Clean and prepare data
                        birth_date = self._clean_date(row.get('Geburtsdatum', ''))
                        raw_icd_code = self._clean_value(row.get('ICD-Code', '') or row.get('ICD-10', '') or row.get('ICD Code', ''))
                        
                        # Calculate age automatically from birth_date and session_date
                        calculated_age = None
                        if birth_date:
                            try:
                                birth_date_obj = datetime.strptime(birth_date, "%Y-%m-%d")
                                age_years = date_obj.year - birth_date_obj.year - ((date_obj.month, date_obj.day) < (birth_date_obj.month, birth_date_obj.day))
                                if 0 <= age_years <= 150:  # Sanity check for reasonable age
                                    calculated_age = age_years
                            except Exception as e:
                                logging.warning(f"Error calculating age for patient {patient_number}: {e}")
                        
                        # Extract ICD family (e.g., "D32.9" -> "D32", "C34.1" -> "C34")
                        icd_family = None
                        if raw_icd_code:
                            # Remove dots and take the letter + first 1-2 digits
                            clean_icd = raw_icd_code.upper().replace('.', '').replace(' ', '')
                            # Match pattern like C34, D32, etc. (letter followed by digits)
                            match = re.match(r'^([A-Z]\d{1,2})', clean_icd)
                            if match:
                                icd_family = match.group(1)
                        
                        patient_data = {
                            'unique_key': unique_key,
                            'session_id': session_id,
                            'patient_number': patient_number,
                            'name': self._clean_value(row.get('Name', '')),
                            'birth_date': birth_date,
                            'age_at_session': calculated_age,  # Now automatically calculated
                            'diagnosis': self._clean_value(row.get('Diagnose', '')),
                            'icd_code': raw_icd_code,
                            'icd_family': icd_family,  # New field for grouped analysis
                            'radiotherapy_indicated': self._clean_value(row.get('Radiotherapie indiziert', '')),
                            'aufgebot_type': self._normalize_aufgebot_type(row.get('Art des Aufgebots', '')),
                            'study_enrollment': self._clean_value(row.get('Vormerken für Studie', '')),
                            'remarks': self._clean_value(row.get('Bemerkung/Procedere', ''))
                        }
                        
                        # Use INSERT OR REPLACE to handle duplicates
                        cursor.execute('''
                            INSERT OR REPLACE INTO patients (
                                unique_key, session_id, patient_number, name, birth_date, age_at_session,
                                diagnosis, icd_code, icd_family, radiotherapy_indicated, aufgebot_type,
                                study_enrollment, remarks, updated_at
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                        ''', (
                            patient_data['unique_key'], patient_data['session_id'], patient_data['patient_number'],
                            patient_data['name'], patient_data['birth_date'], patient_data['age_at_session'],
                            patient_data['diagnosis'], patient_data['icd_code'], patient_data['icd_family'],
                            patient_data['radiotherapy_indicated'], patient_data['aufgebot_type'], 
                            patient_data['study_enrollment'], patient_data['remarks']
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
            output_path = Path.home() / "tumorboards" / "__SQLite_database" / f"master_database_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
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
                        CASE 
                            WHEN p.age_at_session IS NOT NULL 
                            THEN p.age_at_session || ' Jahre'
                            ELSE '-'
                        END as "Alter",
                        p.diagnosis as "Diagnose",
                        p.icd_code as "ICD_Code",
                        p.icd_family as "ICD_Familie",
                        p.radiotherapy_indicated as "Radiotherapie_indiziert",
                        p.aufgebot_type as "Art_des_Aufgebots",
                        p.study_enrollment as "Vormerken_für_Studie",
                        p.remarks as "Bemerkung_Procedere",
                        s.finalized_at as "Abgeschlossen_am",
                        s.finalized_by as "Abgeschlossen_von",
                        s.last_edited_at as "Zuletzt_editiert_am",
                        s.last_edited_by as "Zuletzt_editiert_von",
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
    
    def update_session_completion_data(self, tumorboard_name, session_date, finalized_by=None, is_edit=False):
        """Update session finalization and edit tracking data"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get entity and session
                entity_id = self.get_or_create_entity(tumorboard_name)
                
                # Convert date to SQL format
                if isinstance(session_date, str):
                    try:
                        date_obj = datetime.strptime(session_date, "%d.%m.%Y")
                        sql_date = date_obj.strftime("%Y-%m-%d")
                    except ValueError:
                        logging.error(f"Invalid date format: {session_date}")
                        return False
                else:
                    sql_date = session_date
                
                # Get current session data
                cursor.execute('''
                    SELECT finalized_at, finalized_by 
                    FROM tumorboard_sessions 
                    WHERE entity_id = ? AND session_date = ?
                ''', (entity_id, sql_date))
                
                result = cursor.fetchone()
                if not result:
                    logging.error(f"Session not found: {tumorboard_name} {session_date}")
                    return False
                
                current_finalized_at, current_finalized_by = result
                
                if is_edit:
                    # This is an edit - update only last_edited fields, preserve original finalization
                    cursor.execute('''
                        UPDATE tumorboard_sessions 
                        SET last_edited_at = CURRENT_TIMESTAMP,
                            last_edited_by = ?,
                            last_updated = CURRENT_TIMESTAMP
                        WHERE entity_id = ? AND session_date = ?
                    ''', (finalized_by, entity_id, sql_date))
                    
                    logging.info(f"Updated edit tracking for session {tumorboard_name} {session_date} by {finalized_by}")
                    
                else:
                    # This is initial finalization - set finalized fields only if not already set
                    if current_finalized_at is None and current_finalized_by is None:
                        cursor.execute('''
                            UPDATE tumorboard_sessions 
                            SET finalized_at = CURRENT_TIMESTAMP,
                                finalized_by = ?,
                                last_updated = CURRENT_TIMESTAMP
                            WHERE entity_id = ? AND session_date = ?
                        ''', (finalized_by, entity_id, sql_date))
                        
                        logging.info(f"Set initial finalization for session {tumorboard_name} {session_date} by {finalized_by}")
                    else:
                        # Already finalized, this is actually an edit
                        cursor.execute('''
                            UPDATE tumorboard_sessions 
                            SET last_edited_at = CURRENT_TIMESTAMP,
                                last_edited_by = ?,
                                last_updated = CURRENT_TIMESTAMP
                            WHERE entity_id = ? AND session_date = ?
                        ''', (finalized_by, entity_id, sql_date))
                        
                        logging.info(f"Session already finalized, treating as edit by {finalized_by}")
                
                conn.commit()
                return True
                
        except Exception as e:
            logging.error(f"Error updating session completion data: {e}")
            return False
    
    @staticmethod
    def _normalize_aufgebot_type(value):
        """Normalize aufgebot type to categorical values"""
        if not value or str(value).strip() in ['-', '', 'nan']:
            return None
        
        value_str = str(value).strip()
        
        # Map long descriptions to short categories
        if "Kat I:" in value_str or "1-3 Tagen" in value_str:
            return "Kat I"
        elif "Kat II:" in value_str or "5-7 Tagen" in value_str:
            return "Kat II"
        elif "Kat III:" in value_str or "Nach Eingang des Konsils" in value_str:
            return "Kat III"
        elif value_str in ["Kat I", "Kat II", "Kat III"]:
            return value_str
        else:
            # Log unknown values for debugging
            logging.warning(f"Unknown aufgebot type value: {value_str}")
            return value_str  # Return as-is for unknown values


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
            if entity_dir.is_dir() and entity_dir.name != "__SQLite_database":
                # Look for collection Excel file flexibly - any file starting with "alle_tumorboards_"
                collection_file = None
                for file in entity_dir.glob("alle_tumorboards_*.xlsx"):
                    collection_file = file
                    break
                
                if collection_file and collection_file.exists():
                    logging.info(f"Syncing collection file: {collection_file}")
                    success = db.import_collection_excel(entity_dir.name, collection_file)
                    if success:
                        synced_count += 1
                    else:
                        logging.warning(f"Failed to sync: {collection_file}")
                else:
                    logging.info(f"No collection file found in {entity_dir.name} (looking for files starting with 'alle_tumorboards_')")
        
        logging.info(f"Successfully synced {synced_count} collection files to database")
        return synced_count > 0
        
    except Exception as e:
        logging.error(f"Error syncing collection files: {e}")
        return False