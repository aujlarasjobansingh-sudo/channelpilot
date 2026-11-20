# EP01 hook preview in 2D ink style, cut to the user's voiceover (0 - 14.3 s)
# usage: python3 preview.py [stills t1,t2,...]   (no args = render all shots)
import sys, math, random, subprocess, os
from kit2d import *

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out'); os.makedirs(OUT, exist_ok=True)
END = 14.3

def shake(t, t0, dur=0.45, amp=22):
    if t < t0 or t > t0 + dur: return 0, 0
    k = (1 - (t - t0) / dur) ** 2 * amp; f = int(t * FPS)
    r = random.Random(f * 7 + int(t0 * 100)); return r.uniform(-k, k), r.uniform(-k, k)

def sky(c, top='#1B2350', bot='#4A3E7A'):
    c.drawRect(skia.Rect(-200, -200, W + 200, H + 200), sp(linear(0, 0, 0, H, [hx(top), hx(bot)])))

def city_strip(c, y_base, seed, hmin, hmax, wmin, wmax, body, win, lit=0.35, outline=True, x0=-300, x1=W + 300):
    r = random.Random(seed); x = x0
    while x < x1:
        w = r.uniform(wmin, wmax); h = r.uniform(hmin, hmax)
        rect(c, x, y_base - h, x + w, y_base + 40, body, LW if outline else 0)
        cols = max(1, int(w // 34)); rows = int(h // 44)
        for i in range(cols):
            for j in range(rows):
                if r.random() < lit:
                    wx = x + 12 + i * (w - 24) / cols; wy = y_base - h + 18 + j * 44
                    c.drawRect(skia.Rect(wx, wy, wx + 14, wy + 20), fp(win))
        x += w + r.uniform(-6, 18)

_cache = {}
def cached(key, fn):
    if key not in _cache:
        s = skia.Surface(W, H); cc = s.getCanvas(); cc.clear(C((0, 0, 0), 0)); fn(cc); _cache[key] = s.makeImageSnapshot()
    return _cache[key]

# ======================= SHOT 1: wake up (0 - 2.1)
def s1(c, t):
    tc = twos(t); dx, dy = shake(t, 1.35, .6, 26); c.translate(dx, dy)
    flash = max(0, 1 - (t - 1.35) / .5) if t > 1.35 else 0
    # wall + floor
    c.drawRect(skia.Rect(-100, -100, W + 100, 820), fp('#6F86B8'))
    for i in range(-2, 30): c.drawRect(skia.Rect(i * 80, -100, i * 80 + 40, 820), fp('#6A80B2'))
    rect(c, -100, 800, W + 100, H + 100, '#6B4A3A')
    for i in range(12): line(c, -100, 840 + i * 30, W + 100, 840 + i * 30, 3, '#5A3D30')
    rect(c, -100, 790, W + 100, 812, '#8A6A55', LW)
    # window (right)
    wx0, wy0, wx1, wy1 = 1240, 150, 1700, 600
    win = skia.Path(); win.addRect(skia.Rect(wx0, wy0, wx1, wy1))
    c.save(); c.clipPath(win)
    sky(c, '#141B44', '#3D2F6E'); c.drawCircle(1600, 230, 34, fp('#FFF4D0'))
    city_strip(c, 600, 3, 80, 260, 50, 110, '#232A52', '#FFD27A', .4)
    if flash > 0: c.drawRect(skia.Rect(wx0, wy0, wx1, wy1), fp('#FF8A3C', 220 * flash))
    c.restore()
    shape(c, win, fp((0, 0, 0), 0), LW * 1.4)
    line(c, (wx0 + wx1) / 2, wy0, (wx0 + wx1) / 2, wy1); line(c, wx0, (wy0 + wy1) / 2, wx1, (wy0 + wy1) / 2)
    rect(c, wx0 - 30, wy1, wx1 + 30, wy1 + 26, '#E9E2D0')
    for sx, side in ((wx0 - 70, -1), (wx1 + 10, 1)):
        sw = math.sin(tc * 3 + side) * 6
        poly(c, [(sx, wy0 - 40), (sx + 60, wy0 - 40), (sx + 60 + sw, wy1 + 60), (sx + sw, wy1 + 60)], '#B8424A')
    rect(c, wx0 - 90, wy0 - 52, wx1 + 90, wy0 - 34, '#4A3A30', LW, 8)
    # poster of the #1 hero + picture frame (tilts on boom)
    c.save(); c.translate(330, 260); c.rotate(-4 + (math.sin(t * 30) * 6 * flash))
    rect(c, -110, -140, 110, 140, '#F2C14E', LW); rect(c, -90, -120, 90, 70, '#B5302E', LW * .7)
    label(c, '#1', 0, 120, 52, '#18161B', MARKER, 'center', skew=0)
    c.restore()
    # bedside table + alarm clock (rattles before boom)
    rect(c, 300, 600, 470, 800, '#8C5E3F', LW, 6); line(c, 300, 690, 470, 690)
    circ(c, 385, 690 + 48, 6, '#E9C46A', LW * .6)
    rat = math.sin(t * 70) * 6 if 0.15 < t < 1.3 else 0
    c.save(); c.translate(385 + rat, 545); c.rotate(rat * 1.5)
    circ(c, 0, 0, 52, '#D9262E'); circ(c, 0, 0, 38, '#FFF6DC', LW * .7)
    line(c, 0, 0, 0, -24, LW * .7); line(c, 0, 0, 16, 6, LW * .7)
    circ(c, -38, -44, 16, '#E9C46A', LW * .7); circ(c, 38, -44, 16, '#E9C46A', LW * .7)
    line(c, -30, 46, -40, 62); line(c, 30, 46, 40, 62)
    c.restore()
    if 0.15 < t < 1.3:
        for k in range(3):
            a = -0.9 + k * 0.9; r0 = 70 + (tc * 140 % 30)
            line(c, 385 + math.cos(a - 1.57) * r0, 545 + math.sin(a - 1.57) * r0, 385 + math.cos(a - 1.57) * (r0 + 26), 545 + math.sin(a - 1.57) * (r0 + 26), LW * .8, '#FFF6DC')
    # bed
    rect(c, 480, 560, 520, 800, '#6E4A33', LW, 10)
    rect(c, 500, 660, 1480, 760, '#F1EEE6', LW, 18)
    rect(c, 500, 740, 1480, 800, '#7C5338', LW, 6)
    rect(c, 1450, 620, 1490, 800, '#6E4A33', LW, 10)
    oval(c, 540, 600, 760, 690, '#FFFFFF')
    # hero sits up: pivot at hips
    s = 1.05; hipx, hipy = 960, 700; fx, fy = hipx, hipy + 128 * s
    k = back(K(tc, .5, .38), 2.2) if tc < 1.5 else 1.0
    ang = lerp(-84, 0, k)
    wide = tc > .34
    turn = ease(K(tc, 1.42, .2))
    c.save(); c.clipRect(skia.Rect(-500, -500, W + 500, hipy + 30)); c.translate(hipx, hipy); c.rotate(ang); c.translate(-hipx, -hipy)
    draw_char(c, fx, fy, s, HERO, face=lerp(0.2, 0.75, turn), eyes='wide' if wide else ('closed'),
              mouth='o' if tc > 1.4 else ('open' if wide and tc < .9 else 'flat'), brow=1.0 if wide else 0,
              arms=(('down', 'flail', K(tc, .5, .3)) if tc < 1.4 else 'flail', ('down', 'flail', K(tc, .55, .3))),
              squash=(0.08 * math.sin(K(tc, .88, .25) * math.pi)), sweat=(t - 1.5) * 1.6 if t > 1.5 else -1,
              pupil=lerp(0, 1, turn), tilt=lerp(0, 6, turn), rim='#9FB4FF')
    c.restore()
    # blanket over legs
    bl = skia.Path(); bl.moveTo(900, 690); wv = math.sin(tc * 4) * 4
    bl.cubicTo(900, 640 + wv, 1100, 680, 1250, 650 - wv); bl.cubicTo(1350, 640, 1440, 660, 1475, 670)
    bl.lineTo(1490, 780); bl.lineTo(880, 790); bl.close(); shape(c, bl, '#3E6DB5')
    for i in range(5): line(c, 900 + i * 120, 680, 880 + i * 120, 780, 3, '#2F5592')
    # dust from ceiling after boom
    if t > 1.35:
        r = random.Random(5)
        for i in range(26):
            x = r.uniform(200, 1700); sp_ = r.uniform(300, 600); y = (t - 1.35) * sp_ - 20 + r.uniform(-40, 0)
            c.drawCircle(x + math.sin(t * 5 + i) * 8, y, r.uniform(3, 7), fp('#E8DFC8', 200))
    night(c, [('pool', 860, 520, 520, .55), ('path', win, .9, 30), ('pool', 1470, 380, 420, .5 + .5 * flash)], ambient='#46559A')
    if flash > 0: add_light(c, 1470, 380, 900, '#FF8A3C', 120 * flash)
    add_light(c, 1470, 380, 500, '#9FB4FF', 40)

# ======================= SHOT 2: monster attack (2.1 - 4.95)
def draw_gorrak(c, x, y, s, t, roar=0.0, arm_r=0.0, arm_l=0.0, bob=0.0, lean=0.0):
    c.save(); c.translate(x, y - bob); c.scale(s, s); c.skew(lean, 0)
    PU, PD, BE = '#7B4FC9', '#5A36A0', '#B59BE6'
    for lx in (-120, 120):  # legs
        rect(c, lx - 70, -170, lx + 70, 0, PU, LW, 40)
        for k in (-40, 0, 40): poly(c, [(lx + k - 14, -6), (lx + k + 14, -6), (lx + k, 22)], '#F3E7C8', LW * .7)
    def arm(side, a):
        c.save(); c.translate(side * 250, -520); c.rotate(side * (20 - a))
        ap = skia.Path(); ap.moveTo(-60, 0); ap.cubicTo(-80, 150, -70, 260, -40, 330); ap.lineTo(50, 330); ap.cubicTo(70, 240, 70, 140, 60, 0); ap.close()
        shape(c, ap, PU)
        for k in (-34, 0, 34): poly(c, [(k - 14, 322), (k + 14, 322), (k + side * 6, 372)], '#F3E7C8', LW * .7)
        c.restore()
    arm(-1, arm_l)
    body = skia.Path(); body.addRRect(skia.RRect.MakeRectXY(skia.Rect(-280, -720, 280, -120), 230, 250))
    c.drawPath(body, fp(PU)); c.save(); c.clipPath(body, doAntiAlias=True)
    sh = skia.Path(body); sh.offset(-30, -16); c.drawPath(skia.Op(body, sh, skia.PathOp.kDifference_PathOp), fp(PD))
    oval(c, -170, -440, 170, -130, BE, LW * .8)
    for k in range(4): line(c, -110, -380 + k * 60, 110, -380 + k * 60, 3, '#9A7FD0')
    c.restore(); c.drawPath(body, ink(LW * 1.2))
    for sx in (-1, 1):  # horns
        hp = skia.Path(); hp.moveTo(sx * 120, -690); hp.cubicTo(sx * 190, -800, sx * 260, -820, sx * 300, -900); hp.cubicTo(sx * 240, -800, sx * 190, -740, sx * 200, -660); hp.close()
        shape(c, hp, '#F3E7C8')
    # mouth
    mo = 30 + 90 * roar
    mp = skia.Path(); mp.moveTo(-150, -520); mp.cubicTo(-120, -520 + mo * 1.6, 120, -520 + mo * 1.6, 150, -520); mp.close()
    shape(c, mp, '#2A0F1E')
    for i in range(7):
        tx = -125 + i * 41; poly(c, [(tx - 14, -520), (tx + 14, -520), (tx, -490)], '#FFFFFF', LW * .6)
    # eyes (3) glowing
    for (ex, ey, r) in ((-90, -610, 30), (0, -640, 36), (90, -610, 30)):
        circ(c, ex, ey, r, '#FFE45C', LW * .8); c.drawOval(skia.Rect(ex - 6, ey - r * .7, ex + 6, ey + r * .7), fp(INK))
        add_light(c, ex, ey, r * 3.2, '#FFD23C', 150)
    for sx in (-1, 1): line(c, sx * 40, -700, sx * 140, -660 + roar * 10, LW * 1.2)
    arm(1, arm_r)
    c.restore()

def s2(c, t):
    lt = t - 2.1; tc = twos(t)
    steps = [2.3, 2.85]; dx = dy = 0
    for st in steps: a, b = shake(t, st, .35, 14); dx += a; dy += b
    a, b = shake(t, 3.72, .7, 34); dx += a; dy += b
    c.translate(dx, dy)
    sky(c, '#141A45', '#6B3E6E')
    c.drawCircle(300, 200, 60, fp('#FFF2CC')); add_light(c, 300, 200, 260, '#FFF2CC', 50)
    # searchlights
    for i, base in enumerate((420, 1500)):
        ang = math.sin(t * 1.4 + i * 2) * 0.35 + (0.25 if i == 0 else -0.25)
        cp = cone_path(0, 0, 20, 260, 1100); c.save(); c.translate(base, 900); c.rotate(math.degrees(math.pi + ang))
        c.drawPath(cp, sp(linear(0, 0, 0, 1100, [hx('#DDE7FF', 90), hx('#DDE7FF', 0)]), blend=skia.BlendMode.kPlus)); c.restore()
    far = cached('far', lambda cc: city_strip(cc, 820, 11, 160, 420, 70, 150, '#2A2F60', '#F7C873', .3, outline=False))
    bp = skia.Paint(); bp.setImageFilter(skia.ImageFilters.Blur(3, 3)); c.drawImage(far, 0, 0, skia.SamplingOptions(), bp)
    # monster walks in from right, then smashes
    walk = ease_out(K(t, 2.1, 1.0)); mx = lerp(1500, 1160, walk)
    ph = (t - 2.1) / .55 * math.pi
    bob = abs(math.sin(ph)) * 18 if t < 3.1 else 0
    raise_ = back(K(tc, 3.15, .4), 1.2); smash = ease(K(t, 3.58, .14))
    arm_r = raise_ * 150 - smash * 170
    roar = ease(K(tc, 3.2, .3)) * (1 - .3 * smash) + .2 * math.sin(tc * 20) * K(tc, 3.4, .1)
    draw_gorrak(c, mx, 1000, .92, tc, roar=roar, arm_r=arm_r, arm_l=10 + 10 * math.sin(tc * 3), bob=bob, lean=-.05 * smash)
    # smashed building (left of monster)
    bx0, bx1, btop = 640, 860, 430
    broken = t > 3.72
    r = random.Random(4)
    rect(c, bx0, btop + (90 if broken else 0), bx1, 1100, '#3B4278', LW)
    for i in range(4):
        for j in range(12):
            if r.random() < .5:
                wy = btop + 30 + j * 50
                if broken and wy < btop + 100: continue
                c.drawRect(skia.Rect(bx0 + 22 + i * 50, wy, bx0 + 40 + i * 50, wy + 24), fp('#FFD27A'))
    if not broken:
        rect(c, bx0 + 60, btop - 60, bx0 + 90, btop, '#3B4278', LW * .8)
    else:
        jag = [(bx0, btop + 90), (bx0 + 40, btop + 60), (bx0 + 90, btop + 100), (bx0 + 140, btop + 55), (bx0 + 190, btop + 95), (bx1, btop + 70), (bx1, btop + 120), (bx0, btop + 120)]
        poly(c, jag, '#3B4278')
        rr = random.Random(9); dt = t - 3.72
        for i in range(16):
            vx = rr.uniform(-520, 420); vy = rr.uniform(-760, -260); g = 1500
            x = bx0 + 110 + vx * dt; y = btop + 60 + vy * dt + .5 * g * dt * dt; sz = rr.uniform(18, 46)
            c.save(); c.translate(x, y); c.rotate(dt * rr.uniform(-500, 500)); rect(c, -sz / 2, -sz / 2, sz / 2, sz / 2, '#4A5290', LW * .8); c.restore()
        fa = max(0, 1 - dt / 1.1)
        for i in range(7):  # dust puffs drifting out and fading
            ang = -2.6 + i / 6 * 2.2; rad = 50 + dt * 300
            c.drawCircle(bx0 + 110 + math.cos(ang) * rad, btop + 80 + math.sin(ang) * rad * .5, 46 + dt * 70, fp('#8E8AA6', 200 * fa))
    # near buildings + street
    city_strip(c, 1000, 21, 120, 300, 120, 220, '#2C3266', '#FFC864', .35, x0=-200, x1=560)
    city_strip(c, 1000, 22, 140, 320, 120, 200, '#2C3266', '#FFC864', .35, x0=1350, x1=W + 200)
    rect(c, -200, 960, W + 200, H + 200, '#35304A', LW)
    for i in range(10): rect(c, i * 220 + ((t * 0) % 220), 1010, i * 220 + 110, 1022, '#F2D36B', 0)
    # tiny civilians running away (left)
    for i, (sx, sp_) in enumerate(((1300, 520), (1420, 600), (1180, 470), (1550, 650))):
        x = sx - (t - 2.1) * sp_; ph2 = (t - 2.1) * 16 + i
        draw_char(c, x, 1050, .26, TEENS[i % 4], face=-.8, eyes='wide', mouth='open', arms=('flail', 'up'), legs=walk_legs(ph2, 60, 26), bob=8 * abs(math.sin(ph2)), lean=.12)
    night(c, [('pool', mx, 520, 700, .55), ('pool', 300, 200, 300, .5), ('oval', 960, 1040, 1100, 160, .4)], ambient='#5A64A8')
    if broken: add_light(c, bx0 + 110, btop + 80, 500, '#FF9A4A', 150 * max(0, 1 - (t - 3.72) / .8))

# ======================= SHOT 3: heroes ranked like celebrities (4.95 - 7.45)
def s3(c, t):
    tc = twos(t)
    sky(c, '#121842', '#3A2C6A')
    city_strip(c, 760, 31, 200, 480, 90, 160, '#262C5C', '#F7C873', .35)
    # billboard
    bx, by = 960, 245
    rect(c, bx - 520, by - 230, bx + 520, by + 210, '#1F1B2E', LW * 1.3, 24)
    rect(c, bx - 495, by - 205, bx + 495, by + 185, '#E9B53C', LW, 14)
    c.save(); c.clipRect(skia.Rect(bx - 495, by - 205, bx + 495, by + 185))
    for i in range(14):
        a = i / 14 * 6.28 + t * .3; c.drawPath(cone_path(0, 0, 0, 260, 900), sp(linear(0, 0, 0, 900, [hx('#FFF1B8', 120), hx('#FFF1B8', 0)]))) if False else None
        p = skia.Path(); p.moveTo(bx - 260, by); p.lineTo(bx - 260 + math.cos(a) * 900, by + math.sin(a) * 900); p.lineTo(bx - 260 + math.cos(a + .2) * 900, by + math.sin(a + .2) * 900); p.close()
        c.drawPath(p, fp('#F7CF5E'))
    draw_char(c, bx - 260, by + 470, 1.35, AUREX, face=.2, eyes='half', mouth='grin', arms=('hip', 'gesture'), light=-1)
    c.restore()
    rect(c, bx - 495, by - 205, bx + 495, by + 185, fp((0, 0, 0), 0), LW)
    label(c, '#1', bx + 40, by - 20, 210, '#FFF6DC', MARKER, 'left', stroke=18, skew=0)
    label(c, 'AUREX', bx + 50, by + 120, 96, '#B5302E', MARKER, 'left', stroke=12, stroke_col='#FFF6DC', skew=0)
    for k in range(5):  # stars
        sx_, sy_ = bx + 400, by - 150 + k * 0
    # marquee bulbs blink
    for i in range(30):
        u = i / 30; x = bx - 510 + u * 1020
        on = (i + int(t * 8)) % 3 == 0
        c.drawCircle(x, by - 218, 8, fp('#FFF2B0' if on else '#7A6A40'))
        if on: add_light(c, x, by - 218, 30, '#FFE38A', 120)
    # stage + Aurex waving
    rect(c, 360, 830, 1560, 890, '#7A2230', LW, 10); rect(c, 340, 880, 1580, 940, '#521824', LW, 6)
    for x in (520, 1400):  # spotlights cones
        c.drawPath(cone_path(x, 0, 40, 380, 780, (960 - x) * .5), sp(linear(0, 0, 0, 780, [hx('#FFF1C8', 110), hx('#FFF1C8', 10)]), blend=skia.BlendMode.kPlus))
    wv = int(tc * 6) % 2
    draw_char(c, 960, 850, .74, AUREX, face=-.15 + .1 * math.sin(tc * 2), eyes='closed' if blink(t, 2.0) else 'dot', mouth='grin',
              arms=('hip', 'wave' if wv else 'wave2'), bob=abs(math.sin(tc * 4)) * 6, sparkle=K(t, 5.4, .5) * 1.6,
              squash=.07 * math.sin(K(t, 4.95, .2) * math.pi), rim='#FFE9A8')
    # confetti
    r = random.Random(77)
    for i in range(70):
        x = r.uniform(0, W) + math.sin(t * 3 + i) * 30; y = (r.uniform(-300, 900) + (t - 4.95) * r.uniform(160, 300)) % 1100 - 60
        c.save(); c.translate(x, y); c.rotate(t * 200 + i * 40); c.drawRect(skia.Rect(-7, -4, 7, 4), fp(r.choice(['#F2C14E', '#D9262E', '#FFFFFF', '#4AB0E8', '#B8F04A']))); c.restore()
    # crowd (backs of heads) + phones
    r = random.Random(3)
    fl = []
    for row, (yb, s) in enumerate(((1010, .9), (1110, 1.15))):
        for i in range(9):
            x = 80 + i * 225 + (110 if row else 0) + r.uniform(-30, 30); sp_ = TEENS[r.randrange(4)]
            jump = abs(math.sin(tc * 5 + i * 1.7 + row)) * 26 * s
            hy = yb - jump
            c.save(); c.translate(x, hy); c.scale(s, s)
            rect(c, -80, -40, 80, 200, sp_['suit'], LW, 60)
            circ(c, 0, -110, 82, sp_.get('hair_col', '#1D1A20') if sp_['hair'] != 'cap' else sp_['cap_col'])
            if r.random() < .55:
                arm_x = r.choice((-1, 1)) * 60; py = -250 - abs(math.sin(tc * 3 + i)) * 20
                line(c, arm_x, -20, arm_x * 1.3, py + 50, LW); circ(c, arm_x * 1.3, py + 50, 14, sp_['skin'], LW * .8)
                rect(c, arm_x * 1.3 - 24, py - 40, arm_x * 1.3 + 24, py + 40, '#22222A', LW * .8, 8)
                c.drawRect(skia.Rect(arm_x * 1.3 - 16, py - 30, arm_x * 1.3 + 16, py + 30), fp('#9FD6FF'))
                if (int(t * 12) + i * 3 + row * 5) % 11 == 0: fl.append((x + arm_x * 1.3 * s, hy + (py - 30) * s))
            c.restore()
    night(c, [('pool', 960, 300, 760, .75), ('pool', 960, 640, 520, .7), ('oval', 960, 840, 760, 120, .5)], ambient='#4E5AA4')
    add_light(c, 960, 300, 700, '#FFD66A', 60)
    for (x, y) in fl:  # phone camera flashes
        add_light(c, x, y, 120, '#FFFFFF', 255)
        for a in range(4):
            aa = a * math.pi / 2 + .4; line(c, x + math.cos(aa) * 20, y + math.sin(aa) * 20, x + math.cos(aa) * 60, y + math.sin(aa) * 60, 5, '#FFFFFF')

# ======================= SHOT 4: every 18-year-old gets a number (7.45 - 11.3)
SCAN = [(560, 8.15, '742'), (1160, 8.95, '518'), (1760, 9.75, '903')]
def scanner(c, x, num, roll_t, land_t, t, color='#7CF2E0', land_col='#B8F04A', y=880):
    rect(c, x - 70, y - 380, x + 70, y, '#D7DDE8', LW, 18); rect(c, x - 70, y - 60, x + 70, y, '#9AA4B8', LW, 10)
    pad_on = t > roll_t
    rect(c, x - 52, y - 330, x + 52, y - 250, '#1E2A3A', LW * .8, 12)
    if pad_on: c.drawRect(skia.Rect(x - 44, y - 322, x + 44, y - 258), fp(color, 160 + 60 * math.sin(t * 20)))
    # display
    rect(c, x - 150, y - 610, x + 150, y - 430, '#1B1E2C', LW, 20); line(c, x, y - 430, x, y - 380, LW * 2)
    if t < roll_t: txt, cl = '---', '#5A6A80'
    elif t < land_t: txt, cl = '%03d' % random.Random(int(t * 24)).randint(0, 999), color
    else: txt, cl = num, land_col
    pk = pop(K(t, land_t, .3)) if t >= land_t else 1
    c.save(); c.translate(x, y - 485); c.scale(pk, pk); label(c, txt, 0, 0, 120 if len(txt) < 4 else 110, cl, MARKER, 'center', skew=0); c.restore()
    if pad_on: add_light(c, x, y - 290, 220, color, 90)
    add_light(c, x, y - 520, 300, cl, 45)

def hall(c, t, hero_in=True):
    c.drawRect(skia.Rect(-400, -200, W + 600, 900), fp('#3E4B78'))
    for i in range(-3, 18): rect(c, i * 180, 190, i * 180 + 150, 760, '#4A5888', LW * .6, 10)
    label(c, 'BUREAU OF HEROES  ·  SPARK TEST', 1100, 150, 64, '#F2C14E', KALAM, 'center', skew=0)
    rect(c, -400, 860, W + 600, H + 200, '#2B3150', LW)
    for i in range(-3, 22): line(c, i * 140, 880, i * 140 - 160, H + 20, 3, '#363D60')

def s4(c, t):
    tc = twos(t)
    hall(c, t)
    for (x, lt, num) in SCAN: scanner(c, x, num, lt - .55, lt, t)
    for i, (x, lt, num) in enumerate(SCAN):
        sp_ = TEENS[i]; landed = tc >= lt; step = back(K(tc, 7.45 + i * .2, .4))
        cx = x - 260 + (1 - step) * -120
        draw_char(c, cx, 900, .95, sp_, face=.55 if not landed else .1, eyes='closed' if landed and tc < lt + .7 else ('dot' if not blink(t, 2.3, i) else 'closed'),
                  mouth='grin' if landed else 'flat', arms=('down', ('down', 'scan', K(tc, lt - .6, .25)) if not landed else ('scan', 'up', K(tc, lt + .05, .25))),
                  squash=.1 * math.sin(K(tc, lt, .25) * math.pi), bob=abs(math.sin(tc * 6)) * 10 * (1 if landed else 0),
                  sparkle=K(t, lt + .1, .45) * 1.7, brow=.6 if landed else 0, legs=walk_legs(tc * 12) if step < .95 else None)
    # the hero waits at the end of the line, nervous
    hx_ = 2160 + (1 - back(K(tc, 9.9, .5))) * 260
    draw_char(c, hx_, 900, .95, HERO, face=-.5, eyes='dot', mouth='flat', arms=('fist', 'down'), sweat=(t - 10.3) * 1.5 if t > 10.3 else -1,
              pupil=-.6, brow_tilt=.8, legs=walk_legs(tc * 12) if t < 10.35 else None)
    night(c, [('pool', 1100, 500, 1100, .6), ('oval', 1100, 900, 1300, 200, .5)], ambient='#6A74B4')

# ======================= SHOT 5: "...and your number is zero." (11.3 - 14.3)
def s5(c, t):
    tc = twos(t); zero_t = 12.74
    dx, dy = shake(t, zero_t + .05, .5, 30); c.translate(dx, dy)
    bg = cached('hallblur', lambda cc: (cc.save(), cc.translate(W / 2, H / 2), cc.scale(1.5, 1.5), cc.translate(-W / 2 - 200, -H / 2 + 60), hall(cc, 0), cc.restore()))
    bp = skia.Paint(); bp.setImageFilter(skia.ImageFilters.Blur(13, 13)); c.drawImage(bg, 0, 0, skia.SamplingOptions(), bp)
    zero = t >= zero_t
    # display + pad on the right
    sx = 1450
    rect(c, sx - 280, 140, sx + 280, 470, '#1B1E2C', LW * 1.3, 28)
    if t < zero_t:
        # slows down as it approaches the end
        rate = lerp(24, 5, K(t, 11.3, 1.4)); txt = '%03d' % random.Random(int(t * rate)).randint(1, 999); cl = '#7CF2E0'
    else: txt, cl = '0', '#FF4A4A'
    pk = pop(K(t, zero_t, .3)) if zero else 1
    c.save(); c.translate(sx, 380); c.scale(pk, pk); label(c, txt, 0, 0, 230, cl, MARKER, 'center', skew=0); c.restore()
    label(c, 'SPARK SCORE', sx, 200, 46, '#9AA4B8', KALAM, 'center', skew=0)
    line(c, sx, 470, sx, 600, LW * 3)
    rect(c, sx - 130, 600, sx + 130, H + 60, '#D7DDE8', LW * 1.3, 30)
    rect(c, sx - 100, 660, sx + 100, 820, '#1E2A3A', LW, 18)
    padc = '#FF4A4A' if zero else '#7CF2E0'
    c.drawRect(skia.Rect(sx - 86, 674, sx + 86, 806), fp(padc, 170 + 60 * math.sin(t * 18)))
    # hero close-up
    gulp = .06 * math.sin(K(tc, 12.0, .3) * math.pi)
    react = back(K(tc, zero_t, .25), 2.4)
    draw_char(c, 760, 1400, 2.15, HERO, face=lerp(.55, .3, react), eyes='wide' if zero else ('closed' if blink(t, 2.3, .4) else 'dot'),
              mouth='o' if zero else 'flat', brow=lerp(0, 1.4, react), brow_tilt=.7 if not zero else -.4,
              arms=('down', 'scan'), squash=gulp - .08 * math.sin(K(tc, zero_t, .3) * math.pi), sweat=(t - 11.9) * 1.1 if t > 11.9 else -1,
              rim='#FF8080' if zero else '#9FF6EA', light=-1, pupil=.5 if not zero else 0, tilt=-4 * react)
    if zero:  # red alarm pulse + speed lines
        a = (math.sin((t - zero_t) * 14) * .5 + .5) * 60
        c.drawRect(skia.Rect(-100, -100, W + 100, H + 100), fp('#FF2020', a, blend=skia.BlendMode.kPlus))
        if t - zero_t < .14: c.drawRect(skia.Rect(-100, -100, W + 100, H + 100), fp('#FFFFFF', 200))
        r = random.Random(int(t * 12))
        for i in range(24):
            ang = r.uniform(0, 6.28); r0 = r.uniform(620, 760)
            line(c, 760 + math.cos(ang) * r0, 560 + math.sin(ang) * r0, 760 + math.cos(ang) * (r0 + 400), 560 + math.sin(ang) * (r0 + 400), 7, '#FFFFFF', 160)
    night(c, [('pool', 760, 560, 700, .55), ('pool', sx, 380, 520, .7), ('pool', sx, 740, 360, .6)], ambient='#5E68A8')
    add_light(c, sx, 740, 380, padc, 90); add_light(c, sx, 330, 420, cl, 50)
    if zero:  # stamp
        st = K(t, zero_t + .05, .2); sc = lerp(2.6, 1, ease_out(st))
        if st > 0:
            c.save(); c.translate(1130, 900); c.rotate(-10); c.scale(sc, sc)
            al = 255 * min(1, st * 2)
            p = skia.Path(); p.addRRect(skia.RRect.MakeRectXY(skia.Rect(-300, -110, 300, 110), 22, 22)); c.drawPath(p, ink(16, RED, al, boil=False))
            p2 = skia.Path(); p2.addRRect(skia.RRect.MakeRectXY(skia.Rect(-276, -86, 276, 86), 16, 16)); c.drawPath(p2, ink(6, RED, al, boil=False))
            label(c, 'ZERO', 0, 62, 170, RED, MARKER, 'center', skew=0, alpha=al / 255)
            c.restore()
    if t > END - .45: c.drawRect(skia.Rect(-200, -200, W + 200, H + 200), fp((0, 0, 0), 255 * K(t, END - .45, .45)))

# shot list: (name, start, end, draw, zoom, focus, whip_in, whip_out)
SHOTS = [
    ('s1', 0.0, 2.1, s1, (1.22, 1.34), (1060, 520), False, True),
    ('s2', 2.1, 4.95, s2, (1.04, 1.12), (960, 560), True, True),
    ('s3', 4.95, 7.45, s3, (1.0, 1.09), (960, 520), True, False),
    ('s4', 7.45, 11.3, s4, (1.0, 1.06), None, False, False),
    ('s5', 11.3, END, s5, (1.0, 1.08), (900, 560), False, False),
]

def s4_focus(t):  # pan along the line of scanners
    return (lerp(620, 1500, ease(K(t, 7.45, 3.85))), 560)

def frame(surf, t):
    for (name, a, b, fn, z, focus, wi, wo) in SHOTS:
        if a <= t < b or (name == 's5' and t >= a): break
    set_boil(t); c = surf.getCanvas(); e = ease(K(t, a, b - a)); n0, n1 = round(a * FPS), round(b * FPS); f = round(t * FPS)
    wx = sig = 0
    if wo and n1 - f <= 5: wx = -((6 - (n1 - f)) ** 2) * 34; sig = (6 - (n1 - f)) * 16
    if wi and f - n0 < 4: wx = (4 - (f - n0)) ** 2 * 52; sig = (4 - (f - n0)) * 18
    fo = focus or s4_focus(t)
    c.clear(C((0, 0, 0))); c.save(); c.translate(W / 2 + wx, H / 2); zz = lerp(z[0], z[1], e); c.scale(zz, zz); c.translate(-fo[0], -fo[1])
    fn(c, t); c.restore()
    finish(surf); vignette(c, .55)
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
                          '-c:v', 'libx264', '-crf', '18', '-preset', 'medium', '-pix_fmt', 'yuv420p', os.path.join(OUT, 'video.mp4')], stdin=subprocess.PIPE)
    for f in range(n):
        frame(surf, f / FPS); p.stdin.write(surf.makeImageSnapshot().toarray(colorType=skia.kBGRA_8888_ColorType).tobytes())
        if f % 48 == 0: print('frame', f, flush=True)
    p.stdin.close(); p.wait(); print('done')
