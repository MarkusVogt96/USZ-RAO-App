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
    while True:
        try:
            tage = int(input("Labor in wie vielen Tagen? (0 = heute, 1 = morgen, 2 = übermorgen ...) "))
            if tage >= 0:
                 return tage
            else:
                 print("Bitte eine nicht-negative ganze Zahl eingeben.")
        except ValueError:
            print("Bitte geben Sie eine ganze Zahl ein.")

def userinput_labordatum():
    global datum_labor
    tage_in_zukunft = input_tage()
    heute = datetime.now()
    zukunft = heute + timedelta(days=tage_in_zukunft)
    datum_labor = zukunft.strftime("%d.%m.%Y")
    print(f"Labor wird für Datum {datum_labor} angemeldet.")

def userinput_auswahl():
    global auswahl
    optionen = (["h", "i", "b"])
    while True:
        choice = input("Was anmelden? (h = HAD, i = IKC Niere+CRP, b = beides): ").lower().strip()
        if choice in optionen:
            auswahl = choice
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
                pyautogui.click(button_center, button=click_button)
                print(f'{image_filename} ({click_button}-Klick) angeklickt.')
                time.sleep(delay_after)
                return True
        except pyautogui.ImageNotFoundException:
            if attempts == 0:
                 print(f'{image_filename} nicht gefunden (Versuch {attempts+1}/{retries})... Path: {full_path}')
        except Exception as e:
            print(f"Fehler bei Suche/Klick auf {image_filename}: {e}")
        attempts += 1
        time.sleep(0.05)
    print(f"FEHLER: {image_filename} konnte nach {retries} Versuchen nicht gefunden werden.")
    return False

def find_lab(image_filename, confidence=0.9, retries=50):
    """Finds an image using relative paths for lab.py without clicking."""
    full_path = os.path.join(lab_screenshots_dir, image_filename)
    attempts = 0
    while attempts < retries:
        try:
            location = pyautogui.locateOnScreen(full_path, confidence=confidence)
            if location is not None:
                print(f"{image_filename} gefunden.")
                return True
        except pyautogui.ImageNotFoundException:
            if attempts == 0:
                 print(f'{image_filename} nicht gefunden (Versuch {attempts+1}/{retries})... Path: {full_path}')
        except Exception as e:
            print(f"Fehler bei Suche nach {image_filename}: {e}")
        attempts += 1
        time.sleep(0.05)
    print(f"FEHLER: {image_filename} konnte nach {retries} Versuchen nicht gefunden werden.")
    return False

# --- Workflow 1: Standard Labor für stationäre Patienten ---
def standard_labor_station():
    """Führt die Standard-Laboranmeldung für stationäre Patienten durch."""
    print("\n--- Starte Workflow: Standard Labor Station ---")
    
    userinput_labordatum()
    userinput_auswahl()

    UNIVERSAL.KISIM_im_vordergrund()
    print("Navigiere zu Bereich Kurve...")
    if not UNIVERSAL.navigiere_bereich_kurve():
        sys.exit("FEHLER: Navigation zum Bereich Kurve fehlgeschlagen.")
    print("Bereich Kurve erreicht.")

    if auswahl == 'h' or auswahl == 'b':
        print("\n--- Starte HAD Anmeldung ---")
        if not UNIVERSAL.labor_oeffne_hadh():
            sys.exit("FEHLER in Funktion UNIVERSAL.labor_oeffne_hadh(). Breche ab.")
        if not UNIVERSAL.laborhadh_ausfuellen(datum_labor):
            sys.exit("FEHLER in Funktion UNIVERSAL.laborhadh_ausfuellen(). Breche ab.")
        
    if auswahl == 'i' or auswahl == 'b':
        print("\n--- Starte IKC Anmeldung ---")
        if not find_and_click_lab('button_neu.png'): sys.exit("FEHLER: button_neu.png für IKC nicht gefunden.")
        if not find_and_click_lab('button_suche.png'): sys.exit("FEHLER: button_suche.png für IKC nicht gefunden.")
        pyautogui.hotkey('ctrl', 'a'); time.sleep(0.05); pyautogui.press('backspace')
        pyautogui.typewrite('ikc blut', interval=0.01)
        if not find_and_click_lab('button_ikcblut.png', confidence=0.8): sys.exit("FEHLER: button_ikcblut.png nicht gefunden.")
        if not find_and_click_lab('button_blau_ikc.png', confidence=0.8, click_button='right'): sys.exit("FEHLER: button_blau_ikc.png nicht gefunden.")
        for i in range(3): pyautogui.press('tab')
        clipboard.copy(datum_labor); pyautogui.hotkey('ctrl', 'v'); time.sleep(0.1)
        pyautogui.press('tab'); pyautogui.press('tab')
        zeit = '07:00'; clipboard.copy(zeit); pyautogui.hotkey('ctrl', 'v'); time.sleep(0.1)
        if not find_and_click_lab('button_suche_ikc.png', confidence=0.8): sys.exit("FEHLER: button_suche_ikc.png nicht gefunden.")
        pyautogui.hotkey('ctrl', 'a'); pyautogui.press('backspace'); time.sleep(0.05)
        pyautogui.typewrite('nieren'); pyautogui.press('enter'); time.sleep(0.3)
        print("Füge Nierenblock hinzu...")
        if not find_and_click_lab('button_nierenblock.png', retries=10):
             print("WARNUNG: Konnte Nierenblock nicht hinzufügen nach mehreren Versuchen.")
        else:
             time.sleep(0.05); print("Nierenblock hinzugefügt (oder Klick versucht).")
        if not find_and_click_lab('button_suche_ikc.png', confidence=0.9): sys.exit("FEHLER: button_suche_ikc.png (für CRP) nicht gefunden.")
        pyautogui.hotkey('ctrl', 'a'); pyautogui.press('backspace'); pyautogui.typewrite('crp'); pyautogui.press('enter'); time.sleep(0.3)
        if not find_and_click_lab('button_crp.png', confidence=0.8): sys.exit("FEHLER: button_crp.png nicht gefunden.")
        time.sleep(0.3)
        if not find_and_click_lab('button_speichern.png', confidence=0.8): sys.exit("FEHLER: button_speichern.png nicht gefunden.")
        print("Prüfe auf Fehlermeldung nach Speichern...")
        if find_and_click_lab('button_meldung_speichern.png', confidence=0.8, retries=30, delay_after=0.05):
            print("Fehlermeldung beim Speichern gefunden und weggeklickt.")
        else:
            print("Keine Fehlermeldung beim Speichern gefunden.")
        print("--- IKC Anmeldung beendet ---")

# --- Helper function for Temodal Automation ---
def temodal_pyautogui_automatisierung(aktuelles_datum):
    """Führt die PyAutoGUI-Automatisierung für ein einzelnes Datum der Temodal-Serie aus."""
    print(f"\n--- Verarbeite Datum: {aktuelles_datum} ---")

    # --- 1. IKC Anmeldung (Niere + Leber) ---
    print("--- Starte IKC Anmeldung (Niere + Leber) ---")
    if not find_and_click_lab('button_neu.png'): sys.exit("FEHLER: button_neu.png für IKC nicht gefunden.")
    if not find_and_click_lab('button_suche.png'): sys.exit("FEHLER: button_suche.png für IKC nicht gefunden.")
    pyautogui.hotkey('ctrl', 'a'); time.sleep(0.05); pyautogui.press('backspace')
    pyautogui.typewrite('ikc blut', interval=0.01)
    if not find_and_click_lab('button_ikcblut.png', confidence=0.8): sys.exit("FEHLER: button_ikcblut.png nicht gefunden.")
    if not find_and_click_lab('button_blau_ikc.png', confidence=0.8, click_button='right'): sys.exit("FEHLER: button_blau_ikc.png nicht gefunden.")
    
    for i in range(3): pyautogui.press('tab')
    clipboard.copy(aktuelles_datum)
    pyautogui.hotkey('ctrl', 'v'); time.sleep(0.1)
    pyautogui.press('tab'); pyautogui.press('tab')
    zeit = '07:00'; clipboard.copy(zeit); pyautogui.hotkey('ctrl', 'v'); time.sleep(0.1)

    
    if not find_and_click_lab('button_nierenblock.png', retries=10):
        print("WARNUNG: Konnte Nierenblock nicht hinzufügen.")
    else:
        print("Nierenblock hinzugefügt.")
    
    if not find_and_click_lab('button_leberblock.png', retries=10):
        print("WARNUNG: Konnte Leberblock nicht hinzufügen.")
    else:
        print("Leberblock hinzugefügt.")
    
    if not find_and_click_lab('button_speichern.png', confidence=0.8): sys.exit("FEHLER: button_speichern.png nicht gefunden.")
    if find_and_click_lab('button_meldung_speichern.png', confidence=0.8, retries=10, delay_after=0.05):
        print("Fehlermeldung beim Speichern gefunden und weggeklickt.")
    print("--- IKC Anmeldung beendet ---")

    # --- 2. HAD Anmeldung (Blutbild) ---
    print("\n--- Starte HAD Anmeldung (Blutbild) ---")
    if not UNIVERSAL.labor_oeffne_hadh():
        sys.exit("FEHLER in Funktion UNIVERSAL.labor_oeffne_hadh(). Breche ab.")
    if not UNIVERSAL.laborhadh_ausfuellen(aktuelles_datum):
        sys.exit(f"FEHLER in Funktion UNIVERSAL.laborhadh_ausfuellen() für Datum {aktuelles_datum}. Breche ab.")
    
    print("Prüfe auf Fehlermeldung nach Speichern...")
    if find_and_click_lab('button_meldung_speichern.png', confidence=0.8, retries=10, delay_after=0.05):
        print("Fehlermeldung beim Speichern gefunden und weggeklickt.")
    print("--- HAD Anmeldung beendet ---")


# --- Workflow 2: Temodal Serienverordnung für Glioblastom ---
def temodal_serienverordnung_glioblastom():
    """Fragt den User nach mehreren Daten für eine Serienverordnung und startet die Automatisierung."""
    print("\n--- Starte Workflow: Temodal Serienverordnung Glioblastom ---")

    eingegebene_daten = []
    max_daten = 10
    ordinals = ["Datum #1", "Datum #2", "Datum #3", "Datum #4", "Datum #5", "Datum #6", "Datum #7", "Datum #8", "Datum #9", "Datum #10"]

    while len(eingegebene_daten) < max_daten:
        prompt = f"Bitte geben Sie das {ordinals[len(eingegebene_daten)]}  ein (Format: DD.MM.YYYY) oder '-' zum Starten des Skripts: \n"
        user_input = input(prompt).strip()

        if user_input == '-':
            print("Eingabe beendet.")
            break
        try:
            datetime.strptime(user_input, "%d.%m.%Y")
            eingegebene_daten.append(user_input)
            print(f"Datum '{user_input}' hinzugefügt.")
        except ValueError:
            print("Falsches Format oder ungültiges Datum. Bitte erneut versuchen.")

    if not eingegebene_daten:
        print("Keine Daten eingegeben. Workflow wird beendet.")
        return

    print("\n--- Zusammenfassung der eingegebenen Daten ---")
    for i, datum in enumerate(eingegebene_daten):
        print(f"Datum {i+1}: {datum}")
    
    print("\nStarte die Automatisierung der Temodal Serienverordnung...")
    UNIVERSAL.KISIM_im_vordergrund()
    if not UNIVERSAL.navigiere_bereich_kurve():
        sys.exit("FEHLER: Navigation zum Bereich Kurve fehlgeschlagen.")
    print("Bereich Kurve erreicht. Starte Serienverordnung.")

    for datum in eingegebene_daten:
        temodal_pyautogui_automatisierung(datum)
    
    print("\n--- Temodal Serienverordnung für alle Daten abgeschlossen. ---")

# --- Main execution block ---
def main():
    print("\n--- Starte lab.py Skriptausführung ---")
    try:
        while True:
            print("\nWelche Aktion möchten Sie ausführen?")
            print("1: Standard Labor Station")
            print("2: Temodal Serienverordnung Glioblastom")
            wahl = input("Ihre Wahl (1 oder 2): ").strip()

            if wahl == '1':
                standard_labor_station()
                break
            elif wahl == '2':
                temodal_serienverordnung_glioblastom()
                break
            else:
                print("Ungültige Eingabe. Bitte '1' oder '2' eingeben.")
        
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