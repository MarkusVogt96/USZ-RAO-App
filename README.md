# USZ RAO App - Übersicht

## 1. Projektübersicht

Diese PyQt6-Anwendung dient zwei Hauptzwecken für die Radioonkologie am USZ:

1.  **Wissensdatenbank:** Bereitstellung einer strukturierten Ansicht von Tumorentitäten mit zugehörigen Contouring Instructions und Standard Operating Procedures (SOPs).
2.  **Automatisierungs-Tool:** Ausführung von Python-Skripten zur Automatisierung wiederkehrender Aufgaben im klinischen Informationssystem (KISIM), hauptsächlich mittels GUI-Automatisierung (PyAutoGUI).

## 2. Kernfunktionen

Die Anwendung ist in mehrere Reiter (Tabs) unterteilt:

*   **Tumorentitäten (`HomePage`):** Zeigt Informationen zu verschiedenen Tumorentitäten an (aktuell noch rudimentär).
*   **KISIM Scripts (`KisimPage`):** Bietet eine Oberfläche (Kacheln) zum Starten verschiedener Automatisierungs-Skripte für KISIM. Enthält Buttons zum Öffnen der relevanten Ordner (`scripts`, `patdata`).
*   **Script Output (`CmdScriptsPage`):** Zeigt die Echtzeit-Ausgabe des aktuell laufenden KISIM-Skripts an, ermöglicht Benutzereingaben für das Skript und bietet eine "STOP"-Funktion.

## 3. Wichtige Ordner und Dateien

```
├───.cursor
│   └───rules
├───assets
│   ├───py scripts
│   └───sop
├───build
│   ├───main
│   │   └───localpycs
│   └───main_stable
│       └───localpycs
├───components
│   └───__pycache__
├───dist
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
```

## 4. Wichtige Mechanismen

### 4.1. KISIM Scripting (`scripts/` & `pages/`)

*   Die `KisimPage` zeigt Kacheln an, die auf den Skript-Definitionen in `pages/kisim_page.py` basieren.
*   Ein Klick auf eine Kachel löst die Ausführung des entsprechenden Python-Skripts aus dem `scripts/`-Ordner über die `CmdScriptsPage` aus.
*   Die `CmdScriptsPage` verwendet `QProcess` (in Entwicklungsumgebung) oder `threading` und `subprocess`/Modulimport (in der gebundelten .exe), um die Skripte auszuführen und deren Standard-Output/-Error anzuzeigen.
*   Benutzereingaben für die Skripte werden über ein `QLineEdit` in der `CmdScriptsPage` an den laufenden Prozess/Thread weitergeleitet.
*   Die Skripte in `scripts/` nutzen häufig `pyautogui` für GUI-Automatisierung und greifen auf Screenshots in `scripts/screenshots pyautogui/` zurück.
*   Viele Skripte nutzen das Modul `scripts/UNIVERSAL.py`, das zentrale Hilfsfunktionen (z.B. Laden von Patientendaten, GUI-Interaktionen, OCR) bereitstellt.

### 4.2. Patientendaten (`patdata`)

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
        "patientennummer": "1234567",
        "eintrittsdatum": "15.07.2024",
        "spi": "...",
        "rea": "...",
        "ips": "...",
        "oberarzt": "Brown",
        "simultane_chemotherapie": "ja",
        "chemotherapeutikum": "Cisplatin",
        "therapieintention": "kurativ",
        "fraktionen_woche": 5,
        "behandlungskonzept_serie1": "...",
        "behandlungskonzept_serie2": null,
        "behandlungskonzept_serie3": null,
        "behandlungskonzept_serie4": null,
        "datum_erste_rt": "16.07.2024",
        "datum_letzte_rt": "28.08.2024",
        "ecog": 1,
        "tumor": "Beispiel Tumor",
        "zimmer": "A101",
        "aufnahmegrund": "Beispiel Grund"
    }
    ```

## 5. Build-Prozess (PyInstaller)

*   Die Anwendung kann mittels PyInstaller in eine eigenständig ausführbare `.exe`-Datei für Windows gebündelt werden.
*   Die Konfiguration erfolgt über die `main.spec`-Datei.
*   **Wichtig:**
    *   Der `patdata`-Ordner wird **nicht** in das Bundle aufgenommen (siehe `datas`-Sektion in `main.spec`).
    *   Abhängigkeiten wie Tesseract und EasyOCR-Modelle werden aus dem `offline_packages`-Ordner in das Bundle kopiert.
    *   Notwendige `hiddenimports` sind in `main.spec` definiert.
    *   **Offline-Module:** Für alle Python-Module, die von den Skripten im `scripts/`-Ordner verwendet werden (z.B. `pyautogui`, `clipboard`, `openpyxl`), müssen die entsprechenden Wheel-Dateien (`.whl`) im Verzeichnis `offline_packages/python_modules` vorhanden sein. PyInstaller benötigt diese, um die Abhängigkeiten korrekt in die `.exe`-Datei einzubinden, insbesondere wenn der Build-Prozess offline erfolgt.
*   **Befehl zum Bauen (Beispiel):** `pyinstaller main.spec` (im Hauptverzeichnis ausführen)


