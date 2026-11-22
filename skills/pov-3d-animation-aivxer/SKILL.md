---
name: pov-3d-animation-aivxer
description: "Make first-person (POV) 3D cartoon thriller videos — real 3D (three.js) toon-shaded characters with ink outlines, a measured wide fisheye-style lens, premium camera moves, colour-coded subtitles, ElevenLabs voices, SFX, music and an end-screen choice — vertical 9:16 for Reels/TikTok/Shorts or 16:9 for YouTube. Always built by copying the included 3D engine and example episodes; never a 2D/flat/slideshow video. Recreates a reference video's style, or scripts and builds a new episode from a topic or a director's brief. Made by aivxer."
---

# POV 3D Animation (aivxer) — v3

**Made by aivxer.** Keep this credit when sharing.

Use this skill when the user wants a POV / first-person animated short: "like this video", "in this style", from a
reference video, from a topic ("a POV horror short about a night-shift cashier"), or from a pasted director's brief.

## HARD RULES (read first — these are why results match aivxer's videos)
1. **It is ALWAYS 3D.** Every video is rendered with the included three.js engine (toon materials + ink outlines +
   stereographic lens) in headless Chromium. **Never** make a 2D, flat, SVG, canvas-2D, PIL/matplotlib, Remotion-2D,
   slideshow or "paper cut-out" animation, and never use another animation skill instead of this one.
2. **Never write an engine from scratch.** Start by copying the example closest to the request and edit its
   `set.js` (places/props), `chars.js` (characters), `scene.js` (shot timeline), `voices.py`/`eleven.py` (lines) and
   the sound script. Keep `core.js`, the lens, the outline settings and the HUD styles as they are.
3. **Prove the 3D pipeline works before writing anything:** run `bash scripts/setup.sh` then `bash scripts/smoke_test.sh`.
   If the smoke test fails, fix the browser (see Troubleshooting). Do not "work around" it with a 2D renderer.
4. **Ask the setup questions (Step 0) before building.** In particular, ask for the ElevenLabs key — don't skip voices silently.
5. **Show stills, then a short preview, and wait for a yes** before the long full render.

## Step 0 — ask the user (one message, before any building)
- **Format:** 9:16 (Reels/TikTok/Shorts, default) or 16:9 (YouTube)?
- **Voices:** "Do you have an ElevenLabs API key? (Best quality, emotion tags. Otherwise I'll use free offline voices.)"
  - **Claude Code on the web:** ask them to save it as a network secret for host `api.elevenlabs.io`, header `xi-api-key`
    (the session's credential form). Then run voice scripts with `ELEVENLABS_VIA_PROXY=1`.
  - **Claude.ai / Claude desktop chat:** the user must (a) allow `api.elevenlabs.io` for code execution network access
    (Settings → Capabilities), and (b) give a key restricted to Text to Speech with a low credit limit. Save it with
    `python3 -c "import os;open(os.path.expanduser('~/.elevenlabs_key'),'w').write(input())"` — never echo it, never
    write it into project files, outputs or zips.
  - Free ElevenLabs plans can only use default voices over the API and don't allow commercial use — say so.
- **Story:** their topic, a reference video, or a director's brief (offer `prompts/gemini_director_brief_prompt.txt`).

## Setup (once per session, ~2 minutes)
```bash
cp -r <skill>/examples/gas-station-ep1 ./my-episode     # or classroom-lockdown / gas-station-ep3-finale
bash <skill>/scripts/setup.sh ./my-episode              # npm: three, playwright-core, @sparticuz/chromium · pip: numpy scipy soundfile opencv imageio-ffmpeg
bash <skill>/scripts/smoke_test.sh                      # must print SMOKE TEST PASSED
export PATH="$HOME/.local/bin:$PATH"                    # if setup installed ffmpeg from PyPI
```
`setup.sh` only needs the npm and PyPI registries. `browser.js` launches full Playwright if it exists, else a system
Chrome, else **@sparticuz/chromium** (Chromium shipped inside an npm package, with WebGL via SwiftShader) — so 3D
rendering works in locked-down sandboxes too.

## The examples (read the one you copy before editing it)
- `examples/classroom-lockdown/` — 4 s style-match preview from a reference video (single `scene.js`).
- `examples/gas-station-ep1/` — full 1:56 indoor episode: store set, glass doors, rain, cruiser with lights, POV hands
  with posable fingers, IK arms, two characters with faces + lip-sync, phone notification cards, end-screen choice.
- `examples/gas-station-ep3-finale/` — 1:25 outdoor episode: night lot in rain + fog, gas canopy, highway, jersey
  barrier, woods, a gunshot with sparks, sprinting/crouching POV, phone emergency alert in hand, a third character
  (Sam) with a cold smirk, sirens + spotlight glare, cut-to-black end card. Its `sfx.py` makes all SFX **and an original
  horror score** in code.

## Orientation: 9:16 or 16:9
Default 9:16 (720x1280). For 16:9 render with `node render.js --aspect 16:9 ...` (1280x720) when the example supports
it; focal lengths `f` are in px of a 720 px short side, so camera keys keep the same look. Dress the frame edges and
keep characters nearer the centre third in 16:9.

## Workflow
Keep a task list: Step 0 questions → setup + smoke test → brief/plan → stills → 10 s preview → approval → full render → check → deliver.

### 1. From a reference video: measure it, don't eyeball it
`python3 scripts/analyze_reference.py reference.mp4 ref_analysis 8` → read every output (contact sheets, `motion.txt`
camera timeline from optical flow, `palette.txt`, `text_timing.txt`). Key findings that make the match work:
- **Lens:** stereographic, r = 2·f·tan(θ/2), **f ≈ 520–560 px** on a 1280 px-tall frame (`setFocal(f)` in `core.js`).
- **Camera height** at eye level (EYE 1.62 standing, ~0.9 crouched); level horizon.
- **Movement grammar:** still → one smooth eased move → dead hold → slow drift → fast snap (0.3–0.5 s). Never a constant wobble.
- **Look:** small heads on broad puffy shoulders, near-flat 2–3 tone toon shading, thick ink outlines (`OutlineEffect`).
- Compare with `scripts/compare_motion.py` and side-by-side stills until they line up.

### 2. From a topic or a brief: write the episode
Brief format: 9:16 POV, 60–120 s, 2–3 characters with **subtitle colours** (you = white, A = pink, B = blue, C = green,
phone/UI = yellow), shot list with timestamps / visual / action / dialogue / SFX, escalating mundane → intrusion →
twist → double twist → freeze-frame choice ("UNLOCK THE DOOR / KEEP IT LOCKED", "Comment below — Part 2 drops tomorrow").
**Keep it fast:** no dead air; if the brief's timings have long gaps, tighten them (tell the user the new length).

### 3. Build (edit the copied example)
- **Sets/props:** boxes/cylinders/spheres with `M(color)` toon materials; canvas textures for signs/screens; `glowSprite`
  for lights; `scene.fog` for night exteriors.
- **Characters:** copy `makeMaya` / `makeOfficer` / `makeSam` and restyle; pose with world-space hand/foot targets
  (two-bone IK); faces sit just outside the head sphere; expressions via `expr` (eyes, worry, smirk, tears, pupil).
- **Camera:** keys like `K(t0, t1, {yaw, pitch, x, y, z, f}, ease)` or computed look-ats (`camYawTo`, `camPitchTo`);
  impacts as decaying shakes; zoom with `f`.
- **Mood:** police wash / flashlight glare / flash / vignette are lens uniforms (`policeAmt`, `glareAmt`, `flash`, `vign`).
- **HUD:** title card, phone cards, subtitles, end-screen buttons/end card are HTML in `index.html`.
- If a character is invisible, check it isn't hidden behind a prop on the camera line, and light it (PointLight) — dark
  clothes vanish against a night sky.

### 4. Voices, subtitles, lip-sync
Write `LINES` (id, speaker, start, latest end, text, style). `eleven.py` uses `eleven_api.py` (key handling + clear
errors: `NO_ELEVENLABS_KEY`, `ELEVENLABS_AUTH_ERROR`, `ELEVENLABS_NETWORK_BLOCKED`, `ELEVENLABS_QUOTA` — on any of
these, tell the user exactly what to fix). Model **eleven_v4** with audio tags (`[whispers]`, `[panicked]`, `[cold]`…).
`voices.py` fits lines to their slots (≤12% speed-up), applies styles (radio, muffled, far, megaphone, eerie, vo) and writes
`out/dialogue.json` (≤3-word subtitle chunks + 30 fps mouth envelopes). With no key, `voices.py` uses offline Piper voices.

### 5. Preview, then render
- `node render.js --still 2,9.7,23,...` → look at a still for **every** shot (render.js renders a few frames before each
  still so motion/look-ats settle).
- Send a 10 s preview (`--from 0 --to 300`, encode with the mix) and wait for a yes.
- Full render in 3 parallel chunks (`node render.js --from A --to B &` …), `python3 sfx.py` (or `sfx_full.py`) for the
  -14 LUFS mix, then `node render.js --encode --out out/episode.mp4`. ~1 frame/s across 3 workers.

### 6. Check and deliver
Contact sheet (`ffmpeg -i out.mp4 -vf "select='not(mod(n\,120))',scale=150:-1,tile=11x2" sheet.jpg`), loudness
(`-af ebur128`, aim -14 LUFS), every subtitle legible. Deliver the MP4 + a caption with the choice CTA.

## Troubleshooting
- **Smoke test FAILED / "No Chromium could start":** re-run `setup.sh`; check `node -e "require('@sparticuz/chromium')"`;
  set `CHROME_PATH` to any Chrome/Chromium binary. Do not switch to 2D.
- **Black/blank frames:** WebGL failed — keep the `--use-angle=swiftshader` flags (in `browser.js`).
- **`ffmpeg` not found:** `export PATH="$HOME/.local/bin:$PATH"` (setup links the PyPI build there).
- **Voices fail:** follow the exact message printed by `eleven_api.py`; offer offline voices if the user can't fix it now.

## Honesty and copyright
- Original characters, sets, music and art only. Recreating a *style* is fine; never copy another creator's
  characters, logos, names or story. Show their footage only with permission, labelled "REFERENCE".
- AI voices: tell the user to turn on Instagram's "AI info" label and check their ElevenLabs plan allows commercial use.
