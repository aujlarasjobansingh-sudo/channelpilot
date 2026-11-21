"""preview.py <scene id> [fractions e.g. .3,.7]  -> shots/prev_<id>_<f>.png stills to look at BEFORE rendering"""
import sys, os, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
ROOT = os.environ.setdefault("TUT_ROOT", os.getcwd())
import comps
from eng import still
spec = importlib.util.spec_from_file_location("scenes", os.path.join(ROOT, "scenes.py")); S = importlib.util.module_from_spec(spec)
sys.path.insert(0, ROOT); spec.loader.exec_module(S)
ids = sys.argv[1].split(","); fr = [float(x) for x in (sys.argv[2] if len(sys.argv) > 2 else ".35,.85").split(",")]
os.makedirs(f"{ROOT}/shots", exist_ok=True)
for sid, a, b, fn in S.SCENES:
    if sid not in ids: continue
    r = fn(a, b - a)
    for f in fr:
        p = f"{ROOT}/shots/prev_{sid}_{int(f * 100):02d}.png"; still(p, (b - a) * f, r[1], r[0]); print(p)
    for v in (r[2] if len(r) > 2 else []): v.close()
    comps.SF.clear()
