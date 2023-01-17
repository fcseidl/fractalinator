
import numpy as np
from PIL import Image


def guides_from_image(imagefile, threshold=128):
    """
    Given a file name for an image, threshold the image into light/dark, and
    return the complex coordinates for the dark points as guides for a Halo.
    Also return top left and bottom right corners of the viewing window in
    the complex plane.
    """
    image = Image.open(imagefile)
    image = np.asarray(image)[:, :, :3].sum(axis=2)
    guide_vu = np.argwhere(image < threshold)
    guide_u = guide_vu[:, 1]    # png format is transposed relative to numpy
    guide_v = guide_vu[:, 0]
    # window is centered at origin with image aspect ratio and volume 8
    v_max, u_max = image.shape
    h = np.sqrt(8 * v_max / u_max)
    w = 8 / h
    topleft = 0.5 * (-w + h * 1j)
    bottomright = 0.5 * (w - h * 1j)
    # convert pixels to complex plane
    re = w * (guide_u / u_max) - w / 2
    im = -h * (guide_v / v_max) + h / 2
    guides = re + im * 1j
    return guides, topleft, bottomright


