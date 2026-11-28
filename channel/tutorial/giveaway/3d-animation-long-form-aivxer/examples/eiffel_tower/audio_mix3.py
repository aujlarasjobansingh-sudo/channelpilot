# 3D Animation Long Form - made by aivxer. Copyright (c) 2026 aivxer.
# Free for your own videos. Do not re-share, sell, or claim this skill as your own (see LICENSE.txt).
import numpy as np, soundfile as sf
from scipy.signal import resample_poly, butter, lfilter, fftconvolve
from timeline import CUE, LINES, END, SHOT_T, FLASH, A3

SR = 48000; N = int(SR * END)
rng = np.random.default_rng(5)


def bq(x, kind, f, q=0.707, gain=0.0):
    w = 2 * np.pi * f / SR; al = np.sin(w) / (2 * q); A = 10 ** (gain / 40); cw = np.cos(w)
    if kind == 'peak': b = [1 + al * A, -2 * cw, 1 - al * A]; a = [1 + al / A, -2 * cw, 1 - al / A]
    elif kind == 'hs':
        s = 2 * np.sqrt(A) * al
        b = [A * ((A + 1) + (A - 1) * cw + s), -2 * A * ((A - 1) + (A + 1) * cw), A * ((A + 1) + (A - 1) * cw - s)]
        a = [(A + 1) - (A - 1) * cw + s, 2 * ((A - 1) - (A + 1) * cw), (A + 1) - (A - 1) * cw - s]
    elif kind == 'ls':
        s = 2 * np.sqrt(A) * al
        b = [A * ((A + 1) - (A - 1) * cw + s), 2 * A * ((A - 1) - (A + 1) * cw), A * ((A + 1) - (A - 1) * cw - s)]
        a = [(A + 1) + (A - 1) * cw + s, -2 * ((A - 1) + (A + 1) * cw), (A + 1) + (A - 1) * cw - s]
    return lfilter(np.array(b) / a[0], np.array(a) / a[0], x)


def lp(x, fc, o=2): b, a = butter(o, fc / (SR / 2), 'low'); return lfilter(b, a, x)
def hp(x, fc, o=2): b, a = butter(o, fc / (SR / 2), 'high'); return lfilter(b, a, x)
def bp(x, f1, f2): b, a = butter(2, [f1 / (SR / 2), f2 / (SR / 2)], 'band'); return lfilter(b, a, x)


def comp(x, thr_db=-20, ratio=3.0, att=0.004, rel=0.12, makeup=0.0):
    env = np.zeros(len(x)); e = 0.0; a_ = np.exp(-1 / (att * SR)); r_ = np.exp(-1 / (rel * SR)); ax = np.abs(x)
    for i in range(len(x)):
        v = ax[i]; e = a_ * e + (1 - a_) * v if v > e else r_ * e + (1 - r_) * v; env[i] = e
    db = 20 * np.log10(env + 1e-9); over = np.maximum(db - thr_db, 0)
    return x * 10 ** ((-over * (1 - 1 / ratio) + makeup) / 20)


def deess(x, amt=0.55):
    s = hp(x, 5200); env = lp(np.abs(s), 60); g = 1 - amt * np.clip(env / (env.max() + 1e-9) * 2.2, 0, 1)
    return (x - s) + s * g


def room_ir(dur=0.28, bright=5000, seed=1):
    r = np.random.default_rng(seed); n = int(dur * SR); t = np.arange(n) / SR
    ir = r.standard_normal((n, 2)) * np.exp(-t * 22)[:, None]; ir[:int(.004 * SR)] = 0
    ir = np.stack([lp(ir[:, 0], bright), lp(ir[:, 1], bright)], 1); return ir / np.sqrt((ir ** 2).sum(0))


def voice_chain(s, sr, narrator=True):
    s = resample_poly(s, SR, sr); s = s / (np.abs(s).max() + 1e-9) * 0.7
    s = hp(s, 72); s = bq(s, 'peak', 280, 1.0, -2.0); s = bq(s, 'ls', 130, 0.7, 1.5 if narrator else 0)
    s = bq(s, 'peak', 3400, 0.9, 2.5); s = bq(s, 'hs', 8500, 0.7, 3.0)
    s = deess(s); s = comp(s, -22, 3.2, makeup=4.0)
    return s


def place(buf, x, t, gain=1.0, pan=0.0):
    i = int(t * SR)
    if x.ndim == 1:
        l, r = np.cos((pan + 1) * np.pi / 4) * 1.414, np.sin((pan + 1) * np.pi / 4) * 1.414
        x = np.stack([x * l, x * r], 1)
    j = min(i + len(x), len(buf))
    if i < len(buf): buf[i:j] += x[:j - i] * gain


voice = np.zeros((N, 2)); vmono = np.zeros(N)
IRN = room_ir(0.22, 6000, 1); IRC = room_ir(0.34, 4200, 2)
for k, t in CUE.items():
    s, sr = sf.read(f"{A3}/{k}.wav"); narr = k.startswith('n')
    d = voice_chain(s, sr, narr)
    wet = np.stack([fftconvolve(d, (IRN if narr else IRC)[:, ch])[:len(d) + 8000] for ch in (0, 1)], 1)
    dry = np.zeros_like(wet); pan = 0.0 if narr else (0.28 if k == 'b1' else -0.28)
    place(dry, d, 0, 1.0, pan)
    place(voice, dry + wet * (0.05 if narr else 0.16), t)
    i = int(t * SR); vmono[i:i + len(d)] += d[:max(0, N - i)]

# ------------------------------------------------------------ music (original; A minor, 104 bpm, sneaky + musette colour)
bpm = 104; beat = 60 / bpm; e8 = beat / 2; bar = 4 * beat
music = np.zeros((N + SR, 2))
hz = lambda n: 440 * 2 ** ((n - 69) / 12)


def pluck(f, dur=0.34, amp=0.5, decay=10):
    n = int(dur * SR); t = np.arange(n) / SR; env = np.exp(-t * decay) * (1 - np.exp(-t * 500))
    return amp * env * (np.sin(2 * np.pi * f * t) + .5 * np.sin(4 * np.pi * f * t) + .22 * np.sin(6 * np.pi * f * t) + .1 * np.sin(8 * np.pi * f * t))


def bass(f, dur=0.42, amp=0.6):
    n = int(dur * SR); t = np.arange(n) / SR; env = np.exp(-t * 6) * (1 - np.exp(-t * 300))
    return amp * env * lp(np.sin(2 * np.pi * f * t) + .6 * np.sin(4 * np.pi * f * t) + .25 * np.sin(6 * np.pi * f * t), 900)


def vibes(f, dur=0.9, amp=0.2):
    n = int(dur * SR); t = np.arange(n) / SR; env = np.exp(-t * 4.5) * (1 - np.exp(-t * 900))
    return amp * env * (np.sin(2 * np.pi * f * t) + .3 * np.sin(2 * np.pi * 4 * f * t) * np.exp(-t * 14)) * (1 + .25 * np.sin(2 * np.pi * 5.5 * t))


def accordion(freqs, dur, amp=0.05):
    n = int(dur * SR); t = np.arange(n) / SR; out = np.zeros(n)
    for f in freqs:
        for d in (-1.8, 0, 2.1):
            ph = ((f + d) * t) % 1; out += (2 * ph - 1) + .5 * np.sign(np.sin(2 * np.pi * (f + d) * t))
    out = bp(out, 300, 3200); env = np.minimum(1, t / .12) * np.minimum(1, (dur - t) / .2) * (1 + .12 * np.sin(2 * np.pi * 5 * t))
    return amp * out * env / len(freqs)


def brush(amp=0.06, dur=0.07):
    n = int(dur * SR); return amp * hp(rng.standard_normal(n), 5500) * np.exp(-np.arange(n) / SR * 55)


def kick(amp=0.4):
    n = int(.22 * SR); t = np.arange(n) / SR; return amp * np.sin(2 * np.pi * (48 + 70 * np.exp(-t * 34)) * t) * np.exp(-t * 15)


prog = [(45, [57, 60, 64]), (41, [53, 57, 60]), (38, [50, 53, 57]), (40, [52, 56, 59])]
walk = [[0, 3, 7, 3], [0, 4, 7, 4], [0, 3, 7, 10], [0, 4, 7, 11]]
motifs = [[76, None, 75, 76, None, 72, None, None], [None, 69, None, 72, 71, None, 69, None], [77, None, 76, 74, None, 72, None, 74], [None, 71, 72, None, 76, None, 80, None]]
card0, card1 = SHOT_T['card']; tw0 = SHOT_T['tower'][0]
t = 0.0; bi = 0
while t < END:
    root, ch = prog[bi % 4]; mute = (t + bar * .5 > card0 and t < card1 - .1)
    if not mute:
        place(music, accordion([hz(n) for n in ch], bar * .98, 0.05), t, 1.0, -0.2)
        for i, off in enumerate(walk[bi % 4]): place(music, bass(hz(root - 12 + off + 12), beat * .95, .55), t + i * beat, 1.0, 0.0)
        for i in (1, 3): place(music, pluck(hz(ch[0] + 12), .2, .18) + pluck(hz(ch[1] + 12), .2, .18) + pluck(hz(ch[2] + 12), .2, .18), t + i * beat, 1.0, 0.25)
        for i, n in enumerate(motifs[bi % 4]):
            if n: place(music, vibes(hz(n), .8, .15), t + i * e8, 1.0, -0.3 + .08 * i)
        for i in range(8): place(music, brush(.07 if i % 2 == 0 else .04), t + i * e8 + (0.03 if i % 2 else 0), 1.0, 0.3)
        for i in (0, 2): place(music, kick(.32), t + i * beat)
    t += bar; bi += 1
music = music[:N]
tt = np.arange(N) / SR
g = np.ones(N); g[(tt > card0 - .05) & (tt < card1)] = 0.0; g = lp(g, 10, 1)
music *= g[:, None]; music *= np.minimum(1, tt / .25)[:, None]
music *= np.where(tt > FLASH, np.clip(1 - (tt - FLASH) / .08, 0, 1), 1)[:, None]
# final sting chord on the flash + resolve
for n, pan in ((45, 0), (57, -.3), (64, .3), (68, .1), (72, -.1)): place(music, vibes(hz(n), 1.6, .22) + pluck(hz(n), 1.6, .2, 4), FLASH, 1.0, pan)
# suspended tone under the text card
n_ = int((card1 - card0) * SR); t_ = np.arange(n_) / SR
drone = lp(np.sin(2 * np.pi * 55 * t_) + .4 * np.sin(2 * np.pi * 110.4 * t_) + .2 * np.sin(2 * np.pi * 164.8 * t_), 500) * np.minimum(1, t_ / .3) * np.minimum(1, (card1 - card0 - t_) / .3) * .16
place(music, drone, card0)

# ------------------------------------------------------------ SFX
sfx = np.zeros((N, 2))


def whoosh(dur=0.5):
    n = int(dur * SR); x = rng.standard_normal(n); out = np.zeros(n); seg = 600
    for i in range(0, n, seg):
        u = i / n; fc = 350 + 5200 * np.sin(np.pi * u) ** 1.3
        y = bp(x[i:i + seg], max(fc * .55, 120), min(fc * 1.6, 16000)); out[i:i + len(y)] = y
    return out * np.sin(np.pi * np.arange(n) / n) ** 2 * 1.3


def popfx(f0=340):
    n = int(.13 * SR); t = np.arange(n) / SR; return np.sin(2 * np.pi * (f0 + 900 * np.exp(-t * 42)) * t) * np.exp(-t * 34) * .6


def thud(big=False):
    n = int(.7 * SR); t = np.arange(n) / SR
    out = np.sin(2 * np.pi * (42 + 95 * np.exp(-t * 26)) * t) * np.exp(-t * 8) + lp(rng.standard_normal(n), 2800) * np.exp(-t * 38) * .7
    if big: out += hp(rng.standard_normal(n), 3500) * np.exp(-t * 7) * .22
    return out * .9


def tick(): n = int(.016 * SR); return hp(rng.standard_normal(n), 2800) * np.exp(-np.arange(n) / SR * 280) * .5


def step():
    n = int(.09 * SR); t = np.arange(n) / SR
    return (lp(rng.standard_normal(n), 1400) * np.exp(-t * 60) * .8 + np.sin(2 * np.pi * 150 * t) * np.exp(-t * 50) * .5)


def shutter():
    out = np.zeros(int(.45 * SR)); a = tick() * 2.2; out[:len(a)] += a; k = int(.07 * SR); out[k:k + len(a)] += a
    n = len(out); t = np.arange(n) / SR; out += hp(rng.standard_normal(n), 6000) * np.exp(-t * 12) * .12; return out


def scribble(dur=.42):
    n = int(dur * SR); t = np.arange(n) / SR; return bp(rng.standard_normal(n), 1400, 5200) * (0.5 + 0.5 * np.sin(2 * np.pi * 13 * t)) * .26


def boom():
    n = int(1.6 * SR); t = np.arange(n) / SR; return np.sin(2 * np.pi * 36 * t) * np.exp(-t * 2.4) * .8 + lp(rng.standard_normal(n), 180) * np.exp(-t * 3) * .4


def ding():
    n = int(.9 * SR); t = np.arange(n) / SR; return (np.sin(2 * np.pi * 2637 * t) + .5 * np.sin(2 * np.pi * 3951 * t)) * np.exp(-t * 7) * .25


def paper():
    n = int(.35 * SR); t = np.arange(n) / SR; return bp(rng.standard_normal(n), 900, 7000) * np.sin(np.pi * t / .35) ** 2 * .35


n3, n5, n6, c1 = CUE['n3'], CUE['n5'], CUE['n6'], CUE['c1']
for tw, pan in ((SHOT_T['office'][0], -.3), (SHOT_T['table'][0], .3), (SHOT_T['hero'][0], -.2)): place(sfx, whoosh(.5), tw - .3, .5, pan)
place(sfx, popfx(), 3.6, .5, -.2); place(sfx, popfx(420), 4.55, .8, -.3)
place(sfx, paper(), SHOT_T['table'][0] + .08, .9, -.4)
place(sfx, popfx(), n3 + .15, .7, .3)
for i in range(20): place(sfx, tick(), n3 + .25 + i * 0.055, .55, .3)
place(sfx, paper(), n3 + 1.75, .8, .5); place(sfx, popfx(380), n3 + 1.95, .8, 0.1)
place(sfx, ding(), c1 + LINES['c1']['dur'] - .12, .8, -.2)
place(sfx, boom(), card0, .7)
place(sfx, thud(True), n5 + .42, 1.15)
s0 = SHOT_T['hero'][0]
for i in range(4): place(sfx, step(), s0 + .12 + i * 0.285, .55, -.5 + i * .12)
place(sfx, popfx(300), n6 + .5, .55, .3); place(sfx, whoosh(.22), n6 + .5, .18, -.1)
place(sfx, shutter(), FLASH, 1.0); place(sfx, scribble(.4), FLASH + .3, .8, -.2); place(sfx, popfx(360), FLASH + .68, .6, -.3)
# faint room tone glue
tone = lp(rng.standard_normal(N), 400) * 0.004
sfx += tone[:, None]

# ------------------------------------------------------------ mix
env = lp(np.abs(vmono), 5, 1); env /= env.max() + 1e-9
duck = (1 - 0.6 * np.clip(env * 3.2, 0, 1))[:, None]
mix = voice * 1.0 + music * 0.36 * duck + sfx * 0.5
mix = np.tanh(mix * 1.15) / np.tanh(1.15)
sf.write("/home/claude/vid/audio3/mix_raw.wav", mix.astype(np.float32), SR)
print("ok", float(np.abs(mix).max()))
