import os, sys
import myo

from myo.utils import TimeInterval

from flask import Flask
from flask import request, render_template, jsonify, redirect, url_for
from flask import Response
import json

app = Flask(__name__)

sys.path.append("./libs") #Project base-folder: Armband-Gesture-Toolkit
from sensorUDP import imus_UDP
import JinsSocket
from NoseExperiment_clean import Experiment
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
####


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
        


#### MAIN ####
@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/myo-init')
def myo_data():
    # def init_myo():
    #     myo.init(sdk_path='./myo-sdk-win-0.9.0/')
    #     global myoHub, myoListener
    #     myoHub = myo.Hub()
    #     myoListener = Listener()
    def get_myo_data():
        myo.init(sdk_path='./libs/myo-sdk-win-0.9.0/')
        global myoHub, myoListener
        myoHub = myo.Hub()
        myoListener = Listener()
        while myoHub.run(myoListener.on_event, 500):
            pass
        
    # init_myo()
    # get_myo_data()
    return Response(get_myo_data(), mimetype='text/event-stream')

# call the 'run' method
if __name__ == '__main__':
    url = "http://127.0.0.1:5000"    
    app.run()