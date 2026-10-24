import sqlite3

import pytest

from expense_manager.database.repository import ExpenseRepository
from expense_manager.database.schema import create_schema
from expense_manager.models.vendor_summary import VendorSummary
# ==========================================================================================
# ==========================================================================================
# File:    test_vendor_summary.py
# Date:    October 24, 2026
# Author:  Jonathan A. Webb
# Purpose: Describe the types of testing to occur in this file.
# ==========================================================================================
# ==========================================================================================
# Insert Code here

@pytest.fixture
def repository():
    """Create an isolated, in-memory expense database."""
    connection = sqlite3.connect(":memory:")
    create_schema(connection)

    repo = ExpenseRepository(connection)

    yield repo

    connection.close()


def insert_expense(
    repository: ExpenseRepository,
    purchase_date: str,
    vendor: str,
    cost: int,
    expense_type: str = "FOOD",
    sub_type: str = "GROCERIES",
) -> None:
    """Insert a test transaction."""
    repository.connection.execute(
        """
        INSERT INTO expense (
            purchase_date,
            vendor,
            cost,
            type,
            sub_type,
            validated
        )
        VALUES (?, ?, ?, ?, ?, 0)
        """,
        (
            purchase_date,
            vendor,
            cost,
            expense_type,
            sub_type,
        ),
    )
    repository.connection.commit()


# def test_vendor_totals_across_categories(repository):
#     """One vendor should aggregate transactions from all categories."""
#     insert_expense(
#         repository, "2026-10-05", "Walmart", -12500
#     )
#     insert_expense(
#         repository, "2026-10-06", "Walmart", -7500,
#         "AUTO", "NA",
#     )
#     insert_expense(
#         repository, "2026-10-07", "Chevron", -4000,
#         "GAS", "NA",
#     )
#
#     results = repository.get_vendor_summary(
#         "2026-10-01",
#         "2026-10-31",
#     )
#
#     assert results == [
#         VendorSummary("Walmart", -20000, 2),
#         VendorSummary("Chevron", -4000, 1),
#     ]


def test_vendor_includes_date_boundaries(repository):
    """Transactions on both boundary dates should be included."""
    insert_expense(
        repository, "2026-10-01", "Costco", -10000
    )
    insert_expense(
        repository, "2026-10-31", "Costco", -5000
    )

    results = repository.get_vendor_summary(
        "2026-10-01",
        "2026-10-31",
    )

    assert results == [
        VendorSummary("Costco", -15000, 2),
    ]


def test_vendor_excludes_outside_dates(repository):
    """Transactions outside the reporting period should be excluded."""
    insert_expense(
        repository, "2026-09-30", "Amazon", -1000
    )
    insert_expense(
        repository, "2026-10-15", "Amazon", -2000
    )
    insert_expense(
        repository, "2026-11-01", "Amazon", -3000
    )

    results = repository.get_vendor_summary(
        "2026-10-01",
        "2026-10-31",
    )

    assert results == [
        VendorSummary("Amazon", -2000, 1),
    ]


def test_vendor_refunds_offset_expenses(repository):
    """Positive refunds should offset negative purchases."""
    insert_expense(
        repository, "2026-10-05", "Amazon", -10000
    )
    insert_expense(
        repository, "2026-10-10", "Amazon", 2500
    )

    results = repository.get_vendor_summary(
        "2026-10-01",
        "2026-10-31",
    )

    assert results == [
        VendorSummary("Amazon", -7500, 2),
    ]


def test_vendor_income_is_preserved(repository):
    """Positive income transactions should retain their sign."""
    insert_expense(
        repository, "2026-10-15", "Employer", 250000,
        "PAYCHECK", "NA",
    )

    results = repository.get_vendor_summary(
        "2026-10-01",
        "2026-10-31",
    )

    assert results == [
        VendorSummary("Employer", 250000, 1),
    ]


def test_vendor_empty_period(repository):
    """No matching transactions should return an empty list."""
    results = repository.get_vendor_summary(
        "2026-10-01",
        "2026-10-31",
    )

    assert results == []


def test_vendor_sorting(repository):
    """Vendors should be ordered by signed total, then name."""
    insert_expense(
        repository, "2026-10-05", "Zulu", -5000
    )
    insert_expense(
        repository, "2026-10-05", "Alpha", -5000
    )
    insert_expense(
        repository, "2026-10-05", "Bravo", -10000
    )

    results = repository.get_vendor_summary(
        "2026-10-01",
        "2026-10-31",
    )

    assert [result.vendor for result in results] == [
        "Bravo",
        "Alpha",
        "Zulu",
    ]


@pytest.mark.parametrize(
    "start_date, end_date",
    [
        ("2026-10-31", "2026-10-01"),
        ("2026-13-01", "2026-10-31"),
        ("2026-10-01", "invalid"),
        ("10/01/2026", "2026-10-31"),
        ("2026-10-1", "2026-10-31"),
    ],
)
def test_vendor_rejects_invalid_dates(
    repository,
    start_date,
    end_date,
):
    """Invalid reporting dates should raise ValueError."""
    with pytest.raises(ValueError):
        repository.get_vendor_summary(
            start_date,
            end_date,
        )

# ==========================================================================================
# eof
