Libraries to install:

PySide6         # For graphics
mido            # For midi data processing classes
python-rtmidi   # some sort of backend library for midi playback. The regular "rtmidi" is not supported in newer versions.


Instructions:

Run the program with
python ./bluesbot.py

You start with an empty midi file. Pressing any piano key will append that note to the end of the file (with constant timing). Play a little song and press "Play MIDI" to hear it played back/

Pressing "Load MIDI" allows you to select a midi file to play and edit. A sample file is included. It's the song Willy Wonka plays on his piccolo to summon an oompa loompa.
Any piano notes played after a midi file is loaded will be appended to the end of the loaded song.

Pressing "Save MIDI" allows you to name a file the currently loaded song will be saved to. This includes any notes appended with the piano.

Pressing "Convert MIDI" processes the current midi file so each not fits within the C Diatonic scale, which is the range of notes our harmonica is able to play.
Feel free to try it with the sample MIDI to hear how the song changes, or with a song you created yourself. Each black note played will be shifted to a white note.