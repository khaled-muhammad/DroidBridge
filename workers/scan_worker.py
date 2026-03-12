"""Background worker for device and file scanning."""

from PySide6.QtCore import QObject, QThread, Signal

from core.device_scanner import DeviceScanner
from core.file_indexer import FileIndexer
from models import DeviceInfo, FileRecord


class ScanWorker(QObject):
    """Worker for scanning devices and indexing files."""

    devices_ready = Signal(list)  # List[DeviceInfo]
    index_progress = Signal(int, int)  # current, total
    step_started = Signal(str)  # status message for current step
    index_complete = Signal(list)  # List[FileRecord]
    error_occurred = Signal(str)

    def __init__(self):
        super().__init__()
        self.scanner = DeviceScanner()
        self.indexer = FileIndexer(progress_callback=self._on_progress)

    def _on_progress(self, current: int, total: int):
        self.index_progress.emit(current, total)

    def scan_devices(self) -> None:
        """Scan for connected devices."""
        try:
            devices = self.scanner.scan()
            self.devices_ready.emit(devices)
        except Exception as e:
            self.error_occurred.emit(str(e))

    def index_local(self, base_path: str) -> None:
        """Index local folder."""
        try:
            self.step_started.emit("Step 1: Scanning local folder...")
            records = self.indexer.index_local_folder(base_path)
            self.index_complete.emit(records)
        except Exception as e:
            self.error_occurred.emit(str(e))

    def index_adb(self, serial: str) -> None:
        """Index ADB device."""
        try:
            self.step_started.emit("Step 1: Fetching file list from device (this may take a while)...")
            def progress(c, t):
                self.index_progress.emit(c, t)

            records = self.indexer.index_adb_device(serial, progress)
            self.index_complete.emit(records)
        except Exception as e:
            self.error_occurred.emit(str(e))
