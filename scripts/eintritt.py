# -*- coding: utf-8 -*-
print("Starte Skript eintritt.py für Eintrittsberichte...")
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
eintritt_screenshots_dir = os.path.join(screenshots_dir, 'etrao') # Common dir
bereich_berichte_screenshots_dir = os.path.join(screenshots_dir, 'UNIVERSAL', 'bereich_berichte')
# Define the absolute path to patdata in the user's home directory
user_home = os.path.expanduser("~") 
patdata_dir = os.path.join(user_home, "patdata")

print(f"Script directory (eintritt.py): {script_dir}")
print(f"App directory: {app_dir}")
print(f"Patient data directory: {patdata_dir}")
print(f"Screenshots directory: {eintritt_screenshots_dir}")

# --- Globale Konfigurationen ---
MAX_SEARCH_ATTEMPTS = 150; SEARCH_INTERVAL = 0.05; CONFIDENCE_LEVEL = 0.9; ACTION_DELAY = 0.02

# --- Globale Variablen ---
patdata = None; patientennummer = None; eintritt_typ = None; glossary = {}
nachname = None; vorname = None; name = None; geburtsdatum = None; alter = None; geschlecht = None; eintrittsdatum = None; spi = None; rea = None; ips = None; oberarzt = None; simultane_chemotherapie = None; systemtherapie = None; therapieintention_code = None; therapieintention_gross = None; therapieintention_klein = None; fraktionen_woche = None; behandlungskonzept_serie1 = None; behandlungskonzept_serie2 = None; behandlungskonzept_serie3 = None; behandlungskonzept_serie4 = None; rt_konzept = None; rt_zeitraum_beginn = None; rt_zeitraum_ende = None; ecog = None; tumor = None; zimmer = None; aufnahmegrund = None

# --- Funktionen ---
# Dieser Block ersetzt die open_JSON Funktion in berrao.py, eintritt.py und austritt.py:
def open_JSON():
    global patdata, patientennummer # patientennummer wird hier nur gelesen/geprüft
    
    # Wenn die Patientennummer nicht durch den Funktionsaufruf gesetzt wurde, fragen.
    if patientennummer is None:
        pat_id_input = input("Bitte patientennummer angeben: ")
        if not pat_id_input.isdigit():
            print("FEHLER: Patientennummer muss eine Zahl sein.")
            sys.exit(1)
        patientennummer = pat_id_input
    else:
        print(f"INFO: Patientennummer '{patientennummer}' aus Aufruf übernommen.")
            
    patdata = UNIVERSAL.load_json(patientennummer)
    if patdata == "patdata":
        # Diese Logik bleibt für den Fall, dass ein User 'patdata' eingibt
        print(f"{os.path.basename(sys.argv[0])}: User will patdata ausführen...")
        # ... (restliche patdata-Importlogik bleibt gleich) ...
        print("JSON vermutlich angelegt. Bitte Skript erneut starten."); sys.exit()
    elif not isinstance(patdata, dict):
        print(f"Fehler: JSON für Patient '{patientennummer}' konnte nicht geladen werden.")
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

def definiere_glossary():
    # ... (Funktion bleibt gleich) ...
    global glossary, geschlecht
    print("Starte Definition des glossary")
    if geschlecht: glossary = UNIVERSAL.create_patdata_glossary(geschlecht); print(f"Glossary definiert.\n")
    else: print("WARNUNG: Geschlecht nicht definiert."); glossary = UNIVERSAL.create_patdata_glossary(None)


def eintritt_typ_definieren():
    # ... (Funktion bleibt gleich) ...
    global eintritt_typ
    print("\nWelche Art Eintrittsbericht wird angelegt:")
    print("[1] = Eintritt RAO allgemein")
    print("[2] = Eintritt Brachy")
    print("[3] = Eintritt Chemo")
    print("[4] = Eintritt Palliative Care")
    typ_map = {'1':1, '2':2, '3':3, '4':4}
    while True:
        choice = input("Auswahl: ").strip()
        if choice in typ_map: eintritt_typ = typ_map[choice]; return eintritt_typ
        else: print("Ungültige Eingabe.")

# --- Helper function find_and_click_eintritt ---
# ... (Funktion bleibt gleich) ...
def find_and_click_eintritt(image_filename, confidence=CONFIDENCE_LEVEL, retries=20, delay_after=ACTION_DELAY, clicks=1, button='left'):
    full_path = os.path.join(eintritt_screenshots_dir, image_filename)
    attempts = 0
    while attempts < retries:
        try:
            location = pyautogui.locateOnScreen(full_path, confidence=confidence)
            if location: pyautogui.click(pyautogui.center(location), button=button, clicks=clicks); print(f'{image_filename} ({button}/{clicks}x) geklickt.'); time.sleep(delay_after); return True
        except pyautogui.ImageNotFoundException:
            if attempts == 0: print(f'{image_filename} n.gef. (Try {attempts+1}/{retries}). Path: {full_path}')
        except Exception as e: print(f"Fehler Suche/Klick {image_filename}: {e}")
        attempts += 1; time.sleep(0.1)
    print(f"FEHLER: {image_filename} n. {retries} Versuchen n. gef."); return False


# --- Helper function paste_standard_text ---
# ... (Funktion bleibt gleich) ...
def paste_standard_text(text):
    if text: clipboard.copy(str(text)); pyautogui.hotkey('ctrl', 'v')
    pyautogui.hotkey('ctrl', 'tab')

# --- Helper function paste_procedere_point ---
# ... (Funktion bleibt gleich) ...
def paste_procedere_point(text):
    if text: pyautogui.hotkey('ctrl', 'shift', '.'); clipboard.copy(str(text)); pyautogui.hotkey('ctrl', 'v'); pyautogui.press('enter'); pyautogui.press('enter')


# --- Main execution block ---
def main(patientennummer_param=None):
    global eintritt_typ, patdata, glossary, eintrittsdatum, oberarzt, patientennummer # Globale Variablen für main
    try:

        #Check, ob patientennummer bereits aus patdata erhalten wurde
        if patientennummer_param:
            patientennummer = patientennummer_param
        # --- Setup ---
        open_JSON()
        eintritt_typ = eintritt_typ_definieren()
        dictionary_ohne_None() # Extrahiert Daten
        definiere_glossary()

        # --- NEU: Texte aus fliesstexte.py holen ---
        print(f"Rufe fliesstexte.define_eintritt_texte für Typ {eintritt_typ} auf...")
        texte_dict = fliesstexte.define_eintritt_texte(eintritt_typ, patdata, glossary)
        print(f"Texte für Eintrittstyp {eintritt_typ} erhalten.")
        # --- Ende Neu ---

        # --- Start Automation ---
        print("Starte KISIM Automatisierung für Eintrittsbericht...")
        UNIVERSAL.KISIM_im_vordergrund()
        UNIVERSAL.navigiere_bereich_berichte()
        if not find_and_click_eintritt('button_neu.png'): sys.exit("Abbruch: Neu")

        UNIVERSAL.find_and_click_button_offset(image_name='button_bericht_for_offset.png', base_path=eintritt_screenshots_dir, y_offset=55, confidence=0.9)

        # --- ÄNDERUNG: Suche nach 'button_suchleiste.png' ---
        if not find_and_click_eintritt('button_suchleiste.png'): sys.exit("Abbruch: Suche")

        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.05)
        pyautogui.press('backspace')
        time.sleep(0.05)
        eintrittradioonkologie = "eintritt radioonkologie"
        clipboard.copy(eintrittradioonkologie)
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(0.1)

        if not find_and_click_eintritt('button_eintrittradioonkologie.png'): sys.exit("Abbruch: Berichtwahl")
        
        print("Warte auf Bericht..."); time.sleep(0.1)
        if not UNIVERSAL.prozent_zoom_100(): print("Fehler: UNIVERSAL.prozent_zoom_100() == False. Breche ab. Bitte bei Admin melden."); sys.exit()


        # --- Klicke auf "Jetziges Leiden", um sicher im ersten Feld zu sein ---
        if not find_and_click_eintritt('button_jetziges_leiden.png'): sys.exit("Abbruch: Jetziges Leiden (Anker)")
        print("Bericht geöffnet."); time.sleep(0.1)

        # --- Fill Anamnese ---
        print("Fülle Anamnesefelder...")
        pyautogui.hotkey('ctrl', 'tab')#navigiere in Jetziges Leiden
        pyautogui.hotkey('ctrl', 'tab')#navigiere in Jetziges Leiden
        clipboard.copy(texte_dict.get('leiden', 'FEHLER')) # Verwende Text aus Dict
        pyautogui.hotkey('ctrl', 'v')
        pyautogui.hotkey('ctrl', 'tab') # Nächstes Feld (Persönl. Anamnese)
        pyautogui.hotkey('ctrl', 'tab') # Nächstes Feld (Familienanamnese)

        # Verwende paste_standard_text mit Werten aus dem Dict
        paste_standard_text(texte_dict.get('familienanamnese', 'FEHLER'))
        paste_standard_text(texte_dict.get('soziales', 'FEHLER'))
        paste_standard_text(texte_dict.get('noxen', 'FEHLER'))
        paste_standard_text(texte_dict.get('ecog_beschreibung', 'FEHLER'))
        paste_standard_text(texte_dict.get('gastro', 'FEHLER'))
        paste_standard_text(texte_dict.get('pulmo', 'FEHLER'))
        paste_standard_text(texte_dict.get('kardial', 'FEHLER'))
        paste_standard_text(texte_dict.get('uro', 'FEHLER'))
        paste_standard_text(texte_dict.get('bewegung', 'FEHLER'))
        paste_standard_text(texte_dict.get('neuro', 'FEHLER'))
        paste_standard_text(texte_dict.get('schmerzen', 'FEHLER'))
        paste_standard_text(texte_dict.get('b_symp', 'FEHLER'))
        paste_standard_text(texte_dict.get('allergien', 'FEHLER'))
        paste_standard_text(texte_dict.get('az_ez', 'FEHLER'))
        paste_standard_text(texte_dict.get('gewicht', 'FEHLER'))
        paste_standard_text(texte_dict.get('status', 'FEHLER'))
        pyautogui.hotkey('ctrl', 'a')
        pyautogui.hotkey('ctrl', 'shift', 'j') #Blocksatz
        print("Anamnesefelder befüllt.")
        time.sleep(0.1)
        print("navigiere zu Diagnosen... (7x ctrl-tabs)")
        UNIVERSAL.ctrl_tabs(7)
        time.sleep(0.1)
        pyautogui.press('enter')
        if not UNIVERSAL.diagnose_uebernehmen(): print("UNIVERSAL.diagnose_uebernehmen() nicht funktioniert, manuell tätigen")

        print("navigiere zu Bemerkung... (3x ctrl-tabs)")
        UNIVERSAL.ctrl_tabs(3)
        print("Fülle Bemerkung...")
        paste_standard_text(texte_dict.get('bemerkung', 'FEHLER'))
        print("Bemerkung gefüllt...")
        pyautogui.hotkey('ctrl', 'a')
        pyautogui.hotkey('ctrl', 'shift', 'j')
        print("Fülle Procedere...")
        procedere_list = texte_dict.get('procedere_list', ['FEHLER'])
        if isinstance(procedere_list, list):
            for item in procedere_list: paste_procedere_point(item)
        else: paste_procedere_point(procedere_list)
        print("Procedere befüllt.")

        # --- Fill Date/Signature Fields ---
        print("Fülle Datum/Signatur...")
        pyautogui.hotkey('ctrl', 'tab')
        pyautogui.hotkey('ctrl', 'tab') #navigation zu signieren/visieren
        #ändere visieren zu signieren
        pyautogui.press('enter') 
        pyautogui.press('down')
        pyautogui.press('down')
        pyautogui.press('enter')

        pyautogui.hotkey('ctrl', 'tab') # Nächstes Feld AA
        UNIVERSAL.signation_benutzer_eintragen()
        
        for _ in range(3):
            pyautogui.hotkey('ctrl', 'tab') # Nächstes Feld Oberarzt
        pyautogui.typewrite(str(oberarzt) if oberarzt else "")
        time.sleep(0.2)
        pyautogui.press('enter')
        
        print("Datum/Signaturfelder befüllt.")

        print("\n--- eintritt.py Skript beendet ---")

    except KeyboardInterrupt: print("\nSkript durch Benutzer unterbrochen.")
    except SystemExit as e: print(f"\nSkript wurde beendet: {e}")
    except Exception as e: print(f"\nUnerwarteter FEHLER: {e}\n{traceback.format_exc()}")


print("DEBUG: main() ist definiert, jetzt erfolgt der Aufruf mittels if __name__ == '__main__'")
if __name__ == "__main__":
    print("DEBUG: if __name__ == '__main__' ist wahr, daher wird main() aufgerufen")
    main()