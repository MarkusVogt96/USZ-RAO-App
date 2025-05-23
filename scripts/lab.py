# -*- coding: utf-8 -*-
import pyautogui
import sys
import time
import os
import clipboard
import UNIVERSAL 
from datetime import datetime, timedelta
import traceback


# --- Define Paths ---
# Get the absolute path of the directory containing the current script (lab.py)
script_dir = os.path.dirname(os.path.abspath(__file__))
# Get the absolute path of the parent directory (the application root, e.g., "USZ RAO App")
app_dir = os.path.dirname(script_dir)
# Define the path to the main screenshots directory (located within the script directory)
screenshots_base_dir = os.path.join(script_dir, 'screenshots pyautogui')
# Define the specific path for this script's screenshots
lab_screenshots_dir = os.path.join(screenshots_base_dir, 'lab')
# Define the absolute path to patdata in the user's home directory
user_home = os.path.expanduser("~") 
patdata_dir = os.path.join(user_home, "patdata")


print(f"Script directory (lab.py): {script_dir}")
print(f"App directory: {app_dir}")
print(f"Patient data directory: {patdata_dir}")
print(f"Screenshots base directory: {screenshots_base_dir}")
print(f"LAB screenshots directory: {lab_screenshots_dir}")
# --- End Relative Path Definitions ---



datum_labor = None
auswahl = None

# --- Input Functions (remain unchanged) ---
def input_tage():
    # Removed global zahl as it's only used locally and returned
    while True:
        try:
            tage = int(input("Labor in wie vielen Tagen? (0 = heute, 1 = morgen, 2 = übermorgen ...) "))
            # Add check for negative numbers if needed
            if tage >= 0:
                 return tage
            else:
                 print("Bitte eine nicht-negative ganze Zahl eingeben.")
        except ValueError:
            print("Bitte geben Sie eine ganze Zahl ein.")

def userinput_labordatum():
    global datum_labor # Declare modification of global
    tage_in_zukunft = input_tage()
    heute = datetime.now()
    zukunft = heute + timedelta(days=tage_in_zukunft)
    datum_labor = zukunft.strftime("%d.%m.%Y")
    print(f"Labor wird für Datum {datum_labor} angemeldet.")

def userinput_auswahl():
    global auswahl # Declare modification of global
    optionen = (["h", "i", "b"])
    while True:
        choice = input("Was anmelden? (h = HAD, i = IKC Niere+CRP, b = beides): ").lower().strip() # Use different variable name
        if choice in optionen:
            auswahl = choice # Assign to global variable
            return auswahl
        else:
            print(f"Ungültige Eingabe. Bitte wählen Sie aus {', '.join(optionen)}.")

# --- Helper function for PyAutoGUI actions ---
def find_and_click_lab(image_filename, confidence=0.9, retries=50, delay_after=0.05, click_button='left'):
    """Finds and clicks an image using relative paths for lab.py"""
    full_path = os.path.join(lab_screenshots_dir, image_filename)
    attempts = 0
    while attempts < retries:
        try:
            location = pyautogui.locateOnScreen(full_path, confidence=confidence)
            if location is not None:
                button_center = pyautogui.center(location)
                pyautogui.click(button_center, button=click_button) # Use specified button
                print(f'{image_filename} ({click_button}-Klick) angeklickt.')
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

# --- Main execution block ---
def main():
    print("\n--- Starte lab.py Skriptausführung ---")

    try:
        # --- 1. Get User Input ---
        userinput_labordatum()
        userinput_auswahl()

        # --- 2. Navigate to Kurve ---
        UNIVERSAL.KISIM_im_vordergrund()
        print("Navigiere zu Bereich Kurve...")
        if not UNIVERSAL.navigiere_bereich_kurve():
            sys.exit("FEHLER: Navigation zum Bereich Kurve fehlgeschlagen.")
        print("Bereich Kurve erreicht.")

        # --- 3. HAD Anmeldung (falls ausgewählt) ---
        if auswahl == 'h' or auswahl == 'b':
            print("\n--- Starte HAD Anmeldung ---")
            if UNIVERSAL.labor_oeffne_hadh() is not True:
                print("FEHLER in Funktion UNIVERSAL.labor_oeffne_hadh(). Breche ab.")
                sys.exit()
            if UNIVERSAL.laborhadh_ausfuellen(datum_labor) is not True:
                print("FEHLER in Funktion UNIVERSAL.laborhadh_ausfuellen(). Breche ab.")
                sys.exit()
            

        # --- 4. IKC Anmeldung (falls ausgewählt) ---
        if auswahl == 'i' or auswahl == 'b':
            print("\n--- Starte IKC Anmeldung ---")

            # button_neu (find within Kurve context)
            if not find_and_click_lab('button_neu.png'): sys.exit("FEHLER: button_neu.png für IKC nicht gefunden.")

            # Button Suchfeld
            if not find_and_click_lab('button_suche.png'): sys.exit("FEHLER: button_suche.png für IKC nicht gefunden.")

            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.05)
            pyautogui.press('backspace')
            pyautogui.typewrite('ikc blut', interval=0.01)

            # Button IKC Blut
            if not find_and_click_lab('button_ikcblut.png', confidence=0.8): sys.exit("FEHLER: button_ikcblut.png nicht gefunden.")

            # Button IKC Blau (Rechtsklick)
            if not find_and_click_lab('button_blau_ikc.png', confidence=0.8, click_button='right'): sys.exit("FEHLER: button_blau_ikc.png nicht gefunden.")

            # Zeit eintragen
            for i in range(3):
                pyautogui.press('tab')
            clipboard.copy(datum_labor)
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(0.1)
            pyautogui.press('tab')
            pyautogui.press('tab')
            zeit = '06:00'
            clipboard.copy(zeit)
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(0.1)


            # Button Suche IKC
            if not find_and_click_lab('button_suche_ikc.png', confidence=0.8): sys.exit("FEHLER: button_suche_ikc.png nicht gefunden.")

            pyautogui.hotkey('ctrl', 'a')
            pyautogui.press('backspace')
            time.sleep(0.05)
            pyautogui.typewrite('nieren')
            pyautogui.press('enter')
            time.sleep(0.3) # Wait for search results

            # Nierenblock hinzufügen function (simplified)
            print("Füge Nierenblock hinzu...")
            if not find_and_click_lab('button_nierenblock.png', retries=10):
                 print("WARNUNG: Konnte Nierenblock nicht hinzufügen nach mehreren Versuchen.")
                 # Decide how to proceed: continue or exit? Continuing for now.
            else:
                 # Optional: Add confirmation check for button_niereja.png if needed
                 time.sleep(0.05) # Wait after adding block
                 print("Nierenblock hinzugefügt (oder Klick versucht).")


            # Button Suche IKC (again for CRP)
            if not find_and_click_lab('button_suche_ikc.png', confidence=0.9): sys.exit("FEHLER: button_suche_ikc.png (für CRP) nicht gefunden.")

            pyautogui.hotkey('ctrl', 'a')
            pyautogui.press('backspace')
            pyautogui.typewrite('crp')
            pyautogui.press('enter')
            time.sleep(0.3) # Wait for search results

            # Button CRP
            if not find_and_click_lab('button_crp.png', confidence=0.8): sys.exit("FEHLER: button_crp.png nicht gefunden.")
            time.sleep(0.3) # Wait after adding CRP

            # Button Speichern
            if not find_and_click_lab('button_speichern.png', confidence=0.8): sys.exit("FEHLER: button_speichern.png nicht gefunden.")

            # Optional: Handle potential save confirmation/error message
            # Button Fehlermeldung Speichern - Check briefly if it appears
            print("Prüfe auf Fehlermeldung nach Speichern...")
            if find_and_click_lab('button_meldung_speichern.png', confidence=0.8, retries=30, delay_after=0.05):
                print("Fehlermeldung beim Speichern gefunden und weggeklickt.")
            else:
                print("Keine Fehlermeldung beim Speichern gefunden.")

            print("--- IKC Anmeldung beendet ---")

        print("\n--- lab.py Skript beendet ---")

    except KeyboardInterrupt:
        print("\nSkript durch Benutzer unterbrochen.")
    except SystemExit as e:
        print(f"\nSkript wurde beendet: {e}")
    except Exception as e:
        print(f"\nEin unerwarteter FEHLER ist im Hauptskript aufgetreten: {e}")
        traceback.print_exc()



if __name__ == "__main__":
    main()