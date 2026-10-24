from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QComboBox, QStyleOptionViewItem

from expense_manager.models.expense import Expense
from expense_manager.views.main_window import MainWindow
# ==========================================================================================
# ==========================================================================================
# File:    test_expense_table_proxy_integration.py
# Date:    October 24, 2026
# Author:  Jonathan A. Webb
# Purpose: Describe the types of testing to occur in this file.

# ==========================================================================================
# ==========================================================================================

def make_expense(expense_id, purchase_date, vendor, expense_type, subtype):
    return Expense(
        id=expense_id,
        entry_date="2026-10-01",
        purchase_date=purchase_date,
        vendor=vendor,
        cost=-1000,
        type=expense_type,
        sub_type=subtype,
        validated=False,
        description=None,
    )


def test_table_uses_proxy_model(qtbot):
    window = MainWindow()
    qtbot.addWidget(window)

    assert window.table.model() is window.filter_model
    assert window.filter_model.sourceModel() is window.table_model


def test_default_sort_newest_first(qtbot):
    window = MainWindow()
    qtbot.addWidget(window)

    window.table_model.load_expenses(
        [
            make_expense(1, "2026-10-01", "A", "FOOD", "GROCERIES"),
            make_expense(2, "2026-10-20", "B", "GAS", "NA"),
            make_expense(3, "2026-10-10", "C", "AUTO", "NA"),
        ]
    )

    source_index = window.filter_model.mapToSource(
        window.filter_model.index(0, 0)
    )

    assert window.table_model.expenses[source_index.row()].id == 2


def test_selected_row_maps_to_source(qtbot):
    window = MainWindow()
    qtbot.addWidget(window)

    window.table_model.load_expenses(
        [
            make_expense(1, "2026-10-01", "A", "FOOD", "GROCERIES"),
            make_expense(2, "2026-10-20", "B", "GAS", "NA"),
        ]
    )

    window.table.selectRow(0)

    assert window.selected_row() == 1


def test_subtype_editor_uses_correct_expense(qtbot):
    window = MainWindow()
    qtbot.addWidget(window)

    window.table_model.load_expenses(
        [
            make_expense(1, "2026-10-01", "A", "FOOD", "GROCERIES"),
            make_expense(2, "2026-10-20", "B", "GAS", "NA"),
        ]
    )

    delegate = window.table.itemDelegate()
    index = window.filter_model.index(0, 6)

    editor = delegate.createEditor(
        window.table,
        QStyleOptionViewItem(),
        index,
    )

    assert isinstance(editor, QComboBox)
    assert [
        editor.itemText(i) for i in range(editor.count())
    ] == ["NA"]
# ==========================================================================================
# ==========================================================================================
# eof
