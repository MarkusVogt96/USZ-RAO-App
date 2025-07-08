"""
Path management utilities for Backoffice functionality.

This module provides centralized path management for all Backoffice pages,
implementing priority logic for network vs local paths.
"""

import os
import logging
from pathlib import Path
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class BackofficePathManager:
    """Manages path resolution for Backoffice functionality with network/local priority."""
    
    # Class-level variables to track path status
    _network_path_available = None
    _local_path_available = None
    _warning_shown = False
    
    NETWORK_BASE_PATH = Path("K:/RAO_Projekte/App/tumorboards")
    LOCAL_BASE_PATH = Path.home() / "tumorboards"
    
    @classmethod
    def get_backoffice_path(cls, show_warnings=True):
        """
        Get the appropriate backoffice path with priority logic.
        
        Priority:
        1. Network path: K:\RAO_Projekte\App\tumorboards\_Backoffice
        2. Local path: {user_home}\tumorboards\_Backoffice
        
        Args:
            show_warnings (bool): Whether to show warning dialogs for path issues
            
        Returns:
            tuple: (Path object for _Backoffice directory, bool indicating if network path was used)
            
        Raises:
            FileNotFoundError: If neither path is available
        """
        # Check network path
        network_backoffice = cls.NETWORK_BASE_PATH / "_Backoffice"
        local_backoffice = cls.LOCAL_BASE_PATH / "_Backoffice"
        
        # Update class-level status variables
        cls._network_path_available = network_backoffice.exists()
        cls._local_path_available = local_backoffice.exists()
        
        logging.info(f"Path status check: Network={cls._network_path_available}, Local={cls._local_path_available}")
        
        # Priority 1: Network path
        if cls._network_path_available:
            logging.info(f"Using network backoffice path: {network_backoffice}")
            return network_backoffice, True
        
        # Priority 2: Local path
        if cls._local_path_available:
            logging.info(f"Using local backoffice path: {local_backoffice}")
            
            # Show warning dialog if requested and not already shown
            if show_warnings and not cls._warning_shown:
                cls._show_network_unavailable_warning()
                cls._warning_shown = True
            
            return local_backoffice, False
        
        # Neither path available
        if show_warnings:
            cls._show_no_paths_available_error()
        
        raise FileNotFoundError("Neither network nor local backoffice path is available")
    
    @classmethod
    def get_tumorboard_base_path(cls):
        """
        Get the base tumorboard path (without _Backoffice suffix).
        
        Returns:
            tuple: (Path object for base tumorboard directory, bool indicating if network path was used)
        """
        # Check network path
        if cls.NETWORK_BASE_PATH.exists():
            return cls.NETWORK_BASE_PATH, True
        
        # Fallback to local path
        if cls.LOCAL_BASE_PATH.exists():
            return cls.LOCAL_BASE_PATH, False
        
        raise FileNotFoundError("Neither network nor local tumorboard base path is available")
    
    @classmethod
    def reset_warning_state(cls):
        """Reset the warning state to allow warnings to be shown again."""
        cls._warning_shown = False
    
    @classmethod
    def _show_network_unavailable_warning(cls):
        """Show warning dialog when only local path is available."""
        msg = QMessageBox()
        msg.setWindowTitle("Netzwerkverbindung nicht verfügbar")
        msg.setText("Achtung! Es besteht kein Netzwerkzugriff zum K:\\ (RAO:Daten)-Server! "
                   "Es wurde auf den lokalen Pfad zu Testzwecken zurückgegriffen.\n\n"
                   "Sämtliche Änderungen werden nicht auf dem Server gespeichert!")
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        
        # Apply custom styling to match the application theme
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #1a2633;
                color: white;
                font-size: 14px;
                border: 2px solid #FFD700;
                border-radius: 8px;
            }
            QMessageBox QLabel {
                color: white;
                font-size: 14px;
                padding: 15px;
                font-weight: 500;
            }
            QPushButton {
                background-color: #114473;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
                min-width: 100px;
                min-height: 35px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #1a5a9e;
            }
            QPushButton:pressed {
                background-color: #0d3355;
            }
        """)
        
        # Set button text to German
        msg.button(QMessageBox.StandardButton.Ok).setText("OK")
        
        # Set font
        font = QFont("Helvetica", 13)
        msg.setFont(font)
        
        logging.warning("Showing network unavailable warning to user")
        msg.exec()
    
    @classmethod
    def _show_no_paths_available_error(cls):
        """Show error dialog when neither path is available."""
        msg = QMessageBox()
        msg.setWindowTitle("Backoffice nicht verfügbar")
        msg.setText(f"Weder der Netzwerkpfad K:\\ (RAO_Daten) noch einer lokaler "
                   f"{Path.home()}\\tumorboards-Pfad konnten gefunden werden. "
                   f"Backoffice laden ist nicht möglich.")
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        
        # Apply custom styling to match the application theme
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #1a2633;
                color: white;
                font-size: 14px;
                border: 2px solid #FF6B6B;
                border-radius: 8px;
            }
            QMessageBox QLabel {
                color: white;
                font-size: 14px;
                padding: 15px;
                font-weight: 500;
            }
            QPushButton {
                background-color: #114473;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
                min-width: 100px;
                min-height: 35px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #1a5a9e;
            }
            QPushButton:pressed {
                background-color: #0d3355;
            }
        """)
        
        # Set button text to German
        msg.button(QMessageBox.StandardButton.Ok).setText("OK")
        
        # Set font
        font = QFont("Helvetica", 13)
        msg.setFont(font)
        
        logging.error("Showing no paths available error to user")
        msg.exec()
    
    @classmethod
    def is_network_path_available(cls):
        """Check if the network path is currently available."""
        return cls.NETWORK_BASE_PATH.exists()
    
    @classmethod
    def is_local_path_available(cls):
        """Check if the local path is currently available."""
        return cls.LOCAL_BASE_PATH.exists()
    
    @classmethod
    def get_current_path_status(cls):
        """
        Get current path availability status.
        
        Returns:
            dict: Status information about path availability
        """
        network_available = cls.is_network_path_available()
        local_available = cls.is_local_path_available()
        
        if network_available:
            status = "network"
            message = "Netzwerkpfad verfügbar"
        elif local_available:
            status = "local"
            message = "Nur lokaler Pfad verfügbar"
        else:
            status = "none"
            message = "Keine Pfade verfügbar"
        
        return {
            "status": status,
            "message": message,
            "network_available": network_available,
            "local_available": local_available,
            "network_path": str(cls.NETWORK_BASE_PATH),
            "local_path": str(cls.LOCAL_BASE_PATH)
        } 