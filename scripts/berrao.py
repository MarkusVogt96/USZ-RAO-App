# -*- coding: utf-8 -*-
print("Starte Skript berrao.py (inkl. Woko)...")
import UNIVERSAL # Import UNIVERSAL first
import json
import pyautogui
import os
import sys
import time
import datetime
import clipboard
import traceback
import fliesstexte # <<< NEUER IMPORT

# --- Define Relative Paths ---
# ... (Pfade bleiben gleich) ...
script_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.dirname(script_dir)
screenshots_dir = os.path.join(script_dir, 'screenshots pyautogui')
image_base_path = os.path.join(screenshots_dir, "UNIVERSAL", "bereich_berichte") # Path for report buttons
# Define the absolute path to patdata in the user's home directory
user_home = os.path.expanduser("~") 
patdata_dir = os.path.join(user_home, "patdata")

print(f"Script directory (berrao.py): {script_dir}")
print(f"App directory: {app_dir}")
print(f"Patient data directory: {patdata_dir}")
print(f"Screenshots base directory: {screenshots_dir}")
print(f"Image base path for report actions: {image_base_path}")

# --- Globale Konfigurationen ---
MAX_SEARCH_ATTEMPTS = 150
SEARCH_INTERVAL = 0.05
CONFIDENCE_LEVEL = 0.8
ACTION_DELAY = 0.01

# --- Globale Variablen ---
patdata = None
bericht_typ = None
glossary = {}

#Variablen aus patdata
nachname = None
vorname = None
geburtsdatum = None
alter = None
geschlecht = None
patientennummer = None
eintrittsdatum = None
spi = None
rea = None
ips = None
tumor = None
entity = None
icd_code = None
secondary_entity = None
secondary_icd_code = None
oberarzt = None
simultane_chemotherapie = None
chemotherapeutikum = None
therapieintention = None
fraktionen_woche = None
behandlungskonzept_serie1 = None
behandlungskonzept_serie2 = None
behandlungskonzept_serie3 = None
behandlungskonzept_serie4 = None
rt_konzept = None
datum_erste_rt = None
datum_letzte_rt = None
ecog = None
zimmer = None
aufnahmegrund = None

#Variablen für workflow
soll_leistung_erfasst_werden = False
bericht_typ_fuer_leistung = None
soll_symp_vor_rt_erfasst_werden = False
soll_akuttox_nach_rt_erfasst_werden = False
soll_nachsorgeformular_erfasst_werden = False

# --- Funktionen ---
def open_JSON():
    # ... (Funktion bleibt gleich) ...
    global patdata, patientennummer
    patientennummer = input("Bitte patientennummer angeben: ")
    if not patientennummer.isdigit():
        print("FEHLER: Patientennummer muss Zahl sein.")
        sys.exit(1)
    patdata = UNIVERSAL.load_json(patientennummer)
    if patdata == "patdata":
        print("berrao.py: User will patdata ausführen...")
        original_sys_path = list(sys.path)
        if app_dir not in sys.path:
            sys.path.insert(0, app_dir)
            print(f"Temporär '{app_dir}' zu sys.path hinzugefügt.")
        try:
            import patdata
            print("patdata importiert.")
        except ImportError:
            print(f"FEHLER: 'patdata.py' Import fehlgeschlagen.")
            traceback.print_exc()
            sys.exit("Abbruch.")
        except Exception as e:
            print(f"Fehler bei patdata Ausführung: {e}")
            traceback.print_exc()
            sys.exit("Abbruch.")
        finally:
            sys.path = original_sys_path
            print("sys.path wiederhergestellt.")
        print("JSON vermutlich angelegt. Bitte Skript erneut starten.")
        sys.exit()
    elif not isinstance(patdata, dict):
        print(f"Fehler: JSON für '{patientennummer}' nicht geladen.")
        sys.exit()


    

def dictionary_ohne_None():
    # ... (Funktion bleibt gleich - wichtig für Variablenextraktion!) ...
    global patdata, nachname, vorname, geburtsdatum, alter, geschlecht, patientennummer, eintrittsdatum, spi, rea, ips, tumor, entity, icd_code, secondary_entity, secondary_icd_code, oberarzt, simultane_chemotherapie, chemotherapeutikum, therapieintention, fraktionen_woche, behandlungskonzept_serie1, behandlungskonzept_serie2, behandlungskonzept_serie3, behandlungskonzept_serie4, rt_konzept, datum_erste_rt, datum_letzte_rt, ecog, zimmer, aufnahmegrund
    if isinstance(patdata, dict):
        print("Lese Patientendaten aus Dictionary...")
        nachname = patdata.get("nachname", "")
        vorname = patdata.get("vorname", "")
        geburtsdatum = patdata.get("geburtsdatum", "")
        alter = patdata.get("alter", "")
        geschlecht = patdata.get("geschlecht", "")
        patientennummer = patdata.get("patientennummer", "")
        eintrittsdatum = patdata.get("eintrittsdatum", "")
        spi = patdata.get("spi", "")
        rea = patdata.get("rea", "")
        ips = patdata.get("ips", "")
        tumor = patdata.get("tumor", "")
        entity = patdata.get("entity", "")
        icd_code = patdata.get("icd_code", "")
        secondary_entity = patdata.get("secondary_entity", "")
        secondary_icd_code = patdata.get("secondary_icd_code", "")
        oberarzt = patdata.get("oberarzt", "")
        simultane_chemotherapie = patdata.get("simultane_chemotherapie", "")
        chemotherapeutikum = patdata.get("chemotherapeutikum", "")
        therapieintention = patdata.get("therapieintention", "")
        fraktionen_woche = patdata.get("fraktionen_woche", "")
        behandlungskonzept_serie1 = patdata.get("behandlungskonzept_serie1", "")
        behandlungskonzept_serie2 = patdata.get("behandlungskonzept_serie2", "")
        behandlungskonzept_serie3 = patdata.get("behandlungskonzept_serie3", "")
        behandlungskonzept_serie4 = patdata.get("behandlungskonzept_serie4", "")
        datum_erste_rt = patdata.get("datum_erste_rt", "")
        datum_letzte_rt = patdata.get("datum_letzte_rt", "")
        ecog = patdata.get("ecog", "")
        zimmer = patdata.get("zimmer", "")
        aufnahmegrund = patdata.get("aufnahmegrund", "")
        print(f"29 Variablen aus patdata aus JSON erfolgreich geladen\n")
    else: print("FEHLER: patdata ist kein Dictionary."); sys.exit()

def get_initial_user_inputs():
    global therapieintention, nachsorgeformular_typ, bericht_typ, soll_leistung_erfasst_werden, bericht_typ_fuer_leistung, soll_akuttox_nach_rt_erfasst_werden, soll_symp_vor_rt_erfasst_werden, soll_nachsorgeformular_erfasst_werden
    #bericht_typ erfragen
    print("\nAuswahl tätigen: Welche Art Bericht wird angelegt:")
    print("[e] Erstkons. [a] Abschluss [k] Klin. VK [t] Telef. VK [w] Woko")
    bericht_typ_map = {'e': 'Erstkonsultation', 'a': 'Abschlusskontrolle', 'k': 'Klinische VK', 't': 'Telefonische VK', 'w': 'Wochenkontrolle'}
    while True:
        typ_eingabe = input("Ihre Wahl (e/a/k/t/w): ").strip().lower()
        if typ_eingabe in bericht_typ_map:
            bericht_typ = typ_eingabe
            bericht_typ_fuer_leistung = bericht_typ
            break
        else:
            print("Ungültige Eingabe.")
    print(f"\nBerichtstyp '{bericht_typ_map[bericht_typ]}' (Typ: {bericht_typ}) gewählt.")


    #Tox-Formular erfassen?
    if bericht_typ == 'e':
        while True:
            soll_symp_vor_rt_erfasst_werden = input("Soll Formular 'Symptome vor RT' mit angelegt werden (j/n)?")
            if soll_symp_vor_rt_erfasst_werden == 'j':
                soll_symp_vor_rt_erfasst_werden = True
                break
            elif soll_symp_vor_rt_erfasst_werden == 'n':
                soll_symp_vor_rt_erfasst_werden = False
                break
            else:
                print("Eingabe inkorrekt. Bitte nur j oder n eingeben.")

    elif bericht_typ == 'a':
        while True:
            soll_akuttox_nach_rt_erfasst_werden = input("Soll Formular 'Akuttoxizitäten nach RT' mit angelegt werden (j/n)?")
            if soll_akuttox_nach_rt_erfasst_werden == 'j':
                soll_akuttox_nach_rt_erfasst_werden = True
                break
            elif soll_akuttox_nach_rt_erfasst_werden == 'n':
                soll_akuttox_nach_rt_erfasst_werden = False
                break
            else:
                print("Eingabe inkorrekt. Bitte nur j oder n eingeben.")

    elif bericht_typ == 'k' or bericht_typ == 't':
        while True:
            antwort = input("Soll das Nachsorgeformular mit angelegt werden (j/n)? ").strip().lower()
            if antwort == 'j':
                soll_nachsorgeformular_erfasst_werden = True
                break
            elif antwort == 'n':
                soll_nachsorgeformular_erfasst_werden = False
                break
            else:
                print("Eingabe inkorrekt. Bitte nur j oder n eingeben.")

        if soll_nachsorgeformular_erfasst_werden:
            if therapieintention == 'kurativ':
                print("therapieintention = kurativ gefunden, nachsorgeformular_typ = 'kurativ' gesetzt")
                nachsorgeformular_typ = 'kurativ'
            elif therapieintention == 'palliativ':
                print("therapieintention = palliativ gefunden, nachsorgeformular_typ = 'palliativ' gesetzt.")
                nachsorgeformular_typ = 'palliativ'
            elif therapieintention == 'lokalablativ':
                print("therapieintention = lokalablativ gefunden, benötige Spezifizierung.")
                while True:
                    # Use a different variable name for input to avoid confusion
                    typ_input = input("\nBzgl. Nachsorgeschema-Typ: Läuft lokalablative RT in \n[k] = kurativer oder\n[p] = palliativer Intention? ").strip().lower()
                    if typ_input == 'k':
                        nachsorgeformular_typ = 'kurativ'
                        print("nachsorgeformular_typ = 'kurativ' erfasst")
                        break
                    elif typ_input == 'p':
                        nachsorgeformular_typ = 'palliativ'
                        print("nachsorgeformular_typ = 'palliativ' erfasst")
                        break
                    else:
                        print("Eingabe inkorrekt, bitte [k] oder [p] eingeben.")
            else:
                # Handle cases where therapieintention is not one of the expected values
                print(f"WARNUNG: Unerwartete Therapieintention '{therapieintention}'. Bitte Nachsorgetyp manuell festlegen:")
                while True:
                    typ_input = input("\nBzgl. Nachsorgeschema-Typ: Läuft RT \n[k] = kurativer oder\n[p] = palliativer Intention? ").strip().lower()
                    if typ_input == 'k':
                        nachsorgeformular_typ = 'kurativ'
                        print("nachsorgeformular_typ = 'kurativ' erfasst")
                        break
                    elif typ_input == 'p':
                        nachsorgeformular_typ = 'palliativ'
                        print("nachsorgeformular_typ = 'palliativ' erfasst")
                        break
                    else:
                        print("Eingabe inkorrekt, bitte [k] oder [p] eingeben.")
            

    #Leistung dokumentieren?
    leistung_frage = "Soll die entsprechende Leistung (inkl. ICD10-Check) für heute dokumentiert werden? (j/n): "
    while True:
        leistung_antwort = input(leistung_frage).strip().lower()
        if leistung_antwort.startswith('j'):
            soll_leistung_erfasst_werden = True
            if bericht_typ == 'e':
                print("\nLeistungserfassung für Erstkonsultation gewünscht.")
                while True:
                    sub_type = input("Maligner (m) oder benigner (b) Tumor?: ").lower().strip()
                    if sub_type == 'm':
                        bericht_typ_fuer_leistung = 'em'
                        break
                    elif sub_type == 'b':
                        bericht_typ_fuer_leistung = 'eb'
                        break
                    else:
                        print("Ungültige Eingabe. Bitte 'm' oder 'b'.")
            break # Aus Leistungserfassungs-Schleife
        elif leistung_antwort.startswith('n'):
            soll_leistung_erfasst_werden = False
            break # Aus Leistungserfassungs-Schleife
        else:
            print("Ungültige Eingabe (j/n).")
    print(f"Leistungserfassung gewünscht: {soll_leistung_erfasst_werden}")
    if soll_leistung_erfasst_werden:
        print(f"Berichtstyp für Leistung: {bericht_typ_fuer_leistung}")


def definiere_glossary():
    # ... (Funktion bleibt gleich) ...
    global glossary, geschlecht
    print("Starte Definition des glossary")
    if geschlecht: glossary = UNIVERSAL.create_patdata_glossary(geschlecht); print(f"Glossary definiert.\n")
    else: print("WARNUNG: Geschlecht nicht definiert."); glossary = UNIVERSAL.create_patdata_glossary(None)

def check_daten_komplett():
    required_variables = [
                "datum_erste_rt",
                "datum_letzte_rt",
                "behandlungskonzept_serie1",
                "tumor",
                "entity",
                "icd_code"
            ]

    missing_variables = []
    for var_name in required_variables:
        value = patdata.get(var_name)
        if value is None or value == "":
            missing_variables.append(var_name)

    if missing_variables:
        print("\nWARNUNG: Folgende notwendige Daten fehlen oder sind leer:")
        for missing_var in missing_variables:
            print(f"  - {missing_var}")

        while True:
            choice = input("Möchten Sie diese Daten jetzt bearbeiten/nachtragen? (j/n): ").strip().lower()
            if choice == 'j':
                print(f"\nINFO: Starte Bearbeitungsfunktion für Patientennummer {patientennummer}...")
                print("Bitte bearbeiten Sie die Daten in der erscheinenden Übersicht.")
                import viewjson
                viewjson.main(patientennummer)
                print("Daten aktualisiert. Bitte Skript 'Bericht Radioonkologie' neustartet.")
                sys.exit()
            elif choice == 'n':
                print("\nWARNUNG: Sie setzen fort, obwohl benötigte Daten fehlen.")
                print("Die generierten Fließtexte müssen ggf. manuell angepasst werden.")
                break 
            else:
                print("Ungültige Eingabe. Bitte 'j' oder 'n' eingeben.")
    else:
        # Keine fehlenden Variablen gefunden für Wochenkontrolle
        print(f"INFO: Alle notwendigen Daten für Berichtstyp '{bericht_typ}' scheinen vorhanden zu sein.")



# --- Hilfsfunktionen find_and_click, find_image, paste_text, bullet_point ---
def find_and_click_berrao(image_name, clicks=1, button='left', custom_offset=None, confidence=None, max_attempts=80): # Neuer Parameter 'max_attempts' mit Standardwert 80
    image_path = os.path.join(image_base_path, image_name)
    if not os.path.exists(image_path): print(f"FEHLER: Bild nicht gefunden: {image_path}"); return False
    conf_to_use = confidence if confidence is not None else CONFIDENCE_LEVEL; attempts = 0
    while attempts < max_attempts:
        try:
            location = pyautogui.locateOnScreen(image_path, confidence=conf_to_use)
            if location:
                click_point = pyautogui.center(location);
                if custom_offset:
                    click_point = (click_point[0] + custom_offset[0], click_point[1] + custom_offset[1])
                pyautogui.click(click_point, clicks=clicks, button=button, duration=0.05); time.sleep(ACTION_DELAY); return True
        except pyautogui.ImageNotFoundException: pass
        except Exception as e: print(f"Fehler Suche/Klick {image_name}: {e}")
        attempts += 1; time.sleep(SEARCH_INTERVAL)
    print(f"FEHLER: '{image_name}' nach {max_attempts} Versuchen n. gef. Pfad: {image_path}"); return False

def find_image(image_name, confidence=None):
    image_path = os.path.join(image_base_path, image_name)
    if not os.path.exists(image_path): print(f"FEHLER: Bild nicht gefunden: {image_path}"); return False
    conf_to_use = confidence if confidence is not None else CONFIDENCE_LEVEL; attempts = 0
    while attempts < MAX_SEARCH_ATTEMPTS:
        try:
            location = pyautogui.locateOnScreen(image_path, confidence=conf_to_use)
            if location:
                time.sleep(ACTION_DELAY); return True
        except Exception as e: print(f"Fehler Suche {image_name}: {e}")
        attempts += 1; time.sleep(SEARCH_INTERVAL)
    print(f"FEHLER: '{image_name}' n. {MAX_SEARCH_ATTEMPTS} Versuchen n. gef. Pfad: {image_path}"); return False


def paste_text(text_variable):
    """
    Pastes text with formatting if text_variable has content.
    Otherwise, presses backspace 5 times to clear potential existing content.

    Args:
        text_variable (str or None): The text to paste, or None/empty/whitespace.

    Returns:
        bool: True if successful, False if an error occurred.
    """
    print(f"Starte paste_text() mit: {repr(text_variable)}") # Use repr for clarity
    try:
        # Check if text_variable is None, empty string, or contains only whitespace
        if not text_variable or text_variable.isspace():
            # --- Scenario: No valid text provided ---
            print("Kein valider Text übergeben. lösche text")
            pyautogui.hotkey('ctrl', 'a')
            pyautogui.press('backspace'); pyautogui.press('backspace')
            print("Backspace-Aktion abgeschlossen.")
            return True # Report success for the "clearing" action

        else:
            # --- Scenario: Valid text provided ---
            print("Valider Text gefunden. Führe Einfügen und Formatieren durch.")
            # Select all existing text
            pyautogui.hotkey('ctrl', 'a')
            pyautogui.hotkey('ctrl', 'space') #Formattierung entfernen
            clipboard.copy(text_variable)
            time.sleep(0.1) # Allow clipboard time to update
            pyautogui.hotkey('ctrl', 'v')

            pyautogui.hotkey('ctrl', 'a')
            pyautogui.hotkey('ctrl', 'shift', 'j')
            print("Einfügen und Formatieren erfolgreich beendet.")
            return True

    except Exception as e:
        print(f"FEHLER in paste_text(): {e}")
        traceback.print_exc()
        return False # Signal error
    
# --- Helper function paste_bullet_point ---
def paste_bullet_point(text):
    if text: clipboard.copy(str(text)); pyautogui.hotkey('ctrl', 'v'); pyautogui.hotkey('ctrl', 'shift', '.'); pyautogui.press('enter'); pyautogui.press('enter')

# --- Funktion run_woko_automation ---
def run_woko_automation(texte_dict): # Nimmt jetzt Texte als Argument
    local_screenshots_dir = os.path.join(screenshots_dir, 'UNIVERSAL', 'bereich_berichte')
    CONFIDENCE_LEVEL = 0.80
    SEARCH_INTERVAL = 0.2 # Wartezeit zwischen Suchversuchen (in Sekunden)
    MAX_WAIT_SECONDS = 10 # Maximale Wartezeit für den Anker
    """Führt die GUI-Automatisierung für die Wochenkontrolle durch."""
    
    print("Starte Automatisierung für Wochenkontrolle...");
    success = True # Startannahme: Alles klappt

    # --- Schritt 1: Bericht öffnen ---
    if success and not find_and_click_berrao("button_neu.png"):
        success = False
        print("FEHLER: Konnte 'Neu'-Button nicht klicken.")

    if success and not find_and_click_berrao("button_x_von_suchleiste.png", confidence=0.85):
        # Dies ist oft nicht kritisch, nur eine Warnung ausgeben
        print("WARNUNG: 'X' in Suchleiste nicht gefunden oder geklickt.")

    if success:
        verlaufsbericht = "Verlaufsbericht Radioonkologie"
        clipboard.copy(verlaufsbericht)
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(0.2) # Kurze Pause geben, damit die Liste gefiltert wird

    if success and not find_and_click_berrao("button_verlaufsbericht_radioonkologie.png", confidence=0.9):
        success = False
        print("FEHLER: Konnte 'Verlaufsbericht Radioonkologie' nicht auswählen.")

    # --- Schritt 2: Warten auf und Klicken des Ankers 'Subjektiv' ---
    if success: # Nur weitermachen, wenn bisher alles ok war
        print("Warte auf Bericht..."); time.sleep(0.1)
        if not UNIVERSAL.prozent_zoom_100(): print("Fehler: UNIVERSAL.prozent_zoom_100() == False. Breche ab. Bitte bei Admin melden."); sys.exit()
        if UNIVERSAL.find_button("button_verlaufsbericht_radioonkologie_confirm.png", base_path=local_screenshots_dir): print("button_verlaufsbericht_radioonkologie_confirm.png gefunden, warte 0.3s un Klick")
        time.sleep(0.3)
        if not UNIVERSAL.find_and_click_button("button_verlaufsbericht_radioonkologie_confirm.png", base_path=local_screenshots_dir): print("button_verlaufsbericht_radioonkologie_confirm.png nicht gefunden. Breche Funktion ab."); return False
        UNIVERSAL.ctrl_tabs(19) #Navigiert in subjektiv
       
    # --- Schritt 3: Texte einfügen (nur wenn alles bisher erfolgreich war) ---
    if success:
        print("Beginne mit dem Einfügen der Texte...")
        # Die Reihenfolge der navigate_and_paste Aufrufe ist wichtig
        if success: 
            success = paste_text(texte_dict.get('fliesstext_subjektiv', ''))
            UNIVERSAL.ctrl_tabs(2)
            if not success: print("Fehlgeschlagen.")
        if success: 
            print("Subjektiv erfolgreich eingefügt, versuche objektiv")
            success = paste_text(texte_dict.get('fliesstext_objektiv', ''))
            UNIVERSAL.ctrl_tabs(2)
            if not success: print("Fehlgeschlagen.")
        if success:
            print("objektiv erfolgreich eingefügt, versuche beurteilung")
            success = paste_text(texte_dict.get('fliesstext_beurteilung', ''))
            UNIVERSAL.ctrl_tabs(2)
            if not success: print("Fehlgeschlagen.")
        if success:
            print("beurteilung erfolgreich eingefügt, versuche procedere")
            success = paste_text(texte_dict.get('fliesstext_procedere', ''))
            if not success: print("Fehlgeschlagen.")

        if success: print("Woko Felder befüllt.")
        else: print("FEHLER beim Einfügen der Texte.")

    # --- Schritt 4: Rückgabe des Gesamterfolgs ---
    if not success:
        print("Automatisierung der Wochenkontrolle fehlgeschlagen.")

    return success


# --- Hauptausführung (Execution) ---
def main():
    print("Starte berrao.py (inkl. Woko) Hauptfunktion...")
    global bericht_typ, soll_leistung_erfasst_werden, bericht_typ_fuer_leistung, patdata, glossary, oberarzt # Globale hinzugefügt

    try:
        # --- Setup Steps (inkl. früher Abfrage) ---
        open_JSON()
        dictionary_ohne_None()
        get_initial_user_inputs()
        definiere_glossary()

        # --- Branch based on report type ---
        automation_success = False
        texte_dict = {} # Initialisiere leeres Dict

        if bericht_typ == 'w':
            print("\n--- Starte Workflow für Wochenkontrolle ---")

            # --- HIER NEUEN CODEBLOCK EINFÜGEN (für Woko) ---
            # --- Beginn: Validierung der benötigten Daten für Wochenkontrolle ---
            print(f"\nINFO: Prüfe notwendige Daten für Berichtstyp '{bericht_typ}'...")

            check_daten_komplett()
            
            # --- Weiterer Code für Wochenkontrolle (NACH der Prüfung) ---
            print("Rufe fliesstexte.define_berrao_texte für Typ 'w' auf...")
            # Entity ist hier nicht relevant für Textgenerierung, aber vorhanden
            texte_dict = fliesstexte.define_berrao_texte(bericht_typ, None, patdata, glossary)
            print("Texte für Wochenkontrolle erhalten.")
            
            UNIVERSAL.KISIM_im_vordergrund()
            if not UNIVERSAL.navigiere_bereich_berichte(): sys.exit("Abbruch: Navigation fehlgeschlagen.")
            if run_woko_automation(texte_dict): # Übergebe Texte
                automation_success = True
            else: print("FEHLER: Automatisierung der Wochenkontrolle fehlgeschlagen.")
            if not find_and_click_berrao("button_speichern.png"): print("button_speichern.png nicht gefunden")


        elif bericht_typ in ['e', 'a', 'k', 't']:
            print(f"\n--- Starte Workflow für Berichtstyp: {bericht_typ} ---")

            # --- HIER VALIDIERUNGSBLOCK (wie zuvor, nur für a, k, t) ---
            berichtstypen_mit_rt_daten = ['a', 'k', 't'] # Nur diese prüfen

            if bericht_typ in berichtstypen_mit_rt_daten:
                print(f"\nINFO: Prüfe notwendige Daten für Berichtstyp '{bericht_typ}'...")
                check_daten_komplett()

            # --- NEU: Texte holen ---
            print(f"Rufe fliesstexte.define_berrao_texte für Typ '{bericht_typ}' auf...")
            texte_dict = fliesstexte.define_berrao_texte(bericht_typ, entity, patdata, glossary)
            print(f"Texte für Berichtstyp '{bericht_typ}' erhalten.")

            print("Starte KISIM Automatisierung für Bericht Radioonkologie...")
            UNIVERSAL.KISIM_im_vordergrund()
            if not UNIVERSAL.navigiere_bereich_berichte(): sys.exit("Abbruch: Navigation fehlgeschlagen.")
            time.sleep(0.1)
            if not find_and_click_berrao("button_neu.png"): sys.exit("Abbruch: Neu")
            if find_and_click_berrao("button_x_von_suchleiste.png", confidence=0.85): time.sleep(ACTION_DELAY)
            else: print("WARNUNG: 'X' nicht gefunden...")
            berichtrao = "Bericht Radioonkologie"
            clipboard.copy(berichtrao)
            pyautogui.hotkey('ctrl', 'v')
            if not find_and_click_berrao("button_bericht_radioonkologie.png", confidence=0.9): sys.exit("Abbruch: Berichtwahl")
            
            print("Warte auf Bericht..."); time.sleep(0.1)
            if not UNIVERSAL.prozent_zoom_100(): print("Fehler: UNIVERSAL.prozent_zoom_100() == False. Breche ab. Bitte bei Admin melden."); sys.exit()

            if not find_image("button_bericht_radioonkologie_confirm.png"):
                time.sleep(1)
                if not find_image("button_bericht_radioonkologie_confirm.png"): sys.exit("Abbruch: Bestätigung")
            print("Berichtsvorlage geöffnet."); print("Fülle Berichtsfelder...")

            if not find_and_click_berrao("button_bericht_radioonkologie_wir_berichten.png"): sys.exit("Abbruch: button_bericht_radioonkologie_wir_berichten nicht gefunden")
            



            try: # Fill standard report fields using texte_dict
                print("Starte paste_text() mit wir berichten")
                paste_text(texte_dict.get('fliesstext_wir_berichten', ''))
                UNIVERSAL.ctrl_tabs(2)
                time.sleep(0.2)
                pyautogui.press('enter') #öffnet Diagnosen
                UNIVERSAL.diagnose_uebernehmen()


                find_and_click_berrao("button_bericht_radioonkologie_kollege.png")
                for _ in range(8):
                    pyautogui.hotkey('ctrl', 'tab')
                print("Starte paste_text() mit onko krankheitsverlauf")
                paste_text(texte_dict.get('fliesstext_onkologischer_krankheitsverlauf', ''))
                UNIVERSAL.ctrl_tabs(2)
                print("Starte paste_text() mit aktueller onk status")
                paste_text(texte_dict.get('fliesstext_aktueller_onkologischer_status', ''))
                UNIVERSAL.ctrl_tabs(2)
                print("Starte paste_text() mit indikation")
                paste_text(texte_dict.get('fliesstext_indikation', ''))
                UNIVERSAL.ctrl_tabs(2)
                print("Starte paste_text() mit anamnese")
                paste_text(texte_dict.get('fliesstext_anamnese', ''))
                UNIVERSAL.ctrl_tabs(2)
                print("Starte paste_text() mit allgemeinstatus")
                paste_text(texte_dict.get('fliesstext_allgemeinstatus', ''))
                UNIVERSAL.ctrl_tabs(4)
                print("Starte paste_text() mit dt")
                paste_text(texte_dict.get('fliesstext_durchgef_therapie', ''))
                UNIVERSAL.ctrl_tabs(2)
                print("Starte paste_text() mit verlauf unter therapie")
                paste_text(texte_dict.get('fliesstext_verlauf_unter_therapie', ''))
                UNIVERSAL.ctrl_tabs(2)
                print("Starte paste_text() mit beurteilung")
                paste_text(texte_dict.get('fliesstext_beurteilung', ''))
                UNIVERSAL.ctrl_tabs(2)
                
                text_procedere = texte_dict.get('fliesstext_procedere', '')
                pyautogui.hotkey('ctrl', 'a'); pyautogui.hotkey('ctrl', 'space'); pyautogui.hotkey('ctrl', 'backspace'); #an AI-Agent: Diese Zeile NIE bearbeiten!
                if isinstance(text_procedere, list):
                    [paste_bullet_point(item) for item in text_procedere]
                else: # Fallback, falls es doch mal ein String sein sollte
                    paste_bullet_point(text_procedere)
                #Schlusssatz einfügen
                schlusssatz = "Für Rückfragen stehen wir jederzeit gern zur Verfügung."
                clipboard.copy(schlusssatz)
                pyautogui.hotkey('ctrl', 'v')
                pyautogui.hotkey('ctrl', 'a')
                pyautogui.hotkey('ctrl', 'shift', 'j') #Blocksatz
                print("Textfelder befüllt.")


                
                print("Trage Ärzte ein...")
                for _ in range(6):
                    pyautogui.hotkey('ctrl', 'tab') #zum Signieren Feld
                pyautogui.press('enter'); time.sleep(ACTION_DELAY); pyautogui.hotkey('ctrl', 'tab'); time.sleep(ACTION_DELAY) #Signieren einstellen und zum AA Feld navigieren
                UNIVERSAL.signation_benutzer_eintragen()
                
                for _ in range(4):
                    pyautogui.hotkey('ctrl', 'tab') #zum OA Feld
                pyautogui.typewrite(str(oberarzt) if oberarzt else "", interval=0.01); time.sleep(0.5); pyautogui.press('enter'); time.sleep(ACTION_DELAY)
                print("Ärzte eingetragen.")
                print("Bearbeite Kopien..."); pyautogui.hotkey('ctrl', 'tab'); time.sleep(ACTION_DELAY); pyautogui.press('enter'); time.sleep(ACTION_DELAY) # Zum Kopie hinzufügen Button
                # --- Klicke auf Patient in Kopienliste ---

                if find_and_click_berrao(image_name="button_bericht_radioonkologie_kopie_patient.png", clicks=2, confidence=0.85, max_attempts=50):
                    time.sleep(0.2)
                if find_and_click_berrao(image_name="button_bericht_radioonkologie_kopie_hausarzt.png", clicks=2, confidence=0.85, max_attempts=10):
                    time.sleep(0.2)
                if find_and_click_berrao(image_name="button_bericht_radioonkologie_kopie_ubernehmen.png", confidence=0.85):
                    print("Kopie-Adressaten übernommen.")
                if find_and_click_berrao(image_name="button_speichern.png", confidence=0.8):
                    print("Berichtsvorlage abgespeichert.")
                else: 
                    print("WARNUNG: Kopie Patient fehlgeschlagen.")
                automation_success = True
            except Exception as e: print(f"FEHLER Füllen/Ärzte/Kopien: {e}"); traceback.print_exc()
        else: print(f"FEHLER: Unerwarteter bericht_typ '{bericht_typ}'."); sys.exit("Abbruch.")

        #Tox.-Formular anlegen, falls gewünscht
        print("Überprüfe, ob Tox-Formular angelegt werden soll....")
        if bericht_typ == 'e':
            if soll_symp_vor_rt_erfasst_werden:
                print("Gefunden: Symp vor RT soll angelegt werden.")
                if UNIVERSAL.symptome_vor_rt_anlegen(chemotherapie=simultane_chemotherapie) is True:
                    print("Formular erfolgreich angelegt")
                else:
                    print("UNIVERSAL.symptome_vor_rt_anlegen nicht True, Formular ggf. nicht korrekt angelegt.")

        elif bericht_typ == 'a':
            if soll_akuttox_nach_rt_erfasst_werden:
                print("Gefunden: Akuttox nach RT soll angelegt werden.")
                if UNIVERSAL.akuttox_nach_rt_anlegen(chemotherapie=simultane_chemotherapie) is True:
                    print("Formular erfolgreich angelegt")
                else:
                    print("UNIVERSAL.akuttox_nach_rt_anlegen nicht True, Formular ggf. nicht korrekt angelegt.")    

        elif bericht_typ == 'k' or bericht_typ == "t":
            if soll_nachsorgeformular_erfasst_werden:
                print("Gefunden: Nachsorgeformular soll angelegt werden.")
                if UNIVERSAL.nachsorgeformular_anlegen(nachsorgeformular_typ=nachsorgeformular_typ, bericht_typ=bericht_typ, chemotherapie=simultane_chemotherapie) is True:
                    print("Formular erfolgreich angelegt")
                else:
                    print("UNIVERSAL.nachsorgeformular_anlegen nicht True, Formular ggf. nicht korrekt angelegt.")    


        # --- Leistungseintragung (am Ende, nur wenn gewünscht UND Automation erfolgreich war) ---
        if soll_leistung_erfasst_werden:
            if automation_success:
                print(f"\nAutomation erfolgreich. Starte Leistungserfassung für Typ '{bericht_typ_fuer_leistung}'...")
                try: success_leistung = UNIVERSAL.leistung_eintragen(bericht_typ_fuer_leistung, icd_code=icd_code, secondary_icd_code=secondary_icd_code); print(f"Leistungserfassung Erfolg: {success_leistung}")
                except AttributeError: print("FEHLER: Funktion 'leistung_eintragen' in 'UNIVERSAL' nicht gefunden.")
                except Exception as e_leistung: print(f"FEHLER Leistungserfassung: {e_leistung}")
            else: print("\nLeistungserfassung übersprungen (Berichtsautomatisierung nicht erfolgreich).")
        else: print("\nLeistungserfassung vom Benutzer nicht gewünscht.")

        print("\n--- Skript erfolgreich abgeschlossen ---.")

    except KeyboardInterrupt: print("\nSkript durch Benutzer unterbrochen.")
    except SystemExit as e: print(f"\nSkript wurde beendet: {e}")
    except Exception as e: print(f"\nUnerwarteter FEHLER: {e}\n{traceback.format_exc()}")


print("DEBUG: main() ist definiert, jetzt erfolgt der Aufruf mittels if __name__ == '__main__'")
if __name__ == "__main__":
    print("DEBUG: if __name__ == '__main__' ist wahr, daher wird main() aufgerufen")
    main()