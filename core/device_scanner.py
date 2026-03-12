"""Device scanning and detection."""

from typing import List

from models import DeviceInfo
from core.adb_manager import ADBManager
from utils.logger import get_logger

logger = get_logger(__name__)


class DeviceScanner:
    """Scans for connected Android devices."""

    def __init__(self):
        self.adb = ADBManager()

    def scan(self) -> List[DeviceInfo]:
        """Scan for connected devices."""
        devices = self.adb.get_devices()
        logger.info("Found %d device(s)", len(devices))
        return devices
