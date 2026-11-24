"""SFX + original horror score for Season 2 Episode 1 (Into the Woods), mixed with out/dialogue.wav
-> out/mix.wav (two-pass loudnorm to -14 LUFS, -1.5 dBTP). Everything is synthesised here (royalty-free). Timings mirror scene.js."""
import os, json, subprocess
import numpy as np
import soundfile as sf
from scipy import signal

HERE = os.path.dirname(os.path.abspath(__file__))
SR = 48000; DUR = 92.0; N = int(SR * DUR)
t = np.arange(N) / SR
rng = np.random.default_rng(31)
L = np.zeros(N); R = np.zeros(N); ML = np.zeros(N); MR = np.zeros(N)   # sfx bus, music bus
FREEZE = 80.4; T_TRIP = 10.0; T_KICK = 19.0; T_SLAM = 20.5; T_BUZZ = 25.4; T_FLASH = 35.5; T_GRAB = 45.3; T_STING = 53.4; T_WHIP = 62.0; BANGS = [71.5, 72.2, 72.9, 74.8, 76.2]

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
inside = seg(19.6, 20.6)
# ---------------------------------------------------------------- ambience: rain on leaves outside, on the roof inside; wind; distant sirens
for buf, s_ in ((L, 1), (R, 2)):
    nz = np.random.default_rng(s_).standard_normal(N)
    leaves = (lp(hp(nz, 300), 4200) * 0.9 + bp(nz, 3000, 9000) * 0.3) * (1 + 0.15 * np.sin(2 * np.pi * 0.21 * t + s_))
    roof = lp(hp(nz, 150), 1400) * (1 + 0.25 * np.abs(np.sin(2 * np.pi * 0.37 * t + s_)))
    buf += leaves * db(-19) * (1 - inside) * (1 - 0.8 * frz) + roof * db(-21) * inside * (1 - 0.7 * frz)
    for _ in range(int(DUR * 50)):
        st = rng.uniform(0, FREEZE); ln = int(SR * 0.012); d = rng.standard_normal(ln) * expdec(ln, 9); i = int(st * SR)
        buf[i:i + ln] += bp(d, 1500, 6000)[:max(0, min(ln, N - i))] * db(-28 + rng.uniform(-6, 4)) * (0.5 if st > 19.6 else 1)
wind = lp(noise(N), 500) * (1 + 0.5 * np.sin(2 * np.pi * 0.09 * t)) * db(-24) * (1 - 0.6 * inside) * (1 - frz)
L += wind; R += wind * 0.9
sir_f = np.where((t * 1.5) % 1 < 0.5, 760.0, 980.0); sir_f = lp(sir_f, 12, 2)
siren = np.sin(2 * np.pi * np.cumsum(sir_f) / SR) * np.interp(t, [0, 8, 16, 20, 92], [1.0, 0.6, 0.15, 0.0, 0.0])
siren = lp(siren, 2500) * db(-24); L += siren * 0.7; R += siren * 0.9
# ---------------------------------------------------------------- Scene 1: shoved through the woods, the trip
for k in range(int(T_TRIP * 5.4)):
    st = k / 5.4; place(st, step(-12), pan=0.12 if k % 2 else -0.12); place(st + 0.09, step(-17), pan=0.0)   # our steps + Sam's
for k in range(int((T_TRIP) / 0.36)): place(k * 0.36, breath(0.26, -18 if k % 2 else -21, 400, 3200))
for st in (2.6, 6.0, 8.4): place(st, bp(noise(int(SR * .35)), 1500, 7000) * np.sin(np.linspace(0, np.pi, int(SR * .35))), db(-20), rng.uniform(-.4, .4))   # branches whipping
place(5.4, whoosh(0.35, 400, 4000, -22)); place(7.0, whoosh(0.35, 400, 4000, -22))
place(T_TRIP, whoosh(0.4, 200, 2000, -16)); place(T_TRIP + 0.38, impact(0.4, 70, -6, 0.7))
place(T_TRIP + 0.4, bp(noise(int(SR * .6)), 400, 5000) * expdec(int(SR * .6), 5), db(-12))          # splat into the mud
for k in range(8): place(T_TRIP + 0.6 + k * 0.3, breath(0.24, -16, 400, 3000))
for k in range(int((18.9 - 12.6) * 4.2)): place(12.6 + k / 4.2, step(-13), pan=0.1 if k % 2 else -0.1)
# ---------------------------------------------------------------- Scene 2: the cabin
place(T_KICK, impact(0.6, 75, -3, 0.9)); place(T_KICK + 0.05, bp(noise(int(SR * .5)), 600, 4000) * expdec(int(SR * .5), 6), db(-12))   # door kicked in
n = int(SR * 0.9); tt = np.arange(n) / SR; place(T_KICK + 0.1, np.sin(2 * np.pi * (220 + 160 * np.sin(tt * 9)) * tt) * bp(noise(n), 300, 1500) * np.exp(-tt * 2) * 0.6, db(-18))   # creak
for k in range(4): place(19.4 + k * 0.25, step(-15, False))
place(T_SLAM, impact(0.7, 60, -2, 1.0)); place(T_SLAM + 0.02, bp(noise(int(SR * .4)), 2000, 8000) * expdec(int(SR * .4), 6), db(-18))   # SLAM
n = int(SR * 0.25); tt = np.arange(n) / SR
clack = (hp(noise(n), 2000) * np.exp(-tt * 120) + np.sin(2 * np.pi * 1900 * tt) * np.exp(-tt * 40) * 0.5 + np.sin(2 * np.pi * 180 * tt) * np.exp(-tt * 30))
place(T_SLAM + 0.33, bp(noise(int(SR * .15)), 1500, 6000) * np.linspace(0.3, 1, int(SR * .15)), db(-20)); place(T_SLAM + 0.48, clack, db(-6))   # bolt slides — CLACK
for k in range(5): place(22.3 + k * 0.28, bp(noise(int(SR * .18)), 300, 2500) * np.sin(np.linspace(0, np.pi, int(SR * .18))), db(-22))   # sliding down the wall
for k in range(14): place(23.8 + k * 0.78, lp(step(-20, False), 1600), pan=-0.3 + 0.04 * (k % 5))    # Sam pacing on floorboards
for k in range(10): n = int(SR * 0.6); tt = np.arange(n) / SR; place(21.0 + k * 1.37 + rng.uniform(0, .3), np.sin(2 * np.pi * (180 + 60 * rng.uniform()) * tt) * bp(noise(n), 200, 900) * np.exp(-tt * 4) * 0.5, db(-28))  # boards creaking
def bzzt(dur):
    n = int(SR * dur); tt = np.arange(n) / SR
    return (lp(np.sign(np.sin(2 * np.pi * 172 * tt)) * 0.6 + np.sin(2 * np.pi * 344 * tt) * 0.3, 1800) * 0.8 + bp(noise(n), 1200, 5000) * 0.3) * env_ar(n, 0.012, 0.03)
place(T_BUZZ, bzzt(0.3), db(-11), -0.3); place(T_BUZZ + 0.45, bzzt(0.3), db(-11), -0.3)
# ---------------------------------------------------------------- Scene 3: the flashlight, boots on gravel, the grab
n = int(SR * 0.5); place(T_FLASH, hp(noise(n), 3000) * expdec(n, 10) * 0.5, db(-14))
for k in range(9): place(36.0 + k * 0.62, lp(bp(noise(int(SR * .2)), 500, 5000) * expdec(int(SR * .2), 6), 2800), db(-17), -0.4)    # boots crunching outside
for k in range(4): place(43.4 + k * 0.32, step(-17, False), pan=0.2)
place(T_GRAB - 0.1, whoosh(0.3, 400, 4000, -16)); place(T_GRAB, bp(noise(int(SR * .35)), 300, 3000) * expdec(int(SR * .35), 4), db(-10)); place(T_GRAB + 0.3, impact(0.25, 110, -14, 0.3))
for k in range(8): place(46.0 + k * 0.6, breath(0.3, -20, 400, 3000))
place(51.0, whoosh(1.2, 200, 1500, -26))
# ---------------------------------------------------------------- Scene 4: the twist, the hatch, the kicks
place(T_WHIP, whoosh(0.4, 400, 4500, -16))
place(62.7, bp(noise(int(SR * .9)), 300, 4000) * np.sin(np.linspace(0, np.pi, int(SR * .9))), db(-12))   # rug ripped back (dust)
n = int(SR * 1.4); tt = np.arange(n) / SR
creak = np.sin(2 * np.pi * (140 + 90 * np.sin(tt * 3.3)) * tt) * (0.6 + 0.4 * np.sign(np.sin(2 * np.pi * 31 * tt))) * bp(noise(n), 200, 2200) * env_ar(n, 0.1, 0.4)
place(66.0, creak, db(-10)); place(67.2, impact(0.6, 55, -6, 0.8))                                      # rusted hatch groans open, clangs
place(67.25, bp(noise(int(SR * 2.0)), 80, 400) * expdec(int(SR * 2.0), 2), db(-16))                     # cold air from below
for b in BANGS:
    place(b, impact(0.9, 58, 0, 1.0)); place(b + 0.01, bp(noise(int(SR * .5)), 1500, 7000) * expdec(int(SR * .5), 7), db(-12))
    n = int(SR * .4); tt = np.arange(n) / SR; place(b + 0.02, np.sin(2 * np.pi * 1300 * tt) * np.exp(-tt * 18) * 0.25 + hp(noise(n), 3000) * np.exp(-tt * 30) * 0.3, db(-14))   # bolt rattles
for k in range(14): place(70.9 + k * 0.4, breath(0.25, -19, 400, 3000))
# ---------------------------------------------------------------- SCORE (original, made in code)
def mtof(m): return 440 * 2 ** ((m - 69) / 12)
def saw(f, n): ph = (np.arange(n) / SR * f) % 1.0; return 2 * ph - 1
def tone(m, dur, g, cut=1800):
    n = int(SR * dur); return lp(saw(mtof(m), n), cut) * env_ar(n, 0.01, 0.15) * db(g)
def braam(g, dur=3.5, root=26):
    n = int(SR * dur); tt = np.arange(n) / SR
    x = sum(saw(mtof(root + iv), n) * (1 + 0.003 * k) for k, iv in enumerate((0, 7, 12, 13)))
    return lp(x, 900) * np.exp(-tt * 0.9) * env_ar(n, 0.02, 1.0) * db(g) + np.sin(2 * np.pi * 36 * tt) * np.exp(-tt * 1.5) * db(g + 4)
# chase: 140 bpm bass ostinato + taiko hits
beat = 60 / 140; pat = [33, 33, 45, 33, 36, 33, 44, 32]; k = 0; st = 0.2
while st < T_TRIP:
    place(st, tone(pat[k % 8], beat * 0.48, -18, 900), bus='mus')
    if k % 4 == 0: n = int(SR * .3); tt = np.arange(n) / SR; place(st, np.sin(2 * np.pi * 52 * tt * (1 - tt)) * np.exp(-tt * 13), db(-13), bus='mus')
    st += beat * 0.5; k += 1
place(T_TRIP + 0.38, braam(-14, 2.5, 28), bus='mus')
str_ = lp(sum(saw(mtof(m) * (1 + 0.002 * i), N) for i, m in enumerate((57, 58, 63))), 2200) * seg(12.6, 14) * (1 - seg(18.6, 19.2)) * db(-31); ML += str_; MR += str_ * 0.9
place(T_SLAM, braam(-13, 3.0, 26), bus='mus')
# the cabin: low drone + slow heartbeat pulse, a high cold note when he says "just like you"
drone = lp(sum(np.sin(2 * np.pi * mtof(m) * t + i) for i, m in enumerate((26, 33, 38, 39))), 450) * seg(21, 23) * (1 - seg(35.3, 35.6)) * db(-25); ML += drone; MR += drone
for st in np.arange(22.0, 35.3, 0.95): n = int(SR * .4); tt = np.arange(n) / SR; place(st, lp(np.sin(2 * np.pi * 48 * tt) * np.exp(-tt * 18), 200), db(-16), bus='mus')
n = int(SR * 4.0); tt = np.arange(n) / SR; place(32.6, (np.sin(2 * np.pi * mtof(88) * tt) + 0.5 * np.sin(2 * np.pi * mtof(89) * tt)) * env_ar(n, 0.8, 1.5) * db(-32), bus='mus')
# flashlight: hit + false-hope warm pad, cut off by Sam's whisper
place(T_FLASH, braam(-15, 2.0, 31), bus='mus')
n = int(SR * 9.5); tt = np.arange(n) / SR; place(36.0, lp(sum(saw(mtof(m), n) for m in (48, 55, 60, 64)), 1400) * env_ar(n, 1.5, 0.3) * db(-31), bus='mus')
pulse = lp(sum(saw(mtof(m) * (1 + 0.003 * i), N) for i, m in enumerate((38, 45, 50, 51))), 700) * seg(45.5, 47) * (1 - seg(53.2, 53.4)) * db(-28); ML += pulse; MR += pulse
# the reveal: horror violin sting (screech cluster) + braam
n = int(SR * 1.6); tt = np.arange(n) / SR
viol = sum(saw(mtof(m) * (1 + 0.004 * np.sin(2 * np.pi * 6 * tt)), n) for m in (88, 89, 94)) * np.exp(-tt * 1.8) * env_ar(n, 0.01, 0.4)
place(T_STING, hp(viol, 1500) * db(-17), bus='mus'); place(T_STING, braam(-10, 4.0, 25), bus='mus')
cluster = sum(np.sin(2 * np.pi * mtof(m) * t + i) for i, m in enumerate((81, 82, 88))) * seg(54, 56) * (1 - seg(61.6, 62.0)) * db(-36); ML += cluster; MR += cluster
# the hatch: creeping low strings → war drums with the kicks → riser into the freeze
creep = lp(sum(saw(mtof(m) * (1 + 0.003 * i), N) for i, m in enumerate((36, 43, 48, 49))), 700) * seg(62, 64) * (1 - seg(80.3, 80.45)) * db(-27); ML += creep; MR += creep
for st in np.arange(71.5, FREEZE - 0.1, 0.43): n = int(SR * .3); tt = np.arange(n) / SR; place(st, np.sin(2 * np.pi * 66 * tt * (1 - 0.5 * tt)) * np.exp(-tt * 12), db(-14), bus='mus')
n = int(SR * (FREEZE - 73.0)); tt = np.arange(n) / SR
place(73.0, lp(saw(55 * 2 ** (tt / tt[-1] * 2.0), n) + bp(noise(n), 800, 6000) * (tt / tt[-1]) * 0.8, 3000) * (tt / tt[-1]) ** 1.6 * db(-17), bus='mus')
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
