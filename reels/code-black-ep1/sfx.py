"""SFX + original horror score for Code Black: Oakridge High, Episode 1, mixed with out/dialogue.wav
-> out/mix.wav (two-pass loudnorm to -14 LUFS, -1.5 dBTP). Everything is synthesised here (royalty-free). Timings mirror scene.js."""
import os, json, subprocess
import numpy as np
import soundfile as sf
from scipy import signal

HERE = os.path.dirname(os.path.abspath(__file__))
SR = 48000; DUR = 90.0; N = int(SR * DUR)
t = np.arange(N) / SR
rng = np.random.default_rng(31)
L = np.zeros(N); R = np.zeros(N); ML = np.zeros(N); MR = np.zeros(N)   # sfx bus, music bus
FREEZE = 78.6; T_BOOM = 9.4; T_FEED = 12.3; T_LOCK = 25.2; T_DARK = 25.8; T_GRAB = 26.1; T_HANDLE = 36.0; T_TAP = 49.0; T_WRIST = 56.6; T_STING = 62.0; T_CHARGE = 66.0

def sos(kind, f, order=4): return signal.butter(order, f, btype=kind, fs=SR, output='sos')
def bp(x, lo, hi, o=2): return signal.sosfilt(sos('band', [lo, hi], o), x)
def lp(x, f, o=4): return signal.sosfilt(sos('low', f, o), x)
def hp(x, f, o=4): return signal.sosfilt(sos('high', f, o), x)
def db(x): return 10 ** (x / 20)
def noise(n): return rng.standard_normal(n)
def env_ar(n, a, r):
    e = np.ones(n); a = max(1, min(int(a * SR), n)); r = max(1, min(int(r * SR), n))
    e[:a] = np.linspace(0, 1, a); e[-r:] *= np.linspace(1, 0, r); return e
def expdec(n, k): return np.exp(-np.linspace(0, k, n))
def seg(a, b): return np.clip((t - a) / (b - a), 0, 1)
def place(st, clip, g=1.0, pan=0.0, bus='sfx'):
    BL, BR = (L, R) if bus == 'sfx' else (ML, MR)
    i = int(st * SR)
    if i >= N or i + len(clip) <= 0: return
    if i < 0: clip = clip[-i:]; i = 0
    n = min(len(clip), N - i)
    BL[i:i + n] += clip[:n] * g * np.sqrt(0.5 * (1 - pan)) * 1.414
    BR[i:i + n] += clip[:n] * g * np.sqrt(0.5 * (1 + pan)) * 1.414
def whoosh(dur, lo=300, hi=2500, g=-27):
    n = int(SR * dur); return bp(noise(n), lo, hi) * np.sin(np.linspace(0, np.pi, n)) ** 2 * db(g)
def impact(dur, f0, g, bright=0.5):
    n = int(SR * dur); tt = np.arange(n) / SR
    return (np.sin(2 * np.pi * f0 * tt * (1 - 0.3 * tt / dur)) * np.exp(-tt * 18) + hp(noise(n), 1500) * np.exp(-tt * 60) * bright) * db(g)
def step(g, wet=True):
    n = int(SR * 0.1); tt = np.arange(n) / SR
    return (bp(noise(n), 300, 3500) * np.exp(-tt * 55) + bp(noise(n), 2500, 8000) * np.exp(-tt * 22) * (0.8 if wet else 0)) * db(g)
def breath(dur, g, lo=500, hi=3500):
    n = int(SR * dur); return bp(noise(n), lo, hi) * np.sin(np.linspace(0, np.pi, n)) ** 1.5 * db(g)
def reverb(x, sec=1.6, wet=0.35, seed=1):
    r = np.random.default_rng(seed); n = int(SR * sec); ir = r.standard_normal(n) * np.exp(-np.linspace(0, 7, n)); ir = lp(ir, 5000); ir[0] = 0
    y = signal.fftconvolve(x, ir)[:len(x) + n] ; y = y / (np.max(np.abs(y)) + 1e-9) * np.max(np.abs(x))
    out = np.zeros(len(y)); out[:len(x)] += x; return out + y * wet



frz = seg(FREEZE, FREEZE + 0.05)
dark = seg(T_DARK, T_DARK + 0.1)
# ---------------------------------------------------------------- room tone: AC hum, distant hallway chatter (stops at the BOOM), pages, typing
ac = (lp(noise(N), 300) * 0.6 + np.sin(2 * np.pi * 120 * t) * 0.05) * db(-30) * (1 - 0.8 * frz)
L += ac; R += ac
chat = bp(noise(N), 300, 2500) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.7 * t) * np.sin(2 * np.pi * 1.9 * t)) * db(-36) * (1 - seg(T_BOOM, T_BOOM + 0.6))
L += chat * 0.8; R += chat
for st in (0.8, 3.6, 6.2): n = int(SR * 0.4); place(st, bp(noise(n), 2000, 8000) * np.sin(np.linspace(0, np.pi, n)) ** 2, db(-28), rng.uniform(-.4, .4))   # page turns
for k in range(40):
    st = rng.uniform(0, 9.0); n = int(SR * 0.025); place(st, hp(noise(n), 2500) * expdec(n, 10), db(-34), 0.5)                                           # laptop typing
for k in range(14): place(0.4 + k * 0.62, hp(noise(int(SR * 0.02)), 3000) * expdec(int(SR * 0.02), 9), db(-34), -0.1)                                  # pen clicks/spins
# ---------------------------------------------------------------- the BOOM, the PA takeover
n = int(SR * 3.0); tt = np.arange(n) / SR
boom = lp(np.sin(2 * np.pi * 38 * tt) * np.exp(-tt * 2.2) + noise(n) * np.exp(-tt * 3.5) * 0.6, 450)
place(T_BOOM, boom, db(0)); place(T_BOOM + 0.05, bp(noise(int(SR * 1.2)), 2000, 7000) * expdec(int(SR * 1.2), 5), db(-24))      # rattle of pens/laptops
n = int(SR * 0.9); tt = np.arange(n) / SR
feed = (np.sin(2 * np.pi * (2400 + 900 * tt) * tt) + 0.5 * np.sin(2 * np.pi * 3700 * tt)) * env_ar(n, 0.02, 0.2)
place(T_FEED, feed, db(-13), -0.5)                                                                                              # PA feedback SCREECH
hum = (np.sin(2 * np.pi * 60 * t) + 0.4 * np.sin(2 * np.pi * 180 * t)) * seg(T_FEED, T_FEED + 0.1) * (1 - seg(21.9, 22.1)) * db(-34); L += hum * 1.2; R += hum * 0.6
# ---------------------------------------------------------------- panic: chairs, the deadbolt, the lights, the grab
for k in range(9): st = 22.4 + rng.uniform(0, 1.4); n = int(SR * 0.4); tt = np.arange(n) / SR; place(st, np.sin(2 * np.pi * rng.uniform(300, 700) * tt) * bp(noise(n), 400, 3000) * np.exp(-tt * 6), db(-22), rng.uniform(-.6, .6))   # chairs scraping
for k in range(10): place(22.4 + k * 0.26, step(-22, False), pan=-0.3 - 0.04 * k)                                                     # librarian running
for k in range(4): place(22.6 + rng.uniform(0, 2), breath(0.3, -26, 600, 4000), pan=rng.uniform(-.5, .5))                             # gasps
n = int(SR * 0.4); tt = np.arange(n) / SR
place(T_LOCK, (hp(noise(n), 1500) * np.exp(-tt * 60) + np.sin(2 * np.pi * 900 * tt) * np.exp(-tt * 30) * 0.5 + np.sin(2 * np.pi * 140 * tt) * np.exp(-tt * 25)), db(-8), -0.6)   # CLANK
n = int(SR * 0.08); place(T_DARK, hp(noise(n), 2000) * expdec(n, 12), db(-16), -0.6); place(T_DARK + 0.05, impact(0.4, 50, -18, 0.2))    # light switch, power-down thunk
place(T_GRAB - 0.1, whoosh(0.35, 400, 4000, -16)); place(T_GRAB + 0.1, impact(0.3, 90, -14, 0.4))
for k in range(5): place(26.4 + k * 0.32, step(-18, False))
place(27.6, bp(noise(int(SR * .5)), 300, 2500) * np.sin(np.linspace(0, np.pi, int(SR * .5))), db(-20))                               # sliding down behind the shelf
for k in range(12): place(28.4 + k * 0.9, breath(0.5, -25, 400, 2500))
# ---------------------------------------------------------------- the hallway: tactical boots, radio static, the handle
for k in range(int((34.4 - 29.3) / 0.42)):
    st = 29.3 + k * 0.42; g = -15 if 30.5 < st < 33 else -21
    place(st, lp(impact(0.2, 85, g, 0.3), 1800), pan=-0.7); place(st + 0.03, lp(impact(0.2, 80, g - 3, 0.3), 1800), pan=-0.75)
for k in range(9): place(33.6 + k * 0.42, lp(impact(0.2, 85, -18, 0.3), 1800), pan=-0.7)
def radio_burst(dur, g):
    n = int(SR * dur); return bp(noise(n), 1200, 4000) * env_ar(n, 0.01, 0.05) * (0.7 + 0.3 * np.sign(np.sin(2 * np.pi * 47 * np.arange(n) / SR))) * db(g)
for st in (30.6, 31.9, 37.2, 39.5): place(st, radio_burst(0.25, -22), pan=-0.7)
n = int(SR * 0.6); tt = np.arange(n) / SR
click = np.zeros(n); i1 = int(0.32 * SR)
click[:int(0.08 * SR)] += hp(noise(int(0.08 * SR)), 2500) * expdec(int(0.08 * SR), 10); click[i1:i1 + int(0.1 * SR)] += hp(noise(int(0.1 * SR)), 2000) * expdec(int(0.1 * SR), 9)
place(T_HANDLE, click + np.sin(2 * np.pi * 1300 * tt) * np.exp(-tt * 20) * 0.2, db(-6), -0.6)                                       # CLICK-CLACK
place(T_HANDLE + 0.35, impact(0.25, 120, -16, 0.2), pan=-0.6)                                                                       # the door thumps against the bolt
# ---------------------------------------------------------------- the back door: taps, the grab, the monitor, the charge, pounding
for k in range(int((48.4 - 45.5) * 5)): place(45.5 + k / 5, step(-17, False), pan=0.1 if k % 2 else -0.1)
for k in range(int((48.4 - 45.5) / 0.35)): place(45.5 + k * 0.35, breath(0.25, -20, 400, 3000))
for st in np.arange(T_TAP, 55.6, 0.62):
    for j in range(3): place(st + j * 0.12, lp(impact(0.12, 260, -18, 0.6), 2500))                                                  # tap-tap-tap on steel
n = int(SR * 0.3); place(55.6, hp(noise(n), 1500) * expdec(n, 8) * 0.4 + 0, db(-22))                                                    # hand on the cold bar
place(T_WRIST - 0.1, whoosh(0.3, 400, 4000, -17)); place(T_WRIST, impact(0.2, 140, -14, 0.3))
place(60.7, whoosh(0.5, 300, 2500, -24))
n = int(SR * 6.0); place(61.0, (bp(noise(n), 3000, 9000) * 0.4 + np.sin(2 * np.pi * 15734 / 2 * np.arange(n) / SR) * 0.02) * env_ar(n, 0.3, 0.6), db(-30))   # monitor hiss/whine
place(66.4, whoosh(0.35, 400, 4500, -17)); place(67.5, whoosh(0.35, 400, 4500, -17))
for st in np.arange(T_CHARGE + 0.3, FREEZE, 1 / 2.2): n = int(SR * 0.06); tt = np.arange(n) / SR; place(st, np.sin(2 * np.pi * 2200 * tt) * env_ar(n, 0.005, 0.02), db(-24), -0.6)   # charge beeping
for st in np.arange(67.4, FREEZE, 0.48): place(st, lp(impact(0.35, 70, -6, 0.7), 2400)); place(st + 0.01, bp(noise(int(SR * .25)), 1500, 5000) * expdec(int(SR * .25), 9), db(-18))   # pounding on steel
# ---------------------------------------------------------------- SCORE (original, made in code)
def mtof(m): return 440 * 2 ** ((m - 69) / 12)
def saw(f, n): ph = (np.arange(n) / SR * f) % 1.0; return 2 * ph - 1
def braam(g, dur=3.5, root=26):
    n = int(SR * dur); tt = np.arange(n) / SR
    x = sum(saw(mtof(root + iv), n) * (1 + 0.003 * k) for k, iv in enumerate((0, 7, 12, 13)))
    return lp(x, 900) * np.exp(-tt * 0.9) * env_ar(n, 0.02, 1.0) * db(g) + np.sin(2 * np.pi * 36 * tt) * np.exp(-tt * 1.5) * db(g + 4)
# calm study-hall piano-ish plucks (cut by the BOOM)
for k, st in enumerate(np.arange(0.2, T_BOOM, 0.8)):
    m = [64, 67, 71, 69, 67, 64, 62, 64, 67, 72, 71][k % 11]; n = int(SR * 1.2); tt = np.arange(n) / SR
    place(st, (np.sin(2 * np.pi * mtof(m) * tt) + 0.3 * np.sin(4 * np.pi * mtof(m) * tt)) * np.exp(-tt * 3) * db(-30), bus='mus')
place(T_BOOM, braam(-12, 3.0, 26), bus='mus')
drone = lp(sum(np.sin(2 * np.pi * mtof(m) * t + i) for i, m in enumerate((26, 33, 38, 39))), 450) * seg(12.5, 14) * (1 - seg(22.2, 22.5)) * db(-25); ML += drone; MR += drone
# panic: 150 bpm pulse + taiko during the scramble
beat = 60 / 150; st = 22.4; k = 0
while st < 28.4:
    n = int(SR * beat * 0.45); place(st, lp(saw(mtof([33, 33, 45, 36][k % 4]), n), 900) * env_ar(n, 0.01, 0.1) * db(-18), bus='mus')
    if k % 4 == 0: n = int(SR * .3); tt = np.arange(n) / SR; place(st, np.sin(2 * np.pi * 52 * tt * (1 - tt)) * np.exp(-tt * 13), db(-13), bus='mus')
    st += beat * 0.5; k += 1
# hiding: heartbeat pulse + high cluster as the men pass; dread swells on the handle
for st in np.arange(28.6, 45.4, 0.9): n = int(SR * .4); tt = np.arange(n) / SR; place(st, lp(np.sin(2 * np.pi * 48 * tt) * np.exp(-tt * 18), 200), db(-16), bus='mus')
cl = sum(np.sin(2 * np.pi * mtof(m) * t + i) for i, m in enumerate((81, 82, 88))) * seg(29.5, 31) * (1 - seg(44.8, 45.4)) * db(-37); ML += cl; MR += cl
place(T_HANDLE, braam(-15, 2.5, 29), bus='mus')
# Chloe at the door: tense strings; the monitor reveal: violin sting + braam
str_ = lp(sum(saw(mtof(m) * (1 + 0.002 * i), N) for i, m in enumerate((57, 58, 63))), 2200) * seg(49, 51) * (1 - seg(61.8, 62.0)) * db(-30); ML += str_; MR += str_ * 0.9
n = int(SR * 1.6); tt = np.arange(n) / SR
viol = sum(saw(mtof(m) * (1 + 0.004 * np.sin(2 * np.pi * 6 * tt)), n) for m in (88, 89, 94)) * np.exp(-tt * 1.8) * env_ar(n, 0.01, 0.4)
place(T_STING, hp(viol, 1500) * db(-17), bus='mus'); place(T_STING, braam(-10, 4.0, 25), bus='mus')
creep = lp(sum(saw(mtof(m) * (1 + 0.003 * i), N) for i, m in enumerate((36, 43, 48, 49))), 700) * seg(62, 64) * (1 - seg(78.5, 78.65)) * db(-27); ML += creep; MR += creep
n = int(SR * (FREEZE - 70.0)); tt = np.arange(n) / SR
place(70.0, lp(saw(55 * 2 ** (tt / tt[-1] * 2.0), n) + bp(noise(n), 800, 6000) * (tt / tt[-1]) * 0.8, 3000) * (tt / tt[-1]) ** 1.6 * db(-18), bus='mus')
# freeze: hard stop, deep hit, cold pad + loud heartbeat
n = int(SR * 3.5); tt = np.arange(n) / SR; place(FREEZE, np.sin(2 * np.pi * 36 * tt) * np.exp(-tt * 1.4) * 1.2 + lp(noise(n), 300) * np.exp(-tt * 3) * 0.4, db(-5), bus='mus')
n = int(SR * (DUR - FREEZE - 0.6)); tt = np.arange(n) / SR
place(FREEZE + 0.6, lp(sum(np.sin(2 * np.pi * mtof(m) * tt + i) for i, m in enumerate((45, 52, 57, 60))), 1200) * env_ar(n, 1.5, 2.0) * db(-25), bus='mus')
def heartbeat(g):
    n = int(SR * 0.55); tt = np.arange(n) / SR
    b = lambda d: np.where(tt >= d, np.sin(2 * np.pi * 52 * (tt - d)) * np.exp(-(tt - d) * 16), 0)
    return lp(b(0) + 0.75 * b(0.17), 200) * db(g)
for st in np.arange(FREEZE + 0.3, DUR - 0.6, 0.95): place(st, heartbeat(-9), bus='mus')
L *= (1 - 0.85 * frz); R *= (1 - 0.85 * frz)

# ---------------------------------------------------------------- mix with dialogue (duck sfx + music under voices)
dlg, sr = sf.read(os.path.join(HERE, 'out', 'dialogue.wav'), always_2d=True)
dlg = dlg[:N]; dlg = np.pad(dlg, ((0, N - len(dlg)), (0, 0)))
denv = signal.sosfilt(sos('low', 6, 2), np.abs(dlg.mean(1))); denv = np.clip(denv / (denv.max() + 1e-9) * 6, 0, 1)
duck_s = 1 - 0.35 * denv; duck_m = 1 - 0.5 * denv
mix = np.stack([L * duck_s * db(-2) + ML * duck_m * db(-1) + dlg[:, 0] * db(2.0), R * duck_s * db(-2) + MR * duck_m * db(-1) + dlg[:, 1] * db(2.0)], 1)
mix *= 0.9 / np.max(np.abs(mix))
fade = np.clip((DUR - t) / 0.5, 0, 1)[:, None] * np.clip(t / 0.1, 0, 1)[:, None]
raw = os.path.join(HERE, 'out', 'mix_raw.wav'); sf.write(raw, (mix * fade).astype(np.float32), SR, subtype='PCM_24')
comp = os.path.join(HERE, 'out', 'mix_comp.wav')
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', raw, '-af', 'acompressor=threshold=0.12:ratio=3:attack=4:release=160:makeup=1.6,alimiter=limit=0.89:attack=2:release=60', comp], check=True)
meas = subprocess.run(['ffmpeg', '-hide_banner', '-i', comp, '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json', '-f', 'null', '-'], capture_output=True, text=True).stderr
m = json.loads(meas[meas.rindex('{'):meas.rindex('}') + 1])
af = (f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}"
      f":measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', comp, '-af', af, '-ar', '48000', os.path.join(HERE, 'out', 'mix.wav')], check=True)
print('wrote out/mix.wav')
