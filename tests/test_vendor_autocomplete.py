import pytest

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLineEdit

from expense_manager.views.expense_dialog import ExpenseDialog
from expense_manager.views.vendor_autocomplete import (
    configure_vendor_autocomplete,
    normalize_vendor_names,
)
# ==========================================================================================
# ==========================================================================================
# File:    test_vendor_autocomplete.py
# Date:    October 24, 2026
# Author:  Jonathan A. Webb
# Purpose: Describe the types of testing to occur in this file.
# ==========================================================================================
# ==========================================================================================

def test_normalize_vendor_names():
    names = normalize_vendor_names(
        [
            "Walmart",
            "walmart",
            " Costco ",
            "Chevron",
            "WALMART",
            "",
            "  ",
        ]
    )

    assert names == [
        "Chevron",
        "Costco",
        "Walmart",
    ]


def test_autocomplete_configuration(qtbot):
    editor = QLineEdit()
    qtbot.addWidget(editor)

    completer = configure_vendor_autocomplete(
        editor,
        ["Walmart", "Walgreens", "Costco"],
    )

    assert editor.completer() is completer

    assert completer.caseSensitivity() == (
        Qt.CaseSensitivity.CaseInsensitive
    )

    assert completer.filterMode() == (
        Qt.MatchFlag.MatchContains
    )


def test_autocomplete_suggestions(qtbot):
    editor = QLineEdit()
    qtbot.addWidget(editor)

    completer = configure_vendor_autocomplete(
        editor,
        ["Walmart", "Walgreens", "Costco"],
    )

    completer.setCompletionPrefix("wal")

    matches = [
        completer.completionModel().index(row, 0).data()
        for row in range(
            completer.completionModel().rowCount()
        )
    ]

    assert matches == [
        "Walgreens",
        "Walmart",
    ]


def test_substring_matching(qtbot):
    editor = QLineEdit()
    qtbot.addWidget(editor)

    completer = configure_vendor_autocomplete(
        editor,
        ["Walmart", "Costco", "Chevron"],
    )

    completer.setCompletionPrefix("mart")

    matches = [
        completer.completionModel().index(row, 0).data()
        for row in range(
            completer.completionModel().rowCount()
        )
    ]

    assert matches == ["Walmart"]


def test_expense_dialog_autocomplete(qtbot):
    dialog = ExpenseDialog(
        vendors=["Walmart", "Costco"],
    )
    qtbot.addWidget(dialog)

    completer = dialog.vendor.completer()

    assert completer is not None
    assert completer.model().rowCount() == 2


def test_new_vendor_is_allowed(qtbot):
    dialog = ExpenseDialog(
        vendors=["Walmart", "Costco"],
    )
    qtbot.addWidget(dialog)

    dialog.vendor.setText("New Local Vendor")

    assert dialog.vendor.text() == "New Local Vendor"

# ==========================================================================================
# ==========================================================================================
# eof
