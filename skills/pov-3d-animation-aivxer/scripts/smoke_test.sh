#!/usr/bin/env bash
# Proves the 3D pipeline works HERE before any episode is written: renders one still of the gas-station example
# and checks it is a real 3D frame (not blank). Usage: bash scripts/smoke_test.sh   (from the skill folder)
set -e
export PATH="$HOME/.local/bin:$PATH"
HERE="$(cd "$(dirname "$0")/.." && pwd)"; T="${TMPDIR:-/tmp}/pov3d_smoke"
rm -rf "$T"; cp -r "$HERE/examples/gas-station-ep1" "$T"; cp "$HERE/scripts/browser.js" "$T/"
bash "$HERE/scripts/setup.sh" "$T" >/dev/null
cd "$T" && node render.js --still 15.5
python3 - "$T/out/still_15.5.png" <<'PY'
import sys, cv2, numpy as np
im = cv2.imread(sys.argv[1]); ok = im is not None and im.std() > 25 and len(np.unique(im.reshape(-1, 3) // 16, axis=0)) > 60
print(('SMOKE TEST PASSED: 3D render works (%s)' % sys.argv[1]) if ok else 'SMOKE TEST FAILED: frame is blank — do NOT continue, fix the browser first')
sys.exit(0 if ok else 1)
PY
