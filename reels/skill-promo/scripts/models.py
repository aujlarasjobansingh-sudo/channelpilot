"""Local speech models (free, offline): Kokoro TTS + Parakeet ASR + Silero VAD via sherpa-onnx.
Downloads from the sherpa-onnx GitHub releases on first use (Hugging Face is often blocked)."""
import os, subprocess, tarfile, urllib.request
MODELS = os.environ.get("TUT_MODELS", os.path.expanduser("~/models"))
REL = "https://github.com/k2-fsa/sherpa-onnx/releases/download"
NEED = {
    "kokoro-multi-lang-v1_0": f"{REL}/tts-models/kokoro-multi-lang-v1_0.tar.bz2",
    "sherpa-onnx-nemo-parakeet-tdt-0.6b-v2-int8": f"{REL}/asr-models/sherpa-onnx-nemo-parakeet-tdt-0.6b-v2-int8.tar.bz2",
}
def ensure(name):
    os.makedirs(MODELS, exist_ok=True)
    if name == "silero_vad.onnx":
        p = os.path.join(MODELS, name)
        if not os.path.exists(p): urllib.request.urlretrieve(f"{REL}/asr-models/silero_vad.onnx", p)
        return p
    d = os.path.join(MODELS, name)
    if not os.path.isdir(d):
        tb = d + ".tar.bz2"
        if not os.path.exists(tb): subprocess.run(["curl", "-L", "-o", tb, NEED[name]], check=True)
        with tarfile.open(tb) as t: t.extractall(MODELS)
    return d

def tts_engine(threads=2, extra_lexicon=None):
    import sherpa_onnx
    M = ensure("kokoro-multi-lang-v1_0")
    lex = f"{M}/lexicon-us-en.txt,{M}/lexicon-gb-en.txt"
    if extra_lexicon: lex = extra_lexicon + "," + lex     # your own pronunciations first
    cfg = sherpa_onnx.OfflineTtsConfig(model=sherpa_onnx.OfflineTtsModelConfig(kokoro=sherpa_onnx.OfflineTtsKokoroModelConfig(
        model=f"{M}/model.onnx", voices=f"{M}/voices.bin", tokens=f"{M}/tokens.txt", data_dir=f"{M}/espeak-ng-data",
        dict_dir=f"{M}/dict", lexicon=lex, lang="en-us"), num_threads=threads))
    return sherpa_onnx.OfflineTts(cfg)

def asr_engine(threads=2):
    import sherpa_onnx
    M = ensure("sherpa-onnx-nemo-parakeet-tdt-0.6b-v2-int8")
    return sherpa_onnx.OfflineRecognizer.from_transducer(encoder=f"{M}/encoder.int8.onnx", decoder=f"{M}/decoder.int8.onnx",
        joiner=f"{M}/joiner.int8.onnx", tokens=f"{M}/tokens.txt", model_type="nemo_transducer", num_threads=threads)

# Kokoro speaker ids (v1.0 multi-lang)
VOICES = {"michael": 16, "adam": 11, "eric": 13, "liam": 15, "fenrir": 14, "onyx": 17, "george": 26, "lewis": 27,
          "daniel": 24, "heart": 3, "bella": 2, "emma": 21}
