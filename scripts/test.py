import UNIVERSAL

local_path_bereich_berichte = fr"C:\Users\votma\USZ-RAO-App_v2.1\scripts\screenshots pyautogui\UNIVERSAL\bereich_berichte"


if not UNIVERSAL.find_button(image_name="button_ziel.png", base_path=local_path_bereich_berichte, max_attempts=5):
    print("button_ziel.png nicht gefunden, mache page down")
else:
    print("button gefunden")