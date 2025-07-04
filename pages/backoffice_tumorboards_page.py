from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                             QFrame, QTableWidget, QTableWidgetItem, QHeaderView,
                             QComboBox, QDateEdit, QCheckBox, QMessageBox, QProgressBar)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QDate, QTimer
from PyQt6.QtGui import QFont
import os
import logging
import re
from pathlib import Path
from datetime import datetime, date

class TumorboardIndexingThread(QThread):
    """Thread for detailed indexing of completed tumorboards"""
    progress_update = pyqtSignal(str)  # Progress message
    indexing_complete = pyqtSignal(list)  # List of completed tumorboards
    error_occurred = pyqtSignal(str)  # Error message

    def __init__(self):
        super().__init__()
        #self.tumorboards_path = Path("K:/RAO_Projekte/App/tumorboards")
        self.tumorboards_path = Path("C:/Users/marku/tumorboards")
        self.completed_tumorboards = []
        self._should_stop = False
        self._max_runtime = 300  # 5 minutes timeout
    
    def stop_indexing(self):
        """Stop the indexing process"""
        print("DEBUG: Stop indexing requested")
        self._should_stop = True

    def run(self):
        """Run the detailed indexing process"""
        import time
        start_time = time.time()
        
        try:
            print("DEBUG: Starting detailed indexing process...")
            self.progress_update.emit("Starte detailliertes Indexing...")
            logging.info("Starting detailed tumorboard indexing...")
            
            # Check for stop signal
            if self._should_stop:
                print("DEBUG: Stop signal received before start")
                return
            
            # Check if the path is accessible
            print(f"DEBUG: Checking path: {self.tumorboards_path}")
            if not self.tumorboards_path.exists():
                error_msg = f"Tumorboards path does not exist: {self.tumorboards_path}"
                print(f"DEBUG ERROR: {error_msg}")
                logging.error(error_msg)
                self.error_occurred.emit("Keine Verbindung zum Laufwerk K:\\RAO_Daten verfügbar")
                return
            
            print(f"DEBUG: Path exists, continuing with indexing...")
            self.completed_tumorboards = []
            
            # Get all entity folders (exclude _Backoffice and __SQLite_database)
            try:
                print(f"DEBUG: Getting entity folders from: {self.tumorboards_path}")
                all_folders = list(self.tumorboards_path.iterdir())
                print(f"DEBUG: Found {len(all_folders)} total items")
                
                entity_folders = [f for f in all_folders 
                                if f.is_dir() and not f.name.startswith('_') and not f.name.startswith('__')]
                
                print(f"DEBUG: Filtered to {len(entity_folders)} entity folders")
                for folder in entity_folders:
                    print(f"DEBUG: Entity folder: {folder.name}")
                    
            except Exception as e:
                error_msg = f"Error getting entity folders: {e}"
                print(f"DEBUG ERROR: {error_msg}")
                logging.error(error_msg)
                self.error_occurred.emit(f"Fehler beim Abrufen der Entitäts-Ordner: {str(e)}")
                return
            
            total_entities = len(entity_folders)
            logging.info(f"Indexing {total_entities} tumorboard entities for completed tumorboards")
            
            for i, entity_folder in enumerate(entity_folders):
                # Check for stop signal and timeout
                current_time = time.time()
                if self._should_stop:
                    print("DEBUG: Stop signal received during processing")
                    return
                    
                if current_time - start_time > self._max_runtime:
                    error_msg = f"Indexing timeout after {self._max_runtime} seconds"
                    print(f"DEBUG: {error_msg}")
                    logging.error(error_msg)
                    self.error_occurred.emit("Indexing-Timeout: Der Vorgang dauerte zu lange.")
                    return
                
                entity_name = entity_folder.name
                print(f"DEBUG: Processing entity {i+1}/{total_entities}: {entity_name}")
                self.progress_update.emit(f"Prüfe {entity_name} ({i+1}/{total_entities})...")
                
                try:
                    # Check if entity folder still exists and is accessible
                    print(f"DEBUG: Checking if entity folder exists: {entity_folder}")
                    if not entity_folder.exists():
                        print(f"DEBUG: Entity folder no longer exists: {entity_folder}")
                        continue
                    
                    if not entity_folder.is_dir():
                        print(f"DEBUG: Path is not a directory: {entity_folder}")
                        continue
                    
                    # Look for date folders in this entity
                    print(f"DEBUG: Getting date folders from: {entity_folder}")
                    try:
                        date_folder_items = list(entity_folder.iterdir())
                        print(f"DEBUG: Found {len(date_folder_items)} items in {entity_name}")
                        
                        date_folders = [f for f in date_folder_items if f.is_dir()]
                        print(f"DEBUG: Filtered to {len(date_folders)} directories in {entity_name}")
                        
                    except PermissionError as pe:
                        print(f"DEBUG: Permission error iterating {entity_folder}: {pe}")
                        logging.warning(f"Permission denied iterating {entity_folder}: {pe}")
                        continue
                    except Exception as e:
                        print(f"DEBUG: Error iterating {entity_folder}: {e}")
                        logging.error(f"Error iterating {entity_folder}: {e}")
                        continue
                    
                    # Process each date folder with additional safety checks
                    if len(date_folders) == 0:
                        print(f"DEBUG: No date folders found in {entity_name}, skipping...")
                        continue
                        
                    for j, date_folder in enumerate(date_folders):
                        print(f"DEBUG: Processing date folder {j+1}/{len(date_folders)}: {date_folder.name}")
                        
                        try:
                            # Additional safety check
                            if not date_folder.exists() or not date_folder.is_dir():
                                print(f"DEBUG: Date folder {date_folder} not valid, skipping...")
                                continue
                                
                            # Check if folder name matches date format (dd.mm.yyyy)
                            print(f"DEBUG: Checking date format for: {date_folder.name}")
                            if self.is_valid_date_format(date_folder.name):
                                print(f"DEBUG: Valid date format: {date_folder.name}")
                                
                                # Check for timestamp file in this date folder
                                print(f"DEBUG: Looking for timestamp files in: {date_folder}")
                                try:
                                    # Use try-except for glob operation
                                    timestamp_files = []
                                    try:
                                        timestamp_files = list(date_folder.glob("*timestamp*"))
                                    except Exception as glob_e:
                                        print(f"DEBUG: Error in glob operation for {date_folder}: {glob_e}")
                                        continue
                                        
                                    print(f"DEBUG: Found {len(timestamp_files)} timestamp files")
                                    
                                    if timestamp_files:
                                        print(f"DEBUG: Timestamp files found: {[f.name for f in timestamp_files]}")
                                        
                                        # Check for Excel file with matching date
                                        excel_file = date_folder / f"{date_folder.name}.xlsx"
                                        print(f"DEBUG: Checking for Excel file: {excel_file}")
                                        
                                        try:
                                            if excel_file.exists() and excel_file.is_file():
                                                print(f"DEBUG: Excel file exists, adding completed tumorboard: {entity_name} - {date_folder.name}")
                                                # This is a completed tumorboard
                                                self.completed_tumorboards.append({
                                                    'date': date_folder.name,
                                                    'entity': entity_name,
                                                    'date_folder_path': date_folder,
                                                    'excel_path': excel_file,
                                                    'timestamp_file': timestamp_files[0]
                                                })
                                                logging.info(f"Found completed tumorboard: {entity_name} - {date_folder.name}")
                                            else:
                                                print(f"DEBUG: Excel file does not exist or is not a file: {excel_file}")
                                        except Exception as excel_e:
                                            print(f"DEBUG: Error checking Excel file {excel_file}: {excel_e}")
                                            continue
                                    else:
                                        print(f"DEBUG: No timestamp files found in: {date_folder}")
                                        
                                except Exception as e:
                                    print(f"DEBUG: Error processing timestamp/excel files in {date_folder}: {e}")
                                    logging.error(f"Error processing timestamp/excel files in {date_folder}: {e}")
                                    continue
                            else:
                                print(f"DEBUG: Invalid date format: {date_folder.name}")
                                
                        except Exception as e:
                            print(f"DEBUG: Error processing date folder {date_folder}: {e}")
                            logging.error(f"Error processing date folder {date_folder}: {e}")
                            continue
                            
                        # Yield control to prevent UI freezing
                        self.msleep(1)
                
                except PermissionError as pe:
                    print(f"DEBUG: Permission denied accessing {entity_folder}: {pe}")
                    logging.warning(f"Permission denied accessing {entity_folder}: {pe}")
                    continue
                except Exception as e:
                    print(f"DEBUG: Error processing entity {entity_folder}: {e}")
                    logging.error(f"Error processing entity {entity_folder}: {e}")
                    continue
            
            print(f"DEBUG: Indexing completed successfully. Found {len(self.completed_tumorboards)} completed tumorboards")
            self.progress_update.emit(f"Indexing abgeschlossen! {len(self.completed_tumorboards)} abgeschlossene Tumorboards gefunden.")
            self.indexing_complete.emit(self.completed_tumorboards)
            
        except Exception as e:
            print(f"DEBUG: Critical error during detailed indexing: {e}")
            logging.error(f"Critical error during detailed indexing: {e}")
            import traceback
            traceback.print_exc()
            self.error_occurred.emit(f"Fehler beim detaillierten Indexing: {str(e)}")
    
    def is_valid_date_format(self, folder_name):
        """Check if folder name matches the date format dd.mm.yyyy"""
        try:
            date_pattern = r'^\d{2}\.\d{2}\.\d{4}$'
            result = re.match(date_pattern, folder_name) is not None
            print(f"DEBUG: Date format check for '{folder_name}': {result}")
            return result
        except Exception as e:
            print(f"DEBUG: Error in date format check for '{folder_name}': {e}")
            return False

class BackofficeTumorboardsPage(QWidget):
    def __init__(self, main_window):
        print("DEBUG: Initializing BackofficeTumorboardsPage...")
        super().__init__()
        logging.info("Initializing BackofficeTumorboardsPage...")
        
        try:
            print("DEBUG: Setting up instance variables...")
            self.main_window = main_window
            self.indexing_thread = None
            self.completed_tumorboards = []
            self.filtered_tumorboards = []
            
            print("DEBUG: Setting up UI...")
            self.setup_ui()
            
            print("DEBUG: Scheduling indexing start...")
            # Start indexing automatically when page is loaded
            QTimer.singleShot(100, self.start_indexing)
            
            print("DEBUG: BackofficeTumorboardsPage initialization complete")
            logging.info("BackofficeTumorboardsPage initialization complete.")
            
        except Exception as e:
            print(f"DEBUG: Error in BackofficeTumorboardsPage.__init__: {e}")
            logging.error(f"Error in BackofficeTumorboardsPage.__init__: {e}")
            import traceback
            traceback.print_exc()
            raise

    def setup_ui(self):
        """Setup the user interface"""
        # Main layout with optimized spacing
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 5, 20, 15)  # Reduced margins
        main_layout.setSpacing(12)  # Tighter spacing
        self.setLayout(main_layout)

        # Title - more compact
        title_label = QLabel("Abgeschlossene Tumorboards")
        title_label.setFont(QFont("Helvetica", 22, QFont.Weight.Bold))  # Smaller font
        title_label.setStyleSheet("color: white; margin-bottom: 8px;")  # Reduced margin
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)

        # Indexing status section - compact design
        self.indexing_frame = QFrame()
        self.indexing_frame.setStyleSheet("""
            QFrame {
                background-color: #232F3B;
                border-radius: 10px;
                padding: 5px;
                margin-bottom: 5px;
            }
        """)
        indexing_layout = QVBoxLayout(self.indexing_frame)
        indexing_layout.setSpacing(8)  # Tighter spacing within frame
        
        self.indexing_label = QLabel("Lade abgeschlossene Tumorboards...")
        self.indexing_label.setFont(QFont("Helvetica", 13))  # Slightly smaller
        self.indexing_label.setStyleSheet("color: #00BFFF; margin-bottom: 5px;")
        indexing_layout.addWidget(self.indexing_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #425061;
                border-radius: 5px;
                text-align: center;
                color: white;
                background-color: #19232D;
            }
            QProgressBar::chunk {
                background-color: #3292ea;
                border-radius: 3px;
            }
        """)
        indexing_layout.addWidget(self.progress_bar)
        
        main_layout.addWidget(self.indexing_frame)

        # Filter section - streamlined design
        self.filter_frame = QFrame()
        self.filter_frame.setStyleSheet("""
            QFrame {
                background-color: #232F3B;
                border-radius: 8px;
                padding: 5px;
                margin-bottom: 3px;
            }
        """)
        self.filter_frame.setVisible(False)  # Hidden until indexing is complete
        
        filter_layout = QVBoxLayout(self.filter_frame)
        filter_layout.setSpacing(3)  # Ultra-compact spacing
        filter_layout.setContentsMargins(10, 3, 3, 3)  # Minimal margins
        
        # Filter title - very compact
        filter_title = QLabel("Filter-Optionen")
        filter_title.setFont(QFont("Helvetica", 12, QFont.Weight.Bold))  # Even smaller
        filter_title.setStyleSheet("color: white; margin-bottom: 0px;")
        filter_layout.addWidget(filter_title)
        
        # Filter controls layout - perfect alignment
        filter_controls_layout = QHBoxLayout()
        filter_controls_layout.setSpacing(25)
        filter_controls_layout.setAlignment(Qt.AlignmentFlag.AlignTop)  # Top-align all sections
        filter_controls_layout.setContentsMargins(20, 0, 0, 0)  # Add 20px left margin to shift controls right
        
        # Zeitintervall section
        date_section = QVBoxLayout()
        date_section.setSpacing(3)  # Slightly more space for better readability
        date_section.setAlignment(Qt.AlignmentFlag.AlignTop)
        date_section.setContentsMargins(0, 0, 0, 0)  # Remove any default margins
        
        date_label = QLabel("Zeitintervall:")
        date_label.setStyleSheet("color: white; font-weight: bold; font-size: 13px; min-height: 22px;")
        date_label.setAlignment(Qt.AlignmentFlag.AlignBottom)  # Baseline align
        date_section.addWidget(date_label)
        
        # Date controls - aligned baseline with ComboBox
        date_controls_container = QHBoxLayout()
        date_controls_container.setSpacing(6)
        date_controls_container.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        date_controls_container.setContentsMargins(0, 0, 0, 0)  # Remove margins
        
        von_label = QLabel("Von:")
        von_label.setStyleSheet("color: #CCCCCC; font-size: 12px;")
        von_label.setAlignment(Qt.AlignmentFlag.AlignVCenter)  # Vertical center with DateEdit
        date_controls_container.addWidget(von_label)
        
        self.date_from = QDateEdit()
        self.date_from.setDate(QDate.currentDate().addMonths(-6))
        self.date_from.setStyleSheet(self.get_date_edit_style())
        self.date_from.setFixedHeight(32)  # Ensure proper height
        self.date_from.setMinimumWidth(85)  # Ensure minimum width
        self.date_from.dateChanged.connect(self.apply_filters)
        date_controls_container.addWidget(self.date_from)
        
        bis_label = QLabel("Bis:")
        bis_label.setStyleSheet("color: #CCCCCC; font-size: 12px;")
        bis_label.setAlignment(Qt.AlignmentFlag.AlignVCenter)  # Vertical center with DateEdit
        date_controls_container.addWidget(bis_label)
        
        self.date_to = QDateEdit()
        self.date_to.setDate(QDate.currentDate())
        self.date_to.setStyleSheet(self.get_date_edit_style())
        self.date_to.setFixedHeight(32)  # Ensure proper height
        self.date_to.setMinimumWidth(85)  # Ensure minimum width
        self.date_to.dateChanged.connect(self.apply_filters)
        date_controls_container.addWidget(self.date_to)
        
        # Create a widget with explicit size constraints for baseline alignment
        date_controls_widget = QWidget()
        date_controls_widget.setLayout(date_controls_container)
        date_controls_widget.setFixedHeight(32)  # Increased height to prevent cut-off
        date_section.addWidget(date_controls_widget)
        
        filter_controls_layout.addLayout(date_section)
        
        # Entity filter section - consistent structure
        entity_section = QVBoxLayout()
        entity_section.setSpacing(3)  # Slightly more space for better readability
        entity_section.setAlignment(Qt.AlignmentFlag.AlignTop)
        entity_section.setContentsMargins(0, 0, 0, 0)  # Remove any default margins
        
        entity_label = QLabel("Tumorboard-Entität:")
        entity_label.setStyleSheet("color: white; font-weight: bold; font-size: 13px; min-height: 22px;")
        entity_label.setAlignment(Qt.AlignmentFlag.AlignBottom)  # Baseline align
        entity_section.addWidget(entity_label)
        
        self.entity_combo = QComboBox()
        self.entity_combo.setStyleSheet(self.get_combo_style())
        self.entity_combo.currentTextChanged.connect(self.apply_filters)
        self.entity_combo.setFixedHeight(32)  # Explicit height for alignment
        entity_section.addWidget(self.entity_combo)
        
        filter_controls_layout.addLayout(entity_section)
        
        # Reset button section - consistent structure
        reset_section = QVBoxLayout()
        reset_section.setSpacing(3)  # Slightly more space for better readability
        reset_section.setAlignment(Qt.AlignmentFlag.AlignTop)
        reset_section.setContentsMargins(0, 0, 0, 0)  # Remove any default margins
        
        # Spacer label with exact same styling as other labels
        spacer_label = QLabel("")
        spacer_label.setStyleSheet("color: white; font-weight: bold; font-size: 13px; min-height: 22px;")
        spacer_label.setAlignment(Qt.AlignmentFlag.AlignBottom)  # Baseline align
        reset_section.addWidget(spacer_label)
        
        self.reset_filter_button = QPushButton("Zurücksetzen")
        self.reset_filter_button.setStyleSheet("""
            QPushButton {
                background-color: #114473;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 4px 4px;
                font-weight: bold;
                font-size: 11px;
                min-height: 26px;
                max-height: 26px;
                line-height: 20px;
            }
            QPushButton:hover {
                background-color: #1a5a9e;
            }
        """)
        self.reset_filter_button.clicked.connect(self.reset_filters)
        self.reset_filter_button.setFixedHeight(32)  # Explicit height for alignment
        reset_section.addWidget(self.reset_filter_button)
        
        filter_controls_layout.addLayout(reset_section)
        filter_controls_layout.addStretch()
        
        filter_layout.addLayout(filter_controls_layout)
        main_layout.addWidget(self.filter_frame)

        # Table section - optimized design
        self.table_frame = QFrame()
        self.table_frame.setStyleSheet("""
            QFrame {
                background-color: #19232D;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        self.table_frame.setVisible(False)  # Hidden until indexing is complete
        
        table_layout = QVBoxLayout(self.table_frame)
        table_layout.setSpacing(8)  # Tighter spacing
        
        # Results info - more compact
        self.results_label = QLabel("")
        self.results_label.setFont(QFont("Helvetica", 11))  # Smaller font
        self.results_label.setStyleSheet("color: #00BFFF; margin-bottom: 5px;")
        table_layout.addWidget(self.results_label)
        
        # Create table
        self.tumorboards_table = QTableWidget()
        self.tumorboards_table.setColumnCount(2)
        self.tumorboards_table.setHorizontalHeaderLabels(["Datum", "Tumorboard"])
        
        # Table styling - modern and compact
        self.tumorboards_table.setStyleSheet("""
            QTableWidget {
                background-color: #232F3B;
                alternate-background-color: #2A3642;
                selection-background-color: #3292ea;
                gridline-color: #425061;
                color: white;
                border: 1px solid #425061;
                border-radius: 4px;
            }
            QTableWidget::item {
                padding: 12px 12px;
                border-bottom: 1px solid #425061;
                font-size: 11px;
            }
            QTableWidget::item:selected {
                background-color: #3292ea;
                color: white;
            }
            QTableWidget::item:hover {
                background-color: #2d4050;
            }
            QHeaderView::section {
                background-color: #1a2633;
                color: white;
                padding: 8px 8px;
                font-weight: bold;
                font-size: 13px;
                height: 35px;
                min-height: 35px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                text-align: center;
            }
            QHeaderView::section:hover {
                background-color: #233140;
            }
        """)
        
        # Table properties
        self.tumorboards_table.setAlternatingRowColors(True)
        self.tumorboards_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tumorboards_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tumorboards_table.setSortingEnabled(True)
        
        # Configure headers
        horizontal_header = self.tumorboards_table.horizontalHeader()
        horizontal_header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # Date column
        horizontal_header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Entity column
        horizontal_header.setFixedHeight(70)  # Ensure proper header height
        horizontal_header.setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)  # Center align header text
        
        # Hide vertical header
        self.tumorboards_table.verticalHeader().setVisible(False)
        
        # Connect single-click to open Excel viewer
        self.tumorboards_table.itemClicked.connect(self.open_excel_viewer)
        
        table_layout.addWidget(self.tumorboards_table)
        main_layout.addWidget(self.table_frame)

    def get_date_edit_style(self):
        """Get styling for date edit widgets - wider, no arrows, proper height"""
        return """
            QDateEdit {
                background-color: #232F3B;
                color: white;
                border: 1px solid #425061;
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 12px;
                min-height: 20px;
                max-height: 20px;
                min-width: 85px;
                line-height: 20px;
            }
            QDateEdit:focus {
                border: 2px solid #3292ea;
            }
            QDateEdit::up-button {
                subcontrol-origin: border;
                subcontrol-position: top right;
                width: 0px;
                border-left-width: 0px;
                border-left-color: darkgray;
                border-left-style: solid;
                border-top-right-radius: 3px;
                background: transparent;
            }
            QDateEdit::down-button {
                subcontrol-origin: border;
                subcontrol-position: bottom right;
                width: 0px;
                border-left-width: 0px;
                border-left-color: darkgray;
                border-left-style: solid;
                border-bottom-right-radius: 3px;
                background: transparent;
            }
            QDateEdit::drop-down {
                width: 0px;
                border: none;
                background: transparent;
            }
        """

    def get_combo_style(self):
        """Get styling for combo box widgets - aligned with DateEdit"""
        return """
            QComboBox {
                background-color: #232F3B;
                color: white;
                border: 1px solid #425061;
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 12px;
                min-width: 110px;
                min-height: 20px;
                max-height: 20px;
                line-height: 20px;
            }
            QComboBox:focus {
                border: 2px solid #3292ea;
            }
            QComboBox::drop-down {
                border: none;
                width: 16px;
            }
            QComboBox::down-arrow {
                width: 12px;
                height: 12px;
            }
            QComboBox QAbstractItemView {
                background-color: #232F3B;
                color: white;
                selection-background-color: #3292ea;
                border: 1px solid #425061;
                font-size: 11px;
            }
        """

    def start_indexing(self):
        """Start the indexing process"""
        print("DEBUG: Starting indexing process in BackofficeTumorboardsPage...")
        
        if self.indexing_thread is not None and self.indexing_thread.isRunning():
            print("DEBUG: Indexing thread already running, stopping it first...")
            self.stop_indexing()
            if not self.indexing_thread.wait(5000):  # Wait 5 seconds
                print("DEBUG: Forcing thread termination...")
                self.indexing_thread.terminate()
                self.indexing_thread.wait(2000)
        
        try:
            print("DEBUG: Setting up indexing UI...")
            logging.info("Starting detailed tumorboard indexing...")
            self.indexing_label.setText("Lade abgeschlossene Tumorboards...")
            self.progress_bar.setVisible(True)
            self.filter_frame.setVisible(False)
            self.table_frame.setVisible(False)
            
            print("DEBUG: Creating TumorboardIndexingThread...")
            self.indexing_thread = TumorboardIndexingThread()
            
            print("DEBUG: Connecting signals...")
            self.indexing_thread.progress_update.connect(self.update_indexing_progress)
            self.indexing_thread.indexing_complete.connect(self.on_indexing_complete)
            self.indexing_thread.error_occurred.connect(self.on_indexing_error)
            
            print("DEBUG: Starting indexing thread...")
            self.indexing_thread.start()
            print("DEBUG: Indexing thread started successfully")
            
            # Set up a safety timer to force-stop after 10 minutes
            QTimer.singleShot(600000, self.on_indexing_timeout)  # 10 minutes
            
        except Exception as e:
            print(f"DEBUG: Error in start_indexing: {e}")
            logging.error(f"Error in start_indexing: {e}")
            import traceback
            traceback.print_exc()
            self.indexing_label.setText(f"Fehler beim Start des Indexing: {str(e)}")
            self.progress_bar.setVisible(False)

    def stop_indexing(self):
        """Stop the current indexing process"""
        print("DEBUG: Stopping indexing process...")
        if self.indexing_thread is not None and self.indexing_thread.isRunning():
            self.indexing_thread.stop_indexing()

    def on_indexing_timeout(self):
        """Handle indexing timeout"""
        print("DEBUG: Indexing timeout triggered")
        if self.indexing_thread is not None and self.indexing_thread.isRunning():
            print("DEBUG: Forcing indexing stop due to timeout")
            self.indexing_thread.stop_indexing()
            self.indexing_thread.terminate()
            self.on_indexing_error("Indexing-Timeout: Der Vorgang wurde nach 10 Minuten abgebrochen.")

    def update_indexing_progress(self, message):
        """Update the indexing progress display"""
        print(f"DEBUG: Indexing progress update: {message}")
        self.indexing_label.setText(message)
        logging.info(f"Indexing progress: {message}")

    def on_indexing_complete(self, completed_tumorboards):
        """Handle indexing completion"""
        print(f"DEBUG: Indexing completed with {len(completed_tumorboards)} tumorboards")
        try:
            self.completed_tumorboards = completed_tumorboards
            self.filtered_tumorboards = completed_tumorboards.copy()
            
            print("DEBUG: Hiding indexing progress...")
            # Hide indexing progress
            self.indexing_frame.setVisible(False)
            
            print("DEBUG: Showing filter and table sections...")
            # Show filter and table sections
            self.filter_frame.setVisible(True)
            self.table_frame.setVisible(True)
            
            print("DEBUG: Populating entity filter...")
            # Populate entity filter
            self.populate_entity_filter()
            
            print("DEBUG: Populating table...")
            # Populate table
            self.populate_table()
            
            print("DEBUG: Indexing completion handling finished successfully")
            logging.info(f"Indexing completed successfully with {len(completed_tumorboards)} completed tumorboards")
            
        except Exception as e:
            print(f"DEBUG: Error in on_indexing_complete: {e}")
            logging.error(f"Error in on_indexing_complete: {e}")
            import traceback
            traceback.print_exc()

    def on_indexing_error(self, error_message):
        """Handle indexing errors"""
        print(f"DEBUG: Indexing error received: {error_message}")
        logging.error(f"Indexing error: {error_message}")
        
        try:
            print("DEBUG: Hiding progress elements...")
            # Hide progress elements
            self.indexing_frame.setVisible(False)
            
            print("DEBUG: Showing error message dialog...")
            # Show error message
            error_msg = QMessageBox(self)
            error_msg.setWindowTitle("Verbindungsfehler")
            error_msg.setText(error_message)
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
            print("DEBUG: Error dialog completed")
            
        except Exception as e:
            print(f"DEBUG: Error in on_indexing_error: {e}")
            logging.error(f"Error in on_indexing_error: {e}")
            import traceback
            traceback.print_exc()

    def populate_entity_filter(self):
        """Populate the entity filter combo box"""
        print(f"DEBUG: Populating entity filter with {len(self.completed_tumorboards)} tumorboards")
        try:
            entities = sorted(set(tb['entity'] for tb in self.completed_tumorboards))
            print(f"DEBUG: Found {len(entities)} unique entities: {entities}")
            
            self.entity_combo.clear()
            self.entity_combo.addItem("Alle Tumorboards")
            for entity in entities:
                self.entity_combo.addItem(entity)
            print("DEBUG: Entity filter populated successfully")
            
        except Exception as e:
            print(f"DEBUG: Error in populate_entity_filter: {e}")
            logging.error(f"Error in populate_entity_filter: {e}")
            import traceback
            traceback.print_exc()

    def populate_table(self):
        """Populate the table with filtered tumorboard data"""
        print(f"DEBUG: Populating table with {len(self.filtered_tumorboards)} filtered tumorboards")
        try:
            self.tumorboards_table.setRowCount(len(self.filtered_tumorboards))
            
            for row, tumorboard in enumerate(self.filtered_tumorboards):
                print(f"DEBUG: Adding row {row}: {tumorboard['date']} - {tumorboard['entity']}")
                # Date column
                date_item = QTableWidgetItem(tumorboard['date'])
                date_item.setData(Qt.ItemDataRole.UserRole, tumorboard)  # Store full data
                self.tumorboards_table.setItem(row, 0, date_item)
                
                # Entity column
                entity_item = QTableWidgetItem(tumorboard['entity'])
                entity_item.setData(Qt.ItemDataRole.UserRole, tumorboard)  # Store full data in both columns
                self.tumorboards_table.setItem(row, 1, entity_item)
            
            print("DEBUG: Setting results label...")
            # Update results label
            self.results_label.setText(f"{len(self.filtered_tumorboards)} abgeschlossene Tumorboards gefunden")
            
            print("DEBUG: Sorting table...")
            # Sort by date (newest first) by default
            self.tumorboards_table.sortItems(0, Qt.SortOrder.DescendingOrder)
            print("DEBUG: Table populated successfully")
            
        except Exception as e:
            print(f"DEBUG: Error in populate_table: {e}")
            logging.error(f"Error in populate_table: {e}")
            import traceback
            traceback.print_exc()

    def apply_filters(self):
        """Apply the current filter settings"""
        print("DEBUG: Applying filters...")
        if not hasattr(self, 'completed_tumorboards'):
            print("DEBUG: No completed_tumorboards attribute, skipping filters")
            return
        
        try:
            # Convert QDate to Python date (PyQt6 compatible)
            qdate_from = self.date_from.date()
            qdate_to = self.date_to.date()
            # Safe conversion without relying on toPython() method
            date_from = date(qdate_from.year(), qdate_from.month(), qdate_from.day())
            date_to = date(qdate_to.year(), qdate_to.month(), qdate_to.day())
            selected_entity = self.entity_combo.currentText()
            
            print(f"DEBUG: Filter range: {date_from} to {date_to}, entity: '{selected_entity}'")
            
            self.filtered_tumorboards = []
            
            for tumorboard in self.completed_tumorboards:
                # Parse date from tumorboard
                try:
                    tb_date = datetime.strptime(tumorboard['date'], '%d.%m.%Y').date()
                except ValueError:
                    print(f"DEBUG: Invalid date format: {tumorboard['date']}")
                    continue  # Skip invalid dates
                
                # Check date range
                if not (date_from <= tb_date <= date_to):
                    print(f"DEBUG: Date {tb_date} outside range {date_from} - {date_to}")
                    continue
                
                # Check entity filter
                if selected_entity != "Alle Tumorboards" and tumorboard['entity'] != selected_entity:
                    print(f"DEBUG: Entity {tumorboard['entity']} != {selected_entity}")
                    continue
                
                self.filtered_tumorboards.append(tumorboard)
                print(f"DEBUG: Added tumorboard: {tumorboard['date']} - {tumorboard['entity']}")
            
            print(f"DEBUG: Applied filters, {len(self.filtered_tumorboards)} tumorboards match")
            
            # Repopulate table
            self.populate_table()
            
        except Exception as e:
            print(f"DEBUG: Error in apply_filters: {e}")
            logging.error(f"Error in apply_filters: {e}")
            import traceback
            traceback.print_exc()

    def reset_filters(self):
        """Reset all filters to default values"""
        self.date_from.setDate(QDate.currentDate().addMonths(-6))
        self.date_to.setDate(QDate.currentDate())
        self.entity_combo.setCurrentIndex(0)
        self.apply_filters()

    def open_excel_viewer(self, item):
        """Open the Excel viewer for the selected tumorboard"""
        print(f"DEBUG: Clicked on item in column {item.column()}, row {item.row()}")
        
        # Accept clicks on both columns (0=Date, 1=Entity)
        row = item.row()
        
        # Get the date item from the first column (which has the UserRole data)
        date_item = self.tumorboards_table.item(row, 0)
        if not date_item:
            print("DEBUG: No date item found in row")
            return
            
        tumorboard_data = date_item.data(Qt.ItemDataRole.UserRole)
        if not tumorboard_data:
            print("DEBUG: No tumorboard data found in UserRole")
            return
        
        entity_name = tumorboard_data['entity']
        date_str = tumorboard_data['date']
        
        print(f"DEBUG: Opening Excel viewer for {entity_name} on {date_str}")
        logging.info(f"Opening Excel viewer for {entity_name} on {date_str}")
        
        try:
            # Import and create Excel viewer backoffice page
            from pages.backoffice_excel_viewer_page import BackofficeExcelViewerPage
            
            # Check if page already exists
            existing_page_index = self.main_window.find_page_index(BackofficeExcelViewerPage, 
                                                                   entity_name=f"{entity_name}_{date_str}")
            if existing_page_index is not None:
                print("DEBUG: Found existing Excel viewer backoffice page, switching to it.")
                logging.info("Found existing Excel viewer backoffice page, switching to it.")
                self.main_window.stacked_widget.setCurrentIndex(existing_page_index)
            else:
                print("DEBUG: Creating new Excel viewer backoffice page.")
                logging.info("Creating new Excel viewer backoffice page.")
                excel_page = BackofficeExcelViewerPage(self.main_window, entity_name, date_str)
                new_index = self.main_window.stacked_widget.addWidget(excel_page)
                self.main_window.stacked_widget.setCurrentIndex(new_index)
                print(f"DEBUG: Successfully created and switched to page index {new_index}")
                
        except Exception as e:
            print(f"DEBUG: Error opening Excel viewer: {e}")
            logging.error(f"Error opening Excel viewer: {e}")
            import traceback
            traceback.print_exc()

    def refresh_completed_tumorboards(self):
        """Refresh the completed tumorboards data"""
        self.start_indexing() 