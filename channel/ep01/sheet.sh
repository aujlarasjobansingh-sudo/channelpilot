#!/usr/bin/env bash
# sheet.sh out.jpg img1 img2 ... -> 4-column contact sheet
out=$1; shift; n=$#; args=''; for f in "$@"; do args="$args -i $f"; done
fc=''; for i in $(seq 0 $((n-1))); do fc="$fc[$i]scale=480:270[v$i];"; done
cols=4; rows=$(( (n+cols-1)/cols )); r=''
for rr in $(seq 0 $((rows-1))); do row=''; c=0
  for cc in $(seq 0 $((cols-1))); do idx=$((rr*cols+cc)); if [ $idx -lt $n ]; then row="$row[v$idx]"; else fc="${fc}color=black:480x270:d=1[p${rr}_$cc];"; row="$row[p${rr}_$cc]"; fi; done
  fc="$fc${row}hstack=$cols[r$rr];"; r="$r[r$rr]"; done
if [ $rows -gt 1 ]; then fc="$fc${r}vstack=$rows"; else fc="${fc%;}"; fc="${fc%\[r0\]}"; fi
ffmpeg -v error -y $args -filter_complex "$fc" -frames:v 1 $out
