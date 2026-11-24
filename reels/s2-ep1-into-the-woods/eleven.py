"""Season 2 Episode 1 dialogue with ElevenLabs (eleven_v4 + audio tags) -> voices_rec/<id>.wav
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
    'mg': ('mega', '[shouting] [commanding] STOP! POLICE!'),
    's1': ('sam', '[breathless] [aggressive] Keep moving! [threatening] Don\'t look back, or I swear I\'ll pull the trigger!'),
    'y1': ('you', '[gasping] [desperate] Please, just let me go! [pleading] I didn\'t see anything!'),
    's2': ('sam', '[cold] [commanding] Shut up. Inside. Now!'),
    's3': ('sam', '[panting] [low voice] Sit on the floor. Hands on your head.'),
    'y2': ('you', '[cautious] [whispers] Who was that girl at the gas station? Why did your partner want her?'),
    's4': ('sam', '[cold] [quietly] She saw something she wasn\'t supposed to see. [menacing] Just like you.'),
    'c1': ('cop', '[authoritative] [shouting] Police! We know you\'re in there! Drop the weapon and send the kid out first!'),
    'y3': ('you', '[relieved] [excited] It\'s the cops! Let me go!'),
    's5': ('sam', '[frantic whisper] [scared] Stop! Listen! Where are the sirens? [terrified] There are no red and blue lights out there!'),
    'c2': ('cop', '[dead calm] [menacing] [low voice] Sam... you left my cruiser on the highway. Open the door, hand me the kid, and I\'ll forget you messed up.'),
    's6': ('sam', '[whispers] [terrified] He\'s lying. He never leaves witnesses. He\'s gonna shoot both of us the second that door opens. [urgent] Come with me into the tunnel!'),
    'c3': ('cop', '[shouting] [furious] Last chance, kid! Unlock the door and walk out. I only want Sam!'),
    'y4': ('you', '[quietly] [tense] Trust the killer outside... [long pause] [whispers] or crawl into the dark with the one who just held a gun to my head?'),
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
