from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                             QFrame, QMessageBox, QGridLayout, QScrollArea)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
import os
import logging
from pathlib import Path
import pandas as pd
import re
from datetime import datetime

# Import billing tracker and path management
from utils.billing_tracker import BillingTracker
from utils.path_management import BackofficePathManager

class BackofficePage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        logging.info("Initializing BackofficePage Dashboard...")
        self.main_window = main_window
        self.billing_tracker = BillingTracker()
        self.setup_ui()
        logging.info("BackofficePage Dashboard initialization complete.")

    def refresh_status(self):
        """Refresh the status of all task categories"""
        logging.info("Refreshing backoffice status indicators...")
        
        try:
            # Re-calculate all status information
            billing_status = self.get_billing_status()
            kat_i_status = self.get_category_status("Kat_I.xlsx")
            kat_ii_status = self.get_category_status("Kat_II.xlsx")
            kat_iii_status = self.get_category_status("Kat_III.xlsx")
            
            # Find and update the existing status buttons
            # We need to rebuild the open tasks section with fresh data
            self.create_open_tasks_section_refresh(billing_status, kat_i_status, kat_ii_status, kat_iii_status)
            
            logging.info("Backoffice status refresh completed successfully")
            
        except Exception as e:
            logging.error(f"Error refreshing backoffice status: {e}")

    def create_open_tasks_section_refresh(self, billing_status, kat_i_status, kat_ii_status, kat_iii_status):
        """Refresh the open tasks section with new status data"""
        try:
            # Find the main layout and the tasks frame
            main_layout = self.layout()
            if main_layout is None:
                return
                
            # Find and remove the old tasks frame
            tasks_frame_to_remove = None
            for i in range(main_layout.count()):
                item = main_layout.itemAt(i)
                if item and item.widget():
                    widget = item.widget()
                    # Look for the tasks frame by checking its children
                    if hasattr(widget, 'layout') and widget.layout():
                        layout = widget.layout()
                        if layout.count() > 0:
                            first_item = layout.itemAt(0)
                            if first_item and first_item.widget():
                                first_widget = first_item.widget()
                                if isinstance(first_widget, QLabel) and "Offene Aufgaben" in first_widget.text():
                                    tasks_frame_to_remove = widget
                                    break
            
            if tasks_frame_to_remove:
                main_layout.removeWidget(tasks_frame_to_remove)
                tasks_frame_to_remove.deleteLater()
                
                # Create new tasks section with updated data
                self.create_open_tasks_section_with_data(main_layout, billing_status, kat_i_status, kat_ii_status, kat_iii_status)
                
        except Exception as e:
            logging.error(f"Error refreshing open tasks section: {e}")

    def create_open_tasks_section_with_data(self, parent_layout, billing_status, kat_i_status, kat_ii_status, kat_iii_status):
        """Create the open tasks section with provided status data"""
        # Section title
        tasks_title = QLabel("📋 Offene Aufgaben - Übersicht")
        tasks_title.setFont(QFont("Helvetica", 20, QFont.Weight.Bold))
        tasks_title.setStyleSheet("color: #FFA500; margin-bottom: 10px;")
        parent_layout.insertWidget(1, tasks_title)  # Insert after the main title

        # Tasks frame
        tasks_frame = QFrame()
        tasks_frame.setStyleSheet("""
            QFrame {
                background-color: #1a2633;
                border: 1px solid #425061;
                border-radius: 8px;
                padding: 25px;
            }
        """)
        
        tasks_layout = QVBoxLayout(tasks_frame)
        tasks_layout.setSpacing(15)

        # Create status buttons with provided data
        self.create_status_button(tasks_layout, "Abrechnungen", billing_status, self.open_leistungsabrechnungen)
        self.create_status_button(tasks_layout, "Kategorie I", kat_i_status, self.open_kategorie_i)
        self.create_status_button(tasks_layout, "Kategorie II", kat_ii_status, self.open_kategorie_ii)
        self.create_status_button(tasks_layout, "Kategorie III", kat_iii_status, self.open_kategorie_iii)

        parent_layout.insertWidget(2, tasks_frame)  # Insert after the title

    def setup_ui(self):
        """Setup the dashboard user interface"""
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(30, 20, 30, 30)
        main_layout.setSpacing(20)
        self.setLayout(main_layout)

        # Title
        title_label = QLabel("Backoffice Dashboard")
        title_label.setFont(QFont("Helvetica", 28, QFont.Weight.Bold))
        title_label.setStyleSheet("color: white; margin-bottom: 10px;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)

        # Scrollable area for the dashboard content
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

        # 1. OPEN TASKS SECTION (large, prominent)
        self.create_open_tasks_section(content_layout)

        # 2. NAVIGATION & TOOLS SECTION
        self.create_navigation_section(content_layout)

        # 3. COMPLETED TUMORBOARDS SECTION
        self.create_completed_tumorboards_section(content_layout)

        # Set scroll area content
        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)

    def create_open_tasks_section(self, parent_layout):
        """Create the prominent Open Tasks section with dynamic status buttons"""
        # Section title
        tasks_title = QLabel("📋 Offene Aufgaben - Übersicht")
        tasks_title.setFont(QFont("Helvetica", 20, QFont.Weight.Bold))
        tasks_title.setStyleSheet("color: #FFA500; margin-bottom: 10px;")
        parent_layout.addWidget(tasks_title)

        # Tasks frame
        tasks_frame = QFrame()
        tasks_frame.setStyleSheet("""
            QFrame {
                background-color: #1a2633;
                border: 1px solid #425061;
                border-radius: 8px;
                padding: 25px;
            }
        """)
        
        tasks_layout = QVBoxLayout(tasks_frame)
        tasks_layout.setSpacing(15)

        # Calculate open tasks with debug logging
        logging.info("Calculating status for all categories...")
        
        billing_status = self.get_billing_status()
        logging.info(f"Billing status: {billing_status}")
        
        kat_i_status = self.get_category_status("Kat_I.xlsx")
        logging.info(f"Kat I status: {kat_i_status}")
        
        kat_ii_status = self.get_category_status("Kat_II.xlsx")
        logging.info(f"Kat II status: {kat_ii_status}")
        
        kat_iii_status = self.get_category_status("Kat_III.xlsx")
        logging.info(f"Kat III status: {kat_iii_status}")

        # 1. Billing Status Button
        self.create_status_button(tasks_layout, "Abrechnungen", billing_status, self.open_leistungsabrechnungen)
        
        # 2. Category I Status Button
        self.create_status_button(tasks_layout, "Kategorie I", kat_i_status, self.open_kategorie_i)
        
        # 3. Category II Status Button
        self.create_status_button(tasks_layout, "Kategorie II", kat_ii_status, self.open_kategorie_ii)
        
        # 4. Category III Status Button
        self.create_status_button(tasks_layout, "Kategorie III", kat_iii_status, self.open_kategorie_iii)

        parent_layout.addWidget(tasks_frame)

    def create_status_button(self, parent_layout, title, status_info, callback):
        """Create a status button with dynamic text and color (styled like CategoryButton)"""
        logging.info(f"Creating status button for {title} with status: {status_info}")
        
        task_item = QFrame()
        task_item.setFixedHeight(80)
        task_item.setMinimumWidth(600)
        task_item.setStyleSheet("""
            QFrame {
                background-color: #114473;
                border: none;
                border-radius: 10px;
                padding: 5px;
            }
            QFrame:hover {
                background-color: #1a5a9e;
            }
        """)
        task_item.setCursor(Qt.CursorShape.PointingHandCursor)
        task_item.mousePressEvent = lambda event: callback()
        
        # Create layout for button content
        layout = QHBoxLayout(task_item)
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(10)

        # Title
        title_label = QLabel(f"{title}:")
        title_label.setFont(QFont("Calibri", 14, QFont.Weight.Bold))
        title_label.setStyleSheet("color: white; background: transparent;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        title_label.setFixedWidth(140)
        layout.addWidget(title_label)
        
        # Status text with proper color coding
        status_label = QLabel(status_info['text'])
        status_label.setFont(QFont("Calibri", 13, QFont.Weight.Bold))
        status_label.setStyleSheet(f"color: {status_info['color']}; background: transparent;")
        status_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        status_label.setWordWrap(True)
        layout.addWidget(status_label)
        
        layout.addStretch()
        
        logging.info(f"Status button created - Title: '{title_label.text()}', Status: '{status_label.text()}', Color: '{status_info['color']}'")

        parent_layout.addWidget(task_item)

    def get_billing_status(self):
        """Get the billing status for open billing tasks"""
        try:
            # Get all finalized tumorboards
            finalized_tumorboards = self.get_finalized_tumorboards()
            
            # Check billing status for each using the correct method
            unbilled_tumorboards = []
            for tb in finalized_tumorboards:
                billing_status = self.billing_tracker.get_billing_status(tb['entity'], tb['date'])
                if billing_status is None:  # Not billed yet
                    unbilled_tumorboards.append(tb)
            
            if not unbilled_tumorboards:
                return {
                    'text': "alles bearbeitet",
                    'color': '#4CAF50'  # Green (same as categories)
                }
            else:
                # Create description with tumorboard names
                if len(unbilled_tumorboards) == 1:
                    tb = unbilled_tumorboards[0]
                    text = f"1 Abrechnung ausstehend ({tb['entity']} vom {tb['date']})"
                else:
                    tb_names = [f"{tb['entity']} vom {tb['date']}" for tb in unbilled_tumorboards[:2]]
                    if len(unbilled_tumorboards) > 2:
                        text = f"{len(unbilled_tumorboards)} Abrechnungen ausstehend ({', '.join(tb_names)}, ...)"
                    else:
                        text = f"{len(unbilled_tumorboards)} Abrechnungen ausstehend ({', '.join(tb_names)})"
                
                return {
                    'text': text,
                    'color': '#FFD700'  # Yellow (consistent with categories)
                }
        except Exception as e:
            logging.error(f"Error getting billing status: {e}")
            return {
                'text': "Status nicht verfügbar",
                'color': '#FF6B6B'  # Red
            }

    def get_category_status(self, filename):
        """Get the status for a specific category Excel file (same logic as CategoryButton)"""
        try:
            # Use centralized path management with network/local priority
            backoffice_dir, using_network = BackofficePathManager.get_backoffice_path(show_warnings=True)
            excel_path = backoffice_dir / filename
            
            if not excel_path.exists():
                return {
                    'text': f"Datei nicht gefunden",
                    'color': '#FF6B6B'  # Light red for errors
                }
            
            # Read Excel file
            df = pd.read_excel(excel_path, engine='openpyxl')
            
            if df.empty:
                # Wording depends on category
                if "Kat_III" in filename:
                    no_pending_text = "keine Konsil-Eingänge ausstehend"
                else:
                    no_pending_text = "keine Erstkons-Aufgebote ausstehend"
                return {
                    'text': no_pending_text,
                    'color': '#4CAF50'  # Green
                }
            
            # Check if we have enough columns
            if len(df.columns) < 14:
                return {
                    'text': f"Excel-Format fehlerhaft",
                    'color': '#FF6B6B'  # Light red for errors
                }
            
            # Count "Nein" entries in column N (index 13) - same logic as erstkonsultationen
            status_column = df.iloc[:, 13]  # Column N (0-based index 13)
            
            pending_count = 0
            for value in status_column:
                if str(value).strip().lower() == 'nein':
                    pending_count += 1
            
            # Generate text and color based on category (exact same as CategoryButton)
            if pending_count == 0:
                if "Kat_III" in filename:
                    text = "keine Konsil-Eingänge ausstehend"
                else:
                    text = "keine Erstkons-Aufgebote ausstehend"
                color = '#4CAF50'  # Green
            else:
                # Determine category based on filename with precise matching to avoid substring collisions
                if "Kat_III" in filename:
                    if pending_count == 1:
                        text = f"{pending_count} Konsil-Eingang ausstehend"
                    else:
                        text = f"{pending_count} Konsil-Eingänge ausstehend"
                    color = '#FFCC00'  # Bright Yellow
                elif "Kat_II" in filename:
                    if pending_count == 1:
                        text = f"{pending_count} Erstkons-Aufgebot ausstehend"
                    else:
                        text = f"{pending_count} Erstkons-Aufgebote ausstehend"
                    color = '#FF8800'  # Bright Orange
                elif "Kat_I" in filename:
                    if pending_count == 1:
                        text = f"{pending_count} Erstkons-Aufgebot ausstehend"
                    else:
                        text = f"{pending_count} Erstkons-Aufgebote ausstehend"
                    color = '#f93737'  # Bright Red
            
            logging.info(f"Category {filename}: {pending_count} pending, color: {color}, text: {text}")
            
            return {
                'text': text,
                'color': color
            }
            
        except Exception as e:
            logging.error(f"Error getting category status for {filename}: {e}")
            return {
                'text': f"Status nicht verfügbar",
                'color': '#FF6B6B'  # Light red for errors
            }

    def get_finalized_tumorboards(self):
        """Get all finalized tumorboards (same logic as leistungsabrechnungen page)"""
        try:
            # Use centralized path management for tumorboard base path
            tumorboards_path, using_network = BackofficePathManager.get_tumorboard_base_path()
            if not tumorboards_path.exists():
                return []
            
            finalized_tumorboards = []
            
            # Get all entity folders
            entity_folders = [f for f in tumorboards_path.iterdir() 
                            if f.is_dir() and not f.name.startswith('_') and not f.name.startswith('__')]
            
            for entity_folder in entity_folders:
                entity_name = entity_folder.name
                
                # Look for date folders in this entity
                date_folders = [f for f in entity_folder.iterdir() if f.is_dir()]
                
                for date_folder in date_folders:
                    # Check if folder name matches date format (dd.mm.yyyy)
                    if self.is_valid_date_format(date_folder.name):
                        # Check for timestamp file (finalized marker)
                        timestamp_files = list(date_folder.glob("*timestamp*"))
                        
                        if timestamp_files:
                            # Check for Excel file
                            excel_file = date_folder / f"{date_folder.name}.xlsx"
                            
                            if excel_file.exists():
                                finalized_tumorboards.append({
                                    'entity': entity_name,
                                    'date': date_folder.name,
                                    'path': str(date_folder)
                                })
            
            return finalized_tumorboards
            
        except Exception as e:
            logging.error(f"Error getting finalized tumorboards: {e}")
            return []

    def is_valid_date_format(self, folder_name):
        """Check if folder name matches dd.mm.yyyy format"""
        pattern = r"^\d{2}\.\d{2}\.\d{4}$"
        return bool(re.match(pattern, folder_name))

    def open_kategorie_i(self):
        """Open the Kategorie I page"""
        logging.info("Opening Kategorie I page...")
        
        if not self.main_window.check_tumorboard_session_before_navigation():
            return
        
        from pages.backoffice_kat_I_page import BackofficeKatIPage
        
        # Check if page already exists
        kat_i_page = None
        for i in range(self.main_window.stacked_widget.count()):
            widget = self.main_window.stacked_widget.widget(i)
            if isinstance(widget, BackofficeKatIPage):
                kat_i_page = widget
                break
        
        if kat_i_page is None:
            logging.info("Creating new BackofficeKatIPage instance.")
            kat_i_page = BackofficeKatIPage(self.main_window)
            self.main_window.stacked_widget.addWidget(kat_i_page)
        else:
            logging.info("Found existing BackofficeKatIPage, refreshing data.")
            kat_i_page.refresh_data()
        
        self.main_window.stacked_widget.setCurrentWidget(kat_i_page)
        logging.info("Navigated to BackofficeKatIPage.")

    def open_kategorie_ii(self):
        """Open the Kategorie II page"""
        logging.info("Opening Kategorie II page...")
        
        if not self.main_window.check_tumorboard_session_before_navigation():
            return
        
        from pages.backoffice_kat_II_page import BackofficeKatIIPage
        
        # Check if page already exists
        kat_ii_page = None
        for i in range(self.main_window.stacked_widget.count()):
            widget = self.main_window.stacked_widget.widget(i)
            if isinstance(widget, BackofficeKatIIPage):
                kat_ii_page = widget
                break
        
        if kat_ii_page is None:
            logging.info("Creating new BackofficeKatIIPage instance.")
            kat_ii_page = BackofficeKatIIPage(self.main_window)
            self.main_window.stacked_widget.addWidget(kat_ii_page)
        else:
            logging.info("Found existing BackofficeKatIIPage, refreshing data.")
            kat_ii_page.refresh_data()
        
        self.main_window.stacked_widget.setCurrentWidget(kat_ii_page)
        logging.info("Navigated to BackofficeKatIIPage.")

    def open_kategorie_iii(self):
        """Open the Kategorie III page"""
        logging.info("Opening Kategorie III page...")
        
        if not self.main_window.check_tumorboard_session_before_navigation():
            return
        
        from pages.backoffice_kat_III_page import BackofficeKatIIIPage
        
        # Check if page already exists
        kat_iii_page = None
        for i in range(self.main_window.stacked_widget.count()):
            widget = self.main_window.stacked_widget.widget(i)
            if isinstance(widget, BackofficeKatIIIPage):
                kat_iii_page = widget
                break
        
        if kat_iii_page is None:
            logging.info("Creating new BackofficeKatIIIPage instance.")
            kat_iii_page = BackofficeKatIIIPage(self.main_window)
            self.main_window.stacked_widget.addWidget(kat_iii_page)
        else:
            logging.info("Found existing BackofficeKatIIIPage, refreshing data.")
            kat_iii_page.refresh_data()
        
        self.main_window.stacked_widget.setCurrentWidget(kat_iii_page)
        logging.info("Navigated to BackofficeKatIIIPage.")

    def create_task_item(self, parent_layout, icon, title, description, color):
        """Create an individual task item (deprecated - use create_status_button)"""
        task_item = QFrame()
        task_item.setStyleSheet(f"""
            QFrame {{
                background-color: #232F3B;
                border-radius: 6px;
                padding: 8px;
                margin: 2px 0;
            }}
            QFrame:hover {{
                background-color: #2A3642;
            }}
        """)
        
        task_layout = QHBoxLayout(task_item)
        task_layout.setSpacing(12)
        task_layout.setContentsMargins(10, 6, 10, 6)

        # Icon
        icon_label = QLabel(icon)
        icon_label.setFont(QFont("Segoe UI Emoji", 16))
        icon_label.setFixedWidth(30)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        task_layout.addWidget(icon_label)

        # Text content
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Helvetica", 12, QFont.Weight.Bold))
        title_label.setStyleSheet("color: white;")
        text_layout.addWidget(title_label)
        
        desc_label = QLabel(description)
        desc_label.setFont(QFont("Helvetica", 10))
        desc_label.setStyleSheet("color: #CCCCCC;")
        desc_label.setWordWrap(True)
        text_layout.addWidget(desc_label)
        
        task_layout.addLayout(text_layout)
        task_layout.addStretch()

        parent_layout.addWidget(task_item)

    def create_clickable_task_item(self, parent_layout, icon, title, description, color, callback):
        """Create a clickable task item that navigates to a specific page"""
        task_item = QFrame()
        task_item.setStyleSheet(f"""
            QFrame {{
                background-color: #232F3B;
                border-radius: 6px;
                padding: 8px;
                margin: 2px 0;
                border: 1px solid #425061;
            }}
            QFrame:hover {{
                background-color: #2A3642;
                border-color: {color};
                cursor: pointer;
            }}
        """)
        task_item.setCursor(Qt.CursorShape.PointingHandCursor)
        task_item.mousePressEvent = lambda event: callback()
        
        task_layout = QHBoxLayout(task_item)
        task_layout.setSpacing(12)
        task_layout.setContentsMargins(10, 6, 10, 6)

        # Icon
        icon_label = QLabel(icon)
        icon_label.setFont(QFont("Segoe UI Emoji", 16))
        icon_label.setFixedWidth(30)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        task_layout.addWidget(icon_label)

        # Text content
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Helvetica", 12, QFont.Weight.Bold))
        title_label.setStyleSheet("color: white;")
        text_layout.addWidget(title_label)
        
        desc_label = QLabel(description)
        desc_label.setFont(QFont("Helvetica", 10))
        desc_label.setStyleSheet("color: #CCCCCC;")
        desc_label.setWordWrap(True)
        text_layout.addWidget(desc_label)
        
        task_layout.addLayout(text_layout)
        
        # Add arrow indicator
        arrow_label = QLabel("→")
        arrow_label.setFont(QFont("Helvetica", 16, QFont.Weight.Bold))
        arrow_label.setStyleSheet(f"color: {color};")
        arrow_label.setFixedWidth(20)
        arrow_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        task_layout.addWidget(arrow_label)

        parent_layout.addWidget(task_item)

    def create_navigation_section(self, parent_layout):
        """Create the navigation and tools section"""
        # Section title
        nav_title = QLabel("🔧 Navigation & Tools")
        nav_title.setFont(QFont("Helvetica", 18, QFont.Weight.Bold))
        nav_title.setStyleSheet("color: #00BFFF; margin-bottom: 10px; margin-top: 15px;")
        parent_layout.addWidget(nav_title)

        # Navigation frame
        nav_frame = QFrame()
        nav_frame.setStyleSheet("""
            QFrame {
                background-color: #19232D;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        
        nav_layout = QHBoxLayout(nav_frame)
        nav_layout.setSpacing(30)

        # Leistungsabrechnungen button
        leistungsabrechnungen_button = QPushButton("📊 Leistungsabrechnungen")
        leistungsabrechnungen_button.setFont(QFont("Helvetica", 14, QFont.Weight.Bold))
        leistungsabrechnungen_button.setFixedHeight(50)
        leistungsabrechnungen_button.setCursor(Qt.CursorShape.PointingHandCursor)
        leistungsabrechnungen_button.setStyleSheet("""
            QPushButton {
                background-color: #114473;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                text-align: left;
            }
            QPushButton:pressed {
                background-color: #0d3355;
            }
        """)
        leistungsabrechnungen_button.clicked.connect(self.open_leistungsabrechnungen)
        nav_layout.addWidget(leistungsabrechnungen_button)
        
        # Erstkonsultationen button
        erstkonsultationen_button = QPushButton("🩺 Erstkonsultationen aufbieten")
        erstkonsultationen_button.setFont(QFont("Helvetica", 14, QFont.Weight.Bold))
        erstkonsultationen_button.setFixedHeight(50)
        erstkonsultationen_button.setCursor(Qt.CursorShape.PointingHandCursor)
        erstkonsultationen_button.setStyleSheet("""
            QPushButton {
                background-color: #114473;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                text-align: left;
            }
            QPushButton:pressed {
                background-color: #0d3355;
            }
        """)
        erstkonsultationen_button.clicked.connect(self.open_erstkonsultationen)
        nav_layout.addWidget(erstkonsultationen_button)
        
        # Tumorboard Export button
        tumorboard_export_button = QPushButton("📋 Tumorboard Export")
        tumorboard_export_button.setFont(QFont("Helvetica", 14, QFont.Weight.Bold))
        tumorboard_export_button.setFixedHeight(50)
        tumorboard_export_button.setCursor(Qt.CursorShape.PointingHandCursor)
        tumorboard_export_button.setStyleSheet("""
            QPushButton {
                background-color: #114473;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                text-align: left;
            }
            QPushButton:pressed {
                background-color: #0d3355;
            }
        """)
        tumorboard_export_button.clicked.connect(self.open_tumorboard_export)
        nav_layout.addWidget(tumorboard_export_button)

        parent_layout.addWidget(nav_frame)

    def create_completed_tumorboards_section(self, parent_layout):
        """Create the completed tumorboards section"""
        # Section title
        completed_title = QLabel("✅ Abgeschlossene Tumorboards")
        completed_title.setFont(QFont("Helvetica", 18, QFont.Weight.Bold))
        completed_title.setStyleSheet("color: #90EE90; margin-bottom: 10px; margin-top: 15px;")
        parent_layout.addWidget(completed_title)

        # Completed tumorboards frame
        completed_frame = QFrame()
        completed_frame.setStyleSheet("""
            QFrame {
                background-color: #19232D;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        
        completed_layout = QVBoxLayout(completed_frame)
        completed_layout.setSpacing(15)

        # Description
        desc_label = QLabel("Zugriff auf alle abgeschlossenen Tumorboard-Sessions für Nachbearbeitung und Abrechnung")
        desc_label.setFont(QFont("Helvetica", 12))
        desc_label.setStyleSheet("color: #CCCCCC; margin-bottom: 10px;")
        desc_label.setWordWrap(True)
        completed_layout.addWidget(desc_label)

        # Main button
        self.completed_tumorboards_button = QPushButton("📁 Abgeschlossene Tumorboards öffnen")
        self.completed_tumorboards_button.setFixedHeight(50)
        self.completed_tumorboards_button.setFont(QFont("Helvetica", 14, QFont.Weight.Bold))
        self.completed_tumorboards_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.completed_tumorboards_button.setStyleSheet("""
            QPushButton {
                background-color: #114473;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #1a5a9e;
            }
            QPushButton:pressed {
                background-color: #0d3355;
            }
        """)
        self.completed_tumorboards_button.clicked.connect(self.open_completed_tumorboards)
        completed_layout.addWidget(self.completed_tumorboards_button)

        parent_layout.addWidget(completed_frame)

    def open_leistungsabrechnungen(self):
        """Open the Leistungsabrechnungen page"""
        logging.info("Opening Leistungsabrechnungen page...")
        
        # Check if we came from session navigation
        if not self.main_window.check_tumorboard_session_before_navigation():
            return  # User cancelled navigation
        
        from pages.backoffice_page_leistungsabrechnungen import BackofficePageLeistungsabrechnungen
        
        # Check if page already exists
        leistungsabrechnungen_page = None
        for i in range(self.main_window.stacked_widget.count()):
            widget = self.main_window.stacked_widget.widget(i)
            if isinstance(widget, BackofficePageLeistungsabrechnungen):
                leistungsabrechnungen_page = widget
                break
        
        if leistungsabrechnungen_page is None:
            logging.info("Creating new BackofficePageLeistungsabrechnungen instance.")
            leistungsabrechnungen_page = BackofficePageLeistungsabrechnungen(self.main_window)
            self.main_window.stacked_widget.addWidget(leistungsabrechnungen_page)
        else:
            logging.info("Found existing BackofficePageLeistungsabrechnungen.")
        
        self.main_window.stacked_widget.setCurrentWidget(leistungsabrechnungen_page)
        logging.info("Navigated to BackofficePageLeistungsabrechnungen.")

    def open_erstkonsultationen(self):
        """Open the Erstkonsultationen page"""
        logging.info("Opening Erstkonsultationen page...")
        
        # Check if we came from session navigation
        if not self.main_window.check_tumorboard_session_before_navigation():
            return  # User cancelled navigation
        
        from pages.backoffice_page_erstkonsultationen import BackofficePageErstkonsultationen
        
        # Check if page already exists
        erstkonsultationen_page = None
        for i in range(self.main_window.stacked_widget.count()):
            widget = self.main_window.stacked_widget.widget(i)
            if isinstance(widget, BackofficePageErstkonsultationen):
                erstkonsultationen_page = widget
                break
        
        if erstkonsultationen_page is None:
            logging.info("Creating new BackofficePageErstkonsultationen instance.")
            erstkonsultationen_page = BackofficePageErstkonsultationen(self.main_window)
            self.main_window.stacked_widget.addWidget(erstkonsultationen_page)
        else:
            logging.info("Found existing BackofficePageErstkonsultationen.")
        
        self.main_window.stacked_widget.setCurrentWidget(erstkonsultationen_page)
        logging.info("Navigated to BackofficePageErstkonsultationen.")

    def open_tumorboard_export(self):
        """Open the Tumorboard Export script via terminal page"""
        logging.info("Opening Tumorboard Export script...")
        
        # Check if we came from session navigation
        if not self.main_window.check_tumorboard_session_before_navigation():
            return  # User cancelled navigation
        
        # Open the terminal page with the tumorboard export script (from Backoffice context)
        if self.main_window and hasattr(self.main_window, 'open_cmd_scripts_page_from_backoffice'):
            self.main_window.open_cmd_scripts_page_from_backoffice('tumorboard_export')
        else:
            logging.error("Cannot access main_window.open_cmd_scripts_page_from_backoffice for tumorboard export")
            QMessageBox.critical(self, "Fehler", "Tumorboard Export konnte nicht geöffnet werden.")
        
        logging.info("Tumorboard Export script launched.")



    def open_completed_tumorboards(self):
        """Open the completed tumorboards page"""
        logging.info("Opening completed tumorboards page...")
        
        # Check if we came from session navigation
        if not self.main_window.check_tumorboard_session_before_navigation():
            return  # User cancelled navigation
        
        from pages.backoffice_tumorboards_page import BackofficeTumorboardsPage
        
        # Check if page already exists
        backoffice_tumorboards_page = None
        for i in range(self.main_window.stacked_widget.count()):
            widget = self.main_window.stacked_widget.widget(i)
            if isinstance(widget, BackofficeTumorboardsPage):
                backoffice_tumorboards_page = widget
                break
        
        if backoffice_tumorboards_page is None:
            logging.info("Creating new BackofficeTumorboardsPage instance.")
            backoffice_tumorboards_page = BackofficeTumorboardsPage(self.main_window)
            self.main_window.stacked_widget.addWidget(backoffice_tumorboards_page)
        else:
            logging.info("Found existing BackofficeTumorboardsPage, refreshing data.")
            # Refresh the page data
            backoffice_tumorboards_page.refresh_completed_tumorboards()
        
        self.main_window.stacked_widget.setCurrentWidget(backoffice_tumorboards_page)
        logging.info("Navigated to BackofficeTumorboardsPage.") 