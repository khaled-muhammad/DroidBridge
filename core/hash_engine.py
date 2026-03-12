"""Partial hash engine for fast duplicate detection."""

from pathlib import Path
from typing import Optional

import xxhash

from models import FileRecord
from utils.constants import HASH_CHUNK_SIZE
from utils.logger import get_logger

logger = get_logger(__name__)


class HashEngine:
    """Computes partial hashes (first 64KB + last 64KB) for duplicate detection."""

    def compute_partial_hash(self, file_path: str, size: int) -> Optional[str]:
        """
        Compute partial hash: hash(first 64KB + last 64KB).
        For files smaller than 128KB, hash entire file.
        """
        path = Path(file_path)
        if not path.exists() or not path.is_file():
            return None
        try:
            with open(path, "rb") as f:
                if size <= HASH_CHUNK_SIZE * 2:
                    data = f.read()
                    return xxhash.xxh64(data).hexdigest()
                # First chunk
                first = f.read(HASH_CHUNK_SIZE)
                # Seek to last chunk
                if size > HASH_CHUNK_SIZE:
                    f.seek(-HASH_CHUNK_SIZE, 2)
                    last = f.read(HASH_CHUNK_SIZE)
                else:
                    last = b""
                combined = first + last
                return xxhash.xxh64(combined).hexdigest()
        except (OSError, IOError) as e:
            logger.debug("Hash failed for %s: %s", file_path, e)
            return None

    def compute_partial_hash_from_stream(
        self,
        read_first: bytes,
        read_last: bytes,
    ) -> str:
        """Compute hash from pre-read chunks (for ADB stream)."""
        combined = read_first + read_last
        return xxhash.xxh64(combined).hexdigest()

    def update_record_hash(self, record: FileRecord, base_path: str) -> Optional[str]:
        """Update FileRecord with partial hash. Returns hash or None."""
        full_path = Path(base_path) / record.path
        hash_val = self.compute_partial_hash(str(full_path), record.size)
        if hash_val:
            record.partial_hash = hash_val
        return hash_val
