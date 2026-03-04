"""
NS2 Terminal – Terminal Backend
================================
PTY management with pyte VT100 emulation.
Provides shell I/O, resize, clipboard, and signal handling.
The start() method MUST be called after the Qt event loop is running.
"""

import os
import pty
import signal
import fcntl
import termios
import struct
import pyte
from PyQt6.QtCore import QObject, pyqtSignal, QSocketNotifier


class TerminalBackend(QObject):
    """
    Manages a pseudo-terminal, spawns a shell, and uses pyte for VT100
    emulation with large scrollback buffer and clipboard support.
    """

    # Signals
    screen_updated = pyqtSignal()
    process_exited = pyqtSignal()
    title_changed = pyqtSignal(str)

    def __init__(self, cols: int = 80, rows: int = 24,
                 scrollback: int = 10000, parent=None):
        super().__init__(parent)
        self.cols = cols
        self.rows = rows
        self._scrollback = scrollback

        # pyte screen with history for scrollback
        self.screen = pyte.HistoryScreen(cols, rows, history=scrollback)
        self.screen.set_mode(pyte.modes.LNM)
        self.stream = pyte.ByteStream(self.screen)

        self.master_fd = None
        self.pid = None
        self._notifier = None
        self._alive = False

        # Selection state (for copy support)
        self._selection_start = None  # (col, row)
        self._selection_end = None    # (col, row)

    # ── Lifecycle ────────────────────────────────────────────────────────

    def start(self):
        """Fork a child shell process with a PTY. Call AFTER event loop."""
        self.pid, self.master_fd = pty.fork()

        if self.pid == 0:
            # ── Child process ──
            shell = os.environ.get("SHELL", "/bin/bash")
            env = os.environ.copy()
            env["TERM"] = "xterm-256color"
            env["COLORTERM"] = "truecolor"
            os.chdir(os.path.expanduser("~"))
            os.execvpe(shell, [shell], env)
        else:
            # ── Parent process ──
            self._alive = True

            # Non-blocking reads
            flags = fcntl.fcntl(self.master_fd, fcntl.F_GETFL)
            fcntl.fcntl(self.master_fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)

            # Set initial window size
            self._set_winsize(self.cols, self.rows)

            # Hook into Qt event loop
            self._notifier = QSocketNotifier(
                self.master_fd, QSocketNotifier.Type.Read, self
            )
            self._notifier.activated.connect(self._on_ready_read)

    def stop(self):
        """Kill the child process and clean up resources."""
        self._alive = False
        if self._notifier:
            self._notifier.setEnabled(False)
            self._notifier = None
        if self.pid and self.pid > 0:
            try:
                os.kill(self.pid, signal.SIGTERM)
                os.waitpid(self.pid, os.WNOHANG)
            except (ProcessLookupError, ChildProcessError, OSError):
                pass
        if self.master_fd is not None:
            try:
                os.close(self.master_fd)
            except OSError:
                pass
            self.master_fd = None

    @property
    def is_alive(self) -> bool:
        return self._alive

    # ── I/O ──────────────────────────────────────────────────────────────

    def _on_ready_read(self):
        """Called by QSocketNotifier when data arrives from the PTY."""
        if not self._alive or self.master_fd is None:
            return
        try:
            data = os.read(self.master_fd, 65536)
            if data:
                self.stream.feed(data)
                self.screen_updated.emit()
            else:
                self._handle_exit()
        except BlockingIOError:
            pass
        except OSError:
            self._handle_exit()

    def write(self, data: bytes):
        """Write raw bytes to the shell's stdin."""
        if self._alive and self.master_fd is not None:
            try:
                os.write(self.master_fd, data)
            except OSError:
                pass

    def write_text(self, text: str):
        """Write a UTF-8 string to the shell (convenience for paste/drag-drop)."""
        self.write(text.encode("utf-8"))

    # ── Resize ───────────────────────────────────────────────────────────

    def resize(self, cols: int, rows: int):
        """Resize the pyte screen and notify the PTY of new dimensions."""
        if cols == self.cols and rows == self.rows:
            return
        self.cols = cols
        self.rows = rows
        self.screen.resize(rows, cols)
        self._set_winsize(cols, rows)

    def _set_winsize(self, cols: int, rows: int):
        if self.master_fd is not None:
            winsize = struct.pack("HHHH", rows, cols, 0, 0)
            try:
                fcntl.ioctl(self.master_fd, termios.TIOCSWINSZ, winsize)
            except OSError:
                pass

    # ── Selection / Clipboard ────────────────────────────────────────────

    def set_selection(self, start: tuple, end: tuple):
        """Set the text selection range as (col, row) tuples."""
        self._selection_start = start
        self._selection_end = end

    def clear_selection(self):
        """Clear the current text selection."""
        self._selection_start = None
        self._selection_end = None

    def get_selected_text(self) -> str:
        """Extract selected text from the pyte screen buffer."""
        if not self._selection_start or not self._selection_end:
            return ""

        sx, sy = self._selection_start
        ex, ey = self._selection_end

        # Normalize order (top-left to bottom-right)
        if (sy, sx) > (ey, ex):
            sx, sy, ex, ey = ex, ey, sx, sy

        lines = []
        screen = self.screen

        for row_idx in range(sy, ey + 1):
            if row_idx >= len(screen.buffer):
                break
            row = screen.buffer[row_idx]
            start_col = sx if row_idx == sy else 0
            end_col = ex if row_idx == ey else screen.columns - 1

            chars = []
            for col_idx in range(start_col, end_col + 1):
                if col_idx in row:
                    chars.append(row[col_idx].data)
                else:
                    chars.append(" ")
            lines.append("".join(chars).rstrip())

        return "\n".join(lines)

    # ── Exit handling ────────────────────────────────────────────────────

    def _handle_exit(self):
        self._alive = False
        if self._notifier:
            self._notifier.setEnabled(False)
        self.process_exited.emit()
