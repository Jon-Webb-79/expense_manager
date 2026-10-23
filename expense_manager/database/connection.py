import sqlite3
from pathlib import Path

from .schema import create_schema
from .validation import validate_schema

# ==========================================================================================
# ==========================================================================================

# File:    connection.py
# Date:    October 21, 2026
# Author:  Jonathan A. Webb
# Purpose: Handles database creation, opening, and closing
# ==========================================================================================
# ==========================================================================================


def create_database(path: str | Path) -> sqlite3.Connection:
    """Create a new Expense Manager database.

    Args:
        path: Destination database file.

    Returns:
        An open sqlite3.Connection.

    Raises:
        FileExistsError: If the file already exists.
        sqlite3.Error: If creation fails.
    """
    db_path = Path(path).expanduser().resolve()

    if db_path.exists():
        raise FileExistsError(f"Database already exists: {db_path}")

    if not db_path.parent.is_dir():
        raise FileNotFoundError(f"Directory does not exist: {db_path.parent}")

    connection = sqlite3.connect(db_path)
    try:
        connection.execute("PRAGMA foreign_keys = ON")
        create_schema(connection)
        connection.row_factory = sqlite3.Row
        return connection

    except Exception:
        connection.close()
        # Remove an incomplete newly created database.
        db_path.unlink(missing_ok=True)
        raise


def open_database(path: str | Path) -> sqlite3.Connection:
    """Open and validate an existing expense database.

    Args:
        path: Existing SQLite database file.

    Returns:
        An open sqlite3.Connection.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If schema validation fails.
        sqlite3.Error: If the file cannot be opened.
    """
    db_path = Path(path).expanduser().resolve()

    if not db_path.is_file():
        raise FileNotFoundError(f"Database not found: {db_path}")

    # URI mode=rw prevents accidental file creation.
    connection = sqlite3.connect(
        db_path.as_uri() + "?mode=rw",
        uri=True,
    )

    try:
        validate_schema(connection)
        connection.execute("PRAGMA foreign_keys = ON")
        connection.row_factory = sqlite3.Row
        return connection

    except Exception:
        connection.close()
        raise


def close_database(connection: sqlite3.Connection) -> None:
    """Close a database connection."""
    connection.close()


# ==========================================================================================
# ==========================================================================================
# eof
