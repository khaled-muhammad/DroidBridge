"""Media path classification and organization hints."""

from typing import Optional

from utils.constants import MEDIA_PATH_MAPPINGS


class MediaClassifier:
    """Classifies media paths for smart organization."""

    def get_mapped_path(self, original_path: str) -> Optional[str]:
        """
        Get destination path for media organization.
        Returns None if no mapping applies.
        """
        path = original_path.replace("\\", "/")
        for source_pattern, dest_base in MEDIA_PATH_MAPPINGS.items():
            if path.startswith(source_pattern) or source_pattern in path:
                # Extract filename and place under dest
                from pathlib import Path
                filename = Path(path).name
                return f"{dest_base}/{filename}"
        return None

    def should_remap(self, path: str) -> bool:
        """Check if path should be remapped per media rules."""
        return self.get_mapped_path(path) is not None
