# Part 2 music (procedural), timed to ASR words of vo_part2.mp3
import sys, os, math, numpy as np, soundfile as sf
src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../ep01/audio/make_score.py')).read()
exec(src.split("put(music, 0.0, pulse(")[0].replace('DUR = 311.0', 'DUR = 279.0'))
sys.argv = ['x']; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import json, re
W = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../ep01/audio/asr/words_p2.json')))
def at(ph, after=-1):
    ps = [re.sub(r'[^a-z0-9]', '', p.lower()) for p in ph.split()]; nw = [re.sub(r'[^a-z0-9]', '', w['w'].lower()) for w in W]
    for i in range(len(nw)):
        if W[i]['t'] >= after and nw[i:i + len(ps)] == ps: return W[i]['t']
    raise ValueError(ph)
# 0 - 19 aftermath: wide awe pad + bells
chord_seq(0.0, [['D3', 'A3', 'E4', 'F4'], ['A#2', 'F3', 'D4', 'A4'], ['G2', 'D3', 'A#3', 'F4'], ['A2', 'E3', 'C#4', 'A4']], 4.8, 1500, .45)
for i, n in enumerate(['A5', 'F5', 'E5', 'D5']): put(music, 1 + i * 4.8, bell(note(n), 3, .5), .35)
# 19 - 29 silver arrives: comic mallet line
t0 = at('and then through')
for i, n in enumerate(['G4', 'B4', 'D5', 'G5', 'F5', 'D5', 'B4', 'G4'] * 2): put(music, t0 + i * .55, mallet(note(n), .9, .8), .4)
put(music, at('did i miss') - .1, mallet(note('C5'), 1.5), .5); put(music, at('did i miss') + .4, mallet(note('B4'), 1.5), .5)
# 29 - 53 funny part / news: light groove
t0 = at('heres the funny'); t1 = at('you sit on your bed')
b = 60 / 112
for k in range(int((t1 - t0) / b)):
    tt = t0 + k * b
    put(music, tt, mallet(note(['C4', 'E4', 'G4', 'E4', 'A3', 'C4', 'E4', 'C4', 'F3', 'A3', 'C4', 'A3', 'G3', 'B3', 'D4', 'B3'][k % 16]), .4, .7), .35, (-1) ** k * .3)
    if k % 2 == 0: put(music, tt, drum(.3, 60, 120, .4), .25)
# 53 - 69 night bed: soft piano
t0 = at('you sit on your bed')
for i, n in enumerate(['E4', 'G4', 'B4', 'A4', 'G4', 'E4', 'D4', 'E4', 'C4', 'E4', 'G4', 'F#4', 'E4', 'B3', 'E4', 'G4']): put(music, t0 + i * 1.0, piano(note(n), 2.5, .7), .45)
chord_seq(t0, [['E2', 'B2', 'G3'], ['C2', 'G2', 'E3'], ['A2', 'E3', 'C4'], ['B2', 'F#3', 'D#4']], 4.0, 900, .35)
# 69 - 106 experiments: bouncy comedic loop, cut on "nothing" and "the car does not move"
t0 = at('you spend the next'); t1 = at('and thats when')
stops = [at('nothing'), at('the car does not'), at('your cousin screams')]
b = 60 / 124
for k in range(int((t1 - t0) / b)):
    tt = t0 + k * b
    if any(s - .05 < tt < s + 1.1 for s in stops): continue
    put(music, tt, mallet(note(['C3', 'G3', 'C3', 'G3', 'F2', 'C3', 'G2', 'D3'][k % 8]), .35, .9), .45)
    if k % 4 == 2: put(music, tt, noise(.08, 'white') * env(int(.08 * SR), .001, .02), .2)
    if k % 8 == 0: put(music, tt, mallet(note(['E5', 'G5', 'A5', 'G5'][(k // 8) % 4]), .6, .6), .3)
for s in stops: put(music, s, bell(note('C6'), 1.2, .4), .25)
# 106 - 157 realization: pads build, riser into "that was a crowd", epic chords
t0 = at('and thats when'); tc = at('that was a crowd')
chord_seq(t0, [['A2', 'E3', 'A3', 'C4'], ['F2', 'C3', 'A3', 'C4'], ['C3', 'G3', 'C4', 'E4'], ['G2', 'D3', 'B3', 'D4']], (tc - t0) / 4, 1200, .45)
put(music, tc - 3.0, riser(3.0, 150, 2400), .4); put(music, tc, drum(2.5, 40, 90, 1.0), .9)
t2 = at('you should feel')
chord_seq(tc, [['D3', 'A3', 'D4', 'F#4'], ['B2', 'F#3', 'B3', 'D4'], ['G2', 'D3', 'G3', 'B3'], ['A2', 'E3', 'A3', 'C#4']] * 2, (t2 - tc) / 8, 2000, .5)
for k in range(int((t2 - tc) / .5)):
    if k % 2 == 0: put(music, tc + k * .5, drum(.6, 50, 110, .6), .35)
# 158 - 167 cold thought: low drone
t0 = at('instead a cold'); put(music, t0, pad([note('D2'), note('G#2')], 9.0, 500, 2.0, 2.0), .5)
# 167 - 252 Mira: mysterious arps
t0 = at('her name is'); t1 = at('you know the bureau')
arp = ['A3', 'C4', 'E4', 'B4', 'A3', 'C4', 'E4', 'G4', 'F3', 'A3', 'C4', 'E4', 'G3', 'B3', 'D4', 'F#4']
for k in range(int((t1 - t0) / .25)):
    put(music, t0 + k * .25, mallet(note(arp[k % 16]), .4, .5), .22, math.sin(k * .7) * .5)
chord_seq(t0, [['A2', 'E3', 'C4'], ['F2', 'C3', 'A3'], ['C3', 'G3', 'E4'], ['G2', 'D3', 'B3']] * 6, 4.0, 1000, .3)
t2 = at('over the next month')
chord_seq(t1, [['D2', 'A2', 'F3'], ['A#1', 'F2', 'D3'], ['C2', 'G2', 'D#3'], ['A1', 'E2', 'C#3']] * 2, (t2 - t1) / 8, 700, .45)
put(music, at('if people found'), drum(2.0, 40, 80, .8), .6)
# 252 - end: action
t0 = t2; b = 60 / 140
for k in range(int((279 - t0) / b)):
    tt = t0 + k * b
    put(music, tt, pulse(note(['D2', 'D2', 'F2', 'C2'][(k // 8) % 4]), b, 8, .2), .3)
    if k % 2 == 0: put(music, tt, drum(.4, 50, 120, .8), .45)
    if k % 4 == 2: put(music, tt, noise(.1, 'white') * env(int(.1 * SR), .001, .03), .25)
put(music, at('then a quake') + .4, boom(2.5, 1.0), .6); put(music, at('one punch') + .25, boom(3.0, 1.0), .8)
m = music / max(1e-6, np.abs(music).max()) * .8
end = int(278.05 * SR); m[end - SR:end] *= np.linspace(1, 0, SR)[:, None]; m = m[:end]
sf.write('out/music_p2.wav', m.astype(np.float32), SR); print('music ok')
