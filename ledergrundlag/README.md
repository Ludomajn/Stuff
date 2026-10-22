# Ledergrundlag – visualisering

Fem versioner af samme tale, alle i 1920×1080 og 30 fps. v1–v3 er uden lyd (ca. 2:15). v4 og v5 har din indtalte stemme og original baggrundsmusik (2:14,5), og grafikken er synkroniseret med optagelsen.

| Version | Video | Live-præsentation | Stil |
|---|---|---|---|
| v1 Typografi | `ledergrundlag.mp4` | `index.html` | Mørk, kinetisk typografi med en orange prik ("dig") og holdet som prikker |
| v2 Idévæggen | `ledergrundlag-v2-idevaeggen.mp4` | `v2-idevaeggen.html` | Post-its og tusch på en whiteboard. Kameraet panorerer og zoomer til sidst ud over hele væggen |
| v3 Motorvejen | `ledergrundlag-v3-motorvejen.mp4` | `v3-motorvejen.html` | Nattekørsel med talen på vejskilte. Farten følger talen (200 km/t, opbremsning ved "MEN"), og natten går over i solopgang |
| v4 Taktiktavlen 🔊 | `ledergrundlag-v4-taktiktavlen.mp4` | `v4-taktiktavlen.html` | Kridt på grøn tavle: holdet som spillere (O), "DU" og den spillende træner "T", afleveringer, mål og omsorg. Lo-fi klavermusik |
| v5 Level Up 🔊 | `ledergrundlag-v5-levelup.mp4` | `v5-levelup.html` | Retro pixel-spil: PLAYER 2 HAS JOINED, WORLD 1-1: KAOS, STAGE CLEAR, GAME OVER? → CONTINUE, LEVEL UP, quest-log. Chiptune |

## Live-præsentation
v4 og v5: Åbn HTML-filen og klik for at afspille med lyd. Mellemrum sætter på pause, ← og → spoler 5 sek., og F giver fuldskærm.

v1–v3: Åbn HTML-filen i Chrome eller Safari. Hver scene spiller og bliver stående, til du går videre.
- → / mellemrum / klik / presenter-clicker: næste scene
- ←: forrige · A: autoplay · F: fuldskærm

Alle HTML-filer er selvstændige, med indlejrede fonte, og virker offline.

## Redigering
- v1: ret direkte i `index.html`.
- v2/v3: ret i `src/v2-idevaeggen.html` / `src/v3-motorvejen.html` og byg derefter med `python3 src/build.py`. Bygget indlejrer `src/engine.js` og fontene fra `src/fonts/`.
- Hver scene er én `S({...})`-blok, og `dur` er varigheden i sekunder.

## Lyd (v4/v5)
- `src/music.py` genererer original, rettighedsfri musik. Den stopper ved "MEN" og slutter på en akkord ved "bedste hold".
- `src/mix.sh <stemme> <musikmappe>` mixer stemmen ind og dæmper musikken automatisk, når der tales (sidechain). Resultatet bliver `src/audio/mix-v4/v5.mp3`.
- Tidspunkterne for scenerne kommer fra pauserne i optagelsen (fx "MEN" ved 50,46 s og "formegentligt" ved 126,5 s).
- Videoen laves ved at rendere stum video med `render.cjs` og derefter lægge `mix-vX.wav` på med ffmpeg.

## Generér video
Kræver Playwright og ffmpeg:
```
NODE_PATH=$(npm root -g) node render.cjs --in v3-motorvejen.html ledergrundlag-v3-motorvejen.mp4
NODE_PATH=$(npm root -g) node render.cjs --in v3-motorvejen.html --stills 5,30,60 ./stills   # stillbilleder
```
