"""Scenes s02-s41 of the aivxer tutorial (16:9). Imported by scenes.py."""
from comps import *
import json

WORDS = json.load(open(ROOT + "/vo/words.json"))
LINES = []
import re as _re
for ln in open(ROOT + "/vo/transcript.txt"):
    m = _re.match(r"\s*([\d.]+)-\s*([\d.]+)", ln)
    if m: LINES.append((float(m.group(1)), float(m.group(2))))

def wt(word, after=0.0):
    w = word.lower()
    for s, t in WORDS:
        if t >= after - 1e-3 and s.lower().strip(",.?!'\"").startswith(w): return t
    raise KeyError(f"{word} after {after}")

def cut_before(start):
    """cut time in the silence before the phrase starting at `start`"""
    for i, (s, e) in enumerate(LINES):
        if abs(s - start) < .02: return round((LINES[i - 1][1] + s) / 2, 3) if i else 0.0
    raise KeyError(start)

# ---------------- shared helpers ----------------
GREEN, RED, YEL, BLUE, CORAL, PURP = "#22c55e", "#ef4444", "#ffd23f", "#3b82f6", "#d97757", "#8b5cf6"

def R(T0):
    def r(w, after=None): return wt(w, T0 + (after or 0) if after is not None else T0) - T0
    return r

def wk(t, t0, d=.3): return lin(t, t0, t0 + d)
def wsc(t, t0): return mix(.9, 1, back(lin(t, t0, t0 + .45)))

def P(c, t, t0, x, y, s, size=30, icon=None, icol=GREEN, align="c", bgc="#17171b", t1=None, fg="#ffffff"):
    k = wk(t, t0, .35)
    if t1 is not None: k *= 1 - lin(t, t1, t1 + .25)
    if k > 0: pill(c, x, y, s, size, k=min(1, k * 1.2), a=min(1, k * 1.5), icon=icon, icol=icol, align=align, bgc=bgc, fg=fg)

def vwin(c, x, y, h, v, fi, title, a=1.0, sc=1.0, img=None):
    """vertical (9:16) player window; h = picture height"""
    w = h * 9 / 16; im = img if img is not None else (v.frame(fi) if v else None)
    def f(c2, cx, cy, cw, ch):
        rrect(c2, cx, cy, cw, ch, 0, "#000000")
        if im is not None: draw_img(c2, im, cx, cy, cw, ch)
    window(c, x, y, w, h + 38, title, a=a, sc=sc, content=f, bg="#000000")
    return w

def iwin(c, x, y, w, h, img, title, a=1.0, sc=1.0, fx=.5, fy=.5):
    def f(c2, cx, cy, cw, ch): draw_img_cover(c2, img, cx, cy, cw, ch, fx=fx, fy=fy)
    window(c, x, y, w, h + 38, title, a=a, sc=sc, content=f, bg="#000000")

def label(c, s, x, y, k, color=YEL, size=26):
    if k > 0: pill(c, x, y, s, size, k=k, a=min(1, k * 2), icon="dot", icol=color, align="c", bgc="#111114")

def tag(c, s, x, y, k, color=YEL, size=26): ann_label(c, s, x, y, k, color, size)

def wave(c, x, y, w, h, t_abs, color="#ffffff", n=64, a=1.0, scale=1.0, src=None):
    """waveform bars driven by the voice loudness around t_abs"""
    bw = w / n
    for i in range(n):
        v = src(i) if src else env_at(t_abs - (n - i) / 30.0)
        hh = max(4, h * clamp(v * scale, 0, 1))
        rrect(c, x + i * bw + 1, y + h / 2 - hh / 2, bw - 3, hh, (bw - 3) / 2, color, a)

def card(c, x, y, w, h, title=None, k=1.0, accent=None):
    with Pop(c, x, y, w, h, k):
        panel(c, x, y, w, h, 22)
        if accent: rrect(c, x, y, 8, h, 4, accent)
        if title: text(c, title, x + 30, y + 46, 26, "b", "#ffffff")

def checklist(c, t, x, y, items, size=30, gap=74, w=820):
    """items: (t0, text, ok)"""
    for i, (t0, s, ok) in enumerate(items):
        k = wk(t, t0, .3)
        if k <= 0: continue
        yy = y + i * gap + 16 * (1 - eout(k))
        c.saveLayerAlpha(None, int(255 * k))
        rrect(c, x, yy, w, gap - 14, 16, "#17171b", .92); rrect_stroke(c, x, yy, w, gap - 14, 16, "#ffffff", .1, 1.2)
        (check if ok else cross)(c, x + 40, yy + (gap - 14) / 2, 17, GREEN if ok else RED)
        text(c, s, x + 76, yy + (gap - 14) / 2 + size * .36, size, "s", "#ffffff")
        c.restore()

def cues(times, kind="pop", g=.5):
    for t in times: sfx(t, kind, g)

def ttl(c, t, t0, s, y=300, size=110, color="#ffffff", t1=None, sub=None, subt=None):
    k = wk(t, t0, .4)
    if t1 is not None: k *= 1 - lin(t, t1, t1 + .3)
    big_title(c, s, y, size, k, color, sub=sub, subk=(wk(t, subt, .3) * (1 - (lin(t, t1, t1 + .3) if t1 else 0))) if subt is not None else 0)

def V(name, start, w=405, h=720): return Vid(A + "/" + name, start, w, h)

# ---------------- scenes ----------------
def s02(T0, D):
    r = R(T0); v = V("ref.mp4", 0.2); v2 = V("ref.mp4", 118.6)
    t3d, teyes, tmain, tch = r("3D"), r("eyes"), r("main"), r("choose")
    cam = drift(D, 1.0, 1.06, 900, 520)
    sfx(0, "whoosh", .7); cues([.2, t3d, teyes, tmain, tch])
    def draw(c, t):
        bg(c, "Instagram")
        a, sc = wk(t, .1), wsc(t, .1)
        vid = v2 if t >= tch - .1 else v
        fi = int((t - (tch - .1 if t >= tch - .1 else 0)) * FPS)
        vwin(c, 420, 70, 800, vid, fi, "Their video", a=a, sc=sc)
        tag(c, "REFERENCE", 140, 150, wk(t, .5))
        P(c, t, t3d, 1360, 260, "Simple 3D cartoons", 34, "check")
        P(c, t, teyes, 1360, 370, "Filmed through YOUR eyes", 34, "check")
        P(c, t, tmain, 1360, 480, "You are the main character", 34, "check")
        P(c, t, tch, 1360, 620, "You choose what happens", 38, "dot", YEL, bgc="#2a2410")
        bgdock(c, 2)
    return cam, draw, [v, v2]

def s03(T0, D):
    r = R(T0); tq = r("claude"); tsl = r("slideshow"); tav = r("avatar")
    tc, tcam, tvo, tso = r("characters"), r("camera"), r("voices"), r("sound")
    cam = drift(D, 1.0, 1.05)
    sfx(0, "whoosh", .7); cues([tq, tsl, tav, tc, tcam, tvo, tso]); sfx(tq, "rise", .4)
    def draw(c, t):
        bg(c, "Claude")
        ttl(c, t, tq - .15, "Can Claude make this?", 300, 120, "#ffffff")
        P(c, t, tsl, 700, 470, "A slideshow", 34, "cross", RED)
        P(c, t, tav, 1220, 470, "A talking avatar", 34, "cross", RED)
        for i, (s, t0) in enumerate([("Characters", tc), ("Camera moves", tcam), ("Voices", tvo), ("Sound", tso)]):
            P(c, t, t0, 420 + i * 360, 640, s, 34, "check", GREEN)
        k = wk(t, tc - .2, .4)
        if k > 0: text(c, "A REAL ANIMATED SHORT", W / 2, 590, 30, "x", YEL, k, "c")
        bgdock(c, 1)
    return cam, draw

def s04(T0, D):
    r = R(T0); tg = r("gave"); tb = r("built")
    att = IMG("ref_0.2.png")
    msgs = [dict(role="user", text="Recreate this style.", t0=tg + .3, attach=att, attach_name="their_video.mp4"),
            dict(role="ai", text="Got it. Before I build anything, I'm going to study this video properly.", t0=tb, busy=True)]
    cam = Cam([(0, 960, 540, 1.0), (tg, 960, 540, 1.0), (tg + .8, 1000, 330, 1.4), (D, 1000, 350, 1.44)])
    sfx(0, "whoosh", .7); sfx(.2, "pop", .5); sfx(tg + .3, "pop", .6); sfx(tg + .3, "click", .5); sfx(tb, "pop", .4)
    def draw(c, t):
        bg(c, "Claude")
        chat_window(c, 230, 60, 1460, 880, t, msgs, a=wk(t, .1), sc=wsc(t, .1))
        bgdock(c, 1)
    return cam, draw

def s05(T0, D):
    r = R(T0); te = r("everything")
    items = [(r("studied"), "How Claude studied the original", True), (r("rebuilt"), "How it rebuilt the style", True),
             (r("own"), "My own original series", True), (r("results"), "The results on my page", True),
             (r("step"), "How YOU can do it, step by step", True)]
    tg = r("let's", 13)
    cam = Cam([(0, 960, 540, 1.0), (tg - .1, 960, 520, 1.06), (D, 960, 520, 1.3)])
    sfx(0, "whoosh", .7); sfx(te, "pop", .6); cues([i[0] for i in items], "ding", .45); sfx(tg, "whoosh", .6)
    def draw(c, t):
        bg(c, "Notes")
        ttl(c, t, te - .1, "IN THIS VIDEO", 200, 90, YEL)
        checklist(c, t, 550, 280, items, 32, 104, 820)
        bgdock(c, 0)
    return cam, draw

def s06(T0, D):
    r = R(T0); tw_ = r("why"); tf = r("first"); th = r("hands"); tb = r("brain")
    v = V("ref.mp4", 0.2)
    cam = Cam([(0, 960, 540, 1.0), (tf - .1, 960, 540, 1.0), (tf + .6, 960, 540, 1.0), (th - .1, 900, 620, 1.28), (D, 900, 620, 1.32)])
    sfx(0, "whoosh", .7); sfx(tw_, "pop", .5); sfx(tf, "whoosh_s", .5); sfx(tf + .2, "pop", .5); sfx(th + .1, "ding", .5); sfx(tb, "pop", .5)
    def draw(c, t):
        bg(c, "Instagram")
        ttl(c, t, tw_ - .3, "WHY THIS FORMAT WORKS", 470, 96, "#ffffff", t1=tf - .2)
        if t > tf:
            vwin(c, 600, 60, 830, v, int((t - tf) * FPS), "Their video", a=wk(t, tf), sc=wsc(t, tf))
            P(c, t, tf + .2, 1380, 230, "1   The camera is YOUR eyes", 34, "dot", YEL)
            ann_circle(c, 830, 760, 170, wk(t, th + .1, .5))
            P(c, t, th + .3, 830, 960 - 60, "Your own hands", 26, "dot", YEL)
            P(c, t, tb, 1380, 340, "Your brain puts you inside", 30, "check")
        bgdock(c, 2)
    return cam, draw

def s07(T0, D):
    r = R(T0); ts = r("second"); tc = r("cartoon"); to = r("outlines"); thd = r("heads"); tsh = r("shoulders")
    tfr = r("friendly"); thr = r("horror")
    img = IMG("ref_18.png"); pal = ['#bfb9ae', '#8794ac', '#ede6d8', '#5a6a87', '#395a59', '#271d20', '#cf5a5b', '#e5aa52']
    cam = drift(D, 1.0, 1.05, 940, 520)
    sfx(0, "whoosh", .7); cues([ts, to, thd, tsh, tfr]); sfx(tc, "ding", .4)
    def draw(c, t):
        bg(c, "Instagram")
        iwin(c, 330, 60, 470, 836, img, "Their video", a=wk(t, .1), sc=wsc(t, .1))
        P(c, t, ts, 1250, 150, "2   Simple on purpose", 36, "dot", YEL)
        # palette
        k = wk(t, tc, .4)
        if k > 0:
            for i, h in enumerate(pal):
                kk = wk(t, tc + i * .05, .3)
                with Pop(c, 960 + i * 72, 250, 60, 60, kk): rrect(c, 960 + i * 72, 250, 60, 60, 14, h); rrect_stroke(c, 960 + i * 72, 250, 60, 60, 14, "#ffffff", .3, 1.5)
            text(c, "Flat cartoon colours", 960, 350, 26, "s", "#ffffff", k)
        P(c, t, to, 1150, 430, "Thick black outlines", 32, "check")
        P(c, t, thd, 1150, 530, "Small heads", 32, "check")
        P(c, t, tsh, 1450, 530, "Big puffy shoulders", 32, "check")
        tag(c, "small head", 610, 360, wk(t, thd, .3)); tag(c, "puffy shoulders", 500, 520, wk(t, tsh, .3))
        P(c, t, tfr, 1250, 680, "Friendly look  =  scarier horror", 34, "dot", RED, bgc="#2a1212")
        bgdock(c, 2)
    return cam, draw

def s08(T0, D):
    r = R(T0); t3 = r("third"); tcalm = r("calm"); tstr = r("strange"); ttw = r("twist"); tan = r("another")
    tfz = r("freezes"); twd = r("what"); tbt = r("buttons"); tgr = r("green"); trd = r("red"); tcm = r("comment"); tmil = r("millions")
    cam = Cam([(0, 960, 540, 1.0), (twd - .3, 960, 470, 1.04), (twd + .2, 960, 600, 1.12), (tcm - .2, 960, 600, 1.12), (tcm + .3, 960, 540, 1.0), (D, 960, 540, 1.04)])
    sfx(0, "whoosh", .7); cues([t3, tcalm, tstr, ttw, tan, tbt, tgr, trd, tcm]); sfx(tfz, "whoosh_s", .6); sfx(tmil, "ding", .6)
    steps = [("CALM", tcalm, "#3b82f6"), ("STRANGE", tstr, PURP), ("TWIST", ttw, "#f97316"), ("TWIST #2", tan, RED), ("FREEZE", tfz, "#ffffff")]
    def draw(c, t):
        bg(c, "Notes")
        P(c, t, t3, W / 2, 110, "3   The pacing never stops", 38, "dot", YEL)
        for i, (s, t0, cc) in enumerate(steps):
            x = 200 + i * 310; k = wk(t, t0, .3)
            if k <= 0: continue
            with Pop(c, x, 230, 270, 120, k):
                fz = s == "FREEZE"
                rrect(c, x, 230, 270, 120, 22, "#17171b" if not fz else "#ffffff"); rrect(c, x, 230, 270, 10, 5, cc)
                text(c, s, x + 135, 305, 34, "x", "#ffffff" if not fz else "#111111", 1, "c")
            if i:
                aa = wk(t, t0 - .1, .3); c.drawLine(x - 36, 290, x - 8, 290, paint(col("#ffffff", .7 * aa), style="stroke", sw=5))
        k = wk(t, twd, .3)
        if k > 0: big_title(c, "WHAT DO YOU DO?", 470, 76, k, "#ffffff")
        for i, (s, t0, cc) in enumerate([("OPEN THE DOOR", tgr, "#1f9d4c"), ("KEEP IT LOCKED", trd, "#d63a3a")]):
            k = wk(t, max(t0, tbt), .35)
            if k > 0:
                with Pop(c, 560, 540 + i * 140, 800, 110, k):
                    rrect(c, 560, 540 + i * 140, 800, 110, 26, cc); rrect(c, 560, 540 + i * 140, 800, 50, 26, "#ffffff", .12)
                    text(c, s, 960, 612 + i * 140, 44, "x", "#ffffff", 1, "c")
        P(c, t, tcm, 960, 850, "Everyone comments their answer  ->  millions of views", 30, "dot", YEL)
        bgdock(c, 0)
    return cam, draw

def s09(T0, D):
    r = R(T0); tg = r("goal"); tch = r("characters"); tst = r("stories"); tok = r("okay")
    tre = r("recreate"); tl, tle, tc, trh = r("look"), r("lens"), r("camera"), r("rhythm"); tor = r("original")
    cam = drift(D, 1.0, 1.04)
    sfx(0, "whoosh", .7); cues([tch, tst, tl, tle, tc, trh]); sfx(tok, "click", .4); sfx(tor, "ding", .6)
    def draw(c, t):
        bg(c, "Notes")
        k1, k2 = wk(t, tg, .35), wk(t, tre - .2, .35)
        if k1 > 0:
            card(c, 250, 140, 640, 560, None, k1, RED); text(c, "NOT COPIED", 290, 205, 40, "x", RED, k1)
        if k2 > 0:
            card(c, 1030, 140, 640, 560, None, k2, GREEN); text(c, "RECREATED", 1070, 205, 40, "x", GREEN, k2)
        checklist(c, t, 290, 250, [(tch, "Their characters", False), (tst, "Their stories", False)], 32, 96, 560)
        checklist(c, t, 1070, 250, [(tl, "The look", True), (tle, "The lens", True), (tc, "The camera", True), (trh, "The rhythm", True)], 32, 96, 560)
        P(c, t, tok, 570, 520, "That's not okay", 28, "dot", RED)
        P(c, t, tor, W / 2, 790, "Then: MY OWN original stories", 40, "check", GREEN)
        bgdock(c, 0)
    return cam, draw

def s10(T0, D):
    r = R(T0); tu = r("uploaded"); trs = r("recreate"); tey = r("eyeball"); tsm = r("small"); tms = r("measured")
    att = IMG("ref_0.2.png")
    msgs = [dict(role="user", text="Recreate this style.", t0=trs - .2, attach=att, attach_name="their_video.mp4"),
            dict(role="ai", text="I won't eyeball it. I'll measure the video first.", t0=tey, busy=True,
                 items=[("Writing an analysis script", tms - .2, tsm), ("Measuring the video", tms + 1.0, tms)])]
    cam = Cam([(0, 960, 540, 1.0), (tu, 960, 540, 1.0), (tey, 1150, 360, 1.5), (D, 1150, 380, 1.55)])
    sfx(0, "whoosh", .7); sfx(trs - .2, "pop", .6); sfx(tey, "pop", .5); sfx(tsm, "pop", .4); sfx(tms - .2, "ding", .5)
    def draw(c, t):
        bg(c, "Claude")
        ttl(c, t, 0, "MOST PEOPLE DON'T EXPECT THIS", 520, 80, YEL, t1=tu - .2)
        if t > tu - .2: chat_window(c, 230, 60, 1460, 880, t, msgs, a=wk(t, tu - .2), sc=wsc(t, tu - .2))
        bgdock(c, 1)
    return cam, draw

def s11(T0, D):
    r = R(T0); tf = r("frames"); tcs = r("contact"); tev = r("every")
    img = IMG("sheet.jpg")
    cam = Cam([(0, 960, 540, 1.0), (tcs, 960, 520, 1.0), (D, 900, 480, 1.35)])
    sfx(0, "whoosh", .7); sfx(tf, "pop", .5); sfx(tcs, "pop", .6); sfx(tev, "ding", .4)
    tl = [(0, "$ python3 analyze_reference.py their_video.mp4", "#e5e5e5"), (tf, "splitting into frames...  3,672 frames", "#9cdcfe"),
          (tcs, "contact sheets -> sheet_01.jpg ... sheet_04.jpg", "#9cdcfe")]
    def draw(c, t):
        bg(c, "Terminal")
        term_window(c, 120, 90, 760, 300, tl, t, a=wk(t, .1), sc=wsc(t, .1))
        if t > tcs - .2:
            iwin(c, 700, 260, 1100, 1100 * img.height() / img.width(), img, "sheet_01.jpg", a=wk(t, tcs - .2), sc=wsc(t, tcs - .2))
        P(c, t, tev, 1250, 200, "Every scene at once", 32, "check")
        bgdock(c, 4)
    return cam, draw

MOT = [tuple(map(float, l.split()[:2])) for l in open("/tmp/claude-0/ra/motion.txt").read().splitlines()[1:] if l.strip()] \
    if os.path.exists("/tmp/claude-0/ra/motion.txt") else []
def motion_plot(c, x, y, w, h, t, t0, dur=1.8, tmax=4.0, labels=(), fit=0.0):
    panel(c, x, y, w, h, 20)
    text(c, "camera speed (px / frame)", x + 30, y + 44, 22, "s", "#d4d4d8")
    px0, py0, pw, ph = x + 50, y + 80, w - 90, h - 140
    c.drawLine(px0, py0 + ph, px0 + pw, py0 + ph, paint(col("#ffffff", .3), style="stroke", sw=2))
    pts = [(tt, abs(v)) for tt, v in MOT if tt <= tmax]
    if not pts: return
    vmax = max(v for _, v in pts) * 1.1; n = int(len(pts) * clamp((t - t0) / dur))
    p = skia.Path()
    for i, (tt, v) in enumerate(pts[:max(2, n)]):
        X = px0 + pw * tt / tmax; Y = py0 + ph - ph * v / vmax
        (p.moveTo if i == 0 else p.lineTo)(X, Y)
    pp = paint(col(CORAL), style="stroke", sw=5); pp.setStrokeJoin(skia.Paint.kRound_Join); c.drawPath(p, pp)
    if fit > 0:  # sine ease fit over the first move (0.3-1.0 s)
        q = skia.Path(); a0, a1 = .3, 1.0; pk = max(v for tt, v in pts if a0 <= tt <= a1)
        for i in range(41):
            tt = a0 + (a1 - a0) * i / 40; v = pk * math.sin(math.pi * i / 40)
            X = px0 + pw * tt / tmax; Y = py0 + ph - ph * v / vmax; (q.moveTo if i == 0 else q.lineTo)(X, Y)
        m = skia.PathMeasure(q, False); d = skia.Path(); m.getSegment(0, m.getLength() * fit, d, True)
        pq = paint(col(YEL), style="stroke", sw=4); pq.setPathEffect(skia.DashPathEffect.Make([14, 10], 0)); c.drawPath(d, pq)
    for (s, tt0, tx, cc, kk) in labels:
        if kk > 0: label(c, s, px0 + pw * tx / tmax, py0 + 40 if s != "HOLD" else py0 + ph - 60, kk, cc, 22)

def s12(T0, D):
    r = R(T0); to = r("optical"); tpx = r("pixels"); ttl_ = r("timeline"); ths = r("holds"); tsm = r("smooth"); tsn = r("snap")
    lines = [(0, "$ python3 analyze_reference.py --flow", "#e5e5e5")] + \
            [(to + .4 + i * .12, f"t={tt:4.2f}   dx={v:6.2f}", "#9cdcfe") for i, (tt, v) in enumerate(MOT[8:40:2])]
    cam = drift(D, 1.0, 1.04)
    sfx(0, "whoosh", .7); sfx(to, "pop", .5); sfx(ttl_, "pop", .5); cues([ths, tsm, tsn], "ding", .45)
    def draw(c, t):
        bg(c, "Terminal")
        term_window(c, 110, 80, 640, 820, lines, t, a=wk(t, .1), sc=wsc(t, .1), size=18)
        P(c, t, to, 430, 940 - 50, "Optical flow: how pixels move", 28, "dot", YEL)
        if t > ttl_ - .2:
            with Pop(c, 820, 150, 990, 600, wk(t, ttl_ - .2, .35)):
                motion_plot(c, 820, 150, 990, 600, t, ttl_, 2.5, 4.0,
                            [("HOLD", 0, .15, "#9cdcfe", wk(t, ths, .3)), ("EASED MOVE", 0, .62, YEL, wk(t, tsm, .3)), ("FAST SNAP", 0, 2.75, RED, wk(t, tsn, .3))])
        bgdock(c, 4)
    return cam, draw

def s13(T0, D):
    r = R(T0); tsine = r("sign"); tcur = r("curve"); tcol = r("colors"); twall = r("wall"); tdesk = r("desk"); tskin = r("skin"); tmem = r("memory")
    pal = [('#bfb9ae', "wall"), ('#ede6d8', "ceiling"), ('#8794ac', "lockers"), ('#5a6a87', "shadow"), ('#cf5a5b', "shirt"), ('#e5aa52', "desk"), ('#d9a07a', "skin"), ('#271d20', "outline")]
    cam = Cam([(0, 960, 540, 1.0), (tcol - .3, 960, 540, 1.0), (tcol + .4, 960, 540, 1.0), (D, 960, 560, 1.05)])
    sfx(0, "whoosh", .7); sfx(tsine, "pop", .5); sfx(tcur, "ding", .5); sfx(tcol, "whoosh_s", .5); cues([twall, tdesk, tskin]); sfx(tmem, "ding", .5)
    def draw(c, t):
        bg(c, "Notes")
        ka = 1 - lin(t, tcol - .3, tcol)
        if ka > 0:
            c.saveLayerAlpha(None, int(255 * ka))
            motion_plot(c, 360, 120, 1200, 640, 10, 0, 1, 1.6, [("EASED MOVE", 0, .62, YEL, 1)], fit=wk(t, tsine, 1.2))
            P(c, t, tsine, 960, 830, "Matches a sine ease-in / ease-out", 32, "check")
            c.restore()
        if t > tcol - .1:
            ttl(c, t, tcol - .1, "PALETTE FROM THE VIDEO", 200, 72, "#ffffff")
            iwin(c, 160, 270, 330, 587, IMG("ref_18.png"), "frame", a=wk(t, tcol), sc=wsc(t, tcol))
            for i, (h, n) in enumerate(pal):
                t0 = [twall, twall, twall, tdesk, tdesk, tdesk, tskin, tskin][i] + (i % 3) * .08
                k = wk(t, t0, .3)
                if k <= 0: continue
                x = 620 + (i % 4) * 300; y = 300 + (i // 4) * 280
                with Pop(c, x, y, 250, 230, k):
                    rrect(c, x, y, 250, 170, 22, h); rrect_stroke(c, x, y, 250, 170, 22, "#ffffff", .25, 1.5)
                    text(c, n, x + 10, y + 210, 26, "s", "#ffffff"); text(c, h, x + 240, y + 210, 20, "mono", "#a1a1aa", 1, "r")
            P(c, t, tmem, 1100, 900, "Not from memory", 30, "check")
        bgdock(c, 0)
    return cam, draw

def s14(T0, D):
    r = R(T0); tsu = r("subtitles"); tpo = r("pops"); tbg = r("big"); tlo = r("long")
    v = V("ref.mp4", 4.6)
    cam = Cam([(0, 960, 540, 1.0), (tpo - .2, 960, 540, 1.0), (tpo + .3, 760, 700, 1.4), (tlo, 760, 700, 1.4), (D, 900, 560, 1.1)])
    sfx(0, "whoosh", .7); cues([tsu, tpo, tbg, tlo])
    def draw(c, t):
        bg(c, "Instagram")
        vwin(c, 540, 60, 830, v, int(t * FPS), "Their video", a=wk(t, .1), sc=wsc(t, .1))
        P(c, t, tsu, 1350, 200, "Subtitles, measured", 34, "dot", YEL)
        P(c, t, tpo, 1350, 330, "WHEN each word pops", 30, "check")
        P(c, t, tbg, 1350, 430, "HOW BIG the text is", 30, "check")
        P(c, t, tlo, 1350, 530, "HOW LONG it stays", 30, "check")
        ann_circle(c, 773, 750, 120, wk(t, tpo, .5))
        bgdock(c, 2)
    return cam, draw

def grid_warp(c, x, y, w, h, kind, a=1.0, n=10):
    """draw a square grid through a lens: 'barrel' (cheap fisheye) or 'stereo'"""
    cx, cy, R_ = x + w / 2, y + h / 2, w / 2
    def mp(u, v):  # u,v in -1..1
        rr = math.hypot(u, v)
        if rr < 1e-6: return cx, cy
        if kind == "barrel": s = (1 - .32 * rr * rr) * 1.05
        elif kind == "stereo": th = math.atan(rr * 1.6); s = (2 * math.tan(th / 2)) / (rr * 1.6) * 1.18
        else: s = 1
        return cx + u * s * R_ * .95, cy + v * s * R_ * .95
    pp = paint(col("#ffffff", .85 * a), style="stroke", sw=2.5)
    for i in range(n + 1):
        f = -1 + 2 * i / n; p1 = skia.Path(); p2 = skia.Path()
        for j in range(41):
            g = -1 + 2 * j / 40
            (p1.moveTo if j == 0 else p1.lineTo)(*mp(f, g)); (p2.moveTo if j == 0 else p2.lineTo)(*mp(g, f))
        c.drawPath(p1, pp); c.drawPath(p2, pp)

def s15(T0, D):
    r = R(T0); tl = r("lens"); tfe = r("fisheye"); tbu = r("bulging"); tstr = r("straight"); tst = r("stereographic"); tfa = r("faces"); tnum = r("number")
    cam = Cam([(0, 960, 540, 1.0), (tnum - .3, 960, 520, 1.03), (tnum + .3, 960, 420, 1.25), (D, 960, 420, 1.3)])
    sfx(0, "whoosh", .7); sfx(tl, "rise", .5); cues([tfe, tbu, tstr]); sfx(tst, "ding", .6); sfx(tfa, "pop", .5); sfx(tnum, "ding", .6)
    def draw(c, t):
        bg(c, "Notes")
        ttl(c, t, tl - .1, "THE LENS", 150, 90, YEL)
        k1 = wk(t, tfe, .35); k2 = wk(t, tst - .2, .35)
        if k1 > 0:
            with Pop(c, 250, 230, 620, 560, k1):
                panel(c, 250, 230, 620, 560); grid_warp(c, 330, 280, 460, 420, "barrel")
                text(c, "Cheap bulging fisheye", 560, 760, 28, "b", "#ffffff", 1, "c")
            if t > tbu: cross(c, 830, 270, 26, RED)
        if k2 > 0:
            with Pop(c, 1050, 230, 620, 560, k2):
                panel(c, 1050, 230, 620, 560); grid_warp(c, 1130, 280, 460, 420, "stereo")
                text(c, "Stereographic lens", 1360, 760, 28, "b", "#ffffff", 1, "c")
            check(c, 1630, 270, 26, GREEN, clamp((t - tst) / .3))
        P(c, t, tstr, 560, 850, "Measured how straight lines bend", 26, "dot", YEL)
        P(c, t, tfa, 1360, 850, "Natural faces + very wide view", 26, "check")
        k = wk(t, tnum - .2, .4)
        if k > 0:
            with Pop(c, 610, 280, 700, 230, k):
                rrect(c, 610, 280, 700, 230, 30, "#111114", .96); rrect_stroke(c, 610, 280, 700, 230, 30, YEL, .9, 3)
                text(c, "r = 2f · tan(θ/2)", 960, 370, 54, "mono", "#ffffff", 1, "c")
                text(c, "f ≈ 540 px", 960, 460, 64, "x", YEL, 1, "c")
        bgdock(c, 0)
    return cam, draw

def s16(T0, D):
    r = R(T0); tb = r("build"); tco = r("code"); tst = r("stock"); tim = r("image"); tvi = r("video")
    cam = drift(D, 1.0, 1.06)
    sfx(0, "whoosh", .8); sfx(tb, "rise", .5); sfx(tco, "ding", .5); cues([tst, tim, tvi])
    def draw(c, t):
        bg(c, "Code")
        ttl(c, t, tb - .1, "NOW THE BUILD", 330, 130, "#ffffff")
        P(c, t, tco, W / 2, 440, "Everything is drawn in code", 40, "check", GREEN)
        for i, (s, t0) in enumerate([("No stock footage", tst), ("No image generator", tim), ("No video AI", tvi)]):
            P(c, t, t0, 480 + i * 480, 620, s, 34, "cross", RED)
        bgdock(c, 3)
    return cam, draw

CODE_SHAPES = [
    "import * as THREE from 'three';",
    "import { OutlineEffect } from 'three/addons/effects/OutlineEffect.js';",
    "",
    "// every prop is a simple shape with a flat toon material",
    "function box(w, h, d, color) {",
    "  return add(new THREE.Mesh(new THREE.BoxGeometry(w, h, d), M(color)));",
    "}",
    "function cyl(rt, rb, h, color) {",
    "  return add(new THREE.Mesh(new THREE.CylinderGeometry(rt, rb, h, 24), M(color)));",
    "}",
    "function ball(r, color) {",
    "  return add(new THREE.Mesh(new THREE.SphereGeometry(r, 32, 20), M(color)));",
    "}",
    "",
    "desk   = box(1.2, 0.05, 0.6, '#e5aa52');",
    "locker = box(0.5, 1.9, 0.5, '#8794ac');",
    "door   = box(0.9, 2.1, 0.06, '#5a6a87');",
    "",
    "// thick black ink around every object",
    "const effect = new OutlineEffect(renderer, { defaultThickness: 0.006 });",
]
def s17(T0, D):
    r = R(T0); tth = r("3.js"); tcl = r("classroom"); tbx = r("boxes"); tcy = r("cylinders"); tsp = r("spheres"); tol = r("outlines")
    v = V("ours4.mp4", 0)
    def hl(t):
        if t > tol: return (18, 20)
        if t > tsp: return (10, 13)
        if t > tcy: return (7, 10)
        if t > tbx: return (4, 7)
        if t > tcl: return (14, 17)
        return None
    cam = drift(D, 1.0, 1.04, 940, 520)
    sfx(0, "whoosh", .7); sfx(tth, "pop", .5); cues([tbx, tcy, tsp]); sfx(tol, "ding", .5)
    def draw(c, t):
        bg(c, "Code")
        code_window(c, 90, 70, 1080, 830, CODE_SHAPES, hl=hl(t), title="scene.js", reveal=int(t * 160), a=wk(t, .1), sc=wsc(t, .1), size=18)
        vwin(c, 1300, 90, 760, v, int(t * FPS) % 119, "Claude's version", a=wk(t, tth), sc=wsc(t, tth))
        P(c, t, tth, 1515, 940 - 40, "three.js  ·  3D in a web browser", 24, "dot", CORAL)
        bgdock(c, 3)
    return cam, draw

CODE_LENS = [
    "// final pass: the stereographic wide lens",
    "uniform sampler2D tSrc; uniform float focal;",
    "void main() {",
    "  vec2 p = (vUv - 0.5) * res;",
    "  float r = length(p);",
    "  float th = 2.0 * atan(r / (2.0 * focal));   // stereographic",
    "  vec2 dir = p / max(r, 1e-5);",
    "  vec2 ndc = dir * tan(th) / tanXY;",
    "  gl_FragColor = texture2D(tSrc, ndc * 0.5 + 0.5);",
    "}",
]
def s18(T0, D):
    r = R(T0); tl = r("lens"); tre = r("real")
    cam = Cam([(0, 960, 540, 1.0), (tl, 960, 540, 1.0), (tl + .6, 900, 430, 1.3), (D, 900, 430, 1.33)])
    sfx(0, "whoosh", .7); sfx(tl, "pop", .5); sfx(tre, "ding", .5)
    def draw(c, t):
        bg(c, "Code")
        code_window(c, 300, 120, 1320, 560, CODE_LENS, hl=(5, 6) if t > tl else None, title="lens.glsl", reveal=int(t * 120), a=wk(t, .1), sc=wsc(t, .1), size=22)
        P(c, t, tl, 960, 760, "Applied on top as a final pass", 32, "check")
        P(c, t, tre, 960, 860, "Like a real lens on a camera", 32, "dot", YEL)
        bgdock(c, 3)
    return cam, draw

CODE_CAM = [
    "// the camera, written like a director's shot list",
    "K(0.0, 0.3,  { yaw: 0,   pitch: -10 });          // still",
    "K(0.3, 0.9,  { yaw: 14,  pitch: -8 }, 'ease');   // look left",
    "K(2.1, 2.6,  { yaw: 44 },  'ease');              // ease to the door",
    "K(2.6, 4.0,  {});                                // hold",
    "K(4.0, 4.35, { yaw: -30, pitch: 2 }, 'snap');    // snap to the window",
    "K(4.4, 8.0,  { yaw: -33 }, 'drift');             // slow drift",
]
def s19(T0, D):
    r = R(T0); tsl = r("shot"); tlf = r("left"); tdo = r("door"); tho = r("hold"); tsn = r("snap"); tpr = r("premium"); two = r("wobble")
    tst = r("still"); tsm = r("smooth"); tde = r("dead"); tdr = r("drift"); tfs = r("fast")
    def hl(t):
        for a, s in ((tsn, 5), (tho, 4), (tdo, 3), (tlf, 2)):
            if t > a: return (s, s + 1)
        return None
    cam = Cam([(0, 960, 540, 1.0), (tpr - .2, 960, 400, 1.08), (tpr + .4, 960, 560, 1.0), (D, 960, 600, 1.05)])
    sfx(0, "whoosh", .7); cues([tlf, tdo, tho]); sfx(tsn, "whoosh_s", .5); sfx(two, "pop", .5); cues([tst, tsm, tde, tdr, tfs], "click", .5)
    def draw(c, t):
        bg(c, "Code")
        code_window(c, 230, 60, 1460, 470, CODE_CAM, hl=hl(t), title="camera.js", reveal=int(t * 140), a=wk(t, .1), sc=wsc(t, .1), size=21)
        P(c, t, tpr, 700, 610, "That's why it feels premium", 32, "check")
        P(c, t, two, 1250, 610, "Never a constant wobble", 32, "cross", RED)
        for i, (s, t0, cc) in enumerate([("STILL", tst, "#9cdcfe"), ("SMOOTH MOVE", tsm, YEL), ("DEAD HOLD", tde, "#9cdcfe"), ("SLOW DRIFT", tdr, GREEN), ("FAST SNAP", tfs, RED)]):
            k = wk(t, t0, .3)
            if k > 0:
                x = 190 + i * 320
                with Pop(c, x, 720, 290, 110, k):
                    rrect(c, x, 720, 290, 110, 22, "#17171b"); rrect(c, x, 720, 290, 8, 4, cc)
                    text(c, s, x + 145, 790, 30, "x", "#ffffff", 1, "c")
        bgdock(c, 3)
    return cam, draw

def s20(T0, D):
    r = R(T0); tfr = r("frame"); tbr = r("headless"); t30 = r("30"); tst = r("stitches"); tmp = r("mp4")
    def lines(t):
        L = [(0, "$ node render.js --from 0 --to 2910", "#e5e5e5"), (tbr, "launching headless browser (chromium)...", "#9cdcfe")]
        if t > tfr + .3:
            n = int(clamp((t - tfr - .3) / (tst - tfr - .3)) * 2910)
            L.append((tfr + .3, f"rendering frame {n:04d} / 2910   ({n * 100 // 2910}%)", "#b5cea8"))
        L += [(t30, "30 frames for every second of video", "#9cdcfe"), (tst, "$ ffmpeg -framerate 30 -i frames/f_%04d.png episode.mp4", "#e5e5e5"),
              (tmp, "done -> episode.mp4", "#22c55e")]
        return L
    cam = drift(D, 1.0, 1.05)
    sfx(0, "whoosh", .7); sfx(tbr, "pop", .4); sfx(t30, "pop", .4); type_sfx(tst, "ffmpeg -framerate 30", 30); sfx(tmp, "ding", .6)
    def draw(c, t):
        bg(c, "Terminal")
        term_window(c, 260, 110, 1400, 520, lines(t), t, a=wk(t, .1), sc=wsc(t, .1), size=24)
        P(c, t, tfr, 560, 720, "One frame at a time", 32, "check")
        P(c, t, t30, 960, 720, "30 fps", 32, "check")
        P(c, t, tmp, 1330, 720, "Stitched into an MP4", 32, "check")
        bgdock(c, 4)
    return cam, draw

def s21(T0, D):
    r = R(T0); tor = r("original"); tsl = r("same"); tcm = r("camera"); ttm = r("timing")
    v1 = V("ref.mp4", 0.0); v2 = V("ours4.mp4", 0.0)
    cam = drift(D, 1.0, 1.03)
    sfx(0, "whoosh", .7); sfx(.2, "pop", .5); cues([tsl, tcm, ttm], "ding", .5)
    def draw(c, t):
        bg(c, "Compare")
        fi = int(t * FPS) % 119
        vwin(c, 470, 60, 780, v1, fi, "THEIR VIDEO", a=wk(t, .1), sc=wsc(t, .1))
        vwin(c, 1010, 60, 780, v2, fi, "CLAUDE'S VERSION", a=wk(t, .2), sc=wsc(t, .2))
        label(c, "THEIR VIDEO", 689, 140, wk(t, .5), "#ffffff"); label(c, "CLAUDE'S VERSION", 1229, 140, wk(t, .6), CORAL)
        for i, (s, t0) in enumerate([("Same lens", tsl), ("Same camera move", tcm), ("Same timing", ttm)]):
            P(c, t, t0, 220 if i == 0 else (W - 220 if i == 2 else 220), 400 + (i % 2) * 0 + i * 140 if i != 2 else 470, s, 30, "check")
        bgdock(c, 2)
    return cam, draw

def s22(T0, D):
    r = R(T0); tst = r("story"); tch = r("characters"); tsc = r("scratch"); tbo = r("body"); tey = r("eyes"); teb = r("eyebrows"); tmo = r("mouth")
    img = IMG("maya.png")
    cam = Cam([(0, 960, 540, 1.0), (tey - .2, 960, 540, 1.0), (tey + .4, 1000, 380, 1.5), (D, 1000, 390, 1.55)])
    sfx(0, "whoosh", .7); sfx(tch, "pop", .5); sfx(tsc, "ding", .5); cues([tbo, tey, teb, tmo])
    def draw(c, t):
        bg(c, "Characters")
        ttl(c, t, tst - .1, "A STORY NEEDS CHARACTERS", 470, 84, "#ffffff", t1=tch + .4)
        if t > tch + .2:
            iwin(c, 760, 50, 480, 853, img, "maya  (built from scratch)", a=wk(t, tch + .2), sc=wsc(t, tch + .2))
            P(c, t, tsc, 1400, 200, "Built from scratch", 34, "check")
            P(c, t, tbo, 1400, 300, "Body", 30, "check")
            tag(c, "eyes", 830, 365, wk(t, tey, .3)); tag(c, "eyebrows", 1080, 330, wk(t, teb, .3)); tag(c, "mouth", 1080, 470, wk(t, tmo, .3))
        bgdock(c, 0)
    return cam, draw

def ik(sx, sy, tx, ty, l1, l2, flip=1):
    d = min(math.hypot(tx - sx, ty - sy), l1 + l2 - 1e-3); a = math.atan2(ty - sy, tx - sx)
    cb = clamp((l1 * l1 + d * d - l2 * l2) / (2 * l1 * d), -1, 1); b = math.acos(cb)
    ex, ey = sx + l1 * math.cos(a - flip * b), sy + l1 * math.sin(a - flip * b)
    k = d / math.hypot(tx - sx, ty - sy) if math.hypot(tx - sx, ty - sy) > 0 else 1
    return ex, ey, sx + (tx - sx) * k, sy + (ty - sy) * k

def s23(T0, D):
    r = R(T0); tik = r("inverse"); tput = r("put"); tel = r("elbow"); twk = r("walkie"); tbk = r("bike"); tfe = r("fence")
    targets = [(0, 520, 380), (tput, 520, 380), (tput + .8, 700, 300), (tel + .4, 640, 560), (tel + 1.2, 420, 520), (D, 560, 330)]
    tp = Path2(targets)
    cam = drift(D, 1.0, 1.04)
    sfx(0, "whoosh", .7); sfx(tik, "pop", .5); sfx(tput, "click", .6); sfx(tel, "pop", .4); cues([twk, tbk, tfe])
    def draw(c, t):
        bg(c, "Characters")
        k = wk(t, .1)
        with Pop(c, 120, 90, 760, 760, k):
            panel(c, 120, 90, 760, 760)
            text(c, "Inverse kinematics", 160, 150, 30, "b", "#ffffff")
            sx, sy = 260, 640; tx, ty = tp.at(t)
            ex, ey, hx, hy = ik(sx, sy, tx, ty, 260, 240)
            pa = paint(col("#c94a5a"), style="stroke", sw=44); pa.setStrokeCap(skia.Paint.kRound_Cap)
            c.drawLine(sx, sy, ex, ey, pa); c.drawLine(ex, ey, hx, hy, pa)
            for (x, y, s) in ((sx, sy, "shoulder"), (ex, ey, "elbow")):
                c.drawCircle(x, y, 14, paint(col("#ffffff"))); text(c, s, x + 22, y + 40, 22, "s", "#d4d4d8")
            c.drawCircle(hx, hy, 26, paint(col("#e8b48a")))
            kk = wk(t, tput, .3)
            if kk > 0:
                c.drawCircle(tx, ty, 18, paint(col(YEL, kk), style="stroke", sw=4)); c.drawCircle(tx, ty, 5, paint(col(YEL, kk)))
                text(c, "\"put the hand here\"", tx - 120, ty - 34, 24, "s", YEL, kk)
        P(c, t, tel, 500, 900, "Elbow + shoulder figure themselves out", 26, "check")
        for i, (nm, t0, s) in enumerate([("sig_20.4.png", twk, "Grab a walkie-talkie"), ("sig_9.png", tbk, "Hold the handlebars"), ("sig_60.png", tfe, "Press against a fence")]):
            if t > t0 - .1:
                x = 960 + i * 310
                iwin(c, x, 140, 280, 498, IMG(nm), s.split()[-1], a=wk(t, t0 - .1), sc=wsc(t, t0 - .1))
                P(c, t, t0 + .1, x + 140, 720, s, 20, "check")
        bgdock(c, 0)
    return cam, draw

def mouth(c, x, y, o):
    rrect(c, x - 70, y - 10 - 60 * o, 140, 20 + 120 * o, 10 + 60 * o, "#3a0f12"); rrect_stroke(c, x - 70, y - 10 - 60 * o, 140, 20 + 120 * o, 10 + 60 * o, "#000000", 1, 6)

def s24(T0, D):
    r = R(T0); tfe = r("fear"); two = r("worry"); tte = r("tears"); tbl = r("black"); tmo = r("mouths"); tlo = r("loud"); tli = r("lip")
    cam = Cam([(0, 960, 540, 1.0), (tmo - .3, 960, 540, 1.0), (tmo + .3, 1180, 480, 1.08), (D, 1180, 480, 1.1)])
    sfx(0, "whoosh", .7); cues([tfe, two, tte]); sfx(tbl, "ding", .5); sfx(tmo, "whoosh_s", .5); sfx(tli, "ding", .6)
    def draw(c, t):
        bg(c, "Characters")
        iwin(c, 150, 60, 480, 853, IMG("sig_85.5.png"), "the fake Leo", a=wk(t, .1), sc=wsc(t, .1))
        P(c, t, tfe, 820, 200, "Fear", 30, "check"); P(c, t, two, 820, 290, "Worry", 30, "check"); P(c, t, tte, 820, 380, "Tears", 30, "check")
        P(c, t, tbl, 820, 470, "Eyes turn completely black", 30, "dot", RED)
        if t > tmo - .1:
            k = wk(t, tmo - .1, .35)
            with Pop(c, 1050, 230, 760, 560, k):
                panel(c, 1050, 230, 760, 560)
                text(c, "voice loudness  ->  mouth", 1090, 290, 26, "s", "#d4d4d8")
                wave(c, 1090, 330, 680, 160, T0 + t, CORAL, 56, scale=1.0)
                mouth(c, 1430, 640, clamp(env_at(T0 + t) * 1.1))
        P(c, t, tlo, 1430, 860, "Measured frame by frame", 26, "check")
        P(c, t, tli, 1430, 940 - 140, "Lip-sync: automatic", 32, "dot", YEL)
        bgdock(c, 0)
    return cam, draw

CODE_ELEVEN = [
    "LINES = {",
    "  'l5':  ('you',  '[whispers] [terrified] What is that...?'),",
    "  'l6':  ('leo',  '[panicked] [breathless] Something\\'s in the woods!'),",
    "  'l10': ('fake', '[eerily calm] I can\\'t... my leg\\'s stuck.'),",
    "  'l12': ('fake', '[crying] Please don\\'t leave me here...'),",
    "  'l13': ('you',  '[cold] One of them is my best friend.'),",
    "}",
    "",
    "audio = elevenlabs.text_to_speech(text, model='eleven_v4', voice=VOICE[who])",
]
def s25(T0, D):
    r = R(T0); t11 = r("11"); twh = r("whispers"); tpa = r("panicked"); tcr = r("crying"); tco = r("cold"); tapi = r("api")
    ttr = r("trims"); tti = r("tightens"); tfi = r("fits"); tde = r("dead")
    def hl(t):
        for a, s in ((tapi, 8), (tco, 5), (tcr, 4), (tpa, 2), (twh, 1)):
            if t > a: return (s, s + 1)
        return None
    def comp(i, t):  # waveform with gaps that close up
        k = eio(lin(t, ttr, tfi))
        ph = (i % 16) / 16.0
        if ph > .7: return .02 * (1 - k)
        return .25 + .6 * abs(math.sin(i * 1.7)) * (.6 + .4 * math.sin(i * .5))
    cam = Cam([(0, 960, 540, 1.0), (ttr - .3, 960, 380, 1.0), (ttr + .3, 960, 700, 1.15), (D, 960, 700, 1.15)])
    sfx(0, "whoosh", .7); sfx(t11, "pop", .5); cues([twh, tpa, tcr, tco]); sfx(tapi, "ding", .5); cues([ttr, tti, tfi]); sfx(tde, "ding", .5)
    def draw(c, t):
        bg(c, "Voices")
        code_window(c, 200, 60, 1520, 420, CODE_ELEVEN, hl=hl(t), title="eleven.py", reveal=int(t * 200), a=wk(t, .1), sc=wsc(t, .1), size=21)
        P(c, t, t11, 1560, 120, "ElevenLabs  ·  eleven_v4", 24, "dot", CORAL)
        if t > ttr - .2:
            k = wk(t, ttr - .2, .35)
            with Pop(c, 260, 560, 1400, 300, k):
                panel(c, 260, 560, 1400, 300)
                n = int(mix(96, 72, eio(lin(t, ttr, tfi))))
                wave(c, 300, 600, 1320 * n / 96, 220, 0, "#9cdcfe", n, src=lambda i: comp(i, t))
            P(c, t, ttr, 520, 920, "Trims silences", 26, "check"); P(c, t, tti, 960, 920, "Tightens pauses", 26, "check")
            P(c, t, tfi, 1400, 920, "Fits every line to its shot", 26, "check")
        bgdock(c, 5)
    return cam, draw

def s26(T0, D):
    r = R(T0); tef = r("effects"); twa = r("walkie"); tra = r("radio"); tse = r("second"); tec = r("echo"); tcp = r("copying")
    tsv = r("same"); ttv = r("two"); tre = r("real")
    cam = Cam([(0, 960, 540, 1.0), (tre - .4, 960, 520, 1.0), (tre + .1, 960, 520, 1.1), (D, 960, 520, 1.12)])
    sfx(0, "whoosh", .7); sfx(tef, "pop", .4); sfx(twa, "pop", .5); sfx(tra, "pop", .5); sfx(tse, "pop", .5); sfx(tec, "pop", .5); sfx(tsv, "ding", .5); sfx(tre, "rise", .5)
    def draw(c, t):
        bg(c, "Voices")
        P(c, t, tef, W / 2, 100, "It also adds effects", 34, "dot", YEL)
        for i, (nm, t0, cc, fx, t1) in enumerate([("LEO ON THE RADIO", twa, BLUE, ["Radio filter", "Static"], tra), ("\"LEO\" IN THE WOODS", tse, RED, ["Doubled echo", "Same voice"], tec)]):
            k = wk(t, t0, .35)
            if k <= 0: continue
            x = 200 + i * 800
            with Pop(c, x, 180, 720, 420, k):
                panel(c, x, 180, 720, 420); rrect(c, x, 180, 720, 10, 5, cc)
                text(c, nm, x + 40, 250, 34, "x", "#ffffff")
                wave(c, x + 40, 300, 640, 170, T0 + t if (i == 0 and t < tse) or (i == 1 and t >= tse) else T0 + t0 + 1.3, cc, 48, scale=1.0)
            for j, s in enumerate(fx): P(c, t, t1 + j * .3, x + 170 + j * 330, 540, s, 24, "check")
        P(c, t, tcp, W / 2, 680, "Twist: something is copying him", 32, "dot", RED, bgc="#2a1212")
        k = wk(t, tre - .3, .4)
        if k > 0: big_title(c, "WHICH ONE IS REAL?", 830, 86, k, "#ffffff")
        bgdock(c, 5)
    return cam, draw

def s27(T0, D):
    r = R(T0); tsu = r("subtitles"); tth = r("three"); tco = r("color"); twh = r("white"); tbl = r("blue"); trd = r("red")
    v = V("signal.mp4", 44.0)
    cam = drift(D, 1.0, 1.04)
    sfx(0, "whoosh", .7); sfx(tsu, "pop", .5); sfx(tth, "pop", .5); cues([twh, tbl, trd], "ding", .45)
    def draw(c, t):
        bg(c, "Subtitles")
        vwin(c, 300, 60, 830, v, int(t * FPS), "Signal in the Woods", a=wk(t, .1), sc=wsc(t, .1))
        P(c, t, tth, 1350, 180, "3 words at a time", 34, "check")
        for i, (s, who, cc, t0) in enumerate([("I'll pull you up!", "YOU", "#ffffff", twh), ("DON'T MOVE!", "FRIEND ON THE RADIO", "#6fb6ff", tbl), ("Please don't leave", "THE THING IN THE WOODS", "#ff4d4d", trd)]):
            k = wk(t, t0, .3)
            if k <= 0: continue
            y = 300 + i * 190
            with Pop(c, 1000, y, 700, 160, k):
                panel(c, 1000, y, 700, 160); text(c, who, 1040, y + 50, 22, "s", "#a1a1aa")
                f = font("x", 54); c.drawString(s, 1040, y + 120, f, paint(col("#000000"), style="stroke", sw=10)); text(c, s, 1040, y + 120, 54, "x", cc)
        bgdock(c, 0)
    return cam, draw

def s28(T0, D):
    r = R(T0); tsu = r("surprised"); tco = r("code")
    items = [(r("crickets"), "Crickets go silent"), (r("chain"), "Bike chain clicking"), (r("skid"), "Tyre skid"), (r("streetlight"), "Streetlight buzz + pop"),
             (r("glass"), "Glass tinkling down"), (r("radiostatic"), "Radio static"), (r("fence"), "Fence rattling"), (r("shriek"), "Creature shriek")]
    cam = drift(D, 1.0, 1.04)
    sfx(0, "whoosh", .7); sfx(tco, "ding", .5); cues([i[0] for i in items])
    def draw(c, t):
        bg(c, "Sound")
        ttl(c, t, tsu - .1, "EVERY SOUND EFFECT", 160, 84, "#ffffff", sub="synthesised in code", subt=tco)
        for i, (t0, s) in enumerate(items):
            k = wk(t, t0, .3)
            if k <= 0: continue
            x = 130 + (i % 4) * 420; y = 320 + (i // 4) * 300
            with Pop(c, x, y, 390, 260, k):
                panel(c, x, y, 390, 260); text(c, s, x + 30, y + 54, 26, "b", "#ffffff")
                seed = i * 13.7
                wave(c, x + 30, y + 90, 330, 130, 0, [CORAL, YEL, "#9cdcfe", GREEN, PURP, "#9cdcfe", YEL, RED][i], 30,
                     src=lambda j, s_=seed: (.15 + .85 * abs(math.sin(j * .9 + s_ + t * 6))) * (.4 + .6 * abs(math.sin(j * .23 + s_))))
        bgdock(c, 5)
    return cam, draw

def s29(T0, D):
    r = R(T0); tmu = r("music"); tsy = r("synth"); tar = r("peggio"); tdr = r("drone"); thit = r("hit"); tsil = r("silence"); tco = r("copied"); tnn = r("note")
    secs = [("ARPEGGIO", tar, "the ride", BLUE), ("DARK DRONE", tdr, "woods glowing", PURP), ("HEAVY HIT", thit, "creature appears", RED), ("SILENCE + HEARTBEAT", tsil, "freeze frame", "#ffffff")]
    cam = drift(D, 1.0, 1.05)
    sfx(0, "whoosh", .7); sfx(tsy, "pop", .5); cues([s[1] for s in secs]); sfx(tco, "pop", .5); sfx(tnn, "ding", .5)
    def draw(c, t):
        bg(c, "Music")
        ttl(c, t, tmu - .1, "ORIGINAL 80s SYNTH SCORE", 140, 76, "#ffffff")
        k = wk(t, tsy, .35)
        if k > 0:
            with Pop(c, 140, 230, 1640, 420, k):
                panel(c, 140, 230, 1640, 420)
                for row in range(12): c.drawLine(180, 270 + row * 30, 1740, 270 + row * 30, paint(col("#ffffff", .05), style="stroke", sw=1))
                for i, (nm, t0, sub, cc) in enumerate(secs):
                    kk = wk(t, t0, .4)
                    if kk <= 0: continue
                    x0 = 180 + i * 390
                    for j in range(int(16 * kk)):
                        if i == 0: y = 270 + [0, 3, 7, 8, 7, 3, 0, 11][j % 8] * 30; w_ = 22
                        elif i == 1: y = 270 + (9 if j % 2 else 10) * 30; w_ = 44
                        elif i == 2: y = 270 + (j % 3 + 9) * 30; w_ = 70 if j < 4 else 0
                        else: y = 270 + 10 * 30; w_ = 10 if j % 8 == 0 else 0
                        if w_: rrect(c, x0 + j * 22, y, w_, 22, 5, cc, .9)
                    text(c, nm, x0, 615, 24, "x", cc); text(c, sub, x0 + 300, 615, 18, "m", "#a1a1aa", 1, "r")
        P(c, t, tco, 680, 760, "Not copied from any show", 32, "check")
        P(c, t, tnn, 1240, 760, "Composed note by note in code", 32, "check")
        bgdock(c, 5)
    return cam, draw

def s30(T0, D):
    r = R(T0); tmx = r("mixes"); tdk = r("ducks"); tlu = r("lufs"); tin = r("instagram"); ttk = r("tiktok"); tyt = r("youtube")
    cam = drift(D, 1.0, 1.05)
    sfx(0, "whoosh", .7); sfx(tmx, "pop", .5); sfx(tdk, "whoosh_s", .4); sfx(tlu, "ding", .6); cues([tin, ttk, tyt])
    def draw(c, t):
        bg(c, "Mixer")
        k = wk(t, .1)
        with Pop(c, 260, 90, 820, 760, k):
            panel(c, 260, 90, 820, 760); text(c, "Mix", 300, 150, 30, "b", "#ffffff")
            duck = eio(lin(t, tdk, tdk + .6))
            for i, (nm, lv, cc) in enumerate([("VOICE", .82, CORAL), ("MUSIC", mix(.7, .35, duck), PURP), ("SFX", .5, "#9cdcfe")]):
                x = 360 + i * 240
                rrect(c, x, 210, 24, 520, 12, "#2a2a30"); rrect(c, x, 210 + 520 * (1 - lv), 24, 520 * lv, 12, cc)
                rrect(c, x - 30, 200 + 520 * (1 - lv), 84, 30, 8, "#e5e5e5")
                text(c, nm, x + 12, 790, 24, "b", "#ffffff", 1, "c")
            if duck > 0: label(c, "music ducks under dialogue", 670, 180, duck, PURP, 22)
        kk = wk(t, tlu - .3, .4)
        if kk > 0:
            with Pop(c, 1180, 170, 520, 380, kk):
                panel(c, 1180, 170, 520, 380); text(c, "loudness", 1440, 240, 26, "s", "#a1a1aa", 1, "c")
                text(c, "-14", 1440, 400, 150, "d", YEL, 1, "c"); text(c, "LUFS", 1440, 480, 40, "x", "#ffffff", 1, "c")
        P(c, t, tin, 1300, 640, "Instagram", 28, "check"); P(c, t, ttk, 1560, 640, "TikTok", 28, "check"); P(c, t, tyt, 1440, 740, "YouTube", 28, "check")
        bgdock(c, 5)
    return cam, draw

def s31(T0, D):
    r = R(T0); tpg = r("page"); tga = r("gas"); tlk = r("lock"); tcop = r("cop"); t80 = r("80s"); tbmx = r("bmx"); tsig = r("signal")
    v1 = V("gas1.mp4", 6.0); v2 = V("signal.mp4", 8.0)
    cam = Cam([(0, 960, 540, 1.0), (tga, 960, 540, 1.0), (tga + .5, 700, 480, 1.18), (t80 - .3, 700, 480, 1.18), (t80 + .3, 1220, 480, 1.18), (D, 1220, 480, 1.2)])
    sfx(0, "whoosh", .7); sfx(tpg, "pop", .5); sfx(tga, "pop", .6); sfx(tcop, "pop", .4); sfx(t80, "whoosh_s", .5); sfx(t80 + .1, "pop", .6)
    def draw(c, t):
        bg(c, "My page")
        P(c, t, tpg, W / 2, 80, "MY OWN ORIGINAL EPISODES", 34, "dot", CORAL)
        if t > tga - .1:
            vwin(c, 470, 150, 750, v1, int((t - tga) * FPS), "Episode 1: Gas Station", a=wk(t, tga - .1), sc=wsc(t, tga - .1))
            P(c, t, tlk, 680, 960 - 60, "\"LOCK THE DOOR\"", 26, "dot", RED)
        if t > t80 - .1:
            vwin(c, 1030, 150, 750, v2, int((t - t80) * FPS), "The Signal in the Woods", a=wk(t, t80 - .1), sc=wsc(t, t80 - .1))
            P(c, t, tbmx, 1240, 960 - 60, "80s sci-fi horror", 26, "dot", BLUE)
        bgdock(c, 2)
    return cam, draw

def s32(T0, D):
    r = R(T0); tch = r("choice"); tpt = r("part"); t30 = r("30"); t349 = r("349"); tzero = r("zero"); tev = r("every", 8); tcl = r("clod")
    vc = V("signal.mp4", 89.6); prof = IMG("my_profile2.png")
    WX, WY, WW, WH = 800, 50, 560, 880
    S = WW / 1224; IH = 2720 * S; CH = WH - 38; SCR = IH - CH; K = 1224 / 900
    def scroll(t): return SCR * eio(lin(t, tzero + .2, tzero + 1.0))
    def py(y900, t): return WY + 38 + y900 * K * S - scroll(t)
    def px(x900): return WX + x900 * K * S
    dy = WY + 38 + 785 * K * S
    ry = WY + 38 + 1818 * K * S - SCR
    cam = Cam([(0, 960, 540, 1.0), (t30 - .4, 960, 540, 1.0), (t30 + .3, px(450), dy, 1.7), (tzero, px(450), dy, 1.75),
               (tzero + 1.0, px(450), ry - 40, 1.45), (tcl - .5, px(450), ry - 40, 1.5), (tcl - .2, 960, 540, 1.0), (D, 960, 540, 1.03)])
    sfx(0, "whoosh", .7); sfx(tch, "pop", .5); sfx(tpt, "pop", .4); sfx(t30, "whoosh_s", .5); sfx(t349, "ding", .7)
    sfx(tzero + .2, "whoosh_s", .5); sfx(tzero + 1.1, "ding", .5); sfx(tzero + 1.4, "ding", .5); sfx(tzero + 1.7, "pop", .5); sfx(tcl, "ding", .5)
    def page(c2, x, y, w, h, t):
        rrect(c2, x, y, w, h, 0, "#0c0f14"); draw_img(c2, prof, x, y - scroll(t), w, IH)
    def draw(c, t):
        bg(c, "My page")
        vwin(c, 160, 60, 830, vc, int(t * FPS), "every episode ends with a choice", a=wk(t, .1) * (1 - lin(t, t30 - .5, t30 - .2)), sc=wsc(t, .1))
        P(c, t, tpt, 650, 940 - 40, "Comments decide Part 2", 28, "dot", YEL, t1=t30 - .5)
        if t > t30 - .6:
            window(c, WX, WY, WW, WH, "Instagram  •  my page", a=wk(t, t30 - .6), sc=wsc(t, t30 - .6),
                   content=lambda c2, x, y, w, h: page(c2, x, y, w, h, t), bg="#0c0f14")
            kd = wk(t, t349, .5) * (1 - lin(t, tzero + .1, tzero + .4))
            ann_circle(c, px(270), py(795, t), 120, kd)
            k = wk(t, t349 + .1, .4) * (1 - lin(t, tzero + .1, tzero + .4))
            if k > 0:
                with Pop(c, px(450) - 180, py(785, t) + 70, 360, 120, k):
                    x0, y0 = px(450) - 180, py(785, t) + 70
                    rrect(c, x0, y0, 360, 120, 26, "#111114", .95); rrect_stroke(c, x0, y0, 360, 120, 26, GREEN, .9, 3)
                    text(c, "349.4K views", x0 + 180, y0 + 60, 40, "x", "#ffffff", 1, "c"); text(c, "in the last 30 days", x0 + 180, y0 + 100, 22, "m", "#a1a1aa", 1, "c")
            for i, (xx, s_, cc) in enumerate([(660, "330K", GREEN), (370, "80.2K", YEL), (80, "10.7K", "#9cdcfe")]):
                t0 = tzero + 1.1 + i * .3
                kk = wk(t, t0, .4)
                if kk > 0:
                    ann_circle(c, px(xx + 12), py(1816, t), 44, kk, cc)
            kr = wk(t, tzero + 1.8, .4)
            if kr > 0: label(c, "Reel views:  330K  ·  80.2K  ·  10.7K", px(450), py(1818, t) + 95, kr, GREEN, 22)
            P(c, t, tzero, 1650, 300, "Started from zero", 30, "dot", YEL)
            P(c, t, tcl, 1650, 420, "100% made with Claude", 30, "check")
        bgdock(c, 2)
    return cam, draw

def s33(T0, D):
    r = R(T0); tsk = r("skill"); tfig = r("figure"); thw = r("here's")
    cam = drift(D, 1.0, 1.06)
    sfx(0, "whoosh", .8); sfx(tsk, "rise", .5); sfx(tsk + .3, "ding", .6); sfx(thw, "whoosh_s", .5)
    def draw(c, t):
        bg(c, "Finder")
        ttl(c, t, tsk - .3, "SO I MADE IT A SKILL", 300, 110, "#ffffff")
        k = wk(t, tsk + .2, .4)
        if k > 0:
            with Pop(c, 760, 420, 400, 320, k):
                rrect(c, 860, 430, 200, 250, 24, CORAL); rrect(c, 860, 430, 200, 80, 24, "#ffffff", .15)
                text(c, "ZIP", 960, 600, 56, "x", "#ffffff", 1, "c")
                text(c, "pov-3d-animation.zip", 960, 730, 28, "s", "#ffffff", 1, "c")
        P(c, t, thw, W / 2, 860, "Here's exactly how to use it", 34, "dot", YEL)
        bgdock(c, 0)
    return cam, draw

GEM_PROMPT = "You are a film director for 60-120 s vertical POV animated thrillers. Write a director's brief: characters, subtitle colours, shot list with timestamps, dialogue, SFX, freeze-frame choice..."
def gem_window(c, x, y, w, h, t, T):
    def f(c2, cx, cy, cw, ch):
        rrect(c2, cx, cy, cw, ch, 0, "#131314")
        text(c2, "Gemini", cx + 30, cy + 44, 24, "b", "#e3e3e3")
        yy = cy + 90
        k = wk(t, T["paste"], .3)
        if k > 0:
            lines = wrap(GEM_PROMPT, 18, cw * .55)
            bw = cw * .6; bh = len(lines) * 27 + 70; bx = cx + cw - bw - 30
            c2.saveLayerAlpha(None, int(255 * k)); rrect(c2, bx, yy, bw, bh, 18, "#2a2a2c")
            for i, l in enumerate(lines): text(c2, l, bx + 22, yy + 36 + i * 27, 18, "m", "#e3e3e3")
            s, _ = typed("Idea: a night-shift cashier hears knocking from the freezer.", t, T["idea"], 30)
            text(c2, s, bx + 22, yy + 36 + len(lines) * 27 + 12, 18, "b", YEL); c2.restore(); yy += bh + 30
        brief = [("DIRECTOR'S BRIEF — \"COLD STORAGE\"", T["brief"]), ("CHARACTERS: You (white) · Dana, manager (pink) · ??? (red)", T["chars"]),
                 ("SUBTITLE COLOURS: white / pink / red", T["cols"]), ("SHOT LIST", T["shots"]), ("0:00-0:04  POV behind the counter, 2:14 AM, fridge hum", T["shots"] + .4),
                 ("0:04-0:09  KNOCK. KNOCK. From inside the freezer.  SFX: muffled thuds", T["shots"] + .8), ("0:09-0:13  Dana (radio): \"Don't open it.\"", T["shots"] + 1.2),
                 ("DIALOGUE + SFX for every shot ...", T["dia"]), ("FREEZE: OPEN THE FREEZER / CALL THE POLICE", T["sfx"])]
        for i, (s, t0) in enumerate(brief):
            kk = wk(t, t0, .25)
            if kk > 0: text(c2, s, cx + 70, yy + 30 + i * 36, 19 if i else 22, "b" if i in (0, 3) else "m", "#ffffff" if i in (0, 3) else "#c9c9c9", kk)
        if t > T["brief"]: spark(c2, cx + 40, yy + 22, 12, "#8ab4f8", rot=t * 2 if t < T["sfx"] else 0)
        if t > T["copy"] - .5:
            rrect(c2, cx + 70, yy + 360, 150, 46, 12, "#2a2a2c"); text(c2, "Copy", cx + 145, yy + 390, 19, "s", "#ffffff", 1, "c")
            if t > T["copy"]: check(c2, cx + 250, yy + 383, 14, GREEN, clamp((t - T["copy"]) / .2))
    window(c, x, y, w, h, "gemini", content=f, bg="#131314", a=wk(t, .1), sc=wsc(t, .1))

def s34(T0, D):
    r = R(T0)
    T = dict(paste=r("prompt"), idea=r("story"), brief=r("gemini", 6), chars=r("characters"), cols=r("subtitle"), shots=r("shot"), dia=r("dialogue"), sfx=r("sound"), copy=r("copy"))
    tfi = r("first")
    cp = Path2([(0, 1500, 900), (T["copy"] - .6, 1500, 900), (T["copy"] - .05, 455, 63 + 38 + 90 + 230 + 360 + 23)])
    cam = Cam([(0, 960, 540, 1.0), (T["brief"], 960, 540, 1.0), (T["brief"] + .6, 900, 600, 1.12), (T["copy"] - .6, 900, 600, 1.12), (D, 900, 600, 1.12)])
    sfx(0, "whoosh", .7); sfx(tfi, "pop", .5); sfx(T["paste"], "pop", .6); type_sfx(T["idea"], "Idea: a night-shift cashier hears knocking", 30, 4, .6)
    cues([T["brief"], T["chars"], T["cols"], T["shots"], T["dia"], T["sfx"]], "pop", .35); sfx(T["copy"], "click", .7); sfx(T["copy"] + .1, "ding", .5)
    def draw(c, t):
        bg(c, "Browser")
        gem_window(c, 160, 63, 1600, 880, t, T)
        P(c, t, tfi, 300, 130, "STEP 1  ·  Write your brief with Gemini", 26, "dot", YEL, align="l")
        if t > T["copy"] - .6:
            x, y = cp.at(t); cursor(c, x, y, 1.0, 1 if abs(t - T["copy"]) < .12 else 0); click_ring(c, x, y, lin(t, T["copy"], T["copy"] + .4))
        bgdock(c, 2)
    return cam, draw

def s35(T0, D):
    r = R(T0); tdl = r("download"); tzi = r("zip")
    files = [(r("engine"), "engine/  (renderer, three.js)"), (r("lens"), "lens.glsl"), (r("characters"), "chars.js  (hands, faces, IK)"),
             (r("voice"), "voices.py + eleven.py"), (r("sound"), "sfx.py  (sound design)"), (r("two"), "examples/  (2 complete episodes)")]
    cam = drift(D, 1.0, 1.04)
    sfx(0, "whoosh", .7); sfx(tdl, "click", .6); sfx(tdl + 1.6, "ding", .5); cues([f[0] for f in files])
    def draw(c, t):
        bg(c, "Finder")
        P(c, t, 0, 300, 120, "STEP 2  ·  Download the skill", 26, "dot", YEL, align="l")
        k = wk(t, tdl - .1, .35)
        if k > 0:
            with Pop(c, 260, 220, 640, 220, k):
                panel(c, 260, 220, 640, 220); rrect(c, 300, 260, 110, 140, 18, CORAL); text(c, "ZIP", 355, 345, 32, "x", "#ffffff", 1, "c")
                text(c, "pov-3d-animation.zip", 440, 300, 26, "b", "#ffffff")
                pr = eio(lin(t, tdl, tdl + 1.5)); rrect(c, 440, 330, 420, 14, 7, "#2a2a30"); rrect(c, 440, 330, 420 * pr, 14, 7, BLUE)
                text(c, "Download complete" if pr >= 1 else f"Downloading...  {int(pr * 100)}%", 440, 380, 20, "m", "#a1a1aa")
        kk = wk(t, tzi - .2, .35)
        if kk > 0:
            with Pop(c, 1000, 160, 700, 700, kk):
                panel(c, 1000, 160, 700, 700); text(c, "Inside the zip", 1040, 220, 28, "b", "#ffffff")
                for i, (t0, s) in enumerate(files):
                    k3 = wk(t, t0, .25)
                    if k3 > 0:
                        y = 280 + i * 92; rrect(c, 1040, y, 620, 72, 14, "#202026", k3)
                        rrect(c, 1060, y + 18, 44, 36, 8, BLUE if "/" in s else "#a1a1aa", k3); text(c, s, 1124, y + 46, 24, "s", "#ffffff", k3)
                        check(c, 1630, y + 36, 14, GREEN, clamp((t - t0 - .2) / .2))
        bgdock(c, 0)
    return cam, draw

def settings_window(c, x, y, w, h, t, T):
    def f(c2, cx, cy, cw, ch):
        rrect(c2, cx, cy, cw, ch, 0, "#262624"); rrect(c2, cx, cy, 280, ch, 0, "#1f1f1d")
        spark(c2, cx + 36, cy + 40, 13, CORAL); text(c2, "Claude", cx + 60, cy + 47, 20, "s", "#ecebe6")
        for i, s in enumerate(["Chats", "Projects", "Customize", "Settings"]):
            sel = (s == "Customize" and t > T["cust"])
            if sel: rrect(c2, cx + 14, cy + 90 + i * 48, 252, 40, 9, "#3a3a36")
            text(c2, s, cx + 34, cy + 117 + i * 48, 18, "s" if sel else "m", "#ffffff" if sel else "#c9c7bf")
        if t > T["cust"]:
            text(c2, "Customize", cx + 330, cy + 70, 30, "b", "#ffffff")
            for i, s in enumerate(["Connectors", "Skills"]):
                sel = s == "Skills" and t > T["skills"]
                rrect(c2, cx + 330 + i * 170, cy + 100, 150, 42, 21, "#3a3a36" if sel else "#2f2f2c"); text(c2, s, cx + 405 + i * 170, cy + 128, 18, "s", "#ffffff", 1, "c")
            if t > T["skills"]:
                text(c2, "Skills", cx + 330, cy + 210, 24, "b", "#ffffff")
                rrect(c2, cx + cw - 110, cy + 180, 60, 44, 12, CORAL); text(c2, "+", cx + cw - 80, cy + 212, 30, "b", "#ffffff", 1, "c")
                for i, s in enumerate(["skill-creator", "docx"]):
                    rrect(c2, cx + 330, cy + 250 + i * 76, cw - 380, 62, 12, "#2f2f2c"); text(c2, s, cx + 360, cy + 288 + i * 76, 19, "m", "#d4d4d8")
                if t > T["plus"]:
                    k = wk(t, T["plus"], .25)
                    with Pop(c2, cx + cw - 360, cy + 230, 300, 150, k):
                        panel(c2, cx + cw - 360, cy + 230, 300, 150, 14, "#1d1d1b")
                        text(c2, "Create skill", cx + cw - 336, cy + 274, 18, "m", "#c9c7bf")
                        rrect(c2, cx + cw - 352, cy + 300, 284, 42, 9, "#3b3b37" if t > T["upload"] - .3 else "#1d1d1b")
                        text(c2, "Upload a skill", cx + cw - 336, cy + 328, 18, "s", "#ffffff")
                if t > T["done"]:
                    k = wk(t, T["done"], .3)
                    with Pop(c2, cx + 330, cy + 402, cw - 380, 70, k):
                        rrect(c2, cx + 330, cy + 402, cw - 380, 70, 12, "#1f3a2a"); rrect_stroke(c2, cx + 330, cy + 402, cw - 380, 70, 12, GREEN, .8, 2)
                        text(c2, "pov-3d-animation-aivxer", cx + 360, cy + 445, 20, "b", "#ffffff"); check(c2, cx + cw - 90, cy + 437, 16, GREEN, clamp((t - T["done"]) / .2))
    window(c, x, y, w, h, "Claude — Settings", content=f, bg="#262624", a=wk(t, .1), sc=wsc(t, .1))

def s36(T0, D):
    r = R(T0)
    T = dict(cust=r("customize"), skills=r("skills"), plus=r("plus"), upload=r("upload"), done=r("installed") - .3)
    X, Y = 260, 80; WW = 1400
    cp = Path2([(0, 1300, 800), (T["cust"] - .5, 1300, 800), (T["cust"] - .05, X + 80, Y + 38 + 117 + 96 - 6), (T["skills"] - .05, X + 575, Y + 38 + 122),
                (T["plus"] - .05, X + WW - 80, Y + 38 + 202), (T["upload"] - .05, X + WW - 230, Y + 38 + 322), (D, X + WW - 230, Y + 38 + 340)])
    clicks = [T["cust"], T["skills"], T["plus"], T["upload"]]
    cam = Cam([(0, 960, 540, 1.0), (T["cust"] - .3, 960, 540, 1.0), (T["skills"], 1000, 420, 1.12), (D, 1100, 420, 1.15)])
    sfx(0, "whoosh", .7); cues(clicks, "click", .7); sfx(T["done"], "ding", .6)
    def draw(c, t):
        bg(c, "Claude")
        settings_window(c, X, Y, WW, 820, t, T)
        P(c, t, 0, 300, 940 - 20, "STEP 3  ·  Upload it to Claude", 26, "dot", YEL, align="l")
        x, y = cp.at(t); pr = max([1 if abs(t - k) < .1 else 0 for k in clicks]); cursor(c, x, y, 1.0, pr)
        for k in clicks: click_ring(c, x, y, lin(t, k, k + .4))
        bgdock(c, 1)
    return cam, draw

def el_window(c, x, y, w, h, t, T):
    def f(c2, cx, cy, cw, ch):
        rrect(c2, cx, cy, cw, ch, 0, "#0f0f10"); rrect(c2, cx, cy, 260, ch, 0, "#161618")
        text(c2, "ElevenLabs", cx + 30, cy + 50, 24, "x", "#ffffff")
        for i, s in enumerate(["Home", "Voices", "Text to Speech", "API Keys"]):
            sel = s == "API Keys" and t > T["keys"]
            if sel: rrect(c2, cx + 14, cy + 90 + i * 48, 232, 40, 9, "#2a2a2e")
            text(c2, s, cx + 34, cy + 117 + i * 48, 18, "s" if sel else "m", "#ffffff" if sel else "#a1a1aa")
        if t > T["keys"]:
            text(c2, "API Keys", cx + 310, cy + 70, 30, "b", "#ffffff")
            rrect(c2, cx + cw - 260, cy + 40, 220, 48, 12, "#ffffff"); text(c2, "+ Create API key", cx + cw - 150, cy + 71, 18, "s", "#000000", 1, "c")
        if t > T["create"]:
            k = wk(t, T["create"], .3)
            with Pop(c2, cx + 420, cy + 140, 620, 420, k):
                panel(c2, cx + 420, cy + 140, 620, 420, 18, "#1b1b1e")
                text(c2, "Create API key", cx + 450, cy + 190, 24, "b", "#ffffff")
                rrect(c2, cx + 450, cy + 220, 560, 48, 10, "#26262a"); text(c2, "pov-videos", cx + 470, cy + 252, 18, "m", "#ffffff")
                text(c2, "Permissions", cx + 450, cy + 310, 18, "s", "#a1a1aa")
                on = t > T["tts"]
                text(c2, "Text to Speech", cx + 450, cy + 360, 20, "m", "#ffffff")
                rrect(c2, cx + 930, cy + 338, 70, 34, 17, GREEN if on else "#3a3a3e"); c2.drawCircle(cx + (982 if on else 948), cy + 355, 13, paint(col("#ffffff")))
                if t > T["tts"] + .6:
                    rrect(c2, cx + 450, cy + 420, 560, 52, 10, "#26262a"); text(c2, "sk_••••••••••••••••••••••••", cx + 470, cy + 454, 20, "mono", "#ffffff")
    window(c, x, y, w, h, "elevenlabs.io", content=f, bg="#0f0f10", a=wk(t, .1), sc=wsc(t, .1))

def s37(T0, D):
    r = R(T0); tf = r("fourth")
    T = dict(keys=r("api"), create=r("create"), tts=r("text"))
    tfree = r("free"); tcom = r("commercial")
    cam = Cam([(0, 960, 540, 1.0), (T["create"], 960, 540, 1.0), (T["create"] + .5, 1060, 470, 1.18), (tfree - .3, 1060, 470, 1.18), (tfree + .3, 960, 540, 1.0), (D, 960, 540, 1.02)])
    sfx(0, "whoosh", .7); sfx(T["keys"], "click", .6); sfx(T["create"], "click", .6); sfx(T["tts"], "click", .6); sfx(T["tts"] + .6, "ding", .5); sfx(tfree, "pop", .5); sfx(tcom, "pop", .5)
    def draw(c, t):
        bg(c, "Browser")
        el_window(c, 220, 70, 1480, 720, t, T)
        P(c, t, tf, 300, 860, "STEP 4  ·  Get your ElevenLabs key", 26, "dot", YEL, align="l")
        P(c, t, tfree, 1000, 860, "Free plan: default voices only", 26, "dot", YEL, align="l")
        P(c, t, tcom, 1000, 940 - 20, "Commercial use: paid plan", 26, "dot", RED, align="l")
        bgdock(c, 2)
    return cam, draw

def s38(T0, D):
    r = R(T0); tf = r("fifth"); tas = r("asks"); tse = r("secure"); tnv = r("never")
    def chat(c2, cx, cy, cw, ch, t):
        rrect(c2, cx, cy, cw, ch, 0, CHAT_BG)
        spark(c2, cx + 60, cy + 60, 13, CORAL)
        s, _ = typed("To make the voices I need your ElevenLabs API key. Please paste it into the secure form below.", t, tas, 60)
        for i, l in enumerate(wrap(s, 20, cw - 160)): text(c2, l, cx + 90, cy + 68 + i * 30, 20, "m", "#ecebe6")
        k = wk(t, tse, .3)
        if k > 0:
            with Pop(c2, cx + 90, cy + 160, 620, 220, k):
                panel(c2, cx + 90, cy + 160, 620, 220, 16, "#1d1d1b"); text(c2, "Secure form  ·  api.elevenlabs.io", cx + 120, cy + 205, 20, "b", "#ffffff")
                rrect(c2, cx + 120, cy + 230, 560, 52, 10, "#2f2f2c"); text(c2, "•" * int(clamp((t - tse - .4) * 20, 0, 26)), cx + 140, cy + 264, 22, "mono", "#ffffff")
                rrect(c2, cx + 120, cy + 300, 120, 50, 12, CORAL); text(c2, "Save", cx + 180, cy + 332, 20, "s", "#ffffff", 1, "c")
                if t > tse + 2: check(c2, cx + 280, cy + 325, 16, GREEN, clamp((t - tse - 2) / .2))
    cam = drift(D, 1.0, 1.04, 960, 480)
    sfx(0, "whoosh", .7); sfx(tf, "pop", .5); sfx(tse, "pop", .6); sfx(tse + 2, "ding", .5); sfx(tnv, "pop", .6)
    def draw(c, t):
        bg(c, "Claude")
        window(c, 160, 70, 1100, 520, "Claude", content=lambda c2, x, y, w, h: chat(c2, x, y, w, h, t), bg=CHAT_BG, a=wk(t, .1), sc=wsc(t, .1))
        P(c, t, tf, 300, 680, "STEP 5  ·  This is important", 26, "dot", YEL, align="l")
        k = wk(t, tnv, .35)
        if k > 0:
            with Pop(c, 1320, 200, 480, 300, k):
                panel(c, 1320, 200, 480, 300); text(c, "In the chat", 1360, 260, 26, "b", "#ffffff")
                rrect(c, 1360, 300, 400, 60, 18, "#3a3a36"); text(c, "here's my key: sk_8f3...", 1380, 340, 20, "m", "#f4f3ee")
                cross(c, 1560, 430, 36, RED)
            P(c, t, tnv + .2, 1560, 560, "NEVER paste your key in the chat", 26, "cross", RED)
        bgdock(c, 1)
    return cam, draw

def s39(T0, D):
    r = R(T0); tsx = r("sixth"); trd = r("reads"); tpl = r("plans"); tst = r("still"); tpv = r("preview"); tyes = r("yes"); tbu = r("builds")
    tch, tca, tvo, tsu, tmu, ten = r("characters"), r("camera"), r("voices"), r("subtitles"), r("music"), r("end")
    tfm = r("format"); t916 = r("9x16"); t169 = r("16x9")
    msgs = [dict(role="user", text="DIRECTOR'S BRIEF — \"COLD STORAGE\"  ·  9:16 · 75 s · 3 characters · 14 shots ...", t0=tsx + .3),
            dict(role="ai", text="Great brief. Here's my plan:", t0=trd, items=[("Plan the episode", tst - .2, tpl), ("Still frames for every shot", tpv - .2, tst), ("10 s preview", tyes - .4, tpv)]),
            dict(role="user", text="yes, build it", t0=tyes),
            dict(role="ai", text="Building the full video:", t0=tbu, busy=True, items=[("Characters", tch + .3, tch), ("Camera", tca + .3, tca), ("Voices", tvo + .3, tvo), ("Subtitles", tsu + .3, tsu), ("Music", tmu + .3, tmu), ("End-screen choice", ten + .4, ten)])]
    cam = Cam([(0, 960, 540, 1.0), (tsx + .3, 960, 540, 1.0), (trd, 1100, 330, 1.4), (tbu - .2, 1100, 400, 1.4), (tbu + .6, 1050, 560, 1.3), (tfm - .4, 1050, 640, 1.3), (tfm + .2, 960, 540, 1.0), (D, 960, 540, 1.02)])
    sfx(0, "whoosh", .7); sfx(tsx + .3, "pop", .6); sfx(trd, "pop", .4); cues([tpl, tst, tpv], "ding", .35); sfx(tyes, "pop", .6)
    cues([tch, tca, tvo, tsu, tmu, ten], "ding", .35); sfx(tfm, "whoosh_s", .5); cues([t916, t169])
    def draw(c, t):
        bg(c, "Claude")
        kc = 1 - lin(t, tfm - .2, tfm + .2)
        if kc > 0: chat_window(c, 230, 60, 1460, 880, t, msgs, a=wk(t, .1) * kc, sc=wsc(t, .1))
        P(c, t, tsx, 330, 140, "STEP 6  ·  Paste your brief", 24, "dot", YEL, align="l", t1=tfm - .2)
        for i, (s, t0, w_, h_) in enumerate([("9:16  Reels · TikTok · Shorts", t916, 300, 533), ("16:9  YouTube", t169, 760, 428)]):
            k = wk(t, t0, .35)
            if k <= 0: continue
            x = 420 if i == 0 else 860; y = 200
            with Pop(c, x, y, w_, h_, k):
                panel(c, x, y, w_, h_); rrect_stroke(c, x + 20, y + 20, w_ - 40, h_ - 40, 14, YEL, .9, 3)
                text(c, s.split("  ")[0], x + w_ / 2, y + h_ / 2 + 20, 64, "x", "#ffffff", 1, "c")
            P(c, t, t0 + .1, x + w_ / 2, y + h_ + 40, s.split("  ")[1], 24, "check")
        bgdock(c, 1)
    return cam, draw

def s40(T0, D):
    r = R(T0); ttp = r("tips")
    items = [(r("fast"), "Keep it fast: no dead air", True), (r("freeze"), "End on a freeze frame with 2 choices", True),
             (r("part"), "Make Part 2 from the winning comment", True), (r("thumbnail"), "Strong thumbnail with a question", True),
             (r("label"), "Turn on Instagram's AI info label", True), (r("own", 18), "Make your own characters + stories", True)]
    tcs = r("copy"); tnv = r("never")
    cam = Cam([(0, 960, 540, 1.0), (tcs - .3, 960, 500, 1.02), (tcs + .3, 960, 540, 1.0), (D, 960, 540, 1.03)])
    sfx(0, "whoosh", .7); sfx(ttp, "pop", .5); cues([i[0] for i in items], "ding", .4); sfx(tcs, "whoosh_s", .5); sfx(tnv, "pop", .6)
    def draw(c, t):
        bg(c, "Notes")
        ka = 1 - lin(t, tcs - .3, tcs)
        if ka > 0:
            c.saveLayerAlpha(None, int(255 * ka))
            ttl(c, t, ttp - .1, "TIPS FROM MY UPLOADS", 140, 76, YEL)
            checklist(c, t, 510, 210, items, 30, 106, 900)
            c.restore()
        k = wk(t, tcs, .4)
        if k > 0:
            big_title(c, "COPY A STYLE", 400, 120, k, GREEN)
            big_title(c, "NEVER SOMEONE'S CHARACTERS", 580, 84, wk(t, tnv - .1, .4), RED)
        bgdock(c, 0)
    return cam, draw

def s41(T0, D):
    r = R(T0); tsy = r("system"); tref = r("reference"); tsk = r("skill"); tid = r("ideas"); ted = r("editing"); tan = r("animation")
    twa = r("whatsapp"); tde = r("description"); ttag = r("tag"); tsub = r("subscribe"); tnx = r("next")
    cp = Path2([(0, 1500, 900), (tsub - .6, 1500, 900), (tsub - .05, 960, 790)])
    cam = drift(D, 1.0, 1.06)
    sfx(0, "whoosh", .7); sfx(tsy, "rise", .4); cues([tref, tsk, tid, ted, tan]); sfx(twa, "ding", .6); sfx(tde, "pop", .6); sfx(ttag, "pop", .5); sfx(tsub, "click", .8); sfx(tsub + .1, "ding", .5)
    def draw(c, t):
        bg(c, "aivxer")
        ka = 1 - lin(t, twa - .4, twa - .1)
        if ka > 0:
            c.saveLayerAlpha(None, int(255 * ka))
            ttl(c, t, tsy - .2, "THE WHOLE SYSTEM", 260, 110, "#ffffff")
            for i, (s, t0) in enumerate([("1 reference video", tref), ("+  the skill", tsk), ("+  your ideas", tid)]):
                P(c, t, t0, 480 + i * 480, 430, s, 38, "dot", [YEL, CORAL, GREEN][i])
            P(c, t, ted, 700, 600, "No editing software", 32, "cross", RED); P(c, t, tan, 1250, 600, "No animation experience", 32, "cross", RED)
            c.restore()
        if t > twa - .3:
            ttl(c, t, twa - .05, "GET THE SKILL + THE PROMPT", 220, 80, "#ffffff")
            k = wk(t, twa, .35)
            if k > 0:
                with Pop(c, 360, 340, 560, 150, k):
                    rrect(c, 360, 340, 560, 150, 30, "#128c4a"); rrect(c, 360, 340, 560, 60, 30, "#ffffff", .12)
                    text(c, "WhatsApp channel", 640, 432, 44, "x", "#ffffff", 1, "c")
            k = wk(t, tde, .35)
            if k > 0:
                with Pop(c, 1000, 340, 560, 150, k):
                    rrect(c, 1000, 340, 560, 150, 30, "#17171b"); rrect_stroke(c, 1000, 340, 560, 150, 30, "#ffffff", .3, 2)
                    text(c, "Link in description", 1280, 432, 44, "x", "#ffffff", 1, "c")
            P(c, t, ttag, W / 2, 600, "Made one? Tag me!", 34, "dot", YEL)
            k = wk(t, tsub - .5, .35)
            if k > 0:
                sub = t > tsub
                with Pop(c, 780, 740, 360, 100, k):
                    rrect(c, 780, 740, 360, 100, 50, "#ff0033" if not sub else "#3a3a3e")
                    text(c, "SUBSCRIBE" if not sub else "SUBSCRIBED", 960, 805, 36, "x", "#ffffff", 1, "c")
                x, y = cp.at(t); cursor(c, x, y, 1.1, 1 if abs(t - tsub) < .12 else 0); click_ring(c, x, y, lin(t, tsub, tsub + .4))
        bgdock(c, 0)
    return cam, draw, [], dict(fade_out=1.2)

# ---------------- scene list (cuts in the silences) ----------------
STARTS = [(10.50, s02), (18.15, s03), (29.83, s04), (36.90, s05), (51.37, s06), (63.24, s07), (74.89, s08), (93.83, s09), (106.47, s10),
          (117.25, s11), (122.25, s12), (134.57, s13), (148.58, s14), (155.21, s15), (174.76, s16), (182.98, s17), (200.77, s18), (206.66, s19),
          (225.00, s20), (233.77, s21), (239.30, s22), (249.19, s23), (263.69, s24), (281.19, s25), (300.84, s26), (322.53, s27), (333.06, s28),
          (350.09, s29), (370.02, s30), (381.38, s31), (398.82, s32), (412.58, s33), (418.89, s34), (437.61, s35), (447.91, s36), (456.81, s37),
          (470.79, s38), (479.24, s39), (499.85, s40), (526.44, s41)]
END = 546.84

def build_list(first_end):
    out = []; cuts = [first_end] + [cut_before(s) for s, _ in STARTS[1:]] + [END]
    for i, (s, fn) in enumerate(STARTS):
        out.append((fn.__name__, cuts[i], cuts[i + 1], fn))
    return out
