import os
import pyautogui
import time
import clipboard
import sys
import datetime
import UNIVERSAL
import viewjson
import fliesstexte

# Get the absolute path of the directory containing the current script (patdata.py)
script_dir = os.path.dirname(os.path.abspath(__file__))
# Get the absolute path of the parent directory (the application root, e.g., "USZ RAO App")
app_dir = os.path.dirname(script_dir)
# Define the path to the main screenshots directory (located within the script directory)
screenshots_dir = os.path.join(script_dir, 'screenshots pyautogui')
local_screenshots_dir = os.path.join(screenshots_dir, "UNIVERSAL", "bereich_berichte")
# Define the absolute path to patdata in the user's home directory
user_home = os.path.expanduser("~")

# Heutiges Datum ermitteln
today_date = datetime.date.today()
heute = today_date.strftime("%d.%m.%Y")
weekday_today = today_date.weekday()
days_until_saturday = (5 - weekday_today + 7) % 7
samstag_date = today_date + datetime.timedelta(days=days_until_saturday)
sonntag_date = samstag_date + datetime.timedelta(days=1)
samstag = samstag_date.strftime("%d.%m.%Y")
sonntag = sonntag_date.strftime("%d.%m.%Y")

glossary = {}
rea, ips = None, None
nachname, vorname, geburtsdatum, alter, geschlecht, patientennummer, eintrittsdatum = None, None, None, None, None, None, None

def dictionary_ohne_None():
    # ... (Funktion bleibt gleich - wichtig für Variablenextraktion!) ...
    global patdata, nachname, vorname, geburtsdatum, alter, geschlecht, patientennummer, eintrittsdatum, spi, rea, ips, tumor, entity, icd_code, secondary_entity, secondary_icd_code, oberarzt, simultane_chemotherapie, chemotherapeutikum, therapieintention, fraktionen_woche, behandlungskonzept_serie1, behandlungskonzept_serie2, behandlungskonzept_serie3, behandlungskonzept_serie4, rt_konzept, datum_erste_rt, datum_letzte_rt, ecog, zimmer, aufnahmegrund
    if isinstance(patdata, dict):
        print("Lese Patientendaten aus Dictionary...")
        #Folgende Variablen werden erneut ausgelesen am Anfang und sind auskommentiert:

        nachname = patdata.get("nachname", "")
        vorname = patdata.get("vorname", "")
        #geburtsdatum = patdata.get("geburtsdatum", "")
        #alter = patdata.get("alter", "")
        #geschlecht = patdata.get("geschlecht", "")
        #patientennummer = patdata.get("patientennummer", "")
        #eintrittsdatum = patdata.get("eintrittsdatum", "")
        spi = patdata.get("spi", "")
        tumor = patdata.get("tumor", "")
        entity = patdata.get("entity", "")
        icd_code = patdata.get("icd_code", "")
        secondary_entity = patdata.get("secondary_entity", "")
        secondary_icd_code = patdata.get("secondary_icd_code", "")
        oberarzt = patdata.get("oberarzt", "")
        simultane_chemotherapie = patdata.get("simultane_chemotherapie", "")
        chemotherapeutikum = patdata.get("chemotherapeutikum", "")
        therapieintention = patdata.get("therapieintention", "")
        fraktionen_woche = patdata.get("fraktionen_woche", "")
        behandlungskonzept_serie1 = patdata.get("behandlungskonzept_serie1", "")
        behandlungskonzept_serie2 = patdata.get("behandlungskonzept_serie2", "")
        behandlungskonzept_serie3 = patdata.get("behandlungskonzept_serie3", "")
        behandlungskonzept_serie4 = patdata.get("behandlungskonzept_serie4", "")
        datum_erste_rt = patdata.get("datum_erste_rt", "")
        datum_letzte_rt = patdata.get("datum_letzte_rt", "")
        ecog = patdata.get("ecog", "")
        zimmer = patdata.get("zimmer", "")
        aufnahmegrund = patdata.get("aufnahmegrund", "")
        print(f"29 Variablen aus patdata aus JSON erfolgreich geladen\n")
    else: print("FEHLER: patdata ist kein Dictionary."); sys.exit()

def pruefe_wichtige_variablen():
    """
    Überprüft, ob die spezifizierten globalen Variablen gesetzt sind
    (nicht None und nicht leerer String).
    Beendet das Skript, wenn eine Variable fehlt.
    """
    print("Starte Überprüfung wichtiger Variablen...")
    variablen_zu_pruefen = [
        (alter, "Alter"),
        (tumor, "Tumor"),
        (therapieintention, "Therapieintention"),
        (ecog, "ECOG"),
        (aufnahmegrund, "Aufnahmegrund")
    ]

    fehlende_variablen = []

    for var_wert, var_name in variablen_zu_pruefen:
        # Prüft auf None ODER leeren String (nach Entfernung von Leerzeichen)
        if var_wert is None or (isinstance(var_wert, str) and not var_wert.strip()):
            fehlende_variablen.append(var_name)

    if fehlende_variablen:
        print("\nACHTUNG: Folgende Variablen, existieren nicht:")
        for var_name in fehlende_variablen:
            print(f"- {var_name}")
        print("\nviewjson.py wird jetzt geöffnet. Bitte Variablen ergänzen und Skript neu starten!")
        viewjson.main(patientennummer)
        sys.exit()
    else:
        print("Alle erforderlichen Variablen sind vorhanden und ausgefüllt.")
        print("-" * 30)

def oeffne_verlaufsbericht_radioonkologie():
    #Verlaufsbericht Radioonkologie öffnen
    UNIVERSAL.navigiere_bereich_berichte()
    if not UNIVERSAL.find_and_click_button("button_neu.png", base_path=local_screenshots_dir): print("FEHLER: Konnte 'Neu'-Button nicht klicken.")
    while True:
        if not UNIVERSAL.find_button("button_bericht_confirm.png", base_path=local_screenshots_dir, max_attempts=1): 
            print("Konnte button_bericht_confirm nicht finden. Versuche, button_bericht_unselected.png zu finden")
            try:
                UNIVERSAL.find_and_click_button("button_bericht_unselected.png", base_path=local_screenshots_dir, max_attempts=1)
            except:
                print("button_bericht_unselected.png nicht gefunden. Continue while Loop.")
                time.sleep(0.05)
        else:
            print("Konnte button_bericht_confirm gefunden, öffne Verlaufsbericht RAO.")
            break

    if  not UNIVERSAL.find_and_click_button("button_x_von_suchleiste.png", base_path=local_screenshots_dir): print("WARNUNG: 'X' in Suchleiste nicht gefunden oder geklickt.")
    verlaufsbericht = "Verlaufsbericht Radioonkologie"
    clipboard.copy(verlaufsbericht)
    pyautogui.hotkey('ctrl', 'v')
    if not UNIVERSAL.find_and_click_button("button_verlaufsbericht_radioonkologie.png", base_path=local_screenshots_dir): print("FEHLER: Konnte 'Verlaufsbericht Radioonkologie' nicht auswählen.")
    print("Warte auf Bericht..."); time.sleep(0.1)
    if not UNIVERSAL.prozent_zoom_100(): print("Fehler: UNIVERSAL.prozent_zoom_100() == False. Breche ab. Bitte bei Admin melden."); sys.exit()

    if UNIVERSAL.find_button("button_verlaufsbericht_radioonkologie_confirm.png", base_path=local_screenshots_dir): print("button_verlaufsbericht_radioonkologie_confirm.png gefunden, warte 0.3s un Klick")
    time.sleep(0.25)
    if not UNIVERSAL.find_and_click_button("button_verlaufsbericht_radioonkologie_confirm.png", base_path=local_screenshots_dir): print("button_verlaufsbericht_radioonkologie_confirm.png nicht gefunden. Breche Funktion ab.")
    
def check_for_next_KG():
    if not UNIVERSAL.find_button('button_keine_offenen_kgs.png', base_path=local_screenshots_dir, max_attempts=5): 
        print('button_keine_offenen_kgs.png nicht gefunden, es existieren weitere. Führe main erneut durch.')
        return False
    else:
        print('button_keine_offenen_kgs.png gefunden, alle KGs geschlossen.')
        return True

def main():
    

    UNIVERSAL.KISIM_im_vordergrund()
    global nachname, vorname, geburtsdatum, alter, geschlecht, patientennummer, eintrittsdatum, patdata
    placeholder1, placeholder2, geburtsdatum, alter, geschlecht, patientennummer, eintrittsdatum = UNIVERSAL.auslesen_patdata_KISIMzeile()
    patdata = UNIVERSAL.load_json(patientennummer)
    dictionary_ohne_None()
    pruefe_wichtige_variablen()
    global rea, ips
    rea, ips = UNIVERSAL.auslesen_reaips()

    oeffne_verlaufsbericht_radioonkologie()
    
    if not UNIVERSAL.find_and_click_button("button_neuer_abschnitt.png", base_path=local_screenshots_dir): print("button_neuer_abschnitt.png nicht gefunden.")
    
    #Navigiert in heading von neuem Abschnitt
    UNIVERSAL.ctrl_tabs(26)
    heading = f"Übergabe für das Wochenende vom {samstag} und {sonntag}"
    clipboard.copy(heading)
    pyautogui.hotkey('ctrl', 'v')

    #Navigiert in fliesstext
    UNIVERSAL.ctrl_tabs(1)
    eintrag = fliesstexte.define_wochenendeintrag(patdata, eintrittsdatum=eintrittsdatum)
    clipboard.copy(eintrag)
    pyautogui.hotkey('ctrl', 'v')
    pyautogui.press('enter')
    pyautogui.hotkey('ctrl', 'shift', '.')
    pyautogui.hotkey('ctrl', 'a')
    pyautogui.hotkey('ctrl', 'shift', 'j')
    






if __name__ == "__main__":
    main()
