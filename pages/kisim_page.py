from PyQt6.QtWidgets import QWidget, QGridLayout, QLabel, QVBoxLayout, QPushButton, QHBoxLayout, QDialog, QLineEdit, QMessageBox, QFormLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QIcon
from components.widgets import SmallTile
import os
import sys # For platform detection
import re # Import regex for key generation
import unicodedata # For handling umlauts
import subprocess # For opening folder
import logging # Import logging module
from scripts.UNIVERSAL import get_benutzerdaten, save_benutzerdaten # Added QDialog, QLineEdit, QMessageBox, QFormLayout

# --- Script Definitions (Order determines tile display) ---
script_definitions = [
    ("Create PatData JSON", "patdata.py"),
    ("View JSON", "viewjson.py"),
    ("Bericht Radioonkologie", "berrao.py"),
    ("Station: Eintrittsbericht", "eintritt.py"),
    ("Station: Austrittsbericht", "austritt.py"),
    ("PallCare Kons", "konspall.py"),
    ("Wochenendübergabe", "wochenende.py"),
    ("Stationsliste ergänzen", "liste.py"),
    ("Standardlabor", "lab.py"),
    ("Rehaantrag", "reha.py"),
    ("Spitex", "spitex.py"),
    ("Sozialberatung (stat)", "sb.py"),
    ("Physio (stat)", "physio.py"),
    ("Planungs-CT/MRI", "planungsbildgebung.py"),
    ("Ergo (stat)", "ergo.py"),
    ("Database Manager", "database_manager.py"),
    # Add new scripts here with ("Tile Name", "filename.py")
]
# ---------------------------------------------------------

# Helper function to generate script keys from tile names
# This needs to match the logic used when creating the script_map keys
def generate_script_key(tile_name):
    # Lowercase
    key = tile_name.lower()
    # Normalize umlauts and special characters (like removing accents)
    key = unicodedata.normalize('NFKD', key).encode('ascii', 'ignore').decode('ascii')
    # Remove content in brackets (like [WIP], (stat), (Zervix))
    key = re.sub(r'\s*\[.*?\]', '', key).strip()
    key = re.sub(r'\s*\(.*?\)', '', key).strip()
    # Replace spaces and invalid characters with underscores
    key = re.sub(r'[^a-z0-9_]+(?<!^)', '_', key)
    # Remove leading/trailing underscores
    key = key.strip('_')
    return key

class KisimPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        logging.info("Initializing KisimPage...")
        self.main_window = main_window
        self.setup_ui()
        logging.info("KisimPage UI setup complete.")
        
    def setup_ui(self):
        # Main vertical layout
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(10, 0, 40, 40)
        self.setLayout(main_layout)
        
        # Define the path to the scripts directory relative to this file
        scripts_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), os.pardir, "scripts"))
        
        # Header with title and open folder button
        header_layout = QHBoxLayout()
        
        # Page title
        title_label = QLabel("KISIM Scripts")
        title_label.setFont(QFont("Helvetica", 24, QFont.Weight.Bold))
        title_label.setStyleSheet("color: white; margin-bottom: 20px;")
        header_layout.addWidget(title_label)
        
        # Add spacer to push button to the right
        header_layout.addStretch()
    
        
        # Add header to main layout
        main_layout.addLayout(header_layout)

        # Grid layout for script tiles
        grid_layout = QGridLayout()
        grid_layout.setSpacing(15)  # Smaller spacing for smaller tiles
        
        # Create script tiles based on script_definitions order
        num_definitions = len(script_definitions)
        max_tiles = 20 # Target total tiles including placeholders

        for i in range(max_tiles):
            row = i // 5
            col = i % 5

            tile_name = "Placeholder"
            filename = None
            script_exists = False

            if i < num_definitions:
                # Get data from the definitions list
                tile_name, filename = script_definitions[i]
                if filename:
                    full_script_path = os.path.join(scripts_dir, filename)
                    script_exists = os.path.exists(full_script_path)
                    if not script_exists:
                        # Optional: Generate key only for the warning message
                        script_key_for_warning = generate_script_key(tile_name)
                        logging.warning(f"Script file not found for tile '{tile_name}' (key: '{script_key_for_warning}') at '{full_script_path}'")
                        print(f"Warning: Script file not found for tile '{tile_name}' (key: '{script_key_for_warning}') at '{full_script_path}'")
                else:
                     # Optional: Generate key only for the warning message
                    script_key_for_warning = generate_script_key(tile_name)
                    logging.warning(f"Filename missing in script_definitions for tile '{tile_name}' (key: '{script_key_for_warning}')")
                    print(f"Warning: Filename missing in script_definitions for tile '{tile_name}' (key: '{script_key_for_warning}')")

            # Pass info to SmallTile
            tile = SmallTile(tile_name, filename=filename, script_exists=script_exists)
            # Connect signal using the tile_name from the definition (or "Placeholder")
            tile.clicked.connect(lambda checked, name=tile_name: self.open_script(name))
            grid_layout.addWidget(tile, row, col)
            
        # Add grid layout to main layout
        main_layout.addLayout(grid_layout)
        main_layout.addStretch()
            

    def open_script(self, script_name):
        # Define placeholder names
        placeholder_names = ["Placeholder"]
        
        # Don't process placeholder tiles
        if script_name in placeholder_names:
            print(f"Placeholder tile clicked: {script_name}")
            logging.debug(f"Placeholder tile '{script_name}' clicked, ignoring.")
            return

        # --- Generate the script key from the tile name ---
        script_key = generate_script_key(script_name)

        # --- NEU: Check for user data BEFORE proceeding ---
        print("Checking user data before running script...")
        logging.info(f"Checking user data for script key: {script_key}")
        # --- Aufruf ohne UNIVERSAL-Präfix ---
        benutzer_vorname, benutzer_nachname = get_benutzerdaten()

        if benutzer_vorname is None or benutzer_nachname is None:
            logging.warning(f"User data (Vorname/Nachname) not found or incomplete. Prompting user for input before running '{script_key}'.")
            print(f"Benutzerdaten fehlen für Skript '{script_key}'. Bitte eingeben.")
            self.prompt_benutzerdaten(script_key) # Show prompt, it will handle navigation if successful
            return # Stop further execution here, prompt handles the next step
        else:
            logging.info(f"User data found ({benutzer_vorname} {benutzer_nachname}). Proceeding to run script '{script_key}'.")
            print(f"Benutzerdaten gefunden ({benutzer_vorname} {benutzer_nachname}). Starte Skript '{script_key}'...")
            # --- Call the main window method to switch page and run script ---
            if self.main_window and hasattr(self.main_window, 'open_cmd_scripts_page'):
                self.main_window.open_cmd_scripts_page(script_key)
            else:
                logging.error(f"Cannot access main_window.open_cmd_scripts_page for key '{script_key}'")
                print(f"Error: Cannot access main_window.open_cmd_scripts_page for key '{script_key}'")
        # --- ENDE NEU ---

    # --- NEUE METHODE: Prompt für Benutzerdaten ---
    def prompt_benutzerdaten(self, script_key_to_run_after):
        dialog = QDialog(self.main_window) # Parent auf main_window setzen
        dialog.setWindowTitle("Erfassung Benutzerdaten") # Fenster Titel beibehalten
        dialog.setModal(True) # Blockiert andere Fenster
        dialog.setFixedSize(635, 330)

        layout = QVBoxLayout(dialog)

        # --- NEU: Info-Label hinzufügen ---
        info_text = ("Benutzerdaten sind in der App noch nicht hinterlegt, jedoch relevant zum Eintragen des signierenden/visierenden Benutzers in Briefe und Berichte im KISIM. "
                     "Bitte jetzt erfassen und auf Rechtschreibung achten!")
        info_label = QLabel(info_text)
        info_label.setWordWrap(True) # Automatischer Zeilenumbruch
        info_label.setStyleSheet("color: white; margin-bottom: 15px;") # Weißer Text, Abstand nach unten
        layout.addWidget(info_label)
        # --- ENDE NEU ---

        form_layout = QFormLayout()
        # Setze Abstand zwischen Label und Feld im Formular
        form_layout.setHorizontalSpacing(20)
        form_layout.setVerticalSpacing(10)

        vorname_edit = QLineEdit(dialog)
        nachname_edit = QLineEdit(dialog)

        # --- NEU: Styling für Eingabefelder ---
        input_style = "background-color: black; color: white; border: 1px solid #555; padding: 5px; border-radius: 3px;"
        vorname_edit.setStyleSheet(input_style)
        nachname_edit.setStyleSheet(input_style)
        # --- ENDE NEU ---

        # Verwende QLabel für Formular, um Styling zu ermöglichen
        vorname_label = QLabel("Vorname:")
        nachname_label = QLabel("Nachname:")
        label_style = "color: white;" # Styling für die Labels
        vorname_label.setStyleSheet(label_style)
        nachname_label.setStyleSheet(label_style)

        form_layout.addRow(vorname_label, vorname_edit)
        form_layout.addRow(nachname_label, nachname_edit)

        layout.addLayout(form_layout)

        # Buttons
        button_box = QHBoxLayout()
        # --- NEU: Button-Text geändert ---
        save_button = QPushButton("Erfassen und Speichern", dialog)
        # --- ENDE NEU ---
        cancel_button = QPushButton("Abbrechen", dialog)

        # --- NEU: Styling für Buttons ---
        button_style = ("QPushButton { background-color: black; color: white; border: 1px solid #555; "
                        "padding: 8px 15px; border-radius: 4px; }"
                        "QPushButton:hover { background-color: #333; }"
                        "QPushButton:pressed { background-color: #111; }")
        save_button.setStyleSheet(button_style)
        cancel_button.setStyleSheet(button_style)
        save_button.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_button.setCursor(Qt.CursorShape.PointingHandCursor)
        # --- ENDE NEU ---

        button_box.addStretch()
        # --- NEU: Geänderte Reihenfolge der Buttons ---
        button_box.addWidget(save_button) # Speichern zuerst hinzufügen
        button_box.addWidget(cancel_button) # Dann Abbrechen
        # --- ENDE NEU ---
        layout.addLayout(button_box)

        def on_save():
            vorname = vorname_edit.text().strip()
            nachname = nachname_edit.text().strip()

            if not vorname or not nachname:
                # Verwende QMessageBox mit Parent, damit es zum Dialog gehört
                msg_box = QMessageBox(QMessageBox.Icon.Warning, "Eingabe fehlt",
                                        "Bitte geben Sie sowohl Vorname als auch Nachname ein.",
                                        QMessageBox.StandardButton.Ok, dialog)
                msg_box.setStyleSheet("QMessageBox { background-color: #333; color: white; } "
                                        "QPushButton { background-color: black; color: white; padding: 5px 10px; border: 1px solid #555; border-radius: 3px; min-width: 60px; } "
                                        "QPushButton:hover { background-color: #444; }")
                msg_box.exec()
                return

            print(f"Versuche Benutzerdaten zu speichern: Vorname='{vorname}', Nachname='{nachname}'")
            success = save_benutzerdaten(nachname, vorname)

            if success:
                logging.info(f"User data saved successfully. Proceeding to run script '{script_key_to_run_after}'.")
                print("Benutzerdaten erfolgreich gespeichert.")
                dialog.accept() # Schliesst den Dialog

                # --- WICHTIG: Jetzt die ursprüngliche Aktion auslösen ---
                if self.main_window and hasattr(self.main_window, 'open_cmd_scripts_page'):
                    print(f"Löse Navigation zur CmdScriptsPage für Skript '{script_key_to_run_after}' aus...")
                    self.main_window.open_cmd_scripts_page(script_key_to_run_after)
                else:
                    # Sollte nicht passieren, aber zur Sicherheit
                    err_msg = f"FEHLER: Konnte nach Speichern der Benutzerdaten nicht zur CmdScriptsPage navigieren (main_window oder Methode fehlt)."
                    print(err_msg)
                    logging.error(err_msg)
                    # Zeige Fehler im Hauptfenster an, da Dialog geschlossen wird
                    QMessageBox.critical(self.main_window, "Fehler", err_msg)
            else:
                err_msg = "Fehler beim Speichern der Benutzerdaten. Überprüfen Sie die Berechtigungen für das 'patdata'-Verzeichnis."
                print(f"FEHLER: {err_msg}")
                logging.error(f"Failed to save user data. Script key '{script_key_to_run_after}' will not run.")
                # Zeige Fehler im Dialog an
                msg_box = QMessageBox(QMessageBox.Icon.Critical, "Speicherfehler", err_msg,
                                        QMessageBox.StandardButton.Ok, dialog)
                msg_box.setStyleSheet("QMessageBox { background-color: #333; color: white; } "
                                        "QPushButton { background-color: black; color: white; padding: 5px 10px; border: 1px solid #555; border-radius: 3px; min-width: 60px; } "
                                        "QPushButton:hover { background-color: #444; }")
                msg_box.exec()
                # Dialog bleibt offen für Korrektur oder Abbruch

        save_button.clicked.connect(on_save)
        cancel_button.clicked.connect(dialog.reject) # Schliesst den Dialog ohne Aktion

        dialog.setLayout(layout)
        dialog.exec() # Zeigt den Dialog modal an und wartet 