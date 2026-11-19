import cv2, numpy as np, sys
path, secs = sys.argv[1], float(sys.argv[2])
cap = cv2.VideoCapture(path); fps = cap.get(cv2.CAP_PROP_FPS)
ok, prev = cap.read(); prev = cv2.cvtColor(prev, cv2.COLOR_BGR2GRAY)
# mask out HUD/subtitle regions
mask = np.full(prev.shape, 255, np.uint8); mask[60:190, :] = 0; mask[820:920, :] = 0
cx = cy = 0.0; rows = []
for i in range(1, int(secs * fps)):
    ok, f = cap.read()
    if not ok: break
    g = cv2.cvtColor(f, cv2.COLOR_BGR2GRAY)
    p0 = cv2.goodFeaturesToTrack(prev, 400, 0.01, 8, mask=mask)
    p1, st, _ = cv2.calcOpticalFlowPyrLK(prev, g, p0, None)
    a, b = p0[st == 1], p1[st == 1]
    # separate: centre region motion (scene) vs bottom (desk/hands)
    d = b - a
    cen = (a[:, 1] > 300) & (a[:, 1] < 800)
    bot = a[:, 1] > 950
    m = np.median(d[cen], 0) if cen.sum() > 5 else np.array([0, 0])
    mb = np.median(d[bot], 0) if bot.sum() > 5 else np.array([0, 0])
    cx += m[0]; cy += m[1]
    rows.append((i / fps, m[0], m[1], mb[0], mb[1], cx, cy))
    prev = g
for r in rows[::3]:
    print("t=%.2f  centre dx=%6.2f dy=%6.2f | desk dx=%6.2f dy=%6.2f | cum %7.1f %7.1f" % r)
