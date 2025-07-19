from components.widgets import StaticTile
from PyQt6.QtWidgets import QWidget, QGridLayout, QVBoxLayout, QScrollArea, QLabel
from PyQt6.QtCore import Qt
from pages.entity_pages.EntityPage import EntityPage
import os
import logging

class BindegewebstumorePage(QWidget):
    group_name = "Bindegewebstumore"
    
    def __init__(self, main_window):
        super().__init__()
        logging.info("Initializing BindegewebstumorePage...")
        self.main_window = main_window
        self.setup_ui()
        logging.info("BindegewebstumorePage UI setup complete.")

    def setup_ui(self):
        # --- Create Scroll Area --- 
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("QScrollArea { border: none; }")

        # --- Container widget for scroll area content --- 
        scroll_content_widget = QWidget()
        content_layout = QVBoxLayout(scroll_content_widget)
        content_layout.setSpacing(20)
        content_layout.setContentsMargins(10, 10, 40, 40)
        
        # --- Grid layout for placeholder labels --- 
        grid_layout = QGridLayout()
        grid_layout.setHorizontalSpacing(20) 
        grid_layout.setVerticalSpacing(50)   

        # Define placeholders 
        entities = ["Sarkom Extremitäten", "Sarkom Retroperitoneal"]
        
        assets_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "assets")

        for i, entity in enumerate(entities):
            image_path = None 
            contours_dir = os.path.join(assets_dir, "contours_images")
            
            if entity == "Sarkom Extremitäten":
                image_path = os.path.join(contours_dir, "contour_sarcoma.PNG")
            
            # Check if image exists, otherwise use None
            if image_path and not os.path.exists(image_path):
                image_path = None
                
            tile = StaticTile(entity, image_path)
            # Rename navigation method call
            tile.clicked.connect(lambda checked, e=entity: self.open_entity_page(e))
            grid_layout.addWidget(tile, i // 3, i % 3) # Arrange in 3 columns

        # Add grid layout to content layout
        content_layout.addLayout(grid_layout)
        content_layout.addStretch() # Push grid up

        # Set content widget for scroll area
        scroll_area.setWidget(scroll_content_widget)

        # Main page layout containing the scroll area
        page_layout = QVBoxLayout(self)
        page_layout.setContentsMargins(0, 0, 0, 0)
        page_layout.addWidget(scroll_area)

    def open_entity_page(self, entity_name):
        logging.info(f"Opening entity page for: {entity_name} from group {self.group_name}")
        existing_page_index = self.main_window.find_page_index(EntityPage, entity_name=entity_name, group_name=self.group_name)
        if existing_page_index is not None:
             self.main_window.stacked_widget.setCurrentIndex(existing_page_index)
        else:
            entity_page = EntityPage(self.main_window, entity_name, self.group_name)
            new_index = self.main_window.stacked_widget.addWidget(entity_page)
            self.main_window.stacked_widget.setCurrentIndex(new_index)
            logging.info(f"Created and navigated to EntityPage for {entity_name} from {self.group_name}.")