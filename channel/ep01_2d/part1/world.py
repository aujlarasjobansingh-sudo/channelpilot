# sets, monsters and cast for EP01 Part 1 (2D ink style)
import sys, os, math, random
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from kit2d import *
from preview import (grad_rect, grad_shape, city_strip, cached, blit, bokeh, flame, draw_gorrak, scanner, hall,
                     room_bg, window_view, shake)
import numpy as np, subprocess

# ---------------- voice envelope -> mouth shapes for on-screen speakers
VO = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../ep01/audio/vo_part1.mp3')
_raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', VO, '-ac', '1', '-ar', '24000', '-f', 's16le', '-'], capture_output=True).stdout
_s = np.frombuffer(_raw, np.int16).astype(np.float32) / 32768
_hop = 24000 // FPS
_rms = np.array([np.sqrt(np.mean(_s[i * _hop:(i + 1) * _hop] ** 2) + 1e-12) for i in range(len(_s) // _hop)])
_rms /= np.percentile(_rms, 98)
REAL = 0.0
def talk(t):
    i = int(REAL * FPS) // 2 * 2   # always the real voiceover clock   # held on twos
    v = _rms[min(i, len(_rms) - 1)]
    return 'open' if v > .55 else 'mid' if v > .2 else 'flat'

# ---------------- cast (original designs)
MOM = dict(skin='#E8B48C', skin_d='#C99068', suit='#4E9A8E', suit_d='#3A7A70', tee=True, hair='long', hair_col='#3A2418', dress='#4E9A8E', jeans=None)
TECH = dict(skin='#F0CBA6', skin_d='#D4A880', suit='#F2F2EE', suit_d='#CFCFD8', shirt='#9FC4FF', tie='#2E4F8A', hair='short', hair_col='#6B5A4A', glasses=True)
ANCHOR = dict(skin='#C99269', skin_d='#A8724D', suit='#2E3A66', suit_d='#222B4E', shirt='#FFFFFF', tie='#C8242C', hair='short', hair_col='#141218')
SCI = dict(skin='#E9C49C', skin_d='#CDA27A', suit='#F4F4F0', suit_d='#D2D2DA', shirt='#E8E8FF', tie='#4E9A6E', hair='short', hair_col='#B9B9C4', glasses=True)
OLDLADY = dict(skin='#F0CFB4', skin_d='#D4AE90', suit='#8E5AA8', suit_d='#6E4288', tee=True, hair='bun', hair_col='#D8D8E0', dress='#8E5AA8', glasses=True)
GIRL = dict(skin='#C99269', skin_d='#A8724D', suit='#F28AB0', suit_d='#D06A90', tee=True, hair='pigtails', hair_col='#1D1A20', dress='#F28AB0')
SHOUTER = dict(skin='#E8B48C', skin_d='#C99068', suit='#5A6B3A', suit_d='#46542C', tee=True, hair='cap', cap_col='#2E2E38', jeans='#3A3F5C')
POLICE = dict(skin='#D9A47A', skin_d='#B98258', suit='#2B3F7A', suit_d='#1F2F5E', shirt='#9FB4E8', tie='#141820', hair='cap', cap_col='#1F2F5E')
GOLDHERO = dict(skin='#F0C9A0', skin_d='#D6A77A', suit='#E9B53C', suit_d='#C28E22', tee=True, emblem='#FFFFFF', hair='short', hair_col='#8A4A22', jeans='#E9B53C', cape='#2E6BB5', glove='#FFF6DC')
SILVER = dict(skin='#E8B48C', skin_d='#C99068', suit='#B8C2D6', suit_d='#8E9AB4', tee=True, emblem='#3A4A7A', hair='short', hair_col='#1D1A20', jeans='#5A6788', glove='#3A4A7A')
BRONZE = dict(skin='#8D5B3E', skin_d='#6E4330', suit='#C47A3A', suit_d='#9A5A26', tee=True, emblem='#FFF6DC', hair='short', hair_col='#141218', jeans='#5A3A26', glove='#FFF6DC')
IRONH = dict(skin='#F2CDAA', skin_d='#D8AD86', suit='#7E8494', suit_d='#5E6474', tee=True, hair='cap', cap_col='#5E6474', jeans='#3B3F58')
EXEC = dict(skin='#F0CBA6', skin_d='#D4A880', suit='#1E1E28', suit_d='#121218', shirt='#FFFFFF', tie='#E9B53C', hair='short', hair_col='#C8C8D0', glasses=False)
KIDHERO = dict(HERO, emblem=None)
YOUNG = dict(HERO)
KIDS = [dict(t, hair=t['hair']) for t in TEENS]

# ---------------- generic helpers
def stage(c, t, tint='#2A1E5A', floor='#14102A', spot=True, sx=960):
    grad_rect(c, -400, -300, W + 400, 760, '#06060F', tint)
    grad_rect(c, -400, 740, W + 400, H + 300, floor, '#05050C')
    c.drawLine(-400, 750, W + 400, 750, ink(3, '#3A3070', boil=False))
    if spot:
        c.drawPath(cone_path(sx, -100, 80, 720, 900), sp(linear(0, -100, 0, 820, [hx('#FFF6DC', 70), hx('#FFF6DC', 10)]), blend=skia.BlendMode.kPlus))
        c.drawOval(skia.Rect(sx - 380, 760, sx + 380, 880), fp('#FFF6DC', 50, blur=20))
    r = random.Random(2)
    for i in range(40):
        x = r.uniform(0, W) + math.sin(t * .4 + i) * 20; y = r.uniform(0, 760) + math.cos(t * .3 + i) * 10
        c.drawCircle(x, y, r.uniform(1, 3), fp('#C8C0FF', 90))

def chip(c, t, t0, small, big, color='#FF6A3A', x=960, y=930):
    k = back(K(t, t0, .35), 1.6)
    if k <= 0: return
    c.save(); c.translate(x, y); c.scale(k, k)
    w = max(len(big) * 52, 360)
    rect(c, -w / 2, -70, w / 2, 40, '#141220', LW, 16); c.drawRect(skia.Rect(-w / 2 + 8, -62, -w / 2 + 22, 32), fp(color))
    label(c, small, 0, -38, 30, '#B8B0D8', KALAM, 'center', skew=0)
    label(c, big, 0, 22, 64, color, MARKER, 'center', skew=0)
    c.restore()

def text_card(c, t, t0, t1, txt, size=120, col='#FFFFFF'):
    c.drawRect(skia.Rect(-400, -300, W + 400, H + 300), fp((0, 0, 0)))
    n = len(txt); k = K(t, t0, max(.3, (t1 - t0) * .6)); s = txt[:max(1, int(n * k + .5))]
    label(c, s, 960 - skia.Font(FONT_HAND, size).measureText(txt) / 2, 580, size, col, FONT_HAND, 'left', skew=0)

def speed_lines(c, t, cx=960, cy=540, col='#FFFFFF', a=170, n=60, r0=420):
    r = random.Random(int(t * 12))
    for i in range(n):
        ang = r.uniform(0, 6.28); rr = r.uniform(r0, r0 + 200); wdt = r.uniform(3, 12)
        c.drawLine(cx + math.cos(ang) * rr, cy + math.sin(ang) * rr, cx + math.cos(ang) * 1800, cy + math.sin(ang) * 1800, ink(wdt, col, a, boil=False))

def hscroll_lines(c, t, y0=0, y1=H, col='#FFFFFF', a=120, speed=3000):
    r = random.Random(7)
    for i in range(40):
        y = r.uniform(y0, y1); L = r.uniform(200, 700); x = (r.uniform(0, W * 2) - t * speed) % (W * 2) - 400
        c.drawLine(x, y, x + L, y, ink(r.uniform(2, 6), col, a, boil=False))

# ---------------- day street
def street_day(c, t, pan=0.0, cross=False, people=True):
    grad_rect(c, -600, -400, W + 600, 700, '#5FA8E8', '#CFE8FF')
    for i in range(5):
        x = (i * 520 - pan * .1 + t * 12) % 2800 - 500
        puff(c, x, 120 + (i % 3) * 50, 55, i + 40, '#FFFFFF', '#D6E6F8', 255, outline=True)
    far = cached('dayfar', lambda cc: city_strip(cc, 600, 41, 150, 360, 80, 150, '#A9C2E2', '#93AED2', '#E6F0FF', .25, outline=False))
    blit(c, far, -(pan * .2) % 600 - 300, 0, blur=2)
    # shop row (repeats horizontally)
    def shops(cc):
        cols = ['#E9A65A', '#D96A6A', '#6AAFD9', '#9AD07A', '#E8D06A', '#B88AD9']
        for i in range(8):
            x = -400 + i * 380; col_ = cols[i % 6]
            p = skia.Path(); p.addRect(skia.Rect(x, 260, x + 370, 760)); cc.drawPath(p, sp(linear(0, 260, 0, 760, [hx(col_), hx(col_)]))); cc.drawPath(p, ink(LW))
            for j in range(3): rect(cc, x + 30 + j * 110, 300, x + 110 + j * 110, 400, '#BFE0F4', LW * .8, 6)
            rect(cc, x + 30, 560, x + 230, 740, '#BFE0F4', LW * .8, 6); rect(cc, x + 260, 580, x + 340, 760, '#6A4A3A', LW * .8, 4)
            aw = skia.Path(); aw.moveTo(x + 10, 470); aw.lineTo(x + 360, 470); aw.lineTo(x + 380, 540); aw.lineTo(x - 10, 540); aw.close()
            cc.drawPath(aw, fp('#FFFFFF')); cc.save(); cc.clipPath(aw)
            for s_ in range(10): cc.drawRect(skia.Rect(x - 10 + s_ * 40, 470, x + 10 + s_ * 40, 540), fp(col_))
            cc.restore(); cc.drawPath(aw, ink(LW))
            rect(cc, x + 60, 420, x + 310, 462, '#FFF6DC', LW * .7, 8)
            label(cc, ['BAKERY', 'BOOKS', 'CAFE', 'FLOWERS', 'ARCADE', 'PHARMACY'][i % 6], x + 185, 455, 34, '#3A2E2A', KALAM, 'center', skew=0)
    sh = cached('shops', shops)
    off = -(pan * .6) % 380
    blit(c, sh, off - 380, 0); blit(c, sh, off - 380 + 3040, 0)
    grad_rect(c, -600, 760, W + 600, 860, '#D8D2C6', '#BDB6A8', LW)
    for i in range(-2, 14): c.drawLine(i * 160 - (pan * .85) % 160, 760, i * 160 - (pan * .85) % 160 - 30, 860, ink(3, '#A8A092', boil=False))
    grad_rect(c, -600, 860, W + 600, H + 400, '#5A5A66', '#3E3E48', LW)
    if cross:
        for i in range(8): rect(c, 300 + i * 160 - pan, 900, 380 + i * 160 - pan, 1060, '#F4F4F0', 0)
    else:
        for i in range(-2, 12): c.drawRect(skia.Rect(i * 260 - pan % 260, 980, i * 260 + 140 - pan % 260, 996), fp('#F2D36B'))
    # trees + lamp posts (near layer)
    for i in range(-1, 6):
        x = i * 640 - (pan * .85) % 640 + 200
        rect(c, x - 14, 560, x + 14, 780, '#7A5238', LW * .8, 6)
        puff(c, x, 520, 90, i % 3 + 60, '#6EBB5E', '#4E9A44', 255)
        x2 = x + 320; rect(c, x2 - 8, 380, x2 + 8, 780, '#3A3E50', LW * .7, 4); oval(c, x2 - 30, 360, x2 + 30, 400, '#FFF6DC', LW * .7)

def walker(c, t, x, y, s, spec, phase, face=.7, run=False, **kw):
    if run:
        draw_char(c, x, y, s, spec, face=face, legs=walk_legs(phase, 66, 34), arms=run_arms(phase), bob=10 * abs(math.sin(phase)), lean=(-.18 if face > 0 else .18), **kw)
    else:
        kw.setdefault('arms', walk_arms(phase))
        draw_char(c, x, y, s, spec, face=face, legs=walk_legs(phase, 38, 18), bob=7 * abs(math.sin(phase)), **kw)

# ---------------- station
def station(c, t, hole=0.0, alarm=False, pan=0.0):
    grad_rect(c, -600, -400, W + 600, 820, '#D8DCE6', '#B6BCCC')
    for i in range(-4, 30):
        for j in range(16): c.drawRect(skia.Rect(i * 90 - pan % 90 + 2, j * 52 + 2, i * 90 - pan % 90 + 88, j * 52 + 50), fp('#E4E8F0' if (i + j) % 2 else '#DDE2EC'))
    c.drawRect(skia.Rect(-600, 420, W + 600, 470), fp('#3E6DB5')); c.drawLine(-600, 420, W + 600, 420, ink(LW)); c.drawLine(-600, 470, W + 600, 470, ink(LW))
    rect(c, 1240 - pan * .9, 200, 1660 - pan * .9, 300, '#1E2236', LW, 12); label(c, 'PLATFORM 6', 1450 - pan * .9, 268, 56, '#F2C14E', MARKER, 'center', skew=0)
    for i in range(-2, 12): c.drawRect(skia.Rect(i * 300 - pan % 300, 40, i * 300 + 180 - pan % 300, 60), fp('#FFFFFF')); add_light(c, i * 300 + 90 - pan % 300, 50, 160, '#EAF2FF', 60)
    # train on the right side (behind platform edge)
    tx = 1500 - pan * .9
    rect(c, tx, 330, tx + 1400, 820, '#D9DEE8', LW, 30); c.drawRect(skia.Rect(tx, 560, tx + 1400, 600), fp('#C8242C'))
    for i in range(5): rect(c, tx + 60 + i * 260, 380, tx + 240 + i * 260, 520, '#7FA8D8', LW * .8, 14)
    grad_rect(c, -600, 800, W + 600, H + 400, '#9AA0B0', '#6E7486', LW)
    c.drawRect(skia.Rect(-600, 800, W + 600, 830), fp('#F2D36B')); c.drawLine(-600, 830, W + 600, 830, ink(LW * .7))
    for i in range(-2, 8):
        x = i * 520 - (pan * 1.0) % 520 + 100
        p = skia.Path(); p.addRect(skia.Rect(x - 50, -100, x + 50, 840)); c.drawPath(p, sp(linear(x - 50, 0, x + 50, 0, [hx('#E8ECF4'), hx('#B8BFCE')]))); c.drawPath(p, ink(LW))
    if hole > 0:
        hx_, hy_ = 900, 900
        p = skia.Path(); p.addOval(skia.Rect(hx_ - 420 * hole, hy_ - 90 * hole, hx_ + 420 * hole, hy_ + 90 * hole)); c.drawPath(p, fp('#120E18')); c.drawPath(p, ink(LW * 1.2))
        for i in range(10):
            a = i / 10 * 6.28; c.drawLine(hx_ + math.cos(a) * 420 * hole, hy_ + math.sin(a) * 90 * hole, hx_ + math.cos(a) * 600 * hole, hy_ + math.sin(a) * 140 * hole, ink(5))
    if alarm:
        for x in (300, 1600):
            rect(c, x - 30, 90, x + 30, 140, '#5A1010', LW * .8, 10)
            on = math.sin(t * 9) > 0
            if on: add_light(c, x, 115, 500, '#FF2A2A', 150)
        c.drawRect(skia.Rect(-600, -400, W + 600, H + 400), fp('#FF2020', 40 * (math.sin(t * 9) * .5 + .5), blend=skia.BlendMode.kPlus))

# ---------------- monsters
def draw_ember(c, x, y, s, t, open_=0.0):
    c.save(); c.translate(x, y); c.scale(s, s)
    for lx in (-60, -20, 30, 70): line(c, lx, -50, lx + math.sin(t * 12 + lx) * 8, 0, 14)
    tl = skia.Path(); tl.moveTo(-90, -70); tl.cubicTo(-170, -80 + math.sin(t * 6) * 20, -200, -20, -230, -60); tl.lineTo(-90, -50); shape(c, tl, '#E8582A')
    body = skia.Path(); body.addRRect(skia.RRect.MakeRectXY(skia.Rect(-100, -120, 100, -40), 40, 40)); grad_shape(c, body, '#FF7A3A', '#C8401E', -120, -40)
    hd = skia.Path(); hd.addRRect(skia.RRect.MakeRectXY(skia.Rect(60, -170, 170, -80), 40, 40)); grad_shape(c, hd, '#FF8A4A', '#D8502A', -170, -80)
    circ(c, 130, -138, 13, '#FFE45C', LW * .7); c.drawCircle(133, -138, 5, fp(INK))
    mp = skia.Path(); mp.moveTo(110, -100); mp.lineTo(172, -104 - 0); mp.lineTo(172, -96 + open_ * 26); mp.close(); shape(c, mp, '#3A0F10', LW * .6)
    for i in range(5):
        fx_ = -70 + i * 34; flame(c, fx_, -116, .35, t, i)
    c.restore()

def draw_storm(c, x, y, s, t, rear=0.0, open_=0.0, look=0.0):
    """centipede: segments from tail (left/down) to head (rear lifts head)."""
    c.save(); c.translate(x, y); c.scale(s, s)
    n = 9; pts = []
    for i in range(n):
        u = i / (n - 1)
        px = -620 + u * 620 + math.sin(t * 3 + i * .7) * 14
        py = -60 - math.sin(u * math.pi * .5) ** 2 * 520 * rear + math.sin(t * 4 + i) * 8
        pts.append((px, py))
    for i, (px, py) in enumerate(pts[:-1]):
        for sd in (-1, 1):
            lg = math.sin(t * 14 + i * 1.3 + sd) * 18
            p = skia.Path(); p.moveTo(px, py); p.lineTo(px + sd * 30 + lg, py + 70); p.lineTo(px + sd * 44 + lg, py + 120); c.drawPath(p, ink(10, '#2A1A30', boil=False))
    for i, (px, py) in enumerate(pts[:-1]):
        r = 70 + i * 3
        b = skia.Path(); b.addCircle(px, py, r); c.drawPath(b, sp(radial(px - 20, py - 25, r * 1.4, [hx('#6FD08A'), hx('#2E8A5A'), hx('#1E5A3E')]))); c.drawPath(b, ink(LW))
        c.drawArc(skia.Rect(px - r + 14, py - r + 14, px + r - 14, py + r - 14), 200, 80, False, ink(5, '#B8F0C8', 160, boil=False))
        for k_ in (-1, 1): poly(c, [(px + k_ * 20, py - r + 6), (px + k_ * 30, py - r - 30), (px + k_ * 40, py - r + 10)], '#F3E7C8', LW * .6)
    hx_, hy_ = pts[-1]
    c.save(); c.translate(hx_ + 40, hy_ - 10); c.rotate(look * 30)
    hd = skia.Path(); hd.addOval(skia.Rect(-110, -100, 110, 90)); c.drawPath(hd, sp(radial(-30, -30, 160, [hx('#7FE09A'), hx('#2E8A5A')]))); c.drawPath(hd, ink(LW * 1.2))
    for sx in (-1, 1):
        mand = skia.Path(); mand.moveTo(sx * 40, 60); mand.cubicTo(sx * (90 + open_ * 50), 120, sx * (60 + open_ * 70), 200, sx * (10 + open_ * 50), 190); mand.lineTo(sx * 20, 80); mand.close(); shape(c, mand, '#F3E7C8')
    if open_ > .05:
        mo = skia.Path(); mo.addOval(skia.Rect(-60, 20, 60, 20 + 120 * open_)); shape(c, mo, '#2A0F1E')
        for i in range(6): poly(c, [(-50 + i * 20, 24), (-40 + i * 20, 24), (-45 + i * 20, 24 + 40 * open_)], '#FFFFFF', LW * .5)
    for (ex, ey) in ((-45, -30), (45, -30), (-20, -60), (20, -60)):
        circ(c, ex, ey, 16, '#FF3A3A', LW * .6); add_light(c, ex, ey, 60, '#FF4A4A', 150)
    for sx in (-1, 1): line(c, sx * 40, -90, sx * (120 + math.sin(t * 5) * 20), -200, 7)
    c.restore(); c.restore()

def draw_quake(c, x, y, s, t, stomp=0.0):
    c.save(); c.translate(x, y - stomp * 40); c.scale(s, s)
    def rock(cx, cy, w, h, seed, col_='#8C7A6A'):
        r = random.Random(seed); p = skia.Path()
        for i in range(8):
            a = i / 8 * 6.28; rr = r.uniform(.8, 1.05); (p.moveTo if i == 0 else p.lineTo)(cx + math.cos(a) * w * rr, cy + math.sin(a) * h * rr)
        p.close(); c.drawPath(p, sp(linear(cx - w, cy - h, cx + w, cy + h, [hx('#A89684'), hx(col_), hx('#5E5044')]))); c.drawPath(p, ink(LW * 1.1))
        c.drawLine(cx - w * .3, cy - h * .2, cx + w * .1, cy + h * .3, ink(4, '#4A3E34'))
    for lx in (-130, 130): rock(lx, -110, 90, 120, lx)
    rock(-280, -430 - stomp * 60, 90, 150, 3); rock(280, -430 + stomp * 60, 90, 150, 4)
    rock(0, -440, 240, 230, 5)
    rock(0, -720, 130, 110, 6)
    for ex in (-45, 45): circ(c, ex, -730, 18, '#FFB43C', LW * .7); add_light(c, ex, -730, 90, '#FFA03C', 160)
    for i in range(5): c.drawLine(-120 + i * 60, -500 + (i % 2) * 40, -100 + i * 60, -380, ink(6, '#FFA03C', 200, boil=False))
    c.restore()

def draw_extinction(c, x, y, s, t, eyes=1.0):
    c.save(); c.translate(x, y); c.scale(s, s)
    p = skia.Path(); p.moveTo(-900, 0)
    for i in range(13):
        a = i / 12; px = -900 + a * 1800; py = -700 - math.sin(a * math.pi) * 500 + (60 if i % 2 else -60)
        p.lineTo(px, py)
    p.lineTo(900, 0); p.close(); c.drawPath(p, fp('#05030A'))
    c.drawPath(p, ink(10, '#7A0E1E', 200))
    for (ex, ey, r) in ((-180, -900, 60), (180, -900, 60), (0, -980, 40)):
        h_ = r * eyes; c.drawOval(skia.Rect(ex - r, ey - h_ * .5, ex + r, ey + h_ * .5), fp('#FF2A3A')); add_light(c, ex, ey, r * 5, '#FF2A3A', 200 * eyes)
    c.restore()

def draw_cat(c, x, y, s, t, scared=0.0):
    c.save(); c.translate(x, y); c.scale(s, s)
    tl = skia.Path(); tl.moveTo(30, -30); tl.cubicTo(90, -40, 90 + math.sin(t * 5) * 20, -120, 70, -140); c.drawPath(tl, ink(16)); c.drawPath(tl, ink(8, '#F2A65A'))
    oval(c, -50, -80, 50, 0, '#F2A65A'); circ(c, -40, -100, 38, '#F2A65A')
    for sx in (-1, 1): poly(c, [(-40 + sx * 30, -120), (-40 + sx * 12, -150 - scared * 10), (-40 + sx * 2, -128)], '#F2A65A', LW * .7)
    for ex in (-54, -26):
        if scared > .5: oval(c, ex - 8, -112, ex + 8, -94, '#FFFFFF', LW * .5); c.drawCircle(ex, -103, 2.5, fp(INK))
        else: c.drawOval(skia.Rect(ex - 4, -110, ex + 4, -98), fp(INK))
    c.restore()

def draw_dog(c, x, y, s, t, bark=0.0):
    c.save(); c.translate(x, y); c.scale(s, s)
    for lx in (-40, -15, 20, 45): line(c, lx, -40, lx, 0, 12)
    tl = skia.Path(); tl.moveTo(-60, -60); tl.lineTo(-90, -100 + math.sin(t * 20) * 14); c.drawPath(tl, ink(14)); c.drawPath(tl, ink(7, '#C8945A'))
    oval(c, -70, -90, 70, -30, '#C8945A'); circ(c, 70, -100, 40, '#C8945A'); oval(c, 85, -100, 125, -70, '#E8C08A', LW * .7)
    c.drawCircle(122, -90, 7, fp(INK)); c.drawOval(skia.Rect(60, -116, 70, -102), fp(INK))
    oval(c, 30, -140, 60, -80, '#8A5A32', LW * .7)
    if bark > .5: c.drawLine(140, -80, 175, -95, ink(5)); c.drawLine(140, -70, 178, -70, ink(5))
    c.restore()

def phone_ui(c, cx, cy, s, draw_screen, t):
    c.save(); c.translate(cx, cy); c.scale(s, s)
    rect(c, -200, -380, 200, 380, '#1A1A22', LW * 1.2, 46)
    sc = skia.Path(); sc.addRRect(skia.RRect.MakeRectXY(skia.Rect(-176, -340, 176, 340), 26, 26)); c.save(); c.clipPath(sc, doAntiAlias=True)
    draw_screen(c, t); c.restore(); c.drawPath(sc, ink(LW * .6))
    c.drawCircle(0, -360, 7, fp('#333344'))
    c.restore()

def badge(c, x, y, s, kind):
    cols = {'IRON': ('#8A90A0', '#5E6474'), 'BRONZE': ('#D08A4A', '#9A5A26'), 'SILVER': ('#D4DAE6', '#9AA4B8'), 'GOLD': ('#F6CF5A', '#C8921E'), 'CROWN': ('#FFE88A', '#E0A82A')}
    a, b = cols[kind]
    c.save(); c.translate(x, y); c.scale(s, s)
    p = skia.Path(); p.moveTo(0, -130); p.lineTo(110, -90); p.lineTo(100, 40); p.cubicTo(80, 100, 30, 130, 0, 150); p.cubicTo(-30, 130, -80, 100, -100, 40); p.lineTo(-110, -90); p.close()
    c.drawPath(p, sp(linear(-110, -130, 110, 150, [hx(a), hx(b)]))); c.drawPath(p, ink(LW * 1.2))
    c.drawLine(-60, -80, -20, -100, ink(6, '#FFFFFF', 140, boil=False))
    if kind == 'CROWN':
        poly(c, [(-60, 30), (-60, -30), (-30, 0), (0, -50), (30, 0), (60, -30), (60, 30)], '#FFF6DC', LW * .8)
    else:
        label(c, kind[0], 0, 40, 120, '#FFFFFF', MARKER, 'center', stroke=10, skew=0)
    c.restore()
    label(c, kind, x, y + 200 * s, 52 * s / .8, a, MARKER, 'center', stroke=8, skew=0)

def license_card(c, x, y, s, t, k=1.0):
    c.save(); c.translate(x, y); c.scale(s, s); c.rotate(-4 * (1 - k))
    rect(c, -460, -280, 460, 280, '#1E2236', LW * 1.3, 30)
    c.drawRect(skia.Rect(-450, -270, 450, -170), fp('#2E3A66'))
    badge_s = skia.Path(); poly(c, [(-400, -250), (-350, -232), (-354, -190), (-400, -175), (-446, -190), (-450, -232)], '#F2C14E', LW * .7)
    label(c, 'BUREAU OF REGISTERED HEROES', -320, -232, 40, '#F2C14E', KALAM, 'left', skew=0)
    label(c, 'OFFICIAL HERO LICENSE', -320, -190, 30, '#B8C2E0', KALAM, 'left', skew=0)
    rect(c, -410, -130, -160, 170, '#D9262E', LW, 18)
    c.save(); c.clipRect(skia.Rect(-410, -130, -160, 170)); draw_char(c, -285, 330, .9, HERO, face=0, eyes='dot', mouth='flat', shadow=False); c.restore()
    label(c, 'THE ZERO', -120, -70, 72, '#FFFFFF', MARKER, 'left', skew=0)
    label(c, 'RANK', -120, 0, 32, '#8A94B8', KALAM, 'left', skew=0); label(c, 'IRON', -120, 50, 54, '#B8C2D6', MARKER, 'left', skew=0)
    label(c, 'POSITION', 120, 0, 32, '#8A94B8', KALAM, 'left', skew=0); label(c, '#4,812', 120, 50, 54, '#FFFFFF', MARKER, 'left', skew=0)
    label(c, 'SPARK SCORE', -120, 110, 32, '#8A94B8', KALAM, 'left', skew=0); label(c, '0', -120, 175, 70, '#FF4A4A', MARKER, 'left', skew=0)
    c.drawLine(-440, -260, 200, -260 + 500, ink(30, '#FFFFFF', 18, boil=False))
    c.restore()
