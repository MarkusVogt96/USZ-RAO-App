import os
import UNIVERSAL
import clipboard

def dg():
    user_home = os.path.expanduser("~")
    print(user_home)
    za = clipboard.paste()

    if user_home.endswith("votma"):
        ver = UNIVERSAL.gem_fl_dg(za)
    else:
        ver = "[BISHERIGER VERLAUF]"
    clipboard.copy(ver)
    print("done")


dg()