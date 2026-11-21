# aivxer YouTube Tutorial — Full Voiceover Script (16:9)

**Title:** I Gave Claude ONE Viral Video… It Rebuilt the Entire Animation Style (Full Breakdown)
**Length:** ~10–11 minutes · **Format:** 16:9, aivxer editing style (Mac desktop, app windows, cursor, pills, big titles)
**Rules:** the other page's name, photo, link and watermark are always blurred and labelled "THEIR PAGE". No price anywhere.

---

## 0:00 — Hook

This animated POV page has over two hundred thousand followers. One of its videos crossed thirty million views. And there's no studio behind it, no team of animators. It's simple 3D cartoons, filmed through your own eyes, where *you* are the main character, and at the end you choose what happens next.

So I asked myself one question: can Claude make videos like this? Not a slideshow, not a talking avatar, but a real animated short with characters, camera moves, voices and sound. I gave Claude one single video from this page. What it built in the next few hours honestly changed how I think about content.

In this video I'll show you everything: how Claude studied the original, how it rebuilt the style, how I used it to make my own original series, the results I got on my page, and exactly how you can do the same thing, step by step. Let's get into it.

## 0:55 — The Reference: Why These Videos Work

Before building anything, let's understand why this format works so well.

First, the camera is your eyes. You see your own hands on the desk and your own arms, so your brain puts you inside the story.

Second, the style is simple on purpose: flat cartoon colours, thick black outlines and small heads on big puffy shoulders. It looks friendly, which makes the horror moments hit even harder.

Third, the pacing never stops. There's a calm moment, then something strange, then a twist, then another twist, and right when it gets intense, the video freezes and asks you: what do you do? Two buttons, green or red. Everyone comments their answer, and that comment section is what pushes these videos to millions.

So my goal wasn't to copy their characters or their stories. That's not okay. My goal was to recreate the *style*: the look, the lens, the camera, the rhythm. Then I'd tell my own original stories with it.

## 2:00 — Step 1: Claude Measures the Video Instead of Guessing

Here's the part most people don't expect. I uploaded one video to Claude and said, "Recreate this style." Claude didn't eyeball it. It wrote a small analysis script and *measured* the video.

It split the video into frames and made contact sheets, so it could see every scene at once. Then it ran optical flow, a technique that tracks how pixels move from one frame to the next. That gave it a timeline of the camera: when it holds still, when it makes a smooth eased move, when it does a fast snap. It even worked out that the moves follow a sine ease-in and ease-out, from the shape of the speed curve.

Next it sampled the colours, the actual wall colours, desk colours and skin tones, so the palette came from the video, not from memory. And it measured the subtitles: when each word pops, how big the text is and how long it stays on screen.

The biggest discovery was the lens. The video looks like a fisheye, but not a cheap bulging one. Claude measured how straight lines bend toward the edges and matched it to a stereographic lens, the kind that keeps faces looking natural while showing a very wide view. Getting that one number right is what made everything feel like the original.

## 3:30 — Step 2: Rebuilding It in 3D, From Code

Now the build. Everything you're going to see is drawn in code. There's no stock footage, no image generator and no video AI. Claude uses three.js, a 3D engine that runs in a web browser.

The classroom, the desks, the doors and the lockers are all simple shapes: boxes, cylinders and spheres with flat cartoon materials. The thick black outlines come from an outline effect that draws ink around every object. Then the special wide lens is applied on top as a final pass, like putting a real lens on a camera.

The camera itself is written like a director's shot list: at this second, look left; ease to the door over half a second; hold; then snap to the window. That's why the movement feels premium. It's never a constant wobble. It's still, smooth move, dead hold, slow drift, fast snap.

Then Claude renders the video one frame at a time inside a headless browser, thirty frames for every second, and stitches them together into an MP4. Here's the original next to Claude's version: same lens, same camera move, same timing.

## 4:40 — Step 3: Characters That Actually Act

A style test is one thing, but a story needs characters. Claude built them from scratch.

Each character has a body, a face with eyes, eyebrows and a mouth, and arms that use something called inverse kinematics. Instead of animating every joint, you just say "put the hand here," and the elbow and shoulder figure themselves out. That's how my POV hands grab a walkie-talkie, hold bike handlebars, or press against a fence.

The faces can show fear, worry and tears, and in my horror episode one character's eyes slowly turn completely black. The mouths move with the voices too. Claude measures how loud each line of dialogue is, frame by frame, and opens the mouth to match. So the lip-sync is automatic.

## 5:40 — Step 4: Voices with ElevenLabs

For voices, I use ElevenLabs. Claude writes every line of dialogue with emotion tags like *whispers*, *panicked*, *crying* or *cold*, and generates them through the ElevenLabs API.

But it doesn't just drop the audio in. It trims silences, tightens pauses and fits every line to its shot, so there's no dead air. It also adds effects. In my 80s episode, the best friend talks through a walkie-talkie, so Claude ran his voice through a radio filter with static. Then a *second* voice appears in the woods, the same voice but with a strange doubled echo, because the twist is that something is copying him. Same voice, two versions, and the audience has to decide which one is real.

From those lines Claude also creates the subtitles, three words at a time, colour coded. White is you, blue is your friend on the radio, and red is the thing in the woods.

## 6:40 — Step 5: Sound Effects and Music, Also Made in Code

This one surprised me most. Every sound effect is synthesised in code. The crickets that suddenly go silent. The bike chain clicking and the tyre skid. The buzz of a streetlight before it pops and the glass tinkling down. Radio static, the fence rattling, the creature's shriek.

The music is original too. Claude wrote an 80s-style synth score: an arpeggio during the ride, a dark drone when the woods start glowing, a big heavy hit when the creature appears, and then total silence on the freeze frame with just a heartbeat. It's not copied from any show. It's composed note by note in code.

Finally it mixes everything: the music ducks under the dialogue, and the whole thing is normalised to minus fourteen LUFS, the loudness Instagram, TikTok and YouTube expect.

## 7:30 — My Results

So I started my own page and posted original episodes: first a gas station thriller, where a girl runs in at two in the morning screaming "lock the door," and then a cop shows up saying *she's* the dangerous one. Then an 80s sci-fi horror about a kid on a BMX, a power plant and a signal in the woods.

Every video ends with a choice, and the comments decide Part 2. In the last thirty days my page got over three hundred and forty-nine thousand views, starting from zero, and every frame, voice and sound was made with Claude.

## 8:10 — How YOU Can Do It: The Skill

I turned this whole process into a Claude skill, so you don't have to figure it out yourself. Here's exactly how to use it.

**One — write your brief with Gemini.** Take my prompt, paste it into Gemini, and add your story idea in one line, like "a night-shift cashier hears knocking from the freezer." Gemini writes a full director's brief: characters, subtitle colours and a shot list with timings, dialogue and sound effects. Copy it.

**Two — download the skill.** It's a zip file with everything inside: the engine, the lens, the characters, the voice tools, the sound design and two complete example episodes.

**Three — upload it to Claude.** Open Claude, go to Customize, then Skills, click plus, and upload the zip. That's it, it's installed.

**Four — get your ElevenLabs key.** Go to ElevenLabs, open API Keys, and create a new key with text-to-speech turned on. Free plans can only use the default voices, and for commercial use you'll want a paid plan, so check that.

**Five — and this is important:** when Claude asks for the key, paste it into the secure form it shows you. Never paste your key into the chat.

**Six — paste your brief.** Claude reads it, plans the episode and shows you still frames and a short preview first. When you're happy, say yes, and it builds the full video: characters, camera, voices, subtitles, music and the end-screen choice. You also choose the format: nine by sixteen for Reels and TikTok, or sixteen by nine for YouTube.

## 9:30 — Tips Before You Post

A few tips from my own uploads. Keep it fast: no dead air, something new every couple of seconds. End on a freeze frame with two clear choices, and actually make Part 2 from the winning comment. People come back for that. Use a strong thumbnail with a question on it. And turn on Instagram's AI info label, because the voices are AI. Be honest about it, and always make your own characters and stories. Copy a style, never someone's characters.

## 10:00 — Outro

That's the whole system: one reference video, a skill, and your ideas. No editing software and no animation experience. You can get the skill and the prompt from my WhatsApp channel, or from the link in the description. If you make a video with it, tag me. I genuinely want to see what you create. Subscribe for more AI tools that actually do the work, and I'll see you in the next one.
