
import tkinter as tk
import numpy as np
import os
from PIL import Image, ImageTk
from matplotlib import colormaps

from .noise import unit_noise, d2fromcenter


def np2image(arr):
    """Convert a numpy array into an image which can go on a tkinter canvas."""
    return ImageTk.PhotoImage(
        image=Image.fromarray(
            arr.astype(
                np.uint8)))


def upsample(a, sf: int):
    """
    Smoothly upsample a 2D array by an integer scale factor using
    bilinear interpolation.
    """
    u, v = a.shape
    b = np.zeros((u + 1, v + 1), dtype=a.dtype)
    b[:u, :v] = a
    b00, b01, b10, b11 = b[:-1, :-1], b[:-1, 1:], b[1:, :-1], b[1:, 1:]
    u, v = sf * np.array(a.shape)
    result = np.zeros((u, v), dtype=a.dtype)
    for i in range(sf):
        for j in range(sf):
            x, y = i / sf, j / sf
            w00 = (1 - x) * (1 - y)
            w01 = (1 - x) * y
            w10 = x * (1 - y)
            w11 = x * y
            interp = w00 * b00 + w01 * b01 + w10 * b10 + w11 * b11
            result[i:u:sf, j:v:sf] = interp
    return result[:1 - sf, :1 - sf]


class Artwork:
    """
    An Artwork object creates and controls a fractal drawing widget.
    Keyword arguments can be used to control the brush, color, and noise settings.
    They include:

    :param bailout_radius: Escape threshold for iterative fractal generation. Values near
        or below 2 may allow the noise field to affect the background image. Default = 3.00.
    :param brush_strength: Larger values give thicker strokes. Default = 50.0.
    :param brush_radius: May need to be increased to avoid choppy images with
        higher brush strength. Larger values slow drawing. Default = 100.
    :param cmap_name: matplotlib colormap name to use in image. Default = 'gray_r'.
    :param cmap_period: Smaller values make the colormap repeat more frequently around the
        outside of the fractal. Default = 4.0.
    :param max_it: maximum iteration count for iterative fractal generation. Smaller
        values speed computation but reduce image quality. Default = 30.
    :param noise_seed: If positive integer, random seed for reproducible noise. Default = None.
    :param noise_sig: Smaller values result in more, smaller features in the image. Default = 26.0.
    :param power: Multibrot fractal order. Default is 3. Must be a positive integer.
    :param shape: (width, height) of drawing window in pixels. Note that large windows may exhibit
        perceptible lag when drawing. Default = (720, 576).
    :param thin_it: Only iterate pixels to max_it if they are not diverged by this iteration,
        saving computation costs. Default = 5.
    """
    def __init__(self, *,
                 bailout_radius=3.0,
                 brush_strength=50.0,
                 brush_radius=100,
                 cmap_name='gray_r',
                 cmap_period=4.0,
                 max_it=30,
                 noise_seed=None,
                 noise_sig=26.0,
                 power=3,
                 shape=(720, 576),
                 thin_it=5):
        self.w, self.h, = shape
        self.buffer, self.power, self.mpl_cmap, self.period, self.bailout_radius, self.thin_it, self.max_it \
            = brush_radius, power, colormaps[cmap_name], cmap_period, bailout_radius, thin_it, max_it

        # set up brush
        d2 = d2fromcenter((2 * self.buffer + 1, 2 * self.buffer + 1))
        self.brush = brush_strength / (d2 + 1e-7)  # Laplace smoothed
        d2max = d2.max() / 2
        self.brush[d2 > d2max] = 0

        # create buffered layers in numpy
        unit = unit_noise(shape=(self.h, self.w), resolution=1, rbf_sigma=noise_sig, seed=noise_seed)
        buffered_shape = (2 * brush_radius + self.h, 2 * brush_radius + self.w)
        self.buffered_unit = np.zeros(buffered_shape, dtype=complex)
        self.buffered_unit[self.buffer:-self.buffer, self.buffer:-self.buffer] = unit
        self.buffered_intensity = np.zeros((2 * brush_radius + self.h, 2 * brush_radius + self.w))
        self.buffered_rgb = np.zeros(buffered_shape + (3,))
        first_frame = self.z2rgb(self.bailout_radius * unit)
        self.buffered_rgb[self.buffer:-self.buffer, self.buffer:-self.buffer] = first_frame

        # tkinter set up to display and update artwork
        root = tk.Tk()
        root.title("Draw Something!")
        self.canvas = tk.Canvas(root, width=self.w, height=self.h)  # transposed from numpy
        self.canvas.bind("<B1-Motion>", self.paint_stroke)
        #self.canvas.bind("<Button-2>", self.debug_printout)   # debug only
        self.canvas.pack()
        self.image = np2image(first_frame)
        self.image_item = self.canvas.create_image(0, 0, anchor="nw", image=self.image)

        # tkinter set up to save art at user-input resolution
        root.bind('1', lambda event: self.save_art(1))
        root.bind('2', lambda event: self.save_art(2))
        root.bind('3', lambda event: self.save_art(3))
        root.bind('4', lambda event: self.save_art(4))
        root.bind('5', lambda event: self.save_art(5))
        root.bind('6', lambda event: self.save_art(6))
        root.bind('7', lambda event: self.save_art(7))
        root.bind('8', lambda event: self.save_art(8))
        root.bind('9', lambda event: self.save_art(9))

        root.mainloop()

    def t2rgb(self, t):
        """Maps from (smoothed) escape times to rgb space."""
        t = np.maximum(t - 1, 0)    # ensures outside starts at 0 on cmap
        s = (t % self.period) / self.period
        i = (t / self.period).astype(int)   # how many cycles
        reverse = (i % 2) == 1
        s[reverse] = 1. - s[reverse]
        return 255 * self.mpl_cmap(s)[:, :, :3]

    def i2m(self, i):
        """Map paint intensity to modulus."""
        m = np.sqrt((1 / (i + 1e-7)))
        m = np.minimum(m, self.bailout_radius)
        return m

    def z2rgb(self, z0, max_it=None):
        """Map values in the complex plane to fractal image colors."""
        if max_it is None:
            max_it = self.max_it

        zn = z0
        t = -1 * np.ones(z0.shape)          # will contain smooth escape time

        for it in range(min(max_it, self.thin_it)):
            azn = np.abs(zn)
            escaped = (azn > self.bailout_radius + 1e-6) & (t < 0)  # 1e-6 prevents dots w small bailout rad
            t[escaped] = it + np.exp(1 - azn[escaped] / self.bailout_radius)
            zn[t >= 0] = 0     # prevent overflow warning
            zn = zn ** self.power + z0

        # avoid redundant computation for early escaped points
        ind = (t < 0) * (azn <= self.bailout_radius)  # not yet escaped
        zn, z0, t_, = zn[ind], z0[ind], t[ind]

        for it in range(self.thin_it, max_it):
            azn = np.abs(zn)
            escaped = (azn > self.bailout_radius + 1e-6) & (t_ < 0)
            t_[escaped] = it + np.exp(self.bailout_radius - azn[escaped])
            zn[t_ >= 0] = 0     # prevent overflow warning
            if it < self.max_it - 1:
                zn = zn ** self.power + z0

        t[ind] = t_
        interior = (t < 0)
        result = self.t2rgb(t)
        result[interior] = 0
        return result

    def debug_printout(self, event):
        """Utility function for debugging; not used in typical execution."""
        u, v = event.x, event.y
        print("coordinates: (%d, %d)" % (u, v))
        i = self.buffered_intensity[self.buffer + v, self.buffer + u]
        print("intensity:", i)
        print("modulus:", np.sqrt(1 / (i + 0.000001)))
        print("direction:", self.buffered_unit[self.buffer + v, self.buffer + u])
        print()

    def paint_stroke(self, event):
        """Respond to a B1-motion event by updating buffered fields and display window."""
        u, v = event.x, event.y

        # check boundaries
        if u < 0 or v < 0 or u >= self.w or v >= self.h:
            return

        # update intensity
        new_intensity = self.buffered_intensity[v:v + 2 * self.buffer + 1, u:u + 2 * self.buffer + 1]
        new_intensity += self.brush

        # update z and don't exceed bailout radius
        new_z = self.i2m(new_intensity).astype(complex)
        new_z *= self.buffered_unit[v:v + 2 * self.buffer + 1, u:u + 2 * self.buffer + 1]

        # update colors in numpy
        new_rgb = self.z2rgb(new_z)
        self.buffered_rgb[v:v + 2 * self.buffer + 1, u:u + 2 * self.buffer + 1] = new_rgb
        frame = self.buffered_rgb[self.buffer:-self.buffer, self.buffer:-self.buffer]
        self.image = np2image(frame)
        self.canvas.itemconfig(self.image_item, image=self.image)

    def save_art(self, sf: int):
        """Save a png image of the current frame with resolution increased sf times."""
        n = 1
        while os.path.exists("fractalination-%d.png" % n):
            n += 1
        savefile = "fractalination-%d.png" % n
        print("Saving current image to %s with resolution increased %d times..."
              % (savefile, sf))
        if sf == 1:
            image = self.image
        else:
            intensity = self.buffered_intensity[self.buffer:-self.buffer, self.buffer:-self.buffer]
            modulus = self.i2m(intensity)
            unit = self.buffered_unit[self.buffer:-self.buffer, self.buffer:-self.buffer]
            z = unit * modulus
            zz = upsample(z, sf)
            rgb = self.z2rgb(zz, max_it=80)     # crisper image
            image = np2image(rgb)

        imgpil = ImageTk.getimage(image)
        imgpil.save(savefile)
        imgpil.close()

