// Launch a headless Chromium WITH WebGL, wherever this runs (Claude.ai sandbox, Claude Code, a laptop).
// Order: full Playwright → a system Chrome/Chromium → @sparticuz/chromium (a Chromium that ships inside an npm package,
// so it works even when only the npm registry is reachable). Never fall back to a 2D renderer.
const fs = require('fs');
const GL = ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'];
async function launchBrowser() {
  const tried = [];
  try { const { chromium } = require('playwright'); return await chromium.launch({ args: GL }); }
  catch (e) { tried.push('playwright: ' + String(e.message).split('\n')[0]); }
  let chromium;
  try { ({ chromium } = require('playwright-core')); } catch (e) { throw new Error('playwright-core is not installed. Run: bash scripts/setup.sh'); }
  for (const p of [process.env.CHROME_PATH, '/usr/bin/chromium', '/usr/bin/chromium-browser', '/usr/bin/google-chrome', '/opt/pw-browsers/chromium/chrome-linux/chrome'].filter(Boolean)) {
    if (!fs.existsSync(p)) continue;
    try { return await chromium.launch({ executablePath: p, args: [...GL, '--no-sandbox'] }); }
    catch (e) { tried.push(p + ': ' + String(e.message).split('\n')[0]); }
  }
  try {
    const sp = require('@sparticuz/chromium'); const exe = await sp.executablePath();
    return await chromium.launch({ executablePath: exe, args: [...sp.args, ...GL] });
  } catch (e) { tried.push('@sparticuz/chromium: ' + String(e.message).split('\n')[0]); }
  throw new Error('No Chromium could start. Run: bash scripts/setup.sh   Tried:\n  ' + tried.join('\n  '));
}
module.exports = { launchBrowser };
