"""
Export configuration widget.

Provides UI controls for configuring export settings:
- Resolution
- Tile source selection
- Compression type and quality
- Output CRS
- Output file path
- Render delay
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel,
    QDoubleSpinBox, QSpinBox, QComboBox, QSlider, QLineEdit,
    QPushButton, QFileDialog, QGroupBox, QCheckBox
)
from PyQt5.QtCore import Qt, pyqtSignal

from core.geometry import estimate_file_size, format_file_size, calculate_bbox, calculate_output_dimensions, coords_4326_to_3857
from core.tile_sources import get_available_sources
from core.tile_downloader import calculate_zoom_level, meters_per_pixel_at_zoom


class ConfigWidget(QWidget):
    """Widget for export configuration."""

    # Signal emitted when configuration changes
    config_changed = pyqtSignal()

    def __init__(self, translator=None, parent=None):
        super().__init__(parent)

        self.translator = translator
        self.polygon_coords = None  # Will be set by main window
        self.init_ui()

    def refresh_ui(self):
        """Refresh UI text after language change."""
        if not self.translator:
            return

        # Update quality preset labels
        self.quality_preset_combo.setItemText(0, self.translator.tr('quality_low'))
        self.quality_preset_combo.setItemText(1, self.translator.tr('quality_medium'))
        self.quality_preset_combo.setItemText(2, self.translator.tr('quality_high'))

        # Update checkbox and labels
        self.advanced_resolution_check.setText(self.translator.tr('advanced_mode'))
        self.resolution_label.setText(self.translator.tr('label_resolution'))
        self.zoom_label.setText(self.translator.tr('label_zoom_level'))

    def init_ui(self):
        """Initialize user interface."""
        layout = QVBoxLayout(self)

        # Resolution settings
        resolution_group = QGroupBox("Resolution")
        resolution_layout = QFormLayout()

        # Preset quality selector
        self.quality_preset_combo = QComboBox()
        quality_low = self.translator.tr('quality_low') if self.translator else "Low (Zoom 17, ~2.4 m/px)"
        quality_medium = self.translator.tr('quality_medium') if self.translator else "Medium (Zoom 18, ~1.2 m/px)"
        quality_high = self.translator.tr('quality_high') if self.translator else "High (Zoom 19, ~0.6 m/px)"
        self.quality_preset_combo.addItem(quality_low, 17)
        self.quality_preset_combo.addItem(quality_medium, 18)
        self.quality_preset_combo.addItem(quality_high, 19)
        self.quality_preset_combo.setCurrentIndex(1)  # Default to Medium
        self.quality_preset_combo.currentIndexChanged.connect(self.on_config_changed)

        quality_label_text = self.translator.tr('label_quality') if self.translator else "Quality:"
        resolution_layout.addRow(quality_label_text, self.quality_preset_combo)

        # Advanced mode checkbox
        advanced_text = self.translator.tr('advanced_mode') if self.translator else "Advanced mode"
        self.advanced_resolution_check = QCheckBox(advanced_text)
        self.advanced_resolution_check.stateChanged.connect(self.on_advanced_resolution_toggled)
        resolution_layout.addRow("", self.advanced_resolution_check)

        # Advanced resolution controls (initially hidden)
        self.resolution_spin = QDoubleSpinBox()
        self.resolution_spin.setRange(0.1, 10.0)
        self.resolution_spin.setValue(0.6)
        self.resolution_spin.setDecimals(2)
        self.resolution_spin.setSuffix(" m/px")
        self.resolution_spin.valueChanged.connect(self.on_config_changed)
        self.resolution_spin.setVisible(False)

        resolution_label_text = self.translator.tr('label_resolution') if self.translator else "Resolution:"
        self.resolution_label = QLabel(resolution_label_text)
        self.resolution_label.setVisible(False)
        resolution_layout.addRow(self.resolution_label, self.resolution_spin)

        # Zoom level control (alternative advanced option)
        self.zoom_spin = QSpinBox()
        self.zoom_spin.setRange(0, 20)
        self.zoom_spin.setValue(18)  # Default to Medium
        self.zoom_spin.valueChanged.connect(self.on_zoom_changed)
        self.zoom_spin.setVisible(False)

        zoom_label_text = self.translator.tr('label_zoom_level') if self.translator else "Zoom Level:"
        self.zoom_label = QLabel(zoom_label_text)
        self.zoom_label.setVisible(False)
        resolution_layout.addRow(self.zoom_label, self.zoom_spin)

        self.tile_size_spin = QSpinBox()
        self.tile_size_spin.setRange(256, 8192)
        self.tile_size_spin.setValue(2048)
        self.tile_size_spin.setSingleStep(256)
        self.tile_size_spin.setSuffix(" px")
        self.tile_size_spin.valueChanged.connect(self.on_config_changed)
        resolution_layout.addRow("Tile Size:", self.tile_size_spin)

        resolution_group.setLayout(resolution_layout)
        layout.addWidget(resolution_group)

        # Compression settings
        compression_group = QGroupBox("Compression")
        compression_layout = QFormLayout()

        self.compression_combo = QComboBox()
        self.compression_combo.addItems(['LZW', 'JPEG'])
        self.compression_combo.currentTextChanged.connect(self.on_compression_changed)
        compression_layout.addRow("Type:", self.compression_combo)

        self.quality_label = QLabel("JPEG Quality:")
        self.quality_slider = QSlider(Qt.Orientation.Horizontal)
        self.quality_slider.setRange(1, 100)
        self.quality_slider.setValue(90)
        self.quality_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.quality_slider.setTickInterval(10)
        self.quality_value_label = QLabel("90")
        self.quality_slider.valueChanged.connect(self.on_quality_changed)

        quality_layout = QHBoxLayout()
        quality_layout.addWidget(self.quality_slider)
        quality_layout.addWidget(self.quality_value_label)

        compression_layout.addRow(self.quality_label, quality_layout)

        # Initially hide JPEG quality (LZW is default)
        self.quality_label.hide()
        self.quality_slider.hide()
        self.quality_value_label.hide()

        compression_group.setLayout(compression_layout)
        layout.addWidget(compression_group)

        # Output settings
        output_group = QGroupBox("Output")
        output_layout = QFormLayout()

        self.crs_combo = QComboBox()
        self.crs_combo.addItems(['EPSG:4326 (WGS84)', 'EPSG:3857 (Web Mercator)'])
        self.crs_combo.currentTextChanged.connect(self.on_config_changed)
        output_layout.addRow("CRS:", self.crs_combo)

        self.tile_source_combo = QComboBox()
        self._populate_tile_sources()
        self.tile_source_combo.currentTextChanged.connect(self.on_config_changed)
        output_layout.addRow("Tile Source:", self.tile_source_combo)

        # Output file path
        path_layout = QHBoxLayout()
        self.output_path_edit = QLineEdit()
        self.output_path_edit.setPlaceholderText("Select output file path...")
        self.output_path_edit.textChanged.connect(self.on_config_changed)

        self.browse_btn = QPushButton("Browse...")
        self.browse_btn.clicked.connect(self.on_browse_clicked)

        path_layout.addWidget(self.output_path_edit)
        path_layout.addWidget(self.browse_btn)

        output_layout.addRow("Output File:", path_layout)

        output_group.setLayout(output_layout)
        layout.addWidget(output_group)

        # Advanced settings
        advanced_group = QGroupBox("Advanced")
        advanced_layout = QFormLayout()

        self.render_delay_spin = QDoubleSpinBox()
        self.render_delay_spin.setRange(0.0, 5.0)
        self.render_delay_spin.setValue(0.3)  # Increased from 0.2 to reduce rate limiting
        self.render_delay_spin.setDecimals(2)
        self.render_delay_spin.setSuffix(" s")
        self.render_delay_spin.setSingleStep(0.1)

        delay_label = QLabel("Render Delay:")
        delay_label.setToolTip(
            "Delay between tile downloads.\n"
            "Higher values (0.3-0.5s) reduce rate limiting from tile servers.\n"
            "Lower values speed up downloads but may cause failures."
        )
        advanced_layout.addRow(delay_label, self.render_delay_spin)

        advanced_group.setLayout(advanced_layout)
        layout.addWidget(advanced_group)

        # Estimated size
        self.size_label = QLabel("Estimated Size: Not calculated")
        self.size_label.setStyleSheet("QLabel { color: #666; font-style: italic; }")
        layout.addWidget(self.size_label)

        layout.addStretch()

    def on_compression_changed(self, compression: str):
        """Handle compression type change."""
        # Show/hide JPEG quality slider
        is_jpeg = compression == 'JPEG'
        self.quality_label.setVisible(is_jpeg)
        self.quality_slider.setVisible(is_jpeg)
        self.quality_value_label.setVisible(is_jpeg)

        self.on_config_changed()

    def on_quality_changed(self, value: int):
        """Handle JPEG quality slider change."""
        self.quality_value_label.setText(str(value))
        self.on_config_changed()

    def on_advanced_resolution_toggled(self, state):
        """Handle advanced resolution mode toggle."""
        is_advanced = (state == Qt.Checked)

        # Hide/show controls based on mode
        self.quality_preset_combo.setVisible(not is_advanced)
        self.resolution_label.setVisible(is_advanced)
        self.resolution_spin.setVisible(is_advanced)
        self.zoom_label.setVisible(is_advanced)
        self.zoom_spin.setVisible(is_advanced)

        # Sync values when switching to advanced mode
        if is_advanced:
            # Get zoom level from current preset
            preset_zoom = self.quality_preset_combo.currentData()
            self.zoom_spin.setValue(preset_zoom)
            # Update resolution based on zoom
            self.update_resolution_from_zoom()

        self.on_config_changed()

    def on_zoom_changed(self, zoom: int):
        """Handle zoom level change in advanced mode."""
        self.update_resolution_from_zoom()
        self.on_config_changed()

    def update_resolution_from_zoom(self):
        """Update resolution spin box based on zoom level."""
        # Calculate approximate resolution at equator for this zoom
        # At zoom 0, resolution is ~156543 m/px at equator
        # Each zoom level halves the resolution
        zoom = self.zoom_spin.value()
        equator_mpp = 156543.03392
        mpp = equator_mpp / (2 ** zoom)
        self.resolution_spin.setValue(mpp)

    def on_browse_clicked(self):
        """Handle browse button click."""
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Select Output File",
            "",
            "GeoTIFF Files (*.tif *.tiff);;All Files (*)"
        )

        if filename:
            # Ensure .tif extension
            if not filename.lower().endswith(('.tif', '.tiff')):
                filename += '.tif'

            self.output_path_edit.setText(filename)

    def on_config_changed(self):
        """Handle configuration change."""
        self.update_estimated_size()
        self.config_changed.emit()

    def _populate_tile_sources(self):
        """Populate tile source combo box with available sources."""
        sources = get_available_sources()

        for source_id, source in sources.items():
            self.tile_source_combo.addItem(source.name, source_id)

    def set_polygon_coords(self, coords):
        """
        Set polygon coordinates for size estimation.

        Args:
            coords: List of (lat, lon) tuples
        """
        self.polygon_coords = coords
        self.update_estimated_size()

    def update_estimated_size(self):
        """Update estimated file size label."""
        if not self.polygon_coords:
            self.size_label.setText("Estimated Size: Not calculated (no polygon defined)")
            return

        try:
            # Get zoom level (either from preset or advanced mode)
            zoom = self.get_zoom_level()

            # Calculate actual meters per pixel at center of polygon
            center_lat = sum(c[0] for c in self.polygon_coords) / len(self.polygon_coords)
            actual_mpp = meters_per_pixel_at_zoom(zoom, center_lat)

            # Calculate tile count (tiles are 256x256 px)
            from core.tile_downloader import get_tile_bbox_for_polygon
            min_tile_x, min_tile_y, max_tile_x, max_tile_y = get_tile_bbox_for_polygon(
                self.polygon_coords, zoom
            )

            tiles_x = max_tile_x - min_tile_x + 1
            tiles_y = max_tile_y - min_tile_y + 1
            total_tiles = tiles_x * tiles_y

            # Calculate output dimensions (256px per tile)
            TILE_SIZE = 256
            total_width = tiles_x * TILE_SIZE
            total_height = tiles_y * TILE_SIZE

            # Estimate file size
            compression = self.get_compression()
            jpeg_quality = self.get_jpeg_quality()
            raw_size, compressed_size = estimate_file_size(
                total_width, total_height, compression, jpeg_quality
            )

            # Update label
            self.size_label.setText(
                f"Estimated Size: {format_file_size(compressed_size)} "
                f"({total_width}x{total_height} px, {total_tiles} tiles, zoom {zoom}, ≈{actual_mpp:.2f} m/px)"
            )

        except Exception as e:
            self.size_label.setText(f"Estimated Size: Error calculating ({str(e)})")

    def get_resolution(self) -> float:
        """Get resolution in meters per pixel."""
        return self.resolution_spin.value()

    def get_zoom_level(self) -> int:
        """
        Get zoom level based on current mode.

        Returns:
            Zoom level (0-20)
        """
        if self.advanced_resolution_check.isChecked():
            # Advanced mode - use manual zoom level
            return self.zoom_spin.value()
        else:
            # Preset mode - use selected preset zoom
            return self.quality_preset_combo.currentData()

    def is_advanced_mode(self) -> bool:
        """Check if advanced resolution mode is enabled."""
        return self.advanced_resolution_check.isChecked()

    def get_compression(self) -> str:
        """Get compression type."""
        return self.compression_combo.currentText()

    def get_jpeg_quality(self) -> int:
        """Get JPEG quality (1-100)."""
        return self.quality_slider.value()

    def get_output_crs(self) -> str:
        """Get output CRS (EPSG:4326 or EPSG:3857)."""
        text = self.crs_combo.currentText()
        if '4326' in text:
            return 'EPSG:4326'
        else:
            return 'EPSG:3857'

    def get_tile_source_id(self) -> str:
        """Get selected tile source ID."""
        return self.tile_source_combo.currentData()

    def get_output_path(self) -> str:
        """Get output file path."""
        return self.output_path_edit.text()

    def get_render_delay(self) -> float:
        """Get render delay in seconds."""
        return self.render_delay_spin.value()

    def is_valid(self) -> tuple:
        """
        Check if configuration is valid.

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check output path
        output_path = self.get_output_path()
        if not output_path:
            return False, "Output file path is required"

        # Check tile source selection
        tile_source_id = self.get_tile_source_id()
        if not tile_source_id:
            return False, "No tile source selected"

        return True, ""
