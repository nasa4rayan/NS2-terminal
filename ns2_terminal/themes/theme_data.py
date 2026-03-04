"""
NS2 Terminal – Theme Definitions
================================
Four premium themes with full 16-color ANSI palettes, glow effects,
and glassmorphism-compatible color schemes.
"""

from dataclasses import dataclass, field


@dataclass
class Theme:
    """Complete terminal color theme definition."""
    name: str
    background: str          # Main window / terminal bg
    foreground: str          # Default text color
    primary: str             # Primary accent (neon)
    accent: str              # Secondary accent
    secondary_glow: str      # Subtle glow / panel backgrounds
    danger: str              # Error / interrupt color
    selection_bg: str        # Text selection background
    selection_fg: str        # Text selection foreground
    cursor_color: str        # Cursor glow color
    tab_active_bg: str       # Active tab background
    tab_inactive_bg: str     # Inactive tab background
    sidebar_bg: str          # Sidebar panel background
    input_bg: str            # Input field backgrounds
    border_color: str        # Subtle border color
    ansi_palette: list = field(default_factory=list)


# ═══════════════════════════════════════════════════════════════════════
# BLUE GLASS (Default) – Deep space blue with neon cyan accents
# ═══════════════════════════════════════════════════════════════════════
BLUE_GLASS = Theme(
    name="Blue Glass",
    background="#0b1220",
    foreground="#e0e8f0",
    primary="#00c3ff",
    accent="#64ffda",
    secondary_glow="#1f4068",
    danger="#ff4d6d",
    selection_bg="#1f4068",
    selection_fg="#e0e8f0",
    cursor_color="#00c3ff",
    tab_active_bg="rgba(0, 195, 255, 0.15)",
    tab_inactive_bg="transparent",
    sidebar_bg="rgba(11, 18, 32, 0.92)",
    input_bg="rgba(255, 255, 255, 0.06)",
    border_color="rgba(0, 195, 255, 0.2)",
    ansi_palette=[
        # Standard 8 colors
        "#3b4261", "#ff4d6d", "#64ffda", "#ffd866",
        "#00c3ff", "#c792ea", "#89ddff", "#bfc7d5",
        # Bright 8 colors
        "#546190", "#ff6b81", "#a8ffeb", "#ffe08a",
        "#40d4ff", "#d4a6f5", "#a0e8ff", "#e0e8f0",
    ],
)

# ═══════════════════════════════════════════════════════════════════════
# MATRIX GREEN – Hacker green-on-black with phosphor glow
# ═══════════════════════════════════════════════════════════════════════
MATRIX_GREEN = Theme(
    name="Matrix Green",
    background="#060d06",
    foreground="#b8f0b8",
    primary="#00ff41",
    accent="#39ff14",
    secondary_glow="#0a2e0a",
    danger="#ff4d6d",
    selection_bg="#0a3a0a",
    selection_fg="#e0ffe0",
    cursor_color="#00ff41",
    tab_active_bg="rgba(0, 255, 65, 0.12)",
    tab_inactive_bg="transparent",
    sidebar_bg="rgba(6, 13, 6, 0.92)",
    input_bg="rgba(0, 255, 65, 0.06)",
    border_color="rgba(0, 255, 65, 0.2)",
    ansi_palette=[
        "#2d3a2d", "#ff4d6d", "#00ff41", "#ffd866",
        "#39ff14", "#c792ea", "#00e5a0", "#b8f0b8",
        "#4a6b4a", "#ff6b81", "#69ff69", "#ffe08a",
        "#6bff4a", "#d4a6f5", "#40ffb8", "#d0ffd0",
    ],
)

# ═══════════════════════════════════════════════════════════════════════
# PURPLE CYBER – Deep violet with magenta / electric purple accents
# ═══════════════════════════════════════════════════════════════════════
PURPLE_CYBER = Theme(
    name="Purple Cyber",
    background="#0d0221",
    foreground="#e0d0f0",
    primary="#b026ff",
    accent="#ff6ec7",
    secondary_glow="#1a0a3e",
    danger="#ff4d6d",
    selection_bg="#2a1050",
    selection_fg="#f0e0ff",
    cursor_color="#b026ff",
    tab_active_bg="rgba(176, 38, 255, 0.15)",
    tab_inactive_bg="transparent",
    sidebar_bg="rgba(13, 2, 33, 0.92)",
    input_bg="rgba(176, 38, 255, 0.06)",
    border_color="rgba(176, 38, 255, 0.2)",
    ansi_palette=[
        "#3b2861", "#ff4d6d", "#a6e3a1", "#ffd866",
        "#b026ff", "#ff6ec7", "#89ddff", "#d0c0e8",
        "#5a3e90", "#ff6b81", "#c0f0c0", "#ffe08a",
        "#cc60ff", "#ff90d0", "#a0e8ff", "#e0d0f0",
    ],
)

# ═══════════════════════════════════════════════════════════════════════
# MINIMAL LIGHT – Clean light theme for daytime use
# ═══════════════════════════════════════════════════════════════════════
MINIMAL_LIGHT = Theme(
    name="Minimal Light",
    background="#f5f5f5",
    foreground="#2c2c2c",
    primary="#0066ff",
    accent="#00b4d8",
    secondary_glow="#e0e8f0",
    danger="#d32f2f",
    selection_bg="#b3d9ff",
    selection_fg="#2c2c2c",
    cursor_color="#0066ff",
    tab_active_bg="rgba(0, 102, 255, 0.12)",
    tab_inactive_bg="transparent",
    sidebar_bg="rgba(245, 245, 245, 0.95)",
    input_bg="rgba(0, 0, 0, 0.04)",
    border_color="rgba(0, 0, 0, 0.12)",
    ansi_palette=[
        "#c0c0c0", "#d32f2f", "#2e7d32", "#f57f17",
        "#1565c0", "#7b1fa2", "#00838f", "#424242",
        "#9e9e9e", "#e53935", "#43a047", "#f9a825",
        "#1e88e5", "#8e24aa", "#00acc1", "#2c2c2c",
    ],
)

# ─── Theme Registry ────────────────────────────────────────────────────
THEMES: dict[str, Theme] = {
    "Blue Glass": BLUE_GLASS,
    "Matrix Green": MATRIX_GREEN,
    "Purple Cyber": PURPLE_CYBER,
    "Minimal Light": MINIMAL_LIGHT,
}

DEFAULT_THEME = "Blue Glass"
