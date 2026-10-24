from dataclasses import dataclass
# ==========================================================================================
# ==========================================================================================

# File:    vendor_summary.py
# Date:    October 24, 2026
# Author:  Jonathan A. Webb
# Purpose: Data model for aggregate vendor expense reporting
# ==========================================================================================
# ==========================================================================================


@dataclass(frozen=True)
class VendorSummary:
    """Represent aggregated transactions for a single vendor."""

    vendor: str
    total_cents: int
    transaction_count: int

# ==========================================================================================
# ==========================================================================================
# eof
