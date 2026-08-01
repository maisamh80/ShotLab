@echo off
chcp 65001 > nul
setlocal
cd /d "%~dp0"

call build_windows.bat
if errorlevel 1 goto :error

for /f "tokens=2 delims== " %%V in ('findstr /b "__version__" "shotlab\__init__.py"') do set "SHOTLAB_VERSION=%%~V"
if not defined SHOTLAB_VERSION goto :error
set "SHOTLAB_EXTENSION_VERSION=0.1.3"

if not exist "release" mkdir "release"

echo Creating portable release archive...
powershell -NoProfile -ExecutionPolicy Bypass -Command "Compress-Archive -Path 'dist\ShotLab\*' -DestinationPath 'release\ShotLab_Portable_v%SHOTLAB_VERSION%.zip' -Force"
if errorlevel 1 goto :error

echo Creating Chrome extension archive...
powershell -NoProfile -ExecutionPolicy Bypass -Command "Compress-Archive -Path 'browser_extension\*' -DestinationPath 'release\ShotLab_Chrome_Extension_v%SHOTLAB_EXTENSION_VERSION%.zip' -Force"
if errorlevel 1 goto :error

set "ISCC_PATH="
if exist "%ProgramFiles%\Inno Setup 7\ISCC.exe" set "ISCC_PATH=%ProgramFiles%\Inno Setup 7\ISCC.exe"
if not defined ISCC_PATH if exist "%ProgramFiles(x86)%\Inno Setup 7\ISCC.exe" set "ISCC_PATH=%ProgramFiles(x86)%\Inno Setup 7\ISCC.exe"
if not defined ISCC_PATH if exist "%LOCALAPPDATA%\Programs\Inno Setup 7\ISCC.exe" set "ISCC_PATH=%LOCALAPPDATA%\Programs\Inno Setup 7\ISCC.exe"
if not defined ISCC_PATH if exist "%ProgramFiles%\Inno Setup 6\ISCC.exe" set "ISCC_PATH=%ProgramFiles%\Inno Setup 6\ISCC.exe"
if not defined ISCC_PATH if exist "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" set "ISCC_PATH=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
if not defined ISCC_PATH if exist "%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe" set "ISCC_PATH=%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe"

if not defined ISCC_PATH (
    echo.
    echo Portable and Chrome extension releases created:
    echo release\ShotLab_Portable_v%SHOTLAB_VERSION%.zip
    echo release\ShotLab_Chrome_Extension_v%SHOTLAB_EXTENSION_VERSION%.zip
    echo.
    echo Inno Setup 7 or 6 was not found, so the installer EXE was skipped.
    echo Install Inno Setup 7 x64 and run publish_windows.bat again to create it.
    pause
    exit /b 0
)

echo Creating ShotLab installer...
"%ISCC_PATH%" /DMyAppVersion=%SHOTLAB_VERSION% "installer\ShotLab.iss"
if errorlevel 1 goto :error

echo.
echo Publishing files are ready in the release folder.
pause
exit /b 0

:error
echo.
echo ShotLab publishing failed.
pause
exit /b 1
