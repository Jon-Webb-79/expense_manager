
from dataclasses import replace

from PyQt6.QtCore import QAbstractTableModel, QModelIndex, Qt
from PyQt6.QtGui import QColor, QIcon, QPainter, QPixmap

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
        "ID",
        "Entry Date",
        "Purchase Date",
        "Vendor",
        "Cost",
        "Type",
        "Sub Type",
        "Validated",
        "Description",
    )

    FIELDS = (
        "id",
        "entry_date",
        "purchase_date",
        "vendor",
        "cost",
        "type",
        "sub_type",
        "validated",
        "description",
    )

    def __init__(self, parent=None):
        """Initialize the expense table model."""
        super().__init__(parent)

        self.expenses: list[Expense] = []
        self.original: list[Expense] = []

        # Generate and cache the validation icons.
        self.validated_icon = self.validation_icon(True)
        self.unvalidated_icon = self.validation_icon(False)

    # ======================================================================================
    # Qt Model Interface
    # ======================================================================================

    def rowCount(self, parent=QModelIndex()) -> int:
        """Return the number of expense records."""
        if parent.isValid():
            return 0

        return len(self.expenses)

    def columnCount(self, parent=QModelIndex()) -> int:
        """Return the number of expense attributes."""
        if parent.isValid():
            return 0

        return len(self.FIELDS)

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        """Return column and row header labels."""
        if role != Qt.ItemDataRole.DisplayRole:
            return None

        if orientation == Qt.Orientation.Horizontal:
            if 0 <= section < len(self.HEADERS):
                return self.HEADERS[section]
            return None

        return section + 1

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        """Return expense data according to the requested Qt role."""
        if not index.isValid():
            return None

        if not (
            0 <= index.row() < len(self.expenses)
            and 0 <= index.column() < len(self.FIELDS)
        ):
            return None

        expense = self.expenses[index.row()]
        field = self.FIELDS[index.column()]
        value = getattr(expense, field)

        # ------------------------------------------------------------------
        # Editing values
        # ------------------------------------------------------------------
        if role == Qt.ItemDataRole.EditRole:
            return value

        # ------------------------------------------------------------------
        # Display values
        # ------------------------------------------------------------------
        if role == Qt.ItemDataRole.DisplayRole:
            if field == "cost":
                return f"${value / 100:,.2f}"

            if field == "validated":
                return ""

            return "" if value is None else str(value)

        # ------------------------------------------------------------------
        # Validation status icons
        # ------------------------------------------------------------------
        if role == Qt.ItemDataRole.DecorationRole:
            if field == "validated":
                return (
                    self.validated_icon
                    if value
                    else self.unvalidated_icon
                )

        # ------------------------------------------------------------------
        # Cell alignment
        # ------------------------------------------------------------------
        if role == Qt.ItemDataRole.TextAlignmentRole:
            if field == "validated":
                return Qt.AlignmentFlag.AlignCenter

            if field in ("id", "cost"):
                return (
                    Qt.AlignmentFlag.AlignRight
                    | Qt.AlignmentFlag.AlignVCenter
                )

        # ------------------------------------------------------------------
        # Tooltips
        # ------------------------------------------------------------------
        if role == Qt.ItemDataRole.ToolTipRole:
            if field == "validated":
                return (
                    "Expense has been validated"
                    if value
                    else "Expense has not been validated"
                )

        return None

    def flags(self, index):
        """Return the interaction flags for a table cell."""
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags

        flags = (
            Qt.ItemFlag.ItemIsEnabled
            | Qt.ItemFlag.ItemIsSelectable
        )

        # Database-managed fields are read-only.
        if self.FIELDS[index.column()] not in ("id", "entry_date"):
            flags |= Qt.ItemFlag.ItemIsEditable

        return flags

    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
        """Modify an expense in memory without writing to SQLite."""
        if role != Qt.ItemDataRole.EditRole:
            return False

        if not index.isValid():
            return False

        if not (
            0 <= index.row() < len(self.expenses)
            and 0 <= index.column() < len(self.FIELDS)
        ):
            return False

        field = self.FIELDS[index.column()]

        # Prevent editing database-managed attributes.
        if field in ("id", "entry_date"):
            return False

        expense = self.expenses[index.row()]

        try:
            # --------------------------------------------------------------
            # Validate the incoming value.
            # --------------------------------------------------------------
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

            elif field == "description":
                if value is not None and not isinstance(value, str):
                    return False

            # --------------------------------------------------------------
            # Update the expense record.
            # --------------------------------------------------------------
            if field == "type":
                expense.type = value

                # Ensure the subtype remains valid for the selected type.
                if expense.sub_type not in CATEGORIES[value]:
                    expense.sub_type = CATEGORIES[value][0]

                    subtype_index = self.index(index.row(), 6)

                    self.dataChanged.emit(
                        subtype_index,
                        subtype_index,
                        [
                            Qt.ItemDataRole.DisplayRole,
                            Qt.ItemDataRole.EditRole,
                        ],
                    )

            else:
                setattr(expense, field, value)

        except (TypeError, ValueError, KeyError):
            return False

        # Notify Qt that the cell has changed.
        self.dataChanged.emit(
            index,
            index,
            [
                Qt.ItemDataRole.DisplayRole,
                Qt.ItemDataRole.EditRole,
                Qt.ItemDataRole.DecorationRole,
                Qt.ItemDataRole.ToolTipRole,
            ],
        )

        return True

    # ======================================================================================
    # Expense Data Management
    # ======================================================================================

    def load_expenses(self, expenses: list[Expense]) -> None:
        """Replace table contents and reset the change-tracking baseline."""
        self.beginResetModel()

        self.expenses = [replace(expense) for expense in expenses]
        self.original = [replace(expense) for expense in expenses]

        self.endResetModel()

    def add_expense(self, expense: Expense) -> None:
        """Append a new, unsaved expense to the table."""
        row = len(self.expenses)

        self.beginInsertRows(QModelIndex(), row, row)

        self.expenses.append(replace(expense))

        self.endInsertRows()

    def remove_expense(self, row: int) -> None:
        """Remove an expense from the in-memory table."""
        if not 0 <= row < len(self.expenses):
            raise IndexError("Invalid expense row")

        self.beginRemoveRows(QModelIndex(), row, row)

        del self.expenses[row]

        self.endRemoveRows()

    def has_changes(self) -> bool:
        """Determine whether unsaved changes exist."""
        return self.expenses != self.original

    # ======================================================================================
    # Validation Icon Generation
    # ======================================================================================

    @staticmethod
    def validation_icon(validated: bool) -> QIcon:
        """Generate a green checkmark or gray X icon."""
        size = 20

        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)

        painter.setRenderHint(
            QPainter.RenderHint.Antialiasing
        )

        color = (
            QColor("#2EAD60")
            if validated
            else QColor("#999999")
        )

        pen = painter.pen()
        pen.setColor(color)
        pen.setWidth(2)
        painter.setPen(pen)

        # Draw the surrounding circle.
        painter.drawEllipse(2, 2, 16, 16)

        if validated:
            # Green checkmark.
            painter.drawLine(6, 10, 9, 13)
            painter.drawLine(9, 13, 15, 6)

        else:
            # Gray X.
            painter.drawLine(7, 7, 13, 13)
            painter.drawLine(13, 7, 7, 13)

        painter.end()

        return QIcon(pixmap)

# ==========================================================================================
# ==========================================================================================
# eof
