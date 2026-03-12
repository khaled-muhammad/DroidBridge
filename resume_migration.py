#!/usr/bin/env python3
"""
Resume migration - continue push/extract without re-compressing.
Run after a failed migration. Uses existing temp/migration.tar and migration_plan.json.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from core.adb_manager import ADBManager
from core.extraction_engine import ExtractionEngine
from utils.constants import MIGRATION_TEMP_DIR, SDCARD_PATH, MIGRATION_PLAN_FILE
from utils.file_utils import format_size
from utils.logger import setup_logger


def main() -> int:
    setup_logger()
    adb = ADBManager()

    # 1. List devices
    devices = adb.get_devices()
    if not devices:
        print("No ADB devices found. Connect a device and enable USB debugging.")
        return 1

    print("\nConnected devices:")
    for i, d in enumerate(devices, 1):
        print(f"  {i}. {d.display_name()}")
    print()

    try:
        choice = input("Select device (number): ").strip()
        idx = int(choice)
        if idx < 1 or idx > len(devices):
            print("Invalid choice.")
            return 1
        device = devices[idx - 1]
    except (ValueError, EOFError):
        print("Invalid input.")
        return 1

    serial = device.serial
    print(f"\nUsing: {device.display_name()}\n")

    # 2. Check archive exists locally
    archive_path = Path("temp/migration.tar")
    if not archive_path.exists():
        print("Archive not found: temp/migration.tar")
        print("Run a full migration first (Analyze + Start Migration) to create it.")
        return 1

    size_mb = archive_path.stat().st_size / (1024 * 1024)
    print(f"Archive: {archive_path} ({format_size(archive_path.stat().st_size)})")

    # 3. Check if archive already on device (skip push if so)
    remote_archive = f"{MIGRATION_TEMP_DIR}/migration.tar"
    if adb.file_exists(remote_archive, serial):
        print(f"Archive already on device - skipping push, extracting only.\n")
        skip_push = True
    else:
        print("Pushing archive to device...")
        skip_push = False

    # 4. Push if needed
    if not skip_push:
        adb.create_remote_dir(MIGRATION_TEMP_DIR, serial)
        code, stdout, stderr = adb.push_file(str(archive_path), remote_archive, serial)
        if code != 0:
            print(f"Push failed: {stderr.strip() or stdout.strip()}")
            return 1
        print("Push complete.\n")

    # 5. Extract
    print("Extracting on device (this may take 30+ mins for large archives)...")
    extractor = ExtractionEngine()
    ok, err = extractor.extract_on_device(remote_archive, SDCARD_PATH, serial, adb)
    if not ok:
        print(f"Extraction failed: {err}")
        print("\nRun this script again to retry extraction (push will be skipped).")
        return 1

    print("Extraction complete.")

    # 6. Cleanup
    adb.remove_remote_file(remote_archive, serial)
    adb.run_shell(f'rmdir "{MIGRATION_TEMP_DIR}" 2>/dev/null', serial)
    print("Cleanup done. Migration complete.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
