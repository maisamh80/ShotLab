@echo off
chcp 65001 > nul
setlocal
cd /d "%~dp0"

where py >nul 2>nul
if errorlevel 1 (
    echo Python 3.11 or newer is required for the development environment.
    pause
    exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
    echo Creating the ShotLab development environment...
    py -3 -m venv .venv
    if errorlevel 1 goto :error
)

".venv\Scripts\python.exe" -c "import PySide6, PIL" >nul 2>nul
if not errorlevel 1 goto :ready

if exist "vendor\wheels\*.whl" (
    echo Installing dependencies from the offline wheel cache...
    ".venv\Scripts\python.exe" -m pip install --no-index --find-links "vendor\wheels" -r requirements.txt
) else (
    echo Installing dependencies from the internet once...
    ".venv\Scripts\python.exe" -m pip install -r requirements.txt
)
if errorlevel 1 goto :error

:ready
echo.
echo ShotLab is ready. Future runs do not install dependencies.
echo Use run_windows.bat for development or publish_windows.bat for release builds.
pause
exit /b 0

:error
echo.
echo ShotLab setup failed.
pause
exit /b 1
