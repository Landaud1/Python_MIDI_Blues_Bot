import pianoRoll as pr
import mido as md
from PySide6 import QtWidgets
from PySide6.QtCore import QRect, QMimeData, Qt
from PySide6.QtGui import QPainter, QColor, QDrag

TIME_SCALE_FACTOR = 128


class Sequence():

    def __init__(self):
        self.__notes = []
        self.__tpb = 480 # Ticks per beat

    def addNote(self, note):
        note.show()
        self.__notes += [note]

    def removeNote(self, note):
        self.__notes.remove(note)

    # Convert from sequence of note class to mido track for eventual midifile write
    def note_to_track(self):
        events = []

        # Append General start and end messages per note
        for n in self.__notes:
            events.append((n.getStart(), md.Message('note_on',  note=n.getPitch(), velocity=n.getVelocity(), channel=n.getChannel())))
            events.append((n.end,       md.Message('note_off', note=n.getPitch(), velocity=0,               channel=n.getChannel())))
            print(f"{n.getStart()}, {n.end}")

        # Sort new events by timing
        events.sort(key=lambda e: (e[0], e[1].type == 'note_on'))

        # Write and return track 
        track = md.MidiTrack()
        last_time = 0
        for abs_time, msg in events:
            msg.time = abs_time - last_time
            track.append(msg)
            last_time = abs_time

        # Add to midi file
        mid = md.MidiFile(ticks_per_beat = self.__tpb)
        mid.tracks.append(track)
        return mid

    def track_to_note(self, track, parent):
        # self.__tpb = track.ticks_per_beat

        #Dictionary to track times keyed by note
        active_notes = {}

        current_time = 0

        for msg in track:

            current_time += msg.time

            # Detect beginning of note, add to dictionary
            if msg.type == 'note_on' and msg.velocity > 0:
                key = (msg.note, msg.channel)
                if key not in active_notes:
                    active_notes[key] = []
                active_notes[key].append((current_time, msg.velocity))


            # Detect end of note, fully define in dictionary
            elif (msg.type == 'note_off') or (msg.type == 'note_on' and msg.velocity == 0):
                key = (msg.note, msg.channel)

                if key in active_notes:
                    start_time, velocity = active_notes[key].pop(0)

                    duration = current_time - start_time

                    print(f"{start_time}, {duration}, {msg.note}")

                    note = Note(start=start_time, duration=duration, pitch=msg.note, velocity=velocity, channel=msg.channel, parent=parent)
                    self.addNote(note)

# "Note" class definition (used to store note information before construction a song)
class Note(QtWidgets.QWidget):
    def __init__(self, start, duration, pitch, velocity=64, channel=0, parent=None):
        super().__init__(parent)

        self.start = start
        self.duration = duration 
        self.pitch = pitch
        self.velocity = velocity
        self.channel = channel

        # Rectangle for drawing :)
        self.__rect = QRect(pr.start_to_x(self.start), pr.pitch_to_y(self.pitch), self.duration * TIME_SCALE_FACTOR, pr.KEY_HEIGHT)
        self.setGeometry(self.__rect)

    def setStart(self, start):
        self.start=start
        self.__rect = QRect(pr.start_to_x(self.start), pr.pitch_to_y(self.pitch), self.duration * TIME_SCALE_FACTOR, pr.KEY_HEIGHT)
        self.setGeometry(self.__rect)

    def setDuration(self, duration):
        self.duration = duration
        self.__rect = QRect(pr.start_to_x(self.start), pr.pitch_to_y(self.pitch), self.duration * TIME_SCALE_FACTOR, pr.KEY_HEIGHT)
        self.setGeometry(self.__rect)

    def setPitch(self, pitch):
        self.pitch = pitch
        self.__rect = QRect(pr.start_to_x(self.start), pr.pitch_to_y(self.pitch), self.duration * TIME_SCALE_FACTOR, pr.KEY_HEIGHT)
        self.setGeometry(self.__rect)

    def getStart(self):
        return self.start
    def getDuration(self):
        return self.duration
    def getPitch(self):
        return self.pitch
    def getVelocity(self):
        return self.velocity
    def getChannel(self):
        return self.channel
    def getRect(self):
        return self.__rect

    @property
    def end(self):
        return self.getStart() + self.getDuration()
    
    # UI stuff

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setBrush(QColor(50, 170, 50))
        painter.drawRect(0, 0, self.width(), self.height())

    # dies when double clicked
    def mouseDoubleClickEvent(self, event):
        self.parent().removeNote(self)
        self.deleteLater()

    # Moves when dragged
    def mouseMoveEvent(self, e):
        if e.buttons() == Qt.MouseButton.LeftButton:
            drag = QDrag(self)
            mime = QMimeData()
            drag.setMimeData(mime)
            drag.exec(Qt.DropAction.MoveAction)
