// Code Black E1 set: Oakridge High 2nd-floor library (sunlit → lights out), hallway beyond the oak doors,
// the back stairwell (seen live on the librarian's CCTV monitor).
import { THREE, scene, M, noOutline, add, box, cyl, sph, canvasTex, texPlane, glowMat, glowSprite, F } from './core.js';

export const EYE = 1.2;                                   // seated eye height
export const ROOM = { x0: -6, x1: 6, z0: -14, z1: 2, h: 3.2 };
export const MAIN = { x: -6, z: -6.0 };                   // main oak double doors (left wall)
export const BACK = { x: 3.9, z: 2 };                     // back stairwell steel door (back wall)
export const DESK = new THREE.Vector3(2.15, 0, 0.55);
export const MON = new THREE.Vector3(2.3, 1.02, 0.78);    // CCTV monitor screen centre
export const S = {};
let sd = 4; const r = () => (sd = (sd * 16807) % 2147483647) / 2147483647;
const basic = (c, o = {}) => noOutline(new THREE.MeshBasicMaterial({ color: c, ...o }));

function bookTex(seed) {
  let s2 = seed; const rr = () => (s2 = (s2 * 16807) % 2147483647) / 2147483647;
  return canvasTex(512, 256, (g, w, h) => {
    g.fillStyle = '#5b4632'; g.fillRect(0, 0, w, h);
    const cols = ['#b23a3a', '#2f5d9a', '#3c8a52', '#d9a33a', '#6b3f8f', '#e0dccd', '#1f3460', '#c46a2c', '#2c2c30'];
    for (const y0 of [8, 134]) { let x = 6; while (x < w - 8) { const bw = 10 + rr() * 16, bh = 92 + rr() * 26; g.fillStyle = cols[Math.floor(rr() * cols.length)]; g.fillRect(x, y0 + 118 - bh, bw, bh); g.fillStyle = 'rgba(255,255,255,.25)'; g.fillRect(x + 2, y0 + 118 - bh + 10, bw - 4, 3); x += bw + 1.5; } }
    g.fillStyle = '#3f2f21'; g.fillRect(0, 126, w, 8); g.fillRect(0, 250, w, 6);
  });
}
function shelf(x, z, len, rotY = 0, h = 2.2) {
  const g = new THREE.Group(); g.position.set(x, 0, z); g.rotation.y = rotY; scene.add(g);
  box(len, h, 0.42, '#6d533b', 0, h / 2, 0, g);
  for (const s of [-1, 1]) { const t = texPlane(len - 0.08, h - 0.2, bookTex(Math.floor(x * 31 + z * 17 + s * 7 + 99)), 0, h / 2, s * 0.215, g, false); if (s < 0) t.rotation.y = Math.PI; }
  return g;
}
function table(x, z, w = 1.8, d = 0.9) { box(w, 0.06, d, '#c9a46e', x, 0.76, z); for (const [dx, dz] of [[-w / 2 + 0.08, -d / 2 + 0.08], [w / 2 - 0.08, -d / 2 + 0.08], [-w / 2 + 0.08, d / 2 - 0.08], [w / 2 - 0.08, d / 2 - 0.08]]) box(0.06, 0.74, 0.06, '#6b6f78', x + dx, 0.37, z + dz); }
function chair(x, z, ry) { const g = new THREE.Group(); g.position.set(x, 0, z); g.rotation.y = ry; scene.add(g); box(0.44, 0.05, 0.42, '#2f5d9a', 0, 0.46, 0, g); box(0.44, 0.45, 0.05, '#2f5d9a', 0, 0.7, -0.2, g); for (const [dx, dz] of [[-0.19, -0.18], [0.19, -0.18], [-0.19, 0.18], [0.19, 0.18]]) box(0.03, 0.45, 0.03, '#888c94', dx, 0.22, dz, g); return g; }

function buildLibrary() {
  const { x0, x1, z0, z1, h } = ROOM;
  const carpet = canvasTex(1024, 1024, (g, w) => { g.fillStyle = '#5d6b82'; g.fillRect(0, 0, w, w); for (let i = 0; i < 1400; i++) { g.fillStyle = `rgba(${r() > .5 ? 255 : 0},${r() > .5 ? 255 : 0},${255},${0.03})`; g.fillRect(r() * w, r() * w, 3, 3); } g.strokeStyle = 'rgba(30,40,60,.18)'; g.lineWidth = 3; for (let x = 0; x < w; x += 128) { g.beginPath(); g.moveTo(x, 0); g.lineTo(x, w); g.stroke(); g.beginPath(); g.moveTo(0, x); g.lineTo(w, x); g.stroke(); } });
  carpet.wrapS = carpet.wrapT = THREE.RepeatWrapping; carpet.repeat.set(3, 4);
  { const f = add(new THREE.Mesh(new THREE.PlaneGeometry(x1 - x0, z1 - z0), new THREE.MeshToonMaterial({ map: carpet, gradientMap: M('#000').gradientMap }))); f.material.userData.outlineParameters = { visible: false }; f.rotation.x = -Math.PI / 2; f.position.set(0, 0, (z0 + z1) / 2); }
  box(x1 - x0, 0.06, z1 - z0, '#e9e6dc', 0, h, (z0 + z1) / 2);
  S.panels = [];
  for (let x = -4; x <= 4; x += 2.7) for (let z = -12; z <= 0; z += 3) { const p = box(1.2, 0.03, 0.6, '#fbfaf0', x, h - 0.03, z); p.material = basic('#fbfaf0'); S.panels.push(p); }
  const wallM = '#e8e1cf';
  box(0.12, h, z1 - z0, wallM, x1 + 0.06, h / 2, (z0 + z1) / 2);                                  // right wall (windows cut as panes over it)
  box(x1 - x0, h, 0.12, wallM, 0, h / 2, z0 - 0.06);                                            // front wall
  // left wall with the main door gap
  const dz0 = MAIN.z - 0.95, dz1 = MAIN.z + 0.95, DH = 2.35;
  box(0.12, h, dz0 - z0, wallM, x0 - 0.06, h / 2, (z0 + dz0) / 2); box(0.12, h, z1 - dz1, wallM, x0 - 0.06, h / 2, (dz1 + z1) / 2); box(0.12, h - DH, dz1 - dz0, wallM, x0 - 0.06, (h + DH) / 2, MAIN.z);
  // back wall with the stairwell door gap
  const bx0 = BACK.x - 0.5, bx1 = BACK.x + 0.5;
  box(bx0 - x0, h, 0.12, wallM, (x0 + bx0) / 2, h / 2, z1 + 0.06); box(x1 - bx1, h, 0.12, wallM, (bx1 + x1) / 2, h / 2, z1 + 0.06); box(1.0, h - 2.15, 0.12, wallM, BACK.x, (h + 2.15) / 2, z1 + 0.06);
  // wainscot stripe
  for (const [w, x, z, ry] of [[z1 - z0, x1 - 0.005, (z0 + z1) / 2, -Math.PI / 2], [x1 - x0, 0, z0 + 0.005, 0]]) { const s2 = add(new THREE.Mesh(new THREE.PlaneGeometry(w, 0.12), basic('#2f5d9a'))); s2.position.set(x, 1.0, z); s2.rotation.y = ry; }
  // windows on the right wall (sun, then grey-blue)
  S.windows = [];
  for (const z of [-11.5, -7.5, -3.5]) {
    const glass = add(new THREE.Mesh(new THREE.PlaneGeometry(2.6, 1.7), basic('#fff6d8'))); glass.position.set(x1 - 0.002, 1.95, z); glass.rotation.y = -Math.PI / 2; S.windows.push(glass);
    for (const dz of [-1.3, 0, 1.3]) box(0.06, 1.74, 0.06, '#ffffff', x1 - 0.03, 1.95, z + dz); for (const y of [1.1, 2.8]) box(0.08, 0.06, 2.66, '#ffffff', x1 - 0.03, y, z);
    const pool = add(new THREE.Mesh(new THREE.PlaneGeometry(2.4, 2.6), glowMat('#fff2c8', 0.14))); pool.rotation.x = -Math.PI / 2; pool.position.set(x1 - 1.9, 0.01, z); S.windows.push(pool);
  }
  // PA speaker + clock + banner on the front wall
  S.speaker = new THREE.Group(); S.speaker.position.set(x0 + 0.06, 2.6, -2.6); S.speaker.rotation.y = Math.PI / 2; scene.add(S.speaker);
  S.speaker.scale.setScalar(1.5); box(0.42, 0.42, 0.1, '#d8d4c8', 0, 0, 0.05, S.speaker); const grill = canvasTex(128, 128, (g) => { g.fillStyle = '#d8d4c8'; g.fillRect(0, 0, 128, 128); g.fillStyle = '#3a3d44'; for (let y = 14; y < 120; y += 12) for (let x = 14; x < 120; x += 12) { g.beginPath(); g.arc(x, y, 3.2, 0, 7); g.fill(); } }); texPlane(0.36, 0.36, grill, 0, 0, 0.105, S.speaker, false);
  { const c = cyl(0.22, 0.22, 0.05, '#ffffff', 1.6, 2.6, z0 + 0.04); c.rotation.x = Math.PI / 2; const ct = canvasTex(128, 128, (g) => { g.fillStyle = '#fff'; g.beginPath(); g.arc(64, 64, 62, 0, 7); g.fill(); g.strokeStyle = '#222'; g.lineWidth = 6; g.beginPath(); g.moveTo(64, 64); g.lineTo(64, 18); g.stroke(); g.beginPath(); g.moveTo(64, 64); g.lineTo(98, 70); g.stroke(); }); texPlane(0.4, 0.4, ct, 1.6, 2.6, z0 + 0.07); }
  const ban = canvasTex(1024, 160, (g, w) => { g.fillStyle = '#1f3460'; g.fillRect(0, 0, w, 160); g.fillStyle = '#f5d23a'; g.font = F(900, 96); g.textAlign = 'center'; g.fillText('OAKRIDGE HIGH LIBRARY', w / 2, 116); });
  texPlane(3.6, 0.56, ban, 2.2, 2.85, z0 + 0.07, null, false);
  // shelves (front stacks + the tall back shelf we hide behind)
  for (const z of [-9.2, -11.2, -13.3]) { shelf(-2.6, z, 3.4); shelf(2.6, z, 3.4); }
  S.backShelf = shelf(1.0, -1.65, 2.4);
  shelf(5.6, -1.0, 2.2, Math.PI / 2, 1.9);
  // study tables + chairs + laptops
  table(0, -4.2); chair(0, -3.35, Math.PI); chair(0, -5.05, 0);
  table(-3.4, -5.0); chair(-3.4, -4.15, Math.PI); chair(-3.4, -5.85, 0);
  table(3.4, -4.4); chair(3.4, -3.55, Math.PI); chair(3.4, -5.25, 0);
  table(3.4, -7.0); chair(3.4, -6.15, Math.PI);
  for (const [x, z, ry] of [[-3.5, -5.2, 0.1], [3.3, -4.6, 0.3], [0.45, -4.45, -0.2]]) { const lg = new THREE.Group(); lg.position.set(x, 0.79, z); lg.rotation.y = ry; scene.add(lg); box(0.34, 0.015, 0.24, '#9aa0a8', 0, 0, 0, lg); const sc = box(0.34, 0.22, 0.012, '#2a2d34', 0, 0.11, -0.12, lg); sc.rotation.x = -0.2; const scr = add(new THREE.Mesh(new THREE.PlaneGeometry(0.3, 0.18), basic('#9fc4ff')), lg); scr.position.set(0, 0.115, -0.112); scr.rotation.x = -0.2; }
  box(0.22, 0.03, 0.3, '#e9e6dc', -0.35, 0.8, -4.05); box(0.2, 0.025, 0.28, '#f4f1e8', 0.25, 0.8, -4.5);   // notebooks
  // the main oak doors (double), glass strips, deadbolt, lever handle, light switch
  S.mainDoor = new THREE.Group(); S.mainDoor.position.set(x0 - 0.02, 0, MAIN.z); scene.add(S.mainDoor);
  const oak = canvasTex(256, 512, (g, w, hh) => { g.fillStyle = '#8a5a32'; g.fillRect(0, 0, w, hh); for (let i = 0; i < 60; i++) { g.strokeStyle = `rgba(60,30,10,${0.08 + r() * 0.1})`; g.lineWidth = 2; g.beginPath(); const x = r() * w; g.moveTo(x, 0); g.bezierCurveTo(x + 10, hh * 0.3, x - 10, hh * 0.7, x + 4, hh); g.stroke(); } });
  const oakM = new THREE.MeshToonMaterial({ map: oak, gradientMap: M('#000').gradientMap }); oakM.userData.outlineParameters = { thickness: 0.0029, color: [0.08, 0.08, 0.09], alpha: 1 };
  for (const s of [-1, 1]) {
    const zc = s * 0.47, gz = s * 0.72, gy0 = 1.05, gy1 = 2.05, gw = 0.3;
    const piece = (h2, y, w2, z) => { const d = add(new THREE.Mesh(new THREE.BoxGeometry(0.07, h2, w2), oakM), S.mainDoor); d.position.set(0, y, z); };
    piece(gy0, gy0 / 2, 0.92, zc); piece(DH - 0.02 - gy1, (gy1 + DH - 0.02) / 2, 0.92, zc);
    const inner = s > 0 ? [zc - 0.46, gz - gw / 2] : [gz + gw / 2, zc + 0.46], outer = s > 0 ? [gz + gw / 2, zc + 0.46] : [zc - 0.46, gz - gw / 2];
    for (const [a1, b1] of [inner, outer]) if (b1 - a1 > 0.01) piece(gy1 - gy0, (gy0 + gy1) / 2, b1 - a1, (a1 + b1) / 2);
    const gl = add(new THREE.Mesh(new THREE.PlaneGeometry(0.3, 1.0), basic('#9fb6cc', { transparent: true, opacity: 0.14, depthWrite: false })), S.mainDoor); gl.position.set(0.04, 1.55, s * 0.72); gl.rotation.y = Math.PI / 2;
  }
  S.glassZ = MAIN.z + 0.72;
  for (const zz of [dz0 - 0.05, dz1 + 0.05]) box(0.18, DH + 0.1, 0.1, '#5a3a20', x0, (DH + 0.1) / 2, zz); box(0.18, 0.1, 2.0, '#5a3a20', x0, DH + 0.05, MAIN.z);
  S.lever = new THREE.Group(); S.lever.position.set(x0 + 0.06, 1.05, MAIN.z + 0.12); scene.add(S.lever);
  cyl(0.03, 0.03, 0.04, '#c9a640', 0, 0, 0, S.lever).rotation.z = Math.PI / 2; box(0.03, 0.03, 0.15, '#d8b54c', 0.04, 0, 0.07, S.lever);
  S.bolt = new THREE.Group(); S.bolt.position.set(x0 + 0.06, 1.35, MAIN.z + 0.12); scene.add(S.bolt);
  cyl(0.035, 0.035, 0.03, '#c9a640', 0, 0, 0, S.bolt).rotation.z = Math.PI / 2; S.boltKnob = box(0.03, 0.08, 0.02, '#d8b54c', 0.03, 0, 0, S.bolt);
  box(0.02, 0.14, 0.09, '#f2efe6', x0 + 0.01, 1.3, MAIN.z + 1.35);       // light switch
  S.charge = glowSprite('#ff2020', 0.7); S.charge.position.set(x0 - 0.12, 1.55, S.glassZ); S.charge.material.opacity = 0;
  // librarian's desk + CCTV monitor + exit sign
  box(1.7, 0.08, 0.7, '#b48a5a', DESK.x, 0.82, DESK.z); box(1.7, 0.78, 0.06, '#8a6a46', DESK.x, 0.4, DESK.z - 0.33); box(0.06, 0.78, 0.66, '#8a6a46', DESK.x + 0.82, 0.4, DESK.z);
  S.monitor = new THREE.Group(); S.monitor.position.copy(MON); scene.add(S.monitor);
  box(0.56, 0.4, 0.05, '#1c1e22', 0, 0, -0.03, S.monitor); box(0.08, 0.16, 0.06, '#1c1e22', 0, -0.26, -0.05, S.monitor);
  S.screen = add(new THREE.Mesh(new THREE.PlaneGeometry(0.5, 0.34), basic('#222')), S.monitor); S.screen.position.z = 0.0;
  S.monGlow = glowSprite('#d9e4ff', 0.9, S.monitor); S.monGlow.position.z = 0.08; S.monGlow.material.opacity = 0.06;
  { const kb = box(0.4, 0.02, 0.14, '#2a2c31', DESK.x - 0.1, 0.87, DESK.z + 0.1); }
  const ex = canvasTex(256, 96, (g, w) => { g.fillStyle = '#0f6a32'; g.fillRect(0, 0, w, 96); g.fillStyle = '#ffffff'; g.font = F(900, 60); g.textAlign = 'center'; g.fillText('EXIT', w / 2, 70); });
  S.exit = texPlane(0.42, 0.16, ex, BACK.x, 2.4, ROOM.z1 - 0.01); S.exit.rotation.y = Math.PI;
  S.exitGlow = glowSprite('#3dff7a', 0.6); S.exitGlow.position.set(BACK.x, 2.4, ROOM.z1 - 0.05);
}

function buildBackDoor() {
  // steel stairwell door (opens outward into the stairwell) with a push-bar
  S.backDoor = new THREE.Group(); S.backDoor.position.set(BACK.x - 0.48, 0, ROOM.z1 + 0.04); scene.add(S.backDoor);
  box(0.96, 2.12, 0.06, '#8d949c', 0.48, 1.06, 0, S.backDoor);
  const sign = canvasTex(512, 160, (g, w) => { g.fillStyle = '#c9312a'; g.fillRect(0, 0, w, 160); g.fillStyle = '#fff'; g.font = F(900, 54); g.textAlign = 'center'; g.fillText('STAIRWELL B', w / 2, 70); g.font = F(800, 34); g.fillText('EMERGENCY EXIT', w / 2, 122); });
  const sg = texPlane(0.5, 0.16, sign, 0.48, 1.65, -0.035, S.backDoor); sg.rotation.y = Math.PI;
  S.pushBar = box(0.78, 0.07, 0.08, '#c7ccd2', 0.48, 1.0, -0.08, S.backDoor);
  for (const dx of [0.1, 0.86]) box(0.06, 0.12, 0.08, '#9aa0a6', dx, 1.0, -0.05, S.backDoor);
  box(0.08, 2.2, 0.16, '#6d737a', BACK.x - 0.54, 1.1, ROOM.z1 + 0.04); box(0.08, 2.2, 0.16, '#6d737a', BACK.x + 0.54, 1.1, ROOM.z1 + 0.04); box(1.16, 0.08, 0.16, '#6d737a', BACK.x, 2.18, ROOM.z1 + 0.04);
}

function buildHallway() {
  const { x0 } = ROOM;
  const f = add(new THREE.Mesh(new THREE.PlaneGeometry(4, 22), basic('#9aa0a6'))); f.rotation.x = -Math.PI / 2; f.position.set(x0 - 2.1, 0.002, -6);
  box(0.12, 3.2, 22, '#c9ccc4', x0 - 4.0, 1.6, -6);
  for (let z = -15; z < 4; z += 0.62) { box(0.4, 1.9, 0.58, '#2f5d9a', x0 - 3.75, 0.95, z); }
  box(4, 0.06, 22, '#d8d8d0', x0 - 2.1, 3.2, -6);
  S.hallLight = new THREE.PointLight('#ffd9b0', 0, 12, 1.2); S.hallLight.position.set(x0 - 2, 2.8, -6); scene.add(S.hallLight);
}

function buildStairwell() {
  // offstage concrete stairwell behind the back door; only ever seen through the CCTV camera
  const z0 = ROOM.z1 + 0.1, cx = BACK.x + 0.6;
  const conc = '#b9b9b2';
  { const f = add(new THREE.Mesh(new THREE.PlaneGeometry(5, 5), M('#9a9a94'))); f.rotation.x = -Math.PI / 2; f.position.set(cx, 0.003, z0 + 2.5); }
  box(0.15, 3.2, 5, conc, cx - 2.5, 1.6, z0 + 2.5); box(0.15, 3.2, 5, conc, cx + 2.5, 1.6, z0 + 2.5); box(5, 3.2, 0.15, conc, cx, 1.6, z0 + 5); box(5, 0.1, 5, '#cfcfc8', cx, 3.2, z0 + 2.5);
  for (let i = 0; i < 8; i++) box(1.1, 0.18, 0.3, '#a5a59e', cx - 1.8, 0.09 + i * 0.18, z0 + 2.4 + i * 0.3);       // stairs going up (left)
  box(0.12, 1.6, 1.6, conc, BACK.x + 1.55, 0.8, z0 + 1.55);                                                      // the blind corner
  box(0.05, 1.0, 2.4, '#5a5f66', cx - 1.2, 1.05, z0 + 3.4);                                                    // railing
  S.stairLight = new THREE.PointLight('#e8ecf2', 2.2, 7, 1.4); S.stairLight.position.set(cx, 2.9, z0 + 2.5); scene.add(S.stairLight);
}

export function buildSet() { buildLibrary(); buildBackDoor(); buildHallway(); buildStairwell(); }
