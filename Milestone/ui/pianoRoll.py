from PySide6 import QtWidgets
import mido
import midiFunctions as mf

KEY_HEIGHT = 24
KEY_WIDTH = 75

class PianoKeys(QtWidgets.QWidget):

    def __init__(self, port):
        super().__init__()

        # Initial values
        self.__port = port
        self.__mid = None
        self.__keys = []

        # Start drawing the keys
        # I'm going to use this array to haphazardly draw the keys. It represents the c major scale
        scale = [1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1] 

        curr_note = 96 # Start at C7

        # Starting position
        key_y = 10

        while (curr_note >= 60): # End at C4
            key_type = scale[(curr_note % 12)]

            # Add key
            key = Key(curr_note, self.__port, self)

            # aesthetics and properties based on key type
            if key_type: # White key
                key.move(10, key_y)
                key.setMinimumHeight(KEY_HEIGHT)
                key.setMaximumHeight(KEY_HEIGHT)
                key.setMinimumWidth(KEY_WIDTH)
                key.setMaximumWidth(KEY_WIDTH)
                # for color
                key.setStyleSheet("""
                    QPushButton {
                        background-color: white;
                        border: 1px solid black;
                    }
                    QPushButton:pressed {
                        background-color: #ccc;
                    }
                """)
                key.lower()
            else: # Black key
                key.move(10, key_y + KEY_HEIGHT / 4)
                key.setMinimumHeight(KEY_HEIGHT/2)
                key.setMaximumHeight(KEY_HEIGHT/2)
                key.setMinimumWidth(KEY_WIDTH * 0.6)
                key.setMaximumWidth(KEY_WIDTH * 0.6)
                # for color
                key.setStyleSheet("""
                    QPushButton {
                        background-color: black;
                    }
                    QPushButton:pressed {
                        background-color: #555;
                    }
                """)
                key.raise_()

            # Decide next position based on key type
            if (curr_note > 60):
                next_key = scale[((curr_note - 1) % 12)]
                # adjacent white notes get full width
                if key_type == next_key:
                    key_y += KEY_HEIGHT
                else:
                    key_y += KEY_HEIGHT/2
            
            # Keep list of keys
            self.__keys.append(key)

            # iterate
            curr_note -= 1

    def setMidi(self, mid):
        self.__mid = mid
        
        for key in self.__keys:
            key.setMidi(self.__mid)

    def setPort(self, port):
        self.__port = port

        for key in self.__keys:
            key.setPort(self.__port)
        
class Key(QtWidgets.QPushButton):

    def __init__(self, note, port, parent):
        super().__init__(parent)

        self.__port = port
        self.__note = note
        self.__mid = None
        self.pressed.connect(self._on_click)
    
    def setPort(self, port):
        self.__port = port

    def _on_click(self):
        # plays the note
        msg = mido.Message('note_on', note=self.__note, time=0, velocity=64)
        self.__port.send(msg)
        # msg = mido.Message('note_off', note=self.__note, time=256)
        # self.__port.send(msg)

        # Appends the note to current file
        if not self.__mid == None:
            mf.append_note(self.__note, 128, self.__mid)
        
    def setMidi(self, mid):
        self.__mid = mid