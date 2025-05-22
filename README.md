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
*   Die genaue Implementierung der Datenhaltung und des Digitalisierungstools ist noch in Entwicklung, greift aber potenziell auf externe Dateien oder eine interne Datenstruktur zu.