# NS2 Terminal

A next-generation, premium futuristic terminal emulator for Linux, built with Python + PyQt6 and `pyte`.

## Features

- **Glassmorphism UI:** Translucency, soft glow effects, and deep space aesthetics.
- **Visual Effects:** 60fps animated cursor, sliding tab indicators, and an optional 30-particle floating overlay.
- **Core Engine:** Rock-solid PTY integration via `pty` with `pyte` rendering (VT100/ANSI).
- **Advanced UX:** Drag-and-drop file paths, click-to-copy, fuzzy-search Command Palette (Ctrl+Shift+P), and collapsible quick-action sidebar.
- **Multiplexing:** Built-in tabs and deeply nested split panes (Horizontal/Vertical).
- **Customization:** 4 premium themes (Blue Glass, Matrix Green, Purple Cyber, Minimal Light) + full settings panel.

## Prerequisites

- Linux OS (tested on Ubuntu/Debian, Wayland & X11)
- Python 3.10+
- PyQt6
- pyte

## Installation (Local Dev)

1. Clone the repository and setup the virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
2. Run the application:
   ```bash
   cd ns2_terminal
   python main.py
   ```

## Installation (System-Wide `.deb`)

If you want to install it system-wide with a desktop icon:

1. Navigate to the `packaging` directory:
   ```bash
   cd ns2_terminal/packaging
   ```
2. Run the build script:
   ```bash
   chmod +x build_deb.sh
   ./build_deb.sh
   ```
3. Install the `.deb` file:
   ```bash
   sudo apt install ./build_deb/ns2-terminal_2.0.0_amd64.deb
   ```

## Keyboard Shortcuts

| Shortcut       | Action               |
| -------------- | -------------------- |
| `Ctrl+Shift+T` | New Tab              |
| `Ctrl+Shift+W` | Close Tab            |
| `Ctrl+Shift+H` | Split Horizontal     |
| `Ctrl+Shift+E` | Split Vertical       |
| `Ctrl+Shift+P` | Open Command Palette |
| `Ctrl+Shift+S` | Open Settings        |
| `Ctrl+Shift+B` | Toggle Sidebar       |
| `Ctrl+Alt+M`   | Minimize Window      |
| `Ctrl+Shift+C` | Copy Selection       |
| `Ctrl+Shift+V` | Paste Clipboard      |
| `F11`          | Toggle Fullscreen    |

## Set as Default Terminal

If installed system-wide via `.deb`, open your window manager's keyboard shortcut settings (e.g., in GNOME, KDE, or Hyprland) and map your terminal launch bind to `ns2-terminal`.
