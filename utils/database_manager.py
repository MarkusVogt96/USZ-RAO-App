# Tumorboard Database Manager for Windows
"""
Tumorboard Database Manager
Standalone tool for managing the central tumorboard database
"""

import sys
import os
from pathlib import Path

# Add the parent directory to the path so we can import from utils
sys.path.append(str(Path(__file__).parent.parent))

from utils.database_utils import TumorboardDatabase, sync_all_collection_files
from utils.data_analysis_utils import generate_full_analysis_report
import logging

def get_tumorboard_base_path():
    """Determine the correct tumorboard base path, prioritizing K: drive"""
    k_path = Path("K:/RAO_Projekte/App/tumorboards")
    if k_path.exists() and k_path.is_dir():
        return k_path
    else:
        # Fall back to user home only if K: is not available
        return Path.home() / "tumorboards"

def get_database_path():
    """Get the correct database path"""
    base_path = get_tumorboard_base_path()
    return base_path / "__SQLite_database" / "master_tumorboard.db"

# Determine correct paths
TUMORBOARD_BASE_PATH = get_tumorboard_base_path()
DATABASE_PATH = get_database_path()

# Setup logging with correct path
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(TUMORBOARD_BASE_PATH / "__SQLite_database" / "database_manager.log"),
        logging.StreamHandler()
    ]
)

def show_menu():
    """Display the main menu"""
    print("\n" + "="*60)
    print("           TUMORBOARD DATABASE MANAGER")
    print("="*60)
    
    # Show which path is being used
    if "K:" in str(TUMORBOARD_BASE_PATH):
        print(f"🗄️  Database-Pfad: {DATABASE_PATH} (K:-Intranet)")
    else:
        print(f"⚠️  Database-Pfad: {DATABASE_PATH} (Lokaler Fallback)")
    print("="*60)
    
    print("1. Datenbank initialisieren/überprüfen")
    print("2. Alle Sammel-Excel-Dateien zur Datenbank synchronisieren")
    print("3. Datenbankstatistiken anzeigen")
    print("4. Vollständigen Analysebericht erstellen")
    print("5. Datenbank zu Excel exportieren")
    print("6. Datenbank-Backup erstellen")
    print("7. Datenbank zurücksetzen (VORSICHT!)")
    print("0. Beenden")
    print("="*60)

def init_database():
    """Initialize or check database"""
    try:
        print("Initialisiere Datenbank...")
        db = TumorboardDatabase(db_path=DATABASE_PATH)
        stats = db.get_statistics()
        
        if stats:
            print(f"✓ Datenbank erfolgreich initialisiert/überprüft")
            print(f"  - Tumorboard-Typen: {stats['total_entities']}")
            print(f"  - Sessions: {stats['total_sessions']}")
            print(f"  - Patienten: {stats['total_patients']}")
        else:
            print("✗ Fehler beim Initialisieren der Datenbank")
            
    except Exception as e:
        print(f"✗ Fehler: {e}")

def sync_all_collections():
    """Sync all collection Excel files to database"""
    try:
        print("Synchronisiere alle Sammel-Excel-Dateien...")
        success = sync_all_collection_files(tumorboard_base_path=TUMORBOARD_BASE_PATH)
        
        if success:
            print("✓ Synchronisation erfolgreich abgeschlossen")
            # Show updated statistics
            db = TumorboardDatabase(db_path=DATABASE_PATH)
            stats = db.get_statistics()
            if stats:
                print(f"  - Tumorboard-Typen: {stats['total_entities']}")
                print(f"  - Sessions: {stats['total_sessions']}")
                print(f"  - Patienten: {stats['total_patients']}")
        else:
            print("✗ Synchronisation fehlgeschlagen")
            
    except Exception as e:
        print(f"✗ Fehler: {e}")

def show_statistics():
    """Display database statistics"""
    try:
        print("Lade Datenbankstatistiken...")
        db = TumorboardDatabase(db_path=DATABASE_PATH)
        stats = db.get_statistics()
        
        if stats:
            print("\n" + "="*50)
            print("           DATENBANKSTATISTIKEN")
            print("="*50)
            print(f"Tumorboard-Typen:     {stats['total_entities']}")
            print(f"Gesamte Sessions:     {stats['total_sessions']}")
            print(f"Gesamte Patienten:    {stats['total_patients']}")
            print("\nStatistiken nach Tumorboard-Typ:")
            print("-" * 40)
            
            for entity_name, session_count in stats['entity_statistics']:
                print(f"{entity_name:<25} {session_count:>3} Sessions")
                
        else:
            print("✗ Fehler beim Laden der Statistiken")
            
    except Exception as e:
        print(f"✗ Fehler: {e}")

def create_analysis_report():
    """Create comprehensive analysis report"""
    try:
        print("Erstelle vollständigen Analysebericht...")
        print("Dies kann einige Minuten dauern...")
        
        results = generate_full_analysis_report(tumorboard_base_path=TUMORBOARD_BASE_PATH)
        
        if results['success']:
            print("✓ Analysebericht erfolgreich erstellt")
            if results.get('excel_report'):
                print(f"  Excel-Bericht: {results['excel_report']}")
            if results.get('charts_directory'):
                print(f"  Diagramme: {results['charts_directory']}")
        else:
            print("✗ Fehler beim Erstellen des Analyseberichts")
            if 'error' in results:
                print(f"  Fehler: {results['error']}")
                
    except Exception as e:
        print(f"✗ Fehler: {e}")

def export_database():
    """Export database to Excel"""
    try:
        print("Exportiere Datenbank zu Excel...")
        db = TumorboardDatabase(db_path=DATABASE_PATH)
        export_path = db.export_to_excel()
        
        if export_path:
            print(f"✓ Datenbank erfolgreich exportiert: {export_path}")
        else:
            print("✗ Fehler beim Exportieren der Datenbank")
            
    except Exception as e:
        print(f"✗ Fehler: {e}")

def backup_database():
    """Create database backup"""
    try:
        print("Erstelle Datenbank-Backup...")
        db = TumorboardDatabase(db_path=DATABASE_PATH)
        
        from datetime import datetime
        import shutil
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = db.db_path.parent / f"master_tumorboard_backup_{timestamp}.db"
        
        shutil.copy2(db.db_path, backup_path)
        print(f"✓ Backup erfolgreich erstellt: {backup_path}")
        
    except Exception as e:
        print(f"✗ Fehler: {e}")

def reset_database():
    """Reset database (with confirmation)"""
    try:
        print("\n" + "!"*60)
        print("           WARNUNG: DATENBANK ZURÜCKSETZEN")
        print("!"*60)
        print("Diese Aktion wird ALLE Daten in der Datenbank löschen!")
        print("Dies kann NICHT rückgängig gemacht werden!")
        print("\nStellen Sie sicher, dass Sie ein Backup haben!")
        
        confirmation = input("\nGeben Sie 'RESET' ein, um fortzufahren: ")
        
        if confirmation == "RESET":
            db = TumorboardDatabase(db_path=DATABASE_PATH)
            db_path = db.db_path
            
            # Close all database connections
            db.close_all_connections()
            print("✓ Datenbankverbindungen geschlossen")
            
            # Force garbage collection to ensure connection is released
            import gc
            del db
            gc.collect()
            
            # Small delay to ensure file handle is released
            import time
            time.sleep(1.0)
            
            # Delete database file
            if db_path.exists():
                try:
                    db_path.unlink()
                    print("✓ Datenbank-Datei gelöscht")
                except PermissionError:
                    print("✗ Datei wird noch von einem anderen Prozess verwendet")
                    print("  Bitte schließen Sie alle anderen Programme, die auf die Datenbank zugreifen")
                    print("  und versuchen Sie es erneut.")
                    return
            
            # Reinitialize
            new_db = TumorboardDatabase(db_path=DATABASE_PATH)
            print("✓ Neue leere Datenbank erstellt")
            
        else:
            print("Zurücksetzen abgebrochen")
            
    except Exception as e:
        print(f"✗ Fehler: {e}")

def main():
    """Main program loop"""
    print("Tumorboard Database Manager gestartet")
    
    # Show path information and warning if using fallback
    if "K:" in str(TUMORBOARD_BASE_PATH):
        print(f"✅ Verwende K:-Intranet Database: {DATABASE_PATH}")
    else:
        print(f"⚠️  WARNUNG: K:-Laufwerk nicht verfügbar!")
        print(f"⚠️  Verwende lokalen Fallback-Pfad: {DATABASE_PATH}")
        print(f"⚠️  Daten werden NICHT mit dem Server synchronisiert!")
        input("\nDrücken Sie Enter, um trotzdem fortzufahren...")
    
    while True:
        show_menu()
        
        try:
            choice = input("\nWählen Sie eine Option (0-7): ").strip()
            
            if choice == "0":
                print("Database Manager beendet.")
                break
            elif choice == "1":
                init_database()
            elif choice == "2":
                sync_all_collections()
            elif choice == "3":
                show_statistics()
            elif choice == "4":
                create_analysis_report()
            elif choice == "5":
                export_database()
            elif choice == "6":
                backup_database()
            elif choice == "7":
                reset_database()
            else:
                print("Ungültige Auswahl. Bitte wählen Sie 0-7.")
                
        except KeyboardInterrupt:
            print("\n\nProgramm durch Benutzer unterbrochen.")
            break
        except Exception as e:
            print(f"Unerwarteter Fehler: {e}")
        
        input("\nDrücken Sie Enter, um fortzufahren...")

if __name__ == "__main__":
    main() 