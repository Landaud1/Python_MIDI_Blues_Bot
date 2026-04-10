import sys
from PySide6 import QtWidgets
import ui.pianoRoll as pr
import midiFunctions as mf
import mido
import time

# The main window of the application, inherits from QtWidget
class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        # Initial first midi
        self.__mid = mido.MidiFile()
        track = mido.MidiTrack()
        track.append(mido.MetaMessage('end_of_track', time=0))
        self.__mid.tracks.append(track)

        # Initialize window
        self.__port = mido.open_output(mido.get_output_names()[0])

        # Piano keys
        self.piano = pr.PianoKeys(self.__port)
        self.piano.setMidi(self.__mid)

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.piano)

        # Load midi
        self.load_midi_button = QtWidgets.QPushButton()
        self.load_midi_button.setText("Load MIDI")
        self.load_midi_button.pressed.connect(self._load_midi)
        self.layout.addWidget(self.load_midi_button)

        # Save midi
        self.save_midi_button = QtWidgets.QPushButton()
        self.save_midi_button.setText("Save MIDI")
        self.save_midi_button.pressed.connect(self._save_midi)
        self.layout.addWidget(self.save_midi_button)

        # Play midi
        self.play_midi_button = QtWidgets.QPushButton()
        self.play_midi_button.setText("Play MIDI")
        self.play_midi_button.pressed.connect(self._play_midi)
        self.layout.addWidget(self.play_midi_button)

        # Convert midi
        self.convert_midi_button = QtWidgets.QPushButton()
        self.convert_midi_button.setText("Convert MIDI")
        self.convert_midi_button.pressed.connect(self._convert_midi)
        self.layout.addWidget(self.convert_midi_button)

    def _load_midi(self):
        # Prompt for file selection
        dialog = QtWidgets.QFileDialog(self)
        dialog.setNameFilter("MIDI Files (*.mid *.midi)")
        dialog.setFileMode(QtWidgets.QFileDialog.ExistingFile)
        filename = dialog.getOpenFileName()[0] # Returns a tuple with first value filename...

        # Load the midi file
        self.__mid = mido.MidiFile(filename)
        self.piano.setMidi(self.__mid)
        return
    
    def _save_midi(self):
        # Prompt for file selection
        dialog = QtWidgets.QFileDialog(self)
        dialog.setNameFilter("MIDI Files (*.mid *.midi)")
        dialog.setFileMode(QtWidgets.QFileDialog.AnyFile)
        filename = dialog.getSaveFileName()[0]

        # Save the midi file
        if not filename == None:
            self.__mid.save(filename)
        return
    
    def _play_midi(self):
        # I have to refresh the midi file to fix a bug :(
        self.__mid = mf.reload_file(self.__mid)
        self.piano.setMidi(self.__mid)
        # Play each msg in the midi file
        for msg in self.__mid.play():
            self.__port.send(msg)
        return
    
    def _convert_midi(self):
        self.__mid = mf.convert_diatonic(self.__mid)
        self.piano.setMidi(self.__mid)
        return

    # close the port upon window close
    def closeEvent(self, event):
        self.__port.close()
        super().closeEvent(event)


# Main function of the program, launches the main window
if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    main_window = MainWindow()
    main_window.resize(800, 800)
    main_window.show()

    sys.exit(app.exec())