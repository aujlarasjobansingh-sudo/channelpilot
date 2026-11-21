// Characters: POV hands/arms (posable fingers, IK arms), Maya, the Officer.
import { THREE, scene, M, noOutline, INK, add, box, cyl, sph, capsule, orient, glowSprite, glowMat } from './core.js';

const V = (x, y, z) => new THREE.Vector3(x, y, z);
const unitCyl = (rt, rb, color, parent) => add(new THREE.Mesh(new THREE.CylinderGeometry(rt, rb, 1, 18), M(color)), parent);

// two-bone IK solve (returns elbow/knee position)
export function ik(S, T, a, b, pole) {
  const v = T.clone().sub(S); const d = Math.max(1e-4, Math.min(v.length(), (a + b) * 0.999)); const u = v.normalize();
  const ca = (a * a + d * d - b * b) / (2 * a * d), sa = Math.sqrt(Math.max(0, 1 - ca * ca));
  const p = pole.clone().sub(u.clone().multiplyScalar(pole.dot(u))).normalize();
  return S.clone().add(u.clone().multiplyScalar(a * ca)).add(p.multiplyScalar(a * sa));
}
export function basisQuat(fingerDir, palmNormal) {    // local -z = fingerDir, local -y = palmNormal
  const z = fingerDir.clone().normalize().negate();
  let y = palmNormal.clone().normalize().negate(); y.sub(z.clone().multiplyScalar(y.dot(z))).normalize();
  const x = new THREE.Vector3().crossVectors(y, z);
  return new THREE.Quaternion().setFromRotationMatrix(new THREE.Matrix4().makeBasis(x, y, z));
}

// ------------------------------------------------------------------ POV hand with posable fingers
const SKIN = '#d9a079';
export const HAND_POSES = {
  flat: { c: [0.12, 0.1, 0.1, 0.12], th: 0.15, sp: 0.05 },
  wipe: { c: [0.35, 0.4, 0.45, 0.5], th: 0.3, sp: 0.02 },
  grip: { c: [1.0, 1.1, 1.1, 1.1], th: 0.8, sp: 0 },
  point: { c: [0.0, 1.25, 1.3, 1.3], th: 0.9, sp: 0 },
  open: { c: [0.0, 0.0, 0.05, 0.1], th: 0.0, sp: 0.18 },
  hover: { c: [0.3, 0.38, 0.46, 0.55], th: 0.35, sp: 0.06 },
  rest: { c: [0.55, 0.6, 0.65, 0.7], th: 0.4, sp: 0.02 },
};
export function makeHand(side) {      // side: +1 right, -1 left
  const g = new THREE.Group(); scene.add(g);
  const palm = sph(0.043, SKIN, 0, 0, 0, g); palm.scale.set(1.05, 0.55, 1.15);
  const fingers = [];
  for (let i = 0; i < 4; i++) {
    const k = new THREE.Group(); k.position.set(side * (-0.029 + i * 0.0195), -0.002, -0.042); g.add(k);
    const len1 = [0.026, 0.029, 0.027, 0.021][i], len2 = len1 * 0.75;
    const p1 = capsule(0.0105, len1, SKIN, k); p1.rotation.x = Math.PI / 2; p1.position.z = -len1 / 2;
    const k2 = new THREE.Group(); k2.position.z = -len1 - 0.004; k.add(k2);
    const p2 = capsule(0.0095, len2, SKIN, k2); p2.rotation.x = Math.PI / 2; p2.position.z = -len2 / 2;
    fingers.push({ k, k2, i });
  }
  const tb = new THREE.Group(); tb.position.set(-side * 0.036, -0.006, -0.01); g.add(tb);
  const t1 = capsule(0.012, 0.026, SKIN, tb); t1.rotation.x = Math.PI / 2; t1.position.z = -0.016;
  const tb2 = new THREE.Group(); tb2.position.z = -0.034; tb.add(tb2);
  const t2 = capsule(0.011, 0.018, SKIN, tb2); t2.rotation.x = Math.PI / 2; t2.position.z = -0.011;
  return { g, fingers, tb, tb2, side };
}
export function poseHand(h, A, B, k = 0) {   // blend between two named poses
  const a = HAND_POSES[A], b = HAND_POSES[B || A];
  h.fingers.forEach((f, i) => {
    const c = a.c[i] + (b.c[i] - a.c[i]) * k, sp = (a.sp + (b.sp - a.sp) * k) * (i - 1.5);
    f.k.rotation.set(-c * 1.15, h.side * -sp * 0.4, 0); f.k2.rotation.x = -c * 1.25;
  });
  const th = a.th + (b.th - a.th) * k;
  h.tb.rotation.set(-0.2 - th * 0.5, -h.side * (0.75 - th * 0.55), h.side * 0.3); h.tb2.rotation.x = -th * 0.9;
}
// POV arm: shoulder (torso frame) → elbow → wrist; navy polo short sleeve
const UPPER = 0.31, FORE = 0.29;
const JK = '#7a2232', CUFF = '#c7b28c';
export function makeArm() {
  return { fore: unitCyl(0.05, 0.058, JK), elbow: sph(0.06, JK, 0, 0, 0), upper: unitCyl(0.064, 0.064, JK), sleeve: unitCyl(0.07, 0.066, JK), cuff: unitCyl(0.047, 0.05, CUFF) };
}
export function placeArm(arm, wrist, side, bf, visible) {
  for (const k of ['fore', 'elbow', 'upper', 'sleeve', 'cuff']) arm[k].visible = visible;
  if (!visible) return;
  const S = V(0.19 * side, -0.27, 0.03).applyMatrix4(bf);
  const pole = V(0.7 * side, -1, 0.35).transformDirection(bf);
  const E = ik(S, wrist, UPPER, FORE, pole);
  const Wr = E.clone().add(wrist.clone().sub(E).normalize().multiplyScalar(FORE));
  const cu = Wr.clone().lerp(E, 0.16); orient(arm.fore, cu, E); orient(arm.cuff, Wr.clone().lerp(E, -0.05), cu); arm.elbow.position.copy(E);
  const sl = S.clone().lerp(E, 0.7); orient(arm.sleeve, S, sl); orient(arm.upper, sl, E);
}

// ------------------------------------------------------------------ generic limb
function makeLimb(r1, r2, c1, c2) {
  return { a: unitCyl(r1, r1 * 0.92, c1), j: sph(r1 * 0.98, c1 === c2 ? c1 : c2, 0, 0, 0, null, 18), b: unitCyl(r2, r2 * 0.85, c2) };
}
function setLimb(L, S, E, T) { orient(L.a, S, E); L.j.position.copy(E); orient(L.b, E, T); }

// ------------------------------------------------------------------ MAYA
export function makeMaya() {
  const hood = '#7f858e', hoodDark = '#6b7179', legs = '#2a2e38', skin = '#e2ae8b', hair = '#2a1f1b';
  const root = new THREE.Group(); scene.add(root);
  const torso = new THREE.Group(); root.add(torso);
  const tb = add(new THREE.Mesh(new THREE.CapsuleGeometry(0.16, 0.3, 8, 22), M(hood)), torso); tb.scale.set(1.28, 1, 0.86); tb.position.y = 0.26;
  for (const s of [-1, 1]) { const sh = sph(0.095, hood, s * 0.17, 0.47, 0, torso); sh.scale.set(1.05, 0.9, 1); }
  const pocket = add(new THREE.Mesh(new THREE.CapsuleGeometry(0.06, 0.16, 6, 16), M(hoodDark)), torso);
  pocket.rotation.z = Math.PI / 2; pocket.scale.set(1, 1, 0.45); pocket.position.set(0, 0.12, 0.13);
  const hoodBunch = sph(0.13, hood, 0, 0.56, -0.07, torso); hoodBunch.scale.set(1.25, 0.6, 0.9);
  for (const s of [-1, 1]) { const ds = cyl(0.006, 0.006, 0.16, '#cfd3d8', s * 0.04, 0.42, 0.135, torso, 8); ds.rotation.x = 0.1; }
  const hem = cyl(0.22, 0.22, 0.05, hoodDark, 0, -0.02, 0, torso); hem.scale.set(1, 1, 0.75);
  // head
  const head = new THREE.Group(); head.position.set(0, 0.69, 0.01); torso.add(head);
  cyl(0.045, 0.05, 0.12, skin, 0, -0.08, 0, head);
  const hs = sph(0.115, skin, 0, 0.03, 0, head); hs.scale.set(1, 1.08, 1);
  const cap = add(new THREE.Mesh(new THREE.SphereGeometry(0.124, 30, 18, 0, Math.PI * 2, 0, Math.PI * 0.55), M(hair)), head);
  cap.position.y = 0.04; cap.rotation.x = -0.3;
  // wet strands plastered along the sides of the face (kept clear of the eyes)
  const strands = [[-0.1, 0.02, 0.055, 0.12, 0.1], [0.102, 0.01, 0.055, -0.12, 0.1], [-0.085, 0.07, 0.075, 0.5, 0.06], [0.08, 0.075, 0.078, -0.55, 0.06], [-0.02, 0.118, 0.07, 1.25, 0.05]];
  for (const [x, y, z, rz, len] of strands) { const s = capsule(0.017, len, hair, head); s.position.set(x, y, z); s.rotation.set(0.15, 0, rz); s.scale.set(1, 1, 0.5); }
  for (const [x, z] of [[-0.08, -0.06], [0, -0.1], [0.08, -0.06], [-0.04, -0.09], [0.04, -0.09]]) { const s = capsule(0.032, 0.16, hair, head); s.position.set(x, -0.1, z); s.scale.set(1, 1, 0.6); }
  // face
  const face = {};
  face.eyes = [-1, 1].map(s => {
    const e = new THREE.Group(); e.position.set(s * 0.042, 0.035, 0.1135); e.rotation.y = s * 0.3; head.add(e);
    const white = add(new THREE.Mesh(new THREE.CircleGeometry(0.029, 28), noOutline(new THREE.MeshBasicMaterial({ color: '#ffffff' }))), e);
    const ring = add(new THREE.Mesh(new THREE.RingGeometry(0.029, 0.0335, 32), INK), e);
    const pupil = add(new THREE.Mesh(new THREE.CircleGeometry(0.012, 18), INK), e); pupil.position.z = 0.001;
    const shine = add(new THREE.Mesh(new THREE.CircleGeometry(0.004, 10), noOutline(new THREE.MeshBasicMaterial({ color: '#ffffff' }))), e); shine.position.set(0.005, 0.006, 0.002);
    const lid = add(new THREE.Mesh(new THREE.CircleGeometry(0.0365, 28, 0, Math.PI), M(skin, { flat: false })), e); lid.position.z = 0.0025; noOutline(lid.material = lid.material.clone());
    return { e, white, ring, pupil, shine, lid };
  });
  face.brows = [-1, 1].map(s => { const b = capsule(0.0065, 0.036, '#1f1714', head); b.position.set(s * 0.045, 0.085, 0.111); b.rotation.z = Math.PI / 2; return b; });
  face.nose = sph(0.014, skin, 0, 0.005, 0.116, head, 14);
  face.mouth = add(new THREE.Mesh(new THREE.CircleGeometry(0.02, 24), noOutline(new THREE.MeshBasicMaterial({ color: '#3a1716' }))), head); face.mouth.position.set(0, -0.045, 0.1125);
  face.tears = [-1, 1].map(s => { const t = sph(0.007, '#bfe6ff', s * 0.05, -0.0, 0.112, head, 10); t.scale.set(0.8, 1.4, 0.6); t.material = noOutline(new THREE.MeshBasicMaterial({ color: '#c8ecff' })); return t; });
  // limbs + hands + feet
  const armL = makeLimb(0.05, 0.043, hood, hood), armR = makeLimb(0.05, 0.043, hood, hood);
  const legL = makeLimb(0.065, 0.05, legs, legs), legR = makeLimb(0.065, 0.05, legs, legs);
  const hands = [-1, 1].map(s => { const g = new THREE.Group(); scene.add(g); const p = sph(0.034, skin, 0, 0, 0, g); p.scale.set(0.9, 0.6, 1.25); const th = capsule(0.01, 0.025, skin, g); th.position.set(-s * 0.028, 0, -0.012); th.rotation.set(Math.PI / 2, 0, -s * 0.6); for (let i = 0; i < 4; i++) { const f = capsule(0.0085, 0.025, skin, g); f.rotation.x = Math.PI / 2; f.position.set(-0.02 + i * 0.013, 0, -0.045); } return g; });
  const feet = [-1, 1].map(() => { const f = sph(0.045, skin, 0, 0, 0); f.scale.set(0.85, 0.5, 1.9); return f; });
  // knife (in right hand)
  const knife = new THREE.Group(); hands[1].add(knife);
  box(0.024, 0.02, 0.1, '#16171b', 0, 0, 0.0, knife);
  const blade = add(new THREE.Mesh(new THREE.BoxGeometry(0.006, 0.026, 0.15), M('#d9dee5')), knife); blade.position.set(0, 0.002, -0.125);
  const tip = add(new THREE.Mesh(new THREE.ConeGeometry(0.013, 0.04, 4), M('#d9dee5')), knife); tip.rotation.x = -Math.PI / 2; tip.position.set(0, 0.002, -0.215); tip.scale.set(0.45, 1, 1);
  const glint = glowSprite('#ffffff', 0.12, knife); glint.position.set(0.01, 0.01, -0.17);
  knife.rotation.set(0, 0, 0); knife.position.set(0, 0, -0.01); knife.scale.setScalar(1.35);
  return { root, torso, head, face, armL, armR, legL, legR, hands, feet, knife, glint, pocket };
}
export function makeLeo() {
  const hood = '#f2c230', hoodDark = '#c99a1c', legs = '#3b5687', skin = '#e8b791', hair = '#5a3a22';
  const root = new THREE.Group(); scene.add(root);
  const torso = new THREE.Group(); root.add(torso);
  const tb = add(new THREE.Mesh(new THREE.CapsuleGeometry(0.16, 0.3, 8, 22), M(hood)), torso); tb.scale.set(1.28, 1, 0.86); tb.position.y = 0.26;
  for (const s of [-1, 1]) { const sh = sph(0.095, hood, s * 0.17, 0.47, 0, torso); sh.scale.set(1.05, 0.9, 1); }
  const pocket = add(new THREE.Mesh(new THREE.CapsuleGeometry(0.06, 0.16, 6, 16), M(hoodDark)), torso);
  pocket.rotation.z = Math.PI / 2; pocket.scale.set(1, 1, 0.45); pocket.position.set(0, 0.12, 0.13);
  const hoodBunch = sph(0.13, hood, 0, 0.56, -0.07, torso); hoodBunch.scale.set(1.25, 0.6, 0.9);
  
  const hem = cyl(0.2, 0.2, 0.04, hoodDark, 0, 0.0, 0, torso); hem.scale.set(1, 1, 0.7);
  // head
  const head = new THREE.Group(); head.position.set(0, 0.69, 0.01); torso.add(head);
  cyl(0.045, 0.05, 0.12, skin, 0, -0.08, 0, head);
  const hs = sph(0.115, skin, 0, 0.03, 0, head); hs.scale.set(1, 1.08, 1);
  const cap = add(new THREE.Mesh(new THREE.SphereGeometry(0.124, 30, 18, 0, Math.PI * 2, 0, Math.PI * 0.55), M(hair)), head);
  cap.position.y = 0.04; cap.rotation.x = -0.3;
  // bowl cut: fringe above the brows + fuller back
  cap.scale.set(1.04, 1.02, 1.06); cap.rotation.x = -0.12;
  const fr = add(new THREE.Mesh(new THREE.CapsuleGeometry(0.03, 0.15, 6, 14), M(hair)), head); fr.rotation.z = Math.PI / 2; fr.position.set(0, 0.112, 0.083); fr.scale.set(1, 1, 0.55);
  for (const s of [-1, 1]) { const sb = capsule(0.03, 0.06, hair, head); sb.position.set(s * 0.105, 0.04, 0.0); sb.scale.set(0.6, 1, 1); }
  // red backpack + straps
  const bp = add(new THREE.Mesh(new THREE.CapsuleGeometry(0.13, 0.14, 6, 16), M('#a8322e')), torso); bp.scale.set(1.15, 1, 0.55); bp.position.set(0, 0.3, -0.2);
  for (const s of [-1, 1]) { const st = box(0.035, 0.34, 0.02, '#7e2420', s * 0.1, 0.33, 0.135, torso); st.rotation.x = 0.06; }
  // windbreaker zip + chest stripe
  box(0.012, 0.36, 0.01, '#9a7a18', 0, 0.28, 0.142, torso); box(0.36, 0.05, 0.02, '#2f6fd0', 0, 0.38, 0.13, torso);
  // face
  const face = {};
  face.eyes = [-1, 1].map(s => {
    const e = new THREE.Group(); e.position.set(s * 0.042, 0.035, 0.1135); e.rotation.y = s * 0.3; head.add(e);
    const white = add(new THREE.Mesh(new THREE.CircleGeometry(0.029, 28), noOutline(new THREE.MeshBasicMaterial({ color: '#ffffff' }))), e);
    const ring = add(new THREE.Mesh(new THREE.RingGeometry(0.029, 0.0335, 32), INK), e);
    const pupil = add(new THREE.Mesh(new THREE.CircleGeometry(0.012, 18), INK), e); pupil.position.z = 0.001;
    const shine = add(new THREE.Mesh(new THREE.CircleGeometry(0.004, 10), noOutline(new THREE.MeshBasicMaterial({ color: '#ffffff' }))), e); shine.position.set(0.005, 0.006, 0.002);
    const lid = add(new THREE.Mesh(new THREE.CircleGeometry(0.0365, 28, 0, Math.PI), M(skin, { flat: false })), e); lid.position.z = 0.0025; noOutline(lid.material = lid.material.clone());
    return { e, white, ring, pupil, shine, lid };
  });
  face.brows = [-1, 1].map(s => { const b = capsule(0.0065, 0.036, '#3a2414', head); b.position.set(s * 0.045, 0.085, 0.111); b.rotation.z = Math.PI / 2; return b; });
  face.nose = sph(0.014, skin, 0, 0.005, 0.116, head, 14);
  face.mouth = add(new THREE.Mesh(new THREE.CircleGeometry(0.02, 24), noOutline(new THREE.MeshBasicMaterial({ color: '#3a1716' }))), head); face.mouth.position.set(0, -0.045, 0.1125);
  face.tears = [-1, 1].map(s => { const t = sph(0.007, '#bfe6ff', s * 0.05, -0.0, 0.112, head, 10); t.scale.set(0.8, 1.4, 0.6); t.material = noOutline(new THREE.MeshBasicMaterial({ color: '#c8ecff' })); return t; });
  // limbs + hands + feet
  const armL = makeLimb(0.05, 0.043, hood, hood), armR = makeLimb(0.05, 0.043, hood, hood);
  const legL = makeLimb(0.065, 0.05, legs, legs), legR = makeLimb(0.065, 0.05, legs, legs);
  const hands = [-1, 1].map(s => { const g = new THREE.Group(); scene.add(g); const p = sph(0.034, skin, 0, 0, 0, g); p.scale.set(0.9, 0.6, 1.25); const th = capsule(0.01, 0.025, skin, g); th.position.set(-s * 0.028, 0, -0.012); th.rotation.set(Math.PI / 2, 0, -s * 0.6); for (let i = 0; i < 4; i++) { const f = capsule(0.0085, 0.025, skin, g); f.rotation.x = Math.PI / 2; f.position.set(-0.02 + i * 0.013, 0, -0.045); } return g; });
  const feet = [-1, 1].map(() => { const f = sph(0.05, '#f1f1ee', 0, 0, 0); f.scale.set(0.9, 0.55, 2.0); return f; });
  // knife (in right hand)
  const knife = new THREE.Group(); hands[1].add(knife);
  box(0.024, 0.02, 0.1, '#16171b', 0, 0, 0.0, knife);
  const blade = add(new THREE.Mesh(new THREE.BoxGeometry(0.006, 0.026, 0.15), M('#d9dee5')), knife); blade.position.set(0, 0.002, -0.125);
  const tip = add(new THREE.Mesh(new THREE.ConeGeometry(0.013, 0.04, 4), M('#d9dee5')), knife); tip.rotation.x = -Math.PI / 2; tip.position.set(0, 0.002, -0.215); tip.scale.set(0.45, 1, 1);
  const glint = glowSprite('#ffffff', 0.12, knife); glint.position.set(0.01, 0.01, -0.17);
  knife.visible = false;
  return { root, torso, head, face, armL, armR, legL, legR, hands, feet, knife, glint, pocket };
}
// pose = { x, z, yaw, hipY, lean, twist, side, headYaw, headPitch, handL, handR (world V3), handLdir, handRdir, footL, footR (world V3), expr }
export function poseMaya(m, p, t, mouth) {
  m.root.position.set(p.x, 0, p.z); m.root.rotation.y = p.yaw;
  m.torso.position.set(0, p.hipY, 0); m.torso.rotation.set(p.lean, p.twist || 0, p.side || 0, 'YXZ');
  m.head.rotation.set(p.headPitch || 0, p.headYaw || 0, p.headRoll || 0, 'YXZ');
  m.root.updateMatrixWorld(true);
  const sh = s => m.torso.localToWorld(V(s * 0.19, 0.47, 0));
  const hip = s => m.torso.localToWorld(V(s * 0.09, -0.02, 0));
  const fwd = V(0, 0, 1).transformDirection(m.root.matrixWorld), right = V(1, 0, 0).transformDirection(m.root.matrixWorld);
  for (const [s, L, hand, H, dir] of [[-1, m.armL, p.handL, m.hands[0], p.handLdir], [1, m.armR, p.handR, m.hands[1], p.handRdir]]) {
    const S = sh(s), E = ik(S, hand, 0.29, 0.27, right.clone().multiplyScalar(s * 0.6).add(V(0, -1, 0)).add(fwd.clone().multiplyScalar(-0.5)));
    const wr = E.clone().add(hand.clone().sub(E).normalize().multiplyScalar(0.27));
    setLimb(L, S, E, wr);
    const fd = dir || hand.clone().sub(E).normalize();
    H.position.copy(wr.clone().add(fd.clone().normalize().multiplyScalar(0.035)));
    H.quaternion.copy(basisQuat(fd, p.palm && s > 0 ? p.palm : V(0, -1, 0)));
  }
  for (const [s, L, foot, F] of [[-1, m.legL, p.footL, m.feet[0]], [1, m.legR, p.footR, m.feet[1]]]) {
    const S = hip(s), K = ik(S, foot, 0.44, 0.43, fwd.clone().add(V(0, 0.2, 0)));
    setLimb(L, S, K, foot); F.position.copy(foot).add(fwd.clone().multiplyScalar(0.05)); F.position.y = Math.max(0.02, foot.y - 0.01);
    F.rotation.y = p.yaw;
  }
  // face
  const e = p.expr || {};
  const open = e.eyes ?? 1, worry = e.worry ?? 0, cold = e.cold ?? 0;
  m.face.eyes.forEach((E, i) => {
    const s = i ? 1 : -1;
    E.e.scale.set(1 + 0.1 * (open - 1), Math.max(0.15, open), 1);
    E.lid.visible = cold > 0.01; E.lid.position.y = 0.03 - 0.05 * cold; E.lid.scale.set(1.05, 1, 1);
    E.pupil.scale.setScalar(e.pupil ?? 1); E.pupil.position.set((e.gx || 0) * 0.012, (e.gy || 0) * 0.01, 0.001);
    E.shine.position.set(0.005 + (e.gx || 0) * 0.012, 0.006 + (e.gy || 0) * 0.01, 0.002);
    const b = m.face.brows[i];
    b.position.y = 0.088 + 0.012 * worry - 0.006 * cold + 0.01 * (open - 1);
    b.rotation.z = Math.PI / 2 + s * (0.42 * worry - 0.08 * cold);
  });
  const mo = Math.min(1, (e.mouthBase ?? 0.1) + (mouth || 0) * (cold > 0.3 ? 0.45 : 1));
  m.face.mouth.scale.set(cold > 0.5 ? 1.3 : 1 - 0.2 * mo, 0.18 + mo * 0.95, 1);
  m.face.tears.forEach((tr, i) => { tr.visible = (e.tears || 0) > 0.05; tr.position.y = -0.005 - ((t * 0.035 + i * 0.4) % 0.06); });
  m.knife.visible = !!p.knife; m.glint.material.opacity = p.glint || 0;
}

// ------------------------------------------------------------------ OFFICER
export function makeOfficer() {
  const navy = '#1c2541', pants = '#1a2036', black = '#141519', skin = '#9a6e55', gold = '#d9b23a';
  const root = new THREE.Group(); scene.add(root);
  const torso = new THREE.Group(); root.add(torso);
  const tb = add(new THREE.Mesh(new THREE.CapsuleGeometry(0.19, 0.36, 8, 22), M(navy)), torso); tb.scale.set(1.25, 1, 0.8); tb.position.y = 0.3;
  for (const s of [-1, 1]) { const shd = sph(0.11, navy, s * 0.21, 0.56, 0, torso); shd.scale.set(1.1, 0.85, 1); box(0.12, 0.02, 0.06, '#232c4a', s * 0.21, 0.66, 0, torso); }
  box(0.05, 0.06, 0.012, gold, -0.1, 0.46, 0.15, torso);           // chest badge
  box(0.07, 0.016, 0.01, '#c9ccd2', 0.1, 0.46, 0.152, torso);      // name tag
  // duty belt with holster — and NO radio
  const belt = cyl(0.205, 0.205, 0.07, black, 0, 0.02, 0, torso); belt.scale.set(1.22, 1, 0.82);
  box(0.06, 0.05, 0.012, '#9aa0a8', 0, 0.02, 0.17, torso);
  const holster = new THREE.Group(); holster.position.set(0.25, -0.05, 0.02); torso.add(holster);
  box(0.07, 0.2, 0.09, black, 0, 0, 0, holster);
  const grip = box(0.04, 0.09, 0.05, '#2a2b30', 0, 0.12, -0.01, holster); grip.rotation.x = -0.25;
  const strap = box(0.075, 0.025, 0.1, black, 0, 0.09, 0, holster);
  box(0.05, 0.06, 0.05, black, -0.24, 0.01, 0.05, torso);          // cuff case (left)
  // head + cap
  const head = new THREE.Group(); head.position.set(0, 0.8, 0.0); torso.add(head);
  cyl(0.055, 0.06, 0.12, skin, 0, -0.09, 0, head);
  const hs = sph(0.118, skin, 0, 0.03, 0, head); hs.scale.set(0.98, 1.1, 1);
  sph(0.03, skin, -0.115, 0.02, 0, head, 12); sph(0.03, skin, 0.115, 0.02, 0, head, 12);
  cyl(0.122, 0.118, 0.07, navy, 0, 0.14, 0, head);
  const top = cyl(0.14, 0.125, 0.04, navy, 0, 0.19, -0.005, head); top.scale.set(1, 1, 1.05);
  cyl(0.124, 0.124, 0.022, black, 0, 0.115, 0, head);
  const brim = add(new THREE.Mesh(new THREE.CylinderGeometry(0.13, 0.13, 0.012, 24, 1, false, -Math.PI / 2, Math.PI), M(black)), head);
  brim.position.set(0, 0.105, 0.03); brim.rotation.x = 0.18; brim.scale.set(1, 1, 0.75);
  box(0.035, 0.035, 0.01, gold, 0, 0.15, 0.123, head);
  const face = {};
  face.eyes = [-1, 1].map(s => { const e = add(new THREE.Mesh(new THREE.CircleGeometry(0.014, 16), INK), head); e.position.set(s * 0.042, 0.035, 0.1185); e.scale.y = 0.45; return e; });
  face.brows = [-1, 1].map(s => { const b = capsule(0.008, 0.04, '#1c1410', head); b.position.set(s * 0.043, 0.062, 0.11); b.rotation.z = Math.PI / 2 - s * 0.25; return b; });
  sph(0.016, skin, 0, 0.0, 0.118, head, 12);
  face.mouth = add(new THREE.Mesh(new THREE.CircleGeometry(0.022, 20), INK), head); face.mouth.position.set(0, -0.05, 0.113);
  face.shadow = add(new THREE.Mesh(new THREE.SphereGeometry(0.121, 24, 12, 0, Math.PI * 2, 0, Math.PI * 0.42), noOutline(new THREE.MeshBasicMaterial({ color: '#000000', transparent: true, opacity: 0.35 }))), head);
  face.shadow.position.y = 0.035;
  const armL = makeLimb(0.06, 0.05, navy, navy), armR = makeLimb(0.06, 0.05, navy, navy);
  const legL = makeLimb(0.08, 0.065, pants, pants), legR = makeLimb(0.08, 0.065, pants, pants);
  const hands = [-1, 1].map(() => { const g = new THREE.Group(); scene.add(g); const p = sph(0.042, black, 0, 0, 0, g); p.scale.set(0.95, 0.7, 1.25); return g; });
  const boots = [-1, 1].map(() => { const b = box(0.12, 0.1, 0.28, black, 0, 0, 0); return b; });
  // flashlight (left hand)
  const fl = new THREE.Group(); hands[0].add(fl);
  const flb = cyl(0.022, 0.026, 0.2, '#202228', 0, 0, -0.04, fl); flb.rotation.x = Math.PI / 2;
  const lensM = add(new THREE.Mesh(new THREE.CircleGeometry(0.024, 20), noOutline(new THREE.MeshBasicMaterial({ color: '#ffffff' }))), fl); lensM.position.z = -0.141; lensM.rotation.y = Math.PI;
  const flGlow = glowSprite('#ffffff', 0.5, fl); flGlow.position.z = -0.16;
  const beam = add(new THREE.Mesh(new THREE.ConeGeometry(0.6, 4, 28, 1, true), glowMat('#f4f6ff', 0.07)), fl); beam.rotation.x = Math.PI / 2; beam.position.z = -2.14;
  // badge (right hand)
  const badge = new THREE.Group(); hands[1].add(badge);
  const bd = box(0.06, 0.075, 0.008, gold, 0, 0, -0.05, badge); bd.rotation.x = 0;
  const bglint = glowSprite('#fff6c8', 0.1, badge); bglint.position.set(0.015, 0.02, -0.05);
  return { root, torso, head, face, armL, armR, legL, legR, hands, boots, holster, strap, flashlight: fl, flGlow, beam, badge, bglint };
}
export function poseOfficer(o, p, t, mouth) {
  o.root.position.set(p.x, 0, p.z); o.root.rotation.y = p.yaw;
  o.torso.position.set(0, p.hipY ?? 1.02, 0); o.torso.rotation.set(p.lean || 0, p.twist || 0, 0, 'YXZ');
  o.head.rotation.set(p.headPitch || 0, p.headYaw || 0, 0, 'YXZ');
  o.root.updateMatrixWorld(true);
  const fwd = V(0, 0, 1).transformDirection(o.root.matrixWorld), right = V(1, 0, 0).transformDirection(o.root.matrixWorld);
  for (const [s, L, hand, H, dir] of [[-1, o.armL, p.handL, o.hands[0], p.handLdir], [1, o.armR, p.handR, o.hands[1], p.handRdir]]) {
    const S = o.torso.localToWorld(V(s * 0.23, 0.56, 0));
    const E = ik(S, hand, 0.33, 0.31, right.clone().multiplyScalar(s * 0.7).add(V(0, -1, 0)).add(fwd.clone().multiplyScalar(-0.4)));
    const wr = E.clone().add(hand.clone().sub(E).normalize().multiplyScalar(0.31));
    setLimb(L, S, E, wr);
    const fd = (dir || hand.clone().sub(E)).clone().normalize();
    H.position.copy(wr.clone().add(fd.clone().multiplyScalar(0.04)));
    H.quaternion.copy(basisQuat(fd, s > 0 && p.palmR ? p.palmR : V(0, -1, 0)));
  }
  for (const [s, L, foot, B] of [[-1, o.legL, p.footL, o.boots[0]], [1, o.legR, p.footR, o.boots[1]]]) {
    const S = o.torso.localToWorld(V(s * 0.1, -0.03, 0)), K = ik(S, foot, 0.5, 0.5, fwd.clone().add(V(0, 0.2, 0)));
    setLimb(L, S, K, foot.clone().add(V(0, 0.05, 0))); B.position.copy(foot).add(fwd.clone().multiplyScalar(0.05)); B.position.y = 0.05 + Math.max(0, foot.y); B.rotation.y = p.yaw;
  }
  o.face.mouth.scale.set(1 - 0.2 * (mouth || 0), 0.12 + (mouth || 0) * 0.9, 1);
  o.flashlight.visible = !!p.flash; o.flGlow.material.opacity = p.flashOn || 0; o.beam.material.opacity = 0.07 * (p.flashOn || 0);
  o.badge.visible = !!p.badge;
  o.strap.position.y = 0.09 + (p.unclip || 0) * 0.04; o.strap.rotation.x = (p.unclip || 0) * -0.9;
}
