
import numpy as np
from sklearn.neighbors import NearestNeighbors
from perlin_noise import PerlinNoise


class Halo:

    def __init__(self, shape: np.ndarray, tightness=1, noise_scale=1e-2, noise_octaves=5, noise_seed=0):
        # store real and imaginary parts separately to comply with NearestNeighbors
        self._real_shape = np.array([shape.real, shape.imag]).T
        self._nearest = NearestNeighbors(n_neighbors=1).fit(self._real_shape)
        self._tight = tightness
        self._ns = noise_scale
        #self._re_noise = PerlinNoise(octaves=noise_octaves, seed=noise_seed)
        #self._im_noise = PerlinNoise(octaves=noise_octaves, seed=noise_seed + 1)

    def __call__(self, z: np.ndarray) -> np.ndarray:
        # must flatten and convert to (real, imag) to comply with NearestNeighbors
        flat_z = z.reshape(-1)
        real_flat_z = np.array([flat_z.real, flat_z.imag]).T
        neigh_ind = self._nearest.kneighbors(real_flat_z, return_distance=False)[:, 0]
        neigh = self._real_shape[neigh_ind]
        real_flat_h = real_flat_z - neigh
        flat_h = real_flat_h[:, 0] + real_flat_h[:, 1] * 1j
        return self._tight * flat_h.reshape(z.shape)


