import sqlite3

import pytest

from expense_manager.database.account_repository import AccountRepository
from expense_manager.database.schema import create_schema
# ==========================================================================================
# ==========================================================================================
# File:    test_account_repository.py
# Date:    October 24, 2026
# Author:  Jonathan A. Webb
# Purpose: Describe the types of testing to occur in this file.
# ==========================================================================================
# ==========================================================================================

@pytest.fixture
def repository():
    connection = sqlite3.connect(":memory:")
    connection.execute("PRAGMA foreign_keys = ON")
    create_schema(connection)

    repo = AccountRepository(connection)

    yield repo

    connection.close()


def insert_expense(connection, purchase_date, cost):
    connection.execute(
        """
        INSERT INTO expense (
            purchase_date,
            vendor,
            cost,
            type,
            sub_type
        )
        VALUES (?, 'Test Vendor', ?, 'MISC', 'NA')
        """,
        (purchase_date, cost),
    )


def test_account_configuration(repository):
    repository.configure_account(
        name="Checking",
        start_date="2026-10-01",
        opening_balance=500000,
    )

    account = repository.get_account()

    assert account["name"] == "Checking"
    assert account["opening_balance"] == 500000


def test_daily_balance_calculation(repository):
    connection = repository.connection

    insert_expense(connection, "2026-10-01", -10000)
    insert_expense(connection, "2026-10-01", -2500)
    insert_expense(connection, "2026-10-03", 200000)

    repository.configure_account(
        name="Checking",
        start_date="2026-10-01",
        opening_balance=500000,
    )

    repository.recalculate_balances(
        through_date="2026-10-04"
    )

    balances = repository.get_daily_balances()

    assert len(balances) == 4

    assert balances[0]["daily_change"] == -12500
    assert balances[0]["closing_balance"] == 487500

    assert balances[1]["daily_change"] == 0
    assert balances[1]["closing_balance"] == 487500

    assert balances[2]["daily_change"] == 200000
    assert balances[2]["closing_balance"] == 687500

    assert balances[3]["daily_change"] == 0
    assert balances[3]["closing_balance"] == 687500


def test_recalculation_updates_history(repository):
    connection = repository.connection

    insert_expense(connection, "2026-10-01", -10000)

    repository.configure_account(
        name="Checking",
        start_date="2026-10-01",
        opening_balance=500000,
    )

    repository.recalculate_balances(
        through_date="2026-10-02"
    )

    assert repository.get_current_balance() == 490000

    insert_expense(connection, "2026-10-01", -5000)

    repository.recalculate_balances(
        through_date="2026-10-02"
    )

    assert repository.get_current_balance() == 485000


def test_start_date_cannot_follow_expenses(repository):
    insert_expense(
        repository.connection,
        "2026-10-01",
        -10000,
    )

    with pytest.raises(ValueError):
        repository.configure_account(
            name="Checking",
            start_date="2026-10-02",
            opening_balance=500000,
        )


def test_unconfigured_account(repository):
    assert repository.get_account() is None
    assert repository.get_current_balance() is None

    repository.recalculate_balances()

    assert repository.get_daily_balances() == []

# ==========================================================================================
# ==========================================================================================
# eof
