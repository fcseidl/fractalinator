
from mandelbrot import KBrot
from viewer import Viewer
from halo import Halo
import imageio

import matplotlib.pyplot as plt


if __name__ == '__main__':
    # example with straight line
    if 0:
        import numpy as np

        n = 50
        x = np.linspace(-1, 1, n, dtype=complex)
        halo = Halo(x, smoothness=0.7, tightness=1.5, octaves=1.5, seed=1)
        fract = KBrot(k=2)  # , julia_param=-.618)
        view = Viewer(fract, input_transform=halo, pixels_per_unit=50, topleft=-2.5+1.5j, bottomright=2.5-1.5j)
        img = view.image()
        plt.imshow(img)
        plt.axis('off')
        plt.show()

    # example with test file
    if 1:
        fract = KBrot(k=2)  # , julia_param=-.618)

        guides, tl, br = imageio.guides_from_image('love_in.png')
        halo = Halo(guides, smoothness=0.6, tightness=5, octaves=7, seed=1)
        view = Viewer(fract, input_transform=halo, pixels_per_unit=250, topleft=tl, bottomright=br)
        img = view.image()
        plt.imshow(img)
        plt.axis('off')
        plt.show()
