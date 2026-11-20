# Maps real voiceover time <-> the shot-design timeline, using ASR word timestamps.
# Each anchor: (design_time, phrase, nth_occurrence_from_pointer offset, extra_seconds)
import json, os, re
import numpy as np
WORDS = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../ep01/audio/asr/words.json')))
def norm(s): return re.sub(r'[^a-z0-9]', '', s.lower())
NW = [norm(w['w']) for w in WORDS]

ANCHORS = [
    (0.0, None), (2.1, 'giant monsters'), (4.95, 'where heroes'), (7.45, 'and every 18yearold'), (11.3, 'and your number'), (12.74, 'zero'),
    (14.05, 'everyone calls'), (16.95, 'your own rank'), (18.56, 'the news'), (19.87, 'even the kids'), (22.10, 'but theres'),
    (25.44, 'and by the end'), (26.77, 'the strongest'), (30.84, 'before we start'), (34.73, 'every week we'), (38.80, 'now lets'),
    (39.97, 'in this world'), (42.85, 'they come out'), (44.54, 'nobody knows'), (46.95, 'scientists call'), (49.27, 'everyone else'),
    (51.59, 'some are the size of a dog'), (53.48, 'some are the size of a building'), (55.52, 'and every single one'), (59.29, 'ember level'),
    (63.49, 'storm level'), (67.38, 'quake level'), (69.66, 'eclipse level'), (72.43, 'and extinction'), (77.04, 'the last one'),
    (82.22, 'so the world'), (84.24, 'the bureau of registered'), (89.47, 'it trains'), (92.69, 'importantly'), (95.64, 'hero merchandise'),
    (99.54, 'in meridian'), (102.37, 'and every hero has'), (104.90, 'iron is the'), (108.22, 'bronze and'), (111.08, 'gold heroes'),
    (113.76, 'and crown'), (116.81, 'so how does'), (122.15, 'simple'), (125.42, 'you walk into'), (130.69, 'it reads'),
    (135.40, 'score above 100'), (139.64, 'score above 500'), (142.71, 'score above 900'), (146.92, 'that number is'), (150.88, 'which brings'),
    (154.42, 'four years ago'), (159.51, 'you were wearing'), (163.83, 'youd drawn'), (169.75, 'you put your hand'), (173.57, 'the lights started'),
    (177.47, 'zero'), (178.49, 'not five'), (180.83, 'the technician'), (182.84, 'he said'), (186.28, 'he even took'), (188.45, 'by the next'),
    (191.55, 'people made memes'), (195.50, 'the bureau still'), (203.47, 'the very last'), (207.89, 'so for four'), (211.11, 'you help old'),
    (213.79, 'you get cats'), (215.67, 'once you spent'), (217.43, 'and every day'), (222.84, 'hey zero'), (224.35, 'careful zero'),
    (226.14, 'you smile'), (230.85, 'because heres'), (236.13, 'every time someone'), (239.02, 'like something'), (242.55, 'you always thought'),
    (244.45, 'you were wrong'), (245.73, 'its a tuesday'), (249.46, 'then the floor'), (250.66, 'explodes'), (254.52, 'explodes'), (256.55, 'a storm level'),
    (259.63, 'the kind that'), (261.16, 'alarms are'), (263.62, 'people are running'), (267.10, 'and the nearest'), (269.56, 'you check your'),
    (272.89, 'nine minutes'), (276.65, 'in nine minutes'), (280.65, 'the monster turns'), (284.27, 'it sees'), (285.62, 'it opens'),
    (288.58, 'you dont think'), (292.11, 'you jump'), (294.09, 'the monsters claw'), (297.18, 'and as you raise'), (302.14, 'get out'),
    (305.00, 'and your hands'), (306.85, 'no not warm'), (308.84, 'they burn'),
]
LEAD = 0.12   # cut slightly before the first word

def _find(phrase, start):
    ps = [norm(p) for p in phrase.split()]
    for i in range(start, len(NW) - len(ps) + 1):
        if NW[i:i + len(ps)] == ps: return i
    joined = ''.join(ps)
    for i in range(start, len(NW)):
        acc = ''
        for j in range(i, min(i + 8, len(NW))):
            acc += NW[j]
            if acc == joined: return i
            if not joined.startswith(acc): break
    raise ValueError(f'phrase not found: {phrase} after word {start} ({WORDS[start]["t"]})')

OLD, NEW = [], []
_ptr = 0
for old, ph in ANCHORS:
    if ph is None: OLD.append(old); NEW.append(0.0); continue
    i = _find(ph, _ptr if old != 254.52 else _ptr - 1); _ptr = i + 1
    t = WORDS[i]['t'] - LEAD
    if old == 250.66: t = WORDS[i]['t'] + .05          # impact lands on "explodes"
    if old in (12.74, 177.47): t = WORDS[i]['t']       # the reveal hits right on "zero"
    OLD.append(old); NEW.append(t)
OLD.append(310.6); NEW.append(310.6)
OLD = np.array(OLD); NEW = np.array(NEW)
# hand-tuned around the explosion: the gap between "explodes" and "a storm level monster" is < 1 s
_ix = {o: i for i, o in enumerate(OLD)}
ex = NEW[_ix[250.66]]
NEW[_ix[254.52]] = ex + 1.25     # smoke clears
NEW[_ix[256.55]] = ex + 1.75     # monster rises during "a storm-level monster..."
NEW[_ix[259.63]] = NEW[_ix[261.16]] - 0.8   # short silver-badge insert right before "alarms"
assert np.all(np.diff(NEW) > 0.25), list(zip(OLD[1:][np.diff(NEW) <= .25], NEW[1:][np.diff(NEW) <= .25]))

def to_old(t): return float(np.interp(t, NEW, OLD))
def to_new(t): return float(np.interp(t, OLD, NEW))

if __name__ == '__main__':
    for o, n in zip(OLD, NEW): print(f'{o:7.2f} -> {n:7.2f}  ({n - o:+.2f})')

# extra beats inside shots (design time -> real time)
for _o, _n in ((32.35, 33.95), (129.0, 129.35)):
    _k = int(np.searchsorted(OLD, _o)); OLD = np.insert(OLD, _k, _o); NEW = np.insert(NEW, _k, _n)
assert np.all(np.diff(NEW) > 0.25) and np.all(np.diff(OLD) > 0)
