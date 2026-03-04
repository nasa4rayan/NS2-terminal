"""
NS2 Terminal – Splash Screen
==============================
Animated startup splash with logo, typewriter text effect,
glowing loading bar, and auto-dismiss.
"""

from PyQt6.QtWidgets import QWidget, QGraphicsDropShadowEffect
from PyQt6.QtCore import Qt, QTimer, QRectF
from PyQt6.QtGui import (
    QPainter, QColor, QFont, QLinearGradient, QPen, QRadialGradient,
)

from ns2_terminal.themes.theme_data import BLUE_GLASS


class SplashScreen(QWidget):
    """
    Frameless, translucent splash screen with animated effects.
    Calls `on_finished` callback when done.
    """

    def __init__(self, on_finished=None, parent=None):
        super().__init__(parent)
        self._on_finished = on_finished

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.SplashScreen
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(480, 320)

        # ── Animation state ──
        self._progress = 0.0          # 0.0 → 1.0 loading bar
        self._text_reveal = 0         # Characters revealed in subtitle
        self._logo_alpha = 0.0        # Fade-in for logo
        self._glow_pulse = 0.0
        self._glow_dir = 1

        self._subtitle = "ADVANCED TERMINAL EMULATOR"

        # ── Drop shadow ──
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(50)
        shadow.setOffset(0, 10)
        shadow.setColor(QColor(0, 0, 0, 160))
        self.setGraphicsEffect(shadow)

        # ── Timers ──
        self._anim_timer = QTimer(self)
        self._anim_timer.timeout.connect(self._tick)
        self._anim_timer.start(20)  # 50 FPS

        # Auto-dismiss after ~2.5 seconds
        QTimer.singleShot(2500, self._finish)

    def _tick(self):
        """Advance all animations each frame."""
        # Logo fade in
        if self._logo_alpha < 1.0:
            self._logo_alpha = min(1.0, self._logo_alpha + 0.04)

        # Loading bar progress
        if self._progress < 1.0:
            self._progress = min(1.0, self._progress + 0.012)

        # Typewriter subtitle
        target_chars = int(self._progress * len(self._subtitle))
        if self._text_reveal < target_chars:
            self._text_reveal = target_chars

        # Glow pulse
        self._glow_pulse += 0.06 * self._glow_dir
        if self._glow_pulse >= 1.0:
            self._glow_dir = -1
        elif self._glow_pulse <= 0.0:
            self._glow_dir = 1

        self.update()

    def _finish(self):
        self._anim_timer.stop()
        self.close()
        if self._on_finished:
            self._on_finished()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        theme = BLUE_GLASS
        w, h = self.width(), self.height()

        # ── Background panel ──
        bg = QColor(theme.background)
        bg.setAlpha(240)
        painter.setBrush(bg)
        painter.setPen(QPen(QColor(theme.primary + "40"), 1))
        painter.drawRoundedRect(QRectF(0, 0, w, h), 16, 16)

        # ── Center glow ──
        glow_alpha = int(30 + 20 * self._glow_pulse)
        radial = QRadialGradient(w / 2, h / 2, w / 2)
        g_color = QColor(theme.primary)
        g_color.setAlpha(glow_alpha)
        radial.setColorAt(0.0, g_color)
        radial.setColorAt(1.0, QColor(0, 0, 0, 0))
        painter.setBrush(radial)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(0, 0, w, h)

        # ── Logo text "NS2" ──
        painter.setOpacity(self._logo_alpha)
        logo_font = QFont("Inter", 52, QFont.Weight.Bold)
        painter.setFont(logo_font)
        painter.setPen(QColor(theme.primary))
        painter.drawText(QRectF(0, 50, w, 80),
                         Qt.AlignmentFlag.AlignCenter, "NS2")

        # ── Logo accent — "TERMINAL" ──
        sub_font = QFont("Inter", 14, QFont.Weight.Normal)
        sub_font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 12)
        painter.setFont(sub_font)
        painter.setPen(QColor(theme.accent))
        painter.drawText(QRectF(0, 130, w, 30),
                         Qt.AlignmentFlag.AlignCenter, "TERMINAL")
        painter.setOpacity(1.0)

        # ── Typewriter subtitle ──
        if self._text_reveal > 0:
            revealed = self._subtitle[:self._text_reveal]
            tiny = QFont("Inter", 9, QFont.Weight.Normal)
            tiny.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 3)
            painter.setFont(tiny)
            painter.setPen(QColor(theme.foreground + "99"))
            painter.drawText(QRectF(0, 175, w, 20),
                             Qt.AlignmentFlag.AlignCenter, revealed)

        # ── Loading bar ──
        bar_w = w - 120
        bar_x = 60
        bar_y = h - 60
        bar_h = 3

        # Track
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(255, 255, 255, 20))
        painter.drawRoundedRect(QRectF(bar_x, bar_y, bar_w, bar_h), 2, 2)

        # Fill with gradient
        fill_w = bar_w * self._progress
        if fill_w > 0:
            grad = QLinearGradient(bar_x, bar_y, bar_x + fill_w, bar_y)
            grad.setColorAt(0.0, QColor(theme.primary))
            grad.setColorAt(1.0, QColor(theme.accent))
            painter.setBrush(grad)
            painter.drawRoundedRect(
                QRectF(bar_x, bar_y, fill_w, bar_h), 2, 2
            )

            # Glow tip
            glow_tip = QColor(theme.accent)
            glow_tip.setAlpha(int(80 + 60 * self._glow_pulse))
            painter.setBrush(glow_tip)
            painter.drawEllipse(
                QRectF(bar_x + fill_w - 4, bar_y - 3, 8, bar_h + 6)
            )

        # ── Version ──
        ver_font = QFont("Inter", 8)
        painter.setFont(ver_font)
        painter.setPen(QColor(theme.foreground + "55"))
        painter.drawText(QRectF(0, h - 30, w, 20),
                         Qt.AlignmentFlag.AlignCenter, "v2.0.0")

        painter.end()

    def showEvent(self, event):
        """Center the splash on the screen."""
        super().showEvent(event)
        screen = self.screen()
        if screen:
            geo = screen.availableGeometry()
            x = geo.x() + (geo.width() - self.width()) // 2
            y = geo.y() + (geo.height() - self.height()) // 2
            self.move(x, y)
