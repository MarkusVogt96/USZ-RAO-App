import pandas as pd
import logging
from pathlib import Path
from openpyxl import Workbook, load_workbook
from openpyxl.utils.dataframe import dataframe_to_rows
import os
from .database_utils import TumorboardDatabase




def export_tumorboard_to_collection(tumorboard_name, date_str):
    """Export a specific tumorboard session to the collection Excel file"""
    try:
        # Paths
        tumorboard_dir = Path.home() / "tumorboards" / tumorboard_name
        daily_excel_path = tumorboard_dir / date_str / f"{date_str}.xlsx"
        
        # Find collection file flexibly - look for any file starting with "alle_tumorboards_"
        collection_file_path = None
        for file in tumorboard_dir.glob("alle_tumorboards_*.xlsx"):
            collection_file_path = file
            break
        
        # Check if daily Excel file exists
        if not daily_excel_path.exists():
            logging.error(f"Daily Excel file not found: {daily_excel_path}")
            return False
        
        # Check if collection file exists
        if not collection_file_path or not collection_file_path.exists():
            logging.error(f"Collection Excel file not found in {tumorboard_dir}. Looking for files starting with 'alle_tumorboards_'")
            return False
        
        # Read the daily Excel data
        daily_df = pd.read_excel(daily_excel_path, engine='openpyxl')
        
        # Load or create collection workbook
        try:
            collection_wb = load_workbook(collection_file_path)
        except Exception as e:
            logging.warning(f"Could not load existing collection file, creating new one: {e}")
            collection_wb = Workbook()
            # Remove default sheet if it exists
            if "Sheet" in collection_wb.sheetnames:
                collection_wb.remove(collection_wb["Sheet"])
        
        # Ensure the overview sheet exists and is properly named
        if "Tabelle1" in collection_wb.sheetnames:
            overview_sheet = collection_wb["Tabelle1"]
            overview_sheet.title = "Übersicht"
        elif "Übersicht" not in collection_wb.sheetnames:
            # Create overview sheet if it doesn't exist
            overview_sheet = collection_wb.create_sheet("Übersicht", 0)
            overview_sheet['A1'] = f"Sammel-Excel für Tumorboard: {tumorboard_name}"
            overview_sheet['A2'] = "Erstellt automatisch durch USZ-RAO-App"
            overview_sheet['A3'] = "Jeder Tab repräsentiert ein Tumorboard-Datum"
        
        # Check if sheet with this date already exists
        sheet_name = date_str.replace(".", "_")  # Excel sheet names can't contain dots
        
        if sheet_name in collection_wb.sheetnames:
            # Remove existing sheet to overwrite
            collection_wb.remove(collection_wb[sheet_name])
            logging.info(f"Removed existing sheet '{sheet_name}' for overwrite")
        
        # Create new sheet
        new_sheet = collection_wb.create_sheet(title=sheet_name)
        
        # Write data to new sheet
        for r in dataframe_to_rows(daily_df, index=False, header=True):
            new_sheet.append(r)
        
        # Auto-adjust column widths
        for column in new_sheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)  # Cap at 50 characters
            new_sheet.column_dimensions[column_letter].width = adjusted_width
        
        # Save collection workbook
        collection_wb.save(collection_file_path)
        
        logging.info(f"Successfully exported {tumorboard_name} {date_str} to collection Excel")
        
        # After successful collection Excel export, sync to central database
        try:
            sync_collection_to_database(tumorboard_name, collection_file_path)
        except Exception as db_error:
            logging.warning(f"Collection Excel export succeeded, but database sync failed: {db_error}")
            # Don't fail the entire operation if database sync fails
        
        return True
        
    except Exception as e:
        logging.error(f"Error exporting tumorboard to collection: {e}")
        return False


def sync_collection_to_database(tumorboard_name, collection_excel_path):
    """Sync a specific collection Excel file to the central database"""
    try:
        db = TumorboardDatabase()
        success = db.import_collection_excel(tumorboard_name, collection_excel_path)
        
        if success:
            logging.info(f"Successfully synced {tumorboard_name} collection to central database")
        else:
            logging.warning(f"Failed to sync {tumorboard_name} collection to central database")
        
        return success
        
    except Exception as e:
        logging.error(f"Error syncing collection to database for {tumorboard_name}: {e}")
        return False


def sync_all_collections_to_database():
    """Sync all collection Excel files to the central database"""
    try:
        from .database_utils import sync_all_collection_files
        return sync_all_collection_files()
        
    except Exception as e:
        logging.error(f"Error syncing all collections to database: {e}")
        return False

 