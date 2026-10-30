# Установщик MARKIZ PS5: ставит нужные программы, находит игры и программы этого компьютера,
# рисует оформление и включает его в Rainmeter. Запускается через УСТАНОВИТЬ.bat.
$ErrorActionPreference = "Stop"
$Root = Split-Path $PSScriptRoot -Parent
$Tablet = Join-Path $Root "tablet"
$Build = Join-Path $Tablet "ps_build"
$Settings = Join-Path $Root "настройки.txt"
$Backup = Join-Path $PSScriptRoot "backup.json"

function Step($n, $text) { Write-Host ""; Write-Host "[$n/7] $text" -ForegroundColor Cyan }
function Ok($text) { Write-Host "  + $text" -ForegroundColor Green }
function Warn($text) { Write-Host "  ! $text" -ForegroundColor Yellow }
function Refresh-Path { $env:Path = [Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [Environment]::GetEnvironmentVariable("Path", "User") }

Write-Host "=============================================" -ForegroundColor Blue
Write-Host "        MARKIZ PS5 — установка оформления" -ForegroundColor White
Write-Host "=============================================" -ForegroundColor Blue

# ---------- 1. Программы ----------
Step 1 "Проверяю программы"
function Find-Python {
    foreach ($c in @("py", "python")) {
        $cmd = Get-Command $c -ErrorAction SilentlyContinue
        if ($cmd -and $cmd.Source -notlike "*WindowsApps*") {  # заглушка из Microsoft Store не считается
            $exe = & $cmd.Source -c "import sys; print(sys.executable)" 2>$null
            if ($LASTEXITCODE -eq 0 -and $exe) { return $exe.Trim() }
        }
    }
    $p = Get-ChildItem "$env:LOCALAPPDATA\Programs\Python\Python3*\python.exe" -ErrorAction SilentlyContinue | Sort-Object FullName -Descending | Select-Object -First 1
    if ($p) { return $p.FullName }
    return $null
}
$chromePaths = @("$env:ProgramFiles\Google\Chrome\Application\chrome.exe", "${env:ProgramFiles(x86)}\Google\Chrome\Application\chrome.exe", "$env:LOCALAPPDATA\Google\Chrome\Application\chrome.exe")
$rmExe = "$env:ProgramFiles\Rainmeter\Rainmeter.exe"
$need = @()
if (-not (Find-Python)) { $need += @{ id = "Python.Python.3.12"; name = "Python" } }
if (-not ($chromePaths | Where-Object { Test-Path $_ })) { $need += @{ id = "Google.Chrome"; name = "Google Chrome" } }
if (-not (Test-Path $rmExe)) { $need += @{ id = "Rainmeter.Rainmeter"; name = "Rainmeter" } }

if ($need.Count -gt 0) {
    Write-Host "  Не хватает: $(($need | ForEach-Object { $_.name }) -join ', ')"
    if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
        Warn "Нет winget. Поставь эти программы вручную и запусти установщик ещё раз."; exit 1
    }
    $ans = Read-Host "  Установить их сейчас с официальных сайтов? (Д/Н)"
    if ($ans -notmatch "^[ДдYy]") { Warn "Без них оформление не заработает. Выход."; exit 1 }
    foreach ($n in $need) {
        Write-Host "  Ставлю $($n.name)..."
        winget install --id $n.id -e --source winget --accept-package-agreements --accept-source-agreements --silent | Out-Null
    }
    Refresh-Path
}
$Py = Find-Python
if (-not $Py) { Warn "Python не нашёлся даже после установки. Перезапусти компьютер и запусти установщик ещё раз."; exit 1 }
if (-not (Test-Path $rmExe)) { Warn "Rainmeter не установился. Поставь его с rainmeter.net и запусти установщик ещё раз."; exit 1 }
Ok "Python: $Py"
Ok "Rainmeter и Chrome на месте"

Write-Host "  Ставлю библиотеки для Python..."
& $Py -m pip install --user --quiet --disable-pip-version-check pillow cryptography
if ($LASTEXITCODE -ne 0) { Warn "Не получилось поставить библиотеки (pillow, cryptography). Проверь интернет."; exit 1 }
Ok "Библиотеки готовы"

# ---------- 2. Настройки ----------
Step 2 "Настройки"
$city = Read-Host "  Твой город для погоды (например: Москва, Kazan). Enter — Москва"
if (-not $city) { $city = "Москва" }
$lines = @(
    "# Настройки MARKIZ PS5. После изменений запусти УСТАНОВИТЬ.bat ещё раз.",
    "",
    "# Город для погоды и как его подписать на карточке",
    "ГОРОД = $city",
    "ГОРОД_ПОДПИСЬ = $city",
    "",
    "# Разрешение экрана: «авто» или, например, 1920x1080",
    "ЭКРАН = авто",
    "",
    "# Сколько последних Steam-игр показывать в ряду",
    "ИГР_ИЗ_STEAM = 8",
    "",
    "# Имя в приветствии: «авто» — имя пользователя Windows",
    "ИМЯ = авто"
)
[IO.File]::WriteAllLines($Settings, $lines, (New-Object Text.UTF8Encoding $true))
Ok "Сохранил в настройки.txt"

# ---------- 3. Игры и программы этого компьютера ----------
Step 3 "Ищу игры, лаунчеры и программы"
New-Item -ItemType Directory -Force $Build | Out-Null
$start = Get-StartApps
function Find-App($pattern) { $start | Where-Object { $_.Name -match $pattern } | Select-Object -First 1 }

# лаунчеры и игры не из Steam: (ключ, подпись, по какому названию искать в меню «Пуск»)
$launchers = @(
    @("epic", "Epic Games", "^Epic Games Launcher$"),
    @("roblox", "Roblox", "^Roblox Player$"),
    @("minecraft", "Minecraft", "^(Minecraft Launcher|TLauncher)$"),
    @("battlenet", "Battle.net", "^Battle\.net$"),
    @("ea", "EA app", "^EA$|^EA app$"),
    @("ubisoft", "Ubisoft Connect", "^Ubisoft Connect$"),
    @("riot", "Riot Client", "^Riot Client$"),
    @("rockstar", "Rockstar Games", "^Rockstar Games Launcher$"),
    @("gog", "GOG Galaxy", "^GOG GALAXY")
)
# программы для нижней панели — берём первые 7 найденных
$dockWanted = @(
    @("telegram", "Telegram", "^Telegram"),
    @("discord", "Discord", "^Discord$"),
    @("chrome", "Chrome", "^Google Chrome$"),
    @("yandex", "Яндекс", "^(Yandex|Яндекс)$"),
    @("edge", "Edge", "^Microsoft Edge$"),
    @("firefox", "Firefox", "^Firefox$"),
    @("spotify", "Spotify", "^Spotify"),
    @("explorer", "Проводник", "^(Проводник|File Explorer)$"),
    @("terminal", "Терминал", "^(Терминал|Terminal)$")
)
$extraIcons = @{}; $dockIcons = @{}; $extra = @(); $dock = @()
foreach ($l in $launchers) {
    $a = Find-App $l[2]
    if ($a) { $extraIcons[$l[0]] = "shell:AppsFolder\$($a.AppID)"; $extra += @{ key = $l[0]; name = $l[1]; run = "shell:AppsFolder\$($a.AppID)" } }
}
foreach ($d in $dockWanted) {
    if ($dock.Count -ge 7) { break }
    $a = Find-App $d[2]
    if ($a) { $dockIcons[$d[0]] = "shell:AppsFolder\$($a.AppID)"; $dock += @{ key = $d[0]; name = $d[1]; appid = $a.AppID } }
}
# Steam: путь из реестра, нужен для плитки «Магазин Steam»
$steamExe = (Get-ItemProperty "HKCU:\Software\Valve\Steam" -ErrorAction SilentlyContinue).SteamExe
if ($steamExe -and (Test-Path $steamExe)) { $extraIcons["steam"] = $steamExe; Ok "Steam найден: игры из него подтянутся сами" }
else { Warn "Steam не найден — ряд игр будет без Steam" }

& (Join-Path $Tablet "extract_icons.ps1") -Out (Join-Path $Build "exeicons") -Items $extraIcons | Out-Null
& (Join-Path $Tablet "extract_icons.ps1") -Out (Join-Path $Build "dockicons") -Items $dockIcons | Out-Null
@{ extra = $extra; dock = $dock } | ConvertTo-Json -Depth 4 | Set-Content (Join-Path $Build "apps.json") -Encoding UTF8
Ok "Лаунчеры: $(if ($extra) { ($extra | ForEach-Object { $_.name }) -join ', ' } else { 'не найдены' })"
Ok "Нижняя панель: $(($dock | ForEach-Object { $_.name }) -join ', ')"

# ---------- 4. Рисую оформление ----------
Step 4 "Рисую оформление (минуты две)"
Push-Location $Tablet
try {
    foreach ($s in @("make_ps.py", "make_pc_wall.py", "make_pc_ps.py", "make_pc_home.py")) {
        Write-Host "  $s"
        & $Py $s | Out-Null
        if ($LASTEXITCODE -ne 0) { throw "скрипт $s завершился с ошибкой" }
    }
    $dockPos = (& $Py "make_pc_dock.py") -split " "
    if ($LASTEXITCODE -ne 0) { throw "скрипт make_pc_dock.py завершился с ошибкой" }
} finally { Pop-Location }
Ok "Оформление нарисовано"

# ---------- 5. Rainmeter ----------
Step 5 "Включаю главный экран и нижнюю панель в Rainmeter"
if (-not (Get-Process Rainmeter -ErrorAction SilentlyContinue)) { Start-Process $rmExe; Start-Sleep 5 }
$ini = "$env:APPDATA\Rainmeter\Rainmeter.ini"
# (скин, слой: -2 на рабочем столе / 2 поверх всего, сквозной для мыши, X, Y)
$skins = @(
    @("MarkizPS\Hero", "Hero.ini", -2, 1, 0, 0),
    @("MarkizPS\Home", "Home.ini", -2, 0, 0, 0),
    @("MarkizPS\Dock", "Dock.ini", -2, 0, $dockPos[0], $dockPos[1]),
    @("MarkizPS\Splash", "Splash.ini", 2, 1, 0, 0)
)
& $rmExe !RefreshApp; Start-Sleep 3
foreach ($s in $skins) {
    & $rmExe !WriteKeyValue $s[0] AlwaysOnTop $s[2] $ini
    & $rmExe !WriteKeyValue $s[0] ClickThrough $s[3] $ini
    & $rmExe !WriteKeyValue $s[0] WindowX $s[4] $ini
    & $rmExe !WriteKeyValue $s[0] WindowY $s[5] $ini
    & $rmExe !WriteKeyValue $s[0] Draggable 0 $ini
}
foreach ($s in $skins) { & $rmExe !ActivateConfig $s[0] $s[1]; Start-Sleep 1 }
Ok "Скины включены"

# ---------- 6. Обои ----------
Step 6 "Ставлю синие обои"
$old = (Get-ItemProperty "HKCU:\Control Panel\Desktop").WallPaper
if (-not (Test-Path $Backup)) { @{ wallpaper = $old } | ConvertTo-Json | Set-Content $Backup -Encoding UTF8 }  # запоминаем только самые первые обои
$pics = Join-Path ([Environment]::GetFolderPath("MyPictures")) "MarkizPS5"
New-Item -ItemType Directory -Force $pics | Out-Null
Copy-Item (Join-Path $Tablet "markiz_blue_pc.png") (Join-Path $pics "markiz_blue_pc.png") -Force
Add-Type -Namespace MarkizInstall -Name Native -MemberDefinition '[DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern int SystemParametersInfo(int a, int b, string c, int d);'
[MarkizInstall.Native]::SystemParametersInfo(20, 0, (Join-Path $pics "markiz_blue_pc.png"), 3) | Out-Null
Ok "Обои стоят (если у тебя Wallpaper Engine — он может их перекрывать)"

# ---------- 7. Готово ----------
Step 7 "Готово!"
Write-Host ""
Write-Host "  Сверни все окна (Win + D) — там новый главный экран." -ForegroundColor White
Write-Host "  Поменять город и другое: настройки.txt, потом снова УСТАНОВИТЬ.bat"
Write-Host "  Убрать всё: УДАЛИТЬ.bat"
