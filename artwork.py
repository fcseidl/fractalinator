
import tkinter as tk
import numpy as np
from PIL import Image, ImageTk

from noise import unit_noise, d2fromcenter


def np2image(arr):
    """Convert a numpy array into an image which can go on a tkinter canvas."""
    return ImageTk.PhotoImage(
        image=Image.fromarray(
            arr.astype(
                np.uint8)))


class Artwork:

    def __init__(self,
                 width,
                 height,
                 brush_strength,
                 buffer,
                 paint,
                 noise_sig,
                 noise_seed):
        self.w, self.h, = width, height

        # set up brush
        self.buffer = buffer
        d2 = d2fromcenter((2 * self.buffer + 1, 2 * self.buffer + 1))
        self.brush = brush_strength / (d2 + 1e-7)   # Laplace smoothed
        self.brush[d2 > d2.max() / 2] = 0       # circular mask

        # create buffered image layers
        unit = unit_noise(shape=(self.h, self.w), resolution=1, rbf_sigma=noise_sig, seed=noise_seed)
        self.buffered_unit = np.zeros((2 * buffer + height, 2 * buffer + width), dtype=complex)
        self.buffered_unit[buffer:-buffer, buffer:-buffer] = unit
        self.buffered_intensity = np.zeros((self.h + 2 * buffer, self.w + 2 * buffer))
        self.buffered_frame = np.zeros((self.h + 2 * buffer, self.w + 2 * buffer, 3))

        # paint first frame
        self.paint = paint
        first_frame = paint(50 * np.ones((self.h, self.w), dtype=complex))
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

    def paint_stroke(self, event):
        u, v = event.x, event.y
        if u < 0 or v < 0 or u >= self.w or v >= self.h:  # check boundaries
            return
        new_intensity = self.buffered_intensity[v:v + 2 * self.buffer + 1, u:u + 2 * self.buffer + 1]
        new_intensity += self.brush
        new_z = np.sqrt(1 / (new_intensity + (0.000001 + 0j)))
        new_z *= self.buffered_unit[v:v + 2 * self.buffer + 1, u:u + 2 * self.buffer + 1]
        new_rgb = self.paint(new_z)
        self.buffered_frame[v:v + 2 * self.buffer + 1, u:u + 2 * self.buffer + 1] = new_rgb
        frame = self.buffered_frame[self.buffer:-self.buffer, self.buffer:-self.buffer]
        self.image = np2image(frame)
        self.canvas.itemconfig(self.image_item, image=self.image)

