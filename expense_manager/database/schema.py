
# ==========================================================================================
# File:    schema.py
# Date:    October 24, 2026
# Author:  Jonathan A. Webb
# Purpose: Defines database tables, constraints, and indexes
# ==========================================================================================

"""SQLite schema definitions for the Expense Manager."""

import sqlite3

SCHEMA_VERSION = 2

CATEGORIES = {
    "FOOD": (
        "GROCERIES",
        "RESTAURANT",
    ),
    "AUTO": (
        "FUEL",
        "MAINTENANCE",
        "REPAIRS",
        "INSURANCE",
        "REGISTRATION",
        "MISC",
    ),
    "TRAVEL": (
        "LODGING",
        "TRANSPORTATION",
        "FOOD",
        "ACTIVITIES",
        "MISC",
    ),
    "BILLS": (
        "PHONE",
        "ELECTRICITY",
        "GAS",
        "INSURANCE",
        "HOUSING",
        "MISC",
    ),
    "BENEFITS": (
        "MEDICAL_INSURANCE",
        "DENTAL_INSURANCE",
        "VISION_INSURANCE",
        "AD_AND_D",
        "CRITICAL_ILLNESS",
        "HOSPITAL_INDEMNITY",
        "HSA",
        "401k",
    ),
    "TAXES": (
        "INCOME_TAX",
        "STATE_TAX",
        "MEDICAID",
        "MEDICARE",
        "SOCIAL_SECURITY",
    ),
    "PAYCHECK": ("NA",),
    "MEDICAL": (
        "DOCTOR",
        "HOSPITAL",
        "DRUGS",
    ),
    "MISC": ("NA",),
    "ALCOHOL": ("NA",),
}


def _sql_string(value: str) -> str:
    """Quote a string literal for generated SQL."""
    return "'" + value.replace("'", "''") + "'"


def _sql_values(values) -> str:
    """Build a comma-separated list of SQL string literals."""
    return ", ".join(_sql_string(value) for value in values)


def _type_subtype_constraint() -> str:
    """Generate the valid Type/Subtype constraint."""
    conditions = []

    for expense_type, subtypes in CATEGORIES.items():
        conditions.append(
            f"(type = {_sql_string(expense_type)} "
            f"AND sub_type IN ({_sql_values(subtypes)}))"
        )

    return "\n        OR ".join(conditions)


CREATE_EXPENSE_TABLE = f"""
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
        CHECK (type IN ({_sql_values(CATEGORIES.keys())})),

    sub_type TEXT NOT NULL DEFAULT 'NA',

    validated INTEGER NOT NULL DEFAULT 0
        CHECK (
            typeof(validated) = 'integer'
            AND validated IN (0, 1)
        ),

    description TEXT NOT NULL DEFAULT 'NA',

    CONSTRAINT valid_type_subtype
    CHECK (
        {_type_subtype_constraint()}
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


def create_schema(connection: sqlite3.Connection) -> None:
    """Create the approved expense schema in a new database."""

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
