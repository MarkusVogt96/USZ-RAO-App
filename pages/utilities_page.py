from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QScrollArea, QHBoxLayout, 
                             QGroupBox, QGridLayout, QDoubleSpinBox, QSpinBox, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QFrame)
from PyQt6.QtCore import Qt, QLocale
from PyQt6.QtGui import QFont, QDoubleValidator
import logging

class UtilitiesPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        logging.info("Initializing UtilitiesPage...")
        self.main_window = main_window
        self.setup_ui()
        logging.info("UtilitiesPage UI setup complete.")
        
    def setup_ui(self):
        # Main layout for the entire page
        page_layout = QVBoxLayout()
        page_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(page_layout)
        
        # Create scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)
        
        # Content widget
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(10)
        
        # Page Title
        title_label = QLabel("Utilities")
        title_font = QFont()
        title_font.setPointSize(28)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: white; margin-bottom: 20px;")
        content_layout.addWidget(title_label)
        
        # EQD2/BED Calculator
        self.create_eqd2_calculator(content_layout)
        
        # Add stretch to push content to top
        content_layout.addStretch()
        
        # Set content widget to scroll area
        scroll_area.setWidget(content_widget)
        page_layout.addWidget(scroll_area)
    
    def create_eqd2_calculator(self, parent_layout):
        """Erstellt den EQD2/BED-Rechner"""
        # Calculator GroupBox
        calc_group = QGroupBox("EQD2 / BED Rechner")
        calc_group.setStyleSheet("""
            QGroupBox {
                font-size: 18px;
                font-weight: bold;
                color: white;
                border: 2px solid #2a3642;
                border-radius: 8px;
                margin: 10px 0px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
            }
        """)
        
        calc_layout = QVBoxLayout(calc_group)
        calc_layout.setSpacing(30)
        calc_layout.setContentsMargins(20, 15, 20, 15)
        
        # Eingabebereich
        input_frame = QFrame()
        input_frame.setStyleSheet("""
            QFrame {
                background-color: #114473;
                border-radius: 8px;
                border: 1px solid #2a3642;
                padding: 8px;
            }
        """)
        input_layout = QHBoxLayout(input_frame)
        input_layout.setSpacing(15)
        input_layout.setContentsMargins(8, 5, 8, 5)
        
        # Anzahl Fraktionen
        fractions_layout = QVBoxLayout()
        fractions_layout.setSpacing(5)
        fractions_label = QLabel("Anzahl Fraktionen:")
        fractions_label.setStyleSheet("font-size: 14px; font-weight: bold; color: white;")
        self.fractions_spinbox = QSpinBox()
        self.fractions_spinbox.setRange(1, 100)
        self.fractions_spinbox.setValue(25)
        self.fractions_spinbox.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)
        self.fractions_spinbox.setStyleSheet("""
            QSpinBox {
                font-size: 14px;
                padding: 5px;
                border: 1px solid #2a3642;
                border-radius: 4px;
                background-color: #0f1419;
                color: white;
            }
            QSpinBox:focus {
                border-color: #367E9E;
            }
        """)
        fractions_layout.addWidget(fractions_label)
        fractions_layout.addWidget(self.fractions_spinbox)
        
        # Dosis pro Fraktion
        dose_layout = QVBoxLayout()
        dose_layout.setSpacing(5)
        dose_label = QLabel("Dosis pro Fraktion [Gy]:")
        dose_label.setStyleSheet("font-size: 14px; font-weight: bold; color: white;")
        self.dose_spinbox = QDoubleSpinBox()
        self.dose_spinbox.setRange(0.1, 20.0)
        self.dose_spinbox.setValue(2)
        self.dose_spinbox.setDecimals(2)
        self.dose_spinbox.setSingleStep(0.1)
        self.dose_spinbox.setButtonSymbols(QDoubleSpinBox.ButtonSymbols.NoButtons)
        
        # Setze deutsches Locale für Komma als Dezimaltrennzeichen
        german_locale = QLocale(QLocale.Language.German, QLocale.Country.Germany)
        self.dose_spinbox.setLocale(german_locale)
        self.dose_spinbox.setStyleSheet("""
            QDoubleSpinBox {
                font-size: 14px;
                padding: 5px;
                border: 1px solid #2a3642;
                border-radius: 4px;
                background-color: #0f1419;
                color: white;
            }
            QDoubleSpinBox:focus {
                border-color: #367E9E;
            }
        """)
        dose_layout.addWidget(dose_label)
        dose_layout.addWidget(self.dose_spinbox)
        
        input_layout.addLayout(fractions_layout)
        input_layout.addLayout(dose_layout)
        input_layout.addStretch()
        
        calc_layout.addWidget(input_frame)
        
        # Ergebnistabelle (ohne Zeilennummerierung)
        self.results_table = QTableWidget(4, 3)
        self.results_table.setHorizontalHeaderLabels(["α/β", "EQD2 (Gy)", "BED (Gy)"])
        
        # Entferne Zeilennummerierung
        self.results_table.verticalHeader().setVisible(False)
        
        # Tabellen-Konfiguration wie EntityPage
        self.results_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.results_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.results_table.setAlternatingRowColors(True)
        
        # EntityPage-Tabellen-Styling
        self.results_table.setStyleSheet("""
            QTableWidget {
                background-color: #2a2a2a;
                color: white;
                border: none;
                border-radius: 10px;
                gridline-color: #5a5a5a;
                margin-left: 20px;
                margin-right: 20px;
                font-size: 13px;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #5a5a5a;
                border-right: 1px solid #5a5a5a;
            }
            QTableWidget::item:alternate {
                background-color: #3a3a3a;
            }
            QTableWidget::item:selected {
                background-color: #1a5a9e;
            }
            QHeaderView::section {
                background-color: #114473;
                color: white;
                padding: 2px;
                border: 1px solid #1a5a9e;
                font-weight: bold;
                font-size: 14px;
            }
            QHeaderView::section:first {
                border-top-left-radius: 10px;
                border-left: none;
            }
            QHeaderView::section:last {
                border-top-right-radius: 10px;
                border-right: none;
            }
            QHeaderView {
                border: none;
            }
        """)
        
        # α/β-Werte einfügen
        alpha_beta_values = [2, 3, 6, 10]
        for i, ab_value in enumerate(alpha_beta_values):
            item = QTableWidgetItem(str(ab_value))
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item.setFlags(Qt.ItemFlag.ItemIsEnabled)  # Nicht editierbar
            self.results_table.setItem(i, 0, item)
        
        # Spaltenbreiten anpassen
        header = self.results_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.results_table.setColumnWidth(0, 80)
        
        # Tabellenhöhe anpassen (kompakter)
        self.results_table.setMaximumHeight(180)
        
        calc_layout.addWidget(self.results_table)
        
        # Event-Handler für automatische Berechnung
        self.fractions_spinbox.valueChanged.connect(self.calculate_results)
        self.dose_spinbox.valueChanged.connect(self.calculate_results)
        
        # Event-Handler für Select-All beim Klick
        self.fractions_spinbox.lineEdit().mousePressEvent = self.create_select_all_handler(self.fractions_spinbox.lineEdit())
        self.dose_spinbox.lineEdit().mousePressEvent = self.create_select_all_handler(self.dose_spinbox.lineEdit())
        
        parent_layout.addWidget(calc_group)
        
        # Initiale Berechnung
        self.calculate_results()
    
    def create_select_all_handler(self, line_edit):
        """Erstellt einen Event-Handler der den gesamten Text beim Klick auswählt"""
        original_mouse_press = line_edit.mousePressEvent
        
        def select_all_mouse_press(event):
            # Führe das normale mousePressEvent aus
            original_mouse_press(event)
            # Wähle den gesamten Text aus
            line_edit.selectAll()
        
        return select_all_mouse_press
    
    def calculate_bed(self, n, d, alpha_beta):
        """Berechnet BED: BED = n × d × (1 + d/(α/β))"""
        return n * d * (1 + d / alpha_beta)
    
    def calculate_eqd2(self, bed, alpha_beta):
        """Berechnet EQD2: EQD2 = BED / (1 + 2/(α/β))"""
        return bed / (1 + 2 / alpha_beta)
    
    def calculate_results(self):
        """Berechnet und aktualisiert die Ergebnistabelle"""
        try:
            n = self.fractions_spinbox.value()
            d = self.dose_spinbox.value()
            
            alpha_beta_values = [2, 3, 6, 10]
            
            for i, ab_value in enumerate(alpha_beta_values):
                # BED berechnen
                bed = self.calculate_bed(n, d, ab_value)
                
                # EQD2 berechnen
                eqd2 = self.calculate_eqd2(bed, ab_value)
                
                # Ergebnisse in Tabelle eintragen
                eqd2_item = QTableWidgetItem(f"{eqd2:.2f}")
                eqd2_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                eqd2_item.setFlags(Qt.ItemFlag.ItemIsEnabled)
                
                bed_item = QTableWidgetItem(f"{bed:.2f}")
                bed_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                bed_item.setFlags(Qt.ItemFlag.ItemIsEnabled)
                
                self.results_table.setItem(i, 1, eqd2_item)
                self.results_table.setItem(i, 2, bed_item)
                
        except Exception as e:
            logging.error(f"Fehler bei der Berechnung: {e}")