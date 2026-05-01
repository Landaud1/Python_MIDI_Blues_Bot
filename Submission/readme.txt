Libraries to install:

PySide6         # For graphics
mido            # For midi data processing classes
python-rtmidi   # some sort of backend library for midi playback. The regular "rtmidi" is not supported in newer versions.

GitHub page: https://github.com/Landaud1/Python_MIDI_Blues_Bot

Instructions:

Run the program with
python ./bluesbot.py

You start with an empty midi file. Double clicking on the piano roll allows you to create a new note. These notes can be dragged around, or double clicked again to remove them.
The piano on the left can be played but it is only there for aesthetic reasons and does not change the song.

Pressing "Load MIDI" allows you to select a midi file to play and edit. A folder of sample files are included.
When a new MIDI is loaded it is constrained to the constraints of the harmonica the robot uses i.e. the notes are shifted to the C Diatonic scale and blow and draw notes cannot be played at the same time.

Pressing "Save MIDI" allows you to name a file the currently loaded song will be saved to. This includes any changes made.

Pressing "Play MIDI" plays the currently loaded midi with any changes made. Please don't poke the program too much when its doing this its trying its hardest.