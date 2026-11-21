from comps import *
import json

VO = "vo/vo48.wav"
OUT = "out/final.mp4"
MUSIC_DB = -30
WORDS = json.load(open(ROOT + "/vo/words.json"))

def wt(word, after=0.0):
    """start time of the first spoken word (prefix match) at or after `after` seconds"""
    w = word.lower()
    for s, t in WORDS:
        if t >= after - 1e-3 and s.lower().strip(",.?!").startswith(w): return t
    raise KeyError(word)

# ---------- s01: hook — the reference page (identity blurred) ----------
def s01(T0, D):
    prof, grid = IMG("their_profile.png"), IMG("their_grid.png")
    WX, WY, WW, WH = 660, 60, 600, 840
    S = WW / 1224; PH, GH = 984 * S, 2107 * S; CH = WH - 38
    SCR = PH + GH - CH                              # scroll that shows the bottom row of the grid
    t_200 = wt("200,000") - T0; t_one = wt("one", 4) - T0; t_30 = wt("30") - T0
    t_studio = wt("studio") - T0; t_anim = wt("animators") - T0
    def scroll(t): return SCR * eio(lin(t, t_one, t_one + 1.0))
    # 30.7M label position (bottom-right tile) in desktop coordinates at full scroll
    vx, vy = WX + 940 * S, WY + 38 + PH + 2050 * S - SCR
    cam = Cam([(0, 960, 540, 1.0), (t_200 - .35, 960, 540, 1.04), (t_200 + .1, WX + 640 * S, WY + 38 + 340 * S, 1.75),
               (t_one - .05, WX + 640 * S, WY + 38 + 340 * S, 1.8), (t_one + .9, 960, 540, 1.0),
               (t_30 - .1, vx - 40, vy - 90, 1.7), (t_studio - .5, vx - 40, vy - 90, 1.78), (t_studio - .05, 960, 540, 1.0), (D, 960, 540, 1.03)])
    sfx(0, "whoosh", .7); sfx(.15, "pop", .6); sfx(.7, "pop", .5); sfx(t_200 + .05, "pop", .6)
    sfx(t_one, "whoosh_s", .5); sfx(t_30 + .1, "ding", .6); sfx(t_studio - .45, "whoosh", .55)
    sfx(t_studio, "pop", .6); sfx(t_anim, "pop", .6)

    def page(c2, x, y, w, h, t):
        rrect(c2, x, y, w, h, 0, "#0c0f14"); sc = scroll(t)
        draw_img(c2, prof, x, y - sc, w, PH); draw_img(c2, grid, x, y + PH - sc, w, GH)

    def draw(c, t):
        bg(c, "Browser")
        k = lin(t, .1, .35)
        window(c, WX, WY, WW, WH, "Instagram", a=k, sc=mix(.9, 1, back(lin(t, .1, .55))),
               content=lambda c2, x, y, w, h: page(c2, x, y, w, h, t), bg="#0c0f14")
        ann_label(c, "THEIR PAGE", WX - 250, WY + 120, lin(t, .7, 1.0), "#ffd23f", 30)
        # 217K highlight
        ky = lin(t, t_200 + .05, t_200 + .5) * (1 - lin(t, t_one, t_one + .3))
        ann_circle(c, WX + 650 * S, WY + 38 + 340 * S, 62, ky)
        pill(c, WX + 650 * S, WY + 38 + 470 * S, "217K followers", 22, k=lin(t, t_200 + .15, t_200 + .5), a=ky,
             icon="dot", icol="#ffd23f", align="c")
        # 30.7M highlight
        kv = lin(t, t_30, t_30 + .45) * (1 - lin(t, t_studio - .5, t_studio - .2))
        ann_circle(c, vx + 4, vy - 2, 48, kv)
        pill(c, vx - 70, vy - 150, "30.7M views", 22, k=lin(t, t_30 + .1, t_30 + .45), a=kv, icon="dot",
             icol="#ef4444", align="c")
        # no studio / no animators
        for i, (s, t1) in enumerate([("No studio", t_studio), ("No animators", t_anim)]):
            kk = lin(t, t1, t1 + .35)
            pill(c, 1560, 380 + i * 110, s, 34, k=kk, a=kk, icon="cross", icol="#ef4444", align="c")
        bgdock(c, 1)
    return cam, draw


from scenes_b import build_list
SCENES = [("s01", 0.0, 10.355, s01)] + build_list(10.355)
INSERTS = [dict(id="x_signal", after=SCENES[-1][2], path=A + "/signal_169.mp4", dur=97.0, label="THE SIGNAL IN THE WOODS  ·  Episode 1", color="#ef4444")]
