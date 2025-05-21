from components.widgets import StaticTile
from PyQt6.QtWidgets import QWidget, QGridLayout, QVBoxLayout, QScrollArea, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
# EntityPage import not needed if no entities are listed
# from pages.entity_pages.EntityPage import EntityPage 
import os
import logging

class GutartigeErkrankungenPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        logging.info("Initializing GutartigeErkrankungenPage...")
        self.main_window = main_window
        self.setup_ui()
        logging.info("GutartigeErkrankungenPage UI setup complete.")

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

        # No entities defined for this group yet
        entities = []
        
        if not entities:
             placeholder_label = QLabel("Keine Entitäten für diese Gruppe definiert.")
             placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
             placeholder_label.setStyleSheet("color: grey; font-size: 16px;")
             content_layout.addWidget(placeholder_label)
        else:
            assets_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets")
            for i, entity in enumerate(entities):
                image_path = None 
                tile = StaticTile(entity, image_path)
                # tile.clicked.connect(lambda checked, e=entity: self.open_entity_page(e))
                grid_layout.addWidget(tile, i // 3, i % 3) 
            content_layout.addLayout(grid_layout)
        
        content_layout.addStretch() 

        scroll_area.setWidget(scroll_content_widget)

        page_layout = QVBoxLayout(self)
        page_layout.setContentsMargins(0, 0, 0, 0)
        page_layout.addWidget(scroll_area)

    # No open_entity_page needed if there are no entities to navigate to
    # def open_entity_page(self, entity_name):
    #     ... 