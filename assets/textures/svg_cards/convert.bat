@echo off
mkdir "assets\textures"
for %%f in (svg_cards\*.svg) do (
    inkscape "%%f" --export-type=png --export-filename="assets\textures\%%~nf.png" -w 80 -h 120
)
pause