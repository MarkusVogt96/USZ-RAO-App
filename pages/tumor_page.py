from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QHBoxLayout, QFrame
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QPixmap, QIcon
from .sop_page import SOPPage
from .contouring_page import ContouringPage # <-- Import the new page
import os
import logging # Import logging module

class TumorPage(QWidget):
    def __init__(self, main_window, tumor_type):
        super().__init__()
        logging.info(f"Initializing TumorPage for tumor: {tumor_type}...")
        self.main_window = main_window
        self.tumor_type = tumor_type
        self.setup_ui()
        logging.info(f"TumorPage UI setup complete for {tumor_type}.")

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(10, 0, 40, 40)
        self.setLayout(layout)

        # Add title
        title = QLabel(f"{self.tumor_type}")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont('Arial', 24, QFont.Weight.Bold))
        title.setStyleSheet("color: white; margin-bottom: 20px;")
        layout.addWidget(title)

        # Style the buttons
        button_style = """
            QPushButton {
                background-color: #1c97ff;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 15px;
                font-size: 16px;
                min-width: 300px;
            }
            QPushButton:hover {
                background-color: #3292ea;
            }
            QPushButton:pressed {
                background-color: #1a72ca;
            }
        """

        # For specific tumor types, customize the buttons shown
        if self.tumor_type in ["Anaplastic astrocytoma", "Glioblastoma"]:
            # Only show SOP button for these tumors
            sop_btn = QPushButton("View SOP")
            sop_btn.setStyleSheet(button_style)
            layout.addWidget(sop_btn, alignment=Qt.AlignmentFlag.AlignCenter)
            sop_btn.clicked.connect(self.open_sop_page) # <-- Use method reference
        else:
            # Default buttons for other tumor types
            contouring_btn = QPushButton("Contouring Instructions")
            sop_btn = QPushButton("View SOP")

            contouring_btn.setStyleSheet(button_style)
            sop_btn.setStyleSheet(button_style)

            layout.addWidget(contouring_btn, alignment=Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(sop_btn, alignment=Qt.AlignmentFlag.AlignCenter)

            # Connect buttons
            sop_btn.clicked.connect(self.open_sop_page) # <-- Use method reference
            contouring_btn.clicked.connect(self.open_contouring_page) # <-- Connect contouring button

        # Add stretch to push buttons towards the center/top if layout has few items
        layout.addStretch()

    def open_sop_page(self):
        """Opens the SOP page for the current tumor type."""
        logging.info(f"Opening SOP page for tumor: {self.tumor_type}")
        # Check if page already exists
        existing_sop_page_index = self.main_window.find_page_index(SOPPage, self.tumor_type)
        if existing_sop_page_index is not None:
            logging.info("Found existing SOP page, switching to it.")
            self.main_window.stacked_widget.setCurrentIndex(existing_sop_page_index)
        else:
            logging.info("Creating new SOP page.")
            sop_page = SOPPage(self.main_window, self.tumor_type)
            new_index = self.main_window.stacked_widget.addWidget(sop_page)
            self.main_window.stacked_widget.setCurrentIndex(new_index)

    def open_contouring_page(self):
        """Opens the Contouring Instructions page for the current tumor type."""
        logging.info(f"Opening Contouring Instructions page for tumor: {self.tumor_type}")
        # Check if page already exists
        existing_contouring_page_index = self.main_window.find_page_index(ContouringPage, self.tumor_type)
        if existing_contouring_page_index is not None:
            logging.info("Found existing Contouring page, switching to it.")
            self.main_window.stacked_widget.setCurrentIndex(existing_contouring_page_index)
        else:
            logging.info("Creating new Contouring page.")
            contouring_page = ContouringPage(self.main_window, self.tumor_type)
            new_index = self.main_window.stacked_widget.addWidget(contouring_page)
            self.main_window.stacked_widget.setCurrentIndex(new_index)