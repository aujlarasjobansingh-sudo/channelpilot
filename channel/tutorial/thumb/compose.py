# Rebuild the thumbnail: same layout, new panel images, new headline. Person stays on top.
import skia, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
def P(p): return os.path.join(HERE, p)
HEADLINE = sys.argv[1] if len(sys.argv) > 1 else "CLAUDE MADE THE SAME!"
GOLD_WORDS = int(sys.argv[2]) if len(sys.argv) > 2 else 1     # how many leading words are gold
OUT = sys.argv[3] if len(sys.argv) > 3 else "thumbnail.png"

base = skia.Image.open(P('base.png')); W, H = base.width(), base.height()
mask = skia.Image.open(P('mask.png'))
surf = skia.Surface(W, H); c = surf.getCanvas(); c.drawImage(base, 0, 0)
S = skia.SamplingOptions(skia.FilterMode.kLinear, skia.MipmapMode.kLinear)

def panel(img_path, rect, r, src_pt=None, dst_pt=None, scale=None):
    img = skia.Image.open(P(img_path)); iw, ih = img.width(), img.height()
    x0, y0, x1, y1 = rect; w, h = x1 - x0, y1 - y0
    smin = max(w / iw, h / ih); s = max(scale or smin, smin)
    if src_pt is None: sx, sy = iw / 2, ih / 2; dx, dy = x0 + w / 2, y0 + h / 2
    else: (sx, sy), (dx, dy) = src_pt, dst_pt
    left = sx - (dx - x0) / s; top = sy - (dy - y0) / s
    left = min(max(left, 0), iw - w / s); top = min(max(top, 0), ih - h / s)   # keep the whole panel covered
    c.save(); c.clipRRect(skia.RRect.MakeRectXY(skia.Rect(x0, y0, x1, y1), r, r), True)
    c.drawImageRect(img, skia.Rect(left, top, left + w / s, top + h / s), skia.Rect(x0, y0, x1, y1), S)
    c.restore()

panel('doom_island.jpg', (36, 198, 684, 507), 20, (640, 300), (360, 352))
panel('cand/c_12.95.png', (986, 193, 1642, 505), 20)
panel('cand/c_70.5.png', (30, 545, 684, 894), 20, (960, 650), (300, 700), .42)
panel('cand/c_262.5.png', (1046, 543, 1644, 895), 20, (1480, 520), (1430, 700), .42)

# small honesty tag on the other creator's thumbnail
def tag(x, y, s, bgc, fg=skia.ColorWHITE, size=30):
    f = skia.Font(skia.Typeface.MakeFromFile(os.path.expanduser('~/vid/fonts/Anton-Regular.ttf')), size)
    tw = f.measureText(s); rr = skia.RRect.MakeRectXY(skia.Rect(x, y, x + tw + 28, y + size + 18), 10, 10)
    c.drawRRect(rr, skia.Paint(AntiAlias=True, Color=bgc)); c.drawString(s, x + 14, y + size + 6, f, skia.Paint(AntiAlias=True, Color=fg))
tag(52, 455, "ORIGINAL", skia.Color(200, 30, 40))

# headline: clear the old text, draw the new one in the same gold + white style
c.save(); c.clipRect(skia.Rect(0, 0, W, 180))
c.drawPaint(skia.Paint(Shader=skia.GradientShader.MakeRadial((W / 2, 40), W * .7, [skia.Color(26, 20, 30), skia.Color(6, 6, 10)])))
c.restore()
c.drawRect(skia.Rect(0, 160, W, 186), skia.Paint(Shader=skia.GradientShader.MakeLinear([(0, 160), (0, 186)], [skia.Color(6, 6, 10, 255), skia.Color(6, 6, 10, 0)])))
tf = skia.Typeface.MakeFromFile(os.path.expanduser('~/vid/fonts/Anton-Regular.ttf'))
words = HEADLINE.split(" ")
size = 160
while True:
    f = skia.Font(tf, size); total = f.measureText(HEADLINE)
    if total <= 1520 or size < 60: break
    size -= 4
f = skia.Font(tf, size); total = f.measureText(HEADLINE)
x = (W - total) / 2; base_y = 32 + size * .82
gold_s = " ".join(words[:GOLD_WORDS]) + " "; white_s = " ".join(words[GOLD_WORDS:])
gw = f.measureText(gold_s)
def draw_text(s, x, shader, glow):
    blob = skia.TextBlob(s, f)
    gp = skia.Paint(AntiAlias=True, Color=glow); gp.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 18)); c.drawTextBlob(blob, x, base_y, gp)
    sh = skia.Paint(AntiAlias=True, Color=skia.Color(0, 0, 0, 200)); c.drawTextBlob(blob, x + 5, base_y + 7, sh)
    st = skia.Paint(AntiAlias=True, Color=skia.Color(40, 22, 4), Style=skia.Paint.kStroke_Style, StrokeWidth=9, StrokeJoin=skia.Paint.kRound_Join); c.drawTextBlob(blob, x, base_y, st)
    fp = skia.Paint(AntiAlias=True); fp.setShader(shader); c.drawTextBlob(blob, x, base_y, fp)
top, bot = base_y - size * .78, base_y
draw_text(gold_s, x, skia.GradientShader.MakeLinear([(0, top), (0, bot)], [skia.Color(255, 244, 160), skia.Color(255, 200, 40), skia.Color(214, 130, 10)], [0, .5, 1]), skia.Color(255, 170, 30, 170))
draw_text(white_s, x + gw, skia.GradientShader.MakeLinear([(0, top), (0, bot)], [skia.Color(255, 255, 255), skia.Color(232, 232, 236), skia.Color(170, 172, 182)], [0, .55, 1]), skia.Color(255, 255, 255, 90))

# person back on top (from the original, with its rim glow)
lay = skia.Surface(W, H); lc = lay.getCanvas(); lc.drawImage(base, 0, 0)
mp = skia.Paint(); mp.setBlendMode(skia.BlendMode.kDstIn)
mimg = mask.makeRasterImage()
arr = mimg.toarray(colorType=skia.kRGBA_8888_ColorType); arr[..., 3] = arr[..., 0]
lc.drawImage(skia.Image.fromarray(arr, colorType=skia.kRGBA_8888_ColorType), 0, 0, skia.SamplingOptions(), mp)
c.drawImage(lay.makeImageSnapshot(), 0, 0)
surf.makeImageSnapshot().save(P(OUT), skia.kPNG); print('saved', OUT)
