import pytest

from PyQt6.QtCore import Qt

from expense_manager.models.vendor_summary import VendorSummary
from expense_manager.models.vendor_summary_model import VendorSummaryModel
# ==========================================================================================
# ==========================================================================================
# File:    test_vendor_summary_model.py
# Date:    October 24, 2026
# Author:  Jonathan A. Webb
# Purpose: Describe the types of testing to occur in this file.

# ==========================================================================================
# ==========================================================================================

@pytest.fixture
def model(qtbot):
    """Create an empty vendor summary model."""
    return VendorSummaryModel()


def test_model_initialization(model):
    """The model should start empty with the correct headers."""
    assert model.rowCount() == 0
    assert model.columnCount() == 3
    assert model.grand_total_cents() == 0

    assert model.headerData(
        0, Qt.Orientation.Horizontal
    ) == "Vendor"

    assert model.headerData(
        1, Qt.Orientation.Horizontal
    ) == "Total"

    assert model.headerData(
        2, Qt.Orientation.Horizontal
    ) == "Transactions"


def test_load_vendor_summary(model):
    """Vendor data should populate the correct columns."""
    summaries = [
        VendorSummary("Walmart", -20000, 2),
        VendorSummary("Chevron", -4000, 1),
    ]

    model.load_summary(summaries)

    assert model.rowCount() == 2

    assert model.item(0, 0).text() == "Walmart"
    assert model.item(0, 1).text() == "-$200.00"
    assert model.item(0, 2).text() == "2"

    assert model.item(1, 0).text() == "Chevron"
    assert model.item(1, 1).text() == "-$40.00"
    assert model.item(1, 2).text() == "1"


def test_grand_total(model):
    """Grand total should include all signed vendor totals."""
    summaries = [
        VendorSummary("Walmart", -20000, 2),
        VendorSummary("Chevron", -4000, 1),
        VendorSummary("Employer", 250000, 1),
    ]

    model.load_summary(summaries)

    assert model.grand_total_cents() == 226000


def test_currency_formatting(model):
    """Currency formatting should handle signs and large values."""
    assert model._format_currency(-123456789) == "-$1,234,567.89"
    assert model._format_currency(123456789) == "$1,234,567.89"
    assert model._format_currency(0) == "$0.00"
    assert model._format_currency(-5) == "-$0.05"


def test_numeric_sort_values(model):
    """Numeric columns should retain integer values for sorting."""
    model.load_summary(
        [
            VendorSummary("Amazon", -12500, 3),
        ]
    )

    assert model.item(0, 1).data(
        Qt.ItemDataRole.UserRole
    ) == -12500

    assert model.item(0, 2).data(
        Qt.ItemDataRole.UserRole
    ) == 3


def test_items_are_read_only(model):
    """Report cells must not be editable."""
    model.load_summary(
        [
            VendorSummary("Costco", -5000, 1),
        ]
    )

    for column in range(model.columnCount()):
        assert not model.item(0, column).isEditable()


def test_reload_replaces_existing_data(model):
    """Generating another report should replace previous results."""
    model.load_summary(
        [
            VendorSummary("Walmart", -10000, 1),
            VendorSummary("Chevron", -5000, 1),
        ]
    )

    model.load_summary(
        [
            VendorSummary("Amazon", -2500, 1),
        ]
    )

    assert model.rowCount() == 1
    assert model.item(0, 0).text() == "Amazon"
    assert model.grand_total_cents() == -2500


def test_empty_summary(model):
    """An empty report should clear the model and totals."""
    model.load_summary(
        [
            VendorSummary("Walmart", -10000, 1),
        ]
    )

    model.load_summary([])

    assert model.rowCount() == 0
    assert model.grand_total_cents() == 0


def test_sort_by_total(model):
    """Sorting should use numeric totals rather than dollar strings."""
    model.load_summary(
        [
            VendorSummary("Small", -1000, 1),
            VendorSummary("Large", -100000, 1),
            VendorSummary("Medium", -10000, 1),
        ]
    )

    model.setSortRole(Qt.ItemDataRole.UserRole)
    model.sort(1, Qt.SortOrder.AscendingOrder)

    assert [
        model.item(row, 0).text()
        for row in range(model.rowCount())
    ] == ["Large", "Medium", "Small"]


def test_sort_by_transaction_count(model):
    """Sorting by transaction count should be numerical."""
    model.load_summary(
        [
            VendorSummary("One", -1000, 1),
            VendorSummary("Ten", -10000, 10),
            VendorSummary("Two", -2000, 2),
        ]
    )

    model.setSortRole(Qt.ItemDataRole.UserRole)
    model.sort(2, Qt.SortOrder.DescendingOrder)

    assert [
        model.item(row, 0).text()
        for row in range(model.rowCount())
    ] == ["Ten", "Two", "One"]

# ==========================================================================================
# ==========================================================================================
# eof
