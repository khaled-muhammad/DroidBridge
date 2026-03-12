"""Background worker for file hashing."""

from PySide6.QtCore import QObject, Signal

from core.hash_engine import HashEngine
from models import FileRecord


class HashWorker(QObject):
    """Worker for computing partial hashes on file records."""

    hash_progress = Signal(int, int)  # current, total
    step_started = Signal(str)  # status message
    hash_complete = Signal(list)  # List[FileRecord]
    error_occurred = Signal(str)

    def __init__(self):
        super().__init__()
        self.hash_engine = HashEngine()

    def hash_records(
        self,
        records: list[FileRecord],
        base_path: str,
    ) -> None:
        """Compute partial hashes for records (local files)."""
        try:
            self.step_started.emit("Step 3: Computing file hashes...")
            total = len(records)
            for i, record in enumerate(records):
                self.hash_engine.update_record_hash(record, base_path)
                if (i + 1) % 50 == 0:
                    self.hash_progress.emit(i + 1, total)
            self.hash_progress.emit(total, total)
            self.hash_complete.emit(records)
        except Exception as e:
            self.error_occurred.emit(str(e))
