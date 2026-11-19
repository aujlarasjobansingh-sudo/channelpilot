"""Dialogue for Episode 1 using Piper (offline neural TTS).
Outputs: out/dialogue.wav (48k stereo), out/dialogue.json (line timings, subtitle chunks, mouth envelopes @30fps)
Cast: YOU = ryan-high, MAYA = libritts #558, OFFICER = libritts #186 (swap here to recast).
To replace with recorded voices later: drop files in voices_rec/<id>.wav and they are used instead of TTS.
"""
import os, json, re
import numpy as np
import soundfile as sf
from scipy import signal
from piper import PiperVoice, SynthesisConfig

HERE = os.path.dirname(os.path.abspath(__file__))
MD = os.path.join(HERE, 'voices_models')
SR = 48000
TOTAL = 116.0

VOICES = {
    'you':  dict(model='en-us-ryan-high.onnx', sid=None),
    'maya': dict(model='en-us-libritts-high.onnx', sid=558),
    'cop':  dict(model='en-us-libritts-high.onnx', sid=186),
}
# id, speaker, start, latest end, text, style
LINES = [
    ('l01', 'you', 10.55, 13.6, 'Dead quiet. Just me and the crickets.', 'sigh'),
    ('l02', 'maya', 15.75, 18.5, 'Lock it! Please, hit the lock right now!', 'panic'),
    ('l03', 'you', 18.75, 21.9, "Whoa, hey, slow down! What's going on?", 'alarm'),
    ('l04', 'maya', 22.3, 29.8, 'A guy in a black sedan followed me for three miles. He saw me run in here. Lock the door!', 'panic'),
    ('l05', 'you', 33.2, 37.9, "Okay, it's locked. You're safe. I'm calling nine one one.", 'normal'),
    ('l06', 'you', 39.6, 44.6, "Wait, you're good. A cop just pulled into the lot.", 'relief'),
    ('l07', 'maya', 45.7, 48.9, "No. No, no, no. That's not a real cop.", 'whisper'),
    ('l08', 'you', 49.0, 50.6, "What? He's in a cruiser.", 'alarm'),
    ('l09', 'maya', 50.7, 54.0, "Look at the roof. There's no unit number. He's the one who was chasing me.", 'whisperfast'),
    ('l10', 'cop', 64.4, 70.8, 'Police! Open the door! Is there a girl in a grey hoodie in there?', 'muffled'),
    ('l11', 'maya', 71.1, 77.0, "Don't open it! Look at his belt. He doesn't even have a radio. If you unlock that door, we're both dead.", 'whisperfast'),
    ('l12', 'cop', 76.9, 82.9, "Sir, step away from her right now! She just attacked a clerk at the Shell station two miles up. She's armed!", 'muffledyell'),
    ('l13', 'you', 83.15, 84.0, 'Wait. What?', 'whisper'),
    ('l14', 'you', 84.3, 85.75, "Hey. What's in your pocket?", 'tense'),
    ('l15', 'maya', 85.95, 89.0, "It's just my house keys! Please, don't listen to him!", 'plead'),
    ('l16', 'you', 91.4, 95.6, "Holy crap. She's telling the truth.", 'relief'),
    ('l17', 'cop', 103.3, 106.8, 'Last chance! Unlock the door!', 'muffledyell'),
    ('l18', 'maya', 108.6, 111.6, "Don't touch that button.", 'cold'),
    ('l19', 'you', 112.6, 116.0, 'One of them is lying. Or both of them are.', 'vo'),
]
STYLE = {   # length_scale, gain dB
    'sigh': (1.08, -2), 'panic': (0.86, 0), 'alarm': (0.92, 0), 'normal': (1.0, -1), 'relief': (0.97, -1),
    'whisper': (1.05, -7), 'whisperfast': (0.9, -6), 'muffled': (0.98, -3), 'muffledyell': (0.9, -1),
    'tense': (1.08, -3), 'plead': (0.92, 0), 'cold': (1.25, -3), 'vo': (1.12, -1),
}
_cache = {}
def voice(model):
    if model not in _cache: _cache[model] = PiperVoice.load(os.path.join(MD, model))
    return _cache[model]

def synth(spk, text, ls):
    v = VOICES[spk]; pv = voice(v['model'])
    cfg = SynthesisConfig(speaker_id=v['sid'], length_scale=ls, noise_scale=0.62, noise_w_scale=0.75)
    a = np.concatenate([c.audio_float_array for c in pv.synthesize(text, syn_config=cfg)]).astype(np.float64)
    a = signal.resample_poly(a, SR, pv.config.sample_rate)
    # trim silence
    e = np.abs(a) > 0.02; idx = np.where(e)[0]
    a = a[max(0, idx[0] - 600): idx[-1] + 2400] if len(idx) else a
    return a

def sos(kind, f, order=4): return signal.butter(order, f, btype=kind, fs=SR, output='sos')
def process(a, style):
    rng = np.random.default_rng(len(a))
    if style.startswith('muffled'):
        a = signal.resample_poly(a, 100, 92 if style == 'muffled' else 96)   # deeper (and a little slower)
        a = signal.sosfilt(sos('low', 1700), a); a = signal.sosfilt(sos('high', 160), a)
        rv = np.zeros(int(SR * 0.6)); taps = rng.integers(0, len(rv), 30); rv[taps] = rng.uniform(0.05, 0.25, 30) * np.exp(-taps / (SR * 0.15))
        rv[0] = 1; a = signal.fftconvolve(a, rv)[:len(a) + len(rv) // 2] * 0.8
    if style.startswith('whisper'):
        env = np.abs(signal.hilbert(a)); env = signal.sosfilt(sos('low', 30, 2), env)
        breath = signal.sosfilt(sos('band', [1500, 6000], 2), rng.standard_normal(len(a))) * env * 0.9
        a = signal.sosfilt(sos('high', 350), a) * 0.75 + breath
    if style == 'cold':
        a = signal.sosfilt(sos('high', 120), a)
    if style == 'vo':
        rv = np.zeros(int(SR * 1.2)); taps = rng.integers(0, len(rv), 60); rv[taps] = rng.uniform(0.02, 0.12, 60) * np.exp(-taps / (SR * 0.35))
        rv[0] = 1; a = signal.fftconvolve(a, rv)[:len(a) + len(rv) // 2]
    if style == 'sigh':   # breathy exhale in front of the line
        n = int(SR * 0.55); ex = signal.sosfilt(sos('band', [400, 3000], 2), rng.standard_normal(n)) * np.sin(np.linspace(0, np.pi, n)) ** 2 * 0.12
        a = np.concatenate([ex, np.zeros(int(SR * 0.08)), a])
    return a / (np.max(np.abs(a)) + 1e-9) * 0.9

def words_chunks(text, n_words_max=3):
    words = re.findall(r"\S+", text); chunks = []; cur = []
    for w in words:
        cur.append(w)
        if len(cur) >= n_words_max or re.search(r'[.!?,]$', w): chunks.append(' '.join(cur)); cur = []
    if cur: chunks.append(' '.join(cur))
    return chunks

out = np.zeros(int(SR * TOTAL)); lines_json = []; envs = {s: np.zeros(int(TOTAL * 30) + 1) for s in VOICES}
for lid, spk, t0, tmax, text, style in LINES:
    rec = os.path.join(HERE, 'voices_rec', lid + '.wav')
    ls, gdb = STYLE[style]
    if os.path.exists(rec):
        a, sr = sf.read(rec, always_2d=True); a = signal.resample_poly(a.mean(1), SR, sr)
    else:
        a = process(synth(spk, text, ls), style)
        for _ in range(4):                    # tighten until it fits its window
            if t0 + len(a) / SR <= tmax: break
            ls = max(0.78, ls * max(0.85, (tmax - t0) / (len(a) / SR) * 0.98))
            a = process(synth(spk, text, ls), style)
    dur = len(a) / SR
    i0 = int(t0 * SR); n = min(len(a), len(out) - i0)
    out[i0:i0 + n] += a[:n] * 10 ** (gdb / 20)
    # mouth envelope @30fps (speech band RMS)
    sp = signal.sosfilt(sos('band', [200, 3000], 2), a)
    for f in range(int(dur * 30)):
        seg = sp[int(f / 30 * SR): int((f + 1) / 30 * SR)]
        if len(seg): envs[spk][min(len(envs[spk]) - 1, int(t0 * 30) + f)] = float(np.sqrt(np.mean(seg ** 2)))
    # subtitle chunks timed by syllable-ish weight within the voiced span
    voiced = np.where(np.abs(sp) > 0.04)[0]
    v0 = voiced[0] / SR if len(voiced) else 0; v1 = voiced[-1] / SR if len(voiced) else dur
    if style == 'sigh': v0 = max(v0, 0.6)
    chunks = words_chunks(text); wts = [max(2, len(re.sub(r'[^a-zA-Z0-9]', '', c))) + 3 for c in chunks]
    tot = sum(wts); cur = t0 + v0; cj = []
    for c, wgt in zip(chunks, wts):
        d = (v1 - v0) * wgt / tot; cj.append({'t0': round(cur, 3), 't1': round(cur + d, 3), 'text': c}); cur += d
    cj[-1]['t1'] = round(min(t0 + dur + 0.35, tmax + 0.3), 3)
    lines_json.append({'id': lid, 'spk': spk, 't0': t0, 't1': round(t0 + dur, 3), 'text': text, 'chunks': cj})
    print(f'{lid} {spk:4s} {t0:6.2f}-{t0 + dur:6.2f} (max {tmax}) ls={ls:.2f}  {text}')

for s in envs:
    m = envs[s].max() or 1; envs[s] = np.round(np.clip(envs[s] / m * 1.6, 0, 1), 3)
os.makedirs(os.path.join(HERE, 'out'), exist_ok=True)
st = np.stack([out, out], 1); st *= 0.89 / np.max(np.abs(st))
sf.write(os.path.join(HERE, 'out', 'dialogue.wav'), st.astype(np.float32), SR, subtype='PCM_16')
json.dump({'lines': lines_json, 'mouth': {s: envs[s].tolist() for s in envs}}, open(os.path.join(HERE, 'out', 'dialogue.json'), 'w'))
print('wrote out/dialogue.wav + out/dialogue.json')
