
from mandelbrot import KBrot
from viewer import Viewer
from halo import Halo

import matplotlib.pyplot as plt


if __name__ == '__main__':
    # example with straight line
    if 1:
        import numpy as np

        n = 50
        x = np.linspace(-1, 1, n, dtype=complex)
        halo = Halo(x, smoothness=0.7, tightness=1.5, octaves=1.5, seed=1)

    fract = KBrot(k=2)#, julia_param=-.618)
    view = Viewer(fract, input_transform=halo, pixels_per_unit=100)
    img = view.image()
    plt.imshow(img)
    plt.axis('off')
    plt.show()
