@echo off
setlocal
set SCRIPT_NAME=ai-translate_gui.py
set INSTALL_SCRIPT=ai-translate_install.bat

echo Checking for Python...

where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Python is not installed.
    echo Launching installer: %INSTALL_SCRIPT%
    call %INSTALL_SCRIPT%
    goto END
)

echo Python found. Launching GUI...
python %SCRIPT_NAME%

:END
echo.
pause
endlocal
