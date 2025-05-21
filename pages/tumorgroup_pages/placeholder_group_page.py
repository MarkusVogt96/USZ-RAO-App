from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
import logging

class PlaceholderGroupPage(QWidget):
    def __init__(self, main_window, group_name):
        super().__init__()
        logging.info(f"Initializing PlaceholderGroupPage for group: {group_name}")
        self.main_window = main_window
        self.group_name = group_name
        self.setup_ui()
        logging.info("PlaceholderGroupPage UI setup complete.")

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setLayout(layout)

        label = QLabel(f"Platzhalter für Tumorgruppe:\n{self.group_name}")
        font = QFont()
        font.setPointSize(16)
        label.setFont(font)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(label) 