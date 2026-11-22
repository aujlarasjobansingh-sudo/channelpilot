// EPISODE 3 (FINALE) — "The Late-Night Gas Station Shift" — full timeline (POV cashier).
// Continues straight from Episode 2's freeze frame: hand on the cruiser's rear door handle.
import { THREE, scene, camera, setFocal, projectLens, renderFrame, lens, D2R, sineIO, sineIn, easeOut, seg, lerp, F, rr } from './core.js';
import { buildSet, drawRain, C, EYE, car, phone, phoneTex, body, ep3, BARRIER_Z } from './set.js';
import { makeHand, poseHand, makeArm, placeArm, basisQuat, makeMaya, poseMaya, makeOfficer, poseOfficer, makeSam, poseSam } from './chars.js';

const V = (x, y, z) => new THREE.Vector3(x, y, z);
await Promise.all([500, 600, 700, 800, 900].map(w => document.fonts.load(`${w} 40px Rubik`)));
const DLG = await (await fetch('out/dialogue.json')).json();
buildSet();
scene.background = new THREE.Color('#04060b');
scene.fog = new THREE.Fog('#05070c', 9, 62);
camera.far = 120; camera.updateProjectionMatrix();
const amb = new THREE.AmbientLight('#f4f7ff', 1.7); scene.add(amb);
const sun = new THREE.DirectionalLight('#ffffff', 0.7); sun.position.set(-1, 6, 2); scene.add(sun);
const canLight = new THREE.PointLight('#ffffff', 60, 14, 1.4); canLight.position.set(ep3.canopy.x, 3.7, ep3.canopy.z); scene.add(canLight);
const maya = makeMaya(), cop = makeOfficer(), sam = makeSam();
const handR = makeHand(1), handL = makeHand(-1), armR = makeArm(), armL = makeArm();
const BLACK = 76.9, DUR = 85;
// Maya's wounded arm
const mayaBlood = new THREE.Mesh(new THREE.SphereGeometry(0.055, 14, 10), new THREE.MeshToonMaterial({ color: '#9a1414' })); mayaBlood.scale.set(1, 1.7, 0.6); scene.add(mayaBlood);
maya.knife.visible = false;

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
function pathAt(t, keys) {
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
function gait(t, root, yaw, speed, phase0 = 0) {
  const ph = phase0 + t * (speed > 1.5 ? 2.7 : 1.8) * Math.PI * 2;
  const fwd = V(Math.sin(yaw), 0, Math.cos(yaw)), rt = V(Math.cos(yaw), 0, -Math.sin(yaw)), stride = Math.min(0.42, 0.18 * speed);
  const off = s => ph + (s > 0 ? Math.PI : 0);
  const foot = s => root.clone().add(rt.clone().multiplyScalar(s * 0.1)).add(fwd.clone().multiplyScalar(stride * Math.sin(off(s)))).add(V(0, Math.max(0, Math.cos(off(s))) * 0.13 * Math.min(1, speed), 0));
  const hand = s => root.clone().add(rt.clone().multiplyScalar(s * 0.26)).add(fwd.clone().multiplyScalar(-stride * 0.8 * Math.sin(off(s)) + 0.05)).add(V(0, 0.95 + 0.06 * Math.abs(Math.sin(ph)), 0));
  return { footL: foot(-1), footR: foot(1), handL: hand(-1), handR: hand(1), bob: 0.03 * Math.abs(Math.sin(ph)) };
}
const headLook = (root, yaw, lean, headH, pt) => {
  const dir = V(pt.x - root.x, pt.y - headH, pt.z - root.z);
  return { headYaw: Math.max(-1.3, Math.min(1.3, wrapA(Math.atan2(dir.x, dir.z) - yaw))), headPitch: Math.max(-0.75, Math.min(0.75, -Math.atan2(dir.y, Math.hypot(dir.x, dir.z)) - lean)) };
};

// ============================================================ key places
const CAR_X = 1.2, CAR_Z = -10.3;
const P0 = V(2.95, 0, -11.85);                       // where Ep2 froze: beside the rear door
const OPENING = V(2.1, 0.95, -11.0);                 // the dark backseat behind the opened door
const SAM_OUT = V(2.25, 0, -12.45);
const COP0 = V(1.35, 0, -7.9);                        // by the store doors, aiming over the cruiser's roof
const CAN = V(ep3.canopy.x - 0.3, 0, ep3.canopy.z - 1.85);   // under the canopy lights
const CROUCH = V(-4.6, 0, BARRIER_Z + 0.68), SAMC = V(-5.38, 0, BARRIER_Z + 0.72);
const CY = 0.92;                                      // crouched eye height
const SPARK = V(CAR_X + 1.15, 1.47, CAR_Z - 0.82);
const T_SHOT = 9.6, T_GUN = 63.9, T_SIREN = 65.0, T_GRAB = 67.4;
const pcX = t => t < 65 ? lerp(95, 26, sineIO(seg(t, 23.0, 65))) : lerp(26, 6.5, easeOut(seg(t, 65, 71.4)));
const PC_Z = BARRIER_Z - 1.95;

// ============================================================ CAMERA
const RUN = [
  [9.95, V(P0.x, EYE - 0.25, P0.z)], [11.0, V(2.7, EYE - 0.05, -13.4)], [12.4, V(1.6, EYE - 0.05, -15.2)], [14.0, V(0.2, EYE - 0.05, -17.2)],
  [15.8, V(-1.5, EYE - 0.05, -19.1)], [17.8, V(-3.1, EYE - 0.05, -20.8)], [19.8, V(-4.3, EYE - 0.1, -21.9)], [21.2, V(CROUCH.x, 1.25, CROUCH.z - 0.05)], [22.2, V(CROUCH.x, CY, CROUCH.z)],
];
const runPos = t => pathAt(t, RUN);
const ROAD_FAR = V(-60, 1.0, PC_Z), STATION = V(11.2, 1.25, -13.9);
function camAt(tReal) {
  const t = Math.min(tReal, BLACK);
  const c = { x: P0.x, y: EYE, z: P0.z, yaw: 0, pitch: 0, roll: 0, f: 540 };
  const from = V(c.x, c.y, c.z);
  if (t < 9.95) {
    // hand on the handle → yank → the backseat → Sam climbs out → GUNSHOT
    const handle = V(2.12, 0.9, -11.28);
    const yH = camYawTo(P0, handle), pH = camPitchTo(V(P0.x, EYE, P0.z), handle);
    const yO = camYawTo(P0, OPENING), pO = camPitchTo(V(P0.x, EYE, P0.z), OPENING);
    const samHead = sam.head.getWorldPosition(V(0, 0, 0));
    const yS = unwrapNear(camYawTo(P0, samHead), yO), pS = camPitchTo(V(P0.x, EYE, P0.z), samHead);
    const k1 = ease.snap(seg(t, 0.95, 1.35)), k2 = sineIO(seg(t, 3.3, 5.0));
    c.yaw = lerp(lerp(yH, yO, k1), yS, k2); c.pitch = lerp(lerp(pH, pO + 2, k1), pS - 4, k2);
    c.f = lerp(lerp(620, 560, k1), 600, k2);
    c.z = P0.z - 0.25 * k1 + 0.15 * k2; c.x = P0.x + 0.2 * k1;
    if (t > 7.4 && t < 9.5) { const g = sineIO(seg(t, 7.4, 7.9)) * (1 - sineIO(seg(t, 8.9, 9.4))); c.yaw += 14 * g; }  // follow Sam's glance at the store
    if (t > T_SHOT) { const d = sineIO(seg(t, T_SHOT, T_SHOT + 0.25)); c.y -= 0.25 * d; c.pitch += 8 * d; }
  } else if (t < 22.3) {
    // the sprint to the highway
    const p = runPos(t), q = runPos(t + 0.3), pq = runPos(t - 0.3);
    let yaw = camYawTo(pq, q);
    if (t < 10.6) yaw = lerp(camYawTo(P0, OPENING), yaw, sineIO(seg(t, 9.95, 10.6)));
    const back = sineIO(seg(t, 12.6, 13.25)) * (1 - sineIO(seg(t, 14.3, 14.95)));     // look back: the officer is running after us
    yaw = lerp(yaw, unwrapNear(camYawTo(p, V(COP0.x + 2.5, 1.4, -10.5)), yaw), back);
    const ph = t * 2.7 * Math.PI * 2, amp = 1 - sineIO(seg(t, 20.6, 22.0));
    c.x = p.x; c.y = p.y + (0.045 * Math.abs(Math.sin(ph)) - 0.02) * amp; c.z = p.z;
    const settle = sineIO(seg(t, 20.8, 22.2));
    c.yaw = lerp(yaw, unwrapNear(camYawTo(V(CROUCH.x, CY, CROUCH.z), V(30, 1.0, PC_Z)), yaw), settle) + noise(t, 1) * 1.8 * amp;
    c.pitch = -4 + 1.6 * Math.sin(ph * 2) * amp + noise(t, 2) * 1.3 * amp - 3 * back + settle * 3;
    c.roll = 1.5 * Math.sin(ph) * amp + noise(t, 3) * 0.9 * amp; c.f = 520;
  } else {
    // crouched behind the barrier
    c.x = CROUCH.x; c.y = CY; c.z = CROUCH.z;
    const eye = V(c.x, c.y, c.z);
    const yRoad = camYawTo(eye, V(30, 1.0, PC_Z)), pRoad = camPitchTo(eye, V(30, 1.15, PC_Z));
    const samHead = sam.head.getWorldPosition(V(0, 0, 0));
    const yCar = camYawTo(eye, V(pcX(t), 1.0, PC_Z));
    const ySam = unwrapNear(camYawTo(eye, samHead), yRoad), pSam = camPitchTo(eye, samHead);
    const yStation = unwrapNear(camYawTo(eye, STATION), ySam), pStation = camPitchTo(eye, STATION);
    let yaw = yRoad, pitch = pRoad, f = 560;
    // 22.3–28.4: rise slightly over the barrier, watch the headlights come out of the fog
    const peek = sineIO(seg(t, 23.0, 24.0)) * (1 - sineIO(seg(t, 31.4, 32.0)));
    c.y += 0.18 * peek; f = lerp(560, 760, sineIO(seg(t, 23.4, 25.0))) - 200 * sineIO(seg(t, 28.2, 28.8));
    yaw = lerp(yRoad, unwrapNear(yCar, yRoad), sineIO(seg(t, 23.4, 25.0)));
    // 28.4: Sam — "don't step into the road yet" (staring back at the station)
    const kS = sineIO(seg(t, 28.3, 28.9)); yaw = lerp(yaw, ySam + 6, kS); pitch = lerp(pitch, pSam - 3, kS);
    // 31.6: turn around over the shoulder: the station
    const kB = sineIO(seg(t, 31.6, 32.9)); yaw = lerp(yaw, yStation, kB); pitch = lerp(pitch, pStation, kB); if (kB > 0) f = lerp(f, 700, kB);
    f += 650 * sineIO(seg(t, 32.6, 38.5));                                    // creeping push-in on the officer under the lights
    // 39.5 buzz → 40.2 look down at the phone
    const kP = sineIO(seg(t, 40.1, 40.8)); yaw = lerp(yaw, yStation + 20, kP); pitch = lerp(pitch, -24, kP); f = lerp(f, 540, kP);
    // 50.4: slow pan left to Sam — he's staring at the screen
    const kL = sineIO(seg(t, 50.4, 53.6)); yaw = lerp(yaw, ySam + 3, kL); pitch = lerp(pitch, pSam - 6, kL); f = lerp(f, 600, kL);
    const kW = sineIO(seg(t, 53.6, 54.3)) * (1 - sineIO(seg(t, 54.9, 55.5))); pitch -= 16 * kW;     // tilt down: no handcuffs
    // 55: backing away
    const kBack = sineIO(seg(t, 55.0, 56.0)); c.x += 0.28 * kBack; c.z += 0.08 * kBack; f -= 30 * kBack;
    // 58–63.7: he smiles — slow push in
    f += 120 * sineIO(seg(t, 58.0, 63.6));
    // gun + sirens: frame Sam with the police car coming up behind him
    const kG = sineIO(seg(t, 63.8, 64.4)); f = lerp(f, 560, kG); pitch = lerp(pitch, pSam - 2, kG);
    const kR = sineIO(seg(t, 64.9, 65.6)); yaw = lerp(yaw, lerp(ySam, unwrapNear(yCar, ySam), 0.28), kR); f = lerp(f, 470, kR);
    if (t >= 70.2) {    // dragged backwards toward the trees, facing the road and the spotlight
      const k = sineIO(seg(t, 70.2, 71.0)), dr = seg(t, 70.4, 76.9);
      c.x = lerp(c.x, lerp(CROUCH.x + 0.3, -10.5, dr), k); c.z = lerp(c.z, lerp(CROUCH.z, -18.6, dr), k); c.y = lerp(c.y, 1.2 + 0.08 * Math.sin(t * 9), k);
      const pcPos = V(pcX(t) - 0.9, 1.4, PC_Z + 0.95);
      yaw = lerp(yaw, unwrapNear(camYawTo(V(c.x, c.y, c.z), pcPos), yaw), k); pitch = lerp(pitch, camPitchTo(V(c.x, c.y, c.z), pcPos) + 4, k);
      f = lerp(f, 520, k);
      yaw += noise(t, 7) * 5 * k; pitch += noise(t, 8) * 4 * k; c.roll = noise(t, 9) * 6 * k;
    }
    if (t > T_GRAB && t < 70.4) { const d = t - T_GRAB; yaw += 6 * Math.exp(-d * 6) * Math.sin(d * 30); pitch += 5 * Math.exp(-d * 6); }
    c.yaw = yaw + noise(t, 4) * 0.5; c.pitch = pitch + noise(t, 5) * 0.4; c.f = f;
    if (t < 31.4) c.roll = noise(t, 6) * 0.4;
  }
  // impacts
  for (const [t0, a] of [[0.95, 1.2], [T_SHOT, 2.4], [39.5, 0.5], [T_GUN + 0.4, 0.9], [T_SIREN, 0.7], [T_GRAB, 2.2]]) {
    if (t > t0 && t < t0 + 0.5) { const d = t - t0; c.yaw += a * Math.exp(-d * 10) * Math.sin(d * 55); c.pitch += a * 0.7 * Math.exp(-d * 10) * Math.cos(d * 47); }
  }
  return c;
}

// ============================================================ SAM
function samAt(t) {
  const mouth = mouthOf('sam', t);
  let p;
  const POVc = camera.position.clone();
  const fear = { eyes: 1.15, worry: 1.1, mouthBase: 0.25 }, calm = { eyes: 0.95, worry: -0.2, smirk: 1, mouthBase: 0.04 };
  if (t < 9.95) {
    // crouched in the dark backseat → scrambles out → stands, clutching his wrists
    const out = sineIO(seg(t, 3.0, 4.6)), up = sineIO(seg(t, 4.2, 5.2));
    const root = V(1.95, 0, -10.7).lerp(SAM_OUT, out); const yaw = yawTo(root, POVc);
    const hipY = lerp(0.55, 0.98, up) - 0.05 * Math.sin(t * 9) * (1 - up), lean = lerp(0.9, 0.12, up);
    const cuff = loc(root, yaw, 0.0, hipY + 0.28, 0.32);
    p = { x: root.x, z: root.z, yaw, hipY, lean, handL: cuff.clone().add(V(0, 0, 0)), handR: cuff.clone().add(V(0.02, 0.03, 0)),
      footL: loc(root, yaw, -0.13, 0, -0.05 + 0.2 * (1 - out)), footR: loc(root, yaw, 0.14, 0, 0.06), expr: { ...fear, eyes: 1.2 } };
    const lookStore = t > 7.4 && t < 9.4;
    Object.assign(p, headLook(root, yaw, lean, hipY + 0.78, lookStore ? V(COP0.x, 1.6, COP0.z) : POVc));
    if (t > T_SHOT) { const d = sineIO(seg(t, T_SHOT, T_SHOT + 0.3)); p.hipY -= 0.3 * d; p.lean += 0.4 * d; }
  } else if (t < 22.2) {
    // running ahead of us (left), wrists still held together
    const lead = Math.min(t + 0.55, 21.9);
    const rp = runPos(lead); const nx = runPos(lead + 0.2);
    const yaw = yawTo(rp, nx); const side = V(Math.cos(yaw), 0, -Math.sin(yaw));
    const root = V(rp.x, 0, rp.z).add(side.multiplyScalar(-0.75));
    if (t > 20.8) root.lerp(SAMC, sineIO(seg(t, 20.8, 22.0)));
    const crouch = sineIO(seg(t, 21.0, 22.0));
    const gt = gait(t, root, yaw, 2.6 * (1 - crouch), 0.7);
    p = { x: root.x, z: root.z, yaw: lerp(yaw, yawTo(SAMC, V(SAMC.x, 0, BARRIER_Z)), crouch), hipY: lerp(0.92 - gt.bob, 0.48, crouch), lean: lerp(0.35, 0.5, crouch),
      footL: gt.footL, footR: gt.footR, expr: fear };
    const cuff = loc(root, p.yaw, 0, p.hipY + 0.3, 0.3); p.handL = cuff; p.handR = cuff.clone().add(V(0.02, 0.03, 0));
    if (crouch > 0) { p.footL = loc(root, p.yaw, -0.16, 0, 0.1); p.footR = loc(root, p.yaw, 0.17, 0, -0.18); }
    Object.assign(p, headLook(root, p.yaw, p.lean, p.hipY + 0.78, t < 20 ? V(COP0.x, 1.5, COP0.z) : V(30, 1, PC_Z)));
  } else {
    // crouched behind the barrier on our left
    const root = SAMC.clone(); const facePOV = yawTo(root, POVc), faceRoad = yawTo(root, V(root.x, 0, BARRIER_Z));
    let yaw = faceRoad, hipY = 0.5, lean = 0.45;
    const turn = sineIO(seg(t, 50.8, 52.2));                     // body opens toward us
    yaw = lerp(faceRoad, facePOV, 0.55 * turn + 0.45 * sineIO(seg(t, 63.8, 64.4)));
    let expr = { ...fear };
    let tgt = t < 28.0 ? V(30, 1, PC_Z) : t < 49 ? STATION : null;
    if (t >= 49 && t < 55.0) tgt = phone.getWorldPosition(V(0, 0, 0));                         // staring at OUR phone screen
    if (t >= 55.0) tgt = camera.position.clone();
    if (t >= 49) expr = { eyes: 0.9, worry: 0, mouthBase: 0.03 };
    if (t >= 57.6) expr = { ...calm };
    if (t >= T_SIREN + 0.5) expr = { eyes: 1.25, worry: 0.6, mouthBase: 0.2 };              // eyes widen at the sirens
    if (t >= T_SIREN + 0.5 && t < 66.6) tgt = V(pcX(t), 1.2, PC_Z);
    // hands: wrists together → lowered apart (no cuffs) → gun out of the jacket → aimed at us → grab the collar
    const shoulder = loc(root, yaw, 0.18, hipY + 0.55, 0.05);
    const cuff = loc(root, yaw, 0, hipY + 0.3, 0.3);
    const low = sineIO(seg(t, 53.4, 54.5));
    let handL = cuff.clone().lerp(loc(root, yaw, -0.25, hipY + 0.05, 0.25), low), handR = cuff.clone().add(V(0.02, 0.03, 0)).lerp(loc(root, yaw, 0.25, hipY + 0.05, 0.25), low);
    let dirR = null, gun = false, dirL = null;
    if (t > T_GUN) {
      const draw = sineIO(seg(T_GUN, T_GUN, T_GUN + 0.25) * 0 + seg(t, T_GUN, T_GUN + 0.3)), aim = sineIO(seg(t, T_GUN + 0.25, T_GUN + 0.6));
      const inJacket = loc(root, yaw, 0.08, hipY + 0.42, 0.12);
      const aimT = POVc.clone().add(V(0, -0.35, 0)); const aimPt = shoulder.clone().add(V(0, -0.1, 0)).add(aimT.clone().sub(shoulder).normalize().multiplyScalar(0.5));
      handR = handR.clone().lerp(inJacket, draw).lerp(aimPt, aim); gun = t > T_GUN + 0.2; dirR = aimT.clone().add(V(0.25, 0, 0)).sub(handR).normalize();
    }
    if (t > T_GRAB - 0.35) {   // left hand lunges for our collar
      const g = sineIO(seg(t, T_GRAB - 0.35, T_GRAB));
      handL = handL.clone().lerp(camLocal(0.02, -0.17, -0.2), g); dirL = POVc.clone().sub(handL).normalize();
    }
    if (t > 69.6) { const u = sineIO(seg(t, 69.6, 70.3)); hipY = lerp(hipY, 0.95, u); lean = lerp(lean, 0.1, u); }
    p = { x: root.x, z: root.z, yaw, hipY, lean, handL, handR, handRdir: dirR, handLdir: dirL, gun,
      footL: loc(root, yaw, -0.16, 0, 0.12), footR: loc(root, yaw, 0.18, 0, -0.2), expr };
    if (tgt) Object.assign(p, headLook(root, yaw, lean, hipY + 0.78, tgt));
    if (t >= 58 && t < 63.8) p.headRoll = 0.12 * sineIO(seg(t, 58.4, 59.4));               // head tilt with the smile
    if (t >= 70.2) { sam.root.visible = false; }
  }
  sam.root.visible = t < 70.3;
  [...sam.hands, ...sam.shoes, sam.armL.a, sam.armL.j, sam.armL.b, sam.armR.a, sam.armR.j, sam.armR.b, sam.legL.a, sam.legL.j, sam.legL.b, sam.legR.a, sam.legR.j, sam.legR.b].forEach(m => m.visible = t < 70.3);
  poseSam(sam, p, t, Math.min(1, mouth * 1.15));
}

// ============================================================ OFFICER (fake cop)
function copAt(t) {
  const mouth = mouthOf('cop', t);
  let root, yaw, sp = 0, gun = true, aimAt = camera.position.clone(), hipY = 1.02, lean = 0;
  if (t < 10.4) { root = COP0.clone(); yaw = yawTo(root, camera.position); }
  else if (t < 19.5) { const k = sineIO(seg(t, 10.4, 19.5)); root = COP0.clone().lerp(V(4.8, 0, -13.4), k); yaw = yawTo(COP0, V(4.8, 0, -13.4)); sp = 2.4 * (1 - seg(t, 18.5, 19.5)); }
  else if (t < 24.0) { const k = sineIO(seg(t, 19.5, 24.0)); root = V(4.8, 0, -13.4).lerp(CAN, k); yaw = yawTo(V(4.8, 0, -13.4), CAN); sp = 1.0; gun = false; }
  else { root = CAN.clone(); yaw = yawTo(root, V(-4.6, 0, -22.4)); gun = false; }
  if (t > 12.4 && t < 15.0) { aimAt = V(-1, 1.5, -18); }
  cop.torso.updateMatrixWorld();
  const sh = cop.torso.localToWorld(V(0.1, 0.56, 0)), ad = aimAt.clone().sub(sh).normalize();
  let handR, handL, dirR = null;
  if (gun) { handR = sh.clone().add(ad.clone().multiplyScalar(0.55)); dirR = ad; handL = handR.clone().add(V(-0.06, -0.05, 0).applyAxisAngle(V(0, 1, 0), yaw)); }
  else { handR = loc(root, yaw, 0.28, 0.92, 0.1); handL = loc(root, yaw, -0.28, 0.92, 0.1); }
  if (t > 12.4 && t < 15.0) { handL = loc(root, yaw, -0.25, 1.55, 0.35); }   // shouting, waving us back
  let footL, footR;
  if (sp > 0) { const gt = gait(t, root, yaw, sp, 0.4); footL = gt.footL; footR = gt.footR; hipY -= gt.bob * 0.6; }
  else { footL = loc(root, yaw, -0.13, 0, 0); footR = loc(root, yaw, 0.14, 0, 0.04); }
  const p = { x: root.x, z: root.z, yaw, hipY, lean, handL, handR, handRdir: dirR, footL, footR, flash: false, flashOn: 0, gun, blood: true, badge: false };
  const dir = (t > 24 ? V(-4.6, 1, -22.4) : camera.position.clone()).sub(V(root.x, hipY + 0.8, root.z));
  p.headYaw = Math.max(-1, Math.min(1, wrapA(Math.atan2(dir.x, dir.z) - yaw))); p.headPitch = Math.max(-0.8, Math.min(0.8, -Math.atan2(dir.y, Math.hypot(dir.x, dir.z))));
  poseOfficer(cop, p, t, Math.min(1, mouth * 1.2));
  cop.face.shadow.material.opacity = 0.55;
  cop.gun.children.forEach(ch => { if (ch.isSprite) ch.material.opacity = t > T_SHOT && t < T_SHOT + 0.08 ? 1 : 0; });
  cop.gun.scale.setScalar(t > T_SHOT && t < T_SHOT + 0.08 ? 1.0 : 1.0);
}

// ============================================================ MAYA — running for the highway, holding her bleeding arm
function mayaAt(t) {
  const vis = t > 32.0 && t < 50;
  maya.root.visible = vis; mayaBlood.visible = vis;
  [...maya.hands, ...maya.feet, maya.armL.a, maya.armL.j, maya.armL.b, maya.armR.a, maya.armR.j, maya.armR.b, maya.legL.a, maya.legL.j, maya.legL.b, maya.legR.a, maya.legR.j, maya.legR.b].forEach(m => m.visible = vis);
  if (!vis) return;
  const a = V(14.6, 0, -9.0), b = V(11.8, 0, -21.5), k = seg(t, 32.0, 44.0);
  const root = a.clone().lerp(b, k), yaw = yawTo(a, b);
  const gt = gait(t, root, yaw, 2.2, 1.3);
  maya.torso.updateMatrixWorld();
  const armPt = loc(root, yaw, -0.2, 1.12, 0.12);
  const p = { x: root.x, z: root.z, yaw, hipY: 0.9 - gt.bob, lean: 0.3, footL: gt.footL, footR: gt.footR, handL: loc(root, yaw, -0.18, 1.0, 0.1), handR: armPt.clone().add(V(0.02, 0.02, 0.06)),
    knife: false, expr: { eyes: 1.15, worry: 1.2, mouthBase: 0.3 }, headYaw: 0.5, headPitch: 0.05 };
  poseMaya(maya, p, t, 0.2);
  mayaBlood.position.copy(maya.armL.b.position); mayaBlood.quaternion.copy(maya.armL.b.quaternion);
}

// ============================================================ POV hands
function applyHand(h, s) { h.g.visible = s.vis; if (s.vis) { h.g.position.copy(s.pos); h.g.quaternion.copy(basisQuat(s.fd, s.pn)); poseHand(h, s.pose); h.g.updateMatrixWorld(); } }
let phoneShown = false;
function handsAt(t) {
  const R = { pos: V(0, 0, 0), fd: V(0, 0, -1), pn: V(0, -1, 0), pose: 'rest', vis: false };
  const L = { pos: V(0, 0, 0), fd: V(0, 0, -1), pn: V(0, -1, 0), pose: 'rest', vis: false };
  phoneShown = false;
  if (t < 3.0) {           // grip the handle, yank the door open, let go
    car.g.updateMatrixWorld(); car.handle.updateMatrixWorld();
    const hp = car.handle.getWorldPosition(V(0, 0, 0)).add(V(0.0, -0.01, -0.05));
    const tr = V(Math.sin(t * 53) * 0.004, Math.sin(t * 47) * 0.004, 0).multiplyScalar(t < 0.8 ? 1 : 0);
    const grab = sineIO(seg(t, 0.25, 0.75)), go = sineIO(seg(t, 1.6, 2.6));
    R.pos = hp.clone().add(V(0.04, 0.03, -0.08).multiplyScalar(1 - grab)).add(tr).lerp(camLocal(0.3, -0.55, -0.2), go);
    R.fd = V(-0.6, -0.05, -0.7).normalize(); R.pn = V(0.1, 0.1, 1).normalize(); R.pose = grab > 0.6 ? 'grip' : 'hover'; R.vis = go < 0.98;
  }
  if (t > 9.95 && t < 21.0) {   // pumping arms while sprinting
    const ph = t * 2.7 * Math.PI;
    for (const [H, s] of [[R, 1], [L, -1]]) {
      const sw = Math.sin(ph + (s > 0 ? 0 : Math.PI));
      H.pos = camLocal(s * 0.24, -0.5 + 0.17 * Math.max(0, sw), -0.32 - 0.06 * sw); H.fd = camDir(-s * 0.3, 0.6, -1); H.pn = camDir(-s * 0.8, -0.2, 0); H.pose = 'grip'; H.vis = sw > -0.2;
    }
  }
  if (t > 21.6 && t < 31.6) {   // left hand braced on the barrier top
    const k = sineIO(seg(t, 21.6, 22.3)) * (1 - sineIO(seg(t, 31.0, 31.6)));
    L.pos = V(camera.position.x - 0.16, 0.81, BARRIER_Z + 0.12).lerp(camLocal(-0.3, -0.6, -0.2), 1 - k); L.fd = V(0.3, 0, -1); L.pn = V(0, -1, 0); L.pose = 'flat'; L.vis = k > 0.05;
  }
  if (t > 24.9 && t < 27.8) {   // pointing at the headlights
    const k = sineIO(seg(t, 24.9, 25.4)) * (1 - sineIO(seg(t, 27.2, 27.8)));
    R.pos = camLocal(0.06, -0.12, -0.36).lerp(camLocal(0.3, -0.6, -0.2), 1 - k); R.fd = camDir(-0.25, 0.08, -1); R.pn = camDir(0, -1, 0); R.pose = 'point'; R.vis = k > 0.05;
  }
  if (t > 39.9 && t < 70.4) {   // the phone
    const up = sineIO(seg(t, 39.9, 40.9)), down = sineIO(seg(t, 50.4, 53.0)), away = sineIO(seg(t, 63.8, 64.3));
    const hold = camLocal(0.0, -0.03, -0.185), low = camLocal(0.16, -0.36, -0.3), gone = camLocal(0.3, -0.7, -0.2);
    R.pos = gone.clone().lerp(hold, up).lerp(low, down).lerp(gone, away);
    R.fd = camDir(-0.05, 1, 0.12); R.pn = camDir(0, 0, -1); R.pose = 'grip'; R.vis = up > 0.02 && away < 0.98;
    phoneShown = R.vis;
  }
  if (t > 64.0 && t < 70.0) {   // hands up at the gun
    const up = sineIO(seg(t, 64.0, 64.5)) * (1 - sineIO(seg(t, 69.4, 70.0)));
    for (const [H, s] of [[R, 1], [L, -1]]) {
      const tr = V(Math.sin(t * (37 + s * 4)) * 0.004, Math.sin(t * (29 - s * 5)) * 0.004, 0);
      H.pos = camLocal(s * 0.17, -0.12, -0.36).add(tr).lerp(camLocal(s * 0.25, -0.6, -0.2), 1 - up); H.fd = camDir(s * 0.1, 1, -0.25); H.pn = camDir(0, 0, -1); H.pose = 'open'; H.vis = up > 0.05;
    }
  }
  return { R, L };
}

// ============================================================ phone screen (emergency alert)
const PHONE_SCREEN = (() => { let last = -1; return t => {
  const st = t < 41.6 ? 0 : 1, k = easeOut(seg(t, 41.6, 42.0)), fr = Math.floor(t * 10);
  if (fr === last) return; last = fr;
  const g = phoneTex.userData.canvas.getContext('2d'), w = 400, h = 844;
  const bg = g.createLinearGradient(0, 0, 0, h); bg.addColorStop(0, '#1c2433'); bg.addColorStop(1, '#090b11'); g.fillStyle = bg; g.fillRect(0, 0, w, h);
  g.fillStyle = '#e8ecf4'; g.textAlign = 'center'; g.font = F(300, 96); g.fillText('2:21', w / 2, 200); g.font = F(500, 24); g.fillText('Saturday, November 22', w / 2, 240);
  g.fillStyle = 'rgba(255,255,255,0.65)'; g.font = F(600, 18); g.textAlign = 'left'; g.fillText('9:41', 22, 32); g.textAlign = 'right'; g.fillText('5G ▮▮▮', w - 22, 32);
  if (st) {
    g.save(); g.translate(0, -60 * (1 - k)); g.globalAlpha = k;
    g.fillStyle = 'rgba(40,14,14,0.96)'; rr(g, 16, 290, w - 32, 330, 26); g.fill(); g.strokeStyle = '#ff4a3d'; g.lineWidth = 4; g.stroke();
    g.fillStyle = '#f5d23a'; g.beginPath(); g.moveTo(52, 344); g.lineTo(72, 310); g.lineTo(92, 344); g.closePath(); g.fill(); g.fillStyle = '#1a1a1a'; g.font = F(900, 24); g.textAlign = 'center'; g.fillText('!', 72, 341);
    g.textAlign = 'left'; g.fillStyle = '#ff5a4d'; g.font = F(900, 25); g.fillText('EMERGENCY ALERT', 106, 336);
    g.fillStyle = '#ffffff'; g.font = F(800, 26); g.fillText('UPDATE:', 34, 392);
    const lines = ['Police impersonator is', 'NOT acting alone.', 'Second suspect described', 'as male, early 20s,', 'dark jacket.'];
    g.fillStyle = '#f5d23a'; g.font = F(800, 29); lines.forEach((l, i) => g.fillText(l, 34, 436 + i * 38));
    g.restore();
  }
  // raindrops on the glass
  let sd = 11 + Math.floor(t * 2); const r = () => (sd = (sd * 16807) % 2147483647) / 2147483647;
  for (let i = 0; i < 26; i++) { const x = r() * w, y = r() * h, rad = 5 + r() * 12; const gr = g.createRadialGradient(x - rad * 0.3, y - rad * 0.3, 1, x, y, rad);
    gr.addColorStop(0, 'rgba(255,255,255,0.55)'); gr.addColorStop(0.6, 'rgba(180,200,230,0.18)'); gr.addColorStop(1, 'rgba(180,200,230,0)'); g.fillStyle = gr; g.beginPath(); g.arc(x, y, rad, 0, 7); g.fill(); }
  phoneTex.needsUpdate = true;
}; })();

// ============================================================ lens rain (screen space, outdoors)
const fx = document.getElementById('rainfx').getContext('2d');
let sdr = 5; const rrr = () => (sdr = (sdr * 16807) % 2147483647) / 2147483647;
const STREAKS = Array.from({ length: 170 }, () => ({ x: rrr() * 760, y: rrr() * 1280, l: 40 + rrr() * 90, s: 1800 + rrr() * 1400, a: 0.12 + rrr() * 0.22 }));
const DROPS = Array.from({ length: 34 }, () => ({ x: rrr() * 720, y: rrr() * 1280, r: 6 + rrr() * 16, t0: rrr() * 12, life: 2 + rrr() * 4 }));
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
const titleEl = document.getElementById('title'), subEl = document.getElementById('subtxt'), endEl = document.getElementById('end'), blackEl = document.getElementById('black');
function hudAt(t) {
  const a = easeOut(seg(t, 0.15, 0.55)), out = seg(t, 4.6, 5.0);
  titleEl.style.opacity = a * (1 - out); titleEl.style.transform = `translateX(${-12 * (1 - a)}px)`;
  let sub = null;
  for (const l of DLG.lines) for (const c of l.chunks) if (t >= c.t0 && t < c.t1) sub = { c, spk: l.spk };
  subEl.textContent = sub && t < BLACK ? sub.c.text : ''; subEl.className = sub ? sub.spk : '';
  if (sub) subEl.style.transform = `translateX(-50%) scale(${0.91 + 0.09 * easeOut(seg(t, sub.c.t0, sub.c.t0 + 0.1))})`;
  blackEl.style.opacity = t >= BLACK ? 1 : 0;
  endEl.style.display = t > BLACK + 0.3 ? 'block' : 'none';
  if (t > BLACK + 0.3) {
    const k = easeOut(seg(t, BLACK + 0.3, BLACK + 0.8)), kb = easeOut(seg(t, BLACK + 1.4, BLACK + 1.9));
    endEl.querySelector('.e1').style.opacity = k; endEl.querySelector('.e1').style.transform = `scale(${0.85 + 0.15 * k})`;
    endEl.querySelector('.e2').style.opacity = kb; endEl.querySelector('.e2').style.transform = `translateY(${16 * (1 - kb)}px)`;
  }
}

// ============================================================ render
function policeAt(t, rate = 2.15) {
  const ph = (t * rate) % 1, half = ph < 0.5, q = (ph % 0.5) / 0.5, pulse = (q < 0.18 ? 1 : q < 0.3 ? 0.15 : q < 0.48 ? 1 : 0.2);
  return { red: half ? pulse : 0.08, blue: half ? 0.08 : pulse };
}
window.setHud = on => { document.getElementById('hud').style.display = on ? 'block' : 'none'; document.getElementById('rainfx').style.display = on ? 'block' : 'none'; };
window.renderAt = (tReal) => {
  const t = Math.min(tReal, BLACK);
  drawRain(t);
  // set pieces first (characters read camera position from the previous pose; fine at 30 fps)
  car.g.position.set(CAR_X, 0, CAR_Z); car.doorPivot.rotation.y = -1.1;
  ep3.rearPivot.rotation.y = 1.25 * easeOut(seg(t, 0.95, 1.35)) - 0.06 * Math.sin(seg(t, 1.35, 1.8) * Math.PI);
  const pol = policeAt(t);
  car.red.material.color.set(pol.red > 0.5 ? '#ff3a3a' : '#4a0c0c'); car.blue.material.color.set(pol.blue > 0.5 ? '#3a6bff' : '#0b1440');
  car.redGlow.material.opacity = pol.red; car.blueGlow.material.opacity = pol.blue;
  car.redPool.position.set(CAR_X + 0.2, 0.015, -11.5); car.bluePool.position.set(CAR_X + 0.2, 0.016, -11.5);
  car.redPool.material.opacity = 0.25 * pol.red; car.bluePool.material.opacity = 0.25 * pol.blue;
  car.palms.visible = false; car.truck.visible = false;
  // gunshot sparks
  ep3.sparks.forEach((s, i) => { const d = t - T_SHOT; s.s.visible = d > 0 && d < 0.7; if (s.s.visible) { s.s.position.copy(SPARK).addScaledVector(s.v, d).add(V(0, -4.9 * d * d, 0)); s.s.material.opacity = 1 - d / 0.7; } });
  // the real police car
  const px = pcX(t); ep3.pc.position.set(px, 0, PC_Z); ep3.pc.visible = t > 22.8;
  const siren = t > T_SIREN, sp = policeAt(t, 2.8);
  ep3.pcRed.material.opacity = siren ? sp.red : 0; ep3.pcBlue.material.opacity = siren ? sp.blue : 0;
  ep3.pcSpot.position.set(0.9, 1.5, -0.95); ep3.pc.rotation.y = Math.PI; ep3.pcSpot.material.opacity = t > 71.6 ? 1 : 0;
  ep3.pcBeam.material.opacity = 0.05;
  // camera
  const c = camAt(tReal);
  camera.position.set(c.x, c.y, c.z); camera.rotation.set(c.pitch * D2R, c.yaw * D2R, (c.roll || 0) * D2R); camera.updateMatrixWorld(); setFocal(c.f);
  body.visible = false;
  // characters
  samAt(t); copAt(t); mayaAt(t);
  // hands + arms + phone
  const bf = new THREE.Matrix4().makeRotationY(c.yaw * D2R); bf.setPosition(c.x, c.y, c.z);
  const hs = handsAt(t); applyHand(handR, hs.R); applyHand(handL, hs.L);
  placeArm(armR, handR.g.localToWorld(V(0, 0.004, 0.045)), 1, bf, hs.R.vis);
  placeArm(armL, handL.g.localToWorld(V(0, 0.004, 0.045)), -1, bf, hs.L.vis);
  phone.visible = phoneShown;
  if (phoneShown) {
    phone.position.copy(handR.g.localToWorld(V(0, 0.03, -0.05)));
    const toCam = camera.position.clone().sub(phone.position).normalize();
    phone.quaternion.copy(basisQuat(camDir(0, -1, 0), toCam.clone().negate())); phone.rotateX(Math.PI / 2); phone.rotateZ(Math.PI);
    phone.lookAt(camera.position); phone.rotateZ(0);
    PHONE_SCREEN(t);
  }
  // lens: police wash (the cruiser behind us, then the real car), gunshot flash, spotlight glare
  const camToCar = Math.max(0, -camDir(0, 0, -1).dot(V(CAR_X - c.x, 0, CAR_Z - c.z).normalize()));
  let wash = (0.18 + 0.12 * camToCar) * Math.max(pol.red, pol.blue) * Math.max(0.25, 1 - Math.hypot(c.x - CAR_X, c.z - CAR_Z) / 16);
  let wcol = pol.red >= pol.blue ? new THREE.Color(1, 0.12, 0.1) : new THREE.Color(0.12, 0.28, 1);
  if (siren) { const w2 = 0.3 * Math.max(sp.red, sp.blue); if (w2 > wash) { wash = w2; wcol = sp.red >= sp.blue ? new THREE.Color(1, 0.12, 0.1) : new THREE.Color(0.12, 0.28, 1); } }
  lens.uniforms.policeAmt.value = wash; lens.uniforms.policeCol.value.copy(wcol); lens.uniforms.policeDim.value = 0.4;
  lens.uniforms.flash.value = (t > T_SHOT && t < T_SHOT + 0.07 ? 0.35 : 0) + (t > T_SIREN && t < T_SIREN + 0.06 ? 0.06 : 0);
  lens.uniforms.glareAmt.value = 0;
  if (t > 71.6) {
    ep3.pc.updateMatrixWorld(); const lp = ep3.pcSpot.getWorldPosition(V(0, 0, 0)), s2 = projectLens(lp);
    const sweep = 0.5 + 0.5 * Math.sin((t - 71.6) * 2.2 - 1.2);
    if (s2) { lens.uniforms.glarePos.value.copy(s2); lens.uniforms.glareAmt.value = (0.15 + 0.35 * sweep) * (0.6 + 0.6 * seg(t, 74.5, 76.8)); }
    lens.uniforms.flash.value += 0.05 * seg(t, 76.0, 76.9) + 0.05 * Math.pow(sweep, 10);
  } else if (t > 23.0 && t < 71.6 && !(t > 31.4 && t < 53.5)) {   // oncoming headlights flare through the fog
    ep3.pc.updateMatrixWorld(); const lp = ep3.pc.localToWorld(V(2.5, 0.78, 0)), s2 = projectLens(lp);
    if (s2) { lens.uniforms.glarePos.value.copy(s2); lens.uniforms.glareAmt.value = 0.08 + 0.22 * seg(px, 95, 10); }
  }
  lens.uniforms.vign.value = 0.35;
  amb.intensity = 2.0;
  renderFrame();
  lensRain(t, t < BLACK ? 1 : 0);
  hudAt(tReal);
};
window.__dbg = () => ({ cop: cop.root.position, vis: cop.root.visible, hip: cop.torso.position, cam: camera.position });
window.DURATION = DUR;
window.sceneReady = Promise.resolve(true);
