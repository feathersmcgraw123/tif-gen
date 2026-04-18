"""
Satellite Imagery Export Tool - Main Entry Point

This application exports high-resolution georeferenced GeoTIFF files
by downloading tiles directly from online tile servers (Google, ESRI, Bing, etc.).

No QGIS installation required!

Usage:
    python main.py

Requirements:
    - Python 3.7+
    - PyQt5
    - GDAL
    - NumPy
    - Pillow
    - requests
"""

import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

from ui.main_window import MainWindow


def main():
    """Main application entry point."""
    print("=" * 60)
    print("Satellite Imagery Export Tool v2.0")
    print("Standalone Edition - No QGIS Required")
    print("=" * 60)
    print()

    # Create Qt application
    app = QApplication(sys.argv)
    app.setApplicationName("Satellite Imagery Export Tool")
    app.setApplicationVersion("2.0")

    # Set application style (improves cross-platform appearance)
    app.setStyle('Fusion')

    # Create and show main window
    window = MainWindow()
    window.show()

    print("Application started successfully!")
    print("=" * 60)

    # Run application event loop
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
