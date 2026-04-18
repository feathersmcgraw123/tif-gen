"""
Tile downloading utilities.

Handles downloading tiles from XYZ tile servers with:
- HTTP requests with user agent
- Retry logic
- Rate limiting
- Tile coordinate calculation
"""

import math
import time
import requests
from typing import Tuple, Optional
from io import BytesIO
from PIL import Image


class TileDownloader:
    """Downloads tiles from XYZ tile servers."""

    def __init__(self, user_agent: str = None, timeout: int = 10, max_retries: int = 3):
        """
        Initialize tile downloader.

        Args:
            user_agent: User agent string for HTTP requests
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
        """
        self.user_agent = user_agent or (
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/91.0.4472.124 Safari/537.36'
        )
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': self.user_agent})

    def download_tile(self, url: str, delay: float = 0.0) -> Optional[Image.Image]:
        """
        Download a tile from URL.

        Args:
            url: Tile URL
            delay: Delay before download (seconds)

        Returns:
            PIL Image object or None if download failed
        """
        if delay > 0:
            time.sleep(delay)

        for attempt in range(self.max_retries):
            try:
                response = self.session.get(url, timeout=self.timeout)
                response.raise_for_status()

                # Validate response has content
                if len(response.content) < 100:  # Suspiciously small
                    if attempt < self.max_retries - 1:
                        continue
                    return None

                # Load image from response
                img = Image.open(BytesIO(response.content))

                # Verify image loaded properly
                img.load()  # Force image data to be loaded/decoded

                # Validate image dimensions
                if img.size[0] == 0 or img.size[1] == 0:
                    if attempt < self.max_retries - 1:
                        continue
                    return None

                return img

            except requests.exceptions.RequestException as e:
                if attempt < self.max_retries - 1:
                    # Wait before retry (exponential backoff)
                    wait_time = (2 ** attempt) * 0.5
                    time.sleep(wait_time)
                else:
                    print(f"Failed to download tile after {self.max_retries} attempts: {url}")
                    print(f"Error: {e}")
                    return None

            except Exception as e:
                # Image decoding error - likely corrupted data
                if attempt < self.max_retries - 1:
                    wait_time = (2 ** attempt) * 0.5
                    time.sleep(wait_time)
                else:
                    print(f"Error processing tile image after {self.max_retries} attempts: {e}")
                    return None

        return None


def lat_lon_to_tile_coords(lat: float, lon: float, zoom: int) -> Tuple[int, int]:
    """
    Convert latitude/longitude to tile coordinates at given zoom level.

    Args:
        lat: Latitude in degrees
        lon: Longitude in degrees
        zoom: Zoom level

    Returns:
        Tuple of (tile_x, tile_y)
    """
    lat_rad = math.radians(lat)
    n = 2.0 ** zoom
    tile_x = int((lon + 180.0) / 360.0 * n)
    tile_y = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
    return tile_x, tile_y


def tile_coords_to_bbox(tile_x: int, tile_y: int, zoom: int) -> Tuple[float, float, float, float]:
    """
    Convert tile coordinates to bounding box (lat/lon).

    Args:
        tile_x: Tile X coordinate
        tile_y: Tile Y coordinate
        zoom: Zoom level

    Returns:
        Tuple of (lon_min, lat_min, lon_max, lat_max)
    """
    n = 2.0 ** zoom

    lon_min = tile_x / n * 360.0 - 180.0
    lat_min_rad = math.atan(math.sinh(math.pi * (1 - 2 * (tile_y + 1) / n)))
    lat_min = math.degrees(lat_min_rad)

    lon_max = (tile_x + 1) / n * 360.0 - 180.0
    lat_max_rad = math.atan(math.sinh(math.pi * (1 - 2 * tile_y / n)))
    lat_max = math.degrees(lat_max_rad)

    return lon_min, lat_min, lon_max, lat_max


def calculate_zoom_level(lat: float, meters_per_pixel: float) -> int:
    """
    Calculate appropriate zoom level for desired resolution.

    Args:
        lat: Latitude (affects scale due to Web Mercator projection)
        meters_per_pixel: Desired resolution in meters per pixel

    Returns:
        Zoom level (0-20)
    """
    # At equator, zoom 0 = 156543 m/px, each zoom level halves the resolution
    equator_meters_per_pixel = 156543.03392  # At zoom 0
    lat_rad = math.radians(lat)

    # Adjust for latitude (Web Mercator distortion)
    meters_per_pixel_at_lat = meters_per_pixel / math.cos(lat_rad)

    # Calculate zoom level
    zoom = math.log2(equator_meters_per_pixel / meters_per_pixel_at_lat)

    # Clamp to valid range
    zoom = max(0, min(20, int(round(zoom))))

    return zoom


def get_tile_bbox_for_polygon(coords_4326: list, zoom: int) -> Tuple[int, int, int, int]:
    """
    Calculate tile bounding box for polygon.

    Args:
        coords_4326: List of (lat, lon) tuples
        zoom: Zoom level

    Returns:
        Tuple of (min_tile_x, min_tile_y, max_tile_x, max_tile_y)
    """
    if not coords_4326:
        raise ValueError("Empty coordinates list")

    # Find bounding box in lat/lon
    lats = [coord[0] for coord in coords_4326]
    lons = [coord[1] for coord in coords_4326]

    min_lat, max_lat = min(lats), max(lats)
    min_lon, max_lon = min(lons), max(lons)

    # Convert corners to tile coordinates
    # In tile coordinates: Y increases downward, X increases eastward
    # Northwest corner (max_lat, min_lon) gives min_tile_x, min_tile_y
    # Southeast corner (min_lat, max_lon) gives max_tile_x, max_tile_y
    min_tile_x, min_tile_y = lat_lon_to_tile_coords(max_lat, min_lon, zoom)
    max_tile_x, max_tile_y = lat_lon_to_tile_coords(min_lat, max_lon, zoom)

    return min_tile_x, min_tile_y, max_tile_x, max_tile_y


def meters_per_pixel_at_zoom(zoom: int, lat: float) -> float:
    """
    Calculate meters per pixel at given zoom level and latitude.

    Args:
        zoom: Zoom level
        lat: Latitude in degrees

    Returns:
        Meters per pixel
    """
    # Earth circumference at equator
    earth_circumference = 40075016.686  # meters

    # Meters per pixel at equator for this zoom level
    equator_mpp = earth_circumference / (256 * (2 ** zoom))

    # Adjust for latitude
    lat_rad = math.radians(lat)
    mpp = equator_mpp * math.cos(lat_rad)

    return mpp
