# MARKIZ PS5

Оформление компьютера и планшета в стиле консоли: синие живые обои, главный экран с играми, карточки и нижняя панель. Всё рисуется скриптами на Python.

> Фанатский проект. Не связан с Sony Interactive Entertainment и не одобрен ею. «PlayStation» и «PS5» — товарные знаки Sony; их логотипов, шрифтов и звуков здесь нет, вся графика и звуки нарисованы и сгенерированы с нуля.

![Планшет](tablet/ps_preview.jpg)

## Что внутри

**`tablet/` — скрипты, которые рисуют оформление**

| Скрипт | Что делает |
|---|---|
| `make_wall.py` | Обои «MARKIZ NIGHT»: ночной неоновый город и кот Маркиз |
| `make_theme.py` | Неоновые иконки и тема Huawei (`.hwt`) |
| `make_ps.py` | Синие обои с волнами и цветные плитки-иконки |
| `make_iconpack.py` | Пакет иконок (APK) для Lawnchair, Nova и других лаунчеров |
| `make_pc_wall.py` | Синие обои под экран компьютера 2560x1440 |
| `make_pc_ps.py` | Иконки папок и первая версия плиток для Rainmeter |
| `make_pc_home.py` | Главный экран для Rainmeter: ряд игр, фон игры, кнопка «Играть», карточки (система, погода, диски, MARKIZ LAND, Steam, время в играх, звук и питание), заставка |
| `make_pc_dock.py` | Нижняя панель: «Домой», программы, звук, сеть, уведомления, время, питание |
| `make_cursor.py` | Курсор: белая стрелка с синей обводкой |

**`wallpaper_engine/markiz_ps5/`** — живые обои для Wallpaper Engine: синий фон с волнами и огоньками.

**`windows/`** — откат и настройки Windows:
- `ВЕРНУТЬ_КАК_БЫЛО.ps1` возвращает прежнее оформление;
- `set_scale.ps1` меняет масштаб экрана;
- `start_button_styler.txt` — настройки мода Windhawk для своего значка на кнопке «Пуск».

## Что нужно

- Python 3 с библиотеками `pillow` и `cryptography`.
- Google Chrome: картинки рисуются в HTML/SVG и снимаются Chrome без окна.
- Rainmeter, Wallpaper Engine, TranslucentTB и Windhawk — для оформления компьютера.
- Для пакета иконок: Android build-tools (`aapt2`, `zipalign`) и `android.jar` в `%USERPROFILE%\android-build`.

Обложки игр берутся из кэша Steam на твоём компьютере, поэтому в репозитории их нет.

Для пакета иконок нужен список приложений планшета `tablet/components.txt` (его нет в репозитории). Получить его можно так, при подключённом по USB устройстве:

```
adb shell cmd package query-activities --brief -a android.intent.action.MAIN -c android.intent.category.LAUNCHER > tablet/components.txt
```

## Лицензия

MIT — см. [LICENSE](LICENSE).
