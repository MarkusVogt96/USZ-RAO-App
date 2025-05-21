# -*- coding: utf-8 -*-
# Removed implicit print statement here, execution starts below
# import mouseinfo # Unused import removed
import sys
import time
import clipboard
import pyautogui
import os
import json
import traceback # Added for error handling

# --- Define Relative Paths ---
# Get the absolute path of the directory containing the current script (liste.py)
script_dir = os.path.dirname(os.path.abspath(__file__))
# Get the absolute path of the parent directory (the application root, e.g., "USZ RAO App")
app_dir = os.path.dirname(script_dir)
# Define the absolute path to patdata in the user's home directory
user_home = os.path.expanduser("~") 
patdata_dir = os.path.join(user_home, "patdata")

print(f"Script directory (liste.py): {script_dir}")
print(f"App directory: {app_dir}")
print(f"Patient data directory: {patdata_dir}")
# --- End Relative Path Definitions ---


##JSON patdata laden
# Removed hardcoded default directory path
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

# --- Main execution block ---
def main():
    print("\n--- Starte liste.py Skriptausführung ---")

    patient_id = input("Bitte die Patienten-ID eingeben: ").strip()
    # Pass the relative patdata_dir to the function
    patient_data = load_patient_data(patient_id, directory=patdata_dir)

    # Check if data was loaded successfully
    if patient_data is None:
        print("Patientendaten konnten nicht geladen werden. Skript wird beendet.")
        sys.exit(1)

    # Variablen-Definition mittels Extraktion aus variable "patient_data" (=JSON dic):
    # Use lowercase keys consistent with patdata.py export and default values
    try:
        # Combine name fields
        vorname = patient_data.get("vorname", "")
        nachname = patient_data.get("nachname", "Unbekannt")
        name = f"{vorname} {nachname}".strip() if vorname else nachname

        geburtsdatum = patient_data.get("geburtsdatum", "Unbekannt")
        alter = patient_data.get("alter", "Unbekannt")
        zimmer = patient_data.get("zimmer", "Unbekannt")
        eintrittsdatum = patient_data.get("eintrittsdatum", "Unbekannt")
        # telefon_pflege missing
        # telefon_pflege = patient_data.get("Telefonnummer_Pflege", "Unbekannt")
        oberarzt = patient_data.get("oberarzt", "Unbekannt")
        aufnahmegrund = patient_data.get("aufnahmegrund", "Unbekannt")
        tumorentitaet = patient_data.get("tumor", "Unbekannt")

        # Combine Behandlungskonzept fields
        konzepte = [str(k) for k in [
            patient_data.get("behandlungskonzept_serie1"),
            patient_data.get("behandlungskonzept_serie2"),
            patient_data.get("behandlungskonzept_serie3"),
            patient_data.get("behandlungskonzept_serie4")]
            if k and k not in ["", "Nicht erfasst", None]]
        rt_konzept = "\n".join(konzepte) if konzepte else "Nicht erfasst"

        therapieintention = patient_data.get("therapieintention", "Unbekannt") # Should be full word now
        # setting missing
        setting = patient_data.get("setting", "ambulant") # Default?
        fraktionen_pro_woche = patient_data.get("fraktionen_woche", "Unbekannt")
        rt_zeitraum_beginn = patient_data.get("datum_erste_rt", "Unbekannt")
        rt_zeitraum_ende = patient_data.get("datum_letzte_rt", "Unbekannt")
        systemtherapie = patient_data.get("chemotherapeutikum", "Keine Angabe") # Use chemo drug name

        print("Variablen erfolgreich aus JSON extrahiert.")

    except Exception as e:
        print(f"Fehler beim Extrahieren der Variablen aus JSON: {e}")
        traceback.print_exc()
        sys.exit(1)

    # --- Start Automation ---
    try:
        print("Starte Automatisierung (3s Pause zum Positionieren)...")
        time.sleep(3) #Zeit zum Klicken in Familienanamnese

        # Helper function for pasting
        def paste_with_delay(text):
            if text is None: text = "" # Ensure text is string
            clipboard.copy(str(text))
            time.sleep(0.1)
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(0.05) # Short pause after paste

        print("Fülle Felder...")
        # Name, Geburtsdatum, Alter
        paste_with_delay(name)
        pyautogui.press('enter')
        time.sleep(0.05)

        paste_with_delay(geburtsdatum)
        pyautogui.press('enter')
        time.sleep(0.05)
        pyautogui.press('enter')
        time.sleep(0.05)

        paste_with_delay(alter)
        pyautogui.typewrite(' -J') # Append suffix
        pyautogui.press('tab')
        time.sleep(0.05)

        # Zimmer
        paste_with_delay(zimmer)
        pyautogui.press('tab')
        time.sleep(0.05)

        # OA
        paste_with_delay(oberarzt)
        pyautogui.press('tab')
        time.sleep(0.05)

        # Aufnahmegrund
        paste_with_delay(aufnahmegrund)
        pyautogui.press('tab')
        time.sleep(0.05)

        # Tumor
        paste_with_delay(tumorentitaet)
        pyautogui.press('tab')
        time.sleep(0.05)

        # Intention, Setting, RT-Konzept
        pyautogui.typewrite('Therapieintention: ')
        time.sleep(0.05)
        paste_with_delay(therapieintention) # Paste the full word
        pyautogui.press('enter')
        time.sleep(0.05)

        paste_with_delay(rt_konzept) # Paste combined RT Konzept
        pyautogui.press('tab')
        time.sleep(0.05)

        # Systemtherapie
        paste_with_delay(systemtherapie) # Paste chemo drug name
        pyautogui.press('tab')
        time.sleep(0.05)

        # RT Start und Ende
        zeitraum = f"{rt_zeitraum_beginn} - {rt_zeitraum_ende}" if rt_zeitraum_beginn != "Unbekannt" and rt_zeitraum_ende != "Unbekannt" else "Unbekannt"
        paste_with_delay(zeitraum)
        pyautogui.press('tab')
        time.sleep(0.05)

        # Eintrittsdatum
        if eintrittsdatum != "Unbekannt": # Only paste if known
            pyautogui.typewrite('ET: ')
            time.sleep(0.05)
            paste_with_delay(eintrittsdatum)
        else:
            print("Eintrittsdatum unbekannt, wird nicht eingefügt.")

        #Alles Schriftgrösse 7
        print("Setze Schriftgröße auf 7...")
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.1)
        # Use direct shortcut if known, otherwise keep the alt sequence
        # Example: pyautogui.hotkey('ctrl', 'shift', '<') # Might decrease font size, depends on app
        # Keeping original alt sequence for now:
        with pyautogui.hold('alt'):
                pyautogui.press(['r', 'h', 'c']) # Ensure this sequence works reliably
        time.sleep(0.2) # Pause before typing size
        pyautogui.typewrite('7')
        time.sleep(0.1)
        pyautogui.press('enter')
        time.sleep(0.1)

        print("\n--- liste.py Skript beendet ---")

    except KeyboardInterrupt:
        print("\nSkript durch Benutzer unterbrochen.")
    except Exception as e:
        print(f"\nEin unerwarteter FEHLER ist im Automatisierungsteil aufgetreten: {e}")
        traceback.print_exc() # Print detailed traceback for debugging





print("DEBUG: main() ist definiert, jetzt erfolgt der Aufruf mittels if __name__ == '__main__'")
if __name__ == "__main__":
    print("DEBUG: if __name__ == '__main__' ist wahr, daher wird main() aufgerufen")
    main()