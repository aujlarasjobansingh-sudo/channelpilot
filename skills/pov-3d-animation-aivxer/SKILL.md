---
name: pov-3d-animation-aivxer
description: "Make first-person (POV) 3D cartoon thriller videos, vertical 9:16 for Reels/TikTok/Shorts or 16:9 for YouTube: toon-shaded characters with ink outlines, a measured wide fisheye-style lens, premium camera moves, colour-coded subtitles, ElevenLabs voices, SFX and an end-screen choice. Recreates a reference video's exact style, or scripts and builds a new episode from just a topic. Made by aivxer."
---

# POV 3D Animation (aivxer)

**Made by aivxer.** Keep this credit when sharing.

Use this skill when the user wants a POV / first-person animated short "like this video", "in this style", from a
reference video, or from a topic alone ("make a POV horror short about a night-shift cashier"). Everything is drawn in
code (three.js rendered frame by frame in headless Chromium), so there is no stock footage and no image generator.

Two complete, working examples ship in `examples/` — read them before writing anything:
- `examples/classroom-lockdown/` — a 4-second style-match preview built from a reference video (one file, `scene.js`).
- `examples/gas-station-ep1/` — a full 1:56 episode: `core.js` (renderer, lens, helpers), `set.js` (store, doors,
  counter, cruiser), `chars.js` (POV hands with posable fingers, IK arms, two full characters with faces and lip-sync),
  `scene.js` (the whole shot timeline), `voices.py` + `eleven.py` (dialogue), `sfx_full.py` (sound design + mix).

## Setup (once per session)
1. Copy the example closest to the request into a project folder. Run `npm i` there (three@0.160.0, @fontsource/rubik).
2. Python: `pip install opencv-python-headless numpy scipy soundfile`. ffmpeg must exist. Playwright + Chromium must
   exist (`node -e "require('playwright')"`); render with `--use-angle=swiftshader` (already in `render.js`).
3. Voices: ElevenLabs (`eleven.py`, model **eleven_v4**, audio tags) if the user has a key — set `ELEVENLABS_API_KEY`,
   or in a Claude cloud session save it as a network secret for `api.elevenlabs.io` with header `xi-api-key`.
   Free ElevenLabs plans can only use default voices over the API and don't allow commercial use — tell the user.
   No key: offline Piper voices (`voices.py`, models from the rhasspy/piper GitHub release v0.0.2; Hugging Face is often blocked).

## Orientation: 9:16 or 16:9
Ask which format the user wants if they haven't said (default 9:16 for Reels/TikTok/Shorts; 16:9 for YouTube).
- The engine reads `index.html?aspect=16:9`; render with `node render.js --aspect 16:9 ...` (1280x720). Default is 9:16 (720x1280).
- Focal lengths (`f`) are in px of a 720px short side, so the same camera keys keep the same lens look in both orientations.
- `index.html` has a `.landscape` layout for every overlay (title card, phone cards, subtitles lower third, end-screen buttons side by side).
- 16:9 shows more of the set left and right: dress the edges of each shot, keep characters nearer the centre third, and
  prefer slightly tighter focal lengths (×1.1–1.2) for close-ups. For both formats from one project, render each with its own `--aspect`.

## Writing the brief with Gemini (optional)
`prompts/gemini_director_brief_prompt.txt` makes Gemini (or any chat model) write a director's brief in exactly the format
this skill expects. The user pastes that brief here; build from it.

## Workflow
Keep a task list: analyse → plan → 4 s (or 10 s) preview → approval → full build → check → deliver.

### 1. From a reference video: measure it, don't eyeball it
`python3 scripts/analyze_reference.py reference.mp4 ref_analysis 8` and read **every** output:
- `sheet_*.jpg`, `early.jpg`, `stills/` — what's in each scene; the preview must match the first seconds exactly.
- `motion.txt` — the camera timeline from optical flow. Zero rows = a dead hold. A bell of px/frame = an eased move
  (peak/average ≈ 1.57 → sine ease-in-out). Small steady values = a slow drift. Centre and desk moving by the same
  amount = pure rotation (no head translation). Convert px to degrees with the lens below.
- `palette.txt` — sampled colours; build the toon palette from these, not from memory.
- `text_timing.txt` — subtitle pop times, widths and heights; title fade/slide timing.
Key lessons that made the match work (see `examples/classroom-lockdown/scene.js`):
- **Lens:** a stereographic wide lens, r = 2·f·tan(θ/2) with **f ≈ 540 px on a 1280 px-tall frame** (~122° vertical),
  not a bulging barrel. Render a rectilinear source with the matching FOV and remap in a fragment shader (`core.js` → `lens`).
- **Camera height** at the subject's eye level; level horizon at frame centre unless the reference says otherwise.
- **Movement is what reads as "premium":** still → one smooth eased move → dead hold → slow drift → fast snap
  (0.3–0.5 s). Never a constant sine wobble or roll.
- **Proportions:** small heads on broad, puffy shoulders; near-flat 2–3 tone shading; thick ink outlines (`OutlineEffect`).
- Compare your render to the reference with `scripts/compare_motion.py` and side-by-side stills; iterate until the
  motion table and the stills line up. Then show the user a side-by-side video.

### 2. From a topic only: write the episode
Write a director's brief first and show it: format (9:16 POV, ~60–120 s), 2–3 characters with **subtitle colours**
(you = white, character A = pink, character B = blue, phone/UI = yellow), and a shot list with timestamps, visual,
action, dialogue and SFX per shot, ending on a freeze frame with a two-option choice ("UNLOCK THE DOOR / KEEP IT
LOCKED") and "Comment below — Part 2 drops tomorrow". Escalate: mundane → intrusion → twist → double twist → choice.

### 3. Build
- Sets and props are boxes/cylinders/spheres with `M(color)` toon materials, canvas textures for signs and screens,
  and `inkLine` strips on room edges. Animated canvas for rain on glass, phone screens, POS screens.
- Characters: copy `makeMaya`/`makeOfficer`/`makeHand` from `chars.js` and recolour or restyle; pose with world-space
  hand/foot targets (two-bone IK). Faces sit just outside the head sphere (eyes at z ≈ r + 0.0035).
- Camera: list moves as `K(t0, t1, {yaw, pitch, x, y, z, f}, ease)` like `scene.js`; add `SHAKES` for impacts; zoom by changing `f`.
- Lighting moods: police red/blue wash and flashlight glare are lens-shader uniforms (`policeAmt`, `glareAmt`), freeze
  vignette is `vign`. Keep tints multiplicative so shadows stay dark.
- HUD (title, phone notification cards, subtitles, end-screen buttons) is HTML over the canvas in `index.html`.

### 4. Voices, subtitles, lip-sync
Write `LINES` with a start time and a latest end per line (fit each line to its shot). `eleven.py` generates them with
emotion tags (`[whispers]`, `[panicked]`, `[crying]`, `[cold]` …); `voices.py` trims, tightens pauses, speeds up at most
12%, schedules lines (starting earlier into slack, L-cutting over the next shot when nobody else speaks), applies the
muffled-through-glass effect to off-screen speakers, and writes `out/dialogue.json` (subtitle chunks of ≤3 words +
mouth envelopes at 30 fps) used by `scene.js`.

### 5. Preview, then render
- `node render.js --still 1,6.9,15.5` → look at stills for every shot before any long render.
- Send a 4 s or 10 s preview and wait for a yes.
- Full render in parallel chunks: `node render.js --from 0 --to 1160 & … & wait`, then `python3 sfx_full.py` (SFX +
  music + dialogue → `out/mix.wav`, two-pass loudnorm to -14 LUFS) and `node render.js --encode`.
  Speed: ~1 frame/s across 3 workers (a 2-minute episode ≈ 55 min). Re-render the whole thing only when subtitles or
  lip-sync timing change (they are drawn into the frames).

### 6. Check
Contact sheet of the final (`ffmpeg -i out.mp4 -vf "select='not(mod(n\,150))',scale=180:-1,tile=12x2" sheet.jpg`),
loudness (`-af ebur128`, aim -14 LUFS), and every subtitle chunk legible. Deliver the MP4 plus a caption.

## Honesty and copyright
- Only original characters, sets and art. Recreating a *style* is fine; never copy another creator's characters,
  logos, names or story. Show their footage (e.g. a side-by-side) only if the user has permission, labelled "REFERENCE".
- AI voices: tell the user to turn on Instagram's "AI info" label, and check their ElevenLabs plan allows commercial use.
