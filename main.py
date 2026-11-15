import sys

from PySide6.QtWidgets import QApplication

from database.database import initialize_database

from ui.login import LoginWindow


def main():

    # Initialize database
    initialize_database()
   

    # Create application
    app = QApplication(sys.argv)

    # Create login window
    window = LoginWindow()

    window.show()

    # Start application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()