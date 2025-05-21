import os
os.environ['QTWEBENGINE_CHROMIUM_FLAGS'] = '--disable-gpu' # Disable GPU acceleration for WebEngine
from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QDialog, QLineEdit, QDialogButtonBox, QMessageBox
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QCoreApplication, QTimer
from PyQt6.QtGui import QPalette, QColor, QFont, QPixmap, QIcon
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineSettings, QWebEngineProfile
from pages.tumorgroup_pages.tumor_group_page import TumorGroupPage
from pages.entity_pages.EntityPage import EntityPage
from pages.entity_pages.sop_page import SOPPage
from pages.entity_pages.contouring_page import ContouringPage
from pages.tumorgroup_pages.neuroonkologie_page import NeuroonkologiePage
from pages.tumorgroup_pages.bindegewebstumore_page import BindegewebstumorePage
from pages.tumorgroup_pages.placeholder_group_page import PlaceholderGroupPage
from pages.kisim_page import KisimPage
from pages.cmdscripts_page import CmdScriptsPage
from pages.pdf_reader import PdfReaderPage
# Import ALL specific group pages
from pages.tumorgroup_pages.KopfHalsTumorePage import KopfHalsTumorePage
from pages.tumorgroup_pages.ThorakaleTumorePage import ThorakaleTumorePage
from pages.tumorgroup_pages.GastrointestinaleTumorePage import GastrointestinaleTumorePage
from pages.tumorgroup_pages.UrogenitaleTumorePage import UrogenitaleTumorePage
from pages.tumorgroup_pages.GynPage import GynPage
from pages.tumorgroup_pages.HauttumorePage import HauttumorePage
from pages.tumorgroup_pages.LymphomePage import LymphomePage
from pages.tumorgroup_pages.FernmetastasenPage import FernmetastasenPage
from pages.tumorgroup_pages.GutartigeErkrankungenPage import GutartigeErkrankungenPage
import sys
import datetime
import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
import json 
import logging 

# --- Windows-spezifischer Code zum Setzen des Taskleisten-Icons ---
if sys.platform == 'win32': # Nur für Windows ausführen
    try:
        import ctypes
        # Erfinden Sie eine eindeutige AppID für Ihre Anwendung
        # Format: CompanyName.ProductName.SubProduct.VersionInformation
        # Sie können hier etwas Relativ Eindeutiges wählen.
        myappid = u'USZ.RAOApp.TumorGuide.1.0' # u'String' für Unicode
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        print(f"INFO: AppUserModelID gesetzt auf: {myappid}")
    except ImportError:
        print("WARNUNG: ctypes Modul nicht gefunden. Taskleisten-Icon wird möglicherweise nicht korrekt angezeigt.")
    except AttributeError:
        print("WARNUNG: SetCurrentProcessExplicitAppUserModelID nicht verfügbar (wahrscheinlich nicht Windows). Taskleisten-Icon wird möglicherweise nicht korrekt angezeigt.")
    except Exception as e:
        print(f"WARNUNG: Fehler beim Setzen der AppUserModelID: {e}")
# --- Ende Windows-spezifischer Code ---

# --- Define persistent log path ---
try:
    # Get user's home directory
    user_home = os.path.expanduser("~")
    # Define the patdata directory (consistent with UNIVERSAL.py)
    patdata_dir = os.path.join(user_home, "patdata")
    # Create patdata directory if it doesn't exist
    os.makedirs(patdata_dir, exist_ok=True)
    # Define the log file path within patdata directory
    log_file_path = os.path.join(patdata_dir, 'usz_rao_app.log') # Changed filename slightly for clarity
    print(f"INFO: Logging to: {log_file_path}") # For console feedback
except Exception as e:
    # Fallback if patdata creation fails (e.g., permissions)
    print(f"WARNING: Could not create/use log path in patdata directory: {e}. Logging to current directory instead.")
    # Log in the directory where the script/exe is located (might be temp folder in bundle)
    # Determine base path reliably
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            # Bundled app: Use executable dir (better than temp)
            base_dir = os.path.dirname(sys.executable)
    else:
            # Development mode: Use script directory
            base_dir = os.path.dirname(os.path.abspath(__file__))
    log_file_path = os.path.join(base_dir, 'usz_rao_app_fallback.log')

# --- Configure Logging ---
logging.basicConfig(
    level=logging.INFO, # Log INFO, WARNING, ERROR, CRITICAL
    format='%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    filename=log_file_path, # Log to the defined persistent file
    filemode='w' # Overwrite the log file on each start
)
logging.info(f"--- Application Starting (Logging to: {log_file_path}) ---")

# Public Key constant - replace the content with the actual key you generated
PUBLIC_KEY_PEM = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA2IFO7yr+4s/9vlmLZXfY
vKbVBuCk0fUgWdh88jL3SiUPhHJ0MTNP1s7ZTvgIFPIzfFO5Hv/3rT/csFiB//IN
1ad1fxuClq4Rm/Y0NGA14VWqxQzRMDnvH5cAqANBoND1g5uEpL/S00Ed0eB3snse
QTLqZtf0mMyYIg30WinWrkX5C7T2KNTMp6BZGrcyeFXGBM/mwVvkRxzeUOTGCPZe
7a4heBP8p1hp1q4fpVoNBgzBJ6BSW5GjWhAKurfs1VMSde9xuJmEhb5tclYcH23s
N2UkIBZjMerEXyDVgzD+zI/6YfyeVOHiAvdAzqbLj+k167qQsT5Y3N/BJ6zz9Tvk
2QIDAQAB
-----END PUBLIC KEY-----"""

# --- Persistence File ---
LICENSE_STATE_FILE = "license_state.txt"

# --- New Global Function to Initialize WebEngine Settings ---
def initialize_global_webengine_settings():
    """Initialize WebEngine settings globally, once at startup."""
    try:
        # Get the default profile
        profile = QWebEngineProfile.defaultProfile()

        # Configure the profile (example settings, adjust as needed)
        # These settings are generally good for privacy and reducing disk cache.
        profile.setPersistentCookiesPolicy(QWebEngineProfile.PersistentCookiesPolicy.NoPersistentCookies)
        profile.setHttpCacheType(QWebEngineProfile.HttpCacheType.MemoryHttpCache)
        # Note: QWebEngineSettings.WebAttribute.PluginsEnabled and PdfViewerEnabled
        # are typically set per QWebEngineView instance, not globally on the profile.

        logging.info("Global WebEngine profile settings initialized successfully.")
    except Exception as e:
        logging.error(f"Error initializing global WebEngine profile settings: {e}", exc_info=True)
        # Depending on the severity, you might want to inform the user or exit.
        # For now, we'll log and continue.

def verify_license(public_key_pem, license_key_b64, expected_data_str):
    """Verifies the provided license key against the public key."""
    try:
        public_key = serialization.load_pem_public_key(
            public_key_pem.encode('utf-8')
        )
        signature = base64.b64decode(license_key_b64)
        expected_data = expected_data_str.encode('utf-8')

        # Verify the signature
        public_key.verify(
            signature,
            expected_data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        logging.info(f"License verification successful for data: {expected_data_str}")
        return True # Verification successful
    except Exception as e:
        # Log the specific exception
        logging.error(f"License verification failed for data '{expected_data_str}': {e}", exc_info=True)
        print(f"License verification failed: {e}") # Keep console output for immediate feedback
        return False # Verification failed

# --- Persistence Functions ---
def read_license_state():
    """Reads the last valid license month and ISO week from the state file."""
    try:
        with open(LICENSE_STATE_FILE, 'r') as f:
            state = json.load(f)
            return state.get("month", None), state.get("iso_year", None), state.get("iso_week", None)
    except (FileNotFoundError, json.JSONDecodeError):
        return None, None, None # No valid state found

def write_license_state(month_str, iso_year, iso_week):
    """Writes the current valid license month and ISO week to the state file."""
    state = {"month": month_str, "iso_year": iso_year, "iso_week": iso_week}
    try:
        with open(LICENSE_STATE_FILE, 'w') as f:
            json.dump(state, f)
            logging.info(f"Wrote license state: month={month_str}, year={iso_year}, week={iso_week}")
    except IOError as e:
        logging.error(f"Error writing license state: {e}", exc_info=True)
        print(f"Error writing license state: {e}")

class LicenseDialog(QDialog):
    """A simple dialog to ask for the monthly license key."""
    def __init__(self, month_str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("License Activation")
        self.setModal(True) # Block interaction with main window
        self.setMinimumWidth(400)

        # --- Style the dialog ---
        self.setStyleSheet("""
            QDialog {
                background-color: #19232D; /* Dark background */
            }
            QLabel {
                color: white; /* White text for labels */
                font-size: 14px;
            }
            QLineEdit {
                background-color: #232F3B; /* Slightly lighter background for input */
                color: white; /* White text for input */
                border: 1px solid #425061;
                padding: 5px;
                font-size: 14px;
            }
            QPushButton { /* Style buttons if needed - Uses QDialogButtonBox default or this */
                background-color: #37414F;
                color: white;
                padding: 8px 15px;
                border: none;
                border-radius: 3px;
                min-width: 80px; /* Ensure buttons have some width */
            }
            QPushButton:hover {
                background-color: #4C5A6D;
            }
        """)

        layout = QVBoxLayout(self)

        self.info_label = QLabel(f"Please enter the license key for {month_str}:")
        layout.addWidget(self.info_label)

        self.key_input = QLineEdit()
        self.key_input.setPlaceholderText("Enter license key here")
        layout.addWidget(self.key_input)

        # Use standard buttons, they should inherit some styling or use default system ones if stylesheet is tricky
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

    def get_key(self):
        """Returns the entered license key."""
        return self.key_input.text().strip()

class TumorGuideApp(QMainWindow):
    # ... (your existing __init__ and other methods like _create_left_menu, _create_header, etc.) ...

    def attempt_dummy_pdf_load(self): # Renamed for clarity, but still serves the "dummy load" purpose
        logging.info("TumorGuideApp: Attempting initial PDF load for WebEngine setup.")
        
        # Define the path to your existing PDF relative to main.py
        # This assumes main.py is in the root of "USZ-RAO-App"
        pdf_group = "Fernmetastasen"
        pdf_entity = "palliative RT von Knochenmetastasen"
        pdf_filename = "RT_Palliativ Knochen_03-2017.pdf"
        
        base_dir = os.path.dirname(os.path.abspath(__file__)) # Get directory of main.py
        target_pdf_path = os.path.join(base_dir, 'assets', 'sop', pdf_group, pdf_entity, pdf_filename)

        if not os.path.exists(target_pdf_path):
            logging.error(f"Target PDF for workaround not found: {target_pdf_path}")
            # Optionally show a message to the user or just log and skip the workaround.
            # For now, we'll just log and return if the specific PDF is missing.
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Icon.Warning)
            msg_box.setWindowTitle("Workaround PDF Missing")
            msg_box.setText(f"The PDF file required for an initial stability workaround was not found:\n{target_pdf_path}\n\nThe application might be unstable on first PDF open.")
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg_box.exec()
            return

        try:
            logging.info(f"Instantiating PdfReaderPage with existing PDF: {target_pdf_path}")
            # Use the group and entity names associated with this PDF for consistency
            temp_pdf_page = PdfReaderPage(self, target_pdf_path, pdf_group, pdf_entity)
            
            original_index = self.stacked_widget.currentIndex() # Store current index
            temp_idx = self.stacked_widget.addWidget(temp_pdf_page)
            self.stacked_widget.setCurrentIndex(temp_idx)
            
            # Process events to allow the page to render (and potentially trigger the issue)
            QApplication.processEvents() 
            QApplication.processEvents() # Sometimes a second call helps ensure rendering starts
            
            # Schedule cleanup. If a crash occurs, this might not run, which is fine for the workaround's purpose.
            # Increased delay slightly to give more time for rendering/crash if it's going to happen
            QTimer.singleShot(100, lambda: self._cleanup_dummy_page(temp_pdf_page, original_index)) 
            
            logging.info("Workaround PdfReaderPage added to stack and shown briefly.")

        except Exception as e:
            logging.error(f"Error during workaround PdfReaderPage instantiation/showing: {e}", exc_info=True)
            # The app will likely restart if it crashes here.

    def _cleanup_dummy_page(self, page_to_remove, index_to_restore):
        """Helper to remove the dummy/workaround page and restore original view if app didn't restart."""
        logging.info(f"Attempting to clean up workaround page. Page: {page_to_remove}, Index to restore: {index_to_restore}")
        try:
            if page_to_remove is not None and self.stacked_widget.indexOf(page_to_remove) != -1:
                self.stacked_widget.removeWidget(page_to_remove)
                page_to_remove.deleteLater() # Ensure proper Qt object deletion
                logging.info(f"Workaround PDF page {page_to_remove} removed and scheduled for deletion.")
            else:
                logging.warning(f"Workaround page {page_to_remove} not found in stack or already None during cleanup.")

            # Restore to a known good index or home
            # Ensure index_to_restore is valid before using it
            if 0 <= index_to_restore < self.stacked_widget.count() and self.stacked_widget.widget(index_to_restore) is not None:
                 self.stacked_widget.setCurrentIndex(index_to_restore)
                 logging.info(f"Restored to original index: {index_to_restore}")
            else:
                 # Fallback if original_index is no longer valid (e.g., if pages were removed)
                 self.go_home() # A safe fallback
                 logging.info("Restored to home page after workaround PDF load as original index was invalid.")
        except Exception as e_cleanup:
            logging.error(f"Error cleaning up workaround PDF page: {e_cleanup}", exc_info=True)
            self.go_home() # Fallback to ensure UI is in a known state

    def _create_left_menu(self):
        menu_frame = QFrame()
        menu_frame.setObjectName("leftMenu")
        menu_frame.setFixedWidth(230)  # Set width for the menu
        menu_frame.setStyleSheet("""
            #leftMenu {
                background-color: #1a2633;
                border-right: 1px solid #2a3642;
            }
        """)
        
        menu_layout = QVBoxLayout(menu_frame)
        menu_layout.setContentsMargins(10, 20, 10, 10)
        menu_layout.setSpacing(0)
        
        # Add USZ logo at the top of the left menu
        logo_container = QFrame()
        logo_container.setStyleSheet("background: transparent;")
        logo_layout = QVBoxLayout(logo_container)
        logo_layout.setContentsMargins(0, 0, 0, 20)  # Add some space below the logo
        logo_layout.setSpacing(5)
        
        logo_label = QLabel()
        logo_path = os.path.join(os.path.dirname(__file__), "assets", "usz_logo.png")
        if os.path.exists(logo_path):
            logo_pixmap = QPixmap(logo_path)
            logo_pixmap = logo_pixmap.scaledToHeight(50, Qt.TransformationMode.SmoothTransformation)
            logo_label.setPixmap(logo_pixmap)
        else:
            print(f"Warning: Logo not found at {logo_path}")
            logo_label.setText("USZ")
        
        dept_label = QLabel("Department of Radiation Oncology")
        dept_label.setFont(QFont("Helvetica", 11, QFont.Weight.Bold))
        dept_label.setStyleSheet("color: #00BFFF; padding: 0; margin: 0; background: transparent;")
        dept_label.setWordWrap(True)
        
        logo_layout.addWidget(logo_label, 0, Qt.AlignmentFlag.AlignLeft)
        logo_layout.addWidget(dept_label, 0, Qt.AlignmentFlag.AlignLeft)
        
        menu_layout.addWidget(logo_container)
        
        # Add separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("background-color: #2a3642; min-height: 1px; max-height: 1px;")
        menu_layout.addWidget(separator)
        menu_layout.addSpacing(20)  # Add some space after separator
        
        # Define styles for menu buttons
        self.active_menu_style = """
            QPushButton {
                background-color: #3292ea;
                color: white;
                font-weight: bold;
                font-size: 16px;
                text-align: left;
                padding-left: 15px;
                border: none;
            }
            QPushButton:hover {
                background-color: #4da2fa;
            }
        """
        
        self.inactive_menu_style = """
            QPushButton {
                background-color: transparent;
                color: white;
                font-size: 15px;
                text-align: left;
                padding-left: 15px;
                border: none;
                border-bottom: 1px solid #2a3642;
            }
            QPushButton:hover {
                background-color: #2a3642;
            }
        """
        
        # Menu items
        menu_items = ["Tumor navigator", "KISIM scripts", "Placeholder", "Placeholder", "Placeholder"]
        
        for i, item in enumerate(menu_items):
            menu_button = QPushButton(item)
            menu_button.setCursor(Qt.CursorShape.PointingHandCursor)
            menu_button.setFixedHeight(60)
            
            # First item (Tumor navigator) is active by default
            if i == 0:
                menu_button.setStyleSheet(self.active_menu_style)
                menu_button.clicked.connect(self.go_home)
            else:
                menu_button.setStyleSheet(self.inactive_menu_style)
                
                # Connect KISIM scripts button
                if item == "KISIM scripts":
                    menu_button.clicked.connect(self.open_kisim_page)
            
            # Store reference to the button
            self.menu_buttons[item] = menu_button
            
            menu_layout.addWidget(menu_button)
        
        # Add stretch to push items to the top
        menu_layout.addStretch()
        
        return menu_frame

    def _create_header(self):
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 30, 0)
        header_layout.setSpacing(0)
        header_layout.addStretch()
        return header_layout

    def _create_breadcrumb_bar(self):
        breadcrumb_layout = QHBoxLayout()
        breadcrumb_layout.setContentsMargins(0, 0, 0, 0)
        breadcrumb_layout.setSpacing(5)
        breadcrumb_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        return breadcrumb_layout

    def _clear_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def update_breadcrumb(self, index):
        self._clear_layout(self.breadcrumb_layout)
        current_widget = self.stacked_widget.widget(index)

        if current_widget is None:
            logging.warning(f"update_breadcrumb called with invalid index {index}, current_widget is None.")
            return

        main_window_ref = self 
        page_name = current_widget.__class__.__name__
        logging.info(f"Updating breadcrumb for page index {index}, type: {page_name}")

        # --- Styles --- 
        separator_style = "color: white; font-size: 20px;"
        page_label_style = "color: #3292ea; font-weight: bold; font-size: 20px;"
        page_button_style = """
            QPushButton { color: white; background: transparent; border: none; font-weight: bold; font-size: 20px; text-align: left; padding: 0; }
            QPushButton:hover { text-decoration: underline; }
        """

        # --- Helper to add separator --- 
        def add_separator():
            separator = QLabel("→")
            separator.setStyleSheet(separator_style)
            self.breadcrumb_layout.addWidget(separator)

        # --- Helper to add clickable button --- 
        def add_button(text, target_page_class, **kwargs):
            button = QPushButton(text)
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.setStyleSheet(page_button_style)
            page_idx = self.find_page_index(target_page_class, **kwargs)
            if page_idx is not None:
                button.clicked.connect(lambda checked=False, idx=page_idx: main_window_ref.stacked_widget.setCurrentIndex(idx))
            else:
                button.setEnabled(False)
                logging.warning(f"Could not find index for breadcrumb button: {text} ({target_page_class.__name__}) with args {kwargs}")
            self.breadcrumb_layout.addWidget(button)
            return button # Return button in case it needs further modification

        # --- Helper to add non-clickable label --- 
        def add_label(text):
            label = QLabel(text)
            label.setStyleSheet(page_label_style)
            self.breadcrumb_layout.addWidget(label)
            return label

        # --- Create Home Button --- 
        home_breadcrumb_btn = QPushButton()
        home_icon_path = os.path.join(os.path.dirname(__file__), "assets", "home_button.png")
        if os.path.exists(home_icon_path):
            home_icon = QPixmap(home_icon_path)
            home_icon = home_icon.scaledToHeight(60, Qt.TransformationMode.SmoothTransformation)
            home_breadcrumb_btn.setIcon(QIcon(home_icon))
            home_breadcrumb_btn.setIconSize(QSize(60, 60))
        else: home_breadcrumb_btn.setText("Home")
        home_breadcrumb_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        home_breadcrumb_btn.clicked.connect(self.go_home)
        home_breadcrumb_btn.setStyleSheet("QPushButton { background: transparent; border: none; padding: 0; margin-right: 3px; } QPushButton:hover { background-color: rgba(255, 255, 255, 30); }")
        self.breadcrumb_layout.addWidget(home_breadcrumb_btn)

        # --- Page Specific Breadcrumbs --- 
        
        # Level 1: TumorGroupPage (Initial Page) 
        if isinstance(current_widget, TumorGroupPage):
            pass # Only Home button needed

        # Level 2: Specific Group Pages 
        elif isinstance(current_widget, (NeuroonkologiePage, KopfHalsTumorePage, ThorakaleTumorePage, 
                                       GastrointestinaleTumorePage, UrogenitaleTumorePage, GynPage, 
                                       BindegewebstumorePage, HauttumorePage, LymphomePage, 
                                       FernmetastasenPage, GutartigeErkrankungenPage)):
            add_separator()
            # Use the group_name attribute we added earlier if it exists, otherwise fallback
            group_display_name = getattr(current_widget, 'group_name', page_name.replace('Page','')) 
            add_label(group_display_name)

        # Level 3: Entity Pages 
        elif isinstance(current_widget, EntityPage):
            group_name = getattr(current_widget, 'group_name', None)
            entity_name = getattr(current_widget, 'entity_name', 'Entity')
            
            if group_name:
                # Find the corresponding group page class dynamically
                group_page_class = None
                if group_name == "Neuroonkologie": group_page_class = NeuroonkologiePage
                elif group_name == "Kopf-Hals-Tumore": group_page_class = KopfHalsTumorePage
                elif group_name == "Thorakale Tumore": group_page_class = ThorakaleTumorePage
                elif group_name == "Gastrointestinale Tumore": group_page_class = GastrointestinaleTumorePage
                elif group_name == "Urogenitale Tumore": group_page_class = UrogenitaleTumorePage
                elif group_name == "Gynäkologische Tumore": group_page_class = GynPage
                elif group_name == "Bindegewebstumore": group_page_class = BindegewebstumorePage
                elif group_name == "Hauttumore": group_page_class = HauttumorePage
                elif group_name == "Lymphome": group_page_class = LymphomePage
                elif group_name == "Fernmetastasen": group_page_class = FernmetastasenPage
                elif group_name == "Gutartige Erkrankungen": group_page_class = GutartigeErkrankungenPage
                
                if group_page_class:
                    add_separator()
                    add_button(group_name, group_page_class)
                    add_separator()
                    add_label(entity_name)
                else:
                    # Fallback if group class not found (shouldn't happen)
                    add_separator()
                    add_label(group_name) # Show group name as label
                    add_separator()
                    add_label(entity_name)
            else:
                # Fallback if EntityPage doesn't have group_name
                add_separator()
                add_label(entity_name)

        # ADDED: Level 4 - PdfReaderPage
        elif isinstance(current_widget, PdfReaderPage):
            group_name = getattr(current_widget, 'group_name', None)
            entity_name = getattr(current_widget, 'entity_name', None)
            pdf_path = getattr(current_widget, 'pdf_path', None)
            pdf_filename = os.path.basename(pdf_path) if pdf_path else "PDF"

            if group_name and entity_name:
                # Find the corresponding group page class dynamically (same logic as for EntityPage)
                group_page_class = None
                if group_name == "Neuroonkologie": group_page_class = NeuroonkologiePage
                elif group_name == "Kopf-Hals-Tumore": group_page_class = KopfHalsTumorePage
                elif group_name == "Thorakale Tumore": group_page_class = ThorakaleTumorePage
                elif group_name == "Gastrointestinale Tumore": group_page_class = GastrointestinaleTumorePage
                elif group_name == "Urogenitale Tumore": group_page_class = UrogenitaleTumorePage
                elif group_name == "Gynäkologische Tumore": group_page_class = GynPage
                # elif group_name == "Bindegewebstumore": group_page_class = BindegewebstumorePage # Assuming deleted
                elif group_name == "Hauttumore": group_page_class = HauttumorePage
                elif group_name == "Lymphome": group_page_class = LymphomePage
                elif group_name == "Fernmetastasen": group_page_class = FernmetastasenPage
                elif group_name == "Gutartige Erkrankungen": group_page_class = GutartigeErkrankungenPage
                # Add other groups if necessary

                entity_page_class = EntityPage # The class for the entity level is always EntityPage

                if group_page_class and entity_page_class:
                    add_separator()
                    add_button(group_name, group_page_class)
                    add_separator()
                    # Pass necessary arguments to find the correct EntityPage instance
                    add_button(entity_name, entity_page_class, entity_name=entity_name, group_name=group_name)
                    add_separator()
                    # Display PDF filename as the final, non-clickable label
                    add_label(pdf_filename)
                else:
                    # Fallback if group class not found
                    logging.warning(f"Could not find group page class for group: {group_name} while building breadcrumb for PDF.")
                    add_separator()
                    add_label(group_name)
                    add_separator()
                    add_label(entity_name)
                    add_separator()
                    add_label(pdf_filename)
            else:
                # Fallback if PdfReaderPage missing group/entity name
                logging.warning("PdfReaderPage instance is missing group_name or entity_name for breadcrumb.")
                add_separator()
                add_label(entity_name if entity_name else "Entity")
                add_separator()
                add_label(pdf_filename)

        # Level 4: SOP/Contouring Pages 
        elif isinstance(current_widget, (SOPPage, ContouringPage)):
            group_name = getattr(current_widget, 'group_name', None)
            entity_name = getattr(current_widget, 'tumor_type', 'Entity') # Still uses tumor_type internally
            page_type_label = "SOP" if isinstance(current_widget, SOPPage) else "Contouring"
            
            if group_name and entity_name:
                 # Find the corresponding group page class dynamically
                group_page_class = None
                if group_name == "Neuroonkologie": group_page_class = NeuroonkologiePage
                elif group_name == "Kopf-Hals-Tumore": group_page_class = KopfHalsTumorePage
                elif group_name == "Thorakale Tumore": group_page_class = ThorakaleTumorePage
                elif group_name == "Gastrointestinale Tumore": group_page_class = GastrointestinaleTumorePage
                elif group_name == "Urogenitale Tumore": group_page_class = UrogenitaleTumorePage
                elif group_name == "Gynäkologische Tumore": group_page_class = GynPage
                elif group_name == "Bindegewebstumore": group_page_class = BindegewebstumorePage
                elif group_name == "Hauttumore": group_page_class = HauttumorePage
                elif group_name == "Lymphome": group_page_class = LymphomePage
                elif group_name == "Fernmetastasen": group_page_class = FernmetastasenPage
                elif group_name == "Gutartige Erkrankungen": group_page_class = GutartigeErkrankungenPage

                if group_page_class:
                    add_separator()
                    add_button(group_name, group_page_class)
                    add_separator()
                    # Pass group_name when finding EntityPage index for disambiguation if needed
                    add_button(entity_name, EntityPage, entity_name=entity_name, group_name=group_name)
                    add_separator()
                    add_label(page_type_label)
                else:
                     # Fallback if group class not found
                     add_separator()
                     add_label(group_name)
                     add_separator()
                     add_label(entity_name)
                     add_separator()
                     add_label(page_type_label)
            else:
                # Fallback if SOP/Contouring page missing group/entity name
                add_separator()
                add_label(entity_name) 
                add_separator()
                add_label(page_type_label)

        # --- KISIM / CmdScripts --- 
        elif isinstance(current_widget, KisimPage):
            add_separator()
            add_label("KISIM Scripts")
        elif isinstance(current_widget, CmdScriptsPage):
            add_separator()
            add_button("KISIM Scripts", KisimPage)
            add_separator()
            # Get the current text from the title_label of the CmdScriptsPage instance
            script_name_full = getattr(current_widget.title_label, 'text', lambda: "Script Output")() # Call text()
            if " (" in script_name_full: # Clean up status like " (Running)" or " (Finished OK)"
                script_name = script_name_full.split(" (")[0]
            else:
                script_name = script_name_full
            if not script_name or script_name.startswith("Error:") or script_name == "Script Output": # Fallback if title is not set or is an error
                script_name = "Script Output" # Default if something went wrong with title
            add_label(script_name)
            
        # --- Fallback for any other page type --- 
        else:
            add_separator()
            add_label(page_name.replace('Page',''))

        self.breadcrumb_layout.addStretch() 

    def find_page_index(self, page_type, entity_name=None, group_name=None):
        """Find the index of a page in the stack, optionally matching name and group."""
        for i in range(self.stacked_widget.count()):
            widget = self.stacked_widget.widget(i)
            if isinstance(widget, page_type):
                match = True
                # Check entity name if provided
                if entity_name is not None:
                    # Check against different possible attribute names
                    widget_entity_name = getattr(widget, 'entity_name', None)
                    widget_tumor_type = getattr(widget, 'tumor_type', None) # For SOP/Contouring backward compat?
                    widget_group_name_attr = getattr(widget, 'group_name', None) # Check group_name attr if page_type is PlaceholderGroupPage
                    
                    if not (widget_entity_name == entity_name or 
                            widget_tumor_type == entity_name or 
                            (isinstance(widget, PlaceholderGroupPage) and widget_group_name_attr == entity_name)): # Allow matching placeholder by group name
                        match = False
                
                # Check group name if provided (for disambiguation, e.g., if same entity name existed in multiple groups)
                if match and group_name is not None:
                     widget_group = getattr(widget, 'group_name', None)
                     if widget_group != group_name:
                         match = False
                         
                if match:
                    return i
        return None # Not found

    def go_home(self):
        """Navigate to the initial page (now TumorGroupPage)."""
        # Ensure the initial page (TumorGroupPage) exists at index 0
        if self.stacked_widget.count() > 0 and isinstance(self.stacked_widget.widget(0), TumorGroupPage):
            self.stacked_widget.setCurrentIndex(0)
            self._update_active_menu("Home") # Keep highlighting "Home" in menu if desired
            logging.info("Navigated to TumorGroupPage (Home).")
        else:
            # Fallback or error handling if the initial page isn't the expected type
            logging.warning("Could not navigate home, initial page is not TumorGroupPage or doesn't exist.")
            # Optionally, recreate it if missing:
            # self.tumor_group_page = TumorGroupPage(self)
            # self.stacked_widget.insertWidget(0, self.tumor_group_page)
            # self.stacked_widget.setCurrentIndex(0)

    def open_kisim_page(self):
        # Check if KISIM page already exists
        if self.kisim_page is None:
            logging.info("Creating KisimPage instance.")
            self.kisim_page = KisimPage(self)
            self.stacked_widget.addWidget(self.kisim_page)
        else:
            logging.info("KisimPage instance already exists.")

        self.stacked_widget.setCurrentWidget(self.kisim_page)
        # Update active menu button
        self._update_active_menu("KISIM scripts") # Ensure key matches menu item text
        logging.info("Navigated to KISIM Scripts page.")

    # Add method to open and run scripts on the CmdScriptsPage
    def open_cmd_scripts_page(self, script_key: str):
        """Navigates to the CmdScriptsPage and tells it which script to run."""
        logging.info(f"Attempting to open CmdScriptsPage for script key: {script_key}")
        if not script_key:
            logging.error("No script key provided for CmdScriptsPage.")
            # Optionally show an error message to the user
            QMessageBox.warning(self, "Navigation Error", "No script selected to run.")
            return

        # Check if CmdScriptsPage already exists, create if not
        if self.cmd_scripts_page is None:
            logging.info("Creating CmdScriptsPage instance.")
            self.cmd_scripts_page = CmdScriptsPage(self)
            self.stacked_widget.addWidget(self.cmd_scripts_page)
            # Set initial state if needed (though run_script_by_key handles clearing)
            # self.cmd_scripts_page.set_initial_state()
        else:
            logging.info("CmdScriptsPage instance already exists.")

        # Switch to the CmdScriptsPage
        self.stacked_widget.setCurrentWidget(self.cmd_scripts_page)
        logging.info(f"Switched to CmdScriptsPage.")

        # Run the script associated with the key
        self.cmd_scripts_page.run_script_by_key(script_key) # This method should also log start

        # Optional: Update active menu button if CmdScriptsPage should have its own menu item
        # If it's just a detail view of KISIM, keep KISIM active:
        self._update_active_menu("KISIM scripts")
        logging.info("Updated active menu to 'KISIM scripts'.")
        # Or, if it needs its own button (add button first):
        # self._update_active_menu("Script Runner")

    def handle_page_change(self, index):
        """Stops the script on CmdScriptsPage if navigating away from it."""
        current_widget = self.stacked_widget.widget(index)
        page_name = current_widget.__class__.__name__ if current_widget else "None"
        logging.info(f"Page changed to index {index}, widget: {page_name}")

        # Check if cmd_scripts_page exists and is initialized
        if hasattr(self, 'cmd_scripts_page') and self.cmd_scripts_page is not None:
            # If the newly selected widget is NOT the cmd_scripts_page, stop the script
            if current_widget is not self.cmd_scripts_page:
                logging.info("Navigated away from CmdScriptsPage, attempting to stop script...") # Debug print
                self.cmd_scripts_page.stop_current_script() # This method should log success/failure
            else:
                 logging.info("Navigated TO CmdScriptsPage, no script stop needed.")
        else:
            logging.debug("CmdScriptsPage not initialized or doesn't exist, no script stop needed.")

    def _update_active_menu(self, active_item):
        """Update menu button styles to highlight the active item."""
        for item, button in self.menu_buttons.items():
            if item == active_item:
                button.setStyleSheet(self.active_menu_style)
            else:
                button.setStyleSheet(self.inactive_menu_style)

    def apply_dark_blue_theme(self):
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(25, 35, 45))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.Base, QColor(35, 45, 55))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(45, 55, 65))
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(25, 35, 45))
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.Text, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.Button, QColor(35, 45, 55))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
        
        QApplication.setPalette(palette)

if __name__ == '__main__':
    app = QApplication(sys.argv)

    initialize_global_webengine_settings()

    # Apply theme before creating any widgets
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(25, 35, 45))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.Base, QColor(35, 45, 55))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(45, 55, 65))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(25, 35, 45))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.Text, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.Button, QColor(55, 65, 75)) # Slightly lighter buttons for dialog?
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
    app.setPalette(palette) # Apply palette to the application

    # --- Apply Global Stylesheet (including ScrollBar) ---
    app.setStyleSheet("""
        QScrollBar:vertical {
            border: none;
            background: #232F3B; /* Slightly lighter dark background for the track */
            width: 12px;
            margin: 0px 0px 0px 0px;
        }
        QScrollBar::handle:vertical {
            background: #4C5A6D; /* Color for the handle */
            min-height: 25px;
            border-radius: 6px;
        }
        QScrollBar::handle:vertical:hover {
            background: #5A6A7D; /* Slightly lighter on hover */
        }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            border: none;
            background: none;
            height: 0px; /* Hide arrow buttons */
            width: 0px;
        }
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
            background: none;
        }

        /* Horizontal Scrollbar (if ever needed) */
        QScrollBar:horizontal {
            border: none;
            background: #232F3B;
            height: 12px;
            margin: 0px 0px 0px 0px;
        }
        QScrollBar::handle:horizontal {
            background: #4C5A6D;
            min-width: 25px;
            border-radius: 6px;
        }
         QScrollBar::handle:horizontal:hover {
            background: #5A6A7D;
        }
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
            border: none;
            background: none;
            width: 0px;
            height: 0px;
        }
        QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
            background: none;
        }
    """)

    # --- License Check (Weekly Logic) ---
    today = datetime.date.today()
    current_month_str = today.strftime("%Y-%m")
    current_iso_year, current_iso_week, _ = today.isocalendar()

    last_valid_month, last_valid_iso_year, last_valid_iso_week = read_license_state()

    needs_check = False
    if last_valid_month != current_month_str:
        print(f"License check needed: Month changed (Current: {current_month_str}, Last valid: {last_valid_month}).")
        needs_check = True
    else:
        print(f"License check skipped: Already validated for {current_month_str}.")

    license_ok = not needs_check # Assume ok if check is not needed

    if needs_check:
        # --- Perform the check ---
        # We use the current month string for the check now
        required_month_str = current_month_str
        print(f"Requesting license key for {required_month_str}")

        dialog = LicenseDialog(required_month_str)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            entered_key = dialog.get_key()
            if verify_license(PUBLIC_KEY_PEM, entered_key, required_month_str):
                print(f"License key accepted for {required_month_str}.")
                write_license_state(current_month_str, current_iso_year, current_iso_week)
                license_ok = True # Explicitly set license to OK
            else:
                # Invalid key
                QMessageBox.critical(None, "License Error", f"Invalid license key provided for {required_month_str}.")
                license_ok = False # Ensure license is marked as not OK
        else:
            # Dialog cancelled
            print("License dialog cancelled by user.")
            license_ok = False # Ensure license is marked as not OK

    # --- Start application only if license is OK ---
    if license_ok:
        logging.info("License check passed or was not required.")
        print("Starting TumorGuideApp...")
        logging.info("Creating main application window.")
        window = TumorGuideApp()
        window.show()
        logging.info("Application window shown. Starting event loop.")
        exit_code = app.exec()
        logging.info(f"Application event loop finished with exit code {exit_code}.")
        sys.exit(exit_code)
    else:
        print("Exiting due to failed or cancelled license check.")
        logging.warning("Exiting due to failed or cancelled license check.")
        sys.exit(1)
