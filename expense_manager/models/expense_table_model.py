from dataclasses import replace

from PyQt6.QtCore import QAbstractTableModel, QModelIndex, Qt

from expense_manager.database.schema import CATEGORIES
from expense_manager.models.expense import Expense
# ==========================================================================================
# ==========================================================================================

# File:    expense_table_model.py
# Date:    October 23, 2026
# Author:  Jonathan A. Webb
# Purpose: Qt table model for expense records
# ==========================================================================================
# ==========================================================================================


class ExpenseTableModel(QAbstractTableModel):
    """Provide editable expense data to a QTableView."""

    HEADERS = (
        "ID", "Entry Date", "Purchase Date", "Vendor",
        "Cost", "Type", "Sub Type", "Validated",
        "Description",
    )

    FIELDS = (
        "id", "entry_date", "purchase_date", "vendor",
        "cost", "type", "sub_type", "validated",
        "description",
    )

    def __init__(self, parent=None):
        super().__init__(parent)
        self.expenses: list[Expense] = []
        self.original: list[Expense] = []

    def load_expenses(self, expenses: list[Expense]) -> None:
        """Replace the table contents and clear pending changes."""
        self.beginResetModel()
        self.expenses = [replace(e) for e in expenses]
        self.original = [replace(e) for e in expenses]
        self.endResetModel()

    def rowCount(self, parent=QModelIndex()) -> int:
        return 0 if parent.isValid() else len(self.expenses)

    def columnCount(self, parent=QModelIndex()) -> int:
        return 0 if parent.isValid() else len(self.FIELDS)

    def headerData(self, section, orientation, role):
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return self.HEADERS[section]
            return section + 1
        return None

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None

        expense = self.expenses[index.row()]
        field = self.FIELDS[index.column()]
        value = getattr(expense, field)

        if role == Qt.ItemDataRole.EditRole:
            return value

        if role == Qt.ItemDataRole.DisplayRole:
            if field == "cost":
                return f"${value / 100:,.2f}"
            if field == "validated":
                return "TRUE" if value else "FALSE"
            return "" if value is None else str(value)

        if role == Qt.ItemDataRole.TextAlignmentRole:
            if field in ("id", "cost"):
                return (
                    Qt.AlignmentFlag.AlignRight
                    | Qt.AlignmentFlag.AlignVCenter
                )

        return None

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags

        flags = (
            Qt.ItemFlag.ItemIsEnabled
            | Qt.ItemFlag.ItemIsSelectable
        )

        # Database-managed fields cannot be edited.
        if self.FIELDS[index.column()] not in ("id", "entry_date"):
            flags |= Qt.ItemFlag.ItemIsEditable

        return flags

    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
        """Update a cell in memory without writing to SQLite."""
        if role != Qt.ItemDataRole.EditRole or not index.isValid():
            return False

        field = self.FIELDS[index.column()]
        if field in ("id", "entry_date"):
            return False

        expense = self.expenses[index.row()]

        try:
            if field == "cost":
                if type(value) is not int:
                    return False

            elif field == "validated":
                if type(value) is not bool:
                    return False

            elif field == "type":
                if value not in CATEGORIES:
                    return False

            elif field == "sub_type":
                if value not in CATEGORIES[expense.type]:
                    return False

            elif field in ("vendor", "purchase_date"):
                if not isinstance(value, str) or not value.strip():
                    return False

            if field == "type":
                expense.type = value

                if expense.sub_type not in CATEGORIES[value]:
                    expense.sub_type = CATEGORIES[value][0]

                subtype_index = self.index(index.row(), 6)
                self.dataChanged.emit(
                    subtype_index,
                    subtype_index,
                )
            else:
                setattr(expense, field, value)

        except (TypeError, ValueError):
            return False

        self.dataChanged.emit(index, index)
        return True

    def add_expense(self, expense: Expense) -> None:
        """Append an unsaved expense."""
        row = len(self.expenses)
        self.beginInsertRows(QModelIndex(), row, row)
        self.expenses.append(expense)
        self.endInsertRows()

    def remove_expense(self, row: int) -> None:
        """Remove a row from the in-memory table."""
        if not 0 <= row < len(self.expenses):
            raise IndexError("Invalid expense row")

        self.beginRemoveRows(QModelIndex(), row, row)
        del self.expenses[row]
        self.endRemoveRows()

    def has_changes(self) -> bool:
        """Return True when table data differs from loaded data."""
        return self.expenses != self.original
# ==========================================================================================
# ==========================================================================================
# eof
