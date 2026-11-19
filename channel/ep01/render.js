// Usage: node render.js <fps> <startFrame> <endFrame> [outDir]   or   STILLS=12.5,40 node render.js
const { chromium } = require('playwright');
const http = require('http'), fs = require('fs'), path = require('path');
const root = path.join(__dirname, '..');
const fps = Number(process.argv[2] || 24);
const f0 = Number(process.argv[3] || 0), f1 = Number(process.argv[4] || 0);
const outDir = process.env.STILLS ? path.join(__dirname, 'stills') : path.join(__dirname, process.argv[5] || 'frames');
fs.mkdirSync(outDir, { recursive: true });
const types = { '.html': 'text/html', '.js': 'text/javascript' };
const server = http.createServer((req, res) => {
  const p = path.join(root, decodeURIComponent(req.url.split('?')[0]));
  if (!p.startsWith(root) || !fs.existsSync(p) || fs.statSync(p).isDirectory()) { res.writeHead(404); return res.end(); }
  res.writeHead(200, { 'Content-Type': types[path.extname(p)] || 'application/octet-stream' });
  fs.createReadStream(p).pipe(res);
}).listen(0, async () => {
  const browser = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  const page = await browser.newPage({ viewport: { width: 1280, height: 720 } });
  page.on('console', (m) => { if (m.type() === 'error') console.log('PAGE:', m.text()); });
  page.on('pageerror', (e) => console.log('PAGEERR:', e.message));
  await page.goto(`http://127.0.0.1:${server.address().port}/ep01/index.html`);
  await page.waitForFunction(() => window.sceneReady === true, null, { timeout: 120000 });
  const jobs = process.env.STILLS ? process.env.STILLS.split(',').map((s) => ({ t: Number(s), name: `s_${Number(s).toFixed(2)}.jpg` }))
    : Array.from({ length: f1 - f0 }, (_, i) => ({ t: (f0 + i) / fps, name: `f_${String(f0 + i).padStart(5, '0')}.jpg` }));
  for (let i = 0; i < jobs.length; i++) {
    const out = path.join(outDir, jobs[i].name);
    if (!process.env.STILLS && fs.existsSync(out)) continue;
    await page.evaluate((t) => window.renderFrame(t), jobs[i].t);
    await page.screenshot({ path: out, type: 'jpeg', quality: 93, clip: { x: 0, y: 0, width: 1280, height: 720 } });
    if (i % 100 === 0) console.log('frame', f0 + i, new Date().toISOString());
  }
  await browser.close(); server.close(); console.log('done', jobs.length);
});
