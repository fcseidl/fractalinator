import numpy as np
from artwork import Artwork
from matplotlib import colormaps

from time import time_ns


niter = 80
cutoff = 6
cmap_name = 'gray'

t0 = time_ns()


def paint(z0):
    global t0
    t1 = time_ns()
    print(t1 - t0)
    t0 = t1

    # compute escape time map
    zn = z0
    smooth = np.zeros(z0.shape)

    for it in range(0, cutoff):
        azn = np.abs(zn)
        escaped = (azn > 2.) & (smooth == 0.)
        smooth[escaped] = it + np.exp(2 - azn[escaped]) + 1e-8  # avoid sentinel value zero
        zn[smooth > 0.] = 0.  # avoids overflow
        zn = zn * zn * zn + z0

    ind = (smooth == 0) & (azn < 2)
    zn_, z0_, smooth_ = zn[ind], z0[ind], smooth[ind]

    for it in range(cutoff, niter):
        azn_ = np.abs(zn_)
        escaped = (azn_ > 2.) & (smooth_ == 0.)
        smooth_[escaped] = it + np.exp(2 - azn_[escaped])
        zn_[smooth_ > 0] = 0.
        if it < niter - 1:
            zn_ = zn_ * zn_ * zn_ + z0_

    smooth[ind] = smooth_

    # assign colors to lemniscates
    greyscale = (((smooth / niter) ** 0.3) * 1) % 1.
    return 255 * colormaps[cmap_name](greyscale)[:, :, :3]

w, h = (1000, 1000)

Artwork(
    width=w,
    height=h,
    brush_strength=100,
    buffer=100,
    paint=paint,
    noise_sig=30,
    noise_seed=24
)
