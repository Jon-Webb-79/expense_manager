import pytest

from expense_manager.models.expense_summary import ExpenseSummary
from expense_manager.views.expense_summary_dialog import ExpenseSummaryDialog
# ==========================================================================================
# ==========================================================================================
# File:    test_expense_summary.py
# Date:    October 23, 2026
# Author:  Jonathan A. Webb
# Purpose: Describe the types of testing to occur in this file.
# Instruction: This code can be run in hte following ways
# ==========================================================================================
# ==========================================================================================

@pytest.fixture
def dialog(qtbot):
    """Create the dialog for testing."""
    window = ExpenseSummaryDialog()
    qtbot.addWidget(window)
    return window


def test_dialog_initialization(dialog):
    """Verify that the dialog initializes correctly."""
    assert dialog.windowTitle() == "Expense Reports"
    assert dialog.summary_model.rowCount() == 0
    assert dialog.grand_total_label.text() == "Net Total: $0.00"


def test_date_range(dialog):
    """Verify that date selectors return ISO-formatted dates."""
    start_date, end_date = dialog.get_date_range()

    assert len(start_date) == 10
    assert len(end_date) == 10
    assert start_date[4] == "-"
    assert end_date[4] == "-"


def test_display_summary(dialog):
    """Verify that summary data populates the report."""
    summaries = [
        ExpenseSummary("FOOD", "GROCERIES", -12500, 2),
        ExpenseSummary("FOOD", "RESTAURANT", -4500, 1),
        ExpenseSummary("GAS", "NA", -6000, 1),
    ]

    dialog.display_summary(summaries)

    assert dialog.summary_model.rowCount() == 2
    assert dialog.summary_model.grand_total_cents() == -23000
    assert dialog.grand_total_label.text() == "Net Total: -$230.00"


def test_empty_report(dialog):
    """Verify that an empty report displays a zero total."""
    dialog.display_summary([])

    assert dialog.summary_model.rowCount() == 0
    assert dialog.grand_total_label.text() == "Net Total: $0.00"

# ==========================================================================================
# ==========================================================================================
# eof
