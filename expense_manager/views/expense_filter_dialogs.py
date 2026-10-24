from datetime import date

from PyQt6.QtCore import QDate
from PyQt6.QtWidgets import (
    QComboBox,
    QCompleter,
    QDateEdit,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QVBoxLayout,
)

from expense_manager.views.vendor_autocomplete import (
    configure_vendor_autocomplete,
)
# ==========================================================================================
# ==========================================================================================

# File:    expense_filter_dialog.py
# Date:    October 24, 2026
# Author:  Jonathan A. Webb
# Purpose: Dialogs for configuring expense table filters
# ==========================================================================================
# ==========================================================================================

class DateRangeFilterDialog(QDialog):
    """Collect an inclusive purchase-date range."""

    def __init__(
        self,
        parent=None,
        start_date: date | None = None,
        end_date: date | None = None,
    ):
        super().__init__(parent)

        self.setWindowTitle("Filter Purchase Date")
        self.setMinimumWidth(320)

        today = date.today()

        self.start_date = QDateEdit(self)
        self.start_date.setCalendarPopup(True)
        self.start_date.setDisplayFormat("yyyy-MM-dd")
        self.start_date.setDate(
            self._to_qdate(start_date or today.replace(month=1, day=1))
        )

        self.end_date = QDateEdit(self)
        self.end_date.setCalendarPopup(True)
        self.end_date.setDisplayFormat("yyyy-MM-dd")
        self.end_date.setDate(self._to_qdate(end_date or today))

        form = QFormLayout()
        form.addRow("Start Date:", self.start_date)
        form.addRow("End Date:", self.end_date)

        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(self.buttons)

    @staticmethod
    def _to_qdate(value: date) -> QDate:
        return QDate(value.year, value.month, value.day)

    def get_date_range(self) -> tuple[date, date]:
        return (
            date.fromisoformat(
                self.start_date.date().toString("yyyy-MM-dd")
            ),
            date.fromisoformat(
                self.end_date.date().toString("yyyy-MM-dd")
            ),
        )

    def accept(self) -> None:
        start, end = self.get_date_range()

        if start > end:
            QMessageBox.warning(
                self,
                "Invalid Date Range",
                "The start date cannot be later than the end date.",
            )
            return

        super().accept()


class SelectionFilterDialog(QDialog):
    """Choose a filter value from a searchable list."""

    def __init__(
        self,
        title: str,
        label: str,
        choices: list[str],
        current_value: str | None = None,
        parent=None,
    ):
        super().__init__(parent)

        self.setWindowTitle(title)
        self.setMinimumWidth(350)

        self.value_edit = QLineEdit(self)
        self.value_edit.setPlaceholderText("Search or select a value")

        configure_vendor_autocomplete(
            self.value_edit,
            choices,
        )

        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(label))
        layout.addWidget(self.value_edit)
        layout.addWidget(self.buttons)

        self._choices = {
            choice.casefold(): choice
            for choice in choices
        }

        if current_value:
            self.value_edit.setText(current_value)

    def selected_value(self) -> str:
        """Return the canonical spelling of the selected choice."""
        entered = self.value_edit.text().strip()
        return self._choices[entered.casefold()]

    def accept(self) -> None:
        entered = self.value_edit.text().strip()

        if entered.casefold() not in self._choices:
            QMessageBox.warning(
                self,
                "Invalid Filter",
                "Please select an existing value.",
            )
            return

        super().accept()

# ==========================================================================================
# ==========================================================================================
# eof
