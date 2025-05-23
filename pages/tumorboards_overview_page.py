# pages/tumorboards_overview_page.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QScrollArea, QFrame, QGridLayout)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QPixmap, QIcon
import os
from data.tumorboard_config import TUMORBOARD_SCHEDULE, TUMORBOARD_LOCATIONS, USER_TUMORBOARDS_DIR # Importiere die Konfigurationen
import datetime

# Import für die spezifischen Tumorboard-Detailseiten
# from .specific_tumorboard_page import SpecificTumorboardPage # Wird später importiert, um Circular Imports zu vermeiden

class TumorboardTile(QPushButton):
    def __init__(self, board_info, parent=None):
        super().__init__(parent)
        self.board_info = board_info
        self.setMinimumHeight(100) # Mindesthöhe für bessere Klickbarkeit
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)

        name_label = QLabel(f"<b>{board_info['name']}</b>")
        name_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        name_label.setWordWrap(True)
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        time_label = QLabel(board_info['display_time'])
        time_label.setFont(QFont("Arial", 9))
        time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        location_text = TUMORBOARD_LOCATIONS.get(board_info['location_key'], 'Ort: N.N.')
        location_label = QLabel(f"<i>{location_text}</i>") # Kursiv für den Ort
        location_label.setFont(QFont("Arial", 9, italic=True))
        location_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        notes_label_text = board_info.get('notes', '')
        notes_label = QLabel(notes_label_text)
        notes_label.setFont(QFont("Arial", 8, QFont.Weight.Light))
        notes_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        notes_label.setWordWrap(True)
        if not notes_label_text: # Verstecke das Label, wenn keine Notizen da sind
            notes_label.setVisible(False)


        layout.addWidget(name_label)
        layout.addWidget(time_label)
        layout.addWidget(location_label)
        layout.addWidget(notes_label)
        layout.addStretch() # Um Inhalt nach oben zu drücken, falls Platz

        # Basis-Styling, das ggf. überschrieben werden kann
        self.setStyleSheet("""
            QPushButton {
                background-color: #2c3e50; /* Dunkelblau-Grau */
                color: white;
                border: 1px solid #34495e;
                border-radius: 8px;
                padding: 5px;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #34495e; /* Etwas heller im Hover */
            }
            QPushButton:pressed {
                background-color: #233140; /* Etwas dunkler beim Drücken */
            }
            QLabel { background-color: transparent; color: white; }
        """)


class TumorboardsOverviewPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20) # Außenabstände
        main_layout.setSpacing(20)

        title_label = QLabel("Tumorboard Wochenübersicht")
        title_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: white; margin-bottom: 15px;")
        main_layout.addWidget(title_label)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("QScrollArea { border: none; background-color: transparent; }") # Transparenter Hintergrund für ScrollArea

        scroll_content_widget = QWidget()
        scroll_content_widget.setStyleSheet("background-color: transparent;") # Stellt sicher, dass das Widget im Scrollbereich auch transparent ist
        
        # Hauptlayout für die Tage (horizontal)
        days_main_layout = QHBoxLayout(scroll_content_widget)
        days_main_layout.setSpacing(15) # Abstand zwischen den Tages-Spalten
        days_main_layout.setAlignment(Qt.AlignmentFlag.AlignTop) # Spalten oben ausrichten

        days_german = ["Mo", "Di", "Mi", "Do", "Fr"]
        day_frames = {}

        for day_idx, day_name_german in enumerate(days_german):
            day_frame = QFrame()
            day_frame.setObjectName(f"dayFrame{day_name_german}")
            day_frame.setFixedWidth(280) # Feste Breite pro Tagesspalte
            # Styling für den Rahmen jeder Tagesspalte
            day_frame.setStyleSheet(f"""
                QFrame#{day_frame.objectName()} {{
                    background-color: #1e2a38; /* Hintergrund für die Tages-Spalte */
                    border-radius: 10px;
                    padding: 10px;
                }}
            """)
            day_layout_vertical = QVBoxLayout(day_frame)
            day_layout_vertical.setContentsMargins(8, 8, 8, 8) # Innenabstände für die Spalte
            day_layout_vertical.setSpacing(10) # Abstand zwischen den Elementen in der Spalte
            day_layout_vertical.setAlignment(Qt.AlignmentFlag.AlignTop) # Elemente oben ausrichten

            day_header_label = QLabel(day_name_german)
            day_header_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
            day_header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            day_header_label.setStyleSheet("color: #e0e0e0; margin-bottom: 5px; background-color: transparent;")
            day_layout_vertical.addWidget(day_header_label)

            # ScrollArea für die Kacheln innerhalb eines Tages
            day_scroll_area = QScrollArea()
            day_scroll_area.setWidgetResizable(True)
            day_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            day_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            day_scroll_area.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")

            day_scroll_content_widget = QWidget() # Widget für die Kacheln dieses Tages
            day_scroll_content_widget.setStyleSheet("background-color: transparent;")
            
            # Layout für die Kacheln dieses Tages
            self.tiles_layout_for_day = QVBoxLayout(day_scroll_content_widget)
            self.tiles_layout_for_day.setContentsMargins(0,0,0,0) # Keine zusätzlichen Margins im Kachel-Layout
            self.tiles_layout_for_day.setSpacing(8) # Abstand zwischen Kacheln
            self.tiles_layout_for_day.setAlignment(Qt.AlignmentFlag.AlignTop)
            day_frames[day_idx] = self.tiles_layout_for_day # Speichere das Layout zum Hinzufügen von Kacheln

            day_scroll_area.setWidget(day_scroll_content_widget)
            day_layout_vertical.addWidget(day_scroll_area) # Füge die ScrollArea dem Tages-Frame hinzu
            
            days_main_layout.addWidget(day_frame)


        # Boards laden und den Tageslayouts zuordnen
        boards_by_day = {i: [] for i in range(5)} # 0=Mo, ..., 4=Fr
        for board in TUMORBOARD_SCHEDULE:
            if 0 <= board['day_numeric'] <= 4: # Nur Mo-Fr berücksichtigen
                boards_by_day[board['day_numeric']].append(board)

        for day_idx in range(5):
            # Sortiere Boards nach Startzeit
            sorted_boards_for_day = sorted(boards_by_day[day_idx], key=lambda b: b['time_start'])
            
            day_tile_layout = day_frames.get(day_idx)
            if day_tile_layout: # Überprüfen, ob das Layout existiert
                for board in sorted_boards_for_day:
                    tile = TumorboardTile(board)
                    tile.clicked.connect(lambda checked, b=board: self.open_specific_tumorboard(b))
                    day_tile_layout.addWidget(tile)
                day_tile_layout.addStretch() # Stellt sicher, dass Kacheln nach oben gedrückt werden

        scroll_area.setWidget(scroll_content_widget)
        main_layout.addWidget(scroll_area)

    def open_specific_tumorboard(self, board_info):
        print(f"INFO: Tumorboard-Kachel geklickt: {board_info['name']}")
        # Der Import hier, um Circular Dependency beim Start zu vermeiden
        from pages.specific_tumorboard_page import SpecificTumorboardPage

        # Prüfen, ob die Seite bereits existiert
        page_index = self.main_window.find_page_index(
            SpecificTumorboardPage,
            board_folder_name=board_info['folder_name'] # Identifikator für die Seite
        )

        if page_index is not None:
            self.main_window.stacked_widget.setCurrentIndex(page_index)
        else:
            specific_page = SpecificTumorboardPage(self.main_window, board_info)
            new_index = self.main_window.stacked_widget.addWidget(specific_page)
            self.main_window.stacked_widget.setCurrentIndex(new_index)