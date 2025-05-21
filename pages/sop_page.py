from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTextEdit, QLabel, QHBoxLayout, QFrame, QScrollArea, QTextBrowser
from PyQt6.QtCore import Qt, QUrl, QSize
from PyQt6.QtGui import QFont, QPalette, QColor, QPixmap, QIcon, QDesktopServices
import os
import logging # Import logging module

class ExpandableSection(QWidget):
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.expanded = False
        self.title = title
        self.content_text = ""
        # Logging added within ExpandableSection
        logging.debug(f"Creating ExpandableSection: {title}")
        
        # Create layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        # Create button for header
        self.toggle_button = QPushButton(title)
        self.toggle_button.setFont(QFont('Arial', 12, QFont.Weight.Bold))
        self.toggle_button.setStyleSheet("""
            QPushButton {
                background-color: #1c5a9e;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px;
                text-align: left;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2a69ad;
            }
        """)
        self.toggle_button.setIcon(QIcon.fromTheme("go-down"))
        self.toggle_button.clicked.connect(self.toggle_expand)
        
        # Create content area using QTextBrowser
        self.content = QTextBrowser()
        self.content.setFont(QFont('Arial', 11))
        self.content.setStyleSheet("""
            QTextBrowser {
                background-color: #2a3b4c;
                color: white;
                border: none;
                border-radius: 0px 0px 5px 5px;
                padding: 10px;
            }
        """)
        self.content.setVisible(False)
        self.content.setFixedHeight(0)
        self.content.setOpenExternalLinks(True)
        
        # Add widgets to layout
        self.layout.addWidget(self.toggle_button)
        self.layout.addWidget(self.content)
        
    def set_content(self, text):
        # Limit logged content length
        log_content = (text[:100] + '...') if len(text) > 100 else text
        logging.debug(f"Setting content for '{self.title}': {log_content}")
        self.content_text = text
        self.content.setHtml(text)
        # If the section is already expanded when content changes, update its height
        if self.expanded:
            self.content.document().adjustSize() # Ensure document size is updated
            doc_height = self.content.document().size().height()
            required_height = int(doc_height) + 20 # Changed margin to 20
            self.content.setFixedHeight(required_height)

    def toggle_expand(self):
        logging.debug(f"Toggling expand for section '{self.title}'. New state: {not self.expanded}")
        self.expanded = not self.expanded

        if self.expanded:
            self.content.setVisible(True)
            # Ensure document size is calculated correctly after setting HTML
            self.content.document().adjustSize()
            # Calculate required height based on document size
            doc_height = self.content.document().size().height()
            # Add a margin/padding of 20 pixels
            required_height = int(doc_height) + 20 # Changed margin to 20
            self.content.setFixedHeight(required_height) # Set dynamic height
            self.toggle_button.setIcon(QIcon.fromTheme("go-up"))
            # Optional: ensure the parent scroll area updates if necessary
            # QTimer.singleShot(0, self.parentWidget().updateGeometry) # May not be needed
        else:
            self.content.setFixedHeight(0) # Collapse
            # It's better to hide after setting height to 0 to avoid brief flicker
            self.content.setVisible(False)
            self.toggle_button.setIcon(QIcon.fromTheme("go-down"))

class SOPPage(QWidget):
    def __init__(self, main_window, tumor_type):
        super().__init__()
        logging.info(f"Initializing SOPPage for tumor: {tumor_type}...")
        self.main_window = main_window
        self.tumor_type = tumor_type
        
        # Initialize ALL potential section variables to None
        self.indikation_section = None
        self.kriterien_section = None
        self.staging_section = None
        self.aufklaerung_section = None # Meningeoma specific
        self.ablauf_plan_section = None # Meningeoma specific
        self.lagerung_section = None    # Meningeoma specific
        self.rt_indikation_section = None # AA/GBM specific / Standard
        self.planungs_ct_section = None   # AA/GBM specific / Standard
        self.zielvolumen_section = None
        self.oar_section = None
        self.dosierung_section = None
        self.planung_section = None
        self.akzeptanz_section = None
        self.applikation_section = None
        self.nachsorge_section = None
        
        self.setup_ui()
        self.load_section_content() # Load content after UI setup
        
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(10, 0, 40, 40)
        self.setLayout(layout)
        
        # Add title
        title_label = QLabel(f"SOP: {self.tumor_type}")
        title_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title_label.setStyleSheet("color: white;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        layout.addSpacing(20)
        
        # Create a scroll area for expandable sections
        scroll_area = QScrollArea()
        scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: #1e2c39;
                border: none;
                border-radius: 10px;
            }
        """)
        scroll_area.setWidgetResizable(True)
        
        # Create a widget to hold all expandable sections
        scroll_content = QWidget()
        scroll_content.setStyleSheet("background-color: #1e2c39;")
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(10)
        scroll_layout.setContentsMargins(20, 20, 20, 20)
        
        # Add common expandable sections (present for all tumors)
        self.indikation_section = ExpandableSection("Rechtfertigende Indikation")
        self.kriterien_section = ExpandableSection("Einschlusskriterien und Ausschlusskriterien")
        scroll_layout.addWidget(self.indikation_section)
        scroll_layout.addWidget(self.kriterien_section)
        
        # Add tumor-specific expandable sections only for Meningeoma
        if self.tumor_type == "Meningeoma":
            logging.debug("Loading Meningeoma specific sections.")
            self.staging_section = ExpandableSection("Staging")
            self.aufklaerung_section = ExpandableSection("Aufklärung")
            self.ablauf_plan_section = ExpandableSection("Ablauf Radiotherapie Planung")
            self.lagerung_section = ExpandableSection("Lagerung im Bestrahlungsplanungs CT")
            self.zielvolumen_section = ExpandableSection("Zielvolumen Definition")
            self.oar_section = ExpandableSection("OAR Definition")
            self.dosierung_section = ExpandableSection("Dosierung und Fraktionierung")
            self.planung_section = ExpandableSection("Bestrahlungsplanung")
            self.akzeptanz_section = ExpandableSection("Planakzeptanzkriterien")
            self.applikation_section = ExpandableSection("Bestrahlungsapplikation")
            self.nachsorge_section = ExpandableSection("Nachsorge")
            
            # Add Meningeoma-specific sections to layout
            scroll_layout.addWidget(self.staging_section)
            scroll_layout.addWidget(self.aufklaerung_section)
            scroll_layout.addWidget(self.ablauf_plan_section)
            scroll_layout.addWidget(self.lagerung_section)
            scroll_layout.addWidget(self.zielvolumen_section)
            scroll_layout.addWidget(self.oar_section)
            scroll_layout.addWidget(self.dosierung_section)
            scroll_layout.addWidget(self.planung_section)
            scroll_layout.addWidget(self.akzeptanz_section)
            scroll_layout.addWidget(self.applikation_section)
            scroll_layout.addWidget(self.nachsorge_section)
        
        # Add tumor-specific expandable sections for Anaplastic astrocytoma
        elif self.tumor_type == "Anaplastic astrocytoma":
            logging.debug("Loading Anaplastic Astrocytoma specific sections.")
            self.staging_section = ExpandableSection("Staging")
            self.rt_indikation_section = ExpandableSection("Indikationen für die adjuvante Radiotherapie")
            self.planungs_ct_section = ExpandableSection("Planungs-CT bei perkutaner Bestrahlung")
            self.zielvolumen_section = ExpandableSection("Zielvolumen Definition")
            self.oar_section = ExpandableSection("OAR Definition")
            self.dosierung_section = ExpandableSection("Dosierung und Fraktionierung")
            self.planung_section = ExpandableSection("Bestrahlungsplanung")
            self.akzeptanz_section = ExpandableSection("Planakzeptanzkriterien")
            self.applikation_section = ExpandableSection("Bestrahlungsapplikation")
            self.nachsorge_section = ExpandableSection("Nachsorge")
            
            # Add Anaplastic astrocytoma-specific sections to layout
            scroll_layout.addWidget(self.staging_section)
            scroll_layout.addWidget(self.rt_indikation_section)
            scroll_layout.addWidget(self.planungs_ct_section)
            scroll_layout.addWidget(self.zielvolumen_section)
            scroll_layout.addWidget(self.oar_section)
            scroll_layout.addWidget(self.dosierung_section)
            scroll_layout.addWidget(self.planung_section)
            scroll_layout.addWidget(self.akzeptanz_section)
            scroll_layout.addWidget(self.applikation_section)
            scroll_layout.addWidget(self.nachsorge_section)
        
        # Add tumor-specific expandable sections for Glioblastoma
        elif self.tumor_type == "Glioblastoma":
            logging.debug("Loading Glioblastoma specific sections.")
            self.staging_section = ExpandableSection("Staging")
            self.rt_indikation_section = ExpandableSection("Indikationen für die adjuvante Radiotherapie")
            self.planungs_ct_section = ExpandableSection("Planungs-CT bei perkutaner Bestrahlung")
            self.zielvolumen_section = ExpandableSection("Zielvolumen Definition")
            self.oar_section = ExpandableSection("OAR Definition")
            self.dosierung_section = ExpandableSection("Dosierung und Fraktionierung")
            self.planung_section = ExpandableSection("Bestrahlungsplanung")
            self.akzeptanz_section = ExpandableSection("Planakzeptanzkriterien")
            self.applikation_section = ExpandableSection("Bestrahlungsapplikation")
            self.nachsorge_section = ExpandableSection("Nachsorge")
            
            # Add Glioblastoma-specific sections to layout
            scroll_layout.addWidget(self.staging_section)
            scroll_layout.addWidget(self.rt_indikation_section)
            scroll_layout.addWidget(self.planungs_ct_section)
            scroll_layout.addWidget(self.zielvolumen_section)
            scroll_layout.addWidget(self.oar_section)
            scroll_layout.addWidget(self.dosierung_section)
            scroll_layout.addWidget(self.planung_section)
            scroll_layout.addWidget(self.akzeptanz_section)
            scroll_layout.addWidget(self.applikation_section)
            scroll_layout.addWidget(self.nachsorge_section)
        
        else:
            # Create the standard sections
            logging.debug(f"Loading standard sections for tumor: {self.tumor_type}.")
            self.staging_section = ExpandableSection("Staging")
            self.rt_indikation_section = ExpandableSection("Indikationen für die adjuvante Radiotherapie")
            self.planungs_ct_section = ExpandableSection("Planungs-CT bei perkutaner Bestrahlung")
            self.zielvolumen_section = ExpandableSection("Zielvolumen Definition")
            self.oar_section = ExpandableSection("OAR Definition")
            self.dosierung_section = ExpandableSection("Dosierung und Fraktionierung")
            self.planung_section = ExpandableSection("Bestrahlungsplanung")
            self.akzeptanz_section = ExpandableSection("Planakzeptanzkriterien")
            self.applikation_section = ExpandableSection("Bestrahlungsapplikation")
            self.nachsorge_section = ExpandableSection("Nachsorge")
            
            # Add standard sections to layout (after common ones)
            scroll_layout.addWidget(self.staging_section)
            scroll_layout.addWidget(self.rt_indikation_section)
            scroll_layout.addWidget(self.planungs_ct_section)
            scroll_layout.addWidget(self.zielvolumen_section)
            scroll_layout.addWidget(self.oar_section)
            scroll_layout.addWidget(self.dosierung_section)
            scroll_layout.addWidget(self.planung_section)
            scroll_layout.addWidget(self.akzeptanz_section)
            scroll_layout.addWidget(self.applikation_section)
            scroll_layout.addWidget(self.nachsorge_section)
        
        scroll_layout.addStretch()
        
        # Set the scroll content
        scroll_area.setWidget(scroll_content)
        
        layout.addWidget(scroll_area)
        
    def load_section_content(self):
        # Placeholder content - will be replaced with actual content
        logging.info(f"Loading SOP content for tumor: {self.tumor_type}")
        
        # --- Common Sections Content ---
        
        if self.indikation_section:
            # ... existing code ...
            pass
        if self.kriterien_section:
            # ... existing code ...
            pass
        
        if self.tumor_type == "Meningeoma":
            logging.debug("Loading Meningeoma specific sections.")
            if self.staging_section:
                self.staging_section.set_content("<p>Die Indikationsstellung zur Strahlentherapie von WHO Grad I, II und III Meningeomen erfolgt gemäss den Empfehlungen der Leitlinien Neuroonkologie des Klinischen Neurozentrums USZ.</p>")
            if self.aufklaerung_section:
                self.aufklaerung_section.set_content("<p>Standardisierter Aufklärungsbogen</p>")
            if self.ablauf_plan_section:
                self.ablauf_plan_section.set_content("<p>- Planungs-CT mit Kontrastmittel<br>- Planungs-cMRI gemäss Stereotaxie-Protokoll (T1 +/- KM) nicht älter als 5 Tage</p>")
            if self.lagerung_section:
                self.lagerung_section.set_content("<p>- Stereotaktische Maske</p>")
            if self.zielvolumen_section:
                self.zielvolumen_section.set_content("""
                    <p><b>Grad I Meningeom</b>:</p>
                    <ul>
                        <li>GTV = Tumor (wenn keine Operation) oder T1-KM Veränderungen + OP-Höhle (wenn operiert)</li>
                        <li>CTV= GTV + 0 mm</li>
                        <li>PTV = CTV + 3 mm</li>
                    </ul>
                    <p><b>Grad II Meningeom</b>:</p>
                    <ul>
                        <li>GTV = T1-KM Veränderungen + OP-Höhle</li>
                        <li>CTV= GTV + 7mm</li>
                        <li>PTV = CTV + 3 mm</li>
                    </ul>
                    <p><b>Grad III Meningeom</b>:</p>
                    <ul>
                        <li>GTV = T1-KM Veränderungen + OP-Höhle</li>
                        <li>CTV= GTV + 10 mm</li>
                        <li>PTV = CTV + 3 mm</li>
                    </ul>
                """)
            if self.oar_section:
                self.oar_section.set_content("""
                    <ul>
                        <li>Brain, Brain-Brainstem, Brain-GTV</li>
                        <li>Brainstem</li>
                        <li>Optic_nerve_L, Optic_nerve_R</li>
                        <li>Chiasm</li>
                        <li>LacrimGland_L</li>
                        <li>LacrimGland_R</li>
                        <li>Hippocampus_L</li>
                        <li>Hippocampus_R</li>
                    </ul>
                """)
            if self.dosierung_section:
                self.dosierung_section.set_content("""
                    <p><b>Grad I Meningeom:</b></p>
                    <ul>
                        <li>30 Fraktionen</li>
                        <li>1.8 Gy Einzeldosis</li>
                        <li>54 Gy Gesamtdosis</li>
                    </ul>
                    <p><b>Grad II Meningeom:</b></p>
                    <ul>
                        <li>30 Fraktionen</li>
                        <li>1.8 Gy-2Gy Einzeldosis</li>
                        <li>54 -60Gy Gesamtdosis</li>
                    </ul>
                    <p><b>Grad III Meningeom:</b></p>
                    <ul>
                        <li>30 Fraktionen</li>
                        <li>2.0 Gy Einzeldosis</li>
                        <li>60 Gy Gesamtdosis</li>
                    </ul>
                """)
            if self.planung_section:
                self.planung_section.set_content("""
                    <p><b>Bestrahlungsplanung:</b></p>
                    <ul>
                        <li>Auf Planungs CT</li>
                        <li>Triple AAA oder Accuros Algorithmus</li>
                        <li>RapidArc</li>
                        <li>6MV mit normaler Dosisrate</li>
                    </ul>
                """)
            if self.akzeptanz_section:
                self.akzeptanz_section.set_content("""
                    <ul>
                        <li>Entsprechend Planungskonzept</li>
                    </ul>
                """)
            if self.applikation_section:
                self.applikation_section.set_content("""
                    <ul>
                        <li>Tägliche Bildgebung mittels ExacTrac</li>
                        <li>CBCT Tag 1 und dann 1x/Woche</li>
                    </ul>
                """)
            if self.nachsorge_section:
                self.nachsorge_section.set_content("""
                    <ul>
                        <li>Erste klinische Nachsorge nach 4 Wochen mit cMRI für Grad II und III Tumoren</li>
                        <li>Anschliessend klinische Nachsorge mit cMRI im 3-6 Monatsintervall über Neurochirurgie und Radio-Onkologie (eventuell alternierend)</li>
                    </ul>
                """)
        
        # --- Anaplastic Astrocytoma Specific Sections Content ---
        elif self.tumor_type == "Anaplastic astrocytoma":
            logging.debug("Loading Anaplastic Astrocytoma specific sections.")
            if self.staging_section:
                self.staging_section.set_content("<p>Die <a href=\"https://www.sciencedirect.com/science/article/abs/pii/S0140673617314423?via%%3Dihub\" style=\"color: #3292ea; text-decoration: none;\"><b>EORTC Studie 26053-22054</b></a> zeigte, dass die Strahlentherapie gefolgt von einer adjuvanten Temozolomid-Chemotherapie mit einem signifikanten Überlebensvorteil bei Patienten mit neu diagnostizierten nicht-ko-deletierten anaplastischen Gliomen assoziiert ist. Somit ist die alleinige postoperative Strahlentherapie mit kumulativ 60 Gy gefolgt von 12 Zyklen Temodal gemäss <a href=\"https://www.nccn.org/guidelines/guidelines-detail?category=1&id=1425\" style=\"color: #3292ea; text-decoration: none;\"><b>NCCN</b></a> und ESMO Leitlinie als Standard anzusehen</p>")
            if self.kriterien_section:
                self.kriterien_section.set_content("<p><b>Einschlusskriterien:</b></p><ul><li>Histologisch gesicherte Gliome gemäss WHO Klassifikation 2016</li><li>Fall wurde am interdisziplinären Neuro-Onkologie Tumorboard diskutiert</li><li>Karnofsky Performance Status (KPS) &gt;= 60%; bei Tumor-bedingter KPS Einschränkung auch &gt; 40%</li></ul><p><b>Ausschlusskriterien:</b></p><ul><li>KPS 40% oder weniger</li></ul>")
            if self.rt_indikation_section:
                self.rt_indikation_section.set_content("<ul><li>Generell bei allen Patienten mit ein KPS &gt;=60%</li><li>Radiotherapie gefolgt von adjuvante Temodal Chemotherapie</li></ul><p><a href=\"https://www.sciencedirect.com/science/article/abs/pii/S0140673617314423?via%%3Dihub\" style=\"color: #3292ea; text-decoration: none;\"><b>[Van den Bent et al, Lancet, 2017]</b></a></p>")
            if self.planungs_ct_section:
                self.planungs_ct_section.set_content("<ul><li>Rückenlage, Arme unten/seitlich</li><li>3-Punktmaske</li><li>Kontrastmittelgabe bei fehlende Kontraindikation</li><li>Planungs-MRI gemäss Gliom-Protokoll (T1 +/-KM; T2 FLAIR) nicht älter als 7 Tage, FET-PET</li></ul>")
            if self.zielvolumen_section:
                self.zielvolumen_section.set_content("<ul><li>GTV = Post-operative Tumorhöhle und FLAIR</li><li>CTV = GTV + 15 mm</li><li>PTV = CTV + 3 mm</li></ul><p><a href=\"https://www.sciencedirect.com/science/article/abs/pii/S0140673617314423?via%%3Dihub\" style=\"color: #3292ea; text-decoration: none;\"><b>[Van den Bent et al, Lancet, 2017]</b></a></p>")
            if self.oar_section:
                self.oar_section.set_content("<ul><li>Brain (ohne Brainstem)</li><li>Brain - PTV</li><li>Eye R, Eye L</li><li>Lens R, Lens L</li><li>Lacrimal Gland R, Lacrimal Gland L</li><li>Optic nerve R, Optic nerve L</li><li>Optic nerve R PRV (+ 3 mm margin), Optic nerve L PRV  (+ 3 mm margin)</li><li>Optic chiasm PRV  (+ 3 mm margin)</li><li>Brainstem</li><li>Spinal Cord</li></ul>")
            if self.dosierung_section:
                self.dosierung_section.set_content("""
                    <p><b>Dosierung und Fraktionierung für Glioblastoma</b></p>
                    <ul>
                        <li>Standard 30 x 2Gy = 60Gy, täglich 5x/Woche 
                            <a href="https://www.sciencedirect.com/science/article/abs/pii/S1470204509700257?via%3Dihub" style="color: #3292ea; text-decoration: none; font-weight: bold;">(Stupp et al, Lancet Oncology, 2009)</a>
                        </li>
                        <li>Elderly oder reduzierte KPS - hypofraktioniert mit 15 x 2.67 Gy = 40.05 Gy, täglich 5x/Woche 
                            <a href="https://www.nejm.org/doi/10.1056/NEJMoa1611977?url_ver=Z39.88-2003&rfr_id=ori%3Arid%3Acrossref.org&rfr_dat=cr_pub%3Dwww.ncbi.nlm.nih.gov" style="color: #3292ea; text-decoration: none; font-weight: bold;">(Perry et al, NEJM, 2017)</a>
                        </li>
                    </ul>
                    <p><b>Chemotherapie:</b></p>
                    <ul>
                        <li>Konkomitant Temodal Chemotherapie 75mg/m² täglich wird in der Klinik für Radio-Onkologie rezeptiert; die adjuvante Temodal Chemotherapie wird in der Klinik für Neurologie stattfinden.</li>
                        <li>Keine Routine PCP Prophylaxe mit Bactrim – nur in immunsupprimierte Patienten oder bei Patienten mit Lymphozyten < 0.5 G/l.</li>
                    </ul>
                """)
            if self.planung_section:
                self.planung_section.set_content("<ul><li>Auf Planungs CT</li><li>6MV mit normaler Dosisrate</li><li>AAA oder Accuros Algorithmus</li><li>RapidArc</li></ul>")
            if self.akzeptanz_section:
                self.akzeptanz_section.set_content("<ul><li>Entsprechend Planungskonzept</li></ul>")
            if self.applikation_section:
                self.applikation_section.set_content("<ul><li>Kontrollbildgebung gemässIGRT-Protokoll</li><li>Offline review durch zuständigen Assistenzarzt/Kaderarzt</li></ul><p><a href=\"file://fs-group/RAO_Daten/RAO_QM/Handbuch/06.%%20Patientenbezogener%%20Behandlungsprozess/6.4.%%20Durchf%%C3%%BChrung%%20Bestrahlung/6-4-10%%20Linac/IGRT\" style=\"color: #3292ea; text-decoration: none;\"><b>[Imaging Protokoll: Bildgestützte Lokalisation]</b></a></p>")
            if self.nachsorge_section:
                self.nachsorge_section.set_content("<ul><li>Nach 4 Wochen: MRI Gehirn und Termin in der Klinik für Neurologie</li><li>Radio-Onkologische Kontrolle nur in speziellen Situationen</li><li>Brief an Zuweiser, Hausarzt und alle involvierte Ärzte</li></ul>")
        
        # --- Glioblastoma Specific Sections Content ---
        elif self.tumor_type == "Glioblastoma":
            logging.debug("Loading Glioblastoma specific sections.")
            if self.staging_section:
                self.staging_section.set_content("<p><b>Kombinierte Radiochemotherapie:</b></p>" \
                                                 "<p>Die Zugabe von Temozolomid zu einer normo-fraktionierten Strahlentherapie bei neu diagnostiziertem Glioblastom führte zu einem klinisch bedeutsamen und statistisch signifikanten Überlebensvorteil bei einer Hazard Ratio von 0.63 mit minimaler zusätzlicher Toxizität. Somit ist die postoperative Radiochemotherapie, gefolgt von einer adjuvanten Temodaltherapie, gemäss <a href=\"https://www.nccn.org/guidelines/guidelines-detail?category=1&id=1425\" style=\"color: #3292ea; text-decoration: none;\"><b>NCCN</b></a> und ESMO Leitlinie die Standard-Behandlung.</p>" \
                                                 "<p><a href=\"https://www.nejm.org/doi/full/10.1056/NEJMoa043330\" style=\"color: #3292ea; text-decoration: none;\"><b>(Stupp et al. New England Journal of Medicine 2005)</b></a></p>" \
                                                 "<br><p><b>Radiochemotherapie bei elderly Patienten:</b></p>" \
                                                 "<p>Die Zugabe von Temozolomid zu einer hypo-fraktionierten Strahlentherapie bei neu diagnostiziertem Glioblastom von Patienten älter als 65 Jahren führte zu einem klinisch bedeutsamen und statistisch signifikanten Überlebensvorteil bei einer Hazard Ratio von 0.67 mit minimaler zusätzlicher Toxizität. Somit ist die hypo-fraktionierte Radiochemotherapie, gefolgt von einer adjuvanten Temodaltherapie, insbesondere bei Patienten mit MGMTMethylierung und gutem Performance-Status als Therapie der Wahl anzusehen.</p>" \
                                                 "<p><a href=\"https://www.nejm.org/doi/10.1056/NEJMoa1611977?url_ver=Z39.88-2003&rfr_id=ori%%3Arid%%3Acrossref.org&rfr_dat=cr_pub%%3Dwww.ncbi.nlm.nih.gov\" style=\"color: #3292ea; text-decoration: none;\"><b>(Perry et al. New England Journal of Medicine 2017)</b></a></p>" \
                                                 "<br><p><b>TMZ oder RT bei elderly Patienten:</b></p>" \
                                                 "<p>Basierend auf dem systematischen Review von Zarnett et al., ist die alleinige hypofraktionierte Strahlentherapie eine Standard-Behandlung von älteren Patienten mit neu diagnostiziertem GBM, bei welchen eine Kombinationstherapie aus hypo-fraktionierter Strahlentherapie und Temodal nicht möglich ist.</p>" \
                                                 "<p><a href=\"https://jamanetwork.com/journals/jamaneurology/fullarticle/2212144\" style=\"color: #3292ea; text-decoration: none;\"><b>(Zarnett et al. JAMA Neurol. 2015)</b></a></p>")
            if self.kriterien_section:
                self.kriterien_section.set_content("<p><b>Einschlusskriterien:</b></p><ul><li>Histologisch gesicherte Gliome gemäss WHO Klassifikation 2016</li><li>Fall wurde am interdisziplinären Neuro-Onkologie Tumorboard diskutiert</li><li>Karnofsky Performance Status (KPS) &gt;= 60%; bei Tumor-bedingter KPS Einschränkung auch &gt; 40%</li></ul><p><b>Ausschlusskriterien:</b></p><ul><li>KPS 40% oder weniger</li></ul>")
            if self.rt_indikation_section:
                self.rt_indikation_section.set_content("<p><b>Glioblastom</b></p><ul>" \
                                                      "<li>Generell bei allen Patienten mit ein KPS &gt;=60% und &lt;= 70j.</li>" \
                                                      "<li>Standard RT und konkomitant und adjuvant Temodal</li>" \
                                                      "<li>Bei Patienten &lt;=70j. und KPS &lt; 70%: Hypofraktionierte RT +/- Temodal je nach MGMT Status</li>" \
                                                      "<li>Bei Patienten &gt; 70j, Behandlung abhängig vom MGMT Methyleriungsstatus und KPS<ul>" \
                                                          "<li>MGMT methyliert und KPS &gt;=70%: hypofraktionierte RT und konkomitant und adjuvant Temodal</li>" \
                                                          "<li>MGMT methyliert und KPS &lt; 70%: Temodal mono</li>" \
                                                          "<li>MGMT nicht methyliert und KPS &gt;=70%: hypofraktionierte RT und eventuell konkomitant und adjuvant Temodal</li>" \
                                                          "<li>MGMT nicht methyliert und KPS &lt;70%: alleinige hypofraktionierte RT</li></ul></li>" \
                                                      "<li>Bei KPS &lt;=40% - Best Supportive Care diskutieren und Palliative Care Konsultation organisieren</li>" \
                                                      "<li>Die Möglichkeit für die Teilnahme in eine klinische Studie sollte bei allen Patienten diskutiert sein</li></ul>" \
                                                      "<p><a href=\"https://www.nejm.org/doi/full/10.1056/NEJMoa043330\" style=\"color: #3292ea; text-decoration: none;\"><b>[Stupp et al, NEJM, 2005]</b></a><br>" \
                                                      "<a href=\"https://www.sciencedirect.com/science/article/abs/pii/S1470204509700257?via%%3Dihub\" style=\"color: #3292ea; text-decoration: none;\"><b>[Stupp et al, Lancet Oncology, 2009]</b></a><br>" \
                                                      "<a href=\"https://www.nejm.org/doi/10.1056/NEJMoa1611977?url_ver=Z39.88-2003&rfr_id=ori%%3Arid%%3Acrossref.org&rfr_dat=cr_pub%%3Dwww.ncbi.nlm.nih.gov\" style=\"color: #3292ea; text-decoration: none;\"><b>[Perry et al, NEJM, 2017]</b></a><br>" \
                                                      "<a href=\"https://ascopubs.org/doi/abs/10.1200/JCO.2004.06.082?rfr_dat=cr_pub%%3Dpubmed&url_ver=Z39.88-2003&rfr_id=ori%%3Arid%%3Acrossref.org\" style=\"color: #3292ea; text-decoration: none;\"><b>[Roa et al, JCO, 2004]</b></a></p>")                                              
            if self.planungs_ct_section:
                self.planungs_ct_section.set_content("<ul><li>Rückenlage, Arme unten/seitlich</li><li>3-Punktmaske</li><li>Kontrastmittelgabe bei fehlende Kontraindikation</li><li>Planungs-MRI gemäss Gliom-Protokoll (T1 +/-KM; T2 FLAIR) nicht älter als 7 Tage, FET-PET</li></ul>")
            if self.zielvolumen_section:
                self.zielvolumen_section.set_content("""
                    <p><b>Glioblastom</b></p>
                    <ul>
                        <li>GTV = post-operative Tumorhöhle in T1Gad; bei sekundär Glioblastom -> non-enhancing Tumor einschliessen in FLAIR Sequenzen</li>
                        <li>CTV = GTV + 1.5cm begrenzend auf anatomische Strukturen; bei sekundär Glioblastom kann man ein reduzierte CTV margin an der FLAIR Veränderungen benutzen (0.5-0.7cm)</li>
                        <li>PTV = CTV + 0.3cm</li>
                        <li>Bei sehr grossen Zielvolumina (PTV >> 400cc ist ein Boost ab 46Gy mit reduzierten Sicherheitsäumen möglich) RTOG</li>
                    </ul>
                    <p><a href="https://www.sciencedirect.com/science/article/abs/pii/S0167814015006611?via%3Dihub" style="color: #3292ea; text-decoration: none;\"><b>[ESTRO/ACROP guideline \'target volume definition of glioblastomas\']</b></a></p>
                """)
            if self.oar_section:
                self.oar_section.set_content("<p>OAR Definition für Glioblastoma</p>")
            if self.dosierung_section:
                self.dosierung_section.set_content("""
                    <p><b>Dosierung und Fraktionierung für Glioblastoma</b></p>
                    <ul>
                        <li>Standard 30 x 2Gy = 60Gy, täglich 5x/Woche 
                            <a href="https://www.sciencedirect.com/science/article/abs/pii/S1470204509700257?via%3Dihub" style="color: #3292ea; text-decoration: none; font-weight: bold;">(Stupp et al, Lancet Oncology, 2009)</a>
                        </li>
                        <li>Elderly oder reduzierte KPS - hypofraktioniert mit 15 x 2.67 Gy = 40.05 Gy, täglich 5x/Woche 
                            <a href="https://www.nejm.org/doi/10.1056/NEJMoa1611977?url_ver=Z39.88-2003&rfr_id=ori%3Arid%3Acrossref.org&rfr_dat=cr_pub%3Dwww.ncbi.nlm.nih.gov" style="color: #3292ea; text-decoration: none; font-weight: bold;">(Perry et al, NEJM, 2017)</a>
                        </li>
                    </ul>
                    <p><b>Chemotherapie:</b></p>
                    <ul>
                        <li>Konkomitant Temodal Chemotherapie 75mg/m² täglich wird in der Klinik für Radio-Onkologie rezeptiert; die adjuvante Temodal Chemotherapie wird in der Klinik für Neurologie stattfinden.</li>
                        <li>Keine Routine PCP Prophylaxe mit Bactrim – nur in immunsupprimierte Patienten oder bei Patienten mit Lymphozyten < 0.5 G/l.</li>
                    </ul>
                """)
            if self.planung_section:
                self.planung_section.set_content("""
                    <p><b>Bestrahlungsplanung für Glioblastoma</b></p>
                    <ul>
                        <li>Auf Planungs CT</li>
                        <li>6MV mit normaler Dosisrate</li>
                        <li>AAA oder Accuros Algorithmus</li>
                        <li>RapidArc</li>
                    </ul>
                """)
            if self.akzeptanz_section:
                self.akzeptanz_section.set_content("""
                    <p><b>Planakzeptanzkriterien für Glioblastoma</b></p>
                    <ul>
                        <li>Entsprechend Planungskonzept</li>
                    </ul>
                """)
            if self.applikation_section:
                self.applikation_section.set_content("""
                    <p><b>Bestrahlungsapplikation für Glioblastoma</b></p>
                    <ul>
                        <li>Kontrollbildgebung gemäss IGRT-Protokoll</li>
                        <li>Offline review durch zuständigen Assistenzarzt/Kaderarzt</li>
                    </ul>
                """)
            if self.nachsorge_section:
                self.nachsorge_section.set_content("""
                    <p><b>Nachsorge für Glioblastoma</b></p>
                    <ul>
                        <li>Nach 4 Wochen: MRI Gehirn und Termin in der Klinik für Neurologie</li>
                        <li>Radio-Onkologische Kontrolle nur in speziellen Situationen</li>
                        <li>Brief an Zuweiser, Hausarzt und alle involvierte Ärzte</li>
                    </ul>
                """)
        
        elif self.tumor_type == "Brain Metastasis - Primary RT":
            # Specific content for Primary RT Brain Metastasis
            # Rechtfertigende Indikation
            if self.indikation_section: 
                self.indikation_section.set_content("""
                    <p><a href="https://ascopubs.org/doi/full/10.1200/jco.2010.30.1655" style="color: #3292ea; text-decoration: none; font-weight: bold;">Die EORTC 22952-26001 Studie</a>, welche die Wertigkeit einer alleinigen
                    Radiochirurgie ohne Ganzhirnbestrahlung zur Behandlung einer limitierten
                    Hirnmetastasierung untersuchte, ergab ein gleichwertiges Gesamtüberleben bei
                    sehr guter lokaler Kontrolle der therapierten Metastasen (Kocher et al., JCO, 2011).</p>
                    <p>Daher ist die Radiochirurgie bei limitierter Hirnmetastasierung als Standardtherapie
                    anzusehen.</p>
                    <p>Die Radiochirurgie ist daher auch bei multiplen Hirnmetastasen (n&lt;10) als Standard
                    einer Ganzhirnbestrahlung vorzuziehen. Bei mehr als 10 Hirnmetastasen kann die
                    Radiochirurgie bei guter technischer Durchführbarkeit ebenfalls in Erwägung
                    gezogen werden, um die neurokognitiven Folgen einer Ganzhirnbestrahlung zu
                    vermeiden. <a href="https://www.thelancet.com/journals/lanonc/article/PIIS1470-2045(14)70061-0/abstract" style="color: #3292ea; text-decoration: none; font-weight: bold;">(Yamamoto et al., Lancet Oncology, 2014)</a></p>
                """)
            # Set specific content for Einschlusskriterien
            if self.kriterien_section: 
                self.kriterien_section.set_content("""
                    <p><b>1-4 Hirnmetastasen</b></p>
                    <p>Bei Patienten mit bis zu 4 Metastasen ist die Radiochirurgie (SRS) oder fraktionierte
                    stereotaktische Radiotherapie (SRT) ohne Ganzhirnbestrahlung die bevorzugte
                    Behandlungsoption (<a href="https://ascopubs.org/doi/full/10.1200/jco.2010.30.1655" style="color: #3292ea; text-decoration: none; font-weight: bold;">Kocher et al., JCO, 2011</a>). Dies steht im Einklang mit der von der
                    ASTRO empfohlenen "Choosing wisely list", die 2014 veröffentlicht wurde. Die
                    additive Ganzhirnbestrahlung reduziert die Entwicklung neuer Hirnmetastasen, hat
                    jedoch keine Auswirkung auf das Überleben. Dies muss dem Patienten im Hinblick
                    auf die alleinige Durchführung einer Überwachungs-MRT-Bildgebung nach SRS/SRT
                    klar kommuniziert werden. Bei dieser Indikation ist es wichtig zu betonen, dass
                    qualitativ hochwertige Daten des Evidenz Grades I vorliegen, welche belegen, dass
                    SRS/SRT die bevorzugte Behandlungsoption bleiben sollte (insbesondere bei
                    asymptomatischen Patienten). Hiervon auszunehmen sind neue Daten des Evidenz
                    Grades I (z.B. für die systemische Behandlung von Tumoren mit Treibermutationen).</p>
                    
                    <p><b>5-9 Hirnmetastasen</b></p>
                    <p>Hier wurde kein in einer sehr grossen multi-institutionellen Datenbankanalyse
                    Überlebensunterschied zwischen Patienten beobachtet, die eine alleinige SRS bei bis
                    zu 4 Metastasen erhielten, verglichen mit Patienten, bei denen 5-9 Metastasen
                    diagnostiziert wurden (<a href="https://www.thelancet.com/journals/lanonc/article/PIIS1470-2045(14)70061-0/abstract" style="color: #3292ea; text-decoration: none; font-weight: bold;">Yamamoto et al., Lancet Oncology, 2014b</a>). Die SRS oder SRT
                    ist daher in unserer Klinik die bevorzugte Behandlungsoption bei 4-9 Hirnmetastasen,
                    um eine Ganzhirnbestrahlung möglichst hinauszuzögern und mögliche
                    neurokognititve Defizite zu verringern.</p>
                    <p>Aus diesem Grund wird ein vorsichtiger Ansatz gewählt, bei dem die SRS nur bei
                    Läsionen unter einem Zentimeter und die SRT nur bei größeren Läsionen
                    durchgeführt wird.</p>
                    
                    <p><b>&gt;9 Hirnmetastasen</b></p>
                    <p>In dieser Patientenkohorte gibt es keine hochgradige Evidenz, welche unsere
                    Behandlung lenken könnte. Die Ganzhirnbestrahlung wird somit nach wie vor als
                    Standardtherapie betrachtet. SRS oder SRT kann jedoch bei mehr als 9 Metastasen
                    sinnvoll sein, dies sollte mit dem Patienten individuell diskutiert werden (<b>Yamamoto et
                    al., Radiation Oncology, 2013; Yamamoto et al., Journal of Neurosurgery, 2014a</b>;
                    <a href="https://www.thelancet.com/journals/lanonc/article/PIIS1470-2045(14)70061-0/abstract" style="color: #3292ea; text-decoration: none; font-weight: bold;">Yamamoto et al., Lancet Oncology, 2014b</a>).</p>
                    <p>Abhängig von der Prognose des Patienten (geschätzt nach GPA-Klasse) kann ein
                    integrierter oder sequentieller stereotaktischer Boost zur lokalen Dosis-Eskalation in
                    Betracht gezogen werden. Da der Nachweis des Evidenz Grades I für eine DosisEskalation fehlt, bleibt dies eine individuelle Entscheidung.</p>
                    <p>Eine Ganzhirnbestrahlung mit integrierter Hippocampus-Schonung kann zum
                    aktuellen Zeitpunkt nicht empfohlen werden: in einer prospektiv-randomisierten Studie
                    wurde zwar ein kurzfristiger positiver Effekt auf die Neurokognition beobachtet
                    (<a href="https://ascopubs.org/doi/full/10.1200/JCO.19.02767" style="color: #3292ea; text-decoration: none; font-weight: bold;">Brown et al., JCO, 2020</a>), aber aufgrund von wenigen Langzeitüberlebenden in der
                    Studie und der höheren integralen Gesamthirndosis bei Hippocampus-Schonung (<a href="https://ascopubs.org/doi/full/10.1200/JCO.2014.57.2909?url_ver=Z39.88-2003&rfr_id=ori:rid:crossref.org&rfr_dat=cr_pub%20%200pubmed" style="color: #3292ea; text-decoration: none; font-weight: bold;">Gondi et al., JCO, 2014</a>) und
                    damit beobachteten MR-Veränderung (erhöhte Leukenzephalopathie-Rate;
                    <a href="https://www.ejcancer.com/article/S0959-8049(19)30817-2/fulltext" style="color: #3292ea; text-decoration: none; font-weight: bold;">Andratschke et al., JCO, 2020</a>; <a href="https://www.ejcancer.com/article/S0959-8049(19)30817-2/fulltext" style="color: #3292ea; text-decoration: none; font-weight: bold;">Mayinger et al., European Journal of Cancer, 2020</a>) ist
                    die tatsächliche Wertigkeit, insbesondere bei Langzeitüberleben, ungeklärt.</p>
                    <p>Bei Patienten mit ausgedehnter extrakranialer Erkrankung, schlechtem
                    Allgemeinstatus und eingeschränkten oder fehlenden systemischen TherapieOptionen sollte eine best-supportive-care Strategie unter früher Einbeziehung des
                    Palliative Care Temas der Klinik erfolgen.</p>
                """)
            # Set generic placeholders for other standard sections for now
            # if self.kriterien_section: self.kriterien_section.set_content(f"<p>Einschluss- und Ausschlusskriterien für {self.tumor_type}</p>") 
            # Set specific content for Staging
            if self.staging_section: 
                self.staging_section.set_content("""
                    <ul>
                        <li>Ggf. vorhergehendes extrakraniales Staging</li>
                        <li>Stereotaxie-MRI, bei Radiotherapiebeginn nicht älter als 7 Tage</li>
                    </ul>
                """)
            # Hide the adjuvant RT indication section as it's not relevant for primary RT
            if self.rt_indikation_section: 
                self.rt_indikation_section.setVisible(False)
            # Keep generic placeholders for the rest for now
            # Set specific content for Planungs-CT
            if self.planungs_ct_section: 
                self.planungs_ct_section.set_content("""
                    <ul>
                        <li>SRS/SRT Planungs-CT mit Kontrastmittel</li>
                        <li>Bei der postoperative SRS/SRT ohne Hinweis auf Resttumor im cMRI kann bei
                        Bedarf auf die KM-Gabe verzichtet werden</li>
                    </ul>
                """)
            # Keep generic placeholders for the rest for now
            # if self.planungs_ct_section: self.planungs_ct_section.set_content(f"<p>Planungs-CT bei perkutaner Bestrahlung für {self.tumor_type}</p>")
            # Set specific content for Zielvolumen
            if self.zielvolumen_section: self.zielvolumen_section.set_content("""
                <ul>
                    <li>GTV Definition in der T1-KM Sequenz (Stereotaxie-MRI)</li>
                    <li>bei nicht operierten, intakten Hirnmetastasen: GTV=CTV (CTV als Struktur
                    nicht notwendig)<br>
                    PTV Sicherheitssaum von 1mm</li>
                    <li>bei postoperativer SRS/SRT: GTV nur bei Resttumor, CTV=Resektionshöhle,<br>
                    PTV Sicherheitssaum von 2 mm</li>
                </ul>
            """)
            if self.oar_section: self.oar_section.set_content("""
                <ul>
                    <li>Brain (ohne Brainstem)</li>
                    <li>Brain - PTV</li>
                    <li>Eye R, Eye L</li>
                    <li>Lens R, Lens L</li>
                    <li>Lacrimal Gland R, Lacrimal Gland L</li>
                    <li>Optic nerve R, Optic nerve L</li>
                    <li>Optic nerve R PRV, Optic nerve L PRV</li>
                    <li>Optic chiasm</li>
                    <li>Optic chiasm PRV</li>
                    <li>Brainstem</li>
                    <li>Spinal Cord</li>
                </ul>
                <p>PRV Saum 2 mm.</p>
            """)
            if self.dosierung_section: self.dosierung_section.set_content("""
                <h4>Keine Vorbestrahlung abgesehen von SRS/SRT</h4>
                <table border="1" style="width:100%; border-collapse: collapse; border-color: white;">
                  <thead>
                    <tr>
                      <th style="padding: 5px; text-align: left; border: 1px solid white;"># der Metastasen</th>
                      <th style="padding: 5px; text-align: left; border: 1px solid white;">Grösse</th>
                      <th style="padding: 5px; text-align: left; border: 1px solid white;">Dosis</th>
                      <th style="padding: 5px; text-align: left; border: 1px solid white;">Kommentar</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td rowspan="2" style="padding: 5px; border: 1px solid white;">1-9<br>Kumulatives Volumen &lt;= 30cc</td>
                      <td style="padding: 5px; border: 1px solid white;">&lt; 2.5 cm</td>
                      <td style="padding: 5px; border: 1px solid white;">1 x 18-20Gy @80%</td>
                      <td style="padding: 5px; border: 1px solid white;">Keine zentralen, zystischen Veränderungen oder Nekrose</td>
                    </tr>
                    <tr>
                      <td style="padding: 5px; border: 1px solid white;"></td> <!-- Empty cell for Grösse -->
                      <td style="padding: 5px; border: 1px solid white;">6 x 5Gy @80%</td>
                      <td style="padding: 5px; border: 1px solid white;">Falls zentral-zystische Veränderungen oder Nekrose; Frühe Entscheidung über fraktionierten Ansatz aufgrund signifikanter Änderung der Planungsparameter erforderlich</td>
                    </tr>
                     <tr>
                      <td style="padding: 5px; border: 1px solid white;"></td> <!-- Empty cell for # der Metastasen -->
                      <td style="padding: 5px; border: 1px solid white;">&gt;2.5 cm</td>
                      <td style="padding: 5px; border: 1px solid white;">6 x 5Gy @80%</td>
                      <td style="padding: 5px; border: 1px solid white;">Alternative Option - 3 x 8-9 Gy bei einem Durchmesser von weniger als 3.5 cm (<a href="https://thejns.org/view/journals/j-neurosurg/121/Suppl_2/article-p110.xml" style="color: #3292ea; text-decoration: none; font-weight: bold;">Toma-Dasu et al., Journal of Neurosurgery</a>)</td>
                    </tr>
                  </tbody>
                </table>
                <br> <!-- Add some space between tables -->
                <h4>&gt;= 10 Metastasen oder kumulatives Volumen &gt;= 30cc</h4>
                <table border="1" style="width:100%; border-collapse: collapse; border-color: white;">
                  <thead>
                    <tr>
                      <th style="padding: 5px; text-align: left; border: 1px solid white;"># der Metastasen / Kum. Volumen</th>
                      <th style="padding: 5px; text-align: left; border: 1px solid white;">Grösse</th>
                      <th style="padding: 5px; text-align: left; border: 1px solid white;">Dosis</th>
                      <th style="padding: 5px; text-align: left; border: 1px solid white;">Kommentar</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td rowspan="2" style="padding: 5px; border: 1px solid white; vertical-align: top;">&gt;= 10<br>Kumulatives Volumen &gt;= 30cc</td>
                      <td style="padding: 5px; border: 1px solid white;">&lt;2 cm</td>
                      <td style="padding: 5px; border: 1px solid white;">1 x 18-20Gy @80%</td>
                      <td rowspan="2" style="padding: 5px; border: 1px solid white; vertical-align: top;">Individueller Entscheidungsprozess</td>
                    </tr>
                    <tr>
                      <td style="padding: 5px; border: 1px solid white;">&gt;2 cm</td>
                      <td style="padding: 5px; border: 1px solid white;">6 x 5Gy @80%</td>
                    </tr>
                  </tbody>
                </table>
                <br> <!-- Add some space between tables -->
                <h4>Sonderfall: >= 10 Metastasen nicht für SRS/SRT zugänglich</h4>
                <table border="1" style="width:100%; border-collapse: collapse; border-color: white;">
                  <thead>
                    <tr>
                      <th style="padding: 5px; text-align: left; border: 1px solid white;">Situation</th>
                      <th style="padding: 5px; text-align: left; border: 1px solid white;">Bevorzugte Therapie</th>
                      <th style="padding: 5px; text-align: left; border: 1px solid white;">Vorgehen bei GPA Score >= 2.0</th>
                      <th style="padding: 5px; text-align: left; border: 1px solid white;">Vorgehen bei GPA Score 0-1 (hoch palliativ)</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td style="padding: 5px; border: 1px solid white;">>= 10 Metastasen<br>Aufgrund von Verteilung der Läsionen, miliarer Verbreitung und/oder meningealer Anhaftung oder Invasion nicht zugänglich für SRS/SRT</td>
                      <td style="padding: 5px; border: 1px solid white;">Vorzugsweise Ganzhirnradiotherapie</td>
                      <td style="padding: 5px; border: 1px solid white;">10 x 3Gy (Standard)</td>
                      <td style="padding: 5px; border: 1px solid white;">Best supportive care in Erwägung ziehen</td>
                    </tr>
                  </tbody>
                </table>
            """)
            if self.planung_section: self.planung_section.set_content("""
                <p><b>CT-Linac:</b></p>
                <ul>
                    <li>Auf Planungs CT</li>
                    <li>6FFF mit 1400 MU/min Dosisrate</li>
                    <li>Accuros Algorithmus</li>
                    <li>RapidArc</li>
                </ul>
            """)
            if self.akzeptanz_section: self.akzeptanz_section.set_content("""
                <ul>
                    <li>Entsprechend Clinical Protocols</li>
                </ul>
            """)
            if self.applikation_section: self.applikation_section.set_content("""
                <ul>
                    <li>Tägliche CBCT Bildgebung</li>
                    <li>Kaderarzt bei erster Fraktion anwesend</li>
                    <li>Einstellung kann für n+1 Fraktion an MTRAs delegiert werden</li>
                    <li>Offline Review bei Delegation vor Folgefraktionen</li>
                </ul>
            """)
            if self.nachsorge_section: self.nachsorge_section.set_content("""
                <ul>
                    <li>Dokumentation ECOG, Outcome, Tox. CTCAE v5.0, QoL</li>
                    <li>Erste klinische VK 6-8 Wochen nach SRS/ SRT, anschliessend alle 3 Monate,
                    im 1. Jahr mit entsprechender Bildgebung</li>
                    <li>Jahr 2-5 alle 6 Monate mit entsprechender Bildgebung</li>
                    <li>Brief an Zuweiser, Hausarzt und alle involvierten Ärzte</li>
                </ul>
            """)
        
        else:
            # Generic content for the standard sections for OTHER tumor types
            # Make sure common sections are set if no specific match was found
            self.indikation_section.set_content(f"<p>Rechtfertigende Indikation für {self.tumor_type}</p>")
            self.kriterien_section.set_content(f"<p>Einschluss- und Ausschlusskriterien für {self.tumor_type}</p>")
            # Set generic content for the 10 additional standard sections
            if self.staging_section: self.staging_section.set_content(f"<p>Staging für {self.tumor_type}</p>")
            if self.rt_indikation_section: 
                self.rt_indikation_section.setVisible(False)
            if self.planungs_ct_section: self.planungs_ct_section.set_content(f"<p>Planungs-CT bei perkutaner Bestrahlung für {self.tumor_type}</p>")
            if self.zielvolumen_section: self.zielvolumen_section.set_content(f"<p>Zielvolumen Definition für {self.tumor_type}</p>")
            if self.oar_section: self.oar_section.set_content("<p>OAR Definition für Glioblastoma</p>")
            if self.dosierung_section: self.dosierung_section.set_content(f"<p>Dosierung und Fraktionierung für {self.tumor_type}</p>")
            if self.planung_section: self.planung_section.set_content(f"<p>Bestrahlungsplanung für {self.tumor_type}</p>")
            if self.akzeptanz_section: self.akzeptanz_section.set_content(f"<p>Planakzeptanzkriterien für {self.tumor_type}</p>")
            if self.applikation_section: self.applikation_section.set_content(f"<p>Bestrahlungsapplikation für {self.tumor_type}</p>")
            if self.nachsorge_section: self.nachsorge_section.set_content(f"<p>Nachsorge für {self.tumor_type}</p>")
        
    def go_back(self):
        # Import TumorPage locally to avoid circular import at module level
        from .tumor_page import TumorPage
        # go_back now goes to the corresponding tumor page
        current_tumor_page_index = self.main_window.find_page_index(TumorPage, self.tumor_type)
        if current_tumor_page_index is not None:
            self.main_window.stacked_widget.setCurrentIndex(current_tumor_page_index)
        else:
            logging.warning(f"Could not find TumorPage for {self.tumor_type} when going back. Navigating home.")
            # Fallback to home if the specific tumor page isn't found (shouldn't happen ideally)
            self.main_window.go_home()
        
    def go_home(self):
        # Use main window's navigation method
        logging.info("Navigating back to Home page from SOP page.")
        self.main_window.go_home() 