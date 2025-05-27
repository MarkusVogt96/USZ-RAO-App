# -*- coding: utf-8 -*-
import pyautogui
import sys
import time
import os
import json
from datetime import datetime, timedelta 
import clipboard
import traceback 
import UNIVERSAL 

# --- Define Relative Paths ---
# Get the absolute path of the directory containing the current script (sd.py)
script_dir = os.path.dirname(os.path.abspath(__file__))
# Get the absolute path of the parent directory (the application root, e.g., "USZ RAO App")
app_dir = os.path.dirname(script_dir)
# Define the path to the main screenshots directory (located within the script directory)
screenshots_base_dir = os.path.join(script_dir, 'screenshots pyautogui')
# Define the specific path for this script's screenshots
sd_screenshots_dir = os.path.join(screenshots_base_dir, 'sb')
# Define the absolute path to patdata in the user's home directory
user_home = os.path.expanduser("~") 
patdata_dir = os.path.join(user_home, "patdata")

print(f"Script directory (sd.py): {script_dir}")
print(f"App directory: {app_dir}")
print(f"Patient data directory: {patdata_dir}")
print(f"Screenshots base directory: {screenshots_base_dir}")
print(f"SD screenshots directory: {sd_screenshots_dir}")
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

# --- Helper function for PyAutoGUI actions ---
def find_and_click_sd(image_filename, confidence=0.8, retries=100, delay_after=0.05, click_button='left', clicks=1):
    """Finds and clicks an image using relative paths for sd.py"""
    full_path = os.path.join(sd_screenshots_dir, image_filename)
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
        time.sleep(0.05) # Wait longer between retries
    print(f"FEHLER: {image_filename} konnte nach {retries} Versuchen nicht gefunden werden.")
    return False

# --- Main execution block ---
def main():
    print("\n--- Starte sd.py Skriptausführung ---")

    # --- 1. Load Patient Data ---
    patient_id_input = input("Bitte die Patienten-ID eingeben: ").strip()
    patient_data = load_patient_data(patient_id_input, directory=patdata_dir)

    if patient_data is None:
        print("Patientendaten konnten nicht geladen werden. Skript wird beendet.")
        sys.exit(1)
    UNIVERSAL.KISIM_im_vordergrund()

    # --- 2. Extract Variables and Gender Terms ---
    try:
        # Extract Gender and Terms
        geschlecht_aus_json = patient_data.get("geschlecht", "")
        glossary = {} # Initialize glossary

        if not geschlecht_aus_json:
            print("WARNUNG: 'geschlecht' nicht in JSON gefunden oder leer. Verwende Fallback-Glossary.")
            # --- CORRECTED FALLBACK ---
            # Define fallback glossary directly instead of calling removed function
            glossary = {
                "pat_nominativ_gross": "Der Patient/Die Patientin",
                "pat_nominativ_klein": "der Patient/die Patientin",
                "pat_genitiv_klein": "des Patienten/der Patientin",
                "pat_dativ_klein": "dem Patienten/der Patientin",
                "pat_akkusativ_klein": "den Patienten/die Patientin",
                "pat_artikel_genitiv": "des/der",
                "pat_patient_genitiv": "Patient/in"
            }
            # --- END CORRECTION ---
        else:
            # Use UNIVERSAL module to create the glossary
            glossary = UNIVERSAL.create_patdata_glossary(geschlecht_aus_json)
            if not glossary: # Handle case where glossary creation fails
                 print("FEHLER: Konnte Glossary nicht erstellen. Verwende minimalen Fallback.")
                 # Define minimal fallback glossary manually
                 glossary = {
                    "pat_artikel_genitiv": "des/der",
                    "pat_patient_genitiv": "Patienten/Patientin"
                 } # Minimal fallback

        # Extract terms needed for f-string (use .get for safety)
        pat_artikel_genitiv = glossary.get("pat_artikel_genitiv", "des/der")
        pat_patient_genitiv = glossary.get("pat_patient_genitiv", "Patienten/Patientin")

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
    try:
        print("Starte Sozialdienst Anmeldung...")

        UNIVERSAL.navigiere_bereich_kurve()

        # --- Navigation and Form Filling ---
        if not find_and_click_sd('button_neu.png'): sys.exit("Abbruch: button_neu nicht gefunden.")
        if not find_and_click_sd('button_suche.png'): sys.exit("Abbruch: button_suche nicht gefunden.")

        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.05)
        pyautogui.press('backspace')
        time.sleep(0.05)
        pyautogui.typewrite('sozial', interval=0.01)
        time.sleep(0.2) # Wait for search results

        if not find_and_click_sd('button_sozialberatung.png'): sys.exit("Abbruch: button_sozialberatung nicht gefunden.")
        if not find_and_click_sd('button_anmeldung.png'): sys.exit("Abbruch: button_anmeldung nicht gefunden.")

        # Navigate to Arzt field and type name
        print("Navigiere zu Anmelder und trage Namen ein...")
        for i in range(13):
            pyautogui.hotkey('ctrl', 'tab')
            time.sleep(0.03)
        pyautogui.typewrite('vogt markus', interval=0.01)
        time.sleep(0.3) # Wait for autocomplete
        pyautogui.press('enter')
        time.sleep(0.1)

        # Navigate to Grund field and paste text
        print("Trage Eintrittsgrund ein...")
        for i in range(2):
            pyautogui.hotkey('ctrl', 'tab')
            time.sleep(0.03)

        # Corrected variable names in f-string
        eintrittsgrund = (
            f"Der Eintritt {pat_artikel_genitiv} {alter}-jährigen {pat_patient_genitiv} erfolgt am {eintrittsdatum} zur Durchführung der {therapieintention_klein} Radiotherapie bei {tumorentitaet};"
            f" die stationäre Aufnahme ist aufgrund {aufnahmegrund} indiziert gewesen."
            )
        clipboard.copy(eintrittsgrund)
        time.sleep(0.1)
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(0.1)

        # Select Diagnose
        print("Wähle Diagnose...")
        pyautogui.hotkey('ctrl', 'tab') # Navigate to Diagnose button
        time.sleep(0.05)
        pyautogui.press('enter') # Open diagnose list/search
        time.sleep(0.5) # Wait for list/search to open

        # Click middle Diagnose button (assuming this selects the primary diagnosis)
        if not UNIVERSAL.find_and_click_button_offset(image_name='button_herkunft.png', base_path=sd_screenshots_dir, y_offset=40):
            print("WARNUNG: button_herkunft.png nicht gefunden/geklickt.")
        else:
            print("Diagnose ausgewählt.")
            time.sleep(0.3)
            pyautogui.press('enter') # Confirm selection
            time.sleep(0.5)
        
        if UNIVERSAL.find_button("button_inhalt_uebernehmen_aus.png", base_path=sd_screenshots_dir, max_attempts=3):
            pyautogui.hotkey('alt', 'f4') #Diagnosenfenster schliessen, falls nicht erfolgreich


        # Navigate to Austrittsdatum vorauss. and Datum
        print("Fülle Austrittsdatum...")
        for i in range(6):
            pyautogui.hotkey('ctrl', 'tab')
            time.sleep(0.03)

        # Select 'voraussichtlich'
        pyautogui.press('enter')
        pyautogui.press('down')
        pyautogui.press('down')
        pyautogui.press('enter')
        time.sleep(0.1)

        pyautogui.hotkey('ctrl', 'tab') # Navigate to AT Datum field
        time.sleep(0.05)
        # Type the RT End Date as the estimated discharge date
        pyautogui.typewrite(str(rt_zeitraum_ende), interval=0.01)
        time.sleep(0.1)

        # --- Fill checkboxes at bottom ---
        print("Setze Checkboxen...")
        pyautogui.press('pagedown')

        if not find_and_click_sd('button_finanzierung.png'): print("WARNUNG: button_finanzierung nicht gefunden/geklickt.")
        if not find_and_click_sd('button_sozialesituation.png'): print("WARNUNG: button_sozialesituation nicht gefunden/geklickt.")
        if not find_and_click_sd('button_informiert.png'): print("WARNUNG: button_informiert nicht gefunden/geklickt.")

        print("\n--- sd.py Skript beendet ---")

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