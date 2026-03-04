# NASA Cyber Terminal

A custom, futuristic, premium terminal emulator for Linux built with Python + PyQt6 and `pyte`.

## Features

- **Modern UI:** Glassmorphism, animated cursor, translucent background, custom themes.
- **True Terminal Backend:** Powered by `pty` scaling and complete VT100/ANSI emulation with `pyte`.
- **Multiplexing inside:** Built-in Tab support and Split Panes (Horizontal/Vertical).
- **Customizable:** Settings panel for theme, opacity, font, cursive, and animations.
- **Cool Animations:** Fade-in splash screen and startup sequence.

## Prerequisites

- Linux OS (tested on Ubuntu/Debian)
- Python 3.10+
- PyQt6
- pyte

## Installation (Local Dev)

1. Clone the repository
2. Set up virtual environment
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
3. Run the application
   ```bash
   python main.py
   ```

## Installation (System-Wide via .deb)

1. Navigate to the `packaging` directory.
2. Make script executable and run it:
   ```bash
   chmod +x build_deb.sh
   ./build_deb.sh
   ```
3. Install the resulting `.deb` package:
   ```bash
   sudo apt install ./build_deb/nasa-cyber-terminal_1.0.0_amd64.deb
   ```

## Keyboard Shortcuts

| Shortcut       | Action                          |
| -------------- | ------------------------------- |
| `Ctrl+Shift+C` | Copy selection (WIP in backend) |
| `Ctrl+Shift+V` | Paste (WIP in backend)          |
| `Ctrl+Shift+T` | New tab                         |
| `Ctrl+Shift+W` | Close tab                       |
| `Ctrl+Shift+H` | Split horizontal                |
| `Ctrl+Shift+E` | Split vertical                  |
| `F11`          | Toggle fullscreen               |
| `Ctrl+Shift+S` | Open settings                   |
| `Ctrl+Alt+M`   | Minimize window                 |

## Set as Default Terminal

If installed system-wide via `.deb`, open your terminal shortcut settings in your desktop environment (e.g., GNOME/KDE) and set the custom command to `nasa-cyber-terminal` instead of `gnome-terminal` or `konsole`.
