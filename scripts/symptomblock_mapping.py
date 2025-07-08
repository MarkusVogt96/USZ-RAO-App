"""
Dieses Dictionary mappt Tupel von ICD-10-Code-Präfixen auf die entsprechenden
Dateinamen der Symptomblock-Buttons. Die Logik sucht nach einem Präfix,
das mit dem Anfang des vollständigen ICD-10-Codes des Patienten übereinstimmt.
"""

MAPPING_SYMPTOMBLOCK = {
    # Key: Tupel von ICD-Präfixen (als Strings)
    # Value: Dateiname des Button-Bildes (als String)

    ("C71", "D32", "D33", "D35", "Q28", "H06", "C79.3"): "button_symptomblock_brain.png",
    
    ("C00", "C01", "C02", "C03", "C04", "C05", "C06", "C07", 
     "C08", "C09", "C10", "C11", "C30"): "button_symptomblock_orl.png",
     
    ("C15", "C18", "C22", "C24", "C25", "C64", "C78.7"): "button_symptomblock_abdomen.png",
    
    ("C34", "C45", "C78.0"): "button_symptomblock_thorax.png",
    ("C61",): "button_symptomblock_pelvismale.png",

    # Spezialfall: Blasenkarzinom als Entität im Becken, die Männer und Frauen haben können
    ("C67", "C20", "C21"): {
        "M": "button_symptomblock_pelvismale.png",
        "W": "button_symptomblock_pelvisfemale.png"
    },
    
    ("C50",): "button_symptomblock_breast.png",
    
    ("C51", "C52", "C53", "C54"): "button_symptomblock_pelvisfemale.png",

    ("M17", "M19", "M61", "M72", "M75", "M76", "M77", "L91", "C79.5"): "button_symptomblock_bone_extremities.png"
}