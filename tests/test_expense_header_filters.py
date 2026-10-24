from datetime import date

from PyQt6.QtCore import Qt

from expense_manager.models.expense import Expense
from expense_manager.views.main_window import MainWindow
# ==========================================================================================
# ==========================================================================================
# File:    test_expense_header_filters.py
# Date:    October 24, 2026
# Author:  Jonathan A. Webb
# Purpose: Describe the types of testing to occur in this file.
# ==========================================================================================
# ==========================================================================================

def make_expense(
    expense_id,
    purchase_date,
    vendor,
    expense_type,
    subtype,
):
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


def test_header_context_menu_enabled(qtbot):
    window = MainWindow()
    qtbot.addWidget(window)

    header = window.table.horizontalHeader()

    assert header.contextMenuPolicy() == (
        Qt.ContextMenuPolicy.CustomContextMenu
    )


def test_clear_vendor_filter_preserves_date_filter(qtbot):
    window = MainWindow()
    qtbot.addWidget(window)

    window.table_model.load_expenses([
        make_expense(
            1, "2026-10-05", "Walmart", "FOOD", "GROCERIES"
        ),
        make_expense(
            2, "2026-10-15", "Costco", "FOOD", "GROCERIES"
        ),
        make_expense(
            3, "2026-09-20", "Walmart", "GAS", "NA"
        ),
    ])

    window.filter_model.set_date_filter(
        date(2026, 10, 1),
        date(2026, 10, 31),
    )
    window.filter_model.set_vendor_filter("Walmart")

    assert window.filter_model.rowCount() == 1

    window.clear_column_filter(window.VENDOR_COLUMN)

    assert window.filter_model.rowCount() == 2
    assert window.filter_model._start_date == date(2026, 10, 1)


def test_clear_all_filters(qtbot):
    window = MainWindow()
    qtbot.addWidget(window)

    window.table_model.load_expenses([
        make_expense(
            1, "2026-10-05", "Walmart", "FOOD", "GROCERIES"
        ),
        make_expense(
            2, "2026-10-15", "Costco", "GAS", "NA"
        ),
    ])

    window.filter_model.set_vendor_filter("Walmart")
    assert window.filter_model.rowCount() == 1

    window.clear_all_filters()

    assert window.filter_model.rowCount() == 2
    assert "Showing 2 of 2" in (
        window.statusBar().currentMessage()
    )


def test_type_and_subtype_filters(qtbot):
    window = MainWindow()
    qtbot.addWidget(window)

    window.table_model.load_expenses([
        make_expense(
            1, "2026-10-05", "Walmart", "FOOD", "GROCERIES"
        ),
        make_expense(
            2, "2026-10-15", "Costco", "FOOD", "RESTAURANT"
        ),
        make_expense(
            3, "2026-10-20", "Chevron", "GAS", "NA"
        ),
    ])

    window.filter_model.set_type_filter("FOOD")
    window.filter_model.set_subtype_filter("GROCERIES")

    assert window.filter_model.rowCount() == 1

    window.clear_column_filter(window.SUBTYPE_COLUMN)

    assert window.filter_model.rowCount() == 2

# ==========================================================================================
# ==========================================================================================
# eof
