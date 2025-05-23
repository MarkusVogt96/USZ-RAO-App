import os
os.environ['QTWEBENGINE_CHROMIUM_FLAGS'] = '--disable-gpu'

from PyQt6.QtWidgets import (QApplication, QMainWindow, QStackedWidget, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QPushButton, QFrame, QDialog,
                             QLineEdit, QDialogButtonBox, QMessageBox)
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QCoreApplication, QTimer, QUrl
from PyQt6.QtGui import QPalette, QColor, QFont, QPixmap, QIcon
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineSettings, QWebEngineProfile

# Page Imports (ensure these paths are correct relative to main.py)
from pages.tumorgroup_pages.tumor_group_page import TumorGroupPage
from pages.entity_pages.EntityPage import EntityPage
from pages.entity_pages.sop_page import SOPPage
from pages.entity_pages.contouring_page import ContouringPage

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
from pages.tumorboards_overview_page import TumorboardsOverviewPage
from pages.specific_tumorboard_page import SpecificTumorboardPage
from pages.tumorboard_excel_view_page import TumorboardExcelViewPage

from pages.kisim_page import KisimPage
from pages.cmdscripts_page import CmdScriptsPage
from pages.pdf_reader import PdfReaderPage

# Standard Library Imports
import sys
import datetime
import base64
import json
import traceback

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
        self.setMinimumSize(1600, 900)
        self.setWindowTitle("USZ-RAO-App_closed-beta_stable")
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
        header_layout = self._create_header(); self.content_layout.addLayout(header_layout)
        self.breadcrumb_layout = self._create_breadcrumb_bar(); self.content_layout.addLayout(self.breadcrumb_layout)
        self.stacked_widget = QStackedWidget(); self.content_layout.addWidget(self.stacked_widget)
        self.main_layout.addWidget(content_widget); self.setCentralWidget(main_widget)
        self.tumor_group_page = TumorGroupPage(self); self.stacked_widget.addWidget(self.tumor_group_page)
        self.kisim_page = None; self.cmd_scripts_page = None; self.tumorboards_overview_page = None
        self.stacked_widget.currentChanged.connect(self.update_breadcrumb)
        self.stacked_widget.currentChanged.connect(self.handle_page_change)
        
        QTimer.singleShot(10, self._initialize_sacrificial_webengine_html_only)

        self.apply_dark_blue_theme()
        self.update_breadcrumb(0)
        print(f"{APP_PREFIX}TumorGuideApp initialization complete.")

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
        menu_frame=QFrame();menu_frame.setObjectName("leftMenu");menu_frame.setFixedWidth(230);menu_frame.setStyleSheet("#leftMenu { background-color: #1a2633; border-right: 1px solid #2a3642; }");menu_layout=QVBoxLayout(menu_frame);menu_layout.setContentsMargins(10,20,10,10);menu_layout.setSpacing(0);logo_container=QFrame();logo_container.setStyleSheet("background: transparent;");logo_layout=QVBoxLayout(logo_container);logo_layout.setContentsMargins(0,0,0,20);logo_layout.setSpacing(5);logo_label=QLabel();logo_path=os.path.join(os.path.dirname(__file__),"assets","usz_logo.png");
        if os.path.exists(logo_path):logo_label.setPixmap(QPixmap(logo_path).scaledToHeight(50,Qt.TransformationMode.SmoothTransformation))
        else:logo_label.setText("USZ")
        dept_label=QLabel("Department of Radiation Oncology");dept_label.setFont(QFont("Helvetica",11,QFont.Weight.Bold));dept_label.setStyleSheet("color: #00BFFF; padding: 0; margin: 0; background: transparent;");dept_label.setWordWrap(True);logo_layout.addWidget(logo_label,0,Qt.AlignmentFlag.AlignLeft);logo_layout.addWidget(dept_label,0,Qt.AlignmentFlag.AlignLeft);menu_layout.addWidget(logo_container);separator=QFrame();separator.setFrameShape(QFrame.Shape.HLine);separator.setStyleSheet("background-color: #2a3642; min-height: 1px; max-height: 1px;");menu_layout.addWidget(separator);menu_layout.addSpacing(20)
        self.active_menu_style="QPushButton { background-color: #3292ea; color: white; font-weight: bold; font-size: 16px; text-align: left; padding-left: 15px; border: none; } QPushButton:hover { background-color: #4da2fa; }";self.inactive_menu_style="QPushButton { background-color: transparent; color: white; font-size: 15px; text-align: left; padding-left: 15px; border: none; border-bottom: 1px solid #2a3642; } QPushButton:hover { background-color: #2a3642; }"
        menu_items=["Tumor navigator","KISIM scripts","Tumorboards","Placeholder","Placeholder"]
        for i,item_text in enumerate(menu_items):
            menu_button=QPushButton(item_text);menu_button.setCursor(Qt.CursorShape.PointingHandCursor);menu_button.setFixedHeight(60)
            if i==0:menu_button.setStyleSheet(self.active_menu_style);menu_button.clicked.connect(self.go_home)
            elif item_text == "Tumorboards": 
                menu_button.clicked.connect(self.open_tumorboards_overview_page)
            else:
                menu_button.setStyleSheet(self.inactive_menu_style)
                if item_text=="KISIM scripts":menu_button.clicked.connect(self.open_kisim_page)
            self.menu_buttons[item_text]=menu_button;menu_layout.addWidget(menu_button)
        menu_layout.addStretch();return menu_frame
    def _create_header(self): header_layout=QHBoxLayout();header_layout.setContentsMargins(0,0,30,0);header_layout.setSpacing(0);header_layout.addStretch();return header_layout
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
            if page_idx is not None:button.clicked.connect(lambda checked=False,idx=page_idx:self.stacked_widget.setCurrentIndex(idx))
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
        elif isinstance(current_widget,KisimPage):add_separator();add_label("KISIM Scripts")
        elif isinstance(current_widget,CmdScriptsPage):
            add_separator();add_button("KISIM Scripts",KisimPage);add_separator();script_name_full=getattr(current_widget.title_label,'text',lambda:"Script Output")();script_name=script_name_full.split(" (")[0] if " (" in script_name_full else script_name_full
            if not script_name or script_name.startswith("Error:")or script_name=="Script Output":script_name="Script Output"
            add_label(script_name)
        elif isinstance(current_widget, TumorboardsOverviewPage): # NEU
            add_separator()
            add_label("Tumorboards")
        elif isinstance(current_widget, SpecificTumorboardPage): # NEU
            board_name = getattr(current_widget.board_info, 'get', lambda k,d: d)('name', 'Board Detail') # Sicherer Zugriff
            add_separator()
            add_button("Tumorboards", TumorboardsOverviewPage)
            add_separator()
            add_label(board_name)
        elif isinstance(current_widget, TumorboardExcelViewPage): # NEU
            board_name = getattr(current_widget, 'board_name', 'Board')
            excel_date = getattr(current_widget, 'excel_file_date', 'Liste')
            # Finde die übergeordnete SpecificTumorboardPage (braucht board_folder_name)
            # Dies ist etwas tricky, da wir die board_info der SpecificPage hier nicht direkt haben.
            # Wir könnten den date_folder_path verwenden, um die board_info zu rekonstruieren, falls nötig.
            # Einfacher: Knopf zur Tumorboard-Übersichtsseite und dann den Namen des Boards
            add_separator()
            add_button("Tumorboards", TumorboardsOverviewPage)
            # Den spezifischen Board-Namen als Button zu machen, erfordert, die board_info zu kennen
            # oder die SpecificTumorboardPage-Instanz zu finden.
            # Fürs Erste: Button zum spezifischen Board (wenn wir die Instanz finden könnten)
            # oder Label, wenn nicht.
            # Nehmen wir an, SpecificTumorboardPage speichert `board_folder_name`
            
            # Den parent_board_folder_name aus dem date_folder_path extrahieren
            parent_board_folder_name = os.path.basename(os.path.dirname(current_widget.date_folder_path))

            add_separator()
            # Button zur SpecificTumorboardPage, die diesen Ordner verwaltet
            add_button(board_name, SpecificTumorboardPage, board_folder_name=parent_board_folder_name)
            add_separator()
            add_label(f"Liste vom {excel_date}")
        else:add_separator();add_label(page_name.replace('Page',''))
        self.breadcrumb_layout.addStretch()
    def find_page_index(self, page_type, entity_name=None, group_name=None, **kwargs):
        for i in range(self.stacked_widget.count()):
            widget=self.stacked_widget.widget(i)
            if isinstance(widget, page_type):
                match=True
                if entity_name is not None:
                    widget_entity_name=getattr(widget,'entity_name',getattr(widget,'tumor_type',None));widget_group_name_attr=getattr(widget,'group_name',None)
                    if not(widget_entity_name==entity_name or(isinstance(widget,PlaceholderGroupPage)and widget_group_name_attr==entity_name)):match=False
                if match and group_name is not None and getattr(widget,'group_name',None)!=group_name:match=False
                if match:return i
            if isinstance(widget, page_type):
                match = True
                # Check entity name if provided (für SOPPage, ContouringPage, EntityPage)
                if entity_name is not None and hasattr(widget, 'entity_name'):
                    if getattr(widget, 'entity_name', None) != entity_name: match = False
                elif entity_name is not None and hasattr(widget, 'tumor_type'): # Für SOP/Contouring
                    if getattr(widget, 'tumor_type', None) != entity_name: match = False
                
                # Check group name if provided (für SOPPage, ContouringPage, EntityPage)
                if match and group_name is not None and hasattr(widget, 'group_name'):
                    if getattr(widget, 'group_name', None) != group_name: match = False

                # NEU: Check für SpecificTumorboardPage
                if match and page_type == SpecificTumorboardPage and hasattr(kwargs, 'get'): # Sicherstellen, dass kwargs ein Dict ist
                    board_folder_name_arg = kwargs.get('board_folder_name')
                    if board_folder_name_arg is not None and getattr(widget, 'board_folder_name', None) != board_folder_name_arg:
                        match = False
                
                # NEU: Check für TumorboardExcelViewPage
                if match and page_type == TumorboardExcelViewPage and hasattr(kwargs, 'get'):
                    date_folder_path_arg = kwargs.get('date_folder_path')
                    if date_folder_path_arg is not None and getattr(widget, 'date_folder_path', None) != date_folder_path_arg:
                        match = False
                        
                if match:
                    return i
            return None
        return None
    def go_home(self):
        if self.stacked_widget.count()>0 and isinstance(self.stacked_widget.widget(0),TumorGroupPage):self.stacked_widget.setCurrentIndex(0);self._update_active_menu("Tumor navigator");print(f"{APP_PREFIX}Navigated to TumorGroupPage (Home).")
        else:print(f"WARNUNG: {APP_PREFIX}Could not navigate home, initial page is not TumorGroupPage or doesn't exist.")
    def open_kisim_page(self):
        if self.kisim_page is None:print(f"{APP_PREFIX}Creating KisimPage instance.");self.kisim_page=KisimPage(self);self.stacked_widget.addWidget(self.kisim_page)
        self.stacked_widget.setCurrentWidget(self.kisim_page);self._update_active_menu("KISIM scripts");print(f"{APP_PREFIX}Navigated to KISIM Scripts page.")
    def open_cmd_scripts_page(self,script_key:str):
        print(f"{APP_PREFIX}Attempting to open CmdScriptsPage for script key: {script_key}")
        if not script_key:print(f"ERROR: {APP_PREFIX}No script key provided for CmdScriptsPage.");QMessageBox.warning(self,"Navigation Error","No script selected to run.");return
        if self.cmd_scripts_page is None:print(f"{APP_PREFIX}Creating CmdScriptsPage instance.");self.cmd_scripts_page=CmdScriptsPage(self);self.stacked_widget.addWidget(self.cmd_scripts_page)
        self.stacked_widget.setCurrentWidget(self.cmd_scripts_page);print(f"{APP_PREFIX}Switched to CmdScriptsPage.");self.cmd_scripts_page.run_script_by_key(script_key);self._update_active_menu("KISIM scripts")
    def open_tumorboards_overview_page(self):
        print(f"{APP_PREFIX}Opening Tumorboards Overview Page...")
        if self.tumorboards_overview_page is None:
            print(f"{APP_PREFIX}Creating TumorboardsOverviewPage instance.")
            self.tumorboards_overview_page = TumorboardsOverviewPage(self)
            self.stacked_widget.addWidget(self.tumorboards_overview_page)
        
        self.stacked_widget.setCurrentWidget(self.tumorboards_overview_page)
        self._update_active_menu("Tumorboards")
        print(f"{APP_PREFIX}Navigated to Tumorboards Overview Page.")

    def open_specific_tumorboard_page(self, board_info):
        board_folder_name = board_info.get('folder_name', 'UnknownBoard')
        print(f"{APP_PREFIX}Opening Specific Tumorboard Page for folder: {board_folder_name}")
        
        # Dynamischer Import hier, um Circular Import beim Start zu vermeiden
        from pages.specific_tumorboard_page import SpecificTumorboardPage

        # Jede SpecificTumorboardPage ist einzigartig pro board_folder_name
        page_index = self.find_page_index(SpecificTumorboardPage, board_folder_name=board_folder_name)

        if page_index is not None:
            print(f"{APP_PREFIX}Found existing SpecificTumorboardPage for {board_folder_name}, switching.")
            self.stacked_widget.setCurrentIndex(page_index)
        else:
            print(f"{APP_PREFIX}Creating new SpecificTumorboardPage for {board_folder_name}.")
            specific_page = SpecificTumorboardPage(self, board_info)
            new_index = self.stacked_widget.addWidget(specific_page)
            self.stacked_widget.setCurrentIndex(new_index)
        self._update_active_menu("Tumorboards") # Behalte "Tumorboards" im Hauptmenü aktiv

    def open_tumorboard_excel_view_page(self, date_folder_path, excel_file_name, board_name):
        print(f"{APP_PREFIX}Opening Tumorboard Excel View Page for: {excel_file_name} in {date_folder_path}")
        
        # Dynamischer Import
        from pages.tumorboard_excel_view_page import TumorboardExcelViewPage

        # Jede ExcelViewPage ist einzigartig pro date_folder_path
        page_index = self.find_page_index(TumorboardExcelViewPage, date_folder_path=date_folder_path)

        if page_index is not None:
            print(f"{APP_PREFIX}Found existing TumorboardExcelViewPage for {date_folder_path}, switching.")
            self.stacked_widget.setCurrentIndex(page_index)
        else:
            print(f"{APP_PREFIX}Creating new TumorboardExcelViewPage for {date_folder_path}.")
            excel_page = TumorboardExcelViewPage(self, date_folder_path, excel_file_name, board_name)
            new_index = self.stacked_widget.addWidget(excel_page)
            self.stacked_widget.setCurrentIndex(new_index)
        self._update_active_menu("Tumorboards") # Behalte "Tumorboards" im Hauptmenü aktiv
    def handle_page_change(self,index):
        current_widget=self.stacked_widget.widget(index);page_name=current_widget.__class__.__name__ if current_widget else"None";print(f"{APP_PREFIX}Page changed to index {index}, widget: {page_name}")
        if hasattr(self,'cmd_scripts_page')and self.cmd_scripts_page is not None:
            if current_widget is not self.cmd_scripts_page:print(f"{APP_PREFIX}Navigated away from CmdScriptsPage, attempting to stop script...");self.cmd_scripts_page.stop_current_script()
            else:print(f"{APP_PREFIX}Navigated TO CmdScriptsPage, no script stop needed.")
    def _update_active_menu(self,active_item_key):
        for item_text,button in self.menu_buttons.items():button.setStyleSheet(self.active_menu_style if item_text==active_item_key else self.inactive_menu_style)
    def apply_dark_blue_theme(self):
        palette=QPalette();palette.setColor(QPalette.ColorRole.Window,QColor(25,35,45));palette.setColor(QPalette.ColorRole.WindowText,Qt.GlobalColor.white);palette.setColor(QPalette.ColorRole.Base,QColor(35,45,55));palette.setColor(QPalette.ColorRole.AlternateBase,QColor(45,55,65));palette.setColor(QPalette.ColorRole.ToolTipBase,QColor(25,35,45));palette.setColor(QPalette.ColorRole.ToolTipText,Qt.GlobalColor.white);palette.setColor(QPalette.ColorRole.Text,Qt.GlobalColor.white);palette.setColor(QPalette.ColorRole.Button,QColor(35,45,55));palette.setColor(QPalette.ColorRole.ButtonText,Qt.GlobalColor.white);palette.setColor(QPalette.ColorRole.BrightText,Qt.GlobalColor.red);palette.setColor(QPalette.ColorRole.Link,QColor(42,130,218));palette.setColor(QPalette.ColorRole.Highlight,QColor(42,130,218));palette.setColor(QPalette.ColorRole.HighlightedText,Qt.GlobalColor.black);QApplication.setPalette(palette)



if __name__ == '__main__':
    print(f"{APP_PREFIX}__main__ block started.")
    QCoreApplication.setAttribute(Qt.ApplicationAttribute.AA_UseSoftwareOpenGL)
    print(f"{APP_PREFIX}Attempted to set Qt.ApplicationAttribute.AA_UseSoftwareOpenGL.")

    app = QApplication(sys.argv)
    print(f"{APP_PREFIX}QApplication instance created.")

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
            else: QMessageBox.critical(None, "License Error", f"Invalid license key for {required_month_str}."); license_ok = False
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

        window.show()
        print(f"{APP_PREFIX}Application window shown.")
        
        # Schedule the workaround to run after the window is shown and event loop has started.
        QTimer.singleShot(200, perform_initialization_workaround) # 200ms delay

        print(f"{APP_PREFIX}Starting event loop...")
        exit_code = app.exec()
        print(f"{APP_PREFIX}Application event loop finished with exit code {exit_code}.")
        sys.exit(exit_code)
    else:
        print(f"{APP_PREFIX}Exiting due to failed or cancelled license check.")
        sys.exit(1)