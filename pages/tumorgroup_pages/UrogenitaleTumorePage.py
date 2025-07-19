from components.widgets import StaticTile
from PyQt6.QtWidgets import QWidget, QGridLayout, QVBoxLayout, QScrollArea
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from pages.entity_pages.EntityPage import EntityPage 
import os
import logging

class UrogenitaleTumorePage(QWidget):
    group_name = "Urogenitale Tumore"
    
    def __init__(self, main_window):
        super().__init__()
        logging.info("Initializing UrogenitaleTumorePage...")
        self.main_window = main_window
        self.setup_ui()
        logging.info("UrogenitaleTumorePage UI setup complete.")

    def setup_ui(self):
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("QScrollArea { border: none; }")

        scroll_content_widget = QWidget()
        content_layout = QVBoxLayout(scroll_content_widget)
        content_layout.setSpacing(20)
        content_layout.setContentsMargins(10, 10, 40, 40)
        
        grid_layout = QGridLayout()
        grid_layout.setHorizontalSpacing(20) 
        grid_layout.setVerticalSpacing(50)   

        entities = [
            "Prostata-Ca", "Blasen-Ca", "RCC"
        ]
        
        assets_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "assets")

        for i, entity in enumerate(entities):
            image_path = None 
            contours_dir = os.path.join(assets_dir, "contours_images")
            
            if entity == "Prostata-Ca":
                image_path = os.path.join(contours_dir, "contour_prostate.PNG")
            elif entity == "Blasen-Ca":
                image_path = os.path.join(contours_dir, "contour_bladder.PNG")
            
            # Check if image exists, otherwise use None
            if image_path and not os.path.exists(image_path):
                image_path = None
                
            tile = StaticTile(entity, image_path)
            tile.clicked.connect(lambda checked, e=entity: self.open_entity_page(e))
            grid_layout.addWidget(tile, i // 3, i % 3) 

        content_layout.addLayout(grid_layout)
        content_layout.addStretch() 

        scroll_area.setWidget(scroll_content_widget)

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