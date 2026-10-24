from PyQt6.QtCore import Qt
from PyQt6.QtGui import QStandardItem, QStandardItemModel

from expense_manager.models.vendor_summary import VendorSummary
# ==========================================================================================
# ==========================================================================================

# File:    vendor_summary_model.py
# Date:    October 24, 2026
# Author:  Jonathan A. Webb
# Purpose: Qt item model for vendor expense summary reporting
# ==========================================================================================
# ==========================================================================================
# Insert Code here

class VendorSummaryModel(QStandardItemModel):
    """Display vendor totals and transaction counts."""

    HEADERS = ("Vendor", "Total", "Transactions")

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setHorizontalHeaderLabels(self.HEADERS)
        self._grand_total_cents = 0

    @staticmethod
    def _format_currency(cents: int) -> str:
        """Format signed integer cents as dollars."""
        sign = "-" if cents < 0 else ""
        dollars, remainder = divmod(abs(cents), 100)

        return f"{sign}${dollars:,}.{remainder:02d}"

    @staticmethod
    def _make_item(
        text: str,
        sort_value=None,
        alignment=None,
    ) -> QStandardItem:
        """Create a read-only item with optional sort data."""
        item = QStandardItem(text)
        item.setEditable(False)

        if sort_value is not None:
            item.setData(sort_value, Qt.ItemDataRole.UserRole)

        if alignment is not None:
            item.setTextAlignment(alignment)

        return item

    def load_summary(
        self,
        summaries: list[VendorSummary],
    ) -> None:
        """Replace the model contents with aggregated vendor data."""
        self.removeRows(0, self.rowCount())

        self._grand_total_cents = sum(
            summary.total_cents for summary in summaries
        )

        for summary in summaries:
            vendor_item = self._make_item(
                summary.vendor,
                sort_value=summary.vendor.casefold(),
            )

            total_item = self._make_item(
                self._format_currency(summary.total_cents),
                sort_value=summary.total_cents,
                alignment=Qt.AlignmentFlag.AlignRight
                | Qt.AlignmentFlag.AlignVCenter,
            )

            count_item = self._make_item(
                str(summary.transaction_count),
                sort_value=summary.transaction_count,
                alignment=Qt.AlignmentFlag.AlignRight
                | Qt.AlignmentFlag.AlignVCenter,
            )

            self.appendRow(
                [vendor_item, total_item, count_item]
            )

    def grand_total_cents(self) -> int:
        """Return the sum of all vendor totals."""
        return self._grand_total_cents

# ==========================================================================================
# ==========================================================================================
# eof
