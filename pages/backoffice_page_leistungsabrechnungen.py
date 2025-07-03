from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                             QFrame, QMessageBox, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QProgressBar, QScrollArea, QComboBox,
                             QDateEdit, QDialog, QDialogButtonBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QDate, QTimer
from PyQt6.QtGui import QFont
import os
import logging
import re
import subprocess
from pathlib import Path
from datetime import datetime, date
import pandas as pd

# Import our billing tracker
from utils.billing_tracker import BillingTracker

class KisimBillingDialog(QDialog):
    """Dialog for confirming KISIM billing automation"""
    def __init__(self, tumorboard_name, date_str, parent=None):
        super().__init__(parent)
        self.tumorboard_name = tumorboard_name
        self.date_str = date_str
        self.setWindowTitle("KISIM Automatisierte Abrechnung")
        self.setFixedSize(500, 250)
        self.setStyleSheet("""
            QDialog {
                background-color: #1a2633;
                color: white;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Message
        message_label = QLabel(f"Es erfolgt jetzt die automatisierte Leistungsabrechnung für:\n\n"
                              f"Tumorboard: {tumorboard_name}\n"
                              f"Datum: {date_str}\n\n"
                              f"Bitte gewährleisten Sie, dass KISIM geöffnet ist und sich der "
                              f"Benutzer eingeloggt hat.\n\n"
                              f"Bestätigen Sie die Voraussetzung mit \"OK\".")
        message_label.setFont(QFont("Helvetica", 12))
        message_label.setStyleSheet("color: white; line-height: 1.4;")
        message_label.setWordWrap(True)
        layout.addWidget(message_label)
        
        # Buttons
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | 
                                          QDialogButtonBox.StandardButton.Cancel)
        self.button_box.setStyleSheet("""
            QPushButton {
                background-color: #114473;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
                min-width: 80px;
                min-height: 30px;
            }
            QPushButton:hover {
                background-color: #1a5a9e;
            }
            QPushButton:pressed {
                background-color: #0d3355;
            }
        """)
        
        # Set button text to German
        self.button_box.button(QDialogButtonBox.StandardButton.Ok).setText("OK")
        self.button_box.button(QDialogButtonBox.StandardButton.Cancel).setText("Abbrechen")
        
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        
        layout.addWidget(self.button_box)

class TumorboardIndexingThread(QThread):
    """Thread for indexing completed tumorboards with billing status"""
    progress_update = pyqtSignal(str)  # Progress message
    indexing_complete = pyqtSignal(list)  # List of completed tumorboards with billing info
    error_occurred = pyqtSignal(str)  # Error message

    def __init__(self):
        super().__init__()
        self.tumorboards_path = Path("C:/Users/marku/tumorboards")
        self.billing_tracker = BillingTracker()
        self.completed_tumorboards = []
        self._should_stop = False
        self._max_runtime = 300  # 5 minutes timeout
    
    def stop_indexing(self):
        """Stop the indexing process"""
        self._should_stop = True

    def is_valid_date_format(self, folder_name):
        """Check if folder name matches dd.mm.yyyy format"""
        pattern = r"^\d{2}\.\d{2}\.\d{4}$"
        return bool(re.match(pattern, folder_name))
        
    def get_excel_case_count(self, excel_path):
        """Get number of cases from Excel file"""
        try:
            df = pd.read_excel(excel_path)
            if df.empty:
                return 0
            
            # Count all rows that contain patient data
            # Look for rows that have patient number or name data
            patient_count = 0
            for _, row in df.iterrows():
                # Check if row has meaningful patient data (not just empty cells)
                non_empty_cells = [str(cell).strip() for cell in row if pd.notna(cell) and str(cell).strip()]
                if len(non_empty_cells) > 0:
                    patient_count += 1
            
            return patient_count
        except Exception as e:
            logging.warning(f"Could not read Excel file {excel_path}: {e}")
            return 0

    def run(self):
        """Run the indexing process"""
        import time
        start_time = time.time()
        
        try:
            logging.info("Starting tumorboard indexing for billing...")
            self.progress_update.emit("Starte Indexing der abgeschlossenen Tumorboards...")
            
            if self._should_stop:
                return
            
            # Check if the path is accessible
            if not self.tumorboards_path.exists():
                error_msg = f"Tumorboards path does not exist: {self.tumorboards_path}"
                logging.error(error_msg)
                self.error_occurred.emit("Keine Verbindung zum Tumorboards-Verzeichnis verfügbar")
                return
            
            self.completed_tumorboards = []
            
            # Get all entity folders
            try:
                all_folders = list(self.tumorboards_path.iterdir())
                entity_folders = [f for f in all_folders 
                                if f.is_dir() and not f.name.startswith('_') and not f.name.startswith('__')]
                
            except Exception as e:
                error_msg = f"Error getting entity folders: {e}"
                logging.error(error_msg)
                self.error_occurred.emit(f"Fehler beim Abrufen der Entitäts-Ordner: {str(e)}")
                return
            
            total_entities = len(entity_folders)
            logging.info(f"Indexing {total_entities} tumorboard entities for billing status")
            
            for i, entity_folder in enumerate(entity_folders):
                current_time = time.time()
                if self._should_stop or current_time - start_time > self._max_runtime:
                    return
                
                entity_name = entity_folder.name
                self.progress_update.emit(f"Prüfe {entity_name} ({i+1}/{total_entities})...")
                
                try:
                    if not entity_folder.exists() or not entity_folder.is_dir():
                        continue
                    
                    # Look for date folders in this entity
                    try:
                        date_folder_items = list(entity_folder.iterdir())
                        date_folders = [f for f in date_folder_items if f.is_dir()]
                        
                    except (PermissionError, Exception) as e:
                        logging.warning(f"Error iterating {entity_folder}: {e}")
                        continue
                    
                    for date_folder in date_folders:
                        try:
                            if not date_folder.exists() or not date_folder.is_dir():
                                continue
                                
                            # Check if folder name matches date format
                            if self.is_valid_date_format(date_folder.name):
                                # Check for timestamp file
                                try:
                                    timestamp_files = list(date_folder.glob("*timestamp*"))
                                    
                                    if timestamp_files:
                                        # Check for Excel file
                                        excel_file = date_folder / f"{date_folder.name}.xlsx"
                                        
                                        if excel_file.exists() and excel_file.is_file():
                                            # Get case count
                                            case_count = self.get_excel_case_count(excel_file)
                                            
                                            # Check billing status
                                            billing_status = self.billing_tracker.get_billing_status(
                                                entity_name, date_folder.name)
                                            
                                            # This is a completed tumorboard
                                            tumorboard_info = {
                                                'tumorboard': entity_name,
                                                'datum': date_folder.name,
                                                'anzahl_faelle': case_count,
                                                'date_folder_path': date_folder,
                                                'excel_path': excel_file,
                                                'timestamp_file': timestamp_files[0],
                                                'billing_status': billing_status,
                                                'is_billed': billing_status is not None
                                            }
                                            
                                            self.completed_tumorboards.append(tumorboard_info)
                                            logging.info(f"Found completed tumorboard: {entity_name} - {date_folder.name}")
                                            
                                except Exception as e:
                                    logging.error(f"Error processing timestamp/excel files in {date_folder}: {e}")
                                    continue
                                    
                        except Exception as e:
                            logging.error(f"Error processing date folder {date_folder}: {e}")
                            continue
                            
                        # Yield control to prevent UI freezing
                        self.msleep(1)
                        
                except Exception as e:
                    logging.error(f"Error processing entity folder {entity_folder}: {e}")
                    continue
            
            # Sort by date (newest first)
            self.completed_tumorboards.sort(key=lambda x: datetime.strptime(x['datum'], '%d.%m.%Y'), reverse=True)
            
            logging.info(f"Indexing complete. Found {len(self.completed_tumorboards)} completed tumorboards")
            self.indexing_complete.emit(self.completed_tumorboards)
            
        except Exception as e:
            logging.error(f"Error during tumorboard indexing: {e}")
            self.error_occurred.emit(f"Fehler beim Indexing: {str(e)}")

class BackofficePageLeistungsabrechnungen(QWidget):
    def __init__(self, main_window):
        super().__init__()
        logging.info("Initializing BackofficePageLeistungsabrechnungen...")
        self.main_window = main_window
        self.billing_tracker = BillingTracker()
        self.completed_tumorboards = []
        self.indexing_thread = None
        self.setup_ui()
        logging.info("BackofficePageLeistungsabrechnungen initialization complete.")

    def setup_ui(self):
        """Setup the leistungsabrechnungen user interface"""
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(30, 20, 30, 30)
        main_layout.setSpacing(20)
        self.setLayout(main_layout)

        # Header with back button, title and refresh button
        header_layout = QHBoxLayout()
        header_layout.setSpacing(15)

        # Back button removed as per user request

        # Title
        title_label = QLabel("Leistungsabrechnung Tumorboards")
        title_label.setFont(QFont("Helvetica", 24, QFont.Weight.Bold))
        title_label.setStyleSheet("color: white;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        # Refresh button
        self.refresh_button = QPushButton("⟲ Aktualisieren")
        self.refresh_button.setFont(QFont("Helvetica", 12))
        self.refresh_button.setFixedSize(140, 40)
        self.refresh_button.setStyleSheet("""
            QPushButton {
                background-color: #114473;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 15px;
            }
            QPushButton:hover {
                background-color: #1a5a9e;
            }
            QPushButton:pressed {
                background-color: #0d3355;
            }
            QPushButton:disabled {
                background-color: #425061;
                color: #888888;
            }
        """)
        self.refresh_button.clicked.connect(self.start_indexing)
        header_layout.addWidget(self.refresh_button)

        main_layout.addLayout(header_layout)

        # Progress bar (initially hidden)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #425061;
                border-radius: 4px;
                text-align: center;
                color: white;
                background-color: #232F3B;
            }
            QProgressBar::chunk {
                background-color: #3292ea;
                border-radius: 3px;
            }
        """)
        main_layout.addWidget(self.progress_bar)

        # Progress label (initially hidden)
        self.progress_label = QLabel("")
        self.progress_label.setVisible(False)
        self.progress_label.setFont(QFont("Helvetica", 11))
        self.progress_label.setStyleSheet("color: #CCCCCC; margin-bottom: 10px;")
        main_layout.addWidget(self.progress_label)

        # Content
        self.create_content(main_layout)
        
        # Start initial indexing
        QTimer.singleShot(500, self.start_indexing)

    def create_content(self, parent_layout):
        """Create the main content"""
        # Scrollable area for content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                background-color: #232F3B;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #425061;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #5A6B7D;
            }
        """)
        
        # Content widget inside scroll area
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(25)
        content_layout.setContentsMargins(0, 0, 0, 0)

        # Tumorboard Abrechnungen section
        self.create_tumorboard_section(content_layout)

        # Set scroll area content
        scroll_area.setWidget(content_widget)
        parent_layout.addWidget(scroll_area)

    def create_tumorboard_section(self, parent_layout):
        """Create section showing tumorboard billings"""
        bills_title = QLabel("Übersicht abgeschlossener und abrechenbarer Tumorboards:")
        bills_title.setFont(QFont("Helvetica", 18, QFont.Weight.Bold))
        bills_title.setStyleSheet("color: #00BFFF; margin-bottom: 10px; margin-top: 15px;")
        parent_layout.addWidget(bills_title)

        # Table frame
        table_frame = QFrame()
        # Use transparent frame with no padding to avoid dark border and misalignment
        table_frame.setStyleSheet("""
            QFrame {
                background-color: transparent;
                border: none;
                padding: 0px;
            }
        """)
        
        table_layout = QVBoxLayout(table_frame)
        
        # Create table
        self.bills_table = QTableWidget()
        self.bills_table.setColumnCount(5)
        self.bills_table.setHorizontalHeaderLabels([
            "Tumorboard", "Datum", "Anzahl Fälle", "Abrechnung Status", "Aktionen"
        ])
        
        # Style the table
        self.bills_table.setStyleSheet("""
            QTableWidget {
                background-color: #232F3B;
                alternate-background-color: #2A3642;
                selection-background-color: #3292ea;
                gridline-color: #425061;
                color: white;
                border: 1px solid #425061;
            }
            QTableWidget::item {
                padding: 3px;
                border-bottom: 1px solid #425061;
            }
            QTableWidget::item:selected {
                background-color: #3292ea;
            }
            QHeaderView::section {
                background-color: #1a2633;
                color: white;
                padding: 3px;
                border: 1px solid #425061;
                font-weight: bold;
                font-size: 16px;
            }
            QTableWidget QTableCornerButton::section {
                background-color: #1a2633;
                border: 1px solid #425061;
            }
        """)
        
        # Set table properties
        self.bills_table.setAlternatingRowColors(True)
        self.bills_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.bills_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.bills_table.setSortingEnabled(True)

        # Configure headers to resize properly
        horizontal_header = self.bills_table.horizontalHeader()
        horizontal_header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        horizontal_header.setStretchLastSection(True)
        # Allow dynamic height based on font size and padding (no fixed height)

        vertical_header = self.bills_table.verticalHeader()
        vertical_header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        vertical_header.setMinimumSectionSize(60)
        
        # Hide the vertical header (row numbers) to avoid offset issues
        vertical_header.setVisible(False)
        
        # Set specific column widths
        horizontal_header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # Tumorboard
        horizontal_header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # Datum
        horizontal_header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Anzahl Fälle
        horizontal_header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)  # Status
        horizontal_header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)  # Aktionen
        
        # Fix corner button styling after widget is created
        QTimer.singleShot(100, self._fix_corner_button_styling)
        
        table_layout.addWidget(self.bills_table)
        parent_layout.addWidget(table_frame)

    def _fix_corner_button_styling(self):
        """Fix the corner button styling after the widget is fully initialized"""
        try:
            # Find the corner button and apply styling
            corner_button = self.bills_table.findChild(QPushButton)
            if corner_button:
                corner_button.setStyleSheet("""
                    QPushButton {
                        background-color: #1a2633;
                        border: 1px solid #425061;
                    }
                """)
                # Disable the corner button to prevent select all functionality
                corner_button.setEnabled(False)
                logging.info("Corner button styling applied successfully")
        except Exception as e:
            logging.warning(f"Could not apply corner button styling: {e}")

    def start_indexing(self):
        """Start the indexing process"""
        if self.indexing_thread and self.indexing_thread.isRunning():
            return
            
        logging.info("Starting tumorboard indexing for billing...")
        self.refresh_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.progress_label.setVisible(True)
        self.progress_label.setText("Starte Indexing...")
        
        # Create and start indexing thread
        self.indexing_thread = TumorboardIndexingThread()
        self.indexing_thread.progress_update.connect(self.update_indexing_progress)
        self.indexing_thread.indexing_complete.connect(self.on_indexing_complete)
        self.indexing_thread.error_occurred.connect(self.on_indexing_error)
        self.indexing_thread.start()

    def update_indexing_progress(self, message):
        """Update the progress message"""
        self.progress_label.setText(message)

    def on_indexing_complete(self, completed_tumorboards):
        """Handle indexing completion"""
        logging.info(f"Indexing complete. Found {len(completed_tumorboards)} completed tumorboards")
        self.completed_tumorboards = completed_tumorboards
        self.populate_table()
        
        # Hide progress indicators
        self.progress_bar.setVisible(False)
        self.progress_label.setVisible(False)
        self.refresh_button.setEnabled(True)

    def on_indexing_error(self, error_message):
        """Handle indexing error"""
        logging.error(f"Indexing error: {error_message}")
        
        # Error message with custom styling
        indexing_error_msg = QMessageBox(self)
        indexing_error_msg.setWindowTitle("Indexing Fehler")
        indexing_error_msg.setText(f"Fehler beim Indexing:\n\n{error_message}")
        indexing_error_msg.setIcon(QMessageBox.Icon.Critical)
        indexing_error_msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        indexing_error_msg.setStyleSheet("""
            QMessageBox {
                background-color: #1a2633;
                color: white;
                font-size: 14px;
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
                min-height: 30px;
            }
            QPushButton:hover {
                background-color: #1a5a9e;
            }
        """)
        indexing_error_msg.button(QMessageBox.StandardButton.Ok).setText("OK")
        indexing_error_msg.exec()
        
        # Hide progress indicators
        self.progress_bar.setVisible(False)
        self.progress_label.setVisible(False)
        self.refresh_button.setEnabled(True)

    def populate_table(self):
        """Populate the table with tumorboard data"""
        self.bills_table.setRowCount(len(self.completed_tumorboards))
        
        for row, tumorboard in enumerate(self.completed_tumorboards):
            # Tumorboard name - make clickable
            tumorboard_item = QTableWidgetItem(tumorboard['tumorboard'])
            tumorboard_item.setFont(QFont("Helvetica", 11, QFont.Weight.Bold))
            tumorboard_item.setForeground(Qt.GlobalColor.cyan)  # Make it look clickable
            tumorboard_item.setData(Qt.ItemDataRole.UserRole, tumorboard)  # Store tumorboard data
            self.bills_table.setItem(row, 0, tumorboard_item)
            
            # Date
            date_item = QTableWidgetItem(tumorboard['datum'])
            date_item.setFont(QFont("Helvetica", 11))
            self.bills_table.setItem(row, 1, date_item)
            
            # Case count
            count_item = QTableWidgetItem(str(tumorboard['anzahl_faelle']))
            count_item.setFont(QFont("Helvetica", 11))
            count_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.bills_table.setItem(row, 2, count_item)
            
            # Billing status
            status_widget = self.create_status_widget(tumorboard)
            self.bills_table.setCellWidget(row, 3, status_widget)
            
            # Actions
            actions_widget = self.create_actions_widget(tumorboard, row)
            self.bills_table.setCellWidget(row, 4, actions_widget)
        
        # Resize rows to content
        self.bills_table.resizeRowsToContents()
        
        # Connect single-click signal (row, column) to open Excel viewer
        self.bills_table.cellClicked.connect(self.on_table_cell_clicked)

    def create_status_widget(self, tumorboard):
        """Create status widget for a tumorboard"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(1)  # Reduced spacing between widgets
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        if tumorboard['is_billed']:
            billing_info = tumorboard['billing_status']
            
            # Main status
            status_label = QLabel("✅ Abgerechnung erfolgt")
            status_label.setFont(QFont("Helvetica", 11, QFont.Weight.Bold))
            status_label.setStyleSheet("color: #32CD32;")
            status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(status_label)
            
            # Details - all in one line
            details_text = f"Art: {billing_info['art_der_abrechnung'].title()} | {billing_info['abgerechnet_am']} | {billing_info['benutzer']}"
            
            details_label = QLabel(details_text)
            details_label.setFont(QFont("Helvetica", 9))
            details_label.setStyleSheet("color: #CCCCCC;")
            details_label.setWordWrap(False)  # Prevent word wrapping
            details_label.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Center align the text
            layout.addWidget(details_label)
        else:
            status_label = QLabel("❌ Abrechnung ausstehend")
            status_label.setFont(QFont("Helvetica", 11, QFont.Weight.Bold))
            status_label.setStyleSheet("color: #DC143C;")
            status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(status_label)
        
        return widget

    def create_actions_widget(self, tumorboard, row):
        """Create actions widget for a tumorboard"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        if tumorboard['is_billed']:
            # Already billed - show status only
            billed_label = QLabel("Bereits abgerechnet")
            billed_label.setFont(QFont("Helvetica", 10))
            billed_label.setStyleSheet("color: #32CD32; font-style: italic;")
            layout.addWidget(billed_label)
        else:
            # Not billed - show action buttons
            # KISIM Script button
            script_button = QPushButton("Abrechnung mittels KISIM Script")
            script_button.setFixedHeight(28)
            script_button.setStyleSheet("""
                QPushButton {
                    background-color: #FF8C00;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 4px 8px;
                    font-size: 12px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #FFA500;
                }
                QPushButton:pressed {
                    background-color: #FF7F00;
                }
            """)
            script_button.clicked.connect(lambda: self.run_kisim_script(tumorboard, row))
            layout.addWidget(script_button)
            
            # Manual button
            manual_button = QPushButton("Manuell als abgerechnet markieren")
            manual_button.setFixedHeight(28)
            manual_button.setStyleSheet("""
                        QPushButton {
                            background-color: #114473;
                            color: white;
                            border: none;
                            border-radius: 4px;
                    padding: 4px 8px;
                    font-size: 12px;
                    font-weight: bold;
                        }
                        QPushButton:hover {
                            background-color: #1a5a9e;
                        }
                QPushButton:pressed {
                    background-color: #0d3355;
                }
            """)
            manual_button.clicked.connect(lambda: self.mark_manual_billing(tumorboard, row))
            layout.addWidget(manual_button)
        
        # No extra stretch to keep content centered
        return widget

    def run_kisim_script(self, tumorboard, row):
        """Run KISIM billing script for a tumorboard"""
        logging.info(f"Starting KISIM billing for {tumorboard['tumorboard']} on {tumorboard['datum']}")
        
        # Show confirmation dialog
        dialog = KisimBillingDialog(tumorboard['tumorboard'], tumorboard['datum'], self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            logging.info("User confirmed KISIM billing automation")
            self.execute_billing_script(tumorboard, row)
        else:
            logging.info("User cancelled KISIM billing automation")

    def execute_billing_script(self, tumorboard, row):
        """Execute the billing automation script"""
        try:
            # Get the script path
            script_path = Path(__file__).parent.parent / "scripts" / "abrechnung.py"
            
            if not script_path.exists():
                # Warning message with custom styling
                warning_msg = QMessageBox(self)
                warning_msg.setWindowTitle("Skript nicht gefunden")
                warning_msg.setText(f"Das Abrechnungsskript wurde nicht gefunden:\n{script_path}")
                warning_msg.setIcon(QMessageBox.Icon.Warning)
                warning_msg.setStandardButtons(QMessageBox.StandardButton.Ok)
                warning_msg.setStyleSheet("""
                    QMessageBox {
                        background-color: #1a2633;
                        color: white;
                        font-size: 14px;
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
                        min-height: 30px;
                    }
                    QPushButton:hover {
                        background-color: #1a5a9e;
                    }
                """)
                warning_msg.button(QMessageBox.StandardButton.Ok).setText("OK")
                warning_msg.exec()
                logging.error(f"Billing script not found: {script_path}")
                return
                
            logging.info(f"Executing billing script: {script_path}")
            
            # Show progress message
            progress_msg = QMessageBox()
            progress_msg.setWindowTitle("KISIM Abrechnung")
            progress_msg.setText("Die automatisierte Abrechnung wird durchgeführt...\n\nBitte warten Sie.")
            progress_msg.setStandardButtons(QMessageBox.StandardButton.NoButton)
            progress_msg.setModal(True)
            progress_msg.show()
            
            # Process events to show the message
            from PyQt6.QtWidgets import QApplication
            QApplication.processEvents()
            
            try:
                # Execute the script
                result = subprocess.run([
                    "python", str(script_path)
                ], capture_output=True, text=True, timeout=300)  # 5 minute timeout
                
                # Close progress message
                progress_msg.close()
                
                if result.returncode == 0:
                    # Success - mark as billed with script
                    try:
                        self.billing_tracker.mark_as_billed(
                            tumorboard['tumorboard'], 
                            tumorboard['datum'], 
                            "script"
                        )
                        
                        # Update the tumorboard info and refresh the row
                        tumorboard['billing_status'] = self.billing_tracker.get_billing_status(
                            tumorboard['tumorboard'], tumorboard['datum'])
                        tumorboard['is_billed'] = True
                        
                        # Update the table row
                        self.update_table_row(row, tumorboard)
                        
                        logging.info("KISIM billing script executed successfully")
                        
                        # Success message with custom styling
                        success_msg = QMessageBox(self)
                        success_msg.setWindowTitle("Abrechnung erfolgreich")
                        success_msg.setText("Die automatisierte KISIM-Abrechnung wurde erfolgreich durchgeführt.")
                        success_msg.setIcon(QMessageBox.Icon.Information)
                        success_msg.setStandardButtons(QMessageBox.StandardButton.Ok)
                        success_msg.setStyleSheet("""
                            QMessageBox {
                                background-color: #1a2633;
                                color: white;
                                font-size: 14px;
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
                                min-height: 30px;
                            }
                            QPushButton:hover {
                                background-color: #1a5a9e;
                            }
                        """)
                        success_msg.button(QMessageBox.StandardButton.Ok).setText("OK")
                        success_msg.exec()
                        
                    except Exception as e:
                        logging.error(f"Error updating billing status: {e}")
                        
                        # Warning message with custom styling
                        warning_msg = QMessageBox(self)
                        warning_msg.setWindowTitle("Status-Update Fehler")
                        warning_msg.setText(f"Die Abrechnung war erfolgreich, aber der Status konnte nicht aktualisiert werden:\n\n{str(e)}")
                        warning_msg.setIcon(QMessageBox.Icon.Warning)
                        warning_msg.setStandardButtons(QMessageBox.StandardButton.Ok)
                        warning_msg.setStyleSheet("""
                            QMessageBox {
                                background-color: #1a2633;
                                color: white;
                                font-size: 14px;
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
                                min-height: 30px;
                            }
                            QPushButton:hover {
                                background-color: #1a5a9e;
                            }
                        """)
                        warning_msg.button(QMessageBox.StandardButton.Ok).setText("OK")
                        warning_msg.exec()
                else:
                    # Error
                    error_msg = result.stderr if result.stderr else "Unbekannter Fehler"
                    logging.error(f"Billing script failed: {error_msg}")
                    
                    # Error message with custom styling
                    error_msg_box = QMessageBox(self)
                    error_msg_box.setWindowTitle("Abrechnung fehlgeschlagen")
                    error_msg_box.setText(f"Die automatisierte Abrechnung ist fehlgeschlagen:\n\n{error_msg}")
                    error_msg_box.setIcon(QMessageBox.Icon.Critical)
                    error_msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
                    error_msg_box.setStyleSheet("""
                        QMessageBox {
                            background-color: #1a2633;
                            color: white;
                            font-size: 14px;
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
                            min-height: 30px;
                        }
                        QPushButton:hover {
                            background-color: #1a5a9e;
                        }
                    """)
                    error_msg_box.button(QMessageBox.StandardButton.Ok).setText("OK")
                    error_msg_box.exec()
                    
            except subprocess.TimeoutExpired:
                progress_msg.close()
                logging.error("Billing script timeout")
                
                # Timeout message with custom styling
                timeout_msg = QMessageBox(self)
                timeout_msg.setWindowTitle("Timeout")
                timeout_msg.setText("Die Abrechnung dauerte zu lange und wurde abgebrochen.")
                timeout_msg.setIcon(QMessageBox.Icon.Critical)
                timeout_msg.setStandardButtons(QMessageBox.StandardButton.Ok)
                timeout_msg.setStyleSheet("""
                    QMessageBox {
                        background-color: #1a2633;
                        color: white;
                        font-size: 14px;
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
                        min-height: 30px;
                    }
                    QPushButton:hover {
                        background-color: #1a5a9e;
                    }
                """)
                timeout_msg.button(QMessageBox.StandardButton.Ok).setText("OK")
                timeout_msg.exec()
                                   
            except Exception as e:
                progress_msg.close()
                logging.error(f"Error executing billing script: {e}")
                
                # Error message with custom styling
                exec_error_msg = QMessageBox(self)
                exec_error_msg.setWindowTitle("Ausführungsfehler")
                exec_error_msg.setText(f"Fehler bei der Ausführung der Abrechnung:\n\n{str(e)}")
                exec_error_msg.setIcon(QMessageBox.Icon.Critical)
                exec_error_msg.setStandardButtons(QMessageBox.StandardButton.Ok)
                exec_error_msg.setStyleSheet("""
                    QMessageBox {
                        background-color: #1a2633;
                        color: white;
                        font-size: 14px;
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
                        min-height: 30px;
                    }
                    QPushButton:hover {
                        background-color: #1a5a9e;
                    }
                """)
                exec_error_msg.button(QMessageBox.StandardButton.Ok).setText("OK")
                exec_error_msg.exec()
                
        except Exception as e:
            logging.error(f"Error in execute_billing_script: {e}")
            
            # Unexpected error message with custom styling
            unexpected_error_msg = QMessageBox(self)
            unexpected_error_msg.setWindowTitle("Unerwarteter Fehler")
            unexpected_error_msg.setText(f"Ein unerwarteter Fehler ist aufgetreten:\n\n{str(e)}")
            unexpected_error_msg.setIcon(QMessageBox.Icon.Critical)
            unexpected_error_msg.setStandardButtons(QMessageBox.StandardButton.Ok)
            unexpected_error_msg.setStyleSheet("""
                QMessageBox {
                    background-color: #1a2633;
                    color: white;
                    font-size: 14px;
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
                    min-height: 30px;
                }
                QPushButton:hover {
                    background-color: #1a5a9e;
                }
            """)
            unexpected_error_msg.button(QMessageBox.StandardButton.Ok).setText("OK")
            unexpected_error_msg.exec()

    def mark_manual_billing(self, tumorboard, row):
        """Mark tumorboard as manually billed"""
        # Show confirmation dialog with custom styling
        reply_box = QMessageBox(self)
        reply_box.setWindowTitle("Manuelle Abrechnung bestätigen")
        reply_box.setText(f"Möchten Sie das Tumorboard '{tumorboard['tumorboard']}' "
                         f"vom {tumorboard['datum']} als manuell abgerechnet markieren?")
        reply_box.setIcon(QMessageBox.Icon.Question)
        reply_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        reply_box.setDefaultButton(QMessageBox.StandardButton.No)
        
        # Apply custom styling
        reply_box.setStyleSheet("""
            QMessageBox {
                background-color: #1a2633;
                color: white;
                font-size: 14px;
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
                min-height: 30px;
            }
            QPushButton:hover {
                background-color: #1a5a9e;
            }
            QPushButton:pressed {
                background-color: #0d3355;
            }
        """)
        
        # Set button text to German
        reply_box.button(QMessageBox.StandardButton.Yes).setText("Ja")
        reply_box.button(QMessageBox.StandardButton.No).setText("Nein")
        
        reply = reply_box.exec()
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                # Mark as billed with user
                self.billing_tracker.mark_as_billed(
                    tumorboard['tumorboard'], 
                    tumorboard['datum'], 
                    "user"
                )
                
                # Update the tumorboard info and refresh the row
                tumorboard['billing_status'] = self.billing_tracker.get_billing_status(
                    tumorboard['tumorboard'], tumorboard['datum'])
                tumorboard['is_billed'] = True
                
                # Update the table row
                self.update_table_row(row, tumorboard)
                
                logging.info(f"Manually marked as billed: {tumorboard['tumorboard']} on {tumorboard['datum']}")
                
                # Success message with custom styling
                success_msg = QMessageBox(self)
                success_msg.setWindowTitle("Erfolgreich markiert")
                success_msg.setText("Das Tumorboard wurde erfolgreich als abgerechnet markiert.")
                success_msg.setIcon(QMessageBox.Icon.Information)
                success_msg.setStandardButtons(QMessageBox.StandardButton.Ok)
                success_msg.setStyleSheet("""
                    QMessageBox {
                        background-color: #1a2633;
                        color: white;
                        font-size: 14px;
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
                        min-height: 30px;
                    }
                    QPushButton:hover {
                        background-color: #1a5a9e;
                    }
                """)
                success_msg.button(QMessageBox.StandardButton.Ok).setText("OK")
                success_msg.exec()
                
            except Exception as e:
                logging.error(f"Error marking manual billing: {e}")
                
                # Error message with custom styling
                error_msg = QMessageBox(self)
                error_msg.setWindowTitle("Fehler")
                error_msg.setText(f"Fehler beim Markieren der Abrechnung:\n\n{str(e)}")
                error_msg.setIcon(QMessageBox.Icon.Critical)
                error_msg.setStandardButtons(QMessageBox.StandardButton.Ok)
                error_msg.setStyleSheet("""
                    QMessageBox {
                        background-color: #1a2633;
                        color: white;
                        font-size: 14px;
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
                        min-height: 30px;
                    }
                    QPushButton:hover {
                        background-color: #1a5a9e;
                    }
                """)
                error_msg.button(QMessageBox.StandardButton.Ok).setText("OK")
                error_msg.exec()

    def update_table_row(self, row, tumorboard):
        """Update a single table row"""
        # Update status widget
        status_widget = self.create_status_widget(tumorboard)
        self.bills_table.setCellWidget(row, 3, status_widget)
        
        # Update actions widget
        actions_widget = self.create_actions_widget(tumorboard, row)
        self.bills_table.setCellWidget(row, 4, actions_widget)
        
        # Resize row to content
        self.bills_table.resizeRowToContents(row)

    def on_table_cell_clicked(self, row: int, column: int):
        """Handle single-click on any cell to open the Excel viewer.

        We ignore clicks on the action buttons of un‐billed Einträge,
        da dort eigene Buttons hinterlegt sind (Script/Manuell)."""
        try:
            # If Actions-Spalte (index 4) und der Eintrag ist noch NICHT abgerechnet,
            # dann könnten Buttons vorhanden sein → klicke nicht automatisch durch.
            if column == 4:
                tumorboard = self.completed_tumorboards[row] if row < len(self.completed_tumorboards) else None
                if tumorboard and not tumorboard.get('is_billed', False):
                    return  # dort gibt es Buttons – nichts tun

            # Sicherheit: Index prüfen
            if 0 <= row < len(self.completed_tumorboards):
                tumorboard_data = self.completed_tumorboards[row]
                self.open_excel_viewer(tumorboard_data)
        except Exception as e:
            logging.error(f"Error handling single click: {e}")

    def open_excel_viewer(self, tumorboard_data):
        """Open Excel viewer for the selected tumorboard"""
        try:
            logging.info(f"Opening Excel viewer for {tumorboard_data['tumorboard']} on {tumorboard_data['datum']}")
            
            # Import the Excel viewer backoffice page
            from pages.excel_viewer_backoffice_page import ExcelViewerBackofficePage
            
            # Create the Excel viewer page
            excel_viewer_page = ExcelViewerBackofficePage(
                self.main_window,
                tumorboard_data['tumorboard'],
                tumorboard_data['datum'],
                source_page="leistungsabrechnungen"  # Indicate this came from billing page
            )
            
            # Add the page to the stacked widget and navigate to it
            self.main_window.stacked_widget.addWidget(excel_viewer_page)
            self.main_window.stacked_widget.setCurrentWidget(excel_viewer_page)
            
            logging.info(f"Successfully navigated to Excel viewer for {tumorboard_data['tumorboard']} on {tumorboard_data['datum']}")
            
        except Exception as e:
            logging.error(f"Error opening Excel viewer: {e}")
            
            # Error message with custom styling
            excel_error_msg = QMessageBox(self)
            excel_error_msg.setWindowTitle("Fehler")
            excel_error_msg.setText(f"Fehler beim Öffnen der Excel-Ansicht:\n\n{str(e)}")
            excel_error_msg.setIcon(QMessageBox.Icon.Critical)
            excel_error_msg.setStandardButtons(QMessageBox.StandardButton.Ok)
            excel_error_msg.setStyleSheet("""
                QMessageBox {
                    background-color: #1a2633;
                    color: white;
                    font-size: 14px;
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
                    min-height: 30px;
                }
                QPushButton:hover {
                    background-color: #1a5a9e;
                }
            """)
            excel_error_msg.button(QMessageBox.StandardButton.Ok).setText("OK")
            excel_error_msg.exec()

    def go_back(self):
        """Navigate back to the backoffice page"""
        logging.info("Navigating back to backoffice page")
        self.main_window.show_page("backoffice") 