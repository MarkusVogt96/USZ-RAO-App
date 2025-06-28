import csv

# --- Konfiguration ---
# HINWEIS: Aktualisiere diesen Pfad zu deiner entpackten CSV/TXT-Datei!
# Beispiel: 'C:/Users/DeinBenutzer/Downloads/ICD-10-GM-2025-Metadaten.txt'
CSV_FILE = r'C:\Users\votma\AppData\Roaming\USZ-RAO-App\scripts\icd10gm2025syst_kodes.txt' # Annahme, dass die Datei im gleichen Verzeichnis liegt

# Die gewünschten ICD-Hauptkategorien
TARGET_CATEGORIES = {'C', 'D', 'G', 'Q', 'R'}

# Spalten-Indizes (0-basiert) in der CSV/TXT-Datei
# Basierend auf dem bereitgestellten 'codes.txt' Beispiel
CODE_COLUMN_INDEX = 5       # 6. Spalte ist der ICD-Code (z.B. C00.0)
DESCRIPTION_COLUMN_INDEX = 8 # 9. Spalte ist die Beschreibung (z.B. Bösartige Neubildung: Äußere Oberlippe)

# Das Trennzeichen der CSV-Datei (Semikolon im Beispiel)
DELIMITER = ';'

# Encoding der Datei. 'utf-8' ist Standard, 'latin-1' oder 'cp1252' können bei deutschen Texten auch vorkommen.
# Wenn Umlaute falsch dargestellt werden, versuchen Sie 'latin-1'.
FILE_ENCODING = 'utf-8'
# --- Ende Konfiguration ---

ICD_DATABASE = {}

try:
    print(f"Lade Datei: '{CSV_FILE}'...")
    with open(CSV_FILE, mode='r', encoding=FILE_ENCODING) as file:
        # Verwende csv.reader, da es keine Kopfzeile gibt und wir per Index zugreifen
        reader = csv.reader(file, delimiter=DELIMITER)

        for row_index, row in enumerate(reader):
            # Stellen Sie sicher, dass die Zeile genügend Spalten hat
            if len(row) > max(CODE_COLUMN_INDEX, DESCRIPTION_COLUMN_INDEX):
                code = row[CODE_COLUMN_INDEX]
                description = row[DESCRIPTION_COLUMN_INDEX]

                if code and description:
                    code_str = str(code).strip()
                    description_str = str(description).strip()

                    # Überprüfe, ob der Code mit einer der Zielkategorien beginnt
                    # und dass es sich um einen "echten" ICD-Code handelt
                    # (Filtert möglicherweise übergeordnete Kapitel wie "C00.-" aus,
                    # wenn nur die spezifischen Codes gewünscht sind.)
                    if code_str and len(code_str) > 0 and code_str[0] in TARGET_CATEGORIES:
                        # Optionaler weiterer Filter, falls Sie nur die untersten Ebenen wollen
                        # if not code_str.endswith('.-'): # Um C00.-, D00.- etc. auszuschließen
                        ICD_DATABASE[code_str] = description_str
            else:
                print(f"Warnung: Zeile {row_index + 1} hat nicht genügend Spalten und wurde übersprungen: {row}")


    print(f"\nErfolgreich {len(ICD_DATABASE)} ICD-Codes für die Kategorien {', '.join(TARGET_CATEGORIES)} geladen.")

    # Ausgabe des Dictionaries in das gewünschte Format
    print("\nICD_DATABASE = {")
    # Nur die ersten 20 Einträge für die Konsole ausgeben, ansonsten wird es zu lang
    items_to_print = list(ICD_DATABASE.items())
    for i, (code, description) in enumerate(items_to_print):
        if i < 20: # Limit for console output
            # Ersetzen Sie Anführungszeichen in der Beschreibung, um Fehler zu vermeiden
            # oder maskieren Sie sie entsprechend
            clean_description = description.replace("'", "\\'")
            print(f"    '{code}': '{clean_description}',")
        elif i == 20:
            print("    # ... weitere Einträge ...")
            break # Stop after printing placeholder
    print("}")

    # Empfehlung für sehr große Dictionaries: In eine JSON-Datei speichern
    import json
    output_filename = 'icd_database_filtered.json'
    with open(output_filename, 'w', encoding='utf-8') as f:
        # ensure_ascii=False stellt sicher, dass Umlaute korrekt gespeichert werden
        json.dump(ICD_DATABASE, f, ensure_ascii=False, indent=4)
    print(f"\nDas vollständige Dictionary wurde in '{output_filename}' gespeichert.")

except FileNotFoundError:
    print(f"Fehler: Die Datei '{CSV_FILE}' wurde nicht gefunden.")
    print("Bitte stelle sicher, dass der Pfad korrekt ist und die Datei existiert.")
except Exception as e:
    print(f"Ein unerwarteter Fehler ist aufgetreten: {e}")