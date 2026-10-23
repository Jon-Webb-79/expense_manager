import sqlite3
from dataclasses import replace

import pytest

# ==========================================================================================
# File:    test.py
# Date:    October 21, 2026
# Author:  Jonathan A. Webb
# Purpose: Unit tests for database management and expense repository operations.
# ==========================================================================================

from expense_manager.database.connection import (
    create_database,
    open_database,
)
from expense_manager.database.repository import ExpenseRepository
from expense_manager.database.schema import CATEGORIES
from expense_manager.database.validation import validate_schema
from expense_manager.models.expense import Expense

# ==========================================================================================
# Fixtures
# ==========================================================================================


@pytest.fixture
def database(tmp_path):
    """Create a temporary SQLite database for each test."""
    connection = create_database(tmp_path / "test_expenses.db")

    yield connection

    connection.close()


@pytest.fixture
def repository(database):
    """Create an expense repository using the test database."""
    return ExpenseRepository(database)


@pytest.fixture
def sample_expense():
    """Create a valid expense object for testing."""
    return Expense(
        id=None,
        entry_date="2026-10-21",
        purchase_date="2026-10-21",
        vendor="Smiths",
        cost=-8532,
        type="FOOD",
        sub_type="GROCERIES",
        validated=False,
        description="Weekly grocery shopping",
    )


# ==========================================================================================
# Database Creation and Connection Tests
# ==========================================================================================


def test_database_creation(database):
    """Verify the expense table exists."""
    result = database.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
          AND name = 'expense'
        """).fetchone()

    assert result is not None
    assert result["name"] == "expense"


def test_database_schema_validation(database):
    """Verify a newly created database passes schema validation."""
    validate_schema(database)


def test_open_existing_database(tmp_path):
    """Verify an existing valid database can be reopened."""
    path = tmp_path / "expenses.db"

    connection = create_database(path)
    connection.close()

    reopened = open_database(path)

    assert reopened is not None
    reopened.close()


def test_reject_invalid_database(tmp_path):
    """Verify a database with an invalid schema is rejected."""
    path = tmp_path / "invalid.db"

    connection = sqlite3.connect(path)
    connection.execute("CREATE TABLE unrelated (id INTEGER)")
    connection.close()

    with pytest.raises(ValueError):
        open_database(path)


def test_open_nonexistent_database(tmp_path):
    """Verify opening a nonexistent database raises an error."""
    path = tmp_path / "missing.db"

    with pytest.raises(FileNotFoundError):
        open_database(path)

    assert not path.exists()


def test_prevent_database_overwrite(tmp_path):
    """Verify database creation does not overwrite existing files."""
    path = tmp_path / "expenses.db"

    connection = create_database(path)
    connection.close()

    with pytest.raises(FileExistsError):
        create_database(path)


# ==========================================================================================
# Expense Insertion and Retrieval Tests
# ==========================================================================================


def test_add_expense(repository, sample_expense):
    """Verify an expense can be inserted and retrieved."""
    expense_id = repository.add_expense(sample_expense)

    saved = repository.get_expense(expense_id)

    assert saved is not None
    assert isinstance(saved, Expense)

    assert saved.id == expense_id
    assert saved.vendor == "Smiths"
    assert saved.cost == -8532
    assert saved.type == "FOOD"
    assert saved.sub_type == "GROCERIES"
    assert saved.validated is False
    assert saved.description == "Weekly grocery shopping"


def test_expense_default_values(repository, sample_expense):
    """Verify default values are correctly stored."""
    expense_id = repository.add_expense(sample_expense)

    saved = repository.get_expense(expense_id)

    assert saved is not None
    assert saved.id is not None
    assert saved.entry_date is not None
    assert saved.validated is False


def test_get_nonexistent_expense(repository):
    """Verify retrieving an unknown expense returns None."""
    result = repository.get_expense(999999)

    assert result is None


def test_get_all_expenses(repository, sample_expense):
    """Verify multiple expenses can be retrieved."""
    first_id = repository.add_expense(sample_expense)

    second = replace(
        sample_expense,
        vendor="Shell",
        cost=-4500,
        type="GAS",
        sub_type="NA",
    )

    second_id = repository.add_expense(second)

    expenses = repository.get_all_expenses()

    assert len(expenses) == 2
    assert all(isinstance(expense, Expense) for expense in expenses)

    assert {expense.id for expense in expenses} == {
        first_id,
        second_id,
    }


# ==========================================================================================
# Expense Validation Tests
# ==========================================================================================


def test_invalid_type(repository, sample_expense):
    """Verify invalid expense types are rejected."""
    expense = replace(
        sample_expense,
        type="INVALID",
        sub_type="NA",
    )

    with pytest.raises(ValueError):
        repository.add_expense(expense)


def test_invalid_subtype(repository, sample_expense):
    """Verify invalid type/subtype combinations are rejected."""
    expense = replace(
        sample_expense,
        type="FOOD",
        sub_type="HOUSING",
    )

    with pytest.raises(ValueError):
        repository.add_expense(expense)


@pytest.mark.parametrize(
    "expense_type, sub_type",
    [
        (expense_type, sub_type)
        for expense_type, sub_types in CATEGORIES.items()
        for sub_type in sub_types
    ],
)
def test_valid_categories(
    repository,
    sample_expense,
    expense_type,
    sub_type,
):
    """Verify every approved type/subtype combination is accepted."""
    expense = replace(
        sample_expense,
        type=expense_type,
        sub_type=sub_type,
    )

    expense_id = repository.add_expense(expense)

    saved = repository.get_expense(expense_id)

    assert saved is not None
    assert saved.type == expense_type
    assert saved.sub_type == sub_type


def test_invalid_cost_type(repository, sample_expense):
    """Verify costs must be integer cents."""
    expense = replace(
        sample_expense,
        cost=85.32,
    )

    with pytest.raises(ValueError):
        repository.add_expense(expense)


def test_invalid_validated_type(repository, sample_expense):
    """Verify validated must be a Boolean."""
    expense = replace(
        sample_expense,
        validated="TRUE",
    )

    with pytest.raises(ValueError):
        repository.add_expense(expense)


def test_database_constraint(database):
    """Verify SQLite independently rejects invalid categories."""
    with pytest.raises(sqlite3.IntegrityError):
        database.execute(
            """
            INSERT INTO expense (
                purchase_date,
                vendor,
                cost,
                type,
                sub_type
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


def test_database_validated_constraint(database):
    """Verify SQLite rejects invalid validated values."""
    with pytest.raises(sqlite3.IntegrityError):
        database.execute(
            """
            INSERT INTO expense (
                purchase_date,
                vendor,
                cost,
                type,
                sub_type,
                validated
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                "2026-10-21",
                "Smiths",
                -8532,
                "FOOD",
                "GROCERIES",
                2,
            ),
        )


# ==========================================================================================
# Expense Modification Tests
# ==========================================================================================


def test_update_expense(repository, sample_expense):
    """Verify an existing expense can be modified."""
    expense_id = repository.add_expense(sample_expense)

    saved = repository.get_expense(expense_id)
    assert saved is not None

    updated = replace(
        saved,
        cost=-9000,
        vendor="Smiths Marketplace",
        validated=True,
    )

    assert repository.update_expense(updated)

    result = repository.get_expense(expense_id)

    assert result is not None
    assert result.cost == -9000
    assert result.vendor == "Smiths Marketplace"
    assert result.validated is True


def test_update_expense_category(repository, sample_expense):
    """Verify type and subtype can be changed together."""
    expense_id = repository.add_expense(sample_expense)

    saved = repository.get_expense(expense_id)
    assert saved is not None

    updated = replace(
        saved,
        type="BILLS",
        sub_type="HOUSING",
    )

    assert repository.update_expense(updated)

    result = repository.get_expense(expense_id)

    assert result is not None
    assert result.type == "BILLS"
    assert result.sub_type == "HOUSING"


def test_update_nonexistent_expense(repository, sample_expense):
    """Verify updating an unknown expense returns False."""
    expense = replace(
        sample_expense,
        id=999999,
    )

    assert repository.update_expense(expense) is False


def test_update_without_id(repository, sample_expense):
    """Verify an expense without an ID cannot be updated."""
    with pytest.raises(ValueError):
        repository.update_expense(sample_expense)


# ==========================================================================================
# Expense Deletion Tests
# ==========================================================================================


def test_delete_expense(repository, sample_expense):
    """Verify an expense can be deleted."""
    expense_id = repository.add_expense(sample_expense)

    assert repository.delete_expense(expense_id)
    assert repository.get_expense(expense_id) is None


def test_delete_nonexistent_expense(repository):
    """Verify deleting an unknown expense returns False."""
    assert repository.delete_expense(999999) is False


# ==========================================================================================
# Transaction Tests
# ==========================================================================================


def test_transaction_commit(database, sample_expense):
    """Verify committed expenses persist after reopening."""
    repository = ExpenseRepository(database)

    with database:
        expense_id = repository.add_expense(sample_expense)

    result = repository.get_expense(expense_id)

    assert result is not None
    assert result.vendor == "Smiths"


def test_transaction_rollback(database, sample_expense):
    """Verify failed transactions can be rolled back."""
    repository = ExpenseRepository(database)

    with pytest.raises(RuntimeError):
        with database:
            repository.add_expense(sample_expense)
            raise RuntimeError("Simulated transaction failure")

    assert repository.get_all_expenses() == []


# ==========================================================================================
# ==========================================================================================
# eof
