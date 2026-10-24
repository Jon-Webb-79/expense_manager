from collections.abc import Iterable
from datetime import date

from PyQt6.QtCore import QDate
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDateEdit,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QLineEdit,
    QMessageBox,
    QTextEdit,
    QVBoxLayout,
)

from expense_manager.database.schema import CATEGORIES
from expense_manager.models.expense import Expense
from expense_manager.views.vendor_autocomplete import (
    configure_vendor_autocomplete,
)
# ==========================================================================================
# ==========================================================================================

# File:    expense_dialog.py.py
# Date:    October 23, 2026
# Author:  Jonathan A. Webb
# Purpose: Dialog for entering a new expense
# ==========================================================================================
# ==========================================================================================


class ExpenseDialog(QDialog):
    """Collect information for a new expense transaction."""

    def __init__(
        self,
        parent=None,
        vendors: Iterable[str] = (),
    ):
        super().__init__(parent)

        self.setWindowTitle("Add Expense")
        self.setMinimumWidth(420)

        self.purchase_date = QDateEdit()
        self.purchase_date.setCalendarPopup(True)
        self.purchase_date.setDate(QDate.currentDate())
        self.purchase_date.setDisplayFormat("yyyy-MM-dd")

        self.vendor = QLineEdit()
        configure_vendor_autocomplete(self.vendor, vendors)

        self.cost = QDoubleSpinBox()
        self.cost.setDecimals(2)
        self.cost.setRange(-999999999.99, 999999999.99)
        self.cost.setPrefix("$")

        self.expense_type = QComboBox()
        self.expense_type.addItems(CATEGORIES.keys())

        self.sub_type = QComboBox()

        self.validated = QCheckBox()

        self.description = QTextEdit()
        self.description.setMaximumHeight(100)

        form = QFormLayout()
        form.addRow("Purchase Date:", self.purchase_date)
        form.addRow("Vendor:", self.vendor)
        form.addRow("Cost:", self.cost)
        form.addRow("Type:", self.expense_type)
        form.addRow("Sub Type:", self.sub_type)
        form.addRow("Validated:", self.validated)
        form.addRow("Description:", self.description)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(buttons)

        self.expense_type.currentTextChanged.connect(
            self.update_subtypes
        )
        self.update_subtypes(self.expense_type.currentText())

    def update_subtypes(self, expense_type: str) -> None:
        """Populate valid subtypes for the selected type."""
        self.sub_type.clear()
        self.sub_type.addItems(CATEGORIES[expense_type])

    def accept(self) -> None:
        """Reject incomplete entries before closing the dialog."""
        if not self.vendor.text().strip():
            QMessageBox.warning(
                self,
                "Invalid Expense",
                "A vendor is required.",
            )
            return

        super().accept()

    def get_expense(self) -> Expense:
        """Construct an unsaved Expense from the form values."""
        return Expense(
            id=None,
            entry_date=date.today().isoformat(),
            purchase_date=self.purchase_date.date().toString(
                "yyyy-MM-dd"
            ),
            vendor=self.vendor.text().strip(),
            cost=round(self.cost.value() * 100),
            type=self.expense_type.currentText(),
            sub_type=self.sub_type.currentText(),
            validated=self.validated.isChecked(),
            description=self.description.toPlainText().strip() or "NA",
        )


# ==========================================================================================
# ==========================================================================================
# eof
