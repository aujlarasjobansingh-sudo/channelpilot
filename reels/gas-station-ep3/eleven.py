"""Gas Station Episode 3 (finale) dialogue with ElevenLabs (eleven_v4 + audio tags) -> voices_rec/<id>.wav
The API key is injected by the session's network proxy (no key in code).
Usage: python3 eleven.py [ids...]   (default: all lines)
"""
import os, sys, json, subprocess, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'voices_rec'); os.makedirs(os.path.join(OUT, 'mp3'), exist_ok=True)
VOICE = {'you': 'iP95p4xoKVk53GoZ742B',    # Chris — same POV voice as Ep1/Ep2
         'cop': 'nPczCjzI2devNBz1zQrb',    # Brian — the fake officer (same as Ep2)
         'sam': 'bIHbv24MWmeRgasZH58o',    # Will  — the man in the backseat (same voice as Ep2's car)
         'mega': 'JBFqnCBsd6RMkjVDRZzb'}   # George — real police on the megaphone
LINES = {
    'y1': ('you', '[panicked] [shouting] Get out! [desperate] Come on, run!'),
    's1': ('sam', '[gasping] [frantic] Thank god— [panicked] he\'s right behind us! Move!'),
    'c1': ('cop', '[yelling] [furious] STOP! GET BACK HERE!'),
    'y2': ('you', '[panting] [hopeful] A car! [excited] We can flag them down!'),
    's2': ('sam', '[catching his breath] [uneasy] Wait... [low voice] don\'t step into the road yet.'),
    'y3': ('you', '[confused] [out of breath] Wait... why did he stop chasing us?'),
    'y4': ('you', '[terrified] [whispers] You... [shaky] you were never locked in that car.'),
    's3': ('sam', '[dead calm] [cold] The back doors don\'t open from the inside, kid. [smiling] [menacing] I just needed someone stupid enough to pull the handle.'),
    's4': ('sam', '[alarmed] [urgent] Great. [aggressive] Get up— we\'re going into the woods. NOW!'),
    'mg': ('mega', '[shouting] [commanding] DROP THE WEAPON!'),
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
