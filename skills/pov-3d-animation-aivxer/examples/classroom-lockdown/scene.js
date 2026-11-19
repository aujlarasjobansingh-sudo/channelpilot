// Classroom POV scene v2 — rebuilt from measurements of the reference video.
// Camera eye sits at the origin (x=0, z=0, y=EYE), looking down -z.
// Projection: stereographic wide lens (f = 540px on a 1280px-tall frame), measured from the reference.
// Window API (used by render.js): window.sceneReady, window.renderAt(seconds), window.setHud(bool)
import * as THREE from 'three';
import { OutlineEffect } from 'three/addons/effects/OutlineEffect.js';

// ---------------------------------------------------------------------------
// CLOTHING COLOURS — the only thing changed vs. the reference video.
// ---------------------------------------------------------------------------
const CLOTHES = {
  playerSleeve:  '#2f5f8f', // ref: slate grey  #687486
  frontShirt:    '#2a9d8f', // ref: coral red   #d65968
  frontHood:     '#f4d35e', // ref: mint        #9fd9b0
  frontPants:    '#3a3f4f',
  teacherTop:    '#8e3b5a', // ref: mustard     #d49f36
  teacherPants:  '#5b5f6b', // ref: grey-blue   #8b8e9a
  bunGirlTop:    '#f08a3c', // ref: yellow      #f2c23e
  bunGirlPants:  '#4a4f60',
  rightKidTop:   '#7cbf4a', // ref: lilac       #b98ad8
  rightKidPants: '#2d3a5c',
  leftKidTop:    '#ef7fb0', // ref: light blue  #5c97cd
  leftKidPants:  '#3a3f4f',
};

// ---------------------------------------------------------------------------
// palette sampled from the reference frames
// ---------------------------------------------------------------------------
const C = {
  ceiling: '#bebab0', wall: '#e9e0cd', wallLow: '#ddd3b4', wallLine: '#bab195', baseboard: '#c9be9a',
  floor: '#8d9ab1', floorLine: '#7f8ca4', desk: '#e0b473', metal: '#8a909c', chair: '#576889',
  board: '#2a6858', boardFrame: '#b4b09e', door: '#62769f', doorFrame: '#3b4a6e', light: '#fbfaed',
  skinA: '#e8bb92', skinB: '#c38c60', skinC: '#85563c', skinD: '#f0c8a2', hand: '#ecc29c',
  paper: '#f2f1ec', caseCol: '#ad5875', bottle: '#c5ceda', cap: '#373b52',
  purpleBag: '#8b58d2', redBag: '#d45b47', lilac: '#c6b3ec', tdesk: '#b07a4e',
};

const W = 720, H = 1280;
const EYE = 1.2;
const FOCAL = 540;                      // output px per radian at centre (stereographic)
const SRC_W = 1350, SRC_H = 2400;       // rectilinear source render
const TAN_Y = (H / 2) / Math.hypot(W / 2, H / 2) * Math.tan(2 * Math.atan(Math.hypot(W / 2, H / 2) / (2 * FOCAL)));
const TAN_X = TAN_Y * (W / H);
const SRC_FOV = 2 * Math.atan(TAN_Y) * 180 / Math.PI;

const canvas = document.getElementById('c');
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, preserveDrawingBuffer: true });
renderer.setPixelRatio(1);
renderer.setSize(W, H, false);
const scene = new THREE.Scene();
scene.background = new THREE.Color(C.ceiling);

// ---------------------------------------------------------------------------
// helpers
// ---------------------------------------------------------------------------
const grad = new THREE.DataTexture(new Uint8Array([200, 236, 255]), 3, 1, THREE.RedFormat);
grad.minFilter = grad.magFilter = THREE.NearestFilter; grad.needsUpdate = true;
const OUT = 0.0029;
const matCache = {};
function M(color, opts = {}) {
  const { thin, flat, ...mo } = opts;
  const key = color + (thin ? 't' : '') + (flat ? 'f' : '');
  if (matCache[key] && !mo.map) return matCache[key];
  const m = flat ? new THREE.MeshBasicMaterial({ color, ...mo }) : new THREE.MeshToonMaterial({ color, gradientMap: grad, ...mo });
  m.userData.outlineParameters = { thickness: thin ? OUT * 0.6 : OUT, color: [0.08, 0.08, 0.09], alpha: 1 };
  if (!mo.map) matCache[key] = m;
  return m;
}
const noOutline = m => { m.userData.outlineParameters = { visible: false }; return m; };
const INK = noOutline(new THREE.MeshBasicMaterial({ color: '#17171b' }));
const mat = c => (typeof c === 'string' ? M(c) : c);
function add(mesh, parent) { (parent || scene).add(mesh); return mesh; }
function box(w, h, d, color, x, y, z, parent, opts) {
  const m = add(new THREE.Mesh(new THREE.BoxGeometry(w, h, d), typeof color === 'string' ? M(color, opts) : color), parent);
  m.position.set(x, y, z); return m;
}
// box with rounded top (chair backs, bags)
function roundTop(w, h, d, color, x, y, z, parent) {
  const r = w / 2, s = new THREE.Shape();
  s.moveTo(-r, -h / 2); s.lineTo(r, -h / 2); s.lineTo(r, h / 2 - r); s.absarc(0, h / 2 - r, r, 0, Math.PI, false); s.lineTo(-r, -h / 2);
  const g = new THREE.ExtrudeGeometry(s, { depth: d, bevelEnabled: true, bevelThickness: d * 0.25, bevelSize: d * 0.25, bevelSegments: 4, curveSegments: 24 });
  g.translate(0, 0, -d / 2);
  const m = add(new THREE.Mesh(g, mat(color)), parent); m.position.set(x, y, z); return m;
}
function roundRect(w, h, d, r, color, x, y, z, parent) {
  const s = new THREE.Shape(), a = w / 2, b = h / 2;
  s.moveTo(-a + r, -b); s.lineTo(a - r, -b); s.quadraticCurveTo(a, -b, a, -b + r); s.lineTo(a, b - r); s.quadraticCurveTo(a, b, a - r, b);
  s.lineTo(-a + r, b); s.quadraticCurveTo(-a, b, -a, b - r); s.lineTo(-a, -b + r); s.quadraticCurveTo(-a, -b, -a + r, -b);
  const g = new THREE.ExtrudeGeometry(s, { depth: d, bevelEnabled: true, bevelThickness: d * 0.3, bevelSize: d * 0.3, bevelSegments: 3, curveSegments: 12 });
  g.translate(0, 0, -d / 2);
  const m = add(new THREE.Mesh(g, mat(color)), parent); m.position.set(x, y, z); return m;
}
function cyl(rt, rb, h, color, x, y, z, parent, seg = 24) {
  const m = add(new THREE.Mesh(new THREE.CylinderGeometry(rt, rb, h, seg), mat(color)), parent); m.position.set(x, y, z); return m;
}
function sph(r, color, x, y, z, parent) {
  const m = add(new THREE.Mesh(new THREE.SphereGeometry(r, 32, 20), mat(color)), parent); m.position.set(x, y, z); return m;
}
function limb(a, b, r, color, parent, r2) {
  const A = new THREE.Vector3(...a), B = new THREE.Vector3(...b), len = A.distanceTo(B);
  const geo = r2 ? new THREE.CylinderGeometry(r2, r, len, 20) : new THREE.CapsuleGeometry(r, len, 8, 20);
  const m = add(new THREE.Mesh(geo, mat(color)), parent);
  m.position.copy(A).add(B).multiplyScalar(0.5);
  m.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), B.clone().sub(A).normalize());
  return m;
}
function inkLine(a, b, t = 0.022) {
  const A = new THREE.Vector3(...a), B = new THREE.Vector3(...b);
  const m = add(new THREE.Mesh(new THREE.BoxGeometry(t, A.distanceTo(B), t), INK));
  m.position.copy(A).add(B).multiplyScalar(0.5);
  m.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), B.clone().sub(A).normalize());
}
function canvasTex(w, h, draw) {
  const c = document.createElement('canvas'); c.width = w; c.height = h;
  draw(c.getContext('2d'), w, h);
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 16;
  return t;
}
function texPlane(w, h, tex, x, y, z, parent) {
  const m = add(new THREE.Mesh(new THREE.PlaneGeometry(w, h), noOutline(new THREE.MeshBasicMaterial({ map: tex, transparent: true }))), parent);
  m.position.set(x, y, z); return m;
}
const F = (wt, px) => `${wt} ${px}px Rubik, sans-serif`;
await Promise.all([600, 700, 800, 900].map(w => document.fonts.load(F(w, 40))));

// ---------------------------------------------------------------------------
// room
// ---------------------------------------------------------------------------
const XL = -3.75, XR = 3.7, ZF = -5.8, ZB = 3.0, RH = 3.15;
function buildRoom() {
  const floorTex = canvasTex(1024, 1024, (g, w, h) => {
    g.fillStyle = C.floor; g.fillRect(0, 0, w, h);
    g.strokeStyle = C.floorLine; g.lineWidth = 4;
    for (let i = 0; i <= 4; i++) { const p = i * w / 4; g.beginPath(); g.moveTo(p, 0); g.lineTo(p, h); g.stroke(); g.beginPath(); g.moveTo(0, p); g.lineTo(w, p); g.stroke(); }
  });
  floorTex.wrapS = floorTex.wrapT = THREE.RepeatWrapping; floorTex.repeat.set((XR - XL) / 2.4, (ZB - ZF) / 2.4);
  floorTex.offset.set(0.31, 0.12);
  const floor = add(new THREE.Mesh(new THREE.PlaneGeometry(XR - XL, ZB - ZF), noOutline(new THREE.MeshBasicMaterial({ map: floorTex }))));
  floor.rotation.x = -Math.PI / 2; floor.position.set((XL + XR) / 2, 0, (ZB + ZF) / 2);
  const ceil = add(new THREE.Mesh(new THREE.PlaneGeometry(XR - XL, ZB - ZF), noOutline(new THREE.MeshBasicMaterial({ color: C.ceiling }))));
  ceil.rotation.x = Math.PI / 2; ceil.position.set((XL + XR) / 2, RH, (ZB + ZF) / 2);

  const wallTex = canvasTex(64, 630, (g, w, h) => {      // 1px = 5mm
    g.fillStyle = C.wall; g.fillRect(0, 0, w, h);
    const y1 = h - 1.0 * 200;                             // wainscot at 1.0m
    g.fillStyle = C.wallLow; g.fillRect(0, y1, w, h - y1);
    g.fillStyle = C.wallLine; g.fillRect(0, y1 - 2, w, 4);
    g.fillStyle = C.baseboard; g.fillRect(0, h - 22, w, 22);
    g.fillStyle = '#a99f80'; g.fillRect(0, h - 23, w, 2);
  });
  const wm = noOutline(new THREE.MeshBasicMaterial({ map: wallTex }));
  const wall = (w, x, z, ry) => { const m = add(new THREE.Mesh(new THREE.PlaneGeometry(w, RH), wm)); m.position.set(x, RH / 2, z); m.rotation.y = ry; };
  wall(XR - XL, (XL + XR) / 2, ZF, 0); wall(XR - XL, (XL + XR) / 2, ZB, Math.PI);
  wall(ZB - ZF, XL, (ZB + ZF) / 2, Math.PI / 2); wall(ZB - ZF, XR, (ZB + ZF) / 2, -Math.PI / 2);
  for (const [x, z] of [[XL, ZF], [XR, ZF], [XL, ZB], [XR, ZB]]) inkLine([x, 0, z], [x, RH, z]);
  inkLine([XL, RH, ZF], [XR, RH, ZF]); inkLine([XL, RH, ZF], [XL, RH, ZB]); inkLine([XR, RH, ZF], [XR, RH, ZB]);
  inkLine([XL, 0, ZF], [XR, 0, ZF], 0.016); inkLine([XL, 0, ZF], [XL, 0, ZB], 0.016); inkLine([XR, 0, ZF], [XR, 0, ZB], 0.016);

  // ceiling light panels: rows measured at z -2.6 / -5.0, columns x -2.75 / -0.6 / 1.6
  const lightTex = canvasTex(600, 150, (g, w, h) => {
    g.fillStyle = C.light; g.fillRect(0, 0, w, h);
    g.strokeStyle = '#8b8a86'; g.lineWidth = 6; g.lineCap = 'round';
    for (let i = 1; i < 7; i++) { const x = i * w / 7; g.beginPath(); g.moveTo(x - 6, 26); g.lineTo(x + 6, h - 26); g.stroke(); }
  });
  for (const z of [-0.2, -2.6, -5.0]) for (const x of [-2.75, -0.6, 1.6]) {
    box(1.45, 0.03, 0.36, C.light, x, RH - 0.02, z, null, { flat: true });
    const p = texPlane(1.43, 0.34, lightTex, x, RH - 0.036, z); p.rotation.x = Math.PI / 2;
  }

  // ---- front wall (z = ZF), positions measured from the reference
  const z = ZF + 0.012;
  box(3.04, 1.51, 0.05, C.boardFrame, -1.6, 1.575, z);
  const boardTex = canvasTex(1450, 695, (g, w, h) => {
    g.fillStyle = C.board; g.fillRect(0, 0, w, h);
    g.fillStyle = '#f3f2ea'; g.font = F(800, 74); g.fillText('BIOLOGY FINAL', 70, 140);
    g.font = F(600, 50); g.fillText('10:00 – 11:30', 70, 225);
    g.fillStyle = '#f2df78'; g.font = F(800, 50); g.fillText('NO PHONES · NO TALKING', 70, 520);
    g.fillStyle = '#f3f2ea'; g.font = F(600, 48); g.fillText('Good luck!', 1090, 470);
    g.strokeStyle = '#f3f2ea'; g.lineWidth = 7;
    const x0 = 820, len = 400, yc = 300, amp = 55;
    for (const ph of [0, Math.PI]) { g.beginPath(); for (let x = 0; x <= len; x += 4) { const y = yc + amp * Math.sin(x / 34 + ph); x ? g.lineTo(x0 + x, y) : g.moveTo(x0 + x, y); } g.stroke(); }
    g.lineWidth = 4; for (let x = 10; x < len; x += 24) { g.beginPath(); g.moveTo(x0 + x, yc + amp * Math.sin(x / 34)); g.lineTo(x0 + x, yc + amp * Math.sin(x / 34 + Math.PI)); g.stroke(); }
  });
  texPlane(2.9, 1.39, boardTex, -1.6, 1.575, z + 0.03);
  box(2.9, 0.04, 0.08, '#a19c86', -1.6, 0.86, z + 0.05);
  box(0.36, 0.28, 0.07, '#d4cfc2', -0.02, 2.52, z);
  cyl(0.075, 0.075, 0.02, '#57585e', -0.02, 2.52, z + 0.045).rotation.x = Math.PI / 2;
  const exitTex = canvasTex(260, 108, (g, w, h) => { g.fillStyle = '#3aa86a'; g.fillRect(0, 0, w, h); g.fillStyle = '#fff'; g.font = F(800, 66); g.textAlign = 'center'; g.fillText('EXIT', w / 2, 80); });
  box(0.5, 0.21, 0.04, '#3aa86a', 1.41, 2.33, z);
  texPlane(0.47, 0.19, exitTex, 1.41, 2.33, z + 0.025);
  box(1.25, 2.27, 0.05, C.doorFrame, 1.415, 1.135, z);
  box(1.08, 2.15, 0.07, C.door, 1.415, 1.075, z + 0.02);
  box(0.2, 0.62, 0.02, '#dbe7f2', 1.15, 1.6, z + 0.065, null, { thin: true });
  box(0.17, 0.045, 0.07, '#cfd2d8', 1.8, 1.0, z + 0.09, null, { thin: true });
  box(0.06, 0.15, 0.04, '#cfd2d8', 1.86, 1.04, z + 0.07, null, { thin: true });
  const clockTex = canvasTex(256, 256, g => {
    g.fillStyle = '#fff'; g.beginPath(); g.arc(128, 128, 118, 0, 7); g.fill();
    g.lineWidth = 6; g.strokeStyle = '#1b1b1f';
    for (let i = 0; i < 12; i++) { const a = i / 12 * Math.PI * 2; g.beginPath(); g.moveTo(128 + 90 * Math.cos(a), 128 + 90 * Math.sin(a)); g.lineTo(128 + 104 * Math.cos(a), 128 + 104 * Math.sin(a)); g.stroke(); }
    g.lineWidth = 9; g.lineCap = 'round';
    const hand = (a, l) => { g.beginPath(); g.moveTo(128, 128); g.lineTo(128 + l * Math.sin(a), 128 - l * Math.cos(a)); g.stroke(); };
    hand((10 + 42 / 60) / 12 * Math.PI * 2, 55); hand(42 / 60 * Math.PI * 2, 84);
  });
  cyl(0.19, 0.19, 0.04, '#1b1b1f', 2.7, 2.35, z).rotation.x = Math.PI / 2;
  texPlane(0.34, 0.34, clockTex, 2.7, 2.35, z + 0.025);
  const lockTex = canvasTex(240, 320, (g, w, h) => {
    g.fillStyle = '#fbfaf6'; g.fillRect(0, 0, w, h);
    g.fillStyle = '#d23a3a'; g.fillRect(0, 0, w, 64); g.fillStyle = '#fff'; g.font = F(800, 36); g.fillText('LOCKDOWN', 14, 46);
    g.fillStyle = '#c23030'; g.font = F(700, 27); ['1 LOCK', '2 LIGHTS', '3 OUT OF', '   SIGHT'].forEach((s, i) => g.fillText(s, 16, 116 + i * 48));
  });
  box(0.48, 0.64, 0.015, '#fbfaf6', 2.72, 1.52, z, null, { thin: true });
  texPlane(0.46, 0.62, lockTex, 2.72, 1.52, z + 0.012);

  // ---- left wall: window with blinds
  const blindTex = canvasTex(256, 256, (g, w, h) => {
    g.fillStyle = '#eef0f3'; g.fillRect(0, 0, w, h);
    g.fillStyle = '#9ea4ae'; for (let y = 6; y < h; y += 16) g.fillRect(0, y, w, 4);
  });
  const wl = new THREE.Group(); wl.position.set(XL + 0.02, 1.65, -3.55); wl.rotation.y = Math.PI / 2; scene.add(wl);
  box(1.95, 1.5, 0.05, '#4f5666', 0, 0, 0, wl);
  texPlane(1.83, 1.38, blindTex, 0, 0, 0.03, wl);
  // ---- right wall: bulletin board
  const rb = new THREE.Group(); rb.position.set(XR - 0.02, 1.7, -3.2); rb.rotation.y = -Math.PI / 2; scene.add(rb);
  box(2.2, 1.25, 0.05, '#7b5233', 0, 0, 0, rb);
  const corkTex = canvasTex(440, 250, (g, w, h) => {
    g.fillStyle = '#b07a4c'; g.fillRect(0, 0, w, h);
    const cols = ['#f2efe4', '#f4d77a', '#9fd0e8', '#f2b6b6', '#bfe3b0'];
    for (let i = 0; i < 8; i++) { g.fillStyle = cols[i % 5]; const x = 22 + (i % 4) * 104, y = 20 + Math.floor(i / 4) * 118; g.fillRect(x, y, 78, 96); g.fillStyle = '#c55'; g.fillRect(x + 34, y + 4, 9, 9); }
  });
  texPlane(2.1, 1.15, corkTex, 0, 0, 0.03, rb);
}

// ---------------------------------------------------------------------------
// furniture
// ---------------------------------------------------------------------------
function desk(x, z, o = {}) {
  const g = new THREE.Group(); g.position.set(x, 0, z); g.rotation.y = o.ry || 0; scene.add(g);
  const w = o.w || 0.86, d = o.d || 0.56, h = 0.74;
  box(w, 0.04, d, o.top || C.desk, 0, h - 0.02, 0, g);
  for (const sx of [-1, 1]) for (const sz of [-1, 1]) cyl(0.017, 0.017, h - 0.04, C.metal, sx * (w / 2 - 0.05), (h - 0.04) / 2, sz * (d / 2 - 0.05), g, 10);
  box(w - 0.12, 0.02, 0.02, C.metal, 0, 0.12, d / 2 - 0.05, g, { thin: true });
  if (o.paper) { const p = box(0.21, 0.004, 0.28, C.paper, -0.12, h + 0.003, 0.02, g, { thin: true }); p.rotation.y = 0.12; }
  if (o.pencil) { const p = cyl(0.007, 0.007, 0.17, '#f2c230', 0.14, h + 0.008, 0.06, g, 8); p.rotation.set(0, 0.5, Math.PI / 2); }
  if (o.laptop) { box(0.34, 0.016, 0.24, '#3a3e48', 0.1, h + 0.01, 0.02, g); const s = box(0.34, 0.22, 0.014, '#2a2d35', 0.1, h + 0.12, -0.1, g); s.rotation.x = -0.25; }
  return g;
}
function chair(x, z, o = {}) {        // back is on the +z side (faces away from camera)
  const g = new THREE.Group(); g.position.set(x, 0, z); g.rotation.y = o.ry || 0; scene.add(g);
  const col = o.color || C.chair;
  box(0.44, 0.035, 0.42, col, 0, 0.46, 0, g);
  const back = roundRect(0.32, 0.23, 0.025, 0.05, col, 0, 0.79, 0.215, g);
  back.rotation.x = -0.05;
  for (const sx of [-1, 1]) {
    cyl(0.013, 0.013, 0.46, C.metal, sx * 0.19, 0.23, -0.18, g, 8);
    cyl(0.013, 0.013, 0.7, C.metal, sx * 0.19, 0.35, 0.2, g, 8);
  }
  return g;
}

// ---------------------------------------------------------------------------
// characters (small heads on broad puffy shoulders, as in the reference)
// ---------------------------------------------------------------------------
function head(parent, { skin, hair, style, face = false }) {
  const h = new THREE.Group(); parent.add(h);
  sph(0.105, skin, 0, 0, 0, h).scale.set(1, 1.07, 1);
  sph(0.026, skin, -0.104, -0.008, 0, h); sph(0.026, skin, 0.104, -0.008, 0, h);
  const back = face ? -1 : 1;   // +z side is the back of the head for students
  const capGeo = (cov) => new THREE.SphereGeometry(0.113, 32, 18, 0, Math.PI * 2, 0, Math.PI * cov);
  if (style === 'bowl') {
    const c = add(new THREE.Mesh(capGeo(0.5), M(hair)), h); c.position.y = 0.004; c.rotation.x = 0.28 * back;
  } else if (style === 'bun') {
    const c = add(new THREE.Mesh(capGeo(0.52), M(hair)), h); c.position.y = 0.003; c.rotation.x = 0.35 * back;
    sph(0.05, hair, 0, 0.115, 0.03 * back, h);
  } else if (style === 'short') {
    const c = add(new THREE.Mesh(capGeo(0.46), M(hair)), h); c.rotation.x = 0.3 * back;
  }
  if (face) {
    for (const sx of [-1, 1]) {
      const ring = add(new THREE.Mesh(new THREE.TorusGeometry(0.034, 0.008, 8, 28), INK), h); ring.position.set(sx * 0.042, 0.012, 0.1);
      const lens = add(new THREE.Mesh(new THREE.CircleGeometry(0.031, 24), noOutline(new THREE.MeshBasicMaterial({ color: '#ffffff' }))), h); lens.position.set(sx * 0.042, 0.012, 0.101);
      const pupil = add(new THREE.Mesh(new THREE.CircleGeometry(0.011, 14), INK), h); pupil.position.set(sx * 0.042, 0.012, 0.103);
    }
    const mouth = add(new THREE.Mesh(new THREE.CircleGeometry(0.014, 16), INK), h); mouth.position.set(0, -0.052, 0.098); mouth.scale.set(1.2, 0.7, 1);
  }
  return h;
}
// seated student facing -z; (x, z) is the head position
function student(x, z, { top, hood, pants, skin, hair, style, shoes = '#2b2b33' }) {
  const g = new THREE.Group(); g.position.set(x, 0, z); scene.add(g);
  const torso = add(new THREE.Mesh(new THREE.CapsuleGeometry(0.15, 0.2, 8, 24), M(top)), g);
  torso.scale.set(1.2, 1, 0.78); torso.position.set(0, 0.72, 0.03);
  for (const sx of [-1, 1]) {
    sph(0.092, top, sx * 0.158, 0.885, 0.03, g).scale.set(1, 0.92, 0.95);
    limb([sx * 0.17, 0.87, 0.02], [sx * 0.2, 0.7, -0.12], 0.068, top, g);
    limb([sx * 0.2, 0.7, -0.12], [sx * 0.1, 0.75, -0.36], 0.058, top, g);
    limb([sx * 0.09, 0.53, 0.02], [sx * 0.1, 0.53, -0.3], 0.07, pants, g);
    limb([sx * 0.1, 0.51, -0.3], [sx * 0.11, 0.08, -0.33], 0.06, pants, g);
    box(0.09, 0.065, 0.17, shoes, sx * 0.11, 0.033, -0.37, g);
  }
  if (hood) { const hd = sph(0.095, hood, 0, 0.955, 0.035, g); hd.scale.set(1.0, 0.42, 0.75); }
  cyl(0.042, 0.045, 0.16, skin, 0, 1.03, 0.0, g);
  const h = head(g, { skin, hair, style }); h.position.set(0, 1.2, 0);
  return g;
}
function teacher(x, z) {
  const g = new THREE.Group(); g.position.set(x, 0, z); g.rotation.y = 0.18; scene.add(g);
  const top = CLOTHES.teacherTop, pants = CLOTHES.teacherPants, skin = C.skinD;
  for (const sx of [-1, 1]) {
    limb([sx * 0.085, 0.92, 0], [sx * 0.095, 0.09, 0.0], 0.068, pants, g);
    box(0.1, 0.07, 0.2, '#1f2028', sx * 0.095, 0.035, 0.04, g);
  }
  const torso = add(new THREE.Mesh(new THREE.CapsuleGeometry(0.15, 0.3, 8, 24), M(top)), g);
  torso.scale.set(1.15, 1, 0.78); torso.position.set(0, 1.12, 0);
  for (const sx of [-1, 1]) sph(0.09, top, sx * 0.16, 1.36, 0, g).scale.set(1, 0.92, 0.95);
  limb([-0.18, 1.34, 0], [-0.24, 1.02, 0.03], 0.06, top, g);
  limb([-0.24, 1.02, 0.03], [-0.2, 0.8, 0.09], 0.052, top, g);
  sph(0.045, skin, -0.2, 0.77, 0.1, g);
  limb([0.18, 1.34, 0], [0.24, 1.1, 0.12], 0.06, top, g);
  limb([0.24, 1.1, 0.12], [0.08, 1.12, 0.22], 0.052, top, g);
  sph(0.045, skin, 0.05, 1.12, 0.24, g);
  cyl(0.04, 0.042, 0.14, skin, 0, 1.46, 0, g);
  const h = head(g, { skin, hair: '#97472e', style: 'bun', face: true }); h.position.set(0, 1.62, 0);
  return g;
}

// ---------------------------------------------------------------------------
// player desk + POV body (all positions measured from the reference)
// ---------------------------------------------------------------------------
function buildPOV() {
  desk(0.03, -0.42, { w: 0.86, d: 0.56 });           // far edge z=-0.70, near edge z=-0.14
  chair(0.0, 0.13, {});                              // own chair, seen when looking down
  const examTex = canvasTex(660, 840, (g, w, h) => {
    g.fillStyle = C.paper; g.fillRect(0, 0, w, h);
    g.fillStyle = '#17171b'; g.font = F(800, 40); g.fillText('BIOLOGY — FINAL EXAM', 36, 64);
    g.font = F(600, 28); g.fillText('Name:  Noah R.', 36, 108);
    g.strokeStyle = '#a3abbf'; g.lineWidth = 6;
    for (let i = 0; i < 10; i++) { const y = 175 + i * 64; g.beginPath(); g.moveTo(36, y); g.lineTo(36 + (i % 3 === 1 ? 200 : 250), y); g.stroke(); }
    const filled = [[0, 1], [1, 0], [2, 3], [3, 2], [4, 1], [5, 0]];
    g.lineWidth = 3.5; g.strokeStyle = '#17171b';
    for (let r = 0; r < 10; r++) for (let c = 0; c < 4; c++) {
      g.beginPath(); g.arc(395 + c * 60, 160 + r * 64, 18, 0, 7);
      if (filled.some(([a, b]) => a === r && b === c)) { g.fillStyle = '#17171b'; g.fill(); } else g.stroke();
    }
  });
  const pz = -0.40, px = 0.01, rot = -0.03;
  const pb = box(0.22, 0.003, 0.28, C.paper, px, 0.7415, pz, null, { thin: true }); pb.rotation.y = rot;
  const pp = add(new THREE.Mesh(new THREE.PlaneGeometry(0.22, 0.28), noOutline(new THREE.MeshBasicMaterial({ map: examTex }))));
  pp.rotation.set(-Math.PI / 2, 0, rot); pp.position.set(px, 0.7445, pz);
  const pc = box(0.23, 0.065, 0.09, C.caseCol, -0.17, 0.7725, -0.56); pc.rotation.y = -0.04;
  cyl(0.04, 0.04, 0.19, C.bottle, 0.32, 0.835, -0.5);
  cyl(0.037, 0.04, 0.04, C.cap, 0.32, 0.95, -0.5);
  sph(0.037, C.cap, 0.32, 0.97, -0.5).scale.set(1, 0.35, 1);
  // bags hanging just beyond the desk (purple with ZOE tag, red)
  const pbag = roundTop(0.145, 0.27, 0.08, C.purpleBag, -0.42, 0.7, -0.72); pbag.rotation.y = 0.25;
  const tagTex = canvasTex(140, 80, (g, w, h) => { g.fillStyle = '#fff'; g.fillRect(0, 0, w, h); g.fillStyle = '#17171b'; g.font = F(800, 46); g.fillText('ZOE', 22, 58); });
  const tg = new THREE.Group(); tg.position.set(-0.5, 0.69, -0.66); tg.rotation.set(0, 0.6, -0.55); scene.add(tg);
  box(0.075, 0.042, 0.006, '#ffffff', 0, 0, 0, tg, { thin: true });
  texPlane(0.07, 0.038, tagTex, 0, 0, 0.0035, tg);
  roundTop(0.135, 0.3, 0.07, C.redBag, -0.16, 0.615, -0.86);
}
function buildArms() {
  const sleeve = CLOTHES.playerSleeve;
  const L = [-0.105, 0.8, -0.365], R = [0.122, 0.8, -0.31];
  limb([-0.33, 0.84, 0.05], [L[0] - 0.025, L[1] + 0.005, L[2] + 0.05], 0.05, sleeve, null, 0.064);
  limb([0.35, 0.84, 0.05], [R[0] + 0.02, R[1] + 0.005, R[2] + 0.05], 0.05, sleeve, null, 0.064);
  sph(0.047, C.hand, ...L).scale.set(1, 0.85, 1.1);
  sph(0.047, C.hand, ...R).scale.set(1, 0.85, 1.1);
  limb([R[0] + 0.01, 0.815, R[2] + 0.01], [0.07, 0.76, -0.45], 0.0065, '#f2c230', null, 0.0065);
  limb([0.07, 0.76, -0.45], [0.064, 0.752, -0.462], 0.0065, '#f0c48e', null, 0.001);
}

// ---------------------------------------------------------------------------
// populate (head positions measured from the reference frames)
// ---------------------------------------------------------------------------
buildRoom();
buildPOV();
buildArms();
// front kid + their chair/desk
chair(0.18, -1.24, {});
desk(0.17, -1.85, { paper: true });
student(0.19, -1.25, { top: CLOTHES.frontShirt, hood: CLOTHES.frontHood, pants: CLOTHES.frontPants, skin: C.skinA, hair: '#37281e', style: 'bowl' });
// bun girl, right kid, left kid
chair(-1.05, -2.44, {}); desk(-1.05, -3.1, { paper: true, pencil: true });
student(-1.05, -2.5, { top: CLOTHES.bunGirlTop, pants: CLOTHES.bunGirlPants, skin: C.skinB, hair: '#1d1a1a', style: 'bun' });
chair(1.75, -2.64, {}); desk(1.75, -3.3, { paper: true });
student(1.75, -2.7, { top: CLOTHES.rightKidTop, pants: CLOTHES.rightKidPants, skin: C.skinC, hair: '#151313', style: 'short' });
chair(-1.95, -2.04, {}); desk(-1.95, -2.7, { paper: true });
student(-1.95, -2.1, { top: CLOTHES.leftKidTop, pants: CLOTHES.leftKidPants, skin: C.skinD, hair: '#5a3a24', style: 'short' });
// Zoe's empty desk + lilac chair (she's not in class)
desk(-1.12, -1.72, { paper: true, pencil: true });
chair(-1.12, -1.08, { color: C.lilac });
// more empty desks/chairs to fill the room
for (const [x, z] of [[1.55, -1.45], [2.95, -1.5], [-2.95, -1.2], [2.95, -3.5], [0.35, -3.6], [-2.2, -3.95], [3.0, 0.3], [-3.0, 0.3], [1.6, 0.2]]) {
  desk(x, z, { paper: Math.abs(x * z) % 2 > 0.6 }); chair(x, z + 0.62, {});
}
desk(-2.5, -3.95 - 0.1, { w: 1.4, d: 0.7, top: C.tdesk, laptop: true });   // teacher's desk (front-left)
teacher(-1.2, -5.0);

scene.add(new THREE.AmbientLight('#ffffff', 2.55));
const sun = new THREE.DirectionalLight('#ffffff', 0.7); sun.position.set(-2, 5, 3); scene.add(sun);

// ---------------------------------------------------------------------------
// camera + stereographic lens pass
// ---------------------------------------------------------------------------
const camera = new THREE.PerspectiveCamera(SRC_FOV, W / H, 0.02, 60);
camera.rotation.order = 'YXZ';
const effect = new OutlineEffect(renderer, { defaultThickness: OUT, defaultColor: [0.08, 0.08, 0.09] });
const rt = new THREE.WebGLRenderTarget(SRC_W, SRC_H, { samples: 4, type: THREE.HalfFloatType });
rt.texture.minFilter = THREE.LinearFilter;
const lens = new THREE.ShaderMaterial({
  uniforms: { tSrc: { value: rt.texture }, focal: { value: FOCAL }, res: { value: new THREE.Vector2(W, H) }, tanXY: { value: new THREE.Vector2(TAN_X, TAN_Y) } },
  vertexShader: `varying vec2 vUv; void main(){ vUv = uv; gl_Position = vec4(position.xy, 0., 1.); }`,
  fragmentShader: `
    uniform sampler2D tSrc; uniform float focal; uniform vec2 res; uniform vec2 tanXY; varying vec2 vUv;
    vec3 toSRGB(vec3 c){ return mix(c*12.92, 1.055*pow(c, vec3(1./2.4)) - 0.055, step(0.0031308, c)); }
    void main(){
      vec2 p = (vUv - 0.5) * res;                 // pixels from centre
      float r = length(p);
      float th = 2.0 * atan(r / (2.0 * focal));   // stereographic
      vec2 dir = r > 0.0 ? p / r : vec2(0.0);
      vec2 ndc = dir * tan(th) / tanXY;
      gl_FragColor = vec4(toSRGB(texture2D(tSrc, ndc * 0.5 + 0.5).rgb), 1.0);
    }`,
  depthTest: false, depthWrite: false,
});
const quadScene = new THREE.Scene();
const quadCam = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);
quadScene.add(new THREE.Mesh(new THREE.PlaneGeometry(2, 2), lens));

// ---------------------------------------------------------------------------
// camera timeline — measured from the reference with optical flow:
// still → smooth pan left → hold → slow drift → snap tilt to the paper → slow drift back
// ---------------------------------------------------------------------------
const D2R = Math.PI / 180;
const sineIO = t => 0.5 - 0.5 * Math.cos(Math.PI * t);
const sineIn = t => 1 - Math.cos(Math.PI * t / 2);
const seg = (t, a, b) => Math.min(1, Math.max(0, (t - a) / (b - a)));
const CAM = { yaw0: 0, pan: 13.6, panLift: 2.0, drift1: 1.25, tiltPitch: -50, tiltYaw: 0.6, drift2: -1.5 };
function camAt(t) {
  let yaw = CAM.yaw0 + CAM.pan * sineIO(seg(t, 0.28, 0.93)) + CAM.drift1 * sineIn(seg(t, 1.45, 2.5));
  let pitch = CAM.panLift * sineIO(seg(t, 0.42, 0.95));
  const k = sineIO(seg(t, 2.48, 3.0));
  yaw = yaw + (CAM.tiltYaw - yaw) * k;
  pitch = pitch + (CAM.tiltPitch - pitch) * k;
  yaw += CAM.drift2 * sineIn(seg(t, 3.0, 4.3));
  pitch += 0.3 * sineIn(seg(t, 3.0, 4.3));
  return { yaw: yaw * D2R, pitch: pitch * D2R };
}

// ---------------------------------------------------------------------------
// HUD timing — measured from the reference
// ---------------------------------------------------------------------------
const SUBS = [[0.57, 1.70, 'Ten more minutes,'], [1.70, 2.27, 'people.'], [2.27, 3.33, 'Eyes on your own'], [3.33, 4.07, 'paper.']];
const titleEl = document.getElementById('title'), subEl = document.getElementById('subtxt'), hudEl = document.getElementById('hud');
const easeOut = t => 1 - Math.pow(1 - t, 3);
function hudAt(t) {
  const a = easeOut(seg(t, -0.05, 0.4)), out = seg(t, 3.5, 3.85);
  titleEl.style.opacity = (0.25 + 0.75 * a) * (1 - out);
  titleEl.style.transform = `translateX(${-12 * (1 - a)}px)`;
  const s = SUBS.find(([a0, b0]) => t >= a0 && t < b0);
  subEl.textContent = s ? s[2] : '';
  if (s) subEl.style.transform = `translateX(-50%) scale(${0.91 + 0.09 * easeOut(seg(t, s[0], s[0] + 0.1))})`;
}
window.setHud = on => { hudEl.style.display = on ? 'block' : 'none'; };
window.CAM = CAM;
window.renderAt = (t) => {
  const c = camAt(t);
  const lean = sineIO(seg(t, 2.48, 3.05));
  camera.position.set(0, EYE - 0.03 * lean, -0.06 * lean);
  camera.rotation.set(c.pitch, c.yaw, 0);
  renderer.setRenderTarget(rt);
  effect.render(scene, camera);
  renderer.setRenderTarget(null);
  renderer.render(quadScene, quadCam);
  hudAt(t);
};
window.sceneReady = Promise.resolve(true);
