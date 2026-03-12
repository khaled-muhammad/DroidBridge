"""File utility functions."""

import os
from pathlib import Path
from typing import Optional

from .constants import MIGRATED_SUFFIX


def format_size(size_bytes: int) -> str:
    """Format byte size to human-readable string."""
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} PB"


def format_duration(seconds: float) -> str:
    """Format seconds to human-readable duration."""
    if seconds < 60:
        return f"{seconds:.0f}s"
    if seconds < 3600:
        mins = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{mins}m {secs}s"
    hours = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    return f"{hours}h {mins}m"


def get_conflict_path(original_path: str) -> str:
    """Generate conflict resolution path: filename (migrated).ext."""
    path = Path(original_path)
    stem = path.stem
    suffix = path.suffix
    new_name = f"{stem}{MIGRATED_SUFFIX}{suffix}"
    return str(path.parent / new_name)


def safe_path_join(base: str, *parts: str) -> Optional[str]:
    """Safely join paths and ensure result is under base (no path traversal)."""
    result = Path(base)
    for part in parts:
        part = part.lstrip("/")
        if ".." in part or part.startswith("/"):
            return None
        result = result / part
    try:
        resolved = result.resolve()
        base_resolved = Path(base).resolve()
        if not str(resolved).startswith(str(base_resolved)):
            return None
        return str(resolved)
    except (OSError, RuntimeError):
        return None


def get_mime_type(path: str) -> Optional[str]:
    """Get MIME type from file extension (basic mapping)."""
    ext_map = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".gif": "image/gif",
        ".webp": "image/webp",
        ".mp4": "video/mp4",
        ".3gp": "video/3gpp",
        ".mp3": "audio/mpeg",
        ".m4a": "audio/mp4",
        ".pdf": "application/pdf",
        ".doc": "application/msword",
        ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    }
    return ext_map.get(Path(path).suffix.lower())
