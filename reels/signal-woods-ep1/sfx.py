"""THE SIGNAL IN THE WOODS — Ep1 sound: synthesized SFX + an original 80s synth horror score + dialogue.
Everything is generated in code (royalty-free). Usage: python3 sfx.py -> out/mix.wav (-14 LUFS)
"""
import os, json, subprocess
import numpy as np, soundfile as sf
from scipy import signal

HERE = os.path.dirname(os.path.abspath(__file__)); SR = 48000; DUR = 97.0; N = int(DUR * SR)
t = np.arange(N) / SR
rng = np.random.default_rng(86)
DLG = json.load(open(os.path.join(HERE, 'out', 'dialogue.json')))
LN = {l['id']: l for l in DLG['lines']}
FREEZE = 88.4
FX = np.zeros((N, 2)); MU = np.zeros((N, 2))

def sos(k, f, o=4): return signal.butter(o, f, btype=k, fs=SR, output='sos')
def db(x): return 10 ** (x / 20)
def mtof(n): return 440 * 2 ** ((n - 69) / 12)
def noise(n): return rng.standard_normal(n)
def env(n, a, r):
    e = np.ones(n); a = max(1, min(int(a * SR), n)); r = max(1, min(int(r * SR), n)); e[:a] = np.linspace(0, 1, a); e[-r:] *= np.linspace(1, 0, r); return e
def place(buf, st, x, g=1.0, pan=0.0):
    i = int(st * SR)
    if i >= N: return
    if i < 0: x = x[-i:]; i = 0
    n = min(len(x), N - i)
    buf[i:i + n, 0] += x[:n] * g * np.sqrt(0.5 * (1 - pan)) * 1.414; buf[i:i + n, 1] += x[:n] * g * np.sqrt(0.5 * (1 + pan)) * 1.414
def gate(a, b, fi=0.3, fo=0.3): return np.clip((t - a) / max(fi, 1e-3), 0, 1) * np.clip((b - t) / max(fo, 1e-3), 0, 1)
def saw(f, n, det=0.0):
    f = np.broadcast_to(np.asarray(f, float), (n,)) * (1 + det); ph = np.cumsum(f) / SR % 1.0; return 2 * ph - 1
def pulse(f, n, w=0.5):
    f = np.broadcast_to(np.asarray(f, float), (n,)); ph = np.cumsum(f) / SR % 1.0; return np.where(ph < w, 1.0, -1.0)
def both(x): return np.stack([x, x], 1)

# ======================================================================= SFX
# night bed: crickets until the blackout, wind all the way
cr = np.zeros(N)
for f0, rate, ph in ((4300, 2.9, 0), (4700, 3.4, 1.3), (3900, 2.5, 2.1), (5100, 3.8, .7)):
    chirp = (np.sin(2 * np.pi * rate * t + ph) > 0.55) * (np.sin(2 * np.pi * 38 * t) > 0)
    cr += np.sin(2 * np.pi * f0 * t) * signal.sosfilt(sos('low', 300, 2), chirp.astype(float))
cr *= np.clip((24.9 - t) / 0.02, 0, 1)
FX[:, 0] += cr * db(-33); FX[:, 1] += np.roll(cr, 900) * db(-33)
wind = signal.sosfilt(sos('band', [120, 900], 2), noise(N)) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.07 * t)) * (1 + 0.6 * gate(30, 97, 2, 1))
FX += both(wind * db(-36) * np.where(t > FREEZE, 0.25, 1))

# BMX: freewheel ticking + tyre hum on asphalt (speed-driven), then the skid
VR, B0, ST = 4.2, 18.3, 19.7
speed = np.where(t < B0, VR, np.where(t < ST, VR * (1 - (t - B0) / (ST - B0)), 0))
hum = signal.sosfilt(sos('band', [90, 700], 2), noise(N)) * (speed / VR)
FX += both(hum * db(-27))
pedal = (speed / VR) * (np.sin(2 * np.pi * 1.6 * t) > -0.2)
ticks = (np.sin(2 * np.pi * 14 * np.cumsum(speed / VR) / SR) > 0.97).astype(float)
ticks = signal.sosfilt(sos('high', 2500), ticks) * pedal
FX += both(ticks * db(-24))
n = int(1.4 * SR); sk = signal.sosfilt(sos('band', [1800, 4200], 2), noise(n)) * np.sin(np.linspace(0, np.pi, n)) ** 0.6
sk *= 1 + 0.4 * np.sin(2 * np.pi * 23 * np.arange(n) / SR); place(FX, B0, sk, db(-18), 0.1)
place(FX, B0, signal.sosfilt(sos('band', [200, 900]), noise(n)) * env(n, .05, .8), db(-22))

def buzz(d, g=1.0, f=120):
    n = int(d * SR); tt = np.arange(n) / SR
    x = np.sign(np.sin(2 * np.pi * f * tt)) * 0.5 + signal.sosfilt(sos('band', [1500, 6000], 2), noise(n)) * 0.6
    return x * env(n, .002, .01) * g
def click(g=1.0, f=3000):
    n = int(.03 * SR); tt = np.arange(n) / SR; return signal.sosfilt(sos('band', [f * .5, f * 2], 2), noise(n)) * np.exp(-tt * 200) * g
# headlight dying: BZZT flickers, then the taps
for k, on in enumerate([1, 0.2, 1, 1, 0, 0.8, 0.1, 1, 0, 0, 0.6, 0, 0.9, 0, 0, 0.3]):
    if 0.05 < on < 0.95 or (k and on == 0): place(FX, 17.6 + k * 0.05, buzz(0.05, 0.7), db(-20), 0.05)
place(FX, 18.4, buzz(0.18, 1.0), db(-17)); place(FX, 18.42, click(1.0, 1500), db(-14))
for tt0 in (20.3, 20.75): place(FX, tt0, click(1.0, 900), db(-12)); place(FX, tt0 + 0.05, buzz(0.06, 0.6), db(-22))

# streetlights: hum, buzz, POP (glass + thump), one after another
POPS = [22.3, 22.75, 23.2, 23.65, 24.1, 24.35, 24.5, 24.6]
lh = np.sin(2 * np.pi * 120 * t) * 0.5 + np.sin(2 * np.pi * 240 * t) * 0.3
FX += both(signal.sosfilt(sos('band', [100, 400], 2), lh) * db(-38) * np.clip((24.6 - t) / 0.05, 0, 1))
for i, p in enumerate(POPS):
    near = 1 - abs(i - 4) / 5
    place(FX, p - 0.45, buzz(0.42, 0.5, 120 + i * 7) * np.sin(np.linspace(0, np.pi, int(.42 * SR))) ** 2, db(-30 + 8 * near), 0.4)
    n = int(.35 * SR); tt = np.arange(n) / SR
    pop = signal.sosfilt(sos('band', [1200, 9000], 2), noise(n)) * np.exp(-tt * 40) + np.sin(2 * np.pi * 70 * tt) * np.exp(-tt * 18) * 0.8
    place(FX, p, pop, db(-22 + 12 * near), 0.35 - near * 0.3)
    n2 = int(.4 * SR); place(FX, p + 0.04, signal.sosfilt(sos('high', 4000), noise(n2)) * np.exp(-np.arange(n2) / SR * 12) * 0.4, db(-26 + 8 * near), 0.5)   # glass tinkle

# walkie: squelch bursts, roger clicks, the static reply, the feedback screech
def kshh(d, g=1.0):
    n = int(d * SR); x = signal.sosfilt(sos('band', [900, 6500], 2), noise(n)); x *= 0.7 + 0.3 * np.sin(2 * np.pi * 9 * np.arange(n) / SR)
    return x * env(n, .005, .06) * g
for lid in ('l1', 'l6', 'l11'):
    l = LN[lid]; place(FX, l['t0'] - 0.18, kshh(0.18), db(-21), 0.3); place(FX, l['t1'] + 0.02, kshh(0.22), db(-21), 0.3)
for lid in ('l2', 'l4', 'l7'):
    l = LN[lid]; place(FX, l['t0'] - 0.15, click(1, 2500), db(-19), 0.3); place(FX, l['t1'] + 0.05, click(1, 2500), db(-19), 0.3)
    n = int(.12 * SR); place(FX, l['t1'] + 0.08, np.sin(2 * np.pi * 1400 * np.arange(n) / SR) * env(n, .005, .02) * 0.4, db(-26), 0.3)
place(FX, 29.4, kshh(0.9), db(-17), 0.3)                       # no answer, just static
n = int(0.45 * SR); tt = np.arange(n) / SR
fb = np.sin(2 * np.pi * np.cumsum(2200 + 1800 * tt / 0.45) / SR) * env(n, .01, .08) + 0.4 * signal.sosfilt(sos('band', [2000, 7000]), noise(n))
place(FX, 76.92, fb, db(-17), 0.3)                              # radio screeches out after "RUN!"

# low rumble when the red glow appears; rift hum after it opens
rum = signal.sosfilt(sos('low', 70, 4), noise(N)) * 3 + np.sin(2 * np.pi * 38 * t) * 0.4
FX += both(rum * db(-24) * (gate(30.0, 200, 2.5) * 0.7 + gate(63.9, 200, 0.3) * 0.6) * np.where(t > FREEZE, np.exp(-(t - FREEZE) * 3), 1))
rh = (np.sin(2 * np.pi * 55 * t) + 0.5 * np.sin(2 * np.pi * 82.5 * t + np.sin(2 * np.pi * 0.3 * t) * 3)) * gate(63.9, FREEZE, 0.5, 0.02)
FX += both(signal.sosfilt(sos('low', 400), rh) * db(-28))
n = int(2.4 * SR); tt = np.arange(n) / SR                        # the rift tears open
tear = signal.sosfilt(sos('band', [300, 5000], 2), noise(n)) * (np.abs(np.sin(2 * np.pi * 27 * tt)) ** 4) * np.exp(-tt * 1.5) + np.sin(2 * np.pi * 45 * tt) * np.exp(-tt * 1.2)
place(FX, 63.85, tear, db(-11), -0.4)

# Leo bursting out of the trees: branches + leaf footsteps
n = int(2.0 * SR); place(FX, 46.7, signal.sosfilt(sos('band', [600, 5000], 2), noise(n)) * env(n, .2, .6) * (0.6 + 0.4 * (np.sin(2 * np.pi * 6 * np.arange(n) / SR) > 0)), db(-21), -0.5)
for k in np.arange(46.9, 48.7, 1 / 6.0): place(FX, k, signal.sosfilt(sos('band', [300, 3000], 2), noise(int(.08 * SR))) * env(int(.08 * SR), .003, .07), db(-20), -0.5)
for p in (47.3, 47.9): place(FX, p, click(1, 1800) * 3, db(-16), -0.5)        # twig snaps
# chain-link rattles
def rattle(d, g=1.0, rate=14):
    n = int(d * SR); tt = np.arange(n) / SR
    x = sum(np.sin(2 * np.pi * f * tt + rng.random() * 6) for f in (1830, 2470, 3120, 4210)) * 0.25 + signal.sosfilt(sos('band', [1500, 7000], 2), noise(n)) * 0.5
    return x * (0.3 + 0.7 * np.abs(np.sin(np.pi * rate * tt))) * env(n, .01, .15) * g
place(FX, 48.7, rattle(0.5, 1.0), db(-17), -0.3); place(FX, 49.2, rattle(5.2, 0.6), db(-23), -0.3)
place(FX, 58.6, rattle(0.4, 1.0), db(-15), -0.1); place(FX, 59.0, rattle(3.0, 0.5), db(-25))
place(FX, 77.25, rattle(0.4, 1.0), db(-16), -0.2); place(FX, 79.0, rattle(7.8, 0.6, 18), db(-24), -0.2)
# bike dropped on the asphalt, then running to the fence
n = int(1.0 * SR); tt = np.arange(n) / SR
clat = sum(np.sin(2 * np.pi * f * tt) for f in (620, 1130, 1790, 2650)) * np.exp(-tt * 6) * 0.3 + signal.sosfilt(sos('band', [400, 6000], 2), noise(n)) * np.exp(-tt * 14)
place(FX, 55.15, clat, db(-12), 0.4); place(FX, 55.35, clat[:int(.4 * SR)] * 0.5, db(-16), 0.4)
for i, k in enumerate(np.arange(55.45, 58.4, 1 / 2.9)):
    grass = k > 56.6; n = int(.1 * SR)
    st = signal.sosfilt(sos('band', [150, 2500] if grass else [200, 4000], 2), noise(n)) * env(n, .002, .09)
    place(FX, k, st, db(-17), -0.15 if i % 2 else 0.15)
FX += both(signal.sosfilt(sos('band', [300, 1500], 2), noise(N)) * np.abs(np.sin(2 * np.pi * 1.4 * t)) * gate(55.6, FREEZE, 0.5, 0.05) * db(-34))   # heavy breathing
# the creature's slow, heavy steps (wood cracking)
for k in (65.2, 65.9, 66.6, 67.3, 68.0):
    n = int(.5 * SR); tt = np.arange(n) / SR
    place(FX, k, np.sin(2 * np.pi * 50 * tt) * np.exp(-tt * 9) + signal.sosfilt(sos('band', [400, 3000], 2), noise(n)) * np.exp(-tt * 25) * 0.6, db(-17), -0.5)
# INHUMAN SHRIEK, cut dead on the freeze
n = int((FREEZE - 86.9) * SR); tt = np.arange(n) / SR
f0 = 520 + 900 * (1 - np.exp(-tt * 6)) + 60 * np.sin(2 * np.pi * 9 * tt)
sh = sum(saw(f0 * m, n, d) for m, d in ((1, 0), (1.51, .01), (2.03, -.01), (0.74, .02))) / 4
sh = signal.sosfilt(sos('band', [700, 6500], 2), np.tanh(sh * 3)) + signal.sosfilt(sos('band', [2000, 9000], 2), noise(n)) * 0.6
sh *= env(n, .02, .01)
place(FX, 86.9, sh, db(-6), -0.35); place(FX, 86.95, np.roll(sh, 300) * 0.7, db(-8), 0.35)
FX[int(FREEZE * SR):] *= np.exp(-(t[int(FREEZE * SR):] - FREEZE) * 40)[:, None] * 1.0 + 0.0
# synth heartbeat under the voice-over / end screen
for k in np.arange(88.7, 96.6, 0.92):
    for d, g in ((0, 1), (0.24, 0.7)):
        n = int(.35 * SR); tt = np.arange(n) / SR
        place(FX, k + d, np.sin(2 * np.pi * (55 + 30 * np.exp(-tt * 25)) * tt) * np.exp(-tt * 9) * g, db(-11))

# ======================================================================= SCORE (original 80s synth horror)
def arp(a, b, bpm, notes, g, cut=1800, div=4, pan=0.0, fall=0.6):
    step = 60 / bpm / div * 4 / 4
    for k, st in enumerate(np.arange(a, b, step)):
        n = int(step * SR * 0.95); nn = notes[k % len(notes)]
        x = (saw(mtof(nn), n, -0.004) + pulse(mtof(nn), n, 0.3) * 0.6) * 0.5
        e = np.exp(-np.arange(n) / SR / (step * fall))
        x = signal.sosfilt(sos('low', cut, 2), x) * e
        place(MU, st, x, g, pan * (1 if k % 2 else -1))
def pad(a, b, chord, g, cut=900, fi=1.5, fo=1.5):
    i0, i1 = int(a * SR), int(min(b, DUR) * SR); n = i1 - i0
    x = sum(saw(mtof(nn), n, d) for nn in chord for d in (-0.006, 0.0, 0.007)) / (3 * len(chord))
    x = signal.sosfilt(sos('low', cut, 2), x) * env(n, fi, fo)
    lfo = 1 + 0.25 * np.sin(2 * np.pi * 0.2 * np.arange(n) / SR)
    MU[i0:i1, 0] += x * g * lfo; MU[i0:i1, 1] += np.roll(x, 400) * g * (2 - lfo)
def bassp(a, b, bpm, notes, g):
    step = 60 / bpm / 2
    for k, st in enumerate(np.arange(a, b, step)):
        n = int(step * SR * 0.9); x = signal.sosfilt(sos('low', 300, 2), saw(mtof(notes[k % len(notes)]), n)) * env(n, .005, step * .5)
        place(MU, st, x, g)
def braam(dur=3.0):
    n = int(SR * dur); x = sum(saw(mtof(nn), n, d) for nn in (33, 40, 45) for d in (-.006, 0, .007)) / 9
    return np.tanh(signal.sosfilt(sos('low', 650, 2), x) * 3) * env(n, .04, dur * .7)
def riser(dur):
    n = int(SR * dur); tt = np.arange(n) / SR; k = (tt / dur) ** 2
    return signal.sosfilt(sos('band', [700, 9000], 2), noise(n)) * k + np.sin(2 * np.pi * np.cumsum(200 + 1800 * k) / SR) * k * 0.3
def stinger():
    n = int(SR * 2.0); tt = np.arange(n) / SR
    x = sum(saw(mtof(nn), n, .003 * k) for k, nn in enumerate((81, 82, 88, 89, 94)))
    return signal.sosfilt(sos('band', [900, 7000], 2), x) * env(n, .01, 1.5) / 3
# 1) nostalgic ride: A-minor arp (A C E F E C A G#), warm pad
RIDE = [57, 60, 64, 65, 64, 60, 57, 56]
arp(0.0, 17.6, 104, RIDE, db(-17), cut=1500, pan=0.2)
pad(0.0, 18.4, [45, 52, 57, 60], db(-15), cut=800, fi=2.0, fo=0.4)
pad(0.0, 18.4, [33], db(-14), cut=200, fi=2.0, fo=0.4)
# 2) headlight dies → lights pop: a single high detuned note that bends down, then nothing
n = int(6.5 * SR); tt = np.arange(n) / SR
place(MU, 18.4, signal.sosfilt(sos('low', 2500, 2), saw(mtof(76) * (1 - 0.06 * tt / 6.5), n, .004) + saw(mtof(76) * (1 - 0.06 * tt / 6.5), n, -.004)) * env(n, .5, 1.0), db(-24), 0.2)
# 3) the woods: sub drone + slow pulse that keeps quickening
pad(30.2, 63.9, [33, 40], db(-14), cut=260, fi=3.0, fo=0.1)
pad(33.0, 63.9, [57, 58], db(-25), cut=1600, fi=4.0, fo=0.1)            # the dissonant minor second
bassp(37.2, 47.0, 84, [33, 33, 33, 34], db(-16))
# 4) "Leo" appears: dark arp returns, faster
DARK = [57, 60, 63, 64, 63, 60, 58, 57]
arp(47.0, 63.9, 128, DARK, db(-18), cut=2200, pan=0.3, fall=0.5)
bassp(47.0, 63.9, 128, [33, 33, 45, 33, 34, 33, 45, 34], db(-15))
place(MU, 47.0, stinger(), db(-15), -0.2)
place(MU, 62.4, riser(1.5), db(-17))
# 5) the rift opens: BRAAM, driving pulse under the radio contradiction
place(MU, 63.9, braam(3.5), db(-8)); place(MU, 63.9, stinger(), db(-14), 0.3)
arp(66.5, 77.1, 140, [45, 45, 57, 45, 46, 45, 58, 45], db(-17), cut=1800, pan=0.25, fall=0.45)
bassp(66.5, 77.1, 140, [33, 33, 33, 34], db(-14))
for k in np.arange(69.2, 77.0, 60 / 140 * 2):
    n = int(.5 * SR); tt = np.arange(n) / SR
    place(MU, k, np.sin(2 * np.pi * np.cumsum(70 * (1 + 0.6 * np.exp(-tt * 30))) / SR) * np.exp(-tt * 7), db(-14))   # toms
pad(66.5, FREEZE, [45, 46, 52], db(-19), cut=1100, fi=1.0, fo=0.02)
# 6) whip back to "Leo" with black eyes: stinger; rising whine to the shriek
place(MU, 77.2, stinger(), db(-12), -0.3); place(MU, 77.2, braam(2.5), db(-13))
n = int((86.9 - 79.0) * SR); tt = np.arange(n) / SR
place(MU, 79.0, np.sin(2 * np.pi * np.cumsum(1500 + 500 * tt / 7.9 + 20 * np.sin(2 * np.pi * 5.5 * tt)) / SR) * (tt / 7.9) ** 1.5, db(-27), 0.4)
place(MU, 85.0, riser(1.9), db(-15))
place(MU, 86.9, braam(1.5), db(-7))
MU[int(FREEZE * SR):] *= 0
# 7) freeze / VO / CTA: low pad and a slow, sad version of the ride arp
pad(88.5, DUR, [45, 52, 60], db(-18), cut=700, fi=1.0, fo=2.0)
arp(89.0, 96.0, 80, [69, 72, 76, 77, 76, 72, 69, 68], db(-24), cut=1400, div=2, pan=0.3)

# ======================================================================= mix: duck music + fx under dialogue, normalise
dlg, _ = sf.read(os.path.join(HERE, 'out', 'dialogue.wav'), always_2d=True)
dlg = np.pad(dlg, ((0, max(0, N - len(dlg))), (0, 0)))[:N]
e = signal.sosfilt(sos('low', 6, 2), np.abs(dlg[:, 0])); e = np.clip(e / (e.max() + 1e-9) * 7, 0, 1)
MU *= (1 - 0.55 * e)[:, None]; FX *= (1 - 0.3 * e)[:, None]
MU *= db(-7) / (np.abs(MU).max() + 1e-9)
FX *= db(-3) / (np.abs(FX).max() + 1e-9)
out = dlg * db(0) + FX + MU
out *= 0.95 / np.abs(out).max()
raw = os.path.join(HERE, 'out', 'mix_raw.wav'); sf.write(raw, out.astype(np.float32), SR, subtype='PCM_24')
fin = os.path.join(HERE, 'out', 'mix.wav')
st = subprocess.run(['ffmpeg', '-hide_banner', '-i', raw, '-af', 'acompressor=threshold=0.15:ratio=2.5:attack=5:release=150:makeup=1.3,loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json', '-f', 'null', '-'], capture_output=True, text=True).stderr
js = json.loads(st[st.rindex('{'):st.rindex('}') + 1])
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', raw, '-af', 'acompressor=threshold=0.15:ratio=2.5:attack=5:release=150:makeup=1.3,'
                f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={js['input_i']}:measured_TP={js['input_tp']}:measured_LRA={js['input_lra']}:measured_thresh={js['input_thresh']}:offset={js['target_offset']}:linear=true",
                '-ar', '48000', fin], check=True)
print('wrote', fin)
