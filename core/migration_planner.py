"""Migration planning - builds transfer plan from source/dest indexes."""

import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from models import FileRecord, MigrationPlan
from core.duplicate_detector import DuplicateDetector
from core.conflict_resolver import ConflictResolver
from core.path_mapper import PathMapper
from utils.constants import MIGRATION_PLAN_FILE
from utils.file_utils import format_size
from utils.logger import get_logger

logger = get_logger(__name__)

# Approximate transfer speed (bytes/sec) for archive push - conservative estimate
ESTIMATED_SPEED_BPS = 5 * 1024 * 1024  # 5 MB/s


class MigrationPlanner:
    """Builds migration plan from source and destination indexes."""

    def __init__(self):
        self.duplicate_detector = DuplicateDetector()
        self.conflict_resolver = ConflictResolver()
        self.path_mapper = PathMapper()

    def create_plan(
        self,
        source_records: List[FileRecord],
        dest_records: List[FileRecord],
        source_type: str,
        source_path: str,
        destination_serial: str,
        use_media_mapping: bool = True,
    ) -> MigrationPlan:
        """
        Create migration plan from source and destination file records.
        """
        # Build dest index: path -> (size, hash)
        dest_index: Dict[str, Tuple[int, str]] = {
            r.path: (r.size, r.partial_hash or "")
            for r in dest_records
            if r.partial_hash
        }
        dest_hash_index = self.duplicate_detector.build_dest_hash_index(dest_records)

        # Find duplicates (skip files already on dest or duplicate in source)
        unique_records, duplicates = self.duplicate_detector.find_duplicates(
            source_records, dest_hash_index
        )

        # Resolve conflicts (rename when dest has different file)
        conflict_mappings, files_to_transfer = self.conflict_resolver.resolve_conflicts(
            unique_records, dest_index
        )

        # Apply path mapping for media organization
        if use_media_mapping:
            mapped = []
            for r in files_to_transfer:
                new_path = self.path_mapper.map_path(r.path)
                if new_path != r.path:
                    r = FileRecord(
                        path=new_path,
                        size=r.size,
                        modified_time=r.modified_time,
                        partial_hash=r.partial_hash,
                        mime_type=r.mime_type,
                        source=r.source,
                    )
                mapped.append(r)
            files_to_transfer = mapped

        total_size = sum(r.size for r in files_to_transfer)
        estimated_time = total_size / ESTIMATED_SPEED_BPS if total_size else 0

        plan = MigrationPlan(
            files_to_transfer=[r.path for r in files_to_transfer],
            duplicates=list(duplicates),
            conflicts=conflict_mappings,
            total_size=total_size,
            estimated_time_seconds=estimated_time,
            source_type=source_type,
            source_path=source_path,
            destination_serial=destination_serial,
        )
        logger.info(
            "Plan: %d to transfer, %d duplicates, %d conflicts, %s",
            len(plan.files_to_transfer),
            len(plan.duplicates),
            len(plan.conflicts),
            format_size(plan.total_size),
        )
        return plan

    def save_plan(self, plan: MigrationPlan, path: Optional[str] = None) -> str:
        """Save plan to JSON file."""
        filepath = path or MIGRATION_PLAN_FILE
        data = {
            "files_to_transfer": plan.files_to_transfer,
            "duplicates": plan.duplicates,
            "conflicts": plan.conflicts,
            "total_size": plan.total_size,
            "estimated_time_seconds": plan.estimated_time_seconds,
            "source_type": plan.source_type,
            "source_path": plan.source_path,
            "destination_serial": plan.destination_serial,
        }
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        logger.info("Plan saved to %s", filepath)
        return filepath
