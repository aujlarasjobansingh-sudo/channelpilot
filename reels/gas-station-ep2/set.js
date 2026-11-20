// Set: store interior, glass front + doors, coolers, aisles, counter (lock button, landline, phone),
// exterior lot + police cruiser, cashier's own torso/legs.
import { THREE, scene, M, noOutline, INK, add, box, cyl, sph, capsule, inkLine, canvasTex, texPlane, glowMat, glowSprite, rr, F, rnd } from './core.js';

export const C = {
  ceiling: '#cfccc4', wall: '#ebe6d8', stripe: '#d2483c', stripe2: '#f2b632', floor: '#d5d7d0', floorLine: '#bcc0b8',
  counterTop: '#7d828c', counterFront: '#2e3b55', counterInner: '#26304a', counterTrim: '#c9ccd2', metal: '#a3a9b2', darkMetal: '#3a3e47',
  frame: '#b9bec7', kick: '#5b606b', light: '#fbfaf0', skin: '#d9a079', polo: '#1f3460', pants: '#2e333d', rag: '#c9d3dc',
  phone: '#1b1d23', cooler: '#30343c', shelf: '#9aa1ab', shelfDark: '#6f7680',
};
export const EYE = 1.62, CT = 0.98;
export const XL = -4.6, XR = 3.6, ZF = -7.0, ZB = 1.3, RH = 3.0;
const GLASS_Y0 = 0.35, GLASS_Y1 = 2.6;

// ---------------------------------------------------------------- room
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
    g.fillStyle = 'rgba(120,110,90,0.06)'; for (let i = 0; i < 40; i++) { g.beginPath(); g.arc(rnd() * w, rnd() * h, 10 + rnd() * 40, 0, 7); g.fill(); }   // scuffs
  });
  floorTex.wrapS = floorTex.wrapT = THREE.RepeatWrapping; floorTex.repeat.set((XR - XL) / 4.8, (ZB - ZF) / 4.8);
  const floor = add(new THREE.Mesh(new THREE.PlaneGeometry(XR - XL, ZB - ZF), noOutline(new THREE.MeshBasicMaterial({ map: floorTex }))));
  floor.rotation.x = -Math.PI / 2; floor.position.set((XL + XR) / 2, 0, (ZB + ZF) / 2);
  const ceil = add(new THREE.Mesh(new THREE.PlaneGeometry(XR - XL, ZB - ZF), noOutline(new THREE.MeshBasicMaterial({ color: C.ceiling }))));
  ceil.rotation.x = Math.PI / 2; ceil.position.set((XL + XR) / 2, RH, (ZB + ZF) / 2);
  const wallTex = canvasTex(64, 600, (g, w, h) => {
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
  for (const z of [-1.7, -3.9, -6.1]) for (const x of [-2.7, -0.4, 1.9]) {
    box(1.22, 0.03, 0.62, C.light, x, RH - 0.016, z, null, { flat: true });
    const p = texPlane(1.2, 0.6, lightTex, x, RH - 0.033, z); p.rotation.x = Math.PI / 2;
  }
  // back wall behind the cashier: cigarette/lottery cabinet
  box(2.6, 1.2, 0.3, '#3a3f4a', -0.3, 1.75, ZB - 0.15);
  const cig = canvasTex(520, 240, (g, w, h) => { g.fillStyle = '#2c313b'; g.fillRect(0, 0, w, h); const cs = ['#e33b2f', '#f2f2f2', '#2f73d8', '#f2b51e', '#2fa64d']; for (let r = 0; r < 4; r++) for (let i = 0; i < 13; i++) { g.fillStyle = cs[(i + r * 2) % 5]; g.fillRect(8 + i * 39, 10 + r * 57, 32, 44); } });
  const cp = texPlane(2.5, 1.1, cig, -0.3, 1.75, ZB - 0.31); cp.rotation.y = Math.PI;
}

// ---------------------------------------------------------------- rain on the glass (transparent overlay)
export const rainTex = canvasTex(1400, 360, () => {});
const drops = [], streaks = [];
for (let i = 0; i < 300; i++) streaks.push({ x: rnd() * 1400, y: rnd() * 360, len: 18 + rnd() * 40, sp: 900 + rnd() * 700, a: 0.16 + rnd() * 0.3 });
for (let i = 0; i < 120; i++) drops.push({ x: rnd() * 1400, y0: rnd() * 360, sp: 6 + rnd() * 30, r: 2 + rnd() * 3, ph: rnd() * 10 });
export function drawRain(t) {
  const g = rainTex.userData.canvas.getContext('2d'), w = 1400, h = 360;
  g.clearRect(0, 0, w, h);
  g.fillStyle = 'rgba(10,15,24,0.16)'; g.fillRect(0, 0, w, h);
  const sh = g.createLinearGradient(0, 0, w, h); sh.addColorStop(0.2, 'rgba(200,215,235,0)'); sh.addColorStop(0.45, 'rgba(200,215,235,0.05)'); sh.addColorStop(0.55, 'rgba(200,215,235,0)');
  g.fillStyle = sh; g.fillRect(0, 0, w, h);
  g.lineCap = 'round';
  for (const s of streaks) {
    const y = ((s.y + t * s.sp) % (h + 80)) - 40, x = s.x + y * 0.12;
    g.strokeStyle = `rgba(190,205,225,${s.a})`; g.lineWidth = 2.4; g.beginPath(); g.moveTo(x, y); g.lineTo(x + s.len * 0.12, y + s.len); g.stroke();
  }
  for (const d of drops) {
    const y = (d.y0 + t * d.sp + 4 * Math.sin(t * 2 + d.ph)) % (h + 20);
    g.strokeStyle = 'rgba(170,190,215,0.18)'; g.lineWidth = d.r * 0.9;
    g.beginPath(); g.moveTo(d.x, Math.max(0, y - 30 - d.sp)); g.lineTo(d.x + 1, y); g.stroke();
    g.fillStyle = 'rgba(205,220,240,0.45)'; g.beginPath(); g.arc(d.x + 1, y, d.r, 0, 7); g.fill();
    g.fillStyle = 'rgba(255,255,255,0.6)'; g.beginPath(); g.arc(d.x, y - d.r * 0.35, d.r * 0.35, 0, 7); g.fill();
  }
  rainTex.needsUpdate = true;
}
const glassMat = () => noOutline(new THREE.MeshBasicMaterial({ map: rainTex, transparent: true, depthWrite: false }));

// ---------------------------------------------------------------- front wall + doors (pivoting leaves) + maglock
export const doors = {};
function buildFront() {
  const z = ZF;
  const glass = add(new THREE.Mesh(new THREE.PlaneGeometry(XR - XL, GLASS_Y1 - GLASS_Y0), glassMat()));
  glass.position.set((XL + XR) / 2, (GLASS_Y0 + GLASS_Y1) / 2, z); glass.renderOrder = 2;
  // cut the door opening out of the big pane: left / right panes only
  glass.geometry = new THREE.PlaneGeometry(XR - XL, GLASS_Y1 - GLASS_Y0);
  const uvFix = (mesh, x0, x1, y0, y1) => {
    const uv = mesh.geometry.attributes.uv;
    for (let i = 0; i < uv.count; i++) { const u = uv.getX(i), v = uv.getY(i); uv.setXY(i, ((x0 + u * (x1 - x0)) - XL) / (XR - XL), ((y0 + v * (y1 - y0)) - GLASS_Y0) / (GLASS_Y1 - GLASS_Y0)); }
    uv.needsUpdate = true;
  };
  scene.remove(glass);
  for (const [x0, x1] of [[XL, 0.15], [2.85, XR]]) {
    const p = add(new THREE.Mesh(new THREE.PlaneGeometry(x1 - x0, GLASS_Y1 - GLASS_Y0), glassMat())); p.renderOrder = 2;
    p.position.set((x0 + x1) / 2, (GLASS_Y0 + GLASS_Y1) / 2, z); uvFix(p, x0, x1, GLASS_Y0, GLASS_Y1);
  }
  const tr = add(new THREE.Mesh(new THREE.PlaneGeometry(2.7, GLASS_Y1 - 2.45), glassMat())); tr.renderOrder = 2;   // transom over doors
  tr.position.set(1.5, (2.45 + GLASS_Y1) / 2, z); uvFix(tr, 0.15, 2.85, 2.45, GLASS_Y1);
  // kick wall left/right of the doors
  box(0.15 - XL, GLASS_Y0, 0.12, C.kick, (XL + 0.15) / 2, GLASS_Y0 / 2, z);
  box(XR - 2.85, GLASS_Y0, 0.12, C.kick, (2.85 + XR) / 2, GLASS_Y0 / 2, z);
  const hdr = add(new THREE.Mesh(new THREE.PlaneGeometry(XR - XL, RH - GLASS_Y1), noOutline(new THREE.MeshBasicMaterial({ color: C.wall }))));
  hdr.position.set((XL + XR) / 2, (GLASS_Y1 + RH) / 2, z + 0.001);
  box(XR - XL, 0.2, 0.02, C.stripe, (XL + XR) / 2, 2.72, z + 0.01, null, { thin: true });
  box(XR - XL, 0.08, 0.1, C.frame, (XL + XR) / 2, GLASS_Y1, z + 0.02);
  box(0.15 - XL, 0.06, 0.1, C.frame, (XL + 0.15) / 2, GLASS_Y0 + 0.02, z + 0.02);
  box(XR - 2.85, 0.06, 0.1, C.frame, (2.85 + XR) / 2, GLASS_Y0 + 0.02, z + 0.02);
  box(2.7, 0.07, 0.1, C.frame, 1.5, 2.45, z + 0.02);   // door head
  for (const x of [-4.5, -2.9, -1.3, 0.15, 2.85, 3.5]) box(0.08, GLASS_Y1 - (x === 0.15 || x === 2.85 ? 0 : GLASS_Y0), 0.1, C.frame, x, x === 0.15 || x === 2.85 ? GLASS_Y1 / 2 : (GLASS_Y0 + GLASS_Y1) / 2, z + 0.02);
  // leaves: hinge on the outer jambs, swing inward (+z)
  const dz = z + 0.06;
  box(2.7, 0.06, 0.12, C.frame, 1.5, 0.03, dz);
  for (const side of ['L', 'R']) {
    const hingeX = side === 'L' ? 0.19 : 2.81, s = side === 'L' ? 1 : -1;
    const pivot = new THREE.Group(); pivot.position.set(hingeX, 0, dz); scene.add(pivot);
    const leaf = new THREE.Group(); leaf.position.set(s * 0.655, 0, 0); pivot.add(leaf);
    box(1.31, 0.1, 0.06, C.frame, 0, 2.37, 0, leaf); box(1.31, 0.18, 0.06, C.frame, 0, 0.09, 0, leaf);
    box(0.08, 2.42, 0.06, C.frame, -0.62, 1.21, 0, leaf); box(0.08, 2.42, 0.06, C.frame, 0.62, 1.21, 0, leaf);
    const dg = add(new THREE.Mesh(new THREE.PlaneGeometry(1.16, 2.14), glassMat()), leaf); dg.renderOrder = 2;
    dg.position.set(0, 1.25, 0); uvFix(dg, hingeX + s * 0.655 - 0.58, hingeX + s * 0.655 + 0.58, 0.18, 2.32);
    const hx = s * 0.52;
    cyl(0.018, 0.018, 0.6, C.metal, hx, 1.1, 0.06, leaf, 12); cyl(0.018, 0.018, 0.6, C.metal, hx, 1.1, -0.06, leaf, 12);
    for (const yy of [1.38, 0.82]) { box(0.02, 0.02, 0.14, C.metal, hx, yy, 0, leaf); }
    const push = canvasTex(160, 60, (g, w) => { g.fillStyle = 'rgba(255,255,255,0.85)'; g.font = F(800, 40); g.textAlign = 'center'; g.fillText(side === 'L' ? 'PUSH' : 'PUSH', w / 2, 44); });
    texPlane(0.2, 0.075, push, -s * 0.25, 1.3, 0.035, leaf);
    doors[side] = { pivot, leaf, s };
  }
  const hours = canvasTex(256, 140, (g, w) => { g.fillStyle = 'rgba(255,255,255,0.85)'; g.font = F(800, 46); g.textAlign = 'center'; g.fillText('OPEN 24/7', w / 2, 60); g.font = F(600, 28); g.fillText('ROUTE 9 FUEL', w / 2, 108); });
  texPlane(0.42, 0.23, hours, 0.1, 1.6, 0.035, doors.R.leaf);
  box(2.0, 0.012, 1.0, '#3d424b', 1.5, 0.006, z + 0.65, null, { thin: true });
  // door chime + magnetic lock bar with status LED
  box(0.16, 0.08, 0.06, '#e9e9e4', 2.3, 2.6, z + 0.08);
  box(0.62, 0.06, 0.07, '#8d939c', 1.5, 2.37, z + 0.12);
  doors.led = add(new THREE.Mesh(new THREE.SphereGeometry(0.014, 12, 8), noOutline(new THREE.MeshBasicMaterial({ color: '#39d36b' }))));
  doors.led.position.set(1.78, 2.37, z + 0.16);
  doors.ledGlow = glowSprite('#39d36b', 0.09); doors.ledGlow.position.copy(doors.led.position);
  const neon = canvasTex(420, 150, (g, w, h) => {
    g.clearRect(0, 0, w, h); g.shadowColor = 'rgba(255,60,60,0.9)'; g.shadowBlur = 22;
    g.strokeStyle = '#ff5b5b'; g.lineWidth = 8; rr(g, 12, 12, w - 24, h - 24, 26); g.stroke();
    g.fillStyle = '#ff6a6a'; g.font = F(800, 82); g.textAlign = 'center'; g.fillText('OPEN', w / 2, 106);
  });
  texPlane(0.84, 0.3, neon, -2.1, 1.95, z + 0.03);
}
export function setDoor(side, ang) { doors[side].pivot.rotation.y = -doors[side].s * ang; }
export function setLocked(on) {
  const c = on ? '#ff3b3b' : '#39d36b'; doors.led.material.color.set(c); doors.ledGlow.material.color.set(c);
}

// ---------------------------------------------------------------- exterior: wet lot, curb, cruiser
export const car = {};
function buildExterior() {
  const lot = canvasTex(1024, 1024, (g, w, h) => {
    g.fillStyle = '#0b0e14'; g.fillRect(0, 0, w, h);
    for (let i = 0; i < 70; i++) { g.fillStyle = `rgba(80,100,130,${0.04 + rnd() * 0.06})`; g.beginPath(); g.ellipse(rnd() * w, rnd() * h, 20 + rnd() * 70, 8 + rnd() * 20, 0, 0, 7); g.fill(); }
    g.strokeStyle = 'rgba(210,210,190,0.18)'; g.lineWidth = 10; for (let i = 0; i < 6; i++) { g.beginPath(); g.moveTo(80 + i * 170, 420); g.lineTo(80 + i * 170, 760); g.stroke(); }
  });
  const ground = add(new THREE.Mesh(new THREE.PlaneGeometry(60, 30), noOutline(new THREE.MeshBasicMaterial({ map: lot }))));
  ground.rotation.x = -Math.PI / 2; ground.position.set(0, 0, ZF - 15.1);
  const curb = add(new THREE.Mesh(new THREE.BoxGeometry(60, 0.12, 1.6), noOutline(new THREE.MeshBasicMaterial({ color: '#171b23' }))));
  curb.position.set(0, 0.06, ZF - 0.86);
  const curbEdge = add(new THREE.Mesh(new THREE.BoxGeometry(60, 0.13, 0.08), noOutline(new THREE.MeshBasicMaterial({ color: '#232832' }))));
  curbEdge.position.set(0, 0.065, ZF - 1.66);
  const sky = add(new THREE.Mesh(new THREE.PlaneGeometry(200, 80), noOutline(new THREE.MeshBasicMaterial({ color: '#04060a' }))));
  sky.position.set(0, 10, ZF - 29);
  // distant sodium light pole
  cyl(0.06, 0.08, 6, '#15181f', 7.5, 3, -24); const lp = glowSprite('#ffb066', 1.6); lp.position.set(7.2, 6.0, -24);
  const pool = add(new THREE.Mesh(new THREE.CircleGeometry(3.2, 32), glowMat('#ff9a4a', 0.10))); pool.rotation.x = -Math.PI / 2; pool.position.set(7.2, 0.01, -24);

  // ---- store exterior shell (so it reads as a building from the lot)
  const shell = noOutline(new THREE.MeshBasicMaterial({ color: '#2a2e38' }));
  for (const x of [XL - 0.12, XR + 0.12]) { const w = add(new THREE.Mesh(new THREE.BoxGeometry(0.2, RH + 0.5, ZB - ZF + 0.3), shell)); w.position.set(x, (RH + 0.5) / 2, (ZB + ZF) / 2); }
  const roof = add(new THREE.Mesh(new THREE.BoxGeometry(XR - XL + 0.5, 0.25, ZB - ZF + 0.3), shell)); roof.position.set((XL + XR) / 2, RH + 0.13, (ZB + ZF) / 2);
  const fascia = add(new THREE.Mesh(new THREE.BoxGeometry(XR - XL + 0.5, 0.75, 0.12), noOutline(new THREE.MeshBasicMaterial({ color: '#d8d2c2' })))); fascia.position.set((XL + XR) / 2, RH + 0.12, ZF - 0.12);
  const band = add(new THREE.Mesh(new THREE.BoxGeometry(XR - XL + 0.5, 0.16, 0.13), noOutline(new THREE.MeshBasicMaterial({ color: '#d2483c' })))); band.position.set((XL + XR) / 2, RH - 0.1, ZF - 0.12);
  const signT = canvasTex(1024, 160, (c, w, h) => { c.fillStyle = '#d8d2c2'; c.fillRect(0, 0, w, h); c.fillStyle = '#1f3460'; c.font = F(900, 110); c.textAlign = 'center'; c.fillText('ROUTE 9 FUEL', w / 2, 120); });
  texPlane(4.2, 0.6, signT, (XL + XR) / 2, RH + 0.17, ZF - 0.19).rotation.y = Math.PI;
  const header = add(new THREE.Mesh(new THREE.BoxGeometry(XR - XL, RH - GLASS_Y1, 0.05), shell)); header.position.set((XL + XR) / 2, (GLASS_Y1 + RH) / 2, ZF - 0.03);

  // ---- dark highway beyond the lot
  const road = add(new THREE.Mesh(new THREE.PlaneGeometry(80, 5), noOutline(new THREE.MeshBasicMaterial({ color: '#141821' })))); road.rotation.x = -Math.PI / 2; road.position.set(0, 0.012, -26);
  for (let x = -40; x < 40; x += 4) { const d = add(new THREE.Mesh(new THREE.PlaneGeometry(2, 0.12), noOutline(new THREE.MeshBasicMaterial({ color: '#8f8a6a' })))); d.rotation.x = -Math.PI / 2; d.position.set(x, 0.014, -26); }
  for (let x = -40; x < 40; x += 3) { cyl(0.04, 0.04, 0.6, '#3a3f49', x, 0.3, -23.3, null, 6); const r = glowSprite(x % 6 === 0 ? '#ff5a4a' : '#ffffff', 0.18); r.position.set(x, 0.58, -23.25); }
  box(80, 0.12, 0.05, '#4a505c', 0, 0.5, -23.3, null, { thin: true });
  car.truck = new THREE.Group(); scene.add(car.truck);
  for (const dz of [-0.6, 0.6]) { const hl = glowSprite('#fff4d6', 1.8, car.truck); hl.position.set(0, 1.1, dz); }
  const tb = box(2.5, 3.2, 2.4, '#1a1d24', 4, 1.9, 0, car.truck); tb.material = noOutline(new THREE.MeshBasicMaterial({ color: '#12151b' }));
  for (const dx of [-3, 0, 3, 6]) { const ml = glowSprite('#ffae42', 0.35, car.truck); ml.position.set(dx, 3.4, 1.2); }
  car.truck.position.set(-60, 0, -27);

  // ---- police cruiser (heading -x, driver side faces the store)
  const g = new THREE.Group(); scene.add(g); car.g = g;
  const body = '#15181f', white = '#eceef1';
  box(4.9, 0.62, 1.86, body, 0, 0.62, 0, g);
  box(1.2, 0.18, 1.8, body, -1.85, 0.98, 0, g).rotation.z = 0.06;
  box(1.0, 0.16, 1.8, body, 1.95, 0.98, 0, g).rotation.z = -0.05;
  const cab = new THREE.Group(); cab.position.set(0.15, 1.2, 0); g.add(cab);
  box(2.5, 0.5, 1.62, body, 0, 0, 0, cab);
  const winMat = noOutline(new THREE.MeshBasicMaterial({ color: '#1d2636' }));
  { const w1 = add(new THREE.Mesh(new THREE.PlaneGeometry(2.25, 0.36), winMat), cab); w1.position.set(0, 0.02, 0.812); }
  // store side (+z): interior visible through the open driver door (front) and the tinted rear window
  const interior = canvasTex(1024, 180, (c, w, h) => {
    c.translate(w, 0); c.scale(-1, 1);   // seen from the passenger side: mirror so the wheel sits at the front
    const bg = c.createLinearGradient(0, 0, 0, h); bg.addColorStop(0, '#20283a'); bg.addColorStop(1, '#0d111b'); c.fillStyle = bg; c.fillRect(0, 0, w, h);
    c.fillStyle = '#2b3245'; c.fillRect(300, 70, 160, 110); c.fillRect(720, 60, 260, 120);       // seats
    c.strokeStyle = '#0b0d12'; c.lineWidth = 14; c.beginPath(); c.arc(160, 95, 52, 0, 7); c.stroke();  // steering wheel
    c.fillStyle = '#0b0d12'; c.fillRect(150, 95, 20, 90);
    c.fillStyle = '#111520'; c.beginPath(); c.arc(840, 66, 34, 0, 7); c.fill(); c.fillRect(790, 92, 100, 88);   // trapped man silhouette
  });
  const inside = add(new THREE.Mesh(new THREE.PlaneGeometry(2.25, 0.4), noOutline(new THREE.MeshBasicMaterial({ map: interior }))), cab); inside.position.set(0, 0.02, -0.814); inside.rotation.y = Math.PI;
  car.tint = add(new THREE.Mesh(new THREE.PlaneGeometry(1.1, 0.38), noOutline(new THREE.MeshBasicMaterial({ color: '#16202f', transparent: true, opacity: 0.55, depthWrite: false }))), cab);
  car.tint.position.set(0.58, 0.02, -0.826); car.tint.rotation.y = Math.PI;
  // muddy palms slammed against the inside of the rear window
  car.palms = new THREE.Group(); car.palms.rotation.y = Math.PI; car.palms.position.x = 1.16; cab.add(car.palms);
  for (const px of [0.38, 0.78]) {
    const pg = new THREE.Group(); pg.position.set(px, 0.03, 0.818); car.palms.add(pg);
    const p = add(new THREE.Mesh(new THREE.CircleGeometry(0.05, 20), noOutline(new THREE.MeshBasicMaterial({ color: '#a77a58' }))), pg); p.scale.set(0.9, 1.1, 1);
    for (let i = 0; i < 4; i++) { const f = add(new THREE.Mesh(new THREE.PlaneGeometry(0.018, 0.06), noOutline(new THREE.MeshBasicMaterial({ color: '#a77a58' }))), pg); f.position.set(-0.027 + i * 0.018, 0.075, 0.0005); }
    const th = add(new THREE.Mesh(new THREE.PlaneGeometry(0.018, 0.045), noOutline(new THREE.MeshBasicMaterial({ color: '#a77a58' }))), pg); th.position.set(px < 0.5 ? 0.05 : -0.05, 0.0, 0.0005); th.rotation.z = px < 0.5 ? -0.8 : 0.8;
    const mud = add(new THREE.Mesh(new THREE.CircleGeometry(0.03, 12), noOutline(new THREE.MeshBasicMaterial({ color: '#4a3524', transparent: true, opacity: 0.7 }))), pg); mud.position.set(0.012, -0.015, 0.001);
  }
  car.palms.visible = false;
  // keys dangling in the ignition (seen through the open driver door)
  car.keys = new THREE.Group(); car.keys.position.set(-0.83, -0.02, -0.83); car.keys.rotation.y = Math.PI; car.keys.scale.setScalar(2.2); cab.add(car.keys);
  { const kg = glowSprite('#ffffff', 0.06, car.keys); kg.position.set(0.005, -0.05, 0.01); }
  { const ring = add(new THREE.Mesh(new THREE.TorusGeometry(0.014, 0.003, 6, 16), M('#c9ccd2', { thin: true })), car.keys); ring.position.y = -0.03;
    for (const [dx, rz] of [[-0.008, 0.25], [0.01, -0.3]]) { const k = box(0.008, 0.045, 0.003, '#d5d8de', dx, -0.06, 0, car.keys, { thin: true }); k.rotation.z = rz; }
    box(0.016, 0.022, 0.006, '#20232a', 0.0, -0.085, 0.002, car.keys, { thin: true }); }
  // rear door handle (store side)
  car.handle = box(0.12, 0.03, 0.035, '#1f2229', 0.95, 0.88, -0.945, g);
  box(0.08, 0.48, 1.64, body, -0.2, 0, 0, cab);           // B-pillar
  const ws = add(new THREE.Mesh(new THREE.PlaneGeometry(1.5, 0.6), winMat), cab); ws.position.set(-1.27, 0.0, 0); ws.rotation.set(0, -Math.PI / 2, 0.55);
  box(2.5, 0.03, 1.62, body, 0, 0.26, 0, cab);            // roof — completely blank (no unit number)
  // lightbar
  const lb = new THREE.Group(); lb.position.set(0.2, 1.52, 0); g.add(lb);
  box(0.3, 0.1, 1.3, '#2a2d34', 0, 0, 0, lb);
  car.red = add(new THREE.Mesh(new THREE.BoxGeometry(0.26, 0.09, 0.6), noOutline(new THREE.MeshBasicMaterial({ color: '#5a1010' }))), lb); car.red.position.z = 0.33;
  car.blue = add(new THREE.Mesh(new THREE.BoxGeometry(0.26, 0.09, 0.6), noOutline(new THREE.MeshBasicMaterial({ color: '#0e1a5a' }))), lb); car.blue.position.z = -0.33;
  car.redGlow = glowSprite('#ff2a2a', 2.2, lb); car.redGlow.position.z = 0.4;
  car.blueGlow = glowSprite('#2a5bff', 2.2, lb); car.blueGlow.position.z = -0.4;
  car.redPool = add(new THREE.Mesh(new THREE.CircleGeometry(4.5, 40), glowMat('#ff2020', 0))); car.redPool.rotation.x = -Math.PI / 2;
  car.bluePool = add(new THREE.Mesh(new THREE.CircleGeometry(4.5, 40), glowMat('#2050ff', 0))); car.bluePool.rotation.x = -Math.PI / 2;
  // door decal POLICE on store-facing side
  const dec = canvasTex(512, 96, (c, w) => { c.clearRect(0, 0, w, 96); c.fillStyle = white; c.font = F(900, 78); c.textAlign = 'center'; c.fillText('POLICE', w / 2, 78); });
  // driver door (opens on hinge at its front edge)
  car.doorPivot = new THREE.Group(); car.doorPivot.position.set(-0.75, 0, 0.94); g.add(car.doorPivot);
  const dr = new THREE.Group(); dr.position.set(0.6, 0, 0); car.doorPivot.add(dr);
  box(1.2, 0.6, 0.05, body, 0, 0.64, 0, dr);
  texPlane(1.1, 0.2, dec, 0, 0.66, 0.03, dr);
  const dwin = add(new THREE.Mesh(new THREE.PlaneGeometry(1.0, 0.34), winMat), dr); dwin.position.set(0.05, 1.22, 0.01);
  texPlane(1.6, 0.28, dec, 1.15, 0.66, 0.935, g);
  // wheels
  for (const [x, zz] of [[-1.55, 0.86], [1.55, 0.86], [-1.55, -0.86], [1.55, -0.86]]) {
    const wh = cyl(0.36, 0.36, 0.26, '#0c0d10', x, 0.36, zz, g); wh.rotation.x = Math.PI / 2;
    const rim = cyl(0.2, 0.2, 0.27, '#5d636d', x, 0.36, zz, g); rim.rotation.x = Math.PI / 2;
  }
  // lights
  box(0.06, 0.12, 0.4, '#f6f7f2', -2.46, 0.78, 0.6, g, { flat: true }); box(0.06, 0.12, 0.4, '#f6f7f2', -2.46, 0.78, -0.6, g, { flat: true });
  box(0.06, 0.12, 0.35, '#c41f1f', 2.46, 0.82, 0.62, g, { flat: true }); box(0.06, 0.12, 0.35, '#c41f1f', 2.46, 0.82, -0.62, g, { flat: true });
  box(0.18, 0.5, 1.4, '#22252c', -2.55, 0.55, 0, g);       // push bar
  car.headGlow = [glowSprite('#ffffff', 0.75, g), glowSprite('#ffffff', 0.75, g)];
  car.headGlow[0].position.set(-2.55, 0.78, 0.6); car.headGlow[1].position.set(-2.55, 0.78, -0.6);
  const beam = add(new THREE.Mesh(new THREE.ConeGeometry(2.2, 9, 32, 1, true), glowMat('#dfe8ff', 0.05)), g);
  beam.rotation.z = -Math.PI / 2; beam.position.set(-7.0, 0.7, 0); car.beam = beam;
  car.groundPool = add(new THREE.Mesh(new THREE.CircleGeometry(3, 32), glowMat('#dfe8ff', 0.08)), g); car.groundPool.rotation.x = -Math.PI / 2; car.groundPool.position.set(-6, 0.02, 0);
}

// ---------------------------------------------------------------- coolers + aisles + misc
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
  box(wd + 0.04, hgt, 0.06, C.shelf, 0, hgt / 2, len / 2 + 0.03, g);
  texPlane(wd - 0.04, hgt - 0.12, productTex(5, 4), 0, 0.08 + (hgt - 0.12) / 2 + 0.06, len / 2 + 0.065, g, false);
  const sign = canvasTex(400, 160, (c, w, h) => { c.fillStyle = '#d2483c'; rr(c, 6, 6, w - 12, h - 12, 18); c.fill(); c.strokeStyle = '#16161a'; c.lineWidth = 8; rr(c, 6, 6, w - 12, h - 12, 18); c.stroke(); c.fillStyle = '#fff'; c.font = F(900, 70); c.textAlign = 'center'; c.fillText(signText, w / 2, 106); });
  box(wd * 0.9, 0.32, 0.03, '#d2483c', 0, hgt + 0.22, len / 2 + 0.03, g);
  texPlane(wd * 0.88, 0.3, sign, 0, hgt + 0.22, len / 2 + 0.05, g);
  cyl(0.012, 0.012, 0.1, C.metal, 0, hgt + 0.03, len / 2 + 0.03, g, 8);
}
function buildStore() {
  gondola(-1.25, -3.9, 2.9, '2 FOR $5');
  gondola(-3.05, -3.9, 2.9, 'SNACKS');
  box(1.2, 0.85, 0.7, '#f3f5f7', -0.5, 0.425, -6.4);
  const ice = canvasTex(400, 200, (g, w) => { g.fillStyle = '#f3f5f7'; g.fillRect(0, 0, w, 200); g.fillStyle = '#2f73d8'; g.font = F(900, 130); g.textAlign = 'center'; g.fillText('ICE', w / 2, 150); });
  texPlane(0.9, 0.45, ice, -0.5, 0.48, -6.045);
  const wf = new THREE.Group(); wf.position.set(0.25, 0, -4.9); wf.rotation.y = 0.5; scene.add(wf);
  const wft = canvasTex(160, 300, (g, w) => { g.fillStyle = '#f5cf1f'; g.fillRect(0, 0, w, 300); g.fillStyle = '#16161a'; g.font = F(900, 40); g.textAlign = 'center'; g.fillText('WET', w / 2, 170); g.fillText('FLOOR', w / 2, 214); g.beginPath(); g.moveTo(w / 2, 40); g.lineTo(w / 2 + 40, 110); g.lineTo(w / 2 - 40, 110); g.closePath(); g.lineWidth = 7; g.stroke(); });
  for (const s of [-1, 1]) { const p = box(0.3, 0.62, 0.015, '#f5cf1f', 0, 0.31, s * 0.1, wf); p.rotation.x = s * 0.25; const tp = texPlane(0.28, 0.56, wft, 0, 0.31, s * 0.112, wf); tp.rotation.x = s * 0.25; if (s < 0) tp.rotation.y = Math.PI; }
  cyl(0.24, 0.22, 0.9, '#4a515c', -1.0, 0.45, -6.55);
  box(0.5, 1.1, 0.35, C.shelf, -2.2, 0.55, -1.3);
  texPlane(0.46, 1.0, productTex(2, 3), -2.2, 0.57, -1.12, null, false);
}

// ---------------------------------------------------------------- counter, lock button, landline, phone
export const counterZ0 = -0.12, counterZ1 = -0.8;
export const phone = new THREE.Group(); scene.add(phone);
export const phoneTex = canvasTex(400, 844, () => {});
export const lockBtn = {}; export const landline = {};
function buildCounter() {
  const cx0 = -1.6, cx1 = 0.95, w = cx1 - cx0, cxm = (cx0 + cx1) / 2;
  box(w, 0.05, counterZ0 - counterZ1, C.counterTop, cxm, CT - 0.025, (counterZ0 + counterZ1) / 2);
  box(w, CT - 0.05, 0.05, C.counterFront, cxm, (CT - 0.05) / 2, counterZ1 + 0.025);
  box(w + 0.02, 0.03, 0.06, C.counterTrim, cxm, CT - 0.065, counterZ1 + 0.02);
  box(0.05, CT - 0.05, counterZ0 - counterZ1, C.counterFront, cx1 - 0.025, (CT - 0.05) / 2, (counterZ0 + counterZ1) / 2);
  box(0.05, CT - 0.05, counterZ0 - counterZ1, C.counterFront, cx0 + 0.025, (CT - 0.05) / 2, (counterZ0 + counterZ1) / 2);
  // under-counter (cashier side): inner panel, shelf, clutter
  box(w - 0.1, CT - 0.1, 0.01, C.counterInner, cxm, (CT - 0.05) / 2, counterZ1 + 0.055, null, { thin: true });
  box(w - 0.1, 0.03, 0.5, '#4a5266', cxm, 0.32, -0.5, null, { thin: true });
  for (let i = 0; i < 5; i++) { const r = cyl(0.04, 0.04, 0.07, '#f2f2ee', -0.9 + i * 0.09, 0.37, -0.55); r.rotation.x = Math.PI / 2; }
  box(0.3, 0.12, 0.25, '#e8e2d2', 0.5, 0.4, -0.52);
  box(0.24, 0.2, 0.2, '#b9a58a', -0.3, 0.44, -0.6);
  // DOOR LOCK button: yellow housing under the lip, red mushroom button, dusty label
  const lb = new THREE.Group(); lb.position.set(0.24, CT - 0.11, counterZ0 - 0.02); scene.add(lb); lockBtn.g = lb;
  box(0.13, 0.12, 0.07, '#e8b82c', 0, 0, -0.035, lb);
  const lab = canvasTex(260, 80, (g, w, h) => { g.fillStyle = '#e8b82c'; g.fillRect(0, 0, w, h); g.fillStyle = '#16161a'; g.font = F(900, 34); g.textAlign = 'center'; g.fillText('DOOR LOCK', w / 2, 52); g.fillStyle = 'rgba(120,110,90,0.25)'; for (let i = 0; i < 160; i++) g.fillRect(rnd() * w, rnd() * h, 2, 2); });
  texPlane(0.12, 0.035, lab, 0, 0.042, 0.001, lb);
  cyl(0.036, 0.036, 0.012, '#30333a', 0, -0.012, 0.004, lb).rotation.x = Math.PI / 2;
  const cap = add(new THREE.Mesh(new THREE.SphereGeometry(0.032, 28, 14, 0, Math.PI * 2, 0, Math.PI / 2), M('#e0262b')), lb);
  cap.rotation.x = Math.PI / 2; cap.position.set(0, -0.012, 0.01); cap.scale.set(1, 0.55, 1); lockBtn.cap = cap;
  lockBtn.glow = glowSprite('#ff2a2a', 0.22, lb); lockBtn.glow.position.set(0, -0.012, 0.04);
  // register (moved left), card terminal, candy rack, coffee
  box(0.4, 0.09, 0.32, '#2d3038', -1.0, CT + 0.045, -0.5);
  box(0.36, 0.06, 0.06, '#3b3f49', -1.0, CT + 0.06, -0.68);
  cyl(0.025, 0.025, 0.16, '#2d3038', -1.0, CT + 0.17, -0.5);
  const scr = new THREE.Group(); scr.position.set(-1.0, CT + 0.28, -0.52); scr.rotation.set(-0.35, 0.35, 0); scene.add(scr);
  box(0.36, 0.25, 0.04, '#25282f', 0, 0, 0, scr);
  const posTex = canvasTex(360, 240, (g, w, h) => {
    g.fillStyle = '#1d3d6e'; g.fillRect(0, 0, w, h); g.fillStyle = '#2b5797'; g.fillRect(0, 0, w, 46);
    g.fillStyle = '#fff'; g.font = F(700, 26); g.fillText('ROUTE 9 POS', 14, 32);
    g.font = F(800, 64); g.textAlign = 'right'; g.fillText('$0.00', w - 18, 150);
    g.fillStyle = '#7fe0a0'; g.font = F(600, 22); g.textAlign = 'left'; g.fillText('READY', 16, 214);
  });
  texPlane(0.33, 0.22, posTex, 0, 0, 0.021, scr);
  box(0.09, 0.04, 0.16, '#26292f', -0.22, CT + 0.02, -0.66);
  box(0.07, 0.002, 0.05, '#7fe0a0', -0.22, CT + 0.041, -0.69, null, { flat: true });
  box(0.5, 0.12, 0.14, '#b9bfc7', 0.55, CT + 0.06, -0.72);
  const candy = canvasTex(500, 120, (g) => { g.fillStyle = '#d9dde2'; g.fillRect(0, 0, 500, 120); const cs = ['#e33b2f', '#f2b51e', '#2f73d8', '#2fa64d', '#8d4ad0', '#f07f22']; for (let i = 0; i < 10; i++) { g.fillStyle = cs[i % 6]; rr(g, 6 + i * 49, 18, 42, 92, 6); g.fill(); g.strokeStyle = '#1b1c20'; g.lineWidth = 3; rr(g, 6 + i * 49, 18, 42, 92, 6); g.stroke(); } });
  const cp = texPlane(0.5, 0.12, candy, 0.55, CT + 0.06, -0.638); cp.rotation.y = Math.PI;
  cyl(0.04, 0.032, 0.11, '#f3efe6', -1.35, CT + 0.055, -0.36);
  cyl(0.042, 0.042, 0.02, '#3b2a20', -1.35, CT + 0.115, -0.36);
  // landline (beige desk phone) with liftable handset
  const ll = new THREE.Group(); ll.position.set(-0.55, CT, -0.48); ll.rotation.y = 0.25; scene.add(ll); landline.g = ll;
  box(0.19, 0.06, 0.22, '#d8d1bf', 0, 0.03, 0, ll);
  const kp = canvasTex(120, 140, (g) => { g.fillStyle = '#cfc7b3'; g.fillRect(0, 0, 120, 140); g.fillStyle = '#5a5648'; for (let r = 0; r < 4; r++) for (let c = 0; c < 3; c++) { rr(g, 12 + c * 34, 10 + r * 32, 26, 24, 5); g.fill(); } });
  const kpp = texPlane(0.1, 0.11, kp, 0.03, 0.062, 0.03, ll); kpp.rotation.x = -Math.PI / 2;
  const hs = new THREE.Group(); ll.add(hs); landline.handset = hs; landline.rest = new THREE.Vector3(-0.045, 0.085, 0);
  hs.position.copy(landline.rest);
  const hb = box(0.05, 0.035, 0.21, '#d8d1bf', 0, 0, 0, hs);
  box(0.06, 0.05, 0.06, '#d8d1bf', 0, -0.01, 0.085, hs); box(0.06, 0.05, 0.06, '#d8d1bf', 0, -0.01, -0.085, hs);
  // phone (screen faces local +z)
  box(0.074, 0.154, 0.009, C.phone, 0, 0, 0, phone);
  const sp = add(new THREE.Mesh(new THREE.PlaneGeometry(0.067, 0.146), noOutline(new THREE.MeshBasicMaterial({ map: phoneTex }))), phone);
  sp.position.z = 0.0047;
}
export const rag = new THREE.Group(); scene.add(rag);
function buildRag() {
  const r = M(C.rag);
  for (const [x, z, s, h] of [[0, 0, 1, 1], [0.045, 0.02, 0.7, 0.8], [-0.04, 0.03, 0.75, 0.7], [0.01, -0.045, 0.65, 0.75], [-0.03, -0.03, 0.55, 0.6]]) {
    const m = add(new THREE.Mesh(new THREE.SphereGeometry(0.06 * s, 20, 12), r), rag); m.position.set(x, 0.006, z); m.scale.set(1, 0.22 * h, 1);
  }
}
// cashier's own torso + legs (seen when looking straight down)
export const body = new THREE.Group(); scene.add(body);
function buildBody() {
  const t = add(new THREE.Mesh(new THREE.CapsuleGeometry(0.17, 0.32, 8, 20), M(C.polo)), body); t.scale.set(1.15, 1, 0.75); t.position.set(0, 1.18, 0.1);
  for (const s of [-1, 1]) {
    const th = add(new THREE.Mesh(new THREE.CylinderGeometry(0.075, 0.065, 0.48, 16), M(C.pants)), body); th.position.set(s * 0.1, 0.7, 0.07);
    const sh = add(new THREE.Mesh(new THREE.CylinderGeometry(0.06, 0.05, 0.42, 16), M(C.pants)), body); sh.position.set(s * 0.1, 0.25, 0.06);
    box(0.11, 0.08, 0.27, '#1c1e24', s * 0.1, 0.04, 0.0, body);
  }
  box(0.36, 0.05, 0.22, '#1c1e24', 0, 0.95, 0.09, body);   // belt
}

export function buildSet() {
  buildRoom(); buildFront(); buildExterior(); buildCoolers(); buildStore(); buildCounter(); buildRag(); buildBody();
}
