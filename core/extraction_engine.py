"""Extraction engine - safe extraction with path validation."""

from typing import Optional

from core.path_mapper import PathMapper
from utils.logger import get_logger

logger = get_logger(__name__)


class ExtractionEngine:
    """Handles safe extraction on device."""

    def __init__(self):
        self.path_mapper = PathMapper()

    def extract_on_device(
        self,
        archive_path: str,
        extract_to: str,
        serial: Optional[str] = None,
        adb=None,
    ) -> tuple[bool, str]:
        """
        Extract tar archive on device using adb shell tar -xf.
        Returns (success, error_message).
        """
        if adb is None:
            from core.adb_manager import ADBManager
            adb = ADBManager()
        cmd = f'cd "{extract_to}" && tar -xf "{archive_path}"'
        code, stdout, stderr = adb.run_shell(cmd, serial, timeout=600)
        if code != 0:
            err = stderr.strip() or stdout.strip() or "Unknown error"
            logger.error("Extract failed: %s", err)
            return False, err
        return True, ""

    def validate_archive_path(self, path: str) -> bool:
        """Validate path before extraction - no traversal, under sdcard."""
        return self.path_mapper.validate_extraction_path(path)
