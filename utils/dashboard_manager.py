import os
import shutil
import logging
from pathlib import Path
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QMessageBox, QApplication
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl, QTimer, pyqtSignal, Qt
from .dashboard_data_export import DashboardDataExporter

class DashboardManager(QWidget):
    """Dashboard manager widget for the main application"""
    
    data_updated = pyqtSignal()
    
    def __init__(self, parent=None, tumorboard_base_path=None):
        super().__init__(parent)
        
        # Determine correct tumorboard base path
        if tumorboard_base_path is None:
            # Try K: first, fall back to user home
            k_path = Path("K:/RAO_Projekte/App/tumorboards")
            if k_path.exists() and k_path.is_dir():
                tumorboard_base_path = k_path
            else:
                tumorboard_base_path = Path.home() / "tumorboards"
        
        self.tumorboard_base_path = tumorboard_base_path
        self.exporter = DashboardDataExporter(tumorboard_base_path)
        self.dashboard_dir = tumorboard_base_path / "__SQLite_database" / "dashboard"
        self.data_file = self.dashboard_dir / "dashboard_data.json"
        self.html_file = self.dashboard_dir / "dashboard.html"
        
        self.setup_ui()
        self.setup_dashboard_files()
        
        # Auto-refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_data)
        
    def setup_ui(self):
        """Setup the dashboard UI"""
        layout = QVBoxLayout(self)
        
        # Header with controls
        header_layout = QHBoxLayout()
        
        self.title_label = QLabel("📊 Tumorboard Analytics Dashboard")
        self.title_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #2E7D32;
                padding: 10px;
            }
        """)
        
        self.refresh_btn = QPushButton("🔄 Daten aktualisieren")
        self.refresh_btn.clicked.connect(self.refresh_data)
        self.refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        
        self.auto_refresh_btn = QPushButton("⏰ Auto-Refresh")
        self.auto_refresh_btn.setCheckable(True)
        self.auto_refresh_btn.clicked.connect(self.toggle_auto_refresh)
        self.auto_refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:checked {
                background-color: #FF9800;
            }
        """)
        
        self.status_label = QLabel("Bereit")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #666;
                padding: 10px;
            }
        """)
        
        header_layout.addWidget(self.title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.status_label)
        header_layout.addWidget(self.auto_refresh_btn)
        header_layout.addWidget(self.refresh_btn)
        
        layout.addLayout(header_layout)
        
        # Web view for dashboard
        self.web_view = QWebEngineView()
        self.web_view.setMinimumHeight(600)
        layout.addWidget(self.web_view)
        
        # Load dashboard
        self.load_dashboard()
        
    def setup_dashboard_files(self):
        """Setup dashboard directory and copy HTML template"""
        try:
            # Create dashboard directory
            self.dashboard_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy HTML template to dashboard directory
            template_path = Path(__file__).parent.parent / "templates" / "dashboard_simple.html"
            if template_path.exists():
                shutil.copy2(template_path, self.html_file)
                logging.info(f"Dashboard template copied to: {self.html_file}")
            else:
                logging.warning(f"Dashboard template not found at: {template_path}")
                
        except Exception as e:
            logging.error(f"Error setting up dashboard files: {e}")
            
    def load_dashboard(self):
        """Load the dashboard in the web view"""
        try:
            if self.html_file.exists():
                url = QUrl.fromLocalFile(str(self.html_file))
                self.web_view.load(url)
                self.status_label.setText("Dashboard geladen")
            else:
                self.show_error("Dashboard-Datei nicht gefunden")
                
        except Exception as e:
            logging.error(f"Error loading dashboard: {e}")
            self.show_error(f"Fehler beim Laden des Dashboards: {e}")
            
    def refresh_data(self):
        """Refresh dashboard data"""
        try:
            self.status_label.setText("Aktualisiere Daten...")
            self.refresh_btn.setEnabled(False)
            
            # Export fresh data
            output_path = self.exporter.export_dashboard_data(self.data_file)
            
            if output_path:
                # Reload the web view to pick up new data
                self.web_view.reload()
                self.status_label.setText(f"Daten aktualisiert: {Path(output_path).stat().st_mtime}")
                self.data_updated.emit()
                logging.info("Dashboard data refreshed successfully")
            else:
                self.show_error("Fehler beim Exportieren der Daten")
                
        except Exception as e:
            logging.error(f"Error refreshing dashboard data: {e}")
            self.show_error(f"Fehler beim Aktualisieren: {e}")
            
        finally:
            self.refresh_btn.setEnabled(True)
            
    def toggle_auto_refresh(self):
        """Toggle auto-refresh functionality"""
        if self.auto_refresh_btn.isChecked():
            # Start auto-refresh every 5 minutes
            self.refresh_timer.start(300000)  # 5 minutes
            self.auto_refresh_btn.setText("⏰ Auto-Refresh (AN)")
            self.status_label.setText("Auto-Refresh aktiviert (5 Min)")
            logging.info("Auto-refresh enabled")
        else:
            # Stop auto-refresh
            self.refresh_timer.stop()
            self.auto_refresh_btn.setText("⏰ Auto-Refresh")
            self.status_label.setText("Auto-Refresh deaktiviert")
            logging.info("Auto-refresh disabled")
            
    def show_error(self, message):
        """Show error message"""
        self.status_label.setText(f"Fehler: {message}")
        QMessageBox.warning(self, "Dashboard Fehler", message)
        
    def export_dashboard_data(self):
        """Export dashboard data (can be called from other parts of the app)"""
        return self.refresh_data()
        
    def get_dashboard_url(self):
        """Get the dashboard URL for external access"""
        if self.html_file.exists():
            return QUrl.fromLocalFile(str(self.html_file))
        return None


class DashboardWindow(QWidget):
    """Standalone dashboard window"""
    
    def __init__(self, tumorboard_base_path=None):
        super().__init__()
        self.setWindowTitle("🏥 Tumorboard Analytics Dashboard")
        self.setGeometry(100, 100, 1400, 900)
        
        # Set window properties to keep it alive
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, False)
        self.setWindowFlags(Qt.WindowType.Window)
        
        layout = QVBoxLayout(self)
        
        # Add dashboard manager with correct base path
        self.dashboard_manager = DashboardManager(self, tumorboard_base_path)
        layout.addWidget(self.dashboard_manager)
        
        # Initial data refresh
        self.dashboard_manager.refresh_data()
        
        # Show window
        self.show()
        self.raise_()
        self.activateWindow()
        
    def closeEvent(self, event):
        """Handle window close event"""
        print("🔴 Dashboard wird geschlossen...")
        
        # Stop auto-refresh timer
        if hasattr(self.dashboard_manager, 'refresh_timer'):
            self.dashboard_manager.refresh_timer.stop()
            
        # Accept the close event
        event.accept()
        
        # Quit the application
        QApplication.quit()


def create_dashboard_window(tumorboard_base_path=None):
    """Create and return a dashboard window"""
    return DashboardWindow(tumorboard_base_path)


def export_dashboard_data(tumorboard_base_path=None):
    """Standalone function to export dashboard data"""
    # Determine correct tumorboard base path if not provided
    if tumorboard_base_path is None:
        # Try K: first, fall back to user home
        k_path = Path("K:/RAO_Projekte/App/tumorboards")
        if k_path.exists() and k_path.is_dir():
            tumorboard_base_path = k_path
        else:
            tumorboard_base_path = Path.home() / "tumorboards"
    
    exporter = DashboardDataExporter(tumorboard_base_path)
    return exporter.export_dashboard_data() 