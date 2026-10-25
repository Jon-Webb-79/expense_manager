from datetime import date
from decimal import Decimal, InvalidOperation

from PyQt6.QtCore import QDate
from PyQt6.QtWidgets import (
    QDateEdit,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QVBoxLayout,
)
# ==========================================================================================
# ==========================================================================================

# File:    account_settings_dialog.py
# Date:    October 24, 2026
# Author:  Jonathan A. Webb
# Purpose: Describe the purpose of functions of this file
# ==========================================================================================
# ==========================================================================================

class AccountSettingsDialog(QDialog):
    """Edit the account name, start date, and opening balance."""

    def __init__(self, parent=None, account=None):
        super().__init__(parent)

        self.setWindowTitle("Account Settings")
        self.setMinimumWidth(380)

        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Account name")

        self.start_date_edit = QDateEdit()
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setDisplayFormat("yyyy-MM-dd")
        self.start_date_edit.setDate(QDate.currentDate())

        self.opening_balance_edit = QLineEdit()
        self.opening_balance_edit.setPlaceholderText("0.00")

        form = QFormLayout()
        form.addRow("Account Name:", self.name_edit)
        form.addRow("Start Date:", self.start_date_edit)
        form.addRow("Opening Balance ($):", self.opening_balance_edit)

        explanation = QLabel(
            "The opening balance is the account balance at the "
            "end of the day preceding the start date."
        )
        explanation.setWordWrap(True)

        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
        )

        self.buttons.accepted.connect(self._validate_and_accept)
        self.buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(explanation)
        layout.addWidget(self.buttons)

        if account is not None:
            self.name_edit.setText(account["name"])

            start = date.fromisoformat(account["start_date"])
            self.start_date_edit.setDate(
                QDate(start.year, start.month, start.day)
            )

            self.opening_balance_edit.setText(
                f"{Decimal(account['opening_balance']) / 100:.2f}"
            )
        else:
            self.name_edit.setText("Account")
            self.opening_balance_edit.setText("0.00")

    def _validate_and_accept(self) -> None:
        """Validate inputs before accepting the dialog."""
        if not self.name_edit.text().strip():
            QMessageBox.warning(
                self,
                "Invalid Account Name",
                "The account name cannot be empty.",
            )
            return

        try:
            self._parse_balance()
        except ValueError as exc:
            QMessageBox.warning(
                self,
                "Invalid Opening Balance",
                str(exc),
            )
            return

        self.accept()

    def _parse_balance(self) -> int:
        """Convert a dollar amount to integer cents."""
        value = self.opening_balance_edit.text().strip()

        try:
            amount = Decimal(value)
        except InvalidOperation as exc:
            raise ValueError(
                "Enter a valid opening balance, such as 1500.00."
            ) from exc

        if not amount.is_finite():
            raise ValueError("Opening balance must be finite.")

        cents = amount * 100

        if cents != cents.to_integral_value():
            raise ValueError(
                "Opening balance cannot have more than two "
                "decimal places."
            )

        return int(cents)

    def get_account_settings(self) -> tuple[str, str, int]:
        """Return the validated account settings.

        Returns:
            Account name, ISO start date, opening balance in cents.
        """
        return (
            self.name_edit.text().strip(),
            self.start_date_edit.date().toString("yyyy-MM-dd"),
            self._parse_balance(),
        )


# ==========================================================================================
# ==========================================================================================
# eof
