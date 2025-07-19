from PyQt6.QtWidgets import QPushButton, QVBoxLayout, QLabel
from PyQt6.QtGui import QFont, QPixmap, QPainter, QPainterPath
from PyQt6.QtCore import Qt, QSize, QRectF # Added QSize import
import os # Needed for path joining

class StaticTile(QPushButton):
    def __init__(self, text, image_path=None, parent=None):
        super().__init__(parent)
        self.setFixedSize(400, 300)

        # Set basic button styling
        self.setStyleSheet("""
            QPushButton {
                background-color: #114473;
                color: white;
                border: none;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #1a5a9e;
            }
            QPushButton:pressed {
                background-color: #0d2e4d;
            }
        """)

        # Create layout for button content
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 20, 10, 20)
        layout.setSpacing(20)
        self.setLayout(layout)

        # Add text label at the top
        text_label = QLabel(text)
        text_label.setStyleSheet("color: white; background: transparent;")
        text_label.setFont(QFont('Calibri', 16, QFont.Weight.Bold))
        text_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(text_label)

        # Add image if provided
        if image_path and os.path.exists(image_path):
            image_label = QLabel()
            pixmap = QPixmap(image_path)
            # Scale image to fit within tile (max 280px height, maintaining aspect ratio)
            pixmap = pixmap.scaledToHeight(200, Qt.TransformationMode.SmoothTransformation)
            
            # Create rounded corners using QPainter
            rounded_pixmap = self.create_rounded_pixmap(pixmap, 10)
            
            image_label.setPixmap(rounded_pixmap)
            image_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            image_label.setStyleSheet("background: transparent;")
            layout.addWidget(image_label)
            
        # Add stretch to push content to top
        layout.addStretch()
    
    def create_rounded_pixmap(self, pixmap, radius):
        """Create a pixmap with rounded corners"""
        # Create a new pixmap with transparent background
        rounded = QPixmap(pixmap.size())
        rounded.fill(Qt.GlobalColor.transparent)
        
        # Create painter
        painter = QPainter(rounded)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Create rounded rectangle path
        path = QPainterPath()
        path.addRoundedRect(QRectF(rounded.rect()), radius, radius)
        
        # Set the clipping path and draw the original pixmap
        painter.setClipPath(path)
        painter.drawPixmap(0, 0, pixmap)
        painter.end()
        
        return rounded

class SmallTile(QPushButton):
    def __init__(self, text, filename=None, script_exists=True, image_path=None, parent=None):
        super().__init__(parent)
        self.setFixedSize(220, 130)

        # Set basic button styling
        self.setStyleSheet("""
            QPushButton {
                background-color: #114473;
                color: white;
                border: none;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #1a5a9e;
            }
            QPushButton:pressed {
                background-color: #0d2e4d;
            }
        """)

        # Create layout for button content
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)
        self.setLayout(layout)

        # Main text label (Tile Name) - Color changes based on script_exists
        text_label = QLabel(text)
        title_color = "lime" if script_exists else "#CC0000" # Green if exists, darker red if not
        text_label.setStyleSheet(f"color: {title_color}; background: transparent;")
        text_label.setFont(QFont('Calibri', 14, QFont.Weight.Bold))
        text_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        text_label.setWordWrap(True)
        layout.addWidget(text_label)

        # Add subtitle label (Filename or "Kein script verknüpft")
        subtitle_text = ""
        if script_exists and filename:
            subtitle_text = filename
        elif not script_exists:
             # This covers both file not found and mapping not found (filename is None)
            subtitle_text = "Kein script verknüpft"

        if subtitle_text: # Only add the label if there's subtitle text
            filename_label = QLabel(subtitle_text)
            # Style for smaller, less prominent filename/message
            filename_label.setStyleSheet("color: #cccccc; background: transparent;") # Light gray
            filename_font = QFont('Calibri', 10) # Smaller font size
            filename_label.setFont(filename_font)
            filename_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            filename_label.setWordWrap(True)
            layout.addWidget(filename_label)
            # Reduce spacing after subtitle if there's no image
            if not (image_path and os.path.exists(image_path)):
                layout.setSpacing(2) # Tighter spacing

        # Add image if provided
        if image_path and os.path.exists(image_path):
             # Reset spacing if subtitle was added and image exists
            if subtitle_text:
                layout.setSpacing(6) # Reset to default spacing if both subtitle and image exist
            image_label = QLabel()
            pixmap = QPixmap(image_path)
            pixmap = pixmap.scaledToHeight(80, Qt.TransformationMode.SmoothTransformation)
            image_label.setPixmap(pixmap)
            image_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            layout.addWidget(image_label)
            
        # Add stretch to push content to top
        layout.addStretch()