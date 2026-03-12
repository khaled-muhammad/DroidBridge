"""Background worker for migration execution."""

from datetime import datetime
from pathlib import Path

from PySide6.QtCore import QObject, Signal

from core.archive_builder import ArchiveBuilder
from core.file_indexer import FileIndexer
from core.hash_engine import HashEngine
from core.migration_planner import MigrationPlanner
from core.transfer_engine import TransferEngine
from core.report_generator import ReportGenerator
from models import FileRecord, MigrationPlan


class MigrationWorker(QObject):
    """Worker for full migration pipeline."""

    migration_progress = Signal(str, int, int)  # phase, current, total
    migration_complete = Signal(str)  # report path
    error_occurred = Signal(str)

    def __init__(self):
        super().__init__()
        self.planner = MigrationPlanner()
        self.archive_builder = ArchiveBuilder()
        self.transfer_engine = TransferEngine()
        self.report_generator = ReportGenerator()
        self.hash_engine = HashEngine()
        self.file_indexer = FileIndexer()

    def run_migration(
        self,
        plan: MigrationPlan,
        source_base_path: str,
    ) -> None:
        """
        Execute migration: build archive from source, push, extract.
        For ADB source, we need to pull files first - plan stores paths.
        """
        start_time = datetime.now()
        try:
            # Get file records for files to transfer
            files_to_transfer = plan.files_to_transfer
            if not files_to_transfer:
                self.migration_complete.emit("")
                return

            # Build FileRecords - we need full records with size
            # For local source we can stat; for ADB we'd need to pull
            # Simplified: assume local source for archive build
            records: list[FileRecord] = []
            base = Path(source_base_path)
            for path in files_to_transfer:
                full = base / path
                if full.exists():
                    stat = full.stat()
                    records.append(
                        FileRecord(
                            path=path,
                            size=stat.st_size,
                            modified_time=stat.st_mtime,
                            source="local",
                        )
                    )

            self.migration_progress.emit("archive", 0, len(records))

            def archive_progress(c, t):
                self.migration_progress.emit("archive", c, t)

            archive_path = self.archive_builder.build_archive(
                records,
                source_base_path,
                progress_callback=archive_progress,
            )
            self.migration_progress.emit("transfer", 1, 1)
            ok, err_msg = self.transfer_engine.transfer_archive(
                archive_path,
                plan.destination_serial,
            )
            if not ok:
                self.error_occurred.emit(err_msg or "Transfer failed")
                return

            end_time = datetime.now()
            report_path = self.report_generator.generate_report(
                start_time=start_time,
                end_time=end_time,
                files_scanned=len(plan.files_to_transfer) + len(plan.duplicates),
                files_migrated=len(plan.files_to_transfer),
                duplicates_skipped=len(plan.duplicates),
                conflicts_resolved=len(plan.conflicts),
                errors=[],
                total_bytes=plan.total_size,
            )
            self.migration_complete.emit(report_path)
        except Exception as e:
            self.error_occurred.emit(str(e))
