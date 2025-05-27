import fitz  # PyMuPDF
import re
import os

def clean_and_format_text_block(text_block):
    """
    Bereinigt den Textblock und passt Zeilenumbrüche für Markdown an.
    - Entfernt spezifische Checkbox-Textmuster.
    - Wandelt Zeilen, die nur aus zwei "seltsamen" Zeichen bestehen, 
      gefolgt von Text in der nächsten Zeile, in Markdown-Bullets um.
    - Ersetzt einzelne Newlines durch '  \n' für Markdown-Line-Breaks.
    - Behält echte Absatzumbrüche ('\n\n') bei.
    """
    # 1. Spezifische Checkbox-Textmuster entfernen (Muss zuerst passieren!)
    checkbox_patterns_to_remove = re.compile(
        r"(?:Gewichtsverlust:\s*Ja\s*Nein|"
        r"Primärfall:\s*Ja\s*Nein|"
        r"Rezidiv:\s*Ja\s*Nein)",
        re.IGNORECASE
    )
    cleaned_text = checkbox_patterns_to_remove.sub("", text_block)

    # 2. Handle Unrecognized Bullet Points (basierend auf neuer Definition)
    lines = cleaned_text.split('\n')
    processed_lines = []
    i = 0
    
    # Definiere "seltsames Zeichen": Nicht-Buchstabe (inkl. Umlaute), Nicht-Zahl, 
    # und nicht die erlaubten Satzzeichen (. - , _ !). Darf auch kein Leerzeichen sein.
    strange_char_pattern = r"[^a-zA-Z0-9\s\.,\-_!äöüÄÖÜß]"
    # Regex für eine Zeile, die optional mit Leerzeichen beginnt/endet und genau ZWEI "seltsame Zeichen" enthält.
    # Wichtig: Die seltsamen Zeichen selbst dürfen keine Leerzeichen sein.
    bullet_symbol_line_regex = re.compile(rf"^\s*({strange_char_pattern}){{2}}\s*$")

    while i < len(lines):
        current_line = lines[i]
        if bullet_symbol_line_regex.match(current_line):
            # Dies ist eine Zeile, die nur die zwei "seltsamen" Platzhalter-Bullet-Symbole enthält.
            # Der eigentliche Text des Stichpunkts sollte in der nächsten Zeile stehen.
            if i + 1 < len(lines):
                bullet_text_line = lines[i+1].strip()
                if bullet_text_line: # Nur wenn die nächste Zeile Text enthält
                    processed_lines.append(f"- {bullet_text_line}")
                # else: Leere Zeile nach Bullet-Symbolen, oder nur Whitespace. 
                #       In diesem Fall wird der Bullet-Symbol-Platzhalter effektiv gelöscht
                #       und kein neuer Stichpunkt erzeugt, was meistens gewünscht ist.
                i += 1 # Wichtig: Die nächste Zeile wurde verarbeitet (oder als leer befunden), also überspringen.
            # else: Bullet-Symbol-Zeile ist die letzte Zeile, kann ignoriert werden (wird nicht zu processed_lines hinzugefügt).
        else:
            # Keine Bullet-Symbol-Zeile, einfach die Zeile übernehmen.
            processed_lines.append(current_line)
        i += 1
    
    cleaned_text = "\n".join(processed_lines)
    # Nach der Zeilenverarbeitung und dem Join erneut strippen, falls leere Zeilen am Anfang/Ende entstanden sind.
    cleaned_text = cleaned_text.strip()

    # 3. Allgemeine Zeilenumbruch-Formatierung für Markdown
    #    Dies geschieht NACHDEM die Stichpunkte umformatiert wurden.
    # Ersetze alle Vorkommen von 2+ Newlines mit einem Platzhalter für echte Absätze
    processed_text_for_markdown_newlines = re.sub(r'\n{2,}', 'PARAGRAPH_BREAK_PLACEHOLDER', cleaned_text)
    
    # Jetzt ersetze alle verbleibenden einzelnen Newlines mit '  \n' für Markdown Line Breaks
    processed_text_for_markdown_newlines = processed_text_for_markdown_newlines.replace('\n', '  \n')
    
    # Ersetze den Platzhalter wieder mit echten doppelten Newlines
    final_text = processed_text_for_markdown_newlines.replace('PARAGRAPH_BREAK_PLACEHOLDER', '\n\n')

    return final_text.strip()


def format_patient_text_to_markdown(name_dob, full_id_str, text_content_after_header):
    """
    Formatiert den gegebenen Textblock in Markdown.
    - name_dob: String für die H1 Überschrift (Name und Geburtsdatum).
    - full_id_str: String der kompletten ID (XXXXX-YYYYY) für die fette Zeile.
    - text_content_after_header: Der Textblock, der NACH dem ursprünglichen Header beginnt.
    """
    markdown_lines = []
    markdown_lines.append(f"# {name_dob.strip()}")
    markdown_lines.append(f"**{full_id_str.strip()}**")
    markdown_lines.append("")  # 1 leere Zeile wie gewünscht

    # Vorab-Bereinigung und Markdown-konforme Zeilenumbrüche für den gesamten Textblock
    processed_main_content = clean_and_format_text_block(text_content_after_header)

    # Trennsequenz für die Abschnitte (case-insensitive Suche)
    sections = [
        {"keyword": "Diagnose", "keyword_display": "Diagnose"},
        {"keyword": "Fragestellung", "keyword_display": "Fragestellung"}
    ]

    last_processed_char_index = 0
    
    # Text bis zur ersten Sektion (oder alles, wenn keine Sektionen)
    first_section_keyword = sections[0]["keyword"] if sections else None
    
    if first_section_keyword:
        match_first_keyword = re.search(r"\b" + re.escape(first_section_keyword) + r"\b", processed_main_content, re.IGNORECASE)
        if match_first_keyword:
            text_before_first_keyword = processed_main_content[:match_first_keyword.start()].strip()
            if text_before_first_keyword:
                markdown_lines.append(text_before_first_keyword)
            last_processed_char_index = match_first_keyword.start()
        else: # Kein erstes Schlüsselwort gefunden
            if processed_main_content: # aber es gibt Text davor
                markdown_lines.append(processed_main_content)
            # Wichtig: Setze processed_main_content auf leer, um Doppelverarbeitung zu vermeiden
            # falls der gesamte Text vor der ersten Sektion lag und keine Sektionen gefunden werden.
            processed_main_content = "" 
            last_processed_char_index = len(processed_main_content) # Stellt sicher, dass der Index am Ende ist.
    else: # Keine Sektionen definiert, der ganze Text gehört hierhin
        if processed_main_content:
            markdown_lines.append(processed_main_content)
        processed_main_content = ""


    # Verarbeite die definierten Sektionen
    for i in range(len(sections)):
        current_keyword_info = sections[i]
        keyword_to_find = current_keyword_info["keyword"]
        
        # Suche das aktuelle Schlüsselwort im verbleibenden Teil von processed_main_content
        match_current = re.search(r"\b" + re.escape(keyword_to_find) + r"\b", processed_main_content[last_processed_char_index:], re.IGNORECASE)

        if match_current:
            # Indizes sind relativ zum gesamten processed_main_content
            absolute_start_index_keyword = last_processed_char_index + match_current.start() 
            absolute_end_index_keyword = last_processed_char_index + match_current.end()

            # Füge 3 leere Zeilen vor dem neuen Abschnitt (erzeugt 2 Leer-Absätze davor)
            markdown_lines.append("") 
            markdown_lines.append("") 
            markdown_lines.append("") 
            
            # Füge das Schlüsselwort selbst fett gedruckt hinzu
            markdown_lines.append(f"**{processed_main_content[absolute_start_index_keyword:absolute_end_index_keyword]}**") 
            
            # Eine weitere leere Zeile direkt nach dem fett gedruckten Schlüsselwort (erzeugt einen Absatz danach)
            markdown_lines.append("") 

            content_after_current_keyword = ""
            # Der Start für die Suche nach dem nächsten Keyword ist nach dem aktuellen Keyword
            search_start_for_next_keyword = absolute_end_index_keyword

            if i + 1 < len(sections): # Wenn es ein nächstes Schlüsselwort gibt
                next_keyword_to_find = sections[i+1]["keyword"]
                # Suche das nächste Keyword im Rest des Textes ab search_start_for_next_keyword
                match_next = re.search(r"\b" + re.escape(next_keyword_to_find) + r"\b", processed_main_content[search_start_for_next_keyword:], re.IGNORECASE)
                if match_next:
                    # Text zwischen Ende des aktuellen Keywords und Anfang des nächsten Keywords
                    content_after_current_keyword = processed_main_content[search_start_for_next_keyword : search_start_for_next_keyword + match_next.start()].strip()
                    last_processed_char_index = search_start_for_next_keyword + match_next.start() # Setze den Index für die nächste Iteration
                else: # Nächstes Keyword nicht gefunden, nimm den Rest des Textes
                    content_after_current_keyword = processed_main_content[search_start_for_next_keyword:].strip()
                    last_processed_char_index = len(processed_main_content) # Alles verarbeitet
            else: # Dies ist das letzte definierte Schlüsselwort, nimm den Rest des Textes
                content_after_current_keyword = processed_main_content[search_start_for_next_keyword:].strip()
                last_processed_char_index = len(processed_main_content) # Alles verarbeitet
            
            if content_after_current_keyword:
                markdown_lines.append(content_after_current_keyword)

            # Füge 3 leere Zeilen nach dem Inhalt des Abschnitts ein
            markdown_lines.append("") 
            markdown_lines.append("") 
            markdown_lines.append("") 
            
        # else: Wenn ein Schlüsselwort nicht gefunden wird, wird es übersprungen.

    output_string = "\n".join(line.rstrip() for line in markdown_lines) # rstrip() für jede Zeile vor dem Join
    
    return output_string.strip() # final strip für den gesamten Block


def create_markdown_files(pdf_path, output_dir_markdown):
    if not os.path.exists(output_dir_markdown):
        os.makedirs(output_dir_markdown)

    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        print(f"Fehler beim Öffnen der PDF-Datei '{pdf_path}': {e}")
        return

    num_pages = len(doc)
    if num_pages == 0:
        print("Die PDF-Datei ist leer.")
        return

    detailed_header_regex = re.compile(
        r"((?:.*?)\s+(?:\d{2}\.\d{2}\.\d{4}))\s+(((\d{5,9})-\d{5,9}))"
    )
    text_block_end_marker = "Beilagen"

    patient_markers = []
    for page_index in range(num_pages):
        page_text = doc[page_index].get_text("text")
        for match in detailed_header_regex.finditer(page_text):
            patient_markers.append({
                "page_index": page_index,
                "match_start_pos_on_page": match.start(),
                "full_header_text_matched": match.group(0).strip(),
                "name_and_dob": match.group(1).strip(),
                "full_id_with_hyphen": match.group(3).strip(),
                "id_for_filename": match.group(4).strip()
            })

    patient_markers.sort(key=lambda m: (m['page_index'], m['match_start_pos_on_page']))

    if not patient_markers:
        print("Keine Patienten-Header im Dokument gefunden.")
        doc.close()
        return

    for i in range(len(patient_markers)):
        current_marker = patient_markers[i]
        patient_sequence_num = i + 1
        
        start_page_patient = current_marker["page_index"]
        
        end_page_for_text_collection_exclusive = num_pages
        next_header_start_pos_if_same_page = -1 # Default: Kein nächster Header auf derselben Seite

        if i + 1 < len(patient_markers):
            next_marker = patient_markers[i+1]
            end_page_for_text_collection_exclusive = next_marker["page_index"] + 1 
            if next_marker["page_index"] == start_page_patient:
                next_header_start_pos_if_same_page = next_marker["match_start_pos_on_page"]

        raw_text_for_patient = ""
        for p_idx in range(start_page_patient, end_page_for_text_collection_exclusive):
            page_content = doc[p_idx].get_text("text")
            
            # Wenn der nächste Patient auf DIESER aktuellen Seite (p_idx) beginnt
            if i + 1 < len(patient_markers) and patient_markers[i+1]["page_index"] == p_idx and next_header_start_pos_if_same_page != -1:
                 raw_text_for_patient += page_content[:next_header_start_pos_if_same_page]
                 break # Text für diesen Patientenblock endet hier
            else:
                 raw_text_for_patient += page_content
        
        actual_content_start_index_in_raw = raw_text_for_patient.find(current_marker["full_header_text_matched"])
        
        if actual_content_start_index_in_raw == -1:
            print(f"Warnung: Konnte Header für Pat. {patient_sequence_num:02d} ({current_marker['id_for_filename']}) nicht im extrahierten Block finden. Überspringe.")
            continue
        
        text_from_header_onwards = raw_text_for_patient[actual_content_start_index_in_raw:]

        match_beilage = re.search(r"\b" + re.escape(text_block_end_marker) + r"\b", text_from_header_onwards, re.IGNORECASE)
        if match_beilage:
            relevant_text_block_with_header = text_from_header_onwards[:match_beilage.start()]
        else:
            relevant_text_block_with_header = text_from_header_onwards
        
        text_content_for_formatting = relevant_text_block_with_header[len(current_marker["full_header_text_matched"]):].strip()
        
        markdown_content = format_patient_text_to_markdown(
            current_marker["name_and_dob"],
            current_marker["full_id_with_hyphen"],
            text_content_for_formatting
        )

        if markdown_content:
            md_filename = os.path.join(output_dir_markdown, f"{patient_sequence_num:02d}_{current_marker['id_for_filename']}.md")
            try:
                with open(md_filename, "w", encoding="utf-8") as f_md:
                    f_md.write(markdown_content)
                print(f"MD gespeichert: {md_filename}")
            except Exception as e:
                print(f"Fehler beim Speichern von {md_filename}: {e}")
        else:
            print(f"Kein Markdown-Inhalt für Pat. {patient_sequence_num:02d} ({current_marker['id_for_filename']}) generiert.")

    doc.close()

# --- Anwendung ---
user_home = os.path.expanduser("~") 
tumorboards_dir = os.path.join(user_home, "tumorboards")
pdf_file_path = os.path.join(tumorboards_dir, "Thorax", "Tumorboard_Thorax.pdf")
base_output_path = os.path.dirname(pdf_file_path) 
output_directory_markdown = os.path.join(base_output_path, "entries_splitted_markdown")

if os.path.exists(pdf_file_path):
    create_markdown_files(pdf_file_path, output_directory_markdown)
else:
    print(f"Datei nicht gefunden: {pdf_file_path}")