import UNIVERSAL
import clipboard

dg_liste = clipboard.paste()

# GEÄNDERT: Der Funktionsaufruf wurde an den neuen Namen in UNIVERSAL.py angepasst.
dg_liste_zusammenfassung = UNIVERSAL.llama_diagnosenliste_zusammenfassung(dg_liste)

clipboard.copy(dg_liste_zusammenfassung)