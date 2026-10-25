import pytest

from PyQt6.QtCore import Qt

from expense_manager.models.daily_balance_table_model import (
    DailyBalanceTableModel,
)
# ==========================================================================================
# ==========================================================================================
# File:    test_daily_balance_table_model.py
# Date:    October 24, 2026
# Author:  Jonathan A. Webb
# Purpose: Describe the types of testing to occur in this file.
# ==========================================================================================
# ==========================================================================================

@pytest.fixture
def model(qapp):
    """Create a daily balance model."""
    return DailyBalanceTableModel()


def test_empty_model(model):
    assert model.rowCount() == 0
    assert model.columnCount() == 3


def test_load_balances(model):
    balances = [
        {
            "balance_date": "2026-10-01",
            "daily_change": -12500,
            "closing_balance": 487500,
        },
        {
            "balance_date": "2026-10-02",
            "daily_change": 0,
            "closing_balance": 487500,
        },
    ]

    model.load_balances(balances)

    assert model.rowCount() == 2
    assert model.columnCount() == 3


def test_display_data(model):
    model.load_balances(
        [
            {
                "balance_date": "2026-10-01",
                "daily_change": -12500,
                "closing_balance": 487500,
            }
        ]
    )

    date_index = model.index(0, 0)
    change_index = model.index(0, 1)
    balance_index = model.index(0, 2)

    assert model.data(date_index) == "2026-10-01"
    assert model.data(change_index) == "$-125.00"
    assert model.data(balance_index) == "$4,875.00"


def test_edit_role_returns_raw_values(model):
    model.load_balances(
        [
            {
                "balance_date": "2026-10-01",
                "daily_change": -12500,
                "closing_balance": 487500,
            }
        ]
    )

    index = model.index(0, 1)

    assert model.data(
        index,
        Qt.ItemDataRole.EditRole,
    ) == -12500


def test_model_is_read_only(model):
    model.load_balances(
        [
            {
                "balance_date": "2026-10-01",
                "daily_change": -12500,
                "closing_balance": 487500,
            }
        ]
    )

    index = model.index(0, 1)

    assert not (
        model.flags(index)
        & Qt.ItemFlag.ItemIsEditable
    )


def test_reloading_balances(model):
    model.load_balances(
        [
            {
                "balance_date": "2026-10-01",
                "daily_change": 0,
                "closing_balance": 500000,
            }
        ]
    )

    model.load_balances([])

    assert model.rowCount() == 0

# ==========================================================================================
# ==========================================================================================
# eof
