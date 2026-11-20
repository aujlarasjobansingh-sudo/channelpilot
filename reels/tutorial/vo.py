"""Tutorial voice-over with ElevenLabs eleven_v4 (voice: Liam). Key is injected by the proxy / ELEVENLABS_API_KEY."""
import json, os, subprocess, urllib.request
import numpy as np, soundfile as sf
HERE = os.path.dirname(os.path.abspath(__file__)); VOICE = 'TX3LPaxmHKxFdv7VOQHJ'
LINES = [
    ('v1', '[excited] Claude made this entire horror short. [confident] Here\'s how you can too.'),
    ('v2', '[upbeat] Step one: download the skill.'),
    ('v3', 'Step two: in Claude, open Customize, then Skills, and upload the zip.'),
    ('v4', 'Step three: for the voices, go to ElevenLabs, open API Keys, and create a key with text to speech turned on.'),
    ('v5', 'Step four: when Claude asks for the key, paste it into the secure form. [serious] Never into the chat.'),
    ('v6', '[excited] Now just type your topic. Claude writes the script, shows you a preview, and builds the full video.'),
    ('v7', '[energetic] Comment SKILL and I\'ll send you the link.'),
]
for k, txt in LINES:
    body = json.dumps({'text': txt, 'model_id': 'eleven_v4', 'voice_settings': {'stability': 0.45, 'similarity_boost': 0.8, 'style': 0.35}}).encode()
    req = urllib.request.Request(f'https://api.elevenlabs.io/v1/text-to-speech/{VOICE}?output_format=mp3_44100_128', data=body,
                                 headers={'Content-Type': 'application/json', 'xi-api-key': os.environ.get('ELEVENLABS_API_KEY', 'proxy-injected')})
    mp3 = os.path.join(HERE, 'vo', k + '.mp3')
    with urllib.request.urlopen(req, timeout=120) as r, open(mp3, 'wb') as f: f.write(r.read())
    wav = os.path.join(HERE, 'vo', k + '.wav')
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', mp3, '-ar', '48000', '-ac', '1', wav], check=True)
    a, sr = sf.read(wav); e = np.where(np.abs(a) > 0.02)[0]; a = a[max(0, e[0] - 480): e[-1] + 1800]; sf.write(wav, a, sr)
    print(k, f'{len(a) / sr:.2f}s', txt)
