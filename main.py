
from mandelbrot import Fractal
from viewer import Viewer
from halo import Halo

import matplotlib.pyplot as plt


if __name__ == '__main__':
    # example with straight line
    if 1:
        import numpy as np
        np.random.seed(0)

        n = 200
        x = np.linspace(-1, 1, n, dtype=complex)
        halo = Halo(x, tightness=2, noise_octaves=1)

    fract = Fractal(k=3)#, julia_param=-.618)
    view = Viewer(fract, input_transform=halo, pixels_per_unit=100)
    img = view.image()
    plt.imshow(img)
    plt.axis('off')
    plt.show()
