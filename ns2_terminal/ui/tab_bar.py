"""
NS2 Terminal – Tab Bar
=======================
Custom-styled QTabWidget with animated active-tab indicator,
neon glow effects, and smooth hover transitions.
"""

from PyQt6.QtWidgets import QTabWidget, QPushButton, QTabBar
from PyQt6.QtCore import Qt, QPropertyAnimation, QRect, QEasingCurve, QTimer
from PyQt6.QtGui import QPainter, QColor, QLinearGradient, QPen

from ns2_terminal.ui.split_pane import SplitPane
from ns2_terminal.config_manager import config
from ns2_terminal.themes.theme_data import THEMES, DEFAULT_THEME


class GlowTabBar(QTabBar):
    """Custom-painted tab bar with animated glowing underline indicator."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._indicator_x = 0.0
        self._indicator_width = 0.0
        self._glow_alpha = 0.7

        # Animation for sliding indicator
        self._anim = QPropertyAnimation(self, b"geometry")  # Dummy target
        self._slide_timer = QTimer(self)
        self._slide_timer.setInterval(16)  # ~60 FPS
        self._slide_timer.timeout.connect(self._step_indicator)
        self._target_x = 0.0
        self._target_w = 0.0

        self.currentChanged.connect(self._on_tab_changed)

    def _on_tab_changed(self, index):
        if index < 0:
            return
        rect = self.tabRect(index)
        self._target_x = float(rect.x())
        self._target_w = float(rect.width())
        if config.animations_enabled:
            self._slide_timer.start()
        else:
            self._indicator_x = self._target_x
            self._indicator_width = self._target_w
            self.update()

    def _step_indicator(self):
        """Smoothly interpolate indicator position."""
        dx = (self._target_x - self._indicator_x) * 0.18
        dw = (self._target_w - self._indicator_width) * 0.18
        self._indicator_x += dx
        self._indicator_width += dw
        if abs(dx) < 0.5 and abs(dw) < 0.5:
            self._indicator_x = self._target_x
            self._indicator_width = self._target_w
            self._slide_timer.stop()
        self.update()

    def showEvent(self, event):
        super().showEvent(event)
        # Initialize indicator to current tab
        idx = self.currentIndex()
        if idx >= 0:
            rect = self.tabRect(idx)
            self._indicator_x = float(rect.x())
            self._indicator_width = float(rect.width())

    def paintEvent(self, event):
        super().paintEvent(event)

        if self.count() == 0 or self._indicator_width <= 0:
            return

        theme = THEMES.get(config.theme, THEMES[DEFAULT_THEME])
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # ── Neon underline indicator ──
        h = 3
        y = self.height() - h
        ix = int(self._indicator_x)
        iw = int(self._indicator_width)

        # Glow effect (wider, softer)
        glow = QColor(theme.primary)
        glow.setAlpha(50)
        painter.fillRect(ix - 4, y - 2, iw + 8, h + 4, glow)

        # Main indicator line
        grad = QLinearGradient(ix, y, ix + iw, y)
        grad.setColorAt(0.0, QColor(theme.primary))
        grad.setColorAt(0.5, QColor(theme.accent))
        grad.setColorAt(1.0, QColor(theme.primary))
        painter.fillRect(ix, y, iw, h, grad)

        painter.end()


class TabBar(QTabWidget):
    """Premium tab widget with glassmorphism styling and animated indicators."""

    def __init__(self, parent=None):
        super().__init__(parent)

        # Use custom tab bar
        self._glow_bar = GlowTabBar(self)
        self.setTabBar(self._glow_bar)

        self.setTabsClosable(True)
        self.setMovable(True)
        self.setDocumentMode(True)

        self.tabCloseRequested.connect(self._close_tab)

        # "+" button
        self.add_btn = QPushButton("+")
        self.add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.add_btn.setFixedSize(30, 30)
        self.add_btn.clicked.connect(self.add_new_tab)
        self.setCornerWidget(self.add_btn, Qt.Corner.TopRightCorner)

        # Apply theme
        config.theme_changed.connect(self._apply_style)
        self._apply_style()

        # Initial tab
        self.add_new_tab()

    def _apply_style(self, _=None):
        theme = THEMES.get(config.theme, THEMES[DEFAULT_THEME])

        self.setStyleSheet(f"""
            QTabWidget::pane {{
                border: none;
                background: transparent;
            }}
            QTabBar {{
                background: transparent;
            }}
            QTabBar::tab {{
                background: {theme.tab_inactive_bg};
                color: {theme.foreground};
                padding: 7px 16px;
                border: none;
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
                margin-right: 2px;
                font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif;
                font-size: 12px;
                font-weight: 500;
                min-width: 88px;
            }}
            QTabBar::tab:hover {{
                background: rgba(255, 255, 255, 0.05);
            }}
            QTabBar::tab:selected {{
                background: {theme.tab_active_bg};
                color: {theme.primary};
                font-weight: 600;
            }}
            QTabBar::close-button {{
                subcontrol-position: right;
                padding: 2px;
                margin-left: 8px;
                margin-right: 2px;
            }}
            QTabBar::close-button:hover {{
                background: rgba(255, 77, 109, 0.3);
                border-radius: 3px;
            }}
        """)

        self.add_btn.setStyleSheet(f"""
            QPushButton {{
                border: none;
                color: {theme.primary};
                font-weight: bold;
                font-size: 18px;
                border-radius: 6px;
                margin: 4px 6px;
                background: transparent;
            }}
            QPushButton:hover {{
                background: rgba(255, 255, 255, 0.06);
            }}
        """)

    def add_new_tab(self) -> SplitPane:
        pane = SplitPane(self)
        idx = self.addTab(pane, f"Terminal {self.count() + 1}")
        self.setCurrentIndex(idx)
        return pane

    def _close_tab(self, index: int):
        if self.count() > 1:
            widget = self.widget(index)
            if isinstance(widget, SplitPane):
                widget.cleanup_all()
            widget.deleteLater()
            self.removeTab(index)

    def get_current_pane(self) -> SplitPane:
        return self.currentWidget()
