"""
NS2 Terminal – Theme Definitions
================================
Premium themes with full 16-color ANSI palettes, glassmorphism tokens,
and strict color system for a production-level UI.
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
    scrollbar_color: str = "rgba(176, 196, 222, 0.25)"   # Scrollbar thumb
    sidebar_active_bg: str = "rgba(0, 191, 255, 0.12)"   # Active sidebar item
    muted_text: str = "rgba(176, 196, 222, 0.6)"         # Muted/secondary text
    ansi_palette: list = field(default_factory=list)


# ═══════════════════════════════════════════════════════════════════════
# BLUE GLASS (Default) – Deep black + neon blue, premium cyber terminal
# Strict color system: no purple, no green, no random glow.
# ═══════════════════════════════════════════════════════════════════════
BLUE_GLASS = Theme(
    name="Blue Glass",
    background="#050C18",
    foreground="#B0C4DE",
    primary="#00BFFF",
    accent="#00E5FF",
    secondary_glow="#0A192F",
    danger="#FF4C4C",
    selection_bg="#0E2A4A",
    selection_fg="#E0E8F0",
    cursor_color="#00BFFF",
    tab_active_bg="rgba(0, 191, 255, 0.10)",
    tab_inactive_bg="transparent",
    sidebar_bg="rgba(10, 25, 47, 0.88)",
    input_bg="rgba(176, 196, 222, 0.06)",
    border_color="rgba(0, 191, 255, 0.15)",
    scrollbar_color="rgba(0, 191, 255, 0.25)",
    sidebar_active_bg="rgba(0, 191, 255, 0.12)",
    muted_text="rgba(176, 196, 222, 0.6)",
    ansi_palette=[
        # Standard 8 — blue-cold spectrum only
        "#1E2A3A", "#FF4C4C", "#5EC4B6", "#E8C87A",
        "#00BFFF", "#7EB8DA", "#00E5FF", "#B0C4DE",
        # Bright 8
        "#2E3E52", "#FF6B6B", "#7AD4C8", "#F0D890",
        "#40D0FF", "#9ECEE8", "#40F0FF", "#D0DCE8",
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
    danger="#FF4C4C",
    selection_bg="#0a3a0a",
    selection_fg="#e0ffe0",
    cursor_color="#00ff41",
    tab_active_bg="rgba(0, 255, 65, 0.12)",
    tab_inactive_bg="transparent",
    sidebar_bg="rgba(6, 13, 6, 0.92)",
    input_bg="rgba(0, 255, 65, 0.06)",
    border_color="rgba(0, 255, 65, 0.2)",
    scrollbar_color="rgba(0, 255, 65, 0.25)",
    sidebar_active_bg="rgba(0, 255, 65, 0.12)",
    muted_text="rgba(184, 240, 184, 0.6)",
    ansi_palette=[
        "#2d3a2d", "#FF4C4C", "#00ff41", "#ffd866",
        "#39ff14", "#88cc88", "#00e5a0", "#b8f0b8",
        "#4a6b4a", "#FF6B6B", "#69ff69", "#ffe08a",
        "#6bff4a", "#a0dda0", "#40ffb8", "#d0ffd0",
    ],
)

# ═══════════════════════════════════════════════════════════════════════
# MIDNIGHT STEEL – Dark gunmetal with silver-blue monochrome
# ═══════════════════════════════════════════════════════════════════════
MIDNIGHT_STEEL = Theme(
    name="Midnight Steel",
    background="#0C0E14",
    foreground="#C8CDD6",
    primary="#6B8BA4",
    accent="#8AAFC4",
    secondary_glow="#141820",
    danger="#FF4C4C",
    selection_bg="#1E2836",
    selection_fg="#E0E4EA",
    cursor_color="#6B8BA4",
    tab_active_bg="rgba(107, 139, 164, 0.12)",
    tab_inactive_bg="transparent",
    sidebar_bg="rgba(12, 14, 20, 0.92)",
    input_bg="rgba(200, 205, 214, 0.05)",
    border_color="rgba(107, 139, 164, 0.15)",
    scrollbar_color="rgba(107, 139, 164, 0.25)",
    sidebar_active_bg="rgba(107, 139, 164, 0.12)",
    muted_text="rgba(200, 205, 214, 0.5)",
    ansi_palette=[
        "#2A2E38", "#FF4C4C", "#7ABFA7", "#D4B872",
        "#6B8BA4", "#8A8EB0", "#6BBCCC", "#C8CDD6",
        "#3E4450", "#FF6B6B", "#92D1BC", "#E0C888",
        "#88A8BF", "#A4A8C8", "#88D0E0", "#E0E4EA",
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
    scrollbar_color="rgba(0, 0, 0, 0.18)",
    sidebar_active_bg="rgba(0, 102, 255, 0.10)",
    muted_text="rgba(44, 44, 44, 0.5)",
    ansi_palette=[
        "#c0c0c0", "#d32f2f", "#2e7d32", "#f57f17",
        "#1565c0", "#5c6bc0", "#00838f", "#424242",
        "#9e9e9e", "#e53935", "#43a047", "#f9a825",
        "#1e88e5", "#7986cb", "#00acc1", "#2c2c2c",
    ],
)

# ─── Theme Registry ────────────────────────────────────────────────────
THEMES: dict[str, Theme] = {
    "Blue Glass": BLUE_GLASS,
    "Matrix Green": MATRIX_GREEN,
    "Midnight Steel": MIDNIGHT_STEEL,
    "Minimal Light": MINIMAL_LIGHT,
}

DEFAULT_THEME = "Blue Glass"
