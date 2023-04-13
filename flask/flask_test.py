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
import pandas as pd

from collections import deque
from threading import Lock, Thread
from datetime import datetime

from flask import Flask
from flask import request, render_template, jsonify, redirect, url_for
from flask import Response

sys.path.append("./libs") #Project base-folder: Armband-Gesture-Toolkit

######## DATA COLLECTION SETTINGS ########
participant_name = "P0"
participant_no = 0
target_gestures = ['pinch', 'grip']
number_of_force_levels = 2
number_of_trials = 5

save_folder = "TrainingData"

time_before = 2
time_recording = 2

is_pygame_running = False
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

class EMGListener(myo.DeviceListener):
    df_column = ['T','E1', 'E2', 'E3', 'E4', 'E5', 'E6', 'E7', 'E8']
    trial_df = pd.DataFrame(columns=df_column)

    ### Collects EMG data in a queue with *n* maximum number of elements
    def __init__(self, n):
        self.n = n
        self.lock = Lock()
        self.emg_data_queue = deque(maxlen=n)
        self.emg_data = []

    def get_emg_data(self):
        with self.lock:
            return list(self.emg_data_queue)
    
    def on_connected(self, event):
        event.device.stream_emg(True)

    def on_emg(self, event):
        with self.lock:
            self.emg_data = [event.timestamp] + event.emg
            self.add_emg()
            self.emg_data_queue.append((event.timestamp, event.emg))

    def add_emg(self):
        self.trial_df.loc[len(self.trial_df), self.df_column] = self.emg_data

    def save_emg(self):
        self.trial_df.to_csv("CollectedData/test.csv")




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

        myFont = pygame.font.SysFont("notosansdisplay", 30, True, False)
        textColor = (0,0,0, 120)
        text = myFont.render("Testing", True, textColor)

        self.screen.blit(text, [200,300])

    def main(self):
        self.init_pygame()
        show = True
        while show:
            self.update_plot()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    show = False
                    pygame.quit()

                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_ESCAPE:
                        show = False
                        pygame.quit()
                    elif event.key == pygame.K_RIGHT:
                        show = True
                        self.emg_listener.save_emg()
                        ## next trial
                        

def run_pygame():

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
    # save_name_str = save_folder +"/"+ datetime.now().strftime('%Y-%m-%d %H_%M_%S')+"_"+participant_name

    #### Initialize Pygame ####

    #### Data Collection ####
    # exp = Experiment(pa_name = participant_name,
    #                  pa_no = participant_no,
    #                  gestures = target_gestures,
    #                  level_num = number_of_force_levels,
    #                  trial_num = number_of_trials)
    # exp.setDataCollection(display_size = [window_width, window_height],
    #                       time_before = time_before,
    #                       time_recording = time_recording)

    #### Pygame Event Handling ####

    #### Close Things Down ####

    #### Save Result as a File ####

#### MAIN ####
@app.route('/', methods = ['GET', 'POST'])
def hello_world():

    if request.method == 'POST':
        participant_name = request.form['input_name'].upper()
        ## participant_no
        target_gestures = [x.strip() for x in request.form["input_gesture_set"].split(',')]
        number_of_force_levels = int(request.form['input_number_of_force_level'])
        number_of_trials = int(request.form['input_number_of_gesture'])
        
        time_before = float(request.form['time-before-length'])
        time_recording = float(request.form['time-window-length'])

        if request.form['action'] == 'startGathering':
            if not is_pygame_running:
                run_pygame()

    return render_template('collecting_form.html') #, name=participant_name)

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

@app.route('/_initdata', methods=['GET'])
def info_to_html():
    print("<<stuff>>\nname:",participant_name,
          "\ntarget_gestures:",target_gestures,
          "\nnumber_of_trials:",number_of_trials)
    return jsonify(participant_name=participant_name,
                   level_numbers = number_of_force_levels,
                   trial_numbers=number_of_trials,
                   target_gestures=",".join(target_gestures),
                   time_before=time_before,
                   time_recording=time_recording)

# call the 'run' method
if __name__ == '__main__':
    url = "http://127.0.0.1:5000"    
    app.run()


