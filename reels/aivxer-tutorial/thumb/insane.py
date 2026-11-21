import cv2, numpy as np
ref = cv2.imread('ref_insane.png'); H, W = ref.shape[:2]
mask = cv2.imread('person_mask.png', 0).astype(np.float32) / 255.0
out = ref.copy()
panels = {  # inner rects x0,y0,x1,y1 ; source ; vertical centre (0..1)
    'TL': ((32, 192, 687, 510), 'f_class.png', .47),
    'TR': ((987, 189, 1643, 510), 'f_leo.png', .53),
    'BL': ((29, 538, 687, 895), 'f_maya.png', .50),
    'BR': ((1040, 535, 1644, 896), 'f_cop.png', .45),
}
for k, ((x0, y0, x1, y1), src, fy) in panels.items():
    w, h = x1 - x0, y1 - y0; im = cv2.imread(src); ih, iw = im.shape[:2]
    s = max(w / iw, h / ih); sw, sh = int(round(w / s)), int(round(h / s))
    sx = (iw - sw) // 2; sy = int(np.clip(fy * ih - sh / 2, 0, ih - sh))
    crop = cv2.resize(im[sy:sy + sh, sx:sx + sw], (w, h), interpolation=cv2.INTER_AREA)
    rm = np.zeros((h, w), np.uint8); r = 18
    cv2.rectangle(rm, (r, 0), (w - r, h), 255, -1); cv2.rectangle(rm, (0, r), (w, h - r), 255, -1)
    for cx, cy in ((r, r), (w - r, r), (r, h - r), (w - r, h - r)): cv2.circle(rm, (cx, cy), r, 255, -1)
    a = (cv2.GaussianBlur(rm, (3, 3), 0) / 255.0)[..., None]
    out[y0:y1, x0:x1] = (crop * a + out[y0:y1, x0:x1] * (1 - a)).astype(np.uint8)
m = cv2.GaussianBlur(mask, (5, 5), 0)[..., None]
out = (ref * m + out * (1 - m)).astype(np.uint8)
cv2.imwrite('thumbnail_E_insane.png', out); cv2.imwrite('thumbnail_E_insane.jpg', out, [cv2.IMWRITE_JPEG_QUALITY, 93])
