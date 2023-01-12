
import numpy as np


black = np.array([0, 0, 0], dtype=int)

# quadratically interpolates between blue and red over N steps.
N = 7
default_cycle = [
    np.array([0, 0, 255]) * (1 - n/N)**2 + np.array([255, 0, 0]) * (n/N)**2
    for n in range(N)
]
default_cycle = np.array(default_cycle).astype(int)


class KBrot:
    """Represents a k-brot set with lemniscates visualized in the plane."""

    NOT_ESCAPED = -1

    def __init__(self, k=2, maxiter=100, color_cycle=default_cycle):
        self._k = k
        self._maxiter = maxiter
        self._cycle = color_cycle
        self._period = len(color_cycle)

    # TODO: handle arrays
    def _escape_time(self, z0):
        map = lambda z: z ** self._k + z0
        zn = z0
        for it in range(self._maxiter):
            if np.abs(zn) > 2:
                return it
            zn = map(zn)
        return self.NOT_ESCAPED

    def z2rgb(self, z) -> np.ndarray:
        """Map a complex number to the color corresponding to its escape time."""
        t = self._escape_time(z)
        if t == self.NOT_ESCAPED:
            return black
        return self._cycle[t % self._period]


class Visualizer(KBrot):
    """Wrapper class for KBrot which creates an image of the fractal."""

    def __init__(self, topleft=-2 + 2j, bottomright=1 - 2j, pixels_per_unit=100, **kwargs):
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
        img = np.empty((self._u_max, self._v_max, 3), dtype=int)
        for u in range(self._u_max):
            for v in range(self._v_max):
                img[u, v] = self.z2rgb(self.uv2z(u, v))
        return img


