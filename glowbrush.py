"""
Simple Tkinkter demo widget which allows user to draw in glowing white on a dark background.
"""

import tkinter as tk
import numpy as np
from PIL import Image, ImageTk


# widget parameters
width = 640
height = 480
brightness = 10
fade_dist = 300


def np2image(arr):
    return ImageTk.PhotoImage(image=Image.fromarray(arr))


class GlowBrush:

    def __init__(self, canvas, buffer, filter):
        self.buffer = buffer
        self.filter = filter
        self.canvas = canvas

        # create blur of light intensity around source
        blur_width = 2 * buffer + 1
        self.blur = np.ones((blur_width, blur_width)) * brightness
        for u in range(blur_width):
            for v in range(blur_width):
                self.blur[u, v] /= ((u - buffer)**2 + (v - buffer)**2) + 1   # Laplace smoothing

        self.buffered_intensity = np.zeros((height + 2 * fade_dist, width + 2 * fade_dist))

        self.canvas.bind("<B1-Motion>", self.stroke)
        self.canvas.pack(expand="yes", fill="both")

        self.img = None

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
    canvas = tk.Canvas(root, width=640, height=480)

    GlowBrush(canvas, 200, basic_filter)
    root.mainloop()


if __name__ == "__main__":
    main()


