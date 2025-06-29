#!/usr/bin/env python3
"""
Interactive Dashboard Generator for Tumorboard Analytics
This script generates a complete HTML dashboard with embedded data and opens it in the browser.
"""

import sys
import os
import webbrowser
import logging
from pathlib import Path

# Add parent directory to Python path for imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from utils.dashboard_html_generator import generate_complete_dashboard
from utils.database_utils import sync_all_collection_files
from utils.dashboard_data_export import test_aufgebot_mapping

def main():
    """Main function to generate and open dashboard"""
    print("🚀 Generiere interaktives Tumorboard-Dashboard...")
    
    # Setup logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    try:
        # Test Aufgebot mapping
        print("\n🔧 Teste Aufgebot-Mapping...")
        if test_aufgebot_mapping():
            print("✅ Aufgebot-Mapping Test erfolgreich")
        else:
            print("❌ Aufgebot-Mapping Test fehlgeschlagen")
        
        # Sync collection files to database
        print("\n📊 Synchronisiere Collection-Dateien mit der Datenbank...")
        sync_success = sync_all_collection_files()
        if sync_success:
            print("✅ Datenbank-Synchronisation erfolgreich")
        else:
            print("⚠️ Datenbank-Synchronisation fehlgeschlagen oder keine neuen Daten")
        
        # Generate dashboard  
        print("\n🎨 Generiere Dashboard HTML...")
        
        # Determine correct tumorboard base path
        k_path = Path("K:/RAO-Projekte/App/tumorboards")
        if k_path.exists() and k_path.is_dir():
            tumorboard_base_path = k_path
            print(f"✅ Verwende K:-Pfad: {tumorboard_base_path}")
        else:
            tumorboard_base_path = Path.home() / "tumorboards"
            print(f"⚠️ K:-Pfad nicht verfügbar, verwende Fallback: {tumorboard_base_path}")
        
        dashboard_path = generate_complete_dashboard(interactive=True, tumorboard_base_path=tumorboard_base_path)
        
        if dashboard_path and Path(dashboard_path).exists():
            print(f"✅ Dashboard erfolgreich generiert: {dashboard_path}")
            
            # Open in browser
            print("🌐 Öffne Dashboard im Browser...")
            webbrowser.open(f"file://{dashboard_path}")
            print("Dashboard geöffnet! Prüfen Sie Ihren Browser.")
            
            # Show summary
            print(f"\n📍 Dashboard-Pfad: {dashboard_path}")
            print("📈 Features:")
            print("   • Übersicht mit Key Metrics")
            print("   • Tumorboard-Analyse")
            print("   • Radiotherapie-Statistiken")
            print("   • 🆕 Art des Aufgebots (Kat I/II/III)")
            print("   • ICD-Code-Analyse")
            print("   • Zeitverlauf")
            print("   • Interaktive Charts")
            
        else:
            print("❌ Fehler beim Generieren des Dashboards")
            return False
            
    except Exception as e:
        print(f"❌ Fehler: {e}")
        logging.error(f"Error in dashboard generation: {e}")
        return False
    
    return True


def test_aufgebot_only():
    """Test only the Aufgebot functionality"""
    print("🔧 Teste nur Aufgebot-Funktionalität...")
    
    try:
        from utils.dashboard_data_export import DashboardDataExporter
        import json
        
        exporter = DashboardDataExporter()
        data_path = exporter.export_dashboard_data()
        
        if data_path and Path(data_path).exists():
            with open(data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            print("\n📊 Aufgebot-Daten:")
            if 'aufgebot_data' in data:
                print("✅ Aufgebot-Daten gefunden:")
                print(json.dumps(data['aufgebot_data'], indent=2, ensure_ascii=False))
            else:
                print("❌ Keine Aufgebot-Daten gefunden")
                print("Verfügbare Keys:", list(data.keys()))
        
        return True
        
    except Exception as e:
        print(f"❌ Test fehlgeschlagen: {e}")
        return False


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--test-aufgebot":
        test_aufgebot_only()
    else:
        main() 