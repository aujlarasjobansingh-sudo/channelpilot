# usage: python3 render.py stills t1,t2,...  |  python3 render.py seg <i> <n>
import sys, os, subprocess
from shots_b import *
ALL = SHOTS_A + SHOTS_B
DUR = 310.6
OUTD = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out'); os.makedirs(OUTD, exist_ok=True)
SEPIA_CF = skia.ColorFilters.Matrix([.50, .48, .14, 0, .06, .42, .46, .12, 0, .04, .32, .36, .14, 0, .0, 0, 0, 0, 1, 0])

def find(t):
    for sh in ALL:
        if sh[0] <= t < sh[1]: return sh
    return ALL[-1]

def frame(surf, t):
    t0, t1, fn, cam = find(t); set_boil(t); c = surf.getCanvas()
    if cam == 'card': zz, fx, fy = 1.0, 960, 540
    elif cam: zz, fx, fy = cam(t)
    else:
        e = ease(K(t, t0, t1 - t0)); zz = lerp(1.0, 1.07, e); fx = 960 + lerp(-12, 12, e); fy = 540
    c.clear(C((0, 0, 0))); c.save(); c.translate(W / 2, H / 2); c.scale(zz, zz); c.translate(-fx, -fy)
    fn(c, t); c.restore()
    finish(surf, bloom=.42); vignette(c, .5)
    if SEPIA[0] <= t < SEPIA[1]:
        img = surf.makeImageSnapshot(); p = skia.Paint(); p.setColorFilter(SEPIA_CF); p.setAlphaf(.55); c.drawImage(img, 0, 0, skia.SamplingOptions(), p)
    if any(0 <= t - it < 2.5 / FPS for it in IMPACTS): impact(surf)
    grain(c, t)
    # 2-frame soft cut: tiny white-to-clear flash at shot starts makes cuts feel snappier
    if 0 <= t - t0 < 1.5 / FPS and t0 > 0 and cam != 'card': c.drawRect(skia.Rect(0, 0, W, H), fp((0, 0, 0), 70))

if __name__ == '__main__':
    surf = skia.Surface(W, H)
    if sys.argv[1] == 'stills':
        for s in sys.argv[2].split(','):
            frame(surf, float(s)); surf.makeImageSnapshot().save(os.path.join(OUTD, f'st_{float(s):06.2f}.png'), skia.kPNG)
        sys.exit()
    i, n = int(sys.argv[2]), int(sys.argv[3]); N = round(DUR * FPS)
    a, b = N * i // n, N * (i + 1) // n
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgra', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                          '-c:v', 'libx264', '-crf', '18', '-preset', 'medium', '-pix_fmt', 'yuv420p', os.path.join(OUTD, f'seg_{i}.mp4')], stdin=subprocess.PIPE)
    for f in range(a, b):
        frame(surf, f / FPS); p.stdin.write(surf.makeImageSnapshot().toarray(colorType=skia.kBGRA_8888_ColorType).tobytes())
        if (f - a) % 120 == 0: print('seg', i, 'frame', f, '/', b, flush=True)
    p.stdin.close(); p.wait(); print('done', i, flush=True)
