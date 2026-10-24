from PyQt6.QtWidgets import (
    QAbstractItemView,
    QMainWindow,
    QMessageBox,
    QTableView,
    QToolBar,
)

from expense_manager.models.expense_table_model import ExpenseTableModel
from expense_manager.views.delegates import ExpenseDelegate
# ==========================================================================================
# ==========================================================================================

# File:    main_window.py
# Date:    October 23, 2026
# Author:  Jonathan A. Webb
# Purpose: Graphical window for expense manager
# ==========================================================================================
# ==========================================================================================

class MainWindow(QMainWindow):
    """Display the expense table and application commands."""

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Expense Manager")
        self.resize(1250, 700)

        self.table_model = ExpenseTableModel(self)

        self.table = QTableView()
        self.table.setModel(self.table_model)
        self.table.setItemDelegate(ExpenseDelegate(self.table))

        self.table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.table.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )
        self.table.setAlternatingRowColors(True)
        self.table.setSortingEnabled(False)

        self.table.horizontalHeader().setStretchLastSection(True)

        self.setCentralWidget(self.table)

        self._create_actions()
        self._create_menus()
        self._create_toolbar()

        self.statusBar().showMessage("No database loaded")

        # Assigned by the controller.
        self.confirm_close = lambda: True

    def _create_actions(self):
        """Create application menus and actions."""
        self.file_menu = self.menuBar().addMenu("File")

        self.new_action = self.file_menu.addAction("New Database...")
        self.open_action = self.file_menu.addAction("Open Database...")
        self.validate_action = self.file_menu.addAction(
            "Validate Database Schema"
        )

        self.file_menu.addSeparator()

        self.save_action = self.file_menu.addAction("Save Changes")
        self.discard_action = self.file_menu.addAction(
            "Discard Changes"
        )

        self.file_menu.addSeparator()
        self.exit_action = self.file_menu.addAction("Exit")

        self.edit_menu = self.menuBar().addMenu("Edit")

        self.add_action = self.edit_menu.addAction("Add Expense")
        self.delete_action = self.edit_menu.addAction(
            "Delete Selected Expense"
        )

        # Reporting menu.
        self.reports_menu = self.menuBar().addMenu("Reports")
        self.expense_summary_action = self.reports_menu.addAction(
            "Expense Summary..."
        )

        # Keyboard shortcuts.
        self.save_action.setShortcut("Ctrl+S")
        self.add_action.setShortcut("Ctrl+N")
        self.delete_action.setShortcut("Delete")

        self.exit_action.triggered.connect(self.close)

    def _create_menus(self):
        """Reserve a location for future menu configuration."""
        pass

    def _create_toolbar(self):
        """Create the expense editing toolbar."""
        toolbar = QToolBar("Expense Actions", self)
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        toolbar.addAction(self.add_action)
        toolbar.addAction(self.delete_action)
        toolbar.addSeparator()
        toolbar.addAction(self.save_action)
        toolbar.addAction(self.discard_action)

    def selected_row(self) -> int | None:
        """Return the selected model row."""
        index = self.table.currentIndex()

        return index.row() if index.isValid() else None

    def show_error(self, title: str, message: str) -> None:
        """Display an application error."""
        QMessageBox.critical(self, title, message)

    def closeEvent(self, event):
        """Allow the controller to check for unsaved changes."""
        if self.confirm_close():
            event.accept()
        else:
            event.ignore()

# ==========================================================================================
# ==========================================================================================
# eof
