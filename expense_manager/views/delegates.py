from PyQt6.QtCore import Qt
from PyQt6.QtCore import QDate
from PyQt6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QDoubleSpinBox,
    QStyledItemDelegate,
)

from expense_manager.database.schema import CATEGORIES

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

    def createEditor(self, parent, option, index):
        column = index.column()

        if column == 2:
            editor = QDateEdit(parent)
            editor.setCalendarPopup(True)
            editor.setDisplayFormat("yyyy-MM-dd")
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
                expense = index.model().expenses[index.row()]
                editor.addItems(CATEGORIES[expense.type])

            else:
                editor.addItems(["FALSE", "TRUE"])

            return editor

        return super().createEditor(parent, option, index)

    def setEditorData(self, editor, index):
        value = index.data(Qt.ItemDataRole.DisplayRole) 

        if isinstance(editor, QDateEdit):
            date = QDate.fromString(value, "yyyy-MM-dd")
            editor.setDate(date if date.isValid() else QDate.currentDate())

        elif isinstance(editor, QDoubleSpinBox):
            cents = index.model().data(
                index,
                2,  # Qt.ItemDataRole.EditRole
            )
            editor.setValue(cents / 100)

        elif isinstance(editor, QComboBox):
            raw = index.model().data(index, 2)
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

        else:
            super().setModelData(editor, model, index)
            return

        model.setData(index, value)


# ==========================================================================================
# ==========================================================================================
# eof
