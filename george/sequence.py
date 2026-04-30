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
    def note_to_track(self):
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

    def track_to_note(self, track):

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

                    note = Note(start=start_time, duration=duration, pitch=msg.note, velocity=velocity, channel=msg.channel)
                    self.__notes.append(note)

    
