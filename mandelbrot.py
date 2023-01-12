
import numpy as np


black = np.array([0, 0, 0])
white = np.array([1, 1, 1])
red = np.array([1, 0, 0])

# linearly interpolates between white and red over N steps.
N = 5
default_cycle = np.array([
    white * (1 - n / N) + red * (n / N)
    for n in range(N + 1)
])


class Fractal:
    """
    # TODO: documentation
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


class Visualizer(Fractal):
    """
    Wrapper class for Fractal which creates an image of the fractal.
    Parameters include complex coordinates for the top left and
    bottom right corners of the viewing window, and the number of
    pixels per unit distance in the plane, which controls the
    resolution. Additional keyword arguments are passed to the Fractal
    constructor.
    """

    def __init__(self, topleft=-2 + 2j, bottomright=2 - 2j, pixels_per_unit=200, **kwargs):
        super().__init__(**kwargs)
        self._tl = topleft
        self._br = bottomright
        self._ppu = pixels_per_unit
        self._u_max = int(pixels_per_unit * (bottomright.real - topleft.real))
        self._v_max = int(pixels_per_unit * (topleft.imag - bottomright.imag))

    def uv2z(self, u, v):
        """Convert from pixel coordinates to complex plane."""
        re = self._tl.real + u / self._ppu
        im = self._tl.imag - v / self._ppu
        return re + im * 1j

    def image(self):
        """Return the image."""
        u_grid, v_grid = np.meshgrid(np.arange(self._u_max), np.arange(self._v_max))
        z_grid = self.uv2z(u_grid, v_grid)
        return self.z2rgb(z_grid)


