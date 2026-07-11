"""
Application-wide dark theme (Qt stylesheet).

Applied once in main.py via app.setStyleSheet(STYLESHEET). Keeping it in one
place avoids each widget file hand-rolling its own colors.
"""

# Palette
BG = "#14161c"            # window background
PANEL = "#1c1f28"         # group box / menu background
SURFACE = "#242836"       # input fields, tables, text areas
BORDER = "#333849"
BORDER_LIGHT = "#414759"
TEXT = "#e6e8ef"
TEXT_MUTED = "#9aa2b8"
TEXT_DISABLED = "#565c6e"
ACCENT = "#4da6ff"
ACCENT_HOVER = "#6bb8ff"
ACCENT_PRESSED = "#3a8ee0"
ACCENT_TEXT = "#0b0d12"   # text on top of accent-colored backgrounds
SUCCESS = "#4ade80"
DANGER = "#f87171"
DANGER_HOVER = "#ff8a8a"

STYLESHEET = f"""
QWidget {{
    background-color: {BG};
    color: {TEXT};
    font-size: 10pt;
}}

QMainWindow, QDialog {{
    background-color: {BG};
}}

QGroupBox {{
    background-color: {PANEL};
    border: 1px solid {BORDER};
    border-radius: 8px;
    margin-top: 16px;
    padding-top: 12px;
    font-weight: 600;
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 12px;
    padding: 0 6px;
    color: {ACCENT};
}}

QPushButton {{
    background-color: #2a2f3d;
    border: 1px solid {BORDER_LIGHT};
    border-radius: 6px;
    padding: 6px 16px;
    color: {TEXT};
}}
QPushButton:hover {{
    background-color: #333a4d;
    border-color: {ACCENT};
}}
QPushButton:pressed {{
    background-color: #232734;
}}
QPushButton:disabled {{
    background-color: {PANEL};
    color: {TEXT_DISABLED};
    border-color: #2a2f3a;
}}

QPushButton#primaryButton {{
    background-color: {ACCENT};
    border: 1px solid {ACCENT};
    color: {ACCENT_TEXT};
    font-weight: 700;
}}
QPushButton#primaryButton:hover {{ background-color: {ACCENT_HOVER}; }}
QPushButton#primaryButton:pressed {{ background-color: {ACCENT_PRESSED}; }}
QPushButton#primaryButton:disabled {{
    background-color: #2a2f3a;
    color: {TEXT_DISABLED};
    border-color: #2a2f3a;
}}

QPushButton#dangerButton {{ color: {DANGER}; border-color: {DANGER}; }}
QPushButton#dangerButton:hover {{ color: {DANGER_HOVER}; border-color: {DANGER_HOVER}; background-color: #2a1f22; }}

QLabel {{ background-color: transparent; color: {TEXT}; }}

QLineEdit, QTextEdit, QTableWidget, QListWidget {{
    background-color: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 6px;
    color: {TEXT};
    selection-background-color: {ACCENT};
    selection-color: {ACCENT_TEXT};
    gridline-color: {BORDER};
}}
QLineEdit:focus, QTextEdit:focus {{ border: 1px solid {ACCENT}; }}
QLineEdit:disabled {{ color: {TEXT_DISABLED}; }}

QComboBox {{
    background-color: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 6px;
    padding: 4px 8px;
    color: {TEXT};
}}
QComboBox:hover {{ border-color: {ACCENT}; }}
QComboBox::drop-down {{ border: none; width: 22px; }}
QComboBox QAbstractItemView {{
    background-color: {SURFACE};
    border: 1px solid {BORDER};
    color: {TEXT};
    selection-background-color: {ACCENT};
    selection-color: {ACCENT_TEXT};
    outline: none;
}}

QSpinBox, QDoubleSpinBox {{
    background-color: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 6px;
    padding: 3px 6px;
    color: {TEXT};
}}
QSpinBox:hover, QDoubleSpinBox:hover {{ border-color: {ACCENT}; }}

QCheckBox {{ spacing: 8px; }}
QCheckBox::indicator {{
    width: 16px;
    height: 16px;
    border: 1px solid {BORDER_LIGHT};
    border-radius: 4px;
    background-color: {SURFACE};
}}
QCheckBox::indicator:checked {{
    background-color: {ACCENT};
    border-color: {ACCENT};
}}

QSlider::groove:horizontal {{
    height: 4px;
    background: {BORDER};
    border-radius: 2px;
}}
QSlider::handle:horizontal {{
    background: {ACCENT};
    width: 14px;
    margin: -6px 0;
    border-radius: 7px;
}}
QSlider::sub-page:horizontal {{
    background: {ACCENT};
    border-radius: 2px;
}}

QProgressBar {{
    background-color: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 6px;
    text-align: center;
    color: {TEXT};
    height: 18px;
}}
QProgressBar::chunk {{
    background-color: {ACCENT};
    border-radius: 5px;
}}

QTabWidget::pane {{
    border: 1px solid {BORDER};
    border-radius: 8px;
    top: -1px;
}}
QTabBar::tab {{
    background: {PANEL};
    border: 1px solid {BORDER};
    border-bottom: none;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    padding: 8px 18px;
    color: {TEXT_MUTED};
}}
QTabBar::tab:selected {{
    background: {SURFACE};
    color: {ACCENT};
    font-weight: 600;
}}
QTabBar::tab:hover {{ color: {TEXT}; }}

QMenuBar {{
    background-color: {BG};
    color: {TEXT};
    border-bottom: 1px solid {BORDER};
    padding: 2px;
}}
QMenuBar::item {{ background: transparent; padding: 4px 10px; border-radius: 4px; }}
QMenuBar::item:selected {{ background-color: {SURFACE}; }}
QMenu {{
    background-color: {PANEL};
    border: 1px solid {BORDER};
    color: {TEXT};
    padding: 4px;
}}
QMenu::item {{ padding: 6px 24px 6px 12px; border-radius: 4px; }}
QMenu::item:selected {{ background-color: {ACCENT}; color: {ACCENT_TEXT}; }}

QHeaderView::section {{
    background-color: {PANEL};
    color: {TEXT_MUTED};
    border: none;
    border-bottom: 1px solid {BORDER};
    padding: 6px;
}}

QScrollBar:vertical {{
    background: transparent;
    width: 12px;
    margin: 0;
}}
QScrollBar::handle:vertical {{
    background: {BORDER_LIGHT};
    border-radius: 5px;
    min-height: 24px;
    margin: 2px;
}}
QScrollBar::handle:vertical:hover {{ background: {ACCENT}; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{ background: none; }}

QScrollBar:horizontal {{
    background: transparent;
    height: 12px;
    margin: 0;
}}
QScrollBar::handle:horizontal {{
    background: {BORDER_LIGHT};
    border-radius: 5px;
    min-width: 24px;
    margin: 2px;
}}
QScrollBar::handle:horizontal:hover {{ background: {ACCENT}; }}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width: 0; }}
QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{ background: none; }}

QSplitter::handle {{ background-color: {BORDER}; }}
QSplitter::handle:horizontal {{ width: 3px; }}
QSplitter::handle:vertical {{ height: 3px; }}

QToolTip {{
    background-color: {SURFACE};
    color: {TEXT};
    border: 1px solid {ACCENT};
    padding: 4px 8px;
    border-radius: 4px;
}}

QMessageBox {{ background-color: {PANEL}; }}
"""
