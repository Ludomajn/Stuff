"""Bygger selvstændige HTML-filer: indlejrer engine.js og fonte (base64), så filerne virker offline.

Brug: python3 src/build.py   (fra ledergrundlag/)
"""
import base64
from pathlib import Path

SRC = Path(__file__).parent
OUT = SRC.parent
PAGES = {'v2-idevaeggen.html': 'v2-idevaeggen.html', 'v3-motorvejen.html': 'v3-motorvejen.html'}

engine = (SRC / 'engine.js').read_text()
for src, dst in PAGES.items():
    if not (SRC / src).exists():
        continue
    html = (SRC / src).read_text()
    html = html.replace('<script src="engine.js"></script>', '<script>\n' + engine + '</script>')
    for font in (SRC / 'fonts').glob('*.woff2'):
        b64 = base64.b64encode(font.read_bytes()).decode()
        html = html.replace(f'url(fonts/{font.name})', f'url(data:font/woff2;base64,{b64})')
    (OUT / dst).write_text(html)
    print('->', OUT / dst)
