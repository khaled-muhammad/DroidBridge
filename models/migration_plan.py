"""Migration plan model."""

from dataclasses import dataclass, field
from typing import List


@dataclass
class MigrationPlan:
    """Plan for migration execution."""

    files_to_transfer: List[str] = field(default_factory=list)
    duplicates: List[str] = field(default_factory=list)
    conflicts: List[tuple] = field(default_factory=list)  # (source_path, dest_path)
    total_size: int = 0
    estimated_time_seconds: float = 0.0
    source_type: str = "adb"  # "adb" or "local"
    source_path: str = ""
    destination_serial: str = ""
