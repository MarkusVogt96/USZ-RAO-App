# USZ RAO App - Übersicht

## 1. Projektübersicht

Diese PyQt6-Anwendung dient mehreren Hauptzwecken für die Radioonkologie am USZ:

1.  **Wissensdatenbank:** Bereitstellung einer strukturierten Ansicht von Tumorentitäten mit zugehörigen Contouring Instructions und Standard Operating Procedures (SOPs).
2.  **Automatisierungs-Tool:** Ausführung von Python-Skripten zur Automatisierung wiederkehrender Aufgaben im klinischen Informationssystem (KISIM), hauptsächlich mittels GUI-Automatisierung (PyAutoGUI).
3.  **Tumorboard Organisation:** Gibt eine Übersicht über die Tumorboards der Woche (Tag, Zeit, Ort), stellt die jeweiligen Tumorboard-Listen am Morgen des jeweiligen Tages zur Verfügung und bietet ein Digitalisierungstool für die besprochenen Patientenfälle.

## 2. Kernfunktionen

Die Anwendung ist in mehrere Reiter (Tabs) unterteilt:

*   **Tumor Navigator (`TumorGroupPage`):** Navigiert durch Tumorgruppen zu spezifischen Tumorentitäten. Die einzelnen Entitätsseiten (`EntityPage`) zeigen dann zugehörige SOPs (als PDF-Dateien) und Contouring Instructions an.
*   **KISIM Scripts (`KisimPage`):** Bietet eine Oberfläche (Kacheln) zum Starten verschiedener Automatisierungs-Skripte für KISIM.
*   **Script Output (`CmdScriptsPage`):** Zeigt die Echtzeit-Ausgabe des aktuell laufenden KISIM-Skripts an, ermöglicht Benutzereingaben für das Skript und bietet eine "STOP"-Funktion.
*   **Tumor Boards Page:** Zeigt eine Übersicht über die Tumorboards der Woche sowie Kacheln für die jeweiligen Tumorboards an, mit denen interagiert werden kann, um Listen einzusehen oder Fälle zu digitalisieren.
*   **Backoffice (`BackofficePage`):** Zentrale Verwaltungsseite für administrative Aufgaben mit automatisiertem Indexing der Tumorboard-Ordner und Zugang zu abgeschlossenen Tumorboards.

## 3. Wichtige Ordner und Dateien
C:.
├───.cursor
│   └───rules
├───assets
│   └───sop
│       ├───Fernmetastasen
│       │   ├───Hirnmetastasen
│       │   ├───palliative RT von Knochenmetastasen
│       │   └───SBRT extrakranieller Hirnmetastasen
│       ├───Gastrointestinale Tumore
│       │   ├───Anal-Ca
│       │   ├───CCC
│       │   ├───HCC
│       │   ├───Pankreas-Ca
│       │   ├───Rektum-Ca
│       │   └───Ösophagus-Ca
│       ├───Gutartige Erkrankungen
│       ├───Gynäkologische Tumore
│       │   ├───Cervix-Ca
│       │   ├───Endometrium-Ca
│       │   ├───Mamma-Ca
│       │   └───Vulva-Ca
│       ├───Hauttumore
│       │   ├───BCC und cSCC
│       │   ├───Melanom
│       │   └───Merkelzell-Ca
│       ├───Kopf-Hals-Tumore
│       │   ├───Larynx und Hypopharynx
│       │   ├───Nasenkarzinom
│       │   ├───Nasopharynxkarzinom
│       │   ├───Oropharynxkarzinom
│       │   └───Speicheldrüsenkarzinom
│       ├───Lymphome
│       │   ├───DLBCL
│       │   ├───Hodgkin-Lymphom
│       │   ├───MALT
│       │   └───Plasmozytom
│       ├───Neuroonkologie
│       │   ├───Anaplastisches Astrozytom
│       │   ├───Glioblastom
│       │   ├───Meningeom
│       │   ├───Oligodendrogliom
│       │   ├───Schwannom
│       │   └───Vestibularisschwannom
│       ├───Thorakale Tumore
│       │   ├───Mesotheliom
│       │   ├───NSCLC
│       │   └───SCLC
│       └───Urogenitale Tumore
│           ├───Blasen-Ca
│           ├───Prostata-Ca
│           └───RCC
├───components
│   └───__pycache__
├───offline_packages
│   ├───easyocr_models
│   ├───python_modules
│   └───tesseract
│       ├───doc
│       └───tessdata
│           ├───configs
│           ├───script
│           └───tessconfigs
├───pages
│   ├───entity_pages
│   │   └───__pycache__
│   ├───tumorgroup_pages
│   │   └───__pycache__
│   └───__pycache__
└───scripts
    ├───screenshots pyautogui
    │   ├───atrao
    │   ├───chemo
    │   ├───ecres
    │   ├───etrao
    │   ├───icd
    │   ├───kons
    │   ├───lab
    │   ├───m
    │   ├───patdata
    │   ├───physio
    │   ├───reha
    │   ├───sb
    │   ├───spitex
    │   ├───stemp
    │   └───UNIVERSAL
    │       ├───bereiche
    │       ├───bereich_berichte
    │       ├───bereich_bilder
    │       ├───bereich_dashboard
    │       ├───bereich_einzelresultate
    │       ├───bereich_exttools
    │       ├───bereich_kurve
    │       ├───bereich_laborkumulativ
    │       ├───bereich_leistungen
    │       ├───bereich_pflegedok
    │       ├───bereich_pflegeprozess
    │       ├───bereich_pflegeprozesse
    │       ├───bereich_physioergo
    │       ├───bereich_probleme
    │       ├───bereich_stammdaten
    │       ├───bereich_workflows
    │       ├───image_preprocessing
    │       ├───KG_management
    │       └───kisim_suche
    └───__pycache__

## 4. Wichtige Mechanismen

### 4.1. Wissensdatenbank / Tumor Navigator

*   Die `TumorGroupPage` (Startseite des "Tumor Navigator"-Tabs) zeigt Kacheln für übergeordnete Tumorgruppen an (z.B. Neuroonkologie, Kopf-Hals-Tumore).
*   Ein Klick auf eine Tumorgruppe führt zur entsprechenden spezifischen Gruppenseite (z.B. `NeuroonkologiePage`).
*   Auf der spezifischen Gruppenseite werden Kacheln für einzelne Tumorentitäten dieser Gruppe angezeigt.
*   Ein Klick auf eine Tumorentität öffnet die `EntityPage` für diese Entität.
*   Die `EntityPage` lädt und zeigt Links zu relevanten SOP-PDF-Dateien aus dem Verzeichnis `assets/sop/<GroupName>/<EntityName>/`. Ein Klick auf einen PDF-Link öffnet die Datei im integrierten `PdfReaderPage`.
*   Die `EntityPage` enthält zudem einen (aktuell als Platzhalter implementierten) Bereich für Contouring Instructions, der zur `ContouringPage` führen würde.

### 4.2. KISIM Scripting (`scripts/` & `pages/`)

*   Die `KisimPage` zeigt Kacheln an, die auf den Skript-Definitionen in `pages/kisim_page.py` basieren.
*   Ein Klick auf eine Kachel löst die Ausführung des entsprechenden Python-Skripts aus dem `scripts/`-Ordner über die `CmdScriptsPage` aus.
*   Die `CmdScriptsPage` verwendet `QProcess` (in Entwicklungsumgebung) oder `threading` und `subprocess`/Modulimport (in der gebundelten .exe), um die Skripte auszuführen und deren Standard-Output/-Error anzuzeigen.
*   Benutzereingaben für die Skripte werden über ein `QLineEdit` in der `CmdScriptsPage` an den laufenden Prozess/Thread weitergeleitet.
*   Die Skripte in `scripts/` nutzen häufig `pyautogui` für GUI-Automatisierung und greifen auf Screenshots in `scripts/screenshots pyautogui/` zurück.
*   Viele Skripte nutzen das Modul `scripts/UNIVERSAL.py`, das zentrale Hilfsfunktionen (z.B. Laden von Patientendaten, GUI-Interaktionen, OCR) bereitstellt.

### 4.3. Patientendaten (`patdata`)

*   **Speicherort:** Patientenspezifische Daten werden in JSON-Dateien gespeichert. Diese befinden sich **nicht** im Anwendungsverzeichnis, sondern in einem dedizierten Ordner namens `patdata` direkt im **Benutzerverzeichnis** (`%USERPROFILE%\patdata` unter Windows, `~/patdata` auf anderen Systemen).
*   **Zugriff:** Die Skripte (insbesondere `UNIVERSAL.py`) greifen auf diesen Ordner zu, um Patientendaten zu laden (`UNIVERSAL.load_json`) oder zu speichern (z.B. in `patdata.py`, `viewjson.py`).
*   **Persistenz:** Da der Ordner außerhalb der Anwendung liegt, bleiben die Daten über Anwendungs-Updates und -Neustarts hinweg erhalten.
*   **Erstellung:** Der `patdata`-Ordner wird bei Bedarf automatisch von der Anwendung im Benutzerverzeichnis erstellt.
*   **Struktur einer `patdata`-JSON-Datei (Beispiel):**
    ```json
    {
        "nachname": "Mustermann",
        "vorname": "Max",
        "geburtsdatum": "01.01.1970",
        "alter": 54,
        "geschlecht": "M",
        "patientennummer": "12345678",
        "eintrittsdatum": "22.05.2025",
        "spi": "37%",
        "rea": "Nein",
        "ips": "Ja",
        "oberarzt": "Brown",
        "simultane_chemotherapie": "ja",
        "chemotherapeutikum": "Cisplatin",
        "therapieintention": "kurativ",
        "fraktionen_woche": "5 pro Woche",
        "behandlungskonzept_serie1": "Resektionshöhle des Glioblastoms mit 30 x 2 Gy = 60 Gy",
        "behandlungskonzept_serie2": "",
        "behandlungskonzept_serie3": "",
        "behandlungskonzept_serie4": "",
        "datum_erste_rt": "16.07.2025",
        "datum_letzte_rt": "28.08.2025",
        "ecog": 1,
        "tumor": "Glioblastom temporal rechts",
        "zimmer": "G 21",
        "aufnahmegrund": "häusliche Dekompensation bei reduziertem Allgemeinzustand und Schmerzexazerbation"
    }
    ```

### 4.4. Tumorboard Organisation

*   Die `Tumor Boards Page` bietet eine Übersicht der wöchentlichen Tumorboards inklusive Tag, Zeit und Ort.
*   Sie ermöglicht den Zugriff auf die jeweiligen Tumorboard-Listen, die typischerweise am Morgen des Board-Tages bereitgestellt werden.
*   Ein integriertes Tool unterstützt die Digitalisierung der Patientenfälle, die im Tumorboard besprochen wurden (z.B. Erfassung strukturierter Daten, Notizen).
*   **Automatische Aktualisierung:** Die `SpecificTumorboardPage` aktualisiert automatisch die angezeigten Tumorboard-Daten (aktuelle und vergangene Termine) jedes Mal, wenn die Seite aufgerufen wird. Dies gewährleistet, dass Änderungen an den Tumorboard-Ordnern (Hinzufügen/Löschen von Datums-Ordnern) sofort ohne App-Neustart sichtbar werden.
*   **Intelligente Pfad-Hierarchie:** Das System verwendet eine Fallback-Strategie für Tumorboard-Daten:
    1. **Priorität 1:** `K:\RAO_Projekte\App\tumorboards\` (Intranet/primär)
    2. **Priorität 2:** `{Benutzer-Home}\tumorboards\` (lokal/Fallback)
    3. **Fehlerbehandlung:** Automatische Warnungen bei Fallback-Nutzung oder Fehlermeldungen bei komplettem Ausfall
*   **Export-Import-Konsistenz:** Das System merkt sich, von welchem Pfad die Tumorboard-Daten geladen wurden, und exportiert beim Abschließen der Tumorboard-Session automatisch in denselben Pfad:
    - **Intranet-Export:** Wurden Daten von `K:\RAO_Projekte\App\tumorboards\` geladen → Export erfolgt nach `K:\`
    - **Lokaler Export:** Wurden Daten von `{Benutzer-Home}\tumorboards\` geladen → Export erfolgt lokal mit Administratoren-Warnung
*   **Administratoren-Warnung bei lokalem Export:** Nach Abschluss eines lokalen Tumorboards wird automatisch eine Warnung angezeigt, die darauf hinweist, dass die Daten manuell auf den Server übertragen werden müssen

### 4.5. Automatisches Datenbank-Backup-System

Das System implementiert ein robustes Backup-System für die zentrale SQLite-Datenbank:

*   **Backup-Auslöser:** Automatische Backups werden erstellt vor:
    - Synchronisation aller Collection-Excel-Dateien zur Datenbank (`sync_all_collection_files()`)
    - Import einzelner Collection-Excel-Dateien (`import_collection_excel()` mit `create_backup=True`)
*   **Backup-Speicherort:** `{Benutzer-Home}/tumorboards/__SQLite_database/backup/`
*   **Backup-Namensformat:** `YYYY-MM-DD_HHMM_master_tumorboard.db`
    - Beispiel: `2024-06-26_2209_master_tumorboard.db`
*   **Backup-Logik:**
    1. Prüfung ob Datenbank-Datei existiert (bei neuer Installation nicht nötig)
    2. Automatische Erstellung des Backup-Verzeichnisses falls nicht vorhanden
    3. Schließung aller offenen Datenbankverbindungen vor Backup
    4. Kopie der aktuellen `master_tumorboard.db` mit Zeitstempel
    5. Logging des Backup-Erfolgs/Fehlers
*   **Fehlerbehandlung:** Bei Backup-Fehlern wird eine Warnung geloggt, aber der Import/Sync wird fortgesetzt
*   **Implementierung:** Die Backup-Funktionalität ist in der `TumorboardDatabase.create_database_backup()` Methode implementiert und wird automatisch von den entsprechenden Sync-Funktionen aufgerufen

*   Die genaue Implementierung der Datenhaltung und des Digitalisierungstools ist noch in Entwicklung, greift aber potenziell auf externe Dateien oder eine interne Datenstruktur zu.

### 4.6. Backoffice-System

Das Backoffice-System bietet administrative Funktionen für die Verwaltung und Nachbearbeitung abgeschlossener Tumorboards:

#### 4.6.1. Backoffice-Startseite (`BackofficePage`)
*   **Automatisches Indexing:** Beim Laden der Seite erfolgt automatisch ein Indexing aller Tumorboard-Ordner unter `K:\RAO_Projekte\App\tumorboards`
*   **Verbindungsprüfung:** Das System prüft die Erreichbarkeit des K:-Laufwerks und zeigt entsprechende Fehlermeldungen bei Verbindungsproblemen
*   **Zugang zu abgeschlossenen Tumorboards:** Zentraler Button führt zur Übersicht aller finalisierter Tumorboard-Sessions

#### 4.6.2. Abgeschlossene Tumorboards (`BackofficeTumorboardsPage`)
*   **Detailliertes Indexing:** Systematische Durchsuchung aller Tumorboard-Entitäten nach abgeschlossenen Sessions:
    - Erkennung von Datums-Ordnern im Format `dd.mm.yyyy`
    - Prüfung auf `*timestamp*` Dateien als Abschluss-Indikator
    - Validierung der entsprechenden Excel-Dateien (`{datum}.xlsx`)
*   **Filter- und Sortierfunktionen:**
    - **Zeitintervall-Filter:** Auswahl von Datum bis Datum
    - **Entitäts-Filter:** Filterung nach spezifischen Tumorboard-Typen (z.B. Neuro, Thorax)
    - **Sortierbare Tabelle:** Sortierung nach Datum oder Tumorboard-Entität durch Klick auf Spaltenköpfe
*   **Direkte Navigation:** Doppelklick auf Tabelleneinträge öffnet den spezialisierten Excel Viewer

#### 4.6.3. Excel Viewer Backoffice (`BackofficeExcelViewerPage`)
*   **Spezialisierte Ansicht:** Angepasste Version des Standard Excel Viewers ohne Start/Edit Tumorboard Funktionen
*   **QISM Abrechnungsintegration:**
    - **Abrechnungs-Button:** Prominent platzierter Button für automatisierte Leistungsabrechnung
    - **Bestätigungsdialog:** Sicherheitsabfrage mit Voraussetzungsprüfung (QISM geöffnet, Benutzer eingeloggt)
    - **Script-Ausführung:** Automatischer Aufruf des `scripts/abrechnung.py` Scripts
    - **Fehlerbehandlung:** Umfassende Behandlung von Script-Fehlern, Timeouts und Ausnahmen
*   **Excel-Anzeige:** Vollständige Darstellung der Tumorboard-Daten mit allen Standard-Formatierungen und Spalten-Anpassungen

#### 4.6.4. Technische Details
*   **Pfad-Konfiguration:** Hard-coded Zugriff auf `K:\RAO_Projekte\App\tumorboards` (keine lokalen Fallbacks)
*   **Threading:** Indexing-Prozesse laufen in separaten Threads um UI-Reaktivität zu gewährleisten
*   **Fehlerbehandlung:** Robuste Behandlung von Netzwerkfehlern, Berechtigungsproblemen und fehlenden Dateien
*   **Breadcrumb-Navigation:** Integrierte Navigation zwischen Backoffice-Seiten mit automatischer Breadcrumb-Generierung

#### 4.6.5. Task Management System
Das erweiterte Backoffice-System umfasst ein zentralisiertes Task Management für administrative Aufgaben:

**Hauptkategorien:**
*   **Leistungsabrechnungen:** Verwaltung offener QISM-Abrechnungen für abgeschlossene Tumorboards
*   **Erstkonsultationen:** Management wartender Patienten für Terminvergabe

**Zentrale Übersicht (`BackofficePage`):**
*   **Task-Aggregation:** Sammlung und Darstellung aller offenen Aufgaben aus verschiedenen Kategorien
*   **Klickbare Task-Items:** Direkte Navigation zu spezialisierten Verwaltungsseiten durch Klick auf Aufgaben-Übersicht
*   **Echtzeit-Statistiken:** Anzeige aktueller Zahlen (Anzahl offener Abrechnungen, wartende Patienten, etc.)

**Leistungsabrechnungen (`BackofficePageLeistungsabrechnungen`):**
*   **Abrechnungsübersicht:** Tabellarische Darstellung aller offenen Tumorboard-Abrechnungen
*   **Statistik-Dashboard:** Visualisierung von Kennzahlen (Anzahl offener Boards, geschätzter Betrag, älteste Abrechnung)
*   **Direkte Bearbeitung:** Integration von Abrechnung-Scripts pro Tumorboard
*   **Filterfunktionen:** Suche und Filterung nach Tumorboard-Typ, Datum, Status

**Erstkonsultationen (`BackofficePageErstkonsultationen`):**
*   **Warteschlangen-Management:** Übersicht aller wartenden Patienten für Erstkonsultationen
*   **Priorisierung:** Farbkodierte Darstellung nach Dringlichkeit (< 7 Tage, Normal, Niedrig)
*   **Filter-System:** Filterung nach Priorität, Tumorart, Anmeldedatum
*   **Terminaufgebot:** Direkte Integration für Terminvergabe und Patientenbenachrichtigung

**Navigation & UX:**
*   **Unified Navigation:** Einheitliche Navigation zwischen allen Backoffice-Seiten
*   **Zurück-Buttons:** Konsistente Rücknavigation mit Session-Schutz
*   **Visual Feedback:** Hover-Effekte und Farbkodierung für bessere Benutzererfahrung