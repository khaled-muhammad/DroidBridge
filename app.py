#!/usr/bin/env python3
"""DroidBridge - Entry point."""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from ui.main_window import MainWindow
from utils.logger import setup_logger


def main() -> int:
    """Run the application."""
    setup_logger()
    app = QApplication(sys.argv)
    app.setApplicationName("DroidBridge")
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
