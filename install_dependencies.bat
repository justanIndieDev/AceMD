@echo off
setlocal
title ACEMD Dependency Installer

echo ========================================
echo   ACEMD - AceMacroDeck Setup
echo ========================================
echo.

where py >nul 2>nul
if errorlevel 1 (
    echo ERROR: Python Launcher was not found.
    echo Install Python 3.13 from https://www.python.org/downloads/
    pause
    exit /b 1
)

py -3.13 --version >nul 2>nul
if errorlevel 1 (
    echo ERROR: Python 3.13 was not found.
    echo Install Python 3.13 from https://www.python.org/downloads/
    pause
    exit /b 1
)

echo Installing or updating ACEMD dependencies...
py -3.13 -m pip install --upgrade pip
if errorlevel 1 (
    echo WARNING: pip could not be upgraded. Continuing with package installation...
)

py -3.13 -m pip install pygame pyautogui pynput pystray pillow
if errorlevel 1 (
    echo.
    echo ERROR: Dependency installation failed.
    echo Check your internet connection and Python installation, then try again.
    pause
    exit /b 1
)

echo.
echo Dependencies installed successfully.
echo You can now run start_acemd.bat.
pause
endlocal
