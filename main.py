import os
os.environ['QTWEBENGINE_CHROMIUM_FLAGS'] = '--disable-gpu'

from PyQt6.QtWidgets import (QApplication, QMainWindow, QStackedWidget, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QPushButton, QFrame, QDialog,
                             QLineEdit, QDialogButtonBox, QMessageBox)
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QCoreApplication, QTimer, QUrl
from PyQt6.QtGui import QPalette, QColor, QFont, QPixmap, QIcon, QScreen
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineSettings, QWebEngineProfile

# Page Imports (ensure these paths are correct relative to main.py)
from pages.tumorgroup_pages.tumor_group_page import TumorGroupPage
from pages.entity_pages.EntityPage import EntityPage
from pages.entity_pages.sop_page import SOPPage
from pages.entity_pages.contouring_page import ContouringPage

# Component Imports
from components.sop_search_widget import SopSearchWidget

from pages.tumorgroup_pages.neuroonkologie_page import NeuroonkologiePage
from pages.tumorgroup_pages.bindegewebstumore_page import BindegewebstumorePage
from pages.tumorgroup_pages.KopfHalsTumorePage import KopfHalsTumorePage
from pages.tumorgroup_pages.ThorakaleTumorePage import ThorakaleTumorePage
from pages.tumorgroup_pages.GastrointestinaleTumorePage import GastrointestinaleTumorePage
from pages.tumorgroup_pages.UrogenitaleTumorePage import UrogenitaleTumorePage
from pages.tumorgroup_pages.GynPage import GynPage
from pages.tumorgroup_pages.HauttumorePage import HauttumorePage
from pages.tumorgroup_pages.LymphomePage import LymphomePage
from pages.tumorgroup_pages.FernmetastasenPage import FernmetastasenPage
from pages.tumorgroup_pages.GutartigeErkrankungenPage import GutartigeErkrankungenPage
from pages.tumorgroup_pages.placeholder_group_page import PlaceholderGroupPage

from pages.kisim_page import KisimPage
from pages.cmdscripts_page import CmdScriptsPage
from pages.pdf_reader import PdfReaderPage

from pages.tumorboards_page import TumorboardsPage
from pages.specific_tumorboard_page import SpecificTumorboardPage
from pages.excel_viewer_page import ExcelViewerPage
from pages.tumorboard_session_page import TumorboardSessionPage

# Utils imports (removed initialize_all_collection_files as it's no longer needed)

# Standard Library Imports
import sys
import datetime
import base64
import json
import traceback
import re
import subprocess

# Cryptography Imports
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization

# --- Global Print Prefix ---
APP_PREFIX = "INFO: USZ-RAO-App: main.py - "
print(f"{APP_PREFIX}--- Application Starting (Print Logging Mode) ---")

# --- Windows Specific AppUserModelID Setup ---
if sys.platform == 'win32':
    try:
        import ctypes
        myappid = u'USZ.RAOApp.TumorGuide.1.0' # Unique App ID
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        print(f"{APP_PREFIX}AppUserModelID gesetzt auf: {myappid}")
    except Exception as e:
        print(f"WARNUNG: {APP_PREFIX}Fehler beim Setzen der AppUserModelID: {e}")

# --- Constants ---
PUBLIC_KEY_PEM = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA2IFO7yr+4s/9vlmLZXfY
vKbVBuCk0fUgWdh88jL3SiUPhHJ0MTNP1s7ZTvgIFPIzfFO5Hv/3rT/csFiB//IN
1ad1fxuClq4Rm/Y0NGA14VWqxQzRMDnvH5cAqANBoND1g5uEpL/S00Ed0eB3snse
QTLqZtf0mMyYIg30WinWrkX5C7T2KNTMp6BZGrcyeFXGBM/mwVvkRxzeUOTGCPZe
7a4heBP8p1hp1q4fpVoNBgzBJ6BSW5GjWhAKurfs1VMSde9xuJmEhb5tclYcH23s
N2UkIBZjMerEXyDVgzD+zI/6YfyeVOHiAvdAzqbLj+k167qQsT5Y3N/BJ6zz9Tvk
2QIDAQAB
-----END PUBLIC KEY-----"""
LICENSE_STATE_FILE = "license_state.txt"

# --- Helper Functions ---
def initialize_global_webengine_settings():
    print(f"{APP_PREFIX}Attempting to initialize global WebEngine profile settings.")
    try:
        profile = QWebEngineProfile.defaultProfile()
        profile.setPersistentCookiesPolicy(QWebEngineProfile.PersistentCookiesPolicy.NoPersistentCookies)
        profile.setHttpCacheType(QWebEngineProfile.HttpCacheType.MemoryHttpCache)
        print(f"{APP_PREFIX}Global WebEngine profile settings initialized successfully.")
    except Exception as e:
        print(f"ERROR: {APP_PREFIX}Error initializing global WebEngine profile settings: {e}")
        traceback.print_exc()

def verify_license(public_key_pem, license_key_b64, expected_data_str):
    try:
        public_key = serialization.load_pem_public_key(public_key_pem.encode('utf-8'))
        signature = base64.b64decode(license_key_b64)
        expected_data = expected_data_str.encode('utf-8')
        public_key.verify(
            signature, expected_data,
            padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
            hashes.SHA256()
        )
        print(f"{APP_PREFIX}License verification successful for data: {expected_data_str}")
        return True
    except Exception as e:
        print(f"ERROR: {APP_PREFIX}License verification failed for data '{expected_data_str}': {e}")
        return False

def read_license_state():
    try:
        with open(LICENSE_STATE_FILE, 'r') as f:
            state = json.load(f)
            return state.get("month", None), state.get("iso_year", None), state.get("iso_week", None)
    except (FileNotFoundError, json.JSONDecodeError):
        return None, None, None

def write_license_state(month_str, iso_year, iso_week):
    state = {"month": month_str, "iso_year": iso_year, "iso_week": iso_week}
    try:
        with open(LICENSE_STATE_FILE, 'w') as f:
            json.dump(state, f)
            print(f"{APP_PREFIX}Wrote license state: month={month_str}, year={iso_year}, week={iso_week}")
    except IOError as e:
        print(f"ERROR: {APP_PREFIX}Error writing license state: {e}")
        traceback.print_exc()

class LicenseDialog(QDialog):
    def __init__(self, month_str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("License Activation"); self.setModal(True); self.setMinimumWidth(400)
        self.setStyleSheet("""
            QDialog { background-color: #19232D; } QLabel { color: white; font-size: 14px; }
            QLineEdit { background-color: #232F3B; color: white; border: 1px solid #425061; padding: 5px; font-size: 14px; }
            QPushButton { background-color: #37414F; color: white; padding: 8px 15px; border: none; border-radius: 3px; min-width: 80px; }
            QPushButton:hover { background-color: #4C5A6D; }""")
        layout = QVBoxLayout(self)
        self.info_label = QLabel(f"Please enter the license key for {month_str}:"); layout.addWidget(self.info_label)
        self.key_input = QLineEdit(); self.key_input.setPlaceholderText("Enter license key here"); layout.addWidget(self.key_input)
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept); self.button_box.rejected.connect(self.reject); layout.addWidget(self.button_box)
    def get_key(self): return self.key_input.text().strip()

class TumorGuideApp(QMainWindow):
    def __init__(self):
        super().__init__()
        print(f"{APP_PREFIX}Initializing TumorGuideApp...")
        self.app_version = "N/A"
        try:
            version_path = os.path.join(os.path.dirname(__file__), 'version.txt')
            if os.path.exists(version_path):
                with open(version_path, 'r') as f:
                    self.app_version = f.read().strip()
            else:
                print(f"WARNUNG: {APP_PREFIX}version.txt nicht gefunden.")
        except Exception as e:
            print(f"WARNUNG: {APP_PREFIX}Konnte version.txt nicht lesen: {e}")
        self.setMinimumSize(1600, 900)
        self.setWindowTitle(f"USZ-RAO-App_v{self.app_version}")
        base_dir = os.path.dirname(os.path.abspath(__file__)) # Use abspath for reliability
        icon_path = os.path.join(base_dir, "assets", "usz_logo_klein.ico")
        if os.path.exists(icon_path): self.setWindowIcon(QIcon(icon_path))
        else: print(f"WARNUNG: {APP_PREFIX}Icon-Datei nicht gefunden: {icon_path}")

        self._sacrificial_web_view_html = None
        self.menu_buttons = {}
        main_widget = QWidget(); self.main_layout = QHBoxLayout(main_widget)
        self.main_layout.setContentsMargins(0,0,0,0); self.main_layout.setSpacing(0)
        self.left_menu = self._create_left_menu(); self.main_layout.addWidget(self.left_menu)
        content_widget = QWidget(); self.content_layout = QVBoxLayout(content_widget)
        self.content_layout.setContentsMargins(10,10,10,10); self.content_layout.setSpacing(15)
        
        # Kombiniertes Layout für Breadcrumbs und Searchbar auf derselben Zeile
        self.header_breadcrumb_layout = QHBoxLayout()
        self.header_breadcrumb_layout.setContentsMargins(0,0,20,0)  # 20px rechter Abstand
        self.header_breadcrumb_layout.setSpacing(10)
        self.header_breadcrumb_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)  # Vertikale Zentrierung
        
        # Breadcrumbs links
        self.breadcrumb_layout = self._create_breadcrumb_bar()
        self.header_breadcrumb_layout.addLayout(self.breadcrumb_layout)
        
        # Stretch um Platz zwischen Breadcrumbs und Searchbar zu schaffen
        self.header_breadcrumb_layout.addStretch()
        
        # Searchbar wird später hier hinzugefügt
        self.content_layout.addLayout(self.header_breadcrumb_layout)
        self.stacked_widget = QStackedWidget(); self.content_layout.addWidget(self.stacked_widget)
        self.main_layout.addWidget(content_widget); self.setCentralWidget(main_widget)
        self.tumor_group_page = TumorGroupPage(self); self.stacked_widget.addWidget(self.tumor_group_page)
        self.kisim_page = None; self.cmd_scripts_page = None; self.tumorboards_page = None; self.backoffice_page = None; self.developer_area_page = None
        self.stacked_widget.currentChanged.connect(self.update_breadcrumb)
        self.stacked_widget.currentChanged.connect(self.handle_page_change)
        
        # SOP-Dateien sammeln und Searchbar initialisieren
        self.sop_files = self._collect_sop_files()
        self.sop_search_widget = SopSearchWidget(self.sop_files, self)
        self.sop_search_widget.pdf_selected.connect(self.open_sop_from_search)
        self.sop_search_widget.hide()  # Standardmäßig versteckt
        
        QTimer.singleShot(10, self._initialize_sacrificial_webengine_html_only)

        self.apply_dark_blue_theme()
        self.update_breadcrumb(0)
        
        # Setup monitor detection and positioning
        self.setup_monitor_positioning()
        
        # Searchbar zum Header hinzufügen (nach der Initialisierung)
        self._add_searchbar_to_header()
        
        # Initiale Sichtbarkeit der Searchbar setzen (TumorGroupPage ist standardmäßig aktiv)
        if hasattr(self, 'sop_search_widget'):
            self.sop_search_widget.show()
            print(f"{APP_PREFIX}Searchbar initial sichtbar (Tumor navigator ist Startseite)")
        
        print(f"{APP_PREFIX}TumorGuideApp initialization complete.")

    def setup_monitor_positioning(self):
        """Detect monitors and position window on secondary monitor if available, otherwise primary monitor maximized"""
        try:
            app = QApplication.instance()
            screens = app.screens()
            screen_count = len(screens)
            
            print(f"{APP_PREFIX}Detected {screen_count} monitor(s)")
            
            if screen_count >= 2:
                # Multiple monitors detected - use secondary monitor (non-primary)
                primary_screen = app.primaryScreen()
                secondary_screen = None
                
                # Find the first non-primary screen
                for screen in screens:
                    if screen != primary_screen:
                        secondary_screen = screen
                        break
                
                if secondary_screen:
                    print(f"{APP_PREFIX}Using secondary monitor: {secondary_screen.name()}")
                    # Get the geometry of the secondary screen
                    screen_geometry = secondary_screen.availableGeometry()
                    
                    # Move window to secondary screen and show maximized (windowed but maximized)
                    self.setGeometry(screen_geometry)
                    self.show()
                    self.showMaximized()
                    print(f"{APP_PREFIX}Application positioned on secondary monitor in maximized windowed mode")
                else:
                    # Fallback to primary screen if secondary not found
                    print(f"{APP_PREFIX}Secondary monitor not found, using primary monitor")
                    self.show()
                    self.showMaximized()
            else:
                # Single monitor - use primary monitor maximized
                print(f"{APP_PREFIX}Single monitor detected, using primary monitor in maximized windowed mode")
                self.show()
                self.showMaximized()
                
        except Exception as e:
            print(f"ERROR: {APP_PREFIX}Error in monitor detection: {e}")
            # Fallback to normal maximized on primary monitor
            self.show()
            self.showMaximized()

    def _collect_sop_files(self):
        """Sammelt alle PDF-Dateien aus dem assets/sop Verzeichnis rekursiv"""
        sop_files = []
        base_dir = os.path.dirname(os.path.abspath(__file__))
        sop_dir = os.path.join(base_dir, 'assets', 'sop')
        
        if not os.path.exists(sop_dir):
            print(f"WARNUNG: {APP_PREFIX}SOP-Verzeichnis nicht gefunden: {sop_dir}")
            return sop_files
            
        # Rekursiv alle PDF-Dateien sammeln
        for root, dirs, files in os.walk(sop_dir):
            for file in files:
                if file.lower().endswith('.pdf'):
                    full_path = os.path.join(root, file)
                    sop_files.append(full_path)
                    
        print(f"{APP_PREFIX}Gefundene SOP-PDF-Dateien: {len(sop_files)}")
        return sop_files
        
    def _add_searchbar_to_header(self):
        """Fügt die Searchbar zum kombinierten Header-Breadcrumb-Layout hinzu"""
        if hasattr(self, 'sop_search_widget') and hasattr(self, 'header_breadcrumb_layout'):
            # Searchbar rechts zum kombinierten Layout hinzufügen
            self.header_breadcrumb_layout.addWidget(self.sop_search_widget)
            print(f"{APP_PREFIX}Searchbar zum kombinierten Header-Breadcrumb-Layout hinzugefügt")
                
    def open_sop_from_search(self, pdf_path):
        """Öffnet eine SOP-PDF aus der Suche in der PdfReaderPage"""
        if not os.path.exists(pdf_path):
            print(f"ERROR: {APP_PREFIX}PDF-Datei nicht gefunden: {pdf_path}")
            return
            
        try:
            # Extrahiere Gruppen- und Entity-Namen aus dem Pfad für die Breadcrumbs
            rel_path = os.path.relpath(pdf_path, os.path.join(os.path.dirname(__file__), 'assets', 'sop'))
            path_parts = rel_path.split(os.sep)
            
            group_name = path_parts[0] if len(path_parts) > 1 else "SOP"
            entity_name = path_parts[1] if len(path_parts) > 2 else os.path.basename(pdf_path).replace('.pdf', '')
            
            # Erstelle PdfReaderPage
            pdf_reader = PdfReaderPage(self, pdf_path, group_name, entity_name)
            
            # Füge zur StackedWidget hinzu und zeige an
            pdf_index = self.stacked_widget.addWidget(pdf_reader)
            self.stacked_widget.setCurrentIndex(pdf_index)
            
            print(f"{APP_PREFIX}SOP-PDF geöffnet: {os.path.basename(pdf_path)}")
            
        except Exception as e:
            print(f"ERROR: {APP_PREFIX}Fehler beim Öffnen der SOP-PDF: {e}")
            import traceback
            traceback.print_exc()

    def _initialize_sacrificial_webengine_html_only(self):
        if self._sacrificial_web_view_html is None:
            print(f"{APP_PREFIX}_initialize_sacrificial_webengine_html_only: Attempting basic HTML init.")
            try:
                self._sacrificial_web_view_html = QWebEngineView()
                self._sacrificial_web_view_html.setHtml("<html><body>Basic Init</body></html>", QUrl("local://basic.html"))
                QApplication.processEvents()
                print(f"{APP_PREFIX}_initialize_sacrificial_webengine_html_only: Basic HTML WebEngineView created.")
                QTimer.singleShot(200, self._delete_sacrificial_web_view_html)
            except Exception as e:
                print(f"ERROR: {APP_PREFIX}_initialize_sacrificial_webengine_html_only: {e}")
                traceback.print_exc()

    def _delete_sacrificial_web_view_html(self):
        if self._sacrificial_web_view_html:
            print(f"{APP_PREFIX}Deleting sacrificial HTML-only QWebEngineView.")
            self._sacrificial_web_view_html.deleteLater()
            self._sacrificial_web_view_html = None

    def attempt_first_run_pdf_load_workaround(self):
        print(f"{APP_PREFIX}attempt_first_run_pdf_load_workaround: Initiating PDF load with dummy.pdf.")
        
        pdf_filename_dummy = "dummy.pdf"
        base_dir = os.path.dirname(os.path.abspath(__file__))
        target_pdf_path = os.path.join(base_dir, 'assets', 'sop', pdf_filename_dummy)

        if not os.path.exists(target_pdf_path):
            print(f"ERROR: {APP_PREFIX}Dummy PDF for workaround not found: {target_pdf_path}")
            # No QMessageBox here, just print, as it's an internal workaround file
            return

        print(f"{APP_PREFIX}attempt_first_run_pdf_load_workaround: Creating PdfReaderPage for: {target_pdf_path}")
        try:
            # Pass placeholder group/entity names for dummy.pdf
            workaround_pdf_viewer = PdfReaderPage(self, target_pdf_path, "WORKAROUND_DUMMY", "INIT_PDF")
            
            original_main_idx = self.stacked_widget.currentIndex()
            temp_idx = self.stacked_widget.addWidget(workaround_pdf_viewer)
            self.stacked_widget.setCurrentIndex(temp_idx)
            print(f"{APP_PREFIX}attempt_first_run_pdf_load_workaround: Workaround PDF viewer (dummy.pdf) set as current widget.")

            QApplication.processEvents(); QApplication.processEvents() 
            print(f"{APP_PREFIX}attempt_first_run_pdf_load_workaround: Events processed after showing workaround PDF (dummy.pdf).")

            QTimer.singleShot(100, lambda: self._cleanup_workaround_pdf_viewer(workaround_pdf_viewer, original_main_idx))
            print(f"{APP_PREFIX}attempt_first_run_pdf_load_workaround: Cleanup for workaround PDF viewer (dummy.pdf) scheduled.")
        except Exception as e:
            print(f"ERROR: {APP_PREFIX}Exception during attempt_first_run_pdf_load_workaround with dummy.pdf: {e}")
            traceback.print_exc()

    def _cleanup_workaround_pdf_viewer(self, viewer_instance, original_idx):
        print(f"{APP_PREFIX}_cleanup_workaround_pdf_viewer: Cleaning up after first-run PDF load attempt.")
        try:
            if viewer_instance and self.stacked_widget.indexOf(viewer_instance) != -1 :
                self.stacked_widget.removeWidget(viewer_instance)
                viewer_instance.deleteLater()
                print(f"{APP_PREFIX}_cleanup_workaround_pdf_viewer: Workaround PDF viewer removed.")
            
            if 0 <= original_idx < self.stacked_widget.count() and self.stacked_widget.widget(original_idx) is not None :
                self.stacked_widget.setCurrentIndex(original_idx)
            else: self.go_home()
            print(f"{APP_PREFIX}_cleanup_workaround_pdf_viewer: View restored.")
        except Exception as e:
            print(f"ERROR: {APP_PREFIX}_cleanup_workaround_pdf_viewer: {e}")
            traceback.print_exc()
            self.go_home()

    def _create_left_menu(self):
        menu_frame=QFrame();menu_frame.setObjectName("leftMenu");menu_frame.setFixedWidth(215);menu_frame.setStyleSheet("#leftMenu { background-color: #1a2633; border-right: 1px solid #2a3642; }");menu_layout=QVBoxLayout(menu_frame);menu_layout.setContentsMargins(10,20,10,10);menu_layout.setSpacing(0);logo_container=QFrame();logo_container.setStyleSheet("background: transparent;");logo_layout=QVBoxLayout(logo_container);logo_layout.setContentsMargins(0,0,0,20);logo_layout.setSpacing(5);logo_label=QLabel();logo_path=os.path.join(os.path.dirname(__file__),"assets","usz_logo.png");
        if os.path.exists(logo_path):logo_label.setPixmap(QPixmap(logo_path).scaledToHeight(50,Qt.TransformationMode.SmoothTransformation))
        else:logo_label.setText("USZ")
        dept_label=QLabel("Department of Radiation Oncology");dept_label.setFont(QFont("Helvetica",11,QFont.Weight.Bold));dept_label.setStyleSheet("color: #00BFFF; padding: 0; margin: 0; background: transparent;");dept_label.setWordWrap(True);logo_layout.addWidget(logo_label,0,Qt.AlignmentFlag.AlignLeft);logo_layout.addWidget(dept_label,0,Qt.AlignmentFlag.AlignLeft);menu_layout.addWidget(logo_container);separator=QFrame();separator.setFrameShape(QFrame.Shape.HLine);separator.setStyleSheet("background-color: #2a3642; min-height: 1px; max-height: 1px;");menu_layout.addWidget(separator);menu_layout.addSpacing(20)
        
        version_label = QLabel(f"Version: {self.app_version}")
        version_label.setFont(QFont("Helvetica", 9)) # Etwas kleiner als der Department-Text
        version_label.setStyleSheet("color: #cccccc; padding-top: 4px; background: transparent;") # Weiss/Hellgrau, dünn (durch Font-Einstellung), mit etwas Abstand nach oben
        logo_layout.addWidget(version_label, 0, Qt.AlignmentFlag.AlignLeft)

        self.active_menu_style="QPushButton { background-color: #3292ea; color: white; font-weight: bold; font-size: 16px; text-align: left; padding-left: 15px; border: none; } QPushButton:hover { background-color: #4da2fa; }";self.inactive_menu_style="QPushButton { background-color: transparent; color: white; font-size: 15px; text-align: left; padding-left: 15px; border: none; border-bottom: 1px solid #2a3642; } QPushButton:hover { background-color: #2a3642; }"
        menu_items=["Tumor navigator","Tumorboards", "KISIM Scripts","Backoffice","Developer Area"]
        for i,item_text in enumerate(menu_items):
            menu_button=QPushButton(item_text);menu_button.setCursor(Qt.CursorShape.PointingHandCursor);menu_button.setFixedHeight(60)
            if i==0:menu_button.setStyleSheet(self.active_menu_style);menu_button.clicked.connect(self.go_home)
            else:
                menu_button.setStyleSheet(self.inactive_menu_style)
                if item_text=="KISIM Scripts":menu_button.clicked.connect(self.open_kisim_page)
                elif item_text=="Tumorboards":menu_button.clicked.connect(self.open_tumorboards_page)
                elif item_text=="Backoffice":menu_button.clicked.connect(self.open_backoffice_page)
                elif item_text=="Developer Area":menu_button.clicked.connect(self.open_developer_area_page)
            self.menu_buttons[item_text]=menu_button;menu_layout.addWidget(menu_button)
        menu_layout.addStretch();return menu_frame

    def _create_breadcrumb_bar(self): breadcrumb_layout=QHBoxLayout();breadcrumb_layout.setContentsMargins(0,0,0,0);breadcrumb_layout.setSpacing(5);breadcrumb_layout.setAlignment(Qt.AlignmentFlag.AlignLeft);return breadcrumb_layout
    def _clear_layout(self,layout):
        while layout.count():
            child=layout.takeAt(0)
            if child.widget():child.widget().deleteLater()
    def update_breadcrumb(self,index):
        self._clear_layout(self.breadcrumb_layout);current_widget=self.stacked_widget.widget(index)
        if current_widget is None:print(f"WARNUNG: {APP_PREFIX}update_breadcrumb called with invalid index {index}, current_widget is None.");return
        page_name=current_widget.__class__.__name__;print(f"{APP_PREFIX}Updating breadcrumb for page index {index}, type: {page_name}");separator_style="color: white; font-size: 20px;";page_label_style="color: #3292ea; font-weight: bold; font-size: 20px;"
        page_button_style="QPushButton { color: white; background: transparent; border: none; font-weight: bold; font-size: 20px; text-align: left; padding: 0; } QPushButton:hover { text-decoration: underline; }"
        def add_separator():separator=QLabel("→");separator.setStyleSheet(separator_style);self.breadcrumb_layout.addWidget(separator)
        def add_button(text,target_page_class,**kwargs):
            button=QPushButton(text);button.setCursor(Qt.CursorShape.PointingHandCursor);button.setStyleSheet(page_button_style);page_idx=self.find_page_index(target_page_class,**kwargs)
            if page_idx is not None:button.clicked.connect(lambda checked=False,idx=page_idx:self.navigate_with_session_check(idx))
            else:button.setEnabled(False);print(f"WARNUNG: {APP_PREFIX}Could not find index for breadcrumb button: {text} ({target_page_class.__name__}) with args {kwargs}")
            self.breadcrumb_layout.addWidget(button)
        def add_label(text):label=QLabel(text);label.setStyleSheet(page_label_style);self.breadcrumb_layout.addWidget(label)
        home_breadcrumb_btn=QPushButton();home_icon_path=os.path.join(os.path.dirname(__file__),"assets","home_button.png")
        if os.path.exists(home_icon_path):home_icon=QPixmap(home_icon_path).scaledToHeight(60,Qt.TransformationMode.SmoothTransformation);home_breadcrumb_btn.setIcon(QIcon(home_icon));home_breadcrumb_btn.setIconSize(QSize(60,60))
        else:home_breadcrumb_btn.setText("Home")
        home_breadcrumb_btn.setCursor(Qt.CursorShape.PointingHandCursor);home_breadcrumb_btn.clicked.connect(self.go_home);home_breadcrumb_btn.setStyleSheet("QPushButton { background: transparent; border: none; padding: 0; margin-right: 3px; } QPushButton:hover { background-color: rgba(255, 255, 255, 30); }");self.breadcrumb_layout.addWidget(home_breadcrumb_btn)
        group_page_map={"Neuroonkologie":NeuroonkologiePage,"Kopf-Hals-Tumore":KopfHalsTumorePage,"Thorakale Tumore":ThorakaleTumorePage,"Gastrointestinale Tumore":GastrointestinaleTumorePage,"Urogenitale Tumore":UrogenitaleTumorePage,"Gynäkologische Tumore":GynPage,"Bindegewebstumore":BindegewebstumorePage,"Hauttumore":HauttumorePage,"Lymphome":LymphomePage,"Fernmetastasen":FernmetastasenPage,"Gutartige Erkrankungen":GutartigeErkrankungenPage}
        if isinstance(current_widget,TumorGroupPage):pass
        elif isinstance(current_widget,tuple(group_page_map.values())):add_separator();add_label(getattr(current_widget,'group_name',page_name.replace('Page','')))
        elif isinstance(current_widget,EntityPage):
            group_name=getattr(current_widget,'group_name',None);entity_name=getattr(current_widget,'entity_name','Entity')
            if group_name:group_page_class=group_page_map.get(group_name);
            if group_page_class:add_separator();add_button(group_name,group_page_class)
            else:add_separator();add_label(group_name)
            add_separator();add_label(entity_name)
        elif isinstance(current_widget,PdfReaderPage):
            group_name=getattr(current_widget,'group_name',None);entity_name=getattr(current_widget,'entity_name',None);pdf_filename=os.path.basename(getattr(current_widget,'pdf_path','PDF'))
            if group_name and entity_name:
                group_page_class=group_page_map.get(group_name)
                if group_page_class:add_separator();add_button(group_name,group_page_class)
                else:add_separator();add_label(group_name)
                add_separator();add_button(entity_name,EntityPage,entity_name=entity_name,group_name=group_name)
            elif entity_name:add_separator();add_label(entity_name)
            add_separator();add_label(pdf_filename)
        elif isinstance(current_widget,(SOPPage,ContouringPage)):
            group_name=getattr(current_widget,'group_name',None);entity_name=getattr(current_widget,'tumor_type','Entity');page_type_label="SOP" if isinstance(current_widget,SOPPage) else "Contouring"
            if group_name:
                group_page_class=group_page_map.get(group_name)
                if group_page_class:add_separator();add_button(group_name,group_page_class)
                else:add_separator();add_label(group_name)
            add_separator();add_button(entity_name,EntityPage,entity_name=entity_name,group_name=group_name);add_separator();add_label(page_type_label)
        elif isinstance(current_widget,TumorboardsPage):add_separator();add_label("Tumorboards")
        elif isinstance(current_widget,SpecificTumorboardPage):add_separator();add_button("Tumorboards",TumorboardsPage);add_separator();add_label(getattr(current_widget,'tumorboard_name','Tumorboard'))
        elif isinstance(current_widget,ExcelViewerPage):add_separator();add_button("Tumorboards",TumorboardsPage);add_separator();add_button(getattr(current_widget,'tumorboard_name','Tumorboard'),SpecificTumorboardPage,entity_name=getattr(current_widget,'tumorboard_name','Tumorboard'));add_separator();add_label(getattr(current_widget,'date_str','Datum'))
        elif isinstance(current_widget,TumorboardSessionPage):add_separator();add_button("Tumorboards",TumorboardsPage);add_separator();add_button(getattr(current_widget,'tumorboard_name','Tumorboard'),SpecificTumorboardPage,entity_name=getattr(current_widget,'tumorboard_name','Tumorboard'));add_separator();add_button(getattr(current_widget,'date_str','Datum'),ExcelViewerPage,entity_name=f"{getattr(current_widget,'tumorboard_name','Tumorboard')}_{getattr(current_widget,'date_str','Datum')}");add_separator();add_label("Session")
        elif isinstance(current_widget,KisimPage):add_separator();add_label("KISIM Scripts")
        elif current_widget.__class__.__name__ == "BackofficePage":add_separator();add_label("Backoffice")
        elif current_widget.__class__.__name__ == "BackofficeTumorboardsPage":
            # Import BackofficePage for breadcrumb button
            try:
                from pages.backoffice_page import BackofficePage
                add_separator();add_button("Backoffice",BackofficePage);add_separator();add_label("Abgeschlossene Tumorboards")
            except ImportError:
                add_separator();add_label("Backoffice");add_separator();add_label("Abgeschlossene Tumorboards")
        elif current_widget.__class__.__name__ == "BackofficeExcelViewerPage":
            # Check if this came from the billing (leistungsabrechnungen) page
            source_page = getattr(current_widget, 'source_page', None)
            
            if source_page == "leistungsabrechnungen":
                # Import BackofficePage and BackofficePageLeistungsabrechnungen for breadcrumb buttons
                try:
                    from pages.backoffice_page import BackofficePage
                    from pages.backoffice_page_leistungsabrechnungen import BackofficePageLeistungsabrechnungen
                    add_separator();add_button("Backoffice",BackofficePage);add_separator();add_button("Leistungsabrechnungen Tumorboards",BackofficePageLeistungsabrechnungen);add_separator();add_label(f"{getattr(current_widget,'tumorboard_name','Tumorboard')} - {getattr(current_widget,'date_str','Datum')}")
                except ImportError:
                    add_separator();add_label("Backoffice");add_separator();add_label("Leistungsabrechnungen Tumorboards");add_separator();add_label(f"{getattr(current_widget,'tumorboard_name','Tumorboard')} - {getattr(current_widget,'date_str','Datum')}")
            else:
                # Default behavior - came from regular tumorboards page
                try:
                    from pages.backoffice_page import BackofficePage
                    from pages.backoffice_tumorboards_page import BackofficeTumorboardsPage
                    add_separator();add_button("Backoffice",BackofficePage);add_separator();add_button("Abgeschlossene Tumorboards",BackofficeTumorboardsPage);add_separator();add_label(f"{getattr(current_widget,'tumorboard_name','Tumorboard')} - {getattr(current_widget,'date_str','Datum')}")
                except ImportError:
                    add_separator();add_label("Backoffice");add_separator();add_label("Abgeschlossene Tumorboards");add_separator();add_label(f"{getattr(current_widget,'tumorboard_name','Tumorboard')} - {getattr(current_widget,'date_str','Datum')}")
        elif current_widget.__class__.__name__ == "BackofficePageErstkonsultationen":
            # Import BackofficePage for breadcrumb button
            try:
                from pages.backoffice_page import BackofficePage
                add_separator();add_button("Backoffice",BackofficePage);add_separator();add_label("Erstkonsultationen")
            except ImportError:
                add_separator();add_label("Backoffice");add_separator();add_label("Erstkonsultationen")
        elif current_widget.__class__.__name__ == "BackofficeKatIPage":
            # Import BackofficePage and BackofficePageErstkonsultationen for breadcrumb buttons  
            try:
                from pages.backoffice_page import BackofficePage
                from pages.backoffice_page_erstkonsultationen import BackofficePageErstkonsultationen
                add_separator();add_button("Backoffice",BackofficePage);add_separator();add_button("Erstkonsultationen",BackofficePageErstkonsultationen);add_separator();add_label("Kategorie I")
            except ImportError:
                add_separator();add_label("Backoffice");add_separator();add_label("Erstkonsultationen");add_separator();add_label("Kategorie I")
        elif current_widget.__class__.__name__ == "BackofficeKatIIPage":
            # Import BackofficePage and BackofficePageErstkonsultationen for breadcrumb buttons
            try:
                from pages.backoffice_page import BackofficePage
                from pages.backoffice_page_erstkonsultationen import BackofficePageErstkonsultationen
                add_separator();add_button("Backoffice",BackofficePage);add_separator();add_button("Erstkonsultationen",BackofficePageErstkonsultationen);add_separator();add_label("Kategorie II")
            except ImportError:
                add_separator();add_label("Backoffice");add_separator();add_label("Erstkonsultationen");add_separator();add_label("Kategorie II")
        elif current_widget.__class__.__name__ == "BackofficeKatIIIPage":
            # Import BackofficePage and BackofficePageErstkonsultationen for breadcrumb buttons
            try:
                from pages.backoffice_page import BackofficePage
                from pages.backoffice_page_erstkonsultationen import BackofficePageErstkonsultationen
                add_separator();add_button("Backoffice",BackofficePage);add_separator();add_button("Erstkonsultationen",BackofficePageErstkonsultationen);add_separator();add_label("Kategorie III")
            except ImportError:
                add_separator();add_label("Backoffice");add_separator();add_label("Erstkonsultationen");add_separator();add_label("Kategorie III")
        elif current_widget.__class__.__name__ == "DeveloperAreaPage":add_separator();add_label("Developer Area")
        elif isinstance(current_widget,CmdScriptsPage):
            # Check if we came from Developer Area by looking at the script being run
            script_name_full=getattr(current_widget.title_label,'text',lambda:"Script Output")();script_name=script_name_full.split(" (")[0] if " (" in script_name_full else script_name_full
            if not script_name or script_name.startswith("Error:")or script_name=="Script Output":script_name="Script Output"
            
            # Check if this is a database_manager script (from Developer Area)
            if hasattr(current_widget, 'current_script_key') and current_widget.current_script_key == "database_manager":
                # Import the DeveloperAreaPage class for breadcrumb button
                try:
                    from pages.developer_area_page_simple import DeveloperAreaPage
                    add_separator();add_button("Developer Area",DeveloperAreaPage);add_separator();add_label(script_name)
                except ImportError:
                    add_separator();add_label("Developer Area");add_separator();add_label(script_name)
            else:
                add_separator();add_button("KISIM Scripts",KisimPage);add_separator();add_label(script_name)
        else:add_separator();add_label(page_name.replace('Page',''))
        # addStretch() wird jetzt im übergeordneten header_breadcrumb_layout gemacht
    def find_page_index(self,page_type,entity_name=None,group_name=None):
        for i in range(self.stacked_widget.count()):
            widget=self.stacked_widget.widget(i)
            if isinstance(widget,page_type):
                match=True
                if entity_name is not None:
                    widget_entity_name=getattr(widget,'entity_name',getattr(widget,'tumor_type',None));widget_group_name_attr=getattr(widget,'group_name',None)
                    if not(widget_entity_name==entity_name or(isinstance(widget,PlaceholderGroupPage)and widget_group_name_attr==entity_name)):match=False
                if match and group_name is not None and getattr(widget,'group_name',None)!=group_name:match=False
                if match:return i
        return None    
    def check_tumorboard_session_before_navigation(self):
        """Check if there's an active tumorboard session with unsaved changes"""
        current_widget = self.stacked_widget.currentWidget()
        if hasattr(current_widget, 'check_unsaved_changes'):
            # This is a TumorboardSessionPage with unsaved changes check
            return current_widget.check_unsaved_changes()
        return True  # No active session or no unsaved changes
    
    def navigate_with_session_check(self, target_index):
        """Navigate to target index after checking for unsaved changes"""
        if self.check_tumorboard_session_before_navigation():
            self.stacked_widget.setCurrentIndex(target_index)
    
    def go_home(self):        
        if not self.check_tumorboard_session_before_navigation():
            return  # User cancelled navigation
            
        if self.stacked_widget.count()>0 and isinstance(self.stacked_widget.widget(0),TumorGroupPage):
            self.stacked_widget.setCurrentIndex(0);self._update_active_menu("Tumor navigator");print(f"{APP_PREFIX}Navigated to TumorGroupPage (Home).")        
        else:print(f"WARNUNG: {APP_PREFIX}Could not navigate home, initial page is not TumorGroupPage or doesn't exist.")    
    def open_kisim_page(self):        
        if not self.check_tumorboard_session_before_navigation():
            return  # User cancelled navigation
            
        if self.kisim_page is None:
            print(f"{APP_PREFIX}Creating KisimPage instance.")
            self.kisim_page=KisimPage(self)
            self.stacked_widget.addWidget(self.kisim_page)
        
        self.stacked_widget.setCurrentWidget(self.kisim_page)
        self._update_active_menu("KISIM Scripts")
        print(f"{APP_PREFIX}Navigated to KISIM Scripts page.")    
    def open_tumorboards_page(self):        
        if not self.check_tumorboard_session_before_navigation():
            return  # User cancelled navigation
            
        if self.tumorboards_page is None:
            print(f"{APP_PREFIX}Creating TumorboardsPage instance.")
            self.tumorboards_page=TumorboardsPage(self)
            self.stacked_widget.addWidget(self.tumorboards_page)
        
        self.stacked_widget.setCurrentWidget(self.tumorboards_page)
        self._update_active_menu("Tumorboards")
        print(f"{APP_PREFIX}Navigated to Tumorboards page.")
    
    def open_backoffice_page(self):        
        if not self.check_tumorboard_session_before_navigation():
            return  # User cancelled navigation
            
        if self.backoffice_page is None:
            print(f"{APP_PREFIX}Creating BackofficePage instance.")
            from pages.backoffice_page import BackofficePage
            self.backoffice_page=BackofficePage(self)
            self.stacked_widget.addWidget(self.backoffice_page)
        
        self.stacked_widget.setCurrentWidget(self.backoffice_page)
        self._update_active_menu("Backoffice")
        print(f"{APP_PREFIX}Navigated to Backoffice page.")

    def open_developer_area_page(self):        
        if not self.check_tumorboard_session_before_navigation():
            return  # User cancelled navigation
        
        # Show password dialog before opening Developer Area
        from pages.developer_area_page_simple import PasswordDialog
        
        password_dialog = PasswordDialog(self)
        if password_dialog.exec() == QDialog.DialogCode.Accepted:
            entered_password = password_dialog.get_password()
            
            # Check password
            if entered_password == "developer":
                print(f"{APP_PREFIX}Developer Area access granted.")
                
                if self.developer_area_page is None:
                    print(f"{APP_PREFIX}Creating DeveloperAreaPage instance.")
                    from pages.developer_area_page_simple import DeveloperAreaPage
                    self.developer_area_page=DeveloperAreaPage(self)
                    self.stacked_widget.addWidget(self.developer_area_page)
                
                self.stacked_widget.setCurrentWidget(self.developer_area_page)
                self._update_active_menu("Developer Area")
                print(f"{APP_PREFIX}Navigated to Developer Area page.")
            else:
                print(f"{APP_PREFIX}Developer Area access denied - incorrect password.")
                msg_box = QMessageBox(self)
                msg_box.setWindowTitle("Zugriff verweigert")
                msg_box.setText("Falsches Passwort. Zugriff zur Developer Area verweigert.")
                msg_box.setIcon(QMessageBox.Icon.Warning)
                msg_box.setStyleSheet("""
                    QMessageBox {
                        background-color: #19232D;
                        color: white;
                    }
                    QMessageBox QLabel {
                        color: white;
                        font-size: 14px;
                        padding: 10px;
                    }
                    QMessageBox QPushButton {
                        background-color: #3292ea;
                        color: white;
                        padding: 8px 20px;
                        border: none;
                        border-radius: 6px;
                        font-size: 13px;
                        font-weight: bold;
                        min-width: 80px;
                        min-height: 30px;
                    }
                    QMessageBox QPushButton:hover {
                        background-color: #4da2fa;
                    }
                    QMessageBox QPushButton:pressed {
                        background-color: #2a82da;
                    }
                """)
                msg_box.exec()
        else:
            print(f"{APP_PREFIX}Developer Area access cancelled by user.")
    def open_cmd_scripts_page(self,script_key:str):
        print(f"{APP_PREFIX}Attempting to open CmdScriptsPage for script key: {script_key}")
        if not script_key:print(f"ERROR: {APP_PREFIX}No script key provided for CmdScriptsPage.");QMessageBox.warning(self,"Navigation Error","No script selected to run.");return
        if self.cmd_scripts_page is None:print(f"{APP_PREFIX}Creating CmdScriptsPage instance.");self.cmd_scripts_page=CmdScriptsPage(self);self.stacked_widget.addWidget(self.cmd_scripts_page)
        self.stacked_widget.setCurrentWidget(self.cmd_scripts_page);print(f"{APP_PREFIX}Switched to CmdScriptsPage.");self.cmd_scripts_page.run_script_by_key(script_key)
        
        # Update menu based on script origin
        if script_key == "database_manager":
            self._update_active_menu("Developer Area")
        else:
            self._update_active_menu("KISIM Scripts")
    
    def navigate_back_to_excel_viewer(self, tumorboard_name, date_str):
        """Navigate back to excel viewer page and refresh it to show timestamp"""
        print(f"{APP_PREFIX}Navigating back to Excel viewer for {tumorboard_name} on {date_str}")
        
        # Find existing Excel viewer page
        existing_page_index = self.find_page_index(ExcelViewerPage, 
                                                   entity_name=f"{tumorboard_name}_{date_str}")
        if existing_page_index is not None:
            print(f"{APP_PREFIX}Found existing Excel viewer page, switching to it.")
            self.stacked_widget.setCurrentIndex(existing_page_index)
            
            # Refresh the page to update Excel data and button state
            excel_page = self.stacked_widget.widget(existing_page_index)
            if hasattr(excel_page, 'refresh_excel_data'):
                excel_page.refresh_excel_data()
            elif hasattr(excel_page, 'refresh_finalization_state'):
                excel_page.refresh_finalization_state()
        else:
            print(f"{APP_PREFIX}Creating new Excel viewer page.")
            excel_page = ExcelViewerPage(self, tumorboard_name, date_str)
            new_index = self.stacked_widget.addWidget(excel_page)
            self.stacked_widget.setCurrentIndex(new_index)

    def handle_page_change(self,index):
        current_widget=self.stacked_widget.widget(index);page_name=current_widget.__class__.__name__ if current_widget else"None";print(f"{APP_PREFIX}Page changed to index {index}, widget: {page_name}")
        
        # Searchbar nur bei TumorGroupPage (Tumor navigator) anzeigen
        if hasattr(self, 'sop_search_widget'):
            if isinstance(current_widget, TumorGroupPage):
                self.sop_search_widget.show()
                print(f"{APP_PREFIX}Searchbar angezeigt (Tumor navigator aktiv)")
            else:
                self.sop_search_widget.hide()
                self.sop_search_widget.clear_search()  # Suchfeld leeren
                print(f"{APP_PREFIX}Searchbar versteckt")
        
        if hasattr(self,'cmd_scripts_page')and self.cmd_scripts_page is not None:
            if current_widget is not self.cmd_scripts_page:print(f"{APP_PREFIX}Navigated away from CmdScriptsPage, attempting to stop script...");self.cmd_scripts_page.stop_current_script()
            else:print(f"{APP_PREFIX}Navigated TO CmdScriptsPage, no script stop needed.")
    def _update_active_menu(self,active_item_key):
        for item_text,button in self.menu_buttons.items():button.setStyleSheet(self.active_menu_style if item_text==active_item_key else self.inactive_menu_style)
    def apply_dark_blue_theme(self):
        palette=QPalette();palette.setColor(QPalette.ColorRole.Window,QColor(25,35,45));palette.setColor(QPalette.ColorRole.WindowText,Qt.GlobalColor.white);palette.setColor(QPalette.ColorRole.Base,QColor(35,45,55));palette.setColor(QPalette.ColorRole.AlternateBase,QColor(45,55,65));palette.setColor(QPalette.ColorRole.ToolTipBase,QColor(25,35,45));palette.setColor(QPalette.ColorRole.ToolTipText,Qt.GlobalColor.white);palette.setColor(QPalette.ColorRole.Text,Qt.GlobalColor.white);palette.setColor(QPalette.ColorRole.Button,QColor(35,45,55));palette.setColor(QPalette.ColorRole.ButtonText,Qt.GlobalColor.white);palette.setColor(QPalette.ColorRole.BrightText,Qt.GlobalColor.red);palette.setColor(QPalette.ColorRole.Link,QColor(42,130,218));palette.setColor(QPalette.ColorRole.Highlight,QColor(42,130,218));palette.setColor(QPalette.ColorRole.HighlightedText,Qt.GlobalColor.black);QApplication.setPalette(palette)

def run_update_check():
    """
    Prüft auf eine neue Version der App und fragt den Benutzer,
    ob diese installiert werden soll.
    """
    try:
        # --- 1. Pfade definieren ---
        # Der neue, feste Pfad zur Remote-App-Installation
        network_app_content_path = r'K:\RAO_Projekte\App\Resources\USZ-RAO-App'
        
        # Der Pfad zur updater.bat-Datei. Es wird angenommen, dass diese nun
        # im 'Resources'-Ordner liegt, eine Ebene über dem 'USZ-RAO-App'-Ordner.
        network_resources_path = os.path.dirname(network_app_content_path)
        updater_script_path = os.path.join(network_resources_path, 'EXECUTE_ME_FOR_INSTALLING_OR_UPDATING.bat')

        local_version_file = os.path.join(os.path.dirname(__file__), 'version.txt')

        # --- 2. Netzwerk-Verfügbarkeit prüfen ---
        if not os.path.exists(network_app_content_path):
            print(f"INFO: {APP_PREFIX}Update check skipped: Network application path '{network_app_content_path}' not found.")
            return # App normal starten

        # --- 3. Versionen aus den 'version.txt' Dateien lesen ---
        remote_version_str = None
        remote_version_file = os.path.join(network_app_content_path, 'version.txt')
        
        if os.path.exists(remote_version_file):
            with open(remote_version_file, 'r') as f:
                remote_version_str = f.read().strip()

        local_version_str = None
        if os.path.exists(local_version_file):
            with open(local_version_file, 'r') as f:
                local_version_str = f.read().strip()
        
        if not remote_version_str or not local_version_str:
            print(f"WARNUNG: {APP_PREFIX}Update check skipped: version.txt file missing (Local: {local_version_str is not None}, Remote: {remote_version_str is not None}).")
            return # App normal starten

        # --- 4. Versionen vergleichen ---
        print(f"INFO: {APP_PREFIX}Version Check - Local: {local_version_str}, Remote: {remote_version_str}")
        if remote_version_str == local_version_str:
            print(f"INFO: {APP_PREFIX}Application is up to date.")
            return # Versionen sind identisch, App normal starten

        # --- 5. Update-Dialog anzeigen, wenn Versionen abweichen ---
        print(f"INFO: {APP_PREFIX}Update available. Showing dialog to user.")
        msg_box = QMessageBox()
        msg_box.setWindowTitle("Update verfügbar")
        msg_box.setText("Update verfügbar. Installation zu Stabilitätszwecken dringend empfohlen!\n\nUpdate jetzt automatisch installieren lassen? (ca. 2 min)")
        msg_box.setIcon(QMessageBox.Icon.Information)
        yes_button = msg_box.addButton("Ja", QMessageBox.ButtonRole.YesRole)
        no_button = msg_box.addButton("Nein, Update später laden", QMessageBox.ButtonRole.NoRole)
        
        # KORREKTUR 1: Setze eine Mindestbreite für die gesamte Dialogbox.
        # Dies gibt dem Layout genug Platz für den Textumbruch. Passen Sie den Wert bei Bedarf an.
        msg_box.setMinimumWidth(500)

        # Style für den Dialog (angepasst an Ihr Theme)
        msg_box.setStyleSheet("""
            QMessageBox { background-color: #19232D; }
            /* KORREKTUR 2: Keine Breitenangabe mehr für das Label, damit es flexibel bleibt. */
            QMessageBox QLabel { color: white; font-size: 14px; padding: 15px; }
            QMessageBox QPushButton {
                background-color: #37414F; color: white; padding: 8px 20px;
                border-radius: 4px; min-width: 180px; font-size: 13px; margin: 5px;
            }
            QMessageBox QPushButton:hover { background-color: #4C5A6D; }
        """)
        yes_button.setStyleSheet("background-color: #3292ea; font-weight: bold;")

        msg_box.exec()

        if msg_box.clickedButton() == yes_button:
            # --- 6. Update-Skript ausführen und App beenden ---
            if os.path.exists(updater_script_path):
                print(f"INFO: {APP_PREFIX}User accepted update. Executing: {updater_script_path}")
                try:
                    # subprocess.CREATE_NEW_CONSOLE stellt sicher, dass das Batch-Skript
                    # in einem neuen Konsolenfenster ausgeführt wird und Ihre App beendet werden kann.
                    subprocess.Popen([updater_script_path], creationflags=subprocess.CREATE_NEW_CONSOLE)
                    print(f"INFO: {APP_PREFIX}Updater launched. Exiting application.")
                    sys.exit(0) # App beenden, damit das Update durchgeführt werden kann
                except Exception as e:
                    print(f"ERROR: {APP_PREFIX}Failed to execute updater script: {e}")
                    error_msg = QMessageBox()
                    error_msg.setIcon(QMessageBox.Icon.Critical)
                    error_msg.setText(f"Das Update-Skript konnte nicht gestartet werden.\n\nFehler: {e}\n\nBitte kontaktieren Sie den Support.")
                    error_msg.setWindowTitle("Update-Fehler")
                    error_msg.exec()
                    sys.exit(1) # App mit Fehlercode beenden
            else:
                print(f"ERROR: {APP_PREFIX}Updater script not found at: {updater_script_path}")
                # Optional: Benutzer informieren, dass das Skript fehlt
                QMessageBox.critical(None, "Update-Fehler", 
                                     f"Das Update-Skript wurde nicht gefunden:\n{updater_script_path}\n\nBitte kontaktieren Sie den Support.")
                return # App normal starten, da kein Update möglich ist

        else:
            print(f"INFO: {APP_PREFIX}User declined update. Starting application normally.")
            return

    except Exception as e:
        print(f"ERROR: {APP_PREFIX}An unexpected error occurred during the update check: {e}")
        # Optional: Benutzer über den Fehler informieren
        QMessageBox.warning(None, "Update-Prüfungsfehler", 
                            f"Ein unerwarteter Fehler ist bei der Update-Prüfung aufgetreten: {e}\n\nDie Anwendung wird normal gestartet.")
        return


if __name__ == '__main__':
    print(f"{APP_PREFIX}__main__ block started.")
    QCoreApplication.setAttribute(Qt.ApplicationAttribute.AA_UseSoftwareOpenGL)
    print(f"{APP_PREFIX}Attempted to set Qt.ApplicationAttribute.AA_UseSoftwareOpenGL.")

    app = QApplication(sys.argv)
    print(f"{APP_PREFIX}QApplication instance created.")

    # UPDATE CHECK
    run_update_check()

    initialize_global_webengine_settings()
    print(f"{APP_PREFIX}Global WebEngine settings initialized.")

    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(25,35,45));palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white);palette.setColor(QPalette.ColorRole.Base, QColor(35,45,55));palette.setColor(QPalette.ColorRole.AlternateBase, QColor(45,55,65));palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(25,35,45));palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white);palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white);palette.setColor(QPalette.ColorRole.Button, QColor(55,65,75));palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white);palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red);palette.setColor(QPalette.ColorRole.Link, QColor(42,130,218));palette.setColor(QPalette.ColorRole.Highlight, QColor(42,130,218));palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.white)
    app.setPalette(palette)
    print(f"{APP_PREFIX}Application palette set.")

    app.setStyleSheet("""
        QScrollBar:vertical { border: none; background: #232F3B; width: 12px; margin: 0px; }
        QScrollBar::handle:vertical { background: #4C5A6D; min-height: 25px; border-radius: 6px; }
        QScrollBar::handle:vertical:hover { background: #5A6A7D; }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { border: none; background: none; height: 0px; width: 0px; }
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: none; }
        QScrollBar:horizontal { border: none; background: #232F3B; height: 12px; margin: 0px; }
        QScrollBar::handle:horizontal { background: #4C5A6D; min-width: 25px; border-radius: 6px; }
        QScrollBar::handle:horizontal:hover { background: #5A6A7D; }
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { border: none; background: none; width: 0px; height: 0px; }
        QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal { background: none; }
    """)
    print(f"{APP_PREFIX}Application stylesheet set.")

    today = datetime.date.today(); current_month_str = today.strftime("%Y-%m")
    current_iso_year, current_iso_week, _ = today.isocalendar()
    last_valid_month, last_valid_iso_year, last_valid_iso_week = read_license_state()
    needs_check = False
    if last_valid_month != current_month_str: needs_check = True
    license_ok = not needs_check
    if needs_check:
        print(f"{APP_PREFIX}License check needed for month {current_month_str}.")
        required_month_str = current_month_str; dialog = LicenseDialog(required_month_str)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            entered_key = dialog.get_key()
            if verify_license(PUBLIC_KEY_PEM, entered_key, required_month_str):
                write_license_state(current_month_str, current_iso_year, current_iso_week); license_ok = True
            else: 
                # Create styled error message box for better visibility with dark theme
                error_msg = QMessageBox()
                error_msg.setWindowTitle("License Error")
                error_msg.setText(f"Invalid license key for {required_month_str}.")
                error_msg.setIcon(QMessageBox.Icon.Critical)
                error_msg.setStandardButtons(QMessageBox.StandardButton.Ok)
                error_msg.setStyleSheet("""
                    QMessageBox {
                        background-color: #19232D;
                        color: white;
                    }
                    QMessageBox QLabel {
                        color: white;
                        font-size: 14px;
                        padding: 10px;
                    }
                    QMessageBox QPushButton {
                        background-color: #d32f2f;
                        color: white;
                        padding: 8px 20px;
                        border: none;
                        border-radius: 6px;
                        font-size: 13px;
                        font-weight: bold;
                        min-width: 80px;
                        min-height: 30px;
                    }
                    QMessageBox QPushButton:hover {
                        background-color: #f44336;
                    }
                    QMessageBox QPushButton:pressed {
                        background-color: #b71c1c;
                    }
                """)
                error_msg.exec()
                license_ok = False
        else: print(f"{APP_PREFIX}License dialog cancelled by user."); license_ok = False
    else: print(f"{APP_PREFIX}License check skipped for month {current_month_str} (already validated or not needed).")

    if license_ok:
        print(f"{APP_PREFIX}License check passed or was not required.")
        print(f"{APP_PREFIX}Starting TumorGuideApp...")
        window = TumorGuideApp()
        print(f"{APP_PREFIX}TumorGuideApp instance created.")
        
        def perform_initialization_workaround():
            print(f"{APP_PREFIX}perform_initialization_workaround: Scheduled actions starting.")
            
            # This workaround runs on EVERY cold start of the app.
            print(f"{APP_PREFIX}perform_initialization_workaround: Attempting PDF load workaround on this run.")
            try:
                window.attempt_first_run_pdf_load_workaround()
                # If the above call causes a restart, the code below this line in this function
                # for *this specific process* will not be reached.
                print(f"{APP_PREFIX}perform_initialization_workaround: Call to attempt_first_run_pdf_load_workaround completed in this process.")
            except Exception as e_workaround_call:
                print(f"ERROR: {APP_PREFIX}perform_initialization_workaround: Error calling attempt_first_run_pdf_load_workaround: {e_workaround_call}")
                traceback.print_exc()
            print(f"{APP_PREFIX}perform_initialization_workaround: Scheduled actions finished for this process.")

        # Window positioning and showing is handled by setup_monitor_positioning()
        print(f"{APP_PREFIX}Application window positioning completed.")
        
        # Schedule the workaround to run after the window is shown and event loop has started.
        QTimer.singleShot(200, perform_initialization_workaround) # 200ms delay

        print(f"{APP_PREFIX}Starting event loop...")
        exit_code = app.exec()
        print(f"{APP_PREFIX}Application event loop finished with exit code {exit_code}.")
        sys.exit(exit_code)
    else:
        print(f"{APP_PREFIX}Exiting due to failed or cancelled license check.")
        sys.exit(1)