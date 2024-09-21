
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
                 brush_strength=100,
                 buffer=100,
                 power=2.,
                 cmap_name='twilight_shifted',
                 noise_sig=30,
                 noise_seed=None,
                 thin_it=5,
                 n_it=80):
        self.w, self.h, self.buffer, self.p_inv, self.cmap, self.thin_it, self.n_it \
            = width, height, buffer, 1 / power, colormaps[cmap_name], thin_it, n_it

        # set up brush
        d2 = d2fromcenter((2 * self.buffer + 1, 2 * self.buffer + 1))
        self.brush = brush_strength / (d2 + 1e-7)  # Laplace smoothed
        self.brush[d2 > d2.max() / 2] = 0

        # create buffered image layers
        unit = unit_noise(shape=(self.h, self.w), resolution=1, rbf_sigma=noise_sig, seed=noise_seed)
        self.buffered_unit = np.zeros((2 * buffer + height, 2 * buffer + width), dtype=complex)
        self.buffered_unit[buffer:-buffer, buffer:-buffer] = unit
        self.buffered_mod = np.zeros((self.h + 2 * buffer, self.w + 2 * buffer))
        self.buffered_frame = np.zeros((self.h + 2 * buffer, self.w + 2 * buffer, 3))

        # paint first frame
        first_frame = self.color(50 * np.ones((self.h, self.w), dtype=complex))
        self.buffered_frame[self.buffer:-self.buffer, self.buffer:-self.buffer] = first_frame

        # tkinter set up to display and update artwork
        root = tk.Tk()
        root.title("Paint Something!")
        self.canvas = tk.Canvas(root, width=self.w, height=self.h)  # transposed from numpy
        self.canvas.bind("<B1-Motion>", self.paint_stroke)
        self.canvas.pack()
        self.image = np2image(first_frame)
        self.image_item = self.canvas.create_image(0, 0, anchor="nw", image=self.image)
        root.mainloop()

    def color(self, z0):
        zn = z0
        smooth = -1 * np.ones(z0.shape)

        for it in range(self.thin_it):
            azn = np.abs(zn)
            escaped = (azn > 2) & (smooth < 0)
            smooth[escaped] = it + np.exp(2 - azn[escaped])
            zn[smooth >= 0] = 0     # prevent overflow warning
            zn = zn * zn * zn + z0

        ind = (smooth < 0) * (azn < 2)  # not yet escaped
        zn, z0, smooth_, = zn[ind], z0[ind], smooth[ind]

        for it in range(self.thin_it, self.n_it):
            azn = np.abs(zn)
            escaped = (azn > 2) & (smooth_ < 0)
            smooth_[escaped] = it + np.exp(2 - azn[escaped])
            zn[smooth_ >= 0] = 0     # prevent overflow warning
            if it < self.n_it - 1:
                zn = zn * zn * zn + z0

        smooth[ind] = smooth_
        smooth[smooth < 0] = 0.
        smooth = (smooth / self.n_it) ** self.p_inv
        return 255 * self.cmap(smooth)[:, :, :3]

    def paint_stroke(self, event):
        u, v = event.x, event.y
        if u < 0 or v < 0 or u >= self.w or v >= self.h:  # check boundaries
            return
        new_mod = self.buffered_mod[v:v + 2 * self.buffer + 1, u:u + 2 * self.buffer + 1]
        new_mod += self.brush
        new_z = np.sqrt(1 / (new_mod + (0.000001 + 0j)))
        new_z *= self.buffered_unit[v:v + 2 * self.buffer + 1, u:u + 2 * self.buffer + 1]
        new_rgb = self.color(new_z)
        self.buffered_frame[v:v + 2 * self.buffer + 1, u:u + 2 * self.buffer + 1] = new_rgb
        frame = self.buffered_frame[self.buffer:-self.buffer, self.buffer:-self.buffer]
        self.image = np2image(frame)
        self.canvas.itemconfig(self.image_item, image=self.image)
