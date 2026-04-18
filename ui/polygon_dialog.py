"""
Polygon definition dialog.

Provides four methods for defining export polygon:
1. Draw on Map - Click to add polygon vertices interactively
2. Manual Entry - Type coordinates into a table
3. Import from File - Load from GeoJSON or CSV
4. Preview - View polygon details
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QTableWidget, QTableWidgetItem, QPushButton, QLabel,
    QFileDialog, QMessageBox, QComboBox, QTextEdit, QHeaderView
)
from PyQt5.QtCore import Qt

from core.geometry import (
    validate_polygon, close_polygon, check_self_intersection,
    calculate_polygon_area
)
from utils.file_utils import (
    load_geojson, load_csv, detect_csv_columns, get_csv_preview
)
from .map_widget import InteractiveMapWidget


class PolygonDialog(QDialog):
    """Dialog for defining export polygon."""

    def __init__(self, parent=None, initial_coords=None, translator=None):
        super().__init__(parent)

        self.translator = translator
        self.coords = initial_coords if initial_coords else []

        title = translator.tr('dialog_polygon_title') if translator else "Define Export Polygon"
        self.setWindowTitle(title)
        self.setMinimumSize(900, 650)

        self.init_ui()

        # Load initial coordinates if provided
        if self.coords:
            self.load_coords_to_table(self.coords)
            self.map_widget.set_points(self.coords)

    def tr(self, key):
        """Get translated string or fallback to English."""
        if self.translator:
            return self.translator.tr(key)
        # Fallback to basic English
        fallbacks = {
            'tab_draw_map': '🗺️ Draw on Map',
            'tab_manual_entry': '✏️ Manual Entry',
            'tab_import_file': '📁 Import from File',
            'tab_preview': '👁️ Preview',
            'btn_validate': 'Validate',
            'btn_ok': 'OK',
            'btn_cancel': 'Cancel'
        }
        return fallbacks.get(key, key)

    def init_ui(self):
        """Initialize user interface."""
        layout = QVBoxLayout(self)

        # Tab widget for different input methods
        self.tabs = QTabWidget()

        # Tab 0: Interactive Map (Primary method)
        self.map_widget = InteractiveMapWidget(self.translator)
        self.map_widget.point_clicked.connect(self.on_map_point_added)
        self.tabs.addTab(self.map_widget, self.tr('tab_draw_map'))

        # Tab 1: Manual Entry
        self.manual_tab = self.create_manual_tab()
        self.tabs.addTab(self.manual_tab, self.tr('tab_manual_entry'))

        # Tab 2: Import from File
        self.import_tab = self.create_import_tab()
        self.tabs.addTab(self.import_tab, self.tr('tab_import_file'))

        # Tab 3: Preview
        self.preview_tab = self.create_preview_tab()
        self.tabs.addTab(self.preview_tab, self.tr('tab_preview'))

        # Connect tab changes to sync data
        self.tabs.currentChanged.connect(self.on_tab_changed)

        layout.addWidget(self.tabs)

        # Info label
        self.info_label = QLabel("")
        self.info_label.setStyleSheet("QLabel { color: #666; }")
        layout.addWidget(self.info_label)

        # Dialog buttons
        button_layout = QHBoxLayout()

        self.validate_btn = QPushButton(self.tr('btn_validate'))
        self.validate_btn.clicked.connect(self.on_validate_clicked)
        button_layout.addWidget(self.validate_btn)

        button_layout.addStretch()

        self.ok_btn = QPushButton(self.tr('btn_ok'))
        self.ok_btn.clicked.connect(self.on_ok_clicked)
        self.ok_btn.setEnabled(False)
        button_layout.addWidget(self.ok_btn)

        self.cancel_btn = QPushButton(self.tr('btn_cancel'))
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)

        layout.addLayout(button_layout)

    def create_manual_tab(self):
        """Create manual entry tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Instructions
        instructions = QLabel(
            "Enter polygon vertices as latitude and longitude coordinates.\n"
            "Polygon will be automatically closed (first vertex repeated at end)."
        )
        instructions.setWordWrap(True)
        layout.addWidget(instructions)

        # Table
        self.coords_table = QTableWidget()
        self.coords_table.setColumnCount(2)
        self.coords_table.setHorizontalHeaderLabels(["Latitude", "Longitude"])
        self.coords_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.coords_table)

        # Buttons
        button_layout = QHBoxLayout()

        add_row_btn = QPushButton("Add Row")
        add_row_btn.clicked.connect(self.on_add_row_clicked)
        button_layout.addWidget(add_row_btn)

        remove_row_btn = QPushButton("Remove Selected")
        remove_row_btn.clicked.connect(self.on_remove_row_clicked)
        button_layout.addWidget(remove_row_btn)

        clear_btn = QPushButton("Clear All")
        clear_btn.clicked.connect(self.on_clear_clicked)
        button_layout.addWidget(clear_btn)

        button_layout.addStretch()

        layout.addLayout(button_layout)

        return widget

    def create_import_tab(self):
        """Create import from file tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Instructions
        instructions = QLabel(
            "Import polygon coordinates from GeoJSON or CSV file.\n"
            "For CSV files, specify which columns contain latitude and longitude."
        )
        instructions.setWordWrap(True)
        layout.addWidget(instructions)

        # File selection
        file_layout = QHBoxLayout()

        file_layout.addWidget(QLabel("File:"))

        self.file_path_edit = QLabel("No file selected")
        self.file_path_edit.setStyleSheet("QLabel { color: #666; }")
        file_layout.addWidget(self.file_path_edit)

        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.on_browse_file_clicked)
        file_layout.addWidget(browse_btn)

        layout.addLayout(file_layout)

        # CSV column selection (initially hidden)
        self.csv_column_widget = QWidget()
        csv_column_layout = QHBoxLayout(self.csv_column_widget)

        csv_column_layout.addWidget(QLabel("Latitude Column:"))
        self.lat_column_combo = QComboBox()
        csv_column_layout.addWidget(self.lat_column_combo)

        csv_column_layout.addWidget(QLabel("Longitude Column:"))
        self.lon_column_combo = QComboBox()
        csv_column_layout.addWidget(self.lon_column_combo)

        csv_column_layout.addStretch()

        self.csv_column_widget.hide()
        layout.addWidget(self.csv_column_widget)

        # Preview
        layout.addWidget(QLabel("File Preview:"))

        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setMaximumHeight(200)
        layout.addWidget(self.preview_text)

        # Load button
        load_layout = QHBoxLayout()
        load_layout.addStretch()

        self.load_btn = QPushButton("Load Coordinates")
        self.load_btn.clicked.connect(self.on_load_file_clicked)
        self.load_btn.setEnabled(False)
        load_layout.addWidget(self.load_btn)

        layout.addLayout(load_layout)

        layout.addStretch()

        return widget

    def create_preview_tab(self):
        """Create preview tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Info
        info = QLabel(
            "Preview of defined polygon.\n"
            "Shows polygon area and vertex count."
        )
        info.setWordWrap(True)
        layout.addWidget(info)

        # Stats
        self.preview_stats_label = QLabel("No polygon defined")
        self.preview_stats_label.setStyleSheet("QLabel { font-weight: bold; }")
        layout.addWidget(self.preview_stats_label)

        # Map preview
        # Note: For a full implementation, you would embed a folium map here
        # using QWebEngineView. For simplicity, we'll show coordinates text.
        layout.addWidget(QLabel("Polygon Coordinates:"))

        self.preview_coords_text = QTextEdit()
        self.preview_coords_text.setReadOnly(True)
        layout.addWidget(self.preview_coords_text)

        # Refresh button
        refresh_layout = QHBoxLayout()
        refresh_layout.addStretch()

        refresh_btn = QPushButton("Refresh Preview")
        refresh_btn.clicked.connect(self.update_preview)
        refresh_layout.addWidget(refresh_btn)

        layout.addLayout(refresh_layout)

        return widget

    def on_map_point_added(self, lat, lon):
        """Handle point added from map widget."""
        # Add to table
        row = self.coords_table.rowCount()
        self.coords_table.insertRow(row)
        self.coords_table.setItem(row, 0, QTableWidgetItem(f"{lat:.8f}"))
        self.coords_table.setItem(row, 1, QTableWidgetItem(f"{lon:.8f}"))

        # Update info
        self.update_info_label(f"Added point {row + 1}: ({lat:.6f}, {lon:.6f})")

    def on_tab_changed(self, index):
        """Handle tab change - sync data between tabs."""
        # If switching away from manual entry, update map
        if index == 0:  # Switching to map tab
            coords = self.get_coords_from_table()
            if coords:
                self.map_widget.set_points(coords)

        # If switching away from map, update table
        if index == 1:  # Switching to manual entry
            map_coords = self.map_widget.get_points()
            if map_coords:
                self.load_coords_to_table(map_coords)

    def on_add_row_clicked(self):
        """Add a new row to coordinates table."""
        row = self.coords_table.rowCount()
        self.coords_table.insertRow(row)

    def on_remove_row_clicked(self):
        """Remove selected rows from coordinates table."""
        selected_rows = set(index.row() for index in self.coords_table.selectedIndexes())

        for row in sorted(selected_rows, reverse=True):
            self.coords_table.removeRow(row)

    def on_clear_clicked(self):
        """Clear all rows from coordinates table."""
        self.coords_table.setRowCount(0)

    def on_browse_file_clicked(self):
        """Browse for file to import."""
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Select Polygon File",
            "",
            "GeoJSON Files (*.geojson *.json);;CSV Files (*.csv);;All Files (*)"
        )

        if filename:
            self.file_path_edit.setText(filename)
            self.load_btn.setEnabled(True)

            # Check if CSV
            if filename.lower().endswith('.csv'):
                # Detect columns
                success, columns, message = detect_csv_columns(filename)

                if success:
                    self.lat_column_combo.clear()
                    self.lon_column_combo.clear()
                    self.lat_column_combo.addItems(columns)
                    self.lon_column_combo.addItems(columns)

                    # Try to auto-select lat/lon columns
                    for i, col in enumerate(columns):
                        col_lower = col.lower()
                        if 'lat' in col_lower and 'lon' not in col_lower:
                            self.lat_column_combo.setCurrentIndex(i)
                        if 'lon' in col_lower or 'lng' in col_lower:
                            self.lon_column_combo.setCurrentIndex(i)

                    self.csv_column_widget.show()

                    # Show preview
                    success, rows, message = get_csv_preview(filename, max_rows=5)
                    if success:
                        preview_text = f"Preview (first {len(rows)} rows):\n\n"
                        for row in rows:
                            preview_text += str(row) + "\n"
                        self.preview_text.setText(preview_text)
                else:
                    QMessageBox.warning(self, "Error", message)

            else:
                # Hide CSV column selection for non-CSV files
                self.csv_column_widget.hide()
                self.preview_text.setText("GeoJSON file selected. Click 'Load Coordinates' to import.")

    def on_load_file_clicked(self):
        """Load coordinates from selected file."""
        filename = self.file_path_edit.text()

        if not filename or filename == "No file selected":
            return

        # Load based on file type
        if filename.lower().endswith('.csv'):
            lat_col = self.lat_column_combo.currentText()
            lon_col = self.lon_column_combo.currentText()

            success, coords, message = load_csv(filename, lat_col, lon_col)
        else:
            success, coords, message = load_geojson(filename)

        if success:
            self.coords = coords
            self.load_coords_to_table(coords)
            self.update_info_label(f"Loaded {len(coords)} vertices from file")
            QMessageBox.information(self, "Success", message)
        else:
            QMessageBox.warning(self, "Error", message)

    def load_coords_to_table(self, coords):
        """
        Load coordinates into table.

        Args:
            coords: List of (lat, lon) tuples
        """
        self.coords_table.setRowCount(len(coords))

        for i, (lat, lon) in enumerate(coords):
            self.coords_table.setItem(i, 0, QTableWidgetItem(str(lat)))
            self.coords_table.setItem(i, 1, QTableWidgetItem(str(lon)))

    def get_coords_from_table(self):
        """
        Get coordinates from table.

        Returns:
            List of (lat, lon) tuples or None if invalid
        """
        coords = []

        for i in range(self.coords_table.rowCount()):
            lat_item = self.coords_table.item(i, 0)
            lon_item = self.coords_table.item(i, 1)

            if not lat_item or not lon_item:
                QMessageBox.warning(self, "Error", f"Empty cell at row {i + 1}")
                return None

            try:
                lat = float(lat_item.text().strip())
                lon = float(lon_item.text().strip())
                coords.append((lat, lon))
            except ValueError:
                QMessageBox.warning(self, "Error", f"Invalid number at row {i + 1}")
                return None

        return coords

    def on_validate_clicked(self):
        """Validate polygon coordinates."""
        # Get coordinates from current active tab
        current_tab = self.tabs.currentIndex()

        if current_tab == 0:  # Map tab
            coords = self.map_widget.get_points()
        else:
            coords = self.get_coords_from_table()

        if not coords:
            QMessageBox.warning(self, "No Coordinates", "Please add at least 3 points to define a polygon.")
            return

        # Validate
        is_valid, message = validate_polygon(coords)

        if not is_valid:
            QMessageBox.warning(self, "Invalid Polygon", message)
            self.ok_btn.setEnabled(False)
            return

        # Check self-intersection
        has_intersection, message = check_self_intersection(coords)

        if has_intersection:
            QMessageBox.warning(self, "Self-Intersection", message)
            self.ok_btn.setEnabled(False)
            return

        # Close polygon if needed
        closed_coords = close_polygon(coords)

        # Calculate area
        area_km2 = calculate_polygon_area(coords)

        self.coords = closed_coords
        self.ok_btn.setEnabled(True)
        self.update_info_label(
            f"Valid polygon: {len(coords)} vertices, area: {area_km2:.2f} km²"
        )

        QMessageBox.information(
            self,
            "Validation Success",
            f"Polygon is valid!\n\nVertices: {len(coords)}\nArea: {area_km2:.2f} km²"
        )

        # Update preview
        self.update_preview()

    def update_preview(self):
        """Update preview tab with current polygon."""
        if not self.coords:
            coords = self.get_coords_from_table()
            if not coords:
                return
            self.coords = coords

        # Update stats
        area_km2 = calculate_polygon_area(self.coords)
        self.preview_stats_label.setText(
            f"Vertices: {len(self.coords)} | Area: {area_km2:.2f} km²"
        )

        # Update coordinates text
        coords_text = ""
        for i, (lat, lon) in enumerate(self.coords, 1):
            coords_text += f"{i}. ({lat:.6f}, {lon:.6f})\n"

        self.preview_coords_text.setText(coords_text)

    def update_info_label(self, text):
        """Update info label at bottom of dialog."""
        self.info_label.setText(text)

    def on_ok_clicked(self):
        """Handle OK button click."""
        # Get final coordinates
        if not self.coords:
            # Try to get from current tab
            current_tab = self.tabs.currentIndex()

            if current_tab == 0:  # Map tab
                coords = self.map_widget.get_points()
            else:
                coords = self.get_coords_from_table()

            if not coords:
                QMessageBox.warning(self, "No Coordinates", "Please add at least 3 points to define a polygon.")
                return

            # Validate
            is_valid, message = validate_polygon(coords)
            if not is_valid:
                QMessageBox.warning(self, "Invalid Polygon", message)
                return

            # Close polygon
            self.coords = close_polygon(coords)

        self.accept()

    def get_coordinates(self):
        """
        Get polygon coordinates.

        Returns:
            List of (lat, lon) tuples
        """
        return self.coords
