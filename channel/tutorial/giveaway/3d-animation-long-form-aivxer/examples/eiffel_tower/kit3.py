# 3D Animation Long Form - made by aivxer. Copyright (c) 2026 aivxer.
# Free for your own videos. Do not re-share, sell, or claim this skill as your own (see LICENSE.txt).
"""v3 style kit — flat cel-shaded round-head puppets with one uniform thick ink line,
night-lighting layer (multiply darkness with punched light pools), depth blur, bloom."""
import math, random
import skia
from lib import W, H, FPS, C, hx, radial, linear, ease, ease_out, pop, mouth_track, blink, FONT_HAND

F = "/home/claude/vid/fonts/"
KALAM = skia.Typeface.MakeFromFile(F + "Kalam-Bold.ttf")
PATRICK = skia.Typeface.MakeFromFile(F + "PatrickHand-Regular.ttf")
MARKER = skia.Typeface.MakeFromFile(F + "PermanentMarker-Regular.ttf")
INK = (24, 22, 27)
LW = 6.0


def col(v, a=255):
    return hx(v, a) if isinstance(v, str) else C(v, a)


def fp(v, a=255, blur=0, blend=None):
    p = skia.Paint(AntiAlias=True, Color=col(v, a))
    if blur: p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur))
    if blend: p.setBlendMode(blend)
    return p


def sp(shader, blend=None, blur=0):
    p = skia.Paint(AntiAlias=True); p.setShader(shader)
    if blend: p.setBlendMode(blend)
    if blur: p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur))
    return p


def ink(w=LW, v=INK, a=255):
    p = skia.Paint(AntiAlias=True, Color=col(v, a))
    p.setStyle(skia.Paint.kStroke_Style); p.setStrokeWidth(w)
    p.setStrokeCap(skia.Paint.kRound_Cap); p.setStrokeJoin(skia.Paint.kRound_Join)
    return p


def shape(c, path, fill, w=LW, v=INK):
    c.drawPath(path, fill if isinstance(fill, skia.Paint) else fp(fill))
    if w: c.drawPath(path, ink(w, v))


def rect(c, x0, y0, x1, y1, fill, w=LW, r=0, v=INK):
    p = skia.Path()
    if r: p.addRRect(skia.RRect.MakeRectXY(skia.Rect(x0, y0, x1, y1), r, r))
    else: p.addRect(skia.Rect(x0, y0, x1, y1))
    shape(c, p, fill, w, v); return p


def circ(c, x, y, r, fill, w=LW, v=INK):
    p = skia.Path(); p.addCircle(x, y, r); shape(c, p, fill, w, v); return p


def oval(c, x0, y0, x1, y1, fill, w=LW, v=INK):
    p = skia.Path(); p.addOval(skia.Rect(x0, y0, x1, y1)); shape(c, p, fill, w, v); return p


def line(c, x0, y0, x1, y1, w=LW, v=INK, a=255):
    c.drawLine(x0, y0, x1, y1, ink(w, v, a))


def poly(c, pts, fill, w=LW, v=INK, close=True):
    p = skia.Path(); p.moveTo(*pts[0])
    for q in pts[1:]: p.lineTo(*q)
    if close: p.close()
    shape(c, p, fill, w, v); return p


def label(c, s, x, y, size, color, font=None, align='left', stroke=0, stroke_col=INK, skew=-0.16, alpha=1.0, rot=0.0):
    f = skia.Font(font or KALAM, size); w = f.measureText(s)
    ox = -w / 2 if align == 'center' else -w if align == 'right' else 0
    c.save(); c.translate(x, y); c.rotate(rot); c.skew(skew, 0)
    if stroke:
        c.drawString(s, ox, 0, f, ink(stroke, stroke_col, 255 * alpha))
    c.drawString(s, ox, 0, f, fp(color, 255 * alpha))
    c.restore(); return w


def text_w(s, size, font=None):
    return skia.Font(font or KALAM, size).measureText(s)


def back(u, k=1.9):
    """ease-out with overshoot (snappy pose change)"""
    u = min(max(u, 0.0), 1.0); u -= 1
    return 1 + (k + 1) * u ** 3 + k * u ** 2


def lerp(a, b, k): return a + (b - a) * k


# ---------------------------------------------------------------- lighting
def night(c, lights, ambient='#4A5A9A'):
    """Multiply a navy darkness over everything drawn so far, with soft holes where lights are."""
    p = skia.Paint(); p.setBlendMode(skia.BlendMode.kMultiply)
    c.saveLayer(None, p)
    c.drawPaint(fp(ambient))
    for L in lights:
        if L[0] == 'pool':
            _, x, y, r, a = L
            c.drawCircle(x, y, r, sp(radial(x, y, r, [C((0, 0, 0), 255 * a), C((0, 0, 0), 255 * a * .75), C((0, 0, 0), 0)], [0, .5, 1]),
                                     blend=skia.BlendMode.kDstOut))
        elif L[0] == 'oval':
            _, x, y, rx, ry, a = L
            c.save(); c.translate(x, y); c.scale(1, ry / rx)
            c.drawCircle(0, 0, rx, sp(radial(0, 0, rx, [C((0, 0, 0), 255 * a), C((0, 0, 0), 255 * a * .7), C((0, 0, 0), 0)], [0, .55, 1]),
                                     blend=skia.BlendMode.kDstOut))
            c.restore()
        elif L[0] == 'path':
            _, path, a, blur = L
            c.drawPath(path, fp((0, 0, 0), 255 * a, blur=blur, blend=skia.BlendMode.kDstOut))
    c.restore()


def add_light(c, x, y, r, v, a):
    c.drawCircle(x, y, r, sp(radial(x, y, r, [col(v, a), col(v, a * .4), col(v, 0)], [0, .5, 1]), blend=skia.BlendMode.kPlus))


def cone_path(x, y, top_w, bot_w, length, lean=0):
    p = skia.Path(); p.moveTo(x - top_w / 2, y); p.lineTo(x + top_w / 2, y)
    p.lineTo(x + lean + bot_w / 2, y + length); p.lineTo(x + lean - bot_w / 2, y + length); p.close(); return p


def blur_begin(c, sigma):
    p = skia.Paint(); p.setImageFilter(skia.ImageFilters.Blur(sigma, sigma)); c.saveLayer(None, p)


def vignette(c, strength=0.65, inner=.42):
    c.drawRect(skia.Rect(0, 0, W, H), sp(radial(W / 2, H / 2, W * 0.74,
               [C((0, 0, 0), 0), C((0, 0, 0), 0), C((2, 3, 12), 255 * strength)], [0, inner, 1])))


def _sat(s, contrast, lift):
    lr, lg, lb = 0.2126, 0.7152, 0.0722
    m = [lr * (1 - s) + s, lg * (1 - s), lb * (1 - s), lr * (1 - s), lg * (1 - s) + s, lb * (1 - s), lr * (1 - s), lg * (1 - s), lb * (1 - s) + s]
    out = []
    for r in range(3): out += [m[r * 3 + i] * contrast for i in range(3)] + [0, lift]
    return out + [0, 0, 0, 1, 0]


GRADE_CF = skia.ColorFilters.Matrix(_sat(0.94, 0.97, 0.012))
THRESH_CF = skia.ColorFilters.Matrix([1.7, 0, 0, 0, -0.78, 0, 1.7, 0, 0, -0.78, 0, 0, 1.7, 0, -0.78, 0, 0, 0, 1, 0])


def finish(surf, bloom=0.42, sigma=20):
    c = surf.getCanvas(); img = surf.makeImageSnapshot()
    c.clear(C((0, 0, 0)))
    p = skia.Paint(); p.setColorFilter(GRADE_CF); c.drawImage(img, 0, 0, skia.SamplingOptions(), p)
    if bloom > 0:
        b = skia.Paint(); b.setImageFilter(skia.ImageFilters.Blur(sigma, sigma, skia.TileMode.kClamp, skia.ImageFilters.ColorFilter(THRESH_CF)))
        b.setBlendMode(skia.BlendMode.kScreen); b.setAlphaf(bloom); c.drawImage(img, 0, 0, skia.SamplingOptions(), b)


# ---------------------------------------------------------------- characters
BODY_TOP, BODY_BOT, HEAD_R = -345, -128, 100
HEAD_CY = BODY_TOP - 74
SHOULDER = (-56, BODY_TOP + 54)
ARM = {  # left arm: (elbow, hand, show_hand)
    'down': ((-90, -235), (-96, -168), True),
    'pocket': ((-96, -232), (-70, -176), False),
    'hip': ((-128, -238), (-84, -190), True),
    'present': ((-128, -306), (-208, -338), True),
    'gesture': ((-136, -262), (-152, -352), True),
    'chin': ((-128, -262), (-62, -322), True),
    'hat': ((-140, -400), (-104, -482), True),
    'hold': ((-96, -236), (-44, -214), True),
    'push': ((-120, -270), (-190, -262), True),
}


def _arm(spec):
    if isinstance(spec, str):
        e, h, s = ARM[spec]; return e, h, s
    a, b, k = spec; k = back(k, 1.6)
    ea, ha, sa = ARM[a]; eb, hb, sb = ARM[b]
    return (lerp(ea[0], eb[0], k), lerp(ea[1], eb[1], k)), (lerp(ha[0], hb[0], k), lerp(ha[1], hb[1], k)), (sb if k > .5 else sa)


def draw_char3(c, x, y, s, spec, face=0.0, eyes='dot', mouth='smile', brow=0.0, brow_tilt=0.0, arms=('down', 'down'),
               tilt=0.0, bob=0.0, squash=0.0, sweat=-1.0, light=-1, rim=None, hat=False, legs=None, pupil=0.0, sparkle=0.0):
    """x,y = feet. s=1 -> head radius 100px. light: -1 key from left, +1 from right. face: -1..1 (3/4 turn)."""
    lw = max(5.2, 4.0 / s)
    R = HEAD_R
    c.save(); c.translate(x, y); c.scale(s, s)
    # --- legs (plain ink lines, no feet)
    if legs is None: legs = ((-24, 0, 0), (24, 0, 0))
    for (hx0, fx, lift) in legs:
        c.drawLine(hx0, BODY_BOT - 8, hx0 + fx, -lift, ink(lw))
    c.translate(0, -bob); c.scale(1 + squash * .6, 1 - squash)
    # --- body (pill)
    body = skia.Path(); body.addRRect(skia.RRect.MakeRectXY(skia.Rect(-84, BODY_TOP, 84, BODY_BOT), 66, 72))
    c.drawPath(body, fp(spec['suit']))
    c.save(); c.clipPath(body, doAntiAlias=True)
    sh = skia.Path(body); sh.offset(light * 16, -5)
    c.drawPath(skia.Op(body, sh, skia.PathOp.kDifference_PathOp), fp(spec['suit_d']))
    if spec.get('pants'):
        c.drawRect(skia.Rect(-90, BODY_BOT - 40, 90, BODY_BOT + 4), fp(spec['pants']))
        c.drawLine(-90, BODY_BOT - 40, 90, BODY_BOT - 40, ink(lw * .8))
    # shirt V, collar, tie / bow tie
    v = skia.Path(); v.moveTo(-34, BODY_TOP - 4); v.lineTo(0, BODY_TOP + 96); v.lineTo(34, BODY_TOP - 4); v.close()
    c.drawPath(v, fp(spec['shirt']))
    if spec.get('bowtie'):
        by = BODY_TOP + 40
        bt = skia.Path(); bt.moveTo(0, by); bt.lineTo(-24, by - 14); bt.lineTo(-24, by + 14); bt.close()
        bt.moveTo(0, by); bt.lineTo(24, by - 14); bt.lineTo(24, by + 14); bt.close()
        shape(c, bt, spec['tie'], lw * .75); circ(c, 0, by, 5, spec['tie'], lw * .7)
    else:
        t = skia.Path(); t.moveTo(-9, BODY_TOP + 24); t.lineTo(9, BODY_TOP + 24); t.lineTo(13, BODY_TOP + 82); t.lineTo(0, BODY_TOP + 98); t.lineTo(-13, BODY_TOP + 82); t.close()
        shape(c, t, spec['tie'], lw * .75)
    for sx in (-1, 1):
        lp = skia.Path(); lp.moveTo(sx * 36, BODY_TOP - 2); lp.lineTo(sx * 2, BODY_TOP + 98); lp.lineTo(sx * 2, BODY_BOT)
        c.drawPath(lp, ink(lw * .75))
        c.drawLine(sx * 22, BODY_TOP + 58, sx * 40, BODY_TOP + 44, ink(lw * .6))  # lapel notch
    if spec.get('hanky'):
        poly(c, [(30, BODY_TOP + 96), (52, BODY_TOP + 92), (48, BODY_TOP + 76), (40, BODY_TOP + 86), (33, BODY_TOP + 76)], spec['hanky'], lw * .55)
    c.restore()
    c.drawPath(body, ink(lw))
    # --- arms (ink lines drawn over the body) + small hands
    for side, a in ((-1, arms[0]), (1, arms[1])):
        e, h, show = _arm(a); m = 1 if side < 0 else -1
        sx, sy = SHOULDER[0] * m, SHOULDER[1]
        ex, ey, hx_, hy_ = e[0] * m, e[1], h[0] * m, h[1]
        cx_, cy_ = 1.35 * ex - 0.175 * (sx + hx_), 1.35 * ey - 0.175 * (sy + hy_)
        ap = skia.Path(); ap.moveTo(sx, sy); ap.quadTo(cx_, cy_, hx_, hy_)
        c.drawPath(ap, ink(lw))
        if show: circ(c, hx_, hy_, 13, spec['skin'], lw * .8)
    # --- head
    c.save(); c.translate(0, HEAD_CY); c.rotate(tilt)
    head = skia.Path(); head.addCircle(0, 0, R)
    hair = spec.get('hair')
    if hair == 'bald':  # side tufts sit behind the head
        for sx in (-1, 1):
            tf = skia.Path(); tf.moveTo(sx * 84, -44)
            for i, (px, py) in enumerate(((112, -34), (98, -18), (118, -4), (100, 10), (112, 26), (86, 34))): tf.lineTo(sx * px, py)
            tf.close(); shape(c, tf, spec.get('hair_col', '#8A8A92'), lw * .8)
    c.drawPath(head, fp(spec['skin']))
    c.save(); c.clipPath(head, doAntiAlias=True)
    lit = skia.Path(head); lit.offset(light * 7, -17)
    c.drawPath(skia.Op(head, lit, skia.PathOp.kDifference_PathOp), fp(spec['skin_d']))
    if rim:
        rm = skia.Path(head); rm.offset(-light * 11, 4)
        c.drawPath(skia.Op(head, rm, skia.PathOp.kDifference_PathOp), fp(rim, 215))
    c.restore()
    if hair == 'slick':
        o = skia.Rect(-R - 4, -R - 5, R + 4, R + 3)
        hp = skia.Path(); hp.moveTo(-R - 4, -4); hp.arcTo(o, 181, 178, False)
        fs = face * 14
        hp.cubicTo(R - 6, -40, 56 + fs, -70, 4 + fs, -62); hp.cubicTo(-36 + fs, -58, -78, -44, -R - 4, -4); hp.close()
        shape(c, hp, spec.get('hair_col', '#1C1B22'), lw)
        shn = skia.Path(); shn.addArc(skia.Rect(-R + 20, -R + 14, R - 20, R - 14), 208 if light < 0 else 282, 50)
        c.drawPath(shn, ink(lw * 1.3, (92, 96, 122)))
        c.drawLine(-30 + fs, -98, -18 + fs, -62, ink(lw * .6, (70, 72, 92)))
    c.drawPath(head, ink(lw))
    if hair == 'slick':  # redraw hair outline edge over the head line for a clean silhouette
        pass
    if hat:
        crown = skia.Path(); crown.moveTo(-R + 6, -56); crown.cubicTo(-R - 2, -R - 82, R + 2, -R - 82, R - 6, -56); crown.close()
        shape(c, crown, spec.get('hat_col', '#2E2E38'), lw)
        c.save(); c.clipPath(crown, doAntiAlias=True)
        c.drawRect(skia.Rect(-R, -86, R, -56), fp(spec.get('hat_band', '#7E1C24')))
        c.drawLine(-R, -86, R, -86, ink(lw * .7))
        hs = skia.Path(crown); hs.offset(light * 14, -6); c.drawPath(skia.Op(crown, hs, skia.PathOp.kDifference_PathOp), fp((0, 0, 0), 70))
        c.restore(); c.drawPath(crown, ink(lw))
        oval(c, -R - 40, -70, R + 40, -40, spec.get('hat_col', '#2E2E38'), lw)
    # --- face
    fx = face * 40
    eyy = -6
    for i, ex0 in enumerate((-30, 30)):
        ex = ex0 + fx
        far = (face > 0 and ex0 > 0) or (face < 0 and ex0 < 0)
        sq = 1 - 0.3 * abs(face) if far else 1.0
        if eyes == 'wide':
            oval(c, ex - 17 * sq, eyy - 17, ex + 17 * sq, eyy + 17, '#FBFBF7', lw * .7)
            c.drawOval(skia.Rect(ex - 5.5 * sq + pupil * 6, eyy - 5.5, ex + 5.5 * sq + pupil * 6, eyy + 5.5), fp(INK))
        elif eyes == 'closed':
            e = skia.Path(); e.moveTo(ex - 11 * sq, eyy); e.quadTo(ex, eyy + 9, ex + 11 * sq, eyy); c.drawPath(e, ink(lw * .8))
        elif eyes == 'half':
            c.save(); c.clipRect(skia.Rect(ex - 20, eyy - 3, ex + 20, eyy + 20))
            c.drawOval(skia.Rect(ex - 6.5 * sq, eyy - 9, ex + 6.5 * sq, eyy + 9), fp(INK)); c.restore()
            c.drawLine(ex - 13 * sq, eyy - 4, ex + 13 * sq, eyy - 4, ink(lw * .8))
        else:
            c.drawOval(skia.Rect(ex - 5.5 * sq, eyy - 8, ex + 5.5 * sq, eyy + 8), fp(INK))
            c.drawCircle(ex + 1.5, eyy - 3, 1.8, fp((255, 255, 255), 220))
        inner = 1 if ex0 < 0 else -1  # direction toward nose
        by = eyy - 29 - brow * 9
        c.drawLine(ex - 13 * sq, by + (brow_tilt * 7 if inner < 0 else -brow_tilt * 7) * 1.0,
                   ex + 13 * sq, by + (brow_tilt * 7 if inner > 0 else -brow_tilt * 7), ink(lw * .78))
    if spec.get('glasses'):
        for ex0 in (-30, 30):
            ex = ex0 + fx; far = (face > 0 and ex0 > 0) or (face < 0 and ex0 < 0); sq = 1 - 0.3 * abs(face) if far else 1.0
            g = skia.Path(); g.addOval(skia.Rect(ex - 24 * sq, eyy - 24, ex + 24 * sq, eyy + 24))
            c.drawPath(g, fp((225, 240, 255), 55)); c.drawPath(g, ink(lw * .7))
        c.drawLine(fx - 7, eyy - 3, fx + 7, eyy - 3, ink(lw * .7))
    mx, my = face * 34, 42
    if spec.get('moustache'):
        mu = skia.Path(); mu.moveTo(mx, my - 20)
        mu.cubicTo(mx - 12, my - 28, mx - 30, my - 22, mx - 40, my - 30); mu.cubicTo(mx - 30, my - 10, mx - 12, my - 12, mx, my - 15)
        mu.cubicTo(mx + 12, my - 12, mx + 30, my - 10, mx + 40, my - 30); mu.cubicTo(mx + 30, my - 22, mx + 12, my - 28, mx, my - 20); mu.close()
        c.drawPath(mu, fp(spec.get('hair_col', '#1C1B22')))
    if mouth == 'smile':
        m = skia.Path(); m.moveTo(mx - 17, my - 2); m.quadTo(mx, my + 13, mx + 17, my - 2); c.drawPath(m, ink(lw * .8))
    elif mouth == 'smirk':
        d = 1 if face >= 0 else -1
        m = skia.Path(); m.moveTo(mx - 15 * d, my + 3); m.quadTo(mx + 4 * d, my + 12, mx + 20 * d, my - 6); c.drawPath(m, ink(lw * .8))
    elif mouth == 'flat':
        c.drawLine(mx - 12, my + 2, mx + 12, my + 2, ink(lw * .8))
    elif mouth == 'o':
        oval(c, mx - 8, my - 9, mx + 8, my + 11, '#5A1A1E', lw * .7)
    elif mouth == 'mid':
        oval(c, mx - 12, my - 4, mx + 12, my + 10, '#5A1A1E', lw * .7)
    elif mouth == 'open':
        mp = skia.Path(); mp.moveTo(mx - 20, my - 5); mp.lineTo(mx + 20, my - 5); mp.cubicTo(mx + 19, my + 24, mx - 19, my + 24, mx - 20, my - 5); mp.close()
        c.drawPath(mp, fp('#5A1A1E'))
        c.save(); c.clipPath(mp, doAntiAlias=True)
        c.drawRect(skia.Rect(mx - 22, my - 6, mx + 22, my + 2), fp('#FAFAF4'))
        c.drawOval(skia.Rect(mx - 11, my + 9, mx + 11, my + 26), fp('#D05860')); c.restore()
        c.drawPath(mp, ink(lw * .7))
    if sparkle > 0:
        k = pop(sparkle) * (1 if sparkle < 1 else max(0, 2 - sparkle))
        sx_, sy_ = mx + 26 * (1 if face >= 0 else -1), my - 8
        st = skia.Path()
        for i in range(8):
            r_ = (20 if i % 2 == 0 else 5) * k; a = i * math.pi / 4
            (st.moveTo if i == 0 else st.lineTo)(sx_ + r_ * math.cos(a), sy_ + r_ * math.sin(a))
        st.close(); c.drawPath(st, fp('#FFFFFF')); c.drawCircle(sx_, sy_, 26 * k, fp((255, 255, 255), 70, blur=8))
    if sweat >= 0:
        sd = -1 if face > 0 else 1
        sx0, sy0 = sd * 62, -66 + 30 * (sweat % 1.0)
        d = skia.Path(); d.moveTo(sx0, sy0 - 19); d.cubicTo(sx0 + 12, sy0 - 3, sx0 + 11, sy0 + 10, sx0, sy0 + 10); d.cubicTo(sx0 - 11, sy0 + 10, sx0 - 12, sy0 - 3, sx0, sy0 - 19); d.close()
        shape(c, d, '#8FC8EE', lw * .7)
    c.restore()
    c.restore()


def walk_legs(phase, stride=46, lift=20):
    a = math.sin(phase); b = -a
    return ((-10, a * stride, max(0, math.cos(phase)) * lift), (10, b * stride, max(0, -math.cos(phase)) * lift))


LUSTIG = dict(skin='#E6BE8E', skin_d='#C99F70', suit='#3B4660', suit_d='#2B3348', shirt='#F4EFE2', tie='#A8232B',
              hair='slick', hair_col='#1C1B22', moustache=True, hanky='#F4EFE2')
BUYER = dict(skin='#EBC79C', skin_d='#CFA677', suit='#7A5A3C', suit_d='#5E432B', shirt='#F4EFE2', tie='#2F6B4E',
             bowtie=True, hair='bald', hair_col='#8E8E96', glasses=True)
