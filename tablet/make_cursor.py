# Курсоры в стиле PS5: белая стрелка с синей обводкой и мягким свечением, рука для ссылок — та же стрелка с синей точкой.
# Рисуются в безголовом Chrome и упаковываются в .cur (PNG внутри, несколько размеров) в %LOCALAPPDATA%\MarkizCursors.
import io, os, struct
from PIL import Image
from make_ps import shot, BUILD

OUT = os.path.join(os.environ["LOCALAPPDATA"], "MarkizCursors")
S = 128  # рисуем крупно, потом уменьшаем до 32/48/64/96

ARROW = '''<path d="M14 8 L14 98 L37 76 L52 112 L68 105 L53 70 L86 70 Z"
  fill="#ffffff" stroke="#0070d1" stroke-width="7" stroke-linejoin="round" filter="url(#g)"/>'''
DOT = '<circle cx="98" cy="100" r="14" fill="#0070d1" stroke="#fff" stroke-width="5"/>'
BUSY = '''<circle cx="64" cy="64" r="40" fill="none" stroke="#ffffff" stroke-opacity=".35" stroke-width="12"/>
<path d="M64 24 A40 40 0 0 1 104 64" fill="none" stroke="#0070d1" stroke-width="12" stroke-linecap="round" filter="url(#g)"/>'''

def svg(body):
    return f'''<svg width="{S}" height="{S}" viewBox="0 0 128 128" xmlns="http://www.w3.org/2000/svg">
<defs><filter id="g" x="-30%" y="-30%" width="160%" height="160%"><feDropShadow dx="0" dy="0" stdDeviation="4" flood-color="#2f8bff" flood-opacity=".8"/></filter></defs>{body}</svg>'''

def write_cur(img, path, hot):
    """img: RGBA 128x128, hot: точка клика в координатах 128x128"""
    entries, blobs = [], []
    for size in (32, 48, 64, 96):
        b = io.BytesIO(); img.resize((size, size), Image.LANCZOS).save(b, "PNG"); data = b.getvalue()
        k = size / S
        entries.append((size, round(hot[0] * k), round(hot[1] * k), data))
    off = 6 + 16 * len(entries)
    out = struct.pack("<HHH", 0, 2, len(entries))
    for size, hx, hy, data in entries:
        out += struct.pack("<BBBBHHII", size % 256, size % 256, 0, 0, hx, hy, len(data), off); off += len(data)
    out += b"".join(e[3] for e in entries)
    open(path, "wb").write(out)

def main():
    os.makedirs(OUT, exist_ok=True); os.makedirs(BUILD, exist_ok=True)
    items = [("arrow", ARROW, (14, 8)), ("hand", ARROW + DOT, (14, 8)), ("busy", BUSY, (64, 64)), ("working", ARROW + BUSY.replace('cx="64" cy="64" r="40"', 'cx="96" cy="96" r="22"').replace("M64 24 A40 40 0 0 1 104 64", "M96 74 A22 22 0 0 1 118 96").replace('stroke-width="12"', 'stroke-width="8"'), (14, 8))]
    cells = "".join(f'<div style="position:absolute;left:{i * S}px;top:0">{svg(b)}</div>' for i, (_, b, _) in enumerate(items))
    sheet = os.path.join(BUILD, "_cursors.png")
    shot(f'<html><body style="margin:0;background:transparent">{cells}</body></html>', sheet, len(items) * S, S)
    im = Image.open(sheet).convert("RGBA")
    for i, (name, _, hot) in enumerate(items):
        write_cur(im.crop((i * S, 0, (i + 1) * S, S)), os.path.join(OUT, name + ".cur"), hot)
    print(OUT)

if __name__ == "__main__":
    main()
