"""build.py [render|assemble|all] [scene ids, comma separated, to force re-render]
Reads $TUT_ROOT/scenes.py, which defines:
  VO = "vo/vo48.wav"                                   # voiceover (from prep_voice.py)
  SCENES = [("s01", 0.0, 9.25, builder), ...]         # voiceover source times, back to back, cut in silences
  INSERTS = [dict(id="x1", after=324.55, path="...mp4", dur=20.0, label="Sample 1", color="#d97757")]  # optional
  OUT = "out/final.mp4"                                # optional
  MUSIC_DB = -30                                       # optional quiet bed; None = no music
A builder(T0, D) returns (cam, draw[, videos_to_close[, render_kwargs]]) and calls sfx(t, kind, gain) for sounds.
Shots go to shots/<id>.mp4; unchanged shots are reused, so re-render only what you edit."""
import sys, os, json, time, subprocess, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
ROOT = os.environ.setdefault("TUT_ROOT", os.getcwd())
import comps
from eng import render
from audio import build as build_audio, SR
spec = importlib.util.spec_from_file_location("scenes", os.path.join(ROOT, "scenes.py")); S = importlib.util.module_from_spec(spec)
sys.path.insert(0, ROOT); spec.loader.exec_module(S)
INS = getattr(S, "INSERTS", []); GAP = 0.5
os.makedirs(f"{ROOT}/shots", exist_ok=True); os.makedirs(f"{ROOT}/out", exist_ok=True)

def order():
    seq = []; ins = sorted(INS, key=lambda d: d["after"])
    for sid, a, b, fn in S.SCENES:
        seq.append(("vo", sid, a, b, fn))
        for d in ins:
            if abs(d["after"] - b) < 0.02: seq.append(("ins", d["id"], 0.0, d["dur"] + 2 * GAP, d))
    return seq

def render_all(force=()):
    for kind, sid, a, b, x in order():
        out = f"{ROOT}/shots/{sid}.mp4"
        if os.path.exists(out) and sid not in force: continue
        comps.SF.clear(); t0 = time.time()
        r = x(a, b - a) if kind == "vo" else comps.insert_scene(x["path"], x["dur"], x["label"], x.get("color", "#d97757"), GAP)
        kw = r[3] if len(r) > 3 else {}
        render(out, b - a, r[1], r[0], **kw)
        for v in (r[2] if len(r) > 2 else []): v.close()
        json.dump(comps.SF, open(f"{ROOT}/shots/{sid}.sfx.json", "w"))
        print(f"{sid}: {b - a:.1f}s rendered in {time.time() - t0:.0f}s", flush=True)

def nframes(p):
    r = subprocess.run(["ffprobe", "-v", "error", "-count_packets", "-select_streams", "v", "-show_entries", "stream=nb_read_packets", "-of", "csv=p=0", p], capture_output=True, text=True)
    return int(r.stdout.strip())

def assemble():
    t = 0.0; voices = []; fx = []; clips = []; music = []; lst = []; vo = os.path.join(ROOT, getattr(S, "VO", "vo/vo48.wav"))
    chapters = []
    for kind, sid, a, b, x in order():
        p = f"{ROOT}/shots/{sid}.mp4"; d = nframes(p) / 30.0; lst.append(f"file '{p}'\n")
        if kind == "vo":
            voices.append((t, vo, a, a + d)); music.append((t, t + d))
        else:
            w = f"{ROOT}/shots/{sid}_a.wav"
            subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", x["path"], "-vn", "-ar", str(SR), "-ac", "2", w], check=True)
            clips.append((t + GAP, w, -4.0))
        fx += [(t + s, k, g) for s, k, g in json.load(open(f"{ROOT}/shots/{sid}.sfx.json"))]
        chapters.append(f"{int(t // 60)}:{int(t % 60):02d} {sid}")
        t += d
    open(f"{ROOT}/shots/list.txt", "w").write("".join(lst))
    mr = []
    for a, b in music:
        if mr and abs(mr[-1][1] - a) < .05: mr[-1] = (mr[-1][0], b)
        else: mr.append((a, b))
    mdb = getattr(S, "MUSIC_DB", -30)
    build_audio(t, voices, fx, f"{ROOT}/shots/audio.wav", music_ranges=mr if mdb is not None else None, music_db=mdb or -30, clips_audio=clips)
    subprocess.run(f"ffmpeg -loglevel error -y -f concat -safe 0 -i {ROOT}/shots/list.txt -c copy {ROOT}/shots/video.mp4", shell=True, check=True)
    out = os.path.join(ROOT, getattr(S, "OUT", "out/final.mp4"))
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", f"{ROOT}/shots/video.mp4", "-i", f"{ROOT}/shots/audio.wav", "-map", "0:v", "-map", "1:a",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", out], check=True)
    for f in ("audio.wav.raw.wav",):
        if os.path.exists(f"{ROOT}/shots/{f}"): os.remove(f"{ROOT}/shots/{f}")
    print("\n".join(chapters)); print(f"done: {out}  ({t:.1f}s)")

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "all"
    force = set(sys.argv[2].split(",")) if len(sys.argv) > 2 else set()
    if mode in ("render", "all"): render_all(force)
    if mode in ("assemble", "all"): assemble()
