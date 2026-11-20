import sys, sherpa_onnx, numpy as np, subprocess, json, re, os
M = os.path.expanduser('~/models/sherpa-onnx-nemo-parakeet-tdt-0.6b-v2-int8')
rec = sherpa_onnx.OfflineRecognizer.from_transducer(encoder=f'{M}/encoder.int8.onnx', decoder=f'{M}/decoder.int8.onnx', joiner=f'{M}/joiner.int8.onnx',
                                                    tokens=f'{M}/tokens.txt', num_threads=4, model_type='nemo_transducer')
raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', sys.argv[1], '-ac', '1', '-ar', '16000', '-f', 's16le', '-'], capture_output=True).stdout
s = np.frombuffer(raw, np.int16).astype(np.float32) / 32768; SR = 16000
sil = [float(re.findall(r'[\d.]+', l)[0]) + .15 for l in open(sys.argv[2]) if re.findall(r'[\d.]+', l)]
cuts = [0.0]
for x in sil:
    if x - cuts[-1] > 18: cuts.append(x)
cuts.append(len(s) / SR)
words = []
for a, b in zip(cuts[:-1], cuts[1:]):
    st = rec.create_stream(); st.accept_waveform(SR, s[int(a * SR):int(b * SR)]); rec.decode_stream(st); r = st.result
    cur = None
    for tok, ts in zip(r.tokens, r.timestamps):
        if tok.startswith(' ') or cur is None:
            if cur: words.append(cur)
            cur = {'w': tok.strip(), 't': round(a + ts, 2)}
        else: cur['w'] += tok
    if cur: words.append(cur)
json.dump(words, open(sys.argv[3], 'w'), indent=0)
print(len(words)); print(' '.join(w['w'] for w in words)[:600])
