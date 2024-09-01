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

    def __init__(self, root, w, h, spread, buffer, filter):
        self.canvas = tk.Canvas(root, width=w, height=h)
        self.canvas.bind("<B1-Motion>", self.stroke)
        self.canvas.pack()

        self.buffered_intensity = np.zeros((h + 2 * buffer, w + 2 * buffer))    # transposed from tk
        self.buffer = buffer
        self.filter = filter
        self.img = None

        # define blur of intensity around brushstrokes
        blur_width = 2 * buffer + 1
        self.blur = np.ones((blur_width, blur_width)) * spread
        for u in range(blur_width):
            for v in range(blur_width):
                self.blur[u, v] /= ((u - buffer) ** 2 + (v - buffer) ** 2) + 1  # Laplace smoothing

    def stroke(self, event):
        y, x = event.x, event.y
        self.buffered_intensity[x:x + 2 * self.buffer + 1, y:y + 2 * self.buffer + 1] += self.blur
        intensity = self.buffered_intensity[self.buffer:-self.buffer, self.buffer:-self.buffer]
        arr = self.filter(intensity)
        self.img = np2image(arr)
        self.canvas.create_image(0, 0, anchor="nw", image=self.img)


def basic_filter(raw):
    return np.minimum(np.sqrt(raw), 1) * 255


def main():
    root = tk.Tk()
    GlowBrush(root, 640, 480, 200, basic_filter)
    root.mainloop()


if __name__ == "__main__":
    main()


