# Настройки из файла «настройки.txt» в корне проекта + автоопределение экрана.
# Все размеры главного экрана и нижней панели нарисованы под 2560x1440; SC — во сколько раз их уменьшить/увеличить.
import ctypes, getpass, json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SETTINGS = os.path.join(ROOT, "настройки.txt")
APPS_JSON = os.path.join(HERE, "ps_build", "apps.json")  # что нашёл установщик (см. install/install.ps1)

DEFAULTS = {"ГОРОД": "Moscow", "ГОРОД_ПОДПИСЬ": "Москва", "ЭКРАН": "авто", "ИГР_ИЗ_STEAM": "8", "ИМЯ": "авто"}

def _read():
    cfg = dict(DEFAULTS)
    if os.path.exists(SETTINGS):
        for line in open(SETTINGS, encoding="utf-8-sig"):
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                cfg[k.strip().upper()] = v.strip()
    return cfg

def _screen():
    """Настоящее разрешение основного экрана (без учёта масштаба Windows)"""
    try:
        ctypes.windll.user32.SetProcessDPIAware()
        return ctypes.windll.user32.GetSystemMetrics(0), ctypes.windll.user32.GetSystemMetrics(1)
    except Exception:
        return 1920, 1080

CFG = _read()
m = re.match(r"(\d+)\s*[xх×]\s*(\d+)", CFG["ЭКРАН"])
SCREEN_W, SCREEN_H = (int(m.group(1)), int(m.group(2))) if m else _screen()
SC = min(SCREEN_W / 2560, SCREEN_H / 1440)
from urllib.parse import quote
CITY = quote(CFG["ГОРОД"].replace(" ", "+"), safe="+")  # можно и по-русски: «Казань» превратится в %D0%9A...
CITY_LABEL = CFG["ГОРОД_ПОДПИСЬ"]
MAX_STEAM = int(CFG["ИГР_ИЗ_STEAM"]) if CFG["ИГР_ИЗ_STEAM"].isdigit() else 8
NAME = getpass.getuser().split()[0] if CFG["ИМЯ"].lower() == "авто" else CFG["ИМЯ"]

def _skins_root():
    """Папка скинов Rainmeter: берём из его настроек (SkinPath), иначе «Документы\\Rainmeter\\Skins»"""
    ini = os.path.join(os.environ.get("APPDATA", ""), "Rainmeter", "Rainmeter.ini")
    if os.path.exists(ini):
        for enc in ("utf-16", "utf-8-sig", "mbcs"):
            try:
                m = re.search(r"^SkinPath=(.+)$", open(ini, encoding=enc).read(), re.M)
                if m:
                    return m.group(1).strip().rstrip("\\")
                break
            except (UnicodeError, LookupError):
                continue
    try:  # настоящая папка «Документы» (бывает перенесена в OneDrive)
        buf = ctypes.create_unicode_buffer(260)
        ctypes.windll.shell32.SHGetFolderPathW(None, 5, None, 0, buf)
        return os.path.join(buf.value, "Rainmeter", "Skins")
    except Exception:
        return os.path.join(os.path.expanduser("~"), "Documents", "Rainmeter", "Skins")

SKIN = os.environ.get("MARKIZ_SKIN") or os.path.join(_skins_root(), "MarkizPS")  # MARKIZ_SKIN — для проверки в другой папке

def found_apps():
    """Программы, которые нашёл установщик: {"extra": [...], "dock": [...]}; None, если установщик не запускали"""
    if os.path.exists(APPS_JSON):
        return json.load(open(APPS_JSON, encoding="utf-8-sig"))
    return None

# --- масштабирование готового INI скина под экран ---
_GEOM_KEYS = re.compile(r"^(X|Y|W|H|FontSize|LineLength|LineStart)=(.*)$", re.M)
_NUM = re.compile(r"(?<![#\w.])(-?\d+(?:\.\d+)?)")

def _scale_nums(s):
    return _NUM.sub(lambda m: str(round(float(m.group(1)) * SC)), s)

def _scale_shape(s):
    """Rectangle/Ellipse: масштабируем только геометрию (до первого «|») и толщину линии, цвета не трогаем"""
    parts = s.split("|")
    parts[0] = _scale_nums(parts[0])
    for i in range(1, len(parts)):
        if parts[i].strip().startswith("StrokeWidth"):
            parts[i] = _scale_nums(parts[i])
    return "|".join(parts)

def scale_ini(text):
    if abs(SC - 1) < 1e-3:
        return text
    keep = {}
    def protect(m):  # числа внутри формул анимации плиток (#K#/6, #Cur#=101) — не размеры
        n, tag = len(keep), ""
        while True:  # метка из одних букв, чтобы масштабирование цифр её не задело
            tag = chr(65 + n % 26) + tag; n //= 26
            if not n: break
        tag = f"@@{tag}@@"; keep[tag] = m.group(0); return tag
    text = re.sub(r"#K#/6|#Cur#=\d+|Clamp\([^)]*\)", protect, text)
    text = _GEOM_KEYS.sub(lambda m: f"{m.group(1)}={_scale_nums(m.group(2))}", text)
    text = re.sub(r"^(Shape\d*)=(.*)$", lambda m: f"{m.group(1)}={_scale_shape(m.group(2))}", text, flags=re.M)
    text = re.sub(r'(!SetOption \S+ (?:X|Y|W|H) )(-?\d+)', lambda m: m.group(1) + _scale_nums(m.group(2)), text)
    text = re.sub(r'(!SetOption \S+ Shape ")([^"]*)(")', lambda m: m.group(1) + _scale_shape(m.group(2)) + m.group(3), text)
    for k, v in keep.items():
        text = text.replace(k, v)
    return text
