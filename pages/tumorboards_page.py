from PyQt6.QtWidgets import QWidget, QGridLayout, QLabel, QVBoxLayout, QPushButton, QHBoxLayout, QScrollArea, QFrame
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
import os
import logging

class TumorboardsPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        logging.info("Initializing TumorboardsPage...")
        self.main_window = main_window
        
        # Define all tumorboards (from existing script)
        self.alle_tumorboards = [
            "GAS-CHI-ONK",
            "GIT",
            "Gyn",
            "HCC",
            "HPB",
            "Hämato-Onkologie/Lymphome",
            "Hyperthermie",
            "LLMZ",
            "Melanome",
            "Neuro-Onkologie",
            "NET",
            "ORL",
            "Paragangliome",
            "Pädiatrie",
            "Protonentherapie",
            "Sarkom",
            "Schädelbasis",
            "Schilddrüse",
            "Thorax",
            "Transplantationsboard",
            "Uro",
            "Vascular",
            "ZKGS"
        ]
        
        # Location mappings (placeholders for now)
        self.tumorboard_location_mapping = {
            "GAS-CHI-ONK": "{placeholder}",
            "GIT": "{placeholder}",
            "Gyn": "{placeholder}",
            "HCC": "{placeholder}",
            "HPB": "{placeholder}",
            "Hämato-Onkologie/Lymphome": "{placeholder}",
            "Hyperthermie": "{placeholder}",
            "LLMZ": "{placeholder}",
            "Melanome": "{placeholder}",
            "Neuro-Onkologie": "{placeholder}",
            "NET": "{placeholder}",
            "ORL": "{placeholder}",
            "Paragangliome": "{placeholder}",
            "Pädiatrie": "{placeholder}",
            "Protonentherapie": "{placeholder}",
            "Sarkom": "{placeholder}",
            "Schädelbasis": "{placeholder}",
            "Schilddrüse": "{placeholder}",
            "Thorax": "{placeholder}",
            "Transplantationsboard": "{placeholder}",
            "Uro": "{placeholder}",
            "Vascular": "{placeholder}",
            "ZKGS": "{placeholder}"
        }
        
        # Temporary weekday assignments (distribute tumorboards across Mon-Fri)
        self.weekday_assignments = self._create_weekday_assignments()
        
        # Setup UI after initializing data
        self.setup_ui()
        logging.info("TumorboardsPage UI setup complete.")

    def _create_weekday_assignments(self):
        """Distribute tumorboards across weekdays (Monday-Friday)"""
        weekdays = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag"]
        assignments = {day: [] for day in weekdays}
        
        # Distribute tumorboards evenly across weekdays
        # This is temporary - in real implementation, this would come from configuration
        for i, tumorboard in enumerate(self.alle_tumorboards):
            day_index = i % 5  # Distribute across 5 weekdays
            assignments[weekdays[day_index]].append({
                'name': tumorboard,
                'time': f"{8 + (i % 8)}:00"  # Placeholder times 8:00-15:00
            })
        
        # Sort by time within each day
        for day in weekdays:
            assignments[day].sort(key=lambda x: x['time'])
            
        return assignments

    def setup_ui(self):
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(10, 0, 40, 40)
        self.setLayout(main_layout)

        # Page title
        title_label = QLabel("Tumorboards")
        title_label.setFont(QFont("Helvetica", 24, QFont.Weight.Bold))
        title_label.setStyleSheet("color: white; margin-bottom: 20px;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)

        # Create scrollable area for the week view
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)
        
        # Week view widget
        week_widget = QWidget()
        week_layout = QHBoxLayout(week_widget)
        week_layout.setSpacing(15)
        week_layout.setContentsMargins(10, 10, 10, 10)
        
        # Create columns for each weekday
        weekdays = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag"]
        
        for day in weekdays:
            day_column = self._create_day_column(day)
            week_layout.addWidget(day_column)
        
        scroll_area.setWidget(week_widget)
        main_layout.addWidget(scroll_area)

    def _create_day_column(self, day_name):
        """Create a column for a specific weekday"""
        column_frame = QFrame()
        column_frame.setFixedWidth(280)
        column_frame.setStyleSheet("""
            QFrame {
                background-color: #1a2633;
                border: 1px solid #2a3642;
                border-radius: 8px;
            }
        """)
        
        column_layout = QVBoxLayout(column_frame)
        column_layout.setSpacing(10)
        column_layout.setContentsMargins(15, 15, 15, 15)
        
        # Day header
        day_header = QLabel(day_name)
        day_header.setFont(QFont("Helvetica", 16, QFont.Weight.Bold))
        day_header.setStyleSheet("color: #00BFFF; margin-bottom: 10px;")
        day_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        column_layout.addWidget(day_header)
        
        # Add tumorboard buttons for this day
        tumorboards_for_day = self.weekday_assignments.get(day_name, [])
        
        for tb_info in tumorboards_for_day:
            tb_button = self._create_tumorboard_button(tb_info['name'], tb_info['time'])
            column_layout.addWidget(tb_button)
        
        # Add stretch to push buttons to top
        column_layout.addStretch()
        
        return column_frame

    def _create_tumorboard_button(self, tumorboard_name, time):
        """Create a tumorboard button"""
        button = QPushButton()
        button.setFixedHeight(80)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Button styling
        button.setStyleSheet("""
            QPushButton {
                background-color: #114473;
                color: white;
                border: none;
                border-radius: 6px;
                text-align: left;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #1a5a9e;
            }
            QPushButton:pressed {
                background-color: #0d2e4d;
            }
        """)
        
        # Create button layout with tumorboard name and location
        button_layout = QVBoxLayout(button)
        button_layout.setContentsMargins(5, 5, 5, 5)
        button_layout.setSpacing(3)
        
        # Time and name
        time_name_layout = QHBoxLayout()
        time_name_layout.setSpacing(8)
        
        time_label = QLabel(time)
        time_label.setFont(QFont("Helvetica", 10))
        time_label.setStyleSheet("color: #cccccc;")
        
        name_label = QLabel(tumorboard_name)
        name_label.setFont(QFont("Helvetica", 12, QFont.Weight.Bold))
        name_label.setStyleSheet("color: white;")
        name_label.setWordWrap(True)
        
        time_name_layout.addWidget(time_label)
        time_name_layout.addWidget(name_label)
        time_name_layout.addStretch()
        
        # Location
        location = self.tumorboard_location_mapping.get(tumorboard_name, "{placeholder}")
        location_label = QLabel(f"Ort: {location}")
        location_label.setFont(QFont("Helvetica", 10))
        location_label.setStyleSheet("color: #cccccc;")
        location_label.setWordWrap(True)
        
        button_layout.addLayout(time_name_layout)
        button_layout.addWidget(location_label)
        
        # Connect button click
        button.clicked.connect(lambda checked, name=tumorboard_name: self.open_specific_tumorboard_page(name))
        
        return button

    def open_specific_tumorboard_page(self, tumorboard_name):
        """Open the specific tumorboard page for the selected tumorboard"""
        logging.info(f"Opening specific tumorboard page for: {tumorboard_name}")
        
        # Import here to avoid circular imports
        from .specific_tumorboard_page import SpecificTumorboardPage
        
        # Check if page already exists
        existing_page_index = self.main_window.find_page_index(SpecificTumorboardPage, tumorboard_name)
        if existing_page_index is not None:
            logging.info("Found existing specific tumorboard page, switching to it.")
            self.main_window.stacked_widget.setCurrentIndex(existing_page_index)
        else:
            logging.info("Creating new specific tumorboard page.")
            specific_page = SpecificTumorboardPage(self.main_window, tumorboard_name)
            new_index = self.main_window.stacked_widget.addWidget(specific_page)
            self.main_window.stacked_widget.setCurrentIndex(new_index) 