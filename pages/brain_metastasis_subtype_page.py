from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QSizePolicy, QToolButton, QFrame
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtCore import Qt, QSize
import os # Added import os
import logging # Import logging module

# Assuming sop_page exists and can handle these subtypes, or will be updated
from .tumor_page import TumorPage # Import TumorPage
# from .sop_page import SOPPage 

class BrainMetastasisSubtypePage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        logging.info("Initializing BrainMetastasisSubtypePage...")
        self.main_window = main_window
        self.setup_ui()
        logging.info("BrainMetastasisSubtypePage UI setup complete.")

    def setup_ui(self):
        # Main layout without margins to allow title bar to extend fully
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        self.setStyleSheet("background-color: #19232D;") # Updated to match the main theme color

        # --- Title Frame ---
        title_frame = QFrame()
        title_frame.setStyleSheet("background-color: #19232D; padding: 15px 0;") # Updated to match the main theme color
        title_frame.setMinimumHeight(70) # Set minimum height
        title_frame.setFrameShape(QFrame.Shape.NoFrame)
        
        # Title frame layout
        title_layout = QVBoxLayout(title_frame)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Title label
        title_label = QLabel("Choose subtype of Radiotherapy")
        title_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: white;")
        title_layout.addWidget(title_label)
        
        # Add title frame to main layout
        main_layout.addWidget(title_frame)

        # --- Content Area ---
        content_frame = QFrame()
        content_frame.setStyleSheet("background-color: #19232D;") # Updated to match the main theme color
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(40, 30, 40, 40)
        content_layout.setSpacing(30)
        
        # --- Tiles Layout ---
        tiles_layout = QHBoxLayout()
        tiles_layout.setSpacing(40) 
        tiles_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # --- Primary Radiotherapy Tile (Now First) ---
        primary_icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "bm_primary_radiotherapy.png")
        primary_button = self._create_tile_button("Primary Radiotherapy", icon_path=primary_icon_path)
        primary_button.clicked.connect(lambda: self.go_to_sop_page("Brain Metastasis - Primary RT"))
        tiles_layout.addWidget(primary_button)
        
        # --- Postoperative Radiotherapy Tile (Now Second) ---
        postop_icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "bm_postoperative_radiotherapy.png")
        postop_button = self._create_tile_button("Postoperative Radiotherapy", icon_path=postop_icon_path)
        postop_button.clicked.connect(lambda: self.go_to_sop_page("Brain Metastasis - Postoperative RT"))
        tiles_layout.addWidget(postop_button)

        # --- Re-Irradiation after WBRT Tile (Third) ---
        re_irrad_icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "bm_after_wbrt.png") # Icon path
        re_irrad_button = self._create_tile_button("Re-Irradiation after WBRT", icon_path=re_irrad_icon_path) # Pass icon path
        re_irrad_button.clicked.connect(lambda: self.go_to_sop_page("Brain Metastasis - Re-Irradiation after WBRT"))
        tiles_layout.addWidget(re_irrad_button)
        
        content_layout.addLayout(tiles_layout)
        content_layout.addStretch(1) # Push tiles up a bit
        
        # Add content frame to main layout
        main_layout.addWidget(content_frame)
        main_layout.setStretch(1, 1)  # Make content area expand

    def _create_tile_button(self, text, icon_path=None):
        button = QToolButton()
        button.setText(text)
        button.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        button.setMinimumSize(300, 320) # Adjusted min size for new icon size
        button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon) # Set icon below text
        button.setStyleSheet("""
            QToolButton {
                background-color: #1c5a9e; /* Ensures button background is blue */
                color: white;
                border: none;
                border-radius: 10px;
                padding: 20px; 
                text-align: center; 
            }
            QToolButton:hover {
                background-color: #2a69ad;
            }
            QToolButton:pressed {
                background-color: #154b8f; 
            }
        """)
        # Optional: Add an icon if desired
        if icon_path and os.path.exists(icon_path):
            button.setIcon(QIcon(icon_path))
            button.setIconSize(QSize(225, 225)) # Decreased icon size by 25%
            logging.debug(f"Set icon '{icon_path}' for button '{text}'")
            # Consider adjusting text position if icon makes it look crowded
            # button.setStyleSheet(button.styleSheet() + "QPushButton { text-align: center; padding-top: 10px; }") # Example
        else:
            logging.warning(f"Icon path not found or not provided for button '{text}': {icon_path}")
        return button

    def go_to_sop_page(self, subtype_name):
        # print(f"Navigating to SOP page for: {subtype_name}") # Placeholder action
        # --- Actual Navigation Logic to TumorPage ---
        logging.info(f"Opening TumorPage for Brain Metastasis subtype: {subtype_name}")
        # Check if the TumorPage for this subtype already exists
        existing_page_index = self.main_window.find_page_index(TumorPage, subtype_name)
        if existing_page_index is not None:
            logging.info(f"Found existing TumorPage for {subtype_name}, switching to it.")
            self.main_window.stacked_widget.setCurrentIndex(existing_page_index)
        else:
            logging.info(f"Creating new TumorPage for {subtype_name}.")
            # Create and navigate to the TumorPage
            tumor_page = TumorPage(self.main_window, subtype_name)
            new_index = self.main_window.stacked_widget.addWidget(tumor_page)
            self.main_window.stacked_widget.setCurrentIndex(new_index)

        # --- Temporary Placeholder Navigation ---
        # For now, let's just print. Replace with actual navigation later.
        # pass

    # def go_back(self):
    #     self.main_window.go_home() 