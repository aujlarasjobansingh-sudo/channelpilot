# 3D Animation Long Form - made by aivxer. Copyright (c) 2026 aivxer.
# Free for your own videos. Do not re-share, sell, or claim this skill as your own (see LICENSE.txt).
import json, sys
import numpy as np, soundfile as sf, sherpa_onnx
M = "/home/claude/models/kokoro-multi-lang-v1_0"
cfg = sherpa_onnx.OfflineTtsConfig(model=sherpa_onnx.OfflineTtsModelConfig(
    kokoro=sherpa_onnx.OfflineTtsKokoroModelConfig(model=f"{M}/model.onnx", voices=f"{M}/voices.bin",
        tokens=f"{M}/tokens.txt", data_dir=f"{M}/espeak-ng-data", dict_dir=f"{M}/dict",
        lexicon=f"/home/claude/vid/lex_extra.txt,{M}/lexicon-us-en.txt,{M}/lexicon-gb-en.txt", lang="en-us"), num_threads=4))
tts = sherpa_onnx.OfflineTts(cfg)
# v1_0 speaker ids: 14 am_fenrir, 16 am_michael, 18 am_puck, 25 bm_fable, 26 bm_george, 27 bm_lewis
NARR, CON, BUYER = 16, 26, 18
lines = [
    ("n1", NARR, 0.95, "Paris. Nineteen twenty-five."),
    ("n2", NARR, 1.0, "A man in a very good suit is selling the Eiffel Tower."),
    ("n3", NARR, 1.0, "Seven thousand tons of iron. Going cheap."),
    ("b1", BUYER, 0.95, "How much?"),
    ("c1", CON, 0.95, "For you, monsieur? A bargain."),
    ("n4", NARR, 0.92, "There's just one problem."),
    ("n5", NARR, 0.95, "It isn't his to sell."),
    ("n6", NARR, 1.0, "His name is Victor Lustig."),
    ("n7", NARR, 0.95, "And he's about to sell it twice."),
]
out = {}
A = "/home/claude/vid/audio3"
import os; os.makedirs(A, exist_ok=True)
for key, sid, speed, text in lines:
    a = tts.generate(text, sid=sid, speed=speed)
    s = np.array(a.samples, dtype=np.float32)
    thr = 0.012 * np.abs(s).max(); idx = np.where(np.abs(s) > thr)[0]
    s = s[max(idx[0] - 300, 0): idx[-1] + 1500]
    sf.write(f"{A}/{key}.wav", s, a.sample_rate)
    out[key] = {"sid": sid, "text": text, "dur": round(len(s) / a.sample_rate, 3), "sr": a.sample_rate}
    print(key, out[key]["dur"], text, flush=True)
json.dump(out, open(f"{A}/lines.json", "w"), indent=1)
print("total", round(sum(v["dur"] for v in out.values()), 2))
