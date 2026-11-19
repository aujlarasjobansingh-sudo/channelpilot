// EP01 Part 1 timeline (0 - 310.5 s), synced to vo_part1.mp3 paragraph timings.
import { THREE, createEngine, makeSky, makePerson, resetPose, mouth, blink, gait, idle, wave, point, laugh, capeWave,
  clamp, smooth, lerp, v3, vlerp, easeOutBack, glow } from './lib.js';
import { buildCity, buildPlaza, buildBureauRoom, buildStudio, buildNeighborhood, buildStation } from './sets.js';

const stage = document.getElementById('stage');
const E = createEngine(stage);
const { scene, camera, grade, radial, renderer } = E;
const sky = makeSky(); scene.add(sky);

const S = { city: buildCity(), plaza: buildPlaza(), room: buildBureauRoom(), studio: buildStudio(), hood: buildNeighborhood(), station: buildStation() };
for (const k in S) { S[k].group.visible = false; scene.add(S[k].group); }

// ---------- cast ----------
const actors = [];
const A = (cfg) => { const p = makePerson(cfg); scene.add(p.root); actors.push(p); return p; };
const hero = A({ skin: 0xc98a5e, shirt: 0xd91f26, pants: 0x223064, shoe: 0xf4f1ea, hair: 0x15111b, hairStyle: 'spiky', emblem: true, band: true, vest: true, bag: true, phone: true });
const mom = A({ skin: 0xb9805a, shirt: 0x6a4c93, pants: 0x3a2e55, dress: 0x6a4c93, hair: 0x1d1410, hairStyle: 'long', shoe: 0x3a2a20 });
const tech = A({ skin: 0xf0c8a0, shirt: 0xffffff, pants: 0x2b3445, hair: 0x3b2314, hairStyle: 'short', coat: true, glasses: true, phone: true });
const teenA = A({ skin: 0xe0ac7e, shirt: 0x06d6a0, pants: 0x2b2b2b, hair: 0x2b1a10, hairStyle: 'short' });
const teenB = A({ skin: 0x8d5a3b, shirt: 0xffbe0b, pants: 0x3d405b, hair: 0x111111, hairStyle: 'long' });
const teenC = A({ skin: 0xf3d2b3, shirt: 0x8338ec, pants: 0x444444, hair: 0xd4a35a, hairStyle: 'short' });
const kid1 = A({ skin: 0xe0ac7e, shirt: 0x3a86ff, pants: 0x2b2b2b, hair: 0x2b1a10, hairStyle: 'cap', capColor: 0xff3a2e, scale: 0.68 });
const kid2 = A({ skin: 0x9c6644, shirt: 0xef476f, pants: 0x1d3557, hair: 0x111111, hairStyle: 'long', scale: 0.64 });
const kid3 = A({ skin: 0xf0c8a0, shirt: 0x06d6a0, pants: 0x444444, hair: 0x6b4226, hairStyle: 'short', scale: 0.66 });
const oldLady = A({ skin: 0xe8c3a0, shirt: 0x8a6fb3, pants: 0x5a4a7a, dress: 0x8a6fb3, hair: 0xd9d9d9, hairStyle: 'bun', cane: true, glasses: true });
const girl = A({ skin: 0xd9a27a, shirt: 0xffb3c6, pants: 0xff8fab, dress: 0xff8fab, hair: 0x3b2314, hairStyle: 'pigtails', scale: 0.6 });
const goldHero = A({ skin: 0xf0c8a0, hairStyle: 'helmet', gold: true, cape: 0xc0262d });
const cameraman = A({ skin: 0x8d5a3b, shirt: 0x333333, pants: 0x222222, hairStyle: 'cap', capColor: 0x111111 });
const shouter = A({ skin: 0xe0ac7e, shirt: 0x5a6270, pants: 0x2b2b2b, hair: 0x2b1a10, hairStyle: 'short' });
const crowd = [];
const crowdCols = [0x3a86ff, 0xffbe0b, 0x06d6a0, 0xef476f, 0x8338ec, 0xfb8500, 0xffffff, 0x264653, 0xe76f51, 0x2a9d8f];
for (let i = 0; i < 10; i++) crowd.push(A({ skin: [0xf0c8a0, 0x8d5a3b, 0xe0ac7e, 0xb5764f, 0xf3d2b3, 0x9c6644][i % 6], shirt: crowdCols[i], pants: [0x2b2b2b, 0x3d405b, 0x1d3557][i % 3], hair: [0x111111, 0x6b4226, 0xd4a35a, 0x2b1a10][i % 4], hairStyle: ['short', 'long', 'bun', 'short', 'cap'][i % 5] }));

// fist glow attached to hero's right hand
const glowTex = (() => { const c = document.createElement('canvas'); c.width = c.height = 128; const g = c.getContext('2d'); const gr = g.createRadialGradient(64, 64, 0, 64, 64, 64); gr.addColorStop(0, 'rgba(255,255,255,1)'); gr.addColorStop(0.25, 'rgba(255,230,170,0.8)'); gr.addColorStop(0.6, 'rgba(255,170,60,0.25)'); gr.addColorStop(1, 'rgba(255,140,40,0)'); g.fillStyle = gr; g.fillRect(0, 0, 128, 128); const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; return t; })();
const fistGlowMat = new THREE.SpriteMaterial({ map: glowTex, color: new THREE.Color(1.8, 1.4, 0.8), transparent: true, opacity: 0, blending: THREE.AdditiveBlending, depthWrite: false });
const fistGlow = new THREE.Sprite(fistGlowMat); hero.armR.elbow.add(fistGlow); fistGlow.position.y = -0.6;
const armGlow = new THREE.Sprite(fistGlowMat.clone()); hero.armR.elbow.add(armGlow); armGlow.position.y = -0.3;
const fistLight = new THREE.PointLight(0xffd88a, 0, 10, 2); scene.add(fistLight);

// ---------- helpers ----------
let cur = null;
function activate(name) {
  if (cur === name) return; cur = name;
  for (const k in S) S[k].group.visible = k === name;
  const e = S[name].env;
  sky.visible = e.sky >= 0; if (e.sky >= 0) sky.material.uniforms.mode.value = e.sky;
  scene.background = e.sky >= 0 ? null : new THREE.Color(e.bg);
  scene.fog = new THREE.FogExp2(e.fog, e.fogD);
  renderer.toneMappingExposure = e.exposure; scene.environmentIntensity = e.envI;
  E.bloom.strength = e.bloom[0]; E.bloom.threshold = e.bloom[1];
}
function cam(pos, look, fov = 40, roll = 0) { camera.position.copy(pos); camera.fov = fov; camera.updateProjectionMatrix(); camera.lookAt(look); if (roll) camera.rotateZ(roll); }
function show(p, x, y, z, ry = 0) { p.root.visible = true; p.root.position.set(x, y, z); p.root.rotation.set(0, ry, 0); return p; }
function shake(amt, t) { camera.position.x += Math.sin(t * 91) * amt; camera.position.y += Math.cos(t * 73) * amt * 0.8; }
const PI = Math.PI;
const chip = document.getElementById('chip'), chipName = document.getElementById('chipName'), chipLvl = document.getElementById('chipLvl'), chipLine = document.getElementById('chipLine');
const titleEl = document.getElementById('title'), titleMain = titleEl.querySelector('.main'), titleBar = titleEl.querySelector('.bar');
const black = document.getElementById('black');
function showChip(name, lvl, color, x, y, a) { chip.style.opacity = a; chip.style.left = x + 'px'; chip.style.top = y + 'px'; chipName.textContent = name; chipLvl.textContent = lvl; chipLine.style.background = color; chip.style.transform = `translate(-50%, ${(1 - a) * 12}px)`; }
function heroGlow(level, t) {
  fistGlowMat.opacity = Math.min(1, 1.2 * level); fistGlow.scale.setScalar(0.6 + level * 1.4 + Math.sin(t * 50) * 0.05 * level);
  armGlow.material.opacity = 0.6 * clamp(level - 0.4, 0, 1); armGlow.scale.set(0.5 + level * 0.5, 1.2 + level * 0.8, 1);
  const w = new THREE.Vector3(); hero.armR.fist.getWorldPosition(w); fistLight.position.copy(w); fistLight.intensity = 10 * level;
}

// ---------- city street helpers ----------
function cityCrowd(t, t0, zFrom, speed, xs) {
  crowd.forEach((p, i) => {
    if (i >= xs.length) return;
    const lt = t - t0 - i * 0.18; if (lt < -0.3) return;
    show(p, xs[i] + Math.sin(lt * 2 + i) * 0.3, 0, zFrom + Math.max(0, lt) * speed, 0);
    gait(p, t * 12 + i, 0.75, true); p.armR.shoulder.rotation.x -= 0.4; p.head.rotation.x = 0.1; mouth(p, 'o');
  });
}

// =====================================================================
// SHOTS: [start, end, set, fn(lt, k, t)]  (lt = local time, k = 0..1)
// =====================================================================
const shots = [];
const add = (t0, t1, set, fn) => shots.push({ t0, t1, set, fn });

// ---- HOOK (0 - 14.05) ----
add(0, 5.0, 'city', (lt, k, t) => { // aerial: monsters attack every week
  S.city.gorrak.animate(t, smooth(1.5, 2.2, lt) * (1 - smooth(3.6, 4.4, lt)));
  cam(v3(lerp(2.5, 1.2, k), lerp(46, 22, k), lerp(72, 40, k)), v3(0, lerp(22, 26, k), -80), 40);
  black.style.opacity = 1 - smooth(0, 0.8, lt);
});
add(5.0, 9.5, 'plaza', (lt, k, t) => { // heroes ranked like celebrities
  S.plaza.crowd.forEach((p, i) => { resetPose(p); p.root.visible = true; if (i % 3 === 0) { p.phone.visible = true; p.armR.shoulder.rotation.set(-2.3, 0, -0.2); p.armR.elbow.rotation.x = -0.6; } else if (i % 3 === 1) { p.armL.shoulder.rotation.z = 2.6 + Math.sin(t * 6 + i) * 0.2; } });
  cam(v3(lerp(-6, 4, k), lerp(4, 7, k), 26), v3(lerp(-14, 10, k), lerp(20, 24, k), -30), 42);
});
add(9.5, 14.05, 'room', (lt, k, t) => { // your number is zero
  const climb = smooth(0.2, 2.0, lt) * (1 - smooth(2.2, 3.0, lt));
  const n = Math.round(lerp(0, 760, climb));
  S.room.setScore(lt < 3.0 ? String(n) : '0', lt < 3.0 ? '#7fd8ff' : '#ff4b3e');
  S.room.setBar(Math.round(climb * 20), new THREE.Color(0.5, 2.5, 4));
  cam(v3(0.3, 4.6, lerp(-1.6, -2.6, k)), v3(0, 4.6, -5.9), 34);
});
// ---- 14.05 - 22.10: everyone calls you the weakest ----
add(14.05, 17.0, 'studio', (lt, k, t) => { // rank card
  S.studio.setCard({ name: 'THE ZERO', rank: 'IRON', num: '#4,812', score: '0' });
  S.studio.lineup.visible = false; S.studio.cardLight.intensity = 70; S.studio.cardFill.intensity = 8;
  S.studio.card.rotation.set(0.1 - 0.1 * k, lerp(-0.5, 0.15, k), 0.05);
  cam(v3(-150, 3.2, 156.5), v3(-150, 3, 150), 36);
});
add(17.0, 19.6, 'studio', (lt, k, t) => { // the news says it
  S.studio.setPost(1); S.studio.lineup.visible = false; S.studio.phoneLight.intensity = 12;
  S.studio.phone.rotation.set(-0.1, lerp(0.4, -0.15, k), 0.08);
  cam(v3(150, 3.0, 157.5), v3(150, 3, 150), 38);
});
add(19.6, 22.10, 'hood', (lt, k, t) => { // kids laugh
  for (const [p, x, off] of [[kid1, -1.2, 0], [kid2, 0, 0.7], [kid3, 1.2, 1.3]]) { show(p, x, 0.25, -6, PI * 0.95); resetPose(p); laugh(p, t + off, 1); }
  point(kid1, 'R', 0.1);
  show(hero, 0.5, 0.25, -14, 0); resetPose(hero); hero.vest.visible = true; hero.bag.visible = false; gait(hero, t * 6, 0.35, false);
  mouth(hero, 'flat'); hero.head.rotation.x = 0.15;
  cam(v3(lerp(3.5, 2.5, k), 1.6, lerp(-1.5, -2.5, k)), v3(0, 1.8, -10), 40);
});
// ---- 22.10 - 25.44: one thing nobody knows ----
add(22.10, 25.44, 'city', (lt, k, t) => {
  const hz = lerp(9.5, 7.0, k); show(hero, 0, 0, hz, PI); resetPose(hero); hero.vest.visible = false; hero.bag.visible = false; gait(hero, t * 7.2, 0.42, false);
  cityCrowd(t, 22.0, -22, 7, [-2.2, 2.4, -4.2, 4.6, -1.0, 1.4, -5.6]);
  S.city.gorrak.animate(t, 0.2);
  cam(v3(1.5, 1.3, hz + 5), v3(0, 9, hz - 40), 46);
});
// ---- 25.44 - 30.84: the strongest hero will find out ----
add(25.44, 28.4, 'city', (lt, k, t) => { // fist closes, glow leaks
  show(hero, 0, 0, 6, PI); resetPose(hero); hero.vest.visible = false; hero.bag.visible = false;
  hero.armR.shoulder.rotation.set(-0.35, 0, -0.1); hero.armR.elbow.rotation.x = -1.2;
  heroGlow(smooth(0.6, 2.6, lt) * 0.55, t);
  const f = new THREE.Vector3(); hero.armR.fist.getWorldPosition(f);
  cam(v3(f.x - 0.9, f.y + 0.2, f.z - 1.4 + 0.3 * k), f, 32);
});
add(28.4, 30.84, 'plaza', (lt, k, t) => { // Aurex billboard
  S.plaza.crowd.forEach((p) => { p.root.visible = false; });
  cam(v3(-8, lerp(10, 14, k), 6), v3(-24, 30, -20), lerp(30, 24, k));
  black.style.opacity = smooth(1.9, 2.4, lt);
});
// ---- 30.84 - 38.80: subscribe ----
add(30.84, 38.80, 'city', (lt, k, t) => {
  show(hero, -24, 45, 37, -0.25); resetPose(hero); hero.vest.visible = false; hero.bag.visible = false; idle(hero, t);
  if (lt > 2.2 && lt < 4.8) wave(hero, t, 'R'); mouth(hero, 'smile', 0.8); blink(hero, t);
  S.city.gorrak.animate(t, 0);
  const a = lerp(-0.5, 0.35, k);
  cam(v3(-24 + Math.sin(a) * 5.5, 47.6, 37 + Math.cos(a) * 5.5), v3(-24, 47.3, 37), 38);
  black.style.opacity = 1 - smooth(0, 0.5, lt);
});
// ---- 38.80 - 44.54: Now let's go -> TITLE -> monsters come out of the ground ----
add(38.80, 41.8, 'city', (lt, k, t) => { // title over aerial
  S.city.gorrak.animate(t, 0.3);
  cam(v3(0, lerp(70, 55, k), lerp(90, 70, k)), v3(0, 15, -60), 44);
  const ti = smooth(0.35, 1.0, lt) * (1 - smooth(2.5, 2.95, lt));
  titleEl.style.opacity = ti; titleMain.style.letterSpacing = `${lerp(0.5, 0.12, smooth(0.35, 1.0, lt))}em`; titleMain.style.filter = `blur(${(1 - smooth(0.35, 1.0, lt)) * 8}px)`;
  titleBar.style.width = `${smooth(0.6, 1.2, lt) * 420}px`;
  radial.enabled = lt < 0.4; radial.uniforms.strength.value = 0.25 * (1 - lt / 0.4);
});
add(41.8, 47.5, 'city', (lt, k, t) => { // ground cracks, breach opens
  S.city.gorrak.group.visible = false;
  const op = smooth(0.4, 2.5, lt);
  S.city.crack.material.opacity = op; S.city.crack.scale.setScalar(0.3 + 0.7 * op); S.city.hole.scale.setScalar(Math.max(0.001, smooth(1.5, 3.0, lt)));
  S.city.breachLight.intensity = 120 * op; S.city.beamMat.opacity = 0.12 * smooth(2.4, 3.2, lt);
  S.city.ember.group.visible = false;
  cam(v3(lerp(4, 3, k), lerp(5.5, 4.5, k), 1), v3(0, 0.3, -12), 44); shake(0.06 * op, t);
});
// ---- 44.54 - 59.29: breach creatures; dog-size to building-size; threat level ----
add(47.5, 52.0, 'city', (lt, k, t) => { // ember crawls out
  S.city.gorrak.group.visible = false;
  S.city.crack.material.opacity = 1; S.city.hole.scale.setScalar(1); S.city.breachLight.intensity = 60; S.city.beamMat.opacity = 0.05;
  const e = S.city.ember; e.group.visible = true; e.group.position.set(0, 0, -12 + smooth(0.3, 4, lt) * 4.5); e.group.rotation.y = 0; e.animate(t, 1);
  e.group.position.y = -1.2 + smooth(0, 1.0, lt) * 1.2;
  const ep = e.group.position; cam(v3(ep.x + 2.0, 1.1, ep.z + 3.0), v3(ep.x, 0.5, ep.z), 38);
});
add(52.0, 55.6, 'city', (lt, k, t) => { // building-size: Gorrak towers
  S.city.gorrak.group.visible = true; S.city.ember.group.visible = false; S.city.crack.material.opacity = 0; S.city.hole.scale.setScalar(0.001); S.city.breachLight.intensity = 0; S.city.beamMat.opacity = 0;
  S.city.gorrak.animate(t, smooth(1.0, 1.6, lt));
  cam(v3(-6, 1.2, -20), v3(0, lerp(20, 32, k), -78), 50);
});
add(55.6, 59.29, 'studio', (lt, k, t) => { // five silhouettes
  S.studio.spots.forEach((s) => { s.s.intensity = 0; s.coneMat.opacity = 0; });
  S.studio.spots.forEach((s, i) => { s.s.intensity = 120 * smooth(0.4 + i * 0.4, 0.9 + i * 0.4, lt) * Math.pow(2.2, i); s.coneMat.opacity = 0.35 * smooth(0.4 + i * 0.4, 0.9 + i * 0.4, lt); });
  studioAnim(t);
  cam(v3(lerp(30, 40, k), 25, 120), v3(40, 18, -20), 44);
});
// ---- 59.29 - 82.22: the five levels ----
const lv = [
  { name: 'EMBER', lvl: 'THREAT LEVEL 1', color: '#ff8a3d', t0: 59.29, t1: 63.6, pos: v3(-37, 1.6, 7), look: v3(-40, 0.6, 0), fov: 36 },
  { name: 'STORM', lvl: 'THREAT LEVEL 2', color: '#4fd8ff', t0: 63.6, t1: 67.8, pos: v3(-14, 4, 18), look: v3(-22, 2.5, 3), fov: 40 },
  { name: 'QUAKE', lvl: 'THREAT LEVEL 3', color: '#ff6a2a', t0: 67.8, t1: 72.0, pos: v3(18, 6, 26), look: v3(5, 10, -6), fov: 44 },
  { name: 'ECLIPSE', lvl: 'THREAT LEVEL 4', color: '#b47cff', t0: 72.0, t1: 76.2, pos: v3(66, 6, 40), look: v3(48, 22, -20), fov: 46 },
  { name: 'EXTINCTION', lvl: 'THREAT LEVEL 5', color: '#ff2a2a', t0: 76.2, t1: 82.22, pos: v3(110, 8, 60), look: v3(125, 40, -80), fov: 46 },
];
function studioAnim(t) {
  S.studio.ember.animate(t, 0.3); S.studio.storm.animate(t, { crawl: 0.2, rear: 0.5 + 0.1 * Math.sin(t), open: 0.2 + 0.2 * Math.sin(t * 2) });
  S.studio.quake.animate(t); S.studio.gorrak.animate(t, 0.15 + 0.15 * Math.sin(t)); S.studio.ext.animate(t, 1);
}
lv.forEach((L, i) => add(L.t0, L.t1, 'studio', (lt, k, t) => {
  S.studio.spots.forEach((s, j) => { s.s.intensity = j === i ? 160 * Math.pow(2.3, j) : 8 * Math.pow(2.2, j); s.coneMat.opacity = j === i ? 0.4 : 0.05; });
  studioAnim(t);
  const dir = L.pos.clone().sub(L.look).normalize();
  cam(L.pos.clone().addScaledVector(dir, -2.5 * k), L.look, L.fov);
  showChip(L.name, L.lvl, L.color, 640, 560, smooth(0.15, 0.6, lt) * (1 - smooth(L.t1 - L.t0 - 0.35, L.t1 - L.t0, lt)));
  if (i === 4) { S.studio.ext.animate(t, smooth(0.5, 2.5, lt)); grade.uniforms.vig.value = 0.55; }
}));
// ---- 82.22 - 86: the Bureau was born ----
add(82.22, 86.5, 'plaza', (lt, k, t) => {
  S.plaza.crowd.forEach((p) => { p.root.visible = false; });
  cam(v3(0, lerp(3, 12, k), lerp(8, 4, k)), v3(0, lerp(40, 110, k), -60), 52);
});
// ---- 86.5 - 102.37: the Bureau runs everything, sells heroes ----
add(86.5, 92.0, 'plaza', (lt, k, t) => { // logo & tower close
  S.plaza.crowd.forEach((p) => { p.root.visible = false; });
  cam(v3(lerp(-30, -18, k), 100, 40), v3(0, 118, -45), 36);
});
add(92.0, 97.0, 'plaza', (lt, k, t) => { // merch store window
  S.plaza.crowd.forEach((p) => { p.root.visible = false; });
  S.plaza.figures.forEach((f, i) => { f.root.rotation.y = -PI / 2 + PI / 2 + Math.sin(t + i) * 0.1; capeWave(f, t + i, 0.6); });
  cam(v3(23.0, 3.6, lerp(13.5, 22.5, k)), v3(32, 3.4, lerp(14, 22, k)), 42);
});
add(97.0, 102.37, 'plaza', (lt, k, t) => { // crowd photographs giant screens
  S.plaza.crowd.forEach((p, i) => { resetPose(p); p.root.visible = true; if (i % 2 === 0) { p.phone.visible = true; p.armR.shoulder.rotation.set(-2.3, 0, -0.2); p.armR.elbow.rotation.x = -0.6; } p.head.rotation.x = -0.25; });
  cam(v3(lerp(10, 6, k), 2.8, 24), v3(-10, 22, -20), 46);
});
// ---- 102.37 - 104.90: every hero has a rank ----
add(102.37, 104.90, 'studio', (lt, k, t) => {
  S.studio.lineup.visible = false; S.studio.badgeLight.intensity = 0; S.studio.badgeFill.intensity = 0;
  S.studio.badgeObjs.forEach((b) => { b.visible = false; });
  const sp = smooth(0.5, 1.6, lt); S.studio.badgeLight.intensity = 500 * sp;
  cam(v3(0, 4, 218), v3(0, 3, 200), 40);
});
// ---- 104.90 - 116.81: Iron..Crown ----
const badgeT = [104.9, 108.6, 109.9, 111.4, 113.3];
add(104.90, 116.81, 'studio', (lt, k, t) => {
  S.studio.lineup.visible = false; S.studio.badgeLight.intensity = 500; S.studio.badgeFill.intensity = 60;
  let focus = 0;
  S.studio.badgeObjs.forEach((b, i) => {
    const a = smooth(badgeT[i], badgeT[i] + 0.6, t); b.visible = a > 0;
    if (a > 0) focus = i;
    b.position.y = 3 + (1 - easeOutBack(a)) * -3; b.rotation.y = (1 - a) * PI + Math.sin(t * 0.8 + i) * 0.15; b.scale.setScalar((1 + i * 0.12) * Math.max(0.01, a));
  });
  const fx = -8 + focus * 4;
  cam(v3(lerp(camera.position.x || fx, fx, 0.08), 4, 210), v3(lerp(-2, 2, k), 3.2, 200), 44);
  camera.position.x = lerp(-6, 6, smooth(104.9, 116.8, t)); camera.lookAt(v3(camera.position.x * 0.5, 3.4, 200));
  const L = [['IRON', '#9aa0a8'], ['BRONZE', '#cd7f32'], ['SILVER', '#d9dee6'], ['GOLD', '#ffd23a'], ['CROWN', '#ffe9a0']][focus];
  const since = t - badgeT[focus]; const nextT = badgeT[focus + 1] ?? 116.81;
  showChip(L[0], `RANK ${focus + 1} OF 5`, L[1], 640, 560, smooth(0.2, 0.6, since) * (1 - smooth(nextT - badgeT[focus] - 0.3, nextT - badgeT[focus], since)));
});
// ---- 116.81 - 122.15: how does the Bureau decide ----
add(116.81, 122.15, 'room', (lt, k, t) => {
  S.room.setScore('---', '#7fd8ff'); S.room.setBar(0, null);
  [teenA, teenB, teenC, crowd[0], crowd[3]].forEach((p, i) => { show(p, 0, 0, 0.5 + i * 1.5, PI); resetPose(p); idle(p, t, i); blink(p, t, i); });
  show(tech, 4.2, 0, -6.3, 0.2); resetPose(tech); idle(tech, t);
  cam(v3(lerp(-7, -6, k), 5.5, 9), v3(0, 2, -4), 44);
});
// ---- 122.15 - 135.40: walk to Scanner; hand on panel ----
add(122.15, 128.5, 'room', (lt, k, t) => {
  S.room.setScore('---', '#7fd8ff'); S.room.setBar(0, null);
  const z = lerp(1.5, -4.4, smooth(0, 4.5, lt));
  show(teenA, 0, 0, z, PI); resetPose(teenA); if (lt < 4.5) gait(teenA, t * 6.5, 0.38, false); blink(teenA, t);
  [teenB, teenC, crowd[0]].forEach((p, i) => { show(p, 0, 0, 3.0 + i * 1.5, PI); resetPose(p); idle(p, t, i); });
  show(tech, 4.2, 0, -6.3, -0.4); resetPose(tech);
  cam(v3(2.6, 3.2, lerp(3.5, 1.5, k)), v3(0, 2.4, -5), 42);
});
add(128.5, 135.40, 'room', (lt, k, t) => {
  const climb = smooth(1.2, 6.5, lt);
  S.room.setScore(String(Math.round(412 * climb)).padStart(3, '0'), '#7fd8ff'); S.room.setBar(Math.round(climb * 412 / 1000 * 20), new THREE.Color(0.5, 2.5, 4));
  show(teenA, 0, 0, -4.4, PI); resetPose(teenA);
  teenA.armR.shoulder.rotation.set(-1.0, 0, -0.1); teenA.armR.elbow.rotation.x = -0.5; teenA.head.rotation.x = 0.3; blink(teenA, t);
  cam(v3(lerp(-2.4, -1.8, k), 2.4, lerp(-2.4, -3.0, k)), v3(0, 1.8, -5.4), 38);
});
// ---- 135.40 - 146.92: scores 412 / 640 / 921 ----
const scoreShot = (t0, t1, p, score, color, gold) => add(t0, t1, 'room', (lt, k, t) => {
  S.room.setScore(String(score), color); S.room.setBar(Math.round(score / 1000 * 20), new THREE.Color(color).multiplyScalar(3));
  show(p, 0, 0, -3.9, 0); resetPose(p); blink(p, t);
  const cheer = smooth(0.3, 0.8, lt);
  if (gold) { p.armR.shoulder.rotation.z = -2.8 * cheer; p.armL.shoulder.rotation.z = 2.8 * cheer; mouth(p, 'open', 1); }
  else { p.armR.shoulder.rotation.set(-0.3, 0, -2.4 * cheer); p.armR.elbow.rotation.x = -0.8; mouth(p, 'smile', 1); }
  S.room.scanLight.color.set(color); S.room.scanLight.intensity = gold ? 60 : 20;
  cam(v3(lerp(1.6, 1.2, k), 3.4, lerp(0.8, 0.2, k)), v3(0, 3.6, -5), 40);
  if (gold) grade.uniforms.flash.value = 0.15 * (1 - smooth(0, 0.6, lt));
});
scoreShot(135.40, 139.4, teenA, 412, '#7fd8ff', false);
scoreShot(139.4, 143.2, teenB, 640, '#9dff7f', false);
scoreShot(143.2, 146.92, teenC, 921, '#ffd23a', true);
// ---- 146.92 - 150.88: that number is your whole future ----
add(146.92, 150.88, 'studio', (lt, k, t) => {
  S.studio.setCard({ name: 'NOVA LEE', rank: 'GOLD', num: '#58', score: '921', scoreColor: '#ffd23a', c1: '#6b5320', c2: '#1b1408' });
  S.studio.lineup.visible = false; S.studio.cardLight.intensity = 70; S.studio.cardFill.intensity = 8;
  S.studio.card.rotation.set(0.05, lerp(0.35, -0.2, k), -0.03);
  cam(v3(-150 + lerp(1.5, 0.5, k), 3.4, 155.5), v3(-150, 3, 150), 38);
});
// ---- 150.88 - 154.42: which brings us to you ----
add(150.88, 154.42, 'city', (lt, k, t) => {
  show(hero, 0, 0, 5, 0.0); resetPose(hero); hero.vest.visible = false; hero.bag.visible = false; idle(hero, t); blink(hero, t);
  hero.head.rotation.y = lerp(0.6, 0, smooth(0.3, 1.4, lt)); mouth(hero, 'smile', 0.3);
  S.city.gorrak.group.visible = false;
  cam(v3(0.4, 3.0, lerp(8.6, 8.0, k)), v3(0, 3.0, 5), 32);
});
// ---- 154.42 - 169.75: flashback, 18th birthday with mom ----
const flash = (fn) => (lt, k, t) => { grade.uniforms.sepia.value = 0.32; fn(lt, k, t); };
add(154.42, 161.5, 'room', flash((lt, k, t) => {
  S.room.setScore('---', '#7fd8ff'); S.room.setBar(0, null);
  const z = lerp(8, 3, smooth(0, 6, lt));
  show(hero, -0.7, 0, z, PI); resetPose(hero); hero.vest.visible = false; hero.bag.visible = false; gait(hero, t * 6, 0.32, false); hero.root.scale.setScalar(0.94);
  show(mom, 0.8, 0, z + 0.3, PI); resetPose(mom); gait(mom, t * 6 + 1, 0.3, false);
  mom.armR.shoulder.rotation.set(-0.3, 0, -0.5);
  show(tech, 4.2, 0, -6.3, 0.3); resetPose(tech);
  cam(v3(lerp(3.5, 2.5, k), 3.2, lerp(-2, -1, k)), v3(0, 2.6, z), 40);
}));
add(161.5, 169.75, 'room', flash((lt, k, t) => {
  S.room.setScore('---', '#7fd8ff'); S.room.setBar(0, null);
  show(hero, -0.5, 0, 0.5, PI); resetPose(hero); hero.vest.visible = false; hero.bag.visible = false; hero.root.scale.setScalar(0.94); idle(hero, t); blink(hero, t);
  hero.head.rotation.x = -0.15; mouth(hero, 'smile', 0.5);
  show(mom, 0.9, 0, 1.0, PI + 0.4); resetPose(mom); mom.armR.shoulder.rotation.set(-0.6, 0, 0.4); mom.armR.elbow.rotation.x = -0.4; mouth(mom, 'smile', 1); blink(mom, t, 1);
  const e = new THREE.Vector3(); hero.emblem.getWorldPosition(e);
  const head = new THREE.Vector3(); hero.head.getWorldPosition(head);
  const look = vlerp(e, head, smooth(2, 7, lt));
  cam(v3(-0.5 + 0.3, look.y + 0.1, -1.6 + 0.5 * k), look, 34);
}));
// ---- 169.75 - 173.57: hand on scanner ----
add(169.75, 173.57, 'room', flash((lt, k, t) => {
  S.room.setScore('---', '#7fd8ff'); S.room.setBar(0, null);
  show(hero, 0, 0, -4.4, PI); resetPose(hero); hero.vest.visible = false; hero.bag.visible = false; hero.root.scale.setScalar(0.94);
  const r = smooth(0.4, 2.0, lt); hero.armR.shoulder.rotation.set(-1.0 * r, 0, -0.1); hero.armR.elbow.rotation.x = -0.5 * r - 0.25 * (1 - r);
  S.room.handGlowMat.color.setRGB(1.5 + 2 * r, 2.5 + 1.5 * r, 3.5 + r);
  cam(v3(1.9, 2.3, -4.6), v3(0, 1.6, -5.45), 36);
}));
// ---- 173.57 - 177.47: lights climb... then stop ----
add(173.57, 177.47, 'room', flash((lt, k, t) => {
  const c = smooth(0.2, 1.6, lt) * 0.5 * (1 - smooth(1.8, 2.8, lt));
  S.room.setBar(Math.round(c * 20), new THREE.Color(0.5, 2.5, 4)); S.room.setScore(String(Math.round(c * 300)), '#7fd8ff');
  cam(v3(1.4, 3.4, lerp(-2.4, -2.8, k)), v3(0, 3.7, -5.5), 44);
}));
// ---- 177.47 - 178.49: ZERO ----
add(177.47, 178.49, 'room', flash((lt, k, t) => {
  S.room.setBar(0, null); S.room.setScore('0', '#ff4b3e'); S.room.scanLight.color.set('#ff4b3e'); S.room.scanLight.intensity = 40;
  cam(v3(0, 4.6, lerp(-2.6, -3.3, k)), v3(0, 4.6, -5.9), 30); shake(0.02, t);
}));
// ---- 178.49 - 188.45: technician laughs, takes a photo ----
add(178.49, 183.0, 'room', flash((lt, k, t) => {
  S.room.setScore('0', '#ff4b3e');
  show(tech, 2.2, 0, -4.2, -0.9); resetPose(tech); laugh(tech, t, 1);
  show(hero, 0, 0, -4.2, PI * 0.8); resetPose(hero); hero.vest.visible = false; hero.bag.visible = false; hero.root.scale.setScalar(0.94); hero.head.rotation.x = 0.25; mouth(hero, 'frown');
  cam(v3(lerp(-1.5, -1.0, k), 3.1, 1.5), v3(1.2, 2.8, -4.2), 38);
}));
add(183.0, 188.45, 'room', flash((lt, k, t) => {
  S.room.setScore('0', '#ff4b3e');
  show(tech, 1.6, 0, -2.8, -0.5); resetPose(tech); tech.phone.visible = true; tech.armR.shoulder.rotation.set(-1.9, 0, 0.3); tech.armR.elbow.rotation.x = -0.9; mouth(tech, 'smile', 1); for (const e of tech.eyes) e.scale.y = 0.4;
  cam(v3(-2.4, 3.0, 0.0), v3(1.1, 3.4, -3.6), 46);
  const fl = Math.max(0, 1 - Math.abs(lt - 2.2) / 0.12); grade.uniforms.flash.value = fl * 0.85;
}));
// ---- 188.45 - 195.50: photo everywhere, memes ----
add(188.45, 195.50, 'studio', (lt, k, t) => {
  const idx = lt < 2.4 ? 0 : lt < 4.8 ? 1 : 2; S.studio.setPost(idx); S.studio.lineup.visible = false; S.studio.phoneLight.intensity = 12;
  S.studio.phone.rotation.set(-0.08, Math.sin(lt * 0.8) * 0.25, 0.05);
  cam(v3(150, 3.0, lerp(158, 156.5, k)), v3(150, 3, 150), 38);
});
// ---- 195.50 - 207.89: license, Iron #4812, last hero ----
add(195.50, 201.0, 'studio', (lt, k, t) => {
  S.studio.setCard({ name: 'THE ZERO', rank: 'IRON', num: '#4,812', score: '0' });
  S.studio.lineup.visible = false; S.studio.cardLight.intensity = 70; S.studio.cardFill.intensity = 8;
  S.studio.card.rotation.set(lerp(-1.2, 0.05, easeOutBack(smooth(0, 1.2, lt))), lerp(0.6, -0.1, k), 0);
  cam(v3(-149.4, 3.3, 155.8), v3(-150, 3, 150), 38);
});
add(201.0, 207.89, 'plaza', (lt, k, t) => {
  S.plaza.crowd.forEach((p) => { p.root.visible = false; });
  S.plaza.drawRankList(Math.pow(smooth(0, 5.5, lt), 2));
  cam(v3(0, 12, lerp(-22, -25, k)), v3(0, 12, -42), 40);
});
// ---- 207.89 - 217.43: four years of small jobs ----
add(207.89, 211.0, 'hood', (lt, k, t) => { // old lady crosswalk
  const x = lerp(-6, 1, k);
  show(oldLady, x, 0, 0.2, PI / 2); resetPose(oldLady); gait(oldLady, t * 4, 0.18, false); oldLady.armL.shoulder.rotation.set(-0.5, 0, 0.2); oldLady.torso.rotation.x = 0.15; blink(oldLady, t);
  show(hero, x + 0.1, 0, -0.9, PI / 2); resetPose(hero); hero.vest.visible = true; hero.bag.visible = false; gait(hero, t * 4, 0.2, false);
  hero.armL.shoulder.rotation.set(-0.6, 0, -0.4); mouth(hero, 'smile', 0.6);
  cam(v3(x + 3, 2.2, 7), v3(x, 2.0, -0.3), 40);
});
add(211.0, 214.2, 'hood', (lt, k, t) => { // cat in tree
  show(hero, -7.2, 0.25, -28.7, -0.7); resetPose(hero); hero.vest.visible = true; hero.bag.visible = false;
  hero.armR.shoulder.rotation.set(-2.6 - 0.1 * Math.sin(t * 3), 0, 0.1); hero.armL.shoulder.rotation.set(-2.4, 0, -0.1); hero.head.rotation.x = -0.45; mouth(hero, 'o');
  cam(v3(-3.2, 2.4, -25.5), v3(-7.6, 3.6, -29.8), 42);
});
add(214.2, 217.43, 'hood', (lt, k, t) => { // parking lot, gold hero commercial
  const L = S.hood.lot.position;
  show(hero, L.x - 9, 0.02, L.z + 5, 0.4); resetPose(hero); hero.vest.visible = true; hero.bag.visible = false; idle(hero, t); mouth(hero, 'flat'); blink(hero, t);
  hero.armR.shoulder.rotation.z = -0.1; hero.armL.shoulder.rotation.z = 0.1;
  show(goldHero, L.x + 2, 0.02, L.z - 1, 0.4); resetPose(goldHero); goldHero.armR.shoulder.rotation.set(0, 0, -2.6); goldHero.armL.shoulder.rotation.set(-0.3, 0, 0.6); goldHero.armL.elbow.rotation.x = -1.8; capeWave(goldHero, t, 1); mouth(goldHero, 'smile', 1);
  show(cameraman, L.x + 4.7, 0.02, L.z + 3.4, PI + 0.8); resetPose(cameraman);
  cam(v3(L.x - 12, 3.0, L.z + 14), v3(L.x - 1, 2.2, L.z + 1), 40);
});
// ---- 217.43 - 222.84: every day someone reminds you ----
add(217.43, 222.84, 'hood', (lt, k, t) => {
  const z = lerp(-8, -14, k);
  show(hero, 7.4, 0.25, z, PI); resetPose(hero); hero.vest.visible = true; hero.bag.visible = false; gait(hero, t * 6, 0.32, false); mouth(hero, 'flat');
  [crowd[1], crowd[4], crowd[6]].forEach((p, i) => { show(p, 8.6 + i * 0.9, 0.25, z - 6 + i * 5 + lt * (i % 2 ? 1.2 : -1.2) * 0.5, i % 2 ? PI : 0); resetPose(p); gait(p, t * 6 + i, 0.32, false); p.head.rotation.y = (i % 2 ? -0.6 : 0.6); });
  cam(v3(1.8, 2.6, z - 5), v3(7.4, 2.4, z), 42);
});
// ---- 222.84 - 226.14: kids shout ----
add(222.84, 226.14, 'hood', (lt, k, t) => {
  for (const [p, x, off] of [[kid1, 6.5, 0], [kid2, 7.6, 0.6], [kid3, 8.6, 1.2]]) { show(p, x, 0.25, -12, -PI / 2 + 0.3); resetPose(p); laugh(p, t + off, 1); }
  point(kid1, 'R', 0.15);
  cam(v3(lerp(3.5, 4.0, k), 1.5, -9.2), v3(7.5, 1.6, -12), 40);
});
// ---- 226.14 - 230.85: smile, wave, keep walking ----
add(226.14, 230.85, 'hood', (lt, k, t) => {
  const z = lerp(-12, -17, k);
  show(hero, 7.4, 0.25, z, PI); resetPose(hero); hero.vest.visible = true; hero.bag.visible = false; gait(hero, t * 6, 0.32, false);
  hero.head.rotation.y = -0.9 * (1 - smooth(2.5, 3.5, lt)); if (lt < 2.8) { wave(hero, t, 'L'); } mouth(hero, 'smile', 1); blink(hero, t);
  cam(v3(1.8, 2.7, z - 5), v3(7.4, 2.7, z), 38);
});
// ---- 230.85 - 245.73: hands get warm; something waking up; you were wrong ----
add(230.85, 236.5, 'city', (lt, k, t) => { // alone at dusk, looking at hands
  S.city.gorrak.group.visible = false;
  show(hero, -11.5, 0.25, 4, PI / 2); resetPose(hero); hero.vest.visible = false; hero.bag.visible = false; blink(hero, t);
  hero.armR.shoulder.rotation.set(-0.9, 0, 0.2); hero.armR.elbow.rotation.x = -1.4; hero.head.rotation.x = 0.4; mouth(hero, 'flat');
  cam(v3(lerp(-5, -6, k), 2.4, 7.5), v3(-11.5, 2.4, 4), 38);
});
add(236.5, 242.55, 'city', (lt, k, t) => { // hand close-up warms up
  S.city.gorrak.group.visible = false;
  show(hero, -11.5, 0.25, 4, PI / 2); resetPose(hero); hero.vest.visible = false; hero.bag.visible = false;
  hero.armR.shoulder.rotation.set(-0.9, 0, 0.2); hero.armR.elbow.rotation.x = -1.4;
  heroGlow(smooth(0.5, 5.5, lt) * 0.35, t);
  const f = new THREE.Vector3(); hero.armR.fist.getWorldPosition(f);
  cam(v3(f.x + 1.3, f.y + 0.35, f.z + 0.4 - 0.2 * k), f, 30);
});
add(242.55, 245.73, 'city', (lt, k, t) => { // eyes; you were wrong
  S.city.gorrak.group.visible = false;
  show(hero, -11.5, 0.25, 4, PI / 2); resetPose(hero); hero.vest.visible = false; hero.bag.visible = false;
  hero.armR.shoulder.rotation.set(-0.9, 0, 0.2); hero.armR.elbow.rotation.x = -1.4; heroGlow(0.4 + 0.3 * smooth(1.9, 2.5, lt), t);
  hero.head.rotation.x = lerp(0.35, 0.0, smooth(1.6, 2.4, lt)); mouth(hero, 'flat');
  const h = new THREE.Vector3(); hero.head.getWorldPosition(h);
  cam(v3(h.x + 1.5, h.y - 0.05, h.z + 0.15), h, 26);
  black.style.opacity = smooth(2.7, 3.15, lt);
});
// ---- 245.73 - 249.46: Tuesday at Central Station ----
add(245.73, 249.46, 'station', (lt, k, t) => {
  S.station.setAlarm(t, 0); S.station.storm.group.visible = false;
  const z = lerp(-6, -10, k);
  show(hero, -3.2, 1.2, z, PI); resetPose(hero); hero.vest.visible = true; hero.bag.visible = true; gait(hero, t * 5.5, 0.3, false);
  hero.armL.shoulder.rotation.set(-0.3, 0, 0.15); hero.armL.elbow.rotation.x = -1.3; mouth(hero, 'smile', 0.5);
  show(oldLady, -4.6, 1.2, z - 0.3, PI); resetPose(oldLady); gait(oldLady, t * 5.5, 0.18, false);
  crowd.slice(0, 6).forEach((p, i) => { show(p, -7 + (i % 3) * 3.5, 1.2, -16 - i * 4, i % 2 ? 0 : PI); resetPose(p); gait(p, t * 5 + i, 0.3, false); p.root.position.z += (i % 2 ? 1 : -1) * lt * 1.2; });
  cam(v3(-1.5, 3.4, z + 6.5), v3(-3.5, 2.8, z - 6), 46);
  black.style.opacity = 1 - smooth(0, 0.4, lt);
});
// ---- 249.46 - 256.55: floor of Platform 6 explodes ----
add(249.46, 253.2, 'station', (lt, k, t) => { // shaking, cracks, freeze
  S.station.setAlarm(t, 0); S.station.storm.group.visible = false;
  const c = smooth(0.4, 3.2, lt); S.station.crackMat.opacity = c; S.station.holeLight.intensity = 60 * c;
  crowd.slice(0, 5).forEach((p, i) => { show(p, -6 + i * 2, 1.2, -31 - (i % 2) * 2, PI * 0.1 * i); resetPose(p); mouth(p, 'o'); p.head.rotation.x = 0.4; for (const e of p.eyes) e.scale.y = 1.3; });
  show(hero, -3.2, 1.2, -12, PI); resetPose(hero); hero.vest.visible = true; hero.bag.visible = true; hero.armL.shoulder.rotation.set(-0.3, 0, 0.15); hero.armL.elbow.rotation.x = -1.3; hero.head.rotation.x = 0.35;
  cam(v3(-4.5, 3.8, -13), v3(-1, 1.3, -24), 44); shake(0.03 + 0.08 * c, t);
});
add(253.2, 256.55, 'station', (lt, k, t) => { // eruption
  S.station.setAlarm(t, 0);
  S.station.crackMat.opacity = 1; S.station.pitHole.scale.setScalar(Math.max(0.001, smooth(0, 0.3, lt))); S.station.holeLight.intensity = 120;
  const dt = Math.max(0, lt - 0.05);
  S.station.debris.forEach((d) => { d.m.visible = true; d.m.position.set(-1 + d.v.x * dt * 0.6, 1.3 + d.v.y * dt * 0.6 - 9.8 * dt * dt * 0.5, -24 + d.v.z * dt * 0.6); d.m.rotation.set(d.r.x * dt, d.r.y * dt, d.r.z * dt); if (d.m.position.y < 1.3) d.m.position.y = 1.3; });
  S.station.dust.forEach((d) => { const r = (1 + d.r * 6) * smooth(0, 2.5, dt); d.s.visible = true; d.s.position.set(-1 + Math.cos(d.a) * r, 1.5 + d.k * 4 * smooth(0, 2, dt), -24 + Math.sin(d.a) * r); d.s.scale.setScalar(3 + 6 * smooth(0, 3, dt)); d.s.material.opacity = 0.6 * (1 - smooth(2, 3.5, dt)); });
  const st = S.station.storm; st.group.visible = true; st.group.position.set(-1, 1.2 - 6 + 6 * smooth(0.1, 1.2, lt), -24); st.group.rotation.y = 0.4;
  st.animate(t, { rear: smooth(0.2, 1.4, lt), open: smooth(1.4, 2.0, lt), crawl: 0.3 });
  cam(v3(-5.5, 2.4, -12), v3(-1, 4.5, -24), 50); shake(0.12 * (1 - smooth(0, 2.5, lt)), t);
  grade.uniforms.flash.value = 0.5 * (1 - smooth(0, 0.25, lt)); grade.uniforms.flashColor.value.setRGB(1, 0.75, 0.5);
});
function stormUp(t, opts = {}) {
  const st = S.station.storm; st.group.visible = true; st.group.position.set(-1, 1.2, -24); st.group.rotation.y = opts.ry ?? 0.4;
  st.animate(t, { rear: 1, open: 0.3 + 0.3 * Math.sin(t * 1.7), crawl: 0.2, ...opts });
  S.station.crackMat.opacity = 1; S.station.pitHole.scale.setScalar(1); S.station.holeLight.intensity = 80;
  S.station.debris.forEach((d) => { d.m.visible = true; d.m.position.y = 1.3; });
}
// ---- 256.55 - 267.10: Storm-level; alarms; people run; kid crying ----
add(256.55, 261.2, 'station', (lt, k, t) => { // monster reveal low angle
  S.station.setAlarm(t, 1); stormUp(t, { open: 0.5 + 0.4 * Math.sin(t * 2) });
  cam(v3(lerp(-6, -5, k), 1.7, -13.5), v3(-1, lerp(5, 7.5, k), -23), 48);
});
add(261.2, 267.10, 'station', (lt, k, t) => { // panic, girl near pillar
  S.station.setAlarm(t, 1); stormUp(t);
  crowd.forEach((p, i) => { show(p, -8 + (i % 5) * 2.4, 1.2, -18 + Math.max(0, lt - i * 0.15) * 7, 0); resetPose(p); gait(p, t * 12 + i, 0.75, true); mouth(p, 'o'); });
  show(girl, -0.8, 1.2, -16, PI * 0.15); resetPose(girl); girl.armR.shoulder.rotation.set(-0.4, 0, 0.6); girl.armR.elbow.rotation.x = -2.2; girl.armL.shoulder.rotation.set(-0.4, 0, -0.6); girl.armL.elbow.rotation.x = -2.2; mouth(girl, 'open', 0.7); for (const e of girl.eyes) e.scale.y = 0.4;
  girl.torso.rotation.x = 0.15 + Math.sin(t * 9) * 0.03;
  cam(v3(-2, 3.0, -2), v3(-1, 2.6, -20), 46);
});
// ---- 267.10 - 269.56: nearest hero is... you ----
add(267.10, 269.56, 'station', (lt, k, t) => {
  S.station.setAlarm(t, 1); stormUp(t);
  show(hero, -3.0, 1.2, -9, PI); resetPose(hero); hero.vest.visible = true; hero.bag.visible = true; hero.armL.shoulder.rotation.set(-0.3, 0, 0.15); hero.armL.elbow.rotation.x = -1.3; blink(hero, t); mouth(hero, 'flat');
  const h = new THREE.Vector3(); hero.head.getWorldPosition(h);
  cam(v3(h.x + 0.2, h.y, h.z - lerp(2.4, 1.9, k)), h, 32);
});
// ---- 269.56 - 272.89: phone app ----
add(269.56, 272.89, 'studio', (lt, k, t) => {
  S.studio.setPost(3); S.studio.lineup.visible = false; S.studio.phoneLight.intensity = 10; S.studio.group.children[1].material.uniforms.tint.value.setRGB(0.35, 0.03, 0.03);
  S.studio.phone.rotation.set(-0.12, 0.12, 0.04);
  cam(v3(150, 3.1, lerp(156.8, 156.0, k)), v3(150, 3, 150), 38);
});
// ---- 272.89 - 280.65: nine minutes; it can tear the station apart ----
add(272.89, 280.65, 'station', (lt, k, t) => {
  S.station.setAlarm(t, 1); stormUp(t, { ry: 0.4 + Math.sin(lt * 0.8) * 0.5, open: 0.7 + 0.3 * Math.sin(t * 3), clawRaise: smooth(2, 3, lt) * (1 - smooth(4, 4.5, lt)) });
  const c = S.station.columns[1]; const hit = smooth(4.2, 4.6, lt); c.rotation.z = -0.4 * hit; c.position.x = 1.5 + 2.5 * hit; c.position.y = 6.6 - 1.5 * hit;
  cam(v3(lerp(-7, -6, k), 2.2, -12), v3(0, 5, -24), 46); shake(0.12 * Math.max(0, 1 - Math.abs(lt - 4.5) * 2), t);
});
// ---- 280.65 - 288.58: it sees the girl; opens its mouth ----
add(280.65, 284.6, 'station', (lt, k, t) => {
  S.station.setAlarm(t, 1); stormUp(t, { ry: lerp(0.4, -0.3, smooth(0, 2.5, lt)) });
  show(girl, -0.8, 1.2, -16, PI * 0.15); resetPose(girl); girl.armR.shoulder.rotation.set(-0.4, 0, 0.6); girl.armR.elbow.rotation.x = -2.2; girl.armL.shoulder.rotation.set(-0.4, 0, -0.6); girl.armL.elbow.rotation.x = -2.2; mouth(girl, 'open', 0.5); girl.head.rotation.x = -0.3;
  cam(v3(6, 2.0, -6), v3(0, 3.2, -20), 40);
});
add(284.6, 288.58, 'station', (lt, k, t) => {
  S.station.setAlarm(t, 1); stormUp(t, { ry: -0.3, open: smooth(0.3, 2.5, lt), look: 0.1 });
  const h = new THREE.Vector3(); S.station.storm.head.getWorldPosition(h);
  const dir = v3(0.6, -0.2, 1).normalize();
  cam(h.clone().addScaledVector(dir, lerp(6.5, 4.5, k)), h, 40);
});
// ---- 288.58 - 292.11: you just run ----
add(288.58, 290.1, 'station', (lt, k, t) => { // groceries drop
  S.station.setAlarm(t, 1); stormUp(t, { ry: -0.3, open: 1 });
  show(hero, -3.0, 1.2, -9, PI); resetPose(hero); hero.vest.visible = true; hero.bag.visible = true;
  const fall = smooth(0.1, 1.2, lt);
  hero.bag.position.set(0, -0.75 - fall * 1.6, 0.15 + fall * 0.4); hero.bag.rotation.x = fall * 1.2;
  cam(v3(-1.0, 3.0, -12.6), v3(-3.0, 2.3, -9), 42);
});
add(290.1, 292.11, 'station', (lt, k, t) => { // run
  S.station.setAlarm(t, 1); stormUp(t, { ry: -0.3, open: 1 });
  hero.bag.position.set(0, -0.75, 0.15); hero.bag.rotation.x = 0;
  const z = lerp(-9, -14.5, k);
  show(hero, lerp(-3, -1.5, k), 1.2, z, PI - 0.3); resetPose(hero); hero.vest.visible = true; hero.bag.visible = false; gait(hero, t * 13, 0.8, true); mouth(hero, 'flat');
  cam(v3(lerp(-6, -4, k), 2.4, z + 2.5), v3(0, 2.6, z - 5), 44);
});
// ---- 292.11 - 302.14: in front of the girl; claw comes down; raise arm ----
add(292.11, 297.0, 'station', (lt, k, t) => {
  S.station.setAlarm(t, 1); stormUp(t, { ry: -0.25, open: 0.8, clawRaise: smooth(1.0, 3.0, lt) });
  show(girl, -0.8, 1.2, -16, PI * 0.15); resetPose(girl); mouth(girl, 'o'); girl.armR.shoulder.rotation.set(-0.4, 0, 0.6); girl.armR.elbow.rotation.x = -2.2;
  show(hero, -1.4, 1.2, -17.3, PI + 0.15); resetPose(hero); hero.vest.visible = true; hero.bag.visible = false;
  const up = smooth(2.0, 3.5, lt); hero.armR.shoulder.rotation.set(-2.0 * up, 0, -0.3 * up); hero.armR.elbow.rotation.x = -1.6 * up; hero.armL.shoulder.rotation.set(0.2, 0, 1.0); hero.legL.hip.rotation.x = -0.4; hero.legR.hip.rotation.x = 0.3; mouth(hero, 'flat');
  cam(v3(-5.6, 2.6, -12.0), v3(-1.2, 3.0, -18), 42);
});
add(297.0, 302.14, 'station', (lt, k, t) => { // slow-motion claw from low angle
  S.station.setAlarm(t, 1); stormUp(t, { ry: -0.25, open: 1, clawRaise: 1 - 0.5 * smooth(0, 5, lt) });
  show(hero, -1.4, 1.2, -17.3, PI + 0.15); resetPose(hero); hero.vest.visible = true; hero.bag.visible = false;
  hero.armR.shoulder.rotation.set(-2.0, 0, -0.3); hero.armR.elbow.rotation.x = -1.6; hero.armL.shoulder.rotation.set(0.2, 0, 1.0); hero.head.rotation.x = -0.35;
  show(girl, -0.7, 1.2, -16.2, PI * 0.15); resetPose(girl);
  cam(v3(-6.0, 1.5, -15.5), v3(-1.6, 5.0, -21), 52, -0.08);
});
// ---- 302.14 - 305.00: "Get out of the way, Zero!" ----
add(302.14, 305.0, 'station', (lt, k, t) => {
  S.station.setAlarm(t, 1); stormUp(t, { ry: -0.25, open: 1, clawRaise: 0.5 });
  show(shouter, -6.5, 1.2, -6, PI * 0.85); resetPose(shouter); mouth(shouter, 'open', 1);
  shouter.armR.shoulder.rotation.set(-1.5, 0, 0.5); shouter.armR.elbow.rotation.x = -2.3; shouter.armL.shoulder.rotation.set(-1.5, 0, -0.5); shouter.armL.elbow.rotation.x = -2.3; shouter.torso.rotation.x = 0.15;
  cam(v3(-5.6, 3.3, -9.2), v3(-6.5, 3.1, -6), 36);
});
// ---- 305.00 - 310.5: hands get warm... they BURN ----
add(305.0, 306.85, 'station', (lt, k, t) => { // eyes widen, glow rushes up arm
  S.station.setAlarm(t, 1); stormUp(t, { ry: -0.25, open: 1, clawRaise: 0.5 });
  show(hero, -1.4, 1.2, -17.3, PI + 0.15); resetPose(hero); hero.vest.visible = true; hero.bag.visible = false;
  hero.armR.shoulder.rotation.set(-2.0, 0, -0.3); hero.armR.elbow.rotation.x = -1.6; hero.head.rotation.x = -0.2;
  for (const e of hero.eyes) e.scale.set(1.15, 1.3, 1); mouth(hero, 'o'); heroGlow(0.3 + 0.4 * smooth(0, 1.8, lt), t);
  const h = new THREE.Vector3(); hero.head.getWorldPosition(h);
  cam(v3(h.x - 0.3, h.y, h.z - lerp(2.2, 1.7, k)), h, 30);
});
add(306.85, 308.84, 'station', (lt, k, t) => { // not warm
  S.station.setAlarm(t, 1); stormUp(t, { ry: -0.25, open: 1, clawRaise: 0.5 });
  show(hero, -1.4, 1.2, -17.3, PI + 0.15); resetPose(hero); hero.vest.visible = true; hero.bag.visible = false;
  hero.armR.shoulder.rotation.set(-2.0, 0, -0.3); hero.armR.elbow.rotation.x = -1.6;
  heroGlow(0.7 + 0.2 * smooth(0, 2, lt), t); mouth(hero, 'flat'); for (const e of hero.eyes) e.scale.y = 0.75;
  const f = new THREE.Vector3(); hero.armR.fist.getWorldPosition(f);
  cam(v3(f.x - 1.4, f.y - 0.3, f.z - 1.6), f, 40); shake(0.02, t);
});
add(308.84, 310.6, 'station', (lt, k, t) => { // they BURN
  S.station.setAlarm(t, 1); stormUp(t, { ry: -0.25, open: 1, clawRaise: 0.5 });
  show(hero, -1.4, 1.2, -17.3, PI + 0.15); resetPose(hero); hero.vest.visible = true; hero.bag.visible = false;
  hero.armR.shoulder.rotation.set(-2.0, 0, -0.3); hero.armR.elbow.rotation.x = -1.6; for (const e of hero.eyes) e.scale.y = 0.6; mouth(hero, 'flat');
  heroGlow(1.0 + 0.6 * smooth(0, 0.8, lt), t);
  const f = new THREE.Vector3(); hero.armR.fist.getWorldPosition(f);
  cam(v3(f.x - 1.6, f.y - 0.6, f.z - 2.4), f, 44); shake(0.06, t);
  radial.enabled = true; radial.uniforms.strength.value = 0.12 * smooth(0.2, 0.9, lt);
  grade.uniforms.flash.value = smooth(0.6, 0.95, lt) * 0.9; grade.uniforms.flashColor.value.setRGB(1, 0.9, 0.6);
  black.style.opacity = smooth(1.0, 1.4, lt);
});

// =====================================================================
window.DURATION = 310.6;
window.renderFrame = (t) => {
  const shot = shots.find((s) => t >= s.t0 && t < s.t1) || shots[shots.length - 1];
  // reset per-frame state
  for (const p of actors) { p.root.visible = false; p.root.scale.setScalar(p.cfg.scale ?? 1); }
  fistGlowMat.opacity = 0; armGlow.material.opacity = 0; fistLight.intensity = 0;
  grade.uniforms.sepia.value = 0; grade.uniforms.flash.value = 0; grade.uniforms.flashColor.value.setRGB(1, 0.97, 0.92); grade.uniforms.vig.value = 0.4;
  radial.enabled = false; titleEl.style.opacity = 0; chip.style.opacity = 0; black.style.opacity = 0;
  S.city.gorrak.group.visible = true; S.city.ember.group.visible = false; S.city.crack.material.opacity = 0; S.city.hole.scale.setScalar(0.001); S.city.breachLight.intensity = 0; S.city.beamMat.opacity = 0;
  S.room.scanLight.color.set('#7fd8ff'); S.room.scanLight.intensity = 10; S.room.handGlowMat.color.setRGB(1.5, 2.5, 3.5);
  S.studio.group.children[1].material.uniforms.tint.value.setRGB(0.18, 0.06, 0.25);
  S.studio.lineup.visible = true; S.studio.spots.forEach((s) => { s.s.intensity = 0; s.coneMat.opacity = 0; }); S.studio.badgeLight.intensity = 0; S.studio.badgeFill.intensity = 0; S.studio.cardLight.intensity = 0; S.studio.cardFill.intensity = 0; S.studio.phoneLight.intensity = 0;
  if (cur !== 'station' || shot.set !== 'station' || t < 253.2) { S.station.debris.forEach((d) => { d.m.visible = false; }); S.station.dust.forEach((d) => { d.s.visible = false; }); S.station.crackMat.opacity = 0; S.station.pitHole.scale.setScalar(0.001); S.station.holeLight.intensity = 0; const c = S.station.columns[1]; c.rotation.z = 0; c.position.set(1.5, 6.6, c.position.z); }
  if (t > 256.4) S.station.dust.forEach((d) => { d.s.visible = false; });
  if (hero.bag) { hero.bag.position.set(0, -0.75, 0.15); hero.bag.rotation.set(0, 0, 0); }
  activate(shot.set);
  const lt = t - shot.t0, k = clamp(lt / (shot.t1 - shot.t0));
  shot.fn(lt, k, t);
  S[shot.set].update(t);
  sky.material.uniforms.time.value = t; grade.uniforms.time.value = t;
  E.composer.render();
  return true;
};
window.sceneReady = true;
window.renderFrame(0);
