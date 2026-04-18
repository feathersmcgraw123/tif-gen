"""
File I/O utilities for polygon import/export.

This module provides functions for:
- Loading polygons from GeoJSON files
- Loading polygons from CSV files
- Saving cutline GeoJSON for gdal.Warp
- File validation
"""

import json
import csv
from typing import List, Tuple, Optional, Dict


def load_geojson(filepath: str) -> Tuple[bool, List[Tuple[float, float]], str]:
    """
    Parse GeoJSON and extract polygon coordinates.

    Supports:
    - Polygon geometry
    - MultiPolygon (takes first polygon)
    - Feature or FeatureCollection with Polygon geometry

    Args:
        filepath: Path to GeoJSON file

    Returns:
        Tuple of (success, coordinates, message)
        coordinates is list of (lat, lon) tuples
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Extract geometry from different GeoJSON structures
        geometry = None

        if 'type' in data:
            if data['type'] == 'FeatureCollection':
                if 'features' in data and len(data['features']) > 0:
                    geometry = data['features'][0].get('geometry')
            elif data['type'] == 'Feature':
                geometry = data.get('geometry')
            elif data['type'] in ['Polygon', 'MultiPolygon']:
                geometry = data
            else:
                return False, [], f"Unsupported GeoJSON type: {data['type']}"

        if not geometry:
            return False, [], "No geometry found in GeoJSON"

        # Extract coordinates based on geometry type
        coords = []

        if geometry['type'] == 'Polygon':
            # Polygon: coordinates[0] is outer ring
            ring = geometry['coordinates'][0]
            # GeoJSON format is [lon, lat]
            coords = [(lat, lon) for lon, lat in ring]

        elif geometry['type'] == 'MultiPolygon':
            # MultiPolygon: take first polygon's outer ring
            ring = geometry['coordinates'][0][0]
            coords = [(lat, lon) for lon, lat in ring]

        else:
            return False, [], f"Unsupported geometry type: {geometry['type']}"

        if len(coords) < 3:
            return False, [], f"Polygon must have at least 3 vertices, found {len(coords)}"

        return True, coords, f"Loaded {len(coords)} vertices from GeoJSON"

    except json.JSONDecodeError as e:
        return False, [], f"Invalid JSON format: {str(e)}"
    except FileNotFoundError:
        return False, [], f"File not found: {filepath}"
    except Exception as e:
        return False, [], f"Error loading GeoJSON: {str(e)}"


def load_csv(filepath: str, lat_col: str = 'lat', lon_col: str = 'lon') -> Tuple[bool, List[Tuple[float, float]], str]:
    """
    Parse CSV and extract coordinates from specified columns.

    Args:
        filepath: Path to CSV file
        lat_col: Name of latitude column (default: 'lat')
        lon_col: Name of longitude column (default: 'lon')

    Returns:
        Tuple of (success, coordinates, message)
        coordinates is list of (lat, lon) tuples
    """
    try:
        coords = []

        with open(filepath, 'r', encoding='utf-8') as f:
            # Detect delimiter (comma or semicolon)
            sample = f.read(1024)
            f.seek(0)
            dialect = csv.Sniffer().sniff(sample)
            reader = csv.DictReader(f, dialect=dialect)

            # Check if columns exist
            if lat_col not in reader.fieldnames:
                return False, [], f"Column '{lat_col}' not found in CSV. Available columns: {', '.join(reader.fieldnames)}"
            if lon_col not in reader.fieldnames:
                return False, [], f"Column '{lon_col}' not found in CSV. Available columns: {', '.join(reader.fieldnames)}"

            # Read coordinates
            for i, row in enumerate(reader, start=2):  # Start at 2 (header is row 1)
                try:
                    lat = float(row[lat_col].strip())
                    lon = float(row[lon_col].strip())
                    coords.append((lat, lon))
                except ValueError:
                    return False, [], f"Invalid numeric value at row {i}"

        if len(coords) < 3:
            return False, [], f"Polygon must have at least 3 vertices, found {len(coords)}"

        return True, coords, f"Loaded {len(coords)} vertices from CSV"

    except FileNotFoundError:
        return False, [], f"File not found: {filepath}"
    except csv.Error as e:
        return False, [], f"CSV parsing error: {str(e)}"
    except Exception as e:
        return False, [], f"Error loading CSV: {str(e)}"


def detect_csv_columns(filepath: str) -> Tuple[bool, List[str], str]:
    """
    Detect column names in CSV file.

    Args:
        filepath: Path to CSV file

    Returns:
        Tuple of (success, column_names, message)
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            sample = f.read(1024)
            f.seek(0)
            dialect = csv.Sniffer().sniff(sample)
            reader = csv.DictReader(f, dialect=dialect)
            columns = reader.fieldnames

            if not columns:
                return False, [], "No columns found in CSV"

            return True, columns, f"Found {len(columns)} columns"

    except Exception as e:
        return False, [], f"Error reading CSV: {str(e)}"


def save_cutline_geojson(coords_4326: List[Tuple[float, float]], output_path: str) -> Tuple[bool, str]:
    """
    Save polygon as GeoJSON for gdal.Warp cutline.

    The cutline must be in EPSG:4326 format for gdal.Warp to work correctly.

    Args:
        coords_4326: List of (lat, lon) tuples
        output_path: Path to save GeoJSON file

    Returns:
        Tuple of (success, message)
    """
    try:
        # GeoJSON format: [lon, lat]
        coordinates = [[lon, lat] for lat, lon in coords_4326]

        # Ensure polygon is closed
        if coordinates[0] != coordinates[-1]:
            coordinates.append(coordinates[0])

        geojson = {
            "type": "FeatureCollection",
            "features": [{
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [coordinates]
                },
                "properties": {}
            }]
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(geojson, f, indent=2)

        return True, f"Cutline saved to {output_path}"

    except Exception as e:
        return False, f"Error saving cutline: {str(e)}"


def validate_file_extension(filepath: str, allowed_extensions: List[str]) -> Tuple[bool, str]:
    """
    Validate file extension.

    Args:
        filepath: Path to file
        allowed_extensions: List of allowed extensions (e.g., ['.geojson', '.json'])

    Returns:
        Tuple of (is_valid, message)
    """
    import os

    ext = os.path.splitext(filepath)[1].lower()

    if ext not in allowed_extensions:
        return False, f"Invalid file extension '{ext}'. Allowed: {', '.join(allowed_extensions)}"

    return True, ""


def get_csv_preview(filepath: str, max_rows: int = 5) -> Tuple[bool, List[Dict], str]:
    """
    Get preview of CSV file contents.

    Args:
        filepath: Path to CSV file
        max_rows: Maximum number of rows to preview

    Returns:
        Tuple of (success, rows, message)
        rows is list of dictionaries (column -> value)
    """
    try:
        rows = []

        with open(filepath, 'r', encoding='utf-8') as f:
            sample = f.read(1024)
            f.seek(0)
            dialect = csv.Sniffer().sniff(sample)
            reader = csv.DictReader(f, dialect=dialect)

            for i, row in enumerate(reader):
                if i >= max_rows:
                    break
                rows.append(dict(row))

        return True, rows, f"Preview of {len(rows)} rows"

    except Exception as e:
        return False, [], f"Error reading CSV: {str(e)}"


def check_file_writable(filepath: str) -> Tuple[bool, str]:
    """
    Check if file path is writable.

    Args:
        filepath: Path to check

    Returns:
        Tuple of (is_writable, message)
    """
    import os

    # Check if directory exists
    directory = os.path.dirname(filepath)
    if not directory:
        directory = '.'

    if not os.path.exists(directory):
        return False, f"Directory does not exist: {directory}"

    if not os.access(directory, os.W_OK):
        return False, f"No write permission for directory: {directory}"

    # Check if file exists and is writable
    if os.path.exists(filepath):
        if not os.access(filepath, os.W_OK):
            return False, f"File exists but is not writable: {filepath}"

    return True, "Path is writable"


def get_available_disk_space(path: str) -> int:
    """
    Get available disk space at path in bytes.

    Args:
        path: File or directory path

    Returns:
        Available space in bytes
    """
    import shutil
    import os

    # Get directory if path is a file
    if os.path.isfile(path):
        path = os.path.dirname(path)

    # If path doesn't exist, use parent directory
    while not os.path.exists(path):
        path = os.path.dirname(path)
        if not path or path == os.path.dirname(path):  # Reached root
            path = '.'
            break

    try:
        stat = shutil.disk_usage(path)
        return stat.free
    except Exception:
        return 0


def ensure_output_extension(filepath: str, extension: str) -> str:
    """
    Ensure output file has the correct extension.

    Args:
        filepath: Original file path
        extension: Desired extension (e.g., '.tif')

    Returns:
        File path with correct extension
    """
    import os

    if not extension.startswith('.'):
        extension = '.' + extension

    current_ext = os.path.splitext(filepath)[1].lower()

    if current_ext != extension:
        # Replace or add extension
        base = os.path.splitext(filepath)[0]
        return base + extension

    return filepath
