"""
NS2 Terminal – Split Pane Manager
==================================
QSplitter-based container for tiling terminal widgets horizontally
and vertically within a single tab.
"""

from PyQt6.QtWidgets import QSplitter
from PyQt6.QtCore import Qt
from ns2_terminal.ui.terminal_widget import TerminalWidget


class SplitPane(QSplitter):
    """
    A tree of QSplitters managing split terminals inside a single tab.
    Supports recursive horizontal/vertical splitting.
    """

    def __init__(self, parent=None):
        super().__init__(Qt.Orientation.Horizontal, parent)
        self.setHandleWidth(2)
        self.setChildrenCollapsible(False)

        # Splitter handle styling
        self.setStyleSheet("""
            QSplitter::handle {
                background: rgba(176, 196, 222, 0.06);
            }
            QSplitter::handle:hover {
                background: rgba(0, 191, 255, 0.25);
            }
        """)

        # Start with one terminal
        self.add_terminal()

    def add_terminal(self) -> TerminalWidget:
        """Add a new TerminalWidget to this splitter."""
        term = TerminalWidget(self)
        self.addWidget(term)
        term.setFocus()
        return term

    def split_current(self, orientation):
        """
        Split the currently focused terminal.
        If orientation matches, add alongside; otherwise, wrap in a sub-splitter.
        """
        focused = self._find_focused_terminal()
        term = TerminalWidget(self)

        if focused and focused.parent() == self:
            idx = self.indexOf(focused)
            if self.orientation() == orientation:
                self.insertWidget(idx + 1, term)
            else:
                # Wrap in a nested splitter
                nested = QSplitter(orientation, self)
                nested.setHandleWidth(2)
                nested.setChildrenCollapsible(False)
                nested.setStyleSheet(self.styleSheet())
                self.replaceWidget(idx, nested)
                nested.addWidget(focused)
                nested.addWidget(term)
        else:
            self.addWidget(term)

        term.setFocus()
        return term

    def split_horizontal(self):
        """Split adding a terminal to the right."""
        self.split_current(Qt.Orientation.Horizontal)

    def split_vertical(self):
        """Split adding a terminal below."""
        self.split_current(Qt.Orientation.Vertical)

    def _find_focused_terminal(self):
        """Walk widget tree to find the focused TerminalWidget."""
        w = self.focusWidget()
        if isinstance(w, TerminalWidget):
            return w
        return None

    def cleanup_all(self):
        """Stop all terminal backends in this pane tree."""
        for i in range(self.count()):
            child = self.widget(i)
            if isinstance(child, TerminalWidget):
                child.cleanup()
            elif isinstance(child, QSplitter):
                self._cleanup_splitter(child)

    def _cleanup_splitter(self, splitter):
        for i in range(splitter.count()):
            child = splitter.widget(i)
            if isinstance(child, TerminalWidget):
                child.cleanup()
            elif isinstance(child, QSplitter):
                self._cleanup_splitter(child)
