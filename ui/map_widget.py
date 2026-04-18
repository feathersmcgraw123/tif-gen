"""
Interactive map widget for polygon definition.

Allows users to click on a map to define polygon vertices.
Uses Leaflet.js with OpenStreetMap tiles.
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl, pyqtSignal, pyqtSlot
from PyQt5.QtWebChannel import QWebChannel
import json


class MapBridge(QWidget):
    """Bridge between JavaScript and Python for map interactions."""

    # Signal emitted when a point is added to the map
    point_added = pyqtSignal(float, float)  # lat, lon

    def __init__(self):
        super().__init__()

    @pyqtSlot(float, float)
    def addPoint(self, lat, lon):
        """Called from JavaScript when user clicks on map."""
        self.point_added.emit(lat, lon)


class InteractiveMapWidget(QWidget):
    """Interactive map widget for defining polygons by clicking."""

    # Signal emitted when a point is added
    point_clicked = pyqtSignal(float, float)

    def __init__(self, translator=None, parent=None):
        super().__init__(parent)

        self.translator = translator
        self.points = []
        self.init_ui()

    def tr(self, key):
        """Get translated string or fallback to English."""
        if self.translator:
            return self.translator.tr(key)
        # Fallback to basic English
        fallbacks = {
            'map_instructions': 'Click on the map to add polygon vertices. Points will appear in order. Use the buttons below to manage points.',
            'btn_undo_point': 'Undo Last Point',
            'btn_clear_all': 'Clear All',
            'btn_reset_view': 'Reset View',
            'label_points': 'Points: {0}'
        }
        return fallbacks.get(key, key)

    def init_ui(self):
        """Initialize user interface."""
        layout = QVBoxLayout(self)

        # Instructions
        instructions = QLabel(self.tr('map_instructions'))
        instructions.setWordWrap(True)
        layout.addWidget(instructions)

        # Web view for map
        self.web_view = QWebEngineView()
        self.web_view.setMinimumHeight(400)
        layout.addWidget(self.web_view)

        # Setup web channel for JavaScript communication
        self.bridge = MapBridge()
        self.bridge.point_added.connect(self.on_point_added)

        self.channel = QWebChannel()
        self.channel.registerObject('bridge', self.bridge)
        self.web_view.page().setWebChannel(self.channel)

        # Control buttons
        button_layout = QHBoxLayout()

        self.undo_btn = QPushButton(self.tr('btn_undo_point'))
        self.undo_btn.clicked.connect(self.undo_last_point)
        self.undo_btn.setEnabled(False)
        button_layout.addWidget(self.undo_btn)

        self.clear_btn = QPushButton(self.tr('btn_clear_all'))
        self.clear_btn.clicked.connect(self.clear_all_points)
        self.clear_btn.setEnabled(False)
        button_layout.addWidget(self.clear_btn)

        self.center_btn = QPushButton(self.tr('btn_reset_view'))
        self.center_btn.clicked.connect(self.reset_view)
        button_layout.addWidget(self.center_btn)

        button_layout.addStretch()

        self.point_count_label = QLabel(self.tr('label_points').format(0))
        button_layout.addWidget(self.point_count_label)

        layout.addLayout(button_layout)

        # Load map
        self.load_map()

    def load_map(self):
        """Load the interactive map with Leaflet.js."""
        html = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <script src="qrc:///qtwebchannel/qwebchannel.js"></script>
    <style>
        body { margin: 0; padding: 0; }
        #map { width: 100%; height: 100vh; }
        .vertex-marker {
            background-color: #ff4444;
            border: 2px solid white;
            border-radius: 50%;
            width: 12px;
            height: 12px;
        }
        .vertex-label {
            background-color: white;
            border: 1px solid #333;
            border-radius: 3px;
            padding: 2px 5px;
            font-size: 11px;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div id="map"></div>
    <script>
        // Initialize map centered on world
        var map = L.map('map').setView([20, 0], 2);

        // Add OpenStreetMap tiles
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors',
            maxZoom: 19
        }).addTo(map);

        // Store markers and polygon
        var markers = [];
        var polygon = null;
        var bridge = null;

        // Setup Qt WebChannel
        new QWebChannel(qt.webChannelTransport, function(channel) {
            bridge = channel.objects.bridge;
        });

        // Handle map clicks
        map.on('click', function(e) {
            if (bridge) {
                bridge.addPoint(e.latlng.lat, e.latlng.lng);
            }
        });

        // Add a vertex marker
        function addVertex(lat, lng, index) {
            // Create marker
            var marker = L.circleMarker([lat, lng], {
                radius: 6,
                fillColor: '#ff4444',
                color: '#ffffff',
                weight: 2,
                opacity: 1,
                fillOpacity: 1
            }).addTo(map);

            // Add number label
            var label = L.tooltip({
                permanent: true,
                direction: 'top',
                className: 'vertex-label',
                offset: [0, -10]
            }).setContent((index + 1).toString());

            marker.bindTooltip(label);
            marker.openTooltip();

            markers.push(marker);

            updatePolygon();
        }

        // Update polygon shape
        function updatePolygon() {
            // Remove old polygon
            if (polygon) {
                map.removeLayer(polygon);
            }

            // Create new polygon if we have enough points
            if (markers.length >= 2) {
                var latlngs = markers.map(m => m.getLatLng());
                polygon = L.polygon(latlngs, {
                    color: '#3388ff',
                    weight: 2,
                    fillOpacity: 0.2
                }).addTo(map);
            }
        }

        // Remove last vertex
        function undoLastVertex() {
            if (markers.length > 0) {
                var marker = markers.pop();
                map.removeLayer(marker);
                updatePolygon();
            }
        }

        // Clear all vertices
        function clearAllVertices() {
            markers.forEach(m => map.removeLayer(m));
            markers = [];
            if (polygon) {
                map.removeLayer(polygon);
                polygon = null;
            }
        }

        // Set vertices from external source
        function setVertices(coords) {
            clearAllVertices();
            coords.forEach((coord, index) => {
                var marker = L.circleMarker([coord[0], coord[1]], {
                    radius: 6,
                    fillColor: '#ff4444',
                    color: '#ffffff',
                    weight: 2,
                    opacity: 1,
                    fillOpacity: 1
                }).addTo(map);

                var label = L.tooltip({
                    permanent: true,
                    direction: 'top',
                    className: 'vertex-label',
                    offset: [0, -10]
                }).setContent((index + 1).toString());

                marker.bindTooltip(label);
                marker.openTooltip();

                markers.push(marker);
            });

            updatePolygon();

            // Zoom to fit all markers
            if (markers.length > 0) {
                var group = L.featureGroup(markers);
                map.fitBounds(group.getBounds().pad(0.1));
            }
        }

        // Reset view to world
        function resetView() {
            map.setView([20, 0], 2);
        }
    </script>
</body>
</html>
        '''

        self.web_view.setHtml(html)

    def on_point_added(self, lat, lon):
        """Handle point added from map."""
        self.points.append((lat, lon))
        self.point_clicked.emit(lat, lon)
        self.update_ui_state()

        # Add marker to map
        self.web_view.page().runJavaScript(
            f"addVertex({lat}, {lon}, {len(self.points) - 1});"
        )

    def undo_last_point(self):
        """Remove the last point."""
        if self.points:
            self.points.pop()
            self.update_ui_state()
            self.web_view.page().runJavaScript("undoLastVertex();")

    def clear_all_points(self):
        """Clear all points."""
        self.points = []
        self.update_ui_state()
        self.web_view.page().runJavaScript("clearAllVertices();")

    def reset_view(self):
        """Reset map view to world."""
        self.web_view.page().runJavaScript("resetView();")

    def update_ui_state(self):
        """Update button states based on points."""
        has_points = len(self.points) > 0
        self.undo_btn.setEnabled(has_points)
        self.clear_btn.setEnabled(has_points)
        self.point_count_label.setText(self.tr('label_points').format(len(self.points)))

    def set_points(self, coords):
        """
        Set points from external source (e.g., loaded from file).

        Args:
            coords: List of (lat, lon) tuples
        """
        self.points = list(coords)
        self.update_ui_state()

        # Convert to JavaScript array format
        coords_js = json.dumps(coords)
        self.web_view.page().runJavaScript(f"setVertices({coords_js});")

    def get_points(self):
        """
        Get current points.

        Returns:
            List of (lat, lon) tuples
        """
        return self.points.copy()
