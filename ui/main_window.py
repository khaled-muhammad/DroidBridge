"""Main application window."""

from pathlib import Path

from PySide6.QtWidgets import (
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSplitter,
    QVBoxLayout,
    QWidget,
)
from PySide6.QtCore import Qt, Slot

from ui.device_selector import DeviceSelector
from ui.source_selector import SourceSelector
from ui.migration_preview import MigrationPreview
from ui.progress_view import ProgressView
from ui.log_view import LogView
from controllers.migration_controller import MigrationController


class MainWindow(QMainWindow):
    """DroidBridge - main window."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("DroidBridge")
        self.setMinimumSize(700, 600)
        self.resize(800, 700)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # Source section
        source_widget = QWidget()
        sl = QVBoxLayout(source_widget)
        self.source_selector = SourceSelector()
        sl.addWidget(self.source_selector)
        layout.addWidget(source_widget)

        # Destination
        dest_widget = QWidget()
        dl = QVBoxLayout(dest_widget)
        self.dest_selector = DeviceSelector("Destination")
        dl.addWidget(self.dest_selector)
        layout.addWidget(dest_widget)

        # Analyze button
        self.analyze_btn = QPushButton("Analyze Storage")
        self.analyze_btn.clicked.connect(self._on_analyze)
        layout.addWidget(self.analyze_btn)

        # Migration summary
        self.preview = MigrationPreview()
        layout.addWidget(self.preview)

        # Start migration
        self.start_btn = QPushButton("Start Migration")
        self.start_btn.setEnabled(False)
        self.start_btn.clicked.connect(self._on_start)
        layout.addWidget(self.start_btn)

        # Progress
        self.progress = ProgressView()
        layout.addWidget(self.progress)

        # Log
        self.log_view = LogView()
        layout.addWidget(self.log_view)

        self.controller = MigrationController(self)
        self.controller.setup()
        self._current_phase = ""

    def _on_analyze(self) -> None:
        self.controller.analyze()

    def _on_start(self) -> None:
        self.controller.start_migration()

    @Slot(str)
    def on_step_update(self, msg: str) -> None:
        """Called from worker via queued connection - runs in main thread."""
        if getattr(self, "_step_message_override", None):
            msg = self._step_message_override
            del self._step_message_override
        self.log_view.append(msg)
        self.progress.set_status(msg)

    @Slot(int, int)
    def on_progress_update(self, current: int, total: int) -> None:
        """Called from worker via queued connection - runs in main thread."""
        self.progress.set_phase(self._current_phase, current, total)

    @Slot(str, int, int)
    def on_migration_progress(self, phase: str, current: int, total: int) -> None:
        """Called from migration worker via queued connection - runs in main thread."""
        self.progress.set_phase(phase, current, total)
