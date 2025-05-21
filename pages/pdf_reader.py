import sys
import os
import logging
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QToolBar,
                             QPushButton, QApplication, QMessageBox, QLabel)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineSettings, QWebEngineProfile # Added QWebEngineProfile
from PyQt6.QtCore import Qt, QUrl, pyqtSlot
from PyQt6.QtGui import QAction, QIcon

class PdfReaderPage(QWidget):
    """A widget to display a PDF file using QWebEngineView."""
    def __init__(self, main_window, pdf_path, group_name, entity_name):
        super().__init__()
        self.main_window = main_window
        self.pdf_path = pdf_path
        self.group_name = group_name
        self.entity_name = entity_name
        logging.info(f"Initializing PdfReaderPage (WebEngine) for: {pdf_path} (Group: {group_name}, Entity: {entity_name})")

        # Initialize WebEngine settings before creating the view
        self._initialize_webengine_settings()

        # Check for WebEngine availability (should be present if import worked)
        try:
            # Basic check if the class exists
            _ = QWebEngineView()
        except NameError:
             logging.error("QWebEngineView is not available. Please ensure PyQt6-WebEngine is installed.")
             self._setup_error_ui("PDF Viewer Error: PyQtWebEngine is missing or not configured correctly.\nPlease install it: pip install PyQt6-WebEngine")
             return
        except Exception as e:
             logging.error(f"Error initializing QWebEngineView: {e}")
             self._setup_error_ui(f"PDF Viewer Error: Could not initialize WebEngine: {e}")
             return

        if not os.path.exists(pdf_path):
            logging.error(f"PDF file not found: {pdf_path}")
            self._setup_error_ui(f"Error: PDF file not found at path: {pdf_path}")
            return

        self.setup_ui()
        self.load_pdf()

    def _initialize_webengine_settings(self):
        """Initialize WebEngine settings globally."""
        try:
            # Get the default profile
            profile = QWebEngineProfile.defaultProfile()

            # Configure the profile
            profile.setPersistentCookiesPolicy(QWebEngineProfile.PersistentCookiesPolicy.NoPersistentCookies)
            profile.setHttpCacheType(QWebEngineProfile.HttpCacheType.MemoryHttpCache)

            logging.info("WebEngine settings initialized successfully")
        except Exception as e:
            logging.error(f"Error initializing WebEngine settings: {e}")
            # Continue anyway, as some settings might still work

    def _setup_error_ui(self, message):
        """Sets up the UI to display an error message."""
        layout = QVBoxLayout(self)
        error_label = QLabel(message)
        error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        error_label.setStyleSheet("color: red; font-size: 16px;")
        error_label.setWordWrap(True)
        layout.addWidget(error_label)
        self.setLayout(layout)

    def setup_ui(self):
        """Sets up the UI with QWebEngineView."""
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # --- Web Engine View ---
        try:
            self.web_view = QWebEngineView()
            # Enable the PDF viewer plugin (important!)
            self.web_view.settings().setAttribute(QWebEngineSettings.WebAttribute.PluginsEnabled, True)
            self.web_view.settings().setAttribute(QWebEngineSettings.WebAttribute.PdfViewerEnabled, True)

            # Add web view to layout
            self.main_layout.addWidget(self.web_view)
        except Exception as e:
            logging.error(f"Error creating WebEngine view: {e}")
            self._setup_error_ui(f"Error creating PDF viewer: {e}")
            return

        self.setLayout(self.main_layout)
        logging.info("PdfReaderPage (WebEngine) UI setup complete (Toolbar removed).")

    def load_pdf(self):
        """Loads the PDF file into the QWebEngineView."""
        if not hasattr(self, 'web_view'):
             logging.error("Web view not initialized, cannot load PDF.")
             return

        logging.info(f"Attempting to load PDF via WebEngine: {self.pdf_path}")
        try:
            # Convert the local file path to a QUrl
            pdf_url = QUrl.fromLocalFile(self.pdf_path)

            if not pdf_url.isValid():
                logging.error(f"Could not create valid QUrl from path: {self.pdf_path}")
                QMessageBox.warning(self, "Error", f"Could not load PDF: Invalid file path.\n{self.pdf_path}")
                return

            self.web_view.setUrl(pdf_url)
            logging.info(f"Set URL for WebEngine: {pdf_url.toString()}")
        except Exception as e:
            logging.error(f"Error loading PDF: {e}")
            self._setup_error_ui(f"Error loading PDF: {e}")