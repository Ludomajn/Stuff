# Ledergrundlag – visualisering

- `ledergrundlag.mp4` – færdig video, 1920×1080, 30 fps, 2:08, uden lyd.
- `index.html` – samme animation som live-præsentation. Åbn i Chrome/Safari:
  - → / mellemrum / klik / presenter-clicker: næste scene (hver scene holder sit slutbillede, til du går videre)
  - ←: forrige · A: autoplay · F: fuldskærm
- `render.cjs` – genererer videoen fra HTML'en (`NODE_PATH=$(npm root -g) node render.cjs`, kræver Playwright + ffmpeg).

Tekster og timing rettes direkte i `index.html` (én `S({...})`-blok pr. scene, `dur` = sekunder).
