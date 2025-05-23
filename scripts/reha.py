# -*- coding: utf-8 -*-
# Removed implicit print statement here, execution starts below
import pyautogui
import sys
import time
import os
import json
import traceback # Keep traceback
import clipboard
import UNIVERSAL


# --- Define Relative Paths ---
# Get the absolute path of the directory containing the current script (reha.py)
script_dir = os.path.dirname(os.path.abspath(__file__))
# Get the absolute path of the parent directory (the application root, e.g., "USZ RAO App")
app_dir = os.path.dirname(script_dir)
# Define the path to the main screenshots directory (located within the script directory)
screenshots_base_dir = os.path.join(script_dir, 'screenshots pyautogui')
# Define the specific path for this script's screenshots
reha_screenshots_dir = os.path.join(screenshots_base_dir, 'reha')
# Define the absolute path to patdata in the user's home directory
user_home = os.path.expanduser("~") 
patdata_dir = os.path.join(user_home, "patdata")

print(f"Script directory (reha.py): {script_dir}")
print(f"App directory: {app_dir}")
print(f"Patient data directory: {patdata_dir}")
print(f"Screenshots base directory: {screenshots_base_dir}")
print(f"REHA screenshots directory: {reha_screenshots_dir}")
# --- End Relative Path Definitions ---


# --- Function to load JSON (modified to take relative path) ---
def load_patient_data(patient_id, directory):
    """
    Lädt die Patientendaten aus einer JSON-Datei basierend auf der Patienten-ID.

    Args:
        patient_id (str): Die ID des Patienten.
        directory (str): Das Verzeichnis, in dem die JSON-Dateien gespeichert sind.

    Returns:
        dict: Das Dictionary mit den Patientendaten, falls erfolgreich geladen.
        None: Falls die Datei nicht gefunden wird oder ein Fehler auftritt.
    """
    filename = f"{patient_id}.json"
    filepath = os.path.join(directory, filename)

    if not os.path.exists(filepath):
        print(f"Die Datei '{filepath}' existiert nicht.")
        return None

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        print(f"Daten aus '{filepath}' erfolgreich geladen.") # Added success message
        return data
    except json.JSONDecodeError as e:
        print(f"Fehler beim Dekodieren der JSON-Datei: {e}")
        return None
    except IOError as e:
        print(f"Fehler beim Öffnen der Datei: {e}")
        return None
    except Exception as e: # Catch other potential errors
        print(f"Ein unerwarteter Fehler trat beim Laden der JSON auf: {e}")
        traceback.print_exc()
        return None

# --- Function to get gender terms (no changes needed) ---
def get_gender_terms(geschlecht):
    geschlecht_lower = str(geschlecht).lower() if geschlecht else ""
    if geschlecht_lower == "m":
        return {
            "pat_nominativ_gross": "Der Patient", "pat_nominativ_klein": "der Patient",
            "pat_genitiv_klein": "des Patienten", "pat_dativ_klein": "dem Patienten",
            "pat_akkusativ_klein": "den Patienten", "pat_artikel_genitiv": "des",
            "pat_patient_genitiv": "Patienten"
            }
    elif geschlecht_lower == "f":
        return {
            "pat_nominativ_gross": "Die Patientin", "pat_nominativ_klein": "die Patientin",
            "pat_genitiv_klein": "der Patientin", "pat_dativ_klein": "der Patientin",
            "pat_akkusativ_klein": "die Patientin", "pat_artikel_genitiv": "der",
            "pat_patient_genitiv": "Patientin"
        }
    else:
        return {
            "pat_nominativ_gross": "Der Patient/Die Patientin", "pat_nominativ_klein": "der Patient/die Patientin",
            "pat_genitiv_klein": "des Patienten/der Patientin", "pat_dativ_klein": "dem Patienten/der Patientin",
            "pat_akkusativ_klein": "den Patienten/die Patientin", "pat_artikel_genitiv": "des/der",
            "pat_patient_genitiv": "Patient/in"
        }

# --- Helper function for PyAutoGUI actions ---
def find_and_click_reha(image_filename, confidence=0.9, retries=70, delay_after=0.05, click_button='left', clicks=1):
    """Finds and clicks an image using relative paths for reha.py"""
    full_path = os.path.join(reha_screenshots_dir, image_filename)
    attempts = 0
    while attempts < retries:
        try:
            location = pyautogui.locateOnScreen(full_path, confidence=confidence)
            if location is not None:
                button_center = pyautogui.center(location)
                pyautogui.click(button_center, button=click_button, clicks=clicks) # Use specified button and clicks
                print(f'{image_filename} ({click_button}-Klick, {clicks}x) angeklickt.')
                time.sleep(delay_after) # Pause after action
                return True
        except pyautogui.ImageNotFoundException:
            if attempts == 0: # Print only on first failure
                 print(f'{image_filename} nicht gefunden (Versuch {attempts+1}/{retries})... Path: {full_path}')
        except Exception as e:
            print(f"Fehler bei Suche/Klick auf {image_filename}: {e}")
        attempts += 1
        time.sleep(0.05) 
    print(f"FEHLER: {image_filename} konnte nach {retries} Versuchen nicht gefunden werden.")
    return False





def main():
    print("\n--- Starte reha.py Skriptausführung ---")

    # --- 1. Load Patient Data ---
    patient_id = input("Bitte die Patienten-ID eingeben: ").strip()
    patient_data = load_patient_data(patient_id, directory=patdata_dir)

    if patient_data is None:
        print("Patientendaten konnten nicht geladen werden. Skript wird beendet.")
        sys.exit(1)

    # --- 2. Extract Variables and Gender Terms ---
    try:
        # Extract Gender and Terms
        geschlecht_aus_json = patient_data.get("geschlecht", "")
        if not geschlecht_aus_json:
            print("WARNUNG: 'geschlecht' nicht in JSON gefunden oder leer. Verwende Fallback-Texte.")
        gender_terms = get_gender_terms(geschlecht_aus_json)
        # Define terms locally for clarity in f-strings (optional)
        # pat_nominativ_gross = gender_terms["pat_nominativ_gross"] ... etc.

        # Extract other variables using lowercase keys
        patient_id_json = patient_data.get("patientennummer", "Unbekannt")
        vorname = patient_data.get("vorname", "")
        nachname = patient_data.get("nachname", "Unbekannt")
        name = f"{vorname} {nachname}".strip() if vorname else nachname # Combined name
        # geschlecht already processed
        geburtsdatum = patient_data.get("geburtsdatum", "Unbekannt")
        alter = patient_data.get("alter", "Unbekannt")
        zimmer = patient_data.get("zimmer", "Unbekannt")
        eintrittsdatum = patient_data.get("eintrittsdatum", "Unbekannt")
        # telefon_pflege missing
        # telefon_pflege = patient_data.get("Telefonnummer_Pflege", "Unbekannt")
        oberarzt = patient_data.get("oberarzt", "Unbekannt")
        aufnahmegrund = patient_data.get("aufnahmegrund", "Unbekannt")
        tumorentitaet = patient_data.get("tumor", "Unbekannt")
        # Combine RT Konzept fields
        konzepte = [str(k) for k in [
            patient_data.get("behandlungskonzept_serie1"),
            patient_data.get("behandlungskonzept_serie2"),
            patient_data.get("behandlungskonzept_serie3"),
            patient_data.get("behandlungskonzept_serie4")]
            if k and k not in ["", "Nicht erfasst", None]]
        rt_konzept = "\n".join(konzepte) if konzepte else "Nicht erfasst"
        therapieintention_code = patient_data.get("therapieintention", "Unbekannt")
        # setting missing
        setting = patient_data.get("setting", "ambulant") # Default?
        fraktionen_pro_woche = patient_data.get("fraktionen_woche", "Unbekannt")
        rt_zeitraum_beginn = patient_data.get("datum_erste_rt", "Unbekannt")
        rt_zeitraum_ende = patient_data.get("datum_letzte_rt", "Unbekannt")
        systemtherapie = patient_data.get("chemotherapeutikum", "Keine Angabe")

        # Map Therapieintention (remains unchanged)
        therapieintention_map_gross = {
            "kurativ": "Kurativ-intendierte", "palliativ": "Palliativ-intendierte",
            "lokalablativ": "Lokalablativ-intendierte" }
        therapieintention_map_klein = {
            "kurativ": "kurativ-intendierten", "palliativ": "palliativ-intendierten",
            "lokalablativ": "lokalablativ-intendierten" }
        therapieintention_code_str = str(therapieintention_code).lower() if therapieintention_code else ""
        therapieintention_gross = therapieintention_map_gross.get(therapieintention_code_str, "Unbekannt")
        therapieintention_klein = therapieintention_map_klein.get(therapieintention_code_str, "unbekannten")

        print('Json fertig geladen und Variablen definiert. Proceed.')

    except Exception as e:
        print(f"Fehler beim Extrahieren der Variablen aus JSON: {e}")
        traceback.print_exc()
        sys.exit(1)


    # --- 3. Start Automation ---
    UNIVERSAL.KISIM_im_vordergrund()
    try:
        print("Starte REHA Anmeldung...")
        
        if not UNIVERSAL.navigiere_bereich_berichte(): sys.exit("Abbruch: Navigation zu bereich_berichte fehlgeschlagen.")
        # --- Navigation and Form Filling ---
        if not find_and_click_reha('button_neu.png'): sys.exit("Abbruch: button_neu nicht gefunden.")
        time.sleep(0.1)

        # Navigate to search field and type 'reha'
        print("Navigiere zu Suchfeld und suche 'reha'...")
        for i in range(6):
            pyautogui.press('tab')
        pyautogui.hotkey('ctrl', 'a')
        pyautogui.press('backspace')
        pyautogui.typewrite('reha')

        # button_einweisungreha
        if not find_and_click_reha('button_einweisungreha.png'): sys.exit("Abbruch: button_einweisungreha nicht gefunden.")

        # Wait for form to load
        print("Warte auf Bericht..."); time.sleep(0.1)
        if not UNIVERSAL.prozent_zoom_100(): print("Fehler: UNIVERSAL.prozent_zoom_100() == False. Breche ab. Bitte bei Admin melden."); sys.exit()
        if not find_and_click_reha('button_reha_offen_confirm.png'): sys.exit("Abbruch: button_einweisungreha nicht gefunden.")
        time.sleep(0.2)

        # button_krankheit
        if not find_and_click_reha('button_krankheit.png'): sys.exit("Abbruch: button_krankheit nicht gefunden.")
        time.sleep(0.1)

        # button_dauer
        if not find_and_click_reha('button_dauer.png'): sys.exit("Abbruch: button_dauer nicht gefunden.")
        time.sleep(0.1)

        # Navigate and select 'Rehabilitation'
        pyautogui.hotkey('ctrl', 'tab')
        pyautogui.hotkey('ctrl', 'tab')
        pyautogui.press('enter') # Rehabilitation
        time.sleep(0.1)

        # Navigate and select 'onkol. Reha'
        for i in range(8):
            pyautogui.press('tab')
        pyautogui.press('enter') # onkol. Reha
        time.sleep(0.1)


        # button_probleme
        if not find_and_click_reha('button_probleme.png'): sys.exit("Abbruch: button_probleme nicht gefunden.")

        # button_ubernehmen
        if not find_and_click_reha('button_ubernehmen.png', confidence=0.8): sys.exit("Abbruch: button_ubernehmen nicht gefunden.")

        # button_dauer (again?) and type '2'
        if not find_and_click_reha('button_dauer.png', confidence=0.8): sys.exit("Abbruch: button_dauer (2. Mal) nicht gefunden.")
        pyautogui.typewrite('2')
        time.sleep(0.1)

        # --- Fill remaining fields using Tab/Enter ---
        print("Fülle weitere Felder über Tab-Navigation...")

        def press_ctrl_tab(tabs=1):
             for _ in range(tabs):
                  pyautogui.hotkey('ctrl', 'tab')

        press_ctrl_tab(tabs=25)
        pyautogui.press('enter') # red. AZ
        time.sleep(0.1)

        press_ctrl_tab(tabs=2) 
        pyautogui.press('enter') # unzur. Ernährungszustand
        time.sleep(0.1)

        press_ctrl_tab(tabs=16)
        pyautogui.typewrite(str(eintrittsdatum)) # Use value from JSON
        time.sleep(0.1)

        
        press_ctrl_tab(tabs=2) # To Fähigkeit 1
        pyautogui.press('enter') # Kostaufbau

        press_ctrl_tab(tabs=1) # To Fähigkeit 2
        pyautogui.press('enter') # Wiedereingliederung Alltag
        
        press_ctrl_tab(tabs=4) # To Fähigkeit 3
        pyautogui.press('enter') # Erhöhung körperliche Selbstständigkeit

        press_ctrl_tab(tabs=16) # To Therapiemassnahmen
        pyautogui.press('enter') # Physiotherapie

        press_ctrl_tab(tabs=21) # To Beatmung
        pyautogui.press('enter') # Beatmung Nein

        press_ctrl_tab(tabs=3) # To ZVK
        pyautogui.press('enter') # ZVK Nein

        press_ctrl_tab(tabs=9) # To Port a Cath
        pyautogui.press('enter') # Port a Cath Nein

        press_ctrl_tab(tabs=3) # To Sauerstoff
        pyautogui.press('enter') # Sauerstoff Nein

        press_ctrl_tab(tabs=3) # To Tracheostoma
        pyautogui.press('enter') # Tracheostoma Nein

        press_ctrl_tab(tabs=3) # To Dialysepflichtig
        pyautogui.press('enter') # Dialysepflichtig Nein

        press_ctrl_tab(tabs=10) # To iv Antibiose
        pyautogui.press('enter') # iv Antibiose Nein

        press_ctrl_tab(tabs=5) # To DK Cystofix
        pyautogui.press('enter') # DK Cystofix Nein

        press_ctrl_tab(tabs=3) # To VAC
        pyautogui.press('enter') # VAC Nein

        press_ctrl_tab(tabs=3) # To Isolation
        pyautogui.press('enter') # Isolation Nein

        press_ctrl_tab(tabs=3) # To Sitzwache
        pyautogui.press('enter') # Sitzwache Nein

        # ADL Status
        press_ctrl_tab(tabs=8) # To Essen/Trinken
        pyautogui.press('enter') # teilweise

        press_ctrl_tab(tabs=4) # To Körperpflege
        pyautogui.press('enter') # teilweise

        press_ctrl_tab(tabs=3) # To Ankleiden
        pyautogui.press('enter') # sst

        press_ctrl_tab(tabs=5) # To Fortbewegung
        pyautogui.press('enter') # teilweise

        press_ctrl_tab(tabs=4) # To Ausscheidung
        pyautogui.press('enter') # teilweise


        # Visierender Arzt
        print("Trage visierenden Arzt ein...")
        press_ctrl_tab(tabs=14) # Navigate to Vis. Arzt field
        pyautogui.typewrite('vogt markus')
        time.sleep(0.3) # Wait for autocomplete
        pyautogui.press('enter')
        time.sleep(0.5)

        print("\n--- reha.py Skript beendet ---")

    except KeyboardInterrupt:
        print("\nSkript durch Benutzer unterbrochen.")
    except SystemExit as e:
        print(f"\nSkript wurde beendet: {e}")
    except Exception as e:
        print(f"\nEin unerwarteter FEHLER ist im Hauptskript aufgetreten: {e}")
        traceback.print_exc()


print("DEBUG: main() ist definiert, jetzt erfolgt der Aufruf mittels if __name__ == '__main__'")
if __name__ == "__main__":
    print("DEBUG: if __name__ == '__main__' ist wahr, daher wird main() aufgerufen")
    main()