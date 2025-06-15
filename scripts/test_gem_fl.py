import os
import UNIVERSAL
import clipboard

def dg():
    user_home = os.path.expanduser("~")
    print(user_home)
    za = clipboard.paste()

    if user_home.endswith("marku"):
        ver = UNIVERSAL.gem_fl_dg(za)
    else:
        ver = "[BISHERIGER VERLAUF]"

    print(ver)


def an():
    user_home = os.path.expanduser("~")
    print(user_home)
    za = clipboard.paste()

    if user_home.endswith("marku"):
        an = UNIVERSAL.gem_fl_an(za)
    else:
        an = ""

    print(an)

an()