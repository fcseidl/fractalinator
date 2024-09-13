from numpy.fft import rfftn, irfftn, fft2, ifft2
import numpy as np


def d2fromcenter(shape, resolution):
    """
    Create an array of the requested shape where each index holds its squared
    distance from the center index, if the number of grid cells per unit is given
    by the resolution.
    """
    grid = np.ogrid[*(slice(0, s) for s in shape), ]
    return sum(((g - s/2 + 0.5) / resolution)**2 for g, s in zip(grid, shape))


def convolve(x, y):
    """Convolve matrices using FFTs."""
    # determine large enough shape
    s = np.maximum(x.shape, y.shape)
    ax = np.arange(s.shape[0])
    fx = rfftn(x, s=s, axes=ax)
    fy = rfftn(y, s=s, axes=ax)
    return irfftn(fx * fy)


def cone_filter(radius, resolution, dimension) -> np.ndarray:
    """
    Convolutional filter for cone kernel, scaled to unit sum.

    :param radius: Radius of cone.
    :param resolution: Number of grid cells per unit.
    :param dimension: Dimension of filter.
    """
    hw = int(radius * resolution)
    w = 2 * hw + 1
    shape = tuple(w for _ in range(dimension))
    d2 = d2fromcenter(shape, resolution)
    filt = (d2 < radius * radius)
    return filt / filt.sum()


def rbf_filter(sigma, nsig, resolution, dimension) -> np.ndarray:
    """
    Convolutional filter for RBF kernel, scaled to unit sum.

    :param sigma: Sigma paremeter of radial basis function. (Not squared.)
    :param nsig: Half-width of filter in units of sigma.
    :param resolution: Number of grid cells per unit.
    :param dimension: Dimension of filter.
    """
    hw = int(sigma * nsig * resolution)
    w = 2 * hw + 1
    shape = tuple(w for _ in range(dimension))
    d2 = d2fromcenter(shape, resolution)
    filt = np.exp(-d2 / (sigma * sigma))  # convolution of Gaussian is Gaussian
    return filt / filt.sum()


def noise(
        shape: float | tuple,
        resolution: int,
        cone_rad: float = None,
        rbf_sigma: float = None,
        rbf_nsig: float = 2.5,
        periodic: bool | tuple = False,
        seed: int = None
) -> np.ndarray:
    """
    Sample an isotropic Gaussian process over a box in n-dimensional space.

    :param shape: Box dimensions; shape=np.ones(d) gives a unit hypercube in d dimensions.
    :param resolution: Number of grid points in one unit of distance.
    :param cone_rad: If provided, correlation kernel is a cone with this radius.
    :param rbf_sigma: Must be provided if cone_rad is not. In this case, correlation kernel is an RBF kernel whose
                    sigma parameter (not squared) is the provided value.
    :param rbf_nsig: If RBF kernel is used, the small correlations over distances beyond rbf_nsig * rbf_s2**0.5
                        may be neglected.
    :param periodic: Whether to wrap noise around each axis, e.g. False for non-repeating noise, (True, False) for
                        2d-noise which is periodic along the first axis.
    :param seed: Random seed for replicability.
    :return: Array of shape np.multiply(resolution, shape) containing process values at sampled grid points.
    """
    if seed is not None:
        np.random.seed(seed)
    shape = (resolution * np.atleast_1d(shape)).astype(int)
    dim = len(shape)
    if type(periodic) == bool:
        periodic == (periodic for _ in shape)

    # construct kernel to convolve with
    if cone_rad is not None:
        kernel = cone_filter(cone_rad, resolution, dim)
    elif rbf_sigma is not None:
        kernel = rbf_filter(rbf_sigma, rbf_nsig, resolution, dim)
    else:
        raise ValueError("No cone_rad or rbf_sigma specified.")

    # determine shape of white noise to sample
    pad_shape = shape.copy()
    pad_shape[np.equal(periodic, False)] += kernel.shape[0] - 1

    # create noise map
    white = np.random.randn(*pad_shape)
    smooth = convolve(white, kernel)
    return smooth[*(slice(0, sj) for sj in shape), ]


def unit_noise(**kwargs) -> np.ndarray:
    if "seed" not in kwargs.keys():
        kwargs["seed"] = 0
    real = noise(**kwargs)
    kwargs["seed"] += 22
    imag = noise(**kwargs)
    angle = np.arctan2(real, imag)
    return np.exp(angle * 1j)


def main():
    import matplotlib.pyplot as plt

    n = noise(
        shape=(1, 1),
        resolution=1000,
        rbf_sigma=.1,
        rbf_nsig=2.,
        periodic=True
    )

    n = np.roll(n, (100, 100), (0, 1))
    plt.imshow(n)
    plt.colorbar()
    plt.show()


if __name__ == "__main__":
    main()
