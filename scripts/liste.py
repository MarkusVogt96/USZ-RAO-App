import os
import pyautogui
import time
import clipboard
import sys
import datetime
# CHANGED: Removed duplicate import
from UNIVERSAL import load_json


# Get the absolute path of the directory containing the current script (patdata.py)
script_dir = os.path.dirname(os.path.abspath(__file__))
# Get the absolute path of the parent directory (the application root, e.g., "USZ RAO App")
app_dir = os.path.dirname(script_dir)
# Define the path to the main screenshots directory (located within the script directory)
screenshots_dir = os.path.join(script_dir, 'screenshots pyautogui')
# Define the absolute path to patdata in the user's home directory
user_home = os.path.expanduser("~")
patdata_dir = os.path.join(user_home, "patdata")


print(f"Script directory (liste.py): {script_dir}")
print(f"App directory: {app_dir}")
print(f"Patient data directory: {patdata_dir}")
# --- End Relative Path Definitions ---


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


glossary = {}
patdata = {} # Initialize patdata to avoid potential errors before loading

def dictionary_ohne_None():
    """
    Loads patient data from the global 'patdata' dictionary into global variables.
    Prints the value of each loaded variable for debugging purposes.
    """
    global nachname, vorname, geburtsdatum, alter, geschlecht, patientennummer, eintrittsdatum, spi, rea, ips, tumor, entity, icd_code, secondary_entity, secondary_icd_code, oberarzt, simultane_chemotherapie, chemotherapeutikum, therapieintention, fraktionen_woche, behandlungskonzept_serie1, behandlungskonzept_serie2, behandlungskonzept_serie3, behandlungskonzept_serie4, rt_konzept, datum_erste_rt, datum_letzte_rt, ecog, zimmer, aufnahmegrund
    if isinstance(patdata, dict):
        print("\n--- Lese Patientendaten aus Dictionary und logge Werte ---")

        # ADDED: Detailed logging for each variable after it's loaded.
        nachname = patdata.get("nachname", "")
        print(f"  Loaded nachname: '{nachname}'")
        vorname = patdata.get("vorname", "")
        print(f"  Loaded vorname: '{vorname}'")
        geburtsdatum = patdata.get("geburtsdatum", "")
        print(f"  Loaded geburtsdatum: '{geburtsdatum}'")
        alter = patdata.get("alter", "")
        print(f"  Loaded alter: '{alter}'")
        geschlecht = patdata.get("geschlecht", "")
        print(f"  Loaded geschlecht: '{geschlecht}'")
        eintrittsdatum = patdata.get("eintrittsdatum", "")
        print(f"  Loaded eintrittsdatum: '{eintrittsdatum}'")
        spi = patdata.get("spi", "")
        # print(f"  Loaded spi: '{spi}'") # Uncomment if needed
        tumor = patdata.get("tumor", "")
        print(f"  Loaded tumor: '{tumor}'")
        entity = patdata.get("entity", "")
        # print(f"  Loaded entity: '{entity}'") # Uncomment if needed
        icd_code = patdata.get("icd_code", "")
        # print(f"  Loaded icd_code: '{icd_code}'") # Uncomment if needed
        oberarzt = patdata.get("oberarzt", "")
        print(f"  Loaded oberarzt: '{oberarzt}'")
        simultane_chemotherapie = patdata.get("simultane_chemotherapie", "")
        # print(f"  Loaded simultane_chemotherapie: '{simultane_chemotherapie}'") # Uncomment if needed
        chemotherapeutikum = patdata.get("chemotherapeutikum", "")
        print(f"  Loaded chemotherapeutikum: '{chemotherapeutikum}'")
        therapieintention = patdata.get("therapieintention", "")
        print(f"  Loaded therapieintention: '{therapieintention}'")
        fraktionen_woche = patdata.get("fraktionen_woche", "")
        # print(f"  Loaded fraktionen_woche: '{fraktionen_woche}'") # Uncomment if needed
        behandlungskonzept_serie1 = patdata.get("behandlungskonzept_serie1", "")
        print(f"  Loaded behandlungskonzept_serie1: '{behandlungskonzept_serie1}'")
        behandlungskonzept_serie2 = patdata.get("behandlungskonzept_serie2", "")
        print(f"  Loaded behandlungskonzept_serie2: '{behandlungskonzept_serie2}'")
        behandlungskonzept_serie3 = patdata.get("behandlungskonzept_serie3", "")
        print(f"  Loaded behandlungskonzept_serie3: '{behandlungskonzept_serie3}'")
        behandlungskonzept_serie4 = patdata.get("behandlungskonzept_serie4", "")
        print(f"  Loaded behandlungskonzept_serie4: '{behandlungskonzept_serie4}'")
        datum_erste_rt = patdata.get("datum_erste_rt", "")
        print(f"  Loaded datum_erste_rt: '{datum_erste_rt}'")
        datum_letzte_rt = patdata.get("datum_letzte_rt", "")
        print(f"  Loaded datum_letzte_rt: '{datum_letzte_rt}'")
        ecog = patdata.get("ecog", "")
        # print(f"  Loaded ecog: '{ecog}'") # Uncomment if needed
        zimmer = patdata.get("zimmer", "")
        print(f"  Loaded zimmer: '{zimmer}'")
        aufnahmegrund = patdata.get("aufnahmegrund", "")
        print(f"  Loaded aufnahmegrund: '{aufnahmegrund}'")

        print("\nVariablen aus patdata.json erfolgreich geladen und geloggt.")
    else:
        print("FEHLER: patdata ist kein Dictionary. Skript wird beendet.", file=sys.stderr)
        sys.exit(1)

def paste_with_delay(text):
    """Copies text to clipboard and pastes it, with logging and a delay."""
    if text is None:
        text = "" # Ensure text is a string
    text_to_paste = str(text)
    
    # ADDED: Logging to show what is about to be pasted.
    print(f"  -> Pasting: '{text_to_paste}'")
    clipboard.copy(text_to_paste)
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(0.1) 

# --- Main execution block ---
def main():
    print("\n--- Starte liste.py Skriptausführung ---")
    while True:
        patientennummer = input("Bitte Patientennummer eingeben (z.B. 123456): ").strip()
        if patientennummer.isdigit() and len(patientennummer) > 3:
            print(f"Patientennummer '{patientennummer}' erkannt, versuche, Daten zu laden...")
            break
        else:
            print("Ungültige Eingabe. Bitte eine gültige Nummer eingeben.")

    global patdata
    patdata = load_json(patientennummer)
    if patdata is None:
        print(f"Konnte keine Daten für Patientennummer {patientennummer} laden. Skript wird beendet.", file=sys.stderr)
        return # Exit main function cleanly

    dictionary_ohne_None()

    ## --- Start Automation ---
    print("\nStarte Automatisierung (3s Pause zum Positionieren des Cursors)...")
    time.sleep(3)

    print("Fülle Felder...")
    # Name, Vorname
    paste_with_delay(nachname)
    pyautogui.typewrite(',')
    time.sleep(0.1) # Small delay
    paste_with_delay(vorname)
    pyautogui.press('enter')
    time.sleep(0.1)

    # Geburtsdatum
    paste_with_delay(geburtsdatum)
    pyautogui.press('enter')
    time.sleep(0.2)
    pyautogui.press('enter') # Assuming two enters are needed
    time.sleep(0.2)

    # Alter
    paste_with_delay(alter)
    pyautogui.typewrite(' -j.') # Append suffix
    pyautogui.press('tab')
    time.sleep(0.4) # CHANGED: Increased delay after tab for reliability

    # Zimmer
    paste_with_delay(zimmer)
    pyautogui.press('tab')
    time.sleep(0.4) # CHANGED: Increased delay after tab for reliability

    # OA
    paste_with_delay(oberarzt)
    pyautogui.press('tab')
    time.sleep(0.4) # CHANGED: Increased delay after tab for reliability

    # Aufnahmegrund
    paste_with_delay(aufnahmegrund)
    pyautogui.press('tab')
    time.sleep(0.4) # CHANGED: Increased delay after tab for reliability

    # Tumor
    paste_with_delay(tumor)
    pyautogui.press('tab')
    time.sleep(0.4) # CHANGED: Increased delay after tab for reliability

    # Intention, Setting, RT-Konzept
    pyautogui.typewrite('Therapieintention: ')
    time.sleep(0.1)
    paste_with_delay(therapieintention)
    pyautogui.press('enter')
    pyautogui.press('enter')
    time.sleep(0.2)

    paste_with_delay(behandlungskonzept_serie1)
    pyautogui.press('enter')
    time.sleep(0.2)
    paste_with_delay(behandlungskonzept_serie2)
    pyautogui.press('enter')
    time.sleep(0.2)
    paste_with_delay(behandlungskonzept_serie3)
    pyautogui.press('enter')
    time.sleep(0.2)
    paste_with_delay(behandlungskonzept_serie4)
    time.sleep(0.1)
    pyautogui.press('tab')
    time.sleep(0.25) # CHANGED: Increased delay after tab for reliability

    # Systemtherapie
    if not simultane_chemotherapie:
        keine_systemtherapie = "keine simultane Systemtherapie"
        clipboard.copy(keine_systemtherapie)
        pyautogui.hotkey('ctrl', 'v')
    else: 
        paste_with_delay(chemotherapeutikum)
        pyautogui.press('tab')
        time.sleep(0.25) # CHANGED: Increased delay after tab for reliability

    # RT Start und Ende
    zeitraum = f"{datum_erste_rt} - {datum_letzte_rt}" if datum_erste_rt and datum_letzte_rt else ""
    paste_with_delay(zeitraum)
    pyautogui.press('tab')
    time.sleep(0.25) # CHANGED: Increased delay after tab for reliability

    # Eintrittsdatum
    pyautogui.typewrite('ET: ')
    time.sleep(0.1)
    paste_with_delay(eintrittsdatum)
    pyautogui.press('enter')
    time.sleep(0.1)
    austritt = f"\nAT:\nnach:"
    paste_with_delay(austritt)

    #Alles Schriftgrösse 7
    print("\nSetze Schriftgröße auf 7...")
    pyautogui.hotkey('ctrl', 'a')
    time.sleep(0.2)
    with pyautogui.hold('alt'):
        pyautogui.press(['r', 'h', 'c'])
    time.sleep(0.3) # Pause before typing size
    pyautogui.typewrite('7')
    time.sleep(0.1)
    pyautogui.press('enter')
    time.sleep(0.1)

    print("\n--- liste.py Skript beendet ---")


if __name__ == "__main__":
    main()