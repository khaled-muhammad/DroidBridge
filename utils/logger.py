"""Logging configuration."""

import logging
import sys
from pathlib import Path

from .constants import LOG_DIR, LOG_FILE


def setup_logger(name: str = "smart_migrate") -> logging.Logger:
    """Configure and return application logger."""
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    # Console handler
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(logging.INFO)
    console_fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    console.setFormatter(console_fmt)
    logger.addHandler(console)

    # File handler
    log_path = Path(LOG_DIR)
    log_path.mkdir(exist_ok=True)
    file_handler = logging.FileHandler(log_path / LOG_FILE, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_fmt = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )
    file_handler.setFormatter(file_fmt)
    logger.addHandler(file_handler)

    return logger


def get_logger(name: str = "smart_migrate") -> logging.Logger:
    """Get the application logger."""
    return logging.getLogger(name)
