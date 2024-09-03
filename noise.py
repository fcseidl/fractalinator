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


def kernelfilter(ker, eps=1e-2):
    # find distance at which correlation is below eps
    rmin, rmax = 2, 3
    while ker(rmax) > eps:
        rmin = rmax
        rmax *= 2
    while rmax - rmin > 1:
        rmid = int((rmin + rmax) * .5)
        if ker(rmid) > eps:
            rmin = rmid
        else:
            rmax = rmid
    # create convolution filter
    d2 = d2fromcenter((2 * rmax, 2 * rmax))
    return ker(d2)[1:, 1:]


class RBF:
    def __init__(self,s2):
        self.gamma = 0.5 / s2
    def __call__(self, d2):
        return np.exp(-d2 * self.gamma)


def convolve2d(A, B):
    """
    Convolve matrices using FFTs. Based on answer at
    https://stackoverflow.com/questions/43086557/convolve2d-just-by-using-numpy
    """
    # check for filter as big as image
    a1, a2 = A.shape
    b1, b2 = B.shape
    if b1 > a1 and b2 > a2:
        raise Warning("Convolution filter is larger than image.")

    fa = fft2(A)
    fb = fft2(np.flipud(np.fliplr(B)), s=A.shape)
    m, n = B.shape
    result = np.real(ifft2(fa * fb))
    result = np.roll(result, int(-m / 2 + 1), axis=0)
    result = np.roll(result, int(-n / 2 + 1), axis=1)
    return result


def noise(shape: tuple, s2: float, seed: int = 0) -> np.ndarray:
    np.random.seed(seed)
    white = np.random.randn(*shape)
    ker = RBF(s2)
    filt = kernelfilter(ker)
    filt = filt / filt.sum()
    return convolve2d(white, filt)


def unit_noise(**kwargs) -> np.ndarray:
    if "seed" not in kwargs.keys():
        kwargs["seed"] = 0
    real = noise(**kwargs)
    kwargs["seed"] += 22
    imag = noise(**kwargs)
    angle = np.arctan2(real, imag)
    return np.exp(angle * 1j)

