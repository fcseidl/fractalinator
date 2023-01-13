
from mandelbrot import Fractal
from viewer import Viewer
import matplotlib.pyplot as plt


if __name__ == '__main__':
    fract = Fractal()
    view = Viewer(fract)
    img = view.image()
    plt.imshow(img)
    plt.axis('off')
    plt.show()
