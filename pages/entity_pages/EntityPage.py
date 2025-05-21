from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QHBoxLayout, QFrame, QMessageBox
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QPixmap, QIcon
from pages.pdf_reader import PdfReaderPage
import os
import logging

class EntityPage(QWidget):
    def __init__(self, main_window, entity_name, group_name):
        super().__init__()
        logging.info(f"Initializing EntityPage for entity: {entity_name} (Group: {group_name})...")
        self.main_window = main_window
        self.entity_name = entity_name
        self.group_name = group_name
        self.sop_pdf_files = [] # Initialize list to store found PDF paths
        self.find_sop_pdfs() # Call the new method to find PDFs
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

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(10, 0, 40, 40)
        self.setLayout(layout)

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
                        background-color: #4a4a4a; /* Dark grey background */
                        color: white;
                        border: 1px solid #5a5a5a;
                        padding: 8px 12px;
                        text-align: left; /* Align text to the left */
                        border-radius: 4px;
                        font-size: 14px;
                    }
                    QPushButton:hover {
                        background-color: #5a5a5a;
                    }
                    QPushButton:pressed {
                        background-color: #6a6a6a;
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

        # --- Contouring Instructions Section ---
        contouring_header = QLabel("Contouring Instructions")
        contouring_header.setFont(QFont('Arial', 16, QFont.Weight.Bold))
        contouring_header.setStyleSheet("color: white; margin-top: 20px; margin-bottom: 5px;")
        layout.addWidget(contouring_header)

        contouring_placeholder = QLabel("Aktuell Work in Progress")
        contouring_placeholder.setStyleSheet("color: grey; font-style: italic; margin-left: 20px;")
        layout.addWidget(contouring_placeholder)

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