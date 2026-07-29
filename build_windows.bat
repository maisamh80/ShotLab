@echo off
chcp 65001 > nul
setlocal
cd /d "%~dp0"

where py >nul 2>nul
if errorlevel 1 (
    echo Python 3.11 or newer is required to build ShotLab.
    exit /b 1
)

if not exist "vendor\ffmpeg\ffmpeg.exe" (
    echo Missing vendor\ffmpeg\ffmpeg.exe
    exit /b 1
)
if not exist "vendor\ffmpeg\ffprobe.exe" (
    echo Missing vendor\ffmpeg\ffprobe.exe
    exit /b 1
)

if not exist ".buildenv\Scripts\python.exe" (
    py -3 -m venv .buildenv
    if errorlevel 1 exit /b 1
)

".buildenv\Scripts\python.exe" -c "import PyInstaller, PySide6, PIL" >nul 2>nul
if errorlevel 1 (
    if exist "vendor\wheels\*.whl" (
        echo Installing build dependencies from the offline wheel cache...
        ".buildenv\Scripts\python.exe" -m pip install --no-index --find-links "vendor\wheels" -r requirements-build.txt
    ) else (
        echo Installing build dependencies from the internet once...
        ".buildenv\Scripts\python.exe" -m pip install -r requirements-build.txt
    )
    if errorlevel 1 exit /b 1
)

".buildenv\Scripts\python.exe" -m unittest discover -s quality_assurance -v
if errorlevel 1 exit /b 1

".buildenv\Scripts\pyinstaller.exe" --noconfirm --clean ShotLab.spec
if errorlevel 1 exit /b 1

echo.
echo Standalone application created:
echo dist\ShotLab\ShotLab.exe
