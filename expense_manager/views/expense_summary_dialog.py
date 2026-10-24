from PyQt6.QtCore import QDate, Qt
from PyQt6.QtWidgets import (
    QDateEdit,
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTreeView,
    QVBoxLayout,
    QWidget,
    QHeaderView,
)

from expense_manager.models.expense_summary_model import ExpenseSummaryModel
# ==========================================================================================
# ==========================================================================================

# File:    expense_summary_dialog.py
# Date:    October 23, 2026
# Author:  Jonathan A. Webb
# Purpose: Dialog for siplaying expense summaries by type and subtype
# ==========================================================================================
# ==========================================================================================


class ExpenseSummaryDialog(QDialog):
    """Display expense totals for a selected reporting period."""

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize the expense summary dialog."""
        super().__init__(parent)

        self.setWindowTitle("Expense Summary")
        self.resize(750, 550)

        # --------------------------------------------------------------
        # Reporting date selectors
        # --------------------------------------------------------------
        today = QDate.currentDate()

        self.start_date_edit = QDateEdit()
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setDisplayFormat("yyyy-MM-dd")
        self.start_date_edit.setDate(QDate(today.year(), today.month(), 1))

        self.end_date_edit = QDateEdit()
        self.end_date_edit.setCalendarPopup(True)
        self.end_date_edit.setDisplayFormat("yyyy-MM-dd")
        self.end_date_edit.setDate(today)

        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("Start Date:"))
        date_layout.addWidget(self.start_date_edit)
        date_layout.addSpacing(15)
        date_layout.addWidget(QLabel("End Date:"))
        date_layout.addWidget(self.end_date_edit)

        # --------------------------------------------------------------
        # Generate report button
        # --------------------------------------------------------------
        self.generate_button = QPushButton("Generate Report")
        date_layout.addWidget(self.generate_button)
        date_layout.addStretch()

        # --------------------------------------------------------------
        # Hierarchical report
        # --------------------------------------------------------------
        self.summary_model = ExpenseSummaryModel(self)

        self.tree_view = QTreeView()
        self.tree_view.setModel(self.summary_model)

        self.tree_view.setAlternatingRowColors(True)
        self.tree_view.setRootIsDecorated(True)
        self.tree_view.setUniformRowHeights(True)
        self.tree_view.setEditTriggers(
            QTreeView.EditTrigger.NoEditTriggers
        )

        header = self.tree_view.header()
        header.setSectionResizeMode(
            0,
            QHeaderView.ResizeMode.Stretch,
        )
        header.setSectionResizeMode(
            1,
            QHeaderView.ResizeMode.ResizeToContents,
        )
        header.setSectionResizeMode(
            2,
            QHeaderView.ResizeMode.ResizeToContents,
        )

        # --------------------------------------------------------------
        # Grand total
        # --------------------------------------------------------------
        self.grand_total_label = QLabel("Net Total: $0.00")
        self.grand_total_label.setAlignment(
            Qt.AlignmentFlag.AlignRight
        )

        font = self.grand_total_label.font()
        font.setBold(True)
        font.setPointSize(font.pointSize() + 2)
        self.grand_total_label.setFont(font)

        # --------------------------------------------------------------
        # Close button
        # --------------------------------------------------------------
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.close)

        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.close_button)

        # --------------------------------------------------------------
        # Main layout
        # --------------------------------------------------------------
        main_layout = QVBoxLayout(self)

        main_layout.addLayout(date_layout)
        main_layout.addWidget(self.tree_view)
        main_layout.addWidget(self.grand_total_label)
        main_layout.addLayout(bottom_layout)

    def get_date_range(self) -> tuple[str, str]:
        """Return selected start and end dates as ISO strings."""
        return (
            self.start_date_edit.date().toString("yyyy-MM-dd"),
            self.end_date_edit.date().toString("yyyy-MM-dd"),
        )

    def display_summary(self, summaries) -> None:
        """Populate the report tree and update the grand total."""
        self.summary_model.load_summary(summaries)

        self.tree_view.expandAll()

        total_cents = self.summary_model.grand_total_cents()

        sign = "-" if total_cents < 0 else ""
        dollars, cents = divmod(abs(total_cents), 100)

        self.grand_total_label.setText(
            f"Net Total: {sign}${dollars:,}.{cents:02d}"
        )

# ==========================================================================================
# ==========================================================================================
# eof
