"""
Main application window.

Integrates all components:
- Polygon definition dialog
- Export configuration widget
- Progress tracking widget
- Direct tile source access
- Export worker threading
"""

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QGroupBox, QPushButton, QLabel, QMessageBox, QMenuBar, QMenu, QAction
)
from PyQt5.QtCore import Qt

from core.exporter import ExportConfig, GeoTIFFExporter
from core.export_worker import ExportWorker
from core.tile_sources import get_available_sources
from utils.file_utils import check_file_writable, get_available_disk_space
from utils.translations import get_translator
from core.geometry import estimate_file_size, format_file_size
from core.tile_downloader import calculate_zoom_level, get_tile_bbox_for_polygon, meters_per_pixel_at_zoom

from .polygon_dialog import PolygonDialog
from .config_widget import ConfigWidget
from .progress_widget import ProgressWidget


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()

        self.polygon_coords = None
        self.export_worker = None
        self.translator = get_translator()

        self.setWindowTitle(self.translator.tr('app_title'))
        self.setMinimumSize(1000, 700)

        self.init_ui()
        self.log_startup()

    def init_ui(self):
        """Initialize user interface."""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)

        # Create menu bar
        self.create_menu_bar()

        # Top section: Polygon + Config
        top_splitter = QSplitter(Qt.Orientation.Horizontal)

        # Polygon definition section
        self.polygon_group = QGroupBox(self.translator.tr('section_polygon'))
        polygon_layout = QVBoxLayout()

        self.polygon_status_label = QLabel(self.translator.tr('polygon_not_defined'))
        self.polygon_status_label.setStyleSheet("QLabel { color: #666; font-style: italic; }")
        polygon_layout.addWidget(self.polygon_status_label)

        self.define_polygon_btn = QPushButton(self.translator.tr('btn_define_polygon'))
        self.define_polygon_btn.clicked.connect(self.on_define_polygon_clicked)
        polygon_layout.addWidget(self.define_polygon_btn)

        polygon_layout.addStretch()

        self.polygon_group.setLayout(polygon_layout)
        top_splitter.addWidget(self.polygon_group)

        # Export configuration section
        self.config_group = QGroupBox(self.translator.tr('section_config'))
        config_layout = QVBoxLayout()

        self.config_widget = ConfigWidget(self.translator)
        self.config_widget.config_changed.connect(self.update_export_button_state)
        config_layout.addWidget(self.config_widget)

        self.config_group.setLayout(config_layout)
        top_splitter.addWidget(self.config_group)

        main_layout.addWidget(top_splitter, stretch=2)

        # Export button
        export_layout = QHBoxLayout()
        export_layout.addStretch()

        self.start_export_btn = QPushButton(self.translator.tr('btn_start_export'))
        self.start_export_btn.setEnabled(False)
        self.start_export_btn.setMinimumHeight(40)
        self.start_export_btn.setStyleSheet("QPushButton { font-size: 14pt; font-weight: bold; }")
        self.start_export_btn.clicked.connect(self.on_start_export_clicked)
        export_layout.addWidget(self.start_export_btn)

        export_layout.addStretch()

        main_layout.addLayout(export_layout)

        # Bottom section: Progress
        self.progress_group = QGroupBox(self.translator.tr('section_progress'))
        progress_layout = QVBoxLayout()

        self.progress_widget = ProgressWidget(self.translator)
        self.progress_widget.pause_requested.connect(self.on_pause_requested)
        self.progress_widget.resume_requested.connect(self.on_resume_requested)
        self.progress_widget.cancel_requested.connect(self.on_cancel_requested)
        progress_layout.addWidget(self.progress_widget)

        self.progress_group.setLayout(progress_layout)
        main_layout.addWidget(self.progress_group, stretch=1)

    def create_menu_bar(self):
        """Create menu bar."""
        menubar = self.menuBar()

        # File menu
        self.file_menu = menubar.addMenu(self.translator.tr('menu_file'))

        self.exit_action = QAction(self.translator.tr('menu_exit'), self)
        self.exit_action.triggered.connect(self.close)
        self.file_menu.addAction(self.exit_action)

        # Language menu
        self.language_menu = menubar.addMenu(self.translator.tr('menu_language'))

        # Create language actions
        self.language_actions = []
        for lang_code, lang_name in self.translator.get_available_languages():
            action = QAction(lang_name, self)
            action.setCheckable(True)
            action.setChecked(lang_code == self.translator.language)
            action.triggered.connect(lambda checked, code=lang_code: self.on_language_changed(code))
            self.language_menu.addAction(action)
            self.language_actions.append((lang_code, action))

        # Help menu
        self.help_menu = menubar.addMenu(self.translator.tr('menu_help'))

        self.about_action = QAction(self.translator.tr('menu_about'), self)
        self.about_action.triggered.connect(self.show_about)
        self.help_menu.addAction(self.about_action)

        self.sources_action = QAction(self.translator.tr('menu_tile_sources'), self)
        self.sources_action.triggered.connect(self.show_tile_sources)
        self.help_menu.addAction(self.sources_action)

    def log_startup(self):
        """Log startup information."""
        self.progress_widget.add_log("=== Satellite Imagery Export Tool ===")
        self.progress_widget.add_log("Application started successfully")

        # List available tile sources
        sources = get_available_sources()
        self.progress_widget.add_log(f"Available tile sources: {len(sources)}")
        for source_id, source in sources.items():
            self.progress_widget.add_log(f"  - {source.name}")

    def on_define_polygon_clicked(self):
        """Open polygon definition dialog."""
        dialog = PolygonDialog(self, self.polygon_coords, self.translator)

        if dialog.exec() == PolygonDialog.DialogCode.Accepted:
            self.polygon_coords = dialog.get_coordinates()

            # Update status
            num_vertices = len(self.polygon_coords)
            self.polygon_status_label.setText(
                self.translator.tr('polygon_defined').format(num_vertices)
            )
            self.polygon_status_label.setStyleSheet("QLabel { color: green; font-weight: bold; }")

            # Update config widget for size estimation
            self.config_widget.set_polygon_coords(self.polygon_coords)

            # Enable export button if config is valid
            self.update_export_button_state()

            self.progress_widget.add_log(f"Polygon defined with {num_vertices} vertices")

    def on_start_export_clicked(self):
        """Start export process."""
        # Validate configuration
        is_valid, error_msg = self.config_widget.is_valid()

        if not is_valid:
            QMessageBox.warning(self, "Invalid Configuration", error_msg)
            return

        # Check polygon
        if not self.polygon_coords:
            QMessageBox.warning(self, "No Polygon", "Please define an export polygon first.")
            return

        # Check output path is writable
        output_path = self.config_widget.get_output_path()
        is_writable, message = check_file_writable(output_path)

        if not is_writable:
            QMessageBox.warning(self, "Output Path Error", message)
            return

        # Check disk space
        estimated_size = self.estimate_output_size()
        available_space = get_available_disk_space(output_path)

        if available_space < estimated_size * 1.5:  # Need 1.5x for temp files
            QMessageBox.warning(
                self,
                "Insufficient Disk Space",
                f"Estimated output size: {format_file_size(estimated_size)}\n"
                f"Available disk space: {format_file_size(available_space)}\n\n"
                f"Please free up disk space or choose a different output location."
            )
            return

        # Confirm start
        reply = QMessageBox.question(
            self,
            "Start Export",
            f"Ready to start export.\n\n"
            f"Output: {output_path}\n"
            f"Estimated size: {format_file_size(estimated_size)}\n\n"
            f"This may take several minutes to hours depending on the area size.\n"
            f"Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        # Create export config
        # Use zoom level if not in advanced mode, otherwise use meters per pixel
        if self.config_widget.is_advanced_mode():
            config = ExportConfig(
                coords_4326=self.polygon_coords,
                output_path=output_path,
                tile_source_id=self.config_widget.get_tile_source_id(),
                meters_per_pixel=self.config_widget.get_resolution(),
                compression=self.config_widget.get_compression(),
                jpeg_quality=self.config_widget.get_jpeg_quality(),
                output_crs=self.config_widget.get_output_crs(),
                render_delay=self.config_widget.get_render_delay(),
                zoom_level=self.config_widget.get_zoom_level()
            )
        else:
            config = ExportConfig(
                coords_4326=self.polygon_coords,
                output_path=output_path,
                tile_source_id=self.config_widget.get_tile_source_id(),
                compression=self.config_widget.get_compression(),
                jpeg_quality=self.config_widget.get_jpeg_quality(),
                output_crs=self.config_widget.get_output_crs(),
                render_delay=self.config_widget.get_render_delay(),
                zoom_level=self.config_widget.get_zoom_level()
            )

        # Create exporter
        exporter = GeoTIFFExporter(config)

        # Create worker
        self.export_worker = ExportWorker(exporter)
        self.export_worker.progress_updated.connect(self.on_progress_updated)
        self.export_worker.log_message.connect(self.on_log_message)
        self.export_worker.export_complete.connect(self.on_export_complete)

        # Update UI
        self.start_export_btn.setEnabled(False)
        self.define_polygon_btn.setEnabled(False)
        self.progress_widget.reset()
        self.progress_widget.set_export_started()

        # Start export
        self.export_worker.start()
        self.progress_widget.add_log("Export started...")

    def on_progress_updated(self, tile_num, total_tiles, row_num, total_rows, elapsed):
        """Handle progress update from export worker."""
        self.progress_widget.update_progress(tile_num, total_tiles, row_num, total_rows, elapsed)

    def on_log_message(self, message):
        """Handle log message from export worker."""
        self.progress_widget.add_log(message)

    def on_export_complete(self, success, message):
        """Handle export completion."""
        self.progress_widget.set_export_finished(success, message)

        # Re-enable UI
        self.start_export_btn.setEnabled(True)
        self.define_polygon_btn.setEnabled(True)

        # Show completion message
        if success:
            QMessageBox.information(
                self,
                "Export Complete",
                f"Export completed successfully!\n\n{message}"
            )
        else:
            QMessageBox.critical(
                self,
                "Export Failed",
                f"Export failed:\n\n{message}"
            )

        self.export_worker = None

    def on_pause_requested(self):
        """Handle pause request."""
        if self.export_worker:
            self.export_worker.pause()

    def on_resume_requested(self):
        """Handle resume request."""
        if self.export_worker:
            self.export_worker.resume()

    def on_cancel_requested(self):
        """Handle cancel request."""
        if self.export_worker:
            reply = QMessageBox.question(
                self,
                "Cancel Export",
                "Are you sure you want to cancel the export?\n\n"
                "Progress will be lost and partial files will be deleted.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                self.export_worker.cancel()

    def update_export_button_state(self):
        """Enable/disable export button based on configuration."""
        has_polygon = self.polygon_coords is not None
        config_valid, _ = self.config_widget.is_valid()

        self.start_export_btn.setEnabled(has_polygon and config_valid)

    def estimate_output_size(self):
        """Estimate output file size in bytes."""
        if not self.polygon_coords:
            return 0

        # Get zoom level from config widget (preset or advanced)
        zoom = self.config_widget.get_zoom_level()

        # Get tile count
        min_tile_x, min_tile_y, max_tile_x, max_tile_y = get_tile_bbox_for_polygon(
            self.polygon_coords, zoom
        )

        tiles_x = max_tile_x - min_tile_x + 1
        tiles_y = max_tile_y - min_tile_y + 1

        # Calculate output dimensions (256px per tile)
        TILE_SIZE = 256
        total_width = tiles_x * TILE_SIZE
        total_height = tiles_y * TILE_SIZE

        _, compressed_size = estimate_file_size(
            total_width,
            total_height,
            self.config_widget.get_compression(),
            self.config_widget.get_jpeg_quality()
        )

        return compressed_size

    def on_language_changed(self, language_code):
        """Handle language change."""
        # Change language
        self.translator.set_language(language_code)

        # Update language action checkmarks
        for lang_code, action in self.language_actions:
            action.setChecked(lang_code == language_code)

        # Refresh UI
        self.refresh_ui()

    def refresh_ui(self):
        """Refresh all UI text after language change."""
        # Update window title
        self.setWindowTitle(self.translator.tr('app_title'))

        # Update menus
        self.file_menu.setTitle(self.translator.tr('menu_file'))
        self.exit_action.setText(self.translator.tr('menu_exit'))
        self.language_menu.setTitle(self.translator.tr('menu_language'))
        self.help_menu.setTitle(self.translator.tr('menu_help'))
        self.about_action.setText(self.translator.tr('menu_about'))
        self.sources_action.setText(self.translator.tr('menu_tile_sources'))

        # Update group boxes
        self.polygon_group.setTitle(self.translator.tr('section_polygon'))
        self.config_group.setTitle(self.translator.tr('section_config'))
        self.progress_group.setTitle(self.translator.tr('section_progress'))

        # Update buttons
        self.define_polygon_btn.setText(self.translator.tr('btn_define_polygon'))
        self.start_export_btn.setText(self.translator.tr('btn_start_export'))

        # Update polygon status
        if self.polygon_coords:
            num_vertices = len(self.polygon_coords)
            self.polygon_status_label.setText(
                self.translator.tr('polygon_defined').format(num_vertices)
            )
        else:
            self.polygon_status_label.setText(self.translator.tr('polygon_not_defined'))

        # Refresh child widgets
        self.config_widget.refresh_ui()
        self.progress_widget.refresh_ui()

    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            self.translator.tr('about_title'),
            self.translator.tr('about_text')
        )

    def show_tile_sources(self):
        """Show available tile sources dialog."""
        sources = get_available_sources()

        info_text = "<h3>Available Tile Sources</h3>"
        info_text += "<table style='width:100%'>"
        info_text += "<tr><th align='left'>Source</th><th align='left'>Max Zoom</th><th align='left'>Attribution</th></tr>"

        for source_id, source in sources.items():
            info_text += f"<tr><td>{source.name}</td><td>{source.max_zoom}</td><td>{source.attribution}</td></tr>"

        info_text += "</table>"
        info_text += "<p><b>Note:</b> Usage of these tile sources is subject to their respective terms of service.</p>"

        QMessageBox.information(self, "Tile Sources", info_text)

    def closeEvent(self, event):
        """Handle window close event."""
        # Check if export is running
        if self.export_worker and self.export_worker.isRunning():
            reply = QMessageBox.question(
                self,
                "Export in Progress",
                "An export is currently running. Are you sure you want to quit?\n\n"
                "The export will be cancelled and progress will be lost.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply != QMessageBox.StandardButton.Yes:
                event.ignore()
                return

            # Cancel export
            self.export_worker.cancel()
            self.export_worker.wait()

        event.accept()
