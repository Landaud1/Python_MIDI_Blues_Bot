import sys
from PySide6 import QtWidgets

# The main window of the application, inherits from QtWidget
class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.button = QtWidgets.QPushButton("Click me!")

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.button)


# Main function of the program, launches the main window
if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    main_window = MainWindow()
    main_window.resize(800, 600)
    main_window.show()

    sys.exit(app.exec())