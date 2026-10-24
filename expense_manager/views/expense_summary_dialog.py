from PyQt6.QtCore import QDate, Qt
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QDateEdit,
    QDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QTableView,
    QTabWidget,
    QTreeView,
    QVBoxLayout,
    QWidget,
)

from expense_manager.models.expense_summary_model import ExpenseSummaryModel
from expense_manager.models.vendor_summary_model import VendorSummaryModel
# ==========================================================================================
# ==========================================================================================

# File:    expense_summary_dialog.py
# Date:    October 23, 2026
# Author:  Jonathan A. Webb
# Purpose: Dialog for siplaying expense summaries by type and subtype
# ==========================================================================================
# ==========================================================================================


class ExpenseSummaryDialog(QDialog):
    """Display category and vendor summaries for a shared date range."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.setWindowTitle("Expense Reports")
        self.resize(850, 600)

        today = QDate.currentDate()

        self.start_date_edit = QDateEdit()
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setDisplayFormat("yyyy-MM-dd")
        self.start_date_edit.setDate(
            QDate(today.year(), today.month(), 1)
        )

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

        self.generate_button = QPushButton("Generate Report")
        date_layout.addWidget(self.generate_button)
        date_layout.addStretch()

        # Shared tab container.
        self.tabs = QTabWidget()

        # --------------------------------------------------------------
        # Type / Subtype tab
        # --------------------------------------------------------------
        self.summary_model = ExpenseSummaryModel(self)

        self.tree_view = QTreeView()
        self.tree_view.setModel(self.summary_model)
        self.tree_view.setAlternatingRowColors(True)
        self.tree_view.setRootIsDecorated(True)
        self.tree_view.setUniformRowHeights(True)
        self.tree_view.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )

        category_header = self.tree_view.header()
        category_header.setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch
        )
        category_header.setSectionResizeMode(
            1, QHeaderView.ResizeMode.ResizeToContents
        )
        category_header.setSectionResizeMode(
            2, QHeaderView.ResizeMode.ResizeToContents
        )

        category_tab = QWidget()
        category_layout = QVBoxLayout(category_tab)
        category_layout.addWidget(self.tree_view)

        self.tabs.addTab(category_tab, "Type / Subtype")

        # --------------------------------------------------------------
        # Vendors tab
        # --------------------------------------------------------------
        self.vendor_model = VendorSummaryModel(self)
        self.vendor_model.setSortRole(Qt.ItemDataRole.UserRole)

        self.vendor_table = QTableView()
        self.vendor_table.setModel(self.vendor_model)
        self.vendor_table.setAlternatingRowColors(True)
        self.vendor_table.setSortingEnabled(True)
        self.vendor_table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )
        self.vendor_table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )

        vendor_header = self.vendor_table.horizontalHeader()
        vendor_header.setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch
        )
        vendor_header.setSectionResizeMode(
            1, QHeaderView.ResizeMode.ResizeToContents
        )
        vendor_header.setSectionResizeMode(
            2, QHeaderView.ResizeMode.ResizeToContents
        )

        vendor_tab = QWidget()
        vendor_layout = QVBoxLayout(vendor_tab)
        vendor_layout.addWidget(self.vendor_table)

        self.tabs.addTab(vendor_tab, "Vendors")

        # --------------------------------------------------------------
        # Shared grand total and close button
        # --------------------------------------------------------------
        self.grand_total_label = QLabel("Net Total: $0.00")
        self.grand_total_label.setAlignment(
            Qt.AlignmentFlag.AlignRight
        )

        font = self.grand_total_label.font()
        font.setBold(True)
        font.setPointSize(font.pointSize() + 2)
        self.grand_total_label.setFont(font)

        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.close)

        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.close_button)

        main_layout = QVBoxLayout(self)
        main_layout.addLayout(date_layout)
        main_layout.addWidget(self.tabs)
        main_layout.addWidget(self.grand_total_label)
        main_layout.addLayout(bottom_layout)

    def get_date_range(self) -> tuple[str, str]:
        """Return the selected inclusive reporting date range."""
        return (
            self.start_date_edit.date().toString("yyyy-MM-dd"),
            self.end_date_edit.date().toString("yyyy-MM-dd"),
        )

    @staticmethod
    def _format_currency(cents: int) -> str:
        """Format signed integer cents as dollars."""
        sign = "-" if cents < 0 else ""
        dollars, remainder = divmod(abs(cents), 100)

        return f"{sign}${dollars:,}.{remainder:02d}"

    def display_summary(self, summaries) -> None:
        """Display type/subtype results.

        Retained for compatibility with existing dialog tests.
        """
        self.summary_model.load_summary(summaries)
        self.tree_view.expandAll()

        total_cents = self.summary_model.grand_total_cents()
        self.grand_total_label.setText(
            f"Net Total: {self._format_currency(total_cents)}"
        )

    def display_vendor_summary(self, summaries) -> None:
        """Display vendor results in the vendor tab."""
        self.vendor_model.load_summary(summaries)

        # Default ordering: largest net expenses first.
        self.vendor_table.sortByColumn(
            1, Qt.SortOrder.AscendingOrder
        )

    def display_reports(
        self,
        expense_summaries,
        vendor_summaries,
    ) -> None:
        """Update both tabs using the same reporting period."""
        self.display_summary(expense_summaries)
        self.display_vendor_summary(vendor_summaries)

        category_total = self.summary_model.grand_total_cents()
        vendor_total = self.vendor_model.grand_total_cents()

        if category_total != vendor_total:
            raise ValueError(
                "Report totals do not agree: "
                f"categories={category_total}, "
                f"vendors={vendor_total}"
            )

        if not expense_summaries:
            self.grand_total_label.setText(
                "Net Total: $0.00 (No transactions)"
            )

# ==========================================================================================
# ==========================================================================================
# eof
