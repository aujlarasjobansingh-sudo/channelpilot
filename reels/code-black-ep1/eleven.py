"""Code Black Episode 1 dialogue with ElevenLabs (eleven_v4 + audio tags) -> voices_rec/<id>.wav
The API key is injected by the session's network proxy (no key in code).
Usage: python3 eleven.py [ids...]   (default: all lines)
"""
import os, sys, json, subprocess, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'voices_rec'); os.makedirs(os.path.join(OUT, 'mp3'), exist_ok=True)
VOICE = {'you': 'iP95p4xoKVk53GoZ742B',     # Chris  — POV student
         'marcus': 'TX3LPaxmHKxFdv7VOQHJ',  # Liam   — young American guy
         'chloe': 'EXAVITQu4vr4xnSDxMaL',   # Sarah  — young American woman
         'pa': 'N2lVS1w4EtoT3dr4eOWO',      # Callum — cold voice over the PA
         'radio': 'onwK4e9ZLuTAKqWW03F9'}   # Daniel — tactical radio chatter
LINES = {
    'm1': ('marcus', '[whispers] [bored] Bro, if Chloe doesn\'t get back with the notes in two minutes, we\'re failing this test.'),
    'y1': ('you', '[confused] [quietly] Did you feel that?'),
    'pa': ('pa', '[dead calm] [cold] Attention, Oakridge High. Every exit is sealed. Cell towers are jammed. Stay in your classrooms, keep your hands visible, and nobody gets hurt.'),
    'm2': ('marcus', '[urgent] [shouting] Get down! Stay away from the windows!'),
    'y2': ('you', '[whispers] [terrified] Those aren\'t cops... who are they?'),
    'r1': ('radio', '[calm] [flat] Library\'s locked. Bring the breach kit.'),
    'm3': ('marcus', '[urgent whisper] They\'re gonna blow the front door. The back stairwell, we can slip out right now!'),
    'c1': ('chloe', '[crying] [desperate whisper] Guys?! Please, open it! I\'m locked out in the stairwell. [panicked] I hear them coming up!'),
    'y3': ('you', '[urgent] [frustrated] Marcus, let go, that\'s Chloe!'),
    'm4': ('marcus', '[urgent whisper] Wait! Look at the security monitor!'),
    'y4': ('you', '[horrified whisper] He\'s right behind her... she doesn\'t even see him.'),
    'c2': ('chloe', '[sobbing] [screaming] Please! Don\'t leave me out here! Open the door!'),
    'm5': ('marcus', '[terrified whisper] If you open that door, he shoots all of us. [voice breaking] If we don\'t... she\'s dead.'),
    'y5': ('you', '[quietly] [tense] Save Chloe and walk into an ambush... [long pause] [whispers] or stay quiet and let them breach the front?'),
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
