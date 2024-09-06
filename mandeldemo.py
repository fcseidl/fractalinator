import numpy as np
from artwork import Artwork


def paint(z0):
    # compute escape time map
    #z0 = 1 / z0
    zn = z0
    fun = lambda z: z * z + z0
    time = np.zeros(z0.shape, dtype=int)
    for it in range(0, 80):
        ind = time == 0
        time[(np.abs(zn) > 2) & ind] = it
        zn[ind == False] = 0  # avoids overflow
        zn = fun(zn)
    # assign colors to lemniscates
    t = time % 5
    greyscale = np.array([0, 63, 127, 191, 255])[t]
    return np.dstack((greyscale, greyscale, greyscale))


w, h = (1000, 1000)

Artwork(
    width=w,
    height=h,
    brush_strength=80,
    buffer=90,
    paint=paint,
    noise_s2=(w + h) / 100,
    noise_seed=24
)
