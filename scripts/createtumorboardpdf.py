import UNIVERSAL
import os
import sys
import time
import pyautogui
import clipboard
from datetime import datetime
import shutil
import re
import openpyxl
from openpyxl import load_workbook


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
alle_tumorboards = [
    "GAS-CHI-ONK",
    "GIT",
    "Gyn",
    "HCC",
    "HPB",
    "Hämato-Onkologie/Lymphome",
    "Hyperthermie",
    "LLMZ",
    "Melanome",
    "Neuro-Onkologie",
    "NET",
    "ORL",
    "Paragangliome",
    "Pädiatrie",
    "Protonentherapie",
    "Sarkom",
    "Schädelbasis",
    "Schilddrüse",
    "Thorax",
    "Transplantationsboard",
    "Uro",
    "Vascular",
    "ZKGS"
]

tumorboard_auswahl = None


tumorboard_png_mapping = {
    "GAS-CHI-ONK": "button_tumorboard_gas-chi-onk.png",
    "GIT": "button_tumorboard_gi.png",
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

    if not UNIVERSAL.find_and_click_button_offset(image_name="button_erledigt_am.png", base_path=local_screenshots_dir, y_offset=30): print("Fehler: freier_bereich_Button nicht gefunden."); sys.exit()
    time.sleep(2)
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


    time.sleep(2)
    if not UNIVERSAL.find_and_click_button("button_ja_rot.png", base_path=local_screenshots_dir, confidence=0.90, max_attempts=5): print("button_ja_rot.png wurde nicht gefunden, fahre fort.")
    
    # PDF-Speichern-Loop für alle Tumorboard-Anmeldungen
    #Export dir definieren
    if not UNIVERSAL.find_and_click_button("button_export_zeile.png", base_path=local_screenshots_dir, confidence=0.90): print("Fehler: Konnte button_export_zeile.png nicht klicken."); sys.exit()
    clipboard.copy(tb_folder)
    pyautogui.hotkey('ctrl', 'v') #fügt den Text "Export" ein
    pyautogui.press('enter') #Bestätigen
    time.sleep(0.5)

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

    # Erstelle einen neuen Ordner mit aktuellem Datum im tb_folder
    date_str = datetime.now().strftime("%d.%m.%Y")
    global dated_folder
    dated_folder = os.path.join(tb_folder, date_str)
    if os.path.exists(dated_folder):
        # Lösche alle Inhalte im Ordner
        for filename in os.listdir(dated_folder):
            file_path = os.path.join(dated_folder, filename)
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
    else:
        os.makedirs(dated_folder, exist_ok=True)

    # Verschiebe alle PDFs mit nur Zahlen im Namen in den neuen Ordner
    for filename in os.listdir(tb_folder):
        if filename.lower().endswith(".pdf") and re.fullmatch(r"\d+\.pdf", filename):
            src = os.path.join(tb_folder, filename)
            dst = os.path.join(dated_folder, filename)
            shutil.move(src, dst)
    print(f"Alle exportierten PDFs wurden nach {dated_folder} verschoben.")



def pdfs_umbenennen(dated_folder):
    import fitz  # PyMuPDF

    # Regex für 5-10-stellige Zahl
    patient_num_re = re.compile(r"\b\d{5,10}\b")

    for filename in os.listdir(dated_folder):
        if filename.lower().endswith(".pdf") and re.fullmatch(r"\d+\.pdf", filename):
            pdf_path = os.path.join(dated_folder, filename)
            try:
                with fitz.open(pdf_path) as doc:
                    text = ""
                    for page in doc:
                        text += page.get_text()
                # Suche nach "Patienteninformationen" und dann nach erster 5-10-stelliger Zahl danach
                idx = text.find("Patienteninformationen")
                patientennummer = None
                if idx != -1:
                    # Nur Text nach "Patienteninformationen" durchsuchen
                    after = text[idx:]
                    match = patient_num_re.search(after)
                    if match:
                        patientennummer = match.group()
                if patientennummer:
                    new_filename = f"{os.path.splitext(filename)[0]} - {patientennummer}.pdf"
                    new_path = os.path.join(dated_folder, new_filename)
                    os.rename(pdf_path, new_path)
                    print(f"{filename} umbenannt in {new_filename}")
                else:
                    print(f"Keine Patientennummer in {filename} gefunden.")
            except Exception as e:
                print(f"Fehler beim Auslesen von {filename}: {e}")

def create_excel_file():
    import fitz  # PyMuPDF

    # Regex patterns
    patient_num_re = re.compile(r"\b\d{5,10}\b")
    geschlecht_geb_re = re.compile(r"\b([MW])\s*/\s*(\d{2}\.\d{2}\.\d{4})")

    # Collect data for each PDF
    patient_data = []

    # Sortiere Dateien numerisch. Funktioniert für "1 - 12345.pdf"
    pdf_files = sorted(
        [f for f in os.listdir(dated_folder) if f.lower().endswith(".pdf") and re.fullmatch(r"\d+\s-\s\d+\.pdf", f)],
        key=lambda x: int(re.match(r"(\d+)", x).group(1))
    )
    if not pdf_files:
        print("Keine passend benannten PDF-Dateien für die Excel-Erstellung gefunden.")
        return

    for filename in pdf_files:
        pdf_path = os.path.join(dated_folder, filename)
        try:
            with fitz.open(pdf_path) as doc:
                text = ""
                for page in doc:
                    text += page.get_text()
            
            # Extrahiere Daten
            patientennummer = name = geschlecht = geburtsdatum = diagnose = ""
            
            # Suche nach "Patienteninformationen"
            idx_info = text.find("Patienteninformationen")
            if idx_info != -1:
                after_info = text[idx_info + len("Patienteninformationen"):].lstrip()
                # Patientennummer
                match_num = patient_num_re.search(after_info)
                if match_num:
                    patientennummer = match_num.group()
                    # Name: Zeile direkt unter Patientennummer
                    lines = after_info[match_num.end():].lstrip().splitlines()
                    if lines:
                        name = lines[0].strip()
                # Geschlecht und Geburtsdatum
                match_geschlecht = geschlecht_geb_re.search(after_info)
                if match_geschlecht:
                    geschlecht = match_geschlecht.group(1)
                    geburtsdatum = match_geschlecht.group(2)

            # Diagnose extrahieren
            idx_diag = text.lower().find("diagnose")
            if idx_diag != -1:
                diag_after = text[idx_diag + len("diagnose"):].lstrip()
                diag_lines = diag_after.splitlines()
                for line in diag_lines:
                    line = line.strip()
                    if line:
                        diagnose = line
                        break
            
            patient_data.append([patientennummer, name, geschlecht, geburtsdatum, diagnose])
        except Exception as e:
            print(f"Fehler beim Auslesen von {filename}: {e}")
            patient_data.append(["", "", "", "", ""])

    # Excel-Template kopieren
    template_path = os.path.join(user_home, "tumorboards", "__SQLite_database", "template.xlsx")
    if not os.path.exists(template_path):
        print(f"Excel-Template nicht gefunden: {template_path}")
        return
    excel_dst = os.path.join(dated_folder, "template.xlsx")
    shutil.copy(template_path, excel_dst)

    # Excel ausfüllen
    wb = load_workbook(excel_dst)
    ws = wb.active
    for idx, (patnum, name, geschlecht, geburtsdatum, diagnose) in enumerate(patient_data, start=2):
        ws[f"B{idx}"] = patnum
        ws[f"C{idx}"] = name
        ws[f"D{idx}"] = geschlecht
        ws[f"E{idx}"] = geburtsdatum
        ws[f"F{idx}"] = diagnose

    # === NEUER TEIL: FINALE PDF-UMBENENNUNG UND EXCEL-ANPASSUNG ===

    # Zweite Umbenennung der PDFs basierend auf den extrahierten Namen
    print("\nBenenne PDFs final um (Nachname - Patientennummer.pdf)...")
    for i, filename in enumerate(pdf_files):
        if i < len(patient_data):
            patnum, name, _, _, _ = patient_data[i]
            
            # Extrahiere Nachname (das erste Wort des Namens)
            nachname = "Unbekannt"
            if name and name.strip():
                # Nimmt das erste Wort (vor Komma oder Leerzeichen)
                nachname = name.strip().split(',')[0].strip().split()[0]

            if patnum and nachname != "Unbekannt":
                old_path = os.path.join(dated_folder, filename)
                new_filename = f"{nachname} - {patnum}.pdf"
                new_path = os.path.join(dated_folder, new_filename)
                
                if os.path.exists(old_path):
                    try:
                        os.rename(old_path, new_path)
                        print(f"'{filename}' umbenannt in '{new_filename}'")
                    except Exception as e:
                        print(f"Fehler beim Umbenennen von '{filename}' zu '{new_filename}': {e}")
                else:
                    print(f"Warnung: Quelldatei für Umbenennung nicht gefunden: {old_path}")
            else:
                print(f"Warnung: Kein Name oder Patientennummer für '{filename}', Umbenennung wird übersprungen.")

    # Spalte A in der Excel-Datei löschen
    print("\nLösche Spalte A in der Excel-Datei...")
    ws.delete_cols(1)  # Löscht die erste Spalte (Spalte A)

    # === ENDE NEUER TEIL ===

    # Excel-Datei speichern und umbenennen
    date_str = datetime.now().strftime("%d.%m.%Y")
    excel_final = os.path.join(dated_folder, f"{date_str}.xlsx")
    wb.save(excel_final)
    print(f"\nExcel-Datei gespeichert als {excel_final}")

    # Template-Datei im Zielordner löschen
    try:
        os.remove(excel_dst)
        print(f"Template-Datei {excel_dst} wurde gelöscht.")
    except Exception as e:
        print(f"Fehler beim Löschen der Template-Datei: {e}")


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
    # Nach dem Verschieben der PDFs aufrufen:
    pdfs_umbenennen(dated_folder)
    create_excel_file()
    print("\nProzess abgeschlossen. PDFs wurden final umbenannt und die Excel-Liste wurde erstellt.")


if __name__ == "__main__":
    main()