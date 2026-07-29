@echo off
chcp 65001 > nul
setlocal
cd /d "%~dp0"

where py >nul 2>nul
if errorlevel 1 (
    echo Python 3.11 or newer is required.
    pause
    exit /b 1
)

if not exist "vendor\wheels" mkdir "vendor\wheels"

echo Downloading Windows dependency wheels for this Python version...
py -3 -m pip download --only-binary=:all: --dest "vendor\wheels" -r requirements-build.txt
if errorlevel 1 (
    echo Dependency caching failed.
    pause
    exit /b 1
)

echo.
echo Offline dependencies are ready in vendor\wheels.
echo Keep this folder when moving the source project to another offline machine.
pause
exit /b 0
