import sys
import myo
import threading
import queue
import numpy as np
from dataclasses import dataclass, field

from myo.utils import TimeInterval

sys.path.append("./libs") #Project base-folder: Armband-Gesture-Toolkit
import MyoListener

class MyoModule(threading.Thread):
    def __init__(self, saveFileName = "test", isSaving = True):
        threading.Thread.__init__(self)

        self.q = queue.Queue()
        
        """ Init Myo """
        myo.init(sdk_path='./flask/myo-sdk-win-0.9.0/')
        self.hub = myo.Hub()
        self.listener = MyoListener.MyoListener(self.q)
        
        """ Define Array """
        self.w_size = 2000      # window size

        ## RAW DATA ##
        self.IMU = np.zeros((self.w_size, 7))    # t, Accel(3), Gyro(3)
        self.EMG2 = np.zeros((self.w_size, 9))   # t, EMG(8)

        self.TimeEMG = np.zeros(self.w_size)
        self.EMG = np.zeros((8, self.w_size))
        self.TimeIMU = np.zeros(self.w_size)
        self.Acc = np.zeros((3, self.w_size))
        self.Gyro = np.zeros((3, self.w_size))

        self.mAvgNum = 100
        self.avg = []           # list of 14: EMG(8), Accel(3), Gyro(3)

        self.PAUSE_loop = False
        self.STOP_loop = False

        """Save File Setup"""
        self.saveFileEMG = open(saveFileName+"_emg.csv", "w")
        self.saveFileEMG.write("Time,EMG_1,EMG_2,EMG_3,EMG_4,EMG_5,EMG_6,EMG_7,EMG_8\n")
        self.saveFileIMU = open(saveFileName+"_imu.csv", "w")
        self.saveFileIMU.write("Time,Acc_x,Acc_y,Acc_z,Gyro_x,Gyro_y,Gyro_z\n")

    def run(self):
        while self.hub.run(self.listener.on_event, 500):
            if self.STOP_loop:
                print("Loop STOP")
                break
            print("\nflush here? " + str(self.q.qsize()) + " " + str(self.listener.cnt))
            self.listener.ResetCnt()
            self.q.queue.clear()
            # 여기서 새는 entry 생길 것 같음.
            # 굳이 threading을 할 필요가 없을 지도.

            # if not self.PAUSE_loop:
            #     while True:
            #         try:
            #             data = self.q.get() # list
            #             print("getting data")
            #         except queue.Empty as e:
            #             print("queue empty")
            #             break

            #         if len(data) == 10 and data[0] == 'E':
            #             self.addFromList(data, data[0])
            #             self.OutputList(data)
            #             # self.UpdateMovingAverage(data)
            #         elif len(data) == 8 and data[0] == 'I':
            #             self.addFromList(data, data[0])
            #             self.OutputList(data)
            #             # self.UpdateMovingAverage(data)
            #     print ("while end")
                    
    def addFromList(self, data_list, label):
        self.rollDataByOne(label)
        if label == 'E':
            # self.TimeEMG[-1] = data_list[1]
            # self.EMG[:,-1] = np.swapaxes(data_list[2:],0,1)
            self.EMG2[-1,:] = data_list[1:]
        elif label == 'I':
            # self.TimeIMU[-1] = data_list[1]
            # self.Acc[:,-1] = np.swapaxes(data_list[2:5],0,1)
            # self.Gyro[:,-1] = np.swapaxes(data_list[5:],0,1)
            self.IMU[-1,:] = data_list[1:]
    
    def rollDataByOne(self, label):
        if label == 'E':
            # self.TimeEMG = np.roll(self.TimeEMG, -1)
            # self.EMG = np.roll(self.EMG, -1, axis=1)
            self.EMG2 = np.roll(self.EMG2, -1, axis=0)
        elif label == 'I':
            # self.TimeIMU = np.roll(self.TimeIMU, -1)
            # self.Acc = np.roll(self.Acc, -1, axis=1)
            # self.Gyro = np.roll(self.Gyro, -1, axis=1)
            self.IMU = np.roll(self.IMU, -1, axis=0)

    def UpdateMovingAverage(self, data_list):
        for i, avg in enumerate(self.avg):
            avg = self.UpdateCumulativeAverage(avg, data_list[i+1])
    
    def UpdateCumulativeAverage(self, cur_avg, last_value):
        return ((self.mAvgNum * cur_avg + last_value)/(self.mAvgNum + 1))
        
    def OutputList(self, data_list):
        print('\r' + ''.join('[{}]'.format(p) for p in data_list))
        sys.stdout.flush()

if __name__ == '__main__':
    myoclient = MyoModule(saveFileName="test", isSaving=True)
    myoclient.start()

