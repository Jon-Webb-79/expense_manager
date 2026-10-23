# Import necessary packages here
import sqlite3
import pytest

# ==========================================================================================
# ==========================================================================================
# File:    test.py
# Date:    October 21, 2026
# Author:  Jonathan A. Webb
# Purpose: Tests database functions and classes
# ==========================================================================================
# ==========================================================================================

from expense_manager.database.connection import (
    create_database,
    open_database,
)
from expense_manager.database.repository import ExpenseRepository


@pytest.fixture
def database(tmp_path):
    """Create a temporary database for each test."""
    connection = create_database(
        tmp_path / "test_expenses.db"
    )
    yield connection
    connection.close()


def test_database_creation(database):
    """Verify the expense table exists."""
    result = database.execute(
        """
        SELECT name FROM sqlite_master
        WHERE type = 'table' AND name = 'expense'
        """
    ).fetchone()

    assert result is not None


def test_add_expense(database):
    """Verify expense insertion and default values."""
    repository = ExpenseRepository(database)

    expense_id = repository.add_expense(
        purchase_date="2026-10-21",
        vendor="Smiths",
        cost=-8532,
        type="FOOD",
        sub_type="GROCERIES",
    )

    expense = repository.get_expense(expense_id)

    assert expense["vendor"] == "Smiths"
    assert expense["cost"] == -8532
    assert expense["validated"] == 0


def test_invalid_subtype(database):
    """Reject invalid type/subtype combinations."""
    repository = ExpenseRepository(database)

    with pytest.raises(ValueError):
        repository.add_expense(
            purchase_date="2026-10-21",
            vendor="Smiths",
            cost=-8532,
            type="FOOD",
            sub_type="HOUSING",
        )


def test_database_constraint(database):
    """Verify SQLite independently rejects invalid data."""
    with pytest.raises(sqlite3.IntegrityError):
        database.execute(
            """
            INSERT INTO expense (
                purchase_date, vendor, cost,
                type, sub_type
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                "2026-10-21",
                "Smiths",
                -8532,
                "FOOD",
                "HOUSING",
            ),
        )


def test_update_expense(database):
    """Verify expense modification."""
    repository = ExpenseRepository(database)

    expense_id = repository.add_expense(
        purchase_date="2026-10-21",
        vendor="Smiths",
        cost=-8532,
        type="FOOD",
        sub_type="GROCERIES",
    )

    assert repository.update_expense(
        expense_id,
        cost=-9000,
    )

    assert repository.get_expense(expense_id)["cost"] == -9000


def test_delete_expense(database):
    """Verify expense deletion."""
    repository = ExpenseRepository(database)

    expense_id = repository.add_expense(
        purchase_date="2026-10-21",
        vendor="Smiths",
        cost=-8532,
        type="FOOD",
        sub_type="GROCERIES",
    )

    assert repository.delete_expense(expense_id)
    assert repository.get_expense(expense_id) is None


def test_open_existing_database(tmp_path):
    """Verify an existing valid database can be reopened."""
    path = tmp_path / "expenses.db"

    connection = create_database(path)
    connection.close()

    reopened = open_database(path)
    reopened.close()


def test_reject_invalid_database(tmp_path):
    """Verify databases with incorrect schemas are rejected."""
    path = tmp_path / "invalid.db"

    connection = sqlite3.connect(path)
    connection.execute(
        "CREATE TABLE unrelated (id INTEGER)"
    )
    connection.close()

    with pytest.raises(ValueError):
        open_database(path)

# ==========================================================================================
# ==========================================================================================
# eof
