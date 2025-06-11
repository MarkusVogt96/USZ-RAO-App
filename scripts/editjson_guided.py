# -*- coding: utf-8 -*-
import json
import os
import sys
import traceback

# Stellen Sie sicher, dass diese Skripte im selben Verzeichnis oder im Python-Pfad sind
try:
    import UNIVERSAL
    import entities
except ImportError as e:
    print(f"FEHLER: Konnte UNIVERSAL oder entities nicht importieren: {e}")
    sys.exit("Abbruch: Wichtige Module fehlen.")

# --- Define Paths ---
script_dir = os.path.dirname(os.path.abspath(__file__))
user_home = os.path.expanduser("~")
patdata_dir = os.path.join(user_home, "patdata")

def main(patientennummer, missing_keys):
    """
    Führt einen geführten Prozess zur Korrektur fehlender JSON-Daten durch
    und ermöglicht anschließend manuelle Änderungen.

    Args:
        patientennummer (str): Die ID des Patienten.
        missing_keys (list): Eine Liste von Keys, die fehlen und ausgefüllt werden müssen.
    """
    if not patientennummer or not patientennummer.isdigit():
        print("Fehler: Gültige Patientennummer erforderlich.")
        return

    filepath = os.path.join(patdata_dir, f"{patientennummer}.json")

    if not os.path.exists(filepath):
        print(f"Fehler: Die Datei '{filepath}' wurde nicht gefunden.")
        return

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            print(f"\nDaten für Patient {patientennummer} aus '{filepath}' geladen.")
    except Exception as e:
        print(f"Fehler beim Laden der JSON-Datei: {e}")
        traceback.print_exc()
        return

    # --- 1. GEFÜHRTE EINGABE ---
    # Zuerst die fehlenden Daten nacheinander abfragen
    print("\n--- GEFÜHRTE EINGABE FÜR FEHLENDE DATEN ---")
    print("Bitte tragen Sie die folgenden Werte nacheinander ein.")

    for key_to_fix in missing_keys:
        current_value = data.get(key_to_fix, "LEER")
        print(f"\n>>> Bearbeite fehlenden Wert für: '{key_to_fix}' (Aktuell: {current_value})")
        
        # Logik aus viewjson.py übernehmen, um den richtigen Input-Typ zu verwenden
        # Diese Logik wird nur für den aktuellen 'key_to_fix' ausgeführt
        new_value = None
        if key_to_fix == "therapieintention":
            new_value = UNIVERSAL.userinput_intention("Wert (k/p/l oder Enter):")
        elif key_to_fix in ["geburtsdatum", "eintrittsdatum", "datum_erste_rt", "datum_letzte_rt"]:
            new_value = UNIVERSAL.userinput_date_ddmmyyyy("Wert (dd.mm.yyyy oder Enter):")
        elif key_to_fix == "ecog":
            new_value = UNIVERSAL.userinput_ecog("Wert (0-4, x oder Enter):")
        elif key_to_fix == "simultane_chemotherapie":
             stat_input = UNIVERSAL.userinput_stat("Wert (j/n oder Enter):")
             if stat_input == 'j': new_value = "ja"
             elif stat_input == 'n': new_value = "nein"
             else: new_value = None
        elif key_to_fix == "entity":
            print("Starte manuelle Auswahl für primäre Entität...")
            selected_entity, auto_icd = entities.manuelle_entity_auswahl()
            if selected_entity:
                data['entity'] = selected_entity
                if UNIVERSAL.userinput_stat("Zugehörigen ICD-Code übernehmen? (j/n): ") == 'j':
                    data['icd_code'] = auto_icd
                else:
                    data['icd_code'] = UNIVERSAL.userinput_freitext("ICD manuell eingeben: ")
            continue # Springe zum nächsten fehlenden Key
        elif key_to_fix == "icd_code":
            # Wird typischerweise mit 'entity' gesetzt, aber auch direkter Edit erlaubt
            new_value = UNIVERSAL.userinput_freitext(f"Neuer Wert für '{key_to_fix}': ")
        else: # Fallback für alle anderen (Freitext)
            new_value = UNIVERSAL.userinput_freitext(f"Neuer Wert für '{key_to_fix}': ")

        data[key_to_fix] = new_value
        print(f"-> Wert für '{key_to_fix}' auf '{data[key_to_fix]}' gesetzt.")


    print("\n--- GEFÜHRTE EINGABE ABGESCHLOSSEN ---")

    # --- 2. OPTIONALE MANUELLE KORREKTUR ---
    # Nach der Pflichteingabe kann der User optional weitere Werte korrigieren.
    keys_ordered = list(data.keys())
    while True:
        print("\nAKTUELLE DATENÜBERSICHT:")
        max_key_len = max(len(k) for k in keys_ordered) if keys_ordered else 25
        for i, key in enumerate(keys_ordered, start=1):
            value = data.get(key, "")
            print(f"[{i:2}] {key.ljust(max_key_len + 2)} → {value}")

        selection = input("\nOptional: Weitere Variable ändern (Zahl eingeben) oder mit [-] speichern und exportieren: ").strip().lower()
        
        if selection == "-":
            break # Schleife beenden und speichern
        
        try:
            if selection.isdigit():
                index = int(selection) - 1
                if 0 <= index < len(keys_ordered):
                    chosen_key = keys_ordered[index]
                    current_value = data.get(chosen_key, "LEER")
                    print(f"\nÄndere Key: '{chosen_key}' (Aktuell: {current_value})")
                    # Hier könnte man die detaillierte Input-Logik erneut einfügen,
                    # der Einfachheit halber verwenden wir hier generischen Freitext-Input.
                    new_manual_value = UNIVERSAL.userinput_freitext("Neuer Wert eingeben: ")
                    data[chosen_key] = new_manual_value
                    print(f"-> Wert für '{chosen_key}' auf '{data[chosen_key]}' gesetzt.")
                else:
                    print("Ungültige Zahl.")
            else:
                print("Ungültige Eingabe. Bitte eine Zahl oder '-' eingeben.")
        except Exception as e:
            print(f"Ein Fehler ist aufgetreten: {e}")


    # --- 3. SPEICHERN UND BEENDEN ---
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"\nDie Datei '{filepath}' wurde erfolgreich aktualisiert und gespeichert.")
    except Exception as e:
        print(f"Fehler beim Speichern der Datei: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    print("Dieses Skript ist für den Import durch andere Skripte gedacht.")
    print("Zum Testen können Sie eine Patientennummer und fehlende Keys übergeben.")
    # Beispielhafter Testaufruf:
    # test_patient = "12345"
    # test_missing = ["datum_erste_rt", "tumor"]
    # main(test_patient, test_missing)