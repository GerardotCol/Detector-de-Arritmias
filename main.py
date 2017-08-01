"""
Based on RealTimeMicrophone

source: http://stackoverflow.com/questions/26478315/getting-volume-levels-from-pyaudio-for-use-in-arduino
audioop.max alternative to audioop.rms

Real time plotting of ECG level using kivy
Created on Wed Jul 26 13:45:06 2017

The development envioroment will be

    - kivy
    - numpy
    - wfdb

    @author: Samsa
"""

from kivy.lang import Builder
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.garden.graph import MeshLinePlot
from kivy.clock import Clock
from threading import Thread  #importing the threading allows execute simultaneus
# variables

import datetime             # This add a Clock

from kivy.properties import NumericProperty, ReferenceListProperty,\
    ObjectProperty
from kivy.vector import Vector

import audioop          # For test propuses
import pyaudio          #

import matplotlib.pyplot as plt
import numpy
import wfdb

import os
import sys

## This folow lines are the serial interface with the Arduino

#THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
#f = os.path.join(THIS_FOLDER, 'sampledata/100')

# from pyfirmata import Arduino
# from pyfirmata import util
# from pyfirmata.util import Iterator
#
# board = Arduino('COM4')
#
# for a in range(0,5):
#     board.analog[a].enable_reporting()

# start an iterator thread so
# serial buffer doesn't overflow
#it = util.Iterator(board)
#it.start()

fs = 360
adcgain=200.0
adczero=1

def get_microphone_level():

    # set the microphone constants

    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    chunk = 1024  # 2^10
    p = pyaudio.PyAudio() # se instancia pyaudio

    # se agregarn las constantes al objeto
    s = p.open(format=FORMAT,
               channels=CHANNELS,
               rate=RATE,
               input=True,
               frames_per_buffer=chunk)

    global levels
    global peaks_indexes

    while True:
        data = s.read(chunk)
        mx = audioop.rms(data, 2)
        if len(levels) >= 100:
            #peaks_indexes = wfdb.processing.gqrs_detect(x=x, frequency=fs, adcgain=record.adcgain[0], adczero=record.adczero[0], threshold=1.0)
            #peaks_indexes = wfdb.processing.gqrs_detect(x=levels, frequency=fs, adcgain=200.0, adczero=1, threshold=1.0)
            #return peaks_indexes
            levels = []
            peaks_indexes = []

        levels.append(mx)

def get_qrs():
    if len(levels) >= 99:
        peaks_indexes = wfdb.processing.gqrs_detect(x=levels, frequency=fs, adcgain=200.0, adczero=1, threshold=1.0)

# def get_Arduino():
#
#     global Alevels
#     while True:
#         #mx = audioop.rms(data, 2)
#         amx = board.analog[2].read()
#         if len(Alevels) >= 100:
#             levels = []
#         Alevels.append(amx)
#
# def Umbral(nivel): #esta función tiene que detectar un umbral para mostrar
#     self.nivel = nivel
#     if nivel > 250:
#         return True
#     return False
#

class Logic(BoxLayout):

    #player1 = ObjectProperty(None)
    player1 = ObjectProperty(None)
    score = NumericProperty(0)
    peaks_indexes = NumericProperty(0)
    time = datetime.datetime.now()

    def __init__(self,):
        super(Logic, self).__init__()
        self.plot = MeshLinePlot(color=[1, 0, 0, 1])

    def start(self):
        self.ids.graph.add_plot(self.plot)
        Clock.schedule_interval(self.get_value, 0.001)

    def stop(self):
        Clock.unschedule(self.get_value)

    def record(self):
        time = datetime.datetime.now()
        self.plot.points = [(i, j/20) for i, j in enumerate(peaks_indexes)]

        #print(self.score)
        #print(self.time.second)
        print(self.peaks_indexes)


    def get_value(self, dt):
        self.plot.points = [(i, j/20) for i, j in enumerate(levels)]
        if levels[-1] > 5000:
            print(levels[-1])
            self.score += 1

        #if self.plot.points > self.plot.points:
            #self.pulse1.score += 1

class RealTimeMicrophone(App):
    def build(self):
        return Builder.load_file("look.kv")

if __name__ == "__main__":
    levels = []  # store levels of microphone
    #Alevels = [] # store Levels of Arduino
    get_level_thread = Thread(target = get_microphone_level)
    get_qrs = Thread(target = get_qrs)
    #get_level_thread2 = Thread(target = get_Arduino)
    get_level_thread.daemon = True
    get_qrs.daemon = True
    #get_level_thread2.daemon = True
    get_level_thread.start()
    get_qrs.start()
    #get_level_thread2.start()
    RealTimeMicrophone().run()
