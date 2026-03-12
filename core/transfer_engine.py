"""Transfer engine - push archive and extract on device."""

from pathlib import Path
from typing import Optional

from core.adb_manager import ADBManager
from core.extraction_engine import ExtractionEngine
from utils.constants import MIGRATION_TEMP_DIR, SDCARD_PATH
from utils.logger import get_logger

logger = get_logger(__name__)


class TransferEngine:
    """Handles archive push and extraction on destination device."""

    def __init__(self, adb: Optional[ADBManager] = None):
        self.adb = adb or ADBManager()
        self.extractor = ExtractionEngine()

    def transfer_archive(
        self,
        local_archive_path: str,
        dest_serial: Optional[str] = None,
    ) -> bool:
        """
        Push archive to device and extract.
        Steps: create temp dir, push, extract, cleanup.
        """
        remote_archive = f"{MIGRATION_TEMP_DIR}/migration.tar"
        # Create temp dir
        if not self.adb.create_remote_dir(MIGRATION_TEMP_DIR, dest_serial):
            logger.error("Failed to create temp dir on device")
            return False
        # Push
        code, stdout, stderr = self.adb.push_file(
            local_archive_path, remote_archive, dest_serial
        )
        if code != 0:
            logger.error("Push failed: %s", stderr)
            return False
        logger.info("Archive pushed successfully")
        # Extract - use adb shell tar
        extract_ok = self.extractor.extract_on_device(
            remote_archive, SDCARD_PATH, dest_serial, self.adb
        )
        if not extract_ok:
            logger.error("Extraction failed")
            return False
        # Cleanup
        self.adb.remove_remote_file(remote_archive, dest_serial)
        self.adb.run_shell(f'rmdir "{MIGRATION_TEMP_DIR}" 2>/dev/null', dest_serial)
        logger.info("Transfer complete")
        return True
