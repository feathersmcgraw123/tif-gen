@echo off
setlocal

echo ============================================================
echo  Satellite Imagery Export Tool
echo ============================================================
echo.

REM Check Python is installed
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found.
    echo.
    echo Please install Python 3.7+ from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

REM Check Python version >= 3.7
python -c "import sys; exit(0 if sys.version_info >= (3,7) else 1)" >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python 3.7 or higher is required.
    python --version
    echo.
    pause
    exit /b 1
)

REM Create virtual environment if it doesn't exist
if not exist ".venv" (
    echo Setting up virtual environment...
    python -m venv .venv
    if %errorlevel% neq 0 (
        echo ERROR: Failed to create virtual environment.
        pause
        exit /b 1
    )
)

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Install / update dependencies
echo Checking dependencies...
pip install -r requirements.txt -q --upgrade
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies.
    echo Try running: pip install -r requirements.txt
    pause
    exit /b 1
)

echo Starting...
echo.
python main.py

if %errorlevel% neq 0 (
    echo.
    echo Application exited with an error. See output above.
    pause
)
