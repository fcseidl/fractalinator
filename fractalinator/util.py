from numpy.fft import fft2, ifft2
import numpy as np
from cnvlnoise import noise


def createUint8ClampedArray(rgb):
    """
    Turn an (h, w, 3)-shaped rgb image of uint8s into a
    4hw-byte rgba data array with full opacity.
    """
    h, w, _ = rgb.shape
    rgba = np.concatenate(
        (rgb, 255 * np.ones((h, w, 1), dtype=np.uint8)), axis=2
    ).reshape(-1)
    return rgba.data


def upsample(a, sf: int):
    """
    Smoothly upsample a 2D array by an integer scale factor using
    bilinear interpolation.
    """
    u, v = a.shape
    b = np.zeros((u + 1, v + 1), dtype=a.dtype)
    b[:u, :v] = a
    b00, b01, b10, b11 = b[:-1, :-1], b[:-1, 1:], b[1:, :-1], b[1:, 1:]
    u, v = sf * np.array(a.shape)
    result = np.zeros((u, v), dtype=a.dtype)
    for i in range(sf):
        for j in range(sf):
            x, y = i / sf, j / sf
            w00 = (1 - x) * (1 - y)
            w01 = (1 - x) * y
            w10 = x * (1 - y)
            w11 = x * y
            interp = w00 * b00 + w01 * b01 + w10 * b10 + w11 * b11
            result[i:u:sf, j:v:sf] = interp
    return result[:1 - sf, :1 - sf]


def unit_noise(**kwargs) -> np.ndarray:
    """
    Create a field of spatially correlated complex unit noise. Keyword arguments are used
    as in noise().
    """
    if "seed" not in kwargs.keys() or kwargs["seed"] is None:
        kwargs["seed"] = np.random.randint(1000000)
    real = noise(**kwargs)
    kwargs["seed"] += 22
    imag = noise(**kwargs)
    z = real + 1j * imag
    z /= np.abs(z)
    return z
