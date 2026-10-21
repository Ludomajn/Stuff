# Ledergrundlag – visualisering

Tre versioner af samme tale. Alle er 1920×1080, 30 fps, ca. 2:08 og uden lyd.

| Version | Video | Live-præsentation | Stil |
|---|---|---|---|
| v1 Typografi | `ledergrundlag.mp4` | `index.html` | Mørk, kinetisk typografi med en orange prik ("dig") og holdet som prikker |
| v2 Idévæggen | `ledergrundlag-v2-idevaeggen.mp4` | `v2-idevaeggen.html` | Post-its og tusch på en whiteboard. Kameraet panorerer og zoomer til sidst ud over hele væggen |
| v3 Motorvejen | `ledergrundlag-v3-motorvejen.mp4` | `v3-motorvejen.html` | Nattekørsel med talen på vejskilte. Farten følger talen (200 km/t, opbremsning ved "MEN"), og natten går over i solopgang |

## Live-præsentation
Åbn HTML-filen i Chrome eller Safari. Hver scene spiller og bliver stående, til du går videre.
- → / mellemrum / klik / presenter-clicker: næste scene
- ←: forrige · A: autoplay · F: fuldskærm

Alle HTML-filer er selvstændige, med indlejrede fonte, og virker offline.

## Redigering
- v1: ret direkte i `index.html`.
- v2/v3: ret i `src/v2-idevaeggen.html` / `src/v3-motorvejen.html` og byg derefter med `python3 src/build.py`. Bygget indlejrer `src/engine.js` og fontene fra `src/fonts/`.
- Hver scene er én `S({...})`-blok, og `dur` er varigheden i sekunder.

## Generér video
Kræver Playwright og ffmpeg:
```
NODE_PATH=$(npm root -g) node render.cjs --in v3-motorvejen.html ledergrundlag-v3-motorvejen.mp4
NODE_PATH=$(npm root -g) node render.cjs --in v3-motorvejen.html --stills 5,30,60 ./stills   # stillbilleder
```
