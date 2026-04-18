#!/bin/bash

echo "============================================================"
echo " Satellite Imagery Export Tool"
echo "============================================================"
echo ""

# Find Python 3.7+
PYTHON=""
for cmd in python3 python; do
    if command -v "$cmd" &>/dev/null; then
        if "$cmd" -c "import sys; exit(0 if sys.version_info >= (3,7) else 1)" 2>/dev/null; then
            PYTHON="$cmd"
            break
        fi
    fi
done

if [ -z "$PYTHON" ]; then
    echo "ERROR: Python 3.7+ not found."
    echo ""
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "Install via Homebrew:  brew install python3"
        echo "Or download from:      https://www.python.org/downloads/"
    else
        echo "Install with:  sudo apt install python3 python3-pip python3-venv"
        echo "Or download:   https://www.python.org/downloads/"
    fi
    exit 1
fi

# Create virtual environment if needed
if [ ! -d ".venv" ]; then
    echo "Setting up virtual environment..."
    $PYTHON -m venv .venv
fi

# Activate
source .venv/bin/activate

# Install / update dependencies
echo "Checking dependencies..."
pip install -r requirements.txt -q --upgrade

echo "Starting..."
echo ""
python main.py
