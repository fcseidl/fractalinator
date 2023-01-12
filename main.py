
import mandelbrot
import matplotlib.pyplot as plt


if __name__ == '__main__':
    vis = mandelbrot.Visualizer(k=2, pixels_per_unit=200, julia_param=-0.5+0.5j)
    img = vis.image()
    plt.imshow(img.transpose((1, 0, 2)))     # need transpose because imshow transposes the image
    plt.axis('off')
    plt.show()
