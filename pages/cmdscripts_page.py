# pages/cmdscripts_page.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLabel, QApplication, QPushButton, QHBoxLayout, QLineEdit
from PyQt6.QtCore import Qt, QProcess, pyqtSignal, QProcessEnvironment, QMetaObject
from PyQt6.QtGui import QFont, QColor, QPalette, QTextCursor, QTextCharFormat
# --- Remove winpty --- 
# import winpty 
# import re # No longer needed for cleaning

import os
import sys
import shlex
import shutil  # For file copying
# import errno # No longer needed
import re # For prompt detection
import io
import threading
import queue
import time
import logging # Import logging module

# Import the script definitions and key generator from kisim_page
from .kisim_page import script_definitions, generate_script_key

# --- Script Directory ---
# Define the path to the scripts directory relative to this file's location
# pages/../scripts -> resolves to the 'scripts' folder in the project root
scripts_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), os.pardir, "scripts"))

# Optional: Check if the directory exists at startup (can help debugging)
if not os.path.exists(scripts_dir):
    print(f"Warning: Scripts directory not found at expected location: {scripts_dir}")
# -----------------------

class CmdScriptsPage(QWidget):
    """A QWidget page to display script execution output using QProcess."""
    def __init__(self, main_window=None): # Optional main_window reference
        super().__init__()
        logging.info("Initializing CmdScriptsPage...")
        self.main_window = main_window # Store if needed later
        self.process = None # QProcess object, managed directly by the widget
        self.output_buffer = "" # Buffer for incomplete lines
        
        # For bundled mode
        self.input_queue = queue.Queue()
        self.input_buffer = ""
        self.bundled_input_thread = None
        self.bundled_mode_active = False
        self.stop_requested = False  # Flag to signal script to stop
        self.script_thread = None   # Thread for script execution
        
        self.default_text_color = QColor(248, 248, 242) # #f8f8f2
        self.prompt_text_color = QColor(80, 250, 123)  # #50fa7b (Dracula green)
        self.setup_ui()
        
    # Redirector classes for bundled mode
    class OutputRedirector:
        def __init__(self, output_callback):
            self.output_callback = output_callback
            self.buffer = ""
        
        def write(self, text):
            self.buffer += text
            if '\n' in text:
                self.output_callback(self.buffer)
                self.buffer = ""
        
        def flush(self):
            if self.buffer:
                self.output_callback(self.buffer)
                self.buffer = ""
    
    class StdinRedirector:
        def __init__(self, queue_obj):
            self.queue = queue_obj
            self.buffer = ""
            self.parent = None  # Will be set when instance is created
            
        def readline(self):
            # Enable input field when input is requested
            try:
                # Check for stop request before doing anything else
                if self.parent and hasattr(self.parent, 'stop_requested') and self.parent.stop_requested:
                    # Safely raise KeyboardInterrupt within controlled environment
                    self.safe_raise_interrupt("Script execution interrupted by user")
                
                # Only process UI events if we're still allowed to continue
                try:
                    QApplication.processEvents()  # Process events to update UI
                    if self.parent and hasattr(self.parent, 'input_field'):
                        self.parent.input_field.setEnabled(True)
                        self.parent.input_field.setFocus()
                    QApplication.processEvents()  # Process events again to update UI
                except Exception as ui_error:
                    logging.warning(f"UI error during readline: {ui_error}")
                    # If UI operations fail, we should abort the script
                    self.safe_raise_interrupt("UI error during input request")
                
                # Wait for input from the queue (filled by send_input)
                start_time = time.time()
                max_wait_without_check = 0.2  # Check for interruption more frequently
                
                while True:
                    # Prioritize checking for stop request
                    if self.parent and hasattr(self.parent, 'stop_requested') and self.parent.stop_requested:
                        self.safe_raise_interrupt("Script execution interrupted by user")
                    
                    # Then check for input
                    if self.parent and hasattr(self.parent, 'input_buffer') and self.parent.input_buffer:
                        text = self.parent.input_buffer + '\n'
                        self.parent.input_buffer = ""
                        return text
                    
                    # Use shorter sleep time to be more responsive to interruptions
                    # Also check if too much time has passed without any response
                    elapsed = time.time() - start_time
                    if elapsed > 60.0:  # If waiting for more than a minute
                        logging.warning("Waited too long for input in readline")
                        # Every minute, remind the user they can interrupt
                        start_time = time.time()  # Reset the start time
                        try:
                            print("\n*** Still waiting for input. Press STOP to abort. ***")
                        except Exception:
                            pass
                    
                    # Use smaller sleep chunks
                    time.sleep(min(max_wait_without_check, 0.03))
                    
                    # Only process events if parent widget still exists
                    if self.parent:
                        try:
                            QApplication.processEvents()  # Keep processing events while waiting
                        except Exception:
                            # If event processing fails, we might be shutting down
                            self.safe_raise_interrupt("Error processing events during input request")
            except KeyboardInterrupt:
                # Let KeyboardInterrupt pass through directly
                raise
            except Exception as e:
                # If anything goes wrong during readline, convert to KeyboardInterrupt for clean abort
                error_msg = f"\n*** Error in stdin readline: {e} ***"
                logging.error(error_msg)
                print(error_msg)
                self.safe_raise_interrupt(f"Error in stdin: {e}")
        
        def isatty(self):
            return True
            
        def safe_raise_interrupt(self, message):
            """Safely raise KeyboardInterrupt with proper logging and UI feedback"""
            try:
                # Try to log and display the message
                logging.warning(f"Script interrupt requested: {message}")
                print(f"\n*** {message} ***")
            except Exception:
                # Ignore any errors in printing/logging
                pass
                
            # Raise the interruption - this should be caught by the script thread's
            # exception handler which is properly protected
            raise KeyboardInterrupt(message)

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Define button styles
        self.stop_button_style_active = """
            QPushButton {
                background-color: #A80000; /* Dark Red */
                color: white;
                padding: 5px 15px;
                border-radius: 4px;
                border: 1px solid #600000; /* Darker border */
                min-width: 60px;
            }
            QPushButton:hover { background-color: #C80000; }
            QPushButton:pressed { background-color: #880000; }
        """
        self.stop_button_style_inactive = """
            QPushButton {
                background-color: #6c757d; /* Gray */
                color: white;
                padding: 5px 15px;
                border-radius: 4px;
                border: 1px solid #5a6268; /* Darker gray border */
                min-width: 60px;
            }
            QPushButton:hover { background-color: #868e96; }
            QPushButton:pressed { background-color: #545b62; }
        """

        # --- Top Header (Title + Stop Button) ---
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 5) # Add some bottom margin

        self.title_label = QLabel("Script Output")
        self.title_label.setFont(QFont("Helvetica", 18, QFont.Weight.Bold))
        self.title_label.setStyleSheet("color: white;")
        header_layout.addWidget(self.title_label)

        header_layout.addStretch() # Push button to the right

        self.stop_button = QPushButton("STOP")
        self.stop_button.setFont(QFont("Helvetica", 10, QFont.Weight.Bold))
        self.stop_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.stop_button.setStyleSheet(self.stop_button_style_inactive) # Start inactive (gray)
        
        # Use a protected click handler to prevent exceptions from propagating
        self.stop_button.clicked.connect(self.safe_stop_button_clicked)
        header_layout.addWidget(self.stop_button)
        # --- End Top Header ---

        layout.addLayout(header_layout) # Add header layout to main vertical layout

        self.output_area = QTextEdit()
        self.output_area.setReadOnly(True)
        # Store base font properties
        self.base_font_family = "Consolas"
        self.base_font_size = 12
        base_font = QFont(self.base_font_family, self.base_font_size)
        self.output_area.setFont(base_font) # Apply default font
        logging.debug("CmdScriptsPage UI setup started.")

        # Dark theme for the terminal area
        palette = self.output_area.palette()
        palette.setColor(QPalette.ColorRole.Base, QColor(40, 42, 54)) # Dark background
        palette.setColor(QPalette.ColorRole.Text, self.default_text_color)
        self.output_area.setPalette(palette)
        self.output_area.setStyleSheet("border: 1px solid #6272a4;") # Optional border

        layout.addWidget(self.output_area)

        # --- Input Section --- 
        input_layout = QHBoxLayout()
        input_layout.setSpacing(5)

        self.input_field = QLineEdit()
        # Use the base font for consistency, but maybe different style
        self.input_field.setFont(QFont(self.base_font_family, self.base_font_size))
        self.input_field.setFixedHeight(40) # Adjusted height
        self.input_field.setStyleSheet("""
            QLineEdit {
                background-color: #282a36; /* Slightly lighter bg */
                color: #f8f8f2; /* Light text */
                border: 1px solid #6272a4; 
                padding: 5px; 
            }
            QLineEdit:disabled {
                background-color: #44475a; /* Disabled bg */
                color: #6272a4; /* Disabled text */
            }
        """)
        self.input_field.setPlaceholderText("Enter input and press Enter...")
        self.input_field.returnPressed.connect(self.send_input)
        input_layout.addWidget(self.input_field)

        layout.addLayout(input_layout)
        # --- End Input Section ---

        self.setLayout(layout)
        self.input_field.setEnabled(False) # Initially disabled
        logging.info("CmdScriptsPage UI setup complete.")

    def safe_stop_button_clicked(self):
        """Safe wrapper for stop_current_script to prevent app crashes"""
        try:
            logging.info("STOP button clicked. Initiating safe script termination...")
            result = self.stop_current_script()
            logging.info(f"Script termination initiated: {result}")
        except Exception as e:
            # Catch ALL exceptions to prevent app crash
            logging.critical(f"CRITICAL ERROR in stop button handler: {e}")
            try:
                # Try to show error in output area
                self.append_formatted_output(f"\n*** FEHLER beim Stoppen des Skripts: {e} ***\n", bold=True)
                # Try to reset UI state
                self.stop_button.setText("STOP")
                self.stop_button.setEnabled(True)
                self.stop_button.setStyleSheet(self.stop_button_style_inactive)
            except Exception as ui_error:
                # Absolutely last resort
                logging.critical(f"Failed to update UI after stop error: {ui_error}")
            
            # Try to disable the script in a very minimal way
            try:
                self.stop_requested = True
                self.bundled_mode_active = False
            except Exception:
                pass

    # --- QProcess Signal Handlers --- 

    def handle_output(self):
        if not self.process:
            return
        data = self.process.readAllStandardOutput()
        try:
            # Decode the received chunk
            output_chunk = data.data().decode('utf-8', errors='replace') 
            logging.debug(f"QProcess stdout received: {len(output_chunk)} chars")
            # Append the chunk directly, let append_formatted_output handle formatting
            self.append_formatted_output(output_chunk) 
        except Exception as e:
             print(f"Error processing output chunk: {e}")
             try:
                 # Ensure error messages have newlines
                 error_text = f"[Processing Error: {e}]\n"
                 logging.error(f"Error processing output chunk: {e}", exc_info=True)
                 self.append_formatted_output(error_text, bold=False)
                 # Try decoding as latin-1 as a fallback for errors
                 fallback_text = data.data().decode('latin-1', errors='ignore') + "\n"
                 self.append_formatted_output(fallback_text, bold=False)
             except Exception:
                 pass
             
    def handle_error(self, error):
        if not self.process: # Avoid errors if process already cleaned up
             return
        error_map = {
            QProcess.ProcessError.FailedToStart: "Failed to Start",
            QProcess.ProcessError.Crashed: "Crashed",
            QProcess.ProcessError.Timedout: "Timed Out",
            QProcess.ProcessError.ReadError: "Read Error",
            QProcess.ProcessError.WriteError: "Write Error",
            QProcess.ProcessError.UnknownError: "Unknown Error",
        }
        error_string = error_map.get(error, "Unknown Error")
        # Ensure error message uses regular font and adds newline
        error_text = f"\n--- Process Error: {error_string} ---\n"
        logging.error(f"QProcess error occurred: {error_string} (Code: {error})")
        self.append_formatted_output(error_text, bold=False)
        # Finished signal might still be emitted after an error, 
        # so cleanup is primarily handled in handle_finish

    def handle_finish(self, exitCode, exitStatus):
        logging.info(f"QProcess finished. Exit Code: {exitCode}, Exit Status: {exitStatus}")
        if not self.process: # Avoid double-handling if called after cleanup
            logging.warning("handle_finish called but self.process is None. Already cleaned up?")
            return
        # Process any final, non-prompt data remaining in buffer
        if self.output_buffer:
             self.append_formatted_output(self.output_buffer, bold=False) # Append final chunk without extra newline
             self.output_buffer = "" 

        # Read final output (might be empty, but good practice)
        # This call might append if there was data between last read and finish
        # self.handle_output() # Reconsider if this is needed/causes issues
        
        status_text = "normally" if exitStatus == QProcess.ExitStatus.NormalExit else "crashed"
        final_message = f"Process finished {status_text} with exit code {exitCode}"
        is_success = exitCode == 0 and exitStatus == QProcess.ExitStatus.NormalExit
        if is_success:
            final_message += " (no errors encountered)"
            
        current_title = self.title_label.text().split(" (")[0] # Remove old status
        status_indicator = "Finished OK" if is_success else f"Finished: Error Code {exitCode}"
        self.title_label.setText(f"{current_title} ({status_indicator})")
        self.input_field.setEnabled(False) # Disable input
        self.process.deleteLater() # Schedule QProcess object for deletion
        self.process = None # Clear reference
        # Set button to inactive style regardless of whether a process was running
        self.stop_button.setStyleSheet(self.stop_button_style_inactive)

    # --- Control Methods --- 

    def run_script_by_key(self, script_key):
        """Starts the execution of a script based on its unique key."""
        
        logging.info(f"Attempting to run script with key: '{script_key}'")
        # Stop any currently running script first
        self.stop_current_script()
        
        self.output_area.clear()
        self.output_buffer = "" # Clear buffer on new run
        self.title_label.setText(f"Running: {script_key}") # Indicate running

        # Find script_name by iterating through definitions and matching the key
        script_name = None
        found_mapping = False
        for tile_name, fname in script_definitions:
            current_key = generate_script_key(tile_name)
            if current_key == script_key:
                script_name = fname
                found_mapping = True
                break # Found the script, exit loop

        if found_mapping and script_name:
            script_path = os.path.join(scripts_dir, script_name)
            # script_dir_actual = os.path.dirname(script_path) # No longer needed, use scripts_dir directly

            # Check if the script file exists
            if not os.path.exists(script_path):
                logging.error(f"Script file not found: {script_path}")
                self.title_label.setText(f"Error: Script not found")
                self.append_formatted_output(f"Error: Script file not found at: {script_path}\n")
                self.script_finished(-1) # Indicate error
                self.stop_button.setStyleSheet(self.stop_button_style_inactive) # Ensure button is gray
                return

            # --- Create and configure QProcess --- 
            self.input_field.setEnabled(False) # Ensure disabled before start
            self.input_field.clear()

            # Set button to active style BEFORE starting
            self.stop_button.setStyleSheet(self.stop_button_style_active)
            self.stop_button.setEnabled(True) # Ensure button is clickable

            # Check if we're running in a PyInstaller bundle
            if getattr(sys, 'frozen', False):
                # We're running in a PyInstaller bundle - need to use a different approach
                self.append_formatted_output(f"Executing script: {script_name} in bundled mode\n", bold=False)
                separator_line = "-" * 50 + "\n"
                self.append_formatted_output(separator_line, bold=False)
                
                # Start the stdin reader thread
                self.bundled_mode_active = True
                self.bundled_input_thread = threading.Thread(target=self.stdin_reader)
                self.bundled_input_thread.daemon = True
                self.bundled_input_thread.start()
                
                # Enable input for bundled mode
                self.input_field.setEnabled(True)
                self.input_field.setFocus()
                
                # Force Qt to process events to ensure UI updates
                QApplication.processEvents()
                
                # Call our enable_input method to ensure proper setup
                self.enable_input()
                
                # Reset the stop flag
                self.stop_requested = False
                
                # Define a function to run the script in a thread
                def run_script_in_thread():
                    # Save original stdout/stderr/stdin and sys.path
                    old_stdout = sys.stdout
                    old_stderr = sys.stderr
                    old_stdin = sys.stdin
                    old_sys_path = sys.path.copy()
                    original_time_sleep = time.sleep
                    
                    try:
                        # Create redirectors
                        stdout_redirector = self.OutputRedirector(lambda text: self.append_formatted_output(text))
                        stderr_redirector = self.OutputRedirector(lambda text: self.append_formatted_output(text))
                        stdin_redirector = self.StdinRedirector(self.input_queue)
                        stdin_redirector.parent = self  # Set reference to parent for UI access
                        
                        # Replace with our redirectors
                        sys.stdout = stdout_redirector
                        sys.stderr = stderr_redirector
                        sys.stdin = stdin_redirector
                        
                        # Add scripts directory to sys.path for imports if not already there
                        if scripts_dir not in sys.path:
                            sys.path.insert(0, scripts_dir)
                            print(f"Added scripts directory to sys.path: {scripts_dir}")
                        
                        # Add app directory to path as well
                        app_dir = os.path.dirname(scripts_dir)
                        if app_dir not in sys.path:
                            sys.path.insert(0, app_dir)
                            print(f"Added app directory to sys.path: {app_dir}")
                            
                        # Print current sys.path for debugging
                        print("Python sys.path:")
                        for path in sys.path:
                            print(f"  - {path}")
                        
                        # ---- Safely check for interruption ----
                        # Create a helper function to check if we should stop
                        def should_stop():
                            if hasattr(self, 'stop_requested') and self.stop_requested:
                                return True
                            return False
                        
                        # Check early for stop request
                        if should_stop():
                            raise KeyboardInterrupt("Script interrupted before it could start")
                            
                        # Import the script as a module and execute it
                        import importlib.util
                        print(f"Attempting to import: {script_path}")
                        
                        # Add periodic interrupt checks during import and module loading
                        # which can be slow operations
                        spec = None
                        try:
                            spec = importlib.util.spec_from_file_location("script_module", script_path)
                            # Check again after spec creation
                            if should_stop():
                                raise KeyboardInterrupt("Script interrupted during module loading")
                            
                            if spec is None:
                                raise ImportError(f"Could not create spec for {script_path}")
                                
                            module = importlib.util.module_from_spec(spec)
                            
                            # Check again after module creation
                            if should_stop():
                                raise KeyboardInterrupt("Script interrupted during module creation")
                                
                            print("Module created, executing...")
                        except KeyboardInterrupt:
                            raise  # Let interrupt pass through
                        except Exception as import_error:
                            print(f"Error loading module: {import_error}")
                            raise
                        
                        # Check periodically for stop request
                        def patched_sleep(seconds):
                            # Check immediately before sleeping
                            if should_stop():
                                raise KeyboardInterrupt("Script interrupted during sleep")
                                
                            # Break sleep into smaller chunks and check for stop request
                            end_time = time.time() + seconds
                            while time.time() < end_time:
                                if should_stop():
                                    raise KeyboardInterrupt("Script interrupted during sleep")
                                # Sleep in small increments
                                original_time_sleep(min(0.03, end_time - time.time()))
                        
                        # Patch time.sleep to periodically check for interrupts
                        time.sleep = patched_sleep
                        
                        # Also patch sys.excepthook to catch any uncaught exceptions
                        # and check stop flag before processing them
                        original_excepthook = sys.excepthook
                        def patched_excepthook(exctype, value, traceback):
                            # Check if we should stop before handling any other exception
                            if should_stop():
                                print("\n*** Script execution interrupted by user during exception handling ***")
                                raise KeyboardInterrupt("Script interrupted during exception handling")
                            # Call the original excepthook
                            return original_excepthook(exctype, value, traceback)
                        sys.excepthook = patched_excepthook
                        
                        try:
                            # Check one last time before executing
                            if should_stop():
                                raise KeyboardInterrupt("Script interrupted before execution")
                                
                            # Execute the module
                            spec.loader.exec_module(module)
                            
                            # Check if the module has a main() function and execute it
                            if hasattr(module, 'main'):
                                # Check again before main execution
                                if should_stop():
                                    raise KeyboardInterrupt("Script interrupted before main() execution")
                                    
                                print("Found main() function, executing it...")
                                module.main()
                            elif hasattr(module, '__name__') and module.__name__ == '__main__':
                                print("Module has __name__ == '__main__' check, simulating main module execution...")
                                # This approach is useful for scripts that use if __name__ == '__main__' pattern
                                # but don't have an explicit main() function
                                
                            print("Module execution completed successfully")
                            # Use QMetaObject.invokeMethod to call script_finished from UI thread
                            self.script_finished(0, QProcess.ExitStatus.NormalExit)
                        finally:
                            # Important: Set flags first to indicate we're done
                            self.stop_requested = False
                            
                            # Restore excepthook
                            sys.excepthook = original_excepthook
                            
                            # Clean up standard streams first
                            try:
                                # Restore original stdout/stderr/stdin
                                sys.stdout = old_stdout
                                sys.stderr = old_stderr
                                sys.stdin = old_stdin
                            except Exception as stream_error:
                                print(f"Error restoring standard streams: {stream_error}")
                            
                            try:
                                # Restore original sys.path
                                sys.path = old_sys_path
                            except Exception as path_error:
                                print(f"Error restoring sys.path: {path_error}")
                            
                            try:
                                # Restore original time.sleep
                                time.sleep = original_time_sleep
                            except Exception as sleep_error:
                                print(f"Error restoring time.sleep: {sleep_error}")
                            
                            # Handle thread and UI cleanup using separate try blocks
                            try:
                                # Clean up the bundled mode
                                self.bundled_mode_active = False
                            except Exception as flag_error:
                                print(f"Error resetting bundled_mode_active: {flag_error}")
                                
                            try:
                                if hasattr(self, 'bundled_input_thread') and self.bundled_input_thread and self.bundled_input_thread.is_alive():
                                    try:
                                        self.bundled_input_thread.join(timeout=1.0)
                                    except Exception as join_error:
                                        print(f"Error joining bundled input thread: {join_error}")
                                self.bundled_input_thread = None
                            except Exception as thread_error:
                                print(f"Error cleaning up input thread: {thread_error}")
                            
                            # Disable input field (with maximum safety)
                            try:
                                if hasattr(self, 'input_field') and self.input_field:
                                    self.input_field.setEnabled(False)
                            except Exception as ui_error:
                                print(f"Error disabling input field: {ui_error}")
                                
                            # Finally clear the thread reference
                            self.script_thread = None
                            
                    except KeyboardInterrupt:
                        try:
                            print("\nScript execution interrupted by user.")
                            # Explicitly catch potential errors during script_finished
                            try:
                                self.script_finished(-9, QProcess.ExitStatus.NormalExit)  # Use -9 to indicate user interruption
                            except Exception as finish_error:
                                print(f"Error during script_finished after interruption: {finish_error}")
                                # Manual cleanup as last resort
                                self.bundled_mode_active = False
                                self.stop_requested = False
                        except Exception as outer_error:
                            # Last defense against app crashes
                            print(f"Critical error handling interruption: {outer_error}")
                    except Exception as e:
                        try:
                            import traceback
                            error_text = f"Error executing script: {e}\n"
                            self.append_formatted_output(error_text, bold=False)
                            traceback_text = traceback.format_exc()
                            self.append_formatted_output(traceback_text, bold=False)
                            # Explicitly catch potential errors during script_finished
                            try:
                                self.script_finished(1, QProcess.ExitStatus.CrashExit)
                            except Exception as finish_error:
                                print(f"Error during script_finished after exception: {finish_error}")
                                # Manual cleanup as last resort
                                self.bundled_mode_active = False
                                self.stop_requested = False
                        except Exception as outer_error:
                            # Last defense against app crashes
                            print(f"Critical error handling script exception: {outer_error}")
                
                # Start the script thread
                self.script_thread = threading.Thread(target=run_script_in_thread)
                self.script_thread.daemon = True
                self.script_thread.start()
                
                # We don't do the try/except here anymore since it's handled in the thread
                # Instead we'll rely on the thread to update the UI
            else:
                # Normal execution with QProcess (for development environment)
                self.process = QProcess(self) # Parent to widget for auto-cleanup
                self.process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
                self.process.setWorkingDirectory(scripts_dir) # Use the main scripts_dir as CWD

                # --- Set environment to force UTF-8 for IO ---
                environment = QProcessEnvironment.systemEnvironment() # Get system environment
                environment.insert("PYTHONIOENCODING", "utf-8") # Set the variable
                self.process.setProcessEnvironment(environment) # Apply to this process
                # -----------------------------------------------

                # Connect signals
                self.process.readyReadStandardOutput.connect(self.handle_output)
                self.process.finished.connect(self.handle_finish)
                self.process.errorOccurred.connect(self.handle_error)
                # Connect started signal to enable input
                self.process.started.connect(self.enable_input)

                command = sys.executable
                args = ["-u", script_path]
                
                # Use append_formatted_output for initial messages (regular font)
                exec_line = f"Executing: {shlex.quote(command)} {' '.join(shlex.quote(arg) for arg in args)}\n"
                # Ensure initial messages have newlines
                self.append_formatted_output(exec_line, bold=False)
                separator_line = "-" * 50 + "\n"
                self.append_formatted_output(separator_line, bold=False)
                
                self.process.start(command, args)
                # QProcess runs asynchronously using the main event loop
        else:
            # Ensure error messages have newlines
            error_msg = f"Error: No script mapping found for key '{script_key}'.\n"
            self.append_formatted_output(error_msg, bold=False)
            self.title_label.setText("Script Output - Error")
            self.input_field.setEnabled(False)
            self.stop_button.setStyleSheet(self.stop_button_style_inactive) # Ensure button is gray

    def stop_current_script(self):
        """Stops the currently running script process or thread in a gentle way.
        Instead of directly manipulating thread objects, this sets a flag and lets
        the script decide when to exit cleanly."""
        
        logging.info("Attempting to stop current script safely...")
        
        # Signal to all script components that they should stop
        self.stop_requested = True

        # Add visible indication that stop was requested - all wrapped in try/except
        try:
            self.append_formatted_output("\n*** STOPP angefordert - Warte auf sichere Beendigung des Skripts... ***\n", bold=True)
            # Make the stop button show "stopping..." state
            self.stop_button.setText("STOPPING...")
            self.stop_button.setEnabled(False)
            self.stop_button.setStyleSheet("""
                QPushButton {
                    background-color: #FFA500; /* Orange */
                    color: white;
                    padding: 5px 15px;
                    border-radius: 4px;
                    border: 1px solid #FF8C00; /* Darker orange */
                    min-width: 60px;
                }
            """)
            # Process events to update UI
            QApplication.processEvents()
        except Exception as ui_error:
            # Never let UI errors propagate to app event loop
            logging.warning(f"Non-critical UI error during stop signaling: {ui_error}")
        
        # For QProcess, we can be more direct since it's safer
        if self.process and self.process.state() != QProcess.ProcessState.NotRunning:
            try:
                logging.info("Stopping QProcess script.")
                self.process.kill()
                # Clear reference immediately to avoid double kills
                temp_process = self.process
                self.process = None
                # Wait for finish after clearing reference
                if not temp_process.waitForFinished(1000):  # Wait 1 second
                    logging.warning("Process did not finish after kill signal and 1s wait.")
                else:
                    logging.info("QProcess finished after kill signal.")
            except Exception as process_error:
                # Never let process errors propagate to app event loop
                logging.error(f"Error killing QProcess: {process_error}")
                # Still make sure to clear the reference
                self.process = None

        # For bundled mode, we don't directly interact with the thread
        # We just set flags and let the readline or patched_sleep methods handle it
        if self.bundled_mode_active:
            logging.info("Stop signal sent to bundled script. Waiting for script to notice...")
            
            # Queue a timed update - if script hasn't stopped after 5 seconds, 
            # update the UI again to indicate we're still waiting
            def check_if_stopped():
                try:
                    # If script is still active after timeout
                    if self.bundled_mode_active and self.stop_requested:
                        try:
                            self.append_formatted_output("\n*** Warte weiter auf Beendigung... Bitte haben Sie Geduld! ***\n", bold=True)
                            # Process events to keep UI responsive
                            QApplication.processEvents()
                        except Exception as e:
                            # Never let UI errors propagate to timer callback
                            logging.error(f"Error in stop check timer: {e}")
                except Exception as e:
                    # Catch-all for any error in timer
                    logging.error(f"Unexpected error in stop check timer: {e}")
            
            # Use a simple timer to check progress without blocking UI
            try:
                timer = threading.Timer(5.0, check_if_stopped)
                timer.daemon = True
                timer.start()
            except Exception as timer_error:
                # Never let timer errors propagate to app event loop
                logging.error(f"Error starting timer: {timer_error}")
        
        # For any other case, just make sure the UI state is consistent
        # script_finished will be called by the script itself when it detects the stop flag
        if not self.bundled_mode_active and not self.process:
            try:
                # No active script, so clean up the UI right away
                logging.info("No active script found, resetting UI only.")
                self.script_finished(-1, force_ui_reset=True)
            except Exception as e:
                # Never let script_finished errors propagate to app event loop
                logging.error(f"Error in script_finished for inactive state: {e}")
                # Do minimal UI reset directly
                try:
                    self.stop_button.setText("STOP")
                    self.stop_button.setEnabled(True)
                    self.stop_button.setStyleSheet(self.stop_button_style_inactive)
                    self.input_field.setEnabled(False)
                except Exception as ui_reset_error:
                    # Final catch-all for UI reset
                    logging.error(f"Error in emergency UI reset: {ui_reset_error}")
                    
        # Return True to indicate success to event handlers
        return True

    def is_prompt_line(self, line):
        """More robust heuristic to determine if a line is likely an input prompt."""
        stripped = line.strip()
        # Common prompt endings (characters themselves)
        if stripped.endswith(':') or stripped.endswith('?') or stripped.endswith('>') or stripped.endswith('#'):
            return True
        # Common prompt endings (character + space)
        if line.endswith(': ') or line.endswith('? ') or line.endswith('> ') or line.endswith('# '):
            return True
        # Specific case from user: ends with ') ' perhaps after stripping?
        if stripped.endswith(')') and line.endswith(') '):
            return True

        return False

    def append_formatted_output(self, text, bold=None):
        """Appends text, applying prompt formatting only to the last line if auto-detecting.
        This method is critical for UI updates and must never crash the application."""
        try:
            # Validate input first
            if text is None:
                return
                
            # Convert to string if not already
            if not isinstance(text, str):
                text = str(text)
                
            cursor = self.output_area.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.End)

            # --- Format Definitions ---
            # Default format
            default_format = QTextCharFormat()
            default_font = QFont(self.base_font_family, self.base_font_size)
            default_font.setWeight(QFont.Weight.Normal)
            default_format.setFont(default_font)
            default_format.setForeground(self.default_text_color)

            # Prompt format
            prompt_format = QTextCharFormat()
            prompt_font = QFont(self.base_font_family, self.base_font_size)
            prompt_font.setWeight(QFont.Weight.Bold)
            prompt_format.setFont(prompt_font)
            prompt_format.setForeground(self.prompt_text_color)
            # --- End Format Definitions ---

            # Apply explicit formatting if requested
            if bold is not None:
                cursor.setCharFormat(prompt_format if bold else default_format)
                cursor.insertText(text)
            else:
                # Auto-detect: Format last line based on prompt check
                last_newline_pos = text.rfind('\n')
                if last_newline_pos != -1:
                    # Text contains newline(s)
                    part1 = text[:last_newline_pos + 1] # Includes the newline
                    part2 = text[last_newline_pos + 1:] # The part after the last newline

                    # Append part1 with default format
                    cursor.setCharFormat(default_format)
                    cursor.insertText(part1)

                    # Append part2 (last line) with detected format
                    if part2: # Only if there's text after the last newline
                        is_prompt = self.is_prompt_line(part2)
                        cursor.setCharFormat(prompt_format if is_prompt else default_format)
                        cursor.insertText(part2)
                else:
                    # No newline in the text, check the whole text
                    is_prompt = self.is_prompt_line(text)
                    cursor.setCharFormat(prompt_format if is_prompt else default_format)
                    cursor.insertText(text)

            # Reset format for subsequent typing or appends outside this method
            cursor.setCharFormat(default_format)
            self.output_area.ensureCursorVisible() # Scroll to the end
            
            # Process events to update UI immediately
            try:
                QApplication.processEvents()
            except Exception:
                # Ignore process events errors
                pass
                
        except Exception as e:
            # Critical failure - do NOT propagate exceptions from this method
            try:
                logging.critical(f"Critical error in append_formatted_output: {e}")
                # Try to append error message in simplest way possible
                cursor = self.output_area.textCursor()
                cursor.movePosition(QTextCursor.MoveOperation.End)
                cursor.insertText(f"\n*** ERROR DISPLAYING OUTPUT: {e} ***\n")
            except Exception as final_error:
                # Absolutely last resort - log only
                logging.critical(f"FATAL UI ERROR: {final_error}")
                # At this point we've done everything we can do

    def script_finished(self, exit_code, exit_status=QProcess.ExitStatus.NormalExit, force_ui_reset=False):
        """Common cleanup actions when a script finishes or is stopped."""
        log_msg = f"Script finished cleanup initiated. Exit Code: {exit_code}, Status: {exit_status}, Force UI Reset: {force_ui_reset}"
        if exit_code == 0:
            logging.info(log_msg)
        else:
            logging.warning(log_msg)

        # If we're called from a non-GUI thread, use invokeMethod to process in the GUI thread
        if threading.current_thread() is not threading.main_thread():
            try:
                # Process events to ensure UI updates
                QApplication.processEvents()
                logging.debug("script_finished called from non-main thread, processing UI updates")
            except Exception as e:
                logging.warning(f"Error processing events from non-main thread: {e}")

        # Only perform cleanup if not already cleaned up or forced
        if self.process or self.bundled_mode_active or force_ui_reset:
            # First update flags to prevent recursive calls
            was_bundled_active = self.bundled_mode_active
            self.bundled_mode_active = False
            self.stop_requested = False
            
            # Remember if we need to inform about a stop
            was_stopped = exit_code == -9
            
            try:
                # Update the button first
                self.stop_button.setText("STOP")
                self.stop_button.setStyleSheet(self.stop_button_style_inactive)
                self.stop_button.setEnabled(True)  # Re-enable for future use
                self.input_field.setEnabled(False) # Disable input when finished

                # Handle process cleanup carefully
                if self.process:
                    # Disconnect signals to prevent potential late calls after object deletion
                    try: # Wrap in try-except as disconnecting might fail if object state is weird
                        self.process.readyReadStandardOutput.disconnect(self.handle_output)
                        self.process.errorOccurred.disconnect(self.handle_error)
                        self.process.finished.disconnect(self.handle_finish)
                        self.process.started.disconnect(self.enable_input)
                    except (TypeError, RuntimeError) as e:
                        logging.warning(f"Error disconnecting QProcess signals: {e}")
                    self.process.deleteLater() # Schedule for deletion
                    self.process = None # Clear reference

                # Display appropriate message for the user
                if was_stopped:
                    success_message = "\n--- Skript wurde auf Anforderung beendet ---\n"
                    self.append_formatted_output(success_message, bold=True)
                elif exit_code != 0:
                    final_message = f"\n--- Skript beendet mit Exit-Code: {exit_code} ---\n"
                    self.append_formatted_output(final_message, bold=False)
                else:
                    # Success message for normal completion
                    self.append_formatted_output("\n--- Skript erfolgreich abgeschlossen ---\n", bold=False)
                
                # If it was a bundle mode script, ensure we clean up
                if was_bundled_active:
                    # Clear thread reference - this is safe because we're not joining the thread
                    self.script_thread = None
                
                logging.info("Script finished UI cleanup complete.")
            except Exception as e:
                # Protect against any UI exceptions that might occur during cleanup
                logging.error(f"Error during script_finished UI cleanup: {e}")
        else:
            logging.debug("Script finished called, but no active process or bundled mode detected, and force_ui_reset is False. Skipping UI reset.")
            # No active process or thread to clean up

    def set_initial_state(self):
        self.stop_current_script() # Ensure no process is running
        self.title_label.setText("Script Output")
        self.output_area.clear() # Clear previous content
        initial_msg = "Select a script tile from the KISIM page to run it.\n"
        self.append_formatted_output(initial_msg, bold=False)
        self.input_field.setEnabled(False)

    def enable_input(self):
        # Connected to QProcess.started signal or called directly from bundled mode
        if not self.bundled_mode_active: # Only enable for QProcess started
            logging.info("QProcess started, enabling input field.")
            self.input_field.setEnabled(True)
            self.input_field.setFocus()
        else:
            logging.debug("enable_input called in bundled mode, input handled by readline override.")
            pass # Input enabling/disabling is handled by StdinRedirector.readline

    def send_input(self):
        # --- Use QProcess write --- 
        input_text = self.input_field.text()
        self.input_field.clear()
        logging.info(f"Sending input: '{input_text}'")
        
        if self.bundled_mode_active:
            logging.debug("Putting input into queue for bundled script.")
            # Put the input into the queue for the bundled script's stdin redirector
            self.input_buffer = input_text
            # self.input_queue.put(input_text + '\n')
            # Disable input field after sending, it will be re-enabled by readline
            self.input_field.setEnabled(False)
            
            # Append the sent input to the output area for visibility
            # Use a different color/style for user input?
            input_display_text = f"> {input_text}\n"
            self.append_formatted_output(input_display_text, bold=True) # Maybe bold input?
            
        elif self.process and self.process.state() == QProcess.ProcessState.Running:
            logging.debug("Writing input to QProcess stdin.")
            # Append newline as most command-line tools expect it
            full_input = input_text + "\n" 
            self.process.write(full_input.encode('utf-8'))
            # Optionally disable input field briefly?
            # self.input_field.setEnabled(False) # Could re-enable on next output?
            
            # Append the sent input to the output area for visibility
            input_display_text = f"> {input_text}\n"
            self.append_formatted_output(input_display_text, bold=True) # Maybe bold input?
        else:
            logging.warning("send_input called but no running process or bundled script active.")
            # Optionally show a message? Or just ignore.
            pass

    def closeEvent(self, event):
        """Ensure script is stopped when the widget (or window) is closed."""
        logging.info("closeEvent triggered for CmdScriptsPage. Stopping script.")
        self.stop_current_script()
        super().closeEvent(event)

    def stdin_reader(self):
        """Placeholder or alternative input handling if needed."""
        logging.debug("stdin_reader called (currently placeholder).")
        # This might be used if a different input mechanism were required
        pass


# Example usage for testing this page directly
if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)

    # --- Example Setup for Direct Testing ---
    # Create dummy script directory and file if they don't exist
    if not os.path.exists(scripts_dir):
        os.makedirs(scripts_dir)
    test_script_path = os.path.join(scripts_dir, "test_script.py")
    if not os.path.exists(test_script_path):
        with open(test_script_path, "w") as f:
            f.write("import time\n")
            f.write("import sys\n")
            f.write("import os\n") # Added os import
            f.write("print('Hello from test_script.py!')\n")
            f.write("print(f'Running with Python: {sys.executable}')\n")
            f.write("print(f'Working Directory: {os.getcwd()}')\n")
            f.write("user_input = input(\'Enter something: \')\n") # Add input test
            f.write("print(f'You entered: {user_input}\')\n")
            f.write("time.sleep(1)\n")
            f.write("print(\'This is line 2.\')\n")
            # f.write("sys.stderr.write(\'This is an error message.\\n\')\n") # Uncomment to test stderr
            f.write("time.sleep(1)\n")
            f.write("print(\'Test script finished.\')\n")

    # Add mappings for test scripts *to the imported list* for testing
    # Note: This modifies the list only within the scope of this test block
    script_definitions.append(("Test Tile", "test_script.py"))
    script_definitions.append(("Nonexistent Tile", "no_script.py")) # Test error handling
    # Ensure lab.py is testable if not already in definitions
    if not any(fname == "lab.py" for _, fname in script_definitions):
         script_definitions.append(("Labor Test", "lab.py")) 

    # Create lab.py if it doesn't exist for testing
    lab_script_path = os.path.join(scripts_dir, "lab.py")
    if not os.path.exists(lab_script_path):
        with open(lab_script_path, "w") as f:
            f.write("import sys\n")
            f.write("print('hello, this is lab.py')\n")
            f.write("number = input(\'enter digit: \')\n")
            f.write("if number.isdigit():\n")
            f.write("    print(f'You entered the number: {number}')\n")
            f.write("else:\n")
            f.write("    print('Invalid input.')\n")

    # -----------------------------------------

    window = QWidget() # Main window container for testing
    main_layout = QVBoxLayout(window)
    cmd_page = CmdScriptsPage()
    main_layout.addWidget(cmd_page)

    # Add buttons to simulate selecting a script
    test_button = QPushButton("Run Test Script (with input)")
    # Generate key for the test tile dynamically for the connection
    test_key = generate_script_key("Test Tile") 
    test_button.clicked.connect(lambda checked, key=test_key: cmd_page.run_script_by_key(key))
    main_layout.addWidget(test_button)
    
    lab_button = QPushButton("Run lab.py Script")
    # Find or use a default key for lab
    lab_key = "labor" # Assume standard key
    for tile_name, fname in script_definitions:
        if fname == "lab.py":
            lab_key = generate_script_key(tile_name)
            break
    lab_button.clicked.connect(lambda checked, key=lab_key: cmd_page.run_script_by_key(key))
    main_layout.addWidget(lab_button)

    error_button = QPushButton("Run Nonexistent Script")
    nonexistent_key = generate_script_key("Nonexistent Tile")
    error_button.clicked.connect(lambda checked, key=nonexistent_key: cmd_page.run_script_by_key(key))
    main_layout.addWidget(error_button)

    no_key_button = QPushButton("Run Invalid Key")
    no_key_button.clicked.connect(lambda: cmd_page.run_script_by_key("invalid_key"))
    main_layout.addWidget(no_key_button)
    
    stop_button = QPushButton("Stop Current Script")
    stop_button.clicked.connect(cmd_page.stop_current_script)
    main_layout.addWidget(stop_button)

    window.setWindowTitle("CmdScriptsPage Test (QProcess)")
    window.setGeometry(100, 100, 700, 600) # Increased height for buttons
    window.show()

    # Set initial state after showing the window
    cmd_page.set_initial_state()

    sys.exit(app.exec()) 