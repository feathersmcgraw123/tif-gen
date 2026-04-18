@echo off
REM Satellite Imagery Export Tool - Windows Launcher

echo ============================================================
echo Satellite Imagery Export Tool v2.0
echo Standalone Edition - No QGIS Required
echo ============================================================
echo.

REM Launch the application using Python
python main.py

REM Check if there was an error
if errorlevel 1 (
    echo.
    echo ============================================================
    echo ERROR: Application exited with error code %errorlevel%
    echo ============================================================
    echo.
    echo Possible issues:
    echo   - Python not installed or not in PATH
    echo   - Missing dependencies (run: pip install -r requirements.txt)
    echo   - GDAL not properly installed
    echo.
    echo For installation help, see README.md
    echo ============================================================
    pause
)
