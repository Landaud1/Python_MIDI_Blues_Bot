from PySide6 import QtWidgets
from PySide6.QtCore import QLineF, QRect
from PySide6.QtGui import QPainter, QPen, QColor
import sequence as sq
import mido
import midiFunctions as mf
import time

KEY_HEIGHT = 24
KEY_WIDTH = 75
scale = [1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1] 

# Some static functions that do ui location/midi property conversions
def x_to_start(x):
    return (x - KEY_WIDTH - 20) / sq.TIME_SCALE_FACTOR

def start_to_x(start):
    return (start * sq.TIME_SCALE_FACTOR) + KEY_WIDTH + 20

def y_to_pitch(y):
    global scale
    pitch = 96 - int((y - 18) / KEY_HEIGHT)
    
    # sub from pitch each black note skipped
    i = 96
    while(i > pitch):
        if scale[(i - 1) % 12] == 0:
            pitch -= 1
        i -= 1

    return pitch



def pitch_to_y(pitch):
    global scale
    # only progress for each white note
    y = 18
    i = 96
    while(i > pitch):
        if scale[(i-1) % 12] == 1:
            y += KEY_HEIGHT
        i -= 1

    return y


class PianoRoll(QtWidgets.QWidget):

    def __init__(self, port):
        super().__init__()
        self.setAcceptDrops(True) #for drag/drop notes

        self.__port = port

        self.layout = QtWidgets.QGridLayout(self)

        # Sequence
        self.__sequence = sq.Sequence()
        # self.layout.addWidget(self.__sequence)

        # Piano keys
        self.piano = PianoKeys(self.__port)
        self.layout.addWidget(self.piano)

    def removeNote(self, note):
        self.__sequence.removeNote(note)

    def getMidi(self):
        return self.__sequence.note_to_track()
    
    def setMidi(self, mid):
        self.__sequence.track_to_note(mid, self)

    # UI Stuff

    def paintEvent(self, event):
        ROLL_LENGTH = 3000

        painter = QPainter(self)

        # Draw rectangle
        self.__rect = QRect(KEY_WIDTH + 20, 18, ROLL_LENGTH, KEY_HEIGHT * 22)

        painter.setBrush(QColor(20, 20, 20))
        painter.drawRect(self.__rect)

        # Draw lines
        self.__lines = []
        for y in range(18, KEY_HEIGHT * 23 + 18, KEY_HEIGHT):
            self.__lines += [QLineF(KEY_WIDTH + 20, y, ROLL_LENGTH + KEY_WIDTH + 20, y)]

        pen = QPen(QColor(100, 100, 100))
        painter.setPen(pen)
        painter.drawLines(self.__lines)

        painter.end()

    # This is overriding a function of QWidget that waits for a double click
    # Using this to create a new note
    def mouseDoubleClickEvent(self, event):
        # find out where the double click happened
        pos = event.position()
        # print(y_to_pitch(pos.y()))
        if y_to_pitch(pos.y()) >= 60 and y_to_pitch(pos.y()) <= 96: #create a note if it's within range
            note = sq.Note(start=x_to_start(pos.x()), pitch=y_to_pitch(pos.y()), duration=240, parent=self)
            self.__sequence.addNote(note=note)

    # To allow for note dragging
    def dragEnterEvent(self, event):
        event.accept()

    # Note moves to new position when dropped
    def dropEvent(self, event):
        pos = event.position()
        print(y_to_pitch(pos.y()))
        if y_to_pitch(pos.y()) >= 60 and y_to_pitch(pos.y()) <= 96: #move note if in ranges
            widget = event.source()
            widget.setStart(x_to_start(pos.x()))
            widget.setPitch(y_to_pitch(pos.y()))

        

        


class PianoKeys(QtWidgets.QWidget):

    def __init__(self, port):
        super().__init__()

        # Initial values
        self.__port = port
        self.__keys = []

        # Start drawing the keys
        # I'm going to use this array to haphazardly draw the keys. It represents the c major scale
        global scale

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

    def setPort(self, port):
        self.__port = port

        for key in self.__keys:
            key.setPort(self.__port)
        
class Key(QtWidgets.QPushButton):

    def __init__(self, note, port, parent):
        super().__init__(parent)

        self.__port = port
        self.__note = note
        self.pressed.connect(self._on_click)
    
    def setPort(self, port):
        self.__port = port

    # Overrides the QPushButton's behavior
    def _on_click(self):
        # plays the note
        msg = mido.Message('note_on', note=self.__note, velocity=64)
        self.__port.send(msg)
        time.sleep(0.5)
        msg = mido.Message('note_off', note=self.__note)
        self.__port.send(msg)