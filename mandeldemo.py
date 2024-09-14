import numpy as np
from artwork import Artwork


niter = 80

def paint(z0):
    # compute escape time map
    zn = z0
    fun = lambda z: z * z * z + z0
    smooth = np.zeros(z0.shape)
    for it in range(0, niter):
        azn = np.abs(zn)
        escaped = (azn > 2.) & (smooth == 0.)
        smooth[escaped] = it + np.exp(2 - azn[escaped])
        zn[escaped] = 0.  # avoids overflow
        zn = fun(zn)
    # assign colors to lemniscates
    greyscale = 255 * (smooth / niter) ** 0.5
    return np.dstack((greyscale, greyscale, greyscale))


w, h = (1000, 1000)

Artwork(
    width=w,
    height=h,
    brush_strength=60,
    buffer=100,
    paint=paint,
    noise_sig=30,
    noise_seed=24
)
