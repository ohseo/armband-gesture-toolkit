
from __future__ import print_function
import collections
import myo
import time
import sys


class EmgRate(myo.DeviceListener):

  def __init__(self, n):
    super(EmgRate, self).__init__()
    self.times = collections.deque()
    self.last_time = None
    self.n = int(n)

  @property
  def rate(self):
    if not self.times:
      return 0.0
    else:
      return 1.0 / (sum(self.times) / float(self.n))

  def on_arm_synced(self, event):
    event.device.stream_emg(True)

  def on_emg(self, event):
    # t = time.clock()    ## deprecated function
    t = time.perf_counter()
    if self.last_time is not None:
      self.times.append(t - self.last_time)
      if len(self.times) > self.n:
        self.times.popleft()
    self.last_time = t


def main():
  myo.init(sdk_path='./libs/myo-sdk-win-0.9.0/')
  hub = myo.Hub()
  listener = EmgRate(n=50)
  while hub.run(listener.on_event, 500):
    print("\r\033[KEMG Rate:", listener.rate, end='')
    sys.stdout.flush()

# rate = sampling rate

if __name__ == '__main__':
  main()
