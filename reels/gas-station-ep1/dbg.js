const { chromium } = require('playwright'); const http = require('http'); const fs = require('fs'); const path = require('path');
const ROOT = __dirname; const views = process.argv.slice(2);
const server = http.createServer((q, r) => { const p = path.join(ROOT, decodeURIComponent(q.url.split('?')[0])); if (!fs.existsSync(p) || fs.statSync(p).isDirectory()) { r.writeHead(404); return r.end(); } r.writeHead(200, { 'Content-Type': { '.html': 'text/html', '.js': 'text/javascript', '.json': 'application/json', '.woff2': 'font/woff2' }[path.extname(p)] || 'application/octet-stream' }); fs.createReadStream(p).pipe(r); });
(async () => { await new Promise(r => server.listen(0, r)); const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
 const pg = await b.newPage({ viewport: { width: 720, height: 1280 } }); pg.on('pageerror', e => console.error('ERR', e.message)); pg.on('console', m => { if (m.type() === 'error') console.log('[c]', m.text()); });
 await pg.goto(`http://127.0.0.1:${server.address().port}/debug.html`); await pg.waitForFunction(() => window.sceneReady, null, { timeout: 60000 });
 for (const v of views) { await pg.evaluate(v => window.renderAt(1.0, v), v); await (await pg.$('#stage')).screenshot({ path: `out/dbg_${v}.png` }); }
 await b.close(); server.close(); })();
