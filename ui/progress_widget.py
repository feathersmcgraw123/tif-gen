"""
Progress tracking widget.

Displays:
- Progress bar
- Current tile / total tiles
- Current row / total rows
- Time elapsed
- Estimated time remaining (ETA)
- Log messages
- Pause/Resume and Cancel buttons
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QProgressBar, QLabel,
    QPushButton, QTextEdit, QGroupBox
)
from PyQt5.QtCore import Qt, pyqtSignal


class ProgressWidget(QWidget):
    """Widget for displaying export progress."""

    # Signals
    pause_requested = pyqtSignal()
    resume_requested = pyqtSignal()
    cancel_requested = pyqtSignal()

    def __init__(self, translator=None, parent=None):
        super().__init__(parent)

        self.translator = translator
        self.is_paused = False
        self.init_ui()

    def refresh_ui(self):
        """Refresh UI text after language change."""
        if not self.translator:
            return
        # For now, progress widget strings remain in English
        # Can be extended to translate if needed
        pass

    def init_ui(self):
        """Initialize user interface."""
        layout = QVBoxLayout(self)

        # Progress bar group
        progress_group = QGroupBox("Export Progress")
        progress_layout = QVBoxLayout()

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        progress_layout.addWidget(self.progress_bar)

        # Status labels
        status_layout = QHBoxLayout()

        self.tile_label = QLabel("Tiles: 0 / 0")
        status_layout.addWidget(self.tile_label)

        self.row_label = QLabel("Row: 0 / 0")
        status_layout.addWidget(self.row_label)

        self.elapsed_label = QLabel("Elapsed: 00:00")
        status_layout.addWidget(self.elapsed_label)

        self.eta_label = QLabel("ETA: --:--")
        status_layout.addWidget(self.eta_label)

        status_layout.addStretch()

        progress_layout.addLayout(status_layout)

        # Control buttons
        button_layout = QHBoxLayout()

        self.pause_resume_btn = QPushButton("Pause")
        self.pause_resume_btn.clicked.connect(self.on_pause_resume_clicked)
        self.pause_resume_btn.setEnabled(False)
        button_layout.addWidget(self.pause_resume_btn)

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.on_cancel_clicked)
        self.cancel_btn.setEnabled(False)
        button_layout.addWidget(self.cancel_btn)

        button_layout.addStretch()

        progress_layout.addLayout(button_layout)

        progress_group.setLayout(progress_layout)
        layout.addWidget(progress_group)

        # Log output
        log_group = QGroupBox("Log Output")
        log_layout = QVBoxLayout()

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(200)
        log_layout.addWidget(self.log_text)

        log_group.setLayout(log_layout)
        layout.addWidget(log_group)

    def on_pause_resume_clicked(self):
        """Handle pause/resume button click."""
        if self.is_paused:
            self.resume_requested.emit()
            self.is_paused = False
            self.pause_resume_btn.setText("Pause")
            self.add_log("Export resumed")
        else:
            self.pause_requested.emit()
            self.is_paused = True
            self.pause_resume_btn.setText("Resume")
            self.add_log("Export paused")

    def on_cancel_clicked(self):
        """Handle cancel button click."""
        self.cancel_requested.emit()
        self.pause_resume_btn.setEnabled(False)
        self.cancel_btn.setEnabled(False)
        self.add_log("Cancelling export...")

    def update_progress(self, tile_num: int, total_tiles: int, row_num: int, total_rows: int, elapsed: float):
        """
        Update progress display.

        Args:
            tile_num: Current tile number
            total_tiles: Total number of tiles
            row_num: Current row number
            total_rows: Total number of rows
            elapsed: Elapsed time in seconds
        """
        # Update progress bar
        if total_tiles > 0:
            progress = int((tile_num / total_tiles) * 100)
            self.progress_bar.setValue(progress)

        # Update labels
        self.tile_label.setText(f"Tiles: {tile_num} / {total_tiles}")
        self.row_label.setText(f"Row: {row_num} / {total_rows}")

        # Format elapsed time
        elapsed_str = self.format_time(elapsed)
        self.elapsed_label.setText(f"Elapsed: {elapsed_str}")

        # Calculate and format ETA
        if tile_num > 0 and total_tiles > tile_num:
            progress_fraction = tile_num / total_tiles
            eta = (elapsed / progress_fraction) - elapsed
            eta_str = self.format_time(eta)
            self.eta_label.setText(f"ETA: {eta_str}")
        else:
            self.eta_label.setText("ETA: --:--")

    def format_time(self, seconds: float) -> str:
        """
        Format time in seconds to MM:SS or HH:MM:SS.

        Args:
            seconds: Time in seconds

        Returns:
            Formatted time string
        """
        if seconds < 0:
            return "--:--"

        seconds = int(seconds)
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60

        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes:02d}:{secs:02d}"

    def add_log(self, message: str):
        """
        Add log message.

        Args:
            message: Log message to add
        """
        self.log_text.append(message)
        # Auto-scroll to bottom
        self.log_text.verticalScrollBar().setValue(
            self.log_text.verticalScrollBar().maximum()
        )

    def clear_log(self):
        """Clear log output."""
        self.log_text.clear()

    def reset(self):
        """Reset progress display to initial state."""
        self.progress_bar.setValue(0)
        self.tile_label.setText("Tiles: 0 / 0")
        self.row_label.setText("Row: 0 / 0")
        self.elapsed_label.setText("Elapsed: 00:00")
        self.eta_label.setText("ETA: --:--")
        self.is_paused = False
        self.pause_resume_btn.setText("Pause")
        self.pause_resume_btn.setEnabled(False)
        self.cancel_btn.setEnabled(False)

    def set_export_started(self):
        """Enable controls when export starts."""
        self.pause_resume_btn.setEnabled(True)
        self.cancel_btn.setEnabled(True)
        self.is_paused = False
        self.pause_resume_btn.setText("Pause")

    def set_export_finished(self, success: bool, message: str):
        """
        Handle export completion.

        Args:
            success: Whether export succeeded
            message: Completion message
        """
        self.pause_resume_btn.setEnabled(False)
        self.cancel_btn.setEnabled(False)

        if success:
            self.progress_bar.setValue(100)
            self.add_log(f"SUCCESS: {message}")
        else:
            self.add_log(f"ERROR: {message}")
