"""Path mapping for migration (media organization, etc.)."""

from pathlib import Path
from typing import Optional

from utils.constants import MEDIA_PATH_MAPPINGS, SDCARD_PATH


class PathMapper:
    """Maps source paths to destination paths."""

    def map_path(self, source_path: str, use_media_rules: bool = True) -> str:
        """
        Map source path to destination path.
        If use_media_rules and mapping exists, use it; else keep original.
        """
        path = source_path.replace("\\", "/")
        if use_media_rules:
            for source_pattern, dest_base in MEDIA_PATH_MAPPINGS.items():
                if path.startswith(source_pattern):
                    rel = path[len(source_pattern) :].lstrip("/")
                    return f"{dest_base}/{rel}" if rel else dest_base
        return path

    def validate_extraction_path(self, path: str) -> bool:
        """Validate path for safe extraction (no traversal, under sdcard)."""
        path = path.replace("\\", "/").strip("/")
        if ".." in path or path.startswith("/"):
            return False
        full = f"{SDCARD_PATH}/{path}"
        # Must remain under sdcard
        return full.startswith(SDCARD_PATH)
