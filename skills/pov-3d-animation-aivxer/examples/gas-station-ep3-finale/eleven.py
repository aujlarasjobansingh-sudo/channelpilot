"""Gas Station Episode 3 (finale) dialogue with ElevenLabs (eleven_v4 + audio tags) -> voices_rec/<id>.wav
API key: see eleven_api.py. With no key it STOPS with NO_ELEVENLABS_KEY: ask the user, or use the free offline voices (voices.py).
Usage: python3 eleven.py [ids...]   (default: all lines)
"""
import os, sys
from eleven_api import get_key, tts, to_wav

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
get_key()
for lid in ids:
    spk, text = LINES[lid]
    mp3 = os.path.join(OUT, 'mp3', lid + '.mp3'); wav = os.path.join(OUT, lid + '.wav')
    tts(text, VOICE[spk], mp3)
    print(f'{lid} {spk:4s} {to_wav(mp3, wav):5.2f}s  {text}')
