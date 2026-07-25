#!/usr/bin/env python3
"""Сборка single-file артефакта: index.html + сжатые img/ → dist/tennis-class.html.

Картинки пережимаются под фактический размер контейнера (retina 2x) и
инлайнятся base64. Запуск: python3 build.py [выходной_путь]
"""
import base64
import io
import os
import re
import sys

from PIL import Image

ROOT = os.path.dirname(os.path.abspath(__file__))
# (файл, целевая ширина px, JPEG quality)
IMAGES = {
    'img/hero.jpg': (1440, 72),
    'img/offer.jpg': (920, 72),
    'img/hall-1.jpg': (1400, 72),
    'img/hall-2.jpg': (1100, 72),
    'img/hall-3.jpg': (1100, 72),
    'img/coach-igor.jpg': (760, 74),
    'img/coach-alexander.jpg': (760, 74),
}


def compress(path, width, quality):
    im = Image.open(os.path.join(ROOT, path)).convert('RGB')
    if im.width > width:
        im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, 'JPEG', quality=quality, optimize=True, progressive=True)
    return buf.getvalue()


def main():
    out_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'dist', 'tennis-class.html')
    html = open(os.path.join(ROOT, 'index.html'), encoding='utf-8').read()
    for src, (width, quality) in IMAGES.items():
        data = compress(src, width, quality)
        b64 = base64.b64encode(data).decode()
        html, n = re.subn(re.escape(src), f'data:image/jpeg;base64,{b64}', html)
        print(f'{src}: {len(data) // 1024} KB inlined ({n} ref)')
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    open(out_path, 'w', encoding='utf-8').write(html)
    print(f'→ {out_path}: {os.path.getsize(out_path) // 1024} KB')


if __name__ == '__main__':
    main()
