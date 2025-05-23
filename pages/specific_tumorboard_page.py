# pages/specific_tumorboard_page.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QScrollArea, QFrame, QSizePolicy
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont
import os
import datetime
from data.tumorboard_config import USER_TUMORBOARDS_DIR # Importiere Basispfad

# Import für die Excel-Ansicht Seite
# from .tumorboard_excel_view_page import TumorboardExcelViewPage # Wird später importiert

class DatedTumorboardTile(QPushButton):
    def __init__(self, date_str, date_folder_path, parent=None):
        super().__init__(parent)
        self.date_str = date_str
        self.date_folder_path = date_folder_path
        self.setText(date_str)
        self.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.setMinimumHeight(50)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Standard-Styling
        self.setStyleSheet("""
            QPushButton {
                background-color: #34495e; /* Dunkleres Blau-Grau */
                color: white;
                border: 1px solid #2c3e50;
                border-radius: 6px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #4a6fa5; /* Heller bei Hover */
            }
            QPushButton:pressed {
                background-color: #2c3e50;
            }
        """)

    def set_text_color(self, color_name):
        current_style = self.styleSheet()
        # Entferne alte color-Eigenschaft und füge neue hinzu
        import re
        current_style = re.sub(r"color\s*:\s*[^;]+;", "", current_style)
        self.setStyleSheet(current_style + f"color: {color_name};")


class SpecificTumorboardPage(QWidget):
    def __init__(self, main_window, board_info):
        super().__init__()
        self.main_window = main_window
        self.board_info = board_info
        # Für find_page_index, um diese spezifische Instanz zu identifizieren
        self.board_folder_name = board_info.get('folder_name', 'UnknownBoard')
        self.setup_ui()
        self.load_board_dates()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        title_label = QLabel(f"Tumorboard: {self.board_info.get('name', 'Unbekannt')}")
        title_label.setFont(QFont("Arial", 22, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: white; margin-bottom: 10px;")
        main_layout.addWidget(title_label)

        # Sektion für aktuelle/zukünftige Termine
        current_section_frame = QFrame()
        current_section_frame.setObjectName("currentSectionFrame")
        current_section_layout = QVBoxLayout(current_section_frame)
        current_section_layout.setContentsMargins(0,0,0,0)
        current_section_layout.setSpacing(8)
        
        current_header = QLabel("Aktuelle/Zukünftige Termine")
        current_header.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        current_header.setStyleSheet("color: #bdc3c7; margin-bottom: 5px;")
        current_section_layout.addWidget(current_header)
        
        self.current_scroll_area = QScrollArea()
        self.current_scroll_area.setWidgetResizable(True)
        self.current_scroll_area.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        self.current_scroll_content = QWidget()
        self.current_scroll_content.setStyleSheet("background-color: transparent;")
        self.current_tiles_layout = QVBoxLayout(self.current_scroll_content)
        self.current_tiles_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.current_tiles_layout.setSpacing(8)
        self.current_scroll_area.setWidget(self.current_scroll_content)
        current_section_layout.addWidget(self.current_scroll_area)
        
        main_layout.addWidget(current_section_frame)
        
        # Trennlinie
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("background-color: #425061; min-height: 1px; max-height: 1px; margin-top: 10px; margin-bottom: 10px;")
        main_layout.addWidget(separator)

        # Sektion für abgeschlossene Termine
        past_section_frame = QFrame()
        past_section_frame.setObjectName("pastSectionFrame")
        past_section_layout = QVBoxLayout(past_section_frame)
        past_section_layout.setContentsMargins(0,0,0,0)
        past_section_layout.setSpacing(8)

        past_header = QLabel("Abgeschlossene Termine")
        past_header.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        past_header.setStyleSheet("color: #bdc3c7; margin-bottom: 5px;")
        past_section_layout.addWidget(past_header)

        self.past_scroll_area = QScrollArea()
        self.past_scroll_area.setWidgetResizable(True)
        self.past_scroll_area.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        self.past_scroll_content = QWidget()
        self.past_scroll_content.setStyleSheet("background-color: transparent;")
        self.past_tiles_layout = QVBoxLayout(self.past_scroll_content)
        self.past_tiles_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.past_tiles_layout.setSpacing(8)
        self.past_scroll_area.setWidget(self.past_scroll_content)
        past_section_layout.addWidget(self.past_scroll_area)

        main_layout.addWidget(past_section_frame)

        # Style für die Frames
        section_frame_style = """
            QFrame#currentSectionFrame, QFrame#pastSectionFrame {
                background-color: #232f3b; /* Dunklerer Hintergrund für Sektionen */
                border-radius: 8px;
                padding: 15px;
            }
        """
        self.setStyleSheet(section_frame_style)


    def load_board_dates(self):
        board_folder_path = os.path.join(USER_TUMORBOARDS_DIR, self.board_info['folder_name'])
        
        # Clear existing tiles before loading new ones
        self._clear_layout_widgets(self.current_tiles_layout)
        self._clear_layout_widgets(self.past_tiles_layout)

        if not os.path.exists(board_folder_path):
            no_dates_label_current = QLabel(f"Keine Termine für {self.board_info['name']} gefunden (Ordner fehlt).")
            no_dates_label_current.setStyleSheet("color: grey; font-style: italic;")
            self.current_tiles_layout.addWidget(no_dates_label_current)
            
            no_dates_label_past = QLabel(f"Keine Termine für {self.board_info['name']} gefunden (Ordner fehlt).")
            no_dates_label_past.setStyleSheet("color: grey; font-style: italic;")
            self.past_tiles_layout.addWidget(no_dates_label_past)
            return

        today = datetime.date.today()
        current_dates = []
        past_dates = []

        for item_name in os.listdir(board_folder_path):
            item_path = os.path.join(board_folder_path, item_name)
            if os.path.isdir(item_path): # Nur Ordner berücksichtigen
                try:
                    date_obj = datetime.datetime.strptime(item_name, "%d.%m.%Y").date()
                    # Prüfen, ob eine Excel-Datei mit dem gleichen Namen wie der Ordner existiert
                    excel_file_name = f"{item_name}.xlsx"
                    excel_file_path = os.path.join(item_path, excel_file_name)
                    if os.path.exists(excel_file_path):
                        if date_obj >= today:
                            current_dates.append((date_obj, item_name, item_path))
                        else:
                            past_dates.append((date_obj, item_name, item_path))
                    else:
                        print(f"WARNUNG: Excel-Datei '{excel_file_name}' nicht im Ordner '{item_path}' gefunden. Termin wird ignoriert.")
                except ValueError:
                    # Ignoriere Ordner, die nicht dem Datumsformat entsprechen
                    pass
        
        # Sortiere Termine: Aktuelle aufsteigend, Vergangene absteigend
        current_dates.sort(key=lambda x: x[0])
        past_dates.sort(key=lambda x: x[0], reverse=True)

        if not current_dates:
            no_current_label = QLabel("Keine aktuellen oder zukünftigen Termine.")
            no_current_label.setStyleSheet("color: grey; font-style: italic;")
            self.current_tiles_layout.addWidget(no_current_label)
        else:
            for date_obj, date_str, folder_path in current_dates:
                tile = DatedTumorboardTile(date_str, folder_path)
                tile.set_text_color("#4CAF50") # Grün
                tile.clicked.connect(lambda checked, fp=folder_path, dt=date_str: self.open_excel_view(fp, f"{dt}.xlsx"))
                self.current_tiles_layout.addWidget(tile)
        self.current_tiles_layout.addStretch()


        if not past_dates:
            no_past_label = QLabel("Keine abgeschlossenen Termine.")
            no_past_label.setStyleSheet("color: grey; font-style: italic;")
            self.past_tiles_layout.addWidget(no_past_label)
        else:
            for date_obj, date_str, folder_path in past_dates:
                tile = DatedTumorboardTile(date_str, folder_path)
                tile.set_text_color("white") # Weiß
                tile.clicked.connect(lambda checked, fp=folder_path, dt=date_str: self.open_excel_view(fp, f"{dt}.xlsx"))
                self.past_tiles_layout.addWidget(tile)
        self.past_tiles_layout.addStretch()

    def open_excel_view(self, date_folder_path, excel_file_name):
        print(f"INFO: Excel-Ansicht angefordert für: {date_folder_path} / {excel_file_name}")
        from pages.tumorboard_excel_view_page import TumorboardExcelViewPage # Import hier

        page_index = self.main_window.find_page_index(
            TumorboardExcelViewPage,
            date_folder_path=date_folder_path # Verwende einen eindeutigen Identifikator
        )

        if page_index is not None:
            self.main_window.stacked_widget.setCurrentIndex(page_index)
        else:
            excel_page = TumorboardExcelViewPage(self.main_window, date_folder_path, excel_file_name, self.board_info['name'])
            new_index = self.main_window.stacked_widget.addWidget(excel_page)
            self.main_window.stacked_widget.setCurrentIndex(new_index)

    def _clear_layout_widgets(self, layout):
        """ Hilfsmethode zum Entfernen aller Widgets aus einem Layout. """
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()