from datetime import date

import pytest

from PyQt6.QtCore import Qt

from expense_manager.models.expense import Expense
from expense_manager.models.expense_filter_proxy_model import (
    ExpenseFilterProxyModel,
)
from expense_manager.models.expense_table_model import ExpenseTableModel
# ==========================================================================================
# ==========================================================================================
# File:    test_expense_filter_proxy_model.py
# Date:    October 24, 2026
# Author:  Jonathan A. Webb
# Purpose: Describe the types of testing to occur in this file.
# ==========================================================================================
# ==========================================================================================

@pytest.fixture
def proxy(qtbot):
    """Create a source model containing representative expenses."""
    expenses = [
        Expense(
            id=1,
            entry_date="2026-10-01",
            purchase_date="2026-10-05",
            vendor="Walmart",
            cost=-12500,
            type="FOOD",
            sub_type="GROCERIES",
            validated=False,
            description=None,
        ),
        Expense(
            id=2,
            entry_date="2026-10-01",
            purchase_date="2026-10-15",
            vendor="Chevron",
            cost=-4000,
            type="GAS",
            sub_type="NA",
            validated=False,
            description=None,
        ),
        Expense(
            id=3,
            entry_date="2026-10-01",
            purchase_date="2026-10-20",
            vendor="Walmart",
            cost=-7500,
            type="AUTO",
            sub_type="NA",
            validated=False,
            description=None,
        ),
        Expense(
            id=4,
            entry_date="2026-10-01",
            purchase_date="2026-09-25",
            vendor="Costco",
            cost=-10000,
            type="FOOD",
            sub_type="GROCERIES",
            validated=False,
            description=None,
        ),
        Expense(
            id=5,
            entry_date="2026-10-01",
            purchase_date="2026-10-25",
            vendor="Walmart",
            cost=-5000,
            type="FOOD",
            sub_type="RESTAURANT",
            validated=False,
            description=None,
        ),
    ]

    source = ExpenseTableModel()
    source.load_expenses(expenses)

    model = ExpenseFilterProxyModel()
    model.setSourceModel(source)

    # Keep the source model alive for the duration of the test.
    model._test_source = source

    return model


def visible_ids(proxy):
    """Return expense IDs in the order currently displayed."""
    source = proxy.sourceModel()

    return [
        source.expenses[
            proxy.mapToSource(proxy.index(row, 0)).row()
        ].id
        for row in range(proxy.rowCount())
    ]


def test_no_filters(proxy):
    assert proxy.rowCount() == 5


def test_date_filter(proxy):
    proxy.set_date_filter(
        date(2026, 10, 1),
        date(2026, 10, 20),
    )

    assert set(visible_ids(proxy)) == {1, 2, 3}


def test_date_filter_includes_boundaries(proxy):
    proxy.set_date_filter(
        date(2026, 10, 5),
        date(2026, 10, 15),
    )

    assert set(visible_ids(proxy)) == {1, 2}


def test_invalid_date_range(proxy):
    with pytest.raises(ValueError):
        proxy.set_date_filter(
            date(2026, 10, 31),
            date(2026, 10, 1),
        )


def test_vendor_filter_case_insensitive(proxy):
    proxy.set_vendor_filter("walmart")

    assert set(visible_ids(proxy)) == {1, 3, 5}


def test_type_filter(proxy):
    proxy.set_type_filter("FOOD")

    assert set(visible_ids(proxy)) == {1, 4, 5}


def test_subtype_filter(proxy):
    proxy.set_subtype_filter("GROCERIES")

    assert set(visible_ids(proxy)) == {1, 4}


def test_combined_filters(proxy):
    proxy.set_date_filter(
        date(2026, 10, 1),
        date(2026, 10, 31),
    )
    proxy.set_vendor_filter("Walmart")
    proxy.set_type_filter("FOOD")
    proxy.set_subtype_filter("GROCERIES")

    assert visible_ids(proxy) == [1]


def test_clear_filters(proxy):
    proxy.set_vendor_filter("Walmart")
    proxy.set_type_filter("FOOD")

    assert proxy.rowCount() == 2

    proxy.clear_filters()

    assert proxy.rowCount() == 5


def test_sort_newest_first(proxy):
    proxy.sort(
        2,
        Qt.SortOrder.DescendingOrder,
    )

    assert visible_ids(proxy) == [5, 3, 2, 1, 4]


def test_sort_cost_ascending(proxy):
    proxy.sort(
        4,
        Qt.SortOrder.AscendingOrder,
    )

    assert visible_ids(proxy) == [1, 4, 3, 5, 2]


def test_type_change_clears_invalid_subtype(proxy):
    proxy.set_type_filter("FOOD")
    proxy.set_subtype_filter("GROCERIES")

    proxy.set_type_filter("GAS")

    assert visible_ids(proxy) == [2]


def test_filter_does_not_modify_source(proxy):
    source = proxy.sourceModel()

    original_ids = [
        expense.id for expense in source.expenses
    ]

    proxy.set_vendor_filter("Walmart")

    assert [
        expense.id for expense in source.expenses
    ] == original_ids

# ==========================================================================================
# ==========================================================================================
# eof
