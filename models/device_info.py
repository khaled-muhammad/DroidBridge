"""Device information model."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class DeviceInfo:
    """Represents an Android device connected via ADB."""

    serial: str
    model: str
    status: str = "device"
    android_version: Optional[str] = None
    storage_size: Optional[int] = None
    available_space: Optional[int] = None
    product: Optional[str] = None

    def display_name(self) -> str:
        """Human-readable display name."""
        model_part = self.model or self.product or "Unknown"
        return f"{model_part} ({self.serial})"
