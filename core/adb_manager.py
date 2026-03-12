"""ADB device management and command execution."""

import subprocess
from pathlib import Path
import os
from typing import List, Optional, Tuple

from models import DeviceInfo
from utils.adb_utils import run_adb, parse_devices_output
from utils.constants import SDCARD_PATH
from utils.logger import get_logger

logger = get_logger(__name__)


class ADBManager:
    """Manages ADB communication with Android devices."""

    def get_devices(self) -> List[DeviceInfo]:
        """Get list of connected devices."""
        code, stdout, stderr = run_adb(["devices", "-l"])
        if code != 0:
            logger.error("Failed to list devices: %s", stderr)
            return []
        devices_data = parse_devices_output(stdout)
        return [
            DeviceInfo(
                serial=d["serial"],
                model=d.get("model") or "Unknown",
                status=d.get("status", "device"),
                product=d.get("product"),
            )
            for d in devices_data
        ]

    def run_shell(
        self,
        command: str,
        serial: Optional[str] = None,
        timeout: Optional[int] = None,
    ) -> Tuple[int, str, str]:
        """Execute shell command on device. timeout: seconds (default 120)."""
        args = ["shell", command]
        return run_adb(args, serial, timeout=timeout)

    def push_file(
        self,
        local_path: str,
        remote_path: str,
        serial: Optional[str] = None,
        timeout: Optional[int] = None,
    ) -> Tuple[int, str, str]:
        """Push file to device. timeout: seconds (auto-calculated from file size if None)."""
        if timeout is None:
            try:
                size_mb = os.path.getsize(local_path) / (1024 * 1024)
                # ~5 MB/s USB2, 50% buffer; min 10 min, max 6 hours
                timeout = max(600, min(6 * 3600, int(size_mb / 5 * 1.5)))
            except OSError:
                timeout = 4 * 3600
        return run_adb(["push", local_path, remote_path], serial, timeout=timeout)

    def pull_file(
        self,
        remote_path: str,
        local_path: str,
        serial: Optional[str] = None,
        timeout: Optional[int] = None,
    ) -> Tuple[int, str, str]:
        """Pull file from device. timeout: seconds (default 4h for large files)."""
        if timeout is None:
            timeout = 4 * 3600
        return run_adb(["pull", remote_path, local_path], serial, timeout=timeout)

    def file_exists(self, remote_path: str, serial: Optional[str] = None) -> bool:
        """Check if file exists on device."""
        code, stdout, _ = self.run_shell(f'[ -f "{remote_path}" ] && echo exists', serial)
        return "exists" in stdout

    def get_file_info(
        self,
        remote_path: str,
        serial: Optional[str] = None,
    ) -> Optional[Tuple[int, float]]:
        """Get file size and mtime. Returns (size, mtime) or None."""
        code, stdout, _ = self.run_shell(
            f'stat -c "%s %Y" "{remote_path}" 2>/dev/null || stat -f "%z %m" "{remote_path}" 2>/dev/null',
            serial,
        )
        if code != 0 or not stdout.strip():
            return None
        try:
            parts = stdout.strip().split()
            return int(parts[0]), float(parts[1])
        except (ValueError, IndexError):
            return None

    def list_files_recursive(
        self,
        base_path: str = SDCARD_PATH,
        serial: Optional[str] = None,
    ) -> List[Tuple[str, int, float]]:
        """List all files under base path with size and mtime."""
        # Use find with stat for size and mtime
        cmd = f'find "{base_path}" -type f -exec stat -c "%n|%s|%Y" {{}} \\; 2>/dev/null || find "{base_path}" -type f -exec stat -f "%N|%z|%m" {{}} \\; 2>/dev/null'
        code, stdout, stderr = self.run_shell(cmd, serial, timeout=600)
        if code != 0:
            logger.error("Find failed: %s", stderr)
            return []

        results = []
        for line in stdout.strip().split("\n"):
            if "|" not in line:
                continue
            parts = line.split("|", 2)
            if len(parts) < 3:
                continue
            path, size_str, mtime_str = parts[0], parts[1], parts[2]
            # Normalize path to relative from sdcard
            if path.startswith("/sdcard/"):
                rel_path = path[8:]
            elif path.startswith("sdcard/"):
                rel_path = path[7:]
            else:
                rel_path = path
            try:
                results.append((rel_path, int(size_str), float(mtime_str)))
            except ValueError:
                continue
        return results

    def create_remote_dir(self, path: str, serial: Optional[str] = None) -> bool:
        """Create directory on device."""
        code, _, _ = self.run_shell(f'mkdir -p "{path}"', serial)
        return code == 0

    def remove_remote_file(self, path: str, serial: Optional[str] = None) -> bool:
        """Remove file on device."""
        code, _, _ = self.run_shell(f'rm -f "{path}"', serial)
        return code == 0
