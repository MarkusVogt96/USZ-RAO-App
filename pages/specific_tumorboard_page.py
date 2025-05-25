from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QScrollArea, QFrame
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
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
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(15)
        content_layout.setContentsMargins(20, 20, 20, 20)

        # Get tumorboard dates
        current_dates, past_dates = self._scan_tumorboard_dates()

        # Current/Future Tumorboards Section
        current_section = self._create_section("Aktuelle Tumorboards", current_dates, is_current=True)
        content_layout.addWidget(current_section)

        # Past Tumorboards Section
        past_section = self._create_section("Abgeschlossene Tumorboards", past_dates, is_current=False)
        content_layout.addWidget(past_section)

        # Add stretch to push content to top
        content_layout.addStretch()

        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)

    def _scan_tumorboard_dates(self):
        """Scan for tumorboard date folders and categorize them"""
        tumorboard_path = Path.home() / "tumorboards" / self.tumorboard_name
        current_dates = []
        past_dates = []
        today = datetime.date.today()

        logging.info(f"Scanning tumorboard path: {tumorboard_path}")

        if not tumorboard_path.exists():
            logging.warning(f"Tumorboard path does not exist: {tumorboard_path}")
            return current_dates, past_dates

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
            excel_page = ExcelViewerPage(self.main_window, self.tumorboard_name, date_str)
            new_index = self.main_window.stacked_widget.addWidget(excel_page)
            self.main_window.stacked_widget.setCurrentIndex(new_index) 