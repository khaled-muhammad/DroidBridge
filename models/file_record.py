"""File record model for indexed files."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class FileRecord:
    """Represents an indexed file from source (ADB or local folder)."""

    path: str
    size: int
    modified_time: float
    partial_hash: Optional[str] = None
    mime_type: Optional[str] = None
    source: str = "unknown"  # "adb" or "local"

    def __hash__(self) -> int:
        return hash((self.path, self.size, self.partial_hash))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, FileRecord):
            return False
        return (
            self.path == other.path
            and self.size == other.size
            and self.partial_hash == other.partial_hash
        )
