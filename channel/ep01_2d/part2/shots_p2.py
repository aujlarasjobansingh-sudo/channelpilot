# EP01 Part 2 shots - every shot starts on a word from the ASR transcript of vo_part2.mp3
import sys, os, json, re, math, random
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '../part1')); sys.path.insert(0, os.path.join(HERE, '..'))
import world
from shots_b import *          # all part-1 helpers, sets, cast
import numpy as np, subprocess

# ---------- part-2 voice clock (lip flaps)
VO2 = os.path.join(HERE, '../../ep01/audio/vo_part2.mp3')
_raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', VO2, '-ac', '1', '-ar', '24000', '-f', 's16le', '-'], capture_output=True).stdout
_s = np.frombuffer(_raw, np.int16).astype(np.float32) / 32768; _hop = 24000 // FPS
_r = np.array([np.sqrt(np.mean(_s[i * _hop:(i + 1) * _hop] ** 2) + 1e-12) for i in range(len(_s) // _hop)])
world._rms = _r / np.percentile(_r, 98)
DUR2 = len(_s) / 24000

# ---------- word lookup
WORDS = json.load(open(os.path.join(HERE, '../../ep01/audio/asr/words_p2.json')))
def norm(s): return re.sub(r'[^a-z0-9]', '', s.lower())
NW = [norm(w['w']) for w in WORDS]
def at(phrase, after=-1.0):
    ps = [norm(p) for p in phrase.split()]
    for i in range(len(NW) - len(ps) + 1):
        if WORDS[i]['t'] >= after and NW[i:i + len(ps)] == ps: return WORDS[i]['t']
    raise ValueError(f'not found: {phrase} after {after}')

# ---------- new cast
MIRA = dict(skin='#7A4A32', skin_d='#5E3624', suit='#2E8A9A', suit_d='#226A78', tee=True, emblem=None, hair='puff', hair_col='#1A1416',
            jeans='#3A4058', goggles=True, glove='#C8D2E6', band='#C8D2E6', vest='#C8D2E6')
COUSIN = dict(skin='#E8B48C', skin_d='#C99068', suit='#F2B84A', suit_d='#D0962A', tee=True, hair='pigtails', hair_col='#3A2418', dress='#F2B84A')
AUNT = dict(skin='#E8B48C', skin_d='#C99068', suit='#C84A6A', suit_d='#A0324E', tee=True, hair='bun', hair_col='#3A2418', dress='#C84A6A')
MAN = dict(skin='#C99269', skin_d='#A8724D', suit='#4A6AA8', suit_d='#344E80', tee=True, hair='cap', cap_col='#E8A33A', jeans='#2E3550')
REPORTER = dict(skin='#F0CBA6', skin_d='#D4A880', suit='#8A3A4A', suit_d='#6A2A36', shirt='#FFFFFF', tie='#2A2A34', hair='long', hair_col='#C8902A')

def drone(c, x, y, s, t, light='#7CF2E0'):
    c.save(); c.translate(x, y + math.sin(t * 5 + x) * 8 * s); c.scale(s, s)
    for sx in (-1, 1):
        c.drawLine(0, 0, sx * 60, -14, ink(10)); c.drawOval(skia.Rect(sx * 60 - 40, -24, sx * 60 + 40, -14), fp('#C8D2E6', 160))
        c.drawLine(sx * 60 - 40 * abs(math.cos(t * 40)), -19, sx * 60 + 40 * abs(math.cos(t * 40)), -19, ink(4, boil=False))
    rect(c, -34, -14, 34, 18, '#3A4058', LW * .8, 10)
    on = int(t * 4) % 2; c.drawCircle(0, 4, 7, fp(light if on else '#2A3040')); add_light(c, 0, 4, 50, light, 140 if on else 0)
    c.restore()

def tablet(c, x, y, s, draw, t, rot=0.0):
    c.save(); c.translate(x, y); c.rotate(rot); c.scale(s, s)
    rect(c, -300, -210, 300, 210, '#1A1A22', LW * 1.2, 26)
    sc = skia.Path(); sc.addRRect(skia.RRect.MakeRectXY(skia.Rect(-276, -186, 276, 186), 12, 12)); c.save(); c.clipPath(sc, doAntiAlias=True)
    draw(c, t); c.restore(); c.drawPath(sc, ink(LW * .6)); c.restore()

def note_card(c, t, t0, txt, sub=None):
    grad_rect(c, -400, -300, W + 400, H + 300, '#E8DCC0', '#C8B898')
    r = random.Random(3)
    for i in range(200): c.drawCircle(r.uniform(-200, W + 200), r.uniform(-200, H + 200), r.uniform(1, 3), fp('#A8905E', 70))
    for i in range(14): c.drawLine(200, 160 + i * 64, 1720, 160 + i * 64, ink(2, '#8AB0D8', 120, boil=False))
    c.drawLine(320, 100, 320, 1000, ink(3, '#D86A6A', 160, boil=False))
    k = pop(K(t, t0 + .05, .35))
    c.save(); c.translate(960, 560); c.rotate(-4); c.scale(k, k); label(c, txt, 0, 0, 170, '#2A2E5A', FONT_HAND, 'center', skew=0); c.restore()
    if sub: label(c, sub, 960, 740, 70, '#C8242C', FONT_HAND, 'center', skew=0)

def bedroom_night(c, t):
    room_bg(c); window_view(c, t, 0)
    hb = skia.Path(); hb.addRRect(skia.RRect.MakeRectXY(skia.Rect(480, 500, 540, 800), 24, 24)); grad_shape(c, hb, '#8A5D40', '#5E3E2B', 500, 800)
    mat = skia.Path(); mat.addRRect(skia.RRect.MakeRectXY(skia.Rect(510, 650, 1480, 760), 22, 22)); grad_shape(c, mat, '#FBF8F1', '#D9D2C2', 650, 760)
    rect(c, 500, 740, 1490, 800, '#7C5338', LW, 6); rect(c, 1450, 600, 1495, 800, '#6E4A33', LW, 14)
    bl = skia.Path(); bl.addRRect(skia.RRect.MakeRectXY(skia.Rect(1000, 660, 1480, 770), 20, 20)); grad_shape(c, bl, '#4F7FC8', '#2D5596', 660, 770)

def fire_escape(c, t):
    grad_rect(c, -400, -300, W + 400, H + 300, '#0A0E2A', '#2A2458')
    r = random.Random(8)
    for i in range(60): c.drawCircle(r.uniform(0, W), r.uniform(0, 500), r.uniform(1, 2.4), fp('#FFFFFF', 120 + 100 * math.sin(t * 2 + i)))
    city = cached('fecity', lambda cc: city_strip(cc, 1000, 61, 200, 520, 70, 150, '#161C44', '#10143A', '#FFC864', .45, outline=False))
    blit(c, city, 0, 0, blur=3)
    p = skia.Path(); p.addRect(skia.Rect(-400, -300, 360, H + 300)); c.drawPath(p, sp(linear(-400, 0, 360, 0, [hx('#5A3A3A'), hx('#7A4A40')]))); c.drawPath(p, ink(LW))
    for j in range(8):
        for i in range(5): c.drawRect(skia.Rect(-380 + i * 150, j * 130, -250 + i * 150, j * 130 + 60), fp('#4A2E2E'))
    rect(c, 240, 400, 400, 860, '#FFC864', LW, 6); c.drawLine(320, 400, 320, 860, ink(LW))
    add_light(c, 320, 620, 400, '#FFC864', 80)
    rect(c, 300, 860, 1700, 890, '#2A2E3A', LW, 4)
    for i in range(30): c.drawLine(320 + i * 46, 760, 320 + i * 46, 860, ink(5, '#2A2E3A', boil=False))
    c.drawLine(300, 760, 1700, 760, ink(10, '#2A2E3A', boil=False))

def living_room(c, t):
    grad_rect(c, -400, -300, W + 400, 800, '#E8C89A', '#D8B080')
    for i in range(-4, 30): c.drawRect(skia.Rect(i * 80, -300, i * 80 + 40, 800), fp('#E0BC8A', 120))
    grad_rect(c, -400, 790, W + 400, H + 300, '#8A6A50', '#5A4434', LW)
    rect(c, 1400, 200, 1700, 480, '#4A6A8A', LW, 6); c.drawRect(skia.Rect(1420, 220, 1680, 460), fp('#9FC4E8'))
    rect(c, 200, 300, 420, 460, '#F2C14E', LW, 4); c.drawCircle(310, 380, 50, fp('#E8A0A0'))
    for i, cl in enumerate(('#C84A6A', '#4AB0E8', '#9AD07A')): circ(c, 1500 + i * 70, 760, 30, cl, LW * .6)

def mall(c, t, pan=0):
    grad_rect(c, -600, -400, W + 600, 760, '#F0E6D8', '#D8CCBC')
    for i in range(-2, 9):
        x = i * 360 - pan % 360
        rect(c, x, 200, x + 330, 760, ['#E86A6A', '#6AAFD9', '#9AD07A', '#E8D06A'][i % 4], LW, 6); rect(c, x + 30, 320, x + 300, 700, '#CFE8F8', LW * .8, 6)
        rect(c, x + 40, 230, x + 290, 290, '#FFF6DC', LW * .7, 8)
    grad_rect(c, -600, 760, W + 600, H + 400, '#C8C0B0', '#9A9284', LW)
    for i in range(-2, 14): c.drawLine(i * 200 - pan % 200, 760, i * 200 - pan % 200 - 300, H + 300, ink(3, '#AAA294', boil=False))

# =============================================================== shots (fn(c, t, t0))
def P1_dust(c, t, t0):
    lt = t - t0
    station(c, t, 1.0, False, 500)
    for i in range(10):
        a = i / 10 * 6.28; rad = 200 + lt * 60
        puff(c, 900 + math.cos(a) * rad * 1.6, 820 + math.sin(a) * rad * .4 - lt * 20, 110 - lt * 12, i + 3, '#D9D3E6', '#9E95B8', 255 * max(0, 1 - lt / 3.2), outline=False)
    r = random.Random(3)
    for i in range(30):
        x = r.uniform(400, 1500); y = (r.uniform(0, 800) + lt * 60) % 900
        c.drawCircle(x, y, r.uniform(2, 5), fp('#E8E0D0', 150))

def P2_empty(c, t, t0):
    lt = t - t0
    station(c, t, 1.0, False, 520 + lt * 30)
    r = random.Random(5)
    for i in range(6):
        y = min(900, 300 + (lt * 600 + i * 120) % 900); c.drawCircle(700 + i * 80, y, 8, fp('#9AA0B0')); c.drawCircle(700 + i * 80, y, 8, ink(3, boil=False))
    for i in range(3): puff(c, 900 + (i - 1) * 300, 860, 60, i + 9, '#D9D3E6', '#9E95B8', 120, outline=False)

def P3_gone(c, t, t0):
    lt = t - t0
    grad_rect(c, -400, -300, W + 400, H + 300, '#C8C4D8', '#8A86A0')
    for i in range(6): puff(c, 200 + i * 300, 900 + math.sin(t + i) * 20, 150, i + 30, '#E8E4F0', '#BEB8D0', 200, outline=False)
    c.drawPath(cone_path(960, -200, 200, 600, 1300), sp(linear(0, -200, 0, 1100, [hx('#FFFFFF', 120), hx('#FFFFFF', 10)]), blend=skia.BlendMode.kPlus))
    draw_char(c, 960, 960, 1.15, HERO, face=0, eyes='half', mouth='flat', arms=('down', 'up'), rim='#FFFFFF', squash=.04 * math.sin(K(lt, 0, .3) * math.pi))

def P4_roof(c, t, t0):
    lt = t - t0
    grad_rect(c, -400, -1400, W + 400, H + 300, '#A8AEBE', '#D8DCE6')
    for i in range(-3, 24): c.drawLine(i * 100, -1400, i * 100, 1100, ink(3, '#9AA0B0', boil=False))
    hp = skia.Path(); pts = [(600, -700), (760, -820), (900, -760), (1000, -880), (1120, -800), (1260, -900), (1340, -760), (1300, -560), (1140, -500), (980, -560), (820, -480), (660, -560)]
    hp.moveTo(*pts[0]); [hp.lineTo(*p) for p in pts[1:]]; hp.close()
    c.save(); c.clipPath(hp, doAntiAlias=True); grad_rect(c, 500, -1000, 1400, -400, '#4A9AE8', '#AEE0FF')
    puff(c, 900 + lt * 20, -720, 60, 4, '#FFFFFF', '#D6E6F8', 255); c.restore(); c.drawPath(hp, ink(LW * 1.4))
    c.drawPath(cone_path(980, -650, 600, 1400, 1800), sp(linear(0, -650, 0, 1100, [hx('#FFF6DC', 120), hx('#FFF6DC', 0)]), blend=skia.BlendMode.kPlus))
    r = random.Random(2)
    for i in range(40):
        u = (r.random() + t * .1) % 1; c.drawCircle(r.uniform(600, 1350), -600 + u * 1600, r.uniform(2, 4), fp('#FFFFFF', 160))
    draw_char(c, 960, 1080, .7, HERO, face=0, eyes='wide', mouth='o', arms=('down', 'down'), tilt=-8, pupil=0, shadow=True)

def P4_cam(t, t0): k = ease(K(t, t0, 4.0)); return lerp(1.1, 1.0, k), 960, lerp(700, -200, k)

def P5_fist(c, t, t0):
    lt = t - t0
    hero_close(c, t, BG_STATION(), face=.2, eyes='dot', mouth='o', arms=('down', ('down', 'fist', K(lt, 0, .3))), pupil=.8, rim='#FFFFFF')
    hx_, hy_ = 760 + 70 * 2.15, 1400 - 270 * 2.15
    for i in range(3):
        u = (lt * .8 + i / 3) % 1; c.drawCircle(hx_ + math.sin(t * 3 + i) * 20, hy_ - 40 - u * 200, 14 + u * 20, fp('#C8C4D8', 140 * (1 - u)))

def P6_clean(c, t, t0):
    lt = t - t0
    grad_rect(c, -400, -300, W + 400, H + 300, '#3A3A5A', '#1E1E34')
    c.drawLine(1300, 1300, 980, 640, ink(170, boil=False)); c.drawLine(1300, 1300, 980, 640, ink(150, HERO['skin'], boil=False))
    circ(c, 960, 560, 190, HERO['skin'], LW * 1.4)
    for f in range(4): c.drawLine(840 + f * 80, 400, 850 + f * 78, 500, ink(6, '#C99068', boil=False))
    circ(c, 1140, 700, 38, '#1B1A20', LW)
    k = K(lt, .3, .5)
    if k > 0:
        st = skia.Path(); sx, sy = 1080, 420
        for i in range(8): r_ = (60 if i % 2 == 0 else 14) * pop(k); a = i * math.pi / 4; (st.moveTo if i == 0 else st.lineTo)(sx + r_ * math.cos(a), sy + r_ * math.sin(a))
        st.close(); c.drawPath(st, fp('#FFFFFF'))
    label(c, '0 scratches', 960, 900, 70, '#FFF6DC', FONT_HAND, 'center', stroke=8, skew=0, alpha=K(lt, .6, .3))

def P7_girl(c, t, t0):
    lt = t - t0
    blit(c, BG_STATION(), 0, 0, blur=12)
    draw_char(c, 960, 1450, 2.2, GIRL, face=.1, eyes='wide', mouth='o', arms=('heart', 'heart'), pupil=.3, sparkle=(lt * 1.2) % 2, blush=.8, shadow=False)

def P8_everyone(c, t, t0):
    lt = t - t0
    station(c, t, 1.0, False, 500)
    for i, (x, sp_) in enumerate(((260, TEENS[0]), (500, TEENS[1]), (1400, TEENS[2]), (1640, TEENS[3]), (380, OLDLADY), (1520, SHOUTER))):
        y = 1000 if i < 4 else 1060
        draw_char(c, x, y, .8, sp_, face=.6 if x < 960 else -.6, eyes='wide', mouth='o', arms=('down', 'down'), pupil=1 if x < 960 else -1)
    draw_char(c, 960, 1040, 1.0, HERO, face=0, eyes='dot', mouth='flat', arms=('down', 'down'), sweat=(lt * 1.2) % 1, pupil=math.sin(t * 3))

def P9_silver(c, t, t0):
    lt = t - t0; land = at('lands', t0) - .1; look = at('looks', t0)
    station(c, t, 1.0, False, 500)
    for i in range(6): puff(c, 300 + i * 260, 700 + math.sin(t + i) * 30, 120, i + 50, '#D9D3E6', '#9E95B8', 170, outline=False)
    if t < land:
        k = K(t, t0 + .4, land - t0 - .4); y = lerp(-400, 1000, ease(k) ** 2)
        draw_char(c, 1100, y, 1.0, SILVER, face=.2, eyes='half', mouth='smirk', arms=('up', 'up'), legs=((-20, -10, 40), (20, 10, 40)), rim='#FFFFFF')
        hscroll_lines(c, t, 0, H, '#FFFFFF', 0)
    else:
        sq = .2 * math.sin(K(t, land, .3) * math.pi); turn = math.sin((t - look) * 2.5) * .7 if t > look else .3
        draw_char(c, 1100, 1000, 1.0, SILVER, face=turn, eyes='half' if t < look else 'dot', mouth='smirk' if t < look else 'o', arms=('fist', 'hip') if t < look else ('hip', 'hip'), squash=sq, pupil=turn, rim='#FFFFFF')
        dt = t - land
        if dt < 1.2:
            for i in range(5): puff(c, 1100 + (i - 2) * 120 * (1 + dt * 2), 1000, 50, i + 60, '#D9D3E6', '#9E95B8', 255 * (1 - dt / 1.2))
            if dt < .4: ring = dt / .4; c.drawOval(skia.Rect(1100 - 600 * ring, 1000 - 60 * ring, 1100 + 600 * ring, 1000 + 60 * ring), ink(10, '#FFFFFF', 255 * (1 - ring), boil=False))

def P10_miss(c, t, t0):
    lt = t - t0
    blit(c, BG_STATION(), 0, 0, blur=12)
    draw_char(c, 900, 1420, 2.1, SILVER, face=math.sin(lt * 2) * .5, eyes='dot', mouth=talk(t) if talk(t) != 'flat' else 'o', arms=('down', 'chin'), pupil=math.sin(lt * 2), sweat=lt % 1, brow=.8, shadow=False)
    k = pop(K(lt, .4, .3))
    if k > 0: c.save(); c.translate(1400, 330); c.scale(k, k); label(c, '?', 0, 0, 200, '#F2C14E', MARKER, 'center', stroke=14, skew=0); c.restore()

def P11_funny(c, t, t0):
    lt = t - t0
    stage(c, t, tint='#3A2A5A')
    draw_char(c, 960, 900, 1.1, HERO, face=.25, eyes='closed', mouth='grin', arms=('down', 'chin'), blush=.9, sweat=(lt) % 1, tilt=6 * math.sin(t * 3))

def P12_cctv(c, t, t0):
    lt = t - t0
    grad_rect(c, -400, -300, W + 400, H + 300, '#B8BCC8', '#8A90A0')
    c.save(); c.translate(700, 380); c.rotate(20 + math.sin(t * 9) * 3 * max(0, 1 - lt))
    rect(c, -200, -70, 160, 70, '#E8ECF4', LW, 18); circ(c, -200, 0, 60, '#2A2E3A'); c.drawCircle(-200, 0, 30, fp('#5A1010'))
    c.drawLine(-240, -40, -160, 40, ink(6, '#FFFFFF')); c.drawLine(-220, 30, -170, -20, ink(4, '#FFFFFF'))
    c.restore(); rect(c, 820, 340, 860, 420, '#5A5A66', LW)
    rect(c, 1000, 560, 1700, 980, '#1A1A22', LW * 1.3, 20)
    c.save(); c.clipRect(skia.Rect(1020, 580, 1680, 960)); r = random.Random(int(t * 24))
    for i in range(400): c.drawRect(skia.Rect(1020 + r.uniform(0, 660), 580 + r.uniform(0, 380), 1020 + r.uniform(0, 660) + 8, 584 + r.uniform(0, 380)), fp('#FFFFFF', r.randint(40, 220)))
    c.restore(); label(c, 'NO SIGNAL', 1350, 800, 90, '#FF4A4A', MARKER, 'center', stroke=10, skew=0)
    r = random.Random(int(t * 12))
    if lt < 1.5:
        for i in range(8): a = r.uniform(0, 6.28); c.drawLine(500, 380, 500 + math.cos(a) * 80, 380 + math.sin(a) * 80, ink(4, '#FFD27A', boil=False))

def P13_dusty(c, t, t0):
    lt = t - t0
    station(c, t, 1.0, False, 500)
    c.drawRect(skia.Rect(-400, -300, W + 400, H + 300), fp('#C8C0B0', 170))
    for i in range(12): puff(c, (i * 220 + t * 30) % 2400 - 200, 300 + (i % 4) * 200, 140, i + 70, '#D8D0C4', '#B0A898', 200, outline=False)
    for i, x in enumerate((400, 800, 1300, 1600)):
        cough = abs(math.sin(t * 6 + i)) * 8
        c.save(); c.saveLayerAlpha(None, 150); draw_char(c, x, 1000 - cough, .8, TEENS[i], face=.3, eyes='closed', mouth='open', arms=('heart', 'down'), shadow=False); c.restore(); c.restore()

def P14_reporters(c, t, t0):
    lt = t - t0; h1 = at('half', t0); h2 = at('and the other', t0)
    street_day(c, t, 500)
    mic = lambda x, y: (rect(c, x - 10, y, x + 10, y + 70, '#2A2A34', LW * .6), circ(c, x, y - 10, 22, '#3A3A44', LW * .6))
    draw_char(c, 330, 1010, .9, REPORTER, face=.6, eyes='dot', mouth='flat', arms=('down', 'push'))
    if t < h1:
        draw_char(c, 1100, 1000, .9, TEENS[0], face=-.4, eyes='dot', mouth='flat', arms=('down', 'down')); draw_char(c, 1450, 1000, .9, TEENS[1], face=-.4, eyes='dot', mouth='flat', arms=('down', 'down'))
    elif t < h2:
        draw_char(c, 1100, 1000 - abs(math.sin(t * 8)) * 20, .95, TEENS[0], face=-.4, eyes='wide', mouth=talk(t) if talk(t) != 'flat' else 'grin', arms=('up', 'point'), sparkle=1.0)
        draw_char(c, 1450, 1000, .9, TEENS[1], face=-.6, eyes='half', mouth='flat', arms=('down', 'down'), pupil=-1)
        k = pop(K(t, h1 + .3, .3)); c.save(); c.translate(1100, 420); c.scale(k, k); rect(c, -150, -70, 150, 60, '#FFFFFF', LW, 30); draw_char(c, 0, 50, .2, HERO, face=0, eyes='dot', mouth='grin', arms=('up', 'down'), shadow=False); c.restore()
    else:
        draw_char(c, 1100, 1000, .9, TEENS[0], face=-.4, eyes='half', mouth='flat', arms=('down', 'down'))
        draw_char(c, 1450, 1000, .95, TEENS[1], face=-.3, eyes='closed', mouth=talk(t) if talk(t) != 'flat' else 'grin', arms=('laugh', 'point'), bob=abs(math.sin(t * 10)) * 10)
        k = pop(K(t, h2 + .3, .3)); c.save(); c.translate(1450, 420); c.scale(k, k); rect(c, -150, -70, 150, 60, '#FFFFFF', LW, 30); label(c, 'ZERO?? lol', 0, 14, 50, '#C8242C', MARKER, 'center', skew=0); c.restore()

def P15_news(c, t, t0):
    grad_rect(c, -400, -300, W + 400, H + 300, '#1E3A7A', '#0E1E4A')
    rect(c, 980, 120, 1780, 600, '#141826', LW * 1.3, 24)
    c.save(); c.clipRect(skia.Rect(990, 130, 1770, 590)); grad_rect(c, 990, 130, 1770, 590, '#B8C2D6', '#8E9AB4')
    draw_char(c, 1380, 1000, 1.5, SILVER, face=.2, eyes='half', mouth='grin', arms=('hip', 'up'), shadow=False); c.restore()
    draw_char(c, 600, 1000, 1.05, ANCHOR, face=.25, eyes='closed' if blink(t, 2.1) else 'dot', mouth=talk(t), arms=('down', 'present'))
    rect(c, 200, 760, 1100, 1100, '#2A3050', LW, 16)
    c.drawRect(skia.Rect(-400, 900, W + 400, 1000), fp('#C8242C')); c.drawLine(-400, 900, W + 400, 900, ink(LW)); c.drawLine(-400, 1000, W + 400, 1000, ink(LW))
    rect(c, 40, 880, 380, 1020, '#FFFFFF', LW, 10); label(c, 'EVENING', 210, 975, 60, '#C8242C', MARKER, 'center', skew=0)

def P16_headline(c, t, t0):
    lt = t - t0
    grad_rect(c, -400, -300, W + 400, H + 300, '#1E3A7A', '#0E1E4A')
    rect(c, 160, 80, 1760, 900, '#141826', LW * 1.4, 30); c.save(); c.clipRect(skia.Rect(180, 100, 1740, 880))
    grad_rect(c, 180, 100, 1740, 880, '#B8C2D6', '#6E7A94')
    draw_char(c, 700, 1300, 2.0, SILVER, face=.2, eyes='half', mouth='grin', arms=('hip', 'up'), sparkle=(lt * 1.3) % 2, shadow=False, rim='#FFFFFF')
    draw_storm(c, 1700, 900, .5, t, rear=.5, open_=.8 + .2 * math.sin(t * 9)); c.restore()
    c.drawRect(skia.Rect(160, 780, 1760, 900), fp('#C8242C'))
    x = 1800 - lt * 380; c.save(); c.clipRect(skia.Rect(160, 780, 1760, 900))
    label(c, 'SILVER HERO SCARES OFF STORM-LEVEL MONSTER  -  CITY SAVED  -', x, 868, 70, '#FFFFFF', MARKER, 'left', skew=0); c.restore()

def P17_bed(c, t, t0):
    lt = t - t0
    bedroom_night(c, t)
    draw_char(c, 900, 760, 1.0, HERO, face=.3, eyes='half', mouth='flat', arms=('down', ('down', 'heart', K(lt, .3, .4))), pupil=.8, shadow=False, tilt=5)
    night(c, [('pool', 900, 500, 600, .5), ('pool', 1470, 380, 400, .5)], ambient='#3E4D94')

def P18_uppercut(c, t, t0):
    lt = t - t0; hit = t0 + .9
    dx, dy = shake(t, hit, .6, 34); c.translate(dx, dy)
    station(c, t, 1.0, False, 500)
    up = K(t, hit - .2, .2)
    draw_char(c, 760, 1000, 1.05, HERO, face=.5, eyes='half', mouth='open' if t > hit - .2 else 'flat', arms=('fist', ('fist', 'up', up)), brow=-.6, squash=-.1 * math.sin(up * math.pi), rim='#FFB46A')
    if t < hit: draw_storm(c, 1350, 1180, 1.25, t, rear=.9, open_=.7)
    else:
        dt = t - hit; c.save(); c.translate(1200, 400 - dt * 1600); c.rotate(dt * 300); draw_storm(c, 0, 600, .9, t, rear=.6, open_=1); c.restore()
        hscroll_lines(c, t, 0, H, '#FFFFFF', 0); speed_lines(c, t, 1100, 300, '#FFFFFF', 150, 40, 300)

def P19_zero(c, t, t0):
    stage(c, t, tint='#3A1020')
    k = back(K(t, t0, .4), 1.4); license_card(c, 960, lerp(1400, 540, k), 1.25, t, k)
    g = .5 + .5 * math.sin(t * 6); add_light(c, 960 - 120 * 1.25, 540 + 175 * 1.25 - 40, 160, '#FF4A4A', 120 * g)

def P20_scanner(c, t, t0):
    lt = t - t0; b2 = at('or youre', t0)
    blit(c, BG_HALL(), 0, 0, blur=12)
    if t < b2:
        PV.scanner(c, 960, '0', -10, -5, t, land_col='#FF4A4A')
        r = random.Random(int(t * 12))
        for i in range(6): a = r.uniform(0, 6.28); c.drawLine(960, 420, 960 + math.cos(a) * 90, 420 + math.sin(a) * 90, ink(5, '#FFD27A', boil=False))
        c.drawLine(890, 300, 1010, 440, ink(6, '#FFFFFF'))
        k = pop(K(lt, .2, .3)); c.save(); c.translate(1400, 300); c.scale(k, k); label(c, 'BROKEN?', 0, 0, 100, '#F2C14E', MARKER, 'center', stroke=10, skew=0); c.restore()
    else:
        PV.scanner(c, 1300, '???', -10, -5, t, land_col='#FF4A4A')
        g = ease(K(t, b2, 1.0))
        for i in range(3): c.drawCircle(700, 600, 260 + i * 60 + 20 * math.sin(t * 4 + i), ink(10, '#FF8A3C', 200 * g * (1 - i * .3), boil=False))
        draw_char(c, 700, 900, 1.0, dict(HERO, skin='#1A1418', skin_d='#100C10', suit='#1A1418', suit_d='#100C10', hair_col='#1A1418', jeans='#1A1418', emblem='#FF8A3C', shoe='#1A1418', band='#1A1418'),
                  face=0, eyes='closed', mouth='flat', arms=('down', 'down'), rim='#FF8A3C')
        add_light(c, 700, 560, 500 * g, '#FF8A3C', 120)

def P21_need(c, t, t0):
    lt = t - t0
    hero_close(c, t, BG_NIGHT(), face=.15, eyes='half', mouth='flat', brow=-.6, brow_tilt=-.8, arms=('down', ('down', 'fist', K(lt, .3, .3))), rim='#FFB46A')

def P22_weeks(c, t, t0):
    lt = t - t0
    grad_rect(c, -400, -300, W + 400, H + 300, '#E8DCC0', '#C8B898')
    for i in range(14):
        k = K(lt, i * .18, .25); a = -ease(k) * 160
        c.save(); c.translate(960, 300); c.rotate(a if k < 1 else -160);
        if k < 1: rect(c, -280, 0, 280, 500, '#FFFFFF', LW, 10); label(c, f'DAY {i + 1}', 0, 180, 80, '#2A2E5A', MARKER, 'center', skew=0)
        c.restore()
    rect(c, 660, 240, 1260, 320, '#C8242C', LW, 10); label(c, 'EXPERIMENTS', 960, 302, 60, '#FFFFFF', MARKER, 'center', skew=0)

def park(c, t):
    grad_rect(c, -400, -300, W + 400, 760, '#6AB8F0', '#D8F0FF')
    for i in range(4): puff(c, (i * 600 + t * 15) % 2400 - 300, 140 + (i % 2) * 70, 60, i + 100, '#FFFFFF', '#D6E6F8', 255)
    grad_rect(c, -400, 740, W + 400, H + 300, '#7AC860', '#4E9A44', LW)
    for i in range(6): puff(c, -100 + i * 420, 720, 110, i + 110, '#5EAA54', '#3E8A3A', 255)

def P23_exp(c, t, t0, n):
    note_card(c, t, t0, f'Experiment {n}')

def P24_tree(c, t, t0):
    lt = t - t0; hit = t0 + 1.2
    park(c, t)
    rect(c, 1150, 300, 1250, 1000, '#7A5238', LW, 14); puff(c, 1200, 300, 260, 8, '#6EBB5E', '#4E9A44')
    wind = K(lt, 0, 1.0)
    draw_char(c, 900 if t < hit else 960, 1000, 1.1, HERO, face=.6, eyes='half', mouth='open' if t > hit - .3 else 'flat', brow=-.6,
              arms=('fist', ('fist', 'push', K(t, hit - .25, .2))) if t < hit + .1 else ('fist', 'push'), squash=-.05 * wind)
    if hit - .1 < t < hit + .2: speed_lines(c, t, 1150, 600, '#FFFFFF', 120, 30, 120)

def P25_nothing(c, t, t0):
    lt = t - t0
    park(c, t)
    rect(c, 1150, 300, 1250, 1000, '#7A5238', LW, 14); puff(c, 1200, 300, 260, 8, '#6EBB5E', '#4E9A44')
    draw_char(c, 960, 1000, 1.1, HERO, face=.6, eyes='dot', mouth='flat', arms=('fist', 'push'), sweat=lt % 1)
    y = 400 + lt * 300; c.save(); c.translate(1100 + math.sin(t * 4) * 40, y); c.rotate(math.sin(t * 3) * 40); oval(c, -20, -10, 20, 10, '#6EBB5E', LW * .6); c.restore()

def P26_ouch(c, t, t0):
    lt = t - t0
    park(c, t)
    hop = abs(math.sin(lt * 7)) * 60
    draw_char(c, 960, 1000 - hop, 1.1, HERO, face=.2, eyes='closed', mouth='open', arms=('down', 'heart'), blush=1.0, legs=((-26, 0, 0), (26, 20, 70)), tilt=8 * math.sin(lt * 7))
    for i in range(2):
        u = (lt * 2 + i * .5) % 1; c.drawCircle(960 - 70 + i * 140 + (i * 2 - 1) * u * 90, 1000 - hop - 1.1 * 420 + u * 140, 10, fp('#8FC8EE'))
    k = pop(K(lt, .6, .3))
    if k > 0: c.save(); c.translate(1400, 380); c.rotate(-8); c.scale(k, k); label(c, 'x3 days', 0, 0, 90, '#C8242C', FONT_HAND, 'center', stroke=8, stroke_col='#FFFFFF', skew=0); c.restore()

def P28_lift(c, t, t0):
    lt = t - t0
    street_day(c, t, 2600)
    strain = math.sin(t * 30) * 4
    draw_car(c, 1150, 1050, 1.3, '#4AB0E8')
    draw_char(c, 700 + strain, 1050, 1.05, HERO, face=.6, eyes='closed', mouth='open', arms=('push', 'push'), squash=.08 + .02 * math.sin(t * 20), blush=1.0, sweat=(lt * 2) % 1, brow=-.5)

def P29_nomove(c, t, t0):
    lt = t - t0
    street_day(c, t, 2600)
    draw_car(c, 1150, 1050, 1.3, '#4AB0E8')
    fall = ease(K(lt, .2, .5))
    c.save(); c.translate(700, 1050); c.rotate(-80 * fall); c.translate(-700, -1050)
    draw_char(c, 700, 1050, 1.05, HERO, face=.3, eyes='closed' if fall > .5 else 'dot', mouth='open', arms=('flail', 'flail') if fall > .5 else ('push', 'push'), shadow=fall < .5)
    c.restore()

def P30_bro(c, t, t0):
    lt = t - t0
    street_day(c, t, 2600 + lt * 40)
    draw_car(c, 1250, 1050, 1.3, '#4AB0E8')
    walker(c, t, lerp(300, 760, min(1, lt / 2.0)), 1010, 1.0, MAN, lt * 8, face=.4, eyes='dot', mouth=talk(t) if talk(t) != 'flat' else 'flat', arms=('down', 'shrug') if lt > 1.0 else walk_arms(lt * 8), brow=.8, pupil=.6)
    draw_char(c, 1000, 1050, 1.0, HERO, face=-.3, eyes='wide', mouth='o', arms=('push', 'push'), sweat=lt % 1, blush=.8)

def P32_angry(c, t, t0):
    lt = t - t0; pan = lt * 220
    street_day(c, t, 3400 + pan)
    walker(c, t, 960, 1000, 1.05, HERO, lt * 11, face=.55, eyes='half', mouth='frown', brow=-.8, brow_tilt=-1.0, arms=('fist', 'fist'))
    puff(c, 960 + 40, 340 + math.sin(t * 3) * 10, 90, 4, '#4A4A5A', '#2E2E3A', 255)
    if int(t * 6) % 3 == 0: poly(c, [(960, 400), (930, 470), (960, 470), (935, 540), (1000, 450), (965, 450)], '#F2D36B', LW * .6)

def P33_cousin(c, t, t0):
    lt = t - t0
    living_room(c, t)
    draw_char(c, 1300, 1000, 1.0, HERO, face=-.4, eyes='half', mouth='frown', arms=('down', 'down'), brow=-.6, pupil=-.6)
    draw_char(c, 700, 1020, .7, COUSIN, face=.5, eyes='closed' if int(t * 3) % 2 else 'half', mouth=talk(t) if talk(t) != 'flat' else 'grin', arms=('laugh', 'point'), bob=abs(math.sin(twos(t) * 8)) * 12, blush=.6)

def wrestle_table(c):
    rect(c, 560, 760, 1360, 810, '#8C5E3F', LW, 6); rect(c, 600, 810, 640, 1080, '#6E4A33', LW); rect(c, 1280, 810, 1320, 1080, '#6E4A33', LW)

def P34_challenge(c, t, t0):
    lt = t - t0
    living_room(c, t); wrestle_table(c)
    draw_char(c, 520, 980, 1.0, HERO, face=.5, eyes='half', mouth='smirk', arms=('down', ('down', 'push', K(lt, .2, .3))), shadow=False)
    draw_char(c, 1400, 960, .7, COUSIN, face=-.5, eyes='half', mouth='grin', arms=(('down', 'push', K(lt, .3, .3)), 'down'), shadow=False)
    wrestle_table(c) if False else None

def P35_hands(c, t, t0):
    lt = t - t0
    grad_rect(c, -400, -300, W + 400, H + 300, '#5A3A2A', '#2A1A14')
    rect(c, -400, 760, W + 400, H + 300, '#8C5E3F', LW)
    g = ease(K(lt, .6, 1.5)) * (.8 + .2 * math.sin(t * 9))
    c.drawLine(300, 1100, 900, 620, ink(160, boil=False)); c.drawLine(300, 1100, 900, 620, ink(140, HERO['skin'], boil=False))
    c.drawLine(1620, 1100, 1020, 620, ink(110, boil=False)); c.drawLine(1620, 1100, 1020, 620, ink(92, COUSIN['skin'], boil=False))
    circ(c, 1010, 600, 110, COUSIN['skin'], LW * 1.2); circ(c, 920, 590, 140, HERO['skin'], LW * 1.3)
    add_light(c, 940, 590, 420 * g, '#FF8A3C', 140 * g); c.drawCircle(920, 590, 150, ink(10, '#FFB45C', 230 * g, boil=False))
    r = random.Random(int(t * 12) // 2)
    for i in range(int(30 * g)): c.drawCircle(r.uniform(760, 1120), 560 - ((t * 200 + i * 33) % 400), r.uniform(2, 5), fp('#FFB45C', 220))

def P36_cscream(c, t, t0):
    lt = t - t0
    living_room(c, t)
    k = K(lt, 0, 1.2); x = lerp(1100, 1700, ease_out(k)); y = 900 - math.sin(k * math.pi) * 400
    c.save(); c.translate(x, y - 200); c.rotate(k * 540); c.translate(-x, -(y - 200))
    draw_char(c, x, y, .7, COUSIN, face=0, eyes='shock', mouth='open', arms=('up', 'up'), shadow=False); c.restore()
    hscroll_lines(c, t, 300, 900, '#FFFFFF', 90, 2000)

def P37_aunt(c, t, t0):
    lt = t - t0
    living_room(c, t)
    rect(c, 700, 160, 1220, 1000, '#6A4A3A', LW, 8); c.drawRect(skia.Rect(720, 180, 1200, 990), fp('#2A1E18'))
    draw_char(c, 960, 1000, 1.1, AUNT, face=0, eyes='shock', mouth='open', arms=('up', 'up'), bob=abs(math.sin(t * 20)) * 6, sweat=lt % 1)
    c.save(); c.translate(960 + 170 * 1.1, 1000 - 470 * 1.1); c.rotate(-30); circ(c, 0, -60, 60, '#3A3A44'); rect(c, -8, 0, 8, 90, '#6A4A3A', LW * .7); c.restore()

def P38_table(c, t, t0):
    lt = t - t0
    living_room(c, t)
    c.save(); c.translate(760, 1000); c.rotate(-25); rect(c, -200, -40, 200, 0, '#8C5E3F', LW, 6); c.restore()
    c.save(); c.translate(1160, 1000); c.rotate(25); rect(c, -200, -40, 200, 0, '#8C5E3F', LW, 6); c.restore()
    for i in range(4): puff(c, 960 + (i - 1.5) * 140, 1000 - lt * 30, 50 + lt * 10, i + 40, '#D8CCB8', '#B0A490', 200 * max(0, 1 - lt / 2.5))
    draw_char(c, 960, 960, 1.0, HERO, face=.1, eyes='closed', mouth='grin', arms=('down', 'chin'), blush=1.0, sweat=lt % 1, tilt=5)

def P39_understand(c, t, t0):
    lt = t - t0
    grad_rect(c, -400, -300, W + 400, H + 300, '#2A2A6A', '#E8906A')
    city = cached('dawncity', lambda cc: city_strip(cc, 1050, 71, 150, 420, 80, 160, '#2A2050', '#1E1840', '#FFB46A', .2, outline=False)); blit(c, city)
    draw_char(c, 960, 960, 1.1, HERO, face=0, eyes='wide' if lt > .6 else 'half', mouth='o' if lt > .6 else 'flat', arms=('down', 'down'), rim='#FFB46A', brow=.6)
    k = pop(K(lt, .6, .3))
    if k > 0:
        c.save(); c.translate(960, 300); c.scale(k, k); circ(c, 0, 0, 60, '#FFE88A', LW); rect(c, -24, 50, 24, 90, '#B8BCC8', LW * .8, 6); add_light(c, 0, 0, 200, '#FFE88A', 160)
        for i in range(8): a = i * math.pi / 4; c.drawLine(math.cos(a) * 80, math.sin(a) * 80, math.cos(a) * 110, math.sin(a) * 110, ink(6, '#FFE88A', boil=False))
        c.restore()

def streams(c, t, src, dst, k=1.0, col_='#FF8A3C'):
    for j, (sx, sy) in enumerate(src):
        for i in range(6):
            u = ((t * .9 + i / 6 + j * .13) % 1)
            if u > k: continue
            x = lerp(sx, dst[0], u) + math.sin(u * 9 + j) * 30; y = lerp(sy, dst[1], u) - math.sin(u * math.pi) * 120
            c.drawCircle(x, y, 7, fp(col_, 230)); add_light(c, x, y, 30, col_, 120)

def P40_source(c, t, t0):
    lt = t - t0; b = at('it comes from', t0)
    grad_rect(c, -400, -300, W + 400, H + 300, '#0E0C24', '#1E1640')
    draw_char(c, 960, 900, 1.1, dict(HERO, suit='#2A2440', suit_d='#1E1A30', skin='#3A3450', skin_d='#2A2440', hair_col='#2A2440', jeans='#2A2440', emblem='#4A4470', band='#2A2440', shoe='#2A2440'), face=0, eyes='dot', mouth='flat', arms=('down', 'down'), rim='#8A80C0')
    cx, cy = 960, 900 - 240 * 1.1
    if t < b:
        c.drawCircle(cx, cy, 70, ink(8, '#8A80C0', 200, boil=False)); label(c, 'EMPTY', cx, cy + 15, 40, '#8A80C0', MARKER, 'center', skew=0)
    else:
        src = [(150 + i * 230, 300 + (i % 2) * 400) for i in range(8) if abs(150 + i * 230 - 960) > 250]
        for (sx, sy) in src: draw_char(c, sx, sy + 260, .45, TEENS[int(sx) % 4], face=.5 if sx < 960 else -.5, eyes='closed', mouth='open', arms=('laugh', 'point'), shadow=False)
        streams(c, t, [(x, y) for x, y in src], (cx, cy), ease(K(t, b, 1.0)))
        add_light(c, cx, cy, 260, '#FF8A3C', 140 * K(t, b + .5, .8))

def P41_laughs(c, t, t0):
    lt = t - t0
    stage(c, t, tint='#2A1E3A', spot=True)
    meter = min(1, lt / 7.0)
    draw_char(c, 960, 900, 1.0, HERO, face=0, eyes='half', mouth='flat', arms=('fist', 'fist'), rim='#FF8A3C')
    people = [(220, 900, TEENS[0]), (460, 950, KIDS[1]), (1460, 950, SHOUTER), (1700, 900, TEENS[2])]
    for i, (x, y, sp_) in enumerate(people):
        if lt > i * 1.2: draw_char(c, x, y, .75, sp_, face=.5 if x < 960 else -.5, eyes='closed', mouth='open', arms=('laugh', 'point'), bob=abs(math.sin(t * 9 + i)) * 10)
    streams(c, t, [(x, y - 400) for (x, y, _) in people[:int(lt / 1.2) + 1]], (960, 640))
    rect(c, 1780, 200, 1860, 800, '#141826', LW, 14); c.drawRect(skia.Rect(1792, 788 - 576 * meter, 1848, 788), fp('#FF8A3C')); add_light(c, 1820, 788 - 576 * meter, 100, '#FF8A3C', 140)

def P42_boxer(c, t, t0):
    lt = t - t0
    stage(c, t, tint='#3A1E1E')
    draw_char(c, 400, 900, .8, TEENS[1], face=.6, eyes='closed', mouth='open', arms=('laugh', 'point'), bob=abs(math.sin(t * 9)) * 8)
    k = ease(K(lt, .5, .8))
    c.save(); c.saveLayerAlpha(None, int(150 * k)); draw_char(c, 1150, 940, 1.5, dict(SHOUTER, suit='#C8242C', suit_d='#9A1A20', hair='bald', jeans='#C8242C', glove='#C8242C'), face=-.2, eyes='half', mouth='smirk', arms=('fist', 'fist'), shadow=False); c.restore(); c.restore()
    draw_char(c, 1150, 900, 1.0, HERO, face=-.2, eyes='half', mouth='smirk', arms=('fist', 'fist'), rim='#FF8A3C')
    streams(c, t, [(400, 500)], (1150, 640))
    label(c, 'HEAVYWEIGHT', 1150, 220, 80, '#FF8A3C', MARKER, 'center', stroke=10, skew=0, alpha=k)

def P43_crowd(c, t, t0):
    lt = t - t0
    grad_rect(c, -400, -300, W + 400, H + 300, '#1A0A10', '#3A1414')
    crowd_heads(c, t, 1000, 1.0, 21, 10, .5, rim='#FF8A3C'); crowd_heads(c, t, 1120, 1.25, 22, 9, .5, rim='#FF8A3C')
    streams(c, t, [(100 + i * 190, 900) for i in range(10)], (960, 300))
    add_light(c, 960, 300, 400, '#FF8A3C', 200); circ(c, 960, 300, 60, '#FFB45C', LW)

def P44_wasacrowd(c, t, t0):
    lt = t - t0
    dx, dy = shake(t, t0 + .3, .8, 26); c.translate(dx, dy)
    blit(c, BG_STATION(), 0, 0, blur=8)
    c.drawRect(skia.Rect(-400, -300, W + 400, H + 300), fp('#5A2010', 120))
    crowd_heads(c, t, 1100, 1.2, 9, 8, .3, rim='#FF8A3C')
    speed_lines(c, t, 960, 500, '#FFB45C', 200, 70, 300)
    flame(c, 960, 620, 2.4, t, 1); add_light(c, 960, 500, 700, '#FFC870', 200)

def P45_think(c, t, t0):
    hero_close(c, t, BG_NIGHT(), face=.3, eyes='half', mouth='flat', arms=('down', 'chin'), pupil=.8, rim='#A9BCFF')

def P46_city(c, t, t0):
    lt = t - t0
    grad_rect(c, -400, -300, W + 400, H + 300, '#5FA8E8', '#CFE8FF')
    city = cached('daycity2', lambda cc: city_strip(cc, 1080, 81, 250, 700, 100, 200, '#A9C2E2', '#8EA8CE', '#E6F0FF', .3))
    blit(c, city)
    words = ['ZERO', 'lol', 'WEAKEST', 'haha', 'ZERO KID', 'loser', 'lmao', 'ZERO']
    r = random.Random(4)
    for i, w in enumerate(words):
        k = pop(K(lt, .2 + i * .5, .3))
        if k <= 0: continue
        x = r.uniform(200, 1700); y = r.uniform(200, 700)
        c.save(); c.translate(x, y); c.scale(k, k); rect(c, -len(w) * 24 - 30, -60, len(w) * 24 + 30, 40, '#FFFFFF', LW, 30)
        poly(c, [(-20, 38), (10, 38), (-30, 80)], '#FFFFFF', LW); label(c, w, 0, 10, 56, '#C8242C', MARKER, 'center', skew=0); c.restore()

def P47_millions(c, t, t0):
    lt = t - t0
    grad_rect(c, -400, -300, W + 400, H + 300, '#14102A', '#2A2050')
    n = int(min(1, lt / 1.4) * 240)
    for i in range(n):
        x = 160 + (i % 24) * 66; y = 260 + (i // 24) * 66
        c.drawCircle(x, y, 16, fp(TEENS[i % 4]['suit'])); c.drawCircle(x, y - 26, 12, fp(TEENS[i % 4]['skin']))
    num = int(min(1, lt / 1.4) * 4200000)
    label(c, f'{num:,}', 960, 1000, 120, '#F2C14E', MARKER, 'center', stroke=12, skew=0)

def P48_memes(c, t, t0):
    lt = t - t0; b = at('charging', t0) - .3
    grad_rect(c, -400, -300, W + 400, H + 300, '#2A2050', '#14102A')
    def scr(cc, tt): grad_rect(cc, -180, -340, 180, 340, '#E8D06A', '#C8A04A'); draw_char(cc, 0, 300, .7, HERO, face=0, eyes='dot', mouth='flat', shadow=False); label(cc, 'lol', 0, -220, 80, '#C8242C', MARKER, 'center', stroke=6, skew=0)
    if t < b:
        for i in range(6):
            k = back(K(lt, i * .3, .3), 1.6)
            if k > 0: phone_ui(c, 220 + i * 300, 560 + (i % 2) * 60, .55 * k, scr, t)
    else:
        lv = ease(K(t, b, 2.6))
        rect(c, 560, 260, 1360, 820, '#141826', LW * 1.4, 40); rect(c, 1360, 440, 1420, 640, '#141826', LW, 12)
        c.drawRect(skia.Rect(590, 290, 590 + 740 * lv, 790), fp('#B8F04A' if lv < .99 else '#FF8A3C'))
        for i in range(5): c.drawLine(590 + i * 148, 290, 590 + i * 148, 790, ink(4, '#141826', boil=False))
        draw_char(c, 960, 760, .8, HERO, face=0, eyes='half', mouth='smirk', arms=('fist', 'fist'), shadow=False)
        add_light(c, 960, 540, 600 * lv, '#B8F04A', 80)
        poly(c, [(940, 140), (900, 220), (950, 220), (920, 290), (1000, 190), (950, 190)], '#F2D36B')

def P49_measure(c, t, t0):
    lt = t - t0; b = at('and yours', t0)
    blit(c, BG_HALL(), 0, 0, blur=12)
    PV.scanner(c, 1350, '0', -10, -5, t, land_col='#FF4A4A')
    draw_char(c, 700, 900, 1.0, HERO, face=.4, eyes='dot', mouth='flat', arms=('down', 'scan'))
    y = 400 + ((lt * 300) % 500); c.drawLine(450, y, 950, y, ink(8, '#7CF2E0', 220, boil=False)); add_light(c, 700, y, 200, '#7CF2E0', 80)
    if t > b:
        k = pop(K(t, b, .3)); c.save(); c.translate(700, 260); c.scale(k, k); rect(c, -260, -70, 260, 50, '#FFFFFF', LW, 30); label(c, 'NOT MINE?!', 0, 10, 64, '#C8242C', MARKER, 'center', skew=0); c.restore()

def P50_borrowed(c, t, t0):
    lt = t - t0
    grad_rect(c, -400, -300, W + 400, H + 300, '#1E1A3A', '#0E0C1E')
    src = [(160, 300), (420, 180), (1500, 180), (1760, 300), (160, 800), (1760, 800), (500, 950), (1420, 950)]
    for i, (x, y) in enumerate(src): draw_char(c, x, y + 200, .4, TEENS[i % 4], face=.5 if x < 960 else -.5, eyes='half', mouth='smirk', arms=('down', 'point'), shadow=False)
    draw_char(c, 960, 900, 1.0, HERO, face=0, eyes='closed', mouth='flat', arms=('down', 'down'), rim='#FF8A3C')
    streams(c, t, src, (960, 640))
    label(c, 'BORROWED', 960, 180, 110, '#FF8A3C', MARKER, 'center', stroke=12, skew=0, alpha=K(lt, .3, .4))

def P51_scale(c, t, t0):
    lt = t - t0
    stage(c, t, tint='#1E2A4A')
    tilt = ease(K(lt, .5, 2.5)) * 22 + math.sin(t * 2) * 1.5
    rect(c, 940, 300, 980, 900, '#C8A04A', LW); poly(c, [(860, 900), (1060, 900), (960, 840)], '#C8A04A')
    c.save(); c.translate(960, 320); c.rotate(-tilt)
    rect(c, -560, -14, 560, 14, '#E8C060', LW, 8)
    for sx, txt, cl in ((-1, 'WORLD THINKS: WEAK', '#8A90A0'), (1, 'YOU: STRONG', '#FF8A3C')):
        c.save(); c.translate(sx * 520, 0); c.rotate(tilt)
        c.drawLine(-120, 200, 0, 0, ink(4)); c.drawLine(120, 200, 0, 0, ink(4)); oval(c, -170, 180, 170, 240, '#E8C060', LW)
        label(c, txt, 0, 300, 50, cl, MARKER, 'center', stroke=8, skew=0)
        if sx < 0: rect(c, -90, 100, 90, 186, '#5A5A66', LW, 10); label(c, '10 TONS', 0, 160, 34, '#FFFFFF', MARKER, 'center', skew=0)
        else: draw_char(c, 0, 180, .45, HERO, face=0, eyes='half', mouth='smirk', arms=('fist', 'up'), shadow=False)
        c.restore()
    c.restore()

def P52_happy(c, t, t0):
    bedroom_night(c, t)
    draw_char(c, 900, 760, 1.0, HERO, face=.2, eyes='closed', mouth='smile', arms=('down', 'down'), blush=.6, shadow=False)
    night(c, [('pool', 900, 500, 600, .55)], ambient='#4A5AA0')

def P53_cold(c, t, t0):
    lt = t - t0; k = ease(K(lt, 0, 1.2))
    bedroom_night(c, t)
    draw_char(c, 900, 760, 1.0, HERO, face=.1, eyes='wide', mouth='o', arms=('down', 'heart'), pupil=0, shadow=False, rim='#9FD6FF')
    night(c, [('pool', 900, 500, 600, .4 * (1 - k) + .1)], ambient='#2A3A7A')
    c.drawRect(skia.Rect(-400, -300, W + 400, H + 300), fp('#5A8AE8', 70 * k, blend=skia.BlendMode.kPlus))
    for i in range(12):
        a = i / 12 * 6.28; r0 = 1000 - 300 * k; c.drawLine(960 + math.cos(a) * r0, 540 + math.sin(a) * r0, 960 + math.cos(a) * (r0 + 300), 540 + math.sin(a) * (r0 + 300), ink(12, '#DDEEFF', 160 * k, boil=False))

def P54_stop(c, t, t0):
    lt = t - t0
    stage(c, t, tint='#1A1A2A', spot=False)
    crowd_heads(c, t, 1050, 1.0, 33, 9, .0, rim='#5A5A70')
    lv = 1 - ease(K(lt, .3, 2.0))
    rect(c, 660, 200, 1260, 600, '#141826', LW * 1.4, 34); rect(c, 1260, 330, 1310, 470, '#141826', LW, 10)
    c.drawRect(skia.Rect(690, 230, 690 + 540 * lv, 570), fp('#FF4A4A' if lv < .3 else '#B8F04A'))
    if lv < .3 and int(t * 4) % 2: label(c, '!', 960, 470, 220, '#FFFFFF', MARKER, 'center', skew=0)
    label(c, 'shh...', 960, 820, 90, '#9AA4B8', FONT_HAND, 'center', skew=0, alpha=K(lt, .6, .4))

def P55_secret(c, t, t0):
    lt = t - t0
    bedroom_night(c, t)
    draw_char(c, 900, 760, 1.0, HERO, face=.2, eyes='half', mouth='flat', arms=('down', ('down', 'chin', K(lt, .2, .3))), shadow=False)
    if lt > .6: c.drawLine(900 - 20, 760 - 375, 900 + 30, 760 - 375, ink(6, boil=False)); [c.drawLine(900 - 15 + i * 12, 760 - 385, 900 - 15 + i * 12, 760 - 365, ink(3, boil=False)) for i in range(4)]
    night(c, [('pool', 900, 500, 600, .5)], ambient='#3E4D94')

def P56_someone(c, t, t0):
    lt = t - t0
    grad_rect(c, -400, -300, W + 400, H + 300, '#06060E', '#14102A')
    k = ease(K(lt, 0, 1.5))
    draw_char(c, 960, 1000, 1.1, dict(MIRA, skin='#14121C', skin_d='#0E0C14', suit='#14121C', suit_d='#0E0C14', hair_col='#0A0A10', jeans='#14121C', vest='#14121C', glove='#14121C', band='#14121C'),
              face=.1, eyes='closed', mouth='flat', arms=('down', 'down'), rim='#7CF2E0', shadow=False)
    for gx in (-30, 30): add_light(c, 960 + gx * 1.1 + 4, 1000 - 489 * 1.1, 60, '#7CF2E0', 230 * k)
    drone(c, 1450, 400, 1.0, t)

def P57_mira(c, t, t0):
    lt = t - t0
    grad_rect(c, -400, -300, W + 400, H + 300, '#1E4A5A', '#0E2A34')
    for i in range(10): c.drawLine(-400, 200 + i * 90 + (t * 40) % 90, W + 400, 200 + i * 90 + (t * 40) % 90, ink(2, '#7CF2E0', 40, boil=False))
    draw_char(c, 700, 1000, 1.15, MIRA, face=.35, eyes='half', mouth='smirk', arms=('hip', 'down'), rim='#7CF2E0', sparkle=K(lt, .4, .5) * 1.6, squash=.06 * math.sin(K(lt, 0, .25) * math.pi))
    drone(c, 1100, 360, .9, t)
    k = back(K(lt, .2, .4), 1.4)
    c.save(); c.translate(1300 + (1 - k) * 600, 760)
    rect(c, -260, -80, 420, 80, '#141826', LW, 12); c.drawRect(skia.Rect(-252, -72, -230, 72), fp('#7CF2E0'))
    label(c, 'MIRA OKAFOR', -200, 18, 76, '#FFFFFF', KALAM, 'left', skew=0); c.restore()

def P58_silver(c, t, t0):
    lt = t - t0
    grad_rect(c, -400, -300, W + 400, H + 300, '#1E4A5A', '#0E2A34')
    draw_char(c, 600, 1000, 1.0, MIRA, face=.4, eyes='half', mouth='smirk', arms=('hip', 'down'), rim='#7CF2E0')
    k = back(K(lt, 0, .35), 1.6); badge(c, 1250, 520, .9 * k, 'SILVER')

def P59_540(c, t, t0):
    blit(c, BG_HALL(), 0, 0, blur=12)
    PV.scanner(c, 1250, '540', t0 - .2, t0 + .4, t, land_col='#7CF2E0')
    draw_char(c, 900, 900, 1.0, MIRA, face=.5, eyes='half', mouth='smirk', arms=('down', 'scan'))
    night(c, [('pool', 1050, 500, 900, .62)], ambient='#6670B2')

def P60_gadgets(c, t, t0):
    lt = t - t0; b1 = at('flies', t0); b2 = at('and she was', t0)
    if t < b1:
        grad_rect(c, -400, -300, W + 400, H + 300, '#3A3A4A', '#1E1E28')
        rect(c, 200, 760, 1720, 810, '#6A5A4A', LW, 6)
        for i in range(5): c.save(); c.translate(400 + i * 110, 300); c.rotate(math.sin(t + i) * 5); rect(c, -12, 0, 12, 120, '#8A90A0', LW * .7, 4); c.restore()
        draw_char(c, 900, 1000, 1.0, MIRA, face=.3, eyes='dot', mouth='flat', arms=('hold', ('lin', 'hold', 'draw', .5 + .5 * math.sin(t * 12))), pupil=.6)
        r = random.Random(int(t * 10))
        for i in range(6): a = r.uniform(3.4, 6); c.drawLine(1100, 740, 1100 + math.cos(a) * 60, 740 + math.sin(a) * 60, ink(4, '#FFD27A', boil=False))
        drone(c, 1150, 700, .7, t)
    elif t < b2:
        grad_rect(c, -400, -300, W + 400, H + 300, '#5FA8E8', '#CFE8FF')
        city = cached('daycity2', lambda cc: city_strip(cc, 1080, 81, 250, 700, 100, 200, '#A9C2E2', '#8EA8CE', '#E6F0FF', .3)); blit(c, city)
        for i in range(4): drone(c, (300 + i * 400 + (t - b1) * 300) % 2200 - 100, 300 + i * 80, .9, t)
        draw_char(c, (600 + (t - b1) * 260) % 2200 - 100, 560, .9, MIRA, face=.6, eyes='half', mouth='grin', arms=('up', 'hip'), legs=((-20, -20, 30), (20, 10, 30)), shadow=False)
        drone(c, (600 + (t - b1) * 260) % 2200 - 100, 600, 1.4, t)
    else:
        station(c, t, 1.0, False, 500)
        k = ease_out(K(t, b2, .6)); draw_char(c, lerp(-200, 500, k), 1000, .9, MIRA, face=.5, eyes='dot', mouth='o', arms=('down', 'down'), legs=walk_legs(t * 10) if k < .98 else None)
        label(c, '#2', 500, 400, 100, '#7CF2E0', MARKER, 'center', stroke=10, skew=0, alpha=K(t, b2 + .4, .3))

def P61_looked(c, t, t0):
    lt = t - t0
    station(c, t, 1.0, False, 500)
    draw_char(c, 760, 1020, 1.0, MIRA, face=.2, eyes='dot', mouth='o', arms=('down', 'hold'), tilt=-14, pupil=0, rim='#FFFFFF')
    c.drawPath(cone_path(1100, -100, 300, 600, 1000, -200), sp(linear(0, -100, 0, 900, [hx('#FFF6DC', 90), hx('#FFF6DC', 0)]), blend=skia.BlendMode.kPlus))
    drone(c, 1100, 300, .8, t); c.drawPath(cone_path(1100, 310, 20, 300, 400, 0), sp(linear(0, 310, 0, 710, [hx('#7CF2E0', 90), hx('#7CF2E0', 0)]), blend=skia.BlendMode.kPlus))

def mira_talk(c, t, t0, hero_mouth='flat', hero_eyes='dot', mira_arm='present', tab=None, mira_face=-.4):
    fire_escape(c, t)
    draw_char(c, 1300, 860, 1.0, MIRA, face=mira_face, eyes='closed' if blink(t, 2.4) else 'half', mouth=talk(t), arms=('hold', mira_arm), shadow=False, rim='#7CF2E0')
    draw_char(c, 760, 860, 1.0, HERO, face=.4, eyes=hero_eyes, mouth=hero_mouth, arms=('down', 'down'), shadow=False, rim='#A9BCFF')
    if tab: tablet(c, 1300 - 150, 860 - 300, .35, tab, t)
    night(c, [('pool', 320, 620, 500, .6), ('pool', 1000, 600, 700, .45)], ambient='#4A4A90')

def P62_up(c, t, t0): mira_talk(c, t, t0, tab=lambda cc, tt: (grad_rect(cc, -276, -186, 276, 186, '#0E2A34', '#1E4A5A'), label(cc, 'DATA', 0, 20, 90, '#7CF2E0', MARKER, 'center', skew=0)))

def tab_arrows(cc, tt, t0, mode):
    grad_rect(cc, -276, -186, 276, 186, '#0E2A34', '#1E4A5A')
    for i in range(8): cc.drawLine(-276, -186 + i * 50, 276, -186 + i * 50, ink(1, '#7CF2E0', 50, boil=False))
    circ(cc, 0, 0, 30, '#9AE0B0', LW * .6)
    if mode == 'dirs':
        for j, (dx, dy, cl) in enumerate(((1, 0, '#9AA4B8'), (-1, 0, '#9AA4B8'), (0, 1, '#9AA4B8'), (0, -1, '#FF4A4A'))):
            k = ease(K(tt, t0 + j * .5, .4)); L = 150 * k
            if k > 0: cc.drawLine(dx * 40, dy * 40, dx * (40 + L), dy * (40 + L), ink(12, cl, boil=False))
    else:
        k = ease(K(tt, t0 + .2, .5)); cc.drawLine(0, 180, 0, 180 - 150 * k, ink(14, '#FF8A3C', boil=False)); poly(cc, [(-20, 30 + 120 * (1 - k)), (20, 30 + 120 * (1 - k)), (0, 0 + 120 * (1 - k))], '#FF8A3C', LW * .5)
        if k >= 1: cc.drawCircle(0, 0, 60, ink(6, '#FF8A3C', 200, boil=False))

def P63_dirs(c, t, t0):
    fire_escape(c, t)
    tablet(c, 960, 520, 1.4, lambda cc, tt: tab_arrows(cc, tt, t0, 'dirs'), t)

def P64_below(c, t, t0):
    fire_escape(c, t)
    tablet(c, 960, 520, 1.4, lambda cc, tt: tab_arrows(cc, tt, t0, 'below'), t)

def P65_400(c, t, t0):
    lt = t - t0
    def scr(cc, tt):
        grad_rect(cc, -276, -186, 276, 186, '#0E2A34', '#1E4A5A')
        cc.drawRect(skia.Rect(-200, 140 - 20, -100, 140), fp('#7CF2E0')); label(cc, 'MIRA', -150, 170, 28, '#7CF2E0', MARKER, 'center', skew=0)
        h = 300 * ease(K(tt, t0 + .4, 1.4)); cc.drawRect(skia.Rect(60, 140 - h, 200, 140), fp('#FF8A3C')); label(cc, '???', 130, 170, 28, '#FF8A3C', MARKER, 'center', skew=0)
        label(cc, 'x400', 130, 120 - h, 60, '#FFFFFF', MARKER, 'center', skew=0)
    fire_escape(c, t); tablet(c, 960, 520, 1.4, scr, t)

def drone_frame(cc, tt):
    grad_rect(cc, -276, -186, 276, 186, '#8A8A98', '#5A5A68')
    cc.save(); p = skia.Paint(); p.setImageFilter(skia.ImageFilters.Blur(6, 6)); cc.saveLayer(None, p)
    draw_char(cc, 0, 260, .7, HERO, face=0, eyes='dot', mouth='flat', arms=('down', 'up'), shadow=False); cc.restore(); cc.restore()
    r = random.Random(int(tt * 12))
    for i in range(60): cc.drawRect(skia.Rect(r.uniform(-276, 276), r.uniform(-186, 186), r.uniform(-276, 276) + 30, r.uniform(-186, 186) + 2), fp('#FFFFFF', 40))
    label(cc, 'REC  DRONE-02', -250, -150, 26, '#FF4A4A', MARKER, 'left', skew=0)

def P66_turn(c, t, t0):
    lt = t - t0; k = ease(K(lt, .2, .8))
    fire_escape(c, t)
    draw_char(c, 1300, 860, 1.0, MIRA, face=-.4, eyes='half', mouth='smirk', arms=('hold', 'present'), shadow=False, rim='#7CF2E0')
    c.save(); c.translate(lerp(1150, 1000, k), 560); c.scale(lerp(.35, .6, k) * abs(math.cos(k * math.pi)) + .02, lerp(.35, .6, k))
    rect(c, -300, -210, 300, 210, '#1A1A22', LW * 1.2, 26)
    if k > .5: c.save(); sc = skia.Path(); sc.addRRect(skia.RRect.MakeRectXY(skia.Rect(-276, -186, 276, 186), 12, 12)); c.clipPath(sc); drone_frame(c, t); c.restore()
    c.restore()
    draw_char(c, 600, 860, 1.0, HERO, face=.4, eyes='wide' if k > .5 else 'dot', mouth='o' if k > .5 else 'flat', arms=('down', 'down'), shadow=False, rim='#A9BCFF', pupil=.6)

def P67_blurry(c, t, t0):
    lt = t - t0; zoom = 1.6
    b1 = at('a red', t0 - 3) if t0 > 0 else t0
    fire_escape(c, t)
    tablet(c, 960, 540, 2.2, drone_frame, t)

def P67_cam(t, t0, mode):
    if mode == 'blur': return 1.0, 960, 540
    if mode == 'red': k = ease(K(t, t0, .6)); return lerp(1.0, 1.8, k), 960, lerp(540, 600, k)
    k = ease(K(t, t0, .6)); return lerp(1.8, 3.2, k), lerp(960, 960, k), lerp(600, 560, k)

def P68_mark(c, t, t0, mode):
    fire_escape(c, t); tablet(c, 960, 540, 2.2, drone_frame, t)
    k = ease(K(t, t0 + .1, .5))
    cx, cy, r = (960, 640, 300) if mode == 'red' else (960, 731, 120)
    arc = skia.Path(); arc.addArc(skia.Rect(cx - r * 1.2, cy - r, cx + r * 1.2, cy + r), -90, 355 * k); c.drawPath(arc, ink(14, RED, boil=False))
    kk = pop(K(t, t0 + .5, .3))
    if kk > 0:
        c.save(); c.translate(1500 if mode == 'red' else 1260, 300 if mode == 'red' else 820); c.rotate(-8); c.scale(kk, kk)
        label(c, 'red t-shirt' if mode == 'red' else 'white bolt!', 0, 0, 90, RED, FONT_HAND, 'center', stroke=8, stroke_col='#FFFFFF', skew=0); c.restore()

def P69_zero(c, t, t0):
    lt = t - t0
    blit(c, cached('febg', lambda cc: fire_escape(cc, 0)), 0, 0, blur=12)
    draw_char(c, 960, 1450, 2.2, MIRA, face=-.2, eyes='half', mouth=talk(t) if talk(t) != 'flat' else 'smirk', arms=('hold', 'down'), brow=.3, shadow=False, rim='#7CF2E0')

def P70_wanna(c, t, t0):
    lt = t - t0
    blit(c, cached('febg', lambda cc: fire_escape(cc, 0)), 0, 0, blur=12)
    lean = ease(K(lt, 0, .6))
    draw_char(c, 960, lerp(1450, 1500, lean), lerp(2.2, 2.5, lean), MIRA, face=-.1, eyes='half', mouth=talk(t) if talk(t) != 'flat' else 'smirk', arms=('hold', 'down'), brow=.6, brow_tilt=.4, shadow=False, rim='#7CF2E0', tilt=-6 * lean)

def P71_lie(c, t, t0):
    lt = t - t0; b = at('but mira', t0)
    hero_close(c, t, cached('febg', lambda cc: fire_escape(cc, 0)), face=.3 if t < b else .45, eyes='dot' if t < b else 'half', mouth='flat' if t < b else 'smile',
               pupil=-.6 if t < b else .7, sweat=lt % 1 if t < b else -1, arms=('down', 'down'), blush=0 if t < b else .6, rim='#A9BCFF')

def P72_tell(c, t, t0):
    lt = t - t0
    fire_escape(c, t)
    g = int(twos(t) * 3) % 3
    draw_char(c, 760, 860, 1.0, HERO, face=.4, eyes='dot', mouth=['open', 'mid', 'smile'][g], arms=(['present', 'gesture', 'flail'][g], ['down', 'present', 'up'][g]), shadow=False, rim='#A9BCFF')
    draw_char(c, 1300, 860, 1.0, MIRA, face=-.4, eyes='dot', mouth='flat', arms=('hold', 'down'), shadow=False, rim='#7CF2E0', pupil=-.5)
    r = random.Random(5)
    for i, s_ in enumerate(('zero', 'warm hands', 'laughs', 'POW')):
        k = pop(K(lt, .1 + i * .45, .3))
        if k > 0: c.save(); c.translate(560 + i * 160, 260 - (i % 2) * 70); c.scale(k * .8, k * .8); rect(c, -len(s_) * 22 - 20, -50, len(s_) * 22 + 20, 30, '#FFFFFF', LW, 24); label(c, s_, 0, 6, 46, '#2A2E5A', KALAM, 'center', skew=0); c.restore()
    night(c, [('pool', 320, 620, 500, .6), ('pool', 1000, 600, 700, .45)], ambient='#4A4A90')

def P73_nolaugh(c, t, t0):
    blit(c, cached('febg', lambda cc: fire_escape(cc, 0)), 0, 0, blur=12)
    draw_char(c, 960, 1450, 2.2, MIRA, face=-.15, eyes='dot', mouth='flat', arms=('hold', 'down'), shadow=False, rim='#7CF2E0')

def P74_quiet(c, t, t0):
    lt = t - t0
    fire_escape(c, t)
    draw_char(c, 760, 860, 1.0, HERO, face=.4, eyes='dot', mouth='flat', arms=('down', 'down'), shadow=False, rim='#A9BCFF')
    draw_char(c, 1300, 860, 1.0, MIRA, face=-.1, eyes='half', mouth='flat', arms=('hold', 'hold'), shadow=False, rim='#7CF2E0', pupil=-.3)
    hscroll_lines(c, t, 200, 700, '#A9BCFF', 40, 400)
    night(c, [('pool', 320, 620, 500, .6), ('pool', 1000, 600, 700, .45)], ambient='#4A4A90')

def P75_says(c, t, t0):
    blit(c, cached('febg', lambda cc: fire_escape(cc, 0)), 0, 0, blur=12)
    draw_char(c, 960, 1450, 2.2, MIRA, face=.5, eyes='half', mouth='flat', arms=('hold', 'down'), pupil=1, shadow=False, rim='#7CF2E0')

def P76_never(c, t, t0):
    lt = t - t0
    grad_rect(c, -400, -300, W + 400, H + 300, '#0A0E2A', '#2A2458')
    p = skia.Path(); p.moveTo(1300, 1100); p.lineTo(1360, -200); p.lineTo(1600, -200); p.lineTo(1660, 1100); p.close(); c.drawPath(p, sp(linear(1300, 0, 1660, 0, [hx('#8A6A2A'), hx('#5A4418')]))); c.drawPath(p, ink(LW))
    circ(c, 1480, 120, 80, '#1E2236', LW); label(c, 'B', 1480, 160, 100, '#F2C14E', MARKER, 'center', skew=0)
    add_light(c, 1480, 120, 300, '#FF4A4A', 60 + 30 * math.sin(t * 2))
    draw_char(c, 700, 1450, 2.2, MIRA, face=.25, eyes='half', mouth=talk(t), arms=('hold', 'down'), brow=-.3, shadow=False, rim='#7CF2E0')

def P77_ask(c, t, t0):
    lt = t - t0
    hero_close(c, t, cached('febg', lambda cc: fire_escape(cc, 0)), face=.35, eyes='dot', mouth='mid' if int(t * 6) % 2 else 'flat', arms=('down', 'shrug'), brow=.8, rim='#A9BCFF')
    k = pop(K(lt, .4, .3))
    if k > 0: c.save(); c.translate(1300, 300); c.scale(k, k); label(c, '?', 0, 0, 200, '#F2C14E', MARKER, 'center', stroke=14, skew=0); c.restore()

def P78_think(c, t, t0): mira_talk(c, t, t0, mira_arm='point', mira_face=-.5)

def P79_billions(c, t, t0):
    lt = t - t0
    grad_rect(c, -400, -300, W + 400, H + 300, '#2A2410', '#120E06')
    for i in range(40):
        y = 900 - (i % 8) * 40; x = 300 + (i // 8) * 300
        if lt > i * .03: rect(c, x - 110, y - 20, x + 110, y + 20, '#9AD07A', LW * .6, 4); label(c, '$', x, y + 14, 34, '#3A6A2A', MARKER, 'center', skew=0)
    draw_char(c, 960, 1000, 1.0, EXEC, face=0, eyes='half', mouth='smirk', arms=('present', 'hip'), rim='#F2C14E', sparkle=(lt * 1.2) % 2)
    label(c, '$ BILLIONS', 960, 250, 120, '#F2C14E', MARKER, 'center', stroke=12, skew=0, alpha=K(lt, .3, .4))

def P80_rtt(c, t, t0):
    lt = t - t0
    grad_rect(c, -400, -300, W + 400, H + 300, '#1E1A34', '#0E0C1E')
    items = [at('rankings', t0) - t0, at('toys', t0) - t0, at('t', t0 + .3) - t0 if True else 1.6]
    for i in range(3):
        k = back(K(lt, items[i] - .05, .3), 1.8)
        if k <= 0: continue
        x = 400 + i * 560; c.save(); c.translate(x, 560); c.scale(k, k)
        if i == 0:
            for q in range(4): rect(c, -160, -160 + q * 80, 160, -100 + q * 80, '#1E2236', LW * .7, 8); label(c, f'#{q + 1}', -130, -115 + q * 80, 40, '#F2C14E', MARKER, 'left', skew=0)
            label(c, 'RANKINGS', 0, 240, 60, '#F2C14E', MARKER, 'center', stroke=8, skew=0)
        elif i == 1: draw_char(c, 0, 160, .5, AUREX, face=.2, eyes='dot', mouth='grin', arms=('hip', 'up'), shadow=False); label(c, 'TOYS', 0, 240, 60, '#F2C14E', MARKER, 'center', stroke=8, skew=0)
        else: rect(c, -160, -140, 160, 80, '#141826', LW, 14); c.drawRect(skia.Rect(-144, -124, 144, 64), fp('#4AB0E8')); label(c, 'TV DEALS', 0, 240, 60, '#F2C14E', MARKER, 'center', stroke=8, skew=0)
        c.restore()

def P81_system(c, t, t0):
    lt = t - t0
    stage(c, t, tint='#1E2A4A', spot=False)
    PV.scanner(c, 360, '921', t0 - 1, t0, t, land_col='#FFE88A')
    for i, kind in enumerate(('IRON', 'BRONZE', 'SILVER', 'GOLD', 'CROWN')):
        k = K(lt, .3 + i * .25, .3)
        if k > 0: badge(c, 1250 + (i - 2) * 0 + 0, 900 - i * 160, .35 * back(k), kind) if False else badge(c, 1300, 940 - i * 170, .32 * back(k, 1.5), kind)
    c.drawLine(560, 400, 1150, 600, ink(10, '#F2C14E', 200, boil=False))

def P82_equal(c, t, t0):
    lt = t - t0
    stage(c, t, tint='#2A1E3A')
    badge(c, 560, 520, .8, 'IRON'); label(c, '0', 560, 380, 140, '#FF4A4A', MARKER, 'center', stroke=12, skew=0)
    k = pop(K(lt, .6, .3)); c.save(); c.translate(960, 520); c.scale(k, k); label(c, '=', 0, 50, 220, '#FFFFFF', MARKER, 'center', stroke=12, skew=0); c.restore()
    k2 = back(K(lt, 1.0, .4), 1.6)
    if k2 > 0: badge(c, 1360, 520, .9 * k2, 'CROWN'); add_light(c, 1360, 520, 300, '#FFE88A', 100 * k2)

def P83_collapse(c, t, t0):
    lt = t - t0; dx, dy = shake(t, t0 + .4, 2.0, 12); c.translate(dx, dy)
    stage(c, t, tint='#3A1414', spot=False)
    for i, kind in enumerate(('IRON', 'BRONZE', 'SILVER', 'GOLD', 'CROWN')):
        fall = ease(K(lt, .4 + i * .15, .9)) ** 2
        c.save(); x = 960 + (i - 2) * 40 * fall * 6; y = 900 - (4 - i) * 0 - i * 150 + fall * (900 - (900 - i * 150) + 200)
        c.translate(x, y); c.rotate(fall * (i - 2) * 50); badge(c, 0, 0, .4, kind); c.restore()
    if lt > .5:
        for i in range(5): puff(c, 960 + (i - 2) * 200, 1000, 60 + lt * 20, i + 80, '#C8B8A8', '#9A8A7A', 200 * max(0, 1 - (lt - .5) / 2))

def P84_headdown(c, t, t0):
    lt = t - t0; b = at('and let them', t0)
    fire_escape(c, t)
    walk = K(t, b, 1.6)
    draw_char(c, lerp(1300, 1900, walk), 860, 1.0, MIRA, face=-.4 if walk == 0 else .6, eyes='half', mouth=talk(t), arms=('hold', 'down') if walk == 0 else walk_arms(t * 8), legs=walk_legs(t * 8) if walk > 0 else None, shadow=False, rim='#7CF2E0')
    draw_char(c, 760, 860, 1.0, HERO, face=.4 if walk < .5 else .6, eyes='half', mouth='flat', arms=('down', 'down'), shadow=False, rim='#A9BCFF', pupil=.8)
    night(c, [('pool', 320, 620, 500, .6), ('pool', 1000, 600, 700, .45)], ambient='#4A4A90')

def calendar(c, t, t0, marks, label_txt):
    grad_rect(c, -400, -300, W + 400, H + 300, '#E8DCC0', '#C8B898')
    rect(c, 360, 100, 1560, 1000, '#FFFFFF', LW * 1.3, 16); c.drawRect(skia.Rect(370, 110, 1550, 230), fp('#C8242C'))
    label(c, label_txt, 960, 200, 80, '#FFFFFF', MARKER, 'center', skew=0)
    for i in range(35):
        x = 400 + (i % 7) * 164; y = 260 + (i // 7) * 146
        rect(c, x, y, x + 150, y + 132, '#F8F4EC', LW * .5, 6); label(c, str(i + 1), x + 14, y + 36, 30, '#8A8478', KALAM, 'left', skew=0)
        if i in marks:
            k = pop(K(t, t0 + .2 + marks.index(i) * (1.6 / max(1, len(marks))), .25))
            if k > 0: c.save(); c.translate(x + 75, y + 80); c.scale(k, k); draw_ember(c, 0, 30, .28, t, .5); c.restore()

def P85_month(c, t, t0):
    lt = t - t0
    grad_rect(c, -400, -300, W + 400, H + 300, '#E8DCC0', '#C8B898')
    for i in range(8):
        k = K(lt, i * .3, .3); c.save(); c.translate(960, 200); c.rotate(-ease(k) * 170)
        if k < 1: rect(c, -400, 0, 400, 700, '#FFFFFF', LW, 10); label(c, ['WEEK 1', 'WEEK 2', 'WEEK 3', 'WEEK 4'][i % 4], 0, 380, 120, '#2A2E5A', MARKER, 'center', skew=0)
        c.restore()

def P86_normal(c, t, t0): calendar(c, t, t0, [9, 23], 'NORMAL MONTH')
def P87_three(c, t, t0): calendar(c, t, t0, [1, 3, 5, 8, 10, 12, 15, 17, 19, 22, 24, 26, 29, 31, 33], 'NOW')

def P88_quake(c, t, t0):
    lt = t - t0; dx, dy = shake(t, t0 + .5, .7, 24); c.translate(dx, dy)
    mall(c, t)
    draw_quake(c, 1300, 1000, 1.0, t, stomp=abs(math.sin(lt * 2.2)) * .4)
    for i in range(4):
        x = (600 - lt * 520 - i * 160) % 2200 - 200
        walker(c, t, x, 1020 + (i % 2) * 40, .7, TEENS[i], lt * 16 + i, face=-.8, run=True, eyes='shock', mouth='open')
    chip(c, t, t0 + .4, 'FIRST IN 6 YEARS', 'QUAKE', '#FF6A3A', y=180)

def P89_together(c, t, t0):
    lt = t - t0; pan = lt * 400
    mall(c, t, pan)
    hscroll_lines(c, t, 300, 900, '#FFFFFF', 60, 2400)
    walker(c, t, 760, 1010, 1.0, HERO, lt * 18, face=.7, run=True, eyes='half', mouth='flat', brow=-.6)
    draw_char(c, 1150, 760 + math.sin(t * 4) * 20, .9, MIRA, face=.6, eyes='half', mouth='grin', arms=('up', 'hip'), legs=((-20, -20, 30), (20, 10, 30)), shadow=False)
    drone(c, 1150, 800 + math.sin(t * 4) * 20, 1.3, t)

def P90_drones(c, t, t0):
    lt = t - t0
    grad_rect(c, -400, -300, W + 400, H + 300, '#5FA8E8', '#CFE8FF')
    mall(c, t, 300) if False else None
    city = cached('daycity2', lambda cc: city_strip(cc, 1080, 81, 250, 700, 100, 200, '#A9C2E2', '#8EA8CE', '#E6F0FF', .3)); blit(c, city)
    x = lerp(-200, 1100, ease_out(K(lt, 0, 1.4)))
    draw_char(c, x, 640, 1.0, MIRA, face=.6, eyes='half', mouth='grin', arms=('up', 'point'), legs=((-20, -20, 30), (20, 10, 30)), shadow=False, rim='#FFFFFF')
    drone(c, x, 680, 1.5, t)
    for i in range(3): drone(c, x - 300 - i * 200, 400 + i * 120, .8, t)

def P91_evac(c, t, t0):
    lt = t - t0
    mall(c, t, 800)
    for i in range(4):
        x = 1500 - (lt * 300 + i * 200) % 1600; walker(c, t, x, 1020, .7, TEENS[i], lt * 10 + i, face=-.7, eyes='dot', mouth='o')
    wv = int(twos(t) * 6) % 2
    draw_char(c, 1250, 1000, 1.0, HERO, face=-.3, eyes='closed' if lt > 1.2 else 'dot', mouth='grin', arms=('point', 'wave' if wv else 'wave2'), sparkle=K(lt, 1.2, .5) * 1.5, blush=.4)

def P92_punch(c, t, t0):
    lt = t - t0; hit = at('one punch', t0) + .25
    if t > hit: dx, dy = shake(t, hit, .8, 36); c.translate(dx, dy)
    mall(c, t, 1200)
    if t < hit:
        draw_quake(c, 1250, 1000, 1.0, t, stomp=.2)
        k = K(lt, 0, .6); draw_char(c, lerp(300, 700, ease(k)), 1000, 1.0, HERO, face=.6, eyes='half', mouth='flat', brow=-.7, arms=('fist', ('fist', 'push', K(t, hit - .25, .2))), legs=walk_legs(lt * 14) if k < 1 else None)
        if t > hit - .2: speed_lines(c, t, 900, 600, '#FFFFFF', 140, 40, 200)
    else:
        dt = t - hit
        c.save(); c.translate(1250 + dt * 1400, 1000 - dt * 900); c.rotate(dt * 200); draw_quake(c, 0, 0, 1.0, t, stomp=0); c.restore()
        draw_char(c, 760, 1000, 1.0, HERO, face=.6, eyes='half', mouth='smirk', arms=('fist', 'push'), rim='#FFB46A', squash=.1 * math.sin(K(dt, 0, .3) * math.pi))
        for i in range(6): puff(c, 960 + (i - 2.5) * 160 * (1 + dt), 980, 60 + dt * 40, i + 90, '#D8D0C4', '#B0A898', 255 * max(0, 1 - dt / 1.5))
        if dt < .5: ring = dt / .5; c.drawOval(skia.Rect(1000 - 900 * ring, 700 - 300 * ring, 1000 + 900 * ring, 700 + 300 * ring), ink(16, '#FFFFFF', 255 * (1 - ring), boil=False))
    if t > DUR2 - .8: c.drawRect(skia.Rect(-400, -300, W + 400, H + 300), fp((0, 0, 0), 255 * K(t, DUR2 - .8, .8)))

# shot list: (start phrase, fn, cam) - cam None = default slow push
E = lambda n: (lambda c, t, t0: P23_exp(c, t, t0, n))
SHOTS = [
    (None, P1_dust, None), ('not knocked', P2_empty, None), ('gone', P3_gone, None), ('theres a hole', P4_roof, P4_cam),
    ('you look at your fist', P5_fist, None), ('its not even', P6_clean, None), ('the little girl', P7_girl, None), ('everyone is staring', P8_everyone, None),
    ('and then through', P9_silver, None), ('did i miss', P10_miss, None), ('heres the funny', P11_funny, None), ('the security cameras', P12_cctv, None),
    ('the station was full', P13_dusty, None), ('and when reporters', P14_reporters, None), ('by the evening', P15_news, None), ('silver hero arrives', P16_headline, None),
    ('you sit on your bed', P17_bed, None), ('you punched a', P18_uppercut, 'card'), ('with a spark score', P19_zero, None), ('so either', P20_scanner, None),
    ('you need to know', P21_need, None), ('you spend the next', P22_weeks, 'card'), ('experiment one', E('one'), 'card'), ('you try to punch', P24_tree, None),
    ('nothing', P25_nothing, None), ('your knuckles', P26_ouch, None), ('experiment 2', E('two'), 'card'), ('you try to lift', P28_lift, None),
    ('the car does not', P29_nomove, None), ('a man walks', P30_bro, None), ('experiment 3', E('three'), 'card'), ('you go home', P32_angry, None),
    ('your little cousin', P33_cousin, None), ('you challenge', P34_challenge, None), ('and the moment', P35_hands, None), ('your cousin screams', P36_cscream, None),
    ('your aunt', P37_aunt, None), ('the table is', P38_table, None), ('and thats when', P39_understand, None), ('your power doesnt', P40_source, None),
    ('every time someone believes', P41_laughs, None), ('one persons', P42_boxer, None), ('a whole crowds', P43_crowd, None), ('that was a crowd', P44_wasacrowd, 'card'),
    ('think about what', P45_think, None), ('for four years', P46_city, None), ('millions of', P47_millions, None), ('every meme', P48_memes, None),
    ('the scanner reads', P49_measure, None), ('its borrowed', P50_borrowed, None), ('which means', P51_scale, None), ('you should feel', P52_happy, None),
    ('instead a cold', P53_cold, None), ('what happens if', P54_stop, None), ('you dont tell', P55_secret, None), ('but somebody', P56_someone, None),
    ('her name is', P57_mira, None), ('silver rank', P58_silver, None), ('spark score 540', P59_540, None), ('she builds', P60_gadgets, None),
    ('and unlike', P61_looked, None), ('monsters dont go up', P62_up, None), ('they go sideways', P63_dirs, None), ('like something hit', P64_below, None),
    ('something with about', P65_400, None), ('she turns the tablet', P66_turn, None), ('its a blurry', P67_blurry, lambda t, t0: P67_cam(t, t0, 'blur')),
    ('a red t-shirt', lambda c, t, t0: P68_mark(c, t, t0, 'red'), None), ('a white bolt', lambda c, t, t0: P68_mark(c, t, t0, 'bolt'), None),
    ('so she says', P69_zero, None), ('wanna tell', P70_wanna, None), ('you could lie', P71_lie, None), ('so you tell', P72_tell, None),
    ('she doesnt laugh', P73_nolaugh, None), ('she just goes', P74_quiet, None), ('then she says', P75_says, None), ('you know the bureau', P76_never, None),
    ('you ask her', P77_ask, None), ('think about it', P78_think, None), ('the bureau makes', P79_billions, None), ('rankings', P80_rtt, None),
    ('their whole system', P81_system, None), ('and youre a zero', P82_equal, None), ('if people found', P83_collapse, None), ('so keep your head', P84_headdown, None),
    ('over the next month', P85_month, 'card'), ('normally the city', P86_normal, None), ('now its three', P87_three, None), ('then a quake', P88_quake, None),
    ('you and mira', P89_together, None), ('she flies in', P90_drones, None), ('you help with', P91_evac, None), ('and when nobody', P92_punch, None),
]
LEAD = .12
TIMES = []
_t = -1.0
for ph, fn, cam in SHOTS:
    t0 = 0.0 if ph is None else at(ph, _t + .05) - LEAD
    TIMES.append(t0); _t = t0 + LEAD
TIMES.append(DUR2)
IMPACTS2 = [at('you punched a') - LEAD + .9, at('one punch') + .25, at('that was a crowd') - LEAD + .3]
