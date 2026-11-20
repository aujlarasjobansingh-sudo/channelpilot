# synthesized SFX for the 2D hook preview
import numpy as np, soundfile as sf
from scipy.signal import butter, sosfilt
SR = 48000; END = 14.3; out = np.zeros(int(SR * END) + SR)
rng = np.random.default_rng(1)
def bp(x, lo, hi): return sosfilt(butter(2, [lo, hi], 'bandpass', fs=SR, output='sos'), x)
def lp(x, f): return sosfilt(butter(2, f, 'lowpass', fs=SR, output='sos'), x)
def put(t, x, g=1.0):
    i = int(t * SR); out[i:i + len(x)] += x[:len(out) - i] * g
def env(n, a, d): e = np.ones(n); na = int(a * SR); e[:na] = np.linspace(0, 1, na); e *= np.exp(-np.arange(n) / (d * SR)); return e
def boom(d=1.6, f0=60, g=1.0):
    n = int(d * SR); tt = np.arange(n) / SR; f = f0 * np.exp(-tt * 1.2)
    return (np.sin(2 * np.pi * np.cumsum(f) / SR) + .6 * lp(rng.standard_normal(n), 300)) * env(n, .005, d / 4) * g
def whoosh(d=.35, up=True):
    n = int(d * SR); x = rng.standard_normal(n); lo = np.linspace(400, 2500, n) if up else np.linspace(2500, 400, n)
    y = np.zeros(n); [y.__setitem__(slice(i, i + 2400), bp(x[i:i + 2400], lo[i], lo[i] * 2.2)) for i in range(0, n, 2400)]
    return y * np.sin(np.linspace(0, np.pi, n)) ** 2 * .7
def ring(d=1.1):
    n = int(d * SR); tt = np.arange(n) / SR; s = np.sign(np.sin(2 * np.pi * 22 * tt)) * .5 + .5
    return (np.sin(2 * np.pi * 2100 * tt) + .5 * np.sin(2 * np.pi * 3300 * tt)) * s * .18
def click(): n = 1800; return bp(rng.standard_normal(n), 2000, 8000) * env(n, .0005, .006) * .9
def beep(f=1400, d=.12): n = int(d * SR); tt = np.arange(n) / SR; return np.sin(2 * np.pi * f * tt) * env(n, .003, d / 2) * .35
def tick(): n = 600; return bp(rng.standard_normal(n), 3000, 9000) * env(n, .0003, .003) * .5
def crowd(d):
    n = int(d * SR); x = bp(rng.standard_normal(n), 300, 2400); am = 1 + .35 * np.sin(2 * np.pi * 3.1 * np.arange(n) / SR)
    e = np.minimum(1, np.arange(n) / (.3 * SR)) * np.minimum(1, (n - np.arange(n)) / (.4 * SR)); return x * am * e * .25
def crash(d=1.4):
    n = int(d * SR); return (bp(rng.standard_normal(n), 800, 6000) * env(n, .002, .25) * .8 + boom(d, 45, .9)[:n])
def pop(): n = int(.12 * SR); tt = np.arange(n) / SR; return np.sin(2 * np.pi * np.cumsum(np.linspace(900, 300, n)) / SR) * env(n, .002, .04) * .5
def sting():  # low hit + dissonant cluster for "zero"
    n = int(1.6 * SR); tt = np.arange(n) / SR
    cl = sum(np.sin(2 * np.pi * f * tt) for f in (146.8, 155.6, 207.7, 220)) * .12 * env(n, .01, .7)
    return boom(1.6, 50, 1.0) + cl
put(.15, ring(1.15), .8)
put(1.35, boom(2.0, 55), 1.0); put(1.33, crash(1.0), .35)
put(2.05, whoosh(.3), .6); put(2.3, boom(.8, 70, .7)); put(2.85, boom(.8, 70, .7))
put(3.2, lp(rng.standard_normal(int(.9 * SR)), 500) * env(int(.9 * SR), .2, .4) * .7)   # roar rumble
put(3.52, whoosh(.22), .9); put(3.72, crash(1.6), 1.2); put(3.72, boom(2.2, 40), .8)
put(0.36, pop(), .8)
put(4.82, whoosh(.3), .6); put(4.95, crowd(2.5), 1.0)
r = np.random.default_rng(3)
for t in np.sort(r.uniform(5.0, 7.3, 9)): put(t, click(), .6)
for (lt, a) in ((8.15, 7.6), (8.95, 8.4), (9.75, 9.2)):
    for t in np.arange(a, lt, 1 / 14): put(t, tick(), .5)
    put(lt, beep(1500), 1); put(lt + .02, pop(), .7)
for t in np.arange(11.3, 12.7, 1 / 10): put(t, tick(), .55)
put(12.74, sting(), 1.0); put(12.79, bp(rng.standard_normal(9000), 200, 3000) * env(9000, .001, .03), 1.0)   # stamp thud
for t in np.arange(12.85, 14.0, .5): put(t, beep(880, .2), .6)   # alarm
sf.write('out/sfx.wav', (out[:int(SR * END)] * .9).astype(np.float32), SR)
