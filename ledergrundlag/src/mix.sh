#!/usr/bin/env bash
# Mixer stemmen med baggrundsmusikken (musikken dukker automatisk, når der tales).
# Brug: src/mix.sh <stemme-fil> <musik-mappe>   ->  src/audio/mix-v4.mp3, mix-v5.mp3 (+ .wav til video)
set -euo pipefail
VOICE="$1"; MUSIC="$2"; OUT="$(dirname "$0")/audio"
for v in v4 v5; do
  ffmpeg -loglevel error -y -i "$VOICE" -i "$MUSIC/music-$v.wav" -filter_complex \
    "[0:a]aresample=44100,highpass=f=70,loudnorm=I=-16:TP=-2:LRA=11,aresample=44100,apad=whole_dur=134.5,asplit=2[v][sc];\
     [1:a]volume=0.40[m];[m][sc]sidechaincompress=threshold=0.015:ratio=12:attack=20:release=500[md];\
     [v][md]amix=inputs=2:duration=longest:normalize=0,alimiter=limit=0.95,atrim=0:134.5[out]" \
    -map "[out]" -ac 2 -ar 44100 "$OUT/mix-$v.wav"
  ffmpeg -loglevel error -y -i "$OUT/mix-$v.wav" -c:a libmp3lame -b:a 128k "$OUT/mix-$v.mp3"
done
