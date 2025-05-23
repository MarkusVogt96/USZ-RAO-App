# -*- coding: utf-8 -*-
# Removed implicit print statement here, execution starts below
import json
import os
import pyautogui
import time
import clipboard
import sys
import datetime
import traceback # Keep traceback
import UNIVERSAL # Import the central UNIVERSAL module

# --- Define Relative Paths ---
# Get the absolute path of the directory containing the current script (kons.py)
script_dir = os.path.dirname(os.path.abspath(__file__))
# Get the absolute path of the parent directory (the application root, e.g., "USZ RAO App")
app_dir = os.path.dirname(script_dir)
# Define the path to the main screenshots directory (located within the script directory)
screenshots_base_dir = os.path.join(script_dir, 'screenshots pyautogui')
# Define the specific path for this script's screenshots
kons_screenshots_dir = os.path.join(screenshots_base_dir, 'kons')
# Define the absolute path to patdata in the user's home directory
user_home = os.path.expanduser("~") 
patdata_dir = os.path.join(user_home, "patdata")

print(f"Script directory (kons.py): {script_dir}")
print(f"App directory: {app_dir}")
print(f"Patient data directory: {patdata_dir}")
print(f"Screenshots base directory: {screenshots_base_dir}")
print(f"KONS screenshots directory: {kons_screenshots_dir}")
# --- End Relative Path Definitions ---

# --- Global variables for user input ---
# These will be assigned within abfrage_userinput()
ecog = None
patverfügung = None
pflege = None
pflege_alt = None
minuten = None
beschreibung_ecog = {0: 'altersentsprechendem', 1: 'leicht reduziertem', 2: 'reduziertem', 3: 'deutlich reduziertem', 4: 'stark reduziertem'}

# --- Global variables for data read from KISIM/UNIVERSAL ---
# These will be assigned after calling UNIVERSAL functions
nachname = None
vorname = None # Added for completeness
geburtsdatum = None
alter = None
geschlecht = None
patientennummer = None
eintrittsdatum = None # Added for completeness
spi = None
rea = None
ips = None

glossary = {}
g = {}


# --- Hilfsfunktion für Glossary-Zugriff (lokal in diesem Modul) ---
def _get_from_glossary(glossary, key, default=""):
    """Sicherer Zugriff auf das Glossary-Dictionary."""
    return glossary.get(key, default) if isinstance(glossary, dict) else default



# --- User Input Function (remains largely unchanged) ---
def abfrage_userinput():
    global ecog, patverfügung, pflege, pflege_alt, minuten 

    # ECOG: Allow 'x' for unknown, consistent with patdata.py
    while True:
        ecog_input = input("ECOG eingeben (0-4, oder 'x' für unbekannt): ").strip().lower()
        if ecog_input == 'x':
            ecog = None # Store None for unknown
            break
        elif ecog_input.isdigit() and int(ecog_input) in range(5):
            ecog = int(ecog_input)
            break
        else:
             print("Ungültige Eingabe. Bitte 0-4 oder 'x' eingeben.")


    while True:
        patverfügung_input = input("Patientenverfügung vorliegend? (nur j und n akzeptiert): ").strip().lower()
        if patverfügung_input in ("j", "n"):
            patverfügung = patverfügung_input # Store 'j' or 'n'
            break
        print("Ungültige Eingabe. Bitte nur 'j' oder 'n' eingeben.")

    # Abfrage für die Anzahl abgerechneter Minuten
    while True:
        minuten_input = input("Anzahl abgerechneter Minuten: ").strip()
        if minuten_input.isdigit() and 1 <= len(minuten_input) <= 3:
            minuten = int(minuten_input)
            break
        print("Ungültige Eingabe. Bitte geben Sie eine ganze, 1-3 stellige Zahl ein.")


    # Mapping der Auswahlnummern auf die vordefinierten Namen
    pflege_mapping = {
        "1": "Däster F",
        "2": "Chinyam T",
        "3": "Reisinger M",
        "4": "Vazquez L",
        "5": "Rieser N"
    }

    print("\nWelche der folgenden Pflegeexpertinnen waren anwesend?")
    for num, name in pflege_mapping.items():
        print(f"[{num}]: {name}")
    print("[f]: Freitexteingabe")

    while True:
        pflege_input = input("Auswahl: ").strip().lower()

        if pflege_input in pflege_mapping:
            pflege = pflege_mapping[pflege_input]
            break
        elif pflege_input == "f":
            freitext = input("Bitte geben Sie den Namen der Pflegeexpertin ein (z. B. 'Mustermann A'): ").strip()
            if freitext:
                pflege = freitext
                break
            else:
                print("Freitexteingabe darf nicht leer sein, bitte erneut eingeben.")
        else:
            print("Ungültige Eingabe. Bitte geben Sie 1, 2, 3, 4, 5 oder f ein.")

    # Erstellung von pflege_alt im Format "Initial. Nachname"
    try:
        if " " in pflege:
            teile = pflege.split(" ", 1) # Split only once
            if len(teile) == 2:
                 name_teil, initial_teil = teile
                 pflege_alt = f"{initial_teil}. {name_teil}"
            else: # Handle names without space or unexpected format
                 pflege_alt = pflege
        else:
            pflege_alt = pflege  # Falls Format nicht wie erwartet
    except Exception as e:
        print(f"Fehler beim Formatieren von 'pflege_alt': {e}. Verwende Originalwert '{pflege}'.")
        pflege_alt = pflege


# --- Helper function for PyAutoGUI actions ---
def find_and_click_kons(image_filename, confidence=0.8, retries=50, delay_after=0.05):
    """Finds and clicks an image using relative paths for kons.py"""
    full_path = os.path.join(kons_screenshots_dir, image_filename)
    attempts = 0
    while attempts < retries:
        try:
            location = pyautogui.locateOnScreen(full_path, confidence=confidence)
            if location is not None:
                button_center = pyautogui.center(location)
                pyautogui.click(button_center)
                print(f'{image_filename} angeklickt.')
                time.sleep(delay_after) # Pause after action
                return True
        except pyautogui.ImageNotFoundException:
            if attempts == 0: # Print only on first failure
                 print(f'{image_filename} nicht gefunden (Versuch {attempts+1}/{retries})... Path: {full_path}')
        except Exception as e:
            print(f"Fehler bei Suche/Klick auf {image_filename}: {e}")
        attempts += 1
        time.sleep(0.07) 
    print(f"FEHLER: {image_filename} konnte nach {retries} Versuchen nicht gefunden werden.")
    return False










# --- KISIM Automation Functions (using relative paths via helper) ---
def konspall_anlegen():
    find_and_click_kons('button_neu.png')
    find_and_click_kons('button_x.png')
    pyautogui.typewrite('konsilium rad')
    find_and_click_kons('button_konspall.png')
    print("Warte auf Bericht..."); time.sleep(0.1)
    if not UNIVERSAL.prozent_zoom_100(): print("Fehler: UNIVERSAL.prozent_zoom_100() == False. Breche ab. Bitte bei Admin melden."); sys.exit()
    return True

def konsilium_radioonkologie():
    find_and_click_kons('button_konsil_radioonkologie.png')
    time.sleep(0.3) #Zeit für Verrücken der Anzeige, dann erneute location Bestimmung
    find_and_click_kons('button_konsil_radioonkologie.png')
    konsil_pall = "Konsilium Palliative Care"
    clipboard.copy(konsil_pall)
    pyautogui.hotkey('ctrl', 'a')
    pyautogui.hotkey('ctrl', 'v')
    for _ in range(17):
       pyautogui.hotkey('ctrl', 'tab')  #navigiert in Befund
    return True

def befund_eintragen():
    pyautogui.hotkey('ctrl', 'shift', 'f')
    dv = "Durchgeführt von:"
    clipboard.copy(dv)
    pyautogui.hotkey('ctrl', 'v')
    pyautogui.press('enter')
    pyautogui.press('enter')
    pyautogui.hotkey('ctrl', 'shift', 'f')

    befund = (f"PD Dr. C. Hertler, Leitende Oberärztin und {pflege_alt}, Fachexpertin Pflege Palliative Care."
              f"\n\nEs präsentierte sich {g('ein_nominativ','ein/eine')} {alter}-{g('jährig_nominativ','jährige/r')} {g('patient_nominativ','Patient/in')}, "
              f"wach und freundlich im Bett liegend angetroffen, in {beschreibung_ecog.get(ecog, "____")} Allgemeinzustand (ECOG {ecog}), SPI {spi}.")
    
    clipboard.copy(befund)
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(0.1)
    pyautogui.hotkey('ctrl', 'tab')
    pyautogui.hotkey('ctrl', 'tab') #navigiere in Beurteilung
    return True

def beurteilung_eintragen():
    #Abschnitt Symptomlast
    sl = "Symptomlast:"
    clipboard.copy(sl)
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(0.05)
    pyautogui.hotkey('ctrl', 'a')
    time.sleep(0.05)
    pyautogui.hotkey('ctrl', 'shift', 'f')
    time.sleep(0.05)
    pyautogui.press('right')
    pyautogui.press('enter')
    pyautogui.press('enter')
    pyautogui.hotkey('ctrl', 'shift', 'f')

    sl_text = (f"Zum aktuellen Zeitpunkt präsentiert sich {g('artikel_nominativ_klein')} {g('patient_nominativ')} mit vermehrtem Unterstützungsbedarf in den ADLs sowie ____. Die Orientierung zu ZOPS ist erhalten, GCS 15. Im Vordergrund steht aktuell eine nicht kontrollierte Schmerzsymptomatik / Dyspnoe / ___ .")
    clipboard.copy(sl_text)
    pyautogui.hotkey('ctrl', 'v'); pyautogui.press('enter'); pyautogui.press('enter'); pyautogui.press('enter')
    time.sleep(0.05)


    #Abschnitt Entscheidungsfindung
    ent = "Entscheidungsfindung:"
    clipboard.copy(ent)
    pyautogui.hotkey('ctrl', 'v')
    pyautogui.press('enter')
    pyautogui.press('enter')
    pyautogui.hotkey('ctrl', 'shift', 'f')

    ent_text = (f"{g('herrfrau','Herr/Frau')} {nachname} berichtet sachlich und ausführlich über die zurückliegende Leidensgeschichte. Hier wird im Verlauf klar, dass __")
    clipboard.copy(ent_text)
    pyautogui.hotkey('ctrl', 'v'); pyautogui.press('enter'); pyautogui.press('enter'); pyautogui.press('enter')
    time.sleep(0.05)


    #Abschnitt Netzwerk
    net = "Netzwerk:"
    clipboard.copy(net)
    pyautogui.hotkey('ctrl', 'v')
    pyautogui.press('enter')
    pyautogui.press('enter')
    pyautogui.hotkey('ctrl', 'shift', 'f')

    if geschlecht == 'W':
            partner = "ihrem Mann/Partner, welcher sie"
    elif geschlecht == "M":
        partner = "seiner Frau/Partnerin, welche ihn"
    net_text = (f"{g('herrfrau')} {nachname} lebt daheim zusammen mit {partner} bisher in der Bewältigung der ADLs die notwendige Unterstützung gab, zuletzt mit der Situation und dem steigenden Pflegeaufwand jedoch auch zunehmend an die eigenen Belastungsgrenzen gestossen sei. Zudem ___"
            f"\n\nODER (ggf löschen!)\n{g('herrfrau')} {nachname} lebt daheim allein und versorgte sich bisher weitestgehend eigenständig. {g('herrfrau')} {nachname}'s soziales Netzwerk bestehe primär aus Freunden/Bekannten, welche ihn zuweilen unterstützen. Zudem ___")
    clipboard.copy(net_text)
    pyautogui.hotkey('ctrl', 'v'); pyautogui.press('enter'); pyautogui.press('enter'); pyautogui.press('enter')
    time.sleep(0.05)

    #Abschnitt Support
    sup = "Support:"
    clipboard.copy(sup)
    pyautogui.hotkey('ctrl', 'v')
    pyautogui.press('enter')
    pyautogui.press('enter')
    pyautogui.hotkey('ctrl', 'shift', 'f')

    sup_text = (f"Bis anhin seien keine externen Dienste involviert gewesen, insbesondere wurde keine Unterstützung durch die Spitex wahrgenommen. Bezüglich hausinterner, supportiver Begleitmassnahmen im Sinne von Physiotherapie, Ergotherapie, Austrittsplanung durch den Sozialdienst, sowie Seelsorge und Psychoonkologie steht {g('artikel_nominativ_klein')} {g('patient_nominativ')} grundsätzlich offen gegenüber.")
    clipboard.copy(sup_text)
    pyautogui.hotkey('ctrl', 'v'); pyautogui.press('enter'); pyautogui.press('enter'); pyautogui.press('enter')
    time.sleep(0.05)

    #Abschnitt Patientenverfügung/Rea/IPS
    patver = "Patientenwille/Patientenverfügung:"
    clipboard.copy(patver)
    pyautogui.hotkey('ctrl', 'v')
    pyautogui.press('enter')
    pyautogui.press('enter')
    pyautogui.hotkey('ctrl', 'shift', 'f')

    
    if patverfügung == "j":
        verfügung_text = "Eine Patientenverfügung liegt vor."
    elif patverfügung == "n":
        verfügung_text = "Eine Patientenverfügung liegt nicht vor."
    else: # Should not happen due to input validation
        verfügung_text = "Status der Patientenverfügung unbekannt."
    patver_text = (f"{verfügung_text}\n"
                   f"Laut Dokumentation KISIM: REA = {rea}, IPS = {ips}")
    clipboard.copy(patver_text)
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(0.05)

    pyautogui.hotkey('ctrl', 'tab'); pyautogui.hotkey('ctrl', 'tab') #Navigiere in Vorschlag
    return True


def vorschlag_eintragen():
    vorschlag_text = (
        f"Weitere Begleitung durch uns.\n"
        f"Beratung zum ACP (Advanced Care Planning) anbieten")
    clipboard.copy(vorschlag_text)
    pyautogui.hotkey('ctrl', 'v'); pyautogui.hotkey('ctrl', 'a'); pyautogui.hotkey('ctrl', 'shift', '.') # Bullet points
    for _ in range(8):
        pyautogui.hotkey('ctrl', 'tab')
    return True


def visieren_eintragen():
    UNIVERSAL.signation_benutzer_eintragen()
    pyautogui.hotkey('ctrl', 'tab')
    pyautogui.hotkey('ctrl', 'tab')

    clipboard.copy(pflege)
    pyautogui.hotkey('ctrl', 'v')
    # These space/backspace is needed for triggering dropdown
    pyautogui.press('space')
    pyautogui.press('backspace')
    time.sleep(0.3) 
    pyautogui.press('enter')
    return True

def leistung_erfassen():
    # Use helper function with relative paths
    if not find_and_click_kons('button_extras.png'): return False
    if not find_and_click_kons('button_leistungerfassen.png'): return False
    if not find_and_click_kons('button_tmstat.png'): return False # Assuming stat. Leistung
    if not find_and_click_kons('button_neueleistung.png'): return False
    if not find_and_click_kons('button_persfav.png'): return False
    if not find_and_click_kons('button_konsil_stat.png'): return False
    if not find_and_click_kons('button_minuten.png'): return False

    # Input minutes
    clipboard.copy(str(minuten))
    time.sleep(0.1)
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(0.1)
    pyautogui.press('enter')
    time.sleep(0.1)
    print(f"Leistung mit {minuten} Minuten erfasst.")

    if not find_and_click_kons('button_speichern.png'): return False

    return True




def main():
    print("\n--- Starte kons.py Skriptausführung ---")
    try:
        # --- 1. Get User Input ---
        abfrage_userinput()
        print(f"User Input: ECOG={ecog}, PV={patverfügung}, Pflege={pflege}, Minuten={minuten}")

        # --- 2. Read Data using UNIVERSAL ---
        UNIVERSAL.KISIM_im_vordergrund()
        print("Lese Patientendaten aus KISIM via UNIVERSAL...")
        global nachname, vorname, geburtsdatum, alter, geschlecht, patientennummer, eintrittsdatum, rea, ips, spi
        nachname, vorname, geburtsdatum, alter, geschlecht, patientennummer, eintrittsdatum = UNIVERSAL.auslesen_patdata_KISIMzeile()
        if not patientennummer:
             print("FEHLER: Patientennummer konnte nicht aus KISIM gelesen werden. Abbruch.")
             sys.exit(1)
        if not geschlecht:
            print("FEHLER: Geschlecht nicht ausgelesen, breche Skript ab.")
            sys.exit(1)
        
        global glossary, g
        glossary = UNIVERSAL.create_patdata_glossary(geschlecht)
        # Zugriff auf Glossary über Hilfsfunktion
        g = lambda key, default="": _get_from_glossary(glossary, key, default)

        spi = UNIVERSAL.auslesen_spi()
        rea, ips = UNIVERSAL.auslesen_reaips()
        print(f"KISIM Daten gelesen: Name={nachname}, SPI={spi}, REA={rea}, IPS={ips}")


        # --- 3. Navigate & Fill Report ---
        print("Navigiere zu Berichte und erstelle Konsilium...")
        if not UNIVERSAL.navigiere_bereich_berichte(): sys.exit("Abbruch: Navigation zu Berichte fehlgeschlagen.")
        if not konspall_anlegen(): sys.exit("Abbruch: konsilium_radioonkologie() nicht erfolgreich abgeschlossen.")
        if not konsilium_radioonkologie(): sys.exit("Abbruch: konsilium_radioonkologie() nicht erfolgreich abgeschlossen.")
        if not befund_eintragen(): sys.exit("Abbruch: befund_eintragen() nicht erfolgreich abgeschlossen.")
        if not beurteilung_eintragen(): sys.exit("Abbruch: beurteilung_eintragen() nicht erfolgreich abgeschlossen.")
        if not vorschlag_eintragen(): sys.exit("Abbruch: vorschlag_eintragen() nicht erfolgreich abgeschlossen.")
        if not visieren_eintragen(): sys.exit("Abbruch: visieren_eintragen() nicht erfolgreich abgeschlossen.")




        # --- 4. Erfasse Leistung ---
        print("Erfasse Leistung...")
        if not leistung_erfassen(): print("WARNUNG: Leistungserfassung konnte nicht abgeschlossen werden.")


        print("\n--- kons.py Skript erfolgreich beendet ---")

    except KeyboardInterrupt:
        print("\nSkript durch Benutzer unterbrochen.")
    except SystemExit as e:
        print(f"\nSkript wurde beendet: {e}")
    except Exception as e:
        print(f"\nEin unerwarteter FEHLER ist im Hauptskript aufgetreten: {e}")
        traceback.print_exc()

########################################################
print("DEBUG: main() ist definiert, jetzt erfolgt der Aufruf mittels if __name__ == '__main__'")
if __name__ == "__main__":
    print("DEBUG: if __name__ == '__main__' ist wahr, daher wird main() aufgerufen")
    main()