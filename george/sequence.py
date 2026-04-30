class Sequence():

    def __init__(self):
        self.__notes = []

    def addNote(self, note):
        note.show()
        self.__notes += [note]

    def removeNote(self, note):
        self.__notes.remove(note)

    @property
    def notes(self):
        return self.__notes

    # Convert from sequence of note class to mido track for eventual midifile write
    def to_midi_track(self):
        events = []

        # Append General start and end messages per note
        for n in self.__notes:
            events.append((n.getStart(), Message('note_on',  note=n.getPitch(), velocity=n.getVelocity(), channel=n.getChannel())))
            events.append((n.end,       Message('note_off', note=n.getPitch(), velocity=0,               channel=n.getChannel())))

        # Sort new events by timing
        events.sort(key=lambda e: (e[0], e[1].type == 'note_on'))

        # Write and return track 
        track = MidiTrack()
        last_time = 0
        for abs_time, msg in events:
            msg.time = abs_time - last_time
            track.append(msg)
            last_time = abs_time

        return track
