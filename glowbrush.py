"""
Simple Tkinkter demo widget which allows user to draw in glowing white on a dark background.
"""

import tkinter as tk
import numpy as np
from PIL import Image, ImageTk


def np2image(arr):
    return ImageTk.PhotoImage(
        image=Image.fromarray(
            arr.astype(
                np.uint8)))


class GlowBrush:

    def __init__(self, root, first_frame, spread, buffer, filt):
        self.h, self.w, _ = first_frame.shape
        self.canvas = tk.Canvas(root, width=self.w, height=self.h)    # transposed from numpy
        self.canvas.bind("<B1-Motion>", self.stroke)
        self.canvas.pack()

        self.buffer = buffer
        self.buffered_intensity = np.zeros((self.h + 2 * buffer, self.w + 2 * buffer))
        self.buffered_frame = np.zeros((self.h + 2 * buffer, self.w + 2 * buffer, 3))
        self.buffered_frame[self.buffer:-self.buffer, self.buffer:-self.buffer] = first_frame
        self.filter = filt
        self.image = np2image(first_frame)
        self.image_item = self.canvas.create_image(0, 0, anchor="nw", image=self.image)

        # define blur of intensity around brushstrokes
        blur_width = 2 * buffer + 1
        self.blur = np.ones((blur_width, blur_width)) * spread
        for u in range(blur_width):
            for v in range(blur_width):
                self.blur[u, v] /= ((u - buffer) ** 2 + (v - buffer) ** 2) + 1  # Laplace smoothing

    def stroke(self, event):
        u, v = event.x, event.y
        if u < 0 or v < 0 or u >= self.w or v >= self.h:    # check boundaries
            return
        changed_intensity = self.buffered_intensity[v:v + 2 * self.buffer + 1, u:u + 2 * self.buffer + 1]
        changed_intensity += self.blur
        changed_frame = self.filter(v, u, changed_intensity)
        self.buffered_frame[v:v + 2 * self.buffer + 1, u:u + 2 * self.buffer + 1] = changed_frame
        frame = self.buffered_frame[self.buffer:-self.buffer, self.buffer:-self.buffer]
        self.image = np2image(frame)
        self.canvas.itemconfig(self.image_item, image=self.image)


def basic_filter(_, __, raw):
    grey = np.minimum(np.sqrt(raw), 1) * 255
    return np.dstack([grey, grey, grey])


def main():
    root = tk.Tk()
    GlowBrush(root, np.zeros((700, 1000, 3)), 10, 200, basic_filter)
    root.mainloop()


if __name__ == "__main__":
    main()


