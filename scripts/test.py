import json

# Definieren der Dateinamen
input_filename = r'C:\Users\votma\AppData\Roaming\USZ-RAO-App\scripts\icd_database.json'
output_filename = r'C:\Users\votma\AppData\Roaming\USZ-RAO-App\scripts\icd_database_filtered.json'

print(f"Lese ICD-Daten aus '{input_filename}'...")

try:
    # Die Datei mit der korrekten UTF-8-Kodierung öffnen,
    # da sie deutsche Umlaute enthält.
    with open(input_filename, 'r', encoding='utf-8') as f:
        icd_data = json.load(f)

    print(f"Erfolgreich geladen. Anzahl der Codes vor dem Filtern: {len(icd_data)}")

    # Filtern der Daten mit einer Dictionary Comprehension.
    # Es wird ein neues Dictionary erstellt, das nur die Schlüssel-Wert-Paare enthält,
    # bei denen der Schlüssel (der Code) NICHT die Zeichenfolge ".-" enthält.
    filtered_data = {
        code: description for code, description in icd_data.items() 
        if ".-" not in code
    }

    print(f"Filterung abgeschlossen. Anzahl der Codes nach dem Filtern: {len(filtered_data)}")

    # Speichern der gefilterten Daten in einer neuen JSON-Datei.
    # ensure_ascii=False sorgt dafür, dass Umlaute korrekt dargestellt werden.
    # indent=4 sorgt für eine lesbare Formatierung (Pretty-Printing).
    with open(output_filename, 'w', encoding='utf-8') as f:
        json.dump(filtered_data, f, ensure_ascii=False, indent=4)
    
    print(f"Gefilterte Daten wurden erfolgreich in '{output_filename}' gespeichert.")

except FileNotFoundError:
    print(f"Fehler: Die Datei '{input_filename}' wurde nicht gefunden. "
          "Stellen Sie sicher, dass die Datei im selben Verzeichnis wie das Skript liegt.")
except json.JSONDecodeError:
    print(f"Fehler: Die Datei '{input_filename}' scheint kein gültiges JSON-Format zu haben.")
except Exception as e:
    print(f"Ein unerwarteter Fehler ist aufgetreten: {e}")