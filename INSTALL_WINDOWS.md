# Windows Installation Guide

## Method 1: OSGeo4W (Recommended)

### Step 1: Install OSGeo4W

1. **Download OSGeo4W installer:**
   - Go to: https://trac.osgeo.org/osgeo4w/
   - Click "OSGeo4W Network Installer (64 bit)"
   - Save `osgeo4w-setup.exe`

2. **Run the installer:**
   - Double-click `osgeo4w-setup.exe`
   - Select **"Express Install"**
   - Check these packages:
     - ✅ GDAL
     - ✅ Python
     - ✅ QGIS Desktop (optional, but useful)
   - Click "Next" and wait for installation

3. **OSGeo4W is now installed at:** `C:\OSGeo4W64\`

### Step 2: Install Python Dependencies

1. **Open OSGeo4W Shell:**
   - Start Menu → OSGeo4W → "OSGeo4W Shell"
   - This gives you a command prompt with GDAL already configured

2. **Install Python packages:**
   ```batch
   python3 -m pip install PyQt5 Pillow requests numpy
   ```

### Step 3: Run the Application

1. **In the OSGeo4W Shell:**
   ```batch
   cd C:\Users\%USERNAME%\Documents\Projects\tif
   python3 main.py
   ```

2. **Or create a shortcut:**
   - Right-click on Desktop → New → Shortcut
   - Target: `C:\OSGeo4W64\OSGeo4W.bat python3 C:\Users\%USERNAME%\Documents\Projects\tif\main.py`
   - Name it "Satellite Export Tool"

### Troubleshooting

**If you get "python3: command not found":**
- Try `python` instead of `python3`
- Or use: `C:\OSGeo4W64\bin\python.exe main.py`

**If GDAL imports fail:**
```batch
# In OSGeo4W Shell, test GDAL:
python3 -c "from osgeo import gdal; print(gdal.__version__)"
```

---

## Method 2: Conda (Alternative)

### Step 1: Install Miniconda

1. **Download Miniconda:**
   - Go to: https://docs.conda.io/en/latest/miniconda.html
   - Download "Miniconda3 Windows 64-bit"
   - Run the installer

2. **Accept defaults and complete installation**

### Step 2: Create Environment

1. **Open Anaconda Prompt (Miniconda3)**
   - Start Menu → Anaconda Prompt (Miniconda3)

2. **Create environment with all dependencies:**
   ```batch
   conda create -n geoexport python=3.9 -y
   conda activate geoexport
   conda install -c conda-forge gdal pyqt pillow requests numpy -y
   ```

### Step 3: Run the Application

```batch
# Activate environment (if not already active)
conda activate geoexport

# Navigate to project
cd C:\Users\%USERNAME%\Documents\Projects\tif

# Run
python main.py
```

### Create a Batch File Launcher

Create `run_conda.bat`:
```batch
@echo off
call C:\Users\%USERNAME%\miniconda3\Scripts\activate.bat geoexport
cd C:\Users\%USERNAME%\Documents\Projects\tif
python main.py
pause
```

---

## Method 3: Pre-built Wheels

### Step 1: Download GDAL Wheel

1. **Go to:** https://www.lfd.uci.edu/~gohlke/pythonlibs/#gdal

2. **Find your Python version:**
   ```batch
   python --version
   # Example output: Python 3.9.7
   ```

3. **Download matching wheel:**
   - Python 3.9: `GDAL-3.8.4-cp39-cp39-win_amd64.whl`
   - Python 3.10: `GDAL-3.8.4-cp310-cp310-win_amd64.whl`
   - Python 3.11: `GDAL-3.8.4-cp311-cp311-win_amd64.whl`

### Step 2: Install

```batch
# Install GDAL wheel
pip install C:\Users\%USERNAME%\Downloads\GDAL-3.8.4-cp39-cp39-win_amd64.whl

# Install other dependencies
pip install PyQt5 Pillow requests numpy

# Run the app
cd C:\Users\%USERNAME%\Documents\Projects\tif
python main.py
```

---

## Verification

### Test GDAL Installation

```batch
python -c "from osgeo import gdal; print('GDAL version:', gdal.__version__)"
```

Expected output:
```
GDAL version: 3.x.x
```

### Test PyQt5 Installation

```batch
python -c "from PyQt5.QtWidgets import QApplication; print('PyQt5 OK')"
```

Expected output:
```
PyQt5 OK
```

### Test All Dependencies

```batch
python -c "from osgeo import gdal; from PyQt5.QtWidgets import QApplication; from PIL import Image; import requests; import numpy; print('All dependencies OK!')"
```

---

## Common Issues

### Issue: "ModuleNotFoundError: No module named 'osgeo'"

**Solution:** GDAL is not installed or not in PATH
- Use OSGeo4W Shell (Method 1)
- Or ensure conda environment is activated (Method 2)

### Issue: "ImportError: DLL load failed"

**Solution:** Missing GDAL DLLs
- Reinstall using OSGeo4W or Conda
- Don't mix installation methods

### Issue: "Qt platform plugin could not be initialized"

**Solution:**
```batch
pip install PyQt5 --force-reinstall
```

### Issue: Application window doesn't open

**Solution:** Check if running in headless environment
- Need a display/desktop environment
- For servers, use Xvfb (Linux) or remote desktop

---

## Need Help?

If you encounter issues:

1. **Check Python version:**
   ```batch
   python --version
   ```
   Should be 3.7 or higher

2. **Check if running correct Python:**
   ```batch
   where python
   ```

3. **Try the simplest method first:** OSGeo4W Express Install

4. **Report issues** with:
   - Python version
   - Installation method used
   - Full error message
   - Output of: `python -c "import sys; print(sys.path)"`
