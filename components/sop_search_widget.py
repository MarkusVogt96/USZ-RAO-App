import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, 
                             QListWidget, QListWidgetItem, QLabel, QFrame)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QEvent
from PyQt6.QtGui import QFont, QPalette, QColor, QKeyEvent

class SopSearchWidget(QWidget):
    # Signal wird ausgesendet, wenn eine PDF ausgewählt wird
    pdf_selected = pyqtSignal(str)  # Dateipfad der ausgewählten PDF
    
    def __init__(self, sop_files_list=None, parent=None):
        super().__init__(parent)
        self.sop_files = sop_files_list or []
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self.perform_search)
        self._keyboard_navigation = False  # Flag für Keyboard-Navigation
        
        self.setup_ui()
        self.apply_styles()
        
    def setup_ui(self):
        # Hauptlayout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Widget-Größe für bessere Integration ins Layout
        self.setFixedWidth(300)
        
        # Suchfeld
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("SOP-Dateien durchsuchen...")
        self.search_input.setFixedHeight(40)  # 5px höher für bessere Textdarstellung
        self.search_input.setFixedWidth(300)
        self.search_input.textChanged.connect(self.on_text_changed)
        layout.addWidget(self.search_input)
        
        # Ergebnisliste (Dropdown)
        self.results_list = QListWidget()
        self.results_list.setFixedWidth(300)
        self.results_list.setMaximumHeight(200)
        self.results_list.hide()  # Standardmäßig versteckt
        self.results_list.itemClicked.connect(self.on_result_selected)
        
        # Scrollbar-Einstellungen: nur vertikale Scrollbar
        self.results_list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.results_list.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # Keyboard-Navigation aktivieren
        self.results_list.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
        layout.addWidget(self.results_list)
        
        # Overlay-Verhalten: Liste soll über anderen Elementen schweben
        # Verwende ToolTip statt Popup um Fokus-Probleme zu vermeiden
        self.results_list.setWindowFlags(Qt.WindowType.ToolTip | Qt.WindowType.FramelessWindowHint)
        self.results_list.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)
        
        # Event-Filter für bessere Benutzerinteraktion
        self.search_input.installEventFilter(self)
        self.results_list.installEventFilter(self)
        
    def apply_styles(self):
        # Stil für das Suchfeld
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: #232F3B;
                color: white;
                border: 2px solid #425061;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #3292ea;
            }
            QLineEdit::placeholder {
                color: #8A9BA8;
            }
        """)
        
        # Stil für die Ergebnisliste
        self.results_list.setStyleSheet("""
            QListWidget {
                background-color: #232F3B;
                color: white;
                border: 2px solid #3292ea;
                border-radius: 6px;
                outline: none;
            }
            QListWidget::item {
                padding: 8px 12px;
                border-bottom: 1px solid #425061;
                min-height: 20px;
            }
            QListWidget::item:hover {
                background-color: #3292ea;
            }
            QListWidget::item:selected {
                background-color: #4da2fa;
                color: white;
            }
            QListWidget::item:focus {
                background-color: #4da2fa;
                color: white;
            }
        """)
    
    def set_sop_files(self, sop_files_list):
        """Aktualisiert die Liste der verfügbaren SOP-Dateien"""
        self.sop_files = sop_files_list
        
    def on_text_changed(self, text):
        """Wird aufgerufen, wenn sich der Text im Suchfeld ändert"""
        if len(text) < 2:
            self.hide_results()
            return
            
        # Verzögerung für bessere Performance
        self.search_timer.stop()
        self.search_timer.start(300)  # 300ms Verzögerung
        
    def perform_search(self):
        """Führt die eigentliche Suche durch"""
        query = self.search_input.text().lower().strip()
        
        if len(query) < 2:
            self.hide_results()
            return
            
        # Suche in den SOP-Dateien
        matches = []
        for file_path in self.sop_files:
            filename = os.path.basename(file_path).lower()
            if query in filename:
                matches.append(file_path)
        
        self.show_results(matches)
        
    def show_results(self, matches):
        """Zeigt die Suchergebnisse an"""
        self.results_list.clear()
        
        if not matches:
            # Keine Ergebnisse
            item = QListWidgetItem("Keine Ergebnisse gefunden")
            item.setFlags(Qt.ItemFlag.NoItemFlags)  # Nicht anklickbar
            self.results_list.addItem(item)
        else:
            # Ergebnisse hinzufügen (maximal 10)
            for file_path in matches[:10]:
                filename = os.path.basename(file_path)
                # Entferne .pdf Endung für bessere Anzeige
                display_name = filename.replace('.pdf', '')
                
                item = QListWidgetItem(display_name)
                item.setData(Qt.ItemDataRole.UserRole, file_path)  # Vollständiger Pfad als Daten
                self.results_list.addItem(item)
        
        # Position der Liste unter dem Suchfeld
        search_pos = self.search_input.mapToGlobal(self.search_input.rect().bottomLeft())
        self.results_list.move(search_pos)
        
        # Höhe anpassen basierend auf Anzahl der Ergebnisse
        item_height = 40  # Geschätzte Höhe pro Item
        list_height = min(len(matches) * item_height + 10, 200)
        self.results_list.setFixedHeight(list_height)
        
        self.results_list.show()
        
        # Keine Auswahl beim ersten Anzeigen
        self.results_list.clearSelection()
        self.results_list.setCurrentRow(-1)
        
        # Fokus explizit beim Suchfeld behalten (außer bei Keyboard-Navigation)
        if not self._keyboard_navigation:
            self.search_input.setFocus()
        
    def hide_results(self):
        """Versteckt die Ergebnisliste"""
        self.results_list.hide()
        # Reset keyboard navigation flag
        self._keyboard_navigation = False
        
    def on_result_selected(self, item):
        """Wird aufgerufen, wenn ein Suchergebnis angeklickt wird"""
        file_path = item.data(Qt.ItemDataRole.UserRole)
        if file_path:
            self.pdf_selected.emit(file_path)
            self.search_input.clear()
            self.hide_results()
            # Fokus zurück zum Suchfeld nach der Auswahl
            self.search_input.setFocus()
            
    def clear_search(self):
        """Leert das Suchfeld und versteckt die Ergebnisse"""
        self.search_input.clear()
        self.hide_results()
        
    def eventFilter(self, obj, event):
        """Event-Filter für bessere Keyboard-Navigation und Klick-Verhalten"""
        if obj == self.search_input and event.type() == QEvent.Type.KeyPress:
            key_event = event
            if key_event.key() == Qt.Key.Key_Down and self.results_list.isVisible():
                # Pfeil nach unten: Fokus zur Ergebnisliste
                self._keyboard_navigation = True
                self.results_list.setFocus()
                if self.results_list.count() > 0:
                    self.results_list.setCurrentRow(0)
                return True
            elif key_event.key() == Qt.Key.Key_Up and self.results_list.isVisible():
                # Pfeil nach oben: Fokus zur Ergebnisliste (letztes Element)
                self._keyboard_navigation = True
                self.results_list.setFocus()
                if self.results_list.count() > 0:
                    self.results_list.setCurrentRow(self.results_list.count() - 1)
                return True
            elif key_event.key() == Qt.Key.Key_Escape:
                # Escape: Ergebnisse verstecken
                self.hide_results()
                return True
                
        elif obj == self.results_list:
            if event.type() == QEvent.Type.KeyPress:
                key_event = event
                if key_event.key() == Qt.Key.Key_Return or key_event.key() == Qt.Key.Key_Enter:
                    # Enter: Aktuelles Element auswählen
                    current_item = self.results_list.currentItem()
                    if current_item and current_item.data(Qt.ItemDataRole.UserRole):
                        self.on_result_selected(current_item)
                        return True
                    # Falls kein Item ausgewählt ist, aber Items vorhanden sind, wähle das erste
                    elif self.results_list.count() > 0:
                        first_item = self.results_list.item(0)
                        if first_item and first_item.data(Qt.ItemDataRole.UserRole):
                            self.results_list.setCurrentRow(0)
                            self.on_result_selected(first_item)
                            return True
                    return True
                elif key_event.key() == Qt.Key.Key_Escape:
                    # Escape: Zurück zum Suchfeld
                    self._keyboard_navigation = False
                    self.hide_results()
                    self.search_input.setFocus()
                    return True
                elif key_event.key() == Qt.Key.Key_Up:
                    # Pfeil nach oben: Wenn am Anfang, zurück zum Suchfeld
                    if self.results_list.currentRow() == 0:
                        self._keyboard_navigation = False
                        self.search_input.setFocus()
                        return True
                    # Ansonsten normale Navigation
                    return False
                elif key_event.key() == Qt.Key.Key_Down:
                    # Pfeil nach unten: Normale Navigation, aber nicht über das Ende hinaus
                    if self.results_list.currentRow() >= self.results_list.count() - 1:
                        return True  # Verhindere Navigation über das Ende hinaus
                    return False
            elif event.type() == QEvent.Type.FocusIn:
                # Wenn die Liste Fokus bekommt, gib ihn zurück an das Suchfeld
                # außer wenn explizit mit Pfeiltasten navigiert wird
                if not self._keyboard_navigation:
                    self.search_input.setFocus()
                    return True
                
        return super().eventFilter(obj, event) 