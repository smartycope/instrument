import numpy as np
# import soundfile as sf
# import wave
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
from pygame import mixer
from pygame.mixer import Sound, Channel
from librosa.effects import *
import librosa
# from  scipy.io import wavfile
from copy import copy, deepcopy
from mido import MidiFile
import mido
from enum import auto
import time

# To improve:
# https://github.com/ederwander/PyAutoTune

INTERACTIVE = False
# SONG = '/home/leonard/Downloads/the_entertainer.mid'
SONG = '/home/leonard/Downloads/The Entertainer.mid'
# SONG = '/home/leonard/Downloads/cantinaband.mid'
# SONG = '/home/leonard/Downloads/starwars-cantina___WWW.MIDISFREE.COM.mid'
# SONG = '/home/leonard/Downloads/Theme of Interstellar - Cornfield Chase___WWW.MIDISFREE.COM.mid'
# SONG = '/home/leonard/Downloads/JurassicPark.mid'
# SONG = '/home/leonard/Downloads/Hanz Zimmer - Time(Inception Theme)___WWW.MIDISFREE.COM.mid'
# SONG = '/home/leonard/Downloads/Never-Gonna-Give-You-Up-3.mid'
# SONG = '/home/leonard/Downloads/imperialmarch.mid'
# SONG = '/home/leonard/Downloads/Super Mario Bros. 1 -  Overworld Theme.mid'
MIDI = MidiFile(SONG, clip=True)
TRACK = MIDI.tracks[1]
# TRACK = MIDI.tracks[0]

# MIDI.print_tracks()
# Use different recordings for each octave, then pitch each note
VARY_OCTAVES = auto()
# Use different recordings for each note, then pitch each octave (not implemented)
VARY_NOTE = auto()
# Pitch every octave and note, using random recordings (not implemented)
VARY_RANDOM = auto()
# Use one recording for every octave and note
VARY_NONE = auto()
# METHOD = VARY_NONE
METHOD = VARY_OCTAVES
# This fixes the timing. As far as I can tell, this is arbitrary
TIME_MULTIPLIER = 20
USE_NOTE_OFFS = False
varyNoneFile = 'yes.wav'
# varyNoneFile = 'e.wav'
# varyNoneFile = '/home/leonard/hello/python/instrument/e.wav'
# varyNoneFile = 'corbinYes.wav'
# varyNoneFile = 'pianoa3.wav'
varyNoneOctave = 3
OCTAVE_OFFSET = -2
SHORT_NOTE_CUTOFF=0 #0.0125 / TIME_MULTIPLIER
dt = np.float32
channels = 1
sampleRate = sr = 44100
pygameChannels = 32



if INTERACTIVE:
    import curses
    # Initialize curses
    stdscr = curses.initscr()
    curses.noecho()
    curses.cbreak()
    # stdscr.nodelay(True)
    stdscr.keypad(True)
    stdscr.clear()

    print = stdscr.addstr

def debug(s):
    print(type(s).__name__ + ': ' + str(s) + '\t')
    return s

try:
    # Initialize pygame
    pygame.mixer.init(sampleRate, 32, channels)
    pygame.init()
    pygame.mixer.set_num_channels(pygameChannels)

    def shiftOctave(noteData, octaves):
        return pitch_shift(noteData, sr=sampleRate, n_steps=octaves * 12)

    noteNames = ['c', 'C', 'd', 'D', 'e', 'f', 'F', 'g', 'G', 'a', 'A', 'b']

    if METHOD == VARY_OCTAVES:
        # Load all the various sound files
        # None, because I want the indexes to match and I don't have an A0 file
        _a1 = librosa.load('a1.wav', sr=sr, mono=True)[0]
        _a2 = librosa.load('a2.wav', sr=sr, mono=True)[0]
        _a3 = librosa.load('a3.wav', sr=sr, mono=True)[0]
        _a4 = librosa.load('a4.wav', sr=sr, mono=True)[0]
        a = [shiftOctave(_a1, -3), shiftOctave(_a1, -2), shiftOctave(_a1, -1), _a1, _a2, _a3, _a4, shiftOctave(_a4, 1), shiftOctave(_a4, 2), shiftOctave(_a4, 3), shiftOctave(_a4, 4)]

        # Generate Notes
        notes = []
        # Capitals mean sharps
        for i in a:
            n = {}
            # They must be in THIS order
            for cnt, note in enumerate(('a', 'A', 'b', 'c', 'C', 'd', 'D', 'e', 'f', 'F', 'g', 'G')):
                n[note] = pitch_shift(i, sr=sampleRate, n_steps=cnt)
            n['B'] = n['c']
            n['E'] = n['f']
            notes.append(n)
    elif METHOD == VARY_NONE:
        a = librosa.load(varyNoneFile, sr=sr, mono=True)[0]
        notes = {}
        # They must be in THIS order
        for cnt, note in enumerate(('a', 'A', 'b', 'c', 'C', 'd', 'D', 'e', 'f', 'F', 'g', 'G')):
            notes[note] = pitch_shift(a, sr=sampleRate, n_steps=cnt)
        notes['B'] = notes['c']
        notes['E'] = notes['f']

    def changeTime(noteData, seconds):
        # print(round(seconds, 2))
        seconds *= TIME_MULTIPLIER
        return time_stretch(noteData, rate=seconds / (len(noteData) / sampleRate))

    def scaleTime(noteData, counts):
        return time_stretch(noteData, rate=1/counts)

    i = -1
    def getUnusedChannel():
        global i
        i += 1
        if i >= pygameChannels:
            i = 0
        return i


    ########################## The actual code ##########################

    def midi2octave(midi):
        return noteNames[midi % 12], (midi // 12) - 1

    def octave2midi(note, octave):
        if note == 'E':
            note = 'f'
        if note == 'B':
            note = 'c'
        return (octave + 1) * 12 + noteNames.index(note)

    # def changeVolume()

    def getNoteData(note:'Midi note number'):
        n, o = midi2octave(note)
        o += OCTAVE_OFFSET
        try:
            print(f'Playing {n}{o}\n')
        except:
            pass
        if METHOD == VARY_OCTAVES:
            return notes[o][n]
        elif METHOD == VARY_NONE:
            return shiftOctave(notes[n], o - varyNoneOctave)

    def playInteractiveNote(note, octave, counts=1):
        # print(str(note))
        # print(str(octave))
        if (data := notes[octave].get(note, None)) is not None:
            Channel(getUnusedChannel()).play(pygame.sndarray.make_sound(
                scaleTime(getNoteData(octave2midi(note, octave)), counts)
            ))

        if note == 'q':
            # Exit, but do the finally stuff first
            raise Exception()
        elif note not in noteNames:
            stdscr.clear()
            stdscr.addstr(f'{key} is not a note\n')


    def playMidiNote(note, ticks_per_beat, tempo):
        # Don't allow super short notes
        if note.time > SHORT_NOTE_CUTOFF:
            Channel(getUnusedChannel()).play(pygame.sndarray.make_sound(
                changeTime(getNoteData(note.note), mido.tick2second(note.time, ticks_per_beat, tempo))
            ))


    if INTERACTIVE:
        # Play the sound by writing the audio data to the stream
        octave = 7
        while True:
            key = stdscr.getkey()

            try:
                # octave = key
                octave = int(key)
            except ValueError:
                playInteractiveNote(key, octave)
    else:
        # Default (in microseconds)
        tempo = 500000
        # for note in mid.play(True):
        for note in TRACK:
            try:
                note.type
            except:
                pass
            else:
                if note.type == 'set_tempo':
                    tempo = note.tempo
                if note.type == 'note_on' or (note.type == 'note_off' and USE_NOTE_OFFS):
                    playMidiNote(note, MIDI.ticks_per_beat, tempo)

            time.sleep(mido.tick2second(note.time, MIDI.ticks_per_beat, tempo))



    #####################################################################

finally:
    if INTERACTIVE:
        # Close curses
        curses.nocbreak()
        stdscr.keypad(False)
        curses.echo()
        curses.endwin()
