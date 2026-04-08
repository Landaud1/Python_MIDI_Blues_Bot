import os
from mido import Message, MidiFile, MidiTrack

def append_note(note, duration_ticks, filename='output.mid', velocity=64):
    """
    Appends a MIDI note to an existing file (or creates one if it doesn't exist).

    Parameters:
        note (int): MIDI note number (e.g., 60 = Middle C)
        duration_ticks (int): Duration of the note in ticks
        filename (str): Output MIDI file name
        velocity (int): Note velocity (0–127)
    """

    # Load existing MIDI file
    if os.path.exists(filename):
        mid = MidiFile(filename)
        track = mid.tracks[0]
    else:
        print(f"Midi File {filename} does not exist")

    # Add note ON
    track.append(Message('note_on', note=note, velocity=velocity, time=0))
    # Add note OFF
    track.append(Message('note_off', note=note, velocity=velocity, time=duration_ticks))
    mid.save(filename)
