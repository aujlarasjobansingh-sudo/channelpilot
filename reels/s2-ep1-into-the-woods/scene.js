// SEASON 2 • EPISODE 1 — "INTO THE WOODS". Continues straight from the Season 1 finale: Sam drags/shoves us into the woods.
import { THREE, scene, camera, setFocal, projectLens, renderFrame, lens, D2R, sineIO, sineIn, easeOut, seg, lerp, glowSprite, box } from './core.js';
import { buildSet, EYE, CAB, DOOR_X, WIN_X, WIN_Y0, HATCH, S, pathX } from './set.js';
import { makeHand, poseHand, makeArm, placeArm, basisQuat, makeOfficer, poseOfficer, makeSam, poseSam } from './chars.js';

const V = (x, y, z) => new THREE.Vector3(x, y, z);
await Promise.all([500, 600, 700, 800, 900].map(w => document.fonts.load(`${w} 40px Rubik`)));
const DLG = await (await fetch('out/dialogue.json')).json();
buildSet();
scene.background = new THREE.Color('#05070c');
scene.fog = new THREE.Fog('#06090f', 7, 48);
camera.far = 160; camera.updateProjectionMatrix();
const amb = new THREE.AmbientLight('#dfe7ff', 1.45); scene.add(amb);
const moon = new THREE.DirectionalLight('#b8c8ff', 0.6); moon.position.set(-3, 8, -4); scene.add(moon);
const cop = makeOfficer(), sam = makeSam();
const handR = makeHand(1), handL = makeHand(-1), armR = makeArm(), armL = makeArm();
const FREEZE = 80.4, DUR = 92;
const copLight = new THREE.PointLight('#cfd8ff', 0, 4, 1.5); scene.add(copLight);
// Sam's phone (lights his face blue)
const sPhone = new THREE.Group(); sam.hands[0].add(sPhone);
box(0.07, 0.14, 0.009, '#15171c', 0, 0.0, -0.06, sPhone).rotation.x = -1.2;
const sPhoneGlow = glowSprite('#9fc4ff', 0.25, sPhone); sPhoneGlow.position.set(0, 0.03, -0.06);
const faceLight = new THREE.PointLight('#8fb8ff', 0, 1.6, 1.2); scene.add(faceLight);
// broken slats = the crack we peer through
S.slats[3].visible = false; S.slats[4].scale.x = 0.45; S.slats[4].position.x += 0.2;

// ============================================================ helpers
const ease = { s: sineIO, in: sineIn, lin: t => t, snap: t => t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2, out: easeOut };
const wrapA = a => Math.atan2(Math.sin(a), Math.cos(a));
const yawTo = (from, to) => Math.atan2(to.x - from.x, to.z - from.z);
const camYawTo = (from, to) => Math.atan2(-(to.x - from.x), -(to.z - from.z)) / D2R;
const camPitchTo = (from, to) => Math.atan2(to.y - from.y, Math.hypot(to.x - from.x, to.z - from.z)) / D2R;
const unwrapNear = (a, ref) => a + 360 * Math.round((ref - a) / 360);
const mouthOf = (spk, t) => { const a = DLG.mouth[spk]; return (a && a[Math.floor(t * 30)]) || 0; };
const loc = (root, yaw, x, y, z) => root.clone().add(V(Math.cos(yaw) * x + Math.sin(yaw) * z, y, -Math.sin(yaw) * x + Math.cos(yaw) * z));
const camLocal = (x, y, z) => V(x, y, z).applyMatrix4(camera.matrixWorld);
const camDir = (x, y, z) => V(x, y, z).transformDirection(camera.matrixWorld);
const noise = (t, s) => Math.sin(t * 7.3 + s) * 0.5 + Math.sin(t * 13.1 + s * 2) * 0.3 + Math.sin(t * 23.7 + s * 3) * 0.2;
function gait(t, root, yaw, speed, phase0 = 0) {
  const ph = phase0 + t * (speed > 1.5 ? 2.7 : 1.8) * Math.PI * 2;
  const fwd = V(Math.sin(yaw), 0, Math.cos(yaw)), rt = V(Math.cos(yaw), 0, -Math.sin(yaw)), stride = Math.min(0.42, 0.18 * speed);
  const off = s => ph + (s > 0 ? Math.PI : 0);
  const foot = s => root.clone().add(rt.clone().multiplyScalar(s * 0.1)).add(fwd.clone().multiplyScalar(stride * Math.sin(off(s)))).add(V(0, Math.max(0, Math.cos(off(s))) * 0.13 * Math.min(1, speed), 0));
  return { footL: foot(-1), footR: foot(1), bob: 0.03 * Math.abs(Math.sin(ph)) };
}
const headLook = (root, yaw, lean, headH, pt) => {
  const dir = V(pt.x - root.x, pt.y - headH, pt.z - root.z);
  return { headYaw: Math.max(-1.3, Math.min(1.3, wrapA(Math.atan2(dir.x, dir.z) - yaw))), headPitch: Math.max(-0.75, Math.min(0.75, -Math.atan2(dir.y, Math.hypot(dir.x, dir.z)) - lean)) };
};
const trackAt = (t, keys) => {   // eased hops between [t, V3]
  if (t <= keys[0][0]) return keys[0][1].clone();
  for (let i = 1; i < keys.length; i++) if (t <= keys[i][0]) return keys[i - 1][1].clone().lerp(keys[i][1], sineIO(seg(t, keys[i - 1][0], keys[i][0])));
  return keys[keys.length - 1][1].clone();
};

// ============================================================ key places + timings
const Z1 = CAB.z1;
const T_TRIP = 10.0, T_KICK = 19.0, T_SLAM = 20.5, T_BUZZ = 25.4, T_FLASH = 35.5, T_GRAB = 45.3, T_STING = 53.4, T_WHIP = 62.0, T_BANGS = [71.5, 72.2, 72.9];
const INSIDE = V(0.6, 0, Z1 - 1.1), SIT = V(1.55, 0, -30.85), NEAR_DOOR = V(0.95, 0, Z1 - 0.85), PULLED = V(1.05, 0, Z1 - 1.45);
const PEEK = V(WIN_X + 0.03, 0, Z1 - 0.3), MID = V(-0.35, 0, Z1 - 1.3);
const CRACK_Y = WIN_Y0 + 0.05 + 3 * 0.1;
const COP_OUT = V(-1.05, 0, Z1 + 3.9);
const SAM_WIN = V(-0.9, 0, Z1 - 0.8), SAM_GRAB = V(0.35, 0, Z1 - 1.25), SAM_RUG = V(HATCH.x, 0, HATCH.z - 0.72);
const runZ = t => t < T_TRIP ? lerp(4.0, -13.35, t / T_TRIP) : t < 12.6 ? -13.35 : lerp(-13.35, Z1 + 1.15, sineIO(seg(t, 12.6, 18.9)) * 0.15 + seg(t, 12.6, 18.9) * 0.85);
const pathPos = t => { const z = runZ(t); return V(lerp(pathX(z), DOOR_X, seg(z, -20.0, Z1 + 1.15)), 0, z); };

// ============================================================ CAMERA
function camAt(tReal) {
  const t = Math.min(tReal, FREEZE);
  const c = { x: 0, y: EYE, z: 0, yaw: 0, pitch: -3, roll: 0, f: 520 };
  if (t < 19.5) {
    // shoved through the woods → trip → up → the cabin
    const p = pathPos(t), q = pathPos(Math.min(t + 0.4, 18.9)); c.x = p.x; c.z = p.z;
    let yaw = camYawTo(p, V(q.x, 0, q.z - 0.6)), pitch = -3;
    const run = t < T_TRIP ? 1 : t > 12.6 && t < 18.9 ? 0.75 : 0;
    const ph = t * 2.7 * Math.PI * 2;
    c.y = EYE + (0.045 * Math.abs(Math.sin(ph)) - 0.02) * run;
    // glance back: Sam right behind us, police lights sweeping through the trees
    const back = sineIO(seg(t, 5.4, 6.0)) * (1 - sineIO(seg(t, 7.0, 7.6)));
    yaw = lerp(yaw, yaw + 165, back);
    // trip over the root → hands in the mud
    const fall = ease.snap(seg(t, T_TRIP, T_TRIP + 0.4)), up = sineIO(seg(t, 11.7, 12.7));
    c.y = lerp(c.y, 0.55, fall * (1 - up)); pitch = lerp(pitch, -48, fall * (1 - up)); c.z -= 0.45 * fall;
    c.roll = 7 * fall * (1 - up);
    // look up at the cabin in the fog (13.0), Sam points the gun at it (14.6)
    const cab = V(0.2, 1.4, Z1 - 1), yC = unwrapNear(camYawTo(V(c.x, 0, c.z), cab), yaw);
    const kC = sineIO(seg(t, 12.7, 13.4)); yaw = lerp(yaw, yC, kC); pitch = lerp(pitch, camPitchTo(V(c.x, c.y, c.z), cab), kC);
    const samH = sam.head.getWorldPosition(V(0, 0, 0)), yS = unwrapNear(camYawTo(V(c.x, 0, c.z), samH), yaw);
    const kS = sineIO(seg(t, 14.4, 14.9)) * (1 - sineIO(seg(t, 15.9, 16.5))); yaw = lerp(yaw, yS, kS); pitch = lerp(pitch, camPitchTo(V(c.x, c.y, c.z), samH), kS);
    c.f = lerp(520, 640, sineIO(seg(t, 13.0, 14.2))) - 120 * sineIO(seg(t, 16.5, 17.5));
    // pushed in through the door
    const kIn = sineIO(seg(t, T_KICK + 0.35, T_KICK + 1.1)); c.x = lerp(c.x, INSIDE.x, kIn); c.z = lerp(c.z, INSIDE.z, kIn);
    c.yaw = yaw + noise(t, 1) * 2.2 * (run + 0.3); c.pitch = pitch + noise(t, 2) * 1.4 * (run + 0.2) + 1.8 * Math.sin(ph * 2) * run;
    c.roll += 1.4 * Math.sin(ph) * run + noise(t, 3) * 0.9 * run;
    return withImpacts(c, t, tReal);
  }
  // ---------------- inside the cabin
  const at = (pt) => ({ y: camYawTo(V(c.x, 0, c.z), pt), p: camPitchTo(V(c.x, c.y, c.z), pt) });
  const pos = trackAt(t, [[19.5, INSIDE], [22.1, INSIDE], [23.8, SIT], [42.6, SIT], [43.6, SIT.clone().lerp(NEAR_DOOR, 0.4)], [45.0, NEAR_DOOR], [45.3, NEAR_DOOR], [45.8, PULLED], [51.0, PULLED], [52.6, PEEK], [T_WHIP, PEEK], [T_WHIP + 0.9, MID]]);
  c.x = pos.x; c.z = pos.z;
  const sitK = sineIO(seg(t, 22.4, 23.8)) * (1 - sineIO(seg(t, 42.6, 43.4)));
  c.y = lerp(EYE, 0.82, sitK); if (t > 51.0 && t < T_WHIP + 0.6) c.y = lerp(c.y, CRACK_Y, sineIO(seg(t, 51.0, 52.6)) * (1 - sineIO(seg(t, T_WHIP, T_WHIP + 0.6))));
  const samH = sam.head.getWorldPosition(V(0, 0, 0)), doorPt = V(DOOR_X + 0.4, 1.2, Z1), win = V(WIN_X, 1.35, Z1), rug = V(HATCH.x, 0.2, HATCH.z);
  let a = at(V(0, 1.2, -31.5)); let yaw = a.y, pitch = a.p, f = 540;   // facing into the room (shelves)
  const blend = (k, b) => { if (k <= 0) return; yaw = lerp(yaw, unwrapNear(b.y, yaw), k); pitch = lerp(pitch, b.p, k); };
  blend(sineIO(seg(t, 20.5, 21.2)), at(samH));                                   // turn to Sam slamming the bolt
  blend(sineIO(seg(t, 22.3, 23.6)), at(V(-0.4, 1.1, Z1)));                       // sit: facing the front wall
  blend(sineIO(seg(t, 24.2, 25.2)), at(samH));                                   // watching Sam pace
  if (t > 25.2 && t < 35.4) { const b = at(samH); yaw = lerp(yaw, unwrapNear(b.y, yaw), 0.9); pitch = lerp(pitch, b.p, 0.9); f = lerp(540, 680, sineIO(seg(t, 26.0, 34.0))); }
  blend(ease.snap(seg(t, T_FLASH, T_FLASH + 0.35)), at(win)); if (t > T_FLASH) f = lerp(f, 600, seg(t, T_FLASH, T_FLASH + 0.3));
  blend(sineIO(seg(t, 42.6, 43.4)), at(doorPt));                                  // up, toward the door
  blend(ease.snap(seg(t, T_GRAB, T_GRAB + 0.3)), at(samH));                       // yanked back: Sam's terrified face
  if (t > T_GRAB + 0.3 && t < 51.0) { const b = at(samH); yaw = lerp(yaw, unwrapNear(b.y, yaw), 0.9); pitch = lerp(pitch, b.p, 0.9); f = lerp(600, 720, seg(t, 46, 50.5)); }
  // peek through the broken slat: the lone silhouette outside
  const kP = sineIO(seg(t, 51.0, 52.6)); if (kP > 0) { const b = { y: camYawTo(V(c.x, 0, c.z), V(COP_OUT.x, 0, COP_OUT.z)), p: camPitchTo(V(c.x, c.y, c.z), V(COP_OUT.x, 1.3, COP_OUT.z)) }; blend(kP, b); f = lerp(f, 980, kP); }
  if (t > 52.6 && t < T_WHIP) { f = 980 + 220 * sineIO(seg(t, 52.6, 61.5)); pitch -= 6 * sineIO(seg(t, 55.4, 56.4)); }   // follow the flashlight down to the bloody sleeve
  // whip back to Sam ripping up the rug
  const kW = ease.snap(seg(t, T_WHIP, T_WHIP + 0.4)); if (kW > 0) { blend(kW, at(sam.torso.localToWorld(V(0, 0.2, 0)))); f = lerp(f, 560, kW); }
  if (t > T_WHIP + 0.4) { const b = at(sam.torso.localToWorld(V(0, 0.25, 0))); yaw = lerp(yaw, unwrapNear(b.y, yaw), 0.85); pitch = lerp(pitch, b.p - 6, 0.85); f = lerp(560, 640, seg(t, 64, 70)); }
  // BANG BANG BANG → snap to the door
  blend(ease.snap(seg(t, T_BANGS[0], T_BANGS[0] + 0.3)) * (1 - sineIO(seg(t, 77.2, 78.2))), at(doorPt));
  // final split: left at the rattling deadbolt … then right at Sam in the hatch, reaching up
  blend(sineIO(seg(t, 78.4, 79.2)) * (1 - sineIO(seg(t, 79.5, 80.3))), at(V(DOOR_X + 0.75, 1.25, Z1)));
  blend(sineIO(seg(t, 79.5, 80.3)), at(V(HATCH.x, 0.35, HATCH.z)));
  c.yaw = yaw + noise(t, 4) * 0.6; c.pitch = pitch + noise(t, 5) * 0.45; c.f = f;
  if (t > T_GRAB && t < T_GRAB + 0.6) c.roll = 4 * Math.sin(seg(t, T_GRAB, T_GRAB + 0.6) * Math.PI);
  return withImpacts(c, t, tReal);
}
function withImpacts(c, t, tReal) {
  for (const [t0, a] of [[T_TRIP + 0.38, 2.2], [T_KICK, 1.2], [T_SLAM, 1.4], [T_FLASH, 0.6], [T_GRAB, 2.0], [T_STING, 0.6], [T_WHIP, 0.8], ...T_BANGS.map(b => [b, 1.6]), [74.8, 1.2], [76.2, 1.2]]) {
    if (t > t0 && t < t0 + 0.45) { const d = t - t0; c.yaw += a * Math.exp(-d * 11) * Math.sin(d * 55); c.pitch += a * 0.7 * Math.exp(-d * 11) * Math.cos(d * 47); }
  }
  if (tReal > FREEZE) c.f *= 1 + 0.012 * Math.pow(Math.max(0, Math.sin((tReal - FREEZE) * Math.PI * 2 * 1.15)), 8);
  return c;
}

// ============================================================ SAM
function samAt(t) {
  const mouth = mouthOf('sam', t), POVc = camera.position.clone();
  const cold = { eyes: 0.95, worry: -0.3, mouthBase: 0.05 }, panic = { eyes: 1.25, worry: 1.3, mouthBase: 0.2 };
  let p;
  if (t < 19.6) {
    // right behind us, shoving with the gun; beside us once we're up
    const pp = pathPos(Math.max(0, t - 0.45)), nx = pathPos(t);
    let root = V(pp.x + 0.15, 0, pp.z + 0.75);
    if (t > 12.0) root = V(pathPos(t).x + 0.85, 0, pathPos(t).z + 0.1);
    if (t > 18.0) root = root.lerp(V(DOOR_X + 0.6, 0, Z1 + 0.55), sineIO(seg(t, 18.0, 18.9)));
    const yaw = t > 18.9 ? Math.PI : yawTo(root, V(nx.x, 0, nx.z - 2));
    const moving = (t < T_TRIP || (t > 12.6 && t < 18.9)) ? 2.4 : 0;
    const gt = gait(t, root, yaw, moving, 0.6);
    const shoulder = loc(root, yaw, 0.2, 1.45, 0.05);
    let aim = POVc.clone().add(V(0, -0.2, 0));
    if (t > 14.4 && t < 16.6) aim = V(0.3, 1.2, Z1 + 0.2);                       // points the gun at the cabin
    const handR = shoulder.clone().add(aim.clone().sub(shoulder).normalize().multiplyScalar(0.5));
    let handL = t < T_TRIP ? camLocal(0.12, -0.25, 0.35) : loc(root, yaw, -0.25, 0.92, 0.1);
    let footL = gt.footL, footR = gt.footR;
    if (t > T_KICK - 0.35 && t < T_KICK + 0.3) { const k = Math.sin(seg(t, T_KICK - 0.35, T_KICK + 0.3) * Math.PI); footR = loc(root, yaw, 0.12, 0.5 * k, 0.55 * k); }
    p = { x: root.x, z: root.z, yaw, hipY: 0.98 - gt.bob, lean: moving ? 0.25 : 0.05, handL, handR, handRdir: aim.clone().sub(handR).normalize(), gun: true, footL, footR, expr: { ...cold, eyes: 1.0 } };
    Object.assign(p, headLook(root, yaw, p.lean, p.hipY + 0.78, t > 14.4 && t < 16.6 ? V(0.3, 1.2, Z1) : t > 5.4 && t < 7.6 ? POVc : V(nx.x, 1.4, nx.z - 4)));
  } else {
    // inside
    let root, yaw, hipY = 0.98, lean = 0.05, expr = { ...cold }, tgt = POVc.clone(), gun = true, handL = null, handR = null, dirR = null, dirL = null, footL, footR, sp = 0;
    if (t < 21.5) { root = V(DOOR_X + 0.3, 0, Z1 - 0.35 - 0.3 * sineIO(seg(t, 19.6, 20.4))); yaw = yawTo(root, POVc); lean = -0.1; }
    else if (t < 35.5) {   // pacing by the window, phone buzzes
      const k = 0.5 - 0.5 * Math.cos(Math.max(0, t - 21.5) * 0.55);
      root = V(lerp(DOOR_X + 0.3, -0.35, sineIO(seg(t, 21.5, 23.5))), 0, Z1 - 0.65).lerp(SAM_WIN, t > 23.5 ? k : 0); yaw = t > 23.5 ? (Math.sin(Math.max(0, t - 21.5) * 0.55) > 0 ? -1.4 : 1.4) : yawTo(root, SAM_WIN); sp = t > 23.5 ? 1.0 * Math.abs(Math.sin(Math.max(0, t - 21.5) * 0.55)) : 1.2;
      tgt = t > 24.0 ? V(WIN_X, 1.35, Z1) : POVc;
      if (t > T_BUZZ) { yaw = lerp(yaw, yawTo(root, POVc) + 0.5, sineIO(seg(t, T_BUZZ, T_BUZZ + 0.6))); sp *= 1 - seg(t, T_BUZZ, T_BUZZ + 0.4);
        handL = loc(root, yaw, -0.05, hipY + 0.5, 0.3); dirL = V(0, 0.4, 1).applyAxisAngle(V(0, 1, 0), yaw); tgt = handL.clone(); if (t > 30.8) tgt = POVc; }
      expr = t > 31 ? { eyes: 0.85, worry: -0.4, mouthBase: 0.04 } : cold;
    } else if (t < 44.0) { root = SAM_WIN.clone().add(V(0.4 * sineIO(seg(t, T_FLASH, T_FLASH + 0.6)), 0, -0.3 * sineIO(seg(t, T_FLASH, T_FLASH + 0.6)))); yaw = yawTo(root, V(WIN_X, 0, Z1)); tgt = V(WIN_X, 1.35, Z1); expr = { eyes: 1.15, worry: 0.6, mouthBase: 0.1 }; hipY = 0.85; lean = 0.25; }
    else if (t < 51.0) { root = SAM_WIN.clone().add(V(0.4, 0, -0.3)).lerp(SAM_GRAB, sineIO(seg(t, 44.0, 45.2))); yaw = yawTo(root, POVc); expr = panic; sp = t < 45.2 ? 2 : 0;
      if (t > T_GRAB - 0.25) { const g = sineIO(seg(t, T_GRAB - 0.25, T_GRAB)); handL = loc(root, yaw, -0.1, 1.2, 0.3).lerp(camLocal(0.0, -0.22, -0.22), g * (1 - sineIO(seg(t, 47.5, 48.5)))); dirL = POVc.clone().sub(handL).normalize(); } }
    else if (t < T_WHIP - 0.2) { root = SAM_GRAB.clone(); yaw = yawTo(root, V(WIN_X, 0, Z1)); tgt = V(WIN_X, 1.35, Z1); expr = panic; hipY = 0.9; lean = 0.2; }
    else {                 // drops to his knees, rips back the rug, opens the hatch, climbs in, reaches up
      const k = sineIO(seg(t, T_WHIP - 0.2, T_WHIP + 0.5)); root = SAM_GRAB.clone().lerp(SAM_RUG, k); yaw = yawTo(root, POVc);
      hipY = lerp(0.9, 0.52, k); lean = lerp(0.2, 0.55, k); expr = panic; tgt = t > 64.0 ? POVc : V(HATCH.x, 0, HATCH.z);
      const rugGrab = V(HATCH.x - 0.5, 0.05, HATCH.z - 0.3), handle = V(HATCH.x, 0.06, HATCH.z + 0.3);
      if (t < 64.0) { handL = rugGrab.clone().lerp(V(HATCH.x - 1.0, 0.5, HATCH.z), sineIO(seg(t, 62.7, 63.6))); handR = handL.clone().add(V(0.3, 0, 0)); }
      else if (t < 67.2) { handR = handle.clone().lerp(S.hatchPivot.localToWorld(V(0, 0.05, 0.75)), sineIO(seg(t, 66.0, 67.0))); handL = loc(root, yaw, -0.3, 0.4, 0.2); }
      if (t > 70.9) {    // in the hole up to the chest, hand reaching up to us
        const d = sineIO(seg(t, 70.9, 72.0)); root = SAM_RUG.clone().lerp(V(HATCH.x, 0, HATCH.z + 0.05), d); hipY = lerp(hipY, -0.15, d); lean = lerp(lean, 0.05, d);
        handL = loc(root, yaw, -0.2, lerp(0.5, 1.1, d), 0.25); handR = loc(root, yaw, 0.3, 0.45, 0.25);
        if (t > 79.4) { const u = sineIO(seg(t, 79.4, 80.3)); handR = loc(root, yaw, 0.15, lerp(0.45, 1.05, u), lerp(0.25, 0.55, u)); dirR = POVc.clone().sub(handR).normalize(); }
      }
      gun = t < 62.4;
    }
    if (!handR) { const sh = loc(root, yaw, 0.2, hipY + 0.5, 0.05), aimT = t > 45.3 && t < 51 ? POVc.clone().add(V(0.6, -0.8, 0)) : V(DOOR_X + 0.3, 1.0, Z1); handR = sh.clone().add(aimT.clone().sub(sh).normalize().multiplyScalar(0.45)); dirR = aimT.clone().sub(handR).normalize(); }
    if (!handL) handL = loc(root, yaw, -0.26, hipY - 0.05, 0.1);
    if (t > 66.5 && t < 80.4) handR = handR.clone().add(V(Math.sin(t * 41) * 0.008, Math.sin(t * 37) * 0.008, 0));          // shaking
    if (sp > 0) { const gt = gait(t, root, yaw, sp, 0.3); footL = gt.footL; footR = gt.footR; }
    else if (hipY < 0.6) { footL = loc(root, yaw, -0.15, 0, -0.45); footR = loc(root, yaw, 0.15, 0, -0.45); }
    else { footL = loc(root, yaw, -0.13, 0, 0); footR = loc(root, yaw, 0.14, 0, 0.04); }
    if (t > 70.9) { footL = loc(root, yaw, -0.12, -0.8, 0); footR = loc(root, yaw, 0.12, -0.8, 0); }
    p = { x: root.x, z: root.z, yaw, hipY, lean, handL, handR, handLdir: dirL, handRdir: dirR, gun, footL, footR, expr };
    Object.assign(p, headLook(root, yaw, lean, hipY + 0.78, tgt));
  }
  poseSam(sam, p, t, Math.min(1, mouth * 1.15));
  sam.shoes.forEach(s => s.visible = t < 70.9);
  sPhone.visible = t > T_BUZZ - 0.2 && t < 35.4;
  faceLight.intensity = sPhone.visible ? 2.2 * (0.85 + 0.15 * Math.sin(t * 3)) : 0;
  if (sPhone.visible) faceLight.position.copy(sam.head.getWorldPosition(V(0, 0, 0)).add(V(0, -0.1, 0.25).applyAxisAngle(V(0, 1, 0), sam.root.rotation.y)));
}

// ============================================================ THE OFFICER (outside)
function copAt(t) {
  const mouth = mouthOf('cop', t);
  const vis = t > 50.8; cop.root.visible = vis;
  [...cop.hands, ...cop.boots, cop.armL.a, cop.armL.j, cop.armL.b, cop.armR.a, cop.armR.j, cop.armR.b, cop.legL.a, cop.legL.j, cop.legL.b, cop.legR.a, cop.legR.j, cop.legR.b].forEach(m => m.visible = vis);
  if (!vis) { copLight.intensity = 0; return null; }
  let root = COP_OUT.clone().add(V(-0.6 * (1 - seg(t, T_FLASH - 1.5, 44)), 0, 1.0 * (1 - seg(t, T_FLASH - 1.5, 44)))), sp = t < 44 ? 0.6 : 0;
  if (t > T_WHIP) { root = COP_OUT.clone().lerp(V(DOOR_X + 0.5, 0, Z1 + 0.75), sineIO(seg(t, T_WHIP, 66))); sp = t < 66 ? 1.2 : 0; }
  const win = V(WIN_X, CRACK_Y, Z1); let yaw = yawTo(root, win);
  cop.torso.updateMatrixWorld();
  const tilt = sineIO(seg(t, 55.4, 56.4)) * (1 - sineIO(seg(t, 59.5, 60.5)));
  const aim = win.clone().add(V(0, -1.0 * tilt, 0.6 * tilt));
  const handL = cop.torso.localToWorld(V(-0.22, 0.62, 0.35)).lerp(cop.torso.localToWorld(V(-0.25, 0.35, 0.3)), tilt);
  const handR = loc(root, yaw, 0.3, 0.95, 0.15);
  let footL, footR, hipY = 1.02;
  if (sp > 0) { const gt = gait(t, root, yaw, sp, 0.2); footL = gt.footL; footR = gt.footR; hipY -= gt.bob * 0.5; }
  else { footL = loc(root, yaw, -0.13, 0, 0); footR = loc(root, yaw, 0.14, 0, 0.04); }
  if (t > 70 && t < 78) { const kick = T_BANGS.concat([74.8, 76.2]).reduce((a, b) => a + Math.max(0, Math.sin(seg(t, b - 0.25, b + 0.15) * Math.PI)), 0); footR = loc(root, yaw, 0.14, 0.45 * kick, 0.5 * kick); }
  const p = { x: root.x, z: root.z, yaw, hipY, lean: 0, handL, handR, handLdir: aim.clone().sub(handL).normalize(), footL, footR, flash: true, flashOn: 1, gun: false, blood: true, badge: false };
  const dir = win.clone().sub(V(root.x, hipY + 0.8, root.z));
  p.headYaw = Math.max(-1, Math.min(1, wrapA(Math.atan2(dir.x, dir.z) - yaw))); p.headPitch = Math.max(-0.8, Math.min(0.8, -Math.atan2(dir.y, Math.hypot(dir.x, dir.z))));
  poseOfficer(cop, p, t, Math.min(1, mouth * 1.2));
  cop.face.shadow.material.opacity = 0.7; cop.beam.material.opacity = 0.02;
  copLight.position.copy(root).add(V(0.4, 1.6, -0.8)); copLight.intensity = 3.0;
  return { aim, tilt };
}

// ============================================================ POV hands
function applyHand(h, s) { h.g.visible = s.vis; if (s.vis) { h.g.position.copy(s.pos); h.g.quaternion.copy(basisQuat(s.fd, s.pn)); poseHand(h, s.pose); h.g.updateMatrixWorld(); } }
function handsAt(t) {
  const R = { pos: V(0, 0, 0), fd: V(0, 0, -1), pn: V(0, -1, 0), pose: 'rest', vis: false };
  const L = { pos: V(0, 0, 0), fd: V(0, 0, -1), pn: V(0, -1, 0), pose: 'rest', vis: false };
  const pump = (amp = 1) => { const ph = t * 2.7 * Math.PI; for (const [H, s] of [[R, 1], [L, -1]]) { const sw = Math.sin(ph + (s > 0 ? 0 : Math.PI));
    H.pos = camLocal(s * 0.24, -0.5 + 0.17 * Math.max(0, sw) * amp, -0.32 - 0.06 * sw * amp); H.fd = camDir(-s * 0.3, 0.6, -1); H.pn = camDir(-s * 0.8, -0.2, 0); H.pose = 'grip'; H.vis = sw > -0.2; } };
  if (t < T_TRIP) pump();
  if (t >= T_TRIP && t < 12.4) {           // hands slap into the mud
    const k = ease.out(seg(t, T_TRIP + 0.15, T_TRIP + 0.4)), up = sineIO(seg(t, 11.8, 12.4));
    for (const [H, s] of [[R, 1], [L, -1]]) { const g = camera.position.clone().add(camDir(s * 0.22, 0, -1).setY(0).normalize().multiplyScalar(0.35)).setY(0.04);
      H.pos = camLocal(s * 0.25, -0.45, -0.3).lerp(g.add(camDir(s * 0.15, 0, 0)), k * (1 - up)); H.fd = camDir(0, -0.2, -1).setY(-0.15).normalize(); H.pn = V(0, -1, 0); H.pose = 'flat'; H.vis = k > 0.05 && up < 0.95; }
  }
  if (t > 12.6 && t < 18.9) pump(0.6);
  if (t > 42.8 && t < 45.6) {              // reaching for the door
    const k = sineIO(seg(t, 43.6, 44.8)) * (1 - ease.out(seg(t, T_GRAB, T_GRAB + 0.3)));
    R.pos = camLocal(0.25, -0.5, -0.25).lerp(camLocal(0.05, -0.12, -0.42), k); R.fd = camDir(0, 0.2, -1); R.pn = camDir(-1, 0, 0); R.pose = 'open'; R.vis = k > 0.05;
  }
  if (t > 51.6 && t < T_WHIP) {            // fingers on the shutter slat
    const k = sineIO(seg(t, 51.6, 52.4)); L.pos = camLocal(-0.3, -0.5, -0.2).lerp(V(WIN_X - 0.22, CRACK_Y + 0.12, Z1 - 0.04), k); L.fd = V(0.2, 0.3, 1).normalize(); L.pn = V(0, 0, 1); L.pose = 'hover'; L.vis = false;
  }
  return { R, L };
}

// ============================================================ lens rain (outside only)
const fx = document.getElementById('rainfx').getContext('2d');
let sdr = 5; const rrr = () => (sdr = (sdr * 16807) % 2147483647) / 2147483647;
const STREAKS = Array.from({ length: 170 }, () => ({ x: rrr() * 760, y: rrr() * 1280, l: 40 + rrr() * 90, s: 1800 + rrr() * 1400, a: 0.12 + rrr() * 0.22 }));
const DROPS = Array.from({ length: 34 }, () => ({ x: rrr() * 720, y: rrr() * 1280, r: 6 + rrr() * 16, t0: rrr() * 12, life: 2 + rrr() * 4 }));
function lensRain(t, amt) {
  fx.clearRect(0, 0, 720, 1280); if (amt <= 0) return; fx.lineCap = 'round';
  for (const s of STREAKS) { const y = ((s.y + t * s.s) % 1500) - 150, x = s.x - y * 0.08; fx.strokeStyle = `rgba(200,215,235,${s.a * amt})`; fx.lineWidth = 2; fx.beginPath(); fx.moveTo(x, y); fx.lineTo(x - s.l * 0.08, y + s.l); fx.stroke(); }
  for (const d of DROPS) { const age = ((t - d.t0) % (d.life + 1) + d.life + 1) % (d.life + 1); if (age > d.life) continue;
    const a = amt * Math.min(1, age * 3) * (1 - age / d.life) * 0.55, y = d.y + age * 18; const g = fx.createRadialGradient(d.x - d.r * 0.3, y - d.r * 0.3, 1, d.x, y, d.r);
    g.addColorStop(0, `rgba(255,255,255,${a})`); g.addColorStop(0.5, `rgba(190,205,230,${a * 0.4})`); g.addColorStop(1, 'rgba(190,205,230,0)'); fx.fillStyle = g; fx.beginPath(); fx.arc(d.x, y, d.r, 0, 7); fx.fill(); }
}

// ============================================================ HUD
const titleEl = document.getElementById('title'), subEl = document.getElementById('subtxt'), ctaEl = document.getElementById('cta');
function hudAt(t) {
  const a = easeOut(seg(t, 0.15, 0.55)), out = seg(t, 5.0, 5.4);
  titleEl.style.opacity = a * (1 - out); titleEl.style.transform = `translateX(${-12 * (1 - a)}px)`;
  let sub = null;
  for (const l of DLG.lines) for (const c of l.chunks) if (t >= c.t0 && t < c.t1) sub = { c, spk: l.spk };
  subEl.textContent = sub ? sub.c.text : ''; subEl.className = sub ? sub.spk : '';
  if (sub) subEl.style.transform = `translateX(-50%) scale(${0.91 + 0.09 * easeOut(seg(t, sub.c.t0, sub.c.t0 + 0.1))})`;
  document.getElementById('sub').style.top = t > FREEZE + 0.4 ? '1150px' : '839px';
  ctaEl.style.display = t > FREEZE + 0.9 ? 'block' : 'none';
  if (t > FREEZE + 0.9) {
    const k = easeOut(seg(t, FREEZE + 0.9, FREEZE + 1.2)); ctaEl.querySelector('.q').style.transform = `scale(${0.85 + 0.15 * k})`; ctaEl.style.opacity = k;
    ctaEl.querySelectorAll('.btn').forEach((b, i) => { const kb = easeOut(seg(t, FREEZE + 1.1 + i * 0.15, FREEZE + 1.4 + i * 0.15)); b.style.transform = `scale(${0.8 + 0.2 * kb})`; b.style.opacity = kb; });
  }
}

// ============================================================ render
window.setHud = on => { document.getElementById('hud').style.display = on ? 'block' : 'none'; document.getElementById('rainfx').style.display = on ? 'block' : 'none'; };
window.renderAt = (tReal) => {
  const t = Math.min(tReal, FREEZE);
  const inside = t >= 19.4;
  // set animation
  S.door.rotation.y = t < T_KICK ? 0 : t < T_SLAM ? 1.55 * easeOut(seg(t, T_KICK, T_KICK + 0.25)) - 0.08 * Math.sin(seg(t, T_KICK + 0.25, T_KICK + 0.7) * Math.PI) : 1.55 * (1 - easeOut(seg(t, T_SLAM, T_SLAM + 0.18)));
  const bang = T_BANGS.concat([74.8, 76.2]).reduce((a, b) => a + Math.exp(-Math.pow((t - b) / 0.07, 2)), 0);
  if (t > 70) S.door.rotation.y = 0.03 * bang + 0.004 * Math.sin(t * 60) * (t > 71.5 ? 1 : 0);
  S.bolt.position.x = 0.92 - 0.14 - 0.07 * easeOut(seg(t, T_SLAM + 0.3, T_SLAM + 0.5)) + 0.006 * bang;
  // rug ripped away, hatch opened
  const rugK = sineIO(seg(t, 62.7, 63.6));
  S.rug.position.set(HATCH.x - 1.05 * rugK, 0.03 + 0.4 * Math.sin(rugK * Math.PI), HATCH.z + 0.2 * rugK); S.rug.rotation.set(-Math.PI / 2 + 2.6 * rugK, 0, 0.3 * rugK);
  S.hatchPivot.rotation.x = -1.9 * sineIO(seg(t, 66.0, 67.2));
  // police lights behind us in the woods
  const ph = (t * 2.2) % 1;
  S.pol.forEach((g, i) => { g.position.set(-6 + i * 6 + 3 * Math.sin(t * 0.7 + i), 2.2, 18 + 2 * Math.sin(t * 0.4 + i)); g.material.opacity = (t < 18 ? 1 : 0.3) * ((i % 2 ? ph >= 0.5 : ph < 0.5) ? 1 : 0.15); });
  S.beams.forEach(b => b.visible = false);
  // light through the shutters: moonlight, then the flashlight
  const fl = t > T_FLASH ? easeOut(seg(t, T_FLASH, T_FLASH + 0.15)) * (t > T_WHIP ? 0.35 : 1) : 0;
  const peekK = t > 50.8 && t < T_WHIP + 0.3 ? 1 : 0;
  S.shafts.forEach((m, i) => m.material.opacity = (0.02 + 0.13 * fl * (0.8 + 0.2 * Math.sin(t * 3 + i))) * (1 - peekK));
  S.dust.forEach(d => { d.d.material.opacity = 0.15 + 0.6 * fl; d.d.position.copy(d.p).add(V(0.05 * Math.sin(t * 0.6 + d.ph), 0.04 * Math.sin(t * 0.8 + d.ph * 2), 0)); });
  S.winGlow.material.opacity = (0.15 + 0.85 * fl) * (1 - peekK); S.lightPool.material.opacity = 0.12 * fl; S.flashIn.intensity = 2.2 * fl;
  S.inLight.intensity = inside ? 2.6 : 0;
  scene.fog.near = inside ? 4 : 4; scene.fog.far = inside ? 30 : 25;
  amb.intensity = inside ? 1.25 : 1.45;
  // characters (use last frame's camera; fine at 30 fps)
  samAt(t); const cs = copAt(t);
  // camera
  const c = camAt(tReal);
  camera.position.set(c.x, c.y, c.z); camera.rotation.set(c.pitch * D2R, c.yaw * D2R, (c.roll || 0) * D2R); camera.updateMatrixWorld(); setFocal(c.f);
  const bf = new THREE.Matrix4().makeRotationY(c.yaw * D2R); bf.setPosition(c.x, c.y, c.z);
  const hs = handsAt(t); applyHand(handR, hs.R); applyHand(handL, hs.L);
  placeArm(armR, handR.g.localToWorld(V(0, 0.004, 0.045)), 1, bf, hs.R.vis);
  placeArm(armL, handL.g.localToWorld(V(0, 0.004, 0.045)), -1, bf, hs.L.vis);
  // lens: police wash behind us, flashlight glare at the window / through the crack
  const look = camDir(0, 0, -1), backFacing = Math.max(0, look.z);
  lens.uniforms.policeAmt.value = t < 18 ? (0.06 + 0.22 * backFacing) * (ph < 0.5 ? 1 : 0.6) : 0;
  lens.uniforms.policeCol.value.copy(ph < 0.5 ? new THREE.Color(1, 0.12, 0.1) : new THREE.Color(0.12, 0.28, 1));
  lens.uniforms.policeDim.value = inside ? 0.25 : 0.38;
  lens.uniforms.glareAmt.value = 0;
  if (fl > 0 && t < T_WHIP) {
    let gp = null, amt = 0;
    if (t > 52.0 && cs) { cop.flashlight.updateMatrixWorld(); gp = projectLens(cop.flashlight.localToWorld(V(0, 0, -0.15))); amt = 0.32 * (1 - 0.6 * cs.tilt); }
    else if (t < 42.6) { gp = projectLens(S.winGlow.position); amt = 0.35; }
    if (gp) { lens.uniforms.glarePos.value.copy(gp); lens.uniforms.glareAmt.value = amt * (1 + 0.05 * Math.sin(t * 40)); }
  }
  lens.uniforms.flash.value = (t > T_FLASH && t < T_FLASH + 0.08 ? 0.12 : 0) + (t > T_STING && t < T_STING + 0.06 ? 0.08 : 0);
  lens.uniforms.vign.value = 0.3 + 0.55 * easeOut(seg(tReal, FREEZE - 0.15, FREEZE + 0.4));
  renderFrame();
  lensRain(t, inside ? 0 : 1);
  hudAt(tReal);
};
window.DURATION = DUR;
window.sceneReady = Promise.resolve(true);
