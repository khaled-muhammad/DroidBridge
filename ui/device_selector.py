"""Device selector dropdown component."""

from PySide6.QtWidgets import QComboBox, QHBoxLayout, QLabel, QWidget
from PySide6.QtCore import Signal

from models import DeviceInfo


class DeviceSelector(QWidget):
    """Dropdown for selecting Android device."""

    device_changed = Signal(object)  # DeviceInfo or None

    def __init__(self, label: str = "Device", parent=None):
        super().__init__(parent)
        self._devices: list[DeviceInfo] = []
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(QLabel(label + ":"))
        self.combo = QComboBox()
        self.combo.setMinimumWidth(250)
        self.combo.currentIndexChanged.connect(self._on_change)
        layout.addWidget(self.combo, 1)

    def set_devices(self, devices: list[DeviceInfo]) -> None:
        """Populate dropdown with devices."""
        self._devices = devices
        self.combo.clear()
        self.combo.addItem("-- Select --", None)
        for d in devices:
            self.combo.addItem(d.display_name(), d)
        self.combo.setCurrentIndex(0)

    def get_selected(self) -> DeviceInfo | None:
        """Get currently selected device."""
        return self.combo.currentData()

    def _on_change(self, _index: int) -> None:
        self.device_changed.emit(self.get_selected())
