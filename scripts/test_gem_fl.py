import os
import UNIVERSAL
import clipboard

user_home = os.path.expanduser("~")
print(user_home)
zwischenablage = clipboard.paste()

if user_home.endswith("marku"):
    verlauf = UNIVERSAL.gem_fl(zwischenablage)
else:
    verlauf = "[BISHERIGER VERLAUF]"

print(verlauf)





