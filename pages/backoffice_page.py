from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                             QFrame, QMessageBox, QGridLayout, QScrollArea)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
import os
import logging
from pathlib import Path

class BackofficePage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        logging.info("Initializing BackofficePage Dashboard...")
        self.main_window = main_window
        self.setup_ui()
        logging.info("BackofficePage Dashboard initialization complete.")

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
        """Create the prominent Open Tasks section at the top"""
        # Section title
        tasks_title = QLabel("📋 Offene Aufgaben - Übersicht")
        tasks_title.setFont(QFont("Helvetica", 20, QFont.Weight.Bold))
        tasks_title.setStyleSheet("color: #FFA500; margin-bottom: 10px;")
        parent_layout.addWidget(tasks_title)

        # Compact tasks frame
        tasks_frame = QFrame()
        tasks_frame.setStyleSheet("""
            QFrame {
                background-color: #1a2633;
                border: 1px solid #425061;
                border-radius: 8px;
                padding: 15px;
                min-height: 120px;
            }
        """)
        
        tasks_layout = QVBoxLayout(tasks_frame)
        tasks_layout.setSpacing(8)

        # Task items from different categories (clickable)
        self.create_clickable_task_item(tasks_layout, "📊", "Ausstehende Leistungserfassung Tumorboard", 
                                       "12 offene Tumorboard-Abrechnungen für QISM-System", "#DC143C", 
                                       self.open_leistungsabrechnungen)
        
        self.create_clickable_task_item(tasks_layout, "🩺", "Offene Erstkonsultationen", 
                                       "18 wartende Patienten für Terminvergabe (5 dringend)", "#FF4500",
                                       self.open_erstkonsultationen)

        parent_layout.addWidget(tasks_frame)

    def create_task_item(self, parent_layout, icon, title, description, color):
        """Create an individual task item (deprecated - use create_clickable_task_item)"""
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
        
        nav_layout = QGridLayout(nav_frame)
        nav_layout.setSpacing(15)

        # Navigation buttons
        self.create_nav_button(nav_layout, 0, 0, "📊 Leistungsabrechnungen", 
                              "QISM Abrechnungen für Tumorboards verwalten", self.open_leistungsabrechnungen)
        
        self.create_nav_button(nav_layout, 0, 1, "🩺 Erstkonsultationen aufbieten", 
                              "Wartende Patienten für Erstkonsultationen verwalten", self.open_erstkonsultationen)

        parent_layout.addWidget(nav_frame)

    def create_nav_button(self, grid_layout, row, col, title, description, callback):
        """Create a navigation button"""
        button_frame = QFrame()
        button_frame.setStyleSheet("""
            QFrame {
                background-color: #232F3B;
                border-radius: 8px;
                padding: 15px;
                border: 1px solid #425061;
            }
            QFrame:hover {
                background-color: #2A3642;
                border-color: #00BFFF;
            }
        """)
        button_frame.setCursor(Qt.CursorShape.PointingHandCursor)
        button_frame.mousePressEvent = lambda event: callback()
        
        button_layout = QVBoxLayout(button_frame)
        button_layout.setSpacing(8)
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Helvetica", 13, QFont.Weight.Bold))
        title_label.setStyleSheet("color: white;")
        button_layout.addWidget(title_label)
        
        desc_label = QLabel(description)
        desc_label.setFont(QFont("Helvetica", 10))
        desc_label.setStyleSheet("color: #CCCCCC;")
        desc_label.setWordWrap(True)
        button_layout.addWidget(desc_label)
        
        grid_layout.addWidget(button_frame, row, col)

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