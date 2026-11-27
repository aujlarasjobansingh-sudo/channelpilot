// CODE BLACK: OAKRIDGE HIGH — Episode 1. POV student in the 2nd-floor library.
import { THREE, scene, camera, renderer, setFocal, projectLens, renderFrame, lens, D2R, sineIO, sineIn, easeOut, seg, lerp, box, glowSprite, canvasTex, F, rr, noOutline } from './core.js';
import { buildSet, EYE, ROOM, MAIN, BACK, DESK, MON, S } from './set.js';
import { makeHand, poseHand, makeArm, placeArm, basisQuat, makeMaya, poseMaya, makeOfficer, poseOfficer, makeSam, poseSam } from './chars.js';

const V = (x, y, z) => new THREE.Vector3(x, y, z);
await Promise.all([500, 600, 700, 800, 900].map(w => document.fonts.load(`${w} 40px Rubik`)));
const DLG = await (await fetch('out/dialogue.json')).json();
buildSet();
scene.background = new THREE.Color('#e9e6dc');
camera.far = 60; camera.updateProjectionMatrix();
const amb = new THREE.AmbientLight('#fff8ec', 2.4); scene.add(amb);
const sun = new THREE.DirectionalLight('#fff1d0', 0.8); sun.position.set(6, 5, -3); scene.add(sun);
const FREEZE = 78.6, DUR = 90;
const T_BOOM = 9.4, T_FEED = 12.3, T_LOCK = 25.2, T_DARK = 25.8, T_GRAB = 26.1, T_HANDLE = 36.0, T_TAP = 49.0, T_WRIST = 56.6, T_STING = 62.0, T_CHARGE = 66.0;

// ---------------- cast
const marcus = makeSam({ jacket: '#7a1f2b', jacketD: '#5e1520', sleeve: '#e8dfc8', jeans: '#2f3f5c', skin: '#8d5a3c', hair: '#1b1310', shoe: '#f2f2ee' });
const lib = makeMaya({ hood: '#6b4f7a', hoodDark: '#563f63', legs: '#2a2e38', skin: '#e8b896', hair: '#9a9a98' });
const chloe = makeMaya({ hood: '#5b7fae', hoodDark: '#4a6a94', legs: '#23262e', skin: '#f0c4a4', hair: '#c9a35a' });
const stA = makeSam({ jacket: '#3c8a52', jacketD: '#2f6e41', jeans: '#2a2e38', skin: '#e2ae8b', hair: '#5a3a22' });
const stB = makeMaya({ hood: '#d9a33a', hoodDark: '#b8862a', legs: '#2a2e38', skin: '#c68a63', hair: '#1b1310' });
const MASK = { mask: true, navy: '#1a1b1f', pants: '#1a1b1f' };
const in1 = makeOfficer(MASK), in2 = makeOfficer(MASK), gunman = makeOfficer(MASK);
const menLight = [0, 1].map(() => { const L = new THREE.PointLight('#f4f6ff', 7, 6, 1.3); scene.add(L); return L; });
[lib, chloe, stB].forEach(m => { m.knife.visible = false; });
const handR = makeHand(1), handL = makeHand(-1), armR = makeArm(), armL = makeArm();
// grey hoodie sleeves for the POV student
[armR, armL].forEach(a => { a.sleeve.material = a.sleeve.material.clone(); a.sleeve.material.color.set('#8a8f98'); a.upper.material = a.sleeve.material; a.fore.material = a.sleeve.material; a.elbow.material = a.sleeve.material; });
// Marcus's pen
const pen = box(0.012, 0.012, 0.14, '#1f3fb0', 0, 0, 0); pen.material = pen.material.clone();

// ---------------- POV phone on the table (NO SERVICE)
const phoneTex = canvasTex(400, 844, () => {});
const phone = new THREE.Group(); scene.add(phone); phone.position.set(0.12, 0.795, -3.82); phone.rotation.set(-Math.PI / 2, 0, 0.15);
box(0.074, 0.154, 0.009, '#1b1d23', 0, 0, 0, phone);
{ const sp = new THREE.Mesh(new THREE.PlaneGeometry(0.067, 0.146), noOutline(new THREE.MeshBasicMaterial({ map: phoneTex }))); sp.position.z = 0.0052; phone.add(sp); }
let phoneState = -1;
function drawPhone(st) {
  if (st === phoneState) return; phoneState = st;
  const g = phoneTex.userData.canvas.getContext('2d'), w = 400, h = 844;
  const bg = g.createLinearGradient(0, 0, 0, h); bg.addColorStop(0, '#3a5fa0'); bg.addColorStop(1, '#152238'); g.fillStyle = bg; g.fillRect(0, 0, w, h);
  g.fillStyle = '#fff'; g.font = F(600, 24); g.textAlign = 'left'; g.fillText('1:48', 26, 40);
  g.textAlign = 'right';
  if (st === 0) { g.fillText('5G', w - 112, 40); for (let i = 0; i < 4; i++) g.fillRect(w - 100 + i * 14, 40 - 8 - i * 6, 9, 8 + i * 6); g.beginPath(); g.arc(w - 30, 42, 14, Math.PI * 1.15, Math.PI * 1.85); g.lineWidth = 4; g.strokeStyle = '#fff'; g.stroke(); }
  else { g.fillStyle = '#ff5a4d'; g.font = F(800, 24); g.fillText('NO SERVICE', w - 22, 40); }
  g.textAlign = 'center'; g.fillStyle = '#fff'; g.font = F(300, 104); g.fillText('1:48', w / 2, 220); g.font = F(500, 26); g.fillText('Tuesday, November 24', w / 2, 262);
  g.fillStyle = 'rgba(255,255,255,0.14)'; rr(g, 24, 330, w - 48, 120, 22); g.fill(); g.fillStyle = '#fff'; g.textAlign = 'left'; g.font = F(700, 24); g.fillText('Chloe', 50, 372); g.font = F(500, 22); g.fillText('omw back w the notes 📝', 50, 410);
  if (st === 1) { g.fillStyle = 'rgba(20,10,10,0.92)'; rr(g, 24, 480, w - 48, 110, 22); g.fill(); g.strokeStyle = '#ff5a4d'; g.lineWidth = 3; g.stroke(); g.fillStyle = '#ff5a4d'; g.font = F(800, 24); g.fillText('⚠ Message not delivered', 46, 524); g.fillStyle = '#fff'; g.font = F(500, 20); g.fillText('No network connection', 46, 560); }
  phoneTex.needsUpdate = true;
}

// ---------------- CCTV: a second camera in the stairwell, grainy B/W on the librarian's monitor
const cctvRT = new THREE.WebGLRenderTarget(400, 300);
const cctvCam = new THREE.PerspectiveCamera(78, 4 / 3, 0.05, 30); cctvCam.position.set(BACK.x + 2.6, 2.9, ROOM.z1 + 4.6); cctvCam.lookAt(BACK.x + 0.8, 0.75, ROOM.z1 + 1.0);
const cctvOverlay = canvasTex(400, 300, (g, w, h) => { g.clearRect(0, 0, w, h); g.fillStyle = '#ffffff'; g.font = '700 20px monospace'; g.fillText('CAM 07  STAIRWELL B', 14, 28); g.fillStyle = '#ff3030'; g.beginPath(); g.arc(w - 74, 22, 7, 0, 7); g.fill(); g.fillStyle = '#fff'; g.fillText('REC', w - 60, 29); g.fillText('11/24  13:52:07', 14, h - 14); });
S.screen.material = new THREE.ShaderMaterial({
  uniforms: { tex: { value: cctvRT.texture }, over: { value: cctvOverlay }, time: { value: 0 }, on: { value: 1 } },
  vertexShader: 'varying vec2 vUv; void main(){ vUv = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }',
  fragmentShader: `uniform sampler2D tex, over; uniform float time, on; varying vec2 vUv;
    float h(vec2 p){ return fract(sin(dot(p, vec2(12.9898, 78.233)) + time * 37.0) * 43758.5453); }
    void main(){ vec3 c = texture2D(tex, vUv).rgb; float y = dot(c, vec3(0.3, 0.59, 0.11)); y = pow(y, 0.85) * 1.15;
      y += (h(floor(vUv * vec2(400.0, 300.0))) - 0.5) * 0.18; y *= 0.88 + 0.12 * sin(vUv.y * 600.0); y *= 1.0 - 0.5 * length(vUv - 0.5);
      vec4 o = texture2D(over, vUv); vec3 col = mix(vec3(y) * vec3(0.92, 1.0, 0.95), o.rgb, o.a);
      gl_FragColor = vec4(col * on, 1.0); }` });
S.screen.material.userData.outlineParameters = { visible: false };

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
  const hand = s => root.clone().add(rt.clone().multiplyScalar(s * 0.26)).add(fwd.clone().multiplyScalar(-stride * 0.8 * Math.sin(off(s)) + 0.05)).add(V(0, 0.95, 0));
  return { footL: foot(-1), footR: foot(1), handL: hand(-1), handR: hand(1), bob: 0.03 * Math.abs(Math.sin(ph)) };
}
const headLook = (root, yaw, lean, headH, pt) => {
  const dir = V(pt.x - root.x, pt.y - headH, pt.z - root.z);
  return { headYaw: Math.max(-1.3, Math.min(1.3, wrapA(Math.atan2(dir.x, dir.z) - yaw))), headPitch: Math.max(-0.75, Math.min(0.75, -Math.atan2(dir.y, Math.hypot(dir.x, dir.z)) - lean)) };
};
const track = (t, keys) => { if (t <= keys[0][0]) return keys[0][1].clone(); for (let i = 1; i < keys.length; i++) if (t <= keys[i][0]) return keys[i - 1][1].clone().lerp(keys[i][1], sineIO(seg(t, keys[i - 1][0], keys[i][0]))); return keys[keys.length - 1][1].clone(); };
const seated = (root, yaw) => ({ hipY: 0.52, lean: 0.05, footL: loc(root, yaw, -0.12, 0, 0.45), footR: loc(root, yaw, 0.13, 0, 0.47), handL: loc(root, yaw, -0.17, 0.8, 0.42), handR: loc(root, yaw, 0.17, 0.8, 0.42) });
const crouch = (root, yaw) => ({ hipY: 0.45, lean: 0.45, footL: loc(root, yaw, -0.16, 0, 0.12), footR: loc(root, yaw, 0.18, 0, -0.18) });
function setVis(ch, v) { ch.root.visible = v; [...ch.hands, ...(ch.feet || ch.boots || ch.shoes), ch.armL.a, ch.armL.j, ch.armL.b, ch.armR.a, ch.armR.j, ch.armR.b, ch.legL.a, ch.legL.j, ch.legL.b, ch.legR.a, ch.legR.j, ch.legR.b].forEach(m => m.visible = v); }

// ============================================================ places
const SEAT = V(0, 0, -3.35), C1 = V(0.85, 0, -0.95), C2 = V(-0.35, 0, -1.0), BD = V(3.62, 0, 1.35), CY = 0.86;
const MSEAT = V(0, 0, -5.05), MC = V(1.6, 0, -0.85), MB = V(4.32, 0, 1.25);
const SPK = V(ROOM.x0 + 0.1, 2.6, -2.6), DOORPT = V(MAIN.x, 1.5, MAIN.z), HANDLE = V(MAIN.x + 0.06, 1.1, MAIN.z + 0.18), GLASS = V(MAIN.x, 1.6, S.glassZ);
const BAR = S.pushBar.getWorldPosition(V(0, 0, 0));
S.monitor.lookAt(BD.x, 1.0, BD.z);

// ============================================================ CAMERA
function camAt(tReal) {
  const t = Math.min(tReal, FREEZE);
  const pos = track(t, [[0, SEAT], [T_GRAB + 0.4, SEAT], [28.4, C1], [29.0, C1], [30.0, C2], [45.4, C2], [46.6, V(0.4, 0, 0.25)], [48.4, BD]]);
  const c = { x: pos.x, y: lerp(EYE, CY, sineIO(seg(t, T_GRAB + 0.3, 28.2))), z: pos.z, yaw: 0, pitch: 0, roll: 0, f: 560 };
  const eye = V(c.x, c.y, c.z);
  const at = p => ({ y: camYawTo(eye, p), p: camPitchTo(eye, p) });
  const mH = marcus.head.getWorldPosition(V(0, 0, 0));
  let { y: yaw, p: pitch } = at(mH); pitch -= 2; let f = 560;
  const blend = (k, b, ff) => { if (k <= 0) return; yaw = lerp(yaw, unwrapNear(b.y, yaw), k); pitch = lerp(pitch, b.p, k); if (ff) f = lerp(f, ff, k); };
  f = lerp(560, 600, seg(t, 0, 6.5));
  blend(sineIO(seg(t, 6.6, 7.4)) * (1 - ease.snap(seg(t, T_BOOM, T_BOOM + 0.5))), at(phone.position), 1700);              // the phone: NO SERVICE
  blend(ease.snap(seg(t, 11.9, 12.3)) * (1 - ease.snap(seg(t, 22.3, 22.6))), at(SPK), 1100);                              // whip up to the PA speaker
  if (t > 12.3 && t < 22.3) f += 220 * sineIO(seg(t, 12.6, 22.0));
  const libH = lib.head.getWorldPosition(V(0, 0, 0));
  blend(ease.snap(seg(t, 22.3, 22.6)) * (1 - sineIO(seg(t, 26.0, 26.4))), at(t < 24.6 ? libH : DOORPT), 600);           // the librarian runs to the doors
  blend(ease.snap(seg(t, T_GRAB, T_GRAB + 0.3)) * (1 - sineIO(seg(t, 27.6, 28.6))), at(mH), 540);                       // Marcus yanks us down
  blend(sineIO(seg(t, 28.2, 29.6)) * (1 - sineIO(seg(t, 34.6, 35.2))), at(GLASS), 980);                                  // peer around the shelf at the door's glass strip
  blend(sineIO(seg(t, 34.6, 35.4)) * (1 - sineIO(seg(t, 40.2, 40.8))), at(HANDLE), 1500);                               // the handle turns
  blend(sineIO(seg(t, 40.3, 40.9)) * (1 - sineIO(seg(t, 45.3, 45.8))), at(mH), 640);                                    // Marcus: the back stairwell
  if (t > 45.3 && t < 48.6) { const q = track(t + 0.4, [[45.4, C2], [46.6, V(0.4, 0, 0.25)], [48.4, BD], [49, BD]]); blend(sineIO(seg(t, 45.3, 45.8)), { y: camYawTo(eye, V(q.x, c.y, q.z)), p: -8 }, 520); }
  blend(sineIO(seg(t, 48.2, 48.9)) * (1 - sineIO(seg(t, 56.8, 57.2))), at(BAR.clone().add(V(0, 0.25, 0))), 620);         // the steel door, Chloe knocking
  blend(sineIO(seg(t, 56.8, 57.2)) * (1 - sineIO(seg(t, 60.6, 61.0))), at(mH), 600);                                    // "Marcus, let go"
  blend(sineIO(seg(t, 60.6, 61.4)) * (1 - ease.snap(seg(t, 66.4, 66.7))), at(MON), 1500);                               // the CCTV monitor
  if (t > 61.4 && t < 66.4) f += 160 * sineIO(seg(t, 61.6, 66.0));
  blend(ease.snap(seg(t, 66.4, 66.7)) * (1 - ease.snap(seg(t, 67.5, 67.8))), at(GLASS), 1300);                         // red light on the front door
  blend(ease.snap(seg(t, 67.5, 67.8)) * (1 - sineIO(seg(t, 71.8, 72.4))), at(BAR.clone().add(V(0, 0.35, 0))), 600);    // back door pounding
  blend(sineIO(seg(t, 71.8, 72.4)) * (1 - sineIO(seg(t, 76.6, 77.4))), at(mH), 640);                                    // Marcus: "she's dead"
  blend(sineIO(seg(t, 76.6, 77.6)), at(BAR.clone().add(V(-0.45, 0.05, -0.2))), 560);                                     // hand on the bar, monitor glowing at the edge
  if (t > 28.5 && t < 34.6) f += 120 * sineIO(seg(t, 29.6, 34.0));
  c.yaw = yaw + noise(t, 1) * (t > 22.3 && t < 30 ? 1.6 : 0.5); c.pitch = pitch + noise(t, 2) * (t > 22.3 && t < 30 ? 1.2 : 0.4); c.f = f;
  c.y += 0.55 * sineIO(seg(t, 66.2, 66.6)) * (1 - sineIO(seg(t, 67.4, 67.9)));            // half-stands to see over the desk
  if (t > 45.3 && t < 48.4) { const ph = t * 2.4 * Math.PI * 2; c.y += 0.04 * Math.abs(Math.sin(ph)); c.roll = 2 * Math.sin(ph); }
  for (const [t0, a] of [[T_BOOM, 2.0], [T_FEED, 0.8], [T_LOCK, 0.6], [T_GRAB, 2.0], [T_HANDLE, 0.5], [T_WRIST, 1.6], [T_STING, 0.6], [T_CHARGE + 0.4, 0.8], [68.2, 0.8], [69.4, 0.8], [70.6, 0.8]]) {
    if (t > t0 && t < t0 + 0.45) { const d = t - t0; c.yaw += a * Math.exp(-d * 11) * Math.sin(d * 55); c.pitch += a * 0.7 * Math.exp(-d * 11) * Math.cos(d * 47); }
  }
  if (tReal > FREEZE) c.f *= 1 + 0.012 * Math.pow(Math.max(0, Math.sin((tReal - FREEZE) * Math.PI * 2 * 1.15)), 8);
  return c;
}

// ============================================================ MARCUS
function marcusAt(t) {
  const mouth = mouthOf('marcus', t), POVc = camera.position.clone();
  const bored = { eyes: 0.8, worry: -0.2, mouthBase: 0.04 }, alert = { eyes: 1.15, worry: 0.8, mouthBase: 0.1 }, terror = { eyes: 1.3, worry: 1.4, mouthBase: 0.2 };
  let p, tgt = POVc.clone(), expr = bored;
  if (t < T_GRAB) {
    const root = MSEAT.clone(), yaw = 0; p = { x: root.x, z: root.z, yaw, ...seated(root, yaw) };
    const spin = t < T_BOOM ? 1 : 0; p.handR = loc(root, yaw, 0.15 + 0.02 * Math.cos(t * 7) * spin, 0.84 + 0.02 * Math.sin(t * 7) * spin, 0.45);
    pen.visible = true; pen.position.copy(p.handR).add(V(0, 0.03, 0)); pen.rotation.set(0, t * 9 * spin, 0);
    if (t > T_BOOM) expr = alert; if (t > 12.0 && t < 22.4) tgt = SPK; if (t > 22.4) { tgt = lib.head.getWorldPosition(V(0, 0, 0)); expr = terror; }
  } else {
    pen.visible = t < T_GRAB + 0.2;
    let root, yaw, cr;
    if (t < 28.4) { const k = sineIO(seg(t, T_GRAB + 0.25, 28.3)); root = MSEAT.clone().lerp(V(-0.9, 0, -4.0), Math.min(1, k * 2)).lerp(MC, Math.max(0, k * 2 - 1)); yaw = yawTo(root, POVc); cr = crouch(root, yaw); cr.hipY = lerp(0.85, 0.45, k); cr.lean = lerp(0.3, 0.45, k); expr = terror; }
    else if (t < 45.5) { root = MC.clone(); yaw = yawTo(root, V(MAIN.x, 0, MAIN.z)); cr = crouch(root, yaw); expr = alert; tgt = GLASS; if (t > 40.4) { tgt = POVc; expr = terror; } }
    else if (t < 48.6) { const k = seg(t, 45.5, 48.4); root = MC.clone().lerp(V(2.2, 0, 0.3), Math.min(1, k * 2)).lerp(MB, Math.max(0, k * 2 - 1)); yaw = yawTo(MC, MB); cr = crouch(root, yaw); cr.hipY = 0.62; expr = terror; tgt = V(BACK.x, 1, BACK.z); const gt = gait(t, root, yaw, 2.0); cr.footL = gt.footL; cr.footR = gt.footR; }
    else { root = MB.clone(); yaw = yawTo(root, V(BACK.x, 0, BACK.z)); cr = crouch(root, yaw); expr = terror; tgt = t > 59 && t < 66.5 ? MON : t > 49.0 && t < 56.5 ? V(BACK.x, 1.2, BACK.z) : POVc; }
    p = { x: root.x, z: root.z, yaw, ...cr, expr };
    const sh = loc(root, yaw, 0.18, cr.hipY + 0.5, 0.05);
    p.handL = loc(root, yaw, -0.25, cr.hipY + 0.05, 0.25); p.handR = loc(root, yaw, 0.25, cr.hipY + 0.05, 0.25);
    if (t < 27.2) { const g = sineIO(seg(t, T_GRAB - 0.15, T_GRAB + 0.15)); p.handR = p.handR.clone().lerp(camLocal(0.22, -0.32, -0.28), g * (1 - sineIO(seg(t, 26.9, 27.4)))); }
    if (t > 40.6 && t < 45.4) { const k = sineIO(seg(t, 41.0, 41.5)); p.handR = p.handR.clone().lerp(sh.clone().add(V(BACK.x, 1.1, BACK.z).sub(sh).normalize().multiplyScalar(0.55)), k); p.handRdir = V(BACK.x, 1.1, BACK.z).sub(sh).normalize(); }
    if (t > T_WRIST - 0.25 && t < 60.8) { const g = sineIO(seg(t, T_WRIST - 0.25, T_WRIST)); p.handL = p.handL.clone().lerp(handR.g.position.clone().add(V(0, 0.0, 0.05)), g); }
    if (t > 59.0 && t < 66.0) { const k = sineIO(seg(t, 59.0, 59.5)); p.handR = p.handR.clone().lerp(sh.clone().add(MON.clone().sub(sh).normalize().multiplyScalar(0.55)), k); p.handRdir = MON.clone().sub(sh).normalize(); }
    if (t > 66) { p.handL = p.handL.clone().add(V(Math.sin(t * 37) * 0.006, Math.sin(t * 41) * 0.006, 0)); }
  }
  Object.assign(p, headLook(V(p.x, 0, p.z), p.yaw, p.lean, p.hipY + 0.78, tgt));
  poseSam(marcus, p, t, Math.min(1, mouth * 1.15));
}

// ============================================================ LIBRARIAN + STUDENTS
function libAt(t) {
  let root, yaw, p;
  const behindDesk = V(DESK.x + 0.1, 0, DESK.z + 0.55), atDoor = V(MAIN.x + 0.45, 0, MAIN.z + 0.35), sw = V(MAIN.x + 0.45, 0, MAIN.z + 1.25), hide = V(MAIN.x + 0.6, 0, MAIN.z + 1.9);
  const expr = t > 13 ? { eyes: 1.2, worry: 1.3, mouthBase: 0.3 } : { eyes: 0.9, worry: 0, mouthBase: 0.05 };
  if (t < 22.3) { root = behindDesk; yaw = Math.PI; p = { hipY: 0.94, lean: 0.05, footL: loc(root, yaw, -0.11, 0, 0), footR: loc(root, yaw, 0.12, 0, 0.04), handL: loc(root, yaw, -0.2, 0.86, 0.3), handR: loc(root, yaw, 0.2, 0.86, 0.3) }; }
  else if (t < 25.0) { const k = seg(t, 22.3, 25.0); root = behindDesk.clone().lerp(V(-1.6, 0, -2.6), Math.min(1, k * 1.8)).lerp(atDoor, Math.max(0, (k - 0.55) / 0.45)); yaw = yawTo(root, atDoor); const gt = gait(t, root, yaw, 2.6); p = { hipY: 0.9 - gt.bob, lean: 0.3, ...gt }; }
  else if (t < 26.4) { root = atDoor.clone().lerp(sw, sineIO(seg(t, 25.35, 25.7))); yaw = -Math.PI / 2; p = { hipY: 0.94, lean: 0.1, footL: loc(root, yaw, -0.11, 0, 0), footR: loc(root, yaw, 0.12, 0, 0.04), handL: loc(root, yaw, -0.2, 0.9, 0.2),
    handR: t < 25.4 ? S.boltKnob.getWorldPosition(V(0, 0, 0)).add(V(0.04, 0, 0)) : V(MAIN.x + 0.04, 1.3, MAIN.z + 1.35) }; }
  else { root = sw.clone().lerp(hide, sineIO(seg(t, 26.4, 27.2))); yaw = yawTo(root, V(0, 0, -3)); p = { hipY: 0.42, lean: 0.55, footL: loc(root, yaw, -0.15, 0, 0.12), footR: loc(root, yaw, 0.17, 0, -0.15), handL: loc(root, yaw, -0.12, 0.85, 0.25), handR: loc(root, yaw, 0.12, 0.88, 0.25) }; }
  Object.assign(p, { x: root.x, z: root.z, yaw, knife: false, expr }, headLook(root, yaw, p.lean, p.hipY + 0.72, t > 12 && t < 22.3 ? SPK : t > 26.4 ? camera.position : V(MAIN.x, 1.4, MAIN.z)));
  poseMaya(lib, p, t, t > 22.4 && t < 25 ? 0.4 : 0);
}
function studentsAt(t) {
  { // A: green hoodie at the left table → ducks under it
    const r0 = V(-3.4, 0, -5.85); let p;
    if (t < 22.8) { p = { x: r0.x, z: r0.z, yaw: 0, ...seated(r0, 0), expr: t > T_BOOM ? { eyes: 1.2, worry: 1.0, mouthBase: 0.2 } : {} }; Object.assign(p, headLook(r0, 0, 0.05, 1.3, t > 12 && t < 22.3 ? SPK : t > T_BOOM ? camera.position : V(-3.4, 0.8, -5.0))); }
    else { const k = sineIO(seg(t, 22.8, 23.8)), root = r0.clone().lerp(V(-3.4, 0, -5.1), k); p = { x: root.x, z: root.z, yaw: 0, hipY: lerp(0.52, 0.32, k), lean: lerp(0.05, 0.9, k), footL: loc(root, 0, -0.15, 0, -0.35), footR: loc(root, 0, 0.15, 0, -0.35), handL: loc(root, 0, -0.1, 0.5, 0.3), handR: loc(root, 0, 0.1, 0.52, 0.3), expr: { eyes: 1.2, worry: 1.4, mouthBase: 0.3 }, headPitch: 0.3 }; }
    poseSam(stA, p, t, 0);
  }
  { // B: yellow hoodie at the right table → crouches beside it
    const r0 = V(3.4, 0, -3.55), y0 = Math.PI; let p;
    if (t < 23.0) { p = { x: r0.x, z: r0.z, yaw: y0, ...seated(r0, y0), knife: false, expr: t > T_BOOM ? { eyes: 1.2, worry: 1.1, mouthBase: 0.2 } : {} }; Object.assign(p, headLook(r0, y0, 0.05, 1.25, t > 12 && t < 22.3 ? SPK : V(3.4, 0.8, -4.4))); }
    else { const k = sineIO(seg(t, 23.0, 24.0)), root = r0.clone().lerp(V(4.2, 0, -3.1), k); p = { x: root.x, z: root.z, yaw: y0, hipY: lerp(0.52, 0.4, k), lean: 0.6, footL: loc(root, y0, -0.15, 0, 0.1), footR: loc(root, y0, 0.15, 0, -0.1), handL: loc(root, y0, -0.12, 0.95, 0.15), handR: loc(root, y0, 0.12, 0.98, 0.15), knife: false, expr: { eyes: 1.25, worry: 1.4, mouthBase: 0.35 }, headPitch: 0.1 }; }
    poseMaya(stB, p, t, 0);
  }
}

// ============================================================ INTRUDERS (hallway) + the STAIRWELL
function intruder(o, t, root, yaw, extra = {}) {
  o.torso.updateMatrixWorld();
  const fwdPt = loc(root, yaw, 0, 1.2, 3);
  const handR = loc(root, yaw, 0.2, 1.22, 0.45), handL = o.torso.localToWorld(V(-0.22, 0.62, 0.38));
  const p = { x: root.x, z: root.z, yaw, hipY: 1.02, lean: 0.05, handL, handR, handRdir: fwdPt.clone().sub(handR).normalize(), handLdir: fwdPt.clone().sub(handL).normalize(),
    footL: loc(root, yaw, -0.13, 0, 0), footR: loc(root, yaw, 0.14, 0, 0.04), flash: true, flashOn: 1, gun: false, rifle: true, blood: false, badge: false, headYaw: 0, headPitch: 0, ...extra };
  if (extra.walk) { const gt = gait(t, root, yaw, extra.walk, extra.ph || 0); p.footL = gt.footL; p.footR = gt.footR; p.hipY -= gt.bob * 0.6; }
  poseOfficer(o, p, t, 0); o.face.shadow.material.opacity = 0; o.beam.material.opacity = 0.05;
}
function hallwayAt(t) {
  const X = MAIN.x - 1.4;
  const v2 = t > 29.2 && t < 34.6; setVis(in2, v2);
  if (v2) { const z = lerp(0.0, -11.5, seg(t, 29.2, 34.4)); intruder(in2, t, V(X + 0.2, 0, z), Math.PI, { walk: 1.5, ph: 0.5 }); }
  const v1 = t > 29.6 && t < 42.5; setVis(in1, v1);
  if (v1) {
    let z, yaw = Math.PI, walk = 1.5, extra = {};
    if (t < 33.4) z = lerp(-1.0, -10.0, seg(t, 29.6, 33.4));
    else if (t < 35.2) { z = lerp(-10.0, MAIN.z + 0.3, sineIO(seg(t, 33.6, 35.2))); yaw = 0; }
    else if (t < 40.2) { z = MAIN.z + 0.3; yaw = Math.PI / 2; walk = 0;   // facing the door: tests the handle, radios in
      extra.handL = t > T_HANDLE - 0.3 && t < 37.0 ? V(MAIN.x - 0.08, 1.1, MAIN.z + 0.18) : t > 37.2 && t < 39.6 ? loc(V(X + 0.75, 0, z), yaw, -0.12, 1.5, 0.05) : undefined; extra.flash = !(t > T_HANDLE - 0.3 && t < 37.0); }
    else { z = lerp(MAIN.z + 0.3, 2.5, seg(t, 40.2, 42.4)); yaw = 0; }
    const x = t > 35.2 && t < 40.2 ? X + 0.75 : X;
    if (extra.handL === undefined) delete extra.handL;
    intruder(in1, t, V(x, 0, z), yaw, { walk: t > 33.4 && t < 33.6 ? 0 : walk, ...extra });
  }
  S.hallLight.intensity = t > 28 ? 2.2 : 0.8;
  menLight.forEach((L, i) => { const o = i ? in2 : in1; L.visible = o.root.visible; if (L.visible) { o.flashlight.updateMatrixWorld(); L.position.copy(o.flashlight.localToWorld(V(0, 0, -0.4))); } });
}
function stairwellAt(t) {
  // Chloe at the steel door; the masked gunman crouched behind the blind corner, rifle on the door
  const cr = V(BACK.x, 0, ROOM.z1 + 0.42), yaw = Math.PI;
  const tap = t > T_TAP && t < 56 ? Math.max(0, Math.sin(t * 22)) : 0, pound = t > 67.4 ? Math.max(0, Math.sin(t * 13)) : 0;
  const p = { x: cr.x, z: cr.z, yaw, hipY: 0.92, lean: 0.12, knife: false, footL: loc(cr, yaw, -0.11, 0, 0), footR: loc(cr, yaw, 0.12, 0, 0.04),
    handL: loc(cr, yaw, -0.18, 1.35, 0.28 + 0.04 * tap + 0.05 * pound), handR: loc(cr, yaw, 0.15, 1.15 + 0.1 * pound, 0.27 + 0.05 * pound),
    expr: { eyes: 1.2, worry: 1.4, tears: 1, mouthBase: 0.3 }, headYaw: Math.sin(t * 0.7) * 0.4, headPitch: 0.1 };
  poseMaya(chloe, p, t, Math.min(1, mouthOf('chloe', t)));
  const g = V(BACK.x + 2.05, 0, ROOM.z1 + 1.35), gy = yawTo(g, V(BACK.x, 0, ROOM.z1 + 0.3));
  gunman.torso.updateMatrixWorld();
  const aim = V(BACK.x, 1.0, ROOM.z1 + 0.3), sh = gunman.torso.localToWorld(V(0.12, 0.5, 0)), hr = sh.clone().add(aim.clone().sub(sh).normalize().multiplyScalar(0.45));
  poseOfficer(gunman, { x: g.x, z: g.z, yaw: gy, hipY: 0.5, lean: 0.35, handR: hr, handRdir: aim.clone().sub(hr).normalize(), handL: hr.clone().add(aim.clone().sub(hr).normalize().multiplyScalar(0.25)).add(V(0, -0.04, 0)),
    footL: loc(g, gy, -0.18, 0, 0.15), footR: loc(g, gy, 0.18, 0, -0.25), flash: false, gun: false, rifle: true, blood: false, badge: false, headYaw: 0, headPitch: 0.2 }, t, 0);
  gunman.face.shadow.material.opacity = 0;
}

// ============================================================ POV hands
function applyHand(h, s) { h.g.visible = s.vis; if (s.vis) { h.g.position.copy(s.pos); h.g.quaternion.copy(basisQuat(s.fd, s.pn)); poseHand(h, s.pose); h.g.updateMatrixWorld(); } }
function handsAt(t) {
  const R = { pos: V(0, 0, 0), fd: V(0, 0, -1), pn: V(0, -1, 0), pose: 'rest', vis: false };
  const L = { pos: V(0, 0, 0), fd: V(0, 0, -1), pn: V(0, -1, 0), pose: 'rest', vis: false };
  if (t < T_GRAB + 0.2) {   // hands resting on the table, right one by the phone
    R.pos = V(0.2, 0.8, -3.75); R.fd = V(-0.2, -0.15, -1); L.pos = V(-0.24, 0.8, -3.78); L.fd = V(0.2, -0.15, -1); R.vis = L.vis = true; R.pose = L.pose = 'rest';
    if (t > T_BOOM && t < T_BOOM + 0.5) { R.pos.y += 0.02 * Math.sin((t - T_BOOM) * 40); L.pos.y += 0.02 * Math.sin((t - T_BOOM) * 38); }
  }
  if (t > 45.5 && t < 48.4) {  // crouch-running
    const ph = t * 2.4 * Math.PI; for (const [H, s] of [[R, 1], [L, -1]]) { const sw = Math.sin(ph + (s > 0 ? 0 : Math.PI)); H.pos = camLocal(s * 0.24, -0.48 + 0.12 * Math.max(0, sw), -0.32); H.fd = camDir(-s * 0.3, 0.5, -1); H.pn = camDir(-s * 0.8, -0.2, 0); H.pose = 'grip'; H.vis = sw > -0.2; }
  }
  if (t > 55.3) {              // hand on the push-bar (trembling); taken off while looking at the monitor / the front door
    const on = sineIO(seg(t, 55.3, 56.2)) * (1 - sineIO(seg(t, 60.6, 61.2)) * (1 - sineIO(seg(t, 67.6, 68.4))));
    const tr = V(Math.sin(t * 53) * 0.004, Math.sin(t * 47) * 0.004, 0).multiplyScalar(t > 72 ? 1.6 : 1);
    R.pos = camLocal(0.28, -0.55, -0.2).lerp(BAR.clone().add(V(-0.12, 0.035, -0.05)).add(tr), on); R.fd = V(0.55, -0.05, 0.8).normalize(); R.pn = V(0, 0, 1); R.pose = on > 0.6 ? 'grip' : 'hover'; R.vis = on > 0.03;
  }
  return { R, L };
}

// ============================================================ HUD
const titleEl = document.getElementById('title'), subEl = document.getElementById('subtxt'), ctaEl = document.getElementById('cta');
function hudAt(t) {
  const a = easeOut(seg(t, 0.15, 0.55)), out = seg(t, 6.2, 6.6);
  titleEl.style.opacity = a * (1 - out); titleEl.style.transform = `translateX(${-12 * (1 - a)}px)`;
  let sub = null;
  for (const l of DLG.lines) for (const c of l.chunks) if (t >= c.t0 && t < c.t1) sub = { c, spk: l.spk };
  subEl.textContent = sub ? sub.c.text : ''; subEl.className = sub ? sub.spk : '';
  if (sub) subEl.style.transform = `translateX(-50%) scale(${0.91 + 0.09 * easeOut(seg(t, sub.c.t0, sub.c.t0 + 0.1))})`;
  document.getElementById('sub').style.top = t > FREEZE + 0.3 ? '1150px' : '839px';
  ctaEl.style.display = t > FREEZE + 0.7 ? 'block' : 'none';
  if (t > FREEZE + 0.7) {
    const k = easeOut(seg(t, FREEZE + 0.7, FREEZE + 1.0)); ctaEl.querySelector('.q').style.transform = `scale(${0.85 + 0.15 * k})`; ctaEl.style.opacity = k;
    ctaEl.querySelectorAll('.btn').forEach((b, i) => { const kb = easeOut(seg(t, FREEZE + 0.9 + i * 0.15, FREEZE + 1.2 + i * 0.15)); b.style.transform = `scale(${0.8 + 0.2 * kb})`; b.style.opacity = kb; });
  }
}

// ============================================================ render
window.setHud = on => { document.getElementById('hud').style.display = on ? 'block' : 'none'; const r = document.getElementById('rainfx'); if (r) r.style.display = 'none'; };
const sunCol = new THREE.Color('#fff6d8'), duskCol = new THREE.Color('#7f93b8');
window.renderAt = (tReal) => {
  const t = Math.min(tReal, FREEZE);
  // lights: bright afternoon → librarian kills the lights (25.8) → dim blue
  const dark = easeOut(seg(t, T_DARK, T_DARK + 0.15));
  amb.intensity = lerp(2.4, 0.95, dark); sun.intensity = lerp(0.8, 0.25, dark); amb.color.set(dark > 0.5 ? '#c9d6ff' : '#fff8ec');
  S.panels.forEach(p => p.material.color.set(dark > 0.5 ? '#8f959e' : '#fbfaf0'));
  S.windows.forEach((w, i) => { if (i % 2 === 0) w.material.color.copy(sunCol).lerp(duskCol, dark); else w.material.opacity = lerp(0.14, 0.03, dark); });
  scene.background.set(dark > 0.5 ? '#3a4152' : '#e9e6dc');
  // doors: deadbolt flips, lever turns, red charge blinks; steel door rattles under Chloe's fists
  S.boltKnob.rotation.x = Math.PI / 2 * easeOut(seg(t, T_LOCK, T_LOCK + 0.12));
  S.lever.rotation.x = -0.55 * Math.sin(seg(t, T_HANDLE, 36.4) * Math.PI) - 0.5 * Math.sin(seg(t, 36.4, 36.8) * Math.PI);
  S.charge.material.opacity = t > T_CHARGE ? ((t * 2.2) % 1 < 0.5 ? 1 : 0.05) : 0;
  const pound = t > 67.4 ? Math.max(0, Math.sin(t * 13)) : t > T_TAP && t < 56 ? 0.25 * Math.max(0, Math.sin(t * 22)) : 0;
  S.backDoor.rotation.y = 0.004 * pound; S.pushBar.position.z = -0.08 + 0.003 * pound;
  drawPhone(t < 8.0 ? 0 : 1);
  // cast
  marcusAt(t); libAt(t); studentsAt(t); hallwayAt(t); stairwellAt(t);
  // camera
  const c = camAt(tReal);
  camera.position.set(c.x, c.y, c.z); camera.rotation.set(c.pitch * D2R, c.yaw * D2R, (c.roll || 0) * D2R); camera.updateMatrixWorld(); setFocal(c.f);
  const bf = new THREE.Matrix4().makeRotationY(c.yaw * D2R); bf.setPosition(c.x, c.y, c.z);
  const hs = handsAt(t); applyHand(handR, hs.R); applyHand(handL, hs.L);
  placeArm(armR, handR.g.localToWorld(V(0, 0.004, 0.045)), 1, bf, hs.R.vis);
  placeArm(armL, handL.g.localToWorld(V(0, 0.004, 0.045)), -1, bf, hs.L.vis);
  // CCTV feed
  S.screen.material.uniforms.time.value = t;
  const vis = [handR.g, handL.g, armR.fore, armR.upper, armR.sleeve, armR.elbow, armL.fore, armL.upper, armL.sleeve, armL.elbow].map(m => [m, m.visible]); vis.forEach(([m]) => m.visible = false);
  renderer.setRenderTarget(cctvRT); renderer.render(scene, cctvCam); renderer.setRenderTarget(null);
  vis.forEach(([m, v]) => m.visible = v);
  // lens: blue gloom after the lights go out, BOOM flash, sting, red glow on the charge
  lens.uniforms.policeAmt.value = 0.12 * dark; lens.uniforms.policeCol.value.set(0.25, 0.4, 1.0); lens.uniforms.policeDim.value = 0.1 * dark;
  lens.uniforms.glareAmt.value = 0;
  if (t > 61 && t < 66.4) { const gp = projectLens(MON); if (gp) { lens.uniforms.glarePos.value.copy(gp); lens.uniforms.glareAmt.value = 0.06; } }
  lens.uniforms.flash.value = (t > T_BOOM && t < T_BOOM + 0.06 ? 0.06 : 0) + (t > T_STING && t < T_STING + 0.05 ? 0.06 : 0);
  lens.uniforms.vign.value = 0.25 + 0.6 * easeOut(seg(tReal, FREEZE - 0.15, FREEZE + 0.4));
  renderFrame();
  hudAt(tReal);
};
window.DURATION = DUR;
window.sceneReady = Promise.resolve(true);
