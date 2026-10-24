from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QDialog,
    QMainWindow,
    QMenu,
    QMessageBox,
    QTableView,
    QToolBar,
)

from expense_manager.database.schema import CATEGORIES
from expense_manager.models.expense_filter_proxy_model import (
    ExpenseFilterProxyModel,
)
from expense_manager.models.expense_table_model import ExpenseTableModel
from expense_manager.views.delegates import ExpenseDelegate
from expense_manager.views.expense_filter_dialogs import (
    DateRangeFilterDialog,
    SelectionFilterDialog,
)
# ==========================================================================================
# ==========================================================================================

# File:    main_window.py
# Date:    October 23, 2026
# Author:  Jonathan A. Webb
# Purpose: Graphical window for expense manager
# ==========================================================================================
# ==========================================================================================

class MainWindow(QMainWindow):
    """Display and filter the expense table."""

    PURCHASE_DATE_COLUMN = 2
    VENDOR_COLUMN = 3
    TYPE_COLUMN = 5
    SUBTYPE_COLUMN = 6

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Expense Manager")
        self.resize(1250, 700)

        self.table_model = ExpenseTableModel(self)

        self.filter_model = ExpenseFilterProxyModel(self)
        self.filter_model.setSourceModel(self.table_model)

        self.table = QTableView()
        self.table.setModel(self.filter_model)
        self.table.setItemDelegate(ExpenseDelegate(self.table))

        self.table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.table.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )
        self.table.setAlternatingRowColors(True)
        self.table.setSortingEnabled(True)

        self.table.sortByColumn(
            self.PURCHASE_DATE_COLUMN,
            Qt.SortOrder.DescendingOrder,
        )

        header = self.table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setContextMenuPolicy(
            Qt.ContextMenuPolicy.CustomContextMenu
        )
        header.customContextMenuRequested.connect(
            self.show_header_filter_menu
        )

        self.setCentralWidget(self.table)

        self._create_actions()
        self._create_menus()
        self._create_toolbar()

        self.statusBar().showMessage("No database loaded")
        self.confirm_close = lambda: True

    def _create_actions(self):
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

        self.edit_menu.addSeparator()
        self.clear_filters_action = self.edit_menu.addAction(
            "Clear All Filters"
        )
        self.clear_filters_action.triggered.connect(
            self.clear_all_filters
        )

        self.reports_menu = self.menuBar().addMenu("Reports")
        self.expense_summary_action = self.reports_menu.addAction(
            "Expense Summary..."
        )

        self.save_action.setShortcut("Ctrl+S")
        self.add_action.setShortcut("Ctrl+N")
        self.delete_action.setShortcut("Delete")
        self.exit_action.triggered.connect(self.close)

    def _create_menus(self):
        pass

    def _create_toolbar(self):
        toolbar = QToolBar("Expense Actions", self)
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        toolbar.addAction(self.add_action)
        toolbar.addAction(self.delete_action)
        toolbar.addSeparator()
        toolbar.addAction(self.save_action)
        toolbar.addAction(self.discard_action)

    def selected_row(self) -> int | None:
        """Return the underlying source-model row."""
        proxy_index = self.table.currentIndex()

        if not proxy_index.isValid():
            return None

        return self.filter_model.mapToSource(proxy_index).row()

    def show_header_filter_menu(self, position):
        """Display filtering commands for a column header."""
        header = self.table.horizontalHeader()
        column = header.logicalIndexAt(position)

        supported = (
            self.PURCHASE_DATE_COLUMN,
            self.VENDOR_COLUMN,
            self.TYPE_COLUMN,
            self.SUBTYPE_COLUMN,
        )

        if column not in supported:
            return

        menu = QMenu(self)

        configure_action = menu.addAction("Set Filter...")
        clear_action = menu.addAction("Clear This Filter")

        menu.addSeparator()
        clear_all_action = menu.addAction("Clear All Filters")

        selected = menu.exec(header.mapToGlobal(position))

        if selected == configure_action:
            self.configure_column_filter(column)

        elif selected == clear_action:
            self.clear_column_filter(column)

        elif selected == clear_all_action:
            self.clear_all_filters()

    def configure_column_filter(self, column: int):
        """Open the appropriate filter configuration dialog."""
        if column == self.PURCHASE_DATE_COLUMN:
            self.configure_date_filter()

        elif column == self.VENDOR_COLUMN:
            self.configure_vendor_filter()

        elif column == self.TYPE_COLUMN:
            self.configure_type_filter()

        elif column == self.SUBTYPE_COLUMN:
            self.configure_subtype_filter()

    def configure_date_filter(self):
        dialog = DateRangeFilterDialog(
            parent=self,
            start_date=self.filter_model._start_date,
            end_date=self.filter_model._end_date,
        )

        if dialog.exec() == QDialog.DialogCode.Accepted:
            start, end = dialog.get_date_range()
            self.filter_model.set_date_filter(start, end)
            self.update_filter_status()

    def configure_vendor_filter(self):
        vendors = sorted(
            {
                expense.vendor.strip()
                for expense in self.table_model.expenses
                if expense.vendor and expense.vendor.strip()
            },
            key=str.casefold,
        )

        if not vendors:
            return

        dialog = SelectionFilterDialog(
            title="Filter Vendor",
            label="Select a vendor:",
            choices=vendors,
            current_value=self.filter_model._vendor,
            parent=self,
        )

        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.filter_model.set_vendor_filter(
                dialog.selected_value()
            )
            self.update_filter_status()

    def configure_type_filter(self):
        dialog = SelectionFilterDialog(
            title="Filter Type",
            label="Select an expense type:",
            choices=list(CATEGORIES.keys()),
            current_value=self.filter_model._expense_type,
            parent=self,
        )

        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.filter_model.set_type_filter(
                dialog.selected_value()
            )
            self.update_filter_status()

    def configure_subtype_filter(self):
        expense_type = self.filter_model._expense_type

        if expense_type is not None:
            subtypes = list(CATEGORIES[expense_type])
        else:
            subtypes = sorted(
                {
                    subtype
                    for values in CATEGORIES.values()
                    for subtype in values
                }
            )

        dialog = SelectionFilterDialog(
            title="Filter Subtype",
            label="Select an expense subtype:",
            choices=subtypes,
            current_value=self.filter_model._subtype,
            parent=self,
        )

        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.filter_model.set_subtype_filter(
                dialog.selected_value()
            )
            self.update_filter_status()

    def clear_column_filter(self, column: int):
        """Clear only the filter associated with one column."""
        if column == self.PURCHASE_DATE_COLUMN:
            self.filter_model.set_date_filter(None, None)

        elif column == self.VENDOR_COLUMN:
            self.filter_model.set_vendor_filter(None)

        elif column == self.TYPE_COLUMN:
            self.filter_model.set_type_filter(None)

        elif column == self.SUBTYPE_COLUMN:
            self.filter_model.set_subtype_filter(None)

        self.update_filter_status()

    def clear_all_filters(self):
        """Remove every active filter."""
        self.filter_model.clear_filters()
        self.update_filter_status()

    def update_filter_status(self):
        """Display the number of visible and total transactions."""
        visible = self.filter_model.rowCount()
        total = self.table_model.rowCount()

        self.statusBar().showMessage(
            f"Showing {visible} of {total} expenses"
        )

    def show_error(self, title: str, message: str) -> None:
        QMessageBox.critical(self, title, message)

    def closeEvent(self, event):
        if self.confirm_close():
            event.accept()
        else:
            event.ignore()


# ==========================================================================================
# ==========================================================================================
# eof
