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
    progress_updated = pyqtSignal(int, int, int, int, float)  # tile, total_tiles, row, total_rows, elapsed
    log_message = pyqtSignal(str)  # Log message
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

    def _on_progress(self, tile_num: int, total_tiles: int, row_num: int, total_rows: int, elapsed: float):
        """Handle progress update from exporter."""
        self.progress_updated.emit(tile_num, total_tiles, row_num, total_rows, elapsed)

    def _on_log(self, message: str):
        """Handle log message from exporter."""
        self.log_message.emit(message)

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
