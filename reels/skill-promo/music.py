"""Original background track for the skill promo reel (made in code, royalty-free).
112 BPM light house: four-on-the-floor kick, off-beat hats, claps, sidechained bass + warm chords, pluck hook.
Structure (fits the 38 s reel): 0–3.0 s filtered build (under the reference hook) → DROP at 3.0 s → groove → final lift.
Usage: python3 music.py  -> out/music.wav (full) + out/music_bed.wav (starts at the drop, for the reel)
"""
import os
import numpy as np, soundfile as sf
from scipy import signal

HERE = os.path.dirname(os.path.abspath(__file__))
SR = 48000; BPM = 112; BEAT = 60 / BPM; BAR = 4 * BEAT
OUT_DROP = 3.0; OUT_DUR = 38.0
PRE = 2 * BAR - OUT_DROP                 # pre-roll so the 2-bar build fits; trimmed at the end
DROP = OUT_DROP + PRE; DUR = OUT_DUR + PRE
N = int(SR * DUR); t = np.arange(N) / SR
rng = np.random.default_rng(3)
L = np.zeros(N); R = np.zeros(N)

def sos(kind, f, o=4): return signal.butter(o, f, btype=kind, fs=SR, output='sos')
def db(x): return 10 ** (x / 20)
def mtof(m): return 440 * 2 ** ((m - 69) / 12)
def place(buf, st, x, g=1.0):
    i = int(st * SR)
    if i >= N or i < 0: return
    n = min(len(x), N - i); buf[i:i + n] += x[:n] * g
def both(st, x, g=1.0, pan=0.0):
    place(L, st, x, g * np.sqrt(0.5 * (1 - pan)) * 1.414); place(R, st, x, g * np.sqrt(0.5 * (1 + pan)) * 1.414)

# beat grid: beat 0 of bar 0 sits so that a downbeat lands exactly on the drop
t0 = DROP - 2 * BAR          # two bars of build before the drop
beats = np.arange(t0, DUR, BEAT)

# ---------------- drums
def kick():
    n = int(.42 * SR); tt = np.arange(n) / SR
    f = 48 + 110 * np.exp(-tt * 38); ph = 2 * np.pi * np.cumsum(f) / SR
    return (np.sin(ph) * np.exp(-tt * 7.5) + 0.25 * signal.sosfilt(sos('high', 3000), rng.standard_normal(n)) * np.exp(-tt * 120)) * 0.95
def clap():
    n = int(.3 * SR); tt = np.arange(n) / SR; x = signal.sosfilt(sos('band', [900, 5000], 2), rng.standard_normal(n))
    env = sum(np.exp(-np.maximum(0, tt - d) * 60) * (tt >= d) for d in (0, .011, .022)) * 0.6 + np.exp(-tt * 16) * 0.5
    return x * env
def hat(open_=False):
    n = int((.22 if open_ else .06) * SR); tt = np.arange(n) / SR
    return signal.sosfilt(sos('high', 7000), rng.standard_normal(n)) * np.exp(-tt * (14 if open_ else 70))
K, C, Hc, Ho = kick(), clap(), hat(), hat(True)
side = np.ones(N)                                     # sidechain envelope from the kick
for i, b in enumerate(beats):
    if b < DROP - 0.01:                               # build: only claps rolling faster + hats
        if i % 2 == 1: both(b, C, db(-16 + 6 * (b - t0) / (DROP - t0)))
        both(b + BEAT / 2, Hc, db(-26))
        continue
    both(b, K, db(-6))
    j = int((b - DROP) * SR); m = min(N - j, int(.32 * SR))
    if m > 0: side[j:j + m] = np.minimum(side[j:j + m], 1 - 0.7 * np.exp(-np.arange(m) / SR * 9) )
    if i % 2 == 1: both(b, C, db(-13), 0.05)
    both(b + BEAT / 2, Ho if i % 4 == 3 else Hc, db(-20 if i % 4 == 3 else -22), 0.25)
    both(b + BEAT / 4, Hc, db(-30), -0.3); both(b + 3 * BEAT / 4, Hc, db(-31), -0.3)
# snare roll into the drop
for k in range(16): both(DROP - BAR / 2 + k * BEAT / 8, C, db(-24 + k * 0.8))

# ---------------- harmony: Am – F – C – G  (vi IV I V), one chord per bar
PROG = [(57, [57, 60, 64]), (53, [53, 57, 60]), (48, [55, 60, 64]), (55, [55, 59, 62])]
def saw(f, n, det=0.0):
    ph = (np.arange(n) / SR * f * (1 + det)) % 1.0; return 2 * ph - 1
pad = np.zeros(N); bass = np.zeros(N)
for bi, bs in enumerate(np.arange(t0, DUR, BAR)):
    root, notes = PROG[bi % 4]; i0 = int(bs * SR); n = min(int(BAR * SR), N - i0)
    if n <= 0: break
    env = np.minimum(1, np.arange(n) / (0.03 * SR)) * np.minimum(1, (n - np.arange(n)) / (0.05 * SR))
    ch = sum(saw(mtof(m), n, d) for m in notes for d in (-0.006, 0, 0.007)) / 9
    pad[i0:i0 + n] += ch * env
    # bass: off-beat octave pumping (8ths)
    for k in range(8):
        s = int(k * BEAT / 2 * SR); ln = int(BEAT / 2 * 0.85 * SR)
        if s + ln > n: break
        f = mtof(root - 12 + (12 if k % 2 else 0)); tt = np.arange(ln) / SR
        tone = np.sin(2 * np.pi * f * tt) + 0.35 * np.sign(np.sin(2 * np.pi * f * tt))
        bass[i0 + s:i0 + s + ln] += tone * np.exp(-tt * 3) * np.minimum(1, tt / .004)
# filter sweep on the pad during the build, open after the drop
cut = np.where(t < DROP, 400 + 2600 * np.clip((t - t0) / (DROP - t0), 0, 1) ** 2, 3200)
padf = np.zeros(N); blk = 2400
for i in range(0, N, blk):
    padf[i:i + blk] = signal.sosfilt(sos('low', min(cut[i], 20000), 2), pad[i:i + blk])
padf = signal.sosfilt(sos('low', 6000, 2), padf)
bass = signal.sosfilt(sos('low', 900, 4), bass) * (t >= DROP)
L += padf * side * db(-15) * 1.05; R += padf * side * db(-15) * 0.95
L += bass * side * db(-11); R += bass * side * db(-11)

# ---------------- pluck hook (starts on the drop), 16th-note motif per chord
MOTIF = [0, 2, 1, 2, 0, 2, 3, 2]       # indexes into chord tones (+12 for top)
def pluck(f):
    n = int(.28 * SR); tt = np.arange(n) / SR
    x = (saw(f, n) * 0.6 + np.sin(2 * np.pi * f * 2 * tt) * 0.25) * np.exp(-tt * 14)
    return signal.sosfilt(sos('low', 4200, 2), x)
for bi, bs in enumerate(np.arange(DROP, DUR, BAR)):
    _, notes = PROG[(bi + 2) % 4]
    tones = notes + [notes[0] + 12]
    for k, m in enumerate(MOTIF):
        st = bs + k * BEAT / 2
        if st >= DUR: break
        lift = 12 if st > DUR - 2 * BAR else 0              # octave lift for the ending
        both(st, pluck(mtof(tones[m] + 12 + lift)), db(-17), 0.3 if k % 2 else -0.3)

# ---------------- riser into the drop + impact
n = int((DROP - t0) * SR); tt = np.arange(n) / SR
riser = signal.sosfilt(sos('band', [1500, 9000], 2), rng.standard_normal(n)) * (tt / tt[-1]) ** 2
place(L, t0, riser, db(-22)); place(R, t0, riser, db(-22))
imp_n = int(1.5 * SR); it = np.arange(imp_n) / SR
impact = np.sin(2 * np.pi * 45 * it) * np.exp(-it * 3) + signal.sosfilt(sos('low', 3000), rng.standard_normal(imp_n)) * np.exp(-it * 5) * 0.3
place(L, DROP, impact, db(-10)); place(R, DROP, impact, db(-10))

# ---------------- space + master
ir_n = int(1.6 * SR); ir = rng.standard_normal(ir_n) * np.exp(-np.arange(ir_n) / SR * 3.2) * 0.05; ir[0] = 0
L = L + signal.fftconvolve(L, ir)[:N] * 0.35; R = R + signal.fftconvolve(R, ir[::-1].copy() * 0 + np.roll(ir, 113))[:N] * 0.35
mix = np.stack([L, R], 1)[int(PRE * SR):]
tt = np.arange(len(mix)) / SR
fade = np.clip(tt / 0.05, 0, 1) * np.clip((OUT_DUR - tt) / 1.5, 0, 1)
mix = mix * fade[:, None]
mix = np.tanh(mix / np.max(np.abs(mix)) * 1.6) / np.tanh(1.6) * 0.89      # gentle glue saturation
os.makedirs(os.path.join(HERE, 'out'), exist_ok=True)
sf.write(os.path.join(HERE, 'out', 'music.wav'), mix.astype(np.float32), SR, subtype='PCM_24')
print('wrote out/music.wav', OUT_DUR, 's,', BPM, 'BPM, drop at', OUT_DROP)
