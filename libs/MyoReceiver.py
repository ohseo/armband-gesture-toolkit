import sys
from time import time
import myo
import numpy as np
import queue
from myo.utils import TimeInterval

sys.path.append("./libs") #Project base-folder: Armband-Gesture-Toolkit

class MyoReceiver(myo.DeviceListener):
    def __init__(self, savefile_name = "test", is_saving = True):
        
        self.interval = TimeInterval(None, 0.01)
        
        self.data_emg = None
        self.data_accel = None
        self.data_gyro = None
        self.data_timestamp = None

        self.time_zero = None          # 첫 timestamp 저장
        self.emg_count = None
        self.imu_count = None
        self.trim_index = 50
        self.emg_interval = 5000

        """ Define Array """
        self.w_size = 2000          # window size in ms

        self.imu_array = np.zeros((self.w_size, 11))     # i, t_bucket, t_raw, accel(3), gyro(3), is_dumped, is_interpolated
        self.emg_array = np.zeros((self.w_size, 11))     # i, t_bucket, t_raw, emg(8)

        self.loop_PAUSE = False
        self.loop_STOP = False

        self.q = queue.Queue()
        self.imu_q = queue.Queue()
        self.emg_q = queue.Queue()

        """ File Setup """
        # self.file_emg = open(savefile_name+"_EMG.csv", "w")
        # self.file_emg.write(",Time,Raw Time,EMG 1,EMG 2,EMG 3,EMG 4,EMG 5,EMG 6,EMG 7,EMG 8\n")

        # self.file_imu = open(savefile_name+"_IMU.csv", "w")
        # self.file_imu.write(",Time,Raw Time,ACC_X,ACC_Y,ACC_Z,GYRO_X,GYRO_Y,GYRO_Z,Is Dumped,Is Interpolated\n")

        # self.file_all = open(savefile_name+"_MYO.csv", "w")
        # self.file_all.write(",Time,EMG 1,EMG 2,EMG 3,EMG 4,EMG 5,EMG 6,EMG 7,EMG 8,ACC_X,ACC_Y,ACC_Z,GYRO_X,GYRO_Y,GYRO_Z\n")

        self.file_out = open(savefile_name+"_TEST.csv", "w")
        
    def on_connected(self, event):
        print("{} Successfully Connected".format(event.device_name))
        event.device.vibrate(myo.VibrationType.short)
        event.device.stream_emg(True)

    def on_emg(self, event):
        # self.data_emg = event.emg
        # self.data_timestamp = event.timestamp

        print(self.q.qsize())
        data = []
        data.append('E')
        data.append(self.define_emg_bucket(event.timestamp))
        if self.time_zero != None:
            data.append((event.timestamp - self.time_zero))
        else:
            data.append('')
        data.append(event.timestamp)
        for comp in event.emg:
            data.append(comp)
        if not self.q.full():
            self.q.put(data)
        self.output_list(data)
        # save to file
        
    def on_orientation(self, event):
        # self.data_accel = event.acceleration
        # self.data_gyro = event.gyroscope
        # self.data_timestamp = event.timestamp
        
        if (self.q.qsize() >= self.trim_index) & (self.emg_count == None):
            self.init_timestamp(event)

        data = []
        data.append('I')
        data.append(self.define_imu_bucket(event.timestamp))
        if self.time_zero != None:
            data.append((event.timestamp - self.time_zero))
        else:
            data.append('')
        data.append(event.timestamp)
        for comp in event.acceleration:
            data.append(comp)
        for comp in event.gyroscope:
            data.append(comp)
        if not self.q.full():
            self.q.put(data)
        self.output_list(data)
        # save to file

    def output_list(self, data_list):
        # print('\r' + ''.join('[{}]'.format(p) for p in data_list))
        # sys.stdout.flush()
        str = ''.join('{},'.format(p) for p in data_list)
        self.file_out.write(str+"\n")
        # print(self.imu_q.qsize()+self.emg_q.qsize())

    def init_timestamp(self, event):
        self.time_zero = event.timestamp
        self.emg_count = 0

    def define_emg_bucket(self, timestamp):
        if self.time_zero != None:
            # t = self.emg_count*5000
            # self.emg_count += 1
            t = timestamp - self.time_zero
            return np.round(t/self.emg_interval)
        else:
            return timestamp

    def define_imu_bucket(self, timestamp):
        if self.time_zero != None:
            t = timestamp - self.time_zero
            return np.round(t/self.emg_interval)
        else:
            return timestamp

if __name__ == '__main__':
    """ Init Myo """
    myo.init(sdk_path='./flask/myo-sdk-win-0.9.0/')
    myo_hub = myo.Hub()
    myo_listener = MyoReceiver(savefile_name="test", is_saving=True)
    while myo_hub.run(myo_listener.on_event, 500):
        pass