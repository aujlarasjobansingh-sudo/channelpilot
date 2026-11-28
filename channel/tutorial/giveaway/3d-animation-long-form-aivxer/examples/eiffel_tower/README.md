> Part of the **3D Animation Long Form** skill, made by **aivxer**. Copyright (c) 2026 aivxer.

# Example project: "The Man Who Sold the Eiffel Tower" (1:56)

Made by aivxer, using the Claude 2D Animation Long Form skill.

These are the actual scripts that rendered the sample video. They are a reference
for the skill; paths inside them point to /home/claude/vid and /home/claude/models,
so change those to your own folders before running.

Order:
1. tts3.py            voices for the 21 s intro
2. scenes3.py render 0 1 2 3 4 5 6 7     intro shots
3. audio_mix3.py      intro audio
4. long.py tts        voices for the rest of the story
5. long.py render 0 2 and long.py render 1 2   remaining shots (two processes)
6. long.py audio      full audio, then loudnorm to -14 LUFS and mux (see SKILL.md)

kit3.py is the character + lighting kit (also embedded in SKILL.md).
