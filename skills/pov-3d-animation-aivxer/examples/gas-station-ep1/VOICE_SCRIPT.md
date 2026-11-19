# Episode 1 — Voice Script (for ElevenLabs)

**3 voices:**
- **YOU** (cashier): young American man, tired, casual
- **MAYA**: early-20s American woman, panicked and breathless; cold and flat in her last line
- **OFFICER**: deep, authoritative American man. Generate him clean; I add the muffled-through-glass effect.

**How to deliver:** one file per line, named exactly like the ID (`l01.mp3`, `l02.mp3` …), mp3 or wav.
Keep each line under its **Max length** so it fits its shot. A little over is fine, I can nudge timings.
Tags in [brackets] are ElevenLabs v3 audio tags. Remove them if your model doesn't support tags.

| ID | Starts | Max length | Speaker | Line |
|---|---|---|---|---|
| l01 | 0:10.5 | 3.0s | YOU | [sighs] Dead quiet. Just me and the crickets. |
| l02 | 0:15.7 | 2.7s | MAYA | [panicked, breathless] Lock it! Please, hit the lock right now! |
| l03 | 0:18.7 | 3.1s | YOU | [startled] Whoa, hey—slow down! What's going on? |
| l04 | 0:22.3 | 7.5s | MAYA | [terrified, out of breath] A guy in a black sedan followed me for three miles. He saw me run in here. Lock the door! |
| l05 | 0:33.2 | 4.7s | YOU | [trying to stay calm] Okay, it's locked. You're safe. I'm calling 911— |
| l06 | 0:39.6 | 5.0s | YOU | [relieved] Wait—you're good. A cop just pulled into the lot. |
| l07 | 0:45.7 | 3.2s | MAYA | [terrified whisper] No. No, no, no... that's NOT a real cop. |
| l08 | 0:49.0 | 1.6s | YOU | [confused] What? He's in a cruiser— |
| l09 | 0:50.7 | 3.3s | MAYA | [urgent whisper] Look at the roof. There's no unit number. He's the one who was chasing me. |
| l10 | 1:04.4 | 6.4s | OFFICER | [shouting, authoritative] Police! Open the door! Is there a girl in a grey hoodie in there? |
| l11 | 1:11.1 | 5.9s | MAYA | [frantic whisper] Don't open it! Look at his belt—he doesn't even have a radio. If you unlock that door, we're both dead. |
| l12 | 1:16.9 | 6.0s | OFFICER | [yelling] Sir, step away from her right now! She just attacked a clerk at the Shell station two miles up. She's armed! |
| l13 | 1:23.1 | 0.9s | YOU | [shocked whisper] Wait... what? |
| l14 | 1:24.3 | 1.4s | YOU | [cautious, tense] Hey... what's in your pocket? |
| l15 | 1:25.9 | 3.0s | MAYA | [crying, desperate] It's just my house keys! Please, don't listen to him! |
| l16 | 1:31.4 | 4.2s | YOU | [exhales in relief] Holy crap... she's telling the truth. |
| l17 | 1:43.3 | 3.5s | OFFICER | [yelling, threatening] Last chance! Unlock the door! |
| l18 | 1:48.6 | 3.0s | MAYA | [dead calm, icy] Don't touch that button. |
| l19 | 1:52.6 | 3.4s | YOU | [quiet voiceover, ominous] One of them is lying. Or... both of them are. |

Send the 19 files (zip is fine). I drop them into `voices_rec/`, re-sync the subtitles and lip-sync,
remix with the SFX, and re-render the video.
