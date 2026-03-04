"""
NS2 Terminal – Sidebar
=======================
Collapsible quick-actions panel with glassmorphism styling,
smooth slide animation, and icon-only collapsed mode.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel, QFrame, QSizePolicy,
)
from PyQt6.QtCore import (
    Qt, QPropertyAnimation, QEasingCurve, QSize, pyqtProperty,
)
from PyQt6.QtGui import QColor, QFont

from ns2_terminal.config_manager import config
from ns2_terminal.themes.theme_data import THEMES, DEFAULT_THEME


class SidebarButton(QPushButton):
    """Styled sidebar action button with icon and label."""

    def __init__(self, icon_char: str, label: str, parent=None):
        super().__init__(parent)
        self._icon_char = icon_char
        self._label_text = label
        self.setText(f"  {icon_char}   {label}")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(38)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

    def set_collapsed(self, collapsed: bool):
        if collapsed:
            self.setText(self._icon_char)
            self.setFixedWidth(42)
        else:
            self.setText(f"  {self._icon_char}   {self._label_text}")
            self.setMaximumWidth(16777215)  # Reset max width


class Sidebar(QWidget):
    """Glassmorphism sidebar with quick actions."""

    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self._main_window = main_window
        self._expanded = True
        self._target_width = 180
        self._collapsed_width = 50

        self.setFixedWidth(self._target_width)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 14, 10, 12)
        layout.setSpacing(6)

        # ── Logo / branding ──
        self.brand_label = QLabel("NS2")
        self.brand_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.brand_label.setFont(QFont("Inter", 14, QFont.Weight.Bold))
        layout.addWidget(self.brand_label)

        layout.addSpacing(12)

        # ── Separator ──
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background: rgba(255, 255, 255, 0.06); max-height: 1px;")
        layout.addWidget(sep)
        layout.addSpacing(8)

        # ── Action buttons ──
        self.btn_new_tab = SidebarButton("⊕", "New Tab")
        self.btn_split_h = SidebarButton("⬌", "Split H")
        self.btn_split_v = SidebarButton("⬍", "Split V")
        self.btn_palette = SidebarButton("⌘", "Commands")
        self.btn_settings = SidebarButton("⚙", "Settings")
        self.btn_theme = SidebarButton("◐", "Theme")
        self.btn_fullscreen = SidebarButton("⛶", "Fullscreen")

        self.buttons = [
            self.btn_new_tab, self.btn_split_h, self.btn_split_v,
            self.btn_palette, self.btn_settings, self.btn_theme,
            self.btn_fullscreen,
        ]

        for btn in self.buttons:
            layout.addWidget(btn)

        layout.addStretch()

        # ── Collapse toggle ──
        self.btn_collapse = QPushButton("◀")
        self.btn_collapse.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_collapse.setFixedHeight(32)
        self.btn_collapse.clicked.connect(self.toggle_collapse)
        layout.addWidget(self.btn_collapse)

        # Apply initial theme
        config.theme_changed.connect(self._apply_style)
        self._apply_style()

    def _apply_style(self, _=None):
        theme = THEMES.get(config.theme, THEMES[DEFAULT_THEME])

        self.setStyleSheet(f"""
            Sidebar {{
                background: {theme.sidebar_bg};
                border-right: 1px solid {theme.border_color};
            }}
        """)

        btn_style = f"""
            QPushButton {{
                background: transparent;
                color: {theme.foreground};
                border: none;
                border-radius: 6px;
                font-size: 12px;
                text-align: left;
                padding: 0 10px;
                font-family: 'Inter', 'Segoe UI', sans-serif;
            }}
            QPushButton:hover {{
                background: rgba(255, 255, 255, 0.06);
                color: {theme.foreground};
            }}
            QPushButton:pressed {{
                background: rgba(255, 255, 255, 0.09);
            }}
        """
        for btn in self.buttons:
            btn.setStyleSheet(btn_style)

        self.btn_collapse.setStyleSheet(f"""
            QPushButton {{
                background: rgba(255, 255, 255, 0.04);
                color: {theme.foreground};
                border: none;
                border-radius: 6px;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background: rgba(255, 255, 255, 0.08);
                color: {theme.foreground};
            }}
        """)

        self.brand_label.setStyleSheet(f"""
            color: {theme.primary};
            letter-spacing: 4px;
        """)

    def toggle_collapse(self):
        """Toggle between expanded and collapsed sidebar states."""
        if self._expanded:
            self._collapse()
        else:
            self._expand()

    def _collapse(self):
        self._expanded = False
        if config.animations_enabled:
            anim = QPropertyAnimation(self, b"maximumWidth")
            anim.setDuration(200)
            anim.setStartValue(self.width())
            anim.setEndValue(self._collapsed_width)
            anim.setEasingCurve(QEasingCurve.Type.OutCubic)
            anim.finished.connect(self._update_collapsed_state)
            anim.start()
            self._current_anim = anim  # prevent GC
        else:
            self.setFixedWidth(self._collapsed_width)
            self._update_collapsed_state()

    def _expand(self):
        self._expanded = True
        if config.animations_enabled:
            anim = QPropertyAnimation(self, b"maximumWidth")
            anim.setDuration(200)
            anim.setStartValue(self.width())
            anim.setEndValue(self._target_width)
            anim.setEasingCurve(QEasingCurve.Type.OutCubic)
            anim.finished.connect(self._update_expanded_state)
            anim.start()
            self._current_anim = anim
        else:
            self.setFixedWidth(self._target_width)
            self._update_expanded_state()

    def _update_collapsed_state(self):
        self.setFixedWidth(self._collapsed_width)
        self.btn_collapse.setText("▶")
        self.brand_label.setText("N")
        for btn in self.buttons:
            btn.set_collapsed(True)

    def _update_expanded_state(self):
        self.setFixedWidth(self._target_width)
        self.btn_collapse.setText("◀")
        self.brand_label.setText("NS2")
        for btn in self.buttons:
            btn.set_collapsed(False)
