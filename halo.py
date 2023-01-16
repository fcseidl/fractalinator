
import numpy as np
from sklearn.neighbors import NearestNeighbors
from perlin_noise import PerlinNoise


class Halo:
    """
    TODO: docstring!
    """

    def __init__(self, shape: np.ndarray, tightness=10, noise_octaves=0.2, noise_seed=0):
        # store real and imaginary parts separately to comply with NearestNeighbors
        self._real_shape = np.array([shape.real, shape.imag]).T
        self._nearest = NearestNeighbors(n_neighbors=1).fit(self._real_shape)
        self._tight = tightness
        self._noise = PerlinNoise(octaves=noise_octaves, seed=noise_seed)

    def __call__(self, z: np.ndarray) -> np.ndarray:
        # determine distances from shape
        # must flatten and convert to (real, imag) to comply with NearestNeighbors
        flat_z = z.reshape(-1)
        real_flat_z = np.array([flat_z.real, flat_z.imag]).T
        dist, _ = self._nearest.kneighbors(real_flat_z)
        dist = dist[:, 0] ** 0.7    # TODO: document this exponent which shrinks interior
        # obtain (near-)uniform locally correlated angles
        theta = np.array([self._noise(xy) for xy in real_flat_z]) * np.pi
        # rotate distances into complex plane to obtain halo
        h = self._tight * dist * np.exp(theta * 1j)
        return h.reshape(z.shape)



