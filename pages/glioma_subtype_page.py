from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGridLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
import logging # Import logging module

# Importiere StaticTile aus der neuen Komponentendatei
from components.widgets import StaticTile
from .tumor_page import TumorPage

class GliomaSubtypePage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        logging.info("Initializing GliomaSubtypePage...")
        self.main_window = main_window
        self.setup_ui()
        logging.info("GliomaSubtypePage UI setup complete.")

    def setup_ui(self):
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        # Consistent margins (adjust top margin if needed, similar to other pages)
        main_layout.setContentsMargins(10, 0, 40, 40)
        self.setLayout(main_layout)

        # Add title (similar style to TumorPage title)
        title = QLabel("Select Glioma Subtype")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont('Arial', 24, QFont.Weight.Bold))
        title.setStyleSheet("color: white; margin-bottom: 20px;")
        main_layout.addWidget(title)

        # Grid layout for subtype tiles (like HomePage)
        grid_layout = QGridLayout()
        grid_layout.setSpacing(20)
        # Center the grid if only two items
        # grid_layout.setContentsMargins(50, 0, 50, 0) # Add horizontal margins to center - Removing this as 3 items might not need extra centering margin

        # Create subtype tiles
        subtypes = ["Anaplastic astrocytoma", "Glioblastoma", "Oligodendroglioma"]
        tiles = []
        for subtype in subtypes:
            # Create tile (reuse StaticTile for styling)
            tile = StaticTile(subtype, image_path=None)
            tile.clicked.connect(lambda checked, s=subtype: self.open_tumor_page(s))
            tiles.append(tile)

        # Add tiles to grid - Adjust for potentially three tiles
        if len(tiles) > 0:
            grid_layout.addWidget(tiles[0], 0, 0) # First tile in row 0, col 0
        if len(tiles) > 1:
            grid_layout.addWidget(tiles[1], 0, 1) # Second tile in row 0, col 1
        if len(tiles) > 2:
            grid_layout.addWidget(tiles[2], 0, 2) # Third tile in row 0, col 2
        # Add empty columns/rows if needed to help with centering, or adjust alignment

        # Add grid layout to main layout
        main_layout.addLayout(grid_layout)
        main_layout.addStretch() # Push grid towards the top

    def open_tumor_page(self, subtype_name):
        """Creates and navigates to the TumorPage for the selected subtype."""
        logging.info(f"Opening tumor page for Glioma subtype: {subtype_name}")
        # Check if a page for this specific subtype already exists
        existing_page_index = self.main_window.find_page_index(TumorPage, subtype_name)

        if existing_page_index is not None:
            logging.info(f"Found existing TumorPage for {subtype_name}, switching to it.")
            # Navigate to existing page
            self.main_window.stacked_widget.setCurrentIndex(existing_page_index)
        else:
            logging.info(f"Creating new TumorPage for {subtype_name}.")
            # Create a new TumorPage for the specific subtype
            tumor_page = TumorPage(self.main_window, subtype_name)
            new_index = self.main_window.stacked_widget.addWidget(tumor_page)
            self.main_window.stacked_widget.setCurrentIndex(new_index) 