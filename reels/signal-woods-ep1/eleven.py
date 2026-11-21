"""Generate Episode 1 dialogue with ElevenLabs (eleven_v4 + audio tags) -> voices_rec/<id>.wav
The API key is injected by the session's network proxy (no key in code).
Usage: python3 eleven.py [ids...]   (default: all lines)
"""
import os, sys, json, subprocess, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'voices_rec'); os.makedirs(os.path.join(OUT, 'mp3'), exist_ok=True)
VOICE = {'you': 'TX3LPaxmHKxFdv7VOQHJ',    # Liam — young American guy (POV teen)
         'leo': 'bIHbv24MWmeRgasZH58o',    # Will — Leo on the walkie-talkie
         'fake': 'bIHbv24MWmeRgasZH58o'}   # Will — the SAME voice for "Leo" in the woods (it mimics him)
LINES = {
    'l1': ('leo', '[laughing] Dude, tell me you didn\'t forget your dice bag again. Over.'),
    'l2': ('you', '[smiling] Relax, it\'s in my backpack. I\'m passing the old power plant now. Over.'),
    'l3': ('you', '[startled] What the—? [annoyed] Come on...'),
    'l4': ('you', '[nervous] Leo? Hey, did the power just go out at your house? Over.'),
    'l5': ('you', '[whispers] [terrified] What is that...?'),
    'l6': ('leo', '[panicked] [breathless] Hello?! Dude, are you there?! Something\'s in the woods! The lights are going crazy— I\'m running toward the fence!'),
    'l7': ('you', '[confused] [scared] Leo?! Wait, I thought you were at home!'),
    'l8': ('fake', '[yelling] [breathless] Hey! Over here! Please, help me get over the fence— it\'s right behind me!'),
    'l9': ('you', '[shouting] Leo, run! Climb over— I\'ll pull you up!'),
    'l10': ('fake', '[eerily calm] I can\'t... my leg\'s stuck. [urgent] You have to come through the hole in the fence. Hurry!'),
    'l11': ('leo', '[screaming] [terrified] DUDE! DON\'T MOVE! I\'m still locked in my basement— I never left my house! Whatever is standing in those woods... IT\'S NOT ME! RUN!'),
    'l12': ('fake', '[crying] [desperate] No! Don\'t listen to the radio— that thing MIMICS VOICES! I\'m really out here! Please don\'t leave me!'),
    'l13': ('you', '[quietly] [ominous] One of them is my best friend. [long pause] The other one is a trap.'),
}
ids = sys.argv[1:] or list(LINES)
for lid in ids:
    spk, text = LINES[lid]
    body = json.dumps({'text': text, 'model_id': 'eleven_v4', 'voice_settings': {'stability': 0.5, 'similarity_boost': 0.8}}).encode()
    req = urllib.request.Request(f'https://api.elevenlabs.io/v1/text-to-speech/{VOICE[spk]}?output_format=mp3_44100_128',
                                 data=body, headers={'Content-Type': 'application/json', 'xi-api-key': 'proxy-injected'})
    mp3 = os.path.join(OUT, 'mp3', lid + '.mp3')
    with urllib.request.urlopen(req, timeout=120) as r, open(mp3, 'wb') as f: f.write(r.read())
    wav = os.path.join(OUT, lid + '.wav')
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', mp3, '-ar', '48000', '-ac', '1', wav], check=True)
    dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', wav], capture_output=True, text=True).stdout)
    print(f'{lid} {spk:4s} {dur:5.2f}s  {text}')
