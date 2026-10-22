import sqlite3
from collections.abc import Mapping
from typing import Any

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
    """Provide database operations for expense records."""

    FIELDS = (
        "purchase_date",
        "vendor",
        "cost",
        "type",
        "sub_type",
        "validated",
        "description",
    )

    def __init__(self, connection: sqlite3.Connection):
        self.connection = connection

    @staticmethod
    def _validate_expense(data: Mapping[str, Any]) -> None:
        """Validate expense category and basic data types."""
        expense_type = data.get("type")
        sub_type = data.get("sub_type", "NA")

        if expense_type not in CATEGORIES:
            raise ValueError(
                f"Invalid expense type: {expense_type}"
            )

        if sub_type not in CATEGORIES[expense_type]:
            raise ValueError(
                f"Invalid subtype '{sub_type}' "
                f"for type '{expense_type}'"
            )

        cost = data.get("cost")
        if type(cost) is not int:
            raise ValueError(
                "Cost must be an integer number of cents"
            )

        validated = data.get("validated", 0)
        if type(validated) not in (int, bool):
            raise ValueError("Validated must be 0 or 1")

        if validated not in (0, 1):
            raise ValueError("Validated must be 0 or 1")

    def add_expense(self, **kwargs: Any) -> int:
        """Insert an expense and return its assigned ID."""
        data = {
            "purchase_date": kwargs["purchase_date"],
            "vendor": kwargs["vendor"],
            "cost": kwargs["cost"],
            "type": kwargs["type"],
            "sub_type": kwargs.get("sub_type", "NA"),
            "validated": kwargs.get("validated", 0),
            "description": kwargs.get("description"),
        }

        self._validate_expense(data)

        columns = ", ".join(self.FIELDS)
        placeholders = ", ".join("?" for _ in self.FIELDS)

        values = tuple(data[field] for field in self.FIELDS)

        cursor = self.connection.execute(
            f"INSERT INTO expense ({columns}) "
            f"VALUES ({placeholders})",
            values,
        )

        return cursor.lastrowid

    def get_expense(self, expense_id: int):
        """Retrieve an expense by ID, or None if absent."""
        return self.connection.execute(
            "SELECT * FROM expense WHERE id = ?",
            (expense_id,),
        ).fetchone()

    def get_all_expenses(self):
        """Retrieve expenses ordered by purchase date."""
        return self.connection.execute(
            """
            SELECT *
            FROM expense
            ORDER BY purchase_date DESC, id DESC
            """
        ).fetchall()

    def update_expense(
        self,
        expense_id: int,
        **kwargs: Any,
    ) -> bool:
        """Update an expense using its complete record values."""
        existing = self.get_expense(expense_id)

        if existing is None:
            return False

        unknown = set(kwargs) - set(self.FIELDS)
        if unknown:
            raise ValueError(
                f"Unknown expense fields: {sorted(unknown)}"
            )

        data = {
            field: existing[field]
            for field in self.FIELDS
        }
        data.update(kwargs)

        self._validate_expense(data)

        assignments = ", ".join(
            f"{field} = ?" for field in self.FIELDS
        )
        values = [data[field] for field in self.FIELDS]
        values.append(expense_id)

        cursor = self.connection.execute(
            f"UPDATE expense SET {assignments} "
            "WHERE id = ?",
            values,
        )

        return cursor.rowcount > 0

    def delete_expense(self, expense_id: int) -> bool:
        """Delete an expense by ID."""
        cursor = self.connection.execute(
            "DELETE FROM expense WHERE id = ?",
            (expense_id,),
        )
        return cursor.rowcount > 0


# ==========================================================================================
# ==========================================================================================
# eof
