# EP01 Part 1 shots 0 - 150.9 s
from world import *
import preview as PV
PV.END = 9999   # no fade inside the hook shot

def lt_(t, t0): return t - t0

def draw_car(c, x, y, s, col, squash=0.0):
    c.save(); c.translate(x, y); c.scale(s, s * (1 - squash * .6))
    b = skia.Path(); b.addRRect(skia.RRect.MakeRectXY(skia.Rect(-200, -120, 200, -30), 30, 30)); grad_shape(c, b, col, '#00000000' if False else col, -120, -30)
    rect(c, -120, -190, 110, -110, col, LW, 30); rect(c, -95, -175, -10, -118, '#BFE0F4', LW * .7, 10); rect(c, 5, -175, 85, -118, '#BFE0F4', LW * .7, 10)
    for wx in (-120, 120): circ(c, wx, -30, 38, '#26262E'); circ(c, wx, -30, 16, '#B8BCC8', LW * .6)
    c.restore()

def crowd_heads(c, t, y, s, seed, n=9, bounce=1.0, phones=False, rim='#FFE9A8'):
    r = random.Random(seed)
    for i in range(n):
        x = 80 + i * (W - 160) / max(1, n - 1) + r.uniform(-30, 30); sp_ = TEENS[r.randrange(4)]
        hy = y - abs(math.sin(twos(t) * 5 + i * 1.7)) * 20 * s * bounce
        c.save(); c.translate(x, hy); c.scale(s, s)
        rect(c, -80, -40, 80, 200, sp_['suit_d'], LW, 60)
        hc = sp_.get('hair_col', '#1D1A20') if sp_['hair'] != 'cap' else sp_['cap_col']
        circ(c, 0, -110, 82, hc); c.drawArc(skia.Rect(-74, -184, 74, -36), 200, 140, False, ink(7, rim, 150, boil=False))
        c.restore()

def hero_close(c, t, bgkey, **kw):
    blit(c, bgkey, 0, 0, blur=14)
    kw.setdefault('shadow', False)
    draw_char(c, 760, 1400, 2.15, HERO, **kw)

def bg_img(key, fn, scale=1.5, ox=0, oy=0):
    return cached(key, lambda cc: (cc.save(), cc.translate(W / 2, H / 2), cc.scale(scale, scale), cc.translate(-W / 2 + ox, -H / 2 + oy), fn(cc), cc.restore()))

BG_STREET = lambda: bg_img('bgst', lambda cc: street_day(cc, 0, 300, people=False))
BG_NIGHT = lambda: bg_img('bgnt', lambda cc: (grad_rect(cc, -400, -300, W + 400, H + 300, '#0B1030', '#2A2058'), city_strip(cc, 900, 77, 200, 520, 80, 160, '#1E2450', '#161B40', '#FFC864', .35)))
BG_HALL = lambda: bg_img('bghl', lambda cc: hall(cc, 0), ox=-200, oy=60)
BG_STATION = lambda: bg_img('bgsn', lambda cc: station(cc, 0, 0, False, 200))

# --------------------------------------------------------------- shots
def A_weakest(c, t):
    lt = t - 14.05; pan = lt * 230
    street_day(c, t, pan)
    for i, (wx, sp_) in enumerate(((900, TEENS[0]), (1500, TEENS[1]), (2100, TEENS[2]), (2500, TEENS[3]))):
        x = wx - pan * .85; ph = t * 3 + i
        draw_char(c, x, 900, .8, sp_, face=-.4 if x > 960 else .4, eyes='closed' if int(t * 4 + i) % 3 == 0 else 'dot', mouth='open' if math.sin(t * 12 + i) > 0 else 'grin',
                  arms=('laugh', ('point' if i % 2 == 0 else 'laugh')), bob=abs(math.sin(t * 10 + i)) * 10, blush=.3)
    ph = lt * 9
    walker(c, t, 960, 1000, 1.0, HERO, ph, face=.55, eyes='half', mouth='frown', brow_tilt=.8, sweat=(lt * .8) % 1, tilt=8)

def B_card(c, t):
    stage(c, t, tint='#1E2A5A', spot=True)
    k = back(K(t, 16.95, .45), 1.4)
    license_card(c, 960, lerp(1500, 540, k), 1.25, t, k)
    if t > 17.5:
        st = K(t, 17.5, .18); sc = lerp(2.4, 1, ease_out(st))
        c.save(); c.translate(1300, 760); c.rotate(-12); c.scale(sc, sc)
        p = skia.Path(); p.addRRect(skia.RRect.MakeRectXY(skia.Rect(-210, -70, 210, 70), 16, 16)); c.drawPath(p, ink(12, RED, 255 * min(1, st * 2), boil=False))
        label(c, 'LAST', 0, 44, 110, RED, MARKER, 'center', skew=0, alpha=min(1, st * 2)); c.restore()

def C_news(c, t):
    grad_rect(c, -400, -300, W + 400, H + 300, '#1E3A7A', '#0E1E4A')
    for i in range(12): c.drawRect(skia.Rect(i * 180 - 100, 0, i * 180 - 20, 1100), fp('#2E4E9A', 80))
    rect(c, 980, 120, 1780, 600, '#141826', LW * 1.3, 24)
    c.save(); c.clipRect(skia.Rect(990, 130, 1770, 590)); c.drawRect(skia.Rect(990, 130, 1770, 590), fp('#E8D06A'))
    draw_char(c, 1380, 980, 1.6, HERO, face=0, eyes='dot', mouth='flat', shadow=False)
    label(c, '0', 1660, 300, 160, RED, MARKER, 'center', stroke=12, skew=0); c.restore()
    draw_char(c, 600, 1000, 1.05, ANCHOR, face=.25, eyes='closed' if blink(t, 2.1) else 'dot', mouth=talk(t), arms=('down', 'present'))
    rect(c, 200, 760, 1100, 1100, '#2A3050', LW, 16); c.drawRect(skia.Rect(210, 770, 1090, 800), fp('#C8242C'))
    c.drawRect(skia.Rect(-400, 900, W + 400, 1000), fp('#C8242C')); c.drawLine(-400, 900, W + 400, 900, ink(LW)); c.drawLine(-400, 1000, W + 400, 1000, ink(LW))
    rect(c, 40, 880, 380, 1020, '#FFFFFF', LW, 10); label(c, 'BREAKING', 210, 975, 64, '#C8242C', MARKER, 'center', skew=0)
    x = 1900 - ((t - 18.56) * 600)
    c.save(); c.clipRect(skia.Rect(400, 900, W, 1000)); label(c, 'THE ZERO KID  -  WEAKEST HERO ALIVE  -  SPARK SCORE: 0  -', x, 975, 64, '#FFFFFF', MARKER, 'left', skew=0); c.restore()

def D_kids(c, t):
    lt = t - 19.87
    street_day(c, t, 600 + lt * 40)
    walker(c, t, 1500 + lt * 60, 930, .95, HERO, lt * 8, face=.5, eyes='half', mouth='flat', brow_tilt=.6)
    for i, x in enumerate((420, 640, 860)):
        draw_char(c, x, 1010, .62, KIDS[i], face=.6, eyes='closed' if i != 1 else 'dot', mouth='open', arms=('laugh', 'point'),
                  bob=abs(math.sin(twos(t) * 11 + i)) * 16, squash=.05 * math.sin(t * 22 + i), blush=.6)

def E_secret(c, t):
    lt = t - 22.10
    hero_close(c, t, BG_NIGHT(), face=.35, eyes='half', mouth='flat', arms=('down', 'heart'), pupil=.7, rim='#FFB46A')
    g = .5 + .5 * math.sin(lt * 5)
    hx_, hy_ = 760 + 20 * 2.15, 1400 - 290 * 2.15
    add_light(c, hx_, hy_, 160 + 40 * g, '#FF8A3C', 120 + 60 * g)
    night(c, [('pool', hx_, hy_, 380, .7), ('pool', 760, 600, 600, .3)], ambient='#3A3F80')

def F_sunrise(c, t):
    lt = t - 25.44; k = ease(K(lt, 0, 1.4))
    grad_rect(c, -400, -300, W + 400, 900, '#2E2A6A', '#FF9A6A')
    c.drawCircle(960, lerp(900, 640, k), 150, fp('#FFE6A0')); add_light(c, 960, lerp(900, 640, k), 600, '#FFC870', 140)
    sk = cached('sunsky', lambda cc: city_strip(cc, 900, 91, 200, 560, 80, 160, '#2A2050', '#1E1840', '#FFB46A', .2))
    blit(c, sk)
    for i in range(6):
        x = (300 + i * 140 + lt * 260) % 2200 - 100; y = 300 + math.sin(i) * 60
        w_ = 18 + 10 * math.sin(t * 16 + i); c.drawLine(x - w_, y - 10, x, y, ink(5)); c.drawLine(x, y, x + w_, y - 10, ink(5))

def G_aurex(c, t):
    lt = t - 26.77
    grad_rect(c, -400, -300, W + 400, H + 300, '#1A1450', '#E06A5A')
    for i in range(4): puff(c, (i * 600 + t * 60) % 2600 - 300, 200 + i * 60, 70, i + 80, '#5A3A7A', '#3E2860', 255, outline=False)
    sk = cached('aurexsky', lambda cc: city_strip(cc, 1200, 13, 100, 300, 80, 160, '#2A1E48', '#1E163A', '#FFB46A', .3))
    blit(c, sk, 0, 0, blur=3)
    rect(c, 560, 860, 1360, 1300, '#3A2E5A', LW, 10); rect(c, 520, 840, 1400, 880, '#4E3E78', LW, 6)
    turn = ease(K(lt, 1.8, .5))
    spec = dict(AUREX);
    draw_char(c, 960, 860, 1.25, spec, face=lerp(-.6, .25, turn), eyes='half', mouth='smirk' if turn > .5 else 'flat', arms=('hip', 'hip'), rim='#FFB46A',
              sparkle=K(lt, 2.6, .5) * 1.7, brow=-.3)
    hscroll_lines(c, t, 0, 900, '#FFFFFF', 70, 1600)

def H_subscribe(c, t):
    lt = t - 30.84
    stage(c, t, tint='#5A1E2A', spot=True)
    press = ease_out(K(lt, 1.55, .12)) * (1 - ease(K(lt, 1.8, .3)))
    c.save(); c.translate(1150, 560); c.scale(1, 1 - press * .12)
    rect(c, -360, -110, 360, 110, '#E02A2A', LW * 1.4, 40); label(c, 'SUBSCRIBE', 0, 40, 120, '#FFFFFF', MARKER, 'center', skew=0)
    c.restore()
    if lt > 1.6:
        k = back(K(lt, 1.6, .4), 1.8); ang = math.sin(lt * 18) * 20 * max(0, 1 - (lt - 1.6) / 1.2)
        c.save(); c.translate(1600, 380); c.rotate(ang); c.scale(k, k)
        bp = skia.Path(); bp.moveTo(-70, 40); bp.cubicTo(-70, -60, -50, -100, 0, -100); bp.cubicTo(50, -100, 70, -60, 70, 40); bp.lineTo(90, 60); bp.lineTo(-90, 60); bp.close()
        shape(c, bp, '#F2C14E'); circ(c, 0, 76, 20, '#F2C14E'); c.restore()
    walk_in = ease_out(K(lt, 0, 1.0)); x = lerp(-150, 640, walk_in)
    punching = lt > 1.3
    draw_char(c, x, 900, 1.0, HERO, face=.6, eyes='dot' if not punching else 'half', mouth='grin', blush=.4,
              legs=walk_legs(lt * 10) if walk_in < .98 else None, arms=walk_arms(lt * 10) if walk_in < .98 else ('fist', ('fist', 'push', K(lt, 1.35, .18))),
              squash=.08 * math.sin(K(lt, 1.5, .2) * math.pi), sparkle=K(lt, 2.2, .5) * 1.6)
    if 1.5 < lt < 1.8: speed_lines(c, t, 1000, 560, '#FFFFFF', 140, 30, 200)

def I_portal(c, t):
    lt = t - 34.73
    grad_rect(c, -400, -300, W + 400, H + 300, '#0A0820', '#1E1450')
    op = ease_out(K(lt, 0, .7))
    for i in range(12):
        r = (40 + i * 34) * op; a0 = t * (90 + i * 15)
        col_ = ['#6A4AE8', '#4AB0E8', '#E84AB0', '#F2C14E'][i % 4]
        p = skia.Path(); p.addArc(skia.Rect(1160 - r, 540 - r * .9, 1160 + r, 540 + r * .9), a0, 250); c.drawPath(p, ink(10, col_, 220, boil=False))
    add_light(c, 1160, 540, 500 * op, '#9A7AFF', 150)
    jump = K(lt, 2.4, .6)
    if jump < 1:
        x = lerp(640, 1160, ease(jump)); y = 900 - math.sin(jump * math.pi) * 300; s = lerp(1.0, .1, jump ** 2)
        c.save(); c.translate(x, y - 300 * s); c.rotate(jump * 360); c.translate(-x, -(y - 300 * s))
        wv = int(twos(t) * 6) % 2
        draw_char(c, x, y, s, HERO, face=.3, eyes='closed' if jump > 0 else 'dot', mouth='grin', arms=('wave' if wv else 'wave2', 'down') if jump == 0 else ('up', 'up'), blush=.5, shadow=jump == 0)
        c.restore()
    r = random.Random(4)
    for i in range(40):
        a = r.uniform(0, 6.28); d = (r.uniform(0, 600) - t * 300) % 600
        c.drawCircle(1160 + math.cos(a) * d, 540 + math.sin(a) * d * .9, 3, fp('#FFFFFF', 200))

def J_title(c, t):
    lt = t - 38.80
    far = cached('far', lambda cc: city_strip(cc, 840, 11, 200, 460, 70, 150, '#3A3270', '#2E285E', '#F7C873', .3, outline=False))
    grad_rect(c, -400, -300, W + 400, H + 300, '#0E1238', '#8A3E5E'); blit(c, far, 0, 0, blur=3)
    mid = cached('mid', lambda cc: city_strip(cc, 900, 15, 150, 330, 90, 170, '#2E336A', '#232858', '#FFC864', .35)); blit(c, mid)
    vignette(c, .6)
    k1 = pop(K(lt, .05, .35)); k2 = pop(K(lt, .3, .35))
    c.save(); c.translate(960, 500); c.rotate(-4); c.scale(k1, k1); label(c, 'IN THIS', 0, 0, 170, '#FFF6DC', MARKER, 'center', stroke=22, skew=0); c.restore()
    c.save(); c.translate(980, 700); c.rotate(-4); c.scale(k2, k2); label(c, 'WORLD', 0, 0, 260, '#E02A2A', MARKER, 'center', stroke=26, stroke_col='#FFF6DC', skew=0); c.restore()

def K_cinema(c, t):
    lt = t - 39.97
    grad_rect(c, -400, -300, W + 400, H + 300, '#120E1E', '#06050C')
    rect(c, 260, 80, 1660, 700, '#E8E4F0', LW * 1.4, 10)
    c.save(); c.clipRect(skia.Rect(270, 90, 1650, 690)); grad_rect(c, 270, 90, 1650, 690, '#3A2A6A', '#C86A5A')
    draw_gorrak(c, 960 + math.sin(t * 2) * 30, 1000, .55, t, roar=.5 + .5 * math.sin(t * 6))
    c.restore()
    label(c, 'MONSTER MOVIE NIGHT', 960, 60, 40, '#F2C14E', KALAM, 'center', skew=0)
    c.drawPath(cone_path(960, 1080, 600, 40, -1000), sp(linear(0, 1080, 0, 80, [hx('#BFD0FF', 10), hx('#BFD0FF', 60)]), blend=skia.BlendMode.kPlus))
    crowd_heads(c, t, 900, .95, 3, 8, .2, rim='#BFD0FF'); crowd_heads(c, t, 1020, 1.2, 4, 7, .3, rim='#BFD0FF')
    r = random.Random(int(t * 6))
    for i in range(10):
        x = r.uniform(200, 1700); y = 950 - ((t * 200 + i * 40) % 160)
        c.drawCircle(x, y, 9, fp('#FFF6DC')); c.drawCircle(x, y, 9, ink(3, boil=False))

def L_ground(c, t):
    lt = t - 42.85; burst = 43.35
    street_day(c, t, 900)
    for i, x in enumerate((420, 1520)):
        jump = abs(math.sin(K(t, burst, .5) * math.pi)) * 80
        draw_char(c, x, 920 - jump, .8, TEENS[i], face=.5 if x < 960 else -.5, eyes='shock' if t > burst else 'dot', mouth='open' if t > burst else 'flat',
                  arms=('flail', 'up') if t > burst else ('down', 'down'), sweat=(t - burst) * 2 if t > burst else -1)
    k = K(lt, 0, .5)
    r = random.Random(6)
    for i in range(9):
        a = r.uniform(3.4, 6.0); L = r.uniform(150, 420) * k
        c.drawLine(960, 960, 960 + math.cos(a) * L, 960 + math.sin(a) * L * .35 + 40, ink(7))
    if t > burst:
        e = back(K(t, burst, .25), 1.5)
        for j, dx in enumerate((-90, 0, 90)):
            c.save(); c.translate(960 + dx, 980); c.rotate(dx * .15 + math.sin(t * 8 + j) * 4); c.scale(e, e)
            cl = skia.Path(); cl.moveTo(-30, 0); cl.cubicTo(-40, -200, -10, -330, 30, -380); cl.cubicTo(20, -280, 40, -150, 40, 0); cl.close(); grad_shape(c, cl, '#5A3A8A', '#2A1A4A', -380, 0); poly(c, [(22, -340), (30, -440), (42, -330)], '#F3E7C8', LW * .7)
            c.restore()
        dt = t - burst; rr = random.Random(2)
        for i in range(14):
            vx = rr.uniform(-500, 500); vy = rr.uniform(-800, -300); x = 960 + vx * dt; y = 960 + vy * dt + 800 * dt * dt
            c.save(); c.translate(x, y); c.rotate(dt * 400 + i * 30); rect(c, -18, -12, 18, 12, '#5A5A66', LW * .7); c.restore()
        for i in range(5): puff(c, 960 + (i - 2) * 140 * (1 + dt), 980 - dt * 60, 50 + dt * 50, i + 9, '#E6E0D4', '#B8B0A0', 255 * max(0, 1 - dt / 1.2))

def M_breach(c, t):
    lt = t - 44.54
    grad_rect(c, -400, -300, W + 400, 800, '#0A0E2A', '#1E2458')
    grad_rect(c, -400, 760, W + 400, H + 300, '#262438', '#14121E', LW)
    cr = skia.Path(); pts = [(500, 880), (700, 850), (820, 900), (960, 840), (1100, 905), (1260, 860), (1420, 890)]
    cr.moveTo(*pts[0]); [cr.lineTo(*p) for p in pts[1:]]; pts2 = [(1420, 900), (1250, 930), (1100, 960), (960, 920), (820, 970), (700, 920), (500, 895)]
    [cr.lineTo(*p) for p in pts2]; cr.close()
    c.drawPath(cr, fp('#C88AFF')); c.drawPath(cr, ink(LW))
    g = .6 + .4 * math.sin(t * 4)
    c.drawPath(cone_path(960, 900, 700, 1100, -900), sp(linear(0, 900, 0, 0, [hx('#B87AFF', 120 * g), hx('#B87AFF', 0)]), blend=skia.BlendMode.kPlus))
    r = random.Random(3)
    for i in range(40):
        u = (r.random() + t * .3) % 1; x = r.uniform(550, 1400) + math.sin(t + i) * 20
        c.drawCircle(x, 900 - u * 700, r.uniform(2, 5), fp('#E8C8FF', 220 * (1 - u)))
    rect(c, 140, 820, 520, 900, '#F2C14E', LW, 8)
    for i in range(5): poly(c, [(150 + i * 76, 820), (190 + i * 76, 820), (160 + i * 76, 900), (120 + i * 76, 900)], '#1E1E28', 0)
    for i, x in enumerate((240, 420)):
        peek = ease(K(lt, .3 + i * .3, .5))
        draw_char(c, x, 1080, .85, SCI, face=.6, eyes='wide', mouth='o', arms=('hold', 'chin'), pupil=1, tilt=8 * peek, lean=.0)
    rect(c, 140, 900, 520, 1100, '#3A3A4A', LW, 8)
    add_light(c, 960, 880, 700, '#B87AFF', 120 * g)
    night(c, [('pool', 960, 880, 800, .7)], ambient='#5A5AA0')

def N_scientist(c, t):
    grad_rect(c, -400, -300, W + 400, H + 300, '#E8DCC0', '#C8B898')
    rect(c, 700, 140, 1760, 700, '#2E4A3A', LW * 1.4, 10); rect(c, 680, 690, 1780, 720, '#8C5E3F', LW, 4)
    k = K(t, 46.95, 1.4); s_ = 'BREACH CREATURES'; n = int(len(s_) * k)
    label(c, s_[:n], 1230, 300, 84, '#F4F4EC', FONT_HAND, 'center', skew=0)
    c.drawCircle(1000, 520, 70, ink(5, '#F4F4EC', boil=False)); c.drawLine(1080, 520, 1300, 520, ink(5, '#F4F4EC', boil=False))
    for i in range(3): c.drawLine(1330 + i * 40, 470, 1350 + i * 40, 570, ink(5, '#F4F4EC', boil=False))
    label(c, '???', 1560, 560, 90, '#F4F4EC', FONT_HAND, 'center', skew=0)
    draw_char(c, 460, 1000, 1.1, SCI, face=.45, eyes='closed' if blink(t, 2.4) else 'dot', mouth=talk(t), arms=('down', ('down', 'point', K(t, 47.2, .3))),
              brow=.4, bob=abs(math.sin(twos(t) * 3)) * 6)

def O_monsters(c, t):
    lt = t - 49.27; dx, dy = shake(t, 49.27, 2.3, 6); c.translate(dx, dy)
    street_day(c, t, 1400)
    for i in range(7):
        d = 1 if i % 2 else -1; x = (300 + i * 260 + d * lt * 520) % 2400 - 240; ph = lt * 16 + i
        walker(c, t, x, 900 + (i % 3) * 60, .7 + (i % 3) * .1, TEENS[i % 4], ph, face=.8 * d, run=True, eyes='shock', mouth='open', sweat=(lt * 2 + i * .3) % 1)

def P_dog(c, t):
    lt = t - 51.59
    street_day(c, t, 2000)
    draw_dog(c, 700, 1000, 1.5, t, bark=1 if int(t * 6) % 2 else 0)
    draw_ember(c, 1250, 1000, 1.1, t, open_=.5 + .5 * math.sin(t * 12))
    c.save(); c.translate(-1, 0); c.restore()

def Q_building(c, t):
    lt = t - 53.48
    grad_rect(c, -400, -1200, W + 400, H + 300, '#6AA8E0', '#D8EAFA')
    for i in range(3): puff(c, (i * 700 + t * 20) % 2400 - 300, -700 + i * 200, 80, i + 90, '#FFFFFF', '#D6E6F8', 255)
    p = skia.Path(); p.addRect(skia.Rect(250, -500, 700, 1100)); c.drawPath(p, sp(linear(250, 0, 700, 0, [hx('#B8C8E0'), hx('#8EA0BE')]))); c.drawPath(p, ink(LW))
    for i in range(5):
        for j in range(20): c.drawRect(skia.Rect(280 + i * 84, -470 + j * 78, 330 + i * 84, -430 + j * 78), fp('#E6F0FF'))
    stomp = abs(math.sin(lt * 2.5)) * .3
    draw_quake(c, 1250, 1060, 1.65, t, stomp=stomp)
    grad_rect(c, -400, 1040, W + 400, H + 400, '#6A6A74', '#4A4A54', LW)

def Q_cam(t): k = ease(K(t, 53.48, 1.9)); return 1.0, 960, lerp(700, 0, k)

def R_meter(c, t):
    lt = t - 55.52
    stage(c, t, tint='#1E2A5A')
    cols = ['#FF8A3A', '#F2D36B', '#FF6A3A', '#9A6AE8', '#E02A3A']
    for i in range(5):
        on = K(lt, .3 + i * .5, .2)
        a0 = 180 + i * 36
        p = skia.Path(); p.addArc(skia.Rect(560, 240, 1360, 1040), a0 + 2, 32); c.drawPath(p, ink(110, '#1E1A2E', boil=False)); c.drawPath(p, ink(92, cols[i], 80 + 175 * on, boil=False))
        if on > 0: a_ = math.radians(a0 + 18); add_light(c, 960 + math.cos(a_) * 400, 640 + math.sin(a_) * 400, 140, cols[i], 120 * on)
    na = 180 + 18 + min(4, lt / .5) * 36 + math.sin(t * 20) * 2
    c.save(); c.translate(960, 640); c.rotate(na); poly(c, [(0, -14), (360, 0), (0, 14)], '#FFF6DC'); c.restore(); circ(c, 960, 640, 40, '#2A2640')
    label(c, 'THREAT LEVEL', 960, 760, 70, '#FFF6DC', MARKER, 'center', stroke=10, skew=0)

def S_ember(c, t):
    lt = t - 59.29
    stage(c, t, tint='#5A2A1A')
    caught = t > 62.0
    ex = 960 + (math.sin(lt * 5) * 200 if not caught else 0); hop = abs(math.sin(lt * 9)) * 60 if not caught else 0
    draw_ember(c, ex, 860 - hop, 1.0, t, open_=.6)
    if caught:
        nk = ease_out(K(t, 62.0, .2)); c.save(); c.translate(ex, 760)
        for i in range(-4, 5): c.drawLine(i * 40, -160 * nk, i * 50, 120, ink(4, '#E8E4D8', boil=False))
        for j in range(5): c.drawLine(-200, -140 + j * 60, 200, -140 + j * 60, ink(4, '#E8E4D8', boil=False))
        c.restore()
    for i, side in enumerate((-1, 1)):
        jk = K(t, 61.7, .3); x = 960 + side * lerp(560, 260, ease(jk)); y = 860 - math.sin(jk * math.pi) * 160
        draw_char(c, x, y, .8, POLICE, face=-.6 * side, eyes='half' if not caught else 'closed', mouth='grin' if caught else 'flat',
                  arms=('up', 'up') if 0 < jk < 1 else ('hip', 'fist'), sparkle=K(t, 62.5, .5) * 1.5 if caught else 0)
    chip(c, t, 59.4, 'THREAT LEVEL 1', 'EMBER', '#FF8A3A', y=200)

def T_storm(c, t):
    lt = t - 63.49
    grad_rect(c, -400, -300, W + 400, 800, '#141A40', '#3A3070')
    mid = cached('mid', lambda cc: city_strip(cc, 900, 15, 150, 330, 90, 170, '#2E336A', '#232858', '#FFC864', .35)); blit(c, mid, 0, -100)
    grad_rect(c, -400, 800, W + 400, H + 300, '#3A3450', '#211E30', LW)
    sq = ease_out(K(t, 65.0, .2))
    draw_car(c, 900, 960, 1.0, '#D9473A', squash=sq)
    draw_storm(c, lerp(2200, 1400, ease(K(lt, 0, 2.0))), 900, .7, t, rear=.15, open_=.3)
    land = K(t, 66.3, .25)
    if t > 66.1:
        y = lerp(-200, 960, ease_out(land))
        draw_char(c, 450, y, .9, SILVER, face=.5, eyes='half', mouth='smirk', arms=('fist', 'hip'), squash=.15 * math.sin(K(t, 66.55, .25) * math.pi), rim='#BFD0FF')
        if land >= 1:
            for i in range(4): puff(c, 450 + (i - 1.5) * 90 * (1 + (t - 66.55) * 2), 960, 40, i + 20, '#C8C4D8', '#9A96B0', 255 * max(0, 1 - (t - 66.55) * 1.5))
    night(c, [('oval', 960, 900, 1200, 300, .5), ('pool', 1400, 600, 600, .4)], ambient='#5A64A8')
    chip(c, t, 63.6, 'THREAT LEVEL 2', 'STORM', '#F2D36B', y=180)

def U_quake(c, t):
    lt = t - 67.38; st = 68.0
    dx, dy = shake(t, st, .8, 28); c.translate(dx, dy)
    grad_rect(c, -400, -300, W + 400, 900, '#3A3A6A', '#C88A6A')
    mid = cached('mid', lambda cc: city_strip(cc, 900, 15, 150, 330, 90, 170, '#2E336A', '#232858', '#FFC864', .35))
    k = ease_out(K(t, st, .6))
    for i in range(8):
        c.save(); x = 100 + i * 240; c.translate(x, 900); c.rotate((-1) ** i * 9 * k * (1 if abs(x - 960) < 800 else 0)); c.translate(-x, -900)
        c.save(); c.clipRect(skia.Rect(x - 120, -300, x + 120, 900)); blit(c, mid, 0, 0); c.restore(); c.restore()
    grad_rect(c, -400, 880, W + 400, H + 300, '#5A4A44', '#3A302C', LW)
    draw_quake(c, 960, 960, 1.0, t, stomp=1 - K(t, st - .5, .5) if t < st else 0)
    if t > st:
        rr = random.Random(5)
        for i in range(14):
            a = rr.uniform(0, 3.14); L = 900 * k * rr.uniform(.5, 1)
            c.drawLine(960, 960, 960 + math.cos(a) * L * (1 if i % 2 else -1), 960 + 60 * rr.uniform(.2, 1), ink(8))
        for i in range(6): puff(c, 960 + (i - 2.5) * 260 * k, 940, 70, i + 30, '#B8A890', '#8A7A64', 255 * max(0, 1 - (t - st)))
    chip(c, t, 67.5, 'THREAT LEVEL 3', 'QUAKE', '#FF6A3A', y=180)

def V_eclipse(c, t):
    lt = t - 69.66
    grad_rect(c, -400, -300, W + 400, H + 300, '#2A0618', '#C8242C')
    c.drawCircle(1400, 260, 140, fp('#1A0408')); c.drawCircle(1400, 260, 150, ink(8, '#FF8A6A', 200, boil=False)); add_light(c, 1400, 260, 400, '#FF6A4A', 90)
    draw_gorrak(c, 960, 1100, 1.15, twos(t), roar=ease(K(lt, .6, .4)) * (.8 + .2 * math.sin(t * 20)), arm_r=40 + 20 * math.sin(t * 3), arm_l=40)
    sk = cached('eclcity', lambda cc: city_strip(cc, 1080, 33, 100, 260, 80, 160, '#1A0610', '#12040A', '#FF8A4A', .3))
    blit(c, sk)
    for i in range(3): flame(c, 300 + i * 650, 900, 1.0, t, i)
    chip(c, t, 69.8, 'THREAT LEVEL 4', 'ECLIPSE', '#B88AFF', y=180)

def W_extinction(c, t):
    lt = t - 72.43
    dx, dy = shake(t, 72.43, 4.6, 6); c.translate(dx, dy)
    grad_rect(c, -400, -300, W + 400, H + 300, '#000000', '#14040A')
    draw_extinction(c, 960, 1300, 1.0, t, eyes=ease(K(lt, .4, 2.0)))
    r = random.Random(7)
    for i in range(30):
        u = (r.random() + t * .1) % 1; c.drawCircle(r.uniform(0, W), H - u * H, 2, fp('#FF4A4A', 150 * (1 - u)))
    chip(c, t, 73.0, 'THREAT LEVEL 5', 'EXTINCTION', '#FF2A3A', y=180)

def X_map(c, t):
    lt = t - 77.04
    grad_rect(c, -400, -300, W + 400, H + 300, '#E8D6A8', '#C8B080')
    r = random.Random(1)
    for i in range(300): c.drawCircle(r.uniform(-200, W + 200), r.uniform(-200, H + 200), r.uniform(1, 3), fp('#A8905E', 90))
    land = skia.Path(); pts = [(200, 300), (500, 180), (900, 220), (1300, 150), (1700, 300), (1760, 700), (1400, 900), (900, 860), (500, 950), (220, 700)]
    land.moveTo(*pts[0]); [land.lineTo(*p) for p in pts[1:]]; land.close(); c.drawPath(land, fp('#D8C090')); c.drawPath(land, ink(LW))
    for (x, y, n) in ((480, 400, 'Port Vale'), (1450, 420, 'Meridian City'), (700, 760, 'Ashford')):
        circ(c, x, y, 14, '#3A2E2A', LW * .5); label(c, n, x, y - 30, 40, '#3A2E2A', KALAM, 'center', skew=0)
    hp = skia.Path(); hp.addOval(skia.Rect(980, 480, 1260, 680)); c.drawPath(hp, fp('#2A2018')); c.drawPath(hp, ink(LW))
    for i in range(12): a = i / 12 * 6.28; c.drawLine(1120 + math.cos(a) * 140, 580 + math.sin(a) * 100, 1120 + math.cos(a) * 200, 580 + math.sin(a) * 150, ink(4, '#3A2E2A'))
    k = ease(K(t, 79.2, .8))
    if k > 0:
        arc = skia.Path(); arc.addArc(skia.Rect(940, 440, 1300, 720), -90, 350 * k); c.drawPath(arc, ink(12, RED, boil=False))
    if t > 80.0:
        pk = pop(K(t, 80.0, .3)); c.save(); c.translate(1420, 820); c.rotate(-6); c.scale(pk, pk)
        label(c, '40 years ago...', 0, 0, 80, RED, FONT_HAND, 'center', skew=0); c.restore()

def Y_tower(c, t):
    lt = t - 82.22
    grad_rect(c, -400, -1400, W + 400, H + 300, '#5FA8E8', '#E8F4FF')
    p = skia.Path(); p.moveTo(760, 1100); p.lineTo(820, -1100); p.lineTo(1100, -1100); p.lineTo(1160, 1100); p.close()
    c.drawPath(p, sp(linear(760, 0, 1160, 0, [hx('#FFE48A'), hx('#E9B53C'), hx('#B8801E')]))); c.drawPath(p, ink(LW * 1.3))
    for j in range(30): c.drawLine(800, -1080 + j * 72, 1120, -1080 + j * 72, ink(3, '#B8801E', 160, boil=False))
    c.drawRect(skia.Rect(940, -1100, 980, 1100), fp('#FFFFFF', 60))
    circ(c, 960, -700, 120, '#1E2236', LW * 1.2); label(c, 'B', 960, -650, 150, '#F2C14E', MARKER, 'center', skew=0)
    for sx in (520, 1400):
        rect(c, sx - 6, 500, sx + 6, 1100, '#5A5A66', LW * .7)
        fl = skia.Path(); fl.moveTo(sx, 500); w_ = math.sin(t * 6 + sx) * 14
        fl.cubicTo(sx + 60, 490 + w_, sx + 120, 520 - w_, sx + 180, 510 + w_); fl.lineTo(sx + 180, 610 + w_); fl.cubicTo(sx + 120, 620 - w_, sx + 60, 590 + w_, sx, 600); fl.close()
        shape(c, fl, '#2E3A66'); circ(c, sx + 90, 556, 20, '#F2C14E', LW * .5)
    for i in range(5):
        x = (i * 300 + t * 140) % 2200 - 100; y = -300 + i * 120; w_ = 14 + 8 * math.sin(t * 14 + i)
        c.drawLine(x - w_, y - 8, x, y, ink(4)); c.drawLine(x, y, x + w_, y - 8, ink(4))

def Y_cam(t): k = ease(K(t, 82.22, 2.0)); return 1.0, 960, lerp(700, -300, k)

def Z_control(c, t):
    grad_rect(c, -400, -300, W + 400, H + 300, '#141A34', '#0A0E1E')
    for i in range(5):
        for j in range(2):
            x = 260 + i * 290; y = 120 + j * 220
            rect(c, x - 130, y - 90, x + 130, y + 90, '#0E1428', LW, 10)
            c.save(); c.clipRect(skia.Rect(x - 124, y - 84, x + 124, y + 84))
            k_ = (i + j) % 3
            if k_ == 0:
                for q in range(6): c.drawLine(x - 120, y + 40 - q * 14, x + 120, y + 40 - q * 14 + math.sin(t * 3 + q) * 10, ink(2, '#4AB0E8', 120, boil=False))
            elif k_ == 1: c.drawCircle(x, y, 50 + 10 * math.sin(t * 4 + i), ink(4, '#FF6A5A', boil=False)); c.drawCircle(x + 20, y - 10, 8, fp('#FF6A5A'))
            else:
                for q in range(5): c.drawRect(skia.Rect(x - 100 + q * 42, y + 60 - (30 + 40 * abs(math.sin(t + q))), x - 70 + q * 42, y + 60), fp('#B8F04A'))
            c.restore(); add_light(c, x, y, 200, '#4AB0E8', 30)
    for i in range(4):
        x = 280 + i * 450 if i < 2 else 280 + i * 450 + 0
        rect(c, x - 150, 820, x + 150, 900, '#2A3050', LW, 8)
        draw_char(c, x, 1020, .7, TECH, face=0, eyes='dot', mouth='flat', arms=(('lin', 'hold', 'push', .5 + .5 * math.sin(t * 20 + i)), ('lin', 'hold', 'push', .5 - .5 * math.sin(t * 20 + i))), shadow=False)
        rect(c, x - 130, 760, x + 130, 830, '#0E1428', LW * .8, 6)
    draw_char(c, 960, 1000, .95, EXEC, face=0, eyes='half', mouth=talk(t), arms=('hip', ('present' if math.sin(t * 2) > 0 else 'gesture')), rim='#4AB0E8')

def AA_panels(c, t):
    lt = t - 89.47
    grad_rect(c, -400, -300, W + 400, H + 300, '#1E1A34', '#0E0C1E')
    for i, t0 in enumerate((0, 1.0, 2.0)):
        k = back(K(lt, t0, .35), 1.6)
        if k <= 0: continue
        x = 340 + i * 620; c.save(); c.translate(x, 540); c.rotate((-1) ** i * 3); c.scale(k, k)
        rect(c, -280, -380, 280, 380, '#FFF6DC', LW * 1.3, 8)
        c.save(); c.clipRect(skia.Rect(-270, -370, 270, 370))
        if i == 0:
            grad_rect(c, -270, -370, 270, 370, '#8AC8F0', '#5A98D0')
            up = .5 + .5 * math.sin(t * 6)
            draw_char(c, 0, 330, .8, BRONZE, face=0, eyes='closed', mouth='grin', arms=(('lin', 'down', 'up', up), ('lin', 'down', 'up', up)), sweat=(t * 2) % 1)
            hy = 330 - lerp(168, 470, up) * .8; rect(c, -150, hy - 10, 150, hy + 10, '#3A3A44', LW * .7); circ(c, -150, hy, 40, '#26262E'); circ(c, 150, hy, 40, '#26262E')
            label(c, 'TRAINS', 0, -300, 64, '#FFFFFF', MARKER, 'center', stroke=10, skew=0)
        elif i == 1:
            grad_rect(c, -270, -370, 270, 370, '#9AD07A', '#5A9A4A')
            r = random.Random(2)
            for q in range(14):
                y = (r.uniform(-400, 400) + t * 300) % 800 - 400; xx = r.uniform(-240, 240)
                c.save(); c.translate(xx, y); c.rotate(t * 90 + q * 30); rect(c, -50, -24, 50, 24, '#B8E0A0', LW * .6, 4); label(c, '$', 0, 16, 40, '#3A6A2A', MARKER, 'center', skew=0); c.restore()
            label(c, 'PAYS', 0, -300, 64, '#FFFFFF', MARKER, 'center', stroke=10, skew=0)
        else:
            grad_rect(c, -270, -370, 270, 370, '#F2C14E', '#C8921E')
            for q in range(5):
                yy = -180 + q * 100; rect(c, -220, yy - 36, 220, yy + 36, '#1E2236', LW * .7, 8)
                label(c, f'#{q + 1}', -180, yy + 18, 48, '#F2C14E', MARKER, 'left', skew=0)
                c.drawRect(skia.Rect(-80, yy - 10, -80 + 260 * (1 - q * .17) * min(1, (lt - 2) * 2), yy + 10), fp('#B8F04A'))
            label(c, 'RANKS', 0, -300, 64, '#FFFFFF', MARKER, 'center', stroke=10, skew=0)
        c.restore(); c.restore()

def AB_sells(c, t):
    grad_rect(c, -400, -300, W + 400, H + 300, '#2A1E3E', '#120C1E')
    bokeh(c, 3, 30, ['#F2C14E', '#FFE38A'], 20, 60, t, a=80)
    r = random.Random(5)
    for q in range(40):
        y = (r.uniform(-200, 1200) + t * r.uniform(200, 380)) % 1300 - 150; x = r.uniform(0, W) + math.sin(t * 2 + q) * 40
        c.save(); c.translate(x, y); c.rotate(t * 120 + q * 40); c.scale(math.cos(t * 5 + q), 1)
        rect(c, -60, -28, 60, 28, '#B8E0A0', LW * .6, 4); label(c, '$', 0, 18, 44, '#3A6A2A', MARKER, 'center', skew=0); c.restore()
    draw_char(c, 960, 1080, 1.35, EXEC, face=.2, eyes='half', mouth='smirk', arms=('present', 'hip'), sparkle=K(t, 93.4, .5) * 1.8, rim='#F2C14E', brow=-.3)
    night(c, [('pool', 960, 500, 700, .7)], ambient='#6A5A9A')

def AC_merch(c, t):
    lt = t - 95.64
    grad_rect(c, -400, -300, W + 400, H + 300, '#F4E8D8', '#D8C8B0')
    for row in range(3):
        y = 260 + row * 220; rect(c, 120, y, 1800, y + 24, '#8C5E3F', LW, 4)
        for i in range(9):
            x = 220 + i * 180; spec = [AUREX, GOLDHERO, SILVER, BRONZE][(i + row) % 4]
            if row < 2: draw_char(c, x, y, .32, spec, face=.2, eyes='dot', mouth='grin', arms=('hip', 'up'), shadow=False)
    rect(c, 1300, 60, 1760, 240, '#141826', LW, 14)
    c.save(); c.clipRect(skia.Rect(1310, 70, 1750, 230)); grad_rect(c, 1310, 70, 1750, 230, '#4AB0E8', '#2E6BB5')
    draw_char(c, 1530 + math.sin(t * 3) * 80, 330, .55, GOLDHERO, face=.4, eyes='half', mouth='grin', arms=('up', 'hip'), shadow=False); c.restore()
    for i, t0 in enumerate((0, 1.35, 2.65)):
        k = back(K(lt, t0, .35), 1.8)
        if k <= 0: continue
        x = 560 + i * 400; c.save(); c.translate(x, 860); c.scale(k, k); c.rotate(math.sin(t * 3 + i) * 4)
        if i == 0: draw_char(c, 0, 120, .6, HERO if False else AUREX, face=.2, eyes='dot', mouth='grin', arms=('hip', 'up'), shadow=False); label(c, 'FIGURES', 0, 200, 50, '#C8242C', MARKER, 'center', stroke=8, stroke_col='#FFF6DC', skew=0)
        elif i == 1:
            rect(c, -130, -200, 130, 0, '#141826', LW, 14); c.drawRect(skia.Rect(-116, -186, 116, -14), fp('#4AB0E8'))
            label(c, 'TV', 0, -70, 80, '#FFFFFF', MARKER, 'center', skew=0); label(c, 'SHOWS', 0, 200 - 120, 50, '#C8242C', MARKER, 'center', stroke=8, stroke_col='#FFF6DC', skew=0)
        else:
            for q, dx in enumerate((-80, 0, 80)):
                rect(c, dx - 40, -220 + (q == 1) * -20, dx + 40, 0, '#D9262E', LW, 18); poly(c, [(dx - 10, -150), (dx + 14, -150), (dx - 4, -100), (dx + 16, -100), (dx - 14, -40), (dx - 2, -90), (dx - 18, -90)], '#FFFFFF', LW * .5)
            label(c, 'HERO FUEL', 0, 80, 50, '#C8242C', MARKER, 'center', stroke=8, stroke_col='#FFF6DC', skew=0)
        c.restore()
        add_light(c, x, 760, 260 * k, '#FFF6DC', 60)

def AD_celebs(c, t):
    PV.s3(c, 4.95 + (t - 99.54) * .88)

def AE_ranks(c, t):
    lt = t - 102.37
    stage(c, t, tint='#2A1E5A', spot=False)
    for i, kind in enumerate(('IRON', 'BRONZE', 'SILVER', 'GOLD', 'CROWN')):
        k = K(lt, .15 + i * .3, .4); y = lerp(-300, 520, ease_out(k)) if k < 1 else 520 + math.sin(t * 2 + i) * 8
        if k > 0: badge(c, 240 + i * 360, y, .8 + (.15 if kind == 'CROWN' else 0), kind)
        if k >= 1: add_light(c, 240 + i * 360, 520, 220, '#FFF6DC', 30)

def AF_iron(c, t):
    lt = t - 104.90
    street_day(c, t, 3000, cross=True)
    draw_car(c, 300 + math.sin(t) * 6, 1050, .9, '#4AB0E8'); draw_car(c, 1640, 1050, .9, '#E8D06A')
    alt = int(twos(t) * 2) % 2
    draw_char(c, 960, 1000, 1.0, IRONH, face=0, eyes='half', mouth='o', arms=('point' if alt else 'up', 'up' if alt else 'point'), sweat=(lt) % 1)
    draw_cat(c, 960 + 20, 1000 - 520 - 60, .9, t)
    badge(c, 1700, 240, .45, 'IRON')

def AG_bronze(c, t):
    lt = t - 108.22
    stage(c, t, tint='#3A2A1A')
    spin = K(t, 109.3, 1.0)
    c.save(); c.translate(1300, 820); c.rotate(spin * 720); c.translate(-1300, -820)
    draw_ember(c, 1300 + spin * 300, 860 - math.sin(spin * math.pi) * 300, .9, t, .8); c.restore()
    for i, (spec, x) in enumerate(((BRONZE, 420), (SILVER, 720))):
        firing = 108.7 + i * .2 < t < 109.6
        draw_char(c, x, 900, .9, spec, face=.6, eyes='half', mouth='open' if firing else 'smirk', arms=('fist', 'push' if firing else 'fist'), rim='#FFE9A8')
        if firing:
            y = 900 - 262 * .9; x0 = x + 200 * .9
            c.drawLine(x0, y, 1300, 760, ink(36, ['#FF9A4A', '#9FD6FF'][i], 200, boil=False)); c.drawLine(x0, y, 1300, 760, ink(12, '#FFFFFF', boil=False))
            add_light(c, x0, y, 120, '#FFFFFF', 200)
    badge(c, 1520, 240, .4, 'BRONZE'); badge(c, 1760, 240, .4, 'SILVER')

def AH_gold(c, t):
    lt = t - 111.08
    grad_rect(c, -400, -300, W + 400, H + 300, '#2A2050', '#E8A04A')
    rect(c, 300, 60, 1620, 560, '#1E1A2E', LW * 1.2, 20); c.save(); c.clipRect(skia.Rect(320, 80, 1600, 540))
    grad_rect(c, 320, 80, 1600, 540, '#FFE48A', '#E9B53C'); draw_char(c, 700, 1200, 2.0, GOLDHERO, face=.3, eyes='half', mouth='grin', arms=('hip', 'up'), shadow=False)
    label(c, 'BE GOLDEN.', 1250, 360, 130, '#FFFFFF', MARKER, 'center', stroke=14, stroke_col='#B8801E', skew=0); c.restore()
    draw_char(c, 960, 1000, 1.0, GOLDHERO, face=-.1, eyes='half', mouth='grin', arms=('hip', 'up' if int(twos(t) * 3) % 2 else 'wave'), sparkle=(lt * 1.2) % 2, rim='#FFE9A8')
    r = random.Random(int(t * 10))
    for i in range(2):
        x = r.uniform(200, 1700); y = r.uniform(700, 1000); add_light(c, x, y, 140, '#FFFFFF', 230)
    badge(c, 1720, 860, .45, 'GOLD')

def AI_crown(c, t):
    lt = t - 113.76
    stage(c, t, tint='#3A2E10', spot=False)
    c.drawRect(skia.Rect(-400, -300, W + 400, 800), sp(radial(960, 200, 900, [hx('#FFE88A', 90), hx('#FFE88A', 0)])))
    for i in range(7):
        x = 300 + i * 220; y = 640 - abs(i - 3) * -10; k = K(lt, .1 + i * .15, .4)
        rect(c, x - 70, y, x + 70, y + 200, '#C8A04A', LW, 6)
        if k > 0:
            c.save(); c.saveLayerAlpha(None, int(255 * k))
            draw_char(c, x, y, .55, dict(AUREX, suit='#2A2414', suit_d='#1A160C', skin='#2A2414', skin_d='#1A160C', hair_col='#2A2414', cape='#1A160C', star=None, tie='#2A2414', shirt='#2A2414', glove='#2A2414'),
                      face=0, eyes='closed', mouth='flat', arms=('hip', 'hip'), rim='#FFE88A', shadow=False)
            c.drawOval(skia.Rect(x - 50, y - 330, x + 50, y - 300), ink(6, '#FFE88A', boil=False)); add_light(c, x, y - 315, 80, '#FFE88A', 160)
            c.restore(); c.restore()
    bow = .5 + .5 * math.sin(t * 2.4)
    r = random.Random(3)
    for i in range(10):
        x = 60 + i * 200; s = 1.1
        c.save(); c.translate(x, 1100 - 0); c.rotate(-20 * bow * (1 if i % 2 else .8)); c.scale(s, s)
        rect(c, -80, -40, 80, 200, TEENS[i % 4]['suit_d'], LW, 60); circ(c, 0, -110, 82, TEENS[i % 4].get('hair_col', '#1D1A20') if TEENS[i % 4]['hair'] != 'cap' else '#D9473A')
        c.restore()
    badge(c, 1760, 200, .4, 'CROWN')

def AJ_how(c, t):
    lt = t - 116.81
    stage(c, t, tint='#1E3A5A')
    for i, kind in enumerate(('IRON', 'BRONZE', 'SILVER', 'GOLD', 'CROWN')):
        a = t * .6 + i / 5 * 6.28; badge(c, 960 + math.cos(a) * 560, 480 + math.sin(a) * 200, .35, kind)
    draw_char(c, 960, 900, 1.05, TEENS[1], face=math.sin(t * 1.5) * .4, eyes='dot', mouth='o' if lt < 2.5 else 'flat', arms=('down', 'chin'), tilt=8 * math.sin(t * 1.5), pupil=math.sin(t * 1.5))
    for i, t0 in enumerate((.4, 1.2, 2.0)):
        k = pop(K(lt, t0, .3));
        if k > 0:
            c.save(); c.translate(760 + i * 200, 360 - i * 30); c.rotate(-10 + i * 10); c.scale(k, k); label(c, '?', 0, 0, 160, '#F2C14E', MARKER, 'center', stroke=12, skew=0); c.restore()

def AK_birthday(c, t):
    lt = t - 122.15
    room_bg(c)
    rect(c, 500, 760, 1420, 800, '#8C5E3F', LW, 6); rect(c, 540, 800, 580, 1080, '#6E4A33', LW); rect(c, 1340, 800, 1380, 1080, '#6E4A33', LW)
    blow = K(lt, 1.6, .5)
    draw_char(c, 960, 880, 1.2, TEENS[2], face=0, eyes='closed' if lt > 1.4 else 'dot', mouth='o' if 1.4 < lt < 2.3 else 'grin', squash=-.05 * math.sin(blow * math.pi), blush=.8, arms=('down', 'down'), shadow=False)
    rect(c, 780, 650, 1140, 770, '#F4D6E0', LW, 20); rect(c, 780, 650, 1140, 686, '#FFFFFF', LW * .7, 16)
    for i in range(5): c.drawCircle(800 + i * 80, 700, 10, fp('#E84A8A'))
    label(c, '18', 960, 745, 70, '#E84A8A', MARKER, 'center', skew=0)
    for i in range(6):
        x = 820 + i * 56; rect(c, x - 8, 600, x + 8, 650, ['#4AB0E8', '#F2C14E', '#B8F04A'][i % 3], LW * .5)
        if blow < .6:
            flame(c, x, 600, .25, t, i)
        elif blow < 1.0 or lt < 2.6:
            for q in range(3): c.drawCircle(x + math.sin(t * 4 + q) * 10, 580 - q * 20 - (lt - 2) * 30, 6 + q * 2, fp('#C8C8D0', 140))
    if lt > 2.1:
        r = random.Random(4)
        for i in range(50):
            x = r.uniform(0, W); y = ((lt - 2.1) * r.uniform(300, 600) + r.uniform(-400, 0));
            c.save(); c.translate(x, y); c.rotate(t * 300 + i * 30); c.drawRect(skia.Rect(-8, -5, 8, 5), fp(r.choice(['#F2C14E', '#D9262E', '#4AB0E8', '#B8F04A']))); c.restore()
    night(c, [('pool', 960, 560, 700, .6)], ambient='#8A8AC0')

def AL_walkin(c, t):
    lt = t - 125.42
    hall(c, t)
    PV.scanner(c, 1400, '---', 999, 999, t)
    wk = ease_out(K(lt, 0, 3.4)) if True else 0; x = lerp(-200, 1140, min(1, lt / 3.4)); walking = lt < 3.4
    reach = K(lt, 3.6, .3)
    draw_char(c, x, 900, .95, TEENS[2], face=.55, eyes='dot', mouth='flat', legs=walk_legs(lt * 9) if walking else None,
              arms=walk_arms(lt * 9) if walking else ('down', ('down', 'scan', reach)), sweat=(lt - 3.6) if lt > 3.6 else -1, pupil=.5)
    if reach >= 1: add_light(c, 1400, 590, 260, '#7CF2E0', 120)
    night(c, [('pool', 1100, 500, 1150, .62), ('oval', 1100, 900, 1300, 200, .5)], ambient='#6670B2')

def AM_reads(c, t):
    lt = t - 130.69
    blit(c, BG_HALL(), 0, 0, blur=14)
    draw_char(c, 700, 1400, 2.15, TEENS[2], face=.45, eyes='closed', mouth='flat', arms=('down', 'scan'), shadow=False, rim='#9FF6EA')
    for i in range(4):
        u = (lt * .8 + i / 4) % 1
        c.drawOval(skia.Rect(700 - 300 - u * 200, 300 + u * 900 - 80, 700 + 300 + u * 200, 300 + u * 900 + 80), ink(8, '#7CF2E0', 200 * (1 - u), boil=False))
    sx = 1460; rect(c, sx - 280, 140, sx + 280, 470, '#141826', LW * 1.3, 28)
    num = int(min(1000, lt / 3.6 * 1000)) if lt < 3.6 else 1000
    label(c, 'SPARK SCORE', sx, 200, 46, '#9AA4B8', KALAM, 'center', skew=0)
    label(c, f'{num}', sx, 400, 200, '#7CF2E0', MARKER, 'center', skew=0)
    label(c, '0  -  1000', sx, 560, 60, '#FFF6DC', MARKER, 'center', stroke=10, skew=0)
    add_light(c, sx, 330, 420, '#7CF2E0', 60)

def score_shot(c, t, t0, teen, num, col, extra):
    lt = t - t0; land = t0 + .6
    blit(c, BG_HALL(), 0, 0, blur=12)
    PV.scanner(c, 1250, num, t0 - .1, land, t, land_col=col)
    landed = t >= land; hop = abs(math.sin(K(t, land, .5) * math.pi)) * 70 if landed else 0
    draw_char(c, 900, 900 - hop, 1.0, teen, face=.5 if not landed else .1, eyes='closed' if landed and t < land + .6 else 'dot', mouth='grin' if landed else 'flat',
              arms=('down', 'scan') if not landed else ('up', 'up'), sparkle=K(t, land + .1, .5) * 1.7, blush=.6 if landed else 0, squash=.1 * math.sin(K(t, land, .2) * math.pi))
    extra(c, t, landed, land)
    night(c, [('pool', 1050, 500, 900, .62)], ambient='#6670B2')

def AN_100(c, t):
    def ex(c, t, landed, land):
        if landed: chip(c, t, land + .2, 'SCORE ABOVE 100', 'HERO', '#B8F04A', 960, 220)
    score_shot(c, t, 135.40, TEENS[0], '412', '#B8F04A', ex)

def AO_500(c, t):
    def ex(c, t, landed, land):
        if landed:
            r = random.Random(int(t * 10))
            for i in range(3): x = r.uniform(300, 1700); y = r.uniform(300, 900); add_light(c, x, y, 160, '#FFFFFF', 240)
            chip(c, t, land + .2, 'SCORE ABOVE 500', 'FAMOUS', '#F2C14E', 960, 220)
    score_shot(c, t, 139.64, TEENS[1], '640', '#F2C14E', ex)

def AP_900(c, t):
    def ex(c, t, landed, land):
        if landed:
            add_light(c, 900, 600, 600, '#FFE88A', 150)
            for i in range(12):
                a = i / 12 * 6.28 + t; c.drawLine(900 + math.cos(a) * 300, 620 + math.sin(a) * 300, 900 + math.cos(a) * 420, 620 + math.sin(a) * 420, ink(8, '#FFE88A', 180, boil=False))
            k = ease_out(K(t, land + 1.0, .35)); y = lerp(-100, 900 - 480, k)
            poly(c, [(840, y + 40), (840, y - 20), (870, y + 10), (900, y - 40), (930, y + 10), (960, y - 20), (960, y + 40)], '#FFE88A', LW)
            chip(c, t, land + .2, 'SCORE ABOVE 900', 'CROWN', '#FFE88A', 960, 220)
    score_shot(c, t, 142.71, TEENS[3], '921', '#FFE88A', ex)

def AQ_future(c, t):
    lt = t - 146.92; pan = lt * 150
    street_day(c, t, 4000 + pan)
    for i, (num, col_) in enumerate((('712', '#B8F04A'), ('88', '#FF6A5A'), ('530', '#F2C14E'), ('905', '#FFE88A'))):
        x = 300 + i * 440 - lt * 40 * (1 if i % 2 else -1); ph = lt * 8 + i
        walker(c, t, x, 960, .85, TEENS[i], ph, face=.5 if i % 2 else -.5, mouth='grin' if num != '88' else 'frown', eyes='dot' if num != '88' else 'half')
        y = 960 - 520 * .85 - 30 + math.sin(t * 3 + i) * 8
        rect(c, x - 80, y - 60, x + 80, y + 10, '#141826', LW * .8, 14); label(c, num, x, y - 2, 60, col_, MARKER, 'center', skew=0); add_light(c, x, y - 25, 120, col_, 60)

def AR_you(c, t):
    lt = t - 150.88
    stage(c, t, tint='#14102A', spot=False)
    on = K(lt, .15, .08)
    if on > 0:
        c.drawPath(cone_path(960, -100, 80, 760, 980), sp(linear(0, -100, 0, 880, [hx('#FFF6DC', 110 * on), hx('#FFF6DC', 14 * on)]), blend=skia.BlendMode.kPlus))
        c.drawOval(skia.Rect(560, 840, 1360, 940), fp('#FFF6DC', 70 * on, blur=20))
    look = math.sin(lt * 4) if lt < 1.6 else 0
    draw_char(c, 960, 900, 1.1, HERO, face=look * .6, eyes='wide' if lt < 1.8 else 'dot', mouth='o' if lt < 1.8 else 'smile', pupil=look,
              arms=('down', 'self') if lt > 1.8 else ('down', 'down'), brow=.8, squash=.06 * math.sin(K(lt, 1.8, .2) * math.pi), blush=.5)
    if lt > 1.9:
        k = pop(K(lt, 1.9, .3)); c.save(); c.translate(1250, 400); c.scale(k, k); label(c, 'me?', 0, 0, 110, '#FFF6DC', FONT_HAND, 'center', stroke=10, skew=0); c.restore()

SHOTS_A = [
    (0.0, 2.1, PV.s1, PV.s1_cam),
    (2.1, 4.95, PV.s2, lambda t: (lerp(1.04, 1.12, ease(K(t, 2.1, 2.85))), 960, 560)),
    (4.95, 7.45, PV.s3, lambda t: (lerp(1.0, 1.1, ease(K(t, 4.95, 2.5))), 960, 520)),
    (7.45, 11.3, PV.s4, PV.s4_cam),
    (11.3, 14.05, PV.s5, PV.s5_cam),
    (14.05, 16.95, A_weakest, None), (16.95, 18.56, B_card, None), (18.56, 19.87, C_news, None), (19.87, 22.10, D_kids, None),
    (22.10, 25.44, E_secret, None), (25.44, 26.77, F_sunrise, None), (26.77, 30.84, G_aurex, lambda t: (lerp(1.25, 1.05, ease(K(t, 26.77, 4))), 960, 520)),
    (30.84, 34.73, H_subscribe, None), (34.73, 38.80, I_portal, None), (38.80, 39.97, J_title, lambda t: (lerp(1.0, 1.12, ease(K(t, 38.8, 1.2))), 960, 560)),
    (39.97, 42.85, K_cinema, None), (42.85, 44.54, L_ground, None), (44.54, 46.95, M_breach, None), (46.95, 49.27, N_scientist, None),
    (49.27, 51.59, O_monsters, None), (51.59, 53.48, P_dog, None), (53.48, 55.52, Q_building, Q_cam), (55.52, 59.29, R_meter, None),
    (59.29, 63.49, S_ember, None), (63.49, 67.38, T_storm, None), (67.38, 69.66, U_quake, None), (69.66, 72.43, V_eclipse, None),
    (72.43, 77.04, W_extinction, None), (77.04, 82.22, X_map, None), (82.22, 84.24, Y_tower, Y_cam), (84.24, 89.47, Z_control, None),
    (89.47, 92.69, AA_panels, None), (92.69, 95.64, AB_sells, None), (95.64, 99.54, AC_merch, None), (99.54, 102.37, AD_celebs, None),
    (102.37, 104.90, AE_ranks, None), (104.90, 108.22, AF_iron, None), (108.22, 111.08, AG_bronze, None), (111.08, 113.76, AH_gold, None),
    (113.76, 116.81, AI_crown, None), (116.81, 122.15, AJ_how, None), (122.15, 125.42, AK_birthday, None), (125.42, 130.69, AL_walkin, None),
    (130.69, 135.40, AM_reads, None), (135.40, 139.64, AN_100, None), (139.64, 142.71, AO_500, None), (142.71, 146.92, AP_900, None),
    (146.92, 150.88, AQ_future, None),
]
