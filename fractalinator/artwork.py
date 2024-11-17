
import numpy as np
from matplotlib import colormaps

from fractalinator.util import unit_noise, d2fromcenter


class Artwork:
    """
    An Artwork object maintains the raw image layers of a fractalination.
    Keyword arguments include:

    :param bailout_radius: Escape threshold for iterative fractal generation. Values near
        or below 2 may allow the noise field to affect the background image. Default = 3.00.
    :param brush_strength: Larger values give thicker strokes. Default = 50.0.
    :param brush_radius: May need to be increased to avoid choppy images with
        higher brush strength. Larger values slow drawing. Default = 100.
    :param cmap_name: matplotlib colormap name to use in image. Default = 'gray_r'.
    :param cmap_period: Smaller values make the colormap repeat more frequently around the
        outside of the fractal. Default = 4.0.
    :param max_it: maximum iteration count for iterative fractal generation. Smaller
        values speed computation but reduce image quality. Default = 30.
    :param noise_seed: If positive integer, random seed for reproducible noise. Default = None.
    :param noise_sig: Smaller values result in more, smaller features in the image. Default = 26.0.
    :param power: Multibrot fractal order. Default is 3. Must be a positive integer.
    :param shape: (width, height) of drawing window in pixels. Note that large windows may exhibit
        perceptible lag when drawing. Default = (720, 576).
    :param thin_it: Only iterate pixels to max_it if they are not diverged by this iteration,
        saving computation costs. Default = 5.
    """
    def __init__(self, *,
                 bailout_radius=3.0,
                 brush_strength=50.0,
                 brush_radius=100,
                 cmap_name='gray_r',
                 cmap_period=4.0,
                 max_it=30,
                 noise_seed=None,
                 noise_sig=26.0,
                 power=3,
                 shape=(720, 576),
                 thin_it=5):
        self.w, self.h, = shape
        self.buffer, self.power, self.mpl_cmap, self.period, self.bailout_radius, self.thin_it, self.max_it \
            = brush_radius, power, colormaps[cmap_name], cmap_period, bailout_radius, thin_it, max_it

        # set up brush
        d2 = d2fromcenter((2 * self.buffer + 1, 2 * self.buffer + 1))
        self.brush = brush_strength / (d2 + 1e-7)  # Laplace smoothed
        d2max = d2.max() / 2
        self.brush[d2 > d2max] = 0

        # create buffered layers in numpy
        buffered_shape = (2 * brush_radius + self.h, 2 * brush_radius + self.w)
        self.buffered_unit = np.zeros(buffered_shape, dtype=complex)
        self.buffered_intensity = np.zeros(buffered_shape)
        self.buffered_rgb = np.zeros(buffered_shape + (3,), dtype=np.uint8)

        # unbuffered layers
        sl = 2 * (slice(self.buffer, -self.buffer),)
        self.unit = self.buffered_unit[sl]
        self.intensity = self.buffered_intensity[sl]
        self.rgb = self.buffered_rgb[sl]

        # initialize layers
        self.unit += unit_noise(shape=(self.h, self.w), resolution=1, rbf_sigma=noise_sig, seed=noise_seed)
        self.rgb += self.z2rgb(self.bailout_radius * self.unit)

    def t2rgb(self, t):
        """Maps from (smoothed) escape times to rgb space."""
        t = np.maximum(t - 1, 0)    # ensures outside starts at 0 on cmap
        s = (t % self.period) / self.period
        i = (t / self.period).astype(int)   # how many cycles
        reverse = (i % 2) == 1
        s[reverse] = 1. - s[reverse]
        return (255 * self.mpl_cmap(s)[:, :, :3]).astype(np.uint8)

    def i2m(self, i):
        """Map paint intensity to modulus."""
        m = np.sqrt((1 / (i + 1e-7)))
        m = np.minimum(m, self.bailout_radius)
        return m

    def z2rgb(self, z0, max_it=None):
        """Map values in the complex plane to fractal image colors."""
        if max_it is None:
            max_it = self.max_it

        zn = z0
        t = -1 * np.ones(z0.shape)          # will contain smooth escape time

        for it in range(min(max_it, self.thin_it)):
            azn = np.abs(zn)
            escaped = (azn > self.bailout_radius + 1e-6) & (t < 0)  # 1e-6 prevents dots w small bailout rad
            t[escaped] = it + np.exp(1 - azn[escaped] / self.bailout_radius)
            zn[t >= 0] = 0     # prevent overflow warning
            zn = zn ** self.power + z0

        # avoid redundant computation for early escaped points
        ind = (t < 0) * (azn <= self.bailout_radius)  # not yet escaped
        zn, z0, t_, = zn[ind], z0[ind], t[ind]

        for it in range(self.thin_it, max_it):
            azn = np.abs(zn)
            escaped = (azn > self.bailout_radius + 1e-6) & (t_ < 0)
            t_[escaped] = it + np.exp(self.bailout_radius - azn[escaped])
            zn[t_ >= 0] = 0     # prevent overflow warning
            if it < self.max_it - 1:
                zn = zn ** self.power + z0

        t[ind] = t_
        interior = (t < 0)
        result = self.t2rgb(t)
        result[interior] = 0
        return result

    def paint_stroke(self, u, v):
        """Paint at a location."""
        # check boundaries
        if u < 0 or v < 0 or u >= self.w or v >= self.h:
            return

        # update intensity
        sl = (slice(v, v + 2 * self.buffer + 1), slice(u, u + 2 * self.buffer + 1))
        new_intensity = self.buffered_intensity[sl]
        new_intensity += self.brush

        # update rgb
        new_z = self.i2m(new_intensity).astype(complex) * self.buffered_unit[sl]
        self.buffered_rgb[sl] = self.z2rgb(new_z)

