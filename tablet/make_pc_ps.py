# Оформление компьютера в стиле PS5, вторая часть:
#  - иконки папок на рабочем столе (цветные плитки как на планшете) -> %LOCALAPPDATA%\FolderIconsPS\*.ico
#  - скин Rainmeter MarkizPS: ряд плиток-ярлыков (Home.ini) и часы с погодой и загрузкой ПК (Clock.ini)
# Плитки рисует tile_svg из make_ps.py, глифы берутся из make_theme.py.
import os
from PIL import Image
from make_theme import G, T
from make_ps import tile_svg, shot, BUILD, PX

HERE = os.path.dirname(os.path.abspath(__file__))
HOME = os.path.expanduser("~")
ICO_DIR = os.path.join(os.environ["LOCALAPPDATA"], "FolderIconsPS")
from config import SKIN  # папка скинов Rainmeter этого компьютера
SM_USER = os.path.join(os.environ["APPDATA"], r"Microsoft\Windows\Start Menu\Programs")
SM_ALL = r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs"

BLUE, PURP, ORG, GRN, RED, YEL, CYAN, GRAY = "#36e6ff", "#b04dff", "#ff8a3d", "#3dffa8", "#ff4d6d", "#ffd23d", "#36e6ff", "#7b8798"

# Папки рабочего стола: имя файла иконки -> (глиф, цвет)
FOLDERS = {"docs": ("note", BLUE), "games": ("pad", PURP), "pictures": ("photo", YEL),
           "mods": ("gear", ORG), "apps": ("keys", GRN), "misc": ("folder", CYAN)}

# Плитки-ярлыки: (подпись, глиф, цвет плитки как ключ BRAND/GRAD, что запускать)
TILES = [
    ("Steam", "pad", ("#2a475e", "#171a21"), os.path.join(SM_USER, r"Steam\Steam.lnk")),
    ("Epic Games", T("E", 13), ("#4a4a4a", "#121212"), os.path.join(SM_ALL, "Epic Games Launcher.lnk")),
    ("Roblox", T("R", 13), ("#ff5a5a", "#c8102e"), os.path.join(SM_USER, r"Roblox\Roblox Player.lnk")),
    ("The Last of Us", "cross", ("#5fa36a", "#1f4d2b"), os.path.join(SM_ALL, r"The last of Us. Part 1\The last of Us. Part 1.lnk")),
    ("Discord", "chat", ("#7983f5", "#4752c4"), os.path.join(SM_USER, "Discord.lnk")),
    ("Chrome", "globe", ("#3fb4ff", "#1460d8"), os.path.join(SM_ALL, "Google Chrome.lnk")),
    ("Яндекс", "search", ("#ff5240", "#d81b00"), os.path.join(SM_USER, "Yandex.lnk")),
    ("Проводник", "folder", ("#ffc93d", "#f08a00"), "explorer.exe"),
    ("Настройки", "gear", ("#7b8798", "#3e4756"), "ms-settings:"),
]

def render_tiles(items, out_dir):
    """items: [(имя_файла, глиф, (c1, c2) или цвет)] -> PNG 192x192 в out_dir"""
    os.makedirs(BUILD, exist_ok=True); os.makedirs(out_dir, exist_ok=True)
    cells = ""
    for i, (name, glyph, col) in enumerate(items):
        svg = tile_svg(1000 + i, "", glyph, col if isinstance(col, str) else "")
        if not isinstance(col, str):  # явная пара цветов градиента
            svg = svg.replace('stop-color="#5a7cff"', f'stop-color="{col[0]}"').replace('stop-color="#2a3fb8"', f'stop-color="{col[1]}"')
        cells += f'<div style="position:absolute;left:{i * PX}px;top:0">{svg}</div>'
    sheet = os.path.join(BUILD, "_pc_sheet.png")
    shot(f'<html><body style="margin:0;background:transparent">{cells}</body></html>', sheet, len(items) * PX, PX)
    im = Image.open(sheet).convert("RGBA")
    paths = []
    for i, (name, _, _) in enumerate(items):
        p = os.path.join(out_dir, name + ".png")
        im.crop((i * PX, 0, (i + 1) * PX, PX)).save(p); paths.append(p)
    return paths

def folder_icons():
    pngs = render_tiles([(k, g, c) for k, (g, c) in FOLDERS.items()], ICO_DIR)
    for p in pngs:
        Image.open(p).save(p[:-4] + ".ico", sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
        os.remove(p)

HOME_INI = """[Rainmeter]
Update=1000
AccurateText=1

[Metadata]
Name=MARKIZ PS Home
Information=Ряд плиток в стиле PS5: наведи - плитка подсвечивается, клик - запуск

[Variables]
Font=Segoe UI
Tile=120
Gap=26

[Header]
Meter=String
Text=Игры      Медиа
X=4
Y=0
FontFace=#Font# Semilight
FontSize=22
FontColor=255,255,255,235
InlineSetting=Color | 255,255,255,120
InlinePattern=Медиа
StringEffect=Shadow
FontEffectColor=0,10,40,140
AntiAlias=1
"""

TILE_TMPL = """
[Glow{i}]
Meter=Shape
X={gx}
Y=58
Shape=Rectangle 0,0,138,138,30 | Fill Color 0,0,0,0 | StrokeWidth 4 | Stroke Color 255,255,255,0
Hidden=0

[Tile{i}]
Meter=Image
ImageName=#@#tiles\\{n}.png
X={x}
Y=67
W=#Tile#
H=#Tile#
AntiAlias=1
MouseOverAction=[!SetOption Glow{i} Shape "Rectangle 0,0,138,138,30 | Fill Color 255,255,255,25 | StrokeWidth 4 | Stroke Color 255,255,255,230"][!ShowMeter Label{i}][!UpdateMeter *][!Redraw]
MouseLeaveAction=[!SetOption Glow{i} Shape "Rectangle 0,0,138,138,30 | Fill Color 0,0,0,0 | StrokeWidth 4 | Stroke Color 255,255,255,0"][!HideMeter Label{i}][!UpdateMeter *][!Redraw]
LeftMouseUpAction=["{run}"]

[Label{i}]
Meter=String
Text={label}
X={lx}
Y=206
StringAlign=Center
FontFace=#Font# Semibold
FontSize=14
FontColor=255,255,255,240
StringEffect=Shadow
FontEffectColor=0,10,40,160
AntiAlias=1
Hidden=1
"""

CLOCK_INI = """[Rainmeter]
Update=1000
AccurateText=1
DynamicWindowSize=1

[Metadata]
Name=MARKIZ PS Clock
Information=Часы, погода и загрузка ПК в стиле PS5

[Variables]
City=
Font=Segoe UI
Blue=0,112,209,255
Light=120,190,255,255

[mTime]
Measure=Time
Format=%H:%M

[mDate]
Measure=Time
Format=%A, %#d %B
FormatLocale=ru-RU

[mCPU]
Measure=CPU

[mRAM]
Measure=PhysicalMemory
UpdateDivider=2

[mRAMTotal]
Measure=PhysicalMemory
Total=1
UpdateDivider=-1

[mRAMPct]
Measure=Calc
Formula=Round(mRAM / mRAMTotal * 100)

[mWeather]
Measure=WebParser
URL=https://wttr.in/#City#?format=%t|%C&lang=ru
CodePage=65001
RegExp=(?siU)^\\s*(.*)\\|(.*)\\s*$
UpdateRate=1800
FinishAction=[!UpdateMeter Weather][!Redraw]

[mTemp]
Measure=WebParser
URL=[mWeather]
StringIndex=1
Substitute="+":""

[mCond]
Measure=WebParser
URL=[mWeather]
StringIndex=2

[Panel]
Meter=Shape
X=0
Y=0
Shape=Rectangle 0,0,440,300,28 | Fill LinearGradient PanelGrad | StrokeWidth 1.5 | Stroke Color 255,255,255,60
PanelGrad=90 | 20,50,120,170 ; 0.0 | 5,16,58,200 ; 1.0

[Time]
Meter=String
MeasureName=mTime
X=30
Y=14
FontFace=#Font# Light
FontSize=72
FontColor=255,255,255,250
AntiAlias=1

[Date]
Meter=String
MeasureName=mDate
X=34
Y=-6R
StringCase=Lower
FontFace=#Font# Semilight
FontSize=16
FontColor=200,225,255,230
AntiAlias=1

[Weather]
Meter=String
MeasureName=mTemp
MeasureName2=mCond
Text=%1  ·  %2
X=34
Y=8R
FontFace=#Font#
FontSize=13
FontColor=255,255,255,220
AntiAlias=1

[CPULabel]
Meter=String
MeasureName=mCPU
Text=Процессор  %1%
X=34
Y=16R
FontFace=#Font#
FontSize=11
FontColor=200,225,255,200
AntiAlias=1

[CPUBar]
Meter=Bar
MeasureName=mCPU
X=200
W=200
H=6
Y=8r
BarColor=#Light#
SolidColor=255,255,255,40
BarOrientation=Horizontal

[RAMLabel]
Meter=String
MeasureName=mRAMPct
Text=Память  %1%
X=34
Y=10R
FontFace=#Font#
FontSize=11
FontColor=200,225,255,200
AntiAlias=1

[RAMBar]
Meter=Bar
MeasureName=mRAM
X=200
Y=8r
W=200
H=6
BarColor=#Light#
SolidColor=255,255,255,40
BarOrientation=Horizontal
"""

def rainmeter_skin():
    os.makedirs(os.path.join(SKIN, "Home"), exist_ok=True); os.makedirs(os.path.join(SKIN, "Clock"), exist_ok=True)
    render_tiles([(f"t{i}", g, c) for i, (_, g, c, _) in enumerate(TILES)], os.path.join(SKIN, "@Resources", "tiles"))
    ini = HOME_INI
    for i, (label, _, _, run) in enumerate(TILES):
        x = 9 + i * 146
        ini += TILE_TMPL.format(i=i, n=f"t{i}", x=x, gx=x - 9, lx=x + 60, label=label, run=run)
    open(os.path.join(SKIN, "Home", "Home.ini"), "w", encoding="utf-16").write(ini)
    open(os.path.join(SKIN, "Clock", "Clock.ini"), "w", encoding="utf-16").write(CLOCK_INI)

if __name__ == "__main__":
    folder_icons()
    rainmeter_skin()
    print(ICO_DIR, SKIN)
