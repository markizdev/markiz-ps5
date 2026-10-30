# Общие настройки для скриптов рисования: где лежит Chrome (картинки рисуются HTML/SVG и фотографируются
# безголовым Chrome) и отдельный профиль для него, чтобы не трогать основной браузер.
import os

HERE = os.path.dirname(os.path.abspath(__file__))
CHROME = next((p for p in (r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                           r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                           os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe")) if os.path.exists(p)), None)
PROFILE_DIR = os.path.join(os.environ.get("TEMP", HERE), "mkz_chrome_art")
