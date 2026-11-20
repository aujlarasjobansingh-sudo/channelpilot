# Tutorial "desktop screen" motion engine (skia -> ffmpeg)
import skia, numpy as np, subprocess, math, os, json

W, H, FPS = 1920, 1080, 30
ROOT = os.environ.get("TUT_ROOT", os.getcwd())   # project folder: assets/, shots/, out/

def _find_font(names):
    """search common font folders (and ./fonts) for the first matching file name"""
    import glob
    dirs = [os.path.join(ROOT, "fonts"), os.path.expanduser("~/.fonts"), os.path.expanduser("~/.local/share/fonts"),
            "/usr/share/fonts", "/usr/local/share/fonts", "/Library/Fonts", os.path.expanduser("~/Library/Fonts")]
    for n in names:
        for d in dirs:
            hits = glob.glob(os.path.join(d, "**", n), recursive=True)
            if hits: return skia.Typeface.MakeFromFile(hits[0])
    return None
_W = dict(r=["Inter-Regular.otf", "Inter-Regular.ttf"], m=["Inter-Medium.otf", "Inter-Medium.ttf"],
          s=["Inter-SemiBold.otf", "Inter-SemiBold.ttf"], b=["Inter-Bold.otf", "Inter-Bold.ttf"],
          x=["Inter-ExtraBold.otf", "Inter-ExtraBold.ttf"], d=["InterDisplay-Black.otf", "Inter-Black.otf", "Inter-Black.ttf"],
          mono=["DejaVuSansMono.ttf", "JetBrainsMono-Regular.ttf", "Menlo.ttc"])
_fb = {"r": skia.FontStyle.Normal(), "m": skia.FontStyle.Normal(), "s": skia.FontStyle.Bold(), "b": skia.FontStyle.Bold(),
       "x": skia.FontStyle.Bold(), "d": skia.FontStyle.Bold(), "mono": skia.FontStyle.Normal()}
TF = {}
for k, names in _W.items():
    TF[k] = _find_font(names) or skia.Typeface.MakeFromName("monospace" if k == "mono" else "sans-serif", _fb[k])
_fc = {}
def font(w="m", size=20):
    k = (w, size)
    if k not in _fc:
        f = skia.Font(TF[w], size); f.setEdging(skia.Font.Edging.kAntiAlias); f.setSubpixel(True); _fc[k] = f
    return _fc[k]

def col(h, a=1.0):
    h = h.lstrip("#"); r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return skia.Color(r, g, b, int(max(0, min(1, a)) * 255))

def paint(c, aa=True, style=None, sw=None):
    p = skia.Paint(Color=c, AntiAlias=aa)
    if style == "stroke": p.setStyle(skia.Paint.kStroke_Style); p.setStrokeWidth(sw or 2)
    return p

# ---------- easing ----------
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def lin(t, t0, t1): return clamp((t - t0) / max(1e-6, t1 - t0))
def eio(x): x = clamp(x); return 4 * x * x * x if x < .5 else 1 - (-2 * x + 2) ** 3 / 2
def eout(x): x = clamp(x); return 1 - (1 - x) ** 3
def back(x, s=1.4): x = clamp(x); x -= 1; return x * x * ((s + 1) * x + s) + 1
def mix(a, b, k): return a + (b - a) * k

# ---------- text ----------
def text(c, s, x, y, size=20, w="m", color="#ffffff", a=1.0, align="l"):
    f = font(w, size); p = paint(col(color, a))
    if align != "l":
        tw = f.measureText(s); x -= tw if align == "r" else tw / 2
    c.drawString(s, x, y, f, p)
def tw(s, size=20, w="m"): return font(w, size).measureText(s)

def rrect(c, x, y, w, h, r, color, a=1.0):
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, y, w, h), r, r), paint(col(color, a)))
def rrect_stroke(c, x, y, w, h, r, color, a=1.0, sw=2):
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, y, w, h), r, r), paint(col(color, a), style="stroke", sw=sw))
def shadow(c, x, y, w, h, r, a=0.55, blur=34, dy=18):
    p = paint(col("#000000", a)); p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur / 2))
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, y + dy, w, h), r, r), p)

def load_img(path):
    return skia.Image.open(path)
def draw_img(c, img, x, y, w, h, a=1.0, r=0):
    p = skia.Paint(AntiAlias=True); p.setAlphaf(a)
    if r:
        c.save(); c.clipRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, y, w, h), r, r), True)
    c.drawImageRect(img, skia.Rect.MakeXYWH(x, y, w, h), skia.SamplingOptions(skia.FilterMode.kLinear, skia.MipmapMode.kLinear), p)
    if r: c.restore()
def draw_img_cover(c, img, x, y, w, h, a=1.0, r=0, fx=0.5, fy=0.5):
    iw, ih = img.width(), img.height(); s = max(w / iw, h / ih)
    sw, sh = w / s, h / s; sx, sy = (iw - sw) * fx, (ih - sh) * fy
    p = skia.Paint(AntiAlias=True); p.setAlphaf(a)
    c.save(); c.clipRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, y, w, h), r, r), True)
    c.drawImageRect(img, skia.Rect.MakeXYWH(sx, sy, sw, sh), skia.Rect.MakeXYWH(x, y, w, h),
                    skia.SamplingOptions(skia.FilterMode.kLinear, skia.MipmapMode.kLinear), p)
    c.restore()

# ---------- wallpaper (original wave gradient, desktop look) ----------
_wall = None
def wallpaper():
    global _wall
    if _wall is not None: return _wall
    S = 1.0; ww, wh = W, H
    surf = skia.Surface(ww, wh); c = surf.getCanvas()
    c.drawPaint(skia.Paint(Shader=skia.GradientShader.MakeLinear(
        [(0, 0), (ww, wh)], [col("#3a0b4a"), col("#c2185b"), col("#ff5a3c")])))
    def band(pts_top, color_list, blur=0):
        path = skia.Path(); path.moveTo(*pts_top[0])
        for i in range(1, len(pts_top) - 2, 3):
            path.cubicTo(*pts_top[i], *pts_top[i + 1], *pts_top[i + 2])
        path.lineTo(ww + 50, wh + 50); path.lineTo(-50, wh + 50); path.close()
        p = skia.Paint(AntiAlias=True, Shader=skia.GradientShader.MakeLinear([(0, 0), (ww, 0)], color_list))
        if blur: p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur))
        c.drawPath(path, p)
    band([(-50, 260), (500, 120), (900, -60), (1500, 80), (1700, 120), (1850, 100), (1980, 60)],
         [col("#2b6fd6"), col("#4fb3ff"), col("#7fd8ff")], 3)
    band([(-50, 420), (450, 300), (900, 160), (1400, 330), (1650, 420), (1800, 380), (1980, 300)],
         [col("#e8336b"), col("#ff7a8a"), col("#f0f4ff")], 3)
    band([(-50, 560), (500, 470), (950, 380), (1400, 520), (1650, 600), (1800, 560), (1980, 480)],
         [col("#d11a5a"), col("#ff6a3d"), col("#ffb12e")], 3)
    band([(-50, 760), (450, 640), (900, 560), (1350, 700), (1600, 780), (1800, 760), (1980, 700)],
         [col("#9c0f4f"), col("#e5394d"), col("#ff8c2a")], 3)
    band([(-50, 930), (500, 840), (950, 800), (1400, 900), (1650, 960), (1800, 940), (1980, 900)],
         [col("#5d0b3f"), col("#a3134d"), col("#d63a3a")], 3)
    # soft vignette
    c.drawPaint(skia.Paint(Shader=skia.GradientShader.MakeRadial((ww / 2, wh / 2), ww * 0.75,
        [col("#000000", 0), col("#000000", 0.35)])))
    _wall = surf.makeImageSnapshot(); return _wall

# ---------- dock & menu bar ----------
DOCK_ICONS = [("#3b82f6", "folder"), ("#f97316", "chat"), ("#10b981", "globe"),
              ("#2563eb", "code"), ("#111827", "term"), ("#ec4899", "note")]
def glyph(c, kind, x, y, s):
    wp = paint(col("#ffffff", 0.95)); sp = paint(col("#ffffff", 0.95), style="stroke", sw=s * 0.07)
    cx, cy = x + s / 2, y + s / 2
    if kind == "folder":
        rrect(c, x + s * .2, y + s * .32, s * .6, s * .42, s * .06, "#ffffff", .95)
        rrect(c, x + s * .2, y + s * .26, s * .25, s * .12, s * .04, "#ffffff", .95)
    elif kind == "chat":
        # simple sparkle / asterisk mark (generic)
        for k in range(6):
            a = k * math.pi / 3
            c.drawLine(cx, cy, cx + math.cos(a) * s * .28, cy + math.sin(a) * s * .28, sp)
    elif kind == "globe":
        c.drawCircle(cx, cy, s * .27, sp); c.drawLine(cx - s * .27, cy, cx + s * .27, cy, sp)
        c.drawOval(skia.Rect.MakeXYWH(cx - s * .12, cy - s * .27, s * .24, s * .54), sp)
    elif kind == "code":
        f = font("b", s * .38); text(c, "</>", cx, cy + s * .13, s * .36, "b", "#ffffff", 1, "c")
    elif kind == "term":
        text(c, ">_", x + s * .2, cy + s * .12, s * .34, "b", "#22c55e")
    elif kind == "note":
        c.drawCircle(cx - s * .08, cy + s * .14, s * .09, wp); c.drawLine(cx + s * .01, cy + s * .14, cx + s * .01, cy - s * .2, sp)
        c.drawLine(cx + s * .01, cy - s * .2, cx + s * .18, cy - s * .12, sp)

def dock(c, active=-1, a=1.0):
    n = len(DOCK_ICONS); s = 58; g = 12; dw = n * s + (n + 1) * g; dh = s + 2 * g * .9
    x0 = (W - dw) / 2; y0 = H - dh - 12
    rrect(c, x0, y0, dw, dh, 22, "#ffffff", 0.22 * a); rrect_stroke(c, x0, y0, dw, dh, 22, "#ffffff", 0.25 * a, 1.2)
    for i, (cc, k) in enumerate(DOCK_ICONS):
        x = x0 + g + i * (s + g); y = y0 + (dh - s) / 2
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, y, s, s), 14, 14), skia.Paint(AntiAlias=True,
            Shader=skia.GradientShader.MakeLinear([(x, y), (x, y + s)], [col(cc), col(cc, 1)]), Alphaf=a))
        rrect(c, x, y, s, s * .5, 14, "#ffffff", 0.12 * a)
        glyph(c, k, x, y, s)
        if i == active: c.drawCircle(x + s / 2, y0 + dh - 5, 2.6, paint(col("#ffffff", .9 * a)))

def menubar(c, app="Finder"):
    rrect(c, 0, 0, W, 30, 0, "#000000", 0.25)
    text(c, app, 52, 21, 15, "b", "#ffffff", .95)
    for i, m in enumerate(["File", "Edit", "View", "Window", "Help"]):
        text(c, m, 52 + tw(app, 15, "b") + 26 + i * 64, 21, 15, "m", "#ffffff", .85)
    c.drawCircle(26, 15, 7, paint(col("#ffffff", .9)))
    import datetime; text(c, datetime.datetime.now().strftime("%a %d %b  %I:%M %p"), W - 20, 21, 15, "m", "#ffffff", .9, "r")

# ---------- windows ----------
def window(c, x, y, w, h, title="", a=1.0, bar=38, bg="#1b1b1f", sc=1.0, content=None, radius=14):
    if a <= 0.001: return
    c.save()
    if sc != 1.0:
        c.translate(x + w / 2, y + h / 2); c.scale(sc, sc); c.translate(-(x + w / 2), -(y + h / 2))
    if a < 1: c.saveLayerAlpha(None, int(a * 255))
    shadow(c, x, y, w, h, radius)
    rrect(c, x, y, w, h, radius, bg)
    rrect(c, x, y, w, bar, radius, "#2a2a30"); c.drawRect(skia.Rect.MakeXYWH(x, y + bar - radius, w, radius), paint(col("#2a2a30")))
    c.drawLine(x, y + bar, x + w, y + bar, paint(col("#000000", .5)))
    for i, cc in enumerate(["#ff5f57", "#febc2e", "#28c840"]):
        c.drawCircle(x + 22 + i * 22, y + bar / 2, 6.5, paint(col(cc)))
    if title: text(c, title, x + w / 2, y + bar / 2 + 6, 15, "m", "#c9c9d1", 1, "c")
    if content:
        c.save(); c.clipRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, y + bar, w, h - bar), radius, radius), True)
        c.clipRect(skia.Rect.MakeXYWH(x, y + bar, w, h - bar))
        content(c, x, y + bar, w, h - bar)
        c.restore()
    rrect_stroke(c, x, y, w, h, radius, "#ffffff", .10, 1)
    if a < 1: c.restore()
    c.restore()

# ---------- cursor ----------
_cur = None
def cursor(c, x, y, s=1.0, press=0.0):
    global _cur
    if _cur is None:
        p = skia.Path(); pts = [(0, 0), (0, 25), (6, 19.5), (10.5, 29), (14.5, 27.2), (10, 18), (18, 18)]
        p.moveTo(*pts[0]); [p.lineTo(*q) for q in pts[1:]]; p.close(); _cur = p
    c.save(); c.translate(x, y); sc = s * 1.35 * (1 - 0.12 * press); c.scale(sc, sc)
    sh = paint(col("#000000", .35)); sh.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 2))
    c.save(); c.translate(1.5, 2.5); c.drawPath(_cur, sh); c.restore()
    c.drawPath(_cur, paint(col("#111111"))); c.drawPath(_cur, paint(col("#ffffff"), style="stroke", sw=1.6))
    c.restore()
def click_ring(c, x, y, k):
    if 0 < k < 1:
        c.drawCircle(x, y, 10 + 34 * eout(k), paint(col("#ffffff", .55 * (1 - k)), style="stroke", sw=3))

class Path2:
    """cursor keyframes: list of (t, x, y)"""
    def __init__(self, keys): self.k = keys
    def at(self, t):
        k = self.k
        if t <= k[0][0]: return k[0][1], k[0][2]
        for i in range(len(k) - 1):
            if k[i][0] <= t <= k[i + 1][0]:
                e = eio(lin(t, k[i][0], k[i + 1][0]))
                return mix(k[i][1], k[i + 1][1], e), mix(k[i][2], k[i + 1][2], e)
        return k[-1][1], k[-1][2]

class Cam:
    """camera keyframes (t, cx, cy, zoom); ease in-out between"""
    def __init__(self, keys): self.k = keys
    def at(self, t):
        k = self.k
        if t <= k[0][0]: return k[0][1:]
        for i in range(len(k) - 1):
            if k[i][0] <= t <= k[i + 1][0]:
                e = eio(lin(t, k[i][0], k[i + 1][0]))
                z = math.exp(mix(math.log(k[i][3]), math.log(k[i + 1][3]), e))
                return mix(k[i][1], k[i + 1][1], e), mix(k[i][2], k[i + 1][2], e), z
        return k[-1][1:]

# ---------- video sources ----------
class Vid:
    def __init__(self, path, start, w, h, fps=FPS):
        self.path, self.start, self.w, self.h = path, start, int(w), int(h)
        self.p = None; self.n = -1; self.img = None
    def _open(self):
        self.p = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-ss", str(self.start), "-i", self.path,
            "-vf", f"fps={FPS},scale={self.w}:{self.h}:flags=bicubic", "-f", "rawvideo", "-pix_fmt", "rgba", "-"],
            stdout=subprocess.PIPE, bufsize=10 ** 8)
    def frame(self, i):
        i = max(0, int(i))
        if self.p is None: self._open()
        while self.n < i:
            buf = self.p.stdout.read(self.w * self.h * 4)
            if len(buf) < self.w * self.h * 4: break
            arr = np.frombuffer(buf, np.uint8).reshape(self.h, self.w, 4).copy()
            self.img = skia.Image.fromarray(arr, colorType=skia.kRGBA_8888_ColorType); self.n += 1
        return self.img
    def close(self):
        if self.p: self.p.kill(); self.p = None

# ---------- render ----------
class Writer:
    def __init__(self, path):
        self.tmp = path[:-4] + ".tmp.mp4"; self.path = path
        self.p = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgra",
            "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
            "-pix_fmt", "yuv420p", "-r", str(FPS), self.tmp], stdin=subprocess.PIPE)
    def write(self, surf):
        self.p.stdin.write(surf.makeImageSnapshot().toarray(colorType=skia.kBGRA_8888_ColorType).tobytes())
    def close(self):
        self.p.stdin.close(); r = self.p.wait()
        if r == 0: os.replace(self.tmp, self.path)
        return r

def render(path, dur, draw, cam=None, intro=True, motion_blur=True, overlay=None, fade_out=0.0):
    """draw(c, t) draws the desktop in scene coords. cam: Cam or None."""
    n = int(round(dur * FPS)); wr = Writer(path)
    out = skia.Surface(W, H); scene = skia.Surface(W, H)
    prev = None
    for i in range(n):
        t = i / FPS
        cx, cy, z = cam.at(t) if cam else (W / 2, H / 2, 1.0)
        ik = lin(t, 0, 0.22) if intro else 1
        zi = z * (1 + 0.07 * (1 - eout(ik)))
        blur = 14 * (1 - eout(ik)) if (intro and ik < 1) else 0
        if motion_blur and cam:
            cx2, cy2, z2 = cam.at(max(0, t - 1 / FPS))
            sp = math.hypot((cx - cx2) * z, (cy - cy2) * z) + abs(math.log(z / z2)) * 1500
            blur = max(blur, clamp((sp - 10) / 9, 0, 18))
        sc = scene.getCanvas(); sc.clear(col("#000000"))
        sc.save(); sc.translate(W / 2, H / 2); sc.scale(zi, zi); sc.translate(-cx, -cy)
        draw(sc, t)
        sc.restore()
        if overlay: overlay(sc, t)
        if fade_out and t > dur - fade_out:
            sc.drawPaint(paint(col("#000000", lin(t, dur - fade_out, dur))))
        if blur > 0.4:
            oc = out.getCanvas(); oc.clear(col("#000000"))
            p = skia.Paint(); p.setImageFilter(skia.ImageFilters.Blur(blur, blur * 0.6))
            oc.drawImage(scene.makeImageSnapshot(), 0, 0, skia.SamplingOptions(), p)
            wr.write(out)
        else:
            wr.write(scene)
    return wr.close()

def still(path, t, draw, cam=None):
    s = skia.Surface(W, H); c = s.getCanvas(); c.clear(col("#000000"))
    cx, cy, z = cam.at(t) if cam else (W / 2, H / 2, 1.0)
    c.save(); c.translate(W / 2, H / 2); c.scale(z, z); c.translate(-cx, -cy); draw(c, t); c.restore()
    s.makeImageSnapshot().save(path)
