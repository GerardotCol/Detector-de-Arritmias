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
        if i == 99:
            i = 0



class Logic(BoxLayout):

    BPM = NumericProperty(0)

    def __init__(self,):
        super(Logic, self).__init__()
        self.plot1 = MeshLinePlot(color=[1, 0, 0, 1])
        self.plot2 = MeshLinePlot(color=[0, 1, 0, 1])
        self.plot3 = MeshLinePlot(color=[0, 0, 1, 1])

    def start(self):
        self.ids.graph1.add_plot(self.plot1)
        self.ids.graph2.add_plot(self.plot2)
        self.ids.graph3.add_plot(self.plot3)
        Clock.schedule_interval(self.get_value, 0.001)

    def stop(self):
        Clock.unschedule(self.get_value)

    def get_value(self, dt):

        self.plot1.points = [(i, j * 300 ) for i, j in enumerate(levels)]
        self.plot2.points = [(i, (j*40)**3 ) for i, j in enumerate(levels)]
        #self.plot3.points = [(i, j * 300 ) for i, j in enumerate(np.asarray(levels))]
        A = np.asarray(levels)
        B = np.arange(levels.size)

        ps = np.abs(np.fft.fft(A))**2
        #print(ps.size) #100
        time_step = 1 / 30
        freqs = np.fft.fftfreq(A.size, time_step)
        self.plot3.points = np.stack((freqs,ps*2), axis=-1)

        #self.plot3.points = [B,A]
        #self.plot3.points = np.stack((B, A*300), axis=-1) #no borrar
        #self.plot3.points = np.asarray(levels)
        #self.plot3.points = np.stack((np.arange(levels.size), np.asarray(levels)), axis=-1)
        self.BPM  = int(aa*300)


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
