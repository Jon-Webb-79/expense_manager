import re
import sqlite3

from .schema import (
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
    version = connection.execute("PRAGMA user_version").fetchone()[0]

    if version != SCHEMA_VERSION:
        raise ValueError(
            f"Unsupported schema version: {version}. "
            f"Expected version {SCHEMA_VERSION}."
        )

    row = connection.execute("""
        SELECT sql
        FROM sqlite_master
        WHERE type = 'table' AND name = 'expense'
        """).fetchone()

    if row is None:
        raise ValueError("Invalid database: missing 'expense' table.")

    if _normalize_sql(row[0]) != _normalize_sql(CREATE_EXPENSE_TABLE):
        raise ValueError(
            "Invalid database: expense table definition "
            "does not match the required schema."
        )

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

        if index_row is None or _normalize_sql(index_row[0]) != _normalize_sql(statement):
            raise ValueError(f"Missing or invalid index: {index_name}")

    integrity = connection.execute("PRAGMA integrity_check").fetchone()[0]

    if integrity != "ok":
        raise ValueError(f"Database integrity check failed: {integrity}")


# ==========================================================================================
# ==========================================================================================
# eof
