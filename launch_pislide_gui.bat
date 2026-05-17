@echo off
REM PiSlide Scanner GUI Launcher for Windows
REM Double-click this file to launch the scanner GUI

echo Starting PiSlide Scanner GUI...
cd /d "%~dp0"

REM Try to use python3 first, fall back to python
python3 PiSlide_GUI.py 2>nul || python PiSlide_GUI.py

REM If there was an error, pause so user can see it
if errorlevel 1 (
    echo.
    echo An error occurred. Press any key to close this window.
    pause >nul
)
