#!/bin/bash
# Satellite Imagery Export Tool - Linux/macOS Launcher

echo "============================================================"
echo "Satellite Imagery Export Tool v2.0"
echo "Standalone Edition - No QGIS Required"
echo "============================================================"
echo ""

# Launch the application using Python
python3 main.py

# Check if there was an error
if [ $? -ne 0 ]; then
    echo ""
    echo "============================================================"
    echo "ERROR: Application exited with error code $?"
    echo "============================================================"
    echo ""
    echo "Possible issues:"
    echo "  - Python 3 not installed"
    echo "  - Missing dependencies (run: pip3 install -r requirements.txt)"
    echo "  - GDAL not properly installed"
    echo ""
    echo "For installation help, see README.md"
    echo "============================================================"
    read -p "Press Enter to continue..."
fi
