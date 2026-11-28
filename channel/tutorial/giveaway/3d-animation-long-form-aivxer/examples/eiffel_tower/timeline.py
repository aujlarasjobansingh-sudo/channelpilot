# 3D Animation Long Form - made by aivxer. Copyright (c) 2026 aivxer.
# Free for your own videos. Do not re-share, sell, or claim this skill as your own (see LICENSE.txt).
import json
A3 = "/home/claude/vid/audio3"
LINES = json.load(open(f"{A3}/lines.json"))
CUE = {"n1": 0.35, "n2": 2.55, "n3": 5.95, "b1": 9.25, "c1": 10.28, "n4": 12.50, "n5": 14.32, "n6": 16.12, "n7": 18.05}
END = 21.0
SHOT_T = {"paris": (0.0, 2.40), "office": (2.40, 5.80), "table": (5.80, 9.10), "buyer": (9.10, 10.15),
          "lustig": (10.15, 12.30), "card": (12.30, 14.15), "tower": (14.15, 15.95), "hero": (15.95, END)}
FLASH = 19.90
if __name__ == "__main__":
    for k, t in CUE.items(): print(k, t, round(t + LINES[k]["dur"], 2))
