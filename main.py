
import kbrot
import matplotlib.pyplot as plt


if __name__ == '__main__':
    vis = kbrot.Visualizer(k=4, pixels_per_unit=500)
    img = vis.image()
    plt.imshow(img.transpose((1, 0, 2)))
    plt.axis('off')
    plt.show()
