# -*- coding: utf-8 -*-
import pyautogui
import sys
import time
import os
import traceback
import UNIVERSAL

# --- Define Relative Paths ---
# Get the absolute path of the directory containing the current script (spitex.py)
script_dir = os.path.dirname(os.path.abspath(__file__))
# Get the absolute path of the parent directory (the application root, e.g., "USZ RAO App")
app_dir = os.path.dirname(script_dir)
# Define the path to the main screenshots directory (located within the script directory)
screenshots_base_dir = os.path.join(script_dir, 'screenshots pyautogui')
# Define the specific path for this script's screenshots
spitex_screenshots_dir = os.path.join(screenshots_base_dir, 'spitex')
# Define the absolute path to patdata in the user's home directory
user_home = os.path.expanduser("~") 
patdata_dir = os.path.join(user_home, "patdata")

print(f"Script directory (spitex.py): {script_dir}")
print(f"App directory: {app_dir}")
print(f"Patient data directory: {patdata_dir}")
print(f"Screenshots base directory: {screenshots_base_dir}")
print(f"SPITEX screenshots directory: {spitex_screenshots_dir}")
# --- End Relative Path Definitions ---


# --- Helper function for PyAutoGUI actions ---
def find_and_click_spitex(image_filename, confidence=0.9, retries=5, delay_after=0.1, click_button='left', clicks=1):
    """Finds and clicks an image using relative paths for spitex.py"""
    full_path = os.path.join(spitex_screenshots_dir, image_filename)
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
        time.sleep(0.3) # Wait longer between retries
    print(f"FEHLER: {image_filename} konnte nach {retries} Versuchen nicht gefunden werden.")
    return False

# --- Main execution block ---
def main():
    print("\n--- Starte spitex.py Skriptausführung ---")

    try:
        # --- Start Automation ---
        print("Starte SPITEX Anmeldung...")

        UNIVERSAL.navigiere_bereich_berichte()
        # Button neu
        if not find_and_click_spitex('button_neu.png'): sys.exit("Abbruch: button_neu nicht gefunden.")

        # Button suche
        if not find_and_click_spitex('button_suche.png'): sys.exit("Abbruch: button_suche nicht gefunden.")

        # Search for 'spitexauf'
        pyautogui.hotkey('ctrl', 'a')
        pyautogui.press('backspace')
        pyautogui.typewrite('spitexauf')
        pyautogui.press('enter') # Search after typing

        # Button spitexauftrag
        if not find_and_click_spitex('button_spitexauftrag.png'): sys.exit("Abbruch: button_spitexauftrag nicht gefunden.")

        # Wait for form/elements to load
        print("Warte auf button_leiste...")
        found_leiste = False
        for _ in range(50):
             try:
                  if pyautogui.locateOnScreen(os.path.join(spitex_screenshots_dir, 'button_leiste.png'), confidence=0.9):
                       print('button_leiste.png gefunden. Continue.')
                       found_leiste = True
                       break
             except pyautogui.ImageNotFoundException:
                  pass
             except Exception as e:
                  print(f"Fehler bei Suche nach button_leiste.png: {e}")
             time.sleep(0.1)
        if not found_leiste:
             print("FEHLER: button_leiste.png nicht gefunden. Form eventuell nicht geladen.")
             sys.exit("Abbruch: Bestätigungselement nicht gefunden.")

        # button_krankheit
        if not find_and_click_spitex('button_krankheit.png'): sys.exit("Abbruch: button_krankheit nicht gefunden.")

        # Click Maßnahmen buttons
        if not find_and_click_spitex('button_massnahmen1.png'): print("WARNUNG: button_massnahmen1 nicht gefunden/geklickt.")
        if not find_and_click_spitex('button_massnahmen2.png'): print("WARNUNG: button_massnahmen2 nicht gefunden/geklickt.")
        if not find_and_click_spitex('button_massnahmen3.png'): print("WARNUNG: button_massnahmen3 nicht gefunden/geklickt.")

        # Button textfeld
        if not find_and_click_spitex('button_textfeld.png', confidence=0.8): sys.exit("Abbruch: button_textfeld nicht gefunden.")

        # Navigate and select Gültigkeit
        print("Setze Gültigkeit...")
        time.sleep(0.1)
        for i in range(8):
            pyautogui.press('tab')
        pyautogui.press('enter') # Select '3 Monate'

        # Button speichern
        if not find_and_click_spitex('button_speichern.png'): sys.exit("Abbruch: button_speichern nicht gefunden.")

        print("\n--- spitex.py Skript beendet ---")

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