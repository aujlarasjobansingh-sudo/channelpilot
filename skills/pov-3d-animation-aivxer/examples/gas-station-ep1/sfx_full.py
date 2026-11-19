"""Full SFX + music bed for Episode 1 (116s), mixed with out/dialogue.wav -> out/mix.wav (-14 LUFS, -1.5 dBTP).
All timings mirror scene.js.
"""
import os, json, subprocess
import numpy as np
import soundfile as sf
from scipy import signal

HERE = os.path.dirname(os.path.abspath(__file__))
SR = 48000; DUR = 116.0; N = int(SR * DUR)
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
silence = (seg(98.0, 98.15) * (1 - seg(102.85, 103.1)))          # hum/drone drop-out after the sting
door_open = seg(14.0, 14.1) * (1 - seg(15.8, 15.9))
for buf, s in ((L, 1), (R, 2)):
    nz = np.random.default_rng(s).standard_normal(N)
    body = lp(hp(nz, 250), 3200) * 0.9; hiss = bp(nz, 3000, 9000) * 0.18
    mod = 1 + 0.12 * np.sin(2 * np.pi * 0.23 * t + s) + 0.06 * np.sin(2 * np.pi * 0.61 * t)
    rain = (body + hiss) * mod * db(-27) * (1 + 2.2 * door_open)
    rain += bp(nz, 1500, 7000) * db(-30) * door_open * 2.5
    buf += rain
    for _ in range(int(DUR * 45)):
        st = rng.uniform(0, DUR); ln = int(SR * 0.012)
        d = rng.standard_normal(ln) * expdec(ln, 9)
        i = int(st * SR); buf[i:i + ln] += bp(d, 1800, 6500)[:max(0, min(ln, N - i))] * db(-30 + rng.uniform(-6, 4))
hum = (np.sin(2 * np.pi * 60 * t) + 0.55 * np.sin(2 * np.pi * 120 * t + 0.3) + 0.3 * np.sin(2 * np.pi * 180 * t + 1.1) + 0.12 * np.sin(2 * np.pi * 240 * t))
hum *= (1 + 0.04 * np.sin(2 * np.pi * 0.4 * t)) * (1 - silence)
buzz = bp(np.sign(np.sin(2 * np.pi * 120 * t)) * 0.5, 900, 4000) * (1 - silence)
L += hum * db(-33) + buzz * db(-47); R += hum * db(-34) + buzz * db(-47)
# cruiser engine idling outside (muffled) once it arrives
idle = (np.sin(2 * np.pi * 32 * t) + 0.6 * np.sin(2 * np.pi * 64 * t + 0.4) + 0.3 * lp(noise(N), 180)) * (1 + 0.15 * np.sin(2 * np.pi * 8 * t))
idle *= seg(38.0, 41.0) * db(-32) * (1 - 0.7 * silence)
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

# ---------------------------------------------------------------- Scene 1
amp = np.clip(1 - (t - 5.2) / 0.55, 0, 1)
ph = t * 2 * np.pi / 1.55 + 0.4 * np.sin(t * 1.3)
wipe = lp(bp(noise(N), 700, 5000) * (np.abs(np.sin(ph)) ** 1.5 * 0.7 + 0.3) * amp, 6000)
L += wipe * db(-29) * 0.8; R += wipe * db(-29)
place(5.83, whoosh(0.6))
for st in (6.62, 7.06): place(st, bzzt(0.30), db(-11))
place(7.92, bp(noise(int(SR * 0.18)), 1500, 7000) * env_ar(int(SR * 0.18), 0.02, 0.12), db(-24))
place(7.98, whoosh(0.6, 200, 1800, -29))
REPLY = "Dead quiet. Just me and the crickets."
for i in range(len(REPLY)):
    st = 8.75 + i / 15 + rng.uniform(-0.008, 0.008); ln = int(SR * 0.03)
    tap = bp(noise(ln), 2000, 7000) * expdec(ln, 12); tick = np.sin(2 * np.pi * 220 * np.arange(ln) / SR) * expdec(ln, 18)
    place(st, tap * 0.6 + tick * 0.5, db(-21))
place(11.4, whoosh(0.35, 1500, 6000, -26))                       # message sent
place(14.88, impact(0.25, 180, -22, 0.8))                         # phone set down on counter

# ---------------------------------------------------------------- Scene 2
place(14.0, bell(784, 1.4, -10), pan=0.25); place(14.32, bell(622, 1.6, -10), pan=0.25)        # DING-DONG
place(14.04, impact(0.6, 70, -8, 0.9), pan=0.2); place(14.05, glass_rattle(0.9, -14), pan=0.2)  # door bangs open
place(14.85, whoosh(0.38, 400, 4000, -22))
for k in range(5): place(14.1 + k * 0.2, step(-22), pan=0.25)
place(15.84, impact(0.7, 62, -6, 1.0), pan=0.2); place(15.85, glass_rattle(1.1, -12), pan=0.2)  # slams it shut
place(15.86, bell(784, 0.5, -24), pan=0.25)
for k in range(int((18.2 - 16.3) * 5.4)): place(16.3 + k / 5.4, step(-21 + k * 0.4), pan=0.2 - k * 0.02)
for k in range(8): place(18.25 + k * 0.42, breath(0.38, -26 + (k % 2) * 3))                     # panting
place(18.7, whoosh(0.35, 600, 4000, -28))
place(21.5, whoosh(0.7, 300, 2000, -30))
for k in range(5): place(21.6 + k * 0.19, step(-25), pan=-0.3)
place(29.85, whoosh(0.42, 200, 3000, -21))
place(30.56, click_clunk(), db(-6))
maglock = np.sin(2 * np.pi * 50 * t) * seg(30.6, 30.9) * db(-46)
L += maglock; R += maglock
place(31.0, whoosh(0.55, 300, 2000, -29))
place(32.6, impact(0.2, 300, -24, 0.6), pan=-0.4)                # handset off the cradle
dial = (np.sin(2 * np.pi * 350 * t) + np.sin(2 * np.pi * 440 * t)) * seg(33.0, 33.05) * (1 - seg(38.2, 38.25))
dial = lp(hp(dial, 300), 2500) * db(-36); L += dial * 1.4; R += dial * 0.4

# ---------------------------------------------------------------- Scene 3
crunch = np.zeros(N); i0, i1 = int(38.0 * SR), int(41.4 * SR)
cr = bp(noise(i1 - i0), 800, 6000) * (rng.random(i1 - i0) > 0.985) * 3 + bp(noise(i1 - i0), 200, 1200) * 0.4
cr *= np.linspace(0.3, 1.0, i1 - i0) * env_ar(i1 - i0, 0.2, 0.6)
crunch[i0:i1] = lp(cr, 3500); L += crunch * db(-24); R += crunch * db(-22)
place(38.15, whoosh(0.6, 200, 1500, -28))
place(44.9, whoosh(0.38, 400, 4000, -22))
place(45.4, whoosh(0.4, 300, 1500, -27)); place(46.42, impact(0.18, 220, -20, 0.3))           # grabs the forearm
for k in range(6): place(46.8 + k * 1.1, breath(0.5, -31, 400, 2500))
place(53.9, whoosh(0.45, 300, 3000, -23))
drone_t = np.clip((t - 54.4) / 43.6, 0, 1)
drone = sum(np.sin(2 * np.pi * f * t + rng.uniform(0, 6)) for f in (41.2, 41.6, 61.8, 82.4, 82.9))
drone = lp(drone, 400) * (0.4 + 0.6 * drone_t) * seg(54.4, 58)
pad = bp(sum(np.sign(np.sin(2 * np.pi * f * t)) for f in (329.6, 349.2, 466.2)), 300, 1800) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.17 * t)) * seg(56, 70) * drone_t
mus = (drone * db(-26) + pad * db(-44)) * (1 - silence) * (1 - seg(111.9, 112.4))
low_return = lp(sum(np.sin(2 * np.pi * f * t) for f in (41.2, 41.7)), 200) * seg(103.0, 104.0) * (1 - seg(111.9, 112.4)) * db(-30)
L += mus + low_return; R += mus * 0.95 + low_return

# ---------------------------------------------------------------- Scene 4
place(56.4, impact(0.4, 90, -26, 0.2), pan=0.15)                   # car door opens (muffled)
for k in range(3): place(57.1 + k * 0.45, boot(-29), pan=0.15)
place(58.3, impact(0.5, 70, -25, 0.2), pan=0.15)                   # car door shut
n = int(SR * 1.6); tt = np.arange(n) / SR                         # flashlight blast hit
hit = np.sin(2 * np.pi * 48 * tt * (1 - 0.35 * tt / 1.6)) * np.exp(-tt * 3) + bp(noise(n), 3000, 12000) * np.exp(-tt * 2.5) * 0.35
place(59.33, whoosh(0.5, 500, 6000, -24)); place(59.38, hit, db(-10))
for k in range(int(1.25 / 0.42) + 1): place(61.5 + k * 0.42, boot(-22 + k * 2), pan=0.1)       # boots splashing
for st in (62.9, 63.3, 63.7): place(st, knock(-4), pan=0.1)                                     # THUD THUD THUD
place(70.85, whoosh(0.38, 400, 4000, -22))
for k in range(5): place(71.3 + k * 1.05, breath(0.45, -27, 600, 3800), pan=0.3)
place(76.65, whoosh(0.38, 400, 4000, -22))
for st in (77.55, 78.0, 78.45):                                    # yanks the locked door
    place(st, impact(0.3, 140, -10, 0.9), pan=0.1); place(st + 0.01, glass_rattle(0.5, -14), pan=0.1)
    ln = int(SR * 0.12); place(st + 0.02, np.sin(2 * np.pi * 2400 * np.arange(ln) / SR) * expdec(ln, 30), db(-24), 0.1)
place(82.95, whoosh(0.38, 400, 4000, -23))
place(84.0, whoosh(1.4, 200, 900, -33))

# ---------------------------------------------------------------- Scene 5
place(88.95, whoosh(0.35, 400, 4000, -22))
for st in (89.1, 89.55): place(st, bzzt(0.30), db(-9))
alert = (np.sin(2 * np.pi * 853 * t) + np.sin(2 * np.pi * 960 * t)) * (seg(89.15, 89.17) * (1 - seg(89.95, 89.97)))
alert = bp(alert * (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 4 * t))), 500, 3000) * db(-27); L += alert; R += alert
place(96.6, bell(1568, 0.9, -15)); place(96.72, bell(2093, 0.9, -17))                           # text DING
n = int(SR * 2.4); tt = np.arange(n) / SR                                                       # violin sting + bass drop
sting = sum(signal.sawtooth(2 * np.pi * f * tt * (1 + 0.004 * np.sin(2 * np.pi * 6.5 * tt))) for f in (1244.5, 1318.5, 1760, 1864.7))
sting = bp(sting, 900, 6000) * env_ar(n, 0.015, 1.6) * (0.8 + 0.2 * np.sin(2 * np.pi * 13 * tt))
drop = np.sin(2 * np.pi * (70 * tt - 18 * tt ** 2)) * np.exp(-tt * 1.4) * (tt < 1.9)
place(98.0, sting, db(-15)); place(98.0, drop, db(-4)); place(97.95, whoosh(0.2, 2000, 9000, -20))
def heartbeat(g):
    n = int(SR * 0.55); tt = np.arange(n) / SR
    beat = lambda d: np.where(tt >= d, np.sin(2 * np.pi * 52 * (tt - d)) * np.exp(-(tt - d) * 16), 0)
    return lp(beat(0) + 0.75 * beat(0.17), 200) * db(g)
tb = 98.6
while tb < DUR:
    rate = 1.12 + 0.3 * min(1, (tb - 98.6) / 13.0)
    g = -12 + 4 * min(1, (tb - 98.6) / 13.0) + (5 if tb > 112.4 else 0)
    place(tb, heartbeat(g)); tb += 1 / rate
place(102.9, whoosh(0.3, 500, 5000, -21))
ln = int(SR * 0.08); place(104.55, hp(noise(ln), 2000) * expdec(ln, 40) + np.sin(2 * np.pi * 900 * np.arange(ln) / SR) * expdec(ln, 50) * 0.5, db(-16), 0.1)   # holster snap
place(106.95, whoosh(0.3, 500, 5000, -21))
n = int(SR * 1.3); tt = np.arange(n) / SR                                                     # blade slide + ring
shing = bp(noise(n), 2500, 9000) * np.sin(np.linspace(0, np.pi, n)) ** 2 * 0.5 + np.sin(2 * np.pi * 3520 * tt) * np.exp(-np.maximum(0, tt - 1.0) * 6) * (tt > 1.0) * 0.4
place(109.9, shing, db(-17), -0.35)
place(110.95, bell(4186, 0.6, -24), pan=-0.35)                                                 # glint ting

# ---------------------------------------------------------------- Scene 6 — freeze
place(111.9, whoosh(0.3, 300, 4000, -20))
n = int(SR * 2.2); tt = np.arange(n) / SR
freeze_hit = np.sin(2 * np.pi * 40 * tt) * np.exp(-tt * 2) + bp(noise(n), 200, 2000) * np.exp(-tt * 6) * 0.3
place(112.45, freeze_hit, db(-6))
rain_duck = 1 - 0.6 * seg(112.45, 112.9)

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
