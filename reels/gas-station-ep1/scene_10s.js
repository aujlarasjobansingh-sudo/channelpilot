// EPISODE 1 — "The Late-Night Gas Station Shift" — POV cashier scene.
// Same visual language as the classroom reel: toon shading, ink outlines, stereographic wide lens
// (f = 540px on a 1280px-tall frame), deliberate camera moves (still → smooth move → hold → snap).
// Camera eye at origin (x=0, z=0, y=EYE), looking down -z toward the glass front doors.
// Window API (used by render.js): window.sceneReady, window.renderAt(seconds), window.setHud(bool)
import * as THREE from 'three';
import { OutlineEffect } from 'three/addons/effects/OutlineEffect.js';

// ---------------------------------------------------------------------------
// palette
// ---------------------------------------------------------------------------
const C = {
  ceiling: '#cfccc4', wall: '#ebe6d8', stripe: '#d2483c', stripe2: '#f2b632', floor: '#d5d7d0', floorLine: '#bcc0b8',
  counterTop: '#7d828c', counterFront: '#2e3b55', counterTrim: '#c9ccd2', metal: '#a3a9b2', darkMetal: '#3a3e47',
  frame: '#b9bec7', kick: '#5b606b', light: '#fbfaf0', skin: '#d9a079', polo: '#1f3460', rag: '#c9d3dc',
  phone: '#1b1d23', cooler: '#30343c', shelf: '#9aa1ab', shelfDark: '#6f7680',
};
const EYE = 1.62;
const W = 720, H = 1280, FOCAL = 540, SRC_W = 1350, SRC_H = 2400;
const R_C = Math.hypot(W / 2, H / 2);
const TAN_Y = (H / 2) / R_C * Math.tan(2 * Math.atan(R_C / (2 * FOCAL)));
const TAN_X = TAN_Y * (W / H);
const SRC_FOV = 2 * Math.atan(TAN_Y) * 180 / Math.PI;

const canvas = document.getElementById('c');
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, preserveDrawingBuffer: true });
renderer.setPixelRatio(1); renderer.setSize(W, H, false);
const scene = new THREE.Scene();
scene.background = new THREE.Color(C.ceiling);

// ---------------------------------------------------------------------------
// helpers (same toolkit as the classroom reel)
// ---------------------------------------------------------------------------
const grad = new THREE.DataTexture(new Uint8Array([196, 234, 255]), 3, 1, THREE.RedFormat);
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
const add = (m, p) => { (p || scene).add(m); return m; };
function box(w, h, d, color, x, y, z, parent, opts) {
  const m = add(new THREE.Mesh(new THREE.BoxGeometry(w, h, d), typeof color === 'string' ? M(color, opts) : color), parent);
  m.position.set(x, y, z); return m;
}
function cyl(rt, rb, h, color, x, y, z, parent, seg = 24) {
  const m = add(new THREE.Mesh(new THREE.CylinderGeometry(rt, rb, h, seg), mat(color)), parent); m.position.set(x, y, z); return m;
}
function sph(r, color, x, y, z, parent) {
  const m = add(new THREE.Mesh(new THREE.SphereGeometry(r, 32, 20), mat(color)), parent); m.position.set(x, y, z); return m;
}
function capsule(r, len, color, parent) { return add(new THREE.Mesh(new THREE.CapsuleGeometry(r, len, 8, 16), mat(color)), parent); }
function orient(mesh, A, B) {        // place a unit-height Y-aligned mesh between A and B
  mesh.position.copy(A).add(B).multiplyScalar(0.5);
  mesh.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), B.clone().sub(A).normalize());
  mesh.scale.set(1, A.distanceTo(B), 1);
}
function inkLine(a, b, t = 0.02) {
  const m = add(new THREE.Mesh(new THREE.CylinderGeometry(t / 2, t / 2, 1, 6), INK));
  orient(m, new THREE.Vector3(...a), new THREE.Vector3(...b)); return m;
}
function canvasTex(w, h, draw) {
  const c = document.createElement('canvas'); c.width = w; c.height = h;
  draw(c.getContext('2d'), w, h);
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 16;
  t.userData.canvas = c; return t;
}
function texPlane(w, h, tex, x, y, z, parent, transparent = true) {
  const m = add(new THREE.Mesh(new THREE.PlaneGeometry(w, h), noOutline(new THREE.MeshBasicMaterial({ map: tex, transparent }))), parent);
  m.position.set(x, y, z); return m;
}
function rr(g, x, y, w, h, r) { g.beginPath(); g.moveTo(x + r, y); g.arcTo(x + w, y, x + w, y + h, r); g.arcTo(x + w, y + h, x, y + h, r); g.arcTo(x, y + h, x, y, r); g.arcTo(x, y, x + w, y, r); g.closePath(); }
const F = (wt, px) => `${wt} ${px}px Rubik, sans-serif`;
await Promise.all([500, 600, 700, 800, 900].map(w => document.fonts.load(F(w, 40))));
let seed = 7; const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647;

// ---------------------------------------------------------------------------
// room
// ---------------------------------------------------------------------------
const XL = -4.6, XR = 3.6, ZF = -7.0, ZB = 1.3, RH = 3.0;
const lightTex = canvasTex(400, 200, (g, w, h) => {
  g.fillStyle = C.light; g.fillRect(0, 0, w, h);
  g.strokeStyle = '#a7a6a0'; g.lineWidth = 5;
  for (let i = 1; i < 4; i++) { const x = i * w / 4; g.beginPath(); g.moveTo(x, 14); g.lineTo(x, h - 14); g.stroke(); }
  g.beginPath(); g.moveTo(14, h / 2); g.lineTo(w - 14, h / 2); g.stroke();
});
function buildRoom() {
  const floorTex = canvasTex(1024, 1024, (g, w, h) => {
    g.fillStyle = C.floor; g.fillRect(0, 0, w, h);
    g.fillStyle = '#cdd0c8'; for (let i = 0; i < 8; i++) for (let j = 0; j < 8; j++) if ((i + j) % 2) g.fillRect(i * w / 8, j * h / 8, w / 8, h / 8);
    g.strokeStyle = C.floorLine; g.lineWidth = 3;
    for (let i = 0; i <= 8; i++) { const p = i * w / 8; g.beginPath(); g.moveTo(p, 0); g.lineTo(p, h); g.stroke(); g.beginPath(); g.moveTo(0, p); g.lineTo(w, p); g.stroke(); }
  });
  floorTex.wrapS = floorTex.wrapT = THREE.RepeatWrapping; floorTex.repeat.set((XR - XL) / 4.8, (ZB - ZF) / 4.8);
  const floor = add(new THREE.Mesh(new THREE.PlaneGeometry(XR - XL, ZB - ZF), noOutline(new THREE.MeshBasicMaterial({ map: floorTex }))));
  floor.rotation.x = -Math.PI / 2; floor.position.set((XL + XR) / 2, 0, (ZB + ZF) / 2);
  const ceil = add(new THREE.Mesh(new THREE.PlaneGeometry(XR - XL, ZB - ZF), noOutline(new THREE.MeshBasicMaterial({ color: C.ceiling }))));
  ceil.rotation.x = Math.PI / 2; ceil.position.set((XL + XR) / 2, RH, (ZB + ZF) / 2);

  const wallTex = canvasTex(64, 600, (g, w, h) => {   // 1px = 5mm
    g.fillStyle = C.wall; g.fillRect(0, 0, w, h);
    g.fillStyle = C.stripe; g.fillRect(0, h - 2.55 * 200, w, 0.2 * 200);
    g.fillStyle = C.stripe2; g.fillRect(0, h - 2.35 * 200, w, 0.05 * 200);
    g.fillStyle = '#9aa0a8'; g.fillRect(0, h - 24, w, 24);
  });
  const wm = noOutline(new THREE.MeshBasicMaterial({ map: wallTex }));
  const wall = (w, x, z, ry) => { const m = add(new THREE.Mesh(new THREE.PlaneGeometry(w, RH), wm)); m.position.set(x, RH / 2, z); m.rotation.y = ry; };
  wall(XR - XL, (XL + XR) / 2, ZB, Math.PI);
  wall(ZB - ZF, XL, (ZB + ZF) / 2, Math.PI / 2); wall(ZB - ZF, XR, (ZB + ZF) / 2, -Math.PI / 2);
  for (const [x, z] of [[XL, ZF], [XR, ZF], [XL, ZB], [XR, ZB]]) inkLine([x, 0, z], [x, RH, z]);
  inkLine([XL, RH, ZF], [XR, RH, ZF]); inkLine([XL, RH, ZF], [XL, RH, ZB]); inkLine([XR, RH, ZF], [XR, RH, ZB]);
  inkLine([XL, 0, ZF], [XL, 0, ZB], 0.015); inkLine([XR, 0, ZF], [XR, 0, ZB], 0.015);

  // fluorescent troffers
  for (const z of [-1.7, -3.9, -6.1]) for (const x of [-2.7, -0.4, 1.9]) {
    box(1.22, 0.03, 0.62, C.light, x, RH - 0.016, z, null, { flat: true });
    const p = texPlane(1.2, 0.6, lightTex, x, RH - 0.033, z); p.rotation.x = Math.PI / 2;
  }
}

// ---------------------------------------------------------------------------
// front glass wall with animated rain
// ---------------------------------------------------------------------------
const GLASS_Y0 = 0.35, GLASS_Y1 = 2.6;
const rainTex = canvasTex(1400, 360, () => {});
const drops = [], streaks = [];
for (let i = 0; i < 260; i++) streaks.push({ x: rnd() * 1400, y: rnd() * 360, len: 18 + rnd() * 40, sp: 900 + rnd() * 700, a: 0.16 + rnd() * 0.3 });
for (let i = 0; i < 120; i++) drops.push({ x: rnd() * 1400, y0: rnd() * 360, sp: 6 + rnd() * 30, r: 2 + rnd() * 3, ph: rnd() * 10 });
function drawRain(t) {
  const g = rainTex.userData.canvas.getContext('2d'), w = 1400, h = 360;
  const bg = g.createLinearGradient(0, 0, 0, h); bg.addColorStop(0, '#05070c'); bg.addColorStop(1, '#0a0f17');
  g.fillStyle = bg; g.fillRect(0, 0, w, h);
  // very faint distant sodium light far out in the lot + wet-ground glints
  const glow = g.createRadialGradient(1010, 150, 2, 1010, 150, 60); glow.addColorStop(0, 'rgba(255,170,90,0.20)'); glow.addColorStop(1, 'rgba(255,170,90,0)');
  g.fillStyle = glow; g.fillRect(900, 60, 220, 200);
  g.fillStyle = 'rgba(255,170,90,0.10)'; g.fillRect(990, 250, 40, 3); g.fillRect(1000, 262, 22, 2);
  // interior reflection sheen
  const sh = g.createLinearGradient(0, 0, w, h); sh.addColorStop(0.2, 'rgba(200,215,235,0)'); sh.addColorStop(0.45, 'rgba(200,215,235,0.05)'); sh.addColorStop(0.55, 'rgba(200,215,235,0)');
  g.fillStyle = sh; g.fillRect(0, 0, w, h);
  // falling rain outside
  g.lineCap = 'round';
  for (const s of streaks) {
    const y = ((s.y + t * s.sp) % (h + 80)) - 40, x = s.x + y * 0.12;
    g.strokeStyle = `rgba(190,205,225,${s.a})`; g.lineWidth = 2.4; g.beginPath(); g.moveTo(x, y); g.lineTo(x + s.len * 0.12, y + s.len); g.stroke();
  }
  // water running down the glass
  for (const d of drops) {
    const y = (d.y0 + t * d.sp + 4 * Math.sin(t * 2 + d.ph)) % (h + 20);
    g.strokeStyle = 'rgba(170,190,215,0.16)'; g.lineWidth = d.r * 0.9;
    g.beginPath(); g.moveTo(d.x, Math.max(0, y - 30 - d.sp)); g.lineTo(d.x + 1, y); g.stroke();
    g.fillStyle = 'rgba(205,220,240,0.42)'; g.beginPath(); g.arc(d.x + 1, y, d.r, 0, 7); g.fill();
    g.fillStyle = 'rgba(255,255,255,0.55)'; g.beginPath(); g.arc(d.x, y - d.r * 0.35, d.r * 0.35, 0, 7); g.fill();
  }
  rainTex.needsUpdate = true;
}
function buildFront() {
  const z = ZF;
  const glass = add(new THREE.Mesh(new THREE.PlaneGeometry(XR - XL, GLASS_Y1 - GLASS_Y0), noOutline(new THREE.MeshBasicMaterial({ map: rainTex }))));
  glass.position.set((XL + XR) / 2, (GLASS_Y0 + GLASS_Y1) / 2, z);
  box(XR - XL, GLASS_Y0, 0.12, C.kick, (XL + XR) / 2, GLASS_Y0 / 2, z);                  // kick wall
  const hdr = add(new THREE.Mesh(new THREE.PlaneGeometry(XR - XL, RH - GLASS_Y1), noOutline(new THREE.MeshBasicMaterial({ color: C.wall }))));
  hdr.position.set((XL + XR) / 2, (GLASS_Y1 + RH) / 2, z + 0.001);
  box(XR - XL, 0.2, 0.02, C.stripe, (XL + XR) / 2, 2.65, z + 0.01, null, { thin: true });
  box(XR - XL, 0.08, 0.1, C.frame, (XL + XR) / 2, GLASS_Y1, z + 0.02);                  // head rail
  box(XR - XL, 0.06, 0.1, C.frame, (XL + XR) / 2, GLASS_Y0 + 0.02, z + 0.02);           // sill
  for (const x of [-4.5, -2.9, -1.3, 0.15, 2.85, 3.5]) box(0.08, GLASS_Y1 - GLASS_Y0, 0.1, C.frame, x, (GLASS_Y0 + GLASS_Y1) / 2, z + 0.02);
  // double doors (x 0.45 .. 2.55), floor to 2.3m
  const dz = z + 0.06;
  box(2.7, 0.06, 0.12, C.frame, 1.5, 0.03, dz);                                          // threshold
  for (const [cx, hx] of [[0.825, 1.38], [2.175, 1.62]]) {
    const leaf = new THREE.Group(); leaf.position.set(cx, 0, dz); scene.add(leaf);
    box(1.33, 0.1, 0.06, C.frame, 0, 2.4, 0, leaf); box(1.33, 0.18, 0.06, C.frame, 0, 0.09, 0, leaf);
    box(0.08, 2.45, 0.06, C.frame, -0.63, 1.22, 0, leaf); box(0.08, 2.45, 0.06, C.frame, 0.63, 1.22, 0, leaf);
    const dg = add(new THREE.Mesh(new THREE.PlaneGeometry(1.18, 2.17), noOutline(new THREE.MeshBasicMaterial({ map: rainTex }))), leaf);
    dg.position.set(0, 1.265, -0.005);
    const off = (cx - (XL + XR) / 2) / (XR - XL);
    dg.material = noOutline(new THREE.MeshBasicMaterial({ map: rainTex }));
    const uv = dg.geometry.attributes.uv;   // map door glass onto the matching slice of the rain canvas
    for (let i = 0; i < uv.count; i++) {
      const u = uv.getX(i), v = uv.getY(i);
      const wx = cx - 0.59 + u * 1.18, wy = 0.18 + v * 2.17;
      uv.setXY(i, (wx - XL) / (XR - XL), (wy - GLASS_Y0) / (GLASS_Y1 - GLASS_Y0));
    }
    uv.needsUpdate = true;
    cyl(0.018, 0.018, 0.6, C.metal, hx - cx, 1.1, 0.05, leaf, 12);                     // pull handle
    box(0.02, 0.02, 0.06, C.metal, hx - cx, 1.38, 0.03, leaf); box(0.02, 0.02, 0.06, C.metal, hx - cx, 0.82, 0.03, leaf);
  }
  box(2.0, 0.012, 1.0, '#3d424b', 1.5, 0.006, z + 0.65, null, { thin: true });            // floor mat
  // door chime box + OPEN neon + hours decal
  box(0.16, 0.08, 0.06, '#e9e9e4', 1.5, 2.72, z + 0.08);
  const neon = canvasTex(420, 150, (g, w, h) => {
    g.clearRect(0, 0, w, h); g.shadowColor = 'rgba(255,60,60,0.9)'; g.shadowBlur = 22;
    g.strokeStyle = '#ff5b5b'; g.lineWidth = 8; rr(g, 12, 12, w - 24, h - 24, 26); g.stroke();
    g.fillStyle = '#ff6a6a'; g.font = F(800, 82); g.textAlign = 'center'; g.fillText('OPEN', w / 2, 106);
  });
  texPlane(0.84, 0.3, neon, -2.1, 1.95, z + 0.03);
  const hours = canvasTex(256, 140, (g, w, h) => { g.fillStyle = 'rgba(255,255,255,0.85)'; g.font = F(800, 46); g.textAlign = 'center'; g.fillText('OPEN 24/7', w / 2, 60); g.font = F(600, 28); g.fillText('ROUTE 9 FUEL', w / 2, 108); });
  texPlane(0.42, 0.23, hours, 2.175, 1.6, dz - 0.04);
  const push = canvasTex(160, 60, (g, w, h) => { g.fillStyle = 'rgba(255,255,255,0.85)'; g.font = F(800, 40); g.textAlign = 'center'; g.fillText('PUSH', w / 2, 44); });
  texPlane(0.2, 0.075, push, 0.825, 1.3, dz - 0.04);
}

// ---------------------------------------------------------------------------
// coolers (right wall), aisles, ice chest
// ---------------------------------------------------------------------------
function coolerTex(variant) {
  return canvasTex(300, 760, (g, w, h) => {
    const bg = g.createLinearGradient(0, 0, w, 0); bg.addColorStop(0, '#e6f4ff'); bg.addColorStop(0.5, '#f8fcff'); bg.addColorStop(1, '#e2f0fb');
    g.fillStyle = bg; g.fillRect(0, 0, w, h);
    const cols = [['#d8342c', '#b8241e'], ['#2f6fd6', '#1f55b0'], ['#36a852', '#24813b'], ['#f29a2e', '#d27a14'], ['#f4f6f8', '#c9d4dc'], ['#7a3fc4', '#5d2aa0'], ['#f2d23a', '#d2b21a']];
    for (let row = 0; row < 5; row++) {
      const sy = 40 + row * 145;
      const c = cols[(row * 3 + variant * 2) % cols.length], c2 = cols[(row * 5 + variant + 1) % cols.length];
      for (let i = 0; i < 6; i++) {
        const col = i < 3 ? c : c2, x = 14 + i * 46;
        g.fillStyle = col[0]; rr(g, x, sy + 30, 34, 96, 9); g.fill();
        g.fillStyle = col[1]; g.fillRect(x + 10, sy + 14, 14, 20);
        g.fillStyle = 'rgba(255,255,255,0.85)'; g.fillRect(x + 3, sy + 62, 28, 22);
        g.strokeStyle = '#1b1c20'; g.lineWidth = 3; rr(g, x, sy + 30, 34, 96, 9); g.stroke();
      }
      g.fillStyle = '#9aa6b2'; g.fillRect(0, sy + 128, w, 9);
    }
  });
}
function buildCoolers() {
  const x = XR, z0 = -1.4, n = 6, dw = 0.78;
  box(0.7, 2.5, n * dw + 0.12, C.cooler, x - 0.35, 1.25, z0 - n * dw / 2);
  const sign = canvasTex(900, 110, (g, w, h) => { g.fillStyle = '#1f5fbf'; g.fillRect(0, 0, w, h); g.fillStyle = '#fff'; g.font = F(900, 74); g.textAlign = 'center'; g.fillText('COLD DRINKS', w / 2, 82); });
  const sp = texPlane(n * dw - 0.2, 0.26, sign, x - 0.705, 2.36, z0 - n * dw / 2); sp.rotation.y = -Math.PI / 2;
  for (let i = 0; i < n; i++) {
    const zc = z0 - dw / 2 - i * dw;
    const tp = texPlane(dw - 0.08, 1.95, coolerTex(i), x - 0.71, 1.18, zc, null, false); tp.rotation.y = -Math.PI / 2;
    box(0.05, 2.06, 0.04, C.darkMetal, x - 0.72, 1.18, zc + dw / 2 - 0.02);
    box(0.05, 0.06, dw, C.darkMetal, x - 0.72, 2.18, zc); box(0.05, 0.06, dw, C.darkMetal, x - 0.72, 0.18, zc);
    cyl(0.014, 0.014, 0.85, C.metal, x - 0.76, 1.2, zc + dw / 2 - 0.1, null, 10);
  }
}
function productTex(variant, rows = 4) {
  return canvasTex(1024, 512, (g, w, h) => {
    g.fillStyle = '#e9ebee'; g.fillRect(0, 0, w, h);
    const cols = ['#e33b2f', '#f2b51e', '#2f73d8', '#2fa64d', '#f07f22', '#8d4ad0', '#e65b9c', '#1fb3b0', '#c9302c'];
    const rh = h / rows;
    for (let r = 0; r < rows; r++) {
      let x = 8;
      while (x < w - 60) {
        const bw = 52 + Math.floor(rnd() * 34), bh = rh * (0.62 + rnd() * 0.22), y = (r + 1) * rh - 14 - bh;
        const c = cols[Math.floor(rnd() * cols.length + variant) % cols.length];
        g.fillStyle = c; rr(g, x, y, bw, bh, 10); g.fill();
        g.fillStyle = 'rgba(255,255,255,0.9)'; rr(g, x + 8, y + bh * 0.3, bw - 16, bh * 0.28, 6); g.fill();
        g.fillStyle = 'rgba(0,0,0,0.12)'; g.fillRect(x + bw - 12, y + 6, 6, bh - 12);
        g.strokeStyle = '#1b1c20'; g.lineWidth = 4; rr(g, x, y, bw, bh, 10); g.stroke();
        x += bw + 6;
      }
      g.fillStyle = '#8f97a2'; g.fillRect(0, (r + 1) * rh - 14, w, 14);
      g.fillStyle = '#f6f2c8'; for (let px = 30; px < w; px += 120) g.fillRect(px, (r + 1) * rh - 12, 34, 10);
    }
  });
}
function gondola(x, zc, len, signText) {
  const g = new THREE.Group(); g.position.set(x, 0, zc); scene.add(g);
  const hgt = 1.45, wd = 0.82;
  box(wd, 0.14, len, C.shelfDark, 0, 0.07, 0, g);
  box(0.06, hgt, len, C.shelf, 0, hgt / 2, 0, g);
  for (const sx of [-1, 1]) {
    for (let k = 0; k < 4; k++) box(wd / 2 - 0.04, 0.025, len, C.shelf, sx * (wd / 4 + 0.01), 0.2 + k * 0.33, 0, g, { thin: true });
    const p = texPlane(len, hgt - 0.12, productTex(x > -2 ? 1 : 3), sx * (wd / 2 - 0.02), 0.08 + (hgt - 0.12) / 2 + 0.06, 0, g, false);
    p.rotation.y = sx * Math.PI / 2;
  }
  // endcap facing the counter
  box(wd + 0.04, hgt, 0.06, C.shelf, 0, hgt / 2, len / 2 + 0.03, g);
  const ec = texPlane(wd - 0.04, hgt - 0.12, productTex(5, 4), 0, 0.08 + (hgt - 0.12) / 2 + 0.06, len / 2 + 0.065, g, false);
  const sign = canvasTex(400, 160, (c, w, h) => { c.fillStyle = '#d2483c'; rr(c, 6, 6, w - 12, h - 12, 18); c.fill(); c.strokeStyle = '#16161a'; c.lineWidth = 8; rr(c, 6, 6, w - 12, h - 12, 18); c.stroke(); c.fillStyle = '#fff'; c.font = F(900, 70); c.textAlign = 'center'; c.fillText(signText, w / 2, 106); });
  box(wd * 0.9, 0.32, 0.03, '#d2483c', 0, hgt + 0.22, len / 2 + 0.03, g);
  texPlane(wd * 0.88, 0.3, sign, 0, hgt + 0.22, len / 2 + 0.05, g);
  cyl(0.012, 0.012, 0.1, C.metal, 0, hgt + 0.03, len / 2 + 0.03, g, 8);
}
function buildStore() {
  gondola(-1.25, -3.9, 2.9, '2 FOR $5');
  gondola(-3.05, -3.9, 2.9, 'SNACKS');
  // ice chest near the door
  box(1.2, 0.85, 0.7, '#f3f5f7', -0.5, 0.425, -6.4);
  const ice = canvasTex(400, 200, (g, w, h) => { g.fillStyle = '#f3f5f7'; g.fillRect(0, 0, w, h); g.fillStyle = '#2f73d8'; g.font = F(900, 130); g.textAlign = 'center'; g.fillText('ICE', w / 2, 150); });
  texPlane(0.9, 0.45, ice, -0.5, 0.48, -6.045);
  // wet floor sign
  const wf = new THREE.Group(); wf.position.set(0.25, 0, -4.9); wf.rotation.y = 0.5; scene.add(wf);
  const wft = canvasTex(160, 300, (g, w, h) => { g.fillStyle = '#f5cf1f'; g.fillRect(0, 0, w, h); g.fillStyle = '#16161a'; g.font = F(900, 40); g.textAlign = 'center'; g.fillText('WET', w / 2, 170); g.fillText('FLOOR', w / 2, 214); g.beginPath(); g.moveTo(w / 2, 40); g.lineTo(w / 2 + 40, 110); g.lineTo(w / 2 - 40, 110); g.closePath(); g.lineWidth = 7; g.stroke(); });
  for (const s of [-1, 1]) { const p = box(0.3, 0.62, 0.015, '#f5cf1f', 0, 0.31, s * 0.1, wf); p.rotation.x = s * 0.25; const tp = texPlane(0.28, 0.56, wft, 0, 0.31, s * 0.112, wf); tp.rotation.x = s * 0.25; if (s < 0) tp.rotation.y = Math.PI; }
  // trash can by the door
  cyl(0.24, 0.22, 0.9, '#4a515c', -1.0, 0.45, -6.55);
  // magazine / chips rack along the counter side
  box(0.5, 1.1, 0.35, C.shelf, -2.2, 0.55, -1.3);
  const mr = texPlane(0.46, 1.0, productTex(2, 3), -2.2, 0.57, -1.12, null, false);
}

// ---------------------------------------------------------------------------
// counter + items + phone
// ---------------------------------------------------------------------------
const CT = 0.98;                                          // countertop height
const counterZ0 = -0.12, counterZ1 = -0.8;
const phone = new THREE.Group(); scene.add(phone);
const phoneTex = canvasTex(400, 844, () => {});
function buildCounter() {
  const cx0 = -1.6, cx1 = 0.95, w = cx1 - cx0, cxm = (cx0 + cx1) / 2;
  box(w, 0.05, counterZ0 - counterZ1, C.counterTop, cxm, CT - 0.025, (counterZ0 + counterZ1) / 2);
  box(w, CT - 0.05, 0.05, C.counterFront, cxm, (CT - 0.05) / 2, counterZ1 + 0.025);
  box(w + 0.02, 0.03, 0.06, C.counterTrim, cxm, CT - 0.065, counterZ1 + 0.02);
  // side return of the counter (left)
  box(0.05, CT, 1.2, C.counterFront, cx0, CT / 2, counterZ1 + 0.6);
  // register
  box(0.4, 0.09, 0.32, '#2d3038', -0.68, CT + 0.045, -0.5);
  box(0.36, 0.06, 0.06, '#3b3f49', -0.68, CT + 0.06, -0.68);
  const st = cyl(0.025, 0.025, 0.16, '#2d3038', -0.68, CT + 0.17, -0.5);
  const scr = new THREE.Group(); scr.position.set(-0.68, CT + 0.28, -0.52); scr.rotation.x = -0.35; scene.add(scr);
  box(0.36, 0.25, 0.04, '#25282f', 0, 0, 0, scr);
  const posTex = canvasTex(360, 240, (g, w, h) => {
    g.fillStyle = '#1d3d6e'; g.fillRect(0, 0, w, h); g.fillStyle = '#2b5797'; g.fillRect(0, 0, w, 46);
    g.fillStyle = '#fff'; g.font = F(700, 26); g.fillText('ROUTE 9 POS', 14, 32);
    g.font = F(800, 64); g.textAlign = 'right'; g.fillText('$0.00', w - 18, 150);
    g.fillStyle = '#7fe0a0'; g.font = F(600, 22); g.textAlign = 'left'; g.fillText('READY', 16, 214);
  });
  texPlane(0.33, 0.22, posTex, 0, 0, 0.021, scr);
  // card terminal
  box(0.09, 0.04, 0.16, '#26292f', -0.22, CT + 0.02, -0.66);
  box(0.07, 0.002, 0.05, '#7fe0a0', -0.22, CT + 0.041, -0.69, null, { flat: true });
  // candy rack at the front lip
  box(0.5, 0.12, 0.14, '#b9bfc7', 0.55, CT + 0.06, -0.72);
  const candy = canvasTex(500, 120, (g, w, h) => { g.fillStyle = '#d9dde2'; g.fillRect(0, 0, w, h); const cs = ['#e33b2f', '#f2b51e', '#2f73d8', '#2fa64d', '#8d4ad0', '#f07f22']; for (let i = 0; i < 10; i++) { g.fillStyle = cs[i % 6]; rr(g, 6 + i * 49, 18, 42, 92, 6); g.fill(); g.strokeStyle = '#1b1c20'; g.lineWidth = 3; rr(g, 6 + i * 49, 18, 42, 92, 6); g.stroke(); } });
  const cp = texPlane(0.5, 0.12, candy, 0.55, CT + 0.06, -0.638);
  cp.rotation.x = 0; cp.rotation.y = Math.PI;   // faces the cashier
  // coffee cup
  cyl(0.04, 0.032, 0.11, '#f3efe6', -0.98, CT + 0.055, -0.36);
  cyl(0.042, 0.042, 0.02, '#3b2a20', -0.98, CT + 0.115, -0.36);

  // phone (screen faces local +z)
  box(0.074, 0.154, 0.009, C.phone, 0, 0, 0, phone);
  const sp = add(new THREE.Mesh(new THREE.PlaneGeometry(0.067, 0.146), noOutline(new THREE.MeshBasicMaterial({ map: phoneTex }))), phone);
  sp.position.z = 0.0047;
}
// rag
const rag = new THREE.Group(); scene.add(rag);
function buildRag() {
  const r = M(C.rag);
  for (const [x, z, s, h] of [[0, 0, 1, 1], [0.045, 0.02, 0.7, 0.8], [-0.04, 0.03, 0.75, 0.7], [0.01, -0.045, 0.65, 0.75], [-0.03, -0.03, 0.55, 0.6]]) {
    const m = add(new THREE.Mesh(new THREE.SphereGeometry(0.06 * s, 20, 12), r), rag); m.position.set(x, 0.006, z); m.scale.set(1, 0.22 * h, 1);
  }
}

// ---------------------------------------------------------------------------
// POV arms (navy polo, short sleeves) and hands
// ---------------------------------------------------------------------------
function makeHand(fist) {
  const g = new THREE.Group(); scene.add(g);
  const palm = sph(0.044, C.skin, 0, 0, 0, g); palm.scale.set(1.05, 0.62, 1.2);
  const fingers = [];
  for (let i = 0; i < 4; i++) {
    const f = capsule(0.0125, 0.045, C.skin, g); f.rotation.x = Math.PI / 2;
    f.position.set(-0.03 + i * 0.02, -0.004, -0.07); fingers.push(f);
  }
  const th = capsule(0.013, 0.04, C.skin, g); th.rotation.set(Math.PI / 2, 0, 0.9); th.position.set(-0.05, -0.002, -0.03);
  return { g, fingers, th };
}
const armMat = M(C.skin), poloMat = M(C.polo);
function makeArm() {
  const fore = add(new THREE.Mesh(new THREE.CylinderGeometry(0.036, 0.045, 1, 20), armMat));
  const elbow = sph(0.046, C.skin, 0, 0, 0);
  const upper = add(new THREE.Mesh(new THREE.CylinderGeometry(0.05, 0.05, 1, 20), armMat));
  const sleeve = add(new THREE.Mesh(new THREE.CylinderGeometry(0.068, 0.062, 1, 22), poloMat));
  return { fore, elbow, upper, sleeve };
}
const rightHand = makeHand(), rightArm = makeArm(), leftArm = makeArm();
// phone-holding hands (children of the phone so they move with it)
const holdR = new THREE.Group(); phone.add(holdR);
const holdL = new THREE.Group(); phone.add(holdL);
let thumbL;
function buildHoldHands() {
  const p = sph(0.046, C.skin, 0.03, -0.045, -0.032, holdR); p.scale.set(1.1, 1.3, 0.62);
  for (let i = 0; i < 4; i++) {           // fingers curling over the right edge
    const f = capsule(0.0105, 0.012, C.skin, holdR); f.rotation.z = Math.PI / 2;
    f.position.set(0.046, 0.03 - i * 0.024, 0.004);
  }
  
  const lp = sph(0.038, C.skin, -0.058, -0.088, -0.024, holdL); lp.scale.set(1, 1.15, 0.6);
  thumbL = capsule(0.012, 0.042, C.skin, holdL); thumbL.position.set(-0.02, -0.052, 0.012); thumbL.rotation.z = -0.75;
}

// ---------------------------------------------------------------------------
// phone screen UI (canvas) — off / lock screen notification / chat + typing
// ---------------------------------------------------------------------------
const MSG = 'Quiet night? Don’t forget to lock the side door at 2:30.';
const REPLY = 'Dead quiet. Just me and the crickets.';
function wrap(g, text, maxW) { const words = text.split(' '), lines = []; let l = ''; for (const w of words) { const t = l ? l + ' ' + w : w; if (g.measureText(t).width > maxW && l) { lines.push(l); l = w; } else l = t; } if (l) lines.push(l); return lines; }
let lastPhoneKey = '';
function drawPhone(state, typed, glowK) {
  const key = state + '|' + typed.length + '|' + Math.round(glowK * 20);
  if (key === lastPhoneKey) return; lastPhoneKey = key;
  const g = phoneTex.userData.canvas.getContext('2d'), w = 400, h = 844;
  g.save(); rr(g, 0, 0, w, h, 46); g.clip();
  if (state === 'off') {
    const bg = g.createLinearGradient(0, 0, w, h); bg.addColorStop(0, '#16181e'); bg.addColorStop(0.5, '#0d0e12'); bg.addColorStop(1, '#14161b');
    g.fillStyle = bg; g.fillRect(0, 0, w, h);
    g.fillStyle = 'rgba(255,255,255,0.06)'; g.beginPath(); g.moveTo(0, 0); g.lineTo(w * 0.6, 0); g.lineTo(0, h * 0.5); g.fill();
  } else if (state === 'lock') {
    const bg = g.createLinearGradient(0, 0, 0, h); bg.addColorStop(0, '#20325e'); bg.addColorStop(1, '#0d1427');
    g.fillStyle = bg; g.fillRect(0, 0, w, h);
    g.fillStyle = `rgba(255,255,255,${0.85 * glowK + 0.15})`; g.textAlign = 'center';
    g.font = F(500, 30); g.fillText('Friday', w / 2, 120);
    g.font = F(700, 120); g.fillText('2:14', w / 2, 240);
    g.globalAlpha = glowK; g.fillStyle = 'rgba(28,32,44,0.92)'; rr(g, 22, 300, w - 44, 200, 30); g.fill();
    g.textAlign = 'left'; g.fillStyle = '#f5d23a'; g.beginPath(); g.arc(66, 344, 22, 0, 7); g.fill();
    g.fillStyle = '#14161d'; g.font = F(800, 26); g.textAlign = 'center'; g.fillText('M', 66, 353);
    g.textAlign = 'left'; g.fillStyle = '#fff'; g.font = F(700, 28); g.fillText('Manager', 102, 354);
    g.fillStyle = '#9aa3b5'; g.font = F(500, 22); g.textAlign = 'right'; g.fillText('now', w - 46, 352); g.textAlign = 'left';
    g.fillStyle = '#f5d23a'; g.font = F(700, 28); wrap(g, MSG, w - 100).forEach((l, i) => g.fillText(l, 46, 404 + i * 36));
    g.globalAlpha = 1;
  } else {      // chat
    g.fillStyle = '#0f1117'; g.fillRect(0, 0, w, h);
    g.fillStyle = '#181b24'; g.fillRect(0, 0, w, 130);
    g.fillStyle = '#fff'; g.font = F(600, 22); g.fillText('2:14', 34, 44);
    g.fillStyle = '#f5d23a'; g.beginPath(); g.arc(70, 92, 24, 0, 7); g.fill();
    g.fillStyle = '#14161d'; g.font = F(800, 26); g.textAlign = 'center'; g.fillText('M', 70, 101); g.textAlign = 'left';
    g.fillStyle = '#fff'; g.font = F(700, 28); g.fillText('Manager', 108, 90); g.fillStyle = '#7fe0a0'; g.font = F(500, 18); g.fillText('Active now', 108, 114);
    g.font = F(700, 27); const ls = wrap(g, MSG, 250);
    g.fillStyle = '#262a35'; rr(g, 22, 170, 286, 36 + ls.length * 34, 22); g.fill();
    g.fillStyle = '#f5d23a'; ls.forEach((l, i) => g.fillText(l, 40, 210 + i * 34));
    g.fillStyle = '#6b7385'; g.font = F(500, 18); g.fillText('2:14 AM', 26, 236 + ls.length * 34);
    // input box with typed reply
    g.fillStyle = '#1d212b'; rr(g, 18, 470, w - 36, 64, 32); g.fill();
    g.font = F(600, 24); const tl = wrap(g, typed || ' ', w - 110);
    g.fillStyle = typed ? '#fff' : '#6b7385'; g.fillText(typed ? tl[tl.length - 1] : 'Message', 40, 510);
    if (typed && Math.floor(performance.now() / 1) >= 0) { const cw = g.measureText(tl[tl.length - 1]).width; g.fillStyle = '#4c8dff'; g.fillRect(42 + cw, 488, 3, 30); }
    g.fillStyle = '#4c8dff'; g.beginPath(); g.arc(w - 52, 502, 22, 0, 7); g.fill();
    // keyboard
    g.fillStyle = '#1a1d25'; g.fillRect(0, 560, w, h - 560);
    const rows = ['qwertyuiop', 'asdfghjkl', 'zxcvbnm'];
    g.font = F(500, 22); g.textAlign = 'center';
    rows.forEach((r, ri) => { const kw = 36, off = (w - r.length * kw) / 2; for (let i = 0; i < r.length; i++) { g.fillStyle = '#353a47'; rr(g, off + i * kw + 3, 584 + ri * 62, kw - 6, 50, 8); g.fill(); g.fillStyle = '#e6e9f0'; g.fillText(r[i], off + i * kw + kw / 2, 617 + ri * 62); } });
    g.fillStyle = '#353a47'; rr(g, 90, 772, 220, 48, 8); g.fill(); g.textAlign = 'left';
  }
  g.restore();
  phoneTex.needsUpdate = true;
}

// ---------------------------------------------------------------------------
// build
// ---------------------------------------------------------------------------
buildRoom(); buildFront(); buildCoolers(); buildStore(); buildCounter(); buildRag(); buildHoldHands();
scene.add(new THREE.AmbientLight('#f4f7ff', 2.6));
const sun = new THREE.DirectionalLight('#ffffff', 0.75); sun.position.set(-1, 6, 2); scene.add(sun);

// ---------------------------------------------------------------------------
// camera + lens
// ---------------------------------------------------------------------------
const camera = new THREE.PerspectiveCamera(SRC_FOV, W / H, 0.015, 60);
camera.rotation.order = 'YXZ';
const effect = new OutlineEffect(renderer, { defaultThickness: OUT, defaultColor: [0.08, 0.08, 0.09] });
const rt = new THREE.WebGLRenderTarget(SRC_W, SRC_H, { samples: 4, type: THREE.HalfFloatType });
const lens = new THREE.ShaderMaterial({
  uniforms: { tSrc: { value: rt.texture }, focal: { value: FOCAL }, res: { value: new THREE.Vector2(W, H) }, tanXY: { value: new THREE.Vector2(TAN_X, TAN_Y) } },
  vertexShader: `varying vec2 vUv; void main(){ vUv = uv; gl_Position = vec4(position.xy, 0., 1.); }`,
  fragmentShader: `
    uniform sampler2D tSrc; uniform float focal; uniform vec2 res; uniform vec2 tanXY; varying vec2 vUv;
    vec3 toSRGB(vec3 c){ return mix(c*12.92, 1.055*pow(c, vec3(1./2.4)) - 0.055, step(0.0031308, c)); }
    void main(){
      vec2 p = (vUv - 0.5) * res; float r = length(p);
      float th = 2.0 * atan(r / (2.0 * focal));
      vec2 dir = r > 0.0 ? p / r : vec2(0.0);
      gl_FragColor = vec4(toSRGB(texture2D(tSrc, dir * tan(th) / tanXY * 0.5 + 0.5).rgb), 1.0);
    }`,
  depthTest: false, depthWrite: false,
});
const quadScene = new THREE.Scene(), quadCam = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);
quadScene.add(new THREE.Mesh(new THREE.PlaneGeometry(2, 2), lens));

// ---------------------------------------------------------------------------
// timeline
// ---------------------------------------------------------------------------
const D2R = Math.PI / 180;
const sineIO = t => 0.5 - 0.5 * Math.cos(Math.PI * t);
const sineIn = t => 1 - Math.cos(Math.PI * t / 2);
const easeOut = t => 1 - Math.pow(1 - t, 3);
const seg = (t, a, b) => Math.min(1, Math.max(0, (t - a) / (b - a)));
const T = {
  panL: [0.3, 1.1], panR: [2.5, 3.45], tilt: [5.85, 6.38], buzz1: [6.62, 6.92], buzz2: [7.06, 7.36],
  grab: [7.62, 7.98], lift: [7.98, 8.6], type0: 8.75, typeRate: 15,
};
window.TIMELINE = T;
const PHONE_COUNTER = { pos: new THREE.Vector3(0.06, CT + 0.0045, -0.33), rot: new THREE.Euler(-Math.PI / 2, 0, 0.12) };
const PHONE_HELD = { pos: new THREE.Vector3(0.008, -0.012, -0.135), rot: new THREE.Euler(-0.05, 0.0, -0.04) };   // camera-local
function camAt(t) {
  let yaw = 6 * sineIO(seg(t, ...T.panL)) - 16.5 * sineIO(seg(t, ...T.panR)) - 1.4 * sineIn(seg(t, 3.5, 5.85));
  let pitch = -3 + 1.0 * sineIO(seg(t, ...T.panL));
  const k = sineIO(seg(t, ...T.tilt));
  yaw += (-9 - yaw) * k; pitch += (-60 - pitch) * k;
  const u = sineIO(seg(t, T.lift[0] - 0.05, T.lift[1] + 0.05));
  yaw += (-3 - yaw) * u; pitch += (-21 - pitch) * u;
  yaw += 1.2 * sineIn(seg(t, 8.7, 10.5)); pitch += 0.6 * sineIn(seg(t, 8.7, 10.5));
  const lean = k * (1 - u);
  return { yaw: yaw * D2R, pitch: pitch * D2R, pos: new THREE.Vector3(0.0, EYE - 0.15 * lean - 0.04 * u, -0.12 * lean - 0.02 * u) };
}
// wiping motion (circles), fades out before the tilt
const WIPE_C = new THREE.Vector3(-0.2, CT + 0.003, -0.42);
function wipeAt(t) {
  const amp = 1 - sineIO(seg(t, 5.2, 5.75));
  const ph = t * 2 * Math.PI / 1.55 + 0.4 * Math.sin(t * 1.3);
  return new THREE.Vector3(WIPE_C.x + amp * 0.085 * Math.cos(ph), WIPE_C.y, WIPE_C.z + amp * 0.055 * Math.sin(ph));
}
const tmpM = new THREE.Matrix4(), tmpQ = new THREE.Quaternion(), qCounter = new THREE.Quaternion().setFromEuler(PHONE_COUNTER.rot);
function bodyFrame(c) { // yaw-only frame at the torso
  const m = new THREE.Matrix4().makeRotationY(c.yaw); m.setPosition(c.pos.x, c.pos.y, c.pos.z); return m;
}
// two-bone IK: shoulder (torso frame) -> elbow -> wrist, fixed bone lengths, elbow pointing down/out
const UPPER = 0.31, FORE = 0.29;
function placeArm(arm, wrist, side, bf, visible) {
  for (const k of ['fore', 'elbow', 'upper', 'sleeve']) arm[k].visible = visible;
  if (!visible) return;
  const S = new THREE.Vector3(0.19 * side, -0.27, 0.03).applyMatrix4(bf);
  const pole = new THREE.Vector3(0.7 * side, -1, 0.35).transformDirection(bf);
  const v = wrist.clone().sub(S); const d = Math.min(v.length(), (UPPER + FORE) * 0.995); const u = v.normalize();
  const ca = (UPPER * UPPER + d * d - FORE * FORE) / (2 * UPPER * d), sa = Math.sqrt(Math.max(0, 1 - ca * ca));
  const p = pole.sub(u.clone().multiplyScalar(pole.dot(u))).normalize();
  const E = S.clone().add(u.clone().multiplyScalar(UPPER * ca)).add(p.multiplyScalar(UPPER * sa));
  const Wr = S.clone().add(E.clone().sub(S)).add(wrist.clone().sub(E).normalize().multiplyScalar(FORE));
  orient(arm.fore, Wr, E); arm.elbow.position.copy(E);
  const sl = S.clone().lerp(E, 0.7);
  orient(arm.sleeve, S, sl); orient(arm.upper, sl, E);
}
function hudAt(t) {
  const title = document.getElementById('title');
  const a = easeOut(seg(t, -0.05, 0.4)), out = seg(t, 5.85, 6.2);
  title.style.opacity = (0.25 + 0.75 * a) * (1 - out);
  title.style.transform = `translateX(${-12 * (1 - a)}px)`;
  const card = document.getElementById('card'), msg = document.getElementById('cardMsg');
  const ci = easeOut(seg(t, 6.64, 6.86));
  card.style.opacity = ci; card.style.transform = `translateY(${-24 * (1 - ci)}px) scale(${0.96 + 0.04 * ci})`;
  const typed = REPLY.slice(0, Math.max(0, Math.floor((t - T.type0) * T.typeRate)));
  if (t < 8.62) {
    document.getElementById('cardAv').textContent = 'M'; document.getElementById('cardName').textContent = 'Manager';
    document.getElementById('cardTime').textContent = '2:14'; msg.textContent = MSG; msg.style.color = '#f5d23a';
  } else {
    document.getElementById('cardAv').textContent = 'Y'; document.getElementById('cardName').textContent = 'You';
    document.getElementById('cardTime').innerHTML = '<span class="typing">typing…</span>';
    msg.textContent = typed || ' '; msg.style.color = '#ffffff';
  }
  document.getElementById('subtxt').textContent = '';
  return typed;
}
window.setHud = on => { document.getElementById('hud').style.display = on ? 'block' : 'none'; };
window.renderAt = (t) => {
  drawRain(t);
  const c = camAt(t);
  camera.position.copy(c.pos); camera.rotation.set(c.pitch, c.yaw, 0); camera.updateMatrixWorld();
  const bf = bodyFrame(c);
  // ---- phone pose: on counter (with vibration) → lifted into the camera-local held pose
  const buzz = (seg(t, ...T.buzz1) > 0 && seg(t, ...T.buzz1) < 1) || (seg(t, ...T.buzz2) > 0 && seg(t, ...T.buzz2) < 1);
  const pc = PHONE_COUNTER.pos.clone(); let qc = qCounter.clone();
  if (buzz) { pc.x += 0.0016 * Math.sin(t * 2 * Math.PI * 47); pc.z += 0.0012 * Math.cos(t * 2 * Math.PI * 53); qc.multiply(new THREE.Quaternion().setFromEuler(new THREE.Euler(0, 0, 0.012 * Math.sin(t * 300)))); }
  const L = sineIO(seg(t, ...T.lift));
  const ph = PHONE_HELD.pos.clone().applyMatrix4(camera.matrixWorld);
  const qh = camera.quaternion.clone().multiply(new THREE.Quaternion().setFromEuler(PHONE_HELD.rot));
  phone.position.copy(pc).lerp(ph, L); phone.position.y += 0.06 * Math.sin(Math.PI * L);
  phone.quaternion.copy(qc).slerp(qh, L);
  phone.updateMatrixWorld();
  // ---- right hand: wiping → reaching for phone → holding it
  const holding = t >= T.grab[1];
  holdR.visible = holding; holdL.visible = t >= T.lift[0] + 0.25;
  rightHand.g.visible = !holding;
  let handPos;
  if (!holding) {
    const wp = wipeAt(Math.min(t, 5.8));
    const target = new THREE.Vector3(0.06, -0.045, -0.02).applyMatrix4(phone.matrixWorld); target.y = Math.max(target.y, CT + 0.03);
    const gk = sineIO(seg(t, ...T.grab));
    handPos = wp.clone().add(new THREE.Vector3(0, 0.03, 0)).lerp(target, gk);
    rightHand.g.position.copy(handPos); rightHand.g.rotation.set(0, 0.55 - 0.6 * gk, 0); rightHand.g.updateMatrixWorld();
    rag.position.copy(wipeAt(Math.min(t, 5.8)));
    rag.rotation.y = 0.2 * Math.sin(t * 2);
  } else {
    handPos = new THREE.Vector3(0.03, -0.05, -0.04).applyMatrix4(phone.matrixWorld);
  }
  const wristR = holding ? new THREE.Vector3(0.045, -0.085, -0.03).applyMatrix4(phone.matrixWorld)
                         : rightHand.g.localToWorld(new THREE.Vector3(0, 0.004, 0.045));
  placeArm(rightArm, wristR, 1, bf, true);
  // left arm only while holding the phone
  const lp = new THREE.Vector3(-0.055, -0.11, -0.03).applyMatrix4(phone.matrixWorld);
  placeArm(leftArm, lp, -1, bf, holdL.visible);
  // typing thumb
  const typedNow = Math.floor((t - T.type0) * T.typeRate);
  const tap = t > T.type0 && t < T.type0 + REPLY.length / T.typeRate ? Math.abs(Math.sin((t - T.type0) * T.typeRate * Math.PI)) : 0;
  const kx = ((typedNow * 7) % 9) / 9;
  thumbL.position.set(-0.026 + 0.03 * kx, -0.05 + 0.006 * ((typedNow * 3) % 3), 0.012 + 0.006 * tap);
  // ---- phone screen
  const state = t < T.buzz1[0] ? 'off' : t < T.lift[0] + 0.3 ? 'lock' : 'chat';
  const typed = hudAt(t);
  drawPhone(state, typed, easeOut(seg(t, T.buzz1[0], T.buzz1[0] + 0.25)));
  // ---- render
  renderer.setRenderTarget(rt); effect.render(scene, camera);
  renderer.setRenderTarget(null); renderer.render(quadScene, quadCam);
};
window.sceneReady = Promise.resolve(true);
