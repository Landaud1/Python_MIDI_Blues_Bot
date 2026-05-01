# -*- coding: utf-8 -*-
"""
MIDI -> Diatonic C Harmonica converter

Created on Wed Mar 25 20:35:22 2026
@author: aaron

Reads a MIDI file ("harmonic.mid") and writes a new MIDI file
("output_harmonica.mid") where every note is playable on a diatonic C
harmonica. To do so, the converter applies three passes to each note:

    1. Octave normalization. Notes outside the harmonica's playable range
       [C4 = 60 .. C7 = 96] are shifted by full octaves until they fit.
    2. Closest harmonica note. Each in-range note is matched to the nearest of
       the 19 MIDI numbers an actual diatonic C harmonica can produce.
    3. Blow/draw conflict resolution. When a note arrives at the same
       MIDI tick (delta time = 0) as another note that is still sounding,
       and one is a pure-blow note while the other is a pure-draw note,
       the second is dropped (first-come-first-served) so the result is
       physically playable on a real harmonica.

A small summary of what the conversion did is printed when it finishes.
"""

from mido import MidiFile, MidiTrack, Message


# ---------------------------------------------------------------------------
# Diatonic C harmonica reference data
# ---------------------------------------------------------------------------

# Playable range (MIDI note numbers)
HARMONICA_LOW  = 60   # C4
HARMONICA_HIGH = 96   # C7

# Every note an actual diatonic C harmonica can produce.
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
#   blow only : C, E         (you can only get them by exhaling)
#   draw only : D, F, A, B   (you can only get them by inhaling)
#   both      : G            (G appears on both a blow hole and a draw hole)
# A pure-blow note and a pure-draw note cannot physically be played at
# the same time.
BLOW_ONLY_PC = {0, 4}         # C, E
DRAW_ONLY_PC = {2, 5, 9, 11}  # D, F, A, B


# ---------------------------------------------------------------------------
# Note transformation helpers
# ---------------------------------------------------------------------------

def octave_to_range(note):
    """Shift a MIDI note by full octaves (+/-12 semitones) until it falls
    inside the diatonic C harmonica's playable range [C4=60, C7=96]."""
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
    19 actually playable holes/breaths. Ties (equidistant lower and
    higher candidate) round DOWN, which is the safer, mellower choice.
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


# ---------------------------------------------------------------------------
# Main conversion
# ---------------------------------------------------------------------------

def main():
    # 1 - Loading MIDI file
    music_file = MidiFile("harmonic.mid")

    # 2 - Create new MIDI converted file
    new_mid = MidiFile()

    # Conversion summary counters (across all tracks)
    notes_processed     = 0  # real note_on events seen
    notes_octave_shift  = 0  # notes octave_to_range() actually moved
    notes_remapped      = 0  # in-range notes the harmonica snapper had to move
    conflicts_dropped   = 0  # blow/draw collisions skipped

    # 3 - Processing each file note
    for original_track in music_file.tracks:
        new_track = MidiTrack()
        new_mid.tracks.append(new_track)

        # Make sure there is an assigned instrument
        new_track.append(Message('program_change', program=0, time=0))

        # State machine for blow/draw conflict detection (per track):
        #   sounding         : original_note_number -> "blow" / "draw" / "both"
        #                      Notes whose note_on has been emitted but whose
        #                      note_off has not arrived yet.
        #   dropped_pending  : original_note_number -> int. How many of THIS
        #                      note's note_offs we still have to swallow
        #                      because we dropped their matching note_on.
        #   pending_delta    : delta time accumulated from dropped messages,
        #                      added back to the next kept message so the
        #                      track's overall timing is preserved.
        sounding = {}
        dropped_pending = {}
        pending_delta = 0

        for msg in original_track:
            if msg.type in ("note_on", "note_off"):
                # Pass 1: bring the note into the harmonica's playable range.
                in_range_note = octave_to_range(msg.note)
                if in_range_note != msg.note and msg.type == "note_on" and msg.velocity > 0:
                    notes_octave_shift += 1
                # Pass 2: snap to the nearest note the harmonica can produce.
                new_note = closest_harmonica_note(in_range_note)
                if new_note != in_range_note and msg.type == "note_on" and msg.velocity > 0:
                    notes_remapped += 1

                kind = breath_kind(new_note)
                # MIDI files often use "note_on with velocity 0" as note_off.
                is_real_note_on = (msg.type == "note_on" and msg.velocity > 0)

                if is_real_note_on:
                    notes_processed += 1
                    # Pass 3: blow/draw conflict detection. Only fires when
                    # the new note arrives at the same tick as a still-sounding note.
                    conflict = False
                    if msg.time == 0 and sounding:
                        current_kinds = set(sounding.values())
                        if kind == "blow" and "draw" in current_kinds:
                            conflict = True
                        elif kind == "draw" and "blow" in current_kinds:
                            conflict = True

                    if conflict:
                        # First-come-first-served: keep the older sounding
                        # note, drop this note_on AND remember to swallow its
                        # matching note_off later.
                        dropped_pending[msg.note] = dropped_pending.get(msg.note, 0) + 1
                        pending_delta += msg.time
                        conflicts_dropped += 1
                        continue

                    sounding[msg.note] = kind
                    new_track.append(Message(
                        msg.type, note=new_note, velocity=msg.velocity,
                        time=msg.time + pending_delta, channel=msg.channel))
                    pending_delta = 0

                else:  # real note_off (or note_on with velocity 0)
                    if dropped_pending.get(msg.note, 0) > 0:
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

    # 4 - Saving file
    output_file = "output_harmonica.mid"
    new_mid.save(output_file)

    # 5 - Conversion summary
    print("File conversion completed.")
    print('  Output file               : "{}"'.format(output_file))
    print("  Notes processed           :", notes_processed)
    print("  Octave-shifted into range :", notes_octave_shift)
    print("  Remapped to harmonica set :", notes_remapped)
    print("  Blow/draw conflicts dropped:", conflicts_dropped)


main()
