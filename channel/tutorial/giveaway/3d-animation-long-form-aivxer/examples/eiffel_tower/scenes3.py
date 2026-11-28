# 3D Animation Long Form - made by aivxer. Copyright (c) 2026 aivxer.
# Free for your own videos. Do not re-share, sell, or claim this skill as your own (see LICENSE.txt).
import math, random, json, sys, os, subprocess
import numpy as np, skia
from kit3 import *
from timeline import CUE, LINES, END, SHOT_T, FLASH, A3

MOUTH = {k: mouth_track(f"{A3}/{k}.wav") for k in ("b1", "c1")}
GOLD = '#F2C14E'; RED = '#C8242C'; LIME = '#B8F04A'; CREAM = '#FFF6DC'


def speaking(key, t):
    i = int(round((t - CUE[key]) * FPS)); tr = MOUTH[key]
    return tr[i] if 0 <= i < len(tr) else None


def K(t, t0, d):
    return min(max((t - t0) / d, 0.0), 1.0)


rng = random.Random(7)
STARS = [(rng.uniform(-200, W + 200), rng.uniform(-100, 760), rng.choice((1.6, 2.0, 2.6, 3.2)), rng.uniform(0, 6)) for _ in range(120)]
SPECK = [(rng.uniform(0, W), rng.uniform(70, 1010), rng.uniform(1.5, 4.5), rng.uniform(40, 110)) for _ in range(260)]


# ------------------------------------------------------------------ outdoor pieces
def sky(c, top='#0A1136', bot='#24338A', h=860):
    c.drawRect(skia.Rect(-2000, -1500, W + 2000, H + 1500), sp(linear(0, 0, 0, h, [hx(top), hx(bot)])))


def stars(c, t):
    for (sx, sy, r, ph) in STARS:
        c.drawCircle(sx, sy, r, fp('#E8ECFF', 150 + 90 * math.sin(t * 2.4 + ph)))


def moon(c, x, y, r=50):
    for k, a in ((3.0, 16), (2.2, 22), (1.55, 30)): c.drawCircle(x, y, r * k, fp('#C9D4FF', a))
    c.drawCircle(x, y, r, fp('#F3EDD3')); c.drawCircle(x - r * .3, y - r * .25, r * .16, fp('#D9D2B4')); c.drawCircle(x + r * .25, y + r * .3, r * .22, fp('#DDD6B8'))


def cloud(c, x, y, s, v='#2C3B80', a=255):
    p = skia.Path()
    for dx, dy, r in ((-70, 8, 34), (-30, -14, 46), (22, -6, 40), (64, 10, 30)): p.addCircle(x + dx * s, y + dy * s, r * s)
    p.addRect(skia.Rect(x - 100 * s, y + 8 * s, x + 92 * s, y + 40 * s))
    c.drawPath(p, fp(v, a))


def tower(c, cx, base, hgt, lw=LW, t=0.0, sign=0.0, glow=True, light=-1):
    s = hgt / 1000.0
    X = lambda v: cx + v * s
    Y = lambda v: base - v * s
    body = skia.Path()
    body.moveTo(X(-265), Y(0)); body.cubicTo(X(-170), Y(180), X(-98), Y(330), X(-64), Y(420))
    body.lineTo(X(-34), Y(700)); body.lineTo(X(-11), Y(930)); body.lineTo(X(11), Y(930)); body.lineTo(X(34), Y(700))
    body.lineTo(X(64), Y(420)); body.cubicTo(X(98), Y(330), X(170), Y(180), X(265), Y(0))
    body.lineTo(X(160), Y(0)); body.cubicTo(X(118), Y(112), X(62), Y(172), X(0), Y(176))
    body.cubicTo(X(-62), Y(172), X(-118), Y(112), X(-160), Y(0)); body.close()
    if glow:
        for k, a in ((520, 14), (380, 20), (250, 26)): c.drawCircle(X(0), Y(380), k * s, fp('#FFD98A', a))
    c.drawPath(body, fp('#9A7650'))
    c.save(); c.clipPath(body, doAntiAlias=True)
    c.drawRect(skia.Rect(X(0) if light < 0 else X(-300), Y(1000), X(300) if light < 0 else X(0), Y(0)), fp('#6E5238'))
    lp = ink(max(1.6, lw * .34), INK, 190)
    for i in range(0, 50):
        yy = i * 20 - 20
        c.drawLine(X(-300), Y(yy), X(300), Y(yy + 64), lp); c.drawLine(X(300), Y(yy), X(-300), Y(yy + 64), lp)
    c.restore()
    c.drawPath(body, ink(lw))
    for (yy, ww, hh) in ((176, 178, 30), (420, 94, 24), (700, 52, 16)):
        rect(c, X(-ww), Y(yy + hh), X(ww), Y(yy), '#B48C5C', lw * .85)
        n = max(3, int(ww / 16))
        for i in range(n):
            px = X(-ww + (i + .5) * 2 * ww / n)
            c.drawCircle(px, Y(yy + hh / 2), max(2.2, 4.5 * s), fp('#FFE9A0'))
    poly(c, [(X(-9), Y(930)), (X(0), Y(1000)), (X(9), Y(930))], '#6E5238', lw * .7)
    a = 0.75 + 0.25 * math.sin(t * 5)
    for k, al in ((46, 30), (28, 60)): c.drawCircle(X(0), Y(962), max(k * s, k * .35), fp('#FFF1B8', al * a))
    c.drawCircle(X(0), Y(962), max(9 * s, 4), fp('#FFF6D0'))
    if sign > 0:
        sc = pop(sign)
        c.save(); c.translate(X(0), Y(430)); c.rotate(-7 + 5 * math.sin(t * 3.2) * (1 if sign >= 1 else 0)); c.scale(sc * s * 3.4, sc * s * 3.4)
        c.drawLine(-34, -2, 0, -46, ink(2.2, '#E8E0D0')); c.drawLine(34, -2, 0, -46, ink(2.2, '#E8E0D0'))
        rect(c, -66, -2, 66, 44, '#D63A30', 2.6, r=4)
        label(c, "FOR SALE", 0, 33, 31, CREAM, font=KALAM, align='center', skew=-0.1)
        c.restore()
    return X, Y


def paris_block(c, x, w, h, base, seed, lit=.4, lw=LW, body='#1C2658', roof='#131A42', dim='#263272'):
    r = random.Random(seed); top = base - h
    rect(c, x, top, x + w, base + 600, body, lw)
    poly(c, [(x - 8, top), (x + 16, top - 44), (x + w - 16, top - 44), (x + w + 8, top)], roof, lw)
    for i in range(r.randint(1, 3)):
        cx_ = x + r.uniform(.15, .8) * w
        rect(c, cx_, top - 78, cx_ + 22, top - 44, roof, lw * .8)
    cols = max(2, int((w - 30) // 46)); rows = int((h - 30) // 62)
    gap = (w - cols * 22) / (cols + 1)
    for j in range(rows):
        for i in range(cols):
            wx, wy = x + gap + i * (22 + gap), top + 26 + j * 62
            on = r.random() < lit
            rect(c, wx, wy, wx + 22, wy + 36, '#F2D88C' if on else dim, lw * .5)
            if on: c.drawRect(skia.Rect(wx - 8, wy - 8, wx + 30, wy + 44), fp('#FFD98A', 34, blur=7))


def far_city(c, base, seed=3, v='#1A2560'):
    r = random.Random(seed); x = -260
    while x < W + 260:
        w = r.uniform(90, 200); h = r.uniform(120, 260)
        c.drawRect(skia.Rect(x, base - h, x + w, base + 300), fp(v))
        c.drawRect(skia.Rect(x + 10, base - h - 26, x + w - 10, base - h), fp(v))
        for j in range(int(h // 50)):
            for i in range(int(w // 40)):
                if r.random() < .3: c.drawRect(skia.Rect(x + 12 + i * 40, base - h + 16 + j * 50, x + 24 + i * 40, base - h + 36 + j * 50), fp('#E9CF86', 200))
        x += w + r.uniform(-6, 10)


def tag(c, s, u, x=70, y=H - 86):
    a = ease_out(u * 3)
    if a <= 0: return
    w = text_w(s, 44)
    c.save(); c.translate(-50 * (1 - a), 0)
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(x, y - 52, x + w + 64, y + 18), 10, 10), fp((10, 12, 26), 205 * a))
    c.drawRect(skia.Rect(x, y - 52, x + 10, y + 18), fp(GOLD, 255 * a))
    label(c, s, x + 34, y, 44, CREAM, alpha=a, skew=-0.12)
    c.restore()


def lower_third(c, name, sub, u, x, y):
    a = back(min(u * 2.6, 1), 1.4)
    if u <= 0: return
    w = max(text_w(name, 76), 380)
    c.save(); c.translate(x, y); c.scale(a, a)
    rect(c, 0, -74, w + 84, 74, (12, 14, 28), LW * .8)
    c.drawRect(skia.Rect(3, -71, 19, 71), fp(GOLD))
    label(c, name, 44, 4, 76, CREAM, skew=-0.12)
    label(c, sub, 46, 54, 40, GOLD, skew=-0.12)
    c.restore()


def stamp(c, txt, x, y, u, rot=-10, size=150, v=RED):
    if u <= 0: return
    sc = 2.6 - 1.6 * ease_out(min(u * 5, 1))
    a = min(u * 8, 1)
    w = text_w(txt, size, MARKER)
    c.save(); c.translate(x, y); c.rotate(rot); c.scale(sc, sc)
    for inset, wd in ((0, 13), (18, 5)):
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(-w / 2 - 50 + inset, -size * .98 + inset, w / 2 + 50 - inset, size * .36 - inset), 16, 16), ink(wd, v, 255 * a))
    label(c, txt, 0, 0, size, v, font=MARKER, align='center', skew=0, alpha=a)
    c.restore()


# ------------------------------------------------------------------ shot 1: Paris
def shot_paris(c, t, gt):
    sky(c); stars(c, t); moon(c, 1570, 190)
    cloud(c, 380 + gt * 14, 250, 1.5); cloud(c, 1250 - gt * 10, 360, 1.1, '#26346F'); cloud(c, 1760 + gt * 8, 470, .9)
    blur_begin(c, 2.2); far_city(c, 800); c.restore()
    tower(c, 1010, 866, 740, t=t)
    for (x, w, h, sd) in ((-60, 250, 300, 1), (190, 210, 380, 2), (400, 250, 250, 3), (650, 150, 190, 9), (1330, 190, 210, 8), (1500, 240, 330, 4), (1740, 230, 400, 5)):
        paris_block(c, x, w, h, 866, sd)
    # river + bridge
    c.drawRect(skia.Rect(-400, 866, W + 400, H + 400), sp(linear(0, 866, 0, 1080, [hx('#16215A'), hx('#0A1034')])))
    c.drawLine(-400, 866, W + 400, 866, ink(LW))
    for i in range(30):
        yy = 884 + i * 7.5 + (i % 3) * 2
        xx = (i * 211 + t * 46 * (1 if i % 2 else -1)) % (W + 500) - 250
        c.drawLine(xx, yy, xx + 50 + (i % 4) * 26, yy, ink(3.5, '#F2D88C', 120 - i * 2))
    br = skia.Path(); br.moveTo(-200, 968)
    for i in range(6): br.quadTo(i * 400 - 10, 884, i * 400 + 190, 968)
    br.lineTo(2300, 968); br.lineTo(2300, 920); br.lineTo(-200, 920); br.close()
    br2 = skia.Path(); br2.addRect(skia.Rect(-200, 904, 2300, 1010))
    arch = skia.Path()
    for i in range(6): arch.addOval(skia.Rect(i * 400 - 165, 936, i * 400 + 145, 1100))
    shape(c, skia.Op(br2, arch, skia.PathOp.kDifference_PathOp), '#0E1438', LW)
    for i in range(6):
        lx = i * 400 + 190
        line(c, lx, 904, lx, 858, LW * .8); circ(c, lx, 850, 9, '#FFE9A0', LW * .5)
        add_light(c, lx, 850, 70, '#FFD98A', 120)
    vignette(c, .0)


# ------------------------------------------------------------------ office set
def banker_lamp(c, x, y, t):
    oval(c, x - 58, y - 16, x + 58, y + 6, '#D0A548', LW * .8)
    line(c, x, y - 8, x, y - 118, 12, INK); line(c, x, y - 8, x, y - 118, 6, '#E3BC5C')
    sh = skia.Path(); sh.moveTo(x - 116, y - 112); sh.cubicTo(x - 96, y - 196, x + 96, y - 196, x + 116, y - 112); sh.close()
    shape(c, sh, '#2FA25E', LW)
    hl = skia.Path(); hl.moveTo(x - 82, y - 138); hl.quadTo(x - 50, y - 172, x - 4, y - 174); c.drawPath(hl, ink(7, '#8FE0AE'))
    oval(c, x - 104, y - 122, x + 104, y - 100, '#FFF3B8', LW * .7)
    for i in range(6):  # fine drawn light rays under the shade
        a = math.radians(60 + i * 12)
        c.drawLine(x + 70 * math.cos(a), y - 96, x + 150 * math.cos(a), y - 96 + 84 * math.sin(a), ink(2.4, '#FFF6D0', 110))


def candlestick_phone(c, x, y):
    oval(c, x - 44, y - 16, x + 44, y + 6, '#1E1E26', LW * .8)
    line(c, x, y - 8, x, y - 110, 16, INK); line(c, x, y - 8, x, y - 110, 8, '#2C2C38')
    circ(c, x + 4, y - 122, 20, '#2C2C38', LW * .8); circ(c, x + 12, y - 122, 9, '#14141A', LW * .5)
    line(c, x - 6, y - 76, x - 38, y - 86, LW * .8)
    rect(c, x - 62, y - 128, x - 36, y - 50, '#2C2C38', LW * .8, r=10)


def office_bg(c, t, gt, sign_u=0.0, plant=False):
    # wall + wainscot + floor
    c.drawRect(skia.Rect(-900, -600, W + 900, 820), fp('#2F5449'))
    for i in range(-14, 48): c.drawLine(i * 62, -600, i * 62, 650, ink(10, '#2A4C42'))
    c.drawRect(skia.Rect(-900, 650, W + 900, 820), fp('#4E3020'))
    for i in range(-5, 16): rect(c, i * 190 + 24, 676, i * 190 + 170, 796, '#462A1B', LW * .6)
    line(c, -900, 650, W + 900, 650, LW)
    c.drawRect(skia.Rect(-900, 820, W + 900, H + 600), fp('#6A4429'))
    for i in range(1, 9): c.drawLine(-900, 820 + i * i * 6.5, W + 900, 820 + i * i * 6.5, ink(3, '#553520'))
    line(c, -900, 820, W + 900, 820, LW)
    # window view
    x0, y0, x1, y1 = 150, 96, 800, 640
    c.save(); c.clipRect(skia.Rect(x0, y0, x1, y1))
    sky(c, '#0B1238', '#2A3A96', 640); stars(c, t); moon(c, 250, 180, 30)
    cloud(c, 380 + gt * 5, 250, .6)
    blur_begin(c, 1.6)
    c.save(); c.translate(140, 250); c.scale(.5, .5); far_city(c, 800, 5); c.restore()
    for (bx, bw, bh, sd) in ((150, 150, 150, 11), (320, 130, 210, 12)): paris_block(c, bx, bw, bh, 640, sd, lw=LW * .7)
    tower(c, 645, 648, 500, lw=LW * .8, t=t, sign=sign_u)
    c.restore()
    for k in (0, 1):  # glass reflections
        px = 250 + k * 150
        c.drawPath(skia.Path.Polygon([(px, y0), (px + 60 - k * 30, y0), (px - 190 + 60 - k * 30, y1), (px - 190, y1)], True), fp('#FFFFFF', 15))
    c.restore()
    for (a, b, cc, d) in ((x0 - 22, y0 - 22, x1 + 22, y0), (x0 - 22, y1, x1 + 22, y1 + 22), (x0 - 22, y0, x0, y1), (x1, y0, x1 + 22, y1)):
        rect(c, a, b, cc, d, '#3B2416', LW * .8)
    line(c, (x0 + x1) / 2, y0, (x0 + x1) / 2, y1, 14, INK); line(c, (x0 + x1) / 2, y0, (x0 + x1) / 2, y1, 7, '#3B2416')
    line(c, x0, 300, x1, 300, 14, INK); line(c, x0, 300, x1, 300, 7, '#3B2416')
    rect(c, x0 - 44, y1 + 22, x1 + 44, y1 + 48, '#5A3824', LW * .8)
    # curtains + rod
    line(c, 40, 60, 930, 60, 12, INK); line(c, 40, 60, 930, 60, 6, '#C9A04A'); circ(c, 40, 60, 12, '#C9A04A', LW * .7); circ(c, 930, 60, 12, '#C9A04A', LW * .7)
    for (cx0, cx1) in ((54, 136), (822, 912)):
        cu = poly(c, [(cx0, 60), (cx1, 60), (cx1 + 8, 700), (cx0 - 10, 700)], '#93222B', LW)
        for k in (1, 2, 3): c.drawLine(cx0 + k * (cx1 - cx0) / 4, 66, cx0 - 6 + k * (cx1 - cx0 + 14) / 4, 694, ink(4, '#6E151D'))
    # wall things
    rect(c, 990, 190, 1160, 400, '#C39A45', LW); rect(c, 1008, 208, 1142, 382, '#EFE6CE', LW * .6)
    poly(c, [(1016, 372), (1050, 300), (1076, 340), (1104, 280), (1134, 372)], '#9DB7A6', LW * .5)
    c.drawCircle(1112, 244, 13, fp('#E9B44C'))
    circ(c, 1330, 250, 62, '#F4EFE2', LW); line(c, 1330, 250, 1330, 208, LW * .8); line(c, 1330, 250, 1358, 262, LW * .8); c.drawCircle(1330, 250, 5, fp(INK))
    rect(c, 1500, 170, 1640, 340, '#F7F3E8', LW); rect(c, 1500, 170, 1640, 218, '#C8242C', LW)
    label(c, "MAI", 1570, 208, 38, CREAM, align='center', skew=-0.1); label(c, "1925", 1570, 300, 58, INK, align='center', skew=-0.1)
    # chair + desk
    rect(c, 1430, 560, 1610, 800, '#7A2228', LW, r=26)
    for (bx, by) in ((1480, 620), (1560, 620), (1480, 700), (1560, 700)): c.drawCircle(bx, by, 5, fp('#4E1218'))
    c.drawOval(skia.Rect(1160, 1030, 1900, 1090), fp((0, 0, 0), 70, blur=14))
    rect(c, 1230, 800, 1850, 1062, '#6E4426', LW)
    for (dx0, dx1) in ((1262, 1520), (1560, 1818)):
        rect(c, dx0, 836, dx1, 930, '#7C4E2C', LW * .7); circ(c, (dx0 + dx1) / 2, 883, 9, '#D0A548', LW * .6)
        rect(c, dx0, 956, dx1, 1040, '#7C4E2C', LW * .7); circ(c, (dx0 + dx1) / 2, 998, 9, '#D0A548', LW * .6)
    rect(c, 1196, 770, 1884, 802, '#8E5C36', LW)
    c.drawRect(skia.Rect(1250, 773, 1830, 782), fp('#2F6B45'))
    banker_lamp(c, 1690, 770, t)
    candlestick_phone(c, 1320, 770)
    for k in range(3): rect(c, 1420 + k * 5, 752 - k * 6, 1560 + k * 5, 764 - k * 6, '#F7F3E8', LW * .6)
    # souvenir tower + plant
    poly(c, [(1596, 770), (1614, 700), (1620, 664), (1626, 700), (1644, 770), (1630, 770), (1620, 740), (1610, 770)], '#D0A548', LW * .6)
    if plant: poly(c, [(1866, 800), (1960, 800), (1946, 890), (1880, 890)], '#B5653A', LW)
    for a_ in ((-70, -35, 0, 30) if plant else ()):
        fr = skia.Path(); fr.moveTo(1912, 800); fr.quadTo(1912 + a_ * 1.2, 640, 1912 + a_ * 2.6, 610 + abs(a_))
        c.drawPath(fr, ink(24, INK)); c.drawPath(fr, ink(13, '#3E9A56'))
    # rug
    oval(c, 560, 930, 1360, 1070, '#7E2A30', LW * .8); c.drawOval(skia.Rect(600, 944, 1320, 1056), ink(6, '#C39A45'))


OFFICE_LIGHTS = [('pool', 1690, 720, 600, .95), ('pool', 1000, 560, 430, .92), ('oval', 1000, 1000, 380, 110, .7)]


def office_night(c, extra=()):
    win = skia.Path(); win.addRect(skia.Rect(150, 96, 800, 640))
    spill = skia.Path.Polygon([(190, 700), (760, 700), (1040, 1090), (330, 1090)], True)
    night(c, OFFICE_LIGHTS + [('path', win, .82, 10), ('path', spill, .36, 34)] + list(extra), '#4C5CA0')
    add_light(c, 1690, 690, 430, '#FFD98A', 70)
    add_light(c, 1690, 664, 120, '#FFF3C8', 150)


def shot_office(c, t, gt):
    s0 = SHOT_T['office'][0]
    turn = K(gt, 3.55, .22)
    office_bg(c, t, gt, sign_u=(gt - 4.55) / .32 if gt > 4.55 else 0)
    c.drawOval(skia.Rect(900, 1000, 1110, 1044), fp((0, 0, 0), 110, blur=8))
    spk = (gt > 3.55)
    eyes = 'closed' if blink(gt, 2.3, .2) else ('half' if spk else 'dot')
    sq = 0.05 * math.sin(K(gt, 3.55, .28) * math.pi) + 0.04 * math.sin(K(gt, s0, .3) * math.pi)
    draw_char3(c, 1005, 1024, 1.08, LUSTIG, face=-0.78 * back(turn, 1.2), eyes=eyes, mouth='smirk' if spk else 'smile',
               brow=.9 * turn, arms=(('down', 'present', K(gt, 3.6, .3)), 'pocket'), tilt=-4 * turn + 1.2 * math.sin(gt * 2.2),
               bob=3 + 3 * math.sin(gt * 3.1), squash=sq, light=1, rim='#FFE6B0')
    office_night(c)


# ------------------------------------------------------------------ shot 3: table top
def sleeve(c, x0, y0, x1, y1, width, v, cuff='#F4EFE2', skin='#E6BE8E', fingers=True, hand_r=None):
    ang = math.degrees(math.atan2(y1 - y0, x1 - x0)); L = math.hypot(x1 - x0, y1 - y0)
    hr = hand_r or width * .5
    c.save(); c.translate(x0, y0); c.rotate(ang)
    circ(c, L + hr * .55, 0, hr, skin, LW)
    if fingers:
        for k in (-.42, 0, .42): c.drawLine(L + hr * 1.2, k * hr, L + hr * 1.52, k * hr * 1.1, ink(LW * .8))
    rect(c, -200, -width / 2, L, width / 2, v, LW)
    rect(c, L - 34, -width / 2 - 5, L + 6, width / 2 + 5, cuff, LW)
    c.restore()


def shot_table(c, t, gt):
    s0 = SHOT_T['table'][0]; n3 = CUE['n3']
    c.drawRect(skia.Rect(-900, -700, W + 900, H + 700), fp('#E9DFBF'))
    c.drawRect(skia.Rect(-900, -700, W + 900, H + 700), sp(radial(960, 520, 1300, [hx('#F6EED4'), hx('#E6DBB8'), hx('#CDBF98')], [0, .6, 1])))
    for (sx, sy, r, a) in SPECK: c.drawCircle(sx, sy, r, fp('#9A8F6E', a))
    for (ya, yb) in ((-700, 64), (1016, H + 700)):
        c.drawRect(skia.Rect(-900, ya, W + 900, yb), fp('#2F6B45'))
    for yy in (64, 1016): line(c, -900, yy, W + 900, yy, LW)
    for yy in (78, 1002): line(c, -900, yy, W + 900, yy, 3, INK, 120)
    # blueprint sheet pushed in by Lustig's hand
    k = back(K(gt, s0 + .05, .5), 1.3)
    px = lerp(-560, 700, k); py = 560
    c.save(); c.translate(px, py); c.rotate(-7)
    c.drawRect(skia.Rect(-322, -238, 342, 262), fp((60, 40, 10), 70, blur=12))
    rect(c, -330, -250, 330, 250, '#FBFAF2', LW)
    for i in range(1, 12): c.drawLine(-326, -250 + i * 41, 326, -250 + i * 41, ink(2, '#B9CDE8'))
    wu = ease(K(gt, s0 + .45, 1.0))
    c.save(); c.clipRect(skia.Rect(-330, 250 - 500 * wu, 330, 250))
    bl = ink(5, '#2A44A8')
    pts = [(-150, 205), (-40, -20), (-10, -205), (10, -205), (40, -20), (150, 205)]
    for a_, b_ in zip(pts, pts[1:]): c.drawLine(*a_, *b_, bl)
    for yy, ww in ((110, 100), (-20, 46), (-150, 20)): c.drawLine(-ww, yy, ww, yy, bl)
    ar = skia.Path(); ar.moveTo(-92, 205); ar.quadTo(0, 60, 92, 205); c.drawPath(ar, bl)
    for i in range(7): c.drawLine(-120 + i * 13, 190 - i * 44, 120 - i * 13, 150 - i * 44, ink(2.4, '#2A44A8', 150))
    c.restore()
    if gt > s0 + .5:
        label(c, "TOUR EIFFEL", -300, -196, 44, '#2A44A8', skew=-0.12, alpha=K(gt, s0 + .5, .15))
        label(c, "300 m", 180, 60, 36, '#2A44A8', skew=-0.12, alpha=K(gt, s0 + .9, .15))
        c.drawLine(168, -200, 168, 200, ink(2.4, '#2A44A8', 255 * K(gt, s0 + .9, .15)))
    c.restore()
    hk = k - 0.06 * ease(K(gt, s0 + .7, .5))
    hx_ = lerp(-560, 700, hk) - 400
    sleeve(c, hx_ - 500, 660, hx_, 600, 170, '#3B4660')
    # counter
    if gt > n3 + .15:
        pu = pop(K(gt, n3 + .15, .3))
        v = int(round(7000 * ease_out(K(gt, n3 + .25, 1.15)) / 50) * 50)
        c.save(); c.translate(1440, 290); c.rotate(-4); c.scale(pu, pu)
        label(c, f"{v:,} TONS", 0, 0, 150, LIME, align='center', stroke=16, skew=-0.14)
        label(c, "OF IRON", 0, 96, 78, CREAM, align='center', stroke=13, skew=-0.14)
        c.restore()
    # buyer's hand with cash
    tb = n3 + 1.75
    if gt > tb - .1:
        kb = back(K(gt, tb, .42), 1.5)
        bx = lerp(2500, 1560, kb)
        c.save(); c.translate(bx - 40, 700); c.rotate(-80)
        for i, a_ in enumerate((-16, -4, 9)):
            c.save(); c.rotate(a_); rect(c, -130, 20, 130, 160, '#6FA36A', LW); rect(c, -108, 40, 108, 140, '#84B67E', LW * .5); circ(c, 0, 90, 26, '#6FA36A', LW * .5); c.restore()
        c.restore()
        sleeve(c, bx + 560, 760, bx + 60, 716, 170, '#7A5A3C', skin='#EBC79C')
    # price tag
    tp = n3 + 1.95
    if gt > tp:
        pu = pop(K(gt, tp, .3))
        c.save(); c.translate(1060, 905); c.rotate(-9 + 3 * math.sin(gt * 5) * (1 - K(gt, tp, 1.0))); c.scale(pu, pu)
        c.drawLine(-190, -6, -260, -60, ink(4, '#8A6A3A'))
        poly(c, [(-190, -6), (-140, -62), (170, -62), (170, 62), (-140, 62)], '#EBCB8B', LW)
        circ(c, -150, 0, 11, '#E9DFBF', LW * .6)
        label(c, "CHEAP!", 30, 26, 84, RED, font=MARKER, align='center', skew=-0.06)
        c.restore()


# ------------------------------------------------------------------ close-ups
def closeup_bg(c, t, gt, dx, zoom=1.5):
    blur_begin(c, 13)
    c.save(); c.translate(dx, -200); c.scale(zoom, zoom); office_bg(c, t, gt, sign_u=1.0, plant=True); c.restore()
    c.restore()
    night(c, [('pool', 960, 520, 900, .55)], '#4C5CA0')


def talk(key, gt, rest, mapping):
    m = speaking(key, gt)
    if m is None: return rest, 0
    return mapping[m], (5 if m == 'open' else 2 if m == 'mid' else 0)


def shot_buyer(c, t, gt):
    s0 = SHOT_T['buyer'][0]
    closeup_bg(c, t, gt, -900)
    mouth, hb = talk('b1', gt, 'o', {'open': 'mid', 'mid': 'o', 'closed': 'flat'})
    sq = 0.07 * math.sin(K(gt, s0, .26) * math.pi)
    draw_char3(c, 1080, 1390, 2.15, BUYER, face=-0.72, eyes='wide', mouth=mouth, brow=1.0, brow_tilt=-.7,
               arms=('down', ('down', 'chin', K(gt, s0 + .1, .3))), tilt=2 * math.sin(gt * 9) + 2, bob=hb * .6, squash=sq,
               sweat=(gt - s0) * 1.1, light=1, rim='#FFE6B0', pupil=-1)
    add_light(c, 1500, 380, 700, '#FFD98A', 36)


def shot_lustig(c, t, gt):
    s0 = SHOT_T['lustig'][0]; c1 = CUE['c1']
    closeup_bg(c, t, gt, -1750)
    barg = gt > c1 + 1.12
    mouth, hb = talk('c1', gt, 'smirk', {'open': 'open', 'mid': 'mid', 'closed': 'smirk'})
    eyes = 'closed' if (blink(gt, 2.1, 1.0) or (barg and speaking('c1', gt) is None)) else 'half'
    sq = 0.06 * math.sin(K(gt, s0, .26) * math.pi) + 0.05 * math.sin(K(gt, c1 + 1.12, .26) * math.pi)
    draw_char3(c, 840, 1390, 2.15, LUSTIG, face=0.72, eyes=eyes, mouth=mouth, brow=.95 if barg else .35,
               arms=('pocket', ('down', 'gesture', K(gt, c1 + .05, .3))), tilt=-3 + 2.5 * math.sin(gt * 2.4) - (4 if barg else 0),
               bob=hb * .6, squash=sq, light=-1, rim='#FFE6B0',
               sparkle=(gt - (c1 + LINES['c1']['dur'] - .12)) / .3 if gt > c1 + LINES['c1']['dur'] - .12 else 0)
    add_light(c, 420, 380, 700, '#FFD98A', 36)


def shot_card(c, t, gt):
    c.drawRect(skia.Rect(-W, -H, 2 * W, 2 * H), fp((0, 0, 0)))
    words = "There's just one problem.".split()
    d = LINES['n4']['dur'] - .15; t0 = CUE['n4']
    tot = sum(len(w) + 1 for w in words); acc = 0; k = 0
    for w in words:
        if gt >= t0 + d * acc / tot - .04: k += 1
        acc += len(w) + 1
    f = skia.Font(FONT_HAND, 136); full = f.measureText(" ".join(words))
    if k: c.drawString(" ".join(words[:k]), W / 2 - full / 2, H / 2 + 44, f, fp('#FFFFFF'))


# ------------------------------------------------------------------ tower low angle
def shot_tower(c, t, gt):
    sky(c, '#070C2A', '#22308A', 1080); stars(c, t); moon(c, 380, 250, 44)
    cloud(c, 300 + gt * 22, 560, 1.7); cloud(c, 1560 - gt * 18, 400, 1.4, '#26346F'); cloud(c, 1180 + gt * 12, 760, 1.2)
    tower(c, 960, 1820, 2350, lw=10, t=t)
    ts = CUE['n5'] + .42
    if gt > ts: stamp(c, "NOT FOR SALE", 960, 640, (gt - ts) / .9, rot=-9, size=170)


# ------------------------------------------------------------------ street
def street_lamp(c, x, y_base, y_top):
    line(c, x, y_base, x, y_top, 22, INK); line(c, x, y_base, x, y_top, 11, '#2B2D3C')
    rect(c, x - 22, y_base - 26, x + 22, y_base + 4, '#2B2D3C', LW * .8)
    poly(c, [(x - 40, y_top + 4), (x + 40, y_top + 4), (x + 26, y_top - 72), (x - 26, y_top - 72)], '#FFF0B4', LW)
    poly(c, [(x - 48, y_top - 72), (x + 48, y_top - 72), (x, y_top - 112)], '#2B2D3C', LW)
    line(c, x - 40, y_top + 4, x + 40, y_top + 4, LW)


HERO_POS = [0, 0]


def shot_hero(c, t, gt):
    s0 = SHOT_T['hero'][0]
    sky(c, '#0A1136', '#26358C', 760); stars(c, t); moon(c, 1500, 150, 36)
    cloud(c, 700 + gt * 8, 220, 1.0)
    blur_begin(c, 2.0); far_city(c, 660, 8, '#1E2A68'); tower(c, 985, 716, 450, lw=LW * .7, t=t); c.restore()
    for (x, w, h, sd) in ((-90, 300, 500, 21), (210, 240, 410, 22), (1660, 250, 400, 24), (1900, 260, 470, 25)):
        paris_block(c, x, w, h, 760, sd, lit=.34, body='#222E66', dim='#2C3A80')
    # cafe front
    rect(c, 1090, 470, 1660, 760, '#4A3550', LW)
    rect(c, 1140, 560, 1380, 720, '#F6DE96', LW); line(c, 1260, 560, 1260, 720, LW * .7)
    rect(c, 1440, 540, 1580, 760, '#6A4428', LW); circ(c, 1558, 660, 7, '#D0A548', LW * .5)
    aw = poly(c, [(1070, 470), (1680, 470), (1710, 540), (1040, 540)], '#C8242C', LW)
    c.save(); c.clipPath(aw, doAntiAlias=True)
    for i in range(0, 14, 2): c.drawPath(skia.Path.Polygon([(1070 + i * 46, 470), (1116 + i * 46, 470), (1092 + i * 48, 540), (1044 + i * 48, 540)], True), fp('#F4EFE2'))
    c.restore(); c.drawPath(aw, ink(LW))
    label(c, "CAFÉ", 1375, 452, 60, '#F6DE96', align='center', skew=-0.1)
    # pavement + cobbles
    c.drawRect(skia.Rect(-900, 760, W + 900, 840), fp('#444B70')); line(c, -900, 760, W + 900, 760, LW); line(c, -900, 840, W + 900, 840, LW)
    c.drawRect(skia.Rect(-900, 840, W + 900, H + 600), fp('#30365A'))
    r = random.Random(4)
    for row in range(7):
        yy = 856 + row * 36 + row * row * 1.5; wd = 84 + row * 8
        for kx in range(-4, 30):
            xx = kx * (wd + 10) + (row % 2) * wd / 2 - 100
            c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(xx, yy, xx + wd, yy + 24 + row * 2), 10, 10), fp('#3C4368' if r.random() < .7 else '#474F78'))
    lx = 560
    street_lamp(c, lx, 842, 330)
    # character: walk in, stop, tip hat
    wk = K(gt, s0, 1.15); x = lerp(150, 790, ease_out(wk)) if wk < 1 else 790
    walking = wk < .97
    ph = (gt - s0) * 11
    tip = K(gt, CUE['n6'] + .55, .28) - K(gt, CUE['n6'] + 1.35, .3)
    fin = gt > CUE['n7'] + .2
    eyes = 'closed' if (blink(gt, 2.6, .4) or tip > .5) else 'half'
    c.drawOval(skia.Rect(x - 110, 978, x + 110, 1020), fp((0, 0, 0), 120, blur=8))
    sq = 0.05 * math.sin(K(gt, s0 + 1.15, .25) * math.pi)
    draw_char3(c, x, 1000, 1.0, LUSTIG, face=0.7 if walking else lerp(0.7, 0.3, K(gt, s0 + 1.15, .25)),
               eyes=eyes, mouth='smirk', brow=.9 if fin else .3,
               arms=(('down', 'hat', max(tip, 0)), 'pocket') if not walking else ('down', 'pocket'),
               tilt=(3 * math.sin(ph) if walking else -2 - 7 * max(tip, 0)), bob=(7 * abs(math.sin(ph)) if walking else 2 + 2 * math.sin(gt * 2.4)),
               squash=sq, hat=True, light=-1, rim='#FFE6B0', legs=walk_legs(ph) if walking else None)
    HERO_POS[0], HERO_POS[1] = x, 1000 - 430
    # lighting
    cone = cone_path(lx, 300, 80, 760, 780, lean=110)
    night(c, [('path', cone, .92, 24), ('oval', lx + 130, 1000, 520, 120, .85), ('pool', 1260, 640, 380, .9), ('pool', 985, 520, 300, .6),
              ('pool', x, 600, 340, .5 + .42 * K(x, 300, 400))], '#5A69B6')
    c.drawPath(cone, sp(linear(lx, 300, lx + 110, 1080, [hx('#FFE9A8', 64), hx('#FFE9A8', 12)]), blend=skia.BlendMode.kPlus, blur=20))
    add_light(c, lx, 290, 130, '#FFF0B4', 170); add_light(c, 1260, 640, 360, '#FFD98A', 44)
    c.drawRect(skia.Rect(-400, 900, W + 400, 1200), fp('#8FA0E0', 20, blur=50))
    if gt > CUE['n6'] + .5: lower_third(c, "VICTOR LUSTIG", "CON MAN · PARIS, 1925", gt - (CUE['n6'] + .5), 1090, 930)


SHOTS = [  # name, fn, zoom0, zoom1, focus0, focus1, rot, whip_out, vignette
    ("paris", shot_paris, 1.00, 1.10, (1000, 560), (1010, 540), 0, True, .62),
    ("office", shot_office, 1.00, 1.06, (960, 548), (948, 544), 0, True, .66),
    ("table", shot_table, 1.03, 1.10, (960, 540), (990, 536), 2.0, False, .46),
    ("buyer", shot_buyer, 1.00, 1.05, (960, 540), (975, 540), 0, False, .6),
    ("lustig", shot_lustig, 1.00, 1.07, (960, 540), (945, 540), 0, False, .6),
    ("card", shot_card, 1.0, 1.03, (960, 540), (960, 540), 0, False, 0),
    ("tower", shot_tower, 1.00, 1.14, (960, 620), (960, 560), 0, True, .62),
    ("hero", shot_hero, 1.00, 1.09, (960, 560), (990, 580), 0, False, .64),
]
OUT = "/home/claude/vid/scenes3"


def render_shot(idx, only_frames=None, out_png=None):
    name, fn, z0, z1, f0, f1, rot, whip, vig = SHOTS[idx]
    s0, s1 = SHOT_T[name]
    n0, n1 = int(round(s0 * FPS)), int(round(s1 * FPS))
    surf = skia.Surface(W, H); c = surf.getCanvas(); proc = None
    prev_whip = idx > 0 and SHOTS[idx - 1][7]
    if only_frames is None:
        tmp = f"{OUT}/{idx:02d}_{name}.tmp.mp4"
        proc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{W}x{H}", "-r", str(FPS),
                                 "-i", "-", "-c:v", "libx264", "-crf", "17", "-preset", "medium", "-pix_fmt", "yuv420p", tmp], stdin=subprocess.PIPE)
    for f in (range(n0, n1) if only_frames is None else only_frames):
        gt = f / FPS; u = (f - n0) / max(n1 - n0 - 1, 1)
        c.clear(C((0, 0, 0))); c.save()
        e = ease(u); z = z0 + (z1 - z0) * e
        fx, fy = lerp(f0[0], f1[0], e), lerp(f0[1], f1[1], e)
        wx = 0; sig = 0; wk = n1 - f
        if whip and wk <= 5: wx = -((6 - wk) ** 2) * 34; sig = (6 - wk) * 16
        if prev_whip and f - n0 < 4: wx = (4 - (f - n0)) ** 2 * 52; sig = (4 - (f - n0)) * 18
        shx = shy = 0
        if name == 'tower':
            ts = CUE['n5'] + .42
            if ts <= gt < ts + .35:
                d = 1 - (gt - ts) / .35; shx = 16 * d * math.sin(gt * 90); shy = 12 * d * math.cos(gt * 77)
        c.translate(W / 2 + wx + shx, H / 2 + shy); c.scale(z, z); c.rotate(rot * (e - .5)); c.translate(-fx, -fy)
        fn(c, gt, gt)
        c.restore()
        if name != 'card':
            finish(surf, bloom=0.40); vignette(c, vig)
        if name == 'paris': tag(c, "PARIS  ·  1925", (gt - .25) / 1.0)
        if name == 'tower':
            ts = CUE['n5'] + .42
            if ts <= gt < ts + 2 / FPS + 1e-6:
                c.drawRect(skia.Rect(0, 0, W, H), fp('#FFFFFF'))
                rr = random.Random(f)
                for i in range(110):
                    a = rr.uniform(0, 2 * math.pi); r0 = rr.uniform(300, 470)
                    c.drawLine(W / 2 + r0 * math.cos(a), H / 2 + r0 * .7 * math.sin(a), W / 2 + 1500 * math.cos(a), H / 2 + 1500 * math.sin(a), ink(rr.uniform(3, 15), (0, 0, 0)))
                stamp(c, "NOT FOR SALE", 960, 560, 1.0, rot=-9, size=170, v=(0, 0, 0))
        if name == 'hero' and gt >= FLASH:
            img = surf.makeImageSnapshot()
            c.clear(C((12, 12, 22)))
            k = ease_out((gt - FLASH) / .32)
            c.save(); c.translate(W / 2, H / 2 - 56 * k); c.rotate(-4.0 * k); sc = 1 - .33 * k; c.scale(sc, sc)
            c.drawRect(skia.Rect(-W / 2 - 30, -H / 2 - 30, W / 2 + 70, H / 2 + 200), fp((0, 0, 0), 120, blur=30))
            c.drawRect(skia.Rect(-W / 2 - 44, -H / 2 - 44, W / 2 + 44, H / 2 + 170), fp('#F7F2E6'))
            c.drawImageRect(img, skia.Rect(-W / 2, -H / 2, W / 2, H / 2), skia.SamplingOptions(skia.FilterMode.kLinear))
            c.drawRect(skia.Rect(-W / 2, -H / 2, W / 2, H / 2), ink(4, INK, 160))
            if gt > FLASH + .3:
                cu = min((gt - FLASH - .3) / .4, 1)
                hxs = (HERO_POS[0] - fx) * z; hys = (HERO_POS[1] - fy) * z
                ring = skia.Path(); ring.addArc(skia.Rect(hxs - 185, hys - 190, hxs + 195, hys + 175), -110, 352.0 * ease(cu)); c.drawPath(ring, ink(18, RED))
            if gt > FLASH + .68:
                a = min((gt - FLASH - .68) / .12, 1)
                label(c, "SOLD IT... TWICE", -W / 2 + 40, H / 2 + 128, 118, RED, font=FONT_HAND, skew=0, alpha=a)
            c.restore()
            fl = max(0, 1 - (gt - FLASH) / .22)
            if fl > 0: c.drawRect(skia.Rect(0, 0, W, H), fp('#FFFFFF', 255 * fl))
        if sig > 0:
            img = surf.makeImageSnapshot(); c.clear(C((0, 0, 0)))
            p = skia.Paint(); p.setImageFilter(skia.ImageFilters.Blur(sig, 0.01, skia.TileMode.kClamp)); c.drawImage(img, 0, 0, skia.SamplingOptions(), p)
        if proc: proc.stdin.write(surf.makeImageSnapshot().toarray(colorType=skia.kBGRA_8888_ColorType).tobytes())
        elif out_png: surf.makeImageSnapshot().save(out_png.format(f=f), skia.kPNG)
    if proc:
        proc.stdin.close(); rc = proc.wait()
        if rc == 0: os.replace(tmp, tmp.replace(".tmp.mp4", ".mp4"))
        return rc


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True); os.makedirs("/home/claude/vid/frames3", exist_ok=True)
    if sys.argv[1] == "frames":
        for spec in sys.argv[2:]:
            i, tt = spec.split(":"); i = int(i); f = int(round(float(tt) * FPS))
            render_shot(i, only_frames=[f], out_png="/home/claude/vid/frames3/s%02d_{f}.png" % i)
    else:
        for i in map(int, sys.argv[2:]): print(i, SHOTS[i][0], render_shot(i), flush=True)
