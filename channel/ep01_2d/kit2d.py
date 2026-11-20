# 2D ink-line kit for "In This World" (style adapted from the aivxer 2D long-form skill; original characters)
import math, os
import numpy as np, skia

W, H, FPS = 1920, 1080, 24
FD = os.path.expanduser("~/vid/fonts/")
FONT_HAND = skia.Typeface.MakeFromFile(FD + "CaveatBrush-Regular.ttf")
KALAM = skia.Typeface.MakeFromFile(FD + "Kalam-Bold.ttf")
MARKER = skia.Typeface.MakeFromFile(FD + "PermanentMarker-Regular.ttf")
INK = (24, 22, 27); LW = 6.0
GOLD = '#F2C14E'; RED = '#C8242C'; LIME = '#B8F04A'; CREAM = '#FFF6DC'

# ---- hand-drawn "line boil": outlines jitter slightly, new drawing every 3 frames
BOIL = {'seed': 0, 'on': True}
def set_boil(t): BOIL['seed'] = int(t * FPS) // 3
def twos(t): return math.floor(t * 12) / 12.0   # character animation held on twos (12 drawings/s)

def C(rgb, a=255): return skia.Color(int(rgb[0]), int(rgb[1]), int(rgb[2]), int(max(0, min(255, a))))
def hx(h, a=255):
    h = h.lstrip('#'); return C((int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)), a)
def col(v, a=255): return hx(v, a) if isinstance(v, str) else C(v, a)
def radial(cx, cy, r, colors, pos=None): return skia.GradientShader.MakeRadial(center=(cx, cy), radius=max(r, 1), colors=colors, positions=pos)
def linear(x0, y0, x1, y1, colors, pos=None): return skia.GradientShader.MakeLinear(points=[(x0, y0), (x1, y1)], colors=colors, positions=pos)
def ease(u): u = min(max(u, 0), 1); return 0.5 - 0.5 * math.cos(math.pi * u)
def ease_out(u): u = min(max(u, 0), 1); return 1 - (1 - u) ** 3
def pop(u):
    if u <= 0: return 0.0
    if u >= 1: return 1.0
    return 1.15 * ease_out(u / 0.6) if u < 0.6 else 1.15 - 0.15 * ease((u - 0.6) / 0.4)
def back(u, k=1.9):
    u = min(max(u, 0.0), 1.0) - 1; return 1 + (k + 1) * u ** 3 + k * u ** 2
def lerp(a, b, k): return a + (b - a) * k
def K(t, t0, d): return min(max((t - t0) / d, 0.0), 1.0)
def blink(t, period=2.3, phase=0.0): return ((t + phase) % period) < 0.09

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
def ink(w=LW, v=INK, a=255, boil=True):
    p = skia.Paint(AntiAlias=True, Color=col(v, a)); p.setStyle(skia.Paint.kStroke_Style); p.setStrokeWidth(w)
    p.setStrokeCap(skia.Paint.kRound_Cap); p.setStrokeJoin(skia.Paint.kRound_Join)
    if boil and BOIL['on']: p.setPathEffect(skia.DiscretePathEffect.Make(14, 1.1, BOIL['seed']))
    return p
def shape(c, path, fill, w=LW, v=INK):
    c.drawPath(path, fill if isinstance(fill, skia.Paint) else fp(fill))
    if w:
        b = path.getBounds(); big = max(b.width(), b.height()) > 90   # small shapes stay clean (no polygon look)
        c.drawPath(path, ink(w, v, boil=big))
def rect(c, x0, y0, x1, y1, fill, w=LW, r=0, v=INK):
    p = skia.Path()
    if r: p.addRRect(skia.RRect.MakeRectXY(skia.Rect(x0, y0, x1, y1), r, r))
    else: p.addRect(skia.Rect(x0, y0, x1, y1))
    shape(c, p, fill, w, v); return p
def circ(c, x, y, r, fill, w=LW, v=INK): p = skia.Path(); p.addCircle(x, y, r); shape(c, p, fill, w, v); return p
def oval(c, x0, y0, x1, y1, fill, w=LW, v=INK): p = skia.Path(); p.addOval(skia.Rect(x0, y0, x1, y1)); shape(c, p, fill, w, v); return p
def line(c, x0, y0, x1, y1, w=LW, v=INK, a=255): c.drawLine(x0, y0, x1, y1, ink(w, v, a))
def poly(c, pts, fill, w=LW, v=INK):
    p = skia.Path(); p.moveTo(*pts[0])
    for q in pts[1:]: p.lineTo(*q)
    p.close(); shape(c, p, fill, w, v); return p
def label(c, s, x, y, size, color, font=None, align='left', stroke=0, stroke_col=INK, skew=-0.12, alpha=1.0, rot=0.0):
    f = skia.Font(font or KALAM, size); w = f.measureText(s)
    ox = -w / 2 if align == 'center' else -w if align == 'right' else 0
    c.save(); c.translate(x, y); c.rotate(rot); c.skew(skew, 0)
    if stroke: c.drawString(s, ox, 0, f, ink(stroke, stroke_col, 255 * alpha, boil=False))
    c.drawString(s, ox, 0, f, fp(color, 255 * alpha)); c.restore(); return w

# ---------------- lighting
def night(c, lights, ambient='#4C5CA0'):
    p = skia.Paint(); p.setBlendMode(skia.BlendMode.kMultiply); c.saveLayer(None, p); c.drawPaint(fp(ambient))
    for L in lights:
        if L[0] == 'pool':
            _, x, y, r, a = L
            c.drawCircle(x, y, r, sp(radial(x, y, r, [C((0,0,0), 255*a), C((0,0,0), 255*a*.75), C((0,0,0), 0)], [0, .5, 1]), blend=skia.BlendMode.kDstOut))
        elif L[0] == 'oval':
            _, x, y, rx, ry, a = L; c.save(); c.translate(x, y); c.scale(1, ry / rx)
            c.drawCircle(0, 0, rx, sp(radial(0, 0, rx, [C((0,0,0), 255*a), C((0,0,0), 255*a*.7), C((0,0,0), 0)], [0, .55, 1]), blend=skia.BlendMode.kDstOut)); c.restore()
        else:
            _, path, a, blur = L; c.drawPath(path, fp((0, 0, 0), 255 * a, blur=blur, blend=skia.BlendMode.kDstOut))
    c.restore()
def add_light(c, x, y, r, v, a):
    c.drawCircle(x, y, r, sp(radial(x, y, r, [col(v, a), col(v, a * .4), col(v, 0)], [0, .5, 1]), blend=skia.BlendMode.kPlus))
def cone_path(x, y, top_w, bot_w, length, lean=0):
    p = skia.Path(); p.moveTo(x - top_w/2, y); p.lineTo(x + top_w/2, y); p.lineTo(x + lean + bot_w/2, y + length); p.lineTo(x + lean - bot_w/2, y + length); p.close(); return p
def blur_begin(c, sigma):
    p = skia.Paint(); p.setImageFilter(skia.ImageFilters.Blur(sigma, sigma)); c.saveLayer(None, p)
def vignette(c, strength=0.6, inner=.42):
    c.drawRect(skia.Rect(0, 0, W, H), sp(radial(W/2, H/2, W*.74, [C((0,0,0), 0), C((0,0,0), 0), C((2,3,12), 255*strength)], [0, inner, 1])))
def _sat(s, contrast, lift):
    lr, lg, lb = 0.2126, 0.7152, 0.0722
    m = [lr*(1-s)+s, lg*(1-s), lb*(1-s), lr*(1-s), lg*(1-s)+s, lb*(1-s), lr*(1-s), lg*(1-s), lb*(1-s)+s]
    out = []
    for r in range(3): out += [m[r*3+i] * contrast for i in range(3)] + [0, lift]
    return out + [0, 0, 0, 1, 0]
GRADE_CF = skia.ColorFilters.Matrix(_sat(1.02, 0.98, 0.012))
THRESH_CF = skia.ColorFilters.Matrix([1.7,0,0,0,-0.78, 0,1.7,0,0,-0.78, 0,0,1.7,0,-0.78, 0,0,0,1,0])
_rng = np.random.default_rng(7); GRAIN = []
for _ in range(4):
    g = (_rng.normal(128, 40, (H // 2, W // 2))).clip(0, 255).astype(np.uint8)
    GRAIN.append(skia.Image.fromarray(np.dstack([g, g, g, np.full_like(g, 255)]), colorType=skia.kRGBA_8888_ColorType))
def grain(c, t, a=0.07):
    p = skia.Paint(); p.setBlendMode(skia.BlendMode.kOverlay); p.setAlphaf(a)
    c.drawImageRect(GRAIN[int(t * FPS) % 4], skia.Rect(0, 0, W, H), skia.SamplingOptions(), p)
IMPACT_CF = skia.ColorFilters.Matrix([-2.6*.2126, -2.6*.7152, -2.6*.0722, 0, 1.55, -2.9*.2126, -2.9*.7152, -2.9*.0722, 0, 1.45, -2.9*.2126, -2.9*.7152, -2.9*.0722, 0, 1.4, 0, 0, 0, 1, 0])
def impact(surf):  # anime impact frame: inverted, high-contrast
    c = surf.getCanvas(); img = surf.makeImageSnapshot(); p = skia.Paint(); p.setColorFilter(IMPACT_CF); c.drawImage(img, 0, 0, skia.SamplingOptions(), p)
def puff(c, x, y, r, seed, col_='#D9D3E6', shade='#A79FBF', a=255, outline=True):
    rr = __import__('random').Random(seed); p = skia.Path(); p.addCircle(x, y, r)
    for i in range(6):
        ang = rr.uniform(0, 6.28); d = r * rr.uniform(.5, .9); q = skia.Path(); q.addCircle(x + math.cos(ang) * d, y + math.sin(ang) * d * .7, r * rr.uniform(.45, .75)); p = skia.Op(p, q, skia.PathOp.kUnion_PathOp)
    c.save(); c.saveLayerAlpha(None, int(a)); c.drawPath(p, fp(col_)); c.clipPath(p, doAntiAlias=True)
    o = skia.Path(p); o.offset(-r * .18, -r * .22); c.drawPath(skia.Op(p, o, skia.PathOp.kDifference_PathOp), fp(shade)); c.restore()
    if outline: c.drawPath(p, ink(LW * .9, INK, a))
    c.restore()
def finish(surf, bloom=0.40, sigma=20):
    c = surf.getCanvas(); img = surf.makeImageSnapshot(); c.clear(C((0, 0, 0)))
    p = skia.Paint(); p.setColorFilter(GRADE_CF); c.drawImage(img, 0, 0, skia.SamplingOptions(), p)
    b = skia.Paint(); b.setImageFilter(skia.ImageFilters.Blur(sigma, sigma, skia.TileMode.kClamp, skia.ImageFilters.ColorFilter(THRESH_CF)))
    b.setBlendMode(skia.BlendMode.kScreen); b.setAlphaf(bloom); c.drawImage(img, 0, 0, skia.SamplingOptions(), b)

# ---------------- puppet character
BODY_TOP, BODY_BOT, HEAD_R = -345, -128, 100
HEAD_CY = BODY_TOP - 74
SHOULDER = (-56, BODY_TOP + 54)
ARM = {
    'down': ((-90, -235), (-96, -168), True), 'hip': ((-128, -238), (-84, -190), True),
    'present': ((-128, -306), (-208, -338), True), 'gesture': ((-136, -262), (-152, -352), True),
    'wave': ((-150, -330), (-170, -450), True), 'wave2': ((-170, -320), (-215, -430), True),
    'up': ((-110, -360), (-130, -470), True), 'chin': ((-128, -262), (-62, -322), True),
    'hold': ((-96, -236), (-44, -214), True), 'push': ((-120, -270), (-200, -262), True),
    'phone': ((-120, -300), (-70, -400), True), 'scan': ((-130, -300), (-215, -300), True),
    'flail': ((-150, -300), (-210, -390), True), 'fist': ((-120, -250), (-70, -270), True),
    'swingF': ((-70, -238), (-20, -185), True), 'swingB': ((-110, -236), (-140, -180), True),
    'pumpF': ((-40, -250), (10, -300), True), 'pumpB': ((-130, -230), (-150, -280), True),
    'point': ((-140, -300), (-235, -320), True), 'shrug': ((-150, -250), (-170, -320), True),
    'cover': ((-140, -330), (-40, -400), True), 'bag': ((-110, -230), (-125, -165), True),
    'laugh': ((-120, -235), (-40, -215), True), 'self': ((-110, -250), (-30, -270), True),
    'draw': ((-100, -250), (-150, -230), True), 'heart': ((-110, -260), (-20, -290), True)}

def _arm(spec):
    if isinstance(spec, str): return ARM[spec]
    if spec[0] == 'lin':
        _, a, b, kk = spec; ea, ha, sa = ARM[a]; eb, hb, sb = ARM[b]
        return (lerp(ea[0], eb[0], kk), lerp(ea[1], eb[1], kk)), (lerp(ha[0], hb[0], kk), lerp(ha[1], hb[1], kk)), True
    a, b, k = spec; k = back(k, 1.6); ea, ha, sa = ARM[a]; eb, hb, sb = ARM[b]
    return (lerp(ea[0], eb[0], k), lerp(ea[1], eb[1], k)), (lerp(ha[0], hb[0], k), lerp(ha[1], hb[1], k)), (sb if k > .5 else sa)

def _hair_back(c, spec, R, lw):
    h = spec.get('hair')
    if h == 'long':
        hp = skia.Path(); hp.addRRect(skia.RRect.MakeRectXY(skia.Rect(-R - 12, -R + 10, R + 12, R + 70), 60, 60)); shape(c, hp, spec.get('hair_col', '#2A1D18'), lw)
    if h == 'bun': circ(c, 0, -R - 20, 42, spec.get('hair_col', '#2A1D18'), lw)
    if h == 'pigtails':
        for sx in (-1, 1): circ(c, sx * (R + 18), -10, 38, spec.get('hair_col', '#2A1D18'), lw)

def _hair_front(c, spec, R, lw, face, light):
    h = spec.get('hair'); hc = spec.get('hair_col', '#1C1B22'); fs = face * 16
    if h == 'spiky':
        hp = skia.Path(); n = 9; a0, a1 = math.radians(192), math.radians(348)
        for i in range(n + 1):
            a = lerp(a0, a1, i / n); r = R + (40 if i % 2 else 4)
            if i % 2: a += 0.04
            x, y = math.cos(a) * r, math.sin(a) * r
            (hp.moveTo if i == 0 else hp.lineTo)(x, y)
        # fringe: zig-zag across the forehead
        fr = [(R * .92, -24), (58 + fs, -40), (40 + fs, -18), (22 + fs, -46), (2 + fs, -14), (-18 + fs, -48), (-36 + fs, -20), (-56 + fs, -50), (-R * .95, -18)]
        for p_ in fr: hp.lineTo(*p_)
        hp.close(); shape(c, hp, hc, lw)
        shn = skia.Path(); shn.moveTo(-50 + fs, -78); shn.quadTo(-10 + fs, -96, 34 + fs, -84); c.drawPath(shn, ink(lw * 1.2, (88, 92, 122)))
    elif h in ('short', 'long', 'bun', 'pigtails'):
        hp = skia.Path(); hp.moveTo(-R - 4, -2); hp.arcTo(skia.Rect(-R - 5, -R - 6, R + 5, R + 4), 181, 178, False)
        hp.cubicTo(R - 4, -36, 50 + fs, -64, 6 + fs, -54); hp.cubicTo(-30 + fs, -62, -74, -44, -R - 4, -2); hp.close(); shape(c, hp, hc, lw)
    elif h == 'cap':
        cp = skia.Path(); cp.moveTo(-R + 2, -40); cp.cubicTo(-R, -R - 40, R, -R - 40, R - 2, -40); cp.close(); shape(c, cp, spec.get('cap_col', '#2E6B4E'), lw)
        d = 1 if face >= 0 else -1; poly(c, [(d * 10, -46), (d * (R + 60), -40), (d * (R + 56), -26), (d * 6, -32)], spec.get('cap_col', '#2E6B4E'), lw)

def draw_char(c, x, y, s, spec, face=0.0, eyes='dot', mouth='smile', brow=0.0, brow_tilt=0.0, arms=('down', 'down'),
              tilt=0.0, bob=0.0, squash=0.0, sweat=-1.0, light=-1, rim=None, legs=None, pupil=0.0, sparkle=0.0, lean=0.0, shadow=True, blush=0.0, gloom=0.0):
    lw = max(5.2, 4.0 / s); R = HEAD_R
    c.save(); c.translate(x, y); c.scale(s, s)
    if shadow: c.drawOval(skia.Rect(-120, -16, 120, 16), fp((8, 8, 20), 90, blur=10))
    jeans = spec.get('jeans')
    for (hx0, fx, lift) in (legs or ((-26, 0, 0), (26, 0, 0))):
        if jeans:
            p = skia.Path(); p.moveTo(hx0, BODY_BOT - 14); p.lineTo(hx0 + fx, -lift - 12)
            c.drawPath(p, ink(36, boil=False)); c.drawPath(p, ink(24, jeans, boil=False))
            oval(c, hx0 + fx - 26, -lift - 20, hx0 + fx + 24, -lift + 4, spec.get('shoe', '#F4F1EA'), lw * .8)
        else:
            c.drawLine(hx0, BODY_BOT - 8, hx0 + fx, -lift, ink(lw))
    bob += 3.0 * math.sin(BOIL['seed'] * .7 + x * .013)   # breathing idle, never fully still
    c.translate(0, -bob); c.skew(lean, 0); c.scale(1 + squash * .6, 1 - squash)
    if spec.get('dress'):
        dp = skia.Path(); dp.moveTo(-80, BODY_BOT - 40); dp.lineTo(80, BODY_BOT - 40); dp.lineTo(112, BODY_BOT + 50); dp.lineTo(-112, BODY_BOT + 50); dp.close(); shape(c, dp, spec['dress'], lw)
    if spec.get('cape'):
        cp = skia.Path(); sw = math.sin(BOIL['seed'] * .9) * 10
        cp.moveTo(-70, BODY_TOP + 20); cp.cubicTo(-130 + sw, -200, -150 + sw, -60, -120 + sw, 0); cp.lineTo(120 - sw, 0)
        cp.cubicTo(150 - sw, -60, 130 - sw, -200, 70, BODY_TOP + 20); cp.close(); shape(c, cp, spec['cape'], lw)
    body = skia.Path(); body.addRRect(skia.RRect.MakeRectXY(skia.Rect(-84, BODY_TOP, 84, BODY_BOT), 66, 72))
    c.drawPath(body, fp(spec['suit'])); c.save(); c.clipPath(body, doAntiAlias=True)
    sh = skia.Path(body); sh.offset(light * 16, -5); c.drawPath(skia.Op(body, sh, skia.PathOp.kDifference_PathOp), fp(spec['suit_d']))
    if spec.get('tee'):
        nk = skia.Path(); nk.addOval(skia.Rect(-30, BODY_TOP - 22, 30, BODY_TOP + 20)); c.drawPath(nk, fp(spec['skin']))
        c.drawArc(skia.Rect(-30, BODY_TOP - 22, 30, BODY_TOP + 20), 10, 160, False, ink(lw * .7))
        if spec.get('emblem'):
            ex, ey = face * 18, BODY_TOP + 98
            b = [(ex + 8, ey - 44), (ex - 22, ey + 4), (ex - 2, ey + 4), (ex - 12, ey + 42), (ex + 22, ey - 8), (ex + 2, ey - 8)]
            poly(c, b, spec['emblem'], lw * .6)
        if spec.get('vest'):
            for sx in (-1, 1): rect(c, sx * 84 - (0 if sx < 0 else 40), BODY_TOP, sx * 84 + (40 if sx < 0 else 0), BODY_BOT, spec['vest'], lw * .7)
    else:
        v = skia.Path(); v.moveTo(-34, BODY_TOP - 4); v.lineTo(0, BODY_TOP + 96); v.lineTo(34, BODY_TOP - 4); v.close(); c.drawPath(v, fp(spec['shirt']))
        poly(c, [(-9, BODY_TOP + 24), (9, BODY_TOP + 24), (13, BODY_TOP + 82), (0, BODY_TOP + 98), (-13, BODY_TOP + 82)], spec['tie'], lw * .75)
        for sx in (-1, 1):
            lp = skia.Path(); lp.moveTo(sx * 36, BODY_TOP - 2); lp.lineTo(sx * 2, BODY_TOP + 98); lp.lineTo(sx * 2, BODY_BOT); c.drawPath(lp, ink(lw * .75))
        if spec.get('star'):
            st = skia.Path(); sx_, sy_ = 40, BODY_TOP + 70
            for i in range(10):
                r_ = 16 if i % 2 == 0 else 7; a = -math.pi / 2 + i * math.pi / 5; (st.moveTo if i == 0 else st.lineTo)(sx_ + r_ * math.cos(a), sy_ + r_ * math.sin(a))
            st.close(); shape(c, st, spec['star'], lw * .5)
    c.restore(); c.drawPath(body, ink(lw))
    sleeve_col = spec['suit']; full = not spec.get('tee')
    for side, a in ((-1, arms[0]), (1, arms[1])):
        e, h, show = _arm(a); m = 1 if side < 0 else -1
        sx, sy = SHOULDER[0] * m, SHOULDER[1]; ex, ey, hx_, hy_ = e[0] * m, e[1], h[0] * m, h[1]
        ap = skia.Path(); ap.moveTo(sx, sy); ap.quadTo(1.35*ex - .175*(sx+hx_), 1.35*ey - .175*(sy+hy_), hx_, hy_)
        meas = skia.PathMeasure(ap, False); L = meas.getLength()
        upper = skia.Path(); meas.getSegment(0, L * (0.98 if full else .38), upper, True)
        c.drawPath(ap, ink(27, boil=False)); c.drawPath(ap, ink(16, spec['skin'], boil=False))
        c.save(); c.clipPath(body, skia.ClipOp.kDifference, True); c.drawPath(upper, ink(36, boil=False)); c.restore()
        c.drawPath(upper, ink(25, sleeve_col, boil=False))
        if show:
            if spec.get('band'):
                bx, by = meas.getPosTan(L * .86)[0]; circ(c, bx, by, 15, spec['band'], lw * .7)
            circ(c, hx_, hy_, 19, spec.get('glove', spec['skin']), lw * .8)
            c.drawCircle(hx_ - 5, hy_ - 6, 5, fp((255, 255, 255), 70))
    c.save(); c.translate(0, HEAD_CY); c.rotate(tilt)
    _hair_back(c, spec, R, lw)
    head = skia.Path(); head.addCircle(0, 0, R)
    c.drawPath(head, fp(spec['skin'])); c.save(); c.clipPath(head, doAntiAlias=True)
    lit = skia.Path(head); lit.offset(light * 7, -17); c.drawPath(skia.Op(head, lit, skia.PathOp.kDifference_PathOp), fp(spec['skin_d']))
    if rim: rm = skia.Path(head); rm.offset(-light * 11, 4); c.drawPath(skia.Op(head, rm, skia.PathOp.kDifference_PathOp), fp(rim, 200))
    c.restore(); c.drawPath(head, ink(lw))
    _hair_front(c, spec, R, lw, face, light)
    fx = face * 40; eyy = -2
    for ex0 in (-30, 30):
        ex = ex0 + fx; far = (face > 0 and ex0 < 0) or (face < 0 and ex0 > 0); sq = 1 - .3 * abs(face) if far else 1.0
        if eyes == 'wide':
            oval(c, ex - 18*sq, eyy - 19, ex + 18*sq, eyy + 19, '#FBFBF7', lw * .7)
            c.drawOval(skia.Rect(ex - 5.5*sq + pupil*7, eyy - 5.5, ex + 5.5*sq + pupil*7, eyy + 5.5), fp(INK))
        elif eyes == 'closed':
            e = skia.Path(); e.moveTo(ex - 11*sq, eyy); e.quadTo(ex, eyy + 9, ex + 11*sq, eyy); c.drawPath(e, ink(lw * .8))
        elif eyes == 'sleepy':
            c.drawLine(ex - 12*sq, eyy + 2, ex + 12*sq, eyy + 2, ink(lw * .8))
        elif eyes == 'half':
            c.save(); c.clipRect(skia.Rect(ex - 20, eyy - 3, ex + 20, eyy + 20)); c.drawOval(skia.Rect(ex - 6.5*sq, eyy - 9, ex + 6.5*sq, eyy + 9), fp(INK)); c.restore()
            c.drawLine(ex - 13*sq, eyy - 4, ex + 13*sq, eyy - 4, ink(lw * .8))
        elif eyes == 'shock':
            oval(c, ex - 20*sq, eyy - 22, ex + 20*sq, eyy + 22, '#FBFBF7', lw * .7); c.drawCircle(ex, eyy, 3.2, fp(INK))
        else:
            px = ex + pupil * 3
            c.drawOval(skia.Rect(px - 7.5*sq, eyy - 11, px + 7.5*sq, eyy + 11), fp(INK))
            c.drawCircle(px + 2.5, eyy - 4.5, 3.0, fp((255, 255, 255), 235)); c.drawCircle(px - 2.5, eyy + 4.5, 1.4, fp((255, 255, 255), 160))
        inner = 1 if ex0 < 0 else -1; by = eyy - 30 - brow * 9
        c.drawLine(ex - 13*sq, by + (brow_tilt*7 if inner < 0 else -brow_tilt*7), ex + 13*sq, by + (brow_tilt*7 if inner > 0 else -brow_tilt*7), ink(lw * .78))
    if spec.get('glasses'):
        for ex0 in (-30, 30):
            ex = ex0 + fx; g = skia.Path(); g.addOval(skia.Rect(ex - 23, eyy - 23, ex + 23, eyy + 23)); c.drawPath(g, fp((225, 240, 255), 55)); c.drawPath(g, ink(lw * .7))
        c.drawLine(fx - 7, eyy - 3, fx + 7, eyy - 3, ink(lw * .7))
    if blush > 0:
        for ex0 in (-48, 48): c.drawOval(skia.Rect(ex0 + fx * .8 - 17, 20, ex0 + fx * .8 + 17, 32), fp('#F07A7A', 110 * blush, blur=3))
    if gloom > 0:
        c.save(); hd = skia.Path(); hd.addCircle(0, 0, R - 3); c.clipPath(hd, doAntiAlias=True)
        for i in range(9): c.drawLine(-70 + i * 17, -44, -70 + i * 17, -44 + 40 * gloom + (i % 3) * 8, ink(4, '#4A5FC8', 200, boil=False))
        c.restore()
    mx, my = face * 34, 44
    if mouth == 'smile': m = skia.Path(); m.moveTo(mx - 17, my - 2); m.quadTo(mx, my + 13, mx + 17, my - 2); c.drawPath(m, ink(lw * .8))
    elif mouth == 'grin':
        mp = skia.Path(); mp.moveTo(mx - 24, my - 6); mp.quadTo(mx, my + 30, mx + 24, my - 6); mp.close(); shape(c, mp, '#FAFAF4', lw * .7)
    elif mouth == 'smirk':
        d = 1 if face >= 0 else -1; m = skia.Path(); m.moveTo(mx - 15*d, my + 3); m.quadTo(mx + 4*d, my + 12, mx + 20*d, my - 6); c.drawPath(m, ink(lw * .8))
    elif mouth == 'flat': c.drawLine(mx - 12, my + 2, mx + 12, my + 2, ink(lw * .8))
    elif mouth == 'frown': m = skia.Path(); m.moveTo(mx - 15, my + 8); m.quadTo(mx, my - 4, mx + 15, my + 8); c.drawPath(m, ink(lw * .8))
    elif mouth == 'o': oval(c, mx - 9, my - 10, mx + 9, my + 12, '#5A1A1E', lw * .7)
    elif mouth == 'mid': oval(c, mx - 12, my - 4, mx + 12, my + 10, '#5A1A1E', lw * .7)
    elif mouth == 'open':
        mp = skia.Path(); mp.moveTo(mx - 20, my - 5); mp.lineTo(mx + 20, my - 5); mp.cubicTo(mx + 19, my + 26, mx - 19, my + 26, mx - 20, my - 5); mp.close()
        c.drawPath(mp, fp('#5A1A1E')); c.save(); c.clipPath(mp, doAntiAlias=True)
        c.drawRect(skia.Rect(mx - 22, my - 6, mx + 22, my + 2), fp('#FAFAF4')); c.drawOval(skia.Rect(mx - 11, my + 9, mx + 11, my + 28), fp('#D05860')); c.restore()
        c.drawPath(mp, ink(lw * .7))
    if sparkle > 0:
        k = pop(sparkle) * (1 if sparkle < 1 else max(0, 2 - sparkle)); sx_, sy_ = mx + 30 * (1 if face >= 0 else -1), my - 10; st = skia.Path()
        for i in range(8):
            r_ = (22 if i % 2 == 0 else 5) * k; a = i * math.pi / 4; (st.moveTo if i == 0 else st.lineTo)(sx_ + r_ * math.cos(a), sy_ + r_ * math.sin(a))
        st.close(); c.drawPath(st, fp('#FFFFFF'))
    if sweat >= 0:
        sx0, sy0 = (-1 if face > 0 else 1) * 66, -60 + 34 * (sweat % 1.0)
        d = skia.Path(); d.moveTo(sx0, sy0 - 20); d.cubicTo(sx0 + 13, sy0 - 3, sx0 + 12, sy0 + 11, sx0, sy0 + 11); d.cubicTo(sx0 - 12, sy0 + 11, sx0 - 13, sy0 - 3, sx0, sy0 - 20); d.close()
        shape(c, d, '#8FC8EE', lw * .7)
    c.restore(); c.restore()

def walk_arms(phase):  # opposite to legs
    u = .5 + .5 * math.sin(phase)
    return (('lin', 'swingB', 'swingF', u), ('lin', 'swingB', 'swingF', 1 - u))
def run_arms(phase):
    u = .5 + .5 * math.sin(phase)
    return (('lin', 'pumpB', 'pumpF', u), ('lin', 'pumpB', 'pumpF', 1 - u))
def walk_legs(phase, stride=40, lift=18):
    a = math.sin(phase)
    return ((-12, a * stride, max(0, math.cos(phase)) * lift), (12, -a * stride, max(0, -math.cos(phase)) * lift))

# ---- cast (original designs)
HERO = dict(skin='#EDBE92', skin_d='#D29E70', suit='#D9262E', suit_d='#A91B23', tee=True, emblem='#FFFFFF',
            hair='spiky', hair_col='#17161C', jeans='#2F5FA8', shoe='#F6F3EC', band='#1B1A20')
AUREX = dict(skin='#F0C9A0', skin_d='#D6A77A', suit='#E9B53C', suit_d='#C28E22', shirt='#FFF6DC', tie='#B5302E',
             hair='short', hair_col='#F5E3A6', cape='#B5302E', star='#FFFFFF', jeans='#E9B53C', shoe='#7A3A20', glove='#FFF6DC')
TEENS = [
    dict(skin='#8D5B3E', skin_d='#6E4330', suit='#3E8E6E', suit_d='#2D6B52', tee=True, hair='short', hair_col='#141218', jeans='#3B3F58'),
    dict(skin='#F2CDAA', skin_d='#D8AD86', suit='#E8A33A', suit_d='#C28124', tee=True, hair='long', hair_col='#6B3A22', jeans='#46507A'),
    dict(skin='#C99269', skin_d='#A8724D', suit='#6C4FB0', suit_d='#4F3889', tee=True, hair='cap', cap_col='#D9473A', jeans='#2E3550'),
    dict(skin='#E8B48C', skin_d='#C99068', suit='#2E8DB8', suit_d='#226C8E', tee=True, hair='bun', hair_col='#1D1A20', jeans='#3A3F5C'),
]
