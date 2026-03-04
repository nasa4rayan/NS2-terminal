"""
NS2 Terminal – Particle System
===============================
Subtle floating particle animation rendered as a transparent overlay.
Minimal CPU impact: capped at ~30 particles, updated at ~30 FPS.
"""

import random
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPainter, QColor

from ns2_terminal.config_manager import config
from ns2_terminal.themes.theme_data import THEMES, DEFAULT_THEME


class Particle:
    """A single floating particle with position, velocity, and alpha."""

    __slots__ = ("x", "y", "vx", "vy", "radius", "alpha", "alpha_dir")

    def __init__(self, width: int, height: int):
        self.x = random.uniform(0, width)
        self.y = random.uniform(0, height)
        self.vx = random.uniform(-0.3, 0.3)
        self.vy = random.uniform(-0.15, -0.05)
        self.radius = random.uniform(1.0, 2.5)
        self.alpha = random.uniform(0.1, 0.4)
        self.alpha_dir = random.choice([-1, 1]) * random.uniform(0.003, 0.008)

    def update(self, width: int, height: int):
        self.x += self.vx
        self.y += self.vy
        self.alpha += self.alpha_dir

        if self.alpha <= 0.05:
            self.alpha_dir = abs(self.alpha_dir)
        elif self.alpha >= 0.45:
            self.alpha_dir = -abs(self.alpha_dir)

        # Wrap around edges
        if self.x < -10:
            self.x = width + 10
        elif self.x > width + 10:
            self.x = -10
        if self.y < -10:
            self.y = height + 10
        elif self.y > height + 10:
            self.y = -10


class ParticleOverlay(QWidget):
    """
    Transparent overlay widget that renders floating particles.
    Place over the main content area.
    """

    BASE_PARTICLES = 30
    UPDATE_INTERVAL = 33  # ~30 FPS

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet("background: transparent;")

        self._particles: list[Particle] = []
        self._enabled = config.particles_enabled
        self._density = config.particle_density
        self._glow_intensity = config.glow_intensity

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        if self._enabled and config.animations_enabled:
            self._timer.start(self.UPDATE_INTERVAL)

        config.particles_toggled.connect(self._on_toggle)
        config.particle_density_changed.connect(self._on_density_changed)
        config.glow_intensity_changed.connect(self._on_glow_intensity_changed)
        config.animations_toggled.connect(self._on_anim_toggle)

    def _on_toggle(self, enabled: bool):
        self._enabled = enabled
        if enabled and config.animations_enabled:
            self._timer.start(self.UPDATE_INTERVAL)
        else:
            self._timer.stop()
            self._particles.clear()
            self.update()

    def _on_anim_toggle(self, enabled: bool):
        if enabled and self._enabled:
            self._timer.start(self.UPDATE_INTERVAL)
        else:
            self._timer.stop()

    def _tick(self):
        w, h = self.width(), self.height()
        if w <= 0 or h <= 0:
            return

        max_particles = max(0, int(self.BASE_PARTICLES * max(0.0, min(1.0, self._density))))

        # Spawn particles up to limit
        while len(self._particles) < max_particles:
            self._particles.append(Particle(w, h))

        # Trim if density lowered
        if len(self._particles) > max_particles:
            del self._particles[max_particles:]

        for p in self._particles:
            p.update(w, h)

        self.update()

    def paintEvent(self, event):
        if not self._particles:
            return

        theme = THEMES.get(config.theme, THEMES[DEFAULT_THEME])
        base = QColor(theme.primary)
        glow_scale = 0.55 + 0.75 * max(0.0, min(1.0, self._glow_intensity))

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)

        for p in self._particles:
            c = QColor(base)
            c.setAlphaF(max(0.0, min(1.0, p.alpha * glow_scale)))
            painter.setBrush(c)
            painter.drawEllipse(int(p.x), int(p.y),
                                int(p.radius * 2), int(p.radius * 2))

        painter.end()

    def _on_density_changed(self, density: float):
        self._density = density
        self.update()

    def _on_glow_intensity_changed(self, intensity: float):
        self._glow_intensity = intensity
        self.update()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # No need to re-init particles; they'll wrap
