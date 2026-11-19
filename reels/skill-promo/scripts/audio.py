import numpy as np, soundfile as sf, json, sys, subprocess
SR = 48000
rng = np.random.default_rng(7)

def db(x): return 10 ** (x / 20)
def env_adsr(n, a, r):
    e = np.ones(n); na = max(1, int(a * SR)); nr = max(1, int(r * SR))
    e[:na] = np.linspace(0, 1, na); e[-nr:] *= np.linspace(1, 0, nr) ** 2; return e
def lp(x, k):  # one-pole lowpass, k in (0,1)
    y = np.empty_like(x); acc = 0.0
    for i in range(len(x)): acc += k * (x[i] - acc); y[i] = acc
    return y
def lpf_fft(x, fc):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR); X *= 1 / (1 + (f / fc) ** 4); return np.fft.irfft(X, len(x))
def bpf_fft(x, lo, hi):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR)
    X *= (1 / (1 + (f / hi) ** 4)) * (1 / (1 + (lo / np.maximum(f, 1)) ** 4)); return np.fft.irfft(X, len(x))

def sfx(kind):
    if kind == "pop":
        n = int(.12 * SR); t = np.arange(n) / SR
        f = 900 * np.exp(-t * 18) + 380; ph = 2 * np.pi * np.cumsum(f) / SR
        return np.sin(ph) * np.exp(-t * 38) * db(-24)
    if kind == "click":
        n = int(.05 * SR); t = np.arange(n) / SR
        x = bpf_fft(rng.normal(0, 1, n), 1800, 6000) * np.exp(-t * 160)
        x += np.sin(2 * np.pi * 2400 * t) * np.exp(-t * 220) * .4
        return x / np.abs(x).max() * db(-26)
    if kind in ("whoosh", "whoosh_s"):
        L = .5 if kind == "whoosh" else .38; n = int(L * SR); t = np.arange(n) / SR
        x = rng.normal(0, 1, n)
        # sweep a band upward via segments
        out = np.zeros(n); seg = 2048
        for i in range(0, n, seg):
            k = i / n; c = 400 + 2600 * k ** 1.3
            out[i:i + seg] = bpf_fft(x[i:i + seg], c * .6, c * 1.6)[:len(out[i:i + seg])]
        e = np.sin(np.pi * np.clip(t / L, 0, 1)) ** 2
        out = out * e; out = out / np.abs(out).max()
        return out * db(-27 if kind == "whoosh" else -30)
    if kind == "type":
        n = int(.03 * SR); t = np.arange(n) / SR
        x = bpf_fft(rng.normal(0, 1, n), 2500, 8000) * np.exp(-t * 300)
        return x / np.abs(x).max() * db(-34)
    if kind == "ding":
        n = int(.6 * SR); t = np.arange(n) / SR
        x = (np.sin(2 * np.pi * 1318 * t) + .5 * np.sin(2 * np.pi * 1975 * t)) * np.exp(-t * 7)
        return x * db(-28)
    if kind == "rise":
        L = 1.2; n = int(L * SR); t = np.arange(n) / SR
        x = bpf_fft(rng.normal(0, 1, n), 300, 5000) * (t / L) ** 2 * np.exp(-((t - L) * 30).clip(0))
        return x / np.abs(x).max() * db(-30)
    raise KeyError(kind)

def music(dur):
    """soft lofi-ish pad + plucks, original"""
    bpm = 84; beat = 60 / bpm; bar = 4 * beat
    chords = [[48, 55, 59, 64], [45, 52, 55, 60], [41, 48, 52, 57], [43, 50, 53, 59]]  # Cmaj7 Am7 Fmaj7 G
    n = int(dur * SR) + SR; out = np.zeros(n)
    def mtof(m): return 440 * 2 ** ((m - 69) / 12)
    t_bar = 0.0; ci = 0
    while t_bar < dur + bar:
        ch = chords[ci % 4]; i0 = int(t_bar * SR); L = int(bar * SR)
        tt = np.arange(L) / SR
        pad = np.zeros(L)
        for m in ch:
            f = mtof(m + 12)
            pad += np.sin(2 * np.pi * f * tt + .3 * np.sin(2 * np.pi * .4 * tt)) + .3 * np.sin(2 * np.pi * f * 2.003 * tt)
        pad *= env_adsr(L, .6, .7) * .05
        seg = out[i0:i0 + L]; seg += pad[:len(seg)]
        # plucks: arpeggio 8ths
        for k in range(8):
            if k in (3, 7): continue
            m = ch[[0, 2, 3, 1, 2, 3, 1, 2][k]] + 24
            j0 = i0 + int(k * beat / 2 * SR); pl = int(.5 * SR); tp = np.arange(pl) / SR
            p = np.sin(2 * np.pi * mtof(m) * tp) * np.exp(-tp * 9) * .045
            s2 = out[j0:j0 + pl]; s2 += p[:len(s2)]
        # soft kick + hat
        for k in range(4):
            j0 = i0 + int(k * beat * SR); kl = int(.25 * SR); tk = np.arange(kl) / SR
            kick = np.sin(2 * np.pi * (50 + 60 * np.exp(-tk * 30)) * tk) * np.exp(-tk * 14) * (.10 if k % 2 == 0 else .0)
            s3 = out[j0:j0 + kl]; s3 += kick[:len(s3)]
            hj = j0 + int(beat / 2 * SR); hl = int(.05 * SR)
            hat = bpf_fft(rng.normal(0, 1, hl), 6000, 12000) * np.exp(-np.arange(hl) / SR * 120) * .03
            s4 = out[hj:hj + hl]; s4 += hat[:len(s4)]
        t_bar += bar; ci += 1
    out = out[:int(dur * SR)].astype(np.float32)
    ch = SR * 20
    for i in range(0, len(out), ch):
        out[i:i + ch] = lpf_fft(out[i:i + ch].astype(np.float64), 5000)[:len(out[i:i + ch])]
    return out / (np.abs(out).max() + 1e-9)

def build(dur, voices, sfx_list, out_path, music_ranges=None, music_db=-30, duck_db=-8, clips_audio=()):
    """voices: list of (out_t, wav, src_t0, src_t1); clips_audio: (out_t, wav_path, gain_db) full-level inserts that mute music"""
    n = int(dur * SR); v = np.zeros((n, 2), np.float32); fx = np.zeros(n, np.float32); ins = np.zeros((n, 2), np.float32)
    cache = {}
    for out_t, wav, a, b in voices:
        if wav not in cache:
            s, sr = sf.read(wav, dtype="float32"); assert sr == SR
            if s.ndim == 1: s = np.stack([s, s], 1)
            cache[wav] = s
        s = cache[wav][int(a * SR):int(b * SR)]
        i = int(out_t * SR); L = min(len(s), n - i)
        fade = np.ones(L); f = min(L, int(.01 * SR)); fade[:f] = np.linspace(0, 1, f); fade[-f:] = np.linspace(1, 0, f)
        v[i:i + L] += s[:L] * fade[:, None]
    for out_t, wav, g in clips_audio:
        s, sr = sf.read(wav, dtype="float32")
        if s.ndim == 1: s = np.stack([s, s], 1)
        i = int(out_t * SR); L = min(len(s), n - i); ins[i:i + L] += s[:L] * db(g)
    for t, kind, g in sfx_list:
        x = sfx(kind) * g; i = int(t * SR)
        if i < 0 or i >= n: continue
        L = min(len(x), n - i); fx[i:i + L] += x[:L]
    # voice loudness to approx -16 LUFS-ish via RMS of active parts
    act = np.abs(v[:, 0]) > 0.01
    if act.any():
        r = np.sqrt(np.mean(v[act, 0] ** 2)); v *= db(-19) / r
    out = v + fx[:, None] + ins
    if music_ranges is not None:
        m = music(dur) * np.float32(db(music_db))
        hop = 480; nh = (n + hop - 1) // hop
        gate = np.zeros(nh)
        for a, b in music_ranges: gate[int(a * SR / hop):int(b * SR / hop)] = 1
        e = np.abs(v[:, 0]); pad = np.zeros(nh * hop, np.float32); pad[:n] = e
        ee = (pad.reshape(nh, hop).max(1) > 0.02).astype(float)
        ee = np.convolve(ee, np.ones(25) / 25, mode="same")
        g = gate * (1 - (1 - db(duck_db)) * ee)
        g = np.convolve(g, np.ones(5) / 5, mode="same")
        gs = np.interp(np.arange(n) / hop, np.arange(nh), g).astype(np.float32)
        out += (m * gs)[:, None]
        del m, gs
    peak = np.abs(out).max()
    if peak > 0.98: out *= 0.98 / peak
    sf.write(out_path + ".raw.wav", out, SR)
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", out_path + ".raw.wav", "-af",
                    "loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", str(SR), out_path], check=True)
