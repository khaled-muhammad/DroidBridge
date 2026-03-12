"""Duplicate file detection using size + partial hash."""

from typing import Dict, List, Optional, Set, Tuple

from models import FileRecord
from utils.logger import get_logger

logger = get_logger(__name__)


class DuplicateDetector:
    """Detects duplicate files by size and partial hash."""

    def find_duplicates(
        self,
        records: List[FileRecord],
        dest_hash_index: Optional[Set[Tuple[int, str]]] = None,
    ) -> Tuple[List[FileRecord], Set[str]]:
        """
        Find duplicates. Returns (unique_records, duplicate_paths).
        Two files are duplicates when size and partial_hash match.
        If dest_hash_index provided (set of (size, hash)), skip files already on dest.
        """
        dest_hash_index = dest_hash_index or set()
        seen: Dict[Tuple[int, str], str] = {}  # (size, hash) -> first path
        duplicates: Set[str] = set()

        for record in records:
            if not record.partial_hash:
                continue
            key = (record.size, record.partial_hash)
            # Skip if already on destination
            if key in dest_hash_index:
                duplicates.add(record.path)
                continue
            # Skip if duplicate within source
            if key in seen:
                duplicates.add(record.path)
                continue
            seen[key] = record.path

        unique = [r for r in records if r.path not in duplicates]
        return unique, duplicates

    def build_dest_hash_index(
        self,
        records: List[FileRecord],
    ) -> Set[Tuple[int, str]]:
        """Build set of (size, hash) for destination files."""
        return {
            (r.size, r.partial_hash)
            for r in records
            if r.partial_hash
        }
