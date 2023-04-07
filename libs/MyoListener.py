import sys
import myo
import threading
import numpy as np

from myo.utils import TimeInterval

class MyoListener(myo.DeviceListener):
    # tag(1), timestamp(1), emg(8)
    # tag(1), timestamp(1), accel(3), gyro(3)
    # List
    # data = []

    cnt = 0

    def __init__(self, q):
        self.interval = TimeInterval(None, 0.01)
        self.emg = None
        self.accel = None
        self.gyro = None
        self.timestamp = None
        self.queue = q

    def on_connected(self, event):
        print("Hello, {}!".format(event.device_name))
        event.device.vibrate(myo.VibrationType.short)
        event.device.stream_emg(True)

    def on_emg(self, event):
        self.emg = event.emg
        self.timestamp = event.timestamp #microsecs
        self.putData('E')

    def on_orientation(self, event):
        self.accel = event.acceleration
        self.gyro = event.gyroscope
        self.timestamp = event.timestamp #microsecs
        self.putData('I')

    def putData(self):
        if not self.interval.check_and_reset():
            return
        data = []
        # store data in a global variable
        if self.emg:
            if not self.queue.full():
                data.append(self.timestamp)
                for comp in self.emg:
                    data.append(comp)
                for comp in self.accel:
                    data.append(comp)
                for comp in self.gyro:
                    data.append(comp)
                self.queue.put(data)

    def putData(self, label):
        if not self.interval.check_and_reset():
            return
        data = []
        data.append(label)
        data.append(self.timestamp)
        if label == 'E':
            for comp in self.emg:
                data.append(comp)
        elif label == 'I':
            for comp in self.accel:
                data.append(comp)
            for comp in self.gyro:
                data.append(comp)
        if not self.queue.full():
            self.queue.put(data)
        self.cnt += 1
        # self.OutputList(data)

    def OutputList(self, data_list):
        print('\r' + ''.join('[{}]'.format(p) for p in data_list))
        sys.stdout.flush()

    def ResetCnt(self):
        self.cnt = 0

    # a function for accessing the data from outside