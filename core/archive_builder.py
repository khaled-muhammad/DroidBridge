"""Archive builder for batch transfer."""

import tarfile
from pathlib import Path
from typing import Callable, List, Optional

from models import FileRecord
from utils.constants import MIGRATION_ARCHIVE_NAME
from utils.logger import get_logger

logger = get_logger(__name__)


class ArchiveBuilder:
    """Creates tar archive of files to migrate."""

    def build_archive(
        self,
        files: List[FileRecord],
        base_path: str,
        output_path: Optional[str] = None,
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> str:
        """
        Build tar archive. Paths stored relative to base (e.g. /sdcard).
        Returns path to created archive.
        """
        out = output_path or f"temp/{MIGRATION_ARCHIVE_NAME}"
        Path(out).parent.mkdir(parents=True, exist_ok=True)

        total = len(files)
        with tarfile.open(out, "w") as tar:
            for i, record in enumerate(files):
                full_path = Path(base_path) / record.path
                if not full_path.exists():
                    logger.warning("Skip missing: %s", full_path)
                    continue
                try:
                    tar.add(str(full_path), arcname=record.path)
                except (OSError, tarfile.TarError) as e:
                    logger.warning("Skip %s: %s", record.path, e)
                if progress_callback and (i + 1) % 100 == 0:
                    progress_callback(i + 1, total)

        logger.info("Archive created: %s (%d files)", out, total)
        return out
