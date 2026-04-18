"""
Tile server source configurations.

Provides URL templates and configurations for various satellite imagery
tile servers including Google, Bing, ESRI, and OpenStreetMap.
"""

from typing import Dict, List
import random


class TileSource:
    """Represents a tile server configuration."""

    def __init__(self, name: str, url_template: str, max_zoom: int = 19,
                 attribution: str = "", subdomains: List[str] = None):
        """
        Initialize tile source.

        Args:
            name: Display name
            url_template: URL template with {x}, {y}, {z} placeholders
            max_zoom: Maximum zoom level supported
            attribution: Attribution text
            subdomains: List of subdomains (e.g., ['a', 'b', 'c'])
        """
        self.name = name
        self.url_template = url_template
        self.max_zoom = max_zoom
        self.attribution = attribution
        self.subdomains = subdomains or []

    def get_tile_url(self, x: int, y: int, z: int) -> str:
        """
        Get tile URL for given tile coordinates.

        Args:
            x: Tile X coordinate
            y: Tile Y coordinate
            z: Zoom level

        Returns:
            Complete tile URL
        """
        url = self.url_template

        # Replace placeholders
        url = url.replace('{x}', str(x))
        url = url.replace('{y}', str(y))
        url = url.replace('{z}', str(z))

        # Handle subdomains
        if self.subdomains and '{s}' in url:
            subdomain = random.choice(self.subdomains)
            url = url.replace('{s}', subdomain)

        return url


# Pre-configured tile sources
TILE_SOURCES = {
    'google_satellite': TileSource(
        name='Google Satellite',
        url_template='https://mt{s}.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',
        max_zoom=20,
        attribution='© Google',
        subdomains=['0', '1', '2', '3']
    ),

    'google_hybrid': TileSource(
        name='Google Hybrid (Satellite + Labels)',
        url_template='https://mt{s}.google.com/vt/lyrs=y&x={x}&y={y}&z={z}',
        max_zoom=20,
        attribution='© Google',
        subdomains=['0', '1', '2', '3']
    ),

    'google_terrain': TileSource(
        name='Google Terrain',
        url_template='https://mt{s}.google.com/vt/lyrs=p&x={x}&y={y}&z={z}',
        max_zoom=20,
        attribution='© Google',
        subdomains=['0', '1', '2', '3']
    ),

    'esri_world_imagery': TileSource(
        name='ESRI World Imagery',
        url_template='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        max_zoom=19,
        attribution='© ESRI'
    ),

    'bing_satellite': TileSource(
        name='Bing Satellite',
        url_template='http://ecn.t{s}.tiles.virtualearth.net/tiles/a{quadkey}.jpeg?g=1',
        max_zoom=19,
        attribution='© Microsoft',
        subdomains=['0', '1', '2', '3']
    ),

    'osm_standard': TileSource(
        name='OpenStreetMap Standard',
        url_template='https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
        max_zoom=19,
        attribution='© OpenStreetMap contributors',
        subdomains=['a', 'b', 'c']
    ),

    'carto_light': TileSource(
        name='CartoDB Positron (Light)',
        url_template='https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png',
        max_zoom=19,
        attribution='© CartoDB',
        subdomains=['a', 'b', 'c', 'd']
    ),

    'carto_dark': TileSource(
        name='CartoDB Dark Matter',
        url_template='https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png',
        max_zoom=19,
        attribution='© CartoDB',
        subdomains=['a', 'b', 'c', 'd']
    ),
}


def get_available_sources() -> Dict[str, TileSource]:
    """Get all available tile sources."""
    return TILE_SOURCES


def get_source_by_id(source_id: str) -> TileSource:
    """
    Get tile source by ID.

    Args:
        source_id: Source identifier (e.g., 'google_satellite')

    Returns:
        TileSource object or None if not found
    """
    return TILE_SOURCES.get(source_id)


def xy_to_quadkey(x: int, y: int, z: int) -> str:
    """
    Convert XYZ tile coordinates to Bing quadkey.

    Required for Bing tile URLs.

    Args:
        x: Tile X coordinate
        y: Tile Y coordinate
        z: Zoom level

    Returns:
        Quadkey string
    """
    quadkey = ''
    for i in range(z, 0, -1):
        digit = 0
        mask = 1 << (i - 1)
        if x & mask:
            digit += 1
        if y & mask:
            digit += 2
        quadkey += str(digit)
    return quadkey


# Update Bing source URL to use quadkey
def get_bing_tile_url(x: int, y: int, z: int, subdomain: str = '0') -> str:
    """Get Bing tile URL with quadkey."""
    quadkey = xy_to_quadkey(x, y, z)
    return f'http://ecn.t{subdomain}.tiles.virtualearth.net/tiles/a{quadkey}.jpeg?g=1'
