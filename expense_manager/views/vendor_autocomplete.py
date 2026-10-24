from collections.abc import Iterable

from PyQt6.QtCore import Qt, QStringListModel
from PyQt6.QtWidgets import QCompleter, QLineEdit

# ==========================================================================================
# ==========================================================================================

# File:    vendor_autocomplete.py
# Date:    October 24, 2026
# Author:  Jonathan A. Webb
# Purpose: Shared vendor name autocomplete configuration
# ==========================================================================================
# ==========================================================================================


def normalize_vendor_names(
    vendors: Iterable[str],
) -> list[str]:
    """Return unique vendor suggestions, ignoring case and whitespace."""
    unique: dict[str, str] = {}

    for vendor in vendors:
        name = vendor.strip()

        if not name:
            continue

        key = name.casefold()

        if key not in unique:
            unique[key] = name

    return sorted(unique.values(), key=str.casefold)


def configure_vendor_autocomplete(
    editor: QLineEdit,
    vendors: Iterable[str],
) -> QCompleter:
    """Attach case-insensitive, substring-matching autocomplete."""
    names = normalize_vendor_names(vendors)

    model = QStringListModel(names, editor)

    completer = QCompleter(model, editor)
    completer.setCaseSensitivity(
        Qt.CaseSensitivity.CaseInsensitive
    )
    completer.setFilterMode(
        Qt.MatchFlag.MatchContains
    )
    completer.setCompletionMode(
        QCompleter.CompletionMode.PopupCompletion
    )

    editor.setCompleter(completer)

    return completer

# ==========================================================================================
# ==========================================================================================
# eof
