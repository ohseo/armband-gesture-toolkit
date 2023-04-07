import os, sys
import myo as libmyo

class Listener(libmyo.DeviceListener):
    def on_paired(self, event):
        print("HELLO, {}!".format(event.device_name))
        event.device.vibrate(libmyo.VibrationType.short)
        # return super().on_paired(event)
    def on_unpaired(self, event):
        return False
        # return super().on_unpaired(event)
    def on_orientation(self, event):
        orientation = event.orientation
        acceleration = event.acceleration
        gyroscope = event.gyroscope
        print(acceleration)
        # return super().on_orientation(event)
    def on_emg_data(self, timestamp, event):
        print(event.emg)

# call the 'run' method
if __name__ == '__main__':

    libmyo.init(sdk_path='./libs/myo-sdk-win-0.9.0/')
    hub = libmyo.Hub()
    listener = Listener()
    while hub.run(listener.on_event, 500):
          # print(len(myo))
          pass

