"""
QThread worker for background export.

This module provides a QThread worker that runs the export in the background
to keep the UI responsive. It emits signals for progress updates and completion.
"""

from PyQt5.QtCore import QThread, pyqtSignal

from .exporter import GeoTIFFExporter


class ExportWorker(QThread):
    """Worker thread for running GeoTIFF export in background."""

    # Signals
    progress_updated = pyqtSignal(int, int, int, int, float, int, int)  # tile, total_tiles, row, total_rows, elapsed, cache_hits, cache_misses
    log_message = pyqtSignal(str)  # Log message
    tile_downloaded = pyqtSignal(int, int, object)  # tile_x, tile_y, rgb numpy array
    clip_progress = pyqtSignal(object, int, int)  # preview_canvas, rows_done, total_rows
    export_complete = pyqtSignal(bool, str)  # success, message

    def __init__(self, exporter: GeoTIFFExporter):
        """
        Initialize export worker.

        Args:
            exporter: GeoTIFFExporter instance configured with export settings
        """
        super().__init__()
        self.exporter = exporter

        # Connect callbacks
        self.exporter.set_progress_callback(self._on_progress)
        self.exporter.set_log_callback(self._on_log)
        self.exporter.set_tile_callback(self._on_tile_downloaded)
        self.exporter.set_clip_callback(self._on_clip_progress)

    def _on_progress(self, tile_num: int, total_tiles: int, row_num: int, total_rows: int, elapsed: float,
                      cache_hits: int = 0, cache_misses: int = 0):
        """Handle progress update from exporter."""
        self.progress_updated.emit(tile_num, total_tiles, row_num, total_rows, elapsed, cache_hits, cache_misses)

    def _on_log(self, message: str):
        """Handle log message from exporter."""
        self.log_message.emit(message)

    def _on_tile_downloaded(self, tile_x: int, tile_y: int, arr):
        """Handle a newly downloaded/written tile from exporter."""
        self.tile_downloaded.emit(tile_x, tile_y, arr)

    def _on_clip_progress(self, preview_canvas, rows_done: int, total_rows: int):
        """Handle a clip/assembly progress update from exporter."""
        self.clip_progress.emit(preview_canvas, rows_done, total_rows)

    def run(self):
        """Run export in background thread."""
        try:
            success, message = self.exporter.export()
            self.export_complete.emit(success, message)
        except Exception as e:
            self.export_complete.emit(False, f"Unexpected error: {str(e)}")

    def pause(self):
        """Pause the export."""
        self.exporter.pause()

    def resume(self):
        """Resume the export."""
        self.exporter.resume()

    def cancel(self):
        """Cancel the export."""
        self.exporter.cancel()
