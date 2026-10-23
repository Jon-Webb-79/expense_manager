from dataclasses import dataclass
# ==========================================================================================
# ==========================================================================================

# File:    expense.py
# Date:    October 23, 2026
# Author:  Jonathan A. Webb
# Purpose: Data model representing a personal expense transaction
# ==========================================================================================
# ==========================================================================================

@dataclass
class Expense:
    """Represent a single expense transaction.

    Attributes:
        id: Unique database identifier.
        entry_date: Date the record was entered.
        purchase_date: Date the transaction occurred.
        vendor: Merchant or transaction source.
        cost: Transaction amount in integer cents.
        type: Primary expense category.
        sub_type: Secondary expense category.
        validated: Whether the transaction is validated.
        description: Optional transaction description.
    """

    id: int | None
    entry_date: str
    purchase_date: str
    vendor: str
    cost: int
    type: str
    sub_type: str = "NA"
    validated: bool = False
    description: str | None = None

# ==========================================================================================
# ==========================================================================================
# eof
