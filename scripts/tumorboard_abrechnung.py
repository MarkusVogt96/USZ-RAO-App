#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
KISIM Automatisierte Abrechnungs-Script

Dieses Script führt die automatisierte Leistungsabrechnung in QISM durch.
Es nutzt GUI-Automatisierung mit pyautogui für die Navigation in QISM.
"""

import logging
import time
import sys
import os
import UNIVERSAL
import pyautogui
import pandas as pd
import clipboard

script_dir = os.path.dirname(os.path.abspath(__file__))
screenshots_dir = os.path.join(script_dir, 'screenshots pyautogui')
image_base_path = os.path.join(screenshots_dir, "abrechnung_tumorboard")
user_home = os.path.expanduser("~") 

def process_patient(patientennummer, icd_code):
    """
    Verarbeitet einen einzelnen Patient durch den Abrechnungsworkflow.
    
    Args:
        patientennummer (str): Die bereinigte Patientennummer (ohne .0)
        icd_code (str): Der ICD-Code aus der Excel-Tabelle
    
    Returns:
        bool: True wenn erfolgreich, False bei Fehlern
    """
    print(f"Verarbeite Patient {patientennummer} mit ICD-Code {icd_code}")
    
    # Button Lupe klicken
    if not UNIVERSAL.find_and_click_button("button_lupe.png", base_path=image_base_path):
        print("Button Lupe wurde nicht gefunden")
        return False
    
    #Globale Suche sicherstellen
    if not UNIVERSAL.find_button("button_globale_suche_confirm.png", base_path=image_base_path, max_attempts=10, interval=0.1):
        print("Button button_globale_suche_confirm wurde nicht gefunden. Klicke darauf.")
        if not UNIVERSAL.find_and_click_button("button_globale_suche.png", base_path=image_base_path, max_attempts=10, interval=0.1):
            print("Button button_globale_suche wurde auch nicht gefunden. Return False.")
            return False
    time.sleep(0.1)
    
    # Button PatNr mit Offset klicken
    if not UNIVERSAL.find_and_click_button_offset("button_patnr.png", base_path=image_base_path, x_offset=70):
        print("Button PatNr wurde nicht gefunden")
        return False
    pyautogui.hotkey('ctrl', 'a')
    pyautogui.press('backspace')

    # Bereinigte Patientennummer in Zwischenspeicher und einfügen
    clipboard.copy(patientennummer)
    pyautogui.hotkey('ctrl', 'v')
    pyautogui.press('enter')
    
    #Zeige offene Fälle sicherstellen
    if not UNIVERSAL.find_button("button_zeige_offene_faelle_confirm.png", base_path=image_base_path, max_attempts=5, interval=0.05):
        print("Button zeige_offene_faelle_confirm wurde nicht gefunden")
        if not UNIVERSAL.find_and_click_button("button_zeige.png", base_path=image_base_path): print("button_zeige.png nicht gefunden."); return False
        if not UNIVERSAL.find_and_click_button("button_offene_faelle.png", base_path=image_base_path): print("button_zeige.png nicht gefunden."); return False
        if not UNIVERSAL.find_button("button_zeige_offene_faelle_confirm.png", base_path=image_base_path, max_attempts=5, interval=0.05):
            print("zeige_offene_faelle_confirm.png nicht immer noch nicht gefunden... False")
            return False
        if not UNIVERSAL.find_and_click_button_offset("button_patnr.png", base_path=image_base_path, x_offset=70):
            print("Button PatNr wurde nicht gefunden")
            return False
        pyautogui.press('enter')
        time.sleep(0.1)

    # Enter drücken
    pyautogui.press('enter')
    time.sleep(0.1)
    
    # Falltyp bestimmen
    falltyp = None

    # Erste Suche nach RAO-Buttons
    if UNIVERSAL.find_and_click_button("button_rao_ambulant.png", base_path=image_base_path, max_attempts=3, interval=0.1):
        falltyp = "ambulant"
        print("\n\n button_rao_ambulant.png nicht gefunden")
    elif UNIVERSAL.find_and_click_button("button_rao_stationaer.png", base_path=image_base_path, max_attempts=3, interval=0.1):
        falltyp = "stationaer"
        print("\n\n button_rao_stationaer.png nicht gefunden")
    else:
        # Fallback-Suche
        for _ in range(3):
            pyautogui.press('down')
        
        for _ in range(10):
            if UNIVERSAL.find_button("button_fall_ambulant.png", base_path=image_base_path, max_attempts=1, confidence=0.9):
                falltyp = "ambulant"
                pyautogui.press('enter')
                print(f"\n\n button_fall_ambulant.png gefunden. falltyp = {falltyp}")
                break
            elif UNIVERSAL.find_button("button_fall_stationaer.png", base_path=image_base_path, max_attempts=1, confidence=0.9):
                falltyp = "stationaer"
                pyautogui.press('enter')
                print(f"\n\n button_fall_stationaer.png nht gefunden. falltyp = {falltyp}")
                break
    
    if falltyp is None:
        print("Falltyp konnte nicht bestimmt werden")
        return False
    else:
        print(f"falltyp = {falltyp} bestimmt \n\n")
    
    # Button KG öffnen
    if not UNIVERSAL.find_and_click_button("button_kg_oeffnen.png", base_path=image_base_path, max_attempts=5, interval=0.05):
        print("Button KG öffnen wurde nicht gefunden")
    
    # Navigation zu Bereich Leistungen
    if not UNIVERSAL.navigiere_bereich_leistungen():
        print("Navigation zu Bereich Leistungen fehlgeschlagen")
        return False
    
    # Button Neu klicken
    if not UNIVERSAL.find_and_click_button("button_neu.png", base_path=image_base_path):
        print("Button Neu wurde nicht gefunden")
        return False
    
    
    # Workflow je nach Falltyp
    if falltyp == "ambulant":
        if not process_ambulant_workflow(icd_code):
            return False
    elif falltyp == "stationaer":
        if not process_stationaer_workflow(icd_code):
            return False
    
    # Alle KGs schließen
    if not UNIVERSAL.alle_kgs_schliessen():
        print("Fehler beim Schließen der KGs")
        return False
    
    return True


def process_ambulant_workflow(icd_code):
    """
    Verarbeitet den ambulanten Workflow.
    
    Args:
        icd_code (str): Der ICD-Code für den ICD-Check
    
    Returns:
        bool: True wenn erfolgreich, False bei Fehlern
    """
    # Button TM Ambulant
    if not UNIVERSAL.find_and_click_button("button_tm_ambulant.png", base_path=image_base_path):
        print("Button TM Ambulant wurde nicht gefunden")
        return False
    
    # Button leiste suchen
    if not UNIVERSAL.find_button("button_leiste.png", base_path=image_base_path):
        print("button_leiste wurde nicht gefunden")
        return False
    time.sleep(0.2)

    # Button Radioonkologie ATS
    if not UNIVERSAL.find_and_click_button("button_radioonkologie_ats.png", base_path=image_base_path):
        print("Button Radioonkologie ATS wurde nicht gefunden")
        return False
    
    # Button Leistungen in Abwesenheit
    if not UNIVERSAL.find_and_click_button("button_leistungen_in_abwesenheit.png", base_path=image_base_path):
        print("Button Leistungen in Abwesenheit wurde nicht gefunden")
        return False
    
    # Button Tumorboard
    if not UNIVERSAL.find_and_click_button("button_tumorboard.png", base_path=image_base_path):
        print("Button Tumorboard wurde nicht gefunden")
        return False
    
    # ICD-Check
    if not UNIVERSAL.icd_check(icd_code):
        print("ICD-Check fehlgeschlagen")
        return False
    
    # Button Speichern
    if not UNIVERSAL.find_and_click_button("button_speichern.png", base_path=image_base_path):
        print("Button Speichern wurde nicht gefunden")
        return False
    
    return True


def process_stationaer_workflow(icd_code):
    """
    Verarbeitet den stationären Workflow.
    
    Args:
        icd_code (str): Der ICD-Code für den ICD-Check
    
    Returns:
        bool: True wenn erfolgreich, False bei Fehlern
    """
    # Button TM Stationär
    if not UNIVERSAL.find_and_click_button("button_tm_stationaer.png", base_path=image_base_path):
        print("Button TM Stationär wurde nicht gefunden")
        return False
    
    # Button leiste suchen
    if not UNIVERSAL.find_button("button_leiste.png", base_path=image_base_path):
        print("button_leiste wurde nicht gefunden")
        return False
    time.sleep(0.2)
    
    # Button Radioonkologie ATS
    if not UNIVERSAL.find_and_click_button("button_radioonkologie_ats.png", base_path=image_base_path):
        print("Button Radioonkologie ATS wurde nicht gefunden")
        return False
    
    # Button Leistungen in Abwesenheit
    if not UNIVERSAL.find_and_click_button("button_leistungen_in_abwesenheit.png", base_path=image_base_path):
        print("Button Leistungen in Abwesenheit wurde nicht gefunden")
        return False
    
    # Button Tumorboard
    if not UNIVERSAL.find_and_click_button("button_tumorboard.png", base_path=image_base_path):
        print("Button Tumorboard wurde nicht gefunden")
        return False

    #Bei stationären Patienten braucht es hier keinen ICD check!!
    
    # Button Speichern
    if not UNIVERSAL.find_and_click_button("button_speichern.png", base_path=image_base_path):
        print("Button Speichern wurde nicht gefunden")
        return False
    
    return True


def main():
    """
    Hauptfunktion des Skripts.
    """
    print("Starte Tumorboard-Abrechnung...")

    UNIVERSAL.KISIM_im_vordergrund()
    UNIVERSAL.alle_kgs_schliessen()
    
    # Excel-Datei öffnen
    excel_path = r"K:\RAO_Projekte\App\tumorboards\HPB\17.07.2025\17.07.2025.xlsx"
    
    try:
        df = pd.read_excel(excel_path, header=0)
        print(f"Excel-Datei erfolgreich geöffnet: {excel_path}")
        print(f"DataFrame Shape: {df.shape}")
        print(f"DataFrame Columns: {df.columns.tolist()}")
        print(f"Erste 5 Zeilen:")
        print(df.head())
    except Exception as e:
        print(f"Fehler beim Öffnen der Excel-Datei: {e}")
        return
    
    # Liste für fehlgeschlagene Patienten
    abrechnung_unerfolgreich = []
    
    # Durch Patienten loopen (ab Zeile 2, Index 0 nach korrekter Header-Erkennung)
    for index, row in df.iterrows():
        print(f"Processing row {index}: {row.tolist()}")
        
        patientennummer = row['Patientennummer']  # Spalte nach Header-Name
        icd_code = row['ICD-10']  # Spalte nach Header-Name
        
        print(f"Row {index}: patientennummer='{patientennummer}' (type: {type(patientennummer)})")
        print(f"Row {index}: icd_code='{icd_code}' (type: {type(icd_code)})")
        
        # Prüfen ob Patientennummer leer ist
        if pd.isna(patientennummer) or str(patientennummer).strip() == "":
            print(f"Row {index}: Keine weitere Patientennummer gefunden. Beende Loop.")
            break
        
        # Prüfen ob ICD-Code leer ist
        if pd.isna(icd_code) or str(icd_code).strip() == "":
            print(f"Warnung: Kein ICD-Code für Patient {patientennummer} gefunden")
            icd_code = ""
        
        # Patient verarbeiten - Patientennummer als Integer konvertieren um .0 zu entfernen
        print(f"Converting patientennummer: '{patientennummer}' -> ", end="")
        clean_patientennummer = str(int(float(patientennummer)))
        print(f"'{clean_patientennummer}'")
        
        print(f"Processing patient: {clean_patientennummer} with ICD: {icd_code}")
        success = process_patient(clean_patientennummer, str(icd_code))
        
        if not success:
            abrechnung_unerfolgreich.append(clean_patientennummer)
            print(f"Patient {clean_patientennummer} konnte nicht erfolgreich verarbeitet werden")
    
    # Abschlussbericht
    if abrechnung_unerfolgreich:
        print(f"\n=== ABSCHLUSSBERICHT ===")
        print(f"Folgende Patienten konnten nicht abgerechnet werden: {abrechnung_unerfolgreich}")
        print(f"Anzahl fehlgeschlagener Patienten: {len(abrechnung_unerfolgreich)}")
    else:
        print("\n=== ABSCHLUSSBERICHT ===")
        print("Alle Patienten wurden erfolgreich abgerechnet!")
    
    print("Tumorboard-Abrechnung abgeschlossen.")


if __name__ == "__main__":
    main()



