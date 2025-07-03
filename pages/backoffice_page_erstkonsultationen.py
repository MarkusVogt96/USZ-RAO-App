from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                             QFrame, QMessageBox, QGridLayout, QScrollArea, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QComboBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
import os
import logging
from pathlib import Path

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

        # Header with back button and title
        header_layout = QHBoxLayout()
        header_layout.setSpacing(15)

        # Back button
        back_button = QPushButton("← Zurück")
        back_button.setFont(QFont("Helvetica", 12))
        back_button.setFixedSize(100, 40)
        back_button.setStyleSheet("""
            QPushButton {
                background-color: #425061;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 15px;
            }
            QPushButton:hover {
                background-color: #5A6B7D;
            }
            QPushButton:pressed {
                background-color: #324252;
            }
        """)
        back_button.clicked.connect(self.go_back)
        header_layout.addWidget(back_button)

        # Title
        title_label = QLabel("🩺 Erstkonsultationen aufbieten")
        title_label.setFont(QFont("Helvetica", 28, QFont.Weight.Bold))
        title_label.setStyleSheet("color: white;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()

        main_layout.addLayout(header_layout)

        # Content
        self.create_content(main_layout)

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

        # Overview section
        self.create_overview_section(content_layout)

        # Pending consultations section
        self.create_pending_consultations_section(content_layout)

        # Set scroll area content
        scroll_area.setWidget(content_widget)
        parent_layout.addWidget(scroll_area)

    def create_overview_section(self, parent_layout):
        """Create overview section with statistics"""
        overview_title = QLabel("📊 Übersicht Ausstehende Erstkonsultationen")
        overview_title.setFont(QFont("Helvetica", 20, QFont.Weight.Bold))
        overview_title.setStyleSheet("color: #FFA500; margin-bottom: 10px;")
        parent_layout.addWidget(overview_title)

        # Statistics frame
        stats_frame = QFrame()
        stats_frame.setStyleSheet("""
            QFrame {
                background-color: #1a2633;
                border: 1px solid #425061;
                border-radius: 8px;
                padding: 20px;
            }
        """)
        
        stats_layout = QGridLayout(stats_frame)
        stats_layout.setSpacing(20)

        # Create stat cards
        self.create_stat_card(stats_layout, 0, 0, "📋", "Offene Termine", "18", "#DC143C")
        self.create_stat_card(stats_layout, 0, 1, "⏱️", "Dringend (< 7 Tage)", "5", "#FF4500")
        self.create_stat_card(stats_layout, 0, 2, "👥", "Wartende Patienten", "23", "#FFA500")

        parent_layout.addWidget(stats_frame)

    def create_stat_card(self, grid_layout, row, col, icon, title, value, color):
        """Create a statistics card"""
        card_frame = QFrame()
        card_frame.setStyleSheet(f"""
            QFrame {{
                background-color: #232F3B;
                border-radius: 8px;
                padding: 15px;
                border: 1px solid #425061;
            }}
        """)
        
        card_layout = QVBoxLayout(card_frame)
        card_layout.setSpacing(8)
        card_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Icon
        icon_label = QLabel(icon)
        icon_label.setFont(QFont("Segoe UI Emoji", 24))
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(icon_label)
        
        # Title
        title_label = QLabel(title)
        title_label.setFont(QFont("Helvetica", 11))
        title_label.setStyleSheet("color: #CCCCCC;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(title_label)
        
        # Value
        value_label = QLabel(value)
        value_label.setFont(QFont("Helvetica", 16, QFont.Weight.Bold))
        value_label.setStyleSheet(f"color: {color};")
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(value_label)
        
        grid_layout.addWidget(card_frame, row, col)

    def create_pending_consultations_section(self, parent_layout):
        """Create section showing pending consultations"""
        consultations_title = QLabel("👥 Ausstehende Erstkonsultationen")
        consultations_title.setFont(QFont("Helvetica", 18, QFont.Weight.Bold))
        consultations_title.setStyleSheet("color: #00BFFF; margin-bottom: 10px; margin-top: 15px;")
        parent_layout.addWidget(consultations_title)

        # Table frame
        table_frame = QFrame()
        table_frame.setStyleSheet("""
            QFrame {
                background-color: #19232D;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        
        table_layout = QVBoxLayout(table_frame)
        
        # Filter section
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(15)
        
        filter_label = QLabel("Filter:")
        filter_label.setFont(QFont("Helvetica", 12))
        filter_label.setStyleSheet("color: white;")
        filter_layout.addWidget(filter_label)
        
        self.priority_filter = QComboBox()
        self.priority_filter.addItems(["Alle", "Dringend", "Normal", "Niedrig"])
        self.priority_filter.setStyleSheet("""
            QComboBox {
                background-color: #232F3B;
                border: 1px solid #425061;
                border-radius: 4px;
                padding: 5px;
                color: white;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                width: 12px;
                height: 12px;
            }
        """)
        filter_layout.addWidget(self.priority_filter)
        
        filter_layout.addStretch()
        table_layout.addLayout(filter_layout)
        
        # Create table
        self.consultations_table = QTableWidget()
        self.consultations_table.setColumnCount(6)
        self.consultations_table.setHorizontalHeaderLabels([
            "Patient", "Tumorart", "Anmeldedatum", "Priorität", "Status", "Aktionen"
        ])
        
        # Style the table
        self.consultations_table.setStyleSheet("""
            QTableWidget {
                background-color: #232F3B;
                border: 1px solid #425061;
                border-radius: 6px;
                color: white;
                gridline-color: #425061;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #425061;
            }
            QTableWidget::item:selected {
                background-color: #425061;
            }
            QHeaderView::section {
                background-color: #425061;
                color: white;
                padding: 10px;
                border: none;
                font-weight: bold;
            }
        """)
        
        # Set table properties
        self.consultations_table.horizontalHeader().setStretchLastSection(True)
        self.consultations_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.consultations_table.setAlternatingRowColors(True)
        self.consultations_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        
        # Add sample data
        self.populate_consultations_table()
        
        table_layout.addWidget(self.consultations_table)
        parent_layout.addWidget(table_frame)

    def populate_consultations_table(self):
        """Populate the consultations table with sample data"""
        sample_data = [
            ("Müller, Anna", "Glioblastom", "10.01.2025", "Dringend", "Wartend", "Aufbieten"),
            ("Schmidt, Peter", "Lungenkarzinom", "12.01.2025", "Normal", "Wartend", "Aufbieten"),
            ("Weber, Maria", "Mammakarzinom", "15.01.2025", "Dringend", "Wartend", "Aufbieten"),
            ("Meier, Hans", "Prostatakarzinom", "16.01.2025", "Normal", "Wartend", "Aufbieten"),
            ("Fischer, Lisa", "Ovarialkarzinom", "18.01.2025", "Niedrig", "Wartend", "Aufbieten"),
            ("Bauer, Klaus", "Rektumkarzinom", "19.01.2025", "Dringend", "Wartend", "Aufbieten"),
            ("Huber, Sophie", "Hodgkin-Lymphom", "20.01.2025", "Normal", "Wartend", "Aufbieten")
        ]
        
        self.consultations_table.setRowCount(len(sample_data))
        
        for row, data in enumerate(sample_data):
            for col, value in enumerate(data):
                if col == 5:  # Actions column
                    action_btn = QPushButton("📅 Aufbieten")
                    action_btn.setStyleSheet("""
                        QPushButton {
                            background-color: #114473;
                            color: white;
                            border: none;
                            border-radius: 4px;
                            padding: 6px 12px;
                        }
                        QPushButton:hover {
                            background-color: #1a5a9e;
                        }
                    """)
                    action_btn.clicked.connect(lambda checked, r=row: self.schedule_consultation(r))
                    self.consultations_table.setCellWidget(row, col, action_btn)
                else:
                    item = QTableWidgetItem(str(value))
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    if col == 3:  # Priority column
                        if value == "Dringend":
                            item.setForeground(Qt.GlobalColor.red)
                        elif value == "Normal":
                            item.setForeground(Qt.GlobalColor.yellow)
                        else:
                            item.setForeground(Qt.GlobalColor.white)
                    elif col == 4 and value == "Wartend":  # Status column
                        item.setForeground(Qt.GlobalColor.red)
                    self.consultations_table.setItem(row, col, item)

    def schedule_consultation(self, row):
        """Schedule a specific consultation"""
        patient_name = self.consultations_table.item(row, 0).text()
        tumor_type = self.consultations_table.item(row, 1).text()
        
        msg = QMessageBox(self)
        msg.setWindowTitle("Erstkonsultation aufbieten")
        msg.setText(f"Erstkonsultation für {patient_name} ({tumor_type}) wird aufgeboten.\n\nDiese Funktion wird in einer zukünftigen Version implementiert.")
        msg.setIcon(QMessageBox.Icon.Information)
        msg.exec()

    def go_back(self):
        """Navigate back to the main backoffice page"""
        logging.info("Navigating back to main backoffice page...")
        
        # Check if we came from session navigation
        if not self.main_window.check_tumorboard_session_before_navigation():
            return  # User cancelled navigation
        
        from pages.backoffice_page import BackofficePage
        
        # Find the backoffice page
        backoffice_page = None
        for i in range(self.main_window.stacked_widget.count()):
            widget = self.main_window.stacked_widget.widget(i)
            if isinstance(widget, BackofficePage):
                backoffice_page = widget
                break
        
        if backoffice_page:
            self.main_window.stacked_widget.setCurrentWidget(backoffice_page)
            logging.info("Navigated back to BackofficePage.")
        else:
            logging.warning("BackofficePage not found in stacked widget.") 