"""
Tile cache dialog.

Shows what's currently cached on disk (per tile source, size, tile count)
and lets the user clear it.

Stats computation and clearing both run in background QThreads — a real
cache can hold hundreds of thousands of files, and walking/deleting that
many synchronously on the GUI thread would freeze the whole app.
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal

from core.tile_cache import default_cache_dir, get_cache_stats, clear_cache
from core.geometry import format_file_size


class _StatsWorker(QThread):
    """Computes cache stats off the GUI thread."""

    stats_ready = pyqtSignal(dict)

    def __init__(self, cache_dir: str):
        super().__init__()
        self.cache_dir = cache_dir

    def run(self):
        self.stats_ready.emit(get_cache_stats(self.cache_dir))


class _ClearWorker(QThread):
    """Clears the cache off the GUI thread."""

    clear_done = pyqtSignal(bool, str)

    def __init__(self, cache_dir: str):
        super().__init__()
        self.cache_dir = cache_dir

    def run(self):
        success, message = clear_cache(self.cache_dir)
        self.clear_done.emit(success, message)


class CacheDialog(QDialog):
    """Dialog for viewing and clearing the tile cache."""

    def __init__(self, parent=None, translator=None, cache_dir=None):
        super().__init__(parent)

        self.translator = translator
        self.cache_dir = cache_dir or default_cache_dir()
        self._stats_worker = None
        self._clear_worker = None

        self.setWindowTitle("Tile Cache")
        self.setMinimumSize(520, 400)

        self.init_ui()
        self.refresh_stats()

    def init_ui(self):
        """Initialize user interface."""
        layout = QVBoxLayout(self)

        self.path_label = QLabel(f"Cache location: {self.cache_dir}")
        self.path_label.setWordWrap(True)
        self.path_label.setStyleSheet("QLabel { color: #666; }")
        layout.addWidget(self.path_label)

        self.total_label = QLabel("Computing cache stats...")
        self.total_label.setStyleSheet("QLabel { font-weight: bold; font-size: 12pt; }")
        layout.addWidget(self.total_label)

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Tile Source", "Tiles", "Size"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.table)

        button_layout = QHBoxLayout()

        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.refresh_stats)
        button_layout.addWidget(self.refresh_btn)

        button_layout.addStretch()

        self.clear_btn = QPushButton("Clear Cache")
        self.clear_btn.setStyleSheet("QPushButton { color: #c00; }")
        self.clear_btn.setEnabled(False)
        self.clear_btn.clicked.connect(self.on_clear_clicked)
        button_layout.addWidget(self.clear_btn)

        self.close_btn = QPushButton("Close")
        self.close_btn.clicked.connect(self.accept)
        button_layout.addWidget(self.close_btn)

        layout.addLayout(button_layout)

    def _set_busy(self, busy: bool, message: str = None):
        """Disable controls while a background stats/clear job is running."""
        self.refresh_btn.setEnabled(not busy)
        self.clear_btn.setEnabled(not busy and self.table.rowCount() > 0)
        self.close_btn.setEnabled(not busy)
        if message:
            self.total_label.setText(message)

    def refresh_stats(self):
        """Recompute and display cache stats (runs in background)."""
        if self._stats_worker and self._stats_worker.isRunning():
            return

        self._set_busy(True, "Computing cache stats...")

        self._stats_worker = _StatsWorker(self.cache_dir)
        self._stats_worker.stats_ready.connect(self._on_stats_ready)
        self._stats_worker.start()

    def _on_stats_ready(self, stats: dict):
        """Handle background stats computation completion."""
        self.total_label.setText(
            f"Total: {stats['total_files']} tiles, {format_file_size(stats['total_bytes'])}"
        )

        by_source = stats['by_source']
        self.table.setRowCount(len(by_source))

        for row, (source_id, info) in enumerate(sorted(by_source.items(), key=lambda kv: -kv[1]['bytes'])):
            self.table.setItem(row, 0, QTableWidgetItem(info['name']))
            self.table.setItem(row, 1, QTableWidgetItem(str(info['files'])))
            self.table.setItem(row, 2, QTableWidgetItem(format_file_size(info['bytes'])))

        self._set_busy(False)
        self.clear_btn.setEnabled(stats['total_files'] > 0)

    def on_clear_clicked(self):
        """Handle clear cache button click."""
        reply = QMessageBox.question(
            self,
            "Clear Tile Cache",
            "This will permanently delete all cached tiles from disk. "
            "Future exports will need to re-download them. This may take a "
            "while for a large cache. Continue?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply != QMessageBox.Yes:
            return

        self._set_busy(True, "Clearing cache...")

        self._clear_worker = _ClearWorker(self.cache_dir)
        self._clear_worker.clear_done.connect(self._on_clear_done)
        self._clear_worker.start()

    def _on_clear_done(self, success: bool, message: str):
        """Handle background cache clear completion."""
        if success:
            QMessageBox.information(self, "Cache Cleared", "Tile cache cleared successfully.")
            self.refresh_stats()
        else:
            self._set_busy(False)
            QMessageBox.warning(self, "Error", message)

    def _is_busy(self) -> bool:
        return bool(
            (self._stats_worker and self._stats_worker.isRunning()) or
            (self._clear_worker and self._clear_worker.isRunning())
        )

    def closeEvent(self, event):
        """Prevent closing (X button / Alt+F4) while a background job is still running."""
        if self._is_busy():
            event.ignore()
        else:
            event.accept()

    def reject(self):
        """Prevent closing (Escape key) while a background job is still running."""
        if self._is_busy():
            return
        super().reject()
