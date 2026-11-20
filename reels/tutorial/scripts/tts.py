"""tts.py lines.json out_prefix [voice]
lines.json: [{"key": "hook", "text": "...", "gap": 0.3}, ...]  -> out_prefix.wav (48k stereo) + out_prefix_lines.json with start/end.
Use when the creator has no recording yet (reels, samples). Voice default 'michael'."""
import sys, os, json, numpy as np, soundfile as sf, subprocess
sys.path.insert(0, os.path.dirname(__file__))
from models import tts_engine, VOICES
L = json.load(open(sys.argv[1])); pre = sys.argv[2]; sid = VOICES.get(sys.argv[3] if len(sys.argv) > 3 else "michael", 16)
speed = float(os.environ.get("TTS_SPEED", "1.08"))
lex = os.environ.get("TTS_LEXICON")  # optional file: "word  phonemes..." lines for names the dictionary skips
tts = tts_engine(extra_lexicon=lex)
sr = 24000; out = [np.zeros(int(.2 * sr), np.float32)]; t = .2
for ln in L:
    a = tts.generate(ln["text"], sid=sid, speed=speed); x = np.array(a.samples, np.float32); sr = a.sample_rate
    ln["start"] = round(t, 3); ln["end"] = round(t + len(x) / sr, 3)
    g = ln.get("gap", .3); out += [x, np.zeros(int(g * sr), np.float32)]; t += len(x) / sr + g
y = np.concatenate(out + [np.zeros(int(1.0 * sr), np.float32)]); y = y / np.abs(y).max() * .9
sf.write(pre + "_24k.wav", y, sr)
subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", pre + "_24k.wav", "-ar", "48000", "-ac", "2", pre + ".wav"], check=True)
json.dump(L, open(pre + "_lines.json", "w"), indent=1)
for ln in L: print(f'{ln["key"]:8s} {ln["start"]:6.2f}-{ln["end"]:6.2f}  {ln["text"]}')
print("total", round(len(y) / sr, 2))
