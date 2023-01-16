
from mandelbrot import Fractal
from viewer import Viewer
import matplotlib.pyplot as plt


if __name__ == '__main__':
    # sloppy transform
    if 1:
        import numpy as np
        from scipy.interpolate import lagrange

        np.random.seed(1)

        n = 10
        #x = 4 * (np.random.rand(n) + np.random.rand(n) * 1j - 0.5 - 0.5j)
        x = np.linspace(-1.5, 1.5, n)
        y = np.zeros(n)
        y[0] = 500
        poly = lagrange(x, y)

    # less sloppy try to fit random walk curves
    if 0:
        from polynomial import GuidedContours
        import numpy as np
        np.random.seed(0)

        n = 4
        sig = 1e-1
        x = [0+0j]
        x = np.linspace(-1.5, 1.5, n)
        gc = GuidedContours(degree=4).fit(x)
        poly = lambda z: 10 * gc(z)

    fract = Fractal(k=2)
    view = Viewer(fract, input_transform=poly, pixels_per_unit=200)
    img = view.image()
    plt.imshow(img)
    plt.axis('off')
    plt.show()
