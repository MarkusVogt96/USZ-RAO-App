"""
Simple Developer Area Page for testing
"""

import logging
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                             QFrame, QSpacerItem, QSizePolicy, QMessageBox, QDialog, 
                             QLineEdit, QDialogButtonBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class PasswordDialog(QDialog):
    """Simple password dialog"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Developer Area - Zugriff")
        self.setModal(True)
        self.setFixedSize(500, 320)
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the password dialog UI"""
        self.setStyleSheet("QDialog { background-color: #19232D; }")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Title
        title_label = QLabel("🔐 Developer Area Zugriff")
        title_label.setFont(QFont("Helvetica", 18, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #3292ea; margin-bottom: 5px; padding: 5px;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Description
        desc_label = QLabel("Bitte geben Sie das Passwort ein:")
        desc_label.setFont(QFont("Helvetica", 12))
        desc_label.setStyleSheet("color: #cccccc;")
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
                padding: 15px;
                font-size: 16px;
                min-height: 20px;
                min-width: 300px;
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
        
        ok_button = button_box.button(QDialogButtonBox.StandardButton.Ok)
        cancel_button = button_box.button(QDialogButtonBox.StandardButton.Cancel)
        
        ok_button.setText("Zugriff")
        cancel_button.setText("Abbrechen")
        
        button_box.setStyleSheet("""
            QPushButton {
                background-color: #3292ea;
                color: white;
                padding: 8px 20px;
                border: none;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
                min-width: 100px;
                max-height: 35px;
                margin: 3px;
            }
            QPushButton:hover {
                background-color: #4da2fa;
            }
            QPushButton:pressed {
                background-color: #2a82da;
            }
        """)
        
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.password_input.returnPressed.connect(self.accept)
        self.password_input.setFocus()
        
    def get_password(self):
        """Get the entered password"""
        return self.password_input.text()


class DeveloperAreaPage(QWidget):
    """Simple Developer Area page"""
    
    def __init__(self, main_window=None):
        super().__init__()
        self.main_window = main_window
        logging.info("Initializing simple DeveloperAreaPage...")
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(30)
        
        # Header
        title_label = QLabel("Developer Area")
        title_label.setFont(QFont("Helvetica", 28, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #3292ea;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        subtitle_label = QLabel("Database Management & Analytics Dashboard")
        subtitle_label.setFont(QFont("Helvetica", 16))
        subtitle_label.setStyleSheet("color: #ffffff;")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle_label)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("background-color: #2a3642; min-height: 2px;")
        layout.addWidget(separator)
        
        # Description
        description_label = QLabel(
            "Hier finden Sie Tools zur Verwaltung und Analyse der Tumorboard-Datenbank."
        )
        description_label.setFont(QFont("Helvetica", 14))
        description_label.setStyleSheet("color: #cccccc;")
        description_label.setWordWrap(True)
        description_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(description_label)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(40)
        
        # Database Manager Button
        db_manager_button = QPushButton("🗄️ Database Manager")
        db_manager_button.setStyleSheet("""
            QPushButton {
                background-color: #2a3642;
                border: 2px solid #3292ea;
                border-radius: 15px;
                padding: 20px;
                color: white;
                font-size: 16px;
                font-weight: bold;
                min-height: 100px;
                min-width: 200px;
            }
            QPushButton:hover {
                background-color: #3a4652;
                border-color: #4da2fa;
            }
        """)
        db_manager_button.clicked.connect(self.open_database_manager)
        buttons_layout.addWidget(db_manager_button)
        
        # Database Dashboard Button  
        db_dashboard_button = QPushButton("📊 Database Dashboard")
        db_dashboard_button.setStyleSheet("""
            QPushButton {
                background-color: #2a3642;
                border: 2px solid #3292ea;
                border-radius: 15px;
                padding: 20px;
                color: white;
                font-size: 16px;
                font-weight: bold;
                min-height: 100px;
                min-width: 200px;
            }
            QPushButton:hover {
                background-color: #3a4652;
                border-color: #4da2fa;
            }
        """)
        db_dashboard_button.clicked.connect(self.open_database_dashboard)
        buttons_layout.addWidget(db_dashboard_button)
        
        layout.addLayout(buttons_layout)
        
        # Add spacer
        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        
        logging.info("Simple DeveloperAreaPage UI setup complete.")
    
    def show_styled_message(self, title, message, icon_type):
        """Show a styled message box with proper dark theme"""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setIcon(icon_type)
        
        # Make the dialog more compact
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: #19232D;
                color: white;
                max-width: 400px;
                max-height: 200px;
            }
            QMessageBox QLabel {
                color: white;
                font-size: 13px;
                padding: 8px 15px;
                min-width: 250px;
                max-width: 350px;
                qproperty-wordWrap: false;
            }
            QMessageBox QPushButton {
                background-color: #3292ea;
                color: white;
                padding: 6px 18px;
                border: none;
                border-radius: 5px;
                font-size: 12px;
                font-weight: bold;
                min-width: 70px;
                max-height: 28px;
                margin: 3px;
            }
            QMessageBox QPushButton:hover {
                background-color: #4da2fa;
            }
            QMessageBox QPushButton:pressed {
                background-color: #2a82da;
            }
        """)
        
        # Force compact size
        msg_box.resize(320, 150)
        msg_box.exec()
    
    def show_compact_info_message(self, title, message):
        """Show a very compact information message box"""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setIcon(QMessageBox.Icon.Information)
        
        # Ultra-compact styling
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: #19232D;
                color: white;
                max-width: 300px;
                max-height: 120px;
            }
            QMessageBox QLabel {
                color: white;
                font-size: 12px;
                padding: 5px 10px;
                min-width: 200px;
                max-width: 280px;
                qproperty-wordWrap: false;
            }
            QMessageBox QPushButton {
                background-color: #3292ea;
                color: white;
                padding: 4px 15px;
                border: none;
                border-radius: 4px;
                font-size: 11px;
                font-weight: bold;
                min-width: 50px;
                max-height: 25px;
                margin: 2px;
            }
            QMessageBox QPushButton:hover {
                background-color: #4da2fa;
            }
            QMessageBox QPushButton:pressed {
                background-color: #2a82da;
            }
        """)
    
        msg_box.resize(240, 100)
        msg_box.exec()
        
    def open_database_manager(self):
        """Open database manager in terminal console"""
        try:
            logging.info("Opening Database Manager...")
            
            if self.main_window and hasattr(self.main_window, 'open_cmd_scripts_page'):
                script_key = "database_manager"
                self.main_window.open_cmd_scripts_page(script_key)
                logging.info("Database Manager opened successfully")
            else:
                self.show_styled_message("Fehler", "Konnte Database Manager nicht öffnen.", QMessageBox.Icon.Warning)
                
        except Exception as e:
            logging.error(f"Error opening database manager: {e}")
            self.show_styled_message("Fehler", f"Fehler: {e}", QMessageBox.Icon.Critical)
            
    def open_database_dashboard(self):
        """Open database dashboard in external browser"""
        try:
            logging.info("Opening Database Dashboard...")
            
            import webbrowser
            import sys
            from pathlib import Path
            
            # Add parent directory to path
            sys.path.insert(0, str(Path(__file__).parent.parent))
            
            from utils.dashboard_html_generator import generate_complete_dashboard
            
            # Generate dashboard
            html_file = generate_complete_dashboard(interactive=True)
            if html_file:
                # Open in browser
                html_path = Path(html_file)
                file_url = f"file:///{html_path.as_posix()}"
                webbrowser.open(file_url)
                
                self.show_compact_info_message("Dashboard geöffnet", 
                                              "Das Dashboard wurde in Ihrem Browser geöffnet.")
            else:
                self.show_styled_message("Fehler", "Konnte Dashboard nicht generieren.", QMessageBox.Icon.Warning)
                
        except Exception as e:
            logging.error(f"Error opening dashboard: {e}")
            self.show_styled_message("Fehler", f"Dashboard-Fehler: {e}", QMessageBox.Icon.Critical) 