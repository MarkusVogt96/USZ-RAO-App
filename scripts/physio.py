# -*- coding: utf-8 -*-
import pyautogui
import sys
import time
import os
import traceback
import clipboard
import UNIVERSAL

# --- Define Relative Paths ---
# Get the absolute path of the directory containing the current script (physio.py)
script_dir = os.path.dirname(os.path.abspath(__file__))
# Get the absolute path of the parent directory (the application root, e.g., "USZ RAO App")
app_dir = os.path.dirname(script_dir)
# Define the path to the main screenshots directory (located within the script directory)
screenshots_base_dir = os.path.join(script_dir, 'screenshots pyautogui')
# Define the specific path for this script's screenshots
physio_screenshots_dir = os.path.join(screenshots_base_dir, 'physio')
# Define the absolute path to patdata in the user's home directory
user_home = os.path.expanduser("~") 
patdata_dir = os.path.join(user_home, "patdata")

print(f"Script directory (physio.py): {script_dir}")
print(f"App directory: {app_dir}")
print(f"Patient data directory: {patdata_dir}")
print(f"Screenshots base directory: {screenshots_base_dir}")
print(f"PHYSIO screenshots directory: {physio_screenshots_dir}")
# --- End Relative Path Definitions ---


# --- Helper function for PyAutoGUI actions ---
def find_and_click_physio(image_filename, confidence=0.8, retries=50, delay_after=0.05, click_button='left', clicks=1):
    """Finds and clicks an image using relative paths for physio.py"""
    full_path = os.path.join(physio_screenshots_dir, image_filename)
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

# --- Function to click 'unbestimmt' ---
def click_unbestimmt():
    print("Versuche 'unbestimmt' zu klicken...")
    if not find_and_click_physio('button_unbestimmt.png'):
        print("FEHLER: Konnte 'button_unbestimmt.png' nicht klicken.")
        return False
    return True

# --- Main execution block ---
def main():
    print("\n--- Starte physio.py Skriptausführung ---")

    UNIVERSAL.KISIM_im_vordergrund()
    try:
        # --- Start Automation ---
        print("Starte Physiotherapie Anmeldung...")
        UNIVERSAL.navigiere_bereich_kurve()

        if not find_and_click_physio('button_neu.png'): sys.exit("Abbruch: button_neu nicht gefunden.")

        # Warten bis Auswahl erscheint (visuelle Bestätigung)
        print("Warte auf button_auswahl...")
        found_auswahl = False
        for _ in range(10): # Wait up to ~3 seconds
             try:
                  if pyautogui.locateOnScreen(os.path.join(physio_screenshots_dir, 'button_auswahl.png'), confidence=0.9):
                       print('button_auswahl.png gefunden.')
                       found_auswahl = True
                       break
             except pyautogui.ImageNotFoundException:
                  pass
             except Exception as e:
                  print(f"Fehler bei Suche nach button_auswahl.png: {e}")
             time.sleep(0.3)
        if not found_auswahl:
             print("WARNUNG: button_auswahl.png nicht gefunden, versuche trotzdem weiter...")


        # button_verzeichnis (optional click)
        find_and_click_physio('button_verzeichnis.png', retries=2) # Try only briefly

        # button_suche
        if not find_and_click_physio('button_suche.png'): sys.exit("Abbruch: button_suche nicht gefunden.")

        # Type search term
        physio_text = 'physiotherapie im usz'
        clipboard.copy(physio_text) 
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(0.2) # Wait after typing

        # button_physio
        if not find_and_click_physio('button_physio.png'): sys.exit("Abbruch: button_physio nicht gefunden.")
        time.sleep(0.2)

        for _ in range(9):
            pyautogui.hotkey('ctrl', 'tab')
        pyautogui.press('enter') #1. Verordnung
        pyautogui.press('down')
        pyautogui.press('enter') #1. Verordnung

        for _ in range(9):
            pyautogui.hotkey('ctrl', 'tab')
        pyautogui.press('enter') #Krankheit auswählen

        for _ in range(21):
            pyautogui.hotkey('ctrl', 'tab')
        pyautogui.press('enter') #Mobilität auswählen

        for _ in range(5):
            pyautogui.hotkey('ctrl', 'tab')
        pyautogui.press('enter') #Propriozeption auswählen


        #Zum Schluss noch Diagnose einfügen:

        # button_blauerpfeil
        if not find_and_click_physio('button_blauerpfeil.png'): sys.exit("Abbruch: button_blauerpfeil nicht gefunden.")

        # Warten bis Diagnosen geladen sind
        print("Warte auf button_diagnosenoffen...")

        if not UNIVERSAL.find_and_click_button_offset(image_name='button_herkunft.png', base_path=physio_screenshots_dir, y_offset=40):
            print("WARNUNG: button_herkunft.png nicht gefunden/geklickt.")
        else:
            print("Diagnose ausgewählt.")
            time.sleep(0.3)
            pyautogui.press('enter') # Confirm selection
            time.sleep(0.5)
        
        if UNIVERSAL.find_button("button_inhalt_uebernehmen_aus.png", base_path=physio_screenshots_dir, max_attempts=3):
            pyautogui.hotkey('alt', 'f4') #Diagnosenfenster schliessen, falls nicht erfolgreich

        print("\n--- physio.py Skript beendet ---")

    except KeyboardInterrupt:
        print("\nSkript durch Benutzer unterbrochen.")
    except SystemExit as e:
        print(f"\nSkript wurde beendet: {e}")
    except Exception as e:
        print(f"\nEin unerwarteter FEHLER ist im Hauptskript aufgetreten: {e}")
        traceback.print_exc()



############################
print("DEBUG: main() ist definiert, jetzt erfolgt der Aufruf mittels if __name__ == '__main__'")
if __name__ == "__main__":
    print("DEBUG: if __name__ == '__main__' ist wahr, daher wird main() aufgerufen")
    main()