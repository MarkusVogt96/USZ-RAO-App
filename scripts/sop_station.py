import pyautogui
from UNIVERSAL import get_benutzerdaten
import clipboard
import time
from datetime import datetime
 

def sop_station_ausfuehren():
    """Führt das SOP Station Skript einmal aus"""
    # Aktuelles Datum im gewünschten Format holen (z.B. 08.05.2025)
    current_date = datetime.now().strftime("%d.%m.%Y")
     
    # Die Zeichenkette mit dem aktuellen Datum
    benutzer_nachname, benutzer_vorname = get_benutzerdaten()
    print(f"Benutzer Nachname: {benutzer_nachname}, Vorname: {benutzer_vorname}")
    if datetime.now().weekday() == 2:  # Mittwoch hat den Wert 2
        dt = f"Visite vom {current_date} ({benutzer_nachname}, Vlaskou)"
    else:
        dt = f"Visite vom {current_date} ({benutzer_nachname})"

    time.sleep(3)
     

     
    clipboard.copy(dt)
    pyautogui.hotkey('ctrl', 'v')
    pyautogui.hotkey('ctrl', 'tab')

    time.sleep(0.1)
    pyautogui.typewrite('S:')
    pyautogui.hotkey('enter')
    pyautogui.hotkey('ctrl', 'shift', '.')
     
    #Subjektiv
    subjektiv = (
        f"Ihm Ihr"
        )
    clipboard.copy(subjektiv)
    pyautogui.hotkey('ctrl', 'v')
    pyautogui.hotkey('enter')
    pyautogui.hotkey('enter')
    time.sleep(0.1)
     
    #Objektiv
    pyautogui.typewrite('O:')
    pyautogui.hotkey('enter')
    time.sleep(0.1)
    pyautogui.hotkey('ctrl', 'shift', '.')
    pyautogui.typewrite('AZ ')
    pyautogui.hotkey('enter')
    time.sleep(0.1)
    pyautogui.typewrite('VP i.O./')
    pyautogui.hotkey('enter')
    time.sleep(0.1)
    pyautogui.typewrite('Labor: ')
    pyautogui.hotkey('enter')
    pyautogui.hotkey('enter')
    time.sleep(0.1)
     
    #Procedere
    pyautogui.typewrite('P:')
    pyautogui.hotkey('enter')
    time.sleep(0.1)
    pyautogui.hotkey('ctrl', 'shift', '.')


def main():
    """Hauptfunktion mit Wiederholungsschleife"""
    while True:
        try:
            print("Führe SOP Station Skript aus...")
            sop_station_ausfuehren()
            print("SOP Station Skript erfolgreich ausgeführt.")
            
            # Frage nach Wiederholung
            while True:
                antwort = input("\nMöchten Sie das Skript für den nächsten Patienten nochmals ausführen? (j/n): ").strip().lower()
                if antwort == 'j':
                    print("Starte Skript erneut...")
                    break
                elif antwort == 'n':
                    print("Skript beendet.")
                    return
                else:
                    print("Ungültige Eingabe. Bitte 'j' für Ja oder 'n' für Nein eingeben.")
                    
        except KeyboardInterrupt:
            print("\nSkript durch Benutzer abgebrochen.")
            return
        except Exception as e:
            print(f"Fehler beim Ausführen des Skripts: {e}")
            antwort = input("Möchten Sie es erneut versuchen? (j/n): ").strip().lower()
            if antwort != 'j':
                return


if __name__ == "__main__":
    main()
