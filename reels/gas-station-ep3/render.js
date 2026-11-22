// Usage:
//   node render.js --still 1,2,3                 → out/still_<t>.png
//   node render.js --from 0 --to 1200 [--nohud]  → out/frames/f_XXXX.png for that frame range (no encode)
//   node render.js --encode [--out file.mp4]     → encode out/frames + out/mix.wav (or sfx.wav)
const { chromium } = require('playwright');
const http = require('http'), fs = require('fs'), path = require('path');
const { execFileSync } = require('child_process');
const args = process.argv.slice(2);
const opt = (k, d) => { const i = args.indexOf(k); return i >= 0 ? args[i + 1] : d; };
const ROOT = __dirname, FPS = 30, DIR = path.join(ROOT, 'out', 'frames');
const OUT = opt('--out', path.join(ROOT, 'out', 'episode3_full.mp4'));
if (args.includes('--encode')) {
  const audio = ['mix.wav', 'sfx.wav'].map(f => path.join(ROOT, 'out', f)).find(f => fs.existsSync(f));
  const aIn = audio ? ['-i', audio] : [], aOut = audio ? ['-c:a', 'aac', '-b:a', '192k', '-shortest'] : [];
  execFileSync('ffmpeg', ['-y', '-v', 'error', '-framerate', String(FPS), '-i', path.join(DIR, 'f_%04d.png'), ...aIn,
    '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '17', '-preset', 'slow', ...aOut, '-movflags', '+faststart', OUT]);
  console.log('wrote', OUT); process.exit(0);
}
const types = { '.html': 'text/html', '.js': 'text/javascript', '.json': 'application/json', '.woff2': 'font/woff2' };
const server = http.createServer((req, res) => {
  const p = path.join(ROOT, decodeURIComponent(req.url.split('?')[0]));
  if (!p.startsWith(ROOT) || !fs.existsSync(p) || fs.statSync(p).isDirectory()) { res.writeHead(404); return res.end(); }
  res.writeHead(200, { 'Content-Type': types[path.extname(p)] || 'application/octet-stream' });
  fs.createReadStream(p).pipe(res);
});
(async () => {
  await new Promise(r => server.listen(0, r));
  const browser = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  const page = await browser.newPage({ viewport: { width: 720, height: 1280 }, deviceScaleFactor: 1 });
  page.on('pageerror', e => console.error('[pageerror]', e.message));
  page.on('console', m => { if (m.type() === 'error') console.error('[console]', m.text()); });
  await page.goto(`http://127.0.0.1:${server.address().port}/index.html`);
  await page.waitForFunction(() => window.sceneReady, null, { timeout: 120000 });
  await page.evaluate(() => window.sceneReady);
  await page.evaluate(h => window.setHud(h), !args.includes('--nohud'));
  const stage = await page.$('#stage');
  fs.mkdirSync(DIR, { recursive: true });
  if (opt('--still', null)) {
    for (const t of opt('--still').split(',').map(Number)) {
      for (const dt of [0.1, 0.066, 0.033, 0]) await page.evaluate(t => window.renderAt(t), Math.max(0, t - dt));
      await stage.screenshot({ path: path.join(ROOT, 'out', `still_${t}.png`) });
    }
  } else {
    const from = +opt('--from', 0), to = +opt('--to', 3480);
    for (let i = from; i < to; i++) {
      await page.evaluate(t => window.renderAt(t), i / FPS);
      await stage.screenshot({ path: path.join(DIR, `f_${String(i).padStart(4, '0')}.png`) });
      if (i % 150 === 0) console.log(`frame ${i} (${from}-${to})`);
    }
  }
  await browser.close(); server.close();
})().catch(e => { console.error(e); process.exit(1); });
