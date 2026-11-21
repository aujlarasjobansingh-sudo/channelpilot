"""prep_voice.py <voiceover file>
Makes in $TUT_ROOT: vo/vo48.wav (mix source), vo/vo16.wav, assets/voenv.npy (loudness per video frame),
vo/transcript.txt (one line per phrase with start-end seconds) and vo/words.json (word start times).
Read transcript.txt to plan scenes: cut scenes inside the silences between phrases."""
import sys, os, json, subprocess, numpy as np, soundfile as sf
sys.path.insert(0, os.path.dirname(__file__))
from models import asr_engine, ensure
ROOT = os.environ.get("TUT_ROOT", os.getcwd())
src = sys.argv[1]
os.makedirs(f"{ROOT}/vo", exist_ok=True); os.makedirs(f"{ROOT}/assets", exist_ok=True)
subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", src, "-ar", "48000", "-ac", "2", f"{ROOT}/vo/vo48.wav"], check=True)
subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", src, "-ar", "16000", "-ac", "1", f"{ROOT}/vo/vo16.wav"], check=True)
s48, sr = sf.read(f"{ROOT}/vo/vo48.wav", dtype="float32"); m = s48.mean(1)
hop = sr // 30; n = len(m) // hop
env = np.array([np.sqrt(np.mean(m[i * hop:(i + 1) * hop] ** 2)) for i in range(n)])
np.save(f"{ROOT}/assets/voenv.npy", np.clip(env / (np.percentile(env, 98) + 1e-9), 0, 1.2))
import sherpa_onnx
s, sr = sf.read(f"{ROOT}/vo/vo16.wav", dtype="float32")
vc = sherpa_onnx.VadModelConfig(); vc.silero_vad.model = ensure("silero_vad.onnx")
vc.silero_vad.min_silence_duration = 0.25; vc.silero_vad.max_speech_duration = 20; vc.sample_rate = 16000
vad = sherpa_onnx.VoiceActivityDetector(vc, buffer_size_in_seconds=int(len(s) / 16000) + 60)
segs = []
for i in range(0, len(s), 512):
    vad.accept_waveform(s[i:i + 512])
    while not vad.empty(): segs.append((vad.front.start, vad.front.samples)); vad.pop()
vad.flush()
while not vad.empty(): segs.append((vad.front.start, vad.front.samples)); vad.pop()
rec = asr_engine(); out = []; words = []
for st, sm in segs:
    t0 = st / 16000; x = rec.create_stream(); x.accept_waveform(16000, np.array(sm)); rec.decode_stream(x); r = x.result
    out.append(f"{t0:8.2f}-{t0 + len(sm) / 16000:8.2f}  {r.text}")
    for tok, tt in zip(r.tokens, r.timestamps):
        if tok.startswith(" ") or not words or words[-1][2] != len(out): words.append([tok.strip(), round(t0 + tt, 3), len(out)])
        else: words[-1][0] += tok
open(f"{ROOT}/vo/transcript.txt", "w").write("\n".join(out))
json.dump([w[:2] for w in words], open(f"{ROOT}/vo/words.json", "w"))
print("\n".join(out)); print(f"\n{len(s) / 16000:.2f} s, {len(words)} words")
