from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QScrollArea, QFrame, QMessageBox, QPushButton, QHBoxLayout)
from PyQt6.QtCore import Qt, QTimer
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
        self.refresh_finalization_state()  # Check if tumorboard is finalized
        logging.info(f"ExcelViewerPage UI setup complete for {tumorboard_name} on {date_str}.")

    def setup_ui(self):
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setSpacing(8)  # Reduced from 15 to 8
        main_layout.setContentsMargins(10, 0, 40, 40)
        self.setLayout(main_layout)

        # Top section: Buttons and Title on same height level
        top_section = QWidget()
        top_section.setFixedHeight(50)  # Fixed height to control vertical space
        top_layout = QHBoxLayout(top_section)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(40)
        
        # Left side: Button (fixed width)
        self.start_tumorboard_button = QPushButton("Starte Tumorboard")
        self.start_tumorboard_button.setFont(QFont("Helvetica", 12, QFont.Weight.Bold))
        self.start_tumorboard_button.setFixedHeight(40)
        self.start_tumorboard_button.setFixedWidth(220)
        self.start_tumorboard_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.start_tumorboard_button.setStyleSheet("""
            QPushButton {
                background-color: #2E8B57;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3CB371;
            }
            QPushButton:pressed {
                background-color: #228B22;
            }
        """)
        self.start_tumorboard_button.clicked.connect(self.start_tumorboard_session)
        
        # "Editiere Tumor Board" Button (initially hidden, same position)
        self.edit_tumorboard_button = QPushButton("Editiere Tumorboard")
        self.edit_tumorboard_button.setFont(QFont("Helvetica", 12, QFont.Weight.Bold))
        self.edit_tumorboard_button.setFixedHeight(40)
        self.edit_tumorboard_button.setFixedWidth(220)
        self.edit_tumorboard_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.edit_tumorboard_button.setStyleSheet("""
            QPushButton {
                background-color: #114473;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #FFA500;
            }
            QPushButton:pressed {
                background-color: #FF7F00;
            }
        """)
        self.edit_tumorboard_button.clicked.connect(self.edit_finalized_tumorboard)
        self.edit_tumorboard_button.setVisible(False)
        
        # Add buttons to layout (they will occupy the same space)
        top_layout.addWidget(self.start_tumorboard_button, 0, Qt.AlignmentFlag.AlignVCenter)
        top_layout.addWidget(self.edit_tumorboard_button, 0, Qt.AlignmentFlag.AlignVCenter)
        
        # Right side: Title and Date container (compact)
        title_container = QWidget()
        title_layout = QVBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 300, 0)
        title_layout.setSpacing(4)  # Very tight spacing between title and date
        
        # Page title (smaller font)
        title_label = QLabel(f"Tumorboard: {self.tumorboard_name}")
        title_label.setFont(QFont("Helvetica", 18, QFont.Weight.Bold))  # Reduced from 20 to 18
        title_label.setStyleSheet("color: white;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_layout.addWidget(title_label)

        # Date subtitle (smaller font, tighter)
        date_label = QLabel(f"Datum: {self.date_str}")
        date_label.setFont(QFont("Helvetica", 14))  # Reduced from 16 to 14
        date_label.setStyleSheet("color: #00BFFF;")
        date_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_layout.addWidget(date_label)
        
        # Add title container to layout with stretch to center it
        top_layout.addStretch(1)  # Push title to center
        top_layout.addWidget(title_container, 0, Qt.AlignmentFlag.AlignVCenter)
        top_layout.addStretch(1)  # Balance on right side
        
        main_layout.addWidget(top_section)
        
        # Timestamp section (minimal spacing)
        self.timestamp_label = QLabel("")
        self.timestamp_label.setFont(QFont("Helvetica", 12))
        self.timestamp_label.setStyleSheet("color: #90EE90; margin-top: 5px; margin-bottom: 3px;")
        self.timestamp_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.timestamp_label.setVisible(False)
        main_layout.addWidget(self.timestamp_label)

        # Very small fixed spacer between timestamps and table
        main_layout.addSpacing(5)  # Reduced from 10 to 5

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
            self.table_widget.setColumnWidth(0, 50)  # Row number column
            
            # Apply custom column sizing and hiding (offset by 1 for row number column)
            for col in range(1, self.table_widget.columnCount()):
                column_name = str(df.columns[col - 1])  # Offset by 1 for original column index
                current_width = self.table_widget.columnWidth(col)
                
                # Hide specific columns
                if 'anmeldung' in column_name.lower() and 'nr' in column_name.lower():
                    self.table_widget.setColumnHidden(col, True)
                    continue
                elif 'icd' in column_name.lower() and ('beschreibung' in column_name.lower() or 'description' in column_name.lower()):
                    self.table_widget.setColumnHidden(col, True)
                    continue
                
                # Set minimum width and custom widths for specific columns
                if current_width < 100:
                    self.table_widget.setColumnWidth(col, 100)
                
                # Custom width adjustments
                if 'patientennummer' in column_name.lower():
                    self.table_widget.setColumnWidth(col, 126)  # HIER BREITE DER PATIENTENNUMMER SPALTE ANPASSEN
                
                elif 'name' in column_name.lower() and 'patient' not in column_name.lower():
                    self.table_widget.setColumnWidth(col, 180)  # HIER BREITE DER NAME SPALTE ANPASSEN

                elif 'geschlecht' in column_name.lower():
                    self.table_widget.setColumnWidth(col, 90)  # HIER BREITE DER GESCHLECHT SPALTE ANPASSEN

                elif 'geburt' in column_name.lower() or 'datum' in column_name.lower():
                    self.table_widget.setColumnWidth(col, 120)  # HIER BREITE DER GEBURTSDATUM SPALTE ANPASSEN

                elif 'diagnose' in column_name.lower():
                    self.table_widget.setColumnWidth(col, 400)  # HIER BREITE DER DIAGNOSE SPALTE ANPASSEN

                elif 'icd' in column_name.lower():
                    self.table_widget.setColumnWidth(col, 80)  # HIER BREITE DER DZD/ICD SPALTE ANPASSEN

                elif 'radiotherapie' in column_name.lower() or 'indiziert' in column_name.lower():
                    self.table_widget.setColumnWidth(col, 150)  # HIER BREITE DER RADIOTHERAPIE SPALTE ANPASSEN

                elif 'aufgebot' in column_name.lower():
                    self.table_widget.setColumnWidth(col, 150)  # HIER BREITE DER APPS-AUFGEBOTS SPALTE ANPASSEN

                elif 'bemerkung' in column_name.lower():
                    self.table_widget.setColumnWidth(col, 150)  # HIER BREITE DER BEMERKUNGSPROZEDERE SPALTE ANPASSEN

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

    def start_tumorboard_session(self):
        """Start the tumorboard session page"""
        logging.info(f"Starting tumorboard session for {self.tumorboard_name} on {self.date_str}")
        
        # Import here to avoid circular imports
        from .tumorboard_session_page import TumorboardSessionPage
        
        # Check if page already exists
        existing_page_index = self.main_window.find_page_index(TumorboardSessionPage, entity_name=f"{self.tumorboard_name}_{self.date_str}_session")
        if existing_page_index is not None:
            logging.info("Found existing tumorboard session page, checking for session restoration.")
            existing_session_page = self.main_window.stacked_widget.widget(existing_page_index)
            # Always check for session restoration when returning to existing page
            existing_session_page.check_and_handle_session_restoration()
            self.main_window.stacked_widget.setCurrentIndex(existing_page_index)
        else:
            logging.info("Creating new tumorboard session page.")
            session_page = TumorboardSessionPage(self.main_window, self.tumorboard_name, self.date_str)
            new_index = self.main_window.stacked_widget.addWidget(session_page)
            self.main_window.stacked_widget.setCurrentIndex(new_index) 

    def refresh_finalization_state(self):
        """Check if tumorboard is finalized and update UI accordingly"""
        timestamp_file = Path.home() / "tumorboards" / self.tumorboard_name / self.date_str / "finalized_timestamp.txt"
        
        if timestamp_file.exists():
            try:
                with open(timestamp_file, 'r', encoding='utf-8') as f:
                    timestamp_content = f.read().strip()
                
                # Update timestamp label
                self.timestamp_label.setText(f"{timestamp_content}")
                self.timestamp_label.setVisible(True)
                
                # Hide start button, show edit button
                self.start_tumorboard_button.setVisible(False)
                self.edit_tumorboard_button.setVisible(True)
                
                logging.info(f"Tumorboard marked as finalized: {timestamp_content}")
                
            except Exception as e:
                logging.error(f"Error reading timestamp file: {e}")
                self.timestamp_label.setVisible(False)
                # Show start button, hide edit button
                self.start_tumorboard_button.setVisible(True)
                self.edit_tumorboard_button.setVisible(False)
        else:
            # Not finalized - show start button, hide edit button
            self.timestamp_label.setVisible(False)
            self.start_tumorboard_button.setVisible(True)
            self.edit_tumorboard_button.setVisible(False)

    def edit_finalized_tumorboard(self):
        """Handle editing of a finalized tumorboard with warning dialog"""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Abgeschlossenes Tumorboard bearbeiten")
        msg_box.setText("Möchten Sie das abgeschlossene Tumorboard nachträglich bearbeiten?\n\n"
                        "Bitte beachten Sie: Wenn Sie das bearbeitete Tumorboard speichern "
                        "erfolgt die Dokumentation mittels eines Timestamps und Ihren Benutzerdaten.")
        msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg_box.setDefaultButton(QMessageBox.StandardButton.No)
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: #1a2633;
                color: white;
            }
            QPushButton {
                background-color: #114473;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #1a5a9e;
            }
        """)
        
        result = msg_box.exec()
        
        if result == QMessageBox.StandardButton.Yes:
            # Proceed with editing - use same logic as start_tumorboard_session
            self.start_tumorboard_session()

    def refresh_excel_data(self):
        """Refresh the Excel data by reloading the file"""
        logging.info(f"Refreshing Excel data for {self.tumorboard_name} on {self.date_str}")
        self.load_excel_file()
        self.refresh_finalization_state() 