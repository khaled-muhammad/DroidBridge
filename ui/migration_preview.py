"""Migration preview/summary panel."""

from PySide6.QtWidgets import (
    QFormLayout,
    QGroupBox,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from models import MigrationPlan
from utils.file_utils import format_size, format_duration


class MigrationPreview(QWidget):
    """Displays migration summary before execution."""

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        self.group = QGroupBox("Migration Summary")
        form = QFormLayout(self.group)
        self.files_label = QLabel("0")
        self.duplicates_label = QLabel("0")
        self.conflicts_label = QLabel("0")
        self.size_label = QLabel("0 B")
        self.time_label = QLabel("--")
        form.addRow("Files to transfer:", self.files_label)
        form.addRow("Duplicates skipped:", self.duplicates_label)
        form.addRow("Conflicts resolved:", self.conflicts_label)
        form.addRow("Total size:", self.size_label)
        form.addRow("Estimated time:", self.time_label)
        layout.addWidget(self.group)
        self.set_plan(None)

    def set_plan(self, plan: MigrationPlan | None) -> None:
        """Update display from migration plan."""
        if plan is None:
            self.files_label.setText("0")
            self.duplicates_label.setText("0")
            self.conflicts_label.setText("0")
            self.size_label.setText("0 B")
            self.time_label.setText("--")
            self.group.setEnabled(False)
        else:
            self.files_label.setText(str(len(plan.files_to_transfer)))
            self.duplicates_label.setText(str(len(plan.duplicates)))
            self.conflicts_label.setText(str(len(plan.conflicts)))
            self.size_label.setText(format_size(plan.total_size))
            self.time_label.setText(format_duration(plan.estimated_time_seconds))
            self.group.setEnabled(True)
