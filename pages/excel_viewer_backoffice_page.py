from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QScrollArea, QFrame, QMessageBox, QPushButton, QHBoxLayout,
                             QDialog, QDialogButtonBox)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
import os
import logging
from pathlib import Path
import pandas as pd


class ExcelViewerBackofficePage(QWidget):
    def __init__(self, main_window, tumorboard_name, date_str, source_page=None):
        super().__init__()
        logging.info(f"Initializing ExcelViewerBackofficePage for: {tumorboard_name} on {date_str}")
        self.main_window = main_window
        self.tumorboard_name = tumorboard_name
        self.date_str = date_str
        self.source_page = source_page  # Track which page this was opened from
        
        # Store the tumorboard base path (K: drive for backoffice)
        #self.tumorboard_base_path = Path("K:/RAO_Projekte/App/tumorboards")
        self.tumorboard_base_path = Path("C:/Users/marku/tumorboards")
        
        # Store combined identifier for find_page_index
        self.entity_name = f"{tumorboard_name}_{date_str}"
        
        self.setup_ui()
        self.load_excel_file()
        logging.info(f"ExcelViewerBackofficePage UI setup complete for {tumorboard_name} on {date_str}.")

    def setup_ui(self):
        """Setup the user interface"""
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(10)
        self.setLayout(main_layout)

        # Top section with title
        top_section = QFrame()
        top_section.setFixedHeight(80)
        top_section.setStyleSheet("background: transparent;")
        top_layout = QHBoxLayout(top_section)
        top_layout.setContentsMargins(0, 10, 0, 10)
        top_layout.setSpacing(20)
        
        # Title and Date container (centered)
        title_container = QWidget()
        title_layout = QVBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(4)  # Very tight spacing between title and date
        
        # Page title
        title_label = QLabel(f"Tumorboard: {self.tumorboard_name}")
        title_label.setFont(QFont("Helvetica", 20, QFont.Weight.Bold))
        title_label.setStyleSheet("color: white;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_layout.addWidget(title_label)

        # Date subtitle
        date_label = QLabel(f"Datum: {self.date_str}")
        date_label.setFont(QFont("Helvetica", 16))
        date_label.setStyleSheet("color: #00BFFF;")
        date_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_layout.addWidget(date_label)
        
        # Center the title container
        top_layout.addStretch(1)
        top_layout.addWidget(title_container, 0, Qt.AlignmentFlag.AlignCenter)
        top_layout.addStretch(1)
        
        main_layout.addWidget(top_section)
        
        # Very small fixed spacer between header and table
        main_layout.addSpacing(5)

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
            QTableWidget QTableCornerButton::section {
                background-color: #1a2633;
                border: 1px solid #425061;
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
        
        # Hide the vertical header (row numbers) to avoid offset issues
        vertical_header.setVisible(False)
        
        # Try to fix the corner button styling after widget is created
        QTimer.singleShot(100, self._fix_corner_button_styling)

        main_layout.addWidget(self.table_widget)

    def _fix_corner_button_styling(self):
        """Fix the corner button styling after the widget is fully initialized"""
        try:
            # Find the corner button and apply styling
            corner_button = self.table_widget.findChild(QPushButton)
            if corner_button:
                corner_button.setStyleSheet("""
                    QPushButton {
                        background-color: #1a2633;
                        border: 1px solid #425061;
                    }
                """)
                # Disable the corner button to prevent select all functionality
                corner_button.setEnabled(False)
                logging.info("Corner button styling applied successfully")
        except Exception as e:
            logging.warning(f"Could not apply corner button styling: {e}")

    def load_excel_file(self):
        """Load and display the Excel file for the specific tumorboard and date"""
        excel_path = self.tumorboard_base_path / self.tumorboard_name / self.date_str / f"{self.date_str}.xlsx"
        
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

            # Set up the table with an additional column for row numbers
            self.table_widget.setRowCount(len(df))
            self.table_widget.setColumnCount(len(df.columns) + 1)
            
            # Set column headers with row number column first
            headers = ["#"] + [str(col) for col in df.columns]
            self.table_widget.setHorizontalHeaderLabels(headers)

            # Fill the table with data
            for row_idx, row in df.iterrows():
                # Add row number in first column with proper numeric sorting
                row_number_item = QTableWidgetItem()
                row_number_item.setData(Qt.ItemDataRole.DisplayRole, row_idx + 1)  # Store as integer for proper sorting
                row_number_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table_widget.setItem(row_idx, 0, row_number_item)
                
                # Add data in subsequent columns (offset by 1)
                for col_idx, value in enumerate(row):
                    # Convert value to string, handle NaN values
                    if pd.isna(value):
                        display_value = ""
                    else:
                        display_value = str(value)
                        # Clean patient numbers - remove .0 if present
                        if col_idx < len(df.columns) and str(df.columns[col_idx]).lower() == 'patientennummer':
                            if display_value.endswith('.0'):
                                display_value = display_value[:-2]
                    
                    item = QTableWidgetItem(display_value)
                    self.table_widget.setItem(row_idx, col_idx + 1, item)  # Offset by 1 for row number column

            # Resize columns to content
            self.table_widget.resizeColumnsToContents()
            
            # Set width for row number column
            self.table_widget.setColumnWidth(0, 50)
            
            # Apply custom column sizing and hiding (offset by 1 for row number column)
            for col in range(1, self.table_widget.columnCount()):
                column_name = str(df.columns[col - 1])  # Offset by 1 for original column index
                current_width = self.table_widget.columnWidth(col)
                
                if 'beschreibung' in column_name.lower():
                    self.table_widget.setColumnHidden(col, True)
                    continue
                
                # Set minimum width and custom widths for specific columns
                if current_width < 100:
                    self.table_widget.setColumnWidth(col, 100)
                
                # Custom width adjustments
                if 'patientennummer' in column_name.lower():
                    self.table_widget.setColumnWidth(col, 126)
                elif 'name' in column_name.lower() and 'patient' not in column_name.lower():
                    self.table_widget.setColumnWidth(col, 150)
                elif 'geschlecht' in column_name.lower():
                    self.table_widget.setColumnWidth(col, 90)
                elif 'geburt' in column_name.lower() or 'datum' in column_name.lower():
                    self.table_widget.setColumnWidth(col, 110)
                elif 'diagnose' in column_name.lower():
                    self.table_widget.setColumnWidth(col, 300)
                elif 'icd' in column_name.lower():
                    self.table_widget.setColumnWidth(col, 60)
                elif 'radiotherapie' in column_name.lower() or 'indiziert' in column_name.lower():
                    self.table_widget.setColumnWidth(col, 60)
                elif 'aufgebot' in column_name.lower():
                    self.table_widget.setColumnWidth(col, 120)
                elif 'teams' in column_name.lower():
                    self.table_widget.setColumnWidth(col, 140)
                elif 'studie' in column_name.lower():
                    self.table_widget.setColumnWidth(col, 100)
                elif 'bemerkung' in column_name.lower():
                    self.table_widget.setColumnWidth(col, 120)

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



    def refresh_excel_data(self):
        """Refresh the Excel data by reloading the file"""
        logging.info(f"Refreshing Excel data for {self.tumorboard_name} on {self.date_str}")
        self.load_excel_file() 