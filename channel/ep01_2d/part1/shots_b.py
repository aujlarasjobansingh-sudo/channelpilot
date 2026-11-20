# EP01 Part 1 shots 150.9 - 310.6 s
from shots_a import *

def AS_mom(c, t):
    lt = t - 154.42; pan = lt * 200
    street_day(c, t, 5000 + pan)
    ph = lt * 8
    walker(c, t, 1080, 990, 1.0, MOM, ph, face=-.2 + .3 * math.sin(lt), eyes='closed' if blink(t, 2.6) else 'dot', mouth=talk(t), arms=(walk_arms(ph)[0], 'hold'), blush=.4)
    walker(c, t, 820, 1000, .9, HERO, ph + 1.2, face=.5, eyes='dot', mouth='grin', arms=('hold', walk_arms(ph + 1.2)[1]), blush=.7, sparkle=(lt * .8) % 2)

def AT_shirt(c, t):
    lt = t - 159.51
    blit(c, BG_HALL(), 0, 0, blur=14)
    draw_char(c, 960, 1650, 2.6, HERO, face=.1, eyes='closed', mouth='grin', arms=('hip', 'hip'), blush=.8, shadow=False, squash=.04 * math.sin(K(lt, .2, .3) * math.pi))
    bx, by = 960 + 18 * 2.6 * .1, 1650 + (BODY_TOP + 98) * 2.6
    k = pop(K(lt, .5, .4))
    for i in range(8):
        a = i / 8 * 6.28 + t * .5; c.drawLine(bx + math.cos(a) * 120 * k, by + math.sin(a) * 120 * k, bx + math.cos(a) * 190 * k, by + math.sin(a) * 190 * k, ink(8, '#FFFFFF', 200, boil=False))
    add_light(c, bx, by, 300 * k, '#FFFFFF', 80)

def AU_drawing(c, t):
    lt = t - 163.83
    room_bg(c)
    rect(c, 300, 760, 1620, 800, '#8C5E3F', LW, 6)
    for i, cl in enumerate(('#E84A4A', '#4AB0E8', '#F2C14E', '#4E9A6E')):
        c.save(); c.translate(1300 + i * 50, 745); c.rotate(-20 + i * 15); rect(c, -60, -10, 60, 10, cl, LW * .6, 4); c.restore()
    hold = lt > 3.6
    shirt_x, shirt_y = (760, 700) if not hold else (960, lerp(700, 420, ease_out(K(lt, 3.6, .4))))
    def shirt(x, y, s, bolt):
        c.save(); c.translate(x, y); c.scale(s, s)
        poly(c, [(-150, -120), (-60, -150), (60, -150), (150, -120), (200, -40), (130, -10), (110, -60), (110, 150), (-110, 150), (-110, -60), (-130, -10), (-200, -40)], '#D9262E')
        if bolt > 0:
            k = bolt
            pts = [(10, -80), (-40, 10), (0, 10), (-20, 90), (50, -20), (10, -20)]
            n = max(2, int(len(pts) * k)); pth = skia.Path(); pth.moveTo(*pts[0]); [pth.lineTo(*p) for p in pts[1:n]]
            if k >= 1: pth.close(); c.drawPath(pth, fp('#FFFFFF'))
            c.drawPath(pth, ink(LW * .8))
        c.restore()
    if not hold:
        shirt(shirt_x, shirt_y + 30, .9, K(lt, .3, 2.6))
        draw_char(c, 1000, 960, .8, dict(KIDHERO, cape='#4AB0E8'), face=-.5, eyes='dot', mouth='smile' if lt < 2.8 else 'grin', arms=('down', ('lin', 'draw', 'hold', .5 + .5 * math.sin(t * 14))), pupil=-1, tilt=10, shadow=False)
    else:
        draw_char(c, 960, 960, .8, dict(KIDHERO, cape='#4AB0E8'), face=0, eyes='closed', mouth='grin', arms=('up', 'up'), blush=.9, sparkle=K(lt, 4.0, .5) * 1.6, squash=.08 * math.sin(K(lt, 3.6, .3) * math.pi), shadow=False)
        shirt(shirt_x, shirt_y, .9, 1)
        if lt > 4.2:
            k = pop(K(lt, 4.2, .3)); c.save(); c.translate(1400, 330); c.rotate(-8); c.scale(k, k); label(c, 'age 9', 0, 0, 80, '#FFF6DC', FONT_HAND, 'center', stroke=8, skew=0); c.restore()
    night(c, [('pool', 960, 600, 700, .6)], ambient='#8A8AC0')

def AV_hand(c, t):
    lt = t - 169.75
    blit(c, BG_HALL(), 0, 0, blur=14)
    sx = 1450
    rect(c, sx - 280, 140, sx + 280, 470, '#141826', LW * 1.3, 28); label(c, '---', sx, 380, 200, '#5A6A80', MARKER, 'center', skew=0)
    line(c, sx, 470, sx, 600, LW * 3)
    rect(c, sx - 130, 600, sx + 130, H + 60, '#D7DDE8', LW * 1.3, 30); rect(c, sx - 100, 660, sx + 100, 820, '#1E2A3A', LW, 18)
    reach = K(lt, .6, .5)
    if reach >= 1: c.drawRect(skia.Rect(sx - 86, 674, sx + 86, 806), fp('#7CF2E0', 200)); add_light(c, sx, 740, 300, '#7CF2E0', 100)
    draw_char(c, 760, 1400, 2.15, HERO, face=.5, eyes='dot' if not blink(t, 1.8) else 'closed', mouth='flat', arms=('down', ('down', 'scan', reach)), sweat=lt * .6 % 1, brow_tilt=.8,
              squash=.05 * math.sin(K(lt, 2.4, .3) * math.pi), shadow=False, rim='#9FF6EA')
    blit(c, cached('mom_bl', lambda cc: draw_char(cc, 260, 1200, 1.4, MOM, face=.5, eyes='dot', mouth='smile', arms=('heart', 'heart'), shadow=False)), 0, 0, blur=6)

def AW_bar(c, t):
    lt = t - 173.57
    blit(c, BG_HALL(), 0, 0, blur=16)
    rect(c, 760, 60, 1160, 1020, '#141826', LW * 1.4, 30)
    lvl = min(3, lt / .3) if lt < 1.0 else (3 if lt < 2.2 else max(0, 3 - (lt - 2.2) * 8))
    flick = lt > 1.0 and lt < 2.2 and int(t * 16) % 2
    for i in range(10):
        y = 960 - i * 88; on = i < lvl and not flick
        c.drawRect(skia.Rect(800, y - 70, 1120, y), fp('#7CF2E0' if on else '#26304A'))
        if on: add_light(c, 960, y - 35, 200, '#7CF2E0', 60)
    label(c, 'SPARK', 960, 1060, 50, '#9AA4B8', KALAM, 'center', skew=0)

def AX_zero(c, t):
    lt = t - 177.47
    grad_rect(c, -400, -300, W + 400, H + 300, '#7A0E1E', '#2A0408')
    speed_lines(c, t, 960, 540, '#000000', 160, 70, 380)
    k = pop(K(lt, 0, .25)); c.save(); c.translate(960, 720); c.scale(k * 1.4, k * 1.4); label(c, '0', 0, 0, 500, '#FF4A4A', MARKER, 'center', stroke=24, stroke_col='#FFF6DC', skew=0); c.restore()

def AY_notfive(c, t):
    blit(c, BG_HALL(), 0, 0, blur=16)
    for i, (num, t0) in enumerate((('5', 178.49), ('1', 179.58), ('0', 180.2))):
        k = pop(K(t, t0, .3)); x = 520 + i * 440
        if k <= 0: continue
        c.save(); c.translate(x, 680); c.scale(k, k); label(c, num, 0, 0, 380, '#FFF6DC' if num != '0' else '#FF4A4A', MARKER, 'center', stroke=20, skew=0); c.restore()
        if num != '0' and t > t0 + .35:
            kk = ease(K(t, t0 + .35, .2)); c.drawLine(x - 160, 380, x - 160 + 320 * kk, 380 + 380 * kk, ink(30, RED, boil=False))

def tech_desk(c, t):
    grad_rect(c, -400, -300, W + 400, H + 300, '#4E5E8A', '#2E3A5E')
    rect(c, 1150, 160, 1700, 500, '#141826', LW * 1.2, 20); label(c, '0', 1425, 440, 260, '#FF4A4A', MARKER, 'center', skew=0)
    add_light(c, 1425, 330, 400, '#FF4A4A', 50)

def AZ_laugh(c, t):
    lt = t - 180.83; dx, dy = shake(t, 180.9, 2.0, 5); c.translate(dx, dy)
    tech_desk(c, t)
    sh = math.sin(t * 30) * 6
    draw_char(c, 760 + sh, 1050, 1.25, TECH, face=.15, eyes='closed', mouth='open', arms=('laugh', 'laugh'), bob=abs(math.sin(twos(t) * 12)) * 16, tilt=sh, blush=.9, squash=.04 * math.sin(t * 24))
    for i in range(2):
        u = (lt * 2 + i * .5) % 1; c.drawCircle(760 - 60 + i * 120 + (i * 2 - 1) * u * 80, 1050 - 1.25 * 420 + u * 120, 9, fp('#8FC8EE'))
    rect(c, 300, 900, 1300, 1100, '#6A5A4A', LW, 10)
    for i, s_ in enumerate(('HA', 'HA', 'HA')):
        k = pop(K(lt, .2 + i * .35, .25))
        if k > 0: c.save(); c.translate(1050 + i * 120, 450 - i * 60); c.rotate(-10 + i * 8); c.scale(k, k); label(c, s_, 0, 0, 90, '#FFF6DC', MARKER, 'center', stroke=10, skew=0); c.restore()

def BA_never(c, t):
    tech_desk(c, t)
    draw_char(c, 760, 1050, 1.25, TECH, face=.35, eyes='half', mouth=talk(t), arms=('chin', ('down', 'point', K(t, 183.5, .3))), blush=.5, brow=.4, tilt=4 * math.sin(t * 2))
    rect(c, 300, 900, 1300, 1100, '#6A5A4A', LW, 10)

def BB_photo(c, t):
    lt = t - 186.28
    tech_desk(c, t)
    up = K(lt, .1, .4)
    draw_char(c, 760, 1050, 1.25, TECH, face=.5, eyes='half', mouth='grin', arms=('hold', ('down', 'phone', up)), sparkle=K(lt, 1.0, .5) * 1.5)
    hx_, hy_ = 760 - (-70) * 1.25 * -1 * -1, 1050 - 400 * 1.25
    px = 760 + 70 * 1.25; py = 1050 - 400 * 1.25
    if up >= 1:
        rect(c, px - 34, py - 70, px + 34, py + 30, '#22222A', LW * .8, 10)
        if 186.28 + .9 < t < 186.28 + 1.05:
            c.drawRect(skia.Rect(-400, -300, W + 400, H + 300), fp('#FFFFFF', 220))
        add_light(c, px, py - 60, 80, '#FFFFFF', 160)
    rect(c, 300, 900, 1300, 1100, '#6A5A4A', LW, 10)

def BC_viral(c, t):
    lt = t - 188.45
    grad_rect(c, -400, -300, W + 400, H + 300, '#2A2050', '#14102A')
    def scr(cc, tt):
        grad_rect(cc, -180, -340, 180, 340, '#E8D06A', '#C8A04A')
        draw_char(cc, 0, 300, .7, HERO, face=0, eyes='dot', mouth='flat', shadow=False); label(cc, '0', 110, -200, 120, RED, MARKER, 'center', stroke=8, skew=0)
        label(cc, 'lol', -90, -240, 60, '#FFFFFF', FONT_HAND, 'center', stroke=6, skew=0)
    for i in range(6):
        k = back(K(lt, i * .25, .3), 1.6)
        if k > 0: phone_ui(c, 220 + i * 300, 560 + (i % 2) * 60 + math.sin(t * 2 + i) * 10, .55 * k, scr, t)
        if k > 0:
            n_ = pop(K(lt, i * .25 + .3, .2)); bx = 220 + i * 300 + 90; by = 560 + (i % 2) * 60 - 200
            circ(c, bx, by, 26 * n_, '#E02A2A', LW * .6); label(c, '99+', bx, by + 10, 26 * n_, '#FFFFFF', KALAM, 'center', skew=0)
    if lt > 1.5:
        k = ease_out(K(lt, 1.5, .5)); c.save(); c.translate(960, 560); c.rotate((1 - k) * 720 - 6); c.scale(k * 1.1, k * 1.1)
        rect(c, -420, -280, 420, 280, '#F4F0E4', LW * 1.2, 4); label(c, 'THE DAILY MERIDIAN', 0, -200, 54, '#2A2420', MARKER, 'center', skew=0)
        c.drawLine(-390, -170, 390, -170, ink(4)); label(c, 'THE ZERO KID', 0, -70, 110, '#2A2420', MARKER, 'center', skew=0)
        rect(c, -380, -20, -40, 240, '#C8C0A8', LW * .7); draw_char(c, -210, 330, .6, HERO, face=0, eyes='dot', mouth='flat', shadow=False)
        for q in range(7): c.drawLine(0, 0 + q * 34, 380, 0 + q * 34, ink(4, '#8A8478', boil=False))
        c.restore()

def BD_memes(c, t):
    lt = t - 191.55
    grad_rect(c, -400, -300, W + 400, H + 300, '#F2B8C8', '#D88AA8')
    draw_char(c, 760, 1000, 1.1, SHOUTER, face=.3, eyes='closed', mouth=talk(t) if talk(t) != 'flat' else 'grin', arms=('hold', ('lin', 'hold', 'draw', .5 + .5 * math.sin(t * 16))), bob=abs(math.sin(twos(t) * 6)) * 10)
    gx, gy = 760, 1000 - 250 * 1.1
    c.save(); c.translate(gx, gy); c.rotate(-30)
    oval(c, -110, -80, 60, 80, '#C8742A'); circ(c, -30, 0, 26, '#3A1E0E'); rect(c, 50, -14, 330, 14, '#6A3A1A', LW * .8); c.restore()
    r = random.Random(3)
    for i in range(8):
        u = (lt * .5 + i / 8) % 1; x = 900 + u * 700 + math.sin(t * 3 + i) * 30; y = 600 - u * 500
        label(c, '♪' if i % 2 else '♫', x, y, 90, '#FFFFFF', None, 'center', stroke=8, alpha=math.sin(u * math.pi), skew=0)
    for i in range(3):
        k = pop(K(lt, .4 + i * .6, .3)); x = 1450 + (i - 1) * 140; y = 300 + i * 220
        if k > 0:
            c.save(); c.translate(x, y); c.scale(k, k); circ(c, 0, 0, 80, '#F2D36B', LW)
            for ex in (-28, 28): c.drawArc(skia.Rect(ex - 14, -20, ex + 14, 8), 200, 140, False, ink(6))
            mp = skia.Path(); mp.moveTo(-40, 14); mp.quadTo(0, 70, 40, 14); mp.close(); shape(c, mp, '#5A1A1E', LW * .7)
            c.drawCircle(-50, 0, 12, fp('#8FC8EE')); c.restore()

def BE_license(c, t):
    lt = t - 195.50
    stage(c, t, tint='#1E2A5A')
    k = back(K(lt, 0, .5), 1.4); license_card(c, 960, lerp(1500, 520, k), 1.25, t, k)
    if lt > 2.2:
        st = K(lt, 2.2, .18); sc = lerp(2.4, 1, ease_out(st))
        c.save(); c.translate(1260, 780); c.rotate(-12); c.scale(sc, sc)
        p = skia.Path(); p.addRRect(skia.RRect.MakeRectXY(skia.Rect(-210, -70, 210, 70), 16, 16)); c.drawPath(p, ink(12, '#8A90A0', 255 * min(1, st * 2), boil=False))
        label(c, 'IRON', 0, 44, 110, '#8A90A0', MARKER, 'center', skew=0, alpha=min(1, st * 2)); c.restore()

def BF_list(c, t):
    lt = t - 203.47
    grad_rect(c, -400, -300, W + 400, H + 300, '#141826', '#0A0C14')
    rect(c, 360, 40, 1560, 1040, '#1E2236', LW * 1.3, 24)
    label(c, 'OFFICIAL HERO RANKINGS', 960, 120, 64, '#F2C14E', MARKER, 'center', skew=0)
    c.save(); c.clipRect(skia.Rect(380, 150, 1540, 1020))
    scroll = ease(K(lt, 0, 2.0)) * 4800
    names = ['AUREX', 'VELA STORM', 'KORVAN', 'THE TIDE', 'NOVA PRIME', 'IRONCLAD', 'BLAZE', 'ECHO', 'MIRA OKAFOR', 'QUILL']
    for i in range(80):
        y = 220 + i * 64 - scroll; n = i + 1 if i < 60 else 4812 - (79 - i)
        if -60 < y < 1100:
            last = n == 4812; col_ = '#FF4A4A' if last else '#FFF6DC'
            if last: c.drawRect(skia.Rect(390, y - 46, 1530, y + 14), fp('#5A0E14')); add_light(c, 960, y - 16, 400, '#FF4A4A', 60 * (.6 + .4 * math.sin(t * 6)))
            label(c, f'#{n:,}', 420, y, 44, col_, MARKER, 'left', skew=0)
            label(c, 'THE ZERO' if last else (names[i % 10] if i < 10 else ['HERO', 'AGENT', 'SPARK', 'BOLT'][i % 4] + f' {i * 37 % 900}'), 700, y, 44, col_, KALAM, 'left', skew=0)
            label(c, 'IRON' if i >= 60 else ['CROWN', 'GOLD', 'SILVER', 'BRONZE'][min(3, i // 15)], 1500, y, 40, col_, KALAM, 'right', skew=0)
    c.restore()

def BG_shrug(c, t):
    lt = t - 207.89
    street_day(c, t, 6000)
    sh = K(lt, .8, .3)
    draw_char(c, 960, 1000, 1.1, HERO, face=.1, eyes='half' if lt > .8 else 'dot', mouth='smile', arms=(('down', 'shrug', sh), ('down', 'shrug', sh)), squash=.05 * math.sin(sh * math.pi), blush=.3)

def BH_oldlady(c, t):
    lt = t - 211.11; x = lerp(500, 1300, lt / 2.68)
    street_day(c, t, 3000, cross=True)
    draw_car(c, 180, 1060, .9, '#4AB0E8'); draw_car(c, 1760, 1060, .9, '#E84A6A')
    ph = lt * 6
    walker(c, t, x - 120, 1000, .85, OLDLADY, ph, face=.6, eyes='closed', mouth='smile', arms=(walk_arms(ph)[0], 'hold'), blush=.6)
    walker(c, t, x + 110, 1010, 1.0, HERO, ph + 1, face=.4, eyes='dot', mouth='smile', arms=('hold', walk_arms(ph + 1)[1]))

def BI_cat(c, t):
    lt = t - 213.79; scratch = 214.8
    street_day(c, t, 6800)
    rect(c, 1160, 200, 1220, 1000, '#7A5238', LW, 10)
    puff(c, 1190, 260, 230, 7, '#6EBB5E', '#4E9A44')
    c.save(); c.translate(980, 1000); c.rotate(-14)
    for sx in (-60, 60): rect(c, sx - 8, -620, sx + 8, 0, '#C89A5A', LW * .7)
    for j in range(7): c.drawLine(-60, -60 - j * 85, 60, -60 - j * 85, ink(10)); c.drawLine(-60, -60 - j * 85, 60, -60 - j * 85, ink(5, '#C89A5A', boil=False))
    c.restore()
    hit = t > scratch
    draw_char(c, 1050, 520, .85, HERO, face=.6, eyes='closed' if hit else 'dot', mouth='open' if hit else 'smile', arms=('hold', 'point' if not hit else 'flail'),
              squash=.08 * math.sin(K(t, scratch, .2) * math.pi), tilt=-10 if hit else 0, shadow=False)
    cx = 1290 if not hit else lerp(1290, 1110, ease_out(K(t, scratch - .1, .15)))
    draw_cat(c, cx, 330 if not hit else 420, .9, t, scared=1 if hit else 0)
    if hit and t < scratch + .7:
        for i in range(3): c.drawLine(1080 + i * 22, 300, 1050 + i * 22, 360, ink(7, RED, boil=False))

def BJ_parking(c, t):
    lt = t - 215.67
    k = lt / 1.76
    grad_rect(c, -400, -300, W + 400, 760, '#5FA8E8' if k < .5 else '#E89A6A', '#CFE8FF' if k < .5 else '#F6D0A8')
    sa = math.pi * (1 - k); c.drawCircle(960 + math.cos(sa) * 800, 700 - math.sin(sa) * 520, 70, fp('#FFE6A0'))
    grad_rect(c, -400, 740, W + 400, H + 300, '#6A6A74', '#4A4A54', LW)
    for i in range(8): c.drawLine(100 + i * 240, 800, 60 + i * 240, 1080, ink(6, '#F4F4F0', boil=False))
    rect(c, 1300, 520, 1500, 640, '#2A2A34', LW, 8)
    draw_char(c, 1550, 900, .7, GOLDHERO, face=-.4, eyes='half', mouth='grin', arms=('hip', 'up' if int(t * 3) % 2 else 'wave'), sparkle=(t * 1.5) % 2)
    draw_char(c, 1250, 900, .6, dict(TEENS[0], hair='cap', cap_col='#2E2E38'), face=.6, eyes='dot', mouth='flat', arms=('hold', 'hold'))
    rect(c, 1290, 640, 1390, 700, '#1A1A22', LW * .7, 8); circ(c, 1400, 670, 30, '#3A3A44', LW * .7)
    for x in (260, 500, 740):
        poly(c, [(x - 40, 1000), (x + 40, 1000), (x + 12, 860), (x - 12, 860)], '#FF7A2A'); c.drawRect(skia.Rect(x - 26, 920, x + 26, 940), fp('#FFFFFF'))
    shx = -math.cos(sa) * 140
    c.drawPath(skia.Path().addOval(skia.Rect(500 + shx - 120, 985, 500 + shx + 120, 1015)) if False else skia.Path(), fp((0, 0, 0)))
    draw_char(c, 600, 1000, 1.0, HERO, face=.2, eyes='half', mouth='flat', arms=('hip', 'down'), sweat=(lt * 1.2) % 1, tilt=3 * math.sin(t))
    rect(c, 140, 90, 500, 230, '#141826', LW, 14); hrs = int(k * 6); mins = int((k * 6 % 1) * 60)
    label(c, f'{hrs}h {mins:02d}m', 320, 190, 80, '#F2D36B', MARKER, 'center', skew=0)

def BK_whispers(c, t):
    lt = t - 217.43; pan = lt * 200
    street_day(c, t, 7600 + pan)
    for i, wx in enumerate((800, 1500, 2300, 2900)):
        x = wx - pan * .85
        draw_char(c, x, 900, .8, TEENS[i % 4], face=(-.6 if x > 960 else .6), eyes='half', mouth='smirk' if i % 2 else talk(t), arms=('heart' if i % 2 == 0 else 'point', 'down'), blush=.2)
        if i % 2 == 0:
            draw_char(c, x + 120, 905, .78, TEENS[(i + 1) % 4], face=-.4, eyes='dot', mouth='o', arms=('laugh', 'down'), pupil=-1)
    walker(c, t, 960, 1000, 1.0, HERO, lt * 9, face=.5, eyes='dot', mouth='flat', pupil=-.4)

def BL_taunt(c, t, who, t0):
    lt = t - t0
    street_day(c, t, 9000 + lt * 30)
    draw_char(c, 600, 1000, 1.15 if who == 0 else 1.2, KIDS[1] if who == 0 else SHOUTER if False else TEENS[2], face=.45, eyes='half', mouth=talk(t), arms=('hip', 'point'), brow=-.2, bob=abs(math.sin(twos(t) * 4)) * 6)
    walker(c, t, 1350 + lt * 50, 990, .95, HERO, lt * 8, face=-.3, eyes='closed' if lt > .6 else 'dot', mouth='smile', blush=.3)

def BM_wave(c, t):
    lt = t - 226.14; pan = lt * 280
    street_day(c, t, 9600 + pan)
    waving = lt < 2.4; wv = int(twos(t) * 6) % 2
    arms = ('wave' if wv else 'wave2', walk_arms(lt * 9)[1]) if waving else walk_arms(lt * 9)
    walker(c, t, 960, 1000, 1.05, HERO, lt * 9, face=.35, eyes='closed' if waving else 'dot', mouth='grin' if waving else 'smile', arms=arms, blush=.4)

def BN_roof(c, t):
    lt = t - 230.85
    grad_rect(c, -400, -300, W + 400, H + 300, '#070A22', '#24205A')
    r = random.Random(4)
    for i in range(80):
        x = r.uniform(0, W); y = r.uniform(0, 600); tw = .5 + .5 * math.sin(t * r.uniform(1, 4) + i)
        c.drawCircle(x, y, r.uniform(1, 2.6), fp('#FFFFFF', 120 + 135 * tw))
    c.drawCircle(1500, 200, 70, fp('#FFF4D0')); add_light(c, 1500, 200, 300, '#FFF4D0', 60)
    city = cached('roofcity', lambda cc: city_strip(cc, 1000, 51, 150, 450, 70, 150, '#141A40', '#0E1230', '#FFC864', .45, outline=False))
    blit(c, city, 0, 0, blur=2)
    draw_char(c, 900, 960, 1.2, HERO, face=.2, eyes='half', mouth='flat', arms=('hold', 'hold'), shadow=False, rim='#A9BCFF', tilt=6 + 2 * math.sin(t))
    rect(c, -400, 860, W + 400, H + 300, '#2A2E4A', LW)
    hscroll_lines(c, t, 300, 800, '#A9BCFF', 50, 600)
    night(c, [('pool', 1500, 200, 600, .5), ('pool', 900, 700, 500, .4)], ambient='#4A4A90')

def BO_hands(c, t):
    lt = t - 236.13
    grad_rect(c, -400, -300, W + 400, H + 300, '#14102A', '#2A1A30')
    g = ease(K(lt, 0, 2.5)) * (.8 + .2 * math.sin(t * 9))
    for sx in (-1, 1):
        x = 960 + sx * 280; y = 640 + math.sin(t * 2 + sx) * 10
        c.drawLine(x, 1200, x + sx * 30, y + 60, ink(150, boil=False)); c.drawLine(x, 1200, x + sx * 30, y + 60, ink(130, HERO['skin'], boil=False))
        c.drawLine(x + sx * 10, 1200, x + sx * 20, 900, ink(150, boil=False)); c.drawLine(x + sx * 10, 1200, x + sx * 20, 900, ink(130, HERO['suit'], boil=False))
        circ(c, x, y, 150, HERO['skin'], LW * 1.3)
        for f in range(4): c.drawLine(x - 90 + f * 60, y - 130, x - 80 + f * 58, y - 60, ink(5, '#C99068', boil=False))
        add_light(c, x, y, 420 * g, '#FF8A3C', 110 * g)
        c.drawCircle(x, y, 150, fp('#FF7A2A', 45 * g, blend=skia.BlendMode.kPlus))
        c.drawCircle(x, y, 156, ink(10, '#FFB45C', 200 * g, boil=False))
    r = random.Random(int(t * 12) // 2)
    for i in range(int(30 * g)):
        x = r.uniform(600, 1320); y = 600 - ((t * 200 + i * 40) % 500)
        c.drawCircle(x, y, r.uniform(2, 5), fp('#FFB45C', 220))

def BO_face(c, t):
    lt = t - 239.02
    hero_close(c, t, BG_NIGHT(), face=.2, eyes='half' if lt < 2 else 'dot', mouth='flat', pupil=.0, rim='#FF8A3C', arms=('down', 'down'))
    c.drawRect(skia.Rect(-400, 700, W + 400, H + 300), sp(linear(0, 1100, 0, 600, [hx('#FF6A2A', 160 * ease(K(lt, 0, 3))), hx('#FF6A2A', 0)]), blend=skia.BlendMode.kPlus))
    r = random.Random(9)
    for i in range(40):
        u = (r.random() + t * .3) % 1; c.drawCircle(r.uniform(300, 1300), 1100 - u * 900, r.uniform(2, 4), fp('#FFB45C', 200 * (1 - u)))

def BP_anger(c, t):
    lt = t - 242.55
    hero_close(c, t, BG_NIGHT(), face=.25, eyes='half', mouth='frown', brow=-.8, brow_tilt=-1.0, arms=('down', ('down', 'fist', K(lt, .2, .25))), rim='#FF6A5A',
               squash=.04 * math.sin(K(lt, .35, .2) * math.pi))
    c.drawRect(skia.Rect(-400, -300, W + 400, H + 300), fp('#FF2A2A', 50 + 30 * math.sin(t * 8), blend=skia.BlendMode.kPlus))

def BQ_wrong(c, t): text_card(c, t, 244.45, 245.73, 'You were wrong.', 150)

def BR_groceries(c, t):
    lt = t - 245.73; shake_on = t > 247.97
    if shake_on: dx, dy = shake(t, 247.97, 1.5, 10); c.translate(dx, dy)
    station(c, t, 0, False, 200 + min(lt, 2.2) * 120)
    ph = lt * 7; walking = not shake_on
    walker(c, t, 760, 1000, .85, OLDLADY, ph, face=.5 if walking else -.2, eyes='closed' if walking else 'wide', mouth=talk(t) if walking else 'o', arms=(walk_arms(ph)[0], 'down')) if walking else \
        draw_char(c, 760, 1000, .85, OLDLADY, face=-.2, eyes='wide', mouth='o', arms=('heart', 'heart'))
    if walking:
        walker(c, t, 1000, 1010, 1.0, HERO, ph + 1, face=-.3, eyes='dot', mouth='smile', arms=('bag', 'bag'))
    else:
        draw_char(c, 1000, 1010, 1.0, HERO, face=0, eyes='wide', mouth='o', arms=('bag', 'bag'), pupil=0, sweat=(t - 248) * 1.5)
    for sx in (-1, 1):
        bx = 1000 + sx * 125; by = 1010 - 160 + (math.sin(t * 40) * 6 if shake_on else 0)
        rect(c, bx - 50, by - 30, bx + 50, by + 90, '#D8B888', LW * .8, 8); circ(c, bx - 14, by - 34, 18, '#E84A4A', LW * .5); circ(c, bx + 18, by - 30, 14, '#9AD07A', LW * .5)
    night(c, [('pool', 960, 400, 1100, .5)], ambient='#9AA0D0')

def BS_then(c, t):
    lt = t - 249.46; dx, dy = shake(t, 249.46, 1.3, 14); c.translate(dx, dy)
    station(c, t, 0, False, 500)
    r = random.Random(3); k = K(lt, 0, 1.1)
    for i in range(10):
        a = r.uniform(3.3, 6.1); L = r.uniform(150, 520) * k
        c.drawLine(900, 900, 900 + math.cos(a) * L, 900 + math.sin(a) * L * .3 + 30, ink(9, '#FFB45C', 230, boil=False)); c.drawLine(900, 900, 900 + math.cos(a) * L, 900 + math.sin(a) * L * .3 + 30, ink(3, '#FFFFFF', boil=False))
    add_light(c, 900, 900, 500 * k, '#FF9A4A', 160)

def BT_explode(c, t):
    lt = t - 250.66; dx, dy = shake(t, 250.66, 1.4, 44); c.translate(dx, dy)
    station(c, t, ease_out(K(lt, 0, .3)), False, 500)
    rr = random.Random(5)
    for i in range(26):
        vx = rr.uniform(-900, 900); vy = rr.uniform(-1100, -300); x = 900 + vx * lt; y = 900 + vy * lt + 1300 * lt * lt; sz = rr.uniform(20, 60)
        if y < 1300:
            c.save(); c.translate(x, y); c.rotate(lt * rr.uniform(-600, 600)); pp = skia.Path(); pp.moveTo(-sz / 2, -sz / 3); pp.lineTo(sz / 2, -sz / 2); pp.lineTo(sz / 3, sz / 2); pp.lineTo(-sz / 2, sz / 3); pp.close(); shape(c, pp, '#9AA0B0', LW * .8); c.restore()
    fa = max(0, 1 - lt / 3.5)
    for i in range(9):
        a = -3.1 + i / 8 * 3.1; rad = 80 + min(lt, 2) * 320
        puff(c, 900 + math.cos(a) * rad, 860 + math.sin(a) * rad * .5, 80 + lt * 60, 50 + i, '#D9D3E6', '#9E95B8', 255 * fa)
    if lt < .6:
        ring = ease_out(K(lt, 0, .6)); c.drawOval(skia.Rect(900 - 1100 * ring, 900 - 260 * ring, 900 + 1100 * ring, 900 + 260 * ring), ink(20 * (1 - ring) + 2, '#FFF6DC', 255 * (1 - ring), boil=False))
    for i, (x, d) in enumerate(((400, -1), (1450, 1), (250, -1))):
        fly = ease_out(K(lt, 0, .6))
        draw_char(c, x + d * 200 * fly, 1000 - math.sin(min(1, lt / .8) * math.pi) * 120, .7, TEENS[i], face=-.6 * d, eyes='shock', mouth='open', arms=('flail', 'up'), tilt=d * 25 * fly)
    add_light(c, 900, 880, 900 * fa, '#FF9A4A', 220 * fa)

def BU_smoke(c, t):
    lt = t - 254.52
    station(c, t, 1.0, False, 500)
    for i in range(8):
        u = (lt * .25 + i / 8) % 1; x = 900 + (i - 4) * 160 + math.sin(t + i) * 30
        puff(c, x, 880 - u * 400, 120 + u * 80, 70 + i, '#B8B2C8', '#8A84A0', 230 * (1 - u * .7), outline=False)
    eo = ease(K(lt, .8, .6))
    for ex in (-60, 60, -24, 24):
        c.drawOval(skia.Rect(900 + ex - 14, 780 - abs(ex) * .3 - 8 * eo, 900 + ex + 14, 780 - abs(ex) * .3 + 8 * eo), fp('#FF3A3A')); add_light(c, 900 + ex, 780, 80, '#FF3A3A', 200 * eo)

def BV_storm(c, t):
    lt = t - 256.55; dx, dy = shake(t, 257.6, .8, 20); c.translate(dx, dy)
    station(c, t, 1.0, False, 500)
    rear = back(K(lt, 0, 1.2), 1.3)
    c.save(); c.clipRect(skia.Rect(-400, -400, W + 400, 905)); draw_storm(c, 1350, 1180, 1.25, twos(t), rear=rear, open_=ease(K(lt, 1.0, .3)) * (.8 + .2 * math.sin(t * 20))); c.restore()
    station_front_hole(c)
    if 1.05 < lt < 1.6:
        for i in range(3):
            u = ((lt - 1.05) * 3 + i / 3) % 1; c.drawOval(skia.Rect(1000 - 200 - u * 400, 350 - 80 - u * 160, 1000 + 200 + u * 400, 350 + 80 + u * 160), ink(6, '#FFF6DC', 200 * (1 - u), boil=False))
    chip(c, t, 257.2, 'THREAT LEVEL 2', 'STORM', '#F2D36B', y=1010)

def station_front_hole(c):
    p = skia.Path(); p.addOval(skia.Rect(900 - 420, 900 - 90, 900 + 420, 900 + 90)); c.save(); c.clipRect(skia.Rect(-400, 900, W + 400, H + 400))
    c.drawPath(p, fp('#120E18')); c.restore(); c.drawPath(p, ink(LW * 1.2))

def BW_silver(c, t):
    lt = t - 259.63
    blit(c, BG_STATION(), 0, 0, blur=12)
    c.drawRect(skia.Rect(-400, -300, W + 400, H + 300), fp('#0A0C20', 150))
    rect(c, 560, 200, 1360, 880, '#0E1A34', LW * 1.2, 24); c.drawRect(skia.Rect(570, 210, 1350, 870), fp('#4AB0E8', 30))
    for i in range(0, 660, 8): c.drawLine(570, 210 + i, 1350, 210 + i, ink(1.5, '#9FD6FF', 30, boil=False))
    badge(c, 960, 480, .9, 'SILVER')
    label(c, 'REQUIRED: SILVER+', 960, 820, 64, '#FF6A5A' if int(t * 4) % 2 else '#FFF6DC', MARKER, 'center', skew=0)
    add_light(c, 960, 540, 600, '#4AB0E8', 60)

def BX_alarm(c, t):
    lt = t - 261.16
    station(c, t, 1.0, True, 500)
    c.save(); c.clipRect(skia.Rect(-400, -400, W + 400, 905)); draw_storm(c, 1350, 1180, 1.25, twos(t), rear=.85 + .15 * math.sin(t * 3), open_=.5 + .5 * math.sin(t * 7), look=math.sin(t * 2) * .5); c.restore()
    station_front_hole(c)

def BY_run(c, t):
    lt = t - 263.62
    station(c, t, 1.0, True, 500 + lt * 40)
    for i in range(6):
        d = 1 if i % 2 else -1; x = (200 + i * 340 + d * lt * 600) % 2300 - 200; ph = lt * 16 + i
        walker(c, t, x, 980 + (i % 3) * 40, .7 + (i % 3) * .08, TEENS[i % 4], ph, face=.8 * d, run=True, eyes='shock', mouth='open')
    rect(c, 1640, -100, 1740, 1000, '#D8DCE6', LW)
    draw_char(c, 1560, 1020, .55, GIRL, face=-.3, eyes='closed', mouth='open', arms=('heart', 'heart'), bob=abs(math.sin(t * 10)) * 6)
    for i in range(2):
        u = (lt * 2 + i * .5) % 1; c.drawCircle(1560 - 30 + i * 60, 1020 - 230 * .55 * 2 + u * 60, 6, fp('#8FC8EE'))

def BZ_you(c, t):
    lt = t - 267.10
    hero_close(c, t, BG_STATION(), face=.3, eyes='wide' if lt > .5 else 'dot', mouth='o' if lt > .5 else 'flat', arms=(('bag', 'flail', K(lt, .5, .2)), 'bag'), brow=1.0 if lt > .5 else 0, sweat=lt * .8 % 1, pupil=.5, rim='#FF8080')
    if lt > .5:
        dt = lt - .5; x = 300 - dt * 80; y = 1000 + dt * 800 + .5 * 2400 * dt * dt
        c.save(); c.translate(x, min(y, 1300)); c.rotate(dt * 90); rect(c, -90, -60, 90, 160, '#D8B888', LW, 10); c.restore()
        ax = 300 + dt * 500; ay = min(1050, 1000 + dt * 900 + 1200 * dt * dt); circ(c, ax, ay, 30, '#E84A4A', LW * .7)
    c.drawRect(skia.Rect(-400, -300, W + 400, H + 300), fp('#FF2020', 30 * (math.sin(t * 9) * .5 + .5), blend=skia.BlendMode.kPlus))

def CA_phone(c, t):
    lt = t - 269.56
    blit(c, BG_STATION(), 0, 0, blur=16)
    c.drawRect(skia.Rect(-400, -300, W + 400, H + 300), fp('#FF2020', 30 * (math.sin(t * 9) * .5 + .5), blend=skia.BlendMode.kPlus))
    def scr(cc, tt):
        grad_rect(cc, -180, -340, 180, 340, '#1E2236', '#0E1220')
        cc.drawRect(skia.Rect(-180, -340, 180, -240), fp('#2E3A66')); label(cc, 'BUREAU', 0, -275, 50, '#F2C14E', MARKER, 'center', skew=0)
        k = K(tt, 270.0, .3)
        if k > 0:
            cc.save(); cc.translate(0, -60); cc.scale(back(k), back(k)); rect(cc, -150, -110, 150, 110, '#2A3458', LW * .7, 16)
            label(cc, 'SILVER HERO', 0, -40, 40, '#FFF6DC', MARKER, 'center', skew=0); label(cc, 'DISPATCHED', 0, 10, 40, '#B8F04A', MARKER, 'center', skew=0)
            label(cc, 'ETA', 0, 70, 30, '#9AA4B8', KALAM, 'center', skew=0); cc.restore()
            secs = 540 - int(max(0, tt - 271.5)); label(cc, f'{secs // 60}:{secs % 60:02d}', 0, 200, 110, '#FF4A4A', MARKER, 'center', skew=0)
    c.save(); c.translate(960, 560); c.rotate(-4 + math.sin(t * 2) * 1.5)
    phone_ui(c, 0, 0, 1.2, scr, t)
    for sx in (-1, 1): circ(c, sx * 250, 260, 70, HERO['skin'], LW)
    c.restore()

def CB_nine(c, t):
    lt = t - 272.89
    blit(c, BG_STATION(), 0, 0, blur=18)
    c.drawRect(skia.Rect(-400, -300, W + 400, H + 300), fp('#000000', 150))
    beat = abs(math.sin(lt * 4.5)) ** 8
    k = 1 + .05 * beat
    c.save(); c.translate(960, 640); c.scale(k, k); label(c, '9:00', 0, 0, 380, '#FF4A4A', MARKER, 'center', stroke=22, stroke_col='#1A0408', skew=0); c.restore()
    label(c, 'MINUTES', 960, 800, 80, '#FFF6DC', MARKER, 'center', skew=0)

def CB_smash(c, t):
    lt = t - 276.65; hit1, hit2 = 277.2, 279.0
    dx, dy = shake(t, hit1, .5, 30); a, b = shake(t, hit2, .5, 30); c.translate(dx + a, dy + b)
    station(c, t, 1.0, True, 500)
    look = .3 * math.sin(t * 2)
    c.save(); c.clipRect(skia.Rect(-400, -400, W + 400, 905)); draw_storm(c, 1350 + 60 * math.sin(lt * 2), 1180, 1.25, twos(t), rear=.9, open_=.6 + .4 * math.sin(t * 9), look=look); c.restore()
    station_front_hole(c)
    for (ht, x) in ((hit1, 620), (hit2, 1240)):
        if t > ht:
            dt = t - ht; rr = random.Random(int(ht))
            for i in range(14):
                vx = rr.uniform(-500, 500); vy = rr.uniform(-700, -200); px = x + vx * dt; py = 500 + vy * dt + 1300 * dt * dt
                if py < 1200: c.save(); c.translate(px, py); c.rotate(dt * 500 + i * 20); rect(c, -20, -14, 20, 14, '#C8CCD8', LW * .7); c.restore()
            for i in range(4): puff(c, x + (i - 1.5) * 120 * (1 + dt), 520 - dt * 80, 50 + dt * 50, i + int(ht), '#D9D3E6', '#9E95B8', 255 * max(0, 1 - dt / 1.2))
    draw_char(c, 260, 1060, .8, HERO, face=.6, eyes='wide', mouth='flat', arms=('fist', 'fist'), brow=-.4, brow_tilt=-.8, rim='#FF8080')

def CC_turn(c, t):
    lt = t - 280.65
    station(c, t, 1.0, True, 500)
    look = -ease(K(lt, .4, 2.0)) * .9
    c.save(); c.clipRect(skia.Rect(-400, -400, W + 400, 905)); draw_storm(c, 1350, 1180, 1.25, twos(t), rear=.9, open_=.15, look=look); c.restore()
    station_front_hole(c)

def CD_girl(c, t):
    lt = t - 284.27
    blit(c, BG_STATION(), 0, 0, blur=10)
    rect(c, 1100, -100, 1260, 1200, '#D8DCE6', LW * 1.2)
    draw_char(c, 960, 1080, 1.0, GIRL, face=.4, eyes='wide', mouth='open', arms=('heart', 'heart'), sweat=lt % 1, pupil=1, bob=abs(math.sin(t * 14)) * 5)
    c.drawRect(skia.Rect(-400, -300, W + 400, H + 300), fp('#FF2020', 30 * (math.sin(t * 9) * .5 + .5), blend=skia.BlendMode.kPlus))
    c.drawRect(skia.Rect(-400, -300, 700, H + 300), sp(linear(-400, 0, 700, 0, [hx('#000000', 200), hx('#000000', 0)])))

def CE_teeth(c, t):
    lt = t - 285.62
    blit(c, BG_STATION(), 0, 0, blur=16); c.drawRect(skia.Rect(-400, -300, W + 400, H + 300), fp('#14040A', 150))
    draw_storm(c, 1100, 2300, 2.6, twos(t), rear=1.0, open_=ease(K(lt, .3, 1.6)), look=-.2)
    if lt > 1.8:
        r = random.Random(3)
        for i in range(3):
            u = ((lt - 1.8) * 1.2 + i / 3) % 1; c.drawLine(900 + i * 80, 700 + u * 300, 900 + i * 80, 760 + u * 300, ink(10, '#B8E0F0', 200 * (1 - u), boil=False))

def CF_run(c, t):
    lt = t - 288.58; pan = lt * 1600
    station(c, t, 0, True, 1000 + pan)
    hscroll_lines(c, t * 1.5, 0, H, '#FFFFFF', 120, 3600)
    ph = lt * 20
    walker(c, t, 900, 1010, 1.15, HERO, ph, face=.75, run=True, eyes='half', mouth='flat', brow=-.6, brow_tilt=-.9, rim='#FFB46A')
    for i in range(3):
        u = (lt * 3 + i / 3) % 1; puff(c, 900 - 140 - u * 300, 1010 - 20, 30 + u * 30, i + 5, '#D8D4E0', '#A8A2B8', 255 * (1 - u))

def CG_jump(c, t):
    lt = t - 292.11; land = 1.3
    station(c, t, 0, True, 3000)
    rect(c, 1350, -100, 1490, 1200, '#D8DCE6', LW * 1.2)
    draw_char(c, 1300, 1060, .7, GIRL, face=.4, eyes='wide', mouth='open', arms=('heart', 'heart'), bob=abs(math.sin(t * 14)) * 5)
    k = K(lt, 0, land)
    if k < 1:
        x = lerp(200, 1050, ease(k)); y = 1050 - math.sin(k * math.pi) * 380
        draw_char(c, x, y, 1.05, HERO, face=.7, eyes='half', mouth='flat', arms=('up', 'pumpF'), brow=-.6, legs=((-30, -40, 60), (30, 50, 30)), lean=-.15, tilt=-10)
        hscroll_lines(c, t, 300, 900, '#FFFFFF', 80, 2400)
    else:
        sq = .16 * math.sin(K(lt, land, .25) * math.pi)
        draw_char(c, 1050, 1050, 1.05, HERO, face=-.5, eyes='half', mouth='flat', arms=('point', 'fist'), brow=-.6, brow_tilt=-.9, squash=sq, rim='#FFB46A')
        dt = lt - land
        for i in range(4): puff(c, 1050 + (i - 1.5) * 90 * (1 + dt * 2), 1050, 36, i + 30, '#D8D4E0', '#A8A2B8', 255 * max(0, 1 - dt * 1.5))

def CH_claw(c, t):
    lt = t - 294.09; slow = lt * .5
    blit(c, BG_STATION(), 0, 0, blur=10); c.drawRect(skia.Rect(-400, -300, W + 400, H + 300), fp('#14040A', 140))
    up = ease(K(lt, 0, 1.4)); down = ease(K(lt, 1.8, 1.3))
    ang = lerp(0, -50, up) + down * 70
    c.save(); c.translate(1500, -200); c.rotate(ang)
    cl = skia.Path(); cl.moveTo(-70, 0); cl.cubicTo(-90, 400, -40, 700, 60, 900); cl.cubicTo(80, 700, 120, 400, 70, 0); cl.close(); grad_shape(c, cl, '#6FD08A', '#1E5A3E', 0, 900)
    poly(c, [(20, 860), (140, 1060), (60, 880)], '#F3E7C8'); c.restore()
    if 1.8 < lt < 2.6:
        arc = skia.Path(); arc.addArc(skia.Rect(1500 - 900, -200 - 900, 1500 + 900, -200 + 900), 110 - 50 * 0, 50); c.drawPath(arc, ink(160, '#9AE0B0', 90, boil=False))
    draw_char(c, 760, 1400, 2.15, HERO, face=.5, eyes='wide', mouth='flat', arms=('down', 'down'), brow=-.3, shadow=False, rim='#FF8080', pupil=1)
    c.drawRect(skia.Rect(-400, -300, W + 400, H + 300), sp(radial(960, 540, 1100, [hx('#000000', 0), hx('#000000', 140 * down)])))

def CI_cover(c, t):
    lt = t - 297.18
    blit(c, BG_STATION(), 0, 0, blur=10); c.drawRect(skia.Rect(-400, -300, W + 400, H + 300), fp('#14040A', 120))
    sh = ease(K(lt, 0, 4.5))
    c.drawRect(skia.Rect(-400, -300, W + 400, H + 300), sp(linear(1600, -200, 600, 700, [hx('#000000', 200 * sh), hx('#000000', 0)])))
    draw_char(c, 1250, 1100, .8, GIRL, face=-.3, eyes='closed', mouth='open', arms=('heart', 'heart'), shadow=False)
    up = K(lt, 0, .35)
    draw_char(c, 760, 1350, 1.9, HERO, face=.3, eyes='closed', mouth='frown', arms=('down', ('down', 'cover', up)), brow=-.4, squash=.05 * math.sin(K(lt, .3, .25) * math.pi), shadow=False, rim='#FF8080', tilt=-6)

def CJ_shouter(c, t):
    lt = t - 302.14
    blit(c, BG_STATION(), 0, 0, blur=12)
    crowd_heads(c, t, 1150, 1.0, 9, 6, .2, rim='#FF8080')
    draw_char(c, 900, 1350, 1.9, SHOUTER, face=.4, eyes='half', mouth=talk(t) if talk(t) != 'flat' else 'mid', arms=('down', 'point'), brow=-.8, brow_tilt=-1.0, bob=abs(math.sin(twos(t) * 6)) * 8, shadow=False)
    c.drawRect(skia.Rect(-400, -300, W + 400, H + 300), fp('#FF2020', 25 * (math.sin(t * 9) * .5 + .5), blend=skia.BlendMode.kPlus))

def CK_warm(c, t):
    lt = t - 305.00
    grad_rect(c, -400, -300, W + 400, H + 300, '#1A0A10', '#3A1414')
    g = .4 + .6 * ease(K(lt, 0, 1.8))
    x, y = 960, 560
    c.drawLine(1500, 1300, x + 60, y + 80, ink(170, boil=False)); c.drawLine(1500, 1300, x + 60, y + 80, ink(150, HERO['skin'], boil=False))
    c.drawLine(1600, 1400, 1250, 950, ink(190, boil=False)); c.drawLine(1600, 1400, 1250, 950, ink(170, HERO['suit'], boil=False))
    circ(c, x, y, 180, HERO['skin'], LW * 1.4)
    circ(c, x + 150, y + 120, 34, '#1B1A20', LW)
    add_light(c, x, y, 560 * g, '#FF8A3C', 120 * g); c.drawCircle(x, y, 180, fp('#FF7A2A', 50 * g, blend=skia.BlendMode.kPlus)); c.drawCircle(x, y, 188, ink(12, '#FFB45C', 220 * g, boil=False))
    for f in range(4): c.drawLine(x - 110 + f * 70, y - 160, x - 100 + f * 68, y - 70, ink(6, '#C99068', boil=False))
    r = random.Random(int(t * 12) // 2)
    for i in range(int(40 * g)):
        px = r.uniform(700, 1220); py = 520 - ((t * 260 + i * 37) % 560)
        c.drawCircle(px, py, r.uniform(2, 6), fp('#FFB45C', 230))

def CL_notwarm(c, t):
    lt = t - 306.85
    grad_rect(c, -400, -300, W + 400, H + 300, '#1A0A10', '#000000')
    c.save(); c.translate(960, 540); c.scale(3.2, 3.2); c.translate(-960, -600)
    draw_char(c, 960, 1020, 1.0, HERO, face=.15, eyes='half' if lt < .6 else 'wide', mouth='flat', brow=-.6 if lt < .6 else .2, shadow=False, rim='#FF6A2A', arms=('down', 'down'))
    c.restore()
    c.drawRect(skia.Rect(-400, 700, W + 400, H + 300), sp(linear(0, 1100, 0, 500, [hx('#FF5A1A', 200 * ease(K(lt, 0, 2))), hx('#FF5A1A', 0)]), blend=skia.BlendMode.kPlus))

def CM_burn(c, t):
    lt = t - 308.84
    if lt > 1.15:
        c.drawRect(skia.Rect(-400, -300, W + 400, H + 300), fp((0, 0, 0))); return
    dx, dy = shake(t, 308.84, 1.0, 40); c.translate(dx, dy)
    grad_rect(c, -400, -300, W + 400, H + 300, '#3A0A04', '#FF6A1A')
    speed_lines(c, t, 960, 600, '#3A0A04', 170, 80, 300)
    for i in range(14):
        a = i / 14 * 6.28; fx_ = 960 + math.cos(a) * 260; fy_ = 860 + math.sin(a) * 80
        flame(c, fx_, fy_, 2.6 + math.sin(t * 9 + i) * .4, t, i)
    draw_char(c, 960, 1100, 1.2, HERO, face=0, eyes='wide', mouth='flat', arms=('up', 'up'), brow=-.4, rim='#FFE6A0', shadow=False)
    for sx in (-1, 1):
        hx_, hy_ = 960 + sx * 130 * 1.2, 1100 - 470 * 1.2
        flame(c, hx_, hy_ + 40, 3.0, t, sx); add_light(c, hx_, hy_, 500, '#FFC870', 140)
    if lt > .95: c.drawRect(skia.Rect(-400, -300, W + 400, H + 300), fp('#FFFFFF', 255 * K(lt, .95, .1)))

SHOTS_B = [
    (150.88, 154.42, AR_you, None), (154.42, 159.51, AS_mom, None), (159.51, 163.83, AT_shirt, None), (163.83, 169.75, AU_drawing, None),
    (169.75, 173.57, AV_hand, None), (173.57, 177.47, AW_bar, None), (177.47, 178.49, AX_zero, None), (178.49, 180.83, AY_notfive, None),
    (180.83, 182.84, AZ_laugh, None), (182.84, 186.28, BA_never, None), (186.28, 188.45, BB_photo, None), (188.45, 191.55, BC_viral, None),
    (191.55, 195.50, BD_memes, None), (195.50, 203.47, BE_license, None), (203.47, 207.89, BF_list, None), (207.89, 211.11, BG_shrug, None),
    (211.11, 213.79, BH_oldlady, None), (213.79, 215.67, BI_cat, None), (215.67, 217.43, BJ_parking, None), (217.43, 222.84, BK_whispers, None),
    (222.84, 224.35, lambda c, t: BL_taunt(c, t, 0, 222.84), None), (224.35, 226.14, lambda c, t: BL_taunt(c, t, 1, 224.35), None),
    (226.14, 230.85, BM_wave, None), (230.85, 236.13, BN_roof, None), (236.13, 239.02, BO_hands, None), (239.02, 242.55, BO_face, None),
    (242.55, 244.45, BP_anger, None), (244.45, 245.73, BQ_wrong, 'card'), (245.73, 249.46, BR_groceries, None), (249.46, 250.66, BS_then, None),
    (250.66, 254.52, BT_explode, None), (254.52, 256.55, BU_smoke, None), (256.55, 259.63, BV_storm, None), (259.63, 261.16, BW_silver, None),
    (261.16, 263.62, BX_alarm, None), (263.62, 267.10, BY_run, None), (267.10, 269.56, BZ_you, None), (269.56, 272.89, CA_phone, None),
    (272.89, 276.65, CB_nine, None), (276.65, 280.65, CB_smash, None), (280.65, 284.27, CC_turn, None), (284.27, 285.62, CD_girl, None),
    (285.62, 288.58, CE_teeth, None), (288.58, 292.11, CF_run, None), (292.11, 294.09, CG_jump, None), (294.09, 297.18, CH_claw, None),
    (297.18, 302.14, CI_cover, None), (302.14, 305.00, CJ_shouter, None), (305.00, 306.85, CK_warm, None), (306.85, 308.84, CL_notwarm, None),
    (308.84, 310.60, CM_burn, 'card'),
]
IMPACTS = [3.72, 12.74, 43.35, 177.47, 250.66, 308.84]
SEPIA = (154.42, 195.50)
