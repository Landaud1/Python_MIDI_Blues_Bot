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

# Every note that an actual diatonic C harmonica can produce.
# These are the only MIDI numbers our output is allowed to contain.
# C4=60, D4=62, E4=64, G4=67, B4=71, C5=72, D5=74, E5=76, F5=77,
# G5=79, A5=81, B5=83, C6=84, D6=86, E6=88, F6=89, G6=91, A6=93, C7=96
HARMONICA_NOTES = (
    60, 62, 64, 67, 71,
    72, 74, 76, 77, 79, 81, 83,
    84, 86, 88, 89, 91, 93,
    96,
)

# Pitch-class classification on the diatonic C harmonica:
#   - blow only : C, E         (you can only get them by exhaling)
#   - draw only : D, F, A, B   (you can only get them by inhaling)
#   - both      : G            (G appears on both a blow hole and a draw hole)
# Two notes that are pure-blow + pure-draw cannot physically be played
# at the same time.
BLOW_ONLY_PC = {0, 4}        # C, E
DRAW_ONLY_PC = {2, 5, 9, 11} # D, F, A, B


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


def closest_harmonica_note(note):
    """Return the closest MIDI note that the diatonic C harmonica can play.

    Unlike the C major scale, the harmonica skips a few notes inside its
    own range (for example F4 and A4 do not belong on a diatonic C
    harmonica). This fits any input MIDI number to the nearest of the
    19 actually playable holes/breaths.

    Ties (equidistant lower and higher candidate) round DOWN, which is
    the safer, mellower choice on harmonica.
    """
    if note in HARMONICA_NOTES:
        return note
    return min(HARMONICA_NOTES, key=lambda n: (abs(n - note), n))


def breath_kind(note):
    """Classify a (harmonica-playable) MIDI note as 'blow', 'draw', or
    'both' based on its pitch class. 'both' means G, which lives on
    both a blow hole and a draw hole."""
    pc = note % 12
    if pc in BLOW_ONLY_PC:
        return "blow"
    if pc in DRAW_ONLY_PC:
        return "draw"
    return "both"


def closest_scale_note(note):
    """Closest MIDI note inside the C major scale.

    Kept for reference; the conversion now uses
    closest_harmonica_note() which is stricter.
    """
    scale_c_major = (0, 2, 4, 5, 7, 9, 11)  # C D E F G A B
    pitch_class = note % 12
    if pitch_class in scale_c_major:
        return note

    for offset in range(1, 12):
        if (pitch_class + offset) % 12 in scale_c_major:
            return note + offset
        if (pitch_class - offset) % 12 in scale_c_major:
            return note - offset

    return note


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

    conflicts_dropped = 0  # blow/draw collisions skipped (across all tracks)

    for original_track in music_file.tracks:
        new_track = MidiTrack()
        new_mid.tracks.append(new_track)

        # Make sure there is an assiggnated instrument
        new_track.append(Message('program_change', program=0, time=0))

        # State machine for blow/draw conflict detection (per track):
        #   sounding         : original_note_number -> "blow" / "draw" / "both"
        #                      Notes that have a note_on but no matching note_off yet.
        #   dropped_pending  : original_note_number -> int. How many of THIS note's
        #                      note_offs we still have to swallow because we dropped
        #                      their matching note_on.
        #   pending_delta    : delta time accumulated from messages we dropped, to
        #                      be added to the next message we keep so timing is
        #                      preserved.
        sounding = {}
        dropped_pending = {}
        pending_delta = 0

        for msg in original_track:
            if msg.type in ("note_on", "note_off"):
                # 1) Bring the note into the harmonica's playable range
                #    (C4..C7) by shifting full octaves up or down.
                in_range_note = octave_to_range(msg.note)
                # 2) Snap to the nearest note the diatonic C harmonica
                #    can actually produce (not just the C major scale).
                new_note = closest_harmonica_note(in_range_note)

                kind = breath_kind(new_note)
                # MIDI files often use "note_on with velocity 0" for note_off.
                is_real_note_on = (msg.type == "note_on" and msg.velocity > 0)
                is_real_note_off = (msg.type == "note_off"
                                    or (msg.type == "note_on" and msg.velocity == 0))

                if is_real_note_on:
                    # Blow vs draw conflict only matters when the new note
                    # arrives at delta=0 against a note that's still sounding.
                    conflict = False
                    if msg.time == 0 and sounding:
                        current_kinds = set(sounding.values())
                        if kind == "blow" and "draw" in current_kinds:
                            conflict = True
                        elif kind == "draw" and "blow" in current_kinds:
                            conflict = True

                    if conflict:
                        # First-come-first-served: keep the older sounding note,
                        # drop this note_on AND remember to swallow its note_off
                        # later. Carry its delta forward so timing is preserved.
                        dropped_pending[msg.note] = dropped_pending.get(msg.note, 0) + 1
                        pending_delta += msg.time
                        conflicts_dropped += 1
                        continue

                    # Accepted: register as sounding, emit the message.
                    sounding[msg.note] = kind
                    new_track.append(Message(
                        msg.type, note=new_note, velocity=msg.velocity,
                        time=msg.time + pending_delta, channel=msg.channel))
                    pending_delta = 0

                else:  # real note_off (or note_on velocity=0)
                    if dropped_pending.get(msg.note, 0) > 0:
                        # Matching note_on was dropped, swallow this note_off.
                        dropped_pending[msg.note] -= 1
                        if dropped_pending[msg.note] == 0:
                            del dropped_pending[msg.note]
                        pending_delta += msg.time
                        continue

                    sounding.pop(msg.note, None)
                    new_track.append(Message(
                        msg.type, note=new_note, velocity=msg.velocity,
                        time=msg.time + pending_delta, channel=msg.channel))
                    pending_delta = 0
            else:
                # Copy meta messages and control changes,
                # absorbing any pending delta from dropped notes.
                new_track.append(msg.copy(time=msg.time + pending_delta))
                pending_delta = 0

    # ---------------------------------
    # 4 - Saving file
    # ---------------------------------
    output_file = "output_harmonica.mid"
    new_mid.save(output_file)
    print("File conversion completed, File:", output_file)
    print("Blow/draw conflicts dropped:", conflicts_dropped)
    

main()
