from components.widgets import StaticTile
from PyQt6.QtWidgets import QWidget, QGridLayout, QVBoxLayout, QScrollArea
from PyQt6.QtCore import Qt
import os
import logging
# Import existing group pages
from pages.tumorgroup_pages.neuroonkologie_page import NeuroonkologiePage
from pages.tumorgroup_pages.bindegewebstumore_page import BindegewebstumorePage
# Import the NEW specific group pages
from pages.tumorgroup_pages.KopfHalsTumorePage import KopfHalsTumorePage
from pages.tumorgroup_pages.ThorakaleTumorePage import ThorakaleTumorePage
from pages.tumorgroup_pages.GastrointestinaleTumorePage import GastrointestinaleTumorePage
from pages.tumorgroup_pages.UrogenitaleTumorePage import UrogenitaleTumorePage
from pages.tumorgroup_pages.GynPage import GynPage
from pages.tumorgroup_pages.HauttumorePage import HauttumorePage
from pages.tumorgroup_pages.LymphomePage import LymphomePage
from pages.tumorgroup_pages.FernmetastasenPage import FernmetastasenPage
from pages.tumorgroup_pages.GutartigeErkrankungenPage import GutartigeErkrankungenPage

class TumorGroupPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        logging.info("Initializing TumorGroupPage...")
        self.main_window = main_window
        self.setup_ui()
        logging.info("TumorGroupPage UI setup complete.")

    def setup_ui(self):
        # --- Create Scroll Area --- 
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff) # Hide horizontal scrollbar
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded) # Show vertical only when needed
        scroll_area.setStyleSheet("QScrollArea { border: none; }") # Optional: remove border if theme adds one

        # --- Create a container widget for the scroll area content --- 
        scroll_content_widget = QWidget()

        # --- Create the layout for the container widget (this was the old main_layout) --- 
        content_layout = QVBoxLayout(scroll_content_widget) # Apply layout to the container
        content_layout.setSpacing(20) # Spacing for the QVBoxLayout itself (if needed)
        content_layout.setContentsMargins(10, 10, 40, 40) # Margins *inside* the scroll area
        # Add stretch at the bottom to push grid content upwards if space allows
        # content_layout.addStretch() 

        # Grid layout for tumor group buttons
        grid_layout = QGridLayout()
        # Set individual horizontal and vertical spacing
        grid_layout.setHorizontalSpacing(20) # Half of the previous large spacing
        grid_layout.setVerticalSpacing(50)   # Keep the vertical spacing user liked
        # Remove the combined spacing setting
        # grid_layout.setSpacing(400)

        # Define tumor groups in the final desired order
        tumor_groups = [
            "Neuroonkologie", "Kopf-Hals-Tumore", "Thorakale Tumore",
            "Gastrointestinale Tumore", "Urogenitale Tumore", "Gynäkologische Tumore",
            "Bindegewebstumore", "Hauttumore", "Lymphome",
            "Fernmetastasen", "Gutartige Erkrankungen" # Adjusted order
        ]

        # Map groups to potential placeholder images, fully updated
        group_images = {
            "Neuroonkologie": "tumorgroup_neuroonkologie.png",
            "Kopf-Hals-Tumore": "tumorgroup_kopfhalstumore.png",
            "Thorakale Tumore": "tumorgroup_thorakal.png",
            "Gastrointestinale Tumore": "tumorgroup_gastrointestinal.png",
            "Urogenitale Tumore": "tumorgroup_urogenital.png",
            "Gynäkologische Tumore": "tumorgroup_gyn.png",
            "Hauttumore": "tumorgroup_haut.png",
            "Bindegewebstumore": "tumorgroup_bindegewebstumore.png", # Updated
            "Lymphome": "tumorgroup_lymphome.png", # Added
            "Fernmetastasen": "tumorgroup_fernmetastasen.png", # Added
            "Gutartige Erkrankungen": "tumorgroup_gutartige.png", # Added
        }
        # Define path to assets directory - corrected path
        assets_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "assets")
        # Remove the specific default_image_path, we check existence below
        # default_image_path = os.path.join(assets_dir, "placeholder.png")

        # Create tumor group tiles
        for i, group in enumerate(tumor_groups):
            # Get the specific image filename for the group, default to None if not found
            image_name = group_images.get(group)
            image_path = None # Reset image_path
            if image_name:
                potential_path = os.path.join(assets_dir, image_name)
                if os.path.exists(potential_path):
                    image_path = potential_path
                else:
                    logging.warning(f"Image file not found for group '{group}': {potential_path}")
            
            # If no specific image found or defined, log it (no placeholder fallback for now)
            if not image_path:
                logging.info(f"No image assigned or found for tumor group: {group}")
            
            # Create the tile (pass None if no image_path was set)
            tile = StaticTile(group, image_path)
            tile.clicked.connect(lambda checked, g=group: self.open_group_page(g))
            grid_layout.addWidget(tile, i // 3, i % 3) # Arrange in 3 columns

        # --- Add grid layout to the content layout --- 
        content_layout.addLayout(grid_layout)
        # Add stretch *after* the grid to push it up
        content_layout.addStretch() 

        # --- Set the container widget as the widget for the scroll area --- 
        scroll_area.setWidget(scroll_content_widget)

        # --- Create the main layout for the TumorGroupPage widget --- 
        page_layout = QVBoxLayout(self) # Apply layout directly to self (TumorGroupPage)
        page_layout.setContentsMargins(0, 0, 0, 0) # No margins for the page layout itself
        page_layout.addWidget(scroll_area) # Add the scroll area to the page layout

    def open_group_page(self, group_name):
        logging.info(f"Opening page for tumor group: {group_name}")
        target_page_class = None
        # Map group names to their specific page classes
        group_page_map = {
            "Neuroonkologie": NeuroonkologiePage,
            "Kopf-Hals-Tumore": KopfHalsTumorePage,
            "Thorakale Tumore": ThorakaleTumorePage,
            "Gastrointestinale Tumore": GastrointestinaleTumorePage,
            "Urogenitale Tumore": UrogenitaleTumorePage,
            "Gynäkologische Tumore": GynPage,
            "Bindegewebstumore": BindegewebstumorePage,
            "Hauttumore": HauttumorePage,
            "Lymphome": LymphomePage,
            "Fernmetastasen": FernmetastasenPage,
            "Gutartige Erkrankungen": GutartigeErkrankungenPage,
        }
        
        target_page_class = group_page_map.get(group_name)
        
        if target_page_class:
            # Check if a page of this specific type already exists
            page_index = -1
            for i in range(self.main_window.stacked_widget.count()):
                widget = self.main_window.stacked_widget.widget(i)
                if isinstance(widget, target_page_class):
                    # Check if it's the correct instance for group pages that might have specific initial data
                    # (Currently not needed as they don't take group_name in __init__, but good practice)
                    # if hasattr(widget, 'group_identifier_attribute') and widget.group_identifier_attribute == some_value:
                    page_index = i
                    break
            
            if page_index != -1:
                self.main_window.stacked_widget.setCurrentIndex(page_index)
                logging.info(f"Navigated to existing {target_page_class.__name__} for group '{group_name}'.")
            else:
                # Create and navigate to the new page
                # Pass only main_window as argument (constructor of specific pages expects this)
                new_page = target_page_class(self.main_window)
                new_index = self.main_window.stacked_widget.addWidget(new_page)
                self.main_window.stacked_widget.setCurrentIndex(new_index)
                logging.info(f"Created and navigated to {target_page_class.__name__} for group '{group_name}'.")
        else:
             # Log error if group name doesn't match any known page
             logging.error(f"Could not determine target page class for group: {group_name}") 