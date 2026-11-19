"""Analyse a reference POV video so it can be recreated exactly.
Usage: python3 analyze_reference.py <reference.mp4> [out_dir] [seconds=8]
Writes to out_dir (default ./ref_analysis):
  sheet_*.jpg          contact sheets (1 frame / 2 s) of the whole video
  early.jpg            first seconds at 2 fps (the part the 4 s preview must match)
  stills/*.png         full-res stills at key moments
  cuts.txt             scene-cut timestamps
  motion.txt           per-frame camera motion (optical flow): centre dx/dy, desk dx/dy, cumulative px
  palette.txt          colours sampled on a grid of the first frame (hex) — use for the toon palette
  text_timing.txt      when yellow subtitles / white title text appear, their x-extent and height
Read every output before planning. The motion table is the camera timeline: zero = a hold,
a smooth bell of px/frame = an eased move (peak/avg ≈ 1.57 → sine ease), steady small values = a drift.
"""
import os, sys, subprocess
import numpy as np, cv2

src = sys.argv[1]; out = sys.argv[2] if len(sys.argv) > 2 else 'ref_analysis'; secs = float(sys.argv[3]) if len(sys.argv) > 3 else 8
os.makedirs(os.path.join(out, 'stills'), exist_ok=True)
run = lambda *a: subprocess.run(['ffmpeg', '-v', 'error', '-y', *a], check=True)
dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', src], capture_output=True, text=True).stdout)
run('-i', src, '-vf', 'fps=1/2,scale=240:-1,tile=8x2', os.path.join(out, 'sheet_%02d.jpg'))
run('-i', src, '-t', str(secs), '-vf', 'fps=2,scale=360:-1,tile=8x2', '-frames:v', '1', os.path.join(out, 'early.jpg'))
for t in [0.1, 1.2, secs * 0.45, secs * 0.85] + [dur * f for f in (0.25, 0.5, 0.75)]:
    run('-ss', f'{t:.2f}', '-i', src, '-frames:v', '1', os.path.join(out, 'stills', f'still_{t:06.2f}.png'))
cuts = subprocess.run(['ffmpeg', '-i', src, '-vf', "select='gt(scene,0.3)',showinfo", '-f', 'null', '-'], capture_output=True, text=True).stderr
open(os.path.join(out, 'cuts.txt'), 'w').write('\n'.join(l.split('pts_time:')[1].split()[0] for l in cuts.splitlines() if 'pts_time:' in l))

cap = cv2.VideoCapture(src); fps = cap.get(cv2.CAP_PROP_FPS) or 30
ok, prev = cap.read(); H, W = prev.shape[:2]
g0 = cv2.cvtColor(prev, cv2.COLOR_BGR2GRAY)
mask = np.full(g0.shape, 255, np.uint8); mask[int(H * .05):int(H * .15), :] = 0; mask[int(H * .64):int(H * .72), :] = 0   # skip title + subtitle bands
# palette from the first frame
pal = []
for gy in range(1, 10):
    for gx in range(1, 6):
        x, y = int(W * gx / 6), int(H * gy / 10); b, g, r = prev[y - 2:y + 3, x - 2:x + 3].reshape(-1, 3).mean(0).astype(int)
        pal.append(f'({x},{y}) #{r:02x}{g:02x}{b:02x}')
open(os.path.join(out, 'palette.txt'), 'w').write('\n'.join(pal))
rows = ['t  centre_dx centre_dy  desk_dx desk_dy  cum_x cum_y']; cx = cy = 0.0; txt = ['t  yellow_px x0-x1 height  title_white_px']
i = 0; gp = g0
while i < int(secs * fps):
    ok, f = cap.read()
    if not ok: break
    i += 1; g = cv2.cvtColor(f, cv2.COLOR_BGR2GRAY)
    p0 = cv2.goodFeaturesToTrack(gp, 400, 0.01, 8, mask=mask)
    if p0 is not None:
        p1, st, _ = cv2.calcOpticalFlowPyrLK(gp, g, p0, None); a, b = p0[st == 1], p1[st == 1]; d = b - a
        cen = (a[:, 1] > H * .23) & (a[:, 1] < H * .62); bot = a[:, 1] > H * .74
        m = np.median(d[cen], 0) if cen.sum() > 5 else np.zeros(2); mb = np.median(d[bot], 0) if bot.sum() > 5 else np.zeros(2)
        cx += m[0]; cy += m[1]; rows.append(f'{i / fps:.2f} {m[0]:7.2f} {m[1]:7.2f} {mb[0]:7.2f} {mb[1]:7.2f} {cx:8.1f} {cy:8.1f}')
    band = f[int(H * .62):int(H * .73)].astype(int); yel = (band[..., 2] > 220) & (band[..., 1] > 190) & (band[..., 0] < 120)
    xs = np.where(yel.any(0))[0]; ys = np.where(yel.any(1))[0]
    tb = f[int(H * .07):int(H * .14), :int(W * .6)].astype(int); wh = int(((tb > 235).all(-1)).sum())
    txt.append(f'{i / fps:.2f} {int(yel.sum()):6d} ' + (f'{xs.min()}-{xs.max()} {ys.max() - ys.min()}' if len(xs) else '-') + f'  {wh}')
    gp = g
open(os.path.join(out, 'motion.txt'), 'w').write('\n'.join(rows))
open(os.path.join(out, 'text_timing.txt'), 'w').write('\n'.join(txt))
print(f'{src}: {W}x{H} @ {fps:.0f} fps, {dur:.1f}s -> {out}/ (sheets, early.jpg, stills, cuts, motion, palette, text_timing)')
