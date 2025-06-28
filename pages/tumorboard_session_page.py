from PyQt6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, 
                             QScrollArea, QFrame, QComboBox, QTextEdit, QMessageBox, QDialog, QDialogButtonBox, QLineEdit, QFormLayout, QCheckBox)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QWheelEvent
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineSettings
from PyQt6.QtCore import QUrl
import os
import logging
from pathlib import Path
import pandas as pd
from datetime import datetime
from utils.excel_export_utils import export_tumorboard_to_collection
import json
import os

class NoScrollComboBox(QComboBox):
    """Custom QComboBox that ignores wheel events when not focused"""
    def wheelEvent(self, event: QWheelEvent):
        # Only allow wheel events if the combo box has focus AND is open
        if self.hasFocus() and self.isEnabled():
            # Only process wheel event if dropdown is actually open
            if hasattr(self, 'view') and self.view().isVisible():
                super().wheelEvent(event)
            else:
                event.ignore()
        else:
            # Ignore the wheel event completely
            event.ignore()
            
    def focusInEvent(self, event):
        # When gaining focus, don't automatically show popup
        super().focusInEvent(event)
        
    def mousePressEvent(self, event):
        # Only respond to explicit mouse clicks
        super().mousePressEvent(event)

class PatientNotRecordedDialog(QDialog):
    """Dialog to handle incomplete patient data"""
    def __init__(self, missing_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Patient nicht erfasst")
        self.setModal(True)
        self.setFixedSize(400, 200)
        
        layout = QVBoxLayout()
        
        # Header
        header_label = QLabel("Patient nicht erfasst")
        header_label.setFont(QFont("Helvetica", 16, QFont.Weight.Bold))
        header_label.setStyleSheet("color: #ff6b6b; margin-bottom: 10px;")
        layout.addWidget(header_label)
        
        # Message with proper grammar
        if len(missing_data) == 1:
            message = f"Daten \"{missing_data[0]}\" ist im aktuellen Fall nicht erfasst.\nSoll der Patient als \"Nicht besprochen\" markiert werden?"
        else:
            missing_text = "\" und \"".join(missing_data)
            message = f"Daten \"{missing_text}\" sind im aktuellen Fall nicht erfasst.\nSoll der Patient als \"Nicht besprochen\" markiert werden?"
        
        message_label = QLabel(message)
        message_label.setWordWrap(True)
        message_label.setStyleSheet("color: white; margin-bottom: 20px;")
        layout.addWidget(message_label)
        
        # Buttons
        button_box = QDialogButtonBox()
        yes_button = QPushButton("Ja")
        no_button = QPushButton("Nein, weiter bearbeiten")
        
        button_box.addButton(yes_button, QDialogButtonBox.ButtonRole.YesRole)
        button_box.addButton(no_button, QDialogButtonBox.ButtonRole.NoRole)
        
        yes_button.clicked.connect(self.accept)
        no_button.clicked.connect(self.reject)
        
        layout.addWidget(button_box)
        self.setLayout(layout)
        
        # Apply dark theme
        self.setStyleSheet("""
            QDialog {
                background-color: #1a2633;
                color: white;
            }
            QPushButton {
                background-color: #114473;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1a5a9e;
            }
        """)

class LastPatientCompletedDialog(QDialog):
    """Dialog to show completion message for last patient"""
    def __init__(self, unprocessed_count, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Letzter Patient bearbeitet")
        self.setModal(True)
        self.setFixedSize(500, 200)
        
        layout = QVBoxLayout()
        
        # Header
        header_label = QLabel("Letzter Patient bearbeitet")
        header_label.setFont(QFont("Helvetica", 16, QFont.Weight.Bold))
        header_label.setStyleSheet("color: #4FC3F7; margin-bottom: 15px;")
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header_label)
        
        # Message based on unprocessed count
        if unprocessed_count == 0:
            message = "Letzter Patient wurde erfolgreich erfasst und gespeichert.\nSie können das Tumor Board jetzt abschließen."
        else:
            message = f"Letzter Patient wurde erfolgreich gespeichert.\nAuf der Liste bestehen noch {unprocessed_count} Patienten, die vor Abschluss des Tumor Boards noch bearbeitet werden müssen."
        
        message_label = QLabel(message)
        message_label.setWordWrap(True)
        message_label.setStyleSheet("color: white; font-size: 14px; margin-bottom: 20px;")
        message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(message_label)
        
        # OK Button
        ok_button = QPushButton("OK")
        ok_button.setFixedHeight(40)
        ok_button.setStyleSheet("""
            QPushButton {
                background-color: #1E90FF;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #4169E1;
            }
            QPushButton:pressed {
                background-color: #0000CD;
            }
        """)
        ok_button.clicked.connect(self.accept)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(ok_button)
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # Apply dark theme
        self.setStyleSheet("""
            QDialog {
                background-color: #1a2633;
                color: white;
            }
        """)

class AnwesenderArztDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Anwesender Arzt definieren")
        self.setFixedSize(400, 180)
        self.setModal(True)
        
        # Store the entered data
        self.nachname = ""
        
        self.setup_dialog()
    
    def setup_dialog(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title label
        title_label = QLabel("Bitte definieren Sie den beim Tumorboard anwesenden Arzt:")
        title_label.setFont(QFont("Helvetica", 12, QFont.Weight.Bold))
        title_label.setStyleSheet("color: white; margin-bottom: 10px;")
        title_label.setWordWrap(True)
        layout.addWidget(title_label)
        
        # Form fields
        form_layout = QVBoxLayout()
        form_layout.setSpacing(10)
        
        # Nachname
        nachname_label = QLabel("Nachname Kaderarzt:")
        nachname_label.setFont(QFont("Helvetica", 10))
        nachname_label.setStyleSheet("color: white;")
        form_layout.addWidget(nachname_label)
        
        self.nachname_input = QLineEdit()
        self.nachname_input.setFont(QFont("Helvetica", 11))
        self.nachname_input.setStyleSheet("""
            QLineEdit {
                background-color: #2A3642;
                color: white;
                border: 2px solid #425061;
                border-radius: 4px;
                padding: 8px;
                font-size: 11px;
            }
            QLineEdit:focus {
                border-color: #3292ea;
            }
        """)
        form_layout.addWidget(self.nachname_input)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        self.ok_button = QPushButton("OK")
        self.ok_button.setFont(QFont("Helvetica", 10, QFont.Weight.Bold))
        self.ok_button.setFixedHeight(35)
        self.ok_button.setStyleSheet("""
            QPushButton {
                background-color: #2E8B57;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3CB371;
            }
            QPushButton:pressed {
                background-color: #228B22;
            }
            QPushButton:disabled {
                background-color: #666666;
                color: #999999;
            }
        """)
        self.ok_button.setEnabled(False)  # Initially disabled
        self.ok_button.clicked.connect(self.on_ok)
        
        self.cancel_button = QPushButton("Abbrechen")
        self.cancel_button.setFont(QFont("Helvetica", 10, QFont.Weight.Bold))
        self.cancel_button.setFixedHeight(35)
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #666666;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #777777;
            }
            QPushButton:pressed {
                background-color: #555555;
            }
        """)
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        
        # Connect text change events to validate inputs
        self.nachname_input.textChanged.connect(self.validate_inputs)
        
        # Set dialog style
        self.setStyleSheet("""
            QDialog {
                background-color: #19232D;
                color: white;
            }
        """)
        
        # Focus on input
        self.nachname_input.setFocus()
    
    def validate_inputs(self):
        """Enable OK button only when nachname field has text"""
        nachname_valid = bool(self.nachname_input.text().strip())
        self.ok_button.setEnabled(nachname_valid)
    
    def on_ok(self):
        """Handle OK button click"""
        self.nachname = self.nachname_input.text().strip()
        
        if self.nachname:
            self.accept()
    
    def get_arzt_data(self):
        """Get the entered physician data"""
        return self.nachname

class BenutzerdatenDialog(QDialog):
    """Dialog for user data input"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Erfassung Benutzerdaten")
        self.setModal(True)
        self.setFixedSize(635, 330)
        
        layout = QVBoxLayout()
        
        # Info text
        info_text = ("Benutzerdaten sind in der App noch nicht hinterlegt, jedoch relevant zum Eintragen des signierenden/visierenden Benutzers in Berichte und Berichte im KISIM. "
                     "Bitte jetzt erfassen und auf Rechtschreibung achten!")
        info_label = QLabel(info_text)
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: white; margin-bottom: 15px;")
        layout.addWidget(info_label)
        
        # Form layout
        form_layout = QFormLayout()
        form_layout.setHorizontalSpacing(20)
        form_layout.setVerticalSpacing(10)
        
        self.vorname_edit = QLineEdit()
        self.nachname_edit = QLineEdit()
        
        # Styling for input fields
        input_style = "background-color: black; color: white; border: 1px solid #555; padding: 5px; border-radius: 3px;"
        self.vorname_edit.setStyleSheet(input_style)
        self.nachname_edit.setStyleSheet(input_style)
        
        # Labels
        label_style = "color: white; font-weight: bold;"
        optional_style = "color: #cccccc; font-size: 12px; margin-top: 2px;"
        
        name_label = QLabel("Name:")
        birth_date_label = QLabel("Geburtsdatum:")
        birth_date_optional = QLabel("(optional)")
        birth_date_optional.setStyleSheet(optional_style)
        
        patient_number_label = QLabel("Patientennummer:")
        patient_number_optional = QLabel("(optional)")
        patient_number_optional.setStyleSheet(optional_style)
        
        diagnosis_label = QLabel("Diagnose:")
        diagnosis_optional = QLabel("(optional)")
        diagnosis_optional.setStyleSheet(optional_style)
        
        icd_code_label = QLabel("ICD-Code:")
        icd_code_optional = QLabel("(optional)")
        icd_code_optional.setStyleSheet(optional_style)
        
        name_label.setStyleSheet(label_style)
        birth_date_label.setStyleSheet(label_style)
        patient_number_label.setStyleSheet(label_style)
        diagnosis_label.setStyleSheet(label_style)
        icd_code_label.setStyleSheet(label_style)
        
        # Create containers for labels with optional text
        patient_number_container = QWidget()
        patient_number_layout = QVBoxLayout(patient_number_container)
        patient_number_layout.setContentsMargins(0, 0, 0, 0)
        patient_number_layout.setSpacing(0)
        patient_number_layout.addWidget(patient_number_label)
        patient_number_layout.addWidget(patient_number_optional)
        
        diagnosis_container = QWidget()
        diagnosis_layout = QVBoxLayout(diagnosis_container)
        diagnosis_layout.setContentsMargins(0, 0, 0, 0)
        diagnosis_layout.setSpacing(0)
        diagnosis_layout.addWidget(diagnosis_label)
        diagnosis_layout.addWidget(diagnosis_optional)
        
        icd_code_container = QWidget()
        icd_code_layout = QVBoxLayout(icd_code_container)
        icd_code_layout.setContentsMargins(0, 0, 0, 0)
        icd_code_layout.setSpacing(0)
        icd_code_layout.addWidget(icd_code_label)
        icd_code_layout.addWidget(icd_code_optional)
        
        form_layout.addRow(name_label, self.name_edit)
        form_layout.addRow(birth_date_label, self.birth_date_edit)
        form_layout.addRow(patient_number_container, self.patient_number_edit)
        form_layout.addRow(diagnosis_container, self.diagnosis_edit)
        form_layout.addRow(icd_code_container, self.icd_code_edit)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QVBoxLayout()
        
        self.save_button = QPushButton("Speichern")
        self.cancel_button = QPushButton("Abbrechen")
        
        button_style = """
            QPushButton {
                background-color: black;
                color: white;
                padding: 5px 10px;
                border: 1px solid #555;
                border-radius: 3px;
                min-width: 60px;
            }
            QPushButton:hover {
                background-color: #444;
            }
        """
        self.save_button.setStyleSheet(button_style)
        self.cancel_button.setStyleSheet(button_style)
        
        self.save_button.clicked.connect(self.on_save)
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
        # Apply dark theme
        self.setStyleSheet("""
            QDialog {
                background-color: #333;
                color: white;
            }
        """)
    
    def on_save(self):
        vorname = self.vorname_edit.text().strip()
        nachname = self.nachname_edit.text().strip()
        
        if not vorname or not nachname:
            msg_box = QMessageBox(QMessageBox.Icon.Warning, "Eingabe fehlt",
                                  "Bitte geben Sie sowohl Vorname als auch Nachname ein.",
                                  QMessageBox.StandardButton.Ok, self)
            msg_box.setStyleSheet("""
                QMessageBox { 
                    background-color: #333; 
                    color: white; 
                } 
                QPushButton { 
                    background-color: black; 
                    color: white; 
                    padding: 5px 10px; 
                    border: 1px solid #555; 
                    border-radius: 3px; 
                    min-width: 60px; 
                } 
                QPushButton:hover { 
                    background-color: #444; 
                }
            """)
            msg_box.exec()
            return
        
        success = TumorboardSessionPage.save_benutzerdaten(nachname, vorname)
        if success:
            logging.info("User data saved successfully")
            self.accept()
        else:
            err_msg = "Fehler beim Speichern der Benutzerdaten. Überprüfen Sie die Berechtigungen für das 'patdata'-Verzeichnis."
            msg_box = QMessageBox(QMessageBox.Icon.Critical, "Speicherfehler", err_msg,
                                  QMessageBox.StandardButton.Ok, self)
            msg_box.setStyleSheet("""
                QMessageBox { 
                    background-color: #333; 
                    color: white; 
                } 
                QPushButton { 
                    background-color: black; 
                    color: white; 
                    padding: 5px 10px; 
                    border: 1px solid #555; 
                    border-radius: 3px; 
                    min-width: 60px; 
                } 
                QPushButton:hover { 
                    background-color: #444; 
                }
            """)
            msg_box.exec()

class AddPatientDialog(QDialog):
    """Dialog for adding a new patient manually"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Neuen Patienten anlegen")
        self.setModal(True)
        self.setFixedSize(500, 450)
        
        layout = QVBoxLayout()
        
        # Header
        header_label = QLabel("Neuen Patienten hinzufügen")
        header_label.setFont(QFont("Helvetica", 16, QFont.Weight.Bold))
        header_label.setStyleSheet("color: #4FC3F7; margin-bottom: 15px;")
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header_label)
        
        # Form layout
        form_layout = QFormLayout()
        form_layout.setHorizontalSpacing(20)
        form_layout.setVerticalSpacing(10)
        
        # Input fields
        self.name_edit = QLineEdit()
        self.birth_date_edit = QLineEdit()
        self.birth_date_edit.setPlaceholderText("DD.MM.YYYY")
        self.patient_number_edit = QLineEdit()
        self.diagnosis_edit = QTextEdit()
        self.diagnosis_edit.setFixedHeight(60)
        self.icd_code_edit = QLineEdit()
        
        # Styling for input fields
        input_style = """
            background-color: #114473; 
            color: white; 
            border: 1px solid #2a3642; 
            border-radius: 4px; 
            padding: 6px; 
            font-size: 14px;
        """
        text_style = """
            QTextEdit {
                background-color: #114473; 
                color: white; 
                border: 1px solid #2a3642; 
                border-radius: 4px; 
                padding: 6px; 
                font-size: 14px;
            }
        """
        
        self.name_edit.setStyleSheet(input_style)
        self.birth_date_edit.setStyleSheet(input_style)
        self.patient_number_edit.setStyleSheet(input_style)
        self.diagnosis_edit.setStyleSheet(text_style)
        self.icd_code_edit.setStyleSheet(input_style)
        
        # Labels
        label_style = "color: white; font-weight: bold;"
        optional_style = "color: #cccccc; font-size: 12px; margin-top: 2px;"
        
        name_label = QLabel("Name:")
        birth_date_label = QLabel("Geburtsdatum:")
        birth_date_optional = QLabel("(optional)")
        birth_date_optional.setStyleSheet(optional_style)
        
        patient_number_label = QLabel("Patientennummer:")
        patient_number_optional = QLabel("(optional)")
        patient_number_optional.setStyleSheet(optional_style)
        
        diagnosis_label = QLabel("Diagnose:")
        diagnosis_optional = QLabel("(optional)")
        diagnosis_optional.setStyleSheet(optional_style)
        
        icd_code_label = QLabel("ICD-Code:")
        icd_code_optional = QLabel("(optional)")
        icd_code_optional.setStyleSheet(optional_style)
        
        name_label.setStyleSheet(label_style)
        birth_date_label.setStyleSheet(label_style)
        patient_number_label.setStyleSheet(label_style)
        diagnosis_label.setStyleSheet(label_style)
        icd_code_label.setStyleSheet(label_style)
        
        # Create containers for labels with optional text
        patient_number_container = QWidget()
        patient_number_layout = QVBoxLayout(patient_number_container)
        patient_number_layout.setContentsMargins(0, 0, 0, 0)
        patient_number_layout.setSpacing(0)
        patient_number_layout.addWidget(patient_number_label)
        patient_number_layout.addWidget(patient_number_optional)
        
        diagnosis_container = QWidget()
        diagnosis_layout = QVBoxLayout(diagnosis_container)
        diagnosis_layout.setContentsMargins(0, 0, 0, 0)
        diagnosis_layout.setSpacing(0)
        diagnosis_layout.addWidget(diagnosis_label)
        diagnosis_layout.addWidget(diagnosis_optional)
        
        icd_code_container = QWidget()
        icd_code_layout = QVBoxLayout(icd_code_container)
        icd_code_layout.setContentsMargins(0, 0, 0, 0)
        icd_code_layout.setSpacing(0)
        icd_code_layout.addWidget(icd_code_label)
        icd_code_layout.addWidget(icd_code_optional)
        
        form_layout.addRow(name_label, self.name_edit)
        form_layout.addRow(birth_date_label, self.birth_date_edit)
        form_layout.addRow(patient_number_container, self.patient_number_edit)
        form_layout.addRow(diagnosis_container, self.diagnosis_edit)
        form_layout.addRow(icd_code_container, self.icd_code_edit)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        self.add_button = QPushButton("Hinzufügen")
        self.cancel_button = QPushButton("Abbrechen")
        
        button_style = """
            QPushButton {
                background-color: #2E8B57;
                color: white;
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #3CB371;
            }
        """
        cancel_style = """
            QPushButton {
                background-color: #666;
                color: white;
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #777;
            }
        """
        
        self.add_button.setStyleSheet(button_style)
        self.cancel_button.setStyleSheet(cancel_style)
        
        self.add_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
        
        # Set "Hinzufügen" as default button (activated by Enter key)
        self.add_button.setDefault(True)
        
        button_layout.addStretch()
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
        # Apply dark theme
        self.setStyleSheet("""
            QDialog {
                background-color: #1a2633;
                color: white;
            }
        """)
    
    def get_patient_data(self):
        """Get the entered patient data"""
        return {
            'name': self.name_edit.text().strip(),
            'birth_date': self.birth_date_edit.text().strip(),
            'patient_number': self.patient_number_edit.text().strip(),
            'diagnosis': self.diagnosis_edit.toPlainText().strip(),
            'icd_code': self.icd_code_edit.text().strip()
        }

class TumorboardSessionPage(QWidget):
    def __init__(self, main_window, tumorboard_name, date_str, tumorboard_base_path=None):
        super().__init__()
        logging.info(f"Initializing TumorboardSessionPage for: {tumorboard_name} on {date_str}")
        self.main_window = main_window
        self.tumorboard_name = tumorboard_name
        self.date_str = date_str
        
        # Store the tumorboard base path for consistent file operations
        self.tumorboard_base_path = tumorboard_base_path or (Path.home() / "tumorboards")
        self.is_using_fallback_path = (self.tumorboard_base_path == Path.home() / "tumorboards")
        
        # Store identifier for find_page_index
        self.entity_name = f"{tumorboard_name}_{date_str}_session"
        
        # Patient data
        self.patients_data = []
        self.current_patient_index = 0
        self.patient_states = {}  # Track patient completion states
        
        # Temporary file management
        self.temp_excel_path = None
        self.source_excel_path = self.tumorboard_base_path / self.tumorboard_name / self.date_str / f"{self.date_str}.xlsx"
        self.has_unsaved_changes = False
        
        self.setup_ui()
        
        # Check for existing temporary session and create/restore temp file
        # This must happen AFTER UI setup so dialogs can be shown properly
        # Note: This only runs on initial creation, not when returning to existing page
        self.handle_temp_session_restoration()
        
        self.load_patient_data()
        logging.info(f"TumorboardSessionPage UI setup complete for {tumorboard_name} on {date_str}.")

    def check_and_handle_session_restoration(self):
        """Check for session restoration when returning to an existing session page"""
        logging.info("Checking for session restoration on existing session page")
        
        # Create temporary file name
        temp_filename = f"{self.date_str}_temp_session.xlsx"
        temp_excel_path = self.source_excel_path.parent / temp_filename
        
        # Check if temporary file exists
        if temp_excel_path.exists():
            # Get modification time of temp file
            import os
            import datetime
            mod_time = os.path.getmtime(temp_excel_path)
            mod_datetime = datetime.datetime.fromtimestamp(mod_time)
            formatted_time = mod_datetime.strftime("%d.%m.%Y %H:%M")
            
            # Show restoration dialog
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Session gefunden")
            msg_box.setText(f"Es wurde eine bereits begonnene Session gefunden vom {formatted_time}.\n\n"
                           f"Möchten Sie, dass diese Session fortgesetzt wird?")
            
            continue_button = msg_box.addButton("Ja, fortsetzen", QMessageBox.ButtonRole.YesRole)
            new_session_button = msg_box.addButton("Nein, neue Session starten", QMessageBox.ButtonRole.NoRole)
            msg_box.setDefaultButton(continue_button)
            
            msg_box.setStyleSheet("""
                QMessageBox {
                    background-color: #1a2633;
                    color: white;
                }
                QMessageBox QLabel {
                    color: white;
                    font-size: 14px;
                }
                QPushButton {
                    background-color: #114473;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 8px 16px;
                    font-weight: bold;
                    min-width: 120px;
                }
                QPushButton:hover {
                    background-color: #1a5a9e;
                }
            """)
            
            msg_box.exec()
            clicked_button = msg_box.clickedButton()
            
            if clicked_button == continue_button:
                # Continue with existing temp file
                self.temp_excel_path = temp_excel_path
                logging.info(f"Continuing existing session from: {self.temp_excel_path}")
                self.has_unsaved_changes = True  # Mark as having changes since it's a restored session
                
                # Reload patient data from existing temp file
                self.clear_and_reload_patient_data()
            else:
                # Delete old temp file and create new one
                try:
                    temp_excel_path.unlink()
                    logging.info(f"Deleted old temporary file: {temp_excel_path}")
                except Exception as e:
                    logging.error(f"Error deleting old temporary file: {e}")
                
                # Create new temp file from source
                self.temp_excel_path = temp_excel_path
                self.create_temp_excel_file()
                self.has_unsaved_changes = False
                
                # Clear memory and reload fresh data from new temp file
                self.clear_and_reload_patient_data()
        else:
            # No temp file exists, ensure we're using source file
            self.temp_excel_path = None
            logging.info("No temporary session file found, using source file")

    def clear_and_reload_patient_data(self):
        """Clear all patient data from memory and reload from Excel file"""
        logging.info("Clearing patient data from memory and reloading from Excel")
        
        # Reset current patient index
        self.current_patient_index = 0
        
        # Clear the patient list UI
        for i in reversed(range(self.patient_list_layout.count())):
            child = self.patient_list_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
        
        # Clear patient info display
        self.clear_patient_display()
        
        # Reload patient data from Excel file (this will clear patients_data and patient_states internally)
        self.load_patient_data()
        
        logging.info(f"Patient data cleared and reloaded. Now have {len(self.patients_data)} patients")

    def handle_temp_session_restoration(self):
        """Handle temporary session restoration or creation"""
        # Create temporary file name
        temp_filename = f"{self.date_str}_temp_session.xlsx"
        self.temp_excel_path = self.source_excel_path.parent / temp_filename
        
        # Check if temporary file already exists
        if self.temp_excel_path.exists():
            # Get modification time of temp file
            import os
            import datetime
            mod_time = os.path.getmtime(self.temp_excel_path)
            mod_datetime = datetime.datetime.fromtimestamp(mod_time)
            formatted_time = mod_datetime.strftime("%d.%m.%Y %H:%M")
            
            # Show restoration dialog
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Session gefunden")
            msg_box.setText(f"Es wurde eine bereits begonnene Session gefunden vom {formatted_time}.\n\n"
                           f"Möchten Sie, dass diese Session fortgesetzt wird?")
            
            continue_button = msg_box.addButton("Ja, fortsetzen", QMessageBox.ButtonRole.YesRole)
            new_session_button = msg_box.addButton("Nein, neue Session starten", QMessageBox.ButtonRole.NoRole)
            msg_box.setDefaultButton(continue_button)
            
            msg_box.setStyleSheet("""
                QMessageBox {
                    background-color: #1a2633;
                    color: white;
                }
                QMessageBox QLabel {
                    color: white;
                    font-size: 14px;
                }
                QPushButton {
                    background-color: #114473;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 8px 16px;
                    font-weight: bold;
                    min-width: 120px;
                }
                QPushButton:hover {
                    background-color: #1a5a9e;
                }
            """)
            
            msg_box.exec()
            clicked_button = msg_box.clickedButton()
            
            if clicked_button == continue_button:
                # Continue with existing temp file
                logging.info(f"Continuing existing session from: {self.temp_excel_path}")
                self.has_unsaved_changes = True  # Mark as having changes since it's a restored session
            else:
                # Delete old temp file and create new one
                try:
                    self.temp_excel_path.unlink()
                    logging.info(f"Deleted old temporary file: {self.temp_excel_path}")
                except Exception as e:
                    logging.error(f"Error deleting old temporary file: {e}")
                
                # Create new temp file
                self.create_temp_excel_file()
        else:
            # No existing temp file, create new one
            self.create_temp_excel_file()

    def create_temp_excel_file(self):
        """Create a temporary copy of the Excel file for this session"""
        try:
            if not self.source_excel_path.exists():
                logging.error(f"Source Excel file not found: {self.source_excel_path}")
                return False
            
            # Delete existing temp file if it exists
            if self.temp_excel_path and self.temp_excel_path.exists():
                try:
                    self.temp_excel_path.unlink()
                    logging.info(f"Deleted existing temporary file: {self.temp_excel_path}")
                except Exception as e:
                    logging.warning(f"Could not delete existing temp file: {e}")
            
            # Copy source file to temporary file
            import shutil
            shutil.copy2(self.source_excel_path, self.temp_excel_path)
            
            logging.info(f"Created fresh temporary Excel file: {self.temp_excel_path}")
            return True
            
        except Exception as e:
            logging.error(f"Error creating temporary Excel file: {e}")
            return False

    def copy_temp_to_source(self):
        """Copy temporary Excel file to source file"""
        try:
            if self.temp_excel_path and self.temp_excel_path.exists():
                import shutil
                import time
                
                # Check if source file is accessible (not locked by another process)
                try:
                    # Try to open the source file briefly to check if it's locked
                    with open(self.source_excel_path, 'r+b') as f:
                        pass
                except PermissionError as pe:
                    raise Exception(f"Quelldatei ist gesperrt oder wird von einem anderen Programm verwendet: {self.source_excel_path}. Fehler: {pe}")
                except FileNotFoundError:
                    # File doesn't exist yet, that's okay
                    pass
                
                # Attempt the copy with retry logic
                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        shutil.copy2(self.temp_excel_path, self.source_excel_path)
                        logging.info(f"Copied temporary file to source: {self.source_excel_path}")
                        return True
                    except PermissionError as pe:
                        if attempt < max_retries - 1:
                            logging.warning(f"Copy attempt {attempt + 1} failed with permission error, retrying in 1 second...")
                            time.sleep(1)
                            continue
                        else:
                            raise Exception(f"Berechtigung verweigert beim Kopieren nach {max_retries} Versuchen. Quelldatei: {self.temp_excel_path}, Zieldatei: {self.source_excel_path}. Fehler: {pe}")
                    except Exception as e:
                        raise Exception(f"Unerwarteter Fehler beim Kopieren. Quelldatei: {self.temp_excel_path}, Zieldatei: {self.source_excel_path}. Fehler: {e}")
            else:
                raise Exception(f"Temporäre Datei nicht gefunden oder nicht zugänglich: {self.temp_excel_path}")
                
        except Exception as e:
            logging.error(f"Error copying temporary file to source: {e}")
            # Re-raise with the detailed error message
            raise e

    def cleanup_temp_file(self):
        """Clean up the temporary Excel file"""
        try:
            if self.temp_excel_path and self.temp_excel_path.exists():
                self.temp_excel_path.unlink()
                logging.info(f"Cleaned up temporary Excel file: {self.temp_excel_path}")
        except Exception as e:
            logging.error(f"Error cleaning up temporary file: {e}")

    def check_unsaved_changes(self):
        """Check if there are unsaved changes and show warning dialog"""
        if not self.has_unsaved_changes:
            return True  # No changes, safe to navigate
        
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Ungespeicherte Änderungen")
        msg_box.setText("Möchten Sie wirklich die Bearbeitung des Tumorboards abbrechen?\n\n"
                        "Sämtliche erfolgten Änderungen werden nicht gespeichert.\n\n"
                        "Um Änderungen zu speichern, muss die Session mittels "
                        "\"Tumorboard abschließen\" bestätigt werden.")
        msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg_box.setDefaultButton(QMessageBox.StandardButton.No)
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: #1a2633;
                color: white;
            }
            QMessageBox QLabel {
                color: white;
                font-size: 14px;
            }
            QPushButton {
                background-color: #114473;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #1a5a9e;
            }
        """)
        
        result = msg_box.exec()
        
        if result == QMessageBox.StandardButton.Yes:
            # User confirmed to discard changes
            # NOTE: We do NOT delete the temp file here anymore!
            # It will only be deleted when "Tumorboard abschließen" is confirmed
            self.has_unsaved_changes = False
            logging.info("User chose to discard changes and navigate away. Temp file preserved for potential session restoration.")
            return True
        else:
            # User wants to keep editing
            return False

    def calculate_age(self, birth_date_str):
        """Calculate age from birth date string"""
        try:
            # Try different date formats
            for fmt in ("%d.%m.%Y", "%d/%m/%Y", "%Y-%m-%d"):
                try:
                    birth_date = datetime.strptime(str(birth_date_str), fmt)
                    today = datetime.today()
                    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
                    return f"{age} Jahre"
                except ValueError:
                    continue
            return "-"
        except:
            return "-"

    def get_label_style(self, is_filled=False):
        """Get style for labels based on fill status - BACKGROUND COLOR changes"""
        bg_color = "#2E8B57" if is_filled else "#8B0000"  # Green if filled, dark red if not
        return f"""
            color: white; 
            background-color: {bg_color}; 
            font-weight: bold; 
            font-size: 14px; 
            padding: 5px 6px; 
            border-radius: 4px;
        """

    def get_input_style(self):
        """Get standard style for input elements"""
        return """
            QComboBox {
                background-color: #114473;
                color: white;
                border: 1px solid #2a3642;
                border-radius: 4px;
                padding: 5px 6px;
                font-size: 14px;
            }
            QComboBox:hover {
                background-color: #1a5a9e;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: #114473;
                color: white;
                selection-background-color: #1a5a9e;
            }
        """
    
    def get_textinput_style(self):
        """Get standard style for text input elements"""
        return """
            QTextEdit {
                background-color: #114473;
                color: white;
                border: 10x solid #2a3642;
                border-radius: 0px;
                padding: 0px 4px;
                font-size: 14px;
            }
        """

    def setup_ui(self):
        # Main layout - horizontal with three sections
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(10, 0, 10, 10)
        main_layout.setSpacing(15)
        self.setLayout(main_layout)

        # Left column: Patient list (narrow)
        self.create_patient_list_column(main_layout)
        
        # Middle column: PDF viewer (largest)
        self.create_pdf_viewer_column(main_layout)
        
        # Right column: Data entry
        self.create_data_entry_column(main_layout)

    def create_patient_list_column(self, main_layout):
        """Create the left patient list column"""
        patient_frame = QFrame()
        patient_frame.setFixedWidth(213)  # Made narrower for more PDF space
        patient_frame.setStyleSheet("""
            QFrame {
                background-color: #1a2633;
                border: none;
                border-radius: 8px;
            }
        """)
        
        patient_layout = QVBoxLayout(patient_frame)
        patient_layout.setContentsMargins(10, 15, 10, 15)
        patient_layout.setSpacing(16)
        
        # Header (no border)
        header_label = QLabel("Patienten")
        header_label.setFont(QFont("Helvetica", 14, QFont.Weight.Bold))
        header_label.setStyleSheet("color: #4FC3F7; margin-bottom: 10px; border: none;")
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        patient_layout.addWidget(header_label)
        
        # Add new patient button
        self.add_patient_button = QPushButton("Neuen Patienten\nanlegen")
        self.add_patient_button.setFixedHeight(50)
        self.add_patient_button.setFixedWidth(180)
        self.add_patient_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.add_patient_button.setStyleSheet("""
            QPushButton {
                background-color: #2E8B57;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                font-size: 12px;
                text-align: center;
                padding: 5px;
                margin-bottom: 10px;
            }
            QPushButton:hover {
                background-color: #3CB371;
            }
            QPushButton:pressed {
                background-color: #228B22;
            }
        """)
        self.add_patient_button.clicked.connect(self.add_new_patient)
        patient_layout.addWidget(self.add_patient_button)
        
        # Delete current patient button
        self.delete_patient_button = QPushButton("Markierten Patienten\nlöschen")
        self.delete_patient_button.setFixedHeight(50)
        self.delete_patient_button.setFixedWidth(180)
        self.delete_patient_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.delete_patient_button.setStyleSheet("""
            QPushButton {
                background-color: #880000;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                font-size: 12px;
                text-align: center;
                padding: 5px;
                margin-bottom: 10px;
            }
            QPushButton:hover {
                background-color: #FF6347;
            }
            QPushButton:pressed {
                background-color: #B22222;
            }
            QPushButton:disabled {
                background-color: #666666;
                color: #999999;
            }
        """)
        self.delete_patient_button.clicked.connect(self.delete_current_patient)
        patient_layout.addWidget(self.delete_patient_button)
        
        # Scrollable patient list
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                width: 12px;
            }
        """)
        
        self.patient_list_widget = QWidget()
        self.patient_list_layout = QVBoxLayout(self.patient_list_widget)
        self.patient_list_layout.setContentsMargins(5, 5, 5, 5)
        self.patient_list_layout.setSpacing(5)  # Fixed spacing between patient buttons
        
        scroll_area.setWidget(self.patient_list_widget)
        patient_layout.addWidget(scroll_area)
        
        main_layout.addWidget(patient_frame)

    def create_pdf_viewer_column(self, main_layout):
        """Create the middle PDF viewer column"""
        pdf_frame = QFrame()
        pdf_frame.setStyleSheet("""
            QFrame {
                background-color: #1a2633;
                border: 1px solid #2a3642;
                border-radius: 8px;
            }
        """)
        
        pdf_layout = QVBoxLayout(pdf_frame)
        pdf_layout.setContentsMargins(10, 15, 10, 15)
        pdf_layout.setSpacing(5)
        
        # Header - smaller and without border/outline
        self.pdf_header_label = QLabel("Tumor Board - Anmeldung: Patientenname")
        self.pdf_header_label.setFont(QFont("Helvetica", 14, QFont.Weight.Bold))
        self.pdf_header_label.setStyleSheet("color: #4FC3F7; border: none; outline: none; margin-bottom: 5px;")
        self.pdf_header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pdf_header_label.setFixedHeight(43)  # Fixed height to align with other headers
        pdf_layout.addWidget(self.pdf_header_label)
        
        # PDF viewer
        try:
            self.pdf_viewer = QWebEngineView()
            self.pdf_viewer.settings().setAttribute(QWebEngineSettings.WebAttribute.PluginsEnabled, True)
            self.pdf_viewer.settings().setAttribute(QWebEngineSettings.WebAttribute.PdfViewerEnabled, True)
            pdf_layout.addWidget(self.pdf_viewer)
        except Exception as e:
            logging.error(f"Error creating PDF viewer: {e}")
            error_label = QLabel(f"PDF Viewer Error: {e}")
            error_label.setStyleSheet("color: red; font-size: 14px;")
            error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            error_label.setWordWrap(True)
            pdf_layout.addWidget(error_label)
        
        main_layout.addWidget(pdf_frame, stretch=2)  # Give PDF viewer more space

    def create_data_entry_column(self, main_layout):
        """Create the right data entry column"""
        data_frame = QFrame()
        data_frame.setFixedWidth(350)
        data_frame.setStyleSheet("""
            QFrame {
                background-color: #1a2633;
                border: 1px solid #2a3642;
                border-radius: 8px;
            }
        """)
        
        # Use normal layout but with fixed positioning for data entry
        data_layout = QVBoxLayout(data_frame)
        data_layout.setContentsMargins(10, 23, 10, 10) 
        data_layout.setSpacing(15)  # No automatic spacing
        
        # Header
        header_label = QLabel("Patientendaten")
        header_label.setFont(QFont("Helvetica", 14, QFont.Weight.Bold))
        header_label.setStyleSheet("color: #4FC3F7; border: none;")
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_label.setFixedHeight(25)
        data_layout.addWidget(header_label)
        
        # Patient info section with FIXED HEIGHT -
        PATIENT_INFO_HEIGHT = 150  # Adjusted for combined birth date/age and ICD in one line each
        patient_info_container = QFrame()
        patient_info_container.setFixedHeight(PATIENT_INFO_HEIGHT)
        self.create_patient_info_section_fixed_height(patient_info_container)
        data_layout.addWidget(patient_info_container)
        
        # FIXED SPACER to ensure data entry always starts at same position
        SPACER_TO_DATA_ENTRY = 0  # <-- ÄNDERN: Abstand zwischen Patient Info und Data Entry
        data_layout.addSpacing(SPACER_TO_DATA_ENTRY)
        
        # Data entry section -
        DATA_ENTRY_HEIGHT = 410
        entry_container = QFrame()
        entry_container.setFixedHeight(DATA_ENTRY_HEIGHT)
        self.create_data_entry_section_fixed_height(entry_container)
        data_layout.addWidget(entry_container)
        
        # Add stretch to push buttons to bottom
        data_layout.addStretch()
        
        # Buttons section at the bottom
        self.create_buttons_section(data_layout)
        
        main_layout.addWidget(data_frame)

    def create_patient_info_section_fixed_height(self, container):
        """Create patient information display section with fixed height"""
        container.setStyleSheet("""
            QFrame {
                background-color: #232F3B;
                border: none;
                border-radius: 0px;
                padding: 1px;
            }
        """)
        
        info_layout = QVBoxLayout(container)
        info_layout.setContentsMargins(10, 2, 0, 0)
        info_layout.setSpacing(0) 
        
        # Patient info labels and data - kompakte Darstellung
        self.name_data_label = QLabel("Name: -")
        self.name_data_label.setStyleSheet("color: white; font-size: 14px; border: none; margin: 0px;")
        self.name_data_label.setWordWrap(True)
        info_layout.addWidget(self.name_data_label)
        
        self.birth_date_data_label = QLabel("Geburtsdatum: -")
        self.birth_date_data_label.setStyleSheet("color: white; font-size: 14px; border: none; margin: 0px;")
        info_layout.addWidget(self.birth_date_data_label)
        
        # Diagnose-Label und Text kombiniert in einem Label für bessere Formatierung
        self.diagnosis_data_label = QLabel("<b>Diagnose:</b> -")
        self.diagnosis_data_label.setStyleSheet("color: white; font-size: 14px; border: none; margin: 0px; margin-top: 0px;")
        self.diagnosis_data_label.setWordWrap(True)
        info_layout.addWidget(self.diagnosis_data_label)
        
        # ICD-Code mit Beschreibung in einer Zeile
        self.icd_code_data_label = QLabel("<b>ICD:</b> -")
        self.icd_code_data_label.setStyleSheet("color: white; font-size: 14px; border: none; margin: 0px;")
        self.icd_code_data_label.setWordWrap(True)
        info_layout.addWidget(self.icd_code_data_label)
        
        # Edit ICD Code Button
        self.edit_icd_button = QPushButton("Edit ICD Code")
        self.edit_icd_button.setFixedHeight(25)
        self.edit_icd_button.setStyleSheet("""
            QPushButton {
                background-color: #114473;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 12px;
                font-weight: bold;
                padding: 3px 8px;
                margin-top: 5px;
            }
            QPushButton:hover {
                background-color: #1a5a9e;
            }
            QPushButton:pressed {
                background-color: #0d3659;
            }
        """)
        self.edit_icd_button.clicked.connect(self.open_icd_editor)
        info_layout.addWidget(self.edit_icd_button)
        
        # Add stretch to fill remaining space if content is smaller than max_height
        info_layout.addStretch()

    def create_data_entry_section_fixed_height(self, container):
        """Create data entry controls section with fixed height"""
        container.setStyleSheet("""
            QFrame {
                background-color: #232F3B;
                border: 1px solid #425061;
                border-radius: 6px;
                padding: 12px;
            }
        """)
        
        entry_layout = QVBoxLayout(container)
        entry_layout.setContentsMargins(0, 0, 0, 0) 
        entry_layout.setSpacing(5)  
        
        # Radiotherapie indiziert
        self.radio_label = QLabel("Radiotherapie indiziert:")
        self.radio_label.setStyleSheet(self.get_label_style(False))
        entry_layout.addWidget(self.radio_label)
        
        self.radiotherapy_combo = NoScrollComboBox()
        self.radiotherapy_combo.addItems(["-", "Ja", "Nein"])
        self.radiotherapy_combo.setStyleSheet(self.get_input_style())
        self.radiotherapy_combo.currentTextChanged.connect(self.on_radiotherapy_changed)
        self.radiotherapy_combo.currentTextChanged.connect(self.mark_unsaved_changes)
        entry_layout.addWidget(self.radiotherapy_combo)
        
        # Art des Aufgebots (conditional)
        self.aufgebot_label = QLabel("Art des Aufgebots:")
        self.aufgebot_label.setStyleSheet(self.get_label_style(False))
        self.aufgebot_label.setVisible(False)
        entry_layout.addWidget(self.aufgebot_label)
        
        self.aufgebot_combo = NoScrollComboBox()
        self.aufgebot_combo.addItems(["-", "Kat I: In 1-3 Tagen ohne Konsil", "Kat II: In 5-7 Tagen ohne Konsil", "Kat III: Nach Eingang des Konsils"])
        self.aufgebot_combo.setStyleSheet(self.get_input_style())
        self.aufgebot_combo.currentTextChanged.connect(self.update_label_styles)
        self.aufgebot_combo.currentTextChanged.connect(self.mark_unsaved_changes)
        self.aufgebot_combo.setVisible(False)
        entry_layout.addWidget(self.aufgebot_combo)
        
        # Teams Priorisierung (conditional)
        self.teams_label = QLabel("Teams Priorisierung:")
        self.teams_label.setStyleSheet(self.get_label_style(False))
        self.teams_label.setVisible(False)
        entry_layout.addWidget(self.teams_label)
        
        self.teams_button = QPushButton("Bitte Auswahl tätigen")
        self.teams_button.setStyleSheet("""
            QPushButton {
                background-color: #114473;
                color: white;
                border: 1px solid #2a3642;
                border-radius: 4px;
                padding: 5px 6px;
                font-size: 14px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #1a5a9e;
            }
        """)
        self.teams_button.clicked.connect(self.open_teams_priority_dialog)
        self.teams_button.setVisible(False)
        self.teams_priorities = []  # Store current priorities
        entry_layout.addWidget(self.teams_button)
        
        # Vormerken für Studie (conditional)
        self.studie_label = QLabel("Vormerken für Studie:")
        self.studie_label.setStyleSheet(self.get_label_style(False))
        self.studie_label.setVisible(False)
        entry_layout.addWidget(self.studie_label)
        
        self.studie_combo = NoScrollComboBox()
        self.studie_combo.addItems([
            "-",
            "nicht qualifiziert",
            "CHESS",
            "DeEscO",
            "FLASH",
            "HypoFocal",
            "MAGELLAN",
            "NoMask",
            "OligoCare",
            "OligoRARE",
            "PACCELIO",
            "PROTECT",
            "ReCare",
            "SHARP",
            "SINGLE ISOCENTER",
            "SPRINT",
            "TASTE",
            "X-SMILE"
        ])        
        self.studie_combo.setStyleSheet(self.get_input_style())
        self.studie_combo.currentTextChanged.connect(self.update_label_styles)
        self.studie_combo.currentTextChanged.connect(self.mark_unsaved_changes)
        self.studie_combo.setVisible(False)
        entry_layout.addWidget(self.studie_combo)
        
        # Bemerkung/Procedere
        self.bemerkung_label = QLabel("Bemerkung/Procedere:")
        self.bemerkung_label.setStyleSheet(self.get_label_style(False))
        entry_layout.addWidget(self.bemerkung_label)
        
        self.bemerkung_text = QTextEdit()
        self.bemerkung_text.setFixedHeight(52)  # <-- GEÄNDERT: von 62 auf 52 für kompaktere Darstellung
        self.bemerkung_text.setStyleSheet(self.get_textinput_style())
        self.bemerkung_text.textChanged.connect(self.update_label_styles)
        self.bemerkung_text.textChanged.connect(self.mark_unsaved_changes)
        entry_layout.addWidget(self.bemerkung_text)
        
        # Add stretch to fill remaining space
        entry_layout.addStretch()

    def create_buttons_section(self, layout):
        """Create buttons section"""
        button_layout = QVBoxLayout()
        button_layout.setSpacing(10)
        
        # Combined save and next patient button
        self.save_next_button = QPushButton("Speichern && Nächster Patient")
        self.save_next_button.setFixedHeight(40)
        self.save_next_button.setStyleSheet("""
            QPushButton {
                background-color: #1E90FF;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #4169E1;
            }
            QPushButton:pressed {
                background-color: #0000CD;
            }
        """)
        self.save_next_button.clicked.connect(self.save_and_next_patient)
        button_layout.addWidget(self.save_next_button)
        
        # Finalize tumorboard button
        self.finalize_button = QPushButton("Tumorboard abschließen")
        self.finalize_button.setFixedHeight(40)
        self.finalize_button.setStyleSheet("""
            QPushButton {
                background-color: #FF6B35;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #FF8C69;
            }
            QPushButton:pressed {
                background-color: #FF4500;
            }
        """)
        self.finalize_button.clicked.connect(self.finalize_tumorboard)
        button_layout.addWidget(self.finalize_button)
        
        layout.addLayout(button_layout)

    def mark_unsaved_changes(self):
        """Mark that there are unsaved changes"""
        # Ensure temp file exists when making changes
        if not self.ensure_temp_file_exists():
            logging.error("Cannot mark unsaved changes - failed to create temp file")
            return
            
        self.has_unsaved_changes = True

    def update_label_styles(self):
        """Update label styles based on their content"""
        # Radiotherapy label
        radio_filled = self.radiotherapy_combo.currentText() != "-"
        self.radio_label.setStyleSheet(self.get_label_style(radio_filled))
        
        # Aufgebot label (only if visible)
        if self.aufgebot_combo.isVisible():
            aufgebot_filled = self.aufgebot_combo.currentText() != "-"
            self.aufgebot_label.setStyleSheet(self.get_label_style(aufgebot_filled))
        
        # Teams label (only if visible)
        if self.teams_button.isVisible():
            teams_filled = bool(self.teams_priorities)
            self.teams_label.setStyleSheet(self.get_label_style(teams_filled))
        
        # Studie label (only if visible)
        if self.studie_combo.isVisible():
            studie_filled = self.studie_combo.currentText() != "-"
            self.studie_label.setStyleSheet(self.get_label_style(studie_filled))
        
        # Bemerkung label
        bemerkung_text = self.bemerkung_text.toPlainText().strip()
        bemerkung_filled = bool(bemerkung_text) and bemerkung_text != "-"
        self.bemerkung_label.setStyleSheet(self.get_label_style(bemerkung_filled))

    def on_radiotherapy_changed(self, text):
        """Handle radiotherapy selection change"""
        show_fields = (text == "Ja")
        self.aufgebot_label.setVisible(show_fields)
        self.aufgebot_combo.setVisible(show_fields)
        self.teams_label.setVisible(show_fields)
        self.teams_button.setVisible(show_fields)
        self.studie_label.setVisible(show_fields)
        self.studie_combo.setVisible(show_fields)
        
        # If showing fields for the first time, reset to default values
        if show_fields:
            self.aufgebot_combo.setCurrentText("-")
            self.studie_combo.setCurrentText("-")
            if not self.teams_priorities:
                self.teams_button.setText("Bitte Auswahl tätigen")
        
        # Update styles when visibility changes
        self.update_label_styles()
    
    def open_teams_priority_dialog(self):
        """Open the teams priority selection dialog"""
        dialog = TeamsPriorityDialog(self.teams_priorities, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.teams_priorities = dialog.get_priorities()
            self.update_teams_button_text()
            self.update_label_styles()
            self.mark_unsaved_changes()
    
    def update_teams_button_text(self):
        """Update the teams button text based on current priorities"""
        if self.teams_priorities:
            priority_text = " > ".join(self.teams_priorities)
            self.teams_button.setText(priority_text)
        else:
            self.teams_button.setText("Bitte Auswahl tätigen")

    def load_patient_data(self):
        """Load patient data from Excel file"""
        # Use temporary Excel file if available, otherwise use source file
        excel_path = self.temp_excel_path if self.temp_excel_path and self.temp_excel_path.exists() else self.source_excel_path
        
        try:
            df = pd.read_excel(excel_path, engine='openpyxl')
            
            if df.empty:
                logging.warning(f"Excel file is empty: {excel_path}")
                return
            
            # Clear existing patient data to avoid duplicates
            self.patients_data = []
            self.patient_states = {}
            
            # Extract patient data
            for index, row in df.iterrows():
                # Get patient name and check if it's valid
                patient_name = str(row.get('Name', '')).strip()
                
                # Skip empty rows or rows with invalid names
                if (patient_name == '' or patient_name == 'nan' or 
                    patient_name.lower() == 'nan' or pd.isna(row.get('Name'))):
                    continue
                
                # Clean patient number - remove .0 if present
                patient_number_raw = str(row.get('Patientennummer', f'{index + 1}'))
                if patient_number_raw.endswith('.0'):
                    patient_number_clean = patient_number_raw[:-2]
                else:
                    patient_number_clean = patient_number_raw
                
                # Calculate age from birth date
                birth_date_str = str(row.get('Geburtsdatum', '-'))
                calculated_age = self.calculate_age(birth_date_str)
                
                # Handle ICD code with multiple possible column names and clean data
                icd_code_raw = row.get('ICD-Code') or row.get('ICD-10') or row.get('ICD Code') or row.get('ICD10') or '-'
                icd_code = str(icd_code_raw).strip()
                if icd_code.lower() == 'nan' or pd.isna(icd_code_raw) or icd_code == '':
                    icd_code = '-'
                
                # Get form data and clean it
                radiotherapy_raw = str(row.get('Radiotherapie indiziert', ''))
                aufgebot_raw = str(row.get('Art des Aufgebots', ''))
                bemerkung_raw = str(row.get('Bemerkung/Procedere', ''))
                studie_raw = str(row.get('Vormerken für Studie', ''))
                teams_raw = str(row.get('Teams Priorisierung', ''))
                
                # Clean form data (handle NaN)
                radiotherapy = radiotherapy_raw if radiotherapy_raw != 'nan' and not pd.isna(radiotherapy_raw) else ''
                aufgebot = aufgebot_raw if aufgebot_raw != 'nan' and not pd.isna(aufgebot_raw) else ''
                bemerkung = bemerkung_raw if bemerkung_raw != 'nan' and not pd.isna(bemerkung_raw) else ''
                studie = studie_raw if studie_raw != 'nan' and not pd.isna(studie_raw) else ''
                teams = teams_raw if teams_raw != 'nan' and not pd.isna(teams_raw) else ''
                
                patient_data = {
                    'index': index,
                    'name': patient_name,
                    'birth_date': birth_date_str,
                    'age': calculated_age,
                    'diagnosis': str(row.get('Diagnose', '-')),
                    'icd_code': icd_code,
                    'patient_number': patient_number_clean,
                    'radiotherapy': radiotherapy,
                    'aufgebot': aufgebot,
                    'teams': teams,
                    'studie': studie,
                    'bemerkung': bemerkung
                }
                self.patients_data.append(patient_data)
                
                # Initialize patient state - check Excel data to determine correct state
                patient_index = len(self.patients_data) - 1
                if self.is_patient_skipped(patient_data):
                    self.patient_states[patient_index] = 'skipped'  # Mark as gray (overridden/not discussed)
                elif self.is_patient_complete(patient_data):
                    self.patient_states[patient_index] = 'completed'  # Mark as green
                else:
                    self.patient_states[patient_index] = 'normal'  # Keep as blue
            
            # Create patient buttons
            self.create_patient_buttons()
            
            # Load first patient
            if self.patients_data:
                self.load_patient(0)
            
            # Set initial finalize button state
            self.update_finalize_button_state()
            
            # Set initial delete button state
            self.update_delete_button_state()
                
            logging.info(f"Loaded {len(self.patients_data)} patients from Excel file")
            
        except Exception as e:
            logging.error(f"Error loading patient data: {e}")
            error_msg = QMessageBox(self)
            error_msg.setWindowTitle("Error")
            error_msg.setText(f"Could not load patient data: {e}")
            error_msg.setIcon(QMessageBox.Icon.Critical)
            error_msg.setStandardButtons(QMessageBox.StandardButton.Ok)
            error_msg.setStyleSheet("""
                QMessageBox {
                    background-color: #1a2633;
                    color: white;
                }
                QMessageBox QLabel {
                    color: white;
                    font-size: 14px;
                }
                QPushButton {
                    background-color: #114473;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 8px 16px;
                    font-weight: bold;
                    min-width: 80px;
                }
                QPushButton:hover {
                    background-color: #1a5a9e;
                }
            """)
            error_msg.exec()

    def create_patient_buttons(self):
        """Create clickable patient buttons in the left column"""
        # Clear existing buttons and stretch items
        for i in reversed(range(self.patient_list_layout.count())):
            item = self.patient_list_layout.itemAt(i)
            if item.widget():
                item.widget().setParent(None)
            else:
                # Remove spacer items
                self.patient_list_layout.removeItem(item)
        
        # Create buttons for each patient
        for i, patient in enumerate(self.patients_data):
            # Truncate name if too long
            button_text = patient['name']
            if len(button_text) > 30:
                button_text = button_text[:27] + "..."
            
            button = QPushButton(button_text)
            button.setFixedHeight(40)
            button.setFixedWidth(170)  # Adjusted for narrower column
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            
            # Set button style based on state
            self.update_patient_button_style(button, i)
            
            # Connect button click
            button.clicked.connect(lambda checked, idx=i: self.load_patient(idx))
            
            self.patient_list_layout.addWidget(button)
        
        # Add stretch to push all buttons to the top while maintaining 4px spacing
        self.patient_list_layout.addStretch()

    def update_patient_button_style(self, button, patient_index):
        """Update patient button style based on completion state"""
        state = self.patient_states.get(patient_index, 'normal')
        
        if state == 'completed':
            # Green for completed
            style = """
                QPushButton {
                    background-color: #2E8B57;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    font-weight: bold;
                    text-align: left;
                    padding: 8px;
                }
                QPushButton:hover {
                    background-color: #3CB371;
                }
            """
        elif state == 'skipped':
            # Gray for skipped
            style = """
                QPushButton {
                    background-color: #696969;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    font-weight: bold;
                    text-align: left;
                    padding: 8px;
                }
                QPushButton:hover {
                    background-color: #808080;
                }
            """
        else:
            # Normal style
            style = """
                QPushButton {
                    background-color: #114473;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    font-weight: bold;
                    text-align: left;
                    padding: 8px;
                }
                QPushButton:hover {
                    background-color: #1a5a9e;
                }
            """
        
        # Add selected style if this is the current patient
        if patient_index == self.current_patient_index:
            style = style.replace("background-color: #114473;", "background-color: #3292ea;")
            style = style.replace("background-color: #2E8B57;", "background-color: #228B22;")
            style = style.replace("background-color: #696969;", "background-color: #555555;")
        
        button.setStyleSheet(style)

    def format_label_with_value(self, label, value):
        """Format a label with bold prefix and normal value"""
        return f"<b>{label}</b> {value}"

    def load_patient(self, patient_index):
        """Load a specific patient's data"""
        if patient_index < 0 or patient_index >= len(self.patients_data):
            return
        
        self.current_patient_index = patient_index
        patient = self.patients_data[patient_index]
        
        # Update patient info display - most in one line, only diagnosis separate
        # Use HTML formatting to have bold labels and normal values
        self.name_data_label.setText(self.format_label_with_value("Name:", patient['name']))
        # Combine birth date and age in one line
        birth_date = patient['birth_date']
        age = patient['age']
        if birth_date != '-' and age != '-':
            self.birth_date_data_label.setText(f"<b>Geburtsdatum:</b> {birth_date} ({age})")
        else:
            self.birth_date_data_label.setText(f"<b>Geburtsdatum:</b> {birth_date}")
        # Diagnosis now uses the combined label with HTML formatting
        self.diagnosis_data_label.setText(f"<b>Diagnose:</b> {patient['diagnosis']}")
        
        # Set ICD-Code and description in one line
        icd_code = patient.get('icd_code', '-')
        if icd_code and icd_code != '-':
            # Get ICD description
            icd_description = get_icd_description_from_database(icd_code)
            if icd_description != '-' and not icd_description.startswith('ICD-Code:'):
                self.icd_code_data_label.setText(f"<b>ICD:</b> {icd_code} ({icd_description})")
            else:
                self.icd_code_data_label.setText(f"<b>ICD:</b> {icd_code}")
        else:
            self.icd_code_data_label.setText("<b>ICD:</b> -")
        
        # Load form data from Excel (not from cached patient data) to ensure proper reset
        excel_data = self.get_current_excel_data_for_patient(patient_index)
        
        # Set form fields based on Excel data
        self.radiotherapy_combo.setCurrentText(excel_data['radiotherapy'] if excel_data['radiotherapy'] not in ['', 'nan', '-'] else "-")
        self.aufgebot_combo.setCurrentText(excel_data['aufgebot'] if excel_data['aufgebot'] not in ['', 'nan', '-'] else "-")
        
        # Load teams priorities - use cached patient data first, then Excel data as fallback
        cached_teams = patient.get('teams', '')
        teams_data = cached_teams if cached_teams not in ['', 'nan', '-'] else excel_data['teams']
        teams_data = teams_data if teams_data not in ['', 'nan', '-'] else ""
        
        if teams_data:
            self.teams_priorities = [name.strip() for name in teams_data.split('>') if name.strip()]
        else:
            self.teams_priorities = []
        self.update_teams_button_text()
        
        self.studie_combo.setCurrentText(excel_data['studie'] if excel_data['studie'] not in ['', 'nan', '-'] else "-")
        self.bemerkung_text.setPlainText(excel_data['bemerkung'] if excel_data['bemerkung'] not in ['', 'nan', '-'] else "")
        
        # Update label styles after loading data
        self.update_label_styles()
        
        # Load PDF
        self.load_patient_pdf(patient)
        
        # Update button styles
        self.update_all_patient_button_styles()
        
        logging.info(f"Loaded patient {patient_index + 1}: {patient['name']}")

    def get_current_excel_data_for_patient(self, patient_index):
        """Get current form data for a patient from Excel file"""
        # Use temporary Excel file during session
        excel_path = self.temp_excel_path if self.temp_excel_path and self.temp_excel_path.exists() else self.source_excel_path
        
        try:
            df = pd.read_excel(excel_path, engine='openpyxl')
            patient = self.patients_data[patient_index]
            row_index = patient['index']
            
            # Get current Excel values
            radiotherapy = str(df.at[row_index, 'Radiotherapie indiziert']) if 'Radiotherapie indiziert' in df.columns else ''
            aufgebot = str(df.at[row_index, 'Art des Aufgebots']) if 'Art des Aufgebots' in df.columns else ''
            teams = str(df.at[row_index, 'Teams Priorisierung']) if 'Teams Priorisierung' in df.columns else ''
            studie = str(df.at[row_index, 'Vormerken für Studie']) if 'Vormerken für Studie' in df.columns else ''
            bemerkung = str(df.at[row_index, 'Bemerkung/Procedere']) if 'Bemerkung/Procedere' in df.columns else ''
            
            # Clean values (handle NaN)
            if radiotherapy == 'nan' or pd.isna(radiotherapy):
                radiotherapy = ''
            if aufgebot == 'nan' or pd.isna(aufgebot):
                aufgebot = ''
            if teams == 'nan' or pd.isna(teams):
                teams = ''
            if studie == 'nan' or pd.isna(studie):
                studie = ''
            if bemerkung == 'nan' or pd.isna(bemerkung):
                bemerkung = ''
            
            return {
                'radiotherapy': radiotherapy,
                'aufgebot': aufgebot,
                'teams': teams,
                'studie': studie,
                'bemerkung': bemerkung
            }
        except Exception as e:
            logging.error(f"Error getting Excel data for patient: {e}")
            return {
                'radiotherapy': '',
                'aufgebot': '',
                'teams': '',
                'studie': '',
                'bemerkung': ''
            }

    def load_patient_pdf(self, patient):
        """Load the PDF for the current patient"""
        # Extract first word (surname) from patient name
        patient_name = patient['name'].strip()
        first_word = patient_name.split()[0] if patient_name else "Unknown"
        
        # New PDF naming: "Nachname - Patientennummer.pdf"
        pdf_filename = f"{first_word} - {patient['patient_number']}.pdf"
        pdf_path = self.tumorboard_base_path / self.tumorboard_name / self.date_str / pdf_filename
        
        self.pdf_header_label.setText(f"TB-Anmeldung: {patient['name']}")
        
        if not hasattr(self, 'pdf_viewer'):
            return
        
        logging.info(f"Attempting to load PDF: {pdf_path}")
        
        if pdf_path.exists():
            try:
                # Convert to absolute path and ensure proper URL format
                absolute_path = pdf_path.resolve()
                # Use file:// protocol explicitly for better compatibility
                pdf_url = QUrl.fromLocalFile(str(absolute_path))
                logging.info(f"Loading PDF URL: {pdf_url.toString()}")
                
                # Load PDF with custom settings (no sidebar, 120% zoom)
                pdf_url_with_params = f"{pdf_url.toString()}#toolbar=1&navpanes=0&scrollbar=1&page=1&zoom=120"
                self.pdf_viewer.setUrl(QUrl(pdf_url_with_params))
                
                logging.info(f"Successfully initiated PDF load: {pdf_path}")
            except Exception as e:
                logging.error(f"Error loading PDF {pdf_path}: {e}")
                self.show_pdf_error(f"Error loading PDF: {e}")
        else:
            logging.warning(f"PDF not found: {pdf_path}")
            # Also try alternative naming patterns
            patient_position = self.patients_data.index(patient) + 1  # Fallback for old naming
            alt_patterns = [
                f"{first_word}-{patient['patient_number']}.pdf",  # Without spaces
                f"{patient['patient_number']}.pdf",  # Just the patient number
                f"{first_word}_{patient['patient_number']}.pdf",  # Underscore instead of dash
                f"{first_word} _ {patient['patient_number']}.pdf",  # Spaces with underscore
                f"{patient_position} - {patient['patient_number']}.pdf",  # Old position-based naming
                f"{patient_position}-{patient['patient_number']}.pdf",  # Old position-based without spaces
                f"Patient_{patient_position}.pdf"  # Generic pattern
            ]
            
            for alt_pattern in alt_patterns:
                alt_path = self.tumorboard_base_path / self.tumorboard_name / self.date_str / alt_pattern
                if alt_path.exists():
                    logging.info(f"Found alternative PDF: {alt_path}")
                    try:
                        absolute_path = alt_path.resolve()
                        pdf_url = QUrl.fromLocalFile(str(absolute_path))
                        # Load with same settings (no sidebar, 115% zoom)
                        pdf_url_with_params = f"{pdf_url.toString()}#toolbar=1&navpanes=0&scrollbar=1&page=1&zoom=115"
                        self.pdf_viewer.setUrl(QUrl(pdf_url_with_params))
                        return
                    except Exception as e:
                        logging.error(f"Error loading alternative PDF {alt_path}: {e}")
                        continue
            
            self.show_pdf_error(f"PDF nicht gefunden: {pdf_filename}")

    def show_pdf_error(self, error_message):
        """Show error message in PDF viewer"""
        if hasattr(self, 'pdf_viewer'):
            self.pdf_viewer.setHtml(f"""
                <html><body style="background-color: #1a2633; color: white; text-align: center; padding: 50px; font-family: Arial;">
                    <h2>PDF Fehler</h2>
                    <p>{error_message}</p>
                </body></html>
            """)

    def update_all_patient_button_styles(self):
        """Update all patient button styles"""
        for i in range(self.patient_list_layout.count()):
            button = self.patient_list_layout.itemAt(i).widget()
            if isinstance(button, QPushButton):
                self.update_patient_button_style(button, i)
        
        # Also update finalize button state
        self.update_finalize_button_state()

    def update_finalize_button_state(self):
        """Update finalize button color based on patient completion states"""
        unprocessed_count = 0
        
        for patient_index in range(len(self.patients_data)):
            state = self.patient_states.get(patient_index, 'normal')
            if state == 'normal':  # Not completed or skipped
                unprocessed_count += 1
        
        if unprocessed_count == 0:
            # All patients processed - orange button
            self.finalize_button.setStyleSheet("""
                QPushButton {
                    background-color: #FF8C00;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    font-weight: bold;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #FFA500;
                }
                QPushButton:pressed {
                    background-color: #FF7F00;
                }
            """)
        else:
            # Still unprocessed patients - gray button
            self.finalize_button.setStyleSheet("""
                QPushButton {
                    background-color: #666666;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    font-weight: bold;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #777777;
                }
                QPushButton:pressed {
                    background-color: #555555;
                }
            """)
        
        # Store unprocessed count for use in finalize dialog
        self.unprocessed_patient_count = unprocessed_count

    def save_and_next_patient(self):
        """Save current patient data and move to next patient"""
        if not self.patients_data:
            return
        
        current_patient = self.patients_data[self.current_patient_index]
        
        # Update current patient data
        current_patient['radiotherapy'] = self.radiotherapy_combo.currentText()
        current_patient['aufgebot'] = self.aufgebot_combo.currentText()
        current_patient['teams'] = " > ".join(self.teams_priorities) if self.teams_priorities else ""
        current_patient['studie'] = self.studie_combo.currentText()
        current_patient['bemerkung'] = self.bemerkung_text.toPlainText()
        
        # Mark as having unsaved changes
        self.has_unsaved_changes = True
        
        # Check if current patient is complete
        if not self.is_patient_complete(current_patient):
            missing_fields = self.get_missing_fields(current_patient)
            
            # Show dialog for incomplete patient
            dialog = PatientNotRecordedDialog(missing_fields, self)
            result = dialog.exec()
            
            if result == QDialog.DialogCode.Accepted:
                # Mark as skipped and set default values
                self.patient_states[self.current_patient_index] = 'skipped'
                current_patient['radiotherapy'] = "-"
                current_patient['aufgebot'] = "-"
                current_patient['teams'] = "-"
                current_patient['studie'] = "-"
                current_patient['bemerkung'] = "-"
                
                # Save the changes
                try:
                    self.save_to_excel()
                except Exception as e:
                    logging.error(f"Error saving skipped patient data: {e}")
            else:
                # Stay with current patient
                return
        else:
            # Mark as completed
            self.patient_states[self.current_patient_index] = 'completed'
            # Save the changes
            try:
                self.save_to_excel()
            except Exception as e:
                logging.error(f"Error saving completed patient data: {e}")
        
        # Update button styles
        self.update_all_patient_button_styles()
        
        # Check if this was the last patient
        next_index = self.current_patient_index + 1
        if next_index >= len(self.patients_data):
            # This was the last patient - show completion dialog
            unprocessed_count = 0
            for patient_index in range(len(self.patients_data)):
                state = self.patient_states.get(patient_index, 'normal')
                if state == 'normal':  # Not completed or skipped
                    unprocessed_count += 1
            
            dialog = LastPatientCompletedDialog(unprocessed_count, self)
            dialog.exec()
        else:
            # Move to next patient
            self.load_patient(next_index)

    def is_patient_complete(self, patient):
        """Check if patient data is complete"""
        radiotherapy = patient['radiotherapy']
        aufgebot = patient['aufgebot']
        teams = patient.get('teams', '')
        bemerkung = patient['bemerkung'].strip()
        
        # Radiotherapy must be set
        if radiotherapy == "-" or radiotherapy == "":
            return False
        
        # If radiotherapy is "Ja", aufgebot and teams must be set
        if radiotherapy == "Ja":
            if aufgebot == "-" or aufgebot == "":
                return False
            if not teams or teams == "-":
                return False
        
        # Bemerkung must have content (not empty and not just "-")
        if not bemerkung or bemerkung == "-":
            return False
        
        return True

    def get_missing_fields(self, patient):
        """Get list of missing required fields"""
        missing = []
        
        radiotherapy = patient['radiotherapy']
        aufgebot = patient['aufgebot']
        teams = patient.get('teams', '')
        bemerkung = patient['bemerkung'].strip()
        
        if radiotherapy == "-" or radiotherapy == "":
            missing.append("Radiotherapie indiziert")
        
        if radiotherapy == "Ja":
            if aufgebot == "-" or aufgebot == "":
                missing.append("Art des Aufgebots")
            if not teams or teams == "-":
                missing.append("Teams Priorisierung")
        
        if not bemerkung or bemerkung == "-":
            missing.append("Bemerkung/Procedere")
        
        return missing

    def finalize_tumorboard(self):
        """Handle the finalize tumorboard button"""
        # Show arzt dialog to get attending physician name
        arzt_dialog = AnwesenderArztDialog(self)
        result = arzt_dialog.exec()
        
        if result != QDialog.DialogCode.Accepted:
            # User cancelled, don't proceed
            return
        
        # Get attending physician data
        nachname = arzt_dialog.get_arzt_data()
        
        # WICHTIG: Check if this is first time finalization BEFORE writing timestamp file
        timestamp_file = self.tumorboard_base_path / self.tumorboard_name / self.date_str / "finalized_timestamp.txt"
        is_first_time_finalization = not timestamp_file.exists()
        
        # Check which patients were changed before saving
        changed_patients = self.get_changed_patients_for_finalization()
        
        # Save current patient data to temporary file first
        try:
            self.save_to_excel(skip_edit_logging=True)  # Skip automatic edit logging
        except Exception as e:
            logging.error(f"Error saving to temporary file before finalization: {e}")
            error_msg = QMessageBox(self)
            error_msg.setWindowTitle("Fehler")
            error_msg.setText(f"Fehler beim Speichern in temporäre Datei: {e}")
            error_msg.setIcon(QMessageBox.Icon.Critical)
            error_msg.setStandardButtons(QMessageBox.StandardButton.Ok)
            error_msg.setStyleSheet("""
                QMessageBox {
                    background-color: #1a2633;
                    color: white;
                }
                QMessageBox QLabel {
                    color: white;
                    font-size: 14px;
                }
                QPushButton {
                    background-color: #114473;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 8px 16px;
                    font-weight: bold;
                    min-width: 80px;
                }
                QPushButton:hover {
                    background-color: #1a5a9e;
                }
            """)
            error_msg.exec()
            return
        
        # Copy temporary file to source file
        try:
            self.copy_temp_to_source()
            logging.info("Successfully copied temporary file to source")
        except Exception as e:
            logging.error(f"Error copying temporary file to source: {e}")
            error_msg = QMessageBox(self)
            error_msg.setWindowTitle("Fehler beim Übertragen")
            error_msg.setText(f"Fehler beim Übertragen der Änderungen zur Haupt-Excel-Datei:\n\n{str(e)}\n\nBitte stellen Sie sicher, dass:\n• Die Excel-Datei nicht in einem anderen Programm geöffnet ist\n• Sie Schreibberechtigung für den Ordner haben\n• Genügend Speicherplatz vorhanden ist")
            error_msg.setIcon(QMessageBox.Icon.Critical)
            error_msg.setStandardButtons(QMessageBox.StandardButton.Ok)
            error_msg.setStyleSheet("""
                QMessageBox {
                    background-color: #1a2633;
                    color: white;
                }
                QMessageBox QLabel {
                    color: white;
                    font-size: 14px;
                }
                QPushButton {
                    background-color: #114473;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 8px 16px;
                    font-weight: bold;
                    min-width: 80px;
                }
                QPushButton:hover {
                    background-color: #1a5a9e;
                }
            """)
            error_msg.exec()
            return
        
        # Create timestamp
        now = datetime.now()
        timestamp_str = now.strftime("%d.%m.%Y %H:%M")
        user_name = f"{nachname}"
        
        # Save timestamp to file
        try:
            if is_first_time_finalization:
                # First time finalization
                with open(timestamp_file, 'w', encoding='utf-8') as f:
                    f.write(f"Abgeschlossen: {timestamp_str} von {user_name}\n")
                
                logging.info(f"Tumorboard first finalized at {timestamp_str} by {user_name}")
            else:
                # Already finalized before - this is an edit session
                # Always add edit entry for edit sessions (user explicitly clicked finalize again)
                edit_entry = f"Editiert: {timestamp_str} von {user_name}\n"
                
                with open(timestamp_file, 'a', encoding='utf-8') as f:
                    f.write(edit_entry)
                
                logging.info(f"Logged edit session by {user_name}")
            
        except Exception as e:
            logging.error(f"Error saving timestamp: {e}")
            error_msg = QMessageBox(self)
            error_msg.setWindowTitle("Fehler")
            error_msg.setText(f"Fehler beim Speichern des Timestamps: {e}")
            error_msg.setIcon(QMessageBox.Icon.Critical)
            error_msg.setStandardButtons(QMessageBox.StandardButton.Ok)
            error_msg.setStyleSheet("""
                QMessageBox {
                    background-color: #1a2633;
                    color: white;
                }
                QMessageBox QLabel {
                    color: white;
                    font-size: 14px;
                }
                QPushButton {
                    background-color: #114473;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 8px 16px;
                    font-weight: bold;
                    min-width: 80px;
                }
                QPushButton:hover {
                    background-color: #1a5a9e;
                }
            """)
            error_msg.exec()
            return
        
        # Export to collection Excel file
        try:
            # Skip database sync if using fallback path (not K: drive)
            skip_db_sync = self.is_using_fallback_path
            export_success = export_tumorboard_to_collection(self.tumorboard_name, self.date_str, self.tumorboard_base_path, skip_database_sync=skip_db_sync)
            if export_success:
                logging.info(f"Successfully exported {self.tumorboard_name} {self.date_str} to collection Excel")
                
                # Update database completion tracking (only if NOT using fallback path)
                if not self.is_using_fallback_path:
                    try:
                        from utils.database_utils import TumorboardDatabase
                        db = TumorboardDatabase()
                        
                        # Use the previously determined finalization status
                        is_edit = not is_first_time_finalization
                        
                        # Update session completion data
                        success = db.update_session_completion_data(
                            self.tumorboard_name, 
                            self.date_str, 
                            finalized_by=user_name,
                            is_edit=is_edit
                        )
                        
                        if success:
                            logging.info(f"Successfully updated session completion tracking for {self.tumorboard_name} {self.date_str}")
                        else:
                            logging.warning(f"Failed to update session completion tracking for {self.tumorboard_name} {self.date_str}")
                            
                    except Exception as tracking_error:
                        logging.error(f"Error updating session completion tracking: {tracking_error}")
                        # Don't fail the entire operation if tracking fails
                else:
                    logging.info(f"Skipping database completion tracking for {self.tumorboard_name} {self.date_str} - using fallback path")
                
                # Export patients by category to backoffice Excel files (only on first finalization)
                if is_first_time_finalization:
                    try:
                        from utils.excel_export_utils import export_patients_by_category
                        category_export_success = export_patients_by_category(self.tumorboard_name, self.date_str, self.tumorboard_base_path)
                        if category_export_success:
                            logging.info(f"Successfully exported patients by category for {self.tumorboard_name} {self.date_str}")
                        else:
                            logging.warning(f"Category export failed for {self.tumorboard_name} {self.date_str}")
                    except Exception as category_error:
                        logging.error(f"Error during category export: {category_error}")
                        # Don't fail the entire operation if category export fails
                else:
                    logging.info(f"Skipping category export for {self.tumorboard_name} {self.date_str} - already finalized before")
            else:
                logging.warning(f"Export to collection Excel failed for {self.tumorboard_name} {self.date_str}")
                # Show error message to user if collection file doesn't exist
                tumorboard_dir = self.tumorboard_base_path / self.tumorboard_name
                collection_file_found = False
                collection_file_name = "alle_tumorboards_*.xlsx"
                
                # Check if any collection file exists
                for file in tumorboard_dir.glob("alle_tumorboards_*.xlsx"):
                    collection_file_found = True
                    collection_file_name = file.name
                    break
                
                if not collection_file_found:
                    error_msg = QMessageBox(self)
                    error_msg.setWindowTitle("Export-Fehler")
                    error_msg.setText(f"Die Sammel-Excel-Datei für {self.tumorboard_name} wurde nicht gefunden.\n\n"
                                    f"Erwartet wird eine Datei mit dem Namen 'alle_tumorboards_*.xlsx' im Ordner:\n"
                                    f"{tumorboard_dir}\n\n"
                                    f"Das Tumorboard wurde erfolgreich abgeschlossen, aber der Export in die "
                                    f"Sammel-Excel-Datei ist fehlgeschlagen.\n\n"
                                    f"Bitte wenden Sie sich an Ihren Administrator.")
                    error_msg.setIcon(QMessageBox.Icon.Warning)
                    error_msg.setStandardButtons(QMessageBox.StandardButton.Ok)
                    error_msg.setStyleSheet("""
                        QMessageBox {
                            background-color: #1a2633;
                            color: white;
                        }
                        QMessageBox QLabel {
                            color: white;
                            font-size: 14px;
                        }
                        QPushButton {
                            background-color: #114473;
                            color: white;
                            border: none;
                            border-radius: 4px;
                            padding: 8px 16px;
                            font-weight: bold;
                            min-width: 80px;
                        }
                        QPushButton:hover {
                            background-color: #1a5a9e;
                        }
                    """)
                    error_msg.exec()
        except Exception as e:
            logging.error(f"Error during collection Excel export: {e}")
            # Show generic error message to user
            error_msg = QMessageBox(self)
            error_msg.setWindowTitle("Export-Fehler")
            error_msg.setText(f"Fehler beim Export in die Sammel-Excel-Datei:\n\n{str(e)}\n\n"
                            f"Das Tumorboard wurde erfolgreich abgeschlossen, aber der Export in die "
                            f"Sammel-Excel-Datei ist fehlgeschlagen.\n\n"
                            f"Bitte wenden Sie sich an Ihren Administrator.")
            error_msg.setIcon(QMessageBox.Icon.Warning)
            error_msg.setStandardButtons(QMessageBox.StandardButton.Ok)
            error_msg.setStyleSheet("""
                QMessageBox {
                    background-color: #1a2633;
                    color: white;
                }
                QMessageBox QLabel {
                    color: white;
                    font-size: 14px;
                }
                QPushButton {
                    background-color: #114473;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 8px 16px;
                    font-weight: bold;
                    min-width: 80px;
                }
                QPushButton:hover {
                    background-color: #1a5a9e;
                }
            """)
            error_msg.exec()
        
        # Clean up temporary file after successful finalization
        self.cleanup_temp_file()
        self.has_unsaved_changes = False
        
        # Navigate back to Excel viewer page
        self.main_window.navigate_back_to_excel_viewer(self.tumorboard_name, self.date_str)
        
        # Show appropriate final message based on finalization type
        if is_first_time_finalization:
            # First time finalization - show success/warning based on export destination
            if self.is_using_fallback_path:
                # Local export - show warning dialog that includes success notification
                warning_msg = QMessageBox(self)
                warning_msg.setWindowTitle("Warnung - Lokaler Export")
                warning_msg.setText(f"Das Tumorboard wurde erfolgreich abgeschlossen!\n\nBitte beachten Sie: Die Daten wurden in die lokalen Excel-Tabellen im Pfad {self.tumorboard_base_path} exportiert. Es muss ein manueller Übertrag auf den Server-Ordner in RAO_Daten erfolgen. Bei Fragen melden Sie sich bei Ihrem Administrator.")
                warning_msg.setIcon(QMessageBox.Icon.Warning)
                warning_msg.setStandardButtons(QMessageBox.StandardButton.Ok)
                warning_msg.setStyleSheet("""
                    QMessageBox {
                        background-color: #1a2633;
                        color: white;
                    }
                    QMessageBox QLabel {
                        color: white;
                        font-size: 14px;
                        padding: 10px;
                    }
                    QPushButton {
                        background-color: #FF8C00;
                        color: white;
                        border: none;
                        border-radius: 4px;
                        padding: 8px 16px;
                        font-weight: bold;
                        min-width: 80px;
                    }
                    QPushButton:hover {
                        background-color: #FFA500;
                    }
                """)
                warning_msg.exec()
            else:
                # Intranet export - show success dialog with K:\ reference
                success_msg = QMessageBox(self)
                success_msg.setWindowTitle("Erfolg")
                success_msg.setText(f"Das Tumorboard wurde erfolgreich abgeschlossen!\n\nDie Daten wurden erfolgreich nach K:\\RAO_Projekte\\App\\tumorboards exportiert.")
                success_msg.setIcon(QMessageBox.Icon.Information)
                success_msg.setStandardButtons(QMessageBox.StandardButton.Ok)
                success_msg.setStyleSheet("""
                    QMessageBox {
                        background-color: #1a2633;
                        color: white;
                    }
                    QMessageBox QLabel {
                        color: white;
                        font-size: 14px;
                        padding: 10px;
                    }
                    QPushButton {
                        background-color: #2E8B57;
                        color: white;
                        border: none;
                        border-radius: 4px;
                        padding: 8px 16px;
                        font-weight: bold;
                        min-width: 80px;
                    }
                    QPushButton:hover {
                        background-color: #3CB371;
                    }
                """)
                success_msg.exec()
        else:
            # Edit session - show edit completion dialog
            edit_msg = QMessageBox(self)
            edit_msg.setWindowTitle("Daten aktualisiert")
            edit_msg.setText("Daten aktualisiert und in Database übertragen.\n\nBitte beachten: Es wurden nicht nochmals alle Patientendaten zur Bearbeitung ans Backoffice gesendet. Eine Änderung in der Backoffice Excel-Datei muss manuell erfolgen.")
            edit_msg.setIcon(QMessageBox.Icon.Information)
            edit_msg.setStandardButtons(QMessageBox.StandardButton.Ok)
            edit_msg.setStyleSheet("""
                QMessageBox {
                    background-color: #1a2633;
                    color: white;
                }
                QMessageBox QLabel {
                    color: white;
                    font-size: 14px;
                    padding: 10px;
                }
                QPushButton {
                    background-color: #114473;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 8px 16px;
                    font-weight: bold;
                    min-width: 80px;
                }
                QPushButton:hover {
                    background-color: #1a5a9e;
                }
            """)
            edit_msg.exec()
        
        logging.info("Tumorboard finalization completed")

    def save_to_excel(self, skip_edit_logging=False):
        """Save all patient data back to Excel file"""
        # Ensure temp file exists for editing
        if not self.ensure_temp_file_exists():
            logging.error("Cannot save to Excel - failed to ensure temp file exists")
            raise Exception("Temporäre Datei konnte nicht erstellt werden")
        
        # Use temporary Excel file during session, source file only during finalization
        excel_path = self.temp_excel_path if self.temp_excel_path and self.temp_excel_path.exists() else self.source_excel_path
        
        # Read current Excel file
        df = pd.read_excel(excel_path, engine='openpyxl')
        
        # Track which patients were changed (for edit logging)
        changed_patients = []
        
        # Update the relevant columns using the original Excel index
        for patient in self.patients_data:
            row_index = patient['index']
            
            # Check if data changed from what's in Excel
            current_radio = str(df.at[row_index, 'Radiotherapie indiziert']) if 'Radiotherapie indiziert' in df.columns else ''
            current_aufgebot = str(df.at[row_index, 'Art des Aufgebots']) if 'Art des Aufgebots' in df.columns else ''
            current_teams = str(df.at[row_index, 'Teams Priorisierung']) if 'Teams Priorisierung' in df.columns else ''
            current_studie = str(df.at[row_index, 'Vormerken für Studie']) if 'Vormerken für Studie' in df.columns else ''
            current_bemerkung = str(df.at[row_index, 'Bemerkung/Procedere']) if 'Bemerkung/Procedere' in df.columns else ''
            
            # Clean current values (handle NaN)
            if current_radio == 'nan' or pd.isna(current_radio):
                current_radio = ''
            if current_aufgebot == 'nan' or pd.isna(current_aufgebot):
                current_aufgebot = ''
            if current_teams == 'nan' or pd.isna(current_teams):
                current_teams = ''
            if current_studie == 'nan' or pd.isna(current_studie):
                current_studie = ''
            if current_bemerkung == 'nan' or pd.isna(current_bemerkung):
                current_bemerkung = ''
            
            # Get patient teams data (default to empty string if not present)
            patient_teams = patient.get('teams', '')
            
            # Check if any field changed
            if (patient['radiotherapy'] != current_radio or 
                patient['aufgebot'] != current_aufgebot or 
                patient_teams != current_teams or
                patient['studie'] != current_studie or
                patient['bemerkung'] != current_bemerkung):
                changed_patients.append(patient['patient_number'])
            
            # Update the fields
            df.at[row_index, 'Radiotherapie indiziert'] = patient['radiotherapy']
            df.at[row_index, 'Art des Aufgebots'] = patient['aufgebot']
            df.at[row_index, 'Teams Priorisierung'] = patient_teams
            df.at[row_index, 'Vormerken für Studie'] = patient['studie']
            df.at[row_index, 'Bemerkung/Procedere'] = patient['bemerkung']
        
        # Save back to Excel
        df.to_excel(excel_path, index=False, engine='openpyxl')
        
        # Note: Edit logging is now only done during finalization to avoid redundant entries
        # Individual saves during session do not create timestamp entries
        
        logging.info(f"Saved patient data to Excel: {excel_path}")

    @staticmethod
    def get_benutzerdaten():
        """Get user data from ~/patdata/benutzerdaten.txt"""
        user_home = Path.home()
        patdata_dir = user_home / "patdata"
        benutzerdaten_file = patdata_dir / "benutzerdaten.txt"
        
        # Ensure patdata directory exists
        try:
            patdata_dir.mkdir(exist_ok=True)
        except OSError as e:
            logging.error(f"Could not create directory '{patdata_dir}': {e}")
            return None, None
        
        if benutzerdaten_file.exists():
            try:
                with open(benutzerdaten_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                data = {}
                for line in lines:
                    line = line.strip()
                    if '=' in line:
                        key, value = line.split('=', 1)
                        data[key.strip()] = value.strip()
                
                if "Nachname" in data and data["Nachname"] and \
                   "Vorname" in data and data["Vorname"]:
                    return data["Nachname"], data["Vorname"]
                else:
                    logging.warning(f"Invalid or incomplete entries in '{benutzerdaten_file}'")
                    return None, None
                    
            except Exception as e:
                logging.error(f"Error reading '{benutzerdaten_file}': {e}")
                return None, None
        
        logging.info(f"User data file '{benutzerdaten_file}' not found")
        return None, None
    
    @staticmethod
    def save_benutzerdaten(nachname, vorname):
        """Save user data to ~/patdata/benutzerdaten.txt"""
        user_home = Path.home()
        patdata_dir = user_home / "patdata"
        benutzerdaten_file = patdata_dir / "benutzerdaten.txt"
        
        # Input validation
        if not nachname or not nachname.strip():
            logging.error("Invalid or empty surname for saving")
            return False
        if not vorname or not vorname.strip():
            logging.error("Invalid or empty first name for saving")
            return False
        
        nachname = nachname.strip()
        vorname = vorname.strip()
        
        try:
            patdata_dir.mkdir(exist_ok=True)
            
            with open(benutzerdaten_file, 'w', encoding='utf-8') as f:
                f.write(f"Nachname={nachname}\n")
                f.write(f"Vorname={vorname}\n")
            
            logging.info(f"User data successfully saved to '{benutzerdaten_file}'")
            return True
            
        except OSError as e:
            logging.error(f"Could not create directory '{patdata_dir}' or access it: {e}")
            return False
        except IOError as e:
            logging.error(f"Could not write to file '{benutzerdaten_file}': {e}")
            return False
        except Exception as e:
            logging.error(f"Error saving user data to '{benutzerdaten_file}': {e}")
            return False

    def delete_current_patient(self):
        """Delete the currently selected patient with confirmation dialog"""
        if not self.patients_data or self.current_patient_index >= len(self.patients_data):
            return
        
        current_patient = self.patients_data[self.current_patient_index]
        patient_name = current_patient['name']
        
        # Confirmation dialog
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Patient löschen")
        msg_box.setText(f"Sind Sie sicher, dass der Patient\n\n{patient_name}\n\ngelöscht werden soll?")
        msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg_box.setDefaultButton(QMessageBox.StandardButton.No)
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: #1a2633;
                color: white;
            }
            QMessageBox QLabel {
                color: white;
                font-size: 14px;
            }
            QPushButton {
                background-color: #114473;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #1a5a9e;
            }
        """)
        
        result = msg_box.exec()
        
        if result == QMessageBox.StandardButton.Yes:
            # Mark as having unsaved changes
            self.has_unsaved_changes = True
            
            # Get the Excel row index before deleting from memory
            current_patient = self.patients_data[self.current_patient_index]
            excel_row_index = current_patient['index']
            
            # Delete patient from temporary Excel file first
            try:
                self.delete_patient_from_excel(excel_row_index)
                logging.info(f"Deleted patient {patient_name} from Excel at row {excel_row_index}")
            except Exception as e:
                logging.error(f"Error deleting patient from Excel: {e}")
                # Show error message but continue with memory deletion
                error_msg = QMessageBox(self)
                error_msg.setWindowTitle("Fehler")
                error_msg.setText(f"Fehler beim Löschen aus Excel-Datei: {e}")
                error_msg.setIcon(QMessageBox.Icon.Warning)
                error_msg.setStandardButtons(QMessageBox.StandardButton.Ok)
                error_msg.setStyleSheet("""
                    QMessageBox {
                        background-color: #1a2633;
                        color: white;
                    }
                    QMessageBox QLabel {
                        color: white;
                        font-size: 14px;
                    }
                    QPushButton {
                        background-color: #114473;
                        color: white;
                        border: none;
                        border-radius: 4px;
                        padding: 8px 16px;
                        font-weight: bold;
                        min-width: 80px;
                    }
                    QPushButton:hover {
                        background-color: #1a5a9e;
                    }
                """)
                error_msg.exec()
            
            # Reload all patient data from Excel to ensure consistency
            # This is necessary because deleting a row shifts all subsequent row indices
            self.clear_and_reload_patient_data()
            
            # Adjust current patient index if necessary
            if self.current_patient_index >= len(self.patients_data) and len(self.patients_data) > 0:
                self.current_patient_index = len(self.patients_data) - 1
            elif len(self.patients_data) == 0:
                self.current_patient_index = 0
            
            # Load current patient or clear display if no patients left
            if self.patients_data and self.current_patient_index < len(self.patients_data):
                self.load_patient(self.current_patient_index)
            else:
                self.clear_patient_display()
            
            # Update button states
            self.update_delete_button_state()
            
            logging.info(f"Deleted patient: {patient_name}")

    def delete_patient_from_excel(self, row_index):
        """Delete a patient row from the temporary Excel file"""
        # Use temporary Excel file during session
        excel_path = self.temp_excel_path if self.temp_excel_path and self.temp_excel_path.exists() else self.source_excel_path
        
        try:
            # Read current Excel file
            df = pd.read_excel(excel_path, engine='openpyxl')
            
            # Check if row index is valid
            if row_index < 0 or row_index >= len(df):
                raise ValueError(f"Invalid row index {row_index}. Excel has {len(df)} rows.")
            
            # Drop the row at the specified index
            df = df.drop(index=row_index).reset_index(drop=True)
            
            # Save back to Excel
            df.to_excel(excel_path, index=False, engine='openpyxl')
            
            logging.info(f"Successfully deleted row {row_index} from Excel file: {excel_path}")
            
        except Exception as e:
            logging.error(f"Error deleting patient from Excel: {e}")
            raise e

    def clear_patient_display(self):
        """Clear patient information display when no patients are available"""
        self.name_data_label.setText("Name: -")
        self.birth_date_data_label.setText("Geburtsdatum: -")
        self.diagnosis_data_label.setText("<b>Diagnose:</b> -")
        self.icd_code_data_label.setText("<b>ICD:</b> -")
        
        # Clear form fields
        self.radiotherapy_combo.setCurrentText("-")
        self.aufgebot_combo.setCurrentText("-")
        self.teams_priorities = []
        self.update_teams_button_text()
        self.studie_combo.setCurrentText("-")
        self.bemerkung_text.setPlainText("")
        
        # Update PDF header
        self.pdf_header_label.setText("TB-Anmeldung: Kein Patient ausgewählt")
        
        # Show message in PDF viewer
        if hasattr(self, 'pdf_viewer'):
            self.pdf_viewer.setHtml("""
                <html><body style="background-color: #1a2633; color: white; text-align: center; padding: 50px; font-family: Arial;">
                    <h2>Kein Patient ausgewählt</h2>
                    <p>Alle Patienten wurden gelöscht oder es sind keine Patienten vorhanden.</p>
                </body></html>
            """)

    def update_delete_button_state(self):
        """Update the delete button state based on available patients"""
        has_patients = len(self.patients_data) > 0
        self.delete_patient_button.setEnabled(has_patients)

    def add_new_patient(self):
        """Add a new patient manually through dialog"""
        dialog = AddPatientDialog(self)
        result = dialog.exec()
        
        if result == QDialog.DialogCode.Accepted:
            patient_data = dialog.get_patient_data()
            
            # Validate required fields
            if not patient_data['name'] or not patient_data['birth_date']:
                missing_fields = []
                if not patient_data['name']:
                    missing_fields.append("Name")
                if not patient_data['birth_date']:
                    missing_fields.append("Geburtsdatum")
                
                missing_text = ", ".join(missing_fields)
                QMessageBox.warning(self, "Eingabe fehlt", 
                                  f"Folgende Felder müssen ausgefüllt werden: {missing_text}")
                return
            
            # Check if patient number already exists (only if patient number is provided)
            if patient_data['patient_number']:  # Only check if patient number is not empty
                for existing_patient in self.patients_data:
                    if existing_patient['patient_number'] == patient_data['patient_number']:
                        QMessageBox.warning(self, "Patient existiert", 
                                          f"Ein Patient mit der Nummer {patient_data['patient_number']} existiert bereits.")
                        return
            
            # Calculate age from birth date (birth date is now required)
            calculated_age = self.calculate_age(patient_data['birth_date'])
            
            # Create new patient data entry
            new_patient = {
                'index': len(self.patients_data),  # Temporary index
                'name': patient_data['name'],
                'birth_date': patient_data['birth_date'],
                'age': calculated_age,
                'diagnosis': patient_data['diagnosis'] if patient_data['diagnosis'] else '-',
                'icd_code': patient_data['icd_code'] if patient_data['icd_code'] else '-',
                'patient_number': patient_data['patient_number'] if patient_data['patient_number'] else '-',
                'radiotherapy': '',
                'aufgebot': '',
                'teams': '',
                'studie': '',
                'bemerkung': ''
            }
            
            # Add to patients list
            self.patients_data.append(new_patient)
            
            # Initialize patient state
            patient_index = len(self.patients_data) - 1
            self.patient_states[patient_index] = 'normal'
            
            # Mark as having unsaved changes
            self.has_unsaved_changes = True
            
            # Add to Excel file
            try:
                self.add_patient_to_excel(new_patient)
                
                # Reload all patient data from Excel to ensure consistency
                self.patients_data = []  # Clear current data
                self.patient_states = {}  # Clear current states
                self.load_patient_data()  # Reload from Excel
                
                # Find and load the newly added patient
                for i, patient in enumerate(self.patients_data):
                    if patient['patient_number'] == patient_data['patient_number']:
                        self.load_patient(i)
                        break
                
                success_msg = QMessageBox(self)
                success_msg.setWindowTitle("Erfolg")
                success_msg.setText(f"Patient {patient_data['name']} wurde erfolgreich hinzugefügt.")
                success_msg.setIcon(QMessageBox.Icon.Information)
                success_msg.setStandardButtons(QMessageBox.StandardButton.Ok)
                success_msg.setStyleSheet("""
                    QMessageBox {
                        background-color: #1a2633;
                        color: white;
                    }
                    QMessageBox QLabel {
                        color: white;
                        font-size: 14px;
                    }
                    QPushButton {
                        background-color: #114473;
                        color: white;
                        border: none;
                        border-radius: 4px;
                        padding: 8px 16px;
                        font-weight: bold;
                        min-width: 80px;
                    }
                    QPushButton:hover {
                        background-color: #1a5a9e;
                    }
                """)
                success_msg.exec()
                
                logging.info(f"Successfully added new patient: {patient_data['name']}")
                
            except Exception as e:
                logging.error(f"Error adding patient to Excel: {e}")
                error_msg = QMessageBox(self)
                error_msg.setWindowTitle("Fehler")
                error_msg.setText(f"Fehler beim Hinzufügen des Patienten zur Excel-Datei: {e}")
                error_msg.setIcon(QMessageBox.Icon.Critical)
                error_msg.setStandardButtons(QMessageBox.StandardButton.Ok)
                error_msg.setStyleSheet("""
                    QMessageBox {
                        background-color: #1a2633;
                        color: white;
                    }
                    QMessageBox QLabel {
                        color: white;
                        font-size: 14px;
                    }
                    QPushButton {
                        background-color: #114473;
                        color: white;
                        border: none;
                        border-radius: 4px;
                        padding: 8px 16px;
                        font-weight: bold;
                        min-width: 80px;
                    }
                    QPushButton:hover {
                        background-color: #1a5a9e;
                    }
                """)
                error_msg.exec()

    def add_patient_to_excel(self, patient_data):
        """Add a new patient to the Excel file in the first available empty row"""
        # Use temporary Excel file during session
        excel_path = self.temp_excel_path if self.temp_excel_path and self.temp_excel_path.exists() else self.source_excel_path
        
        try:
            # Read current Excel file
            df = pd.read_excel(excel_path, engine='openpyxl')
            
            # Find the correct ICD column name (check multiple possibilities)
            icd_column = None
            possible_icd_columns = ['ICD-10', 'ICD-Code', 'ICD Code', 'ICD10']
            for col in possible_icd_columns:
                if col in df.columns:
                    icd_column = col
                    break
            
            # If no ICD column found, use the first one as default
            if icd_column is None:
                icd_column = 'ICD-10'
                logging.warning(f"No ICD column found, using default: {icd_column}")
            
            # Define the columns to check for empty rows (B-K equivalent)
            columns_to_check = ['Name', 'Geburtsdatum', 'Diagnose', icd_column, 'Patientennummer', 
                               'Radiotherapie indiziert', 'Art des Aufgebots', 'Teams Priorisierung', 'Vormerken für Studie', 'Bemerkung/Procedere']
            
            # Find the first empty row by checking if all relevant columns are empty/NaN
            insert_row_index = None
            for index, row in df.iterrows():
                is_empty_row = True
                for col in columns_to_check:
                    if col in df.columns:
                        cell_value = row[col]
                        # Check if cell is not empty (not NaN, not empty string, not just whitespace)
                        if pd.notna(cell_value) and str(cell_value).strip() != '':
                            is_empty_row = False
                            break
                
                if is_empty_row:
                    insert_row_index = index
                    break
            
            # If no empty row found, append at the end
            if insert_row_index is None:
                insert_row_index = len(df)
                logging.info(f"No empty row found, appending new patient at row {insert_row_index}")
            else:
                logging.info(f"Found empty row at index {insert_row_index}, inserting new patient there")
            
            # Prepare new patient data using correct column names
            new_patient_data = {
                'Name': patient_data['name'],
                'Geburtsdatum': patient_data['birth_date'],
                'Diagnose': patient_data['diagnosis'],
                icd_column: patient_data['icd_code'],
                'Patientennummer': patient_data['patient_number'],
                'Radiotherapie indiziert': '',
                'Art des Aufgebots': '',
                'Teams Priorisierung': '',
                'Vormerken für Studie': '',
                'Bemerkung/Procedere': ''
            }
            
            # If inserting at the end, add a new row
            if insert_row_index >= len(df):
                # Create a new row and append
                new_row_df = pd.DataFrame([new_patient_data])
                df = pd.concat([df, new_row_df], ignore_index=True)
            else:
                # Insert into existing empty row
                for col_name, value in new_patient_data.items():
                    if col_name in df.columns:
                        df.at[insert_row_index, col_name] = value
            
            # Update the patient's index to the correct row
            patient_data['index'] = insert_row_index
            
            # Save back to Excel
            df.to_excel(excel_path, index=False, engine='openpyxl')
            
            logging.info(f"Successfully added patient {patient_data['name']} to Excel file at row {insert_row_index}")
            
        except Exception as e:
            logging.error(f"Error adding patient to Excel: {e}")
            raise e

    def get_changed_patients_for_finalization(self):
        """Get a list of patient numbers that have changed since the last finalization"""
        excel_path = self.tumorboard_base_path / self.tumorboard_name / self.date_str / f"{self.date_str}.xlsx"
        
        try:
            df = pd.read_excel(excel_path, engine='openpyxl')
            changed_patients = []
            
            # Compare current patient data with what's in Excel
            for patient in self.patients_data:
                row_index = patient['index']
                
                # Get current Excel values
                current_radio = str(df.at[row_index, 'Radiotherapie indiziert']) if 'Radiotherapie indiziert' in df.columns else ''
                current_aufgebot = str(df.at[row_index, 'Art des Aufgebots']) if 'Art des Aufgebots' in df.columns else ''
                current_teams = str(df.at[row_index, 'Teams Priorisierung']) if 'Teams Priorisierung' in df.columns else ''
                current_studie = str(df.at[row_index, 'Vormerken für Studie']) if 'Vormerken für Studie' in df.columns else ''
                current_bemerkung = str(df.at[row_index, 'Bemerkung/Procedere']) if 'Bemerkung/Procedere' in df.columns else ''
                
                # Clean current values (handle NaN)
                if current_radio == 'nan' or pd.isna(current_radio):
                    current_radio = ''
                if current_aufgebot == 'nan' or pd.isna(current_aufgebot):
                    current_aufgebot = ''
                if current_teams == 'nan' or pd.isna(current_teams):
                    current_teams = ''
                if current_studie == 'nan' or pd.isna(current_studie):
                    current_studie = ''
                if current_bemerkung == 'nan' or pd.isna(current_bemerkung):
                    current_bemerkung = ''
                
                # Get patient teams data (default to empty string if not present)
                patient_teams = patient.get('teams', '')
                
                # Check if any field changed
                if (patient['radiotherapy'] != current_radio or 
                    patient['aufgebot'] != current_aufgebot or 
                    patient_teams != current_teams or
                    patient['studie'] != current_studie or
                    patient['bemerkung'] != current_bemerkung):
                    changed_patients.append(patient['patient_number'])
            
            return changed_patients
            
        except Exception as e:
            logging.error(f"Error getting changed patients for finalization: {e}")
            return []

    def is_patient_skipped(self, patient):
        """Check if a patient is marked as skipped (all four data fields are "-")"""
        return (patient['radiotherapy'] == "-" and 
                patient['aufgebot'] == "-" and 
                patient['studie'] == "-" and
                patient['bemerkung'] == "-")

    def ensure_temp_file_exists(self):
        """Ensure temporary file exists for editing, create if necessary"""
        try:
            # If temp file doesn't exist, create it
            if not self.temp_excel_path or not self.temp_excel_path.exists():
                # Create temporary file name
                temp_filename = f"{self.date_str}_temp_session.xlsx"
                self.temp_excel_path = self.source_excel_path.parent / temp_filename
                
                # Create new temp file from source
                if self.create_temp_excel_file():
                    logging.info(f"Created new temporary file for editing: {self.temp_excel_path}")
                    return True
                else:
                    logging.error("Failed to create temporary file for editing")
                    return False
            else:
                logging.info(f"Temporary file already exists: {self.temp_excel_path}")
                return True
                
        except Exception as e:
            logging.error(f"Error ensuring temp file exists: {e}")
            return False

    def open_icd_editor(self):
        """Open the ICD code editor dialog"""
        print("DEBUG: open_icd_editor called")
        
        if not self.patients_data or self.current_patient_index >= len(self.patients_data):
            print("DEBUG: No patient selected, showing warning")
            QMessageBox.warning(self, "Kein Patient", "Bitte wählen Sie zuerst einen Patienten aus.")
            return
        
        current_patient = self.patients_data[self.current_patient_index]
        current_icd_code = current_patient.get('icd_code', '-')
        print(f"DEBUG: Current patient: {current_patient['name']}, ICD: {current_icd_code}")
        
        # Open the ICD editor dialog
        print("DEBUG: Creating ICDEditorDialog...")
        try:
            dialog = ICDEditorDialog(current_icd_code, self)
            print("DEBUG: ICDEditorDialog created successfully")
            
            print("DEBUG: Executing dialog...")
            result = dialog.exec()
            print(f"DEBUG: Dialog execution completed with result: {result}")
            
            if result == QDialog.DialogCode.Accepted:
                print("DEBUG: Dialog accepted, getting selected ICD...")
                # Get the selected ICD code and description
                new_icd_code, new_description = dialog.get_selected_icd()
                print(f"DEBUG: Selected ICD: {new_icd_code}, Description: {new_description}")
                
                if new_icd_code and new_icd_code != current_icd_code:
                    print("DEBUG: ICD code changed, updating patient data...")
                    # Update patient data
                    current_patient['icd_code'] = new_icd_code
                    
                    # Update the ICD display in the patient info section
                    if new_description:
                        self.icd_code_data_label.setText(f"<b>ICD:</b> {new_icd_code} ({new_description})")
                    else:
                        self.icd_code_data_label.setText(f"<b>ICD:</b> {new_icd_code}")
                    
                    # Mark as having unsaved changes
                    self.mark_unsaved_changes()
                    
                    # Save the change to the temporary Excel file
                    try:
                        self.save_icd_change_to_excel(current_patient['index'], new_icd_code)
                        logging.info(f"Updated ICD code for patient {current_patient['name']} to {new_icd_code}")
                        print(f"DEBUG: ICD change saved successfully")
                    except Exception as e:
                        print(f"ERROR: Error saving ICD change to Excel: {e}")
                        logging.error(f"Error saving ICD change to Excel: {e}")
                        QMessageBox.warning(self, "Speicherfehler", 
                                          f"Fehler beim Speichern der ICD-Änderung: {e}")
                else:
                    print("DEBUG: No ICD code change detected")
            else:
                print("DEBUG: Dialog was cancelled or rejected")
        except Exception as e:
            print(f"ERROR: Exception in open_icd_editor: {e}")
            import traceback
            print(f"ERROR: Traceback: {traceback.format_exc()}")

    def save_icd_change_to_excel(self, patient_row_index, new_icd_code):
        """Save ICD code change to the temporary Excel file"""
        # Ensure temp file exists for editing
        if not self.ensure_temp_file_exists():
            raise Exception("Temporäre Datei konnte nicht erstellt werden")
        
        # Use temporary Excel file
        excel_path = self.temp_excel_path
        
        try:
            # Read current Excel file
            df = pd.read_excel(excel_path, engine='openpyxl')
            
            # Find the correct ICD column name (check multiple possibilities)
            icd_column = None
            possible_icd_columns = ['ICD-10', 'ICD-Code', 'ICD Code', 'ICD10']
            for col in possible_icd_columns:
                if col in df.columns:
                    icd_column = col
                    break
            
            # If no ICD column found, use 'ICD-10' as default
            if icd_column is None:
                icd_column = 'ICD-10'
                logging.warning(f"No ICD column found, using default: {icd_column}")
            
            # Update the ICD code in the specified row
            df.at[patient_row_index, icd_column] = new_icd_code
            
            # Save back to Excel
            df.to_excel(excel_path, index=False, engine='openpyxl')
            
            logging.info(f"Successfully updated ICD code in Excel file at row {patient_row_index}")
            
        except Exception as e:
            logging.error(f"Error saving ICD change to Excel: {e}")
            raise e

    @staticmethod
    def get_icd_description(icd_code):
        """Get German description for ICD-10 code"""
        if not icd_code or str(icd_code).strip() in ['-', '', 'nan']:
            return '-'
        
        icd_code = str(icd_code).strip().upper()
        
        # Dictionary of common oncological ICD-10 codes and their German descriptions
        icd_descriptions = {
            # Maligne Neubildungen des Kopfes und Halses
            'C00': 'Bösartige Neubildung der Lippe',
            'C01': 'Bösartige Neubildung des Zungengrundes',
            'C02': 'Bösartige Neubildung sonstiger und nicht näher bezeichneter Teile der Zunge',
            'C03': 'Bösartige Neubildung des Zahnfleisches',
            'C04': 'Bösartige Neubildung des Mundbodens',
            'C05': 'Bösartige Neubildung des Gaumens',
            'C06': 'Bösartige Neubildung sonstiger und nicht näher bezeichneter Teile des Mundes',
            'C07': 'Bösartige Neubildung der Parotis',
            'C08': 'Bösartige Neubildung sonstiger und nicht näher bezeichneter großer Speicheldrüsen',
            'C09': 'Bösartige Neubildung der Tonsille',
            'C10': 'Bösartige Neubildung des Oropharynx',
            'C11': 'Bösartige Neubildung des Nasopharynx',
            'C12': 'Bösartige Neubildung des Sinus piriformis',
            'C13': 'Bösartige Neubildung des Hypopharynx',
            'C14': 'Bösartige Neubildung sonstiger und schlecht bezeichneter Lokalisationen der Lippe, Mundhöhle und des Pharynx',
            'C15': 'Bösartige Neubildung des Ösophagus',
            'C16': 'Bösartige Neubildung des Magens',
            'C17': 'Bösartige Neubildung des Dünndarms',
            'C18': 'Bösartige Neubildung des Kolons',
            'C19': 'Bösartige Neubildung am Rektosigmoid-Übergang',
            'C20': 'Bösartige Neubildung des Rektums',
            'C21': 'Bösartige Neubildung des Anus und des Analkanals',
            'C22': 'Bösartige Neubildung der Leber und der intrahepatischen Gallengänge',
            'C23': 'Bösartige Neubildung der Gallenblase',
            'C24': 'Bösartige Neubildung sonstiger und nicht näher bezeichneter Teile der Gallenwege',
            'C25': 'Bösartige Neubildung des Pankreas',
            'C26': 'Bösartige Neubildung sonstiger und schlecht bezeichneter Verdauungsorgane',
            'C30': 'Bösartige Neubildung der Nasenhöhle und des Mittelohrs',
            'C31': 'Bösartige Neubildung der Nasennebenhöhlen',
            'C32': 'Bösartige Neubildung des Larynx',
            'C33': 'Bösartige Neubildung der Trachea',
            'C34': 'Bösartige Neubildung der Bronchien und der Lunge',
            'C37': 'Bösartige Neubildung des Thymus',
            'C38': 'Bösartige Neubildung des Herzens, Mediastinums und der Pleura',
            'C39': 'Bösartige Neubildung sonstiger und schlecht bezeichneter Lokalisationen des Atmungssystems',
            'C40': 'Bösartige Neubildung des Knochens und des Gelenkknorpels der Extremitäten',
            'C41': 'Bösartige Neubildung des Knochens und des Gelenkknorpels sonstiger und nicht näher bezeichneter Lokalisationen',
            'C43': 'Bösartiges Melanom der Haut',
            'C44': 'Sonstige bösartige Neubildungen der Haut',
            'C45': 'Mesotheliom',
            'C46': 'Kaposi-Sarkom',
            'C47': 'Bösartige Neubildung der peripheren Nerven und des autonomen Nervensystems',
            'C48': 'Bösartige Neubildung des Retroperitoneums und des Peritoneums',
            'C49': 'Bösartige Neubildung sonstigen Bindegewebes und anderer Weichteilgewebe',
            'C50': 'Bösartige Neubildung der Brustdrüse [Mamma]',
            'C53': 'Bösartige Neubildung der Cervix uteri',
            'C54': 'Bösartige Neubildung des Corpus uteri',
            'C55': 'Bösartige Neubildung des Uterus, Teil nicht näher bezeichnet',
            'C56': 'Bösartige Neubildung des Ovars',
            'C57': 'Bösartige Neubildung sonstiger und nicht näher bezeichneter weiblicher Genitalorgane',
            'C58': 'Bösartige Neubildung der Plazenta',
            'C60': 'Bösartige Neubildung des Penis',
            'C61': 'Bösartige Neubildung der Prostata',
            'C62': 'Bösartige Neubildung des Hodens',
            'C63': 'Bösartige Neubildung sonstiger und nicht näher bezeichneter männlicher Genitalorgane',
            'C64': 'Bösartige Neubildung der Niere, ausgenommen Nierenbecken',
            'C65': 'Bösartige Neubildung des Nierenbeckens',
            'C66': 'Bösartige Neubildung des Ureters',
            'C67': 'Bösartige Neubildung der Harnblase',
            'C68': 'Bösartige Neubildung sonstiger und nicht näher bezeichneter Harnorgane',
            'C69': 'Bösartige Neubildung des Auges und der Augenanhangsgebilde',
            'C70': 'Bösartige Neubildung der Meningen',
            'C71': 'Bösartige Neubildung des Gehirns',
            'C72': 'Bösartige Neubildung des Rückenmarks, der Hirnnerven und anderer Teile des Zentralnervensystems',
            'C73': 'Bösartige Neubildung der Schilddrüse',
            'C74': 'Bösartige Neubildung der Nebenniere',
            'C75': 'Bösartige Neubildung sonstiger endokriner Drüsen und verwandter Strukturen',
            'C76': 'Bösartige Neubildung sonstiger und schlecht bezeichneter Lokalisationen',
            'C77': 'Sekundäre und nicht näher bezeichnete bösartige Neubildung der Lymphknoten',
            'C78': 'Sekundäre bösartige Neubildung der Atmungs- und Verdauungsorgane',
            'C79': 'Sekundäre bösartige Neubildung an sonstigen und nicht näher bezeichneten Lokalisationen',
            'C80': 'Bösartige Neubildung ohne Angabe der Lokalisation',
            'C81': 'Hodgkin-Lymphom',
            'C82': 'Follikuläres Lymphom',
            'C83': 'Nicht-follikuläres Lymphom',
            'C84': 'Reifzellige T/NK-Zell-Lymphome',
            'C85': 'Sonstige und nicht näher bezeichnete Typen des Non-Hodgkin-Lymphoms',
            'C86': 'Sonstige spezifizierte T/NK-Zell-Lymphome',
            'C88': 'Bösartige immunproliferative Krankheiten',
            'C90': 'Plasmozytom und bösartige Plasmazellneubildungen',
            'C91': 'Lymphatische Leukämie',
            'C92': 'Myeloische Leukämie',
            'C93': 'Monozytenleukämie',
            'C94': 'Sonstige Leukämien näher bezeichneten Zelltyps',
            'C95': 'Leukämie nicht näher bezeichneten Zelltyps',
            'C96': 'Sonstige und nicht näher bezeichnete bösartige Neubildungen des lymphatischen, blutbildenden und verwandten Gewebes',
            'C97': 'Bösartige Neubildungen als Primärtumoren an mehreren Lokalisationen',
            # Benigne Neubildungen
            'D10': 'Gutartige Neubildung des Mundes und des Pharynx',
            'D11': 'Gutartige Neubildung der großen Speicheldrüsen',
            'D12': 'Gutartige Neubildung des Kolons, Rektums, Anus und Analkanals',
            'D13': 'Gutartige Neubildung sonstiger und schlecht definierter Teile des Verdauungssystems',
            'D14': 'Gutartige Neubildung des Mittelohrs und des Atmungssystems',
            'D15': 'Gutartige Neubildung sonstiger und nicht näher bezeichneter intrathorakaler Organe',
            'D16': 'Gutartige Neubildung des Knochens und des Gelenkknorpels',
            'D17': 'Gutartige Lipomatöse Neubildung',
            'D18': 'Hämangiom und Lymphangiom jeder Lokalisation',
            'D19': 'Gutartige Neubildung des Mesothel-Gewebes',
            'D20': 'Gutartige Neubildung des Weichteilgewebes des Retroperitoneums und des Peritoneums',
            'D21': 'Sonstige gutartige Neubildungen des Bindegewebes und anderer Weichteilgewebe',
            'D22': 'Melanozytärer Nävus',
            'D23': 'Sonstige gutartige Neubildungen der Haut',
            'D24': 'Gutartige Neubildung der Brustdrüse [Mamma]',
            'D25': 'Leiomyom des Uterus',
            'D26': 'Sonstige gutartige Neubildungen des Uterus',
            'D27': 'Gutartige Neubildung des Ovars',
            'D28': 'Gutartige Neubildung sonstiger und nicht näher bezeichneter weiblicher Genitalorgane',
            'D29': 'Gutartige Neubildung der männlichen Genitalorgane',
            'D30': 'Gutartige Neubildung der Harnorgane',
            'D31': 'Gutartige Neubildung des Auges und der Augenanhangsgebilde',
            'D32': 'Gutartige Neubildung der Meningen',
            'D33': 'Gutartige Neubildung des Gehirns und anderer Teile des Zentralnervensystems',
            'D34': 'Gutartige Neubildung der Schilddrüse',
            'D35': 'Gutartige Neubildung sonstiger und nicht näher bezeichneter endokriner Drüsen',
            'D36': 'Gutartige Neubildung an sonstigen und nicht näher bezeichneten Lokalisationen',
            'D37': 'Neubildung unsicheren oder unbekannten Verhaltens der Mundhöhle und der Verdauungsorgane',
            'D38': 'Neubildung unsicheren oder unbekannten Verhaltens des Mittelohrs und der Atmungs- und intrathorakalen Organe',
            'D39': 'Neubildung unsicheren oder unbekannten Verhaltens der weiblichen Genitalorgane',
            'D40': 'Neubildung unsicheren oder unbekannten Verhaltens der männlichen Genitalorgane',
            'D41': 'Neubildung unsicheren oder unbekannten Verhaltens der Harnorgane',
            'D42': 'Neubildung unsicheren oder unbekannten Verhaltens der Meningen',
            'D43': 'Neubildung unsicheren oder unbekannten Verhaltens des Gehirns und des Zentralnervensystems',
            'D44': 'Neubildung unsicheren oder unbekannten Verhaltens der endokrinen Drüsen',
            'D45': 'Polycythaemia vera',
            'D46': 'Myelodysplastische Syndrome',
            'D47': 'Sonstige Neubildungen unsicheren oder unbekannten Verhaltens des lymphatischen, blutbildenden und verwandten Gewebes',
            'D48': 'Neubildung unsicheren oder unbekannten Verhaltens an sonstigen und nicht näher bezeichneten Lokalisationen'
        }
        
        # Try exact match first
        if icd_code in icd_descriptions:
            return icd_descriptions[icd_code]
        
        # Try to match first 3 characters (main category)
        main_code = icd_code[:3]
        if main_code in icd_descriptions:
            return icd_descriptions[main_code]
        
        # If no match found, return the code itself
        return f"ICD-Code: {icd_code}"

    @staticmethod
    def normalize_aufgebot_type(value):
        """Normalize aufgebot type to categorical values for database consistency"""
        if not value or str(value).strip() in ['-', '', 'nan']:
            return None
        
        value_str = str(value).strip()
        
        # Map long descriptions to short categories
        if "Kat I:" in value_str or "1-3 Tagen" in value_str:
            return "Kat I"
        elif "Kat II:" in value_str or "5-7 Tagen" in value_str:
            return "Kat II"
        elif "Kat III:" in value_str or "Nach Eingang des Konsils" in value_str:
            return "Kat III"
        elif value_str in ["Kat I", "Kat II", "Kat III"]:
            return value_str
        else:
            return value_str  # Return as-is for unknown values

# ICD Database Helper Functions
def load_icd_database():
    """Load ICD database from JSON file"""
    print("DEBUG: Starting to load ICD database...")
    try:
        # Get the path to the JSON file in utils folder
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
        json_path = os.path.join(parent_dir, 'utils', 'icd_database.json')
        
        print(f"DEBUG: Looking for JSON file at: {json_path}")
        print(f"DEBUG: JSON file exists: {os.path.exists(json_path)}")
        
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            print(f"DEBUG: Successfully loaded ICD database with {len(data)} entries")
            return data
    except Exception as e:
        print(f"ERROR: Failed to load ICD database: {e}")
        logging.error(f"Error loading ICD database: {e}")
        return {}

def search_by_code(search_term):
    """Search ICD codes by code pattern (prefix matching)"""
    print(f"DEBUG: search_by_code called with term: '{search_term}'")
    try:
        icd_database = load_icd_database()
        if not icd_database:
            print("ERROR: ICD database is empty or failed to load")
            logging.warning("ICD database is empty or failed to load")
            return []
            
        search_term = search_term.upper().strip()
        print(f"DEBUG: Normalized search term: '{search_term}'")
        results = []
        
        for code, description in icd_database.items():
            if search_term in code:  # Contains search (not just prefix)
                results.append((code, description))
        
        print(f"DEBUG: Found {len(results)} results before sorting/limiting")
        final_results = sorted(results)[:50]  # Limit to 50 results
        print(f"DEBUG: Returning {len(final_results)} results")
        return final_results
    except Exception as e:
        print(f"ERROR: Exception in search_by_code: {e}")
        import traceback
        print(f"ERROR: Traceback: {traceback.format_exc()}")
        logging.error(f"Error in search_by_code: {e}")
        return []

def search_by_description(search_term):
    """Search ICD codes by description (case-insensitive substring matching)"""
    try:
        icd_database = load_icd_database()
        if not icd_database:
            logging.warning("ICD database is empty or failed to load")
            return []
            
        search_term = search_term.lower().strip()
        results = []
        
        for code, description in icd_database.items():
            if search_term in description.lower():
                results.append((code, description))
        
        return sorted(results)[:50]  # Limit to 50 results
    except Exception as e:
        logging.error(f"Error in search_by_description: {e}")
        return []

def get_icd_description_from_database(icd_code):
    """Get German description for ICD-10 code from JSON database"""
    try:
        if not icd_code or str(icd_code).strip() in ['-', '', 'nan']:
            return '-'
        
        icd_database = load_icd_database()
        if not icd_database:
            logging.warning("ICD database is empty or failed to load")
            return f"ICD-Code: {icd_code}"
            
        icd_code = str(icd_code).strip().upper()
        
        # Try exact match first
        if icd_code in icd_database:
            return icd_database[icd_code]
        
        # Try to match first 3 characters (main category)
        main_code = icd_code[:3]
        if main_code in icd_database:
            return icd_database[main_code]
        
        # If no match found, return the code itself
        return f"ICD-Code: {icd_code}"
    except Exception as e:
        logging.error(f"Error in get_icd_description_from_database: {e}")
        return f"ICD-Code: {icd_code}"


class ICDEditorDialog(QDialog):
    """Dialog for searching and editing ICD codes"""
    
    def __init__(self, current_icd_code="", parent=None):
        print(f"DEBUG: ICDEditorDialog.__init__ called with ICD: '{current_icd_code}'")
        try:
            super().__init__(parent)
            print("DEBUG: Dialog parent class initialized")
            
            self.setWindowTitle("ICD-Code bearbeiten")
            self.setModal(True)
            self.setFixedSize(800, 600)
            print("DEBUG: Dialog window properties set")
            
            self.current_icd_code = current_icd_code
            self.selected_icd_code = current_icd_code
            self.selected_description = ""
            print("DEBUG: Dialog instance variables initialized")
            
            # Get current description
            if current_icd_code and current_icd_code != '-':
                print("DEBUG: Getting description for current ICD code...")
                self.selected_description = get_icd_description_from_database(current_icd_code)
                print(f"DEBUG: Got description: '{self.selected_description}'")
            
            print("DEBUG: Calling setup_ui...")
            self.setup_ui()
            print("DEBUG: ICDEditorDialog initialization completed successfully")
        except Exception as e:
            print(f"ERROR: Exception in ICDEditorDialog.__init__: {e}")
            import traceback
            print(f"ERROR: Traceback: {traceback.format_exc()}")
            raise
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Top section: Current ICD display only
        top_section = QVBoxLayout()
        
        # Current ICD display
        current_label = QLabel("Aktueller ICD-Code:")
        current_label.setFont(QFont("Helvetica", 12, QFont.Weight.Bold))
        current_label.setStyleSheet("color: white;")
        top_section.addWidget(current_label)
        
        self.current_display = QLabel()
        self.update_current_display()
        self.current_display.setStyleSheet("""
            background-color: #2a3642;
            color: white;
            padding: 10px;
            border-radius: 4px;
            font-size: 14px;
        """)
        self.current_display.setWordWrap(True)
        self.current_display.setMinimumHeight(60)
        top_section.addWidget(self.current_display)
        
        layout.addLayout(top_section)
        
        # Search section
        search_section = QHBoxLayout()
        
        # Code search
        code_search_layout = QVBoxLayout()
        code_search_label = QLabel("Nach ICD-Code suchen:")
        code_search_label.setFont(QFont("Helvetica", 11, QFont.Weight.Bold))
        code_search_label.setStyleSheet("color: white;")
        code_search_layout.addWidget(code_search_label)
        
        self.code_search_input = QLineEdit()
        self.code_search_input.setPlaceholderText("z.B. C34 oder C34.9")
        self.code_search_input.setStyleSheet("""
            QLineEdit {
                background-color: #2a3642;
                color: white;
                border: 1px solid #425061;
                border-radius: 4px;
                padding: 8px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #3292ea;
            }
        """)
        # Prevent Enter from being passed to dialog and ensure it only triggers search
        self.code_search_input.returnPressed.connect(self.search_by_code)
        code_search_layout.addWidget(self.code_search_input)
        
        search_section.addLayout(code_search_layout)
        
        # Description search
        desc_search_layout = QVBoxLayout()
        desc_search_label = QLabel("Nach Beschreibung suchen:")
        desc_search_label.setFont(QFont("Helvetica", 11, QFont.Weight.Bold))
        desc_search_label.setStyleSheet("color: white;")
        desc_search_layout.addWidget(desc_search_label)
        
        self.desc_search_input = QLineEdit()
        self.desc_search_input.setPlaceholderText("z.B. Lunge oder Neubildung")
        self.desc_search_input.setStyleSheet("""
            QLineEdit {
                background-color: #2a3642;
                color: white;
                border: 1px solid #425061;
                border-radius: 4px;
                padding: 8px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #3292ea;
            }
        """)
        # Prevent Enter from being passed to dialog and ensure it only triggers search
        self.desc_search_input.returnPressed.connect(self.search_by_description)
        desc_search_layout.addWidget(self.desc_search_input)
        
        search_section.addLayout(desc_search_layout)
        
        layout.addLayout(search_section)
        
        # Results section
        results_label = QLabel("Suchergebnisse:")
        results_label.setFont(QFont("Helvetica", 11, QFont.Weight.Bold))
        results_label.setStyleSheet("color: white; margin-top: 10px;")
        layout.addWidget(results_label)
        
        # Scrollable results area
        self.results_scroll = QScrollArea()
        self.results_scroll.setWidgetResizable(True)
        self.results_scroll.setStyleSheet("""
            QScrollArea {
                background-color: #1a2633;
                border: 1px solid #425061;
                border-radius: 4px;
            }
            QScrollBar:vertical {
                width: 12px;
                background-color: #2a3642;
            }
            QScrollBar::handle:vertical {
                background-color: #425061;
                border-radius: 6px;
            }
        """)
        
        self.results_widget = QWidget()
        self.results_layout = QVBoxLayout(self.results_widget)
        self.results_layout.setContentsMargins(10, 10, 10, 10)
        self.results_layout.setSpacing(5)
        
        # Initial message
        self.show_initial_message()
        
        self.results_scroll.setWidget(self.results_widget)
        layout.addWidget(self.results_scroll)
        
        # Bottom button section
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        # Left stretch to center the buttons
        button_layout.addStretch()
        
        # Save button (center-left)
        self.save_button = QPushButton("Neue Auswahl speichern")
        self.save_button.setFixedHeight(40)
        self.save_button.setFixedWidth(180)
        self.save_button.setAutoDefault(False)  # Prevent default button behavior
        self.save_button.setDefault(False)  # Prevent default button behavior
        self.save_button.setStyleSheet("""
            QPushButton {
                background-color: #2E8B57;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #3CB371;
            }
            QPushButton:pressed {
                background-color: #228B22;
            }
        """)
        self.save_button.clicked.connect(self.save_selection)
        button_layout.addWidget(self.save_button)
        
        # Close button (center-right)
        close_button = QPushButton("Schließen")
        close_button.setFixedHeight(40)
        close_button.setFixedWidth(120)
        close_button.setAutoDefault(False)  # Prevent default button behavior
        close_button.setDefault(False)  # Prevent default button behavior
        close_button.setStyleSheet("""
            QPushButton {
                background-color: #666666;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #777777;
            }
        """)
        close_button.clicked.connect(self.reject)
        button_layout.addWidget(close_button)
        
        # Right stretch to center the buttons
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        # Apply dark theme
        self.setStyleSheet("""
            QDialog {
                background-color: #1a2633;
                color: white;
            }
        """)
    
    def update_current_display(self):
        """Update the current ICD code display"""
        if self.selected_icd_code and self.selected_icd_code != '-':
            if self.selected_description:
                display_text = f"{self.selected_icd_code} - {self.selected_description}"
            else:
                display_text = f"{self.selected_icd_code}"
        else:
            display_text = "Kein ICD-Code ausgewählt"
        
        self.current_display.setText(display_text)
    
    def show_initial_message(self):
        """Show initial message in results area"""
        print("DEBUG: show_initial_message called")
        
        # Clear existing results
        try:
            print("DEBUG: Clearing existing results for initial message...")
            for i in reversed(range(self.results_layout.count())):
                item = self.results_layout.itemAt(i)
                if item is not None:
                    widget = item.widget()
                    if widget is not None:
                        widget.setParent(None)
                    else:
                        # Handle spacer items
                        self.results_layout.removeItem(item)
            print("DEBUG: Layout cleared for initial message successfully")
        except Exception as e:
            print(f"ERROR: Error clearing initial message layout: {e}")
            logging.error(f"Error clearing initial message layout: {e}")
        
        try:
            print("DEBUG: Creating initial message label...")
            message_label = QLabel("Geben Sie mindestens 2 Zeichen in eines der Suchfelder ein und drücken Sie Enter.")
            message_label.setStyleSheet("color: #888888; font-style: italic; padding: 20px;")
            message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.results_layout.addWidget(message_label)
            self.results_layout.addStretch()
            print("DEBUG: Initial message label created and added successfully")
        except Exception as e:
            print(f"ERROR: Error creating initial message label: {e}")
            import traceback
            print(f"ERROR: Traceback: {traceback.format_exc()}")
    
    def search_by_code(self):
        """Search for ICD codes by code pattern"""
        print("DEBUG: Dialog search_by_code method called")
        try:
            search_term = self.code_search_input.text().strip()
            print(f"DEBUG: Search term from input field: '{search_term}'")
            
            if len(search_term) < 2:
                print("DEBUG: Search term too short, showing message")
                self.show_message("Bitte geben Sie mindestens 2 Zeichen ein.")
                return
            
            print("DEBUG: Calling global search_by_code function...")
            results = search_by_code(search_term)
            print(f"DEBUG: Got {len(results)} results from search function")
            
            print("DEBUG: Calling display_results...")
            self.display_results(results, f"Suchergebnisse für Code '{search_term}':")
            print("DEBUG: display_results completed successfully")
        except Exception as e:
            print(f"ERROR: Exception in dialog search_by_code: {e}")
            import traceback
            print(f"ERROR: Traceback: {traceback.format_exc()}")
            logging.error(f"Error during code search: {e}")
            self.show_message(f"Fehler bei der Code-Suche: {str(e)}")
    
    def search_by_description(self):
        """Search for ICD codes by description"""
        try:
            search_term = self.desc_search_input.text().strip()
            
            if len(search_term) < 2:
                self.show_message("Bitte geben Sie mindestens 2 Zeichen ein.")
                return
            
            results = search_by_description(search_term)
            self.display_results(results, f"Suchergebnisse für Beschreibung '{search_term}':")
        except Exception as e:
            logging.error(f"Error during description search: {e}")
            self.show_message(f"Fehler bei der Beschreibungssuche: {str(e)}")
    
    def display_results(self, results, title):
        """Display search results"""
        print(f"DEBUG: display_results called with {len(results)} results, title: '{title}'")
        
        # Clear existing results
        try:
            print("DEBUG: Clearing existing results layout...")
            for i in reversed(range(self.results_layout.count())):
                item = self.results_layout.itemAt(i)
                if item is not None:
                    widget = item.widget()
                    if widget is not None:
                        widget.setParent(None)
                    else:
                        # Handle spacer items
                        self.results_layout.removeItem(item)
            print("DEBUG: Layout cleared successfully")
        except Exception as e:
            print(f"ERROR: Error clearing results layout: {e}")
            logging.error(f"Error clearing results layout: {e}")
        
        if not results:
            print("DEBUG: No results, showing 'no results' message")
            self.show_message("Keine Treffer gefunden.")
            return
        
        print("DEBUG: Creating title label...")
        # Title
        try:
            title_label = QLabel(title)
            title_label.setFont(QFont("Helvetica", 10, QFont.Weight.Bold))
            title_label.setStyleSheet("color: #4FC3F7; margin-bottom: 10px;")
            self.results_layout.addWidget(title_label)
            print("DEBUG: Title label added successfully")
        except Exception as e:
            print(f"ERROR: Error creating title label: {e}")
            return
        
        # Results
        print(f"DEBUG: Creating {len(results)} result buttons...")
        try:
            for i, (code, description) in enumerate(results):
                print(f"DEBUG: Creating button {i+1}/{len(results)}: {code}")
                result_button = QPushButton(f"{code} - {description}")
                result_button.setAutoDefault(False)  # Prevent default button behavior
                result_button.setStyleSheet("""
                    QPushButton {
                        background-color: #2a3642;
                        color: white;
                        border: 1px solid #425061;
                        border-radius: 4px;
                        padding: 8px;
                        text-align: left;
                        font-size: 13px;
                    }
                    QPushButton:hover {
                        background-color: #3a4652;
                        border-color: #3292ea;
                    }
                    QPushButton:pressed {
                        background-color: #1a2633;
                    }
                """)
                result_button.clicked.connect(lambda checked, c=code, d=description: self.select_result(c, d))
                self.results_layout.addWidget(result_button)
                print(f"DEBUG: Button {i+1} added successfully")
            print("DEBUG: All result buttons created successfully")
        except Exception as e:
            print(f"ERROR: Error creating result buttons: {e}")
            import traceback
            print(f"ERROR: Traceback: {traceback.format_exc()}")
            return
        
        if len(results) >= 50:
            print("DEBUG: Adding info label for 50+ results...")
            try:
                info_label = QLabel("Nur die ersten 50 Treffer werden angezeigt. Verfeinern Sie Ihre Suche für spezifischere Ergebnisse.")
                info_label.setStyleSheet("color: #FFA500; font-style: italic; margin-top: 10px; font-size: 12px;")
                info_label.setWordWrap(True)
                self.results_layout.addWidget(info_label)
                print("DEBUG: Info label added successfully")
            except Exception as e:
                print(f"ERROR: Error adding info label: {e}")
        
        print("DEBUG: Adding stretch to layout...")
        try:
            self.results_layout.addStretch()
            print("DEBUG: display_results completed successfully")
        except Exception as e:
            print(f"ERROR: Error adding stretch: {e}")
    
    def show_message(self, message):
        """Show a message in the results area"""
        print(f"DEBUG: show_message called with message: '{message}'")
        
        # Clear existing results
        try:
            print("DEBUG: Clearing existing results for message...")
            for i in reversed(range(self.results_layout.count())):
                item = self.results_layout.itemAt(i)
                if item is not None:
                    widget = item.widget()
                    if widget is not None:
                        widget.setParent(None)
                    else:
                        # Handle spacer items
                        self.results_layout.removeItem(item)
            print("DEBUG: Layout cleared for message successfully")
        except Exception as e:
            print(f"ERROR: Error clearing message layout: {e}")
            logging.error(f"Error clearing message layout: {e}")
        
        try:
            print("DEBUG: Creating message label...")
            message_label = QLabel(message)
            message_label.setStyleSheet("color: #FFA500; font-style: italic; padding: 20px;")
            message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.results_layout.addWidget(message_label)
            self.results_layout.addStretch()
            print("DEBUG: Message label created and added successfully")
        except Exception as e:
            print(f"ERROR: Error creating message label: {e}")
            import traceback
            print(f"ERROR: Traceback: {traceback.format_exc()}")
    
    def select_result(self, code, description):
        """Select a result from the search"""
        self.selected_icd_code = code
        self.selected_description = description
        self.update_current_display()
        
        # Clear search fields
        self.code_search_input.clear()
        self.desc_search_input.clear()
        
        # Show confirmation message
        self.show_message(f"ICD-Code {code} ausgewählt. Klicken Sie 'Neue Auswahl speichern' um zu übernehmen.")
    
    def save_selection(self):
        """Save the selected ICD code"""
        if self.selected_icd_code and self.selected_icd_code != '-':
            self.accept()
        else:
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Keine Auswahl")
            msg_box.setText("Bitte wählen Sie zuerst einen ICD-Code aus der Trefferliste aus.")
            msg_box.setStyleSheet("""
                QMessageBox {
                    background-color: #1a2633;
                    color: white;
                }
                QMessageBox QLabel {
                    color: white;
                }
                QPushButton {
                    background-color: #114473;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 8px 16px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #1a5a9e;
                }
            """)
            msg_box.exec()
    
    def get_selected_icd(self):
        """Get the selected ICD code and description"""
        return self.selected_icd_code, self.selected_description


class TeamsPriorityDialog(QDialog):
    """Dialog for teams priority selection"""
    def __init__(self, current_priorities=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Teams Priorisierung")
        self.setModal(True)
        self.setFixedSize(600, 400)  # Wider dialog for 3-column layout
        
        # Available team members
        self.team_members = [
            "Guckenberger", "Andratschke", "Balermpas", "Linsenmeier", 
            "Brown", "Motisi", "Vlaskou", "Kretschmer", "Guninski", "Heusel", "Christ", "Ahmadsei"
        ]
        
        # Initialize priority tracking
        self.selected_priorities = current_priorities.copy() if current_priorities else []
        self.checkboxes = {}
        
        self.setup_dialog()
        self.update_title()
        self.update_checkbox_styles()
        
    def setup_dialog(self):
        """Setup the dialog UI"""
        layout = QVBoxLayout()
        
        # Top section with reset button and title
        top_layout = QHBoxLayout()
        
        # Reset button (top left)
        reset_button = QPushButton("Zurücksetzen")
        reset_button.setStyleSheet("""
            QPushButton {
                background-color: #CC5500;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #DD6611;
            }
        """)
        reset_button.clicked.connect(self.reset_selection)
        
        top_layout.addWidget(reset_button)
        top_layout.addStretch()
        layout.addLayout(top_layout)
        
        # Title label
        self.title_label = QLabel()
        self.title_label.setFont(QFont("Helvetica", 14, QFont.Weight.Bold))
        self.title_label.setStyleSheet("color: #4FC3F7; margin-bottom: 15px;")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title_label)
        
        # Grid layout for checkboxes (3 columns × 4 rows)
        from PyQt6.QtWidgets import QGridLayout
        grid_widget = QWidget()
        grid_layout = QGridLayout(grid_widget)
        grid_layout.setSpacing(10)
        
        # Create checkboxes for each team member in grid layout
        for i, member in enumerate(self.team_members):
            row = i // 3  # Integer division for row
            col = i % 3   # Modulo for column
            
            checkbox = QCheckBox(member)
            checkbox.setStyleSheet("""
                QCheckBox {
                    color: white;
                    font-size: 14px;
                    padding: 8px;
                }
                QCheckBox::indicator {
                    width: 24px;
                    height: 24px;
                }
                QCheckBox::indicator:unchecked {
                    background-color: #1a2633;
                    border: 2px solid #555;
                    border-radius: 3px;
                }
                QCheckBox::indicator:checked {
                    background-color: #1E90FF;
                    border: 2px solid #1E90FF;
                    border-radius: 3px;
                    color: white;
                }
            """)
            
            # Check if this member is already in current priorities
            if member in self.selected_priorities:
                checkbox.setChecked(True)
            
            checkbox.stateChanged.connect(lambda state, m=member: self.on_checkbox_changed(m, state))
            self.checkboxes[member] = checkbox
            grid_layout.addWidget(checkbox, row, col)
        
        layout.addWidget(grid_widget)
        
        # Add some space before bottom buttons
        layout.addStretch()
        
        # Bottom buttons
        bottom_button_layout = QHBoxLayout()
        
        # OK button
        ok_button = QPushButton("OK")
        ok_button.setStyleSheet("""
            QPushButton {
                background-color: #1E90FF;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #4169E1;
            }
        """)
        ok_button.clicked.connect(self.accept)
        
        # Cancel button
        cancel_button = QPushButton("Abbrechen")
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #666666;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #777777;
            }
        """)
        cancel_button.clicked.connect(self.reject)
        
        bottom_button_layout.addWidget(ok_button)
        bottom_button_layout.addStretch()
        bottom_button_layout.addWidget(cancel_button)
        layout.addLayout(bottom_button_layout)
        
        self.setLayout(layout)
        
        # Apply dark theme
        self.setStyleSheet("""
            QDialog {
                background-color: #1a2633;
                color: white;
            }
        """)
    
    def on_checkbox_changed(self, member, state):
        """Handle checkbox state change"""
        if state == 2:  # Checked
            if len(self.selected_priorities) < 3 and member not in self.selected_priorities:
                self.selected_priorities.append(member)
        else:  # Unchecked
            if member in self.selected_priorities:
                self.selected_priorities.remove(member)
        
        # If more than 3 are selected, uncheck the last one
        if len(self.selected_priorities) > 3:
            # Find the member that was just added and remove it
            last_member = self.selected_priorities[-1]
            self.selected_priorities.remove(last_member)
            self.checkboxes[last_member].setChecked(False)
        
        self.update_title()
        self.update_checkbox_styles()
    
    def update_checkbox_styles(self):
        """Update checkbox styles to show priority numbers"""
        for member, checkbox in self.checkboxes.items():
            if member in self.selected_priorities:
                priority_num = self.selected_priorities.index(member) + 1
                # Create custom style with priority number
                checkbox.setStyleSheet(f"""
                    QCheckBox {{
                        color: white;
                        font-size: 14px;
                        padding: 8px;
                    }}
                    QCheckBox::indicator {{
                        width: 24px;
                        height: 24px;
                    }}
                    QCheckBox::indicator:unchecked {{
                        background-color: #1a2633;
                        border: 2px solid #555;
                        border-radius: 3px;
                    }}
                    QCheckBox::indicator:checked {{
                        background-color: #1E90FF;
                        border: 2px solid #1E90FF;
                        border-radius: 3px;
                        color: white;
                        image: none;
                    }}
                """)
                # Set text to show priority number
                checkbox.setText(f"{member} ({priority_num})")
            else:
                # Reset to normal style
                checkbox.setStyleSheet("""
                    QCheckBox {
                        color: white;
                        font-size: 14px;
                        padding: 8px;
                    }
                    QCheckBox::indicator {
                        width: 24px;
                        height: 24px;
                    }
                    QCheckBox::indicator:unchecked {
                        background-color: #1a2633;
                        border: 2px solid #555;
                        border-radius: 3px;
                    }
                    QCheckBox::indicator:checked {
                        background-color: #1E90FF;
                        border: 2px solid #1E90FF;
                        border-radius: 3px;
                        color: white;
                    }
                """)
                checkbox.setText(member)
    
    def update_title(self):
        """Update dialog title based on current selection"""
        count = len(self.selected_priorities)
        if count == 0:
            title = "Bitte 1. Priorität ankreuzen"
        elif count == 1:
            title = "Bitte 2. Priorität ankreuzen"
        elif count == 2:
            title = "Bitte 3. Priorität ankreuzen"
        else:
            title = "Prioritäten festgelegt"
        
        self.title_label.setText(title)
    
    def reset_selection(self):
        """Reset all selections"""
        self.selected_priorities.clear()
        for checkbox in self.checkboxes.values():
            checkbox.setChecked(False)
        self.update_title()
        self.update_checkbox_styles()
    
    def get_priorities(self):
        """Get the selected priorities in order"""
        return self.selected_priorities.copy()