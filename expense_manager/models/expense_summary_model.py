from collections import defaultdict

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QStandardItem, QStandardItemModel

from expense_manager.models.expense_summary import ExpenseSummary
# ==========================================================================================
# ==========================================================================================

# File:    expense_summary_model.py
# Date:    October 23, 2026
# Author:  Jonathan A. Webb
# Purpose: Hierarchical Qt model for expense summary reports
# ==========================================================================================
# ==========================================================================================


class ExpenseSummaryModel(QStandardItemModel):
    """Represent expense totals grouped by type and subtype."""

    HEADERS = (
        "Type / Subtype",
        "Total",
        "Transactions",
    )

    def __init__(self, parent=None):
        """Initialize an empty expense summary model."""
        super().__init__(parent)

        # Store monetary totals as integer cents.
        self._grand_total_cents: int = 0

        self.setHorizontalHeaderLabels(self.HEADERS)

    @staticmethod
    def _format_currency(cents: int) -> str:
        """Format signed integer cents as a dollar amount."""
        sign = "-" if cents < 0 else ""
        absolute_cents = abs(cents)

        dollars, remainder = divmod(absolute_cents, 100)

        return f"{sign}${dollars:,}.{remainder:02d}"

    @staticmethod
    def _make_item(
        text: str,
        alignment=None,
        bold: bool = False,
    ) -> QStandardItem:
        """Create a read-only table item."""
        item = QStandardItem(text)
        item.setEditable(False)

        if alignment is not None:
            item.setTextAlignment(alignment)

        if bold:
            font = item.font()
            font.setBold(True)
            item.setFont(font)

        return item

    def load_summary(
        self,
        summaries: list[ExpenseSummary],
    ) -> None:
        """Populate the model with hierarchical expense totals."""
        self.clear()
        self.setHorizontalHeaderLabels(self.HEADERS)

        # Calculate the grand total directly from integer cents.
        self._grand_total_cents = sum(
            summary.total_cents
            for summary in summaries
        )

        # Group subtype summaries under their parent expense type.
        grouped: dict[str, list[ExpenseSummary]] = defaultdict(list)

        for summary in summaries:
            grouped[summary.type].append(summary)

        for expense_type in sorted(grouped):
            subtypes = sorted(
                grouped[expense_type],
                key=lambda summary: summary.sub_type,
            )

            total_cents = sum(
                summary.total_cents
                for summary in subtypes
            )

            transaction_count = sum(
                summary.transaction_count
                for summary in subtypes
            )

            # ------------------------------------------------------------------
            # Parent expense type
            # ------------------------------------------------------------------
            type_item = self._make_item(
                expense_type,
                bold=True,
            )

            total_item = self._make_item(
                self._format_currency(total_cents),
                alignment=(
                    Qt.AlignmentFlag.AlignRight
                    | Qt.AlignmentFlag.AlignVCenter
                ),
                bold=True,
            )

            count_item = self._make_item(
                str(transaction_count),
                alignment=(
                    Qt.AlignmentFlag.AlignRight
                    | Qt.AlignmentFlag.AlignVCenter
                ),
                bold=True,
            )

            self.appendRow([
                type_item,
                total_item,
                count_item,
            ])

            # ------------------------------------------------------------------
            # Child subtype rows
            # ------------------------------------------------------------------
            for summary in subtypes:
                # Do not display redundant NA subtype rows.
                if summary.sub_type == "NA":
                    continue

                subtype_item = self._make_item(
                    summary.sub_type,
                )

                subtype_total_item = self._make_item(
                    self._format_currency(summary.total_cents),
                    alignment=(
                        Qt.AlignmentFlag.AlignRight
                        | Qt.AlignmentFlag.AlignVCenter
                    ),
                )

                subtype_count_item = self._make_item(
                    str(summary.transaction_count),
                    alignment=(
                        Qt.AlignmentFlag.AlignRight
                        | Qt.AlignmentFlag.AlignVCenter
                    ),
                )

                type_item.appendRow([
                    subtype_item,
                    subtype_total_item,
                    subtype_count_item,
                ])

    def grand_total_cents(self) -> int:
        """Return the signed grand total in integer cents."""
        return self._grand_total_cents


# ==========================================================================================
# ==========================================================================================
# eof
