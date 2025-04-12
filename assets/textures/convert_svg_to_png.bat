

@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

REM === Проверка наличия inkscape в PATH
where inkscape >nul 2>&1
if errorlevel 1 (
    echo ❌ Inkscape не найден в PATH. Укажи путь вручную или добавь inkscape в переменные среды.
    pause
    exit /b
)

REM === Папка, где лежат SVG (та же, где .bat файл)
set SOURCE_DIR=%~dp0
cd /d %SOURCE_DIR%

REM === Конвертация всех SVG в PNG
for %%f in (*.svg) do (
    echo 🔄 Конвертируем: %%f
      "C:\Program Files\Inkscape\bin\inkscape.exe" "%%f" --export-type=png --export-filename="%%~nf.png"
)

echo ✅ Все SVG успешно конвертированы в PNG!
pause