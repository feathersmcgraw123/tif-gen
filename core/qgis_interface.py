"""
QGIS connection and layer management.

This module provides functions to:
- Detect if QGIS is available
- Connect to running QGIS instance
- List and retrieve raster layers
- Initialize QGIS application
"""

import os
import sys
from typing import Optional, List, Dict, Tuple


def detect_qgis() -> Tuple[bool, Optional[str]]:
    """
    Check if QGIS Python modules are available.

    Returns:
        Tuple of (is_available, version_string)
        If QGIS is not available, version_string is None
    """
    try:
        from qgis.core import Qgis
        version = Qgis.versionInt() if hasattr(Qgis, 'versionInt') else Qgis.QGIS_VERSION
        return True, str(version)
    except ImportError as e:
        return False, None


def initialize_qgis(prefix_path: Optional[str] = None) -> Tuple[bool, str]:
    """
    Initialize QGIS application.

    This function should be called before using any QGIS functionality.
    It sets up the QGIS environment and initializes the application.

    Args:
        prefix_path: Optional QGIS installation prefix path.
                    If None, will attempt to auto-detect.

    Returns:
        Tuple of (success, message)
    """
    try:
        from qgis.core import QgsApplication

        # If prefix_path is provided, set it
        if prefix_path:
            QgsApplication.setPrefixPath(prefix_path, True)

        # Initialize QGIS application
        # Second argument (False) means this is a non-GUI application
        # However, we still need GUI for rendering, so we pass True
        qgs = QgsApplication([], True)
        qgs.initQgis()

        return True, "QGIS initialized successfully"

    except Exception as e:
        return False, f"Failed to initialize QGIS: {str(e)}"


def find_qgis_installation() -> Optional[str]:
    """
    Attempt to auto-detect QGIS installation path.

    Returns:
        QGIS prefix path if found, None otherwise
    """
    # Common QGIS installation paths
    if sys.platform == 'win32':
        common_paths = [
            r"C:\Program Files\QGIS 3.34",
            r"C:\Program Files\QGIS 3.32",
            r"C:\Program Files\QGIS 3.30",
            r"C:\OSGeo4W\apps\qgis",
            r"C:\OSGeo4W64\apps\qgis",
        ]
    elif sys.platform == 'darwin':  # macOS
        common_paths = [
            "/Applications/QGIS.app/Contents/MacOS",
            "/Applications/QGIS-LTR.app/Contents/MacOS",
        ]
    else:  # Linux
        common_paths = [
            "/usr",
            "/usr/local",
        ]

    for path in common_paths:
        if os.path.exists(path):
            return path

    # Try to get from environment variable
    if 'QGIS_PREFIX_PATH' in os.environ:
        return os.environ['QGIS_PREFIX_PATH']

    return None


def get_available_layers() -> List[Dict[str, str]]:
    """
    Get list of raster layers from current QGIS project.

    Filters for satellite imagery layers (containing 'google', 'satellite',
    'bing', 'esri', or 'xyz' in the name).

    Returns:
        List of dictionaries with keys: 'name', 'id', 'type', 'source'
    """
    try:
        from qgis.core import QgsProject

        layers = []
        project = QgsProject.instance()

        if not project:
            return []

        for layer_id, layer in project.mapLayers().items():
            # Check if it's a raster layer
            if not hasattr(layer, 'rasterType'):
                continue

            layer_name = layer.name().lower()

            # Filter for satellite/XYZ tile layers
            keywords = ['google', 'satellite', 'bing', 'esri', 'xyz', 'aerial']
            if any(keyword in layer_name for keyword in keywords):
                layers.append({
                    'name': layer.name(),
                    'id': layer_id,
                    'type': 'raster',
                    'source': layer.source() if hasattr(layer, 'source') else ''
                })

        return layers

    except Exception as e:
        print(f"Error getting layers: {e}")
        return []


def get_all_raster_layers() -> List[Dict[str, str]]:
    """
    Get all raster layers from current QGIS project (no filtering).

    Returns:
        List of dictionaries with keys: 'name', 'id', 'type', 'source'
    """
    try:
        from qgis.core import QgsProject

        layers = []
        project = QgsProject.instance()

        if not project:
            return []

        for layer_id, layer in project.mapLayers().items():
            # Check if it's a raster layer
            if hasattr(layer, 'rasterType'):
                layers.append({
                    'name': layer.name(),
                    'id': layer_id,
                    'type': 'raster',
                    'source': layer.source() if hasattr(layer, 'source') else ''
                })

        return layers

    except Exception as e:
        print(f"Error getting layers: {e}")
        return []


def get_layer_by_id(layer_id: str):
    """
    Get QGIS layer by ID.

    Args:
        layer_id: Layer ID string

    Returns:
        QgsMapLayer object or None if not found
    """
    try:
        from qgis.core import QgsProject

        project = QgsProject.instance()
        if not project:
            return None

        return project.mapLayer(layer_id)

    except Exception as e:
        print(f"Error getting layer by ID: {e}")
        return None


def get_layer_by_name(layer_name: str):
    """
    Get QGIS layer by name.

    Args:
        layer_name: Layer name string

    Returns:
        QgsMapLayer object or None if not found
    """
    try:
        from qgis.core import QgsProject

        project = QgsProject.instance()
        if not project:
            return None

        for layer_id, layer in project.mapLayers().items():
            if layer.name() == layer_name:
                return layer

        return None

    except Exception as e:
        print(f"Error getting layer by name: {e}")
        return None


def is_qgis_project_open() -> bool:
    """
    Check if a QGIS project is currently open.

    Returns:
        True if project is open, False otherwise
    """
    try:
        from qgis.core import QgsProject

        project = QgsProject.instance()
        if not project:
            return False

        # Check if project has any layers
        return len(project.mapLayers()) > 0

    except Exception as e:
        print(f"Error checking QGIS project: {e}")
        return False


def get_project_crs() -> Optional[str]:
    """
    Get the coordinate reference system (CRS) of the current QGIS project.

    Returns:
        CRS as string (e.g., 'EPSG:4326') or None if project not open
    """
    try:
        from qgis.core import QgsProject

        project = QgsProject.instance()
        if not project:
            return None

        crs = project.crs()
        return crs.authid() if crs else None

    except Exception as e:
        print(f"Error getting project CRS: {e}")
        return None


def setup_qgis_environment():
    """
    Setup QGIS environment variables if not already set.

    This function attempts to configure the Python environment to work
    with QGIS. It should be called before importing QGIS modules.

    Returns:
        Tuple of (success, message)
    """
    # Check if QGIS modules are already available
    try:
        import qgis.core
        return True, "QGIS modules already available"
    except ImportError:
        pass

    # Try to find QGIS installation
    qgis_path = find_qgis_installation()

    if not qgis_path:
        return False, (
            "QGIS installation not found. Please ensure QGIS is installed "
            "and run this application using the provided launcher script."
        )

    # Set environment variables
    if sys.platform == 'win32':
        # Windows
        os.environ['QGIS_PREFIX_PATH'] = qgis_path
        bin_path = os.path.join(qgis_path, 'bin')
        if os.path.exists(bin_path):
            os.environ['PATH'] = bin_path + os.pathsep + os.environ.get('PATH', '')

        # Add Python path
        python_path = os.path.join(qgis_path, 'python')
        if os.path.exists(python_path):
            sys.path.insert(0, python_path)

    elif sys.platform == 'darwin':
        # macOS
        os.environ['QGIS_PREFIX_PATH'] = qgis_path
        python_path = os.path.join(qgis_path, 'Resources/python')
        if os.path.exists(python_path):
            sys.path.insert(0, python_path)

    else:
        # Linux
        python_path = '/usr/share/qgis/python'
        if os.path.exists(python_path):
            sys.path.insert(0, python_path)

    # Try importing again
    try:
        import qgis.core
        return True, f"QGIS environment setup successfully (path: {qgis_path})"
    except ImportError as e:
        return False, f"Failed to import QGIS modules after setup: {str(e)}"


def get_qgis_info() -> Dict[str, str]:
    """
    Get information about the QGIS installation.

    Returns:
        Dictionary with QGIS version, installation path, and other info
    """
    info = {}

    # Check if QGIS is available
    is_available, version = detect_qgis()
    info['available'] = is_available
    info['version'] = version if version else 'Unknown'

    # Get installation path
    qgis_path = find_qgis_installation()
    info['installation_path'] = qgis_path if qgis_path else 'Not found'

    # Check if project is open
    if is_available:
        info['project_open'] = is_qgis_project_open()
        info['project_crs'] = get_project_crs() or 'No project'
        info['num_layers'] = len(get_all_raster_layers())
    else:
        info['project_open'] = False
        info['project_crs'] = 'N/A'
        info['num_layers'] = 0

    return info
