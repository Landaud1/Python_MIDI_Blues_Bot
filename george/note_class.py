# "Note" class definition (used to store note information before construction a song)

class Note:
    def __init__(self, start, duration, pitch, velocity=64, channel=0):
        self.start = start
        self.duration = duration
        self.pitch = pitch
        self.velocity = velocity
        self.channel = channel

    def setStart(self, start):
        self.start=start
    def setDuration(self, duration):
        self.duration = duration

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

    @property
    def end(self):
        return self.start + self.duration
