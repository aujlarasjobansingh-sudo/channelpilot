"""Generate Episode 1 dialogue with ElevenLabs (eleven_v3 + audio tags) -> voices_rec/<id>.wav
The API key is injected by the session's network proxy (no key in code).
Usage: python3 eleven.py [ids...]   (default: all lines)
"""
import os, sys, json, subprocess, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'voices_rec'); os.makedirs(os.path.join(OUT, 'mp3'), exist_ok=True)
VOICE = {'you': 'iP95p4xoKVk53GoZ742B',    # Chris  — casual young American man
         'maya': 'cgSgspJ2msm6clMCkdW9',   # Jessica — expressive young American woman
         'cop': 'nPczCjzI2devNBz1zQrb'}    # Brian  — deep, resonant American man
LINES = {
    'l01': ('you', '[sighs] Dead quiet. Just me and the crickets.'),
    'l02': ('maya', '[panicked] [breathless] Lock it! Please, hit the lock right now!'),
    'l03': ('you', '[startled] Whoa, hey, slow down! What\'s going on?'),
    'l04': ('maya', '[terrified] [out of breath] A guy in a black sedan followed me for three miles. He saw me run in here. Lock the door!'),
    'l05': ('you', '[trying to stay calm] Okay, it\'s locked. You\'re safe. I\'m calling nine-one-one—'),
    'l06': ('you', '[relieved] Wait, you\'re good. A cop just pulled into the lot.'),
    'l07': ('maya', '[whispers] [terrified] No. No, no, no... that\'s NOT a real cop.'),
    'l08': ('you', '[confused] What? He\'s in a cruiser—'),
    'l09': ('maya', '[whispers] [urgent] Look at the roof. There\'s no unit number. He\'s the one who was chasing me.'),
    'l10': ('cop', '[shouting] Police! Open the door! Is there a girl in a grey hoodie in there?'),
    'l11': ('maya', '[whispers] [frantic] Don\'t open it! Look at his belt, he doesn\'t even have a radio. If you unlock that door, we\'re both dead.'),
    'l12': ('cop', '[yelling] Sir, step away from her right now! She just attacked a clerk at the Shell station two miles up. She\'s armed!'),
    'l13': ('you', '[whispers] [shocked] Wait... what?'),
    'l14': ('you', '[cautious] Hey... what\'s in your pocket?'),
    'l15': ('maya', '[crying] [desperate] It\'s just my house keys! Please, don\'t listen to him!'),
    'l16': ('you', '[exhales] Holy crap... she\'s telling the truth.'),
    'l17': ('cop', '[yelling] [threatening] Last chance! Unlock the door!'),
    'l18': ('maya', '[calm] [cold] Don\'t touch that button.'),
    'l19': ('you', '[quietly] [ominous] One of them is lying. Or... both of them are.'),
}
ids = sys.argv[1:] or list(LINES)
for lid in ids:
    spk, text = LINES[lid]
    body = json.dumps({'text': text, 'model_id': 'eleven_v3', 'voice_settings': {'stability': 0.5, 'similarity_boost': 0.8}}).encode()
    req = urllib.request.Request(f'https://api.elevenlabs.io/v1/text-to-speech/{VOICE[spk]}?output_format=mp3_44100_128',
                                 data=body, headers={'Content-Type': 'application/json', 'xi-api-key': 'proxy-injected'})
    mp3 = os.path.join(OUT, 'mp3', lid + '.mp3')
    with urllib.request.urlopen(req, timeout=120) as r, open(mp3, 'wb') as f: f.write(r.read())
    wav = os.path.join(OUT, lid + '.wav')
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', mp3, '-ar', '48000', '-ac', '1', wav], check=True)
    dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', wav], capture_output=True, text=True).stdout)
    print(f'{lid} {spk:4s} {dur:5.2f}s  {text}')
