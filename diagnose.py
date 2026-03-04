#!/usr/bin/env python3
"""Step-by-step test to find the exact SIGSEGV trigger."""
import sys, os, signal

print("=== NASA Cyber Terminal SIGSEGV Diagnostic ===", flush=True)
print(f"Session: {os.environ.get('XDG_SESSION_TYPE','?')}", flush=True)
print()

from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, QTimer

app = QApplication(sys.argv)

# --- Test A: FramelessWindowHint ---
print("Test A: FramelessWindowHint...", flush=True)
w = QMainWindow()
w.setWindowFlags(Qt.WindowType.FramelessWindowHint)
w.resize(300, 200)
w.show()
app.processEvents()
w.close()
print("  OK", flush=True)

# --- Test B: TranslucentBackground ---
print("Test B: WA_TranslucentBackground...", flush=True)
w2 = QMainWindow()
w2.setWindowFlags(Qt.WindowType.FramelessWindowHint)
w2.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
w2.resize(300, 200)
w2.show()
app.processEvents()
w2.close()
print("  OK", flush=True)

# --- Test C: pty.openpty ---
print("Test C: pty.openpty()...", flush=True)
import pty
master, slave = pty.openpty()
os.close(master)
os.close(slave)
print("  OK", flush=True)

# --- Test D: pty.fork ---
print("Test D: pty.fork()...", flush=True)
pid, fd = pty.fork()
if pid == 0:
    # child — just exit
    os._exit(0)
else:
    os.waitpid(pid, 0)
    os.close(fd)
print("  OK", flush=True)

# --- Test E: pty.fork + QSocketNotifier ---
print("Test E: pty.fork + QSocketNotifier + shell...", flush=True)
import fcntl, struct, termios
from PyQt6.QtCore import QSocketNotifier

pid2, fd2 = pty.fork()
if pid2 == 0:
    shell = os.environ.get("SHELL", "/bin/bash")
    env = os.environ.copy()
    env["TERM"] = "xterm-256color"
    os.execvpe(shell, [shell], env)
else:
    flags = fcntl.fcntl(fd2, fcntl.F_GETFL)
    fcntl.fcntl(fd2, fcntl.F_SETFL, flags | os.O_NONBLOCK)
    
    got_data = [False]
    def on_read():
        try:
            data = os.read(fd2, 4096)
            if data:
                got_data[0] = True
        except:
            pass
    
    notifier = QSocketNotifier(fd2, QSocketNotifier.Type.Read)
    notifier.activated.connect(on_read)
    
    # Let it run for 500ms
    QTimer.singleShot(500, app.quit)
    app.exec()
    
    notifier.setEnabled(False)
    os.kill(pid2, signal.SIGTERM)
    os.waitpid(pid2, 0)
    os.close(fd2)
    print(f"  OK (got shell data: {got_data[0]})", flush=True)

# --- Test F: pyte ---
print("Test F: pyte screen...", flush=True)
import pyte
screen = pyte.HistoryScreen(80, 24, history=1000)
stream = pyte.ByteStream(screen)
stream.feed(b"Hello World\r\n")
print(f"  OK (screen line 0: '{screen.display[0].strip()}')", flush=True)

print()
print("=== ALL TESTS PASSED ===", flush=True)
print("The individual components work. The crash is in how they combine.", flush=True)
print("Try: QT_QPA_PLATFORM=xcb venv/bin/python main.py", flush=True)
