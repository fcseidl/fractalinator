from numpy.fft import rfftn, irfftn
import numpy as np


def upsample(a, sf: int):
    """
    Smoothly upsample a 2D array by an integer scale factor using
    bilinear interpolation.
    """
    u, v = a.shape
    b = np.zeros((u + 1, v + 1), dtype=a.dtype)
    b[:u, :v] = a
    b00, b01, b10, b11 = b[:-1, :-1], b[:-1, 1:], b[1:, :-1], b[1:, 1:]
    u, v = sf * np.array(a.shape)
    result = np.zeros((u, v), dtype=a.dtype)
    for i in range(sf):
        for j in range(sf):
            x, y = i / sf, j / sf
            w00 = (1 - x) * (1 - y)
            w01 = (1 - x) * y
            w10 = x * (1 - y)
            w11 = x * y
            interp = w00 * b00 + w01 * b01 + w10 * b10 + w11 * b11
            result[i:u:sf, j:v:sf] = interp
    return result[:1 - sf, :1 - sf]


def d2fromcenter(shape, resolution=1):
    """
    Create an array of the requested shape where each index holds its squared
    distance from the center index, if the number of grid cells per unit is given
    by the resolution.
    """
    # latest syntax is clean for any dimension
    # grid = np.ogrid[*(slice(0, s) for s in shape), ]
    # TODO: 3.8 doesn't like the above so we assume 2d
    s1, s2 = shape
    grid = np.ogrid[0:s1, 0:s2]
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
    return smooth[:shape[0], :shape[1]]
    # old pythons don't like the elegant line below
    # return smooth[*(slice(0, sj) for sj in shape), ]


def unit_noise(**kwargs) -> np.ndarray:
    """
    Create a field of spatially correlated complex unit noise. Keyword arguments are used
    as in noise().
    """
    if "seed" not in kwargs.keys() or kwargs["seed"] is None:
        kwargs["seed"] = 0
    real = noise(**kwargs)
    kwargs["seed"] += 22
    imag = noise(**kwargs)
    z = real + 1j * imag
    z /= np.abs(z)
    return z


def main():
    import matplotlib.pyplot as plt

    n = noise(
        shape=(100, 100),
        resolution=10,
        rbf_sigma=10,
        rbf_nsig=2.,
        periodic=False
    )

    n = np.roll(n, (100, 100), (0, 1))
    plt.imshow(n)
    plt.colorbar()
    plt.show()


if __name__ == "__main__":
    main()
