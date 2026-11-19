// debug harness: static poses for look-dev. Open index.html?debug
import { THREE, scene, camera, setFocal, renderFrame, D2R } from './core.js';
import { buildSet, drawRain, car, EYE, CT, setDoor, body } from './set.js';
window._body = body;
import { makeMaya, poseMaya, makeOfficer, poseOfficer } from './chars.js';
const V = (x, y, z) => new THREE.Vector3(x, y, z);
await Promise.all([500, 600, 700, 800, 900].map(w => document.fonts.load(`${w} 40px Rubik`)));
buildSet();
scene.background = new THREE.Color('#cfccc4');
scene.add(new THREE.AmbientLight('#f4f7ff', 2.6)); const sun = new THREE.DirectionalLight('#ffffff', 0.75); sun.position.set(-1, 6, 2); scene.add(sun);
const maya = makeMaya(), cop = makeOfficer();
const VIEWS = {
  maya: { pos: V(0, EYE, 0), yaw: -2, pitch: -9, f: 620 },
  wide: { pos: V(0, EYE, 0), yaw: -10, pitch: -2, f: 540 },
  cop: { pos: V(0, EYE, 0), yaw: -9.3, pitch: 0, f: 1000 },
  down: { pos: V(0.05, 1.55, -0.05), yaw: -58, pitch: -52, f: 540 },
  btn: { pos: V(0.05, 1.12, 0.1), yaw: -8, pitch: -42, f: 540 },
};
window.renderAt = (t, view = 'maya') => {
  drawRain(t);
  car.g.position.set(1.2, 0, -10.3);
  car.red.material.color.set('#ff3030'); car.redGlow.material.opacity = 1; car.blueGlow.material.opacity = 0.3;
  poseMaya(maya, view === 'down'
    ? { x: 0.5, z: -0.32, yaw: Math.PI * 0.85, hipY: 0.42, lean: 0.35, headPitch: -0.5, handL: V(0.36, 0.45, -0.2), handR: V(0.62, 0.9, -0.35), footL: V(0.4, 0.0, -0.45), footR: V(0.62, 0.0, -0.4), expr: { eyes: 1.25, worry: 1, mouthBase: 0.3 } }
    : { x: 0.03, z: -1.02, yaw: 0, hipY: 0.98, lean: 0.45, headPitch: -0.35, handL: V(-0.2, CT + 0.02, -0.6), handR: V(0.12, CT + 0.08, -0.42), footL: V(-0.1, 0, -1.15), footR: V(0.14, 0, -1.2), expr: { eyes: 1.3, worry: 1, mouthBase: 0.35, tears: 1 } }, t, 0.3);
  poseOfficer(cop, { x: 1.15, z: -7.45, yaw: -0.08, hipY: 1.02, headPitch: 0.05, handL: V(0.85, 1.25, -7.1), handLdir: V(0.1, 0.2, 1), handR: V(1.35, 1.55, -7.12), handRdir: V(0, 1, 0.1), palmR: V(0, 0, 1), footL: V(1.05, 0, -7.5), footR: V(1.27, 0, -7.45), flash: true, flashOn: 1, badge: true }, t, 0.4);
  setDoor('L', 0);
  if (view !== 'maya') maya.root.position.x = 9;
  import('./set.js').then(m => {}); 
  const v = VIEWS[view];
  camera.position.copy(v.pos); camera.rotation.set(v.pitch * D2R, v.yaw * D2R, 0); camera.updateMatrixWorld(); setFocal(v.f);
  window._body && (window._body.visible = view !== 'btn');
  renderFrame();
};
window.setHud = () => {};
window.sceneReady = Promise.resolve(true);
