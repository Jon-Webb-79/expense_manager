import sqlite3
from datetime import date

from expense_manager.models.expense import Expense
from expense_manager.models.expense_summary import ExpenseSummary

from .schema import CATEGORIES
# ==========================================================================================
# ==========================================================================================

# File:    repository.py
# Date:    October 21, 2026
# Author:  Jonathan A. Webb
# Purpose: Provides functions to insert, retrieve, update, and delete expenses
# ==========================================================================================
# ==========================================================================================

class ExpenseRepository:
    """Provide CRUD and reporting operations for expense records."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        """Initialize the repository.

        Args:
            connection: An open SQLite database connection.
        """
        self.connection = connection
        self.connection.row_factory = sqlite3.Row

    @staticmethod
    def _row_to_expense(row: sqlite3.Row) -> Expense:
        """Convert a SQLite row into an Expense object."""
        return Expense(
            id=row["id"],
            entry_date=row["entry_date"],
            purchase_date=row["purchase_date"],
            vendor=row["vendor"],
            cost=row["cost"],
            type=row["type"],
            sub_type=row["sub_type"],
            validated=bool(row["validated"]),
            description=row["description"],
        )

    @staticmethod
    def _validate_expense(expense: Expense) -> None:
        """Validate an expense before database insertion or update."""
        if expense.type not in CATEGORIES:
            raise ValueError(
                f"Invalid expense type: {expense.type}"
            )

        if expense.sub_type not in CATEGORIES[expense.type]:
            raise ValueError(
                f"Invalid subtype '{expense.sub_type}' "
                f"for type '{expense.type}'"
            )

        if type(expense.cost) is not int:
            raise ValueError(
                "Cost must be an integer number of cents"
            )

        if type(expense.validated) is not bool:
            raise ValueError(
                "Validated must be a boolean"
            )

    # ======================================================================================
    # CRUD Operations
    # ======================================================================================

    def add_expense(self, expense: Expense) -> int:
        """Insert an expense and return its database ID.

        Args:
            expense: Expense object to insert.

        Returns:
            Newly assigned expense ID.
        """
        self._validate_expense(expense)

        cursor = self.connection.execute(
            """
            INSERT INTO expense (
                purchase_date,
                vendor,
                cost,
                type,
                sub_type,
                validated,
                description
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                expense.purchase_date,
                expense.vendor,
                expense.cost,
                expense.type,
                expense.sub_type,
                int(expense.validated),
                expense.description,
            ),
        )

        if cursor.lastrowid is None:
            raise sqlite3.DatabaseError(
                "Failed to retrieve inserted expense ID"
            )

        return cursor.lastrowid

    def get_expense(self, expense_id: int) -> Expense | None:
        """Retrieve an expense by its database ID."""
        row = self.connection.execute(
            "SELECT * FROM expense WHERE id = ?",
            (expense_id,),
        ).fetchone()

        if row is None:
            return None

        return self._row_to_expense(row)

    def get_all_expenses(self) -> list[Expense]:
        """Retrieve all expenses ordered by purchase date."""
        rows = self.connection.execute(
            """
            SELECT *
            FROM expense
            ORDER BY purchase_date DESC, id DESC
            """
        ).fetchall()

        return [
            self._row_to_expense(row)
            for row in rows
        ]

    def update_expense(self, expense: Expense) -> bool:
        """Update an existing expense.

        Args:
            expense: Expense containing updated field values.

        Returns:
            True if the expense was updated, otherwise False.
        """
        if expense.id is None:
            raise ValueError(
                "Cannot update an expense without an ID"
            )

        self._validate_expense(expense)

        cursor = self.connection.execute(
            """
            UPDATE expense
            SET
                purchase_date = ?,
                vendor = ?,
                cost = ?,
                type = ?,
                sub_type = ?,
                validated = ?,
                description = ?
            WHERE id = ?
            """,
            (
                expense.purchase_date,
                expense.vendor,
                expense.cost,
                expense.type,
                expense.sub_type,
                int(expense.validated),
                expense.description,
                expense.id,
            ),
        )

        return cursor.rowcount > 0

    def delete_expense(self, expense_id: int) -> bool:
        """Delete an expense using its database ID."""
        cursor = self.connection.execute(
            "DELETE FROM expense WHERE id = ?",
            (expense_id,),
        )

        return cursor.rowcount > 0

    # ======================================================================================
    # Reporting Operations
    # ======================================================================================

    def get_expense_summary(
        self,
        start_date: str,
        end_date: str,
    ) -> list[ExpenseSummary]:
        """Calculate expense totals grouped by type and subtype.

        The reporting period includes both start_date and end_date.
        Dates must use ISO 8601 format (YYYY-MM-DD).

        Costs are summed as signed integer cents.

        Args:
            start_date: First purchase date to include.
            end_date: Last purchase date to include.

        Returns:
            One ExpenseSummary per type/subtype combination
            containing at least one transaction.

        Raises:
            ValueError: If either date is invalid or the date
                range is reversed.
        """
        try:
            start = date.fromisoformat(start_date)
            end = date.fromisoformat(end_date)
        except (TypeError, ValueError) as exc:
            raise ValueError(
                "Dates must use YYYY-MM-DD format"
            ) from exc

        if (
            start.isoformat() != start_date
            or end.isoformat() != end_date
        ):
            raise ValueError(
                "Dates must use YYYY-MM-DD format"
            )

        if start > end:
            raise ValueError(
                "Start date cannot be later than end date"
            )

        rows = self.connection.execute(
            """
            SELECT
                type,
                sub_type,
                SUM(cost) AS total_cents,
                COUNT(*) AS transaction_count
            FROM expense
            WHERE purchase_date BETWEEN ? AND ?
            GROUP BY type, sub_type
            ORDER BY type, sub_type
            """,
            (start_date, end_date),
        ).fetchall()

        return [
            ExpenseSummary(
                type=row["type"],
                sub_type=row["sub_type"],
                total_cents=row["total_cents"],
                transaction_count=row["transaction_count"],
            )
            for row in rows
        ]


# ==========================================================================================
# ==========================================================================================
# eof
