"""Generate Episode 1 dialogue with ElevenLabs (eleven_v4 + audio tags) -> voices_rec/<id>.wav
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
    'l01': ('you', '[tired] [sighs heavily] Dead quiet. [bored] Just me and the crickets.'),
    'l02': ('maya', '[gasping for air] [screaming in panic] Lock it! [desperate] Please, hit the lock right now!'),
    'l03': ('you', '[startled] [raising voice] Whoa, hey, slow down! [confused] What\'s going on?'),
    'l04': ('maya', '[panting] [terrified] A guy in a black sedan followed me for three miles. [voice shaking] He saw me run in here. [shouting desperately] Lock the door!'),
    'l05': ('you', '[nervous] [trying to stay calm] Okay, it\'s locked. You\'re safe. [hurried] I\'m calling nine-one-one—'),
    'l06': ('you', '[relieved] [exhales] Wait, you\'re good. [reassuring] A cop just pulled into the lot.'),
    'l07': ('maya', '[whispers] [terrified] No. [voice trembling] No, no, no... [horrified whisper] that\'s NOT a real cop.'),
    'l08': ('you', '[confused] [skeptical] What? He\'s in a cruiser—'),
    'l09': ('maya', '[urgent whisper] Look at the roof. There\'s no unit number. [shaky breath] [whispers] He\'s the one who was chasing me.'),
    'l10': ('cop', '[shouting] [authoritative] Police! Open the door! [demanding] Is there a girl in a grey hoodie in there?'),
    'l11': ('maya', '[frantic whisper] Don\'t open it! Look at his belt, he doesn\'t even have a radio. [voice breaking] [whispers] If you unlock that door, we\'re both dead.'),
    'l12': ('cop', '[yelling] [aggressive] Sir, step away from her right now! [urgent] She just attacked a clerk at the Shell station two miles up. [shouting] She\'s armed!'),
    'l13': ('you', '[shocked whisper] Wait... [stunned] what?'),
    'l14': ('you', '[suspicious] [slowly] Hey... [tense] what\'s in your pocket?'),
    'l15': ('maya', '[crying] [sniffles] It\'s just my house keys! [sobbing] [pleading] Please, don\'t listen to him!'),
    'l16': ('you', '[exhales in relief] [shaky laugh] Holy crap... [breathless] she\'s telling the truth.'),
    'l17': ('cop', '[yelling] [menacing] Last chance! [furious] Unlock the door!'),
    'l18': ('maya', '[emotionless] [cold] [low voice] Don\'t touch that button.'),
    'l19': ('you', '[quietly] [ominous] One of them is lying. [long pause] [whispers] Or... both of them are.'),
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
