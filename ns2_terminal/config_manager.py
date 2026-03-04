"""
NS2 Terminal – Configuration Manager
=====================================
Singleton settings with file persistence at ~/.config/ns2-terminal/config.json.
All settings changes emit Qt signals for live, reactive UI updates.
"""

import json
from pathlib import Path
from PyQt6.QtCore import QObject, pyqtSignal


class ConfigManager(QObject):
    """
    Manages all application settings with JSON persistence.
    Access the global instance via `config` at module level.
    """

    # ── Signals (emitted on every change) ────────────────────────────────
    theme_changed = pyqtSignal(str)
    opacity_changed = pyqtSignal(float)
    font_changed = pyqtSignal(str)
    font_size_changed = pyqtSignal(int)
    cursor_shape_changed = pyqtSignal(str)
    animations_toggled = pyqtSignal(bool)
    background_image_changed = pyqtSignal(str)
    sound_effects_toggled = pyqtSignal(bool)
    particles_toggled = pyqtSignal(bool)
    particle_density_changed = pyqtSignal(float)
    glow_intensity_changed = pyqtSignal(float)
    sidebar_toggled = pyqtSignal(bool)

    # ── Default values ───────────────────────────────────────────────────
    DEFAULTS = {
        "theme": "Blue Glass",
        "opacity": 0.92,
        "font_family": "Monospace",
        "font_size": 13,
        "cursor_shape": "Beam",        # Block | Beam | Underline
        "animations_enabled": True,
        "background_image": "",
        "sound_effects_enabled": False,
        "particles_enabled": True,
        "particle_density": 0.18,
        "glow_intensity": 0.65,
        "sidebar_visible": True,
    }

    def __init__(self):
        super().__init__()
        self._config_dir = Path.home() / ".config" / "ns2-terminal"
        self._config_file = self._config_dir / "config.json"
        self._data: dict = dict(self.DEFAULTS)
        self._load()

    # ── Persistence ──────────────────────────────────────────────────────

    def _load(self):
        """Load config from disk, merging with defaults."""
        if self._config_file.exists():
            try:
                with open(self._config_file, "r") as fh:
                    saved = json.load(fh)
                self._data.update(saved)
            except Exception as exc:
                print(f"[NS2] Config load error: {exc}")

    def save(self):
        """Persist current config to JSON."""
        try:
            self._config_dir.mkdir(parents=True, exist_ok=True)
            with open(self._config_file, "w") as fh:
                json.dump(self._data, fh, indent=4)
        except Exception as exc:
            print(f"[NS2] Config save error: {exc}")

    def reset_to_default(self):
        """Restore all settings to factory defaults and emit signals."""
        self._data = dict(self.DEFAULTS)
        self.save()
        self._emit_all()

    def _emit_all(self):
        """Fire every signal so the UI can refresh wholesale."""
        self.theme_changed.emit(self.theme)
        self.opacity_changed.emit(self.opacity)
        self.font_changed.emit(self.font_family)
        self.font_size_changed.emit(self.font_size)
        self.cursor_shape_changed.emit(self.cursor_shape)
        self.animations_toggled.emit(self.animations_enabled)
        self.background_image_changed.emit(self.background_image)
        self.sound_effects_toggled.emit(self.sound_effects_enabled)
        self.particles_toggled.emit(self.particles_enabled)
        self.particle_density_changed.emit(self.particle_density)
        self.glow_intensity_changed.emit(self.glow_intensity)
        self.sidebar_toggled.emit(self.sidebar_visible)

    # ── Generic setter helper ────────────────────────────────────────────

    def _set(self, key: str, value, signal: pyqtSignal):
        if self._data.get(key) != value:
            self._data[key] = value
            self.save()
            signal.emit(value)

    # ── Properties ───────────────────────────────────────────────────────

    @property
    def theme(self) -> str:
        return self._data.get("theme", self.DEFAULTS["theme"])

    @theme.setter
    def theme(self, v: str):
        self._set("theme", v, self.theme_changed)

    @property
    def opacity(self) -> float:
        return self._data.get("opacity", self.DEFAULTS["opacity"])

    @opacity.setter
    def opacity(self, v: float):
        self._set("opacity", max(0.0, min(1.0, v)), self.opacity_changed)

    @property
    def font_family(self) -> str:
        return self._data.get("font_family", self.DEFAULTS["font_family"])

    @font_family.setter
    def font_family(self, v: str):
        self._set("font_family", v, self.font_changed)

    @property
    def font_size(self) -> int:
        return self._data.get("font_size", self.DEFAULTS["font_size"])

    @font_size.setter
    def font_size(self, v: int):
        self._set("font_size", max(6, min(72, v)), self.font_size_changed)

    @property
    def cursor_shape(self) -> str:
        return self._data.get("cursor_shape", self.DEFAULTS["cursor_shape"])

    @cursor_shape.setter
    def cursor_shape(self, v: str):
        self._set("cursor_shape", v, self.cursor_shape_changed)

    @property
    def animations_enabled(self) -> bool:
        return self._data.get("animations_enabled", self.DEFAULTS["animations_enabled"])

    @animations_enabled.setter
    def animations_enabled(self, v: bool):
        self._set("animations_enabled", v, self.animations_toggled)

    @property
    def background_image(self) -> str:
        return self._data.get("background_image", self.DEFAULTS["background_image"])

    @background_image.setter
    def background_image(self, v: str):
        self._set("background_image", v, self.background_image_changed)

    @property
    def sound_effects_enabled(self) -> bool:
        return self._data.get("sound_effects_enabled", self.DEFAULTS["sound_effects_enabled"])

    @sound_effects_enabled.setter
    def sound_effects_enabled(self, v: bool):
        self._set("sound_effects_enabled", v, self.sound_effects_toggled)

    @property
    def particles_enabled(self) -> bool:
        return self._data.get("particles_enabled", self.DEFAULTS["particles_enabled"])

    @particles_enabled.setter
    def particles_enabled(self, v: bool):
        self._set("particles_enabled", v, self.particles_toggled)

    @property
    def particle_density(self) -> float:
        return float(self._data.get("particle_density", self.DEFAULTS["particle_density"]))

    @particle_density.setter
    def particle_density(self, v: float):
        self._set("particle_density", max(0.0, min(1.0, float(v))), self.particle_density_changed)

    @property
    def glow_intensity(self) -> float:
        return float(self._data.get("glow_intensity", self.DEFAULTS["glow_intensity"]))

    @glow_intensity.setter
    def glow_intensity(self, v: float):
        self._set("glow_intensity", max(0.0, min(1.0, float(v))), self.glow_intensity_changed)

    @property
    def sidebar_visible(self) -> bool:
        return self._data.get("sidebar_visible", self.DEFAULTS["sidebar_visible"])

    @sidebar_visible.setter
    def sidebar_visible(self, v: bool):
        self._set("sidebar_visible", v, self.sidebar_toggled)


# ── Global singleton ─────────────────────────────────────────────────────
config = ConfigManager()
