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


# create blur of light intensity around source
blur_width = 2 * fade_dist + 1
blur = np.ones((blur_width, blur_width)) * brightness
for u in range(blur_width):
    for v in range(blur_width):
        blur[u, v] /= ((u - fade_dist)**2 + (v - fade_dist)**2) + 1   # Laplace smoothing


root = tk.Tk()
buffered_intensity = np.zeros((height + 2 * fade_dist, width + 2 * fade_dist))
canvas = tk.Canvas(root, width=width, height=height)
img = None


def brush(event):
    global img
    y, x = event.x, event.y
    buffered_intensity[x:x + 2 * fade_dist + 1, y:y + 2 * fade_dist + 1] += blur
    intensity = buffered_intensity[fade_dist:-fade_dist, fade_dist:-fade_dist]
    arr = (np.minimum(np.sqrt(intensity), 1) * 255)
    img = np2image(arr)
    canvas.create_image(0, 0, anchor="nw", image=img)


canvas.bind("<B1-Motion>", brush)
canvas.pack(expand="yes", fill="both")

root.mainloop()


"""import matplotlib.pyplot as plt
plt.imshow(blur)
plt.show()"""
