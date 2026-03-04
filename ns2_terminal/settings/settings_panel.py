"""
NS2 Terminal – Settings Panel
==============================
Professional tabbed settings dialog with glassmorphism styling.
Tabs: Appearance, Font & Text, Behavior, About.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QSlider, QFontComboBox, QSpinBox, QCheckBox, QPushButton,
    QFormLayout, QGroupBox, QTabWidget, QWidget, QFileDialog,
    QTextBrowser,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from ns2_terminal.config_manager import config
from ns2_terminal.themes.theme_data import THEMES, DEFAULT_THEME


class SettingsPanel(QDialog):
    """Premium tabbed settings dialog."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("NS2 Terminal – Settings")
        self.setFixedSize(480, 560)

        theme = THEMES.get(config.theme, THEMES[DEFAULT_THEME])

        # ── Master stylesheet ──
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {theme.background};
                color: {theme.foreground};
                font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif;
            }}
            QLabel {{
                color: {theme.foreground};
                font-size: 13px;
            }}
            QGroupBox {{
                color: {theme.primary};
                font-weight: 600;
                font-size: 13px;
                border: 1px solid {theme.border_color};
                border-radius: 8px;
                margin-top: 20px;
                padding-top: 14px;
                background: {theme.input_bg};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 14px;
                top: -8px;
                padding: 0 6px;
                background: {theme.background};
            }}
            QPushButton {{
                background: {theme.input_bg};
                color: {theme.primary};
                border: 1px solid {theme.border_color};
                padding: 7px 18px;
                border-radius: 6px;
                font-weight: 600;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background: rgba(255, 255, 255, 0.08);
                border: 1px solid {theme.primary};
            }}
            QPushButton:pressed {{
                background: rgba(255, 255, 255, 0.12);
            }}
            QComboBox, QFontComboBox, QSpinBox {{
                background: {theme.input_bg};
                color: {theme.foreground};
                border: 1px solid {theme.border_color};
                padding: 5px 10px;
                border-radius: 6px;
                min-height: 26px;
                font-size: 12px;
            }}
            QComboBox:hover, QFontComboBox:hover, QSpinBox:hover {{
                border: 1px solid {theme.primary};
            }}
            QComboBox::drop-down {{
                border: none;
            }}
            QComboBox QAbstractItemView {{
                background: {theme.background};
                color: {theme.foreground};
                border: 1px solid {theme.border_color};
                selection-background-color: {theme.tab_active_bg};
            }}
            QSlider::groove:horizontal {{
                border-radius: 2px;
                height: 4px;
                background: rgba(255, 255, 255, 0.1);
            }}
            QSlider::handle:horizontal {{
                background: {theme.primary};
                border: none;
                height: 16px;
                width: 16px;
                margin: -6px 0;
                border-radius: 8px;
            }}
            QSlider::handle:horizontal:hover {{
                background: {theme.accent};
            }}
            QSlider::sub-page:horizontal {{
                background: {theme.primary};
                border-radius: 2px;
            }}
            QCheckBox {{
                spacing: 8px;
                font-size: 13px;
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 1px solid {theme.border_color};
                background: {theme.input_bg};
            }}
            QCheckBox::indicator:checked {{
                background: {theme.primary};
                border: 1px solid {theme.primary};
            }}
            QTabWidget::pane {{
                border: none;
                background: transparent;
            }}
            QTabBar::tab {{
                background: transparent;
                color: {theme.foreground};
                padding: 8px 16px;
                border: none;
                font-size: 12px;
                font-weight: 500;
            }}
            QTabBar::tab:hover {{
                color: {theme.primary};
            }}
            QTabBar::tab:selected {{
                color: {theme.primary};
                font-weight: 600;
                border-bottom: 2px solid {theme.primary};
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(12)

        # ── Title ──
        title = QLabel("Settings")
        title.setFont(QFont("Inter", 18, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {theme.foreground}; margin-bottom: 4px;")
        layout.addWidget(title)

        # ── Tab widget ──
        tabs = QTabWidget()
        tabs.addTab(self._build_appearance_tab(), "Appearance")
        tabs.addTab(self._build_font_tab(), "Font & Text")
        tabs.addTab(self._build_behavior_tab(), "Behavior")
        tabs.addTab(self._build_about_tab(), "About")
        layout.addWidget(tabs)

        # ── Bottom buttons ──
        btn_lay = QHBoxLayout()
        reset_btn = QPushButton("Reset to Default")
        reset_btn.clicked.connect(self._reset_defaults)
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)

        btn_lay.addWidget(reset_btn)
        btn_lay.addStretch()
        btn_lay.addWidget(close_btn)
        layout.addLayout(btn_lay)

    # ── Appearance Tab ───────────────────────────────────────────────────

    def _build_appearance_tab(self) -> QWidget:
        w = QWidget()
        form = QFormLayout(w)
        form.setContentsMargins(10, 16, 10, 10)
        form.setSpacing(14)

        # Theme
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(list(THEMES.keys()))
        self.theme_combo.setCurrentText(config.theme)
        self.theme_combo.currentTextChanged.connect(
            lambda t: setattr(config, "theme", t)
        )
        form.addRow("Theme:", self.theme_combo)

        # Opacity
        self.opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.opacity_slider.setRange(60, 100)
        self.opacity_slider.setValue(int(config.opacity * 100))
        self.opacity_label = QLabel(f"{int(config.opacity * 100)}%")
        self.opacity_slider.valueChanged.connect(self._on_opacity)
        opacity_row = QHBoxLayout()
        opacity_row.addWidget(self.opacity_slider)
        opacity_row.addWidget(self.opacity_label)
        form.addRow("Opacity:", opacity_row)

        # Glow intensity
        self.glow_slider = QSlider(Qt.Orientation.Horizontal)
        self.glow_slider.setRange(0, 100)
        self.glow_slider.setValue(int(config.glow_intensity * 100))
        self.glow_label = QLabel(f"{int(config.glow_intensity * 100)}%")
        self.glow_slider.valueChanged.connect(self._on_glow)
        glow_row = QHBoxLayout()
        glow_row.addWidget(self.glow_slider)
        glow_row.addWidget(self.glow_label)
        form.addRow("Glow:", glow_row)

        # Particle density
        self.particle_slider = QSlider(Qt.Orientation.Horizontal)
        self.particle_slider.setRange(0, 100)
        self.particle_slider.setValue(int(config.particle_density * 100))
        self.particle_label = QLabel(f"{int(config.particle_density * 100)}%")
        self.particle_slider.valueChanged.connect(self._on_particle_density)
        particle_row = QHBoxLayout()
        particle_row.addWidget(self.particle_slider)
        particle_row.addWidget(self.particle_label)
        form.addRow("Particles:", particle_row)

        # Background image
        self.bg_path_label = QLabel(
            config.background_image or "None"
        )
        self.bg_path_label.setStyleSheet("font-size: 11px; opacity: 0.7;")
        bg_btn = QPushButton("Browse…")
        bg_btn.clicked.connect(self._browse_background)
        bg_clear = QPushButton("Clear")
        bg_clear.clicked.connect(self._clear_background)
        bg_row = QHBoxLayout()
        bg_row.addWidget(self.bg_path_label, 1)
        bg_row.addWidget(bg_btn)
        bg_row.addWidget(bg_clear)
        form.addRow("Background:", bg_row)

        return w

    def _on_opacity(self, value: int):
        config.opacity = value / 100.0
        self.opacity_label.setText(f"{value}%")

    def _on_glow(self, value: int):
        config.glow_intensity = value / 100.0
        self.glow_label.setText(f"{value}%")

    def _on_particle_density(self, value: int):
        config.particle_density = value / 100.0
        self.particle_label.setText(f"{value}%")

    def _browse_background(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Background Image", "",
            "Images (*.png *.jpg *.jpeg *.webp *.bmp)"
        )
        if path:
            config.background_image = path
            self.bg_path_label.setText(path.split("/")[-1])

    def _clear_background(self):
        config.background_image = ""
        self.bg_path_label.setText("None")

    # ── Font & Text Tab ──────────────────────────────────────────────────

    def _build_font_tab(self) -> QWidget:
        w = QWidget()
        form = QFormLayout(w)
        form.setContentsMargins(10, 16, 10, 10)
        form.setSpacing(14)

        self.font_combo = QFontComboBox()
        self.font_combo.setCurrentText(config.font_family)
        self.font_combo.currentFontChanged.connect(
            lambda f: setattr(config, "font_family", f.family())
        )
        form.addRow("Font Family:", self.font_combo)

        self.size_spin = QSpinBox()
        self.size_spin.setRange(6, 72)
        self.size_spin.setValue(config.font_size)
        self.size_spin.valueChanged.connect(
            lambda v: setattr(config, "font_size", v)
        )
        form.addRow("Font Size:", self.size_spin)

        return w

    # ── Behavior Tab ─────────────────────────────────────────────────────

    def _build_behavior_tab(self) -> QWidget:
        w = QWidget()
        form = QFormLayout(w)
        form.setContentsMargins(10, 16, 10, 10)
        form.setSpacing(14)

        # Cursor shape
        self.cursor_combo = QComboBox()
        self.cursor_combo.addItems(["Block", "Beam", "Underline"])
        self.cursor_combo.setCurrentText(config.cursor_shape)
        self.cursor_combo.currentTextChanged.connect(
            lambda c: setattr(config, "cursor_shape", c)
        )
        form.addRow("Cursor Shape:", self.cursor_combo)

        # Animations
        self.anim_check = QCheckBox("Enable animations")
        self.anim_check.setChecked(config.animations_enabled)
        self.anim_check.toggled.connect(
            lambda v: setattr(config, "animations_enabled", v)
        )
        form.addRow("", self.anim_check)

        # Particles
        self.particles_check = QCheckBox("Background particles")
        self.particles_check.setChecked(config.particles_enabled)
        self.particles_check.toggled.connect(
            lambda v: setattr(config, "particles_enabled", v)
        )
        form.addRow("", self.particles_check)

        # Sound effects
        self.sound_check = QCheckBox("Sound effects")
        self.sound_check.setChecked(config.sound_effects_enabled)
        self.sound_check.toggled.connect(
            lambda v: setattr(config, "sound_effects_enabled", v)
        )
        form.addRow("", self.sound_check)

        return w

    # ── About Tab ────────────────────────────────────────────────────────

    def _build_about_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(10, 16, 10, 10)

        about = QLabel(
            "<h2>NS2 Terminal</h2>"
            "<p>Version 2.0.0</p>"
            "<p>A premium futuristic terminal emulator<br>"
            "built with PyQt6 &amp; pyte.</p>"
            "<hr>"
            "<p><b>Keyboard Shortcuts</b></p>"
            "<table cellpadding='4'>"
            "<tr><td>Ctrl+Shift+T</td><td>New Tab</td></tr>"
            "<tr><td>Ctrl+Shift+W</td><td>Close Tab</td></tr>"
            "<tr><td>Ctrl+Shift+H</td><td>Split Horizontal</td></tr>"
            "<tr><td>Ctrl+Shift+E</td><td>Split Vertical</td></tr>"
            "<tr><td>Ctrl+Shift+P</td><td>Command Palette</td></tr>"
            "<tr><td>Ctrl+Shift+S</td><td>Settings</td></tr>"
            "<tr><td>Ctrl+Shift+B</td><td>Toggle Sidebar</td></tr>"
            "<tr><td>Ctrl+Alt+M</td><td>Minimize Window</td></tr>"
            "<tr><td>Ctrl+Shift+C</td><td>Copy</td></tr>"
            "<tr><td>Ctrl+Shift+V</td><td>Paste</td></tr>"
            "<tr><td>F11</td><td>Fullscreen</td></tr>"
            "</table>"
        )
        about.setWordWrap(True)
        about.setStyleSheet("font-size: 13px;")
        layout.addWidget(about)
        layout.addStretch()

        return w

    # ── Reset ────────────────────────────────────────────────────────────

    def _reset_defaults(self):
        config.reset_to_default()
        self.theme_combo.setCurrentText(config.theme)
        self.opacity_slider.setValue(int(config.opacity * 100))
        self.glow_slider.setValue(int(config.glow_intensity * 100))
        self.particle_slider.setValue(int(config.particle_density * 100))
        self.font_combo.setCurrentText(config.font_family)
        self.size_spin.setValue(config.font_size)
        self.cursor_combo.setCurrentText(config.cursor_shape)
        self.anim_check.setChecked(config.animations_enabled)
        self.particles_check.setChecked(config.particles_enabled)
        self.sound_check.setChecked(config.sound_effects_enabled)
