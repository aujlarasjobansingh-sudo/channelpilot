"""ElevenLabs helper shared by every project's eleven.py. Finds the API key and explains every failure in plain words,
so Claude knows exactly what to ask the user. Never prints the key."""
import os, sys, json, subprocess, urllib.request, urllib.error

KEY_FILE = os.path.expanduser('~/.elevenlabs_key')

def get_key():
    k = os.environ.get('ELEVENLABS_API_KEY', '').strip()
    if not k and os.path.exists(KEY_FILE): k = open(KEY_FILE).read().strip()
    if not k and os.environ.get('ELEVENLABS_VIA_PROXY') == '1': k = 'proxy-injected'   # Claude Code cloud: key saved as a network secret
    if not k:
        print('NO_ELEVENLABS_KEY\n'
              'STOP and ask the user for their ElevenLabs API key (ElevenLabs -> Developers/API Keys -> Create key, with Text to Speech enabled).\n'
              ' - Claude Code on the web: ask them to save it as a network secret for api.elevenlabs.io (header xi-api-key), then run with ELEVENLABS_VIA_PROXY=1.\n'
              ' - Claude.ai / desktop chat: suggest a key restricted to Text to Speech with a low credit limit; save it with\n'
              '     python3 -c "import os;open(os.path.expanduser(\'~/.elevenlabs_key\'),\'w\').write(input())"   (never echo it back, never put it in a file you share)\n'
              '   and make sure Settings -> Capabilities -> code execution network access allows api.elevenlabs.io.\n'
              ' - No key: use the free offline voices (python3 voices.py works without eleven.py).', file=sys.stderr)
        sys.exit(2)
    return k

def tts(text, voice_id, out_mp3, model='eleven_v4', stability=0.5, similarity=0.8):
    body = json.dumps({'text': text, 'model_id': model, 'voice_settings': {'stability': stability, 'similarity_boost': similarity}}).encode()
    req = urllib.request.Request(f'https://api.elevenlabs.io/v1/text-to-speech/{voice_id}?output_format=mp3_44100_128', data=body,
                                 headers={'Content-Type': 'application/json', 'xi-api-key': get_key()})
    try:
        with urllib.request.urlopen(req, timeout=120) as r, open(out_mp3, 'wb') as f: f.write(r.read())
    except urllib.error.HTTPError as e:
        msg = e.read().decode(errors='ignore')[:300]
        if e.code in (401, 403):
            sys.exit(f'ELEVENLABS_AUTH_ERROR {e.code}: the key is wrong, expired, or lacks Text to Speech permission (or the voice is not available on this plan; '
                     f'free plans can only use default voices over the API). Ask the user to check the key. Details: {msg}')
        if e.code == 429: sys.exit('ELEVENLABS_QUOTA: out of credits or too many requests. Ask the user to check their ElevenLabs credits.')
        if e.code == 400 and 'model' in msg: return tts(text, voice_id, out_mp3, model='eleven_multilingual_v2', stability=stability, similarity=similarity)
        sys.exit(f'ELEVENLABS_HTTP_{e.code}: {msg}')
    except urllib.error.URLError as e:
        sys.exit(f'ELEVENLABS_NETWORK_BLOCKED: cannot reach api.elevenlabs.io ({e.reason}). In Claude.ai ask the user to allow api.elevenlabs.io '
                 'in Settings -> Capabilities (code execution network access), then retry. Or use the free offline voices.')

def to_wav(mp3, wav):
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', mp3, '-ar', '48000', '-ac', '1', wav], check=True)
    import soundfile as sf
    return sf.info(wav).duration
