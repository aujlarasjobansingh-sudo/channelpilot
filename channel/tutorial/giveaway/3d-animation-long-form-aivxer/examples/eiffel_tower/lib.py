# 3D Animation Long Form - made by aivxer. Copyright (c) 2026 aivxer.
# Free for your own videos. Do not re-share, sell, or claim this skill as your own (see LICENSE.txt).
"""Drawing kit: original round-head puppet characters, lights, text — skia-python."""
import math, json, random
import numpy as np, skia, soundfile as sf

W, H, FPS = 1920, 1080, 30
FONT_HAND = skia.Typeface.MakeFromFile("/home/claude/vid/fonts/CaveatBrush-Regular.ttf")
FONT_LABEL = skia.Typeface.MakeFromFile("/home/claude/vid/fonts/Bangers-Regular.ttf")
OL = (20, 16, 26)
GOLD = (255, 196, 61)
RED = (214, 32, 39)


def C(rgb, a=255):
    return skia.Color(int(rgb[0]), int(rgb[1]), int(rgb[2]), int(a))


def hx(h, a=255):
    h = h.lstrip('#'); return C((int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)), a)


def P(color=None, stroke=0, aa=True, blend=None, blur=0, shader=None, alpha=None):
    p = skia.Paint(AntiAlias=aa)
    if color is not None: p.setColor(color)
    if shader is not None: p.setShader(shader)
    if stroke:
        p.setStyle(skia.Paint.kStroke_Style); p.setStrokeWidth(stroke)
        p.setStrokeCap(skia.Paint.kRound_Cap); p.setStrokeJoin(skia.Paint.kRound_Join)
    if blend: p.setBlendMode(blend)
    if blur: p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur))
    if alpha is not None: p.setAlphaf(alpha)
    return p


def fill_outline(c, path, fill, width=6, ol=OL):
    c.drawPath(path, fill if isinstance(fill, skia.Paint) else P(fill))
    c.drawPath(path, P(C(ol), stroke=width))


def radial(cx, cy, r, colors, pos=None):
    return skia.GradientShader.MakeRadial(center=(cx, cy), radius=r, colors=colors, positions=pos)


def linear(x0, y0, x1, y1, colors, pos=None):
    return skia.GradientShader.MakeLinear(points=[(x0, y0), (x1, y1)], colors=colors, positions=pos)


def light_pool(c, x, y, r, rgb, a=120):
    c.drawCircle(x, y, r, P(shader=radial(x, y, r, [C(rgb, a), C(rgb, a * 0.35), C(rgb, 0)], [0, .45, 1]),
                             blend=skia.BlendMode.kPlus))


def glow_circle(c, x, y, r, rgb, a=255, spread=3.0):
    c.drawCircle(x, y, r * spread, P(shader=radial(x, y, r * spread, [C(rgb, a * .55), C(rgb, 0)]), blend=skia.BlendMode.kPlus))
    c.drawCircle(x, y, r, P(C(rgb, a)))


def cone(c, x, y, top_w, bot_w, length, rgb, a=90):
    p = skia.Path(); p.moveTo(x - top_w / 2, y); p.lineTo(x + top_w / 2, y)
    p.lineTo(x + bot_w / 2, y + length); p.lineTo(x - bot_w / 2, y + length); p.close()
    c.drawPath(p, P(shader=linear(x, y, x, y + length, [C(rgb, a), C(rgb, a * .4), C(rgb, 0)], [0, .6, 1]),
                    blend=skia.BlendMode.kPlus, blur=18))


def vignette(c, strength=0.7):
    c.drawRect(skia.Rect(0, 0, W, H), P(shader=radial(W / 2, H / 2, W * 0.72,
               [C((0, 0, 0), 0), C((0, 0, 0), 0), C((0, 0, 0), 255 * strength)], [0, .45, 1])))


def text(c, s, x, y, size, color, font=None, align='left', stroke=0, stroke_color=OL, alpha=1.0, skew=0):
    f = skia.Font(font or FONT_LABEL, size)
    w = f.measureText(s)
    if align == 'center': x -= w / 2
    elif align == 'right': x -= w
    if skew:
        c.save(); c.skew(skew, 0)
    if stroke:
        c.drawString(s, x, y, f, P(C(stroke_color, 255 * alpha), stroke=stroke))
    c.drawString(s, x, y, f, P(C(color, 255 * alpha)))
    if skew: c.restore()
    return w


def ease(u):
    u = min(max(u, 0), 1); return 0.5 - 0.5 * math.cos(math.pi * u)


def ease_out(u):
    u = min(max(u, 0), 1); return 1 - (1 - u) ** 3


def pop(u):
    """scale pop-in with overshoot: 0 -> 1.15 -> 1 over u in [0,1]"""
    if u <= 0: return 0.0
    if u >= 1: return 1.0
    if u < 0.6: return 1.15 * ease_out(u / 0.6)
    return 1.15 - 0.15 * ease((u - 0.6) / 0.4)


# ---------------- lip sync from audio ----------------
def mouth_track(wav, hold=3):
    s, sr = sf.read(wav)
    if s.ndim > 1: s = s.mean(1)
    hop = sr // FPS; n = len(s) // hop + 1
    rms = np.array([np.sqrt(np.mean(s[i * hop:(i + 1) * hop] ** 2) + 1e-12) for i in range(n)])
    m = rms.max(); out = []; cur = 'closed'; held = hold
    for v in rms:
        tgt = 'open' if v > .45 * m else 'mid' if v > .14 * m else 'closed'
        if tgt != cur and held >= hold: cur = tgt; held = 0
        held += 1; out.append(cur)
    out[-1] = 'closed'
    return out


# ---------------- characters ----------------
LUSTIG = dict(skin='#E9B48A', skin_dark='#B9805C', suit='#3B3F52', suit_hi='#555B73', shirt='#F3EEDF',
              tie='#B0182A', hair='lustig', moustache=True, glasses=False, hat=False)
BUYER = dict(skin='#EBB993', skin_dark='#BF8763', suit='#6B4A2E', suit_hi='#86603D', shirt='#F1E9D8',
             tie='#2E5C8A', bowtie=True, hair='bald', moustache=False, glasses=True, hat=False)


def draw_char(c, x, y, s, spec, mouth='closed', eyes='open', brow=0.0, arms=('down', 'down'), tilt=0.0,
              bob=0.0, sweat=0.0, rim=None, smile=True):
    """x,y = feet centre. s = scale (1 => ~460px tall). arms: 'down','gesture','up','present','hip'"""
    c.save(); c.translate(x, y - bob); c.scale(s, s)
    ol = 6.5
    # legs
    for dx in (-30, 30):
        c.drawLine(dx, -70, dx + (4 if dx > 0 else -4), 0, P(C(OL), stroke=9))
        sh = skia.Path(); sh.addOval(skia.Rect(dx - 22 + (6 if dx > 0 else -6), -14, dx + 22 + (6 if dx > 0 else -6), 6))
        fill_outline(c, sh, P(hx('#1A1620')), 4)
    # body (bean)
    body = skia.Path()
    body.moveTo(-70, -60); body.cubicTo(-92, -150, -78, -245, -40, -262)
    body.lineTo(40, -262); body.cubicTo(78, -245, 92, -150, 70, -60)
    body.cubicTo(40, -48, -40, -48, -70, -60); body.close()
    c.drawPath(body, P(shader=linear(-80, -260, 80, -60, [hx(spec['suit_hi']), hx(spec['suit'])])))
    # shirt V + tie
    v = skia.Path(); v.moveTo(-30, -262); v.lineTo(0, -185); v.lineTo(30, -262); v.close()
    c.drawPath(v, P(hx(spec['shirt'])))
    if spec.get('bowtie'):
        bt = skia.Path(); bt.moveTo(0, -245); bt.lineTo(-24, -258); bt.lineTo(-24, -232); bt.close()
        bt.moveTo(0, -245); bt.lineTo(24, -258); bt.lineTo(24, -232); bt.close()
        fill_outline(c, bt, hx(spec['tie']), 4)
    else:
        t = skia.Path(); t.moveTo(-9, -255); t.lineTo(9, -255); t.lineTo(13, -200); t.lineTo(0, -186); t.lineTo(-13, -200); t.close()
        fill_outline(c, t, hx(spec['tie']), 4)
    c.drawLine(-30, -262, 0, -185, P(C(OL), stroke=4)); c.drawLine(30, -262, 0, -185, P(C(OL), stroke=4))
    # body highlight arc
    hl = skia.Path(); hl.addArc(skia.Rect(-62, -250, 40, -80), 190, 70)
    c.drawPath(hl, P(C((255, 255, 255), 40), stroke=10))
    c.drawPath(body, P(C(OL), stroke=ol))
    # arms (rubber hose single line)
    poses = {'down': ((-74, -210), (-96, -150), (-88, -95)),
             'gesture': ((-74, -210), (-140, -200), (-165, -260)),
             'present': ((-74, -210), (-150, -190), (-210, -205)),
             'up': ((-74, -210), (-120, -280), (-110, -340)),
             'hip': ((-74, -210), (-125, -170), (-80, -130)),
             'chin': ((-74, -210), (-40, -170), (-20, -250))}
    for side, pose in ((-1, arms[0]), (1, arms[1])):
        (sx, sy), (cx_, cy_), (hx_, hy_) = poses[pose]
        a = skia.Path(); a.moveTo(sx * -side, sy); a.quadTo(cx_ * -side, cy_, hx_ * -side, hy_)
        # sign: poses defined for left side (negative x) -> mirror for right
        c.drawPath(a, P(C(OL), stroke=9))
        hand = skia.Path(); hand.addCircle(hx_ * -side, hy_, 15)
        fill_outline(c, hand, hx(spec['skin']), 4.5)
    # head
    c.save(); c.translate(0, -262); c.rotate(tilt); c.translate(0, -88)
    R = 96
    head = skia.Path(); head.addCircle(0, 0, R)
    c.drawPath(head, P(shader=radial(-30, -35, R * 1.35, [hx(spec['skin']), hx(spec['skin']), hx(spec['skin_dark'])], [0, .45, 1])))
    if rim:
        rp = skia.Path(); rp.addArc(skia.Rect(-R + 6, -R + 6, R - 6, R - 6), -60 if rim[0] > 0 else 150, 90)
        c.drawPath(rp, P(C(rim[1], 150), stroke=10, blur=4))
    c.drawPath(head, P(C(OL), stroke=ol))
    # hair
    hair = spec['hair']
    if hair == 'lustig':
        hp = skia.Path(); hp.moveTo(-R - 2, -5); hp.cubicTo(-R - 8, -R - 20, R + 8, -R - 25, R + 2, -10)
        hp.cubicTo(R - 20, -48, 30, -62, -10, -58); hp.cubicTo(-50, -55, -80, -40, -R - 2, -5); hp.close()
        fill_outline(c, hp, hx('#17151C'), 5)
        c.drawLine(-12, -86, 10, -60, P(C((255, 255, 255), 0), stroke=1))
        sh = skia.Path(); sh.addArc(skia.Rect(-60, -92, 50, -40), 200, 60); c.drawPath(sh, P(C((150, 160, 200), 160), stroke=6))
        c.drawLine(-15, -92, -5, -60, P(C((60, 60, 80)), stroke=3))  # side part
    elif hair == 'bald':
        for sx in (-1, 1):
            tf = skia.Path(); tf.moveTo(sx * 88, -10); tf.quadTo(sx * 112, 0, sx * 96, 30); tf.quadTo(sx * 106, 5, sx * 88, -10); tf.close()
            fill_outline(c, tf, hx('#6E4A30'), 4)
        c.drawCircle(-30, -55, 22, P(C((255, 255, 255), 60), blur=6))
    if spec.get('hat'):
        brim = skia.Path(); brim.addOval(skia.Rect(-R - 40, -R + 10, R + 40, -R + 45))
        crown = skia.Path(); crown.moveTo(-R + 15, -R + 28); crown.cubicTo(-R + 5, -R - 70, R - 5, -R - 70, R - 15, -R + 28); crown.close()
        fill_outline(c, crown, hx('#3A3A45'), 5)
        c.drawRect(skia.Rect(-R + 12, -R + 2, R - 12, -R + 24), P(hx('#151318')))
        fill_outline(c, brim, hx('#2C2C36'), 5)
        c.drawPath(crown, P(C(OL), stroke=5))
    # eyes
    ey = -8
    for ex in (-34, 34):
        if eyes == 'closed':
            e = skia.Path(); e.addArc(skia.Rect(ex - 14, ey - 8, ex + 14, ey + 12), 200, 140); c.drawPath(e, P(C(OL), stroke=5))
        elif eyes == 'smug':
            c.drawCircle(ex, ey + 3, 9, P(C(OL)))
            c.drawLine(ex - 15, ey - 4, ex + 15, ey - 2, P(C(OL), stroke=5))
        elif eyes == 'wide':
            c.drawCircle(ex, ey, 15, P(C((255, 255, 255)))); c.drawCircle(ex, ey, 15, P(C(OL), stroke=4)); c.drawCircle(ex, ey + 1, 7, P(C(OL)))
        else:
            c.drawCircle(ex, ey, 10, P(C(OL)))
            c.drawCircle(ex + 3, ey - 3, 3, P(C((255, 255, 255))))
    # brows
    for ex, sgn in ((-34, -1), (34, 1)):
        by = ey - 30 - (brow * 12 if sgn > 0 else brow * 4)
        c.drawLine(ex - 16, by + sgn * brow * -4 + 3, ex + 16, by - 3 + sgn * brow * 4, P(C(OL), stroke=6))
    if spec.get('glasses'):
        for ex in (-34, 34):
            c.drawCircle(ex, ey, 25, P(C((200, 230, 255), 50))); c.drawCircle(ex, ey, 25, P(C(OL), stroke=4.5))
        c.drawLine(-9, ey, 9, ey, P(C(OL), stroke=4))
    # mouth
    my = 40
    if mouth == 'closed':
        m = skia.Path()
        if smile: m.addArc(skia.Rect(-26, my - 26, 26, my + 6), 25, 130)
        else: m.moveTo(-18, my); m.lineTo(18, my)
        c.drawPath(m, P(C(OL), stroke=5.5))
    else:
        w, h = (22, 12) if mouth == 'mid' else (30, 24)
        if mouth == 'o': w, h = 14, 16
        mp = skia.Path(); mp.addOval(skia.Rect(-w, my - h * .6, w, my + h))
        c.drawPath(mp, P(hx('#4A1418')))
        if mouth == 'open':
            tg = skia.Path(); tg.addOval(skia.Rect(-14, my + h * .35, 14, my + h + 2)); c.save(); c.clipPath(mp, doAntiAlias=True); c.drawPath(tg, P(hx('#D9545C'))); c.restore()
        c.drawPath(mp, P(C(OL), stroke=4.5))
    if spec.get('moustache'):
        mu = skia.Path(); mu.moveTo(0, my - 14)
        mu.cubicTo(-14, my - 24, -38, my - 18, -48, my - 26); mu.cubicTo(-36, my - 8, -14, my - 8, 0, my - 12)
        mu.cubicTo(14, my - 8, 36, my - 8, 48, my - 26); mu.cubicTo(38, my - 18, 14, my - 24, 0, my - 14); mu.close()
        c.drawPath(mu, P(hx('#17151C')))
    # cheeks
    for ex in (-58, 58): c.drawCircle(ex, 22, 14, P(C((230, 90, 90), 55), blur=5))
    if sweat > 0:
        d = skia.Path(); sx0, sy0 = 78, -40 + 30 * sweat
        d.moveTo(sx0, sy0 - 22); d.cubicTo(sx0 + 12, sy0 - 4, sx0 + 12, sy0 + 10, sx0, sy0 + 10); d.cubicTo(sx0 - 12, sy0 + 10, sx0 - 12, sy0 - 4, sx0, sy0 - 22); d.close()
        fill_outline(c, d, hx('#9FD6FF'), 3.5)
    c.restore()
    c.restore()


def blink(t, period=2.7, phase=0.0):
    return ((t + phase) % period) < 0.1
