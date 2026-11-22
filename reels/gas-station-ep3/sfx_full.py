"""Full SFX + music bed for Episode 2 (110s), mixed with out/dialogue.wav -> out/mix.wav (-14 LUFS, -1.5 dBTP).
All timings mirror scene.js.
"""
import os, json, subprocess
import numpy as np
import soundfile as sf
from scipy import signal

HERE = os.path.dirname(os.path.abspath(__file__))
SR = 48000; DUR = 110.0; N = int(SR * DUR)
t = np.arange(N) / SR
rng = np.random.default_rng(11)
L = np.zeros(N); R = np.zeros(N)
amb_gain = np.ones(N)          # automation for ambience (silence moments)

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
def place(st, clip, g=1.0, pan=0.0):
    i = int(st * SR)
    if i >= N or i + len(clip) <= 0: return
    if i < 0: clip = clip[-i:]; i = 0
    n = min(len(clip), N - i)
    L[i:i + n] += clip[:n] * g * np.sqrt(0.5 * (1 - pan)) * 1.414
    R[i:i + n] += clip[:n] * g * np.sqrt(0.5 * (1 + pan)) * 1.414
def seg(a, b):
    return np.clip((t - a) / (b - a), 0, 1)

# ---------------------------------------------------------------- ambience
silence = seg(99.1, 99.3) * 0.85                                   # everything drops away on the freeze (heartbeat stays)
door_open = seg(9.6, 9.7) * (1 - seg(51.0, 51.4))
outdoors = seg(50.8, 51.4)
for buf, s in ((L, 1), (R, 2)):
    nz = np.random.default_rng(s).standard_normal(N)
    body = lp(hp(nz, 250), 3200) * 0.9; hiss = bp(nz, 3000, 9000) * 0.18
    mod = 1 + 0.12 * np.sin(2 * np.pi * 0.23 * t + s) + 0.06 * np.sin(2 * np.pi * 0.61 * t)
    rain = (body + hiss) * mod * db(-27) * (1 + 1.6 * door_open + 3.2 * outdoors) * (1 - 0.55 * silence)
    rain += bp(nz, 1500, 7000) * db(-30) * (door_open * 1.8 + outdoors * 3.5) * (1 - 0.55 * silence)
    buf += rain
    for _ in range(int(DUR * 45)):
        st = rng.uniform(0, DUR); ln = int(SR * 0.012)
        d = rng.standard_normal(ln) * expdec(ln, 9)
        i = int(st * SR); buf[i:i + ln] += bp(d, 1800, 6500)[:max(0, min(ln, N - i))] * db(-30 + rng.uniform(-6, 4))
hum = (np.sin(2 * np.pi * 60 * t) + 0.55 * np.sin(2 * np.pi * 120 * t + 0.3) + 0.3 * np.sin(2 * np.pi * 180 * t + 1.1) + 0.12 * np.sin(2 * np.pi * 240 * t))
hum *= (1 + 0.04 * np.sin(2 * np.pi * 0.4 * t)) * (1 - silence) * (1 - 0.85 * outdoors)
buzz = bp(np.sign(np.sin(2 * np.pi * 120 * t)) * 0.5, 900, 4000) * (1 - silence) * (1 - outdoors)
L += hum * db(-33) + buzz * db(-47); R += hum * db(-34) + buzz * db(-47)
# cruiser engine idling outside (muffled) once it arrives
idle = (np.sin(2 * np.pi * 32 * t) + 0.6 * np.sin(2 * np.pi * 64 * t + 0.4) + 0.3 * lp(noise(N), 180)) * (1 + 0.15 * np.sin(2 * np.pi * 8 * t))
near = np.interp(t, [0, 50, 54, 60, 66, 70, 80, 83, 88, 98, 110], [0.35, 0.35, 0.8, 1.0, 0.9, 0.7, 0.75, 1.0, 0.85, 1.0, 1.0])
idle *= near * db(-27) * (1 - 0.7 * silence)
L += idle * 0.8; R += idle

# ---------------------------------------------------------------- foley helpers
def whoosh(dur, lo=300, hi=2500, g=-27):
    n = int(SR * dur); x = bp(noise(n), lo, hi); e = np.sin(np.linspace(0, np.pi, n)) ** 2; return x * e * db(g)
def bzzt(dur):
    n = int(SR * dur); tt = np.arange(n) / SR
    motor = np.sign(np.sin(2 * np.pi * 172 * tt)) * 0.6 + np.sin(2 * np.pi * 344 * tt) * 0.3
    rattle = bp(noise(n), 1200, 5000) * (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 86 * tt)))
    return (lp(motor, 1800) * 0.8 + rattle * 0.35) * env_ar(n, 0.012, 0.03)
def bell(f, dur, g):
    n = int(SR * dur); tt = np.arange(n) / SR
    x = sum(a * np.sin(2 * np.pi * f * m * tt) * np.exp(-tt * d) for m, a, d in ((1, 1, 2.2), (2.01, 0.45, 3.5), (3.03, 0.22, 5), (4.2, 0.12, 7)))
    return x * env_ar(n, 0.004, 0.05) * db(g)
def impact(dur, f0, g, bright=0.5):
    n = int(SR * dur); tt = np.arange(n) / SR
    thump = np.sin(2 * np.pi * f0 * tt * (1 - 0.3 * tt / dur)) * np.exp(-tt * 18)
    crack = hp(noise(n), 1500) * np.exp(-tt * 60) * bright
    return (thump + crack) * db(g)
def glass_rattle(dur, g):
    n = int(SR * dur); tt = np.arange(n) / SR
    x = bp(noise(n), 2500, 9000) * (0.6 + 0.4 * np.sign(np.sin(2 * np.pi * 38 * tt))) * np.exp(-tt * 9)
    return x * db(g)
def step(g, wet=True):
    n = int(SR * 0.09); tt = np.arange(n) / SR
    slap = bp(noise(n), 300, 3500) * np.exp(-tt * 55)
    splash = bp(noise(n), 2500, 8000) * np.exp(-tt * 25) * (0.5 if wet else 0)
    return (slap + splash) * db(g)
def boot(g):
    n = int(SR * 0.16); tt = np.arange(n) / SR
    thud = np.sin(2 * np.pi * 70 * tt) * np.exp(-tt * 30); splash = bp(noise(n), 1500, 7000) * np.exp(-tt * 14) * 0.7
    return lp(thud + splash, 3000) * db(g)
def knock(g):   # fist on the glass door
    n = int(SR * 0.5); tt = np.arange(n) / SR
    body = np.sin(2 * np.pi * 95 * tt) * np.exp(-tt * 22) + 0.5 * np.sin(2 * np.pi * 190 * tt) * np.exp(-tt * 30)
    return (body + bp(noise(n), 400, 2500) * np.exp(-tt * 45) * 0.8) * db(g) + glass_rattle(0.5, g - 12)
def click_clunk():
    n = int(SR * 0.6); tt = np.arange(n) / SR
    click = hp(noise(n), 2500) * np.exp(-tt * 300)
    clunk = np.zeros(n); i0 = int(0.06 * SR)
    m = n - i0; tm = np.arange(m) / SR
    clunk[i0:] = (np.sin(2 * np.pi * 85 * tm) * np.exp(-tm * 16) * 1.2 + bp(noise(m), 300, 2000) * np.exp(-tm * 30) * 0.8
                  + np.sin(2 * np.pi * 1250 * tm) * np.exp(-tm * 25) * 0.15)
    return click * 0.8 + clunk
def breath(dur, g, lo=500, hi=3500):
    n = int(SR * dur); return bp(noise(n), lo, hi) * np.sin(np.linspace(0, np.pi, n)) ** 1.5 * db(g)


# ---------------------------------------------------------------- Scene 1: the choice
maglock = np.sin(2 * np.pi * 50 * t) * (1 - seg(1.2, 1.25)) * db(-44); L += maglock; R += maglock
place(0.85, whoosh(0.35, 400, 3000, -27))
place(1.22, click_clunk(), db(-5))
n = int(SR * 0.35); place(1.3, bp(noise(n), 200, 900) * np.exp(-np.linspace(0, 6, n)), db(-22))      # magnetic lock releasing
# ---------------------------------------------------------------- Scene 2: Maya's rage, the door bursts open
place(5.9, whoosh(0.38, 400, 4000, -22))
n = int(SR * 0.5); tt = np.arange(n) / SR; place(6.55, bp(noise(n), 3000, 9000) * np.sin(np.linspace(0, np.pi, n)) ** 2 * 0.5 + np.sin(2 * np.pi * 3700 * tt) * np.exp(-tt * 8) * 0.2, db(-20), -0.3)
place(9.6, impact(0.8, 55, -3, 1.0), pan=0.15); place(9.62, glass_rattle(1.3, -9), pan=0.15)        # BANG
for k, st in enumerate((9.62, 9.85, 10.1, 10.35)): place(st, bell(784 if k % 2 == 0 else 622, 0.9, -13), pan=0.25)   # chime ringing wildly
n = int(SR * 3.0); gust = lp(noise(n), 900) * np.sin(np.linspace(0, np.pi, n)) ** 1.5; place(9.6, gust, db(-14), 0.2)    # cold wind
for k in range(6): place(9.9 + k * 0.42, boot(-18 + k * 1.2), pan=0.15 - k * 0.03)
# ---------------------------------------------------------------- Scene 2: the clash
place(14.9, whoosh(0.38, 400, 4000, -22))
n = int(SR * 0.25); tt = np.arange(n) / SR
rack = np.concatenate([hp(noise(int(SR * .05)), 2500) * np.exp(-np.linspace(0, 20, int(SR * .05))), np.zeros(int(SR * .07)), hp(noise(int(SR * .06)), 1800) * np.exp(-np.linspace(0, 15, int(SR * .06)))])
place(15.35, rack, db(-12), 0.1)                                                                   # slide racked
place(18.9, whoosh(1.5, 200, 1500, -30)); place(20.35, impact(0.4, 130, -14, 0.6)); place(20.37, glass_rattle(0.5, -24))   # back hits the cigarette rack
for k in range(6): place(18.95 + k * 0.25, step(-24, False))
place(24.2, whoosh(0.5, 300, 2500, -20)); place(24.35, impact(0.15, 300, -16, 0.6)); place(25.25, impact(0.3, 90, -14, 0.4))   # vault + land
for k in range(7): place(25.3 + k * 0.19, step(-20, False), pan=0.05)
n = int(SR * 0.22); place(26.62, bp(noise(n), 1500, 8000) * np.sin(np.linspace(0, np.pi, n)) ** 3, db(-10)); place(26.72, impact(0.2, 180, -12, 0.3))   # slash
def clatter(g):
    out = np.zeros(int(SR * 1.2))
    for k, (d, a) in enumerate(((0, 1), (.11, .55), (.19, .35), (.26, .2))):
        ln = int(SR * .12); tt = np.arange(ln) / SR
        x = (np.sin(2 * np.pi * 2900 * tt) * 0.4 + np.sin(2 * np.pi * 4600 * tt) * 0.25 + hp(noise(ln), 3000) * 0.5) * np.exp(-tt * 40) * a
        i = int(d * SR); out[i:i + ln] += x
    sc = int(SR * 0.85); i = int(.3 * SR); out[i:i + sc] += bp(noise(sc), 1200, 6000) * np.linspace(0.5, 0, sc) * 0.35
    return out * db(g)
place(27.0, clatter(-6), 0.05)                                                                     # gun hits the tile and slides
for k in range(14): place(27.0 + k * 0.1 + rng.uniform(0, .05), breath(0.12, -26, 300, 2500), pan=rng.uniform(-.2, .2))   # grappling
place(28.4, impact(1.0, 60, -2, 1.0)); place(28.42, glass_rattle(0.8, -14))                         # crash into the aisle
for k in range(46):                                                                                # products raining down
    st = 28.45 + rng.uniform(0, 1.6) ** 1.6
    if k % 3 == 0:
        ln = int(SR * .09); tt = np.arange(ln) / SR; x = np.sin(2 * np.pi * rng.uniform(900, 1800) * tt) * np.exp(-tt * 35) + hp(noise(ln), 2000) * np.exp(-tt * 60) * .4
    else:
        ln = int(SR * .14); x = bp(noise(ln), 1500, 9000) * np.exp(-np.linspace(0, 8, ln)) * (0.6 + 0.4 * np.sign(np.sin(np.arange(ln) / SR * 2 * np.pi * 60)))
    place(st, x, db(-18 + rng.uniform(-6, 2)), rng.uniform(-.4, .2))
for k in range(30):                                                                                # wrestling on the floor
    st = 29.2 + k * 0.62 + rng.uniform(0, .3)
    g = -24 if st < 34 else -30 if st < 42 else -38
    place(st, bp(noise(int(SR * .25)), 300, 3000) * np.sin(np.linspace(0, np.pi, int(SR * .25))), db(g), -0.3)
place(34.0, whoosh(0.35, 400, 4000, -22)); place(37.0, whoosh(0.35, 400, 4000, -22))
# ---------------------------------------------------------------- Scene 3: the escape
for k in range(int((51.2 - 42.0) * 5.4)):
    st = 42.0 + k / 5.4
    if 45.3 < st < 45.9: continue
    place(st, step(-17, False), pan=0.1 if k % 2 else -0.1)
place(45.3, whoosh(0.4, 300, 2000, -24)); place(45.88, impact(0.25, 110, -14, 0.5))                # leap over the snacks
for k in range(4): place(45.9 + k * 0.05, bp(noise(int(SR * .06)), 2000, 8000) * np.exp(-np.linspace(0, 10, int(SR * .06))), db(-22))   # crunch
for k in range(int((69.6 - 51.2) * 5.4)):
    st = 51.2 + k / 5.4
    place(st, step(-13, True), pan=0.12 if k % 2 else -0.12)
for k in range(int((69.9 - 42.2) / 0.36)):                                                        # frantic breathing
    st = 42.2 + k * 0.36
    if any(a < st < b for a, b in ((49.6, 52.4), (57.0, 60.5))): continue
    place(st, breath(0.26, -19 if k % 2 else -22, 400, 3200))
n = int(SR * 7.0); tt = np.arange(n) / SR                                                          # truck passing on the highway
truck = lp(noise(n), 300) * np.sin(np.linspace(0, np.pi, n)) ** 2 + np.sin(2 * np.pi * 55 * tt) * 0.3 * np.sin(np.linspace(0, np.pi, n)) ** 2
place(61.5, truck, db(-22), -0.6)
for st in (66.0, 66.4, 66.8): place(st, lp(knock(-6), 900), pan=0.5)                               # THUD THUD THUD from inside the car
n = int(SR * 0.6); place(69.5, bp(noise(n), 800, 5000) * np.exp(-np.linspace(0, 4, n)), db(-14))    # skid on wet asphalt
# ---------------------------------------------------------------- Scene 4: the cruiser twist
place(70.0, whoosh(0.38, 400, 4000, -21))
for st in (72.0, 72.4, 72.8, 74.6, 75.0, 76.5, 76.9): place(st, lp(knock(-8), 1400), pan=0.35)
for k in range(9): place(79.9 + k * 0.36, step(-17, True), pan=0.1 if k % 2 else -0.1)
place(85.0, whoosh(0.6, 300, 2000, -30))
n = int(SR * .2); place(85.4, (np.sin(2 * np.pi * 3100 * np.arange(n) / SR) + np.sin(2 * np.pi * 4300 * np.arange(n) / SR)) * np.exp(-np.linspace(0, 12, n)) * 0.3, db(-26), -0.3)   # keys jingle
place(87.9, whoosh(0.42, 400, 4000, -21))
for k in range(4): place(87.95 + k * 0.33, step(-18, True))
for k in range(8): place(91.8 + k * 0.5, boot(-26 + k * 1.5), pan=-0.2)
place(91.4, clatter(-22) * 0.4, pan=-0.2)
place(93.5, impact(0.08, 900, -20, 0.8), pan=-0.2)                                                 # flashlight click
place(95.8, boot(-14), pan=-0.2); place(96.3, boot(-14), pan=-0.2)
drone_t = np.clip((t - 66) / 33, 0, 1)
drone = lp(sum(np.sin(2 * np.pi * f * t + rng.uniform(0, 6)) for f in (41.2, 41.6, 61.8, 82.4, 82.9)), 400) * (0.3 + 0.7 * drone_t) * seg(66, 70)
mus = drone * db(-25) * (1 - seg(99.1, 99.4)); L += mus; R += mus * 0.95
# ---------------------------------------------------------------- Scene 5: freeze
def heartbeat(g):
    n = int(SR * 0.55); tt = np.arange(n) / SR
    beat = lambda d: np.where(tt >= d, np.sin(2 * np.pi * 52 * (tt - d)) * np.exp(-(tt - d) * 16), 0)
    return lp(beat(0) + 0.75 * beat(0.17), 200) * db(g)
tb = 96.4
while tb < DUR:
    place(tb, heartbeat(-13 + (6 if tb > 99.2 else 0))); tb += 1 / (1.2 + 0.15 * min(1, (tb - 96.4) / 4))
n = int(SR * 2.2); tt = np.arange(n) / SR
place(99.2, np.sin(2 * np.pi * 40 * tt) * np.exp(-tt * 2) + bp(noise(n), 200, 2000) * np.exp(-tt * 6) * 0.3, db(-6))
rain_duck = 1 - 0.5 * seg(99.2, 99.7)

# ---------------------------------------------------------------- mix with dialogue (ducking ambience under voices)
dlg, sr = sf.read(os.path.join(HERE, 'out', 'dialogue.wav'), always_2d=True)
dlg = dlg[:N]; dlg = np.pad(dlg, ((0, N - len(dlg)), (0, 0)))
denv = signal.sosfilt(sos('low', 6, 2), np.abs(dlg.mean(1))); denv = np.clip(denv / (denv.max() + 1e-9) * 6, 0, 1)
duck = 1 - 0.35 * denv
L *= duck * rain_duck; R *= duck * rain_duck
mix = np.stack([L * db(-2) + dlg[:, 0] * db(1.5), R * db(-2) + dlg[:, 1] * db(1.5)], 1)
mix *= 0.9 / np.max(np.abs(mix))
fade = np.clip((DUR - t) / 0.4, 0, 1)[:, None] * np.clip(t / 0.25, 0, 1)[:, None]
raw = os.path.join(HERE, 'out', 'mix_raw.wav'); sf.write(raw, (mix * fade).astype(np.float32), SR, subtype='PCM_24')
comp = os.path.join(HERE, 'out', 'mix_comp.wav')
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', raw, '-af', 'acompressor=threshold=0.12:ratio=3:attack=4:release=160:makeup=1.6,alimiter=limit=0.89:attack=2:release=60', comp], check=True)
raw = comp
meas = subprocess.run(['ffmpeg', '-hide_banner', '-i', raw, '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json', '-f', 'null', '-'], capture_output=True, text=True).stderr
m = json.loads(meas[meas.rindex('{'):meas.rindex('}') + 1])
af = (f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}"
      f":measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', raw, '-af', af, '-ar', '48000', os.path.join(HERE, 'out', 'mix.wav')], check=True)
print('wrote out/mix.wav')
