import os, sys

import myo
from myo.utils import TimeInterval

import pygame
import pygame.display
from pygame.locals import *
from pygame._sdl2 import Window, Texture, Image, Renderer, get_drivers, messagebox

import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('TkAgg')
matplotlib.use('module://pygame_matplotlib.backend_pygame')

import numpy as np

from collections import deque
from threading import Lock, Thread

from flask import Flask
from flask import request, render_template, jsonify, redirect, url_for
from flask import Response

sys.path.append("./libs") #Project base-folder: Armband-Gesture-Toolkit
from pygameDisplay import showResult
import methods_filter, methods_feature, methods_model

######## DATA COLLECTION SETTINGS ########
participant_name = "P0"
number_of_trials = 5
target_gestures = ['none', 'pinch', 'press']

enable_experiment = False
isTraining = True
save_result = True
save_folder = "TrainingData"
save_trained_folder = "TrainedModel"
save_plot_figure = True
######## DATA COLLECTION SETTINGS END ########

######## DISPLAY SIZING ########
px = 1/plt.rcParams['figure.dpi']
surface_width = 600
surface_height = 400
surface_background = (200,200,200,255)
window_width = surface_width * 2
window_height = surface_height
######## DISPLAY SIZING END ########

######## FLASK ########
app = Flask(__name__)
app.config.update(
    ENV = 'development',
    DEBUG = True,
    TESTING = True
)

######## FLASK END ########

class Listener(myo.DeviceListener):
    def __init__(self):
        self.interval = TimeInterval(None, 0.1)
        self.emg = None
        self.orientation = None
        self.acceleration = None
        self.gyroscope = None

    def on_connected(self, event):
        print("Hello, {}!".format(event.device_name))
        event.device.vibrate(myo.VibrationType.short)
        event.device.stream_emg(True)

    def on_emg(self, event):
        # print(event.emg)
        self.emg = event.emg
        self.output()

    def output(self):
        if not self.interval.check_and_reset():
            return

        parts = []        
        if self.emg:
            for comp in self.emg:
                parts.append(str(comp).ljust(5))
        print('\r' + ''.join('[{}]'.format(p) for p in parts), end='')
        sys.stdout.flush()
        #return ''.join('[{}]'.format(p) for p in parts)
        

class EMGListener(myo.DeviceListener):
    ### Collects EMG data in a queue with *n* maximum number of elements
    def __init__(self, n):
        self.n = n
        self.lock = Lock()
        self.emg_data_queue = deque(maxlen=n)

    def get_emg_data(self):
        with self.lock:
            return list(self.emg_data_queue)
    
    def on_connected(self, event):
        event.device.stream_emg(True)

    def on_emg(self, event):
        with self.lock:
            self.emg_data_queue.append((event.timestamp, event.emg))


class EMGPlot(object):
    def __init__(self, emg_listener):
        self.n = emg_listener.n
        self.emg_listener = emg_listener
        ## figure setup
        self.fig = plt.figure(figsize=(surface_width*px, surface_height*px))
        self.axes = [self.fig.add_subplot(810+i) for i in range(1, 9)]
        [(ax.set_ylim([-100, 100])) for ax in self.axes]
        self.graphs = [ax.plot(np.arange(self.n), np.zeros(self.n))[0] for ax in self.axes]
        ## initial draw
        plt.ion()
        self.fig.canvas.draw()
        
    def update_plot(self):
        law_emg_data = self.emg_listener.get_emg_data()
        ## format emg data
        emg_data = np.array([x[1] for x in law_emg_data]).T
        for g, data in zip(self.graphs, emg_data):
            if len(data) < self.n:
                # Fill the left side with zeroes.
                data = np.concatenate([np.zeros(self.n - len(data)), data])
            g.set_ydata(data)
        ## draw on pygame display
        self.fig.canvas.draw()
        self.screen.blit(self.fig, (surface_width, 0))
        pygame.display.update()
        # plt.pause(1.0/30) < somehow breaks pygame display

    def init_pygame(self):
        self.screen = pygame.display.set_mode((window_width, window_height))
        self.screen.blit(self.fig, (surface_width, 0))

        self.surface = pygame.Surface((surface_width, surface_height), pygame.SRCALPHA)
        self.surface.fill(surface_background)
        self.screen.blit(self.surface, (0, 0))

    def main(self):
        self.init_pygame()
        show = True
        while show:
            self.update_plot()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    show = False
                    pygame.quit()

#### MAIN ####
@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/plot-myo')
def plot_myo():
    pygame.init()

    global myoHub, myoListener
    try:
        myo.init(sdk_path='./libs/myo-sdk-win-0.9.0/')
        myoHub = myo.Hub()
        myoListener = EMGListener(512)
    except Exception as e:
        return 'No Myo?'

    with myoHub.run_in_background(myoListener.on_event):
        EMGPlot(myoListener).main()
    
    return 'Pygame ended'

# call the 'run' method
if __name__ == '__main__':
    url = "http://127.0.0.1:5000"    
    app.run()