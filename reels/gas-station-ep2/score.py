"""Original suspense/horror score for the fast cut of Episode 2 (made in code, royalty-free).
Composed on the CUT timeline (cue times given on the original timeline and mapped through cut.py's CUTS),
mixed under out/mix_fast.wav with ducking under the dialogue, then muxed onto the fast-cut video.
Usage: python3 score.py  -> out/episode2_fast_music.mp4
"""
import os, subprocess
import numpy as np, soundfile as sf
from scipy import signal

HERE = os.path.dirname(os.path.abspath(__file__)); SR = 48000
CUTS = [(2.6, 5.4), (11.2, 14.6), (21.8, 23.8), (30.4, 33.6), (35.6, 36.9), (40.9, 41.8), (52.6, 56.6), (61.0, 65.2), (76.6, 79.6), (107.5, 110.0)]
def m(t):   # original time -> cut time
    s = 0.0
    for a, b in CUTS:
        if t >= b: s += b - a
        elif t > a: return a - s
    return t - s
base, _ = sf.read(os.path.join(HERE, 'out', 'mix_fast.wav'), always_2d=True)
N = len(base); DUR = N / SR; t = np.arange(N) / SR
rng = np.random.default_rng(13)
L = np.zeros(N); R = np.zeros(N)
def sos(k, f, o=4): return signal.butter(o, f, btype=k, fs=SR, output='sos')
def db(x): return 10 ** (x / 20)
def mtof(n): return 440 * 2 ** ((n - 69) / 12)
def place(st, x, g=1.0, pan=0.0):
    i = int(st * SR)
    if i >= N: return
    if i < 0: x = x[-i:]; i = 0
    n = min(len(x), N - i)
    L[i:i + n] += x[:n] * g * np.sqrt(0.5 * (1 - pan)) * 1.414; R[i:i + n] += x[:n] * g * np.sqrt(0.5 * (1 + pan)) * 1.414
def env(n, a, r):
    e = np.ones(n); a = max(1, min(int(a * SR), n)); r = max(1, min(int(r * SR), n)); e[:a] = np.linspace(0, 1, a); e[-r:] *= np.linspace(1, 0, r); return e
def saw(f, n, det=0.0): ph = (np.arange(n) / SR * f * (1 + det)) % 1.0; return 2 * ph - 1
def section(a, b):   # smooth 0..1 gate between two CUT times
    return np.clip((t - a) / 0.6, 0, 1) * np.clip((b - t) / 0.6, 0, 1)

# ---------------- cue points (original timeline -> cut timeline)
T = {k: m(v) for k, v in dict(start=0.0, whip=5.9, bang=9.6, cop=14.9, vault=24.2, slash=26.7, crash=28.4, gun=34.0, door=37.0,
                               run=42.0, out=51.0, thud=66.0, whipcar=70.0, palms=72.0, closer=79.8, keys=85.0, back=87.9, step=95.4, freeze=99.2).items()}
END = DUR

# ---------------- low suspense drone (whole piece until the freeze), swells with the story
dr = np.zeros(N)
for f, d in ((36.7, 0), (36.95, .3), (55.0, .7), (73.4, 1.1), (77.8, 1.9)):   # D1 + A1 + D2 + a dissonant Eb-ish edge
    dr += np.sin(2 * np.pi * f * t + d) * (1 + 0.15 * np.sin(2 * np.pi * 0.11 * t + d))
dr = signal.sosfilt(sos('low', 260, 2), dr + 0.4 * saw(36.7, N, 0.003))
lvl = np.interp(t, [0, T['bang'], T['crash'], T['run'], T['thud'], T['palms'], T['back'], T['step'], T['freeze'] - 0.2, T['freeze']],
                   [0.55, 0.7, 0.9, 0.75, 0.9, 1.0, 0.85, 1.0, 1.0, 0.18])
L += dr * lvl * db(-17); R += dr * lvl * db(-17)

# ---------------- ticking clock (suspense) in the quiet decision moments
def tick(g):
    n = int(SR * .025); tt = np.arange(n) / SR
    return signal.sosfilt(sos('high', 2500), rng.standard_normal(n)) * np.exp(-tt * 260) * g
for a, b, bpm in ((T['start'], T['bang'], 100), (T['gun'], T['run'], 120), (T['closer'], T['back'], 110)):
    k = 0
    for st in np.arange(a + 0.2, b - 0.2, 60 / bpm): place(st, tick(db(-22 if k % 2 else -19)), pan=0.3 if k % 2 else -0.3); k += 1

# ---------------- staccato string ostinato (tension), D minor with a b2 for dread
def stac(f, g):
    n = int(SR * .16); x = sum(saw(f, n, d) for d in (-.004, 0, .005)) / 3
    return signal.sosfilt(sos('low', 2600, 2), x) * env(n, .004, .12) * g
def ostinato(a, b, bpm, pattern, g, oct_=0):
    step = 60 / bpm / 2; k = 0
    for st in np.arange(a, b, step):
        n = pattern[k % len(pattern)] + oct_; k += 1
        place(st, stac(mtof(n), db(g)), pan=0.25 if k % 2 else -0.25)
ostinato(T['cop'], T['vault'], 112, [50, 50, 53, 50, 51, 50, 53, 55], -21)                 # the clash: creeping
ostinato(T['run'], T['thud'], 140, [50, 53, 57, 53, 50, 53, 58, 57], -19)                  # escape: driving
ostinato(T['run'], T['thud'], 140, [38, 38, 38, 38, 39, 39, 38, 38], -21)                  # escape: low cello pulse
ostinato(T['back'], T['step'], 104, [50, 51, 50, 53, 50, 51, 55, 53], -20)                 # officer gets up

# ---------------- war-drum toms under the fight and the run
def tom(f, g):
    n = int(SR * .5); tt = np.arange(n) / SR; ff = f * (1 + 0.6 * np.exp(-tt * 30))
    return (np.sin(2 * np.pi * np.cumsum(ff) / SR) * np.exp(-tt * 7) + 0.2 * signal.sosfilt(sos('low', 1500), rng.standard_normal(n)) * np.exp(-tt * 30)) * g
for st in np.arange(T['vault'], T['gun'] - 0.1, 60 / 150): place(st, tom(70, db(-14)), pan=-0.1)
for i, st in enumerate(np.arange(T['vault'] + 60 / 300, T['gun'] - 0.1, 60 / 150)): place(st, tom(95 if i % 2 else 82, db(-19)), pan=0.2)
for i, st in enumerate(np.arange(T['run'], T['thud'], 60 / 140)): place(st, tom(65 if i % 4 == 0 else 85, db(-16 if i % 4 == 0 else -21)))

# ---------------- horror hits: BRAAM (low brass), stingers (string clusters), risers, eerie whine
def braam(dur=3.0, g=1.0):
    n = int(SR * dur); x = sum(saw(f, n, d) for f in (36.7, 55.0, 73.4) for d in (-.006, 0, .007)) / 9
    x = np.tanh(signal.sosfilt(sos('low', 700, 2), x) * 3) * env(n, .05, dur * .7)
    return x * g
def stinger(g=1.0):
    n = int(SR * 2.2); tt = np.arange(n) / SR
    x = sum(saw(mtof(nn), n, .003 * k) * (1 + 0.004 * np.sin(2 * np.pi * 6 * tt)) for k, nn in enumerate((86, 87, 92, 93, 98)))
    return signal.sosfilt(sos('band', [900, 7000], 2), x) * env(n, .01, 1.6) * g / 3
def riser(dur, g=1.0):
    n = int(SR * dur); tt = np.arange(n) / SR; k = (tt / dur) ** 2
    x = signal.sosfilt(sos('band', [800, 9000], 2), rng.standard_normal(n)) * k + np.sin(2 * np.pi * np.cumsum(200 + 1600 * k) / SR) * k * 0.3
    return x * g
def whine(dur, g=1.0):
    n = int(SR * dur); tt = np.arange(n) / SR; f = 1900 + 300 * np.sin(2 * np.pi * 0.3 * tt) + 25 * np.sin(2 * np.pi * 5.5 * tt)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.linspace(0, np.pi, n)) ** 2 * g
place(T['bang'] - 0.8, riser(0.8, db(-20)))
place(T['bang'], braam(3.2, db(-11))); place(T['bang'], stinger(db(-16)), pan=0.1)
place(T['crash'] - 1.2, riser(1.2, db(-19))); place(T['crash'], braam(3.5, db(-9)))
place(T['door'], braam(2.2, db(-17)))
place(T['thud'] - 0.1, stinger(db(-17)), pan=0.4)
place(T['whipcar'], braam(3.0, db(-12)))
place(T['palms'], stinger(db(-14)), pan=0.3)
place(T['palms'], whine(8.0, db(-30)), pan=-0.4)
place(T['back'] - 1.0, riser(1.0, db(-19))); place(T['back'], stinger(db(-16)), pan=-0.2)
place(T['step'] - 1.5, riser(1.5, db(-17))); place(T['step'], braam(4.0, db(-8)))
place(T['freeze'] - 1.2, riser(1.2, db(-16)))
n = int(SR * 3); tt = np.arange(n) / SR
place(T['freeze'], np.sin(2 * np.pi * 32 * tt) * np.exp(-tt * 1.4) + braam(3.0, 0.5), db(-8))      # final impact into silence

# ---------------- duck under dialogue, mix, normalise
dlg, _ = sf.read(os.path.join(HERE, 'out', 'dialogue.wav'), always_2d=True)
d = np.zeros(N)
keep, start = [], 0
for a, b in CUTS: keep.append((start, a)); start = b
keep.append((start, 1e9))
pos = 0
for a, b in keep:   # cut the dialogue track the same way to know where voices are
    seg = dlg[int(a * SR): int(min(b, len(dlg) / SR) * SR), 0]; n = min(len(seg), N - pos)
    if n <= 0: break
    d[pos:pos + n] = seg[:n]; pos += n
e = signal.sosfilt(sos('low', 6, 2), np.abs(d)); e = np.clip(e / (e.max() + 1e-9) * 7, 0, 1)
duck = 1 - 0.6 * e
music = np.stack([L, R], 1) * duck[:, None]
music *= db(-6) / (np.abs(music).max() + 1e-9)
out = base + music
out *= 0.95 / np.abs(out).max()
raw = os.path.join(HERE, 'out', 'mix_fast_music_raw.wav'); sf.write(raw, out.astype(np.float32), SR, subtype='PCM_24')
sf.write(os.path.join(HERE, 'out', 'score_only.wav'), (np.stack([L, R], 1) / (np.abs(np.stack([L, R], 1)).max() + 1e-9) * 0.9).astype(np.float32), SR, subtype='PCM_24')
fin = os.path.join(HERE, 'out', 'mix_fast_music.wav')
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', raw, '-af', 'acompressor=threshold=0.15:ratio=2.5:attack=5:release=150:makeup=1.3,loudnorm=I=-14:TP=-1.5:LRA=11', '-ar', '48000', fin], check=True)
mp4 = os.path.join(HERE, 'out', 'episode2_fast_music.mp4')
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', os.path.join(HERE, 'out', 'episode2_fast.mp4'), '-i', fin, '-map', '0:v', '-map', '1:a', '-c:v', 'copy',
                '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', mp4], check=True)
print('cues (cut timeline):', {k: round(v, 2) for k, v in T.items()}); print('wrote', mp4)
