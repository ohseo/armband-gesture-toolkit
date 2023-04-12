
import matplotlib
matplotlib.use('TkAgg')
matplotlib.use('module://pygame_matplotlib.backend_pygame')

from matplotlib import pyplot as plt
from collections import deque
from threading import Lock, Thread

import myo
import numpy as np

import pygame
import pygame.display
from pygame.locals import *
import time

class EmgCollector(myo.DeviceListener):
  """
  Collects EMG data in a queue with *n* maximum number of elements.
  """

  def __init__(self, n):
    self.n = n
    self.lock = Lock()
    self.emg_data_queue = deque(maxlen=n)

  def get_emg_data(self):
    with self.lock:
      return list(self.emg_data_queue)

  # myo.DeviceListener

  def on_connected(self, event):
    event.device.stream_emg(True)

  def on_emg(self, event):
    with self.lock:
      self.emg_data_queue.append((event.timestamp, event.emg))


class Plot(object):

  def __init__(self, listener):
    self.n = listener.n
    self.listener = listener
    px = 1/plt.rcParams['figure.dpi']
    self.fig = plt.figure(figsize=(600*px,400*px))
    self.axes = [self.fig.add_subplot(810+i) for i in range(1, 9)]
    [(ax.set_ylim([-100, 100])) for ax in self.axes]
    self.graphs = [ax.plot(np.arange(self.n), np.zeros(self.n))[0] for ax in self.axes]
    plt.ion()
    self.fig.canvas.draw()

  def update_plot(self):
    emg_data = self.listener.get_emg_data()
    emg_data = np.array([x[1] for x in emg_data]).T
    for g, data in zip(self.graphs, emg_data):
      if len(data) < self.n:
        # Fill the left side with zeroes.
        data = np.concatenate([np.zeros(self.n - len(data)), data])
      g.set_ydata(data)
    self.fig.canvas.draw()
    self.screen.blit(self.fig, (0, 0))
    pygame.display.update()
    # plt.pause(1.0/30) < somehow breaks pygame display

  def init_pygame(self):
    pygame.init()
    self.screen = pygame.display.set_mode((600, 400))
    self.screen.blit(self.fig, (0, 0))

  def main(self):
    self.init_pygame()
    show=True
    while show:
      self.update_plot()
      for event in pygame.event.get():
        if event.type == pygame.QUIT:
            # Stop showing when quit
            show=False
            pygame.quit()

#### https://pypi.org/project/pygame-matplotlib/

def main():
  myo.init(sdk_path='./libs/myo-sdk-win-0.9.0/')
  hub = myo.Hub()
  listener = EmgCollector(512)
  with hub.run_in_background(listener.on_event):
    Plot(listener).main()

if __name__ == '__main__':
  main()
