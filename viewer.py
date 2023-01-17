
import numpy as np

from mandelbrot import KBrot


class Viewer:
    """
    A fractal visualization class, whose image() method returns a fractal image.

    Parameters
    ----------
    fractal: a mandelbrot.KBrot instance to view.
    topleft: top left corner of viewing window in the complex plane. Default: -2+2j
    bottomright: bottom right corner of viewing window in the complex plane. Default: 2-2j
    pixels_per_unit: sets resolution so that a unit square in C contains this many pixels, squared. Default: 200
    input_transform: transformation to be applied to a pixel's complex coordinate before coloring according
                        to the fractal. Default is the identity transformation.
    """

    def __init__(
            self,
            fractal: KBrot,
            topleft: complex=-2 + 2j,
            bottomright: complex=2 - 2j,
            pixels_per_unit: int=200,
            input_transform=lambda z: z
    ):
        self._fract = fractal
        self._tl = topleft
        self._br = bottomright
        self._ppu = pixels_per_unit
        self._u_max = int(pixels_per_unit * (bottomright.real - topleft.real))
        self._v_max = int(pixels_per_unit * (topleft.imag - bottomright.imag))
        self._input_transform = input_transform

    def _uv2z(self, u, v):
        """Convert from pixel coordinates to complex plane."""
        re = self._tl.real + u / self._ppu
        im = self._tl.imag - v / self._ppu
        return re + im * 1j

    def image(self):
        """Return the image."""
        u_grid, v_grid = np.meshgrid(np.arange(self._u_max), np.arange(self._v_max))
        z_grid = self._uv2z(u_grid, v_grid)
        inputs = self._input_transform(z_grid)
        return self._fract.z2rgb(inputs)

