from collections.abc import Callable, Iterable

from PyQt6.QtCore import QDate, QSortFilterProxyModel, Qt
from PyQt6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QDoubleSpinBox,
    QLineEdit,
    QStyledItemDelegate,
)

from expense_manager.database.schema import CATEGORIES
from expense_manager.views.vendor_autocomplete import (
    configure_vendor_autocomplete,
)
# ==========================================================================================
# ==========================================================================================

# File:    delegates.py
# Date:    October 23, 2026
# Author:  Jonathan A. Webb
# Purpose: Custom editors for the expense table
# ==========================================================================================
# ==========================================================================================

class ExpenseDelegate(QStyledItemDelegate):
    """Provide column-specific table cell editors."""

    def __init__(
        self,
        parent=None,
        vendor_provider: Callable[[], Iterable[str]] | None = None,
    ):
        super().__init__(parent)
        self.vendor_provider = vendor_provider or (lambda: [])

    @staticmethod
    def _source_index(index):
        """Map a proxy index to the underlying expense model."""
        model = index.model()

        if isinstance(model, QSortFilterProxyModel):
            return model.mapToSource(index)

        return index

    def createEditor(self, parent, option, index):
        column = index.column()

        if column == 2:
            editor = QDateEdit(parent)
            editor.setCalendarPopup(True)
            editor.setDisplayFormat("yyyy-MM-dd")
            return editor

        if column == 3:
            editor = QLineEdit(parent)
            configure_vendor_autocomplete(
                editor,
                self.vendor_provider(),
            )
            return editor

        if column == 4:
            editor = QDoubleSpinBox(parent)
            editor.setDecimals(2)
            editor.setRange(-999999999.99, 999999999.99)
            editor.setPrefix("$")
            return editor

        if column in (5, 6, 7):
            editor = QComboBox(parent)

            if column == 5:
                editor.addItems(CATEGORIES.keys())

            elif column == 6:
                source_index = self._source_index(index)
                expense = source_index.model().expenses[
                    source_index.row()
                ]
                editor.addItems(CATEGORIES[expense.type])

            else:
                editor.addItems(["FALSE", "TRUE"])

            return editor

        return super().createEditor(parent, option, index)

    def setEditorData(self, editor, index):
        value = index.data(Qt.ItemDataRole.DisplayRole)

        if isinstance(editor, QDateEdit):
            date = QDate.fromString(value, "yyyy-MM-dd")
            editor.setDate(
                date if date.isValid() else QDate.currentDate()
            )

        elif isinstance(editor, QDoubleSpinBox):
            cents = index.model().data(
                index,
                Qt.ItemDataRole.EditRole,
            )
            editor.setValue(cents / 100)

        elif isinstance(editor, QComboBox):
            raw = index.model().data(
                index,
                Qt.ItemDataRole.EditRole,
            )
            text = (
                "TRUE" if raw else "FALSE"
            ) if isinstance(raw, bool) else str(raw)
            editor.setCurrentText(text)

        else:
            super().setEditorData(editor, index)

    def setModelData(self, editor, model, index):
        if isinstance(editor, QDateEdit):
            value = editor.date().toString("yyyy-MM-dd")

        elif isinstance(editor, QDoubleSpinBox):
            value = round(editor.value() * 100)

        elif isinstance(editor, QComboBox):
            value = editor.currentText()

            if index.column() == 7:
                value = value == "TRUE"

        elif isinstance(editor, QLineEdit) and index.column() == 3:
            value = editor.text().strip()

        else:
            super().setModelData(editor, model, index)
            return

        model.setData(index, value)


# ==========================================================================================
# ==========================================================================================
# eof
