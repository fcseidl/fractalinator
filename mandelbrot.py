
import numpy as np


black = np.array([0, 0, 0])
white = np.array([1, 1, 1])
red = np.array([1, 0, 0])
purple = np.array([1, 0, 1])

# linearly interpolates between white and red over N steps.
N = 10
default_cycle = np.array([
    white * (1 - n / N) + purple * (n / N)
    for n in range(N + 1)
])


class Fractal:
    """
    This class represents a k-brot set or one of its corresponding filled Julia sets for visualization.
    The z2rgb() function maps complex numbers to rgb pixel values according to a color scheme designed
    to depict the fractal's interior and its lemniscates.

    Parameters
    ----------
    k: degree of the iterated polynomial map, default is 2.
    maxiter: number of iterations to test for divergence, default is 100.
    color_cycle: a point whose orbit diverges after n iterations is colored by color_cycle[n % len(colorcycle)].
                    Default color cycle linearly interpolates between two pretty colors.
    julia_param: If this parameter is a point in the complex plane, then this object visualizes the Julia set
                    corresponding to that point. Otherwise, it visualizes a k-brot set.
    """

    _NOT_ESCAPED = -1

    def __init__(self, k=2, maxiter=100, color_cycle=default_cycle, julia_param=None):
        self._k = k
        self._maxiter = maxiter
        self._cycle = color_cycle
        self._period = len(color_cycle)
        self._jp = julia_param

    '''def _escape_time_point(self, z0: complex) -> int:
        map = lambda z: z ** self._k + z0
        zn = z0
        for it in range(self._maxiter):
            if np.abs(zn) > 2:
                return it
            zn = map(zn)
        return self._NOT_ESCAPED'''

    # TODO: suppress overflow warnings from exploding orbits
    def _escape_time(self, z0: np.ndarray) -> np.ndarray:
        if self._jp is None:
            map = lambda z: z ** self._k + z0
        else:
            map = lambda z: z ** self._k + self._jp
        zn = z0
        times = self._NOT_ESCAPED * np.ones_like(zn, dtype=int)
        for it in range(self._maxiter):
            times[(np.abs(zn) > 2) * (times == self._NOT_ESCAPED)] = it
            zn = map(zn)
        return times

    def z2rgb(self, z: np.ndarray) -> np.ndarray:
        """Map complex numbers to the colors corresponding to their escape times."""
        times = self._escape_time(z)
        modded_times = times % self._period
        result = np.zeros(z.shape + (3,))
        for idx in range(self._period):
            result[modded_times == idx] = self._cycle[idx]
        result[times == self._NOT_ESCAPED] = black
        return result


