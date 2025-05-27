import pygetwindow as gw
titles = gw.getAllTitles()
for t in titles:
    if "KISIM" in t.upper(): # Temporär noch die alte Bedingung zum Finden
        print(f"Potenzieller KISIM Titel: '{t}'")