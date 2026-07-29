@echo off
chcp 65001 > nul
setlocal
cd /d "%~dp0"

if exist "vendor\ffmpeg\ffmpeg.exe" (
    set "PATH=%CD%\vendor\ffmpeg;%PATH%"
)

if not exist ".venv\Scripts\python.exe" (
    echo ShotLab development environment is not ready.
    echo Run setup_windows.bat once, then use this launcher without reinstalling dependencies.
    pause
    exit /b 1
)

".venv\Scripts\python.exe" -c "import PySide6, PIL" >nul 2>nul
if errorlevel 1 (
    echo ShotLab dependencies are incomplete.
    echo Run setup_windows.bat once to repair the development environment.
    pause
    exit /b 1
)

where ffmpeg >nul 2>nul
if errorlevel 1 (
    echo FFmpeg is not available in PATH.
    echo Copy ffmpeg.exe and ffprobe.exe into vendor\ffmpeg or add FFmpeg to PATH.
    pause
    exit /b 1
)

".venv\Scripts\python.exe" main.py
set "APP_EXIT=%ERRORLEVEL%"
if not "%APP_EXIT%"=="0" pause
exit /b %APP_EXIT%
