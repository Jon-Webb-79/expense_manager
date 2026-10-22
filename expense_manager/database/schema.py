
# ==========================================================================================
# ==========================================================================================

# File:    schema.py
# Date:    October 21, 2026
# Author:  Jonathan A. Webb
# Purpose: Defines the database tables, columns, constraints, and indexes
# ==========================================================================================
# ==========================================================================================
# Insert Code here

"""SQLite schema definitions for the Expense Manager."""

SCHEMA_VERSION = 1

CREATE_EXPENSE_TABLE = """
CREATE TABLE expense (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    entry_date TEXT NOT NULL
        DEFAULT (date('now'))
        CHECK (entry_date = date(entry_date, '+0 days')),

    purchase_date TEXT NOT NULL
        CHECK (purchase_date = date(purchase_date, '+0 days')),

    vendor TEXT NOT NULL,

    cost INTEGER NOT NULL
        CHECK (typeof(cost) = 'integer'),

    type TEXT NOT NULL
        CHECK (type IN (
            'FOOD', 'GAS', 'TRAVEL', 'AUTO',
            'BILLS', 'TAXES', '401K', 'PAYCHECK',
            'MEDICAL', 'MISC', 'ALCOHOL'
        )),

    sub_type TEXT NOT NULL DEFAULT 'NA',

    validated INTEGER NOT NULL DEFAULT 0
        CHECK (
            typeof(validated) = 'integer'
            AND validated IN (0, 1)
        ),

    description TEXT,

    CONSTRAINT valid_type_subtype
    CHECK (
        (type = 'FOOD'
            AND sub_type IN ('GROCERIES', 'RESTAURANT'))

        OR (type = 'BILLS'
            AND sub_type IN (
                'PHONE', 'ELECTRICITY', 'GAS',
                'INSURANCE', 'HOUSING', 'MISC'
            ))

        OR (type = 'TAXES'
            AND sub_type IN (
                'INCOME_TAX', 'STATE_TAX',
                'MEDICAID', 'MEDICARE',
                'SOCIAL_SECURITY'
            ))

        OR (type = 'MEDICAL'
            AND sub_type IN (
                'DOCTOR', 'HOSPITAL', 'DRUGS'
            ))

        OR (type IN (
                'GAS', 'TRAVEL', 'AUTO', '401K',
                'PAYCHECK', 'MISC', 'ALCOHOL'
            )
            AND sub_type = 'NA')
    )
)
"""

CREATE_INDEXES = (
    """
    CREATE INDEX idx_expense_purchase_date
    ON expense(purchase_date)
    """,
    """
    CREATE INDEX idx_expense_type
    ON expense(type, sub_type)
    """,
    """
    CREATE INDEX idx_expense_vendor
    ON expense(vendor)
    """,
)

CATEGORIES = {
    "FOOD": ("GROCERIES", "RESTAURANT"),
    "GAS": ("NA",),
    "TRAVEL": ("NA",),
    "AUTO": ("NA",),
    "BILLS": (
        "PHONE", "ELECTRICITY", "GAS",
        "INSURANCE", "HOUSING", "MISC",
    ),
    "TAXES": (
        "INCOME_TAX", "STATE_TAX",
        "MEDICAID", "MEDICARE",
        "SOCIAL_SECURITY",
    ),
    "401K": ("NA",),
    "PAYCHECK": ("NA",),
    "MEDICAL": ("DOCTOR", "HOSPITAL", "DRUGS"),
    "MISC": ("NA",),
    "ALCOHOL": ("NA",),
)


def create_schema(connection):
    """Create the expense schema on a new database connection.

    Args:
        connection: An open sqlite3.Connection.

    Raises:
        sqlite3.Error: If schema creation fails.
    """
    import sqlite3

    if not isinstance(connection, sqlite3.Connection):
        raise TypeError("Expected a sqlite3.Connection")

    if connection.in_transaction:
        raise RuntimeError(
            "Schema creation requires no active transaction"
        )

    try:
        connection.execute("BEGIN IMMEDIATE")
        connection.execute(CREATE_EXPENSE_TABLE)

        for statement in CREATE_INDEXES:
            connection.execute(statement)

        connection.execute(
            f"PRAGMA user_version = {SCHEMA_VERSION}"
        )
        connection.commit()

    except sqlite3.Error:
        connection.rollback()
        raise


# ==========================================================================================
# ==========================================================================================
# eof
