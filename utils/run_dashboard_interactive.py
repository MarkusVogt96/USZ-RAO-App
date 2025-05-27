"""
Interactive Tumorboard Analytics Dashboard
Vollständig interaktives Dashboard mit Filtern, Tabs und anklickbaren Elementen
"""

import sys
import logging
import webbrowser
from pathlib import Path

# Add parent directory to path (to access utils from pages folder)
sys.path.insert(0, str(Path(__file__).parent.parent))

def main():
    """Main function to run interactive dashboard in browser"""
    print("🏥 Tumorboard Analytics Dashboard (Interaktive Version)")
    print("=" * 70)
    print("🎯 Features:")
    print("   ✅ Dropdown-Filter für Tumorboards und Zeiträume")
    print("   ✅ Anklickbare Tabs für verschiedene Ansichten")
    print("   ✅ Interaktive Karten und Tabellen")
    print("   ✅ Hover-Effekte und Tooltips")
    print("   ✅ Dynamische Datenfilterung")
    print("   ✅ Responsive Design")
    print("")
    
    try:
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
        # Import required modules
        from utils.dashboard_html_generator import generate_complete_dashboard
        
        print("📊 Generiere interaktives Dashboard mit eingebetteten Daten...")
        
        # Generate interactive HTML with embedded data
        html_file = generate_complete_dashboard(interactive=True)
        if html_file:
            print(f"✅ Interaktives Dashboard generiert: {html_file}")
        else:
            print("❌ Fehler beim Generieren des Dashboards")
            return
        
        print("🌐 Öffne interaktives Dashboard im Browser...")
        
        # Open in default browser
        html_path = Path(html_file)
        file_url = f"file:///{html_path.as_posix()}"
        webbrowser.open(file_url)
        
        print("✅ Interaktives Dashboard im Browser geöffnet!")
        print(f"📂 Dashboard-Datei: {html_file}")
        print(f"🔗 URL: {file_url}")
        print("")
        print("🎮 Interaktive Features:")
        print("   🔽 Dropdown-Menüs: Wählen Sie Tumorboards und Zeiträume")
        print("   📑 Tabs: Klicken Sie auf verschiedene Bereiche")
        print("   📊 Karten: Klicken Sie auf Metriken für Details")
        print("   📋 Tabellen: Klicken Sie auf Zeilen für Aktionen")
        print("   🎯 Buttons: Wechseln Sie zwischen Ansichten")
        print("   🔄 Filter: Kombinieren Sie verschiedene Filter")
        print("")
        print("💡 Tipps:")
        print("   - Hovern Sie über Elemente für Tooltips")
        print("   - Nutzen Sie die Filter-Kombinationen")
        print("   - Klicken Sie auf Balken und Fortschrittsanzeigen")
        print("   - Wechseln Sie zwischen Tabellen- und Balkenansicht")
        print("   - Aktualisieren Sie die Browser-Seite für neue Daten")
        print("")
        
        # Keep script running so user can see the output
        input("Drücken Sie Enter zum Beenden...")
        
    except ImportError as e:
        print(f"❌ Import-Fehler: {e}")
        print("💡 Stellen Sie sicher, dass alle Module verfügbar sind")
        sys.exit(1)
        
    except Exception as e:
        print(f"❌ Fehler beim Starten des interaktiven Dashboards: {e}")
        logging.error(f"Interactive dashboard startup error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 