// Renders scene.html frame by frame. Usage: node render.js [fps] [seconds] [onlyTimes,comma,separated]
const { chromium } = require('playwright');
const http = require('http');
const fs = require('fs');
const path = require('path');

const root = __dirname;
const fps = Number(process.argv[2] || 30);
const secs = Number(process.argv[3] || 4);
const only = process.argv[4] ? process.argv[4].split(',').map(Number) : null;
const SCENE = process.env.SCENE || 'scene.html';
const VW = Number(process.env.VW || 1280), VH = Number(process.env.VH || 720);
const outDir = path.join(root, only ? 'stills' : (process.env.OUT || 'frames'));
fs.mkdirSync(outDir, { recursive: true });

const types = { '.html': 'text/html', '.js': 'text/javascript' };
const server = http.createServer((req, res) => {
  const p = path.join(root, decodeURIComponent(req.url.split('?')[0]));
  if (!p.startsWith(root) || !fs.existsSync(p)) { res.writeHead(404); return res.end(); }
  res.writeHead(200, { 'Content-Type': types[path.extname(p)] || 'application/octet-stream' });
  fs.createReadStream(p).pipe(res);
}).listen(0, async () => {
  const port = server.address().port;
  const browser = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  const page = await browser.newPage({ viewport: { width: VW, height: VH } });
  page.on('console', (m) => { if (m.type() === 'error') console.log('PAGE:', m.text()); });
  page.on('pageerror', (e) => console.log('PAGEERR:', e.message));
  await page.goto(`http://127.0.0.1:${port}/${SCENE}`);
  await page.waitForFunction(() => window.sceneReady === true, null, { timeout: 60000 });
  const times = only || Array.from({ length: Math.round(fps * secs) }, (_, i) => i / fps);
  for (let i = 0; i < times.length; i++) {
    await page.evaluate((t) => window.renderFrame(t), times[i]);
    const name = only ? `still_${times[i].toFixed(2)}.png` : `f_${String(i).padStart(4, '0')}.png`;
    await page.screenshot({ path: path.join(outDir, name), clip: { x: 0, y: 0, width: VW, height: VH } });
    if (i % 20 === 0) console.log('frame', i, '/', times.length);
  }
  await browser.close(); server.close();
  console.log('done', times.length);
});
