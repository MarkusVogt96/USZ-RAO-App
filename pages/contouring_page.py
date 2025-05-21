from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
import logging

class ContouringPage(QWidget):
    def __init__(self, main_window, tumor_type):
        super().__init__()
        logging.info(f"Initializing ContouringPage for tumor: {tumor_type}...")
        self.main_window = main_window
        self.tumor_type = tumor_type
        self.setup_ui()
        logging.info(f"ContouringPage UI setup complete for {tumor_type}.")

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(10, 0, 40, 40)
        self.setLayout(layout)

        # Add title
        title = QLabel(f"Contouring Instructions - {self.tumor_type}")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont('Arial', 24, QFont.Weight.Bold))
        title.setStyleSheet("color: white; margin-bottom: 20px;")
        layout.addWidget(title)

        # Add work in progress message
        wip_label = QLabel("Work in Progress")
        wip_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        wip_label.setFont(QFont('Arial', 18))
        wip_label.setStyleSheet("color: white;")
        layout.addWidget(wip_label)

        # Add stretch to center the content
        layout.addStretch() 