from decimal import Decimal

from PyQt6.QtCore import (
    QAbstractTableModel,
    QModelIndex,
    Qt,
)
from PyQt6.QtGui import QColor
# ==========================================================================================
# ==========================================================================================

# File:    daily_balance_table.py
# Date:    October 24, 2026
# Author:  Jonathan A. Webb
# Purpose: Describe the purpose of functions of this file
# ==========================================================================================
# ==========================================================================================

class DailyBalanceTableModel(QAbstractTableModel):
    """Display daily net changes and closing account balances."""

    HEADERS = (
        "Date",
        "Net Change ($)",
        "Closing Balance ($)",
    )

    def __init__(self, parent=None):
        super().__init__(parent)
        self.balances = []

    def rowCount(self, parent=QModelIndex()) -> int:
        """Return the number of daily balance records."""
        if parent.isValid():
            return 0

        return len(self.balances)

    def columnCount(self, parent=QModelIndex()) -> int:
        """Return the number of columns."""
        if parent.isValid():
            return 0

        return len(self.HEADERS)

    def data(
        self,
        index: QModelIndex,
        role=Qt.ItemDataRole.DisplayRole,
    ):
        """Return data and formatting for the requested cell."""
        if not index.isValid():
            return None

        if not (0 <= index.row() < len(self.balances)):
            return None

        if not (0 <= index.column() < len(self.HEADERS)):
            return None

        balance = self.balances[index.row()]
        column = index.column()

        if column == 0:
            value = balance["balance_date"]
        elif column == 1:
            value = balance["daily_change"]
        else:
            value = balance["closing_balance"]

        # Display dates and formatted dollar amounts.
        if role == Qt.ItemDataRole.DisplayRole:
            if column == 0:
                return value

            amount = Decimal(value) / Decimal(100)
            return f"${amount:,.2f}"

        # Preserve raw values for correct numeric sorting.
        if role == Qt.ItemDataRole.EditRole:
            return value

        # Color financial values according to daily change.
        if role == Qt.ItemDataRole.ForegroundRole:
            if column in (1, 2):
                daily_change = balance["daily_change"]

                if daily_change < 0:
                    return QColor("#C62828")  # Red: decrease

                if daily_change > 0:
                    return QColor("#2E7D32")  # Green: increase

            return None

        # Align monetary values to the right.
        if role == Qt.ItemDataRole.TextAlignmentRole:
            if column == 0:
                return (
                    Qt.AlignmentFlag.AlignLeft
                    | Qt.AlignmentFlag.AlignVCenter
                )

            return (
                Qt.AlignmentFlag.AlignRight
                | Qt.AlignmentFlag.AlignVCenter
            )

        return None

    def headerData(
        self,
        section: int,
        orientation: Qt.Orientation,
        role=Qt.ItemDataRole.DisplayRole,
    ):
        """Return column header labels."""
        if (
            role == Qt.ItemDataRole.DisplayRole
            and orientation == Qt.Orientation.Horizontal
        ):
            if 0 <= section < len(self.HEADERS):
                return self.HEADERS[section]

        return None

    def flags(self, index: QModelIndex) -> Qt.ItemFlag:
        """Prevent editing of calculated balance values."""
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags

        return (
            Qt.ItemFlag.ItemIsEnabled
            | Qt.ItemFlag.ItemIsSelectable
        )

    def load_balances(self, balances) -> None:
        """Replace the table contents with calculated balances."""
        self.beginResetModel()

        self.balances = list(balances)

        self.endResetModel()


# ==========================================================================================
# ==========================================================================================
# eof
