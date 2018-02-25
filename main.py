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

print ("Setting up the connection to the board ")
it = util.Iterator(board)
it.start()

PINS = (0, 1, 2, 3)

for pin in PINS:
    board.analog[pin].enable_reporting()

def get_microphone_level():
    """
    source: http://stackoverflow.com/questions/26478315/getting-volume-levels-from-pyaudio-for-use-in-arduino
    audioop.max alternative to audioop.rms
    """
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
    #global i
    #aa = 1
    lifo_queue = queue.LifoQueue(10)
    for i in range(10):
        lifo_queue.put(board.analog[2].read())
    levels = np.zeros(100)
    i = 50
    while True:
        data = s.read(chunk)
        mx = audioop.rms(data, 4)
        #print ("Pin %i : %s" % (pin, board.analog[pin].read()))
        #mx =  board.analog[0].read()
        levels[i] = board.analog[2].read()
        i = i + 1
        lifo_queue.get()
        lifo_queue.put(board.analog[2].read())
        aa = np.average(lifo_queue.queue)
        print(aa)
        #lifo_queue.put(Levels[i])
        if i == 99:
            i = 0
            #fa = np.fft.fft(levels)
            #print(lifo_queue)
        #if i <= 10:
        #    aa = np.average(levels[i-1:i])
            #print(lifo_queue.get())
            #lifo_queue.put = board.analog[2].read()
            #print(lifo_queue.get())
        # else:
        #     lifo_queue.get()
        #     lifo_queue.put = board.analog[2].read()
        #aa = levels[i]



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
        #self.plot.points = [(i, j) for i, j in enumerate(levels)]
        self.plot.points = [(i, j * 300 ) for i, j in enumerate(levels)]
        #b = np.asarray(self.plot.points)
        #aa = np.average(b[1])
        #print(np.average(levels[i])*300)
        self.BPM  = int(aa*300)
        #print(self.plot.points[:])
        #print(np.average(self.plot.points))

        #    self.plot.points[i] = [(i, j * 300)]
        # print(levels)
        #print(self.plot.points)
        #print(aa)
        #self.plot.points = [(x,x) for x in range(0, 101)]
        #print(levels)


class RealTimeMicrophone(App):
    def build(self):
        return Builder.load_file("look.kv")

if __name__ == "__main__":
    levels = []  # store levels of microphone
    get_level_thread = Thread(target = get_microphone_level)
    get_level_thread.daemon = True
    get_level_thread.start()
    RealTimeMicrophone().run()
    board.exit()
