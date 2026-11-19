#!/usr/bin/env bash
# Builds the 10-second preview soundtrack (music bed + SFX) with ffmpeg only. Output: mix10.wav
set -euo pipefail
cd "$(dirname "$0")"
R=44100
F="ffmpeg -v error -y"

# drum hit (taiko-ish): pitch-dropping sine + noise click
$F -f lavfi -i "aevalsrc='0.9*sin(2*PI*(48+110*exp(-14*t))*t)*exp(-4.5*t)':d=1.2:s=$R" \
   -f lavfi -i "anoisesrc=d=1.2:c=pink:r=$R:a=1" \
   -filter_complex "[1]lowpass=f=1800,afade=t=out:st=0:d=0.12[n];[0][n]amix=2:weights='1 0.6',volume=1.8" drum.wav
# minor drone (D minor) 0-8s
$F -f lavfi -i "aevalsrc='0.05*(sin(2*PI*73.42*t)+0.8*sin(2*PI*110*t)+0.6*sin(2*PI*146.83*t)+0.35*sin(2*PI*174.61*t))*(1+0.15*sin(2*PI*0.5*t))':d=8.1:s=$R" \
   -af "lowpass=f=900,afade=t=in:d=0.8,afade=t=out:st=7.75:d=0.3" drone.wav
# riser 5.6-7.9: rising saw-ish + noise
$F -f lavfi -i "aevalsrc='0.10*(t/2.3)*(2*mod(80*t+70*t*t,1)-1)':d=2.3:s=$R" \
   -f lavfi -i "anoisesrc=d=2.3:c=white:r=$R:a=0.25" \
   -filter_complex "[0]lowpass=f=2500[s];[1]highpass=f=2000,volume='t/2.3':eval=frame[n];[s][n]amix=2,afade=t=in:d=1.2" riser.wav
# siren (far away)
$F -f lavfi -i "aevalsrc='0.12*sin(2*PI*(800*t+120*sin(2*PI*0.45*t)/(2*PI*0.45)))':d=7.6:s=$R" \
   -af "lowpass=f=1400,aecho=0.8:0.6:180:0.35,afade=t=in:d=1.0,afade=t=out:st=6.8:d=0.8" siren.wav
# monster roar: low growl with tremolo + gritty mid layer
$F -f lavfi -i "anoisesrc=d=2.0:c=brown:r=$R:a=1" \
   -f lavfi -i "aevalsrc='0.7*sin(2*PI*(62+14*sin(2*PI*9*t))*t)+0.35*sin(2*PI*(124+20*sin(2*PI*13*t))*t)':d=2.0:s=$R" \
   -filter_complex "[0]bandpass=f=280:w=400,tremolo=f=23:d=0.6[n];[1][n]amix=2:weights='1 0.9',acrusher=bits=8:mix=0.25,afade=t=in:d=0.25,afade=t=out:st=1.3:d=0.7,aecho=0.7:0.5:90:0.3,volume=2.0" roar.wav
# running footsteps
$F -f lavfi -i "aevalsrc='(lt(mod(t,0.17),0.03))*sin(2*PI*90*t)*exp(-60*mod(t,0.17))*0.8':d=2.6:s=$R" \
   -af "lowpass=f=500,afade=t=in:d=0.3,afade=t=out:st=2.1:d=0.5,volume=1.4" steps.wav
# charge whine
$F -f lavfi -i "aevalsrc='0.16*sin(2*PI*(220*t+260*t*t))*(t/1.35)':d=1.35:s=$R" -af "afade=t=out:st=1.25:d=0.1" charge.wav
# whoosh
$F -f lavfi -i "anoisesrc=d=0.35:c=white:r=$R:a=0.8" -af "highpass=f=600,lowpass=f=6000,afade=t=in:d=0.25,afade=t=out:st=0.25:d=0.1,volume=0.9" whoosh.wav
# BOOM (sub + body + crack) with long tail
$F -f lavfi -i "aevalsrc='1.0*sin(2*PI*(38+120*exp(-9*t))*t)*exp(-1.6*t)':d=2.6:s=$R" \
   -f lavfi -i "anoisesrc=d=2.6:c=pink:r=$R:a=1" \
   -filter_complex "[1]lowpass=f=1200,afade=t=out:st=0:d=1.4[n];[0][n]amix=2:weights='1 0.9',aecho=0.8:0.7:120|260:0.35|0.2,volume=2.6" boom.wav
# debris crumble
$F -f lavfi -i "anoisesrc=d=1.6:c=brown:r=$R:a=0.7" -af "lowpass=f=700,tremolo=f=13:d=0.8,afade=t=in:d=0.15,afade=t=out:st=0.9:d=0.7,volume=1.2" crumble.wav
# title chord (D major, airy) + sub drop
$F -f lavfi -i "aevalsrc='0.06*(sin(2*PI*146.83*t)+sin(2*PI*185*t)+sin(2*PI*220*t)+0.7*sin(2*PI*293.66*t)+0.4*sin(2*PI*369.99*t))':d=1.3:s=$R" \
   -af "afade=t=in:d=0.15,afade=t=out:st=0.7:d=0.6,aecho=0.8:0.8:110|230:0.4|0.25,volume=1.6" chord.wav
$F -f lavfi -i "aevalsrc='0.8*sin(2*PI*(90*exp(-3*t)+30)*t)*exp(-2.2*t)':d=1.2:s=$R" subdrop.wav
# wind bed
$F -f lavfi -i "anoisesrc=d=10:c=pink:r=$R:a=0.15" -af "bandpass=f=500:w=600,tremolo=f=0.3:d=0.5,afade=t=in:d=1,afade=t=out:st=9.2:d=0.8" wind.wav

$F -i wind.wav -i drone.wav -i siren.wav -i drum.wav -i drum.wav -i drum.wav -i roar.wav -i roar.wav -i steps.wav \
   -i riser.wav -i charge.wav -i whoosh.wav -i boom.wav -i crumble.wav -i chord.wav -i subdrop.wav -filter_complex "\
[3]adelay=0|0[d1];[4]adelay=2600|2600[d2];[5]adelay=5200|5200,volume=0.9[d3];\
[6]adelay=1000|1000[r1];[7]adelay=5400|5400,volume=0.6[r2];[8]adelay=2700|2700[st];\
[9]adelay=5600|5600[ri];[10]adelay=6500|6500[ch];[11]adelay=7600|7600[wh];[12]adelay=7920|7920[bo];\
[13]adelay=8100|8100[cr];[14]adelay=8850|8850[cd];[15]adelay=8850|8850,volume=0.8[sd];\
[0][1][2][d1][d2][d3][r1][r2][st][ri][ch][wh][bo][cr][cd][sd]amix=16:normalize=0:duration=longest,\
apad=whole_dur=10,atrim=0:10,alimiter=limit=0.92,afade=t=out:st=9.6:d=0.4[out]" -map "[out]" -ac 2 mix10.wav
ffprobe -v error -show_entries format=duration -of csv=p=0 mix10.wav
