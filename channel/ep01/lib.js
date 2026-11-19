// Shared engine: renderer, post-processing, helpers, materials, people.
import * as THREE from 'three';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { ShaderPass } from 'three/addons/postprocessing/ShaderPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';
import { FXAAShader } from 'three/addons/shaders/FXAAShader.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';

export { THREE, RoundedBoxGeometry };
export const W = 1280, H = 720;

// ---------- math / random ----------
let seed = 1234;
export const reseed = (s) => { seed = s; };
export const rnd = () => { seed = (seed * 16807) % 2147483647; return (seed - 1) / 2147483646; };
export const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
export const smooth = (a, b, x) => { const t = clamp((x - a) / (b - a)); return t * t * (3 - 2 * t); };
export const lerp = (a, b, t) => a + (b - a) * t;
export const v3 = (x, y, z) => new THREE.Vector3(x, y, z);
export const easeOutBack = (x) => { const c1 = 1.7, c3 = c1 + 1; return 1 + c3 * Math.pow(x - 1, 3) + c1 * Math.pow(x - 1, 2); };
export const vlerp = (a, b, t) => new THREE.Vector3(lerp(a.x, b.x, t), lerp(a.y, b.y, t), lerp(a.z, b.z, t));

// ---------- materials ----------
export const std = (color, o = {}) => new THREE.MeshStandardMaterial({ color, roughness: 0.6, metalness: 0, ...o });
export const glow = (r, g, b, o = {}) => new THREE.MeshBasicMaterial({ color: new THREE.Color(r, g, b), ...o });
export const mesh = (geo, mat, cast = true, recv = true) => { const m = new THREE.Mesh(geo, mat); m.castShadow = cast; m.receiveShadow = recv; return m; };
export function canvasTex(w, h, draw, opts = {}) {
  const c = document.createElement('canvas'); c.width = w; c.height = h;
  const g = c.getContext('2d'); draw(g, w, h);
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8;
  if (opts.repeat) { t.wrapS = t.wrapT = THREE.RepeatWrapping; }
  t.userData.canvas = c; t.userData.ctx = g;
  return t;
}
export function redraw(tex, draw) { const c = tex.userData.canvas, g = tex.userData.ctx; g.clearRect(0, 0, c.width, c.height); draw(g, c.width, c.height); tex.needsUpdate = true; }
export function roundRect(g, x, y, w, h, r) { g.beginPath(); g.moveTo(x + r, y); g.arcTo(x + w, y, x + w, y + h, r); g.arcTo(x + w, y + h, x, y + h, r); g.arcTo(x, y + h, x, y, r); g.arcTo(x, y, x + w, y, r); g.closePath(); }

// ---------- renderer & post ----------
export function createEngine(stage) {
  const renderer = new THREE.WebGLRenderer({ antialias: false, preserveDrawingBuffer: true });
  renderer.setSize(W, H); renderer.setPixelRatio(1);
  renderer.toneMapping = THREE.ACESFilmicToneMapping; renderer.toneMappingExposure = 1.05;
  renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  stage.prepend(renderer.domElement);
  const scene = new THREE.Scene();
  const pmrem = new THREE.PMREMGenerator(renderer);
  scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;
  scene.environmentIntensity = 0.35;
  const camera = new THREE.PerspectiveCamera(40, W / H, 0.1, 2000);
  const rt = new THREE.WebGLRenderTarget(W, H, { type: THREE.HalfFloatType });
  const composer = new EffectComposer(renderer, rt);
  composer.addPass(new RenderPass(scene, camera));
  const bloom = new UnrealBloomPass(new THREE.Vector2(W, H), 0.55, 0.6, 0.92); composer.addPass(bloom);
  const radial = new ShaderPass({
    uniforms: { tDiffuse: { value: null }, strength: { value: 0 }, center: { value: new THREE.Vector2(0.5, 0.5) } },
    vertexShader: `varying vec2 vUv; void main(){ vUv=uv; gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0);} `,
    fragmentShader: `uniform sampler2D tDiffuse; uniform float strength; uniform vec2 center; varying vec2 vUv;
      void main(){ vec4 acc=vec4(0.); vec2 d=vUv-center; for(int i=0;i<16;i++){ float s=1.0-strength*float(i)/15.0; acc+=texture2D(tDiffuse, center+d*s);} gl_FragColor=acc/16.0; }`
  });
  radial.enabled = false; composer.addPass(radial);
  composer.addPass(new OutputPass());
  const fxaa = new ShaderPass(FXAAShader); fxaa.uniforms.resolution.value.set(1 / W, 1 / H); composer.addPass(fxaa);
  const grade = new ShaderPass({
    uniforms: { tDiffuse: { value: null }, time: { value: 0 }, flash: { value: 0 }, flashColor: { value: new THREE.Color(1, 0.97, 0.92) },
      aberr: { value: 0.0012 }, vig: { value: 0.4 }, sepia: { value: 0 }, sat: { value: 1.12 }, fade: { value: 0 } },
    vertexShader: `varying vec2 vUv; void main(){ vUv=uv; gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0);} `,
    fragmentShader: `uniform sampler2D tDiffuse; uniform float time, flash, aberr, vig, sepia, sat, fade; uniform vec3 flashColor; varying vec2 vUv;
      void main(){ vec2 uv=vUv; vec2 d=uv-0.5;
        vec3 c; c.r=texture2D(tDiffuse, uv-d*aberr).r; c.g=texture2D(tDiffuse, uv).g; c.b=texture2D(tDiffuse, uv+d*aberr).b;
        float l=dot(c,vec3(0.299,0.587,0.114));
        c=mix(vec3(l),c,sat); c=(c-0.5)*1.07+0.5;
        c+=vec3(-0.022,0.004,0.035)*(1.0-l)*(1.0-l) + vec3(0.03,0.012,-0.022)*l*l;
        vec3 sp=vec3(dot(c,vec3(0.393,0.769,0.189)),dot(c,vec3(0.349,0.686,0.168)),dot(c,vec3(0.272,0.534,0.131)));
        c=mix(c, sp*vec3(1.02,0.97,0.88), sepia);
        float v=smoothstep(0.9,0.28,length(d*vec2(1.0,0.85))); c*=mix(1.0-vig-sepia*0.25,1.0,v);
        float g=fract(sin(dot(uv*vec2(1280.0,720.0)+fract(time)*731.0,vec2(12.9898,78.233)))*43758.5453); c+=(g-0.5)*(0.028+sepia*0.04);
        c=mix(c,flashColor,flash);
        c*=1.0-fade;
        gl_FragColor=vec4(clamp(c,0.0,1.0),1.0); }`
  });
  composer.addPass(grade);
  return { renderer, scene, camera, composer, bloom, radial, grade };
}

// ---------- sky ----------
export function makeSky() {
  const mat = new THREE.ShaderMaterial({
    side: THREE.BackSide, depthWrite: false, fog: false,
    uniforms: { sunDir: { value: v3(0.12, 0.1, -1).normalize() }, time: { value: 0 }, mode: { value: 0 }, clouds: { value: 0.9 } },
    vertexShader: `varying vec3 vDir; void main(){ vDir = position; gl_Position = projectionMatrix*modelViewMatrix*vec4(position,1.0);} `,
    fragmentShader: `varying vec3 vDir; uniform vec3 sunDir; uniform float time, mode, clouds;
    float hash(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}
    float noise(vec2 p){vec2 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);return mix(mix(hash(i),hash(i+vec2(1,0)),f.x),mix(hash(i+vec2(0,1)),hash(i+vec2(1,1)),f.x),f.y);}
    float fbm(vec2 p){float v=0.,a=.5;for(int i=0;i<6;i++){v+=a*noise(p);p*=2.03;a*=.5;}return v;}
    void main(){
      vec3 d=normalize(vDir); float h=d.y;
      // mode 0 = dusk, 1 = day, 2 = night
      vec3 hz0=vec3(1.35,0.55,0.20), lo0=vec3(1.0,0.30,0.22), mi0=vec3(0.42,0.10,0.34), tp0=vec3(0.05,0.04,0.16);
      vec3 hz1=vec3(0.85,0.78,0.7), lo1=vec3(0.55,0.66,0.85), mi1=vec3(0.28,0.47,0.85), tp1=vec3(0.1,0.25,0.65);
      vec3 hz2=vec3(0.25,0.12,0.30), lo2=vec3(0.12,0.08,0.22), mi2=vec3(0.05,0.04,0.14), tp2=vec3(0.01,0.01,0.05);
      float m1=clamp(mode,0.,1.), m2=clamp(mode-1.,0.,1.);
      vec3 hz=mix(mix(hz0,hz1,m1),hz2,m2), lo=mix(mix(lo0,lo1,m1),lo2,m2), mi=mix(mix(mi0,mi1,m1),mi2,m2), tp=mix(mix(tp0,tp1,m1),tp2,m2);
      vec3 c=mix(hz,lo,smoothstep(0.0,0.07,h)); c=mix(c,mi,smoothstep(0.07,0.32,h)); c=mix(c,tp,smoothstep(0.32,0.85,h));
      float sd=max(dot(d,sunDir),0.);
      vec3 sunCol=mix(vec3(1.2,0.55,0.25),vec3(1.0,0.9,0.7),m1)*(1.0-m2);
      c+=sunCol*pow(sd,6.)*0.6 + sunCol*2.5*pow(sd,400.)*3.0;
      vec2 uv=d.xz/(max(h,0.0)+0.12);
      float cl=fbm(uv*0.9+vec2(time*0.02,0.0)); float cl2=fbm(uv*2.3-vec2(time*0.04,0.0));
      cl=smoothstep(0.42,0.78,cl*0.75+cl2*0.35)*smoothstep(-0.01,0.12,h)*clouds;
      vec3 cd=mix(mix(vec3(0.22,0.07,0.16),vec3(0.75,0.8,0.9),m1),vec3(0.06,0.05,0.1),m2);
      vec3 cL=mix(mix(vec3(1.5,0.62,0.32),vec3(1.4,1.4,1.45),m1),vec3(0.25,0.2,0.35),m2);
      vec3 cloudCol=mix(cd, cL, clamp(pow(sd,1.5)+fbm(uv*3.0)*0.35+m1*0.4,0.,1.));
      c=mix(c,cloudCol,cl*0.9);
      if(m2>0.5){ float st=step(0.997,hash(floor(d.xz*400.0/(h+0.2)))); c+=vec3(st)*smoothstep(0.1,0.4,h); }
      gl_FragColor=vec4(c,1.0);
    }`
  });
  return new THREE.Mesh(new THREE.SphereGeometry(1500, 48, 24), mat);
}

// ---------- soft sprite textures ----------
export function softTex(strength = 0.35) {
  return canvasTex(128, 128, (g) => {
    for (let i = 0; i < 26; i++) {
      const x = 40 + rnd() * 48, y = 40 + rnd() * 48, r = 18 + rnd() * 30;
      const gr = g.createRadialGradient(x, y, 0, x, y, r);
      gr.addColorStop(0, `rgba(255,255,255,${strength})`); gr.addColorStop(1, 'rgba(255,255,255,0)');
      g.fillStyle = gr; g.fillRect(0, 0, 128, 128);
    }
  });
}

// ---------- people ----------
const boltShape = (() => { const s = new THREE.Shape(); s.moveTo(0.05, 0.28); s.lineTo(-0.16, -0.02); s.lineTo(-0.01, -0.02); s.lineTo(-0.08, -0.3); s.lineTo(0.16, 0.04); s.lineTo(0.01, 0.04); s.closePath(); return s; })();

export function makePerson(c) {
  // c: { skin, shirt, pants, shoe, hair, hairStyle, emblem, band, vest, coat, glasses, dress, cape, gold, scale }
  const p = { root: new THREE.Group(), cfg: c };
  const skin = std(c.skin, { roughness: 0.55 });
  const shirt = c.gold ? std(0xe8b23a, { roughness: 0.25, metalness: 0.85 }) : std(c.shirt, { roughness: 0.8 });
  const pants = c.gold ? std(0xd9a02b, { roughness: 0.3, metalness: 0.8 }) : std(c.pants, { roughness: 0.85 });
  const shoe = std(c.shoe ?? 0x222222, { roughness: 0.6 }), hair = std(c.hair ?? 0x111111, { roughness: 0.5 });
  p.mats = { skin, shirt, pants };
  p.hips = new THREE.Group(); p.hips.position.y = 1.35; p.root.add(p.hips);
  p.torso = new THREE.Group(); p.hips.add(p.torso);
  const chest = mesh(new THREE.CapsuleGeometry(0.52, 0.55, 10, 24), shirt); chest.scale.set(1.15, 1, 0.8); chest.position.y = 0.55; p.torso.add(chest);
  if (c.emblem) {
    p.emblem = mesh(new THREE.ExtrudeGeometry(boltShape, { depth: 0.04, bevelEnabled: true, bevelSize: 0.01, bevelThickness: 0.01 }), std(0xffffff, { roughness: 0.4 }));
    p.emblem.position.set(0, 0.62, 0.42); p.torso.add(p.emblem);
  }
  if (c.vest) {
    p.vest = new THREE.Group(); p.torso.add(p.vest);
    const vm = std(0x6d7178, { roughness: 0.7, metalness: 0.2 });
    for (const sx of [-1, 1]) {
      const half = mesh(new THREE.CapsuleGeometry(0.4, 0.5, 8, 16, ), vm); half.scale.set(0.75, 1, 0.9); half.position.set(sx * 0.36, 0.55, 0.02); p.vest.add(half);
    }
    const badge = mesh(new THREE.BoxGeometry(0.22, 0.13, 0.03), std(0x9aa0a8, { metalness: 0.9, roughness: 0.3 })); badge.position.set(0.33, 0.78, 0.43); p.vest.add(badge);
    const stripe = mesh(new THREE.BoxGeometry(1.2, 0.07, 0.86), glow(1.6, 1.4, 0.4)); stripe.position.set(0, 0.42, 0); p.vest.add(stripe);
  }
  if (c.coat) {
    const cm = std(0xf2f4f7, { roughness: 0.8 });
    const coat = mesh(new THREE.CylinderGeometry(0.62, 0.7, 1.1, 20, 1, true), cm); coat.position.y = 0.0; p.torso.add(coat);
    coat.material.side = THREE.DoubleSide;
    const lap = mesh(new THREE.CapsuleGeometry(0.53, 0.55, 10, 24), cm); lap.scale.set(1.17, 1.01, 0.82); lap.position.y = 0.55; p.torso.add(lap);
    const tie = mesh(new THREE.BoxGeometry(0.12, 0.5, 0.04), std(0x2e6fd8)); tie.position.set(0, 0.6, 0.44); p.torso.add(tie);
  }
  if (c.dress) {
    const dr = mesh(new THREE.ConeGeometry(0.75, 1.0, 24, 1, true), std(c.dress, { roughness: 0.8, side: THREE.DoubleSide }));
    dr.position.y = -0.35; p.torso.add(dr);
  }
  if (c.cape) {
    p.cape = mesh(new THREE.PlaneGeometry(1.2, 1.9, 6, 10), std(c.cape, { roughness: 0.7, side: THREE.DoubleSide }));
    p.cape.position.set(0, 0.2, -0.45); p.torso.add(p.cape);
    const pos = p.cape.geometry.attributes.position; p.capeBase = pos.array.slice();
  }
  const neck = mesh(new THREE.CylinderGeometry(0.16, 0.18, 0.25, 14), skin); neck.position.y = 1.15; p.torso.add(neck);
  p.head = new THREE.Group(); p.head.position.y = 1.72; p.torso.add(p.head);
  const skull = mesh(new THREE.SphereGeometry(0.56, 40, 30), skin); skull.scale.set(1, 1.05, 0.98); p.head.add(skull);
  const hs = c.hairStyle || 'short';
  if (hs !== 'bald' && hs !== 'helmet') {
    const cap = mesh(new THREE.SphereGeometry(0.585, 40, 20, 0, Math.PI * 2, 0, Math.PI * 0.5), hair); cap.position.y = 0.05; cap.rotation.x = -0.25; p.head.add(cap);
  }
  if (hs === 'spiky') {
    const spikes = [[0, 0.62, -0.05, -0.2, 0], [0.28, 0.55, -0.1, -0.3, -0.5], [-0.28, 0.55, -0.1, -0.3, 0.5], [0.15, 0.5, 0.25, 0.5, -0.2],
      [-0.15, 0.5, 0.25, 0.5, 0.2], [0, 0.45, -0.4, -0.9, 0], [0.4, 0.35, 0.05, 0, -1.0], [-0.4, 0.35, 0.05, 0, 1.0], [0.0, 0.55, 0.15, 0.25, 0]];
    for (const [x, y, z, rx, rz] of spikes) { const s = mesh(new THREE.ConeGeometry(0.16, 0.58, 10), hair); s.position.set(x, y, z); s.rotation.set(rx, 0, rz); p.head.add(s); }
  } else if (hs === 'long') {
    const back = mesh(new THREE.CapsuleGeometry(0.5, 0.7, 8, 20), hair); back.scale.set(1.15, 1, 0.55); back.position.set(0, -0.25, -0.28); p.head.add(back);
    const fr = mesh(new THREE.SphereGeometry(0.6, 30, 16, 0, Math.PI * 2, 0, Math.PI * 0.42), hair); fr.position.set(0, 0.06, 0.04); fr.rotation.x = 0.12; p.head.add(fr);
  } else if (hs === 'bun') {
    const bun = mesh(new THREE.SphereGeometry(0.25, 20, 14), hair); bun.position.set(0, 0.55, -0.3); p.head.add(bun);
  } else if (hs === 'pigtails') {
    for (const sx of [-1, 1]) { const pt = mesh(new THREE.CapsuleGeometry(0.14, 0.35, 6, 12), hair); pt.position.set(sx * 0.62, -0.05, -0.1); pt.rotation.z = sx * 0.4; p.head.add(pt);
      const tie = mesh(new THREE.SphereGeometry(0.08, 10, 8), std(0xff4fa3)); tie.position.set(sx * 0.55, 0.15, -0.1); p.head.add(tie); }
  } else if (hs === 'helmet') {
    const hm = mesh(new THREE.SphereGeometry(0.6, 40, 24, 0, Math.PI * 2, 0, Math.PI * 0.6), std(0xe8b23a, { metalness: 0.9, roughness: 0.2 })); hm.position.y = 0.04; p.head.add(hm);
    const crest = mesh(new THREE.ConeGeometry(0.12, 0.6, 12), std(0xfff2c0, { metalness: 0.9, roughness: 0.2 })); crest.position.set(0, 0.7, 0.05); crest.rotation.x = -0.3; p.head.add(crest);
    const visor = mesh(new THREE.TorusGeometry(0.5, 0.06, 8, 30, Math.PI), std(0xe8b23a, { metalness: 0.9, roughness: 0.2 })); visor.rotation.set(0, 0, 0); visor.position.set(0, 0.16, 0.12); visor.scale.set(1, 0.4, 1); p.head.add(visor);
  } else if (hs === 'cap') {
    const brim = mesh(new THREE.CylinderGeometry(0.4, 0.4, 0.04, 20, 1, false, 0, Math.PI), std(c.capColor ?? 0x1d4ed8)); brim.position.set(0, 0.32, 0.38); brim.rotation.set(0.15, Math.PI / 2, 0); p.head.add(brim);
  }
  const eyeM = new THREE.MeshStandardMaterial({ color: 0x0c0710, roughness: 0.15 });
  const hiM = new THREE.MeshBasicMaterial({ color: 0xffffff });
  p.eyes = []; p.brows = [];
  for (const sx of [-1, 1]) {
    const e = mesh(new THREE.CapsuleGeometry(0.068, 0.12, 6, 14), eyeM, false); e.position.set(sx * 0.2, 0.02, 0.515); p.head.add(e); p.eyes.push(e);
    const hi = new THREE.Mesh(new THREE.SphereGeometry(0.024, 10, 8), hiM); hi.position.set(sx * 0.2 + 0.025, 0.075, 0.585); p.head.add(hi);
    const brow = mesh(new THREE.CapsuleGeometry(0.03, 0.15, 4, 8), hair, false); brow.rotation.z = Math.PI / 2 + sx * -0.3; brow.position.set(sx * 0.21, 0.21, 0.53); p.head.add(brow); p.brows.push(brow);
  }
  if (c.glasses) {
    const gm = std(0x111111, { metalness: 0.5, roughness: 0.3 });
    for (const sx of [-1, 1]) { const r = mesh(new THREE.TorusGeometry(0.12, 0.018, 8, 20), gm, false); r.position.set(sx * 0.2, 0.03, 0.56); p.head.add(r); }
    const br = mesh(new THREE.BoxGeometry(0.16, 0.02, 0.02), gm, false); br.position.set(0, 0.05, 0.57); p.head.add(br);
  }
  p.mouthSmile = mesh(new THREE.TorusGeometry(0.075, 0.016, 8, 16, Math.PI), std(0x4a1d1a), false);
  p.mouthSmile.position.set(0.02, -0.2, 0.53); p.mouthSmile.rotation.z = Math.PI; p.head.add(p.mouthSmile);
  p.mouthOpen = mesh(new THREE.SphereGeometry(0.1, 16, 12), std(0x3a0e12), false); p.mouthOpen.scale.set(1, 0.7, 0.4); p.mouthOpen.position.set(0.02, -0.22, 0.52); p.mouthOpen.visible = false; p.head.add(p.mouthOpen);
  for (const sx of [-1, 1]) { const ear = mesh(new THREE.SphereGeometry(0.11, 14, 10), skin); ear.position.set(sx * 0.55, 0, 0); ear.scale.set(0.6, 1, 0.8); p.head.add(ear); }
  const arm = (sx) => {
    const shoulder = new THREE.Group(); shoulder.position.set(sx * 0.68, 0.95, 0); p.torso.add(shoulder);
    const sleeve = mesh(new THREE.CapsuleGeometry(0.2, 0.25, 8, 16), c.coat ? std(0xf2f4f7, { roughness: 0.8 }) : shirt); sleeve.position.y = -0.2; shoulder.add(sleeve);
    const upper = mesh(new THREE.CapsuleGeometry(0.15, 0.32, 8, 16), c.coat || c.gold ? sleeve.material : skin); upper.position.y = -0.38; shoulder.add(upper);
    const elbow = new THREE.Group(); elbow.position.y = -0.62; shoulder.add(elbow);
    const fore = mesh(new THREE.CapsuleGeometry(0.14, 0.35, 8, 16), c.gold ? sleeve.material : skin); fore.position.y = -0.25; elbow.add(fore);
    if (c.band) { const band = mesh(new THREE.CylinderGeometry(0.16, 0.16, 0.1, 16), std(0x111111)); band.position.y = -0.42; elbow.add(band); }
    const fist = mesh(new THREE.SphereGeometry(0.2, 20, 14), c.gold ? std(0xfff2c0, { metalness: 0.8, roughness: 0.25 }) : skin); fist.scale.set(1, 0.9, 1.1); fist.position.y = -0.6; elbow.add(fist);
    return { shoulder, elbow, fist };
  };
  p.armR = arm(-1); p.armL = arm(1);
  const leg = (sx) => {
    const hip = new THREE.Group(); hip.position.set(sx * 0.26, 0, 0); p.hips.add(hip);
    const thigh = mesh(new THREE.CapsuleGeometry(0.2, 0.4, 8, 16), pants); thigh.position.y = -0.35; hip.add(thigh);
    const knee = new THREE.Group(); knee.position.y = -0.66; hip.add(knee);
    const shin = mesh(new THREE.CapsuleGeometry(0.18, 0.35, 8, 16), pants); shin.position.y = -0.25; knee.add(shin);
    const foot = mesh(new THREE.BoxGeometry(0.3, 0.2, 0.55), shoe); foot.position.set(0, -0.58, 0.1); knee.add(foot);
    return { hip, knee };
  };
  p.legR = leg(-1); p.legL = leg(1);
  if (c.cane) {
    p.cane = mesh(new THREE.CylinderGeometry(0.035, 0.035, 1.2, 8), std(0x5a3a22)); p.cane.position.y = -0.95; p.armL.elbow.add(p.cane);
  }
  if (c.bag) {
    p.bag = new THREE.Group();
    const b = mesh(new THREE.BoxGeometry(0.55, 0.6, 0.35), std(0xc9a46a, { roughness: 0.95 })); p.bag.add(b);
    for (let i = 0; i < 3; i++) { const o = mesh(new THREE.SphereGeometry(0.11, 12, 10), std(0xff8a1f, { roughness: 0.5 })); o.position.set(-0.15 + i * 0.15, 0.33, (i % 2) * 0.06); p.bag.add(o); }
    const bread = mesh(new THREE.CapsuleGeometry(0.07, 0.35, 4, 10), std(0xd8a35a)); bread.position.set(0.15, 0.4, -0.08); bread.rotation.z = 0.3; p.bag.add(bread);
    p.bag.position.set(0, -0.75, 0.15); p.armL.elbow.add(p.bag);
  }
  if (c.phone) {
    p.phone = mesh(new RoundedBoxGeometry(0.22, 0.42, 0.03, 3, 0.03), std(0x111111, { roughness: 0.3, metalness: 0.5 }));
    const scr = new THREE.Mesh(new THREE.PlaneGeometry(0.19, 0.38), glow(0.9, 1.0, 1.2)); scr.position.z = 0.017; p.phone.add(scr);
    p.phone.position.set(0, -0.68, 0.1); p.phone.visible = false; p.armR.elbow.add(p.phone);
  }
  p.root.scale.setScalar(c.scale ?? 1);
  return p;
}

export function resetPose(p) {
  p.hips.position.set(0, 1.35, 0); p.hips.rotation.set(0, 0, 0);
  p.torso.rotation.set(0, 0, 0); p.head.rotation.set(0, 0, 0);
  for (const a of [p.armR, p.armL]) { a.shoulder.rotation.set(0, 0, 0); a.elbow.rotation.set(0, 0, 0); }
  p.armR.shoulder.rotation.z = -0.12; p.armL.shoulder.rotation.z = 0.12;
  p.armR.elbow.rotation.x = -0.25; p.armL.elbow.rotation.x = -0.25;
  for (const l of [p.legR, p.legL]) { l.hip.rotation.set(0, 0, 0); l.knee.rotation.set(0, 0, 0); }
  for (const e of p.eyes) e.scale.set(1, 1, 1);
  for (const b of p.brows) b.position.y = 0.21;
  p.brows[0].rotation.z = Math.PI / 2 + 0.3; p.brows[1].rotation.z = Math.PI / 2 - 0.3;
  mouth(p, 'smile', 0);
  if (p.phone) p.phone.visible = false;
}
export function mouth(p, kind, amt = 1) {
  p.mouthOpen.visible = kind === 'open' || kind === 'o';
  p.mouthSmile.visible = !p.mouthOpen.visible;
  if (kind === 'smile') { p.mouthSmile.rotation.z = Math.PI; p.mouthSmile.scale.set(1 + 0.25 * amt, 1 + 0.4 * amt, 1); }
  if (kind === 'flat') { p.mouthSmile.rotation.z = Math.PI; p.mouthSmile.scale.set(1, 0.15, 1); }
  if (kind === 'frown') { p.mouthSmile.rotation.z = 0; p.mouthSmile.position.y = -0.24; p.mouthSmile.scale.set(1, 0.6, 1); return; }
  if (kind === 'open') p.mouthOpen.scale.set(1.1, 0.5 + 0.6 * amt, 0.4);
  if (kind === 'o') p.mouthOpen.scale.set(0.6, 0.8, 0.4);
  p.mouthSmile.position.y = -0.2;
}
export function blink(p, t, offset = 0) {
  const ph = (t + offset) % 3.7;
  const s = ph < 0.12 ? Math.abs(ph - 0.06) / 0.06 : 1;
  for (const e of p.eyes) e.scale.y = Math.min(e.scale.y, Math.max(0.08, s));
}
export function gait(p, ph, amp, run) {
  const s = Math.sin(ph), s2 = Math.sin(ph + Math.PI);
  p.legR.hip.rotation.set(-s * amp, 0, 0); p.legL.hip.rotation.set(-s2 * amp, 0, 0);
  p.legR.knee.rotation.x = Math.max(0, Math.sin(ph - 1.2)) * amp * 1.6; p.legL.knee.rotation.x = Math.max(0, Math.sin(ph + Math.PI - 1.2)) * amp * 1.6;
  p.armR.shoulder.rotation.set(s * amp * 0.9, 0, -0.12); p.armL.shoulder.rotation.set(s2 * amp * 0.9, 0, 0.12);
  p.armR.elbow.rotation.x = -(run ? 1.4 : 0.35); p.armL.elbow.rotation.x = -(run ? 1.4 : 0.35);
  p.hips.position.y = 1.35 + Math.abs(Math.cos(ph)) * (run ? 0.12 : 0.05) - (run ? 0.05 : 0);
  p.torso.rotation.x = run ? 0.22 : 0.03;
}
export function idle(p, t, off = 0) {
  p.hips.position.y = 1.35 + Math.sin((t + off) * 2.2) * 0.012;
  p.torso.rotation.x = Math.sin((t + off) * 1.1) * 0.015;
  p.head.rotation.y += Math.sin((t + off) * 0.7) * 0.06;
}
export function wave(p, t, side = 'R') {
  const a = side === 'R' ? p.armR : p.armL, sgn = side === 'R' ? -1 : 1;
  a.shoulder.rotation.set(-0.2, 0, sgn * (2.5 + Math.sin(t * 9) * 0.25)); a.elbow.rotation.set(0, 0, 0); a.elbow.rotation.x = -0.4;
}
export function point(p, side = 'R', up = 0) {
  const a = side === 'R' ? p.armR : p.armL;
  a.shoulder.rotation.set(-1.45 - up, 0, side === 'R' ? 0.15 : -0.15); a.elbow.rotation.x = -0.1;
}
export function laugh(p, t, amt = 1) {
  p.torso.rotation.x = -0.12 * amt + Math.sin(t * 18) * 0.04 * amt;
  p.head.rotation.x = -0.25 * amt + Math.sin(t * 18) * 0.06 * amt;
  p.hips.position.y += Math.abs(Math.sin(t * 18)) * 0.03 * amt;
  mouth(p, 'open', 0.6 + 0.4 * Math.abs(Math.sin(t * 18)));
  for (const e of p.eyes) e.scale.y = 0.35;
  p.armL.shoulder.rotation.set(-0.5, 0, 0.3); p.armL.elbow.rotation.x = -1.6; // hand on belly
}
export function capeWave(p, t, strength = 1) {
  if (!p.cape) return;
  const pos = p.cape.geometry.attributes.position, b = p.capeBase;
  for (let i = 0; i < pos.count; i++) {
    const x = b[i * 3], y = b[i * 3 + 1];
    const k = (0.95 - y) / 1.9;
    pos.array[i * 3 + 2] = b[i * 3 + 2] - k * k * 0.5 * strength + Math.sin(t * 6 + x * 3 + y * 2) * 0.08 * k * strength;
  }
  pos.needsUpdate = true; p.cape.geometry.computeVertexNormals();
}
