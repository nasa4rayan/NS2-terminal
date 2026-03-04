#!/usr/bin/env python3
"""
NS2 Terminal – Entry Point
============================
Launch the NS2 Terminal application with splash screen,
GPU hints, and platform detection.
"""

import sys
import os


def main():
    # ── Platform detection ──
    # Force XCB on Wayland to avoid PyQt6 translucency crashes
    if os.environ.get("XDG_SESSION_TYPE") == "wayland":
        os.environ.setdefault("QT_QPA_PLATFORM", "xcb")

    # ── GPU acceleration hints ──
    from PyQt6.QtCore import Qt
    from PyQt6.QtGui import QSurfaceFormat
    fmt = QSurfaceFormat()
    fmt.setSwapBehavior(QSurfaceFormat.SwapBehavior.DoubleBuffer)
    fmt.setRenderableType(QSurfaceFormat.RenderableType.OpenGL)
    QSurfaceFormat.setDefaultFormat(fmt)

    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    app.setApplicationName("NS2 Terminal")
    app.setApplicationVersion("2.0.0")
    app.setOrganizationName("NS2")

    # ── App icon ──
    from PyQt6.QtGui import QIcon
    icon_path = os.path.join(os.path.dirname(__file__), "assets", "icon.png")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    # ── Main window (instant launch) ──
    from ns2_terminal.ui.main_window import MainWindow

    main_window = MainWindow()
    main_window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
