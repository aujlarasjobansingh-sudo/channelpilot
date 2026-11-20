from eng import *
import re, glob
A = ROOT + "/assets"
ENV = np.load(A + "/voenv.npy") if os.path.exists(A + "/voenv.npy") else np.zeros(1)  # voice loudness per frame (make_voenv)
SF = []  # local sfx (t, kind, gain) for the scene being built
def sfx(t, kind, g=1.0): SF.append((t, kind, g))
def env_at(t_abs):
    i = int(t_abs * FPS); return float(ENV[i]) if 0 <= i < len(ENV) else 0.0

_imgc = {}
def IMG(p):
    if p not in _imgc: _imgc[p] = load_img(p if p.startswith("/") else A + "/" + p)
    return _imgc[p]

def bg(c, app="Finder", dock_i=0, dock_a=1.0):
    draw_img(c, wallpaper(), -500, -300, W + 1000, H + 600); menubar(c, app)
def bgdock(c, i=0): dock(c, i)

# ---------- text helpers ----------
def wrap(s, size, maxw, w="m"):
    out = []
    for para in s.split("\n"):
        line = ""
        for word in para.split(" "):
            t = (line + " " + word).strip()
            if tw(t, size, w) > maxw and line: out.append(line); line = word
            else: line = t
        out.append(line)
    return out
def typed(s, t, t0, cps=28):
    n = int(max(0, (t - t0)) * cps); return s[:n], n < len(s)
def type_sfx(t0, s, cps=28, every=3, g=.8):
    for i in range(0, len(s), every):
        if s[i] != " ": sfx(t0 + i / cps, "type", g)

def pill(c, x, y, s, size=22, fg="#ffffff", bgc="#17171b", a=1.0, k=1.0, icon=None, icol="#ff7a45", align="l", pad=18):
    if a <= 0: return
    w = tw(s, size, "s") + pad * 2 + (size * 1.3 if icon else 0); h = size * 2.05
    if align == "c": x -= w / 2
    c.save(); e = back(k)
    c.translate(x + w / 2, y + h / 2); c.scale(mix(.6, 1, e), mix(.6, 1, e)); c.translate(-(x + w / 2), -(y + h / 2))
    c.saveLayerAlpha(None, int(255 * a * clamp(k * 3)))
    shadow(c, x, y, w, h, h / 2, .45, 20, 6)
    rrect(c, x, y, w, h, h / 2, bgc); rrect_stroke(c, x, y, w, h, h / 2, "#ffffff", .14, 1.2)
    tx = x + pad
    if icon:
        cy = y + h / 2; r = size * .48
        if icon == "check": check(c, tx + r, cy, r, icol)
        elif icon == "cross": cross(c, tx + r, cy, r, icol)
        else: c.drawCircle(tx + r, cy, r * .55, paint(col(icol)))
        tx += size * 1.3
    text(c, s, tx, y + h / 2 + size * .36, size, "s", fg)
    c.restore(); c.restore()
    return w

def check(c, x, y, r, color="#22c55e", k=1.0):
    c.drawCircle(x, y, r, paint(col(color)))
    p = skia.Path(); p.moveTo(x - r * .45, y + r * .02); p.lineTo(x - r * .1, y + r * .38); p.lineTo(x + r * .5, y - r * .35)
    pp = paint(col("#ffffff"), style="stroke", sw=r * .28); pp.setStrokeCap(skia.Paint.kRound_Cap); pp.setStrokeJoin(skia.Paint.kRound_Join)
    if k < 1:
        m = skia.PathMeasure(p, False); d = skia.Path(); m.getSegment(0, m.getLength() * k, d, True); p = d
    c.drawPath(p, pp)
def cross(c, x, y, r, color="#ef4444"):
    c.drawCircle(x, y, r, paint(col(color)))
    pp = paint(col("#ffffff"), style="stroke", sw=r * .26); pp.setStrokeCap(skia.Paint.kRound_Cap)
    d = r * .38; c.drawLine(x - d, y - d, x + d, y + d, pp); c.drawLine(x + d, y - d, x - d, y + d, pp)

def spark(c, x, y, r, color="#d97757", rot=0):
    """generic 8-ray sparkle mark used as the assistant avatar"""
    pp = paint(col(color), style="stroke", sw=r * .22); pp.setStrokeCap(skia.Paint.kRound_Cap)
    for k in range(8):
        a = rot + k * math.pi / 4; L = r if k % 2 == 0 else r * .7
        c.drawLine(x + math.cos(a) * r * .18, y + math.sin(a) * r * .18, x + math.cos(a) * L, y + math.sin(a) * L, pp)

class Pop:
    """context manager: scale+fade pop around a rect"""
    def __init__(self, c, x, y, w, h, k, a=None, s0=.85):
        self.c, self.x, self.y, self.w, self.h, self.k = c, x, y, w, h, k
        self.a = clamp(k * 2.5) if a is None else a; self.s0 = s0
    def __enter__(self):
        c = self.c; e = back(self.k); c.save()
        cx, cy = self.x + self.w / 2, self.y + self.h / 2
        c.translate(cx, cy); s = mix(self.s0, 1, e); c.scale(s, s); c.translate(-cx, -cy)
        c.saveLayerAlpha(None, int(255 * clamp(self.a)))
        return self
    def __exit__(self, *a): self.c.restore(); self.c.restore()

def panel(c, x, y, w, h, r=26, bgc="#141418", a=.96):
    shadow(c, x, y, w, h, r, .55, 36, 14)
    rrect(c, x, y, w, h, r, bgc, a); rrect_stroke(c, x, y, w, h, r, "#ffffff", .13, 1.4)

def big_title(c, s, y, size, k, color="#ffffff", sub=None, subk=0):
    if k <= 0: return
    e = back(k)
    c.save(); c.translate(W / 2, y); c.scale(mix(.7, 1, e), mix(.7, 1, e))
    c.saveLayerAlpha(None, int(255 * clamp(k * 3)))
    sh = paint(col("#000000", .45)); sh.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 10))
    f = font("d", size); w = f.measureText(s)
    c.drawString(s, -w / 2 + 4, 8, f, sh)
    text(c, s, 0, 0, size, "d", color, 1, "c")
    c.restore(); c.restore()
    if sub and subk > 0:
        text(c, sub, W / 2, y + size * .75, size * .36, "s", "#ffffff", clamp(subk * 3) * .92, "c")

# ---------- chat window ----------
CHAT_BG = "#262624"
CHAT_HISTORY = ["Style study", "My video", "2 min version"]  # sidebar chat titles; set per video
def chat_window(c, x, y, w, h, t, msgs, inp="", inp_caret=False, model="Opus 5.5", picker=None, a=1.0, sc=1.0, title="Claude"):
    """msgs: list of dict(role='user'|'ai', text, t0 (appear time), items=[(label, t_done)], attach=img)"""
    def f(c2, cx, cy, cw, ch):
        rrect(c2, cx, cy, cw, ch, 0, CHAT_BG)
        # side bar
        rrect(c2, cx, cy, 220, ch, 0, "#1f1f1d")
        spark(c2, cx + 34, cy + 34, 13, "#d97757")
        text(c2, "Claude", cx + 58, cy + 41, 20, "s", "#ecebe6")
        for i, s in enumerate(["New chat"] + list(CHAT_HISTORY)):
            if i == 0: rrect(c2, cx + 14, cy + 78, 192, 34, 8, "#2f2f2c")
            text(c2, s, cx + 28, cy + 100 + i * 42, 15, "m", "#c9c7bf" if i else "#ffffff")
        mx = cx + 260; mw = cw - 300; yy = cy + 40
        for m in msgs:
            if t < m["t0"]: continue
            k = eout(lin(t, m["t0"], m["t0"] + .3))
            if m["role"] == "user":
                lines = wrap(m["text"], 19, mw * .62)
                bw = max(tw(l, 19) for l in lines) + 40; bh = len(lines) * 29 + 26
                bx = mx + mw - bw; by = yy + 14 * (1 - k)
                c2.saveLayerAlpha(None, int(255 * k))
                if m.get("attach") is not None:
                    draw_img(c2, m["attach"], mx + mw - 300, by, 300, 169, r=12)
                    rrect(c2, mx + mw - 300, by + 129, 300, 40, 0, "#000000", .55)
                    text(c2, m.get("attach_name", "video.mp4"), mx + mw - 288, by + 155, 15, "m", "#ffffff")
                    by += 185; yy += 185
                rrect(c2, bx, by, bw, bh, 18, "#3a3a36")
                for i, l in enumerate(lines): text(c2, l, bx + 20, by + 35 + i * 29, 19, "m", "#f4f3ee")
                c2.restore(); yy += bh + 26
            else:
                spark(c2, mx + 14, yy + 18, 12, "#d97757", rot=t * 1.5 if m.get("busy") else 0)
                lines = wrap(m["text"], 19, mw - 60)
                n_chars = int(max(0, t - m["t0"]) * 70); shown = 0
                for i, l in enumerate(lines):
                    if shown >= n_chars: break
                    text(c2, l[:max(0, n_chars - shown)], mx + 44, yy + 25 + i * 30, 19, "m", "#ecebe6")
                    shown += len(l)
                yy += len(lines) * 30 + 14
                for (lab, td, t1) in m.get("items", []):
                    if t < t1: continue
                    kk = eout(lin(t, t1, t1 + .25))
                    c2.saveLayerAlpha(None, int(255 * kk))
                    done = t >= td
                    if done: check(c2, mx + 58, yy + 16, 10, "#22c55e", clamp((t - td) / .2))
                    else:
                        c2.drawArc(skia.Rect.MakeXYWH(mx + 48, yy + 6, 20, 20), (t * 400) % 360, 260, False,
                                   paint(col("#d97757"), style="stroke", sw=3))
                    text(c2, lab, mx + 80, yy + 23, 18, "m", "#ecebe6" if done else "#b9b7ae")
                    c2.restore(); yy += 34
                yy += 18
        # input box
        ix, iy, iw, ih = mx, cy + ch - 120, mw, 92
        rrect(c2, ix, iy, iw, ih, 18, "#30302e"); rrect_stroke(c2, ix, iy, iw, ih, 18, "#ffffff", .12, 1.2)
        if inp:
            lines = wrap(inp, 18, iw - 60)[-2:]
            for i, l in enumerate(lines): text(c2, l, ix + 22, iy + 32 + i * 26, 18, "m", "#f4f3ee")
            if inp_caret and int(t * 2.5) % 2 == 0:
                lx = ix + 24 + tw(lines[-1], 18); c2.drawLine(lx, iy + 14 + (len(lines) - 1) * 26, lx, iy + 38 + (len(lines) - 1) * 26, paint(col("#ffffff"), style="stroke", sw=2))
        else:
            text(c2, "Reply to Claude...", ix + 22, iy + 34, 18, "m", "#8d8b84")
        text(c2, model + "  v", ix + iw - 120, iy + ih - 18, 15, "m", "#c9c7bf")
        rrect(c2, ix + iw - 44, iy + ih - 40, 32, 32, 9, "#d97757")
        if picker is not None:
            opts, sel, k = picker
            if k > 0:
                pw, ph = 300, 44 * len(opts) + 16; px, py = ix + iw - pw - 10, iy - ph - 8 + 20 * (1 - eout(k))
                c2.saveLayerAlpha(None, int(255 * clamp(k * 3)))
                panel(c2, px, py, pw, ph, 14, "#1d1d1b")
                for i, o in enumerate(opts):
                    if i == sel: rrect(c2, px + 8, py + 8 + i * 44, pw - 16, 40, 9, "#3b3b37")
                    text(c2, o, px + 24, py + 35 + i * 44, 18, "s" if i == sel else "m", "#ffffff" if i == sel else "#c9c7bf")
                    if i == sel: check(c2, px + pw - 34, py + 28 + i * 44, 9, "#d97757")
                c2.restore()
    window(c, x, y, w, h, title, a=a, sc=sc, content=f, bg=CHAT_BG)

# ---------- code editor ----------
KW = set("def return if elif else for in while import from as with class lambda and or not None True False".split())
def code_line(c, s, x, y, size=17):
    f = font("mono", size); cx = x
    toks = re.findall(r"#.*|'[^']*'|\"[^\"]*\"|\d+\.?\d*|\w+|\s+|.", s)
    for tk in toks:
        if tk.startswith("#"): cc = "#6a9955"
        elif tk[:1] in "'\"": cc = "#ce9178"
        elif re.match(r"\d", tk): cc = "#b5cea8"
        elif tk in KW: cc = "#c586c0"
        elif re.match(r"\w+", tk) and tk[0].isupper(): cc = "#4ec9b0"
        elif re.match(r"\w+", tk): cc = "#9cdcfe"
        else: cc = "#d4d4d4"
        c.drawString(tk, cx, y, f, paint(col(cc))); cx += f.measureText(tk)
def code_window(c, x, y, w, h, lines, scroll=0.0, hl=None, title="kit3.py", reveal=None, start_no=1, size=17, a=1.0, sc=1.0):
    lh = size * 1.55
    def f(c2, cx, cy, cw, ch):
        rrect(c2, cx, cy, cw, ch, 0, "#1e1e1e")
        rrect(c2, cx, cy, 56, ch, 0, "#1a1a1a")
        rrect(c2, cx + 56, cy, 180, 34, 0, "#252526"); text(c2, title, cx + 72, cy + 23, 14, "m", "#e0e0e0")
        c2.save(); c2.clipRect(skia.Rect.MakeXYWH(cx, cy + 40, cw, ch - 40))
        y0 = cy + 64 - scroll * lh; tot = 0
        for i, s in enumerate(lines):
            yy = y0 + i * lh
            if yy < cy - lh or yy > cy + ch + lh: tot += len(s); continue
            if hl and hl[0] <= i < hl[1]:
                rrect(c2, cx + 56, yy - size * 1.1, cw - 56, lh, 0, "#264f78", .55)
            text(c2, str(i + start_no), cx + 46, yy, size * .8, "m", "#5a5a5a", 1, "r")
            if reveal is not None:
                if tot >= reveal: break
                s = s[:max(0, reveal - tot)]
            code_line(c2, s, cx + 72, yy, size); tot += len(lines[i])
        c2.restore()
    window(c, x, y, w, h, title + " - Editor", a=a, sc=sc, content=f, bg="#1e1e1e")

def term_window(c, x, y, w, h, lines, t, title="Terminal", size=17, a=1.0, sc=1.0):
    """lines: list of (t_appear, text, color)"""
    lh = size * 1.6
    def f(c2, cx, cy, cw, ch):
        rrect(c2, cx, cy, cw, ch, 0, "#0d0f12")
        vis = [l for l in lines if t >= l[0]]
        maxn = int((ch - 30) // lh); vis = vis[-maxn:]
        for i, (t0, s, cc) in enumerate(vis):
            text(c2, s, cx + 20, cy + 32 + i * lh, size, "mono", cc)
        if int(t * 2.5) % 2 == 0:
            rrect(c2, cx + 20, cy + 32 + len(vis) * lh - size, size * .6, size * 1.1, 0, "#e5e5e5")
    window(c, x, y, w, h, title, a=a, sc=sc, content=f, bg="#0d0f12")

def mono_text(c, s, x, y, size, color, a=1.0):
    c.drawString(s, x, y, font("mono", size), paint(col(color, a)))

# ---------- inserted result clip (plays with its own sound; the voiceover pauses) ----------
def insert_scene(path, clip_d, label, cc="#d97757", gap=0.5):
    """window pops in, camera pushes until the video fills the frame, plays, pulls back. returns a builder tuple."""
    D = clip_d + 2 * gap
    v = Vid(path, 0.0, 1920, 1080)
    RX, RY, RW, RH = 160, 108, 1600, 900
    z = W / RW; cx, cy = RX + RW / 2, RY + RH / 2
    cam = Cam([(0, 960, 540, 1.0), (gap * .9, cx, cy, z), (D - gap * .9, cx, cy, z), (D, 960, 540, 1.0)])
    SF.append((0.0, "whoosh", .8))
    def draw(c, t):
        bg(c, "Player")
        img = v.frame(clamp((t - gap) * FPS, 0, clip_d * FPS - 1))
        def f(c2, x, y, w, h):
            rrect(c2, x, y, w, h, 0, "#000000"); draw_img(c2, img, x, y, w, h)
        window(c, RX, RY - 38, RW, RH + 38, label, content=f)
    def overlay(c, t):
        k = lin(t, gap + .2, gap + .6) * (1 - lin(t, gap + 4.5, gap + 5.0))
        if k > 0: pill(c, 50, 44, label, 28, k=min(1, k * 1.5), icon="dot", icol=cc, bgc="#111114")
    return cam, draw, [v], dict(intro=False, overlay=overlay)

def vplayer(c, x, y, w, h, img, title, prog=.3, a=1.0, sc=1.0):
    def f(c2, cx, cy, cw, ch):
        rrect(c2, cx, cy, cw, ch, 0, "#000000")
        if img is not None: draw_img(c2, img, cx, cy, cw, ch)
        c2.drawRect(skia.Rect.MakeXYWH(cx, cy + ch - 5, cw, 5), paint(col("#ffffff", .25)))
        c2.drawRect(skia.Rect.MakeXYWH(cx, cy + ch - 5, cw * clamp(prog), 5), paint(col("#ff0033")))
    window(c, x, y, w, h, title, a=a, sc=sc, content=f)

def drift(d, z0=1.0, z1=1.05, x0=960, y0=540, x1=None, y1=None):
    """slow push-in camera for a whole scene"""
    return Cam([(0, x0, y0, z0), (d, x1 if x1 else x0, y1 if y1 else y0, z1)])

def ann_circle(c, x, y, r, k, color="#ffd23f"):
    if k > 0: c.drawArc(skia.Rect.MakeXYWH(x - r, y - r, 2 * r, 2 * r), -90, 360 * eout(k), False, paint(col(color), style="stroke", sw=5))
def ann_label(c, s, x, y, k, color="#ffd23f", size=28):
    if k <= 0: return
    w = tw(s, size, "b") + 30
    with Pop(c, x, y - size - 10, w, size + 26, k):
        rrect(c, x, y - size - 10, w, size + 26, 12, "#111114", .92); rrect_stroke(c, x, y - size - 10, w, size + 26, 12, color, .9, 2)
        text(c, s, x + 15, y + 6, size, "b", color)
