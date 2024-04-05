import pyaudio
import numpy as np
import curses
import wave


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
stdscr.nodelay(True)
stdscr.keypad(True)
stdscr.clear()

# Initialize PyAudio
audio = pyaudio.PyAudio()

# Initialize wav file
yes = wave.open(yesFile, 'rb')
corbinYes = wave.open(corbinYesFile, 'rb')
rec = None
# stdscr.addstr(str(audio.get_format_from_width(yes.getsampwidth())) + '\n') # 8
# stdscr.addstr(str(yes.getnchannels()) + '\n') # 2
# stdscr.addstr(str(yes.getframerate()) + '\n')

# Create input and output streams
instream = audio.open(format=sample_format,
                      channels=channels,
                      rate=sampleRate,
                      frames_per_buffer=chunk,
                      input=True)

outstream = audio.open(format=sample_format,
                       channels=channels,
                       rate=sampleRate,
                       frames_per_buffer=chunk,
                       output=True)

try:






    ########################## The actual code ##########################

    prevKey = -1
    passThrough = lambda data: data
    nothing     = lambda data: np.zeros(chunk, dt)
    defaultFunc = passThrough
    useFunc = defaultFunc

    def low_pass_filter(data, band_limit, sampling_rate):
        cutoff_index = int(band_limit * data.size / sampling_rate)
        F = np.fft.rfft(data)
        F[cutoff_index + 1:] = 0
        return np.fft.irfft(F, n=data.size).real

    def playYes(_):
        data = yes.readframes(chunk)
        return data if data != '' else defaultFunc(data)

    def closeYes():
        yes.rewind()

    def playCorbinYes(_):
        data = corbinYes.readframes(chunk)
        return data if data != '' else defaultFunc(data)

    def closeCorbinYes():
        corbinYes.rewind()

    def playRecorded(_):
        global rec
        if rec is None:
            rec = wave.open(tmpFile, 'rb')
        data = rec.readframes(chunk)
        if data != '':
            return data
        else:
            rec.close()
            return defaultFunc(data)

    def closePlayRecorded():
        global rec
        stdscr.addstr('closePlayRecorded ran')
        print('closePlayRecorded ran')
        rec.rewind()
        rec.close()
        rec = None

    def record(data):
        global rec
        if rec is None:
            rec = wave.open(tmpFile, 'wb')
            rec.setnchannels(channels)
            rec.setsampwidth(audio.get_sample_size(sample_format))
            rec.setframerate(sampleRate)
        rec.writeframes(data.tobytes())

        return nothing(data)

    def closeRecord():
        global rec
        stdscr.addstr('closeRecord ran')
        print('closePlayRecorded ran')
        # if rec is not None:
        rec.close()
        rec = None

    def setFunc(key) -> "func":
        global useFunc, prevKey
        # With some of the file functions, we want to close after we've changed
        prevKey = key
        # if key != -1:
        if key != -1:
            stdscr.addstr(chr(prevKey))
            try:
                {
                    'y': closeYes,
                    'u': closeCorbinYes,
                    'r': closeRecord,
                    't': closePlayRecorded,
                }[chr(prevKey)]()
            except KeyError:
                pass

        try:
            try:
                return {
                    -1: useFunc,
                    ' ': passThrough,
                    'a': lambda data: np.ones(chunk, dt),
                    's': lambda data: np.full(chunk, 43, dt),
                    '1': lambda data: np.arange(1, chunk*1, 1, dtype=dt),
                    '2': lambda data: np.arange(1, chunk*2, 2, dtype=dt),
                    '3': lambda data: np.arange(1, chunk*3, 3, dtype=dt),
                    '4': lambda data: np.arange(1, chunk*4, 4, dtype=dt),
                    '5': lambda data: np.arange(1, chunk*5, 5, dtype=dt),
                    '6': lambda data: np.arange(1, chunk*6, 6, dtype=dt),
                    '7': lambda data: np.arange(1, chunk*7, 7, dtype=dt),
                    '8': lambda data: np.arange(1, chunk*8, 8, dtype=dt),
                    '9': lambda data: np.arange(1, chunk*9, 9, dtype=dt),
                    'l': lambda data: low_pass_filter(data, 43, sampleRate),
                    'y': playYes,
                    'u': playCorbinYes,
                    'r': record,
                    't': playRecorded,
                }[chr(key)]
            except KeyError:
                stdscr.clear()
                stdscr.addstr(f'{chr(key)} is not recognized\n')
        except:
            pass
        return useFunc


    # Play the sound by writing the audio data to the stream
    while True:
        useFunc = setFunc(stdscr.getch())
        data = useFunc(np.frombuffer(instream.read(chunk), dt))
        outstream.write(data.tobytes() if type(data) != bytes else data)

    #####################################################################





finally:
    # Stop, Close and terminate the stream
    outstream.stop_stream()
    instream.stop_stream()
    outstream.close()
    instream.close()
    audio.terminate()

    # Close curses
    curses.nocbreak()
    stdscr.keypad(False)
    curses.echo()
    curses.endwin()

    # Close the wav files
    yes.close()
    corbinYes.close()
    if rec is not None:
        rec.close()
