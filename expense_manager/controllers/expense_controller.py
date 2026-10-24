import sqlite3
from pathlib import Path

from PyQt6.QtWidgets import (
    QDialog,
    QFileDialog,
    QMessageBox,
)

from expense_manager.database.connection import (
    create_database,
    open_database,
)
from expense_manager.database.repository import ExpenseRepository
from expense_manager.database.validation import validate_schema
from expense_manager.views.expense_dialog import ExpenseDialog
from expense_manager.views.expense_summary_dialog import ExpenseSummaryDialog
from expense_manager.views.main_window import MainWindow
# ==========================================================================================
# ==========================================================================================

# File:    expense_controller.py
# Date:    October 23, 2026
# Author:  Jonathan A. Webb
# Purpose: Controller coorindating expense data and the graphical interface
# ==========================================================================================
# ==========================================================================================

class ExpenseController:
    """Coordinate database operations, expense editing, and reports."""

    def __init__(self, window: MainWindow):
        self.window = window
        self.connection: sqlite3.Connection | None = None
        self.repository: ExpenseRepository | None = None
        self.database_path: Path | None = None

        self.model = window.table_model
        self.window.table.itemDelegate().vendor_provider = (
            self.get_vendor_names
        )
        self.window.confirm_close = self.confirm_discard

        self._connect_actions()
        self._update_actions()


    def _connect_actions(self) -> None:
        """Connect view actions to controller methods."""
        self.window.new_action.triggered.connect(self.new_database)
        self.window.open_action.triggered.connect(self.select_database)
        self.window.validate_action.triggered.connect(
            self.validate_database
        )
        self.window.save_action.triggered.connect(self.save_changes)
        self.window.discard_action.triggered.connect(
            self.discard_changes
        )
        self.window.add_action.triggered.connect(self.add_expense)
        self.window.delete_action.triggered.connect(
            self.delete_expense
        )

        # Connect the reporting action.
        self.window.expense_summary_action.triggered.connect(
            self.show_expense_summary
        )

    def _update_actions(self) -> None:
        """Enable database-dependent actions appropriately."""
        enabled = self.repository is not None

        for action in (
            self.window.add_action,
            self.window.delete_action,
            self.window.save_action,
            self.window.discard_action,
            self.window.validate_action,
            self.window.expense_summary_action,
        ):
            action.setEnabled(enabled)

    def confirm_discard(self) -> bool:
        """Ask permission before discarding unsaved edits."""
        if not self.model.has_changes():
            return True

        answer = QMessageBox.question(
            self.window,
            "Unsaved Changes",
            "Discard unsaved expense changes?",
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        return answer == QMessageBox.StandardButton.Yes

    def _activate_database(
        self,
        connection: sqlite3.Connection,
        path: Path,
    ) -> None:
        """Install a new connection after successful validation."""
        old_connection = self.connection

        self.connection = connection
        self.repository = ExpenseRepository(connection)
        self.database_path = path

        self.refresh_expenses()
        self._update_actions()

        if old_connection is not None:
            old_connection.close()

        self.window.setWindowTitle(
            f"Expense Manager - {path.name}"
        )

    # ======================================================================================
    # Database Operations
    # ======================================================================================

    def new_database(self) -> None:
        """Create and open a user-named SQLite database."""
        if not self.confirm_discard():
            return

        filename, _ = QFileDialog.getSaveFileName(
            self.window,
            "Create Expense Database",
            "",
            "SQLite Database (*.db);;"
            "Other SQLite (*.sqlite *.sqlite3)",
        )

        if not filename:
            return

        path = Path(filename)

        if not path.suffix:
            path = path.with_suffix(".db")

        try:
            connection = create_database(path)
            self._activate_database(connection, path)

        except (OSError, sqlite3.Error, ValueError) as exc:
            self.window.show_error(
                "Database Creation Failed",
                str(exc),
            )

    def select_database(self) -> None:
        """Select and open an existing SQLite database."""
        if not self.confirm_discard():
            return

        filename, _ = QFileDialog.getOpenFileName(
            self.window,
            "Open Expense Database",
            "",
            "SQLite Database (*.db *.sqlite *.sqlite3);;"
            "All Files (*)",
        )

        if not filename:
            return

        path = Path(filename)

        try:
            connection = open_database(path)
            self._activate_database(connection, path)

        except (OSError, sqlite3.Error, ValueError) as exc:
            self.window.show_error(
                "Invalid Database",
                str(exc),
            )

    def validate_database(self) -> None:
        """Validate the currently loaded database."""
        if self.connection is None:
            return

        try:
            validate_schema(self.connection)

        except (sqlite3.Error, ValueError) as exc:
            self.window.show_error(
                "Schema Validation Failed",
                str(exc),
            )
            return

        QMessageBox.information(
            self.window,
            "Schema Validation",
            "The database schema is valid.",
        )

    def refresh_expenses(self) -> None:
        """Reload expenses from SQLite."""
        if self.repository is None:
            self.model.load_expenses([])
            return

        expenses = self.repository.get_all_expenses()
        self.model.load_expenses(expenses)

        self.window.statusBar().showMessage(
            f"{len(expenses)} expenses loaded"
        )

    # ======================================================================================
    # Expense Editing
    # ======================================================================================

    def add_expense(self) -> None:
        """Add a new expense to the working table."""
        if self.repository is None:
            return

        dialog = ExpenseDialog(
            self.window,
            vendors=self.get_vendor_names(),
        )

        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.model.add_expense(dialog.get_expense())

    def delete_expense(self) -> None:
        """Remove the selected expense from the working table."""
        row = self.window.selected_row()

        if row is None:
            return

        answer = QMessageBox.question(
            self.window,
            "Delete Expense",
            "Delete the selected expense?",
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if answer == QMessageBox.StandardButton.Yes:
            self.model.remove_expense(row)

    def discard_changes(self) -> None:
        """Discard edits and restore saved database records."""
        if self.confirm_discard():
            self.refresh_expenses()

    def save_changes(self) -> None:
        """Commit all pending inserts, updates, and deletions."""
        if self.connection is None or self.repository is None:
            return

        if not self.model.has_changes():
            return

        original = {
            e.id: e
            for e in self.model.original
            if e.id is not None
        }

        current = {
            e.id: e
            for e in self.model.expenses
            if e.id is not None
        }

        try:
            with self.connection:
                # Delete records removed from the table.
                for expense_id in original.keys() - current.keys():
                    self.repository.delete_expense(expense_id)

                # Insert new records and update modified ones.
                for expense in self.model.expenses:
                    if expense.id is None:
                        self.repository.add_expense(expense)

                    elif expense != original.get(expense.id):
                        self.repository.update_expense(expense)

        except (sqlite3.Error, ValueError) as exc:
            self.window.show_error(
                "Save Failed",
                str(exc),
            )
            return

        self.refresh_expenses()
        self.window.statusBar().showMessage(
            "Changes saved successfully"
        )

    # ======================================================================================
    # Expense Reporting
    # ======================================================================================


    def show_expense_summary(self) -> None:
        """Open the tabbed expense reporting dialog."""
        if self.repository is None:
            self.window.show_error(
                "No Database",
                "Open or create a database before generating a report.",
            )
            return

        if self.model.has_changes():
            QMessageBox.information(
                self.window,
                "Unsaved Changes",
                "The reports use saved database records only.\n\n"
                "Any unsaved expense changes will not appear "
                "in the reports.",
            )

        dialog = ExpenseSummaryDialog(self.window)

        dialog.generate_button.clicked.connect(
            lambda checked=False: self.generate_expense_summary(dialog)
        )

        # Generate both reports for the initial date range.
        self.generate_expense_summary(dialog)

        dialog.exec()

    def generate_expense_summary(
        self,
        dialog: ExpenseSummaryDialog,
    ) -> None:
        """Generate category and vendor reports for the same dates."""
        if self.repository is None:
            return

        start_date, end_date = dialog.get_date_range()

        if start_date > end_date:
            QMessageBox.warning(
                dialog,
                "Invalid Date Range",
                "The start date cannot be later than the end date.",
            )
            return

        try:
            expense_summaries = self.repository.get_expense_summary(
                start_date,
                end_date,
            )

            vendor_summaries = self.repository.get_vendor_summary(
                start_date,
                end_date,
            )

            dialog.display_reports(
                expense_summaries,
                vendor_summaries,
            )

        except (sqlite3.Error, ValueError) as exc:
            QMessageBox.critical(
                dialog,
                "Report Generation Failed",
                str(exc),
            )


    def get_vendor_names(self) -> list[str]:
        """Return vendor names from the current working expense table."""
        return [
            expense.vendor
            for expense in self.model.expenses
            if expense.vendor
        ]

    

    # ======================================================================================
    # Application Shutdown
    # ======================================================================================

    def close(self) -> None:
        """Close the active database connection."""
        if self.connection is not None:
            self.connection.close()
            self.connection = None
            self.repository = None

# ==========================================================================================
# ==========================================================================================
# eof
