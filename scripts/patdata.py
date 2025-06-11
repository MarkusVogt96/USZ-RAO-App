# -*- coding: utf-8 -*-
import UNIVERSAL
import sys
import os
import time
import datetime
from datetime import timedelta
import re
import json
import pyautogui
import clipboard
import traceback
import logging 
import importlib 

# NEU: Import aus entities
try:
    # Importiere die spezifischen Funktionen und Dictionaries
    from entities import (
        find_matching_entity, get_icd_code, entity_dictionary_icd,
        secondary_neoplasms_icd, manuelle_entity_auswahl,
        manuelle_sekundaer_auswahl
    )
    print("Funktionen und Dictionaries aus entities.py erfolgreich importiert.")
except ImportError as e:
    print(f"FEHLER: Konnte entities.py nicht importieren: {e}")
    # Beende das Skript, wenn die Abhängigkeit fehlt
    sys.exit("Abbruch: entities.py fehlt oder enthält Fehler.")


# --- Define Relative Paths ---
# Get the absolute path of the directory containing the current script (patdata.py)
script_dir = os.path.dirname(os.path.abspath(__file__))
# Get the absolute path of the parent directory (the application root, e.g., "USZ RAO App")
app_dir = os.path.dirname(script_dir)
# Define the path to the main screenshots directory (located within the script directory)
screenshots_dir = os.path.join(script_dir, 'screenshots pyautogui') # KORREKT: Geht vom script_dir aus
# Define the absolute path to patdata in the user's home directory
user_home = os.path.expanduser("~")
patdata_dir = os.path.join(user_home, "patdata")

# Keep these prints for user feedback on paths
print(f"Script directory (patdata.py location): {script_dir}")
print(f"App directory: {app_dir}")
print(f"Patient data directory: {patdata_dir}")
print(f"Screenshots directory: {screenshots_dir}")

# --- End Relative Path Definitions ---

# --- Globale Variablen auf Modulebene ---
# Initialisierung der neuen globalen Variablen
tumor = None
entity = None
icd_code = None
secondary_entity = None      # NEU
secondary_icd_code = None  # NEU

# Bestehende globale Variablen (werden in main() oder anderen Funktionen gesetzt)
oberarzt = None
simultane_chemotherapie = None
chemotherapeutikum = ""
therapieintention = None
fraktionen_woche = None
behandlungskonzept_serie1 = None
behandlungskonzept_serie2 = None
behandlungskonzept_serie3 = None
behandlungskonzept_serie4 = None
datum_erste_rt = None
datum_letzte_rt = None
full_text = ""
ecog = None
zimmer = None
aufnahmegrund = None
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


####Standard Beginn fertig
##########################
###define functions

# --- Funktionen (screenshot_rtkonzept, etc.) ---
# (Funktionen screenshot_rtkonzept, easyocr_screenshot_rtkonzept, oberarzt_aus_ocr_auslesen, simultane_chemotherapie_aus_ocr_auslesen
# bleiben unverändert, da sie nicht direkt von den neuen Änderungen betroffen sind)

def screenshot_rtkonzept():
    print("Versuche Screenshot vom RT Konzept...")
    try:
        ausschnitt_rtkonzept = (630, 200, 665, 300)
        screenshot_rtkonzept = pyautogui.screenshot(region=ausschnitt_rtkonzept)
        screenshot_rtkonzept_preprocessed = UNIVERSAL.PIL_image_preprocessing_Zoom_Contrast_Sharpen(screenshot_rtkonzept)
        save_dir = os.path.join(screenshots_dir, 'UNIVERSAL', 'image_preprocessing')
        save_path = os.path.join(save_dir, 'screenshot_rtkonzept_original_from_patdata.png')
        os.makedirs(save_dir, exist_ok=True)
        screenshot_rtkonzept.save(save_path)
        print(f"Original Screenshot gespeichert unter {save_path}")
        print("(Vorverarbeiteter Screenshot wird von UNIVERSAL-Funktion gespeichert)")
        return True
    except Exception as e:
        print(f"Fehler beim Erstellen/Speichern des Screenshots: {e}")
        logging.error(f"screenshot_rtkonzept: Error during screenshot creation/saving: {e}", exc_info=True)
        traceback.print_exc()
        return False

def easyocr_screenshot_rtkonzept():

    global full_text
    full_text = ""
    screenshot_path = os.path.join(screenshots_dir, 'UNIVERSAL', 'image_preprocessing', 'image_preprocessed_from_function_PIL_image_preprocessing_Zoom_Contrast_Sharpen().png')
    if not os.path.exists(screenshot_path):
        print(f"Vorverarbeitete Screenshot-Datei nicht gefunden: {screenshot_path}")
        logging.error(f"easyocr_screenshot_rtkonzept: Preprocessed screenshot not found at {screenshot_path}")
        return False
    print("Führe EasyOCR für RT Konzept durch...")
    try:
        results_easyocr = UNIVERSAL.ocr_mit_easyocr(screenshot_path)
        if results_easyocr:
            full_text = "\n".join(results_easyocr)
            print("EasyOCR erfolgreich, erkannter Text:")
            print(full_text)
            return True
        elif results_easyocr is None:
             print("EasyOCR ist fehlgeschlagen (Rückgabewert None).")
             logging.warning("easyocr_screenshot_rtkonzept: UNIVERSAL.ocr_mit_easyocr returned None (indicating failure).")
             return False
        else: # results_easyocr is an empty list []
             print("EasyOCR hat keinen Text erkannt.")
             full_text = ""
             return True
    except Exception as e:
        print(f"Fehler während EasyOCR: {e}")
        logging.error(f"easyocr_screenshot_rtkonzept: Exception during OCR call: {e}", exc_info=True)
        traceback.print_exc()
        return False

def oberarzt_aus_ocr_auslesen(): # Benötigt kein UNIVERSAL
    global oberarzt
    oberarzt = None
    if not full_text:
        logging.warning("oberarzt_aus_ocr_auslesen: OCR text (full_text) is empty, cannot extract Oberarzt.")
        print("WARNUNG: Kein OCR-Text vorhanden, Oberarzt kann nicht ausgelesen werden.")
        return
    print("Versuche Oberarzt aus OCR-Text auszulesen...")
    try:
        pattern_oa = r"Zust\. OA:\s*((?:(?!RT-Nummer|RT-Konzept).)*?)\s*(?:RT-Nummer|RT-Konzept)"
        match_oberarzt = re.search(pattern_oa, full_text, re.IGNORECASE | re.DOTALL)
        if match_oberarzt:
            segment = match_oberarzt.group(1).strip()
            words = segment.split()
            if words:
                oberarzt = words[-1]
                if oberarzt == 'Badra':
                    oberarzt = 'Vlaskou'
                print(f"Letztes Wort extrahiert als Oberarzt: '{oberarzt}'")
            else:
                oberarzt = "LEERES_SEGMENT"
                logging.warning("oberarzt_aus_ocr_auslesen: Matched segment was empty after split.")
                print("WARNUNG: Segment für Oberarzt gefunden, aber leer.")
        else:
            print("Kein Text für Oberarzt via OCR gefunden.")
    except Exception as e:
        print(f"Fehler beim Auslesen des Oberarztes aus OCR: {e}")
        logging.error(f"oberarzt_aus_ocr_auslesen: Exception during extraction: {e}", exc_info=True)
        traceback.print_exc()
        oberarzt = "FEHLER_BEI_VERARBEITUNG"

def simultane_chemotherapie_aus_ocr_auslesen(): # Benötigt kein UNIVERSAL (nur pyautogui)
    global simultane_chemotherapie
    simultane_chemotherapie = "nicht bestimmt"
    bereich_berichte_path = os.path.join(screenshots_dir, 'UNIVERSAL', 'bereich_berichte')
    ja_button_path = os.path.join(bereich_berichte_path, 'button_rtkonzept_chemotherapie_ja.png')
    nein_button_path = os.path.join(bereich_berichte_path, 'button_rtkonzept_chemotherapie_nein.png')
    print("Suche nach Bild für simultane Chemotherapie 'ja'...")
    try:
        if pyautogui.locateOnScreen(ja_button_path, confidence=0.99):
            simultane_chemotherapie = "ja"
            print(f'Simultane Chemotherapie: JA (Bild gefunden: {ja_button_path})')
            logging.info(f"simultane_chemotherapie_aus_ocr_auslesen: Found 'ja' button. Status set to 'ja'.")
            return
    except pyautogui.ImageNotFoundException:
        print(f'Button für Chemo "ja" nicht gefunden.')
    except Exception as e:
        print(f"Fehler bei der Suche nach Chemo 'ja' Button: {e}")
        logging.error(f"simultane_chemotherapie_aus_ocr_auslesen: Error searching for 'ja' button: {e}", exc_info=True)

    if simultane_chemotherapie != "ja":
        print("Suche nach Bild für simultane Chemotherapie 'nein'...")
        try:
            if pyautogui.locateOnScreen(nein_button_path, confidence=0.99):
                simultane_chemotherapie = "nein"
                print(f'Simultane Chemotherapie: NEIN (Bild gefunden: {nein_button_path})')
                logging.info(f"simultane_chemotherapie_aus_ocr_auslesen: Found 'nein' button. Status set to 'nein'.")
            else:
                 print('Button für Chemo "nein" nicht gefunden.')
                 logging.warning("simultane_chemotherapie_aus_ocr_auslesen: Neither 'ja' nor 'nein' button found. Status remains 'nicht bestimmt'.")
        except pyautogui.ImageNotFoundException:
            print(f'Button für Chemo "nein" nicht gefunden.')
            logging.warning("simultane_chemotherapie_aus_ocr_auslesen: Neither 'ja' nor 'nein' button found (nein failed). Status remains 'nicht bestimmt'.")
        except Exception as e:
            print(f"Fehler bei der Suche nach Chemo 'nein' Button: {e}")
            logging.error(f"simultane_chemotherapie_aus_ocr_auslesen: Error searching for 'nein' button: {e}", exc_info=True)

    print(f"Status simultane Chemotherapie nach Bildsuche: {simultane_chemotherapie}")
    logging.info(f"simultane_chemotherapie_aus_ocr_auslesen: Final chemo status: {simultane_chemotherapie}")

def therapieintention_auslesen():
    #Versuch, Therapieintention und Fraktionen/Woche auszulesen
    local_path_bereich_berichte = os.path.join(screenshots_dir, 'UNIVERSAL', 'bereich_berichte')
    for x in range(5):
        suche_ziel = False
        if not UNIVERSAL.find_button(image_name="button_ziel.png", base_path=local_path_bereich_berichte, max_attempts=5):
            print("button_ziel.png nicht gefunden, mache page down")
            pyautogui.press('pagedown')
        else:
            print("button_ziel.png  gefunden, lese aus")
            suche_ziel = True
        if suche_ziel is True:
            break

    # Definition der Größe des Screenshot-Bereichs (Breite und Höhe)
    # Dieser Bereich beginnt am berechneten Startpunkt
    screenshot_region_width = 200
    screenshot_region_height = 15

    print(f"Suche nach 'button_ziel.png' auf dem Bildschirm...")
    button_ziel_path = os.path.join(screenshots_dir, 'UNIVERSAL', 'bereich_berichte', 'button_ziel.png')

    # Versuche, das Bild auf dem Bildschirm zu finden
    # locateOnScreen gibt ein 'Box'-Objekt zurück (links, oben, breite, höhe) oder None, wenn nicht gefunden
    # Die confidence hilft, falls das Bild nicht exakt übereinstimmt (z.B. durch Skalierung, leichte Unterschiede)
    try:
        location = pyautogui.locateOnScreen(button_ziel_path, confidence=0.8)
    except FileNotFoundError:
        print(f"Fehler: Die Bilddatei '{button_ziel_path}' wurde nicht gefunden.")
        location = None # Stelle sicher, dass location None ist, wenn die Datei fehlt
    except Exception as e:
        print(f"Ein unerwarteter Fehler bei der Bildsuche ist aufgetreten: {e}")
        location = None


    # Überprüfe, ob das Bild gefunden wurde
    if location is not None:
        print(f"Bild gefunden bei: {location}")

        # Extrahiere die Koordinaten und Dimensionen des gefundenen Bildes
        left, top, width, height = location

        # Berechne die Koordinaten der oberen rechten Ecke des gefundenen Bildes
        screenshot_left = left + width
        screenshot_top = top

        # Definiere den Screenshot-Bereich als Tupel (links, oben, breite, höhe)
        # Die Breite und Höhe sind feste Werte aus der Konfiguration
        screenshot_region = (int(screenshot_left), int(screenshot_top), int(screenshot_region_width), int(screenshot_region_height))

        print(f"Berechneter Screenshot-Bereich (links, oben, breite, höhe): {screenshot_region}")

        # Nimm den Screenshot des definierten Bereichs auf
        screenshot_rtkonzept_intention = pyautogui.screenshot(region=screenshot_region)
        save_path = os.path.join(screenshots_dir, 'UNIVERSAL', 'image_preprocessing', 'screenshot_rtkonzept_intention.png')
        # Speichere den Screenshot
        screenshot_rtkonzept_intention.save(save_path)

        print(f"Screenshot erfolgreich gespeichert als {save_path}")

        screenshot_rtkonzept_intention_preprocessed = UNIVERSAL.PIL_image_preprocessing_Zoom_Contrast_Sharpen(screenshot_rtkonzept_intention)
        screenshot_rtkonzept_intention_preprocessed_path = os.path.join(screenshots_dir, 'UNIVERSAL', 'image_preprocessing', 'image_preprocessed_from_function_PIL_image_preprocessing_Zoom_Contrast_Sharpen().png')
        ocr_aus_screenshot_rtkonzept_intention = UNIVERSAL.ocr_mit_easyocr(screenshot_rtkonzept_intention_preprocessed_path)
        print(f"OCR aus Intention-Scrrenshot: {ocr_aus_screenshot_rtkonzept_intention}")

        #Bestimmen der Intention
        search_text = str(ocr_aus_screenshot_rtkonzept_intention).lower()

        # Initialisiere die Ergebnisvariable mit einem Standardwert
        intention_lokal = ""

        # Prüfe in der gewünschten Reihenfolge (Kurativ > Palliativ > Lokal) und setze die Variable
        if "kurativ" in search_text:
            print("kurativ in OCR Ergebnis gefunden. Gebe kurativ als Definition für therapieintention-Variable zurück...")
            intention_lokal = "kurativ"
            return intention_lokal
        elif "palliativ" in search_text:
            intention_lokal = "palliativ"
            print("palliativ in OCR Ergebnis gefunden. Gebe palliativ als Definition für therapieintention-Variable zurück...")
            return intention_lokal
        elif "lokal" in search_text:
            intention_lokal = "lokalablativ"
            print("lokalablativ in OCR Ergebnis gefunden. Gebe lokalablativ als Definition für therapieintention-Variable zurück...")
            return intention_lokal

        else:
            print("weder kurativ, noch palliativ, noch lokalablativ in OCR gefunden, gebe leeren String zurück. Ggf manuell anpassen!")
            return intention_lokal
    else:
        print("location button_ziel.png konnte nicht zurückgegeben werden. return empty string")
        return ""
    
        

def fraktionen_woche_auslesen():
    #Versuch, Therapieintention und Fraktionen/Woche auszulesen
    local_path_bereich_berichte = os.path.join(screenshots_dir, 'UNIVERSAL', 'bereich_berichte')
    for x in range(3):
        suche_ziel = False
        if not UNIVERSAL.find_button(image_name="button_fraktionen_woche.png", base_path=local_path_bereich_berichte, max_attempts=5):
            print("button_fraktionen_woche.png nicht gefunden, mache page down")
            pyautogui.press('pagedown')
        else:
            print("button_fraktionen_woche.png  gefunden, lese aus")
            suche_ziel = True
        if suche_ziel is True:
            break

    # Definition der Größe des Screenshot-Bereichs (Breite und Höhe)
    # Dieser Bereich beginnt am berechneten Startpunkt
    screenshot_region_width = 200
    screenshot_region_height = 15

    print(f"Suche nach 'button_fraktionen_woche.png' auf dem Bildschirm...")
    button_fraktionen_woche_path = os.path.join(screenshots_dir, 'UNIVERSAL', 'bereich_berichte', 'button_fraktionen_woche.png')

    # Versuche, das Bild auf dem Bildschirm zu finden
    # locateOnScreen gibt ein 'Box'-Objekt zurück (links, oben, breite, höhe) oder None, wenn nicht gefunden
    # Die confidence hilft, falls das Bild nicht exakt übereinstimmt (z.B. durch Skalierung, leichte Unterschiede)
    try:
        location = pyautogui.locateOnScreen(button_fraktionen_woche_path, confidence=0.8)
    except FileNotFoundError:
        print(f"Fehler: Die Bilddatei '{button_fraktionen_woche_path}' wurde nicht gefunden.")
        location = None # Stelle sicher, dass location None ist, wenn die Datei fehlt
    except Exception as e:
        print(f"Ein unerwarteter Fehler bei der Bildsuche ist aufgetreten: {e}")
        location = None


    # Überprüfe, ob das Bild gefunden wurde
    if location is not None:
        print(f"Bild gefunden bei: {location}")

        # Extrahiere die Koordinaten und Dimensionen des gefundenen Bildes
        left, top, width, height = location

        # Berechne die Koordinaten der oberen rechten Ecke des gefundenen Bildes
        screenshot_left = left + width
        screenshot_top = top

        # Definiere den Screenshot-Bereich als Tupel (links, oben, breite, höhe)
        # Die Breite und Höhe sind feste Werte aus der Konfiguration
        screenshot_region = (int(screenshot_left), int(screenshot_top), int(screenshot_region_width), int(screenshot_region_height))

        print(f"Berechneter Screenshot-Bereich (links, oben, breite, höhe): {screenshot_region}")

        # Nimm den Screenshot des definierten Bereichs auf
        screenshot_fraktionen_woche = pyautogui.screenshot(region=screenshot_region)
        save_path = os.path.join(screenshots_dir, 'UNIVERSAL', 'image_preprocessing', 'button_fraktionen_woche.png')
        # Speichere den Screenshot
        screenshot_fraktionen_woche.save(save_path)

        print(f"Screenshot erfolgreich gespeichert als {save_path}")

        screenshot_fraktionen_woche_preprocessed = UNIVERSAL.PIL_image_preprocessing_Zoom_Contrast_Sharpen(screenshot_fraktionen_woche)
        screenshot_fraktionen_woche_preprocessed_path = os.path.join(screenshots_dir, 'UNIVERSAL', 'image_preprocessing', 'image_preprocessed_from_function_PIL_image_preprocessing_Zoom_Contrast_Sharpen().png')
        ocr_aus_screenshot_fraktionen_woche = UNIVERSAL.ocr_mit_easyocr(screenshot_fraktionen_woche_preprocessed_path)
        print(f"OCR aus Intention-Scrrenshot: {ocr_aus_screenshot_fraktionen_woche}")

        #Bestimmen der Intention
        search_text = str(ocr_aus_screenshot_fraktionen_woche)

        fraktionen_mapping = {
            "1x pro Woche": ["1x pro", "ix pro"],
            "3x pro Woche": ["3x pro", "30 pro"],
            "4x pro Woche": ["4x pro", "40 pro"],
            "5x pro Woche inkl. Feiertag": ["erta", "Feier", "inkl"],
            "5x pro Woche": ["5x pro", "50 pro"],
            "6x pro Woche": ["6x pro", "60 pro"],
            "jeden 2. Tag": ["eden 2", "2. Tag"],
            "2x pro Tag": ["x pro", "pro Ta"]
        }

        search_text = str(ocr_aus_screenshot_fraktionen_woche).lower()
        fraktionen_woche_lokal = ""

        # Durchsuche den Text nach den definierten Mustern
        for standard_format, search_patterns in fraktionen_mapping.items():
            if any(pattern in search_text for pattern in search_patterns):
                fraktionen_woche_lokal = standard_format
                print(f"Valide OCR-Angabe gefunden, standardisiert zu: {fraktionen_woche_lokal}")
                return fraktionen_woche_lokal
        else:
            print("Kein sinnvolles Ergebnis vom OCR des Bildes gefunden. Ggf manuell anpassen!")
            return fraktionen_woche_lokal
    
    else:
        print("location fraktionen_woche.png konnte nicht zurückgegeben werden. return empty string")
        return ""



# --- Export Function (uses relative patdata_dir and UNIVERSAL functions) ---
def export_patdata_to_json_and_excel(patdata):
    global entity, icd_code, secondary_entity, secondary_icd_code, tumor # Zugriff auf globale Variablen für Korrektur

    logging.info("export_patdata_to_json_and_excel: Starting export process.")
    export_dir = patdata_dir
    os.makedirs(export_dir, exist_ok=True)
    # Aktualisierte Reihenfolge der Schlüssel
    expected_keys_order = [
        "nachname", "vorname", "geburtsdatum", "alter", "geschlecht", "patientennummer",
        "eintrittsdatum", "spi", "rea", "ips",
        "tumor", "entity", "icd_code",                     
        "secondary_entity", "secondary_icd_code",          
        "oberarzt", "simultane_chemotherapie", "chemotherapeutikum", "therapieintention",
        "fraktionen_woche", "behandlungskonzept_serie1", "behandlungskonzept_serie2",
        "behandlungskonzept_serie3", "behandlungskonzept_serie4", "datum_erste_rt",
        "datum_letzte_rt", "ecog", "zimmer", "aufnahmegrund" 
    ]

    # Stelle sicher, dass alle erwarteten Keys im patdata dict sind (aus globalen Variablen holen)
    for key in expected_keys_order:
        if key not in patdata:
             global_value = globals().get(key)
             patdata[key] = global_value

    print("\nAktuelle Patientendaten (Reihenfolge wie in Excel):")
    key_to_index_map = {} # Für Mapping von Key zu Index
    for i, key in enumerate(expected_keys_order, start=1):
        display_value = patdata.get(key, "")
        if isinstance(display_value, (datetime.date, datetime.datetime)): display_value = display_value.strftime("%d.%m.%Y")
        # Bei None explizit "Nicht gesetzt" anzeigen für Klarheit
        if display_value is None or display_value == "": display_value = ""
        print(f"[{i:2}] {key:<28}: {display_value}")
        key_to_index_map[key] = i # Speichere Key -> Index Mapping

    # --- JSON Export ---
    pat_nr = str(patdata.get("patientennummer", "unbekannt"))
    json_filename = os.path.join(export_dir, f"{pat_nr}.json")
    logging.info(f"export_patdata_to_json_and_excel: Preparing to save JSON to {json_filename}")
    try:
        final_serializable_patdata = {}
        for k in expected_keys_order:
             v = patdata.get(k) # Hole den Wert aus dem finalen patdata dict
             final_serializable_patdata[k] = (v.strftime("%d.%m.%Y") if isinstance(v, (datetime.date, datetime.datetime)) else v)

        with open(json_filename, "w", encoding="utf-8") as f: json.dump(final_serializable_patdata, f, ensure_ascii=False, indent=4)
        print(f"\nJSON gespeichert unter: {json_filename}")
        logging.info(f"export_patdata_to_json_and_excel: JSON saved successfully to {json_filename}")

    except Exception as e:
        print(f"Fehler beim Speichern der JSON-Datei '{json_filename}': {e}\n{traceback.format_exc()}")
        logging.error(f"export_patdata_to_json_and_excel: Failed to save JSON file '{json_filename}': {e}", exc_info=True)

    import viewjson
    print("Starte viewjson mit patientennummer als argument")
    viewjson.main(patientennummer)

    # --- Excel Export ---
    excel_filename = os.path.join(export_dir, "patients.xlsx")
    logging.info(f"export_patdata_to_json_and_excel: Preparing to update Excel file: {excel_filename}")
    try:
        openpyxl = importlib.import_module("openpyxl")

        try: workbook = openpyxl.load_workbook(excel_filename)
        except FileNotFoundError:
            print(f"INFO: Excel-Datei '{excel_filename}' nicht gefunden. Erstelle neue Datei mit Kopfzeile.")
            workbook = openpyxl.Workbook()
            sheet = workbook.active
            # Schreibe Kopfzeile basierend auf expected_keys_order
            for col_idx, header in enumerate(expected_keys_order, start=1):
                sheet.cell(row=1, column=col_idx).value = header
        else: # Wenn Datei existiert
            sheet = workbook.active
            # Optional: Prüfen, ob Kopfzeile existiert/übereinstimmt. Hier nicht implementiert.

        sheet.insert_rows(idx=2)
        data_to_write = []
        for key in expected_keys_order:
            value = patdata.get(key) # Hole den Wert aus dem finalen patdata dict
            if value is None: data_to_write.append("")
            elif isinstance(value, bool): data_to_write.append(str(value).upper())
            # elif isinstance(value, str) and re.match(r'\d{2}\.\d{2}\.\d{4}', value): # Datumsformatierung unten
            #    data_to_write.append(value)
            else: data_to_write.append(value)

        for col_idx, cell_value in enumerate(data_to_write, start=1):
             cell = sheet.cell(row=2, column=col_idx)
             # Datumsformatierung anwenden, falls es ein Datumsobjekt oder String im Format ist
             current_key = expected_keys_order[col_idx-1]
             is_date_key = current_key in ["geburtsdatum", "eintrittsdatum", "datum_erste_rt", "datum_letzte_rt"]

             if is_date_key and isinstance(cell_value, (datetime.date, datetime.datetime)):
                 cell.value = cell_value # Direkt das Objekt schreiben
                 cell.number_format = 'dd.mm.yyyy'
             elif is_date_key and isinstance(cell_value, str) and re.match(r'\d{2}\.\d{2}\.\d{4}', cell_value):
                  try:
                      dt_obj = datetime.datetime.strptime(cell_value, "%d.%m.%Y")
                      cell.value = dt_obj
                      cell.number_format = 'dd.mm.yyyy'
                  except ValueError:
                      print(f"Warnung: Konnte Datumswert '{cell_value}' für Excel nicht korrekt formatieren.")
                      cell.value = cell_value # Schreibe den String, wenn Konvertierung fehlschlägt
             else:
                 cell.value = cell_value # Schreibe den Wert wie er ist

        workbook.save(excel_filename)
        print(f"Excel-Datei '{excel_filename}' aktualisiert (neue Daten in Zeile 2).")
        logging.info(f"export_patdata_to_json_and_excel: Excel file '{excel_filename}' saved successfully.")
    except ImportError: print("\nFEHLER: Modul 'openpyxl' für Excel-Export nicht gefunden.")
    except PermissionError: print(f"\nFEHLER: Keine Schreibberechtigung für Excel-Datei '{excel_filename}'. Geöffnet?")
    except Exception as e: print(f"\nFehler beim Excel-Export: {e}\n{traceback.format_exc()}")
    logging.info("export_patdata_to_json_and_excel: Export process finished.")


# --- Main Function ---
def main():
    global nachname, vorname, geburtsdatum, alter, geschlecht, patientennummer, eintrittsdatum
    global spi, rea, ips, oberarzt, simultane_chemotherapie, chemotherapeutikum, therapieintention
    global fraktionen_woche, behandlungskonzept_serie1, behandlungskonzept_serie2, behandlungskonzept_serie3, behandlungskonzept_serie4
    global datum_erste_rt, datum_letzte_rt, ecog, tumor, zimmer, aufnahmegrund
    global entity, icd_code, secondary_entity, secondary_icd_code # Globale Referenzen für Entitäten


    try:
        # --- 4. Get Basic Patient Data ---
        stat = UNIVERSAL.userinput_stat("Stationärer Patient (j/n)? ")
        UNIVERSAL.KISIM_im_vordergrund()
        print("\nLese KISIM-Zeile nach Patientendaten aus...")
        nachname, vorname, geburtsdatum, alter, geschlecht, patientennummer, eintrittsdatum = UNIVERSAL.auslesen_patdata_KISIMzeile()
        print("\nLese SPI, REA/IPS...")
        if stat == 'j':
            spi = UNIVERSAL.auslesen_spi()
            rea, ips = UNIVERSAL.auslesen_reaips()

        print("Basis-Patientendaten, SPI, REA/IPS erfolgreich ausgelesen.")
        if not patientennummer:
            logging.error("main: Patientennummer konnte nicht gelesen werden. Exiting.")
            print("FEHLER: Patientennummer konnte nicht gelesen werden."); sys.exit(1)
        if not geschlecht:
            logging.warning("main: Geschlecht konnte nicht gelesen werden.")
            print("WARNUNG: Geschlecht nicht gelesen.")

        # --- 5. Attempt to Open RT Konzept ---
        print("\nVersuche RT-Konzept zu öffnen...")
        rtkonzept_offen = UNIVERSAL.rt_konzept_oeffnen()
        print(f"Ergebnis RT-Konzept öffnen: {'Erfolgreich' if rtkonzept_offen else 'Nicht erfolgreich/gefunden'}")
        time.sleep(1)

        # --- 6. Process based on RT Konzept Success ---
        if rtkonzept_offen is True:
            logging.info("main: RT Konzept seems to be open (rtkonzept_offen is True). Proceeding with data extraction.")
            print("\nRT-Konzept geöffnet. Extrahiere Daten...")
            ocr_erfolgreich = False
            if screenshot_rtkonzept():
                print("Screenshot für OCR erstellt. Führe OCR durch...")
                ocr_ergebnis = easyocr_screenshot_rtkonzept()
                if ocr_ergebnis is True:
                    print("OCR erfolgreich durchgeführt.")
                    oberarzt_aus_ocr_auslesen()
                    ocr_erfolgreich = True
                else:
                    logging.warning("main: easyocr_screenshot_rtkonzept failed or returned no text.")
                    print("FEHLER: OCR ist fehlgeschlagen oder hat keinen Text erkannt. Oberarzt kann nicht automatisch extrahiert werden.")
            else:
                 logging.warning("main: screenshot_rtkonzept failed.")
                 print("FEHLER: Screenshot für OCR konnte nicht erstellt werden.")

            if not ocr_erfolgreich:
                 logging.warning("main: OCR process was not successful, RT concept data extraction might be incomplete.")
                 print("WARNUNG: Datenextraktion aus RT-Konzept war nicht vollständig möglich (Screenshot oder OCR fehlgeschlagen).")

            simultane_chemotherapie_aus_ocr_auslesen()
            therapieintention = therapieintention_auslesen()
            print(f"Globale therapieintention definiert: {therapieintention}")
            fraktionen_woche = fraktionen_woche_auslesen()
            print(f"Globale fraktionen_woche definiert: {fraktionen_woche}")

            
                    

            # --- Manuelle Eingaben (immer nach automatischen Versuchen) ---
            logging.info("main: Starting manual input prompts for RT-Konzept related variables.")
            if oberarzt is None:
                logging.info("main: Oberarzt is None, prompting user.")
                print("Oberarzt wurde nicht automatisch via OCR gelesen.")
                oberarzt = UNIVERSAL.userinput_freitext("Bitte Oberarzt manuell eingeben (Enter überspringt): ")

            if simultane_chemotherapie == "ja":
                logging.info("main: Sim-Chemo is 'ja', checking if chemotherapeutikum is set.")
                if not chemotherapeutikum:
                     logging.info("main: Chemotherapeutikum not set, prompting user.")
                     chemotherapeutikum = UNIVERSAL.userinput_chemotherapie("Simultane Chemo = 'ja'. Bitte Medikament spezifizieren (Enter überspringt): ")
            elif simultane_chemotherapie == "nicht bestimmt":
                 logging.info("main: Sim-Chemo is 'nicht bestimmt', prompting user.")
                 chemo_manual = UNIVERSAL.userinput_stat("Simultane Chemo nicht automatisch ausgelesen. Liegt vor? (j/n): ")
                 if chemo_manual == 'j':
                      simultane_chemotherapie = "ja"
                      logging.info("main: User confirmed sim-chemo is 'ja'. Prompting for drug.")
                      chemotherapeutikum = UNIVERSAL.userinput_chemotherapie("Bitte Medikament spezifizieren (Enter überspringt): ")
                 elif chemo_manual == 'n':
                      simultane_chemotherapie = "nein"
                      logging.info("main: User confirmed sim-chemo is 'nein'.")
                 else:
                     logging.info("main: User skipped manual chemo confirmation.")
            # --- Tumor-Eingabe ---
            print("\n--- Tumorentität Erfassung ---")
            tumor = UNIVERSAL.userinput_freitext("Tumor-Freitext eingeben (in Dativ), z.B. 'sphenoidalem Meningeom rechts': ")

            # --- Primäre Entitäts-Erkennung/Validierung ---
            entity_found = find_matching_entity(tumor)

            if entity_found:
                icd_found = get_icd_code(entity_found)
                prompt = f"\n\n'{entity_found}' erkannt (ICD: {icd_found}) - korrekt? \n[j]=Ja \n[n]= Nein, manuell aus Tumorliste auswählen \nEingabe: "
                choice = input(prompt).strip().lower()
                if choice == 'j': # Enter
                    entity = entity_found
                    icd_code = icd_found
                    print("Primäre Entität übernommen.")
                elif choice == 'n':
                    entity, icd_code = manuelle_entity_auswahl()
                else:
                    entity = None
                    icd_code = None
                    print("Ungültige Eingabe. Primäre Entität nicht gesetzt.")
            else: # Kein Match gefunden
                if tumor: # Nur fragen wenn etwas eingegeben wurde
                    print(f"Keine automatische Übereinstimmung für '{tumor}' gefunden.")
                    prompt = "Möchten Sie manuell eine primäre Entität auswählen? [j]=Ja / [n]=Nein/Überspringen: "
                    choice = input(prompt).strip().lower()
                    if choice == 'j':
                        entity, icd_code = manuelle_entity_auswahl()
                    else: # '-' oder andere Eingabe
                        entity = None
                        icd_code = None
                        print("Primäre Entität nicht gesetzt.")
                else: # Wenn Tumor-Eingabe leer war
                    entity = None
                    icd_code = None
                    print("Keine Tumorentität eingegeben, primäre Entität nicht gesetzt.")

            # --- 3. Sekundäre Neoplasie als Ziel Abfragen ---
            secondary_entity = None
            secondary_icd_code = None


            if entity:
                sec_choice = input("\n\nIst eine sekundäre Neoplasie (=Metastase) das Ziel der Bestrahlung? (ICD-10- und Abrechnungsrelevant!).\n[j]= Ja, sekundäre Neoplasie jetzt erfassen \n[n]= Nein\nEingabe:").strip().lower()
                if sec_choice == 'j':
                    secondary_entity, secondary_icd_code = manuelle_sekundaer_auswahl()
                else:
                    print("Keine sekundäre Neoplasie als Bestrahlungsziel angegeben.")
                    secondary_entity = None
                    secondary_icd_code = None
            else:
                print("\nKeine primäre Entität festgelegt, Abfrage für sekundäre Neoplasie übersprungen.")
                secondary_entity = None
                secondary_icd_code = None


            if not therapieintention:
                print("therapieintention konnte nicht automatisch ausgelesen werden, bitte angeben.")
                therapieintention = UNIVERSAL.userinput_intention("\nTherapieintention kurativ, palliativ oder lokalablativ?  (k/p/l oder Enter): ")
            if not fraktionen_woche:
                print("fraktionen_woche konnte nicht automatisch ausgelesen werden, bitte angeben.")    
                fraktionen_woche = UNIVERSAL.userinput_fraktionen_woche("\nAuswahl der Fraktionen pro Woche:")
            behandlungskonzept_serie1, behandlungskonzept_serie2, behandlungskonzept_serie3, behandlungskonzept_serie4 = UNIVERSAL.userinput_behandlungskonzept(f"\nBehandlungskonzept Serie 1 (im Stil:  Metastase mit 5 x 9 Gy = 45 Gy @65%    oder [Enter] zum Überspringen): ")
            datum_erste_rt = UNIVERSAL.userinput_date_ddmmyyyy("\nDatum erster RT-Termin [dd.mm.yyyy oder Enter]: ")
            datum_letzte_rt = UNIVERSAL.userinput_date_ddmmyyyy("\nDatum letzter RT-Termin [dd.mm.yyyy oder Enter]: ")
        else: # rtkonzept_offen is not True
            logging.warning("main: RT Konzept was not detected as open (rtkonzept_offen is not True). Prompting for manual input.")
            print("\nRT-Konzept nicht geöffnet oder nicht erkannt.")
            oberarzt = UNIVERSAL.userinput_freitext("RT-Konzept nicht verfügbar. Bitte Oberarzt eingeben (Enter überspringt): ")
            manual_rt_input_choice = UNIVERSAL.userinput_stat("RT-Konzept Variablen manuell festlegen? (j/n oder Enter): ")
            if manual_rt_input_choice == 'j':
                logging.info("main: User chose to manually input RT variables.")
                print("\nManuelle Eingabe für RT-Variablen:")
                chemo_manual = UNIVERSAL.userinput_stat("Simultane Chemotherapie? (j/n oder Enter): ")
                if chemo_manual == 'j':
                     simultane_chemotherapie = "ja"
                     logging.info("main: User set manual Sim-Chemo to 'ja'. Prompting for drug.")
                     chemotherapeutikum = UNIVERSAL.userinput_chemotherapie("Bitte Chemotherapeutikum spezifizieren (Enter überspringt): ")
                elif chemo_manual == 'n':
                     simultane_chemotherapie = "nein"
                     logging.info("main: User set manual Sim-Chemo to 'nein'.")
                else:
                     simultane_chemotherapie = None
                     logging.info("main: User skipped manual Sim-Chemo input.")

                # --- Tumor-Eingabe ---
                print("\n--- Tumorentität Erfassung ---")
                tumor = UNIVERSAL.userinput_freitext("Tumor-Freitext eingeben (in Dativ), z.B. 'sphenoidalem Meningeom rechts': ")

                # --- Primäre Entitäts-Erkennung/Validierung ---
                entity_found = find_matching_entity(tumor)

                if entity_found:
                    icd_found = get_icd_code(entity_found)
                    prompt = f"\n\nPrimär-Entität (zu Abrechnungszwecken erkannt): \n'{entity_found}' (ICD: {icd_found}). Korrekt? \n[j]=Ja \n[n]= Nein, manuell aus Tumorliste auswählen \nEingabe: "
                    choice = input(prompt).strip().lower()
                    if choice == 'j': # Enter
                        entity = entity_found
                        icd_code = icd_found
                        print("Primäre Entität übernommen.")
                    elif choice == 'n':
                        entity, icd_code = manuelle_entity_auswahl()
                    else:
                        entity = None
                        icd_code = None
                        print("Ungültige Eingabe. Primäre Entität nicht gesetzt.")
                else: # Kein Match gefunden
                    if tumor: # Nur fragen wenn etwas eingegeben wurde
                        print(f"Keine automatische Übereinstimmung für '{tumor}' gefunden.")
                        prompt = "Möchten Sie manuell eine primäre Entität auswählen? [a]=Ja / [-]=Nein/Überspringen: "
                        choice = input(prompt).strip().lower()
                        if choice == 'a':
                            entity, icd_code = manuelle_entity_auswahl()
                        else: # '-' oder andere Eingabe
                            entity = None
                            icd_code = None
                            print("Primäre Entität nicht gesetzt.")
                    else: # Wenn Tumor-Eingabe leer war
                        entity = None
                        icd_code = None
                        print("Keine Tumorentität eingegeben, primäre Entität nicht gesetzt.")
                therapieintention = UNIVERSAL.userinput_intention("Therapieintention (k/p/l oder Enter): ")
                fraktionen_woche = UNIVERSAL.userinput_fraktionen_woche("\nAuswahl der Fraktionen pro Woche:")
                behandlungskonzept_serie1, behandlungskonzept_serie2, behandlungskonzept_serie3, behandlungskonzept_serie4 = UNIVERSAL.userinput_behandlungskonzept("Behandlungskonzept Serie 1 (Enter überspringt): ")
                datum_erste_rt = UNIVERSAL.userinput_date_ddmmyyyy("Datum erster RT-Termin [dd.mm.yyyy oder Enter]: ")
                datum_letzte_rt = UNIVERSAL.userinput_date_ddmmyyyy("Datum letzter RT-Termin [dd.mm.yyyy oder Enter]: ")
            else:
                 logging.info("main: User chose not to manually input RT variables (except Oberarzt).")
                 print("RT-Variablen werden nicht manuell erfasst (außer Oberarzt).")

       

        # --- 7. Ask for remaining data (always asked) ---
        print("\nBitte weitere allgemeine Daten eingeben:")
        ecog = UNIVERSAL.userinput_ecog("ECOG-Status (0-4), oder [x] falls unbekannt): ")

        # --- 8. Ask for inpatient details if applicable ---
        temp_zimmer = ""; temp_aufnahmegrund = ""

        eintrittsdatum_final = eintrittsdatum # Nimm initial das aus KISIM

        if stat == "j":
            logging.info("main: Patient is inpatient. Prompting for Zimmer, Aufnahmegrund, Eintrittsdatum stat.")
            print("Patient ist stationär.")
            temp_zimmer = UNIVERSAL.userinput_freitext("Zimmer (stationär): ")
            temp_aufnahmegrund = UNIVERSAL.userinput_freitext("Aufnahmegrund/Indikation für Hospitalisation: ")

        # Zukunfts-Check für das endgültige Eintrittsdatum
        if eintrittsdatum_final:
            try:
                if isinstance(eintrittsdatum_final, str) and re.match(r'\d{2}\.\d{2}\.\d{4}', eintrittsdatum_final):
                    heute_dt = datetime.date.today()
                    eintritt_dt = datetime.datetime.strptime(eintrittsdatum_final, "%d.%m.%Y").date()
                    limit_dt = heute_dt + timedelta(days=7)
                    if eintritt_dt > limit_dt:
                        logging.warning(f"main: Eintrittsdatum ({eintrittsdatum_final}) is more than 7 days in the future. Setting to None.")
                        print(f"WARNUNG: Eintrittsdatum ({eintrittsdatum_final}) liegt mehr als 7 Tage in der Zukunft. Wird auf None gesetzt.")
                        eintrittsdatum_final = None
                elif not isinstance(eintrittsdatum_final, str):
                     pass
                else: # String doesn't match format
                    raise ValueError("Datum nicht im Format dd.mm.yyyy")
            except ValueError:
                logging.warning(f"main: Could not parse Eintrittsdatum '{eintrittsdatum_final}' for future check or invalid format. Setting to None.")
                print(f"WARNUNG: Konnte Eintrittsdatum '{eintrittsdatum_final}' nicht für Zukunfts-Check parsen oder Format ungültig. Wird auf None gesetzt.")
                eintrittsdatum_final = None

        # Setze die finalen globalen Variablen für stat. Aufenthalt
        eintrittsdatum = eintrittsdatum_final
        if not eintrittsdatum and stat == 'j':
            UNIVERSAL.userinput_date_ddmmyyyy("Eintrittsdatum stationär [dd.mm.yyyy]: ")
        zimmer = temp_zimmer
        aufnahmegrund = temp_aufnahmegrund

        # --- 9. Assemble Final Dictionary ---
        logging.info("main: Assembling final patdata_dict from global variables.")
        patdata_dict = {
            "nachname": nachname, "vorname": vorname, "geburtsdatum": geburtsdatum, "alter": alter, "geschlecht": geschlecht,
            "patientennummer": patientennummer, "eintrittsdatum": eintrittsdatum,
            "spi": spi, "rea": rea, "ips": ips,
            "tumor": tumor, "entity": entity, "icd_code": icd_code,  
            "secondary_entity": secondary_entity, "secondary_icd_code": secondary_icd_code, 
            "oberarzt": oberarzt,
            "simultane_chemotherapie": simultane_chemotherapie, "chemotherapeutikum": chemotherapeutikum,
            "therapieintention": therapieintention, "fraktionen_woche": fraktionen_woche,
            "behandlungskonzept_serie1": behandlungskonzept_serie1, "behandlungskonzept_serie2": behandlungskonzept_serie2,
            "behandlungskonzept_serie3": behandlungskonzept_serie3, "behandlungskonzept_serie4": behandlungskonzept_serie4,
            "datum_erste_rt": datum_erste_rt, "datum_letzte_rt": datum_letzte_rt,
            "ecog": ecog, "zimmer": zimmer, "aufnahmegrund": aufnahmegrund
        }
        print("\nPatientendaten gesammelt. Starte Korrekturphase und Export...")

        # --- 10. Correction and Export ---
        logging.info("main: Calling export_patdata_to_json_and_excel.")
        export_patdata_to_json_and_excel(patdata_dict)
        logging.info("main: Script finished successfully after export call.")
        print("\n--- Datenexport abgeschlossen, patdata.py Skript beendet ---")
        return True

    except KeyboardInterrupt:
        logging.warning("main: Script interrupted by user (KeyboardInterrupt).")
        print("\nSkript durch Benutzer abgebrochen.")
        return False
    except SystemExit as e:
        logging.warning(f"main: Script aborted via sys.exit: {e}")
        print(f"\nSkript wurde beendet: {e}")
        return False
    except Exception as e:
        logging.error(f"main: An unexpected error occurred in main try block: {e}", exc_info=True)
        print(f"\nUnerwarteter FEHLER im Hauptablauf: {e}\n{traceback.format_exc()}")
        return False
    finally:
        logging.info("patdata.py - main() function finished.")


# --- Main execution block ---
if __name__ == "__main__":
    log_file_direct = os.path.join(patdata_dir, 'patdata_direct_run.log')
    os.makedirs(patdata_dir, exist_ok=True)
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
                        filename=log_file_direct,
                        filemode='w')
    logging.info("patdata.py executed directly.")
    print(f"Logging direct execution to: {log_file_direct}")
    main()