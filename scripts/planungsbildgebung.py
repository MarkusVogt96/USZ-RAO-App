import importlib
from UNIVERSAL import find_button, find_and_click_button, navigiere_bereich_berichte, navigiere_bereich_kurve, diagnose_uebernehmen, ctrl_tabs, KISIM_im_vordergrund
import pyautogui
import os
import sys
import time
import datetime
import clipboard
import ctypes

# --- Define Relative Paths ---
script_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.dirname(script_dir)
screenshots_dir = os.path.join(script_dir, 'screenshots pyautogui')
# Pfad für Bericht-Buttons (image_base_path wurde in deinem Code im main() verwendet)
image_base_path = os.path.join(screenshots_dir, "UNIVERSAL", "bereich_kurve")
# Define the absolute path to patdata in the user's home directory
user_home = os.path.expanduser("~")
patdata_dir = os.path.join(user_home, "patdata")

# --- Konfigurationen ---
schema_list = ['Kopf mit 3-Pkt-Maske', 'Gehirn SRT', 'Gehirn SRS']
schema = None

lokalisation_dir = {'Kopf mit 3-Pkt-Maske': 'Gehirn',
                    'Gehirn SRT': 'Gehirn',
                    'Gehirn SRS': 'Gehirn'}

# Anzahl der 'Down'-Tastenanschläge nach Auswahl der Lokalisation (basierend auf Originalcode-Struktur)
subauftrag_unter_gehirn_mapping = {'Kopf mit 3-Pkt-Maske': 'button_auswahl_kopf_mit_3_pkt_maske.png',
                    'Gehirn SRT': 'button_auswahl_gehirn_srt.png',
                    'Gehirn SRS': 'button_auswahl_gehirn_srs.png'}

kontrastmittel_ct_mapping = {'Kopf mit 3-Pkt-Maske': 'ja',
                    'Gehirn SRT': 'ja',
                    'Gehirn SRS': 'ja'}

kontrastmittel_mri_mapping = {'Kopf mit 3-Pkt-Maske': 'ja',
                    'Gehirn SRT': 'ja',
                    'Gehirn SRS': 'ja'}

rt_auftrag_ausfüllen_mri_mapping = {'Kopf mit 3-Pkt-Maske': 'nein',
                    'Gehirn SRT': 'nein',
                    'Gehirn SRS': 'nein'}
rt_auftrag_ausfüllen_ct_mapping = {'Kopf mit 3-Pkt-Maske': 'ja',
                    'Gehirn SRT': 'nein',
                    'Gehirn SRS': 'nein'}
rt_auftrag_mapping = {'Kopf mit 3-Pkt-Maske': 'button_auftrag_moduliert.png',
                    'Gehirn SRT': 'button_auftrag_srt.png',
                    'Gehirn SRS': 'button_auftrag_srs.png'}

maske_ausfüllen_mri_mapping = {'Kopf mit 3-Pkt-Maske': 'nein',
                    'Gehirn SRT': 'nein',
                    'Gehirn SRS': 'nein'}
maske_ausfüllen_ct_mapping = {'Kopf mit 3-Pkt-Maske': 'nein',
                    'Gehirn SRT': 'ja',
                    'Gehirn SRS': 'ja'}
maske_mapping = {'Kopf mit 3-Pkt-Maske': 'button_kopfmaske_3_pkt.png',
                    'Gehirn SRT': 'button_stereo_3_pkt.png',
                    'Gehirn SRS': 'button_stereo_3_pkt.png'}

feldbegrenzung_oben_mri_ausfüllen_mapping = {'Kopf mit 3-Pkt-Maske': 'ja',
                    'Gehirn SRT': 'ja',
                    'Gehirn SRS': 'ja'}
feldbegrenzung_oben_ct_ausfüllen_mapping = {'Kopf mit 3-Pkt-Maske': 'ja',
                    'Gehirn SRT': 'nein',
                    'Gehirn SRS': 'nein'}
feldbegrenzung_oben_mapping = {'Kopf mit 3-Pkt-Maske': '3cm über Kalotte',
                    'Gehirn SRT': '3cm über Kalotte',
                    'Gehirn SRS': '3cm über Kalotte'}

feldbegrenzung_unten_mri_ausfüllen_mapping = {'Kopf mit 3-Pkt-Maske': 'ja',
                    'Gehirn SRT': 'ja',
                    'Gehirn SRS': 'ja'}
feldbegrenzung_unten_ct_ausfüllen_mapping = {'Kopf mit 3-Pkt-Maske': 'ja',
                    'Gehirn SRT': 'ja',
                    'Gehirn SRS': 'ja'}
feldbegrenzung_unten_mapping = {'Kopf mit 3-Pkt-Maske': 'C2',
                    'Gehirn SRT': 'C2',
                    'Gehirn SRS': 'C2'}

def userinput_am_anfang():
    # --- Schema-Auswahl durch Benutzer ---
    global schema
    print("\n\nAktuell supportete Schemata:")
    for i, s in enumerate(schema_list):
        print(f"[{i + 1}] = {s}")

    selected_schema_index = -1 # Initialisierung mit einem ungültigen Index
    while True:
        user_input = input(f"Auswahl: ")
        try:
            input_number = int(user_input)
            if 1 <= input_number <= len(schema_list):
                selected_schema_index = input_number - 1
                schema = schema_list[selected_schema_index]
                print(f"\nSchema '{schema}' ausgewählt.")
                break # Schleife beenden, da Eingabe gültig ist
            else:
                print("Ungültige Eingabe. Bitte geben Sie eine Zahl ein, die in der Liste steht.")
        except ValueError:
            print("Ungültige Eingabe. Bitte geben Sie eine ganze Zahl ein.")

    # --- CT und/oder MRI Auswahl durch Benutzer ---
    print("\nWelche Bildgebung anlegen?")
    print("\n[c] = CT")
    print("[m] = MRI")
    print("[b] = beides")
    global ct, mri
    ct = None
    mri = None
    while True:
        user_input = input(f"Eingabe: ")
        if user_input in ['c', 'm', 'b']:
            if user_input == 'c':
                ct = True
                print("ct = True gesetzt")
            elif user_input == 'm':
                mri = True
                print("mri = True gesetzt")
            elif user_input == 'b':
                ct = True
                mri = True
                print("ct und mri = True gesetzt")
            break # Schleife beenden, da Eingabe gültig ist
        else:
            print("Ungültige Eingabe. Bitte geben Sie [c], [m] oder [b].")

def oeffnen_ct():
    print(">>> Suche und klicke 'button_neu.png'...")
    if not find_and_click_button('button_neu.png', base_path=image_base_path):
        print(">>> FEHLER: 'button_neu.png' nicht gefunden, bitte manuell anklicken."); success = False
    else:
        print(">>> 'button_neu.png' gefunden und geklickt.")

    print(">>> Suche und klicke 'button_suche_x.png' (Suche-Feld)...")
    if not find_and_click_button('button_suche_x.png', base_path=image_base_path):
        print(">>> FEHLER: 'button_suche_x.png' nicht gefunden, bitte manuell anklicken."); success = False
    else:
        print(">>> 'button_suche_x.png' gefunden und geklickt.")
        planung = 'planung'
        print(f">>> Tippe Suchbegriff '{planung}' ein.")
        clipboard.copy(planung)
        pyautogui.hotkey('ctrl', 'v')
        print(">>> Suchbegriff getippt.")

    print(">>> Suche und klicke 'button_planungsbildgebung.png' (erste Option)...")
    if not find_and_click_button('button_planungsbildgebung.png', base_path=image_base_path):
        print(">>> FEHLER: 'button_planungsbildgebung.png' nicht gefunden, bitte manuell anklicken."); success = False
    else:
        print(">>> 'button_planungsbildgebung.png' gefunden und geklickt.")

    print(">>> Suche und klicke 'button_planungsbildgebung_neu.png' (Neu-Button)...")
    if not find_and_click_button('button_planungsbildgebung_neu.png', base_path=image_base_path):
        print(">>> FEHLER: 'button_planungsbildgebung_neu.png' nicht gefunden, bitte manuell anklicken."); success = False
    else:
         print(">>> 'button_planungsbildgebung_neu.png' gefunden und geklickt.")

    print(">>> Suche und klicke 'button_bericht_planungsct.png'...")
    if not find_and_click_button('button_bericht_planungsct.png', base_path=image_base_path, confidence=0.95):
        print(">>> FEHLER: 'button_bericht_planungsct.png' nicht gefunden, bitte manuell anklicken."); success = False
    else:
        print(">>> 'button_bericht_planungsct.png' gefunden und geklickt. Bericht-Formular sollte sich öffnen.")

def oeffnen_mri():
    print(">>> Suche und klicke 'button_neu.png'...")
    if not find_and_click_button('button_neu.png', base_path=image_base_path):
        print(">>> FEHLER: 'button_neu.png' nicht gefunden, bitte manuell anklicken."); success = False
    else:
        print(">>> 'button_neu.png' gefunden und geklickt.")

    print(">>> Suche und klicke 'button_suche_x.png' (Suche-Feld)...")
    if not find_and_click_button('button_suche_x.png', base_path=image_base_path):
        print(">>> FEHLER: 'button_suche_x.png' nicht gefunden, bitte manuell anklicken."); success = False
    else:
        print(">>> 'button_suche_x.png' gefunden und geklickt.")
        planung = 'planung'
        print(f">>> Tippe Suchbegriff '{planung}' ein.")
        clipboard.copy(planung)
        pyautogui.hotkey('ctrl', 'v')
        print(">>> Suchbegriff getippt.")

    print(">>> Suche und klicke 'button_planungsbildgebung.png' (erste Option)...")
    if not find_and_click_button('button_planungsbildgebung.png', base_path=image_base_path):
        print(">>> FEHLER: 'button_planungsbildgebung.png' nicht gefunden, bitte manuell anklicken."); success = False
    else:
        print(">>> 'button_planungsbildgebung.png' gefunden und geklickt.")

    print(">>> Suche und klicke 'button_planungsbildgebung_neu.png' (Neu-Button)...")
    if not find_and_click_button('button_planungsbildgebung_neu.png', base_path=image_base_path):
        print(">>> FEHLER: 'button_planungsbildgebung_neu.png' nicht gefunden, bitte manuell anklicken."); success = False
    else:
         print(">>> 'button_planungsbildgebung_neu.png' gefunden und geklickt.")

    print(">>> Suche und klicke 'button_bericht_planungsmri.png'...")
    time.sleep(0.1)
    if not find_and_click_button('button_bericht_planungsmri.png', base_path=image_base_path, confidence=0.95):
        print(">>> FEHLER: 'button_bericht_planungsmri.png' nicht gefunden, bitte manuell anklicken."); success = False
    else:
        print(">>> 'button_bericht_planungsmri.png' gefunden und geklickt. Bericht-Formular sollte sich öffnen.")

def aerzte_eintragen():
    """Trägt die vordefinierten Ärzte in die entsprechenden Felder ein."""
    print(">>> Starte: Ärzte eintragen...")
    success = True

    # Ärzte oben eintragen
    print(">>> Suche und klicke 'button_anmeldender_arzt.png'...")
    if not find_and_click_button('button_anmeldender_arzt.png', base_path=image_base_path):
        print(">>> FEHLER: 'button_anmeldender_arzt.png' nicht gefunden, bitte manuell anklicken."); success = False
    else:
        print(">>> 'button_anmeldender_arzt.png' gefunden und geklickt.")
        vogt = 'vogt mark'
        print(f">>> Tippe Anmelder: '{vogt}' ein.")
        clipboard.copy(vogt)
        pyautogui.hotkey('ctrl', 'v')
        # Kleiner Workaround, falls Autovervollständigung stört
        pyautogui.press('space'); pyautogui.press('backspace')
        time.sleep(0.2) # Kurze Pause für Systemreaktion
        pyautogui.press('enter') # Auswahl bestätigen
        print(">>> Anmelder eingetragen.")

        print(">>> Navigiere zum OA Feld (Ctrl+Tab x2)...")
        pyautogui.hotkey('ctrl', 'tab'); pyautogui.hotkey('ctrl', 'tab') # ins OA Feld
        print(">>> OA Feld erreicht.")

        brown = 'brown'
        print(f">>> Tippe OA: '{brown}' ein.")
        clipboard.copy(brown)
        pyautogui.hotkey('ctrl', 'v')
        # Kleiner Workaround, falls Autovervollständigung stört
        pyautogui.press('space'); pyautogui.press('backspace')
        time.sleep(0.2) # Kurze Pause
        pyautogui.press('enter') # OA Brown auswählen
        print(">>> OA eingetragen.")

    print(">>> Ende: Ärzte eintragen.")
    return success # Gibt Erfolg zurück

def main():
    """Hauptfunktion zur Automatisierung der Berichtserstellung."""
    print("\n--- Skript zur Anlage eines Planungs-CT Berichts gestartet ---")
    print(f"Ausgewähltes Schema: {schema}")

    # Flag für den Gesamterfolg (wird im Originalcode nur für Prints verwendet)
    success = True

    userinput_am_anfang()

    #Starte Automatisierung
    KISIM_im_vordergrund()
    print(">>> Navigiere zum Bereich 'Kurve' in der Anwendung...")
    navigiere_bereich_kurve()
    print(">>> Bereich 'Kurve' erreicht.")

    if ct:
        oeffnen_ct()

        # --- CT ausfüllen ---
        print(">>> Starte: CT-Details ausfüllen...")

        print(">>> Suche und klicke 'button_lokalisation.png'...")
        if not find_and_click_button('button_lokalisation.png', base_path=image_base_path):
            print(">>> FEHLER: 'button_lokalisation.png' nicht gefunden, bitte manuell anklicken."); success = False
        else:
            print(">>> 'button_lokalisation.png' gefunden und geklickt.")
            lokalisation_val = lokalisation_dir.get(schema)
            print(f">>> Prüfe Lokalisation für Schema '{schema}': '{lokalisation_val}'.")
            # Originalcode-Logik für Lokalisation beibehalten
            if lokalisation_val == 'Gehirn':
                print(">>> Lokalisation ist 'Gehirn'. Drücke Enter zum Öffnen.")
                pyautogui.press('enter')
                time.sleep(0.1) # Kurze Pause

            button_auswahl = subauftrag_unter_gehirn_mapping.get(schema)
            if not find_and_click_button(image_name=button_auswahl, base_path=image_base_path, confidence=0.95): print(f"button {button_auswahl} nicht gefunden.")

        # Ärzte eintragen
        if not aerzte_eintragen():
            print(">>> FEHLER: Ärzte konnten nicht erfolgreich eingetragen werden.")
            success = False

        #KM anklicken
        km_entscheidung = kontrastmittel_ct_mapping.get(schema)
        print(f">>> KM Entscheidung für Schema '{schema}': '{km_entscheidung}'.")
        if km_entscheidung == 'ja':
            print(">>> KM ist 'ja'. Klick KM an.")
            print(">>> Suche und klicke 'button_bericht_planungsct.png'...")
            if not find_and_click_button('button_km.png', base_path=image_base_path):
                print(">>> FEHLER: 'button_km.png' nicht gefunden, bitte manuell anklicken."); success = False
            else:
                print(">>> 'button_km.png' gefunden und geklickt.")

        #RT-Auftrag anklicken
        if rt_auftrag_ausfüllen_ct_mapping.get(schema) == 'ja':
            if not find_and_click_button(image_name=rt_auftrag_mapping.get(schema), base_path=image_base_path): print (f'button {rt_auftrag_mapping.get(schema)} nicht gefunden, manuell hinzufügen')
            else: print (f'button {rt_auftrag_mapping.get(schema)} angeklickt')

        #Maske anklicken
        if maske_ausfüllen_ct_mapping.get(schema) == 'ja':
            if not find_and_click_button(image_name=maske_mapping.get(schema), base_path=image_base_path): print (f'button {maske_mapping.get(schema)} nicht gefunden, manuell hinzufügen')
            else: print (f'button {maske_mapping.get(schema)} angeklickt')

        pyautogui.press('pagedown'); pyautogui.press('pagedown'); pyautogui.press('pagedown')
      

        # Feldbegrenzungen eintragen
        if feldbegrenzung_oben_ct_ausfüllen_mapping.get(schema) == 'ja':
            print(">>> Suche und klicke 'button_feldbegrenzung_oben.png'...")
            if not find_and_click_button('button_feldbegrenzung_oben.png', base_path=image_base_path):
                print(">>> FEHLER: 'button_feldbegrenzung_oben.png' nicht gefunden, bitte manuell anklicken."); success = False
            else:
                print(">>> 'button_feldbegrenzung_oben.png' gefunden und geklickt.")
                feldbegrenzung_oben = feldbegrenzung_oben_mapping.get(schema)
                clipboard.copy(feldbegrenzung_oben)
                pyautogui.hotkey('ctrl', 'v')
                print("Feldbegrenzung oben eingetragen")

        if feldbegrenzung_unten_ct_ausfüllen_mapping.get(schema) == 'ja':
            print(">>> Suche und klicke 'button_feldbegrenzung_unten.png'...")
            if not find_and_click_button('button_feldbegrenzung_unten.png', base_path=image_base_path):
                print(">>> FEHLER: 'button_feldbegrenzung_unten.png' nicht gefunden, bitte manuell anklicken."); success = False
            else:
                print(">>> 'button_feldbegrenzung_unten.png' gefunden und geklickt.")
                feldbegrenzung_unten = feldbegrenzung_unten_mapping.get(schema)
                clipboard.copy(feldbegrenzung_unten)
                pyautogui.hotkey('ctrl', 'v')
                print("Feldbegrenzung unten eingetragen")

        pyautogui.press('pageup'); pyautogui.press('pageup')

        #Diagnosen eintragen
        print("Versuche, Diagnosen zu übernehmen")
        if not find_and_click_button('button_probleme_diagnosen.png', base_path=image_base_path): print (f'button_probleme_diagnosen.png nicht gefunden, manuell öffnen.')
        if not diagnose_uebernehmen(): print("Diagnosen übernehmen nicht erfolgreich, manuell nachtragen")

        print(">>> Suche und klicke 'button_speichern_und_schliessen.png'...")
        if not find_and_click_button('button_speichern_und_schliessen.png', base_path=image_base_path):
            print(">>> FEHLER: 'button_speichern_und_schliessen.png' nicht gefunden, bitte manuell anklicken."); success = False
        else:
            print(">>> 'Speichern und Schliessen' gefunden und geklickt.")
        
        if not find_button('button_abspeichern_confirm.png', base_path=image_base_path): print(">>> FEHLER: 'button_abspeichern_confirm.png' nicht gefunden, bitte manuell anklicken."); success = False
        time.sleep(0.2)

        print(">>> VERSUCHE zu klicken auf 'Senden'...")
        if not find_and_click_button('button_senden.png', base_path=image_base_path):
            print(">>> FEHLER: 'button_senden.png' nicht gefunden."); success = False
        else:
            print(">>> 'Senden' gefunden und geklickt.")
        
        time.sleep(0.2)

        



    print(f"mri Status = {mri}")
    if mri:
        oeffnen_mri()

        # --- MRI ausfüllen ---
        print(">>> Starte: MRI-Details ausfüllen...")

        print(">>> Suche und klicke 'button_lokalisation.png'...")
        if not find_and_click_button('button_lokalisation.png', base_path=image_base_path):
            print(">>> FEHLER: 'button_lokalisation.png' nicht gefunden, bitte manuell anklicken."); success = False
        else:
            print(">>> 'button_lokalisation.png' gefunden und geklickt.")
            lokalisation_val = lokalisation_dir.get(schema)
            print(f">>> Prüfe Lokalisation für Schema '{schema}': '{lokalisation_val}'.")
            # Originalcode-Logik für Lokalisation beibehalten
            if lokalisation_val == 'Gehirn':
                print(">>> Lokalisation ist 'Gehirn'. Drücke Enter (vermutlich zur Auswahl oder zum Öffnen).")
                pyautogui.press('enter')
                time.sleep(0.1) # Kurze Pause

            button_auswahl = subauftrag_unter_gehirn_mapping.get(schema)
            if not find_and_click_button(image_name=button_auswahl, base_path=image_base_path, confidence=0.95): print(f"button {button_auswahl} nicht gefunden.")

        # Ärzte eintragen
        if not aerzte_eintragen():
            print(">>> FEHLER: Ärzte konnten nicht erfolgreich eingetragen werden.")
            success = False

        #KM anklicken
        km_entscheidung = kontrastmittel_ct_mapping.get(schema)
        print(f">>> KM Entscheidung für Schema '{schema}': '{km_entscheidung}'.")
        if km_entscheidung == 'ja':
            print(">>> KM ist 'ja'. Klick KM an.")
            print(">>> Suche und klicke 'button_bericht_planungsct.png'...")
            if not find_and_click_button('button_km.png', base_path=image_base_path):
                print(">>> FEHLER: 'button_km.png' nicht gefunden, bitte manuell anklicken."); success = False
            else:
                print(">>> 'button_km.png' gefunden und geklickt.")

        #RT-Auftrag anklicken
        if rt_auftrag_ausfüllen_mri_mapping.get(schema) == 'ja':
            if not find_and_click_button(image_name=rt_auftrag_mapping.get(schema), base_path=image_base_path): print (f'button {rt_auftrag_mapping.get(schema)} nicht gefunden, manuell hinzufügen')
            else: print (f'button {rt_auftrag_mapping.get(schema)} angeklickt')

        #Maske anklicken
        if maske_ausfüllen_mri_mapping.get(schema) == 'ja':
            if not find_and_click_button(image_name=maske_mapping.get(schema), base_path=image_base_path): print (f'button {maske_mapping.get(schema)} nicht gefunden, manuell hinzufügen')
            else: print (f'button {maske_mapping.get(schema)} angeklickt')

        pyautogui.press('pagedown'); pyautogui.press('pagedown'); pyautogui.press('pagedown')
      

        # Feldbegrenzungen eintragen
        if feldbegrenzung_oben_mri_ausfüllen_mapping.get(schema) == 'ja':
            print(">>> Suche und klicke 'button_feldbegrenzung_oben.png'...")
            if not find_and_click_button('button_feldbegrenzung_oben.png', base_path=image_base_path):
                print(">>> FEHLER: 'button_feldbegrenzung_oben.png' nicht gefunden, bitte manuell anklicken."); success = False
            else:
                print(">>> 'button_feldbegrenzung_oben.png' gefunden und geklickt.")
                feldbegrenzung_oben = feldbegrenzung_oben_mapping.get(schema)
                clipboard.copy(feldbegrenzung_oben)
                pyautogui.hotkey('ctrl', 'v')
                print("Feldbegrenzung oben eingetragen")

        if feldbegrenzung_unten_mri_ausfüllen_mapping.get(schema) == 'ja':
            print(">>> Suche und klicke 'button_feldbegrenzung_unten.png'...")
            if not find_and_click_button('button_feldbegrenzung_unten.png', base_path=image_base_path):
                print(">>> FEHLER: 'button_feldbegrenzung_unten.png' nicht gefunden, bitte manuell anklicken."); success = False
            else:
                print(">>> 'button_feldbegrenzung_unten.png' gefunden und geklickt.")
                feldbegrenzung_unten = feldbegrenzung_unten_mapping.get(schema)
                clipboard.copy(feldbegrenzung_unten)
                pyautogui.hotkey('ctrl', 'v')
                print("Feldbegrenzung unten eingetragen")
        
        pyautogui.press('pageup'); pyautogui.press('pageup')

        #Diagnosen eintragen
        print("Versuche, Diagnosen zu übernehmen")
        if not find_and_click_button('button_probleme_diagnosen.png', base_path=image_base_path): print (f'button_probleme_diagnosen.png nicht gefunden, manuell öffnen.')
        if not diagnose_uebernehmen(): print("Diagnosen übernehmen nicht erfolgreich, manuell nachtragen")
        

        print(">>> Suche und klicke 'button_speichern_und_schliessen.png'...")
        if not find_and_click_button('button_speichern_und_schliessen.png', base_path=image_base_path):
            print(">>> FEHLER: 'button_speichern_und_schliessen.png' nicht gefunden, bitte manuell anklicken."); success = False
        else:
            print(">>> 'Speichern und Schliessen' gefunden und geklickt.")
        
        if not find_button('button_abspeichern_confirm.png', base_path=image_base_path): print(">>> FEHLER: 'button_abspeichern_confirm.png' nicht gefunden, bitte manuell anklicken."); success = False
        time.sleep(0.2)
        print(">>> VERSUCHE zu klicken auf 'Senden'...")
        if not find_and_click_button('button_senden.png', base_path=image_base_path):
            print(">>> FEHLER: 'button_senden.png' nicht gefunden."); success = False
        else:
            print(">>> 'Senden' gefunden und geklickt.")

    if success:
        print(f"Global success == {success}")

# Skript starten
if __name__ == '__main__':
    main()
