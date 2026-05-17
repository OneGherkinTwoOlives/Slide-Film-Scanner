@echo off
REM Create Desktop Shortcut for PiSlide Scanner GUI
REM Run this once to create a shortcut on your desktop

echo Creating desktop shortcut for PiSlide Scanner...

set SCRIPT_DIR=%~dp0
set SHORTCUT_NAME=PiSlide Scanner.lnk
set TARGET=%SCRIPT_DIR%launch_pislide_gui.bat

REM Create VBS script to make shortcut
echo Set oWS = WScript.CreateObject("WScript.Shell") > CreateShortcut.vbs
echo sLinkFile = oWS.SpecialFolders("Desktop") ^& "\%SHORTCUT_NAME%" >> CreateShortcut.vbs
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> CreateShortcut.vbs
echo oLink.TargetPath = "%TARGET%" >> CreateShortcut.vbs
echo oLink.WorkingDirectory = "%SCRIPT_DIR%" >> CreateShortcut.vbs
echo oLink.Description = "PiSlide Film Scanner GUI" >> CreateShortcut.vbs
echo oLink.Save >> CreateShortcut.vbs

REM Execute VBS script
cscript //nologo CreateShortcut.vbs

REM Clean up
del CreateShortcut.vbs

echo.
echo Desktop shortcut created successfully!
echo You can now double-click "PiSlide Scanner" on your desktop to launch the GUI.
echo.
pause
