# Тема MARKIZ NIGHT для Huawei (EMUI 10): неоновые иконки, обои и упаковка в .hwt.
# Иконки рисуются одним листом в безголовом Chrome с прозрачным фоном и режутся на 192x192.
import os, shutil, subprocess, sys, zipfile
from PIL import Image
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from art import CHROME, PROFILE_DIR

HERE = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(HERE, "theme_build")
PX, COLS = 192, 8
PINK, CYAN, PURP, YEL, GRN, ORG, RED = "#ff3dbb", "#36e6ff", "#b04dff", "#ffd23d", "#3dffa8", "#ff8a3d", "#ff4d6d"

# Глифы в системе координат 24x24, рисуются линиями
G = {
    "gear": '<circle cx="12" cy="12" r="3.2"/><path d="M12 2.5v3M12 18.5v3M2.5 12h3M18.5 12h3M5.3 5.3l2.1 2.1M16.6 16.6l2.1 2.1M5.3 18.7l2.1-2.1M16.6 7.4l2.1-2.1"/><circle cx="12" cy="12" r="6.5"/>',
    "camera": '<rect x="3" y="7" width="18" height="13" rx="3"/><path d="M8.5 7l1.5-2.5h4L15.5 7"/><circle cx="12" cy="13.5" r="3.5"/>',
    "photo": '<rect x="3" y="4" width="18" height="16" rx="3"/><path d="M3 17l5-5 4 4 3-3 6 6"/><circle cx="16" cy="9" r="1.8"/>',
    "globe": '<circle cx="12" cy="12" r="9"/><ellipse cx="12" cy="12" rx="4" ry="9"/><path d="M3 12h18"/>',
    "cal": '<rect x="3.5" y="5" width="17" height="15" rx="3"/><path d="M3.5 10h17M8 3v4M16 3v4"/><path d="M8 14h2M14 14h2M8 17h2"/>',
    "calc": '<rect x="5" y="3" width="14" height="18" rx="3"/><path d="M8 7h8M8.5 12h2M9.5 11v2M14 12h2M8.5 16.5l2 2M10.5 16.5l-2 2M14 16.5h2M14 18.5h2"/>',
    "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 6.5V12l3.5 2.5"/>',
    "mail": '<rect x="3" y="5.5" width="18" height="13" rx="2.5"/><path d="M3.5 7l8.5 6 8.5-6"/>',
    "user": '<circle cx="12" cy="8.5" r="3.8"/><path d="M4.5 20c1-4 4-5.5 7.5-5.5s6.5 1.5 7.5 5.5"/>',
    "note": '<rect x="5" y="3" width="14" height="18" rx="2.5"/><path d="M8.5 8h7M8.5 12h7M8.5 16h4"/>',
    "music": '<path d="M9 18V5.5l10-2V16"/><circle cx="6.5" cy="18" r="2.5"/><circle cx="16.5" cy="16" r="2.5"/>',
    "play": '<rect x="3" y="5" width="18" height="14" rx="4"/><path d="M10 9v6l5-3z"/>',
    "book": '<path d="M12 6.5C9.5 4.8 6.5 4.5 3.5 5v13c3-.5 6-.2 8.5 1.5 2.5-1.7 5.5-2 8.5-1.5V5c-3-.5-6-.2-8.5 1.5zM12 6.5v13"/>',
    "folder": '<path d="M3 7.5a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2V17a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>',
    "bag": '<path d="M5 8h14l-1.2 11.5a2 2 0 0 1-2 1.5H8.2a2 2 0 0 1-2-1.5z"/><path d="M9 10V7a3 3 0 0 1 6 0v3"/>',
    "pad": '<path d="M7 8h10a4 4 0 0 1 4 4v2.5a2.5 2.5 0 0 1-4.5 1.5L15 14H9l-1.5 2A2.5 2.5 0 0 1 3 14.5V12a4 4 0 0 1 4-4z"/><path d="M7.5 10.5v3M6 12h3"/><circle cx="15.5" cy="11.2" r=".6"/><circle cx="17.2" cy="13" r=".6"/>',
    "pin": '<path d="M12 21s-6.5-6-6.5-11a6.5 6.5 0 0 1 13 0c0 5-6.5 11-6.5 11z"/><circle cx="12" cy="10" r="2.5"/>',
    "brush": '<path d="M14 4l6 6-7.5 7.5-6-6z"/><path d="M6.5 11.5L4 20l8.5-2.5"/>',
    "shield": '<path d="M12 3l7.5 3v5.5c0 4.5-3.2 8-7.5 9.5-4.3-1.5-7.5-5-7.5-9.5V6z"/><path d="M8.8 12l2.2 2.2 4.2-4.4"/>',
    "mic": '<rect x="9" y="3" width="6" height="11" rx="3"/><path d="M5.5 11a6.5 6.5 0 0 0 13 0M12 17.5V21M9 21h6"/>',
    "radio": '<rect x="3" y="9" width="18" height="11" rx="2.5"/><path d="M6 9l11-5"/><circle cx="15.5" cy="14.5" r="2.5"/><path d="M6.5 13h4M6.5 16h4"/>',
    "plane": '<path d="M21 4L3 11l6 2.5L19 6l-8 9v5l3.5-3.5L18 19z"/>',
    "lock": '<rect x="5" y="10.5" width="14" height="10" rx="2.5"/><path d="M8 10.5V7.5a4 4 0 0 1 8 0v3"/><circle cx="12" cy="15.5" r="1.3"/>',
    "radar": '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><path d="M12 12l6-6"/><circle cx="12" cy="12" r="1"/>',
    "help": '<circle cx="12" cy="12" r="9"/><path d="M9.5 9.5a2.5 2.5 0 1 1 3.5 2.3c-.7.3-1 .9-1 1.7v.5"/><circle cx="12" cy="17" r=".5"/>',
    "bulb": '<path d="M9 17.5h6M10 21h4M12 3a6 6 0 0 0-3.5 10.9c.4.3.5.7.5 1.1v.5h6v-.5c0-.4.1-.8.5-1.1A6 6 0 0 0 12 3z"/>',
    "cloud": '<path d="M7 18.5a4 4 0 0 1-.5-8A5.5 5.5 0 0 1 17 9.5a4.5 4.5 0 0 1 .5 9z"/><path d="M15 4.5l1-1.5M19.5 7l1.5-.8"/>',
    "clone": '<rect x="3" y="5" width="8" height="14" rx="2"/><rect x="13" y="5" width="8" height="14" rx="2"/><path d="M9 12h6M13.5 10l1.5 2-1.5 2"/>',
    "update": '<path d="M19.5 12A7.5 7.5 0 1 1 17 6.5"/><path d="M17.5 2.5v4.5H13"/><path d="M12 8.5v4l2.5 1.5"/>',
    "crop": '<path d="M6.5 3v14.5H21M3 6.5h14.5V21"/>',
    "search": '<circle cx="10.5" cy="10.5" r="6.5"/><path d="M15.5 15.5L21 21"/>',
    "keys": '<rect x="2.5" y="6" width="19" height="12" rx="2.5"/><path d="M6 10h.5M9 10h.5M12 10h.5M15 10h.5M18 10h.5M7.5 14.5h9"/>',
    "chat": '<path d="M4 5h16a1.5 1.5 0 0 1 1.5 1.5v9A1.5 1.5 0 0 1 20 17H10l-4.5 3.5V17H4a1.5 1.5 0 0 1-1.5-1.5v-9A1.5 1.5 0 0 1 4 5z"/><path d="M7.5 11h.5M12 11h.5M16 11h.5"/>',
    "cross": '<circle cx="12" cy="12" r="7.5"/><path d="M12 2.5v5M12 16.5v5M2.5 12h5M16.5 12h5"/><circle cx="12" cy="12" r="1"/>',
    "cat": '<path d="M5 20V8.5L4 3.5l5 3.5h6l5-3.5-1 5V20z"/><path d="M9 12.5v1.5M15 12.5v1.5M10.5 17l1.5 1 1.5-1M2 15.5l4.5.5M2 18l4.5-.5M22 15.5l-4.5.5M22 18l-4.5-.5"/>',
    "dog": '<path d="M6 9.5L3.5 5 8 7h8l4.5-2L18 9.5V16a4 4 0 0 1-4 4h-4a4 4 0 0 1-4-4z"/><circle cx="9.5" cy="12" r=".6"/><circle cx="14.5" cy="12" r=".6"/><path d="M11 16h2l-1 1.2z"/>',
    "film": '<rect x="3" y="4" width="18" height="16" rx="2.5"/><path d="M7.5 4v16M16.5 4v16M3 9h4.5M3 15h4.5M16.5 9H21M16.5 15H21"/>',
}

def T(s, size=11):  # текстовый глиф
    return f'<text x="12" y="{12 + size * .36:.1f}" text-anchor="middle" font-size="{size}" font-weight="900" font-family="Segoe UI, Arial Black, sans-serif" stroke-width=".9">{s}</text>'

# пакет -> (глиф, цвет)
APPS = {
    "com.android.settings": ("gear", CYAN), "com.huawei.camera": ("camera", PINK), "com.huawei.photos": ("photo", YEL),
    "com.android.gallery3d": ("photo", YEL), "com.huawei.browser": ("globe", CYAN), "com.android.browser": ("globe", CYAN),
    "com.huawei.calendar": ("cal", RED), "com.android.calendar": ("cal", RED), "com.huawei.calculator": ("calc", ORG),
    "com.huawei.deskclock": ("clock", PURP), "com.android.deskclock": ("clock", PURP), "com.huawei.email": ("mail", CYAN),
    "com.huawei.contacts": ("user", GRN), "com.huawei.notepad": ("note", YEL), "com.example.android.notepad": ("note", YEL),
    "com.huawei.music": ("music", PINK), "com.android.mediacenter": ("music", PINK), "com.huawei.himovie.overseas": ("film", ORG),
    "com.huawei.hwread.dz": ("book", ORG), "com.huawei.hidisk": ("folder", YEL), "com.android.documentsui": ("folder", YEL),
    "com.huawei.appmarket": ("bag", RED), "com.huawei.gamebox": ("pad", PURP), "com.huawei.gameassistant": ("pad", GRN),
    "com.huawei.maps.app": ("pin", RED), "com.huawei.android.thememanager": ("brush", PINK), "com.huawei.systemmanager": ("shield", GRN),
    "com.huawei.soundrecorder": ("mic", RED), "com.huawei.android.FMRadio": ("radio", ORG), "org.telegram.messenger": ("plane", CYAN),
    "com.gbox.com.google.android.youtube": ("play", RED), "org.amnezia.vpn": ("lock", PURP), "com.huawei.android.findmyphone": ("radar", GRN),
    "com.huawei.phoneservice": ("help", CYAN), "com.huawei.android.tips": ("bulb", YEL), "com.huawei.android.totemweather": ("cloud", CYAN),
    "com.hicloud.android.clone": ("clone", CYAN), "com.huawei.mycenter": ("user", PURP), "com.huawei.android.hwouc": ("update", GRN),
    "com.huawei.HwMultiScreenShot": ("crop", PINK), "com.huawei.hwsearch": ("search", CYAN), "ru.yandex.searchplugin": ("search", RED),
    "ru.mail.search.electroscope": ("search", PURP), "com.touchtype.swiftkey": ("keys", CYAN), "com.huawei.welinknow": ("chat", CYAN),
    "ru.oneme.app": ("chat", PURP), "com.axlebolt.standoff2": ("cross", ORG), "app.netlify.funny_syrniki_05be44.twa": ("cat", PINK),
    "com.outfit7.talkingben.global.huawei": ("dog", ORG), "com.smule.singandroid": ("mic", PINK), "ru.yandex.music": ("music", YEL),
    "com.uma.musicvk": ("music", CYAN), "com.planetvideo.zona": ("play", GRN), "ru.vk.store": ("bag", CYAN),
    "cn.wps.moffice_i18n": (T("W", 13), RED), "com.avito.android": (T("A", 13), GRN), "com.wildberries.ru": (T("WB", 10), PURP),
    "com.kms.free": (T("K", 13), GRN), "com.advant.streamer": (T("L", 13), YEL), "com.gbox.android": (T("G", 13), GRN),
}

def icon_svg(glyph, col):
    body = G.get(glyph, glyph)
    fill_text = 'fill="{0}"'.format(col) if body.startswith("<text") else 'fill="none"'
    return f'''<svg width="{PX}" height="{PX}" viewBox="0 0 192 192" xmlns="http://www.w3.org/2000/svg">
<defs><linearGradient id="b" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#24124a"/><stop offset="1" stop-color="#0a0618"/></linearGradient>
<filter id="gl" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="3.2" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>
<rect x="10" y="10" width="172" height="172" rx="46" fill="url(#b)"/>
<rect x="11.5" y="11.5" width="169" height="169" rx="44.5" fill="none" stroke="{col}" stroke-opacity=".75" stroke-width="3" filter="url(#gl)"/>
<path d="M30 40 Q 96 18 162 40" stroke="#fff" stroke-opacity=".10" stroke-width="10" fill="none" stroke-linecap="round"/>
<g transform="translate(46 46) scale(4.1667)" stroke="{col}" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" {fill_text} filter="url(#gl)">{body}</g>
</svg>'''

def render(html, out, w, h):
    src = os.path.join(BUILD, "_sheet.html"); open(src, "w", encoding="utf-8").write(html)
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--no-first-run", f"--user-data-dir={PROFILE_DIR}",
                    "--default-background-color=00000000", "--force-device-scale-factor=1",
                    f"--screenshot={out}", f"--window-size={w},{h}", "file:///" + src.replace("\\", "/")], check=True, timeout=120)

def main():
    shutil.rmtree(BUILD, ignore_errors=True)
    os.makedirs(os.path.join(BUILD, "icons")); os.makedirs(os.path.join(BUILD, "wallpaper")); os.makedirs(os.path.join(BUILD, "unlock")); os.makedirs(os.path.join(BUILD, "preview"))
    names = list(APPS)
    rows = (len(names) + COLS - 1) // COLS
    cells = "".join(f'<div style="position:absolute;left:{(i % COLS) * PX}px;top:{(i // COLS) * PX}px">{icon_svg(*APPS[n])}</div>' for i, n in enumerate(names))
    sheet = os.path.join(BUILD, "_sheet.png")
    render(f'<html><body style="margin:0;background:transparent">{cells}</body></html>', sheet, COLS * PX, rows * PX)
    im = Image.open(sheet).convert("RGBA")
    for i, n in enumerate(names):
        x, y = (i % COLS) * PX, (i // COLS) * PX
        im.crop((x, y, x + PX, y + PX)).save(os.path.join(BUILD, "icons", n + ".png"))
    # Обои: на рабочий стол и экран блокировки
    wall = Image.open(os.path.join(HERE, "markiz_night.png")).convert("RGB")
    wall.save(os.path.join(BUILD, "wallpaper", "home_wallpaper_0.jpg"), quality=92)
    wall.save(os.path.join(BUILD, "unlock", "unlock_wallpaper_0.jpg"), quality=92)
    open(os.path.join(BUILD, "unlock", "theme.xml"), "w", encoding="utf-8").write(
        '<?xml version="1.0" encoding="utf-8"?>\n<HWTheme>\n   <item style="slide"/>\n   <item wallpaper="unlock_wallpaper_0.jpg"/>\n</HWTheme>\n')
    open(os.path.join(BUILD, "description.xml"), "w", encoding="utf-8").write(
        '<?xml version="1.0" encoding="UTF-8"?>\n<HwTheme>\n    <title>MARKIZ NIGHT</title>\n    <title-cn>MARKIZ NIGHT</title-cn>\n'
        '    <author>MARKIZ LAND</author>\n    <designer>MARKIZ LAND</designer>\n    <screen>WUXGA</screen>\n    <version>10.1.2</version>\n'
        '    <font>Default</font>\n    <font-cn>Default</font-cn>\n</HwTheme>\n')
    # Превью для списка тем: обои с сеткой иконок
    pv = wall.resize((1000, 1000)).crop((0, 190, 1000, 810)).convert("RGBA")
    uniq = list({APPS[n]: n for n in reversed(names)}.values())[::-1]
    for i, n in enumerate(uniq[:18]):
        ic = Image.open(os.path.join(BUILD, "icons", n + ".png")).resize((110, 110))
        pv.alpha_composite(ic, (40 + (i % 6) * 160, 60 + (i // 6) * 170))
    pv = pv.convert("RGB")
    for f in ("preview_icons_0", "preview_land_icons_0", "preview_unlock_0", "preview_land_unlock_0", "preview_widget_0", "preview_land_widget_0"):
        pv.save(os.path.join(BUILD, "preview", f + ".jpg"), quality=88)
    pv.resize((330, 205)).save(os.path.join(BUILD, "preview", "icon_small.jpg"), quality=88)
    pv.save(os.path.join(HERE, "theme_preview.jpg"), quality=88)
    # Упаковка: icons — вложенный zip без расширения, всё лежит в корне архива, без сжатия
    icons_zip = os.path.join(BUILD, "icons_pkg")
    with zipfile.ZipFile(icons_zip, "w", zipfile.ZIP_STORED) as z:
        for f in sorted(os.listdir(os.path.join(BUILD, "icons"))):
            z.write(os.path.join(BUILD, "icons", f), f)
    out = os.path.join(HERE, "MARKIZ_NIGHT.hwt")
    with zipfile.ZipFile(out, "w", zipfile.ZIP_STORED) as z:
        z.write(os.path.join(BUILD, "description.xml"), "description.xml")
        z.write(icons_zip, "icons")
        for d in ("preview", "wallpaper", "unlock"):
            for f in sorted(os.listdir(os.path.join(BUILD, d))):
                z.write(os.path.join(BUILD, d, f), f"{d}/{f}")
    print(out, len(names), "icons")

if __name__ == "__main__":
    main()
