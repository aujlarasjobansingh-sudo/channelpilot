# Tutorial: "How I make these animated What-If videos with Claude" - aivxer tutorial editing style
from comps import *
import json, re

VO = "vo/vo48.wav"
OUT = "out/final.mp4"
MUSIC_DB = -30
EP = "/home/user/channelpilot/channel/ep01_2d/part2/out/ep01_part1_2_combined.mp4"
PREV1 = "/home/user/channelpilot/channel/ep01_2d/out/preview_2d_14s.mp4"
PREV2 = "/home/user/channelpilot/channel/ep01_2d/out/preview_2d_premium.mp4"
CHAT_HISTORY[:] = ["Faceless rules", "World bible", "EP01 part 1", "EP01 part 2"]

_WS = json.load(open(ROOT + "/vo/words.json"))
_N = [re.sub(r"[^a-z0-9]", "", w[0].lower()) for w in _WS]
def wt(phrase, after=0.0):
    ps = [re.sub(r"[^a-z0-9]", "", p.lower()) for p in phrase.split()]
    for i in range(len(_N)):
        if _WS[i][1] >= after - .01 and _N[i:i + len(ps)] == ps: return _WS[i][1]
    raise ValueError(phrase)
def L(phrase, T0): return wt(phrase, T0) - T0          # local time of a spoken phrase

CORAL, YEL, GRN, RED, BLUE, PUR = "#d97757", "#ffd23f", "#22c55e", "#ef4444", "#3b82f6", "#8b5cf6"
def popk(t, t0, d=.45): return back(lin(t, t0, t0 + d))
def win_pop(t, t0): return lin(t, t0, t0 + .25), mix(.9, 1, back(lin(t, t0, t0 + .45)))

def img_win(c, img, x, y, w, h, title, t, t0, fy=0.0):
    a, sc = win_pop(t, t0)
    window(c, x, y, w, h, title, a=a, sc=sc, content=lambda c2, X, Y, Wd, Hd: draw_img_cover(c2, img, X, Y, Wd, Hd, fy=fy))

def vid_win(c, v, x, y, w, h, title, t, t0, start_t=None, prog=None):
    a, sc = win_pop(t, t0)
    img = v.frame(max(0, (t - (t0 if start_t is None else start_t)) * FPS))
    vplayer(c, x, y, w, h, img, title, prog if prog is not None else clamp((t - t0) / 12), a=a, sc=sc)

def step_title(c, t, n, name, t0, color=CORAL):
    k = popk(t, t0)
    if k <= 0: return
    pill(c, W / 2, 380, f"STEP {n}", 30, k=k, bgc=color, align="c")
    big_title(c, name, 560, 150, popk(t, t0 + .15))

# ======================================================================= scenes
def s01(T0, D):   # Look at this channel ... 2.5M views in 7 days
    img = IMG("doomperk_1.png")
    t1, t2, t3 = L("its called", T0), L("it has just", T0), L("but in the", T0)
    sfx(0, "whoosh"); sfx(.1, "pop"); sfx(t1, "ding", .6); sfx(t2 + .3, "pop"); sfx(t2 + 1.6, "pop"); sfx(t3 + 1.2, "rise", .7); sfx(t3 + 2.6, "ding")
    cam = Cam([(0, 960, 520, 1.0), (t1, 960, 520, 1.0), (t1 + .6, 620, 380, 1.45), (t3, 620, 380, 1.45), (t3 + .7, 760, 520, 1.25), (D, 760, 520, 1.3)])
    def draw(c, t):
        bg(c, "Browser")
        img_win(c, img, 160, 70, 1600, 880, "youtube.com/@DOOMPERK", t, 0)
        pill(c, 190, 120, "THEIR CHANNEL", 22, k=popk(t, .3), icon="dot", icol=RED, bgc="#111114")
        ann_circle(c, 560, 375, 120, lin(t, t1, t1 + .5))
        if t > t2: pill(c, 760, 470, "42 videos", 26, k=popk(t, t2 + .3), bgc="#141418")
        if t > t2: pill(c, 760, 530, "25.7K subscribers", 26, k=popk(t, t2 + 1.6), bgc="#141418")
        if t > t3:
            ann_circle(c, 470, 570, 90, lin(t, t3 + 1.0, t3 + 1.6), YEL)
            ann_label(c, "+2.61M views in 7 days", 330, 680, popk(t, t3 + 2.4), YEL, 34)
        dock(c, 2)
    return cam, draw

def s02(T0, D):   # three videos and their views
    img = IMG("doomperk_2.png")
    a1, a2, a3 = L("what if you", T0), L("infinite iq in prison", T0), L("infinite iq in the army", T0)
    v1, v2, v3 = L("17", T0) if False else L("1.7", T0) if False else a1 + 2.8, L("15", T0) if False else a2 + 1.6, a3 + 1.4
    for x in (a1, a2, a3): sfx(x, "whoosh_s")
    for x in (v1, v2, v3): sfx(x, "ding", .7)
    # screenshot is drawn into a 1600x880 window: thumbnails sit roughly at x 200-560, 640-1000, 1080-1440 (window coords)
    cam = Cam([(0, 960, 520, 1.0), (a1, 960, 520, 1.0), (a1 + .5, 520, 330, 1.7), (a2, 520, 330, 1.7), (a2 + .5, 960, 330, 1.7),
               (a3, 960, 330, 1.7), (a3 + .5, 1390, 330, 1.7), (D - .6, 1390, 330, 1.7), (D, 960, 520, 1.1)])
    def draw(c, t):
        bg(c, "Browser")
        img_win(c, img, 160, 70, 1600, 880, "youtube.com/@DOOMPERK/videos", t, -1)
        pill(c, 190, 120, "THEIR VIDEOS", 22, k=1, icon="dot", icol=RED, bgc="#111114")
        for (x, tv, s) in ((520, v1, "1.7M views"), (960, v2, "1.5M views"), (1390, v3, "700K views")):
            if t > tv: pill(c, x, 470, s, 34, k=popk(t, tv), bgc="#141418", icon="dot", icol=YEL, align="c")
        dock(c, 2)
    return cam, draw

def s03(T0, D):   # no face, no studio, no voice actor - 3D animation + what-if story
    ts = [L("no face", T0), L("no studio", T0), L("no voice", T0)]; tt = L("3d", T0) if False else L("animation and", T0) - .4
    sfx(0, "whoosh")
    for x in ts: sfx(x, "pop")
    sfx(tt, "rise", .6); sfx(tt + .5, "ding")
    def draw(c, t):
        bg(c, "Desktop")
        for i, (lab, x0) in enumerate(zip(("No face", "No studio", "No voice actor"), ts)):
            pill(c, W / 2, 250 + i * 110, lab, 40, k=popk(t, x0), icon="cross", icol=RED, align="c")
        if t > tt:
            big_title(c, "3D ANIMATION", 720, 120, popk(t, tt), YEL, sub="+ a \"What if\" story", subk=lin(t, tt + .4, tt + .8))
        dock(c)
    return drift(D, 1.0, 1.06), draw

def s04(T0, D):   # Now look at this. I made this myself. No animator... just AI
    v = Vid(EP, 2.0, 1280, 720)
    t1 = L("i made", T0); tn = [L("no animator", T0), L("no studio", T0), L("no after", T0)]; ta = L("just ai", T0)
    sfx(0, "whoosh"); sfx(.15, "pop"); sfx(t1, "ding", .6)
    for x in tn: sfx(x, "pop")
    sfx(ta, "ding")
    def draw(c, t):
        bg(c, "Player")
        vid_win(c, v, 140, 120, 1100, 660, "my_video.mp4", t, 0)
        pill(c, 170, 170, "MY VIDEO", 24, k=popk(t, t1), icon="dot", icol=CORAL, bgc="#111114")
        for i, (lab, x0) in enumerate(zip(("No animator", "No studio", "No After Effects"), tn)):
            pill(c, 1300, 260 + i * 100, lab, 32, k=popk(t, x0), icon="cross", icol=RED)
        if t > ta: pill(c, 1300, 600, "Just AI", 40, k=popk(t, ta), icon="check", icol=GRN, bgc="#14532d")
        dock(c, 0)
    return drift(D, 1.0, 1.04), draw, [v]

def s05(T0, D):   # searched YouTube, couldn't find one; revealing my entire process
    q = "how to make 3D animation like this"
    tq = .3; tn = L("and i couldnt", T0); tr = L("so today", T0)
    type_sfx(tq, q, 30); sfx(0, "whoosh"); sfx(tn, "pop"); sfx(tr, "whoosh"); sfx(tr + .2, "rise", .6)
    def draw(c, t):
        bg(c, "Browser")
        def f(c2, x, y, w, h):
            rrect(c2, x, y, w, h, 0, "#0f0f12")
            rrect(c2, x + 160, y + 40, w - 320, 60, 30, "#1f1f24"); rrect_stroke(c2, x + 160, y + 40, w - 320, 60, 30, "#ffffff", .12)
            s, car = typed(q, t, tq, 30); text(c2, s + ("|" if car and int(t * 3) % 2 == 0 else ""), x + 200, y + 80, 24, "m", "#ffffff")
            for i in range(4):
                k = lin(t, tq + 1.4 + i * .15, tq + 1.7 + i * .15)
                if k > 0:
                    rrect(c2, x + 160, y + 140 + i * 130, 260, 110, 10, "#26262c", k); rrect(c2, x + 440, y + 150 + i * 130, 500, 22, 6, "#2e2e35", k)
                    rrect(c2, x + 440, y + 186 + i * 130, 320, 16, 6, "#26262c", k)
                    if t > tn: cross(c2, x + 1000, y + 195 + i * 130, 20)
        a, sc = win_pop(t, 0)
        window(c, 200, 80, 1520, 760, "YouTube search", a=a, sc=sc, content=f)
        if t > tn: ann_label(c, "No real tutorial", 1240, 300, popk(t, tn + .2), RED, 32)
        if t > tr:
            c.drawPaint(paint(col("#000000", .55 * lin(t, tr, tr + .3))))
            big_title(c, "FULL PROCESS", 500, 140, popk(t, tr + .1), "#ffffff", sub="from the first idea to the final video", subk=lin(t, tr + .8, tr + 1.2))
        dock(c, 2)
    return drift(D, 1.0, 1.05), draw

def s06(T0, D):   # giving it all away for free: skill, prompts, everything
    tf = 0; ts, tp, te = L("the exact skill", T0), L("the prompts", T0), L("everything", T0); ty = L("youll be able", T0)
    sfx(0, "whoosh"); sfx(.2, "ding")
    for x in (ts, tp, te): sfx(x, "pop")
    sfx(ty, "ding", .6)
    def draw(c, t):
        bg(c, "Desktop")
        big_title(c, "100% FREE", 260, 130, popk(t, .1), GRN)
        for i, (lab, sub, x0, cc) in enumerate((("skill.zip", "the exact skill", ts, CORAL), ("prompts.txt", "every prompt", tp, BLUE), ("everything", "the full process", te, PUR))):
            k = popk(t, x0)
            if k <= 0: continue
            x = 330 + i * 450
            with Pop(c, x, 380, 360, 300, k):
                panel(c, x, 380, 360, 300); rrect(c, x + 130, 420, 100, 120, 14, cc)
                text(c, lab, x + 180, 600, 30, "b", "#ffffff", 1, "c"); text(c, sub, x + 180, 640, 22, "m", "#d4d4d8", 1, "c")
        if t > ty: pill(c, W / 2, 760, "Make a video like this today", 32, k=popk(t, ty), icon="check", icol=GRN, align="c")
        dock(c)
    return drift(D, 1.0, 1.05), draw

def s07(T0, D):   # stay to the end: the mistake
    tm = L("the one mistake", T0); te = L("its a mistake", T0); tf = L("your video will", T0)
    sfx(0, "whoosh"); sfx(tm, "rise", .6); sfx(tm + .6, "pop"); sfx(te, "pop"); sfx(tf, "whoosh_s")
    def draw(c, t):
        bg(c, "Player")
        prog = clamp(t / D * .9)
        x0, x1, y = 260, 1660, 520
        rrect(c, x0, y, x1 - x0, 16, 8, "#ffffff", .25); rrect(c, x0, y, (x1 - x0) * prog, 16, 8, "#ff0033")
        c.drawCircle(x0 + (x1 - x0) * prog, y + 8, 14, paint(col("#ffffff")))
        if t > tm:
            mx = x0 + (x1 - x0) * .86; k = popk(t, tm + .6)
            c.drawCircle(mx, y + 8, 18 * k, paint(col(RED)))
            ann_label(c, "THE MISTAKE", mx - 140, y - 60, k, RED, 40)
        big_title(c, "WATCH TILL THE END", 330, 96, popk(t, .1))
        if t > te: pill(c, W / 2, 680, "Almost everyone makes it", 32, k=popk(t, te), icon="dot", icol=YEL, align="c")
        if t > tf:
            sh = math.sin(t * 50) * 8 * (1 - lin(t, tf + .5, tf + 1.5))
            c.save(); c.translate(sh, 0); pill(c, W / 2, 780, "Your video falls apart", 32, k=popk(t, tf), icon="cross", icol=RED, align="c"); c.restore()
        dock(c, 0)
    return drift(D, 1.0, 1.04), draw

def s08(T0, D):   # five steps
    names = ["Topic", "Script", "Voiceover", "Animation", "Final edit"]
    ts = [L("topic", T0), L("script", T0), L("voiceover", T0), L("animation", T0), L("and the final", T0) + .3]; tc = L("using", T0)
    sfx(0, "whoosh")
    for x in ts: sfx(x, "pop")
    sfx(tc, "ding")
    def draw(c, t):
        bg(c, "Desktop")
        big_title(c, "5 STEPS", 260, 110, popk(t, 0))
        for i, (n, x0) in enumerate(zip(names, ts)):
            k = popk(t, x0)
            if k <= 0: continue
            x = 200 + i * 320
            with Pop(c, x, 420, 260, 220, k):
                panel(c, x, 420, 260, 220); c.drawCircle(x + 130, 490, 38, paint(col(CORAL)))
                text(c, str(i + 1), x + 130, 504, 40, "x", "#ffffff", 1, "c"); text(c, n, x + 130, 600, 30, "b", "#ffffff", 1, "c")
            if i and t > x0: c.drawLine(x - 60, 530, x - 10, 530, paint(col("#ffffff", .5), style="stroke", sw=4))
        if t > tc: pill(c, W / 2, 760, "all with Claude", 36, k=popk(t, tc), icon="dot", icol=CORAL, align="c")
        dock(c)
    return drift(D, 1.0, 1.04), draw

def s09(T0, D):   # Step 1 topic: YouTube rules
    tc = L("before anything", T0); ti = L("in 2026", T0)
    msg = "Read YouTube's current rules for faceless channels."
    sfx(0, "whoosh"); sfx(.3, "pop"); type_sfx(tc + .3, msg, 32); sfx(tc + 2.2, "click")
    items = [("Inauthentic content = no monetization", ti + .3, ti + 1.0), ("Low-effort / mass-produced is out", ti + 2.4, ti + 3.0), ("Original stories with real value", ti + 4.6, ti + 5.2)]
    for _, td, t1 in items: sfx(t1, "pop", .6); sfx(td, "ding", .5)
    def draw(c, t):
        bg(c, "Claude")
        if t < tc - .1: step_title(c, t, 1, "TOPIC", 0)
        else:
            inp, car = typed(msg, t, tc + .3, 32)
            sent = t > tc + 2.2
            msgs = [dict(role="user", text=msg, t0=tc + 2.2)] if sent else []
            if sent: msgs.append(dict(role="ai", text="Here's what matters for faceless channels in 2026:", t0=ti, items=items))
            chat_window(c, 180, 70, 1560, 860, t, msgs, inp="" if sent else inp, inp_caret=car)
        dock(c, 1)
    return drift(D, 1.0, 1.04), draw

def s10(T0, D):   # how I picked the topic
    steps = [("Viral \"In this town\" videos", L("i kept seeing", T0)), ("A new world every week", L("and i thought", T0)),
             ("Monsters, heroes, rankings", L("a world with", T0)), ("You're the weakest alive", L("where youre", T0))]
    te = L("thats how", T0)
    sfx(0, "whoosh")
    for _, x in steps: sfx(x, "pop")
    sfx(te, "ding")
    v = Vid(EP, 1.0, 960, 540)
    def draw(c, t):
        bg(c, "Notes")
        def f(c2, x, y, w, h):
            rrect(c2, x, y, w, h, 0, "#1c1c20"); text(c2, "Channel idea", x + 40, y + 70, 36, "x", YEL)
            for i, (s, x0) in enumerate(steps):
                k = eout(lin(t, x0, x0 + .3))
                if k <= 0: continue
                yy = y + 150 + i * 90
                c2.saveLayerAlpha(None, int(255 * k)); check(c2, x + 60, yy - 8, 16, GRN, k); text(c2, s, x + 95, yy, 30, "s", "#ffffff"); c2.restore()
                if i: text(c2, "↓", x + 52, yy - 50, 22, "b", "#71717a")
        a, sc = win_pop(t, 0); window(c, 160, 90, 900, 700, "Notes - idea.md", a=a, sc=sc, content=f)
        if t > te:
            vid_win(c, v, 1000, 300, 800, 450, "EP01.mp4", t, te)
            pill(c, 1400, 830, "What Happens If You Become the Weakest Hero Alive?", 22, k=popk(t, te + .3), bgc="#141418", align="c")
        dock(c, 5)
    return drift(D, 1.0, 1.04), draw, [v]

def s11(T0, D):   # original story, copyright safe, pick a topic
    tc, to, ts, tp = L("i didnt copy", T0), L("the world has", T0), L("that keeps you", T0), L("pick a topic", T0)
    sfx(0, "whoosh"); sfx(tc, "pop"); sfx(to + .3, "pop"); sfx(ts, "ding"); sfx(tp, "rise", .6)
    def draw(c, t):
        bg(c, "Desktop")
        big_title(c, "ONE IMPORTANT THING", 220, 80, popk(t, .05), YEL)
        if t > tc:
            with Pop(c, 220, 320, 680, 360, popk(t, tc)):
                panel(c, 220, 320, 680, 360); cross(c, 290, 390, 26); text(c, "Copy an anime plot", 340, 402, 34, "b", "#ffffff")
                for i, s in enumerate(("same story", "same names", "same powers")): text(c, "- " + s, 290, 480 + i * 56, 28, "m", "#a1a1aa")
        if t > to:
            with Pop(c, 1020, 320, 680, 360, popk(t, to + .3)):
                panel(c, 1020, 320, 680, 360); check(c, 1090, 390, 26); text(c, "Your own world", 1140, 402, 34, "b", "#ffffff")
                for i, s in enumerate(("anime FEEL only", "own story + names", "own ranks + monsters")):
                    if t > to + .8 + i * .7: text(c, "- " + s, 1090, 480 + i * 56, 28, "m", "#d4d4d8")
        if t > ts: pill(c, W / 2, 760, "Copyright safe", 34, k=popk(t, ts), icon="check", icol=GRN, bgc="#14532d", align="c")
        if t > tp:
            c.drawPaint(paint(col("#000000", .55 * lin(t, tp, tp + .3))))
            big_title(c, "PICK A TOPIC YOU'D WATCH", 540, 90, popk(t, tp + .1))
        dock(c)
    return drift(D, 1.0, 1.04), draw

def s12(T0, D):   # Step 2 script rules
    tr = L("i gave claude", T0)
    rules = [("Open with a \"What happens if you...\" hook", L("open with", T0)), ("Subscribe right after the hook", L("ask viewers to subscribe", T0)),
             ("Explain the world early", L("explain how", T0)), ("Full story in my own style", L("tell the full", T0)), ("Ask which world is next", L("and at the end", T0))]
    sfx(0, "whoosh"); sfx(tr, "pop")
    for _, x in rules: sfx(x, "pop", .7); sfx(x + .5, "ding", .4)
    def draw(c, t):
        bg(c, "Claude")
        if t < tr - .05: step_title(c, t, 2, "SCRIPT", 0)
        else:
            items = [(s, x + .5, x) for s, x in rules]
            msgs = [dict(role="user", text="Write my script with these rules:", t0=tr), dict(role="ai", text="Got it. Script rules:", t0=tr + .5, items=items)]
            chat_window(c, 180, 70, 1560, 860, t, msgs)
        dock(c, 1)
    return drift(D, 1.0, 1.05), draw

def s13(T0, D):   # world bible
    lines = ["# WORLD BIBLE", "", "city: 'Meridian City'", "ranks: ['Iron', 'Bronze', 'Silver', 'Gold', 'Crown']", "score: 'Spark Score 0-1000'",
             "threats: ['Ember', 'Storm', 'Quake', 'Eclipse', 'Extinction']", "hero: 'The Zero - weakest hero alive'", "", "narration: '20-30 min, in parts'"]
    tb = L("claude started", T0); tc = L("the city", T0); tn = L("then it wrote", T0); tp = L("the exact prompt", T0)
    total = sum(len(s) for s in lines)
    sfx(0, "whoosh"); type_sfx(tc, "x" * 120, 40, 4, .6); sfx(tn, "pop"); sfx(tp, "ding")
    ranks = ["Iron", "Bronze", "Silver", "Gold", "Crown"]; rc = ["#8a90a0", "#d08a4a", "#d4dae6", "#f6cf5a", "#ffe88a"]
    def draw(c, t):
        bg(c, "Code")
        rv = int(max(0, t - tc) / max(.1, tn - tc) * total) if t < tn else None
        a, sc = win_pop(t, 0)
        code_window(c, 140, 80, 1100, 760, lines, title="world_bible.md", reveal=rv, size=24, a=a, sc=sc)
        for i, (r, cc) in enumerate(zip(ranks, rc)):
            k = popk(t, tc + 1.2 + i * .35)
            if k > 0: pill(c, 1300, 140 + i * 90, r, 30, k=k, icon="dot", icol=cc)
        if t > tn: pill(c, 1300, 640, "20-30 min narration", 30, k=popk(t, tn), icon="check", icol=GRN)
        if t > tp: pill(c, 1300, 730, "Prompt in description", 30, k=popk(t, tp), icon="dot", icol=YEL)
        dock(c, 3)
    return drift(D, 1.0, 1.04), draw

def s14(T0, D):   # pro tip: split under 5000 chars
    tt = L("ask it to split", T0); te = L("thats how much", T0)
    parts = [("part_01.txt", "4,984"), ("part_02.txt", "4,870"), ("part_03.txt", "4,947"), ("part_04.txt", "1,651")]
    sfx(0, "whoosh"); sfx(.1, "ding", .6)
    for i in range(4): sfx(tt + .6 + i * .3, "pop")
    sfx(te, "pop")
    def draw(c, t):
        bg(c, "Finder")
        big_title(c, "PRO TIP", 210, 90, popk(t, .05), YEL)
        for i, (n, ch) in enumerate(parts):
            k = popk(t, tt + .6 + i * .3)
            if k <= 0: continue
            x = 260 + i * 360
            with Pop(c, x, 360, 300, 320, k):
                panel(c, x, 360, 300, 320); rrect(c, x + 100, 400, 100, 130, 10, "#e4e4e7")
                for q in range(5): rrect(c, x + 115, 425 + q * 20, 70, 6, 3, "#a1a1aa")
                text(c, n, x + 150, 580, 26, "b", "#ffffff", 1, "c"); text(c, ch + " chars", x + 150, 625, 24, "m", GRN, 1, "c")
        if t > tt: pill(c, W / 2, 300, "under 5,000 characters each", 30, k=popk(t, tt), icon="check", icol=GRN, align="c")
        if t > te: pill(c, W / 2, 760, "= one voice generation per part", 30, k=popk(t, te), icon="dot", icol=BLUE, align="c")
        dock(c, 0)
    return drift(D, 1.0, 1.04), draw

def s15(T0, D):   # Step 3 voiceover
    tu = L("i used", T0); tv = L("for storytelling", T0); tg = L("generate each", T0); tw_ = L("one warning", T0)
    sfx(0, "whoosh"); sfx(tu, "pop"); sfx(tv + .4, "click"); sfx(tg + .2, "click"); sfx(tg + 1.4, "ding"); sfx(tw_, "pop")
    def draw(c, t):
        bg(c, "Voice Studio")
        if t < tu - .05: step_title(c, t, 3, "VOICEOVER", 0)
        else:
            def f(c2, x, y, w, h):
                rrect(c2, x, y, w, h, 0, "#121216"); text(c2, "Voice", x + 40, y + 60, 22, "s", "#a1a1aa")
                rrect(c2, x + 40, y + 80, 420, 64, 12, "#1f1f26"); text(c2, "Deep · Calm · English", x + 64, y + 122, 24, "s", "#ffffff")
                if t > tv: ann_circle(c2, x + 250, y + 112, 130, lin(t, tv, tv + .5), YEL)
                rrect(c2, x + 40, y + 180, w - 80, 180, 12, "#1f1f26")
                for i, s in enumerate(("Everyone calls you the weakest hero alive.", "Your own rank card says it. The news says it...")):
                    text(c2, s, x + 64, y + 230 + i * 40, 22, "m", "#d4d4d8")
                bk = 1 - .1 * clamp(1 - abs(t - tg - .2) * 8)
                rrect(c2, x + 40, y + 390, 220 * bk, 60, 30, CORAL); text(c2, "Generate", x + 150, y + 428, 24, "b", "#ffffff", 1, "c")
                if t > tg + .4:
                    for i in range(90):
                        e = env_at(T0 + t - 1 + i / 30); hh = 6 + 70 * e * clamp((t - tg - .4) * 2 - i / 90)
                        rrect(c2, x + 300 + i * 9, y + 420 - hh / 2, 5, hh, 2, CORAL)
                if t > tg + 1.4:
                    for i in range(4):
                        k = eout(lin(t, tg + 1.4 + i * .2, tg + 1.7 + i * .2))
                        if k > 0: text(c2, f"part_0{i + 1}.mp3   ✓", x + 64, y + 510 + i * 34, 22, "m", "#86efac", k)
            a, sc = win_pop(t, tu)
            window(c, 260, 80, 1400, 760, "Voice studio", a=a, sc=sc, content=f)
            if t > tw_: pill(c, W / 2, 900 - 40, "Monetizing? Use a paid plan", 30, k=popk(t, tw_), icon="dot", icol=RED, align="c")
        dock(c, 5)
    return drift(D, 1.0, 1.04), draw

def s16(T0, D):   # Step 4 animation: install skill, what it knows
    tm = L("made with", T0); tf = L("first download", T0); tk = L("now claude knows", T0)
    feats = [("Characters", L("characters", T0)), ("Thick outlines", L("the thick", T0)), ("Moody lighting", L("the moody", T0)), ("Moving camera", L("and a camera", T0))]
    menu = ["Customize", "Skills", "+", "Upload a skill"]
    sfx(0, "whoosh"); sfx(.2, "rise", .6); sfx(tm, "pop")
    for i in range(4): sfx(tf + .6 + i * .55, "click")
    sfx(tf + 3.0, "ding")
    for _, x in feats: sfx(x, "pop", .7)
    v = Vid(EP, 4.0, 960, 540)
    cur = Path2([(tf, 900, 700), (tf + .5, 330, 230), (tf + 1.05, 330, 300), (tf + 1.6, 1000, 230), (tf + 2.15, 1000, 330), (tf + 2.8, 860, 560)])
    def draw(c, t):
        bg(c, "Claude")
        if t < tf - .05:
            step_title(c, t, 4, "ANIMATION", 0)
            if t > tm: pill(c, W / 2, 760, "made with Claude", 34, k=popk(t, tm), icon="dot", icol=CORAL, align="c")
        elif t < tk - .05:
            def f(c2, x, y, w, h):
                rrect(c2, x, y, w, h, 0, "#1f1f1d"); rrect(c2, x, y, 300, h, 0, "#191917")
                for i, s in enumerate(("General", "Customize", "Connectors", "Privacy")):
                    on = s == "Customize" and t > tf + .6
                    if on: rrect(c2, x + 14, y + 40 + i * 54, 272, 44, 8, "#33332f")
                    text(c2, s, x + 34, y + 70 + i * 54, 22, "s" if on else "m", "#ffffff" if on else "#a8a69e")
                if t > tf + 1.15:
                    text(c2, "Skills", x + 360, y + 80, 30, "b", "#ffffff"); rrect(c2, x + 780, y + 50, 44, 44, 10, CORAL); text(c2, "+", x + 802, y + 82, 30, "b", "#ffffff", 1, "c")
                if t > tf + 2.2:
                    rrect(c2, x + 600, y + 110, 280, 56, 10, "#33332f"); text(c2, "Upload a skill", x + 624, y + 146, 22, "s", "#ffffff")
                if t > tf + 2.8:
                    k = eout(lin(t, tf + 2.8, tf + 3.2))
                    rrect(c2, x + 360, y + 220, 520, 90, 12, "#14532d", k); check(c2, x + 400, y + 265, 16, GRN)
                    text(c2, "2d-animation skill  ·  installed", x + 430, y + 274, 24, "s", "#ffffff", k)
            a, sc = win_pop(t, tf)
            window(c, 260, 120, 1400, 640, "Claude - Settings", a=a, sc=sc, content=f)
            x, y = cur.at(t); pr = clamp(1 - min(abs(t - (tf + .6 + i * .55)) for i in range(4)) * 8)
            cursor(c, x, y, 1, pr)
            for i in range(4): click_ring(c, x, y, lin(t, tf + .6 + i * .55, tf + .95 + i * .55))
            pill(c, W / 2, 850, "check the real menu path in your Claude app", 20, k=popk(t, tf + .3), icon="dot", icol=YEL, align="c")
        else:
            vid_win(c, v, 160, 160, 960, 540, "style.mp4", t, tk)
            for i, (s, x0) in enumerate(feats): pill(c, 1200, 220 + i * 110, s, 34, k=popk(t, x0), icon="check", icol=GRN)
        dock(c, 1)
    return drift(D, 1.0, 1.04), draw, [v]

def s17(T0, D):   # reference + prompt; 10s preview first
    msg = "Make animation in this style. I want movement in every scene, and it should feel premium."
    ts = L("next show", T0); tm = L("make animation", T0); tn = L("dont ask", T0); tp = L("ask for a", T0)
    ref = IMG("doomperk_2.png")
    sfx(0, "whoosh"); sfx(ts + .8, "pop"); type_sfx(tm, msg, 34); sfx(tn, "pop"); sfx(tp, "pop"); sfx(tp + .4, "ding")
    def draw(c, t):
        bg(c, "Claude")
        inp, car = typed(msg, t, tm, 34)
        msgs = [dict(role="user", text="Here's the look I want:", t0=ts + .8, attach=ref, attach_name="reference.png")]
        chat_window(c, 180, 70, 1560, 860, t, msgs, inp=inp, inp_caret=car)
        if t > tn: pill(c, 1260, 300, "Full video right away", 30, k=popk(t, tn), icon="cross", icol=RED)
        if t > tp: pill(c, 1260, 380, "10-second preview first", 30, k=popk(t, tp), icon="check", icol=GRN, bgc="#14532d")
        dock(c, 1)
    return drift(D, 1.0, 1.04), draw

def s18(T0, D):   # first preview -> make it premium -> difference
    tf = L("my first preview", T0); ts = L("so i told", T0); td = L("and look at", T0)
    tb, ti, tg = L("the blanket", T0), L("the punches", T0), L("and everything", T0)
    asks = ["Make it more premium.", "Make the characters look better.", "If someone is sleeping, it should look good.", "Make the fight scenes look good."]
    at = [L("make it more", T0), L("make the characters", T0), L("if someone", T0), L("make the fight", T0)]
    v1 = Vid(PREV1, 0.0, 800, 450); v2 = Vid(PREV2, 0.0, 800, 450); v1b = Vid(PREV1, 0.0, 800, 450)
    sfx(0, "whoosh"); sfx(tf, "pop")
    for x in at: sfx(x, "pop", .6)
    sfx(td, "whoosh"); sfx(td + .3, "rise", .5)
    for x in (tb, ti, tg): sfx(x, "ding", .5)
    cam = Cam([(0, 960, 540, 1.0), (td, 960, 540, 1.0), (tb, 960, 540, 1.0), (tb + .4, 1400, 420, 1.35), (D, 1400, 420, 1.4)])
    def draw(c, t):
        bg(c, "Player")
        if t < td:
            vid_win(c, v1, 160, 200, 800, 450, "preview_v1.mp4", t, 0)
            if t > tf + 1.2: pill(c, 560, 740, "fine... but not premium", 28, k=popk(t, tf + 1.2), icon="dot", icol=YEL, align="c")
            for i, (s, x0) in enumerate(zip(asks, at)):
                if t > x0: pill(c, 1040, 260 + i * 100, s, 26, k=popk(t, x0), icon="dot", icol=CORAL)
        else:
            vid_win(c, v1b, 120, 260, 820, 461, "BEFORE", t, td, start_t=td - 1.0)
            vid_win(c, v2, 980, 260, 820, 461, "AFTER - premium", t, td, start_t=td - 1.0)
            pill(c, 530, 790, "before", 28, k=popk(t, td + .2), icon="cross", icol=RED, align="c")
            pill(c, 1390, 790, "after", 28, k=popk(t, td + .2), icon="check", icol=GRN, align="c")
            for i, (s, x0) in enumerate((("breathing blanket", tb), ("real impact frames", ti), ("soft film grain", tg))):
                if t > x0: ann_label(c, s, 1040, 330 + i * 60, popk(t, x0), YEL, 26)
        dock(c, 0)
    return cam, draw, [v1, v2, v1b]

def s19(T0, D):   # upload voiceover, ~100 shots, part two
    tu = L("once youre", T0); tc = L("claude creates", T0); th = L("my first part", T0); tn = L("when you have", T0)
    m2 = "Make part two and join it to part one. Don't remake part one."
    tm2 = L("make part two", T0)
    sfx(0, "whoosh"); sfx(tu + 1.6, "pop"); sfx(tc, "pop"); sfx(th, "ding"); sfx(tm2 - .3, "pop")
    items = [("Transcribe voiceover (word timestamps)", tc - .6, tc - 1.0), ("One scene per sentence", tc + .8, tc + .2), ("~100 shots rendered", th + 1.4, th + .2)]
    def draw(c, t):
        bg(c, "Claude")
        msgs = [dict(role="user", text="Here's my voiceover. Make the full part 1.", t0=tu + 1.6)]
        if t > tc - 1.0: msgs.append(dict(role="ai", text="Building part 1:", t0=tc - 1.0, items=items))
        if t > tm2 - .3: msgs.append(dict(role="user", text=m2, t0=tm2 - .3))
        chat_window(c, 180, 70, 1560, 860, t, msgs)
        if t > th:
            n = int(clamp((t - th) / 1.4) * 100)
            panel(c, 1400, 180, 300, 150); text(c, f"{n}", 1550, 280, 80, "d", CORAL, 1, "c"); text(c, "shots", 1550, 315, 22, "m", "#d4d4d8", 1, "c")
        dock(c, 1)
    return drift(D, 1.0, 1.04), draw

def s20(T0, D):   # that's it / here's the result
    tr = L("heres the result", T0)
    sfx(0, "whoosh"); sfx(.2, "ding"); sfx(tr, "rise", .6)
    def draw(c, t):
        bg(c, "Desktop")
        check(c, W / 2, 380, 70 * popk(t, .1), GRN, lin(t, .2, .6))
        big_title(c, "FULL EPISODE READY", 600, 110, popk(t, .3))
        if t > tr: pill(c, W / 2, 760, "here's the result", 34, k=popk(t, tr), icon="dot", icol=CORAL, align="c")
        dock(c)
    return drift(D, 1.0, 1.06), draw

def s21(T0, D):   # all generated by AI
    tn = L("no drawing", T0)
    sfx(0, "whoosh"); sfx(.2, "ding"); sfx(tn, "pop"); sfx(tn + .6, "pop")
    def draw(c, t):
        bg(c, "Desktop")
        c.drawPaint(paint(col("#000000", .45)))
        big_title(c, "100% AI GENERATED", 400, 120, popk(t, .05), "#ffffff")
        pill(c, 760, 620, "No drawing", 34, k=popk(t, tn), icon="cross", icol=RED, align="c")
        pill(c, 1160, 620, "No animator", 34, k=popk(t, tn + .6), icon="cross", icol=RED, align="c")
        dock(c)
    return drift(D, 1.0, 1.05), draw

def timeline(c, t, t0, x0, y0, w, shift, label_ok=False):
    panel(c, x0 - 40, y0 - 80, w + 80, 380)
    text(c, "VOICE", x0, y0 - 30, 22, "b", "#a1a1aa"); text(c, "VIDEO", x0, y0 + 150, 22, "b", "#a1a1aa")
    for i in range(160):
        e = env_at(250 + i / 12); hh = 8 + 70 * e
        rrect(c, x0 + i * (w / 160), y0 + 50 - hh / 2, w / 160 * .6, hh, 2, BLUE)
    mx = x0 + w * .3
    c.drawLine(mx, y0 - 10, mx, y0 + 260, paint(col(YEL), style="stroke", sw=3))
    pill(c, mx - 20, y0 - 70, "\"the floor explodes\"", 22, k=1, bgc="#141418")
    bx = mx + shift
    rrect(c, bx, y0 + 170, 260, 70, 10, RED if shift > 5 else GRN); text(c, "EXPLOSION", bx + 130, y0 + 214, 24, "b", "#ffffff", 1, "c")
    if shift > 5:
        c.drawLine(mx, y0 + 205, bx, y0 + 205, paint(col(RED), style="stroke", sw=4))
        text(c, "7 s late", (mx + bx) / 2, y0 + 160, 30, "x", RED, 1, "c")

def s22(T0, D):   # the mistake: 7 seconds late
    tv = L("in my first version", T0); tg = L("in one spot", T0); tn = L("the narrator", T0); tb = L("the whole video", T0)
    sfx(0, "whoosh"); sfx(.2, "rise", .5); sfx(tg, "pop"); sfx(tn + 2.5, "whoosh_s"); sfx(tb, "pop")
    vx = Vid(EP, 250.4, 640, 360)
    def draw(c, t):
        bg(c, "Editor"); c.drawPaint(paint(col("#000000", .45)))
        if t < tv - .05: big_title(c, "THE MISTAKE", 540, 150, popk(t, 0), YEL)
        else:
            shift = 560 * clamp(lin(t, tv + .5, tv + 1.5))
            timeline(c, t, tv, 260, 300, 1400, shift)
            if t > tg: pill(c, W / 2, 760, "7 seconds out of sync", 32, k=popk(t, tg), icon="cross", icol=RED, align="c")
            if t > tb:
                sh = math.sin(t * 60) * 10 * (1 - lin(t, tb + .4, tb + 1.2))
                c.save(); c.translate(sh, 0); big_title(c, "BROKEN", 180, 90, popk(t, tb), "#ffffff"); c.restore()
        dock(c, 3)
    return drift(D, 1.0, 1.03), draw, [vx]

def s23(T0, D):   # the fix
    tr = L("the reason", T0); tf = L("the fix is", T0); tb = L("before the animation", T0); tt = L("then ask", T0); tm = L("remember those", T0)
    p1 = "Transcribe my voiceover with word timestamps, and start every scene on the first word of its sentence."
    p2 = "Pull one frame from every sentence and check it matches what the voice is saying."
    sfx(0, "whoosh"); sfx(tr, "pop"); sfx(tf, "ding"); type_sfx(tb, p1, 40); sfx(tb + 3.6, "click"); type_sfx(tt, p2, 40); sfx(tt + 3.0, "click"); sfx(tm, "rise", .6); sfx(tm + .4, "ding")
    def draw(c, t):
        bg(c, "Claude")
        if t < tf:
            pill(c, W / 2, 420, "Scenes timed by GUESSING from pauses", 34, k=popk(t, tr), icon="cross", icol=RED, align="c")
        elif t < tm:
            inp, car = "", False; msgs = []
            if t < tb + 3.6: inp, car = typed(p1, t, tb, 40)
            else: msgs.append(dict(role="user", text=p1, t0=tb + 3.6))
            if t > tt and t < tt + 3.0: inp, car = typed(p2, t, tt, 40)
            elif t >= tt + 3.0: msgs.append(dict(role="user", text=p2, t0=tt + 3.0))
            chat_window(c, 140, 70, 1100, 860, t, msgs, inp=inp, inp_caret=car)
            pill(c, 1290, 160, "THE FIX", 34, k=popk(t, tf), icon="check", icol=GRN, bgc="#14532d")
            if t > tb + 3.8:
                k = popk(t, tb + 3.8)
                with Pop(c, 1290, 260, 520, 220, k):
                    panel(c, 1290, 260, 520, 220); text(c, "voice", 1320, 310, 20, "b", "#a1a1aa")
                    c.drawLine(1460, 290, 1460, 450, paint(col(YEL), style="stroke", sw=3))
                    rrect(c, 1460 + 200 * (1 - eout(lin(t, tb + 4.2, tb + 5.2))), 380, 200, 50, 8, GRN); text(c, "EXPLOSION", 1560 + 200 * (1 - eout(lin(t, tb + 4.2, tb + 5.2))), 413, 20, "b", "#ffffff", 1, "c")
            if t > tt + 3.2:
                for i in range(8):
                    k = popk(t, tt + 3.2 + i * .12)
                    if k > 0:
                        x = 1300 + (i % 4) * 128; y = 540 + (i // 4) * 110
                        with Pop(c, x, y, 116, 90, k): rrect(c, x, y, 116, 90, 8, "#2a2a30"); check(c, x + 96, y + 18, 12, GRN)
        else:
            big_title(c, "REMEMBER THESE 2 LINES", 420, 90, popk(t, tm), YEL)
            pill(c, W / 2, 600, "1. Transcribe with word timestamps", 32, k=popk(t, tm + .4), icon="check", icol=GRN, align="c")
            pill(c, W / 2, 700, "2. Check one frame per sentence", 32, k=popk(t, tm + .8), icon="check", icol=GRN, align="c")
        dock(c, 1)
    return drift(D, 1.0, 1.04), draw

def s24(T0, D):   # outro
    td = L("the free skill", T0); tc = L("download them", T0); tn = L("and tell me", T0); tl = L("if this helped", T0); ts = L("see you", T0)
    sfx(0, "whoosh"); sfx(td, "pop"); sfx(tc + 1.6, "pop"); sfx(tn, "pop"); sfx(tl + .6, "click"); sfx(tl + 1.4, "click"); sfx(ts, "ding")
    def draw(c, t):
        bg(c, "Desktop")
        big_title(c, "THAT'S THE WHOLE PROCESS", 230, 80, popk(t, .05))
        if t > td:
            with Pop(c, 560, 320, 800, 140, popk(t, td)):
                panel(c, 560, 320, 800, 140); text(c, "FREE skill + all prompts", 960, 385, 40, "x", GRN, 1, "c"); text(c, "link in the description  ↓", 960, 430, 26, "m", "#d4d4d8", 1, "c")
        if t > tc + 1.6: pill(c, W / 2, 540, "Drop your first video in the comments", 30, k=popk(t, tc + 1.6), icon="dot", icol=BLUE, align="c")
        if t > tn: pill(c, W / 2, 630, "Next tutorial? Tell me below", 30, k=popk(t, tn), icon="dot", icol=PUR, align="c")
        if t > tl:
            lk = lin(t, tl + .6, tl + .8); sk = lin(t, tl + 1.4, tl + 1.6)
            rrect(c, 640, 730, 280, 80, 40, "#3a3a40" if lk < 1 else BLUE); text(c, "Like", 780, 782, 32, "b", "#ffffff", 1, "c")
            rrect(c, 1000, 730, 280, 80, 40, "#ff0033" if sk < 1 else "#3a3a40"); text(c, "Subscribed" if sk >= 1 else "Subscribe", 1140, 782, 30, "b", "#ffffff", 1, "c")
            cur = Path2([(tl, 1100, 950), (tl + .5, 780, 770), (tl + 1.0, 780, 770), (tl + 1.3, 1140, 770)]); x, y = cur.at(t)
            cursor(c, x, y, 1, clamp(1 - min(abs(t - tl - .6), abs(t - tl - 1.4)) * 8)); click_ring(c, 780, 770, lin(t, tl + .6, tl + .95)); click_ring(c, 1140, 770, lin(t, tl + 1.4, tl + 1.75))
        dock(c)
    return drift(D, 1.0, 1.04), draw

# --------------------------------------------------- timeline (cuts in the silences between phrases)
def cut(phrase, after=0.0):
    t = wt(phrase, after); return round(t - .18, 2)
B = [0.0, cut("what if you had"), cut("every video is"), cut("now look at"), cut("i searched"), cut("and im giving"), cut("but stay with"),
     cut("the whole process"), cut("step one"), cut("then i started"), cut("one important"), cut("step 2"), cut("claude started"),
     cut("heres a pro"), cut("step three"), cut("step four"), cut("next show"), cut("my first preview"), cut("once youre"),
     cut("and thats it", 240), cut("all of that"), cut("now the mistake"), cut("the reason was"), cut("thats my entire"), 307.83]
FNS = [s01, s02, s03, s04, s05, s06, s07, s08, s09, s10, s11, s12, s13, s14, s15, s16, s17, s18, s19, s20, s21, s22, s23, s24]
SCENES = [(f"s{i + 1:02d}", B[i], B[i + 1], FNS[i]) for i in range(len(FNS))]
INSERTS = [dict(id="x1", after=B[20], path=ROOT + "/assets/result_reel.mp4", dur=81.7, label="RESULT - made with Claude", color=CORAL)]
