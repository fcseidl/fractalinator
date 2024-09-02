from numpy.fft import fft2, ifft2
import numpy as np


def d2fromcenter(shape):
    """
    Create an array of the requested shape where each index holds its squared
    distance from the center index.
    """
    grid = np.ogrid[*(slice(0, s) for s in shape)]
    return sum((g - s/2)**2 for g, s in zip(grid, shape))


def circlemask(r):
    """Return a 2r by 2r array of False with a centered circle of True inscribed inside."""
    d = d2fromcenter((2 * r + 1, 2 * r + 1))
    return (d < r * r)[1:, 1:]


def convolve2d(A, B):
    """
    Convolve matrices using FFTs. Based on answer at
    https://stackoverflow.com/questions/43086557/convolve2d-just-by-using-numpy
    """
    fa = fft2(A)
    fb = fft2(np.flipud(np.fliplr(B)), s=A.shape)
    m, n = B.shape
    result = np.real(ifft2(fa * fb))
    result = np.roll(result, int(-m / 2 + 1), axis=0)
    result = np.roll(result, int(-n / 2 + 1), axis=1)
    return result


def noise(shape: tuple, radius: float, seed: int = 0) -> np.ndarray:
    np.random.seed(seed)
    white = np.random.randn(*shape)
    filt = circlemask(radius)
    filt = filt / filt.sum()
    return convolve2d(white, filt)
