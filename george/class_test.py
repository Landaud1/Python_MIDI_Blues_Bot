from mido import MidiFile, MidiTrack, Message
import sys
import os
from note_class import Note

notes = [
        Note(0, 480, 60),
        Note(0, 0, 62),
        Note(960, 480, 64),
        Note(1920, 960, 67),
        Note(1920, 960, 69)
        ]

#Modifying Notes after creation
notes[1].setStart(240)
notes[1].setDuration(720)
notes[2].setStart(480)

events = []
for n in notes:
    events.append((n.getStart(),Message('note_on',note=n.getPitch(),velocity=n.getVelocity(),channel=n.getChannel())))
    events.append((n.end,Message('note_off',note=n.getPitch(),velocity=0,channel=n.getChannel())))

#Sort Timing
events.sort(key=lambda e: (e[0], e[1].type == 'note_on'))


mid = MidiFile()
track = MidiTrack()
mid.tracks.append(track)

last_time = 0

for abs_time, msg in events:
    delta = abs_time - last_time
    msg.time = delta
    track.append(msg)
    last_time = abs_time

mid.save(sys.argv[1])

print(f"Wrote {sys.argv[1]}")
