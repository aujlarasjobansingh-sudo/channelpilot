"""Generate the promo reel voice-over with ElevenLabs eleven_v4 (voice: Liam). Key is injected by the proxy."""
import json, os, subprocess, urllib.request
import numpy as np, soundfile as sf
HERE = os.path.dirname(os.path.abspath(__file__)); VOICE = 'TX3LPaxmHKxFdv7VOQHJ'   # Liam (ElevenLabs default voice)
LINES = [
    ('v1', '[excited] Want to make videos in this exact style? [confident] I built a skill for it.'),
    ('v2', '[upbeat] Step one: give Claude a single reference video.'),
    ('v3', '[impressed] It studies every scene: the lens, the camera moves, the timing.'),
    ('v4', '[enthusiastic] Then it rebuilds the whole world in 3D, scene by scene.'),
    ('v5', 'It matches the movement frame by frame, [satisfied] so it feels the same.'),
    ('v6', '[proud] And I packed it all into one skill. [excited] Any story, same style.'),
    ('v7', '[teasing] Here\'s the reference... [excited] and here\'s ours.'),
    ('v8', '[energetic] Comment SKILL and I\'ll send you the link.'),
]
os.makedirs(os.path.join(HERE, 'vo'), exist_ok=True)
for k, txt in LINES:
    body = json.dumps({'text': txt, 'model_id': 'eleven_v4', 'voice_settings': {'stability': 0.45, 'similarity_boost': 0.8, 'style': 0.35}}).encode()
    req = urllib.request.Request(f'https://api.elevenlabs.io/v1/text-to-speech/{VOICE}?output_format=mp3_44100_128', data=body,
                                 headers={'Content-Type': 'application/json', 'xi-api-key': 'proxy-injected'})
    mp3 = os.path.join(HERE, 'vo', k + '.mp3')
    with urllib.request.urlopen(req, timeout=120) as r, open(mp3, 'wb') as f: f.write(r.read())
    wav = os.path.join(HERE, 'vo', k + '.wav')
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', mp3, '-ar', '48000', '-ac', '1', wav], check=True)
    a, sr = sf.read(wav); e = np.where(np.abs(a) > 0.02)[0]; a = a[max(0, e[0] - 480): e[-1] + 1800]; sf.write(wav, a, sr)
    print(k, f'{len(a) / sr:.2f}s', txt)
