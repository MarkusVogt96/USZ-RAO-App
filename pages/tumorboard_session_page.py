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
        
        # Message
        message = f"Daten {missing_data} im aktuellen Fall nicht erfasst, soll der Patient als \"Nicht besprochen\" markiert werden?"
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
        vorname_label = QLabel("Vorname:")
        nachname_label = QLabel("Nachname:")
        label_style = "color: white;"
        vorname_label.setStyleSheet(label_style)
        nachname_label.setStyleSheet(label_style)
        
        form_layout.addRow(vorname_label, self.vorname_edit)
        form_layout.addRow(nachname_label, self.nachname_edit)
        
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
        patient_layout.setSpacing(10)
        
        # Header (no border)
        header_label = QLabel("Patienten")
        header_label.setFont(QFont("Helvetica", 16, QFont.Weight.Bold))
        header_label.setStyleSheet("color: #4FC3F7; margin-bottom: 10px; border: none;")
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        patient_layout.addWidget(header_label)
        
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
        self.pdf_header_label.setFont(QFont("Helvetica", 12, QFont.Weight.Bold))
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
        
        data_layout = QVBoxLayout(data_frame)
        data_layout.setContentsMargins(15, 15, 15, 15)
        data_layout.setSpacing(15)
        
        # Header (no border)
        header_label = QLabel("Patientendaten")
        header_label.setFont(QFont("Helvetica", 16, QFont.Weight.Bold))
        header_label.setStyleSheet("color: #4FC3F7; margin-bottom: 10px; border: none;")
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        data_layout.addWidget(header_label)
        
        # Patient info section
        self.create_patient_info_section(data_layout)
        
        # Data entry section
        self.create_data_entry_section(data_layout)
        
        # Buttons section
        self.create_buttons_section(data_layout)
        
        # Add stretch to push everything up
        data_layout.addStretch()
        
        main_layout.addWidget(data_frame)

    def create_patient_info_section(self, data_layout):
        """Create patient information display section"""
        info_frame = QFrame()
        info_frame.setStyleSheet("""
            QFrame {
                background-color: #232F3B;
                border: none;
                border-radius: 6px;
                padding: 10px;
            }
        """)
        
        info_layout = QVBoxLayout(info_frame)
        info_layout.setContentsMargins(10, 10, 10, 10)
        info_layout.setSpacing(3)  # Reduced from 8 to 3 for tighter spacing
        
        # Patient info labels and data (most in one line, only diagnosis separate)
        # Name (one line)
        self.name_data_label = QLabel("Name: -")
        self.name_data_label.setStyleSheet("color: white; font-size: 14px; font-weight: bold; border: none;")
        self.name_data_label.setWordWrap(True)
        info_layout.addWidget(self.name_data_label)
        
        # Birth date (one line)
        self.birth_date_data_label = QLabel("Geburtsdatum: -")
        self.birth_date_data_label.setStyleSheet("color: white; font-size: 14px; font-weight: bold; border: none;")
        info_layout.addWidget(self.birth_date_data_label)
        
        # Age (one line)
        self.age_data_label = QLabel("Alter: -")
        self.age_data_label.setStyleSheet("color: white; font-size: 14px; font-weight: bold; border: none;")
        info_layout.addWidget(self.age_data_label)
        
        # Diagnosis (separate lines, no indent, minimal spacing)
        diagnosis_title_label = QLabel("Diagnose:")
        diagnosis_title_label.setStyleSheet("color: white; font-size: 14px; font-weight: bold; border: none; margin-bottom: 0px;")
        info_layout.addWidget(diagnosis_title_label)
        
        self.diagnosis_data_label = QLabel("-")
        self.diagnosis_data_label.setStyleSheet("color: white; font-size: 14px; border: none; margin-top: 0px;")
        self.diagnosis_data_label.setWordWrap(True)
        info_layout.addWidget(self.diagnosis_data_label)
        
        # ICD Code (one line)
        self.icd_data_label = QLabel("ICD-Code: -")
        self.icd_data_label.setStyleSheet("color: white; font-size: 14px; font-weight: bold; border: none;")
        self.icd_data_label.setWordWrap(True)
        info_layout.addWidget(self.icd_data_label)
        
        data_layout.addWidget(info_frame)

    def create_data_entry_section(self, data_layout):
        """Create data entry controls section"""
        entry_frame = QFrame()
        entry_frame.setStyleSheet("""
            QFrame {
                background-color: #232F3B;
                border: 1px solid #425061;
                border-radius: 6px;
                padding: 10px;
            }
        """)
        
        entry_layout = QVBoxLayout(entry_frame)
        entry_layout.setContentsMargins(10, 10, 10, 10)
        entry_layout.setSpacing(15)
        
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
        
        data_layout.addWidget(entry_frame)

    def create_buttons_section(self, data_layout):
        """Create buttons section"""
        button_layout = QVBoxLayout()
        button_layout.setSpacing(10)
        
        # Save button
        self.save_button = QPushButton("Speichern")
        self.save_button.setFixedHeight(40)
        self.save_button.setStyleSheet("""
            QPushButton {
                background-color: #2E8B57;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #3CB371;
            }
            QPushButton:pressed {
                background-color: #228B22;
            }
        """)
        self.save_button.clicked.connect(self.save_patient_data)
        button_layout.addWidget(self.save_button)
        
        # Next patient button
        self.next_button = QPushButton("Nächster Patient")
        self.next_button.setFixedHeight(40)
        self.next_button.setStyleSheet("""
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
        self.next_button.clicked.connect(self.next_patient)
        button_layout.addWidget(self.next_button)
        
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
        
        data_layout.addLayout(button_layout)

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
        bemerkung_filled = bool(self.bemerkung_text.toPlainText().strip())
        self.bemerkung_label.setStyleSheet(self.get_label_style(bemerkung_filled))

    def on_radiotherapy_changed(self, text):
        """Handle radiotherapy selection change"""
        show_aufgebot = (text == "Ja")
        self.aufgebot_label.setVisible(show_aufgebot)
        self.aufgebot_combo.setVisible(show_aufgebot)
        
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
                
                patient_data = {
                    'index': index,
                    'name': patient_name,
                    'birth_date': birth_date_str,
                    'age': calculated_age,
                    'diagnosis': str(row.get('Diagnose', '-')),
                    'icd_code': str(row.get('ICD-Code', '-')),
                    'patient_number': patient_number_clean,
                    'radiotherapy': str(row.get('Radiotherapie indiziert', '')),
                    'aufgebot': str(row.get('Art des Aufgebots', '')),
                    'bemerkung': str(row.get('Bemerkung/Procedere', ''))
                }
                self.patients_data.append(patient_data)
                
                # Initialize patient state using the position in filtered list
                self.patient_states[len(self.patients_data) - 1] = 'normal'  # normal, completed, skipped
            
            # Create patient buttons
            self.create_patient_buttons()
            
            # Load first patient
            if self.patients_data:
                self.load_patient(0)
                
            logging.info(f"Loaded {len(self.patients_data)} patients from Excel file")
            
        except Exception as e:
            logging.error(f"Error loading patient data: {e}")
            QMessageBox.critical(self, "Error", f"Could not load patient data: {e}")

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

    def load_patient(self, patient_index):
        """Load a specific patient's data"""
        if patient_index < 0 or patient_index >= len(self.patients_data):
            return
        
        self.current_patient_index = patient_index
        patient = self.patients_data[patient_index]
        
        # Update patient info display - most in one line, only diagnosis separate
        self.name_data_label.setText(f"Name: {patient['name']}")
        self.birth_date_data_label.setText(f"Geburtsdatum: {patient['birth_date']}")
        self.age_data_label.setText(f"Alter: {patient['age']}")
        self.diagnosis_data_label.setText(patient['diagnosis'])  # Only diagnosis text, no label
        self.icd_data_label.setText(f"ICD-Code: {patient['icd_code']}")
        
        # Load existing data into form
        self.radiotherapy_combo.setCurrentText(patient['radiotherapy'] if patient['radiotherapy'] != 'nan' else "-")
        self.aufgebot_combo.setCurrentText(patient['aufgebot'] if patient['aufgebot'] != 'nan' else "-")
        self.bemerkung_text.setPlainText(patient['bemerkung'] if patient['bemerkung'] != 'nan' else "")
        
        # Update label styles after loading data
        self.update_label_styles()
        
        # Load PDF
        self.load_patient_pdf(patient)
        
        # Update button styles
        self.update_all_patient_button_styles()
        
        logging.info(f"Loaded patient {patient_index + 1}: {patient['name']}")

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

    def save_patient_data(self):
        """Save current patient data to Excel (silent save)"""
        if not self.patients_data:
            return
        
        current_patient = self.patients_data[self.current_patient_index]
        
        # Update patient data
        current_patient['radiotherapy'] = self.radiotherapy_combo.currentText()
        current_patient['aufgebot'] = self.aufgebot_combo.currentText()
        current_patient['bemerkung'] = self.bemerkung_text.toPlainText()
        
        # Check if patient is now complete
        is_complete = self.is_patient_complete(current_patient)
        if is_complete:
            self.patient_states[self.current_patient_index] = 'completed'
        
        # Save to Excel file (silently - no dialog)
        try:
            self.save_to_excel()
            self.update_all_patient_button_styles()
            # No dialog box - silent save
            logging.info(f"Saved data for patient {self.current_patient_index + 1}")
        except Exception as e:
            logging.error(f"Error saving patient data: {e}")
            QMessageBox.critical(self, "Fehler", f"Fehler beim Speichern: {e}")

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
        
        # Bemerkung must have content
        if not bemerkung:
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
        
        if not bemerkung:
            missing.append("Bemerkung/Procedere")
        
        return missing

    def next_patient(self):
        """Move to next patient with validation"""
        # Update current patient data
        current_patient = self.patients_data[self.current_patient_index]
        current_patient['radiotherapy'] = self.radiotherapy_combo.currentText()
        current_patient['aufgebot'] = self.aufgebot_combo.currentText()
        current_patient['bemerkung'] = self.bemerkung_text.toPlainText()
        
        # Check if current patient is complete
        if not self.is_patient_complete(current_patient):
            missing_fields = self.get_missing_fields(current_patient)
            missing_data = ", ".join(missing_fields)
            
            # Show dialog only for "Nächster Patient"
            dialog = PatientNotRecordedDialog(missing_data, self)
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
        
        # Move to next patient
        next_index = self.current_patient_index + 1
        if next_index < len(self.patients_data):
            self.load_patient(next_index)
        else:
            QMessageBox.information(self, "Fertig", "Alle Patienten wurden bearbeitet!")

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
                QMessageBox.critical(self, "Fehler", "Benutzerdaten konnten nicht gespeichert werden. Finalisierung abgebrochen.")
                return
        
        # Show confirmation dialog
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Tumorboard abschließen")
        msg_box.setText("Sind Sie sicher dass Sie das Tumorboard finalisieren und exportieren möchten?")
        msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg_box.setDefaultButton(QMessageBox.StandardButton.No)
        msg_box.setStyleSheet("""
            QMessageBox {
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
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #1a5a9e;
            }
        """)
        
        result = msg_box.exec()
        
        if result == QMessageBox.StandardButton.Yes:
            # Save current patient data first
            try:
                self.save_to_excel()
            except Exception as e:
                logging.error(f"Error saving before finalization: {e}")
                QMessageBox.critical(self, "Fehler", f"Fehler beim Speichern: {e}")
                return
            
            # Create timestamp
            now = datetime.now()
            timestamp_str = now.strftime("%d.%m.%Y %H:%M")
            user_name = f"{vorname} {nachname}"
            
            # Save timestamp to file
            timestamp_file = Path.home() / "tumorboards" / self.tumorboard_name / self.date_str / "finalized_timestamp.txt"
            try:
                with open(timestamp_file, 'w', encoding='utf-8') as f:
                    f.write(f"Finalized: {timestamp_str} by {user_name}\n")
                logging.info(f"Tumorboard finalized at {timestamp_str} by {user_name}")
            except Exception as e:
                logging.error(f"Error saving timestamp: {e}")
                QMessageBox.critical(self, "Fehler", f"Fehler beim Speichern des Timestamps: {e}")
                return
            
            # Navigate back to Excel viewer page
            self.main_window.navigate_back_to_excel_viewer(self.tumorboard_name, self.date_str)
            
            QMessageBox.information(self, "Erfolg", "Das Tumorboard wurde erfolgreich abgeschlossen!")
        
        logging.info("Tumorboard finalization completed")

    def save_to_excel(self):
        """Save all patient data back to Excel file"""
        excel_path = Path.home() / "tumorboards" / self.tumorboard_name / self.date_str / f"{self.date_str}.xlsx"
        
        # Read current Excel file
        df = pd.read_excel(excel_path, engine='openpyxl')
        
        # Update the relevant columns using the original Excel index
        for patient in self.patients_data:
            row_index = patient['index']
            df.at[row_index, 'Radiotherapie indiziert'] = patient['radiotherapy']
            df.at[row_index, 'Art des Aufgebots'] = patient['aufgebot']
            df.at[row_index, 'Bemerkung/Procedere'] = patient['bemerkung']
        
        # Save back to Excel
        df.to_excel(excel_path, index=False, engine='openpyxl')
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