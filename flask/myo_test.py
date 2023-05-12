import os, sys
import myo as libmyo
import numpy as np

from myo.utils import TimeInterval
from matplotlib import pyplot as plt

class Listener(libmyo.DeviceListener):
    def __init__(self):
        self.interval = TimeInterval(None, 0.1)
        self.emg = None
        self.timestamp = None
        self.type = None

    def on_connected(self, event):
        print("Hello, {}!".format(event.device_name))
        event.device.vibrate(libmyo.VibrationType.short)
        event.device.stream_emg(True)

    def on_emg(self, event):
        self.emg = event.emg
        # self.accel = event.acceleration
        # self.gyro = event.gyroscope
        self.timestamp = event.timestamp
        self.type = 'E'
        self.output()

    def on_orientation(self, event):
        self.accel = event.acceleration
        self.gyro = event.gyroscope
        # self.emg = event.emg
        self.timestamp = event.timestamp
        self.type = 'O'
        self.output()

    def output(self):
        if not self.interval.check_and_reset():
            return

        parts = []
        parts.append(self.type)
        if self.emg:
            print([self.timestamp] + self.emg)
        #     for comp in self.emg:
        #         parts.append(str(comp).ljust(5))
        # if self.timestamp:
        #     parts.append(str(self.timestamp))
        # print('\r' + ''.join('[{}]'.format(p) for p in parts), end='')
        sys.stdout.flush()

if __name__ == '__main__':

    libmyo.init(sdk_path='./libs/myo-sdk-win-0.9.0/')
    hub = libmyo.Hub()
    listener = Listener()
    while hub.run(listener.on_event, 500):
        pass