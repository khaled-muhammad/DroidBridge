"""File indexing for local and ADB sources."""

import os
from pathlib import Path
from typing import Callable, List, Optional

from models import FileRecord
from core.adb_manager import ADBManager
from utils.constants import SDCARD_PATH
from utils.file_utils import get_mime_type
from utils.logger import get_logger

logger = get_logger(__name__)


class FileIndexer:
    """Indexes files from local folder or ADB device."""

    def __init__(self, progress_callback: Optional[Callable[[int, int], None]] = None):
        self.progress_callback = progress_callback
        self.adb = ADBManager()

    def index_local_folder(
        self,
        base_path: str,
        relative_to: Optional[str] = None,
    ) -> List[FileRecord]:
        """Index files from local folder using os.walk. Single pass, emits progress as we go."""
        base = Path(base_path).resolve()
        if not base.exists() or not base.is_dir():
            logger.error("Invalid base path: %s", base_path)
            return []

        records = []
        root_for_rel = Path(relative_to or base_path).resolve()
        processed = 0
        for dirpath, _, filenames in os.walk(base):
            for name in filenames:
                full_path = Path(dirpath) / name
                try:
                    stat = full_path.stat()
                    rel = full_path.relative_to(root_for_rel)
                    rel_str = str(rel).replace("\\", "/")
                    record = FileRecord(
                        path=rel_str,
                        size=stat.st_size,
                        modified_time=stat.st_mtime,
                        mime_type=get_mime_type(name),
                        source="local",
                    )
                    records.append(record)
                except (OSError, ValueError) as e:
                    logger.debug("Skip %s: %s", full_path, e)
                processed += 1
                if self.progress_callback and processed % 50 == 0:
                    self.progress_callback(processed, 0)  # 0 = total unknown
        if self.progress_callback and processed > 0:
            self.progress_callback(processed, processed)
        return records

    def index_adb_device(
        self,
        serial: Optional[str] = None,
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> List[FileRecord]:
        """Index files from ADB device using find."""
        if progress_callback:
            progress_callback(0, 1)  # "Fetching file list..."
        files_info = self.adb.list_files_recursive(SDCARD_PATH, serial)
        records = []
        total = len(files_info)
        for i, (path, size, mtime) in enumerate(files_info):
            record = FileRecord(
                path=path,
                size=size,
                modified_time=mtime,
                mime_type=get_mime_type(path),
                source="adb",
            )
            records.append(record)
            if progress_callback and (i + 1) % 100 == 0:
                progress_callback(i + 1, total)
        if progress_callback and total > 0:
            progress_callback(total, total)
        return records
