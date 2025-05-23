# data/tumorboard_config.py
import os

# Basispfad für Tumorboard-Daten im Benutzerverzeichnis
USER_TUMORBOARDS_DIR = os.path.join(os.path.expanduser("~"), "tumorboards")

# Definition der Tumorboard-Termine und -Informationen
# day_numeric: 0 = Montag, 1 = Dienstag, ..., 6 = Sonntag
TUMORBOARD_SCHEDULE = [
    {
        'id': 'neuro', 'name': 'Neuro-Onkologie', 'day_german': 'Mo', 'day_numeric': 0,
        'time_start': '08:30', 'time_end': '09:30', 'display_time': '08.30-09.30 Uhr',
        'location_key': 'neuro_loc', 'folder_name': 'Neuro-Onkologie',
        'responsible': 'NA', 'deputy': 'MB/MM', 'notes': ''
    },
    {
        'id': 'thorax', 'name': 'Thorax-Onkologie', 'day_german': 'Mo', 'day_numeric': 0,
        'time_start': '13:30', 'time_end': '14:30', 'display_time': '13.30-14.30 Uhr',
        'location_key': 'thorax_loc', 'folder_name': 'Thorax',
        'responsible': 'NA/MG', 'deputy': 'VdG', 'notes': ''
    },
    {
        'id': 'git', 'name': 'Gastroentero (GIT)', 'day_german': 'Mo', 'day_numeric': 0,
        'time_start': '16:00', 'time_end': '17:00', 'display_time': '16.00-17.00 Uhr',
        'location_key': 'git_loc', 'folder_name': 'GIT',
        'responsible': 'CL', 'deputy': 'EV', 'notes': ''
    },
    {
        'id': 'hyperthermie', 'name': 'Hyperthermie', 'day_german': 'Mo', 'day_numeric': 0,
        'time_start': '16:30', 'time_end': '17:00', 'display_time': '16.30-17.00 Uhr',
        'location_key': 'hyperthermie_loc', 'folder_name': 'Hyperthermie',
        'responsible': 'CL', 'deputy': 'NA', 'notes': ''
    },
    {
        'id': 'zkgs', 'name': 'ZKGS', 'day_german': 'Mo', 'day_numeric': 0,
        'time_start': '15:30', 'time_end': '16:00', 'display_time': '15.30-16.00 Uhr',
        'location_key': 'zkgs_loc', 'folder_name': 'ZKGS',
        'responsible': 'MB', 'deputy': 'Keine Vertretung', 'notes': '3. Montag im Monat'
    },
    {
        'id': 'net', 'name': 'NET Board', 'day_german': 'Mo', 'day_numeric': 0,
        'time_start': '17:30', 'time_end': '18:30', 'display_time': '17.30-18.30 Uhr',
        'location_key': 'net_loc', 'folder_name': 'NET',
        'responsible': 'CL', 'deputy': 'Keine Vertretung', 'notes': 'Alle 2 Wochen'
    },
    {
        'id': 'melanoma', 'name': 'Melanoma (Derma)', 'day_german': 'Di', 'day_numeric': 1,
        'time_start': '08:00', 'time_end': '09:00', 'display_time': '08.00-09.00 Uhr',
        'location_key': 'melanoma_loc', 'folder_name': 'Melanome', # Foldername angepasst
        'responsible': 'PB', 'deputy': 'CL', 'notes': ''
    },
    {
        'id': 'schaedelbasis', 'name': 'Schädelbasis', 'day_german': 'Di', 'day_numeric': 1,
        'time_start': '08:00', 'time_end': '08:30', 'display_time': '08.00-08.30 Uhr',
        'location_key': 'schaedelbasis_loc', 'folder_name': 'Schädelbasis',
        'responsible': 'MB', 'deputy': 'MM', 'notes': '(Wo.1+3)'
    },
    {
        'id': 'gyn', 'name': 'Gyn', 'day_german': 'Di', 'day_numeric': 1,
        'time_start': '15:00', 'time_end': '16:30', 'display_time': '15.00-16.30 Uhr',
        'location_key': 'gyn_loc', 'folder_name': 'Gyn',
        'responsible': 'CL/PP', 'deputy': 'CL/PP', 'notes': ''
    },
    {
        'id': 'uro', 'name': 'Uro', 'day_german': 'Di', 'day_numeric': 1,
        'time_start': '16:30', 'time_end': '17:30', 'display_time': '16.30-17.30 Uhr',
        'location_key': 'uro_loc', 'folder_name': 'Uro',
        'responsible': 'MM/MG', 'deputy': 'EV, LM, EK ab 1.1.23', 'notes': ''
    },
    {
        'id': 'paragangliom', 'name': 'Paragangliomboard', 'day_german': 'Di', 'day_numeric': 1,
        'time_start': '16:30', 'time_end': '17:00', 'display_time': '16.30-17.00 Uhr',
        'location_key': 'paragangliom_loc', 'folder_name': 'Paragangliome', # Foldername angepasst
        'responsible': 'PB', 'deputy': 'MB', 'notes': '2. Dienstag im Monat'
    },
    {
        'id': 'paediatrie', 'name': 'Pädiatrie', 'day_german': 'Di', 'day_numeric': 1,
        'time_start': '17:30', 'time_end': '18:30', 'display_time': '17.30-18.30 Uhr',
        'location_key': 'paediatrie_loc', 'folder_name': 'Pädiatrie',
        'responsible': 'CL', 'deputy': 'MB', 'notes': ''
    },
    {
        'id': 'hypophyse', 'name': 'Hypophyse', 'day_german': 'Di', 'day_numeric': 1,
        'time_start': '17:15', 'time_end': '18:00', 'display_time': '17.15-18.00 Uhr',
        'location_key': 'hypophyse_loc', 'folder_name': 'Hypophyse', # Eigener Ordner erstellt
        'responsible': 'MB', 'deputy': 'keine Vertretung', 'notes': '(1. Di/Mt)'
    },
    {
        'id': 'kht_orl', 'name': 'KHT (ORL)', 'day_german': 'Mi', 'day_numeric': 2,
        'time_start': '08:00', 'time_end': '09:30', 'display_time': '08.00-09.30 Uhr',
        'location_key': 'kht_orl_loc', 'folder_name': 'ORL', # Foldername angepasst
        'responsible': 'PB', 'deputy': 'EV/VdG/LM', 'notes': ''
    },
    {
        'id': 'vascular', 'name': 'Vascular TB', 'day_german': 'Mi', 'day_numeric': 2,
        'time_start': '08:00', 'time_end': '09:30', 'display_time': '08.00-09.30 Uhr',
        'location_key': 'vascular_loc', 'folder_name': 'Vascular',
        'responsible': 'MB', 'deputy': 'keine Vertretung', 'notes': ''
    },
    {
        'id': 'haemato_lymphom', 'name': 'Hämato-Onkologie/Lymphome', 'day_german': 'Mi', 'day_numeric': 2,
        'time_start': '17:00', 'time_end': '18:00', 'display_time': '17.00-18.00 Uhr',
        'location_key': 'haemato_lymphom_loc', 'folder_name': 'Hämato-Onkologie-Lymphome', # Foldername angepasst
        'responsible': 'LM', 'deputy': 'VdG', 'notes': ''
    },
    {
        'id': 'hepatogastro_hpb', 'name': 'Hepatogastro (HPB)', 'day_german': 'Do', 'day_numeric': 3,
        'time_start': '07:30', 'time_end': '08:30', 'display_time': '07.30-08.30 Uhr',
        'location_key': 'hepatogastro_hpb_loc', 'folder_name': 'HPB', # Foldername angepasst
        'responsible': 'NA', 'deputy': 'PB, CL, (EV)', 'notes': ''
    },
    {
        'id': 'proton', 'name': 'Protonentherapie', 'day_german': 'Do', 'day_numeric': 3,
        'time_start': '13:00', 'time_end': '14:00', 'display_time': '13.00-14.00 Uhr',
        'location_key': 'proton_loc', 'folder_name': 'Protonentherapie',
        'responsible': 'CL', 'deputy': 'MB', 'notes': ''
    },
    {
        'id': 'sarkom', 'name': 'Sarkom', 'day_german': 'Do', 'day_numeric': 3,
        'time_start': '15:30', 'time_end': '17:00', 'display_time': '15.30-17.00 Uhr',
        'location_key': 'sarkom_loc', 'folder_name': 'Sarkom',
        'responsible': 'MB', 'deputy': 'CL', 'notes': ''
    },
    {
        'id': 'transplant', 'name': 'Transplantationsboard', 'day_german': 'Do', 'day_numeric': 3,
        'time_start': '16:30', 'time_end': '17:00', 'display_time': '16.30-17.00 Uhr',
        'location_key': 'transplant_loc', 'folder_name': 'Transplantationsboard',
        'responsible': '', 'deputy': 'Nur auf Zuruf bei Majo Pat', 'notes': ''
    },
    {
        'id': 'schilddruese', 'name': 'Schilddrüse', 'day_german': 'Fr', 'day_numeric': 4,
        'time_start': '12:15', 'time_end': '13:00', 'display_time': '12.15-13.00 Uhr',
        'location_key': 'schilddruese_loc', 'folder_name': 'Schilddrüse',
        'responsible': 'VdG', 'deputy': 'LM', 'notes': ''
    },
    # Zusätzliche Boards aus der Liste, die nicht im Screenshot sind, falls erforderlich
    {
        'id': 'gas_chi_onk', 'name': 'GAS-CHI-ONK', 'day_german': 'N.A.', 'day_numeric': 99, # Tag und Zeit unbekannt
        'time_start': '00:00', 'time_end': '00:00', 'display_time': 'N.A.',
        'location_key': 'gas_chi_onk_loc', 'folder_name': 'GAS-CHI-ONK',
        'responsible': 'N.A.', 'deputy': 'N.A.', 'notes': 'Infos fehlen'
    },
    {
        'id': 'hcc', 'name': 'HCC', 'day_german': 'N.A.', 'day_numeric': 99,
        'time_start': '00:00', 'time_end': '00:00', 'display_time': 'N.A.',
        'location_key': 'hcc_loc', 'folder_name': 'HCC',
        'responsible': 'N.A.', 'deputy': 'N.A.', 'notes': 'Infos fehlen'
    },
    {
        'id': 'llmz', 'name': 'LLMZ', 'day_german': 'N.A.', 'day_numeric': 99,
        'time_start': '00:00', 'time_end': '00:00', 'display_time': 'N.A.',
        'location_key': 'llmz_loc', 'folder_name': 'LLMZ',
        'responsible': 'N.A.', 'deputy': 'N.A.', 'notes': 'Infos fehlen'
    },
    #... ggf. weitere Boards aus der Textliste hier hinzufügen, wenn sie einen Ordner haben
]

# Placeholder für Orte
TUMORBOARD_LOCATIONS = {
    'neuro_loc': 'N.N.',
    'thorax_loc': 'N.N.',
    'git_loc': 'N.N.',
    'hyperthermie_loc': 'N.N.',
    'zkgs_loc': 'N.N.',
    'net_loc': 'N.N.',
    'melanoma_loc': 'N.N.',
    'schaedelbasis_loc': 'N.N.',
    'gyn_loc': 'N.N.',
    'uro_loc': 'N.N.',
    'paragangliom_loc': 'N.N.',
    'paediatrie_loc': 'N.N.',
    'hypophyse_loc': 'N.N.',
    'kht_orl_loc': 'N.N.',
    'vascular_loc': 'N.N.',
    'haemato_lymphom_loc': 'N.N.',
    'hepatogastro_hpb_loc': 'N.N.',
    'proton_loc': 'N.N.',
    'sarkom_loc': 'N.N.',
    'transplant_loc': 'N.N.',
    'schilddruese_loc': 'N.N.',
    'gas_chi_onk_loc': 'N.N.',
    'hcc_loc': 'N.N.',
    'llmz_loc': 'N.N.',
    # ... weitere location_keys für alle Boards ...
}

# Liste aller Tumorboard-Namen (für die Ordnererstellung und -prüfung)
# Wird dynamisch aus TUMORBOARD_SCHEDULE generiert für Konsistenz
ALL_TUMORBOARD_FOLDER_NAMES = sorted(list(set([board['folder_name'] for board in TUMORBOARD_SCHEDULE if board.get('folder_name')])))

# Hilfsfunktion zum Erstellen der Ordner, falls sie nicht existieren
def ensure_tumorboard_folders_exist():
    if not os.path.exists(USER_TUMORBOARDS_DIR):
        os.makedirs(USER_TUMORBOARDS_DIR)
        print(f"Hauptverzeichnis für Tumorboards erstellt: {USER_TUMORBOARDS_DIR}")
    for folder_name in ALL_TUMORBOARD_FOLDER_NAMES:
        folder_path = os.path.join(USER_TUMORBOARDS_DIR, folder_name)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            print(f"Tumorboard-Verzeichnis erstellt: {folder_path}")

# Optional: Beim Import des Moduls die Ordner erstellen lassen
ensure_tumorboard_folders_exist()