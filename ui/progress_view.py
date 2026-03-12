"""Progress bar and status display."""

from PySide6.QtWidgets import (
    QLabel,
    QProgressBar,
    QVBoxLayout,
    QWidget,
)


class ProgressView(QWidget):
    """Shows migration progress."""

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)
        self.status_label = QLabel("Ready")
        layout.addWidget(self.status_label)
        self.speed_label = QLabel("")
        self.speed_label.setVisible(False)
        layout.addWidget(self.speed_label)
        self.file_label = QLabel("")
        self.file_label.setVisible(False)
        layout.addWidget(self.file_label)

    def set_progress(self, value: int, maximum: int = 100) -> None:
        """Set progress bar value."""
        self.progress_bar.setMaximum(maximum)
        self.progress_bar.setValue(value)

    def set_status(self, text: str) -> None:
        """Set status text."""
        self.status_label.setText(text)

    def set_phase(self, phase: str, current: int, total: int) -> None:
        """Update for migration phase."""
        if total > 0:
            pct = int(100 * current / total)
            self.progress_bar.setValue(pct)
            self.progress_bar.setMaximum(100)
        else:
            # Total unknown - show indeterminate / busy
            self.progress_bar.setMaximum(0)
            self.progress_bar.setValue(0)
        if total > 0:
            self.status_label.setText(f"{phase}: {current:,} / {total:,}")
        else:
            self.status_label.setText(f"{phase}: {current:,} files...")
