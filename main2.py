import pyaudio
import numpy as np
import curses
import wave
import asyncio
import librosa
from threading import *

yesFile = 'yes.wav'
corbinYesFile = 'corbinYes.wav'
tmpFile = 'tmp.wav'
chunk = 1024      # Each chunk will consist of 1024 samples
sample_format = pyaudio.paInt16      # 16 bits per sample
dt = np.int16
channels = 1      # Number of audio channels
sampleRate = 44100        # Record at 44100 samples per second
frames = []  # Initialize array to store frames

# Initialize curses
stdscr = curses.initscr()
curses.noecho()
curses.cbreak()
# stdscr.nodelay(True)
stdscr.keypad(True)
stdscr.clear()

# Initialize PyAudio
audio = pyaudio.PyAudio()

# Initialize wav file
# yes = wave.open(yesFile, 'rb')
# corbinYes = wave.open(corbinYesFile, 'rb')
# rec = None
# stdscr.addstr(str(audio.get_format_from_width(yes.getsampwidth())) + '\n') # 8
# stdscr.addstr(str(yes.getnchannels()) + '\n') # 2
# stdscr.addstr(str(yes.getframerate()) + '\n')

outstream = audio.open(format=sample_format,
                       channels=channels,
                       rate=sampleRate,
                       frames_per_buffer=chunk,
                       output=True)


def main():
    try:
        print = stdscr.addstr

        def debug(s):
            print(str(s))
            return s

        ########################## The actual code ##########################

        def playNote(note, octave):
            # outstream = audio.open(format=sample_format,
            #            channels=channels,
            #            rate=sampleRate,
            #            frames_per_buffer=chunk,
            #            output=True)

            if note == 'a':
                while len(data := yes.readframes(chunk)):
                    outstream.write(data)
                yes.rewind()
            else:
                stdscr.clear()
                stdscr.addstr(f'{key} is not recognized\n')

            # outstream.stop_stream()
            # outstream.close()

        # Play the sound by writing the audio data to the stream
        octave = 1
        while True:
            key = stdscr.getkey()

            try:
                octave = int(key)
            except ValueError:
                # asyncio.create_task(playNote(key, octave))
                # Thread(target=playNote, args=(key, octave)).start()
                outstream.write(librosa.load('test.wav', mono=True, sr=44100)[0].tobytes())


        #####################################################################

    finally:
        # Stop, Close and terminate the stream
        outstream.stop_stream()
        outstream.close()
        audio.terminate()

        # Close curses
        curses.nocbreak()
        stdscr.keypad(False)
        curses.echo()
        curses.endwin()

        # Close the wav files
        yes.close()

# asyncio.run(main())

if __name__ == '__main__':
    main()