# -*- coding: utf-8 -*-
# Dictionary für primäre Tumoren und andere Erkrankungen

entity_dictionary_icd = {
    #Universale:
    'Gutartige Neubildung an nicht näher bezeichneter Lokalisation': 'D36.9',
    'Bösartige Neubildung ohne Angabe der Lokalisation': 'C80.9',
    'CUP-Syndrom': 'C80.0', #Bösartige Neubildung, primäre Lokalisation unbekannt, so bezeichnet
    
    # --- Neuro-Okologie / Weichteiltumore ---
    'Glioblastom': 'C71.9', # Bösartige Neubildung des Gehirns, nicht näher bezeichnet
    'Astrozytom': 'C71.9', # Bösartige Neubildung des Gehirns, nicht näher bezeichnet (als allgemeiner Code für Hirntumor)
    'Oligodendrogliom': 'C71.9', # Bösartige Neubildung des Gehirns, nicht näher bezeichnet
    'Meningeom': 'D32.9', # Gutartige Neubildung der Meningen, nicht näher bezeichnet (häufigste Form)
    'Vestibularisschwannom': 'D33.3', # Gutartige Neubildung der Hirnnerven
    'Schwannom': 'D36.9', #	Gutartige Neubildung an nicht näher bezeichneter Lokalisation
    'Hypophysenadenom': 'D35.2', # Gutartige Neubildung der Hypophyse
    'Kraniopharyngeom': 'D44.4', #Neubildung unsicheren oder unbekannten Verhaltens der endokrinen Drüsen, Ductus craniopharyngealis
    'Arteriovenöse Malformation': 'Q28.29', #Angeborene arteriovenöse Fehlbildung der zerebralen Gefäße, nicht näher bezeichnet

    'Sarkom': 'C49.9', #Bösartige Neubildung: Bindegewebe und andere Weichteilgewebe, nicht näher bezeichnet.

    # --- Kopf-Hals (erweitert) ---
    'Karzinom der Lippe': 'C00.9', # Bösartige Neubildung der Lippe, nicht näher bezeichnet
    'Zungengrundkarzinom': 'C01', # Bösartige Neubildung des Zungengrundes
    'Zungenkarzinom': 'C02.9', # Bösartige Neubildung der Zunge, nicht näher bezeichnet
    'Gingivakarzinom': 'C03.9', # Bösartige Neubildung des Zahnfleisches [Gingiva], nicht näher bezeichnet
    'Mundbodenkarzinom': 'C04.9', # Bösartige Neubildung des Mundbodens, nicht näher bezeichnet
    'Karzinom der Mundhöhle': 'C06.9', # Bösartige Neubildung des Mundes, nicht näher bezeichnet
    'Tonsillenkarzinom': 'C09.9', # Bösartige Neubildung der Tonsille, nicht näher bezeichnet
    'Nasenkarzinom': 'C30.0', # Bösartige Neubildung der Nasenhöhle
    'Nasopharynxkarzinom': 'C11.9', # Bösartige Neubildung des Nasopharynx, nicht näher bezeichnet
    'Oropharynxkarzinom': 'C10.9', # Bösartige Neubildung des Oropharynx, nicht näher bezeichnet
    'Larynxkarzinom': 'C32.9', # Bösartige Neubildung des Larynx, nicht näher bezeichnet
    'Speicheldrüsenkarzinom': 'C08.9', # Bösartige Neubildung einer großen Speicheldrüse, nicht näher bezeichnet

    # --- Haut ---
    'Malignes Melanom': 'C43.9', # Bösartiges Melanom der Haut, nicht näher bezeichnete Lokalisation
    'Merkelzellkarzinom': 'C4A.9', # Merkelzell-Karzinom, nicht näher bezeichnete Lokalisation (ICD-10-GM spezifisch)
    'Basalzellkarzinom': 'C44.9', # Sonstige bösartige Neubildungen der Haut, nicht näher bezeichnete Lokalisation
    'Kutanem Plattenepithelkarzinom': 'C44.9', # Sonstige bösartige Neubildungen der Haut, nicht näher bezeichnete Lokalisation
   

    # --- Lymphsystem / Hämatologie ---
    'Diffus-grosszelligem B-Zell-Lymphom': 'C83.3', # Diffuses großzelliges B-Zell-Lymphom
    'Hodgkin-Lymphom': 'C81.9', # Hodgkin-Lymphom, nicht näher bezeichneter Typ
    'MALT-Lymphom': 'C88.4', # Extranodales Marginalzonen-B-Zell-Lymphom des Mukosa-assoziierten lymphatischen Gewebes [MALT-Lymphom]
    'Plasmozytom': 'C90.2', # Plasmozytom, extramedullär
    'Thymom': 'C37', #Bösartige Neubildung des Thymus

    # --- Thorax ---
    'Adenokarzinom der Lunge (NSCLC)': 'C34.9', # Bösartige Neubildung des Bronchus oder der Lunge, nicht näher bezeichnet
    'Plattenepithelkarzinom der Lunge (NSCLC)': 'C34.9', # Bösartige Neubildung des Bronchus oder der Lunge, nicht näher bezeichnet
    'Bronchialkarzinom (NSCLC)': 'C34.9', # Bösartige Neubildung des Bronchus oder der Lunge, nicht näher bezeichnet
    'Kleinzelligem Lungenkarzinom (SCLC)': 'C34.9', # Bösartige Neubildung des Bronchus oder der Lunge, nicht näher bezeichnet
    'Mesotheliom': 'C45.9', # Mesotheliom, nicht näher bezeichnete Lokalisation

    # --- Abdomen / Gastrointestinal ---
    'Cholangiocellulärem Karzinom': 'C24.9', # Bösartige Neubildung der Gallenwege, nicht näher bezeichneter Teil
    'Hepatocellulärem Karzinom': 'C22.0', # Leberzellkarzinom
    'Ösophaguskarzinom': 'C15.9', # Bösartige Neubildung des Ösophagus, nicht näher bezeichneter Teil
    'Pankreaskarzinom': 'C25.9', # Bösartige Neubildung des Pankreas, nicht näher bezeichneter Teil
    'Kolonkarzinom': 'C18.9', # Bösartige Neubildung des Kolons, nicht näher bezeichneter Teil
    'Rektumkarzinom': 'C20', # Bösartige Neubildung des Rektums
    'Analkarzinom': 'C21.0', # Bösartige Neubildung des Anus, nicht näher bezeichnet

    # --- Urogenital ---
    'Nierenzellkarzinom': 'C64.9', # Bösartige Neubildung der Niere, ausgenommen Nierenbecken, nicht näher bezeichnet
    'Urothelkarzinom der Blase': 'C67.9', # Bösartige Neubildung der Harnblase, nicht näher bezeichneter Teil
    'Prostatakarzinom': 'C61', # Bösartige Neubildung der Prostata

    # --- Gynäkologie ---
    'Mammakarzinom': 'C50.9', # Bösartige Neubildung der Brustdrüse [Mamma], nicht näher bezeichnete Lokalisation
    'Endometriumkarzinom': 'C54.1', # Bösartige Neubildung des Endometriums
    'Cervixkarzinom': 'C53.9', # Bösartige Neubildung der Cervix uteri, nicht näher bezeichneter Teil
    'Vaginakarzinom': 'C52.9', # Bösartige Neubildung der Vagina, nicht näher bezeichneter Teil
    'Vulvakarzinom': 'C51.9', # Bösartige Neubildung der Vulva, nicht näher bezeichneter Teil

    # --- Andere Erkrankungen ---
    'Fasciitis plantaris': 'M72.2', # Fasciitis plantaris
    'Achillodynie': 'M76.6', # Tendinitis der Achillessehne
    'Heterotope Ossifikation': 'M61.9', # Verkalkung und Verknöcherung von Muskeln, nicht näher bezeichnet
    'Endokrine Orbitopathie': 'H06.2', # Exophthalmus bei Störungen der Schilddrüsenfunktion
    'Epicondylopathia humeri': 'M77.1', # Epicondylitis radialis humeri [Tennisellenbogen] (häufigste Form)
    'Morbus Dupuytren': 'M72.0', # Fibromatose der Palmarfaszie [Dupuytren-Kontraktur]
    'Morbus Ledderhose': 'M72.2', # Fibromatose der Plantarfaszie [Ledderhose-Kontraktur]
    'Induratio penis plastica': 'N48.6', # Induratio penis plastica
    'Enthesiopathie': 'M77.9', # Enthesiopathie, nicht näher bezeichnet
    'Periarthropathia humeroscapularis': 'M75.9', # Schulterläsion, nicht näher bezeichnet
    'Gonarthrose': 'M17.9', # Gonarthrose, nicht näher bezeichnet
    'Arthrose': 'M19.9', # Arthrose, nicht näher bezeichnet
    'Gynäkomastie': 'N62', # Gynäkomastie
    'Keloid': 'L91.0', # Keloidnarbe
}

# Dictionary für sekundäre Neoplasien (Metastasen) - ERGÄNZT
secondary_neoplasms_icd = {
    'Lymphknotenmetastasen': 'C77.9', # Sekundäre bösartige Neubildung der Lymphknoten, nicht näher bezeichnete Lokalisation
    'Hirnmetastasen': 'C79.3', # Sekundäre bösartige Neubildung des Gehirns und der Hirnhäute
    'Knochenmetastasen': 'C79.5', # Sekundäre bösartige Neubildung des Knochens und des Knochenmarkes
    'Lungenmetastasen': 'C78.0', # Sekundäre bösartige Neubildung der Lunge
    'Lebermetastasen': 'C78.7', # Sekundäre bösartige Neubildung der Leber und der intrahepatischen Gallengänge
    'Weichteilmetastasen': 'C79.8', # Sekundäre bösartige Neubildung an sonstigen näher bezeichneten Lokalisationen
    'Sonstige Fernmetastasierung': 'C79.9', # Sekundäre bösartige Neubildung an nicht näher bezeichneten Lokalisationen
}

# Dictionary mit Keywords für das Matching (unverändert)
entity_keywords = {
    # --- Universal ---
    'CUP-Syndrom': ['cup', 'cancer of unknown'],
    
    # --- Neurologie / ZNS ---
    'Glioblastom': ['gliobl'],
    'Astrozytom': ['astrozy'],
    'Oligodendrogliom': ['oligodendro'],
    'Meningeom': ['meningeom'],
    'Vestibularisschwannom': ['vestibularisschwannom', 'larisschwannom', 'akustikusneurinom', 'akustikus', 'vestibularissch'],
    'Schwannom': [' schwannom'],
    'Hypophysenadenom': ['hypophy'],
    'Kraniopharyngeom': ['raniopharyng'],
    'Arteriovenöse Malformation': ['arteriovenöse Malf', 'venöse Malf', 'avm'],

    'Sarkom': ['sarkom'],

    # --- Kopf-Hals (Spezifisch vor Generisch) ---
    'Zungengrundkarzinom': ['zungengrund'],
    'Zungenkarzinom': ['zungenkarzinom', 'zungenrand', 'zunge'],
    'Gingivakarzinom': ['gingivakarzinom', 'gingiva', 'zahnfleisch'],
    'Mundbodenkarzinom': ['mundbodenkarzinom', 'mundboden'],
    'Tonsillenkarzinom': ['tonsillenkarzinom', 'tonsille'],
    'Karzinom der Lippe': ['lippenkarzinom', 'lippe'],
    'Karzinom der Mundhöhle': ['mundhöhlenkarzinom', 'karzinom der mundhöhle', 'mundhöhle', 'vestibulum oris'],
    'Nasenkarzinom': ['nasenkarz', 'vestibulum nasi', 'nasenhöhle'],
    'Nasopharynxkarzinom': ['nasopharynxkarzinom', 'nasopharynx', 'epipharynx'],
    'Oropharynxkarzinom': ['oropharynxkarzinom', 'oropharynx'],
    'Larynxkarzinom': ['larynxkarzinom', 'larynx', 'kehlkopf', 'stimmlippe'],
    'Speicheldrüsenkarzinom': ['speicheldrüsenkarzinom', 'speicheldrüse', 'parotis', 'submandibularis'],


    # --- Haut ---
    'Malignes Melanom': ['malignes melanom', 'melanom', 'malignes m'],
    'Merkelzellkarzinom': ['merkelzellkarzinom', 'merkelzell'],
    'Basalzellkarzinom': ['basalzellkarzinom', 'basaliom', 'basalzell'],
    'Kutanem Plattenepithelkarzinom': ['kutanem plattenepithelkarzinom', 'plattenepithelkarzinom der haut', 'peca', 'spinaliom'],

    # --- Lymphsystem / Hämatologie ---
    'Diffus-grosszelligem B-Zell-Lymphom': ['diffus-grosszellig', 'dlbcl', 'diffus grosszell'],
    'Hodgkin-Lymphom': ['hodgkin-lymphom', 'hodgkin-lymphom', 'hodgkin', 'm. hodgkin'],
    'MALT-Lymphom': ['malt-lymphom', 'malt', 'maltom'],
    'Plasmozytom': ['plasmozytom', 'myelom'],
    'Thymom': ['thymom', 'thymus'],

    # --- Thorax ---
    'Adenokarzinom der Lunge (NSCLC)': ['adenokarzinom der lunge', 'adeno lunge', 'nsclc adeno', 'adeno nsclc', 'adeno lappen'],
    'Plattenepithelkarzinom der Lunge (NSCLC)': ['plattenepithelkarzinom der lunge', 'platten lunge', 'nsclc platten', 'platten nsclc', 'platten lappen'],
    'Bronchialkarzinom (NSCLC)': ['bronchialkarzinom', 'bronchialcar'],
    'Kleinzelligem Lungenkarzinom (SCLC)': ['kleinzellig lungenkarzinom', 'sclc', 'kleinzellig lunge', 'lunge kleinzellig'],
    'Mesotheliom': ['mesotheliom'],

    # --- Abdomen / Gastrointestinal ---
    'Cholangiocellulärem Karzinom': ['cholangio', 'ccc', 'gallenweg', 'gallengang'],
    'Hepatocellulärem Karzinom': ['hepatocellulärem karzinom', 'hcc', 'leberkarzinom', 'hepatozellu', 'hepatocellu'],
    'Ösophaguskarzinom': ['ösophaguskarzinom', 'ösophagus', 'speiseröhre', 'esophagus', 'oesophagus'],
    'Pankreaskarzinom': ['pankreaskarzinom', 'pankreas', 'pdac'],
    'Kolonkarzinom': ['kolonkarzinom', 'kolon', 'colon'],
    'Rektumkarzinom': ['rektumkarzinom', 'rektum', 'rectum', 'mastdarm'],
    'Analkarzinom': ['analkarzinom', 'anal', 'anus'],

    # --- Urogenital ---
    'Nierenzellkarzinom': ['nierenzellkarzinom', 'rcc', 'ncc','nierenzell'],
    'Urothelkarzinom der Blase': ['urothelkarzinom der blase', 'urothel blase', 'blasenkarzinom', 'harnblase'],
    'Prostatakarzinom': ['prostatakarzinom', 'prostata'],

    # --- Gynäkologie ---
    'Mammakarzinom': ['mammakarzinom', 'mamma', 'brustkrebs', 'brust'],
    'Endometriumkarzinom': ['endometriumkarzinom', 'endometrium', 'corpuskarzinom', 'uterus', 'korpus'],
    'Cervixkarzinom': ['cervixkarzinom', 'cervix', 'zervix'],
    'Vaginakarzinom': ['vaginakarzinom', 'vagina', 'scheidenkarzinom', 'scheide'],
    'Vulvakarzinom': ['vulvakarzinom', 'vulva'],

    # --- Andere Erkrankungen ---
    'Fasciitis plantaris': ['fasciitis plantaris', 'fasciitis', 'fersensporn'],
    'Achillodynie': ['achillodynie', 'achillo', 'achillessehne'],
    'Heterotope Ossifikation': ['heterotope ossifikation'],
    'Endokrine Orbitopathie': ['endokrine orbitopathie', 'basedow', 'exophthalmus'],
    'Epicondylopathia humeri': ['epicondylopathia humeri', 'epicondylitis', 'tennisellenbogen', 'golferellenbogen'],
    'Morbus Dupuytren': ['morbus dupuytren', 'dupuytren', 'palmarfibromatose'],
    'Morbus Ledderhose': ['morbus ledderhose', 'ledderhose', 'plantarfibromatose'],
    'Induratio penis plastica': ['induratio penis'],
    'Enthesiopathie': ['enthesiopathie', 'enthesio'],
    'Periarthropathia humeroscapularis': ['periarthropathia humeroscapularis', 'periarthropathia'],
    'Gonarthrose': ['gonarthrose', 'kniearthrose'],
    'Arthrose': ['arthrose', 'gelenkarthrose'],
    'Gynäkomastie': ['gynäkomastie'],
    'Keloid': ['keloid', 'narbe'],

    # --- Sekundär (Keywords nur für find_matching_entity relevant, nicht für manuelle Auswahl) ---
    'Lymphknotenmetastasen': ['lymphknotenmetastasen', 'lymphknoten'],
    'Hirnmetastasen': ['hirnmetastas', 'zerebralmetastas', 'gehirn metastas', 'cerebell metast'],
    'Knochenmetastasen': ['knochenmetastasen', 'ossär', 'skelettmetastasen', 'knochen metast'],
    'Lungenmetastasen': ['lungenmetastasen', 'pulmonalmetastasen', 'lunge metast'],
    'Lebermetastasen': ['lebermetastasen', 'hepatische metastasen', 'leber metastas'],
    'Weichteilmetastasen': ['weichteilmetastasen', 'subkutan metast', 'musk metastas', 'weichteil metasta'],
    'Sonstige Fernmetastasierung': ['fernmetastase', 'fernmetastasierung', 'metastase nnb'], # Keywords hinzugefügt
}


uaw_mapping = {
    #Universale:
    'Gutartige Neubildung an nicht näher bezeichneter Lokalisation': '',
    'Bösartige Neubildung ohne Angabe der Lokalisation': '',
    'CUP-Syndrom': '',

    # --- Neurologie / ZNS ---
    'Glioblastom': 'Alopezie, Radiodermatitis, Fatigue, Hirnödem mit entsprechender Hirndrucksymptomatik, Kognitionsstörung sowie Radionekrose',
    'Astrozytom': 'Alopezie, Radiodermatitis, Fatigue, Hirnödem mit entsprechender Hirndrucksymptomatik, Kognitionsstörung sowie Radionekrose',
    'Oligodendrogliom': 'Alopezie, Radiodermatitis, Fatigue, Hirnödem mit entsprechender Hirndrucksymptomatik sowie eine potenzielle Radionekrose',
    'Meningeom': 'Alopezie, Fatigue, Radiodermatitis, Hirnödem, Verschlechterung des Hörvermögens sowie Kognitionsstörungen',
    'Vestibularisschwannom': 'Verschlechterung des Hörvermögens bis hin zum vollständigen Hörverlust, Tinnitus, Schwindel und Gleichgewichtsstörungen, Schädigung der Nn. facialis et trigeminus, Pseudoprogress mit Kompression von Umgebungsstrukturen sowie Fatigue und Müdigkeit',
    'Schwannom': '', #keine allgemeine Aussage gültig, lageabhängig
    'Hypophysenadenom': 'Müdigkeit, Fatigue, Hypophyseninsuffizienz mit ggf. notwendiger Hormonsubstitution, langfristig leicht erhöhtes Risiko für Schlaganfälle aufgrund der Nähe zur A. carotis im Sinus cavernosus sowie selten Gesichtsfeldstörungen bei Affektion des N. opticus/Chiasma (<3% Risiko)',
    'Kraniopharyngeom': 'Müdigkeit, Fatigue, Hypophyseninsuffizienz mit ggf. notwendiger Hormonsubstitution, langfristig leicht erhöhtes Risiko für Schlaganfälle aufgrund der Nähe zur A. carotis im Sinus cavernosus sowie selten Gesichtsfeldstörungen bei Affektion des N. opticus/Chiasma (<3% Risiko)',
    'Arteriovenöse Malformation': '',
    
    'Sarkom': '', #keine allgemeine Aussage gültig, lageabhängig

    # --- Kopf-Hals (erweitert) ---
    'Karzinom der Lippe': '',
    'Zungengrundkarzinom': '',
    'Zungenkarzinom': '',
    'Gingivakarzinom': '',
    'Mundbodenkarzinom': '',
    'Karzinom der Mundhöhle': '',
    'Tonsillenkarzinom': '',
    'Nasenkarzinom': '',
    'Nasopharynxkarzinom': '',
    'Oropharynxkarzinom': '',
    'Larynxkarzinom': '',
    'Speicheldrüsenkarzinom': '',

    # --- Haut ---
    'Malignes Melanom': '',
    'Merkelzellkarzinom': '',
    'Basalzellkarzinom': '',
    'Kutanem Plattenepithelkarzinom': '',

    # --- Lymphsystem / Hämatologie ---
    'Diffus-grosszelligem B-Zell-Lymphom': '',
    'Hodgkin-Lymphom': '',
    'MALT-Lymphom': '',
    'Plasmozytom': '',
    'Thymom': '',

    # --- Thorax ---
    'Adenokarzinom der Lunge (NSCLC)': 'Dyspnoe, Ösophagitis, Pneumonitis und Lungenfibrose, Fatigue, Radiodermatitis, Appetitlosigkeit sowie Nausea und Emesis',
    'Plattenepithelkarzinom der Lunge (NSCLC)': 'Dyspnoe, Ösophagitis, Pneumonitis und Lungenfibrose, Fatigue, Radiodermatitis, Appetitlosigkeit sowie Nausea und Emesis',
    'Kleinzelligem Lungenkarzinom (SCLC)': ' Dyspnoe, Ösophagitis, Pneumonitis und Lungenfibrose, Fatigue, Radiodermatitis, Appetitlosigkeit sowie Nausea und Emesis',
    'Mesotheliom': '',

    # --- Abdomen / Gastrointestinal ---
    'Cholangiocellulärem Karzinom': 'Nausea und Emesis, Fatigue, Leberfunktionsstörungen, Oberbauchschmerzen, Appetitlosigkeit, Diarrhoe sowie selten Darmperforationen',
    'Hepatocellulärem Karzinom': 'Nausea und Emesis, Fatigue, Leberfunktionsstörungen, Oberbauchschmerzen, Appetitlosigkeit, Diarrhoe sowie selten Darmperforationen',
    'Ösophaguskarzinom': '',
    'Pankreaskarzinom': ' Nausea und Emesis, Fatigue, Leberfunktionsstörungen, Oberbauchschmerzen, Appetitlosigkeit, Diarrhoe sowie selten Darmperforationen',
    'Kolonkarzinom': '',
    'Rektumkarzinom': '',
    'Analkarzinom': '',

    # --- Urogenital ---
    'Nierenzellkarzinom': '',
    'Urothelkarzinom der Blase': '',
    'Prostatakarzinom': '',

    # --- Gynäkologie ---
    'Mammakarzinom': '',
    'Endometriumkarzinom': '',
    'Cervixkarzinom': '',
    'Vaginakarzinom': '',
    'Vulvakarzinom': '',

    # --- Andere Erkrankungen ---
    'Fasciitis plantaris': '',
    'Achillodynie': '',
    'Heterotope Ossifikation': '',
    'Endokrine Orbitopathie': '',
    'Epicondylopathia humeri': '',
    'Morbus Dupuytren': '',
    'Morbus Ledderhose': '',
    'Induratio penis plastica': '',
    'Enthesiopathie': '',
    'Periarthropathia humeroscapularis': '',
    'Gonarthrose': '',
    'Arthrose': '',
    'Gynäkomastie': '',
    'Keloid': '',

    #Sekundärneoplasien/ Metastasierung
    'Lymphknotenmetastasen': 'Radiodermatitis, Fatigue', #
    'Hirnmetastasen': 'Alopezie, Radiodermatitis, Fatigue, Hirnödem mit entsprechender Hirndrucksymptomatik, Kognitionsstörung sowie Radionekrose', #
    'Knochenmetastasen': 'Fatigue, Radiodermatitis, sowie selten bei grossem Bestrahlungsfeld mögliche Knochenmarksinsuffizienz', #
    'Lungenmetastasen': 'Dyspnoe, Pneumonitis und Lungenfibrose, Ösophagitis, Fatigue, Radiodermatitis, Appetitlosigkeit sowie Nausea und Emesis', #
    'Lebermetastasen': '', #
    'Weichteilmetastasen': '', #
    'Sonstige Fernmetastasierung': '',
}


status_tumorspezifisch_mapping = {
    #Universale:
    'Gutartige Neubildung an nicht näher bezeichneter Lokalisation': '',
    'Bösartige Neubildung ohne Angabe der Lokalisation': '',
    'CUP-Syndrom': '',

    # --- Neurologie / ZNS ---
    'Glioblastom': 'Grob orientierender neurologischer Untersuchungsbefund, inkl. Hirnnervenstatus, bis auf ______ ohne pathologischen Befund',
    'Astrozytom': 'Grob orientierender neurologischer Untersuchungsbefund, inkl. Hirnnervenstatus, bis auf ______ ohne pathologischen Befund',
    'Oligodendrogliom': 'Grob orientierender neurologischer Untersuchungsbefund, inkl. Hirnnervenstatus, bis auf ______ ohne pathologischen Befund',
    'Meningeom': 'Grob orientierender neurologischer Untersuchungsbefund, inkl. Hirnnervenstatus, bis auf ______ ohne pathologischen Befund.',
    'Vestibularisschwannom': 'Grob orientierender neurologischer Untersuchungsbefund, inkl. Hirnnervenstatus, bis auf ______ ohne pathologischen Befund. Romberg-Versuch negativ, Seiltänzergang möglich.',
    'Schwannom': '', #keine allgemeine Aussage gültig, lageabhängig
    'Hypophysenadenom': 'Grob orientierender neurologischer Untersuchungsbefund unauffällig. Visus in allen Gesichtsfeldquadranten fingerperimetrisch erhalten, kein Hinweis auf Kompression des Chiasma opticus',
    'Sarkom': '', #keine allgemeine Aussage gültig, lageabhängig

    # --- Kopf-Hals (erweitert) ---
    'Karzinom der Lippe': '',
    'Zungengrundkarzinom': '',
    'Zungenkarzinom': '',
    'Gingivakarzinom': '',
    'Mundbodenkarzinom': '',
    'Karzinom der Mundhöhle': '',
    'Tonsillenkarzinom': '',
    'Nasenkarzinom': '',
    'Nasopharynxkarzinom': '',
    'Oropharynxkarzinom': '',
    'Larynxkarzinom': '',
    'Speicheldrüsenkarzinom': '',

    # --- Haut ---
    'Malignes Melanom': '',
    'Merkelzellkarzinom': '',
    'Basalzellkarzinom': '',
    'Kutanem Plattenepithelkarzinom': '',

    # --- Lymphsystem / Hämatologie ---
    'Diffus-grosszelligem B-Zell-Lymphom': '',
    'Hodgkin-Lymphom': '',
    'MALT-Lymphom': '',
    'Plasmozytom': '',
    'Thymom': '',

    # --- Thorax ---
    'Adenokarzinom der Lunge (NSCLC)': 'Körperliche Stigmata im Sinne von Halsvenenstauung, Uhrglasnägeln oder Lippenzyanose sind nicht präsent.',
    'Plattenepithelkarzinom der Lunge (NSCLC)': 'Körperliche Stigmata im Sinne von Halsvenenstauung, Uhrglasnägeln oder Lippenzyanose sind nicht präsent.',
    'Kleinzelligem Lungenkarzinom (SCLC)': 'Körperliche Stigmata im Sinne von Halsvenenstauung, Uhrglasnägeln oder Lippenzyanose sind nicht präsent.',
    'Mesotheliom': 'Körperliche Stigmata im Sinne von Halsvenenstauung, Uhrglasnägeln oder Lippenzyanose sind nicht präsent.',

    # --- Abdomen / Gastrointestinal ---
    'Cholangiocellulärem Karzinom': '',
    'Hepatocellulärem Karzinom': '',
    'Ösophaguskarzinom': '',
    'Pankreaskarzinom': '',
    'Kolonkarzinom': '',
    'Rektumkarzinom': '',
    'Analkarzinom': '',

    # --- Urogenital ---
    'Nierenzellkarzinom': '',
    'Urothelkarzinom der Blase': '',
    'Prostatakarzinom': '',

    # --- Gynäkologie ---
    'Mammakarzinom': '',
    'Endometriumkarzinom': '',
    'Cervixkarzinom': '',
    'Vaginakarzinom': '',
    'Vulvakarzinom': '',

    # --- Andere Erkrankungen ---
    'Fasciitis plantaris': '',
    'Achillodynie': '',
    'Heterotope Ossifikation': '',
    'Endokrine Orbitopathie': '',
    'Epicondylopathia humeri': '',
    'Morbus Dupuytren': '',
    'Morbus Ledderhose': '',
    'Induratio penis plastica': '',
    'Enthesiopathie': '',
    'Periarthropathia humeroscapularis': '',
    'Gonarthrose': '',
    'Arthrose': '',
    'Gynäkomastie': '',
    'Keloid': '',

    #Sekundärneoplasien/ Metastasierung
    'Lymphknotenmetastasen': '', #
    'Hirnmetastasen': 'Grob orientierender neurologischer Untersuchungsbefund, inkl. Hirnnervenstatus, bis auf ______ ohne pathologischen Befund.', #
    'Knochenmetastasen': '', #
    'Lungenmetastasen': 'Körperliche Stigmata im Sinne von Halsvenenstauung, Uhrglasnägeln oder Lippenzyanose sind nicht präsent.', #
    'Lebermetastasen': '', #
    'Weichteilmetastasen': '', #
    'Sonstige Fernmetastasierung': '',
}





#-------------------------------------------------- Functions


def find_matching_entity(user_input_text):
    """
    Versucht, eine bekannte Tumorentität anhand von Keywords im Freitext zu finden.
    Prüft sowohl primäre als auch sekundäre Entitäten aus entity_keywords.

    Args:
        user_input_text (str): Der vom Benutzer eingegebene Freitext für die Tumorentität.

    Returns:
        str: Der Name der gefundenen Entität (Key aus den Dictionaries) oder None,
             wenn keine Übereinstimmung gefunden wurde.
    """
    if not user_input_text:
        return None

    text_lower = user_input_text.lower()

    # Prüfe Keywords in der Reihenfolge des entity_keywords Dictionaries
    for entity_name, keywords in entity_keywords.items():
        for keyword in keywords:
            if keyword in text_lower:
                # Check if the found entity exists in either primary or secondary ICD dicts
                if entity_name in entity_dictionary_icd or entity_name in secondary_neoplasms_icd:
                    print(f"Match found: Keyword '{keyword}' for entity '{entity_name}' in text '{user_input_text}'") # Debugging
                    return entity_name # Ersten validen Treffer zurückgeben
                else:
                    # This case should theoretically not happen if entity_keywords is synced with ICD dicts
                    print(f"Keyword match for '{entity_name}', but not found in ICD dictionaries. Check configuration.") # Debugging
                    continue # Continue searching

    print(f"No match found for text '{user_input_text}'") # Debugging
    return None

def get_icd_code(entity_name):
    """
    Gibt den ICD-10 Code für einen gegebenen Entitätsnamen zurück.
    Berücksichtigt beide Dictionaries (primär und sekundär).

    Args:
        entity_name (str): Der Name der Entität (ein Key aus den Dictionaries).

    Returns:
        str: Der ICD-10 Code oder None, wenn die Entität nicht gefunden wurde.
    """
    if entity_name in entity_dictionary_icd:
        return entity_dictionary_icd[entity_name]
    elif entity_name in secondary_neoplasms_icd:
        return secondary_neoplasms_icd[entity_name]
    else:
        return None
    
def get_uaw():
    return uaw_mapping

def get_status_tumorspezifisch():
    return status_tumorspezifisch_mapping

def manuelle_entity_auswahl():
    """
    Zeigt eine nummerierte Liste der Entitäten aus entity_dictionary_icd an,
    fügt Leerzeilen zwischen logischen Blöcken ein, und lässt den Benutzer
    eine Nummer auswählen, '-' zum Überspringen oder 'f' für Freitext-Eingabe.

    Returns:
        tuple: Ein Tupel (entity_name, icd_code) der Auswahl,
               oder (None, None), wenn übersprungen oder ungültig.
    """
    print("\n--- Manuelle Auswahl der primären Entität / Erkrankung ---")
    auswahl_mapping = {}
    entity_list = list(entity_dictionary_icd.items()) # Nur primäre Entitäten

    # NEU: Liste von Entity-Namen, die den Start eines neuen Blocks markieren
    block_starters = {
        'Glioblastom',  # Start ZNS
        'Karzinom der Lippe', # Start Kopf-Hals
        'Malignes Melanom', # Start Haut
        'Diffus-grosszelligem B-Zell-Lymphom', # Start Lymph/Häma
        'Adenokarzinom der Lunge (NSCLC)', # Start Thorax
        'Cholangiocellulärem Karzinom', # Start Abdomen/GI
        'Nierenzellkarzinom', # Start Uro
        'Mammakarzinom', # Start Gyn
        'Fasciitis plantaris' # Start Andere
    }

    print("Universale:") # Manuelle Überschrift für den ersten Block
    for i, (entity_name, icd) in enumerate(entity_list, start=1):
        # NEU: Prüfen, ob eine Leerzeile eingefügt werden soll
        # Füge Leerzeile *vor* dem Eintrag ein, wenn es ein Block-Starter ist (und nicht der allererste)
        if i > 1 and entity_name in block_starters:
            print("\n") # Eine Leerzeile für die Trennung

        print(f"[{i:3}] {entity_name} ({icd})")
        auswahl_mapping[i] = (entity_name, icd)

    # NEU: Option für Freitext anzeigen
    print("\n" + "-"*30) # Trennlinie
    print("[ f ] für Freitext-Eingabe (falls Entität nicht gelistet)")
    print("-" * 30)

    while True:
        try:
             # Prüfen, ob die Eingabe interaktiv ist
             # if not sys.stdin.isatty():
             #      print("Keine interaktive Eingabe möglich. Breche ab.")
             #      return None, None # Oder eine Exception werfen

             auswahl = input("Ihre Auswahl: ").strip()

             if auswahl.lower() == 'f':
                 print("\n--- Freitext-Eingabe ---")
                 freitext_entity = ""
                 while not freitext_entity: # Schleife bis eine Eingabe erfolgt
                     freitext_entity = input("Entitätsangabe (z.B: Schwannom, Chorionkarzinom, etc.) ").strip()
                     if not freitext_entity:
                         print("Eingabe für Entitätsnamen darf nicht leer sein.")

                 freitext_icd = ""
                 while not freitext_icd: # Schleife bis eine Eingabe erfolgt
                     freitext_icd = input("Bitte zugehörigen ICD-10 Code eingeben: ").strip().upper() # Direkt in Großbuchstaben für Konsistenz
                     if not freitext_icd:
                         print("Eingabe für ICD-Code darf nicht leer sein.")

                 print(f"Freitext erfasst: Entität='{freitext_entity}', ICD='{freitext_icd}'")
                 return freitext_entity, freitext_icd

             # Bisherige Logik für Zahlenauswahl
             elif auswahl.isdigit():
                 index = int(auswahl)
                 if index in auswahl_mapping:
                     selected_entity, selected_icd = auswahl_mapping[index]
                     print(f"Ausgewählt: '{selected_entity}' (ICD: {selected_icd})")
                     return selected_entity, selected_icd
                 else:
                     print("Ungültige Nummer.")
             else:
                 print("Ungültige Eingabe. Bitte eine Zahl oder 'f' eingeben.")

        except ValueError: # Falls int(auswahl) fehlschlägt
             print("Ungültige Eingabe. Bitte eine Zahl, 'f' oder '-' eingeben.")
        except EOFError: # Falls Eingabe abgebrochen wird (z.B. Strg+D)
             print("\nEingabe abgebrochen.")
             return None, None

# NEUE Funktion für manuelle Auswahl sekundärer Neoplasien
def manuelle_sekundaer_auswahl():
    """
    Zeigt eine nummerierte Liste der Entitäten aus secondary_neoplasms_icd an
    und lässt den Benutzer eine auswählen.

    Returns:
        tuple: Ein Tupel (secondary_entity_name, secondary_icd_code) der Auswahl,
               oder (None, None), wenn übersprungen oder ungültig.
    """
    print("\n--- Manuelle Auswahl der sekundären Neoplasie (Bestrahlungsziel) ---")
    auswahl_mapping = {}
    entity_list = list(secondary_neoplasms_icd.items()) # Nur sekundäre Entitäten

    for i, (entity_name, icd) in enumerate(entity_list, start=1):
        print(f"[{i:3}] {entity_name} ({icd})")
        auswahl_mapping[i] = (entity_name, icd)

    while True:
        auswahl = input("Bitte wählen Sie die Nummer der korrekten sekundären Entität oder '-' zum Überspringen: ").strip()
        if auswahl == '-':
            print("Auswahl übersprungen.")
            return None, None
        if auswahl.isdigit():
            try:
                index = int(auswahl)
                if index in auswahl_mapping:
                    selected_entity, selected_icd = auswahl_mapping[index]
                    print(f"Ausgewählt: '{selected_entity}' (ICD: {selected_icd})")
                    return selected_entity, selected_icd
                else:
                    print("Ungültige Nummer.")
            except ValueError:
                print("Ungültige Eingabe. Bitte eine Zahl oder '-' eingeben.")
        else:
            print("Ungültige Eingabe. Bitte eine Zahl oder '-' eingeben.")