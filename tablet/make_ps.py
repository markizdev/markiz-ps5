# Стиль "консольное меню" в духе PS5: глубокий синий фон со световыми волнами
# и плитки-иконки с белыми глифами. Глифы и список приложений берутся из make_theme.py.
# Иконки кладутся в ps_build/icons, обои в markiz_blue.png.
import os, random, subprocess
from PIL import Image
from make_theme import G, APPS, CHROME, PROFILE_DIR, PX, COLS

HERE = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(HERE, "ps_build")

# Цвет плитки (верх, низ) по цвету приложения из make_theme; для известных приложений — свой фирменный оттенок
GRAD = {"#ff3dbb": ("#ff5fa8", "#c2186b"), "#36e6ff": ("#3fb4ff", "#1460d8"), "#b04dff": ("#a46bff", "#5b23c9"),
        "#ffd23d": ("#ffc93d", "#f08a00"), "#3dffa8": ("#3ddc84", "#0f9a55"), "#ff8a3d": ("#ff9a3d", "#e0480f"), "#ff4d6d": ("#ff5a5a", "#c8102e")}
BRAND = {"org.telegram.messenger": ("#37b6f2", "#1b87d6"), "com.gbox.com.google.android.youtube": ("#ff3d3d", "#c40000"),
         "com.android.settings": ("#7b8798", "#3e4756"), "com.huawei.camera": ("#4a4f5c", "#1f222a"), "com.huawei.photos": ("#ffb43d", "#f05a28"),
         "com.huawei.appmarket": ("#ff4d55", "#cf0a2c"), "org.amnezia.vpn": ("#9a5cff", "#4a1fb8"), "com.axlebolt.standoff2": ("#ffa53d", "#d9480f"),
         "ru.yandex.searchplugin": ("#ff5240", "#d81b00"), "app.netlify.funny_syrniki_05be44.twa": ("#ff6ec7", "#8a2be2")}

def tile_svg(i, pkg, glyph, col):
    body = G.get(glyph, glyph)
    fill_text = 'fill="#fff"' if body.startswith("<text") else 'fill="none"'
    c1, c2 = BRAND.get(pkg) or GRAD.get(col, ("#5a7cff", "#2a3fb8"))
    # Сплошная цветная плитка: градиент сверху вниз, мягкий блик, толстый белый глиф с тенью (сдвинутая тёмная копия).
    # id градиентов уникальны (i), иначе на общем листе все плитки берут первый градиент
    return f'''<svg width="{PX}" height="{PX}" viewBox="0 0 192 192" xmlns="http://www.w3.org/2000/svg">
<defs><linearGradient id="b{i}" x1="0" y1="0" x2=".35" y2="1"><stop offset="0" stop-color="{c1}"/><stop offset="1" stop-color="{c2}"/></linearGradient>
<radialGradient id="h{i}" cx=".3" cy="0" r=".9"><stop offset="0" stop-color="#fff" stop-opacity=".35"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient></defs>
<rect x="8" y="8" width="176" height="176" rx="40" fill="url(#b{i})"/>
<rect x="8" y="8" width="176" height="176" rx="40" fill="url(#h{i})"/>
<rect x="9" y="9" width="174" height="174" rx="39" fill="none" stroke="#fff" stroke-opacity=".18" stroke-width="2"/>
<g transform="translate(42 45) scale(4.5)" stroke="#000" stroke-opacity=".18" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" {fill_text.replace("#fff", "#000")} fill-opacity=".18">{body}</g>
<g transform="translate(42 42) scale(4.5)" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" {fill_text}>{body}</g>
</svg>'''

def wall_svg(S=2000):
    r = random.Random(5)
    dots = "".join(f'<circle cx="{r.uniform(0, S):.0f}" cy="{r.uniform(300, 1700):.0f}" r="{r.choice([1.5, 2, 3, 5, 8, 12])}" '
                   f'fill="#9cc8ff" opacity="{r.uniform(.05, .35):.2f}" filter="url(#s1)"/>' for _ in range(140))
    waves = []
    for i in range(26):  # пучок плавных световых линий через весь экран
        y0, y1, y2, y3 = 1350 - i * 9, 900 + i * 14, 1250 - i * 6, 800 + i * 11
        waves.append(f'<path d="M-100 {y0} C 500 {y1}, 1100 {y2}, 2100 {y3}" stroke="#7fb4ff" stroke-opacity="{.05 + (i % 5) * .025:.3f}" stroke-width="{1 + (i % 3)}" fill="none"/>')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{S}" height="{S}" viewBox="0 0 {S} {S}">
<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0a1f5c"/><stop offset=".5" stop-color="#05103a"/><stop offset="1" stop-color="#01051a"/></linearGradient>
  <radialGradient id="glow1" cx=".2" cy=".3" r=".6"><stop offset="0" stop-color="#2f6bff" stop-opacity=".55"/><stop offset="1" stop-color="#2f6bff" stop-opacity="0"/></radialGradient>
  <radialGradient id="glow2" cx=".85" cy=".75" r=".5"><stop offset="0" stop-color="#00b7ff" stop-opacity=".25"/><stop offset="1" stop-color="#00b7ff" stop-opacity="0"/></radialGradient>
  <linearGradient id="band" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#5aa0ff" stop-opacity="0"/><stop offset=".5" stop-color="#9fd0ff" stop-opacity=".35"/><stop offset="1" stop-color="#5aa0ff" stop-opacity="0"/></linearGradient>
  <filter id="s1"><feGaussianBlur stdDeviation="1.5"/></filter>
  <filter id="s2"><feGaussianBlur stdDeviation="40"/></filter>
  <linearGradient id="vign" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#000" stop-opacity=".45"/><stop offset=".35" stop-color="#000" stop-opacity="0"/><stop offset=".8" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".5"/></linearGradient>
</defs>
<rect width="{S}" height="{S}" fill="url(#bg)"/>
<rect width="{S}" height="{S}" fill="url(#glow1)"/>
<rect width="{S}" height="{S}" fill="url(#glow2)"/>
<path d="M-100 1250 C 500 950, 1100 1300, 2100 900" stroke="url(#band)" stroke-width="160" fill="none" filter="url(#s2)"/>
{"".join(waves)}
{dots}
<rect width="{S}" height="{S}" fill="url(#vign)"/>
</svg>'''

def shot(html, out, w, h):
    src = os.path.join(BUILD, "_page.html"); open(src, "w", encoding="utf-8").write(html)
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--no-first-run", f"--user-data-dir={PROFILE_DIR}",
                    "--default-background-color=00000000", "--force-device-scale-factor=1",
                    f"--screenshot={out}", f"--window-size={w},{h}", "file:///" + src.replace("\\", "/")], check=True, timeout=120)

def main():
    os.makedirs(os.path.join(BUILD, "icons"), exist_ok=True)
    names = list(APPS)
    rows = (len(names) + COLS - 1) // COLS
    cells = "".join(f'<div style="position:absolute;left:{(i % COLS) * PX}px;top:{(i // COLS) * PX}px">{tile_svg(i, n, *APPS[n])}</div>' for i, n in enumerate(names))
    sheet = os.path.join(BUILD, "_sheet.png")
    shot(f'<html><body style="margin:0;background:transparent">{cells}</body></html>', sheet, COLS * PX, rows * PX)
    im = Image.open(sheet).convert("RGBA")
    for i, n in enumerate(names):
        x, y = (i % COLS) * PX, (i // COLS) * PX
        im.crop((x, y, x + PX, y + PX)).save(os.path.join(BUILD, "icons", n + ".png"))
    wall = os.path.join(HERE, "markiz_blue.png")
    shot(f'<html><body style="margin:0;background:#000">{wall_svg()}</body></html>', wall, 2000, 2000)
    # Превью: обои + ряд плиток, как будет на планшете
    pv = Image.open(wall).convert("RGBA").resize((1920, 1920)).crop((0, 360, 1920, 1560))
    row = ["app.netlify.funny_syrniki_05be44.twa", "com.axlebolt.standoff2", "com.gbox.com.google.android.youtube", "org.telegram.messenger",
           "org.amnezia.vpn", "com.huawei.appmarket", "com.huawei.photos", "com.android.settings"]
    for i, n in enumerate(row):
        pv.alpha_composite(Image.open(os.path.join(BUILD, "icons", n + ".png")).resize((170, 170)), (90 + i * 222, 330))
    pv.convert("RGB").save(os.path.join(HERE, "ps_preview.jpg"), quality=88)
    print(wall, len(names), "icons")

if __name__ == "__main__":
    main()
