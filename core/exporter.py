"""
GeoTIFF export engine with tiled rendering - Standalone version.

This module provides the core export functionality by downloading tiles
directly from XYZ tile servers (no QGIS required).

Uses rasterio instead of GDAL for easier installation.
"""

import os
import time
import tempfile
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Tuple, Dict, Optional, Callable
import numpy as np
from PIL import Image
import rasterio
from rasterio.transform import from_bounds
from rasterio.warp import calculate_default_transform, reproject, Resampling
from rasterio.mask import mask as rasterio_mask
from rasterio.crs import CRS
from rasterio import windows
import json

from .geometry import coords_4326_to_3857, calculate_bbox, calculate_output_dimensions
from .tile_downloader import (
    TileDownloader, calculate_zoom_level, get_tile_bbox_for_polygon,
    lat_lon_to_tile_coords, tile_coords_to_bbox, meters_per_pixel_at_zoom
)
from .tile_sources import get_source_by_id, xy_to_quadkey
from utils.file_utils import save_cutline_geojson


class ExportConfig:
    """Configuration for GeoTIFF export."""

    def __init__(self,
                 coords_4326: List[Tuple[float, float]],
                 output_path: str,
                 tile_source_id: str = 'google_satellite',
                 meters_per_pixel: float = 0.6,
                 compression: str = 'LZW',
                 jpeg_quality: int = 90,
                 output_crs: str = 'EPSG:4326',
                 render_delay: float = 0.2,
                 zoom_level: Optional[int] = None):
        """
        Initialize export configuration.

        Args:
            coords_4326: List of (lat, lon) tuples defining polygon
            output_path: Output GeoTIFF file path
            tile_source_id: Tile source ID (e.g., 'google_satellite')
            meters_per_pixel: Desired resolution in meters per pixel (ignored if zoom_level is set)
            compression: Compression type ('LZW' or 'JPEG')
            jpeg_quality: JPEG quality 1-100 (if using JPEG)
            output_crs: Output coordinate system ('EPSG:4326' or 'EPSG:3857')
            render_delay: Delay between tile downloads in seconds
            zoom_level: Fixed zoom level (0-20). If provided, takes precedence over meters_per_pixel
        """
        self.coords_4326 = coords_4326
        self.output_path = output_path
        self.tile_source_id = tile_source_id
        self.meters_per_pixel = meters_per_pixel
        self.compression = compression
        self.jpeg_quality = jpeg_quality
        self.output_crs = output_crs
        self.render_delay = render_delay
        self.zoom_level = zoom_level


class GeoTIFFExporter:
    """Export satellite imagery to georeferenced GeoTIFF."""

    def __init__(self, config: ExportConfig):
        """
        Initialize exporter.

        Args:
            config: ExportConfig object with export settings
        """
        self.config = config
        self.is_paused = False
        self.is_cancelled = False
        self.progress_callback: Optional[Callable] = None
        self.log_callback: Optional[Callable] = None

        # Temporary files
        self.temp_cutline_path = None

        # Export state
        self.start_time = None
        self.current_tile = 0
        self.total_tiles = 0

    def set_progress_callback(self, callback: Callable[[int, int, int, int, float], None]):
        """Set progress callback function."""
        self.progress_callback = callback

    def set_log_callback(self, callback: Callable[[str], None]):
        """Set log message callback function."""
        self.log_callback = callback

    def log(self, message: str):
        """Log a message."""
        if self.log_callback:
            self.log_callback(message)
        else:
            print(message)

    def pause(self):
        """Pause the export."""
        self.is_paused = True
        self.log("Export paused")

    def resume(self):
        """Resume the export."""
        self.is_paused = False
        self.log("Export resumed")

    def cancel(self):
        """Cancel the export."""
        self.is_cancelled = True
        self.log("Export cancellation requested")

    def export(self) -> Tuple[bool, str]:
        """
        Main export method - downloads tiles and creates GeoTIFF.

        Returns:
            Tuple of (success, message)
        """
        try:
            self.start_time = time.time()
            self.log("=== Starting GeoTIFF Export ===")

            # Get tile source
            tile_source = get_source_by_id(self.config.tile_source_id)
            if not tile_source:
                return False, f"Tile source not found: {self.config.tile_source_id}"

            self.log(f"Tile source: {tile_source.name}")

            # Calculate appropriate zoom level
            center_lat = sum(c[0] for c in self.config.coords_4326) / len(self.config.coords_4326)

            if self.config.zoom_level is not None:
                # Use fixed zoom level from config
                zoom = self.config.zoom_level
                actual_mpp = meters_per_pixel_at_zoom(zoom, center_lat)
                self.log(f"Using fixed zoom level {zoom} (≈{actual_mpp:.2f} m/px at center)")
            else:
                # Calculate zoom from desired meters per pixel
                zoom = calculate_zoom_level(center_lat, self.config.meters_per_pixel)
                actual_mpp = meters_per_pixel_at_zoom(zoom, center_lat)
                self.log(f"Using calculated zoom level {zoom} (≈{actual_mpp:.2f} m/px at center)")

            # Calculate tile bounding box
            min_tile_x, min_tile_y, max_tile_x, max_tile_y = get_tile_bbox_for_polygon(
                self.config.coords_4326, zoom
            )

            tiles_x = max_tile_x - min_tile_x + 1
            tiles_y = max_tile_y - min_tile_y + 1
            self.total_tiles = tiles_x * tiles_y

            self.log(f"Tile range: X[{min_tile_x}-{max_tile_x}], Y[{min_tile_y}-{max_tile_y}]")
            self.log(f"Total tiles: {tiles_x} x {tiles_y} = {self.total_tiles}")

            # Calculate output dimensions (256px per tile)
            TILE_SIZE = 256
            output_width = tiles_x * TILE_SIZE
            output_height = tiles_y * TILE_SIZE

            self.log(f"Output size: {output_width} x {output_height} px")
            self.log(f"Estimated size: {output_width * output_height * 3 / 1e6:.0f} MB (uncompressed)")

            # Calculate geographic extent
            lon_min, lat_min, _, _ = tile_coords_to_bbox(min_tile_x, max_tile_y, zoom)
            _, _, lon_max, lat_max = tile_coords_to_bbox(max_tile_x, min_tile_y, zoom)

            self.log(f"Geographic extent: ({lat_min:.6f}, {lon_min:.6f}) to ({lat_max:.6f}, {lon_max:.6f})")

            # Create temporary files
            self._create_temp_files()

            # Create output GeoTIFF
            temp_output = self.config.output_path + ".tmp.tif"

            # Calculate file size estimate
            estimated_mb = (output_width * output_height * 3) / (1024 * 1024)
            self.log(f"Estimated uncompressed size: {estimated_mb:.0f} MB")

            # Download tiles and write directly to GeoTIFF (memory-efficient)
            self.log("Starting tile download and export...")
            success, message = self._download_and_write_tiles(
                tile_source, zoom,
                min_tile_x, min_tile_y, max_tile_x, max_tile_y,
                output_width, output_height,
                temp_output,
                lon_min, lat_min, lon_max, lat_max
            )

            if not success:
                self._cleanup_temp_files()
                if os.path.exists(temp_output):
                    os.remove(temp_output)
                return False, message

            # GeoTIFF is now created with tiles written directly to it
            # Clip to polygon and optionally reproject
            self.log("Clipping to polygon...")
            success, message = self._clip_and_finalize(temp_output)

            # Cleanup
            if os.path.exists(temp_output):
                os.remove(temp_output)

            self._cleanup_temp_files()

            if not success:
                return False, message

            elapsed = time.time() - self.start_time
            file_size = os.path.getsize(self.config.output_path) / 1e6

            self.log(f"Export completed in {elapsed / 60:.1f} minutes")
            self.log(f"Output file: {self.config.output_path} ({file_size:.1f} MB)")

            return True, "Export completed successfully"

        except Exception as e:
            self._cleanup_temp_files()
            error_msg = f"Export failed: {str(e)}"
            self.log(error_msg)
            import traceback
            self.log(traceback.format_exc())
            return False, error_msg

    def _create_temp_files(self):
        """Create temporary file paths."""
        temp_dir = tempfile.gettempdir()
        timestamp = str(int(time.time()))

        self.temp_cutline_path = os.path.join(temp_dir, f"cutline_{timestamp}.geojson")

        # Save cutline GeoJSON
        save_cutline_geojson(self.config.coords_4326, self.temp_cutline_path)

    def _cleanup_temp_files(self):
        """Clean up temporary files."""
        if self.temp_cutline_path and os.path.exists(self.temp_cutline_path):
            try:
                os.remove(self.temp_cutline_path)
            except Exception as e:
                self.log(f"Warning: Failed to remove temp file {self.temp_cutline_path}: {e}")

    def _get_tile_url(self, tile_source, tx: int, ty: int, zoom: int) -> str:
        """Build tile URL for given coordinates."""
        if self.config.tile_source_id == 'bing_satellite':
            quadkey = xy_to_quadkey(tx, ty, zoom)
            return tile_source.url_template.replace('{quadkey}', quadkey).replace('{s}', '0')
        return tile_source.get_tile_url(tx, ty, zoom)

    def _process_tile(self, tx: int, ty: int, zoom: int, tile_source) -> Tuple[int, int, Optional[np.ndarray]]:
        """Download and process a single tile (runs in thread pool)."""
        TILE_SIZE = 256

        while self.is_paused and not self.is_cancelled:
            time.sleep(0.1)

        if self.is_cancelled:
            return tx, ty, None

        url = self._get_tile_url(tile_source, tx, ty, zoom)

        # Each thread gets its own downloader/session (requests.Session is not thread-safe)
        if not hasattr(self._thread_local, 'downloader'):
            self._thread_local.downloader = TileDownloader()
        downloader = self._thread_local.downloader

        max_retries = 3
        img = None
        for retry in range(max_retries):
            img = downloader.download_tile(url, delay=self.config.render_delay)
            if img is not None:
                break
            if retry < max_retries - 1:
                time.sleep((retry + 1) * 1.0)

        if img is None:
            img = Image.new('RGB', (TILE_SIZE, TILE_SIZE), (0, 0, 0))

        # Handle RGBA with PIL native alpha compositing (avoids float32 intermediate arrays)
        if img.mode == 'RGBA':
            bg = Image.new('RGBA', img.size, (0, 0, 0, 255))
            img = Image.alpha_composite(bg, img).convert('RGB')
        elif img.mode != 'RGB':
            img = img.convert('RGB')

        arr = np.array(img)

        # Single-pass white pixel removal: any pixel with all channels >= 230 → black
        # (equivalent to the old 4-pass loop but in one vectorised operation)
        is_white = (arr.min(axis=2) >= 230) & np.any(arr > 0, axis=2)
        if is_white.any():
            arr[is_white] = 0

        return tx, ty, arr

    def _download_and_write_tiles(self, tile_source, zoom: int,
                                  min_tile_x: int, min_tile_y: int, max_tile_x: int, max_tile_y: int,
                                  output_width: int, output_height: int,
                                  output_path: str,
                                  lon_min: float, lat_min: float, lon_max: float, lat_max: float) -> Tuple[bool, str]:
        """
        Download tiles in parallel and write directly to GeoTIFF using windowed writes.

        Uses a thread pool for concurrent downloads while writing to disk from the
        main thread as results arrive.
        """
        try:
            TILE_SIZE = 256
            NUM_WORKERS = 4
            tiles_x = max_tile_x - min_tile_x + 1
            tiles_y = max_tile_y - min_tile_y + 1
            self.total_tiles = tiles_x * tiles_y
            self._thread_local = threading.local()

            transform = from_bounds(lon_min, lat_min, lon_max, lat_max, output_width, output_height)

            if self.config.compression == 'JPEG':
                compress = 'JPEG'
                extra_options = {'JPEG_QUALITY': self.config.jpeg_quality}
            else:
                compress = 'LZW'
                extra_options = {}

            self.log(f"Creating GeoTIFF file: {output_width}x{output_height} pixels")
            # Log every ~tiles_x completions (≈ once per row)
            log_interval = max(1, tiles_x)

            # No tiled=True here — GDAL's block cache doesn't handle out-of-order
            # writes to tiled TIFFs reliably. The final clipped output is tiled.
            with rasterio.open(
                output_path, 'w',
                driver='GTiff',
                height=output_height,
                width=output_width,
                count=3,
                dtype=np.uint8,
                crs=CRS.from_epsg(4326),
                transform=transform,
                compress=compress,
                **extra_options
            ) as dst:
                tile_num = 0

                with ThreadPoolExecutor(max_workers=NUM_WORKERS) as executor:
                    futures = {
                        executor.submit(self._process_tile, tx, ty, zoom, tile_source): (tx, ty)
                        for ty in range(min_tile_y, max_tile_y + 1)
                        for tx in range(min_tile_x, max_tile_x + 1)
                    }

                    for fut in as_completed(futures):
                        if self.is_cancelled:
                            for f in futures:
                                f.cancel()
                            return False, "Export cancelled by user"

                        tx, ty, arr = fut.result()
                        if arr is None:
                            continue  # tile was skipped due to cancellation

                        tile_num += 1
                        self.current_tile = tile_num
                        px_x = (tx - min_tile_x) * TILE_SIZE
                        px_y = (ty - min_tile_y) * TILE_SIZE
                        tile_h, tile_w = arr.shape[:2]

                        # Clamp to file bounds — edge tiles from some servers are full 256px
                        # even when the logical tile is smaller, which would overrun the file
                        tile_h = min(tile_h, output_height - px_y)
                        tile_w = min(tile_w, output_width - px_x)
                        if tile_h <= 0 or tile_w <= 0:
                            continue
                        arr = arr[:tile_h, :tile_w]

                        window = windows.Window(px_x, px_y, tile_w, tile_h)

                        try:
                            dst.write(arr[:, :, 0], 1, window=window)
                            dst.write(arr[:, :, 1], 2, window=window)
                            dst.write(arr[:, :, 2], 3, window=window)
                        except Exception as e:
                            self.log(f"  WARNING: Failed to write tile ({tx},{ty}): {e}")

                        # Throttle progress/log to once per row-equivalent
                        if tile_num % log_interval == 0 or tile_num == self.total_tiles:
                            elapsed = time.time() - self.start_time
                            pct = tile_num / self.total_tiles * 100
                            eta = elapsed / tile_num * (self.total_tiles - tile_num) if tile_num < self.total_tiles else 0
                            self.log(f"  {tile_num}/{self.total_tiles} tiles ({pct:.0f}%) - ETA {eta/60:.1f} min")
                            if self.progress_callback:
                                row_num = ty - min_tile_y + 1
                                self.progress_callback(tile_num, self.total_tiles, row_num, tiles_y, elapsed)

            elapsed_total = time.time() - self.start_time
            self.log(f"Download and export complete in {elapsed_total/60:.1f} min")
            return True, "Tiles downloaded and written successfully"

        except Exception as e:
            return False, f"Tile download/write failed: {str(e)}"

    def _clip_and_finalize(self, temp_output: str) -> Tuple[bool, str]:
        """Clip to polygon and apply final settings."""
        try:
            # Load polygon from GeoJSON
            with open(self.temp_cutline_path, 'r') as f:
                geojson = json.load(f)

            # Extract polygon geometry
            polygon_geom = geojson['features'][0]['geometry']

            # Open source raster
            with rasterio.open(temp_output) as src:
                # Reproject if needed
                if self.config.output_crs == 'EPSG:3857':
                    # Need to reproject to 3857
                    dst_crs = CRS.from_epsg(3857)

                    # Calculate transform for reprojection
                    transform, width, height = calculate_default_transform(
                        src.crs, dst_crs, src.width, src.height, *src.bounds
                    )

                    # Prepare compression
                    if self.config.compression == 'JPEG':
                        compress = 'JPEG'
                        extra_options = {'JPEG_QUALITY': self.config.jpeg_quality}
                    else:
                        compress = 'LZW'
                        extra_options = {}

                    # Create output with reprojection
                    kwargs = src.meta.copy()
                    kwargs.update({
                        'crs': dst_crs,
                        'transform': transform,
                        'width': width,
                        'height': height,
                        'compress': compress,
                        'tiled': True,
                        **extra_options
                    })

                    temp_reproj = temp_output + ".reproj.tif"

                    with rasterio.open(temp_reproj, 'w', **kwargs) as dst:
                        for i in range(1, src.count + 1):
                            reproject(
                                source=rasterio.band(src, i),
                                destination=rasterio.band(dst, i),
                                src_transform=src.transform,
                                src_crs=src.crs,
                                dst_transform=transform,
                                dst_crs=dst_crs,
                                resampling=Resampling.bilinear
                            )

                    # Now clip the reprojected image
                    with rasterio.open(temp_reproj) as src_reproj:
                        # Note: polygon is still in EPSG:4326, need to use it as-is with mask
                        out_image, out_transform = rasterio_mask(src_reproj, [polygon_geom], crop=True, nodata=0)

                        out_meta = src_reproj.meta.copy()
                        out_meta.update({
                            "height": out_image.shape[1],
                            "width": out_image.shape[2],
                            "transform": out_transform,
                            "nodata": 0
                        })

                        with rasterio.open(self.config.output_path, 'w', **out_meta) as dest:
                            dest.write(out_image)

                    # Cleanup temp reprojected file
                    if os.path.exists(temp_reproj):
                        os.remove(temp_reproj)

                else:
                    # Just clip, no reprojection
                    out_image, out_transform = rasterio_mask(src, [polygon_geom], crop=True, nodata=0)

                    # Prepare compression
                    if self.config.compression == 'JPEG':
                        compress = 'JPEG'
                        extra_options = {'JPEG_QUALITY': self.config.jpeg_quality}
                    else:
                        compress = 'LZW'
                        extra_options = {}

                    out_meta = src.meta.copy()
                    out_meta.update({
                        "height": out_image.shape[1],
                        "width": out_image.shape[2],
                        "transform": out_transform,
                        "compress": compress,
                        "tiled": True,
                        "nodata": 0,
                        **extra_options
                    })

                    with rasterio.open(self.config.output_path, 'w', **out_meta) as dest:
                        dest.write(out_image)

            return True, "Clip and finalize completed"

        except Exception as e:
            return False, f"Clip/finalize failed: {str(e)}"
