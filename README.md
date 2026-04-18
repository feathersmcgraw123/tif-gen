# Satellite Imagery Export Tool

A **fully self-contained** desktop application for downloading and exporting high-resolution georeferenced GeoTIFF files from online satellite imagery tile servers.

**✨ No QGIS required! No complex dependencies! Just Python + pip!**

Works on: **Windows** | **Linux** | **macOS** | **NixOS**

## Features

- **🗺️ Interactive Map** - Click on a map to define your export polygon!
- **🌍 Multi-Language Support** - English and Ukrainian (Українська)
- **Direct Tile Downloading** from Google, ESRI, Bing, OSM, and more
- **Multiple Polygon Input Methods**:
  - 🗺️ Draw on interactive map (click to add points)
  - ✏️ Manual coordinate entry
  - 📁 Import from GeoJSON or CSV files
- **Intelligent Export** with automatic zoom level calculation
- **Memory-Efficient Streaming** - exports any size area without loading entire image into RAM
- **Robust Processing** with pause/resume/cancel support
- **Automatic White Pixel Removal** - cleans up missing data markers from tile sources
- **Real-time Progress** tracking with accurate ETA
- **One-Command Installation** - works out of the box!

## Installation

### Universal Installation (All Platforms)

```bash
# 1. Clone the repository
git clone <repository-url>
cd satellite-imagery-export

# 2. Install dependencies (one command!)
pip install -r requirements.txt

# 3. Run the application
python main.py
```

**That's it!** No OSGeo4W, no Conda, no compilers needed.

### Platform-Specific Notes

<details>
<summary><b>Windows</b></summary>

```batch
# Install Python 3.7+ from python.org if not already installed
pip install -r requirements.txt
python main.py
```

Or double-click `run.bat`

</details>

<details>
<summary><b>Linux / Ubuntu / Debian</b></summary>

```bash
pip3 install -r requirements.txt
python3 main.py
```

Or run `./run.sh`

</details>

<details>
<summary><b>NixOS</b></summary>

Using nix-shell (recommended):

```bash
# Create shell.nix:
nix-shell -p python3 python3Packages.pip python3Packages.pyqt5

# Inside nix-shell:
pip install rasterio Pillow requests numpy
python main.py
```

Or add to your environment:

```nix
environment.systemPackages = with pkgs; [
  python3
  python3Packages.pyqt5
  python3Packages.rasterio
  python3Packages.pillow
  python3Packages.requests
  python3Packages.numpy
];
```

</details>

<details>
<summary><b>macOS</b></summary>

```bash
pip3 install -r requirements.txt
python3 main.py
```

If you encounter issues, use Homebrew:
```bash
brew install python3
pip3 install -r requirements.txt
```

</details>

## Quick Start

1. **Launch the application:**
   ```bash
   python main.py
   ```

2. **Choose your language:**
   - Click **Language** menu → Select **English** or **Українська**
   - The interface will update immediately

3. **Define your export polygon:**
   - Click "Define Polygon..."
   - **Option A: Draw on Map** (Easiest!)
     - Click on the map to add vertices
     - Points appear in order with numbers
     - Use "Undo" to remove last point
     - Click "Validate" then "OK"
   - **Option B: Manual Entry**
     - Type coordinates into the table
     - Click "Validate" then "OK"
   - **Option C: Import File**
     - Load from GeoJSON or CSV file

4. **Configure export settings:**
   - **Quality**: Choose from preset quality levels:
     - **Low** (Zoom 17): ~2.4 m/px - Faster, smaller files
     - **Medium** (Zoom 18): ~1.2 m/px - Balanced quality (recommended)
     - **High** (Zoom 19): ~0.6 m/px - Best quality
   - **Advanced mode** (optional): Check to specify exact zoom level or resolution
   - **Tile Source**: Google Satellite (recommended)
   - **Compression**: JPEG (quality 90) or LZW
   - **Output Path**: Where to save your GeoTIFF

5. **Export:**
   - Click "Start Export"
   - Monitor progress and ETA
   - Use Pause/Resume or Cancel as needed

## Example: Export Specific Area

### Method 1: Using Interactive Map (Recommended!)

1. Click "Define Polygon..."
2. Stay on "🗺️ Draw on Map" tab
3. Click on the map to add vertices for your area of interest
4. Watch as numbered markers appear with a polygon shape
5. Use "Undo Last Point" if you make a mistake
6. Click "Validate" then "OK"
7. Select **Medium** quality (default, recommended)
8. Select "Google Satellite" as tile source
9. Choose output path
10. Click "Start Export"

### Method 2: Using Coordinates

If you have specific coordinates:

```python
# Example coordinates (lat, lon format)
51.60841990, 34.57161562
51.63756171, 34.98175112
51.57096939, 35.35451545
51.50698722, 35.28882733
51.02777302, 34.54148379
51.06124086, 34.44687963
51.42283294, 34.58766415
```

1. Click "Define Polygon..." → "✏️ Manual Entry" tab
2. Add the coordinates above (or paste from CSV)
3. Click "Validate" then "OK"
4. Configure export settings
5. Click "Start Export"

The app will:
- Calculate zoom level (typically 18-19 for 0.6 m/px)
- Download tiles from Google
- Stitch them together
- Clip to your polygon
- Save as georeferenced GeoTIFF

## Available Tile Sources

| Source | Max Zoom | Best For |
|--------|----------|----------|
| Google Satellite | 20 | High-resolution worldwide (Recommended) |
| Google Hybrid | 20 | Satellite with labels |
| ESRI World Imagery | 19 | Alternative high-quality imagery |
| Bing Satellite | 19 | Microsoft's satellite imagery |
| OpenStreetMap | 19 | Map view (not satellite) |
| CartoDB Light/Dark | 19 | Clean base maps |

## File Formats

### Input

- **GeoJSON**: Standard GeoJSON polygon format
- **CSV**: Simple `lat,lon` format

### Output

- **GeoTIFF** with embedded georeferencing
- Compression: LZW (lossless) or JPEG (lossy)
- CRS: EPSG:4326 (WGS84) or EPSG:3857 (Web Mercator)
- BigTIFF support for files > 4GB

## Resolution Guide

The application now uses simple **Quality Presets** for easy selection:

| Preset | Zoom Level | Resolution | File Size | Use Case |
|--------|------------|------------|-----------|----------|
| **High** | 19 | ~0.6 m/px | Large | Best quality |
| **Medium** | 18 | ~1.2 m/px | Medium | Balanced quality/speed (recommended) |
| **Low** | 17 | ~2.4 m/px | Small | Quick exports |

**Advanced Mode** allows you to specify:
- Custom zoom level (0-20) for precise control
- Exact resolution in meters per pixel
- Useful for specific technical requirements

**Note:** Actual resolution varies with latitude due to Web Mercator projection. Values shown are approximate at mid-latitudes.

## Troubleshooting

### Installation Issues

**Problem:** `pip install` fails

**Solution:**
```bash
# Try upgrading pip first
pip install --upgrade pip

# Then install requirements
pip install -r requirements.txt

# If still fails, install packages individually:
pip install PyQt5
pip install rasterio
pip install Pillow requests numpy
```

**Problem:** Missing Qt platform plugin

**Solution:**
```bash
pip install PyQt5 --force-reinstall
```

### Runtime Issues

**Problem:** Tile download failures or white spots

**Solutions:**
- Check internet connection
- Increase render delay (Settings → Render Delay: 0.5s)
- Try different tile source (ESRI instead of Google)
- **Note**: The application automatically removes white pixels (missing data markers) during export
- If still seeing white speckles after export:
  - Try using LZW compression instead of JPEG
  - If using JPEG, increase quality to 95+
  - Reduce tile size to 1024 px (less memory pressure)
  - Try a different zoom level or tile source

**Problem:** Out of memory

**Note:** The application now uses memory-efficient streaming export that writes tiles directly to the GeoTIFF file. This allows exporting very large areas without requiring massive amounts of RAM.

**If you still experience memory issues:**
- Close other applications to free up RAM
- Use **Low** or **Medium** quality instead of **High**
- Export smaller area and combine results later
- Use JPEG compression instead of LZW (lower memory overhead)

## Performance Tips

**For Large Areas:**
- Use **Low** or **Medium** quality preset
- Use JPEG compression (quality 85-90)
- Increase render delay to 0.3-0.5 seconds
- Consider splitting into multiple smaller exports

**For Maximum Quality:**
- Use **High** quality preset (zoom 19, or zoom 19-20 in Advanced mode)
- Use LZW compression
- Source: Google Satellite or ESRI

**For Standard Use:**
- Use **Medium** quality preset (default)
- Good balance of quality and file size
- JPEG compression (quality 90) or LZW

**For Testing:**
- Small polygon first (~5km × 5km)
- Use **Low** quality preset
- JPEG compression

## Legal Notice

**Important:** This tool downloads imagery from third-party tile servers.

You are responsible for:
- ✅ Complying with tile provider Terms of Service
- ✅ Respecting rate limits and fair use policies
- ✅ Obtaining licenses for commercial use
- ✅ Proper attribution

Terms of Service:
- **Google Maps**: https://www.google.com/intl/en_us/help/terms_maps/
- **ESRI**: https://www.esri.com/en-us/legal/terms/full-master-agreement
- **Bing Maps**: https://www.microsoft.com/en-us/maps/product/terms
- **OpenStreetMap**: https://www.openstreetmap.org/copyright

## Technical Details

**Dependencies:**
- Python 3.7+
- PyQt5 (GUI framework)
- PyQtWebEngine (Interactive map display)
- rasterio (GeoTIFF creation - has pre-built wheels!)
- Pillow (Image processing)
- numpy (Numerical operations)
- requests (HTTP tile downloading)

**Why This Tool is Self-Contained:**
- Uses `rasterio` instead of raw GDAL (has pre-built wheels for all platforms)
- No compiler needed
- No system libraries required
- Works with standard `pip install`

**Memory-Efficient Design:**
- Uses streaming tile-by-tile writing instead of building entire image in RAM
- Can export areas of any size without memory limitations
- Writes tiles directly to GeoTIFF using rasterio's windowed writes
- Automatically removes white pixels during tile processing

## Contributing

Contributions welcome! Please submit issues or pull requests.

## License

This project is provided as-is for educational and research purposes.

## Version History

- **v2.0.0** (2024) - Self-Contained Edition
  - ✨ Removed QGIS dependency
  - ✨ Replaced GDAL with rasterio (easy pip install!)
  - ✨ Direct tile downloading from multiple sources
  - ✨ Works on Windows, Linux, macOS, and NixOS
  - ✨ One-command installation
  - ✨ No complex dependencies

- **v1.0.0** (2024) - QGIS-dependent version

## Acknowledgments

- Tile imagery © respective providers
- Built with Python, PyQt5, and rasterio
- Thanks to the open-source GIS community

---

**Questions? Issues? Feature Requests?**
Open an issue on the project repository!
