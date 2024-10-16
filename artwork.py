
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
                 brush_strength=75,
                 brush_radius=100,
                 power=3,
                 cmap_name='gray_r',
                 cmap_period=8,
                 noise_sig=26,
                 noise_seed=None,
                 bailout_radius=3,
                 thin_it=5,
                 iterations=40):
        self.w, self.h, = width, height
        self.buffer, self.power, self.mpl_cmap, self.period, self.bailout_radius, self.thin_it, self.n_it \
            = brush_radius, power, colormaps[cmap_name], cmap_period, bailout_radius, thin_it, iterations

        # set up brush
        d2 = d2fromcenter((2 * self.buffer + 1, 2 * self.buffer + 1))
        self.brush = brush_strength / (d2 + 1e-7)  # Laplace smoothed
        d2max = d2.max() / 2
        self.brush[d2 > d2max] = 0

        # create buffered layers in numpy
        unit = unit_noise(shape=(self.h, self.w), resolution=1, rbf_sigma=noise_sig, seed=noise_seed)
        buffered_shape = (2 * brush_radius + height, 2 * brush_radius + width)
        self.buffered_unit = np.zeros(buffered_shape, dtype=complex)
        self.buffered_unit[self.buffer:-self.buffer, self.buffer:-self.buffer] = unit
        self.buffered_intensity = np.zeros((2 * brush_radius + height, 2 * brush_radius + width))
        self.buffered_rgb = np.zeros(buffered_shape + (3,))
        first_frame = self.z2rgb(self.bailout_radius * unit)
        self.buffered_rgb[self.buffer:-self.buffer, self.buffer:-self.buffer] = first_frame

        # tkinter set up to display and update artwork
        root = tk.Tk()
        root.title("Draw Something!")
        self.canvas = tk.Canvas(root, width=self.w, height=self.h)  # transposed from numpy
        self.canvas.bind("<B1-Motion>", self.paint_stroke)
        # debug util
        self.canvas.bind("<Button-2>", self.debug_printout)
        self.canvas.pack()

        # divide image into tiles for fast drawing
        self.brush_width, _ = self.brush.shape
        self.tiles, self.items = self.init_tiles()

        root.mainloop()

    def tile_idx(self, idx):
        """Compute tile row/column from pixel u/v."""
        return int(idx / self.brush_width)

    def tile_rgb(self, i, j):
        """Return pixel coordinates of nw corner and RGB values of (i, j) tile."""
        l = i * self.brush_width
        r = min(l + self.brush_width, self.h)
        t = j * self.brush_width
        b = min(t + self.brush_width, self.w)
        return l, t, self.buffered_rgb[
                        self.buffer + l:self.buffer + r,
                        self.buffer + t:self.buffer + b]

    def init_tiles(self):
        """Initialize a grid of separately animated image tiles."""
        tiles, items = [], []
        wtiles = self.tile_idx(self.h) + 1
        htiles = self.tile_idx(self.w) + 1
        for i in range(wtiles):
            row_tiles, row_items = [], []
            for j in range(htiles):
                l, t, ijframe = self.tile_rgb(i, j)
                tile = np2image(ijframe)# * ((i + j) % 2))
                row_tiles.append(tile)
                row_items.append(
                    self.canvas.create_image(t, l, anchor="nw", image=tile)
                )
            tiles.append(row_tiles)
            items.append(row_items)
        return tiles, items

    def redraw_tile(self, u, v):
        """Redraw the tile containing a pixel."""
        i = self.tile_idx(u)
        j = self.tile_idx(v)
        _, _, rgb = self.tile_rgb(i, j)
        tile = np2image(rgb)
        self.tiles[i][j] = tile
        self.canvas.itemconfig(self.items[i][j], image=tile)

    def t2rgb(self, t):
        """Maps from (smoothed) escape times to rgb space."""
        t = np.maximum(t - 1, 0)    # ensures outside starts at 0 on cmap
        s = (t % self.period) / self.period
        i = (t / self.period).astype(int)   # how many cycles
        reverse = (i % 2) == 1
        s[reverse] = 1. - s[reverse]
        return 255 * self.mpl_cmap(s)[:, :, :3]

    def z2rgb(self, z0):
        """Map values in the complex plane to fractal image colors."""
        zn = z0
        t = -1 * np.ones(z0.shape)          # smooth escape time

        for it in range(min(self.n_it, self.thin_it)):
            azn = np.abs(zn)
            escaped = (azn > self.bailout_radius) & (t < 0)
            t[escaped] = it + np.exp(1 - azn[escaped] / self.bailout_radius)
            zn[t >= 0] = 0     # prevent overflow warning
            zn = zn ** self.power + z0

        # avoid redundant computation for early escaped points
        ind = (t < 0) * (azn <= self.bailout_radius)  # not yet escaped
        zn, z0, t_, = zn[ind], z0[ind], t[ind]

        for it in range(self.thin_it, self.n_it):
            azn = np.abs(zn)
            escaped = (azn > self.bailout_radius) & (t_ < 0)
            t_[escaped] = it + np.exp(self.bailout_radius - azn[escaped])
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

        # check boundaries
        if u < 0 or v < 0 or u >= self.w or v >= self.h:
            return

        # update intensity
        new_intensity = self.buffered_intensity[v:v + self.brush_width, u:u + self.brush_width]
        new_intensity += self.brush

        # update z and don't exceed bailout radius
        new_z = np.sqrt(1 / (new_intensity + 1e-7))
        new_z = np.minimum(new_z, self.bailout_radius).astype(complex)
        new_z *= self.buffered_unit[v:v + self.brush_width, u:u + self.brush_width]

        # update colors in numpy
        new_rgb = self.z2rgb(new_z)
        self.buffered_rgb[v:v + self.brush_width, u:u + self.brush_width] = new_rgb

        # get pixel coordinates of brush corners
        l = max(0, v - self.buffer)
        r = min(self.h - 1, v + self.buffer + 1)
        t = max(0, u - self.buffer)
        b = min(self.w - 1, u + self.buffer + 1)

        # redraw four tiles
        for u, v in [(l, t), (l, b), (r, t), (r, b)]:
            self.redraw_tile(u, v)
