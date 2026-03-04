"""
NS2 Terminal – Sidebar
=======================
Glassmorphism sidebar with active neon indicator bar, smooth hover
animations, and collapsible icon-only mode.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel, QFrame, QSizePolicy,
)
from PyQt6.QtCore import (
    Qt, QPropertyAnimation, QEasingCurve, QSize, pyqtProperty, QTimer,
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
        self._is_active = False
        self.setText(f"  {icon_char}   {label}")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(40)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

    def set_active(self, active: bool):
        """Mark this button as the active sidebar item."""
        self._is_active = active
        self._refresh_style()

    def set_collapsed(self, collapsed: bool):
        if collapsed:
            self.setText(self._icon_char)
            self.setFixedWidth(44)
        else:
            self.setText(f"  {self._icon_char}   {self._label_text}")
            self.setMaximumWidth(16777215)  # Reset max width

    def _refresh_style(self):
        """Apply active/inactive styling via dynamic property."""
        self.setProperty("active", self._is_active)
        self.style().unpolish(self)
        self.style().polish(self)


class Sidebar(QWidget):
    """Premium glassmorphism sidebar with quick actions."""

    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self._main_window = main_window
        self._expanded = True
        self._target_width = 190
        self._collapsed_width = 52

        self.setFixedWidth(self._target_width)
        self.setObjectName("NS2Sidebar")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 16, 10, 14)
        layout.setSpacing(4)

        # ── Logo / branding ──
        self.brand_label = QLabel("NS2")
        self.brand_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.brand_label.setFont(QFont("Inter", 14, QFont.Weight.Bold))
        self.brand_label.setObjectName("sidebarBrand")
        layout.addWidget(self.brand_label)

        layout.addSpacing(14)

        # ── Separator ──
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setFixedHeight(1)
        sep.setObjectName("sidebarSep")
        layout.addWidget(sep)
        layout.addSpacing(10)

        # ── Action buttons ── (clean unicode icons, Lucide-inspired)
        self.btn_new_tab  = SidebarButton("＋", "New Tab")
        self.btn_split_h  = SidebarButton("⇔", "Split H")
        self.btn_split_v  = SidebarButton("⇕", "Split V")
        self.btn_palette  = SidebarButton("⌘", "Commands")
        self.btn_settings = SidebarButton("⚙", "Settings")
        self.btn_theme    = SidebarButton("◑", "Theme")
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
        self.btn_collapse.setFixedHeight(34)
        self.btn_collapse.setObjectName("collapseBtn")
        self.btn_collapse.clicked.connect(self.toggle_collapse)
        layout.addWidget(self.btn_collapse)

        # Apply initial theme
        config.theme_changed.connect(self._apply_style)
        self._apply_style()

    def _apply_style(self, _=None):
        theme = THEMES.get(config.theme, THEMES[DEFAULT_THEME])

        self.setStyleSheet(f"""
            #NS2Sidebar {{
                background: {theme.sidebar_bg};
                border-right: 1px solid {theme.border_color};
            }}
            #sidebarSep {{
                background: {theme.border_color};
                border: none;
            }}
            #sidebarBrand {{
                color: {theme.primary};
                letter-spacing: 6px;
                font-weight: 700;
            }}

            /* ── Sidebar buttons ── */
            QPushButton {{
                background: transparent;
                color: {theme.foreground};
                border: none;
                border-radius: 8px;
                font-size: 12px;
                text-align: left;
                padding: 0 12px;
                font-family: 'Inter', 'Segoe UI', sans-serif;
            }}
            QPushButton:hover {{
                background: rgba(255, 255, 255, 0.05);
                color: {theme.primary};
                padding-left: 15px;
            }}
            QPushButton:pressed {{
                background: rgba(255, 255, 255, 0.08);
            }}

            /* Active state: left neon bar */
            QPushButton[active="true"] {{
                background: {theme.sidebar_active_bg};
                color: {theme.primary};
                border-left: 3px solid {theme.primary};
                padding-left: 9px;
                font-weight: 600;
            }}

            /* ── Collapse button ── */
            #collapseBtn {{
                background: rgba(255, 255, 255, 0.03);
                color: {theme.muted_text};
                border: none;
                border-radius: 8px;
                font-size: 14px;
                text-align: center;
                padding: 0;
            }}
            #collapseBtn:hover {{
                background: rgba(255, 255, 255, 0.06);
                color: {theme.primary};
            }}
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
            anim.setDuration(180)
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
            anim.setDuration(180)
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
