from components.widgets import StaticTile
from PyQt6.QtWidgets import QWidget, QGridLayout, QPushButton, QLabel, QHBoxLayout, QVBoxLayout, QFrame
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QPalette, QColor, QPixmap, QIcon
from .tumor_page import TumorPage
from .glioma_subtype_page import GliomaSubtypePage
from .brain_metastasis_subtype_page import BrainMetastasisSubtypePage
import os
import logging # Import logging module

class HomePage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        logging.info("Initializing HomePage...")
        self.main_window = main_window
        self.setup_ui()
        logging.info("HomePage UI setup complete.")
        
    def setup_ui(self):
        # Main vertical layout
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        # Adjust top margin if needed, or remove if main window handles spacing
        main_layout.setContentsMargins(10, 0, 40, 40) # Removed top margin, main window handles it
        self.setLayout(main_layout)

        # Grid layout for tumor buttons
        grid_layout = QGridLayout()
        grid_layout.setSpacing(20)
        
        # Create tumor tiles
        tumors = ["Meningeoma", "Sarcoma", "Glioma", "Brain Metastasis"]
        
        for i, tumor in enumerate(tumors):
            # Set image path based on tumor type
            image_path = None
            if tumor == "Meningeoma":
                image_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "meningeoma.png")
            elif tumor == "Glioma":
                image_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "glioma.png")
            elif tumor == "Sarcoma":
                image_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "sarcoma.png")
            elif tumor == "Brain Metastasis":
                image_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "brain_metastasis.png")
                
            # Create tile with image if available
            tile = StaticTile(tumor, image_path)
            
            tile.clicked.connect(lambda checked, t=tumor: self.open_tumor_page(t))
            grid_layout.addWidget(tile, i // 2, i % 2)
            
        # Add grid layout to main layout
        main_layout.addLayout(grid_layout)
            
    def open_tumor_page(self, tumor_type):
        logging.info(f"Opening page for tumor type: {tumor_type}")
        if tumor_type == "Glioma":
            # Navigate to the new Glioma Subtype selection page
            # Check if it exists first
            subtype_page_index = self.main_window.find_page_index(GliomaSubtypePage)
            if subtype_page_index is not None:
                 self.main_window.stacked_widget.setCurrentIndex(subtype_page_index)
            else:
                glioma_subtype_page = GliomaSubtypePage(self.main_window)
                new_index = self.main_window.stacked_widget.addWidget(glioma_subtype_page)
                self.main_window.stacked_widget.setCurrentIndex(new_index)
                logging.info("Created and navigated to GliomaSubtypePage.")
        elif tumor_type == "Brain Metastasis":
            # Navigate to the Brain Metastasis Subtype selection page
            subtype_page_index = self.main_window.find_page_index(BrainMetastasisSubtypePage)
            if subtype_page_index is not None:
                 self.main_window.stacked_widget.setCurrentIndex(subtype_page_index)
            else:
                brain_met_subtype_page = BrainMetastasisSubtypePage(self.main_window)
                new_index = self.main_window.stacked_widget.addWidget(brain_met_subtype_page)
                self.main_window.stacked_widget.setCurrentIndex(new_index)
                logging.info("Created and navigated to BrainMetastasisSubtypePage.")
        else:
            # Original behavior for other tumor types
            # Check if page already exists
            existing_page_index = self.main_window.find_page_index(TumorPage, tumor_type)
            if existing_page_index is not None:
                 self.main_window.stacked_widget.setCurrentIndex(existing_page_index)
            else:
                tumor_page = TumorPage(self.main_window, tumor_type)
                new_index = self.main_window.stacked_widget.addWidget(tumor_page)
                self.main_window.stacked_widget.setCurrentIndex(new_index)
                logging.info(f"Created and navigated to TumorPage for {tumor_type}.")
