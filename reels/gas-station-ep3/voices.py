"""Dialogue for Gas Station Episode 3 (finale) using Piper (offline neural TTS).
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
TOTAL = 85.0

VOICES = {
    'you':  dict(model='en-us-ryan-high.onnx', sid=None),
    'sam':  dict(model='en-us-libritts-high.onnx', sid=42),
    'cop':  dict(model='en-us-libritts-high.onnx', sid=186),
    'mega': dict(model='en-us-libritts-high.onnx', sid=186),
}
# id, speaker, start, latest end, text, style
LINES = [
    ('y1', 'you', 1.3, 5.0, 'Get out! Come on, run!', 'alarm'),
    ('s1', 'sam', 5.6, 9.4, "Thank god, he's right behind us! Move!", 'alarm'),
    ('c1', 'cop', 12.5, 15.5, 'STOP! GET BACK HERE!', 'far'),
    ('y2', 'you', 25.0, 28.3, 'A car! We can flag them down!', 'alarm'),
    ('s2', 'sam', 28.6, 31.4, "Wait... don't step into the road yet.", 'normal'),
    ('y3', 'you', 35.0, 38.8, 'Wait... why did he stop chasing us?', 'normal'),
    ('y4', 'you', 55.0, 57.8, 'You... you were never locked in that car.', 'whisper'),
    ('s3', 'sam', 58.0, 64.0, "The back doors don't open from the inside, kid. I just needed someone stupid enough to pull the handle.", 'cold'),
    ('s4', 'sam', 66.6, 70.2, "Great. Get up, we're going into the woods. NOW!", 'alarm'),
    ('mg', 'mega', 73.5, 76.0, 'DROP THE WEAPON!', 'mega'),
]
STYLE = {   # length_scale, gain dB
    'sigh': (1.08, -2), 'panic': (0.86, 0), 'alarm': (0.92, 0), 'normal': (1.0, -1), 'relief': (0.97, -1),
    'whisper': (1.05, -7), 'whisperfast': (0.9, -6), 'muffled': (0.98, -3), 'muffledyell': (0.9, -1),
    'tense': (1.08, -3), 'plead': (0.92, 0), 'cold': (1.25, -3), 'vo': (1.12, -1), 'radio': (1.0, -1), 'radioclear': (1.0, 0), 'eerie': (1.0, 0), 'far': (1.0, -6), 'mega': (1.0, 0),
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

# ---------------------------------------------------------------- recorded (ElevenLabs) lines: tighten + schedule
ORDER = [l[0] for l in LINES]
T0 = {l[0]: l[2] for l in LINES}
SCHED, END = {}, {}
def compress_pauses(a, keep=0.17, thresh=0.24):
    env = signal.sosfilt(sos('low', 25, 2), np.abs(a)); quiet = env < 0.012
    out, i, n = [], 0, len(a)
    while i < n:
        if quiet[i]:
            j = i
            while j < n and quiet[j]: j += 1
            seglen = (j - i) / SR
            out.append(a[i:j] if seglen <= thresh or i == 0 or j == n else np.concatenate([a[i:i + int(keep * SR / 2)], a[j - int(keep * SR / 2):j]]))
            i = j
        else:
            j = i
            while j < n and not quiet[j]: j += 1
            out.append(a[i:j]); i = j
    return np.concatenate(out)
def fit_recorded(a, lid, spk, t0, style):
    e = np.where(np.abs(a) > 0.02)[0]; a = a[max(0, e[0] - 480): e[-1] + 2400]
    a = compress_pauses(a)
    k = ORDER.index(lid)
    prev_end = END[ORDER[k - 1]] if k else 0
    start = max(t0 - 0.9, prev_end + 0.1)
    nxt = T0[ORDER[k + 1]] - 0.08 if k + 1 < len(ORDER) else TOTAL - 4.6
    avail = max(0.5, nxt - start)
    if len(a) / SR > avail:
        f = min(1.12, (len(a) / SR) / avail)
        tmp_in, tmp_out = '/tmp/claude-0/_in.wav', '/tmp/claude-0/_out.wav'
        sf.write(tmp_in, a, SR)
        import subprocess; subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', tmp_in, '-af', f'atempo={f:.4f}', tmp_out], check=True)
        a, _ = sf.read(tmp_out)
    # start as late as possible (close to the intended beat) while still ending before the next line
    dur = len(a) / SR
    start = max(start, min(t0, nxt - dur))
    SCHED[lid] = round(start, 3); END[lid] = start + dur
    return a / (np.max(np.abs(a)) + 1e-9) * 0.9
def process_fx(a, style):
    rng = np.random.default_rng(len(a))
    if style.startswith('muffled'):
        a = signal.sosfilt(sos('low', 2200), a); a = signal.sosfilt(sos('high', 150), a)
        rv = np.zeros(int(SR * 0.6)); taps = rng.integers(0, len(rv), 30); rv[taps] = rng.uniform(0.05, 0.22, 30) * np.exp(-taps / (SR * 0.15))
        rv[0] = 1; a = signal.fftconvolve(a, rv)[:len(a) + len(rv) // 2] * 0.8
    if style == 'vo':
        rv = np.zeros(int(SR * 1.2)); taps = rng.integers(0, len(rv), 60); rv[taps] = rng.uniform(0.02, 0.1, 60) * np.exp(-taps / (SR * 0.35))
        rv[0] = 1; a = signal.fftconvolve(a, rv)[:len(a) + len(rv) // 2]
    if style.startswith('radio'):   # 80s walkie-talkie: narrow band, clipped, under a static bed
        clean = style == 'radioclear'
        a = signal.sosfilt(sos('band', [350, 3200 if not clean else 4200]), a)
        a = np.tanh(a / (np.max(np.abs(a)) + 1e-9) * (4.0 if not clean else 2.2))
        st = signal.sosfilt(sos('band', [1200, 7000], 2), rng.standard_normal(len(a))) * (0.07 if not clean else 0.04)
        a = a + st * (0.6 + 0.4 * np.abs(np.sin(np.arange(len(a)) / SR * 7.0)))
    if style == 'far':             # yelling from ~40 m away across a wet lot
        a = signal.sosfilt(sos('low', 2600), a); a = signal.sosfilt(sos('high', 220), a)
        rv = np.zeros(int(SR * 1.1)); taps = rng.integers(int(SR * .03), len(rv), 60); rv[taps] = rng.uniform(0.05, 0.2, 60) * np.exp(-taps / (SR * 0.3))
        rv[0] = 0.7; a = signal.fftconvolve(a, rv)[:len(a) + len(rv) // 2]
    if style == 'mega':            # police PA horn: narrow, clipped, slapback off the trees
        a = signal.sosfilt(sos('band', [450, 3400]), a); a = np.tanh(a / (np.max(np.abs(a)) + 1e-9) * 3.2)
        a = a + np.concatenate([np.zeros(int(SR * 0.16)), a])[:len(a)] * 0.35
    if style == 'eerie':            # open air with an unnatural doubled echo
        a2 = np.concatenate([np.zeros(int(SR * 0.012)), a])[:len(a)] * 0.45
        rv = np.zeros(int(SR * 1.4)); taps = rng.integers(int(SR * .05), len(rv), 70); rv[taps] = rng.uniform(0.03, 0.16, 70) * np.exp(-taps / (SR * 0.4))
        rv[0] = 1; a = signal.fftconvolve(a + a2, rv)[:len(a) + len(rv) // 2]
    return a / (np.max(np.abs(a)) + 1e-9) * 0.9

out = np.zeros(int(SR * TOTAL)); lines_json = []; envs = {s: np.zeros(int(TOTAL * 30) + 1) for s in VOICES}
for lid, spk, t0, tmax, text, style in LINES:
    rec = os.path.join(HERE, 'voices_rec', lid + '.wav')
    ls, gdb = STYLE[style]
    if os.path.exists(rec):
        a, sr = sf.read(rec, always_2d=True); a = signal.resample_poly(a.mean(1), SR, sr)
        a = fit_recorded(a, lid, spk, t0, style)
        t0 = SCHED[lid]
        if style.startswith('muffled') or style.startswith('radio') or style in ('vo', 'eerie', 'far', 'mega'): a = process_fx(a, style)
    else:
        a = process(synth(spk, text, ls), style)
        for _ in range(4):                    # tighten until it fits its window
            if t0 + len(a) / SR <= tmax: break
            ls = max(0.78, ls * max(0.85, (tmax - t0) / (len(a) / SR) * 0.98))
            a = process(synth(spk, text, ls), style)
    if os.path.exists(rec): gdb = {'whisper': -3, 'whisperfast': -2, 'cold': -1}.get(style, 0)
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
    if style == 'sigh' and not os.path.exists(rec): v0 = max(v0, 0.6)
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
