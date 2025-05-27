import os
import pyautogui
import time
import clipboard
import sys
import datetime
from UNIVERSAL import load_json, load_json


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
patientennummer = None

def dictionary_ohne_None():
    # ... (Funktion bleibt gleich - wichtig für Variablenextraktion!) ...
    global patdata, nachname, vorname, geburtsdatum, alter, geschlecht, patientennummer, eintrittsdatum, spi, rea, ips, tumor, entity, icd_code, secondary_entity, secondary_icd_code, oberarzt, simultane_chemotherapie, chemotherapeutikum, therapieintention, fraktionen_woche, behandlungskonzept_serie1, behandlungskonzept_serie2, behandlungskonzept_serie3, behandlungskonzept_serie4, rt_konzept, datum_erste_rt, datum_letzte_rt, ecog, zimmer, aufnahmegrund
    if isinstance(patdata, dict):
        print("Lese Patientendaten aus Dictionary...")
        #Folgende Variablen werden erneut ausgelesen am Anfang und sind auskommentiert:

        nachname = patdata.get("nachname", "")
        vorname = patdata.get("vorname", "")
        geburtsdatum = patdata.get("geburtsdatum", "")
        alter = patdata.get("alter", "")
        geschlecht = patdata.get("geschlecht", "")
        #patientennummer = patdata.get("patientennummer", "")
        eintrittsdatum = patdata.get("eintrittsdatum", "")
        spi = patdata.get("spi", "")
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

def paste_with_delay(text):
            if text is None: text = "" # Ensure text is string
            clipboard.copy(str(text))
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(0.05) # Short pause after paste

# --- Main execution block ---
def main():
    print("\n--- Starte liste.py Skriptausführung ---")
    
    global patdata
    patdata = load_json(patientennummer)
    dictionary_ohne_None()

    ## --- Start Automation ---
    try:
        print("Starte Automatisierung (3s Pause zum Positionieren)...")
        time.sleep(3) #Zeit zum Klicken in Familienanamnese

        # Helper function for pasting
        

        print("Fülle Felder...")
        # Name, Geburtsdatum, Alter
        paste_with_delay(nachname)
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
        paste_with_delay(tumor)
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
        paste_with_delay(chemotherapeutikum) # Paste chemo drug name
        pyautogui.press('tab')
        time.sleep(0.05)

        # RT Start und Ende
        zeitraum = f"{datum_erste_rt} - {datum_letzte_rt}"
        paste_with_delay(zeitraum)
        pyautogui.press('tab')
        time.sleep(0.05)

        # Eintrittsdatum
        paste_with_delay(eintrittsdatum)

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





print("DEBUG: main() ist definiert, jetzt erfolgt der Aufruf mittels if __name__ == '__main__'")
if __name__ == "__main__":
    print("DEBUG: if __name__ == '__main__' ist wahr, daher wird main() aufgerufen")
    main()