#!/usr/bin/env python3
"""
WHO ICD-10 Mapping for Neoplasms
Complete mapping for C00-C97 (Malignant neoplasms) and D00-D48 (Other neoplasms)
"""

# WHO ICD-10 Neoplasm Mapping Dictionary
ICD10_NEOPLASM_MAPPING = {
    # C00-C14: Malignant neoplasms of lip, oral cavity and pharynx
    "C00": "Bösartige Neubildung der Lippe",
    "C01": "Bösartige Neubildung des Zungengrundes",
    "C02": "Bösartige Neubildung sonstiger und nicht näher bezeichneter Teile der Zunge",
    "C03": "Bösartige Neubildung des Zahnfleisches",
    "C04": "Bösartige Neubildung des Mundbodens",
    "C05": "Bösartige Neubildung des Gaumens",
    "C06": "Bösartige Neubildung sonstiger und nicht näher bezeichneter Teile des Mundes",
    "C07": "Bösartige Neubildung der Parotis",
    "C08": "Bösartige Neubildung sonstiger und nicht näher bezeichneter großer Speicheldrüsen",
    "C09": "Bösartige Neubildung der Tonsille",
    "C10": "Bösartige Neubildung des Oropharynx",
    "C11": "Bösartige Neubildung des Nasopharynx",
    "C12": "Bösartige Neubildung des Recessus piriformis",
    "C13": "Bösartige Neubildung des Hypopharynx",
    "C14": "Bösartige Neubildung sonstiger und ungenau bezeichneter Lokalisationen der Lippe, der Mundhöhle und des Pharynx",
    
    # C15-C26: Malignant neoplasms of digestive organs
    "C15": "Bösartige Neubildung des Ösophagus",
    "C16": "Bösartige Neubildung des Magens",
    "C17": "Bösartige Neubildung des Dünndarms",
    "C18": "Bösartige Neubildung des Kolons",
    "C19": "Bösartige Neubildung am Rektosigmoid-Übergang",
    "C20": "Bösartige Neubildung des Rektums",
    "C21": "Bösartige Neubildung des Anus und des Analkanals",
    "C22": "Bösartige Neubildung der Leber und der intrahepatischen Gallengänge",
    "C23": "Bösartige Neubildung der Gallenblase",
    "C24": "Bösartige Neubildung sonstiger und nicht näher bezeichneter Teile der Gallenwege",
    "C25": "Bösartige Neubildung des Pankreas",
    "C26": "Bösartige Neubildung sonstiger und ungenau bezeichneter Verdauungsorgane",
    
    # C30-C39: Malignant neoplasms of respiratory and intrathoracic organs
    "C30": "Bösartige Neubildung der Nasenhöhle und des Mittelohrs",
    "C31": "Bösartige Neubildung der Nasennebenhöhlen",
    "C32": "Bösartige Neubildung des Larynx",
    "C33": "Bösartige Neubildung der Trachea",
    "C34": "Bösartige Neubildung der Bronchien und der Lunge",
    "C37": "Bösartige Neubildung des Thymus",
    "C38": "Bösartige Neubildung des Herzens, des Mediastinums und der Pleura",
    "C39": "Bösartige Neubildung sonstiger und ungenau bezeichneter Lokalisationen des Atmungssystems",
    
    # C40-C41: Malignant neoplasms of bone and articular cartilage
    "C40": "Bösartige Neubildung des Knochens und des Gelenkknorpels der Extremitäten",
    "C41": "Bösartige Neubildung des Knochens und des Gelenkknorpels sonstiger und nicht näher bezeichneter Lokalisationen",
    
    # C43-C44: Melanoma and other malignant neoplasms of skin
    "C43": "Bösartiges Melanom der Haut",
    "C44": "Sonstige bösartige Neubildungen der Haut",
    
    # C45-C49: Malignant neoplasms of mesothelial and soft tissue
    "C45": "Mesotheliom",
    "C46": "Kaposi-Sarkom",
    "C47": "Bösartige Neubildung der peripheren Nerven und des autonomen Nervensystems",
    "C48": "Bösartige Neubildung des Retroperitoneums und des Peritoneums",
    "C49": "Bösartige Neubildung sonstiger Bindegewebe- und Weichgewebearten",
    
    # C50: Malignant neoplasm of breast
    "C50": "Bösartige Neubildung der Brustdrüse",
    
    # C51-C58: Malignant neoplasms of female genital organs
    "C51": "Bösartige Neubildung der Vulva",
    "C52": "Bösartige Neubildung der Vagina",
    "C53": "Bösartige Neubildung der Cervix uteri",
    "C54": "Bösartige Neubildung des Corpus uteri",
    "C55": "Bösartige Neubildung des Uterus, Teil nicht näher bezeichnet",
    "C56": "Bösartige Neubildung des Ovars",
    "C57": "Bösartige Neubildung sonstiger und nicht näher bezeichneter weiblicher Genitalorgane",
    "C58": "Bösartige Neubildung der Plazenta",
    
    # C60-C63: Malignant neoplasms of male genital organs
    "C60": "Bösartige Neubildung des Penis",
    "C61": "Bösartige Neubildung der Prostata",
    "C62": "Bösartige Neubildung des Hodens",
    "C63": "Bösartige Neubildung sonstiger und nicht näher bezeichneter männlicher Genitalorgane",
    
    # C64-C68: Malignant neoplasms of urinary tract
    "C64": "Bösartige Neubildung der Niere, ausgenommen Nierenbecken",
    "C65": "Bösartige Neubildung des Nierenbeckens",
    "C66": "Bösartige Neubildung des Ureters",
    "C67": "Bösartige Neubildung der Harnblase",
    "C68": "Bösartige Neubildung sonstiger und nicht näher bezeichneter Harnorgane",
    
    # C69-C72: Malignant neoplasms of eye, brain and other parts of central nervous system
    "C69": "Bösartige Neubildung des Auges und der Augenanhangsgebilde",
    "C70": "Bösartige Neubildung der Meningen",
    "C71": "Bösartige Neubildung des Gehirns",
    "C72": "Bösartige Neubildung des Rückenmarks, der Hirnnerven und sonstiger Teile des Zentralnervensystems",
    
    # C73-C75: Malignant neoplasms of thyroid and other endocrine glands
    "C73": "Bösartige Neubildung der Schilddrüse",
    "C74": "Bösartige Neubildung der Nebenniere",
    "C75": "Bösartige Neubildung sonstiger endokriner Drüsen und verwandter Strukturen",
    
    # C76-C80: Malignant neoplasms of ill-defined, other secondary and unspecified sites
    "C76": "Bösartige Neubildung sonstiger und ungenau bezeichneter Lokalisationen",
    "C77": "Sekundäre und nicht näher bezeichnete bösartige Neubildung der Lymphknoten",
    "C78": "Sekundäre bösartige Neubildung der Atmungs- und Verdauungsorgane",
    "C79": "Sekundäre bösartige Neubildung sonstiger und nicht näher bezeichneter Lokalisationen",
    "C80": "Bösartige Neubildung ohne Angabe der Lokalisation",
    
    # C81-C96: Malignant neoplasms of lymphoid, haematopoietic and related tissue
    "C81": "Hodgkin-Lymphom",
    "C82": "Follikuläres Lymphom",
    "C83": "Nicht-follikuläres Lymphom",
    "C84": "Reifzellige T/NK-Zell-Lymphome",
    "C85": "Sonstige und nicht näher bezeichnete Typen des Non-Hodgkin-Lymphoms",
    "C86": "Sonstige spezifizierte T/NK-Zell-Lymphome",
    "C88": "Bösartige immunproliferative Krankheiten",
    "C90": "Plasmozytom und bösartige Plasmazellen-Neubildungen",
    "C91": "Lymphatische Leukämie",
    "C92": "Myeloische Leukämie",
    "C93": "Monozytenleukämie",
    "C94": "Sonstige Leukämien näher bezeichneten Zelltyps",
    "C95": "Leukämie nicht näher bezeichneten Zelltyps",
    "C96": "Sonstige und nicht näher bezeichnete bösartige Neubildungen des lymphatischen, blutbildenden und verwandten Gewebes",
    
    # C97: Malignant neoplasms of independent (primary) multiple sites
    "C97": "Bösartige Neubildungen als Primärtumoren an mehreren Lokalisationen",
    
    # D00-D09: In situ neoplasms
    "D00": "Carcinoma in situ der Mundhöhle, des Ösophagus und des Magens",
    "D01": "Carcinoma in situ sonstiger und nicht näher bezeichneter Verdauungsorgane",
    "D02": "Carcinoma in situ des Mittelohrs und des Atmungssystems",
    "D03": "Melanoma in situ",
    "D04": "Carcinoma in situ der Haut",
    "D05": "Carcinoma in situ der Brustdrüse",
    "D06": "Carcinoma in situ der Cervix uteri",
    "D07": "Carcinoma in situ sonstiger und nicht näher bezeichneter Genitalorgane",
    "D09": "Carcinoma in situ sonstiger und nicht näher bezeichneter Lokalisationen",
    
    # D10-D36: Benign neoplasms
    "D10": "Gutartige Neubildung der Mundhöhle und des Pharynx",
    "D11": "Gutartige Neubildung der großen Speicheldrüsen",
    "D12": "Gutartige Neubildung des Kolons, des Rektums, des Analkanals und des Anus",
    "D13": "Gutartige Neubildung sonstiger und ungenau bezeichneter Teile des Verdauungssystems",
    "D14": "Gutartige Neubildung des Mittelohrs und des Atmungssystems",
    "D15": "Gutartige Neubildung sonstiger und nicht näher bezeichneter intrathorakaler Organe",
    "D16": "Gutartige Neubildung des Knochens und des Gelenkknorpels",
    "D17": "Gutartige Lipomatöse Neubildung",
    "D18": "Hämangiom und Lymphangiom jeder Lokalisation",
    "D19": "Gutartige Neubildung des Mesothel-Gewebes",
    "D20": "Gutartige Neubildung des Weichteilgewebes des Retroperitoneums und des Peritoneums",
    "D21": "Sonstige gutartige Neubildungen des Bindegewebes und anderer Weichteilgewebe",
    "D22": "Melanozytennävus",
    "D23": "Sonstige gutartige Neubildungen der Haut",
    "D24": "Gutartige Neubildung der Brustdrüse",
    "D25": "Leiomyom des Uterus",
    "D26": "Sonstige gutartige Neubildungen des Uterus",
    "D27": "Gutartige Neubildung des Ovars",
    "D28": "Gutartige Neubildung sonstiger und nicht näher bezeichneter weiblicher Genitalorgane",
    "D29": "Gutartige Neubildung der männlichen Genitalorgane",
    "D30": "Gutartige Neubildung der Harnorgane",
    "D31": "Gutartige Neubildung des Auges und der Augenanhangsgebilde",
    "D32": "Gutartige Neubildung der Meningen",
    "D33": "Gutartige Neubildung des Gehirns und sonstiger Teile des Zentralnervensystems",
    "D34": "Gutartige Neubildung der Schilddrüse",
    "D35": "Gutartige Neubildung sonstiger und nicht näher bezeichneter endokriner Drüsen",
    "D36": "Gutartige Neubildung sonstiger und nicht näher bezeichneter Lokalisationen",
    
    # D37-D48: Neoplasms of uncertain behavior
    "D37": "Neubildung unsicheren oder unbekannten Verhaltens der Mundhöhle und der Verdauungsorgane",
    "D38": "Neubildung unsicheren oder unbekannten Verhaltens des Mittelohrs und der Atmungs- und intrathorakalen Organe",
    "D39": "Neubildung unsicheren oder unbekannten Verhaltens der weiblichen Genitalorgane",
    "D40": "Neubildung unsicheren oder unbekannten Verhaltens der männlichen Genitalorgane",
    "D41": "Neubildung unsicheren oder unbekannten Verhaltens der Harnorgane",
    "D42": "Neubildung unsicheren oder unbekannten Verhaltens der Meningen",
    "D43": "Neubildung unsicheren oder unbekannten Verhaltens des Gehirns und des Zentralnervensystems",
    "D44": "Neubildung unsicheren oder unbekannten Verhaltens der endokrinen Drüsen",
    "D45": "Polycythaemia vera",
    "D46": "Myelodysplastische Syndrome",
    "D47": "Sonstige Neubildungen unsicheren oder unbekannten Verhaltens des lymphatischen, blutbildenden und verwandten Gewebes",
    "D48": "Neubildung unsicheren oder unbekannten Verhaltens sonstiger und nicht näher bezeichneter Lokalisationen"
}

def get_icd_family_description(icd_family):
    """
    Get WHO description for ICD family code
    
    Args:
        icd_family (str): ICD family code like 'C49', 'D17', etc.
    
    Returns:
        str: WHO description or 'Unbekannt' if not found
    """
    if not icd_family:
        return "Unbekannt"
    
    # Clean the family code (remove any extra characters)
    clean_family = icd_family.strip().upper()
    
    return ICD10_NEOPLASM_MAPPING.get(clean_family, f"Unbekannt ({clean_family})")

def get_all_neoplasm_families():
    """
    Get all available ICD neoplasm family codes
    
    Returns:
        list: Sorted list of ICD family codes
    """
    return sorted(ICD10_NEOPLASM_MAPPING.keys())

def is_neoplasm_code(icd_code):
    """
    Check if an ICD code is a neoplasm (C or D category)
    
    Args:
        icd_code (str): Full ICD code like 'C49.2'
    
    Returns:
        bool: True if it's a neoplasm code
    """
    if not icd_code:
        return False
    
    clean_code = icd_code.strip().upper()
    return clean_code.startswith('C') or clean_code.startswith('D')

# Export the mapping for external use
__all__ = ['ICD10_NEOPLASM_MAPPING', 'get_icd_family_description', 'get_all_neoplasm_families', 'is_neoplasm_code'] 