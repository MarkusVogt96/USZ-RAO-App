# -*- coding: utf-8 -*-
print("Starte Skript austritt.py für Austrittsberichte...")
import UNIVERSAL # Import UNIVERSAL first
import json
import pyautogui
import os
import sys
import time
import datetime
import clipboard
import traceback
import fliesstexte 

# --- Define Relative Paths ---
script_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.dirname(script_dir)
screenshots_dir = os.path.join(script_dir, 'screenshots pyautogui')
austritt_screenshots_dir = os.path.join(screenshots_dir, 'atrao') # Common dir
# Define the absolute path to patdata in the user's home directory
user_home = os.path.expanduser("~") 
patdata_dir = os.path.join(user_home, "patdata")

print(f"Script directory (austritt.py): {script_dir}")
print(f"App directory: {app_dir}")
print(f"Patient data directory: {patdata_dir}")
print(f"Screenshots directory: {austritt_screenshots_dir}")

# --- Globale Konfigurationen ---
MAX_SEARCH_ATTEMPTS = 150; SEARCH_INTERVAL = 0.05; CONFIDENCE_LEVEL = 0.9; ACTION_DELAY = 0.02

# --- Globale Variablen ---
patdata = None; patientennummer = None; austritt_typ = None; glossary = {}
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
    global glossary, geschlecht
    print("Starte Definition des glossary")
    if geschlecht: glossary = UNIVERSAL.create_patdata_glossary(geschlecht); print(f"Glossary definiert.\n")
    else: print("WARNUNG: Geschlecht nicht definiert."); glossary = UNIVERSAL.create_patdata_glossary(None)


def austritt_typ_definieren():
    # ... (Funktion bleibt gleich) ...
    global austritt_typ
    print("\nWelche Art Austrittsbericht wird angelegt:")
    print("[1] = Austrittsbericht RAO allgemein")
    print("[2] = Austrittsbericht Brachy")
    print("[3] = Austrittsbericht Chemo (1 Nacht)")
    typ_map = {'1':1, '2':2, '3':3}
    while True:
        choice = input("Ihre Wahl (1, 2 oder 3): ").strip()
        if choice in typ_map: austritt_typ = typ_map[choice]; return austritt_typ
        else: print("Ungültige Eingabe.")



# --- Helper function find_and_click_austritt ---
# ... (Funktion bleibt gleich) ...
def find_and_click_austritt(image_name, confidence=CONFIDENCE_LEVEL, retries=30, delay_after=ACTION_DELAY, clicks=1, button='left'):
    full_path = os.path.join(austritt_screenshots_dir, image_name)
    attempts = 0
    while attempts < retries:
        try:
            location = pyautogui.locateOnScreen(full_path, confidence=confidence)
            if location: pyautogui.click(pyautogui.center(location), button=button, clicks=clicks); print(f'{image_name} ({button}/{clicks}x) geklickt.'); time.sleep(delay_after); return True
        except pyautogui.ImageNotFoundException:
            if attempts == 0: print(f'{image_name} n.gef. (Try {attempts+1}/{retries}). Path: {full_path}')
        except Exception as e: print(f"Fehler Suche/Klick {image_name}: {e}")
        attempts += 1; time.sleep(0.3)
    print(f"FEHLER: {image_name} n. {retries} Versuchen n. gef."); return False

# --- Helper function paste_bullet_point ---
def paste_bullet_point(text):
    if text: pyautogui.hotkey('ctrl', 'shift', '.'); clipboard.copy(str(text)); pyautogui.hotkey('ctrl', 'v'); pyautogui.press('enter'); pyautogui.press('enter')





# --- Main execution block ---
def main(patientennummer_param=None):
    global austritt_typ, patdata, glossary, oberarzt, patientennummer # patdata und glossary hinzufügen

    
    try:
        #Check, ob patientennummer bereits aus patdata erhalten wurde
        if patientennummer_param:
            patientennummer = patientennummer_param

        open_JSON()
        austritt_typ = austritt_typ_definieren()
        dictionary_ohne_None() # Extrahiert Daten in globale Variablen UND patdata dict
        definiere_glossary()

        # --- NEU: Texte aus fliesstexte.py holen ---
        print(f"Rufe fliesstexte.define_austritt_texte für Typ {austritt_typ} auf...")
        text_dt, text_epi, text_procedere = fliesstexte.define_austritt_texte(austritt_typ, patdata, glossary)
        print(f"Texte für Austrittstyp {austritt_typ} erhalten.")
        # --- Ende Neu ---

        print("Starte KISIM Automatisierung für Austrittsbericht...")
        UNIVERSAL.KISIM_im_vordergrund()
        UNIVERSAL.navigiere_bereich_berichte()
        if not find_and_click_austritt("button_neu.png"): sys.exit("Abbruch: Neu")

        UNIVERSAL.find_and_click_button_offset(image_name='button_bericht_for_offset.png', base_path=austritt_screenshots_dir, y_offset=55, confidence=0.9)

        if not find_and_click_austritt("button_suche.png"): sys.exit("Abbruch: Suche")
        pyautogui.hotkey('ctrl', 'a')
        pyautogui.press('backspace')

        austrittradionko = "austrittsbericht radioonkologie"
        clipboard.copy(austrittradionko)
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(0.1)

        if not find_and_click_austritt("button_austrittsbericht.png"): sys.exit("Abbruch: Berichtwahl")

        print("Warte auf Bericht..."); time.sleep(0.1)
        if not UNIVERSAL.prozent_zoom_100(): print("Fehler: UNIVERSAL.prozent_zoom_100() == False. Breche ab. Bitte bei Admin melden."); sys.exit()

        print("Check for button_dt als confirm")
        if not find_and_click_austritt("button_dt.png", retries=10): sys.exit("Abbruch: Bericht nicht bestätigt (DT)")
        print("Bericht offen confirm.")

        while True:
            path_leerer_block = os.path.join(austritt_screenshots_dir, 'button_leererblock.png')
            
            try:
                pyautogui.scroll(-100) #nötig zum finden von leererblock
                button_leererblock = pyautogui.locateOnScreen(path_leerer_block, confidence=0.9)       
                if button_leererblock is not None:
                    # Bestimme die Mitte des Buttons
                    button_center = pyautogui.center(button_leererblock)
                    pyautogui.click(button_center)
                    pyautogui.drag(0, -150, 0.2, button='left')
                    print('button_leererblock.png angeklickt nach oben gezogen. Beende While Loop')
                    break
            except: 
                print('button_leererblock.png not found.')
                continue

        print("Leerer Block gezogen, Klicke in dt")
        if find_and_click_austritt("button_wir_berichten.png", retries=10): 
            print("button_wir_berichten gefunden, beginne Diagnosenübernahme...")
            UNIVERSAL.ctrl_tabs(2)
            time.sleep(0.1)
            pyautogui.press('enter')
            if not UNIVERSAL.diagnose_uebernehmen(): print("UNIVERSAL.diagnose_uebernehmen() fehlgeschlagen, bitte manuell übernehmen.")

        time.sleep(0.1)
        if not find_and_click_austritt("button_wir_berichten.png", retries=10): print("button_wir_berichten nicht gefunden, beende."); sys.exit("Abbruch: button_wir_berichten.png nicht gefunden")
        
        for i in range(30):
            try:
                pyautogui.scroll(-100) # Scrollen, um sicherzustellen, dass der Button sichtbar ist
                if find_and_click_austritt("button_dt.png", retries=1, confidence=0.9):
                    print("button_dt.png gefunden und angeklickt.")
                    break
            except Exception as e:
                print(f"Fehler beim Suchen von button_dt.png: {e}")
                time.sleep(0.05)
                sys.exit("Abbruch: button_dt.png nicht gefunden nach 30 Versuchen")
        
        print("Fülle DT...")
        # --- Verwende die Variable text_dt, die von fliesstexte.py kam ---
        clipboard.copy(text_dt)
        pyautogui.hotkey('ctrl', 'v'); pyautogui.hotkey('ctrl', 'a'); pyautogui.hotkey('ctrl', 'shift', 'j') #einfügen im Blocksatz

        print("Fülle Epikrise...")
        pyautogui.hotkey('ctrl', 'tab')
        pyautogui.hotkey('ctrl', 'tab')
        pyautogui.typewrite('Epikrise') #fügt Überschrift ein
        pyautogui.hotkey('ctrl', 'tab') # Zum Inhaltsbereich
        clipboard.copy(text_epi)
        pyautogui.hotkey('ctrl', 'v'); pyautogui.hotkey('ctrl', 'a'); pyautogui.hotkey('ctrl', 'shift', 'j') #einfügen im Blocksatz
        print("Epikrise eingefügt.")

        print("Fülle Procedere...");
        for _ in range(3): # Zum Procedere-Feld navigieren
            pyautogui.hotkey('ctrl', 'tab')
        time.sleep(0.05)
        # --- Verwende die Variable text_procedere ---
        if isinstance(text_procedere, list):
            [paste_bullet_point(item) for item in text_procedere]
        else: # Fallback, falls es doch mal ein String sein sollte
            paste_bullet_point(text_procedere)
        #Schlusssatz einfügen
        schlusssatz = "Für Rückfragen stehen wir jederzeit gern zur Verfügung."
        clipboard.copy(schlusssatz)
        pyautogui.hotkey('ctrl', 'v')
        pyautogui.hotkey('ctrl', 'a'); pyautogui.hotkey('ctrl', 'shift', 'j') #Blocksatz
        print("Procedere eingefügt.")


        print("Trage Ärzte ein...")
        for _ in range(7): pyautogui.hotkey('ctrl', 'tab') # Signieren Feld
        pyautogui.press('enter') #Wechsel Signieren zu Visieren

        pyautogui.hotkey('ctrl', 'tab') #in AA Feld 
        UNIVERSAL.signation_benutzer_eintragen()

        pyautogui.hotkey('ctrl', 'tab') 
        pyautogui.hotkey('ctrl', 'tab') # Zum Stations-OA Feöd
        # Logik für Stations-OA
        wochentag = datetime.datetime.today().weekday()
        oberarzt_visieren = "Hertler C" if wochentag in [0, 1] else "Vlaskou"
        print("OA Visum:", oberarzt_visieren)
        pyautogui.typewrite(oberarzt_visieren)
        time.sleep(0.3)
        pyautogui.press('enter')

        pyautogui.hotkey('ctrl', 'tab'); pyautogui.press('enter')
        pyautogui.hotkey('ctrl', 'tab') # Zum Feld OA
        oberarzt_str = str(oberarzt) if oberarzt else ""
        vondergrun = oberarzt_str.lower() == "von der grün"
        pyautogui.typewrite('von der Gr' if vondergrun else oberarzt_str); time.sleep(0.3)
        pyautogui.press('enter')        
        print("Ärzte eingetragen.")

        print("Starte HA als Kopieempfänger eintragen")
        pyautogui.hotkey('ctrl', 'tab')
        pyautogui.hotkey('ctrl', 'tab')
        pyautogui.press('enter')
        time.sleep(0.3)

        if find_and_click_austritt(image_name="button_bericht_radioonkologie_kopie_hausarzt.png", clicks=2, confidence=0.8, retries=5):
            time.sleep(0.1)
        if find_and_click_austritt(image_name="button_bericht_radioonkologie_kopie_ubernehmen.png", confidence=0.8):
            print("Kopie-Adressaten übernommen.")
        else: 
            print("WARNUNG: Kopie Patient fehlgeschlagen.")

        print("\n--- austritt.py Skript erfolgreich beendet ---.")



    except KeyboardInterrupt: print("\nSkript durch Benutzer unterbrochen.")
    except SystemExit as e: print(f"\nSkript beendet: {e}")
    except Exception as e: print(f"\nUnerwarteter FEHLER: {e}\n{traceback.format_exc()}")


print("DEBUG: main() ist definiert, jetzt erfolgt der Aufruf mittels if __name__ == '__main__'")
if __name__ == "__main__":
    print("DEBUG: if __name__ == '__main__' ist wahr, daher wird main() aufgerufen")
    main()