"""Shorts tutorial: install the POV skill in Claude + add an ElevenLabs API key (9:16, aivxer reel editing style).
Run: python3 tutorial.py [still t1,t2,...]   -> out/skill_tutorial.mp4
App screens are simplified drawings (no real logos). Check the menu paths match the live apps before posting.
"""
import os, sys, re, subprocess
HERE = os.path.dirname(os.path.abspath(__file__)); os.environ.setdefault('TUT_ROOT', HERE)
sys.path.insert(0, os.path.join(HERE, 'scripts'))
from reel import *
from eng import draw_img, cursor, click_ring, Path2
from comps import pill, check, spark
import numpy as np, soundfile as sf, skia

A = lambda p: os.path.join(HERE, 'assets', p)
VO = [('v1', 0.25), ('v2', 5.1), ('v3', 7.3), ('v4', 13.1), ('v5', 21.1), ('v6', 28.1), ('v7', 36.1)]
TEXT = {'v1': "Claude made this entire horror short. Here's how you can too.", 'v2': 'Step one: download the skill.',
        'v3': 'Step two: in Claude, open Customize, then Skills, and upload the zip.',
        'v4': 'Step three: for the voices, go to ElevenLabs, open API Keys, and create a key with text to speech turned on.',
        'v5': 'Step four: when Claude asks for the key, paste it into the secure form. Never into the chat.',
        'v6': 'Now just type your topic. Claude writes the script, shows you a preview, and builds the full video.',
        'v7': "Comment SKILL and I'll send you the link."}
DUR = 40.0
WORDS = {}
for k, t0 in VO:
    a, sr = sf.read(os.path.join(HERE, 'vo', k + '.wav')); e = np.where(np.abs(a) > 0.03)[0]; v0, v1 = e[0] / sr, e[-1] / sr
    ws = TEXT[k].split(' '); wt_ = [max(2, len(re.sub(r'[^A-Za-z0-9]', '', w))) + 1.5 for w in ws]; tot = sum(wt_); cur = t0 + v0; lst = []
    for w, x in zip(ws, wt_): lst.append((w, cur)); cur += (v1 - v0) * x / tot
    WORDS[k] = lst
wt = lambda k, i: WORDS[k][i][1]

class FullVid:
    def __init__(self, path, start, w=W, h=H, dur=3.0):
        self.w, self.h = w, h
        self.p = subprocess.Popen(['ffmpeg', '-loglevel', 'error', '-ss', str(start), '-t', str(dur), '-i', path, '-vf', f'scale={w}:{h}:flags=bicubic,fps={FPS}',
                                   '-f', 'rawvideo', '-pix_fmt', 'rgba', '-'], stdout=subprocess.PIPE, bufsize=10 ** 8)
        self.n = -1; self.img = None
    def frame(self, i):
        while self.n < i:
            b = self.p.stdout.read(self.w * self.h * 4)
            if len(b) < self.w * self.h * 4: break
            self.img = skia.Image.fromarray(np.frombuffer(b, np.uint8).reshape(self.h, self.w, 4).copy(), colorType=skia.kRGBA_8888_ColorType); self.n += 1
        return self.img
HOOK = [FullVid(A('ep2.mp4'), 6.6, dur=1.6), FullVid(A('ep2.mp4'), 20.0, dur=1.6), FullVid(A('ep2.mp4'), 50.0, dur=1.6)]
RES = FullVid(A('ep2.mp4'), 18.0, 600, 1066, 8.5)
END = [FullVid(A('ep2.mp4'), 70.4, dur=1.3), FullVid(A('ep2.mp4'), 74.6, dur=1.3)]
def full(c, v, t, t0):
    img = v.frame(int((t - t0) * FPS)); sc = mix(1.08, 1.0, eout(clamp((t - t0) / .12)))
    c.save(); c.translate(W / 2, H / 2); c.scale(sc, sc); c.translate(-W / 2, -H / 2)
    if img: c.drawImage(img, 0, 0)
    c.restore()

def mock_window(c, x, y, w, h, title, dark=False):
    card(c, x, y, w, h, 34, '#1b1c22' if dark else '#ffffff')
    rrect(c, x, y, w, 70, 34, '#e9e9ee' if not dark else '#26272e'); c.drawRect(skia.Rect.MakeXYWH(x, y + 40, w, 30), paint(col('#e9e9ee' if not dark else '#26272e')))
    for i, cc in enumerate(('#ff5f57', '#febc2e', '#28c840')): c.drawCircle(x + 36 + i * 28, y + 35, 9, paint(col(cc)))
    text(c, title, x + w / 2, y + 45, 26, 'm', GREY if not dark else '#a1a1aa', 1, 'c')

def row(c, x, y, w, label, k_hi=0.0, icon=None):
    if k_hi > 0: rrect(c, x, y - 34, w, 56, 14, '#d97757', .18 * k_hi)
    text(c, label, x + 22, y + 4, 32, 'b' if k_hi > .5 else 'm', INK)

def toggle(c, x, y, on):
    rrect(c, x, y, 76, 42, 21, '#22c55e' if on > .5 else '#d4d4d8'); c.drawCircle(x + 21 + 34 * on, y + 21, 17, paint(col('#ffffff')))

# ------------------------------------------------------------------ segments
def seg_hook(c, t):
    i = 0 if t < 1.45 else 1 if t < 2.9 else 2; t0 = (0, 1.45, 2.9)[i]
    full(c, HOOK[i], t, t0)
    w = word_at(WORDS['v1'][:6], t)
    if w: caption_word(c, w[1].upper().strip('.'), w[2])

def seg_v1b(c, t):     # "Here's how you can too." on the title card
    if t < 4.4:
        full(c, HOOK[2], t, 2.9); w = word_at(WORDS['v1'], t)
        if w: caption_word(c, w[1].upper().strip('.'), w[2])
        return
    title_card(c, t - 4.4, 'POV ANIMATED', 'VIDEOS')

def seg_v2(c, t):
    c.clear(col(BG)); toptext(c, 'Step one: **download** the **skill.**', WORDS['v2'], t)
    progress_card(c, t, 5.5, 'pov-3d-animation-aivxer.zip', y=860, size_kb=78)

def seg_v3(c, t):
    c.clear(col(BG)); toptext(c, 'Step two: in **Claude,** open **Customize,** then **Skills,** and **upload** the zip.', WORDS['v3'], t)
    k = clamp((t - 7.45) / .3)
    with Pop(c, W / 2, 1050, k):
        mock_window(c, 90, 620, 900, 860, 'Claude')
        spark(c, 170, 760, 26, '#d97757'); text(c, 'Claude', 215, 772, 34, 'x', INK)
        h_c = clamp((t - wt('v3', 6)) / .2); h_s = clamp((t - wt('v3', 8)) / .2)
        row(c, 130, 870, 300, 'Chats'); row(c, 130, 950, 300, 'Projects'); row(c, 130, 1030, 300, 'Customize', h_c)
        if h_c > 0:
            row(c, 470, 870, 480, 'Connectors'); row(c, 470, 950, 480, 'Skills', h_s); row(c, 470, 1030, 480, 'Styles')
        if h_s > 0:
            ku = clamp((t - wt('v3', 10)) / .3)
            rrect(c, 470, 1110, 480, 92, 22, '#1d1d1f', h_s); text(c, '+  Upload a skill', 710, 1168, 32, 'b', '#ffffff', h_s, 'c')
            if ku > 0:
                pr = eio(lin(t, wt('v3', 10), wt('v3', 10) + 1.1))
                rrect(c, 470, 1250, 480, 120, 22, '#f4f4f5'); file_icon(c, 530, 1310, .38)
                text(c, 'pov-3d-animation-aivxer.zip', 580, 1300, 24, 'b', INK); rrect(c, 580, 1325, 330, 10, 5, '#e5e5ea'); rrect(c, 580, 1325, 330 * pr, 10, 5, '#3b82f6')
                text(c, 'Skill added' if pr >= 1 else 'Uploading...', 580, 1362, 22, 'm', '#16a34a' if pr >= 1 else GREY)
                if pr >= 1: check(c, 920, 1310, 22, '#22c55e', clamp((t - wt('v3', 10) - 1.1) / .2))
        path = Path2([(7.6, 600, 1400), (wt('v3', 6) - .15, 260, 1035), (wt('v3', 8) - .15, 620, 955), (wt('v3', 10) - .15, 700, 1160), (13.0, 760, 1300)])
        x, y = path.at(t); press = max(clamp(1 - abs(t - wt('v3', i) + .02) / .08) for i in (6, 8, 10)); cursor(c, x, y, 1.6, press)
        for i in (6, 8, 10): click_ring(c, x, y, (t - wt('v3', i) + .02) / .35)

def seg_v4(c, t):
    c.clear(col(BG)); toptext(c, 'Step three: for the voices, go to **ElevenLabs,** open **API Keys,** and create a key with **text to speech** turned on.', WORDS['v4'], t, y0=200, maxw=1000)
    k = clamp((t - 13.25) / .3)
    with Pop(c, W / 2, 1150, k):
        mock_window(c, 90, 720, 900, 880, 'elevenlabs.io  ·  API Keys', dark=True)
        text(c, 'API Keys', 150, 850, 40, 'x', '#ffffff')
        kc = clamp((t - wt('v4', 14)) / .25)
        rrect(c, 690, 805, 250, 70, 18, '#ffffff', 1); text(c, '+ Create key', 815, 850, 28, 'b', INK, 1, 'c')
        if kc > 0:
            rrect(c, 140, 910, 800, 470, 24, '#26272e', kc)
            text(c, 'Permissions', 180, 975, 30, 'b', '#e4e4e7', kc)
            for i, (lab, wi) in enumerate((('Text to Speech', 18), ('Voices  (read)', 20), ('User  (read)', 20))):
                on = clamp((t - wt('v4', wi) - .1 - i * .25) / .2)
                text(c, lab, 180, 1055 + i * 80, 30, 'm', '#e4e4e7', kc); toggle(c, 820, 1025 + i * 80, on)
            kk = clamp((t - wt('v4', 20) - .9) / .3)
            if kk > 0:
                rrect(c, 180, 1270, 560, 70, 16, '#111216', kk); text(c, 'sk_•••••••••••••••••••', 205, 1316, 28, 'mono', '#a1a1aa', kk)
                rrect(c, 760, 1270, 150, 70, 16, '#3b82f6', kk); text(c, 'Copy', 835, 1316, 28, 'b', '#ffffff', kk, 'c')
                if t > 20.4: pill(c, W / 2, 1480, 'COPIED', 34, fg='#ffffff', bgc='#16a34a', k=clamp((t - 20.4) / .2), icon='check', icol='#ffffff', align='c')
        path = Path2([(13.4, 540, 1500), (wt('v4', 14) - .15, 815, 845), (wt('v4', 18) - .15, 860, 1048), (20.2, 835, 1310), (21.0, 870, 1400)])
        x, y = path.at(t); cursor(c, x, y, 1.6, max(clamp(1 - abs(t - wt('v4', 14)) / .08), clamp(1 - abs(t - 20.3) / .08)))
        click_ring(c, x, y, (t - wt('v4', 14)) / .35); click_ring(c, x, y, (t - 20.3) / .35)

def seg_v5(c, t):
    c.clear(col(BG)); toptext(c, 'Step four: when **Claude** asks for the key, paste it into the **secure** **form.** **Never** into the chat.', WORDS['v5'], t, y0=210)
    k = clamp((t - 21.25) / .3)
    with Pop(c, W / 2, 1080, k):
        mock_window(c, 90, 660, 900, 880, 'Claude')
        rrect(c, 140, 770, 700, 120, 26, '#f4f4f5'); spark(c, 185, 830, 20, '#d97757')
        text(c, 'I need an ElevenLabs API key', 225, 822, 28, 'm', INK); text(c, 'to make the voices.', 225, 862, 28, 'm', INK)
        kf = clamp((t - wt('v5', 10)) / .3)
        if kf > 0:
            card(c, 160, 940, 760, 380, 28, '#ffffff', kf)
            text(c, 'Secure form  ·  api.elevenlabs.io', 200, 1000, 26, 'b', INK, kf); rrect(c, 200, 1040, 680, 80, 18, '#f4f4f5', kf)
            n = int(clamp((t - wt('v5', 9)) / .6) * 22); text(c, '•' * n, 225, 1093, 34, 'm', INK, kf)
            ks = clamp((t - wt('v5', 12)) / .25); rrect(c, 200, 1160, 680, 86, 20, '#1d1d1f', kf); text(c, 'Saved  ✓' if ks > 0 else 'Save', 540, 1215, 32, 'b', '#ffffff', kf, 'c')
        kn = clamp((t - wt('v5', 13)) / .3)
        if kn > 0:
            rrect(c, 140, 1380, 800, 90, 22, '#fee2e2'); text(c, 'Never paste keys in the chat', W / 2, 1438, 32, 'x', '#b91c1c', 1, 'c')

def seg_v6(c, t):
    c.clear(col(BG)); toptext(c, 'Now just type your **topic.** Claude writes the **script,** shows you a **preview,** and builds the **full** **video.**', WORDS['v6'], t, y0=200)
    if t < wt('v6', 15) - .2:
        k = clamp((t - 28.25) / .3)
        with Pop(c, W / 2, 1050, k):
            mock_window(c, 90, 660, 900, 820, 'Claude')
            prompt = 'Make a POV horror short about a night shift at a gas station'
            n = int(clamp((t - 28.5) / 1.6) * len(prompt)); rrect(c, 140, 1340, 800, 100, 26, '#f4f4f5')
            lines = [prompt[:n][:32], prompt[:n][32:]]
            for i, ln in enumerate(lines): text(c, ln, 170, 1382 + i * 38, 28, 'm', INK)
            ks = clamp((t - wt('v6', 8)) / .3)
            if ks > 0:
                card(c, 150, 760, 380, 520, 22, '#ffffff', ks); text(c, 'SCRIPT', 180, 815, 26, 'x', GREY, ks)
                for i in range(8): rrect(c, 180, 850 + i * 48, 320 - (i % 3) * 60, 16, 8, '#e4e4e7', ks)
            kp = clamp((t - wt('v6', 12)) / .3)
            if kp > 0:
                img = RES.frame(int(max(0, t - wt('v6', 12)) * FPS))
                card(c, 570, 760, 360, 520, 22, '#000000', kp)
                if img: draw_img(c, img, 580, 770, 340, 500, kp, 18)
                pill(c, 750, 1240, 'PREVIEW', 24, fg='#ffffff', bgc='#1d1d1f', k=kp, align='c')
    else:
        k = clamp((t - wt('v6', 15) + .2) / .3)
        with Pop(c, W / 2, 1100, k):
            shadow(c, 240, 640, 600, 1066, 36, .3, 40, 20)
            img = RES.frame(int(max(0, t - 28.5) * FPS))
            if img: draw_img(c, img, 240, 640, 600, 1066, 1, 36)
            pill(c, W / 2, 1770, '100% MADE BY CLAUDE', 34, fg='#ffffff', bgc='#d97757', k=k, align='c')

def seg_end(c, t):
    if t < 38.3:
        i = 0 if t < 37.2 else 1; full(c, END[i], t, (36.1, 37.2)[i])
        w = word_at(WORDS['v7'][:2], t)
        if w: caption_word(c, w[1].upper().strip('.'), w[2])
        return
    title_card(c, t - 38.3, 'COMMENT', '"SKILL"')
    k = clamp((t - 38.6) / .3)
    if k > 0: pill(c, W / 2, 1180, "I'LL SEND YOU THE LINK", 44, fg='#ffffff', bgc='#ef4444', k=k, align='c')

def frame(c, t):
    if t < 2.9 + 0.01 and t < 3.6: seg_hook(c, t) if t < 2.9 else None
    if t < 2.9: return
    if t < 5.1: seg_v1b(c, t)
    elif t < 7.3: seg_v2(c, t)
    elif t < 13.1: seg_v3(c, t)
    elif t < 21.1: seg_v4(c, t)
    elif t < 28.1: seg_v5(c, t)
    elif t < 36.1: seg_v6(c, t)
    else: seg_end(c, t)

CUES = [(t, 'whoosh', .9) for t in (1.45, 2.9, 4.4, 5.1, 7.3, 13.1, 21.1, 28.1, 36.1, 37.2, 38.3)]
CUES += [(5.5, 'pop', 1), (6.75, 'ding', .8), (7.45, 'pop', 1), (13.25, 'pop', 1), (21.25, 'pop', 1), (28.25, 'pop', 1), (38.6, 'pop', 1), (38.65, 'ding', .8)]
CUES += [(wt('v3', i), 'click', 1) for i in (6, 8, 10)] + [(wt('v3', 10) + 1.1, 'ding', .8)]
CUES += [(wt('v4', 14), 'click', 1), (20.3, 'click', 1), (20.4, 'ding', .8)] + [(wt('v4', 18) + .1 + i * .25, 'pop', .6) for i in range(3)]
CUES += [(wt('v5', 9) + i * .03, 'type', .5) for i in range(20)] + [(wt('v5', 12), 'ding', .9), (wt('v5', 13), 'pop', 1)]
CUES += [(28.5 + i * 0.07, 'type', .45) for i in range(22)] + [(wt('v6', 8), 'pop', 1), (wt('v6', 12), 'pop', 1), (wt('v6', 15) - .2, 'rise', .7)]

if __name__ == '__main__':
    if len(sys.argv) > 2 and sys.argv[1] == 'still':
        reel_still(frame, [float(x) for x in sys.argv[2].split(',')], os.path.join(HERE, 'shots', 'ts')); sys.exit()
    v = np.zeros(int(DUR * 48000), np.float32)
    for k, t0 in VO:
        a, sr = sf.read(os.path.join(HERE, 'vo', k + '.wav'), dtype='float32'); i = int(t0 * sr); v[i:i + len(a)] += a[:len(v) - i]
    vo_wav = os.path.join(HERE, 'out', 'vo_full.wav'); sf.write(vo_wav, v, 48000)
    render_reel(frame, DUR, os.path.join(HERE, 'out', 'skill_tutorial.mp4'), vo_wav, CUES, music_db=None)
