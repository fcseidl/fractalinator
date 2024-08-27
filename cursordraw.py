import matplotlib.pyplot as plt
from matplotlib.backend_bases import MouseButton
from matplotlib.image import AxesImage

import numpy as np


fig, ax = plt.subplots()

class CursorDraw:

    def __init__(self):
        self.screen = np.zeros((5, 7))
        self.move_bind = None
        plt.connect('button_press_event', self.on_move)
        plt.connect('button_release_event', self.on_release)

    def on_move(self, event):
        if event.inaxes:
            v, u = int(event.xdata), int(event.ydata)
            self.screen[u, v] = 1

    def on_click(self, event):
        if event.button is MouseButton.LEFT:
            self.move_bind = plt.connect('motion_notify_event', on_move)

    def on_release(self, event):
        if event.button is MouseButton.LEFT:
            plt.disconnect(self.move_bind)


cd = CursorDraw()

while True:
    ax.imshow(
        cd.screen
    )
    plt.pause(0.01)

