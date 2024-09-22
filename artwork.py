
import tkinter as tk
import numpy as np
from PIL import Image, ImageTk
from matplotlib import colormaps

from noise import unit_noise, d2fromcenter


def np2image(arr):
    """Convert a numpy array into an image which can go on a tkinter canvas."""
    return ImageTk.PhotoImage(
        image=Image.fromarray(
            arr.astype(
                np.uint8)))


class Artwork:

    def __init__(self, width, height, *,
                 brush_strength=50,
                 brush_radius=100,
                 power=2,
                 cmap_name='twilight_shifted',
                 cmap_period=1,
                 noise_sig=30,
                 noise_seed=None,
                 thin_it=5,
                 iterations=60):
        self.w, self.h, = width, height
        self.buffer, self.power, self.mpl_cmap, self.period, self.thin_it, self.n_it \
            = brush_radius, power, colormaps[cmap_name], cmap_period, thin_it, iterations
        self.norm = 1 - np.exp(-(2 ** power + 2))

        # set up brush
        d2 = d2fromcenter((2 * self.buffer + 1, 2 * self.buffer + 1))
        self.brush = brush_strength / (d2 + 1e-7)  # Laplace smoothed
        self.brush[d2 > d2.max() / 2] = 0

        # create buffered image layers
        unit = unit_noise(shape=(self.h, self.w), resolution=1, rbf_sigma=noise_sig, seed=noise_seed)
        self.buffered_unit = np.zeros((2 * brush_radius + height, 2 * brush_radius + width), dtype=complex)
        self.buffered_unit[self.buffer:-self.buffer, self.buffer:-self.buffer] = unit
        self.buffered_intensity = np.zeros((self.h + 2 * brush_radius, self.w + 2 * brush_radius))
        self.buffered_frame = np.zeros((self.h + 2 * brush_radius, self.w + 2 * brush_radius, 3))

        # paint first frame
        first_frame = self.z2rgb(50 * np.ones((self.h, self.w), dtype=complex))
        self.buffered_frame[self.buffer:-self.buffer, self.buffer:-self.buffer] = first_frame

        # tkinter set up to display and update artwork
        root = tk.Tk()
        root.title("Paint Something!")
        self.canvas = tk.Canvas(root, width=self.w, height=self.h)  # transposed from numpy
        self.canvas.bind("<B1-Motion>", self.paint_stroke)

        # debug util
        self.canvas.bind("<Button-2>", self.debug_printout)

        self.canvas.pack()
        self.image = np2image(first_frame)
        self.image_item = self.canvas.create_image(0, 0, anchor="nw", image=self.image)
        root.mainloop()

    def t2rgb(self, t):
        """Maps from (smoothed) escape times to rgb space."""
        s = (t % self.period) / self.period
        i = (t / self.period).astype(int)   # how many cycles
        reverse = (i % 2) == 1
        s[reverse] = 1. - s[reverse]
        return 255 * self.mpl_cmap(s)[:, :, :3]

    def z2rgb(self, z0):
        """Map values in the complex plane to fractal image colors."""
        zn = z0
        t = -1 * np.ones(z0.shape)          # smooth escape time

        for it in range(self.thin_it):
            azn = np.abs(zn)
            escaped = (azn > 2) & (t < 0)
            t[escaped] = it + np.exp(2 - azn[escaped])
            zn[t >= 0] = 0     # prevent overflow warning
            zn = zn ** self.power + z0

        # avoid redundant computation for early escaped points
        ind = (t < 0) * (azn <= 2)  # not yet escaped
        zn, z0, t_, = zn[ind], z0[ind], t[ind]

        for it in range(self.thin_it, self.n_it):
            azn = np.abs(zn)
            escaped = (azn > 2) & (t_ < 0)
            t_[escaped] = it + np.exp(2 - azn[escaped]) / self.norm
            zn[t_ >= 0] = 0     # prevent overflow warning
            if it < self.n_it - 1:
                zn = zn ** self.power + z0

        t[ind] = t_
        interior = (t < 0)
        result = self.t2rgb(t)
        result[interior] = 0
        return result

    def debug_printout(self, event):
        u, v = event.x, event.y
        print("coordinates: (%d, %d)" % (u, v))
        i = self.buffered_intensity[self.buffer + v, self.buffer + u]
        print("intensity:", i)
        print("modulus:", np.sqrt(1 / (i + 0.000001)))
        print("direction:", self.buffered_unit[self.buffer + v, self.buffer + u])
        print()

    def paint_stroke(self, event):
        u, v = event.x, event.y
        if u < 0 or v < 0 or u >= self.w or v >= self.h:  # check boundaries
            return
        new_intensity = self.buffered_intensity[v:v + 2 * self.buffer + 1, u:u + 2 * self.buffer + 1]
        new_intensity += self.brush
        new_z = np.sqrt(1 / (new_intensity + (0.000001 + 0j)))
        new_z *= self.buffered_unit[v:v + 2 * self.buffer + 1, u:u + 2 * self.buffer + 1]
        new_rgb = self.z2rgb(new_z)
        self.buffered_frame[v:v + 2 * self.buffer + 1, u:u + 2 * self.buffer + 1] = new_rgb
        frame = self.buffered_frame[self.buffer:-self.buffer, self.buffer:-self.buffer]
        self.image = np2image(frame)
        self.canvas.itemconfig(self.image_item, image=self.image)
