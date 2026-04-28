import pianoRoll as pr
from PySide6 import QtWidgets
from PySide6.QtCore import QRect
from PySide6.QtGui import QPainter, QColor


class Sequence():

    def __init__(self):
        self.__notes = []

    def addNote(self, note):
        self.__notes += [note]

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
        self.__rect = QRect(pr.start_to_x(self.start), pr.pitch_to_y(self.pitch), self.duration, pr.KEY_HEIGHT)
        self.setGeometry(self.__rect)

    def setStart(self, start):
        self.start=start
        self.__rect = QRect(pr.start_to_x(self.start), pr.pitch_to_y(self.pitch), self.duration, pr.KEY_HEIGHT)
        self.setGeometry(self.__rect)

    def setDuration(self, duration):
        self.duration = duration
        self.__rect = QRect(pr.start_to_x(self.start), pr.pitch_to_y(self.pitch), self.duration, pr.KEY_HEIGHT)
        self.setGeometry(self.__rect)

    def setPitch(self, pitch):
        self.pitch = pitch
        self.__rect = QRect(pr.start_to_x(self.start), pr.pitch_to_y(self.pitch), self.duration, pr.KEY_HEIGHT)
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
        return self.start + self.duration
    
    # UI stuff

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setBrush(QColor(50, 170, 50))
        painter.drawRect(0, 0, self.width(), self.height())
