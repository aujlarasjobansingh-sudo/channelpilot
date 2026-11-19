"""Procedural score + SFX for EP01 Part 1 (0 - 310.6 s). Writes music.wav and sfx.wav (44.1 kHz stereo)."""
import numpy as np
from scipy.signal import butter, sosfilt, fftconvolve
from scipy.io import wavfile

SR = 44100
DUR = 311.0
N = int(SR * DUR)
rng = np.random.default_rng(7)
music = np.zeros((N, 2))
sfx = np.zeros((N, 2))

def note(n):  # 'A4' style -> Hz
    names = {'C': -9, 'C#': -8, 'D': -7, 'D#': -6, 'E': -5, 'F': -4, 'F#': -3, 'G': -2, 'G#': -1, 'A': 0, 'A#': 1, 'B': 2}
    p, o = n[:-1], int(n[-1])
    return 440.0 * 2 ** ((names[p] + 12 * (o - 4)) / 12)

def lp(x, f, order=2): return sosfilt(butter(order, f, 'low', fs=SR, output='sos'), x)
def hp(x, f, order=2): return sosfilt(butter(order, f, 'high', fs=SR, output='sos'), x)
def bp(x, lo, hi): return sosfilt(butter(2, [lo, hi], 'band', fs=SR, output='sos'), x)
def env(n, a, r):
    e = np.ones(n); A = min(int(a * SR), n); R = min(int(r * SR), n)
    if A: e[:A] = np.linspace(0, 1, A)
    if R: e[-R:] *= np.linspace(1, 0, R)
    return e
def put(buf, t, x, gain=1.0, pan=0.0):
    i = int(t * SR)
    if i >= N: return
    x = x[: N - i]
    l, r = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
    if x.ndim == 1:
        buf[i:i + len(x), 0] += x * gain * l * 1.414; buf[i:i + len(x), 1] += x * gain * r * 1.414
    else:
        buf[i:i + len(x)] += x * gain
def tvec(d): return np.arange(int(d * SR)) / SR
def saw(f, d, det=0.0):
    t = tvec(d); ph = (f * (1 + det)) * t
    return 2 * (ph - np.floor(ph + 0.5))

# ---------------- instruments ----------------
def pad(freqs, d, cutoff=1400, a=1.5, r=1.5, bright=1.0):
    x = np.zeros(int(d * SR))
    for f in freqs:
        for det in (-0.004, 0.0, 0.005):
            x += saw(f, d, det) * 0.15
    x = lp(x, cutoff * bright, 2)
    return x * env(len(x), a, r)
def piano(f, d=2.5, vel=1.0):
    t = tvec(d)
    x = (np.sin(2 * np.pi * f * t) + 0.45 * np.sin(4 * np.pi * f * t) * np.exp(-t * 3) + 0.2 * np.sin(6 * np.pi * f * t) * np.exp(-t * 5))
    return x * np.exp(-t * 1.6) * env(len(t), 0.004, 0.3) * 0.35 * vel
def mallet(f, d=1.2, vel=1.0):
    t = tvec(d); return (np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * f * 3.01 * t) * np.exp(-t * 8)) * np.exp(-t * 4) * 0.3 * vel
def bell(f, d=3.0, vel=1.0):
    t = tvec(d); x = sum(a * np.sin(2 * np.pi * f * m * t) * np.exp(-t * dm) for m, a, dm in [(1, 1, 1.2), (2.76, 0.5, 2.0), (5.4, 0.25, 3.5), (8.9, 0.12, 5)])
    return x * 0.22 * vel
def drum(d=1.2, f0=48, f1=110, vel=1.0):
    t = tvec(d)
    body = np.sin(2 * np.pi * (f0 * t + f1 / 14 * (1 - np.exp(-14 * t)))) * np.exp(-4.5 * t)
    click = lp(rng.standard_normal(len(t)), 1800) * np.exp(-60 * t) * 0.5
    return (body + click) * 0.8 * vel
def pulse(f, d, rate, duty=0.12):
    t = tvec(d); g = ((t * rate) % 1.0) < duty
    return np.sin(2 * np.pi * f * t) * g * np.exp(-((t * rate) % 1.0) * 18)
def noise(d, color='white'):
    x = rng.standard_normal(int(d * SR))
    if color == 'brown': x = np.cumsum(x); x = hp(x / (np.max(np.abs(x)) + 1e-9), 20)
    if color == 'pink': x = lp(x, 1200, 1) + 0.3 * x
    return x / (np.max(np.abs(x)) + 1e-9)
def riser(d, f0=200, f1=2000):
    t = tvec(d); f = f0 * (f1 / f0) ** (t / d)
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.25
    n = hp(noise(d), 1500) * (t / d) * 0.3
    return (tone + n) * (t / d) ** 1.5
def whoosh(d=0.6):
    x = bp(noise(d), 500, 6000); return x * np.sin(np.linspace(0, np.pi, len(x))) ** 2 * 0.7
def boom(d=2.5, vel=1.0):
    t = tvec(d)
    sub = np.sin(2 * np.pi * (38 * t + 120 / 9 * (1 - np.exp(-9 * t)))) * np.exp(-1.6 * t)
    body = lp(noise(d, 'pink'), 1100) * np.exp(-3 * t)
    return (sub + 0.8 * body) * vel
def roar(d=2.0, vel=1.0):
    t = tvec(d)
    g = np.sin(2 * np.pi * (62 + 14 * np.sin(2 * np.pi * 9 * t)) * t) * 0.7 + 0.35 * np.sin(2 * np.pi * (124 + 20 * np.sin(2 * np.pi * 13 * t)) * t)
    n = bp(noise(d, 'brown'), 120, 700) * (0.6 + 0.4 * np.sin(2 * np.pi * 23 * t))
    x = (g + 0.9 * n) * env(len(t), 0.25, 0.7)
    return np.tanh(x * 2.2) * 0.6 * vel
def screech(d=1.4, vel=1.0):
    t = tvec(d); f = 900 + 500 * np.sin(2 * np.pi * 5 * t) - 300 * t
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) + 0.6 * bp(noise(d), 1500, 5000)
    return np.tanh(x * 1.5) * env(len(t), 0.05, 0.6) * 0.35 * vel
def buzz(d=0.7):
    t = tvec(d); return np.sign(np.sin(2 * np.pi * 110 * t)) * 0.25 * env(len(t), 0.005, 0.05)
def beep(f=1400, d=0.08): t = tvec(d); return np.sin(2 * np.pi * f * t) * env(len(t), 0.003, 0.02) * 0.3
def ping(): return bell(1568, 0.8, 0.7) + bell(2093, 0.8, 0.4)
def shutter():
    a = hp(noise(0.03), 2000) * 0.7; b = hp(noise(0.05), 1500) * 0.5
    return np.concatenate([a, np.zeros(int(0.05 * SR)), b])
def heartbeat():
    t = tvec(0.5); lub = np.sin(2 * np.pi * 55 * t) * np.exp(-14 * t)
    return np.concatenate([lub, np.zeros(int(0.12 * SR)), lub * 0.7])
def siren(d):
    t = tvec(d); f = np.where((t % 1.2) < 0.6, 880, 660)
    return lp(np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * 0.12, 2500)
def steps(d, rate=6.5):
    t = tvec(d); ph = (t * rate) % 1.0
    return lp(np.sin(2 * np.pi * 90 * t) * np.exp(-ph * 30) * (ph < 0.15), 600) * 0.8
def crowd_murmur(d):
    x = bp(noise(d), 250, 1800); m = 0.6 + 0.4 * np.sin(2 * np.pi * 0.7 * tvec(d)) * np.sin(2 * np.pi * 1.9 * tvec(d))
    return x * m * 0.25

# ---------------- MUSIC ----------------
def chord_seq(t0, chords, bar, cutoff=1300, gain=0.5, a=1.2, r=1.4):
    t = t0
    for c in chords:
        put(music, t, pad([note(n) for n in c], bar + r, cutoff, a, r), gain)
        t += bar
    return t
# HOOK 0-14: dark D minor tension + low pulse
chord_seq(0, [['D2', 'A2', 'F3'], ['D2', 'A2', 'F3'], ['A#1', 'F2', 'D3'], ['C2', 'G2', 'E3']], 3.5, 900, 0.55)
put(music, 0.0, pulse(note('D2'), 14, 2.0, 0.2), 0.35)
for tt in [0.0, 5.0, 9.5]: put(music, tt, drum(vel=0.9), 0.8)
# 14 - 31: melancholic (Dm - Bb - F - C)
chord_seq(14.05, [['D3', 'F3', 'A3'], ['A#2', 'D3', 'F3'], ['F2', 'A2', 'C3'], ['C3', 'E3', 'G3']], 4.2, 1100, 0.42)
for i, n in enumerate(['A4', 'F4', 'D4', 'F4', 'A4', 'C5', 'A4', 'G4']): put(music, 14.3 + i * 2.0, piano(note(n), 2.5, 0.8), 0.6)
put(music, 22.1, riser(3.3, 120, 900), 0.35)
put(music, 25.44, drum(vel=1.0), 0.9)
# 30.8 - 38.8 subscribe: warm major (F - C - Dm - Bb)
chord_seq(30.84, [['F3', 'A3', 'C4'], ['C3', 'E3', 'G3'], ['D3', 'F3', 'A3'], ['A#2', 'D3', 'F3']], 2.0, 1600, 0.38, 0.4, 0.8)
for i in range(16): put(music, 30.9 + i * 0.5, mallet(note(['F4', 'A4', 'C5', 'A4'][i % 4]), 1.0), 0.5)
# title 38.8: riser + hit
put(music, 37.3, riser(1.6, 200, 2500), 0.5)
put(sfx, 38.85, whoosh(0.7), 0.8)
put(music, 39.3, boom(2.5, 0.8), 0.7)
put(music, 39.3, bell(note('D5'), 3.5), 0.7)
# 40 - 82 world: mysterious (Dm add9) with mallet arpeggio
chord_seq(40.0, [['D3', 'A3', 'E4'], ['A#2', 'F3', 'C4'], ['G2', 'D3', 'A#3'], ['A2', 'E3', 'C#4']] * 2 + [['D3', 'A3', 'E4']] * 2, 4.2, 1000, 0.4)
arp = ['D4', 'A4', 'E5', 'A4']
for i in range(int((82 - 40) / 0.35)): put(music, 40.0 + i * 0.35, mallet(note(arp[i % 4]), 0.9, 0.55), 0.35, pan=0.3 * np.sin(i))
for i, tt in enumerate([59.29, 63.6, 67.8, 72.0, 76.2]):
    put(music, tt, drum(vel=0.6 + 0.12 * i, f0=60 - i * 5), 0.9)
put(music, 76.2, boom(5.5, 0.9), 0.6)
put(music, 76.2, pad([note('D1'), note('A1')], 6, 300, 1.0, 2.0), 0.9)
# 82 - 117 Bureau: grand, commercial (Bb - F - Gm - Eb - Bb - F - C)
chord_seq(82.22, [['A#2', 'D3', 'F3', 'A#3'], ['F2', 'A2', 'C3', 'F3'], ['G2', 'A#2', 'D3', 'G3'], ['D#2', 'G2', 'A#2', 'D#3'],
                  ['A#2', 'D3', 'F3', 'A#3'], ['F2', 'A2', 'C3', 'F3'], ['C3', 'E3', 'G3', 'C4'], ['F2', 'A2', 'C3', 'F3']], 4.3, 2000, 0.42, 0.6, 1.0)
for i in range(int((117 - 82.22) / 0.5)):
    put(music, 82.22 + i * 0.5, drum(0.4, 70, 60, 0.35) if i % 2 == 0 else hp(noise(0.06), 6000) * np.exp(-tvec(0.06) * 60) * 0.3, 0.6)
for i, tt in enumerate([104.9, 108.6, 109.9, 111.4, 113.3]): put(music, tt, bell(note(['F5', 'G5', 'A5', 'C6', 'F6'][i]), 2.5, 0.9), 0.6)
# 117 - 154 scanning: techy pulse
chord_seq(116.81, [['A2', 'E3', 'C4'], ['F2', 'C3', 'A3'], ['G2', 'D3', 'B3'], ['E2', 'B2', 'G#3']] * 2 + [['A2', 'E3', 'C4']], 4.2, 900, 0.36)
for i in range(int((150.9 - 116.81) / 0.25)): put(music, 116.81 + i * 0.25, pulse(note(['A3', 'E4', 'C4', 'E4'][i % 4]), 0.25, 4, 0.5), 0.12)
for tt, ok in [(135.4, 0), (139.4, 1), (143.2, 2)]:
    for k, n in enumerate([['C5', 'E5', 'G5'], ['D5', 'F#5', 'A5'], ['E5', 'G#5', 'B5', 'E6']][ok]): put(music, tt + k * 0.07, bell(note(n), 2.5, 0.8 + 0.2 * ok), 0.5)
put(music, 143.2, boom(2.5, 0.5), 0.5)
put(music, 150.88, drum(vel=0.8), 0.7)
# 154 - 230 flashback / sadness: soft piano progression (Dm - Bb - F - A)
prog = [['D3', 'F3', 'A3'], ['A#2', 'D3', 'F3'], ['F2', 'A2', 'C3'], ['A2', 'C#3', 'E3']]
t = 154.42
mel = ['A4', 'D5', 'C5', 'A4', 'F4', 'G4', 'A4', 'E4']
i = 0
while t < 230.8:
    c = prog[(i // 2) % 4]
    put(music, t, pad([note(n) for n in c], 3.2 + 1.5, 700, 1.0, 1.5), 0.3)
    for k, n in enumerate(c): put(music, t + k * 0.18, piano(note(n) * 2, 3.0, 0.6), 0.45)
    put(music, t + 1.6, piano(note(mel[i % len(mel)]), 2.5, 0.75), 0.5)
    t += 3.2; i += 1
# 230 - 245.7: hands get warm: swelling tension + heartbeat
put(music, 230.85, pad([note('D2'), note('A2'), note('D3'), note('E3')], 15, 600, 4.0, 1.5), 0.6)
put(music, 236.0, riser(9.5, 80, 700), 0.35)
for k in range(13): put(music, 232.0 + k * 1.05, heartbeat(), 0.8)
put(music, 244.45, boom(2.0, 0.8), 0.6)
# 245.7 - 310: station action
chord_seq(245.73, [['D2', 'A2', 'D3']], 3.8, 700, 0.3)
chord_seq(249.46, [['D2', 'G#2', 'D3'], ['C#2', 'G2', 'C#3']] * 2, 3.5, 800, 0.4)
action = [['D2', 'A2', 'F3'], ['A#1', 'F2', 'D3'], ['C2', 'G2', 'E3'], ['A1', 'E2', 'C#3']]
t = 256.55; i = 0
while t < 297.0:
    put(music, t, pad([note(n) for n in action[i % 4]], 3.2 + 1.2, 1500, 0.3, 1.0), 0.45)
    for b in range(8): put(music, t + b * 0.4, drum(0.35, 70, 60, 0.5 if b % 2 else 0.8), 0.55)
    for b in range(16): put(music, t + b * 0.2, pulse(note('D3') * (2 if b % 4 == 3 else 1), 0.2, 5, 0.4), 0.15)
    t += 3.2; i += 1
put(music, 297.0, pad([note('D1'), note('A1'), note('D2')], 13, 400, 1.5, 0.3), 0.8)  # slow-motion drone
put(music, 302.0, riser(8.5, 100, 3000), 0.6)
put(music, 309.6, boom(1.0, 1.0), 0.9)

# ---------------- SFX ----------------
put(sfx, 1.4, roar(2.4, 1.0), 0.9)
put(sfx, 0.0, siren(8), 0.15, pan=-0.5)
for k in range(28): put(sfx, 9.8 + k * 0.08, beep(900 + k * 35), 0.35)
put(sfx, 12.5, buzz(0.6), 0.6)
put(sfx, 22.1, steps(3.3, 6.5), 0.3)
put(sfx, 41.8, boom(5.5, 0.6), 0.6)
put(sfx, 41.8, lp(noise(5.6, 'brown'), 200) * env(int(5.6 * SR), 1.0, 1.0), 0.8)
put(sfx, 47.6, lp(noise(3.0), 3000) * env(int(3 * SR), 0.5, 1.0) * 0.3, 0.5)  # ember hiss
put(sfx, 53.0, roar(2.2, 0.9), 0.8)
put(sfx, 63.8, screech(1.0, 0.7), 0.6)
put(sfx, 72.2, roar(2.0, 0.7), 0.6)
put(sfx, 97.0, crowd_murmur(5.3), 0.5)
for k in range(8): put(sfx, 97.4 + k * 0.6 + rng.random() * 0.3, shutter(), 0.35, pan=rng.uniform(-0.7, 0.7))
put(sfx, 122.2, steps(4.5, 3.2), 0.4)
for k in range(60): put(sfx, 129.7 + k * 0.088, beep(800 + k * 12, 0.05), 0.25)
put(sfx, 170.6, beep(1200, 0.12), 0.4)
for k in range(18): put(sfx, 173.8 + k * 0.08, beep(800 + k * 30), 0.3)
put(sfx, 177.5, buzz(0.8), 0.7)
put(sfx, 185.2, shutter(), 0.8)
for tt in [188.6, 191.0, 193.3]: put(sfx, tt, ping(), 0.5)
put(sfx, 245.73, crowd_murmur(7.0), 0.6)
put(sfx, 245.9, steps(3.6, 2.8), 0.3)
put(sfx, 249.5, lp(noise(3.8, 'brown'), 160) * env(int(3.8 * SR), 1.5, 0.2), 1.0)
put(sfx, 253.2, boom(3.0, 1.2), 1.0)
put(sfx, 253.4, roar(1.5, 0.6) + screech(1.5, 0.8), 0.8)
put(sfx, 256.6, siren(54.0), 0.35, pan=0.3)
put(sfx, 257.0, screech(1.6, 1.0), 0.7)
put(sfx, 261.2, crowd_murmur(6.0) * 1.8, 0.7)
put(sfx, 261.3, steps(5.5, 9), 0.45)
put(sfx, 277.2, boom(2.0, 0.8), 0.9)
put(sfx, 277.25, hp(noise(0.8), 800) * np.exp(-tvec(0.8) * 5), 0.5)
put(sfx, 285.0, screech(2.0, 1.0), 0.8)
put(sfx, 289.6, drum(0.4, 90, 40, 0.5), 0.8)
for k in range(5): put(sfx, 289.75 + k * 0.11, drum(0.2, 160 + k * 20, 40, 0.25), 0.5)
put(sfx, 290.1, steps(2.0, 9), 0.55)
put(sfx, 292.2, whoosh(0.5), 0.6)
put(sfx, 297.0, whoosh(1.2), 0.4)
put(sfx, 305.0, riser(5.5, 300, 4000), 0.4)

# ---------------- reverb + write ----------------
ir_len = int(1.6 * SR); ir = rng.standard_normal(ir_len) * np.exp(-np.arange(ir_len) / SR * 3.2); ir /= np.sqrt(np.sum(ir ** 2))
for ch in range(2):
    music[:, ch] = 0.75 * music[:, ch] + 0.35 * fftconvolve(music[:, ch], ir)[:N]
    sfx[:, ch] = 0.85 * sfx[:, ch] + 0.15 * fftconvolve(sfx[:, ch], ir)[:N]
def norm(x, peak):
    m = np.max(np.abs(x)); return x / m * peak if m > 0 else x
music = norm(music, 0.6); sfx = norm(sfx, 0.85)
wavfile.write('music.wav', SR, (music * 32767).astype(np.int16))
wavfile.write('sfx.wav', SR, (sfx * 32767).astype(np.int16))
print('ok', music.shape)
