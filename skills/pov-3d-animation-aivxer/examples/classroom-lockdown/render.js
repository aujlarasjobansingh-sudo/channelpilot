// Usage: node render.js [--still t1,t2,...] [--out file.mp4] [--seconds 4] [--nohud]
// Serves this folder, renders the three.js scene frame-by-frame in headless Chromium, encodes with ffmpeg.
const { chromium } = require('playwright');
const http = require('http');
const fs = require('fs');
const path = require('path');
const { execFileSync } = require('child_process');

const args = process.argv.slice(2);
const opt = (k, d) => { const i = args.indexOf(k); return i >= 0 ? args[i + 1] : d; };
const LAND = opt('--aspect', '9:16') === '16:9';   // --aspect 16:9 renders 1280x720
const VW = LAND ? 1280 : 720, VH = LAND ? 720 : 1280;
const ROOT = __dirname;
const FPS = 30;
const SECONDS = parseFloat(opt('--seconds', '4'));
const OUT = opt('--out', path.join(ROOT, 'out', 'preview_4s.mp4'));
const STILLS = opt('--still', null);
const HUD = !args.includes('--nohud');

const types = { '.html': 'text/html', '.js': 'text/javascript', '.woff2': 'font/woff2' };
const server = http.createServer((req, res) => {
  const p = path.join(ROOT, decodeURIComponent(req.url.split('?')[0]));
  if (!p.startsWith(ROOT) || !fs.existsSync(p) || fs.statSync(p).isDirectory()) { res.writeHead(404); return res.end(); }
  res.writeHead(200, { 'Content-Type': types[path.extname(p)] || 'application/octet-stream' });
  fs.createReadStream(p).pipe(res);
});

(async () => {
  await new Promise(r => server.listen(0, r));
  const port = server.address().port;
  const browser = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  const page = await browser.newPage({ viewport: { width: VW, height: VH }, deviceScaleFactor: 1 });
  page.on('console', m => console.log('[page]', m.text()));
  page.on('pageerror', e => console.error('[pageerror]', e.message));
  await page.goto(`http://127.0.0.1:${port}/index.html${LAND ? '?aspect=16:9' : ''}`);
  await page.waitForFunction(() => window.sceneReady, null, { timeout: 60000 });
  await page.evaluate(() => window.sceneReady);
  await page.evaluate(h => window.setHud(h), HUD);
  const stage = await page.$('#stage');

  if (STILLS) {
    fs.mkdirSync(path.join(ROOT, 'out'), { recursive: true });
    for (const t of STILLS.split(',').map(Number)) {
      await page.evaluate(t => window.renderAt(t), t);
      const f = path.join(ROOT, 'out', `still_${t}.png`);
      await stage.screenshot({ path: f });
      console.log('wrote', f);
    }
  } else {
    const dir = path.join(ROOT, 'out', 'frames');
    fs.rmSync(dir, { recursive: true, force: true }); fs.mkdirSync(dir, { recursive: true });
    const N = Math.round(SECONDS * FPS);
    for (let i = 0; i < N; i++) {
      await page.evaluate(t => window.renderAt(t), i / FPS);
      await stage.screenshot({ path: path.join(dir, `f_${String(i).padStart(4, '0')}.png`) });
      if (i % 30 === 0) console.log(`frame ${i}/${N}`);
    }
    execFileSync('ffmpeg', ['-y', '-v', 'error', '-framerate', String(FPS), '-i', path.join(dir, 'f_%04d.png'),
      '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '16', '-preset', 'slow', '-movflags', '+faststart', OUT]);
    console.log('wrote', OUT);
  }
  await browser.close(); server.close();
})().catch(e => { console.error(e); process.exit(1); });
