"""Conflict resolution for destination files."""

from typing import Dict, List, Optional, Tuple

from models import FileRecord
from utils.file_utils import get_conflict_path
from utils.logger import get_logger

logger = get_logger(__name__)


class ConflictResolver:
    """Resolves conflicts when file exists on destination with different content."""

    def resolve_conflicts(
        self,
        files_to_transfer: List[FileRecord],
        dest_index: Dict[str, Tuple[int, str]],  # path -> (size, hash)
    ) -> Tuple[List[Tuple[str, str]], List[FileRecord]]:
        """
        Check each file against destination index.
        Same hash -> skip (handled by duplicate detector).
        Different hash, same path -> rename to filename (migrated).ext
        Returns (conflict_mappings: [(original_dest, new_dest)], final_file_list).
        """
        conflict_mappings: List[Tuple[str, str]] = []
        final_files: List[FileRecord] = []

        for record in files_to_transfer:
            dest_info = dest_index.get(record.path)
            if not dest_info:
                final_files.append(record)
                continue
            dest_size, dest_hash = dest_info
            # Same file (size + hash) - duplicate detector should have skipped
            if dest_size == record.size and dest_hash == record.partial_hash:
                continue
            # Different file, same name -> rename
            new_path = get_conflict_path(record.path)
            conflict_mappings.append((record.path, new_path))
            modified_record = FileRecord(
                path=new_path,
                size=record.size,
                modified_time=record.modified_time,
                partial_hash=record.partial_hash,
                mime_type=record.mime_type,
                source=record.source,
            )
            final_files.append(modified_record)

        return conflict_mappings, final_files
