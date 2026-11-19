// Environments for EP01. Each set: { group, env:{...}, update(t), ... }
import { THREE, RoundedBoxGeometry, std, glow, mesh, v3, rnd, reseed, canvasTex, redraw, roundRect, softTex, makePerson, clamp, smooth } from './lib.js';
import { makeGorrak, makeEmber, makeStorm, makeQuake, makeExtinction } from './monsters.js';

// ---------- shared builders ----------
function facade(base, frame, lit, litP = 0.16) {
  const mk = (draw) => canvasTex(256, 512, draw, { repeat: true });
  const wins = [];
  for (let y = 22; y < 500; y += 40) for (let x = 14; x < 246; x += 38) wins.push([x, y, rnd() < litP]);
  const map = mk((g) => { g.fillStyle = base; g.fillRect(0, 0, 256, 512);
    for (let y = 18; y < 500; y += 40) { g.fillStyle = frame; g.fillRect(0, y - 6, 256, 4); }
    for (const [x, y, on] of wins) { g.fillStyle = on ? lit : '#1a1a2e'; g.fillRect(x, y, 26, 24); g.fillStyle = 'rgba(255,255,255,0.12)'; g.fillRect(x, y, 26, 5); } });
  const em = mk((g) => { g.fillStyle = '#000'; g.fillRect(0, 0, 256, 512); for (const [x, y, on] of wins) if (on) { g.fillStyle = lit; g.fillRect(x, y, 26, 24); } });
  return { map, em };
}
const PAL = [['#3d5a80', '#2b405c'], ['#9c4f3c', '#73392b'], ['#5b3f73', '#432d55'], ['#c98a4b', '#9c6834'],
  ['#2f6f73', '#235356'], ['#8a3a52', '#682a3d'], ['#4a4e69', '#363a50'], ['#b5654a', '#8a4b36']];
const LITS = ['#ffd38a', '#ffe7b0', '#ffc070', '#bfe3ff'];
function buildingKit(litP = 0.16, emissive = 0.55) {
  const fac = []; for (let i = 0; i < 12; i++) fac.push(facade(PAL[i % PAL.length][0], PAL[i % PAL.length][1], LITS[i % 4], litP));
  return function building(parent, x, z, w, d, h) {
    const f = fac[Math.floor(rnd() * fac.length)];
    const map = f.map.clone(), em = f.em.clone();
    for (const t of [map, em]) { t.needsUpdate = true; t.repeat.set(Math.max(1, Math.round(w / 7)), Math.max(1, Math.round(h / 14))); }
    const b = mesh(new THREE.BoxGeometry(w, h, d), std(0xffffff, { map, emissiveMap: em, emissive: 0xffffff, emissiveIntensity: emissive, roughness: 0.75, metalness: 0.05 }));
    b.position.set(x, h / 2, z); parent.add(b);
    const cap = mesh(new THREE.BoxGeometry(w + 0.6, 0.8, d + 0.6), std(0x231b2c)); cap.position.set(x, h + 0.4, z); parent.add(cap);
    if (rnd() < 0.5) { const tank = mesh(new THREE.CylinderGeometry(1.1, 1.1, 2.2, 16), std(0x6b5a6e)); tank.position.set(x + (rnd() - 0.5) * w * 0.5, h + 1.9, z + (rnd() - 0.5) * d * 0.5); parent.add(tank); }
    if (rnd() < 0.3) { const ant = mesh(new THREE.CylinderGeometry(0.08, 0.12, 6, 6), std(0x333333)); ant.position.set(x, h + 3.8, z); parent.add(ant);
      const bl = new THREE.Mesh(new THREE.SphereGeometry(0.22, 8, 6), glow(4, 0.3, 0.2)); bl.position.set(x, h + 6.9, z); parent.add(bl); }
    return b;
  };
}
function asphalt() {
  return canvasTex(512, 2048, (g) => {
    g.fillStyle = '#2b2733'; g.fillRect(0, 0, 512, 2048);
    for (let i = 0; i < 9000; i++) { const v = 30 + rnd() * 30; g.fillStyle = `rgba(${v},${v - 4},${v + 6},0.5)`; g.fillRect(rnd() * 512, rnd() * 2048, 2, 2); }
    g.strokeStyle = 'rgba(15,12,20,0.8)'; g.lineWidth = 3;
    for (let i = 0; i < 26; i++) { g.beginPath(); let x = rnd() * 512, y = rnd() * 2048; g.moveTo(x, y); for (let k = 0; k < 6; k++) { x += (rnd() - 0.5) * 70; y += (rnd() - 0.5) * 70; g.lineTo(x, y); } g.stroke(); }
    g.fillStyle = '#f2c14e'; for (let y = 0; y < 2048; y += 96) g.fillRect(250, y, 12, 52);
    g.fillStyle = '#d9d4cc'; g.fillRect(14, 0, 8, 2048); g.fillRect(490, 0, 8, 2048);
  }, { repeat: true });
}
function streetLamp(parent, x, z, sx, bulb) {
  const g = new THREE.Group();
  const m = std(0x2c2834, { metalness: 0.6, roughness: 0.4 });
  const pole = mesh(new THREE.CylinderGeometry(0.12, 0.16, 7, 8), m); pole.position.y = 3.5; g.add(pole);
  const arm = mesh(new THREE.BoxGeometry(1.8, 0.12, 0.12), m); arm.position.set(-sx * 0.9, 7, 0); g.add(arm);
  const b = new THREE.Mesh(new THREE.SphereGeometry(0.22, 10, 8), bulb); b.position.set(-sx * 1.7, 6.85, 0); g.add(b);
  g.position.set(x, 0, z); parent.add(g); return g;
}
function car(parent, x, z, ry, col, flipped) {
  const g = new THREE.Group();
  const paint = std(col, { roughness: 0.25, metalness: 0.5 });
  const body = mesh(new THREE.BoxGeometry(2.2, 0.75, 4.4), paint); body.position.y = 0.75; g.add(body);
  const cab = mesh(new THREE.BoxGeometry(1.95, 0.7, 2.3), paint); cab.position.set(0, 1.45, -0.2); g.add(cab);
  const glass = mesh(new THREE.BoxGeometry(1.98, 0.5, 2.0), std(0x10131c, { roughness: 0.05, metalness: 0.9 })); glass.position.set(0, 1.5, -0.2); g.add(glass);
  for (const [wx, wz] of [[-1.05, 1.45], [1.05, 1.45], [-1.05, -1.45], [1.05, -1.45]]) { const wh = mesh(new THREE.CylinderGeometry(0.42, 0.42, 0.32, 18), std(0x141218, { roughness: 0.9 })); wh.rotation.z = Math.PI / 2; wh.position.set(wx, 0.42, wz); g.add(wh); }
  const tl = glow(4, 0.2, 0.15); for (const sx of [-0.75, 0.75]) { const l = new THREE.Mesh(new THREE.BoxGeometry(0.4, 0.15, 0.05), tl); l.position.set(sx, 0.85, 2.21); g.add(l); }
  g.position.set(x, 0, z); g.rotation.y = ry; if (flipped) { g.rotation.z = Math.PI * 0.94; g.position.y = 1.85; }
  parent.add(g); return g;
}
function billboard(parent, text, sub, color, x, y, z, ry, w = 9, h = 4.5) {
  const t = canvasTex(512, 256, (g) => { g.fillStyle = '#0d0a14'; g.fillRect(0, 0, 512, 256); g.fillStyle = color; g.font = '900 110px Inter, sans-serif'; g.textAlign = 'center'; g.fillText(text, 256, 145); g.fillStyle = '#fff'; g.font = '700 34px Inter, sans-serif'; g.fillText(sub, 256, 212); });
  const m = mesh(new THREE.PlaneGeometry(w, h), new THREE.MeshStandardMaterial({ map: t, emissiveMap: t, emissive: 0xffffff, emissiveIntensity: 1.5 }), false, false);
  m.position.set(x, y, z); m.rotation.y = ry; parent.add(m);
  const fr = mesh(new THREE.BoxGeometry(w + 0.4, h + 0.4, 0.3), std(0x1a1520)); fr.position.copy(m.position); fr.rotation.y = ry; fr.translateZ(-0.2); parent.add(fr);
  return m;
}
function fireFX(parent, x, z, size, fireTex, smokeTex, list, smokes) {
  const group = new THREE.Group(); group.position.set(x, 0, z); parent.add(group);
  const sprites = [];
  for (let i = 0; i < 7; i++) { const s = new THREE.Sprite(new THREE.SpriteMaterial({ map: fireTex, color: new THREE.Color(5, 1.6, 0.3), transparent: true, blending: THREE.AdditiveBlending, depthWrite: false })); group.add(s); sprites.push({ s, ph: rnd() * 6 }); }
  const light = new THREE.PointLight(0xff7a2a, 40 * size, 18 * size, 2); light.position.y = 1.5; group.add(light);
  list.push({ group, sprites, light, size });
  smokeColumn(parent, x, z, size * 1.4, 14, smokeTex, smokes);
}
function smokeColumn(parent, x, z, scale, count, smokeTex, smokes, color = 0x3b2a3c) {
  for (let i = 0; i < count; i++) { const s = new THREE.Sprite(new THREE.SpriteMaterial({ map: smokeTex, color, transparent: true, opacity: 0, depthWrite: false })); parent.add(s); smokes.push({ s, x, z, k: i / count, scale, sp: 0.5 + rnd() * 0.5, ph: rnd() * 10 }); }
}
function updateFX(t, fires, smokes) {
  for (const f of fires) { f.sprites.forEach((sp, i) => { const fl = 0.75 + 0.25 * Math.sin(t * 13 + sp.ph) + 0.15 * Math.sin(t * 29 + sp.ph * 2); sp.s.position.set(Math.sin(sp.ph + t * 3) * 0.4 * f.size, (0.6 + i * 0.35) * f.size, Math.cos(sp.ph) * 0.4 * f.size); sp.s.scale.setScalar((2.2 - i * 0.22) * f.size * fl); }); f.light.intensity = 40 * f.size * (0.8 + 0.2 * Math.sin(t * 17 + f.size)); }
  for (const s of smokes) { const k = (s.k + t * 0.05 * s.sp) % 1; s.s.position.set(s.x + Math.sin(s.ph + k * 4) * 1.5 * s.scale + k * 6 * s.scale, 1 + k * 20 * s.scale, s.z); s.s.scale.setScalar((2 + k * 9) * s.scale); s.s.material.opacity = Math.sin(k * Math.PI) * 0.55; s.s.material.rotation = s.ph + k * 1.5; }
}
function embersFX(parent, n, spread, color = [4, 1.6, 0.4]) {
  const geo = new THREE.BufferGeometry(), p = new Float32Array(n * 3), sd = [];
  for (let i = 0; i < n; i++) { p[i * 3] = (rnd() - 0.5) * spread[0]; p[i * 3 + 1] = rnd() * spread[1]; p[i * 3 + 2] = spread[2] - rnd() * spread[3]; sd.push(rnd()); }
  geo.setAttribute('position', new THREE.BufferAttribute(p, 3)); const p0 = p.slice();
  const pts = new THREE.Points(geo, new THREE.PointsMaterial({ color: new THREE.Color(...color), size: 0.14, transparent: true, opacity: 0.9, depthWrite: false, blending: THREE.AdditiveBlending }));
  parent.add(pts);
  return (t) => { for (let i = 0; i < n; i++) { const s = sd[i]; p[i * 3 + 1] = (p0[i * 3 + 1] + t * (1.2 + s * 2.2)) % spread[1]; p[i * 3] = p0[i * 3] + Math.sin(t * (0.8 + s) + s * 10) * 1.0; } geo.attributes.position.needsUpdate = true; };
}

// =====================================================================
// CITY at dusk (monster attack avenue)
// =====================================================================
export function buildCity() {
  reseed(11);
  const group = new THREE.Group();
  const building = buildingKit();
  const ground = mesh(new THREE.PlaneGeometry(1200, 1200), std(0x2a2230, { roughness: 0.95 }), false); ground.rotation.x = -Math.PI / 2; group.add(ground);
  const road = mesh(new THREE.PlaneGeometry(16, 320), std(0xffffff, { map: (() => { const t = asphalt(); t.repeat.set(1, 6); return t; })(), roughness: 0.85 }), false);
  road.rotation.x = -Math.PI / 2; road.position.set(0, 0.01, -110); group.add(road);
  for (const sx of [-1, 1]) {
    const curb = mesh(new THREE.BoxGeometry(0.4, 0.3, 320), std(0xbab0b8)); curb.position.set(sx * 8.2, 0.15, -110); group.add(curb);
    const walk = mesh(new THREE.BoxGeometry(5, 0.25, 320), std(0x7d6f80, { roughness: 0.9 })); walk.position.set(sx * 10.9, 0.125, -110); group.add(walk);
  }
  for (const sx of [-1, 1]) {
    let z = 30; while (z > -230) { const w = 8 + rnd() * 7, d = 8 + rnd() * 8, h = 16 + rnd() * 26 + (z < -40 ? rnd() * 40 : 0); building(group, sx * (14.2 + w / 2), z - d / 2, w, d, h); z -= d + 0.5 + rnd() * 1.5; }
    z = 20; while (z > -260) { const w = 10 + rnd() * 10, d = 10 + rnd() * 10, h = 30 + rnd() * 60; building(group, sx * (36 + w / 2 + rnd() * 6), z - d / 2, w, d, h); z -= d + 2 + rnd() * 4; }
  }
  for (let i = 0; i < 40; i++) { const w = 12 + rnd() * 18, h = 40 + rnd() * 90; const b = mesh(new THREE.BoxGeometry(w, h, 12), std(0x3a2240, { roughness: 1 }), false, false); b.position.set((rnd() - 0.5) * 400, h / 2, -280 - rnd() * 120); group.add(b); }
  billboard(group, 'WHAT IF?', 'NEW WORLD EVERY WEEK', '#ff3a2e', -14.0, 13, -22, Math.PI / 2);
  billboard(group, 'RAMEN 24', 'OPEN ALL NIGHT', '#3ad1ff', 14.0, 10, -40, -Math.PI / 2);
  billboard(group, 'HERO RANK', 'CHECK YOUR SCORE', '#ffd23a', -14.0, 18, -62, Math.PI / 2);
  const bulb = glow(5, 3.6, 2.0);
  for (let z = 22; z > -150; z -= 16) for (const sx of [-1, 1]) streetLamp(group, sx * 9.2, z, sx, bulb);
  car(group, -5.6, -6, 0.35, 0x2f7de1, false); car(group, 5.2, -14, -0.8, 0xf2b705, true); car(group, -4.4, -27, 1.3, 0x1fa36a, false);
  car(group, -6.4, 16, 0.1, 0xe8e6e1, false); car(group, 6.2, -44, -0.4, 0xc0262d, true); car(group, 4.5, 26, -0.2, 0x3b3b46, false);
  const smokeTex = softTex(0.35), fireTex = softTex(0.9); const fires = [], smokes = [];
  fireFX(group, 5.2, -14, 1.0, fireTex, smokeTex, fires, smokes); fireFX(group, 6.2, -44, 1.3, fireTex, smokeTex, fires, smokes); fireFX(group, -10, -60, 1.6, fireTex, smokeTex, fires, smokes);
  smokeColumn(group, -30, -95, 5, 20, smokeTex, smokes); smokeColumn(group, 28, -120, 6, 20, smokeTex, smokes); smokeColumn(group, -12, -150, 7, 18, smokeTex, smokes);
  const rubble = [];
  for (let i = 0; i < 70; i++) { const s = 0.2 + rnd() * 1.0; const r = mesh(new THREE.DodecahedronGeometry(s, 0), std(rnd() < 0.5 ? 0x6e6270 : 0x8b7a6c, { roughness: 0.95 })); r.position.set((rnd() - 0.5) * 15, s * 0.45, -4 - rnd() * 70); r.rotation.set(rnd() * 3, rnd() * 3, rnd() * 3); group.add(r); rubble.push(r); }
  // rooftop for the subscribe shot (left side, near camera)
  const roof = mesh(new THREE.BoxGeometry(12, 1, 12), std(0x3a3040, { roughness: 0.9 })); roof.position.set(-24, 44.5, 40); group.add(roof);
  const roofBody = mesh(new THREE.BoxGeometry(12, 44, 12), std(0x2b2433)); roofBody.position.set(-24, 22, 40); group.add(roofBody);
  const rail = mesh(new THREE.BoxGeometry(12, 0.6, 0.15), std(0x777777, { metalness: 0.7, roughness: 0.4 })); rail.position.set(-24, 45.3, 34.1); group.add(rail);
  // breach (crack + glow) at street level
  const breach = new THREE.Group(); breach.position.set(0, 0.03, -12); group.add(breach);
  const crackTex = canvasTex(512, 512, (g) => { g.clearRect(0, 0, 512, 512); g.strokeStyle = 'rgba(255,255,255,1)'; g.lineCap = 'round';
    for (let k = 0; k < 14; k++) { g.lineWidth = 10 - k * 0.5; g.beginPath(); let x = 256, y = 256; g.moveTo(x, y); const a = rnd() * Math.PI * 2; for (let s = 0; s < 8; s++) { x += Math.cos(a + (rnd() - 0.5)) * 30; y += Math.sin(a + (rnd() - 0.5)) * 30; g.lineTo(x, y); } g.stroke(); } });
  const crack = new THREE.Mesh(new THREE.PlaneGeometry(14, 14), new THREE.MeshBasicMaterial({ map: crackTex, color: new THREE.Color(1.6, 0.45, 2.6), transparent: true, blending: THREE.AdditiveBlending, depthWrite: false }));
  crack.rotation.x = -Math.PI / 2; breach.add(crack);
  const hole = mesh(new THREE.CircleGeometry(2.4, 32), glow(1.2, 0.3, 1.9), false); hole.rotation.x = -Math.PI / 2; hole.position.y = 0.02; breach.add(hole);
  const breachLight = new THREE.PointLight(0xb04cff, 0, 30, 2); breachLight.position.y = 2; breach.add(breachLight);
  const beamMat = new THREE.MeshBasicMaterial({ color: new THREE.Color(2.5, 0.8, 4), transparent: true, opacity: 0, blending: THREE.AdditiveBlending, depthWrite: false, side: THREE.DoubleSide });
  const beam = new THREE.Mesh(new THREE.CylinderGeometry(2.4, 3.5, 30, 32, 1, true), beamMat); beam.renderOrder = 2; beam.position.y = 15; breach.add(beam);
  const ember = makeEmber(); ember.group.position.set(0, 0, -12); group.add(ember.group);
  const gorrak = makeGorrak(); gorrak.group.scale.setScalar(1.35); gorrak.group.position.set(0, 0, -78); group.add(gorrak.group);
  const mKey = new THREE.SpotLight(0xffb08a, 3200, 220, 0.45, 0.5, 1.6); mKey.position.set(-35, 55, -20); group.add(mKey); group.add(mKey.target); mKey.target.position.set(0, 30, -78);
  const mRim = new THREE.SpotLight(0x7fb0ff, 2000, 220, 0.5, 0.6, 1.6); mRim.position.set(45, 40, -40); group.add(mRim); group.add(mRim.target); mRim.target.position.set(0, 30, -78);
  const updEmbers = embersFX(group, 700, [70, 40, 30, 120]);
  // lights
  const hemi = new THREE.HemisphereLight(0xffb48a, 0x2a1838, 0.55); group.add(hemi);
  const sun = new THREE.DirectionalLight(0xffa060, 4.2); sun.position.set(-70, 55, -25); sun.target.position.set(0, 0, -5); group.add(sun); group.add(sun.target);
  sun.castShadow = true; sun.shadow.mapSize.set(2048, 2048); sun.shadow.bias = -0.0004; sun.shadow.normalBias = 0.03;
  Object.assign(sun.shadow.camera, { left: -45, right: 45, top: 45, bottom: -45, near: 1, far: 260 });
  const fill = new THREE.DirectionalLight(0x8fb2ff, 1.6); fill.position.set(25, 18, 40); group.add(fill);
  return { group, gorrak, ember, breach, breachLight, beamMat, crack, hole, rubble, sun,
    env: { sky: 0, fog: 0xb4583f, fogD: 0.0055, exposure: 1.05, envI: 0.35, bloom: [0.55, 0.92] },
    update(t) { updateFX(t, fires, smokes); updEmbers(t); } };
}

// =====================================================================
// PLAZA: Bureau tower, giant screens, merch store (evening)
// =====================================================================
export function buildPlaza() {
  reseed(77);
  const group = new THREE.Group();
  const building = buildingKit(0.28, 0.7);
  const tiles = canvasTex(512, 512, (g) => { g.fillStyle = '#4a4552'; g.fillRect(0, 0, 512, 512); g.strokeStyle = '#38343f'; g.lineWidth = 4; for (let i = 0; i <= 512; i += 64) { g.beginPath(); g.moveTo(i, 0); g.lineTo(i, 512); g.stroke(); g.beginPath(); g.moveTo(0, i); g.lineTo(512, i); g.stroke(); } }, { repeat: true });
  tiles.repeat.set(40, 40);
  const ground = mesh(new THREE.PlaneGeometry(400, 400), std(0xffffff, { map: tiles, roughness: 0.35, metalness: 0.2 }), false); ground.rotation.x = -Math.PI / 2; group.add(ground);
  // Bureau tower
  const tower = new THREE.Group(); tower.position.set(0, 0, -60); group.add(tower);
  const goldGlass = std(0xd8a845, { roughness: 0.12, metalness: 0.95 });
  const ribTex = canvasTex(256, 1024, (g) => { g.fillStyle = '#000'; g.fillRect(0, 0, 256, 1024); g.fillStyle = '#ffd98a'; for (let y = 0; y < 1024; y += 32) g.fillRect(0, y, 256, 3); for (let x = 0; x < 256; x += 64) g.fillRect(x, 0, 3, 1024); }, { repeat: true });
  ribTex.repeat.set(4, 6);
  const shaft = mesh(new THREE.CylinderGeometry(13, 16, 140, 8), std(0xd8a845, { roughness: 0.15, metalness: 0.9, emissive: 0xffffff, emissiveMap: ribTex, emissiveIntensity: 0.9 })); shaft.position.y = 70; tower.add(shaft);
  const crown = mesh(new THREE.ConeGeometry(13, 26, 8), goldGlass); crown.position.y = 153; tower.add(crown);
  const spire = mesh(new THREE.CylinderGeometry(0.4, 0.8, 22, 8), goldGlass); spire.position.y = 176; tower.add(spire);
  const logoTex = canvasTex(512, 512, (g) => { g.clearRect(0, 0, 512, 512); g.fillStyle = '#fff3c4'; g.beginPath(); g.moveTo(256, 30); g.lineTo(470, 110); g.quadraticCurveTo(470, 360, 256, 490); g.quadraticCurveTo(42, 360, 42, 110); g.closePath(); g.fill();
    g.fillStyle = '#7a4b00'; g.font = '900 300px Inter, sans-serif'; g.textAlign = 'center'; g.fillText('B', 256, 370); });
  const logo = new THREE.Mesh(new THREE.PlaneGeometry(18, 18), new THREE.MeshBasicMaterial({ map: logoTex, transparent: true, color: new THREE.Color(2.2, 1.9, 1.3) })); logo.position.set(0, 118, 15.6); tower.add(logo);
  const towerLight = new THREE.SpotLight(0xffd27a, 9000, 300, 0.5, 0.6, 1.5); towerLight.position.set(0, 2, 40); towerLight.target.position.set(0, 90, -60); group.add(towerLight); group.add(towerLight.target);
  // giant screens (dynamic canvases)
  const screens = {};
  const mkScreen = (name, x, y, z, ry, w, h, draw) => {
    const tex = canvasTex(1024, Math.round(1024 * h / w), draw);
    const m = mesh(new THREE.PlaneGeometry(w, h), new THREE.MeshBasicMaterial({ map: tex, color: new THREE.Color(1.6, 1.6, 1.6) }), false, false);
    m.position.set(x, y, z); m.rotation.y = ry; group.add(m);
    const fr = mesh(new THREE.BoxGeometry(w + 0.8, h + 0.8, 0.5), std(0x15121a, { metalness: 0.6, roughness: 0.4 })); fr.position.copy(m.position); fr.rotation.y = ry; fr.translateZ(-0.3); group.add(fr);
    screens[name] = { mesh: m, tex }; return m;
  };
  const heroCard = (g, w, h, name, rank, score, color) => {
    const grd = g.createLinearGradient(0, 0, 0, h); grd.addColorStop(0, color); grd.addColorStop(1, '#0b0814'); g.fillStyle = grd; g.fillRect(0, 0, w, h);
    g.fillStyle = 'rgba(0,0,0,0.35)'; g.beginPath(); g.arc(w * 0.3, h * 0.55, h * 0.32, 0, Math.PI * 2); g.fill();
    g.fillStyle = 'rgba(255,255,255,0.9)'; g.beginPath(); g.arc(w * 0.3, h * 0.42, h * 0.13, 0, Math.PI * 2); g.fill(); g.fillRect(w * 0.3 - h * 0.18, h * 0.58, h * 0.36, h * 0.35);
    g.fillStyle = '#fff'; g.font = `900 ${h * 0.16}px Inter`; g.textAlign = 'left'; g.fillText(name, w * 0.55, h * 0.42);
    g.fillStyle = '#ffd23a'; g.font = `800 ${h * 0.09}px Inter`; g.fillText(rank, w * 0.55, h * 0.56);
    g.fillStyle = 'rgba(255,255,255,0.8)'; g.font = `700 ${h * 0.07}px Inter`; g.fillText(`SPARK ${score}`, w * 0.55, h * 0.68);
  };
  mkScreen('aurex', -24, 30, -20, Math.PI / 5, 30, 17, (g, w, h) => heroCard(g, w, h, 'AUREX', 'CROWN · #1', 998, '#b8860b'));
  mkScreen('vela', 26, 26, -24, -Math.PI / 5, 26, 15, (g, w, h) => heroCard(g, w, h, 'VELA STORM', 'CROWN · #3', 951, '#3557c9'));
  mkScreen('rank', 0, 12, -42, 0, 22, 12.5, (g, w, h) => drawRankList(g, w, h, 0));
  // surrounding buildings
  for (let i = 0; i < 26; i++) { const a = (i / 26) * Math.PI * 2; const r = 95 + rnd() * 40; const w = 14 + rnd() * 12, h = 40 + rnd() * 70; building(group, Math.cos(a) * r, Math.sin(a) * r - 40, w, w, h); }
  // merch store (right side, facing -x toward plaza center)
  const store = new THREE.Group(); store.position.set(30, 0, 18); store.rotation.y = -Math.PI / 2; group.add(store);
  const shell = mesh(new THREE.BoxGeometry(16, 9, 8), std(0x2b2236, { roughness: 0.8 })); shell.position.set(0, 4.5, -4.2); store.add(shell);
  const inner = mesh(new THREE.BoxGeometry(15, 7.6, 7.4), std(0xfff3e6, { roughness: 0.9, side: THREE.BackSide })); inner.position.set(0, 3.9, -3.9); store.add(inner);
  const sign = billboard(store, 'HERO SHOP', 'OFFICIAL BUREAU MERCH', '#ffd23a', 0, 8.4, 0.2, 0, 12, 2.2);
  const shelfM = std(0xffffff, { roughness: 0.5 });
  const figures = [];
  for (let row = 0; row < 3; row++) {
    const sh = mesh(new THREE.BoxGeometry(13, 0.15, 1.4), shelfM); sh.position.set(0, 1.6 + row * 1.9, -1.6); store.add(sh);
    for (let k = 0; k < 9; k++) {
      const gold = (k + row) % 3 === 0;
      const f = makePerson({ skin: [0xf0c8a0, 0xc98a5e, 0x8d5a3b][k % 3], shirt: [0x3a86ff, 0xef476f, 0x06d6a0, 0x8338ec][k % 4], pants: 0x222244, hairStyle: gold ? 'helmet' : 'short', gold, cape: gold ? 0xc0262d : (k % 4 === 1 ? 0x2244aa : undefined), scale: 0.26 });
      f.root.position.set(-5.8 + k * 1.45, 1.7 + row * 1.9, -1.4); store.add(f.root); figures.push(f);
      const box = mesh(new THREE.BoxGeometry(0.8, 0.9, 0.08), new THREE.MeshPhysicalMaterial({ color: 0xffffff, transmission: 0.9, roughness: 0.05, transparent: true, opacity: 0.25 }), false, false); box.position.set(-5.8 + k * 1.45, 2.15 + row * 1.9, -1.0); store.add(box);
    }
  }
  const canTex = canvasTex(256, 256, (g) => { const gr = g.createLinearGradient(0, 0, 256, 0); gr.addColorStop(0, '#0b0b0b'); gr.addColorStop(0.5, '#222'); gr.addColorStop(1, '#0b0b0b'); g.fillStyle = gr; g.fillRect(0, 0, 256, 256); g.fillStyle = '#ffd23a'; g.font = '900 64px Inter'; g.textAlign = 'center'; g.fillText('HERO', 128, 110); g.fillStyle = '#ff3a2e'; g.fillText('FUEL', 128, 180); });
  for (let k = 0; k < 14; k++) { const c = mesh(new THREE.CylinderGeometry(0.28, 0.28, 0.95, 20), std(0xffffff, { map: canTex, metalness: 0.7, roughness: 0.3 })); c.position.set(-6 + (k % 7) * 0.65, 0.55 + Math.floor(k / 7) * 0.0, 0.4 + Math.floor(k / 7) * 0.65); store.add(c); }
  const storeLight = new THREE.PointLight(0xfff0dd, 60, 18, 2); storeLight.position.set(0, 7, -2); store.add(storeLight);
  const glass = mesh(new THREE.PlaneGeometry(15, 7.4), new THREE.MeshPhysicalMaterial({ color: 0xffffff, roughness: 0.05, metalness: 0, transmission: 1, transparent: true, opacity: 0.12 }), false, false); glass.position.set(0, 3.9, 0.05); store.add(glass);
  // crowd
  const crowd = [];
  const cc = [0x3a86ff, 0xffbe0b, 0x06d6a0, 0xef476f, 0x8338ec, 0xfb8500, 0xffffff, 0x264653, 0xe76f51];
  for (let i = 0; i < 26; i++) {
    const p = makePerson({ skin: [0xf0c8a0, 0x8d5a3b, 0xe0ac7e, 0xb5764f, 0xf3d2b3, 0x9c6644][i % 6], shirt: cc[i % cc.length], pants: [0x2b2b2b, 0x3d405b, 0x1d3557][i % 3], hair: [0x111111, 0x6b4226, 0xd4a35a][i % 3], hairStyle: ['short', 'long', 'bun', 'short', 'cap'][i % 5], phone: true });
    p.root.position.set((rnd() - 0.5) * 34, 0, -8 + rnd() * 26); p.root.rotation.y = Math.PI + (rnd() - 0.5) * 0.8; group.add(p.root); crowd.push(p);
  }
  const hemi = new THREE.HemisphereLight(0x9fb4ff, 0x2a1838, 0.6); group.add(hemi);
  const moon = new THREE.DirectionalLight(0xa9b8ff, 1.4); moon.position.set(40, 80, 60); moon.castShadow = true; moon.shadow.mapSize.set(2048, 2048); Object.assign(moon.shadow.camera, { left: -60, right: 60, top: 60, bottom: -60, near: 1, far: 300 }); moon.shadow.bias = -0.0004; group.add(moon);
  const warm = new THREE.PointLight(0xffb36b, 400, 80, 2); warm.position.set(0, 10, 10); group.add(warm);
  return { group, screens, crowd, figures, tower, logo, store,
    env: { sky: 1.7, fog: 0x2a2140, fogD: 0.004, exposure: 1.1, envI: 0.4, bloom: [0.5, 0.92] },
    drawRankList: (scroll) => redraw(screens.rank.tex, (g, w, h) => drawRankList(g, w, h, scroll)),
    update() {} };
}
export function drawRankList(g, w, h, scroll) {
  g.fillStyle = '#0a0812'; g.fillRect(0, 0, w, h);
  g.fillStyle = '#ffd23a'; g.font = '900 48px Inter'; g.textAlign = 'left'; g.fillText('OFFICIAL HERO RANKINGS', 40, 70);
  g.fillStyle = 'rgba(255,255,255,0.15)'; g.fillRect(40, 92, w - 80, 3);
  const names = ['AUREX', 'KAIRA VOSS', 'VELA STORM', 'IRONCLAD', 'NOVA PRIME', 'DR. TEMPEST', 'BLAZE RUNNER', 'SILENT ARROW', 'MAGNETAR', 'COBALT'];
  const ranks = ['CROWN', 'CROWN', 'CROWN', 'CROWN', 'GOLD', 'GOLD', 'GOLD', 'SILVER', 'SILVER', 'SILVER'];
  const rowH = 54, top = 110;
  g.save(); g.beginPath(); g.rect(0, top, w, h - top); g.clip();
  const total = 4812;
  for (let r = 0; r < 14; r++) {
    // scroll 0 = top of list, 1 = bottom of list
    const idx = Math.floor(scroll * (total - 9)) + r;
    if (idx >= total) break;
    const y = top + 40 + r * rowH - ((scroll * (total - 9)) % 1) * rowH;
    const last = idx === total - 1;
    if (last) { g.fillStyle = 'rgba(255,58,46,0.35)'; g.fillRect(30, y - 38, w - 60, rowH - 6); }
    g.fillStyle = last ? '#ff6b5e' : '#fff'; g.font = `800 34px Inter`;
    g.fillText(`#${(idx + 1).toLocaleString('en-US')}`, 50, y);
    g.fillText(idx < 10 ? names[idx] : last ? 'THE ZERO' : ['HERO', 'CAPTAIN', 'AGENT', 'NIGHT', 'IRON'][idx % 5] + ' ' + ['FOX', 'BOLT', 'WAVE', 'STONE', 'LYNX', 'MOTH'][idx % 6] + ' ' + (idx % 97), 230, y);
    g.fillStyle = last ? '#ff6b5e' : (idx < 4 ? '#ffd23a' : idx < 7 ? '#ffd23a' : 'rgba(255,255,255,0.6)');
    g.textAlign = 'right'; g.fillText(idx < 10 ? ranks[idx] : last ? 'IRON · SPARK 0' : 'IRON', w - 50, y); g.textAlign = 'left';
  }
  g.restore();
}

// =====================================================================
// BUREAU CENTER interior (Scanner room)
// =====================================================================
export function buildBureauRoom() {
  reseed(5);
  const group = new THREE.Group();
  const floorTex = canvasTex(512, 512, (g) => { g.fillStyle = '#e9edf3'; g.fillRect(0, 0, 512, 512); g.strokeStyle = '#d3d9e2'; g.lineWidth = 3; for (let i = 0; i <= 512; i += 128) { g.beginPath(); g.moveTo(i, 0); g.lineTo(i, 512); g.stroke(); g.beginPath(); g.moveTo(0, i); g.lineTo(512, i); g.stroke(); } }, { repeat: true });
  floorTex.repeat.set(8, 8);
  const floor = mesh(new THREE.PlaneGeometry(40, 40), std(0xffffff, { map: floorTex, roughness: 0.18, metalness: 0.1 }), false); floor.rotation.x = -Math.PI / 2; group.add(floor);
  const wallM = std(0xc3ccd8, { roughness: 0.8 });
  const back = mesh(new THREE.PlaneGeometry(40, 12), wallM); back.position.set(0, 6, -10); group.add(back);
  const left = mesh(new THREE.PlaneGeometry(40, 12), wallM); left.position.set(-14, 6, 0); left.rotation.y = Math.PI / 2; group.add(left);
  const right = mesh(new THREE.PlaneGeometry(40, 12), wallM); right.position.set(14, 6, 0); right.rotation.y = -Math.PI / 2; group.add(right);
  const ceil = mesh(new THREE.PlaneGeometry(40, 40), std(0xf4f6f9), false); ceil.rotation.x = Math.PI / 2; ceil.position.y = 10; group.add(ceil);
  for (let x = -9; x <= 9; x += 6) for (let z = -6; z <= 10; z += 6) { const pnl = new THREE.Mesh(new THREE.PlaneGeometry(3.6, 1.2), glow(1.1, 1.15, 1.25)); pnl.rotation.x = Math.PI / 2; pnl.position.set(x, 9.98, z); group.add(pnl); }
  // accent stripe + logo on back wall
  const stripe = new THREE.Mesh(new THREE.PlaneGeometry(40, 0.25), glow(0.4, 1.4, 3.0)); stripe.position.set(0, 3.2, -9.98); group.add(stripe);
  const logoTex = canvasTex(1024, 256, (g) => { g.clearRect(0, 0, 1024, 256); g.fillStyle = '#d8a845'; g.beginPath(); g.moveTo(128, 20); g.lineTo(220, 54); g.quadraticCurveTo(220, 170, 128, 236); g.quadraticCurveTo(36, 170, 36, 54); g.closePath(); g.fill(); g.fillStyle = '#5a3a00'; g.font = '900 130px Inter'; g.textAlign = 'center'; g.fillText('B', 128, 175);
    g.fillStyle = '#2b3445'; g.font = '800 70px Inter'; g.textAlign = 'left'; g.fillText('BUREAU OF REGISTERED HEROES', 260, 110); g.fillStyle = '#6b778c'; g.font = '600 40px Inter'; g.fillText('SPARK SCANNING CENTER · MERIDIAN CITY', 262, 170); });
  const logo = new THREE.Mesh(new THREE.PlaneGeometry(14, 3.5), new THREE.MeshStandardMaterial({ map: logoTex, transparent: true, roughness: 0.6 })); logo.position.set(-2, 6.6, -9.95); group.add(logo);
  // SCANNER
  const scanner = new THREE.Group(); scanner.position.set(0, 0, -6); group.add(scanner);
  const base = mesh(new THREE.CylinderGeometry(1.6, 1.8, 0.4, 40), std(0x2b3445, { metalness: 0.7, roughness: 0.3 })); base.position.y = 0.2; scanner.add(base);
  const pillar = mesh(new RoundedBoxGeometry(1.6, 3.4, 1.0, 4, 0.2), std(0xf7f9fc, { metalness: 0.2, roughness: 0.25 })); pillar.position.y = 2.0; scanner.add(pillar);
  const panel = mesh(new RoundedBoxGeometry(1.25, 0.9, 0.12, 3, 0.05), std(0x10141c, { roughness: 0.15, metalness: 0.6 })); panel.position.set(0, 1.55, 0.55); panel.rotation.x = -0.45; scanner.add(panel);
  const handTex = canvasTex(256, 256, (g) => { g.clearRect(0, 0, 256, 256); g.strokeStyle = '#7fd8ff'; g.lineWidth = 7; g.beginPath();
    g.ellipse(128, 160, 52, 60, 0, 0, Math.PI * 2); g.stroke(); for (const [x, l, a] of [[78, 70, -0.3], [105, 95, -0.1], [130, 100, 0], [155, 92, 0.1], [188, 60, 0.6]]) { g.save(); g.translate(x, 115); g.rotate(a); g.strokeRect(-11, -l, 22, l); g.restore(); } });
  const handGlowMat = new THREE.MeshBasicMaterial({ map: handTex, color: new THREE.Color(1.5, 2.5, 3.5), transparent: true, depthWrite: false });
  const hand = new THREE.Mesh(new THREE.PlaneGeometry(0.75, 0.75), handGlowMat); hand.position.set(0, 1.58, 0.63); hand.rotation.x = -0.45; scanner.add(hand);
  // light bar (20 segments)
  const segs = [];
  for (let i = 0; i < 20; i++) { const s = new THREE.Mesh(new THREE.BoxGeometry(0.5, 0.05, 0.06), new THREE.MeshBasicMaterial({ color: new THREE.Color(0.15, 0.18, 0.22) })); s.position.set(0, 2.15 + i * 0.075, 0.51); scanner.add(s); segs.push(s); }
  // display above
  const dispTex = canvasTex(512, 256, (g) => drawScore(g, 512, 256, '---', '#7fd8ff'));
  const disp = mesh(new RoundedBoxGeometry(2.6, 1.3, 0.2, 3, 0.08), std(0x0b0e14, { metalness: 0.6, roughness: 0.3 })); disp.position.set(0, 4.6, 0.1); scanner.add(disp);
  const dispScreen = new THREE.Mesh(new THREE.PlaneGeometry(2.4, 1.1), new THREE.MeshBasicMaterial({ map: dispTex, color: new THREE.Color(1.1, 1.1, 1.1) })); dispScreen.position.set(0, 4.6, 0.21); scanner.add(dispScreen);
  const scanLight = new THREE.PointLight(0x7fd8ff, 10, 8, 2); scanLight.position.set(0, 2.5, 1.5); scanner.add(scanLight);
  // stanchions + queue
  for (let k = -1; k <= 1; k += 2) for (let z = 0; z < 4; z++) { const p = mesh(new THREE.CylinderGeometry(0.06, 0.06, 1.0, 10), std(0xc9a646, { metalness: 0.9, roughness: 0.25 })); p.position.set(k * 1.6, 0.5, -2 + z * 2.2); group.add(p); }
  for (let k = -1; k <= 1; k += 2) { const r = mesh(new THREE.BoxGeometry(0.05, 0.08, 6.6), std(0x8a1c2b, { roughness: 0.6 })); r.position.set(k * 1.6, 0.85, 1.3); group.add(r); }
  // technician desk
  const desk = mesh(new RoundedBoxGeometry(3, 1.0, 1.2, 3, 0.1), std(0xffffff, { roughness: 0.3 })); desk.position.set(4.2, 0.5, -5.2); group.add(desk);
  const mon = mesh(new THREE.BoxGeometry(1.2, 0.75, 0.06), std(0x111111)); mon.position.set(4.2, 1.45, -5.6); group.add(mon);
  const monScr = new THREE.Mesh(new THREE.PlaneGeometry(1.1, 0.65), glow(0.5, 1.2, 1.8)); monScr.position.set(4.2, 1.45, -5.565); group.add(monScr);
  // plants & chairs
  for (const x of [-12, 12]) { const pot = mesh(new THREE.CylinderGeometry(0.5, 0.4, 0.8, 16), std(0xffffff)); pot.position.set(x, 0.4, -8.5); group.add(pot); const leaves = mesh(new THREE.IcosahedronGeometry(0.9, 1), std(0x2f8f4e, { flatShading: true })); leaves.position.set(x, 1.4, -8.5); group.add(leaves); }
  for (let i = 0; i < 5; i++) { const ch = mesh(new RoundedBoxGeometry(1.0, 0.9, 1.0, 3, 0.15), std(0x3a6fd8, { roughness: 0.6 })); ch.position.set(-11, 0.45, -4 + i * 1.6); group.add(ch); }
  const hemi = new THREE.HemisphereLight(0xffffff, 0x9aa6b8, 0.5); group.add(hemi);
  const key = new THREE.DirectionalLight(0xffffff, 1.3); key.position.set(6, 9, 8); key.castShadow = true; key.shadow.mapSize.set(2048, 2048); Object.assign(key.shadow.camera, { left: -15, right: 15, top: 15, bottom: -15, near: 1, far: 40 }); key.shadow.bias = -0.0005; group.add(key);
  const fill = new THREE.PointLight(0xcfe6ff, 12, 25, 2); fill.position.set(-5, 7, 5); group.add(fill);
  const api = { group, scanner, segs, dispTex, scanLight, handGlowMat,
    env: { sky: -1, bg: 0xc9d2dd, fog: 0xc9d2dd, fogD: 0.002, exposure: 0.95, envI: 0.35, bloom: [0.18, 1.6] },
    setBar(level, color) { segs.forEach((s, i) => { const on = i < level; s.material.color.set(on ? color : new THREE.Color(0.15, 0.18, 0.22)); }); },
    setScore(text, color) { redraw(dispTex, (g, w, h) => drawScore(g, w, h, text, color)); },
    update() {} };
  return api;
}
function drawScore(g, w, h, text, color) {
  g.fillStyle = '#05070c'; g.fillRect(0, 0, w, h);
  g.fillStyle = 'rgba(127,216,255,0.6)'; g.font = '700 26px Inter'; g.textAlign = 'center'; g.fillText('SPARK SCORE', w / 2, 44);
  g.fillStyle = color; g.font = '900 150px Inter'; g.fillText(text, w / 2, 205);
}

// =====================================================================
// STUDIO: dark stage for infographics (monster lineup, rank badges, card, phone)
// =====================================================================
export function buildStudio() {
  reseed(21);
  const group = new THREE.Group();
  const floor = mesh(new THREE.PlaneGeometry(400, 400), std(0x0b0910, { roughness: 0.25, metalness: 0.6 }), false); floor.rotation.x = -Math.PI / 2; group.add(floor);
  const back = new THREE.Mesh(new THREE.SphereGeometry(300, 32, 16), new THREE.ShaderMaterial({ side: THREE.BackSide, depthWrite: false, uniforms: { tint: { value: new THREE.Color(0.18, 0.06, 0.25) } },
    vertexShader: `varying vec3 vP; void main(){ vP=normalize(position); gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0);} `,
    fragmentShader: `uniform vec3 tint; varying vec3 vP; void main(){ float h=vP.y; vec3 c=mix(tint*1.6, vec3(0.01,0.01,0.02), smoothstep(-0.05,0.6,h)); gl_FragColor=vec4(c,1.0);} ` }));
  group.add(back);
  const haze = embersFX(group, 400, [160, 60, 20, 80], [0.6, 0.5, 0.9]);
  // monster lineup along x
  const lineup = new THREE.Group(); group.add(lineup);
  const ember = makeEmber(); ember.group.position.set(-40, 0, 0); lineup.add(ember.group);
  const storm = makeStorm(); storm.group.position.set(-22, 0, 4); storm.group.rotation.y = 0.5; lineup.add(storm.group);
  const quake = makeQuake(); quake.group.position.set(5, 0, -6); quake.group.scale.setScalar(0.9); lineup.add(quake.group);
  const gorrak = makeGorrak(); gorrak.group.position.set(48, 0, -20); gorrak.group.scale.setScalar(1.0); lineup.add(gorrak.group);
  const ext = makeExtinction(); ext.group.position.set(125, 0, -80); lineup.add(ext.group);
  const extFogTex = softTex(0.5);
  const extFog = [];
  for (let i = 0; i < 26; i++) { const s = new THREE.Sprite(new THREE.SpriteMaterial({ map: extFogTex, color: 0x2a1030, transparent: true, opacity: 0.55, depthWrite: false })); s.position.set(125 + (rnd() - 0.5) * 120, rnd() * 50, -40 + rnd() * 30); s.scale.setScalar(40 + rnd() * 40); lineup.add(s); extFog.push(s); }
  const spots = [];
  const spotAt = (x, z, y, color, target) => {
    const s = new THREE.SpotLight(color, 0, 160, 0.42, 0.55, 1.4); s.position.set(x, y, z + 20); s.target.position.copy(target); group.add(s); group.add(s.target); s.castShadow = false;
    const coneMat = new THREE.MeshBasicMaterial({ color: new THREE.Color(color).multiplyScalar(0.25), transparent: true, opacity: 0, blending: THREE.AdditiveBlending, depthWrite: false, side: THREE.DoubleSide });
    const h = y; const cone = new THREE.Mesh(new THREE.ConeGeometry(Math.tan(0.42) * h * 0.9, h, 32, 1, true), coneMat);
    cone.position.copy(s.position).lerp(target, 0.5); cone.lookAt(s.position); cone.rotateX(Math.PI / 2); group.add(cone);
    spots.push({ s, coneMat }); return spots.length - 1;
  };
  spotAt(-40, 0, 14, 0xff8a3d, v3(-40, 0, 0));
  spotAt(-22, 4, 22, 0x4fd8ff, v3(-22, 2, 4));
  spotAt(5, -6, 40, 0xff6a2a, v3(5, 8, -6));
  spotAt(48, -20, 70, 0xb47cff, v3(48, 20, -20));
  spotAt(125, -80, 120, 0xff2a2a, v3(125, 30, -80));
  // rank badges
  const badges = new THREE.Group(); badges.position.set(0, 0, 200); group.add(badges);
  const metal = [[0x6d7178, 0.55], [0xb06a3a, 0.35], [0xc8ced8, 0.2], [0xe8b23a, 0.18], [0xf5d36b, 0.12]];
  const names = ['IRON', 'BRONZE', 'SILVER', 'GOLD', 'CROWN'];
  const badgeObjs = [];
  metal.forEach(([col, rough], i) => {
    const b = new THREE.Group();
    const shield = new THREE.Shape(); shield.moveTo(0, 1.2); shield.lineTo(1.0, 0.85); shield.quadraticCurveTo(1.0, -0.6, 0, -1.25); shield.quadraticCurveTo(-1.0, -0.6, -1.0, 0.85); shield.closePath();
    const m = mesh(new THREE.ExtrudeGeometry(shield, { depth: 0.25, bevelEnabled: true, bevelSize: 0.08, bevelThickness: 0.08, bevelSegments: 4 }), std(col, { metalness: 0.95, roughness: rough }));
    m.position.z = -0.12; b.add(m);
    const inner = mesh(new THREE.ExtrudeGeometry(shield, { depth: 0.1, bevelEnabled: false }), std(0x14101c, { roughness: 0.4 })); inner.scale.setScalar(0.72); inner.position.z = 0.17; b.add(inner);
    const tex = canvasTex(256, 256, (g) => { g.clearRect(0, 0, 256, 256); g.fillStyle = '#' + new THREE.Color(col).getHexString(); g.font = '900 150px Inter'; g.textAlign = 'center'; g.fillText(['I', 'B', 'S', 'G', '♛'][i], 128, 185); });
    const glyph = new THREE.Mesh(new THREE.PlaneGeometry(1.2, 1.2), new THREE.MeshBasicMaterial({ map: tex, transparent: true, color: new THREE.Color(1.6, 1.6, 1.6) })); glyph.position.z = 0.28; b.add(glyph);
    if (i === 4) { for (let k = -2; k <= 2; k++) { const gem = new THREE.Mesh(new THREE.OctahedronGeometry(0.12), glow(3, 0.5, 0.6)); gem.position.set(k * 0.35, 1.25 + (2 - Math.abs(k)) * 0.12, 0.1); b.add(gem); } }
    b.position.set(-8 + i * 4, 3, 0); b.scale.setScalar(1 + i * 0.12); badges.add(b); badgeObjs.push(b);
  });
  const badgeLight = new THREE.SpotLight(0xffffff, 0, 60, 0.6, 0.6, 1.2); badgeLight.position.set(0, 14, 216); badgeLight.target.position.set(0, 3, 200); group.add(badgeLight); group.add(badgeLight.target);
  const badgeFill = new THREE.PointLight(0xffe1b0, 0, 40, 2); badgeFill.position.set(-6, 6, 210); group.add(badgeFill);
  // rank card
  const cardTex = canvasTex(1024, 640, (g, w, h) => drawCard(g, w, h, { name: 'THE ZERO', rank: 'IRON', num: '#4,812', score: '0' }));
  const card = new THREE.Group(); card.position.set(-150, 3, 150); group.add(card);
  const cardBody = mesh(new RoundedBoxGeometry(4.8, 3.0, 0.08, 4, 0.2), std(0x22252c, { metalness: 0.7, roughness: 0.25 })); card.add(cardBody);
  const cardFace = new THREE.Mesh(new THREE.PlaneGeometry(4.6, 2.86), new THREE.MeshStandardMaterial({ map: cardTex, roughness: 0.3, metalness: 0.3, emissiveMap: cardTex, emissive: 0xffffff, emissiveIntensity: 0.05 })); cardFace.position.z = 0.045; card.add(cardFace);
  const cardLight = new THREE.SpotLight(0xffffff, 0, 30, 0.5, 0.6, 1.2); cardLight.position.set(-153, 6, 158); cardLight.target.position.set(-150, 3, 150); group.add(cardLight); group.add(cardLight.target);
  const cardFill = new THREE.PointLight(0x7fa8ff, 0, 20, 2); cardFill.position.set(-146, 2, 154); group.add(cardFill);
  // phone
  const phone = new THREE.Group(); phone.position.set(150, 3, 150); group.add(phone);
  const pb = mesh(new RoundedBoxGeometry(2.0, 4.0, 0.22, 6, 0.28), std(0x111216, { metalness: 0.8, roughness: 0.25 })); phone.add(pb);
  const phoneTex = canvasTex(540, 1080, (g, w, h) => drawPost(g, w, h, 0));
  const ps = new THREE.Mesh(new THREE.PlaneGeometry(1.86, 3.72), new THREE.MeshBasicMaterial({ map: phoneTex, color: new THREE.Color(1.25, 1.25, 1.25) })); ps.position.z = 0.115; phone.add(ps);
  const phoneLight = new THREE.PointLight(0xb7c8ff, 0, 20, 2); phoneLight.position.set(152, 3, 154); group.add(phoneLight);
  const hemi = new THREE.HemisphereLight(0x8a7aa8, 0x050308, 0.25); group.add(hemi);
  return { group, lineup, ember, storm, quake, gorrak, ext, extFog, spots, badges, badgeObjs, names, badgeLight, badgeFill, card, cardTex, cardLight, cardFill, phone, phoneTex, phoneLight,
    env: { sky: -1, bg: 0x050308, fog: 0x0a0610, fogD: 0.004, exposure: 1.1, envI: 0.5, bloom: [0.5, 0.9] },
    setCard(o) { redraw(cardTex, (g, w, h) => drawCard(g, w, h, o)); },
    setPost(k) { redraw(phoneTex, (g, w, h) => drawPost(g, w, h, k)); },
    update(t) { haze(t); } };
}
function drawCard(g, w, h, o) {
  const grd = g.createLinearGradient(0, 0, w, h); grd.addColorStop(0, o.c1 || '#3a3f48'); grd.addColorStop(1, o.c2 || '#14161b'); g.fillStyle = grd; g.fillRect(0, 0, w, h);
  g.strokeStyle = 'rgba(255,255,255,0.08)'; for (let i = -h; i < w; i += 22) { g.beginPath(); g.moveTo(i, 0); g.lineTo(i + h, h); g.stroke(); }
  g.fillStyle = '#d8a845'; g.beginPath(); g.moveTo(80, 50); g.lineTo(150, 74); g.quadraticCurveTo(150, 160, 80, 205); g.quadraticCurveTo(10, 160, 10, 74); g.closePath(); g.fill();
  g.fillStyle = '#5a3a00'; g.font = '900 100px Inter'; g.textAlign = 'center'; g.fillText('B', 80, 165);
  g.textAlign = 'left'; g.fillStyle = 'rgba(255,255,255,0.7)'; g.font = '700 34px Inter'; g.fillText('BUREAU OF REGISTERED HEROES', 180, 95); g.fillText('OFFICIAL HERO LICENSE', 180, 140);
  // photo
  g.fillStyle = '#c94f45'; roundRect(g, 60, 260, 250, 300, 20); g.fill();
  g.fillStyle = '#c98a5e'; g.beginPath(); g.arc(185, 380, 70, 0, Math.PI * 2); g.fill();
  g.fillStyle = '#15111b'; g.beginPath(); g.arc(185, 360, 74, Math.PI, 0); g.fill(); for (let k = 0; k < 6; k++) { g.beginPath(); g.moveTo(120 + k * 26, 330); g.lineTo(130 + k * 26, 280); g.lineTo(142 + k * 26, 330); g.fill(); }
  g.fillStyle = '#0c0710'; g.fillRect(160, 375, 12, 22); g.fillRect(200, 375, 12, 22);
  g.fillStyle = '#e8262b'; roundRect(g, 95, 460, 180, 100, 30); g.fill();
  g.fillStyle = '#fff'; g.font = '900 70px Inter'; g.fillText(o.name, 360, 330);
  g.fillStyle = 'rgba(255,255,255,0.6)'; g.font = '700 34px Inter'; g.fillText('RANK', 360, 400); g.fillText('POSITION', 600, 400); g.fillText('SPARK SCORE', 360, 500);
  g.fillStyle = '#fff'; g.font = '900 52px Inter'; g.fillText(o.rank, 360, 450); g.fillText(o.num, 600, 450);
  g.fillStyle = o.scoreColor || '#ff5a4e'; g.font = '900 64px Inter'; g.fillText(o.score, 360, 570);
}
function drawPost(g, w, h, k) {
  g.fillStyle = '#0f1117'; g.fillRect(0, 0, w, h);
  g.fillStyle = '#1b1e27'; g.fillRect(0, 0, w, 120); g.fillStyle = '#fff'; g.font = '800 40px Inter'; g.textAlign = 'left'; g.fillText(['HeroTok', 'MeridianNews', 'HeroTok', 'Bureau App'][k % 4], 30, 80);
  if (k === 3) { // Bureau app alert
    g.fillStyle = '#ffd23a'; g.font = '900 44px Inter'; g.fillText('⚠ STORM-LEVEL', 40, 260); g.fillText('THREAT DETECTED', 40, 320);
    g.fillStyle = '#fff'; g.font = '700 36px Inter'; g.fillText('Central Station · Platform 6', 40, 400);
    g.fillStyle = '#1e2433'; roundRect(g, 30, 470, w - 60, 330, 30); g.fill();
    g.fillStyle = '#9fb3ff'; g.font = '700 32px Inter'; g.fillText('SILVER HERO DISPATCHED', 60, 540);
    g.fillStyle = '#fff'; g.font = '900 110px Inter'; g.fillText('9:00', 60, 680); g.fillStyle = 'rgba(255,255,255,0.6)'; g.font = '700 30px Inter'; g.fillText('ESTIMATED ARRIVAL (MIN)', 60, 740);
    return;
  }
  const posts = [
    { user: '@meridian_daily', title: 'THE ZERO KID', sub: 'Most powerless human ever scanned 😂', img: '0' },
    { user: 'Meridian News 24', title: 'BREAKING: SPARK SCORE 0', sub: '"In 20 years I never saw a real zero" — technician', img: '0' },
    { user: '@lol_heroes', title: 'zero kid trying to lift a cat 💀', sub: '2.4M likes · 98K comments', img: '😂' },
  ];
  const p = posts[k % 3];
  g.fillStyle = '#3a3f4f'; g.beginPath(); g.arc(70, 190, 40, 0, Math.PI * 2); g.fill();
  g.fillStyle = '#fff'; g.font = '700 32px Inter'; g.fillText(p.user, 125, 202);
  g.fillStyle = '#1d2230'; roundRect(g, 30, 260, w - 60, 480, 24); g.fill();
  g.fillStyle = p.img === '0' ? '#ff4b3e' : '#ffd23a'; g.font = '900 300px Inter'; g.textAlign = 'center'; g.fillText(p.img, w / 2, 620); g.textAlign = 'left';
  g.fillStyle = '#fff'; g.font = '900 46px Inter'; g.fillText(p.title, 34, 820);
  g.fillStyle = 'rgba(255,255,255,0.7)'; g.font = '600 28px Inter'; wrap(g, p.sub, 34, 870, w - 70, 36);
  g.fillStyle = '#ff4b6e'; g.font = '700 34px Inter'; g.fillText('♥ 1.2M   💬 84K   ↗ 310K', 34, 1010);
}
function wrap(g, text, x, y, maxW, lh) { const words = text.split(' '); let line = ''; for (const wd of words) { const t = line + wd + ' '; if (g.measureText(t).width > maxW && line) { g.fillText(line, x, y); line = wd + ' '; y += lh; } else line = t; } g.fillText(line, x, y); }

// =====================================================================
// NEIGHBORHOOD (daytime): shops, crosswalk, tree with cat, parking lot
// =====================================================================
export function buildNeighborhood() {
  reseed(33);
  const group = new THREE.Group();
  const grass = mesh(new THREE.PlaneGeometry(600, 600), std(0x6f8f4e, { roughness: 1 }), false); grass.rotation.x = -Math.PI / 2; grass.position.y = -0.02; group.add(grass);
  const roadTex = asphalt(); roadTex.repeat.set(1, 4);
  const road = mesh(new THREE.PlaneGeometry(14, 200), std(0xffffff, { map: roadTex, roughness: 0.85 }), false); road.rotation.x = -Math.PI / 2; road.position.set(0, 0.01, -40); group.add(road);
  for (let i = 0; i < 8; i++) { const st = mesh(new THREE.PlaneGeometry(1.2, 4), std(0xf2f0ea, { roughness: 0.8 }), false); st.rotation.x = -Math.PI / 2; st.rotation.z = Math.PI / 2; st.position.set(-5 + i * 1.45, 0.02, 0); st.scale.set(1, 1, 1); group.add(st); }
  for (const sx of [-1, 1]) { const walk = mesh(new THREE.BoxGeometry(6, 0.25, 200), std(0xc9c2b8, { roughness: 0.9 })); walk.position.set(sx * 10, 0.125, -40); group.add(walk); }
  const shopCols = ['#f4a261', '#e76f51', '#2a9d8f', '#e9c46a', '#8ab17d', '#d4a5a5', '#6d9dc5', '#f28482'];
  const awn = [0xd62828, 0x2a9d8f, 0xf77f00, 0x264653, 0x9b2226];
  for (const sx of [-1, 1]) {
    let z = 20;
    while (z > -120) {
      const w = 8 + rnd() * 4, h = 7 + rnd() * 6, d = 8;
      const col = shopCols[Math.floor(rnd() * shopCols.length)];
      const tex = canvasTex(256, 256, (g) => { g.fillStyle = col; g.fillRect(0, 0, 256, 256); g.fillStyle = 'rgba(0,0,0,0.12)'; for (let y = 0; y < 256; y += 16) g.fillRect(0, y, 256, 1);
        g.fillStyle = '#cfe8ff'; for (let x = 30; x < 230; x += 70) { g.fillRect(x, 40, 40, 50); } g.fillStyle = '#9cc9ef'; g.fillRect(20, 150, 216, 90); g.fillStyle = '#5b4636'; g.fillRect(170, 150, 50, 100); });
      const b = mesh(new THREE.BoxGeometry(w, h, d), std(0xffffff, { map: tex, roughness: 0.85 })); b.position.set(sx * (13 + d / 2), h / 2, z - w / 2); b.rotation.y = sx > 0 ? -Math.PI / 2 : Math.PI / 2; group.add(b);
      const aw = mesh(new THREE.BoxGeometry(w * 0.9, 0.15, 1.8), std(awn[Math.floor(rnd() * awn.length)], { roughness: 0.7 })); aw.position.set(sx * 12.2, 3.1, z - w / 2); aw.rotation.set(0, sx > 0 ? -Math.PI / 2 : Math.PI / 2, 0); aw.rotateX(0.25); group.add(aw);
      z -= w + 0.4;
    }
  }
  // trees
  const trees = [];
  const tree = (x, z, s = 1) => { const g = new THREE.Group(); g.position.set(x, 0, z); g.scale.setScalar(s); group.add(g);
    const tr = mesh(new THREE.CylinderGeometry(0.25, 0.35, 3.2, 10), std(0x6b4a2f)); tr.position.y = 1.6; g.add(tr);
    for (let i = 0; i < 4; i++) { const f = mesh(new THREE.IcosahedronGeometry(1.4 + rnd() * 0.5, 1), std([0x3f7d3a, 0x4f9a47, 0x5aa850][i % 3], { flatShading: true, roughness: 0.9 })); f.position.set((rnd() - 0.5) * 1.4, 3.6 + rnd() * 1.2, (rnd() - 0.5) * 1.4); g.add(f); }
    trees.push(g); return g; };
  for (let z = 14; z > -100; z -= 12) { tree(-8.6, z, 0.9); tree(8.6, z - 6, 0.9); }
  const catTree = tree(-8.6, -30, 1.15);
  const cat = new THREE.Group(); const catM = std(0xf08c2a, { roughness: 0.8 });
  const cb = mesh(new THREE.CapsuleGeometry(0.18, 0.35, 6, 12), catM); cb.rotation.z = Math.PI / 2; cat.add(cb);
  const ch = mesh(new THREE.SphereGeometry(0.17, 14, 10), catM); ch.position.set(0.32, 0.12, 0); cat.add(ch);
  for (const sz of [-0.08, 0.08]) { const ear = mesh(new THREE.ConeGeometry(0.06, 0.12, 6), catM); ear.position.set(0.34, 0.3, sz); cat.add(ear); }
  const ct = mesh(new THREE.CapsuleGeometry(0.04, 0.35, 4, 8), catM); ct.position.set(-0.4, 0.15, 0); ct.rotation.z = 0.8; cat.add(ct);
  for (const sz of [-0.06, 0.06]) { const e = new THREE.Mesh(new THREE.SphereGeometry(0.025, 8, 6), glow(0.1, 0.6, 0.1)); e.position.set(0.46, 0.15, sz); cat.add(e); }
  cat.position.set(-6.7, 3.9, -29.4); cat.scale.setScalar(1.5);
  const branch = mesh(new THREE.CylinderGeometry(0.08, 0.12, 2.2, 8), std(0x6b4a2f)); branch.position.set(-7.6, 3.15, -29.5); branch.rotation.set(0.4, 0, -1.1); group.add(branch); cat.rotation.y = -0.6; group.add(cat);
  // parking lot (right side, further down): cones + film crew
  const lot = new THREE.Group(); lot.position.set(0, 0, -158); group.add(lot);
  const lotFloor = mesh(new THREE.PlaneGeometry(30, 30), std(0x55525a, { roughness: 0.9 }), false); lotFloor.rotation.x = -Math.PI / 2; lotFloor.position.y = 0.02; lot.add(lotFloor);
  for (let i = 0; i < 6; i++) { const l = mesh(new THREE.PlaneGeometry(0.2, 5), std(0xffffff), false); l.rotation.x = -Math.PI / 2; l.position.set(-10 + i * 4, 0.03, 8); lot.add(l); }
  for (let i = 0; i < 8; i++) { const c = new THREE.Group(); const cone = mesh(new THREE.ConeGeometry(0.3, 0.8, 16), std(0xff6a00, { roughness: 0.5 })); cone.position.y = 0.4; c.add(cone); const band = mesh(new THREE.CylinderGeometry(0.17, 0.22, 0.12, 16), std(0xffffff)); band.position.y = 0.45; c.add(band); c.position.set(-12 + i * 3, 0, -2); lot.add(c); }
  const camRig = new THREE.Group(); camRig.position.set(4, 0, 3); lot.add(camRig);
  const tri = mesh(new THREE.CylinderGeometry(0.05, 0.05, 1.6, 6), std(0x222222)); tri.position.y = 0.8; camRig.add(tri);
  const camBody = mesh(new THREE.BoxGeometry(0.6, 0.45, 0.9), std(0x111111, { metalness: 0.6, roughness: 0.3 })); camBody.position.y = 1.75; camRig.add(camBody);
  const lens = mesh(new THREE.CylinderGeometry(0.15, 0.18, 0.4, 16), std(0x222222)); lens.rotation.x = Math.PI / 2; lens.position.set(0, 1.75, -0.6); camRig.add(lens);
  const softbox = mesh(new THREE.BoxGeometry(1.4, 1.0, 0.2), glow(3, 3, 3)); softbox.position.set(-3, 2.5, 4); softbox.rotation.y = 0.6; lot.add(softbox);
  const sbStand = mesh(new THREE.CylinderGeometry(0.04, 0.04, 2, 6), std(0x222222)); sbStand.position.set(-3, 1, 4); lot.add(sbStand);
  // lights (sunny afternoon)
  const hemi = new THREE.HemisphereLight(0xcfe4ff, 0x6f8f4e, 1.0); group.add(hemi);
  const sun = new THREE.DirectionalLight(0xfff1d6, 3.2); sun.position.set(30, 50, 25); sun.target.position.set(0, 0, -20); group.add(sun); group.add(sun.target);
  sun.castShadow = true; sun.shadow.mapSize.set(2048, 2048); sun.shadow.bias = -0.0004; sun.shadow.normalBias = 0.03; Object.assign(sun.shadow.camera, { left: -50, right: 50, top: 50, bottom: -50, near: 1, far: 200 });
  return { group, cat, catTree, lot, camRig, sun,
    env: { sky: 1, fog: 0xa9c4e6, fogD: 0.0022, exposure: 0.95, envI: 0.45, bloom: [0.15, 1.6] },
    update(t) { cat.rotation.z = Math.sin(t * 2) * 0.05; } };
}

// =====================================================================
// CENTRAL STATION interior
// =====================================================================
export function buildStation() {
  reseed(61);
  const group = new THREE.Group();
  const L = 90; // hall length along z (0 .. -L)
  const tileTex = canvasTex(512, 512, (g) => { g.fillStyle = '#cfc6b8'; g.fillRect(0, 0, 512, 512); for (let y = 0; y < 512; y += 64) for (let x = 0; x < 512; x += 64) { g.fillStyle = ((x + y) / 64) % 2 ? '#c4baa9' : '#d8cfc2'; g.fillRect(x + 2, y + 2, 60, 60); } }, { repeat: true });
  tileTex.repeat.set(4, 30);
  const platform = mesh(new THREE.BoxGeometry(16, 1.2, L), std(0xffffff, { map: tileTex, roughness: 0.3, metalness: 0.1 })); platform.position.set(-2, 0.6, -L / 2); group.add(platform);
  const edge = mesh(new THREE.BoxGeometry(0.6, 0.02, L), std(0xffd23a, { roughness: 0.5 })); edge.position.set(5.6, 1.21, -L / 2); group.add(edge);
  const pit = mesh(new THREE.PlaneGeometry(10, L), std(0x2a2522, { roughness: 1 }), false); pit.rotation.x = -Math.PI / 2; pit.position.set(11, 0, -L / 2); group.add(pit);
  for (const rx of [8.5, 13.5]) { const rail = mesh(new THREE.BoxGeometry(0.2, 0.25, L), std(0x9a9aa5, { metalness: 0.9, roughness: 0.3 })); rail.position.set(rx, 0.15, -L / 2); group.add(rail); }
  // train
  const train = new THREE.Group(); train.position.set(11, 0, -L / 2 - 8); group.add(train);
  const trBody = mesh(new RoundedBoxGeometry(4.2, 4.6, 60, 4, 0.6), std(0xe7ecf2, { metalness: 0.5, roughness: 0.35 })); trBody.position.y = 2.9; train.add(trBody);
  const trStripe = mesh(new THREE.BoxGeometry(4.25, 0.35, 60), std(0x1e6fd9)); trStripe.position.y = 2.0; train.add(trStripe);
  for (let z = -27; z < 28; z += 3) { const w = new THREE.Mesh(new THREE.PlaneGeometry(2.0, 1.3), glow(1.6, 1.5, 1.2)); w.position.set(-2.12, 3.6, z); w.rotation.y = -Math.PI / 2; train.add(w); }
  // walls / ceiling
  const wallTex = canvasTex(512, 256, (g) => { g.fillStyle = '#f1ece2'; g.fillRect(0, 0, 512, 256); g.fillStyle = '#1e6fd9'; g.fillRect(0, 150, 512, 22); for (let x = 0; x < 512; x += 32) for (let y = 0; y < 256; y += 16) { g.strokeStyle = 'rgba(0,0,0,0.05)'; g.strokeRect(x, y, 32, 16); } }, { repeat: true });
  wallTex.repeat.set(12, 2);
  const wall = mesh(new THREE.PlaneGeometry(L, 14), std(0xffffff, { map: wallTex, roughness: 0.6 })); wall.rotation.y = Math.PI / 2; wall.position.set(-10, 7, -L / 2); group.add(wall);
  const farWall = mesh(new THREE.PlaneGeometry(30, 14), std(0xffffff, { map: wallTex, roughness: 0.6 })); farWall.position.set(2, 7, -L); group.add(farWall);
  const vault = mesh(new THREE.CylinderGeometry(13, 13, L, 40, 1, true, -Math.PI / 2, Math.PI), std(0xe9e3d6, { roughness: 0.7, side: THREE.BackSide }));
  vault.rotation.x = Math.PI / 2; vault.rotation.z = Math.PI / 2; vault.position.set(2, 12, -L / 2); vault.scale.set(1, 1, 0.45); group.add(vault);
  const ribs = []; for (let z = -2; z > -L; z -= 8) { const r = mesh(new THREE.TorusGeometry(13, 0.25, 8, 40, Math.PI), std(0x6b5a4a, { metalness: 0.4, roughness: 0.5 })); r.position.set(2, 12, z); r.scale.set(1, 0.45, 1); group.add(r); ribs.push(r); }
  const skylights = []; for (let z = -6; z > -L; z -= 8) { const s = new THREE.Mesh(new THREE.PlaneGeometry(4, 5), glow(2.6, 2.7, 3.0)); s.rotation.x = Math.PI / 2; s.position.set(2, 17.7, z); group.add(s); skylights.push(s); }
  // columns
  const colM = std(0x7a6a5a, { roughness: 0.5, metalness: 0.3 });
  const columns = [];
  for (let z = -6; z > -L; z -= 12) { const c = mesh(new THREE.CylinderGeometry(0.55, 0.65, 12, 20), colM); c.position.set(1.5, 6.6, z); group.add(c); columns.push(c); const cap = mesh(new THREE.BoxGeometry(1.6, 0.4, 1.6), colM); cap.position.set(1.5, 12.4, z); group.add(cap); }
  // benches & signs
  for (let z = -10; z > -L; z -= 12) { const b = mesh(new RoundedBoxGeometry(3, 0.25, 0.9, 2, 0.08), std(0x8a5a33, { roughness: 0.6 })); b.position.set(-6.5, 1.75, z); group.add(b); const leg = mesh(new THREE.BoxGeometry(2.6, 0.5, 0.2), std(0x333333)); leg.position.set(-6.5, 1.45, z); group.add(leg); }
  const sign = billboard(group, 'PLATFORM 6', 'CENTRAL STATION · MERIDIAN', '#ffd23a', 1.5, 9.5, -18.6, 0, 6, 2.4);
  const board = billboard(group, '17:42', 'NORTH LINE · ON TIME', '#3ad1ff', -9.8, 6.5, -30, Math.PI / 2, 6, 2.6);
  // stairs at far end
  for (let i = 0; i < 12; i++) { const st = mesh(new THREE.BoxGeometry(8, 0.35, 0.8), std(0xbdb3a4, { roughness: 0.6 })); st.position.set(-5, 1.2 + i * 0.35, -L + 2 + i * 0.8 - 12); group.add(st); }
  // breach in the floor (explosion point)
  const hole = new THREE.Group(); hole.position.set(-1, 1.21, -24); group.add(hole);
  const crackTex = canvasTex(512, 512, (g) => { g.strokeStyle = '#fff'; g.lineCap = 'round'; for (let k = 0; k < 16; k++) { g.lineWidth = 9 - k * 0.4; g.beginPath(); let x = 256, y = 256; g.moveTo(x, y); const a = rnd() * Math.PI * 2; for (let s = 0; s < 8; s++) { x += Math.cos(a + (rnd() - 0.5)) * 30; y += Math.sin(a + (rnd() - 0.5)) * 30; g.lineTo(x, y); } g.stroke(); } });
  const crackMat = new THREE.MeshBasicMaterial({ map: crackTex, color: new THREE.Color(4, 1.5, 0.4), transparent: true, opacity: 0, blending: THREE.AdditiveBlending, depthWrite: false });
  const crack = new THREE.Mesh(new THREE.PlaneGeometry(12, 12), crackMat); crack.rotation.x = -Math.PI / 2; crack.position.y = 0.02; hole.add(crack);
  const pitHole = mesh(new THREE.CircleGeometry(3.2, 30), std(0x0a0605), false); pitHole.rotation.x = -Math.PI / 2; pitHole.position.y = 0.025; pitHole.scale.setScalar(0.001); hole.add(pitHole);
  const debris = [];
  for (let i = 0; i < 40; i++) { const s = 0.15 + rnd() * 0.5; const d = mesh(new THREE.BoxGeometry(s, s * 0.4, s), std(rnd() < 0.5 ? 0xd8cfc2 : 0xc4baa9, { roughness: 0.6 })); d.visible = false; group.add(d); debris.push({ m: d, v: v3((rnd() - 0.5) * 12, 6 + rnd() * 10, (rnd() - 0.5) * 12), r: v3(rnd() * 9, rnd() * 9, rnd() * 9) }); }
  const smokeTex = softTex(0.4);
  const dust = [];
  for (let i = 0; i < 26; i++) { const s = new THREE.Sprite(new THREE.SpriteMaterial({ map: smokeTex, color: 0xbfb2a2, transparent: true, opacity: 0, depthWrite: false })); group.add(s); dust.push({ s, a: rnd() * Math.PI * 2, r: rnd(), k: rnd() }); }
  const storm = makeStorm(); storm.group.position.set(-1, 1.2, -24); group.add(storm.group); storm.group.visible = false;
  // lights
  const hemi = new THREE.HemisphereLight(0xfff3dc, 0x6b5a4a, 0.7); group.add(hemi);
  const key = new THREE.DirectionalLight(0xfff0d8, 1.8); key.position.set(-8, 30, 10); key.target.position.set(0, 0, -25); group.add(key); group.add(key.target);
  key.castShadow = true; key.shadow.mapSize.set(2048, 2048); key.shadow.bias = -0.0004; Object.assign(key.shadow.camera, { left: -30, right: 30, top: 40, bottom: -40, near: 1, far: 80 });
  const lamps = []; for (let z = -6; z > -L; z -= 16) { const l = new THREE.PointLight(0xffe2b0, 40, 22, 2); l.position.set(-2, 10, z); group.add(l); lamps.push(l); }
  const alarms = []; for (let z = -8; z > -60; z -= 16) { const a = new THREE.PointLight(0xff2020, 0, 26, 2); a.position.set(-9, 9, z); group.add(a); const bulb = new THREE.Mesh(new THREE.SphereGeometry(0.3, 12, 8), new THREE.MeshBasicMaterial({ color: new THREE.Color(0.3, 0.05, 0.05) })); bulb.position.set(-9.7, 9, z); group.add(bulb); alarms.push({ a, bulb }); }
  const holeLight = new THREE.PointLight(0xff7a2a, 0, 25, 2); holeLight.position.set(-1, 2, -24); group.add(holeLight);
  return { group, storm, hole, crackMat, pitHole, debris, dust, alarms, holeLight, lamps, columns, train,
    env: { sky: -1, bg: 0x2a241f, fog: 0x8a7d6c, fogD: 0.012, exposure: 1.05, envI: 0.45, bloom: [0.35, 1.1] },
    setAlarm(t, on) { alarms.forEach(({ a, bulb }, i) => { const v = on * (0.5 + 0.5 * Math.sin(t * 9 + i)); a.intensity = 120 * v; bulb.material.color.setRGB(0.3 + 5 * v, 0.05 + 0.3 * v, 0.05 + 0.2 * v); }); },
    update() {} };
}
