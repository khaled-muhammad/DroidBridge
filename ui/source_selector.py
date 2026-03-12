"""Source selector - device or local folder."""

from pathlib import Path

from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QWidget,
)
from PySide6.QtCore import Signal


class SourceSelector(QWidget):
    """Select source: ADB device or local folder."""

    source_changed = Signal(str, str)  # type, path

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(QLabel("Source:"))
        self.combo = QComboBox()
        self.combo.addItem("Old Device (ADB)", "adb")
        self.combo.addItem("Local Folder", "local")
        self.combo.currentIndexChanged.connect(self._on_type_change)
        layout.addWidget(self.combo)
        self.device_combo = QComboBox()
        self.device_combo.setMinimumWidth(200)
        self.device_combo.addItem("-- Select device --", None)
        layout.addWidget(self.device_combo)
        self.folder_edit = QLineEdit()
        self.folder_edit.setPlaceholderText("Path to /sdcard folder...")
        self.folder_edit.setVisible(False)
        layout.addWidget(self.folder_edit)
        self.browse_btn = QPushButton("Browse...")
        self.browse_btn.setVisible(False)
        self.browse_btn.clicked.connect(self._browse)
        layout.addWidget(self.browse_btn)
        self._update_visibility()

    def set_devices(self, devices: list) -> None:
        """Set available devices for ADB source."""
        self.device_combo.clear()
        self.device_combo.addItem("-- Select device --", None)
        for d in devices:
            self.device_combo.addItem(d.display_name(), d)
        self.device_combo.setCurrentIndex(0)

    def get_source_type(self) -> str:
        """Get 'adb' or 'local'."""
        return self.combo.currentData()

    def get_source_path(self) -> str:
        """Get device serial (adb) or folder path (local)."""
        if self.get_source_type() == "adb":
            dev = self.device_combo.currentData()
            return dev.serial if dev else ""
        return self.folder_edit.text().strip()

    def get_source_base_path(self) -> str:
        """Get base path for indexing. For local, the folder; for ADB, empty (use serial)."""
        if self.get_source_type() == "local":
            return self.folder_edit.text().strip()
        return ""

    def _on_type_change(self) -> None:
        self._update_visibility()
        self._emit_change()

    def _update_visibility(self) -> None:
        is_local = self.get_source_type() == "local"
        self.device_combo.setVisible(not is_local)
        self.folder_edit.setVisible(is_local)
        self.browse_btn.setVisible(is_local)

    def _browse(self) -> None:
        path = QFileDialog.getExistingDirectory(self, "Select /sdcard folder")
        if path:
            self.folder_edit.setText(path)
            self._emit_change()

    def _emit_change(self) -> None:
        self.source_changed.emit(self.get_source_type(), self.get_source_path())
