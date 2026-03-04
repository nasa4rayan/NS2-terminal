"""
NS2 Terminal – Terminal Widget
===============================
Custom QPainter-based terminal renderer with animated glowing cursor,
mouse selection for copy, drag-and-drop file paths, background image
support, and smooth scroll.
"""

from PyQt6.QtWidgets import QWidget, QApplication
from PyQt6.QtGui import (
    QPainter, QColor, QFont, QFontMetrics, QKeyEvent, QFontDatabase,
    QMouseEvent, QPixmap, QPen, QBrush, QLinearGradient,
)
from PyQt6.QtCore import Qt, QTimer, QPointF, QRectF, pyqtSignal

from ns2_terminal.core.terminal_backend import TerminalBackend
from ns2_terminal.config_manager import config
from ns2_terminal.themes.theme_data import THEMES, DEFAULT_THEME


class TerminalWidget(QWidget):
    """QPainter-based VT100 terminal renderer with premium visual effects."""

    title_changed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent, False)
        self.setAcceptDrops(True)
        self.setMouseTracking(True)

        # Rendering margins — premium spacing
        self.MARGIN_X = 16
        self.MARGIN_Y = 12

        # Theme
        self.theme = THEMES.get(config.theme, THEMES[DEFAULT_THEME])

        # Background image cache
        self._bg_pixmap = None
        self._load_background_image()

        # Backend (created but NOT started)
        self.backend = TerminalBackend(cols=80, rows=24, parent=self)

        # Font setup
        self._setup_font()

        # Connect backend signals
        self.backend.screen_updated.connect(self.update)
        self.backend.title_changed.connect(self.title_changed.emit)
        self.backend.process_exited.connect(self._on_process_exit)

        # Cursor blink & glow
        self.cursor_visible = True
        self._cursor_glow_alpha = 0.8
        self._glow_intensity = config.glow_intensity
        self._cursor_glow_direction = -1
        self._blink_timer = QTimer(self)
        self._blink_timer.timeout.connect(self._toggle_cursor)
        self._glow_timer = QTimer(self)
        self._glow_timer.timeout.connect(self._animate_cursor_glow)
        if config.animations_enabled:
            self._blink_timer.start(530)
            self._glow_timer.start(50)

        # Mouse selection state
        self._selecting = False
        self._sel_start = None   # (col, row)
        self._sel_end = None     # (col, row)

        # Connect config signals
        config.theme_changed.connect(self._on_theme_changed)
        config.font_changed.connect(lambda _: self._setup_font())
        config.font_size_changed.connect(lambda _: self._setup_font())
        config.animations_toggled.connect(self._on_animations_toggled)
        config.opacity_changed.connect(lambda _: self.update())
        config.glow_intensity_changed.connect(self._on_glow_intensity_changed)
        config.background_image_changed.connect(lambda _: self._load_background_image())

        # Defer backend start to next event-loop tick
        QTimer.singleShot(0, self._deferred_start)

    # ── Deferred start ───────────────────────────────────────────────────

    def _deferred_start(self):
        self._resize_backend()
        self.backend.start()

    # ── Font ─────────────────────────────────────────────────────────────

    def _setup_font(self):
        family = config.font_family
        if not family or family == "Monospace":
            preferred = (
                "JetBrains Mono",
                "Fira Code",
                "Iosevka",
                "Cascadia Mono",
                "Source Code Pro",
                "DejaVu Sans Mono",
                "Noto Sans Mono",
                "Liberation Mono",
                "Monospace",
            )
            available = set(QFontDatabase.families())
            for cand in preferred:
                if cand in available:
                    family = cand
                    break

        self.term_font = QFont(family, config.font_size)
        self.term_font.setStyleHint(QFont.StyleHint.TypeWriter)
        self.term_font.setHintingPreference(QFont.HintingPreference.PreferFullHinting)
        self.term_font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 0.35)

        fm = QFontMetrics(self.term_font)
        self._native_height = max(fm.height(), 1)
        self.char_width = max(fm.horizontalAdvance("W"), 1)
        self.char_height = max(int(self._native_height * 1.12), 1)
        self.ascent = fm.ascent()
        self._baseline_adjust = int((self.char_height - self._native_height) * 0.5)
        self._resize_backend()
        self.update()

    # ── Theme / animation callbacks ──────────────────────────────────────

    def _on_theme_changed(self, name: str):
        self.theme = THEMES.get(name, THEMES[DEFAULT_THEME])
        self.update()

    def _on_animations_toggled(self, enabled: bool):
        if enabled:
            self._blink_timer.start(530)
            self._glow_timer.start(50)
        else:
            self._blink_timer.stop()
            self._glow_timer.stop()
            self.cursor_visible = True
            self._cursor_glow_alpha = 0.8
            self.update()

    def _toggle_cursor(self):
        self.cursor_visible = not self.cursor_visible
        self.update()

    def _on_glow_intensity_changed(self, intensity: float):
        self._glow_intensity = max(0.0, min(1.0, float(intensity)))
        self.update()

    def _animate_cursor_glow(self):
        """Pulse the cursor glow alpha for a breathing neon effect."""
        step = 0.03 * self._cursor_glow_direction
        self._cursor_glow_alpha += step
        if self._cursor_glow_alpha <= 0.4:
            self._cursor_glow_direction = 1
        elif self._cursor_glow_alpha >= 1.0:
            self._cursor_glow_direction = -1
        # Don't call update() here — blink timer handles repaints

    # ── Background image ─────────────────────────────────────────────────

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

    # ── Resize ───────────────────────────────────────────────────────────

    def _resize_backend(self):
        if self.char_width <= 0 or self.char_height <= 0:
            return
        avail_w = max(0, self.width() - self.MARGIN_X * 2)
        avail_h = max(0, self.height() - self.MARGIN_Y * 2)
        cols = max(1, avail_w // self.char_width)
        rows = max(1, avail_h // self.char_height)
        self.backend.resize(cols, rows)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._resize_backend()

    # ── Paint ────────────────────────────────────────────────────────────

    def paintEvent(self, event):
        painter = QPainter(self)
        if not painter.isActive():
            return

        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # ── Background ──
        bg = QColor(self.theme.background)
        bg.setAlphaF(config.opacity)
        painter.fillRect(self.rect(), bg)

        # ── Background image (if set) ──
        if self._bg_pixmap:
            scaled = self._bg_pixmap.scaled(
                self.size(),
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation,
            )
            x = (self.width() - scaled.width()) // 2
            y = (self.height() - scaled.height()) // 2
            painter.setOpacity(0.15)
            painter.drawPixmap(x, y, scaled)
            painter.setOpacity(1.0)

        painter.setFont(self.term_font)
        screen = self.backend.screen

        # ── Selection range normalization ──
        sel_active = self._sel_start is not None and self._sel_end is not None
        if sel_active:
            sx, sy = self._sel_start
            ex, ey = self._sel_end
            if (sy, sx) > (ey, ex):
                sx, sy, ex, ey = ex, ey, sx, sy
        else:
            sx = sy = ex = ey = -1

        # ── Draw characters ──
        default_char = getattr(screen, "default_char", None)
        for y in range(screen.lines):
            row = screen.buffer[y]
            for x in range(screen.columns):
                char = row.get(x, default_char) if default_char is not None else row.get(x)
                if char is None:
                    continue
                px = self.MARGIN_X + x * self.char_width
                py = self.MARGIN_Y + y * self.char_height

                # Check if this cell is selected
                in_sel = False
                if sel_active:
                    if sy == ey:
                        in_sel = y == sy and sx <= x <= ex
                    else:
                        if y == sy:
                            in_sel = x >= sx
                        elif y == ey:
                            in_sel = x <= ex
                        else:
                            in_sel = sy < y < ey

                # Background
                if in_sel:
                    painter.fillRect(px, py, self.char_width, self.char_height,
                                     QColor(self.theme.selection_bg))
                else:
                    bg_hex = self._color(char.bg, is_bg=True)
                    if bg_hex != self.theme.background:
                        painter.fillRect(px, py, self.char_width, self.char_height,
                                         QColor(bg_hex))

                if char.data == " ":
                    continue

                # Foreground text
                if in_sel:
                    painter.setPen(QColor(self.theme.selection_fg))
                else:
                    fg_hex = self._color(char.fg, is_bg=False)
                    painter.setPen(QColor(fg_hex))

                f = painter.font()
                f.setBold(bool(char.bold))
                f.setItalic(bool(getattr(char, "italics", False)))
                f.setUnderline(bool(getattr(char, "underscore", False)))
                painter.setFont(f)

                painter.drawText(px, py + self.ascent + self._baseline_adjust, char.data)

        # ── Cursor rendering ──
        if self.cursor_visible and self.hasFocus():
            cx = self.MARGIN_X + screen.cursor.x * self.char_width
            cy = self.MARGIN_Y + screen.cursor.y * self.char_height

            cursor_col = QColor(self.theme.cursor_color)
            shape = config.cursor_shape

            if config.animations_enabled:
                # Outer glow (pulsing)
                glow = QColor(self.theme.cursor_color)
                glow.setAlphaF(self._cursor_glow_alpha * (0.16 + 0.22 * self._glow_intensity))
                painter.fillRect(
                    cx - 3, cy - 3,
                    self.char_width + 6, self.char_height + 6,
                    glow,
                )
                # Inner glow
                glow.setAlphaF(self._cursor_glow_alpha * (0.22 + 0.33 * self._glow_intensity))
                painter.fillRect(
                    cx - 1, cy - 1,
                    self.char_width + 2, self.char_height + 2,
                    glow,
                )

            painter.setPen(Qt.PenStyle.NoPen)
            cursor_col.setAlphaF(0.85)
            painter.setBrush(cursor_col)

            if shape == "Block":
                painter.setOpacity(0.75)
                painter.drawRoundedRect(
                    QRectF(cx, cy, self.char_width, self.char_height), 2, 2
                )
                painter.setOpacity(1.0)
            elif shape == "Underline":
                painter.drawRoundedRect(
                    QRectF(cx, cy + self.char_height - 3, self.char_width, 3), 1, 1
                )
            else:  # Beam
                painter.drawRoundedRect(
                    QRectF(cx, cy, 2, self.char_height), 1, 1
                )

        painter.end()

    # ── Colour mapping ───────────────────────────────────────────────────

    _PYTE_NAMES = {
        "black": 0, "red": 1, "green": 2, "brown": 3,
        "blue": 4, "magenta": 5, "cyan": 6, "white": 7,
        "lightblack": 8, "lightred": 9, "lightgreen": 10, "lightbrown": 11,
        "lightblue": 12, "lightmagenta": 13, "lightcyan": 14, "lightwhite": 15,
    }

    def _color(self, name, is_bg=False) -> str:
        if name == "default" or name is None:
            return self.theme.background if is_bg else self.theme.foreground
        if isinstance(name, str) and name in self._PYTE_NAMES:
            idx = self._PYTE_NAMES[name]
            if idx < len(self.theme.ansi_palette):
                return self.theme.ansi_palette[idx]
        if isinstance(name, str) and name.startswith("#"):
            return name
        if isinstance(name, str) and len(name) == 6:
            try:
                int(name, 16)
                return "#" + name
            except ValueError:
                pass
        return self.theme.background if is_bg else self.theme.foreground

    # ── Keyboard input ───────────────────────────────────────────────────

    def keyPressEvent(self, event: QKeyEvent):
        key = event.key()
        mods = event.modifiers()
        text = event.text()

        # Clipboard shortcuts
        ctrl_shift = (Qt.KeyboardModifier.ControlModifier |
                      Qt.KeyboardModifier.ShiftModifier)
        if mods == ctrl_shift:
            if key == Qt.Key.Key_C:
                self._copy_selection()
                return
            elif key == Qt.Key.Key_V:
                self._paste_clipboard()
                return

        # Key sequences
        seq = {
            Qt.Key.Key_Up: b"\x1b[A",
            Qt.Key.Key_Down: b"\x1b[B",
            Qt.Key.Key_Right: b"\x1b[C",
            Qt.Key.Key_Left: b"\x1b[D",
            Qt.Key.Key_Backspace: b"\x7f",
            Qt.Key.Key_Return: b"\r",
            Qt.Key.Key_Enter: b"\r",
            Qt.Key.Key_Tab: b"\t",
            Qt.Key.Key_Escape: b"\x1b",
            Qt.Key.Key_Delete: b"\x1b[3~",
            Qt.Key.Key_Home: b"\x1b[H",
            Qt.Key.Key_End: b"\x1b[F",
            Qt.Key.Key_PageUp: b"\x1b[5~",
            Qt.Key.Key_PageDown: b"\x1b[6~",
            Qt.Key.Key_Insert: b"\x1b[2~",
            Qt.Key.Key_F1: b"\x1bOP",
            Qt.Key.Key_F2: b"\x1bOQ",
            Qt.Key.Key_F3: b"\x1bOR",
            Qt.Key.Key_F4: b"\x1bOS",
            Qt.Key.Key_F5: b"\x1b[15~",
            Qt.Key.Key_F6: b"\x1b[17~",
            Qt.Key.Key_F7: b"\x1b[18~",
            Qt.Key.Key_F8: b"\x1b[19~",
            Qt.Key.Key_F9: b"\x1b[20~",
            Qt.Key.Key_F10: b"\x1b[21~",
            Qt.Key.Key_F11: b"\x1b[23~",
            Qt.Key.Key_F12: b"\x1b[24~",
        }.get(key)

        if seq:
            self.backend.write(seq)
        elif (mods & Qt.KeyboardModifier.ControlModifier and
              Qt.Key.Key_A <= key <= Qt.Key.Key_Z):
            self.backend.write(bytes([key - Qt.Key.Key_A + 1]))
        elif text:
            self.backend.write(text.encode("utf-8"))

        # Reset cursor blink on keypress
        if config.animations_enabled:
            self.cursor_visible = True
            self._blink_timer.start(530)

    # ── Mouse selection ──────────────────────────────────────────────────

    def _pixel_to_cell(self, pos) -> tuple:
        """Convert pixel position to (col, row) in the terminal grid."""
        col = max(0, (pos.x() - self.MARGIN_X) // self.char_width)
        row = max(0, (pos.y() - self.MARGIN_Y) // self.char_height)
        return (int(col), int(row))

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self._selecting = True
            cell = self._pixel_to_cell(event.position())
            self._sel_start = cell
            self._sel_end = cell
            self.backend.clear_selection()
            self.update()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        if self._selecting:
            self._sel_end = self._pixel_to_cell(event.position())
            self.update()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton and self._selecting:
            self._selecting = False
            self._sel_end = self._pixel_to_cell(event.position())
            if self._sel_start and self._sel_end:
                self.backend.set_selection(self._sel_start, self._sel_end)
            self.update()
        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        """Double-click to select a word."""
        cell = self._pixel_to_cell(event.position())
        col, row = cell
        screen = self.backend.screen
        sx, sy = col, row
        ex, ey = col, row
        for row_idx in range(sy, ey + 1):
            row = screen.buffer[row_idx]
            start_col = sx if row_idx == sy else 0
            end_col = ex if row_idx == ey else screen.columns - 1
            while start_col > 0 and start_col - 1 in row and row[start_col - 1].data not in (" ", "\t"):
                start_col -= 1
            while end_col < screen.columns - 1 and end_col + 1 in row and row[end_col + 1].data not in (" ", "\t"):
                end_col += 1
            if row_idx == sy:
                sx = start_col
            if row_idx == ey:
                ex = end_col
        self._sel_start = (sx, sy)
        self._sel_end = (ex, ey)
        self.backend.set_selection(self._sel_start, self._sel_end)
        self.update()

    # ── Clipboard ────────────────────────────────────────────────────────

    def _copy_selection(self):
        text = self.backend.get_selected_text()
        if text:
            clipboard = QApplication.clipboard()
            if clipboard:
                clipboard.setText(text)

    def _paste_clipboard(self):
        clipboard = QApplication.clipboard()
        if clipboard:
            text = clipboard.text()
            if text:
                self.backend.write_text(text)

    # ── Drag & Drop ──────────────────────────────────────────────────────

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls() or event.mimeData().hasText():
            event.acceptProposedAction()

    def dropEvent(self, event):
        mime = event.mimeData()
        if mime.hasUrls():
            paths = []
            for url in mime.urls():
                local = url.toLocalFile()
                if local:
                    # Shell-escape spaces
                    paths.append(local.replace(" ", "\\ "))
            if paths:
                self.backend.write_text(" ".join(paths))
        elif mime.hasText():
            self.backend.write_text(mime.text())

    # ── Cleanup ──────────────────────────────────────────────────────────

    def _on_process_exit(self):
        """Called when the shell process exits."""
        pass  # Tab manager handles tab closure

    def cleanup(self):
        self._blink_timer.stop()
        self._glow_timer.stop()
        self.backend.stop()

    def closeEvent(self, event):
        self.cleanup()
        super().closeEvent(event)
