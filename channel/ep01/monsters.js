// Original monster designs for EP01. All face +z by default.
import { THREE, std, glow, mesh, v3, rnd } from './lib.js';

// ECLIPSE: Gorrak (giant purple, three eyes, horns). Height ~ 40 at scale 1.
export function makeGorrak() {
  const g = new THREE.Group();
  const mSkin = std(0x4e2390, { roughness: 0.42, metalness: 0.05 });
  const mBellyM = std(0x8556bb, { roughness: 0.55 });
  const mDark = std(0x1a0b29, { roughness: 0.4 });
  const hornM = std(0xf1dfc0, { roughness: 0.35 });
  const body = mesh(new THREE.SphereGeometry(11, 48, 32), mSkin); body.scale.set(1.1, 1.25, 0.9); body.position.y = 16; g.add(body);
  const belly = mesh(new THREE.SphereGeometry(8, 48, 32), mBellyM); belly.scale.set(1, 1.2, 0.6); belly.position.set(0, 14, 6.5); g.add(belly);
  const head = new THREE.Group(); head.position.set(0, 29, 2); g.add(head);
  const hb = mesh(new THREE.SphereGeometry(7, 48, 32), mSkin); hb.scale.set(1.2, 0.9, 1); head.add(hb);
  for (const sx of [-1, 1]) {
    const horn = mesh(new THREE.ConeGeometry(1.6, 9, 24), hornM); horn.position.set(sx * 5.5, 5.5, -0.5); horn.rotation.z = -sx * 0.55; head.add(horn);
    const brow = mesh(new THREE.BoxGeometry(3.4, 0.9, 1.2), mDark); brow.position.set(sx * 2.4, 3.3, 5.6); brow.rotation.z = sx * 0.35; head.add(brow);
  }
  const eyeGlow = glow(6, 5, 0.6);
  for (const ex of [-3, 0, 3]) { const e = new THREE.Mesh(new THREE.SphereGeometry(ex === 0 ? 1.3 : 1.05, 20, 14), eyeGlow); e.position.set(ex, ex === 0 ? 2.4 : 1.4, 6.2); head.add(e); }
  const jaw = new THREE.Group(); jaw.position.set(0, -1.5, 4); head.add(jaw);
  const mouth = mesh(new THREE.SphereGeometry(4.2, 32, 20), mDark); mouth.scale.set(1.1, 0.55, 0.6); mouth.position.set(0, -1.2, 2.2); jaw.add(mouth);
  for (let i = -3; i <= 3; i++) { const tooth = mesh(new THREE.ConeGeometry(0.45, 1.5, 10), hornM); tooth.position.set(i * 1.1, -0.2, 3.9); tooth.rotation.x = Math.PI; jaw.add(tooth); }
  const mouthLight = new THREE.PointLight(0xb04cff, 0, 25, 2); mouthLight.position.set(0, -1, 5); jaw.add(mouthLight);
  const arms = [];
  for (const sx of [-1, 1]) {
    const sh = new THREE.Group(); sh.position.set(sx * 11, 21, 1); g.add(sh);
    const arm = mesh(new THREE.CapsuleGeometry(2.6, 12, 10, 24), mSkin); arm.position.y = -7; sh.add(arm);
    for (let c = -1; c <= 1; c++) { const claw = mesh(new THREE.ConeGeometry(0.7, 2.8, 12), hornM); claw.position.set(c * 1.3, -15.4, 0.5); claw.rotation.x = Math.PI; sh.add(claw); }
    sh.rotation.z = sx * 0.5; sh.rotation.x = -0.4; arms.push(sh);
  }
  for (let i = 0; i < 6; i++) { const sp = mesh(new THREE.ConeGeometry(1.4, 4.8, 12), mDark); sp.position.set(0, 27 - i * 4.4, -8.5 + i * 0.5); sp.rotation.x = -1.2; g.add(sp); }
  const api = { group: g, head, jaw, arms, mouthLight,
    animate(t, roar = 0) {
      jaw.rotation.x = 0.4 * roar + Math.sin(t * 34) * 0.03 * roar; head.rotation.x = -0.22 * roar;
      mouthLight.intensity = 300 * roar;
      arms[0].rotation.z = -0.5 - 0.55 * roar; arms[1].rotation.z = 0.5 + 0.55 * roar;
    } };
  return api;
}

// EMBER: dog-sized lava lizard. Length ~2.2.
export function makeEmber() {
  const g = new THREE.Group();
  const skin = std(0x3a2a2a, { roughness: 0.7 });
  const lava = glow(4.5, 1.4, 0.25);
  const body = mesh(new THREE.CapsuleGeometry(0.32, 0.9, 8, 16), skin); body.rotation.x = Math.PI / 2; body.position.y = 0.45; g.add(body);
  const head = new THREE.Group(); head.position.set(0, 0.55, 0.75); g.add(head);
  const hd = mesh(new THREE.SphereGeometry(0.3, 20, 14), skin); hd.scale.set(1, 0.8, 1.3); head.add(hd);
  for (const sx of [-1, 1]) { const e = new THREE.Mesh(new THREE.SphereGeometry(0.05, 10, 8), glow(6, 4, 0.5)); e.position.set(sx * 0.15, 0.1, 0.3); head.add(e); }
  const tail = [];
  for (let i = 0; i < 6; i++) { const s = mesh(new THREE.SphereGeometry(0.22 - i * 0.03, 12, 10), skin); s.position.set(0, 0.42, -0.65 - i * 0.22); g.add(s); tail.push(s); }
  for (let i = 0; i < 5; i++) { const sp = new THREE.Mesh(new THREE.ConeGeometry(0.07, 0.25, 8), lava); sp.position.set(0, 0.8, 0.4 - i * 0.25); g.add(sp); }
  const legs = [];
  for (const [x, z] of [[-0.32, 0.35], [0.32, 0.35], [-0.32, -0.35], [0.32, -0.35]]) { const l = mesh(new THREE.CapsuleGeometry(0.08, 0.3, 4, 8), skin); l.position.set(x, 0.2, z); l.rotation.z = Math.sign(x) * 0.5; g.add(l); legs.push(l); }
  const light = new THREE.PointLight(0xff6a1a, 6, 6, 2); light.position.y = 1; g.add(light);
  return { group: g, head, animate(t, walk = 0) {
    legs.forEach((l, i) => { l.rotation.x = Math.sin(t * 12 + i * Math.PI / 2) * 0.6 * walk; });
    tail.forEach((s, i) => { s.position.x = Math.sin(t * 6 - i * 0.6) * 0.08 * (i + 1); });
    head.rotation.y = Math.sin(t * 2) * 0.2; light.intensity = 6 + Math.sin(t * 13) * 1.5;
  } };
}

// STORM: armoured centipede. ~12 segments, head height when reared ~6.
export function makeStorm() {
  const g = new THREE.Group();
  const shell = std(0x1f3a4a, { roughness: 0.35, metalness: 0.35 });
  const under = std(0x2a2230, { roughness: 0.7 });
  const seam = glow(4.0, 1.6, 0.3);
  const N = 12; const segs = [];
  for (let i = 0; i < N; i++) {
    const r = 1.15 - i * 0.045;
    const s = new THREE.Group(); g.add(s);
    const b = mesh(new THREE.SphereGeometry(r, 24, 18), under); b.scale.set(1.1, 0.85, 1); s.add(b);
    const plate = mesh(new THREE.SphereGeometry(r * 1.06, 24, 12, 0, Math.PI * 2, 0, Math.PI * 0.45), shell); plate.scale.set(1.12, 0.95, 1.05); s.add(plate);
    const ring = new THREE.Mesh(new THREE.TorusGeometry(r * 0.98, 0.04, 6, 30), seam); ring.rotation.x = Math.PI / 2; ring.position.y = 0.15; s.add(ring);
    const spike = mesh(new THREE.ConeGeometry(0.18, 0.7, 10), shell); spike.position.y = r * 1.05; s.add(spike);
    const legs = [];
    for (const sx of [-1, 1]) {
      const hip = new THREE.Group(); hip.position.set(sx * r * 0.9, 0, 0); s.add(hip);
      const up = mesh(new THREE.CapsuleGeometry(0.09, 0.9, 4, 8), shell); up.position.set(sx * 0.45, 0.2, 0); up.rotation.z = sx * -1.0; hip.add(up);
      const low = mesh(new THREE.CapsuleGeometry(0.07, 1.1, 4, 8), shell); low.position.set(sx * 1.0, -0.4, 0); low.rotation.z = sx * 0.35; hip.add(low);
      legs.push(hip);
    }
    segs.push({ s, r, legs });
  }
  // head on segment 0
  const head = new THREE.Group(); segs[0].s.add(head); head.position.set(0, 0.2, 1.0);
  const hd = mesh(new THREE.SphereGeometry(1.0, 28, 20), shell); hd.scale.set(1.2, 0.8, 1.1); head.add(hd);
  const eyes = glow(1.0, 4.5, 6.0);
  for (const [x, y] of [[-0.45, 0.35], [0.45, 0.35], [-0.25, 0.55], [0.25, 0.55]]) { const e = new THREE.Mesh(new THREE.SphereGeometry(0.11, 12, 10), eyes); e.position.set(x, y, 0.95); head.add(e); }
  const jaw = new THREE.Group(); jaw.position.set(0, -0.2, 0.8); head.add(jaw);
  const mouthIn = mesh(new THREE.SphereGeometry(0.6, 20, 14), std(0x14060c)); mouthIn.scale.set(1.1, 0.6, 0.5); jaw.add(mouthIn);
  const teeth = [];
  for (let i = -3; i <= 3; i++) { const t = mesh(new THREE.ConeGeometry(0.07, 0.35, 8), std(0xf3e6cf)); t.position.set(i * 0.15, 0.15, 0.25); t.rotation.x = Math.PI; jaw.add(t); teeth.push(t); }
  const mand = [];
  for (const sx of [-1, 1]) { const m = mesh(new THREE.ConeGeometry(0.16, 1.4, 10), std(0xf3e6cf, { roughness: 0.4 })); m.position.set(sx * 0.6, -0.25, 1.1); m.rotation.set(Math.PI / 2, 0, sx * 0.5); head.add(m); mand.push(m); }
  // claw (big front scythe) for the attack shot
  const claw = new THREE.Group(); segs[1].s.add(claw); claw.position.set(1.3, 0.3, 0.3);
  const c1 = mesh(new THREE.CapsuleGeometry(0.2, 2.0, 6, 12), shell); c1.position.y = 1.0; claw.add(c1);
  const c2 = mesh(new THREE.ConeGeometry(0.25, 1.8, 12), std(0xf3e6cf, { roughness: 0.4 })); c2.position.set(0, 2.6, 0.5); c2.rotation.x = 0.9; claw.add(c2);
  const light = new THREE.PointLight(0x4fd8ff, 0, 14, 2); light.position.set(0, 0.6, 1.6); head.add(light);
  const api = { group: g, head, jaw, claw, segs, rear: 0, open: 0,
    // pose along a path: segments follow the head backwards on the ground, front `rear` segments lift up
    animate(t, { crawl = 0, rear = 0, open = 0, look = 0, clawRaise = 0 } = {}) {
      const spacing = 1.45;
      for (let i = 0; i < N; i++) {
        const sg = segs[i];
        const lift = Math.max(0, 1 - i / 5) * rear;
        const wig = Math.sin(t * 3 - i * 0.7) * 0.45 * (crawl > 0 ? 1 : 0.3);
        const z = -i * spacing * (1 - 0.35 * lift);
        sg.s.position.set(wig * (1 - lift), sg.r * 0.85 + lift * (5.5 - i * 0.9) * (i < 5 ? 1 : 0), z);
        sg.s.rotation.set(-lift * 0.9, Math.cos(t * 3 - i * 0.7) * 0.2 * (crawl > 0 ? 1 : 0.3), 0);
        sg.legs.forEach((hip, k) => { hip.rotation.x = Math.sin(t * 14 * (crawl || 0.15) + i * 0.8 + k * Math.PI) * 0.5 * (0.3 + crawl); });
      }
      head.rotation.set(0.3 * rear + look * 0.2, look, 0);
      jaw.rotation.x = 0.7 * open; teeth.forEach((tt) => { tt.position.y = 0.15 - 0.05 * open; });
      mand.forEach((m, k) => { m.rotation.z = (k ? -1 : 1) * (0.5 + 0.35 * open + Math.sin(t * 20) * 0.05 * open); });
      claw.rotation.set(-0.4 - 1.6 * clawRaise, 0, -0.3);
      light.intensity = 20 + 40 * open;
    } };
  return api;
}

// QUAKE: rock golem with lava cracks. Height ~ 18.
export function makeQuake() {
  const g = new THREE.Group();
  const rock = std(0x5d5047, { roughness: 0.95, flatShading: true });
  const lava = glow(5, 1.5, 0.2);
  const chunk = (r, x, y, z, parent = g) => { const m = mesh(new THREE.DodecahedronGeometry(r, 0), rock); m.position.set(x, y, z); m.rotation.set(rnd() * 3, rnd() * 3, rnd() * 3); parent.add(m); return m; };
  chunk(5, 0, 10, 0); chunk(4, 0, 15, 0.5); chunk(3.2, -2.5, 6, 0); chunk(3.2, 2.5, 6, 0);
  const head = new THREE.Group(); head.position.set(0, 19, 1); g.add(head); chunk(2.4, 0, 0, 0, head);
  for (const sx of [-1, 1]) { const e = new THREE.Mesh(new THREE.SphereGeometry(0.45, 12, 10), lava); e.position.set(sx * 0.9, 0.3, 2.0); head.add(e); }
  for (const sx of [-1, 1]) {
    const arm = new THREE.Group(); arm.position.set(sx * 6, 14, 0); g.add(arm);
    chunk(2.2, 0, -2, 0, arm); chunk(2.0, sx * 0.5, -5.5, 0.5, arm); chunk(2.6, sx * 0.6, -9, 1, arm);
    const legP = new THREE.Group(); legP.position.set(sx * 2.8, 4, 0); g.add(legP); chunk(2.4, 0, -1, 0, legP); chunk(2.2, 0, -3, 0, legP);
  }
  for (let i = 0; i < 14; i++) { const c = new THREE.Mesh(new THREE.BoxGeometry(0.25, 1.5 + rnd() * 2, 0.25), lava); c.position.set((rnd() - 0.5) * 7, 6 + rnd() * 10, 3.6 + rnd() * 0.6); c.rotation.z = (rnd() - 0.5) * 1.5; g.add(c); }
  const light = new THREE.PointLight(0xff5a1a, 80, 30, 2); light.position.set(0, 10, 6); g.add(light);
  return { group: g, head, animate(t) { head.rotation.y = Math.sin(t * 0.8) * 0.2; light.intensity = 80 + Math.sin(t * 7) * 15; } };
}

// EXTINCTION: a colossal shadow with many red eyes. Mostly hidden in fog.
export function makeExtinction() {
  const g = new THREE.Group();
  const dark = std(0x07050a, { roughness: 0.9 });
  const b = mesh(new THREE.SphereGeometry(30, 40, 24), dark); b.scale.set(1.4, 1.1, 0.8); b.position.y = 30; g.add(b);
  const crown = [];
  for (let i = 0; i < 9; i++) { const s = mesh(new THREE.ConeGeometry(2.5, 18, 10), dark); const a = -0.9 + i * 0.225; s.position.set(Math.sin(a) * 30, 58 + Math.cos(a) * 6, -4); s.rotation.z = -a * 0.8; g.add(s); crown.push(s); }
  const eyes = [];
  const em = glow(8, 0.4, 0.3);
  for (let i = 0; i < 11; i++) { const e = new THREE.Mesh(new THREE.SphereGeometry(1 + rnd() * 1.6, 14, 10), em); e.position.set((rnd() - 0.5) * 34, 36 + rnd() * 14, 22); g.add(e); eyes.push(e); }
  return { group: g, eyes, animate(t, open = 1) { eyes.forEach((e, i) => { e.scale.y = Math.max(0.05, open * (0.6 + 0.4 * Math.sin(t * 1.3 + i))); }); } };
}
