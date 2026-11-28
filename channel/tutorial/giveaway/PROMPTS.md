# Free Prompts: Make AI-Animated "What If" Story Videos with Claude

Use these in order. Paste them into Claude exactly as written, and change only the parts in [brackets].

---

## Step 1: Topic

**Prompt 1: Check YouTube's rules first**
```
Read YouTube's current rules for faceless channels, including the inauthentic content and reused content policies, and tell me what I must do so my channel can be monetized.
```

**Prompt 2: Build your idea**
```
My channel idea: second-person POV stories called "[your series name]", where every episode drops the viewer into a brand-new world and makes them the main character. The worlds can have an anime feel, but the story, names, ranks and monsters must be 100% original, with no copied plots. Give me 10 episode ideas with a "What happens if you…" title for each.
```

---

## Step 2: Script

**Prompt 3: World bible + full script**
```
Write a 20–30 minute second-person POV story script for my channel "[your series name]".
Episode: "[your episode title]".

Rules:
1. Open with a "What happens if you…" hook and reveal nothing.
2. Ask viewers to subscribe right after the hook.
3. Explain how the world works early on.
4. Tell the full story in an engaging style, with original names, ranks and monsters only.
5. At the end, ask viewers which world they want next.

First give me a world bible (city, ranks, power system, threat levels, main characters).
Then write the full narration in paragraphs, in English.
```

**Prompt 4: Split it for the voiceover**
```
Split the narration into parts of under 5,000 characters each, cutting only at the end of a paragraph. Narration only: no headings, no notes.
```

---

## Step 3: Voiceover

Paste each part into ElevenLabs, pick a deep, calm English storytelling voice, and download each part as an MP3.
(Use a paid ElevenLabs plan if you're going to monetize. The free plan doesn't allow commercial use.)

---

## Step 4: Animation

First, upload the free skill (the `2d-animation-long-form-aivxer` folder in this pack, zipped) in Claude's settings under Customize → Skills → + → Upload a skill. Check that this matches the menu in your own Claude app.

**Prompt 5: Set the style**
*(attach a reference image or video of the look you like)*
```
Make animation in this style. I want movement in every scene, and it should feel premium. Keep my characters original. Main character: [describe your hero, e.g. red t-shirt with a white lightning bolt, black spiky hair, blue jeans].
```

**Prompt 6: Preview first**
```
Don't make the full video yet. Make a 10-second preview first so I can check the style.
```

**Prompt 7: Make it premium**
```
Make it more premium. Make the characters look better. If someone is sleeping, it should look good. Make the fight scenes look good. Add depth, lighting, impact frames and film grain.
```

**Prompt 8: Full part (with the sync fix built in)**
*(attach your Part 1 voiceover MP3)*
```
Here is the voiceover for Part 1. Make the full part in this style.
Before animating, transcribe the voiceover with word timestamps and start every scene on the first word of its sentence.
One scene per sentence, movement in every shot, characters' mouths moving when they talk, anime-style fight scenes.
```

**Prompt 9: Check every scene**
```
Before the final render, pull one frame from every sentence and check that what's on screen matches what the voice is saying. Fix any scene that doesn't match.
```

**Prompt 10: Next parts**
*(attach your Part 2 voiceover MP3)*
```
Make Part 2 and join it to Part 1. Don't remake Part 1.
```

---

## If your video goes out of sync

```
The voice and the scenes are out of sync. Transcribe my voiceover with word timestamps, and start every scene on the first word of its sentence. Then pull one frame from every sentence and check it matches what the voice is saying.
```

---

Made by aivxer. If you make a video with this, drop the link in the comments!
