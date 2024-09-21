
import numpy as np
from matplotlib.colors import hsv_to_rgb

from artwork import Artwork


def colorwheel(z):
    """Convert from complex plane into rgb space according to color wheel centered at zero."""
    z = z.astype(np.complex64)      # 32-bit for speedup
    h = np.arctan2(z.real, z.imag) + np.pi
    h /= 2 * np.pi
    s = np.tanh(z.real**2 + z.imag**2)
    v = np.ones_like(h)
    hsv = np.dstack((h, s, v))
    return hsv_to_rgb(hsv) * 255


w, h = (1000, 1000)

Artwork(
    width=w,
    height=h,
    brush_strength=70,
    brush_radius=200,
    paint=colorwheel,
    noise_s2=(w + h) / 40,
    noise_seed=24
)

