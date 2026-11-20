"""Generate Episode 1 dialogue with ElevenLabs (eleven_v4 + audio tags) -> voices_rec/<id>.wav
The API key is injected by the session's network proxy (no key in code).
Usage: python3 eleven.py [ids...]   (default: all lines)
"""
import os, sys, json, subprocess, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'voices_rec'); os.makedirs(os.path.join(OUT, 'mp3'), exist_ok=True)
VOICE = {'you': 'iP95p4xoKVk53GoZ742B',    # Chris  — casual young American man
         'maya': 'cgSgspJ2msm6clMCkdW9',   # Jessica — expressive young American woman
         'cop': 'nPczCjzI2devNBz1zQrb',    # Brian  — deep, resonant American man
         'car': 'bIHbv24MWmeRgasZH58o'}    # Will   — young American man (voice in the car)
LINES = {
    'm1': ('maya', '[furious] [screaming] You idiot! [enraged] What did you just do?!'),
    'c1': ('cop', '[shouting] [commanding] Don\'t move! Drop the knife right now!'),
    'y1': ('you', '[panicked] [terrified] I\'m not with her! [desperate] She\'s right here!'),
    'c2': ('cop', '[groaning in pain] Argh! [angry] You psycho—!'),
    'y2': ('you', '[panting] [panicked] Screw this. [determined] I\'m out.'),
    'm2': ('maya', '[struggling] [screaming] Get off me!'),
    'y3': ('you', '[gasping for air] [out of breath] Just get to the highway... [panting] flag down a truck...'),
    'v1': ('car', '[screaming] [desperate] HEY! PLEASE! HELP ME! [panicked] HE LOCKED ME IN HERE!'),
    'y4': ('you', '[shocked whisper] Oh my god... [scared] who are you?!'),
    'v2': ('car', '[crying] [desperate] He pulled me over an hour ago! [sobbing] Please, open the door— [terrified] he\'s coming!'),
    'c3': ('cop', '[cold] [menacing] [low voice] Step away from my car.'),
    'y5': ('you', '[quietly] [tense] If I stop to free them, he shoots us both. [long pause] [whispers] If I run... I leave them to die.'),
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
