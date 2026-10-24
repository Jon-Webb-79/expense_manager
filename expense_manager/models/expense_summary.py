from dataclasses import dataclass
# ==========================================================================================
# ==========================================================================================

# File:    expense_summary.py
# Date:    October 23, 2026
# Author:  Jonathan A. Webb
# Purpose: Data model for aggregated reporting
# ==========================================================================================
# ==========================================================================================


@dataclass(frozen=True)
class ExpenseSummary:
    """Represent the total for one expense type/subtype combination."""

    type: str
    sub_type: str
    total_cents: int
    transaction_count: int

# ==========================================================================================
# ==========================================================================================
# eof
