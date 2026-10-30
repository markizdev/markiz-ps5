# Нижняя панель в стиле консольного «центра управления» (скин Rainmeter MarkizPS\Dock).
# Плавающая стеклянная полоса по центру снизу: «Домой», ярлыки программ, громкость, сеть, уведомления, время, питание.
# Иконки программ достаёт PowerShell в ps_build/dockicons (через shell:AppsFolder), здесь они кладутся на тёмные кнопки.
import os
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
from config import SKIN  # папка скинов Rainmeter этого компьютера
ICONS = os.path.join(HERE, "ps_build", "dockicons")
from config import SCREEN_W, SCREEN_H, SC, scale_ini, found_apps  # экран и программы этого компьютера
B, GAP, PAD, HGT = 64, 14, 18, 96   # кнопка, промежуток, поля, высота панели

# (ключ иконки, подпись, AppID для shell:AppsFolder)
APPS = [
    ("telegram", "Telegram", "TelegramMessengerLLP.TelegramDesktop_t4vj0pshhgkwm!Telegram.TelegramDesktop.Store"),
    ("discord", "Discord", "com.squirrel.Discord.Discord"),
    ("chrome", "Chrome", "Chrome"),
    ("yandex", "Яндекс", "Yandex.4C5BATT3O2Q6RZ4XM2A275W6EY"),
    ("explorer", "Проводник", "Microsoft.Windows.Explorer"),
    ("claude", "Claude", "Claude_pzs8sxrjxfjjc!Claude"),
    ("terminal", "Терминал", "Microsoft.WindowsTerminal_8wekyb3d8bbwe!App"),
]
# Если запускали установщик — его список программ этого компьютера; без иконки кнопку не ставим
_found = found_apps()
if _found is not None:
    APPS = [(a["key"], a["name"], a["appid"]) for a in _found.get("dock", [])]
APPS = [a for a in APPS if os.path.exists(os.path.join(ICONS, a[0] + ".png"))]

# (секция, глиф Segoe Fluent Icons, подсказка, действие)
CONTROLS = [
    ("CNet", "", "Сеть", '["ms-availablenetworks:"]'),
    ("CNote", "", "Уведомления", '["ms-actioncenter:"]'),
    ("CPower", "", "Двойной клик — выключить", None),
]

def button_png(key):
    """Иконка программы на тёмной скруглённой подложке 128x128"""
    t = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
    ImageDraw.Draw(t).rounded_rectangle((0, 0, 127, 127), 30, fill=(255, 255, 255, 18))
    ic = Image.open(os.path.join(ICONS, key + ".png")).convert("RGBA")
    ic = ic.crop(ic.getbbox()); k = 84 / max(ic.size)
    ic = ic.resize((max(1, int(ic.width * k)), max(1, int(ic.height * k))), Image.LANCZOS)
    t.alpha_composite(ic, ((128 - ic.width) // 2, (128 - ic.height) // 2))
    return t

def main():
    res = os.path.join(SKIN, "@Resources", "dock"); os.makedirs(res, exist_ok=True)
    os.makedirs(os.path.join(SKIN, "Dock"), exist_ok=True)
    for k, _, _ in APPS:
        button_png(k).save(os.path.join(res, k + ".png"))

    n_btn = 1 + len(APPS)                       # «Домой» + программы
    w_left = n_btn * B + (n_btn - 1) * GAP
    w_right = 4 * 56 + 3 * 10 + 150             # громкость, сеть, уведомления, питание + время
    W = PAD * 2 + w_left + 40 + w_right
    # панель рисуется в размерах для 2560x1440, scale_ini подгоняет её под экран — позицию считаем уже в настоящих пикселях
    x0 = int((SCREEN_W - W * SC) // 2); y0 = int(SCREEN_H - (HGT + 18) * SC)
    yb = (HGT - B) // 2

    def hover(sec, shape_on, shape_off):
        return (f'MouseOverAction=[!SetOption {sec} Shape "{shape_on}"][!UpdateMeter {sec}][!Redraw]\n'
                f'MouseLeaveAction=[!SetOption {sec} Shape "{shape_off}"][!UpdateMeter {sec}][!Redraw]\n')

    off = f"Rectangle 0,0,{B},{B},18 | Fill Color 0,0,0,1 | StrokeWidth 0"
    on = f"Rectangle 0,0,{B},{B},18 | Fill Color 255,255,255,40 | StrokeWidth 2 | Stroke Color 255,255,255,200"
    ini = f"""[Rainmeter]
Update=1000
AccurateText=1

[Metadata]
Name=MARKIZ PS Dock
Information=Нижняя панель как центр управления консоли: домой, программы, звук, сеть, уведомления, время, питание

[mTime]
Measure=Time
Format=%H:%M

[mDate]
Measure=Time
Format=%a, %#d %b
FormatLocale=ru-RU

[mVol]
Measure=Plugin
Plugin=Win7AudioPlugin

[mVolPct]
Measure=Calc
Formula=Max(mVol, 0)

[mVolIcon]
Measure=Calc
Formula=(mVol < 0) ? 0 : (mVol < 34 ? 1 : (mVol < 67 ? 2 : 3))
RegExpSubstitute=1
Substitute="^0$":"","^1$":"","^2$":"","^3$":""

[Panel]
Meter=Shape
X=0
Y=0
Shape=Rectangle 0,0,{W},{HGT},30 | Fill LinearGradient PG | StrokeWidth 1.5 | Stroke Color 255,255,255,55
PG=90 | 22,44,100,225 ; 0.0 | 8,16,44,235 ; 1.0

[Home]
Meter=Shape
X={PAD}
Y={yb}
Shape={off}
{hover("Home", on, off)}LeftMouseUpAction=[!CommandMeasure mShowDesktop "Run"][Play "#@#sounds\\select.wav"]
ToolTipText=Домой — показать рабочий стол

[HomeIc]
Meter=String
Text=
X={PAD + B // 2}
Y={yb + B // 2}
StringAlign=CenterCenter
FontFace=Segoe Fluent Icons
FontSize=22
FontColor=255,255,255,245
AntiAlias=1

[mShowDesktop]
Measure=Plugin
Plugin=RunCommand
Program=powershell.exe
Parameter=-NoProfile -WindowStyle Hidden -Command "(New-Object -ComObject Shell.Application).ToggleDesktop()"
State=Hide
"""
    for i, (k, label, appid) in enumerate(APPS):
        x = PAD + (i + 1) * (B + GAP)
        ini += f"""
[A{i}]
Meter=Shape
X={x}
Y={yb}
Shape={off}
{hover(f"A{i}", on, off)}LeftMouseUpAction=["explorer.exe" "shell:AppsFolder\\{appid}"][Play "#@#sounds\\select.wav"]
ToolTipText={label}

[A{i}Img]
Meter=Image
ImageName=#@#dock\\{k}.png
X={x}
Y={yb}
W={B}
H={B}
AntiAlias=1
"""
    xs = PAD + w_left + 20
    ini += f"""
[Sep]
Meter=Shape
X={xs}
Y={HGT // 2 - 26}
Shape=Rectangle 0,0,2,52,1 | Fill Color 255,255,255,60 | StrokeWidth 0
"""
    cx = xs + 20
    s_off = "Rectangle 0,0,56,56,16 | Fill Color 0,0,0,1 | StrokeWidth 0"
    s_on = "Rectangle 0,0,56,56,16 | Fill Color 255,255,255,40 | StrokeWidth 2 | Stroke Color 255,255,255,200"
    # громкость: клик — выключить звук, колёсико — громче/тише
    ini += f"""
[CVol]
Meter=Shape
X={cx}
Y={(HGT - 56) // 2}
Shape={s_off}
{hover("CVol", s_on, s_off)}LeftMouseUpAction=[!CommandMeasure mVol "ToggleMute"][!UpdateMeasure *][!UpdateMeter *][!Redraw]
MouseScrollUpAction=[!CommandMeasure mVol "ChangeVolume 5"][!UpdateMeasure *][!UpdateMeter *][!Redraw]
MouseScrollDownAction=[!CommandMeasure mVol "ChangeVolume -5"][!UpdateMeasure *][!UpdateMeter *][!Redraw]
ToolTipText=Звук: клик — выкл/вкл, колёсико — громкость

[CVolIc]
Meter=String
Text=[mVolIcon]
X={cx + 28}
Y={HGT // 2}
StringAlign=CenterCenter
FontFace=Segoe Fluent Icons
FontSize=19
FontColor=255,255,255,245
AntiAlias=1
DynamicVariables=1
"""
    for j, (sec, glyph, tip, act) in enumerate(CONTROLS):
        x = cx + (j + 1) * 66
        action = f"LeftMouseUpAction={act}" if act else 'LeftMouseDoubleClickAction=["shutdown.exe" /s /t 0]'
        ini += f"""
[{sec}]
Meter=Shape
X={x}
Y={(HGT - 56) // 2}
Shape={s_off}
{hover(sec, s_on, s_off)}{action}
ToolTipText={tip}

[{sec}Ic]
Meter=String
Text={glyph}
X={x + 28}
Y={HGT // 2}
StringAlign=CenterCenter
FontFace=Segoe Fluent Icons
FontSize=19
FontColor=255,255,255,245
AntiAlias=1
"""
    tx = W - PAD - 8
    ini += f"""
[Time]
Meter=String
MeasureName=mTime
X={tx}
Y={HGT // 2 - 30}
StringAlign=Right
FontFace=Segoe UI Semibold
FontSize=20
FontColor=255,255,255,250
AntiAlias=1

[Date]
Meter=String
MeasureName=mDate
X={tx}
Y={HGT // 2 + 4}
StringAlign=Right
StringCase=Lower
FontFace=Segoe UI
FontSize=12
FontColor=200,220,255,220
AntiAlias=1
"""
    open(os.path.join(SKIN, "Dock", "Dock.ini"), "w", encoding="utf-16").write(scale_ini(ini))
    print(x0, y0, W)

if __name__ == "__main__":
    main()
