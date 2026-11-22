#!/usr/bin/env bash
# One-time setup for a project folder (a copy of an example). Usage: bash scripts/setup.sh [project_dir]
# Needs only the npm and PyPI registries — no browser download site, no apt.
set -e
DIR="${1:-.}"; HERE="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"
[ -f package.json ] || npm init -y >/dev/null
npm i --no-audit --no-fund --loglevel=error three@0.160.0 @fontsource/rubik@5.0.20 playwright-core@1.49.1 @sparticuz/chromium@131.0.1
cp -n "$HERE/browser.js" ./browser.js 2>/dev/null || true
PIPS="numpy scipy soundfile opencv-python-headless imageio-ffmpeg"
pip install -q $PIPS 2>/dev/null || pip install -q --break-system-packages $PIPS
if ! command -v ffmpeg >/dev/null 2>&1; then
  F=$(python3 -c "import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())")
  mkdir -p "$HOME/.local/bin"; ln -sf "$F" "$HOME/.local/bin/ffmpeg"
  echo "ffmpeg installed from PyPI -> $HOME/.local/bin/ffmpeg  (run: export PATH=\"$HOME/.local/bin:\$PATH\")"
fi
echo "SETUP OK. Next: bash scripts/smoke_test.sh (must pass before writing any scene code)."
