POV 3D Animation skill for Claude — made by aivxer

INSTALL
1. Open Claude → Customize → Skills → "+" → Create skill → Upload a skill.
2. Upload this zip (pov-3d-animation-aivxer.zip).
3. Start a new chat in Claude (with code execution / Claude Code) and say, for example:
   "Make a POV horror short about a night-shift cashier at a gas station"
   or attach a reference video and say "Recreate this video's style".

FORMATS
- 9:16 vertical (Reels, TikTok, Shorts) — default
- 16:9 landscape (YouTube) — just ask Claude for 16:9

NEW IN v3 (fixes)
- Always real 3D: the skill now refuses 2D fallbacks and proves the 3D renderer works first (scripts/smoke_test.sh).
- Works in locked-down sandboxes (Claude.ai): Chromium now installs from npm (@sparticuz/chromium) — no browser download site needed.
- ElevenLabs: Claude now ASKS for your key up front and tells you exactly what to fix if it fails.
  In Claude.ai also allow api.elevenlabs.io under Settings -> Capabilities (code execution network access).
- New full example: Gas Station Episode 3 (outdoor night, rain, gunshot, phone alert, sirens, original horror score).

WHAT YOU GET
- The full skill (SKILL.md) with the step-by-step workflow Claude follows.
- prompts/gemini_director_brief_prompt.txt: paste into Gemini with your idea to get a full director's brief, then paste that into Claude.
- scripts/analyze_reference.py: measures a reference video's lens, camera moves, colours and subtitle timing.
- Three complete example projects: a 4-second style-match preview, a full 1:56 indoor episode and a 1:25 outdoor finale
  (3D set, characters with lip-sync, camera moves, ElevenLabs voices, SFX, subtitles, end-screen choice).

NOTES
- ElevenLabs voices are optional (bring your own API key). Free ElevenLabs plans don't allow commercial use.
- Rendering a 2-minute episode takes about an hour of compute; previews take a few minutes.
- Check the menu path above matches your Claude app before following it.
