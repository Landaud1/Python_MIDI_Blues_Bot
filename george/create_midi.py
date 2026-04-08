from mido import Message, MidiFile, MidiTrack

def write_single_note(note, duration_ticks, filename='output.mid', velocity=64):
    """
    Writes a single MIDI note to a file.

    Parameters:
        note (int): MIDI note number (e.g., 60 = Middle C)
        duration_ticks (int): Duration of the note in ticks
        filename (str): Output MIDI file name
        velocity (int): Note velocity (0–127)
    """

    mid = MidiFile()
    track = MidiTrack()
    mid.tracks.append(track)

    # Note ON
    track.append(Message('note_on', note=note, velocity=velocity, time=0))
    # Note OFF
    track.append(Message('note_off', note=note, velocity=velocity, time=duration_ticks))
    mid.save(filename)
