import tkinter as tk
import numpy as np
from matplotlib.colors import hsv_to_rgb
from perlin_noise import PerlinNoise

from brush import Brush


width = 200
height = 120
buffer = 100


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
norm = (width + height) / 10
rnoise = PerlinNoise(octaves=1, seed=0)
inoise = PerlinNoise(octaves=1, seed=1)
x = np.arange(width) / norm + 20
y = np.arange(height) / norm + 20
x, y = np.meshgrid(x, y)
x, y = x.reshape(-1), y.reshape(-1)
theta = np.array([
    np.arctan2(rnoise([xx, yy]), inoise([xx, yy]))
    for xx, yy in zip(x, y)
]).reshape(height, width)
unit = np.exp(1j * theta)
buffered_unit = np.zeros((2 * buffer + height, 2 * buffer + width), dtype=complex)
buffered_unit[buffer:-buffer, buffer:-buffer] = unit


def wheelpaint(u, v, raw):
    a, b = raw.shape
    splayed = raw * buffered_unit[u:u + a, v:v + b]
    return colorwheel(splayed)


root = tk.Tk()
Brush(root, 255 * np.ones((height, width, 3)), spread=100, buffer=100, paint=wheelpaint)
root.mainloop()
