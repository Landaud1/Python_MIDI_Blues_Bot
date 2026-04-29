# -*- coding: utf-8 -*-
"""
Created on Wed Mar 25 20:35:22 2026

MIDI Files handling

@author: aaron
"""

# Considering the most common armonica type:
# Diatonic Harmonica in C

# Importing MIDI library
from mido import MidiFile, MidiTrack, Message

# Diatonic Harmonica in C playable range (MIDI numbers)
# Lowest playable note  : C4 = 60
# Highest playable note : C7 = 96
HARMONICA_LOW  = 60   # C4
HARMONICA_HIGH = 96   # C7


def octave_to_range(note):
    """Shift a MIDI note by full octaves (+/-12 semitones) until it falls
    inside the diatonic C harmonica's playable range [C4=60, C7=96].

    A loop is used so notes that are several octaves away from the
    instrument's range still end up inside it.
    """
    while note < HARMONICA_LOW:
        note += 12
    while note > HARMONICA_HIGH:
        note -= 12
    return note


def closest_scale_note(note):
    """Returns the closest MIDI note inside the C major scale"""
    # C=60, there are 12 semitones => C%12 = 0
    scale_c_major = (0, 2, 4, 5, 7, 9, 11)  # C D E F G A B
    pitch_class = note % 12
    if pitch_class in scale_c_major:
        return note

    # Search for the closest note in the scale (lower or higher)
    for offset in range(1, 12):
        if (pitch_class + offset) % 12 in scale_c_major:
            return note + offset
        if (pitch_class - offset) % 12 in scale_c_major:
            return note - offset

    return note  # least possible case, unlikely


def main():
    # ---------------------------------
    # 1 - Loading MIDI file
    # ---------------------------------

    music_file = MidiFile("harmonic.mid")

    # Allowed unique notes for harmonica (MIDI):
    # C4=60, D4=62, E4=64, G4=67, B4=71, C5=72, D5=74, E5=76, F5=77,
    # G5=79, A5=81, B5=83, C6=84, D6=86, E6=88, F6=89, G6=91, A6=93, C7=96

    # ---------------------------------
    # 2 - Create new MIDI converted file
    # ---------------------------------

    new_mid = MidiFile()

    # ---------------------------------
    # 3 - Processing each file note
    # ---------------------------------

    for original_track in music_file.tracks:
        new_track = MidiTrack()
        new_mid.tracks.append(new_track)

        # Make sure there is an assiggnated instrument
        new_track.append(Message('program_change', program=0, time=0))

        # Processing notes
        for msg in original_track:
            if msg.type in ("note_on", "note_off"):
                # 1) Bring the note into the harmonica's playable range
                #    (C4..C7) by shifting full octaves up or down.
                in_range_note = octave_to_range(msg.note)
                # 2) Fit the in-range note to the closest C major scale.
                new_note = closest_scale_note(in_range_note)
                new_msg = Message(msg.type, note=new_note,
                                  velocity=msg.velocity, time=msg.time,
                                  channel=msg.channel)
                new_track.append(new_msg)
            else:
                # Copy meta messages and control changes
                new_track.append(msg)

    # ---------------------------------
    # 4 - Saving file
    # ---------------------------------
    output_file = "output_harmonica.mid"
    new_mid.save(output_file)
    print("File conversion completed, File:", output_file)


main()
