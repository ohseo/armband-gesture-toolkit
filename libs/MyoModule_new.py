import time
import numpy as np
import pandas as pd

current_milli_time = lambda: int(round(time.time() * 1000))
current_milli_time_f = lambda: float(time.time() * 1000)

class Experiment:
    def __init__(self, pa_name, pa_no, gestures, level_num, trial_num):
        self.pa_name = pa_name
        self.pa_no = pa_no
        self.gestures = gestures
        self.gesture_num = len(gestures)
        self.level_num = level_num
        self.trial_num = trial_num

        self.total_trials = self.gesture_num * self.level_num * self.trial_num
        self.trial_check = self.trial_num * np.ones(self.gesture_num * level_num)
        self.start_time = current_milli_time()
        self.trial_index = -1
        self.all_trial_done = False
        self.trial_succeed = False

        self.rollbacked = False

        self.df_column = ['Timestamp', 'E1', 'E2', 'E3', 'E4', 'E5', 'E6', 'E7', 'E8']
        self.trial_df = pd.DataFrame(columns=self.df_column)

    def setDataCollection(self, display_size, time_before, time_recording):
        self.display_size = display_size
        self.pre_counter = time_before
        self.record_counter = time_recording

    def startRecording(self):
        self.current_state = 1
    def rollbackOneTrial(self):
        self.recording = False
    def checkStateChange(self):
        self.current_state = 0
    def getNewTrial(self):
        self.recording = True
    def addData(self):
        self.trial_df.at[len(self.trial_df), 0]
        self.recording = True