from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QHBoxLayout, QFrame, QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView, QApplication, QScrollArea
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QPixmap, QIcon
from pages.pdf_reader import PdfReaderPage
import os
import logging
import json

class PatientNumberWidget(QWidget):
    def __init__(self, patientennummer, copy_callback):
        super().__init__()
        self.patientennummer = patientennummer
        self.copy_callback = copy_callback
        self.setup_ui()
    
    def setup_ui(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(5, 0, 5, 0)
        layout.setSpacing(5)
        
        # Patient number label
        self.number_label = QLabel(str(self.patientennummer))
        self.number_label.setStyleSheet("color: white; font-family: Arial; font-size: 14px;")
        layout.addWidget(self.number_label)
        
        # Copy button with standard copy icon
        self.copy_button = QPushButton()
        self.copy_button.setIcon(self.style().standardIcon(self.style().StandardPixmap.SP_DialogSaveButton))
        self.copy_button.setToolTip("Patientennummer kopieren")
        self.copy_button.setFixedSize(20, 20)
        self.copy_button.setStyleSheet("""
            QPushButton {
                border: none;
                background: transparent;
                padding: 2px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
                border-radius: 3px;
            }
            QPushButton:pressed {
                background-color: rgba(255, 255, 255, 0.2);
            }
        """)
        self.copy_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.copy_button.clicked.connect(self.on_copy_clicked)
        layout.addWidget(self.copy_button)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def on_copy_clicked(self):
        self.copy_callback(self.patientennummer)

class EntityPage(QWidget):
    def __init__(self, main_window, entity_name, group_name):
        super().__init__()
        logging.info(f"Initializing EntityPage for entity: {entity_name} (Group: {group_name})...")
        self.main_window = main_window
        self.entity_name = entity_name
        self.group_name = group_name
        self.sop_pdf_files = [] # Initialize list to store found PDF paths
        self.guideline_pdf_files = [] # Initialize list to store guideline PDF paths
        self.fallbeispiele = [] # Initialize list to store case examples
        self.find_sop_pdfs() # Call the new method to find PDFs
        self.load_guideline_mapping() # Load JSON mapping for guidelines
        self.find_contouring_guidelines() # Find available guideline PDFs
        self.load_fallbeispiele_mapping() # Load JSON mapping for case examples
        self.find_fallbeispiele() # Find available case examples
        self.setup_ui()
        logging.info(f"EntityPage UI setup complete for {entity_name}.")

    def find_sop_pdfs(self):
        """Finds PDF files in the specific SOP directory for this entity."""
        try:
            # Construct the expected path to the SOP directory
            # Assumes the script runs from the root directory or has access to assets
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__))) # Go up two levels from pages/entity_pages
            sop_dir_path = os.path.join(base_dir, 'assets', 'sop', self.group_name, self.entity_name)
            logging.info(f"Searching for SOP PDFs in: {sop_dir_path}")

            if not os.path.isdir(sop_dir_path):
                logging.warning(f"SOP directory not found: {sop_dir_path}")
                self.sop_pdf_files = [] # Ensure list is empty if dir doesn't exist
                return

            # List files and filter for PDFs
            for filename in os.listdir(sop_dir_path):
                if filename.lower().endswith('.pdf'):
                    full_path = os.path.join(sop_dir_path, filename)
                    self.sop_pdf_files.append(full_path)
                    logging.info(f"Found SOP PDF: {full_path}")
            
            if not self.sop_pdf_files:
                logging.info(f"No SOP PDFs found in {sop_dir_path}.")

        except Exception as e:
            logging.error(f"Error finding SOP PDFs for {self.entity_name} in {self.group_name}: {e}", exc_info=True)
            self.sop_pdf_files = [] # Ensure list is empty on error

    def load_guideline_mapping(self):
        """Loads the JSON mapping file for guideline PDFs."""
        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            mapping_file_path = os.path.join(base_dir, 'assets', 'json', 'mapping_guidelines.json')
            logging.info(f"Loading guideline mapping from: {mapping_file_path}")
            
            if not os.path.exists(mapping_file_path):
                logging.warning(f"Guideline mapping file not found: {mapping_file_path}")
                self.guideline_mapping = {}
                return
            
            with open(mapping_file_path, 'r', encoding='utf-8') as f:
                self.guideline_mapping = json.load(f)
                logging.info(f"Successfully loaded guideline mapping with {len(self.guideline_mapping)} groups.")
                
        except Exception as e:
            logging.error(f"Error loading guideline mapping: {e}", exc_info=True)
            self.guideline_mapping = {}

    def find_contouring_guidelines(self):
        """Finds available guideline PDF files for this entity based on the JSON mapping."""
        try:
            # Get the list of PDF filenames for this entity from the mapping
            mapped_pdfs = []
            if hasattr(self, 'guideline_mapping') and self.group_name in self.guideline_mapping:
                if self.entity_name in self.guideline_mapping[self.group_name]:
                    mapped_pdfs = self.guideline_mapping[self.group_name][self.entity_name]
                    logging.info(f"Found {len(mapped_pdfs)} mapped PDFs for {self.entity_name}: {mapped_pdfs}")
            
            # Check which of the mapped PDFs actually exist in the guidelines directory
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            guidelines_dir_path = os.path.join(base_dir, 'assets', 'guidelines')
            
            self.guideline_pdf_files = []
            for pdf_filename in mapped_pdfs:
                if pdf_filename:  # Skip empty strings
                    full_path = os.path.join(guidelines_dir_path, pdf_filename)
                    if os.path.exists(full_path):
                        self.guideline_pdf_files.append(full_path)
                        logging.info(f"Found guideline PDF: {full_path}")
                    else:
                        logging.warning(f"Mapped guideline PDF not found: {full_path}")
            
            if not self.guideline_pdf_files:
                logging.info(f"No guideline PDFs found for {self.entity_name} in {self.group_name}.")
                
        except Exception as e:
            logging.error(f"Error finding guideline PDFs for {self.entity_name} in {self.group_name}: {e}", exc_info=True)
            self.guideline_pdf_files = []

    def load_fallbeispiele_mapping(self):
        """Loads the JSON mapping file for case examples."""
        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            mapping_file_path = os.path.join(base_dir, 'assets', 'json', 'mapping_fallbeispiele.json')
            logging.info(f"Loading fallbeispiele mapping from: {mapping_file_path}")
            
            if not os.path.exists(mapping_file_path):
                logging.warning(f"Fallbeispiele mapping file not found: {mapping_file_path}")
                self.fallbeispiele_mapping = {}
                return
            
            with open(mapping_file_path, 'r', encoding='utf-8') as f:
                self.fallbeispiele_mapping = json.load(f)
                logging.info(f"Successfully loaded fallbeispiele mapping with {len(self.fallbeispiele_mapping)} groups.")
                
        except Exception as e:
            logging.error(f"Error loading fallbeispiele mapping: {e}", exc_info=True)
            self.fallbeispiele_mapping = {}

    def find_fallbeispiele(self):
        """Finds available case examples for this entity based on the JSON mapping."""
        try:
            # Get the list of case examples for this entity from the mapping
            self.fallbeispiele = []
            if hasattr(self, 'fallbeispiele_mapping') and self.group_name in self.fallbeispiele_mapping:
                if self.entity_name in self.fallbeispiele_mapping[self.group_name]:
                    self.fallbeispiele = self.fallbeispiele_mapping[self.group_name][self.entity_name]
                    logging.info(f"Found {len(self.fallbeispiele)} case examples for {self.entity_name}: {self.fallbeispiele}")
            
            if not self.fallbeispiele:
                logging.info(f"No case examples found for {self.entity_name} in {self.group_name}.")
                
        except Exception as e:
            logging.error(f"Error finding case examples for {self.entity_name} in {self.group_name}: {e}", exc_info=True)
            self.fallbeispiele = []

    def copy_to_clipboard(self, patientennummer):
        """Copies the patient number to clipboard."""
        try:
            clipboard = QApplication.clipboard()
            clipboard.setText(str(patientennummer))
            logging.info(f"Copied patient number to clipboard: {patientennummer}")
            # TODO: Add visual feedback (toast notification or status message)
        except Exception as e:
            logging.error(f"Error copying to clipboard: {e}", exc_info=True)

    def setup_ui(self):
        # Create scroll area for the entire page
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("QScrollArea { border: none; }")

        # Create container widget for scroll area content
        scroll_content_widget = QWidget()
        layout = QVBoxLayout(scroll_content_widget)
        layout.setSpacing(15)
        layout.setContentsMargins(10, 0, 40, 40)
        
        # Set scroll content widget
        scroll_area.setWidget(scroll_content_widget)
        
        # Main page layout containing the scroll area
        page_layout = QVBoxLayout(self)
        page_layout.setContentsMargins(0, 0, 0, 0)
        page_layout.addWidget(scroll_area)

        # Add title
        title = QLabel(f"{self.entity_name}")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont('Arial', 24, QFont.Weight.Bold))
        title.setStyleSheet("color: white; margin-bottom: 20px;")
        layout.addWidget(title)

        # --- SOP Files Section ---
        sop_header = QLabel("SOP Files")
        sop_header.setFont(QFont('Arial', 16, QFont.Weight.Bold))
        sop_header.setStyleSheet("color: white; margin-top: 10px; margin-bottom: 5px;")
        layout.addWidget(sop_header)

        # Layout for SOP file buttons (indented)
        self.sop_files_layout = QVBoxLayout()
        self.sop_files_layout.setContentsMargins(20, 0, 0, 0) # Indentation via left margin
        self.sop_files_layout.setSpacing(8) # Slightly increased spacing for buttons
        layout.addLayout(self.sop_files_layout)

        # Dynamically add buttons for found SOP PDFs
        if self.sop_pdf_files:
            # Sort files alphabetically for consistent order
            self.sop_pdf_files.sort()
            for pdf_path in self.sop_pdf_files:
                # Extract filename for button text
                pdf_filename = os.path.basename(pdf_path)
                button = QPushButton(pdf_filename)
                button.setStyleSheet("""
                    QPushButton {
                        background-color: #114473;
                        color: white;
                        border: none;
                        padding: 8px 12px;
                        text-align: left;
                        border-radius: 10px;
                        font-size: 14px;
                    }
                    QPushButton:hover {
                        background-color: #1a5a9e;
                    }
                    QPushButton:pressed {
                        background-color: #0d2e4d;
                    }
                """)
                # Set cursor to pointing hand on hover
                button.setCursor(Qt.CursorShape.PointingHandCursor)
                
                # Connect button click to open_pdf_viewer, passing the specific path
                button.clicked.connect(lambda checked, path=pdf_path: self.open_pdf_viewer(path))
                
                self.sop_files_layout.addWidget(button)
        else:
            # Display a message if no PDFs were found
            no_sop_label = QLabel("Keine SOP-Dateien gefunden.")
            no_sop_label.setStyleSheet("color: grey; font-style: italic; margin-left: 20px;") # Matches indentation
            layout.insertWidget(layout.indexOf(self.sop_files_layout) + 1, no_sop_label) # Insert label after the layout
            # Optional: Hide the empty layout itself? Or just leave it.
            # self.sop_files_layout.hide() # Might cause issues if header is there

        # --- Contouring Guidelines Section ---
        contouring_header = QLabel("Contouring Guidelines")
        contouring_header.setFont(QFont('Arial', 16, QFont.Weight.Bold))
        contouring_header.setStyleSheet("color: white; margin-top: 20px; margin-bottom: 5px;")
        layout.addWidget(contouring_header)

        # Layout for guideline file buttons (indented)
        self.guidelines_layout = QVBoxLayout()
        self.guidelines_layout.setContentsMargins(20, 0, 0, 0) # Indentation via left margin
        self.guidelines_layout.setSpacing(8) # Slightly increased spacing for buttons
        layout.addLayout(self.guidelines_layout)

        # Dynamically add buttons for found guideline PDFs
        if self.guideline_pdf_files:
            # Sort files alphabetically for consistent order
            self.guideline_pdf_files.sort()
            for pdf_path in self.guideline_pdf_files:
                # Extract filename for button text
                pdf_filename = os.path.basename(pdf_path)
                button = QPushButton(pdf_filename)
                button.setStyleSheet("""
                    QPushButton {
                        background-color: #114473;
                        color: white;
                        border: none;
                        padding: 8px 12px;
                        text-align: left;
                        border-radius: 10px;
                        font-size: 14px;
                    }
                    QPushButton:hover {
                        background-color: #1a5a9e;
                    }
                    QPushButton:pressed {
                        background-color: #0d2e4d;
                    }
                """)
                # Set cursor to pointing hand on hover
                button.setCursor(Qt.CursorShape.PointingHandCursor)
                
                # Connect button click to open_guideline_pdf, passing the specific path
                button.clicked.connect(lambda checked, path=pdf_path: self.open_guideline_pdf(path))
                
                self.guidelines_layout.addWidget(button)
        else:
            # Display a message if no guideline PDFs were found
            no_guidelines_label = QLabel("Keine Contouring Guidelines gefunden.")
            no_guidelines_label.setStyleSheet("color: grey; font-style: italic; margin-left: 20px;") # Matches indentation
            layout.insertWidget(layout.indexOf(self.guidelines_layout) + 1, no_guidelines_label) # Insert label after the layout

        # --- Fallbeispiele Section ---
        fallbeispiele_header = QLabel("Fallbeispiele")
        fallbeispiele_header.setFont(QFont('Arial', 16, QFont.Weight.Bold))
        fallbeispiele_header.setStyleSheet("color: white; margin-top: 20px; margin-bottom: 5px;")
        layout.addWidget(fallbeispiele_header)

        # Create table for case examples
        if self.fallbeispiele:
            self.fallbeispiele_table = QTableWidget()
            self.fallbeispiele_table.setRowCount(len(self.fallbeispiele))
            self.fallbeispiele_table.setColumnCount(4)
            self.fallbeispiele_table.setHorizontalHeaderLabels(["Patientennummer", "RT-Konzept", "Workflow", "Konturbildgebung"])
            
            # Hide row numbers (vertical header)
            self.fallbeispiele_table.verticalHeader().setVisible(False)
            
            # Configure table appearance
            self.fallbeispiele_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
            self.fallbeispiele_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
            self.fallbeispiele_table.setAlternatingRowColors(True)
            self.fallbeispiele_table.setStyleSheet("""
                QTableWidget {
                    background-color: #2a2a2a;
                    color: white;
                    border: none;
                    border-radius: 10px;
                    gridline-color: #5a5a5a;
                    margin-left: 20px;
                    margin-right: 20px;
                }
                QTableWidget::item {
                    padding: 8px;
                    border-bottom: 1px solid #5a5a5a;
                    border-right: 1px solid #5a5a5a;
                }
                QTableWidget::item:alternate {
                    background-color: #3a3a3a;
                }
                QTableWidget::item:selected {
                    background-color: #1a5a9e;
                }
                QHeaderView::section {
                    background-color: #114473;
                    color: white;
                    padding: 8px;
                    border: 1px solid #1a5a9e;
                    font-weight: bold;
                }
                QHeaderView::section:first {
                    border-top-left-radius: 10px;
                    border-left: none;
                }
                QHeaderView::section:last {
                    border-top-right-radius: 10px;
                    border-right: none;
                }
                QHeaderView {
                    border: none;
                }
            """)
            
            # Fill table with data
            for row, fallbeispiel in enumerate(self.fallbeispiele):
                # Patient number column with custom widget
                patient_widget = PatientNumberWidget(
                    fallbeispiel.get('patientennummer', ''),
                    self.copy_to_clipboard
                )
                self.fallbeispiele_table.setCellWidget(row, 0, patient_widget)
                
                # RT-Konzept column
                rt_konzept_item = QTableWidgetItem(fallbeispiel.get('rt_konzept', ''))
                self.fallbeispiele_table.setItem(row, 1, rt_konzept_item)
                
                # Workflow column
                workflow_item = QTableWidgetItem(fallbeispiel.get('workflow', ''))
                self.fallbeispiele_table.setItem(row, 2, workflow_item)
                
                # Konturbildgebung column
                kontur_item = QTableWidgetItem(fallbeispiel.get('konturbildgebung', ''))
                self.fallbeispiele_table.setItem(row, 3, kontur_item)
            
            # Configure column widths
            header = self.fallbeispiele_table.horizontalHeader()
            header.setStretchLastSection(True)
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
            header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
            
            # Configure table height - ensure all rows are visible
            # Get header height
            header_height = self.fallbeispiele_table.horizontalHeader().sizeHint().height()
            
            # Set uniform row height to match header
            for row in range(len(self.fallbeispiele)):
                self.fallbeispiele_table.setRowHeight(row, header_height)
            
            # Calculate total table height (header + all rows + margins)
            total_height = header_height + (header_height * len(self.fallbeispiele)) + 10  # +10 for margins
            self.fallbeispiele_table.setMinimumHeight(total_height)
            self.fallbeispiele_table.setMaximumHeight(total_height)  # Fixed height to prevent stretching
            
            layout.addWidget(self.fallbeispiele_table)
        else:
            # Display a message if no case examples were found
            no_fallbeispiele_label = QLabel("Keine Fallbeispiele verfügbar.")
            no_fallbeispiele_label.setStyleSheet("color: grey; font-style: italic; margin-left: 20px;")
            layout.addWidget(no_fallbeispiele_label)

        # Add stretch to push content upwards
        layout.addStretch()

    def open_pdf_viewer(self, pdf_path):
        logging.info(f"Opening PDF viewer for: {pdf_path}")
        
        # Extract filename for potential use in breadcrumbs or title
        pdf_filename = os.path.basename(pdf_path)
        
        # --- Check if a page for this EXACT PDF path already exists ---
        # Note: find_page_index might need adjustment if it doesn't handle pdf_path
        # For now, assume we create a new page each time, 
        # or rely on manual back navigation. 
        # A more robust solution might involve passing pdf_path to find_page_index 
        # and storing PdfReaderPage instances with their paths.
        
        # Let's try a simple approach first: create new page instance
        try:
            # Pass group_name and entity_name to PdfReaderPage constructor
            pdf_viewer_page = PdfReaderPage(self.main_window, pdf_path, 
                                            self.group_name, self.entity_name)
            
            # Add the new page to the stacked widget
            new_index = self.main_window.stacked_widget.addWidget(pdf_viewer_page)
            
            # Navigate to the new page
            self.main_window.stacked_widget.setCurrentIndex(new_index)
            logging.info(f"Created and navigated to PdfReaderPage for {pdf_filename}.")
            
            # --- Update breadcrumbs ---
            # This depends heavily on how main_window.update_breadcrumb is implemented
            # We likely need to pass more info or call a specific breadcrumb update method
            # Example assuming update_breadcrumb can handle the new page index:
            # self.main_window.update_breadcrumb(new_index) 
            # Or if it needs explicit path components:
            # self.main_window.update_breadcrumb_for_pdf(self.group_name, self.entity_name, pdf_filename, new_index)
            # For now, we'll call the existing update_breadcrumb and see how it behaves
            # It might need adjustment in main.py later.
            self.main_window.update_breadcrumb(new_index)
            logging.info("Called main_window.update_breadcrumb")

        except Exception as e:
            logging.error(f"Failed to create or open PdfReaderPage for {pdf_path}: {e}", exc_info=True)
            # Optionally show an error message to the user (e.g., using QMessageBox)
            QMessageBox.critical(self, "Error", f"Could not open PDF viewer: {e}")

    def open_guideline_pdf(self, pdf_path):
        """Opens a guideline PDF in the PDF viewer."""
        logging.info(f"Opening guideline PDF viewer for: {pdf_path}")
        
        # Extract filename for potential use in breadcrumbs or title
        pdf_filename = os.path.basename(pdf_path)
        
        try:
            # Pass group_name and entity_name to PdfReaderPage constructor
            # Use same approach as SOP PDFs
            pdf_viewer_page = PdfReaderPage(self.main_window, pdf_path, 
                                            self.group_name, self.entity_name)
            
            # Add the new page to the stacked widget
            new_index = self.main_window.stacked_widget.addWidget(pdf_viewer_page)
            
            # Navigate to the new page
            self.main_window.stacked_widget.setCurrentIndex(new_index)
            logging.info(f"Created and navigated to PdfReaderPage for guideline {pdf_filename}.")
            
            # Update breadcrumbs
            self.main_window.update_breadcrumb(new_index)
            logging.info("Called main_window.update_breadcrumb for guideline PDF")

        except Exception as e:
            logging.error(f"Failed to create or open PdfReaderPage for guideline {pdf_path}: {e}", exc_info=True)
            # Show an error message to the user
            QMessageBox.critical(self, "Error", f"Could not open guideline PDF viewer: {e}")