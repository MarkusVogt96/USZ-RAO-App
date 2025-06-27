from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QScrollArea, QFrame, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QShowEvent
import os
import datetime
import re
import logging
from pathlib import Path

class SpecificTumorboardPage(QWidget):
    def __init__(self, main_window, tumorboard_name):
        super().__init__()
        logging.info(f"Initializing SpecificTumorboardPage for: {tumorboard_name}")
        self.main_window = main_window
        self.tumorboard_name = tumorboard_name
        
        # Store tumorboard_name as attribute for find_page_index
        self.entity_name = tumorboard_name
        
        # Initialize UI components that will be populated
        self.content_layout = None
        
        # Track path usage for warning dialogs
        self.using_fallback_path = False
        
        # Store the actual tumorboard base path that was determined
        self.tumorboard_base_path = None
        
        self.setup_ui()
        logging.info(f"SpecificTumorboardPage UI setup complete for {tumorboard_name}.")

    def setup_ui(self):
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(10, 0, 40, 40)
        self.setLayout(main_layout)

        # Page title
        title_label = QLabel(f"Tumorboard: {self.tumorboard_name}")
        title_label.setFont(QFont("Helvetica", 24, QFont.Weight.Bold))
        title_label.setStyleSheet("color: white; margin-bottom: 20px;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)

        # Create scrollable area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)

        # Content widget
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setSpacing(15)
        self.content_layout.setContentsMargins(20, 20, 20, 20)

        # Initially populate the content
        self._populate_content()

        scroll_area.setWidget(self.content_widget)
        main_layout.addWidget(scroll_area)

    def _populate_content(self):
        """Populate the content with current tumorboard data"""
        # Clear existing content
        self._clear_content_layout()

        # Get tumorboard dates
        current_dates, past_dates = self._scan_tumorboard_dates()

        # If no data was found, show appropriate message
        if not current_dates and not past_dates:
            self._show_no_data_content()
            return

        # Current/Future Tumorboards Section
        current_section = self._create_section("Aktuelle Tumorboards", current_dates, is_current=True)
        self.content_layout.addWidget(current_section)

        # Past Tumorboards Section
        past_section = self._create_section("Vergangene Tumorboards", past_dates, is_current=False)
        self.content_layout.addWidget(past_section)

        # Add stretch to push content to top
        self.content_layout.addStretch()

    def _show_no_data_content(self):
        """Show content when no tumorboard data is available"""
        # Create error message widget
        error_frame = QFrame()
        error_frame.setStyleSheet("""
            QFrame {
                background-color: #2d1b1b;
                border: 2px solid #d32f2f;
                border-radius: 10px;
                padding: 20px;
                margin: 20px;
            }
        """)

        error_layout = QVBoxLayout(error_frame)
        error_layout.setSpacing(15)

        # Error title
        error_title = QLabel("❌ Kein Zugriff auf (K:\\)RAO_Daten")
        error_title.setFont(QFont("Helvetica", 18, QFont.Weight.Bold))
        error_title.setStyleSheet("color: #f44336; text-align: center;")
        error_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        error_layout.addWidget(error_title)

        # Error message
        error_message = QLabel(
            "Es besteht kein Zugriff auf RAO_Daten im Intranet!\n"
            "Tumorboards konnten nicht geladen werden.\n\n"
            "Bitte stellen Sie eine Verbindung zum Intranet her und laden Sie die Seite neu."
        )
        error_message.setFont(QFont("Helvetica", 14))
        error_message.setStyleSheet("color: #ffffff; text-align: center; line-height: 1.4;")
        error_message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        error_message.setWordWrap(True)
        error_layout.addWidget(error_message)

        # Add the error frame to content
        self.content_layout.addWidget(error_frame)
        self.content_layout.addStretch()

    def _clear_content_layout(self):
        """Clear all widgets from the content layout"""
        if self.content_layout is not None:
            while self.content_layout.count():
                child = self.content_layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()

    def refresh_data(self):
        """Refresh tumorboard data - can be called manually"""
        logging.info(f"Refreshing tumorboard data for: {self.tumorboard_name}")
        self._populate_content()

    def showEvent(self, event: QShowEvent):
        """Override showEvent to refresh data whenever the page is shown"""
        super().showEvent(event)
        if event.type() == QShowEvent.Type.Show:
            logging.info(f"SpecificTumorboardPage shown, refreshing data for: {self.tumorboard_name}")
            self.refresh_data()
            
            # Show warning dialog if using fallback path (every time)
            if self.using_fallback_path:
                self._show_fallback_warning()

    def _determine_tumorboard_path(self):
        """
        Determine the correct tumorboard path based on priority:
        1. K:\\RAO_Projekte\\App\\tumorboards\\ (primary/intranet)
        2. {home}\\tumorboards\\ (fallback/local)
        3. None (error - no path available)
        
        Returns:
            tuple: (Path object or None, bool indicating if using fallback)
        """
        # Primary path (Intranet)
        primary_path = Path("K:/RAO_Projekte/App/tumorboards") / self.tumorboard_name
        
        # Fallback path (Local)
        fallback_path = Path.home() / "tumorboards" / self.tumorboard_name
        
        logging.info(f"Checking primary path: {primary_path}")
        
        # Check if primary path exists and is accessible
        try:
            if primary_path.exists() and primary_path.is_dir():
                logging.info("Primary path (Intranet) found and accessible")
                self.tumorboard_base_path = Path("K:/RAO_Projekte/App/tumorboards")
                return primary_path, False
        except (OSError, PermissionError) as e:
            logging.warning(f"Primary path not accessible: {e}")
        
        logging.info(f"Checking fallback path: {fallback_path}")
        
        # Check fallback path
        try:
            if fallback_path.exists() and fallback_path.is_dir():
                logging.info("Fallback path (Local) found and accessible")
                self.tumorboard_base_path = Path.home() / "tumorboards"
                return fallback_path, True
        except (OSError, PermissionError) as e:
            logging.warning(f"Fallback path not accessible: {e}")
        
        # No valid path found
        logging.error("No valid tumorboard path found")
        self.tumorboard_base_path = None
        return None, False

    def _show_fallback_warning(self):
        """Show warning dialog when using fallback path"""
        msg = QMessageBox(self)
        msg.setWindowTitle("Warnung - Fallback Datenquelle")
        msg.setText(f"Achtung: RAO_Daten (K:\\) Laufwerk konnte nicht erreicht werden. Alternativ wurden die Daten aus {Path.home()}\\tumorboards geladen.")
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #19232D;
                color: white;
            }
            QMessageBox QLabel {
                color: white;
                font-size: 14px;
                padding: 10px;
            }
            QMessageBox QPushButton {
                background-color: #3292ea;
                color: white;
                padding: 8px 20px;
                border: none;
                border-radius: 6px;
                font-size: 13px;
                font-weight: bold;
                min-width: 80px;
                min-height: 30px;
            }
            QMessageBox QPushButton:hover {
                background-color: #4da2fa;
            }
            QMessageBox QPushButton:pressed {
                background-color: #2a82da;
            }
        """)
        msg.exec()



    def _scan_tumorboard_dates(self):
        """Scan for tumorboard date folders and categorize them using the new path logic"""
        current_dates = []
        past_dates = []
        today = datetime.date.today()

        # Determine the correct tumorboard path
        tumorboard_path, is_fallback = self._determine_tumorboard_path()
        
        # Update fallback tracking for dialog warnings
        self.using_fallback_path = is_fallback

        if tumorboard_path is None:
            # No valid path found - return empty lists (error handling in _populate_content)
            logging.error("No valid tumorboard path found")
            return current_dates, past_dates

        logging.info(f"Scanning tumorboard path: {tumorboard_path} (fallback: {is_fallback})")

        try:
            for item in tumorboard_path.iterdir():
                if item.is_dir():
                    # Check if folder name matches dd.mm.yyyy format
                    if re.match(r'^\d{2}\.\d{2}\.\d{4}$', item.name):
                        try:
                            # Parse the date
                            folder_date = datetime.datetime.strptime(item.name, '%d.%m.%Y').date()
                            
                            if folder_date >= today:
                                current_dates.append(item.name)
                            else:
                                past_dates.append(item.name)
                                
                        except ValueError:
                            logging.warning(f"Invalid date format in folder name: {item.name}")
                            continue

        except Exception as e:
            logging.error(f"Error scanning tumorboard dates: {e}")
            # Return empty lists (error handling in _populate_content)
            return current_dates, past_dates

        # Sort dates
        current_dates.sort(key=lambda x: datetime.datetime.strptime(x, '%d.%m.%Y'))
        past_dates.sort(key=lambda x: datetime.datetime.strptime(x, '%d.%m.%Y'), reverse=True)

        logging.info(f"Found {len(current_dates)} current and {len(past_dates)} past tumorboard dates")
        return current_dates, past_dates

    def _create_section(self, section_title, dates, is_current=True):
        """Create a section with title and date buttons"""
        section_frame = QFrame()
        section_frame.setStyleSheet("""
            QFrame {
                background-color: transparent;
                border: none;
                border-radius: 0px;
                padding: 0px;
            }
        """)

        section_layout = QVBoxLayout(section_frame)
        section_layout.setSpacing(10)
        section_layout.setContentsMargins(15, 5, 20, 10)

        # Section title
        title_label = QLabel(section_title)
        title_label.setFont(QFont("Helvetica", 16, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #00BFFF; margin-bottom: 5px;")
        section_layout.addWidget(title_label)

        # Date buttons
        if not dates:
            no_dates_label = QLabel("Keine Tumorboards gefunden.")
            no_dates_label.setFont(QFont("Helvetica", 12))
            no_dates_label.setStyleSheet("color: #cccccc; font-style: italic;")
            section_layout.addWidget(no_dates_label)
        else:
            # Create grid layout for buttons
            buttons_layout = QVBoxLayout()
            buttons_layout.setSpacing(10)

            for date in dates:
                date_button = self._create_date_button(date, is_current)
                buttons_layout.addWidget(date_button)

            section_layout.addLayout(buttons_layout)

        return section_frame

    def _create_date_button(self, date_str, is_current=True):
        """Create a button for a specific date"""
        button = QPushButton()
        button.setFixedHeight(60)
        button.setCursor(Qt.CursorShape.PointingHandCursor)

        # Determine text color based on current/past status
        text_color = "lime" if is_current else "white"

        button.setStyleSheet(f"""
            QPushButton {{
                background-color: #114473;
                color: {text_color};
                border: none;
                border-radius: 6px;
                text-align: left;
                padding: 15px;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #1a5a9e;
            }}
            QPushButton:pressed {{
                background-color: #0d2e4d;
            }}
        """)

        # Format date for display
        try:
            date_obj = datetime.datetime.strptime(date_str, '%d.%m.%Y')
            weekday = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"][date_obj.weekday()]
            display_text = f"{weekday}, {date_str}"
        except ValueError:
            display_text = date_str

        button.setText(display_text)

        # Connect button click
        button.clicked.connect(lambda checked, date=date_str: self.open_excel_viewer(date))

        return button

    def get_tumorboard_base_path(self):
        """Get the base path used for tumorboard data (K:\ or local)"""
        return self.tumorboard_base_path
    
    def is_using_fallback_path(self):
        """Check if currently using local fallback path"""
        return self.using_fallback_path

    def open_excel_viewer(self, date_str):
        """Open Excel viewer for the selected date"""
        logging.info(f"Opening Excel viewer for {self.tumorboard_name} on {date_str}")
        
        # Import here to avoid circular imports
        from .excel_viewer_page import ExcelViewerPage
        
        # Check if page already exists
        existing_page_index = self.main_window.find_page_index(ExcelViewerPage, 
                                                               entity_name=f"{self.tumorboard_name}_{date_str}")
        if existing_page_index is not None:
            logging.info("Found existing Excel viewer page, switching to it.")
            self.main_window.stacked_widget.setCurrentIndex(existing_page_index)
        else:
            logging.info("Creating new Excel viewer page.")
            excel_page = ExcelViewerPage(self.main_window, self.tumorboard_name, date_str, self.tumorboard_base_path)
            new_index = self.main_window.stacked_widget.addWidget(excel_page)
            self.main_window.stacked_widget.setCurrentIndex(new_index) 