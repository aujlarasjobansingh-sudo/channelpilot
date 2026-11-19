"""9:16 reel engine in the minimal light-grey step-by-step style (1080x1920, 30 fps).
Write a reel script in $TUT_ROOT that imports this module, defines frame(c, t) and calls render_reel(frame, dur, cues)."""
import sys, os, json, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, skia
from eng import font, text, tw, col, paint, rrect, rrect_stroke, shadow, cursor, click_ring, back, eout, eio, lin, clamp, mix, Vid
from comps import check, spark
W, H, FPS = 1080, 1920, 30
ROOT = os.environ.get("TUT_ROOT", os.getcwd())
BG, INK, GREY = "#f2f2f2", "#1d1d1f", "#6b6b70"

class CropVid:
    """full-bleed vertical crop of a 16:9 video; f = horizontal centre of the subject (0..1)"""
    def __init__(self, path, start, f=.5, dur=3.0):
        cw = 1080 * 9 / 16; x = clamp(f * 1920 - cw / 2, 0, 1920 - cw)
        self.p = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-ss", str(start), "-t", str(dur + .5), "-i", path, "-vf",
            f"scale=1920:1080,crop={cw:.0f}:1080:{x:.0f}:0,scale={W}:{H}:flags=bicubic,fps={FPS}", "-f", "rawvideo", "-pix_fmt", "rgba", "-"],
            stdout=subprocess.PIPE, bufsize=10 ** 8)
        self.n = -1; self.img = None
    def frame(self, i):
        while self.n < i:
            b = self.p.stdout.read(W * H * 4)
            if len(b) < W * H * 4: break
            self.img = skia.Image.fromarray(np.frombuffer(b, np.uint8).reshape(H, W, 4).copy(), colorType=skia.kRGBA_8888_ColorType); self.n += 1
        return self.img

def full_clip(c, v, t, t0):
    """draw a CropVid with a quick punch-in at the cut"""
    img = v.frame(int((t - t0) * FPS)); sc = mix(1.08, 1.0, eout(clamp((t - t0) / .12)))
    c.save(); c.translate(W / 2, H / 2); c.scale(sc, sc); c.translate(-W / 2, -H / 2)
    if img: c.drawImage(img, 0, 0)
    c.restore()

def caption_word(c, w, age, y=1340):
    """one big word, white with black outline, pops on each word"""
    f = font("d", 112); s = w.strip(",."); x = W / 2 - f.measureText(s) / 2
    sc = mix(1.25, 1.0, eout(clamp(age * 4)))
    c.save(); c.translate(W / 2, y - 40); c.scale(sc, sc); c.translate(-W / 2, -(y - 40))
    c.drawString(s, x + 4, y + 6, f, paint(col("#000000", .45)))
    c.drawString(s, x, y, f, paint(col("#000000"), style="stroke", sw=14)); c.drawString(s, x, y, f, paint(col("#ffffff")))
    c.restore()

def word_at(words, t):
    """words: [(word, start_time), ...] -> (index, word, seconds since it started) or None"""
    cur = None
    for i, (w, t0) in enumerate(words):
        if t >= t0 - .03: cur = (i, w, t - t0)
    return cur

def toptext(c, template, words, t, y0=230, big=False, maxw=960):
    """template like 'Download the free **skill** from my **channel.**' (same word count as the spoken line).
    Words appear as they are spoken; **bold** words are larger and extra-bold."""
    toks = template.split(" "); items = []
    for i, tk in enumerate(toks):
        bold = tk.startswith("**"); s = tk.strip("*")
        sz = (96 if big else 74) if bold else (60 if big else 48)
        items.append((s, bold, sz, words[min(i, len(words) - 1)][1]))
    lines, cur, cw = [], [], 0
    for it in items:
        w = tw(it[0], it[2], "x" if it[1] else "m") + 16
        if cw + w > maxw and cur: lines.append(cur); cur, cw = [], 0
        cur.append((it, w)); cw += w
    if cur: lines.append(cur)
    y = y0
    for ln in lines:
        x = W / 2 - (sum(w for _, w in ln) - 16) / 2; lh = max(it[2] for it, _ in ln)
        for (s, bold, sz, t0), w in ln:
            k = clamp((t - t0 + .05) / .18)
            if k > 0: text(c, s, x, y + lh * .5 + 8 * (1 - eout(k)), sz, "x" if bold else "m", INK, k)
            x += w
        y += lh * 1.25
    return y

def card(c, x, y, w, h, r=30, fill="#ffffff", a=1.0):
    shadow(c, x, y, w, h, r, .14 * a, 40, 18)
    rrect(c, x, y, w, h, r, fill, a); rrect_stroke(c, x, y, w, h, r, "#000000", .06 * a, 1.5)

class Pop:
    """with Pop(c, cx, cy, k): ...  springy scale-in around a centre point, k 0..1"""
    def __init__(s, c, cx, cy, k): s.c, s.cx, s.cy, s.k = c, cx, cy, k
    def __enter__(s):
        e = back(s.k, 1.6); s.c.save(); s.c.translate(s.cx, s.cy); sc = mix(.82, 1, e); s.c.scale(sc, sc); s.c.translate(-s.cx, -s.cy)
        s.c.saveLayerAlpha(None, int(255 * clamp(s.k * 2.5))); return s
    def __exit__(s, *a): s.c.restore(); s.c.restore()

def title_card(c, t, small="2D ANIMATED", big="VIDEOS"):
    c.clear(col(BG)); k = eout(clamp(t / .35))
    c.save(); c.translate(W / 2, 900); s = mix(1.15, 1, k); c.scale(s, s); c.translate(-W / 2, -900)
    text(c, small, W / 2, 840, 56, "m", "#8e8e93", k, "c"); text(c, big, W / 2, 990, 170, "x", INK, k, "c")
    c.restore()

def file_icon(c, x, y, s=1.0, top="#4f7bf0", bottom="#2c55c9"):
    """generic zip/file icon"""
    c.save(); c.translate(x, y); c.scale(s, s)
    p = skia.Path(); p.moveTo(-70, -90); p.lineTo(40, -90); p.lineTo(70, -60); p.lineTo(70, 90); p.lineTo(-70, 90); p.close()
    c.drawPath(p, skia.Paint(AntiAlias=True, Shader=skia.GradientShader.MakeLinear([(0, -90), (0, 90)], [col(top), col(bottom)])))
    for i in range(7): rrect(c, -8 + (8 if i % 2 else 0) - 4, -80 + i * 16, 12, 9, 2, "#ffffff", .9)
    rrect(c, -14, 34, 28, 34, 6, "#ffffff"); rrect(c, -8, 44, 16, 14, 3, bottom)
    c.restore()

def progress_card(c, t, t0, name, y=1250, size_kb=52):
    k = lin(t, t0, t0 + .3)
    if k <= 0: return
    with Pop(c, W / 2, y + 90, k):
        card(c, 160, y, 760, 180, 26); file_icon(c, 250, y + 90, .62)
        text(c, name, 320, y + 74, 28, "b", INK)
        pr = eio(lin(t, t0 + .25, t0 + 1.2))
        rrect(c, 320, y + 104, 520, 14, 7, "#e5e5ea"); rrect(c, 320, y + 104, 520 * pr, 14, 7, "#3b82f6")
        text(c, "Download complete" if pr >= 1 else f"Downloading...  {int(pr * size_kb)} KB", 320, y + 150, 22, "m", GREY)
        if pr >= 1: check(c, 870, y + 90, 26, "#22c55e", clamp((t - t0 - 1.2) / .2))

def render_reel(frame, dur, out, vo_wav, cues=(), music_db=-27, clips_audio=()):
    """frame(c, t) draws one frame. cues: [(t, 'click'|'pop'|'whoosh'|'whoosh_s'|'type'|'ding'|'rise', gain)]"""
    from audio import build
    n = int(dur * FPS); tmp = out[:-4] + "_v.tmp.mp4"
    p = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", tmp], stdin=subprocess.PIPE)
    surf = skia.Surface(W, H)
    for i in range(n):
        cc = surf.getCanvas(); cc.clear(col("#000000")); frame(cc, i / FPS)
        p.stdin.write(surf.makeImageSnapshot().toarray(colorType=skia.kBGRA_8888_ColorType).tobytes())
    p.stdin.close(); assert p.wait() == 0
    aw = out[:-4] + "_a.wav"
    build(dur, [(0, vo_wav, 0, dur)], list(cues), aw, music_ranges=[(0, dur)] if music_db is not None else None, music_db=music_db or -30, clips_audio=clips_audio)
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", tmp, "-i", aw, "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                    "-shortest", "-movflags", "+faststart", out], check=True)
    for f in (tmp, aw, aw + ".raw.wav"):
        if os.path.exists(f): os.remove(f)
    print("done:", out)

def reel_still(frame, ts, prefix):
    surf = skia.Surface(W, H)
    for t in ts:
        cc = surf.getCanvas(); cc.clear(col("#000000")); frame(cc, t); surf.makeImageSnapshot().save(f"{prefix}_{t:05.2f}.png")
