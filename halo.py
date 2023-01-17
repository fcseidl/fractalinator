
import numpy as np
from sklearn.neighbors import NearestNeighbors
from perlin_noise import PerlinNoise


class Halo:
    """
    This is a functor designed to be used as an input transform for a kbrot viewer.
    This creates a view where the interior of the kbrot follows a set of guide points.

    Parameters
    ----------
    shape: An array of complex numbers used as guide points.
    smoothness: float, larger values tend to shrink jagged protrusions on the boundary.
    tightness: float, larger values tend to concentrate the fractal more closely
                around the guide points.
    seed: int, must be positive, random seed for reproducability.
    octaves: float, parameter for Perlin noise. Smaller values tend to produce more
                order in the resulting image.
    """

    def __init__(
            self,
            shape: np.ndarray,
            smoothness: float = 0.7,
            tightness: float = 1.5,
            seed: int = 1,
            octaves: float = 1,
    ):
        # store real and imaginary parts separately to comply with NearestNeighbors
        self._real_shape = np.array([shape.real, shape.imag]).T
        self._nearest = NearestNeighbors(n_neighbors=1).fit(self._real_shape)
        self._smooth = smoothness
        self._tight = tightness ** smoothness
        self._noise = PerlinNoise(octaves=octaves, seed=seed)

    def __call__(self, z: np.ndarray) -> np.ndarray:
        # determine distances from shape
        # must flatten and convert to (real, imag) to comply with NearestNeighbors
        flat_z = z.reshape(-1)
        real_flat_z = np.array([flat_z.real, flat_z.imag]).T
        dist, _ = self._nearest.kneighbors(real_flat_z)
        dist = dist[:, 0] ** self._smooth
        # obtain (near-)uniform locally correlated angles
        theta = np.array([self._noise(xy) for xy in real_flat_z]) * np.pi
        # rotate distances into complex plane to obtain halo
        h = self._tight * dist * np.exp(theta * 1j)
        return h.reshape(z.shape)



