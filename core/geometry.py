"""
Coordinate conversion and polygon geometry utilities.

This module provides functions for:
- Converting between EPSG:4326 (WGS84) and EPSG:3857 (Web Mercator)
- Validating polygon geometry
- Calculating bounding boxes and output dimensions
"""

import math
from typing import List, Tuple, Dict


def lon_to_3857_x(lon: float) -> float:
    """
    Convert longitude (EPSG:4326) to Web Mercator X coordinate (EPSG:3857).

    Args:
        lon: Longitude in degrees (-180 to 180)

    Returns:
        X coordinate in meters in EPSG:3857
    """
    return lon * 20037508.34 / 180.0


def lat_to_3857_y(lat: float) -> float:
    """
    Convert latitude (EPSG:4326) to Web Mercator Y coordinate (EPSG:3857).

    Args:
        lat: Latitude in degrees (-85.05 to 85.05)

    Returns:
        Y coordinate in meters in EPSG:3857
    """
    y = math.log(math.tan((90 + lat) * math.pi / 360.0)) / (math.pi / 180.0)
    return y * 20037508.34 / 180.0


def coords_4326_to_3857(coords_4326: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
    """
    Convert a list of (lat, lon) coordinates to EPSG:3857.

    Args:
        coords_4326: List of (latitude, longitude) tuples

    Returns:
        List of (x, y) tuples in EPSG:3857 meters
    """
    coords_3857 = []
    for lat, lon in coords_4326:
        x = lon_to_3857_x(lon)
        y = lat_to_3857_y(lat)
        coords_3857.append((x, y))
    return coords_3857


def validate_polygon(coords: List[Tuple[float, float]]) -> Tuple[bool, str]:
    """
    Validate polygon geometry.

    Checks:
    - At least 3 vertices
    - Coordinates within valid ranges
    - No consecutive duplicate points

    Args:
        coords: List of (lat, lon) tuples

    Returns:
        Tuple of (is_valid, error_message)
    """
    if len(coords) < 3:
        return False, "Polygon must have at least 3 vertices"

    # Check coordinate ranges
    for i, (lat, lon) in enumerate(coords):
        if not (-90 <= lat <= 90):
            return False, f"Invalid latitude at vertex {i+1}: {lat} (must be -90 to 90)"
        if not (-180 <= lon <= 180):
            return False, f"Invalid longitude at vertex {i+1}: {lon} (must be -180 to 180)"

    # Check for consecutive duplicates
    for i in range(len(coords) - 1):
        if coords[i] == coords[i + 1]:
            return False, f"Duplicate consecutive vertices at positions {i+1} and {i+2}"

    # Check if first and last points are the same (closed polygon)
    # If they are, that's fine - we'll handle this in close_polygon()

    return True, ""


def close_polygon(coords: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
    """
    Ensure polygon is closed by repeating first coordinate at end if needed.

    Args:
        coords: List of (lat, lon) tuples

    Returns:
        Closed polygon coordinates
    """
    if len(coords) < 3:
        return coords

    # If first and last coordinates are not the same, close it
    if coords[0] != coords[-1]:
        return coords + [coords[0]]

    return coords


def check_self_intersection(coords: List[Tuple[float, float]]) -> Tuple[bool, str]:
    """
    Check if polygon has self-intersections using a simple algorithm.

    Note: This is a basic implementation. For production use, consider
    using Shapely or other geometry libraries for robust intersection detection.

    Args:
        coords: List of (lat, lon) tuples

    Returns:
        Tuple of (has_intersection, message)
    """
    if len(coords) < 4:
        return False, ""

    # Simple check: for small polygons, basic edge crossing detection
    # For large/complex polygons, this should be enhanced with proper algorithms

    def ccw(A, B, C):
        """Check if three points are in counter-clockwise order"""
        return (C[1] - A[1]) * (B[0] - A[0]) > (B[1] - A[1]) * (C[0] - A[0])

    def segments_intersect(A, B, C, D):
        """Check if line segment AB intersects with CD"""
        return ccw(A, C, D) != ccw(B, C, D) and ccw(A, B, C) != ccw(A, B, D)

    # Check each edge against all non-adjacent edges
    n = len(coords)
    for i in range(n - 1):
        for j in range(i + 2, n - 1):
            # Skip adjacent edges
            if j == i + 1 or (i == 0 and j == n - 2):
                continue

            if segments_intersect(coords[i], coords[i + 1], coords[j], coords[j + 1]):
                return True, f"Self-intersection detected between edges {i+1} and {j+1}"

    return False, ""


def calculate_bbox(coords_3857: List[Tuple[float, float]]) -> Dict[str, float]:
    """
    Calculate bounding box in EPSG:3857.

    Args:
        coords_3857: List of (x, y) tuples in EPSG:3857 meters

    Returns:
        Dictionary with keys: x_min, x_max, y_min, y_max, x_span, y_span
    """
    if not coords_3857:
        raise ValueError("Empty coordinates list")

    xs = [c[0] for c in coords_3857]
    ys = [c[1] for c in coords_3857]

    x_min, x_max = min(xs), max(xs)
    y_min, y_max = min(ys), max(ys)
    x_span = x_max - x_min
    y_span = y_max - y_min

    return {
        'x_min': x_min,
        'x_max': x_max,
        'y_min': y_min,
        'y_max': y_max,
        'x_span': x_span,
        'y_span': y_span
    }


def calculate_output_dimensions(bbox: Dict[str, float], meters_per_pixel: float) -> Dict[str, float]:
    """
    Calculate output raster dimensions.

    Args:
        bbox: Bounding box dictionary from calculate_bbox()
        meters_per_pixel: Desired resolution in meters per pixel

    Returns:
        Dictionary with keys: total_width, total_height, pixel_w, pixel_h
    """
    x_span = bbox['x_span']
    y_span = bbox['y_span']

    total_width = int(round(x_span / meters_per_pixel))
    total_height = int(round(y_span / meters_per_pixel))

    # Recalculate actual pixel size (may differ slightly due to rounding)
    pixel_w = x_span / total_width
    pixel_h = y_span / total_height

    return {
        'total_width': total_width,
        'total_height': total_height,
        'pixel_w': pixel_w,
        'pixel_h': pixel_h
    }


def calculate_polygon_area(coords_4326: List[Tuple[float, float]]) -> float:
    """
    Calculate approximate polygon area in square kilometers.

    Uses a simple planar approximation suitable for small to medium-sized polygons.
    For more accurate results, use proper geodesic calculations.

    Args:
        coords_4326: List of (lat, lon) tuples

    Returns:
        Area in square kilometers
    """
    if len(coords_4326) < 3:
        return 0.0

    # Convert to 3857 (meters)
    coords_3857 = coords_4326_to_3857(coords_4326)

    # Shoelace formula
    area_m2 = 0.0
    n = len(coords_3857)
    for i in range(n):
        j = (i + 1) % n
        area_m2 += coords_3857[i][0] * coords_3857[j][1]
        area_m2 -= coords_3857[j][0] * coords_3857[i][1]

    area_m2 = abs(area_m2) / 2.0
    area_km2 = area_m2 / 1_000_000  # Convert to km²

    return area_km2


def estimate_file_size(total_width: int, total_height: int,
                       compression: str = 'LZW', jpeg_quality: int = 90) -> Tuple[int, int]:
    """
    Estimate output file size.

    Args:
        total_width: Output width in pixels
        total_height: Output height in pixels
        compression: Compression type ('LZW' or 'JPEG')
        jpeg_quality: JPEG quality (1-100) if using JPEG compression

    Returns:
        Tuple of (uncompressed_bytes, estimated_compressed_bytes)
    """
    # Raw size: 3 bytes per pixel (RGB)
    raw_size = total_width * total_height * 3

    # Estimate compressed size
    if compression == 'LZW':
        # LZW typically achieves 2:1 to 3:1 compression on satellite imagery
        compressed_size = int(raw_size * 0.4)  # Assume 2.5:1 compression
    elif compression == 'JPEG':
        # JPEG compression depends on quality
        if jpeg_quality >= 90:
            compressed_size = int(raw_size * 0.1)  # ~10:1 at high quality
        elif jpeg_quality >= 75:
            compressed_size = int(raw_size * 0.05)  # ~20:1 at medium quality
        else:
            compressed_size = int(raw_size * 0.03)  # ~33:1 at low quality
    else:
        # No compression
        compressed_size = raw_size

    return raw_size, compressed_size


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.

    Args:
        size_bytes: Size in bytes

    Returns:
        Formatted string (e.g., "1.5 GB", "250 MB")
    """
    # Handle negative or zero values
    if size_bytes < 0:
        return f"Error: negative size ({size_bytes} B)"
    if size_bytes == 0:
        return "0 B"

    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"
