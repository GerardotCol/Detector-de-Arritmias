"""Real time plotting of Microphone level using kivy
"""

from kivy.lang import Builder
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.garden.graph import MeshLinePlot
from kivy.clock import Clock
from threading import Thread
import audioop
import pyaudio
from math import sin
from kivy.properties import NumericProperty
from pyfirmata import Arduino, util
import numpy as np
import queue

board = Arduino('COM7')

print ("Setting up the connection to the board")
it = util.Iterator(board)
it.start()

PINS = (0, 1, 2, 3)

for pin in PINS:
    board.analog[pin].enable_reporting()

def get_level():

    chunk = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    p = pyaudio.PyAudio()
    s = p.open(format=FORMAT,
               channels=CHANNELS,
               rate=RATE,
               input=True,
               frames_per_buffer=chunk)
    global levels
    global aa
    lifo_queue = queue.LifoQueue(10)
    for i in range(10):
        lifo_queue.put(board.analog[2].read())
    levels = np.zeros(100)
    i = 50

    while True:
        data = s.read(chunk)
        mx = audioop.rms(data, 4)
        levels[i] = board.analog[2].read()
        i = i + 1
        lifo_queue.get()
        lifo_queue.put(board.analog[2].read())
        aa = np.average(lifo_queue.queue)
        print(aa)

        if i == 99:
            i = 0

class Logic(BoxLayout):

    BPM = NumericProperty(0)

    def __init__(self,):
        super(Logic, self).__init__()
        self.plot = MeshLinePlot(color=[1, 0, 0, 1])

    def start(self):
        self.ids.graph.add_plot(self.plot)
        Clock.schedule_interval(self.get_value, 0.001)


    def stop(self):
        Clock.unschedule(self.get_value)

    def get_value(self, dt):
        self.plot.points = [(i, j * 300 ) for i, j in enumerate(levels)]
        self.BPM  = int(aa*300)

class RealTimeMicrophone(App):
    def build(self):
        return Builder.load_file("look.kv")

if __name__ == "__main__":
    levels = []
    get_level_thread = Thread(target = get_level)
    get_level_thread.daemon = True
    get_level_thread.start()
    RealTimeMicrophone().run()
    board.exit()
