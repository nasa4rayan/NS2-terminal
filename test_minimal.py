"""Minimal test to find the SIGSEGV root cause."""
import sys
print("Step 1: Importing PyQt6...")
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel
from PyQt6.QtCore import Qt
print("Step 2: PyQt6 imported OK")

print("Step 3: Creating QApplication...")
app = QApplication(sys.argv)
print("Step 4: QApplication created OK")

print("Step 5: Creating basic window...")
win = QMainWindow()
win.setWindowTitle("Test")
win.resize(400, 300)
label = QLabel("Hello from NASA Cyber Terminal!")
label.setAlignment(Qt.AlignmentFlag.AlignCenter)
win.setCentralWidget(label)
print("Step 6: Window created OK")

print("Step 7: Showing window...")
win.show()
print("Step 8: Window shown — if you see this, basic Qt works!")

sys.exit(app.exec())
