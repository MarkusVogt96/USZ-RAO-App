from PyQt6.QtWidgets import QWidget, QGridLayout, QLabel, QVBoxLayout, QPushButton, QHBoxLayout, QScrollArea, QFrame, QMessageBox, QDialog, QLineEdit, QFormLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
import os
import logging
from pathlib import Path

class TumorboardsPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        logging.info("Initializing TumorboardsPage...")
        self.main_window = main_window
        
        # Define all tumorboards (from existing script)
        self.alle_tumorboards = [
            "GI",
            "Gyn Becken",
            "Gyn Mamma",
            "HCC",
            "HPB",
            "Melanom",
            "Neuro",
            "NET",
            "KHT",
            "Pädiatrie",
            "Hypophyse",
            "Lymphom",
            "Sarkom",
            "Schädelbasis",
            "Schilddrüse",
            "Thorax",
            "Uro"
        ]
        
        self.tumorboard_location_mapping = {
            "GI": "OPS B24",
            "Gyn Becken": "NORD1 C307",
            "Gyn Mamma": "NORD1 C307",
            "HCC": "{placeholder}",
            "HPB": "Kleiner Hörsaal Pathologie",
            "Melanom": "OPS B26",
            "Neuro": "NORD1 C225",
            "NET": "B OPS Demonstrationssaal 3",
            "KHT": "NORD2 B811",
            "Pädiatrie": "Kispi/Online",
            "Hypophyse": "Online",
            "Lymphom": "PATH B82",
            "Sarkom": "HOER B 15",
            "Schädelbasis": "NORD2",
            "Schilddrüse": "NUK A 33",
            "Thorax": "OPS B 26",
            "Uro": "NORD1 B203"
        }
        
        # Temporary weekday assignments (distribute tumorboards across Mon-Fri)
        self.weekday_assignments = self._create_weekday_assignments()
        
        # Setup UI after initializing data
        self.setup_ui()
        logging.info("TumorboardsPage UI setup complete.")

    def _create_weekday_assignments(self):
        """Distribute tumorboards across weekdays (Monday-Friday)"""
        weekdays = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag"]
        assignments = {day: [] for day in weekdays}
        
        # Define specific realistic times for demonstration
        # This shows the chronological ordering and proportional spacing
        specific_assignments = {
            "Montag": [
                {'name': 'Neuro', 'time': '8:30'},
                {'name': 'Thorax', 'time': '13:30'},
                {'name': 'GI', 'time': '16:00'},
                {'name': 'NET', 'time': '17:30'}
            ],
            "Dienstag": [
                {'name': 'Melanom', 'time': '8:00'},
                {'name': 'Schädelbasis', 'time': '8:00'},
                {'name': 'Gyn Becken', 'time': '15:00'},
                {'name': 'Gyn Mamma', 'time': '15:00'},
                {'name': 'Uro', 'time': '16:30'},
                {'name': 'Hypophyse', 'time': '17:15'},
                {'name': 'Pädiatrie', 'time': '17:30'},
            ],
            "Mittwoch": [
                {'name': 'KHT', 'time': '8:00'},
                {'name': 'Lymphom', 'time': '16:30'},
            ],
            "Donnerstag": [
                {'name': 'HPB', 'time': '07:30'},
                {'name': 'Sarkom', 'time': '15:30'},
            ],
            "Freitag": [
                {'name': 'Schilddrüse', 'time': '12:15'}
            ]
        }
        
        # Assign the specific times and sort by time within each day
        for day in weekdays:
            if day in specific_assignments:
                assignments[day] = specific_assignments[day]
                # Sort by time within each day
                assignments[day].sort(key=lambda x: int(x['time'].split(':')[0]))
            
        return assignments

    def setup_ui(self):
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 0, 40, 20)
        self.setLayout(main_layout)

        # Create scrollable area for the week view
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)
        
        # Week view widget with time axis
        week_widget = QWidget()
        week_layout = QHBoxLayout(week_widget)
        week_layout.setSpacing(0)
        week_layout.setContentsMargins(10, 10, 10, 10)
        
        # Add time axis column
        time_axis = self._create_time_axis()
        week_layout.addWidget(time_axis)
        
        # Create columns for each weekday
        weekdays = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag"]
        
        for day in weekdays:
            day_column = self._create_day_column(day)
            week_layout.addWidget(day_column)
        
        scroll_area.setWidget(week_widget)
        main_layout.addWidget(scroll_area)

    def _create_time_axis(self):
        """Create a time axis showing hours from 07:00 to 19:00"""
        time_frame = QFrame()
        time_frame.setFixedWidth(80)
        time_frame.setStyleSheet("""
            QFrame {
                background-color: #0f1419;
                border-right: 2px solid #2a3642;
            }
        """)
        
        # Use a widget with absolute positioning for precise time placement
        # Reduced height to end around 18:30 (about 11.5 hours * 70px = 805px)
        time_container = QWidget(time_frame)
        time_container.setGeometry(0, 0, 80, 805)
        
        # Time labels from 07:00 to 19:00
        for hour in range(7, 20):
            time_label = QLabel(f"{hour:02d}:00", time_container)
            time_label.setFont(QFont("Helvetica", 10))
            time_label.setStyleSheet("color: #cccccc; background: transparent; border: none; outline: none;")
            time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            # Position based on hour (70px per hour, starting at y=20 to move closer to top)
            y_position = 20 + (hour - 7) * 70
            time_label.setGeometry(0, y_position - 10, 80, 20)
            
            # Add horizontal line
            line = QFrame(time_container)
            line.setFrameShape(QFrame.Shape.HLine)
            line.setStyleSheet("background-color: #2a3642; min-height: 1px; max-height: 1px;")
            line.setGeometry(60, y_position, 20, 1)
        
        return time_frame

    def _create_day_column(self, day_name):
        """Create a column for a specific weekday with time-based positioning"""
        column_frame = QFrame()
        column_frame.setFixedWidth(280)
        column_frame.setMinimumHeight(805)  # Match time axis height
        column_frame.setStyleSheet("""
            QFrame {
                background-color: #114473;
                border: 1px solid #2a3642;
                border-radius: 8px;
                margin-left: 15px;
            }
        """)
        
        # Day header (absolute positioning)
        day_header = QLabel(day_name, column_frame)
        day_header.setFont(QFont("Helvetica", 16, QFont.Weight.Bold))
        day_header.setStyleSheet("color: white; background: transparent; border: none; outline: none;")
        day_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        day_header.setGeometry(0, 15, 280, 25)
        
        # Container for tumorboard buttons with absolute positioning
        content_container = QWidget(column_frame)
        content_container.setGeometry(18, 35, 260, 850)  # Proper margins within column
        
        # Add tumorboard buttons for this day with time-based positioning
        tumorboards_for_day = self.weekday_assignments.get(day_name, [])
        
        # Sort tumorboards by time, then by name for consistent ordering
        tumorboards_for_day.sort(key=lambda x: (x['time'], x['name']))
        
        # Handle overlapping tumorboards (special cases)
        overlap_groups = self._group_overlapping_tumorboards(tumorboards_for_day)
        
        # Create buttons for each group
        for group in overlap_groups:
            parallel_count = len(group)
            
            for i, tb_info in enumerate(group):
                tb_button = self._create_tumorboard_button(tb_info['name'], tb_info['time'], content_container, parallel_count)
                
                # Calculate position based on time
                hour = int(tb_info['time'].split(':')[0])
                minute = int(tb_info['time'].split(':')[1]) if ':' in tb_info['time'] else 0
                
                # Position: 70px per hour, starting from hour 7
                y_position = (hour - 7) * 70 + (minute / 60) * 70
                
                # Determine button height based on tumorboard type
                button_height = self._get_button_height(tb_info['name'])
                
                # Handle parallel tumorboards by splitting the width
                if parallel_count == 1:
                    button_width = 240  # Full width for single buttons within container
                    x_position = (260 - button_width) // 2  # Center the button in container
                else:
                    # Distribute parallel buttons across the width
                    total_width = 240
                    spacing = 2
                    available_width = total_width - (spacing * (parallel_count - 1))
                    button_width = available_width // parallel_count
                    # Center the group of parallel buttons
                    group_start = (260 - total_width) // 2
                    x_position = group_start + i * (button_width + spacing)
                
                tb_button.setGeometry(x_position, int(y_position), button_width, button_height)
        
        return column_frame
    
    def _group_overlapping_tumorboards(self, tumorboards):
        """Group tumorboards that overlap in time"""
        if not tumorboards:
            return []
        
        groups = []
        current_group = [tumorboards[0]]
        
        for i in range(1, len(tumorboards)):
            current_tb = tumorboards[i]
            last_tb = current_group[-1]
            
            # Check if current tumorboard overlaps with any in current group
            if self._tumorboards_overlap(last_tb, current_tb):
                current_group.append(current_tb)
            else:
                groups.append(current_group)
                current_group = [current_tb]
        
        groups.append(current_group)
        return groups
    
    def _tumorboards_overlap(self, tb1, tb2):
        """Check if two tumorboards overlap in time"""
        # Parse times
        hour1 = int(tb1['time'].split(':')[0])
        minute1 = int(tb1['time'].split(':')[1]) if ':' in tb1['time'] else 0
        start1 = hour1 * 60 + minute1
        
        hour2 = int(tb2['time'].split(':')[0])
        minute2 = int(tb2['time'].split(':')[1]) if ':' in tb2['time'] else 0
        start2 = hour2 * 60 + minute2
        
        # Get durations
        duration1 = self._get_button_duration(tb1['name'])
        duration2 = self._get_button_duration(tb2['name'])
        
        end1 = start1 + duration1
        end2 = start2 + duration2
        
        # Check for overlap
        return not (end1 <= start2 or end2 <= start1)
    
    def _get_button_duration(self, tumorboard_name):
        """Get button duration in minutes for specific tumorboards"""
        if tumorboard_name == "Uro":
            return 42  # 45 minutes
        else:
            return 60  # Default 60 minutes
    
    def _get_button_height(self, tumorboard_name):
        """Get button height in pixels for specific tumorboards"""
        duration = self._get_button_duration(tumorboard_name)
        # 70px per hour, so scale proportionally
        return int((duration / 60) * 70)

    def _create_tumorboard_button(self, tumorboard_name, time, parent_container, parallel_count=1):
        """Create a tumorboard button"""
        button = QPushButton(parent_container)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Adjust padding based on parallel count
        padding = "3px" if parallel_count > 1 else "6px"
        
        # Button styling
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: #367E9E;
                color: white;
                border: none;
                border-radius: 6px;
                text-align: left;
                padding: {padding};
            }}
            QPushButton:hover {{
                background-color: #4499BC;
            }}
            QPushButton:pressed {{
                background-color: #2A6780;
            }}
        """)
        
        # Create button layout with tumorboard name and location
        button_layout = QVBoxLayout(button)
        
        # Adjust margins and spacing based on parallel count and tumorboard type
        if parallel_count > 1:
            button_layout.setContentsMargins(0, 6, 6, 3)
            button_layout.setSpacing(1)
        else:
            # Special margins for Uro button
            if tumorboard_name == "Uro":
                button_layout.setContentsMargins(10, 3, 3, 3)
            else:
                button_layout.setContentsMargins(10, 8, 6, 6)
            button_layout.setSpacing(3)
        
        # Adjust font sizes based on parallel count and button size
        time_name_font_size = 9 if parallel_count > 1 else 11
        location_font_size = 8 if parallel_count > 1 else 10
        
        # Create combined time and name as single field
        time_name_text = f"{time}  {tumorboard_name}"
        
        # Time and name as single label
        time_name_label = QLabel(time_name_text)
        time_name_label.setFont(QFont("Helvetica", time_name_font_size, QFont.Weight.Bold))
        time_name_label.setStyleSheet("color: white; background: transparent; border: none; outline: none;")
        time_name_label.setWordWrap(True)
        time_name_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        
        # Add the combined time/name label
        button_layout.addWidget(time_name_label)
        
        # Location label
        location = self.tumorboard_location_mapping.get(tumorboard_name, "{placeholder}")
        location_label = QLabel(f"Ort: {location}")
        location_label.setFont(QFont("Helvetica", location_font_size))
        location_label.setStyleSheet("color: white; background: transparent; border: none; outline: none;")
        location_label.setWordWrap(True)
        location_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        button_layout.addWidget(location_label)
        
        # Add stretch to push content to top and bottom (only for single buttons)
        if parallel_count == 1:
            button_layout.addStretch()
        
        # Connect button click
        button.clicked.connect(lambda checked, name=tumorboard_name: self.open_specific_tumorboard_page(name))
        
        return button

    def open_specific_tumorboard_page(self, tumorboard_name):
        """Open the specific tumorboard page for the selected tumorboard"""
        logging.info(f"Opening specific tumorboard page for: {tumorboard_name}")
        
        # Check for user data before proceeding (like QISIM Scripts)
        nachname, vorname = self.get_benutzerdaten()
        
        if nachname is None or vorname is None:
            logging.warning("User data not found. Prompting user for input before opening tumorboard.")
            dialog = self.BenutzerdatenDialog(self)
            result = dialog.exec()
            
            if result != QDialog.DialogCode.Accepted:
                # User cancelled, don't proceed
                return
            
            # Re-check user data after input
            nachname, vorname = self.get_benutzerdaten()
            if nachname is None or vorname is None:
                QMessageBox.critical(self, "Fehler", "Benutzerdaten konnten nicht gespeichert werden. Navigation abgebrochen.")
                return
        
        # Import here to avoid circular imports
        from .specific_tumorboard_page import SpecificTumorboardPage
        
        # Check if page already exists
        existing_page_index = self.main_window.find_page_index(SpecificTumorboardPage, tumorboard_name)
        if existing_page_index is not None:
            logging.info("Found existing specific tumorboard page, switching to it.")
            self.main_window.stacked_widget.setCurrentIndex(existing_page_index)
        else:
            logging.info("Creating new specific tumorboard page.")
            specific_page = SpecificTumorboardPage(self.main_window, tumorboard_name)
            new_index = self.main_window.stacked_widget.addWidget(specific_page)
            self.main_window.stacked_widget.setCurrentIndex(new_index)
    
    @staticmethod
    def get_benutzerdaten():
        """Get user data from ~/patdata/benutzerdaten.txt"""
        user_home = Path.home()
        patdata_dir = user_home / "patdata"
        benutzerdaten_file = patdata_dir / "benutzerdaten.txt"
        
        # Ensure patdata directory exists
        try:
            patdata_dir.mkdir(exist_ok=True)
        except OSError as e:
            logging.error(f"Could not create directory '{patdata_dir}': {e}")
            return None, None
        
        if benutzerdaten_file.exists():
            try:
                with open(benutzerdaten_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                data = {}
                for line in lines:
                    line = line.strip()
                    if '=' in line:
                        key, value = line.split('=', 1)
                        data[key.strip()] = value.strip()
                
                if "Nachname" in data and data["Nachname"] and \
                   "Vorname" in data and data["Vorname"]:
                    return data["Nachname"], data["Vorname"]
                else:
                    logging.warning(f"Invalid or incomplete entries in '{benutzerdaten_file}'")
                    return None, None
                    
            except Exception as e:
                logging.error(f"Error reading '{benutzerdaten_file}': {e}")
                return None, None
        
        logging.info(f"User data file '{benutzerdaten_file}' not found")
        return None, None
    
    @staticmethod
    def save_benutzerdaten(nachname, vorname):
        """Save user data to ~/patdata/benutzerdaten.txt"""
        user_home = Path.home()
        patdata_dir = user_home / "patdata"
        benutzerdaten_file = patdata_dir / "benutzerdaten.txt"
        
        # Input validation
        if not nachname or not nachname.strip():
            logging.error("Invalid or empty surname for saving")
            return False
        if not vorname or not vorname.strip():
            logging.error("Invalid or empty first name for saving")
            return False
        
        nachname = nachname.strip()
        vorname = vorname.strip()
        
        try:
            patdata_dir.mkdir(exist_ok=True)
            
            with open(benutzerdaten_file, 'w', encoding='utf-8') as f:
                f.write(f"Nachname={nachname}\n")
                f.write(f"Vorname={vorname}\n")
            
            logging.info(f"User data successfully saved to '{benutzerdaten_file}'")
            return True
            
        except OSError as e:
            logging.error(f"Could not create directory '{patdata_dir}' or access it: {e}")
            return False
        except IOError as e:
            logging.error(f"Could not write to file '{benutzerdaten_file}': {e}")
            return False
        except Exception as e:
            logging.error(f"Error saving user data to '{benutzerdaten_file}': {e}")
            return False
    
    class BenutzerdatenDialog(QDialog):
        """Dialog for user data input"""
        def __init__(self, parent=None):
            super().__init__(parent)
            self.setWindowTitle("Erfassung Benutzerdaten")
            self.setModal(True)
            self.setFixedSize(635, 330)
            
            layout = QVBoxLayout()
            
            # Info text
            info_text = ("Benutzerdaten sind in der App noch nicht hinterlegt, jedoch relevant zum Eintragen des signierenden/visierenden Benutzers in Berichte und Berichte im KISIM. "
                         "Bitte jetzt erfassen und auf Rechtschreibung achten!")
            info_label = QLabel(info_text)
            info_label.setWordWrap(True)
            info_label.setStyleSheet("color: white; margin-bottom: 15px;")
            layout.addWidget(info_label)
            
            # Form layout
            form_layout = QFormLayout()
            form_layout.setHorizontalSpacing(20)
            form_layout.setVerticalSpacing(10)
            
            self.vorname_edit = QLineEdit()
            self.nachname_edit = QLineEdit()
            
            # Styling for input fields
            input_style = "background-color: black; color: white; border: 1px solid #555; padding: 5px; border-radius: 3px;"
            self.vorname_edit.setStyleSheet(input_style)
            self.nachname_edit.setStyleSheet(input_style)
            
            # Labels
            vorname_label = QLabel("Vorname:")
            nachname_label = QLabel("Nachname:")
            label_style = "color: white;"
            vorname_label.setStyleSheet(label_style)
            nachname_label.setStyleSheet(label_style)
            
            form_layout.addRow(vorname_label, self.vorname_edit)
            form_layout.addRow(nachname_label, self.nachname_edit)
            
            layout.addLayout(form_layout)
            
            # Buttons
            button_layout = QVBoxLayout()
            
            self.save_button = QPushButton("Speichern")
            self.cancel_button = QPushButton("Abbrechen")
            
            button_style = """
                QPushButton {
                    background-color: black;
                    color: white;
                    padding: 5px 10px;
                    border: 1px solid #555;
                    border-radius: 3px;
                    min-width: 60px;
                }
                QPushButton:hover {
                    background-color: #444;
                }
            """
            self.save_button.setStyleSheet(button_style)
            self.cancel_button.setStyleSheet(button_style)
            
            self.save_button.clicked.connect(self.on_save)
            self.cancel_button.clicked.connect(self.reject)
            
            button_layout.addWidget(self.save_button)
            button_layout.addWidget(self.cancel_button)
            
            layout.addLayout(button_layout)
            self.setLayout(layout)
            
            # Apply dark theme
            self.setStyleSheet("""
                QDialog {
                    background-color: #333;
                    color: white;
                }
            """)
        
        def on_save(self):
            vorname = self.vorname_edit.text().strip()
            nachname = self.nachname_edit.text().strip()
            
            if not vorname or not nachname:
                msg_box = QMessageBox(QMessageBox.Icon.Warning, "Eingabe fehlt",
                                      "Bitte geben Sie sowohl Vorname als auch Nachname ein.",
                                      QMessageBox.StandardButton.Ok, self)
                msg_box.setStyleSheet("""
                    QMessageBox { 
                        background-color: #333; 
                        color: white; 
                    } 
                    QPushButton { 
                        background-color: black; 
                        color: white; 
                        padding: 5px 10px; 
                        border: 1px solid #555; 
                        border-radius: 3px; 
                        min-width: 60px; 
                    } 
                    QPushButton:hover { 
                        background-color: #444; 
                    }
                """)
                msg_box.exec()
                return
            
            success = TumorboardsPage.save_benutzerdaten(nachname, vorname)
            if success:
                logging.info("User data saved successfully from TumorboardsPage")
                self.accept()
            else:
                err_msg = "Fehler beim Speichern der Benutzerdaten. Überprüfen Sie die Berechtigungen für das 'patdata'-Verzeichnis."
                msg_box = QMessageBox(QMessageBox.Icon.Critical, "Speicherfehler", err_msg,
                                      QMessageBox.StandardButton.Ok, self)
                msg_box.setStyleSheet("""
                    QMessageBox { 
                        background-color: #333; 
                        color: white; 
                    } 
                    QPushButton { 
                        background-color: black; 
                        color: white; 
                        padding: 5px 10px; 
                        border: 1px solid #555; 
                        border-radius: 3px; 
                        min-width: 60px; 
                    } 
                    QPushButton:hover { 
                        background-color: #444; 
                    }
                """)
                msg_box.exec() 