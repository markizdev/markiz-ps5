# Возвращает оформление Windows, которое было до стиля PS5: старые обои (BMW) и прежний цвет акцента.
# Запуск: правой кнопкой по файлу -> "Выполнить с помощью PowerShell".
$b = $PSScriptRoot
reg import "$b\dwm.reg"
reg import "$b\accent.reg"
if (Test-Path "$b\accent_palette_before.reg") { reg import "$b\accent_palette_before.reg" }
reg import "$b\themes.reg"
Set-ItemProperty 'HKCU:\Control Panel\Desktop' WallpaperStyle '10'
Add-Type @'
using System; using System.Runtime.InteropServices;
public class W { [DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern int SystemParametersInfo(int a, int b, string c, int d);
[DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern IntPtr SendMessageTimeout(IntPtr h, uint m, UIntPtr w, string l, uint f, uint t, out UIntPtr r); }
'@
[W]::SystemParametersInfo(20, 0, "$b\old_wallpaper.jpg", 3) | Out-Null
$r = [UIntPtr]::Zero
[W]::SendMessageTimeout([IntPtr]0xffff, 0x1A, [UIntPtr]::Zero, "ImmersiveColorSet", 2, 3000, [ref]$r) | Out-Null

# Живые обои Wallpaper Engine: прежние "Lost Cat"
& "D:\SteamLibrary\steamapps\common\wallpaper_engine\wallpaper64.exe" -control openWallpaper -file "D:\SteamLibrary\steamapps\workshop\content\431960\3352465485\scene.pkg" -monitor 0

# Rainmeter: убрать виджеты MarkizPS, вернуть часы AnimeSky
$rm = "C:\Program Files\Rainmeter\Rainmeter.exe"
& $rm !DeactivateConfig "MarkizPS\Home"
& $rm !DeactivateConfig "MarkizPS\Clock"
& $rm !DeactivateConfig "MarkizPS\Hero"
& $rm !DeactivateConfig "MarkizPS\Dock"
& $rm !DeactivateConfig "MarkizPS\Splash"
& $rm !ActivateConfig "AnimeSky\Clock" "Clock.ini"

# Панель задач: прежние настройки TranslucentTB
Copy-Item "$b\translucenttb_settings.json" "$env:LOCALAPPDATA\Packages\28017CharlesMilette.TranslucentTB_v826wp6bftszj\RoamingState\settings.json" -Force

# Иконки папок на рабочем столе: прежние из FolderIcons
$d = [Environment]::GetFolderPath('Desktop')
foreach ($k in 'Документы', 'Игры', 'Картинки', 'Моды и утилиты для игр', 'Программы', 'Разное') {
    $ini = Join-Path (Join-Path $d $k) 'desktop.ini'
    (Get-Item $ini -Force).Attributes = 'Normal'
    $t = (Get-Content $ini -Raw) -replace 'FolderIconsPS\\', 'FolderIcons\'
    [IO.File]::WriteAllText($ini, $t, [Text.Encoding]::Unicode)
    (Get-Item $ini -Force).Attributes = 'Hidden,System'
}
ie4uinit.exe -show

# Сглаживание шрифтов (ClearType) и масштаб экрана 100 %
reg import "$b\cleartype.reg"
reg import "$b\desktop_fonts.reg"
& "$b\set_scale.ps1" 0

# Панель задач снова всегда видна (выключить автоскрытие)
Add-Type -TypeDefinition @'
using System; using System.Runtime.InteropServices;
public class ABR { [StructLayout(LayoutKind.Sequential)] public struct APPBARDATA { public int cbSize; public IntPtr hWnd; public uint uCallbackMessage, uEdge; public int l,t,r,b; public IntPtr lParam; }
 [DllImport("shell32.dll")] static extern uint SHAppBarMessage(uint m, ref APPBARDATA d);
 [DllImport("user32.dll", CharSet=CharSet.Unicode)] static extern IntPtr FindWindow(string c, string w);
 public static void Set(int st){ var d=new APPBARDATA(); d.cbSize=Marshal.SizeOf(d); d.hWnd=FindWindow("Shell_TrayWnd", null); d.lParam=(IntPtr)st; SHAppBarMessage(10, ref d); } }
'@
[ABR]::Set(0)

# Значки на рабочем столе снова видны
Set-ItemProperty 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced' HideIcons 0 -Type DWord

# Обычный курсор Windows
reg import "$b\cursors.reg"
Add-Type -Namespace RC -Name S -MemberDefinition '[DllImport("user32.dll")] public static extern bool SystemParametersInfo(uint a, uint b, IntPtr c, uint d);'
[RC.S]::SystemParametersInfo(0x57, 0, [IntPtr]::Zero, 0) | Out-Null

# Экран блокировки: прежние настройки Windows (картинку можно выбрать в Параметры -> Персонализация -> Экран блокировки)
reg import "$b\lockscreen_cdm.reg"

# Перезапуск Проводника, чтобы вернулись значки, и панели задач
Stop-Process -Name explorer -Force
Start-Sleep 3
if (-not (Get-Process explorer -ErrorAction SilentlyContinue)) { Start-Process explorer.exe }
Start-Sleep 6
Start-Process "shell:AppsFolder\28017CharlesMilette.TranslucentTB_v826wp6bftszj!TranslucentTB"

Write-Host "Готово: оформление возвращено."
