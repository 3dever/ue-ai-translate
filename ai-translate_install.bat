@echo off
setlocal ENABLEDELAYEDEXPANSION
title AI Translator Setup

set SCRIPT_NAME=translate_gui.py
set PYTHON_VER=3.12.3
set PYTHON_URL=https://www.python.org/ftp/python/%PYTHON_VER%/python-%PYTHON_VER%-amd64.exe
set PYTHON_INSTALLER=python-installer.exe
set ERROR_OCCURRED=0

echo ============================================
echo        AI Translator Setup Utility
echo ============================================
echo.

rem === STEP 1: CHECK PYTHON ===================
echo [1/4] Checking for Python...

where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Python not found.
    echo Downloading Python %PYTHON_VER%...

    curl -# -o %PYTHON_INSTALLER% %PYTHON_URL%

    if not exist %PYTHON_INSTALLER% (
        echo Failed to download Python installer.
        set ERROR_OCCURRED=1
        goto END
    )

    echo Installing Python silently...
    %PYTHON_INSTALLER% /quiet InstallAllUsers=1 PrependPath=1 Include_test=0

    if %ERRORLEVEL% NEQ 0 (
        echo Python installation failed.
        set ERROR_OCCURRED=1
        goto END
    )

    del %PYTHON_INSTALLER%
    echo Python installed and added to PATH.
) else (
    echo Python is already installed.
)

rem === STEP 2: UPGRADE PIP ====================
echo.
echo [2/4] Upgrading pip...
python -m pip install --upgrade pip >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Failed to upgrade pip (continuing anyway).
) else (
    echo pip upgraded.
)

rem === STEP 3: INSTALL DEPENDENCIES ==========
echo.
echo [3/4] Installing required Python packages...

set PACKAGES=openai polib python-dotenv
for %%P in (%PACKAGES%) do (
    echo Installing %%P...
    python -m pip install %%P >nul 2>&1
    if !ERRORLEVEL! NEQ 0 (
        echo   Failed to install %%P
        set ERROR_OCCURRED=1
        goto END
    ) else (
        echo   Installed %%P
    )
)

rem === STEP 4: LAUNCH SCRIPT ==================
echo.
echo [4/4] Launching translation tool...
python %SCRIPT_NAME%
if %ERRORLEVEL% NEQ 0 (
    echo Error while running %SCRIPT_NAME%.
    set ERROR_OCCURRED=1
    goto END
)

:END
echo.
echo --------------------------------------------
if "%ERROR_OCCURRED%"=="1" (
    echo Setup finished with errors.
    echo Please check the log above for details.
) else (
    echo Setup completed successfully.
    echo Everything is ready to use.
)
echo.
echo Press any key to exit.
pause >nul
