"""Device controller - handles device selection and refresh."""

from PySide6.QtCore import QObject

from core.device_scanner import DeviceScanner
from utils.logger import get_logger

logger = get_logger(__name__)


class DeviceController(QObject):
    """Manages device-related operations."""

    def __init__(self):
        super().__init__()
        self.scanner = DeviceScanner()

    def refresh_devices(self):
        """Refresh list of connected devices."""
        return self.scanner.scan()
