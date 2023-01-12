
import mandelbrot
import matplotlib.pyplot as plt


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    img = mandelbrot.Visualizer().image()
    plt.imshow(img.transpose((1, 0, 2)))
    plt.show()
