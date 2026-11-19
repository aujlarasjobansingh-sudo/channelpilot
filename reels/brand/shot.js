const { chromium } = require('playwright'); const path = require('path');
(async () => { const b = await chromium.launch(); const p = await b.newPage();
  await p.goto('file://' + path.join(__dirname, 'logo.html')); await p.waitForFunction(() => window.ready);
  for (const [id, w, h] of [['square', 1080, 1080], ['wm', 700, 300]]) {
    await p.setViewportSize({ width: w, height: h });
    await p.evaluate(id => { document.querySelectorAll('.v').forEach(e => e.style.display = 'none'); document.getElementById(id).style.display = 'block'; }, id);
    await (await p.$('#' + id)).screenshot({ path: path.join(__dirname, id === 'square' ? 'povXOfficial_logo.png' : 'povXOfficial_watermark.png'), omitBackground: true });
  } await b.close(); })();
