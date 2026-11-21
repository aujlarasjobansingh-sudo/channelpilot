// Set: 1986 small-town road at night — houses, streetlights that pop, pine woods behind a chain-link fence,
// a power plant on the horizon, the BMX, the walkie-talkie, the red rift and the thing that steps out of it.
import { THREE, scene, M, noOutline, add, box, cyl, sph, capsule, orient, canvasTex, texPlane, glowSprite, glowTex, glowMat, rnd, F } from './core.js';
import { mergeGeometries } from 'three/addons/utils/BufferGeometryUtils.js';

const V = (x, y, z) => new THREE.Vector3(x, y, z);
export const FENCE_X = -6.5, HOLE_Z = -83.0, RIFT = V(-15.0, 0, -90.0);
export const LAMP_Z = [-10, -30, -50, -70, -90, -110, -130, -150];
const noFog = m => { m.fog = false; return m; };

export const lamps = [], plantLights = [], windows = [];
export let sky, moon, headlight, bike, walkie, fenceHolePanel, woodsGlow, woodsLight, rift, creature, ash, ashBase;

function sprite(color, size, parent, fog = false) { const s = glowSprite(color, size, parent); s.material.fog = fog; return s; }
function pool(color, r, x, z, op) {
  const m = add(new THREE.Mesh(new THREE.PlaneGeometry(r * 2, r * 2), noOutline(new THREE.MeshBasicMaterial({ map: glowTex, color, transparent: true, opacity: op, blending: THREE.AdditiveBlending, depthWrite: false }))));
  m.rotation.x = -Math.PI / 2; m.position.set(x, 0.02, z); return m;
}

export function buildSet() {
  scene.fog = new THREE.Fog('#0b1222', 18, 150);
  // sky dome (vertical gradient) + moon + stars
  const skyTex = canvasTex(8, 512, (g, w, h) => {
    const gr = g.createLinearGradient(0, 0, 0, h); gr.addColorStop(0, '#050816'); gr.addColorStop(0.42, '#0d1630'); gr.addColorStop(0.5, '#1a2442'); gr.addColorStop(0.56, '#0b1222'); gr.addColorStop(1, '#0b1222');
    g.fillStyle = gr; g.fillRect(0, 0, w, h);
  });
  sky = add(new THREE.Mesh(new THREE.SphereGeometry(300, 32, 16), noOutline(noFog(new THREE.MeshBasicMaterial({ map: skyTex, side: THREE.BackSide, depthWrite: false })))));
  const stars = new THREE.BufferGeometry(), sp = [];
  for (let i = 0; i < 500; i++) { const a = rnd() * Math.PI * 2, e = 0.12 + rnd() * 1.3; sp.push(Math.cos(a) * Math.cos(e) * 280, Math.sin(e) * 280, Math.sin(a) * Math.cos(e) * 280); }
  stars.setAttribute('position', new THREE.Float32BufferAttribute(sp, 3));
  add(new THREE.Points(stars, noFog(new THREE.PointsMaterial({ color: '#cfd8ff', size: 1.6, sizeAttenuation: false, transparent: true, opacity: 0.7 }))));
  moon = add(new THREE.Mesh(new THREE.CircleGeometry(9, 40), noOutline(noFog(new THREE.MeshBasicMaterial({ color: '#f3efdc' })))));
  moon.position.set(-90, 95, -230); moon.lookAt(0, 0, 0);
  const mh = sprite('#9fb3ff', 45); mh.position.copy(moon.position); mh.material.opacity = 0.18;

  // ground: grass, road, shoulders, dashed centre line
  const grass = add(new THREE.Mesh(new THREE.PlaneGeometry(400, 400), M('#18261f'))); grass.rotation.x = -Math.PI / 2; grass.position.z = -80;
  const road = box(6.2, 0.02, 400, '#2a2c33', 0, 0.01, -80); noOutline(road.material = road.material.clone());
  for (const s of [-1, 1]) box(0.12, 0.022, 400, '#8d8a7c', s * 2.95, 0.012, -80);
  for (let z = 10; z > -260; z -= 6) box(0.12, 0.024, 2.6, '#b59a3a', 0, 0.013, z);
  for (const s of [-1, 1]) { const sw = box(1.6, 0.06, 400, '#55565c', s * 4.0, 0.03, -80); }

  // houses (right side all the way, left side until the woods start)
  const hcol = ['#5b6b86', '#7b6a5a', '#5f7d6a', '#8a7a62', '#6c5f7d', '#7d6a6a'];
  const house = (x, z, side, i) => {
    const w = 7 + rnd() * 3, d = 6 + rnd() * 2, h = 3.0 + rnd() * 0.8, col = hcol[i % hcol.length];
    const g = new THREE.Group(); g.position.set(x, 0, z); scene.add(g);
    box(d, h, w, col, 0, h / 2, 0, g);
    const roof = cyl(d * 0.62, d * 0.62, w + 0.4, '#2e2a30', 0, h + d * 0.2, 0, g, 3); roof.rotation.x = Math.PI / 2; roof.rotation.y = 0; roof.scale.set(1, 1, 0.5); roof.rotation.z = Math.PI / 2 * (side > 0 ? 1 : -1) * 0 + Math.PI;
    const fx = -side * (d / 2 + 0.01);
    for (const [wz, wy, on] of [[-w * 0.28, h * 0.5, rnd() < 0.55], [w * 0.28, h * 0.5, rnd() < 0.4]]) {
      const win = box(0.04, 0.9, 1.1, on ? '#ffcf72' : '#1b2233', fx, wy, wz, g, { flat: true }); noOutline(win.material = win.material.clone());
      if (on) { win.material = noOutline(new THREE.MeshBasicMaterial({ color: '#ffcf72' })); const gl = sprite('#ffbf5a', 2.2, g, true); gl.position.set(fx - side * 0.1, wy, wz); gl.material.opacity = 0.22; windows.push({ win, gl, z: z + wz }); }
    }
    box(0.05, 1.9, 0.9, '#3b2a22', fx, 0.95, 0, g);
    const porch = sprite('#ffcf80', 1.2, g, true); porch.position.set(fx - side * 0.25, 2.2, 0.75); porch.material.opacity = i % 3 === 0 ? 0.7 : 0; if (i % 3 === 0) windows.push({ gl: porch, z, porch: true });
    box(0.12, 1.1, 0.12, '#3d3d42', fx - side * 3.0, 0.55, w * 0.42 + 0.3, g); box(0.25, 0.22, 0.45, '#2f5d9a', fx - side * 3.0, 1.15, w * 0.42 + 0.3, g);   // mailbox
  };
  let i = 0;
  for (let z = 6; z > -200; z -= 13 + rnd() * 3) house(14 + rnd() * 2, z, 1, i++);
  for (let z = 2; z > -36; z -= 14) house(-14 - rnd() * 2, z, -1, i++);

  // streetlights (right side, arm over the road), each with a sodium pool on the asphalt
  for (const z of LAMP_Z) {
    const g = new THREE.Group(); g.position.set(3.7, 0, z); scene.add(g);
    cyl(0.07, 0.09, 6.0, '#4a4d55', 0, 3.0, 0, g, 12);
    const arm = box(1.9, 0.08, 0.08, '#4a4d55', -0.95, 5.9, 0, g);
    const head = box(0.5, 0.14, 0.26, '#3a3d44', -1.85, 5.82, 0, g);
    const bulb = box(0.38, 0.04, 0.18, '#ffd59a', -1.85, 5.74, 0, g, { flat: true }); noOutline(bulb.material = bulb.material.clone());
    const glow = sprite('#ffb257', 2.6, g, true); glow.position.set(-1.85, 5.6, 0);
    const cone = add(new THREE.Mesh(new THREE.ConeGeometry(2.6, 5.6, 24, 1, true), glowMat('#ffb257', 0.05)), g); cone.position.set(-1.85, 2.85, 0);
    const pl = pool('#ffae4a', 4.2, 1.85, z, 0.4);
    lamps.push({ z, bulb, glow, cone, pool: pl });
  }

  // chain-link fence along the woods with a torn hole, posts, barbed wire, signs
  const linkTex = (hole) => canvasTex(hole ? 1024 : 256, hole ? 1024 : 256, (g, w, h) => {
    if (hole) g.scale(4, 4); g.clearRect(0, 0, 256, 256); g.strokeStyle = 'rgba(190,198,208,1)'; g.lineWidth = hole ? 0.9 : 3;
    for (let k = -8; k < 16; k++) { const sp = hole ? 11 : 32; for (let q = 0; q < (hole ? 3 : 1); q++) { const o = k * 32 + q * sp; g.beginPath(); g.moveTo(o, 0); g.lineTo(o + 256, 256); g.stroke(); g.beginPath(); g.moveTo(o, 256); g.lineTo(o + 256, 0); g.stroke(); } }
    if (hole) {   // torn opening at the bottom middle with curled ragged edges
      g.globalCompositeOperation = 'destination-out'; g.beginPath(); g.moveTo(54, 256);
      const pts = [[50, 190], [62, 150], [84, 118], [112, 102], [140, 98], [168, 110], [190, 134], [204, 170], [206, 220], [204, 256]];
      for (const [x, y] of pts) g.lineTo(x + Math.sin(x) * 4, y + Math.cos(y) * 4);
      g.closePath(); g.fill(); g.globalCompositeOperation = 'source-over';
      g.strokeStyle = 'rgba(150,156,165,1)'; g.lineWidth = 4; g.beginPath(); g.moveTo(54, 256); for (const [x, y] of pts) g.lineTo(x + Math.sin(x) * 4, y + Math.cos(y) * 4); g.stroke();
    }
  });
  const fmat = (tex, rep) => { tex.wrapS = THREE.RepeatWrapping; tex.repeat.set(rep, 1); tex.anisotropy = 4; const m = new THREE.MeshToonMaterial({ map: tex, color: '#c6ccd6', transparent: true, alphaTest: 0.35, side: THREE.DoubleSide }); return noOutline(m); };
  const FH = 2.4;
  const panel = (z0, z1, hole) => {
    const len = z0 - z1, m = add(new THREE.Mesh(new THREE.PlaneGeometry(len, FH), fmat(linkTex(hole), hole ? 1 : len / 1.0)));
    m.rotation.y = Math.PI / 2; m.position.set(FENCE_X, FH / 2, (z0 + z1) / 2); return m;
  };
  panel(-40, HOLE_Z + 1.25, false); fenceHolePanel = panel(HOLE_Z + 1.25, HOLE_Z - 1.25, true); panel(HOLE_Z - 1.25, -200, false);
  for (let z = -40; z > -200; z -= 2.5) if (Math.abs(z - HOLE_Z) > 1.3) cyl(0.04, 0.04, FH + 0.1, '#7d838c', FENCE_X, (FH + 0.1) / 2, z, null, 8);
  cyl(0.025, 0.025, 160, '#7d838c', FENCE_X, FH, -120, null, 8).rotation.x = Math.PI / 2;
  for (let k = 0; k < 3; k++) { const bw = cyl(0.006, 0.006, 160, '#8a8f98', FENCE_X + 0.12 + k * 0.1, FH + 0.12 + k * 0.12, -120, null, 4); bw.rotation.x = Math.PI / 2; }
  // curled-back flap of the torn wire at the hole
  const flap = add(new THREE.Mesh(new THREE.PlaneGeometry(0.7, 0.7), fmat(linkTex(false), 0.7))); flap.position.set(FENCE_X + 0.25, 0.3, HOLE_Z - 0.7); flap.rotation.set(0, Math.PI / 2 + 0.9, 0.2);
  const signTex = canvasTex(512, 380, (g, w, h) => {
    g.fillStyle = '#ecebe4'; g.fillRect(0, 0, w, h); g.fillStyle = '#c3221c'; g.fillRect(0, 0, w, 120);
    g.strokeStyle = '#1a1a1a'; g.lineWidth = 10; g.strokeRect(5, 5, w - 10, h - 10);
    g.textAlign = 'center'; g.fillStyle = '#fff'; g.font = F(900, 62); g.fillText('RESTRICTED', w / 2, 66); g.font = F(900, 40); g.fillText('AREA', w / 2, 108);
    g.fillStyle = '#111'; g.font = F(900, 46); g.fillText('GOVERNMENT', w / 2, 190); g.fillText('PROPERTY', w / 2, 240);
    g.font = F(800, 30); g.fillText('NO TRESPASSING', w / 2, 300); g.font = F(700, 22); g.fillStyle = '#444'; g.fillText('VIOLATORS WILL BE PROSECUTED', w / 2, 340);
    g.fillStyle = 'rgba(90,60,30,0.25)'; for (let k = 0; k < 40; k++) g.fillRect(Math.random() * w, Math.random() * h, 3 + Math.random() * 8, 2 + Math.random() * 6);
  });
  for (const z of [HOLE_Z - 2.6, -58]) { const s = texPlane(1.15, 0.85, signTex, FENCE_X + 0.05, 1.55, z, null, false); s.rotation.y = Math.PI / 2; }

  // pine woods (merged into a few meshes): dense behind the fence, a clearing at the rift
  const pineG = [], trunkG = [];
  const pine = (x, z, s) => {
    for (let k = 0; k < 3; k++) { const c = new THREE.ConeGeometry((1.5 - k * 0.38) * s, 2.6 * s, 7); c.translate(x, (1.6 + k * 1.45) * s, z); pineG.push(c); }
    const tr = new THREE.CylinderGeometry(0.12 * s, 0.16 * s, 1.4 * s, 6); tr.translate(x, 0.7 * s, z); trunkG.push(tr);
  };
  for (let z = -38; z > -200; z -= 1.6) for (let x = -8.6; x > -70; x -= 1.8 + rnd() * 2.2 + Math.max(0, (-x - 20) * 0.08)) {
    const px = x + (rnd() - 0.5) * 1.4, pz = z + (rnd() - 0.5) * 1.2;
    const dr = Math.hypot(px - RIFT.x, (pz - RIFT.z) * 0.8), dp = Math.hypot(px + 9.5, pz - HOLE_Z - 0.0);
    if (dr < 5.2 || (dp < 2.6) || (px > -12 && px < -8 && pz < HOLE_Z + 1 && pz > HOLE_Z - 5.5)) continue;
    if (rnd() < 0.35) continue;
    pine(px, pz, 1.0 + rnd() * 0.9);
  }
  for (let z = 0; z > -200; z -= 4) for (let x = 24; x < 70; x += 4 + rnd() * 5) if (rnd() < 0.5) pine(x + rnd() * 2, z + rnd() * 2, 1.2 + rnd() * 0.8);
  add(new THREE.Mesh(mergeGeometries(pineG), M('#173528')));
  add(new THREE.Mesh(mergeGeometries(trunkG), M('#2c2219')));
  // undergrowth bushes along the fence
  const bushG = [];
  for (let z = -40; z > -200; z -= 1.1) { if (Math.abs(z - HOLE_Z) < 1.6) continue; const b = new THREE.SphereGeometry(0.5 + rnd() * 0.4, 8, 6); b.scale(1.3, 0.7, 1); b.translate(FENCE_X - 0.8 - rnd() * 1.2, 0.25, z); bushG.push(b); }
  add(new THREE.Mesh(mergeGeometries(bushG), M('#1b3a2a')));

  // power plant on the right horizon: cooling tower, stacks with red aviation lights
  const plant = new THREE.Group(); plant.position.set(72, 0, -140); scene.add(plant);
  const prof = []; for (let k = 0; k <= 12; k++) { const y = k / 12; prof.push(new THREE.Vector2(9 - 4.2 * Math.sin(y * Math.PI * 0.85) + y * 1.2, y * 22)); }
  const tower = add(new THREE.Mesh(new THREE.LatheGeometry(prof, 28), M('#3a4152')), plant);
  const t2 = add(new THREE.Mesh(new THREE.LatheGeometry(prof, 28), M('#363c4c')), plant); t2.position.set(16, 0, -14); t2.scale.setScalar(0.85);
  box(20, 9, 12, '#2c313f', -14, 4.5, 6, plant);
  for (const [x, h] of [[-20, 30], [-12, 26]]) {
    cyl(0.9, 1.3, h, '#4a505e', x, h / 2, 2, plant, 12);
    const r = sprite('#ff2a2a', 4, plant); r.position.set(x, h + 0.8, 2); plantLights.push(r);
  }
  const tl = sprite('#ff2a2a', 4, plant); tl.position.set(0, 23, 0); plantLights.push(tl);
  for (let k = 0; k < 6; k++) { const w = sprite('#ffd38a', 1.4, plant, true); w.position.set(-22 + k * 3, 5, 12.2); w.material.opacity = 0.6; }

  // red glow deep in the woods (before the rift), and the light it throws
  woodsGlow = sprite('#ff2a1e', 11); woodsGlow.position.set(RIFT.x, 1.8, RIFT.z); woodsGlow.material.opacity = 0;
  woodsLight = new THREE.PointLight('#ff3020', 0, 0, 1.4); woodsLight.position.set(RIFT.x + 1.5, 1.8, RIFT.z + 1.0); scene.add(woodsLight);
  // the rift: a vertical tear of light
  const riftTex = canvasTex(256, 1024, (g, w, h) => {
    g.clearRect(0, 0, w, h);
    const pts = []; for (let k = 0; k <= 40; k++) { const y = k / 40; pts.push([w / 2 + Math.sin(y * 17) * 14 + Math.sin(y * 41) * 7, y * h, Math.sin(y * Math.PI) ** 0.7]); }
    for (const [lw, col] of [[150, 'rgba(255,30,20,0.18)'], [90, 'rgba(255,40,30,0.35)'], [44, 'rgba(255,90,70,0.8)'], [16, 'rgba(255,230,220,1)']]) {
      g.strokeStyle = col; g.lineCap = 'round'; g.lineJoin = 'round';
      for (let k = 0; k < 40; k++) { g.lineWidth = lw * pts[k][2] + 2; g.beginPath(); g.moveTo(pts[k][0], pts[k][1]); g.lineTo(pts[k + 1][0], pts[k + 1][1]); g.stroke(); }
    }
  });
  const rmat = noOutline(noFog(new THREE.SpriteMaterial({ map: riftTex, transparent: true, blending: THREE.AdditiveBlending, depthWrite: false })));
  const rs = new THREE.Sprite(rmat); rs.position.set(RIFT.x, 1.75, RIFT.z); scene.add(rs);
  const rg = sprite('#ff2a1e', 6); rg.position.set(RIFT.x, 1.6, RIFT.z + 0.1);
  const rp = pool('#ff3020', 4.5, RIFT.x + 1.5, RIFT.z + 1.2, 0);
  rift = { sprite: rs, glow: rg, pool: rp };

  // ash spores drifting in the red light
  const N = 700; ashBase = new Float32Array(N * 4);
  for (let k = 0; k < N; k++) { ashBase[k * 4] = -24 + rnd() * 20; ashBase[k * 4 + 1] = rnd() * 5; ashBase[k * 4 + 2] = -97 + rnd() * 24; ashBase[k * 4 + 3] = rnd() * 100; }
  const ag = new THREE.BufferGeometry(); ag.setAttribute('position', new THREE.Float32BufferAttribute(new Float32Array(N * 3), 3));
  ash = add(new THREE.Points(ag, noFog(new THREE.PointsMaterial({ map: glowTex, color: '#e8d2c8', size: 0.07, transparent: true, opacity: 0, depthWrite: false }))));

  buildBike(); buildWalkie(); buildCreature();
}

// ---------------------------------------------------------------- BMX (group origin under the rider, faces -z)
function buildBike() {
  const g = new THREE.Group(); scene.add(g);
  const chrome = '#c3c9d2', frame = '#2a6fd6';
  const bars = new THREE.Group(); bars.position.set(0, 0.93, -0.55); g.add(bars);
  const bar = cyl(0.014, 0.014, 0.66, chrome, 0, 0, 0, bars, 10); bar.rotation.z = Math.PI / 2;
  const cross = cyl(0.012, 0.012, 0.34, chrome, 0, 0.12, 0.0, bars, 10); cross.rotation.z = Math.PI / 2;
  const pad = cyl(0.034, 0.034, 0.26, '#d63a34', 0, 0.12, 0.0, bars, 14); pad.rotation.z = Math.PI / 2;
  for (const s of [-1, 1]) {
    const up = cyl(0.013, 0.013, 0.2, chrome, s * 0.17, 0.06, 0, bars, 10); up.rotation.z = s * 0.25;
    const grip = cyl(0.022, 0.022, 0.13, '#17171a', s * 0.29, 0, 0, bars, 12); grip.rotation.z = Math.PI / 2;
  }
  cyl(0.02, 0.02, 0.12, chrome, 0, -0.06, 0, bars, 10);                       // stem
  const fork = []; for (const s of [-1, 1]) { const f = cyl(0.014, 0.014, 0.72, chrome, s * 0.055, -0.4, -0.14, bars, 8); f.rotation.x = -0.35; fork.push(f); }
  const head = cyl(0.026, 0.026, 0.22, frame, 0, -0.16, 0.04, bars, 12); head.rotation.x = -0.3;
  const top = cyl(0.022, 0.022, 0.56, frame, 0, 0.75, -0.2, g, 10); top.rotation.x = Math.PI / 2 - 0.12;
  const down = cyl(0.024, 0.024, 0.7, frame, 0, 0.5, -0.25, g, 10); down.rotation.x = Math.PI / 2 - 0.75;
  const wheel = new THREE.Group(); wheel.position.set(0, 0.27, -0.85); g.add(wheel);
  const tire = add(new THREE.Mesh(new THREE.TorusGeometry(0.25, 0.035, 10, 36), M('#18181b')), wheel); tire.rotation.y = Math.PI / 2;
  for (let k = 0; k < 6; k++) { const sp = cyl(0.004, 0.004, 0.46, chrome, 0, 0, 0, wheel, 4); sp.rotation.x = k * Math.PI / 6; }
  // number plate (faces forward) and headlight
  const plate = box(0.24, 0.18, 0.01, '#f2d23a', 0, 0.06, -0.05, bars);
  const lamp = new THREE.Group(); lamp.position.set(0, -0.08, -0.08); bars.add(lamp);
  const body = cyl(0.045, 0.04, 0.1, '#d9dde3', 0, 0, 0, lamp, 16); body.rotation.x = Math.PI / 2;
  const lensM = add(new THREE.Mesh(new THREE.CircleGeometry(0.04, 20), noOutline(new THREE.MeshBasicMaterial({ color: '#fff4cf' }))), lamp); lensM.position.z = -0.052; lensM.rotation.y = Math.PI;
  const lg = sprite('#fff1c2', 0.3, lamp); lg.position.z = -0.08;
  const beam = add(new THREE.Mesh(new THREE.ConeGeometry(1.4, 9, 24, 1, true), glowMat('#fff1c2', 0.05)), lamp); beam.rotation.x = Math.PI / 2; beam.position.z = -4.6;
  const pl = pool('#fff0c0', 1.8, 0, 0, 0.3);
  headlight = { lens: lensM, glow: lg, beam, pool: pl, lamp };
  bike = { g, bars, wheel, plate };
}

// ---------------------------------------------------------------- walkie-talkie (held in the right hand)
function buildWalkie() {
  const g = new THREE.Group(); scene.add(g);
  box(0.07, 0.16, 0.038, '#26272c', 0, 0, 0, g);
  const grille = canvasTex(64, 128, (c, w, h) => { c.fillStyle = '#1c1d21'; c.fillRect(0, 0, w, h); c.fillStyle = '#0d0d10'; for (let y = 10; y < 78; y += 9) c.fillRect(8, y, w - 16, 4); c.fillStyle = '#c9a43a'; c.fillRect(8, 92, w - 16, 22); c.fillStyle = '#111'; c.font = F(900, 14); c.textAlign = 'center'; c.fillText('CH 14', w / 2, 108); });
  const face = texPlane(0.06, 0.14, grille, 0, 0, 0.0195, g, false);
  const ant = cyl(0.006, 0.009, 0.13, '#141417', 0.022, 0.145, 0, g, 8);
  box(0.014, 0.014, 0.014, '#141417', 0.022, 0.082, 0, g);
  const knob = cyl(0.01, 0.01, 0.02, '#141417', -0.018, 0.09, 0, g, 10);
  const led = sph(0.0065, '#5a0c0c', -0.018, 0.074, 0.016, g, 10); noOutline(led.material = new THREE.MeshBasicMaterial({ color: '#5a0c0c' }));
  const ledGlow = sprite('#ff2a2a', 0.035, g); ledGlow.position.set(-0.018, 0.074, 0.03);
  box(0.008, 0.05, 0.02, '#141417', 0.039, 0.02, 0, g);   // push-to-talk
  walkie = { g, led, ledGlow };
}

// ---------------------------------------------------------------- the creature: tall, spindly, faceless
function buildCreature() {
  const skin = '#0d0809', g = new THREE.Group(); scene.add(g);
  const torso = new THREE.Group(); torso.position.y = 1.75; g.add(torso);
  const ch = capsule(0.13, 0.55, skin, torso); ch.scale.set(1.1, 1, 0.7); ch.position.y = 0.25;
  const pel = sph(0.12, skin, 0, -0.12, 0, torso); pel.scale.set(1.1, 0.8, 0.8);
  for (let k = 0; k < 4; k++) { const rib = add(new THREE.Mesh(new THREE.TorusGeometry(0.12, 0.012, 6, 16, Math.PI), M(skin)), torso); rib.position.set(0, 0.2 + k * 0.09, 0.02); rib.rotation.set(0, 0, Math.PI); }
  const neck = new THREE.Group(); neck.position.y = 0.62; torso.add(neck);
  cyl(0.035, 0.05, 0.3, skin, 0, 0.12, 0, neck, 8).rotation.x = 0.25;
  const head = new THREE.Group(); head.position.set(0, 0.32, 0.06); neck.add(head);
  const hd = sph(0.13, skin, 0, 0.1, 0, head); hd.scale.set(0.75, 1.55, 0.9);
  // the head splits into petals when it shrieks
  const petals = []; for (let k = 0; k < 4; k++) { const p = new THREE.Group(); p.position.set(0, 0.22, 0); head.add(p); const pm = capsule(0.04, 0.2, skin, p); pm.position.y = 0.08; p.rotation.y = k * Math.PI / 2; petals.push(p); }
  const maw = sph(0.06, '#ff3a26', 0, 0.24, 0, head, 12); noOutline(maw.material = noFog(new THREE.MeshBasicMaterial({ color: '#ff3a26' }))); maw.visible = false;
  const limb = (r, len) => { const G = new THREE.Group(); torso.add(G); const a = cyl(r, r * 0.8, len, skin, 0, -len / 2, 0, G, 8); const j = new THREE.Group(); j.position.y = -len; G.add(j); const b = cyl(r * 0.8, r * 0.45, len * 1.05, skin, 0, -len * 0.52, 0, j, 8); const h = new THREE.Group(); h.position.y = -len * 1.05; j.add(h); return { G, j, h }; };
  const arms = [-1, 1].map(s => { const L = limb(0.035, 0.72); L.G.position.set(s * 0.2, 0.55, 0); for (let f = 0; f < 4; f++) { const fg = cyl(0.008, 0.004, 0.28, skin, s * (f - 1.5) * 0.02, -0.13, 0, L.h, 5); fg.rotation.z = s * (f - 1.5) * 0.18; } return L; });
  const legs = [-1, 1].map(s => { const L = limb(0.05, 0.85); L.G.position.set(s * 0.1, -0.15, 0); return L; });
  g.scale.setScalar(1.25); creature = { g, torso, neck, head, arms, legs, petals, maw };
  g.visible = false;
}
