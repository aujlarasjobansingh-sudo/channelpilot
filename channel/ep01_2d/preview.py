# EP01 hook preview (premium pass) in 2D ink style, cut to the user's voiceover (0 - 14.3 s)
# usage: python3 preview.py [stills t1,t2,...]   (no args = render all)
import sys, math, random, subprocess, os
from kit2d import *

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out'); os.makedirs(OUT, exist_ok=True)
END = 14.3
IMPACTS = [3.72, 12.74]

def shake(t, t0, dur=0.45, amp=22):
    if t < t0 or t > t0 + dur: return 0, 0
    k = (1 - (t - t0) / dur) ** 2 * amp; f = int(t * FPS)
    r = random.Random(f * 7 + int(t0 * 100)); return r.uniform(-k, k), r.uniform(-k, k)

def grad_rect(c, x0, y0, x1, y1, top, bot, w=0):
    p = skia.Path(); p.addRect(skia.Rect(x0, y0, x1, y1)); c.drawPath(p, sp(linear(0, y0, 0, y1, [hx(top), hx(bot)])))
    if w: c.drawPath(p, ink(w))
def grad_shape(c, path, top, bot, y0, y1, w=LW):
    c.drawPath(path, sp(linear(0, y0, 0, y1, [hx(top), hx(bot)])))
    if w: c.drawPath(path, ink(w))

def city_strip(c, y_base, seed, hmin, hmax, wmin, wmax, body, body2, win, lit=0.35, outline=True, x0=-400, x1=W + 400, roof=True):
    r = random.Random(seed); x = x0
    while x < x1:
        w = r.uniform(wmin, wmax); h = r.uniform(hmin, hmax); top = y_base - h
        p = skia.Path(); p.addRect(skia.Rect(x, top, x + w, y_base + 60))
        c.drawPath(p, sp(linear(x, 0, x + w, 0, [hx(body), hx(body2)])))
        if roof and r.random() < .5: c.drawRect(skia.Rect(x + w * .2, top - 22, x + w * .45, top), fp(body2))
        if roof and r.random() < .3: c.drawLine(x + w * .7, top, x + w * .7, top - 60, ink(3, body2, boil=False))
        if outline: c.drawPath(p, ink(LW))
        cols = max(1, int(w // 34)); rows = int(h // 44)
        for i in range(cols):
            for j in range(rows):
                if r.random() < lit:
                    wx = x + 12 + i * (w - 24) / cols; wy = top + 18 + j * 44
                    c.drawRect(skia.Rect(wx, wy, wx + 14, wy + 20), fp(win, r.randint(150, 255)))
        x += w + r.uniform(-6, 14)

_cache = {}
def cached(key, fn):
    if key not in _cache:
        s = skia.Surface(W, H); cc = s.getCanvas(); cc.clear(C((0, 0, 0), 0)); fn(cc); _cache[key] = s.makeImageSnapshot()
    return _cache[key]
def blit(c, img, dx=0, dy=0, blur=0, alpha=1.0):
    p = skia.Paint(); p.setAlphaf(alpha)
    if blur: p.setImageFilter(skia.ImageFilters.Blur(blur, blur))
    c.drawImage(img, dx, dy, skia.SamplingOptions(skia.FilterMode.kLinear), p)

def bokeh(c, seed, n, cols, rmin, rmax, t, drift=10, a=70, area=(0, 0, W, H)):
    r = random.Random(seed)
    for i in range(n):
        x = r.uniform(area[0], area[2]) + math.sin(t * .5 + i) * drift; y = r.uniform(area[1], area[3]); rad = r.uniform(rmin, rmax)
        cc = r.choice(cols); c.drawCircle(x, y, rad, fp(cc, a * r.uniform(.5, 1), blur=rad * .25))

def flame(c, x, y, s, t, seed):
    f = math.sin(t * 13 + seed) * .12 + math.sin(t * 21 + seed * 2) * .08
    for (sc, cl) in ((1.0, '#FF6A2A'), (.62, '#FFC23C'), (.3, '#FFF3B0')):
        h = 120 * s * sc * (1 + f); w_ = 46 * s * sc
        p = skia.Path(); p.moveTo(x, y - h); p.cubicTo(x + w_ * 1.3, y - h * .45, x + w_, y, x, y); p.cubicTo(x - w_, y, x - w_ * 1.3, y - h * .45, x + w_ * .2 * f * 5, y - h); p.close()
        c.drawPath(p, fp(cl));
        if sc == 1.0: c.drawPath(p, ink(LW * .7))
    add_light(c, x, y - 50 * s, 260 * s, '#FF8A3C', 110)

# ======================= SHOT 1: asleep -> wake up (0 - 2.1)
def room_bg(c):
    grad_rect(c, -300, -300, W + 300, 820, '#4F5F96', '#7B8FC4')
    for i in range(-4, 34):
        c.drawRect(skia.Rect(i * 70, -300, i * 70 + 4, 820), fp('#8A9DD0', 90))
        for j in range(12): c.drawCircle(i * 70 + 35, j * 80 + 20, 4, fp('#90A2D4', 120))
    grad_rect(c, -300, 790, W + 300, H + 300, '#7A5641', '#4A3226')
    for i in range(-6, 30): c.drawLine(i * 120, 800, i * 120 - 220, H + 300, ink(3, '#5E4032', boil=False))
    rect(c, -300, 780, W + 300, 806, '#E7DCC6', LW)
    p = skia.Path(); p.addOval(skia.Rect(640, 880, 1500, 1060)); c.drawPath(p, fp('#B8464F')); c.drawPath(p, ink(LW))
    p2 = skia.Path(); p2.addOval(skia.Rect(700, 900, 1440, 1040)); c.drawPath(p2, ink(4, '#E9C46A'))
    # shelf with action figure + plant + books
    rect(c, 160, 420, 520, 440, '#8C5E3F', LW, 4)
    for i, (bw, bh, bc) in enumerate(((26, 90, '#3E6DB5'), (22, 76, '#C8424A'), (30, 98, '#E9B53C'), (20, 70, '#4E9A6E'))):
        bx = 180 + sum(q[0] + 4 for q in ((26,), (22,), (30,), (20,))[:i]); rect(c, bx, 420 - bh, bx + bw, 420, bc, LW * .7, 3)
    rect(c, 420, 360, 470, 420, '#C86B3A', LW * .8, 6)
    for a_ in (-50, -15, 20, 55): c.save(); c.translate(445, 360); c.rotate(a_); oval(c, -12, -60, 12, 0, '#5DAA6A', LW * .7); c.restore()
    # poster of #1 hero
    c.save(); c.translate(300, 230); c.rotate(-3)
    rect(c, -95, -120, 95, 120, '#F2C14E', LW); rect(c, -78, -102, 78, 50, '#B5302E', LW * .7)
    c.drawCircle(0, -30, 40, fp('#F0C9A0')); c.drawCircle(0, -30, 40, ink(LW * .7))
    label(c, '#1', 0, 104, 46, '#18161B', MARKER, 'center', skew=0)
    c.restore()

def window_view(c, t, flash):
    wx0, wy0, wx1, wy1 = 1240, 150, 1700, 600
    win = skia.Path(); win.addRect(skia.Rect(wx0, wy0, wx1, wy1))
    c.save(); c.clipPath(win)
    grad_rect(c, wx0, wy0, wx1, wy1, '#10173F', '#4A3474')
    c.drawCircle(1600, 230, 34, fp('#FFF4D0')); add_light(c, 1600, 230, 140, '#FFF4D0', 60)
    for i in range(3):
        cx = 1300 + ((t * 18 + i * 160) % 520); puff(c, cx, 200 + i * 40, 26, i + 3, '#3C3F78', '#2E3062', 220, outline=False)
    city_strip(c, 600, 3, 80, 260, 50, 110, '#262D58', '#1C2246', '#FFD27A', .45, x0=wx0 - 50, x1=wx1 + 50)
    if flash > 0: c.drawRect(skia.Rect(wx0, wy0, wx1, wy1), fp('#FF8A3C', 230 * flash))
    c.restore()
    c.drawPath(win, ink(LW * 1.4))
    line(c, (wx0 + wx1) / 2, wy0, (wx0 + wx1) / 2, wy1); line(c, wx0, (wy0 + wy1) / 2, wx1, (wy0 + wy1) / 2)
    c.drawLine(wx0 + 30, wy0 + 40, wx0 + 90, wy0 + 20, ink(5, '#FFFFFF', 70, boil=False))
    rect(c, wx0 - 30, wy1, wx1 + 30, wy1 + 26, '#E9E2D0')
    for sx, side in ((wx0 - 80, -1), (wx1 + 10, 1)):
        sw = math.sin(t * 2.6 + side) * 7
        cp = skia.Path(); cp.moveTo(sx, wy0 - 40); cp.lineTo(sx + 70, wy0 - 40); cp.cubicTo(sx + 80 + sw, wy0 + 200, sx + 60 + sw, wy1, sx + 74 + sw, wy1 + 70)
        cp.lineTo(sx + sw, wy1 + 70); cp.cubicTo(sx - 8 + sw, wy1, sx + 10, wy0 + 200, sx, wy0 - 40); cp.close()
        c.drawPath(cp, sp(linear(sx, 0, sx + 70, 0, [hx('#C9505A'), hx('#9C343E'), hx('#C9505A')])))
        for k_ in (22, 46): c.drawLine(sx + k_, wy0 - 30, sx + k_ + sw * .8, wy1 + 60, ink(3, '#7E2A33', boil=False))
        c.drawPath(cp, ink(LW))
    rect(c, wx0 - 100, wy0 - 54, wx1 + 100, wy0 - 34, '#4A3A30', LW, 8)
    return win

def s1(c, t):
    tc = twos(t); dx, dy = shake(t, 1.35, .6, 26); c.translate(dx, dy)
    flash = max(0, 1 - (t - 1.35) / .55) if t > 1.35 else 0
    room_bg(c); win = window_view(c, t, flash)
    beam = skia.Path(); beam.moveTo(1240, 150); beam.lineTo(1700, 150); beam.lineTo(1300, 1000); beam.lineTo(620, 1000); beam.close()
    c.drawPath(beam, sp(linear(0, 150, 0, 1000, [hx('#BFD0FF', 46), hx('#BFD0FF', 6)]), blend=skia.BlendMode.kPlus))
    # bedside table + lamp + alarm clock
    rect(c, 300, 600, 470, 800, '#8C5E3F', LW, 6); line(c, 300, 690, 470, 690); circ(c, 385, 738, 7, '#E9C46A', LW * .6)
    rat = math.sin(t * 70) * 6 if 0.15 < t < 1.3 else 0
    jump = -abs(math.sin((t - 1.35) * 9)) * 30 * max(0, 1 - (t - 1.35) * 2) if t > 1.35 else 0
    c.save(); c.translate(395 + rat, 548 + jump); c.rotate(rat * 1.5)
    circ(c, 0, 0, 50, '#D9262E'); circ(c, 0, 0, 37, '#FFF6DC', LW * .7)
    line(c, 0, 0, 0, -24, LW * .7); line(c, 0, 0, 16, 6, LW * .7)
    circ(c, -36, -42, 16, '#E9C46A', LW * .7); circ(c, 36, -42, 16, '#E9C46A', LW * .7)
    c.drawLine(-28, 44, -38, 60, ink(LW)); c.drawLine(28, 44, 38, 60, ink(LW))
    c.restore()
    if 0.15 < t < 1.3:
        for k in range(3):
            a = -0.9 + k * 0.9 - 1.57; r0 = 66 + (tc * 140 % 30)
            line(c, 395 + math.cos(a) * r0, 548 + math.sin(a) * r0, 395 + math.cos(a) * (r0 + 28), 548 + math.sin(a) * (r0 + 28), LW * .9, '#FFF6DC')
    # bed
    hb = skia.Path(); hb.addRRect(skia.RRect.MakeRectXY(skia.Rect(480, 500, 540, 800), 24, 24)); grad_shape(c, hb, '#8A5D40', '#5E3E2B', 500, 800)
    rect(c, 1450, 600, 1495, 800, '#6E4A33', LW, 14)
    mat = skia.Path(); mat.addRRect(skia.RRect.MakeRectXY(skia.Rect(510, 650, 1480, 760), 22, 22)); grad_shape(c, mat, '#FBF8F1', '#D9D2C2', 650, 760)
    rect(c, 500, 740, 1490, 800, '#7C5338', LW, 6)
    pw = skia.Path(); pw.addRRect(skia.RRect.MakeRectXY(skia.Rect(545, 598, 785, 690), 40, 40)); grad_shape(c, pw, '#FFFFFF', '#D8DDEA', 598, 690)
    c.drawLine(600, 640, 660, 650, ink(3, '#B9C0D3', boil=False))
    # hero: asleep -> sits up. pivot at hips
    s = 1.05; hipx, hipy = 960, 702; fx, fy = hipx, hipy + 128 * s
    k = back(K(tc, .5, .38), 2.2); ang = lerp(-86, 0, k)
    awake = tc > .34; turn = ease(K(tc, 1.42, .2))
    breath = math.sin(t * 3.2) * .5 + .5
    c.save(); c.clipRect(skia.Rect(-500, -500, W + 500, hipy + 30)); c.translate(hipx, hipy); c.rotate(ang); c.translate(-hipx, -hipy)
    if not awake:
        draw_char(c, fx, fy, s, HERO, face=0.0, eyes='closed', mouth='o' if breath > .5 else 'smile', arms=('down', 'down'), blush=.8, shadow=False, tilt=6)
    else:
        draw_char(c, fx, fy, s, HERO, face=lerp(0.15, 0.75, turn), eyes='shock' if tc < .5 else ('wide'),
                  mouth='o' if tc > 1.4 else ('open' if tc < .9 else 'flat'), brow=1.2,
                  arms=(('down', 'flail', K(tc, .5, .3)), ('down', 'flail', K(tc, .55, .3))),
                  squash=(.1 * math.sin(K(tc, .88, .25) * math.pi)) - (.08 * math.sin(K(tc, .34, .14) * math.pi)),
                  sweat=(t - 1.5) * 1.6 if t > 1.5 else -1, pupil=lerp(0, 1, turn), tilt=lerp(0, 6, turn), rim='#A9BCFF', shadow=False)
    c.restore()
    # blanket: up to chest while asleep, slides into lap
    kb = ease(K(tc, .5, .45)); bx0 = lerp(760, 905, kb); btop = lerp(600 - breath * 6, 690, kb)
    bl = skia.Path(); bl.moveTo(bx0, btop + 10); wv = math.sin(tc * 4) * 4
    bl.cubicTo(bx0 + 120, btop - 18 + wv, 1100, btop + 6, 1250, btop - 10 - wv); bl.cubicTo(1350, btop - 16, 1440, btop - 4, 1478, btop + 8)
    bl.lineTo(1495, 790); bl.cubicTo(1200, 800, 1000, 805, bx0 - 30, 795); bl.close()
    grad_shape(c, bl, '#4F7FC8', '#2D5596', btop, 800)
    c.save(); c.clipPath(bl, doAntiAlias=True)
    for i in range(-2, 9):
        for j in range(4): c.drawCircle(bx0 + i * 90 + (j % 2) * 45, btop + 30 + j * 45, 6, fp('#F2D36B', 200))
    for i in range(5): c.drawLine(bx0 + 80 + i * 120, btop + 10, bx0 + 60 + i * 120, 800, ink(4, '#244780', boil=False))
    c.restore(); c.drawPath(bl, ink(LW))
    fold = skia.Path(); fold.moveTo(bx0, btop + 10); fold.cubicTo(bx0 + 120, btop - 18, 1100, btop + 6, 1250, btop - 10)
    c.drawPath(fold, ink(12, '#F4EFE2', boil=False)); c.drawPath(fold, ink(LW * .6))
    if not awake:  # Zzz
        for i in range(3):
            u = (t * .9 + i / 3) % 1.0
            label(c, 'z', 690 + u * 90 + i * 8, 560 - u * 150, 40 + u * 30, '#FFF6DC', FONT_HAND, 'center', stroke=8, alpha=math.sin(u * math.pi), skew=0)
    if .34 < tc < .7:  # shock marks
        for a_ in (-2.4, -1.57, -0.7):
            r0 = 150; line(c, 740 + math.cos(a_) * r0, 570 + math.sin(a_) * r0, 740 + math.cos(a_) * (r0 + 46), 570 + math.sin(a_) * (r0 + 46), 8, '#FFF6DC')
    if t > 1.35:
        r = random.Random(5)
        for i in range(30):
            x = r.uniform(200, 1700); sp_ = r.uniform(300, 600); y = (t - 1.35) * sp_ - 20 + r.uniform(-40, 0)
            c.drawCircle(x + math.sin(t * 5 + i) * 8, y, r.uniform(3, 7), fp('#E8DFC8', 210))
    r = random.Random(12)  # dust motes in moonbeam
    for i in range(40):
        u = r.random(); x = lerp(1400, 900, u) + r.uniform(-200, 200) + math.sin(t * .8 + i) * 20; y = 200 + u * 750 + math.cos(t * .6 + i) * 15
        c.drawCircle(x, y, r.uniform(1.5, 3.5), fp('#E6EEFF', 120))
    night(c, [('pool', 860, 560, 560, .5), ('path', win, .9, 30), ('path', beam, .55, 40), ('pool', 1470, 380, 420, .45 + .5 * flash)], ambient='#3E4D94')
    if flash > 0: add_light(c, 1470, 380, 1000, '#FF8A3C', 130 * flash)
    add_light(c, 1600, 230, 300, '#C8D6FF', 40)

def s1_cam(t):
    k = ease(K(t, .35, .7))
    return lerp(1.55, 1.2, k), lerp(760, 1060, k), lerp(610, 520, k)

# ======================= SHOT 2: monster attack (2.1 - 4.95)
def draw_gorrak(c, x, y, s, t, roar=0.0, arm_r=0.0, arm_l=0.0, bob=0.0, lean=0.0):
    c.save(); c.translate(x, y - bob); c.scale(s, s); c.skew(lean, 0)
    PU, PD, BE, RIM = '#7B4FC9', '#4E2E92', '#B59BE6', '#FF9A5A'
    for lx in (-120, 120):
        lg = skia.Path(); lg.addRRect(skia.RRect.MakeRectXY(skia.Rect(lx - 72, -180, lx + 72, 0), 40, 40)); grad_shape(c, lg, PU, PD, -180, 0)
        for k in (-42, 0, 42): poly(c, [(lx + k - 15, -6), (lx + k + 15, -6), (lx + k, 24)], '#F3E7C8', LW * .7)
    def arm(side, a):
        c.save(); c.translate(side * 250, -520); c.rotate(side * (20 - a))
        ap = skia.Path(); ap.moveTo(-64, 0); ap.cubicTo(-90, 150, -76, 260, -46, 330); ap.lineTo(54, 330); ap.cubicTo(78, 240, 76, 140, 64, 0); ap.close()
        c.drawPath(ap, fp(PU)); c.save(); c.clipPath(ap, doAntiAlias=True); o = skia.Path(ap); o.offset(-side * 22, 0)
        c.drawPath(skia.Op(ap, o, skia.PathOp.kDifference_PathOp), fp(RIM if side > 0 else PD, 220)); c.restore(); c.drawPath(ap, ink(LW))
        for k in (-36, 0, 36): poly(c, [(k - 15, 322), (k + 15, 322), (k + side * 6, 378)], '#F3E7C8', LW * .7)
        c.restore()
    arm(-1, arm_l)
    for i in range(5):  # back spikes
        a = math.radians(200 + i * 35); poly(c, [(math.cos(a) * 250, -420 + math.sin(a) * 280), (math.cos(a) * 330, -420 + math.sin(a) * 340), (math.cos(a + .25) * 250, -420 + math.sin(a + .25) * 280)], '#F3E7C8', LW * .8)
    body = skia.Path(); body.addRRect(skia.RRect.MakeRectXY(skia.Rect(-280, -720, 280, -120), 230, 250))
    c.drawPath(body, sp(linear(0, -720, 0, -120, [hx('#8B5FDA'), hx(PU), hx('#6A40B4')]))); c.save(); c.clipPath(body, doAntiAlias=True)
    sh = skia.Path(body); sh.offset(-34, -18); c.drawPath(skia.Op(body, sh, skia.PathOp.kDifference_PathOp), fp(PD))
    rm = skia.Path(body); rm.offset(-24, 10); c.drawPath(skia.Op(body, rm, skia.PathOp.kDifference_PathOp), fp(RIM, 230))
    bel = skia.Path(); bel.addOval(skia.Rect(-170, -440, 170, -130)); c.drawPath(bel, fp(BE)); c.drawPath(bel, ink(LW * .8))
    for k in range(4): c.drawArc(skia.Rect(-120, -400 + k * 62, 120, -330 + k * 62), 20, 140, False, ink(4, '#8E72C8', boil=False))
    c.restore(); c.drawPath(body, ink(LW * 1.3))
    for sx in (-1, 1):
        hp = skia.Path(); hp.moveTo(sx * 120, -690); hp.cubicTo(sx * 190, -800, sx * 260, -820, sx * 300, -910); hp.cubicTo(sx * 240, -800, sx * 190, -740, sx * 200, -660); hp.close()
        grad_shape(c, hp, '#FFF8E6', '#CDBE98', -910, -660)
    mo = 30 + 100 * roar
    mp = skia.Path(); mp.moveTo(-150, -520); mp.cubicTo(-120, -520 + mo * 1.6, 120, -520 + mo * 1.6, 150, -520); mp.close()
    c.drawPath(mp, fp('#2A0F1E')); c.save(); c.clipPath(mp, doAntiAlias=True); c.drawOval(skia.Rect(-70, -520 + mo * .8, 70, -520 + mo * 1.6), fp('#B83A58')); c.restore(); c.drawPath(mp, ink(LW))
    for i in range(7):
        tx = -125 + i * 41; poly(c, [(tx - 14, -521), (tx + 14, -521), (tx, -488)], '#FFFFFF', LW * .6)
        if roar > .3 and i % 2: poly(c, [(tx - 12, -520 + mo * 1.2), (tx + 12, -520 + mo * 1.2), (tx, -520 + mo * 1.2 - 26)], '#FFFFFF', LW * .6)
    for (ex, ey, r) in ((-90, -610, 30), (0, -642, 37), (90, -610, 30)):
        circ(c, ex, ey, r, '#FFE45C', LW * .8); c.drawOval(skia.Rect(ex - 6, ey - r * .72, ex + 6, ey + r * .72), fp(INK))
        add_light(c, ex, ey, r * 3.4, '#FFD23C', 160)
    for sx in (-1, 1): line(c, sx * 40, -704, sx * 150, -662 + roar * 10, LW * 1.4)
    arm(1, arm_r)
    c.restore()

def s2(c, t):
    tt = 3.80 if 3.80 < t < 3.92 else t        # hit-stop after impact
    tc = twos(tt); dx = dy = 0
    for st in (2.3, 2.85): a, b = shake(t, st, .35, 14); dx += a; dy += b
    a, b = shake(t, 3.72, .8, 40); dx += a; dy += b
    c.translate(dx, dy)
    pan = (t - 2.1) * 30
    # sky
    grad_rect(c, -400, -300, W + 400, 1100, '#0E1238', '#8A3E5E')
    c.drawRect(skia.Rect(-400, 500, W + 400, 1000), sp(linear(0, 500, 0, 900, [hx('#FF8A4C', 0), hx('#FF8A4C', 120)])))
    c.drawCircle(300 - pan * .1, 190, 58, fp('#FFF2CC')); add_light(c, 300 - pan * .1, 190, 280, '#FFF2CC', 55)
    for i in range(5): puff(c, (i * 470 + t * 25) % 2400 - 300, 120 + (i % 2) * 90, 60, i, '#3A2E66', '#2A2150', 230, outline=False)
    for i, base in enumerate((420, 1500)):  # searchlights
        ang = math.sin(t * 1.4 + i * 2) * 0.35 + (0.25 if i == 0 else -0.25)
        cp = cone_path(0, 0, 20, 300, 1200); c.save(); c.translate(base - pan * .3, 900); c.rotate(math.degrees(math.pi + ang))
        c.drawPath(cp, sp(linear(0, 0, 0, 1200, [hx('#DDE7FF', 80), hx('#DDE7FF', 0)]), blend=skia.BlendMode.kPlus)); c.restore()
    far = cached('far', lambda cc: city_strip(cc, 840, 11, 200, 460, 70, 150, '#3A3270', '#2E285E', '#F7C873', .3, outline=False))
    blit(c, far, -pan * .25, 0, blur=4, alpha=.9)
    for i in range(3):  # smoke columns
        sx_ = 300 + i * 650 - pan * .4
        for j in range(7):
            u = ((t * .25 + j / 7) % 1.0); puff(c, sx_ + math.sin(u * 5 + i) * 40, 760 - u * 650, 50 + u * 90, i * 10 + j, '#3B3346', '#2A2433', 200 * (1 - u), outline=False)
    mid = cached('mid', lambda cc: city_strip(cc, 900, 15, 150, 330, 90, 170, '#2E336A', '#232858', '#FFC864', .35))
    blit(c, mid, -pan * .5, 0, blur=1.2)
    # monster
    walk = ease_out(K(t, 2.1, 1.0)); mx = lerp(1520, 1170, walk)
    bob = abs(math.sin((t - 2.1) / .55 * math.pi)) * 20 if t < 3.1 else 0
    raise_ = back(K(tc, 3.1, .45), 1.2); smash = ease(K(tt, 3.6, .12))
    arm_r = raise_ * 160 - smash * 180
    roar = ease(K(tc, 3.15, .3)) * (1 - .3 * smash) + .15 * math.sin(tc * 24) * K(tc, 3.4, .1)
    lean = .06 * raise_ * (1 - smash) - .08 * smash
    draw_gorrak(c, mx - pan * .7, 1010, .92, tc, roar=roar, arm_r=arm_r, arm_l=10 + 10 * math.sin(tc * 3), bob=bob, lean=lean)
    if 3.25 < t < 3.62:  # roar shock rings
        for i in range(3):
            u = ((t - 3.25) * 2.5 + i / 3) % 1.0; cx_, cy_ = mx - pan * .7, 1010 - 470 * .92
            c.drawOval(skia.Rect(cx_ - 120 - u * 260, cy_ - 50 - u * 110, cx_ + 120 + u * 260, cy_ + 50 + u * 110), ink(6, '#FFF6DC', 200 * (1 - u), boil=False))
    if 3.6 <= t < 3.73:  # smear arc on the swing
        cx_, cy_ = mx - pan * .7 + 230, 1010 - 480
        arc = skia.Path(); arc.addArc(skia.Rect(cx_ - 420, cy_ - 420, cx_ + 420, cy_ + 420), 190, 90)
        c.drawPath(arc, ink(140, '#9A70E0', 150, boil=False))
        for i in range(6): c.drawPath(arc, ink(4, '#FFFFFF', 150, boil=False)) if False else None
    # smashed building
    bx0, bx1, btop = 640 - pan * .7, 860 - pan * .7, 430
    broken = t > 3.72; r = random.Random(4)
    bp_ = skia.Path(); bp_.addRect(skia.Rect(bx0, btop + (90 if broken else 0), bx1, 1100))
    c.drawPath(bp_, sp(linear(bx0, 0, bx1, 0, [hx('#46508E'), hx('#2E3568')]))); c.drawPath(bp_, ink(LW))
    for i in range(4):
        for j in range(12):
            if r.random() < .5:
                wy = btop + 30 + j * 50
                if broken and wy < btop + 100: continue
                c.drawRect(skia.Rect(bx0 + 22 + i * 50, wy, bx0 + 40 + i * 50, wy + 24), fp('#FFD27A'))
    if not broken: rect(c, bx0 + 60, btop - 60, bx0 + 90, btop, '#3B4278', LW * .8)
    else:
        dt = tt - 3.72
        jag = [(bx0, btop + 90), (bx0 + 40, btop + 60), (bx0 + 90, btop + 100), (bx0 + 140, btop + 55), (bx0 + 190, btop + 95), (bx1, btop + 70), (bx1, btop + 120), (bx0, btop + 120)]
        poly(c, jag, '#3B4278')
        flame(c, bx0 + 70, btop + 90, 1.0, t, 1); flame(c, bx0 + 160, btop + 85, .7, t, 2)
        ring = ease_out(K(t, 3.72, .5))
        if ring < 1: c.drawOval(skia.Rect(bx0 + 110 - 700 * ring, btop + 70 - 160 * ring, bx0 + 110 + 700 * ring, btop + 70 + 160 * ring), ink(14 * (1 - ring) + 2, '#FFF6DC', 255 * (1 - ring), boil=False))
        rr = random.Random(9)
        for i in range(18):
            vx = rr.uniform(-560, 460); vy = rr.uniform(-820, -260); g = 1600
            x = bx0 + 110 + vx * dt; y = btop + 60 + vy * dt + .5 * g * dt * dt; sz = rr.uniform(18, 50)
            c.save(); c.translate(x, y); c.rotate(dt * rr.uniform(-500, 500))
            pp = skia.Path(); pp.moveTo(-sz / 2, -sz / 3); pp.lineTo(sz / 2, -sz / 2); pp.lineTo(sz / 3, sz / 2); pp.lineTo(-sz / 2, sz / 3); pp.close(); shape(c, pp, '#4A5290', LW * .8)
            c.restore()
        fa = max(0, 1 - dt / 1.3)
        for i in range(6):
            ang = -2.8 + i / 5 * 2.6; rad = 40 + dt * 260
            puff(c, bx0 + 110 + math.cos(ang) * rad, btop + 90 + math.sin(ang) * rad * .45, 44 + dt * 60, 30 + i, '#D9D3E6', '#9E95B8', 255 * fa)
        for i in range(30):  # sparks
            a_ = rr.uniform(0, 6.28); v = rr.uniform(300, 900); x = bx0 + 110 + math.cos(a_) * v * dt; y = btop + 70 + math.sin(a_) * v * dt + 500 * dt * dt
            if dt < .7: c.drawLine(x, y, x - math.cos(a_) * 18, y - math.sin(a_) * 18, ink(4, '#FFD27A', 255 * (1 - dt / .7), boil=False))
    # near buildings + street
    near = cached('near', lambda cc: (city_strip(cc, 1000, 21, 120, 300, 120, 220, '#2C3266', '#20254F', '#FFC864', .35, x0=-300, x1=560),
                                      city_strip(cc, 1000, 22, 140, 320, 120, 200, '#2C3266', '#20254F', '#FFC864', .35, x0=1350, x1=W + 400)))
    blit(c, near, -pan * .9, 0)
    for (fx_, fy_, fs_, sd) in ((200, 760, .8, 3), (1550, 720, .9, 4)): flame(c, fx_ - pan * .9, fy_, fs_, t, sd)
    grad_rect(c, -400, 960, W + 400, H + 300, '#3A3450', '#211E30', LW)
    for i in range(-2, 12): c.drawRect(skia.Rect(i * 220 - pan % 220, 1010, i * 220 + 110 - pan % 220, 1022), fp('#F2D36B'))
    for i, (sx, sp_) in enumerate(((1300, 520), (1420, 600), (1180, 470), (1550, 650))):
        x = sx - (t - 2.1) * sp_ - pan; ph2 = (t - 2.1) * 16 + i
        draw_char(c, x, 1050, .26, TEENS[i % 4], face=-.8, eyes='wide', mouth='open', arms=('flail', 'up'), legs=walk_legs(ph2, 60, 26), bob=8 * abs(math.sin(ph2)), lean=.12)
    r = random.Random(21)  # embers rising
    for i in range(50):
        u = (r.random() + t * r.uniform(.15, .35)) % 1.0; x = r.uniform(-100, W + 100) + math.sin(t * 2 + i) * 30 - pan * .6
        c.drawCircle(x, 1050 - u * 1000, r.uniform(2, 4.5), fp('#FFB45C', 230 * math.sin(u * math.pi)))
    night(c, [('pool', mx - pan * .7, 520, 760, .55), ('pool', 300, 200, 300, .5), ('oval', 960, 1040, 1200, 200, .45), ('pool', bx0 + 110, btop + 80, 420, .6 if broken else 0)], ambient='#5A64A8')
    if broken: add_light(c, bx0 + 110, btop + 80, 700, '#FF9A4A', 200 * max(0, 1 - (t - 3.72) / .9))
    # foreground traffic light: close + blurred, fast parallax (depth)
    c.save(); blur_begin(c, 9)
    fxl = 1700 - pan * 2.2
    rect(c, fxl, 300, fxl + 50, 1200, '#191A26', 0); rect(c, fxl - 40, 260, fxl + 90, 520, '#191A26', 0, 20)
    for j, cl in enumerate(('#FF4A4A', '#3A2A1A', '#2A3A1A')): c.drawCircle(fxl + 25, 310 + j * 70, 26, fp(cl))
    c.restore(); c.restore()
    add_light(c, fxl + 25, 310, 120, '#FF4A4A', 120)

# ======================= SHOT 3: heroes ranked like celebrities (4.95 - 7.45)
def s3(c, t):
    tc = twos(t)
    grad_rect(c, -300, -300, W + 300, 1100, '#0D1238', '#3A2C6A')
    bokeh(c, 5, 40, ['#FFD27A', '#FF8AB0', '#8AD0FF'], 14, 40, t, a=90, area=(-100, 0, W + 100, 700))
    sk = cached('sk3', lambda cc: city_strip(cc, 780, 31, 200, 480, 90, 160, '#262C5C', '#1C2148', '#F7C873', .35))
    blit(c, sk, 0, 0, blur=2.5)
    bx, by = 960, 245
    c.drawRect(skia.Rect(bx - 560, by - 260, bx + 560, by + 240), fp('#FFD66A', 90, blur=40))
    rect(c, bx - 520, by - 230, bx + 520, by + 210, '#1F1B2E', LW * 1.3, 24)
    rect(c, bx - 495, by - 205, bx + 495, by + 185, '#E9B53C', LW, 14)
    c.save(); cl = skia.Path(); cl.addRRect(skia.RRect.MakeRectXY(skia.Rect(bx - 495, by - 205, bx + 495, by + 185), 14, 14)); c.clipPath(cl, doAntiAlias=True)
    c.drawRect(skia.Rect(bx - 495, by - 205, bx + 495, by + 185), sp(radial(bx - 260, by, 700, [hx('#FFF1B8'), hx('#F2B53C'), hx('#C8781E')])))
    for i in range(16):
        a = i / 16 * 6.28 + t * .25
        p = skia.Path(); p.moveTo(bx - 260, by); p.lineTo(bx - 260 + math.cos(a) * 900, by + math.sin(a) * 900); p.lineTo(bx - 260 + math.cos(a + .18) * 900, by + math.sin(a + .18) * 900); p.close()
        c.drawPath(p, fp('#FFF6DC', 70))
    draw_char(c, bx - 260, by + 470, 1.35, AUREX, face=.2, eyes='half', mouth='grin', arms=('hip', 'gesture'), light=-1, shadow=False, rim='#FFF6DC')
    for i in range(0, 400, 6): c.drawLine(bx - 495, by - 205 + i, bx + 495, by - 205 + i, ink(1.5, '#000000', 25, boil=False))
    c.restore()
    c.drawPath(cl, ink(LW))
    label(c, '#1', bx + 40, by - 20, 210, '#FFF6DC', MARKER, 'left', stroke=18, skew=0)
    label(c, 'AUREX', bx + 50, by + 120, 96, '#B5302E', MARKER, 'left', stroke=12, stroke_col='#FFF6DC', skew=0)
    for i in range(30):
        x = bx - 510 + i / 30 * 1020; on = (i + int(t * 8)) % 3 == 0
        c.drawCircle(x, by - 218, 8, fp('#FFF2B0' if on else '#7A6A40'))
        if on: add_light(c, x, by - 218, 34, '#FFE38A', 130)
    # stage
    st = skia.Path(); st.addRRect(skia.RRect.MakeRectXY(skia.Rect(360, 830, 1560, 890), 10, 10)); grad_shape(c, st, '#9A2C3C', '#6A1E2A', 830, 890)
    rect(c, 340, 880, 1580, 940, '#521824', LW, 6)
    for i in range(12): c.drawCircle(400 + i * 102, 910, 7, fp('#FFE38A')); add_light(c, 400 + i * 102, 910, 26, '#FFE38A', 120)
    for j, x in enumerate((420, 1500)):
        sw = math.sin(t * 1.3 + j * 2) * 120
        c.drawPath(cone_path(x, -40, 50, 420, 900, (960 - x) * .55 + sw), sp(linear(0, 0, 0, 900, [hx('#FFF1C8', 120), hx('#FFF1C8', 8)]), blend=skia.BlendMode.kPlus))
        add_light(c, x, -40, 160, '#FFFFFF', 200)
    wv = int(tc * 6) % 2
    draw_char(c, 960, 850, .74, AUREX, face=-.15 + .1 * math.sin(tc * 2), eyes='closed' if blink(t, 2.0) else 'dot', mouth='grin',
              arms=('hip', 'wave' if wv else 'wave2'), bob=abs(math.sin(tc * 4)) * 6, sparkle=K(t, 5.4, .5) * 1.6,
              squash=.07 * math.sin(K(t, 4.95, .2) * math.pi), rim='#FFE9A8', blush=.4)
    r = random.Random(77)
    for i in range(80):
        x = r.uniform(0, W) + math.sin(t * 3 + i) * 30; y = (r.uniform(-300, 900) + (t - 4.95) * r.uniform(160, 300)) % 1100 - 60
        c.save(); c.translate(x, y); c.rotate(t * 200 + i * 40); c.scale(math.cos(t * 9 + i), 1)
        c.drawRect(skia.Rect(-8, -5, 8, 5), fp(r.choice(['#F2C14E', '#D9262E', '#FFFFFF', '#4AB0E8', '#B8F04A']))); c.restore()
    r = random.Random(3); fl = []
    for row, (yb, s) in enumerate(((1010, .9), (1110, 1.15))):
        for i in range(9):
            x = 80 + i * 225 + (110 if row else 0) + r.uniform(-30, 30); sp_ = TEENS[r.randrange(4)]
            jump = abs(math.sin(tc * 5 + i * 1.7 + row)) * 26 * s; hy = yb - jump
            c.save(); c.translate(x, hy); c.scale(s, s)
            rect(c, -80, -40, 80, 200, sp_['suit_d'], LW, 60)
            hc = sp_.get('hair_col', '#1D1A20') if sp_['hair'] != 'cap' else sp_['cap_col']
            circ(c, 0, -110, 82, hc); c.drawArc(skia.Rect(-74, -184, 74, -36), 200, 140, False, ink(7, '#FFE9A8', 160, boil=False))
            if r.random() < .55:
                arm_x = r.choice((-1, 1)) * 60; py = -250 - abs(math.sin(tc * 3 + i)) * 20
                c.drawLine(arm_x, -20, arm_x * 1.3, py + 50, ink(24, boil=False)); c.drawLine(arm_x, -20, arm_x * 1.3, py + 50, ink(14, sp_['skin'], boil=False))
                rect(c, arm_x * 1.3 - 24, py - 40, arm_x * 1.3 + 24, py + 40, '#22222A', LW * .8, 8)
                c.drawRect(skia.Rect(arm_x * 1.3 - 16, py - 30, arm_x * 1.3 + 16, py + 30), fp('#9FD6FF'))
                if (int(t * 12) + i * 3 + row * 5) % 11 == 0: fl.append((x + arm_x * 1.3 * s, hy + (py - 30) * s))
            c.restore()
    night(c, [('pool', 960, 300, 780, .78), ('pool', 960, 640, 540, .72), ('oval', 960, 860, 780, 130, .5)], ambient='#4A56A2')
    add_light(c, 960, 300, 700, '#FFD66A', 60)
    for (x, y) in fl:
        add_light(c, x, y, 140, '#FFFFFF', 255)
        for a in range(4):
            aa = a * math.pi / 2 + .4; line(c, x + math.cos(aa) * 20, y + math.sin(aa) * 20, x + math.cos(aa) * 70, y + math.sin(aa) * 70, 5, '#FFFFFF')
    # anamorphic flare from the spot sources
    for x in (420, 1500): c.drawRect(skia.Rect(x - 500, -46, x + 500, -34), fp('#9FC4FF', 60, blur=6, blend=skia.BlendMode.kPlus))

# ======================= SHOT 4: every 18-year-old gets a number (7.45 - 11.3)
SCAN = [(560, 8.15, '742'), (1160, 8.95, '518'), (1760, 9.75, '903')]
def scanner(c, x, num, roll_t, land_t, t, color='#7CF2E0', land_col='#B8F04A', y=880):
    body = skia.Path(); body.addRRect(skia.RRect.MakeRectXY(skia.Rect(x - 70, y - 380, x + 70, y), 18, 18))
    c.drawPath(body, sp(linear(x - 70, 0, x + 70, 0, [hx('#F4F7FC'), hx('#C9D1E0'), hx('#9EA8BE')]))); c.drawPath(body, ink(LW))
    c.drawLine(x - 50, y - 360, x - 50, y - 40, ink(6, '#FFFFFF', 160, boil=False))
    rect(c, x - 70, y - 60, x + 70, y, '#8A94AA', LW, 10)
    pad_on = t > roll_t
    rect(c, x - 52, y - 330, x + 52, y - 250, '#1E2A3A', LW * .8, 12)
    if pad_on: c.drawRect(skia.Rect(x - 44, y - 322, x + 44, y - 258), fp(color, 160 + 60 * math.sin(t * 20)))
    rect(c, x - 150, y - 610, x + 150, y - 430, '#141826', LW, 20); line(c, x, y - 430, x, y - 380, LW * 2)
    for i in range(0, 170, 6): c.drawLine(x - 146, y - 606 + i, x + 146, y - 606 + i, ink(1.5, '#FFFFFF', 12, boil=False))
    if t < roll_t: txt, cl = '---', '#5A6A80'
    elif t < land_t: txt, cl = '%03d' % random.Random(int(t * 24)).randint(0, 999), color
    else: txt, cl = num, land_col
    pk = pop(K(t, land_t, .3)) if t >= land_t else 1
    c.save(); c.translate(x, y - 485); c.scale(pk, pk); label(c, txt, 0, 0, 120, cl, MARKER, 'center', skew=0); c.restore()
    if pad_on: add_light(c, x, y - 290, 240, color, 100)
    add_light(c, x, y - 520, 320, cl, 50)

def hall(c, t):
    grad_rect(c, -400, -300, W + 600, 870, '#2E3A66', '#55659A')
    for i in range(-3, 18):
        p = skia.Path(); p.addRRect(skia.RRect.MakeRectXY(skia.Rect(i * 180, 190, i * 180 + 150, 760), 10, 10))
        c.drawPath(p, sp(linear(0, 190, 0, 760, [hx('#5A6AA0'), hx('#46558A')]))); c.drawPath(p, ink(LW * .6))
        c.drawRect(skia.Rect(i * 180 + 60, 200, i * 180 + 90, 750), fp('#9FC4FF', 40))
    for i in range(-3, 18): c.drawRect(skia.Rect(i * 180 + 20, 20, i * 180 + 140, 34), fp('#E8F0FF')); add_light(c, i * 180 + 80, 30, 120, '#CFE0FF', 60)
    label(c, 'BUREAU OF HEROES  ·  SPARK TEST', 1100, 150, 64, '#F2C14E', KALAM, 'center', skew=0, stroke=10)
    grad_rect(c, -400, 860, W + 600, H + 300, '#2B3150', '#1A1E34', LW)

def s4_scene(c, t, refl=False):
    tc = twos(t)
    for (x, lt, num) in SCAN: scanner(c, x, num, lt - .55, lt, t)
    for i, (x, lt, num) in enumerate(SCAN):
        sp_ = TEENS[i]; landed = tc >= lt; step = back(K(tc, 7.45 + i * .2, .4))
        cx = x - 260 + (1 - step) * -120
        hop = abs(math.sin(K(tc, lt + .05, .5) * math.pi)) * 70 if landed else 0
        draw_char(c, cx, 900 - hop, .95, sp_, face=.55 if not landed else .1, eyes='closed' if landed and tc < lt + .7 else ('dot' if not blink(t, 2.3, i) else 'closed'),
                  mouth='grin' if landed else 'flat', arms=('down', ('down', 'scan', K(tc, lt - .6, .25)) if not landed else ('scan', 'up', K(tc, lt + .05, .2))) if not landed else (('down', 'up', K(tc, lt + .05, .2)), ('scan', 'up', K(tc, lt + .05, .2))),
                  squash=.12 * math.sin(K(tc, lt, .2) * math.pi) - .1 * math.sin(K(tc, lt + .2, .3) * math.pi), bob=0,
                  sparkle=K(t, lt + .1, .45) * 1.7, brow=.6 if landed else 0, legs=walk_legs(tc * 12) if step < .95 else None, blush=.7 if landed else .2, shadow=not refl)
    hx_ = 2160 + (1 - back(K(tc, 9.9, .5))) * 260
    draw_char(c, hx_, 900, .95, HERO, face=-.5, eyes='dot', mouth='frown' if t > 10.6 else 'flat', arms=('fist', 'down'), sweat=(t - 10.3) * 1.5 if t > 10.3 else -1,
              pupil=-.6, brow_tilt=.8, legs=walk_legs(tc * 12) if t < 10.35 else None, squash=.05 * math.sin(K(tc, 10.8, .3) * math.pi), shadow=not refl)

def s4(c, t):
    hall(c, t)
    c.save(); c.clipRect(skia.Rect(-400, 900, W + 600, H + 300))   # glossy floor reflection
    c.saveLayerAlpha(None, 55); c.translate(0, 1800); c.scale(1, -1); s4_scene(c, t, True); c.restore(); c.restore()
    s4_scene(c, t)
    night(c, [('pool', 1100, 500, 1150, .62), ('oval', 1100, 900, 1300, 200, .5)], ambient='#6670B2')

def s4_cam(t): return 1.0 + .06 * ease(K(t, 7.45, 3.85)), lerp(620, 1500, ease(K(t, 7.45, 3.85))), 560

# ======================= SHOT 5: "...and your number is zero." (11.3 - 14.3)
def s5(c, t):
    tc = twos(t); zero_t = 12.74; zero = t >= zero_t
    dx, dy = shake(t, zero_t + .05, .55, 32); c.translate(dx, dy)
    bg = cached('hallblur', lambda cc: (cc.save(), cc.translate(W / 2, H / 2), cc.scale(1.5, 1.5), cc.translate(-W / 2 - 200, -H / 2 + 60), hall(cc, 0), cc.restore()))
    blit(c, bg, 0, 0, blur=14)
    bokeh(c, 9, 18, ['#9FF6EA', '#CFE0FF'], 20, 50, t, a=80)
    if zero:  # anime shock background: red radial + speed lines
        k = ease_out(K(t, zero_t, .25))
        c.drawRect(skia.Rect(-200, -200, W + 200, H + 200), sp(radial(760, 560, 1300, [hx('#FF6A5A', 230 * k), hx('#7A0E1E', 245 * k)])))
        r = random.Random(int(t * 12))
        for i in range(70):
            ang = r.uniform(0, 6.28); r0 = r.uniform(380, 600); wdt = r.uniform(4, 16)
            c.drawLine(760 + math.cos(ang) * r0, 560 + math.sin(ang) * r0, 760 + math.cos(ang) * 1700, 560 + math.sin(ang) * 1700, ink(wdt, '#2A0408', 180 * k, boil=False))
    sx = 1450
    rect(c, sx - 280, 140, sx + 280, 470, '#141826', LW * 1.3, 28)
    for i in range(0, 320, 7): c.drawLine(sx - 276, 144 + i, sx + 276, 144 + i, ink(1.5, '#FFFFFF', 12, boil=False))
    if not zero: rate = lerp(24, 5, K(t, 11.3, 1.4)); txt = '%03d' % random.Random(int(t * rate)).randint(1, 999); cl = '#7CF2E0'
    else: txt, cl = '0', '#FF4A4A'
    pk = pop(K(t, zero_t, .3)) if zero else 1
    c.save(); c.translate(sx, 380); c.scale(pk, pk); label(c, txt, 0, 0, 230, cl, MARKER, 'center', skew=0); c.restore()
    label(c, 'SPARK SCORE', sx, 200, 46, '#9AA4B8', KALAM, 'center', skew=0)
    line(c, sx, 470, sx, 600, LW * 3)
    pb = skia.Path(); pb.addRRect(skia.RRect.MakeRectXY(skia.Rect(sx - 130, 600, sx + 130, H + 60), 30, 30))
    c.drawPath(pb, sp(linear(sx - 130, 0, sx + 130, 0, [hx('#F4F7FC'), hx('#C9D1E0'), hx('#9EA8BE')]))); c.drawPath(pb, ink(LW * 1.3))
    rect(c, sx - 100, 660, sx + 100, 820, '#1E2A3A', LW, 18)
    padc = '#FF4A4A' if zero else '#7CF2E0'
    c.drawRect(skia.Rect(sx - 86, 674, sx + 86, 806), fp(padc, 170 + 60 * math.sin(t * 18)))
    gulp = .06 * math.sin(K(tc, 12.0, .3) * math.pi); react = back(K(tc, zero_t, .25), 2.4)
    draw_char(c, 760, 1400, 2.15, HERO, face=lerp(.55, .3, react), eyes='shock' if zero else ('closed' if blink(t, 2.3, .4) else 'dot'),
              mouth='o' if zero else 'flat', brow=lerp(0, 1.4, react), brow_tilt=.7 if not zero else -.4,
              arms=('down', 'scan'), squash=gulp - .08 * math.sin(K(tc, zero_t, .3) * math.pi), sweat=(t - 11.9) * 1.1 if t > 11.9 else -1,
              rim='#FF8080' if zero else '#9FF6EA', light=-1, pupil=.5 if not zero else 0, tilt=-4 * react, gloom=ease(K(t, zero_t + .2, .5)), shadow=False)
    if not zero: night(c, [('pool', 760, 560, 700, .55), ('pool', sx, 380, 520, .7), ('pool', sx, 740, 360, .6)], ambient='#5E68A8')
    add_light(c, sx, 740, 380, padc, 90); add_light(c, sx, 330, 420, cl, 50)
    if zero:
        st = K(t, zero_t + .05, .2); sc = lerp(2.6, 1, ease_out(st))
        if st > 0:
            c.save(); c.translate(1130, 900); c.rotate(-10); c.scale(sc, sc); al = 255 * min(1, st * 2)
            c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(-300, -110, 300, 110), 22, 22), fp('#FFF6DC', al * .85))
            p = skia.Path(); p.addRRect(skia.RRect.MakeRectXY(skia.Rect(-300, -110, 300, 110), 22, 22)); c.drawPath(p, ink(16, RED, al, boil=False))
            p2 = skia.Path(); p2.addRRect(skia.RRect.MakeRectXY(skia.Rect(-276, -86, 276, 86), 16, 16)); c.drawPath(p2, ink(6, RED, al, boil=False))
            label(c, 'ZERO', 0, 62, 170, RED, MARKER, 'center', skew=0, alpha=al / 255)
            c.restore()
    if t > END - .45: c.drawRect(skia.Rect(-200, -200, W + 200, H + 200), fp((0, 0, 0), 255 * K(t, END - .45, .45)))

def s5_cam(t):
    z = 1.0 + .05 * ease(K(t, 11.3, 1.4)) + .16 * ease_out(K(t, 12.74, .18))
    return z, 900, 560

# shot list: (name, start, end, draw, cam(t)->(zoom,fx,fy), whip_in, whip_out)
SHOTS = [
    ('s1', 0.0, 2.1, s1, s1_cam, False, True),
    ('s2', 2.1, 4.95, s2, lambda t: (lerp(1.04, 1.12, ease(K(t, 2.1, 2.85))), 960, 560), True, True),
    ('s3', 4.95, 7.45, s3, lambda t: (lerp(1.0, 1.1, ease(K(t, 4.95, 2.5))), 960, 520), True, False),
    ('s4', 7.45, 11.3, s4, s4_cam, False, False),
    ('s5', 11.3, END, s5, s5_cam, False, False),
]

def frame(surf, t):
    for (name, a, b, fn, cam, wi, wo) in SHOTS:
        if a <= t < b or name == 's5': break
    set_boil(t); c = surf.getCanvas(); n0, n1 = round(a * FPS), round(b * FPS); f = round(t * FPS)
    wx = sig = 0
    if wo and n1 - f <= 5: wx = -((6 - (n1 - f)) ** 2) * 34; sig = (6 - (n1 - f)) * 16
    if wi and f - n0 < 4: wx = (4 - (f - n0)) ** 2 * 52; sig = (4 - (f - n0)) * 18
    zz, fx, fy = cam(t)
    c.clear(C((0, 0, 0))); c.save(); c.translate(W / 2 + wx, H / 2); c.scale(zz, zz); c.translate(-fx, -fy)
    fn(c, t); c.restore()
    finish(surf, bloom=.45); vignette(c, .5)
    if any(0 <= t - it < 2.5 / FPS for it in IMPACTS): impact(surf)
    grain(c, t)
    if sig:
        img = surf.makeImageSnapshot(); c.clear(C((0, 0, 0)))
        bp = skia.Paint(); bp.setImageFilter(skia.ImageFilters.Blur(sig, 0.01, skia.TileMode.kClamp)); c.drawImage(img, 0, 0, skia.SamplingOptions(), bp)

if __name__ == '__main__':
    surf = skia.Surface(W, H)
    if len(sys.argv) > 2 and sys.argv[1] == 'stills':
        for s in sys.argv[2].split(','):
            frame(surf, float(s)); surf.makeImageSnapshot().save(os.path.join(OUT, f'st_{float(s):05.2f}.png'), skia.kPNG)
        sys.exit()
    n = round(END * FPS)
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgra', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                          '-c:v', 'libx264', '-crf', '17', '-preset', 'medium', '-pix_fmt', 'yuv420p', os.path.join(OUT, 'video.mp4')], stdin=subprocess.PIPE)
    for f in range(n):
        frame(surf, f / FPS); p.stdin.write(surf.makeImageSnapshot().toarray(colorType=skia.kBGRA_8888_ColorType).tobytes())
        if f % 48 == 0: print('frame', f, flush=True)
    p.stdin.close(); p.wait(); print('done')
