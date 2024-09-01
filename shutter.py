
import tkinter as tk
import numpy as np
from PIL import Image, ImageTk


root = tk.Tk()
array = np.ones((500, 500)) * 255
canvas = tk.Canvas(root, width=500, height=500)
photoimage = ImageTk.PhotoImage(image=Image.fromarray(array))
canvas.pack()
image = canvas.create_image(0, 0, anchor="nw", image=photoimage)

def move_shutter(event):
    """Change and redraw the image each time the mouse is moved with the left button down."""
    global photoimage
    array[:event.y] = 0
    photoimage = ImageTk.PhotoImage(image=Image.fromarray(array))
    canvas.itemconfig(image, image=photoimage)

canvas.bind("<B1-Motion>", move_shutter)
root.mainloop()