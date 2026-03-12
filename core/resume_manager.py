"""Migration resume - save and restore state for interrupted migrations."""

import json
from pathlib import Path
from typing import Dict, List, Optional, Set

from utils.constants import MIGRATION_STATE_FILE
from utils.logger import get_logger

logger = get_logger(__name__)


class ResumeManager:
    """Manages migration state for resume capability."""

    def __init__(self, state_path: Optional[str] = None):
        self.state_path = state_path or MIGRATION_STATE_FILE

    def save_state(
        self,
        files_completed: List[str],
        files_remaining: List[str],
        archive_status: str = "pending",  # pending, building, pushed, extracted
        extra: Optional[Dict] = None,
    ) -> None:
        """Save migration state to JSON."""
        data = {
            "files_completed": files_completed,
            "files_remaining": files_remaining,
            "archive_status": archive_status,
            **(extra or {}),
        }
        Path(self.state_path).parent.mkdir(parents=True, exist_ok=True)
        with open(self.state_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        logger.debug("State saved: %d completed, %d remaining", len(files_completed), len(files_remaining))

    def load_state(self) -> Optional[Dict]:
        """Load migration state. Returns None if not found or invalid."""
        path = Path(self.state_path)
        if not path.exists():
            return None
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            logger.warning("Failed to load state: %s", e)
            return None

    def clear_state(self) -> None:
        """Remove state file."""
        Path(self.state_path).unlink(missing_ok=True)
        logger.info("State cleared")
