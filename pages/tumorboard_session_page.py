from PyQt6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, 
                             QScrollArea, QFrame, QComboBox, QTextEdit, QMessageBox, QDialog, QDialogButtonBox, QLineEdit, QFormLayout)
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
        diagnosis_label = QLabel("Diagnose:")
        icd_code_label = QLabel("ICD-Code:")
        icd_code_optional = QLabel("(optional)")
        icd_code_optional.setStyleSheet(optional_style)
        
        name_label.setStyleSheet(label_style)
        birth_date_label.setStyleSheet(label_style)
        patient_number_label.setStyleSheet(label_style)
        diagnosis_label.setStyleSheet(label_style)
        icd_code_label.setStyleSheet(label_style)
        
        # Create containers for labels with optional text
        birth_date_container = QWidget()
        birth_date_layout = QVBoxLayout(birth_date_container)
        birth_date_layout.setContentsMargins(0, 0, 0, 0)
        birth_date_layout.setSpacing(0)
        birth_date_layout.addWidget(birth_date_label)
        birth_date_layout.addWidget(birth_date_optional)
        
        icd_code_container = QWidget()
        icd_code_layout = QVBoxLayout(icd_code_container)
        icd_code_layout.setContentsMargins(0, 0, 0, 0)
        icd_code_layout.setSpacing(0)
        icd_code_layout.addWidget(icd_code_label)
        icd_code_layout.addWidget(icd_code_optional)
        
        form_layout.addRow(name_label, self.vorname_edit)
        form_layout.addRow(birth_date_container, self.nachname_edit)
        form_layout.addRow(patient_number_label, self.patient_number_edit)
        form_layout.addRow(diagnosis_label, self.diagnosis_edit)
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
        diagnosis_label = QLabel("Diagnose:")
        icd_code_label = QLabel("ICD-Code:")
        icd_code_optional = QLabel("(optional)")
        icd_code_optional.setStyleSheet(optional_style)
        
        name_label.setStyleSheet(label_style)
        birth_date_label.setStyleSheet(label_style)
        patient_number_label.setStyleSheet(label_style)
        diagnosis_label.setStyleSheet(label_style)
        icd_code_label.setStyleSheet(label_style)
        
        # Create containers for labels with optional text
        birth_date_container = QWidget()
        birth_date_layout = QVBoxLayout(birth_date_container)
        birth_date_layout.setContentsMargins(0, 0, 0, 0)
        birth_date_layout.setSpacing(0)
        birth_date_layout.addWidget(birth_date_label)
        birth_date_layout.addWidget(birth_date_optional)
        
        icd_code_container = QWidget()
        icd_code_layout = QVBoxLayout(icd_code_container)
        icd_code_layout.setContentsMargins(0, 0, 0, 0)
        icd_code_layout.setSpacing(0)
        icd_code_layout.addWidget(icd_code_label)
        icd_code_layout.addWidget(icd_code_optional)
        
        form_layout.addRow(name_label, self.name_edit)
        form_layout.addRow(birth_date_container, self.birth_date_edit)
        form_layout.addRow(patient_number_label, self.patient_number_edit)
        form_layout.addRow(diagnosis_label, self.diagnosis_edit)
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
        
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.add_button)
        
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
    def __init__(self, main_window, tumorboard_name, date_str):
        super().__init__()
        logging.info(f"Initializing TumorboardSessionPage for: {tumorboard_name} on {date_str}")
        self.main_window = main_window
        self.tumorboard_name = tumorboard_name
        self.date_str = date_str
        
        # Store identifier for find_page_index
        self.entity_name = f"{tumorboard_name}_{date_str}_session"
        
        # Patient data
        self.patients_data = []
        self.current_patient_index = 0
        self.patient_states = {}  # Track patient completion states
        
        self.setup_ui()
        self.load_patient_data()
        logging.info(f"TumorboardSessionPage UI setup complete for {tumorboard_name} on {date_str}.")

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
            padding: 6px; 
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
                padding: 6px;
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
                border: 1px solid #2a3642;
                border-radius: 4px;
                padding: 6px;
                font-size: 14px;
            }
        """

    def setup_ui(self):
        # Main layout - horizontal with three sections
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
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
        patient_frame.setFixedWidth(230)  # Made slightly narrower
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
        self.add_patient_button.setFixedWidth(210)
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
        
        # Scrollable patient list
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)
        
        self.patient_list_widget = QWidget()
        self.patient_list_layout = QVBoxLayout(self.patient_list_widget)
        self.patient_list_layout.setContentsMargins(5, 5, 5, 5)
        self.patient_list_layout.setSpacing(5)
        
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
        data_layout.setContentsMargins(15, 15, 15, 15)
        data_layout.setSpacing(22)  # No automatic spacing
        
        # Header
        header_label = QLabel("Patientendaten")
        header_label.setFont(QFont("Helvetica", 14, QFont.Weight.Bold))
        header_label.setStyleSheet("color: #4FC3F7; border: none;")
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_label.setFixedHeight(25)
        data_layout.addWidget(header_label)
        
        # Patient info section with FIXED HEIGHT
        PATIENT_INFO_HEIGHT = 250  # <-- ÄNDERN: FIXE Höhe für Patient Info (beschränkt die Größe!)
        patient_info_container = QFrame()
        patient_info_container.setFixedHeight(PATIENT_INFO_HEIGHT)
        self.create_patient_info_section_fixed_height(patient_info_container)
        data_layout.addWidget(patient_info_container)
        
        # FIXED SPACER to ensure data entry always starts at same position
        SPACER_TO_DATA_ENTRY = 20  # <-- ÄNDERN: Abstand zwischen Patient Info und Data Entry
        data_layout.addSpacing(SPACER_TO_DATA_ENTRY)
        
        # Data entry section - now always starts at same position!
        DATA_ENTRY_HEIGHT = 358    # <-- ÄNDERN: Höhe der Data Entry Section
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
                border-radius: 6px;
                padding: 8px;
            }
        """)
        
        info_layout = QVBoxLayout(container)
        info_layout.setContentsMargins(8, 8, 8, 8)
        info_layout.setSpacing(1)
        
        # Patient info labels and data
        self.name_data_label = QLabel("Name: -")
        self.name_data_label.setStyleSheet("color: white; font-size: 14px; border: none;")
        self.name_data_label.setWordWrap(True)
        info_layout.addWidget(self.name_data_label)
        
        self.birth_date_data_label = QLabel("Geburtsdatum: -")
        self.birth_date_data_label.setStyleSheet("color: white; font-size: 14px; border: none;")
        info_layout.addWidget(self.birth_date_data_label)
        
        self.age_data_label = QLabel("Alter: -")
        self.age_data_label.setStyleSheet("color: white; font-size: 14px; border: none;")
        info_layout.addWidget(self.age_data_label)
        
        diagnosis_title_label = QLabel("Diagnose:")
        diagnosis_title_label.setStyleSheet("color: white; font-size: 14px; font-weight: bold; border: none; margin-bottom: 0px; margin-top: 2px;")
        info_layout.addWidget(diagnosis_title_label)
        
        self.diagnosis_data_label = QLabel("-")
        self.diagnosis_data_label.setStyleSheet("color: white; font-size: 14px; border: none; margin-top: -2px; margin-bottom: 0px;")
        self.diagnosis_data_label.setWordWrap(True)
        info_layout.addWidget(self.diagnosis_data_label)
        
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
        entry_layout.setContentsMargins(12, 12, 12, 12)
        entry_layout.setSpacing(12)
        
        # Radiotherapie indiziert
        self.radio_label = QLabel("Radiotherapie indiziert:")
        self.radio_label.setStyleSheet(self.get_label_style(False))
        entry_layout.addWidget(self.radio_label)
        
        self.radiotherapy_combo = NoScrollComboBox()
        self.radiotherapy_combo.addItems(["-", "Ja", "Nein"])
        self.radiotherapy_combo.setStyleSheet(self.get_input_style())
        self.radiotherapy_combo.currentTextChanged.connect(self.on_radiotherapy_changed)
        entry_layout.addWidget(self.radiotherapy_combo)
        
        # Art des Aufgebots (conditional)
        self.aufgebot_label = QLabel("Art des Aufgebots:")
        self.aufgebot_label.setStyleSheet(self.get_label_style(False))
        self.aufgebot_label.setVisible(False)
        entry_layout.addWidget(self.aufgebot_label)
        
        self.aufgebot_combo = NoScrollComboBox()
        self.aufgebot_combo.addItems(["-", "Zeitnah direkt durch uns", "Nach Konsil-Eingang"])
        self.aufgebot_combo.setStyleSheet(self.get_input_style())
        self.aufgebot_combo.currentTextChanged.connect(self.update_label_styles)
        self.aufgebot_combo.setVisible(False)
        entry_layout.addWidget(self.aufgebot_combo)
        
        # Bemerkung/Procedere
        self.bemerkung_label = QLabel("Bemerkung/Procedere:")
        self.bemerkung_label.setStyleSheet(self.get_label_style(False))
        entry_layout.addWidget(self.bemerkung_label)
        
        self.bemerkung_text = QTextEdit()
        self.bemerkung_text.setFixedHeight(80)
        self.bemerkung_text.setStyleSheet(self.get_textinput_style())
        self.bemerkung_text.textChanged.connect(self.update_label_styles)
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

    def update_label_styles(self):
        """Update label styles based on their content"""
        # Radiotherapy label
        radio_filled = self.radiotherapy_combo.currentText() != "-"
        self.radio_label.setStyleSheet(self.get_label_style(radio_filled))
        
        # Aufgebot label (only if visible)
        if self.aufgebot_combo.isVisible():
            aufgebot_filled = self.aufgebot_combo.currentText() != "-"
            self.aufgebot_label.setStyleSheet(self.get_label_style(aufgebot_filled))
        
        # Bemerkung label
        bemerkung_text = self.bemerkung_text.toPlainText().strip()
        bemerkung_filled = bool(bemerkung_text) and bemerkung_text != "-"
        self.bemerkung_label.setStyleSheet(self.get_label_style(bemerkung_filled))

    def on_radiotherapy_changed(self, text):
        """Handle radiotherapy selection change"""
        show_aufgebot = (text == "Ja")
        self.aufgebot_label.setVisible(show_aufgebot)
        self.aufgebot_combo.setVisible(show_aufgebot)
        
        # If showing aufgebot for the first time, reset to default "-"
        if show_aufgebot:
            self.aufgebot_combo.setCurrentText("-")
        
        # Update styles when visibility changes
        self.update_label_styles()

    def load_patient_data(self):
        """Load patient data from Excel file"""
        excel_path = Path.home() / "tumorboards" / self.tumorboard_name / self.date_str / f"{self.date_str}.xlsx"
        
        try:
            df = pd.read_excel(excel_path, engine='openpyxl')
            
            if df.empty:
                logging.warning(f"Excel file is empty: {excel_path}")
                return
            
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
                
                # Clean form data (handle NaN)
                radiotherapy = radiotherapy_raw if radiotherapy_raw != 'nan' and not pd.isna(radiotherapy_raw) else ''
                aufgebot = aufgebot_raw if aufgebot_raw != 'nan' and not pd.isna(aufgebot_raw) else ''
                bemerkung = bemerkung_raw if bemerkung_raw != 'nan' and not pd.isna(bemerkung_raw) else ''
                
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
        # Clear existing buttons
        for i in reversed(range(self.patient_list_layout.count())):
            self.patient_list_layout.itemAt(i).widget().setParent(None)
        
        # Create buttons for each patient
        for i, patient in enumerate(self.patients_data):
            # Truncate name if too long
            button_text = patient['name']
            if len(button_text) > 30:
                button_text = button_text[:27] + "..."
            
            button = QPushButton(button_text)
            button.setFixedHeight(40)
            button.setFixedWidth(200)  # Fixed width to ensure proper rounding
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            
            # Set button style based on state
            self.update_patient_button_style(button, i)
            
            # Connect button click
            button.clicked.connect(lambda checked, idx=i: self.load_patient(idx))
            
            self.patient_list_layout.addWidget(button)

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
        self.birth_date_data_label.setText(self.format_label_with_value("Geburtsdatum:", patient['birth_date']))
        self.age_data_label.setText(self.format_label_with_value("Alter:", patient['age']))
        self.diagnosis_data_label.setText(patient['diagnosis'])  # Only diagnosis text, no label
        
        # Load form data from Excel (not from cached patient data) to ensure proper reset
        excel_data = self.get_current_excel_data_for_patient(patient_index)
        
        # Set form fields based on Excel data
        self.radiotherapy_combo.setCurrentText(excel_data['radiotherapy'] if excel_data['radiotherapy'] not in ['', 'nan', '-'] else "-")
        self.aufgebot_combo.setCurrentText(excel_data['aufgebot'] if excel_data['aufgebot'] not in ['', 'nan', '-'] else "-")
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
        excel_path = Path.home() / "tumorboards" / self.tumorboard_name / self.date_str / f"{self.date_str}.xlsx"
        
        try:
            df = pd.read_excel(excel_path, engine='openpyxl')
            patient = self.patients_data[patient_index]
            row_index = patient['index']
            
            # Get current Excel values
            radiotherapy = str(df.at[row_index, 'Radiotherapie indiziert']) if 'Radiotherapie indiziert' in df.columns else ''
            aufgebot = str(df.at[row_index, 'Art des Aufgebots']) if 'Art des Aufgebots' in df.columns else ''
            bemerkung = str(df.at[row_index, 'Bemerkung/Procedere']) if 'Bemerkung/Procedere' in df.columns else ''
            
            # Clean values (handle NaN)
            if radiotherapy == 'nan' or pd.isna(radiotherapy):
                radiotherapy = ''
            if aufgebot == 'nan' or pd.isna(aufgebot):
                aufgebot = ''
            if bemerkung == 'nan' or pd.isna(bemerkung):
                bemerkung = ''
            
            return {
                'radiotherapy': radiotherapy,
                'aufgebot': aufgebot,
                'bemerkung': bemerkung
            }
        except Exception as e:
            logging.error(f"Error getting Excel data for patient: {e}")
            return {
                'radiotherapy': '',
                'aufgebot': '',
                'bemerkung': ''
            }

    def load_patient_pdf(self, patient):
        """Load the PDF for the current patient"""
        # Use the position in the filtered list for PDF numbering
        patient_position = self.patients_data.index(patient) + 1
        # PDF naming includes spaces around the dash
        pdf_filename = f"{patient_position} - {patient['patient_number']}.pdf"
        pdf_path = Path.home() / "tumorboards" / self.tumorboard_name / self.date_str / pdf_filename
        
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
            alt_patterns = [
                f"{patient_position}-{patient['patient_number']}.pdf",  # Without spaces
                f"{patient['patient_number']}.pdf",  # Just the patient number
                f"{patient_position}_{patient['patient_number']}.pdf",  # Underscore instead of dash
                f"{patient_position} _ {patient['patient_number']}.pdf",  # Spaces with underscore
                f"Patient_{patient_position}.pdf"  # Generic pattern
            ]
            
            for alt_pattern in alt_patterns:
                alt_path = Path.home() / "tumorboards" / self.tumorboard_name / self.date_str / alt_pattern
                if alt_path.exists():
                    logging.info(f"Found alternative PDF: {alt_path}")
                    try:
                        absolute_path = alt_path.resolve()
                        pdf_url = QUrl.fromLocalFile(str(absolute_path))
                        # Load with same settings (no sidebar, 120% zoom)
                        pdf_url_with_params = f"{pdf_url.toString()}#toolbar=1&navpanes=0&scrollbar=1&page=1&zoom=120"
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
        current_patient['bemerkung'] = self.bemerkung_text.toPlainText()
        
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
        bemerkung = patient['bemerkung'].strip()
        
        # Radiotherapy must be set
        if radiotherapy == "-" or radiotherapy == "":
            return False
        
        # If radiotherapy is "Ja", aufgebot must be set
        if radiotherapy == "Ja" and (aufgebot == "-" or aufgebot == ""):
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
        bemerkung = patient['bemerkung'].strip()
        
        if radiotherapy == "-" or radiotherapy == "":
            missing.append("Radiotherapie indiziert")
        
        if radiotherapy == "Ja" and (aufgebot == "-" or aufgebot == ""):
            missing.append("Art des Aufgebots")
        
        if not bemerkung or bemerkung == "-":
            missing.append("Bemerkung/Procedere")
        
        return missing

    def finalize_tumorboard(self):
        """Handle the finalize tumorboard button"""
        # Check for user data first
        nachname, vorname = self.get_benutzerdaten()
        
        if nachname is None or vorname is None:
            logging.warning("User data not found. Prompting user for input before finalizing.")
            dialog = BenutzerdatenDialog(self)
            result = dialog.exec()
            
            if result != QDialog.DialogCode.Accepted:
                # User cancelled, don't proceed
                return
            
            # Re-check user data after input
            nachname, vorname = self.get_benutzerdaten()
            if nachname is None or vorname is None:
                error_msg = QMessageBox(self)
                error_msg.setWindowTitle("Fehler")
                error_msg.setText("Benutzerdaten konnten nicht gespeichert werden. Finalisierung abgebrochen.")
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
        
        # Show confirmation dialog
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Tumorboard abschließen")
        
        # Check if there are unprocessed patients
        if hasattr(self, 'unprocessed_patient_count') and self.unprocessed_patient_count > 0:
            msg_text = (f"Sind Sie sicher, dass Sie das Tumor Board abschließen wollen?\n\n"
                       f"Aktuell wurden {self.unprocessed_patient_count} Patient(en) weder als bearbeitet "
                       f"noch als übersprungen definiert.")
        else:
            msg_text = "Sind Sie sicher, dass Sie das Tumorboard finalisieren und exportieren möchten?"
        
        msg_box.setText(msg_text)
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
            # Check which patients were changed before saving
            changed_patients = self.get_changed_patients_for_finalization()
            
            # Save current patient data first
            try:
                self.save_to_excel(skip_edit_logging=True)  # Skip automatic edit logging
            except Exception as e:
                logging.error(f"Error saving before finalization: {e}")
                error_msg = QMessageBox(self)
                error_msg.setWindowTitle("Fehler")
                error_msg.setText(f"Fehler beim Speichern: {e}")
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
            user_name = f"{vorname} {nachname}"
            
            # Save timestamp to file
            timestamp_file = Path.home() / "tumorboards" / self.tumorboard_name / self.date_str / "finalized_timestamp.txt"
            try:
                if timestamp_file.exists():
                    # Already finalized before - this is an edit session
                    if changed_patients:
                        # Only add edit entry if patients were actually changed
                        patient_numbers_str = ", ".join(changed_patients)
                        edit_entry = f"Editiert: {timestamp_str} von {user_name} ({patient_numbers_str})\n"
                        
                        with open(timestamp_file, 'a', encoding='utf-8') as f:
                            f.write(edit_entry)
                        
                        logging.info(f"Logged edit session by {user_name} for patients: {patient_numbers_str}")
                    else:
                        logging.info(f"No changes detected - no edit timestamp added")
                else:
                    # First time finalization
                    with open(timestamp_file, 'w', encoding='utf-8') as f:
                        f.write(f"Abgeschlossen: {timestamp_str} von {user_name}\n")
                    
                    logging.info(f"Tumorboard first finalized at {timestamp_str} by {user_name}")
                
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
            
            # Navigate back to Excel viewer page
            self.main_window.navigate_back_to_excel_viewer(self.tumorboard_name, self.date_str)
            
            # Show success message with proper styling
            success_msg = QMessageBox(self)
            success_msg.setWindowTitle("Erfolg")
            success_msg.setText("Das Tumorboard wurde erfolgreich abgeschlossen!")
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
        
        logging.info("Tumorboard finalization completed")

    def save_to_excel(self, skip_edit_logging=False):
        """Save all patient data back to Excel file"""
        excel_path = Path.home() / "tumorboards" / self.tumorboard_name / self.date_str / f"{self.date_str}.xlsx"
        
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
            current_bemerkung = str(df.at[row_index, 'Bemerkung/Procedere']) if 'Bemerkung/Procedere' in df.columns else ''
            
            # Clean current values (handle NaN)
            if current_radio == 'nan' or pd.isna(current_radio):
                current_radio = ''
            if current_aufgebot == 'nan' or pd.isna(current_aufgebot):
                current_aufgebot = ''
            if current_bemerkung == 'nan' or pd.isna(current_bemerkung):
                current_bemerkung = ''
            
            # Check if any field changed
            if (patient['radiotherapy'] != current_radio or 
                patient['aufgebot'] != current_aufgebot or 
                patient['bemerkung'] != current_bemerkung):
                changed_patients.append(patient['patient_number'])
            
            # Update the fields
            df.at[row_index, 'Radiotherapie indiziert'] = patient['radiotherapy']
            df.at[row_index, 'Art des Aufgebots'] = patient['aufgebot']
            df.at[row_index, 'Bemerkung/Procedere'] = patient['bemerkung']
        
        # Save back to Excel
        df.to_excel(excel_path, index=False, engine='openpyxl')
        
        # Log edits if tumorboard was already finalized (only if not skipping)
        timestamp_file = Path.home() / "tumorboards" / self.tumorboard_name / self.date_str / "finalized_timestamp.txt"
        if not skip_edit_logging and timestamp_file.exists() and changed_patients:
            # Get user data
            nachname, vorname = self.get_benutzerdaten()
            if nachname and vorname:
                user_name = f"{vorname} {nachname}"
                now = datetime.now()
                timestamp_str = now.strftime("%d.%m.%Y %H:%M")
                
                # Create edit log entry
                patient_numbers_str = ", ".join(changed_patients)
                edit_entry = f"Editiert: {timestamp_str} von {user_name} ({patient_numbers_str})\n"
                
                try:
                    # Append edit log to timestamp file
                    with open(timestamp_file, 'a', encoding='utf-8') as f:
                        f.write(edit_entry)
                    logging.info(f"Logged edit session by {user_name} for patients: {patient_numbers_str}")
                except Exception as e:
                    logging.error(f"Error logging edit: {e}")
        
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

    def add_new_patient(self):
        """Add a new patient manually through dialog"""
        dialog = AddPatientDialog(self)
        result = dialog.exec()
        
        if result == QDialog.DialogCode.Accepted:
            patient_data = dialog.get_patient_data()
            
            # Validate required fields
            if not patient_data['name'] or not patient_data['patient_number'] or not patient_data['diagnosis']:
                missing_fields = []
                if not patient_data['name']:
                    missing_fields.append("Name")
                if not patient_data['patient_number']:
                    missing_fields.append("Patientennummer") 
                if not patient_data['diagnosis']:
                    missing_fields.append("Diagnose")
                
                missing_text = ", ".join(missing_fields)
                QMessageBox.warning(self, "Eingabe fehlt", 
                                  f"Folgende Felder müssen ausgefüllt werden: {missing_text}")
                return
            
            # Check if patient number already exists
            for existing_patient in self.patients_data:
                if existing_patient['patient_number'] == patient_data['patient_number']:
                    QMessageBox.warning(self, "Patient existiert", 
                                      f"Ein Patient mit der Nummer {patient_data['patient_number']} existiert bereits.")
                    return
            
            # Calculate age if birth date provided
            calculated_age = "-"
            if patient_data['birth_date']:
                calculated_age = self.calculate_age(patient_data['birth_date'])
            
            # Create new patient data entry
            new_patient = {
                'index': len(self.patients_data),  # Temporary index
                'name': patient_data['name'],
                'birth_date': patient_data['birth_date'] if patient_data['birth_date'] else '-',
                'age': calculated_age,
                'diagnosis': patient_data['diagnosis'] if patient_data['diagnosis'] else '-',
                'icd_code': patient_data['icd_code'] if patient_data['icd_code'] else '-',
                'patient_number': patient_data['patient_number'],
                'radiotherapy': '',
                'aufgebot': '',
                'bemerkung': ''
            }
            
            # Add to patients list
            self.patients_data.append(new_patient)
            
            # Initialize patient state
            patient_index = len(self.patients_data) - 1
            self.patient_states[patient_index] = 'normal'
            
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
        excel_path = Path.home() / "tumorboards" / self.tumorboard_name / self.date_str / f"{self.date_str}.xlsx"
        
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
                               'Radiotherapie indiziert', 'Art des Aufgebots', 'Bemerkung/Procedere']
            
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
        excel_path = Path.home() / "tumorboards" / self.tumorboard_name / self.date_str / f"{self.date_str}.xlsx"
        
        try:
            df = pd.read_excel(excel_path, engine='openpyxl')
            changed_patients = []
            
            # Compare current patient data with what's in Excel
            for patient in self.patients_data:
                row_index = patient['index']
                
                # Get current Excel values
                current_radio = str(df.at[row_index, 'Radiotherapie indiziert']) if 'Radiotherapie indiziert' in df.columns else ''
                current_aufgebot = str(df.at[row_index, 'Art des Aufgebots']) if 'Art des Aufgebots' in df.columns else ''
                current_bemerkung = str(df.at[row_index, 'Bemerkung/Procedere']) if 'Bemerkung/Procedere' in df.columns else ''
                
                # Clean current values (handle NaN)
                if current_radio == 'nan' or pd.isna(current_radio):
                    current_radio = ''
                if current_aufgebot == 'nan' or pd.isna(current_aufgebot):
                    current_aufgebot = ''
                if current_bemerkung == 'nan' or pd.isna(current_bemerkung):
                    current_bemerkung = ''
                
                # Check if any field changed
                if (patient['radiotherapy'] != current_radio or 
                    patient['aufgebot'] != current_aufgebot or 
                    patient['bemerkung'] != current_bemerkung):
                    changed_patients.append(patient['patient_number'])
            
            return changed_patients
            
        except Exception as e:
            logging.error(f"Error getting changed patients for finalization: {e}")
            return []

    def is_patient_skipped(self, patient):
        """Check if a patient is marked as skipped (all three data fields are "-")"""
        return (patient['radiotherapy'] == "-" and 
                patient['aufgebot'] == "-" and 
                patient['bemerkung'] == "-")