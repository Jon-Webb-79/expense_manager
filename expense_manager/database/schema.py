
# ==========================================================================================
# File:    schema.py
# Date:    October 24, 2026
# Author:  Jonathan A. Webb
# Purpose: Defines database tables, constraints, and indexes
# ==========================================================================================

"""SQLite schema definitions for the Expense Manager."""

import sqlite3

SCHEMA_VERSION = 3


# ==========================================================================================
# Expense Categories
# ==========================================================================================

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


# ==========================================================================================
# SQL Helper Functions
# ==========================================================================================

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


# ==========================================================================================
# Expense Table
# ==========================================================================================

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


# ==========================================================================================
# Account Table
# ==========================================================================================

# Each database represents one financial account.
#
# The account ID is restricted to 1 to enforce this rule.
#
# start_date:
#     First day of expense record keeping.
#
# opening_balance:
#     Account balance at the end of the day preceding
#     start_date, expressed in integer cents.
#
# The account table is initially empty. The user will
# configure the account through the GUI.

CREATE_ACCOUNT_TABLE = """
CREATE TABLE account (
    id INTEGER PRIMARY KEY
        CHECK (id = 1),

    name TEXT NOT NULL DEFAULT 'Account'
        CHECK (length(trim(name)) > 0),

    start_date TEXT NOT NULL
        CHECK (start_date = date(start_date, '+0 days')),

    opening_balance INTEGER NOT NULL
        CHECK (typeof(opening_balance) = 'integer')
)
"""


# ==========================================================================================
# Daily Balance Table
# ==========================================================================================

# Stores the calculated account balance for each day.
#
# account_id:
#     References the single account in the database.
#
# balance_date:
#     Date associated with the calculated balance.
#
# daily_change:
#     Sum of all signed expense.cost values for that day.
#
# closing_balance:
#     Previous day's closing balance plus daily_change.
#
# A record will be generated for every calendar day
# beginning with account.start_date, including days
# with no transactions.
#
# Records are calculated by the application rather than
# entered directly by the user.

CREATE_DAILY_BALANCE_TABLE = """
CREATE TABLE daily_balance (
    account_id INTEGER NOT NULL DEFAULT 1
        CHECK (account_id = 1),

    balance_date TEXT NOT NULL
        CHECK (balance_date = date(balance_date, '+0 days')),

    daily_change INTEGER NOT NULL
        CHECK (typeof(daily_change) = 'integer'),

    closing_balance INTEGER NOT NULL
        CHECK (typeof(closing_balance) = 'integer'),

    PRIMARY KEY (account_id, balance_date),

    FOREIGN KEY (account_id)
        REFERENCES account(id)
        ON DELETE CASCADE
)
"""


# ==========================================================================================
# Database Indexes
# ==========================================================================================

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


# ==========================================================================================
# Schema Creation
# ==========================================================================================

def create_schema(connection: sqlite3.Connection) -> None:
    """Create the approved schema in a new database.

    Creates the expense, account, and daily_balance tables,
    along with the required indexes.

    The account and daily_balance tables are initially empty.
    Account configuration and daily balance calculations are
    performed separately by the application.

    Args:
        connection: An open sqlite3.Connection.

    Raises:
        TypeError: If connection is not a SQLite connection.
        RuntimeError: If a transaction is already active.
        sqlite3.Error: If schema creation fails.
    """
    if not isinstance(connection, sqlite3.Connection):
        raise TypeError("Expected a sqlite3.Connection")

    if connection.in_transaction:
        raise RuntimeError(
            "Schema creation requires no active transaction"
        )

    try:
        connection.execute("BEGIN IMMEDIATE")

        connection.execute(CREATE_EXPENSE_TABLE)
        connection.execute(CREATE_ACCOUNT_TABLE)
        connection.execute(CREATE_DAILY_BALANCE_TABLE)

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
