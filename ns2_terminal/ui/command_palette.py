"""
NS2 Terminal – Command Palette
===============================
Ctrl+Shift+P floating overlay with fuzzy-search through available
commands. Glassmorphism styled, keyboard navigable.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit, QListWidget,
    QListWidgetItem, QGraphicsDropShadowEffect,
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor, QFont, QKeyEvent

from ns2_terminal.config_manager import config
from ns2_terminal.themes.theme_data import THEMES, DEFAULT_THEME


class CommandPalette(QWidget):
    """
    Floating command palette overlay.
    Shows a filtered list of available actions.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(500, 380)
        self.setObjectName("commandPalette")

        self._commands = []   # List of (name, callback) tuples
        self._visible = False

        # ── Layout ──
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)

        # ── Search input ──
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Type a command…")
        self.search_input.setObjectName("paletteSearch")
        self.search_input.textChanged.connect(self._filter_commands)
        self.search_input.installEventFilter(self)
        layout.addWidget(self.search_input)

        # ── Results list ──
        self.result_list = QListWidget()
        self.result_list.setObjectName("paletteResults")
        self.result_list.itemActivated.connect(self._execute_selected)
        self.result_list.itemClicked.connect(self._execute_selected)
        layout.addWidget(self.result_list)

        # ── Drop shadow ──
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(48)
        shadow.setOffset(0, 10)
        shadow.setColor(QColor(0, 0, 0, 140))
        self.setGraphicsEffect(shadow)

        # Apply theme
        config.theme_changed.connect(self._apply_style)
        self._apply_style()

    def _apply_style(self, _=None):
        theme = THEMES.get(config.theme, THEMES[DEFAULT_THEME])

        self.setStyleSheet(f"""
            #commandPalette {{
                background: {theme.sidebar_bg};
                border: 1px solid {theme.border_color};
                border-radius: 14px;
            }}

            #paletteSearch {{
                background: {theme.input_bg};
                color: {theme.foreground};
                border: 1px solid {theme.border_color};
                border-radius: 10px;
                padding: 10px 14px;
                font-size: 14px;
                font-family: 'Inter', 'Segoe UI', sans-serif;
            }}
            #paletteSearch:focus {{
                border: 1px solid {theme.primary};
            }}

            #paletteResults {{
                background: transparent;
                border: none;
                color: {theme.foreground};
                font-size: 13px;
                font-family: 'Inter', 'Segoe UI', sans-serif;
                outline: none;
            }}
            #paletteResults::item {{
                padding: 8px 14px;
                border-radius: 8px;
                margin: 1px 0;
            }}
            #paletteResults::item:hover {{
                background: rgba(255, 255, 255, 0.05);
            }}
            #paletteResults::item:selected {{
                background: rgba({self._qcolor_rgb(theme.primary)}, 0.14);
                color: {theme.primary};
            }}
        """)

    @staticmethod
    def _qcolor_rgb(hex_color: str) -> str:
        """Convert #RRGGBB to 'R, G, B' for rgba()."""
        c = QColor(hex_color)
        return f"{c.red()}, {c.green()}, {c.blue()}"

    def register_commands(self, commands: list):
        """Register available commands as (name, callback) tuples."""
        self._commands = commands
        self._populate_list(self._commands)

    def _populate_list(self, commands):
        self.result_list.clear()
        for name, _ in commands:
            item = QListWidgetItem(name)
            self.result_list.addItem(item)
        if self.result_list.count() > 0:
            self.result_list.setCurrentRow(0)

    def _filter_commands(self, text: str):
        query = text.lower().strip()
        if not query:
            self._populate_list(self._commands)
            return
        filtered = [
            (n, cb) for n, cb in self._commands
            if query in n.lower()
        ]
        self._populate_list(filtered)

    def _execute_selected(self, item=None):
        if item is None:
            item = self.result_list.currentItem()
        if item is None:
            return
        name = item.text()
        for cmd_name, callback in self._commands:
            if cmd_name == name:
                self.hide_palette()
                QTimer.singleShot(50, callback)
                return

    def toggle(self):
        """Show or hide the command palette."""
        if self._visible:
            self.hide_palette()
        else:
            self.show_palette()

    def show_palette(self):
        """Show and center the palette over the parent window."""
        self._visible = True
        parent = self.parent()
        if parent:
            # Center horizontally, position near top
            px = parent.mapToGlobal(parent.rect().center())
            self.move(px.x() - self.width() // 2, px.y() - 200)
        self.search_input.clear()
        self._populate_list(self._commands)
        self.show()
        self.raise_()
        self.search_input.setFocus()

    def hide_palette(self):
        self._visible = False
        self.hide()

    # ── Keyboard navigation ──────────────────────────────────────────────

    def eventFilter(self, obj, event):
        if obj == self.search_input and event.type() == event.Type.KeyPress:
            key = event.key()
            if key == Qt.Key.Key_Down:
                row = self.result_list.currentRow()
                if row < self.result_list.count() - 1:
                    self.result_list.setCurrentRow(row + 1)
                return True
            elif key == Qt.Key.Key_Up:
                row = self.result_list.currentRow()
                if row > 0:
                    self.result_list.setCurrentRow(row - 1)
                return True
            elif key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                self._execute_selected()
                return True
            elif key == Qt.Key.Key_Escape:
                self.hide_palette()
                return True
        return super().eventFilter(obj, event)

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Escape:
            self.hide_palette()
        else:
            super().keyPressEvent(event)
