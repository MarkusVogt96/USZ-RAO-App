from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                             QFrame, QMessageBox, QGridLayout, QScrollArea, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QComboBox)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QPixmap
import os
import logging
import pandas as pd
from pathlib import Path

# Import centralized path management
from utils.path_management import BackofficePathManager

class CategoryButton(QPushButton):
    """Custom button for category selection - similar to StaticTile styling"""
    def __init__(self, title, subtitle, count, status_text, category_key, parent=None):
        super().__init__(parent)
        self.title = title
        self.subtitle = subtitle
        self.count = count
        self.status_text = status_text
        self.category_key = category_key
        self.setFixedSize(400, 300)
        
        # Set basic button styling (same as StaticTile)
        self.setStyleSheet("""
            QPushButton {
                background-color: #114473;
                color: white;
                border: none;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #1a5a9e;
            }
            QPushButton:pressed {
                background-color: #0d2e4d;
            }
        """)
        
        # Create layout for button content
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 30, 10, 20)  # More top margin to push content down
        layout.setSpacing(15)  # Slightly tighter spacing
        self.setLayout(layout)
        
        # Add title label at the top
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet("color: white; background: transparent;")
        self.title_label.setFont(QFont('Calibri', 18, QFont.Weight.Bold))  # Increased from 16 to 18
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.title_label.setWordWrap(True)
        layout.addWidget(self.title_label)
        
        # Add subtitle
        self.subtitle_label = QLabel(subtitle)
        self.subtitle_label.setStyleSheet("color: #cccccc; background: transparent;")
        self.subtitle_label.setFont(QFont('Calibri', 14))  # Increased from 12 to 14
        self.subtitle_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.subtitle_label.setWordWrap(True)
        layout.addWidget(self.subtitle_label)
        
        # Add count and status
        self.status_label = QLabel()
        self.status_label.setFont(QFont('Calibri', 14, QFont.Weight.Bold))  # Decreased from 14 to 12
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(self.status_label)
        
        # Set initial status
        self.update_count(count, status_text)
        
        # Add stretch to push content to top
        layout.addStretch()
    
    def update_count(self, count, status_text):
        """Update the count and status text with proper plural/singular and color coding"""
        self.count = count
        self.status_text = status_text
        
        # Handle count display and plural/singular
        if isinstance(count, str) and ("Keine Verbindung" in count or "Fehler" in count):
            # Error case
            display_text = count
            color = "#FF6B6B"  # Light red for errors
        elif count == 0:
            # No pending items - show "alles bearbeitet" in green
            display_text = "alles bearbeitet"
            color = "#4CAF50"  # Green
        else:
            # Format text with proper plural/singular
            if "Erstkons" in status_text:
                if count == 1:
                    singular_text = status_text.replace("Erstkons-Aufgebote", "Erstkons-Aufgebot")
                    display_text = f"{count} {singular_text}"
                else:
                    display_text = f"{count} {status_text}"
            elif "Konsil" in status_text:
                if count == 1:
                    singular_text = status_text.replace("Konsil-Eingänge", "Konsil-Eingang")
                    display_text = f"{count} {singular_text}"
                else:
                    display_text = f"{count} {status_text}"
            else:
                display_text = f"{count} {status_text}"
            
            # Color coding based on category
            if self.category_key == "kat_I":
                color = "#FF4444"  # Red
            elif self.category_key == "kat_II":
                color = "#FF8C00"  # Orange  
            elif self.category_key == "kat_III":
                color = "#FFD700"  # Gold/Yellow
            else:
                color = "#FFA500"  # Default orange
        
        # Update label
        self.status_label.setText(display_text)
        self.status_label.setStyleSheet(f"color: {color}; background: transparent;")

class BackofficePageErstkonsultationen(QWidget):
    def __init__(self, main_window):
        super().__init__()
        logging.info("Initializing BackofficePageErstkonsultationen...")
        self.main_window = main_window
        self.setup_ui()
        logging.info("BackofficePageErstkonsultationen initialization complete.")

    def setup_ui(self):
        """Setup the erstkonsultationen user interface"""
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(30, 20, 30, 30)
        main_layout.setSpacing(20)
        self.setLayout(main_layout)

        # Header with title only (back button removed)
        header_layout = QHBoxLayout()
        header_layout.setSpacing(15)

        # Title
        title_label = QLabel("Erstkonsultationen aufbieten")
        title_label.setFont(QFont("Helvetica", 26, QFont.Weight.Bold))
        title_label.setStyleSheet("color: white;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()

        main_layout.addLayout(header_layout)

        # Content
        self.create_content(main_layout)

    def create_content(self, parent_layout):
        """Create the main content with category buttons"""
        # Scrollable area for content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("QScrollArea { border: none; }")
        
        # Content widget inside scroll area
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(20)
        content_layout.setContentsMargins(10, 10, 40, 40)

        # Grid layout for category buttons (same as tumor group page)
        grid_layout = QGridLayout()
        grid_layout.setHorizontalSpacing(20)
        grid_layout.setVerticalSpacing(50)

        # Create category buttons with counts
        self.create_category_buttons(grid_layout)

        # Add grid layout to content
        content_layout.addLayout(grid_layout)
        content_layout.addStretch()

        # Set scroll area content
        scroll_area.setWidget(content_widget)
        parent_layout.addWidget(scroll_area)

    def create_category_buttons(self, grid_layout):
        """Create the three category buttons with current counts"""
        # Category definitions
        categories = [
            {
                "key": "kat_I",
                "title": "Kategorie I",
                "subtitle": "Aufgebot in 1-3 Tagen",
                "status_text": "Erstkons-Aufgebote ausstehend",
                "excel_file": "Kat_I.xlsx"
            },
            {
                "key": "kat_II", 
                "title": "Kategorie II",
                "subtitle": "Aufgebot in 4-7 Tagen",
                "status_text": "Erstkons-Aufgebote ausstehend",
                "excel_file": "Kat_II.xlsx"
            },
            {
                "key": "kat_III",
                "title": "Kategorie III", 
                "subtitle": "Aufgebot nach Konsil-Eingang",
                "status_text": "Konsil-Eingänge ausstehend",
                "excel_file": "Kat_III.xlsx"
            }
        ]

        # Create buttons for each category
        self.category_buttons = {}
        for i, category in enumerate(categories):
            # Get current count
            count = self.get_category_count(category["excel_file"])
            
            # Create button
            button = CategoryButton(
                category["title"],
                category["subtitle"], 
                count,
                category["status_text"],
                category["key"]  # Pass category key for color coding
            )
            
            # Connect click event
            button.clicked.connect(lambda checked, key=category["key"]: self.open_category_page(key))
            
            # Store button reference
            self.category_buttons[category["key"]] = button
            
            # Add to grid (arrange in single row)
            grid_layout.addWidget(button, 0, i)

    def get_category_count(self, excel_filename):
        """Get count of pending patients from category Excel file"""
        try:
            # Use centralized path management with network/local priority
            backoffice_dir, using_network = BackofficePathManager.get_backoffice_path(show_warnings=False)
            excel_path = backoffice_dir / excel_filename
            
            if not excel_path.exists():
                logging.warning(f"Category Excel file not found: {excel_path}")
                return f"Keine Verbindung zu {excel_filename.replace('.xlsx', '')}"
            
            # Read Excel file
            df = pd.read_excel(excel_path, engine='openpyxl')
            
            if df.empty:
                return 0
            
            # Count patients with "Nein" in column N (Status column)
            # Column N should be index 13 (0-based indexing)
            if len(df.columns) < 14:
                logging.warning(f"Excel file {excel_filename} has insufficient columns")
                return 0
            
            status_column = df.iloc[:, 13]  # Column N (0-based index 13)
            
            # Count "Nein" entries (case-insensitive)
            pending_count = 0
            for value in status_column:
                if str(value).strip().lower() == 'nein':
                    pending_count += 1
            
            return pending_count
            
        except Exception as e:
            logging.error(f"Error reading category Excel file {excel_filename}: {e}")
            return f"Fehler beim Laden von {excel_filename.replace('.xlsx', '')}"

    def open_category_page(self, category_key):
        """Open the specific category page"""
        logging.info(f"Opening category page: {category_key}")
        
        # Check for session navigation
        if not self.main_window.check_tumorboard_session_before_navigation():
            return
        
        # Import the appropriate category page class
        try:
            if category_key == "kat_I":
                from pages.backoffice_kat_I_page import BackofficeKatIPage
                page_class = BackofficeKatIPage
            elif category_key == "kat_II":
                from pages.backoffice_kat_II_page import BackofficeKatIIPage
                page_class = BackofficeKatIIPage
            elif category_key == "kat_III":
                from pages.backoffice_kat_III_page import BackofficeKatIIIPage
                page_class = BackofficeKatIIIPage
            else:
                logging.error(f"Unknown category key: {category_key}")
                return
            
            # Check if page already exists
            existing_page = None
            for i in range(self.main_window.stacked_widget.count()):
                widget = self.main_window.stacked_widget.widget(i)
                if isinstance(widget, page_class):
                    existing_page = widget
                    break
            
            if existing_page:
                # Refresh the existing page to update counts
                if hasattr(existing_page, 'refresh_data'):
                    existing_page.refresh_data()
                self.main_window.stacked_widget.setCurrentWidget(existing_page)
                logging.info(f"Navigated to existing {page_class.__name__}")
            else:
                # Create new page
                new_page = page_class(self.main_window)
                new_index = self.main_window.stacked_widget.addWidget(new_page)
                self.main_window.stacked_widget.setCurrentIndex(new_index)
                logging.info(f"Created and navigated to {page_class.__name__}")
                
        except ImportError as e:
            logging.error(f"Could not import category page for {category_key}: {e}")
            # Show error message to user
            msg = QMessageBox(self)
            msg.setWindowTitle("Seite nicht verfügbar")
            msg.setText(f"Die Kategorie-Seite ist noch nicht implementiert.\n\nFehler: {e}")
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.exec()

    def refresh_category_counts(self):
        """Refresh the counts on all category buttons"""
        categories = [
            {"key": "kat_I", "excel_file": "Kat_I.xlsx", "status_text": "Erstkons-Aufgebote ausstehend"},
            {"key": "kat_II", "excel_file": "Kat_II.xlsx", "status_text": "Erstkons-Aufgebote ausstehend"},
            {"key": "kat_III", "excel_file": "Kat_III.xlsx", "status_text": "Konsil-Eingänge ausstehend"}
        ]
        
        for category in categories:
            if category["key"] in self.category_buttons:
                count = self.get_category_count(category["excel_file"])
                self.category_buttons[category["key"]].update_count(count, category["status_text"])
        
        logging.info("Category counts refreshed")

    def showEvent(self, event):
        """Refresh counts whenever the page is shown"""
        super().showEvent(event)
        if hasattr(self, 'category_buttons'):
            # Use QTimer to ensure the UI is fully loaded before refreshing
            QTimer.singleShot(100, self.refresh_category_counts) 