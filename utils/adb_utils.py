"""ADB utility functions."""

import re
import subprocess
from typing import List, Optional, Tuple


def run_adb(args: List[str], serial: Optional[str] = None) -> Tuple[int, str, str]:
    """
    Run ADB command.
    Returns (return_code, stdout, stderr).
    """
    cmd = ["adb"]
    if serial:
        cmd.extend(["-s", serial])
    cmd.extend(args)
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
        )
        return result.returncode, result.stdout or "", result.stderr or ""
    except subprocess.TimeoutExpired:
        return -1, "", "ADB command timed out"
    except FileNotFoundError:
        return -1, "", "ADB not found. Please ensure ADB is in PATH."
    except Exception as e:
        return -1, "", str(e)


def parse_devices_output(output: str) -> List[dict]:
    """Parse 'adb devices -l' output into device info dicts."""
    devices = []
    lines = output.strip().split("\n")[1:]  # Skip header

    for line in lines:
        if not line.strip():
            continue
        parts = line.split()
        if len(parts) < 2:
            continue
        serial = parts[0]
        status = parts[1]
        if status != "device":
            continue

        info = {"serial": serial, "status": status, "model": None, "product": None}
        for part in parts[2:]:
            if part.startswith("model:"):
                info["model"] = part[6:].replace("_", " ")
            elif part.startswith("product:"):
                info["product"] = part[8:].replace("_", " ")
        if not info["model"] and info["product"]:
            info["model"] = info["product"]
        devices.append(info)
    return devices


def parse_find_output(output: str, base_path: str = "/sdcard") -> List[Tuple[str, int, float]]:
    """
    Parse output of 'adb shell find /sdcard -type f' with stat info.
    Returns list of (path, size, mtime).
    """
    results = []
    for line in output.strip().split("\n"):
        line = line.strip()
        if not line or line.startswith("/"):
            continue
        # Normalize to relative path from sdcard
        if line.startswith("/sdcard/"):
            path = line[8:]  # Remove /sdcard/
        elif line.startswith("sdcard/"):
            path = line[7:]
        else:
            path = line
        results.append((path, 0, 0.0))  # Size and mtime need separate stat
    return results
