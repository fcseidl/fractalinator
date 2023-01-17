
import numpy as np


# a bunch of colors
black = np.array([0, 0, 0])
white = np.array([1, 1, 1])
red = np.array([1, 0, 0])
blue = np.array([0, 0, 1])
um_blue = np.array([0, 39, 76]) / 255
um_maize = np.array([255, 203, 0]) / 255
pink = np.array([1, 0, 1])


def interp(start, end, n=2):
    """Quadratically interpolate a cycle between two colors, with a period of length 2n."""
    there = [start * (1 - k / n) ** 0.5 + end * (k / n) ** 0.5 for k in range(n)]
    back = [end * (1 - k / n) ** 0.5 + start * (k / n) ** 0.5 for k in range(n)]
    return np.array(there + back)


default = interp(blue, red)
wolverine = interp(um_blue, um_maize)
midnight = interp(black, pink)
valentine = interp(white, pink)
zebra = interp(black, white, 1)

rainbow = np.array([
    [255, 0, 0],
    [255, 69, 0],
    [255, 255, 0],
    [0, 255, 0],
    [0, 0, 255],
    [63, 15, 183],
    [127, 0, 255]
]) / 255

cycle_dict = {
    'default': default,
    'wolverine': wolverine,
    'midnight': midnight,
    'valentine': valentine,
    'zebra': zebra,
    'rainbow': rainbow
}