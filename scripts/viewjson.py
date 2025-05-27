# -*- coding: utf-8 -*-
import json
import os
import sys
import traceback

# Importiere UNIVERSAL direkt
try:
    import UNIVERSAL
except ImportError as e:
    print(f"FEHLER: Konnte das Modul UNIVERSAL nicht importieren: {e}")
    print("Stellen Sie sicher, dass UNIVERSAL.py im selben Verzeichnis wie viewjson.py liegt oder im Python-Pfad.")
    sys.exit(1)

# NEU: Importiere spezifische Funktionen aus entities
try:
    import entities
    print("Funktionen aus entities.py erfolgreich importiert.")
except ImportError as e:
    print(f"FEHLER: Konnte entities.py nicht importieren: {e}")
    sys.exit("Abbruch: entities.py fehlt oder enthält Fehler.")


# --- Define Paths ---
script_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.dirname(script_dir)
screenshots_base_dir = os.path.join(script_dir, 'screenshots pyautogui')
user_home = os.path.expanduser("~")
patdata_dir = os.path.join(user_home, "patdata")

def main(patientennummer=None):
    if not patientennummer:
        UNIVERSAL.KISIM_im_vordergrund()

    if patientennummer:
        patient_id = patientennummer
    else:
        patient_id = input("Bitte geben Sie die Patientennummer ein, die dem Dateinamen entspricht: ").strip()
    if not patient_id.isdigit():
        print("Fehler: Patientennummer muss eine Zahl sein.")
        return

    directory = patdata_dir
    filename = f"{patient_id}.json"
    filepath = os.path.join(directory, filename)

    # Verbesserte Logik für nicht gefundene Datei
    while not os.path.exists(filepath):
        print(f"Die Datei '{filepath}' existiert nicht.")
        retry_id = input("Neue Patientennummer eingeben oder '-' zum Abbrechen: ").strip()
        if retry_id == '-':
            print("Abbruch durch Benutzer.")
            return
        elif retry_id.isdigit():
            patient_id = retry_id
            filename = f"{patient_id}.json"
            filepath = os.path.join(directory, filename)
        else:
            print("Ungültige Eingabe.")

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            print(f"\nDaten aus '{filepath}' geladen.")
    except json.JSONDecodeError as e: print(f"Fehler beim Lesen der JSON-Datei: {e}"); return
    except IOError as e: print(f"Fehler beim Öffnen der Datei: {e}"); return
    except Exception as e: print(f"Unerwarteter Fehler beim Laden: {e}\n{traceback.format_exc()}"); return

    try:
        valid_keys = [str(k) for k in data.keys()]
        max_key_len = max(len(k) for k in valid_keys) if valid_keys else 0
    except Exception: max_key_len = 25
    ref_width = max(max_key_len, 25) + 4
    keys = list(data.keys()) # Ursprüngliche Reihenfolge beibehalten

    while True:
        print("\nVerfügbare Keys und aktuelle Werte:")
        key_to_index_map = {}
        for i, key in enumerate(keys, start=1):
            key_str = str(key) # Sicherstellen, dass Key ein String ist für Operationen
            formatted_key = key_str.ljust(ref_width)
            value = data.get(key) # Verwende .get() für Sicherheit
            display_value = str(value) if value is not None else ""
            print(f"[{i:2}] {formatted_key} → {display_value}")
            key_to_index_map[key_str] = i # Index speichern

        try:
            selection = input("\nSoll eine Variable korrigiert werden? (Zahl eingeben; oder [-] zum Export): ").strip()
            if selection == "-": break

            chosen_key = None
            if selection.isdigit():
                index = int(selection) - 1
                if 0 <= index < len(keys): chosen_key = keys[index]
                else: print("Ungültige Auswahl (Zahl außerhalb)."); continue
            else:
                found = False
                for k in keys:
                    if str(k).lower() == selection.lower(): chosen_key = k; found = True; break
                if not found: print(f"Ungültige Auswahl. Key '{selection}' nicht gefunden."); continue

            # Ab hier ist chosen_key der Key aus dem data Dictionary
            chosen_key_str = str(chosen_key) # String-Version für Vergleiche
            current_value = data.get(chosen_key)
            current_value_str = str(current_value) if current_value is not None else ""
            print(f"\nÄndere Key: '{chosen_key_str}' (Aktuell: {current_value_str})")

            prompt_prefix = f"Neuer Wert für '{chosen_key_str}'"

            # --- Spezifische Logik für Entitäten ---
            if chosen_key_str == "entity":
                print("Starte manuelle Auswahl für primäre Entität...")
                selected_entity, auto_icd = entities.manuelle_entity_auswahl()
                if selected_entity is not None:
                    print(f"Entität gewählt: '{selected_entity}'. Automatischer ICD: '{auto_icd}'.")
                    icd_choice = UNIVERSAL.userinput_stat("Diesen ICD-Code übernehmen? ([j]=Ja / [n]=Manuell eingeben / [Enter]=Abbrechen):")
                    if icd_choice == 'j':
                        data[chosen_key] = selected_entity
                        data['icd_code'] = auto_icd
                        print(f"'{chosen_key_str}' und 'icd_code' aktualisiert.")
                    elif icd_choice == 'n':
                        manual_icd = UNIVERSAL.userinput_freitext("Bitte ICD-Code manuell eingeben (Enter lässt leer): ")
                        data[chosen_key] = selected_entity
                        data['icd_code'] = manual_icd if manual_icd else None
                        print(f"'{chosen_key_str}' und 'icd_code' (manuell) aktualisiert.")
                    else: print("Änderung der Entität abgebrochen.")
                else:
                    data[chosen_key] = None
                    data['icd_code'] = None
                    print(f"'{chosen_key_str}' und 'icd_code' auf 'Nicht gesetzt' zurückgesetzt.")
                continue # Zurück zur Key-Auswahl

            elif chosen_key_str == "secondary_entity":
                print("Starte manuelle Auswahl für sekundäre Entität (Bestrahlungsziel)...")
                selected_sec_entity, auto_sec_icd = entities.manuelle_sekundaer_auswahl()
                # --- NEUE LOGIK ---
                if selected_sec_entity is not None: # User hat eine sekundäre Entität ausgewählt
                    print(f"Sekundäre Entität gewählt: '{selected_sec_entity}'. Automatischer ICD: '{auto_sec_icd}'.")
                    icd_choice_sec = UNIVERSAL.userinput_stat("Diesen ICD-Code übernehmen? ([j]=Ja / [n]=Manuell eingeben / [Enter]=Abbrechen):")
                    if icd_choice_sec == 'j':
                        data[chosen_key] = selected_sec_entity
                        data['secondary_icd_code'] = auto_sec_icd # Automatischen ICD setzen
                        print(f"'{chosen_key_str}' und 'secondary_icd_code' aktualisiert.")
                    elif icd_choice_sec == 'n':
                        manual_sec_icd = UNIVERSAL.userinput_freitext("Bitte sekundären ICD-Code manuell eingeben (Enter lässt leer): ")
                        data[chosen_key] = selected_sec_entity # Ausgewählte Entität setzen
                        data['secondary_icd_code'] = manual_sec_icd if manual_sec_icd else None # Manuellen ICD setzen
                        print(f"'{chosen_key_str}' und 'secondary_icd_code' (manuell) aktualisiert.")
                    else: # User hat Enter gedrückt oder ungültig -> Keine Änderung
                         print("Änderung der sekundären Entität abgebrochen.")
                else: # User hat '-' bei der Auswahl gedrückt
                    data[chosen_key] = None
                    data['secondary_icd_code'] = None # Auch sekundären ICD zurücksetzen
                    print(f"'{chosen_key_str}' und 'secondary_icd_code' auf 'Nicht gesetzt' zurückgesetzt.")
                # --- ENDE NEUE LOGIK ---
                continue # Zurück zur Key-Auswahl

            elif chosen_key_str == "secondary_icd_code":
                 secondary_entity_index = key_to_index_map.get("secondary_entity", "?")
                 print(f"INFO: '{chosen_key_str}' kann nicht direkt geändert werden.")
                 print(f"Bitte korrigieren Sie stattdessen 'secondary_entity' (Nummer {secondary_entity_index}).")
                 print("Der ICD-Code wird dann automatisch abgefragt oder kann manuell gesetzt werden.")
                 continue # Zurück zur Key-Auswahl

            elif chosen_key_str == "icd_code": # Direkte Änderung des primären ICD erlaubt
                 new_value_specific = UNIVERSAL.userinput_freitext(f"{prompt_prefix} (Enter für keine Angabe): ")
                 if new_value_specific is None: print("INFO: Primärer ICD Code wird auf 'None' gesetzt.")
                 data[chosen_key] = new_value_specific # Update dictionary
                 print(f"Der Key '{chosen_key_str}' wurde auf '{data[chosen_key]}' aktualisiert.")
                 continue # Zurück zur Auswahl, da spezifisch behandelt

            # --- Standard Logik für andere Keys ---
            # (Dieser Block bleibt größtenteils unverändert, behandelt jetzt alle übrigen Keys)
            else:
                new_value_specific = None # Initialisieren für den else-Block
                # Verwende spezifische input Funktionen wo definiert
                if chosen_key_str == "therapieintention":
                    new_value_specific = UNIVERSAL.userinput_intention(f"{prompt_prefix} (k/p/l oder Enter für keine Angabe):")
                elif chosen_key_str in ["geburtsdatum", "eintrittsdatum", "datum_erste_rt", "datum_letzte_rt"]:
                    new_value_specific = UNIVERSAL.userinput_date_ddmmyyyy(f"{prompt_prefix} (dd.mm.yyyy oder Enter für keine Angabe):")
                elif chosen_key_str == "ecog":
                    new_value_specific = UNIVERSAL.userinput_ecog(f"{prompt_prefix} (0-4, x oder Enter für keine Angabe):")
                elif chosen_key_str == "simultane_chemotherapie":
                     stat_input = UNIVERSAL.userinput_stat(f"{prompt_prefix} (j/n oder Enter für keine Angabe):")
                     if stat_input == 'j': new_value_specific = "ja"
                     elif stat_input == 'n': new_value_specific = "nein"
                     else: new_value_specific = None
                else: # Fallback für alle anderen (Freitext)
                    new_value_specific = UNIVERSAL.userinput_freitext(f"{prompt_prefix} (Enter für keine Angabe):")
                    if new_value_specific is None: print(f"INFO: '{chosen_key_str}' wird auf 'None' gesetzt.")

                # Update data nur, wenn sich der Wert geändert hat oder explizit None gesetzt wurde
                if new_value_specific != current_value:
                     data[chosen_key] = new_value_specific # Update the dictionary
                     print(f"Der Key '{chosen_key_str}' wurde auf '{data[chosen_key]}' aktualisiert.")
                     # Zusätzliche Logik für Abhängigkeiten (Chemo)
                     if chosen_key_str == "simultane_chemotherapie":
                          if data[chosen_key] != "ja" and data.get("chemotherapeutikum"):
                               print("INFO: Da simultane Chemotherapie nicht 'ja' ist, wird Chemotherapeutikum gelöscht.")
                               data["chemotherapeutikum"] = None
                          elif data[chosen_key] == "ja" and not data.get("chemotherapeutikum"):
                               print("INFO: Simultane Chemotherapie ist 'ja'. Bitte Chemotherapeutikum prüfen/ergänzen.")
                else:
                     print("Wert bleibt unverändert.")


        except ValueError: print("Ungültige Eingabe (Zahl erwartet für Index).")
        except Exception as e: print(f"Ein Fehler ist aufgetreten: {e}\n{traceback.format_exc()}")

    # Speichern der aktualisierten JSON-Datei
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"\nDie Datei '{filepath}' wurde erfolgreich aktualisiert und gespeichert.")
    except IOError as e: print(f"Fehler beim Speichern der Datei: {e}")
    except Exception as e: print(f"Unerwarteter Fehler beim Speichern: {e}\n{traceback.format_exc()}")

########################################################
print("DEBUG: main() ist definiert, jetzt erfolgt der Aufruf mittels if __name__ == '__main__'")
if __name__ == "__main__":
    print("DEBUG: if __name__ == '__main__' ist wahr, daher wird main() aufgerufen")
    main()