"""Migration controller - orchestrates UI and workers."""

from pathlib import Path

from PySide6.QtCore import QThread, Qt, QTimer
from PySide6.QtWidgets import QMessageBox, QProgressDialog

from core.file_indexer import FileIndexer
from core.hash_engine import HashEngine
from core.migration_planner import MigrationPlanner
from models import MigrationPlan
from workers.scan_worker import ScanWorker
from workers.hash_worker import HashWorker
from utils.logger import get_logger, setup_logger

logger = get_logger(__name__)


class MigrationController:
    """Coordinates migration flow between UI and workers."""

    def __init__(self, main_window):
        self.window = main_window
        self.plan: MigrationPlan | None = None
        self.source_records = []
        self.dest_records = []
        self._scan_thread: QThread | None = None
        self._hash_thread: QThread | None = None
        self._migration_thread: QThread | None = None

    def setup(self) -> None:
        """Setup logging and defer initial device scan until window is ready."""
        setup_logger()
        QTimer.singleShot(100, self._scan_devices)

    def _scan_devices(self) -> None:
        """Scan for devices in background."""
        self.window.log_view.append("Scanning for devices...")
        worker = ScanWorker()
        thread = QThread()
        worker.moveToThread(thread)
        thread.started.connect(worker.scan_devices)
        worker.devices_ready.connect(self._on_devices_ready, Qt.ConnectionType.QueuedConnection)
        worker.error_occurred.connect(self._on_scan_error, Qt.ConnectionType.QueuedConnection)
        worker.error_occurred.connect(lambda: thread.quit(), Qt.ConnectionType.QueuedConnection)
        worker.devices_ready.connect(lambda: thread.quit(), Qt.ConnectionType.QueuedConnection)
        thread.start()
        self._scan_thread = thread

    def _on_devices_ready(self, devices: list) -> None:
        """Populate device selectors."""
        self.window.source_selector.set_devices(devices)
        self.window.dest_selector.set_devices(devices)
        self.window.log_view.append(f"Found {len(devices)} device(s)")

    def _on_scan_error(self, msg: str) -> None:
        self.window.log_view.append(f"Error: {msg}")
        QMessageBox.warning(self.window, "Scan Error", msg)

    def analyze(self) -> None:
        """Run analysis synchronously to avoid QThread segfaults on macOS."""
        source_type = self.window.source_selector.get_source_type()
        source_path = self.window.source_selector.get_source_path()
        dest = self.window.dest_selector.get_selected()

        if not dest:
            QMessageBox.warning(
                self.window,
                "Missing Destination",
                "Please select a destination device.",
            )
            return

        if source_type == "adb" and not source_path:
            QMessageBox.warning(
                self.window,
                "Missing Source",
                "Please select a source device.",
            )
            return

        if source_type == "local":
            folder = self.window.source_selector.get_source_base_path()
            if not folder or not Path(folder).exists():
                QMessageBox.warning(
                    self.window,
                    "Invalid Folder",
                    "Please select a valid local folder.",
                )
                return

        self.window.analyze_btn.setEnabled(False)
        self.window.log_view.append("Analyzing storage...")
        self.window.log_view.append("")
        self.window.progress.set_status("Starting...")

        progress = QProgressDialog("Analyzing storage...", None, 0, 0, self.window)
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.setMinimumDuration(0)
        progress.show()

        try:
            # Step 1: Index source
            self.window.log_view.append("Step 1: Scanning source...")
            self.window.progress.set_status("Indexing source...")

            indexer = FileIndexer()

            if source_type == "local":
                base_path = self.window.source_selector.get_source_base_path()
                self.source_records = indexer.index_local_folder(base_path)
            else:
                def prog(c, t):
                    progress.setLabelText(f"Indexing source: {c:,} files...")
                self.source_records = indexer.index_adb_device(source_path, prog)

            self.window.log_view.append(f"  → Source: {len(self.source_records)} files found")
            self.window.log_view.append("")

            # Step 2: Index destination
            self.window.log_view.append("Step 2: Fetching file list from destination...")
            self.window.progress.set_status("Indexing destination...")

            def dest_prog(c, t):
                progress.setLabelText(f"Indexing destination: {c:,} / {t:,} files...")
            self.dest_records = indexer.index_adb_device(dest.serial, dest_prog)

            self.window.log_view.append(f"  → Destination: {len(self.dest_records)} files found")
            self.window.log_view.append("")

            # Step 3: Hash (local source only)
            if source_type == "local":
                self.window.log_view.append("Step 3: Computing hashes...")
                self.window.progress.set_status("Hashing...")

                hash_engine = HashEngine()
                base_path = self.window.source_selector.get_source_base_path()
                total = len(self.source_records)
                for i, record in enumerate(self.source_records):
                    hash_engine.update_record_hash(record, base_path)
                    if (i + 1) % 100 == 0:
                        progress.setLabelText(f"Hashing: {i + 1:,} / {total:,}")

                self.window.log_view.append("  → Hashes computed")
                self.window.log_view.append("")
            else:
                self.window.log_view.append("Step 3: Building plan (ADB source - hashing skipped)...")

            # Step 4: Create plan
            self.window.log_view.append("Step 4: Building migration plan...")
            self.window.progress.set_status("Building plan...")

            self._create_plan(self.source_records)

        except Exception as e:
            logger.exception("Analysis failed")
            self._on_analyze_error(str(e))
        finally:
            progress.close()
            self.window.analyze_btn.setEnabled(True)

    def _create_plan(self, source_records: list) -> None:
        """Create migration plan and update UI."""
        self.window.progress.set_status("Building plan...")

        planner = MigrationPlanner()
        source_type = self.window.source_selector.get_source_type()
        source_path = self.window.source_selector.get_source_path()
        dest = self.window.dest_selector.get_selected()

        self.plan = planner.create_plan(
            source_records,
            self.dest_records,
            source_type=source_type,
            source_path=source_path,
            destination_serial=dest.serial,
        )
        planner.save_plan(self.plan)

        self.window.preview.set_plan(self.plan)
        self.window.start_btn.setEnabled(True)
        self.window.analyze_btn.setEnabled(True)
        self.window.progress.set_status("Analysis complete")
        self.window.log_view.append("  → Plan ready")
        self.window.log_view.append("")
        self.window.log_view.append(
            f"Done. {len(self.plan.files_to_transfer)} files to transfer, "
            f"{len(self.plan.duplicates)} duplicates skipped, "
            f"{len(self.plan.conflicts)} conflicts resolved."
        )

    def _on_analyze_error(self, msg: str) -> None:
        self.window.log_view.append(f"Error: {msg}")
        self.window.analyze_btn.setEnabled(True)
        self.window.progress.set_status("Error")
        QMessageBox.warning(self.window, "Analysis Error", msg)

    def start_migration(self) -> None:
        """Start migration execution."""
        if not self.plan or not self.plan.files_to_transfer:
            QMessageBox.information(
                self.window,
                "Nothing to Migrate",
                "No files to transfer. Run analysis first.",
            )
            return

        source_type = self.window.source_selector.get_source_type()
        if source_type == "adb":
            QMessageBox.warning(
                self.window,
                "ADB Source",
                "Migration from ADB source requires pulling files first. "
                "Currently only local folder source is supported for migration execution.",
            )
            return

        base_path = self.window.source_selector.get_source_base_path()
        if not Path(base_path).exists():
            QMessageBox.warning(self.window, "Error", "Source folder not found.")
            return

        reply = QMessageBox.question(
            self.window,
            "Confirm Migration",
            f"Transfer {len(self.plan.files_to_transfer)} files ({self.plan.total_size / (1024**3):.1f} GB)?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return

        self.window.start_btn.setEnabled(False)
        self.window.log_view.append("Starting migration...")

        progress = QProgressDialog("Migrating files...", None, 0, 0, self.window)
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.setMinimumDuration(0)
        progress.show()

        try:
            from core.archive_builder import ArchiveBuilder
            from core.transfer_engine import TransferEngine
            from core.report_generator import ReportGenerator
            from datetime import datetime
            from models import FileRecord

            start_time = datetime.now()
            files_to_transfer = self.plan.files_to_transfer
            if not files_to_transfer:
                self.window.start_btn.setEnabled(True)
                progress.close()
                return

            base = Path(base_path)
            records = []
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

            progress.setLabelText("Building archive...")
            archive_builder = ArchiveBuilder()

            def archive_prog(c, t):
                progress.setLabelText(f"Building archive: {c:,} / {t:,} files")

            archive_path = archive_builder.build_archive(
                records, base_path, progress_callback=archive_prog
            )

            progress.setLabelText("Transferring to device...")
            transfer_engine = TransferEngine()
            ok, err_msg = transfer_engine.transfer_archive(archive_path, self.plan.destination_serial)

            if not ok:
                self._on_migration_error(err_msg or "Transfer failed")
                progress.close()
                return

            end_time = datetime.now()
            report_gen = ReportGenerator()
            report_path = report_gen.generate_report(
                start_time=start_time,
                end_time=end_time,
                files_scanned=len(self.plan.files_to_transfer) + len(self.plan.duplicates),
                files_migrated=len(self.plan.files_to_transfer),
                duplicates_skipped=len(self.plan.duplicates),
                conflicts_resolved=len(self.plan.conflicts),
                errors=[],
                total_bytes=self.plan.total_size,
            )

            self.window.start_btn.setEnabled(True)
            self.window.progress.set_status("Migration complete!")
            self.window.log_view.append(f"Done. Report: {report_path}")
            QMessageBox.information(
                self.window,
                "Migration Complete",
                "Migration completed successfully.",
            )
        except Exception as e:
            self._on_migration_error(str(e))
        finally:
            progress.close()
            self.window.start_btn.setEnabled(True)

    def _on_migration_complete(self, report_path: str) -> None:
        self.window.start_btn.setEnabled(True)
        self.window.progress.set_status("Migration complete!")
        self.window.log_view.append(f"Done. Report: {report_path}")
        QMessageBox.information(
            self.window,
            "Migration Complete",
            "Migration completed successfully.",
        )

    def _on_migration_error(self, msg: str) -> None:
        self.window.start_btn.setEnabled(True)
        self.window.log_view.append(f"Error: {msg}")
        self.window.progress.set_status("Error")
        QMessageBox.critical(self.window, "Migration Error", msg)
