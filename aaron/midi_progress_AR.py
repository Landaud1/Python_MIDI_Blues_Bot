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

def closest_scale_note(note):
    """Returns the closest MIDI note inside the C major scale"""
    # C=60, there are 12 semitones => C%12 = 0
    scale_c_major = (0, 2, 4, 5, 7, 9, 11)  # C D E F G A B (in semitones within the octave)
    pitch_class = note % 12
    if pitch_class in scale_c_major:
        return note
    
    # Search for the closest note in the scale (lower or higher)
    for offset in range(1, 12):
        if (pitch_class + offset) % 12 in scale_c_major:
            return note + offset
        if (pitch_class - offset) % 12 in scale_c_major:
            return note - offset

    return note  # fallback (least possible case, unlikely)
    
    
    

def main():
    # ---------------------------------
    # 1 - Loading MIDI file
    # ---------------------------------
    
    music_file = MidiFile("harmonic.mid")

    # Allowed unique notes for harmonica
    # With its respective MIDI number
    # Note	MIDI Number
    # C4	60
    # D4	62
    # E4	64
    # G4	67
    # B4	71
    # C5	72
    # D5	74
    # E5	76
    # F5	77
    # G5	79
    # A5	81
    # B5	83
    # C6	84
    # D6	86
    # E6	88
    # F6	89
    # G6	91
    # A6	93
    # C7	96
    
    # Creating an allowed notes list for diatonic harmonica:
    # allowed_notes = ["C4","D4","E4","G4","B4","C5","D5","E5","F5","G5","A5",
                     # "B5","C6","D6","E6","F6","G6","A6","C7"]
    
    # Creating a dictionary for these notes
    # note_name_to_midi = {"C4":60, "D4":62, "E4":64, "G4":67, "B4":71, "C5":72,
                         # "D5":74, "E5":76, "F5":77, "G5":79, "A5":81, "B5":83, 
                         # "C6":84, "D6":86, "E6":88, "F6":89, "G6":91, "A6":93,
                         # "C7":96}
                         
    # ---------------------------------
    # 2 - Create new MIDI converted file
    # ---------------------------------

    new_mid = MidiFile()
    # track = MidiTrack()
    # new_mid.tracks.append(track)
    
    # ---------------------------------
    # 3 - Processing each file note
    # ---------------------------------
    
    
    # Copy tempo if exist
    for original_track in music_file.tracks:
        new_track = MidiTrack()
        new_mid.tracks.append(new_track)
        
        # Make sure there is an assiggnated instrument
        new_track.append(Message('program_change', program=0, time=0))
    
        # Processing notes
        for msg in original_track:
            # For each message that belongs to playing a note:
            if msg.type in ("note_on", "note_off"):
                new_note = closest_scale_note(msg.note)
                new_msg = Message(msg.type, note=new_note, velocity=msg.velocity, time=msg.time,
                                  channel= msg.channel)
                new_track.append(new_msg)
            else:
                # Copy meta messages and control changes
                new_track.append(msg)
    
    # ---------------------------------
    # 4 - Saving file
    # --------------------------------- 
    # output_file = input("Enter converted file name: ")
    # output_file = output_file + ".mid"
    
    output_file = "output_harmonica.mid"
    
    new_mid.save(output_file)
    
    print("File conversion completed, File: \"", output_file, "\"")

main()




