import os
import UNIVERSAL
import clipboard

def an():
    user_home = os.path.expanduser("~")
    print(user_home)
    za = clipboard.paste()

    if user_home.endswith("votma"):
        an = UNIVERSAL.gem_fl_an(za)
    else:
        an = ""

    clipboard.copy(an)
    print("copied to clipboard.")

an()