from datetime import date

from PyQt6.QtCore import QModelIndex, QSortFilterProxyModel, Qt
# ==========================================================================================
# ==========================================================================================

# File:    expense_filter_proxy_model.py
# Date:    October 24, 2026
# Author:  Jonathan A. Webb
# Purpose: Describe the purpose of functions of this file
# ==========================================================================================
# ==========================================================================================


class ExpenseFilterProxyModel(QSortFilterProxyModel):
    """Filter expenses by date, vendor, type, and subtype."""

    PURCHASE_DATE_COLUMN = 2
    VENDOR_COLUMN = 3
    TYPE_COLUMN = 5
    SUBTYPE_COLUMN = 6

    def __init__(self, parent=None):
        super().__init__(parent)

        self._start_date: date | None = None
        self._end_date: date | None = None
        self._vendor: str | None = None
        self._expense_type: str | None = None
        self._subtype: str | None = None

        self.setDynamicSortFilter(True)
        self.setSortRole(Qt.ItemDataRole.EditRole)

    def set_date_filter(
        self,
        start_date: date | None,
        end_date: date | None,
    ) -> None:
        """Set an inclusive purchase-date filter."""
        if (
            start_date is not None
            and end_date is not None
            and start_date > end_date
        ):
            raise ValueError(
                "Start date cannot be later than end date."
            )

        self._start_date = start_date
        self._end_date = end_date

        self.invalidateFilter()

    def set_vendor_filter(self, vendor: str | None) -> None:
        """Filter by vendor name, ignoring case."""
        self._vendor = vendor.casefold() if vendor else None
        self.invalidateFilter()

    def set_type_filter(self, expense_type: str | None) -> None:
        """Filter by expense type."""
        self._expense_type = expense_type or None

        # A subtype selected for another type is no longer valid.
        if self._expense_type is not None:
            from expense_manager.database.schema import CATEGORIES

            if self._subtype not in CATEGORIES[self._expense_type]:
                self._subtype = None

        self.invalidateFilter()

    def set_subtype_filter(self, subtype: str | None) -> None:
        """Filter by expense subtype."""
        self._subtype = subtype or None
        self.invalidateFilter()

    def clear_filters(self) -> None:
        """Remove all active filters."""
        self._start_date = None
        self._end_date = None
        self._vendor = None
        self._expense_type = None
        self._subtype = None

        self.invalidateFilter()

    def filterAcceptsRow(
        self,
        source_row: int,
        source_parent: QModelIndex,
    ) -> bool:
        """Return whether a source expense satisfies every filter."""
        source = self.sourceModel()

        if source is None:
            return False

        expense = source.expenses[source_row]

        purchase_date = date.fromisoformat(expense.purchase_date)

        if (
            self._start_date is not None
            and purchase_date < self._start_date
        ):
            return False

        if (
            self._end_date is not None
            and purchase_date > self._end_date
        ):
            return False

        if (
            self._vendor is not None
            and expense.vendor.casefold() != self._vendor
        ):
            return False

        if (
            self._expense_type is not None
            and expense.type != self._expense_type
        ):
            return False

        if (
            self._subtype is not None
            and expense.sub_type != self._subtype
        ):
            return False

        return True


    def lessThan(
        self,
        left: QModelIndex,
        right: QModelIndex,
    ) -> bool:
        """Compare expenses using the appropriate data type."""

        source = self.sourceModel()

        if source is None:
            return False

        left_expense = source.expenses[left.row()]
        right_expense = source.expenses[right.row()]

        column = left.column()

        if column == self.PURCHASE_DATE_COLUMN:
            return bool(
                left_expense.purchase_date
                < right_expense.purchase_date
            )

        if column == self.VENDOR_COLUMN:
            return bool(
                (left_expense.vendor or "").casefold()
                < (right_expense.vendor or "").casefold()
            )

        if column == 4:
            return bool(
                left_expense.cost < right_expense.cost
            )

        left_value = source.data(
            left,
            Qt.ItemDataRole.DisplayRole,
        )

        right_value = source.data(
            right,
            Qt.ItemDataRole.DisplayRole,
        )

        return bool(
            str(left_value or "").casefold()
            < str(right_value or "").casefold()
        )
    

# ==========================================================================================
# ==========================================================================================
# eof
