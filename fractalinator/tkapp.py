
import os
import tkinter as tk
from PIL import Image, ImageTk

from .artwork import Artwork


def np2image(arr):
    """Convert a numpy array into an image which can go on a tkinter canvas."""
    return ImageTk.PhotoImage(image=Image.fromarray(arr))


class App:
    """A fractalination in a tkinter widget. Kwargs passed to Artwork()."""
    def __init__(self, **kwargs):
        art = Artwork(**kwargs)
        root = tk.Tk()
        root.title("Draw Something!")
        canvas = tk.Canvas(root, width=art.w, height=art.h)  # transposed from numpy
        self.image = np2image(art.rgb)
        image_item = canvas.create_image(0, 0, anchor="nw", image=self.image)

        def on_b1_motion(event):
            u, v = event.x, event.y
            art.paint_stroke(u, v)
            self.image = np2image(art.rgb)
            canvas.itemconfig(image_item, image=self.image)

        canvas.bind("<B1-Motion>", on_b1_motion)
        canvas.pack()

        def save_art(sf: int):
            """Save a png image of the current frame with resolution increased sf times."""
            n = 1
            while os.path.exists("fractalination-%d.png" % n):
                n += 1
            savefile = "fractalination-%d.png" % n
            print("Saving current image to %s with resolution increased %d times..."
                  % (savefile, sf))

            image = np2image(art.high_res(sf))
            imgpil = ImageTk.getimage(image)
            imgpil.save(savefile)
            imgpil.close()

        root.bind('1', lambda event: save_art(1))
        root.bind('2', lambda event: save_art(2))
        root.bind('3', lambda event: save_art(3))
        root.bind('4', lambda event: save_art(4))
        root.bind('5', lambda event: save_art(5))

        root.mainloop()

