# Обои для планшета "MARKIZ NIGHT": ночной неоновый город, луна и кот Маркиз на крыше.
# Квадрат 2000x2000: в альбомной ориентации видна полоса y 400..1600, в книжной x 400..1600.
import os, random, subprocess, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from art import CHROME, PROFILE_DIR

HERE = os.path.dirname(os.path.abspath(__file__))
S = 2000
rnd = random.Random(7)

def stars():
    out = []
    for _ in range(260):
        x, y = rnd.uniform(0, S), rnd.uniform(0, 1150)
        r = rnd.choice([0.8, 1, 1.2, 1.6, 2.2])
        o = rnd.uniform(.25, .9)
        out.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r}" fill="#fff" opacity="{o:.2f}"/>')
    return "".join(out)

def skyline(base, hmin, hmax, wmin, wmax, fill, win_p, seed, glow=False):
    r = random.Random(seed)
    out, x = [], -20
    neon = ["#ff3dbb", "#36e6ff", "#b04dff", "#ffd23d"]
    while x < S:
        w = r.uniform(wmin, wmax); h = r.uniform(hmin, hmax); y = base - h
        out.append(f'<rect x="{x:.0f}" y="{y:.0f}" width="{w:.0f}" height="{h + 400:.0f}" fill="{fill}"/>')
        if glow and r.random() < .35:
            c = r.choice(neon)
            out.append(f'<rect x="{x:.0f}" y="{y:.0f}" width="{w:.0f}" height="5" fill="{c}" filter="url(#g)"/>')
        if r.random() < .2:  # антенна
            ax = x + w * r.uniform(.3, .7)
            out.append(f'<rect x="{ax:.0f}" y="{y - 60:.0f}" width="4" height="60" fill="{fill}"/>'
                       f'<circle cx="{ax + 2:.0f}" cy="{y - 62:.0f}" r="5" fill="#ff4d6d" filter="url(#g)"/>')
        cols, rows = int(w // 22), int(h // 30)
        for i in range(cols):
            for j in range(rows):
                if r.random() < win_p:
                    c = r.choice(["#ffd98a", "#ffe7b0", "#8fe9ff", "#ffb3e6"])
                    out.append(f'<rect x="{x + 8 + i * 22:.0f}" y="{y + 14 + j * 30:.0f}" width="10" height="14" fill="{c}" opacity="{r.uniform(.5, 1):.2f}"/>')
        x += w + r.uniform(4, 18)
    return "".join(out)

# Кот Маркиз сидит на крыше спиной к нам и смотрит на луну
CAT = '''
<g transform="translate(1010,1255)">
  <path d="M95 40 C 170 20, 205 -40, 170 -95 C 160 -110, 140 -100, 150 -85 C 175 -45, 150 0, 90 15 Z" fill="#06030f"/>
  <ellipse cx="0" cy="-10" rx="78" ry="62" fill="#06030f"/>
  <ellipse cx="-5" cy="-80" rx="52" ry="58" fill="#06030f"/>
  <circle cx="-5" cy="-150" r="44" fill="#06030f"/>
  <path d="M-45 -165 L-40 -222 L-8 -184 Z" fill="#06030f"/>
  <path d="M35 -165 L32 -222 L0 -184 Z" fill="#06030f"/>
  <path d="M-45 -165 L-40 -222 L-8 -184 M35 -165 L32 -222 L0 -184 M-48 -150 A44 44 0 0 1 38 -158 M-56 -80 C -60 -40, -80 -20, -78 -10 M52 -110 C 65 -60, 82 -40, 78 -10"
        fill="none" stroke="#ff7ad9" stroke-width="3" opacity=".9" filter="url(#g)"/>
</g>'''

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{S}" height="{S}" viewBox="0 0 {S} {S}">
<defs>
  <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#05030f"/><stop offset=".45" stop-color="#140a33"/>
    <stop offset=".62" stop-color="#3a1260"/><stop offset=".7" stop-color="#7a1f6e"/><stop offset=".74" stop-color="#1a0b2e"/>
  </linearGradient>
  <radialGradient id="moonglow"><stop offset="0" stop-color="#ffd6f5" stop-opacity=".55"/><stop offset=".35" stop-color="#c06bff" stop-opacity=".18"/><stop offset="1" stop-color="#c06bff" stop-opacity="0"/></radialGradient>
  <radialGradient id="moon" cx=".4" cy=".38"><stop offset="0" stop-color="#fff8ff"/><stop offset=".7" stop-color="#ffd9f3"/><stop offset="1" stop-color="#f3a6e4"/></radialGradient>
  <linearGradient id="ground" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0b0618"/><stop offset="1" stop-color="#020106"/></linearGradient>
  <linearGradient id="vign" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#000" stop-opacity=".55"/><stop offset=".3" stop-color="#000" stop-opacity="0"/></linearGradient>
  <filter id="g" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="4" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
  <filter id="soft"><feGaussianBlur stdDeviation="18"/></filter>
</defs>
<rect width="{S}" height="{S}" fill="url(#sky)"/>
{stars()}
<circle cx="1625" cy="793" r="330" fill="url(#moonglow)"/>
<circle cx="1625" cy="793" r="115" fill="url(#moon)"/>
<circle cx="1587" cy="762" r="17" fill="#f0b8e4" opacity=".5"/><circle cx="1664" cy="831" r="23" fill="#f0b8e4" opacity=".4"/><circle cx="1652" cy="743" r="9" fill="#f0b8e4" opacity=".5"/>
<ellipse cx="1000" cy="1150" rx="1300" ry="120" fill="#ff3dbb" opacity=".22" filter="url(#soft)"/>
{skyline(1330, 180, 520, 70, 160, "#1c1036", .10, 1)}
{skyline(1420, 120, 380, 90, 200, "#100822", .16, 2, glow=True)}
<rect x="880" y="1300" width="360" height="160" fill="#07040f"/>
<rect x="880" y="1296" width="360" height="6" fill="#36e6ff" filter="url(#g)"/>
{CAT}
<text x="1060" y="1395" text-anchor="middle" font-family="Segoe UI, Arial Black, sans-serif" font-weight="900" font-size="46" letter-spacing="10"
      fill="none" stroke="#36e6ff" stroke-width="2.2" filter="url(#g)">MARKIZ LAND</text>
{skyline(1600, 60, 200, 110, 240, "#07040f", .22, 3, glow=True)}
<rect y="1600" width="{S}" height="400" fill="url(#ground)"/>
<rect y="1598" width="{S}" height="4" fill="#ff3dbb" opacity=".6" filter="url(#g)"/>
<rect width="{S}" height="{S}" fill="url(#vign)"/>
</svg>'''

html = f'<html><body style="margin:0;background:#000">{svg}</body></html>'
src = os.path.join(HERE, "wall.html"); open(src, "w", encoding="utf-8").write(html)
out = os.path.join(HERE, "markiz_night.png")
subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--no-first-run", f"--user-data-dir={PROFILE_DIR}",
                f"--screenshot={out}", f"--window-size={S},{S}", "file:///" + src.replace("\\", "/")], check=True, timeout=120)
print(out)
