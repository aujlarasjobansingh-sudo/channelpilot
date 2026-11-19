"""Synthesized SFX bed for Episode 1, scene 1 (0-10s). Timings mirror scene.js TIMELINE.
Usage: python3 sfx.py [seconds]  -> out/sfx.wav (48 kHz stereo)
"""
import sys, os
import numpy as np
import soundfile as sf
from scipy import signal

SR = 48000
DUR = float(sys.argv[1]) if len(sys.argv) > 1 else 10.0
N = int(SR * DUR)
t = np.arange(N) / SR
rng = np.random.default_rng(9)
L = np.zeros(N); R = np.zeros(N)

def bp(x, lo, hi, order=4):
    sos = signal.butter(order, [lo, hi], btype='band', fs=SR, output='sos'); return signal.sosfilt(sos, x)
def lp(x, f, order=4):
    sos = signal.butter(order, f, btype='low', fs=SR, output='sos'); return signal.sosfilt(sos, x)
def hp(x, f, order=4):
    sos = signal.butter(order, f, btype='high', fs=SR, output='sos'); return signal.sosfilt(sos, x)
def db(x): return 10 ** (x / 20)
def place(buf, start, clip, gain=1.0):
    i = int(start * SR)
    if i >= N: return
    n = min(len(clip), N - i); buf[i:i + n] += clip[:n] * gain
def env(n, a, r):  # attack/release in samples, sustain between
    e = np.ones(n); a = max(1, min(a, n)); r = max(1, min(r, n))
    e[:a] = np.linspace(0, 1, a); e[-r:] *= np.linspace(1, 0, r); return e

# --- rain against the glass (heard from inside: muffled, steady)
for buf, s in ((L, 1), (R, 2)):
    n = np.random.default_rng(s).standard_normal(N)
    body = lp(hp(n, 250), 3200) * 0.9
    hiss = bp(n, 3000, 9000) * 0.18
    mod = 1 + 0.12 * np.sin(2 * np.pi * 0.23 * t + s) + 0.06 * np.sin(2 * np.pi * 0.61 * t)
    buf += (body + hiss) * mod * db(-27)
    # individual drops tapping the glass
    for _ in range(int(DUR * 45)):
        st = rng.uniform(0, DUR); ln = int(SR * 0.012)
        d = rng.standard_normal(ln) * np.exp(-np.linspace(0, 9, ln))
        place(buf, st, bp(d, 1800, 6500, 2), db(-30 + rng.uniform(-6, 4)))

# --- soda cooler compressor hum + fluorescent buzz
hum = (np.sin(2 * np.pi * 60 * t) + 0.55 * np.sin(2 * np.pi * 120 * t + 0.3) + 0.3 * np.sin(2 * np.pi * 180 * t + 1.1)
       + 0.12 * np.sin(2 * np.pi * 240 * t))
hum *= 1 + 0.04 * np.sin(2 * np.pi * 0.4 * t)
buzz = bp(np.sign(np.sin(2 * np.pi * 120 * t)) * 0.5, 900, 4000, 2)
L += hum * db(-33) + buzz * db(-47); R += hum * db(-34) + buzz * db(-47)

# --- rag wiping the counter: two swishes per circle (period 1.55s), fading out 5.2-5.75
amp = np.clip(1 - (t - 5.2) / 0.55, 0, 1)
ph = t * 2 * np.pi / 1.55 + 0.4 * np.sin(t * 1.3)
speed = np.abs(np.sin(ph)) ** 1.5 * 0.7 + 0.3
n = rng.standard_normal(N)
wipe = bp(n, 700, 5000, 2) * speed * amp
wipe = lp(wipe, 6000)
L += wipe * db(-29) * 0.8; R += wipe * db(-29)

# --- camera move whooshes (subtle)
def whoosh(dur, lo, hi, gain):
    n_ = int(SR * dur); x = bp(rng.standard_normal(n_), lo, hi, 2)
    e = np.sin(np.linspace(0, np.pi, n_)) ** 2; return x * e * gain
place(L, 5.83, whoosh(0.6, 300, 2500, db(-27))); place(R, 5.83, whoosh(0.6, 300, 2500, db(-27)))

# --- phone vibrating on a hard counter: BZZT-BZZT
def bzzt(dur):
    n_ = int(SR * dur); tt = np.arange(n_) / SR
    motor = np.sign(np.sin(2 * np.pi * 172 * tt)) * 0.6 + np.sin(2 * np.pi * 344 * tt) * 0.3
    rattle = bp(rng.standard_normal(n_), 1200, 5000, 2) * (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 86 * tt)))
    x = lp(motor, 1800) * 0.8 + rattle * 0.35
    return x * env(n_, int(SR * 0.012), int(SR * 0.03))
for st, dur in ((6.62, 0.30), (7.06, 0.30)):
    b = bzzt(dur); place(L, st, b, db(-12)); place(R, st, b, db(-11))

# --- grab + lift: short slide on the counter, cloth rustle
sl = bp(rng.standard_normal(int(SR * 0.18)), 1500, 7000, 2) * env(int(SR * 0.18), int(SR * 0.02), int(SR * 0.12))
place(L, 7.92, sl, db(-24)); place(R, 7.92, sl, db(-23))
place(L, 7.98, whoosh(0.6, 200, 1800, db(-29))); place(R, 7.98, whoosh(0.6, 200, 1800, db(-28)))

# --- typing: soft screen taps with haptic tick, 15 chars/s from 8.75s
REPLY = "Dead quiet. Just me and the crickets."
for i in range(len(REPLY)):
    st = 8.75 + i / 15 + rng.uniform(-0.008, 0.008)
    if st >= DUR: break
    ln = int(SR * 0.03)
    tap = bp(rng.standard_normal(ln), 2000, 7000, 2) * np.exp(-np.linspace(0, 12, ln))
    tick = np.sin(2 * np.pi * 220 * np.arange(ln) / SR) * np.exp(-np.linspace(0, 18, ln))
    c = tap * 0.6 + tick * 0.5
    place(L, st, c, db(-21)); place(R, st, c, db(-20))

# --- master: gentle fade in, peak normalise to -3 dBFS
fade = np.clip(t / 0.25, 0, 1); L *= fade; R *= fade
out = np.stack([L, R], 1); out *= db(-3) / np.max(np.abs(out))
os.makedirs(os.path.join(os.path.dirname(__file__) or '.', 'out'), exist_ok=True)
sf.write(os.path.join(os.path.dirname(__file__) or '.', 'out', 'sfx.wav'), out.astype(np.float32), SR, subtype='PCM_16')
print('wrote out/sfx.wav', DUR, 's')
