# Главный экран компьютера в стиле PS5 (скин Rainmeter MarkizPS).
#  Hero.ini  — фон на весь экран: картинка выбранной игры (сквозной для мыши, лежит под всем)
#  Home.ini  — вкладки «Игры / Медиа», ряд плиток, логотип выбранной игры и кнопка «Играть»
# Картинки игр берутся из кэша Steam на этом компьютере, для остальных — иконка exe на цветной плитке
# (иконки достаёт PowerShell в ps_build/exeicons). Плитки «Медиа» — из make_pc_ps.py (@Resources/tiles/t*.png).
import os, shutil
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
SKIN = os.path.join(os.path.expanduser("~"), "Documents", "Rainmeter", "Skins", "MarkizPS")
RES = os.path.join(SKIN, "@Resources")
LIB = r"C:\Program Files (x86)\Steam\appcache\librarycache"
ICONS = os.path.join(HERE, "ps_build", "exeicons")
W, H = 2560, 1440
# Имя для приветствия и подсказки на аватаре: первое слово имени пользователя Windows
import getpass
NAME = getpass.getuser().split()[0]
T = 112        # плитка в покое
TS = 160       # плитка под мышкой (выбранная)
GAP = 22
X0, Y0 = 150, 150

# (id, подпись, steam appid или None, иконка exe или None, цвет плитки, что запускать, фон взять у appid)
GAMES = [
    ("steam", "Магазин Steam", None, "steam", ("#2a475e", "#171a21"), "steam://store", None),  # первая плитка, как магазин на консоли
    ("cs2", "Counter-Strike 2", 730, None, None, "steam://rungameid/730", 730),
    ("fh5", "Forza Horizon 5", 1551360, None, None, "steam://rungameid/1551360", 1551360),
    ("gta5", "GTA V", 3240220, None, None, "steam://rungameid/3240220", 3240220),
    ("gta5rp", "GTA5RP", None, "gta5rp", ("#ff9a3d", "#b8360c"), r"C:\Program Files (x86)\GTA5RP\GTA5RPLauncher.exe", 3240220),
    ("fortnite", "Fortnite", None, "fortnite", None, "com.epicgames.launcher://apps/Fortnite?action=launch&silent=true", None),
    ("tlou", "The Last of Us", None, "tlou", ("#5fa36a", "#1f4d2b"), r"E:\The last of Us. Part 1\Launcher.exe", None),
    ("mc", "Minecraft", None, "minecraft", ("#6fbf4a", "#2f6b1c"), os.path.expandvars(r"%APPDATA%\.minecraft\TLauncher.exe"), None),
    ("roblox", "Roblox", None, "roblox", ("#ff5a5a", "#c8102e"), os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs\Roblox\Roblox Player.lnk"), None),
    ("epic", "Epic Games", None, "epic", ("#4a4a4a", "#121212"), r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Epic Games Launcher.lnk", None),
]
# Медиа: (подпись, плитка из make_pc_ps, что запускать)
MEDIA = [
    ("Chrome", "t5", r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Google Chrome.lnk"),
    ("Яндекс", "t6", os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs\Yandex.lnk")),
    ("Discord", "t4", os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs\Discord.lnk")),
    ("YouTube", None, "https://www.youtube.com"),
    ("Проводник", "t7", "explorer.exe"),
    ("Настройки", "t8", "ms-settings:"),
]

def find(appid, name):
    for root, _, files in os.walk(os.path.join(LIB, str(appid))):
        if name in files:
            return os.path.join(root, name)

def rounded(im, r):
    m = Image.new("L", im.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, im.size[0] - 1, im.size[1] - 1), r, fill=255)
    im = im.convert("RGBA"); im.putalpha(m); return im

def grad_tile(c1, c2, icon):
    S = 300
    t = Image.new("RGBA", (S, S))
    a, b = [tuple(int(c[i:i + 2], 16) for i in (1, 3, 5)) for c in (c1, c2)]
    d = ImageDraw.Draw(t)
    for y in range(S):
        k = y / (S - 1); d.line([(0, y), (S, y)], fill=tuple(int(a[i] + (b[i] - a[i]) * k) for i in range(3)) + (255,))
    ic = Image.open(os.path.join(ICONS, icon + ".png")).convert("RGBA")
    ic = ic.crop(ic.getbbox())  # у некоторых exe внутри только маленькая иконка с пустыми полями
    ic = ic.resize((170, 170), Image.NEAREST if ic.width < 64 else Image.LANCZOS)
    t.alpha_composite(ic, ((S - 170) // 2, (S - 170) // 2))
    return rounded(t, 44)

def game_tile(g):
    key, _, appid, icon, cols, _, _ = g
    if appid:
        cover = Image.open(find(appid, "library_600x900.jpg")).convert("RGB")
        w, h = cover.size  # квадрат из верхней части обложки — там обычно лицо/логотип
        cover = cover.crop((0, int(h * .08), w, int(h * .08) + w)).resize((300, 300), Image.LANCZOS)
        return rounded(cover, 44)
    if key == "gta5rp":  # обложка GTA V с плашкой RP
        t = game_tile(next(x for x in GAMES if x[0] == "gta5")).copy(); d = ImageDraw.Draw(t)
        d.rounded_rectangle((150, 222, 286, 286), 18, fill=(255, 140, 40, 255))
        from PIL import ImageFont
        f = ImageFont.truetype(r"C:\Windows\Fonts\segoeuib.ttf", 46)
        d.text((218, 254), "RP", font=f, fill="white", anchor="mm")
        return t
    if key == "fortnite":  # иконка игры и так квадратная на всю плитку
        return rounded(Image.open(os.path.join(ICONS, icon + ".png")).convert("RGB").resize((300, 300), Image.LANCZOS), 44)
    if key == "mc":  # у лаунчера крошечная иконка — рисуем свою плитку с буквами
        t = grad_tile(*cols, "steam"); t = Image.new("RGBA", t.size); d = ImageDraw.Draw(t)
        a, b = [tuple(int(c[i:i + 2], 16) for i in (1, 3, 5)) for c in cols]
        for y in range(300): k = y / 299; d.line([(0, y), (300, y)], fill=tuple(int(a[i] + (b[i] - a[i]) * k) for i in range(3)) + (255,))
        from PIL import ImageFont
        d.text((150, 150), "MC", font=ImageFont.truetype(r"C:\Windows\Fonts\seguibl.ttf", 120), fill="white", anchor="mm")
        return rounded(t, 44)
    return grad_tile(*cols, icon)

def hero(appid):
    """Фон 2560x1440: картинка игры, затемнённая слева и снизу, как на PS5"""
    src = find(appid, "library_hero.jpg")
    im = Image.open(src).convert("RGB")
    k = max(W / im.width, H / im.height); im = im.resize((int(im.width * k) + 1, int(im.height * k) + 1), Image.LANCZOS)
    im = im.crop(((im.width - W) // 2, (im.height - H) // 2, (im.width - W) // 2 + W, (im.height - H) // 2 + H)).convert("RGBA")
    sh = Image.new("RGBA", (W, H)); d = ImageDraw.Draw(sh)
    for x in range(W):  # слева тёмно-синяя дымка, где текст и плитки
        a = int(220 * max(0, 1 - x / (W * .7)) ** 1.4); d.line([(x, 0), (x, H)], fill=(2, 8, 30, a))
    im.alpha_composite(sh)
    sh = Image.new("RGBA", (W, H)); d = ImageDraw.Draw(sh)
    for y in range(H):
        a = int(150 * max(0, (y - H * .55) / (H * .45))) + int(120 * max(0, 1 - y / (H * .25))); d.line([(0, y), (W, y)], fill=(2, 8, 30, min(255, a)))
    im.alpha_composite(sh)
    return im.convert("RGB")

def act_select(i, g, has_logo, has_hero):
    key, name, *_ = g
    run = g[5].replace('"', "")
    a = [f'[!SetVariable Run "{run}"]', f'[!SetOption Name Text "{name}"]']
    if has_logo:
        a += [f'[!SetOption Logo ImageName "#@#games\\{key}_logo.png"]', "[!ShowMeter Logo]", "[!HideMeter Name]"]
    else:
        a += ["[!HideMeter Logo]", "[!ShowMeter Name]"]
    # фон меняется плавно: Hero.ini проявляет новую картинку (Execute 1) или растворяет её до синих волн (Execute 2)
    if has_hero:
        a += [f'[!SetOption Bg ImageName "#@#games\\{key}_hero.jpg" "MarkizPS\\Hero"]', '[!CommandMeasure mFade "Execute 1" "MarkizPS\\Hero"]']
    else:
        a += ['[!CommandMeasure mFade "Execute 2" "MarkizPS\\Hero"]']
    a += ["[!UpdateMeter *]", "[!Redraw]"]
    return "".join(a)

MEASURES = """
[mTime]
Measure=Time
Format=%H:%M

[mCPU]
Measure=CPU

[mRAM]
Measure=PhysicalMemory

[mRAMTotal]
Measure=PhysicalMemory
Total=1
UpdateDivider=-1

[mRAMPct]
Measure=Calc
Formula=Round(mRAM / mRAMTotal * 100)
MinValue=0
MaxValue=100

[mWeather]
Measure=WebParser
URL=https://wttr.in/Nizhny+Novgorod?format=%t|%C|Нижний Новгород&lang=ru
CodePage=65001
RegExp=(?siU)^\\s*(.*)\\|(.*)\\|(.*)\\s*$
UpdateRate=1800

[mTemp]
Measure=WebParser
URL=[mWeather]
StringIndex=1
Substitute="+":""

[mCond]
Measure=WebParser
URL=[mWeather]
StringIndex=2

[mCity]
Measure=WebParser
URL=[mWeather]
StringIndex=3
"""
MEASURES += """
[mVol]
Measure=Plugin
Plugin=Win7AudioPlugin

[mVolPct]
Measure=Calc
Formula=Max(mVol, 0)

; плагин отдаёт -1, когда звук выключен (а как строку — имя устройства, поэтому число берём из Calc)
[mMuteIcon]
Measure=Calc
Formula=(mVol < 0) ? 1 : 0
RegExpSubstitute=1
Substitute="^0$":"","^1$":""
"""
DISKS = [d for d in "CDE" if os.path.exists(d + ":\\")]
for d in DISKS:
    MEASURES += f"""
[m{d}Used]
Measure=FreeDiskSpace
Drive={d}:
InvertMeasure=1

[m{d}Total]
Measure=FreeDiskSpace
Drive={d}:
Total=1

[m{d}Free]
Measure=FreeDiskSpace
Drive={d}:
"""

def header():
    """Справа сверху: поиск, настройки, профиль и время — как в шапке консоли"""
    xs = W - 640
    icon = lambda sec, x, glyph, run: f"""
[{sec}]
Meter=String
Text={glyph}
X={x}
Y=64
FontFace=Segoe Fluent Icons
FontSize=24
FontColor=255,255,255,235
AntiAlias=1
SolidColor=0,0,0,1
MouseOverAction=[!SetOption {sec} FontColor "120,190,255,255"][!UpdateMeter {sec}][!Redraw]
MouseLeaveAction=[!SetOption {sec} FontColor "255,255,255,235"][!UpdateMeter {sec}][!Redraw]
LeftMouseUpAction={run}
"""
    return (icon("HSearch", xs, "", '["ms-search:"]') + icon("HSettings", xs + 90, "", '["ms-settings:"]')
            + f"""
[HAvatar]
Meter=Image
ImageName=#@#games\\avatar.png
X={xs + 172}
Y=52
W=60
H=60
AntiAlias=1
ToolTipText={NAME}
LeftMouseUpAction=["ms-settings:yourinfo"]
""" + f"""
[HTime]
Meter=String
MeasureName=mTime
X={W - 150}
Y=52
StringAlign=Right
FontFace=Segoe UI Light
FontSize=36
FontColor=255,255,255,245
StringEffect=Shadow
FontEffectColor=0,0,0,120
AntiAlias=1
""")

def card(sec, x, y, w, h, title, icon, extra=""):
    return f"""
[{sec}]
Meter=Shape
X={x}
Y={y}
Shape=Rectangle 0,0,{w},{h},22 | Fill Color 14,22,48,190 | StrokeWidth 1.5 | Stroke Color 255,255,255,40
{extra}
[{sec}Icon]
Meter=String
Text={icon}
X={x + 26}
Y={y + 24}
FontFace=Segoe Fluent Icons
FontSize=17
FontColor=255,255,255,230
AntiAlias=1

[{sec}Title]
Meter=String
Text={title}
X={x + 62}
Y={y + 20}
FontFace=Segoe UI Semibold
FontSize=16
FontColor=255,255,255,245
AntiAlias=1
"""

def gauge(sec, cx, cy, measure, label, col):
    """Кольцевой индикатор, как заряд геймпадов на консоли"""
    r = 62
    return f"""
[{sec}Bg]
Meter=Shape
X={cx - r}
Y={cy - r}
Shape=Ellipse {r},{r},{r - 4} | Fill Color 0,0,0,60 | StrokeWidth 7 | Stroke Color 255,255,255,40

[{sec}]
Meter=Roundline
MeasureName={measure}
X={cx - r}
Y={cy - r}
W={2 * r}
H={2 * r}
LineLength={r - 1}
LineStart={r - 8}
StartAngle=4.712
RotationAngle=6.283
Solid=1
LineColor={col}
AntiAlias=1

[{sec}Val]
Meter=String
MeasureName={measure}
Text=%1%
X={cx}
Y={cy}
StringAlign=CenterCenter
FontFace=Segoe UI Semibold
FontSize=20
FontColor=255,255,255,250
AntiAlias=1

[{sec}Lbl]
Meter=String
Text={label}
X={cx}
Y={cy + r + 26}
StringAlign=CenterCenter
FontFace=Segoe UI
FontSize=13
FontColor=200,225,255,220
AntiAlias=1
"""

def cards():
    y1, y2 = 630, 880  # второй ряд кончается выше нижней панели (Dock)
    x = X0; out = ""
    # 1. Система: процессор, память, диск C
    out += card("CSys", x, y1, 560, 400, "Система", "")
    out += gauge("GCpu", x + 110, y1 + 190, "mCPU", "Процессор", "90,200,255,255")
    out += gauge("GRam", x + 280, y1 + 190, "mRAMPct", "Память", "60,220,140,255")
    out += gauge("GDsk", x + 450, y1 + 190, "mCUsed", "Диск C", "255,180,60,255").replace("Text=%1%", "Text=%1%\nPercentual=1").replace("MeasureName=mCUsed\nText", "MeasureName=mCUsed\nText")
    # 2. Погода
    x2 = x + 590
    out += card("CWea", x2, y1, 560, 180, "Погода", "") + f"""
[WTemp]
Meter=String
MeasureName=mTemp
X={x2 + 28}
Y={y1 + 64}
FontFace=Segoe UI Light
FontSize=48
FontColor=255,255,255,255
AntiAlias=1

[WCond]
Meter=String
MeasureName=mCond
MeasureName2=mCity
Text=%1#CRLF#%2
X={x2 + 230}
Y={y1 + 78}
FontFace=Segoe UI
FontSize=15
FontColor=200,225,255,230
ClipString=2
W=300
AntiAlias=1
"""
    # 3. Диски: свободное место
    out += card("CDsk", x2, y1 + 210, 560, 190, "Диски", "")
    for i, d in enumerate(DISKS):
        yy = y1 + 268 + i * 40
        out += f"""
[D{d}Lbl]
Meter=String
MeasureName=m{d}Free
Text={d}:   свободно %1Б
AutoScale=1
NumOfDecimals=0
X={x2 + 28}
Y={yy - 6}
FontFace=Segoe UI
FontSize=13
FontColor=230,240,255,240
AntiAlias=1

[D{d}Bar]
Meter=Bar
MeasureName=m{d}Used
X={x2 + 280}
Y={yy + 4}
W=250
H=8
BarColor=90,170,255,255
SolidColor=255,255,255,35
BarOrientation=Horizontal
"""
    # 4. MARKIZ LAND — своя игра, открывается в браузере
    x3 = x2 + 590
    out += card("CMl", x3, y1, 620, 400, "MARKIZ LAND", "") + f"""
[MlImg]
Meter=Image
ImageName=#@#games\\markiz_card.png
X={x3 + 20}
Y={y1 + 64}
W=580
H=260
LeftMouseUpAction=["https://markiz-land.pages.dev"]

[MlText]
Meter=String
Text=Играть в браузере  ›
X={x3 + 28}
Y={y1 + 344}
FontFace=Segoe UI Semibold
FontSize=16
FontColor=255,255,255,245
SolidColor=0,0,0,1
AntiAlias=1
LeftMouseUpAction=["https://markiz-land.pages.dev"]
"""
    # 5. Магазин Steam
    x4 = x3 + 650
    out += card("CStore", x4, y1, 420, 400, "Магазин Steam", "") + f"""
[StImg]
Meter=Image
ImageName=#@#games\\store_card.png
X={x4 + 20}
Y={y1 + 64}
W=380
H=260
LeftMouseUpAction=["steam://store"]

[StText]
Meter=String
Text=Открыть магазин  ›
X={x4 + 28}
Y={y1 + 344}
FontFace=Segoe UI Semibold
FontSize=16
FontColor=255,255,255,245
SolidColor=0,0,0,1
AntiAlias=1
LeftMouseUpAction=["steam://store"]
"""
    # 6. Время в играх (второй ряд) + уровень игрока: каждые 25 часов — новый уровень
    pt = playtime()
    if pt:
        total = sum(h for _, h in pt); lvl, part = total // 25 + 1, (total % 25) / 25
        out += card("CTime", x, y2 + 170, 1150, 96 + 44 * len(pt), "Время в играх", "") + f"""
[LvlText]
Meter=String
Text=Уровень {lvl}   ·   всего {total} ч
X={x + 1120}
Y={y2 + 170 + 20}
StringAlign=Right
FontFace=Segoe UI Semibold
FontSize=15
FontColor=255,215,120,255
AntiAlias=1

[LvlBar]
Meter=Shape
X={x + 820}
Y={y2 + 170 + 56}
Shape=Rectangle 0,0,300,6,3 | Fill Color 255,255,255,30 | StrokeWidth 0
Shape2=Rectangle 0,0,{max(6, int(300 * part))},6,3 | Fill Color 255,200,90,255 | StrokeWidth 0
"""
    # 7. Звук и питание (второй ряд справа)
    xv, yv, wv = x + 1180, y2 + 170, 560
    out += card("CVol", xv, yv, wv, 228, "Звук и питание", "") + f"""
[VolIcon]
Meter=String
Text=[mMuteIcon]
X={xv + 28}
Y={yv + 70}
FontFace=Segoe Fluent Icons
FontSize=30
FontColor=255,255,255,245
SolidColor=0,0,0,1
AntiAlias=1
DynamicVariables=1
LeftMouseUpAction=[!CommandMeasure mVol "ToggleMute"][!UpdateMeasure mVol][!UpdateMeasure mMuteIcon][!UpdateMeter *][!Redraw]

[VolBar]
Meter=Bar
MeasureName=mVol
X={xv + 100}
Y={yv + 86}
W=330
H=14
BarColor=120,200,255,255
SolidColor=255,255,255,35
BarOrientation=Horizontal
LeftMouseUpAction=[!CommandMeasure mVol "SetVolume $MouseX:%$"][!UpdateMeasure mVol][!UpdateMeter *][!Redraw]
MouseScrollUpAction=[!CommandMeasure mVol "ChangeVolume 5"][!UpdateMeasure mVol][!UpdateMeter *][!Redraw]
MouseScrollDownAction=[!CommandMeasure mVol "ChangeVolume -5"][!UpdateMeasure mVol][!UpdateMeter *][!Redraw]

[VolVal]
Meter=String
MeasureName=mVolPct
Text=%1%
X={xv + wv - 28}
Y={yv + 76}
StringAlign=Right
FontFace=Segoe UI Semibold
FontSize=18
FontColor=255,255,255,250
AntiAlias=1
"""
    # кнопки питания: срабатывают по двойному клику, чтобы случайно не выключить компьютер
    for i, (sec, glyph, label, cmd) in enumerate([
            ("PwSleep", "", "Сон", '["rundll32.exe" "powrprof.dll,SetSuspendState 0,1,0"]'),
            ("PwRestart", "", "Перезагрузка", '["shutdown.exe" /r /t 0]'),
            ("PwOff", "", "Выключить", '["shutdown.exe" /s /t 0]')]):
        bx = xv + 28 + i * 176
        out += f"""
[{sec}]
Meter=Shape
X={bx}
Y={yv + 130}
Shape=Rectangle 0,0,156,80,16 | Fill Color 255,255,255,22 | StrokeWidth 0
MouseOverAction=[!SetOption {sec} Shape "Rectangle 0,0,156,80,16 | Fill Color 255,255,255,55 | StrokeWidth 2 | Stroke Color 255,255,255,180"][!UpdateMeter {sec}][!Redraw]
MouseLeaveAction=[!SetOption {sec} Shape "Rectangle 0,0,156,80,16 | Fill Color 255,255,255,22 | StrokeWidth 0"][!UpdateMeter {sec}][!Redraw]
LeftMouseDoubleClickAction={cmd}
ToolTipText=Двойной клик

[{sec}Ic]
Meter=String
Text={glyph}
X={bx + 78}
Y={yv + 150}
StringAlign=Center
FontFace=Segoe Fluent Icons
FontSize=18
FontColor=255,255,255,240
AntiAlias=1

[{sec}Lb]
Meter=String
Text={label}
X={bx + 78}
Y={yv + 180}
StringAlign=Center
FontFace=Segoe UI
FontSize=11
FontColor=210,225,255,230
AntiAlias=1
"""
        mx = pt[0][1]
        for i, (name, h) in enumerate(pt):
            yy = y2 + 170 + 72 + i * 44
            out += f"""
[PtName{i}]
Meter=String
Text={name}
X={x + 28}
Y={yy}
FontFace=Segoe UI
FontSize=15
FontColor=240,245,255,245
AntiAlias=1

[PtBar{i}]
Meter=Shape
X={x + 300}
Y={yy + 10}
Shape=Rectangle 0,0,620,12,6 | Fill Color 255,255,255,30 | StrokeWidth 0
Shape2=Rectangle 0,0,{max(14, int(620 * h / mx))},12,6 | Fill LinearGradient G | StrokeWidth 0
G=0 | 60,140,255,255 ; 0.0 | 120,210,255,255 ; 1.0

[PtVal{i}]
Meter=String
Text={h} ч
X={x + 1120}
Y={yy}
StringAlign=Right
FontFace=Segoe UI Semibold
FontSize=15
FontColor=255,255,255,250
AntiAlias=1
"""
    return out

def sounds(sdir):
    """Свои тихие звуки интерфейса: короткий «тик» при наведении и мягкий двойной тон при запуске"""
    import math, struct, wave
    os.makedirs(sdir, exist_ok=True)
    def tone(parts, path, vol):
        rate = 44100; data = []
        for f0, f1, ms in parts:
            n = int(rate * ms / 1000)
            for i in range(n):
                t = i / rate; f = f0 + (f1 - f0) * i / n
                env = min(1, i / (rate * .003)) * math.exp(-5 * i / n)  # быстрая атака, мягкое затухание
                data.append(int(32767 * vol * env * (math.sin(2 * math.pi * f * t) + .25 * math.sin(4 * math.pi * f * t))))
        with wave.open(path, "wb") as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(rate)
            w.writeframes(b"".join(struct.pack("<h", max(-32767, min(32767, s))) for s in data))
    tone([(1500, 1300, 45)], os.path.join(sdir, "move.wav"), .10)
    tone([(880, 900, 90), (1320, 1340, 160)], os.path.join(sdir, "select.wav"), .16)

def playtime():
    """Часы в Steam-играх: суммируем Playtime (минуты) по всем аккаунтам из localconfig.vdf"""
    import re
    tot = {}
    ud = os.path.join(os.path.dirname(LIB), "..", "userdata")
    for acc in os.listdir(ud):
        f = os.path.join(ud, acc, "config", "localconfig.vdf")
        if not os.path.exists(f): continue
        txt = open(f, encoding="utf-8", errors="ignore").read()
        for g in GAMES:
            if g[2]:
                m = re.search(r'"%d"\s*\{[^{}]*?"Playtime"\s*"(\d+)"' % g[2], txt)
                if m: tot[g[0]] = tot.get(g[0], 0) + int(m.group(1))
    return sorted(((g[1], tot[g[0]] // 60) for g in GAMES if tot.get(g[0])), key=lambda x: -x[1])

def sort_recent():
    """Как на консоли: сначала магазин, потом Steam-игры по последнему запуску (LastPlayed, по всем аккаунтам), потом остальное"""
    import re
    last = {}
    ud = os.path.join(os.path.dirname(LIB), "..", "userdata")
    for acc in os.listdir(ud):
        f = os.path.join(ud, acc, "config", "localconfig.vdf")
        if not os.path.exists(f): continue
        txt = open(f, encoding="utf-8", errors="ignore").read()
        for g in GAMES:
            if g[2]:
                m = re.search(r'"%d"\s*\{[^{}]*?"LastPlayed"\s*"(\d+)"' % g[2], txt)
                if m: last[g[0]] = max(last.get(g[0], 0), int(m.group(1)))
    store = [g for g in GAMES if g[0] == "steam"]
    steam = sorted((g for g in GAMES if g[2]), key=lambda g: -last.get(g[0], 0))
    rest = [g for g in GAMES if not g[2] and g[0] != "steam"]
    GAMES[:] = store + steam + rest

def avatar(path):
    """Аватар профиля: свой рисунок — кот Маркиз в синем круге"""
    from make_ps import shot
    svg = '''<svg width="192" height="192" viewBox="0 0 192 192" xmlns="http://www.w3.org/2000/svg">
<defs><linearGradient id="a" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3f9bff"/><stop offset="1" stop-color="#0a3c9e"/></linearGradient></defs>
<circle cx="96" cy="96" r="92" fill="url(#a)" stroke="#fff" stroke-width="6"/>
<path d="M52 150 V86 L44 46 L76 70 H116 L148 46 L140 86 V150 Z" fill="#0b1230"/>
<ellipse cx="78" cy="102" rx="9" ry="11" fill="#ffd23d"/><ellipse cx="114" cy="102" rx="9" ry="11" fill="#ffd23d"/>
<ellipse cx="78" cy="104" rx="3" ry="8" fill="#0b1230"/><ellipse cx="114" cy="104" rx="3" ry="8" fill="#0b1230"/>
<path d="M90 122 h12 l-6 7 z" fill="#ff7ad9"/>
<path d="M60 124 l-26 -4 M60 132 l-26 4 M132 124 l26 -4 M132 132 l26 4" stroke="#fff" stroke-width="3" stroke-linecap="round" opacity=".8"/>
</svg>'''
    shot(f'<html><body style="margin:0;background:transparent">{svg}</body></html>', path, 192, 192)

def card_images(gdir):
    """Картинки для карточек: ночной город MARKIZ и обложка Forza для магазина, со скруглёнными углами"""
    im = Image.open(os.path.join(HERE, "markiz_night.png")).convert("RGB")
    im = im.crop((300, 820, 1700, 1450)).resize((1160, 520), Image.LANCZOS)
    rounded(im, 28).save(os.path.join(gdir, "markiz_card.png"))
    st = Image.open(find(1551360, "library_hero.jpg")).convert("RGB")
    k = 520 / st.height; st = st.resize((int(st.width * k), 520), Image.LANCZOS)
    st = st.crop((st.width - 760, 0, st.width, 520))
    rounded(st, 28).save(os.path.join(gdir, "store_card.png"))

def main():
    sort_recent()
    gdir = os.path.join(RES, "games"); os.makedirs(gdir, exist_ok=True)
    for f in os.listdir(gdir): os.remove(os.path.join(gdir, f))
    avatar(os.path.join(gdir, "avatar.png"))
    sel = []
    for g in GAMES:
        key, appid, heroid = g[0], g[2], g[6]
        game_tile(g).save(os.path.join(gdir, key + ".png"))
        logo = find(appid, "logo.png") if appid else (find(heroid, "logo.png") if heroid else None)
        if logo: shutil.copy(logo, os.path.join(gdir, key + "_logo.png"))
        if heroid: hero(heroid).save(os.path.join(gdir, key + "_hero.jpg"), quality=90)
        sel.append(act_select(len(sel), g, bool(logo), bool(heroid)))
    yt = Image.open(os.path.join(HERE, "ps_build", "icons", "com.gbox.com.google.android.youtube.png")).convert("RGBA").resize((300, 300), Image.LANCZOS)
    yt.save(os.path.join(gdir, "youtube.png"))

    # --- Splash.ini: заставка после входа в Windows — тёмный экран с надписью, через секунду плавно тает и прячется
    os.makedirs(os.path.join(SKIN, "Splash"), exist_ok=True)
    open(os.path.join(SKIN, "Splash", "Splash.ini"), "w", encoding="utf-16").write(f"""[Rainmeter]
Update=-1
OnRefreshAction=[!Show][!CommandMeasure mOut "Execute 1"]

[Metadata]
Name=MARKIZ PS Splash
Information=Заставка при запуске: появляется на секунду и плавно исчезает (скин не выключается, а прячется)

[Variables]
A=255

[mOut]
Measure=Plugin
Plugin=ActionTimer
ActionList1=Wait 1300 | Repeat Down,30,17 | Done
Down=[!SetVariable A "(Clamp(#A#-15,0,255))"][!UpdateMeter *][!Redraw]
Done=[!Hide]
DynamicVariables=1

[Bg]
Meter=Shape
Shape=Rectangle 0,0,{W},{H} | Fill RadialGradient G | StrokeWidth 0
G=0,0 | 18,48,120,(#A#) ; 0.0 | 2,6,22,(#A#) ; 1.0
DynamicVariables=1

[Logo]
Meter=String
Text=MARKIZ
X={W // 2}
Y={H // 2 - 40}
StringAlign=CenterCenter
FontFace=Segoe UI Light
FontSize=96
FontColor=255,255,255,(#A#)
CharacterSpacing=24
AntiAlias=1
DynamicVariables=1

[Hello]
Meter=String
Text=Добро пожаловать, {NAME}
X={W // 2}
Y={H // 2 + 70}
StringAlign=CenterCenter
FontFace=Segoe UI
FontSize=22
FontColor=180,210,255,(#A#)
AntiAlias=1
DynamicVariables=1
""")

    # --- Hero.ini: фон, сквозной для мыши
    os.makedirs(os.path.join(SKIN, "Hero"), exist_ok=True)
    open(os.path.join(SKIN, "Hero", "Hero.ini"), "w", encoding="utf-16").write(f"""[Rainmeter]
Update=-1

[Metadata]
Name=MARKIZ PS Hero
Information=Фон выбранной игры на весь экран

[Variables]
A=0

; Плавное появление (1) и исчезновение (2) фона, 12 шагов по 25 мс
[mFade]
Measure=Plugin
Plugin=ActionTimer
ActionList1=Stop2 | SetZero | Repeat Up,25,12
ActionList2=Stop1 | Repeat Down,25,12
Stop1=[!CommandMeasure mFade "Stop 1"]
Stop2=[!CommandMeasure mFade "Stop 2"]
SetZero=[!SetVariable A 0][!UpdateMeter Bg][!Redraw]
Up=[!SetVariable A "(Clamp(#A#+22,0,255))"][!UpdateMeter Bg][!Redraw]
Down=[!SetVariable A "(Clamp(#A#-22,0,255))"][!UpdateMeter Bg][!Redraw]
DynamicVariables=1

[Bg]
Meter=Image
ImageName=
W={W}
H={H}
PreserveAspectRatio=2
ImageAlpha=#A#
DynamicVariables=1
""")

    # --- Home.ini
    DEF = 1  # при запуске выбрана последняя игра, в которую играли (сразу после магазина)
    card_images(gdir)
    sounds(os.path.join(RES, "sounds"))
    ini = [f"""[Rainmeter]
Update=1000
AccurateText=1
OnRefreshAction={sel[DEF]}

[Metadata]
Name=MARKIZ PS Home
Information=Главный экран в стиле PS5: вкладки, ряд игр, логотип и кнопка Играть

[Variables]
Font=Segoe UI
Run=
Cur=-1
K=0
{MEASURES}
; Плавное увеличение плитки под мышкой: 6 шагов по 16 мс, в конце — белая рамка
[mGrow]
Measure=Plugin
Plugin=ActionTimer
ActionList1=Repeat Step,16,6 | Ring
Step=[!SetVariable K "(Clamp(#K#+1,0,6))"][!UpdateMeterGroup Games][!UpdateMeterGroup Media][!Redraw]
Ring=[!ShowMeter Ring][!UpdateMeter Ring][!Redraw]
DynamicVariables=1

[TabGames]
Meter=String
Text=Игры
X={X0}
Y=60
FontFace=#Font# Semibold
FontSize=26
FontColor=255,255,255,255
StringEffect=Shadow
FontEffectColor=0,0,0,120
AntiAlias=1
SolidColor=0,0,0,1
LeftMouseUpAction=[!SetOption TabGames FontColor "255,255,255,255"][!SetOption TabMedia FontColor "255,255,255,130"][!ShowMeterGroup Games][!HideMeterGroup Media]{sel[DEF]}

[TabMedia]
Meter=String
Text=Медиа
X=40R
Y=60
FontFace=#Font# Semibold
FontSize=26
FontColor=255,255,255,130
StringEffect=Shadow
FontEffectColor=0,0,0,120
AntiAlias=1
SolidColor=0,0,0,1
LeftMouseUpAction=[!SetOption TabMedia FontColor "255,255,255,255"][!SetOption TabGames FontColor "255,255,255,130"][!HideMeterGroup Games][!ShowMeterGroup Media][!CommandMeasure mFade "Execute 2" "MarkizPS\\Hero"][!UpdateMeter *][!Redraw]
"""]
    def tile(sec, img, i, group, over_extra, run, hidden, label=""):
        x = X0 + i * (T + GAP); y = Y0; d = (TS - T) // 2
        uid = i + (100 if group == "Media" else 0)   # номер плитки для анимации (у «Медиа» свои)
        over_extra = f'[Play "#@#sounds\\move.wav"][!SetOption SelName X {x - d}][!SetOption SelName Y {y - d + TS + 14}][!SetOption SelName Text "{label}"]' + over_extra
        run = f'"{run}"][Play "#@#sounds\\select.wav"'  # звук запуска после команды: LeftMouseUpAction=["путь"][Play ...]
        # Плитка плавно растёт за 6 шагов: K идёт 0..6 у плитки с номером Cur, остальные стоят в покое
        k = f"(#K#/6*(#Cur#={uid}))"
        return f"""
[{sec}]
Meter=Image
ImageName={img}
X=({x}-{d}*{k})
Y=({y}-{d}*{k})
W=({T}+{2 * d}*{k})
H=({T}+{2 * d}*{k})
AntiAlias=1
DynamicVariables=1
Group={group}
Hidden={hidden}
MouseOverAction=[!SetVariable Cur {uid}][!SetVariable K 0][!SetOption Ring X {x - d - 6}][!SetOption Ring Y {y - d - 6}][!HideMeter Ring][!CommandMeasure mGrow "Execute 1"]{over_extra}[!UpdateMeter *][!Redraw]
MouseLeaveAction=[!CommandMeasure mGrow "Stop 1"][!SetVariable Cur -1][!SetVariable K 0][!HideMeter Ring][!UpdateMeter *][!Redraw]
LeftMouseUpAction=[{run}]
"""
    for i, g in enumerate(GAMES):
        ini.append(tile(f"G{i}", f"#@#games\\{g[0]}.png", i, "Games", sel[i], g[5].replace('"', ""), 0, g[1]))
    for i, (label, t, run) in enumerate(MEDIA):
        img = f"#@#tiles\\{t}.png" if t else "#@#games\\youtube.png"
        ini.append(tile(f"M{i}", img, i, "Media", f'[!SetOption Name Text "{label}"][!HideMeter Logo][!ShowMeter Name]', run, 1, label))
    ini.append(header() + cards())
    ini.append(f"""
[Ring]
Meter=Shape
X=0
Y=0
Shape=Rectangle 3,3,{TS + 6},{TS + 6},30 | Fill Color 0,0,0,0 | StrokeWidth 5 | Stroke Color 255,255,255,240
Hidden=1

[SelName]
Meter=String
Text=
X=0
Y={Y0 + TS + 10}
FontFace=#Font#
FontSize=17
FontColor=255,255,255,240
StringEffect=Shadow
FontEffectColor=0,0,0,160
AntiAlias=1
DynamicVariables=1

[Logo]
Meter=Image
ImageName=
X={X0}
Y={Y0 + TS + 70}
W=480
H=140
PreserveAspectRatio=1
AntiAlias=1

[Name]
Meter=String
Text=
X={X0}
Y={Y0 + TS + 80}
FontFace=#Font# Semibold
FontSize=48
FontColor=255,255,255,255
StringEffect=Shadow
FontEffectColor=0,0,0,160
AntiAlias=1
Hidden=1

[Play]
Meter=Shape
X={X0}
Y={Y0 + TS + 200}
Shape=Rectangle 0,0,260,72,36 | Fill Color 255,255,255,245 | StrokeWidth 0
Group=Games
DynamicVariables=1
MouseOverAction=[!SetOption Play Shape "Rectangle 0,0,260,72,36 | Fill Color 255,255,255,255 | StrokeWidth 4 | Stroke Color 90,170,255,255"][!UpdateMeter Play][!Redraw]
MouseLeaveAction=[!SetOption Play Shape "Rectangle 0,0,260,72,36 | Fill Color 255,255,255,245 | StrokeWidth 0"][!UpdateMeter Play][!Redraw]
LeftMouseUpAction=["#Run#"][Play "#@#sounds\\select.wav"]

[PlayText]
Meter=String
Text=Играть
X={X0 + 130}
Y={Y0 + TS + 236}
StringAlign=CenterCenter
FontFace=#Font# Semibold
FontSize=22
FontColor=10,20,40,255
AntiAlias=1
Group=Games
DynamicVariables=1
LeftMouseUpAction=["#Run#"][Play "#@#sounds\\select.wav"]
""")
    open(os.path.join(SKIN, "Home", "Home.ini"), "w", encoding="utf-16").write("".join(ini))
    print(SKIN, len(GAMES), "games")

if __name__ == "__main__":
    main()
