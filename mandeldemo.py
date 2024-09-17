import numpy as np
from artwork import Artwork
from matplotlib import colormaps


niter = 80
cmap_name = 'hsv'


def paint(z0):
    # compute escape time map
    zn = z0
    fun = lambda z: z * z * z + z0
    smooth = np.zeros(z0.shape)
    for it in range(0, niter):
        azn = np.abs(zn)
        escaped = (azn > 2.) & (smooth == 0.)
        smooth[escaped] = it + np.exp(2 - azn[escaped]) + 1e-8  # avoid sentinel value zero
        zn[smooth > 0.] = 0.  # avoids overflow
        zn = fun(zn)
    # assign colors to lemniscates
    greyscale = (((smooth / niter) ** 0.3) * 4) % 1.
    return 255 * colormaps[cmap_name](greyscale)[:, :, :3]


w, h = (1000, 1000)

Artwork(
    width=w,
    height=h,
    brush_strength=50,
    buffer=100,
    paint=paint,
    noise_sig=30,
    noise_seed=24
)
