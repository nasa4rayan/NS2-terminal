"""
NS2 Terminal – Main Window
============================
Glassmorphism main window with sidebar, tab bar, particle overlay,
command palette, and full keyboard shortcut integration.
"""

import math

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QGraphicsDropShadowEffect, QApplication,
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer, QRectF
from PyQt6.QtGui import QColor, QKeySequence, QShortcut, QIcon, QPainter, QLinearGradient, QRadialGradient, QPixmap

from ns2_terminal.ui.tab_bar import TabBar
from ns2_terminal.ui.sidebar import Sidebar
from ns2_terminal.ui.command_palette import CommandPalette
from ns2_terminal.ui.particles import ParticleOverlay
from ns2_terminal.settings.settings_panel import SettingsPanel
from ns2_terminal.config_manager import config
from ns2_terminal.themes.theme_data import THEMES, DEFAULT_THEME


class BackgroundCanvas(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent, False)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self._theme = THEMES.get(config.theme, THEMES[DEFAULT_THEME])
        self._opacity = config.opacity
        self._glow_intensity = config.glow_intensity
        self._phase = 0.0
        self._bg_pixmap: QPixmap | None = None
        self._load_background_image()

        self._timer = QTimer(self)
        self._timer.setInterval(16)  # ~60 FPS cap
        self._timer.timeout.connect(self._tick)
        if config.animations_enabled:
            self._timer.start()

        config.theme_changed.connect(self._on_theme)
        config.opacity_changed.connect(self._on_opacity)
        config.glow_intensity_changed.connect(self._on_glow)
        config.background_image_changed.connect(lambda _: self._load_background_image())
        config.animations_toggled.connect(self._on_animations)

    def _on_theme(self, name: str):
        self._theme = THEMES.get(name, THEMES[DEFAULT_THEME])
        self.update()

    def _on_opacity(self, v: float):
        self._opacity = v
        self.update()

    def _on_glow(self, v: float):
        self._glow_intensity = max(0.0, min(1.0, float(v)))
        self.update()

    def _on_animations(self, enabled: bool):
        if enabled:
            self._timer.start()
        else:
            self._timer.stop()
            self._phase = 0.0
            self.update()

    def _tick(self):
        self._phase += 0.03
        if self._phase > 1000000.0:
            self._phase = 0.0
        self.update()

    def _load_background_image(self):
        path = config.background_image
        if path and path.strip():
            px = QPixmap(path)
            if not px.isNull():
                self._bg_pixmap = px
                self.update()
                return
        self._bg_pixmap = None
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        if not painter.isActive():
            return
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.width(), self.height()
        theme = self._theme

        # Base background (opacity driven)
        base = QColor(theme.background)
        base.setAlphaF(max(0.0, min(1.0, self._opacity)))
        painter.fillRect(self.rect(), base)

        # Subtle vertical gradient depth
        grad = QLinearGradient(0, 0, 0, max(1, h))
        if theme.name == "Blue Glass":
            top = QColor("#0b1220")
            bot = QColor("#0e1a2f")
        else:
            top = QColor(theme.background).lighter(110)
            bot = QColor(theme.background).darker(112)
        top.setAlphaF(0.70 * self._opacity)
        bot.setAlphaF(0.90 * self._opacity)
        grad.setColorAt(0.0, top)
        grad.setColorAt(1.0, bot)
        painter.fillRect(self.rect(), grad)

        # Background image (optional)
        if self._bg_pixmap:
            scaled = self._bg_pixmap.scaled(
                self.size(),
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation,
            )
            x = (w - scaled.width()) // 2
            y = (h - scaled.height()) // 2
            painter.setOpacity(0.12)
            painter.drawPixmap(x, y, scaled)
            painter.setOpacity(1.0)

        # Breathing center glow (focus-dependent intensity)
        pulse = 0.5
        if config.animations_enabled:
            # 0.85–1.15
            pulse = 1.0 + 0.15 * (0.5 + 0.5 * math.sin(self._phase))

        glow_strength = (0.16 + 0.34 * self._glow_intensity) * pulse
        glow_alpha = int(255 * min(0.14, glow_strength))

        radial = QRadialGradient(w * 0.5, h * 0.38, max(240.0, min(w, h) * 0.72))
        c0 = QColor(theme.primary)
        c0.setAlpha(glow_alpha)
        c1 = QColor(theme.accent)
        c1.setAlpha(int(glow_alpha * 0.55))
        radial.setColorAt(0.0, c0)
        radial.setColorAt(0.35, c1)
        radial.setColorAt(1.0, QColor(0, 0, 0, 0))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(radial)
        painter.drawRect(QRectF(0, 0, w, h))

        painter.end()


class MainWindow(QMainWindow):
    """
    Premium glassmorphism main window.
    Integrates sidebar, tabbed terminals, particles, and command palette.
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("NS2 Terminal")
        self.resize(1100, 750)
        self.setMinimumSize(600, 400)

        # ── Window icon ──
        import os
        icon_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "assets", "icon.png"
        )
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        # ── Central widget ──
        central = QWidget()
        central.setObjectName("centralWidget")
        self.setCentralWidget(central)

        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # ── Background canvas (layer 1) ──
        self._bg_canvas = BackgroundCanvas(central)
        self._bg_canvas.setGeometry(central.rect())
        self._bg_canvas.lower()

        # ── Content area (Sidebar + Tabs) ──
        content_widget = QWidget()
        content_layout = QHBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # Sidebar
        self.sidebar = Sidebar(self, content_widget)
        content_layout.addWidget(self.sidebar)

        # Tab bar
        self.tab_bar = TabBar(content_widget)
        content_layout.addWidget(self.tab_bar, 1)

        root_layout.addWidget(content_widget, 1)

        # ── Particle overlay (layer 2) ──
        self.particles = ParticleOverlay(central)
        self.particles.setGeometry(central.rect())
        self.particles.stackUnder(content_widget)  # behind content, above background
        self.particles.raise_()

        # ── Command palette (floating) ──
        self.command_palette = CommandPalette(self)
        self.command_palette.hide()
        self._register_palette_commands()

        # ── Connect sidebar buttons ──
        self.sidebar.btn_new_tab.clicked.connect(self.tab_bar.add_new_tab)
        self.sidebar.btn_split_h.clicked.connect(
            lambda: self.tab_bar.get_current_pane().split_horizontal()
        )
        self.sidebar.btn_split_v.clicked.connect(
            lambda: self.tab_bar.get_current_pane().split_vertical()
        )
        self.sidebar.btn_palette.clicked.connect(self.command_palette.toggle)
        self.sidebar.btn_settings.clicked.connect(self.open_settings)
        self.sidebar.btn_theme.clicked.connect(self._cycle_theme)
        self.sidebar.btn_fullscreen.clicked.connect(self._toggle_fullscreen)

        # ── Keyboard shortcuts ──
        self._setup_shortcuts()

        # ── Theme connection ──
        config.theme_changed.connect(self._apply_theme)
        config.opacity_changed.connect(lambda _: self._apply_theme())
        config.glow_intensity_changed.connect(lambda _: self._apply_theme())
        config.background_image_changed.connect(lambda _: self._apply_theme())
        config.sidebar_toggled.connect(self._on_sidebar_toggled)
        self._apply_theme()

        # Instant startup: no fade-in delay

    # ── Theme ────────────────────────────────────────────────────────────

    def _apply_theme(self, _=None):
        theme = THEMES.get(config.theme, THEMES[DEFAULT_THEME])

        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {theme.background};
            }}
            #centralWidget {{
                background-color: transparent;
            }}
        """)
        self.update()

    # ── Sidebar toggle ───────────────────────────────────────────────────

    def _on_sidebar_toggled(self, visible: bool):
        self.sidebar.setVisible(visible)

    def _toggle_sidebar(self):
        self.sidebar.setVisible(not self.sidebar.isVisible())

    # ── Settings ─────────────────────────────────────────────────────────

    def open_settings(self):
        SettingsPanel(self).exec()

    # ── Theme cycling ────────────────────────────────────────────────────

    def _cycle_theme(self):
        names = list(THEMES.keys())
        idx = names.index(config.theme) if config.theme in names else 0
        config.theme = names[(idx + 1) % len(names)]

    # ── Fullscreen ───────────────────────────────────────────────────────

    def _toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    # ── Keyboard shortcuts ───────────────────────────────────────────────

    def _setup_shortcuts(self):
        def sc(keys, slot):
            QShortcut(QKeySequence(keys), self).activated.connect(slot)

        sc("F11", self._toggle_fullscreen)
        sc("Ctrl+Shift+S", self.open_settings)
        sc("Ctrl+Shift+P", self.command_palette.toggle)
        sc("Ctrl+Shift+T", self.tab_bar.add_new_tab)
        sc("Ctrl+Shift+W", lambda: self.tab_bar._close_tab(
            self.tab_bar.currentIndex()))
        sc("Ctrl+Shift+H", lambda: self.tab_bar.get_current_pane().split_horizontal())
        sc("Ctrl+Shift+E", lambda: self.tab_bar.get_current_pane().split_vertical())
        sc("Ctrl+Shift+B", self._toggle_sidebar)
        sc("Ctrl+Alt+M", self.showMinimized)

    # ── Command palette registry ─────────────────────────────────────────

    def _register_palette_commands(self):
        commands = [
            ("New Tab", self.tab_bar.add_new_tab),
            ("Close Tab", lambda: self.tab_bar._close_tab(
                self.tab_bar.currentIndex())),
            ("Split Horizontal", lambda: self.tab_bar.get_current_pane().split_horizontal()),
            ("Split Vertical", lambda: self.tab_bar.get_current_pane().split_vertical()),
            ("Toggle Fullscreen", self._toggle_fullscreen),
            ("Minimize Window", self.showMinimized),
            ("Toggle Sidebar", self._toggle_sidebar),
            ("Open Settings", self.open_settings),
            ("Theme: Blue Glass", lambda: setattr(config, "theme", "Blue Glass")),
            ("Theme: Matrix Green", lambda: setattr(config, "theme", "Matrix Green")),
            ("Theme: Purple Cyber", lambda: setattr(config, "theme", "Purple Cyber")),
            ("Theme: Minimal Light", lambda: setattr(config, "theme", "Minimal Light")),
            ("Cycle Theme", self._cycle_theme),
            ("Toggle Particles", lambda: setattr(
                config, "particles_enabled", not config.particles_enabled)),
            ("Toggle Animations", lambda: setattr(
                config, "animations_enabled", not config.animations_enabled)),
            ("Reset Settings", config.reset_to_default),
        ]
        self.command_palette.register_commands(commands)

    # ── Resize (keep particles covering content) ─────────────────────────

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cw = self.centralWidget()
        if cw:
            if hasattr(self, "_bg_canvas"):
                self._bg_canvas.setGeometry(cw.rect())
            if hasattr(self, "particles"):
                self.particles.setGeometry(cw.rect())

    # ── Cleanup ──────────────────────────────────────────────────────────

    def closeEvent(self, event):
        # Clean up all terminal backends
        for i in range(self.tab_bar.count()):
            w = self.tab_bar.widget(i)
            if hasattr(w, "cleanup_all"):
                w.cleanup_all()
        super().closeEvent(event)
