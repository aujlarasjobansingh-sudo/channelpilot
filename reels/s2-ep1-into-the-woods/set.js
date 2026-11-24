// Season 2 Ep1 set: rain-soaked pine woods, the tripping root, and the abandoned ranger cabin (exterior + interior):
// plank walls, cracked shutters, a door with a deadbolt, shelves, table, frayed rug over a rusted cellar hatch.
import { THREE, scene, M, noOutline, add, box, cyl, sph, canvasTex, texPlane, glowMat, glowSprite, F } from './core.js';

export const EYE = 1.62;
export const CAB = { x0: -2.5, x1: 2.5, z0: -31.5, z1: -27.5, h: 2.6 };        // interior box (front wall at z1 faces the approach)
export const DOOR_X = 0.9, WIN_X = -1.25, WIN_Y0 = 1.0, WIN_Y1 = 1.75;
export const HATCH = new THREE.Vector3(0.15, 0, -29.6);
export const S = {};
let sd = 9; const r = () => (sd = (sd * 16807) % 2147483647) / 2147483647;
const basic = (c, o = {}) => noOutline(new THREE.MeshBasicMaterial({ color: c, ...o }));

const plankTex = (base, dark) => canvasTex(512, 512, (g, w, h) => {
  g.fillStyle = base; g.fillRect(0, 0, w, h);
  for (let y = 0; y < h; y += 64) { g.fillStyle = dark; g.fillRect(0, y, w, 5); for (let i = 0; i < 14; i++) { g.fillStyle = `rgba(0,0,0,${0.05 + r() * 0.08})`; g.fillRect(r() * w, y + 8 + r() * 50, 30 + r() * 120, 2); } }
  for (let i = 0; i < 6; i++) { g.fillStyle = 'rgba(0,0,0,0.35)'; g.beginPath(); g.arc(r() * w, r() * h, 3 + r() * 4, 0, 7); g.fill(); }
});

function buildWoods() {
  const mud = canvasTex(1024, 1024, (g, w, h) => { g.fillStyle = '#141712'; g.fillRect(0, 0, w, h);
    for (let i = 0; i < 260; i++) { g.fillStyle = `rgba(${40 + r() * 30},${36 + r() * 20},${22 + r() * 12},${0.25 + r() * 0.3})`; g.beginPath(); g.ellipse(r() * w, r() * h, 6 + r() * 40, 3 + r() * 14, r() * 3, 0, 7); g.fill(); }
    for (let i = 0; i < 40; i++) { g.fillStyle = `rgba(120,140,170,${0.06 + r() * 0.08})`; g.beginPath(); g.ellipse(r() * w, r() * h, 20 + r() * 50, 6 + r() * 14, 0, 0, 7); g.fill(); } });
  mud.wrapS = mud.wrapT = THREE.RepeatWrapping; mud.repeat.set(10, 10);
  const ground = add(new THREE.Mesh(new THREE.PlaneGeometry(140, 140), basic('#ffffff', { map: mud }))); ground.rotation.x = -Math.PI / 2; ground.position.set(0, 0, -30);
  const treeM = [M('#0e1913'), M('#132219'), M('#0b150f')], trunkM = M('#20160f');
  const tree = (x, z, h) => { const k = treeM[Math.floor(r() * 3)];
    for (let i = 0; i < 3; i++) { const c = add(new THREE.Mesh(new THREE.ConeGeometry(h * (0.3 - i * 0.07), h * 0.42, 8), k)); c.position.set(x, h * (0.36 + i * 0.2), z); }
    const tr = add(new THREE.Mesh(new THREE.CylinderGeometry(0.1, 0.16, h * 0.5, 7), trunkM)); tr.position.set(x, h * 0.25, z); };
  for (let i = 0; i < 420; i++) {
    const x = -45 + r() * 90, z = 25 - r() * 90;
    if (Math.abs(x - pathX(z)) < 1.7 && z > -27) continue;                       // keep the escape path clear
    if (x > CAB.x0 - 2 && x < CAB.x1 + 2 && z < -25.5 && z > CAB.z0 - 2) continue; // clearing around the cabin
    tree(x, z, 6 + r() * 7);
  }
  for (let i = 0; i < 60; i++) { const z = 20 - r() * 45, x = pathX(z) + (r() > 0.5 ? 1 : -1) * (1.9 + r() * 2.5); const b = sph(0.5 + r() * 0.5, '#101a13', x, 0.25, z); b.scale.y = 0.55; }
  // the root that trips us (across the path)
  const rootM = M('#2a1d13');
  S.root = new THREE.Group(); scene.add(S.root); S.root.position.set(pathX(-13.6), 0.05, -13.6);
  const rt = add(new THREE.Mesh(new THREE.CapsuleGeometry(0.07, 2.2, 6, 10), rootM), S.root); rt.rotation.z = Math.PI / 2; rt.rotation.y = 0.25;
  // police lights sweeping far behind us (through the trees)
  S.pol = [0, 1, 2].map(i => { const g = glowSprite(i % 2 ? '#2a5bff' : '#ff2a2a', 5); g.position.set(-6 + i * 6, 2, 22); return g; });
  S.beams = [0, 1].map(() => { const b = add(new THREE.Mesh(new THREE.ConeGeometry(2.6, 30, 24, 1, true), glowMat('#eef2ff', 0.035))); b.rotation.x = Math.PI / 2; return b; });
  S.moon = glowSprite('#c9d8ff', 9); S.moon.position.set(-25, 30, -70);
}
export function pathX(z) { return 0.6 * Math.sin(z * 0.11) + (z < -18 ? (z + 18) * -0.04 : 0); }

function buildCabin() {
  const { x0, x1, z0, z1, h } = CAB, T = 0.12;
  const outer = M('#3b2c22'), inner = new THREE.MeshToonMaterial({ color: '#5a4636', map: plankTex('#ffffff', '#9a8a7a'), gradientMap: M('#000').gradientMap });
  inner.userData.outlineParameters = { thickness: 0.0029, color: [0.08, 0.08, 0.09], alpha: 1 };
  const outT = plankTex('#4a3729', '#24190f'); const outerM = new THREE.MeshToonMaterial({ color: '#ffffff', map: outT, gradientMap: inner.gradientMap }); outerM.userData.outlineParameters = inner.userData.outlineParameters;
  const wall = (w, hh, d, x, y, z) => { const m = add(new THREE.Mesh(new THREE.BoxGeometry(w, hh, d), [outerM, outerM, outer, outer, outerM, outerM])); m.position.set(x, y, z); return m; };
  // interior faces (separate thin planes so the inside reads as old boards)
  const inPlane = (w, hh, x, y, z, ry) => { const m = add(new THREE.Mesh(new THREE.PlaneGeometry(w, hh), inner)); m.position.set(x, y, z); m.rotation.y = ry; return m; };
  wall(x1 - x0 + 2 * T, h, T, 0, h / 2, z0 - T / 2); inPlane(x1 - x0, h, 0, h / 2, z0 + 0.001, 0);           // back
  wall(T, h, z1 - z0, x0 - T / 2, h / 2, (z0 + z1) / 2); inPlane(z1 - z0, h, x0 + 0.001, h / 2, (z0 + z1) / 2, Math.PI / 2);  // left
  wall(T, h, z1 - z0, x1 + T / 2, h / 2, (z0 + z1) / 2); inPlane(z1 - z0, h, x1 - 0.001, h / 2, (z0 + z1) / 2, -Math.PI / 2); // right
  // front wall with a door gap and a window gap
  const DW = 0.92, DH = 2.0, WW = 0.8;
  const seg = (a, b, y0, y1) => { if (b - a < 0.01 || y1 - y0 < 0.01) return; wall(b - a, y1 - y0, T, (a + b) / 2, (y0 + y1) / 2, z1 + T / 2); inPlane(b - a, y1 - y0, (a + b) / 2, (y0 + y1) / 2, z1 - 0.001, Math.PI); };
  const wa = WIN_X - WW / 2, wb = WIN_X + WW / 2, da = DOOR_X - DW / 2, db = DOOR_X + DW / 2;
  seg(x0 - T, wa, 0, h); seg(wa, wb, 0, WIN_Y0); seg(wa, wb, WIN_Y1, h); seg(wb, da, 0, h); seg(da, db, DH, h); seg(db, x1 + T, 0, h);
  // roof + floor
  const roof = add(new THREE.Mesh(new THREE.BoxGeometry(x1 - x0 + 1.2, 0.16, z1 - z0 + 1.4), M('#241a13'))); roof.position.set(0, h + 0.35, (z0 + z1) / 2); roof.rotation.x = 0.0;
  for (const s of [-1, 1]) { const rf = add(new THREE.Mesh(new THREE.BoxGeometry(x1 - x0 + 1.2, 0.12, (z1 - z0) / 2 + 0.9), M('#2a1f17'))); rf.position.set(0, h + 0.55, (z0 + z1) / 2 + s * ((z1 - z0) / 4 + 0.2)); rf.rotation.x = s * 0.35; }
  box(x1 - x0 + 0.3, 0.08, z1 - z0 + 0.3, '#2a2119', 0, h + 0.02, (z0 + z1) / 2);
  const floorT = plankTex('#3e3127', '#1f1712'); floorT.wrapS = floorT.wrapT = THREE.RepeatWrapping; floorT.repeat.set(2, 2);
  { const f = add(new THREE.Mesh(new THREE.PlaneGeometry(x1 - x0, z1 - z0), basic('#ffffff', { map: floorT }))); f.rotation.x = -Math.PI / 2; f.position.set(0, 0.006, (z0 + z1) / 2); }
  // porch + steps
  box(x1 - x0 + 0.6, 0.14, 1.4, '#3a2b20', 0, 0.07, z1 + 0.75); box(1.2, 0.08, 0.4, '#3a2b20', DOOR_X, 0.04, z1 + 1.6);
  for (const x of [x0 - 0.1, x1 + 0.1]) cyl(0.07, 0.07, h, '#2e2219', x, h / 2, z1 + 1.35);
  // door (hinged at its left edge), deadbolt
  S.door = new THREE.Group(); S.door.position.set(da, 0, z1 + 0.02); scene.add(S.door);
  const dT = plankTex('#7a3a24', '#3a160c'); const dM = new THREE.MeshToonMaterial({ color: '#ffffff', map: dT, gradientMap: inner.gradientMap }); dM.userData.outlineParameters = inner.userData.outlineParameters;
  const dp = add(new THREE.Mesh(new THREE.BoxGeometry(DW - 0.02, DH - 0.02, 0.06), dM), S.door); dp.position.set(DW / 2, DH / 2, 0);
  for (const y of [0.4, 1.6]) box(DW - 0.08, 0.1, 0.03, '#3a2a1e', DW / 2, y, -0.045, S.door);
  box(0.06, 0.12, 0.05, '#7a7d82', DW - 0.12, 1.0, -0.05, S.door);                    // knob plate
  S.bolt = box(0.16, 0.04, 0.04, '#b8bec4', DW - 0.14, 1.25, -0.06, S.door);
  box(0.05, 0.08, 0.05, '#6d7075', db + 0.04, 1.25, z1 - 0.03);                      // strike on the frame
  for (const x of [da - 0.04, db + 0.04]) box(0.08, DH + 0.08, 0.16, '#1e140d', x, (DH + 0.08) / 2, z1); box(DW + 0.16, 0.08, 0.16, '#1e140d', DOOR_X, DH + 0.04, z1);
  // window: shutters with cracks (outside) — slats
  S.slats = [];
  for (let i = 0; i < 7; i++) { const y = WIN_Y0 + 0.05 + i * 0.1; const sl = box(WW - 0.02, 0.075, 0.03, '#3d2d21', WIN_X, y, z1 + 0.09); S.slats.push(sl); }
  box(WW + 0.12, 0.06, 0.06, '#2c2018', WIN_X, WIN_Y1, z1 + 0.1); box(WW + 0.12, 0.06, 0.06, '#2c2018', WIN_X, WIN_Y0, z1 + 0.1);
  // light coming through the cracks (moonlight, then the flashlight) — additive slabs reaching into the room
  S.shafts = [];
  for (let i = 0; i < 6; i++) {
    const y = WIN_Y0 + 0.1 + i * 0.1, m = add(new THREE.Mesh(new THREE.PlaneGeometry(WW * 0.9, 3.2), glowMat('#cfe0ff', 0.0)));
    m.position.set(WIN_X + 0.3, y - 0.35, z1 - 1.55); m.rotation.set(-Math.PI / 2 + 0.25, 0.25, 0); S.shafts.push(m);
  }
  S.dust = []; for (let i = 0; i < 80; i++) { const d = glowSprite('#ffffff', 0.025); d.position.set(WIN_X + (r() - 0.3) * 1.4, 0.3 + r() * 1.5, z1 - 0.2 - r() * 2.6); d.material.opacity = 0; S.dust.push({ d, p: d.position.clone(), ph: r() * 6 }); }
  S.winGlow = glowSprite('#dfe9ff', 1.2); S.winGlow.position.set(WIN_X, (WIN_Y0 + WIN_Y1) / 2, z1 - 0.02); S.winGlow.material.opacity = 0;
  S.moonPool = add(new THREE.Mesh(new THREE.PlaneGeometry(1.1, 1.6), glowMat('#9fb8ff', 0.05))); S.moonPool.rotation.x = -Math.PI / 2; S.moonPool.position.set(WIN_X + 0.35, 0.01, z1 - 1.3);
  S.lightPool = add(new THREE.Mesh(new THREE.PlaneGeometry(1.1, 2.2), glowMat('#f4f8ff', 0))); S.lightPool.rotation.x = -Math.PI / 2; S.lightPool.position.set(WIN_X + 0.5, 0.012, z1 - 1.7);
  // furniture
  const wood = '#4a3626';
  box(1.3, 0.06, 0.75, wood, -1.35, 0.76, -30.3); for (const [dx, dz] of [[-0.58, -0.32], [0.58, -0.32], [-0.58, 0.32], [0.58, 0.32]]) box(0.06, 0.74, 0.06, '#3a2a1e', -1.35 + dx, 0.37, -30.3 + dz);
  box(0.45, 0.04, 0.45, wood, -0.55, 0.45, -30.1); for (const [dx, dz] of [[-0.19, -0.19], [0.19, -0.19], [-0.19, 0.19], [0.19, 0.19]]) box(0.04, 0.44, 0.04, '#3a2a1e', -0.55 + dx, 0.22, -30.1 + dz);
  // shelves on the back wall with jars, cans, a lantern
  for (const y of [0.9, 1.4, 1.9]) box(1.8, 0.04, 0.3, wood, -1.1, y, z0 + 0.17);
  for (let i = 0; i < 14; i++) { const y = [0.9, 1.4, 1.9][i % 3] + 0.1, x = -1.85 + r() * 1.5; (i % 2 ? cyl(0.05, 0.05, 0.16, ['#6b7d5a', '#8c6d3a', '#4f5f6e'][i % 3], x, y + 0.02, z0 + 0.17) : box(0.1, 0.18, 0.1, ['#7a3d2a', '#3f4a3a', '#5c5242'][i % 3], x, y + 0.03, z0 + 0.17)); }
  cyl(0.07, 0.08, 0.22, '#2a2d30', 1.6, 0.86, -30.6); // old lantern on a crate
  box(0.5, 0.75, 0.5, '#3a2b1f', 1.6, 0.375, -30.6);
  // rusted cellar hatch + the frayed rug over it
  const rust = canvasTex(256, 256, (g, w) => { g.fillStyle = '#5a3a24'; g.fillRect(0, 0, w, w); for (let i = 0; i < 90; i++) { g.fillStyle = `rgba(${120 + r() * 60},${60 + r() * 30},${20},${0.3})`; g.beginPath(); g.arc(r() * w, r() * w, 3 + r() * 14, 0, 7); g.fill(); } g.strokeStyle = '#2a1a10'; g.lineWidth = 8; g.strokeRect(10, 10, w - 20, w - 20); });
  S.hatchHole = add(new THREE.Mesh(new THREE.PlaneGeometry(0.9, 0.9), basic('#030303'))); S.hatchHole.rotation.x = -Math.PI / 2; S.hatchHole.position.set(HATCH.x, 0.008, HATCH.z);
  S.hatchPivot = new THREE.Group(); S.hatchPivot.position.set(HATCH.x, 0.01, HATCH.z - 0.45); scene.add(S.hatchPivot);
  const lid = add(new THREE.Mesh(new THREE.BoxGeometry(0.92, 0.04, 0.92), new THREE.MeshToonMaterial({ color: '#ffffff', map: rust, gradientMap: inner.gradientMap })), S.hatchPivot);
  lid.material.userData.outlineParameters = inner.userData.outlineParameters; lid.position.set(0, 0.02, 0.46);
  const handle = add(new THREE.Mesh(new THREE.TorusGeometry(0.07, 0.014, 8, 20, Math.PI), M('#3a3c3f')), S.hatchPivot); handle.position.set(0, 0.045, 0.75); handle.rotation.x = -Math.PI / 2;
  const rugT = canvasTex(512, 384, (g, w, h) => { g.fillStyle = '#6b2b26'; g.fillRect(0, 0, w, h); g.strokeStyle = '#c9a25a'; g.lineWidth = 14; g.strokeRect(24, 24, w - 48, h - 48); g.strokeStyle = '#2c3f5a'; g.lineWidth = 8; g.strokeRect(60, 60, w - 120, h - 120);
    for (let i = 0; i < 40; i++) { g.fillStyle = 'rgba(0,0,0,0.12)'; g.fillRect(Math.random() * w, Math.random() * h, 20, 3); } g.fillStyle = '#c9a25a'; for (let x = 0; x < w; x += 12) { g.fillRect(x, 0, 4, 10); g.fillRect(x, h - 10, 4, 10); } });
  S.rug = add(new THREE.Mesh(new THREE.PlaneGeometry(1.7, 1.25), basic('#ffffff', { map: rugT, side: THREE.DoubleSide }))); S.rug.rotation.x = -Math.PI / 2; S.rug.position.set(HATCH.x, 0.03, HATCH.z);
  // moon/blue fill inside + the outside flashlight (a real spot so it lights the room through the cracks)
  S.inLight = new THREE.PointLight('#8fa8ff', 0, 7, 1.5); S.inLight.position.set(0, 2.2, -29.5); scene.add(S.inLight);
  S.flashIn = new THREE.PointLight('#f2f6ff', 0, 5, 1.6); S.flashIn.position.set(WIN_X + 0.3, 1.2, z1 - 1.0); scene.add(S.flashIn);
}

export function buildSet() { buildWoods(); buildCabin(); }
