"""Migration report generation."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from utils.constants import MIGRATION_REPORT_FILE
from utils.logger import get_logger

logger = get_logger(__name__)


class ReportGenerator:
    """Generates migration reports after completion."""

    def generate_report(
        self,
        start_time: datetime,
        end_time: datetime,
        files_scanned: int,
        files_migrated: int,
        duplicates_skipped: int,
        conflicts_resolved: int,
        errors: List[str],
        total_bytes: int,
        output_path: Optional[str] = None,
    ) -> str:
        """Generate and save migration report."""
        duration = (end_time - start_time).total_seconds()
        speed_bps = total_bytes / duration if duration > 0 else 0
        report = {
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "duration_seconds": duration,
            "files_scanned": files_scanned,
            "files_migrated": files_migrated,
            "duplicates_skipped": duplicates_skipped,
            "conflicts_resolved": conflicts_resolved,
            "errors": errors,
            "total_bytes": total_bytes,
            "transfer_speed_bps": speed_bps,
        }
        path = output_path or MIGRATION_REPORT_FILE
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        logger.info("Report saved to %s", path)
        return path
