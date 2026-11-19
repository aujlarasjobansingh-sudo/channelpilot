"""povXOfficial promo reel: "I built a skill that makes this exact style" (9:16, aivxer reel editing style).
Run:  TUT_ROOT=<this folder> python3 promo.py [still t1,t2,...]
"""
import os, sys, re, subprocess, json
HERE = os.path.dirname(os.path.abspath(__file__)); os.environ.setdefault('TUT_ROOT', HERE)
sys.path.insert(0, os.path.join(HERE, 'scripts'))
from reel import *                      # W, H, FPS, BG, INK, GREY, card, Pop, title_card, toptext, caption_word, word_at, file_icon
from eng import load_img, draw_img, draw_img_cover, cursor, click_ring, Path2
from comps import pill, check, spark
import numpy as np, soundfile as sf, skia

A = lambda p: os.path.join(HERE, 'assets', p)
# ------------------------------------------------------------------ voice timeline
VO = [('v1', 3.05), ('v2', 7.2), ('v3', 10.5), ('v4', 15.65), ('v5', 20.05), ('v6', 24.45), ('v7', 29.05), ('v8', 33.75)]
TEXT = {
    'v1': 'Want to make videos in this exact style? I built a skill for it.',
    'v2': 'Step one: give Claude a single reference video.',
    'v3': 'It studies every scene: the lens, the camera moves, the timing.',
    'v4': 'Then it rebuilds the whole world in 3D, scene by scene.',
    'v5': 'It matches the movement frame by frame, so it feels the same.',
    'v6': 'And I packed it all into one skill. Any story, same style.',
    'v7': "Here's the reference... and here's ours.",
    'v8': "Comment SKILL and I'll send you the link.",
}
DUR = 38.0
WORDS, LINE_END = {}, {}
def voiced_span(wav):
    a, sr = sf.read(wav); e = np.where(np.abs(a) > 0.03)[0]; return e[0] / sr, e[-1] / sr, len(a) / sr
for k, t0 in VO:
    v0, v1, d = voiced_span(os.path.join(HERE, 'vo', k + '.wav'))
    ws = TEXT[k].split(' '); wt = [max(2, len(re.sub(r'[^A-Za-z0-9]', '', w))) + 1.5 for w in ws]
    tot = sum(wt); cur = t0 + v0; lst = []
    for w, x in zip(ws, wt): lst.append((w, cur)); cur += (v1 - v0) * x / tot
    WORDS[k] = lst; LINE_END[k] = t0 + d

def wt(k, i): return WORDS[k][i][1]          # start time of word i in line k

# ------------------------------------------------------------------ video sources (9:16 sources, scaled to fill)
class FullVid:
    def __init__(self, path, start, w=W, h=H, dur=4.5):
        self.w, self.h = w, h
        self.p = subprocess.Popen(['ffmpeg', '-loglevel', 'error', '-ss', str(start), '-t', str(dur), '-i', path, '-vf',
                                   f'scale={w}:{h}:flags=bicubic,fps={FPS}', '-f', 'rawvideo', '-pix_fmt', 'rgba', '-'], stdout=subprocess.PIPE, bufsize=10 ** 8)
        self.n = -1; self.img = None
    def frame(self, i):
        while self.n < i:
            b = self.p.stdout.read(self.w * self.h * 4)
            if len(b) < self.w * self.h * 4: break
            self.img = skia.Image.fromarray(np.frombuffer(b, np.uint8).reshape(self.h, self.w, 4).copy(), colorType=skia.kRGBA_8888_ColorType); self.n += 1
        return self.img

HOOK = FullVid(A('reference.mp4'), 39.6, dur=3.2)
CMP_W, CMP_H = 468, 832
CMP_REF = FullVid(A('reference.mp4'), 0.0, CMP_W, CMP_H, 4.6)
CMP_OUR = FullVid(A('ours_preview.mp4'), 0.0, CMP_W, CMP_H, 4.6)
END1 = FullVid(A('episode1.mp4'), 47.0, dur=1.2)      # Maya close-up
END2 = FullVid(A('episode1.mp4'), 108.8, dur=1.4)     # cold stare + knife
THUMBS = [load_img(A(f'thumb_{t}.png')) for t in ('1.2', '12', '42', '70', '100', '108')]
OURS = load_img(A('ours_still.png'))

def draw_full(c, v, t, t0):
    img = v.frame(int((t - t0) * FPS)); sc = mix(1.08, 1.0, eout(clamp((t - t0) / .12)))
    c.save(); c.translate(W / 2, H / 2); c.scale(sc, sc); c.translate(-W / 2, -H / 2)
    if img: c.drawImage(img, 0, 0)
    c.restore()

def label(c, s, x, y, bgc='#ffffff', fg=INK, size=30, k=1.0):
    pill(c, x, y, s, size, fg=fg, bgc=bgc, k=k, align='c')

# real measured camera motion (optical flow, cumulative vertical px) — reference vs ours
def load_motion(p):
    rows = [[float(x) for x in re.findall(r'-?\d+\.\d+', l)] for l in open(p)]
    return np.array([[r[0], r[6]] for r in rows if len(r) >= 7])
MREF, MOUR = load_motion(A('m_ref.txt')), load_motion(A('m_new.txt'))

CODE = ['const lens = stereographic(540);', "K(2.48, 3.0, { pitch: -47 });", 'buildRoom(); buildDesks();', 'student(0.19, -1.25, { hood });',
        'teacher(-1.2, -5.0);', 'renderFrame();']

# ------------------------------------------------------------------ frame
def seg_v1(c, t):
    if t < 3.8: title_card(c, t - 3.0, 'POV ANIMATED', 'VIDEOS'); return
    c.clear(col(BG))
    if t < wt('v1', 8) - .05:
        toptext(c, 'Want to make **videos** in this **exact** **style?**', WORDS['v1'][:8], t, y0=560, big=True)
        for i, img in enumerate((THUMBS[0], THUMBS[2])):
            k = clamp((t - 3.85 - i * .15) / .3)
            if k > 0:
                with Pop(c, 300 + i * 480, 1250, k): draw_img(c, img, 170 + i * 480, 1000, 260, 462, 1, 24)
        return
    ws = WORDS['v1'][8:]
    toptext(c, 'I built a **skill** for **it.**', ws, t, y0=520, big=True)
    k = clamp((t - wt('v1', 11)) / .35)
    if k > 0:
        with Pop(c, W / 2, 1150, k):
            card(c, 300, 960, 480, 380, 40); spark(c, W / 2, 1110, 92, '#d97757', t * 0.6)
            text(c, 'pov-animation', W / 2, 1270, 40, 'x', INK, 1, 'c')

def seg_v2(c, t):
    c.clear(col(BG))
    toptext(c, 'Step one: give **Claude** a single **reference** **video.**', WORDS['v2'], t)
    k = clamp((t - 7.35) / .3)
    with Pop(c, W / 2, 1100, k):
        card(c, 120, 640, 840, 900, 40)
        text(c, 'Claude', 170, 715, 34, 'x', INK); spark(c, 880, 700, 22, '#d97757')
        c.drawLine(120, 750, 960, 750, paint(col('#000000', .06)))
        kt = clamp((t - wt('v2', 6)) / .4)          # reference thumbnail drops in on "reference"
        if kt > 0:
            y = mix(560, 800, eout(kt))
            draw_img(c, THUMBS[0], 360, y, 360, 640 * .78, kt, 26)
            label(c, 'REFERENCE', W / 2, y + 40, '#1d1d1f', '#ffffff', 26, kt)
        pr = eio(lin(t, wt('v2', 7), wt('v2', 7) + 1.0))
        if pr > 0:
            rrect(c, 200, 1380, 680, 16, 8, '#e5e5ea'); rrect(c, 200, 1380, 680 * pr, 16, 8, '#3b82f6')
            text(c, 'reference_video.mp4  ·  uploaded' if pr >= 1 else f'Uploading...  {int(pr * 100)}%', 200, 1440, 28, 'm', GREY)
            if pr >= 1: check(c, 900, 1388, 26, '#22c55e', clamp((t - wt('v2', 7) - 1.0) / .2))

def seg_v3(c, t):
    c.clear(col(BG))
    toptext(c, 'It studies **every** **scene:** the **lens,** the **camera** **moves,** the **timing.**', WORDS['v3'], t)
    for i, img in enumerate(THUMBS):
        k = clamp((t - 10.6 - i * .08) / .3); x = 120 + (i % 3) * 290; y = 500 + (i // 3) * 460
        if k <= 0: continue
        with Pop(c, x + 125, y + 220, k):
            draw_img(c, img, x, y, 250, 444, 1, 22)
            sc = (t * 0.9 + i * .17) % 1       # scan line = "studying"
            if t < LINE_END['v3']: rrect(c, x, y + 444 * sc, 250, 4, 2, '#3b82f6', .8)
    for word_i, s, y in ((5, '122° LENS', 1460), (8, 'PAN · TILT · HOLD', 1545), (10, '0.65 s  ·  0.5 s', 1630)):
        k = clamp((t - wt('v3', word_i)) / .3)
        if k > 0: pill(c, W / 2, y, s, 36, fg='#ffffff', bgc='#1d1d1f', k=k, icon='check', icol='#22c55e', align='c')

def seg_v4(c, t):
    c.clear(col(BG))
    toptext(c, 'Then it rebuilds the **whole** **world** in **3D,** scene by scene.', WORDS['v4'], t)
    k = clamp((t - 15.75) / .3)
    with Pop(c, W / 2, 760, k):
        card(c, 100, 520, 880, 470, 30, '#141418')
        for i, ln in enumerate(CODE):
            n = int(clamp((t - 15.9 - i * .38) / .32) * len(ln))
            if n > 0: text(c, ln[:n], 150, 600 + i * 64, 30, 'mono', '#7dd3fc' if i % 2 == 0 else '#e4e4e7')
    k2 = clamp((t - wt('v4', 7)) / .35)
    if k2 > 0:
        with Pop(c, W / 2, 1420, k2):
            card(c, 250, 1060, 580, 720, 34); draw_img_cover(c, OURS, 270, 1080, 540, 680, 1, 24, 0.5, 0.45)
            label(c, '3D SCENE', W / 2, 1110, '#1d1d1f', '#ffffff', 26)

def seg_v5(c, t):
    c.clear(col(BG))
    toptext(c, 'It matches the **movement** frame by frame, so it **feels** **the** **same.**', WORDS['v5'], t)
    k = clamp((t - 20.15) / .3)
    with Pop(c, W / 2, 1050, k):
        card(c, 90, 640, 900, 820, 36)
        text(c, 'CAMERA MOVEMENT', 150, 720, 30, 'x', GREY)
        x0, x1, y0, y1 = 150, 930, 820, 1360
        c.drawLine(x0, y1, x1, y1, paint(col('#000000', .12), style='stroke', sw=3))
        prog = clamp((t - 20.4) / 2.6)
        def curve(m, color, sw):
            p = skia.Path(); first = True
            for tt, cy in m:
                if tt > 4 * prog: break
                x = x0 + (x1 - x0) * tt / 4; y = y0 + (y1 - y0) * (1 - (cy + 480) / 500)
                (p.moveTo if first else p.lineTo)(x, y); first = False
            c.drawPath(p, paint(col(color), style='stroke', sw=sw))
        curve(MREF, '#8e8e93', 14); curve(MOUR, '#ef4444', 6)
        rrect(c, 150, 1395, 34, 12, 6, '#8e8e93'); text(c, 'Reference', 200, 1410, 30, 'm', GREY)
        rrect(c, 470, 1395, 34, 12, 6, '#ef4444'); text(c, 'Ours', 520, 1410, 30, 'm', GREY)
    k3 = clamp((t - wt('v5', 11)) / .3)
    if k3 > 0: pill(c, W / 2, 1600, 'MATCHED', 50, fg='#ffffff', bgc='#16a34a', k=k3, icon='check', icol='#ffffff', align='c')

def seg_v6(c, t):
    c.clear(col(BG))
    toptext(c, 'And I packed it all into **one** **skill.** Any **story,** same **style.**', WORDS['v6'], t)
    k = clamp((t - wt('v6', 6)) / .35)
    if k > 0:
        with Pop(c, W / 2, 900, k):
            card(c, 240, 660, 600, 520, 40); file_icon(c, W / 2, 860, 1.25, '#ef4444', '#b91c1c')
            text(c, 'pov-animation.skill', W / 2, 1110, 40, 'x', INK, 1, 'c')
    for i, s in enumerate(['3D SCENES', 'CAMERA MOVES', 'VOICES', 'SFX', 'SUBTITLES']):
        kk = clamp((t - wt('v6', 8) - i * .16) / .3)
        if kk > 0: pill(c, 270 + (i % 2) * 540 if i < 4 else W / 2, 1300 + (i // 2) * 105, s, 38, fg='#ffffff', bgc='#1d1d1f', k=kk, icon='check', icol='#22c55e', align='c')
    kc = clamp((t - wt('v6', 11) - .1) / .25)
    if kc > 0: check(c, 790, 700, 40, '#22c55e', kc)

def seg_v7(c, t):
    c.clear(col(BG))
    toptext(c, "Here's the **reference...** and here's **ours.**", WORDS['v7'], t, y0=230, big=True)
    for i, (v, lab, tw0) in enumerate(((CMP_REF, 'REFERENCE', wt('v7', 2)), (CMP_OUR, 'OURS', wt('v7', 5)))):
        k = clamp((t - tw0 + .1) / .3)
        if k <= 0: continue
        x = 48 + i * (CMP_W + 48); y = 560
        with Pop(c, x + CMP_W / 2, y + CMP_H / 2, k):
            shadow(c, x, y, CMP_W, CMP_H, 30, .25, 40, 18)
            img = v.frame(int(max(0, t - 29.6) * FPS))
            if img: draw_img(c, img, x, y, CMP_W, CMP_H, 1, 30)
            rrect_stroke(c, x, y, CMP_W, CMP_H, 30, '#000000', .1, 2)
            label(c, lab, x + CMP_W / 2, y + CMP_H + 70, '#ef4444' if i else '#1d1d1f', '#ffffff', 34)

def seg_end(c, t):
    if t < 35.85:
        v, t0 = (END1, 33.75) if t < 34.8 else (END2, 34.8)
        draw_full(c, v, t, t0)
        w = word_at(WORDS['v8'][:2], t)
        if w: caption_word(c, w[1].upper().strip('.'), w[2])
        return
    title_card(c, t - 35.85, 'COMMENT', '"SKILL"')
    k = clamp((t - 36.15) / .3)
    if k > 0:
        pill(c, W / 2, 1180, "I'LL SEND YOU THE LINK", 44, fg='#ffffff', bgc='#ef4444', k=k, align='c')
        text(c, '@povXOfficial', W / 2, 1330, 44, 'x', GREY, k, 'c')

def frame(c, t):
    if t < 3.0:
        draw_full(c, HOOK, t, 0)
        pill(c, 160, 180, 'REFERENCE', 30, fg='#ffffff', bgc='#1d1d1f', k=1, align='c')
    elif t < 7.2: seg_v1(c, t)
    elif t < 10.5: seg_v2(c, t)
    elif t < 15.65: seg_v3(c, t)
    elif t < 20.05: seg_v4(c, t)
    elif t < 24.45: seg_v5(c, t)
    elif t < 29.05: seg_v6(c, t)
    elif t < 33.75: seg_v7(c, t)
    else: seg_end(c, t)

# ------------------------------------------------------------------ sound cues + render
CUES = [(t, 'whoosh', .9) for t in (3.0, 7.2, 10.5, 15.65, 20.05, 24.45, 29.05, 33.75, 34.8, 35.85)]
CUES += [(3.85, 'pop', .8), (4.0, 'pop', .8), (7.35, 'pop', 1), (wt('v2', 6), 'pop', 1), (wt('v2', 7) + 1.0, 'ding', .8), (wt('v1', 11), 'pop', 1)]
CUES += [(10.6 + i * .08, 'pop', .6) for i in range(6)] + [(wt('v3', i), 'pop', .9) for i in (5, 8, 10)]
CUES += [(15.75, 'pop', 1)] + [(15.9 + i * .38 + j * .06, 'type', .5) for i in range(len(CODE)) for j in range(5)] + [(wt('v4', 7), 'pop', 1)]
CUES += [(20.15, 'pop', 1), (20.4, 'rise', .7), (wt('v5', 11), 'ding', 1)]
CUES += [(wt('v6', 6), 'pop', 1)] + [(wt('v6', 8) + i * .16, 'pop', .7) for i in range(5)] + [(wt('v6', 11) + .1, 'ding', 1)]
CUES += [(wt('v7', 2) - .1, 'pop', 1), (wt('v7', 5) - .1, 'pop', 1), (36.15, 'pop', 1), (36.2, 'ding', .8)]

if __name__ == '__main__':
    if len(sys.argv) > 2 and sys.argv[1] == 'still':
        os.makedirs(os.path.join(HERE, 'shots'), exist_ok=True)
        reel_still(frame, [float(x) for x in sys.argv[2].split(',')], os.path.join(HERE, 'shots', 'rs')); sys.exit()
    # voice track
    v = np.zeros(int(DUR * 48000), np.float32)
    for k, t0 in VO:
        a, sr = sf.read(os.path.join(HERE, 'vo', k + '.wav'), dtype='float32'); i = int(t0 * sr); v[i:i + len(a)] += a[:len(v) - i]
    vo_wav = os.path.join(HERE, 'out', 'vo_full.wav'); os.makedirs(os.path.dirname(vo_wav), exist_ok=True); sf.write(vo_wav, v, 48000)
    from audio import build
    out = os.path.join(HERE, 'out', 'skill_promo_reel.mp4'); n = int(DUR * FPS); tmp = out[:-4] + '_v.tmp.mp4'
    p = subprocess.Popen(['ffmpeg', '-loglevel', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgra', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                          '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-pix_fmt', 'yuv420p', tmp], stdin=subprocess.PIPE)
    surf = skia.Surface(W, H)
    for i in range(n):
        cc = surf.getCanvas(); cc.clear(col('#000000')); frame(cc, i / FPS)
        p.stdin.write(surf.makeImageSnapshot().toarray(colorType=skia.kBGRA_8888_ColorType).tobytes())
    p.stdin.close(); assert p.wait() == 0
    aw = out[:-4] + '_a.wav'
    build(DUR, [(0, vo_wav, 0, DUR)], CUES, aw, music_ranges=None, clips_audio=[(0, A('hook_audio.wav'), -4)])
    subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', tmp, '-i', aw, '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k',
                    '-shortest', '-movflags', '+faststart', out], check=True)
    for f in (tmp, aw, aw + '.raw.wav'):
        if os.path.exists(f): os.remove(f)
    print('done:', out)
