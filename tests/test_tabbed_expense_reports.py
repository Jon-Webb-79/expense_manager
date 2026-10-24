import pytest

from expense_manager.models.expense_summary import ExpenseSummary
from expense_manager.models.vendor_summary import VendorSummary
from expense_manager.views.expense_summary_dialog import ExpenseSummaryDialog
# ==========================================================================================
# ==========================================================================================
# File:    test_tabbed_expense_reports.py
# Date:    October 24, 2026
# Author:  Jonathan A. Webb
# Purpose: Describe the types of testing to occur in this file.
# ==========================================================================================
# ==========================================================================================
# Insert Code here

@pytest.fixture
def dialog(qtbot):
    window = ExpenseSummaryDialog()
    qtbot.addWidget(window)
    return window


def test_report_tabs_exist(dialog):
    """Both report tabs should be available."""
    assert dialog.tabs.count() == 2
    assert dialog.tabs.tabText(0) == "Type / Subtype"
    assert dialog.tabs.tabText(1) == "Vendors"


def test_window_title(dialog):
    assert dialog.windowTitle() == "Expense Reports"


def test_display_both_reports(dialog):
    """Both reports should display totals for the same transactions."""
    expense_summaries = [
        ExpenseSummary("FOOD", "GROCERIES", -12500, 2),
        ExpenseSummary("GAS", "NA", -4000, 1),
    ]

    vendor_summaries = [
        VendorSummary("Walmart", -12500, 2),
        VendorSummary("Chevron", -4000, 1),
    ]

    dialog.display_reports(
        expense_summaries,
        vendor_summaries,
    )

    assert dialog.summary_model.rowCount() == 2
    assert dialog.vendor_model.rowCount() == 2

    assert dialog.summary_model.grand_total_cents() == -16500
    assert dialog.vendor_model.grand_total_cents() == -16500

    assert dialog.grand_total_label.text() == (
        "Net Total: -$165.00"
    )


def test_empty_reports(dialog):
    """An empty reporting period should clear both tabs."""
    dialog.display_reports([], [])

    assert dialog.summary_model.rowCount() == 0
    assert dialog.vendor_model.rowCount() == 0
    assert dialog.grand_total_label.text() == (
        "Net Total: $0.00 (No transactions)"
    )


def test_mismatched_totals_raise_error(dialog):
    """Category and vendor totals must agree."""
    expense_summaries = [
        ExpenseSummary("FOOD", "GROCERIES", -10000, 1),
    ]

    vendor_summaries = [
        VendorSummary("Walmart", -9000, 1),
    ]

    with pytest.raises(ValueError, match="totals do not agree"):
        dialog.display_reports(
            expense_summaries,
            vendor_summaries,
        )


def test_vendor_report_replaces_previous_data(dialog):
    """Regenerating reports should replace existing vendor rows."""
    dialog.display_reports(
        [ExpenseSummary("FOOD", "GROCERIES", -10000, 1)],
        [VendorSummary("Walmart", -10000, 1)],
    )

    dialog.display_reports(
        [ExpenseSummary("GAS", "NA", -5000, 1)],
        [VendorSummary("Chevron", -5000, 1)],
    )

    assert dialog.vendor_model.rowCount() == 1
    assert dialog.vendor_model.item(0, 0).text() == "Chevron"
    assert dialog.grand_total_label.text() == "Net Total: -$50.00"


def test_switching_tabs_preserves_data(dialog):
    """Switching tabs should not discard report results."""
    dialog.display_reports(
        [ExpenseSummary("FOOD", "GROCERIES", -2500, 1)],
        [VendorSummary("Costco", -2500, 1)],
    )

    dialog.tabs.setCurrentIndex(1)
    assert dialog.vendor_model.rowCount() == 1

    dialog.tabs.setCurrentIndex(0)
    assert dialog.summary_model.rowCount() == 1

    assert dialog.grand_total_label.text() == "Net Total: -$25.00"

# ==========================================================================================
# ==========================================================================================
# eof
