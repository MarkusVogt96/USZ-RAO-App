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

script_dir = os.path.dirname(os.path.abspath(__file__))
screenshots_dir = os.path.join(script_dir, 'screenshots pyautogui')
image_base_path = os.path.join(screenshots_dir, "abrechnung_tumorboard")
user_home = os.path.expanduser("~") 

icd_code = --> Der entsprechende Wert aus der Spalte A
button_lupe
button_patnr

paste patientennummer aus Excel Spalte A2
pyautogui press enter
pyautogui press enter
time.sleep(0.1)
falls UNIVERSAL.find_and_click_button button_rao_ambulant (5 attempts, 0.1 interval): falltyp = "ambulant" definieren
Falls UNIVERSAL.find_and_click_button button_rao_stationaer (5 attempts, 0.1 interval): falltyp = "stationaer" definieren 
falls beide nicht gefunden:
    pyautogui.press('down') 3x
    Dann 10x loopen mit 1x Suche nach beiden buttons pro loop mittels find_button()
    falls find_button button_fall_ambulant erfolgreich:
        falltyp = "ambulant" definieren
        enter drücken
    falls find_button button_fall_stationaer erfolgreich:
        falltyp = "stationaer" definieren
        enter drücken
     button_kg_oeffnen mit attempts = 10, interval 0.05

UNIVERSAL.navigiere_bereich_leistungen()
button_neu

falls falltyp == "ambulant": 
    button_tm_ambulant
    button_radioonkologie_ats
    button_leistungen_in_abwesenheit
    button_tumorboard
    if not UNIVERSAL.icd_check(icd_code) --> vermerken und später für Endbericht speichern
    button_speichern

falls falltyp == "stationaer": 
    button_tm_stationaer
    button_radioonkologie_ats
    button_leistungen_in_abwesenheit
    button_tumorboard
    if not UNIVERSAL.icd_check(icd_code) --> vermerken und später für Endbericht speichern
    button_speichern

if not UNIVERSAL.alle_kgs_schliessen(): --> Fehlermeldung, dass es einen Fehler beim Schliessen der KGs gab, Skript wurde abgebrochen. sys.exit()



