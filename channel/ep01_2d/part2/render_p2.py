# usage: python3 render_p2.py stills t1,t2,... | python3 render_p2.py seg <i> <n>
import sys, os, subprocess, bisect
from shots_p2 import *
OUTD = os.path.join(HERE, 'out'); os.makedirs(OUTD, exist_ok=True)

def frame(surf, t):
    world.REAL = t
    i = max(0, bisect.bisect_right(TIMES, t) - 1); i = min(i, len(SHOTS) - 1)
    ph, fn, cam = SHOTS[i]; t0, t1 = TIMES[i], TIMES[i + 1]
    set_boil(t); c = surf.getCanvas()
    if cam == 'card': zz, fx, fy = 1.0, 960, 540
    elif cam: zz, fx, fy = cam(t, t0)
    else: e = ease(K(t, t0, t1 - t0)); zz = lerp(1.0, 1.07, e); fx = 960 + lerp(-12, 12, e); fy = 540
    c.clear(C((0, 0, 0))); c.save(); c.translate(W / 2, H / 2); c.scale(zz, zz); c.translate(-fx, -fy)
    fn(c, t, t0); c.restore()
    finish(surf, bloom=.42); vignette(c, .5)
    if any(0 <= t - it < 2.5 / FPS for it in IMPACTS2): impact(surf)
    grain(c, t)
    if 0 <= t - t0 < 1.5 / FPS and t0 > 0 and cam != 'card': c.drawRect(skia.Rect(0, 0, W, H), fp((0, 0, 0), 70))

if __name__ == '__main__':
    surf = skia.Surface(W, H)
    if sys.argv[1] == 'stills':
        for s in sys.argv[2].split(','):
            frame(surf, float(s)); surf.makeImageSnapshot().save(os.path.join(OUTD, f'st_{float(s):06.2f}.png'), skia.kPNG)
        sys.exit()
    i, n = int(sys.argv[2]), int(sys.argv[3]); N = int(DUR2 * FPS)
    a, b = N * i // n, N * (i + 1) // n
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgra', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                          '-c:v', 'libx264', '-crf', '18', '-preset', 'medium', '-pix_fmt', 'yuv420p', os.path.join(OUTD, f'seg_{i}.mp4')], stdin=subprocess.PIPE)
    for f in range(a, b):
        frame(surf, f / FPS); p.stdin.write(surf.makeImageSnapshot().toarray(colorType=skia.kBGRA_8888_ColorType).tobytes())
        if (f - a) % 120 == 0: print('seg', i, 'frame', f, '/', b, flush=True)
    p.stdin.close(); p.wait(); print('done', i, flush=True)
