"""Tighten the edit without re-rendering: drop dead-air ranges from the rendered frames + final mix.
Video gets a 3-frame dissolve at each cut, audio a 30 ms crossfade, so the flow never jumps.
Usage: python3 cut.py  -> out/episode2_fast.mp4
"""
import os, json, subprocess
import numpy as np, cv2, soundfile as sf

HERE = os.path.dirname(os.path.abspath(__file__)); FPS = 30
CUTS = [(2.6, 5.4), (11.2, 14.6), (21.8, 23.8), (30.4, 33.6), (35.6, 36.9), (40.9, 41.8), (52.6, 56.6), (61.0, 65.2), (76.6, 79.6), (107.5, 110.0)]
src = os.path.join(HERE, 'out', 'frames'); dst = os.path.join(HERE, 'out', 'frames_cut')
n_src = len([f for f in os.listdir(src) if f.endswith('.png')])
# kept frame ranges
keep, start = [], 0
for a, b in CUTS:
    keep.append((start, int(round(a * FPS)))); start = int(round(b * FPS))
if start < n_src: keep.append((start, n_src))
keep = [(a, b) for a, b in keep if b > a]
os.makedirs(dst, exist_ok=True)
for f in os.listdir(dst): os.remove(os.path.join(dst, f))
fr = lambda i: os.path.join(src, f'f_{i:04d}.png')
XF = 3; out_i = 0
for k, (a, b) in enumerate(keep):
    for i in range(a, b):
        j = i - a
        if k > 0 and j < XF:   # dissolve from the end of the previous segment
            pa = keep[k - 1][1] - XF + j
            w = (j + 1) / (XF + 1)
            img = cv2.addWeighted(cv2.imread(fr(pa)), 1 - w, cv2.imread(fr(i)), w, 0)
            cv2.imwrite(os.path.join(dst, f'f_{out_i:04d}.png'), img)
        else:
            os.link(fr(i), os.path.join(dst, f'f_{out_i:04d}.png'))
        out_i += 1
# audio: same ranges, 30 ms crossfades
a_, sr = sf.read(os.path.join(HERE, 'out', 'mix.wav'), always_2d=True)
xf = int(0.03 * sr); parts = []
for a, b in keep:
    seg = a_[int(a / FPS * sr): int(b / FPS * sr)].copy(); parts.append(seg)
outa = parts[0]
for p in parts[1:]:
    ramp = np.linspace(0, 1, xf)[:, None]
    blend = outa[-xf:] * (1 - ramp) + p[:xf] * ramp
    outa = np.concatenate([outa[:-xf], blend, p[xf:]])
total = out_i / FPS
outa = outa[:int(total * sr)]
fade = int(0.4 * sr); outa[-fade:] *= np.linspace(1, 0, fade)[:, None]
wav = os.path.join(HERE, 'out', 'mix_fast.wav'); sf.write(wav, outa.astype(np.float32), sr, subtype='PCM_24')
mp4 = os.path.join(HERE, 'out', 'episode2_fast.mp4')
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-framerate', str(FPS), '-i', os.path.join(dst, 'f_%04d.png'), '-i', wav, '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
                '-crf', '18', '-preset', 'slow', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', mp4], check=True)
print(f'{n_src / FPS:.1f}s -> {total:.1f}s  ({len(CUTS)} cuts) -> {mp4}')
