# --- START OF FILE test.py ---

# --- Imports (wie zuvor) ---
import UNIVERSAL
import os
import sys
import pyautogui
import clipboard
import time
import numpy as np
import importlib
import traceback

try:
    from PIL import Image as PIL_Image
    from PIL import ImageEnhance as PIL_ImageEnhance
    from PIL import ImageFilter as PIL_ImageFilter
except ImportError:
    print("FEHLER: PIL (Pillow) Modul nicht gefunden. Bitte installieren (pip install Pillow).")
    sys.exit(1)

# --- Path Definitions (wie zuvor) ---
script_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.dirname(script_dir)
user_home = os.path.expanduser("~")
patdata_dir = os.path.join(user_home, "patdata")
screenshots_dir = os.path.join(script_dir, 'screenshots pyautogui')
local_screenshots_dir = os.path.join(screenshots_dir, 'UNIVERSAL', 'bereich_laborkumulativ')
screenshot_path_preprocessed = os.path.join(screenshots_dir, 'UNIVERSAL', 'image_preprocessing', 'screenshot_labor_preprocessed.png')

print(f"Script directory (test.py): {script_dir}")
print(f"Screenshots base directory: {screenshots_dir}")
print(f"Local lab screenshots directory: {local_screenshots_dir}")
print(f"Path to preprocessed lab image: {screenshot_path_preprocessed}")

# --- Global Variable (kann entfernt werden, wenn main() Werte zurückgibt) ---
# structured_text_lines = [] # Wird jetzt innerhalb von main verarbeitet

# --- Core Functions ---

# ocr_mit_easyocr_detailed() bleibt wie zuvor
def ocr_mit_easyocr_detailed(image_path_or_pil_image):
    # ... (Code aus vorherigem Block ohne Änderungen) ...
    """
    Führt OCR mit EasyOCR durch und gibt die detaillierten Ergebnisse zurück.
    Verwendet den gecachten Reader aus UNIVERSAL.get_reader_easyocr().
    OHNE logging-Modul. Jetzt Teil von test.py.

    Args:
        image_path_or_pil_image (str | PIL.Image.Image): Pfad zum Bild oder PIL Image Objekt.

    Returns:
        list[tuple] | None: Eine Liste von Tupeln im Format [(bounding_box, text, confidence), ...]
                             bounding_box = [[x1,y1],[x2,y2],[x3,y3],[x4,y4]] (TL, TR, BR, BL)
                             Gibt None zurück, wenn ein Fehler auftritt (z.B. Reader nicht verfügbar).
                             Gibt eine leere Liste ([]) zurück, wenn kein Text erkannt wurde.
    """
    function_name = "ocr_mit_easyocr_detailed (local)" # Markiert als lokal
    print(f"\n--- Start {function_name} ---")

    # --- 1. EasyOCR Reader holen (aus UNIVERSAL) ---
    try:
        print(f"[{function_name}] Hole EasyOCR Reader via UNIVERSAL...")
        # WICHTIG: Ruft die Funktion aus UNIVERSAL auf
        reader = UNIVERSAL.get_reader_easyocr()
        if reader is None:
            print(f"FEHLER [{function_name}]: EasyOCR Reader ist nicht verfügbar (via UNIVERSAL). Aborting OCR.")
            return None
        print(f"[{function_name}] EasyOCR Reader erhalten.")
    except Exception as reader_err:
        print(f"FEHLER [{function_name}] beim Holen des EasyOCR Readers via UNIVERSAL: {reader_err}")
        traceback.print_exc()
        return None

    # --- 2. Bild vorbereiten (falls Pfad übergeben wurde) ---
    image_input = None
    input_type = "Unknown"
    try:
        # PIL ist bereits oben importiert
        if isinstance(image_path_or_pil_image, str):
            input_type = "File Path"
            print(f"[{function_name}] Eingabe ist Dateipfad: {image_path_or_pil_image}")
            if not os.path.isfile(image_path_or_pil_image):
                 print(f"FEHLER [{function_name}]: Bilddatei nicht gefunden: {image_path_or_pil_image}")
                 return None
            print(f"[{function_name}] Lade Bild...")
            image_pil = PIL_Image.open(image_path_or_pil_image)
            image_input = np.array(image_pil.convert('RGB')) # Konvertiere zu NumPy Array
            print(f"[{function_name}] Bild geladen und zu NumPy konvertiert.")

        elif isinstance(image_path_or_pil_image, PIL_Image.Image):
            input_type = "PIL Image"
            print(f"[{function_name}] Eingabe ist PIL Image Objekt.")
            image_input = np.array(image_path_or_pil_image.convert('RGB'))
            print(f"[{function_name}] PIL Image zu NumPy konvertiert.")
        else:
            print(f"FEHLER [{function_name}]: Ungültiger Eingabetyp: {type(image_path_or_pil_image)}. Erwartet String oder PIL Image.")
            return None

    except FileNotFoundError:
        print(f"FEHLER [{function_name}]: Bilddatei wurde nach Prüfung nicht gefunden: {image_path_or_pil_image}")
        return None
    except Exception as img_err:
        print(f"FEHLER [{function_name}] beim Laden/Vorbereiten des Bildes (Typ: {input_type}): {img_err}")
        traceback.print_exc()
        return None

    # --- 3. OCR durchführen ---
    try:
        print(f"[{function_name}] Führe OCR mit EasyOCR durch (detail=1, paragraph=False)...")

        detailed_results = reader.readtext(image_input, detail=1, paragraph=False)

        print(f"[{function_name}] EasyOCR Detail-Ergebnis (Anzahl Blöcke): {len(detailed_results)}")

    except Exception as ocr_err:
        print(f"FEHLER [{function_name}] während der Texterkennung (OCR): {ocr_err}")
        traceback.print_exc()
        return None # Bei OCR-Fehler None zurückgeben

    # --- 4. Abschluss und Rückgabe ---
    print(f"--- {function_name} erfolgreich abgeschlossen. Gibt {len(detailed_results)} detaillierte Blöcke zurück. ---")
    return detailed_results # Gibt die Liste der Tupel zurück


# group_results_by_lines() bleibt wie zuvor
def group_results_by_lines(ocr_results, y_tolerance=7, x_spacing_threshold=10):
    # ... (Code aus vorherigem Block ohne Änderungen) ...
    """
    Gruppiert detaillierte OCR-Ergebnisse (von EasyOCR mit detail=1)
    basierend auf der Y-Koordinate der Bounding Box in Zeilen.
    OHNE logging-Modul. Jetzt Teil von test.py.

    Args:
        ocr_results (list): Liste von (bounding_box, text, confidence) von EasyOCR.
                            bounding_box = [[x1,y1],[x2,y2],[x3,y3],[x4,y4]]
        y_tolerance (int): Maximale vertikale Abweichung der Y-Mitte (in Pixeln),
                           damit Blöcke zur selben Zeile gehören. Muss ggf. angepasst werden.
        x_spacing_threshold (int): Minimaler horizontaler Abstand (in Pixeln) zwischen
                                   den Enden einer Box und dem Anfang der nächsten,
                                   unterhalb dessen KEIN zusätzliches Leerzeichen
                                   eingefügt wird.

    Returns:
        list[str]: Eine Liste von Strings, wobei jeder String eine erkannte und
                   horizontal sortierte Textzeile darstellt. Gibt eine leere
                   Liste zurück, wenn keine Ergebnisse gruppiert werden konnten.
    """
    function_name = "group_results_by_lines (local)" # Markiert als lokal
    if not ocr_results:
        print(f"WARNUNG [{function_name}]: Keine OCR-Ergebnisse zum Gruppieren erhalten.")
        return []

    print(f"[{function_name}] Starte Zeilengruppierung (y_tolerance={y_tolerance}, x_spacing={x_spacing_threshold})...")

    lines = {}

    # 1. Textblöcke Y-Koordinaten zuordnen
    for box, text, confidence in ocr_results:
        if not box or len(box) != 4:
             print(f"WARNUNG [{function_name}]: Überspringe ungültige Bounding Box für Text '{text}'. Box: {box}")
             continue

        # Berechne Y-Mitte und X-Grenzen robust
        try:
            y_coords = [p[1] for p in box]
            x_coords = [p[0] for p in box]
            y_start, y_end = min(y_coords), max(y_coords)
            x_start, x_end = min(x_coords), max(x_coords)
            y_center = (y_start + y_end) / 2
        except (IndexError, TypeError):
             print(f"WARNUNG [{function_name}]: Fehler beim Verarbeiten der Koordinaten für Box {box}. Überspringe.")
             continue


        found_line_key = None
        for key_y in lines.keys():
            if abs(y_center - key_y) <= y_tolerance:
                found_line_key = key_y
                break

        if found_line_key is not None:
            lines[found_line_key].append([y_center, x_start, x_end, text])
            # Berechne neuen Durchschnitts-Y-Wert sicher
            current_y_centers = [item[0] for item in lines[found_line_key]]
            if current_y_centers: # Nur wenn Liste nicht leer ist
                 new_avg_y = np.mean(current_y_centers)
                 if new_avg_y != found_line_key:
                      lines[new_avg_y] = lines.pop(found_line_key)
            else: # Sollte nicht vorkommen, aber zur Sicherheit
                 print(f"WARNUNG [{function_name}]: Leere Elementliste für Zeile {found_line_key} nach Hinzufügen?")
        else:
            lines[y_center] = [[y_center, x_start, x_end, text]]

    # 2. Zeilen nach Y sortieren und Elemente innerhalb der Zeile nach X sortieren
    sorted_line_keys = sorted(lines.keys())
    formatted_lines = []

    print(f"[{function_name}] In {len(sorted_line_keys)} potenzielle Zeilen gruppiert.")

    for line_y in sorted_line_keys:
        line_elements = lines[line_y]
        # Sortiere Elemente nach X-Startkoordinate
        line_elements.sort(key=lambda item: item[1])

        # 3. Text der Zeile zusammensetzen
        line_str = ""
        last_x_end = -1
        for y_c, x_s, x_e, txt in line_elements:
            # Füge Leerzeichen hinzu, wenn der Abstand groß genug ist
            # oder wenn es das erste Element ist
            if last_x_end < 0 or (x_s - last_x_end) > x_spacing_threshold:
                 if line_str: # Nur Leerzeichen, wenn schon Text da ist
                      line_str += " "
            # Füge Text hinzu (sicherstellen, dass es ein String ist)
            line_str += str(txt) if txt is not None else ""
            last_x_end = x_e

        formatted_lines.append(line_str)
        # Zum Debuggen:
        # print(f"[{function_name}] Zeile (Y≈{line_y:.1f}): Formatiert='{line_str}'")

    print(f"[{function_name}] Zeilengruppierung abgeschlossen. Gibt {len(formatted_lines)} formatierte Zeilen zurück.")
    return formatted_lines

# extract_first_value_after_unit_heuristic() bleibt wie zuvor
def extract_first_value_after_unit_heuristic(line_text):
    # ... (Code aus vorherigem Block ohne Änderungen) ...
    """
    Extrahiert den ERSTEN numerischen Wert, der NACH den anfänglichen
    Beschreibungs-Teilen (Name, Referenzbereich, Einheit) in einer Zeile vorkommt.
    Berücksichtigt mögliche 'L' oder 'H' Suffixe.

    Args:
        line_text (str): Die Textzeile aus dem Laborbericht.

    Returns:
        str | None: Den gefundenen Wert als String (inkl. L/H) oder None,
                    wenn kein passender numerischer Wert gefunden wurde.
    """
    if not line_text or not isinstance(line_text, str):
        return None
    parts = line_text.split()
    if len(parts) < 3: # Braucht mindestens Name, Ref/Einheit, Wert
        return None

    # Heuristik zur Bestimmung des Startindex für Werte
    start_index = 2 # Fallback: Start bei Index 2
    unit_indices = [i for i, part in enumerate(parts) if ('/' in part or '%' in part) and i > 0] # Suche nach Einheiten ab Index 1
    ref_indices = [i for i, part in enumerate(parts) if '-' in part and '.' not in part and i > 0] # Suche nach Referenzbereichen

    last_desc_index = 0
    if unit_indices:
        last_desc_index = max(last_desc_index, unit_indices[-1])
    if ref_indices:
        last_desc_index = max(last_desc_index, ref_indices[-1])

    start_index = last_desc_index + 1
    if start_index >= len(parts):
        # print(f"DEBUG: Kein Index nach letzter Einheit/Referenz in '{line_text}' gefunden.")
        return None # Einheit/Ref war das letzte Element

    # Starte die Suche ab dem berechneten start_index
    for i in range(start_index, len(parts)):
        part = parts[i]
        cleaned_part = part.strip().upper().replace('L', '').replace('H', '')
        cleaned_part = cleaned_part.replace(',', '.')
        if '(' in cleaned_part and ')' in cleaned_part:
            cleaned_part = cleaned_part.split('(')[0].strip()

        try:
            float(cleaned_part)
            return part.strip()
        except ValueError:
            continue

    # print(f"DEBUG: Konnte keinen ersten numerischen Wert in '{line_text}' ab Index {start_index} finden.")
    return None


# --- Application Specific Functions (using UNIVERSAL) ---
# laborwerte_unbestimmt_anzeigen() bleibt wie zuvor
def laborwerte_unbestimmt_anzeigen():
    # ... (Code aus vorherigem Block ohne Änderungen) ...
    """Navigiert zu den Laborkumulativwerten und stellt den Zeitraum ein."""
    print("\nStarte laborwerte_unbestimmt_anzeigen()...")
    try:
        UNIVERSAL.navigiere_bereich_laborkumulativ()
        print("INFO: Navigiere zu Zeitraum...")
        if not UNIVERSAL.find_and_click_button('button_zeitraum.png', base_path=local_screenshots_dir):
            print('FEHLER: button_zeitraum.png nicht gefunden, beende.')
            return False
        time.sleep(0.2)
        for _ in range(4):
            print("4x press down...")
            pyautogui.press('down')
        pyautogui.press('enter')
        time.sleep(0.8)

    
        print("INFO: Öffne Laborauswahl...")
        if not UNIVERSAL.find_and_click_button('button_auswahl_labor.png', base_path=local_screenshots_dir):
            print('FEHLER: button_auswahl_labor.png nicht gefunden, beende.')
            return False
        print("INFO: Wähle HAE...")
        if not UNIVERSAL.find_and_click_button('button_HAE.png', base_path=local_screenshots_dir):
            print('FEHLER: button_HAE.png nicht gefunden, beende.')
            return False
        print("INFO: Warte auf HAE Bestätigung...")
        if not UNIVERSAL.find_button('button_HAE_confirm.png', base_path=local_screenshots_dir):
            print('FEHLER: button_HAE_confirm.png nicht gefunden, beende.')
            return False
        print("laborwerte_unbestimmt_anzeigen() erfolgreich.")
        return True
    except Exception as e:
        print(f"FEHLER in laborwerte_unbestimmt_anzeigen(): {e}")
        traceback.print_exc()
        return False


# screenshot_labor() bleibt wie zuvor
def screenshot_labor():
    # ... (Code aus vorherigem Block mit Korrektur des Speicherpfads) ...
    """Erstellt einen Screenshot des Laborbereichs und verarbeitet ihn vor."""
    print("\nStarte screenshot_labor()...")
    try:
        ausschnitt_labor = (40, 205, 695, 765)
        print(f"INFO: Screenshot-Region definiert: {ausschnitt_labor}")
        screenshot_labor_pil = pyautogui.screenshot(region=ausschnitt_labor)
        print("INFO: Screenshot erstellt.")
        original_save_dir = os.path.join(screenshots_dir, 'UNIVERSAL', 'image_preprocessing')
        os.makedirs(original_save_dir, exist_ok=True)
        original_save_path = os.path.join(original_save_dir, 'screenshot_labor_original.png')
        screenshot_labor_pil.save(original_save_path)
        print(f"INFO: Original Screenshot gespeichert unter: {original_save_path}")
        print("INFO: Starte Bildvorverarbeitung via UNIVERSAL...")
        screenshot_labor_preprocessed_object = UNIVERSAL.PIL_image_preprocessing_Zoom_Contrast_Sharpen(screenshot_labor_pil)

        if screenshot_labor_preprocessed_object:
            expected_save_path = screenshot_path_preprocessed
            os.makedirs(os.path.dirname(expected_save_path), exist_ok=True)
            screenshot_labor_preprocessed_object.save(expected_save_path)
            print(f"INFO: Vorverarbeitetes Bild ERFOLGREICH gespeichert unter dem erwarteten Pfad: {expected_save_path}")
            print("INFO: screenshot_labor() erfolgreich abgeschlossen.")
            return True
        else:
            print("FEHLER: UNIVERSAL.PIL_image_preprocessing_Zoom_Contrast_Sharpen hat kein Bild zurückgegeben.")
            return False

    except Exception as e:
        print(f"FEHLER in screenshot_labor(): {e}")
        traceback.print_exc()
        return False


# easyocr_screenshot_labor_structured() bleibt wie zuvor
def easyocr_screenshot_labor_structured():
    # ... (Code aus vorherigem Block ohne Änderungen) ...
    """
    Führt detaillierte OCR auf dem vorverarbeiteten Labor-Screenshot durch
    und gruppiert die Ergebnisse zeilenweise unter Verwendung der lokalen Funktionen.
    Gibt die strukturierten Zeilen zurück oder None bei Fehler.
    OHNE logging-Modul.
    """
    # global structured_text_lines # Keine globale Variable mehr nötig

    print("\nStarte easyocr_screenshot_labor_structured()...")
    if not os.path.exists(screenshot_path_preprocessed):
        print(f"FEHLER: Vorverarbeitete Screenshot-Datei nicht gefunden: {screenshot_path_preprocessed}")
        return None # Geändert: Gibt None bei Fehler zurück

    print(f"INFO: Lade vorverarbeitetes Bild: {screenshot_path_preprocessed}")
    try:
        results_easyocr_detailed = ocr_mit_easyocr_detailed(screenshot_path_preprocessed)

        if results_easyocr_detailed is None:
             print("FEHLER: OCR (detailliert) ist fehlgeschlagen (Rückgabewert None).")
             return None # Gibt None bei Fehler zurück
        elif not results_easyocr_detailed:
             print("INFO: OCR (detailliert) hat keinen Text erkannt.")
             return [] # Gibt leere Liste zurück, wenn kein Text erkannt wurde
        else:
             print(f"INFO: OCR (detailliert) hat {len(results_easyocr_detailed)} Textblöcke erkannt.")
             local_structured_text_lines = group_results_by_lines(
                 results_easyocr_detailed,
                 y_tolerance=7,
                 x_spacing_threshold=8
             )

             if local_structured_text_lines:
                 print("\n--- Strukturierte OCR-Ergebnisse (Zeilen) ---")
                 for i, line in enumerate(local_structured_text_lines):
                     print(f"Zeile {i+1:02d}: {line[:100]}{'...' if len(line)>100 else ''}")
                 print("----------------------------------------------")
                 print("INFO: easyocr_screenshot_labor_structured() erfolgreich.")
                 return local_structured_text_lines # Gibt die Liste der Zeilen zurück
             else:
                 print("FEHLER: Konnte Textblöcke nicht sinnvoll zu Zeilen gruppieren.")
                 return None # Gibt None bei Fehler zurück

    except Exception as e:
        print(f"FEHLER während OCR (detailliert) oder Gruppierung: {e}")
        traceback.print_exc()
        return None # Gibt None bei Fehler zurück


# get_ctcae_grade() bleibt wie zuvor
def get_ctcae_grade(param_type, value_str, lower_normal_limit):
    # ... (Code aus vorherigem Block ohne Änderungen) ...
    """
    Bestimmt den CTCAE v5.0 Grad für einen gegebenen Laborparameterwert.
    Berücksichtigt die korrigierten Grenzwerte und die Prüfreihenfolge.

    Args:
        param_type (str): Der Name des Parameters (exakt wie in `thresholds` definiert).
        value_str (str | None): Der extrahierte Laborwert als String (kann L/H enthalten).
        lower_normal_limit (float | None): Die untere Grenze des Normalbereichs für diesen Patienten/Labor.

    Returns:
        int | None: Der CTCAE Grad (0-4) oder None bei ungültiger Eingabe/Fehler.
                    Grad 0 bedeutet normal oder erhöht.
    """
    if value_str is None:
        # print(f"DEBUG get_ctcae_grade: Kein Wert für {param_type} übergeben.")
        return None # Kein Wert vorhanden, kein Grad bestimmbar
    if lower_normal_limit is None:
        print(f"WARNUNG get_ctcae_grade: Keine untere Normgrenze (LNL) für {param_type} übergeben. Grad 1 kann nicht bestimmt werden.")
        # Grading ohne Grad 1 ist möglich, aber unvollständig

    # Wert bereinigen und in float konvertieren
    cleaned_value_str = value_str.strip().upper().replace('L', '').replace('H', '')
    cleaned_value_str = cleaned_value_str.replace(',', '.')
    try:
        value = float(cleaned_value_str)
    except ValueError:
        print(f"FEHLER get_ctcae_grade: Konnte Wert '{value_str}' für {param_type} nicht in Zahl umwandeln.")
        return None

    # CTCAE v5.0 Grenzwerte (G/L Einheiten für Zellen, g/L für Hb)
    # Schlüssel müssen exakt mit denen in parameters_to_extract übereinstimmen
    thresholds = {
        "Hämoglobin":        {"g4": None, "g3": 80.0, "g2": 100.0}, # g/L
        "Leukozyten":        {"g4": 1.0,  "g3": 2.0,  "g2": 3.0},   # G/L
        "Thrombozyten":      {"g4": 25.0, "g3": 50.0, "g2": 75.0},   # G/L (umgerechnet)
        "Neutrophile (abs)": {"g4": 0.5,  "g3": 1.0,  "g2": 1.5},   # G/L
        "Lymphozyten (abs)": {"g4": 0.2,  "g3": 0.5,  "g2": 0.8},   # G/L
    }

    if param_type not in thresholds:
        print(f"FEHLER get_ctcae_grade: Unbekannter Parametertyp '{param_type}' für Grading.")
        return None

    th = thresholds[param_type]

    # Korrigiere LNL aus dem Dictionary mit dem Wert aus dem Aufruf
    # (falls vorhanden, sonst bleibt es None in der Funktion)
    lnl_value = lower_normal_limit

    # Grading von hoch nach niedrig prüfen
    if th.get("g4") is not None and value < th["g4"]:
        return 4
    if th.get("g3") is not None and value < th["g3"]:
        return 3
    if th.get("g2") is not None and value < th["g2"]:
         # Für Leukozyten: Wenn LNL bekannt ist und G2-Schwelle == LNL
         if param_type == "Leukozyten" and lnl_value is not None and th['g2'] == lnl_value:
               # Wenn Wert < LNL (was auch < G2 ist), dann ist es Grad 2 (höchster zutreffender Grad)
               # Wenn Wert >= LNL, aber < G2 (kann hier nicht passieren), wäre es Grad 0
               return 2 # Explizit Grad 2, da < 3.0
         elif param_type != "Leukozyten":
               return 2
         # Fallback für Leukozyten, falls LNL nicht bekannt oder anders als 3.0
         elif param_type == "Leukozyten":
              return 2 # Standardmäßig Grad 2, wenn < 3.0

    # Grad 1: Nur prüfen, wenn LNL bekannt ist
    if lnl_value is not None and value < lnl_value:
        # Grad 1 nur, wenn keine höhere Grade zutreffen
        if (th.get("g2") is None or value >= th["g2"]) and \
           (th.get("g3") is None or value >= th["g3"]) and \
           (th.get("g4") is None or value >= th["g4"]):
            # Spezialfall Leukozyten: Wenn LNL==3.0, wird G1 nie erreicht, da G2 bei <3.0 beginnt.
            if param_type == "Leukozyten" and lnl_value == 3.0:
                pass # Grad 1 ist für Leukozyten mit LNL 3.0 nicht erreichbar
            else:
                return 1

    # Grad 0 (Normal oder erhöht)
    return 0


# --- MODIFIZIERTE main() Funktion ---
def main():
    """
    Hauptfunktion: Führt die Schritte zur Labordatenextraktion aus
    und gibt die CTCAE-Grade der Zielparameter zurück.

    Returns:
        tuple | None: Ein Tuple mit 5 Integer/None-Werten für die CTCAE-Grade
                      in der Reihenfolge: Hämoglobin, Leukozyten, Thrombozyten,
                      Neutrophile (abs), Lymphozyten (abs).
                      Gibt None zurück, wenn ein kritischer Schritt fehlschlägt.
    """
    print("\n--- Starte main() [Modifiziert für Return] ---")

    # 1. Navigation und Screenshot
    if not laborwerte_unbestimmt_anzeigen():
        print("FEHLER: laborwerte_unbestimmt_anzeigen() fehlgeschlagen.")
        return None # Signalisiert Fehler an Aufrufer
    time.sleep(2.5)
    if not screenshot_labor():
        print("FEHLER: screenshot_labor() fehlgeschlagen.")
        return None # Signalisiert Fehler an Aufrufer

    # 2. Strukturierte OCR durchführen
    # Die Funktion gibt jetzt die Zeilenliste oder None zurück
    local_structured_text_lines = easyocr_screenshot_labor_structured()
    if local_structured_text_lines is None:
        print("FEHLER: easyocr_screenshot_labor_structured() fehlgeschlagen.")
        return None # Signalisiert Fehler an Aufrufer
    elif not local_structured_text_lines:
         print("WARNUNG: Keine Textzeilen von OCR erhalten.")
         # In diesem Fall geben wir None für alle Grade zurück
         return (None, None, None, None, None)


    # 3. Gezielte Extraktion und CTCAE Grading
    print("\n--- Starte gezielte Extraktion und CTCAE Grading [Modifiziert für Return] ---")

    parameters_to_extract = {
        "Hämoglobin": 134.0,
        "Leukozyten": 3.0,
        "Thrombozyten": 143.0,
        "Neutrophile (abs)": 1.40,
        "Lymphozyten (abs)": 1.50,
    }
    results = {param: {"wert": None, "grad": None} for param in parameters_to_extract}
    current_section = None

    for line_number, line_text in enumerate(local_structured_text_lines):
        line_lower = line_text.lower()

        if "blutbild automatisch absolut" in line_lower:
            current_section = "absolut"
            continue
        elif "blutbild automatisch relativ" in line_lower:
            current_section = "relativ"
            continue

        for param_name, lnl in parameters_to_extract.items():
            if results[param_name]["wert"] is not None:
                continue

            keyword = param_name.split(" ")[0].lower()
            is_abs_param = "(abs)" in param_name
            process_this_param = False

            if is_abs_param:
                if current_section == "absolut" and keyword in line_lower:
                    process_this_param = True
            elif keyword in line_lower:
                 if current_section == "relativ" and keyword in ["leukozyten", "neutrophile", "lymphozyten"]:
                      pass
                 else:
                      abs_version_exists = f"{param_name.split(' ')[0]} (abs)" in parameters_to_extract
                      if current_section == "absolut" and abs_version_exists and not is_abs_param:
                          pass
                      else:
                          process_this_param = True

            if process_this_param:
                extracted_value_str = extract_first_value_after_unit_heuristic(line_text)
                if extracted_value_str:
                    results[param_name]["wert"] = extracted_value_str
                    grade = get_ctcae_grade(param_name, extracted_value_str, lnl)
                    results[param_name]["grad"] = grade
                    print(f"  -> Wert für '{param_name}' gefunden: {extracted_value_str} (Grad: {grade if grade is not None else 'N/A'})")


    # --- Werte für die Rückgabe extrahieren ---
    hb_grade = results.get("Hämoglobin", {}).get("grad")
    lc_grade = results.get("Leukozyten", {}).get("grad")
    tc_grade = results.get("Thrombozyten", {}).get("grad")
    np_grade = results.get("Neutrophile (abs)", {}).get("grad")
    lz_grade = results.get("Lymphozyten (abs)", {}).get("grad")

    # --- Optionale Ausgabe der finalen Grade (zum Debuggen) ---
    print("\n--- Finale CTCAE Grade für Rückgabe ---")
    print(f"Hämoglobin: {hb_grade}")
    print(f"Leukozyten: {lc_grade}")
    print(f"Lymphozyten (abs): {lz_grade}")
    print(f"Neutrophile (abs): {np_grade}")
    print(f"Thrombozyten: {tc_grade}")
    print("--------------------------------------")

    print("\n--- main() beendet, gibt Grade zurück ---")
    # --- Rückgabe der Grade als Tuple ---
    return hb_grade, lc_grade, lz_grade, np_grade, tc_grade,


# --- Script Entry Point ---
if __name__ == "__main__":
    print("\n==================================================")
    print("=== test.py wird als Hauptskript ausgeführt ===")
    print("==================================================")
    # Wenn direkt ausgeführt, rufe main auf und printe das Ergebnis
    returned_grades = main()
    if returned_grades is None:
        print("\nFEHLER: main() hat None zurückgegeben (kritischer Fehler).")
    else:
        print(f"\nRückgabewert von main(): {returned_grades}")
    print("\n=== Skriptausführung normal beendet ===")

# --- END OF FILE test.py ---