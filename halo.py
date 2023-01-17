
import numpy as np
from sklearn.neighbors import NearestNeighbors
from perlin_noise import PerlinNoise


class Halo:
    """
    This is a functor designed to be used as an input transform for a kbrot viewer.
    This creates a view where the interior of the kbrot follows a set of guide points.

    Parameters
    ----------
    guides:
        An array of complex numbers used as guide points.
    smoothness:
        float, larger values tend to shrink jagged protrusions on the boundary.
    tightness:
        float, larger values tend to concentrate the fractal more closely
        around the guide points.
    seed:
        int, must be positive, random seed for reproducability.
    octaves:
        float, parameter for Perlin noise. Smaller values tend to produce more
        order in the resulting image.
    """

    def __init__(
            self,
            guides: np.ndarray,
            smoothness: float = 0.7,
            tightness: float = 1.5,
            seed: int = 1,
            octaves: float = 1,
    ):
        # store real and imaginary parts separately to comply with NearestNeighbors
        self._real_guides = np.array([guides.real, guides.imag]).T
        self._nearest = NearestNeighbors(n_neighbors=1).fit(self._real_guides)
        self._smooth = smoothness
        self._tight = tightness ** smoothness
        self._x_noise = PerlinNoise(octaves=octaves, seed=seed)
        self._y_noise = PerlinNoise(octaves=octaves, seed=seed + 1)

    def __call__(self, z: np.ndarray) -> np.ndarray:
        # determine distances from guides
        # must flatten and convert to (real, imag) to comply with NearestNeighbors
        flat_z = z.reshape(-1)
        real_flat_z = np.array([flat_z.real, flat_z.imag]).T
        dist, _ = self._nearest.kneighbors(real_flat_z)
        dist = dist[:, 0] ** self._smooth
        # obtain uniform locally correlated angles
        theta = [np.arctan2(self._x_noise(xy), self._y_noise(xy)) for xy in real_flat_z]
        theta = np.array(theta)
        # rotate distances into complex plane to obtain halo
        h = self._tight * dist * np.exp(theta * 1j)
        return h.reshape(z.shape)



