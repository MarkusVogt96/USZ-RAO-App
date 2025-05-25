"""
Developer Area Page
Provides access to database management and visualization tools
"""

import sys
import os
import logging
import webbrowser
from pathlib import Path
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                             QFrame, QSpacerItem, QSizePolicy, QMessageBox, QDialog, 
                             QLineEdit, QDialogButtonBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap, QIcon

class PasswordDialog(QDialog):
    """Password dialog for Developer Area access"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Developer Area - Zugriff")
        self.setModal(True)
        self.setFixedSize(500, 300)
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the password dialog UI"""
        # Set dialog background
        self.setStyleSheet("""
            QDialog {
                background-color: #19232D;
                border: 2px solid #3292ea;
                border-radius: 10px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)
        
        # Title
        title_label = QLabel("🔐 Developer Area Zugriff")
        title_label.setFont(QFont("Helvetica", 18, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #3292ea; margin-bottom: 10px;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Description
        desc_label = QLabel("Bitte geben Sie das Passwort ein, um auf die Developer Area zuzugreifen:")
        desc_label.setFont(QFont("Helvetica", 12))
        desc_label.setStyleSheet("color: #cccccc; margin-bottom: 15px;")
        desc_label.setWordWrap(True)
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(desc_label)
        
        # Password input
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Passwort eingeben...")
        self.password_input.setStyleSheet("""
            QLineEdit {
                background-color: #2a3642;
                color: white;
                border: 2px solid #3292ea;
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
                font-family: 'Helvetica';
            }
            QLineEdit:focus {
                border-color: #4da2fa;
                background-color: #3a4652;
            }
            QLineEdit::placeholder {
                color: #888888;
            }
        """)
        layout.addWidget(self.password_input)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        
        # Get individual buttons for custom styling
        ok_button = button_box.button(QDialogButtonBox.StandardButton.Ok)
        cancel_button = button_box.button(QDialogButtonBox.StandardButton.Cancel)
        
        # Set German text
        ok_button.setText("Zugriff")
        cancel_button.setText("Abbrechen")
        
        button_box.setStyleSheet("""
            QPushButton {
                background-color: #3292ea;
                color: white;
                padding: 10px 10px;
                border: none;
                border-radius: 6px;
                font-size: 13px;
                font-weight: bold;
                min-width: 90px;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #4da2fa;
            }
            QPushButton:pressed {
                background-color: #2a82da;
            }
            QPushButton:focus {
                outline: none;
                border: 2px solid #ffffff;
            }
        """)
        
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        # Allow Enter key to submit
        self.password_input.returnPressed.connect(self.accept)
        
        # Set focus to password input
        self.password_input.setFocus()
        
    def get_password(self):
        """Get the entered password"""
        return self.password_input.text()


class DeveloperAreaPage(QWidget):
    """Developer Area page with database management and visualization tools"""
    
    def __init__(self, main_window=None):
        super().__init__()
        self.main_window = main_window
        logging.info("Initializing DeveloperAreaPage...")
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(30)
        
        # Header
        header_layout = QVBoxLayout()
        
        title_label = QLabel("Developer Area")
        title_label.setFont(QFont("Helvetica", 28, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #3292ea; margin-bottom: 10px;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(title_label)
        
        subtitle_label = QLabel("Database Management & Analytics Dashboard")
        subtitle_label.setFont(QFont("Helvetica", 16))
        subtitle_label.setStyleSheet("color: #ffffff; margin-bottom: 20px;")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(subtitle_label)
        
        layout.addLayout(header_layout)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("background-color: #2a3642; min-height: 2px; max-height: 2px;")
        layout.addWidget(separator)
        
        # Main content area
        content_layout = QVBoxLayout()
        content_layout.setSpacing(40)
        
        # Description
        description_label = QLabel(
            "Hier finden Sie Tools zur Verwaltung und Analyse der Tumorboard-Datenbank. "
            "Diese Funktionen sind für Entwickler und Administratoren gedacht."
        )
        description_label.setFont(QFont("Helvetica", 14))
        description_label.setStyleSheet("color: #cccccc; margin-bottom: 20px;")
        description_label.setWordWrap(True)
        description_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(description_label)
        
        # Buttons container
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(40)
        
        # Database Manager Button
        db_manager_button = self.create_feature_button(
            "Database Manager",
            "Interaktive Datenbank-Verwaltung über Terminal-Konsole",
            "🗄️",
            self.open_database_manager
        )
        buttons_layout.addWidget(db_manager_button)
        
        # Database Dashboard Button  
        db_dashboard_button = self.create_feature_button(
            "Database Dashboard",
            "Interaktive Datenvisualisierung im Web-Browser",
            "📊",
            self.open_database_dashboard
        )
        buttons_layout.addWidget(db_dashboard_button)
        
        content_layout.addLayout(buttons_layout)
        
        # Add spacer to center content
        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        layout.addLayout(content_layout)
        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        
        logging.info("DeveloperAreaPage UI setup complete.")
        
    def create_feature_button(self, title, description, icon, callback):
        """Create a styled feature button"""
        button_frame = QFrame()
        button_frame.setStyleSheet("""
            QFrame {
                background-color: #2a3642;
                border: 2px solid #3292ea;
                border-radius: 15px;
                padding: 20px;
            }
            QFrame:hover {
                background-color: #3a4652;
                border-color: #4da2fa;
            }
        """)
        button_frame.setFixedSize(300, 200)
        button_frame.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Make frame clickable
        button_frame.mousePressEvent = lambda event: callback()
        
        layout = QVBoxLayout(button_frame)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(15)
        
        # Icon
        icon_label = QLabel(icon)
        icon_label.setFont(QFont("Helvetica", 48))
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet("color: #3292ea;")
        layout.addWidget(icon_label)
        
        # Title
        title_label = QLabel(title)
        title_label.setFont(QFont("Helvetica", 16, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #ffffff;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Description
        desc_label = QLabel(description)
        desc_label.setFont(QFont("Helvetica", 12))
        desc_label.setStyleSheet("color: #cccccc;")
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        return button_frame
        
    def open_database_manager(self):
        """Open database manager in terminal console"""
        try:
            logging.info("Opening Database Manager in terminal console...")
            
            # Use the same pattern as KISIM Scripts - open CmdScriptsPage with database_manager
            if self.main_window and hasattr(self.main_window, 'open_cmd_scripts_page'):
                # Create a script key for database manager
                script_key = "database_manager"
                self.main_window.open_cmd_scripts_page(script_key)
                logging.info("Database Manager opened in CmdScriptsPage")
            else:
                QMessageBox.warning(self, "Fehler", "Konnte Database Manager nicht öffnen.")
                logging.error("Main window or open_cmd_scripts_page method not available")
                
        except Exception as e:
            logging.error(f"Error opening database manager: {e}")
            QMessageBox.critical(self, "Fehler", f"Fehler beim Öffnen des Database Managers: {e}")
            
    def open_database_dashboard(self):
        """Open database dashboard in web browser engine"""
        try:
            logging.info("Opening Database Dashboard in web browser...")
            
            # Import and run the interactive dashboard
            sys.path.insert(0, str(Path(__file__).parent.parent))
            
            try:
                from utils.dashboard_html_generator import generate_complete_dashboard
                
                # Generate interactive HTML with embedded data
                html_file = generate_complete_dashboard(interactive=True)
                if html_file:
                    logging.info(f"Interactive dashboard generated: {html_file}")
                    
                    # Open in external browser (safer approach)
                    html_path = Path(html_file)
                    file_url = f"file:///{html_path.as_posix()}"
                    webbrowser.open(file_url)
                    logging.info("Dashboard opened in external browser")
                    
                    QMessageBox.information(self, "Dashboard geöffnet", 
                                          "Das interaktive Dashboard wurde in Ihrem Standard-Browser geöffnet.")
                else:
                    QMessageBox.warning(self, "Fehler", "Konnte Dashboard nicht generieren.")
                    logging.error("Failed to generate dashboard HTML")
                    
            except ImportError as ie:
                logging.error(f"Dashboard import error: {ie}")
                QMessageBox.critical(self, "Import-Fehler", 
                                   f"Dashboard-Module konnten nicht importiert werden: {ie}")
                
        except Exception as e:
            logging.error(f"Error opening database dashboard: {e}")
            QMessageBox.critical(self, "Fehler", f"Fehler beim Öffnen des Dashboards: {e}")
            
 