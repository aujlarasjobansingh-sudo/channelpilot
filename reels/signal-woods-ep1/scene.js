// THE SIGNAL IN THE WOODS — Episode 1. POV on a BMX, November 1986. Full ~97 s timeline.
import { THREE, scene, camera, setFocal, projectLens, renderFrame, lens, D2R, sineIO, sineIn, easeOut, seg, lerp } from './core.js';
import { buildSet, FENCE_X, HOLE_Z, RIFT, lamps, plantLights, windows, headlight, bike, walkie, woodsGlow, woodsLight, rift, creature, ash, ashBase } from './set.js';
import { makeHand, poseHand, makeArm, placeArm, basisQuat, makeLeo, poseMaya } from './chars.js';

const V = (x, y, z) => new THREE.Vector3(x, y, z);
await Promise.all([500, 600, 700, 800, 900].map(w => document.fonts.load(`${w} 40px Rubik`)));
const DLG = await (await fetch('out/dialogue.json')).json();
buildSet();
camera.far = 400; camera.updateProjectionMatrix();
scene.background = new THREE.Color('#050816');
const amb = new THREE.AmbientLight('#4a5c94', 1.5); scene.add(amb);
const moonL = new THREE.DirectionalLight('#9fb4ff', 1.0); moonL.position.set(-90, 95, -230).normalize().multiplyScalar(10); scene.add(moonL);
const leo = makeLeo();
const handR = makeHand(1), handL = makeHand(-1), armR = makeArm(), armL = makeArm();
handR.g.add(walkie.g); walkie.g.position.set(-0.035, -0.045, -0.03); walkie.g.rotation.set(0, 0, Math.PI / 2);
const FREEZE = 88.4, DUR = 97.0;

// ============================================================ helpers
const ease = { s: sineIO, in: sineIn, lin: t => t, snap: t => t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2, out: easeOut };
const yawTo = (from, to) => Math.atan2(to.x - from.x, to.z - from.z);
const camYawTo = (from, to) => Math.atan2(-(to.x - from.x), -(to.z - from.z)) / D2R;
const camPitchTo = (from, to) => Math.atan2(to.y - from.y, Math.hypot(to.x - from.x, to.z - from.z)) / D2R;
const mouthOf = (spk, t) => { const a = DLG.mouth[spk]; return (a && a[Math.floor(t * 30)]) || 0; };
const speaking = (spk, t, pad = 0) => DLG.lines.some(l => l.spk === spk && t >= l.t0 - pad && t < l.t1 + pad);
const loc = (root, yaw, x, y, z) => root.clone().add(V(Math.cos(yaw) * x + Math.sin(yaw) * z, y, -Math.sin(yaw) * x + Math.cos(yaw) * z));
const noise = (t, s) => Math.sin(t * 7.3 + s) * 0.5 + Math.sin(t * 13.1 + s * 2) * 0.3 + Math.sin(t * 23.7 + s * 3) * 0.2;
const bump = (t, t0, w = 0.06) => Math.exp(-Math.pow((t - t0) / w, 2));
function pathAt(t, keys) {
  if (t <= keys[0][0]) return keys[0][1].clone();
  for (let i = 0; i < keys.length - 1; i++) if (t <= keys[i + 1][0]) {
    const p0 = keys[Math.max(0, i - 1)][1], p1 = keys[i][1], p2 = keys[i + 1][1], p3 = keys[Math.min(keys.length - 1, i + 2)][1];
    const u = (t - keys[i][0]) / (keys[i + 1][0] - keys[i][0]), u2 = u * u, u3 = u2 * u;
    return p1.clone().multiplyScalar(2).add(p2.clone().sub(p0).multiplyScalar(u)).add(p0.clone().multiplyScalar(2).sub(p1.clone().multiplyScalar(5)).add(p2.clone().multiplyScalar(4)).sub(p3).multiplyScalar(u2))
      .add(p3.clone().sub(p0).add(p1.clone().multiplyScalar(3)).sub(p2.clone().multiplyScalar(3)).multiplyScalar(u3)).multiplyScalar(0.5);
  }
  return keys[keys.length - 1][1].clone();
}
function trackAt(t, keys) {
  if (t <= keys[0][0]) return keys[0][1];
  for (let i = 1; i < keys.length; i++) if (t <= keys[i][0]) return lerp(keys[i - 1][1], keys[i][1], sineIO((t - keys[i - 1][0]) / (keys[i][0] - keys[i - 1][0])));
  return keys[keys.length - 1][1];
}

// ============================================================ the ride (4.2 m/s, skid to a stop when the headlight dies)
const VR = 4.2, BRAKE0 = 18.3, STOP = 19.7;
const rideZ = t => t < BRAKE0 ? -VR * t : -VR * BRAKE0 - VR * (Math.min(t, STOP) - BRAKE0) * (1 - (Math.min(t, STOP) - BRAKE0) / (2 * (STOP - BRAKE0)));
const ZS = rideZ(STOP), BX = 1.0, EYE = 1.36, STAND = 1.48;
const FENCE_CAM = V(-5.95, STAND, HOLE_Z + 0.42);
const RUN = [[54.9, V(BX, EYE, ZS)], [55.4, V(BX - 0.45, STAND, ZS - 0.25)], [56.3, V(-1.5, STAND - 0.02, ZS - 1.1)], [57.3, V(-3.7, STAND - 0.02, ZS - 2.0)],
             [58.1, V(-5.45, STAND, FENCE_CAM.z + 0.1)], [58.6, FENCE_CAM]];
function posAt(t) {
  if (t < STOP) { const ph = t * 1.6 * Math.PI * 2, amp = t < BRAKE0 ? 1 : 1 - seg(t, BRAKE0, STOP); return V(BX + 0.03 * Math.sin(ph * 0.5) * amp, EYE + 0.012 * Math.sin(ph) * amp, rideZ(t)); }
  if (t < 54.9) return V(BX, EYE + 0.004 * Math.sin(t * 1.7), ZS);
  if (t < 58.6) { const p = pathAt(t, RUN), run = seg(t, 55.4, 55.6) * (1 - seg(t, 58.1, 58.6)); p.y += (0.04 * Math.abs(Math.sin(t * 2.9 * Math.PI)) - 0.02) * run; return p; }
  const p = FENCE_CAM.clone(); p.y += 0.005 * Math.sin(t * 2.2);
  return p;
}
function bodyYawAt(t) {
  if (t < 55.3) return 0;
  if (t < 58.6) { const a = pathAt(t - 0.15, RUN), b = pathAt(t + 0.15, RUN); return lerp(0, camYawTo(a, b), seg(t, 55.3, 55.7)); }
  return lerp(camYawTo(pathAt(58.45, RUN), FENCE_CAM), 92, seg(t, 58.6, 59.2));
}

// ============================================================ CAMERA
const CAMK = [];
const K = (t0, t1, v, e = 's') => CAMK.push({ t0, t1, v, e });
const START = { yaw: 0, pitch: -10, f: 520, roll: 0 };
K(7.7, 8.3, { pitch: -21, yaw: -9 }); K(12.1, 12.7, { pitch: -10, yaw: 0 });          // glance at the walkie for Leo
K(13.5, 14.6, { yaw: -44, pitch: -1 }); K(16.4, 17.3, { yaw: 0, pitch: -10 });        // the old power plant
K(18.4, 18.9, { pitch: -27, yaw: 3, f: 540 }, 'snap'); K(19.2, 19.7, { yaw: 8 });      // headlight dies, skid
K(21.5, 22.1, { pitch: 3, yaw: 2, f: 560 });                                           // streetlights ahead
K(24.15, 24.45, { pitch: 10, yaw: -3 }, 'snap');                                       // the one above pops
K(25.2, 25.8, { pitch: -18, yaw: -8, f: 530 });                                        // into the walkie
K(29.3, 29.9, { pitch: -4, yaw: 8 });
K(30.8, 33.2, { yaw: 63, pitch: 1 });                                                  // slow pan: red glow in the woods
K(33.0, 35.6, { f: 790 });                                                             // push in on it
K(37.1, 37.45, { pitch: -21, yaw: -8, f: 560 }, 'snap');                               // Leo panics on the radio
K(42.9, 43.4, { pitch: 1, yaw: 64, f: 640 }, 'snap');                                  // back to the woods
K(46.9, 47.4, { f: 700 });
K(54.5, 54.9, { f: 560, pitch: -6 });
K(58.2, 58.7, { f: 560 });
K(63.0, 66.0, { f: 690 }, 's');
K(66.0, 66.5, { f: 560 }, 's');
K(69.1, 69.45, { pitch: -24, yaw: 75, f: 600 }, 'snap');                               // real Leo on the radio
K(77.1, 77.45, { pitch: 3, yaw: 74, f: 560 }, 'snap');                                 // whip back up: he's at the fence
K(79.0, 86.7, { f: 690 }, 's');
K(87.0, 87.3, { f: 620 }, 'snap');
K(87.5, 88.3, { f: 470, pitch: -13, yaw: 80 }, 's');                                   // final frame: hand on the hole, walkie in hand
// look-at windows (weight ramps) towards Leo / the rift
const AIMS = [
  { t0: 46.9, t1: 54.7, ramp: 0.4, tgt: t => leoHead(t), off: [0, -3] },
  { t0: 55.4, t1: 58.7, ramp: 0.3, tgt: t => runLook(t), off: [0, -4] },
  { t0: 58.7, t1: 69.1, ramp: 0.35, tgt: t => leoHead(t).lerp(creatureHead(t), 0.35 * sineIO(seg(t, 64.6, 66.0))), off: [0, -4] },
  { t0: 65.9, t1: 66.9, ramp: 0.25, tgt: () => V(FENCE_X, 0.55, HOLE_Z), off: [0, 0] },
  { t0: 77.45, t1: 87.5, ramp: 0.3, tgt: t => leoHead(t).lerp(creatureHead(t), t > 86.9 ? 0.55 * sineIO(seg(t, 86.9, 87.2)) : 0.3), off: [0, -3] },
];
const runLook = t => pathAt(Math.min(58.6, t + 0.5), RUN).lerp(leoHead(t), seg(t, 56.5, 58.4)).setY(STAND - 0.3 + 0.3 * seg(t, 56.5, 58.4) + 0.2);
let leoState = null;
const leoHead = t => leoAt(t, true).head.clone();
const creatureHead = t => creaturePos(t).add(V(0, 3.6, 0));
const SHAKES = [[18.4, 0.5], [22.3, 0.25], [22.75, 0.3], [23.2, 0.35], [23.65, 0.45], [24.1, 0.9], [24.35, 0.4], [30.0, 0.3], [37.3, 0.6], [55.15, 0.7], [58.6, 0.5], [63.9, 1.1], [69.2, 1.0], [75.9, 0.8], [76.4, 1.0], [86.9, 2.2]];
function camAt(tReal) {
  const t = Math.min(tReal, FREEZE);
  const c = { ...START };
  for (const k of CAMK) { if (t < k.t0) break; const prev = { ...c }, kk = ease[k.e](seg(t, k.t0, k.t1)); for (const key in k.v) c[key] = lerp(prev[key], k.v[key], kk); }
  const p = posAt(t); c.x = p.x; c.y = p.y; c.z = p.z;
  // body turn during the run / at the fence carries the keyed yaw with it
  const by = bodyYawAt(t); if (t > 55.3 && t < 69.1) c.yaw = by;
  for (const a of AIMS) {
    if (t < a.t0 || t > a.t1 + a.ramp) continue;
    const w = sineIO(seg(t, a.t0, a.t0 + a.ramp)) * (1 - sineIO(seg(t, a.t1, a.t1 + a.ramp)));
    const tg = a.tgt(t); let ay = camYawTo(p, tg) + a.off[0]; ay = c.yaw + ((ay - c.yaw + 540) % 360 - 180);
    c.yaw = lerp(c.yaw, ay, w); c.pitch = lerp(c.pitch, camPitchTo(p, tg) + a.off[1], w);
  }
  // riding sway, breathing, panic handheld
  if (t < STOP) { const amp = t < BRAKE0 ? 1 : 1 - seg(t, BRAKE0, STOP); c.roll = 1.6 * Math.sin(t * 1.6 * Math.PI) * amp + noise(t, 3) * 0.4 * amp; c.yaw += noise(t, 1) * 0.7 * amp; c.pitch += noise(t, 2) * 0.5 * amp; }
  const panic = t > 37 ? (t > 69 ? 1.3 : t > 47 ? 1.0 : 0.7) : t > 22 ? 0.4 : 0.15;
  c.yaw += noise(t * 0.6, 11) * 0.5 * panic; c.pitch += noise(t * 0.6, 12) * 0.4 * panic;
  if (t > 55.4 && t < 58.4) { const ph = t * 2.9 * Math.PI * 2; c.roll += 1.3 * Math.sin(ph * 0.5); c.pitch += 1.2 * Math.sin(ph); }
  for (const [t0, a] of SHAKES) if (t > t0 && t < t0 + 0.5) { const d = t - t0; c.yaw += a * Math.exp(-d * 10) * Math.sin(d * 55); c.pitch += a * 0.7 * Math.exp(-d * 10) * Math.cos(d * 47); }
  if (tReal > FREEZE) c.f *= 1 + 0.012 * Math.pow(Math.max(0, Math.sin((tReal - FREEZE) * Math.PI * 2 * 1.15)), 8);
  return c;
}

// ============================================================ LEO (the one in the woods)
const LEO_FENCE = V(-6.98, 0, HOLE_Z - 0.05), LEO_RUN = [[46.9, V(-11.6, 0, -86.6)], [47.8, V(-9.6, 0, -85.0)], [48.7, LEO_FENCE]];
function leoAt(tt, probe = false) {
  const t = Math.min(tt, FREEZE);
  const vis = t > 46.85;
  let root = t < 48.7 ? pathAt(Math.max(46.9, t), LEO_RUN) : LEO_FENCE.clone();
  const cam = posAt(t);
  if (t > 77.0) root = LEO_FENCE.clone().add(V(0.1, 0, 0));             // pressed right up to the wire
  const yaw = t < 48.4 ? lerp(yawTo(pathAt(46.9, LEO_RUN), LEO_FENCE), yawTo(root, cam), seg(t, 48.0, 48.6)) : yawTo(root, cam);
  const p = { x: root.x, z: root.z, yaw, hipY: 0.86, lean: 0.05, headYaw: 0, headPitch: -0.05, headRoll: 0, expr: {} };
  const R0 = V(root.x, 0, root.z);
  const stand = () => { p.footL = loc(R0, yaw, -0.11, 0, 0.02); p.footR = loc(R0, yaw, 0.11, 0, 0.02); };
  const hang = (k = 0) => { p.handL = loc(R0, yaw, -0.25, 0.58 + k, 0.06); p.handR = loc(R0, yaw, 0.25, 0.58 + k, 0.06); p.handLdir = V(0, -1, 0.1); p.handRdir = V(0, -1, 0.1); };
  stand(); hang();
  if (t < 48.7) {                      // sprinting out of the trees
    const ph = t * 3.0 * Math.PI * 2, run = 1 - seg(t, 48.3, 48.7);
    for (const s of [-1, 1]) {
      const sw = Math.sin(ph + (s < 0 ? 0 : Math.PI));
      p[s < 0 ? 'footL' : 'footR'] = loc(R0, yaw, s * 0.11, Math.max(0, sw) * 0.16 * run, sw * 0.24 * run + 0.02);
      p[s < 0 ? 'handL' : 'handR'] = loc(R0, yaw, s * 0.25, 0.75 - sw * 0.05, -sw * 0.25 * run + 0.1);
    }
    p.hipY = 0.84 + 0.03 * Math.abs(Math.sin(ph)) * run; p.lean = 0.25 * run;
    p.expr = { eyes: 1.25, worry: 1, mouthBase: 0.5, pupil: 0.8 };
  } else {
    // hands on the wire (fence is at FENCE_X, he is on the far side)
    const fx = FENCE_X - 0.06, rat = (t < 62.6 || (t > 79 && t < 86.8)) ? 0.03 * Math.sin(t * 19) * (speaking('fake', t) ? 1 : 0.4) : 0;
    const onWire = t < 62.8 ? 1 : t > 76.8 ? sineIO(seg(t, 76.8, 77.2)) : 1 - sineIO(seg(t, 62.8, 63.3));
    const dz = Math.cos(yaw) > 0 ? 1 : -1;
    const wL = V(fx + rat, 1.28, root.z + 0.24), wR = V(fx + rat, 1.32, root.z - 0.24);
    hang();
    if (t > 76.8) { wL.y = 1.52; wR.y = 1.5; }
    p.handL = p.handL.lerp(wL, onWire); p.handR = p.handR.lerp(wR, onWire);
    if (onWire > 0.5) { p.handLdir = V(-1, 0.3, 0); p.handRdir = V(-1, 0.3, 0); }
    // pointing down at the hole ("come through the hole in the fence")
    const pt = sineIO(seg(t, 65.5, 65.9)) * (1 - sineIO(seg(t, 67.4, 67.9)));
    if (pt > 0) { p.handR = p.handR.lerp(loc(R0, yaw, 0.22, 0.95, 0.42), pt); p.handRdir = V(1, -0.7, 0).normalize(); }
    p.lean = t > 76.8 ? 0.12 : 0.06;
    const calm = t > 62.6 && t < 76.8;
    if (calm) {      // eerily calm: dead still, head slowly tilting
      p.headRoll = 0.28 * sineIO(seg(t, 63.0, 66.5)); p.headPitch = -0.08;
      p.expr = { eyes: 1.15, worry: 0, mouthBase: 0.05, pupil: 0.75 + 0.4 * seg(t, 66, 68) };
    } else if (t > 76.8) {   // pressed against the wire, crying — with eyes that are all black
      const black = sineIO(seg(t, 77.0, 78.0));
      p.expr = { eyes: 1.25, worry: 1.1, mouthBase: 0.3, tears: 1, pupil: 0.8 + 1.85 * black };
      p.headRoll = 0.06 * Math.sin(t * 2.1);
      if (t > 86.9) { const k = sineIO(seg(t, 86.9, 87.15)); p.expr.mouthBase = 0.3 + 0.65 * k; p.expr.worry = 1.1 - 1.4 * k; p.headRoll = 0.32 * k; p.headPitch = -0.15 * k; }
    } else {
      p.expr = { eyes: 1.2, worry: 1, mouthBase: 0.25, pupil: 0.85, tears: t > 53 ? 0.6 : 0 };
      p.headYaw = 0.9 * sineIO(seg(t, 51.4, 51.8)) * (1 - sineIO(seg(t, 52.3, 52.7)));     // glance over the shoulder
    }
  }
  if (probe) {
    poseMaya(leo, p, t, 0); leo.head.updateMatrixWorld(true);
    return { head: leo.head.localToWorld(V(0, 0.03, 0)) };
  }
  leo.root.visible = vis; [leo.armL, leo.armR, leo.legL, leo.legR].forEach(L => [L.a, L.j, L.b].forEach(m => m.visible = vis));
  leo.hands.forEach(h => h.visible = vis); leo.feet.forEach(f => f.visible = vis);
  poseMaya(leo, p, t, mouthOf('fake', t));
  return { head: leo.head.localToWorld(V(0, 0.03, 0)) };
}

// ============================================================ the creature
const CR_END = V(-12.6, 0, -88.4);
const creaturePos = t => RIFT.clone().lerp(CR_END, sineIO(seg(t, 64.8, 68.2)));
function creatureAt(tt) {
  const t = Math.min(tt, FREEZE), C = creature;
  C.g.visible = t > 64.5;
  if (!C.g.visible) return;
  const p = creaturePos(t), cam = posAt(t);
  C.g.position.copy(p); C.g.rotation.y = yawTo(p, cam);
  const walk = seg(t, 64.8, 65.0) * (1 - seg(t, 67.9, 68.2)), ph = (t - 64.8) * 0.75 * Math.PI * 2;
  C.legs.forEach((L, i) => { const s = i ? 1 : -1; L.G.rotation.x = -0.35 * Math.sin(ph + (s < 0 ? 0 : Math.PI)) * walk; L.j.rotation.x = 0.25 + 0.25 * Math.max(0, Math.sin(ph + (s < 0 ? 0 : Math.PI))) * walk; });
  const shriek = t > 86.9 ? sineIO(seg(t, 86.9, 87.15)) : 0;
  C.torso.rotation.x = 0.16 + 0.04 * Math.sin(t * 0.9) - 0.1 * shriek;
  C.torso.position.y = 1.75 - 0.03 * Math.abs(Math.sin(ph)) * walk;
  C.arms.forEach((L, i) => { const s = i ? 1 : -1; L.G.rotation.set(0.25 * Math.sin(ph + (s < 0 ? Math.PI : 0)) * walk - 0.1 - 0.5 * shriek, 0, s * (0.1 + 0.05 * Math.sin(t * 1.3 + s) + 0.95 * shriek)); L.j.rotation.x = -0.2 - 0.3 * shriek; });
  C.neck.rotation.set(0.35 - 0.8 * shriek, 0, 0);
  C.head.rotation.set(0, 0, 0.35 * Math.sin(t * 0.45) * (1 - shriek) + (t > 76 ? 0.25 : 0) * (1 - shriek));
  C.petals.forEach(P => { P.rotation.order = 'YXZ'; P.rotation.x = -1.1 * shriek; });
  C.maw.visible = shriek > 0.1;
}

// ============================================================ POV hands: left on the bar / fence, right holds the walkie
const WALK_RAISE = [[0, 0], [7.6, 0], [8.1, 1], [12.2, 1], [12.8, 0.55], [17.3, 0.55], [17.8, 0], [25.2, 0], [25.7, 1], [30.3, 1], [30.9, 0.3], [37.05, 0.3], [37.4, 1], [43.0, 1], [43.6, 0.3], [44.2, 0.3], [44.5, 0.75], [46.9, 0.75], [47.4, 0.3]];
function applyHand(h, s) { h.g.visible = s.vis; if (s.vis) { h.g.position.copy(s.pos); h.g.quaternion.copy(basisQuat(s.fd, s.pn)); poseHand(h, s.pose); h.g.updateMatrixWorld(); } }
function handsAt(t, bf) {
  const bl = (x, y, z) => V(x, y, z).applyMatrix4(bf), bd = (x, y, z) => V(x, y, z).transformDirection(bf);
  const R = { pos: bl(0.2, -0.36, -0.36), fd: bd(-0.35, 0.15, -1), pn: bd(-1, 0, 0.25), pose: 'grip', vis: true };
  const L = { pos: V(), fd: bd(0.1, -0.6, -1), pn: bd(0, -1, 0.3), pose: 'grip', vis: true };
  bike.bars.updateMatrixWorld(true);
  const grip = bike.bars.localToWorld(V(-0.29, 0.03, 0.02));
  L.pos = grip;
  if (t > 18.9 && t < 21.6) {          // tap the dead headlight
    const lamp = bike.bars.localToWorld(V(0, 0.0, -0.08)), k = sineIO(seg(t, 18.9, 19.6)) * (1 - sineIO(seg(t, 21.0, 21.6)));
    const tap = bump(t, 20.3, 0.07) + bump(t, 20.75, 0.07);
    L.pos = grip.clone().lerp(lamp.clone().add(V(0.01, 0.06 + 0.03 * (1 - tap), 0.04)), k); L.fd = bd(0.2, -0.8, -0.6); L.pn = bd(0, -1, 0); L.pose = k > 0.5 ? 'flat' : 'grip';
  }
  // right hand: walkie lifted for each radio exchange
  if (t < 54.9) {
    const k = trackAt(t, WALK_RAISE);
    R.pos = bl(0.2, -0.36, -0.36).lerp(bl(0.13, -0.21, -0.36), k);
    R.fd = bd(-0.35, 0.15, -1).lerp(bd(-0.4, 0.32, -1), k).normalize();
  }
  if (t >= 54.9 && t < 58.6) {          // off the bike and running: arms pumping
    const ph = t * 2.9 * Math.PI, off = seg(t, 54.9, 55.4);
    for (const [H, s] of [[R, 1], [L, -1]]) {
      const sw = Math.sin(ph + (s > 0 ? 0 : Math.PI)) * seg(t, 55.3, 55.6);
      const run = bl(s * 0.24, -0.46 + 0.16 * Math.max(0, sw), -0.32 - 0.07 * sw);
      H.pos = (s < 0 ? grip : bl(0.2, -0.36, -0.36)).lerp(run, off);
      H.fd = bd(-s * 0.3, 0.6, -1); H.pn = bd(-s * 0.8, -0.2, 0);
    }
    const toFence = sineIO(seg(t, 58.2, 58.6));
    L.pos.lerp(V(FENCE_X + 0.07, 1.32, FENCE_CAM.z + 0.12), toFence);
  }
  if (t >= 58.6) {
    // left hand on the wire, then down to the torn edge of the hole for the final frame
    const shake = (t < 62.5 ? 0.01 * Math.sin(t * 17) : 0.003 * Math.sin(t * 23));
    L.pos = V(FENCE_X + 0.07, 1.32 + shake, FENCE_CAM.z + 0.12).lerp(V(FENCE_X + 0.07, 1.06, HOLE_Z + 0.52), sineIO(seg(t, 87.3, 88.2)));
    L.fd = V(-0.5, -0.85, 0).normalize(); L.pn = V(-1, 0, 0);
    const k = sineIO(seg(t, 69.1, 69.45)) * (1 - sineIO(seg(t, 77.0, 77.5)));
    const tr = V(Math.sin(t * 41) * 0.003, Math.sin(t * 37) * 0.003, 0).multiplyScalar(t > 69 ? 1 : 0.3);
    R.pos = bl(0.22, -0.4, -0.3).lerp(bl(0.1, -0.17, -0.33), k).lerp(bl(0.2, -0.3, -0.33), sineIO(seg(t, 87.4, 88.2))).add(tr);
    R.fd = bd(-0.35, 0.15, -1).lerp(bd(-0.4, 0.32, -1), k).normalize();
  }
  return { R, L };
}

// ============================================================ HUD
const titleEl = document.getElementById('title'), subEl = document.getElementById('subtxt'), ctaEl = document.getElementById('cta');
const CTA_T = 89.0;
function hudAt(t) {
  const a = easeOut(seg(t, 0.15, 0.55)), out = seg(t, 5.8, 6.2);
  titleEl.style.opacity = a * (1 - out); titleEl.style.transform = `translateX(${-12 * (1 - a)}px)`;
  let sub = null;
  for (const l of DLG.lines) for (const c of l.chunks) if (t >= c.t0 && t < c.t1) sub = { c, spk: l.spk };
  subEl.textContent = sub ? sub.c.text : ''; subEl.className = sub ? sub.spk : '';
  if (sub) subEl.style.transform = `translateX(-50%) scale(${0.91 + 0.09 * easeOut(seg(t, sub.c.t0, sub.c.t0 + 0.1))})`;
  document.getElementById('sub').style.top = t > CTA_T - 0.3 ? '1150px' : '839px';
  ctaEl.style.display = t > CTA_T ? 'block' : 'none';
  if (t > CTA_T) {
    const k = easeOut(seg(t, CTA_T, CTA_T + 0.3)); ctaEl.style.opacity = k;
    ctaEl.querySelector('.q').style.transform = `scale(${0.85 + 0.15 * k})`;
    ctaEl.querySelectorAll('.btn').forEach((b, i) => { const kb = easeOut(seg(t, CTA_T + 0.2 + i * 0.15, CTA_T + 0.5 + i * 0.15)); b.style.transform = `scale(${0.8 + 0.2 * kb})`; b.style.opacity = kb; });
  }
}

// ============================================================ lights + world state
const POPS = { '-150': 22.3, '-130': 22.75, '-110': 23.2, '-90': 23.65, '-70': 24.1, '-50': 24.35, '-30': 24.5, '-10': 24.6 };
function lampLevel(t, tp) {
  if (t < tp - 0.45) return 1;
  if (t < tp) return [1, 0.3, 1, 1, 0.15, 1, 0.6, 1, 0.2][Math.floor((t - tp + 0.45) / 0.05)] ?? 1;   // buzz/flicker
  if (t < tp + 0.06) return 2.2;   // the pop flash
  return 0;
}
function headlightLevel(t) {
  if (t < 17.6) return 1;
  if (t < 18.4) { const k = Math.floor((t - 17.6) / 0.05); return [1, 0.2, 1, 1, 0, 0.8, 0.1, 1, 0, 0, 0.6, 0, 0.9, 0, 0, 0.3][k] ?? 0; }
  if (Math.abs(t - 20.36) < 0.05 || Math.abs(t - 20.8) < 0.03) return 0.5;
  return 0;
}
function worldAt(t) {
  // streetlights
  for (const L of lamps) {
    const lv = lampLevel(t, POPS[String(L.z)]);
    L.glow.material.opacity = Math.min(1.3, 0.9 * lv); L.cone.material.opacity = 0.05 * Math.min(1, lv); L.pool.material.opacity = 0.4 * Math.min(1.3, lv);
    L.bulb.material.color.set(lv > 0.5 ? '#ffd59a' : '#2a2a2e');
  }
  windows.forEach((w, i) => { const off = t > 23.4 + (i * 0.37 % 1.2); if (w.win) w.win.material.color.set(off ? '#141a28' : '#ffcf72'); w.gl.material.opacity = off ? 0 : (w.porch ? 0.7 : 0.22); });
  plantLights.forEach((s, i) => s.material.opacity = (t < 24.0 && ((t * 0.8 + i * 0.33) % 1) < 0.45) ? 1 : 0);
  // headlight
  const hl = headlightLevel(t);
  headlight.glow.material.opacity = hl; headlight.beam.material.opacity = 0.05 * hl; headlight.pool.material.opacity = 0.3 * hl;
  headlight.lens.material.color.set(hl > 0.3 ? '#fff4cf' : '#4a4740');
  bike.g.updateMatrixWorld(true); const hp = bike.g.localToWorld(V(0, 0, -5.5)); headlight.pool.position.set(hp.x, 0.025, hp.z);
  // red glow in the woods, then the rift
  const glow = sineIO(seg(t, 30.4, 32.6)), open = t > 63.9 ? easeOut(seg(t, 63.9, 64.5)) : 0;
  const pulse = 0.85 + 0.15 * Math.sin(t * 2.3) + 0.08 * Math.sin(t * 7.1);
  woodsGlow.material.opacity = (0.42 * glow + 0.45 * open) * pulse;
  woodsLight.intensity = (22 * glow + 40 * open) * pulse;
  rift.sprite.visible = open > 0; rift.sprite.scale.set(2.0 * open * (1 + 0.06 * Math.sin(t * 13)), 4.3 * Math.min(1, open * 1.6), 1);
  rift.glow.material.opacity = 0.9 * open * pulse; rift.pool.material.opacity = 0.35 * Math.max(glow * 0.5, open);
  // ash spores
  const pos = ash.geometry.attributes.position.array;
  for (let k = 0; k < pos.length / 3; k++) {
    const b = k * 4, ph = ashBase[b + 3];
    pos[k * 3] = ashBase[b] + Math.sin(t * 0.3 + ph) * 0.5; pos[k * 3 + 1] = (ashBase[b + 1] + t * 0.14 + Math.sin(t * 0.7 + ph) * 0.1) % 5;
    pos[k * 3 + 2] = ashBase[b + 2] + Math.cos(t * 0.25 + ph) * 0.5;
  }
  ash.geometry.attributes.position.needsUpdate = true; ash.material.opacity = 0.85 * sineIO(seg(t, 30.0, 33.0));
  amb.intensity = t < 24.6 ? 1.5 : 1.15;
}
function bikeAt(t) {
  const z = rideZ(Math.min(t, STOP));
  bike.g.position.set(BX, 0, z);
  const skid = sineIO(seg(t, BRAKE0, STOP));
  bike.g.rotation.set(0, 0.22 * skid, 0, 'YXZ');
  if (t < STOP) bike.g.rotation.z = -0.025 * Math.sin(t * 1.6 * Math.PI) * (1 - skid);
  bike.wheel.rotation.x = z / 0.28;
  bike.bars.rotation.y = 0.04 * Math.sin(t * 1.6 * Math.PI) * (1 - skid) + 0.3 * skid;
  const fall = t > 54.9 ? Math.min(1, Math.pow(seg(t, 54.9, 55.2), 2)) : 0;
  bike.g.rotation.z = lerp(bike.g.rotation.z, -1.45, fall);
  if (fall > 0) bike.g.position.x = BX + 0.35 * fall;
}

// ============================================================ render
window.setHud = on => { document.getElementById('hud').style.display = on ? 'block' : 'none'; };
window.renderAt = (tReal) => {
  const t = Math.min(tReal, FREEZE);
  bikeAt(t); worldAt(t);
  const c = camAt(tReal);
  camera.position.set(c.x, c.y, c.z); camera.rotation.set(c.pitch * D2R, c.yaw * D2R, (c.roll || 0) * D2R); camera.updateMatrixWorld(); setFocal(c.f);
  const by = bodyYawAt(t), bf = new THREE.Matrix4().makeRotationY(by * D2R); bf.setPosition(c.x, c.y, c.z);
  leoAt(t); creatureAt(t);
  const hs = handsAt(t, bf); applyHand(handR, hs.R); applyHand(handL, hs.L);
  placeArm(armR, handR.g.localToWorld(V(0, 0.004, 0.045)), 1, bf, hs.R.vis);
  placeArm(armL, handL.g.localToWorld(V(0, 0.004, 0.045)), -1, bf, hs.L.vis);
  // walkie LED: red while a signal comes through (Leo or the static), plus when you key the mic
  const rx = speaking('leo', t, 0.1) || (t > 29.4 && t < 30.3) || (t > 76.9 && t < 77.3);
  const tx = DLG.lines.some(l => l.spk === 'you' && ['l2', 'l4', 'l7'].includes(l.id) && t >= l.t0 - 0.2 && t < l.t1);
  const led = rx ? (0.6 + 0.4 * Math.sin(t * 30)) : tx ? 1 : (Math.floor(t * 1.2) % 2 ? 0.15 : 0);
  walkie.led.material.color.set(led > 0.3 ? '#ff3a3a' : '#5a0c0c'); walkie.ledGlow.material.opacity = led;
  // grade: red cast once the woods glow, flashes on the pops / rift / shriek
  const red = 0.05 * sineIO(seg(t, 30.4, 33)) + 0.07 * (t > 63.9 ? 1 : 0) + 0.06 * (t > 86.9 ? 1 : 0);
  lens.uniforms.policeAmt.value = red; lens.uniforms.policeCol.value.set(1, 0.22, 0.18); lens.uniforms.policeDim.value = 0;
  lens.uniforms.glareAmt.value = 0;
  lens.uniforms.vign.value = 0.25 + 0.6 * easeOut(seg(tReal, FREEZE - 0.15, FREEZE + 0.4));
  lens.uniforms.flash.value = 0.12 * bump(t, 63.95, 0.06) + 0.1 * bump(t, 86.95, 0.05) + 0.01 * Object.values(POPS).reduce((a, p) => a + bump(t, p + 0.03, 0.025), 0);
  renderFrame();
  hudAt(tReal);
};
window.DURATION = DUR;
window.sceneReady = Promise.resolve(true);
