// EPISODE 1 — "The Late-Night Gas Station Shift" — full 1:56 timeline (POV cashier).
// Shots follow the director's brief; camera language matches the approved preview
// (still → smooth move → hold/drift → snap), stereographic lens, toon + ink outlines.
import { THREE, scene, camera, setFocal, projectLens, renderFrame, lens, D2R, sineIO, sineIn, easeOut, seg, lerp } from './core.js';
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
const holdR = new THREE.Group(); phone.add(holdR);
const holdL = new THREE.Group(); phone.add(holdL);
let thumbL;
(function buildHoldHands() {
  const skinMat = handR.g.children[0].material;
  const mk = (r, x, y, z, sx, sy, sz, p) => { const m = new THREE.Mesh(new THREE.SphereGeometry(r, 28, 16), skinMat); m.position.set(x, y, z); m.scale.set(sx, sy, sz); p.add(m); return m; };
  mk(0.046, 0.03, -0.045, -0.032, 1.1, 1.3, 0.62, holdR);
  for (let i = 0; i < 4; i++) { const f = new THREE.Mesh(new THREE.CapsuleGeometry(0.0105, 0.012, 6, 12), skinMat); f.rotation.z = Math.PI / 2; f.position.set(0.046, 0.03 - i * 0.024, 0.004); holdR.add(f); }
  mk(0.038, -0.058, -0.088, -0.024, 1, 1.15, 0.6, holdL);
  thumbL = new THREE.Mesh(new THREE.CapsuleGeometry(0.012, 0.042, 6, 12), skinMat); thumbL.position.set(-0.02, -0.052, 0.012); thumbL.rotation.z = -0.75; holdL.add(thumbL);
})();

// ============================================================ helpers
const ease = { s: sineIO, in: sineIn, lin: t => t, snap: t => t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2, out: easeOut };
const wrapA = a => Math.atan2(Math.sin(a), Math.cos(a));
const yawTo = (from, to) => Math.atan2(to.x - from.x, to.z - from.z);
const mouthOf = (spk, t) => { const a = DLG.mouth[spk]; return a[Math.floor(t * 30)] || 0; };
const loc = (root, yaw, x, y, z) => root.clone().add(V(Math.cos(yaw) * x + Math.sin(yaw) * z, y, -Math.sin(yaw) * x + Math.cos(yaw) * z));
const inAny = (t, ranges) => ranges.some(([a, b]) => t > a && t < b);
const camLocal = (x, y, z) => V(x, y, z).applyMatrix4(camera.matrixWorld);
const camDir = (x, y, z) => V(x, y, z).transformDirection(camera.matrixWorld);

// ============================================================ CAMERA
const CAMK = [];
const K = (t0, t1, v, e = 's') => CAMK.push({ t0, t1, v, e });
const START = { yaw: 0, pitch: -3, x: 0, y: EYE, z: 0, f: 540 };
// ---- Scene 1 (approved preview)
K(0.3, 1.1, { yaw: 6, pitch: -2 });
K(2.5, 3.45, { yaw: -10.5 });
K(3.5, 5.85, { yaw: -11.9 }, 'in');
K(5.85, 6.38, { yaw: -9, pitch: -60, y: EYE - 0.15, z: -0.12 });
K(7.93, 8.65, { yaw: -3, pitch: -21, y: EYE - 0.04, z: -0.02 });
K(8.7, 10.5, { yaw: -1.8, pitch: -20.4 }, 'in');
K(10.5, 14.4, { yaw: -1.0, pitch: -19.6 }, 'lin');
// ---- Scene 2
K(14.85, 15.18, { yaw: -8.5, pitch: -1.5, y: EYE, z: 0 }, 'snap');
K(16.3, 18.0, { yaw: -4, pitch: -6 });
K(18.7, 19.05, { z: 0.05, pitch: -4 }, 'out'); K(20.9, 21.4, { z: 0 });
K(21.5, 22.3, { yaw: 13.5, pitch: -12.5, f: 690 });
K(22.3, 29.8, { yaw: 14.6, pitch: -12.2 }, 'lin');
K(29.85, 30.25, { yaw: -32, pitch: -36, x: 0.04, y: 1.12, z: 0.08, f: 540 }, 'snap');
K(31.0, 31.6, { yaw: 22, pitch: -24, x: 0, y: EYE, z: 0 });
K(32.7, 33.5, { yaw: 7, pitch: -8 });
K(33.5, 37.9, { yaw: 5.5, pitch: -7 }, 'lin');
// ---- Scene 3
K(38.15, 38.7, { yaw: -11, pitch: -1 });
K(38.7, 44.8, { yaw: -12.4, pitch: -0.6 }, 'lin');
K(44.9, 45.25, { yaw: -1.5, pitch: -9, z: -0.02, f: 600 }, 'snap');
K(46.45, 46.7, { pitch: -11.5 }, 'out');
K(46.7, 53.8, { yaw: -0.8, pitch: -10.8 }, 'lin');
K(53.9, 54.35, { yaw: -7.4, pitch: -1.5, z: 0, f: 540 }, 'snap');
K(54.5, 58.6, { f: 1350, pitch: -2.4, yaw: -6.7 });
K(59.35, 59.6, { f: 1260 }, 'out');
// ---- Scene 4
K(61.5, 62.3, { f: 1100, yaw: -8.7, pitch: 0.2 });
K(62.3, 70.8, { f: 1180, pitch: 0.5 }, 'lin');
K(70.85, 71.2, { yaw: -55, pitch: -55, x: 0.06, y: 1.56, z: -0.04, f: 540 }, 'snap');
K(71.2, 76.6, { yaw: -57, pitch: -53.5 }, 'lin');
K(76.65, 77.0, { yaw: -8.7, pitch: -3.6, x: 0, y: EYE, z: 0, f: 1250 }, 'snap');
K(77.0, 82.9, { f: 1320, pitch: -3.2 }, 'lin');
K(82.95, 83.3, { yaw: -61, pitch: -12, f: 600 }, 'snap');
K(84.0, 85.6, { pitch: -38, yaw: -63, f: 700 });
K(85.75, 86.45, { pitch: -9, yaw: -61, f: 640 });
K(86.45, 88.8, { pitch: -9.6, yaw: -61.6 }, 'lin');
// ---- Scene 5
K(88.95, 89.25, { yaw: -9, pitch: -60, y: EYE - 0.15, z: -0.12, f: 540 }, 'snap');
K(89.3, 96.4, { y: EYE - 0.19, z: -0.145 }, 'lin');
K(97.6, 102.8, { y: EYE - 0.25, z: -0.185, f: 610 }, 'lin');
K(102.9, 103.15, { yaw: -8.6, pitch: -1.2, y: EYE, z: 0, f: 1250 }, 'snap');
K(104.0, 105.2, { pitch: -3.6, yaw: -8.2, f: 1350 });
K(106.95, 107.2, { yaw: -61, pitch: -11, f: 600 }, 'snap');
K(109.4, 111.0, { pitch: -15, f: 560 });
// ---- Scene 6
K(111.9, 112.2, { yaw: -32, pitch: -34, x: 0.04, y: 1.12, z: 0.08, f: 600 }, 'snap');
const FREEZE = 112.45;
const SHAKES = [[62.9, 1.1], [63.3, 1.2], [63.7, 1.4], [77.55, 0.7], [78.0, 0.8], [78.45, 0.9], [30.55, 0.9], [14.0, 0.5], [15.85, 0.6], [98.0, 0.6]];
function camAt(t) {
  const c = { ...START };
  for (const k of CAMK) {
    if (t < k.t0) break;
    const prev = { ...c }, kk = ease[k.e](seg(t, k.t0, k.t1));
    for (const key in k.v) c[key] = lerp(prev[key], k.v[key], kk);
  }
  for (const [t0, a] of SHAKES) if (t > t0 && t < t0 + 0.45) { const d = t - t0; c.yaw += a * Math.exp(-d * 11) * Math.sin(d * 55); c.pitch += a * 0.7 * Math.exp(-d * 11) * Math.cos(d * 47); }
  if (t > FREEZE) c.f *= 1 + 0.012 * Math.pow(Math.max(0, Math.sin((t - FREEZE) * Math.PI * 2 * 1.15)), 8);
  return c;
}

// ============================================================ DOORS / CAR / LIGHTS
const doorAngle = t => {
  if (t < 14.0) return 0;
  if (t < 15.35) return 1.25 * easeOut(seg(t, 14.0, 14.22));
  const k = seg(t, 15.35, 15.85); let a = 1.25 * (1 - k * k);
  if (t > 15.85 && t < 16.1) a = 0.04 * Math.sin((t - 15.85) * 40) * Math.exp(-(t - 15.85) * 14);
  return a;
};
const carX = t => t < 38.0 ? 16 : 1.2 + 14.8 * Math.pow(1 - seg(t, 38.0, 41.3), 2.4);
function policeAt(t) {
  if (t < 38.0) return { on: 0, red: 0, blue: 0 };
  const on = easeOut(seg(t, 38.0, 38.5));
  const ph = (t * 2.15) % 1, half = ph < 0.5, q = (ph % 0.5) / 0.5;
  const pulse = (q < 0.18 ? 1 : q < 0.3 ? 0.15 : q < 0.48 ? 1 : 0.2);
  return { on, red: half ? pulse : 0.08, blue: half ? 0.08 : pulse };
}

// ============================================================ PHONE
const MSG1 = 'Quiet night? Don’t forget to lock the side door at 2:30.';
const REPLY = 'Dead quiet. Just me and the crickets.';
const ALERT = 'Suspect impersonating a police officer reported near Route 9. Do NOT open doors.';
const MSG2 = 'Just saw the news. Lock the doors. A girl in a grey hoodie just stabbed the night clerk down the road.';
const T = { buzz1: [6.62, 6.92], buzz2: [7.06, 7.36], grab: [7.62, 7.98], lift: [7.98, 8.6], type0: 8.75, rate: 15, sent: 11.4, down: [14.45, 14.95],
  alertBuzz: [[89.1, 89.4], [89.55, 89.85]], chime: 96.6 };
const PHONE_COUNTER = { pos: V(0.06, CT + 0.0045, -0.33), rot: new THREE.Euler(-Math.PI / 2, 0, 0.12) };
const PHONE_HELD = { pos: V(0.008, -0.012, -0.135), rot: new THREE.Euler(-0.05, 0, -0.04) };
const qCounter = new THREE.Quaternion().setFromEuler(PHONE_COUNTER.rot);
function wrap(g, text, maxW) { const ws = text.split(' '), out = []; let l = ''; for (const w of ws) { const tt = l ? l + ' ' + w : w; if (g.measureText(tt).width > maxW && l) { out.push(l); l = w; } else l = tt; } if (l) out.push(l); return out; }
function rrp(g, x, y, w, h, r) { g.beginPath(); g.moveTo(x + r, y); g.arcTo(x + w, y, x + w, y + h, r); g.arcTo(x + w, y + h, x, y + h, r); g.arcTo(x, y + h, x, y, r); g.arcTo(x, y, x + w, y, r); g.closePath(); }
const PF = (wt, px) => `${wt} ${px}px Rubik, sans-serif`;
let lastKey = '';
function drawPhone(state, typed, k, sent) {
  const key = state + typed.length + Math.round(k * 20) + sent; if (key === lastKey) return; lastKey = key;
  const g = phoneTex.userData.canvas.getContext('2d'), w = 400, h = 844;
  g.save(); rrp(g, 0, 0, w, h, 46); g.clip();
  const lockBg = (dim) => { const bg = g.createLinearGradient(0, 0, 0, h); bg.addColorStop(0, dim ? '#101a33' : '#20325e'); bg.addColorStop(1, '#0d1427'); g.fillStyle = bg; g.fillRect(0, 0, w, h);
    g.fillStyle = 'rgba(255,255,255,0.9)'; g.textAlign = 'center'; g.font = PF(500, 30); g.fillText('Friday', w / 2, 120); g.font = PF(700, 120); g.fillText(state.startsWith('alert') ? '2:21' : '2:14', w / 2, 240); g.textAlign = 'left'; };
  const notif = (y, name, av, msg, bgCol) => {
    g.font = PF(700, 27); const ls = wrap(g, msg, w - 100); const hh = 92 + ls.length * 35;
    g.fillStyle = bgCol; rrp(g, 22, y, w - 44, hh, 30); g.fill();
    g.fillStyle = '#f5d23a'; g.beginPath(); g.arc(66, y + 44, 22, 0, 7); g.fill();
    g.fillStyle = '#14161d'; g.font = PF(800, 26); g.textAlign = 'center'; g.fillText(av, 66, y + 53); g.textAlign = 'left';
    g.fillStyle = name.startsWith('LOCAL') ? '#ff4a3d' : '#fff'; g.font = PF(800, 26); g.fillText(name, 102, y + 54);
    g.fillStyle = '#f5d23a'; g.font = PF(700, 27); ls.forEach((l, i) => g.fillText(l, 46, y + 100 + i * 35));
    return hh;
  };
  if (state === 'off') {
    const bg = g.createLinearGradient(0, 0, w, h); bg.addColorStop(0, '#16181e'); bg.addColorStop(0.5, '#0d0e12'); bg.addColorStop(1, '#14161b');
    g.fillStyle = bg; g.fillRect(0, 0, w, h); g.fillStyle = 'rgba(255,255,255,0.06)'; g.beginPath(); g.moveTo(0, 0); g.lineTo(w * 0.6, 0); g.lineTo(0, h * 0.5); g.fill();
  } else if (state === 'lock' || state === 'lockdim') {
    lockBg(state === 'lockdim');
    if (state === 'lock') { g.globalAlpha = k; notif(300, 'Manager', 'M', MSG1, 'rgba(28,32,44,0.92)'); g.globalAlpha = 1; }
  } else if (state === 'alert' || state === 'alert2') {
    lockBg(false);
    let y = 290;
    if (state === 'alert2') y += notif(y, 'Manager', 'M', MSG2, 'rgba(28,32,44,0.95)') + 14;
    g.globalAlpha = state === 'alert' ? k : 1;
    notif(y, 'LOCAL ALERT', '!', ALERT, 'rgba(70,14,14,0.96)');
    g.globalAlpha = 1;
  } else {
    g.fillStyle = '#0f1117'; g.fillRect(0, 0, w, h); g.fillStyle = '#181b24'; g.fillRect(0, 0, w, 130);
    g.fillStyle = '#fff'; g.font = PF(600, 22); g.fillText('2:14', 34, 44);
    g.fillStyle = '#f5d23a'; g.beginPath(); g.arc(70, 92, 24, 0, 7); g.fill();
    g.fillStyle = '#14161d'; g.font = PF(800, 26); g.textAlign = 'center'; g.fillText('M', 70, 101); g.textAlign = 'left';
    g.fillStyle = '#fff'; g.font = PF(700, 28); g.fillText('Manager', 108, 90); g.fillStyle = '#7fe0a0'; g.font = PF(500, 18); g.fillText('Active now', 108, 114);
    g.font = PF(700, 27); const ls = wrap(g, MSG1, 250);
    g.fillStyle = '#262a35'; rrp(g, 22, 170, 286, 36 + ls.length * 34, 22); g.fill();
    g.fillStyle = '#f5d23a'; ls.forEach((l, i) => g.fillText(l, 40, 210 + i * 34));
    if (sent) { g.font = PF(700, 25); const rs = wrap(g, REPLY, 230); const by = 250 + ls.length * 34; g.fillStyle = '#3d7bff'; rrp(g, w - 22 - 262, by, 262, 30 + rs.length * 32, 22); g.fill(); g.fillStyle = '#fff'; rs.forEach((l, i) => g.fillText(l, w - 262, by + 40 + i * 32)); }
    g.fillStyle = '#1d212b'; rrp(g, 18, 470, w - 36, 64, 32); g.fill();
    g.font = PF(600, 24); const shown = sent ? '' : typed; const tl = wrap(g, shown || ' ', w - 110);
    g.fillStyle = shown ? '#fff' : '#6b7385'; g.fillText(shown ? tl[tl.length - 1] : 'Message', 40, 510);
    if (shown) { const cw = g.measureText(tl[tl.length - 1]).width; g.fillStyle = '#4c8dff'; g.fillRect(42 + cw, 488, 3, 30); }
    g.fillStyle = '#4c8dff'; g.beginPath(); g.arc(w - 52, 502, 22, 0, 7); g.fill();
    g.fillStyle = '#1a1d25'; g.fillRect(0, 560, w, h - 560);
    const rows = ['qwertyuiop', 'asdfghjkl', 'zxcvbnm']; g.font = PF(500, 22); g.textAlign = 'center';
    rows.forEach((r, ri) => { const kw = 36, off = (w - r.length * kw) / 2; for (let i = 0; i < r.length; i++) { g.fillStyle = '#353a47'; rrp(g, off + i * kw + 3, 584 + ri * 62, kw - 6, 50, 8); g.fill(); g.fillStyle = '#e6e9f0'; g.fillText(r[i], off + i * kw + kw / 2, 617 + ri * 62); } });
    g.fillStyle = '#353a47'; rrp(g, 90, 772, 220, 48, 8); g.fill(); g.textAlign = 'left';
  }
  g.restore(); phoneTex.needsUpdate = true;
}

// ============================================================ MAYA performance
const DOOR_SPOT = V(1.12, 0, -6.2), RUN_TO = V(0.36, 0, -1.78), RACK = V(-0.62, 0, -2.6), COUNTER = V(0.04, 0, -1.02);
const HIDE = V(0.5, 0, -0.33), BESIDE = V(0.48, 0, -0.27);
function gait(t, root, yaw, speed, phase0 = 0) {
  const ph = phase0 + t * (speed > 1.5 ? 2.7 : 1.8) * Math.PI * 2;
  const fwd = V(Math.sin(yaw), 0, Math.cos(yaw)), rt = V(Math.cos(yaw), 0, -Math.sin(yaw));
  const stride = Math.min(0.42, 0.18 * speed);
  const off = s => ph + (s > 0 ? Math.PI : 0);
  const foot = s => root.clone().add(rt.clone().multiplyScalar(s * 0.1)).add(fwd.clone().multiplyScalar(stride * Math.sin(off(s)))).add(V(0, Math.max(0, Math.cos(off(s))) * 0.13 * Math.min(1, speed), 0));
  const hand = s => root.clone().add(rt.clone().multiplyScalar(s * 0.26)).add(fwd.clone().multiplyScalar(-stride * 0.8 * Math.sin(off(s)) + 0.05)).add(V(0, 0.95 + 0.06 * Math.abs(Math.sin(ph)), 0));
  return { footL: foot(-1), footR: foot(1), handL: hand(-1), handR: hand(1), bob: 0.03 * Math.abs(Math.sin(ph)) };
}
function lookAtCam(from, rootYaw, twist, lean, headH) {
  const cam = camera.position, dir = V(cam.x - from.x, cam.y - headH, cam.z - from.z);
  const hy = Math.max(-1.35, Math.min(1.35, wrapA(Math.atan2(dir.x, dir.z) - rootYaw - twist)));
  const hp = -Math.atan2(dir.y, Math.hypot(dir.x, dir.z)) - lean;
  return { headYaw: hy, headPitch: Math.max(-0.7, Math.min(0.7, hp)) };
}
function mayaAt(t, povForearm) {
  const mouth = mouthOf('maya', t);
  const terror = { eyes: 1.32, worry: 1, pupil: 0.75, mouthBase: 0.18 };
  let p;
  if (t < 14.0) { maya.root.visible = false; maya.hands.forEach(h => h.visible = false); setLimbsVis(maya, false); return; }
  maya.root.visible = true; maya.hands.forEach(h => h.visible = true); setLimbsVis(maya, true);
  if (t < 15.35) {
    const root = DOOR_SPOT.clone().add(V(0, 0, (1 - easeOut(seg(t, 14.0, 14.5))) * -0.6)), yaw = Math.PI;
    p = { x: root.x, z: root.z, yaw, hipY: 0.95, lean: 0.25, handL: loc(root, yaw, -0.25, 1.05, 0.35), handR: loc(root, yaw, 0.25, 1.05, 0.35), footL: loc(root, yaw, -0.12, 0, -0.05), footR: loc(root, yaw, 0.14, 0, 0.15), expr: terror };
  } else if (t < 15.9) {
    const root = DOOR_SPOT.clone(), yaw = Math.PI; doors.L.leaf.updateMatrixWorld();
    const hnd = doors.L.leaf.localToWorld(V(0.52, 1.1, 0.08));
    p = { x: root.x, z: root.z, yaw, hipY: 0.94, lean: 0.3, handL: hnd.clone().add(V(-0.05, 0.05, 0)), handR: hnd.clone(), footL: loc(root, yaw, -0.12, 0, -0.1), footR: loc(root, yaw, 0.14, 0, 0.12), expr: terror };
  } else if (t < 18.3) {
    const k = seg(t, 16.3, 18.2), root = DOOR_SPOT.clone().lerp(RUN_TO, k);
    const yt = yawTo(DOOR_SPOT, RUN_TO), yaw = lerp(Math.PI, yt + (yt < 0 ? Math.PI * 2 : 0), easeOut(seg(t, 15.9, 16.3)));
    const sp = t > 16.3 && t < 18.2 ? 2.4 : 0.2;
    const gt = gait(t, root, yaw, sp);
    p = { x: root.x, z: root.z, yaw, hipY: 0.93 - gt.bob, lean: sp > 1 ? 0.28 : 0.15, ...gt, expr: terror };
    Object.assign(p, lookAtCam(root, yaw, 0, p.lean, 1.6));
  } else if (t < 21.6) {
    const root = RUN_TO.clone(), yaw = yawTo(RUN_TO, V(0, 0, 0)), heave = Math.sin(t * 9) * 0.03;
    p = { x: root.x, z: root.z, yaw, hipY: 0.95 + heave * 0.2, lean: 0.12 + heave, handL: loc(root, yaw, -0.12, 1.22, 0.22), handR: loc(root, yaw, 0.1, 1.25, 0.24), footL: loc(root, yaw, -0.11, 0, 0), footR: loc(root, yaw, 0.12, 0, 0.05), expr: terror };
    Object.assign(p, lookAtCam(root, yaw, 0, p.lean, 1.62));
  } else if (t < 41.5) {
    const k = seg(t, 21.6, 22.5), root = RUN_TO.clone().lerp(RACK, sineIO(k));
    const yawRack = 2.2, yaw = lerp(yawTo(RUN_TO, V(0, 0, 0)), yawRack, sineIO(seg(t, 21.6, 22.3)));
    const crouch = sineIO(seg(t, 22.2, 22.75));
    const peek = t > 26.8 ? sineIO(seg(t, 26.8, 27.6)) * (t < 38.2 ? 1 : 1 - seg(t, 38.2, 38.6)) : 0;
    const hipY = lerp(0.95, 0.5, crouch) + 0.1 * peek - (t > 38.2 ? 0.06 * seg(t, 38.2, 38.5) : 0);
    if (k < 1) { const gt = gait(t, root, yaw, 1.6); p = { x: root.x, z: root.z, yaw, hipY: hipY - gt.bob, lean: 0.2 + 0.25 * crouch, ...gt, expr: terror }; }
    else p = { x: root.x, z: root.z, yaw, hipY, lean: 0.45 - 0.15 * peek, twist: 0.35,
      handL: loc(root, yaw, -0.3, hipY + 0.42, 0.25), handR: loc(root, yaw, 0.12, hipY + 0.25, 0.32), footL: loc(root, yaw, -0.14, 0, 0.18), footR: loc(root, yaw, 0.16, 0, 0.08), expr: terror };
    const talking = t > 22.3 && t < 26.8;
    const la = lookAtCam(root, yaw, p.twist || 0, p.lean, p.hipY + 0.75);
    const w = talking ? sineIO(seg(t, 22.3, 22.7)) * (1 - sineIO(seg(t, 26.4, 26.8))) : 0;
    p.headYaw = lerp(-0.25, la.headYaw, w); p.headPitch = lerp(-0.1 - p.lean, la.headPitch, w);
    p.expr = { ...terror, gx: w > 0.5 ? 0 : -0.6 };
  } else if (t < 54.2) {
    const k = seg(t, 41.9, 43.3), root = RACK.clone().lerp(COUNTER, sineIO(k));
    const yaw = t < 43.3 ? yawTo(RACK, COUNTER) : lerp(yawTo(RACK, COUNTER), 0, sineIO(seg(t, 43.3, 43.8)));
    const rise = sineIO(seg(t, 41.5, 41.9));
    if (t < 43.4) { const gt = gait(t, root, yaw, k > 0 && k < 1 ? 2.0 : 0.3); p = { x: root.x, z: root.z, yaw, hipY: lerp(0.5, 0.94, rise) - gt.bob, lean: 0.25, ...gt, expr: terror }; }
    else {
      const lunge = sineIO(seg(t, 45.35, 45.9)) * (1 - sineIO(seg(t, 53.9, 54.2)));
      const grab = sineIO(seg(t, 46.0, 46.5)) * (1 - sineIO(seg(t, 53.8, 54.2)));
      const lean = 0.08 + 0.55 * lunge;
      const handR = loc(root, yaw, 0.12, 1.08, 0.3).lerp(povForearm, grab);
      p = { x: root.x, z: root.z, yaw, hipY: 0.94 - 0.04 * lunge, lean, handL: loc(root, yaw, -0.2, CT + 0.03, 0.42 + 0.1 * lunge), handR, handRdir: grab > 0.5 ? V(0.2, -0.6, 1) : null,
        footL: loc(root, yaw, -0.11, 0, -0.08), footR: loc(root, yaw, 0.13, 0, -0.02), expr: { ...terror, eyes: 1.38, pupil: 0.6 } };
      Object.assign(p, lookAtCam(root, yaw, 0, lean, 0.94 + 0.7 * Math.cos(lean)));
      if (t < 45.3) { p.headYaw = -0.15; p.headPitch = -0.05; p.expr.gx = 0.5; }
    }
  } else if (t < 82.9) {
    const path = [[54.2, COUNTER], [55.4, V(1.28, 0, -1.02)], [56.4, V(1.3, 0, -0.1)], [57.5, HIDE]];
    let root = COUNTER.clone(), yaw = 0, sp = 0;
    for (let i = 1; i < path.length; i++) if (t >= path[i - 1][0]) {
      const kk = seg(t, path[i - 1][0], path[i][0]); root = path[i - 1][1].clone().lerp(path[i][1], kk);
      if (kk < 1) { yaw = yawTo(path[i - 1][1], path[i][1]); sp = 1.6; }
    }
    if (t > 57.5) { yaw = yawTo(HIDE, V(0.0, 0, 0.15)); sp = 0; }
    const crouch = sineIO(seg(t, 57.3, 58.0));
    if (sp > 0) { const gt = gait(t, root, yaw, sp); p = { x: root.x, z: root.z, yaw, hipY: 0.94 - gt.bob - 0.2 * seg(t, 56.4, 57.5), lean: 0.3, ...gt, expr: terror }; }
    else {
      const shake = Math.sin(t * 31) * 0.006 + Math.sin(t * 23) * 0.004, hipY = lerp(0.94, 0.42, crouch);
      const point = sineIO(seg(t, 72.4, 72.9)) * (1 - sineIO(seg(t, 75.8, 76.3)));
      const handR = loc(root, yaw, 0.14, hipY + 0.32, 0.32).lerp(loc(root, yaw, 0.05, 1.05, -0.35), point);
      p = { x: root.x + shake, z: root.z, yaw, hipY, lean: 0.38 - 0.25 * point, handL: loc(root, yaw, -0.14, hipY + 0.28, 0.33), handR, handRdir: point > 0.5 ? V(-0.3, 0.5, -1) : null,
        footL: loc(root, yaw, -0.15, 0, 0.22), footR: loc(root, yaw, 0.15, 0, 0.2), expr: { ...terror, eyes: 1.35, pupil: 0.65 } };
      Object.assign(p, lookAtCam(root, yaw, 0, p.lean, hipY + 0.72));
    }
  } else if (t < 107) {
    const rise = sineIO(seg(t, 82.9, 83.7)), root = HIDE.clone().lerp(BESIDE, rise), yaw = yawTo(BESIDE, V(0.0, 0, 0.1));
    const hipY = lerp(0.42, 0.94, rise);
    maya.torso.updateMatrixWorld();
    const pocket = maya.torso.localToWorld(V(0.06, 0.12, 0.17));
    const tears = seg(t, 85.6, 86.2);
    p = { x: root.x, z: root.z, yaw, hipY, lean: lerp(0.38, 0.06, rise), handL: loc(root, yaw, -0.2, hipY + 0.05, 0.12), handR: pocket, handRdir: V(-0.3, -0.6, -0.4),
      footL: loc(root, yaw, -0.11, 0, 0), footR: loc(root, yaw, 0.12, 0, 0.04), expr: { eyes: 1.25, worry: 1, pupil: 0.8, mouthBase: 0.12, tears } };
    Object.assign(p, lookAtCam(root, yaw, 0, p.lean, hipY + 0.72));
  } else {
    const root = BESIDE.clone(), yaw = yawTo(BESIDE, V(0.0, 0, 0.1)), hipY = 0.94;
    maya.torso.updateMatrixWorld();
    const pocket = maya.torso.localToWorld(V(0.06, 0.12, 0.17)), out = maya.torso.localToWorld(V(0.1, 0.36, 0.34));
    const pull = sineIO(seg(t, 109.0, 111.2));
    p = { x: root.x, z: root.z, yaw, hipY, lean: 0.04, handL: loc(root, yaw, -0.2, hipY + 0.05, 0.1), handR: pocket.clone().lerp(out, pull), handRdir: V(-0.15, 0.5 + 0.5 * pull, -0.6 + 0.9 * pull),
      footL: loc(root, yaw, -0.11, 0, 0), footR: loc(root, yaw, 0.12, 0, 0.04), knife: pull > 0.15, glint: t > 110.9 && t < 111.6 ? Math.sin(seg(t, 110.9, 111.6) * Math.PI) : 0,
      expr: { eyes: 0.95, worry: 0, cold: 0.55, pupil: 1.05, mouthBase: 0.02, tears: 0 } };
    Object.assign(p, lookAtCam(root, yaw, 0, p.lean, hipY + 0.72));
  }
  poseMaya(maya, p, t, Math.min(1, mouth * 1.1));
  maya.pocket.scale.set(1, t > 82.9 ? 1.08 : 1, t > 82.9 && t < 109 ? 0.6 : 0.45);
}
function setLimbsVis(ch, v) { for (const L of [ch.armL, ch.armR, ch.legL, ch.legR]) { L.a.visible = L.j.visible = L.b.visible = v; } (ch.feet || ch.boots).forEach(f => f.visible = v); }

// ============================================================ OFFICER performance
function copAt(t) {
  const mouth = mouthOf('cop', t);
  if (t < 56.9) { cop.root.visible = false; cop.hands.forEach(h => h.visible = false); setLimbsVis(cop, false); return null; }
  cop.root.visible = true; cop.hands.forEach(h => h.visible = true); setLimbsVis(cop, true);
  const cx = carX(t), carDoorStand = V(cx + 0.15, 0, -9.2), DOOR = V(1.12, 0, -7.42);
  let root, yaw = 0, sp = 0;
  if (t < 58.2) { root = V(cx - 0.05, 0, -10.0).lerp(carDoorStand, sineIO(seg(t, 56.9, 58.2))); sp = 1.0; }
  else if (t < 61.5) root = carDoorStand;
  else if (t < 62.75) { root = carDoorStand.clone().lerp(DOOR, seg(t, 61.5, 62.75)); yaw = yawTo(carDoorStand, DOOR); sp = 1.7; }
  else root = DOOR;
  if (sp === 0) yaw = yawTo(root, camera.position) * 0.6;
  const p = { x: root.x, z: root.z, yaw, hipY: 1.02, flash: true, flashOn: 0, badge: false };
  if (sp > 0) { const gt = gait(t, root, yaw, sp, 0.4); p.footL = gt.footL; p.footR = gt.footR; p.hipY -= gt.bob * 0.6; }
  else { p.footL = loc(root, yaw, -0.12, 0, 0); p.footR = loc(root, yaw, 0.13, 0, 0.04); }
  const raise = sineIO(seg(t, 59.0, 59.4)) * (1 - sineIO(seg(t, 61.4, 61.8)));
  const aim = camera.position.clone().sub(loc(root, yaw, -0.25, 1.45, 0.3)).normalize();
  const lowHand = loc(root, yaw, -0.3, 0.95, 0.15), upHand = loc(root, yaw, -0.22, 1.45, 0.42), shoulderHand = loc(root, yaw, -0.28, 1.2, 0.3);
  p.handL = t < 62.75 ? lowHand.clone().lerp(upHand, raise) : lowHand.clone().lerp(shoulderHand, sineIO(seg(t, 62.8, 63.4)));
  p.handLdir = raise > 0.3 ? aim : t > 61.6 && t < 102.9 ? V(0.15, -0.85, 0.5) : t >= 102.9 ? aim.clone().lerp(V(0, -0.6, 1), 0.3) : V(0.1, -0.7, 1);
  p.flashOn = t > 58.6 ? 1 : 0;
  const glassZ = -7.1;
  let handR = loc(root, yaw, 0.3, 0.95, 0.12), palmR = null, dirR = null;
  const knock = [62.9, 63.3, 63.7].reduce((acc, k0) => acc + Math.exp(-Math.pow((t - k0) / 0.07, 2)), 0);
  if (t > 62.75 && t < 64.1) { handR = V(1.3, 1.5, glassZ - 0.12 + 0.1 * Math.min(1, knock)); dirR = V(0, 0.3, 1); }
  else if (t >= 64.1 && t < 70.9) { handR = V(1.3, 1.5, glassZ - 0.02); palmR = V(0, 0, 1); dirR = V(0, 1, 0.05); p.badge = true; }
  else if (t >= 77.3 && t < 79.2) { const y = Math.sin((t - 77.3) * 13) * 0.04; handR = V(1.36, 1.1, -7.08 + y); dirR = V(0, 0, 1); }
  else if (t >= 103.5) { const k = sineIO(seg(t, 103.5, 104.3)); cop.torso.updateMatrixWorld(); const hol = cop.holster.localToWorld(V(0, 0.15, 0.02)); handR = handR.clone().lerp(hol, k); dirR = V(0, -1, 0.2); p.unclip = sineIO(seg(t, 104.4, 105.0)); }
  p.handR = handR; p.handRdir = dirR; p.palmR = palmR;
  const dir = camera.position.clone().sub(V(root.x, 1.75, root.z));
  p.headYaw = Math.max(-1, Math.min(1, wrapA(Math.atan2(dir.x, dir.z) - yaw))); p.headPitch = -Math.atan2(dir.y, Math.hypot(dir.x, dir.z)) * 0.8;
  if (t > 79.2 && t < 83) p.lean = 0.08;
  poseOfficer(cop, p, t, Math.min(1, mouth * 1.2));
  cop.face.shadow.material.opacity = 0.35 + 0.35 * seg(t, 102.9, 104.0);
  return { raise };
}

// ============================================================ POV hands
const REST_R = V(0.2, CT + 0.035, -0.3), REST_L = V(-0.26, CT + 0.035, -0.3);
const WIPE_C = V(-0.2, CT + 0.003, -0.42);
function wipeAt(t) {
  const amp = 1 - sineIO(seg(t, 5.2, 5.75)), ph = t * 2 * Math.PI / 1.55 + 0.4 * Math.sin(t * 1.3);
  return V(WIPE_C.x + amp * 0.085 * Math.cos(ph), WIPE_C.y, WIPE_C.z + amp * 0.055 * Math.sin(ph));
}
function handsAt(t, bf) {
  const R = { pos: REST_R.clone(), fd: V(-0.15, -0.25, -1), pn: V(0, -1, 0), pose: 'rest', vis: true };
  if (t < 7.98) {
    const wp = wipeAt(Math.min(t, 5.8)); phone.updateMatrixWorld();
    const target = V(0.06, -0.045, -0.02).applyMatrix4(phone.matrixWorld); target.y = Math.max(target.y, CT + 0.03);
    const gk = sineIO(seg(t, ...T.grab));
    R.pos = wp.clone().add(V(0, 0.03, 0)).lerp(target, gk); R.fd = V(-0.45 + 0.4 * gk, -0.15, -1); R.pose = gk > 0.5 ? 'grip' : 'wipe';
    rag.position.copy(wipeAt(Math.min(t, 5.8))); rag.rotation.y = 0.2 * Math.sin(Math.min(t, 5.8) * 2);
  } else if (t < T.down[1]) R.vis = false;
  if (t > 18.6 && t < 21.4) {
    const up = sineIO(seg(t, 18.6, 18.95)) * (1 - sineIO(seg(t, 20.9, 21.4))), tr = V(Math.sin(t * 37) * 0.003, Math.sin(t * 29) * 0.003, 0);
    R.pos = REST_R.clone().lerp(camLocal(0.15, -0.09, -0.34).add(tr), up); R.fd = V(-0.15, -0.25, -1).lerp(camDir(0.1, 1, -0.25), up); R.pn = V(0, -1, 0).lerp(camDir(0, 0, -1), up).normalize(); R.pose = up > 0.4 ? 'open' : 'rest';
  }
  if (t > 30.2 && t < 31.5) {
    const cap = lockBtn.cap.getWorldPosition(V(0, 0, 0));
    const reach = sineIO(seg(t, 30.2, 30.5)) * (1 - sineIO(seg(t, 30.9, 31.4)));
    const hit = t > 30.5 ? Math.max(0, 1 - (t - 30.5) * 6) : 0;
    R.pos = REST_R.clone().lerp(cap.clone().add(V(0, 0, 0.085 - 0.04 * hit - 0.03 * reach)), reach); R.fd = V(-0.15, -0.25, -1).lerp(V(0.05, 1, -0.15), reach); R.pn = V(0, -1, 0).lerp(V(0, 0, -1), reach).normalize(); R.pose = 'flat';
  }
  if (t > 39.5 && t < 42.3) {
    const k = sineIO(seg(t, 39.5, 39.9)) * (1 - sineIO(seg(t, 41.8, 42.3)));
    const pp = camLocal(0.13, -0.12, -0.42), dir = V(1.2, 1.0, -10).sub(pp).normalize();
    R.pos = REST_R.clone().lerp(pp, k); R.fd = V(-0.15, -0.25, -1).lerp(dir, k); R.pn = V(0, -1, 0).lerp(V(0, -0.3, 0.2).normalize(), k).normalize(); R.pose = k > 0.4 ? 'point' : 'rest';
  }
  if (t > 44.9 && t < 54.3) { R.pos = V(0.12, CT + 0.04, -0.47); R.fd = V(-0.1, -0.1, -1); R.pose = 'rest'; }
  if (t > 111.9) {
    const cap = lockBtn.cap.getWorldPosition(V(0, 0, 0)), tt = Math.min(t, FREEZE);
    const tr = V(Math.sin(tt * 53) * 0.004 + Math.sin(tt * 31) * 0.003, Math.sin(tt * 47) * 0.004, 0);
    const k = sineIO(seg(t, 111.95, 112.35));
    R.pos = REST_R.clone().lerp(cap.clone().add(V(0.0, 0.115, 0.06)).add(tr), k); R.fd = V(-0.15, -0.25, -1).lerp(V(0.0, 0.75, -0.6), k); R.pn = V(0, -1, 0).lerp(V(0, -0.4, -1).normalize(), k).normalize(); R.pose = 'hover';
  }
  const L = { pos: REST_L.clone(), fd: V(0.15, -0.25, -1), pn: V(0, -1, 0), pose: 'rest', vis: !(t > T.lift[0] && t < T.down[1]) };
  if (t < T.lift[0]) L.vis = false;
  if (t > 18.6 && t < 21.4) {
    const up = sineIO(seg(t, 18.65, 19.0)) * (1 - sineIO(seg(t, 20.9, 21.4))), tr = V(Math.sin(t * 33) * 0.003, Math.sin(t * 41) * 0.003, 0);
    L.pos = REST_L.clone().lerp(camLocal(-0.15, -0.1, -0.34).add(tr), up); L.fd = V(0.15, -0.25, -1).lerp(camDir(-0.1, 1, -0.25), up); L.pn = V(0, -1, 0).lerp(camDir(0, 0, -1), up).normalize(); L.pose = up > 0.4 ? 'open' : 'rest';
  }
  landline.g.updateMatrixWorld();
  const hsRest = landline.g.localToWorld(landline.rest.clone());
  landline.handset.position.copy(landline.rest); landline.handset.rotation.set(0, 0, 0);
  if (t > 32.0 && t < 44.95) {
    const reach = sineIO(seg(t, 32.0, 32.6)), lift = sineIO(seg(t, 32.6, 33.3));
    const hp = REST_L.clone().lerp(hsRest.clone().add(V(0, 0.03, 0)), reach).lerp(camLocal(-0.16, -0.02, 0.05), lift);
    L.pos = hp; L.pose = 'grip'; L.fd = V(0.3, -0.4, -1).lerp(camDir(0.2, 1, 0.2), lift); L.pn = V(0, -1, 0).lerp(camDir(1, 0, 0), lift).normalize();
    if (lift > 0) { landline.handset.position.copy(landline.g.worldToLocal(hp.clone().add(V(0, -0.02, 0)))); landline.handset.rotation.set(lift * 1.2, 0, lift * 0.8); }
  }
  return { R, L };
}
function applyHand(h, s) {
  h.g.visible = s.vis;
  if (s.vis) { h.g.position.copy(s.pos); h.g.quaternion.copy(basisQuat(s.fd, s.pn)); poseHand(h, s.pose); h.g.updateMatrixWorld(); }
}

// ============================================================ HUD
const titleEl = document.getElementById('title'), cardsEl = document.getElementById('cards'), subEl = document.getElementById('subtxt'), ctaEl = document.getElementById('cta');
function card(av, name, time, msg, col, avCol = '#f5d23a') {
  return `<div class="card"><div class="row"><div class="av" style="background:${avCol}">${av}</div><div class="name">${name}</div><div class="time">${time}</div></div><div class="msg" style="color:${col}">${msg}</div></div>`;
}
const CARDS = [
  { id: 'm1', t0: 6.64, t1: 8.62, html: () => card('M', 'Manager', '2:14', MSG1, '#f5d23a') },
  { id: 'y1', t0: 8.62, t1: 14.45, html: (t) => { const typed = REPLY.slice(0, Math.max(0, Math.floor((t - T.type0) * T.rate))); return card('Y', 'You', t < T.sent ? '<span style="font-size:19px">typing…</span>' : 'sent', typed || ' ', '#ffffff', '#ffffff'); } },
  { id: 'al', t0: 89.15, t1: 103.0, html: () => `<div class="card alert"><div class="hdr"><div class="tri"></div>LOCAL ALERT</div><div class="msg">${ALERT}</div></div>` },
  { id: 'm2', t0: 96.65, t1: 103.0, html: () => card('M', 'Manager', '2:21', MSG2, '#f5d23a') },
];
const cardEls = {};
function hudAt(t) {
  const a = easeOut(seg(t, -0.05, 0.4)), out = seg(t, 5.85, 6.2);
  titleEl.style.opacity = (0.25 + 0.75 * a) * (1 - out); titleEl.style.transform = `translateX(${-12 * (1 - a)}px)`;
  const live = CARDS.filter(c => t > c.t0 - 0.01 && t < c.t1 + 0.3);
  let y = 0;
  for (const c of [...live].reverse()) {
    if (!cardEls[c.id]) { const d = document.createElement('div'); cardsEl.appendChild(d); cardEls[c.id] = d; }
    const el = cardEls[c.id]; el.innerHTML = c.html(t);
    const ci = easeOut(seg(t, c.t0, c.t0 + 0.22)), co = 1 - seg(t, c.t1, c.t1 + 0.3);
    const inner = el.firstChild; inner.style.opacity = ci * co; inner.style.top = `${y}px`;
    inner.style.transform = `translateY(${-24 * (1 - ci)}px) scale(${0.96 + 0.04 * ci})`;
    y += (inner.offsetHeight + 14) * ci * co;
  }
  for (const id in cardEls) if (!live.find(c => c.id === id)) { cardEls[id].remove(); delete cardEls[id]; }
  let sub = null;
  for (const l of DLG.lines) for (const c of l.chunks) if (t >= c.t0 && t < c.t1) sub = { c, spk: l.spk };
  subEl.textContent = sub ? sub.c.text : ''; subEl.className = sub ? sub.spk : '';
  if (sub) subEl.style.transform = `translateX(-50%) scale(${0.91 + 0.09 * easeOut(seg(t, sub.c.t0, sub.c.t0 + 0.1))})`;
  document.getElementById('sub').style.top = t > 112.6 ? '1150px' : '839px';
  ctaEl.style.display = t > 112.75 ? 'block' : 'none';
  if (t > 112.75) {
    const k = easeOut(seg(t, 112.75, 113.05));
    ctaEl.querySelector('.q').style.transform = `scale(${0.85 + 0.15 * k})`; ctaEl.style.opacity = k;
    ctaEl.querySelectorAll('.btn').forEach((b, i) => { const kb = easeOut(seg(t, 112.95 + i * 0.15, 113.25 + i * 0.15)); b.style.transform = `scale(${0.8 + 0.2 * kb})`; b.style.opacity = kb; });
  }
}

// ============================================================ render
window.setHud = on => { document.getElementById('hud').style.display = on ? 'block' : 'none'; };
window.renderAt = (tReal) => {
  const t = Math.min(tReal, FREEZE);
  drawRain(t);
  const c = camAt(tReal);
  camera.position.set(c.x, c.y, c.z); camera.rotation.set(c.pitch * D2R, c.yaw * D2R, 0); camera.updateMatrixWorld(); setFocal(c.f);
  const bf = new THREE.Matrix4().makeRotationY(c.yaw * D2R); bf.setPosition(c.x, c.y, c.z);
  body.visible = c.y > 1.35; body.position.set(c.x, 0, c.z * 0.5); body.rotation.y = c.yaw * D2R * 0.35;
  // doors, lock, car, lights
  setDoor('L', t > 77.3 && t < 79.2 ? 0.012 * Math.sin((t - 77.3) * 26) : doorAngle(t));
  setLocked(t > 30.56);
  lockBtn.cap.position.z = 0.01 - (t > 30.5 && t < 30.75 ? 0.008 : 0);
  car.g.position.set(carX(t), 0, -10.3); car.g.visible = t > 37.9;
  car.doorPivot.rotation.y = -1.1 * sineIO(seg(t, 56.4, 57.0));
  const pol = policeAt(t);
  car.red.material.color.set(pol.red > 0.5 ? '#ff3a3a' : '#4a0c0c'); car.blue.material.color.set(pol.blue > 0.5 ? '#3a6bff' : '#0b1440');
  car.redGlow.material.opacity = pol.on * pol.red; car.blueGlow.material.opacity = pol.on * pol.blue;
  car.redPool.position.set(carX(t) + 0.2, 0.015, -9.0); car.bluePool.position.set(carX(t) + 0.2, 0.016, -9.0);
  car.redPool.material.opacity = 0.22 * pol.on * pol.red; car.bluePool.material.opacity = 0.22 * pol.on * pol.blue;
  const headOn = t > 37.9 ? 1 : 0; car.headGlow.forEach(h => h.material.opacity = headOn); car.beam.material.opacity = 0.05 * headOn; car.groundPool.material.opacity = 0.08 * headOn;
  const facingDoor = Math.max(0, Math.cos((c.yaw + 9) * D2R)) * Math.max(0, Math.cos(c.pitch * D2R));
  const washK = pol.on * (0.17 + 0.16 * facingDoor);
  lens.uniforms.policeAmt.value = washK * Math.max(pol.red, pol.blue);
  lens.uniforms.policeCol.value.copy(pol.red >= pol.blue ? new THREE.Color(1, 0.12, 0.1) : new THREE.Color(0.12, 0.28, 1));
  lens.uniforms.policeDim.value = 0.3 * pol.on;
  amb.intensity = 2.6 - 0.45 * pol.on;
  // phone
  const buzz = inAny(t, [T.buzz1, T.buzz2, ...T.alertBuzz, [T.chime, T.chime + 0.15]]);
  const pc = PHONE_COUNTER.pos.clone(), qc = qCounter.clone();
  if (buzz) { pc.x += 0.0016 * Math.sin(t * 2 * Math.PI * 47); pc.z += 0.0012 * Math.cos(t * 2 * Math.PI * 53); qc.multiply(new THREE.Quaternion().setFromEuler(new THREE.Euler(0, 0, 0.012 * Math.sin(t * 300)))); }
  const Lk = t < T.down[0] ? sineIO(seg(t, ...T.lift)) : 1 - sineIO(seg(t, ...T.down));
  const ph = PHONE_HELD.pos.clone().applyMatrix4(camera.matrixWorld);
  const qh = camera.quaternion.clone().multiply(new THREE.Quaternion().setFromEuler(PHONE_HELD.rot));
  phone.position.copy(pc).lerp(ph, Lk); phone.position.y += 0.06 * Math.sin(Math.PI * Lk);
  phone.quaternion.copy(qc).slerp(qh, Lk); phone.updateMatrixWorld();
  holdR.visible = t >= T.grab[1] && t < T.down[1] - 0.15; holdL.visible = t >= T.lift[0] + 0.25 && t < T.down[1] - 0.2;
  const typedN = Math.floor((t - T.type0) * T.rate), typed = REPLY.slice(0, Math.max(0, typedN));
  const tap = t > T.type0 && t < T.type0 + REPLY.length / T.rate ? Math.abs(Math.sin((t - T.type0) * T.rate * Math.PI)) : 0;
  const kx = ((typedN * 7) % 9) / 9;
  thumbL.position.set(-0.026 + 0.03 * kx, -0.05 + 0.006 * ((typedN * 3) % 3), 0.012 + 0.006 * tap);
  const pstate = t < T.buzz1[0] ? 'off' : t < T.lift[0] + 0.3 ? 'lock' : t < T.down[1] ? 'chat' : t < 20 ? 'lockdim' : t < T.alertBuzz[0][0] ? 'off' : t < T.chime ? 'alert' : 'alert2';
  drawPhone(pstate, typed, pstate === 'alert' ? easeOut(seg(t, T.alertBuzz[0][0], T.alertBuzz[0][0] + 0.25)) : easeOut(seg(t, T.buzz1[0], T.buzz1[0] + 0.25)), t > T.sent);
  // POV hands + arms
  const hs = handsAt(t, bf);
  applyHand(handR, hs.R); applyHand(handL, hs.L);
  const wristR = holdR.visible ? V(0.045, -0.085, -0.03).applyMatrix4(phone.matrixWorld) : handR.g.localToWorld(V(0, 0.004, 0.045));
  placeArm(armR, wristR, 1, bf, holdR.visible || hs.R.vis);
  const wristL = holdL.visible ? V(-0.055, -0.11, -0.03).applyMatrix4(phone.matrixWorld) : handL.g.localToWorld(V(0, 0.004, 0.045));
  placeArm(armL, wristL, -1, bf, holdL.visible || hs.L.vis);
  // characters
  mayaAt(t, armR.fore.position.clone());
  const cs = copAt(t);
  lens.uniforms.glareAmt.value = 0;
  if (cs && cop.flashlight.visible) {
    cop.flashlight.updateMatrixWorld();
    const lp = cop.flashlight.localToWorld(V(0, 0, -0.15)), ld = V(0, 0, -1).transformDirection(cop.flashlight.matrixWorld);
    const facing = Math.max(0, ld.dot(camera.position.clone().sub(lp).normalize()));
    const sp = projectLens(lp);
    if (sp) { lens.uniforms.glarePos.value.copy(sp); lens.uniforms.glareAmt.value = Math.pow(facing, 6) * (0.16 + 1.25 * cs.raise) * (1 + 0.08 * Math.sin(t * 40)); }
  }
  lens.uniforms.vign.value = 0.85 * easeOut(seg(tReal, 112.3, 112.8));
  renderFrame();
  hudAt(tReal);
};
window.DURATION = 116;
window.sceneReady = Promise.resolve(true);
