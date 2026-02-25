@echo off
title RevitComfyUI Installer

where py >nul 2>&1
if %ERRORLEVEL%==0 ( py "%~dp0install.py" & goto done )

where python >nul 2>&1
if %ERRORLEVEL%==0 ( python "%~dp0install.py" & goto done )

echo.
echo  Python not found!
echo  Download from https://www.python.org/downloads/
echo  During install tick "Add Python to PATH"
echo.
pause
:done
