import UNIVERSAL
import os
import sys
import time
import pyautogui
import clipboard
from datetime import datetime

# Get the absolute path of the directory containing the current script (patdata.py)
script_dir = os.path.dirname(os.path.abspath(__file__))
# Get the absolute path of the parent directory (the application root, e.g., "USZ RAO App")
app_dir = os.path.dirname(script_dir)
# Define the path to the main screenshots directory (located within the script directory)
screenshots_dir = os.path.join(script_dir, 'screenshots pyautogui')
local_screenshots_dir = os.path.join(screenshots_dir, "tumorboards")
# Define the absolute path to patdata in the user's home directory
user_home = os.path.expanduser("~")


#Definne global variables
alle_tumorboards = sorted([
    "GAS-CHI-ONK", 
    "Gastrointestinal", 
    "HCC", 
    "LLMZ", 
    "Sarkom", 
    "Schädelbasis", 
    "Thorax"
])

tumorboard_auswahl = None


tumorboard_png_mapping = {
    "GAS-CHI-ONK": "button_tumorboard_gas-chi-onk.png",
    "Gastrointestinal": "button_tumorboard_gi.png",
    "HCC": "button_tumorboard_hcc.png",
    "LLMZ": "button_tumorboard_llmz.png",
    "Sarkom": "button_tumorboard_sarkom.png",
    "Schädelbasis": "button_tumorboard_schaedelbasis.png",
    "Thorax": "button_tumorboard_thorax.png",
}

def userinput():
    print("Bitte wählen Sie ein Tumorboard aus:")
    for idx, tb in enumerate(alle_tumorboards, 1):
        print(f"{idx}: {tb}")
    while True:
        try:
            auswahl = int(input("Nummer eingeben: "))
            if 1 <= auswahl <= len(alle_tumorboards):
                global tumorboard_auswahl
                tumorboard_auswahl = alle_tumorboards[auswahl - 1]
                print(f"Ausgewählt: {tumorboard_auswahl}")
                # Set the path to the tumorboard folder
                global tb_folder
                tb_folder = os.path.join(os.path.expanduser("~"), "tumorboards", tumorboard_auswahl)
                break
            else:
                print("Ungültige Nummer. Bitte erneut versuchen.")
        except ValueError:
            print("Bitte eine gültige Zahl eingeben.")

def open_tumorboard():

    pyautogui.press('f6') #öffnet Briefkasten
    time.sleep(2)
    pyautogui.click(740, 120) #klickt auf Briefkasten
    while True:
        if UNIVERSAL.find_button(image_name="button_briefkasten_confirm.png", base_path=local_screenshots_dir, max_attempts=1, confidence=0.9): 
            print("button_briefkasten_confirm.png gefunden, break While loop.")
            break
        elif UNIVERSAL.find_and_click_button(image_name="button_briefkasten.png", base_path=local_screenshots_dir, max_attempts=1, confidence=0.9): 
            print("button_briefkasten.png gefunden und geklickt, break While loop.")
            break
        else:
            print("Fehler: button_briefkasten.png und button_briefkasten_confirm.png nicht gefunden, loope weiter.")
            time.sleep(0.1)
            continue

    if not UNIVERSAL.find_and_click_button(image_name="button_suchleiste.png", base_path=local_screenshots_dir): print("Fehler: Konnte x-Suchleiste-Button nicht klicken."); sys.exit()
    tumor = "tumor"
    clipboard.copy(tumor)
    pyautogui.hotkey('ctrl', 'v') #fügt den Text "tumor" ein

    tumorboard_png = tumorboard_png_mapping.get(tumorboard_auswahl)
    print(f"tumorboard_png: {tumorboard_png}")
    if tumorboard_png is None:
        print(f"Fehler: Tumorboard {tumorboard_auswahl} nicht gefunden.")
        sys.exit(1)
    if not UNIVERSAL.find_and_click_button(image_name=tumorboard_png, base_path=local_screenshots_dir, confidence=0.95): print("Fehler: Konnte spez. Tumorboard-Button nicht klicken."); sys.exit()

    time.sleep(2)

    if UNIVERSAL.find_button("button_keine_patienten.png", base_path=local_screenshots_dir, confidence=0.95, interval=0.1, max_attempts=10): 
        print("ACHTUNG: Zum aktuellen Zeitpunkt keine Patienten für das ausgewählte Tumorboard angemeldet! Breche ab.")
        # Erstelle eine .txt-Datei im tumorboard-Ordner mit aktuellem Datum und Hinweis
        
        os.makedirs(tb_folder, exist_ok=True)
        date_str = datetime.now().strftime("%d.%m.%Y")
        file_path = os.path.join(tb_folder, f"{date_str}_KEINE_PATIENTEN.txt")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(f"Aktuell sind keine Patienten für das Tumorboard {tumorboard_auswahl} angemeldet.\n")
        return

    if not UNIVERSAL.find_and_click_button("button_freier_bereich.png", base_path=local_screenshots_dir, confidence=0.95): print("Fehler: freier_bereich_Button nicht gefunden."); sys.exit()
    time.sleep(3)
    pyautogui.hotkey('ctrl', 'a') #wählt alles aus
    time.sleep(2)

def tumorboard_nach_nachname_sortieren():
    #Sortierung festlegen
    location_grauer_bereich = pyautogui.locateOnScreen(os.path.join(local_screenshots_dir, "button_grauer_bereich.png"), confidence=0.8)
    if location_grauer_bereich is not None:
        x, y = pyautogui.center(location_grauer_bereich)
        pyautogui.rightClick(x, y) #klickt auf grauer Bereich
    else:
        print("Fehler: Grauer Bereich nicht gefunden.")
        return False
    
    time.sleep(1)
    for _ in range(5):
        pyautogui.press('down') #Auf Option sortieren klicken
    pyautogui.press('enter') #Bestätigen

    UNIVERSAL.ctrl_tabs(2) #Wechselt in den Tab "Spalte 1"
    pyautogui.press('enter') #Bestätigen
    pyautogui.typewrite("pat") #pat schreiben
    time.sleep(0.5)
    pyautogui.press('enter') #wählt Patienten aus
    time.sleep(0.5)

    UNIVERSAL.ctrl_tabs(1)
    pyautogui.press('enter') #wählt Art der Sortierung aus
    pyautogui.typewrite("auf") #auf schreiben
    pyautogui.press('enter') #wählt aufsteigend aus
    time.sleep(0.5)
    if not UNIVERSAL.find_and_click_button("button_sortierung_ok.png", base_path=local_screenshots_dir, confidence=0.95): print("Fehler: Konnte Button_sortierung_ok.png nicht klicken."); sys.exit()


def als_pdf_speichern():
    location_grauer_bereich = pyautogui.locateOnScreen(os.path.join(local_screenshots_dir, "button_grauer_bereich.png"), confidence=0.8)
    if location_grauer_bereich is not None:
        x, y = pyautogui.center(location_grauer_bereich)
        pyautogui.rightClick(x, y) #klickt auf grauer Bereich
    else:
        print("Fehler: Grauer Bereich nicht gefunden.")
        return False
    
    time.sleep(1)
    for _ in range(2):
        pyautogui.press('down') 
    pyautogui.press('enter') #Ausgewählte Aufträge drucken
    time.sleep(2)

    if not UNIVERSAL.find_and_click_button_offset("button_drucker.png", base_path=local_screenshots_dir, confidence=0.95, x_offset=170): print("Fehler: Konnte button_drucker.png nicht klicken."); sys.exit()
    time.sleep(2)
    if not UNIVERSAL.find_and_click_button_offset("button_name.png", base_path=local_screenshots_dir, confidence=0.95, x_offset=150): print("Fehler: Konnte button_name.png nicht klicken."); sys.exit()
    if not UNIVERSAL.find_and_click_button("button_microsoft_print_to_pdf.png", base_path=local_screenshots_dir, confidence=0.95): print("Fehler: Konnte button_microsoft_print_to_pdf.png nicht klicken."); sys.exit()
    time.sleep(2)
    pyautogui.press('enter') #Bestätigen
    time.sleep(2)
    pyautogui.press('enter') #Bestätigen

    # PDF-Speichern-Loop für alle Tumorboard-Anmeldungen
    nummer = 1
    while UNIVERSAL.find_and_click_button(
        "button_dateiname.png",
        base_path=local_screenshots_dir,
        confidence=0.90,
        max_attempts=50,
        interval=0.1
    ):
        pyautogui.typewrite(str(nummer))
        time.sleep(0.1)
        pyautogui.press("enter")
        nummer += 1
    print("Alle Tumorboard-Anmeldung erfolgreich als PDFs einzeln exportiert")






def main():
    # Check if the script is running in the correct environment
    if not os.path.exists(user_home):
        print("Fehler: Benutzerverzeichnis nicht gefunden.")
        sys.exit(1)

    # Create the screenshots directory if it doesn't exist
    if not os.path.exists(local_screenshots_dir):
        os.makedirs(local_screenshots_dir)

    # Get user input for tumorboard selection
    userinput()

    #Check, dass KISIM im Vordergrund ist
    if not UNIVERSAL.KISIM_im_vordergrund():
        print("Fehler: KISIM ist nicht im Vordergrund.")
        sys.exit(1)

    
    open_tumorboard()
    tumorboard_nach_nachname_sortieren()
    als_pdf_speichern()


if __name__ == "__main__":
    main()


