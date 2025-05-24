from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QScrollArea, QFrame, QMessageBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
import os
import logging
from pathlib import Path
import pandas as pd

class ExcelViewerPage(QWidget):
    def __init__(self, main_window, tumorboard_name, date_str):
        super().__init__()
        logging.info(f"Initializing ExcelViewerPage for: {tumorboard_name} on {date_str}")
        self.main_window = main_window
        self.tumorboard_name = tumorboard_name
        self.date_str = date_str
        
        # Store combined identifier for find_page_index
        self.entity_name = f"{tumorboard_name}_{date_str}"
        
        self.setup_ui()
        self.load_excel_file()
        logging.info(f"ExcelViewerPage UI setup complete for {tumorboard_name} on {date_str}.")

    def setup_ui(self):
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(10, 0, 40, 40)
        self.setLayout(main_layout)

        # Page title
        title_label = QLabel(f"Tumorboard: {self.tumorboard_name}")
        title_label.setFont(QFont("Helvetica", 20, QFont.Weight.Bold))
        title_label.setStyleSheet("color: white;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)

        # Date subtitle
        date_label = QLabel(f"Datum: {self.date_str}")
        date_label.setFont(QFont("Helvetica", 16))
        date_label.setStyleSheet("color: #00BFFF; margin-bottom: 20px;")
        date_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(date_label)

        # Create table widget for Excel display
        self.table_widget = QTableWidget()
        self.table_widget.setStyleSheet("""
            QTableWidget {
                background-color: #232F3B;
                alternate-background-color: #2A3642;
                selection-background-color: #3292ea;
                gridline-color: #425061;
                color: white;
                border: 1px solid #425061;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #425061;
            }
            QTableWidget::item:selected {
                background-color: #3292ea;
            }
            QHeaderView::section {
                background-color: #1a2633;
                color: white;
                padding: 10px;
                border: 1px solid #425061;
                font-weight: bold;
            }
        """)

        # Set table properties
        self.table_widget.setAlternatingRowColors(True)
        self.table_widget.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table_widget.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)  # Read-only
        
        # Enable sorting
        self.table_widget.setSortingEnabled(True)

        # Configure headers to resize properly
        horizontal_header = self.table_widget.horizontalHeader()
        horizontal_header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        horizontal_header.setStretchLastSection(True)

        vertical_header = self.table_widget.verticalHeader()
        vertical_header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)

        main_layout.addWidget(self.table_widget)

    def load_excel_file(self):
        """Load and display the Excel file for the specific tumorboard and date"""
        excel_path = Path.home() / "tumorboards" / self.tumorboard_name / self.date_str / f"{self.date_str}.xlsx"
        
        logging.info(f"Attempting to load Excel file: {excel_path}")

        if not excel_path.exists():
            self._show_file_not_found_message()
            return

        try:
            # Try to read the Excel file with pandas
            df = pd.read_excel(excel_path, engine='openpyxl')
            
            # Handle empty dataframe
            if df.empty:
                self._show_empty_file_message()
                return

            # Set up the table
            self.table_widget.setRowCount(len(df))
            self.table_widget.setColumnCount(len(df.columns))
            
            # Set column headers
            self.table_widget.setHorizontalHeaderLabels([str(col) for col in df.columns])

            # Fill the table with data
            for row_idx, row in df.iterrows():
                for col_idx, value in enumerate(row):
                    # Convert value to string, handle NaN values
                    if pd.isna(value):
                        display_value = ""
                    else:
                        display_value = str(value)
                    
                    item = QTableWidgetItem(display_value)
                    self.table_widget.setItem(row_idx, col_idx, item)

            # Resize columns to content
            self.table_widget.resizeColumnsToContents()
            
            # Set minimum column width
            for col in range(self.table_widget.columnCount()):
                current_width = self.table_widget.columnWidth(col)
                if current_width < 100:
                    self.table_widget.setColumnWidth(col, 100)

            logging.info(f"Successfully loaded Excel file with {len(df)} rows and {len(df.columns)} columns")

        except Exception as e:
            logging.error(f"Error loading Excel file: {e}")
            self._show_error_message(str(e))

    def _show_file_not_found_message(self):
        """Show message when Excel file is not found"""
        self.table_widget.setRowCount(1)
        self.table_widget.setColumnCount(1)
        self.table_widget.setHorizontalHeaderLabels(["Status"])
        
        item = QTableWidgetItem("Excel-Datei nicht gefunden")
        item.setFont(QFont("Helvetica", 12, QFont.Weight.Bold))
        item.setForeground(Qt.GlobalColor.yellow)
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.table_widget.setItem(0, 0, item)
        
        self.table_widget.resizeColumnsToContents()
        
        logging.warning(f"Excel file not found for {self.tumorboard_name} on {self.date_str}")

    def _show_empty_file_message(self):
        """Show message when Excel file is empty"""
        self.table_widget.setRowCount(1)
        self.table_widget.setColumnCount(1)
        self.table_widget.setHorizontalHeaderLabels(["Status"])
        
        item = QTableWidgetItem("Excel-Datei ist leer")
        item.setFont(QFont("Helvetica", 12, QFont.Weight.Bold))
        item.setForeground(Qt.GlobalColor.yellow)
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.table_widget.setItem(0, 0, item)
        
        self.table_widget.resizeColumnsToContents()
        
        logging.warning(f"Excel file is empty for {self.tumorboard_name} on {self.date_str}")

    def _show_error_message(self, error_msg):
        """Show error message when Excel file cannot be loaded"""
        self.table_widget.setRowCount(2)
        self.table_widget.setColumnCount(1)
        self.table_widget.setHorizontalHeaderLabels(["Fehler"])
        
        # Error title
        title_item = QTableWidgetItem("Fehler beim Laden der Excel-Datei")
        title_item.setFont(QFont("Helvetica", 12, QFont.Weight.Bold))
        title_item.setForeground(Qt.GlobalColor.red)
        title_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.table_widget.setItem(0, 0, title_item)
        
        # Error details
        error_item = QTableWidgetItem(f"Details: {error_msg}")
        error_item.setFont(QFont("Helvetica", 10))
        error_item.setForeground(Qt.GlobalColor.yellow)
        error_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.table_widget.setItem(1, 0, error_item)
        
        self.table_widget.resizeColumnsToContents()
        
        logging.error(f"Error loading Excel file for {self.tumorboard_name} on {self.date_str}: {error_msg}") 