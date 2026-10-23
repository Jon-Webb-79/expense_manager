import sys

from PyQt6.QtWidgets import QApplication

from expense_manager.controllers.expense_controller import ExpenseController
from expense_manager.views.main_window import MainWindow
# ==========================================================================================
# ==========================================================================================

# File:    main.py
# Date:    October 21, 2026
# Author:  Jonathan A. Webb
# Purpose: Application entry point for Expense Manager
# ==========================================================================================
# ==========================================================================================


def main() -> int:
    """Initialize and execute the Expense Manager application."""
    app = QApplication(sys.argv)
    app.setApplicationName("Expense Manager")

    window = MainWindow()
    controller = ExpenseController(window)

    app.aboutToQuit.connect(controller.close)

    window.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
# ==========================================================================================
# ==========================================================================================
# eof
