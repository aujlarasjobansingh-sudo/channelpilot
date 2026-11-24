// Core: renderer, shared helpers, stereographic lens pass (zoomable) + police wash, glare, vignette.
import * as THREE from 'three';
import { OutlineEffect } from 'three/addons/effects/OutlineEffect.js';
export { THREE };

export const W = 720, H = 1280, SRC_W = 1350, SRC_H = 2400, R_C = Math.hypot(W / 2, H / 2);
export const OUT = 0.0029;
const canvas = document.getElementById('c');
export const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, preserveDrawingBuffer: true });
renderer.setPixelRatio(1); renderer.setSize(W, H, false);
export const scene = new THREE.Scene();

// ---------------------------------------------------------------- materials / builders
const grad = new THREE.DataTexture(new Uint8Array([196, 234, 255]), 3, 1, THREE.RedFormat);
grad.minFilter = grad.magFilter = THREE.NearestFilter; grad.needsUpdate = true;
const matCache = {};
export function M(color, opts = {}) {
  const { thin, flat, ...mo } = opts;
  const key = color + (thin ? 't' : '') + (flat ? 'f' : '');
  if (matCache[key] && !mo.map) return matCache[key];
  const m = flat ? new THREE.MeshBasicMaterial({ color, ...mo }) : new THREE.MeshToonMaterial({ color, gradientMap: grad, ...mo });
  m.userData.outlineParameters = { thickness: thin ? OUT * 0.6 : OUT, color: [0.08, 0.08, 0.09], alpha: 1 };
  if (!mo.map) matCache[key] = m;
  return m;
}
export const noOutline = m => { m.userData.outlineParameters = { visible: false }; return m; };
export const INK = noOutline(new THREE.MeshBasicMaterial({ color: '#17171b' }));
export const mat = c => (typeof c === 'string' ? M(c) : c);
export const add = (m, p) => { (p || scene).add(m); return m; };
export function box(w, h, d, color, x, y, z, parent, opts) {
  const m = add(new THREE.Mesh(new THREE.BoxGeometry(w, h, d), typeof color === 'string' ? M(color, opts) : color), parent);
  m.position.set(x, y, z); return m;
}
export function cyl(rt, rb, h, color, x, y, z, parent, seg = 24) {
  const m = add(new THREE.Mesh(new THREE.CylinderGeometry(rt, rb, h, seg), mat(color)), parent); m.position.set(x, y, z); return m;
}
export function sph(r, color, x, y, z, parent, seg = 32) {
  const m = add(new THREE.Mesh(new THREE.SphereGeometry(r, seg, Math.max(12, seg * 0.6 | 0)), mat(color)), parent); m.position.set(x, y, z); return m;
}
export function capsule(r, len, color, parent) { return add(new THREE.Mesh(new THREE.CapsuleGeometry(r, len, 8, 16), mat(color)), parent); }
export function orient(mesh, A, B) {
  mesh.position.copy(A).add(B).multiplyScalar(0.5);
  mesh.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), B.clone().sub(A).normalize());
  mesh.scale.set(1, Math.max(1e-4, A.distanceTo(B)), 1);
}
export function inkLine(a, b, t = 0.02) {
  const m = add(new THREE.Mesh(new THREE.CylinderGeometry(t / 2, t / 2, 1, 6), INK));
  orient(m, new THREE.Vector3(...a), new THREE.Vector3(...b)); return m;
}
export function canvasTex(w, h, draw) {
  const c = document.createElement('canvas'); c.width = w; c.height = h;
  draw(c.getContext('2d'), w, h);
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 16;
  t.userData.canvas = c; return t;
}
export function texPlane(w, h, tex, x, y, z, parent, transparent = true) {
  const m = add(new THREE.Mesh(new THREE.PlaneGeometry(w, h), noOutline(new THREE.MeshBasicMaterial({ map: tex, transparent }))), parent);
  m.position.set(x, y, z); return m;
}
export function glowMat(color, opacity = 1) {
  return noOutline(new THREE.MeshBasicMaterial({ color, transparent: true, opacity, blending: THREE.AdditiveBlending, depthWrite: false }));
}
export function rr(g, x, y, w, h, r) { g.beginPath(); g.moveTo(x + r, y); g.arcTo(x + w, y, x + w, y + h, r); g.arcTo(x + w, y + h, x, y + h, r); g.arcTo(x, y + h, x, y, r); g.arcTo(x, y, x + w, y, r); g.closePath(); }
export const F = (wt, px) => `${wt} ${px}px Rubik, sans-serif`;
let seed = 7; export const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
// radial glow sprite texture
export const glowTex = canvasTex(128, 128, (g, w) => {
  const gr = g.createRadialGradient(64, 64, 0, 64, 64, 64); gr.addColorStop(0, 'rgba(255,255,255,1)'); gr.addColorStop(0.25, 'rgba(255,255,255,0.55)'); gr.addColorStop(1, 'rgba(255,255,255,0)');
  g.fillStyle = gr; g.fillRect(0, 0, w, w);
});
export function glowSprite(color, size, parent) {
  const s = new THREE.Sprite(noOutline(new THREE.SpriteMaterial({ map: glowTex, color, transparent: true, blending: THREE.AdditiveBlending, depthWrite: false })));
  s.scale.set(size, size, 1); add(s, parent); return s;
}

// ---------------------------------------------------------------- easing
export const sineIO = t => 0.5 - 0.5 * Math.cos(Math.PI * t);
export const sineIn = t => 1 - Math.cos(Math.PI * t / 2);
export const easeOut = t => 1 - Math.pow(1 - t, 3);
export const seg = (t, a, b) => Math.min(1, Math.max(0, (t - a) / (b - a)));
export const lerp = (a, b, k) => a + (b - a) * k;
export const D2R = Math.PI / 180;

// ---------------------------------------------------------------- camera + lens
export const camera = new THREE.PerspectiveCamera(130, W / H, 0.012, 80);
camera.rotation.order = 'YXZ';
const effect = new OutlineEffect(renderer, { defaultThickness: OUT, defaultColor: [0.08, 0.08, 0.09] });
const rt = new THREE.WebGLRenderTarget(SRC_W, SRC_H, { samples: 4, type: THREE.HalfFloatType });
export const lens = new THREE.ShaderMaterial({
  uniforms: {
    tSrc: { value: rt.texture }, focal: { value: 540 }, res: { value: new THREE.Vector2(W, H) }, tanXY: { value: new THREE.Vector2(1, 1) },
    policeAmt: { value: 0 }, policeCol: { value: new THREE.Color(1, 0, 0) }, policeDim: { value: 0 },
    glarePos: { value: new THREE.Vector2(0, 0) }, glareAmt: { value: 0 }, vign: { value: 0 }, flash: { value: 0 },
  },
  vertexShader: `varying vec2 vUv; void main(){ vUv = uv; gl_Position = vec4(position.xy, 0., 1.); }`,
  fragmentShader: `
    uniform sampler2D tSrc; uniform float focal; uniform vec2 res; uniform vec2 tanXY; varying vec2 vUv;
    uniform float policeAmt; uniform vec3 policeCol; uniform float policeDim;
    uniform vec2 glarePos; uniform float glareAmt; uniform float vign; uniform float flash;
    vec3 toSRGB(vec3 c){ c = max(c, 0.0); return mix(c*12.92, 1.055*pow(c, vec3(1./2.4)) - 0.055, step(0.0031308, c)); }
    void main(){
      vec2 p = (vUv - 0.5) * res; float r = length(p);
      float th = 2.0 * atan(r / (2.0 * focal));
      vec2 dir = r > 0.0 ? p / r : vec2(0.0);
      vec3 col = texture2D(tSrc, dir * tan(th) / tanXY * 0.5 + 0.5).rgb;
      // red/blue light wash coming through the front glass
      vec3 tint = mix(vec3(1.0), policeCol * 2.1 + 0.12, policeAmt);
      col = col * tint * (1.0 - policeDim) + policeCol * policeAmt * 0.015;
      // flashlight glare (bloom + anamorphic streak)
      vec2 d = p - glarePos;
      float g = exp(-dot(d, d) / (2.0 * 70.0 * 70.0)) * 1.4 + exp(-length(d) / 210.0) * 0.55
              + exp(-abs(d.y) / 7.0) * exp(-abs(d.x) / 420.0) * 0.5;
      col += glareAmt * g * vec3(1.0, 0.98, 0.94);
      col += flash;
      // heavy vignette for the freeze frame
      float v = smoothstep(0.35, 1.05, length(p / res * vec2(1.25, 1.0)) * 1.55);
      col *= 1.0 - vign * v;
      gl_FragColor = vec4(toSRGB(col), 1.0);
    }`,
  depthTest: false, depthWrite: false,
});
const quadScene = new THREE.Scene(), quadCam = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);
quadScene.add(new THREE.Mesh(new THREE.PlaneGeometry(2, 2), lens));
export function setFocal(f) {
  const thc = 2 * Math.atan(R_C / (2 * f));
  const ty = (H / 2) / R_C * Math.tan(thc), tx = ty * W / H;
  lens.uniforms.focal.value = f; lens.uniforms.tanXY.value.set(tx, ty);
  camera.fov = 2 * Math.atan(ty) * 180 / Math.PI; camera.updateProjectionMatrix();
}
// project a world point to lens screen coords (px from centre, +y up); returns null if behind
export function projectLens(v) {
  const pc = v.clone().applyMatrix4(camera.matrixWorldInverse);
  if (pc.z > -0.01) return null;
  const x = pc.x, y = pc.y, zf = -pc.z, rr_ = Math.hypot(x, y);
  const th = Math.atan2(rr_, zf), rpx = 2 * lens.uniforms.focal.value * Math.tan(th / 2);
  return rr_ > 0 ? new THREE.Vector2(x / rr_ * rpx, y / rr_ * rpx) : new THREE.Vector2(0, 0);
}
export function renderFrame() {
  renderer.setRenderTarget(rt); effect.render(scene, camera);
  renderer.setRenderTarget(null); renderer.render(quadScene, quadCam);
}
