import pyautogui
from UNIVERSAL import get_benutzerdaten
import clipboard
import time
from datetime import datetime
 

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
