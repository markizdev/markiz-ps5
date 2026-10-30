# Убирает оформление MARKIZ PS5: выключает скины в Rainmeter и возвращает прежние обои.
# Программы (Python, Chrome, Rainmeter) не удаляет — они могут быть нужны и для другого.
$Backup = Join-Path $PSScriptRoot "backup.json"
$rmExe = "$env:ProgramFiles\Rainmeter\Rainmeter.exe"

Write-Host "MARKIZ PS5 — удаление оформления" -ForegroundColor Cyan

if (Test-Path $rmExe) {
    foreach ($c in "MarkizPS\Hero", "MarkizPS\Home", "MarkizPS\Dock", "MarkizPS\Splash", "MarkizPS\Clock") { & $rmExe !DeactivateConfig $c }
    Write-Host "  + Скины в Rainmeter выключены" -ForegroundColor Green
}

$old = $null
if (Test-Path $Backup) { $old = (Get-Content $Backup -Raw | ConvertFrom-Json).wallpaper }
Add-Type -Namespace MarkizUninstall -Name Native -MemberDefinition '[DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern int SystemParametersInfo(int a, int b, string c, int d);'
if ($old -and (Test-Path $old)) {
    [MarkizUninstall.Native]::SystemParametersInfo(20, 0, $old, 3) | Out-Null
    Write-Host "  + Прежние обои возвращены" -ForegroundColor Green
} else {
    Write-Host "  ! Прежние обои не нашлись — выбери их в Параметры -> Персонализация -> Фон" -ForegroundColor Yellow
}

$ans = Read-Host "Удалить и файлы скина из папки Rainmeter? (Д/Н)"
if ($ans -match "^[ДдYy]") {
    $skins = Join-Path ([Environment]::GetFolderPath("MyDocuments")) "Rainmeter\Skins\MarkizPS"
    if (Test-Path $skins) { Remove-Item $skins -Recurse -Force; Write-Host "  + Файлы скина удалены" -ForegroundColor Green }
}
Write-Host "Готово."
