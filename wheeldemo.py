import tkinter as tk
import numpy as np
from matplotlib.colors import hsv_to_rgb

from noise import noise
from brush import Brush


width = 640
height = 480
buffer = 200
seed = 42


def colorwheel(z):
    """Convert from complex plane into rgb space according to color wheel centered at zero."""
    z = z.astype(np.complex64)      # 32-bit for speedup
    h = np.arctan2(z.real, z.imag) + np.pi
    h /= 2 * np.pi
    s = np.tanh(z.real**2 + z.imag**2)
    v = np.ones_like(h)
    hsv = np.dstack((h, s, v))
    return hsv_to_rgb(hsv) * 255


# obtain random smooth field of complex units
rad = (width + height) / 20
real = noise((height, width), rad, seed=seed)
imag = noise((height, width), rad, seed=seed + 22)
angle = np.arctan2(real, imag)
unit = np.exp(angle * 1j)
buffered_unit = np.zeros((2 * buffer + height, 2 * buffer + width), dtype=complex)
buffered_unit[buffer:-buffer, buffer:-buffer] = unit


def wheelpaint(u, v, raw):
    a, b = raw.shape
    splayed = raw * buffered_unit[u:u + a, v:v + b]
    return colorwheel(splayed)


root = tk.Tk()
Brush(root, 255 * np.ones((height, width, 3)), spread=100, buffer=100, paint=wheelpaint)
root.mainloop()
