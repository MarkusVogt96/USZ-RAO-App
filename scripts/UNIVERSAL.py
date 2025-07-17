
# Flag to track if UNIVERSAL has been initialized
_universal_initialized = False

# Only print the import message on first load
if not _universal_initialized:
    print("importing UNIVERSAL database...")
import os
if not _universal_initialized:
    print("import os - done")
import sys
if not _universal_initialized:
    print("import sys - done")
import time
if not _universal_initialized:
    print("import time - done")
import datetime
if not _universal_initialized:
    print("import datetime - done")
import importlib
if not _universal_initialized:
    print("import importlib - done")
import logging
if not _universal_initialized:
    print("import logging - done")
import pyautogui
if not _universal_initialized:
    print("import pyautogui - done")
import clipboard
if not _universal_initialized:
    print("import clipboard - done")
import traceback
if not _universal_initialized:
    print("import logging - done")


# --- Define Paths ---
# Get the absolute path of the directory containing the current script (UNIVERSAL.py)
script_dir = os.path.dirname(os.path.abspath(__file__))
# Get the absolute path of the parent directory (the application root, e.g., "USZ RAO App")
app_dir = os.path.dirname(script_dir)
# Define the absolute path to patdata in the user's home directory
user_home = os.path.expanduser("~") 
patdata_dir = os.path.join(user_home, "patdata")
#define screenshots directory
screenshots_dir = os.path.join(script_dir, 'screenshots pyautogui')

if not _universal_initialized:
    print(f"Script directory: {script_dir}")
    print(f"App directory: {app_dir}")
    print(f"Patient data directory: {patdata_dir}")
    print(f"Screenshots directory: {screenshots_dir}")

# Mark as initialized
_universal_initialized = True





######################################################
######################################################
#speichere reader-Status für easyocr und pytesseract
reader_easyocr = None
pytesseract = None


######################################################
######################################################


def PIL_image_preprocessing_Zoom_Contrast_Sharpen(image):
    print(f"\nStart PIL_image_prepocessing aus UNIVERSAL.py")

    # Abhängigkeiten laden
    PIL_Image = importlib.import_module("PIL.Image") if "PIL.Image" not in sys.modules else sys.modules["PIL.Image"]
    PIL_ImageEnhance = importlib.import_module("PIL.ImageEnhance") if "PIL.ImageEnhance" not in sys.modules else sys.modules["PIL.ImageEnhance"]
    PIL_ImageFilter = importlib.import_module("PIL.ImageFilter") if "PIL.ImageFilter" not in sys.modules else sys.modules["PIL.ImageFilter"]
    image_preprocessed = image
    # Bildgröße um Faktor 3 vergrößern
    width, height = image_preprocessed.size
    image_preprocessed = image_preprocessed.resize((width * 3, height * 3), PIL_Image.Resampling.LANCZOS)
    print("Zoom 3x - done")

    # Bildverarbeitung
    image_preprocessed = image_preprocessed.convert('L')  # Graustufen
    image_preprocessed = PIL_ImageEnhance.Contrast(image_preprocessed).enhance(2)  # Kontrast erhöhen
    image_preprocessed = image_preprocessed.filter(PIL_ImageFilter.SHARPEN)  # Schärfen

    # Save path using screenshots_dir
    save_dir = os.path.join(screenshots_dir, 'UNIVERSAL', 'image_preprocessing')
    os.makedirs(save_dir, exist_ok=True) # Ensure directory exists
    save_path = os.path.join(save_dir, 'image_preprocessed_from_function_PIL_image_preprocessing_Zoom_Contrast_Sharpen().png')

    image_preprocessed.save(save_path)
    print(rf"PIL.Enhance und PIL.SHARPEN done, screenshot.png unter {save_path} abgespeichert. ")
    return image_preprocessed

######################################################
######################################################
#dieser Funktion kann in main.py ein screenshot hinzugefügt werden: text = UNIVERSAL.run_tesseract_ocr_deutsch(screenshot.png)

def run_tesseract_ocr_deutsch(screenshot_path):
    """
    Führt Tesseract OCR auf Deutsch für eine Bilddatei durch (All-in-One-Funktion).

    Prüft, ob als Bundle ausgeführt, findet tesseract.exe und tessdata,
    lädt pytesseract bei Bedarf, führt OCR aus und gibt Text zurück.

    Args:
        screenshot_path (str): Der vollständige Pfad zur Bilddatei.

    Returns:
        str: Der erkannte Text (bereinigt).
        None: Wenn ein Fehler auftritt (Initialisierung, Datei nicht gefunden, OCR-Fehler).
    """
    print(f"Starte run_tesseract_ocr_deutsch (All-in-One) für: {screenshot_path}")
    global pytesseract

    # --- 1. Pytesseract laden und Pfad setzen (unverändert) ---
    if pytesseract is None:
        print("Pytesseract Modul noch nicht geladen oder initialisiert. Versuche Initialisierung...")
        try:
            if "pytesseract" not in sys.modules:
                pytesseract_module = importlib.import_module("pytesseract")
                print("Modul 'pytesseract' erfolgreich importiert.")
            else:
                pytesseract_module = sys.modules["pytesseract"]
                print("Modul 'pytesseract' war bereits importiert.")

            if getattr(sys, 'frozen', False):
                app_path = sys._MEIPASS
                print(f"Anwendung läuft als Bundle. Basispfad: {app_path}")
            else:
                app_path = app_dir
                print(f"Anwendung läuft als Skript. Basispfad: {app_path}")

            tesseract_exe_path_bundle = os.path.join(app_path, 'offline_packages', 'tesseract', 'tesseract.exe')
            local_tesseract_fallback = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

            tesseract_cmd_to_set = None
            if os.path.exists(tesseract_exe_path_bundle):
                tesseract_cmd_to_set = tesseract_exe_path_bundle
                print(f"Tesseract executable im App-Pfad gefunden: {tesseract_cmd_to_set}")
            elif os.path.exists(local_tesseract_fallback):
                tesseract_cmd_to_set = local_tesseract_fallback
                print(f"WARNUNG: Tesseract executable nicht im App-Pfad gefunden. Verwende lokalen Fallback: {tesseract_cmd_to_set}")
            else:
                print(f"FEHLER: Tesseract executable weder im App-Pfad ({tesseract_exe_path_bundle}) noch im lokalen Fallback ({local_tesseract_fallback}) gefunden.")
                return None

            pytesseract_module.pytesseract.tesseract_cmd = tesseract_cmd_to_set
            pytesseract = pytesseract_module
            print("Pytesseract initialisiert und tesseract_cmd gesetzt.")

        except ImportError:
            print("FEHLER: Das Modul 'pytesseract' konnte nicht importiert werden.")
            return None
        except Exception as e:
            print(f"FEHLER bei der Initialisierung von Pytesseract: {e}")
            return None

    # --- 2. Tessdata-Pfad bestimmen und als Umgebungsvariable setzen ---
    tessdata_dir_to_use = None
    try:
        if getattr(sys, 'frozen', False):
            app_path = sys._MEIPASS
        else:
            app_path = app_dir

        tessdata_path_bundle = os.path.join(app_path, 'offline_packages', 'tesseract', 'tessdata')
        local_tessdata_fallback = 'C:\\Program Files\\Tesseract-OCR\\tessdata'
        
        if os.path.isdir(tessdata_path_bundle):
            tessdata_dir_to_use = tessdata_path_bundle
        elif os.path.isdir(local_tessdata_fallback):
            tessdata_dir_to_use = local_tessdata_fallback
            print(f"WARNUNG: Tessdata Verzeichnis nicht im App-Pfad gefunden. Verwende lokalen Fallback: {tessdata_dir_to_use}")
        else:
            print(f"FEHLER: Tessdata Verzeichnis weder im App-Pfad ({tessdata_path_bundle}) noch im lokalen Fallback ({local_tessdata_fallback}) gefunden.")
            return None

        # === FINALE KORREKTUR HIER ===
        # Setze die Umgebungsvariable direkt auf den 'tessdata'-Ordner.
        os.environ['TESSDATA_PREFIX'] = tessdata_dir_to_use
        print(f"INFO: TESSDATA_PREFIX Umgebungsvariable gesetzt auf: {os.environ['TESSDATA_PREFIX']}")

    except Exception as e:
        print(f"FEHLER beim Bestimmen des Tessdata-Pfades: {e}")
        return None

    # --- 3. Eingabedatei prüfen ---
    if not os.path.exists(screenshot_path):
        print(f"FEHLER: Bilddatei nicht gefunden unter: {screenshot_path}")
        return None

    # --- 4. OCR durchführen (ohne 'config' Parameter) ---
    try:
        print(f"Führe Tesseract OCR aus (via TESSDATA_PREFIX), lang='deu' für Datei: {screenshot_path}")
        text = pytesseract.image_to_string(screenshot_path, lang='deu')
        print("Tesseract OCR abgeschlossen.")
        cleaned_text = text.strip()
        return cleaned_text
    except Exception as e:
        if pytesseract and hasattr(pytesseract, 'TesseractNotFoundError') and isinstance(e, pytesseract.TesseractNotFoundError):
            print("FEHLER: Tesseract executable nicht gefunden während OCR (unerwartet).")
        else:
            print(f"FEHLER während pytesseract.image_to_string für {screenshot_path}: {e}")
        return None
    

###################################
###################################

def get_reader_easyocr():
    """
    Initialisiert und gibt die EasyOCR Reader Instanz zurück.
    Stellt sicher, dass Modelle aus dem korrekten lokalen Verzeichnis geladen werden,
    sowohl im Skript- als auch im Bundle-Modus.
    """
    logging.critical("!!! UNIVERSAL.get_reader_easyocr WURDE AUFGERUFEN !!!") 
    global reader_easyocr
    if reader_easyocr is None:
        logging.info("Attempting to initialize EasyOCR Reader...") # Use logging
        print("Initialisiere EasyOCR Reader...")
        try:
            # Dynamischer Import von easyocr
            if "easyocr" not in sys.modules:
                logging.info("Importing easyocr module...") # Use logging
                print("Importiere easyocr Modul...")
                importlib.import_module("easyocr")
                logging.info("easyocr module imported.") # Use logging
                print("easyocr Modul importiert.")
            easyocr = sys.modules["easyocr"]

            # Bestimme den Modellpfad basierend auf dem Ausführungskontext
            model_dir = None # Initialize model_dir
            if getattr(sys, 'frozen', False):
                # Anwendung läuft als PyInstaller-Bundle
                if hasattr(sys, '_MEIPASS'):
                    bundle_root = sys._MEIPASS
                else: # Fallback, falls _MEIPASS nicht existiert (sollte nicht vorkommen)
                    bundle_root = os.path.dirname(sys.executable) # Versuche den Pfad der Exe zu bekommen

                model_dir = os.path.join(bundle_root, 'easyocr_models')
                logging.info(f"EasyOCR Bundle-Mode: Looking for models in: {model_dir} (relative to {bundle_root})") # Use logging
                print(f"EasyOCR Bundle-Modus: Suche Modelle in: {model_dir} (relativ zu {bundle_root})")

            else:
                # Anwendung läuft als normales Skript
                model_dir = os.path.join(app_dir, 'offline_packages', 'easyocr_models')
                logging.info(f"EasyOCR Script-Mode: Looking for models in: {model_dir}") # Use logging
                print(f"EasyOCR Skript-Modus: Suche Modelle in: {model_dir}")

            # Überprüfe, ob das Verzeichnis existiert (wichtig für Debugging)
            if not os.path.isdir(model_dir):
                 logging.error(f"EasyOCR model directory NOT FOUND: {model_dir}") # Use logging.error
                 print(f"FEHLER: EasyOCR Modellverzeichnis nicht gefunden: {model_dir}")
                 return None # Wichtig: Fehler signalisieren

            # Initialisiere den Reader mit dem spezifischen Modellverzeichnis
            # und expliziter GPU-Deaktivierung (oft stabiler in Bundles)
            logging.info(f"Initializing easyocr.Reader with model_storage_directory='{model_dir}', gpu=False") # Use logging
            print(f"Initialisiere easyocr.Reader mit model_storage_directory='{model_dir}', gpu=False")
            # Verwende die Sprachen, die du tatsächlich brauchst ('de', 'en' sind üblich)
            reader_easyocr = easyocr.Reader(['de', 'en'], gpu=False, model_storage_directory=model_dir)
            logging.info("EasyOCR Reader initialized successfully.") # Use logging
            print("EasyOCR Reader erfolgreich initialisiert.")

        except ImportError as ie:
             logging.error(f"Failed to import EasyOCR or a dependency: {ie}", exc_info=True) # Log with traceback
             print(f"FEHLER: EasyOCR oder eine Abhängigkeit konnte nicht importiert werden: {ie}")
             reader_easyocr = None # Sicherstellen, dass Reader None bleibt
        except Exception as e:
            # Logge den Fehler detailliert
            logging.error(f"Error during EasyOCR Reader initialization: {e}", exc_info=True) # Log with traceback
            print(f"FEHLER bei der Initialisierung des EasyOCR Readers: {e}")
            # Gib auch den Traceback im Terminal aus, falls sichtbar
            import traceback
            traceback.print_exc()
            reader_easyocr = None # Sicherstellen, dass Reader None bleibt
    # Gib den (möglicherweise neu initialisierten oder bereits existierenden) Reader zurück
    return reader_easyocr


###################################
###################################
def ocr_mit_easyocr(image_path):
    """
    Liest Text aus der angegebenen Bilddatei mittels EasyOCR.
    Enthält erweitertes Logging für Fehlersuche.

    Args:
        image_path (str): Der vollständige Pfad zur Bilddatei (z.B. .png, .jpg).

    Returns:
        list[str]: Eine Liste der von EasyOCR erkannten Textblöcke/Paragraphen (paragraph=True).
                   Gibt eine leere Liste ([]) zurück, wenn OCR erfolgreich war, aber keinen Text erkannt hat.
        None: Wenn ein Fehler auftritt.
    """
    function_name = "ocr_mit_easyocr"
    logging.info(f"--- Starting {function_name} for image: {image_path} ---")
    print(f"\n--- Start {function_name}() ---")
    ocr_result_text = None # Standard-Rückgabewert bei Fehlern

    # --- 1. Dynamische Imports ---
    try:
        # Module für Bildverarbeitung und OCR-Vorbereitung
        logging.debug(f"[{function_name}] Importing required modules (PIL, numpy)...")
        PIL_Image = importlib.import_module("PIL.Image") if "PIL.Image" not in sys.modules else sys.modules["PIL.Image"]
        numpy = importlib.import_module("numpy") if "numpy" not in sys.modules else sys.modules["numpy"]
        logging.debug(f"[{function_name}] Modules imported successfully.")
        # os ist global verfügbar
    except ImportError as e:
        logging.error(f"[{function_name}] Failed to import required module: {e}", exc_info=True)
        print(f"FEHLER [{function_name}]: Import eines benötigten Moduls fehlgeschlagen: {e}")
        return None # Kann ohne Module nicht arbeiten

    # --- 2. Eingabepfad prüfen ---
    if not isinstance(image_path, str) or not image_path:
        logging.error(f"[{function_name}] Invalid image path provided (not a string or empty). Path: {image_path}")
        print(f"FEHLER [{function_name}]: Ungültiger Pfad übergeben (kein String oder leer).")
        return None
    logging.debug(f"[{function_name}] Target file for OCR: {image_path}")
    print(f"[{function_name}] Zieldatei für OCR: {image_path}")

    # --- 3. Dateiexistenz prüfen ---
    # Use os.path.isfile for better clarity that we expect a file
    if not os.path.isfile(image_path):
        logging.error(f"[{function_name}] Image file not found or is not a file: {image_path}")
        print(f"FEHLER [{function_name}]: Bilddatei nicht gefunden oder ist kein File: {image_path}")
        return None

    # --- 4. Bild laden und vorbereiten ---
    try:
        logging.info(f"[{function_name}] Loading image file...")
        print(f"[{function_name}] Lade Bilddatei...")
        image = PIL_Image.open(image_path)
        logging.info(f"[{function_name}] Image loaded successfully.")
        print(f"[{function_name}] Bild erfolgreich geladen.")

        logging.info(f"[{function_name}] Converting image to RGB NumPy Array for EasyOCR...")
        print(f"[{function_name}] Konvertiere Bild zu RGB NumPy Array für EasyOCR...")
        image_rgb = image.convert('RGB') # Stelle sicher, dass es RGB ist
        image_np = numpy.array(image_rgb)
        logging.info(f"[{function_name}] Conversion to NumPy array complete.")
        print(f"[{function_name}] Konvertierung abgeschlossen.")

    except FileNotFoundError:
        # Sollte durch os.path.isfile abgefangen sein, aber zur Sicherheit
        logging.error(f"[{function_name}] Image file not found after check (race condition?): {image_path}", exc_info=True)
        print(f"FEHLER [{function_name}]: Bilddatei wurde nach Prüfung nicht gefunden: {image_path}")
        return None
    except Exception as img_err: # Catch more specific PIL/IO errors if possible
        logging.error(f"[{function_name}] Error loading or preparing image '{os.path.basename(image_path)}': {img_err}", exc_info=True)
        print(f"FEHLER [{function_name}] beim Laden oder Vorbereiten von Bild '{os.path.basename(image_path)}': {img_err}")
        return None

    # --- 5. EasyOCR Reader holen ---
    try:
        logging.info(f"[{function_name}] Getting EasyOCR Reader instance...")
        print(f"[{function_name}] Hole EasyOCR Reader...")
        # Rufe die andere Funktion auf, die bereits Logging enthält
        reader = get_reader_easyocr()
        if reader is None:
            # get_reader_easyocr sollte bereits geloggt haben, warum es fehlschlug
            logging.error(f"[{function_name}] EasyOCR Reader is not available (initialization failed?). Aborting OCR.")
            print(f"FEHLER [{function_name}]: EasyOCR Reader ist nicht verfügbar (Initialisierung fehlgeschlagen?).")
            return None # Reader konnte nicht geholt werden
        logging.info(f"[{function_name}] EasyOCR Reader obtained successfully.")
        print(f"[{function_name}] EasyOCR Reader erhalten.")
    except Exception as reader_err:
        logging.error(f"[{function_name}] Unexpected error while getting EasyOCR Reader: {reader_err}", exc_info=True)
        print(f"FEHLER [{function_name}] beim Holen des EasyOCR Readers: {reader_err}")
        return None

    # --- 6. OCR durchführen ---
    try:
        logging.info(f"[{function_name}] Performing OCR with EasyOCR for '{os.path.basename(image_path)}' (paragraph=True)...")
        print(f"[{function_name}] Führe OCR mit EasyOCR durch für '{os.path.basename(image_path)}'...")
        # detail=0: Gibt nur den Text zurück (Liste von Strings)
        # paragraph=True: Versucht, zusammenhängende Zeilen als einen Eintrag zu erkennen
        raw_results = reader.readtext(image_np, detail=0, paragraph=True)
        logging.info(f"[{function_name}] EasyOCR raw result: {raw_results}")
        print(f"[{function_name}] EasyOCR Roh-Ergebnis:", raw_results)

    except Exception as ocr_err:
        # Fängt Fehler von reader.readtext() ab
        logging.error(f"[{function_name}] Error during OCR text recognition for '{os.path.basename(image_path)}': {ocr_err}", exc_info=True)
        print(f"FEHLER [{function_name}] während der Texterkennung (OCR) für '{os.path.basename(image_path)}': {ocr_err}")
        return None # Bei OCR-Fehler None zurückgeben

    # --- 7. Abschluss und Rückgabe ---
    if raw_results is not None:
        # Ensure it returns a list, even if empty
        final_result = raw_results if isinstance(raw_results, list) else []
        logging.info(f"--- {function_name}() completed successfully. Returning {len(final_result)} text blocks. ---")
        print(f"--- {function_name}() erfolgreich abgeschlossen. Ergebnis (Anzahl Blöcke: {len(final_result)}) wird zurückgegeben. ---")
        return final_result
    else:
        # Der 'None'-Fall wird bereits durch die return-Statements in den except-Blöcken behandelt
        logging.warning(f"--- {function_name}() likely finished with errors (raw_results is None). Returning None. ---")
        print(f"--- {function_name}() mit Fehlern abgeschlossen. Gibt None zurück. ---")
        return None # Explicitly return None on error path

###################################
###################################


def KISIM_im_vordergrund(prefix: str = "KISIM - ") -> bool:
    import ctypes
    from ctypes import wintypes
    """
    Sucht nach dem ersten sichtbaren Fenster, dessen Titel mit `prefix` beginnt,
    maximiert es und holt es in den Vordergrund.

    Verwendet AttachThreadInput, um SetForegroundWindow-Einschränkungen zu umgehen.

    Returns:
        True, falls das Fenster gefunden und aktiviert wurde, False sonst.
    """
    user32 = ctypes.WinDLL('user32', use_last_error=True)
    kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)

    SW_SHOWMAXIMIZED = 3

    # Definition der WinAPI-Funktionen und ihrer Argument-/Rückgabetypen
    # Das hilft ctypes bei der Typprüfung und stellt korrekte Aufrufe sicher.
    # KORRIGIERT: ctypes.WINFUNCTYPE statt wintypes.WINFUNCTYPE
    user32.EnumWindows.argtypes = [ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM), wintypes.LPARAM]
    user32.EnumWindows.restype = wintypes.BOOL

    user32.IsWindowVisible.argtypes = [wintypes.HWND]
    user32.IsWindowVisible.restype = wintypes.BOOL

    user32.GetWindowTextLengthW.argtypes = [wintypes.HWND]
    user32.GetWindowTextLengthW.restype = wintypes.INT

    user32.GetWindowTextW.argtypes = [wintypes.HWND, wintypes.LPWSTR, wintypes.INT]
    user32.GetWindowTextW.restype = wintypes.INT

    user32.ShowWindow.argtypes = [wintypes.HWND, wintypes.INT]
    user32.ShowWindow.restype = wintypes.BOOL

    user32.SetForegroundWindow.argtypes = [wintypes.HWND]
    user32.SetForegroundWindow.restype = wintypes.BOOL

    user32.GetForegroundWindow.restype = wintypes.HWND

    user32.GetWindowThreadProcessId.argtypes = [wintypes.HWND, wintypes.LPDWORD]
    user32.GetWindowThreadProcessId.restype = wintypes.DWORD

    kernel32.GetCurrentThreadId.restype = wintypes.DWORD

    user32.AttachThreadInput.argtypes = [wintypes.DWORD, wintypes.DWORD, wintypes.BOOL]
    user32.AttachThreadInput.restype = wintypes.BOOL

    # --- Fenster finden ---
    hwnd_container = {'hwnd': None}
    # Diese Zeile war schon korrekt und verwendet ctypes.WINFUNCTYPE
    EnumWindowsProc = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)

    def _enum_cb(hwnd, lParam, prefix=prefix):
        if user32.IsWindowVisible(hwnd):
            length = user32.GetWindowTextLengthW(hwnd)
            if length > 0:
                buf = ctypes.create_unicode_buffer(length + 1)
                user32.GetWindowTextW(hwnd, buf, length + 1)
                title = buf.value
                if title.startswith(prefix):
                    hwnd_container['hwnd'] = hwnd
                    return False
        return True

    user32.EnumWindows(EnumWindowsProc(_enum_cb), 0)

    hwnd = hwnd_container['hwnd']
    if not hwnd:
        print(f"Kein Fenster mit Präfix '{prefix}' gefunden.")
        return False

    # --- Fenster maximieren (falls nötig) ---
    user32.ShowWindow(hwnd, SW_SHOWMAXIMIZED)

    # --- Fenster in den Vordergrund bringen ---
    current_thread_id = kernel32.GetCurrentThreadId()
    target_thread_id = user32.GetWindowThreadProcessId(hwnd, None)

    foreground_hwnd = user32.GetForegroundWindow()
    foreground_thread_id = 0
    if foreground_hwnd:
        foreground_thread_id = user32.GetWindowThreadProcessId(foreground_hwnd, None)

    attached_to_target = False
    attached_to_foreground = False
    success = False

    try:
        if hwnd == foreground_hwnd:
            print("KISIM ist bereits im Vordergrund und maximiert.")
            return True

        if current_thread_id != target_thread_id:
            if user32.AttachThreadInput(current_thread_id, target_thread_id, True):
                attached_to_target = True
            else:
                error_code = ctypes.get_last_error()
                print(f"Warnung: Konnte unseren Thread nicht an den KISIM-Thread (ID: {target_thread_id}) anhängen. Fehler: {error_code} ({ctypes.FormatError(error_code)})")

            if foreground_thread_id and \
               foreground_thread_id != current_thread_id and \
               foreground_thread_id != target_thread_id:
                if user32.AttachThreadInput(current_thread_id, foreground_thread_id, True):
                    attached_to_foreground = True
                else:
                    error_code = ctypes.get_last_error()
                    print(f"Warnung: Konnte unseren Thread nicht an den Vordergrund-Thread (ID: {foreground_thread_id}) anhängen. Fehler: {error_code} ({ctypes.FormatError(error_code)})")

        success = user32.SetForegroundWindow(hwnd)
        if not success:
            error_code = ctypes.get_last_error()
            print(f"Warnung: SetForegroundWindow konnte nicht direkt ausgeführt werden. Fehler: {error_code} ({ctypes.FormatError(error_code)})")

    except Exception as e:
        print(f"Ein unerwarteter Fehler ist aufgetreten: {e}")
    finally:
        if attached_to_target:
            user32.AttachThreadInput(current_thread_id, target_thread_id, False)
        if attached_to_foreground:
            user32.AttachThreadInput(current_thread_id, foreground_thread_id, False)

    if not success:
        print(f"KISIM konnte nicht erfolgreich in den Vordergrund gebracht werden.")
        return False

    print("KISIM ist jetzt im Vordergrund und maximiert.")
    return True



###################################
###################################

def find_button(image_name, base_path = None, max_attempts=80, interval=0.05, confidence=0.8):
    """
    Sucht wiederholt nach einem Bild auf dem Bildschirm.

    Args:
        image_path (str): Der Name der Bilddatei.
        description (str, optional): Eine Beschreibung des Bildes für Log-Meldungen. Standard: "Bild".
        max_attempts (int, optional): Maximale Anzahl von Suchversuchen. Standard: 100.
        interval (float, optional): Wartezeit zwischen den Versuchen in Sekunden. Standard: 0.05.
        confidence (float, optional): Genauigkeitsschwelle für die Bilderkennung (0.0 bis 1.0). Standard: 0.8.

    Returns:
        bool: True, wenn das Bild innerhalb der Versuche gefunden wurde, sonst False.
    """
    # Prüfen, ob pyautogui geladen ist
    try:
        pyautogui = importlib.import_module("pyautogui") if "pyautogui" not in sys.modules else sys.modules["pyautogui"]
    except ImportError:
        print(f"FEHLER): Modul 'pyautogui' konnte nicht geladen werden.")
        return False # Funktion kann nicht ohne pyautogui ausgeführt werden

    if not base_path or not os.path.isdir(base_path): # Added check if base_path is a directory
        print(f"FEHLER: Ungültiger oder fehlender Screenshot-Basispfad angegeben: '{base_path}'")
        return False

    image_path = os.path.join(base_path, image_name)
    # Check if the image file itself exists before starting the loop

    if not os.path.isfile(image_path):
        print(f"FEHLER: Bilddatei nicht gefunden unter: '{image_path}'")
        return False

    print(f"Suche nach... Pfad: {image_path}")
    attempts = 0
    while attempts < max_attempts:
        try:
            location = pyautogui.locateOnScreen(image_path, confidence=confidence)

            if location:
                print(f"'{image_path}' gefunden bei {location}.")
                return True 

        except pyautogui.ImageNotFoundException:
            pass
        except Exception as e:
            print(f"Ein unerwarteter Fehler ist bei der Suche nach '{image_path}' aufgetreten (Versuch {attempts + 1}): {e}")
            pass

        # Zähler erhöhen und kurz warten
        attempts += 1
        time.sleep(interval)

    # Schleife beendet, ohne das Bild zu finden
    print(f"FEHLER: '{image_path}' konnte nach {max_attempts} Versuchen nicht gefunden werden. Pfad: '{image_path}'.")
    return False

###################################
###################################

def find_and_click_button(image_name, description="Button", base_path=None, max_attempts= 100, interval=0.05, confidence=0.8):
    # Check if pyautogui is loaded, handle import error if necessary
    try:
        pyautogui = importlib.import_module("pyautogui") if "pyautogui" not in sys.modules else sys.modules["pyautogui"]
    except ImportError:
        print(f"FEHLER ({description}): Modul 'pyautogui' konnte nicht geladen werden.")
        return False
    """
    Sucht wiederholt nach einem Bild auf dem Bildschirm und klickt darauf, wenn gefunden.
    Angepasste Version für UNIVERSAL.py, die einen Basispfad akzeptiert.

    Args:
        image_name (str): Der Dateiname des Bildes (ohne Pfad).
        description (str): Eine Beschreibung des Buttons für Log-Meldungen.
        base_path (str): Der Basispfad zum Screenshot-Verzeichnis. Mandatory.
        max_attempts (int): Maximale Anzahl von Suchversuchen.
        interval (float): Wartezeit zwischen den Versuchen in Sekunden.
        confidence (float): Genauigkeitsschwelle für die Bilderkennung.

    Returns:
        bool: True, wenn der Button gefunden und geklickt wurde, sonst False.
    """
    if not base_path or not os.path.isdir(base_path): # Added check if base_path is a directory
        print(f"FEHLER ({description}): Ungültiger oder fehlender Screenshot-Basispfad angegeben: '{base_path}'")
        return False

    image_path = os.path.join(base_path, image_name)
    # Check if the image file itself exists before starting the loop
    if not os.path.isfile(image_path):
        print(f"FEHLER ({description}): Bilddatei nicht gefunden unter: '{image_path}'")
        return False

    print(f"Suche nach '{description}' ({image_name})... Pfad: {image_path}")
    attempts = 0
    while attempts < max_attempts:
        try:
            # Verwende locateCenterOnScreen für direkte Koordinaten zum Klicken
            location = pyautogui.locateCenterOnScreen(image_path, confidence=confidence)
            if location:
                print(f"'{description}' gefunden bei {location}. Klicke...")
                pyautogui.click(location) # Click the identified center
                print(f"'{description}' geklickt.")
                return True
        except pyautogui.ImageNotFoundException:
            # Fehler wird nur am Ende gemeldet, wenn alle Versuche fehlschlagen
            pass
        except Exception as e:
            print(f"Ein unerwarteter Fehler ist bei der Suche/Klick nach '{description}' aufgetreten (Versuch {attempts + 1}): {e}")
            pass # Continue trying for now

        attempts += 1
        time.sleep(interval) # Kurze Pause zwischen den Suchversuchen bleibt

    print(f"Fehler: '{description}' ({image_name}) konnte nach {max_attempts} Versuchen nicht gefunden werden unter '{image_path}'.")
    return False

###################################
###################################


def find_and_click_button_offset(
    image_name, 
    base_path=None,
    clicks=1,            # Anzahl der Klicks (umbenannt von num_clicks)
    x_offset=0,
    y_offset=0,
    max_attempts=50,
    interval=0.05,
    confidence=0.9,
    rightclick=False,  # Neu: Option für Rechtsklick
):
    """
    Sucht wiederholt nach einem Bild anhand seines vollständigen Pfades und führt
    eine definierte Anzahl Klicks an einer Position mit x/y-Offset zum Zentrum
    des gefundenen Bildes aus.

    Args:
        image_path (str): Der vollständige, absolute Pfad zur .png-Bilddatei.
        clicks (int): Die Anzahl der Klicks (1=einfach, 2=doppel, etc.). Standard=1.
        x_offset (int): Horizontaler Versatz zum Bildzentrum für den Klick.
        y_offset (int): Vertikaler Versatz zum Bildzentrum (positiv = nach unten).
        max_attempts (int): Maximale Anzahl von Suchversuchen.
        interval (float): Wartezeit zwischen den Versuchen in Sekunden.
        confidence (float): Genauigkeitsschwelle für die Bilderkennung.
        rightclick (bool): Wenn True, wird ein Rechtsklick statt eines Linksklicks ausgeführt.

    Returns:
        bool: True, wenn das Bild gefunden und der Offset-Klick ausgeführt wurde, sonst False.
    """
    try:
        pyautogui = importlib.import_module("pyautogui") if "pyautogui" not in sys.modules else sys.modules["pyautogui"]

        # Direkte Prüfung des übergebenen Pfades
        image_path = os.path.join(base_path, image_name) if base_path else image_name
        if not image_path or not isinstance(image_path, str):
            print(f"FEHLER (find_and_click_offset): Ungültiger 'image_path' übergeben: {image_path}")
            return False
        if not os.path.isfile(image_path):
            print(f"FEHLER (find_and_click_offset): Bilddatei nicht gefunden unter: '{image_path}'")
            return False

        # Bestimme die Beschreibung für den Klick-Typ
        click_desc = f"{clicks}-fach Klick"
        if clicks == 1:
            click_desc = "Einfachklick"
        elif clicks == 2:
            click_desc = "Doppelklick"
        elif clicks == 3:
             click_desc = "Dreifachklick"

        # Verwende den Dateinamen für generische Log-Meldungen
        image_filename = os.path.basename(image_path)
        print(f"Suche nach '{image_filename}' für Offset-{click_desc}... Pfad: {image_path}")

    except ImportError:
        print(f"FEHLER (find_and_click_offset): Modul 'pyautogui' konnte nicht geladen werden.")
        return False
    except Exception as e:
         print(f"FEHLER (find_and_click_offset): Initialisierung fehlgeschlagen - {e}")
         return False

    attempts = 0
    while attempts < max_attempts:
        try:
            # Finde das Zentrum des Bildes mit dem direkten Pfad
            location = pyautogui.locateCenterOnScreen(image_path, confidence=confidence)

            if location:
                # Berechne die Zielkoordinaten für den Klick
                target_x = location.x + x_offset
                target_y = location.y + y_offset

                print(f"'{image_filename}' gefunden bei {location}.")
                print(f"Führe {click_desc} aus bei Offset-Position ({target_x}, {target_y})...")

                # Führe die Klicks aus
                if rightclick:
                    pyautogui.rightClick(x=target_x, y=target_y, interval=0.1)
                else:
                    # Standard-Linksklick
                    pyautogui.click(x=target_x, y=target_y, clicks=clicks, interval=0.1)

                print(f"'{image_filename}' -> Offset-{click_desc} ausgeführt.")
                return True # Erfolg

            # Wenn nicht gefunden, warte kurz und versuche es erneut
            attempts += 1
            if attempts < max_attempts:
                 time.sleep(interval)

        except pyautogui.ImageNotFoundException:
            attempts += 1
            if attempts < max_attempts:
                time.sleep(interval)
        except Exception as e:
            print(f"FEHLER (find_and_click_offset): Unerwarteter Fehler bei Versuch {attempts + 1} bei Suche/Klick auf '{image_filename}': {e}")
            attempts += 1
            if attempts < max_attempts:
                 time.sleep(interval)

    # Wenn die Schleife ohne Erfolg endet
    print(f"FEHLER (find_and_click_offset): '{image_filename}' konnte nach {max_attempts} Versuchen nicht gefunden werden. Offset-{click_desc} nicht ausgeführt.")
    return False

###################################
###################################

#Hier Definition der Bereichsnavigation in KISIM


# --- Überarbeitete Navigationsfunktionen ---

def _navigiere_bereich_template(bereich_name):
    """
    Interne Template-Funktion für die Navigation. Nicht direkt aufrufen.

    Args:
        bereich_name (str): Der Name des Bereichs (z.B. "Dashboard", "Stammdaten").
                            Wird für Logging und Dateinamen verwendet.

    Returns:
        bool: True bei erfolgreicher Navigation, False bei Fehler oder Timeout.
    """
    # ---- Dynamisches Laden der benötigten Module ----
    try:
        pyautogui = importlib.import_module("pyautogui") if "pyautogui" not in sys.modules else sys.modules["pyautogui"]
        time = importlib.import_module("time") if "time" not in sys.modules else sys.modules["time"]
        # os wird für basename und join benötigt, Import sicherstellen
        os_module = importlib.import_module("os") if "os" not in sys.modules else sys.modules["os"]
    except ImportError as e:
        print(f"FEHLER [navigiere_bereich_{bereich_name.lower()}]: Import fehlgeschlagen: {e}")
        return False # Kann ohne Module nicht arbeiten

    print(f"\nStart navigiere_bereich_{bereich_name.lower()}()")
    max_attempts = 100  # Ca. 5 Sekunden Timeout (100 * 0.05s)
    sleep_interval = 0.05

    # Pfade zu den Bildern konstruieren - Verwende screenshots_dir
    try:
        confirm_image_filename = f'button_bereich_{bereich_name.lower()}_confirm.png'
        nav_image_filename = f'button_bereich_{bereich_name.lower()}.png'
        # Pfad relativ zum screenshots_dir bauen
        bereich_screenshot_path = os_module.path.join(screenshots_dir, 'UNIVERSAL', 'bereiche')
        confirm_image_path = os_module.path.join(bereich_screenshot_path, confirm_image_filename)
        nav_image_path = os_module.path.join(bereich_screenshot_path, nav_image_filename)


        # Überprüfen, ob die Bilddateien existieren (optional, aber hilfreich für Debugging)
        if not os_module.path.exists(confirm_image_path):
            print(f"WARNUNG: Bestätigungsbild nicht gefunden: {confirm_image_path}")
            # Hier könnte man False zurückgeben oder weitermachen und auf pyautogui hoffen
        if not os_module.path.exists(nav_image_path):
            print(f"WARNUNG: Navigationsbild nicht gefunden: {nav_image_path}")

    except Exception as e:
        print(f"FEHLER [navigiere_bereich_{bereich_name.lower()}]: Fehler beim Erstellen der Bildpfade: {e}")
        return False

    # ---- 1. Prüfen, ob bereits im Zielbereich ----
    try:
        print(f"Prüfe, ob bereits im Bereich '{bereich_name}'...")
        if pyautogui.locateOnScreen(confirm_image_path, confidence=0.8):
            print(f"Bereits im Bereich '{bereich_name}'. Navigation erfolgreich.")
            return True
        else:
            print(f"Nicht im Bereich '{bereich_name}'. Starte Navigation...")
    except pyautogui.PyAutoGUIException as e:
        print(f"WARNUNG [navigiere_bereich_{bereich_name.lower()}]: Fehler bei initialer Prüfung auf '{confirm_image_filename}': {e}. Versuche trotzdem Navigation.")
    except Exception as e: # Andere Fehler (z.B. Pfad ungültig trotz vorheriger Prüfung)
         print(f"FEHLER [navigiere_bereich_{bereich_name.lower()}]: Unerwarteter Fehler bei initialer Prüfung: {e}")
         return False # Kritischer Fehler schon bei der Prüfung

    # ---- 2. Navigation initiieren (falls nicht schon im Zielbereich) ----
    nav_button_found_and_clicked = False
    print(f"Suche Navigationsbutton '{nav_image_filename}'...")
    for attempt in range(1, max_attempts + 1):
        try:
            nav_button_location = pyautogui.locateOnScreen(nav_image_path, confidence=0.8)
            if nav_button_location:
                button_center = pyautogui.center(nav_button_location)
                pyautogui.click(button_center)
                print(f"Navigationsbutton '{nav_image_filename}' gefunden und geklickt (Versuch {attempt}/{max_attempts}).")
                nav_button_found_and_clicked = True
                time.sleep(0.2) # Kurze Pause, damit UI nach Klick reagieren kann
                break # Erfolgreich geklickt, Navigationsschleife verlassen

        except pyautogui.PyAutoGUIException as e:
            # Check if it's specifically ImageNotFound; only log other errors verbosely
            if not isinstance(e, pyautogui.ImageNotFoundException):
                print(f"WARNUNG [navigiere_bereich_{bereich_name.lower()}]: Fehler bei Suche/Klick auf '{nav_image_filename}' (Versuch {attempt}): {e}")
            # Bei Fehler trotzdem weitermachen mit nächstem Versuch / sleep
        except Exception as e:
             print(f"FEHLER [navigiere_bereich_{bereich_name.lower()}]: Kritischer Fehler bei Navigation (Versuch {attempt}): {e}")
             return False # Bei unerwartetem Fehler abbrechen

        time.sleep(sleep_interval) # Warte kurz vor dem nächsten Versuch
    else:
        # Diese 'else'-Klausel gehört zum 'for'-Loop und wird ausgeführt, wenn die Schleife ohne 'break' endet
        print(f"FEHLER [navigiere_bereich_{bereich_name.lower()}]: Navigationsbutton '{nav_image_filename}' nach {max_attempts} Versuchen nicht gefunden (Timeout).")
        return False # Timeout bei der Suche nach dem Navigationsbutton

    # Sicherstellen, dass der Button wirklich geklickt wurde (sollte durch obige Logik abgedeckt sein)
    if not nav_button_found_and_clicked:
         print(f"FEHLER [navigiere_bereich_{bereich_name.lower()}]: Unerwarteter Zustand - Navigationsschleife beendet, ohne Button zu klicken.")
         return False

    # ---- 3. Bestätigen, dass Zielbereich geladen wurde ----
    print(f"Bestätige Erreichen des Bereichs '{bereich_name}' (Suche '{confirm_image_filename}')...")
    for attempt in range(1, max_attempts + 1):
        try:
            if pyautogui.locateOnScreen(confirm_image_path, confidence=0.8):
                print(f"Bereich '{bereich_name}' erfolgreich erreicht und bestätigt (Versuch {attempt}/{max_attempts}). Navigation erfolgreich.")
                return True 

        except pyautogui.PyAutoGUIException as e:
            # Check if it's specifically ImageNotFound; only log other errors verbosely
             if not isinstance(e, pyautogui.ImageNotFoundException):
                print(f"WARNUNG [navigiere_bereich_{bereich_name.lower()}]: Fehler bei Suche nach Bestätigung '{confirm_image_filename}' (Versuch {attempt}): {e}")
            # Weitermachen mit nächstem Versuch / sleep
        except Exception as e:
             print(f"FEHLER [navigiere_bereich_{bereich_name.lower()}]: Kritischer Fehler bei Bestätigung (Versuch {attempt}): {e}")
             return False # Bei unerwartetem Fehler abbrechen

        time.sleep(sleep_interval) # Warte kurz vor nächstem Versuch
    else:
        # Diese 'else'-Klausel gehört zum 'for'-Loop
        print(f"FEHLER [navigiere_bereich_{bereich_name.lower()}]: Bestätigungsbild '{confirm_image_filename}' nach {max_attempts} Versuchen nicht gefunden (Timeout). Navigation fehlgeschlagen.")
        return False # Timeout bei der Suche nach dem Bestätigungsbild


# --- Konkrete Navigationsfunktionen rufen das Template auf ---
# (Diese Funktionen bleiben unverändert, da sie nur das Template aufrufen)
def navigiere_bereich_dashboard(): return _navigiere_bereich_template("dashboard")
def navigiere_bereich_stammdaten(): return _navigiere_bereich_template("stammdaten")
def navigiere_bereich_leistungen(): return _navigiere_bereich_template("leistungen")
def navigiere_bereich_probleme(): return _navigiere_bereich_template("probleme")
def navigiere_bereich_workflows(): return _navigiere_bereich_template("workflows")
def navigiere_bereich_kurve(): return _navigiere_bereich_template("kurve")
def navigiere_bereich_pflegeprozess(): return _navigiere_bereich_template("pflegeprozess")
def navigiere_bereich_physioergo(): return _navigiere_bereich_template("physioergo")
def navigiere_bereich_pflegedok(): return _navigiere_bereich_template("pflegedok")
def navigiere_bereich_berichte(): return _navigiere_bereich_template("berichte")
def navigiere_bereich_einzelresultate(): return _navigiere_bereich_template("einzelresultate")
def navigiere_bereich_laborkumulativ(): return _navigiere_bereich_template("laborkumulativ")
def navigiere_bereich_bilder(): return _navigiere_bereich_template("bilder")
def navigiere_bereich_exttools(): return _navigiere_bereich_template("exttools")

########################################
########################################
#####ACHTUNG!
# in main.py: spi = UNIVERSAL.auslesen_spi()


def auslesen_spi():
    """
    Liest den SPI-Wert aus einem bestimmten Bildschirmbereich aus.

    Verwendet PyAutoGUI für Screenshots, PIL/Pillow für Bildverarbeitung
    und EasyOCR für die Texterkennung.

    Returns:
        str: Der gefundene SPI-Wert als String (z.B. "85 %"),
             "nicht gefunden" wenn OCR erfolgreich war, aber kein Wert erkannt wurde,
             "Fehler" wenn während des Prozesses ein Fehler auftrat.
    """
    # Standard-Rückgabewert im Fehlerfall
    spi_default_error = "Fehler"
    spi = spi_default_error # Initialisiere mit Fehlerstatus

    # ---- Dynamisches Laden der benötigten Module ----
    try:
        # Stelle sicher, dass os importiert ist für Pfadoperationen
        os = importlib.import_module("os") if "os" not in sys.modules else sys.modules["os"]
        pyautogui = importlib.import_module("pyautogui") if "pyautogui" not in sys.modules else sys.modules["pyautogui"]
        PIL_Image = importlib.import_module("PIL.Image") if "PIL.Image" not in sys.modules else sys.modules["PIL.Image"]
        PIL_ImageEnhance = importlib.import_module("PIL.ImageEnhance") if "PIL.ImageEnhance" not in sys.modules else sys.modules["PIL.ImageEnhance"]
        numpy = importlib.import_module("numpy") if "numpy" not in sys.modules else sys.modules["numpy"]
        re = importlib.import_module("re") if "re" not in sys.modules else sys.modules["re"]
        
    except ImportError as e:
        print(f"Fehler beim Importieren eines benötigten Moduls: {e}")
        return spi_default_error # Rückgabe Fehlerstatus

    print("\nStart auslesen_spi()")

    base_path = os.path.join(screenshots_dir, "UNIVERSAL", "image_preprocessing")
    screenshot_filename = "screenshot_spi.png"
    preprocessed_filename = "screenshot_spi_preprocessed.png"
    screenshot_fullpath = os.path.join(base_path, screenshot_filename)
    preprocessed_fullpath = os.path.join(base_path, preprocessed_filename)

    #Zuerst Navigation in Pflegeleistung
    if not navigiere_bereich_pflegeprozess(): print('Navigation in Bereich pflegeprozess nach 100 Versuchen fehlgeschlagen. Bitte sicherstellen, dass KISIM im Vollbildmodus auf dem Hauptbildschirmoffen ist und erneut versuchen. Programm abgebrochen.'); sys.exit()
    # ---- Screenshot aufnehmen und speichern ----
    try:
        ausschnitt_spi = (113, 119, 20, 13) # Feste Koordinaten
        screenshot_spi = pyautogui.screenshot(region=ausschnitt_spi)

        # Stelle sicher, dass das Verzeichnis existiert
        os.makedirs(base_path, exist_ok=True)

        screenshot_spi.save(screenshot_fullpath)
        print(rf"Screenshot für SPI gespeichert unter: {screenshot_fullpath}")

    except (pyautogui.PyAutoGUIException, OSError, IOError, Exception) as e:
        # Fange PyAutoGUI-Fehler, OS/IO-Fehler (Speichern/Verzeichnis) und andere Ausnahmen ab
        print(f"FEHLER beim Erstellen/Speichern des Screenshots: {e}")
        return spi_default_error # Rückgabe Fehlerstatus

    # ---- Bild laden und Vorverarbeitung ----
    try:
        # Lade das gerade gespeicherte Bild
        img_to_process = PIL_Image.open(screenshot_fullpath)

        # Konvertierungen und Verbesserungen
        screenshot_spi_preprocessed = img_to_process.convert('L')
        screenshot_spi_preprocessed = PIL_ImageEnhance.Contrast(screenshot_spi_preprocessed).enhance(2.0)
        screenshot_spi_preprocessed = screenshot_spi_preprocessed.point(lambda x: 0 if x < 150 else 255, 'L')

        # Skalierung
        scale_factor = 6
        width, height = screenshot_spi_preprocessed.size
        screenshot_spi_preprocessed = screenshot_spi_preprocessed.resize(
            (width * scale_factor, height * scale_factor),
            PIL_Image.Resampling.LANCZOS # Verwende PIL Enum für Resampling
        )

        # Zurück zu RGB für EasyOCR
        screenshot_spi_preprocessed = screenshot_spi_preprocessed.convert('RGB')

        # Speichern des vorverarbeiteten Bildes (optional, gut für Debugging)
        screenshot_spi_preprocessed.save(preprocessed_fullpath)
        print(rf"Vorverarbeitetes Bild gespeichert unter: {preprocessed_fullpath}. Verarbeite mit numpy.")

        # Konvertiere zu NumPy Array für EasyOCR
        screenshot_spi_preprocessed_numpy = numpy.array(screenshot_spi_preprocessed)

    except FileNotFoundError:
        print(f"FEHLER: Screenshot-Datei '{screenshot_fullpath}' nicht gefunden zum Laden.")
        return spi_default_error
    except (PIL_Image.UnidentifiedImageError, IOError, OSError, ValueError, Exception) as e:
        # Fange Pillow-Fehler (Öffnen, Verarbeiten), OS/IO (Speichern preprocessed) und andere Ausnahmen ab
        print(f"FEHLER bei der Bildverarbeitung: {e}")
        return spi_default_error

    # ---- OCR und Extraktion ----
    try:
        # Hole EasyOCR Reader (angenommen, get_reader_easyocr behandelt Fehler intern oder gibt None/Exception)
        reader = get_reader_easyocr()
        if reader is None:
             print("FEHLER: Konnte EasyOCR Reader nicht initialisieren.")
             return spi_default_error

        # Führe OCR durch
        easyocr_results = reader.readtext(screenshot_spi_preprocessed_numpy, detail=0)
        print(rf"EasyOCR Ergebnis: {easyocr_results}")

        # --- Extraktion (nur wenn OCR erfolgreich war) ---
        spi = "" 
        for result in easyocr_results:
            # Suche nach Zahl 0-100
            spi_match = re.search(r'\b([1-9]?[0-9]|100)\b', str(result))
            if spi_match:
                spi_value = spi_match.group(1)
                if spi_value.isdigit():
                     spi = f"{spi_value} %" # Erfolgreich gefunden und extrahiert
                     print(f"Gültiger SPI-Wert gefunden: {spi}")
                     break # Nimm den ersten gültigen Treffer
                else:
                     print(f"Ungültiger Treffer (keine Zahl nach Regex-Match) übersprungen: {result}")

    except Exception as e:
        # Fange alle möglichen Fehler von get_reader_easyocr() oder reader.readtext() ab
        print(f"FEHLER während OCR oder Extraktion: {e}")
        spi = spi_default_error # Setze zurück auf Fehlerstatus

    # ---- Finaler Rückgabewert ----
    if spi == spi_default_error:
        print(rf"Funktion auslesen_spi() beendet mit Fehler.")
    elif spi == "nicht gefunden":
        print(rf"Funktion auslesen_spi() beendet, kein SPI-Wert im Text gefunden.")
    else:
        print(rf"Funktion auslesen_spi() erfolgreich beendet. Global variable 'spi' (im UNIVERSAL Modul) wurde gesetzt und Wert wird zurückgegeben: spi = {spi}")

    # WICHTIG: Die globale Variable 'spi' im UNIVERSAL Modul wird hier nicht mehr explizit gesetzt.
    # Die aufrufende Funktion (z.B. in main.py) sollte den *Rückgabewert* dieser Funktion verwenden: spi = UNIVERSAL.auslesen_spi()
    return spi

###################################
###################################

###################################
###################################
###ACHTUNG!
#in main.py: rea, ips = UNIVERSAL.auslesen_reaips()


def auslesen_reaips():
    """
    Liest die REA- und IPS-Status ("Ja" oder "Nein") aus einem
    definierten Bildschirmbereich aus.

    Verwendet PyAutoGUI, PIL/Pillow und EasyOCR.

    Returns:
        tuple: Ein Tupel (rea, ips) mit den erkannten Werten als Strings.
               Mögliche Werte für rea und ips sind "Ja", "Nein",
               "nicht gefunden" (wenn OCR lief, aber kein Muster passte),
               oder "Fehler" (wenn ein Fehler im Prozess auftrat).
               Beispiel: ("Ja", "Nein"), ("nicht gefunden", "Fehler")
    """
    # Standard-Rückgabewerte definieren
    rea = ""
    ips = ""

    # ---- Dynamisches Laden der benötigten Module ----
    try:
        os = importlib.import_module("os") if "os" not in sys.modules else sys.modules["os"]
        pyautogui = importlib.import_module("pyautogui") if "pyautogui" not in sys.modules else sys.modules["pyautogui"]
        PIL_Image = importlib.import_module("PIL.Image") if "PIL.Image" not in sys.modules else sys.modules["PIL.Image"]
        PIL_ImageEnhance = importlib.import_module("PIL.ImageEnhance") if "PIL.ImageEnhance" not in sys.modules else sys.modules["PIL.ImageEnhance"]
        numpy = importlib.import_module("numpy") if "numpy" not in sys.modules else sys.modules["numpy"]
        re = importlib.import_module("re") if "re" not in sys.modules else sys.modules["re"]
    except ImportError as e:
        print(f"FEHLER [auslesen_reaips]: Import eines benötigten Moduls fehlgeschlagen: {e}")
        return False, False

    print("\nStart auslesen_reaips()")

    #Check, ob bereits in Kurve, wenn nicht, dann dahin navigieren
    if not navigiere_bereich_kurve(): print('Navigation in Bereich kurve nach 100 Versuchen fehlgeschlagen. Bitte sicherstellen, dass KISIM im Vollbildmodus auf dem Hauptbildschirmoffen ist und erneut versuchen. Programm abgebrochen.'); sys.exit()


    # Pfade definieren (konsistent mit auslesen_spi) - Verwende screenshots_dir
    base_path = os.path.join(screenshots_dir, "UNIVERSAL", "image_preprocessing")
    screenshot_filename = "screenshot_reaips.png"
    preprocessed_filename = "screenshot_reaips_preprocessed.png"
    screenshot_fullpath = os.path.join(base_path, screenshot_filename)
    preprocessed_fullpath = os.path.join(base_path, preprocessed_filename)


    # ---- Gesamtablauf in einem try-Block für generelle Fehler ----
    try:
        # ---- Screenshot aufnehmen und speichern ----
        try:
            ausschnitt_reaips = (45, 142, 155, 20) # Feste Koordinaten
            screenshot = pyautogui.screenshot(region=ausschnitt_reaips)
            os.makedirs(base_path, exist_ok=True) # Verzeichnis sicherstellen
            screenshot.save(screenshot_fullpath)
            print(f"Screenshot für REA/IPS gespeichert unter: {screenshot_fullpath}")
        except (pyautogui.PyAutoGUIException, OSError, IOError, Exception) as e:
            print(f"FEHLER [auslesen_reaips]: Erstellen/Speichern des Screenshots fehlgeschlagen: {e}")
            raise RuntimeError("Screenshot-Fehler") from e # Fehler nach außen geben für Haupt-try-Block

        # ---- Bild laden und Vorverarbeitung ----
        try:
            image = PIL_Image.open(screenshot_fullpath)
            # Dieselbe Vorverarbeitung wie im Original (und ähnlich zu auslesen_spi)
            image_proc = image.convert('L')
            image_proc = PIL_ImageEnhance.Contrast(image_proc).enhance(2.0)
            image_proc = image_proc.point(lambda x: 0 if x < 150 else 255, 'L')
            scale_factor = 6
            width, height = image_proc.size
            image_proc = image_proc.resize(
                (width * scale_factor, height * scale_factor),
                PIL_Image.Resampling.LANCZOS # Verwende Resampling Enum
            )
            image_proc = image_proc.convert('RGB') # Für EasyOCR
            image_proc.save(preprocessed_fullpath) # Speichere vorverarbeitetes Bild
            print(f"Vorverarbeitetes Bild gespeichert unter: {preprocessed_fullpath}")

            # Konvertiere zu NumPy Array
            image_np = numpy.array(image_proc)

        except FileNotFoundError:
            print(f"FEHLER [auslesen_reaips]: Screenshot-Datei '{screenshot_fullpath}' nicht gefunden zum Laden.")
            raise RuntimeError("Bildlade-Fehler")
        except (PIL_Image.UnidentifiedImageError, IOError, OSError, ValueError, Exception) as e:
            print(f"FEHLER [auslesen_reaips]: Bildverarbeitung fehlgeschlagen: {e}")
            raise RuntimeError("Bildverarbeitungs-Fehler") from e

        # ---- OCR und Extraktion ----
        try:
            reader = get_reader_easyocr() # Hole den Reader
            if reader is None:
                print("FEHLER [auslesen_reaips]: Konnte EasyOCR Reader nicht initialisieren.")
                raise RuntimeError("EasyOCR Reader Fehler")

            # Führe OCR durch ('de' wird von get_reader_easyocr angenommen)
            results = reader.readtext(image_np, detail=0)
            print(f"EasyOCR Ergebnis für REA/IPS: {results}")

            text = " ".join(results) # Füge alle erkannten Teile zusammen
            print(f"Zusammengefügter OCR-Text: '{text}'")

            # Suche nach REA: Ja/Nein (Groß/Kleinschreibung ignorieren)
            rea_match = re.search(r'REA:\s*(Ja|Nein)', text, re.IGNORECASE)
            if rea_match:
                # Nimm das gefundene Wort ("Ja" oder "Nein") und formatiere es (erster Buchstabe groß)
                rea = rea_match.group(1).capitalize()
                print(f"REA Status gefunden: {rea}")

            # Suche nach IPS: Ja/Nein (Groß/Kleinschreibung ignorieren)
            ips_match = re.search(r'IPS:\s*(Ja|Nein)', text, re.IGNORECASE)
            if ips_match:
                # Nimm das gefundene Wort ("Ja" oder "Nein") und formatiere es
                ips = ips_match.group(1).capitalize()
                print(f"IPS Status gefunden: {ips}")

        except Exception as e:
            # Fange Fehler von get_reader_easyocr(), readtext() oder der Regex-Verarbeitung ab
            print(f"FEHLER [auslesen_reaips]: OCR oder Extraktion fehlgeschlagen: {e}")
            return False, False

    except RuntimeError as e:
        # Fängt die weitergereichten Fehler aus den inneren Blöcken
        print(f"Funktion auslesen_reaips() wird aufgrund eines vorherigen Fehlers ({e}) mit Status 'Fehler' beendet.")
        return False, False
    except Exception as e:
        # Fängt unerwartete Fehler im Hauptablauf
        print(f"Unerwarteter FEHLER [auslesen_reaips]: {e}")
        return False, False

    # ---- Finaler Status und Rückgabe ----
    print(f"Funktion auslesen_reaips() beendet. REA='{rea}', IPS='{ips}'")
    return rea, ips 

###################################
###################################

def auslesen_rt_start_ende():
    # ---- Dynamisches Laden der benötigten Module ----
    try:
        pyautogui = importlib.import_module("pyautogui") if "pyautogui" not in sys.modules else sys.modules["pyautogui"]
    except ImportError as e:
        print(f"FEHLER [auslesen_rt_start_ende]: Import eines benötigten Moduls fehlgeschlagen: {e}") # Funktion benannt
        return # Added return on import error

    navigiere_bereich_berichte()

    #button_extras.png - Verwende screenshots_dir und os.path.join
    button_extras_path = os.path.join(screenshots_dir, 'UNIVERSAL', 'bereich_berichte', 'button_extras.png')
    while True:
        try:
            button_extras = pyautogui.locateOnScreen(button_extras_path, confidence=0.8)
            if button_extras is not None:
                button_center = pyautogui.center(button_extras)
                pyautogui.click(button_center)
                print(f'button_extras.png ({button_extras_path}) angeklickt und while Loop unterbrochen')
                break
        except pyautogui.ImageNotFoundException:
            # Weniger verbose Log bei Nicht-Fund
            print(f'Warte auf button_extras.png ({button_extras_path})...')
            time.sleep(0.2) # Kleine Pause
            continue
        except Exception as e: # Catch other potential errors
            print(f"FEHLER beim Suchen/Klicken von button_extras.png: {e}")
            time.sleep(0.2)
            continue

    for _ in range(4):
        pyautogui.press('down')
    pyautogui.press('enter') #öffne Termine


###################################
###################################
#ACHTUNG: der Funktion muss ein argument path zum image zugespielt werden
#in main.py results_easyocr = UNIVERSAL.auslesen_easyocr(path)
# Diese Funktion nimmt einen Pfad entgegen, sie konstruiert keine relativen Pfade selbst.
# Daher ist hier KEINE ÄNDERUNG bezüglich user_dir etc. notwendig. Die aufrufende Funktion
# muss den korrekten (ggf. relativen) Pfad übergeben.


def bereich_berichte_click_in_OE():
    pyautogui = importlib.import_module("pyautogui") if "pyautogui" not in sys.modules else sys.modules["pyautogui"]
    #button_oe klicken - Verwende screenshots_dir und os.path.join
    button_oe_path = os.path.join(screenshots_dir, 'UNIVERSAL', 'bereich_berichte', 'button_oe.png')
    while True:
        try:
            button_oe = pyautogui.locateOnScreen(button_oe_path, confidence=0.8)
            if button_oe is not None:
                button_center = pyautogui.center(button_oe)
                pyautogui.click(button_center)
                print(f'button_oe.png ({button_oe_path}) angeklickt und while Loop unterbrochen')
                break
        except pyautogui.ImageNotFoundException:
            print(f'Warte auf button_oe.png ({button_oe_path})...')
            time.sleep(0.2)
            continue
        except Exception as e: # Catch other potential errors
            print(f"FEHLER beim Suchen/Klicken von button_oe.png: {e}")
            time.sleep(0.2)
            continue


###################################
###################################


def labor_oeffne_hadh():
    """
    Öffnet den HAD-H Dialog im Laborbereich.
    Verwendet find_and_click_button (die True/False zurückgibt) für Linksklicks.
    Implementiert eine spezielle Suchlogik für Button Verzeichnis / Confirm.
    Gibt True bei Erfolg zurück, False bei Fehlern.
    """
    try:
        # Module dynamisch laden oder aus Cache holen
        pyautogui = importlib.import_module("pyautogui") if "pyautogui" not in sys.modules else sys.modules["pyautogui"]
        # Prüfe, ob die globale Variable screenshots_dir existiert
        if 'screenshots_dir' not in globals() and 'screenshots_dir' not in locals():
             if '__main__' in sys.modules and hasattr(sys.modules['__main__'], 'screenshots_dir'):
                 screenshots_dir = sys.modules['__main__'].screenshots_dir
                 print("Info (labor_oeffne_hadh): 'screenshots_dir' aus __main__ übernommen.")
             else:
                 print("FEHLER (labor_oeffne_hadh): Globale Variable 'screenshots_dir' nicht definiert.")
                 return False
        else:
             screenshots_dir = globals().get('screenshots_dir') or locals().get('screenshots_dir')

    except ImportError:
        print("FEHLER (labor_oeffne_hadh): Modul 'pyautogui' konnte nicht geladen werden.")
        return False
    except NameError:
        print("FEHLER (labor_oeffne_hadh): Variable 'screenshots_dir' konnte nicht gefunden werden.")
        return False

    # Definiere Basispfad für die Screenshots dieser Funktion
    kurve_screenshots = os.path.join(screenshots_dir, 'UNIVERSAL', 'bereich_kurve')
    if not os.path.isdir(kurve_screenshots):
        print(f"FEHLER (labor_oeffne_hadh): Screenshot-Verzeichnis nicht gefunden: {kurve_screenshots}")
        return False

    print("Starte labor_oeffne_hadh...")

    # 1. Klicke Button "Neu"
    if not find_and_click_button('button_neu.png', 'Button Neu', base_path=kurve_screenshots, confidence=0.8):
        print("FEHLER (labor_oeffne_hadh): Konnte 'Button Neu' nicht finden oder klicken.")
        return False
    time.sleep(0.2) # Kurze Pause nach dem Klick auf Neu

    # 2. Suche und Klicke Button "Verzeichnis" oder "Verzeichnis Confirm"
    print("Suche nach 'Button Verzeichnis Confirm' oder 'Button Verzeichnis'...")
    verzeichnis_button_found = False
    max_verzeichnis_attempts = 50
    for attempt in range(max_verzeichnis_attempts):
        print(f"  Versuch {attempt + 1}/{max_verzeichnis_attempts}...")
        # Priorität 1: Suche nach Confirm-Button (kurzer Versuch)
        if find_and_click_button('button_verzeichnis_confirm.png',
                                 'Button Verzeichnis Confirm',
                                 base_path=kurve_screenshots,
                                 confidence=0.8,
                                 max_attempts=1, # Nur 1 Versuch pro Schleifendurchlauf
                                 interval=0.01):
            print("Info (labor_oeffne_hadh): 'Button Verzeichnis Confirm' gefunden und geklickt.")
            verzeichnis_button_found = True
            break # Erfolg, Schleife verlassen

        # Priorität 2: Suche nach normalem Verzeichnis-Button (kurzer Versuch)
        if find_and_click_button('button_verzeichnis.png',
                                 'Button Verzeichnis',
                                 base_path=kurve_screenshots,
                                 confidence=0.8,
                                 max_attempts=1, # Nur 1 Versuch pro Schleifendurchlauf
                                 interval=0.01):
            print("Info (labor_oeffne_hadh): 'Button Verzeichnis' gefunden und geklickt.")
            verzeichnis_button_found = True
            break # Erfolg, Schleife verlassen

        # Wenn keiner gefunden wurde, kurz warten
        print("  Keiner der Verzeichnis-Buttons in diesem Versuch gefunden.")
        time.sleep(0.05)

    # Nach der Schleife prüfen, ob einer der Buttons gefunden wurde
    if not verzeichnis_button_found:
        print(f"FEHLER (labor_oeffne_hadh): Konnte weder 'Button Verzeichnis Confirm' noch 'Button Verzeichnis' nach {max_verzeichnis_attempts} Versuchen finden.")
        return False
    # Kurze Pause nach dem Klick auf den Verzeichnis-Button
    time.sleep(0.2)

    # 3. Klicke Button "Suche X"
    if not find_and_click_button('button_suche_x.png', 'Button Suche X', base_path=kurve_screenshots, confidence=0.8):
        print("FEHLER (labor_oeffne_hadh): Konnte 'Button Suche X' nicht finden oder klicken.")
        return False
    time.sleep(0.1)

    # 4. Tippe Suchbegriff
    try:
        print("Tippe Suchbegriff 'had h'...")
        pyautogui.typewrite('had h', interval=0.05)
        print("Suchbegriff 'had h' eingegeben.")
        time.sleep(0.5) # Warte kurz auf Suchergebnisse
    except Exception as e:
        print(f"FEHLER (labor_oeffne_hadh) beim Tippen von 'had h': {e}")
        return False

    # 5. Klicke Button "had" (Suchergebnis)
    if not find_and_click_button('button_had.png', 'Button HAD (Suchergebnis)', base_path=kurve_screenshots, confidence=0.8):
        print("FEHLER (labor_oeffne_hadh): Konnte 'Button HAD (Suchergebnis)' nicht finden oder klicken.")
        return False

    print("labor_oeffne_hadh erfolgreich abgeschlossen.")
    return True

###################################
###################################

def laborhadh_ausfuellen(datum_labor):
    """
    Füllt den HAD-H Dialog aus und speichert.
    Verwendet find_and_click_button (die True/False zurückgibt) für Linksklicks.
    Führt Rechtsklick manuell aus.
    Gibt True bei Erfolg zurück, False bei Fehlern.

    Args:
        datum_labor (str): Das Datum im Format DD.MM.YYYY.
    """
    try:
        # Module dynamisch laden oder aus Cache holen
        pyautogui = importlib.import_module("pyautogui") if "pyautogui" not in sys.modules else sys.modules["pyautogui"]
        clipboard = importlib.import_module("clipboard") if "clipboard" not in sys.modules else sys.modules["clipboard"]

        # Prüfe, ob die globale Variable screenshots_dir existiert
        if 'screenshots_dir' not in globals() and 'screenshots_dir' not in locals():
             # Versuche, sie aus dem aufrufenden Modul zu bekommen
             if '__main__' in sys.modules and hasattr(sys.modules['__main__'], 'screenshots_dir'):
                 screenshots_dir = sys.modules['__main__'].screenshots_dir
                 print("Info: 'screenshots_dir' aus __main__ übernommen.")
             else:
                print("FEHLER (laborhadh_ausfuellen): Globale Variable 'screenshots_dir' nicht definiert.")
                return False
        else:
            # Hole sie aus dem globalen Scope, falls sie dort definiert ist
             screenshots_dir = globals().get('screenshots_dir') or locals().get('screenshots_dir')

    except ImportError:
        print("FEHLER (laborhadh_ausfuellen): Module 'pyautogui' oder 'clipboard' konnten nicht geladen werden.")
        return False
    except NameError:
        print("FEHLER (laborhadh_ausfuellen): Variable 'screenshots_dir' konnte nicht gefunden werden.")
        return False

    # Definiere Basispfad für die Screenshots dieser Funktion
    kurve_screenshots = os.path.join(screenshots_dir, 'UNIVERSAL', 'bereich_kurve')
    button_blau_had_path = os.path.join(kurve_screenshots, 'button_blau_had.png') # Pfad für manuelle Suche

    if not os.path.isdir(kurve_screenshots):
        print(f"FEHLER (laborhadh_ausfuellen): Screenshot-Verzeichnis nicht gefunden: {kurve_screenshots}")
        return False

    print(f"Starte laborhadh_ausfuellen mit Datum: {datum_labor}...")

    # 1. Rechtsklick auf "Button Blau HAD" (manuell, da Helferfunktion nicht geändert wird)
    print(f"Suche nach 'Button Blau HAD' für Rechtsklick... Pfad: {button_blau_had_path}")
    button_found = False
    max_attempts_right_click = 200 # Anzahl Versuche für Rechtsklick
    interval_right_click = 0.01   # Intervall für Rechtsklick-Suche
    attempts = 0
    location = None # Initialisieren
    while attempts < max_attempts_right_click:
        try:
            location = pyautogui.locateCenterOnScreen(button_blau_had_path, confidence=0.8)
            if location:
                print(f"'Button Blau HAD' gefunden bei {location}. Führe Rechtsklick aus...")
                pyautogui.rightClick(location)
                print("'Button Blau HAD' erfolgreich rechts geklickt.")
                button_found = True
                break # Erfolg, Schleife verlassen
        except pyautogui.ImageNotFoundException:
            # Einfach weiter versuchen, keine Nachricht bei jedem Versuch
            pass
        except Exception as e:
            print(f"FEHLER (laborhadh_ausfuellen): Unerwarteter Fehler bei Suche/Rechtsklick auf 'Button Blau HAD' (Versuch {attempts + 1}): {e}")
            # Hier könnten wir auch abbrechen: return False
            pass # Weiter versuchen

        attempts += 1
        time.sleep(interval_right_click) # Kurze Pause zwischen Versuchen

    if not button_found:
        print(f"FEHLER (laborhadh_ausfuellen): 'Button Blau HAD' ({button_blau_had_path}) konnte nach {max_attempts_right_click} Versuchen nicht gefunden werden für Rechtsklick.")
        return False

    # 2. Navigation und Eingabe von Datum und Zeit
    try:
        print("Navigiere und fülle Datum/Zeit aus...")
        time.sleep(0.1) # Etwas längere Pause nach Rechtsklick, Menü braucht ggf. Zeit
        for _ in range(4):
            pyautogui.hotkey('ctrl', 'tab')
        time.sleep(0.1)
        print(f"Füge Datum '{datum_labor}' ein...")
        clipboard.copy(datum_labor)
        pyautogui.hotkey('ctrl', 'v')
        print(f"Datum '{datum_labor}' eingefügt.")
        time.sleep(0.1)
        pyautogui.hotkey('ctrl', 'tab')
        time.sleep(0.05)
        pyautogui.hotkey('ctrl', 'tab')
        time.sleep(0.05)
        zeit = '07:00'
        print(f"Füge Zeit '{zeit}' ein...")
        clipboard.copy(zeit)
        pyautogui.hotkey('ctrl', 'v')
        print(f"Zeit '{zeit}' eingefügt.")
        time.sleep(0.1)
    except Exception as e:
        print(f"FEHLER (laborhadh_ausfuellen) bei der Navigation oder Eingabe von Datum/Zeit: {e}")
        return False

    # 3. Klicke Button "Haem5"
    if not find_and_click_button('button_haem5.png', 'Button Haem5', base_path=kurve_screenshots, confidence=0.8):
        print("FEHLER (laborhadh_ausfuellen): Konnte 'Button Haem5' nicht finden oder klicken.")
        return False

    # 4. Klicke Button "Speichern"
    if not find_and_click_button('button_speichern.png', 'Button Speichern', base_path=kurve_screenshots, confidence=0.8):
        print("FEHLER (laborhadh_ausfuellen): Konnte 'Button Speichern' nicht finden oder klicken.")
        return False

    print('laborhadh_ausfuellen erfolgreich abgeschlossen (HAD angemeldet und gespeichert).')
    return True



###################################
###################################
#ACHTUNG: man muss der Funktion die fallnummer passen

def KG_oeffnen_via_fallnummer(fallnummer):
    pyautogui = importlib.import_module("pyautogui") if "pyautogui" not in sys.modules else sys.modules["pyautogui"]
    clipboard = importlib.import_module("clipboard") if "clipboard" not in sys.modules else sys.modules["clipboard"]

    print(f"\nStart KG_offnen_via_fallnummer aus UNIVERSAL.py")

    # Define paths using os.path.join and screenshots_dir
    kisim_suche_path = os.path.join(screenshots_dir, 'UNIVERSAL', 'kisim_suche')
    bereiche_path = os.path.join(screenshots_dir, 'UNIVERSAL', 'bereiche')

    button_lupe_path = os.path.join(kisim_suche_path, 'button_lupe.png')
    confirm_path = os.path.join(kisim_suche_path, 'button_globale_suche_confirm.png')
    suche_path = os.path.join(kisim_suche_path, 'button_globale_suche.png')
    button_stammdaten_confirm_path = os.path.join(bereiche_path, 'button_bereich_stammdaten_confirm.png')
    button_kg_oeffnen_path = os.path.join(bereiche_path, 'button_KG_oeffnen.png')


    # --- Loop 1: button_lupe klicken ---
    print("\nStarting Loop 1: Looking for button_lupe...")
    loop1_counter = 0
    while True:
        loop1_counter += 1
        if loop1_counter > 30:
             print(f"ERROR: Loop 1 timed out looking for {button_lupe_path}")
             return
        try:
            button_lupe = pyautogui.locateOnScreen(button_lupe_path, confidence=0.8)
            # If found without exception:
            print(f'button_lupe.png found at {button_lupe}. Clicking...')
            button_center = pyautogui.center(button_lupe)
            pyautogui.click(button_center)
            print('button_lupe.png clicked. Loop 1 finished.')
            break
        except pyautogui.ImageNotFoundException:
            print(f'Loop 1: button_lupe.png not found (attempt {loop1_counter}) path: {button_lupe_path}')
            time.sleep(0.1) # Short pause
            continue
        except Exception as e:
             print(f"--- Unexpected Error during Lupe Search: {type(e).__name__} - {e} ---")
             return # Stop if lupe fails unexpectedly


    # --- Loop 2: button_globale_suche_confirm ODER button_globale_suche ---
    print("\nStarting Loop 2: Looking for globale_suche_confirm OR globale_suche button...")
    loop2_counter = 0
    while True:
        loop2_counter += 1
        if loop2_counter > 30: # Safety break
             print("ERROR: Loop 2 (global search) timed out after 30 tries.")
             return

        print(f"\nLoop 2 - Attempt {loop2_counter}")
        # Paths already defined above

        try:
            # --- Try finding CONFIRM button FIRST ---
            print(f"Attempting to find CONFIRM button: {confirm_path}")
            button_globale_suche_confirm = pyautogui.locateOnScreen(confirm_path, confidence=0.9)
            # If the above line succeeds without exception, the button was found
            print(f'button_globale_suche_confirm.png FOUND at {button_globale_suche_confirm}. Loop 2 finished.')
            break # Success, exit Loop 2

        except pyautogui.ImageNotFoundException:
            # --- CONFIRM button NOT found, now try the other SEARCH button ---
            print(f"CONFIRM button not found ({confirm_path}).")
            print(f"Attempting to find SEARCH button: {suche_path}")
            try:
                button_globale_suche = pyautogui.locateOnScreen(suche_path, confidence=0.9)
                # If this succeeds without exception, the second button was found
                print(f'button_globale_suche.png FOUND at {button_globale_suche}. Clicking...')
                button_center = pyautogui.center(button_globale_suche)
                pyautogui.click(button_center)
                print('button_globale_suche.png clicked. Loop 2 finished.')
                break # Success, exit Loop 2

            except pyautogui.ImageNotFoundException:
                # --- Neither CONFIRM nor SEARCH button was found in this iteration ---
                print(f"SEARCH button also not found ({suche_path}). Retrying loop.")
                time.sleep(0.1) # Short pause
                continue # Go to next iteration of the outer while loop

            except Exception as inner_e: # Catch unexpected errors for the *second* button search
                print(f"--- Unexpected Error searching for button_globale_suche: {type(inner_e).__name__} - {inner_e} ---")
                time.sleep(0.1)
                continue # Continue outer loop after inner error


        except Exception as outer_e: # Catch unexpected errors during the *first* (confirm) button search
            print(f"--- Unexpected Error searching for button_globale_suche_confirm: {type(outer_e).__name__} - {outer_e} ---")
            time.sleep(0.1)
            continue # Continue outer loop after outer error


    pyautogui.hotkey('ctrl', 'a')
    pyautogui.press('backspace')
    clipboard.copy(fallnummer)
    pyautogui.hotkey('ctrl', 'v')
    pyautogui.press('enter')
    time.sleep(0.1)
    pyautogui.press('enter')

    #Check, if KG offen
    while True:
        try:
            # Use the defined path variable
            button_bereich_stammdaten_confirm = pyautogui.locateOnScreen(button_stammdaten_confirm_path, confidence=0.8)
            if button_bereich_stammdaten_confirm is not None:
                print(f'button_bereich_stammdaten_confirm.png ({button_stammdaten_confirm_path}) gefunden, Fall geöffnet')
                break
        except pyautogui.ImageNotFoundException:
            print(f'button_bereich_stammdaten_confirm ({button_stammdaten_confirm_path}) not found. Try clicking button_KG_oeffnen')
            try:
                # Use the defined path variable
                button_KG_oeffnen = pyautogui.locateOnScreen(button_kg_oeffnen_path, confidence=0.8)
                if button_KG_oeffnen is not None:
                    button_center = pyautogui.center(button_KG_oeffnen)
                    pyautogui.click(button_center)
                    print(f'button_KG_oeffnen.png ({button_kg_oeffnen_path}) angeklickt')
                    time.sleep(0.5) # Give time for KG to potentially open after click
            except pyautogui.ImageNotFoundException:
                print(f"button_KG_oeffnen.png ({button_kg_oeffnen_path}) nicht gefunden, versuche button_bereich_stammdaten_confirm.png zu finden")
                time.sleep(0.2) # Pause before next check
                continue
            except Exception as e:
                print(f"FEHLER beim Suchen/Klicken von button_KG_oeffnen.png: {e}")
                time.sleep(0.2)
                continue
        except Exception as e:
            print(f"FEHLER beim Suchen von button_bereich_stammdaten_confirm.png: {e}")
            time.sleep(0.2)
            continue


###################################
###################################
#ACHTUNG: man muss der Funktion die patientennummer passen


def KG_oeffnen_via_patientennummer(patientennummer):
    pyautogui = importlib.import_module("pyautogui") if "pyautogui" not in sys.modules else sys.modules["pyautogui"]
    clipboard = importlib.import_module("clipboard") if "clipboard" not in sys.modules else sys.modules["clipboard"]

    print(f"\nStart KG_offnen_via_patientennummer aus UNIVERSAL.py")

    # Define paths using os.path.join and screenshots_dir (same as Fallnummer)
    kisim_suche_path = os.path.join(screenshots_dir, 'UNIVERSAL', 'kisim_suche')
    bereiche_path = os.path.join(screenshots_dir, 'UNIVERSAL', 'bereiche')

    button_lupe_path = os.path.join(kisim_suche_path, 'button_lupe.png')
    confirm_path = os.path.join(kisim_suche_path, 'button_globale_suche_confirm.png')
    suche_path = os.path.join(kisim_suche_path, 'button_globale_suche.png')
    button_stammdaten_confirm_path = os.path.join(bereiche_path, 'button_bereich_stammdaten_confirm.png')
    button_kg_oeffnen_path = os.path.join(bereiche_path, 'button_KG_oeffnen.png')


    # --- Loop 1: button_lupe klicken ---
    print("\nStarting Loop 1: Looking for button_lupe...")
    loop1_counter = 0
    while True:
        loop1_counter += 1
        if loop1_counter > 30:
             print(f"ERROR: Loop 1 timed out looking for {button_lupe_path}")
             return
        try:
            button_lupe = pyautogui.locateOnScreen(button_lupe_path, confidence=0.8)
            # If found without exception:
            print(f'button_lupe.png found at {button_lupe}. Clicking...')
            button_center = pyautogui.center(button_lupe)
            pyautogui.click(button_center)
            print('button_lupe.png clicked. Loop 1 finished.')
            break
        except pyautogui.ImageNotFoundException:
            print(f'Loop 1: button_lupe.png not found (attempt {loop1_counter}) path: {button_lupe_path}')
            time.sleep(0.1) # Short pause
            continue
        except Exception as e:
             print(f"--- Unexpected Error during Lupe Search: {type(e).__name__} - {e} ---")
             return # Stop if lupe fails unexpectedly


    # --- Loop 2: button_globale_suche_confirm ODER button_globale_suche ---
    print("\nStarting Loop 2: Looking for globale_suche_confirm OR globale_suche button...")
    loop2_counter = 0
    while True:
        loop2_counter += 1
        if loop2_counter > 30: # Safety break
             print("ERROR: Loop 2 (global search) timed out after 30 tries.")
             return

        print(f"\nLoop 2 - Attempt {loop2_counter}")
        # Paths already defined above

        try:
            # --- Try finding CONFIRM button FIRST ---
            print(f"Attempting to find CONFIRM button: {confirm_path}")
            button_globale_suche_confirm = pyautogui.locateOnScreen(confirm_path, confidence=0.9)
            # If the above line succeeds without exception, the button was found
            print(f'button_globale_suche_confirm.png FOUND at {button_globale_suche_confirm}. Loop 2 finished.')
            break # Success, exit Loop 2

        except pyautogui.ImageNotFoundException:
            # --- CONFIRM button NOT found, now try the other SEARCH button ---
            print(f"CONFIRM button not found ({confirm_path}).")
            print(f"Attempting to find SEARCH button: {suche_path}")
            try:
                button_globale_suche = pyautogui.locateOnScreen(suche_path, confidence=0.9)
                # If this succeeds without exception, the second button was found
                print(f'button_globale_suche.png FOUND at {button_globale_suche}. Clicking...')
                button_center = pyautogui.center(button_globale_suche)
                pyautogui.click(button_center)
                print('button_globale_suche.png clicked. Loop 2 finished.')
                break # Success, exit Loop 2

            except pyautogui.ImageNotFoundException:
                # --- Neither CONFIRM nor SEARCH button was found in this iteration ---
                print(f"SEARCH button also not found ({suche_path}). Retrying loop.")
                time.sleep(0.1) # Short pause
                continue # Go to next iteration of the outer while loop

            except Exception as inner_e: # Catch unexpected errors for the *second* button search
                print(f"--- Unexpected Error searching for button_globale_suche: {type(inner_e).__name__} - {inner_e} ---")
                time.sleep(0.1)
                continue # Continue outer loop after inner error


        except Exception as outer_e: # Catch unexpected errors during the *first* (confirm) button search
            print(f"--- Unexpected Error searching for button_globale_suche_confirm: {type(outer_e).__name__} - {outer_e} ---")
            time.sleep(0.1)
            continue # Continue outer loop after outer error


    pyautogui.hotkey('ctrl', 'a')
    pyautogui.press('backspace')
    clipboard.copy(patientennummer)
    pyautogui.hotkey('ctrl', 'v')
    pyautogui.press('enter')
    time.sleep(0.1)
    pyautogui.press('enter')

    #Check, if KG offen (same logic as Fallnummer)
    while True:
        try:
            # Use the defined path variable
            button_bereich_stammdaten_confirm = pyautogui.locateOnScreen(button_stammdaten_confirm_path, confidence=0.8)
            if button_bereich_stammdaten_confirm is not None:
                print(f'button_bereich_stammdaten_confirm.png ({button_stammdaten_confirm_path}) gefunden, Fall geöffnet')
                break
        except pyautogui.ImageNotFoundException:
            print(f'button_bereich_stammdaten_confirm ({button_stammdaten_confirm_path}) not found. Try clicking button_KG_oeffnen')
            try:
                # Use the defined path variable
                button_KG_oeffnen = pyautogui.locateOnScreen(button_kg_oeffnen_path, confidence=0.8)
                if button_KG_oeffnen is not None:
                    button_center = pyautogui.center(button_KG_oeffnen)
                    pyautogui.click(button_center)
                    print(f'button_KG_oeffnen.png ({button_kg_oeffnen_path}) angeklickt')
                    time.sleep(0.5) # Give time for KG to potentially open after click
            except pyautogui.ImageNotFoundException:
                print(f"button_KG_oeffnen.png ({button_kg_oeffnen_path}) nicht gefunden, versuche button_bereich_stammdaten_confirm.png zu finden")
                time.sleep(0.2) # Pause before next check
                continue
            except Exception as e:
                print(f"FEHLER beim Suchen/Klicken von button_KG_oeffnen.png: {e}")
                time.sleep(0.2)
                continue
        except Exception as e:
            print(f"FEHLER beim Suchen von button_bereich_stammdaten_confirm.png: {e}")
            time.sleep(0.2)
            continue


##############################################
##############################################

def KG_schliessen():
    pyautogui = importlib.import_module("pyautogui") if "pyautogui" not in sys.modules else sys.modules["pyautogui"]

    # Define paths using os.path.join and screenshots_dir
    kg_mgmt_path = os.path.join(screenshots_dir, 'UNIVERSAL', 'KG_management')
    button_kgschliessen_path = os.path.join(kg_mgmt_path, 'button_kgschliessen.png')
    button_keinekgoffen_path = os.path.join(kg_mgmt_path, 'button_keinekgoffen.png')

    pyautogui.rightClick(340, 34) # Fixed coordinates - keep as is unless they need to be dynamic
    # button_kgschliessen
    while True:
        try:
            button_kgschliessen = pyautogui.locateOnScreen(button_kgschliessen_path, confidence=0.8)
            if button_kgschliessen is not None:
                button_center = pyautogui.center(button_kgschliessen)
                pyautogui.click(button_center)
                print(f'button_kgschliessen.png ({button_kgschliessen_path}) angeklickt und while Loop unterbrochen')
                break
        except pyautogui.ImageNotFoundException:
            print(f'Warte auf button_kgschliessen.png ({button_kgschliessen_path})...')
            time.sleep(0.2)
            continue
        except Exception as e:
            print(f"FEHLER beim Suchen/Klicken von button_kgschliessen.png: {e}")
            time.sleep(0.2)
            continue


    # button_keinekgoffen
    while True:
        try:
            button_keinekgoffen = pyautogui.locateOnScreen(button_keinekgoffen_path, confidence=0.8)
            if button_keinekgoffen is not None:
                print(f'alle KGs geschlossen (Bestätigung: {button_keinekgoffen_path} gefunden)')
                break
        except pyautogui.ImageNotFoundException:
            print(f'Warte auf button_keinekgoffen.png ({button_keinekgoffen_path})...')
            time.sleep(0.2)
            continue
        except Exception as e:
            print(f"FEHLER beim Suchen von button_keinekgoffen.png: {e}")
            time.sleep(0.2)
            continue


##############################################
##############################################
###ACHTUNG!!!
# in main.py: nachname, vorname, geburtsdatum, alter, geschlecht, patientennummer, eintrittsdatum = UNIVERSAL.auslesen_patdata_KISIMzeile()


def auslesen_patdata_KISIMzeile():

    print(f"\nStart auslesen_patdata_KISIMzeile() aus UNIVERSAL.py")
    # dependency module laden
    try:
        # Dynamische Imports für alle benötigten Module außer os, sys, importlib
        pyautogui = importlib.import_module("pyautogui") if "pyautogui" not in sys.modules else sys.modules["pyautogui"]
        re = importlib.import_module("re") if "re" not in sys.modules else sys.modules["re"]
        PIL_Image = importlib.import_module("PIL.Image") if "PIL.Image" not in sys.modules else sys.modules["PIL.Image"]
        PIL_ImageEnhance = importlib.import_module("PIL.ImageEnhance") if "PIL.ImageEnhance" not in sys.modules else sys.modules["PIL.ImageEnhance"]
        PIL_ImageFilter = importlib.import_module("PIL.ImageFilter") if "PIL.ImageFilter" not in sys.modules else sys.modules["PIL.ImageFilter"]
        numpy = importlib.import_module("numpy") if "numpy" not in sys.modules else sys.modules["numpy"] # numpy jetzt hier dynamisch importiert
        # os, sys, importlib sind bereits global verfügbar
    except ImportError as e:
        print(f"FEHLER [auslesen_patdata_KISIMzeile]: Import fehlgeschlagen: {e}")
        # Rückgabe von None-Werten für alle erwarteten Variablen (jetzt 7)
        return None, None, None, None, None, None, None

    # Pfade definieren - Verwende screenshots_dir
    # Specific directories for screenshots related to patient data reading
    screenshot_patdata_dir = os.path.join(screenshots_dir, "patdata") # Dir to save the raw screenshot
    screenshot_preprocessing_dir = os.path.join(screenshots_dir, "UNIVERSAL", "image_preprocessing") # Dir to save the processed screenshot
    screenshot_path = os.path.join(screenshot_patdata_dir, "screenshot_patdata.png")
    preprocessed_path = os.path.join(screenshot_preprocessing_dir, "screenshot_patdata_preprocessed_from_function_patdata_KISIMzeile.png")


    # Initialisiere alle Rückgabewerte mit None
    nachname = None
    vorname = None
    geburtsdatum = None
    alter = None
    geschlecht = None
    patientennummer = None
    eintrittsdatum = None

    try:
        print("Starte Auslesen der KISIM-Basisdaten (obere Zeile)")
        ausschnitt = (46, 60, 1000, 20)

        # Verzeichnisse sicherstellen - Use the new directory variables
        os.makedirs(screenshot_patdata_dir, exist_ok=True)
        os.makedirs(screenshot_preprocessing_dir, exist_ok=True)


        screenshot_patdata = pyautogui.screenshot(region=ausschnitt)
        screenshot_patdata.save(screenshot_path)
        print(f"Screenshot gespeichert: {screenshot_path}")

        screenshot_patdata_img = PIL_Image.open(screenshot_path)

        # --- Bildverarbeitung ---
        width, height = screenshot_patdata_img.size
        screenshot_patdata_preprocessed_pil = screenshot_patdata_img.resize((width * 3, height * 3), PIL_Image.Resampling.LANCZOS)
        screenshot_patdata_preprocessed_pil = screenshot_patdata_preprocessed_pil.convert('L')
        screenshot_patdata_preprocessed_pil = PIL_ImageEnhance.Contrast(screenshot_patdata_preprocessed_pil).enhance(2)
        screenshot_patdata_preprocessed_pil = screenshot_patdata_preprocessed_pil.filter(PIL_ImageFilter.SHARPEN)
        screenshot_patdata_preprocessed_pil.save(preprocessed_path)
        print(f"Vorverarbeitetes Bild (Zoom 3x, Contrast, Sharpen) gespeichert: {preprocessed_path}")

        screenshot_patdata_preprocessed_rgb = screenshot_patdata_preprocessed_pil.convert('RGB')
        # Verwende die dynamisch importierte numpy Variable
        screenshot_patdata_preprocessed_numpy = numpy.array(screenshot_patdata_preprocessed_rgb)

        # --- OCR mit EasyOCR ---
        print("Starte OCR mit EasyOCR...")
        reader = get_reader_easyocr()
        if reader is None:
             raise RuntimeError("EasyOCR Reader konnte nicht initialisiert werden.")

        easyocr_results = reader.readtext(screenshot_patdata_preprocessed_numpy, detail=0, paragraph=False)
        print("OCR Output via EasyOCR:", easyocr_results)

        # --- Extraktion --- (Keine Pfadänderungen hier nötig)

        # Namen-Extraktion
        potential_names = []
        for block in easyocr_results:
            # Handle potential None or non-string blocks robustly
            if not isinstance(block, str): continue
            words_in_block = block.split()
            for word in words_in_block:
                cleaned_word = word.strip(',.()')
                # Check if cleaned_word is not empty before accessing index
                if cleaned_word and cleaned_word[0].isupper() and cleaned_word.isalpha():
                    potential_names.append(cleaned_word)

        if len(potential_names) >= 1:
            nachname = potential_names[0]
            print(f"Nachname gefunden: {nachname}")
        if len(potential_names) >= 2:
            vorname = potential_names[1]
            print(f"Vorname gefunden: {vorname}")

        # Zusammenfügen für Regex
        output = " ".join(filter(None, easyocr_results)) # Filter out None before joining
        output = output.strip().replace('\n', ' ').replace('\f', '')
        print(f"Zusammengefügter EasyOCR Output für Regex: '{output}'")

        # Daten-Extraktion (dd.mm.yyyy)
        date_pattern = r'\b(\d{2}\.\d{2}\.\d{4})\b'
        alle_daten = re.findall(date_pattern, output)
        print(f"Gefundene Daten (dd.mm.yyyy): {alle_daten}")

        if len(alle_daten) >= 1: # Adjusted logic slightly for clarity
            geburtsdatum = alle_daten[0]
            if len(alle_daten) > 1:
                eintrittsdatum = alle_daten[-1]
            else:
                eintrittsdatum = None # Explicitly None if only one date found
        else:
             geburtsdatum = None
             eintrittsdatum = None


        # Alter-Extraktion
        if geburtsdatum:
            # More robust regex, handling potential spaces/commas better
            alter_regex = re.escape(geburtsdatum) + r'.*?(\d{1,3})\s*,?\s*(?:Jahre|J)\b'
            alter_match = re.search(alter_regex, output, re.IGNORECASE)
            if alter_match:
                try: alter = int(alter_match.group(1))
                except ValueError: alter = None
            else:
                # Fallback if date context fails
                alter_match_general = re.search(r'\b(\d{1,3})\s*,?\s*(?:Jahre|J)\b', output, re.IGNORECASE)
                if alter_match_general:
                     try: alter = int(alter_match_general.group(1))
                     except ValueError: alter = None
                else:
                    alter = None # Ensure alter is None if no match
        else:
            alter = None # Ensure alter is None if no birthdate


        # Geschlecht-Extraktion
        # Make regex slightly more specific to common patterns like ", M" or " M," or "(M)"
        geschlecht_match = re.search(r'(?:,\s*|\(\s*|\b)([MW])\b(?:\s*,|\s*\))?', output)
        geschlecht = geschlecht_match.group(1) if geschlecht_match else None


        # Patientennummer-Extraktion (Robust approach)
        # Try finding number after gender first
        pat_nr_match = None
        if geschlecht:
             pat_nr_regex = rf'\b{re.escape(geschlecht)}\b\D*?(\d{{5,9}})\b' # Look for number after gender, skip non-digits
             pat_nr_match = re.search(pat_nr_regex, output)

        # If not found after gender, try finding a 5-9 digit number that isn't the age
        if not pat_nr_match:
             pat_nr_fallback = re.findall(r'\b(\d{5,9})\b', output) # Find all potential numbers
             if pat_nr_fallback:
                 # Filter out the number if it matches the detected age
                 age_str = str(alter) if alter is not None else "-1" # Use a string that won't match pat nr
                 possible_pat_nrs = [nr for nr in pat_nr_fallback if nr != age_str]
                 if possible_pat_nrs:
                      # Heuristic: Often the last long number is the patient number
                      patientennummer = possible_pat_nrs[-1]
                 else:
                      patientennummer = None
             else:
                 patientennummer = None # No fallback found
        else:
            patientennummer = pat_nr_match.group(1) # Use the match found after gender


    except (pyautogui.PyAutoGUIException, OSError, IOError, FileNotFoundError, PIL_Image.UnidentifiedImageError, RuntimeError, Exception) as e:
        print(f"FEHLER [auslesen_patdata_KISIMzeile]: Ein Fehler ist aufgetreten: {e}")
        # Ensure all variables are set to None on error
        nachname, vorname, geburtsdatum, alter, geschlecht, patientennummer, eintrittsdatum = (None,) * 7

    # Ausgabe der extrahierten Variablen
    print("\nFunktion hat folgende Variablen extrahiert:")
    print(f"nachname = {nachname}")
    print(f"vorname = {vorname}")
    print(f"geburtsdatum = {geburtsdatum}")
    print(f"alter = {alter}")
    print(f"geschlecht = {geschlecht}")
    print(f"patientennummer = {patientennummer}")
    print(f"eintrittsdatum = {eintrittsdatum}")
    print("\n")

    # Gib alle 7 extrahierten Variablen zurück
    return nachname, vorname, geburtsdatum, alter, geschlecht, patientennummer, eintrittsdatum


###################################
###################################

###################################
###################################
### TESSERACT-VERSION ZUM AUSLESEN DER PATIENTENDATEN-ZEILE

def auslesen_patdata_KISIMzeile_tesseract():
    """
    Liest Patientendaten (Name, Geburtsdatum, Alter, etc.) aus der oberen KISIM-Zeile.
    Diese Version verwendet Tesseract OCR anstelle von EasyOCR.

    Die Funktion führt folgende Schritte aus:
    1. Erstellt einen Screenshot eines definierten Bildschirmbereichs.
    2. Führt eine Bildvorverarbeitung durch (Skalierung, Kontrast, Schärfen), um die OCR-Qualität zu verbessern.
    3. Ruft die Funktion `run_tesseract_ocr_deutsch` auf, um Text aus dem Bild zu extrahieren.
    4. Analysiert den erkannten Text mit regulären Ausdrücken, um die einzelnen Datenfelder zu extrahieren.
    5. Gibt die extrahierten Daten als 7 separate Variablen zurück.

    Returns:
        tuple: Ein Tupel mit 7 Elementen in der Reihenfolge:
               (nachname, vorname, geburtsdatum, alter, geschlecht, patientennummer, eintrittsdatum).
               Jeder Wert ist ein String oder Integer, oder None, falls die Extraktion fehlschlug.
    """
    print(f"\nStart auslesen_patdata_KISIMzeile_tesseract() aus UNIVERSAL.py")
    # Dynamische Imports für alle benötigten Module
    try:
        pyautogui = importlib.import_module("pyautogui") if "pyautogui" not in sys.modules else sys.modules["pyautogui"]
        re = importlib.import_module("re") if "re" not in sys.modules else sys.modules["re"]
        PIL_Image = importlib.import_module("PIL.Image") if "PIL.Image" not in sys.modules else sys.modules["PIL.Image"]
        PIL_ImageEnhance = importlib.import_module("PIL.ImageEnhance") if "PIL.ImageEnhance" not in sys.modules else sys.modules["PIL.ImageEnhance"]
        PIL_ImageFilter = importlib.import_module("PIL.ImageFilter") if "PIL.ImageFilter" not in sys.modules else sys.modules["PIL.ImageFilter"]
    except ImportError as e:
        print(f"FEHLER [auslesen_patdata_KISIMzeile_tesseract]: Import fehlgeschlagen: {e}")
        return None, None, None, None, None, None, None

    # Pfade definieren - Verwende screenshots_dir
    screenshot_patdata_dir = os.path.join(screenshots_dir, "patdata")
    screenshot_preprocessing_dir = os.path.join(screenshots_dir, "UNIVERSAL", "image_preprocessing")
    # Eindeutige Dateinamen für die Tesseract-Version, um Konflikte zu vermeiden
    screenshot_path = os.path.join(screenshot_patdata_dir, "screenshot_patdata_tesseract.png")
    preprocessed_path = os.path.join(screenshot_preprocessing_dir, "screenshot_patdata_preprocessed_from_function_patdata_KISIMzeile_tesseract.png")

    # Initialisiere alle Rückgabewerte mit None
    nachname, vorname, geburtsdatum, alter, geschlecht, patientennummer, eintrittsdatum = (None,) * 7

    try:
        print("Starte Auslesen der KISIM-Basisdaten (obere Zeile) mit Tesseract.")
        ausschnitt = (46, 60, 1000, 20) # Derselbe Ausschnitt wie in der EasyOCR-Version

        # Verzeichnisse sicherstellen
        os.makedirs(screenshot_patdata_dir, exist_ok=True)
        os.makedirs(screenshot_preprocessing_dir, exist_ok=True)

        # --- Screenshot und Bildvorverarbeitung (identisch zur Originalfunktion) ---
        screenshot_patdata = pyautogui.screenshot(region=ausschnitt)
        screenshot_patdata.save(screenshot_path)
        print(f"Screenshot gespeichert: {screenshot_path}")

        screenshot_patdata_img = PIL_Image.open(screenshot_path)
        width, height = screenshot_patdata_img.size
        screenshot_patdata_preprocessed_pil = screenshot_patdata_img.resize((width * 3, height * 3), PIL_Image.Resampling.LANCZOS)
        screenshot_patdata_preprocessed_pil = screenshot_patdata_preprocessed_pil.convert('L')
        screenshot_patdata_preprocessed_pil = PIL_ImageEnhance.Contrast(screenshot_patdata_preprocessed_pil).enhance(2)
        screenshot_patdata_preprocessed_pil = screenshot_patdata_preprocessed_pil.filter(PIL_ImageFilter.SHARPEN)
        screenshot_patdata_preprocessed_pil.save(preprocessed_path)
        print(f"Vorverarbeitetes Bild (Zoom 3x, Contrast, Sharpen) gespeichert: {preprocessed_path}")

        # --- OCR mit Tesseract ---
        print("Starte OCR mit Tesseract...")
        # Rufe die bestehende Helper-Funktion auf, die den Pfad zum Bild benötigt
        ocr_text = run_tesseract_ocr_deutsch(preprocessed_path)

        if ocr_text is None:
            print("FEHLER: Tesseract OCR hat keinen Text zurückgegeben oder ist fehlgeschlagen.")
            # Beende die Funktion und gib None-Werte zurück
            return nachname, vorname, geburtsdatum, alter, geschlecht, patientennummer, eintrittsdatum

        # Bereinige den Output von Tesseract (kann manchmal unnötige Zeichen enthalten)
        output = ocr_text.strip().replace('\n', ' ').replace('\f', '')
        print(f"Zusammengefügter Tesseract Output für Regex: '{output}'")


        # --- Extraktion aus dem Tesseract-String ---

        # Namen-Extraktion (angepasste Logik für einen einzelnen String)
        # Findet alle Wörter, die mit einem Grossbuchstaben beginnen und nur aus Buchstaben bestehen.
        # Annahme: Nachname und Vorname sind die ersten beiden solchen Wörter.
        potential_names = re.findall(r'\b([A-ZÄÖÜ][a-zäöü]+(?:-[A-ZÄÖÜ][a-zäöü]+)?)\b', output)
        if len(potential_names) >= 1:
            nachname = potential_names[0]
            print(f"Nachname gefunden: {nachname}")
        if len(potential_names) >= 2:
            vorname = potential_names[1]
            print(f"Vorname gefunden: {vorname}")

        # Daten-Extraktion (dd.mm.yyyy) - Dieselbe Regex wie im Original
        date_pattern = r'\b(\d{2}\.\d{2}\.\d{4})\b'
        alle_daten = re.findall(date_pattern, output)
        print(f"Gefundene Daten (dd.mm.yyyy): {alle_daten}")
        if len(alle_daten) >= 1:
            geburtsdatum = alle_daten[0]
            if len(alle_daten) > 1:
                eintrittsdatum = alle_daten[-1] # Annahme: letztes Datum ist Eintrittsdatum
        # (Variablen bleiben None, wenn keine Daten gefunden werden)

        # Alter-Extraktion - Dieselbe Regex wie im Original
        if geburtsdatum:
            alter_regex = re.escape(geburtsdatum) + r'.*?(\d{1,3})\s*,?\s*(?:Jahre|J)\b'
            alter_match = re.search(alter_regex, output, re.IGNORECASE)
            if alter_match:
                try: alter = int(alter_match.group(1))
                except ValueError: alter = None
            else: # Fallback, falls Kontext fehlschlägt
                alter_match_general = re.search(r'\b(\d{1,3})\s*,?\s*(?:Jahre|J)\b', output, re.IGNORECASE)
                if alter_match_general:
                     try: alter = int(alter_match_general.group(1))
                     except ValueError: alter = None

        # Geschlecht-Extraktion - Dieselbe Regex wie im Original
        geschlecht_match = re.search(r'(?:,\s*|\(\s*|\b)([MW])\b(?:\s*,|\s*\))?', output)
        geschlecht = geschlecht_match.group(1) if geschlecht_match else None

        # Patientennummer-Extraktion - Dieselbe robuste Logik wie im Original
        pat_nr_match = None
        if geschlecht:
             pat_nr_regex = rf'\b{re.escape(geschlecht)}\b\D*?(\d{{5,9}})\b'
             pat_nr_match = re.search(pat_nr_regex, output)
        if not pat_nr_match:
             pat_nr_fallback = re.findall(r'\b(\d{5,9})\b', output)
             if pat_nr_fallback:
                 age_str = str(alter) if alter is not None else "-1"
                 possible_pat_nrs = [nr for nr in pat_nr_fallback if nr != age_str]
                 if possible_pat_nrs:
                      patientennummer = possible_pat_nrs[-1]
        else:
            patientennummer = pat_nr_match.group(1)

    except (pyautogui.PyAutoGUIException, OSError, IOError, FileNotFoundError, PIL_Image.UnidentifiedImageError, RuntimeError, Exception) as e:
        print(f"FEHLER [auslesen_patdata_KISIMzeile_tesseract]: Ein Fehler ist aufgetreten: {e}")
        # Stelle sicher, dass bei einem Fehler alle Variablen auf None zurückgesetzt werden
        nachname, vorname, geburtsdatum, alter, geschlecht, patientennummer, eintrittsdatum = (None,) * 7

    # Ausgabe der extrahierten Variablen (zur Überprüfung)
    print("\nFunktion hat folgende Variablen extrahiert (Tesseract-Version):")
    print(f"nachname = {nachname}")
    print(f"vorname = {vorname}")
    print(f"geburtsdatum = {geburtsdatum}")
    print(f"alter = {alter}")
    print(f"geschlecht = {geschlecht}")
    print(f"patientennummer = {patientennummer}")
    print(f"eintrittsdatum = {eintrittsdatum}")
    print("\n")

    # Gib alle 7 extrahierten Variablen zurück
    return nachname, vorname, geburtsdatum, alter, geschlecht, patientennummer, eintrittsdatum


###################################
###################################

def rt_konzept_oeffnen():
    function_name = "rt_konzept_oeffnen"
    logging.info(f"--- Starting {function_name} ---")
    print(f"\n--- Start {function_name}() ---")
    # Make imports local if not already loaded
    logging.debug(f"[{function_name}] Importing required modules (clipboard, pyautogui)...")
    clipboard = importlib.import_module("clipboard") if "clipboard" not in sys.modules else sys.modules["clipboard"]
    pyautogui = importlib.import_module("pyautogui") if "pyautogui" not in sys.modules else sys.modules["pyautogui"]
    logging.debug(f"[{function_name}] Modules imported successfully.")

    script_dir = os.path.dirname(os.path.abspath(__file__))
    berichte_path = os.path.join(script_dir, "screenshots pyautogui", "UNIVERSAL", "bereich_berichte")


    # --- Navigation und Texteingabe ---
    if not navigiere_bereich_berichte(): print('Navigation in Bereich Berichte nach 100 Versuchen fehlgeschlagen. Bitte sicherstellen, dass KISIM im Vollbildmodus auf dem Hauptbildschirmoffen ist und erneut versuchen. Programm abgebrochen.'); sys.exit()
    bereich_berichte_click_in_OE() 
    for _ in range(4):
        pyautogui.hotkey('ctrl', 'tab') #in Name
        time.sleep(0.1) # Kleine Pause hinzufügen
    rt_konzept = "rt-konzept"
    clipboard.copy(rt_konzept)
    time.sleep(0.3) # Pause vor dem Einfügen
    print("Paste rt-konzept...)")
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(0.5) # Pause nach dem Einfügen

    find_button("button_rtkonzept_confirm.png", base_path=berichte_path, max_attempts=100, interval=0.1, confidence=0.90)
                

    time.sleep(0.3)
    #Versuche, den Button "button_rtkonzept_confirm.png" zu finden und zu klicken
    if not find_button("button_rtkonzept_doppelt.png", base_path=berichte_path, max_attempts=25, interval=0.05, confidence=0.80): 
        print("button_rtkonzept_doppelt.png nicht gefunden, versuche setze Zeitraum zurück und versuche button_rtkonzept_doppelt_schwarz zu finden.png")
        #Zeitraum zurücksetzen und nach button_rtkonzept_doppelt_schwarz.png suchen
        if not find_and_click_button_offset("button_zeitraum_pfeil.png", base_path=berichte_path, max_attempts=20, interval=0.05, confidence=0.90, x_offset=-45):
            print("button_zeitraum_pfeil.png nicht gefunden")
            return False
        if not find_and_click_button("button_unbestimmt.png", base_path=berichte_path, max_attempts=100, interval=0.05, confidence=0.90):
            print("button_unbestimmt.png nicht gefunden")
            return False
        if not find_and_click_button_offset("button_rtkonzept_doppelt_schwarz.png", base_path=berichte_path, max_attempts=40, interval=0.05, confidence=0.80, clicks=2, y_offset=7):
            print("button_rtkonzept_doppelt_schwarz.png nicht gefunden; offset Klick fehlgeschlagen")
            return False
    else: # Wenn button_rtkonzept_doppelt.png gefunden wurde, versuche Offset-Klick
        time.sleep(0.2)
        print("button_rtkonzept_doppelt.png gefunden, versuche offset Klick")
        if not find_and_click_button_offset("button_rtkonzept_doppelt.png", base_path=berichte_path, max_attempts=20, interval=0.05, confidence=0.75, clicks=2, y_offset=7):
            print("button_rtkonzept_doppelt.png nicht gefunden; offset Klick fehlgeschlagen")
            return False

    if not find_button("button_rtkonzept_offen_confirm.png", base_path=berichte_path, max_attempts=150, interval=0.05, confidence=0.80):
        print("button_rtkonzept_offen_confirm.png nicht gefunden, Fehler beim Öffnen des RT-Konzepts")
        return False
    else:
        print("RT-Konzept erfolgreich geöffnet.")
        return True


###################################
###################################

def ctrl_tabs(anzahl):
    print(f"Starte {anzahl} ctrl_tabs")
    for _ in range(anzahl):
        pyautogui.hotkey('ctrl', 'tab')
    print("tabs erfolgreich ausgeführt")


###################################
###################################
# create_patdata_glossary: No path changes needed.
def create_patdata_glossary(geschlecht):
    """
    Erstellt ein Dictionary (Glossar) mit geschlechtsabhängigen Formulierungen
    für Arztbriefe basierend auf dem übergebenen Geschlecht. Enthält Artikel,
    Bezeichnung "Patient/in", Adjektivendung "-jährig", Personal- und
    Possessivpronomen.

    Args:
        geschlecht (str): Das Geschlecht des Patienten ('W' für weiblich,
                          'M' für männlich). Groß-/Kleinschreibung wird ignoriert.

    Returns:
        dict: Ein Dictionary mit den geschlechtsspezifischen Begriffen.
              Gibt None zurück, wenn nach Fehleraufforderung keine gültige
              Eingabe erfolgte (sollte durch die Schleife aber nicht passieren).
        str: Eine Fehlermeldung, falls die initiale Eingabe ungültig war
             und der User keine valide Eingabe nachliefert (optional, hier geben wir None zurück).

    Raises:
        # Keine Exceptions, Fehler wird über print/input gehandhabt
    """
    # Eingabe normalisieren (Großbuchstaben)
    if isinstance(geschlecht, str):
        geschlecht = geschlecht.upper()
    else:
         geschlecht = None # Setze auf None, wenn kein String übergeben wurde

    # Prüfen, ob Geschlecht gültig ist, sonst nachfragen
    while geschlecht not in ["W", "M"]:
        print("FEHLER: Weder W noch M wurde dem glossary als geschlecht des Patienten zugespielt.")
        user_input = input("Bitte geben Sie das Geschlecht manuell ein (W/M): ").upper().strip() # Added strip()
        if user_input in ["W", "M"]:
            geschlecht = user_input
            print(f"Geschlecht wurde auf '{geschlecht}' gesetzt.")
        else:
             print("Ungültige Eingabe. Bitte nur 'W' oder 'M' eingeben.")
             # Wenn man hier abbrechen soll, könnte man 'return None' oder 'sys.exit()' verwenden
             # return None # Beispiel: Funktion ohne gültiges Glossar beenden


    # Glossar initialisieren
    glossary = {}

    # Glossar basierend auf dem Geschlecht füllen (Inhalt unverändert)
    if geschlecht == "M":
        glossary = {
            # --- Artikel ---
            "artikel_nominativ_gross": "Der", "artikel_genitiv_gross": "Des", "artikel_dativ_gross": "Dem", "artikel_akkusativ_gross": "Den",
            "artikel_nominativ_klein": "der", "artikel_genitiv_klein": "des", "artikel_dativ_klein": "dem", "artikel_akkusativ_klein": "den",
            # --- Patientenbezeichnung ---
            "patient_nominativ": "Patient", "patient_genitiv": "Patienten", "patient_dativ": "Patienten", "patient_akkusativ": "Patienten",
            # --- Adjektivendung (Beispiel: -jährig) ---
            "jährig_nominativ": "jähriger", "jährig_genitiv": "jährigen", "jährig_dativ": "jährigen", "jährig_akkusativ": "jährigen",
            # --- Personalpronomen ---
            "pronomen_nominativ": "er", "pronomen_genitiv": "seiner", "pronomen_dativ": "ihm", "pronomen_akkusativ": "ihn",
            # --- Possessivpronomen ---
            "possessiv_basis": "sein", "possessiv_form_e": "seine", "possessiv_form_em": "seinem", "possessiv_form_er": "seiner", "possessiv_form_en": "seinen", "possessiv_form_es": "seines",
            #genannte
            "genannte_nominativ": "genannte", "genannte_genitiv": "genannten", "genannte_dativ": "genannten", "genannte_akkusativ": "genannten",
            #ein
            "ein_nominativ": "ein", "ein_genitiv": "eines", "ein_dativ": "einem", "ein_akkusativ": "einen",
            #herrfrau
            "herrfrau" : "Herr"
        }
    elif geschlecht == "W":
        glossary = {
             # --- Artikel ---
            "artikel_nominativ_gross": "Die", "artikel_genitiv_gross": "Der", "artikel_dativ_gross": "Der", "artikel_akkusativ_gross": "Die",
            "artikel_nominativ_klein": "die", "artikel_genitiv_klein": "der", "artikel_dativ_klein": "der", "artikel_akkusativ_klein": "die",
             # --- Patientenbezeichnung ---
            "patient_nominativ": "Patientin", "patient_genitiv": "Patientin", "patient_dativ": "Patientin", "patient_akkusativ": "Patientin",
            # --- Adjektivendung (Beispiel: -jährig) ---
            "jährig_nominativ": "jährige", "jährig_genitiv": "jährigen", "jährig_dativ": "jährigen", "jährig_akkusativ": "jährige",
            # --- Personalpronomen ---
            "pronomen_nominativ": "sie", "pronomen_genitiv": "ihrer", "pronomen_dativ": "ihr", "pronomen_akkusativ": "sie",
            # --- Possessivpronomen ---
            "possessiv_basis": "ihr", "possessiv_form_e": "ihre", "possessiv_form_em": "ihrem", "possessiv_form_er": "ihrer", "possessiv_form_en": "ihren", "possessiv_form_es": "ihres",
            #genannten
            "genannte_nominativ": "genannte", "genannte_genitiv": "genannten", "genannte_dativ": "genannten", "genannte_akkusativ": "genannte",
            #ein
            "ein_nominativ": "eine", "ein_genitiv": "einer", "ein_dativ": "einer", "ein_akkusativ": "eine",
            #herrfrau
            "herrfrau" : "Frau"
        }

    return glossary

###################################
###################################
####ACHTUNG
#Muss in main.py mittels glossary = UNIVERSAL.load_json(input("Bitte patientennummer eingeben: ")) aufgerufen werden.
#return ist entweder das dictionary oder "patdata" (falls der user mittel patdata.py eine neue JSON jetzt anlegen will)


def load_json(patientennummer):
    json = importlib.import_module("json") if "json" not in sys.modules else sys.modules["json"]
    """
    Sucht nach einer JSON-Datei mit dem Namen der Patientennummer im
    relativen Verzeichnis 'patdata' (innerhalb des App-Ordners) und lädt deren Inhalt.
    """
    try:
        # Konvertiere zu String, falls es eine Zahl ist
        patientennummer_str = str(patientennummer)

        # Pfad zum Ordner zusammenbauen - Verwende patdata_dir
        # data_folder = os.path.join(user_dir, "py patdata") # OLD
        data_folder = patdata_dir # NEW - uses the globally defined relative path

        # Prüfen, ob der Ordner existiert
        if not os.path.isdir(data_folder): # isdir prüft, ob es ein Verzeichnis ist
            print(f"FEHLER: Patientendaten-Ordner '{data_folder}' nicht gefunden.")
            print("Stellen Sie sicher, dass der 'patdata'-Ordner im Anwendungsverzeichnis existiert.")
            print("Programm wird abgebrochen.")
            sys.exit(1) # Abbruch mit Fehlercode

        # Pfad zur spezifischen Datei zusammenbauen
        file_name = f"{patientennummer_str}.json"
        file_path = os.path.join(data_folder, file_name)

        # Versuche, die JSON-Datei zu öffnen und zu laden
        print(f"Suche nach Patientendaten in: {file_path}")
        with open(file_path, 'r', encoding='utf-8') as f:
            data_dictionary = json.load(f)
        print(f"Daten für Patientennummer {patientennummer_str} erfolgreich geladen.")
        return data_dictionary

    except FileNotFoundError:
        # Dieser Block wird jetzt nur erreicht, wenn der ORDNER existiert,
        # aber die spezifische DATEI darin nicht.
        print(f"\nFEHLER: Datei '{file_name}' im Ordner '{data_folder}' nicht gefunden.")
        # Schleife für Benutzereingabe bei nicht gefundener Datei
        while True:
            print("\nOptionen:")
            print(f" - Geben Sie eine neue mehrstellige Patientennummer ein, um es erneut zu versuchen.")
            print(f" - Geben Sie [j] ein, um eine .json für einen neuen Patienten anzulegen (für das Auslesen der Daten muss KISIM mit dem Patienten auf dem Hauptbildschirm im Vollbildmodus geöffnet sein")
            print(f" - Geben Sie [x] ein, um das Programm abzubrechen.")

            choice = input("Ihre Wahl: ").strip().lower()

            if choice == 'x':
                print("Programm wird auf Benutzerwunsch abgebrochen.")
                sys.exit(0)
            elif choice == 'j':
                print("Signal zum Auslesen/Erstellen der .json-Datei aus KISIM empfangen.")
                import patdata
                create_json_success = patdata.main()  #main returns True if patdata creation is successful
                if create_json_success == True:
                    print("Neue patdata-JSON wurde erfolgreich. Skript beendet, bitte ursprüngliches script erneut ausführen.")
                    sys.exit()
                else:
                    print("Fehler beim Anlegen einer neuen patdata-JSON. Bitte Create patdata manuell ausführen. Beende Skript.")
                    sys.exit()
            else:
                # Check if input is purely digits and has reasonable length
                if choice.isdigit() and len(choice) > 3: # Simple check for multi-digit number
                    print(f"Versuche erneut mit Patientennummer: {choice}")
                    # Rekursiver Aufruf mit der neuen Nummer
                    return load_json(choice)
                else:
                    print(f"Ungültige Eingabe '{choice}'. Bitte eine mehrstellige Nummer, 'j' oder 'x' eingeben.")

    except json.JSONDecodeError:
        print(f"FEHLER: Die Datei '{file_path}' existiert, konnte aber nicht als gültiges JSON gelesen werden.")
        print("Bitte überprüfen Sie den Inhalt der Datei.")
        print("Programm wird wegen fehlerhafter JSON-Datei abgebrochen.")
        sys.exit(1)

    except Exception as e:
        print(f"\nFEHLER: Ein unerwarteter Fehler ist aufgetreten beim Versuch, '{file_path}' zu lesen:")
        print(e)
        print("Programm wird abgebrochen.")
        sys.exit(1)

###################################
###################################
##Muss in main.py als z.B. UNIVERSAL.dict_to_global_variables(glossary) abgerufen werden.
# dict_to_global_variables: No path changes needed.
def dict_to_global_variables(data_dict):
    """
    Erstellt globale Variablen aus den Schlüssel-Wert-Paaren eines Dictionaries.

    Für jeden Eintrag im Eingabe-Dictionary wird versucht, eine globale Variable
    zu erstellen, bei der:
    - Der Variablenname der key ist
    - Der Variablenwert die STRING-Repräsentation des Dictionary-Wertes ist.

    Args:
        data_dict (dict): Das Dictionary, dessen Elemente zu globalen Variablen werden sollen.

    Raises:
        TypeError: Wenn die Eingabe kein Dictionary ist.

    Warnungen:
        - Gibt eine Warnung aus und überspringt Schlüssel, die keine Strings oder keine
          gültigen Python-Identifier sind (z.B. beginnen mit einer Zahl, enthalten Bindestriche).
        - Das direkte Modifizieren des globalen Namensraums kann riskant sein,
          potenziell bestehende Variablen überschreiben oder Code schwer verständlich machen.
          Mit Vorsicht verwenden!

    Returns:
        None: Diese Funktion modifiziert den globalen Scope direkt und gibt None zurück.
    """
    if not isinstance(data_dict, dict):
        raise TypeError("Eingabe muss ein Dictionary sein.")

    # Hole den globalen Namensraum als Dictionary
    global_namespace = globals()

    skipped_keys = [] # Liste für übersprungene Schlüssel

    for key, value in data_dict.items():
        # 1. Prüfen, ob der Schlüssel ein String ist
        if not isinstance(key, str):
            print(f"Warnung: Überspringe Schlüssel '{key}' (Typ: {type(key).__name__}). "
                  f"Globale Variablennamen müssen Strings sein.", file=sys.stderr)
            skipped_keys.append(key)
            continue # Zum nächsten Element springen

        # 2. Prüfen, ob der String-Schlüssel ein gültiger Python-Identifier ist
        #    (beginnt mit Buchstabe/_, gefolgt von Buchstaben/Zahlen/_, kein Keyword)
        if not key.isidentifier():
            print(f"Warnung: Überspringe Schlüssel '{key}'. Er ist kein gültiger Python-"
                  f"Identifier (z.B. darf nicht mit Zahl beginnen, Bindestriche enthalten oder ein Keyword sein).",
                  file=sys.stderr)
            skipped_keys.append(key)
            continue # Zum nächsten Element springen

        # 3. Optional: Zusätzliche Sicherheitsprüfung (überspringe, wenn es eine existierende Funktion/Modul ist)
        #    Dies ist eine einfache Prüfung, sie könnte erweitert werden.
        # if key in global_namespace and (callable(global_namespace[key]) or isinstance(global_namespace[key], type(sys))):
        #      print(f"Warnung: Überspringe Schlüssel '{key}', da er eine existierende Funktion oder Modul überschreiben könnte.", file=sys.stderr)
        #      skipped_keys.append(key)
        #      continue

        # Wenn alle Prüfungen bestanden sind:
        # Wert in String umwandeln und dem globalen Namensraum hinzufügen
        string_value = str(value)
        global_namespace[key] = string_value
        # print(f"Globale Variable erstellt: {key} = \"{string_value}\"") # Zum Debuggen einkommentieren

    if skipped_keys:
        print(f"\nInfo: Folgende Schlüssel wurden übersprungen: {skipped_keys}")

###################################
###################################

def viewjson_via_patientennummer(patientennummer):
    json = importlib.import_module("json") if "json" not in sys.modules else sys.modules["json"]

    # Use patdata_dir for the directory
    # directory = rf"{user_dir}\py patdata" # OLD
    directory = patdata_dir # NEW
    filename = f"{patientennummer}.json"
    filepath = os.path.join(directory, filename)

    if not os.path.exists(filepath):
        print(f"Die Datei '{filepath}' existiert nicht.")
        return # Changed to return instead of pass

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Fehler beim Lesen der JSON-Datei '{filepath}': {e}")
        return
    except IOError as e:
        print(f"Fehler beim Öffnen der Datei '{filepath}': {e}")
        return

    # Definiere den Referenz-Key und eine gewünschte Gesamtbreite (angenommen Tab = 4 Leerzeichen)
    ref_key = "Fraktionen_pro_Woche"
    # Calculate width based on the longest key dynamically for better formatting
    try:
        max_key_len = max(len(k) for k in data.keys()) if data else 0
    except Exception: # Handle potential errors if keys are not strings etc.
        max_key_len = 20 # Default fallback width
    ref_width = max(len(ref_key), max_key_len) + 4 # Use the longer one + buffer


    keys = list(data.keys())  # Liste aller Keys für die nummerierte Auswahl

    while True:
        # Zeige nummerierte Liste der Keys mit den aktuellen Werten
        print("\nVerfügbare Keys und aktuelle Werte:")
        for i, key in enumerate(keys, start=1):
            # Fülle alle Keys mit Leerzeichen bis zur gewünschten Breite
            formatted_key = key.ljust(ref_width)
            print(f"{i}: {formatted_key} → {data[key]}")

        try:
            selection = input("\nWelchen Key möchten Sie ändern? (Geben Sie die Zahl ein oder '-' zum Beenden): ").strip()
            if selection == "-":
                break

            index = int(selection) - 1  # Umwandlung der Eingabe in einen Index
            if index < 0 or index >= len(keys):
                print("Ungültige Auswahl. Bitte eine gültige Zahl eingeben.")
                continue

            chosen_key = keys[index]
            new_value = input(f"Mit welchem neuen Wert möchten Sie '{chosen_key}' überschreiben? (Aktuell: {data[chosen_key]}): ")
            data[chosen_key] = new_value
            print(f"Der Key '{chosen_key}' wurde auf '{new_value}' aktualisiert.")

        except ValueError:
            print("Bitte eine gültige Zahl eingeben.")

        # Abfrage, ob ein weiterer Key geändert werden soll - Simplified
        # further = input("Möchten Sie einen weiteren Key ändern? (Geben Sie eine Zahl ein oder '-' zum Beenden): ")
        # if further == "-":
        #     break

    # Speichern der aktualisierten JSON-Datei (überschreibt die alte Datei)
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"\nDie Datei '{filepath}' wurde erfolgreich aktualisiert und gespeichert.")
        return True
    except IOError as e:
        print(f"Fehler beim Speichern der Datei '{filepath}': {e}")
        return False

###################################
###################################
# _ask_user_entity_confirmation: No path changes needed.
def _ask_user_entity_confirmation(tumor_name_display, entity_value_on_yes):
    """
    Private helper function to ask the user for confirmation.
    Moved to UNIVERSAL.py

    Args:
        tumor_name_display (str): The name of the tumor to display in the prompt.
        entity_value_on_yes (str): The value to return if user enters 'j'.

    Returns:
        str | None: Returns `entity_value_on_yes` if the user confirmed ('j'),
                    otherwise returns `None`.
    """
    while True:
        antwort = input(f"Als Tumorentität wurde {tumor_name_display} erkannt; Tumorspezifischen Brief für diese Entität anlegen? (j/n): ").strip().lower()
        if antwort == 'j':
            print(f"--> Spezifischer Bericht für '{entity_value_on_yes}' wird vorbereitet.")
            return entity_value_on_yes # Return the entity string
        elif antwort == 'n':
            print("--> Kein spezifischer Bericht für diese Entität gewählt.")
            return None # Return None if declined
        else:
            print("Ungültige Eingabe. Bitte 'j' oder 'n' eingeben.")

# suche_nach_tumor_entity: No path changes needed.
def suche_nach_tumor_entity(tumor_text):
    """
    Analyzes the provided tumor text to identify a specific tumor entity,
    asks the user for confirmation via console input, and returns the
    identified entity string or None.
    Moved to UNIVERSAL.py

    Args:
        tumor_text (str): The tumor description string from patient data.

    Returns:
        str | None: The lowercase string name of the confirmed entity
                    (e.g., 'meningeom', 'hirnmetastase') or None if no
                    specific entity is confirmed or a standard report
                    is requested, or if the user aborts the final step.
    """
    entity_to_return = None # Variable to hold the potential return value
    entity_check_performed = False # Flag to know if any specific check was triggered

    if not tumor_text or not isinstance(tumor_text, str):
        print("Kein Tumoreintrag übergeben oder Eintrag ist ungültig.")
        tumor_lower = "" # Ensure tumor_lower exists
    else:
        tumor_lower = tumor_text.lower() # Case-insensitive comparison
        print(f"Prüfe Tumoreintrag: '{tumor_text}'")

        # --- Specific Tumor Checks (Order might matter) ---
        # Check conditions and call helper. If helper returns an entity string, store it and break the check.

        # List of tuples: (keyword(s), display_name, return_value)
        tumor_checks = [
            (["vestibularisschwan"], "Vestibularisschwannom", "vestibularisschwannom"),
            (["paraganglio"], "Paragangliom", "paragangliom"),
            (["meningeo"], "Meningeom", "meningeom"),
            (["glioblastom"], "Glioblastom", "glioblastom"),
            (["astrozytom"], "Astrozytom", "astrozytom"),
            (["oligodendrogliom"], "Oligodendrogliom", "oligodendrogliom"),
            (["karz", ("lappen", "lunge")], "Lungenkarzinom", "lungenkarzinom"), # Combo check
            (["lebermetastase"], "Lebermetastase", "lebermetastase"),
            (["lungenmetastase"], "Lungenmetastase", "lungenmetastase"),
             (["metastase", ("knochen", "hwk", "bwk", "lwk")], "eine Form der Knochenmetastase", "knochenmetastase"), # Combo check
            (["metastase", ("hirn", "gehirn")], "eine Form der Hirnmetastasierung", "hirnmetastase") # Combo check
        ]

        for check_data in tumor_checks:
            keywords, display_name, return_value = check_data
            primary_keyword = keywords[0]
            secondary_keywords = None
            is_combo = False

            # Check if it's a combo check (list contains a tuple/list of secondary words)
            if len(keywords) > 1 and isinstance(keywords[1], (list, tuple)):
                is_combo = True
                secondary_keywords = keywords[1]

            # Perform the check
            match = False
            if is_combo:
                if primary_keyword in tumor_lower and any(sec_kw in tumor_lower for sec_kw in secondary_keywords):
                    match = True
            else:
                if primary_keyword in tumor_lower:
                    match = True

            if match:
                entity_check_performed = True
                confirmed_entity = _ask_user_entity_confirmation(display_name, return_value)
                if confirmed_entity is not None:
                    return confirmed_entity # Directly return confirmed entity if user says 'j'
                else:
                    # User said 'n' to this specific match, continue searching?
                    # Current logic: If user says 'n', we fall through to the generic prompt.
                    # If we should continue checking other specific types, this logic needs adjustment.
                    # For now, break the loop as the original code did (implicitly by returning).
                    # If we want to check others after 'n', remove the 'return confirmed_entity' above
                    # and handle the 'None' case after the loop. Let's stick to original flow for now.
                    break # Stop checking specific tumors if user declined this one

    # --- Handle No Specific Match or User Declined Specific Match ---
    # This block is reached if tumor_text was empty/invalid OR
    # if none of the specific checks resulted in a 'j' confirmation.

    if not entity_check_performed:
        print("\nEs wurde keine spezifische Tumorentität im Text gefunden.")
    # else: # A specific entity was found but declined if we reach here
        # print("\nDie Auswahl der spezifischen Tumorentität wurde abgelehnt.")


    while True:
        antwort = input("Soll ein nicht-tumorspezifischer Bericht angelegt werden? (j/n): ").strip().lower()
        if antwort == 'j':
            print("--> Standardbericht wird angelegt.")
            return None # Standard report means None entity
        elif antwort == 'n':
            print("Programm vom User abgebrochen, kein Brief angelegt.")
            # Returning None here indicates abortion to the caller.
            # Caller needs to decide how to handle this (e.g., exit).
            return None
        else:
            print("Ungültige Eingabe. Bitte 'j' oder 'n' eingeben.")


###################################
###################################


def find_and_click_button(image_name, description="Button", base_path=None, max_attempts= 200, interval=0.01, confidence=0.8):
    # Check if pyautogui is loaded, handle import error if necessary
    try:
        pyautogui = importlib.import_module("pyautogui") if "pyautogui" not in sys.modules else sys.modules["pyautogui"]
    except ImportError:
        print(f"FEHLER ({description}): Modul 'pyautogui' konnte nicht geladen werden.")
        return False
    """
    Sucht wiederholt nach einem Bild auf dem Bildschirm und klickt darauf, wenn gefunden.
    Angepasste Version für UNIVERSAL.py, die einen Basispfad akzeptiert.

    Args:
        image_name (str): Der Dateiname des Bildes (ohne Pfad).
        description (str): Eine Beschreibung des Buttons für Log-Meldungen.
        base_path (str): Der Basispfad zum Screenshot-Verzeichnis. Mandatory.
        max_attempts (int): Maximale Anzahl von Suchversuchen.
        interval (float): Wartezeit zwischen den Versuchen in Sekunden.
        confidence (float): Genauigkeitsschwelle für die Bilderkennung.

    Returns:
        bool: True, wenn der Button gefunden und geklickt wurde, sonst False.
    """
    if not base_path or not os.path.isdir(base_path): # Added check if base_path is a directory
        print(f"FEHLER ({description}): Ungültiger oder fehlender Screenshot-Basispfad angegeben: '{base_path}'")
        return False

    image_path = os.path.join(base_path, image_name)
    # Check if the image file itself exists before starting the loop
    if not os.path.isfile(image_path):
        print(f"FEHLER ({description}): Bilddatei nicht gefunden unter: '{image_path}'")
        return False

    print(f"Suche nach '{description}' ({image_name})... Pfad: {image_path}")
    attempts = 0
    while attempts < max_attempts:
        try:
            # Verwende locateCenterOnScreen für direkte Koordinaten zum Klicken
            location = pyautogui.locateCenterOnScreen(image_path, confidence=confidence)
            if location:
                # Add a small random offset to the click location? Optional.
                # x_offset = random.randint(-2, 2)
                # y_offset = random.randint(-2, 2)
                # click_location = (location.x + x_offset, location.y + y_offset)
                print(f"'{description}' gefunden bei {location}. Klicke...")
                pyautogui.click(location) # Click the identified center
                # KEIN time.sleep() hier hinzufügen, wie gewünscht
                print(f"'{description}' geklickt.")
                return True
            # Kein else-Block für "nicht gefunden" für weniger Konsolenausgabe
        except pyautogui.ImageNotFoundException:
            # Fehler wird nur am Ende gemeldet, wenn alle Versuche fehlschlagen
            pass
        except Exception as e:
            # Log unexpected errors during search/click
            print(f"Ein unerwarteter Fehler ist bei der Suche/Klick nach '{description}' aufgetreten (Versuch {attempts + 1}): {e}")
            # Consider if returning False immediately is better on unexpected errors
            # return False
            pass # Continue trying for now

        attempts += 1
        time.sleep(interval) # Kurze Pause zwischen den Suchversuchen bleibt

    print(f"Fehler: '{description}' ({image_name}) konnte nach {max_attempts} Versuchen nicht gefunden werden unter '{image_path}'.")
    return False


###################################
###################################

def leistung_eintragen(bericht_typ, icd_code=None, secondary_icd_code=None):
    pyautogui = importlib.import_module("pyautogui") if "pyautogui" not in sys.modules else sys.modules["pyautogui"]
    """
    Navigiert zum Leistungsbereich, wählt passende Leistung und prüft ICD-Status.
    Versucht, fehlenden ICD-Code automatisch einzutragen, basierend auf übergebenen Argumenten.

    Args:
        bericht_typ (str): Typ des Berichts ('em', 'eb', 'a', 'k', 't', 'w').
        icd_code (str, optional): Der primäre ICD-Code aus den Patientendaten. Defaults to None.
        secondary_icd_code (str, optional): Der sekundäre ICD-Code aus den Patientendaten. Defaults to None.

    Returns:
        bool: True bei Erfolg (Leistung gespeichert oder Automatisierung erfolgreich), False bei Fehler oder wenn Speichern fehlschlägt.
    """
    # --- Vorab-Prüfungen und Initialisierung ---
    print(f"\n--- Starte Leistungseintragung für Berichtstyp/Code: {bericht_typ} ---")
    local_screenshot_base_path = os.path.join(screenshots_dir, "UNIVERSAL", "bereich_leistungen")
    print("Zugespielte Argumente:")
    print(f"icd_code: {icd_code}")
    print(f"secondary_icd_code: {secondary_icd_code}")

    # --- 1. Leistungscode ist jetzt direkt der bericht_typ ---
    leistung_code = bericht_typ # Verwende den übergebenen Typ direkt

    # Validierung des übergebenen Typs (optional, aber gut)
    valid_codes = ['em', 'eb', 'a', 'k', 't', 'w']
    if leistung_code not in valid_codes:
        print(f"FEHLER: Ungültiger bericht_typ '{leistung_code}' für Leistungserfassung erhalten.")
        return False

    print(f"Zugehöriger Leistungscode: {leistung_code}")

    # --- Navigation und Button-Klicks (wie zuvor) ---
    if not navigiere_bereich_leistungen(): print("FEHLER: Navigation zu Leistungen fehlgeschlagen."); return False
    if not find_and_click_button("button_neu.png", "Neu Button", base_path=local_screenshot_base_path): return False
    if not find_and_click_button("button_tmambulant.png", "TM ambulant Button", base_path=local_screenshot_base_path): return False
    if not find_button("button_zeile_leistungen.png", base_path=local_screenshot_base_path): return False
    time.sleep(0.3) # Kurze Pause nach dem Klicken
    if not find_and_click_button("button_radioonkologie_ats.png", "Radioonkologie ATS Button", base_path=local_screenshot_base_path):
            print("FEHLER: Button 'Radioonkologie ATS' nicht gefunden.")
            return False
    if not find_and_click_button("button_konsultationen.png", "Konsultationen Button", base_path=local_screenshot_base_path):
            print("FEHLER: Button 'Konsultationen' nicht gefunden.")
            return False


    #je nach leistung_code, indivuduelle Buttons
    if leistung_code == 'em':       
        if not find_and_click_button("button_erstkonsultationen.png", "Erstkonsultationen Button", base_path=local_screenshot_base_path):
            print("FEHLER: Button 'Erstkonsultationen' nicht gefunden.")
            return False
        if not find_and_click_button("button_erstkons_maligne.png", "Erstkonsultationen maligne Button", base_path=local_screenshot_base_path):
            print("FEHLER: Button 'Erstkonsultationen maligne' nicht gefunden.")
            return False
        
    elif leistung_code == 'eb':
        
        if not find_and_click_button("button_erstkonsultationen.png", "Erstkonsultationen Button", base_path=local_screenshot_base_path):
            print("FEHLER: Button 'Erstkonsultationen' nicht gefunden.")
            return False
        if not find_and_click_button("button_erstkons_benigne.png", "Erstkonsultationen benigne Button", base_path=local_screenshot_base_path):
            print("FEHLER: Button 'Erstkonsultationen benigne' nicht gefunden.")
            return False
    
    elif leistung_code == 'w':
        if not find_and_click_button("button_woko.png", "Wochenkontrolle Button", base_path=local_screenshot_base_path):
            print("FEHLER: Button 'Wochenkontrolle' nicht gefunden.")
            return False
        if not find_and_click_button("button_wochenkontrolle.png", "Wochenkontrolle Button", base_path=local_screenshot_base_path):
            print("FEHLER: Button 'Wochenkontrolle' nicht gefunden.")
            return False

    elif leistung_code == 'a':
        if not find_and_click_button("button_abschluss.png", "Abschluss Button", base_path=local_screenshot_base_path):
            print("FEHLER: Button 'Abschluss' nicht gefunden.")
            return False
        if not find_and_click_button("button_abschlusskontrolle.png", "Abschlusskontrolle Button", base_path=local_screenshot_base_path):
            print("FEHLER: Button 'Abschlusskontrolle' nicht gefunden.")
            return False
        
    elif leistung_code == 'k':
        if not find_and_click_button("button_verlaufskontrollen.png", "Verlaufskontrollen Button", base_path=local_screenshot_base_path):
            print("FEHLER: Button 'Verlaufskontrollen' nicht gefunden.")
            return False
        if not find_and_click_button("button_verlaufskontrolle_klinisch.png", "Verlaufskontrolle klinisch Button", base_path=local_screenshot_base_path):
            print("FEHLER: Button 'Verlaufskontrolle klinisch' nicht gefunden.")
            return False
        
    elif leistung_code == 't':
        if not find_and_click_button("button_verlaufskontrolle_telefonisch.png", "Verlaufskontrolle telefonisch Button", base_path=local_screenshot_base_path):
            print("FEHLER: Button 'Verlaufskontrolle telefonisch' nicht gefunden.")
            return False


    # --- Prüfung ICD & Speichern ---
    print("INFO: Prüfe ICD-Code Status...")
    icd_check_attempts = 0
    max_icd_checks = 100 # Ca. 10 Sekunden Timeout
    action_taken = False
    icd_automatically_entered = False # Flag für erfolgreiche Auto-Eingabe

    # Pfade zu den Bildern definieren
    icd_fehlt_path = os.path.join(local_screenshot_base_path, "button_ICDfehlt.png")
    icd_komplett_path = os.path.join(local_screenshot_base_path, "button_ICDkomplett.png")
    icd_feld_path = os.path.join(local_screenshot_base_path, "button_ICD_feld.png") # Pfad zum Eingabefeld
    speichern_path = os.path.join(local_screenshot_base_path, "button_speichern.png")

    while icd_check_attempts < max_icd_checks and not action_taken:
        icd_fehlt_location = None
        icd_komplett_location = None

        # Suche nach "ICD fehlt"
        try:
            icd_fehlt_location = pyautogui.locateCenterOnScreen(icd_fehlt_path, confidence=0.85)
        except pyautogui.ImageNotFoundException: pass
        except Exception as e: print(f"WARNUNG: Fehler bei Suche nach 'ICD fehlt': {e}")

        # Suche nach "ICD komplett"
        try:
            icd_komplett_location = pyautogui.locateCenterOnScreen(icd_komplett_path, confidence=0.85)
        except pyautogui.ImageNotFoundException: pass
        except Exception as e: print(f"WARNUNG: Fehler bei Suche nach 'ICD komplett': {e}")

        # --- Logik basierend auf gefundenen Buttons ---
        if icd_fehlt_location:
            print("INFO: Button 'ICD fehlt' gefunden.")
            try:
                pyautogui.click(icd_fehlt_location)
                print("INFO: 'ICD fehlt' geklickt. Versuche automatische Eingabe...")
                time.sleep(0.5) # Warten auf Feld
            except Exception as e:
                print(f"FEHLER beim Klicken auf 'ICD fehlt': {e}")
                return False # Kritischer Fehler, da wir nicht fortfahren können

            # --- ICD-Code bestimmen (Priorisierung basierend auf Argumenten) ---
            icd_to_type = None
            if secondary_icd_code: # Priorität 1: Sekundärer Code
                icd_to_type = str(secondary_icd_code) # Sicherstellen, dass es ein String ist
                print(f"INFO: Verwende sekundären ICD-Code (Argument): {icd_to_type}")
            elif icd_code: # Priorität 2: Primärer Code
                icd_to_type = str(icd_code) # Sicherstellen, dass es ein String ist
                print(f"INFO: Verwende primären ICD-Code (Argument): {icd_to_type}")

            # --- Eingabe versuchen, wenn Code vorhanden ---
            if icd_to_type and icd_to_type != "None" and icd_to_type != "": # Stelle sicher, dass es ein valider Code ist
                print(f"INFO: Versuche ICD-Code '{icd_to_type}' einzugeben...")
                # Klicke in das ICD-Eingabefeld
                if find_and_click_button("button_ICD_feld.png", "ICD Eingabefeld", base_path=local_screenshot_base_path, confidence=0.8):
                    time.sleep(0.1) # Kurze Pause
                    try:
                        pyautogui.typewrite(icd_to_type)
                        print("INFO: ICD-Code getippt.")
                        time.sleep(0.2)
                        pyautogui.press('enter')
                        print("INFO: Enter nach ICD-Eingabe gedrückt.")
                        icd_automatically_entered = True # Setze Flag
                        action_taken = True # Aktion abgeschlossen
                        print("INFO: ICD automatisch eingetragen. Fortfahren mit Speichern...")
                        # Breche die while-Schleife ab, um direkt zu speichern
                        break
                    except Exception as e:
                        print(f"FEHLER beim Tippen des ICD-Codes oder Drücken von Enter: {e}")
                        print("FEHLER: Automatische ICD-Eingabe fehlgeschlagen. Abbruch.")
                        return False # Automatisierung gescheitert, Abbruch

                else: # ICD-Feld nicht gefunden
                    print("FEHLER: Konnte ICD-Eingabefeld nicht finden/klicken.")
                    print("FEHLER: Automatische ICD-Eingabe fehlgeschlagen. Abbruch.")
                    return False # Automatisierung gescheitert, Abbruch

            else: # Kein ICD-Code zum Eintragen gefunden
                print("-" * 40)
                print("FEHLER: KEIN ICD-Code ZUM EINTRAGEN VERFÜGBAR!")
                print("Weder primärer noch sekundärer ICD-Code wurde an die Funktion übergeben oder beide sind leer/None.")
                print("Automatisches Eintragen nicht möglich. Bitte manuell icd_code eintragen und Leistung abspeichern. Programm beendet.")
                sys.exit("Abbruch wegen fehlendem ICD-Code für automatische Eingabe.")

        elif icd_komplett_location:
            print("INFO: ICD-10 Status ist 'komplett'.")
            # Speichern versuchen
            if find_and_click_button("button_speichern.png", "Speichern Button", base_path=local_screenshot_base_path):
                print("INFO: Leistung erfolgreich gespeichert.")
                action_taken = True
                return True # Erfolg
            else:
                print("FEHLER: Speichern fehlgeschlagen, obwohl ICD als komplett angezeigt wurde.")
                action_taken = True # Aktion gescheitert, Loop beenden
                return False # Fehler signalisieren

        # --- Warte kurz, wenn noch keine Aktion erfolgte ---
        if not action_taken:
            if icd_check_attempts % 10 == 0:
                print(f"INFO: Warte auf ICD Status (Versuch {icd_check_attempts + 1}/{max_icd_checks})...")
            icd_check_attempts += 1
            time.sleep(0.1)

    # --- Nach der Schleife ---
    if icd_automatically_entered:
        # Wenn der ICD automatisch eingegeben wurde, müssen wir jetzt speichern
        print("INFO: Versuche nach automatischer ICD-Eingabe zu speichern...")
        time.sleep(0.1) # Kurze Pause, damit KISIM den Enter verarbeiten kann
        if find_and_click_button("button_speichern_icd.png", "Speichern Button (nach Auto-ICD)", base_path=local_screenshot_base_path, max_attempts=50):
            print("INFO: Leistung nach automatischer ICD-Eingabe erfolgreich gespeichert. Speichere zuerst ICD10")
            time.sleep(0.2)
            if find_and_click_button("button_speichern.png", "Speichern Button", base_path=local_screenshot_base_path, max_attempts=50):
                print("Speichere Leistung...")
                return True # Erfolg
        else:
            print("FEHLER: Speichern nach automatischer ICD-Eingabe fehlgeschlagen.")
            return False # Fehler
    elif not action_taken:
        # Fallback, wenn nach max_checks weder "fehlt" noch "komplett" gefunden wurde
        print(f"FEHLER: ICD Status nach {max_icd_checks} Versuchen nicht eindeutig erkannt.")
        print("Versuche Fallback-Speichern (könnte fehlschlagen, wenn ICD wirklich fehlt)...")
        if find_and_click_button("button_speichern.png", "Speichern (Fallback)", base_path=local_screenshot_base_path):
            print("WARNUNG: Fallback-Speichern geklickt (Erfolg unsicher).")
            return True # Gehen wir mal von Erfolg aus, auch wenn Status unklar war
        else:
            print("FEHLER: Fallback-Speichern fehlgeschlagen.")
            return False # Fehler

    # Sollte nicht erreicht werden, wenn die Logik oben stimmt
    print("WARNUNG: Unerwartetes Ende der Funktion leistung_eintragen.")
    return False


def icd_check(icd_code=None):
    local_screenshot_base_path = os.path.join(screenshots_dir, "UNIVERSAL", "bereich_leistungen")
    anker_icd = None
    for i in range(50):
        if find_button("button_icd_komplett.png", base_path=local_screenshot_base_path, max_attempts=1):
            print("button_icd_komplett.png gefunden, ICD bereits eingetragen")
            anker_icd = True
            break
        elif find_button("button_icd_fehlt.png", base_path=local_screenshot_base_path, max_attempts=1):
            print("button_icd_fehlt.png gefunden, ICD muss eingetragen werden")
            anker_icd = False
            break
        else:
            print(f"Nach Versuch {i}:Weder ICD komplett noch ICD fehlt gefunden, versuche erneut.")

    if anker_icd == None:
        print("nach 50 Versuchen kein ICD anker gefunden")
        return False
    elif anker_icd == True:
        print("ICD bereits gesetzt. Return True")
        return True
    elif anker_icd == False:
        print("ICD nicht gesetzt, fahre fort mich Ausfüllen...\n\n\n")

    if icd_code == None:
        print("\n\nERROR: ICD ist nicht eingetragen, aber es wurde kein icd_code der Funktion UNIVERSAL.icd_check() gepassed. ICD eintragen erfolglos!\n\n")
        return False
    if not find_and_click_button("button_icd_fehlt.png", base_path=local_screenshot_base_path): print("button ICD fehlt nicht gefunden")
    if not find_and_click_button("button_ICD_feld.png", base_path=local_screenshot_base_path): print("ERROR button ICD Feld nicht gefunden")
    pyautogui.typewrite(icd_code)
    time.sleep(0.1)
    pyautogui.press("enter")
    if find_button("button_icd_fehler.png", base_path=local_screenshot_base_path, max_attempts=5):
        print("\n\neingegebener ICD Code nicht akzeptiert")
        time.sleep(0.1)
        pyautogui.hotkey("alt, f4")
        time.sleep(0.1)
        pyautogui.press("enter")
        return False
    if not find_and_click_button("button_speichern_und_schliessen_icd.png", base_path=local_screenshot_base_path): print("ERROR button button_speichern_und_schliessen_icd nicht gefunden")
    print("\n\n Funktion UNIVERSAL.icd_check erfolgreich abgeschlossen, ICD wurde eingetragen\n\n")
    return True
###################################
###################################

def alle_kgs_schliessen():
    local_screenshot_base_path = os.path.join(screenshots_dir, "UNIVERSAL", "KG_management")
    pyautogui.rightClick(350, 35)
    time.sleep(0.1)
    if not find_and_click_button("button_alle_kgs_schliessen.png", base_path=local_screenshot_base_path): 
        print("ERROR button button_alle_kgs_schliessen nicht gefunden")
        return False
    if not find_button("button_keinekgoffen.png", base_path=local_screenshot_base_path):
        print("\n\n\nACHTUNG!: Es sind nicht alle KGs geschlossen, bitte manuell KG schliessen! (10s Zeit für manuelles Schliessen)")
        time.sleep(10)
        if not find_button("button_keinekgoffen.png", base_path=local_screenshot_base_path, max_attempts=3, interval=0.05):
            print("\n\n\n Offene KGs wurden auch manuell nicht geschlossen, breche Skript ab...)")
            sys.exit()
        
    return True
    
    



    




###################################
###################################

def userinput_freitext(prompt):
    """
    Fordert den Benutzer zu einer Freitexteingabe auf und gibt den bereinigten String zurück.
    Eine leere Eingabe gibt None zurück.

    Args:
        prompt (str): Die anzuzeigende Eingabeaufforderung.

    Returns:
        str | None: Der vom Benutzer eingegebene und bereinigte Text, oder None bei leerer Eingabe.
    """
    print(prompt, end=" ")
    user_input = input().strip()
    # --- ÄNDERUNG ---
    if not user_input:
        return None # Gibt None zurück, wenn nur Enter gedrückt wurde
    else:
        return user_input
    # --- Ende Änderung ---

def userinput_chemotherapie(prompt):
    """
    Fordert den Benutzer zur Eingabe des Chemotherapeutikums auf (als Freitext).
    Eine leere Eingabe gibt None zurück.

    Args:
        prompt (str): Die anzuzeigende Eingabeaufforderung.

    Returns:
        str | None: Das eingegebene Chemotherapeutikum oder None bei leerer Eingabe.
    """
    # Verwendet jetzt die Logik von userinput_freitext
    return userinput_freitext(prompt)

def userinput_fraktionen_woche(prompt):
    """
    Präsentiert dem Benutzer eine nummerierte Liste von Frequenzoptionen zur Auswahl
    oder ermöglicht eine Freitexteingabe.

    Der Benutzer wählt durch Eingabe der entsprechenden Zahl oder 'f' für Freitext.
    Akzeptiert NUR Zahlen (im gültigen Bereich) oder 'f'/'F' als erste Eingabe.
    Andere Eingaben führen zu einer erneuten Aufforderung.

    Args:
        prompt (str): Die Aufforderung, die dem Benutzer vor der Auswahl angezeigt wird.

    Returns:
        str: Der Text der ausgewählten Option oder der eingegebene Freitext.
             Gibt None zurück, wenn keine interaktive Eingabe möglich ist
             oder die Eingabe abgebrochen wird (z.B. durch Strg+D).
             Kann auch eine leere Zeichenkette zurückgeben, wenn der Benutzer
             bei der Freitexteingabe nichts eingibt.
    """
    options = [
        "1x pro Woche",
        "3x pro Woche",
        "jeden 2. Tag",
        "4x pro Woche",
        "5x pro Woche",
        "5x pro Woche inkl. Feiertage",
        "6x pro Woche",
        "2x pro Tag"
    ]

    print(f"\n{prompt}")
    # Nutze enumerate, um eine nummerierte Liste auszugeben (beginnend bei 1)
    for i, option in enumerate(options):
        print(f"{i + 1}: {option}")
    print(f"[f] für Freitexteingabe") # Füge die Option für Freitext hinzu

    while True:
        try:
            prompt_text = f"Ihre Auswahl (1-{len(options)} oder 'f'): "
            choice_str = input(prompt_text)

            # 1. Prüfen, ob der Benutzer Freitext gewählt hat (Groß-/Kleinschreibung ignorieren)
            if choice_str.lower() == 'f':
                try:
                    free_text_prompt = "Bitte geben Sie die Frequenz als freien Text ein: "
                    free_text = input(free_text_prompt)
                    # Optional: Validierung des Freitextes könnte hier erfolgen
                    return free_text # Gib den eingegebenen Freitext zurück
                except EOFError:
                    # Eingabe wurde während der Freitexteingabe abgebrochen
                    print("\nEingabe abgebrochen.")
                    return None

            # 2. Prüfen, ob die Eingabe eine gültige Zahl ist
            elif choice_str.isdigit():
                choice_num = int(choice_str)
                # Prüfen, ob die eingegebene Zahl im gültigen Bereich liegt
                if 1 <= choice_num <= len(options):
                    # Gültige Wahl: Hole den Text aus der Liste
                    selected_option = options[choice_num - 1]
                    return selected_option # Gib den ausgewählten Text zurück
                else:
                    # Zahl außerhalb des gültigen Bereichs
                    print(f"Ungültige Nummer. Bitte geben Sie eine Zahl zwischen 1 und {len(options)} oder 'f' ein.")
                    # Die Schleife wird fortgesetzt (implizit durch das Fehlen von return/break)

            # 3. Wenn weder 'f' noch eine Ziffer eingegeben wurde
            else:
                print(f"Ungültige Eingabe. Bitte geben Sie NUR eine Zahl zwischen 1 und {len(options)} oder 'f' ein.")
                # Die Schleife wird fortgesetzt (implizit)

        except EOFError:
             # Eingabe wurde bei der Hauptauswahl abgebrochen (z.B. Strg+D)
             print("\nEingabe abgebrochen.")
             return None # Gibt None zurück bei Abbruch
        except KeyboardInterrupt: # Optional: Fängt auch Strg+C ab
             print("\nEingabe durch Benutzer abgebrochen.")
             return None

def userinput_intention(prompt):
    """
    Fordert den Benutzer zur Eingabe der Therapieintention auf (k/p/l oder Enter).
    Gibt den vollständigen Begriff oder None zurück.

    Args:
        prompt (str): Die anzuzeigende Eingabeaufforderung.

    Returns:
        str | None: Die validierte, ausgeschriebene Therapieintention oder None bei leerer Eingabe.
    """
    mapping = {"k": "kurativ", "p": "palliativ", "l": "lokalablativ"}
    while True:
        print(prompt, end=" ")
        val = input().strip().lower()
        # --- ÄNDERUNG ---
        if not val:
            return None # Erlaube leere Eingabe -> None
        # --- Ende Änderung ---
        if val in mapping:
            return mapping[val]
        else:
            print("Ungültige Eingabe. Bitte 'k', 'p', 'l' oder Enter (für keine Angabe) eingeben.")

def userinput_date_ddmmyyyy(prompt):
    """
    Fordert den Benutzer zur Eingabe eines Datums im Format dd.mm.yyyy auf
    oder erlaubt leere Eingabe (Enter). Gibt das Datum als String oder None zurück.

    Args:
        prompt (str): Die anzuzeigende Eingabeaufforderung.

    Returns:
        str | None: Das validierte Datum im Format "dd.mm.yyyy" oder None bei leerer Eingabe.
    """
    while True:
        print(prompt, end=" ")
        date_str = input().strip() # Read and strip input

        if not date_str:
            print("Info: Keine Datumseingabe, wird als 'None' gespeichert.") # Optional: Info für den User
            return None # Gibt None zurück, wenn nur Enter gedrückt wurde
        try:
            datetime.datetime.strptime(date_str, "%d.%m.%Y")
            return date_str # Gibt den validierten String zurück
        except ValueError:
            # Diese Meldung erscheint nur, wenn etwas eingegeben wurde, das *kein* gültiges Datum ist.
            print("Falsches Format oder ungültiges Datum. Bitte dd.mm.yyyy oder Enter (für keine Angabe) eingeben.")
            # Die Schleife beginnt erneut.

def userinput_ecog(prompt):
    """
    Fordert den Benutzer zur Eingabe des ECOG-Status (0-4, 'x' oder Enter) auf.
    Gibt den validierten Wert (Integer 0-4 oder None) zurück.

    Args:
        prompt (str): Die anzuzeigende Eingabeaufforderung.

    Returns:
        int | None: Der validierte ECOG-Status (0-4) oder None für 'x' oder leere Eingabe.
    """
    while True:
        print(prompt, end=" ")
        user_input = input().strip().lower()
        # --- ÄNDERUNG ---
        if not user_input: # Prüfe auf leere Eingabe zuerst
             return None # Leere Eingabe bedeutet auch "unbekannt" -> None
        # --- Ende Änderung ---
        if user_input == "x":
            return None # 'x' bedeutet auch "unbekannt" -> None
        if user_input.isdigit() and int(user_input) in range(5): # 0, 1, 2, 3, 4
            return int(user_input)
        print("Ungültige Eingabe. Bitte 0-4, 'x' oder Enter (für keine Angabe) eingeben.")

def userinput_stat(prompt):
    """
    Fordert den Benutzer zu einer Ja/Nein-Eingabe (j/n oder Enter) auf.

    Args:
        prompt (str): Die anzuzeigende Eingabeaufforderung.

    Returns:
        str | None: 'j', 'n' oder None bei leerer Eingabe.
    """
    while True:
        print(prompt, end=" ")
        user_input = input().strip().lower()
        # --- ÄNDERUNG ---
        if not user_input:
            return None # Erlaube leere Eingabe -> None
        # --- Ende Änderung ---
        if user_input in ["j", "n"]:
            return user_input
        print("Ungültige Eingabe. Bitte 'j', 'n' oder Enter (für keine Angabe) eingeben.")

def userinput_behandlungskonzept(prompt_serie1):
    """
    Fordert den Benutzer zur Eingabe von bis zu vier Behandlungsserien auf.
    Leere Eingabe ist für alle Serien erlaubt und wird als None gespeichert.

    Args:
        prompt_serie1 (str): Die Eingabeaufforderung für die erste Serie.

    Returns:
        tuple: Ein Tupel (serie1, serie2, serie3, serie4), wobei jeder Wert
               ein String oder None ist.
    """
    behandlungskonzept_serie1 = None
    behandlungskonzept_serie2 = None
    behandlungskonzept_serie3 = None
    behandlungskonzept_serie4 = None

    # --- Serie 1 ---
    # Verwendung von userinput_freitext, das jetzt None bei leerer Eingabe zurückgibt
    behandlungskonzept_serie1 = userinput_freitext(prompt_serie1)
    if behandlungskonzept_serie1 is None:
        print("Info: Serie 1 wurde übersprungen (keine Eingabe).")

    # --- Serie 2 (Optional) ---
    # --- ÄNDERUNG: userinput_stat gibt jetzt auch None zurück ---
    add_serie2 = userinput_stat("Serie 2 erfassen? (j/n):")
    if add_serie2 == 'j':
        behandlungskonzept_serie2 = userinput_freitext("Bitte Behandlungskonzept eingeben - Serie 2 (Enter zum Überspringen):")
        if behandlungskonzept_serie2 is None:
            print("Info: Serie 2 wurde übersprungen.")

        # --- Serie 3 (Optional, only if Serie 2 was added *and* has value) ---
        if behandlungskonzept_serie2 is not None: # Nur fragen, wenn Serie 2 nicht übersprungen wurde
            add_serie3 = userinput_stat("Serie 3 erfassen? (j/n):")
            if add_serie3 == 'j':
                behandlungskonzept_serie3 = userinput_freitext("Bitte Behandlungskonzept eingeben - Serie 3 (Enter zum Überspringen):")
                if behandlungskonzept_serie3 is None:
                    print("Info: Serie 3 wurde übersprungen.")

                # --- Serie 4 (Optional, only if Serie 3 was added *and* has value) ---
                if behandlungskonzept_serie3 is not None:
                    add_serie4 = userinput_stat("Serie 4 erfassen? (j/n):")
                    if add_serie4 == 'j':
                        behandlungskonzept_serie4 = userinput_freitext("Bitte Behandlungskonzept eingeben - Serie 4 (Enter zum Überspringen):")
                        if behandlungskonzept_serie4 is None:
                            print("Info: Serie 4 wurde übersprungen.")

    # Gibt None zurück für nicht erfasste/übersprungene Serien
    return behandlungskonzept_serie1, behandlungskonzept_serie2, behandlungskonzept_serie3, behandlungskonzept_serie4

# ==============================================================================
# Ende der zentralisierten User-Input Funktionen
# ==============================================================================


###################################
###################################

def get_benutzerdaten():
    """
    Liest Nachname und Vorname des Benutzers aus der Datei ~/patdata/benutzerdaten.txt.

    Stellt sicher, dass der patdata-Ordner existiert.
    Liest die Datei und prüft auf gültige Einträge 'Nachname=' und 'Vorname='.

    Returns:
        tuple: Ein Tupel (nachname, vorname). Gibt (None, None) zurück,
               wenn die Datei nicht existiert, ungültig ist oder die Namen fehlen.
    """
    benutzerdaten_file = os.path.join(patdata_dir, "benutzerdaten.txt")

    nachname = None
    vorname = None

    # Stelle sicher, dass das patdata-Verzeichnis existiert
    # Normalerweise sollte dies durch andere Initialisierungsprozesse geschehen,
    # aber zur Sicherheit hier prüfen/erstellen.
    try:
        os.makedirs(patdata_dir, exist_ok=True)
    except OSError as e:
        print(f"FEHLER: Konnte das Verzeichnis '{patdata_dir}' nicht erstellen: {e}")
        # In diesem Fall kann die Datei sicher nicht gelesen oder geschrieben werden.
        # Es ist sinnvoll, hier None, None zurückzugeben, da die Daten nicht verfügbar sind.
        return None, None


    if os.path.exists(benutzerdaten_file):
        try:
            with open(benutzerdaten_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            data = {}
            for line in lines:
                line = line.strip()
                if '=' in line:
                    # Teile nur beim ersten '='
                    key, value = line.split('=', 1)
                    data[key.strip()] = value.strip()

            # Prüfe, ob die Schlüssel existieren UND die Werte nicht leer sind
            if "Nachname" in data and data["Nachname"] and \
               "Vorname" in data and data["Vorname"]:
                nachname = data["Nachname"]
                vorname = data["Vorname"]
            else:
                # Datei existiert, aber Inhalt ist ungültig oder unvollständig
                print(f"WARNUNG: Die Datei '{benutzerdaten_file}' enthält ungültige oder fehlende Einträge für Nachname/Vorname.")
                # nachname und vorname bleiben None

        except Exception as e:
            print(f"FEHLER beim Lesen oder Verarbeiten der Datei '{benutzerdaten_file}': {e}")
            # Bei Lesefehler bleiben nachname und vorname None

    if nachname is None or vorname is None:
         print(f"INFO: Benutzerdaten (Nachname/Vorname) konnten nicht aus '{benutzerdaten_file}' geladen werden.")
         return None, None

    return nachname, vorname

def save_benutzerdaten(nachname, vorname):
    """
    Speichert Nachname und Vorname des Benutzers in der Datei ~/patdata/benutzerdaten.txt.

    Erstellt das Verzeichnis ~/patdata, falls es nicht existiert.
    Überschreibt die Datei, falls sie bereits existiert.

    Args:
        nachname (str): Der Nachname des Benutzers.
        vorname (str): Der Vorname des Benutzers.

    Returns:
        bool: True bei Erfolg, False bei Fehler (z.B. ungültige Eingabe, Schreibfehler).
    """
    benutzerdaten_file = os.path.join(patdata_dir, "benutzerdaten.txt")

    # Eingabevalidierung
    if not nachname or not isinstance(nachname, str) or not nachname.strip():
        print("FEHLER: Ungültiger oder leerer Nachname für das Speichern angegeben.")
        return False
    if not vorname or not isinstance(vorname, str) or not vorname.strip():
        print("FEHLER: Ungültiger oder leerer Vorname für das Speichern angegeben.")
        return False

    # Bereinige die Eingaben leicht (entferne führende/nachfolgende Leerzeichen)
    nachname = nachname.strip()
    vorname = vorname.strip()

    try:
        # Stelle sicher, dass das Verzeichnis existiert, erstelle es bei Bedarf
        os.makedirs(patdata_dir, exist_ok=True)

        # Schreibe die Daten in die Datei (überschreibt bestehende Datei)
        with open(benutzerdaten_file, 'w', encoding='utf-8') as f:
            f.write(f"Nachname={nachname}\n")
            f.write(f"Vorname={vorname}\n")
        print(f"Benutzerdaten erfolgreich in '{benutzerdaten_file}' gespeichert.")
        return True

    except OSError as e:
        # Spezieller Fehler für Verzeichniserstellung
        print(f"FEHLER: Konnte das Verzeichnis '{patdata_dir}' nicht erstellen oder darauf zugreifen: {e}")
        return False
    except IOError as e:
         # Fehler beim Schreiben der Datei
        print(f"FEHLER: Konnte nicht in die Datei '{benutzerdaten_file}' schreiben: {e}")
        return False
    except Exception as e:
        # Andere unerwartete Fehler
        print(f"FEHLER beim Speichern der Benutzerdaten in '{benutzerdaten_file}': {e}")
        return False


###################################
###################################
def signation_benutzer_eintragen():
    pyautogui = importlib.import_module("pyautogui") if "pyautogui" not in sys.modules else sys.modules["pyautogui"]
    clipboard = importlib.import_module("clipboard") if "clipboard" not in sys.modules else sys.modules["clipboard"]
    benutzer_nachname, benutzer_vorname = get_benutzerdaten()
    if benutzer_nachname is None or benutzer_vorname is None:
        print("Benutzerdaten konnte nicht aus benutzerdaten.txt ausgelesen werden (im patdata Folder), bitte benutzerdaten.txt anlegen und \n\nVorname=xxx\nNachname=xxx\n\n eingeben und speichern.")
    benutzererfassung = benutzer_nachname + " " + benutzer_vorname
    clipboard.copy(benutzererfassung)
    pyautogui.hotkey('ctrl', 'v')
    pyautogui.typewrite(" ")
    pyautogui.press('backspace')
    time.sleep(0.4)
    pyautogui.press('enter')

###################################
###################################
try:
    from symptomblock_mapping import MAPPING_SYMPTOMBLOCK
except ImportError:
    print("WARNUNG: symptomblock_mapping.py nicht gefunden...")
    MAPPING_SYMPTOMBLOCK = {}

def _get_symptomblock_image_from_icd(icd_code, geschlecht):
    """
    Sucht im Mapping nach dem passenden Symptomblock-Button für einen ICD-Code.
    
    Args:
        icd_code (str): Der ICD-Code des Patienten (z.B. "C71.3").
        geschlecht (str): Das Geschlecht ('M' oder 'W') für Spezialfälle.

    Returns:
        str | None: Der Dateiname des PNG-Buttons oder None, wenn kein Match gefunden wurde.
    """
    if not icd_code or not isinstance(icd_code, str):
        return None

    for icd_prefixes, button_info in MAPPING_SYMPTOMBLOCK.items():
        for prefix in icd_prefixes:
            if icd_code.startswith(prefix):
                # Prüfen, ob es ein geschlechtsspezifischer Eintrag ist
                if isinstance(button_info, dict):
                    # Gib den passenden Button für das Geschlecht zurück, mit 'M' als Fallback
                    return button_info.get(geschlecht, button_info.get("M"))
                else:
                    # Standardfall: Gib den Button-Namen direkt zurück
                    return button_info
    
    # Wenn die Schleife durchläuft, ohne einen Treffer zu finden
    return None

###################################
###################################

def symptome_vor_rt_anlegen(chemotherapie, icd_code, geschlecht):
    local_screenshots_dir = os.path.join(screenshots_dir, 'UNIVERSAL', 'bereich_berichte')
    print(f'local_screenshots_dir angelegt in {local_screenshots_dir}')
    
    navigiere_bereich_berichte()
    if not find_and_click_button('button_neu.png', base_path=local_screenshots_dir): print("button_neu.png nicht gefunden"); return False
    if not find_and_click_button('button_suchleiste.png', base_path=local_screenshots_dir): print("button_suchleiste.png nicht gefunden"); return False
    symp = "symptome"
    clipboard.copy(symp)
    pyautogui.hotkey('ctrl', 'v')
    if not find_and_click_button('button_sympakuttox.png', base_path=local_screenshots_dir): print("button_sympakuttox.png nicht gefunden"); return False
    if not find_button('button_sympakuttox_confirm.png', base_path=local_screenshots_dir, max_attempts=100): print("button_sympakuttox_confirm.png nicht gefunden"); return False
    time.sleep(0.4)
    if not find_and_click_button('button_sympakuttox_confirm.png', base_path=local_screenshots_dir, max_attempts=100): print("button_sympakuttox_confirm.png nicht gefunden"); return False
    pyautogui.press('down')
    pyautogui.press('enter')
    ctrl_tabs(9)
    time.sleep(0.1)
    pyautogui.press('enter')
    print(f"Chemotherapie Argument zugespielt: {chemotherapie}. Fahre damit fort.")
    if chemotherapie == 'ja':
        print("chemotherapie == ja gefunden, lege mit Blutbildveränderungen an.")
        pyautogui.press('enter')
    elif chemotherapie == 'nein':
        print("chemotherapie == nein gefunden, lege ohne Blutbildveränderungen an.")
        pyautogui.press('down')
        pyautogui.press('enter')
    else:
        print("chemotherapie weder ja noch nein gefunden. Lege ohne an Blutbild an.")
        pyautogui.press('down')
        pyautogui.press('enter')

    while True:
        if find_button(image_name='button_symptomauswahl_offen.png', base_path=local_screenshots_dir, max_attempts=1):
            print("Gruppe auswählen noch offen, Navigation pausiert.")
            time.sleep(0.05)
        else:
            print("Gruppe auswählen nicht mehr offen, fahre fort.")
            break

    # === NEUER CODEBLOCK SPEZIFISCHE TOX GRUPPE ===
    symptom_button_image = _get_symptomblock_image_from_icd(icd_code, geschlecht)
    if symptom_button_image:
    
        print(f"INFO: Passender Symptomblock für ICD '{icd_code}' gefunden: {symptom_button_image}")
        print("INFO: Versuche, den zusätzlichen Symptomblock anzuklicken...")
        for attempt in range(30):
            if not find_and_click_button("button_symptomblock_auswahl.png", base_path=local_screenshots_dir, max_attempts=1):
                print("WARNUNG: Konnte den Button 'button_symptomblock_auswahl.png' nicht finden. Probiere button_symptomblock_auswahl_rot.png ...")
                if not find_and_click_button("button_symptomblock_auswahl_rot.png", base_path=local_screenshots_dir, max_attempts=1):
                    print("WARNUNG: Konnte den Button 'button_symptomblock_auswahl_rot.png' nicht finden. Loop erneut (max 50)...")
                    time.sleep(0.05)
                else:
                    print("INFO: Button 'button_symptomblock_auswahl_rot.png' gefunden und angeklickt.")
                    break
            else:
                print("INFO: Button 'button_symptomblock_auswahl.png' gefunden und angeklickt.")
                break

        if not find_and_click_button(symptom_button_image, "Spezifischer Symptomblock", base_path=local_screenshots_dir, max_attempts=20, interval=0.05):
            print(f"WARNUNG: Konnte den spezifischen Symptomblock-Button '{symptom_button_image}' nicht klicken.")
            return False
        #Warten, bis alle Nebenwirkungen geladen            
        while True:
            if find_button(image_name='button_symptomauswahl_offen.png', base_path=local_screenshots_dir, max_attempts=1):
                print("Gruppe auswählen noch offen, Navigation pausiert.")
                time.sleep(0.05)
            else:
                print("Gruppe auswählen nicht mehr offen, fahre fort.")
                break
    else:
        print(f"INFO: Kein spezifischer Symptomblock für ICD-Code '{icd_code}' im Mapping gefunden. Lege nur General Symptomblock an.")
        
    # === NEUER CODEBLOCK ENDE ===


    if chemotherapie == 'ja':
        print("chemotherapie-Argument existiert und ist nicht gleich 'nein'. Wähle path mit chemotherapie-Akuttox aus.")
        import ctcaeauslesen
        hb_grade, leucos_grade, lymphos_grade, neutros_grade, thrombos_grade  = ctcaeauslesen.main()
        print(hb_grade, leucos_grade, lymphos_grade, neutros_grade, thrombos_grade)
        navigiere_bereich_berichte()

        if not find_and_click_button('button_leere_zeile.png', base_path=local_screenshots_dir, max_attempts=100): print("button_leere_zeile.png nicht gefunden"); return False
        ctrl_tabs(1)

        for _ in range(9): #füllt alles aus bis inkl. peripheral neuropathy
                    pyautogui.press('down')
                    pyautogui.hotkey('ctrl', 'tab')
                    pyautogui.press('enter')
                    time.sleep(0.05)
        
        print("Starte Eintragen der CTCAE Hämatogramm Veränderungen...")

        pyautogui.press('down'); ctrl_tabs(1) #Anemia Zeile
        if isinstance(hb_grade, int):
            print(f"hb_grade = integer erkannt. Führe tabs aus: {hb_grade}, danach Enter")
            ctrl_tabs((hb_grade))
            pyautogui.press('enter')
        elif not isinstance(hb_grade, int):
            print(f"ACHTUNG!!! hb_grade =/= integer erkannt. Es konnte kein Laborwert für Hb ausgelesen werden!! Ggf. in letzten 6 Monaten kein vollständiges Hämatogramm erfolgt?")
            print("Überspringe Ankreuzen des CTCAE-Grades, gehe zu nächstem.")

        pyautogui.press('down'); ctrl_tabs(1) #WBC Zeile
        if isinstance(leucos_grade, int):
            print(f"leucos_grade = integer erkannt. Führe tabs aus: {leucos_grade}, danach Enter")
            ctrl_tabs((leucos_grade))
            pyautogui.press('enter')
        elif not isinstance(leucos_grade, int):
            print(f"ACHTUNG!!! leucos_grade =/= integer erkannt. Es konnte kein Laborwert für Hb ausgelesen werden!! Ggf. in letzten 6 Monaten kein vollständiges Hämatogramm erfolgt?")
            print("Überspringe Ankreuzen des CTCAE-Grades, gehe zu nächstem.")

        pyautogui.press('down'); ctrl_tabs(1) #Lymphos Zeile
        if isinstance(lymphos_grade, int):
            print(f"lymphos_grade = integer erkannt. Führe tabs aus: {lymphos_grade}, danach Enter")
            ctrl_tabs((lymphos_grade))
            pyautogui.press('enter')
        elif not isinstance(lymphos_grade, int):
            print(f"ACHTUNG!!! lymphos_grade =/= integer erkannt. Es konnte kein Laborwert für Hb ausgelesen werden!! Ggf. in letzten 6 Monaten kein vollständiges Hämatogramm erfolgt?")
            print("Überspringe Ankreuzen des CTCAE-Grades, gehe zu nächstem.")

        pyautogui.press('down'); ctrl_tabs(1) #Neutros Zeile
        if isinstance(neutros_grade, int):
            print(f"neutros_grade = integer erkannt. Führe tabs aus: {neutros_grade}, danach Enter")
            ctrl_tabs((neutros_grade))
            pyautogui.press('enter')
        elif not isinstance(neutros_grade, int):
            print(f"ACHTUNG!!! neutros_grade =/= integer erkannt. Es konnte kein Laborwert für Hb ausgelesen werden!! Ggf. in letzten 6 Monaten kein vollständiges Hämatogramm erfolgt?")
            print("Überspringe Ankreuzen des CTCAE-Grades, gehe zu nächstem.")

        pyautogui.press('down'); ctrl_tabs(1) #Thrombos Zeile
        if isinstance(thrombos_grade, int):
            print(f"thrombos_grade = integer erkannt. Führe tabs aus: {thrombos_grade}, danach Enter")
            ctrl_tabs((thrombos_grade))
            pyautogui.press('enter')
        elif not isinstance(thrombos_grade, int):
            print(f"ACHTUNG!!! thrombos_grade =/= integer erkannt. Es konnte kein Laborwert für Hb ausgelesen werden!! Ggf. in letzten 6 Monaten kein vollständiges Hämatogramm erfolgt?")
            print("Überspringe Ankreuzen des CTCAE-Grades, gehe zu nächstem.")



        #GENERAL BLOCK bearbeitet, jetzt check auf spez. UAW BLOCK
        if symptom_button_image:
            mapping_number_tox = {"button_symptomblock_brain.png": 8,
                                "button_symptomblock_orl.png": 12,
                                "button_symptomblock_abdomen.png": 9,
                                "button_symptomblock_thorax.png": 8,
                                "button_symptomblock_pelvismale.png": 10,
                                "button_symptomblock_pelvisfemale.png": 12,
                                "button_symptomblock_bone_extremities.png": 7, 
                                "button_symptomblock_breast.png": 6}
        
        #je nach mapping: number of tx
        number_tox = mapping_number_tox.get(symptom_button_image, 6) if symptom_button_image else 6
        print(f"\n\n\n führe {number_tox} loops aus, um die spezifischen Toxizitäten für {symptom_button_image} zu erfassen.")
        for _ in range(number_tox):
            pyautogui.press('down')
            pyautogui.hotkey('ctrl', 'tab')
            pyautogui.press('enter')
            time.sleep(0.05)


    else:
        for _ in range(9):
            pyautogui.press('down')
            pyautogui.hotkey('ctrl', 'tab')
            pyautogui.press('enter')
            time.sleep(0.05)

        #GENERAL BLOCK bearbeitet, jetzt check auf spez. UAW BLOCK
        if symptom_button_image:
            mapping_number_tox = {"button_symptomblock_brain.png": 8,
                                "button_symptomblock_orl.png": 12,
                                "button_symptomblock_abdomen.png": 9,
                                "button_symptomblock_thorax.png": 8,
                                "button_symptomblock_pelvismale.png": 10,
                                "button_symptomblock_pelvisfemale.png": 12,
                                "button_symptomblock_bone_extremities.png": 7, 
                                "button_symptomblock_breast.png": 6}
        
        #je nach mapping: number of tx
        number_tox = mapping_number_tox.get(symptom_button_image, 6) if symptom_button_image else 6
        print(f"\n\n\n führe {number_tox} loops aus, um die spezifischen Toxizitäten für {symptom_button_image} zu erfassen.")
        for _ in range(number_tox):
            pyautogui.press('down')
            pyautogui.hotkey('ctrl', 'tab')
            pyautogui.press('enter')
            time.sleep(0.05)



        
    if not find_and_click_button('button_speichern.png', base_path=local_screenshots_dir): print("'button_speichern.png nicht gefunden"); return False
    return True

###################################
###################################

def akuttox_nach_rt_anlegen(chemotherapie, icd_code, geschlecht):
    local_screenshots_dir = os.path.join(screenshots_dir, 'UNIVERSAL', 'bereich_berichte')
    print(f'local_screenshots_dir angelegt in {local_screenshots_dir}')
    
    navigiere_bereich_berichte()
    if not find_and_click_button('button_neu.png', base_path=local_screenshots_dir): print("button_neu.png nicht gefunden"); return False
    if not find_and_click_button('button_suchleiste.png', base_path=local_screenshots_dir): print("button_suchleiste.png nicht gefunden"); return False
    symp = "symptome"
    clipboard.copy(symp)
    pyautogui.hotkey('ctrl', 'v')
    if not find_and_click_button('button_sympakuttox.png', base_path=local_screenshots_dir): print("button_sympakuttox.png nicht gefunden"); return False
    if not find_button('button_sympakuttox_confirm.png', base_path=local_screenshots_dir, max_attempts=100): print("button_sympakuttox_confirm.png nicht gefunden"); return False
    time.sleep(0.4)
    if not find_and_click_button('button_sympakuttox_confirm.png', base_path=local_screenshots_dir, max_attempts=100): print("button_sympakuttox_confirm.png nicht gefunden"); return False
    pyautogui.press('enter') #Akuttox belassen

    ctrl_tabs(9)
    pyautogui.press('enter') #Auswahl Gruppe Nebenwirkungen

    if chemotherapie == 'ja':
        print("chemotherapie == ja gefunden, lege mit Blutbildveränderungen an.")
        pyautogui.press('enter')
    elif chemotherapie == 'nein':
        print("chemotherapie == nein gefunden, lege ohne Blutbildveränderungen an.")
        pyautogui.press('down')
        pyautogui.press('enter')
    else:
        print("chemotherapie weder ja noch nein gefunden. Lege ohne an Blutbild an.")
        pyautogui.press('down')
        pyautogui.press('enter')

    #Warten, bis alle Nebenwirkungen geladen            
    while True:
        if find_button(image_name='button_symptomauswahl_offen.png', base_path=local_screenshots_dir, max_attempts=1):
            print("Gruppe auswählen noch offen, Navigation pausiert.")
            time.sleep(0.05)
        else:
            print("Gruppe auswählen nicht mehr offen, fahre fort.")
            break

    # === NEUER CODEBLOCK SPEZIFISCHE TOX GRUPPE ===
    symptom_button_image = _get_symptomblock_image_from_icd(icd_code, geschlecht)
    if symptom_button_image:
    
        print(f"INFO: Passender Symptomblock für ICD '{icd_code}' gefunden: {symptom_button_image}")
        print("INFO: Versuche, den zusätzlichen Symptomblock anzuklicken...")
        for attempt in range(30):
            if not find_and_click_button("button_symptomblock_auswahl.png", base_path=local_screenshots_dir, max_attempts=1):
                print("WARNUNG: Konnte den Button 'button_symptomblock_auswahl.png' nicht finden. Probiere button_symptomblock_auswahl_rot.png ...")
                if not find_and_click_button("button_symptomblock_auswahl_rot.png", base_path=local_screenshots_dir, max_attempts=1):
                    print("WARNUNG: Konnte den Button 'button_symptomblock_auswahl_rot.png' nicht finden. Loop erneut (max 50)...")
                    time.sleep(0.05)
                else:
                    print("INFO: Button 'button_symptomblock_auswahl_rot.png' gefunden und angeklickt.")
                    break
            else:
                print("INFO: Button 'button_symptomblock_auswahl.png' gefunden und angeklickt.")
                break

        if not find_and_click_button(symptom_button_image, "Spezifischer Symptomblock", base_path=local_screenshots_dir, max_attempts=20, interval=0.05):
            print(f"WARNUNG: Konnte den spezifischen Symptomblock-Button '{symptom_button_image}' nicht klicken.")
            return False
        #Warten, bis alle Nebenwirkungen geladen            
        while True:
            if find_button(image_name='button_symptomauswahl_offen.png', base_path=local_screenshots_dir, max_attempts=1):
                print("Gruppe auswählen noch offen, Navigation pausiert.")
                time.sleep(0.05)
            else:
                print("Gruppe auswählen nicht mehr offen, fahre fort.")
                break
    else:
        print(f"INFO: Kein spezifischer Symptomblock für ICD-Code '{icd_code}' im Mapping gefunden. Lege nur General Symptomblock an.")

    # === NEUER CODEBLOCK ENDE ===

    if chemotherapie == 'ja':
        import ctcaeauslesen
        hb_grade, leucos_grade, lymphos_grade, neutros_grade, thrombos_grade  = ctcaeauslesen.main()
        print(hb_grade, leucos_grade, lymphos_grade, neutros_grade, thrombos_grade)
        navigiere_bereich_berichte()

        if not find_and_click_button('button_leere_zeile.png', base_path=local_screenshots_dir, max_attempts=100): print("button_leere_zeile.png nicht gefunden"); return False
        ctrl_tabs(1)

        for _ in range(9): #füllt alles aus bis inkl. peripheral neuropathy
                    pyautogui.press('down')
                    pyautogui.hotkey('ctrl', 'tab')
                    pyautogui.press('enter')
                    time.sleep(0.05)
        
        print("Starte Eintragen der CTCAE Hämatogramm Veränderungen...")

        pyautogui.press('down'); ctrl_tabs(1) #Anemia Zeile
        if isinstance(hb_grade, int):
            print(f"hb_grade = integer erkannt. Führe tabs aus: {hb_grade}, danach Enter")
            ctrl_tabs((hb_grade))
            pyautogui.press('enter')
        elif not isinstance(hb_grade, int):
            print(f"ACHTUNG!!! hb_grade =/= integer erkannt. Es konnte kein Laborwert für Hb ausgelesen werden!! Ggf. in letzten 6 Monaten kein vollständiges Hämatogramm erfolgt?")
            print("Überspringe Ankreuzen des CTCAE-Grades, gehe zu nächstem.")

        pyautogui.press('down'); ctrl_tabs(1) #WBC Zeile
        if isinstance(leucos_grade, int):
            print(f"leucos_grade = integer erkannt. Führe tabs aus: {leucos_grade}, danach Enter")
            ctrl_tabs((leucos_grade))
            pyautogui.press('enter')
        elif not isinstance(leucos_grade, int):
            print(f"ACHTUNG!!! leucos_grade =/= integer erkannt. Es konnte kein Laborwert für Hb ausgelesen werden!! Ggf. in letzten 6 Monaten kein vollständiges Hämatogramm erfolgt?")
            print("Überspringe Ankreuzen des CTCAE-Grades, gehe zu nächstem.")

        pyautogui.press('down'); ctrl_tabs(1) #Lymphos Zeile
        if isinstance(lymphos_grade, int):
            print(f"lymphos_grade = integer erkannt. Führe tabs aus: {lymphos_grade}, danach Enter")
            ctrl_tabs((lymphos_grade))
            pyautogui.press('enter')
        elif not isinstance(lymphos_grade, int):
            print(f"ACHTUNG!!! lymphos_grade =/= integer erkannt. Es konnte kein Laborwert für Hb ausgelesen werden!! Ggf. in letzten 6 Monaten kein vollständiges Hämatogramm erfolgt?")
            print("Überspringe Ankreuzen des CTCAE-Grades, gehe zu nächstem.")

        pyautogui.press('down'); ctrl_tabs(1) #Neutros Zeile
        if isinstance(neutros_grade, int):
            print(f"neutros_grade = integer erkannt. Führe tabs aus: {neutros_grade}, danach Enter")
            ctrl_tabs((neutros_grade))
            pyautogui.press('enter')
        elif not isinstance(neutros_grade, int):
            print(f"ACHTUNG!!! neutros_grade =/= integer erkannt. Es konnte kein Laborwert für Hb ausgelesen werden!! Ggf. in letzten 6 Monaten kein vollständiges Hämatogramm erfolgt?")
            print("Überspringe Ankreuzen des CTCAE-Grades, gehe zu nächstem.")

        pyautogui.press('down'); ctrl_tabs(1) #Thrombos Zeile
        if isinstance(thrombos_grade, int):
            print(f"thrombos_grade = integer erkannt. Führe tabs aus: {thrombos_grade}, danach Enter")
            ctrl_tabs((thrombos_grade))
            pyautogui.press('enter')
        elif not isinstance(thrombos_grade, int):
            print(f"ACHTUNG!!! thrombos_grade =/= integer erkannt. Es konnte kein Laborwert für Hb ausgelesen werden!! Ggf. in letzten 6 Monaten kein vollständiges Hämatogramm erfolgt?")
            print("Überspringe Ankreuzen des CTCAE-Grades, gehe zu nächstem.")

        #GENERAL BLOCK bearbeitet, jetzt check auf spez. UAW BLOCK
        if symptom_button_image:
            mapping_number_tox = {"button_symptomblock_brain.png": 8,
                                "button_symptomblock_orl.png": 12,
                                "button_symptomblock_abdomen.png": 9,
                                "button_symptomblock_thorax.png": 8,
                                "button_symptomblock_pelvismale.png": 10,
                                "button_symptomblock_pelvisfemale.png": 12,
                                "button_symptomblock_bone_extremities.png": 7, 
                                "button_symptomblock_breast.png": 6}
    
        #je nach mapping: number of tx
        number_tox = mapping_number_tox.get(symptom_button_image, 6) if symptom_button_image else 6
        print(f"\n\n\n führe {number_tox} loops aus, um die spezifischen Toxizitäten für {symptom_button_image} zu erfassen.")
        for _ in range(number_tox):
            pyautogui.press('down')
            pyautogui.hotkey('ctrl', 'tab')
            pyautogui.press('enter')
            time.sleep(0.05)

    else:
        print("chemotherapie-Variable = nein oder None, lege UAW ohne Systemtherapie an...")
        for _ in range(9):
            pyautogui.press('down')
            pyautogui.hotkey('ctrl', 'tab')
            pyautogui.press('enter')
            time.sleep(0.05)

        #GENERAL BLOCK bearbeitet, jetzt check auf spez. UAW BLOCK
        if symptom_button_image:
            mapping_number_tox = {"button_symptomblock_brain.png": 8,
                                "button_symptomblock_orl.png": 12,
                                "button_symptomblock_abdomen.png": 9,
                                "button_symptomblock_thorax.png": 8,
                                "button_symptomblock_pelvismale.png": 10,
                                "button_symptomblock_pelvisfemale.png": 12,
                                "button_symptomblock_bone_extremities.png": 7, 
                                "button_symptomblock_breast.png": 6}
        
        #je nach mapping: number of tx
        number_tox = mapping_number_tox.get(symptom_button_image, 6) if symptom_button_image else 6
        print(f"\n\n\n führe {number_tox} loops aus, um die spezifischen Toxizitäten für {symptom_button_image} zu erfassen.")
        for _ in range(number_tox):
            pyautogui.press('down')
            pyautogui.hotkey('ctrl', 'tab')
            pyautogui.press('enter')
            time.sleep(0.05)

    if not find_and_click_button('button_speichern.png', base_path=local_screenshots_dir): print("'button_speichern.png nicht gefunden"); return False
    return True


###################################
###################################

def nachsorgeformular_anlegen(nachsorgeformular_typ, bericht_typ, chemotherapie, icd_code, geschlecht):
    print("Starte nachsorgeformular_anlegen mit Argumenten nachsorgeformular_typ, bericht_typ, chemotherapie")
    local_screenshots_dir = os.path.join(screenshots_dir, 'UNIVERSAL', 'bereich_berichte')
    navigiere_bereich_berichte()
    if not find_and_click_button('button_neu.png', base_path=local_screenshots_dir): print('button_neu.png nicht gefunden'); return False
    if not find_and_click_button('button_suchleiste.png', base_path=local_screenshots_dir): print('button_suchleiste.png nicht gefunden'); return False
    nachsorge = 'nachsorge'
    clipboard.copy(nachsorge)
    pyautogui.hotkey('ctrl', 'v')

    # --- Typ Kurativ ---
    if nachsorgeformular_typ == 'kurativ':
        if not find_and_click_button('button_nachsorge_kurativ.png', base_path=local_screenshots_dir): print('button_nachsorge_kurativ.png nicht gefunden'); return False # Added base_path
        if not find_button('button_nachsorge_kurativ_confirm.png', base_path=local_screenshots_dir, max_attempts=100): print('button_nachsorge_kurativ_confirm.png nicht gefunden'); return False # Added base_path
        time.sleep(0.3)
        if not find_and_click_button('button_nachsorge_kurativ_confirm.png', base_path=local_screenshots_dir, max_attempts=100): print('button_nachsorge_kurativ_confirm.png nicht gefunden'); return False # Added base_path

        #Auswahl Patient lebt
        ctrl_tabs(5) 
        pyautogui.press('enter')

        #Auswahl Nachsorgeart
        ctrl_tabs(6)
        pyautogui.press('enter')
        if bericht_typ == 'k':
              pyautogui.press('down'); pyautogui.press('enter')
        elif bericht_typ == 't':
              pyautogui.press('down'); pyautogui.press('down'); pyautogui.press('enter')
        else:
              print('bericht_typ weder k noch t, überspringe Feld')
              pyautogui.press('enter')

        #Tox>Grad 3 Nein auswählen.
        ctrl_tabs(22)
        pyautogui.press('enter')

        #Nebenwirkungen eintragen
        ctrl_tabs(2)
        pyautogui.press('enter')


        # Block für MIT Chemo
        if chemotherapie == 'ja':
            pyautogui.press('enter') #Auswahl WITH syst therapy
            print("INFO: Auswahl 'WITH syst therapy' getroffen (Chemo=True)")

            #Warten, bis alle Nebenwirkungen geladen            
            while True:
                if find_button(image_name='button_symptomauswahl_offen.png', base_path=local_screenshots_dir, max_attempts=1):
                    print("Gruppe auswählen noch offen, Navigation pausiert.")
                    time.sleep(0.05)
                else:
                    print("Gruppe auswählen nicht mehr offen, fahre fort.")
                    break

            # === NEUER CODEBLOCK SPEZIFISCHE TOX GRUPPE ===
            symptom_button_image = _get_symptomblock_image_from_icd(icd_code, geschlecht)
            if symptom_button_image:
            
                print(f"INFO: Passender Symptomblock für ICD '{icd_code}' gefunden: {symptom_button_image}")
                print("INFO: Versuche, den zusätzlichen Symptomblock anzuklicken...")
                for attempt in range(30):
                    if not find_and_click_button("button_symptomblock_auswahl.png", base_path=local_screenshots_dir, max_attempts=1):
                        print("WARNUNG: Konnte den Button 'button_symptomblock_auswahl.png' nicht finden. Probiere button_symptomblock_auswahl_rot.png ...")
                        if not find_and_click_button("button_symptomblock_auswahl_rot.png", base_path=local_screenshots_dir, max_attempts=1):
                            print("WARNUNG: Konnte den Button 'button_symptomblock_auswahl_rot.png' nicht finden. Loop erneut (max 50)...")
                            time.sleep(0.05)
                        else:
                            print("INFO: Button 'button_symptomblock_auswahl_rot.png' gefunden und angeklickt.")
                            break
                    else:
                        print("INFO: Button 'button_symptomblock_auswahl.png' gefunden und angeklickt.")
                        break

                if not find_and_click_button(symptom_button_image, "Spezifischer Symptomblock", base_path=local_screenshots_dir, max_attempts=20, interval=0.05):
                    print(f"WARNUNG: Konnte den spezifischen Symptomblock-Button '{symptom_button_image}' nicht klicken.")
                    return False
                #Warten, bis alle Nebenwirkungen geladen            
                while True:
                    if find_button(image_name='button_symptomauswahl_offen.png', base_path=local_screenshots_dir, max_attempts=1):
                        print("Gruppe auswählen noch offen, Navigation pausiert.")
                        time.sleep(0.05)
                    else:
                        print("Gruppe auswählen nicht mehr offen, fahre fort.")
                        break
            else:
                print(f"INFO: Kein spezifischer Symptomblock für ICD-Code '{icd_code}' im Mapping gefunden. Lege nur General Symptomblock an.")
                
            # === NEUER CODEBLOCK ENDE ===


            #Holen der CTCAE Grade
            import ctcaeauslesen
            hb_grade, leucos_grade, lymphos_grade, neutros_grade, thrombos_grade  = ctcaeauslesen.main()
            print(hb_grade, leucos_grade, lymphos_grade, neutros_grade, thrombos_grade)
            navigiere_bereich_berichte()

            #Weiter in Nachsorgeformular:
            if not find_and_click_button('button_psa_feld.png', base_path=local_screenshots_dir): print('button_psa_feld.png not found. Bitte manuell übernehmen.'); sys.exit()

            ctrl_tabs(8); pyautogui.press('enter') #Pain 0
            for _ in range(8):
                pyautogui.press('down'); ctrl_tabs(6); pyautogui.press('enter'); time.sleep(0.05) #Restliche 0 bis inkl periph. neuropathy
            
            pyautogui.press('down'); ctrl_tabs(6) #Anemia Zeile
           


            print("Starte Eintragen der CTCAE Hämatogramm Veränderungen...")

            if isinstance(hb_grade, int):
                print(f"hb_grade = integer erkannt. Führe tabs aus: {hb_grade}, danach Enter")
                ctrl_tabs((hb_grade))
                pyautogui.press('enter')
                time.sleep(0.2)
            elif not isinstance(hb_grade, int):
                print(f"ACHTUNG!!! hb_grade =/= integer erkannt. Es konnte kein Laborwert für Hb ausgelesen werden!! Ggf. in letzten 6 Monaten kein vollständiges Hämatogramm erfolgt?")
                print("Überspringe Ankreuzen des CTCAE-Grades, gehe zu nächstem.")

            pyautogui.press('down'); ctrl_tabs(6) #WBC Zeile
            if isinstance(leucos_grade, int):
                print(f"leucos_grade = integer erkannt. Führe tabs aus: {leucos_grade}, danach Enter")
                ctrl_tabs((leucos_grade))
                pyautogui.press('enter')
                time.sleep(0.2)
            elif not isinstance(leucos_grade, int):
                print(f"ACHTUNG!!! leucos_grade =/= integer erkannt. Es konnte kein Laborwert für Hb ausgelesen werden!! Ggf. in letzten 6 Monaten kein vollständiges Hämatogramm erfolgt?")
                print("Überspringe Ankreuzen des CTCAE-Grades, gehe zu nächstem.")

            pyautogui.press('down'); ctrl_tabs(6) #Lymphos Zeile
            if isinstance(lymphos_grade, int):
                print(f"lymphos_grade = integer erkannt. Führe tabs aus: {lymphos_grade}, danach Enter")
                ctrl_tabs((lymphos_grade))
                pyautogui.press('enter')
                time.sleep(0.2)
            elif not isinstance(lymphos_grade, int):
                print(f"ACHTUNG!!! lymphos_grade =/= integer erkannt. Es konnte kein Laborwert für Hb ausgelesen werden!! Ggf. in letzten 6 Monaten kein vollständiges Hämatogramm erfolgt?")
                print("Überspringe Ankreuzen des CTCAE-Grades, gehe zu nächstem.")

            pyautogui.press('down'); ctrl_tabs(6) #Neutros Zeile
            if isinstance(neutros_grade, int):
                print(f"neutros_grade = integer erkannt. Führe tabs aus: {neutros_grade}, danach Enter")
                ctrl_tabs((neutros_grade))
                pyautogui.press('enter')
                time.sleep(0.2)
            elif not isinstance(neutros_grade, int):
                print(f"ACHTUNG!!! neutros_grade =/= integer erkannt. Es konnte kein Laborwert für Hb ausgelesen werden!! Ggf. in letzten 6 Monaten kein vollständiges Hämatogramm erfolgt?")
                print("Überspringe Ankreuzen des CTCAE-Grades, gehe zu nächstem.")

            pyautogui.press('down'); ctrl_tabs(6) #Thrombos Zeile
            if isinstance(thrombos_grade, int):
                print(f"thrombos_grade = integer erkannt. Führe tabs aus: {thrombos_grade}, danach Enter")
                ctrl_tabs((thrombos_grade))
                pyautogui.press('enter')
                time.sleep(0.2)
            elif not isinstance(thrombos_grade, int):
                print(f"ACHTUNG!!! thrombos_grade =/= integer erkannt. Es konnte kein Laborwert für Hb ausgelesen werden!! Ggf. in letzten 6 Monaten kein vollständiges Hämatogramm erfolgt?")
                print("Überspringe Ankreuzen des CTCAE-Grades, gehe zu nächstem.")


            #GENERAL BLOCK bearbeitet, jetzt check auf spez. UAW BLOCK
            if symptom_button_image:
                mapping_number_tox = {"button_symptomblock_brain.png": 8,
                                    "button_symptomblock_orl.png": 12,
                                    "button_symptomblock_abdomen.png": 9,
                                    "button_symptomblock_thorax.png": 8,
                                    "button_symptomblock_pelvismale.png": 10,
                                    "button_symptomblock_pelvisfemale.png": 12,
                                    "button_symptomblock_bone_extremities.png": 7, 
                                    "button_symptomblock_breast.png": 6}
            
            #je nach mapping: number of tx
            number_tox = mapping_number_tox.get(symptom_button_image, 6) if symptom_button_image else 6
            print(f"\n\n\n führe {number_tox} loops aus, um die spezifischen Toxizitäten für {symptom_button_image} zu erfassen.")
            for _ in range(number_tox):
                pyautogui.press('down')
                ctrl_tabs(6) #Navigation auf nächste 0
                pyautogui.press('enter') #Auswahl 0
                time.sleep(0.05)    


            pyautogui.press('down'); ctrl_tabs(5); pyautogui.press('enter') #leitlinien-gerechte Nachsorge ja




        # Block für OHNE Chemo
        else:
            print("chemotherapie-Variable = nein oder None, lege UAW ohne Systemtherapie an...")
            pyautogui.press('down'); pyautogui.press('enter') #Auswahl WITHOUT syst therapy
            print("INFO: Auswahl 'WITHOUT syst therapy' getroffen (Chemo=False)")
              
            #Warten, bis alle Nebenwirkungen geladen            
            while True:
                if find_button(image_name='button_symptomauswahl_offen.png', base_path=local_screenshots_dir, max_attempts=1):
                    print("Gruppe auswählen noch offen, Navigation pausiert.")
                    time.sleep(0.05)
                else:
                    print("Gruppe auswählen nicht mehr offen, fahre fort.")
                    break

            # === NEUER CODEBLOCK SPEZIFISCHE TOX GRUPPE ===
            symptom_button_image = _get_symptomblock_image_from_icd(icd_code, geschlecht)
            if symptom_button_image:
            
                print(f"INFO: Passender Symptomblock für ICD '{icd_code}' gefunden: {symptom_button_image}")
                print("INFO: Versuche, den zusätzlichen Symptomblock anzuklicken...")
                for attempt in range(30):
                    if not find_and_click_button("button_symptomblock_auswahl.png", base_path=local_screenshots_dir, max_attempts=1):
                        print("WARNUNG: Konnte den Button 'button_symptomblock_auswahl.png' nicht finden. Probiere button_symptomblock_auswahl_rot.png ...")
                        if not find_and_click_button("button_symptomblock_auswahl_rot.png", base_path=local_screenshots_dir, max_attempts=1):
                            print("WARNUNG: Konnte den Button 'button_symptomblock_auswahl_rot.png' nicht finden. Loop erneut (max 50)...")
                            time.sleep(0.05)
                        else:
                            print("INFO: Button 'button_symptomblock_auswahl_rot.png' gefunden und angeklickt.")
                            break
                    else:
                        print("INFO: Button 'button_symptomblock_auswahl.png' gefunden und angeklickt.")
                        break

                if not find_and_click_button(symptom_button_image, "Spezifischer Symptomblock", base_path=local_screenshots_dir, max_attempts=20, interval=0.05):
                    print(f"WARNUNG: Konnte den spezifischen Symptomblock-Button '{symptom_button_image}' nicht klicken.")
                    return False
                #Warten, bis alle Nebenwirkungen geladen            
                while True:
                    if find_button(image_name='button_symptomauswahl_offen.png', base_path=local_screenshots_dir, max_attempts=1):
                        print("Gruppe auswählen noch offen, Navigation pausiert.")
                        time.sleep(0.05)
                    else:
                        print("Gruppe auswählen nicht mehr offen, fahre fort.")
                        break
            else:
                print(f"INFO: Kein spezifischer Symptomblock für ICD-Code '{icd_code}' im Mapping gefunden. Lege nur General Symptomblock an.")
                
            # === NEUER CODEBLOCK ENDE ===

            if not find_and_click_button('button_psa_feld.png', base_path=local_screenshots_dir): print('button_psa_feld.png not found. Bitte manuell übernehmen.'); sys.exit() 

            #Nebenwirkungen ausfüllen
            ctrl_tabs(8); pyautogui.press('enter') #Pain 0
            for _ in range(8):
                pyautogui.press('down'); ctrl_tabs(6); pyautogui.press('enter'); time.sleep(0.05) #Restliche 0


            #GENERAL BLOCK bearbeitet, jetzt check auf spez. UAW BLOCK
            if symptom_button_image:
                mapping_number_tox = {"button_symptomblock_brain.png": 8,
                                    "button_symptomblock_orl.png": 12,
                                    "button_symptomblock_abdomen.png": 9,
                                    "button_symptomblock_thorax.png": 8,
                                    "button_symptomblock_pelvismale.png": 10,
                                    "button_symptomblock_pelvisfemale.png": 12,
                                    "button_symptomblock_bone_extremities.png": 7, 
                                    "button_symptomblock_breast.png": 6}
            
            #je nach mapping: number of tx
            number_tox = mapping_number_tox.get(symptom_button_image, 6) if symptom_button_image else 6
            print(f"\n\n\n führe {number_tox} loops aus, um die spezifischen Toxizitäten für {symptom_button_image} zu erfassen.")
            for _ in range(number_tox):
                pyautogui.press('down')
                ctrl_tabs(6) #Navigation auf nächste 0
                pyautogui.press('enter') #Auswahl 0
                time.sleep(0.05)   

            ctrl_tabs(13); pyautogui.press('enter') #leitlinien-gerechte Nachsorge ja

        if not find_and_click_button('button_speichern.png', base_path=local_screenshots_dir): print('button_speichern.png not found. Bitte manuell übernehmen.'); sys.exit() 
        return True


    # --- Typ Palliativ ---
    elif nachsorgeformular_typ == 'palliativ':
            if not find_and_click_button('button_nachsorge_palliativ.png', base_path=local_screenshots_dir): print('button_nachsorge_palliativ.png nicht gefunden'); return False 
            if not find_button('button_nachsorge_palliativ_confirm.png', base_path=local_screenshots_dir, max_attempts=100): print('button_nachsorge_palliativ_confirm.png nicht gefunden'); return False 
            time.sleep(0.3)
            if not find_and_click_button('button_nachsorge_palliativ_confirm.png', base_path=local_screenshots_dir, max_attempts=100): print('button_nachsorge_palliativ_confirm.png nicht gefunden'); return False

            #AUswahl Patient lebt
            ctrl_tabs(5)
            pyautogui.press('enter')

            #AUswahl Nachsorgeart
            ctrl_tabs(6)
            pyautogui.press('enter')
            if bericht_typ == 'k':
                  pyautogui.press('down'); pyautogui.press('enter')
            elif bericht_typ == 't':
                  pyautogui.press('down'); pyautogui.press('down'); pyautogui.press('enter')
            else:
                  print('bericht_typ weder k noch t, überspringe Feld')
                  pyautogui.press('enter')

            #Tox>Grad 3 Nein auswählen.
            ctrl_tabs(8)
            pyautogui.press('enter')

            #Nebenwirkungen eintragen
            ctrl_tabs(2)
            pyautogui.press('enter')





             # Block für MIT Chemo
            if chemotherapie == 'ja':
                pyautogui.press('enter') #Auswahl WITH syst therapy
                print("INFO: Auswahl 'WITH syst therapy' getroffen (Chemo=True)")

                #Warten, bis alle Nebenwirkungen geladen            
                while True:
                    if find_button(image_name='button_symptomauswahl_offen.png', base_path=local_screenshots_dir, max_attempts=1):
                        print("Gruppe auswählen noch offen, Navigation pausiert.")
                        time.sleep(0.05)
                    else:
                        print("Gruppe auswählen nicht mehr offen, fahre fort.")
                        break

                # === NEUER CODEBLOCK SPEZIFISCHE TOX GRUPPE ===
                symptom_button_image = _get_symptomblock_image_from_icd(icd_code, geschlecht)
                if symptom_button_image:
                
                    print(f"INFO: Passender Symptomblock für ICD '{icd_code}' gefunden: {symptom_button_image}")
                    print("INFO: Versuche, den zusätzlichen Symptomblock anzuklicken...")
                    for attempt in range(30):
                        if not find_and_click_button("button_symptomblock_auswahl.png", base_path=local_screenshots_dir, max_attempts=1):
                            print("WARNUNG: Konnte den Button 'button_symptomblock_auswahl.png' nicht finden. Probiere button_symptomblock_auswahl_rot.png ...")
                            if not find_and_click_button("button_symptomblock_auswahl_rot.png", base_path=local_screenshots_dir, max_attempts=1):
                                print("WARNUNG: Konnte den Button 'button_symptomblock_auswahl_rot.png' nicht finden. Loop erneut (max 50)...")
                                time.sleep(0.05)
                            else:
                                print("INFO: Button 'button_symptomblock_auswahl_rot.png' gefunden und angeklickt.")
                                break
                        else:
                            print("INFO: Button 'button_symptomblock_auswahl.png' gefunden und angeklickt.")
                            break

                    if not find_and_click_button(symptom_button_image, "Spezifischer Symptomblock", base_path=local_screenshots_dir, max_attempts=20, interval=0.05):
                        print(f"WARNUNG: Konnte den spezifischen Symptomblock-Button '{symptom_button_image}' nicht klicken.")
                        return False
                    #Warten, bis alle Nebenwirkungen geladen            
                    while True:
                        if find_button(image_name='button_symptomauswahl_offen.png', base_path=local_screenshots_dir, max_attempts=1):
                            print("Gruppe auswählen noch offen, Navigation pausiert.")
                            time.sleep(0.05)
                        else:
                            print("Gruppe auswählen nicht mehr offen, fahre fort.")
                            break
                else:
                    print(f"INFO: Kein spezifischer Symptomblock für ICD-Code '{icd_code}' im Mapping gefunden. Lege nur General Symptomblock an.")
                    
                # === NEUER CODEBLOCK ENDE ===

                #Holen der CTCAE Grade
                import ctcaeauslesen
                hb_grade, leucos_grade, lymphos_grade, neutros_grade, thrombos_grade  = ctcaeauslesen.main()
                print(hb_grade, leucos_grade, lymphos_grade, neutros_grade, thrombos_grade)
                navigiere_bereich_berichte()

                #Weiter in Nachsorgeformular:

                if not find_and_click_button('button_ecog_feld.png', base_path=local_screenshots_dir): print('button_ecog_feld.png not found. Bitte manuell übernehmen.'); sys.exit()

                ctrl_tabs(8); pyautogui.press('enter') #Pain 0
                for _ in range(8):
                    pyautogui.press('down'); ctrl_tabs(6); pyautogui.press('enter'); time.sleep(0.05) #Restliche 0 bis inkl periph. neuropathy
                
                pyautogui.press('down'); ctrl_tabs(6) #Anemia Zeile
                
                print("Starte Eintragen der CTCAE Hämatogramm Veränderungen...")

                if isinstance(hb_grade, int):
                    print(f"hb_grade = integer erkannt. Führe tabs aus: {hb_grade}, danach Enter")
                    ctrl_tabs((hb_grade))
                    pyautogui.press('enter')
                    time.sleep(0.2)
                elif not isinstance(hb_grade, int):
                    print(f"ACHTUNG!!! hb_grade =/= integer erkannt. Es konnte kein Laborwert für Hb ausgelesen werden!! Ggf. in letzten 6 Monaten kein vollständiges Hämatogramm erfolgt?")
                    print("Überspringe Ankreuzen des CTCAE-Grades, gehe zu nächstem.")

                pyautogui.press('down'); ctrl_tabs(6) #WBC Zeile
                if isinstance(leucos_grade, int):
                    print(f"leucos_grade = integer erkannt. Führe tabs aus: {leucos_grade}, danach Enter")
                    ctrl_tabs((leucos_grade))
                    pyautogui.press('enter')
                    time.sleep(0.2)
                elif not isinstance(leucos_grade, int):
                    print(f"ACHTUNG!!! leucos_grade =/= integer erkannt. Es konnte kein Laborwert für Hb ausgelesen werden!! Ggf. in letzten 6 Monaten kein vollständiges Hämatogramm erfolgt?")
                    print("Überspringe Ankreuzen des CTCAE-Grades, gehe zu nächstem.")

                pyautogui.press('down'); ctrl_tabs(6) #Lymphos Zeile
                if isinstance(lymphos_grade, int):
                    print(f"lymphos_grade = integer erkannt. Führe tabs aus: {lymphos_grade}, danach Enter")
                    ctrl_tabs((lymphos_grade))
                    pyautogui.press('enter')
                    time.sleep(0.2)
                elif not isinstance(lymphos_grade, int):
                    print(f"ACHTUNG!!! lymphos_grade =/= integer erkannt. Es konnte kein Laborwert für Hb ausgelesen werden!! Ggf. in letzten 6 Monaten kein vollständiges Hämatogramm erfolgt?")
                    print("Überspringe Ankreuzen des CTCAE-Grades, gehe zu nächstem.")

                pyautogui.press('down'); ctrl_tabs(6) #Neutros Zeile
                if isinstance(neutros_grade, int):
                    print(f"neutros_grade = integer erkannt. Führe tabs aus: {neutros_grade}, danach Enter")
                    ctrl_tabs((neutros_grade))
                    pyautogui.press('enter')
                    time.sleep(0.2)
                elif not isinstance(neutros_grade, int):
                    print(f"ACHTUNG!!! neutros_grade =/= integer erkannt. Es konnte kein Laborwert für Hb ausgelesen werden!! Ggf. in letzten 6 Monaten kein vollständiges Hämatogramm erfolgt?")
                    print("Überspringe Ankreuzen des CTCAE-Grades, gehe zu nächstem.")

                pyautogui.press('down'); ctrl_tabs(6) #Thrombos Zeile
                if isinstance(thrombos_grade, int):
                    print(f"thrombos_grade = integer erkannt. Führe tabs aus: {thrombos_grade}, danach Enter")
                    ctrl_tabs((thrombos_grade))
                    pyautogui.press('enter')
                    time.sleep(0.2)
                elif not isinstance(thrombos_grade, int):
                    print(f"ACHTUNG!!! thrombos_grade =/= integer erkannt. Es konnte kein Laborwert für Hb ausgelesen werden!! Ggf. in letzten 6 Monaten kein vollständiges Hämatogramm erfolgt?")
                    print("Überspringe Ankreuzen des CTCAE-Grades, gehe zu nächstem.")


                #GENERAL BLOCK bearbeitet, jetzt check auf spez. UAW BLOCK
                if symptom_button_image:
                    mapping_number_tox = {"button_symptomblock_brain.png": 8,
                                        "button_symptomblock_orl.png": 12,
                                        "button_symptomblock_abdomen.png": 9,
                                        "button_symptomblock_thorax.png": 8,
                                        "button_symptomblock_pelvismale.png": 10,
                                        "button_symptomblock_pelvisfemale.png": 12,
                                        "button_symptomblock_bone_extremities.png": 7, 
                                        "button_symptomblock_breast.png": 6}
                
                #je nach mapping: number of tx
                number_tox = mapping_number_tox.get(symptom_button_image, 6) if symptom_button_image else 6
                print(f"\n\n\n führe {number_tox} loops aus, um die spezifischen Toxizitäten für {symptom_button_image} zu erfassen.")
                for _ in range(number_tox):
                    pyautogui.press('down')
                    ctrl_tabs(6) #Navigation auf nächste 0
                    pyautogui.press('enter') #Auswahl 0
                    time.sleep(0.05)    


                pyautogui.press('down'); ctrl_tabs(5); pyautogui.press('enter') #leitlinien-gerechte Nachsorge ja

            # Block für OHNE Chemo
            else:
                print("chemotherapie-Variable = nein oder Nein, lege UAW ohne Systemtherapie an...")
                pyautogui.press('down'); pyautogui.press('enter') #Auswahl WITHOUT syst therapy
                print("INFO: Auswahl 'WITHOUT syst therapy' getroffen (Chemo=False)")
                
                #Warten, bis alle Nebenwirkungen geladen            
                while True:
                    if find_button(image_name='button_symptomauswahl_offen.png', base_path=local_screenshots_dir, max_attempts=1):
                        print("Gruppe auswählen noch offen, Navigation pausiert.")
                        time.sleep(0.05)
                    else:
                        print("Gruppe auswählen nicht mehr offen, fahre fort.")
                        break


                # === NEUER CODEBLOCK SPEZIFISCHE TOX GRUPPE ===
                symptom_button_image = _get_symptomblock_image_from_icd(icd_code, geschlecht)
                if symptom_button_image:
                
                    print(f"INFO: Passender Symptomblock für ICD '{icd_code}' gefunden: {symptom_button_image}")
                    print("INFO: Versuche, den zusätzlichen Symptomblock anzuklicken...")
                    for attempt in range(30):
                        if not find_and_click_button("button_symptomblock_auswahl.png", base_path=local_screenshots_dir, max_attempts=1):
                            print("WARNUNG: Konnte den Button 'button_symptomblock_auswahl.png' nicht finden. Probiere button_symptomblock_auswahl_rot.png ...")
                            if not find_and_click_button("button_symptomblock_auswahl_rot.png", base_path=local_screenshots_dir, max_attempts=1):
                                print("WARNUNG: Konnte den Button 'button_symptomblock_auswahl_rot.png' nicht finden. Loop erneut (max 50)...")
                                time.sleep(0.05)
                            else:
                                print("INFO: Button 'button_symptomblock_auswahl_rot.png' gefunden und angeklickt.")
                                break
                        else:
                            print("INFO: Button 'button_symptomblock_auswahl.png' gefunden und angeklickt.")
                            break

                    if not find_and_click_button(symptom_button_image, "Spezifischer Symptomblock", base_path=local_screenshots_dir, max_attempts=20, interval=0.05):
                        print(f"WARNUNG: Konnte den spezifischen Symptomblock-Button '{symptom_button_image}' nicht klicken.")
                        return False
                    #Warten, bis alle Nebenwirkungen geladen            
                    while True:
                        if find_button(image_name='button_symptomauswahl_offen.png', base_path=local_screenshots_dir, max_attempts=1):
                            print("Gruppe auswählen noch offen, Navigation pausiert.")
                            time.sleep(0.05)
                        else:
                            print("Gruppe auswählen nicht mehr offen, fahre fort.")
                            break
                else:
                    print(f"INFO: Kein spezifischer Symptomblock für ICD-Code '{icd_code}' im Mapping gefunden. Lege nur General Symptomblock an.")
                    
                # === NEUER CODEBLOCK ENDE ===



                if not find_and_click_button('button_ecog_feld.png', base_path=local_screenshots_dir): print('button_ecog_feld.png not found. Bitte manuell übernehmen.'); sys.exit() 

                #Nebenwirkungen ausfüllen
                ctrl_tabs(8); pyautogui.press('enter') #Pain 0
                for _ in range(8):
                    pyautogui.press('down'); ctrl_tabs(6); pyautogui.press('enter'); time.sleep(0.05) #Restliche 0

                #GENERAL BLOCK bearbeitet, jetzt check auf spez. UAW BLOCK
                if symptom_button_image:
                    mapping_number_tox = {"button_symptomblock_brain.png": 8,
                                        "button_symptomblock_orl.png": 12,
                                        "button_symptomblock_abdomen.png": 9,
                                        "button_symptomblock_thorax.png": 8,
                                        "button_symptomblock_pelvismale.png": 10,
                                        "button_symptomblock_pelvisfemale.png": 12,
                                        "button_symptomblock_bone_extremities.png": 7, 
                                        "button_symptomblock_breast.png": 6}
                
                #je nach mapping: number of tx
                number_tox = mapping_number_tox.get(symptom_button_image, 6) if symptom_button_image else 6
                print(f"\n\n\n führe {number_tox} loops aus, um die spezifischen Toxizitäten für {symptom_button_image} zu erfassen.")
                for _ in range(number_tox):
                    pyautogui.press('down')
                    ctrl_tabs(6) #Navigation auf nächste 0
                    pyautogui.press('enter') #Auswahl 0
                    time.sleep(0.05)    


                ctrl_tabs(13); pyautogui.press('enter') #leitlinien-gerechte Nachsorge ja


            if not find_and_click_button('button_speichern_nachsorge.png', base_path=local_screenshots_dir, max_attempts=80): print('button_speichern.png not found. Bitte manuell übernehmen.'); sys.exit() # Added base_path
            return True

    # --- Ungültiger Typ ---
    else:
            # Escaped single quotes within the f-string as requested
            print(f'Variable nachsorgeformular_typ ist {nachsorgeformular_typ} und somit weder \'kurativ\' noch \'palliativ\'. Entsprechend konnte kein Nachsorgeformular angelegt werden. Bitte manuell tätigen.')
            return False


###################################
###################################

def diagnose_uebernehmen():
    print("diagnose_uebernehmen()")
    local_screenshots_dir = os.path.join(screenshots_dir, 'UNIVERSAL', 'bereich_berichte')
    print("probiere find_button() mit button_diagnose_confirm.png")
    if not find_button('button_diagnose_confirm.png', base_path=local_screenshots_dir, max_attempts=50, interval=0.1): print("Diagnosenfenster nicht geöffnet, bitte manuell übernehmen."); return False
    else:
        print("Diagnosenfenster geöffnet.")
        if not find_and_click_button("button_uebernehmen_diagnose.png", base_path=local_screenshots_dir, max_attempts=3, interval=0.05): 
            print("button_uebernehmen_diagnose nach 3 Versuchen nicht gefunden, schliesse Fenster...")
            pyautogui.hotkey('alt', 'f4')
            if not find_and_click_button("button_diag_schliessen_ja.png", base_path=local_screenshots_dir): print("Button button_diag_schliessen_ja.png nicht gefunden. Diag-Fenster manuell schliessen."); return False
            time.sleep(0.2)
        else:
            return True


###################################
###################################

def prozent_zoom_100():
    print("Starte prozent_zoom_100() aus UNIVERSAL")
    local_screenshots_dir = os.path.join(screenshots_dir, 'UNIVERSAL', 'bereich_berichte')
    print("probiere find_button() mit button_prozent_confirm.png")


    if not find_button('button_leiste_kurz.png', base_path=local_screenshots_dir, max_attempts=200, interval=0.1, confidence=0.95):
        print("button_leiste_kurz nicht gefunden.")
        return False
    time.sleep(0.3)
    if not find_button('button_prozent_confirm.png', base_path=local_screenshots_dir, max_attempts=20, interval=0.1):
        print("button_prozent_confirm nicht gefunden.")
        return False
    print("button_prozent_confirm gefunden, versuche button_100_prozent.png")
    time.sleep(0.2)
    if not find_button('button_100_prozent.png', base_path=local_screenshots_dir, max_attempts=5, interval=0.1, confidence=0.95):
        print("button_100_prozent nicht gefunden. Stelle Zoom manuell auf 100%.")
        time.sleep(0.2)
        if not find_and_click_button_offset(image_name='button_prozent_confirm.png', base_path=local_screenshots_dir, x_offset=-10): print("button_prozent_confirm nicht gefunden."); return False
        if not find_and_click_button_offset(image_name='button_100_prozent_auswahl.png', base_path=local_screenshots_dir, x_offset=-10): print("button_100_prozent_auswahl nicht gefunden."); return False
        return True
    else:
        print("100% Zoom bereits ausgewählt.")
        return True

###################################
###################################
def gem_fl_dg(za):
    try:
        with open(os.path.join(user_home, 'kp', 'k1.txt'), 'r') as f:
            k1 = f.read().strip()
        with open(os.path.join(user_home, 'kp', 'k2.txt'), 'r') as f:
            k2 = f.read().strip()
        with open(os.path.join(user_home, 'kp', 'p_dg.txt'), 'r') as f:
            p_dg = f.read().strip()
        from google import genai
    except Exception as e:
        print(f"Fehler beim Lesen der Dateien aus dem kp Ordner: {e}")
        return False
    k = str(k1) + str(k2)
    
    p_dg = p_dg + str(za)
    c = genai.Client(api_key=f"{k}")
    print("Starte req...")
    response = c.models.generate_content(
        model="gemini-2.5-flash-preview-05-20", contents=f"{p_dg}"
    )
    return response.text

###################################
###################################

def gem_fl_an(za):
    try:
        with open(os.path.join(user_home, 'kp', 'k1.txt'), 'r') as f:
            k1 = f.read().strip()
        with open(os.path.join(user_home, 'kp', 'k2.txt'), 'r') as f:
            k2 = f.read().strip()
        with open(os.path.join(user_home, 'kp', 'p_an.txt'), 'r') as f:
            p_an = f.read().strip()
        from google import genai
    except Exception as e:
        print(f"Fehler beim Lesen der Dateien aus dem kp Ordner: {e}")
        return False
    k = str(k1) + str(k2)
    
    p_an = p_an + str(za)
    c = genai.Client(api_key=f"{k}")
    print("Starte req...")
    response = c.models.generate_content(
        model="gemini-2.5-flash-preview-05-20", contents=f"{p_an}"
    )
    return response.text