import sqlite3
from datetime import date, timedelta
# ==========================================================================================
# ==========================================================================================

# File:    account_repository.py
# Date:    October 24, 2026
# Author:  Jonathan A. Webb
# Purpose: Describe the purpose of functions of this file
# ==========================================================================================
# ==========================================================================================


class AccountRepository:
    """Manage the single account associated with an expense database."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        """Initialize the account repository.

        Args:
            connection: An open SQLite database connection.
        """
        self.connection = connection
        self.connection.row_factory = sqlite3.Row

    def get_account(self) -> sqlite3.Row | None:
        """Return account settings, or None if not configured."""
        return self.connection.execute(
            """
            SELECT id, name, start_date, opening_balance
            FROM account
            WHERE id = 1
            """
        ).fetchone()

    def configure_account(
        self,
        name: str,
        start_date: str,
        opening_balance: int,
    ) -> None:
        """Create or update the account configuration.

        Args:
            name: Account name.
            start_date: First date of record keeping, YYYY-MM-DD.
            opening_balance: Previous day's closing balance in cents.

        Raises:
            ValueError: If account settings are invalid.
        """
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Account name cannot be empty")

        try:
            parsed_date = date.fromisoformat(start_date)
        except (TypeError, ValueError) as exc:
            raise ValueError(
                "Start date must use YYYY-MM-DD format"
            ) from exc

        if parsed_date.isoformat() != start_date:
            raise ValueError(
                "Start date must use YYYY-MM-DD format"
            )

        if type(opening_balance) is not int:
            raise ValueError(
                "Opening balance must be an integer number of cents"
            )

        # The opening balance must precede all tracked expenses.
        earliest_expense = self.connection.execute(
            "SELECT MIN(purchase_date) FROM expense"
        ).fetchone()[0]

        if (
            earliest_expense is not None
            and start_date > earliest_expense
        ):
            raise ValueError(
                "Account start date cannot be later than "
                "the earliest recorded expense date"
            )

        self.connection.execute(
            """
            INSERT INTO account (
                id, name, start_date, opening_balance
            )
            VALUES (1, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                name = excluded.name,
                start_date = excluded.start_date,
                opening_balance = excluded.opening_balance
            """,
            (name.strip(), start_date, opening_balance),
        )

        self.recalculate_balances()

    def recalculate_balances(
        self,
        through_date: str | None = None,
    ) -> None:
        """Recalculate every daily balance from the account start date.

        The daily balance table is rebuilt using the signed costs
        of expenses grouped by purchase_date.

        Args:
            through_date: Last date to calculate, inclusive.
                Defaults to the current local calendar date.

        Raises:
            ValueError: If the supplied date is invalid.
        """
        account = self.get_account()

        if account is None:
            return

        start = date.fromisoformat(account["start_date"])

        if through_date is None:
            end = date.today()
        else:
            try:
                end = date.fromisoformat(through_date)
            except (TypeError, ValueError) as exc:
                raise ValueError(
                    "Through date must use YYYY-MM-DD format"
                ) from exc

            if end.isoformat() != through_date:
                raise ValueError(
                    "Through date must use YYYY-MM-DD format"
                )

        # Remove previously calculated balances.
        self.connection.execute(
            "DELETE FROM daily_balance WHERE account_id = 1"
        )

        if end < start:
            return

        rows = self.connection.execute(
            """
            SELECT purchase_date, SUM(cost) AS daily_change
            FROM expense
            WHERE purchase_date BETWEEN ? AND ?
            GROUP BY purchase_date
            """,
            (start.isoformat(), end.isoformat()),
        ).fetchall()

        changes = {
            row["purchase_date"]: row["daily_change"]
            for row in rows
        }

        balance = account["opening_balance"]
        current = start
        balance_rows = []

        while current <= end:
            current_date = current.isoformat()
            daily_change = changes.get(current_date, 0)

            balance += daily_change

            balance_rows.append(
                (
                    1,
                    current_date,
                    daily_change,
                    balance,
                )
            )

            current += timedelta(days=1)

        self.connection.executemany(
            """
            INSERT INTO daily_balance (
                account_id,
                balance_date,
                daily_change,
                closing_balance
            )
            VALUES (?, ?, ?, ?)
            """,
            balance_rows,
        )

    def get_daily_balances(
        self,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> list[sqlite3.Row]:
        """Return daily balances ordered by date.

        Optional dates restrict the returned history.
        """
        query = """
            SELECT balance_date, daily_change, closing_balance
            FROM daily_balance
            WHERE account_id = 1
        """

        parameters = []

        if start_date is not None:
            query += " AND balance_date >= ?"
            parameters.append(start_date)

        if end_date is not None:
            query += " AND balance_date <= ?"
            parameters.append(end_date)

        query += " ORDER BY balance_date ASC"

        return self.connection.execute(
            query,
            parameters,
        ).fetchall()

    def get_current_balance(self) -> int | None:
        """Return the latest calculated closing balance in cents."""
        row = self.connection.execute(
            """
            SELECT closing_balance
            FROM daily_balance
            WHERE account_id = 1
            ORDER BY balance_date DESC
            LIMIT 1
            """
        ).fetchone()

        if row is not None:
            return row["closing_balance"]

        account = self.get_account()

        if account is None:
            return None

        return account["opening_balance"]

# ==========================================================================================
# ==========================================================================================
# eof
