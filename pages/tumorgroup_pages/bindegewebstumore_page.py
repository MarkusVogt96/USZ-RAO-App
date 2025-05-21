from components.widgets import StaticTile
from PyQt6.QtWidgets import QWidget, QGridLayout, QVBoxLayout, QScrollArea, QLabel
from PyQt6.QtCore import Qt
import os
import logging

class BindegewebstumorePage(QWidget):
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
        placeholders = ["Placeholder 1", "Placeholder 2"]

        for i, text in enumerate(placeholders):
            # Simple QLabel as placeholder
            label = QLabel(text)
            label.setFixedSize(400, 300) # Same size as StaticTile for alignment
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setStyleSheet("background-color: #114473; color: grey; border-radius: 10px; font-size: 16px;")
            grid_layout.addWidget(label, i // 3, i % 3) # Arrange in 3 columns

        # Add grid layout to content layout
        content_layout.addLayout(grid_layout)
        content_layout.addStretch() # Push grid up

        # Set content widget for scroll area
        scroll_area.setWidget(scroll_content_widget)

        # Main page layout containing the scroll area
        page_layout = QVBoxLayout(self)
        page_layout.setContentsMargins(0, 0, 0, 0)
        page_layout.addWidget(scroll_area)

    # Remove open_tumor_page method as it's no longer needed here
    # def open_tumor_page(self, tumor_type):
    #     ... 