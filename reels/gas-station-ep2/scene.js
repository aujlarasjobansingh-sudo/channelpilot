// EPISODE 2 — "The Late-Night Gas Station Shift" (Part 2) — full 1:50 timeline (POV cashier).
// Continues straight from Episode 1's freeze frame. Same lens, toon look and camera language.
import { THREE, scene, camera, setFocal, projectLens, renderFrame, lens, D2R, sineIO, sineIn, easeOut, seg, lerp, M, box, cyl } from './core.js';
import { buildSet, drawRain, C, EYE, CT, doors, setDoor, setLocked, car, phone, phoneTex, lockBtn, landline, rag, body } from './set.js';
import { makeHand, poseHand, makeArm, placeArm, basisQuat, makeMaya, poseMaya, makeOfficer, poseOfficer } from './chars.js';

const V = (x, y, z) => new THREE.Vector3(x, y, z);
await Promise.all([500, 600, 700, 800, 900].map(w => document.fonts.load(`${w} 40px Rubik`)));
const DLG = await (await fetch('out/dialogue.json')).json();
buildSet();
scene.background = new THREE.Color(C.ceiling);
const amb = new THREE.AmbientLight('#f4f7ff', 2.6); scene.add(amb);
const sun = new THREE.DirectionalLight('#ffffff', 0.75); sun.position.set(-1, 6, 2); scene.add(sun);
const maya = makeMaya(), cop = makeOfficer();
const handR = makeHand(1), handL = makeHand(-1), armR = makeArm(), armL = makeArm();
const FREEZE = 99.2, DUR = 110;

// ============================================================ helpers
const ease = { s: sineIO, in: sineIn, lin: t => t, snap: t => t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2, out: easeOut };
const wrapA = a => Math.atan2(Math.sin(a), Math.cos(a));
const yawTo = (from, to) => Math.atan2(to.x - from.x, to.z - from.z);              // character yaw (faces +z)
const camYawTo = (from, to) => Math.atan2(-(to.x - from.x), -(to.z - from.z)) / D2R; // camera yaw (faces -z)
const camPitchTo = (from, to) => Math.atan2(to.y - from.y, Math.hypot(to.x - from.x, to.z - from.z)) / D2R;
const mouthOf = (spk, t) => { const a = DLG.mouth[spk]; return (a && a[Math.floor(t * 30)]) || 0; };
const loc = (root, yaw, x, y, z) => root.clone().add(V(Math.cos(yaw) * x + Math.sin(yaw) * z, y, -Math.sin(yaw) * x + Math.cos(yaw) * z));
const camLocal = (x, y, z) => V(x, y, z).applyMatrix4(camera.matrixWorld);
const camDir = (x, y, z) => V(x, y, z).transformDirection(camera.matrixWorld);
const noise = (t, s) => Math.sin(t * 7.3 + s) * 0.5 + Math.sin(t * 13.1 + s * 2) * 0.3 + Math.sin(t * 23.7 + s * 3) * 0.2;
function pathAt(t, keys) {   // Catmull-Rom through [t, Vector3] keys
  if (t <= keys[0][0]) return keys[0][1].clone();
  for (let i = 0; i < keys.length - 1; i++) {
    if (t <= keys[i + 1][0]) {
      const p0 = keys[Math.max(0, i - 1)][1], p1 = keys[i][1], p2 = keys[i + 1][1], p3 = keys[Math.min(keys.length - 1, i + 2)][1];
      const u = (t - keys[i][0]) / (keys[i + 1][0] - keys[i][0]), u2 = u * u, u3 = u2 * u;
      return p1.clone().multiplyScalar(2).add(p2.clone().sub(p0).multiplyScalar(u)).add(p0.clone().multiplyScalar(2).sub(p1.clone().multiplyScalar(5)).add(p2.clone().multiplyScalar(4)).sub(p3).multiplyScalar(u2))
        .add(p3.clone().sub(p0).add(p1.clone().multiplyScalar(3)).sub(p2.clone().multiplyScalar(3)).multiplyScalar(u3)).multiplyScalar(0.5);
    }
  }
  return keys[keys.length - 1][1].clone();
}
function trackAt(t, keys) {  // eased hops between [t, value] keys (numbers or vectors)
  if (t <= keys[0][0]) return typeof keys[0][1] === 'number' ? keys[0][1] : keys[0][1].clone();
  for (let i = 1; i < keys.length; i++) if (t <= keys[i][0]) {
    const k = sineIO((t - keys[i - 1][0]) / (keys[i][0] - keys[i - 1][0])), a = keys[i - 1][1], b = keys[i][1];
    return typeof a === 'number' ? lerp(a, b, k) : a.clone().lerp(b, k);
  }
  const l = keys[keys.length - 1][1]; return typeof l === 'number' ? l : l.clone();
}

// ============================================================ key places
const BESIDE = V(0.48, 0, -0.27), OFC = V(0.8, 0, -3.75), DOOR_OUT = V(1.12, 0, -7.45), FIGHT = V(-0.45, 0, -3.4);
const GUN_REST = V(-0.92, 0.035, -2.8), CAR_X = 1.2, CAR_Z = -10.3;
const HANDLE = V(CAR_X + 0.95, 0.88, CAR_Z - 0.96), REAR_WIN = V(CAR_X + 0.73, 1.24, CAR_Z - 0.83), KEYS = V(CAR_X - 0.68, 1.12, CAR_Z - 0.83);
const unwrapNear = (a, ref) => a + 360 * Math.round((ref - a) / 360);
const P9 = V(2.75, 0, -11.95), P10 = V(5.0, 0, -10.5), P11 = V(2.95, 0, -11.85);

// ============================================================ CAMERA
const RUN = [   // escape route: around the counter, out the door, across the lot
  [42.0, V(0, EYE, 0.2)], [42.8, V(0.72, EYE - 0.02, 0.05)], [43.6, V(1.3, EYE - 0.03, -0.35)], [45.0, V(1.33, EYE - 0.03, -2.4)],
  [46.6, V(1.2, EYE - 0.03, -4.4)], [48.4, V(0.95, EYE - 0.03, -6.2)], [49.6, V(0.8, EYE - 0.03, -7.2)], [51.0, V(0.35, EYE - 0.04, -7.85)],
  [52.6, V(-0.25, EYE - 0.04, -8.0)], [54.4, V(-0.85, EYE - 0.04, -8.25)], [57.0, V(-1.5, EYE - 0.04, -8.7)], [59.8, V(-2.25, EYE - 0.04, -9.7)],
  [62.6, V(-2.75, EYE - 0.04, -10.9)], [65.6, V(-3.1, EYE - 0.04, -12.3)], [68.4, V(-3.3, EYE - 0.04, -13.6)], [69.9, V(-3.36, EYE - 0.02, -14.05)],
];
const runPos = t => pathAt(t, RUN);
function runCam(t) {
  const p = runPos(t), q = runPos(t + 0.25), pq = runPos(t - 0.25);
  let yaw = camYawTo(pq, q);
  if (t > 50.2) yaw = lerp(yaw, camYawTo(p, V(-3.2, 0, -22)), sineIO(seg(t, 50.2, 51.6)));
  if (t < 42.6) yaw = lerp(-12, yaw, sineIO(seg(t, 42.0, 42.6)));
  yaw += 38 * sineIO(seg(t, 44.6, 45.2)) * (1 - sineIO(seg(t, 46.0, 46.6)));      // glance left at the fight
  yaw += 22 * sineIO(seg(t, 63.8, 64.4)) * (1 - sineIO(seg(t, 65.2, 65.9)));      // glance right at the cruiser
  const stop = sineIO(seg(t, 69.3, 69.9));
  const ph = t * 2.7 * Math.PI * 2, amp = 1 - stop;
  p.y += (0.045 * Math.abs(Math.sin(ph)) - 0.02) * amp + (t > 45.2 && t < 45.9 ? 0.13 * Math.sin(seg(t, 45.2, 45.9) * Math.PI) : 0);
  return { x: p.x, y: p.y, z: p.z, yaw: yaw + noise(t, 1) * 1.6 * amp, pitch: -4 + 1.6 * Math.sin(ph * 2) * amp + noise(t, 2) * 1.2 * amp + 5 * stop * Math.exp(-(t - 69.9) * 3) * (t > 69.9),
    roll: 1.4 * Math.sin(ph) * amp + noise(t, 3) * 0.8 * amp, f: 520 };
}
const CAMK = [];
const K = (t0, t1, v, e = 's') => CAMK.push({ t0, t1, v, e });
const START = { yaw: -32, pitch: -34, x: 0.04, y: 1.12, z: 0.08, f: 600, roll: 0 };
// Scene 1 — continuation of the Episode 1 freeze frame
K(0.0, 1.0, { pitch: -36, f: 640 }, 'in');
K(1.22, 1.45, { pitch: -38 }, 'out');
K(2.0, 5.6, { pitch: -33, f: 600 }, 'lin');
K(5.9, 6.25, { yaw: -61, pitch: -9, x: 0, y: EYE, z: 0, f: 600 }, 'snap');                 // whip to Maya
K(9.6, 9.75, { yaw: -58 }, 'out'); K(10.2, 10.8, { yaw: -50, pitch: -7 });
// Scene 2
K(14.9, 15.25, { yaw: -9, pitch: -1, f: 560 }, 'snap');                                      // the officer storms in
K(18.9, 20.5, { z: 0.85, pitch: -3, yaw: -14, f: 540 });                                       // back up against the cigarette rack
K(20.5, 23.9, { yaw: -18 }, 'lin');
const TRACK = [   // chaotic handheld follows the fight (Scene 2, shot 4)
  [24.0, V(0.48, 1.45, -0.27)], [24.8, V(0.42, 1.35, -0.75)], [25.8, V(0.62, 1.4, -2.3)], [26.7, V(0.72, 1.45, -3.2)],
  [27.5, V(0.15, 0.55, -3.3)], [28.4, V(-0.55, 1.0, -3.4)], [33.8, V(-0.5, 0.65, -3.4)],
];
// Scene 2, shot 5: the gun under the shelf, then the open door
K(34.0, 34.4, { yaw: 17, pitch: -27, f: 1150, x: 0, y: EYE, z: 0.2 }, 'snap');
K(34.4, 36.9, { f: 1300 }, 'lin');
K(37.0, 37.35, { yaw: -12, pitch: -1, f: 540 }, 'snap');
// Scene 4 — after the run (values continue from the end of the run)
const AFTER = [];
const A = (t0, t1, v, e = 's') => AFTER.push({ t0, t1, v, e });
const Y8 = camYawTo(V(-3.36, 0, -14.05), REAR_WIN), Y9 = unwrapNear(camYawTo(P9, REAR_WIN), Y8), YK = unwrapNear(camYawTo(P9, KEYS), Y9) - 3;
const Y10 = unwrapNear(camYawTo(P10, V(1.0, 0, -6.4)), YK), Y11 = unwrapNear(camYawTo(P11, V(1.6, 0, -9.6)), Y10);
A(70.0, 70.35, { yaw: Y8 - 2, pitch: camPitchTo(V(-3.36, EYE, -14.05), REAR_WIN), f: 1250 }, 'snap');   // whip right: the cruiser's rear window
A(70.35, 79.6, { f: 1380 }, 'lin');
A(79.8, 83.0, { x: P9.x, z: P9.z, y: EYE - 0.02, f: 560 });                                      // steps closer
A(80.4, 83.0, { yaw: Y9, pitch: camPitchTo(V(P9.x, EYE, P9.z), REAR_WIN) });
A(85.0, 86.4, { yaw: YK, pitch: camPitchTo(V(P9.x, EYE, P9.z), KEYS), f: 1250 });                // keys in the ignition
A(87.9, 88.35, { yaw: Y10, pitch: -3, f: 700 }, 'snap');                                         // whip back to the station…
A(87.9, 89.4, { x: P10.x, z: P10.z });                                                            // …stepping clear of the trunk
A(89.4, 97.8, { f: 700 }, 'lin');
A(98.0, 98.8, { x: P11.x, z: P11.z, yaw: Y11, pitch: -15, f: 520 });                              // hand on the handle, officer over the roof
function camAt(tReal) {
  const t = Math.min(tReal, FREEZE);
  let c;
  if (t >= 42.0 && t < 69.95) c = runCam(t);
  else if (t >= 69.95) {
    c = runCam(69.95);
    for (const k of AFTER) { if (t < k.t0) break; const prev = { ...c }, kk = ease[k.e](seg(t, k.t0, k.t1)); for (const key in k.v) c[key] = lerp(prev[key], k.v[key], kk); }
    c.roll *= 1 - seg(t, 69.95, 70.3);
  } else {
    c = { ...START };
    for (const k of CAMK) { if (t < k.t0) break; const prev = { ...c }, kk = ease[k.e](seg(t, k.t0, k.t1)); for (const key in k.v) c[key] = lerp(prev[key], k.v[key], kk); }
    if (t >= 23.9 && t < 34.0) {   // tracking override with handheld shake
      const tgt = trackAt(t, TRACK), from = V(c.x, c.y, c.z), w = sineIO(seg(t, 23.9, 24.25));
      c.yaw = lerp(c.yaw, camYawTo(from, tgt), w) + noise(t, 4) * 2.2; c.pitch = lerp(c.pitch, camPitchTo(from, tgt), w) + noise(t, 5) * 1.6; c.roll = noise(t, 6) * 1.5;
      const fwd = sineIO(seg(t, 23.9, 24.6)); c.z = lerp(c.z, 0.2, fwd); c.y = EYE - 0.04 * fwd;
      c.f = lerp(540, 760, sineIO(seg(t, 25.4, 26.4))) - 60 * sineIO(seg(t, 28.2, 28.5)) + 60 * sineIO(seg(t, 29.0, 30.0));
    }
  }
  // impacts
  for (const [t0, a] of [[1.25, 0.8], [9.6, 1.6], [26.7, 1.2], [28.4, 1.8], [66.0, 0.5], [66.4, 0.5], [66.8, 0.6], [72.0, 0.5], [72.4, 0.5], [72.8, 0.6]]) {
    if (t > t0 && t < t0 + 0.45) { const d = t - t0; c.yaw += a * Math.exp(-d * 11) * Math.sin(d * 55); c.pitch += a * 0.7 * Math.exp(-d * 11) * Math.cos(d * 47); }
  }
  if (tReal > FREEZE) c.f *= 1 + 0.012 * Math.pow(Math.max(0, Math.sin((tReal - FREEZE) * Math.PI * 2 * 1.15)), 8);
  c.roll = c.roll || 0;
  return c;
}

// ============================================================ products exploding off the shelf (precomputed physics)
const PARTS = [];
(function buildParticles() {
  let sd = 21; const r = () => (sd = (sd * 16807) % 2147483647) / 2147483647;
  const cols = ['#e33b2f', '#f2b51e', '#2f73d8', '#2fa64d', '#f07f22', '#8d4ad0', '#e65b9c', '#1fb3b0'];
  for (let i = 0; i < 46; i++) {
    const bottle = i % 3 === 0, col = cols[i % cols.length];
    const m = bottle ? cyl(0.035, 0.035, 0.21, col, 0, -5, 0) : box(0.17, 0.23, 0.06, col, 0, -5, 0);
    const p = V(-0.82, 0.3 + r() * 1.05, -3.0 - r() * 1.2), v = V(0.6 + r() * 2.6, 0.4 + r() * 2.4, (r() - 0.5) * 2.4), w = V((r() - 0.5) * 18, (r() - 0.5) * 18, (r() - 0.5) * 18);
    const frames = []; const dt = 1 / 120; let rot = V(0, 0, 0), rest = false;
    for (let k = 0; k < 120 * 6; k++) {
      if (!rest) {
        v.y -= 9.8 * dt; p.addScaledVector(v, dt); rot.addScaledVector(w, dt);
        if (p.y < 0.04) { p.y = 0.04; v.y *= -0.28; v.x *= 0.55; v.z *= 0.55; w.multiplyScalar(0.5); if (Math.abs(v.y) < 0.25 && v.length() < 0.3) { rest = true; rot.x = bottle ? Math.PI / 2 : -Math.PI / 2 + (r() - 0.5) * 0.3; } }
      }
      if (k % 4 === 0) frames.push([p.x, p.y, p.z, rot.x, rot.y, rot.z]);
    }
    PARTS.push({ m, frames });
  }
})();
const BURST = 28.4;
function particlesAt(t) {
  for (const P of PARTS) {
    if (t < BURST) { P.m.visible = false; continue; }
    P.m.visible = true; const f = P.frames[Math.min(P.frames.length - 1, Math.floor((t - BURST) * 30))];
    P.m.position.set(f[0], f[1], f[2]); P.m.rotation.set(f[3], f[4], f[5]);
  }
}
// the officer's pistol once it's knocked away
const gunProp = new THREE.Group(); scene.add(gunProp);
box(0.032, 0.036, 0.17, '#1a1b20', 0, 0.02, -0.07, gunProp); box(0.028, 0.09, 0.04, '#1f2026', 0, -0.02, 0.0, gunProp).rotation.x = 0.25;
gunProp.scale.setScalar(1.5);
{ const gl = new THREE.Sprite(new THREE.SpriteMaterial({ map: (await import('./core.js')).glowTex, color: '#ffffff', transparent: true, blending: THREE.AdditiveBlending, depthWrite: false })); gl.scale.set(0.12, 0.12, 1); gl.position.set(0.01, 0.04, -0.1); gunProp.add(gl); gl.material.userData.outlineParameters = { visible: false }; }
function gunPropAt(t, hand) {
  gunProp.visible = t > 26.72 && t < 91.4;
  if (!gunProp.visible) return;
  const land = V(0.32, 0.035, -3.35);
  if (t < 27.0) { const k = seg(t, 26.72, 27.0); gunProp.position.copy(hand.clone().lerp(land, k)); gunProp.position.y += Math.sin(k * Math.PI) * 0.35; gunProp.rotation.set(k * 6, k * 9, 0); }
  else { const k = easeOut(seg(t, 27.0, 27.9)); gunProp.position.copy(land.clone().lerp(GUN_REST, k)); gunProp.rotation.set(Math.PI / 2, 9 + k * 7, 0); }
}

// ============================================================ MAYA performance
function setLimbsVis(ch, v) { for (const L of [ch.armL, ch.armR, ch.legL, ch.legR]) { L.a.visible = L.j.visible = L.b.visible = v; } (ch.feet || ch.boots).forEach(f => f.visible = v); }
function gait(t, root, yaw, speed, phase0 = 0) {
  const ph = phase0 + t * (speed > 1.5 ? 2.7 : 1.8) * Math.PI * 2;
  const fwd = V(Math.sin(yaw), 0, Math.cos(yaw)), rt = V(Math.cos(yaw), 0, -Math.sin(yaw)), stride = Math.min(0.42, 0.18 * speed);
  const off = s => ph + (s > 0 ? Math.PI : 0);
  const foot = s => root.clone().add(rt.clone().multiplyScalar(s * 0.1)).add(fwd.clone().multiplyScalar(stride * Math.sin(off(s)))).add(V(0, Math.max(0, Math.cos(off(s))) * 0.13 * Math.min(1, speed), 0));
  const hand = s => root.clone().add(rt.clone().multiplyScalar(s * 0.26)).add(fwd.clone().multiplyScalar(-stride * 0.8 * Math.sin(off(s)) + 0.05)).add(V(0, 0.95 + 0.06 * Math.abs(Math.sin(ph)), 0));
  return { footL: foot(-1), footR: foot(1), handL: hand(-1), handR: hand(1), bob: 0.03 * Math.abs(Math.sin(ph)) };
}
function lookAtPt(from, rootYaw, twist, lean, headH, pt) {
  const dir = V(pt.x - from.x, pt.y - headH, pt.z - from.z);
  const hy = Math.max(-1.35, Math.min(1.35, wrapA(Math.atan2(dir.x, dir.z) - rootYaw - twist)));
  return { headYaw: hy, headPitch: Math.max(-0.7, Math.min(0.7, -Math.atan2(dir.y, Math.hypot(dir.x, dir.z)) - lean)) };
}
const copHead = () => cop.head.getWorldPosition(V(0, 0, 0));
function mayaAt(t) {
  const mouth = mouthOf('maya', t);
  const rage = { eyes: 1.0, worry: -1.5, cold: 0.32, pupil: 0.85, mouthBase: 0.3 }, cold = { eyes: 0.95, worry: 0, cold: 0.55, pupil: 1.05, mouthBase: 0.02 };
  let p;
  maya.torso.updateMatrixWorld();
  if (t < 24.2) {
    const root = BESIDE.clone(); const facePOV = yawTo(BESIDE, V(0, 0, 0.1)), faceCop = yawTo(BESIDE, OFC);
    const turn = sineIO(seg(t, 9.7, 10.4)) * 0.6 + sineIO(seg(t, 14.6, 15.4)) * 0.4;
    const yaw = lerp(facePOV, faceCop, turn), hipY = 0.94;
    const raise = sineIO(seg(t, 6.3, 6.9)), flinch = t > 9.6 && t < 10.2 ? Math.sin(seg(t, 9.6, 10.2) * Math.PI) : 0;
    const pocketOut = maya.torso.localToWorld(V(0.1, 0.36, 0.34));
    const toCam = camera.position.clone().sub(V(root.x, 1.35, root.z)).setY(0).normalize();
    const atPOV = V(root.x, 1.3, root.z).add(toCam.multiplyScalar(0.36)).add(V(0.04, 0, 0)), atCop = loc(root, yaw, 0.18, 1.32, 0.5);
    const handR = pocketOut.clone().lerp(t < 14.6 ? atPOV : atCop, raise);
    const tgt = t < 9.6 ? camera.position.clone() : t < 15.4 ? V(1.2, 1.6, -7) : copHead();
    p = { x: root.x + flinch * 0.03, z: root.z, yaw, hipY: hipY - flinch * 0.03, lean: 0.06 + flinch * -0.1, handL: loc(root, yaw, -0.22, hipY + 0.1 + 0.2 * raise, 0.18), handR,
      handRdir: (t < 14.6 ? camera.position.clone().sub(atPOV).normalize().add(V(0, 0.5, 0)) : V(0, 0.4, 1).applyAxisAngle(V(0, 1, 0), yaw)), footL: loc(root, yaw, -0.11, 0, 0), footR: loc(root, yaw, 0.12, 0, 0.04), knife: true,
      glint: t > 6.7 && t < 7.2 ? Math.sin(seg(t, 6.7, 7.2) * Math.PI) : 0, expr: t < 6.3 ? cold : { ...rage, eyes: 1.12 + 0.3 * flinch } };
    Object.assign(p, lookAtPt(root, yaw, 0, p.lean, hipY + 0.72, tgt));
  } else if (t < 26.7) {   // vaults the counter and charges the officer
    const vault = seg(t, 24.2, 25.3), runK = seg(t, 25.3, 26.6);
    let root, hipY, lean, yaw;
    if (t < 25.3) {
      root = BESIDE.clone().lerp(V(0.38, 0, -1.0), sineIO(vault)); hipY = 0.94 + 0.38 * Math.sin(vault * Math.PI); lean = 0.5 * Math.sin(vault * Math.PI) + 0.1; yaw = yawTo(BESIDE, OFC);
      p = { x: root.x, z: root.z, yaw, hipY, lean, handL: V(0.3, CT + 0.02 + 0.2 * vault, -0.5), handR: V(0.45, CT + 0.08 + 0.2 * vault, -0.48), knife: true,
        footL: loc(root, yaw, -0.12, 0.25 + 0.45 * Math.sin(vault * Math.PI), -0.2), footR: loc(root, yaw, 0.12, 0.25 + 0.45 * Math.sin(vault * Math.PI), -0.1), expr: rage };
    } else {
      root = V(0.38, 0, -1.0).lerp(V(0.66, 0, -3.05), runK); yaw = yawTo(V(0.38, 0, -1), OFC);
      const gt = gait(t, root, yaw, 2.6);
      p = { x: root.x, z: root.z, yaw, hipY: 0.9 - gt.bob, lean: 0.35, ...gt, handR: loc(root, yaw, 0.18, 1.3, 0.45), knife: true, expr: rage };
    }
    Object.assign(p, lookAtPt(V(p.x, 0, p.z), p.yaw, 0, p.lean, p.hipY + 0.72, copHead()));
  } else if (t < 70) {     // slash, grapple, crash into the aisle, wrestle on the floor
    const fall = sineIO(seg(t, 28.4, 29.0)), wr = t > 29 ? 1 : 0;
    const root = V(0.66, 0, -3.05).lerp(V(-0.35, 0, -3.38), sineIO(seg(t, 27.0, 28.5)));
    root.x += wr * 0.06 * Math.sin(t * 3.1); root.z += wr * 0.05 * Math.sin(t * 2.3);
    const yaw = 2.6 + wr * 0.25 * Math.sin(t * 1.7);
    const hipY = lerp(0.9, 0.48, fall) + wr * 0.04 * Math.sin(t * 5);
    const slash = sineIO(seg(t, 26.6, 26.85));
    const ch = cop.torso.localToWorld(V(0, 0.5, 0));
    const handR = t < 27.0 ? loc(root, yaw, 0.4 - 0.7 * slash, 1.35 - 0.3 * slash, 0.5) : ch.clone().add(V(0.12, 0.05 * Math.sin(t * 6), 0));
    p = { x: root.x, z: root.z, yaw, hipY, lean: lerp(0.3, 0.75, fall), handL: ch.clone().add(V(-0.15, 0.05 * Math.cos(t * 5), 0.05)), handR,
      footL: loc(root, yaw, -0.18, 0, lerp(0, -0.35, fall)), footR: loc(root, yaw, 0.18, 0, lerp(0.05, -0.32, fall)), knife: t < 29.2, expr: { ...rage, eyes: 1.2 } };
    Object.assign(p, lookAtPt(root, yaw, 0, p.lean, hipY + 0.6, ch));
  } else {                 // motionless on the floor
    const root = V(0.35, 0, -3.65), yaw = 1.2;
    p = { x: root.x, z: root.z, yaw, hipY: 0.17, lean: 1.5, headYaw: 0.9, headPitch: 0.2, handL: loc(root, yaw, -0.35, 0.05, 0.55), handR: loc(root, yaw, 0.4, 0.05, 0.4),
      footL: loc(root, yaw, -0.12, 0.05, -0.85), footR: loc(root, yaw, 0.1, 0.05, -0.8), knife: false, expr: { eyes: 0.12, worry: 0.2, mouthBase: 0.08 } };
  }
  poseMaya(maya, p, t, Math.min(1, mouth * 1.1));
}

// ============================================================ OFFICER performance
function copAt(t) {
  const mouth = mouthOf('cop', t);
  let root, yaw, hipY = 1.02, lean = 0, gun = true, flash = false, flashOn = 0, sp = 0, handR, handL, dirR = null, dirL = null, footL, footR, headTgt = camera.position.clone(), blood = t > 26.72;
  cop.torso.updateMatrixWorld();
  const mHead = maya.head.getWorldPosition(V(0, 0, 0));
  if (t < 9.6) { root = DOOR_OUT.clone(); yaw = Math.PI * 0.02; }
  else if (t < 12.5) { root = DOOR_OUT.clone().lerp(OFC, sineIO(seg(t, 9.6, 12.5))); yaw = yawTo(DOOR_OUT, OFC) * 0 + yawTo(OFC, BESIDE); sp = 1.8; }
  else if (t < 26.7) {
    root = OFC.clone().add(V(0, 0, -0.25 * sineIO(seg(t, 25.4, 26.5)))); yaw = yawTo(root, mHead);
  } else if (t < 28.4) { root = OFC.clone().add(V(0, 0, -0.25)).lerp(FIGHT, sineIO(seg(t, 27.0, 28.4))); yaw = yawTo(root, V(1, 0, -2)); gun = false; }
  else if (t < 70) { root = FIGHT.clone().add(V(0.05 * Math.sin(t * 2.7), 0, 0.04 * Math.sin(t * 1.9))); yaw = -1.5; gun = false; }
  else if (t < 88.5) { root = V(-0.25, 0, -4.1); yaw = 0.9; gun = false; }
  else if (t < 89.5) { root = V(-0.25, 0, -4.1); yaw = lerp(0.9, -0.3, sineIO(seg(t, 88.5, 89.5))); gun = false; }
  else if (t < 91.6) { root = V(-0.25, 0, -4.1).lerp(V(-0.62, 0, -2.85), sineIO(seg(t, 89.5, 91.0))); yaw = -0.4; gun = t > 91.4; sp = t < 91 ? 1.0 : 0; }
  else if (t < 95.8) { const k = seg(t, 91.6, 95.8); root = V(-0.62, 0, -2.85).lerp(V(1.0, 0, -6.6), Math.min(1, k * 1.3)).lerp(V(1.22, 0, -7.75), Math.max(0, k * 1.3 - 0.3) / 1.0 * 0.77); yaw = yawTo(root, camera.position); sp = 1.4; flash = t > 93.5; flashOn = flash ? 1 : 0; }
  else { root = V(1.22, 0, -7.75); yaw = yawTo(root, camera.position); flash = true; flashOn = 1; }
  if (t >= 28.4 && t < 70) {          // on his back, fighting her off
    const fall = sineIO(seg(t, 28.4, 29.0)); hipY = lerp(0.95, 0.24, fall); lean = lerp(-0.2, -1.42, fall);
    const mT = maya.torso.localToWorld(V(0, 0.45, 0));
    handR = mT.clone().add(V(0.12, 0.03 * Math.sin(t * 7), 0)); handL = mT.clone().add(V(-0.14, 0.03 * Math.cos(t * 6), 0));
    footL = loc(root, yaw, -0.15, 0.05 + 0.12 * Math.max(0, Math.sin(t * 4)), 0.8); footR = loc(root, yaw, 0.15, 0.05 + 0.12 * Math.max(0, Math.cos(t * 4.4)), 0.75);
    headTgt = mHead;
  } else if (t >= 70 && t < 89.5) {   // kneeling, catching his breath, then getting up
    const up = sineIO(seg(t, 88.5, 89.5)); hipY = lerp(0.52, 1.02, up); lean = lerp(0.55, 0.05, up);
    handR = loc(root, yaw, 0.25, lerp(0.6, 0.95, up), 0.3); handL = loc(root, yaw, -0.3, lerp(0.75, 1.0, up), 0.1);
    footL = loc(root, yaw, -0.14, 0, lerp(-0.4, 0, up)); footR = loc(root, yaw, 0.14, 0, lerp(0.25, 0.04, up)); headTgt = V(0.35, 0.3, -3.65);
  } else if (t >= 26.7 && t < 28.4) { // slashed: arms up
    const k = Math.sin(seg(t, 26.7, 27.2) * Math.PI);
    handR = loc(root, yaw, 0.3, 1.2 + 0.3 * k, 0.35); handL = loc(root, yaw, -0.25, 1.15 + 0.35 * k, 0.3); dirL = V(0, 1, 0.3);
  }
  if (!handR) {
    const aimAt = t < 26.7 ? mHead : camera.position.clone();
    const sh = cop.torso.localToWorld(V(0.1, 0.56, 0)); const ad = aimAt.clone().sub(sh).normalize();
    if (gun && t > 9.9 && !(t > 89.5 && t < 91.6)) { handR = sh.clone().add(ad.clone().multiplyScalar(0.55)); dirR = ad; if (!flash) { handL = handR.clone().add(V(-0.06, -0.05, 0).applyAxisAngle(V(0, 1, 0), yaw)); } }
    else if (t > 90.8 && t < 91.6) { handR = GUN_REST.clone().add(V(0, 0.05, 0)); hipY = lerp(1.02, 0.6, Math.sin(seg(t, 90.8, 91.6) * Math.PI)); lean = 0.5 * Math.sin(seg(t, 90.8, 91.6) * Math.PI); }
    else handR = loc(root, yaw, 0.3, 0.95, 0.12);
  }
  if (!handL) { handL = flash ? cop.torso.localToWorld(V(-0.22, 0.62, 0.35)) : loc(root, yaw, -0.3, 0.95, 0.12); }
  if (flash) dirL = camera.position.clone().sub(handL).normalize();
  if (!footL) {
    if (sp > 0) { const gt = gait(t, root, yaw, sp, 0.4); footL = gt.footL; footR = gt.footR; hipY -= gt.bob * 0.6; }
    else { footL = loc(root, yaw, -0.12, 0, 0); footR = loc(root, yaw, 0.13, 0, 0.04); }
  }
  const p = { x: root.x, z: root.z, yaw, hipY, lean, handL, handR, handLdir: dirL, handRdir: dirR, footL, footR, flash, flashOn, gun, blood, badge: false };
  const dir = headTgt.clone().sub(V(root.x, hipY + 0.8, root.z));
  p.headYaw = Math.max(-1, Math.min(1, wrapA(Math.atan2(dir.x, dir.z) - yaw))); p.headPitch = Math.max(-0.8, Math.min(0.8, -Math.atan2(dir.y, Math.hypot(dir.x, dir.z)) - lean));
  poseOfficer(cop, p, t, Math.min(1, mouth * 1.2));
  cop.face.shadow.material.opacity = t > 88 ? 0.6 : 0.4;
  return { flash };
}

// ============================================================ POV hands
const REST_R = V(0.2, CT + 0.035, -0.3), REST_L = V(-0.26, CT + 0.035, -0.3);
function applyHand(h, s) { h.g.visible = s.vis; if (s.vis) { h.g.position.copy(s.pos); h.g.quaternion.copy(basisQuat(s.fd, s.pn)); poseHand(h, s.pose); h.g.updateMatrixWorld(); } }
function handsAt(t) {
  const R = { pos: REST_R.clone(), fd: V(-0.15, -0.25, -1), pn: V(0, -1, 0), pose: 'rest', vis: false };
  const L = { pos: REST_L.clone(), fd: V(0.15, -0.25, -1), pn: V(0, -1, 0), pose: 'rest', vis: false };
  const cap = lockBtn.cap.getWorldPosition(V(0, 0, 0)), tt = Math.min(t, FREEZE);
  if (t < 2.6) {          // trembling hover → slam the button
    const tr = V(Math.sin(tt * 53) * 0.004 + Math.sin(tt * 31) * 0.003, Math.sin(tt * 47) * 0.004, 0).multiplyScalar(t < 1.0 ? 1 : 0);
    const hover = cap.clone().add(V(0.0, 0.115, 0.06)).add(tr), press = cap.clone().add(V(0, 0, 0.048));
    const k = sineIO(seg(t, 0.9, 1.22)), back = sineIO(seg(t, 1.9, 2.6));
    R.pos = hover.clone().lerp(press, k).lerp(REST_R, back); R.vis = true;
    R.fd = V(0.0, 0.75, -0.6).lerp(V(0.05, 1, -0.15), k).lerp(V(-0.15, -0.25, -1), back); R.pn = V(0, -0.4, -1).lerp(V(0, 0, -1), k).normalize(); R.pose = k > 0.5 ? 'flat' : 'hover';
  }
  if (t > 19.0 && t < 24.0) {   // hands up against the rack
    const up = sineIO(seg(t, 19.0, 19.4)) * (1 - sineIO(seg(t, 23.4, 24.0)));
    for (const [H, s] of [[R, 1], [L, -1]]) {
      const tr = V(Math.sin(t * (37 + s * 4)) * 0.003, Math.sin(t * (29 - s * 5)) * 0.003, 0);
      H.pos = camLocal(s * 0.15, -0.09, -0.34).add(tr).lerp(camLocal(s * 0.22, -0.55, -0.2), 1 - up); H.fd = camDir(s * 0.1, 1, -0.25); H.pn = camDir(0, 0, -1); H.pose = 'open'; H.vis = up > 0.05;
    }
  }
  if (t > 42.0 && t < 69.6) {   // pumping arms while sprinting
    const ph = t * 2.7 * Math.PI;
    for (const [H, s] of [[R, 1], [L, -1]]) {
      const sw = Math.sin(ph + (s > 0 ? 0 : Math.PI));
      H.pos = camLocal(s * 0.24, -0.5 + 0.17 * Math.max(0, sw), -0.32 - 0.06 * sw); H.fd = camDir(-s * 0.3, 0.6, -1); H.pn = camDir(-s * 0.8, -0.2, 0); H.pose = 'grip'; H.vis = sw > -0.2;
    }
  }
  if (t > 98.0) {               // hovering inches from the rear door handle
    const k = sineIO(seg(t, 98.0, 98.8)), tr = V(Math.sin(tt * 53) * 0.005 + Math.sin(tt * 31) * 0.003, Math.sin(tt * 47) * 0.004, Math.sin(tt * 41) * 0.003);
    R.pos = camLocal(0.25, -0.5, -0.25).lerp(HANDLE.clone().add(V(0.05, 0.03, 0.1)).add(tr), k); R.fd = V(-0.6, -0.1, -0.8); R.pn = V(-0.2, -0.3, -1).normalize(); R.pose = 'hover'; R.vis = true;
  }
  return { R, L };
}

// ============================================================ lens rain (screen space, outdoors)
const fx = document.getElementById('rainfx').getContext('2d');
let sdr = 5; const rr = () => (sdr = (sdr * 16807) % 2147483647) / 2147483647;
const STREAKS = Array.from({ length: 170 }, () => ({ x: rr() * 760, y: rr() * 1280, l: 40 + rr() * 90, s: 1800 + rr() * 1400, a: 0.12 + rr() * 0.22 }));
const DROPS = Array.from({ length: 34 }, () => ({ x: rr() * 720, y: rr() * 1280, r: 6 + rr() * 16, t0: rr() * 12, life: 2 + rr() * 4 }));
function lensRain(t, amt) {
  fx.clearRect(0, 0, 720, 1280);
  if (amt <= 0) return;
  fx.lineCap = 'round';
  for (const s of STREAKS) {
    const y = ((s.y + t * s.s) % 1500) - 150, x = s.x - y * 0.08;
    fx.strokeStyle = `rgba(200,215,235,${s.a * amt})`; fx.lineWidth = 2; fx.beginPath(); fx.moveTo(x, y); fx.lineTo(x - s.l * 0.08, y + s.l); fx.stroke();
  }
  for (const d of DROPS) {
    const age = ((t - d.t0) % (d.life + 1) + d.life + 1) % (d.life + 1); if (age > d.life) continue;
    const a = amt * Math.min(1, age * 3) * (1 - age / d.life) * 0.55, y = d.y + age * 18;
    const g = fx.createRadialGradient(d.x - d.r * 0.3, y - d.r * 0.3, 1, d.x, y, d.r);
    g.addColorStop(0, `rgba(255,255,255,${a})`); g.addColorStop(0.5, `rgba(190,205,230,${a * 0.4})`); g.addColorStop(1, 'rgba(190,205,230,0)');
    fx.fillStyle = g; fx.beginPath(); fx.arc(d.x, y, d.r, 0, 7); fx.fill();
  }
}

// ============================================================ HUD
const titleEl = document.getElementById('title'), subEl = document.getElementById('subtxt'), ctaEl = document.getElementById('cta');
function hudAt(t) {
  const a = easeOut(seg(t, 0.15, 0.55)), out = seg(t, 5.6, 6.0);
  titleEl.style.opacity = a * (1 - out); titleEl.style.transform = `translateX(${-12 * (1 - a)}px)`;
  let sub = null;
  for (const l of DLG.lines) for (const c of l.chunks) if (t >= c.t0 && t < c.t1) sub = { c, spk: l.spk };
  subEl.textContent = sub ? sub.c.text : ''; subEl.className = sub ? sub.spk : '';
  if (sub) subEl.style.transform = `translateX(-50%) scale(${0.91 + 0.09 * easeOut(seg(t, sub.c.t0, sub.c.t0 + 0.1))})`;
  document.getElementById('sub').style.top = t > 99.6 ? '1150px' : '839px';
  ctaEl.style.display = t > 99.7 ? 'block' : 'none';
  if (t > 99.7) {
    const k = easeOut(seg(t, 99.7, 100.0));
    ctaEl.querySelector('.q').style.transform = `scale(${0.85 + 0.15 * k})`; ctaEl.style.opacity = k;
    ctaEl.querySelectorAll('.btn').forEach((b, i) => { const kb = easeOut(seg(t, 99.9 + i * 0.15, 100.2 + i * 0.15)); b.style.transform = `scale(${0.8 + 0.2 * kb})`; b.style.opacity = kb; });
  }
}

// ============================================================ render
function policeAt(t) {
  const ph = (t * 2.15) % 1, half = ph < 0.5, q = (ph % 0.5) / 0.5, pulse = (q < 0.18 ? 1 : q < 0.3 ? 0.15 : q < 0.48 ? 1 : 0.2);
  return { on: 1, red: half ? pulse : 0.08, blue: half ? 0.08 : pulse };
}
const PHONE_COUNTER = { pos: V(0.06, CT + 0.0045, -0.33), rot: new THREE.Euler(-Math.PI / 2, 0, 0.12) };
window.setHud = on => { document.getElementById('hud').style.display = on ? 'block' : 'none'; document.getElementById('rainfx').style.display = on ? 'block' : 'none'; };
window.renderAt = (tReal) => {
  const t = Math.min(tReal, FREEZE);
  drawRain(t);
  const c = camAt(tReal);
  camera.position.set(c.x, c.y, c.z); camera.rotation.set(c.pitch * D2R, c.yaw * D2R, (c.roll || 0) * D2R); camera.updateMatrixWorld(); setFocal(c.f);
  const outside = c.z < -7.05;
  scene.background.set(outside ? '#04060b' : C.ceiling);
  body.visible = c.y > 1.35 && c.z > -0.15 && c.z < 0.3 && Math.abs(c.x) < 0.3; body.position.set(c.x, 0, c.z * 0.5); body.rotation.y = c.yaw * D2R * 0.35;
  // door: flung open at 9.6 and left open; lock released at 1.22
  setDoor('L', t < 9.6 ? 0 : 1.42 * easeOut(seg(t, 9.6, 9.8)) - 0.06 * Math.sin(seg(t, 9.8, 10.4) * Math.PI));
  setLocked(t < 1.22);
  lockBtn.cap.position.z = 0.01 - (t > 1.18 && t < 1.45 ? 0.008 : 0);
  phone.position.copy(PHONE_COUNTER.pos); phone.quaternion.setFromEuler(PHONE_COUNTER.rot);
  // cruiser: idling, driver door open, lights going
  car.g.position.set(CAR_X, 0, CAR_Z); car.g.visible = true; car.doorPivot.rotation.y = -1.1;
  const pol = policeAt(t);
  car.red.material.color.set(pol.red > 0.5 ? '#ff3a3a' : '#4a0c0c'); car.blue.material.color.set(pol.blue > 0.5 ? '#3a6bff' : '#0b1440');
  car.redGlow.material.opacity = pol.red; car.blueGlow.material.opacity = pol.blue;
  car.redPool.position.set(CAR_X + 0.2, 0.015, -9.0); car.bluePool.position.set(CAR_X + 0.2, 0.016, -9.0);
  car.redPool.material.opacity = 0.25 * pol.red; car.bluePool.material.opacity = 0.25 * pol.blue;
  car.headGlow.forEach(h => h.material.opacity = 1); car.beam.material.opacity = 0.06; car.groundPool.material.opacity = 0.1;
  car.palms.visible = t > 71.95; const pound = [72.0, 72.4, 72.8, 74.6, 75.0, 76.5, 76.9].reduce((a, k0) => a + Math.exp(-Math.pow((t - k0) / 0.06, 2)), 0);
  car.palms.position.z = 0.002 * pound; car.palms.scale.setScalar(1 + 0.06 * pound);
  car.keys.rotation.z = 0.25 * Math.sin(t * 3.2) * Math.exp(-Math.max(0, t - 85) * 0.05);
  car.truck.position.set(-45 + Math.max(0, t - 61) * 9.5, 0, -27);
  const facingDoor = outside ? 1 : Math.max(0, Math.cos((c.yaw + 9) * D2R)) * Math.max(0, Math.cos(c.pitch * D2R));
  lens.uniforms.policeAmt.value = (0.17 + 0.16 * facingDoor + (outside ? 0.12 : 0)) * Math.max(pol.red, pol.blue);
  lens.uniforms.policeCol.value.copy(pol.red >= pol.blue ? new THREE.Color(1, 0.12, 0.1) : new THREE.Color(0.12, 0.28, 1));
  lens.uniforms.policeDim.value = outside ? 0.42 : 0.3;
  amb.intensity = outside ? 1.7 : 2.15;
  // hands + arms
  const bf = new THREE.Matrix4().makeRotationY(c.yaw * D2R); bf.setPosition(c.x, c.y, c.z);
  const hs = handsAt(t); applyHand(handR, hs.R); applyHand(handL, hs.L);
  placeArm(armR, handR.g.localToWorld(V(0, 0.004, 0.045)), 1, bf, hs.R.vis);
  placeArm(armL, handL.g.localToWorld(V(0, 0.004, 0.045)), -1, bf, hs.L.vis);
  // characters, props, particles
  mayaAt(t);
  const cs = copAt(t);
  cop.hands[1].updateMatrixWorld();
  gunPropAt(t, cop.hands[1].getWorldPosition(V(0, 0, 0)));
  particlesAt(t);
  // flashlight glare (shot 10–11)
  lens.uniforms.glareAmt.value = 0;
  if (cs.flash && cop.flashlight.visible) {
    cop.flashlight.updateMatrixWorld();
    const lp = cop.flashlight.localToWorld(V(0, 0, -0.15)), ld = V(0, 0, -1).transformDirection(cop.flashlight.matrixWorld);
    const facing = Math.max(0, ld.dot(camera.position.clone().sub(lp).normalize())), sp = projectLens(lp);
    if (sp) { lens.uniforms.glarePos.value.copy(sp); lens.uniforms.glareAmt.value = Math.pow(facing, 6) * 0.55 * (1 + 0.06 * Math.sin(t * 40)); }
  }
  lens.uniforms.vign.value = 0.85 * easeOut(seg(tReal, FREEZE - 0.15, FREEZE + 0.4));
  lens.uniforms.flash.value = t > 9.6 && t < 9.75 ? 0.08 : 0;
  renderFrame();
  lensRain(t, outside ? 1 : (t > 9.6 && t < 15 ? 0 : 0));
  hudAt(tReal);
};
window.DURATION = DUR;
window.sceneReady = Promise.resolve(true);
