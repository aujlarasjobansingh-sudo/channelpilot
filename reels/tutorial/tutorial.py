"""Shorts tutorial: Gemini brief → install the POV skill in Claude → ElevenLabs API key → paste the brief (9:16, aivxer reel style).
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
ORDER = ['v1', 'g1', 'v2', 'v3', 'v4', 'v5', 'v6', 'v7']
TEXT = {'v1': "Claude made this entire horror short. Here's how you can too.",
        'g1': "Step one: paste my prompt into Gemini with your idea, and it writes the full director's brief. Copy it.",
        'v2': 'Step two: download the skill.',
        'v3': 'Step three: in Claude, open Customize, then Skills, and upload the zip.',
        'v4': 'Step four: for the voices, go to ElevenLabs, open API Keys, and create a key with text to speech turned on.',
        'v5': 'Step five: when Claude asks for the key, paste it into the secure form. Never into the chat.',
        'v6': 'Now paste the brief into Claude. It shows you a preview, and builds the full video.',
        'v7': "Comment SKILL and I'll send you the link."}
DURS = {k: sf.info(os.path.join(HERE, 'vo', k + '.wav')).duration for k in ORDER}
S = {'v1': 0.25}; S['g1'] = 5.1
for prev, k in zip(ORDER[1:-1], ORDER[2:]): S[k] = S[prev] + DURS[prev] + 0.12
S['v7'] = S['v6'] + DURS['v6'] + 2.2           # let the finished video play
T_TITLE = 4.4; T_END_CARD = S['v7'] + DURS['v7'] + 0.25; DUR = T_END_CARD + 1.7
WORDS = {}
for k in ORDER:
    a, sr = sf.read(os.path.join(HERE, 'vo', k + '.wav')); e = np.where(np.abs(a) > 0.03)[0]; v0, v1 = e[0] / sr, e[-1] / sr
    ws = TEXT[k].split(' '); wt_ = [max(2, len(re.sub(r'[^A-Za-z0-9]', '', w))) + 1.5 for w in ws]; tot = sum(wt_); cur = S[k] + v0; lst = []
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
HOOK = [FullVid(A('ep2.mp4'), 6.6, dur=1.6), FullVid(A('ep2.mp4'), 20.0, dur=1.6), FullVid(A('ep2.mp4'), 50.0, dur=2.4)]
RES = FullVid(A('ep2.mp4'), 18.0, 600, 1066, 9.5)
END = [FullVid(A('ep2.mp4'), 70.4, dur=1.3), FullVid(A('ep2.mp4'), 74.6, dur=1.3)]
def full(c, v, t, t0):
    img = v.frame(int((t - t0) * FPS)); sc = mix(1.08, 1.0, eout(clamp((t - t0) / .12)))
    c.save(); c.translate(W / 2, H / 2); c.scale(sc, sc); c.translate(-W / 2, -H / 2)
    if img: c.drawImage(img, 0, 0)
    c.restore()
def mock_window(c, x, y, w, h, title, dark=False):
    card(c, x, y, w, h, 34, '#1b1c22' if dark else '#ffffff')
    bar = '#26272e' if dark else '#e9e9ee'
    rrect(c, x, y, w, 70, 34, bar); c.drawRect(skia.Rect.MakeXYWH(x, y + 40, w, 30), paint(col(bar)))
    for i, cc in enumerate(('#ff5f57', '#febc2e', '#28c840')): c.drawCircle(x + 36 + i * 28, y + 35, 9, paint(col(cc)))
    text(c, title, x + w / 2, y + 45, 26, 'm', '#a1a1aa' if dark else GREY, 1, 'c')
def row(c, x, y, w, label, k_hi=0.0):
    if k_hi > 0: rrect(c, x, y - 34, w, 56, 14, '#d97757', .18 * k_hi)
    text(c, label, x + 22, y + 4, 32, 'b' if k_hi > .5 else 'm', INK)
def toggle(c, x, y, on):
    rrect(c, x, y, 76, 42, 21, '#22c55e' if on > .5 else '#d4d4d8'); c.drawCircle(x + 21 + 34 * on, y + 21, 17, paint(col('#ffffff')))
def text_lines(c, x, y, n, w, a=1.0, gap=40, color='#e4e4e7'):
    for i in range(n): rrect(c, x, y + i * gap, w - (i % 3) * 70 - (40 if i % 5 == 4 else 0), 14, 7, color, a)

# ------------------------------------------------------------------ segments
def seg_hook(c, t):
    if t < T_TITLE:
        i = 0 if t < 1.45 else 1 if t < 2.9 else 2; full(c, HOOK[i], t, (0, 1.45, 2.9)[i])
        w = word_at(WORDS['v1'], t)
        if w: caption_word(c, w[1].upper().strip('.'), w[2])
        return
    title_card(c, t - T_TITLE, 'POV ANIMATED', 'VIDEOS')

def seg_gemini(c, t):
    c.clear(col(BG)); toptext(c, "Step one: **paste** my **prompt** into **Gemini** with your idea, and it writes the full **director's** **brief.** **Copy** it.", WORDS['g1'], t, y0=200)
    k = clamp((t - S['g1'] - .15) / .3)
    with Pop(c, W / 2, 1120, k):
        mock_window(c, 90, 700, 900, 900, 'Gemini')
        kp = clamp((t - wt('g1', 2)) / .25)                     # prompt pasted
        if kp > 0:
            rrect(c, 140, 800, 800, 230, 22, '#f4f4f5', kp); text(c, 'PROMPT  (from the link)', 170, 845, 24, 'x', GREY, kp)
            text_lines(c, 170, 880, 4, 700, kp, 34, '#d4d4d8')
        ki = clamp((t - wt('g1', 8)) / .2)                      # your idea typed
        if ki > 0:
            idea = 'TOPIC: a night shift at a gas station'; n = int(clamp((t - wt('g1', 8)) / .9) * len(idea))
            rrect(c, 140, 1045, 800, 70, 18, '#eef2ff'); text(c, idea[:n], 170, 1090, 28, 'b', '#3730a3')
        kr = clamp((t - wt('g1', 12)) / .3)                     # brief written
        if kr > 0:
            card(c, 140, 1140, 800, 380, 22, '#ffffff', kr)
            text(c, "# DIRECTOR'S BRIEF: EPISODE 1", 170, 1190, 28, 'x', INK, kr)
            n = int(clamp((t - wt('g1', 12)) / 1.2) * 7); text_lines(c, 170, 1225, n, 720, kr, 36, '#d4d4d8')
            kc = clamp((t - wt('g1', 17)) / .2)
            rrect(c, 760, 1450, 150, 56, 14, '#3b82f6', kr); text(c, 'Copied' if kc > 0 else 'Copy', 835, 1487, 26, 'b', '#ffffff', kr, 'c')
        path = Path2([(S['g1'], 600, 1550), (wt('g1', 2) - .1, 540, 920), (wt('g1', 17) - .15, 835, 1478), (S['v2'], 870, 1560)])
        x, y = path.at(t); cursor(c, x, y, 1.6, max(clamp(1 - abs(t - wt('g1', 2)) / .08), clamp(1 - abs(t - wt('g1', 17)) / .08)))
        click_ring(c, x, y, (t - wt('g1', 2)) / .35); click_ring(c, x, y, (t - wt('g1', 17)) / .35)

def seg_v2(c, t):
    c.clear(col(BG)); toptext(c, 'Step two: **download** the **skill.**', WORDS['v2'], t)
    progress_card(c, t, S['v2'] + 0.3, 'pov-3d-animation-aivxer.zip', y=860, size_kb=78)

def seg_v3(c, t):
    c.clear(col(BG)); toptext(c, 'Step three: in **Claude,** open **Customize,** then **Skills,** and **upload** the zip.', WORDS['v3'], t)
    k = clamp((t - S['v3'] - .15) / .3); iC, iS, iU = wt('v3', 5), wt('v3', 7), wt('v3', 9)
    with Pop(c, W / 2, 1050, k):
        mock_window(c, 90, 620, 900, 860, 'Claude')
        spark(c, 170, 760, 26, '#d97757'); text(c, 'Claude', 215, 772, 34, 'x', INK)
        h_c = clamp((t - iC) / .2); h_s = clamp((t - iS) / .2)
        row(c, 130, 870, 300, 'Chats'); row(c, 130, 950, 300, 'Projects'); row(c, 130, 1030, 300, 'Customize', h_c)
        if h_c > 0: row(c, 470, 870, 480, 'Connectors'); row(c, 470, 950, 480, 'Skills', h_s); row(c, 470, 1030, 480, 'Styles')
        if h_s > 0:
            rrect(c, 470, 1110, 480, 92, 22, '#1d1d1f', h_s); text(c, '+  Upload a skill', 710, 1168, 32, 'b', '#ffffff', h_s, 'c')
            if t > iU:
                pr = eio(lin(t, iU, iU + 1.1))
                rrect(c, 470, 1250, 480, 120, 22, '#f4f4f5'); file_icon(c, 530, 1310, .38)
                text(c, 'pov-3d-animation-aivxer.zip', 580, 1300, 24, 'b', INK); rrect(c, 580, 1325, 330, 10, 5, '#e5e5ea'); rrect(c, 580, 1325, 330 * pr, 10, 5, '#3b82f6')
                text(c, 'Skill added' if pr >= 1 else 'Uploading...', 580, 1362, 22, 'm', '#16a34a' if pr >= 1 else GREY)
                if pr >= 1: check(c, 920, 1310, 22, '#22c55e', clamp((t - iU - 1.1) / .2))
        path = Path2([(S['v3'] + .3, 600, 1400), (iC - .15, 260, 1035), (iS - .15, 620, 955), (iU - .15, 700, 1160), (S['v4'], 760, 1300)])
        x, y = path.at(t); cursor(c, x, y, 1.6, max(clamp(1 - abs(t - w) / .08) for w in (iC, iS, iU)))
        for w in (iC, iS, iU): click_ring(c, x, y, (t - w) / .35)

def seg_v4(c, t):
    c.clear(col(BG)); toptext(c, 'Step four: for the voices, go to **ElevenLabs,** open **API** **Keys,** and create a key with **text** **to** **speech** turned on.', WORDS['v4'], t, y0=200, maxw=1000)
    k = clamp((t - S['v4'] - .15) / .3); iK, iT, iO = wt('v4', 14), wt('v4', 18), wt('v4', 20); tCopy = S['v5'] - 0.7
    with Pop(c, W / 2, 1150, k):
        mock_window(c, 90, 720, 900, 880, 'elevenlabs.io  ·  API Keys', dark=True)
        text(c, 'API Keys', 150, 850, 40, 'x', '#ffffff')
        kc = clamp((t - iK) / .25)
        rrect(c, 690, 805, 250, 70, 18, '#ffffff'); text(c, '+ Create key', 815, 850, 28, 'b', INK, 1, 'c')
        if kc > 0:
            rrect(c, 140, 910, 800, 470, 24, '#26272e', kc); text(c, 'Permissions', 180, 975, 30, 'b', '#e4e4e7', kc)
            for i, lab in enumerate(('Text to Speech', 'Voices  (read)', 'User  (read)')):
                on = clamp((t - (iT if i == 0 else iO) - i * .2) / .2)
                text(c, lab, 180, 1055 + i * 80, 30, 'm', '#e4e4e7', kc); toggle(c, 820, 1025 + i * 80, on)
            kk = clamp((t - iO - .5) / .3)
            if kk > 0:
                rrect(c, 180, 1270, 560, 70, 16, '#111216', kk); text(c, 'sk_•••••••••••••••••••', 205, 1316, 28, 'mono', '#a1a1aa', kk)
                rrect(c, 760, 1270, 150, 70, 16, '#3b82f6', kk); text(c, 'Copy', 835, 1316, 28, 'b', '#ffffff', kk, 'c')
                if t > tCopy: pill(c, W / 2, 1480, 'COPIED', 34, fg='#ffffff', bgc='#16a34a', k=clamp((t - tCopy) / .2), icon='check', icol='#ffffff', align='c')
        path = Path2([(S['v4'] + .3, 540, 1500), (iK - .15, 815, 845), (iT - .15, 860, 1048), (tCopy - .15, 835, 1310), (S['v5'], 870, 1400)])
        x, y = path.at(t); cursor(c, x, y, 1.6, max(clamp(1 - abs(t - iK) / .08), clamp(1 - abs(t - tCopy) / .08)))
        click_ring(c, x, y, (t - iK) / .35); click_ring(c, x, y, (t - tCopy) / .35)

def seg_v5(c, t):
    c.clear(col(BG)); toptext(c, 'Step five: when **Claude** asks for the key, paste it into the **secure** **form.** **Never** into the chat.', WORDS['v5'], t, y0=210)
    k = clamp((t - S['v5'] - .15) / .3); iP, iSv, iN = wt('v5', 8), wt('v5', 13), wt('v5', 14)
    with Pop(c, W / 2, 1080, k):
        mock_window(c, 90, 660, 900, 880, 'Claude')
        rrect(c, 140, 770, 700, 120, 26, '#f4f4f5'); spark(c, 185, 830, 20, '#d97757')
        text(c, 'I need an ElevenLabs API key', 225, 822, 28, 'm', INK); text(c, 'to make the voices.', 225, 862, 28, 'm', INK)
        kf = clamp((t - iP + .3) / .3)
        if kf > 0:
            card(c, 160, 940, 760, 380, 28, '#ffffff', kf)
            text(c, 'Secure form  ·  api.elevenlabs.io', 200, 1000, 26, 'b', INK, kf); rrect(c, 200, 1040, 680, 80, 18, '#f4f4f5', kf)
            n = int(clamp((t - iP) / .6) * 22); text(c, '•' * n, 225, 1093, 34, 'm', INK, kf)
            rrect(c, 200, 1160, 680, 86, 20, '#1d1d1f', kf); text(c, 'Saved  ✓' if t > iSv else 'Save', 540, 1215, 32, 'b', '#ffffff', kf, 'c')
        if t > iN: rrect(c, 140, 1380, 800, 90, 22, '#fee2e2'); text(c, 'Never paste keys in the chat', W / 2, 1438, 32, 'x', '#b91c1c', clamp((t - iN) / .2), 'c')

def seg_v6(c, t):
    c.clear(col(BG)); toptext(c, 'Now **paste** the **brief** into **Claude.** It shows you a **preview,** and builds the **full** **video.**', WORDS['v6'], t, y0=200)
    iB, iPv, iF = wt('v6', 1), wt('v6', 10), wt('v6', 14)
    if t < iF - .2:
        k = clamp((t - S['v6'] - .15) / .3)
        with Pop(c, W / 2, 1050, k):
            mock_window(c, 90, 660, 900, 820, 'Claude')
            kb = clamp((t - iB) / .25)
            if kb > 0:
                rrect(c, 140, 1180, 800, 250, 26, '#f4f4f5', kb); text(c, "# DIRECTOR'S BRIEF: EPISODE 1", 170, 1225, 26, 'x', INK, kb)
                text_lines(c, 170, 1258, 4, 700, kb, 36, '#d4d4d8')
            kp = clamp((t - iPv) / .3)
            if kp > 0:
                img = RES.frame(int(max(0, t - iPv) * FPS)); card(c, 360, 760, 360, 400, 22, '#000000', kp)
                if img: draw_img(c, img, 370, 770, 340, 380, kp, 18)
                pill(c, W / 2, 1130, '4 S PREVIEW', 24, fg='#ffffff', bgc='#1d1d1f', k=kp, align='c')
    else:
        k = clamp((t - iF + .2) / .3)
        with Pop(c, W / 2, 1100, k):
            shadow(c, 240, 640, 600, 1066, 36, .3, 40, 20)
            img = RES.frame(int(max(0, t - iPv) * FPS))
            if img: draw_img(c, img, 240, 640, 600, 1066, 1, 36)
            pill(c, W / 2, 1770, '100% MADE BY CLAUDE', 34, fg='#ffffff', bgc='#d97757', k=k, align='c')

def seg_end(c, t):
    if t < T_END_CARD:
        i = 0 if t < S['v7'] + 1.1 else 1; full(c, END[i], t, (S['v7'], S['v7'] + 1.1)[i])
        w = word_at(WORDS['v7'][:2], t)
        if w: caption_word(c, w[1].upper().strip('.'), w[2])
        return
    title_card(c, t - T_END_CARD, 'COMMENT', '"SKILL"')
    k = clamp((t - T_END_CARD - .3) / .3)
    if k > 0: pill(c, W / 2, 1180, "I'LL SEND YOU THE LINK", 44, fg='#ffffff', bgc='#ef4444', k=k, align='c')

SEGS = [(S['g1'], seg_hook), (S['v2'], seg_gemini), (S['v3'], seg_v2), (S['v4'], seg_v3), (S['v5'], seg_v4), (S['v6'], seg_v5), (S['v7'], seg_v6), (1e9, seg_end)]
def frame(c, t):
    for end, fn in SEGS:
        if t < end: fn(c, t); return

CUES = [(t, 'whoosh', .9) for t in (1.45, 2.9, T_TITLE, S['g1'], S['v2'], S['v3'], S['v4'], S['v5'], S['v6'], S['v7'], S['v7'] + 1.1, T_END_CARD)]
CUES += [(S[k] + .15, 'pop', 1) for k in ('g1', 'v3', 'v4', 'v5', 'v6')] + [(S['v2'] + .3, 'pop', 1), (S['v2'] + 1.5, 'ding', .8), (T_END_CARD + .3, 'pop', 1), (T_END_CARD + .35, 'ding', .8)]
CUES += [(wt('g1', 2), 'click', 1), (wt('g1', 12), 'pop', .8), (wt('g1', 17), 'click', 1), (wt('g1', 17) + .1, 'ding', .7)] + [(wt('g1', 8) + i * .04, 'type', .45) for i in range(20)]
CUES += [(wt('v3', i), 'click', 1) for i in (5, 7, 9)] + [(wt('v3', 9) + 1.1, 'ding', .8)]
CUES += [(wt('v4', 14), 'click', 1), (S['v5'] - .7, 'click', 1), (S['v5'] - .6, 'ding', .8)] + [(wt('v4', 18), 'pop', .6), (wt('v4', 20), 'pop', .6), (wt('v4', 20) + .2, 'pop', .6)]
CUES += [(wt('v5', 8) + i * .03, 'type', .5) for i in range(20)] + [(wt('v5', 13), 'ding', .9), (wt('v5', 14), 'pop', 1)]
CUES += [(wt('v6', 1), 'pop', 1), (wt('v6', 10), 'pop', 1), (wt('v6', 14) - .2, 'rise', .7)]

if __name__ == '__main__':
    if len(sys.argv) > 2 and sys.argv[1] == 'still':
        reel_still(frame, [float(x) for x in sys.argv[2].split(',')], os.path.join(HERE, 'shots', 'ts')); sys.exit()
    v = np.zeros(int(DUR * 48000), np.float32)
    for k in ORDER:
        a, sr = sf.read(os.path.join(HERE, 'vo', k + '.wav'), dtype='float32'); i = int(S[k] * sr); v[i:i + len(a)] += a[:len(v) - i]
    vo_wav = os.path.join(HERE, 'out', 'vo_full.wav'); sf.write(vo_wav, v, 48000)
    print('timeline:', {k: round(x, 2) for k, x in S.items()}, 'DUR', round(DUR, 2))
    render_reel(frame, DUR, os.path.join(HERE, 'out', 'skill_tutorial.mp4'), vo_wav, CUES, music_db=None)
