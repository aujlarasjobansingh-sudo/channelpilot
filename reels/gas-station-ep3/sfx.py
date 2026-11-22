"""SFX + original horror/suspense score for Gas Station Episode 3 (finale), mixed with out/dialogue.wav
-> out/mix.wav (two-pass loudnorm to -14 LUFS, -1.5 dBTP). Everything is synthesised here (royalty-free). Timings mirror scene.js."""
import os, json, subprocess
import numpy as np
import soundfile as sf
from scipy import signal

HERE = os.path.dirname(os.path.abspath(__file__))
SR = 48000; DUR = 85.0; N = int(SR * DUR)
t = np.arange(N) / SR
rng = np.random.default_rng(31)
L = np.zeros(N); R = np.zeros(N); ML = np.zeros(N); MR = np.zeros(N)   # sfx bus, music bus
BLACK = 76.9; T_SHOT = 9.6; T_GUN = 63.9; T_SIREN = 65.0; T_GRAB = 67.4

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

silent = seg(BLACK, BLACK + 0.01)           # hard cut to black
# ---------------------------------------------------------------- ambience: heavy rain outdoors, the cruiser idling behind us
for buf, s in ((L, 1), (R, 2)):
    nz = np.random.default_rng(s).standard_normal(N)
    body = lp(hp(nz, 250), 3200) * 0.9; hiss = bp(nz, 3000, 9000) * 0.25
    mod = 1 + 0.12 * np.sin(2 * np.pi * 0.23 * t + s) + 0.06 * np.sin(2 * np.pi * 0.61 * t)
    lvl = db(-19) * (1 - 0.6 * seg(41.6, 42.4) * (1 - seg(49.5, 51.0)))          # rain fades into ringing on the alert
    buf += (body + hiss) * mod * lvl * (1 - silent)
    for _ in range(int(BLACK * 55)):
        st = rng.uniform(0, BLACK); ln = int(SR * 0.012)
        d = rng.standard_normal(ln) * expdec(ln, 9); i = int(st * SR)
        buf[i:i + ln] += bp(d, 1800, 6500)[:max(0, min(ln, N - i))] * db(-27 + rng.uniform(-6, 4))
idle = (np.sin(2 * np.pi * 32 * t) + 0.6 * np.sin(2 * np.pi * 64 * t + 0.4) + 0.3 * lp(noise(N), 180)) * (1 + 0.15 * np.sin(2 * np.pi * 8 * t))
idle *= np.interp(t, [0, 10, 20, 85], [1.0, 1.0, 0.25, 0.2]) * db(-24) * (1 - silent)
L += idle * 0.8; R += idle

# ---------------------------------------------------------------- Scene 1: the door, Sam, the GUNSHOT
n = int(SR * 0.6); tt = np.arange(n) / SR
latch = hp(noise(n), 2500) * np.exp(-tt * 250) * 0.8 + np.sin(2 * np.pi * 95 * tt) * np.exp(-tt * 14) * 0.9 + bp(noise(n), 300, 2000) * np.exp(-tt * 20) * 0.6
place(0.95, latch, db(-6), 0.15)
place(1.0, whoosh(0.5, 200, 1800, -16), pan=0.1)
n = int(SR * 0.7); tt = np.arange(n) / SR; place(1.05, np.sin(2 * np.pi * (300 + 120 * tt) * tt) * np.exp(-tt * 3) * bp(noise(n), 200, 900) * 0.5, db(-24), 0.1)  # hinge creak
place(1.35, impact(0.25, 70, -12, 0.2), pan=0.1)                                     # door stops
for k in range(10): place(3.0 + k * 0.17 + rng.uniform(0, 0.05), bp(noise(int(SR * .14)), 300, 3500) * np.sin(np.linspace(0, np.pi, int(SR * .14))), db(-22), -0.1)   # scrambling out
for k in range(4): place(4.3 + k * 0.28, step(-16), pan=-0.1)
for k in range(5): place(5.2 + k * 0.6, breath(0.35, -21, 500, 3000), pan=-0.1)
# BANG — the shot from the store, ricochet off the roof, sparks, ears ringing
n = int(SR * 2.5); tt = np.arange(n) / SR
bang = hp(noise(n), 200) * np.exp(-tt * 28) * 1.2 + np.sin(2 * np.pi * 55 * tt) * np.exp(-tt * 9) * 1.4 + lp(noise(n), 400) * np.exp(-tt * 3) * 0.5
place(T_SHOT, reverb(bang, 2.2, 0.55, 3), db(1), 0.25)
n = int(SR * 0.45); tt = np.arange(n) / SR; place(T_SHOT + 0.04, np.sin(2 * np.pi * (5200 - 3800 * tt) * tt) * np.exp(-tt * 9) * 0.6, db(-10), -0.2)   # ricochet ping
for k in range(14): place(T_SHOT + 0.05 + rng.uniform(0, 0.6), hp(noise(int(SR * .03)), 3000) * expdec(int(SR * .03), 8), db(-20 + rng.uniform(-6, 3)), rng.uniform(-0.4, 0.2))   # sparks
n = int(SR * 4.0); tt = np.arange(n) / SR; place(T_SHOT + 0.1, np.sin(2 * np.pi * 3150 * tt) * np.exp(-tt * 0.9) * env_ar(n, 0.05, 1.0), db(-25))        # tinnitus
# ---------------------------------------------------------------- Scene 2: the sprint
for k in range(int((21.2 - 10.0) * 5.6)):
    st = 10.0 + k / 5.6; place(st, step(-11), pan=0.12 if k % 2 else -0.12)
    if k % 2 == 0: place(st + 0.07, step(-18), pan=-0.4)                                     # Sam's steps
for k in range(int((22.5 - 10.2) / 0.34)): place(10.2 + k * 0.34, breath(0.25, -17 if k % 2 else -20, 400, 3200))
for st in (11.1, 14.6, 18.2): place(st, whoosh(0.4, 400, 3500, -24))                         # puddle splashes
place(12.6, whoosh(0.35, 400, 4000, -22)); place(14.4, whoosh(0.35, 400, 4000, -22))          # head whips back and forth
place(21.25, whoosh(0.45, 200, 2500, -18)); place(21.7, impact(0.35, 90, -10, 0.6)); place(21.75, bp(noise(int(SR * .5)), 1500, 7000) * expdec(int(SR * .5), 7), db(-18))  # slide behind the barrier
place(21.9, impact(0.3, 120, -16, 0.5), pan=-0.4)
for k in range(10): place(22.4 + k * 0.62, breath(0.4, -22 - k, 400, 2800))
# the car coming out of the fog (engine + tyres on wet road), getting closer
car_lvl = np.interp(t, [0, 23, 40, 60, 65, 71.4, 85], [0, 0.05, 0.18, 0.4, 0.55, 0.9, 0.6]) * (1 - silent)
eng = (np.sin(2 * np.pi * 46 * t) * 0.6 + lp(noise(N), 160) * 0.8) * car_lvl * db(-18)
hiss_t = bp(noise(N), 1200, 6000) * car_lvl * db(-24)
L += (eng + hiss_t) * 1.1; R += (eng + hiss_t) * 0.8
# ---------------------------------------------------------------- Scene 3: the phone
def bzzt(dur):
    n = int(SR * dur); tt = np.arange(n) / SR
    return (lp(np.sign(np.sin(2 * np.pi * 172 * tt)) * 0.6 + np.sin(2 * np.pi * 344 * tt) * 0.3, 1800) * 0.8 + bp(noise(n), 1200, 5000) * 0.3) * env_ar(n, 0.012, 0.03)
place(39.45, bzzt(0.32), db(-9), 0.2); place(39.9, bzzt(0.32), db(-9), 0.2)
place(40.0, bp(noise(int(SR * .4)), 400, 3000) * np.sin(np.linspace(0, np.pi, int(SR * .4))), db(-22), 0.2)   # pulled from the pocket
n = int(SR * 9.0); tt = np.arange(n) / SR
ring = (np.sin(2 * np.pi * 2900 * tt) + 0.4 * np.sin(2 * np.pi * 4350 * tt)) * env_ar(n, 0.6, 3.0)
place(41.7, ring, db(-26))
# ---------------------------------------------------------------- Scene 4: the twist
place(50.4, whoosh(3.2, 150, 900, -30))
place(53.6, whoosh(0.5, 300, 2000, -26)); place(54.2, bp(noise(int(SR * .3)), 300, 2500) * np.sin(np.linspace(0, np.pi, int(SR * .3))), db(-24), -0.3)   # hands lowering
for k in range(3): place(55.0 + k * 0.3, step(-24, False), pan=0.2)                          # backing away on gravel
place(T_GUN, bp(noise(int(SR * .35)), 300, 3000) * np.sin(np.linspace(0, np.pi, int(SR * .35))), db(-16), -0.3)   # jacket
n = int(SR * 0.3); tt = np.arange(n) / SR
rack = np.concatenate([hp(noise(int(SR * .04)), 2500) * expdec(int(SR * .04), 20), np.zeros(int(SR * .06)), hp(noise(int(SR * .05)), 1800) * expdec(int(SR * .05), 15)])
place(T_GUN + 0.42, rack, db(-8), -0.2)
# sirens: WEE-OO, getting closer
sir_t = t - T_SIREN
f = np.where((sir_t * 1.6) % 1 < 0.5, 760.0, 980.0); f = lp(f, 12, 2)
ph = np.cumsum(f) / SR
siren = (np.sin(2 * np.pi * ph) + 0.35 * np.sin(4 * np.pi * ph)) * np.clip(sir_t / 0.4, 0, 1) * np.interp(t, [0, T_SIREN, 71.4, 76.9, 85], [0, 0.35, 1.0, 1.0, 0]) * (1 - silent)
siren = lp(siren, 3500) * db(-15)
L += siren * 1.15; R += siren * 0.85
place(T_GRAB - 0.3, whoosh(0.35, 400, 4000, -16)); place(T_GRAB, impact(0.25, 140, -12, 0.4)); place(T_GRAB + 0.02, bp(noise(int(SR * .4)), 300, 3000) * expdec(int(SR * .4), 4), db(-14))
# ---------------------------------------------------------------- Scene 5: dragged into the woods, spotlights, cut to black
for k in range(int((76.8 - 70.3) * 3.2)):
    st = 70.3 + k / 3.2; place(st, bp(noise(int(SR * .3)), 300, 2500) * np.sin(np.linspace(0, np.pi, int(SR * .3))) ** 2, db(-18), rng.uniform(-.3, .3))   # heels dragging
    place(st + 0.12, bp(noise(int(SR * .2)), 1500, 7000) * expdec(int(SR * .2), 5), db(-24), rng.uniform(-.5, .5))              # brush
for k in range(int((76.8 - 70.3) / 0.3)): place(70.3 + k * 0.3, breath(0.22, -17, 400, 3200))
n = int(SR * 1.6); tt = np.arange(n) / SR
screech = (np.sin(2 * np.pi * (2300 + 300 * np.sin(2 * np.pi * 9 * tt)) * tt) * 0.5 + bp(noise(n), 1500, 6000) * 0.8) * env_ar(n, 0.05, 0.4)
place(70.9, screech, db(-11), 0.4)
place(71.6, impact(0.2, 300, -14, 0.8), pan=0.4)                                                # spotlight clunk on
for st in (72.0, 72.6): place(st, impact(0.12, 900, -24, 0.9), pan=0.4)                        # car doors
place(75.6, whoosh(1.3, 200, 3000, -18))

# ---------------------------------------------------------------- SCORE (music bus) — original, made in code
def mtof(m): return 440 * 2 ** ((m - 69) / 12)
def saw(f, n): ph = (np.arange(n) / SR * f) % 1.0; return 2 * ph - 1
def tone(m, dur, g, kind='saw', a=0.01, r=0.15, cut=1800):
    n = int(SR * dur); x = saw(mtof(m), n) if kind == 'saw' else np.sin(2 * np.pi * mtof(m) * np.arange(n) / SR)
    return lp(x, cut) * env_ar(n, a, r) * db(g)
def braam(g, dur=3.5, root=26):
    n = int(SR * dur); tt = np.arange(n) / SR
    x = sum(saw(mtof(root + iv), n) * (1 + 0.003 * k) for k, iv in enumerate((0, 7, 12, 13)))
    return lp(x, 900) * np.exp(-tt * 0.9) * env_ar(n, 0.02, 1.0) * db(g) + np.sin(2 * np.pi * 36 * tt) * np.exp(-tt * 1.5) * db(g + 4)
# cold open: low dread under the door
dread = lp(sum(np.sin(2 * np.pi * mtof(m) * t + k) for k, m in enumerate((33, 34, 45))), 300) * seg(0, 1.5) * (1 - seg(9.4, 9.6)) * db(-26)
ML += dread; MR += dread
place(T_SHOT, braam(-12, 3.0), bus='mus')
# the run: driving 150 bpm bass ostinato + ticking hats + rising strings
bpm = 150; beat = 60 / bpm
pat = [33, 33, 45, 33, 36, 33, 44, 33]
k = 0; st = 10.1
while st < 21.4:
    place(st, tone(pat[k % 8], beat * 0.48, -17, cut=900), bus='mus')
    place(st, hp(noise(int(SR * .03)), 6000) * expdec(int(SR * .03), 8), db(-30), bus='mus')
    if k % 4 == 0: n = int(SR * .25); tt = np.arange(n) / SR; place(st, np.sin(2 * np.pi * 55 * tt * (1 - tt)) * np.exp(-tt * 14), db(-14), bus='mus')
    st += beat * 0.5; k += 1
strings = lp(sum(saw(mtof(m) * (1 + 0.002 * i), N) for i, m in enumerate((57, 58, 64))), 2400) * seg(10, 21) * (1 - seg(21.2, 22.0)) * db(-31) * (0.6 + 0.4 * seg(10, 21))
ML += strings; MR += strings * 0.9
# hiding: a pulse like a heartbeat under a tense drone
drone = lp(sum(np.sin(2 * np.pi * mtof(m) * t + i) for i, m in enumerate((28, 35, 40, 41))), 500) * seg(22, 24) * (1 - seg(41.5, 41.9)) * db(-24)
ML += drone; MR += drone
for st in np.arange(22.5, 41.5, 0.85): n = int(SR * .4); tt = np.arange(n) / SR; place(st, lp(np.sin(2 * np.pi * 50 * tt) * np.exp(-tt * 18), 200), db(-15), bus='mus')
# the alert: horror sting, then a high glassy cluster
place(41.7, braam(-9, 4.5, 25), bus='mus')
n = int(SR * 0.9); tt = np.arange(n) / SR; place(41.7, hp(noise(n), 2000) * np.exp(-tt * 5) * 0.5 + sum(np.sin(2 * np.pi * f * tt) for f in (1480, 1568, 2217)) * np.exp(-tt * 2.5) * 0.3, db(-14), bus='mus')
cluster = sum(np.sin(2 * np.pi * mtof(m) * t + i) for i, m in enumerate((84, 85, 91))) * seg(42.5, 45) * (1 - seg(62.5, 63.8)) * db(-36)
ML += cluster; MR += cluster
# the pan to Sam: low strings creep in, a sting on "no handcuffs", a sour chord on the smile
creep = lp(sum(saw(mtof(m) * (1 + 0.003 * i), N) for i, m in enumerate((38, 45, 50, 51))), 700) * seg(50.4, 54) * (1 - seg(63.6, 63.9)) * db(-28)
ML += creep; MR += creep
place(54.0, braam(-14, 2.5, 29), bus='mus')
n = int(SR * 5.8); tt = np.arange(n) / SR
sour = lp(sum(saw(mtof(m), n) for m in (50, 53, 56, 61)), 1500) * env_ar(n, 1.2, 1.5) * db(-28); place(58.0, sour, bus='mus')
# gun → sirens → riser into chaos
place(T_GUN + 0.4, braam(-10, 2.0, 27), bus='mus')
n = int(SR * (BLACK - 66.0)); tt = np.arange(n) / SR
riser = lp(saw(55 * 2 ** (tt / (BLACK - 66.0) * 2.0), n) + bp(noise(n), 800, 6000) * (tt / tt[-1]) * 0.8, 3000) * (tt / tt[-1]) ** 1.5 * db(-17)
place(66.0, riser, bus='mus')
for st in np.arange(70.2, BLACK - 0.1, 0.2):                                                    # war drums
    n = int(SR * .3); tt = np.arange(n) / SR; place(st, np.sin(2 * np.pi * 70 * tt * (1 - 0.5 * tt)) * np.exp(-tt * 12), db(-12 if int((st - 70.2) / 0.2) % 2 == 0 else -17), bus='mus')
# hard cut: silence, then one deep hit + a cold pad for the end card
n = int(SR * 4.0); tt = np.arange(n) / SR
place(BLACK + 0.25, np.sin(2 * np.pi * 34 * tt) * np.exp(-tt * 1.2) * 1.2 + lp(noise(n), 300) * np.exp(-tt * 3) * 0.4, db(-6), bus='mus')
n = int(SR * (DUR - BLACK - 1.0)); tt = np.arange(n) / SR
pad = lp(sum(np.sin(2 * np.pi * mtof(m) * tt + i) for i, m in enumerate((45, 52, 57, 60))), 1200) * env_ar(n, 1.5, 2.0) * db(-24)
place(BLACK + 1.0, pad, bus='mus')
def heartbeat(g):
    n = int(SR * 0.55); tt = np.arange(n) / SR
    b = lambda d: np.where(tt >= d, np.sin(2 * np.pi * 52 * (tt - d)) * np.exp(-(tt - d) * 16), 0)
    return lp(b(0) + 0.75 * b(0.17), 200) * db(g)
for st in np.arange(BLACK + 1.4, DUR - 0.8, 1.15): place(st, heartbeat(-14), bus='mus')
# sfx bus is silent after the cut
L *= (1 - silent); R *= (1 - silent)

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
