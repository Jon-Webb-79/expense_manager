import pytest

from expense_manager.models.expense_summary import ExpenseSummary
from expense_manager.models.expense_summary_model import ExpenseSummaryModel
# ==========================================================================================
# ==========================================================================================
# File:    test_expense_summary_model.py
# Date:    October 23, 2026
# Author:  Jonathan A. Webb
# Purpose: Describe the types of testing to occur in this file.
# Instruction: This code can be run in hte following ways
# ==========================================================================================
# ==========================================================================================

@pytest.fixture
def model(qapp):
    """Create a Qt summary model."""
    return ExpenseSummaryModel()


def test_empty_summary(model):
    """An empty report should contain no categories."""
    model.load_summary([])

    assert model.rowCount() == 0
    assert model.grand_total_cents() == 0


def test_summary_parent_totals(model):
    """Parent rows should sum their subtype amounts."""
    model.load_summary([
        ExpenseSummary("FOOD", "GROCERIES", -21000, 2),
        ExpenseSummary("FOOD", "RESTAURANT", -4500, 1),
        ExpenseSummary("GAS", "NA", -6000, 1),
    ])

    assert model.rowCount() == 2

    food = model.item(0, 0)
    assert food is not None
    assert food.text() == "FOOD"
    assert food.rowCount() == 2

    assert model.item(0, 1).text() == "-$255.00"
    assert model.item(0, 2).text() == "3"


def test_na_subtype_is_hidden(model):
    """Categories with NA subtypes should not have child rows."""
    model.load_summary([
        ExpenseSummary("GAS", "NA", -6000, 1),
    ])

    gas = model.item(0, 0)

    assert gas is not None
    assert gas.rowCount() == 0


def test_grand_total(model):
    """Grand total should preserve positive and negative values."""
    model.load_summary([
        ExpenseSummary("FOOD", "GROCERIES", -5000, 1),
        ExpenseSummary("PAYCHECK", "NA", 250000, 1),
    ])

    assert model.grand_total_cents() == 245000


def test_model_is_read_only(model):
    """Report items should not be editable."""
    model.load_summary([
        ExpenseSummary("FOOD", "GROCERIES", -5000, 1),
    ])

    item = model.item(0, 0)

    assert item is not None
    assert not item.isEditable()

# ==========================================================================================
# ==========================================================================================
# eof
