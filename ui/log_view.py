"""Log output view."""

from PySide6.QtWidgets import QPlainTextEdit, QVBoxLayout, QWidget


class LogView(QWidget):
    """Scrollable log output."""

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        self.text = QPlainTextEdit()
        self.text.setReadOnly(True)
        self.text.setMaximumBlockCount(10000)
        layout.addWidget(self.text)

    def append(self, message: str) -> None:
        """Append message to log."""
        self.text.appendPlainText(message)
        # Scroll to bottom
        scrollbar = self.text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def clear(self) -> None:
        """Clear log."""
        self.text.clear()
