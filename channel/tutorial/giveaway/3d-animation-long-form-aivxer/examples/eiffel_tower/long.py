# 3D Animation Long Form - made by aivxer. Copyright (c) 2026 aivxer.
# Free for your own videos. Do not re-share, sell, or claim this skill as your own (see LICENSE.txt).
"""2-minute cut: reuses the finished 21 s intro (scenes3/*.mp4) and adds the rest of the story."""
import sys, os, json, math, random, subprocess
import numpy as np, skia, soundfile as sf

A4 = "/home/claude/vid/audio4"; OUT = "/home/claude/vid/scenes4"; T0 = 21.0
NARR, CON, BUY = 16, 26, 18
TXT = {
 "n10": (NARR, "It starts with a newspaper."),
 "n11": (NARR, "The Eiffel Tower is rusting. Repairs cost a fortune. And Paris is wondering if it's even worth keeping."),
 "n12": (NARR, "Most people read that, and turn the page."),
 "n13": (NARR, "Victor Lustig reads it, and sees a product."),
 "n14": (NARR, "He prints fake government letterhead. Books a suite in one of the finest hotels in Paris."),
 "n15": (NARR, "And invites six scrap metal dealers to a very secret meeting."),
 "c2": (CON, "Gentlemen. The government is selling the tower. For scrap. Tell no one."),
 "b2": (BUY, "Why us?"),
 "c3": (CON, "Because you can keep a secret."),
 "n16": (NARR, "One dealer wants it badly. Andre Poisson. New in town, and desperate to make his name."),
 "n17": (NARR, "But Poisson gets nervous. Why the secrecy? Why the rush?"),
 "n18": (NARR, "So Lustig does something brilliant. He confesses."),
 "c4": (CON, "I am a poor civil servant, monsieur. A small gift would help things along."),
 "n19": (NARR, "A bribe. And to Poisson, that is proof."),
 "n20": (NARR, "Only a real official would be this corrupt."),
 "n21": (NARR, "So he pays. For the bribe, and for the tower."),
 "n22": (NARR, "Then Lustig boards a train to Vienna, with a suitcase full of cash."),
 "n23": (NARR, "And Poisson? He is too embarrassed to tell the police."),
 "n24": (NARR, "So nobody comes looking."),
 "n25": (NARR, "One month later, Lustig comes back. Finds a new set of dealers."),
 "n26": (NARR, "And sells the Eiffel Tower all over again."),
 "n27": (NARR, "This time, the buyer goes to the police. Lustig slips away to America."),
 "n28": (NARR, "Where his next mark is a man named Al Capone."),
 "n29": (NARR, "But that's another story."),
}
# (shot kind, arg, line keys)
SEQ = [("card", "The Idea", []), ("news", None, ["n10", "n11"]), ("lclose", "idea", ["n12", "n13"]),
       ("card", "The Pitch", []), ("letter", None, ["n14"]), ("meeting", None, ["n15", "c2"]),
       ("bclose", "why", ["b2"]), ("lclose", "secret", ["c3"]), ("bclose", "poisson", ["n16"]),
       ("card", "The Twist", []), ("bclose", "nervous", ["n17"]), ("lclose", "confess", ["n18", "c4"]),
       ("bclose", "proof", ["n19", "n20"]), ("pay", None, ["n21"]), ("map", None, ["n22"]),
       ("bclose", "shame", ["n23"]), ("card", "So nobody comes looking.", ["n24"]),
       ("paris2", None, ["n25"]), ("office2", None, ["n26"]), ("street2", None, ["n27", "n28"]),
       ("card", "But that's another story.", ["n29"])]


def tts():
    import sherpa_onnx
    M = "/home/claude/models/kokoro-multi-lang-v1_0"
    open("/home/claude/vid/lex_extra.txt", "w").write("eiffel ˈ I f ə l\nlustig l ˈ ʊ s t ɪ ɡ\npoisson p w ɑ s ˈ ɔ n\nandre ˈ ɑ n d r A\n")
    cfg = sherpa_onnx.OfflineTtsConfig(model=sherpa_onnx.OfflineTtsModelConfig(kokoro=sherpa_onnx.OfflineTtsKokoroModelConfig(
        model=f"{M}/model.onnx", voices=f"{M}/voices.bin", tokens=f"{M}/tokens.txt", data_dir=f"{M}/espeak-ng-data", dict_dir=f"{M}/dict",
        lexicon=f"/home/claude/vid/lex_extra.txt,{M}/lexicon-us-en.txt,{M}/lexicon-gb-en.txt", lang="en-us"), num_threads=4))
    t = sherpa_onnx.OfflineTts(cfg); os.makedirs(A4, exist_ok=True); out = {}
    for k, (sid, text) in TXT.items():
        a = t.generate(text, sid=sid, speed=1.03 if sid == NARR else 0.97); s = np.array(a.samples, dtype=np.float32)
        idx = np.where(np.abs(s) > 0.012 * np.abs(s).max())[0]; s = s[max(idx[0] - 300, 0): idx[-1] + 1500]
        sf.write(f"{A4}/{k}.wav", s, a.sample_rate); out[k] = {"dur": round(len(s) / a.sample_rate, 3)}
    json.dump(out, open(f"{A4}/lines.json", "w"))
    print("speech total", round(sum(v["dur"] for v in out.values()), 1))


if len(sys.argv) > 1 and sys.argv[1] == "tts":
    tts(); sys.exit()

DUR = json.load(open(f"{A4}/lines.json"))
CUE2 = {}; SH = []; cur = T0
for kind, arg, keys in SEQ:
    s0 = cur; cur += 0.3
    if not keys: cur += 1.2
    for k in keys: CUE2[k] = round(cur, 3); cur += DUR[k]["dur"] + 0.26
    cur += 0.12; cur = round(cur * 30) / 30
    SH.append(dict(kind=kind, arg=arg, keys=keys, s0=s0, s1=cur))
END2 = cur + 0.5; SH[-1]["s1"] = END2

if len(sys.argv) > 1 and sys.argv[1] == "audio":
    from scipy.signal import resample_poly, fftconvolve
    src = open("/home/claude/vid/audio_mix3.py").read()
    exec(src[:src.index("voice = np.zeros((N, 2))")]); exec(src[src.index("bpm = 104"):src.index("prog = [")])
    exec(src[src.index("def whoosh"):src.index("n3, n5, n6, c1 =")])
    L = END2 - T0; N = int(L * SR); voice = np.zeros((N, 2)); vm = np.zeros(N); music = np.zeros((N + SR, 2)); sfx = np.zeros((N, 2))
    IRN = room_ir(0.22, 6000, 1); IRC = room_ir(0.34, 4200, 2)
    for k, t in CUE2.items():
        s, sr = sf.read(f"{A4}/{k}.wav"); narr = k.startswith('n'); d = voice_chain(s, sr, narr)
        wet = np.stack([fftconvolve(d, (IRN if narr else IRC)[:, ch])[:len(d) + 8000] for ch in (0, 1)], 1)
        dry = np.zeros_like(wet); place(dry, d, 0, 1.0, 0.0 if narr else (0.28 if k[0] == 'b' else -0.28))
        place(voice, dry + wet * (0.05 if narr else 0.16), t - T0); i = int((t - T0) * SR); vm[i:i + len(d)] += d[:max(0, N - i)]
    prog = [(45, [57, 60, 64]), (41, [53, 57, 60]), (38, [50, 53, 57]), (40, [52, 56, 59])]
    walk = [[0, 3, 7, 3], [0, 4, 7, 4], [0, 3, 7, 10], [0, 4, 7, 11]]
    motifs = [[76, None, 75, 76, None, 72, None, None], [None, 69, None, 72, 71, None, 69, None], [77, None, 76, 74, None, 72, None, 74], [None, 71, 72, None, 76, None, 80, None]]
    cards = [(s["s0"] - T0, s["s1"] - T0) for s in SH if s["kind"] == "card"]
    t = 0.0; bi = 0
    while t < L:
        root, ch = prog[bi % 4]
        place(music, accordion([hz(n) for n in ch], bar * .98, 0.05), t, 1.0, -0.2)
        for i, off in enumerate(walk[bi % 4]): place(music, bass(hz(root + off), beat * .95, .55), t + i * beat)
        for i in (1, 3): place(music, sum(pluck(hz(n + 12), .2, .18) for n in ch), t + i * beat, 1.0, 0.25)
        if bi % 2 == 0 or bi > 20:
            for i, n in enumerate(motifs[bi % 4]):
                if n: place(music, vibes(hz(n), .8, .15), t + i * e8, 1.0, -0.3 + .08 * i)
        for i in range(8): place(music, brush(.07 if i % 2 == 0 else .04), t + i * e8 + (0.03 if i % 2 else 0), 1.0, 0.3)
        for i in (0, 2): place(music, kick(.32), t + i * beat)
        t += bar; bi += 1
    music = music[:N]; tt = np.arange(N) / SR; g = np.ones(N)
    for a, b in cards: g[(tt > a - .05) & (tt < b)] = 0.0; place(sfx, boom(), a, .6)
    g = lp(g, 10, 1); music *= g[:, None]; music *= np.minimum(1, tt / .25)[:, None]; music *= np.clip((L - .9 - tt) / .5, 0, 1)[:, None]
    for s in SH:
        a = s["s0"] - T0; kd = s["kind"]
        if kd in ("news", "letter", "pay"): place(sfx, paper(), a + .08, .9, -.3)
        if kd in ("map", "paris2", "street2", "meeting"): place(sfx, whoosh(.45), max(a - .25, 0), .4)
    ev = [("n11", 1.7, "pop"), ("n11", .3, "scribble"), ("n13", 1.2, "ding"), ("n14", .9, "thud"), ("n14", 3.0, "pop"), ("c2", 3.6, "thud"),
          ("n16", .9, "pop"), ("n17", 1.6, "pop"), ("n17", 2.6, "pop"), ("c4", 2.6, "ding"), ("n20", 1.2, "thud"), ("n21", 1.5, "thud"),
          ("n26", .6, "pop"), ("n26", 1.5, "thud"), ("n28", .5, "pop")]
    fx = {"pop": lambda: popfx(380), "ding": ding, "thud": lambda: thud(True), "scribble": lambda: scribble(.45)}
    for k, dt, nm in ev: place(sfx, fx[nm](), CUE2[k] - T0 + dt, .8)
    for i in range(int((SH[-2]["s1"] - SH[-2]["s0"]) / .285)): place(sfx, step(), SH[-2]["s0"] - T0 + .1 + i * .285, .4, -.5 + .04 * i)
    for i in range(14): place(sfx, tick() + 0, CUE2["n22"] - T0 + .6 + i * .14, .35)
    sfx += (lp(rng.standard_normal(N), 400) * 0.004)[:, None]
    env = lp(np.abs(vm), 5, 1); env /= env.max() + 1e-9; duck = (1 - 0.6 * np.clip(env * 3.2, 0, 1))[:, None]
    mix = np.tanh((voice + music * 0.36 * duck + sfx * 0.5) * 1.15) / np.tanh(1.15)
    intro, _ = sf.read("/home/claude/vid/audio3/mix_raw.wav")
    sf.write(f"{A4}/full_raw.wav", np.vstack([intro[:int(T0 * SR)], mix]).astype(np.float32), SR); print("audio ok", round(END2, 2)); sys.exit()

# ------------------------------------------------------------------ picture
from scenes3 import *
from lib import mouth_track
MO = {k: mouth_track(f"{A4}/{k}.wav") for k in ("c2", "c3", "c4", "b2")}


def sp2(key, gt):
    i = int(round((gt - CUE2[key]) * FPS)); tr = MO[key]; return tr[i] if 0 <= i < len(tr) else None


def af(key, gt, dt=0.0): return gt - (CUE2[key] + dt)
def frac(key, f): return DUR[key]["dur"] * f


_cache = {}
def cached(name, draw):
    if name not in _cache:
        s = skia.Surface(W + 600, H + 400); cc = s.getCanvas(); cc.translate(300, 200); draw(cc); _cache[name] = s.makeImageSnapshot()
    return _cache[name]


def table_base(c):
    c.drawRect(skia.Rect(-900, -700, W + 900, H + 700), sp(radial(960, 520, 1300, [hx('#F6EED4'), hx('#E6DBB8'), hx('#CDBF98')], [0, .6, 1])))
    for (sx, sy, r, a) in SPECK: c.drawCircle(sx, sy, r, fp('#9A8F6E', a))
    for (ya, yb) in ((-700, 64), (1016, H + 700)): c.drawRect(skia.Rect(-900, ya, W + 900, yb), fp('#2F6B45'))
    for yy in (64, 1016): line(c, -900, yy, W + 900, yy, LW)


def textlines(c, x0, y0, x1, n, gap=30, v='#8E8878'):
    r = random.Random(int(x0 + y0))
    for i in range(n): c.drawLine(x0, y0 + i * gap, x1 - r.uniform(0, (x1 - x0) * .3), y0 + i * gap, ink(6, v))


def sh_card(c, gt, S):
    c.drawRect(skia.Rect(-W, -H, 2 * W, 2 * H), fp((0, 0, 0)))
    words = S["arg"].split(); key = S["keys"][0] if S["keys"] else None
    t0 = CUE2[key] if key else S["s0"] + .2; d = (DUR[key]["dur"] - .15) if key else .5
    tot = sum(len(w) + 1 for w in words); acc = 0; k = 0
    for w in words:
        if gt >= t0 + d * acc / tot - .04: k += 1
        acc += len(w) + 1
    f = skia.Font(FONT_HAND, 150 if not key else 130); full = f.measureText(S["arg"])
    if k: c.drawString(" ".join(words[:k]), W / 2 - full / 2, H / 2 + 44, f, fp('#FFFFFF'))


def sh_news(c, gt, S):
    table_base(c); k = back(K(gt, S["s0"] + .05, .5), 1.3); px = lerp(-700, 760, k)
    c.save(); c.translate(px, 545); c.rotate(4)
    c.drawRect(skia.Rect(-392, -288, 412, 312), fp((60, 40, 10), 70, blur=12)); rect(c, -400, -300, 400, 300, '#F1EAD6', LW)
    label(c, "LE JOURNAL", 0, -222, 84, INK, font=MARKER, align='center', skew=0)
    c.drawLine(-370, -196, 370, -196, ink(5)); c.drawLine(-370, -184, 370, -184, ink(2.5))
    label(c, "LA TOUR EIFFEL : TROP CHÈRE ?", -360, -118, 50, INK, skew=-0.08)
    rect(c, -360, -80, -60, 262, '#E3DAC2', LW * .6)
    tower(c, -210, 250, 310, lw=4, glow=False)
    rr = random.Random(2)
    for i in range(16): c.drawCircle(-210 + rr.uniform(-50, 50), 240 - rr.uniform(0, 230), rr.uniform(4, 9), fp('#C2571F', 230))
    textlines(c, -20, -62, 360, 11)
    cu = K(gt, CUE2["n11"] + .3, .45)
    if cu > 0:
        ring = skia.Path(); ring.addArc(skia.Rect(-384, -176, 384, -92), -170, 356 * ease(cu)); c.drawPath(ring, ink(11, RED))
    c.restore()
    sleeve(c, px - 1000, 700, px - 480, 640, 170, '#3B4660')
    t1 = CUE2["n11"] + frac("n11", .3)
    if gt > t1:
        pu = pop(K(gt, t1, .3)); c.save(); c.translate(1420, 330); c.rotate(-5); c.scale(pu * .86, pu * .86)
        label(c, "REPAIRS:", 0, 0, 110, CREAM, align='center', stroke=14); label(c, "A FORTUNE", 0, 122, 128, LIME, align='center', stroke=16); c.restore()
    t2 = CUE2["n11"] + frac("n11", .62)
    if gt > t2:
        pu = pop(K(gt, t2, .3)); c.save(); c.translate(1420, 760); c.rotate(6); c.scale(pu, pu)
        label(c, "KEEP IT ?", 0, 0, 120, RED, font=MARKER, align='center', skew=0); c.restore()


def sh_letter(c, gt, S):
    table_base(c); k = back(K(gt, S["s0"] + .05, .5), 1.3); px = lerp(-700, 700, k)
    c.save(); c.translate(px, 545); c.rotate(-5)
    c.drawRect(skia.Rect(-312, -348, 332, 372), fp((60, 40, 10), 70, blur=12)); rect(c, -320, -360, 320, 360, '#FBFAF2', LW)
    circ(c, 0, -280, 40, '#2A44A8', LW * .6); c.drawCircle(0, -280, 22, fp('#FBFAF2'))
    label(c, "MINISTÈRE DES POSTES", 0, -196, 46, '#2A44A8', align='center', skew=0)
    label(c, "ET TÉLÉGRAPHES", 0, -150, 38, '#2A44A8', align='center', skew=0)
    c.drawLine(-270, -124, 270, -124, ink(3, '#2A44A8')); textlines(c, -260, -80, 270, 9, 38)
    sg = skia.Path(); sg.moveTo(60, 300); sg.cubicTo(100, 240, 130, 330, 170, 280); sg.cubicTo(200, 250, 220, 320, 270, 290); c.drawPath(sg, ink(5, '#1B2A6A'))
    stamp(c, "OFFICIEL", -90, 250, af("n14", gt, .9) / .9, rot=-14, size=84); c.restore()
    sleeve(c, px - 940, 720, px - 400, 660, 170, '#3B4660')
    if af("n14", gt, 1.25) > 0:
        pu = pop(K(gt, CUE2["n14"] + 1.25, .3)); c.save(); c.translate(1500, 300); c.rotate(-6); c.scale(pu, pu)
        label(c, "100% FAKE", 0, 0, 130, LIME, align='center', stroke=16); c.restore()
    tk = CUE2["n14"] + frac("n14", .5)
    if gt > tk:
        pu = pop(K(gt, tk, .3)); c.save(); c.translate(1470, 720); c.rotate(-18); c.scale(pu, pu)
        circ(c, -150, 0, 62, '#D0A548', LW); c.drawCircle(-150, 0, 26, fp('#E6DBB8')); c.drawCircle(-150, 0, 26, ink(LW * .7))
        rect(c, -90, -16, 150, 16, '#D0A548', LW); rect(c, 96, 14, 120, 60, '#D0A548', LW); rect(c, 50, 14, 74, 48, '#D0A548', LW)
        c.rotate(30); poly(c, [(-160, 110), (-110, 70), (120, 70), (120, 190), (-110, 190)], '#C8242C', LW); label(c, "SUITE", 10, 152, 62, CREAM, align='center', skew=0)
        c.restore()


DEAL = [dict(BUYER, suit='#5A6B4A', suit_d='#44523A', hair='slick', hair_col='#6B4A2A', glasses=False, bowtie=False, tie='#B5653A'),
        dict(BUYER, suit='#6A4A6A', suit_d='#503650'), dict(LUSTIG, suit='#7A5A3C', suit_d='#5E432B', hair_col='#8E8E96', tie='#2F6B4E', moustache=False),
        dict(BUYER, suit='#3F5F72', suit_d='#2E4756', glasses=False), dict(LUSTIG, suit='#5B5B66', suit_d='#44444E', hair_col='#7A3A20', tie='#D0A548'), BUYER]


def sh_meeting(c, gt, S):
    c.drawImage(cached("office", lambda cc: office_bg(cc, 0, 5, 0)), -300, -200)
    shock = af("c2", gt, frac("c2", .55)) > 0; hush = af("c2", gt, frac("c2", .8)) > 0
    for i, spec in enumerate(DEAL):
        x = 150 + i * 122; y = 1016 + (i % 2) * 22; ent = back(K(gt, S["s0"] + .1 + i * .07, .3), 1.2)
        c.drawOval(skia.Rect(x - 70, y - 14, x + 70, y + 14), fp((0, 0, 0), 90, blur=6))
        draw_char3(c, x, y + (1 - ent) * 60, .66, spec, face=.7, eyes='wide' if shock else 'dot', mouth='o' if shock else 'flat', brow=.8 if shock else 0,
                   hat=(i in (1, 4)), bob=2 * math.sin(gt * 3 + i), squash=.05 * math.sin(K(gt, CUE2["c2"] + frac("c2", .55) + i * .03, .25) * math.pi), light=1, pupil=1)
    m = sp2("c2", gt); mouth = {'open': 'open', 'mid': 'mid', 'closed': 'smirk', None: 'smirk'}[m]
    c.drawOval(skia.Rect(1010, 1002, 1210, 1044), fp((0, 0, 0), 110, blur=8))
    draw_char3(c, 1110, 1024, 1.05, LUSTIG, face=-.75, eyes='closed' if blink(gt, 2.3, .2) else 'half', mouth=mouth, brow=.8 if hush else .3,
               arms=(('down', 'gesture', K(gt, CUE2["c2"], .3)) if not hush else ('gesture', 'chin', K(gt, CUE2["c2"] + frac("c2", .8), .25)), 'pocket'),
               tilt=-2 + 1.5 * math.sin(gt * 2.2), bob=3 + (4 if m == 'open' else 0), light=1, rim='#FFE6B0')
    win = skia.Path(); win.addRect(skia.Rect(150, 96, 800, 640))
    night(c, [('pool', 1690, 720, 600, .95), ('pool', 1110, 560, 430, .92), ('oval', 500, 900, 520, 330, .78), ('path', win, .82, 10)], '#4C5CA0')
    add_light(c, 1690, 690, 430, '#FFD98A', 70)
    stamp(c, "TOP SECRET", 1420, 330, af("c2", gt, frac("c2", .8)) / .9, rot=-8, size=110)


def close(c, gt, who, s0, **kw):
    dx = -900 if who == 'b' else -1750
    c.drawImage(cached("cu" + who, lambda cc: closeup_bg(cc, 0, 5, dx)), -300, -200)
    sq = 0.07 * math.sin(K(gt, s0, .26) * math.pi) + kw.pop('sq', 0)
    if who == 'b': draw_char3(c, 1080, 1390, 2.15, BUYER, face=-.72, light=1, rim='#FFE6B0', squash=sq, **kw); add_light(c, 1500, 380, 700, '#FFD98A', 36)
    else: draw_char3(c, 840, 1390, 2.15, LUSTIG, face=.72, light=-1, rim='#FFE6B0', squash=sq, **kw); add_light(c, 420, 380, 700, '#FFD98A', 36)


def poplabel(c, s, x, y, t, size=120, v=LIME, rot=-5, font=None, stroke=15):
    if t <= 0: return
    pu = pop(min(t / .3, 1)); c.save(); c.translate(x, y); c.rotate(rot); c.scale(pu, pu)
    label(c, s, 0, 0, size, v, font=font, align='center', stroke=stroke, skew=-0.14 if font is None else 0); c.restore()


def sh_bclose(c, gt, S):
    a = S["arg"]; s0 = S["s0"]
    if a == "why":
        m = sp2("b2", gt); close(c, gt, 'b', s0, eyes='wide', mouth={'open': 'mid', 'mid': 'o', 'closed': 'flat', None: 'flat'}[m], brow=1, brow_tilt=-.6,
                                 arms=('down', ('down', 'chin', K(gt, s0 + .1, .3))), tilt=2 + 2 * math.sin(gt * 8), pupil=-1)
    elif a == "poisson":
        eager = af("n16", gt, frac("n16", .25)) > 0
        close(c, gt, 'b', s0, eyes='wide' if eager else 'dot', mouth='open' if eager else 'smile', brow=.9 if eager else 0, pupil=-1,
              arms=('down', ('down', 'gesture', K(gt, CUE2["n16"] + frac("n16", .25), .3))), tilt=3 * math.sin(gt * 3), bob=3 * abs(math.sin(gt * 5)) if eager else 0)
        if af("n16", gt, frac("n16", .28)) > 0: lower_third(c, "ANDRÉ POISSON", "SCRAP DEALER · NEW IN TOWN", af("n16", gt, frac("n16", .28)), 90, 900)
    elif a == "nervous":
        close(c, gt, 'b', s0, eyes='wide', mouth='flat', brow=1, brow_tilt=-.8, sweat=(gt - s0) * 1.2, pupil=math.sin(gt * 7),
              arms=('down', ('down', 'chin', K(gt, s0 + .1, .3))), tilt=3 * math.sin(gt * 9))
        poplabel(c, "WHY THE SECRECY?", 420, 330, af("n17", gt, frac("n17", .42)), 92, CREAM, -6)
        poplabel(c, "WHY THE RUSH?", 470, 520, af("n17", gt, frac("n17", .72)), 104, LIME, 4)
    elif a == "proof":
        ok = af("n20", gt, frac("n20", .1)) > 0
        close(c, gt, 'b', s0, eyes='wide' if not ok else 'closed', mouth='o' if not ok else 'open', brow=.9, brow_tilt=0 if ok else -.4, pupil=-1,
              arms=('down', 'down') if not ok else ('down', ('down', 'gesture', K(gt, CUE2["n20"], .3))), tilt=2 * math.sin(gt * 3),
              sq=.06 * math.sin(K(gt, CUE2["n20"], .26) * math.pi), bob=4 * abs(math.sin(gt * 6)) if ok else 0)
        poplabel(c, "A BRIBE", 440, 360, af("n19", gt, .1), 130, RED, -6, MARKER, 0)
        stamp(c, "REAL OFFICIAL", 500, 640, af("n20", gt, frac("n20", .45)) / .9, rot=-9, size=96, v='#2F8A4E')
    else:
        close(c, gt, 'b', s0, eyes='half', mouth='flat', brow=0, brow_tilt=-.9, sweat=(gt - s0) * .8, arms=('down', 'down'), tilt=-6 + math.sin(gt * 2), pupil=0)
        c.drawRect(skia.Rect(-400, -300, W + 400, H + 300), fp((6, 8, 30), 90))
        poplabel(c, "TOO EMBARRASSED", 520, 400, af("n23", gt, frac("n23", .4)), 78, CREAM, -5)


def sh_lclose(c, gt, S):
    a = S["arg"]; s0 = S["s0"]; bl = blink(gt, 2.1, 1.0)
    if a == "idea":
        got = af("n13", gt, frac("n13", .5)) > 0
        close(c, gt, 'l', s0, eyes='closed' if bl else ('half' if got else 'dot'), mouth='smirk' if got else 'flat', brow=.95 if got else 0,
              arms=('pocket', ('down', 'chin', K(gt, s0 + .2, .3)) if not got else ('chin', 'gesture', K(gt, CUE2["n13"] + frac("n13", .5), .28))),
              tilt=-3 + 2 * math.sin(gt * 2), sq=.06 * math.sin(K(gt, CUE2["n13"] + frac("n13", .5), .26) * math.pi),
              sparkle=af("n13", gt, frac("n13", .62)) / .3 if af("n13", gt, frac("n13", .62)) > 0 else 0)
        poplabel(c, "A PRODUCT.", 1420, 380, af("n13", gt, frac("n13", .6)), 130, LIME, -5)
    elif a == "secret":
        m = sp2("c3", gt)
        close(c, gt, 'l', s0, eyes='closed' if bl else 'half', mouth={'open': 'open', 'mid': 'mid', 'closed': 'smirk', None: 'smirk'}[m], brow=.7,
              arms=('pocket', ('down', 'gesture', K(gt, s0 + .1, .3))), tilt=-3 + 2 * math.sin(gt * 2.4), bob=3 if m == 'open' else 0)
    else:
        talkn = af("c4", gt) > 0; m = sp2("c4", gt)
        close(c, gt, 'l', s0, eyes='closed' if (bl or (talkn and af("c4", gt, frac("c4", .5)) < 0)) else 'half',
              mouth={'open': 'mid', 'mid': 'o', 'closed': 'flat' if talkn else 'smirk', None: 'smirk'}[m], brow=.2 if talkn else .8, brow_tilt=-.9 if talkn else 0,
              arms=('pocket', ('down', 'gesture', K(gt, CUE2["c4"] + frac("c4", .5), .3)) if talkn else 'down'), tilt=(-8 if talkn else -3) + 2 * math.sin(gt * 2),
              bob=3 if m == 'open' else 0, sq=.06 * math.sin(K(gt, CUE2["c4"], .26) * math.pi),
              sparkle=af("c4", gt, frac("c4", .92)) / .3 if af("c4", gt, frac("c4", .92)) > 0 else 0)
        poplabel(c, "HE CONFESSES", 1400, 360, af("n18", gt, frac("n18", .68)) if not talkn else 0, 110, CREAM, -5)
        poplabel(c, "\"A SMALL GIFT\"", 1420, 380, af("c4", gt, frac("c4", .55)), 104, LIME, -5)


def bills(c, x, y, rot):
    c.save(); c.translate(x, y); c.rotate(rot)
    for a_ in (-16, -4, 9):
        c.save(); c.rotate(a_); rect(c, -130, -70, 130, 70, '#6FA36A', LW); rect(c, -108, -50, 108, 50, '#84B67E', LW * .5); circ(c, 0, 0, 26, '#6FA36A', LW * .5); c.restore()
    c.restore()


def sh_pay(c, gt, S):
    table_base(c); kb = back(K(gt, S["s0"] + .1, .45), 1.4); bx = lerp(2500, 1250, kb)
    take = ease(K(gt, CUE2["n21"] + frac("n21", .35), .5)); cx = lerp(bx - 120, 620, take)
    bills(c, cx, 420, 8); bills(c, cx + 40, 700, -10)
    sleeve(c, bx + 640, 600, bx + 140, 560, 170, '#7A5A3C', skin='#EBC79C')
    lx = lerp(-700, 280, back(K(gt, CUE2["n21"] + frac("n21", .2), .4), 1.3)); sleeve(c, lx - 600, 600, lx, 560, 170, '#3B4660')
    poplabel(c, "THE BRIBE", cx + 20, 250, af("n21", gt, frac("n21", .32)), 84, CREAM, -5)
    poplabel(c, "THE TOWER", cx + 60, 900, af("n21", gt, frac("n21", .62)), 84, LIME, 4)
    stamp(c, "SOLD", 1480, 820, af("n21", gt, frac("n21", .7)) / .9, rot=-12, size=190)


def sh_map(c, gt, S):
    c.drawRect(skia.Rect(-900, -700, W + 900, H + 700), fp('#0E1840'))
    for i in range(-8, 30): c.drawLine(i * 120, -700, i * 120, H + 700, ink(2, '#1A2658')); c.drawLine(-900, i * 120, W + 900, i * 120, ink(2, '#1A2658'))
    land = skia.Path(); land.moveTo(-200, 300); land.cubicTo(200, 120, 500, 260, 760, 180); land.cubicTo(1100, 80, 1500, 200, 2200, 120)
    land.lineTo(2200, 1300); land.lineTo(-200, 1300); land.cubicTo(60, 900, -120, 600, -200, 300); land.close(); shape(c, land, '#22306E', LW)
    isl = skia.Path(); isl.addOval(skia.Rect(260, -40, 620, 130)); shape(c, isl, '#22306E', LW)
    P0, P1 = (520, 640), (1440, 560); u = ease(K(gt, CUE2["n22"] + .5, 2.2))
    for (px, py), nm in ((P0, "PARIS"), (P1, "VIENNA")):
        for k_, a_ in ((46, 30), (28, 60)): c.drawCircle(px, py, k_, fp('#FFD98A', a_))
        circ(c, px, py, 13, '#FFE9A0', LW * .7); label(c, nm, px, py + 90, 62, CREAM, align='center', stroke=10)
    pos = P0
    for i in range(41):
        f = i / 40; x = lerp(P0[0], P1[0], f); y = lerp(P0[1], P1[1], f) - 190 * math.sin(math.pi * f)
        if f <= u:
            if i % 2 == 0: c.drawCircle(x, y, 7, fp(RED))
            pos = (x, y)
    c.save(); c.translate(pos[0], pos[1] - 34)
    rect(c, -60, -34, 40, 20, '#2B2D3C', LW * .8); rect(c, 40, -50, 76, 20, '#C8242C', LW * .8); rect(c, -44, -58, -20, -34, '#2B2D3C', LW * .7)
    for wx in (-36, 6, 54): circ(c, wx, 24, 13, '#D0A548', LW * .6)
    for i in range(3): c.drawCircle(-34 - i * 26 - (gt * 40 % 26), -76 - i * 16, 14 + i * 5, fp('#C9D4FF', 90 - i * 25))
    c.restore()
    if u > .15:
        pu = pop(K(gt, CUE2["n22"] + frac("n22", .6), .3)); c.save(); c.translate(980, 880); c.rotate(-4); c.scale(pu, pu)
        rect(c, -110, -70, 110, 70, '#7A4A2A', LW, r=14); rect(c, -40, -100, 40, -70, '#5A3824', LW, r=8); c.drawLine(-110, -20, 110, -20, ink(LW * .7))
        label(c, "+ CASH", 250, 24, 84, LIME, align='center', stroke=12); c.restore()


def sh_paris2(c, gt, S): shot_paris(c, gt, gt)


def sh_office2(c, gt, S):
    office_bg(c, gt, gt, sign_u=af("n26", gt, .6) / .32 if af("n26", gt, .6) > 0 else 0)
    c.drawOval(skia.Rect(900, 1000, 1110, 1044), fp((0, 0, 0), 110, blur=8))
    draw_char3(c, 1005, 1024, 1.08, LUSTIG, face=-.78, eyes='closed' if blink(gt, 2.3, .2) else 'half', mouth='smirk', brow=.9,
               arms=(('down', 'present', K(gt, CUE2["n26"] + .4, .3)), 'pocket'), tilt=-4 + 1.2 * math.sin(gt * 2.2), bob=3 + 3 * math.sin(gt * 3.1),
               squash=.05 * math.sin(K(gt, CUE2["n26"] + .4, .28) * math.pi), light=1, rim='#FFE6B0')
    office_night(c); stamp(c, "AGAIN", 1400, 360, af("n26", gt, 1.5) / .9, rot=-9, size=170)


def sh_street2(c, gt, S):
    sky(c, '#0A1136', '#26358C', 760); stars(c, gt); moon(c, 1500, 150, 36); cloud(c, 700 + gt * 8, 220, 1.0)
    blur_begin(c, 2.0); far_city(c, 660, 8, '#1E2A68'); tower(c, 985, 716, 450, lw=LW * .7, t=gt); c.restore()
    for (x, w, h, sd) in ((-90, 300, 500, 21), (210, 240, 410, 22), (1150, 260, 430, 23), (1410, 250, 400, 24), (1660, 300, 470, 25)):
        paris_block(c, x, w, h, 760, sd, lit=.3, body='#222E66', dim='#2C3A80')
    c.drawRect(skia.Rect(-900, 760, W + 900, 840), fp('#444B70')); line(c, -900, 760, W + 900, 760, LW); line(c, -900, 840, W + 900, 840, LW)
    c.drawRect(skia.Rect(-900, 840, W + 900, H + 600), fp('#30365A'))
    r = random.Random(4)
    for row in range(7):
        yy = 856 + row * 36 + row * row * 1.5; wd = 84 + row * 8
        for kx in range(-4, 30):
            xx = kx * (wd + 10) + (row % 2) * wd / 2 - 100
            c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(xx, yy, xx + wd, yy + 24 + row * 2), 10, 10), fp('#3C4368' if r.random() < .7 else '#474F78'))
    lx = 560; street_lamp(c, lx, 842, 330)
    u = (gt - S["s0"]) / (S["s1"] - S["s0"]); x = lerp(60, 1560, u); ph = (gt - S["s0"]) * 11
    c.drawOval(skia.Rect(x - 110, 978, x + 110, 1020), fp((0, 0, 0), 120, blur=8))
    c.save(); c.translate(x + 96, 1000 - 150 - 7 * abs(math.sin(ph))); rect(c, -46, 0, 46, 70, '#7A4A2A', LW * .8, r=8); rect(c, -16, -16, 16, 0, '#5A3824', LW * .7, r=5); c.restore()
    draw_char3(c, x, 1000, 1.0, LUSTIG, face=.7, eyes='closed' if blink(gt, 2.6, .4) else 'half', mouth='smirk', brow=.5, arms=('down', 'down'),
               tilt=3 * math.sin(ph), bob=7 * abs(math.sin(ph)), hat=True, light=-1, rim='#FFE6B0', legs=walk_legs(ph))
    cone = cone_path(lx, 300, 80, 760, 780, lean=110)
    night(c, [('path', cone, .92, 24), ('oval', lx + 130, 1000, 520, 120, .85), ('pool', 985, 520, 300, .6), ('pool', x, 600, 340, .62)], '#5A69B6')
    c.drawPath(cone, sp(linear(lx, 300, lx + 110, 1080, [hx('#FFE9A8', 64), hx('#FFE9A8', 12)]), blend=skia.BlendMode.kPlus, blur=20))
    add_light(c, lx, 290, 130, '#FFF0B4', 170)
    stamp(c, "WANTED", 1380, 330, af("n27", gt, frac("n27", .3)) / .9, rot=-8, size=130)
    if af("n28", gt, .5) > 0: lower_third(c, "NEXT MARK: AL CAPONE", "CHICAGO", af("n28", gt, .5), 90, 930)


FN = dict(card=sh_card, news=sh_news, letter=sh_letter, meeting=sh_meeting, bclose=sh_bclose, lclose=sh_lclose, pay=sh_pay, map=sh_map,
          paris2=sh_paris2, office2=sh_office2, street2=sh_street2)
VIG = dict(card=0, news=.46, letter=.46, pay=.46, map=.55)


def render(i, only=None):
    S = SH[i]; kind = S["kind"]; n0, n1 = int(round(S["s0"] * FPS)), int(round(S["s1"] * FPS))
    surf = skia.Surface(W, H); c = surf.getCanvas(); proc = None
    if only is None:
        tmp = f"{OUT}/{i:02d}.tmp.mp4"
        proc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                                 "-c:v", "libx264", "-crf", "17", "-preset", "medium", "-pix_fmt", "yuv420p", tmp], stdin=subprocess.PIPE)
    for f in (range(n0, n1) if only is None else only):
        gt = f / FPS; u = (f - n0) / max(n1 - n0 - 1, 1); e = ease(u)
        z = 1.0 + (0.03 if kind == 'card' else 0.07) * e; rot = (1.6 * (e - .5)) if kind in ('news', 'letter', 'pay') else 0
        c.clear(C((0, 0, 0))); c.save(); c.translate(W / 2, H / 2); c.scale(z, z); c.rotate(rot); c.translate(-960, -545 if kind != 'card' else -540)
        FN[kind](c, gt, S); c.restore()
        if kind != 'card': finish(surf, bloom=0.40); vignette(c, VIG.get(kind, .64))
        if kind == 'paris2': tag(c, "ONE MONTH LATER", (gt - S["s0"] - .2) / 1.0)
        if proc: proc.stdin.write(surf.makeImageSnapshot().toarray(colorType=skia.kBGRA_8888_ColorType).tobytes())
        else: surf.makeImageSnapshot().save(f"/home/claude/vid/frames4/s{i:02d}_{f}.png", skia.kPNG)
    if proc:
        proc.stdin.close()
        if proc.wait() == 0: os.replace(tmp, tmp.replace(".tmp.mp4", ".mp4"))


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True); os.makedirs("/home/claude/vid/frames4", exist_ok=True)
    if sys.argv[1] == "info": print(round(END2, 2), [(i, s["kind"], s["arg"], round(s["s0"], 2), round(s["s1"], 2)) for i, s in enumerate(SH)])
    elif sys.argv[1] == "frames":
        for spec in sys.argv[2:]:
            i, fr = spec.split(":"); i = int(i); S = SH[i]; render(i, [int(round((S["s0"] + (S["s1"] - S["s0"]) * float(fr)) * FPS))])
    else:
        for i in range(len(SH)):
            if i % int(sys.argv[3]) == int(sys.argv[2]): render(i); print("done", i, flush=True)
