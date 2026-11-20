# synthesized SFX for EP01 Part 1 (2D version), aligned to the shot list
import numpy as np, soundfile as sf
from scipy.signal import butter, sosfilt
SR = 48000; DUR = 310.6; out = np.zeros(int(SR * DUR) + SR * 3)
rng = np.random.default_rng(1)
def bp(x, lo, hi): return sosfilt(butter(2, [lo, hi], 'bandpass', fs=SR, output='sos'), x)
def lp(x, f): return sosfilt(butter(2, f, 'lowpass', fs=SR, output='sos'), x)
def hp(x, f): return sosfilt(butter(2, f, 'highpass', fs=SR, output='sos'), x)
def put(t, x, g=1.0):
    i = int(t * SR); n = min(len(x), len(out) - i)
    if n > 0: out[i:i + n] += x[:n] * g
def env(n, a, d): e = np.ones(n); na = max(1, int(a * SR)); e[:na] = np.linspace(0, 1, na); e *= np.exp(-np.arange(n) / (d * SR)); return e
def noise(d): return rng.standard_normal(int(d * SR))
def tone(f, d, wave='sin'):
    tt = np.arange(int(d * SR)) / SR; ph = 2 * np.pi * (np.cumsum(f) / SR if hasattr(f, '__len__') else f * tt)
    return np.sin(ph) if wave == 'sin' else np.sign(np.sin(ph))
def boom(d=1.6, f0=60):
    n = int(d * SR); tt = np.arange(n) / SR; f = f0 * np.exp(-tt * 1.2)
    return (np.sin(2 * np.pi * np.cumsum(f) / SR) + .6 * lp(rng.standard_normal(n), 300)) * env(n, .005, d / 4)
def whoosh(d=.35, lo=400, hi=2500):
    n = int(d * SR); x = rng.standard_normal(n); f = np.linspace(lo, hi, n); y = np.zeros(n)
    for i in range(0, n, 2400): y[i:i + 2400] = bp(x[i:i + 2400], f[i], min(f[i] * 2.2, 20000))
    return y * np.sin(np.linspace(0, np.pi, n)) ** 2 * .7
def crash(d=1.4): n = int(d * SR); return bp(rng.standard_normal(n), 800, 6000) * env(n, .002, .25) * .8 + boom(d, 45)[:n] * .9
def pop(): n = int(.12 * SR); return tone(np.linspace(900, 300, n), .12) * env(n, .002, .04) * .5
def click(): n = 1800; return bp(rng.standard_normal(n), 2000, 8000) * env(n, .0005, .006) * .9
def shutter(): return np.concatenate([click(), np.zeros(int(.06 * SR)), click()])
def beep(f=1400, d=.12): n = int(d * SR); return tone(f, d) * env(n, .003, d / 2) * .35
def tick(): n = 600; return bp(rng.standard_normal(n), 3000, 9000) * env(n, .0003, .003) * .5
def ding(f=1760, d=1.0): n = int(d * SR); return (tone(f, d) + .4 * tone(f * 2.76, d)) * env(n, .002, .25) * .3
def thud(): n = int(.4 * SR); return (boom(.4, 90)[:n] + bp(rng.standard_normal(n), 200, 2000) * env(n, .001, .03)) * .9
def crowd(d, lo=300, hi=2400, rate=3.1):
    n = int(d * SR); x = bp(rng.standard_normal(n), lo, hi); am = 1 + .35 * np.sin(2 * np.pi * rate * np.arange(n) / SR)
    e = np.minimum(1, np.arange(n) / (.3 * SR)) * np.minimum(1, (n - np.arange(n)) / (.4 * SR)); return x * am * e * .25
def laugh(d, f0=220, rate=6.5):  # "ha ha" vowel bursts
    n = int(d * SR); tt = np.arange(n) / SR; v = np.sign(np.sin(2 * np.pi * f0 * (1 + .05 * np.sin(tt * 3)) * tt))
    v = bp(v, 500, 1400) * (np.maximum(0, np.sin(2 * np.pi * rate * tt)) ** 2); return v * .25
def ring(d=1.1):
    n = int(d * SR); tt = np.arange(n) / SR; s = np.sign(np.sin(2 * np.pi * 22 * tt)) * .5 + .5
    return (np.sin(2 * np.pi * 2100 * tt) + .5 * np.sin(2 * np.pi * 3300 * tt)) * s * .18
def sting(): n = int(1.6 * SR); tt = np.arange(n) / SR; cl = sum(np.sin(2 * np.pi * f * tt) for f in (146.8, 155.6, 207.7, 220)) * .12 * env(n, .01, .7); return boom(1.6, 50) + cl
def roar(d=1.2):
    n = int(d * SR); tt = np.arange(n) / SR; v = np.sign(np.sin(2 * np.pi * (70 + 20 * np.sin(tt * 30)) * tt))
    return (lp(v, 900) * .5 + bp(rng.standard_normal(n), 200, 1500) * .6) * np.sin(np.linspace(0, np.pi, n)) ** .5 * .8
def rumble(d): n = int(d * SR); return lp(rng.standard_normal(n), 120) * np.sin(np.linspace(0, np.pi, n)) * 1.6
def step(): n = int(.08 * SR); return lp(rng.standard_normal(n), 900) * env(n, .001, .02) * .6
def bark(): return np.concatenate([bp(tone(np.linspace(500, 380, int(.12 * SR)), .12, 'sq'), 400, 2500) * .4, np.zeros(int(.08 * SR)), bp(tone(np.linspace(520, 390, int(.12 * SR)), .12, 'sq'), 400, 2500) * .4])
def hiss(d=.8): n = int(d * SR); return hp(rng.standard_normal(n), 3000) * np.sin(np.linspace(0, np.pi, n)) * .3
def zap(): n = int(.5 * SR); return tone(np.linspace(1800, 300, n), .5, 'sq') * env(n, .002, .15) * .12 + hiss(.5) * .5
def whistle(): n = int(.7 * SR); tt = np.arange(n) / SR; return np.sin(2 * np.pi * (2600 + 140 * np.sign(np.sin(2 * np.pi * 28 * tt))) * tt) * env(n, .01, .4) * .18
def chord(fs, d=2.0, a=.3): n = int(d * SR); return sum(tone(f, d) for f in fs) * np.minimum(1, np.arange(n) / (a * SR)) * np.exp(-np.arange(n) / (d * .5 * SR)) * .1
def pluck(f, d=1.2):
    n = int(d * SR); L = int(SR / f); buf = rng.uniform(-1, 1, L); y = np.zeros(n)
    for i in range(n): y[i] = buf[i % L]; buf[i % L] = .5 * (buf[i % L] + buf[(i + 1) % L]) * .996
    return y * .3
def siren(d): n = int(d * SR); tt = np.arange(n) / SR; f = np.where(np.sin(2 * np.pi * .8 * tt) > 0, 960, 760); return bp(tone(f, d, 'sq'), 500, 3000) * .06
def heartbeat(): return np.concatenate([boom(.18, 60)[:int(.18 * SR)], np.zeros(int(.12 * SR)), boom(.2, 55)[:int(.2 * SR)] * .8])
def crackle(d, dens=40):
    n = int(d * SR); y = lp(rng.standard_normal(n), 400) * .15
    for t in rng.uniform(0, d, int(d * dens)): i = int(t * SR); y[i:i + 300] += bp(rng.standard_normal(300), 1500, 6000)[:max(0, min(300, n - i))] * .5
    return y * np.minimum(1, np.arange(n) / (.4 * SR))
def scribble(d): n = int(d * SR); return bp(rng.standard_normal(n), 1500, 5000) * (.5 + .5 * np.sin(2 * np.pi * 9 * np.arange(n) / SR)) * .2

# ---------- hook (0 - 14.05)
put(.15, ring(1.15), .8); put(.36, pop(), .8)
put(1.35, boom(2.0, 55), 1.0); put(1.33, crash(1.0), .35)
put(2.05, whoosh(.3), .6); put(2.3, boom(.8, 70), .7); put(2.85, boom(.8, 70), .7)
put(3.2, roar(.9), .8); put(3.52, whoosh(.22), .9); put(3.72, crash(1.6), 1.2); put(3.72, boom(2.2, 40), .8)
put(4.82, whoosh(.3), .6); put(4.95, crowd(2.5), 1.0)
for t in np.sort(rng.uniform(5.0, 7.3, 9)): put(t, click(), .6)
for (lt, a) in ((8.15, 7.6), (8.95, 8.4), (9.75, 9.2)):
    for t in np.arange(a, lt, 1 / 14): put(t, tick(), .5)
    put(lt, beep(1500), 1); put(lt + .02, pop(), .7)
for t in np.arange(11.3, 12.7, 1 / 10): put(t, tick(), .55)
put(12.74, sting(), 1.0)
for t in np.arange(12.85, 14.0, .5): put(t, beep(880, .2), .6)
# ---------- intro
put(14.05, crowd(2.8, 400, 1800, 5) + laugh(2.8, 240), .7)
put(16.95, whoosh(.3), .5); put(17.5, thud(), .9)
put(18.56, chord([523, 659, 784], 1.0, .01), 1.0)
put(19.87, laugh(2.2, 330, 7), .9)
put(22.10, chord([110, 165, 220], 3.3, 1.0), .8)
for t in (25.6, 25.9, 26.3): put(t, tone(np.linspace(3200, 4200, 2400), .05) * .1)
put(26.77, hp(noise(4.0), 400) * np.sin(np.linspace(0, np.pi, int(4.0 * SR))) * .12)
put(29.4, ding(2400, .8), .7)
for t in np.arange(30.9, 31.9, .4): put(t, step(), .8)
put(32.35, thud(), 1.0); put(32.45, ding(1320, 1.5), .9); put(33.0, pop(), .6)
put(34.73, whoosh(1.2, 200, 3000), .8); put(37.13, whoosh(.6, 300, 4000), 1.0)
put(38.80, boom(1.5, 50), 1.0); put(38.85, pop(), .8); put(39.1, pop(), .8)
# ---------- world
put(39.97, chord([196, 247, 294], 2.5, .2), .6)
put(42.85, rumble(.6), 1.0); put(43.35, crash(1.4), 1.1)
put(44.54, rumble(2.4) * .5 + chord([98, 147], 2.4, .5), .8)
put(46.95, scribble(1.4), .8)
put(49.27, crowd(2.3, 500, 3000, 4), 1.0)
for t in (51.7, 52.4, 53.0): put(t, bark(), .8)
put(51.9, hiss(.5), .8)
for t in (53.9, 55.15): put(t, boom(.9, 50), .9)
for i in range(5): put(55.82 + i * .5, beep(600 + i * 200, .15), .8)
put(59.39, pop(), .7); put(61.7, whoosh(.3), .7); put(62.0, thud(), .8)
put(63.59, pop(), .7); put(65.0, crash(1.0), .9); put(66.55, thud(), 1.0)
put(67.48, pop(), .7); put(68.0, boom(2.0, 38), 1.2); put(68.0, crash(1.4), .5)
put(69.76, pop(), .7); put(70.26, roar(1.6), .9)
put(72.43, rumble(4.6), 1.0); put(73.0, pop(), .5)
put(79.2, scribble(.8), 1.0); put(80.0, pop(), .6)
put(82.22, chord([392, 494, 587, 784], 2.0, .05), .9)
put(84.24, crowd(5.2, 1500, 5000, 9) * .4)
for t in (89.47, 90.47, 91.47): put(t, pop(), .8)
put(92.69, ding(2637, 1.0), .5); put(93.4, ding(2093, 1.0), .7)
for t in (95.64, 96.99, 98.29): put(t, pop(), .8)
put(99.54, crowd(2.8), 1.0)
for t in np.sort(rng.uniform(99.6, 102.2, 6)): put(t, click(), .6)
for i in range(5): put(102.52 + i * .3 + .4, ding(1200 + i * 150, .5), .5)
put(104.9, whistle(), 1.0); put(106.0, whistle(), .8)
put(108.7, zap(), 1.0); put(108.9, zap(), 1.0); put(109.3, whoosh(.8), .6)
for t in np.sort(rng.uniform(111.1, 113.6, 7)): put(t, click(), .7)
put(113.76, chord([261, 329, 392, 523], 3.0, .8), 1.0)
for t in (117.21, 118.01, 118.81): put(t, pop(), .8)
put(123.75, hp(noise(.5), 300) * env(int(.5 * SR), .05, .2) * .5); put(124.3, crash(.4), .2); put(124.3, pop(), .8)
for t in np.arange(125.5, 128.8, .38): put(t, step(), .7)
put(129.05, beep(1300, .2), .9)
put(130.69, whoosh(3.6, 200, 3000) * .6)
for (t0, land) in ((135.40, 136.0), (139.64, 140.24), (142.71, 143.31)):
    for t in np.arange(t0 - .1, land, 1 / 14): put(t, tick(), .5)
    put(land, beep(1500), 1); put(land + .02, pop(), .7); put(land + .2, pop(), .5)
for t in np.sort(rng.uniform(140.3, 142.3, 5)): put(t, click(), .6)
put(144.31, ding(2093, 1.5), .9)
put(151.03, thud(), .8); put(152.78, pop(), .7)
# ---------- flashback
put(154.42, whoosh(.8, 3000, 300), .6)
put(160.0, ding(2637, 1.0), .7)
put(163.83, scribble(3.4), .7); put(167.43, pop(), .7); put(168.0, ding(2093, .8), .5)
put(170.35, beep(1300, .25), .8)
for i in range(3): put(173.6 + i * .3, beep(500 + i * 150, .12), .8)
put(175.8, tone(110, .6, 'sq') * env(int(.6 * SR), .01, .3) * .15)
put(177.47, sting(), 1.1)
put(178.49, pop(), .7); put(178.84, scribble(.25), 1); put(179.58, pop(), .7); put(179.93, scribble(.25), 1); put(180.2, thud(), 1.0)
put(180.83, laugh(2.0, 180, 6), 1.3)
put(187.18, shutter(), 1.0)
for i in range(6): put(188.45 + i * .25, ding(1568 + (i % 2) * 400, .4), .5)
put(189.95, whoosh(.5), .7); put(190.45, thud(), .6)
for i, f in enumerate((196, 247, 294, 196, 247, 330, 196, 247)): put(191.6 + i * .48, pluck(f), .9)
put(197.7, thud(), 1.0)
for t in np.arange(203.5, 205.5, .06): put(t, tick(), .4)
put(205.5, tone(220, .4, 'sq') * env(int(.4 * SR), .01, .2) * .12)
# ---------- daily life
put(207.89, crowd(3.2, 300, 1500, 2) * .4); put(208.7, whoosh(.2), .4)
put(211.11, crowd(2.7, 100, 800, 1) * .5)
for t in np.arange(211.2, 213.7, .45): put(t, step(), .5)
put(214.8, tone(np.linspace(1400, 2600, int(.35 * SR)), .35, 'sq') * .06 * env(int(.35 * SR), .01, .2)); put(214.85, scribble(.2), 1.2)
for t in np.arange(215.7, 217.4, .1): put(t, tick(), .6)
put(217.43, crowd(5.4, 600, 2500, 6) * .5)
for t in np.arange(217.5, 222.8, .45): put(t, step(), .5)
for t in np.arange(226.2, 230.8, .42): put(t, step(), .5)
put(230.85, (bp(noise(5.3), 3500, 5000) * (np.sin(2 * np.pi * 14 * np.arange(int(5.3 * SR)) / SR) > .3)) * .05)
put(236.13, crackle(6.4, 12), .8)
for t in (242.6, 243.4, 244.2): put(t, heartbeat(), .9)
put(244.45, boom(1.2, 45), .8)
# ---------- station
put(245.73, crowd(2.3, 200, 1200, 1) * .5)
for t in np.arange(245.8, 247.9, .42): put(t, step(), .5)
put(247.97, rumble(1.5), 1.0); put(249.46, rumble(1.2) + whoosh(1.2, 100, 900), 1.0)
put(250.66, crash(2.5), 1.4); put(250.66, boom(3.0, 35), 1.2)
put(254.52, rumble(2.0) * .5); put(255.3, hiss(1.0), .6)
put(256.55, rumble(1.2), 1.0); put(257.6, roar(1.8), 1.1)
put(259.63, beep(880, .3), .6); put(260.1, beep(880, .3), .6)
put(261.16, siren(19.5), 1.0)
put(263.62, crowd(3.5, 500, 3000, 4), 1.0)
put(268.0, thud(), .8); put(268.3, tone(np.linspace(800, 400, 4800), .1) * .05)
put(270.0, ding(1760, .6), .8)
for t in np.arange(271.5, 272.9, 1.0): put(t, tick(), 1.0)
for t in np.arange(273.0, 276.6, .8): put(t, heartbeat(), 1.0)
put(277.2, crash(1.6), 1.2); put(279.0, crash(1.6), 1.2)
put(281.0, hiss(1.5), .8); put(282.5, roar(1.0), .5)
put(284.27, tone(np.linspace(900, 1100, int(1.3 * SR)), 1.3) * .02)
put(285.9, roar(2.4) * .7 + hiss(2.4), 1.0)
for t in np.arange(288.6, 292.1, .22): put(t, step(), .9)
put(288.58, whoosh(3.5, 300, 1500) * .5)
put(292.11, whoosh(.6, 300, 3000), 1.0); put(293.41, thud(), 1.1)
put(294.09, whoosh(3.0, 120, 600) * .8); put(295.9, rumble(1.3), .8)
put(297.18, heartbeat(), 1.0); put(298.2, heartbeat(), 1.0); put(299.2, heartbeat(), 1.0)
put(305.0, crackle(4.0, 30), 1.0); put(306.85, whoosh(2.0, 200, 5000), .9)
put(308.84, crash(1.0), 1.5); put(308.84, boom(1.5, 38), 1.5); put(308.84, crackle(1.1, 120) * 1.5)
o = out[:int(SR * DUR)]
cut = int(309.95 * SR); o[cut:] *= np.exp(-np.arange(len(o) - cut) / (.05 * SR))
sf.write('out/sfx_part1.wav', (o * .9).astype(np.float32), SR)
print('ok', np.abs(o).max())
