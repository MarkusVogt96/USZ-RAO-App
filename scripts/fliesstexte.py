# -*- coding: utf-8 -*-
print("Lade Modul fliesstexte.py...")
import UNIVERSAL
import datetime
import indikationen_mapping


print("Erstelle Indikationen-Mapping für Fließtexte...")
try:
    INDICATIONS_MAP = indikationen_mapping.create_indication_mapping()
    print("Indikationen-Mapping erfolgreich erstellt.")
except Exception as e:
    print(f"FEHLER beim Erstellen des Indikationen-Mappings: {e}")
    INDICATIONS_MAP = {} # Im Fehlerfall ein leeres Dict verwenden, um Abstürze zu vermeiden.



# --- Hilfsfunktion für Glossary-Zugriff (lokal in diesem Modul) ---
def _get_from_glossary(glossary, key, default=""):
    """Sicherer Zugriff auf das Glossary-Dictionary."""
    return glossary.get(key, default) if isinstance(glossary, dict) else default



# --- Funktion für Eintrittsberichte ---
def define_eintritt_texte(eintritt_typ, patdata, glossary):
    """
    Definiert die Texte für verschiedene Typen von Eintrittsberichten.

    Args:
        eintritt_typ (int): Typ des Berichts (1, 2 oder 3).
        patdata (dict): Das Dictionary mit den Patientendaten.
        glossary (dict): Das Dictionary mit geschlechtsspezifischen Begriffen.

    Returns:
        dict: Ein Dictionary mit allen benötigten Texten für den Bericht.
              Bei unbekanntem Typ: Gibt Dictionary mit 'FEHLER'-Werten zurück.
    """
    # Zugriff auf Glossary über Hilfsfunktion
    g = lambda key, default="": _get_from_glossary(glossary, key, default)

    # Extrahiere benötigte Variablen aus patdata (mit Defaults)
    if isinstance(patdata, dict):
        print("Lese Patientendaten aus Dictionary...")
        nachname = patdata.get("nachname", "")
        vorname = patdata.get("vorname", "")
        geburtsdatum = patdata.get("geburtsdatum", "")
        alter = patdata.get("alter", "")
        geschlecht = patdata.get("geschlecht", "")
        patientennummer = patdata.get("patientennummer", "")
        eintrittsdatum = patdata.get("eintrittsdatum", "")
        spi = patdata.get("spi", "")
        rea = patdata.get("rea", "")
        ips = patdata.get("ips", "")
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
        tumor = patdata.get("tumor", "")
        zimmer = patdata.get("zimmer", "")
        aufnahmegrund = patdata.get("aufnahmegrund", "")

    # Kombiniere RT-Konzept
    konzepte = [str(k) for k in [behandlungskonzept_serie1, behandlungskonzept_serie2, behandlungskonzept_serie3, behandlungskonzept_serie4] if k]
    konzept_alle_serien = "\n".join(konzepte) if konzepte else "Nicht erfasst"

    # Therapieintention mappen
    map_gross = {"kurativ": "Kurativ-intendierte", "palliativ": "Palliativ-intendierte", "lokalablativ": "Lokalablativ-intendierte"}
    map_klein = {"kurativ": "kurativ-intendierte", "palliativ": "palliativ-intendierte", "lokalablativ": "lokalablativ-intendierte"}
    therapieintention_gross = map_gross.get(therapieintention, "______-intendierte")
    therapieintention_klein = map_klein.get(therapieintention, "______-intendierte")

    #individuelle Fall-Variablen für Texte
    rct = 'Radiochemotherapie' if chemotherapeutikum not in [None, '', '-', 'none', 'nicht erfasst'] else 'Radiotherapie'
    chemo = f' mit {chemotherapeutikum}' if rct == 'Radiochemotherapie' else ''
    prof_dr = "Prof." if oberarzt.lower() in ["guckenberger", "andratschke", "balermpas"] else "Dr."
    if rct == 'Radiochemotherapie':
        chemo_in_text = f' mit begleitender Systemtherapie mittels {chemotherapeutikum}'
    else:
        chemo_in_text = ""
    beschreibung_ecog = {0: 'altersentsprechendem', 1: 'leicht reduziertem', 2: 'reduziertem', 3: 'deutlich reduziertem', 4: 'stark reduziertem'}



    # Start der Fliesstexte
    texte = {
        "leiden": "FEHLER: Typ nicht definiert\n\n ",
        "familienanamnese": "Nicht eruiert.\n\n ",
        "soziales": "Wohnt in / Eintritt aus …\n\n ",
        "noxen": "Tabakabusus: \nAlkohol: \nSonstige Drogen/Noxen: \n\n ",
        "ecog_beschreibung": f"ECOG {ecog or "____"}.\n\n ",
        "gastro": 'Regelmässiger Stuhlgang, kein Durchfall, keine Obstipation. Keine Übelkeit, kein Erbrechen, keine abdominalen Schmerzen. Kein Gewichtsverlust, kein Blut im Stuhl.\n\n ',
        "pulmo": 'Kein Husten oder Auswurf, keine Dyspnoe, kein Thoraxschmerz.\n\n ',
        "kardial": 'Keine Palpitationen. Keine Dyspnoe bei Belastung oder in Ruhe, keine AP-Beschwerden. Keine Unterschenkelödeme.\n\n ',
        "uro": 'Kein Dysurie. Keine Pollakis- oder Nykturie. Keine Urininkontinenz, keine DK-Einlage.\n\n ',
        "bewegung": 'Aktiv und passiv freie Beweglichkeit aller Extremitäten. Aktuell keine Gelenkschmerzen oder -schwellungen.\n\n ',
        "neuro": 'Kein Schwindel, keine Kopfschmerzen, keine fokalneurologischen Defizite. Keine Bewusstseinsstörungen.\n\n ',
        "schmerzen": 'Aktuell keine Schmerzen.\n\n ',
        "b_symp": f'Kein Nachtschweiss, kein Fieber > 38°C, keine ungewollte Gewichtsabnahme > 10% in 6 Monaten.\n\n ',
        "allergien": 'Keine Allergien bekannt.\n\n ',
        "az_ez": f"{g('patient_nominativ')} in {beschreibung_ecog.get(ecog, "____")} Allgemeinzustand (ECOG {ecog}).\nNormaler Ernährungszustand.  / Leicht adipöser Ernährungszustand. / Leicht reduzierter Ernährungszustand.\n\n ",
        "gewicht": f'Eigenanamnetisch aktuell ___ kg.\n\n ', 
        "status": "Herztöne rein und rhythmisch, keine Herzgeräusche, Halsvenen nicht gestaut. Auskultatorisch vesikuläres Atemgeräusch über allen Lungenfeldern. Weiche Bauchdecke, keine Druckdolenzien oder lokalisierte Resistenzen, kein Peritonismus, normale Darmgeräusche in allen Quadranten, digital-rektale Untersuchung nicht durchgeführt. Räumlich, zeitlich, situativ und zur Person orientiert, GCS 15. Extremitäten aktiv und passiv frei beweglich, keine fokalneurologischen Defizite, Sensibilität und Motorik erhalten.\n\n ",
        "bemerkung": "",
        "procedere_list": ["FEHLER: Typ nicht definiert"]
    }

    if eintritt_typ == 1: # Allgemein
        print("Definiere Texte für Eintritt RAO allgemein (Typ 1)...")
        
        texte["leiden"] = (
            f"Der Eintritt {g('artikel_genitiv_klein')} {alter}-{g('jährig_genitiv')} {g('patient_genitiv')} erfolgt am {eintrittsdatum} zur Durchführung der {therapieintention_klein} Radiotherapie bei {tumor};"
            f" die stationäre Aufnahme ist aufgrund einer {aufnahmegrund or '____'} indiziert.\n\n"
            f"{g('artikel_nominativ_gross')} {g('patient_nominativ')} präsentiert sich kardiopulmonal stabil sowie in {beschreibung_ecog.get(ecog, "____")} Allgemeinzustand (ECOG {ecog}). Im Rahmen der initial durchgeführten Laboranalyse sowie der körperlichen Eintrittsuntersuchung liessen sich keine interventionsbedürftigen Befunde eruieren.\n\n\n ")
        
        texte["procedere_list"] = [
            f"Die Radiotherapie ist gemäss RT-Konzept vom {datum_erste_rt} - {datum_letzte_rt} geplant. Die Fortführung der Bestrahlung erfolgt nun im stationären Setting.",
            f"Es erfolgte eine Anpassung der Medikation mittels ____. Die sonstige vorbestehende Medikation wird unverändert fortgeführt.",
            f"Zum aktuellen Zeitpunkt liegt eine adäquate Schmerzkompensation unter Einnahme von ___ vor; sollte es zu einer Aggravation der Schmerzen kommen, ist bis auf Weiteres der Ausbau der Analgesie nach WHO-Stufenschema anzustreben.",
            f"Nach Abschluss des stationären Aufenthalts ist die Rückkehr in die Häuslichkeit respektive in das Alters- und Pflegeheim vorgesehen. Sollte sich dies voraussichtlich nicht realisieren lassen, erfolgt die zeitnahe, vorausschauende Organisation einer adäquaten Anschlusslösung unter Zuzug unter hausinternen Sozialberatung."]
        
    elif eintritt_typ == 2: # Brachy Placeholder
        print("Definiere Placeholder-Texte für Eintritt Brachy (Typ 2)...")

        texte["leiden"] = (
            f"Der Eintritt {g('artikel_genitiv_klein')} {alter}-{g('jährig_genitiv')} {g('patient_genitiv')} erfolgt am {eintrittsdatum} zur Durchführung der geplanten Brachytherapie bei {tumor};"
            f" die stationäre Aufnahme ist aufgrund einer {aufnahmegrund or '____'} indiziert.\n\n"
            f"{g('artikel_nominativ_gross')} {g('patient_nominativ')} präsentiert sich kardiopulmonal stabil sowie in {beschreibung_ecog.get(ecog, "____")} Allgemeinzustand (ECOG {ecog}). Im Rahmen der initial durchgeführten Laboranalyse sowie der körperlichen Eintrittsuntersuchung liessen sich keine interventionsbedürftigen Befunde eruieren.\n\n\n ")
        
        texte["procedere_list"] = [
            f"Die Brachytherapie ist gemäss RT-Konzept vom {datum_erste_rt} - {datum_letzte_rt} geplant.",
            f"Eine Transfusion etwaiger Blutprodukte ist bei aktuell ausreichend gutem Blutbild zum aktuellen Zeitpunkt nicht von Nöten. Im Rahmen der therapeutischen Intervention werden weitere Verlaufskontrollen erfolgen.",
            f"Parallel zur durchgeführten Brachytherapie wird eine adäquate analgetische Medikation mittels Paracetamol und Metamizol i.v. erfolgen. Zum Zeitpunkt des Eintritts liegt eine adäquate Schmerzkompensation vor; sollte es zu einer Aggravation der Schmerzen kommen, ist bis auf Weiteres der Ausbau der Analgesie nach WHO-Stufenschema -ggf. unter additivem Zuzug von Opiatpräparaten- anzustreben.",
            f"Nach Abschluss des stationären Aufenthalts ist die Rückkehr in die Häuslichkeit respektive in das Alters- und Pflegeheim vorgesehen. Sollte sich dies voraussichtlich nicht realisieren lassen, erfolgt die Organisation einer adäquaten Anschlusslösung unter Zuzug unserer hausinternen Sozialberatung."]
        
    elif eintritt_typ == 3: # Chemo Placeholder
        print("Definiere Placeholder-Texte für Eintritt Chemo (Typ 3)...")

        texte["leiden"] = (
            f"Der Eintritt {g('artikel_genitiv_klein')} {alter}-{g('jährig_genitiv')} {g('patient_genitiv')} erfolgt am {eintrittsdatum} zur Durchführung der {therapieintention_klein} Radiochemotherapie bei {tumor};"
            f" die stationäre Aufnahme -voraussichtlich für 1 Nacht- erfolgt im Rahmen der Applikation der konkomitanten Systemtherapie.\n\n"
            f"{g('artikel_nominativ_gross')} {g('patient_nominativ')} präsentiert sich kardiopulmonal stabil sowie in {beschreibung_ecog.get(ecog, "____")} Allgemeinzustand (ECOG {ecog}). Im Rahmen der initial durchgeführten Laboranalyse sowie der körperlichen Eintrittsuntersuchung liessen sich keine interventionsbedürftigen Befunde eruieren.\n\n\n ")
        
        texte["procedere_list"] = [
            f"Die Radiotherapie ist gemäss RT-Konzept vom {datum_erste_rt} - {datum_letzte_rt} geplant. Nach Gabe der Systemtherapie wird diese im ambulanten Setting weiter erfolgen.",
            f"Die etwaig vorbestehende Medikation wird unverändert fortgeführt.",
            f"Zum aktuellen Zeitpunkt liegt eine adäquate Schmerzkompensation unter Einnahme von ___ vor; sollte es zu einer Aggravation der Schmerzen kommen, ist bis auf Weiteres der Ausbau der Analgesie nach WHO-Stufenschema anzustreben.",
            f"Nach stationärer Gabe der Systemtherapie ist die Rückkehr in die Häuslichkeit respektive in das Alters- und Pflegeheim vorgesehen."]
        
    elif eintritt_typ == 4: # Palliative Care
        print("Definiere Placeholder-Texte für Eintritt Palli (Typ 4)...")

        texte["leiden"] = (
            f"Der Eintritt {g('artikel_genitiv_klein')} {alter}-{g('jährig_genitiv')} {g('patient_genitiv')} erfolgt am {eintrittsdatum} auf unserer spezialisierte Palliativ-Care Station;"
            f" die stationäre Aufnahme ist aufgrund einer {aufnahmegrund or '____'} indiziert.\n\n"
            f"{g('artikel_nominativ_gross')} {g('patient_nominativ')} präsentiert sich kardiopulmonal stabil sowie in {beschreibung_ecog.get(ecog, "____")} Allgemeinzustand (ECOG {ecog}). Im Rahmen der initial durchgeführten Laboranalyse sowie der körperlichen Eintrittsuntersuchung liessen sich keine akut interventionsbedürftigen Befunde eruieren.\n\n\n ")
        
        if geschlecht == 'W':
            partner = "ihrem Mann/Partner, welcher sie"
        elif geschlecht == "M":
            partner = "seiner Frau/Partnerin, welche ihn"
        texte["bemerkung"] = (
            f"Symptomlast:\n\nZum Zeitpunkt des stationären Eintritts präsentiert sich {g('artikel_nominativ_klein')} {g('patient_nominativ')} mit vermehrtem Unterstützungsbedarf in den ADLs sowie ____. Die Orientierung zu ZOPS ist erhalten, GCS 15. Im Vordergrund steht aktuell eine nicht kontrollierte Schmerzsymptomatik / Dyspnoe / ___ ."
            f"\n\n\n\nEntscheidungsfindung:\n\nDer Entscheid zur stationären Aufnahme auf die spezialisierte Palliative Care-Station erfolgte nach zuletzt dynamischer Entwicklung des Zustand {g('artikel_genitiv_klein')} {g('patient_genitiv')}; hierbei zeigte sich ___ . Bezüglich des Therapieziels wurde zuletzt REA/IPS respektive ja/ja / nein/ja / nein/nein vom Patienten gewünscht. Für {g('herrfrau')} {nachname} bedeute Lebensqualität in der momentanen Lage insbesondere eine ___. Eine Patientenverfügung liegt nicht vor."
            f"\n\n\n\nNetzwerk:\n\n{g('herrfrau')} {nachname} lebt daheim zusammen mit {partner} bisher in der Bewältigung der ADLs die notwendige Unterstützung gab, zuletzt mit der Situation und dem steigenden Pflegeaufwand jedoch auch zunehmend an die eigenen Belastungsgrenzen gestossen sei. Zudem ___"
            f"\n\nODER (ggf löschen!)\n{g('herrfrau')} {nachname} lebt daheim allein und versorgte sich bisher weitestgehend eigenständig. {g('herrfrau')} {nachname}'s soziales Netzwerk bestehe primär aus Freunden/Bekannten, welche ihn zuweilen unterstützen. Zudem ___"
            f"\n\n\n\nSupport:\n\nBis anhin seien keine externen Dienste involviert gewesen, insbesondere wurde keine Unterstützung durch die Spitex wahrgenommen. Bezüglich hausinterner, supportiver Begleitmassnahmen im Sinne von Physiotherapie, Ergotherapie, Austrittsplanung durch den Sozialdienst, sowie Seelsorge und Psychoonkologie steht {g('artikel_nominativ_klein')} {g('patient_nominativ')} grundsätzlich offen gegenüber.")

        texte["procedere_list"] = [
            f"Im Verlauf, Etablierung einer symptomorientierten Fix- und Bedarfsmedikation zur bestmöglichen Linderung bestehender Beschwerden",
            f"Erstellung einer Patientenverfügung/ACP-Beratung, sofern dies seitens {g('artikel_genitiv_klein')} {g('patient_genitiv')} gewünscht ist",
            f"Durchführung einer komplexen Austrittsplanung und Organisation einer adäquaten Anschlusslösung unter Einbeziehen der hausinternen Sozialberatung",
            f"Anbieten von psychoonkologischer Betreuung",
            f"Allenfalls Anmeldung von supportiver Physio- und Ergotherapie",
            f"Evaluation von supportiver Spiritual Care"]
    else:
        print(f"FEHLER: Unbekannter Eintrittstyp '{eintritt_typ}' in fliesstexte.py.")
        # Fehlertexte bleiben bestehen

    return texte


# --- Funktion für Austrittsberichte ---
def define_austritt_texte(austritt_typ, patdata, glossary):
    """
    Definiert die Texte für verschiedene Typen von Austrittsberichten.

    Args:
        austritt_typ (int): Typ des Berichts (1, 2 oder 3).
        patdata (dict): Das Dictionary mit den Patientendaten.
        glossary (dict): Das Dictionary mit geschlechtsspezifischen Begriffen.

    Returns:
        tuple: (text_dt, text_epi, text_procedere)
               Bei unbekanntem Typ: ("FEHLER", "FEHLER", ["FEHLER"])
    """
    # Zugriff auf Glossary über Hilfsfunktion
    g = lambda key, default="": _get_from_glossary(glossary, key, default)

    # Extrahiere benötigte Variablen aus patdata (mit Defaults)
    if isinstance(patdata, dict):
        print("Lese Patientendaten aus Dictionary...")
        nachname = patdata.get("nachname", "")
        vorname = patdata.get("vorname", "")
        geburtsdatum = patdata.get("geburtsdatum", "")
        alter = patdata.get("alter", "")
        geschlecht = patdata.get("geschlecht", "")
        patientennummer = patdata.get("patientennummer", "")
        eintrittsdatum = patdata.get("eintrittsdatum", "")
        spi = patdata.get("spi", "")
        rea = patdata.get("rea", "")
        ips = patdata.get("ips", "")
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
        tumor = patdata.get("tumor", "")
        zimmer = patdata.get("zimmer", "")
        aufnahmegrund = patdata.get("aufnahmegrund", "")

    # Kombiniere RT-Konzept
    konzepte = [str(k) for k in [behandlungskonzept_serie1, behandlungskonzept_serie2, behandlungskonzept_serie3, behandlungskonzept_serie4] if k]
    konzept_alle_serien = "\n".join(konzepte) if konzepte else "Nicht erfasst"

    # Therapieintention mappen
    map_gross = {"kurativ": "Kurativ-intendierte", "palliativ": "Palliativ-intendierte", "lokalablativ": "Lokalablativ-intendierte"}
    map_klein = {"kurativ": "kurativ-intendierte", "palliativ": "palliativ-intendierte", "lokalablativ": "lokalablativ-intendierte"}
    therapieintention_gross = map_gross.get(therapieintention, "______-intendierte")
    therapieintention_klein = map_klein.get(therapieintention, "______-intendierte")

    text_dt, text_epi, text_procedere = "FEHLER", "FEHLER", ["FEHLER"] # Defaults

    #individuelle Fall-Variablen für Texte
    rct = 'Radiochemotherapie' if chemotherapeutikum not in [None, '', '-', 'none', 'nicht erfasst'] else 'Radiotherapie'
    chemo = f' mit {chemotherapeutikum}' if rct == 'Radiochemotherapie' else ''
    prof_dr = "Prof." if oberarzt.lower() in ["guckenberger", "andratschke", "balermpas"] else "Dr."

    if simultane_chemotherapie == 'ja':
        chemo_in_dt = f'\n\nChemotherapie im Rahmen der Hospitalisation: {chemotherapeutikum}, Zyklus ____ zuletzt am __.__.2025 verabreicht.'
    else:
        chemo_in_dt = ""
    beschreibung_ecog = {0: 'altersentsprechendem', 1: 'leicht reduziertem', 2: 'reduziertem', 3: 'deutlich reduziertem', 4: 'stark reduziertem'}



    #Beginn der Fliesstexte
    if austritt_typ == 1: # --- Allgemein (atrao.py Logik) ---
        print("Definiere Texte für Austrittsbericht RAO allgemein (Typ 1)...")
        
    
        #Text Durchgeführte Therapie
        text_dt = (
            f"Zeitraum: {datum_erste_rt} - {datum_letzte_rt}\n\n"
            f"Dosiskonzept: {therapieintention_gross} Radiotherapie bei {tumor}\n\n"
            f"{konzept_alle_serien}\n\n"
            f"Fraktionen pro Woche: {fraktionen_woche}\n\n"
            f"Technik: Nach CT / MR-gestützter Planung erfolgte die Radiotherapie im Bereich oben genannter Lokalisationen am Linearbeschleuniger mit 6MV Photonen in VMAT Technik.\n\n"
            f"Im Rahmen der Hospitalisation verabreichte Fraktionen: __/__\n\n"
            f"Die Radiotherapie wird somit bis voraussichtlich {datum_letzte_rt} fortgeführt.    ODER     Die Radiotherapie ist somit nach Applikation aller Fraktionen abgeschlossen."
            f"{chemo_in_dt}\n\n")
        
        #Text Epikrise
        text_epi = (
            f"Der Eintritt {g('artikel_genitiv_klein')} {alter}-{g('jährig_genitiv')} {g('patient_genitiv')} erfolgte am {eintrittsdatum} zur Durchführung der {therapieintention_klein}n {rct}{chemo} bei {tumor}; "
            f"die stationäre Hospitalisation war aufgrund {aufnahmegrund} indiziert.\n\n"
            f"{g('artikel_nominativ_gross')} {g('patient_nominativ')} präsentierte sich kardiopulmonal stabil sowie in {beschreibung_ecog.get(ecog, "____")} Allgemeinzustand (ECOG {ecog}). Im Rahmen der initial durchgeführten Laboranalyse sowie der körperlichen Eintrittsuntersuchung liessen sich keine interventionsbedürftigen Befunde eruieren.\n\n"
            f"...Epikrise diktiert...\n\n"
            f"Die {rct} konnte somit im Rahmen des stationären Aufenthalts planmässig und ohne Manifestation signifikanter Komplikationen appliziert werden.\n"
            f"Am __.__.2025 konnten wir {g('artikel_akkusativ_klein')} {g('patient_akkusativ')} in ordentlichem Allgemeinzustand zurück in die Häuslichkeit / in die Anschlussrehabilitation entlassen.")
        

        #Text Procedere: Einzelne Stichpunkte als Liste, um mit bullet points und einzelnem Einfügen arbeiten zu können.
        text_procedere = [
            f"Ambulante Fortführung der {rct} bis zum geplanten Abschluss am {datum_letzte_rt}.",
            f"FALLS ORL-Abschluss: Tumor- und therapiespezifische Nachsorge via interdisziplinärer HNO-Tumorsprechstunde in 6-8 Wochen nach Abschluss der Therapie. Wir bitten die betreuuenden Kollegen der ORL um ein entsprechendes Aufgebot. Die erste bildgebende Verlaufskontrolle ist 3 Monate nach Abschluss empfohlen. Die entsprechende Anmeldung, Aufgebot und Befundbesprechung erfolgt durch die hausinternen Kollegen der ORL (Otorhinolaryngologie).",
            f"Die nächste ambulante Verlaufskontrolle ist in ca 6-8 Wochen geplant; das direkte Aufgebot erfolgt zeitnah. Die weitere Betreuung {g('artikel_genitiv_klein')} {g('patient_genitiv')} erfolgt durch das entsprechende Behandlungsteam ({prof_dr} {oberarzt}).   [CAVE: wenn in 6-8 Wochen: Bei Abschicken des AT-Berichts noch Senden intern an Sekretariat zur Termin-Orga!]",
            f"Fortführung der systematischen lokalen Hautpflege mit Excipial zur Prophylaxe einer Radiodermatitis / bis zur Regredienz der aktuell mild ausgeprägten Radiodermatitis. Fortführung der enoralen Schleimhautpflege mit Bepanthen Mundspülung sowie analgetisch Lidoral vor den Mahlzeiten bis zur Regredienz der radiogenen Mucositis und damit assoziierten Schmerzen.",
            f"Reduktion der peroralen Analgesie mit Dafalgan / Minalgin nach Massgabe der Beschwerden im Verlauf.",
            f"{g('artikel_nominativ_gross')} {g('patient_nominativ')} ist über eine mögliche Aggravierung allfälliger Akuttoxizität in den ersten 2 Wochen nach Abschluss der Therapie informiert. Die selbstständige Wiedervorstellung in unserer Abteilung ist bei Aggravation etwaiger Akuttoxizitäten, Auftreten von Fieber oder sonstigen unerwarteten, therapieassoziierten Komplikationen bei Bedarf jederzeit möglich."
        ]

    elif austritt_typ == 2: # --- Brachy (atbrachy.py Logik) ---
        print("Definiere Texte für Austrittsbericht Brachy (Typ 2)...")

        #Text Durchgeführte Therapie
        text_dt = (
            f"STANDARD FÜR ZERVIX, ggf. tumorspezifisch anpassen:\n\nNach abgeschlossener EBRT erfolgte die Brachytherapie vom {datum_erste_rt} - {datum_letzte_rt}. Die Planung erfolgte CT-/MR-gestützt nach Einlage des Applikators.\n\n"
            f"Dosiskonzept: Brachytherapie mittels Ringstiftapplikator (und interstitiellen Nadeln?) in 4 x 7 Gy = 28 Gy.\n\n"
            f"Fraktionen pro Tag: 2x; Intervall zwischen den Fraktionen mindestens 6 Stunden.\n\n"
            f"Zum Zeitpunkt der Entlassung ist die geplante Brachytherapie somit vollständig abgeschlossen. / Zum Zeitpunkt der Entlassung ist die geplante Brachytherapie somit noch nicht vollständig abgeschlossen; 2 weitere Fraktionen werden am xx.xx.2025 - xx.xx.2025 erfolgen. \n\n"
            f"{chemo_in_dt}" )
        
        #Text Epikrise
        text_epi = (
            f"Der Eintritt {g('artikel_genitiv_klein')} {alter}-{g('jährig_genitiv')} {g('patient_genitiv')} erfolgte am {eintrittsdatum} zur Durchführung der {therapieintention_klein}n Brachytherapie bei {tumor}; "
            f"die stationäre Hospitalisation war aufgrund der invasiven und pflegeintensiven Brachytherapie indiziert.\n\n"
            f"{g('artikel_nominativ_gross')} {g('patient_nominativ')} präsentierte sich kardiopulmonal stabil sowie in {beschreibung_ecog.get(ecog, "____")}  Allgemeinzustand (ECOG {ecog}). Im Rahmen der initial durchgeführten Laboranalyse sowie der körperlichen Eintrittsuntersuchung liessen sich keine interventionsbedürftigen Befunde eruieren.\n\n"
            f"Nach initial erfolgter, enteraler Abführung und anschliessender Einlage des Applikators erfolgte die 1. und 2. Fraktion am __.__. respektive __.__.2025. "
            f"Nach applikatorfreiem Intervall konnten schliesslich auch die 3. und 4. Fraktion am __.__. respektive __.__.2025 ohne Auftreten signifikanter Blutungen oder sonstiger nennenswerter Komplikationen erfolgen.\n"
            f"\nEine dezente Nausea konnte durch eine bedarfsweise antiemetische Therapie mit Metoclopramid coupiert werden; "
            f"auch zeigten sich die Schmerzen unter der analgetischen Therapie mit Paracetamol i.v. und Novaminsulfon i.v. weitestgehend kompensiert, sodass diese zum Austrittstag auf entsprechende orale Präparate umgestellt werden konnten und im Verlauf nach Massgabe der Beschwerden auszuschleichen sind.\n\n"
            f"Zusammenfassend konnte die Brachytherapie somit im Rahmen des stationären Aufenthalts planmässig und komplikationslos appliziert werden.\n"
            f"\nAm __.__.2025 konnten wir {g('artikel_akkusativ_klein')} {g('patient_akkusativ')} in ordentlichem Allgemeinzustand zurück in die Häuslichkeit und die ambulante Weiterbetreuung entlassen.")
        
        #Text Procedere: Einzelne Stichpunkte als Liste, um mit bullet points und einzelnem Einfügen arbeiten zu können.
        text_procedere = [
            f"Elektive Vorstellung in der Sprechstunde von Dr. Motisi in ca. 6 Wochen nach Abschluss der Radiotherapie. Ein Aufgebot ergeht schriftlich.    [CAVE: ggf an Sekretariat KISIM Senden intern für Termin-Orga!]",
            f"Die weitere tumorspezifische Nachsorge erfolgt durch die zuständigen Kollegen der Gynäkologie. Wir bitten um ein entsprechendes Aufgebot und empfehlen freundlicherweise eine bildgebende Nachsorge mittels MRI oder PET-MRI nach 3 Monaten, 6 Monaten und danach mindestens jährlich oder basierend auf dem klinischen Bild.",
            f"Die Patientin sollte Schwimmen oder Baden für mindestens zwei Monate nach Abschluss der Brachytherapie vermeiden.",
            f"Das Heben schwerer Lasten sollte vermieden werden.",
            f"Wir erwarten keine wesentlichen akuten Nebenwirkungen nach der Brachytherapie. Im Fall einer leichten Dysurie, erhöhten Miktionsfrequenz, Hämaturie und/oder Durchfall sollte primär eine symptomorientierte Behandlung erfolgen. Bei schwerwiegenden Komplikationen können spezifische Untersuchungen und Therapien indiziert sein und die Patientin sollte ihren Hausarzt/in aufsuchen.",
            f"Bei Blutungen aus der Scheide, starken Becken- oder Bauchschmerzen, eitrigem Ausfluss aus der Scheide, Fieber oder anderen besorgniserregenden Symptomen sollte die Patientin zeitnahe Hilfe beim Hausarzt oder einer Notaufnahme suchen. Auch für Beratungsgespräche stehen wir Ihnen jederzeit zur Verfügung.",
            f"Reduktion der Analgesie mit Dafalgan und Minalgin p.o. nach Massgabe der Beschwerden im Verlauf."]

    elif austritt_typ == 3: # --- Chemo (atchemo.py Logik) ---
        print("Definiere Texte für Austrittsbericht Chemo (Typ 3)...")

        #Text Durchgeführte Therapie
        text_dt = (
            f"{g('artikel_nominativ_gross')} {g('patient_nominativ')} erhielt im Rahmen der stationären Therapie des {tumor} den __. Zyklus der begleitenden Chemotherapie mittels {chemotherapeutikum} sowie die ___. von insgesamt ____ Fraktionen Radiotherapie.")
        
        #Text Epikrise
        if geschlecht.lower() == "m":
            asymppat = "asymptomatischem Patienten"
            print("Geschlecht = m erkannt, definiere asymppat Variable.")
        elif geschlecht.lower() == "w":
            asymppat = "asymptomatischer Patientin"
            print("Geschlecht = w erkannt, definiere asymppat Variable.")
        else:
            print("geschlecht konnte weder als m noch w erkannt werden. Breche Programm ab. Bitte checke patdata-JSON.")

        text_epi = (
            f"Der elektive Eintritt {g('artikel_genitiv_klein')} {alter}-{g('jährig_genitiv')} {g('patient_genitiv')} erfolgte am {eintrittsdatum} anlässlich des ___. Zyklus der simultan zur Radiotherapie bei {tumor} durchgeführten Systemtherapie mittels {chemotherapeutikum}.\n\n"
            f"{g('artikel_nominativ_gross')} {g('patient_nominativ')} präsentierte sich kardiopulmonal stabil sowie in {beschreibung_ecog.get(ecog, "____")} Allgemeinzustand (ECOG {ecog}). Im Rahmen der initial durchgeführten Laboranalyse sowie der körperlichen Eintrittsuntersuchung liessen sich keine interventionsbedürftigen Befunde eruieren.\n\n"
            f"Nach Ausschluss klinischer sowie laboranalytischer Kontraindikationen konnte die Systemtherapie mit {chemotherapeutikum} wie geplant verabreicht werden. Eine medikamentös forcierte Steigerung der Diurese war bei {asymppat} und mangels bestehender Beinödeme oder sonstiger Zeichen der Hypervolämie trotz vor der Systemtherapie erfolgter Hydrierung nicht notwendig.\n"
            f"Es präsentierten sich die antizipierten, mild ausgeprägten Akuttoxizitäten der {rct} mit leichter Nausea, jedoch ohne Emesis.\n\n"
            f"Wir konnten {g('artikel_akkusativ_klein')} {g('patient_akkusativ')} somit am __.__.2025 in gutem Allgemeinzustand in die ambulante Weiterbehandlung entlassen.")
        
        #Text Procedere: Einzelne Stichpunkte als Liste, um mit bullet points und einzelnem Einfügen arbeiten zu können.
        text_procedere = [
            f"Ambulante Fortführung der {rct} bis zum geplanten Abschluss am {datum_letzte_rt}.",
            f"FALLS ORL-Abschluss: Tumor- und therapiespezifische Nachsorge via interdisziplinärer HNO-Tumorsprechstunde in 6-8 Wochen nach Abschluss der Therapie. Wir bitten die betreuuenden Kollegen der ORL um ein entsprechendes Aufgebot. Die erste bildgebende Verlaufskontrolle ist 3 Monate nach Abschluss empfohlen. Die entsprechende Anmeldung, Aufgebot und Befundbesprechung erfolgt durch die hausinternen Kollegen der ORL (Otorhinolaryngologie).",
            f"Die nächste ambulante Verlaufskontrolle ist in ca 6-8 Wochen geplant; das direkte Aufgebot erfolgt zeitnah. Die weitere Betreuung {g('artikel_genitiv_klein')} {g('patient_genitiv')} erfolgt durch das entsprechende Behandlungsteam ({prof_dr} {oberarzt}).   [CAVE: wenn in 6-8 Wochen: Bei Abschicken des AT-Berichts noch Senden intern an Sekretariat zur Termin-Orga!]",
            f"Fortführung der systematischen lokalen Hautpflege mit Excipial zur Prophylaxe einer Radiodermatitis / bis zur Regredienz der aktuell mild ausgeprägten Radiodermatitis. Fortführung der enoralen Schleimhautpflege mit Bepanthen Mundspülung sowie analgetisch Lidoral vor den Mahlzeiten bis zur Regredienz der radiogenen Mucositis und damit assoziierten Schmerzen.",
            f"Reduktion der peroralen Analgesie mit Dafalgan / Minalgin nach Massgabe der Beschwerden im Verlauf.",
            f"{g('artikel_nominativ_gross')} {g('patient_nominativ')} ist über eine mögliche Aggravierung allfälliger Akuttoxizität in den ersten 2 Wochen nach Abschluss der Therapie informiert. Die selbstständige Wiedervorstellung in unserer Abteilung ist bei Aggravation etwaiger Akuttoxizitäten, Auftreten von Fieber oder sonstigen unerwarteten, therapieassoziierten Komplikationen bei Bedarf jederzeit möglich.",
            f"Fortführung der antiemetischen Therapie mit Dexamethason bis inkl. __.__.2025, dann STOPP."]
    else:
        print(f"FEHLER: Unbekannter Austrittstyp '{austritt_typ}' in fliesstexte.py.")

    return text_dt, text_epi, text_procedere

# --- Funktion für Berrao/Woko Berichte ---
def define_berrao_texte(bericht_typ, entity, patdata, glossary):
    """
    Definiert die Fließtexte für Berrao-Berichte (inkl. Woko).

    Args:
        bericht_typ (str): Typ des Berichts ('e', 'a', 'k', 't', 'w').
        entity (str | None): Die erkannte Tumorentität oder None.
        patdata (dict): Das Dictionary mit den Patientendaten.
        glossary (dict): Das Dictionary mit geschlechtsspezifischen Begriffen.

    Returns:
        dict: Ein Dictionary mit den generierten Texten. Schlüssel entsprechen
              den ursprünglichen Variablennamen (z.B. 'fliesstext_wir_berichten').
              Gibt leere Strings für nicht zutreffende Texte zurück.
    """
    # Zugriff auf Glossary über Hilfsfunktion
    g = lambda key, default="": _get_from_glossary(glossary, key, default)

    # Extrahiere benötigte Variablen aus patdata (mit Defaults)
    if isinstance(patdata, dict):
        print("Lese Patientendaten aus Dictionary...")
        nachname = patdata.get("nachname", "")
        vorname = patdata.get("vorname", "")
        geburtsdatum = patdata.get("geburtsdatum", "")
        alter = patdata.get("alter", "")
        geschlecht = patdata.get("geschlecht", "")
        patientennummer = patdata.get("patientennummer", "")
        eintrittsdatum = patdata.get("eintrittsdatum", "")
        spi = patdata.get("spi", "")
        rea = patdata.get("rea", "")
        ips = patdata.get("ips", "")
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

    # Kombiniere RT-Konzept
    konzepte = [str(k) for k in [behandlungskonzept_serie1, behandlungskonzept_serie2, behandlungskonzept_serie3, behandlungskonzept_serie4] if k]
    konzept_alle_serien = "\n".join(konzepte) if konzepte else "Nicht erfasst"

    # Therapieintention mappen
    map_gross = {"kurativ": "Kurativ-intendierte", "palliativ": "Palliativ-intendierte", "lokalablativ": "Lokalablativ-intendierte"}
    map_klein = {"kurativ": "kurativ-intendierte", "palliativ": "palliativ-intendierte", "lokalablativ": "lokalablativ-intendierte"}
    therapieintention_gross = map_gross.get(therapieintention, "______-intendierte")
    therapieintention_klein = map_klein.get(therapieintention, "______-intendierte")

    #individuelle Fall-Variablen für Texte
    rct = 'Radiochemotherapie' if chemotherapeutikum not in [None, '', '-', 'none', 'nicht erfasst'] else 'Radiotherapie'
    chemo = f' mit {chemotherapeutikum}' if rct == 'Radiochemotherapie' else ''
    prof_dr = "Prof." if oberarzt.lower() in ["guckenberger", "andratschke", "balermpas"] else "Dr."
    if rct == 'Radiochemotherapie':
        chemo_in_dt = f'Systemtherapie im Rahmen der Hospitalisation: {chemotherapeutikum}, Zyklus ____ zuletzt am _____ verabreicht.'
    else:
        chemo_in_dt = ""
    beschreibung_ecog = {0: 'altersentsprechendem', 1: 'leicht reduziertem', 2: 'reduziertem', 3: 'deutlich reduziertem', 4: 'stark reduziertem'}

    #heute definieren
    import datetime
    today_date = datetime.date.today()
    heute = today_date.strftime("%d.%m.%Y")
    print(f"Heutiges Datum gesetzt: {heute}")

    #Kontrolle Mapping
    kontrolle_map = {"e": "Erstkonsultation", "a": "Abschlusskontrolle", "k": "klinischen Verlaufskontrolle", "t": "telefonischen Verlaufskontrolle", "w": "Wochenkontrolle"}
    kontrolle = kontrolle_map.get(bericht_typ, "Unbekannte Kontrolle")

    # UAW Mapping
    import entities
    print(f"getting uaw-dictionary from entities.py")
    uaw_mapping = entities.get_uaw()
    if secondary_entity:
        print(f"Getting uaw for {secondary_entity} from dictionary in entities.py")
        uaw = uaw_mapping.get(secondary_entity, "______")
    elif entity:
        uaw = uaw_mapping.get(entity, "______")
        print(f"Getting uaw for {entity} from dictionary in entities.py")
    else:
        print("Weder entity noch secondary_entity festgelegt, tumorspezifische uaw konnte nicht geladen werden.")
        uaw = ''

    # status_tumorspezifisch Mapping 
    print(f"getting status_tumorspezifisch_mapping from entities.py")
    status_tumorspezifisch_mapping = entities.get_status_tumorspezifisch()
    if secondary_entity:
        print(f"Getting status_tumorspezifisch for {secondary_entity} from dictionary in entities.py")
        status_tumorspezifisch = status_tumorspezifisch_mapping.get(secondary_entity, "______")
    elif entity:
        status_tumorspezifisch = status_tumorspezifisch_mapping.get(entity, "______")
        print(f"Getting status_tumorspezifisch for {entity} from dictionary in entities.py")
    else:
        print("Weder entity noch secondary_entity festgelegt, tumorspezifischer status konnte nicht geladen werden.")
        status_tumorspezifisch = ''

    # Initialisiere Dictionary für Rückgabe
    texte = {}

    # Generiere Texte basierend auf bericht_typ
    if bericht_typ == "e":
        print("Definiere Texte für Berrao Erstkonsultation (Typ e)...")

        # --- BEGINN NEUE LOGIK FÜR INDIKATIONSTEXT ---
        
        # 1. Bestimme den zu verwendenden ICD-Code gemäß der festgelegten Priorität.
        icd_code_to_use = None
        if secondary_icd_code and secondary_icd_code.strip():
            icd_code_to_use = secondary_icd_code
            print(f"INFO: Verwende 'secondary_icd_code' für Indikationssuche: {icd_code_to_use}")
        elif icd_code and icd_code.strip():
            icd_code_to_use = icd_code
            print(f"INFO: Verwende primären 'icd_code' für Indikationssuche: {icd_code_to_use}")
        else:
            print("WARNUNG: Kein ICD-Code in patdata für die Indikationssuche gefunden.")

        # 2. Rufe den Indikationstext aus dem Mapping ab.
        fliesstext_indikation = ""  # Standardwert ist ein leerer String.
        if icd_code_to_use:
            # Ruft die Funktion aus dem importierten Modul auf
            retrieved_text = indikationen_mapping.get_indication_text(icd_code_to_use, INDICATIONS_MAP)
            
            # Wandelt das Ergebnis 'None' in einen leeren String um, falls nichts gefunden wird.
            fliesstext_indikation = retrieved_text or ""
            if fliesstext_indikation:
                 print(f"INFO: Indikationstext für {icd_code_to_use} erfolgreich gefunden. \n\n\nGefundener Text:\n{fliesstext_indikation}")
            else:
                 print(f"\n\n\nINFO: Kein spezifischer Indikationstext für {icd_code_to_use} gefunden. Feld bleibt leer.")
        # --- ENDE LOGIK FÜR INDIKATIONSTEXT ---

        texte["fliesstext_wir_berichten"] = f"Wir berichten Ihnen über oben {g('genannte_akkusativ', 'genannten/genannte')} {g('patient_akkusativ','Patienten/in')}, {g('artikel_akkusativ_klein','den/die')} wir am {heute} zur Erstkonsultation gesehen haben."
        texte["fliesstext_onkologischer_krankheitsverlauf"] = (f"{g('herrfrau','Herr/Frau')} {nachname} ist {g('ein_nominativ','ein/eine')} {alter}-{g('jährig_nominativ','jährige/r')} {g('patient_nominativ','Patient/in')} mit {tumor} (Erstdiagnose _____ )."
                                                      f"\n\n[BISHERIGER VERLAUF]"
                                                      f"\n\n{g('artikel_nominativ_gross','Der/Die')} {alter}-jährige {g('patient_nominativ','Patient/in')} wird uns nun zur Evaluation einer potenziellen Radiotherapie in unsere ambulante Sprechstunde zugewiesen.")
        texte["fliesstext_aktueller_onkologischer_status"] = (f" ")
        texte["fliesstext_indikation"] = fliesstext_indikation
        texte["fliesstext_anamnese"] = (f"{g('herrfrau','Herr/Frau')} {nachname} stellte sich planmässig zur heutigen Erstkonsultation vor, um mit uns im Sinne eines shared decision-making "
                               f"etwaig indizierte radioonkologische Therapieoptionen im Rahmen der onkologischen Grunderkrankung bei {tumor} zu evaluieren.\n\n- ")
        texte["fliesstext_allgemeinstatus"] = (f"{alter}-{g('jährig_nominativ','jährige/r')} {g('patient_nominativ','Patient/in')} in {beschreibung_ecog.get(ecog, "____")} Allgemeinzustand (ECOG {ecog}) und normalem Ernährungszustand. "
                                      f"{g('artikel_nominativ_gross','Der/Die')} {g('patient_nominativ','Patient/in')} zeigt sich wach und kooperativ, sowie zu allen Qualitäten orientiert. "
                                      f"Klinisch präsentiert sich {g('artikel_nominativ_klein','der/die')} {g('patient_nominativ','Patient/in')} normokard und eupnoeisch, sowie in Ruhe kardiopulmonal kompensiert."
                                      f"\n{status_tumorspezifisch}")
        texte["fliesstext_durchgef_therapie"] = (f" ")
        texte["fliesstext_verlauf_unter_therapie"] = (f" ")
        texte["fliesstext_beurteilung"] = (f"Im Rahmen der heutigen Erstkonsultation haben wir mit {g('artikel_dativ_klein','dem/der')} {g('patient_dativ','Patienten/in')} ausführlich über mögliche radioonkologische Therapieoptionen"
                                  f" sowie deren Zielsetzung, Technik, als auch alternativen Therapiemöglichkeiten gesprochen."
                                  f"\n\nInsbesondere erläuterten wir {g('artikel_dativ_klein','dem/der')} {g('patient_dativ','Patienten/in')} die Möglichkeit der {therapieintention_klein}n Bestrahlung des {konzept_alle_serien} mit dem Ziel einer verbesserten lokalen Tumorkontrolle und Vermeiden von Symptomexazerbation bei weiterem Tumorwachstum. Die radioonkologische Therapie würde sich entsprechend über einen Zeitraum von ca. _____ Wochen erstrecken."
                                  f"\n\nDarüber hinaus erfolgte die ausführliche Aufklärung über mögliche akute und späte bzw. chronische Toxizitäten und Nebenwirkungen. Hierbei wurden u.a. {uaw or '______'} konkret thematisiert sowie entsprechend gegenüberstehenden Behandlungsmöglichkeiten erläutert."
                                  f"\n\n{g('artikel_nominativ_gross','Der/Die')} {g('patient_nominativ','Patient/in')} zeigte Verständnis gegenüber der {g('pronomen_dativ','ihm/ihr')} vorgebrachten Erläuterungen; allfällige Fragen wurden unsererseits beantwortet."
                                  f"\n\nEin individualisierter, therapiespezifischer Aufklärungsbogen wurde seitens {g('artikel_genitiv_klein','des/der')} {g('patient_genitiv','Patienten/in')} abschliessend unterzeichnet.")
        texte["fliesstext_procedere"] = [f"Zeitnahe Durchführung des Planungs-CT sowie Planungs-MR; {g('artikel_dativ_klein','dem/der')} {g('patient_dativ','Patienten/in')} wurden die entsprechenden Termine im Rahmen der heutigen Sprechstunde mitgeteilt ( __.__.2025).",
                                f"Der anschliessende Beginn der Radiotherapie steht aktuell noch nicht fest; {g('artikel_nominativ_klein','der/die')} {g('patient_nominativ','Patient/in')} erhält in Bälde ein direktes Aufgebot.",
                                f"Komplettierung der prätherapeutischen Diagnostik mit _____, anschliessend Wiedervorstellung zur Evaluation der indizierten Therapieoptionen.",
                                f"Zeitnahe Vorstellung {g('artikel_genitiv_klein','des/der')} {g('patient_genitiv','Patienten/in')} in der Sprechstunde der Kollegen der MOH USZ (Medizinische Onkologie und Hämatologie) zur Evaluation und ggf. Initiation einer begleitenden Systemtherapie. Eine diesbezügliche Anbindung ist unsererseits bereits aufgegleist; ein entsprechendes Aufgebot erfolgt zeitnah.",
                                f"Bei Exazerbation oder Neuauftreten von allfälligen Beschwerden ist eine ausserplanmässige Vorstellung in unserer ambulanten Sprechstunde jederzeit möglich."]

    elif bericht_typ == "a":
        print("Definiere Texte für Berrao Abschlusskontrolle (Typ a)...")

        # --- BEGINN NEUE LOGIK FÜR INDIKATIONSTEXT ---
        # Dieser Block kann später für andere Berichtstypen (z.B. 'e') wiederverwendet werden.
        
        # 1. Bestimme den zu verwendenden ICD-Code gemäß der festgelegten Priorität.
        icd_code_to_use = None
        if secondary_icd_code and secondary_icd_code.strip():
            icd_code_to_use = secondary_icd_code
            print(f"INFO: Verwende 'secondary_icd_code' für Indikationssuche: {icd_code_to_use}")
        elif icd_code and icd_code.strip():
            icd_code_to_use = icd_code
            print(f"INFO: Verwende primären 'icd_code' für Indikationssuche: {icd_code_to_use}")
        else:
            print("WARNUNG: Kein ICD-Code in patdata für die Indikationssuche gefunden.")

        # 2. Rufe den Indikationstext aus dem Mapping ab.
        fliesstext_indikation = ""  # Standardwert ist ein leerer String.
        if icd_code_to_use:
            # Ruft die Funktion aus dem importierten Modul auf
            retrieved_text = indikationen_mapping.get_indication_text(icd_code_to_use, INDICATIONS_MAP)
            
            # Wandelt das Ergebnis 'None' in einen leeren String um, falls nichts gefunden wird.
            fliesstext_indikation = retrieved_text or ""
            if fliesstext_indikation:
                 print(f"INFO: Indikationstext für {icd_code_to_use} erfolgreich gefunden. \n\n\nGefundener Text:\n{fliesstext_indikation}")
            else:
                 print(f"\n\n\nINFO: Kein spezifischer Indikationstext für {icd_code_to_use} gefunden. Feld bleibt leer.")
        # --- ENDE LOGIK FÜR INDIKATIONSTEXT ---

        texte["fliesstext_wir_berichten"] = f"Wir berichten Ihnen über oben {g('genannte_akkusativ', 'genannten/genannte')} {g('patient_akkusativ','Patienten/in')}, {g('artikel_akkusativ_klein','den/die')} wir am {heute} zur Abschlusskontrolle konsultiert haben."
        texte["fliesstext_onkologischer_krankheitsverlauf"] = (f" ")
        texte["fliesstext_aktueller_onkologischer_status"] = (f"Kürzlicher Abschluss ({datum_letzte_rt or '__.__.2025'}) der bei zugrundeliegendem {tumor or '____________'} durchgeführten, {therapieintention_klein}n Radiotherapie.")
        texte["fliesstext_indikation"] = fliesstext_indikation
        texte["fliesstext_anamnese"] = (f"{g('herrfrau','Herr/Frau')} {nachname} stellte sich planmässig zur heutigen Abschlusskontrolle vor, um mit uns den Verlauf"
                               f" der zuletzt durchgeführten Radiotherapie zu re-evaluieren sowie bei allfällig ausgeprägten Akuttoxizitäten oder Komplikationen entsprechend medizinische Massnahmen einzuleiten."
                               f"\n\n-")
        texte["fliesstext_allgemeinstatus"] = (f"{alter}-{g('jährig_nominativ','jährige/r')} {g('patient_nominativ','Patient/in')} in {beschreibung_ecog.get(ecog, "____")} Allgemeinzustand (ECOG {ecog}) und normalem Ernährungszustand. "
                                      f"{g('artikel_nominativ_gross','Der/Die')} {g('patient_nominativ','Patient/in')} zeigt sich wach und kooperativ, sowie zu allen Qualitäten orientiert. "
                                      f"Klinisch präsentiert sich {g('artikel_nominativ_klein','der/die')} {g('patient_nominativ','Patient/in')} normokard und eupnoeisch, sowie in Ruhe kardiopulmonal kompensiert."
                                      f"\n{status_tumorspezifisch}")
        texte["fliesstext_durchgef_therapie"] = (f"Zeitraum: {datum_erste_rt or '__.__.2025'} - {datum_letzte_rt or '__.__.2025'}\n\n"
                                        f"Dosiskonzept: {therapieintention_klein} Radiotherapie bei {tumor or '_______'}\n\n"
                                        f"{konzept_alle_serien}\n\n"
                                        f"Fraktionen: {fraktionen_woche or '__'}\n\n"
                                        f"Technik: Nach CT/MR-gestützer Planung erfolgte die Radiotherapie im Bereich oben genannter Lokalisationen am Linearbeschleuniger mit 6 MV Photonen in VMAT/Rapid Arc-Technik.")
        texte["fliesstext_verlauf_unter_therapie"] = (f"Die Radiotherapie konnte im o.g. Zeitraum zeitgerecht und -bis auf eine mild ausgeprägte _____ - komplikationslos durchgeführt werden.")
        texte["fliesstext_beurteilung"] = (f"Regelrechte Abschlusskontrolle nach erfolgter Radiotherapie.\nZum aktuellen Zeitpunkt präsentieren sich keine interventionsbedürftigen Akuttoxizitäten. ")
        texte["fliesstext_procedere"] = [f"Eine erste ambulante Verlaufskontrolle im Rahmen der radioonkologischen Therapienachsorge wird in ca. 6 Wochen in der ambulanten Sprechstunde von {prof_dr} {oberarzt} angestrebt. {g('artikel_nominativ_gross','Der/Die')} {g('patient_nominativ','Patient/in')} erhält zeitnah das entsprechende, direkte Aufgebot.",
                                f"Sonstiger weiterer Verlauf gemäss des leitliniengerechten, tumorspezifischen Nachsorgeschemas. {g('artikel_nominativ_gross','Der/Die')} {g('patient_nominativ','Patient/in')} ist zwecks entsprechender onkologischer Betreuung bei ______ angebunden.",
                                f"Bei Exazerbation oder Neuauftreten von tumor- oder therapieassoziierten Beschwerden ist eine ausserplanmässige Vorstellung in unserer ambulanten Sprechstunde allzeit möglich."]

    elif bericht_typ == "k":
        print("Definiere Texte für Berrao Klinische VK (Typ k)...\n\n")

        texte["fliesstext_wir_berichten"] = f"Wir berichten Ihnen über oben {g('genannte_akkusativ', 'genannten/genannte')} {g('patient_akkusativ','Patienten/in')}, {g('artikel_akkusativ_klein','den/die')} wir am {heute} zur klinischen Verlaufskontrolle konsultiert haben."
        texte["fliesstext_onkologischer_krankheitsverlauf"] = (f" ")
        texte["fliesstext_aktueller_onkologischer_status"] = (f"St. n. durchgeführter Radiotherapie im Rahmen der onkologischen Grunderkrankung eines {tumor or '_________'} vom {datum_erste_rt or '__.__.2025'} bis {datum_letzte_rt or '__.__.2025'}.")
        texte["fliesstext_indikation"] = (f" ")
        texte["fliesstext_anamnese"] = (f"{g('herrfrau','Herr/Frau')} {nachname} stellte sich planmässig zur heutigen klinischen Verlaufskontrolle im Rahmen der tumorspezifschen Nachsorge vor.\n\nAktuell berichtet {g('artikel_nominativ_klein','der/die')} {g('patient_nominativ','Patient/in')} über \n-")
        texte["fliesstext_allgemeinstatus"] = (f"{alter}-{g('jährig_nominativ','jährige/r')} {g('patient_nominativ','Patient/in')} in {beschreibung_ecog.get(ecog, "____")} Allgemeinzustand (ECOG {ecog}) und normalem Ernährungszustand. "
                                      f"{g('artikel_nominativ_gross','Der/Die')} {g('patient_nominativ','Patient/in')} zeigt sich wach und kooperativ, sowie zu allen Qualitäten orientiert. "
                                      f"Klinisch präsentiert sich {g('artikel_nominativ_klein','der/die')} {g('patient_nominativ','Patient/in')} normokard und eupnoeisch, sowie in Ruhe kardiopulmonal kompensiert."
                                      f"\n{status_tumorspezifisch}")
        texte["fliesstext_durchgef_therapie"] = (f" ")
        texte["fliesstext_verlauf_unter_therapie"] = (f" ")
        texte["fliesstext_beurteilung"] = (f"Klinisch und anamnestisch findet sich aktuell kein Anhalt für einen Tumorprogress oder höhergradige Spättoxizität der Radiotherapie. Insgesamt handelt es sich um einen erfreulichen Verlauf.")
        texte["fliesstext_procedere"] = [f"Nächste geplante Verlaufskontrolle in ____ Monaten.",
                                         f"Bildgebung ___ veranlasst/geplant.",
                                         f"Bei Exazerbation oder Neuauftreten von tumor- oder therapieassoziierten Beschwerden ist eine ausserplanmässige Vorstellung in unserer ambulanten Sprechstunde allzeit möglich."]

    elif bericht_typ == "t":
        print("Definiere Texte für Berrao Telefonische VK (Typ t)...\n\n")

        texte["fliesstext_wir_berichten"] = f"Wir berichten Ihnen über oben {g('genannte_akkusativ', 'genannten/genannte')} {g('patient_akkusativ','Patienten/in')}, {g('artikel_akkusativ_klein','den/die')} wir am {heute} zur telefonischen Verlaufskontrolle konsultiert haben."
        texte["fliesstext_onkologischer_krankheitsverlauf"] = (f" ")
        texte["fliesstext_aktueller_onkologischer_status"] = (f"St. n. durchgeführter Radiotherapie im Rahmen der onkologischen Grunderkrankung eines {tumor or '_________'} vom {datum_erste_rt or '__.__.2025'} bis {datum_letzte_rt or '__.__.2025'}.")
        texte["fliesstext_indikation"] = (f" ")
        texte["fliesstext_anamnese"] = (f"{g('herrfrau','Herr/Frau')} {nachname} wurde planmässig zur heutigen telefonischen Verlaufskontrolle im Rahmen der tumorspezifschen Nachsorge bei {tumor or '_______'} kontaktiert.\n\nEigenanamnestisch berichtet {g('artikel_nominativ_klein','der/die')} {g('patient_nominativ','Patient/in')} über \n\n-")
        texte["fliesstext_allgemeinstatus"] = (f"{g('artikel_nominativ_gross','Der/Die')} {g('patient_nominativ','Patient/in')} macht im Gespräch einen kooperativen und kognitiv adäquaten Eindruck. Eine klinische Beurteilung ist im Rahmen der telefonischen Verlaufskontrolle nicht erfolgt.")
        texte["fliesstext_durchgef_therapie"] = (f" ")
        texte["fliesstext_verlauf_unter_therapie"] = (f" ")
        texte["fliesstext_beurteilung"] = (f"{g('artikel_nominativ_gross','Der/Die')} {g('patient_nominativ','Patient/in')} präsentiert sich -bis auf ______- im Rahmen der radioonkologischen Nachsorge bei vorbekanntem {tumor or '______'} in regelrechtem Verlauf.")
        texte["fliesstext_procedere"] = [f"Nächste geplante Verlaufskonsultation in ___ Monaten.",
                                         f"Bildgebung ___ empfohlen/veranlasst.",
                                         f"Bei Exazerbation oder Neuauftreten von tumor- oder therapieassoziierten Beschwerden ist eine ausserplanmässige Vorstellung in unserer ambulanten Sprechstunde allzeit möglich."]

    elif bericht_typ == "w":
        print("Definiere Texte für Berrao Wochenkontrolle (Typ w)...")

        texte["fliesstext_subjektiv"] = (f"Vorstellung {g('artikel_genitiv_klein','des/der')} {alter}-{g('jährig_genitiv','jährigen')} {g('patient_genitiv','Patienten/in')} am {heute} zur Wochenkontrolle im Rahmen der Radiotherapie bei {tumor} nach aktuell xx/xx Fraktionen."
                                f"\n\n{g('artikel_nominativ_gross','Der/Die')} {g('patient_nominativ','Patient/in')} berichtet über Wohlbefinden und bisher gute Verträglichkeit der durchgeführten Radiotherapie."
                                f"\n\nLediglich wird über eine zum aktuellen Zeitpunkt mild ausgeprägte _____ berichtet. Sonstige Symptome werden seitens {g('artikel_genitiv_klein','des/der')} {g('patient_genitiv','Patienten/in')} verneint.")
        texte["fliesstext_objektiv"] = (f"{alter}-{g('jährig_nominativ','jährige/r')} {g('patient_nominativ','Patient/in')} in {beschreibung_ecog.get(ecog, "____")} Allgemeinzustand (ECOG {ecog}) und normalem Ernährungszustand. "
                                      f"{g('artikel_nominativ_gross','Der/Die')} {g('patient_nominativ','Patient/in')} zeigt sich wach und kooperativ, sowie zu allen Qualitäten orientiert. "
                                      f"Klinisch präsentiert sich {g('artikel_nominativ_klein','der/die')} {g('patient_nominativ','Patient/in')} normokard und eupnoeisch, sowie in Ruhe kardiopulmonal kompensiert."
                                      f"\n{status_tumorspezifisch}")
        texte["fliesstext_beurteilung"] = (f"Unauffällige klinische Wochenkontrolle unter laufender Radiotherapie bei {tumor}.")
        texte["fliesstext_procedere"] = (f"Fortführung der aktuell durchgeführten Radiotherapie wie geplant.")

    else:
        print(f"WARNUNG: Unbekannter Berrao-Typ '{bericht_typ}' in fliesstexte.py.")
        # Fülle alle möglichen Keys mit leeren Strings, um Fehler im Hauptskript zu vermeiden
        possible_keys = [
            "fliesstext_wir_berichten", "fliesstext_onkologischer_krankheitsverlauf",
            "fliesstext_aktueller_onkologischer_status", "fliesstext_indikation",
            "fliesstext_anamnese", "fliesstext_allgemeinstatus",
            "fliesstext_durchgef_therapie", "fliesstext_verlauf_unter_therapie",
            "fliesstext_beurteilung", "fliesstext_procedere",
            "fliesstext_subjektiv", "fliesstext_objektiv"
        ]
        for key in possible_keys:
            texte[key] = ""

    
    standard_keys = [
        "fliesstext_wir_berichten", "fliesstext_onkologischer_krankheitsverlauf",
        "fliesstext_aktueller_onkologischer_status", "fliesstext_indikation",
        "fliesstext_anamnese", "fliesstext_allgemeinstatus",
        "fliesstext_durchgef_therapie", "fliesstext_verlauf_unter_therapie",
        "fliesstext_beurteilung", "fliesstext_procedere"
    ]
    woko_keys = ["fliesstext_subjektiv", "fliesstext_objektiv", "fliesstext_beurteilung", "fliesstext_procedere"]

    all_expected_keys = set(standard_keys + woko_keys)
    for key in all_expected_keys:
        if key not in texte:
            texte[key] = "" 

    return texte

def define_wochenendeintrag(patdata, eintrittsdatum):
    """
    Definiert die Fließtexte für Wochenendeintrag.
        patdata (dict): Das Dictionary mit den Patientendaten.
        glossary (dict): Das Dictionary mit geschlechtsspezifischen Begriffen.

    Returns:
        dict: Ein Dictionary mit den generierten Texten. Schlüssel entsprechen
              den ursprünglichen Variablennamen (z.B. 'fliesstext_wir_berichten').
              Gibt leere Strings für nicht zutreffende Texte zurück.
    """


    # Extrahiere benötigte Variablen aus patdata (mit Defaults)
    if isinstance(patdata, dict):
        print("Lese Patientendaten aus Dictionary...")
        nachname = patdata.get("nachname", "")
        vorname = patdata.get("vorname", "")
        geburtsdatum = patdata.get("geburtsdatum", "")
        alter = patdata.get("alter", "")
        geschlecht = patdata.get("geschlecht", "")
        patientennummer = patdata.get("patientennummer", "")
        #eintrittsdatum = patdata.get("eintrittsdatum", "")
        spi = patdata.get("spi", "")
        rea = patdata.get("rea", "")
        ips = patdata.get("ips", "")
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

    print("Starte Definition des glossary in define_wochenendeintrag")
    if geschlecht: 
        glossary = UNIVERSAL.create_patdata_glossary(geschlecht); print(f"Glossary definiert.\n")
    else: print("WARNUNG: Geschlecht nicht definiert."); glossary = UNIVERSAL.create_patdata_glossary(None)
    # Zugriff auf Glossary über Hilfsfunktion
    g = lambda key, default="": _get_from_glossary(glossary, key, default)

    # Kombiniere RT-Konzept
    konzepte = [str(k) for k in [behandlungskonzept_serie1, behandlungskonzept_serie2, behandlungskonzept_serie3, behandlungskonzept_serie4] if k]
    konzept_alle_serien = "\n".join(konzepte) if konzepte else "Nicht erfasst"

    # Therapieintention mappen
    map_gross = {"kurativ": "Kurativ-intendierte", "palliativ": "Palliativ-intendierte", "lokalablativ": "Lokalablativ-intendierte"}
    map_klein = {"kurativ": "kurativ-intendierte", "palliativ": "palliativ-intendierte", "lokalablativ": "lokalablativ-intendierte"}
    therapieintention_gross = map_gross.get(therapieintention, "______-intendierte")
    therapieintention_klein = map_klein.get(therapieintention, "______-intendierte")

    #individuelle Fall-Variablen für Texte
    rct = 'Radiochemotherapie' if chemotherapeutikum not in [None, '', '-', 'none', 'nicht erfasst'] else 'Radiotherapie'
    chemo = f' mit {chemotherapeutikum}' if rct == 'Radiochemotherapie' else ''
    prof_dr = "Prof." if oberarzt.lower() in ["guckenberger", "andratschke", "balermpas"] else "Dr."
    if rct == 'Radiochemotherapie':
        chemo_in_dt = f'Systemtherapie im Rahmen der Hospitalisation: {chemotherapeutikum}, Zyklus ____ zuletzt am _____ verabreicht.'
    else:
        chemo_in_dt = ""
    beschreibung_ecog = {0: 'altersentsprechendem', 1: 'leicht reduziertem', 2: 'reduziertem', 3: 'deutlich reduziertem', 4: 'stark reduziertem'}
    
    aktueller_stand = ""
    if datum_erste_rt and datum_letzte_rt and konzept_alle_serien:
            aktueller_stand = f"\n\nRT-Konzept:\n{datum_erste_rt} - {datum_letzte_rt}: {therapieintention_gross} Radiotherapie der {konzept_alle_serien}."
    eintrag = (f"{alter}-{g('jährig_nominativ','jährige/r')} {g('patient_nominativ','Patient/in')} in {beschreibung_ecog.get(ecog, "____")} Allgemeinzustand (ECOG {ecog}) im Rahmen der onkologischen Grunderkrankung bei {tumor}."
               f"\nDie stationäre Aufnahme erfolgte am {eintrittsdatum} aufgrund {aufnahmegrund}."
               f"{aktueller_stand}"
               f"\n\nREA/IPS-Status:\nREA = {rea}\nIPS = {ips}"
               f"\n\nProbleme/Komplikationen: Keine erwartet"
               f"\n\nTo Dos:")
    
    return eintrag
    
