import re
import sqlite3

from .schema import (
    CREATE_ACCOUNT_TABLE,
    CREATE_DAILY_BALANCE_TABLE,
    CREATE_EXPENSE_TABLE,
    CREATE_INDEXES,
    SCHEMA_VERSION,
)


# ==========================================================================================
# ==========================================================================================

# File:    validation.py
# Date:    October 21, 2026
# Author:  Jonathan A. Webb
# Purpose: Verifies that a selected database has the required schema
# ==========================================================================================
# ==========================================================================================


def _normalize_sql(sql: str) -> str:
    """Normalize SQL formatting for schema comparison."""
    sql = re.sub(r"\s+", " ", sql.strip())
    sql = re.sub(r"\s*([(),=])\s*", r"\1", sql)
    return sql.rstrip(";").casefold()


def validate_schema(connection: sqlite3.Connection) -> None:
    """Verify that a database matches the approved schema.

    Args:
        connection: Open SQLite connection.

    Raises:
        ValueError: If the schema is incompatible.
        sqlite3.Error: If SQLite cannot inspect the file.
    """
    version = connection.execute(
        "PRAGMA user_version"
    ).fetchone()[0]

    if version != SCHEMA_VERSION:
        raise ValueError(
            f"Unsupported schema version: {version}. "
            f"Expected version {SCHEMA_VERSION}."
        )

    # Validate all required tables.
    required_tables = {
        "expense": CREATE_EXPENSE_TABLE,
        "account": CREATE_ACCOUNT_TABLE,
        "daily_balance": CREATE_DAILY_BALANCE_TABLE,
    }

    for table_name, expected_sql in required_tables.items():
        row = connection.execute(
            """
            SELECT sql
            FROM sqlite_master
            WHERE type = 'table' AND name = ?
            """,
            (table_name,),
        ).fetchone()

        if row is None:
            raise ValueError(
                f"Invalid database: missing '{table_name}' table."
            )

        if _normalize_sql(row[0]) != _normalize_sql(expected_sql):
            raise ValueError(
                f"Invalid database: '{table_name}' table "
                "definition does not match the required schema."
            )

    # Validate required indexes.
    for statement in CREATE_INDEXES:
        match = re.search(
            r"CREATE INDEX\s+(\w+)",
            statement,
            re.IGNORECASE,
        )

        if match is None:
            raise RuntimeError("Invalid index definition")

        index_name = match.group(1)

        index_row = connection.execute(
            """
            SELECT sql
            FROM sqlite_master
            WHERE type = 'index' AND name = ?
            """,
            (index_name,),
        ).fetchone()

        if (
            index_row is None
            or _normalize_sql(index_row[0])
            != _normalize_sql(statement)
        ):
            raise ValueError(
                f"Missing or invalid index: {index_name}"
            )

    # Verify database integrity.
    integrity = connection.execute(
        "PRAGMA integrity_check"
    ).fetchone()[0]

    if integrity != "ok":
        raise ValueError(
            f"Database integrity check failed: {integrity}"
        )

    # Verify foreign-key relationships.
    foreign_key_errors = connection.execute(
        "PRAGMA foreign_key_check"
    ).fetchall()

    if foreign_key_errors:
        raise ValueError(
            "Database foreign-key validation failed: "
            f"{foreign_key_errors}"
        )



# ==========================================================================================
# ==========================================================================================
# eof
