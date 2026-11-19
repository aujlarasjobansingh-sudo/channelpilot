// Classroom POV scene — toon-shaded 3D with ink outlines and a fisheye lens.
// Window API (used by render.js): window.sceneReady (Promise), window.renderAt(seconds), window.setHud(bool)
import * as THREE from 'three';
import { OutlineEffect } from 'three/addons/effects/OutlineEffect.js';

// ---------------------------------------------------------------------------
// CLOTHING COLOURS — the only thing changed vs. the reference video.
// (reference colour in comments)
// ---------------------------------------------------------------------------
const CLOTHES = {
  playerSleeve:  '#2f5f8f', // ref: slate grey  #5c6373
  frontShirt:    '#2a9d8f', // ref: coral red   #e05463
  frontCollar:   '#f4d35e', // ref: mint        #8fd3a8
  frontPants:    '#3a3f4f', // ref: charcoal
  teacherTop:    '#8e3b5a', // ref: mustard     #e7b03c
  teacherPants:  '#5b5f6b', // ref: navy        #2c3346
  bunGirlTop:    '#f08a3c', // ref: yellow      #f2c23e
  bunGirlPants:  '#4a4f60',
  rightKidTop:   '#7cbf4a', // ref: lilac       #b98ad8
  rightKidPants: '#2d3a5c',
  leftKidTop:    '#ef7fb0', // ref: light blue  #6fb0dc
  leftKidPants:  '#3a3f4f',
  backKidTop:    '#e4574a', // ref: blue        (distant kid, right)
};

const W = 720, H = 1280, SS = 1.5;           // output size, supersample factor
const canvas = document.getElementById('c');
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, preserveDrawingBuffer: true });
renderer.setPixelRatio(1);
renderer.setSize(W, H, false);

const scene = new THREE.Scene();
scene.background = new THREE.Color('#bdb8ad');

// ---------------------------------------------------------------------------
// materials
// ---------------------------------------------------------------------------
const grad = new THREE.DataTexture(new Uint8Array([165, 215, 255]), 3, 1, THREE.RedFormat);
grad.minFilter = grad.magFilter = THREE.NearestFilter; grad.needsUpdate = true;
const matCache = {};
function M(color, opts = {}) {
  const key = color + JSON.stringify(opts);
  if (matCache[key] && !opts.map) return matCache[key];
  const { thin, ...mo } = opts;
  const m = new THREE.MeshToonMaterial({ color, gradientMap: grad, ...mo });
  m.userData.outlineParameters = { thickness: opts.thin ? 0.0025 : 0.0045, color: [0.07, 0.07, 0.08], alpha: 1 };
  if (!opts.map) matCache[key] = m;
  return m;
}
function noOutline(m) { m.userData.outlineParameters = { visible: false }; return m; }
const INK = new THREE.MeshBasicMaterial({ color: '#16161a' });
noOutline(INK);

function box(w, h, d, color, x, y, z, parent = scene, opts) {
  const mesh = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), typeof color === 'string' ? M(color, opts) : color);
  mesh.position.set(x, y, z); parent.add(mesh); return mesh;
}
function cyl(rt, rb, h, color, x, y, z, parent = scene, seg = 20) {
  const mesh = new THREE.Mesh(new THREE.CylinderGeometry(rt, rb, h, seg), typeof color === 'string' ? M(color) : color);
  mesh.position.set(x, y, z); parent.add(mesh); return mesh;
}
function sph(r, color, x, y, z, parent = scene) {
  const mesh = new THREE.Mesh(new THREE.SphereGeometry(r, 28, 18), typeof color === 'string' ? M(color) : color);
  mesh.position.set(x, y, z); parent.add(mesh); return mesh;
}
function caps(r, len, color, parent = scene) {
  const mesh = new THREE.Mesh(new THREE.CapsuleGeometry(r, len, 8, 20), typeof color === 'string' ? M(color) : color);
  parent.add(mesh); return mesh;
}
// capsule spanning point a -> b
function limb(a, b, r, color, parent = scene) {
  const A = new THREE.Vector3(...a), B = new THREE.Vector3(...b);
  const len = A.distanceTo(B);
  const m = caps(r, Math.max(0.001, len), color, parent);
  m.position.copy(A).add(B).multiplyScalar(0.5);
  m.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), B.clone().sub(A).normalize());
  return m;
}
// black ink strip between two points (for room edges)
function inkLine(a, b, t = 0.025) {
  const A = new THREE.Vector3(...a), B = new THREE.Vector3(...b);
  const m = new THREE.Mesh(new THREE.BoxGeometry(t, A.distanceTo(B), t), INK);
  m.position.copy(A).add(B).multiplyScalar(0.5);
  m.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), B.clone().sub(A).normalize());
  scene.add(m); return m;
}
function canvasTex(w, h, draw) {
  const c = document.createElement('canvas'); c.width = w; c.height = h;
  const g = c.getContext('2d'); draw(g, w, h);
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8;
  return t;
}
function texPlane(w, h, tex, x, y, z, ry = 0, parent = scene) {
  const m = new THREE.Mesh(new THREE.PlaneGeometry(w, h), noOutline(new THREE.MeshBasicMaterial({ map: tex, transparent: true })));
  m.position.set(x, y, z); m.rotation.y = ry; parent.add(m); return m;
}
const F = (wt, px) => `${wt} ${px}px Rubik, sans-serif`;

// ---------------------------------------------------------------------------
// room   (x: left/right, y: up, z: toward camera; front wall at z = -7)
// ---------------------------------------------------------------------------
const RX = 5.0, RZF = -5.3, RZB = 5, RH = 3.15;
const WALL = '#ebe3cc', WALL_LOW = '#e3d9bc', CEIL = '#bcb7ab', FLOOR = '#9ba4ba';

function buildRoom() {
  // floor with tile grid
  const floorTex = canvasTex(1024, 1024, (g, w, h) => {
    g.fillStyle = FLOOR; g.fillRect(0, 0, w, h);
    g.strokeStyle = '#8890a6'; g.lineWidth = 5;
    for (let i = 0; i <= 8; i++) { const p = i * w / 8; g.beginPath(); g.moveTo(p, 0); g.lineTo(p, h); g.stroke(); g.beginPath(); g.moveTo(0, p); g.lineTo(w, p); g.stroke(); }
  });
  floorTex.wrapS = floorTex.wrapT = THREE.RepeatWrapping; floorTex.repeat.set(2.6, 3);
  const floor = new THREE.Mesh(new THREE.PlaneGeometry(RX * 2, RZB - RZF), noOutline(M(FLOOR, { map: floorTex })));
  floor.rotation.x = -Math.PI / 2; floor.position.set(0, 0, (RZB + RZF) / 2); scene.add(floor);

  const ceil = new THREE.Mesh(new THREE.PlaneGeometry(RX * 2, RZB - RZF), noOutline(new THREE.MeshBasicMaterial({ color: CEIL })));
  ceil.rotation.x = Math.PI / 2; ceil.position.set(0, RH, (RZB + RZF) / 2); scene.add(ceil);

  const wallTex = canvasTex(256, 512, (g, w, h) => {
    g.fillStyle = WALL; g.fillRect(0, 0, w, h);
    const split = h * (1 - 1.0 / RH);
    g.fillStyle = WALL_LOW; g.fillRect(0, split, w, h - split);
    g.fillStyle = '#cfc4a3'; g.fillRect(0, split - 3, w, 6);
    g.fillStyle = '#c9c0a8'; g.fillRect(0, h - 14, w, 14); // baseboard
  });
  const wallMat = noOutline(new THREE.MeshBasicMaterial({ map: wallTex }));
  const front = new THREE.Mesh(new THREE.PlaneGeometry(RX * 2, RH), wallMat);
  front.position.set(0, RH / 2, RZF); scene.add(front);
  const back = new THREE.Mesh(new THREE.PlaneGeometry(RX * 2, RH), wallMat);
  back.position.set(0, RH / 2, RZB); back.rotation.y = Math.PI; scene.add(back);
  const left = new THREE.Mesh(new THREE.PlaneGeometry(RZB - RZF, RH), wallMat);
  left.position.set(-RX, RH / 2, (RZB + RZF) / 2); left.rotation.y = Math.PI / 2; scene.add(left);
  const right = new THREE.Mesh(new THREE.PlaneGeometry(RZB - RZF, RH), wallMat);
  right.position.set(RX, RH / 2, (RZB + RZF) / 2); right.rotation.y = -Math.PI / 2; scene.add(right);

  // ink edges
  for (const [x, z] of [[-RX, RZF], [RX, RZF], [-RX, RZB], [RX, RZB]]) inkLine([x, 0, z], [x, RH, z]);
  inkLine([-RX, RH, RZF], [RX, RH, RZF]); inkLine([-RX, 0, RZF], [RX, 0, RZF], 0.02);
  inkLine([-RX, RH, RZF], [-RX, RH, RZB]); inkLine([RX, RH, RZF], [RX, RH, RZB]);
  inkLine([-RX, 0, RZF], [-RX, 0, RZB], 0.02); inkLine([RX, 0, RZF], [RX, 0, RZB], 0.02);

  // ceiling light panels (slightly bowed, with grid lines)
  const lightTex = canvasTex(512, 128, (g, w, h) => {
    g.fillStyle = '#fbfbf8'; g.fillRect(0, 0, w, h);
    g.strokeStyle = '#7d7f86'; g.lineWidth = 7;
    for (let i = 1; i < 6; i++) { const x = i * w / 6; g.beginPath(); g.moveTo(x, 18); g.lineTo(x + 8, h - 18); g.stroke(); }
    g.strokeStyle = '#1a1a1e'; g.lineWidth = 10; g.strokeRect(5, 5, w - 10, h - 10);
  });
  for (const z of [-4.4, -2.85, -1.3, 0.15])
    for (const x of [-4.3, -1.3, 1.9, 4.9]) {
      const p = texPlane(1.75, 0.45, lightTex, x, RH - 0.01, z);
      p.rotation.set(Math.PI / 2, 0, 0.0);
    }

  // --- front wall details
  const z = RZF + 0.02;
  // chalkboard
  box(4.25, 1.45, 0.06, '#b8a98a', -2.05, 1.72, z);           // frame
  const boardTex = canvasTex(1360, 460, (g, w, h) => {
    g.fillStyle = '#2f6b52'; g.fillRect(0, 0, w, h);
    g.fillStyle = '#f2f2ea'; g.font = F(800, 64); g.fillText('BIOLOGY FINAL', 40, 110);
    g.font = F(600, 40); g.fillText('10:00 – 11:30', 40, 175);
    g.font = F(800, 40); g.fillStyle = '#f4e27a'; g.fillText('NO PHONES · NO TALKING', 40, 340);
    g.fillStyle = '#f2f2ea'; g.font = F(600, 38); g.fillText('Good luck!', 1000, 340);
    // DNA helix doodle
    g.strokeStyle = '#f2f2ea'; g.lineWidth = 6;
    for (const ph of [0, Math.PI]) { g.beginPath(); for (let x = 0; x <= 360; x += 4) { const y = 150 + 45 * Math.sin(x / 32 + ph); x === 0 ? g.moveTo(700 + x, y) : g.lineTo(700 + x, y); } g.stroke(); }
    g.lineWidth = 3; for (let x = 8; x < 360; x += 22) { g.beginPath(); g.moveTo(700 + x, 150 + 45 * Math.sin(x / 32)); g.lineTo(700 + x, 150 + 45 * Math.sin(x / 32 + Math.PI)); g.stroke(); }
  });
  texPlane(4.05, 1.3, boardTex, -2.05, 1.72, z + 0.035);
  box(4.0, 0.05, 0.1, '#a99a7c', -2.05, 0.98, z + 0.05);       // chalk ledge
  // speaker
  box(0.38, 0.28, 0.08, '#d8d4c9', -0.55, 2.7, z);
  cyl(0.08, 0.08, 0.02, '#55565c', -0.55, 2.7, z + 0.05).rotation.x = Math.PI / 2;
  // exit sign
  const exitTex = canvasTex(256, 110, (g, w, h) => { g.fillStyle = '#2f9e57'; g.fillRect(0, 0, w, h); g.fillStyle = '#fff'; g.font = F(800, 64); g.textAlign = 'center'; g.fillText('EXIT', w / 2, 80); });
  box(0.56, 0.24, 0.05, '#2f9e57', 1.25, 2.62, z);
  texPlane(0.52, 0.2, exitTex, 1.25, 2.62, z + 0.03);
  // door
  box(1.32, 2.28, 0.06, '#33456e', 1.25, 1.14, z);
  box(1.12, 2.12, 0.08, '#5872a6', 1.25, 1.08, z + 0.02);
  box(0.22, 0.62, 0.02, '#d9e6f2', 1.05, 1.62, z + 0.07, scene, { thin: true });
  box(0.16, 0.05, 0.08, '#c9ccd3', 1.6, 1.0, z + 0.1, scene, { thin: true });
  box(0.05, 0.16, 0.05, '#c9ccd3', 1.67, 1.05, z + 0.08, scene, { thin: true });
  // clock
  const clockTex = canvasTex(256, 256, (g, w) => {
    g.fillStyle = '#fff'; g.beginPath(); g.arc(128, 128, 120, 0, 7); g.fill();
    g.lineWidth = 16; g.strokeStyle = '#1b1b1f'; g.stroke();
    g.lineWidth = 6; for (let i = 0; i < 12; i++) { const a = i / 12 * Math.PI * 2; g.beginPath(); g.moveTo(128 + 92 * Math.cos(a), 128 + 92 * Math.sin(a)); g.lineTo(128 + 104 * Math.cos(a), 128 + 104 * Math.sin(a)); g.stroke(); }
    g.lineWidth = 9; g.lineCap = 'round';
    const hand = (a, l) => { g.beginPath(); g.moveTo(128, 128); g.lineTo(128 + l * Math.sin(a), 128 - l * Math.cos(a)); g.stroke(); };
    hand((10 + 42 / 60) / 12 * Math.PI * 2, 55); hand(42 / 60 * Math.PI * 2, 85);
  });
  cyl(0.19, 0.19, 0.04, '#1b1b1f', 2.6, 2.48, z).rotation.x = Math.PI / 2;
  texPlane(0.36, 0.36, clockTex, 2.6, 2.48, z + 0.03);
  // lockdown poster
  const lockTex = canvasTex(220, 300, (g, w, h) => {
    g.fillStyle = '#fafaf6'; g.fillRect(0, 0, w, h);
    g.fillStyle = '#d23a3a'; g.fillRect(0, 0, w, 62); g.fillStyle = '#fff'; g.font = F(800, 34); g.fillText('LOCKDOWN', 14, 44);
    g.fillStyle = '#d23a3a'; g.font = F(700, 26); ['1 LOCK', '2 LIGHTS', '3 OUT OF', '   SIGHT'].forEach((s, i) => g.fillText(s, 16, 110 + i * 46));
  });
  box(0.48, 0.66, 0.02, '#fafaf6', 3.05, 1.82, z, scene, { thin: true });
  texPlane(0.46, 0.63, lockTex, 3.05, 1.82, z + 0.015);

  // --- left wall: window with blinds
  const blindTex = canvasTex(256, 256, (g, w, h) => {
    g.fillStyle = '#e9ecf1'; g.fillRect(0, 0, w, h);
    g.fillStyle = '#9aa1ad'; for (let y = 0; y < h; y += 18) g.fillRect(0, y, w, 5);
  });
  const wl = new THREE.Group(); wl.position.set(-RX + 0.03, 1.75, -3.4); wl.rotation.y = Math.PI / 2; scene.add(wl);
  box(2.6, 1.6, 0.06, '#5a6170', 0, 0, 0, wl);
  texPlane(2.45, 1.45, blindTex, 0, 0, 0.04, 0, wl);
  const wl2 = wl.clone(); wl2.position.z = -0.6; scene.add(wl2);

  // --- right wall: bulletin board
  const rb = new THREE.Group(); rb.position.set(RX - 0.03, 1.7, -2.4); rb.rotation.y = -Math.PI / 2; scene.add(rb);
  box(2.4, 1.3, 0.05, '#7b5233', 0, 0, 0, rb);
  const corkTex = canvasTex(480, 260, (g, w, h) => {
    g.fillStyle = '#b07a4c'; g.fillRect(0, 0, w, h);
    const cols = ['#f2efe4', '#f4d77a', '#9fd0e8', '#f2b6b6', '#f2efe4', '#bfe3b0'];
    for (let i = 0; i < 10; i++) { g.fillStyle = cols[i % cols.length]; const x = 20 + (i % 5) * 92, y = 20 + Math.floor(i / 5) * 120; g.fillRect(x, y, 70, 95); g.fillStyle = '#c55'; g.fillRect(x + 30, y + 4, 9, 9); }
  });
  texPlane(2.3, 1.2, corkTex, 0, 0, 0.03, 0, rb);
}

// ---------------------------------------------------------------------------
// furniture
// ---------------------------------------------------------------------------
const DESK_TOP = '#e3b46c', METAL = '#8e939e', CHAIR = '#55678f';
function desk(x, z, opts = {}) {
  const g = new THREE.Group(); g.position.set(x, 0, z); scene.add(g);
  const w = opts.w || 1.1, d = opts.d || 0.62, h = opts.h || 0.74;
  box(w, 0.045, d, DESK_TOP, 0, h, 0, g);
  for (const sx of [-1, 1]) for (const sz of [-1, 1]) cyl(0.02, 0.02, h, METAL, sx * (w / 2 - 0.06), h / 2, sz * (d / 2 - 0.06), g, 8);
  if (opts.stuff) {
    if (opts.stuff.includes('paper')) box(0.22, 0.004, 0.29, '#f7f6f0', -0.15, h + 0.025, 0.02, g, { thin: true }).rotation.y = 0.15;
    if (opts.stuff.includes('pencil')) { const p = cyl(0.008, 0.008, 0.18, '#f2c230', 0.12, h + 0.03, 0.05, g, 6); p.rotation.z = Math.PI / 2; p.rotation.y = 0.4; }
    if (opts.stuff.includes('laptop')) { box(0.34, 0.015, 0.24, '#3a3e48', 0.15, h + 0.03, 0.0, g); const s = box(0.34, 0.22, 0.012, '#2a2d35', 0.15, h + 0.14, -0.12, g); s.rotation.x = -0.25; }
  }
  return g;
}
function chair(x, z, rot = 0, color = CHAIR) {
  const g = new THREE.Group(); g.position.set(x, 0, z); g.rotation.y = rot; scene.add(g);
  box(0.46, 0.04, 0.44, color, 0, 0.45, 0, g);
  const back = box(0.48, 0.34, 0.035, color, 0, 0.78, 0.23, g); back.rotation.x = -0.06;
  for (const sx of [-1, 1]) {
    cyl(0.015, 0.015, 0.45, METAL, sx * 0.2, 0.225, -0.18, g, 8);
    cyl(0.015, 0.015, 0.95, METAL, sx * 0.2, 0.475, 0.21, g, 8);
  }
  return g;
}

// ---------------------------------------------------------------------------
// characters
// ---------------------------------------------------------------------------
const SKIN = { light: '#f1c8a2', tan: '#d9a77c', brown: '#a8714a', dark: '#7a4e33' };
function head(parent, { skin, hair, style, face = false, glasses = false }) {
  const h = new THREE.Group(); parent.add(h);
  const s = sph(0.155, skin, 0, 0, 0, h); s.scale.set(1, 1.06, 0.98);
  sph(0.035, skin, -0.152, -0.01, 0.0, h); sph(0.035, skin, 0.152, -0.01, 0.0, h); // ears
  if (style === 'bowl') { // hair cap covering top/back
    const cap = new THREE.Mesh(new THREE.SphereGeometry(0.168, 28, 16, 0, Math.PI * 2, 0, Math.PI * 0.5), M(hair));
    cap.position.y = 0.01; cap.rotation.x = face ? -0.35 : 0.12; h.add(cap);
  } else if (style === 'bun') {
    const cap = new THREE.Mesh(new THREE.SphereGeometry(0.165, 28, 16, 0, Math.PI * 2, 0, Math.PI * 0.55), M(hair));
    cap.position.y = 0.005; cap.rotation.x = face ? -0.3 : 0.2; h.add(cap);
    sph(0.075, hair, 0, 0.17, face ? -0.04 : 0.03, h);
  } else if (style === 'curly') {
    for (let i = 0; i < 9; i++) { const a = i / 9 * Math.PI * 2; sph(0.07, hair, Math.cos(a) * 0.11, 0.1 + 0.02 * Math.sin(i * 3), Math.sin(a) * 0.1, h); }
    sph(0.12, hair, 0, 0.1, 0.02, h);
  } else if (style === 'short') {
    const cap = new THREE.Mesh(new THREE.SphereGeometry(0.163, 28, 16, 0, Math.PI * 2, 0, Math.PI * 0.45), M(hair));
    cap.rotation.x = face ? -0.2 : 0.15; h.add(cap);
  }
  if (face) { // teacher faces camera: glasses + mouth
    if (glasses) for (const sx of [-1, 1]) {
      const ring = new THREE.Mesh(new THREE.TorusGeometry(0.045, 0.011, 8, 24), INK);
      ring.position.set(sx * 0.055, 0.02, 0.15); h.add(ring);
      const lens = new THREE.Mesh(new THREE.CircleGeometry(0.04, 20), noOutline(new THREE.MeshBasicMaterial({ color: '#ffffff' })));
      lens.position.set(sx * 0.055, 0.02, 0.152); h.add(lens);
      const pupil = new THREE.Mesh(new THREE.CircleGeometry(0.014, 12), INK); pupil.position.set(sx * 0.055, 0.02, 0.155); h.add(pupil);
    }
    const mouth = new THREE.Mesh(new THREE.BoxGeometry(0.04, 0.008, 0.01), INK); mouth.position.set(0, -0.07, 0.15); h.add(mouth);
  }
  return h;
}
// seated student facing -z (away from camera)
function student(x, z, { top, collar, pants, skin, hair, style, shoes = '#2b2b33', scale = 1.12 }) {
  const g = new THREE.Group(); g.position.set(x, 0, z); g.scale.setScalar(scale); scene.add(g);
  const seat = 0.47;
  const torso = caps(0.16, 0.26, top, g); torso.scale.set(1.28, 1, 0.82); torso.position.set(0, seat + 0.3, 0.05);
  for (const sx of [-1, 1]) {
    sph(0.105, top, sx * 0.2, seat + 0.47, 0.05, g).scale.set(1, 0.9, 1);       // puffy shoulder
    limb([sx * 0.22, seat + 0.45, 0.04], [sx * 0.2, seat + 0.25, -0.12], 0.075, top, g);   // upper arm
    limb([sx * 0.2, seat + 0.25, -0.12], [sx * 0.1, seat + 0.3, -0.38], 0.065, top, g);    // forearm on desk
    limb([sx * 0.1, seat + 0.05, 0.0], [sx * 0.11, seat + 0.05, -0.32], 0.075, pants, g); // thigh
    limb([sx * 0.11, seat + 0.03, -0.32], [sx * 0.12, 0.08, -0.34], 0.065, pants, g);    // shin
    box(0.1, 0.07, 0.18, shoes, sx * 0.12, 0.035, -0.38, g);
  }
  if (collar) { const c = cyl(0.085, 0.1, 0.06, collar, 0, seat + 0.55, 0.05, g); }
  cyl(0.055, 0.055, 0.08, skin, 0, seat + 0.6, 0.05, g);
  const hd = head(g, { skin, hair, style }); hd.position.set(0, seat + 0.77, 0.06);
  return g;
}
function teacher(x, z) {
  const g = new THREE.Group(); g.position.set(x, 0, z); g.rotation.y = -0.15; g.scale.setScalar(1.12); scene.add(g);
  const top = CLOTHES.teacherTop, pants = CLOTHES.teacherPants, skin = SKIN.light;
  for (const sx of [-1, 1]) {
    limb([sx * 0.09, 0.82, 0], [sx * 0.1, 0.1, 0.0], 0.07, pants, g);
    box(0.1, 0.07, 0.2, '#1f2028', sx * 0.1, 0.035, 0.04, g);
  }
  const torso = caps(0.16, 0.36, top, g); torso.scale.set(1.2, 1, 0.8); torso.position.set(0, 1.1, 0);
  for (const sx of [-1, 1]) sph(0.1, top, sx * 0.19, 1.34, 0, g);
  limb([-0.21, 1.32, 0], [-0.27, 0.95, 0.04], 0.065, top, g);
  limb([-0.27, 0.95, 0.04], [-0.22, 0.72, 0.1], 0.055, top, g);
  sph(0.05, skin, -0.22, 0.68, 0.11, g);
  limb([0.21, 1.32, 0], [0.26, 1.05, 0.12], 0.065, top, g);
  limb([0.26, 1.05, 0.12], [0.08, 1.08, 0.22], 0.055, top, g);
  sph(0.05, skin, 0.05, 1.09, 0.24, g);
  cyl(0.05, 0.05, 0.1, skin, 0, 1.5, 0, g);
  const hd = head(g, { skin, hair: '#b5452f', style: 'bun', face: true, glasses: true });
  hd.position.set(0, 1.68, 0);
  return g;
}

// ---------------------------------------------------------------------------
// player POV: desk, exam, arms
// ---------------------------------------------------------------------------
const pov = new THREE.Group(); scene.add(pov);
function buildPOV() {
  const dz = 1.95, h = 0.74;
  desk(0, dz, { w: 1.15, d: 0.7 });
  chair(0, 2.6, 0); // own chair (seen when looking down)
  // exam paper
  const examTex = canvasTex(520, 680, (g, w, hh) => {
    g.fillStyle = '#fbfaf5'; g.fillRect(0, 0, w, hh);
    g.fillStyle = '#16161a'; g.font = F(800, 30); g.fillText('BIOLOGY — FINAL EXAM', 30, 52);
    g.font = F(600, 22); g.fillText('Name:  Noah R.', 30, 86);
    g.strokeStyle = '#9aa3b8'; g.lineWidth = 5;
    for (let i = 0; i < 10; i++) { const y = 140 + i * 52; g.beginPath(); g.moveTo(30, y); g.lineTo(30 + (i % 3 === 1 ? 170 : 210), y); g.stroke(); }
    const filled = [[0, 1], [1, 0], [2, 3], [3, 2], [4, 1], [5, 0]];
    g.lineWidth = 3; g.strokeStyle = '#16161a';
    for (let r = 0; r < 10; r++) for (let c = 0; c < 4; c++) {
      g.beginPath(); g.arc(300 + c * 48, 130 + r * 52, 15, 0, 7);
      if (filled.some(([a, b]) => a === r && b === c)) { g.fillStyle = '#16161a'; g.fill(); } else g.stroke();
    }
  });
  const paperBox = box(0.27, 0.004, 0.35, '#fbfaf5', 0.0, h + 0.027, dz + 0.06, scene, { thin: true });
  paperBox.rotation.y = 0.06;
  const pp = new THREE.Mesh(new THREE.PlaneGeometry(0.27, 0.35), noOutline(new THREE.MeshBasicMaterial({ map: examTex })));
  pp.rotation.set(-Math.PI / 2, 0, 0.06); pp.position.set(0.0, h + 0.03, dz + 0.06); scene.add(pp);
  // pencil case (maroon) + water bottle
  const pc = box(0.3, 0.07, 0.11, '#b14f6b', -0.2, h + 0.057, dz - 0.13); pc.rotation.y = -0.08;
  cyl(0.052, 0.052, 0.27, '#c8ccd6', 0.48, h + 0.16, dz - 0.25);
  cyl(0.048, 0.052, 0.07, '#3b4150', 0.48, h + 0.33, dz - 0.25);
  // backpacks on neighbours' chairs: purple (ZOE tag) and red
  const bp1 = caps(0.13, 0.12, '#8a55d6'); bp1.scale.set(1, 1, 0.65); bp1.position.set(-0.56, 0.86, 1.4); bp1.rotation.z = 0.15;
  const tagTex = canvasTex(128, 64, (g, w, hh) => { g.fillStyle = '#fff'; g.fillRect(0, 0, w, hh); g.fillStyle = '#16161a'; g.font = F(800, 38); g.fillText('ZOE', 18, 46); });
  const tag = box(0.09, 0.05, 0.005, '#ffffff', -0.62, 0.8, 1.49, scene, { thin: true }); tag.rotation.z = 0.5;
  const tp = texPlane(0.085, 0.045, tagTex, -0.62, 0.8, 1.496); tp.rotation.z = 0.5;
  chair(-0.62, 1.26, 0.1);
  const bp2 = caps(0.12, 0.1, '#d9533f'); bp2.scale.set(1, 1, 0.7); bp2.position.set(-0.27, 0.66, 1.12);
}
// arms parented to camera rig so they stay "attached" to the player's body
const body = new THREE.Group(); scene.add(body);
function buildArms() {
  const sleeve = CLOTHES.playerSleeve, skin = SKIN.light;
  limb([-0.34, 0.86, 2.6], [-0.15, 0.795, 2.04], 0.062, sleeve, body);
  limb([0.34, 0.86, 2.6], [0.15, 0.795, 2.02], 0.062, sleeve, body);
  sph(0.064, skin, -0.13, 0.79, 1.98, body).scale.set(1, 0.85, 1.1);
  sph(0.064, skin, 0.13, 0.79, 1.96, body).scale.set(1, 0.85, 1.1);
  // pencil in right hand
  const p = cyl(0.007, 0.007, 0.2, '#f1bf2c', 0.17, 0.83, 1.9, body, 8); p.rotation.set(0.7, 0, -0.75);
}

// ---------------------------------------------------------------------------
// populate
// ---------------------------------------------------------------------------
await Promise.all([700,800,900,600].map(w=>document.fonts.load(F(w,40))));
buildRoom();
buildPOV();
buildArms();
// desk grid
const cols = [-3.75, -1.65, 0.15, 2.45, 4.4];
const rows = [-3.0, -1.55, -0.1];
for (const z of rows) for (const x of cols) {
  if (x === 0.15 && z === -0.1) { desk(0.15, -0.95, { stuff: 'paper' }); chair(0.15, -0.25, 0); continue; }
  desk(x, z, { stuff: (x + z) % 2 > 0.5 ? 'paper pencil' : 'paper' });
  chair(x, z + 0.55, 0);
}
desk(-3.3, -4.35, { w: 1.5, d: 0.75, stuff: 'laptop' });   // teacher desk
student(0.15, -0.3, { scale: 1.25, top: CLOTHES.frontShirt, collar: CLOTHES.frontCollar, pants: CLOTHES.frontPants, skin: SKIN.tan, hair: '#4a2f22', style: 'bowl' });
student(-1.65, -1.05, { top: CLOTHES.bunGirlTop, pants: CLOTHES.bunGirlPants, skin: SKIN.brown, hair: '#1d1a1a', style: 'bun' });
student(2.45, 0.4, { top: CLOTHES.rightKidTop, pants: CLOTHES.rightKidPants, skin: SKIN.dark, hair: '#151313', style: 'short' });
student(-3.75, 0.4, { top: CLOTHES.leftKidTop, pants: CLOTHES.leftKidPants, skin: SKIN.light, hair: '#5a3a24', style: 'short' });
student(-3.75, -2.5, { top: CLOTHES.backKidTop, pants: '#3a3f4f', skin: SKIN.tan, hair: '#2a1d16', style: 'short' });
teacher(-0.75, -4.55);

// lights
scene.add(new THREE.AmbientLight('#ffffff', 2.3));
const sun = new THREE.DirectionalLight('#ffffff', 1.05); sun.position.set(-2, 5, 4); scene.add(sun);

// ---------------------------------------------------------------------------
// camera + fisheye pass
// ---------------------------------------------------------------------------
const camera = new THREE.PerspectiveCamera(120, W / H, 0.03, 60);
camera.rotation.order = 'YXZ';
const effect = new OutlineEffect(renderer, { defaultThickness: 0.0045, defaultColor: [0.07, 0.07, 0.08] });
const rt = new THREE.WebGLRenderTarget(W * SS, H * SS, { samples: 4, type: THREE.HalfFloatType });
const fisheye = new THREE.ShaderMaterial({
  uniforms: { tSrc: { value: rt.texture }, k: { value: 1.0 }, aspect: { value: W / H } },
  vertexShader: `varying vec2 vUv; void main(){ vUv = uv; gl_Position = vec4(position.xy, 0., 1.); }`,
  fragmentShader: `
    uniform sampler2D tSrc; uniform float k; uniform float aspect; varying vec2 vUv;
    vec3 toSRGB(vec3 c){ return mix(c*12.92, 1.055*pow(c, vec3(1./2.4)) - 0.055, step(0.0031308, c)); }
    void main(){
      vec2 p = vUv*2.0-1.0; p.x *= aspect;
      float rc2 = aspect*aspect + 1.0;
      vec2 q = p * (1.0 + k*dot(p,p)) / (1.0 + k*rc2);
      q.x /= aspect;
      vec3 col = texture2D(tSrc, q*0.5+0.5).rgb;
      // soft vignette
      float v = smoothstep(1.55, 0.6, length(p*vec2(1.0,0.9)));
      col *= mix(0.9, 1.0, v);
      gl_FragColor = vec4(toSRGB(col), 1.0);
    }`,
  depthTest: false, depthWrite: false,
});
const quadScene = new THREE.Scene();
const quadCam = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);
quadScene.add(new THREE.Mesh(new THREE.PlaneGeometry(2, 2), fisheye));

// ---------------------------------------------------------------------------
// animation timeline (matches reference: drift left, hold, quick tilt to paper)
// ---------------------------------------------------------------------------
const D2R = Math.PI / 180;
const ease = t => t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
const clamp01 = t => Math.min(1, Math.max(0, t));
function camAt(t) {
  // yaw (+ = look left), pitch (+ = look up)
  let yaw, pitch;
  const a = ease(clamp01(t / 0.6));
  yaw = -4 + 6.5 * a + 1.2 * Math.sin(t * 0.9);            // slow drift left
  pitch = 5 - 1.0 * a + 0.5 * Math.sin(t * 1.7);
  const tilt = ease(clamp01((t - 2.65) / 0.6));              // tilt down to exam
  yaw = yaw * (1 - tilt) + (-1.5 + 0.8 * Math.sin(t * 1.3)) * tilt;
  pitch = pitch * (1 - tilt) + (-36 + 0.8 * Math.sin(t * 2.1)) * tilt;
  const roll = 0.6 * Math.sin(t * 1.1) * D2R;
  const pos = new THREE.Vector3(0.03, 1.15 + 0.006 * Math.sin(t * 2.4) - 0.04 * tilt, 2.66 - 0.08 * tilt);
  return { yaw: yaw * D2R, pitch: pitch * D2R, roll, pos };
}
const SUBS = [
  [0.25, 1.35, 'Ten more minutes,'],
  [1.35, 2.45, 'people.'],
  [2.45, 3.45, 'Eyes on your own'],
  [3.45, 9.0, 'paper.'],
];
const titleEl = document.getElementById('title'), subEl = document.getElementById('subtxt'), hudEl = document.getElementById('hud');
function hudAt(t) {
  titleEl.style.opacity = clamp01(t / 0.3);
  const s = SUBS.find(([a, b]) => t >= a && t < b);
  subEl.textContent = s ? s[2] : '';
  if (s) { const k = clamp01((t - s[0]) / 0.09); subEl.style.transform = `translateX(-50%) scale(${0.88 + 0.12 * k})`; }
}
window.setHud = on => { hudEl.style.display = on ? 'block' : 'none'; };
window.renderAt = (t) => {
  const c = camAt(t);
  camera.position.copy(c.pos);
  camera.rotation.set(c.pitch, c.yaw, c.roll);
  // arms follow body gently (small hand motion while writing)
  body.position.set(0.004 * Math.sin(t * 3.1), 0.003 * Math.sin(t * 4.3), 0);
  renderer.setRenderTarget(rt);
  effect.render(scene, camera);
  renderer.setRenderTarget(null);
  renderer.render(quadScene, quadCam);
  hudAt(t);
};
window.sceneReady = (async () => {
  await document.fonts.ready;
  return true;
})();
