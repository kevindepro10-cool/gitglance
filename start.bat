@echo off
setlocal enabledelayedexpansion
title gitglance

cd /d "%~dp0"

echo.
echo   gitglance - repo analytics for the terminal
echo   ===========================================
echo.

where python >nul 2>nul
if errorlevel 1 (
    echo   [!] Python not found on PATH.
    echo       Install Python 3.9 or newer from https://www.python.org/downloads/
    echo       and make sure "Add Python to PATH" is checked.
    echo.
    pause
    exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
    echo   [*] Creating virtual environment .venv ...
    python -m venv .venv
    if errorlevel 1 (
        echo   [!] Could not create the virtual environment.
        pause
        exit /b 1
    )
)

call ".venv\Scripts\activate.bat"

python -m pip install --quiet --disable-pip-version-check --upgrade pip >nul 2>nul
python -c "import gitglance" >nul 2>nul
if errorlevel 1 (
    echo   [*] Installing gitglance ...
    python -m pip install --quiet --disable-pip-version-check .
    if errorlevel 1 (
        echo   [!] Installation failed. Check the messages above.
        pause
        exit /b 1
    )
)

echo.

if "%~1"=="" (
    python -m gitglance summary --no-color
) else (
    python -m gitglance %*
)

echo.
echo   ===========================================
pause
endlocal
