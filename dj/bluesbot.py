import sys
from PySide6 import QtWidgets
import ui.pianoRoll as pr
import mido

# The main window of the application, inherits from QtWidget
class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        # Prompt to select audio device
        print("Audio Devices: ")
        for i in range(len(mido.get_output_names())):
            print(f"{i}: {mido.get_output_names()[i]}")

        sel = -1
        while (int(sel) < 0 or int(sel) > len(mido.get_output_names()) - 1):
            sel = input(f"Please enter audio device to use (0-{len(mido.get_output_names())-1}): ")

        # Initialize window
        self.__port = mido.open_output(mido.get_output_names()[int(sel)])

        self.piano = pr.PianoKeys(self.__port)

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.piano)

    # close the port upon window close
    def closeEvent(self, event):
        self.__port.close()
        super().closeEvent(event)


# Main function of the program, launches the main window
if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    main_window = MainWindow()
    main_window.resize(800, 600)
    main_window.show()

    sys.exit(app.exec())