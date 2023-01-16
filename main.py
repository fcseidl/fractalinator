
from mandelbrot import Fractal
from viewer import Viewer
from halo import Halo

import matplotlib.pyplot as plt


if __name__ == '__main__':
    # example with straight line
    if 1:
        import numpy as np

        n = 2
        x = np.linspace(-1, 1, n, dtype=complex)
        halo = Halo(x, tightness=0.5)

    fract = Fractal(k=5)
    view = Viewer(fract, input_transform=halo, pixels_per_unit=200)
    img = view.image()
    plt.imshow(img)
    plt.axis('off')
    plt.show()
