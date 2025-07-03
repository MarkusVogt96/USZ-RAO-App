import json
import os
import logging
from datetime import datetime
from pathlib import Path
import shutil

class BillingTracker:
    """Handles billing status tracking for completed tumorboards"""
    
    def __init__(self):
        # Base paths
        self.backoffice_path = Path.home() / "tumorboards" / "_Backoffice"
        self.log_path = self.backoffice_path / "log_abrechnungen"
        self.backup_path = self.backoffice_path / "backup" / "json_abrechnungen"
        self.status_file = self.log_path / "abrechnung_status.json"
        
        # Ensure directories exist
        self._ensure_directories()
        
    def _ensure_directories(self):
        """Create necessary directories if they don't exist"""
        try:
            self.log_path.mkdir(parents=True, exist_ok=True)
            self.backup_path.mkdir(parents=True, exist_ok=True)
            logging.info(f"Billing tracker directories ensured: {self.log_path}")
        except Exception as e:
            logging.error(f"Error creating billing tracker directories: {e}")
            
    def _get_current_windows_user(self):
        """Get current Windows username"""
        try:
            return os.getlogin()
        except Exception as e:
            logging.warning(f"Could not get Windows username: {e}")
            return "unknown"
            
    def _get_timestamp(self):
        """Get current timestamp in German format"""
        return datetime.now().strftime("%d.%m.%Y %H:%M:%S")
        
    def _create_backup(self):
        """Create backup of current JSON file before modification"""
        if not self.status_file.exists():
            return  # No file to backup
            
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
            backup_filename = f"abrechnung_status_{timestamp}.json"
            backup_file = self.backup_path / backup_filename
            
            shutil.copy2(self.status_file, backup_file)
            logging.info(f"Created backup: {backup_file}")
            
        except Exception as e:
            logging.error(f"Error creating backup: {e}")
            
    def _load_status_data(self):
        """Load billing status data from JSON file"""
        if not self.status_file.exists():
            return {"abgerechnete_tumorboards": []}
            
        try:
            with open(self.status_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Error loading billing status: {e}")
            return {"abgerechnete_tumorboards": []}
            
    def _save_status_data(self, data):
        """Save billing status data to JSON file"""
        try:
            self._create_backup()  # Backup before saving
            
            with open(self.status_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logging.info("Billing status data saved successfully")
            
        except Exception as e:
            logging.error(f"Error saving billing status: {e}")
            raise
            
    def mark_as_billed(self, tumorboard, datum, art_der_abrechnung):
        """
        Mark a tumorboard as billed
        
        Args:
            tumorboard (str): Name of tumorboard entity
            datum (str): Date in format dd.mm.yyyy
            art_der_abrechnung (str): "script" or "user"
        """
        try:
            data = self._load_status_data()
            
            # Check if already exists
            for entry in data["abgerechnete_tumorboards"]:
                if entry["tumorboard"] == tumorboard and entry["datum"] == datum:
                    # Update existing entry
                    entry["abgerechnet_am"] = self._get_timestamp()
                    entry["benutzer"] = self._get_current_windows_user()
                    entry["art_der_abrechnung"] = art_der_abrechnung
                    self._save_status_data(data)
                    logging.info(f"Updated billing status: {tumorboard} {datum} ({art_der_abrechnung})")
                    return
            
            # Add new entry
            new_entry = {
                "tumorboard": tumorboard,
                "datum": datum,
                "abgerechnet_am": self._get_timestamp(),
                "benutzer": self._get_current_windows_user(),
                "art_der_abrechnung": art_der_abrechnung
            }
            
            data["abgerechnete_tumorboards"].append(new_entry)
            self._save_status_data(data)
            logging.info(f"Marked as billed: {tumorboard} {datum} ({art_der_abrechnung})")
            
        except Exception as e:
            logging.error(f"Error marking as billed: {e}")
            raise
            
    def is_billed(self, tumorboard, datum):
        """
        Check if a tumorboard is already billed
        
        Args:
            tumorboard (str): Name of tumorboard entity
            datum (str): Date in format dd.mm.yyyy
            
        Returns:
            bool: True if billed, False otherwise
        """
        try:
            data = self._load_status_data()
            
            for entry in data["abgerechnete_tumorboards"]:
                if entry["tumorboard"] == tumorboard and entry["datum"] == datum:
                    return True
                    
            return False
            
        except Exception as e:
            logging.error(f"Error checking billing status: {e}")
            return False
            
    def get_billing_status(self, tumorboard, datum):
        """
        Get complete billing information for a tumorboard
        
        Args:
            tumorboard (str): Name of tumorboard entity
            datum (str): Date in format dd.mm.yyyy
            
        Returns:
            dict or None: Billing information or None if not billed
        """
        try:
            data = self._load_status_data()
            
            for entry in data["abgerechnete_tumorboards"]:
                if entry["tumorboard"] == tumorboard and entry["datum"] == datum:
                    return entry
                    
            return None
            
        except Exception as e:
            logging.error(f"Error getting billing status: {e}")
            return None
            
    def get_all_billed_tumorboards(self):
        """
        Get all billed tumorboards
        
        Returns:
            list: List of all billing entries
        """
        try:
            data = self._load_status_data()
            return data.get("abgerechnete_tumorboards", [])
            
        except Exception as e:
            logging.error(f"Error getting all billed tumorboards: {e}")
            return [] 