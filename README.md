# Fractalinator

This repo holds the source code from a digital art demo I created and deployed as a single-page web application. To use the app to make your own art, click [here](https://fcseidl.github.io/fractalinator/). Read on to learn more about the idea and its implementation.

This is an drawing app which lets you draw a [multibrot](https://en.wikipedia.org/wiki/Multibrot_set)-like fractal in any shape that you choose! The video below shows an example. I tried to evoke a saguaro cactus. A few more example fractalinations are at the bottom of this README.


https://github.com/user-attachments/assets/bca13855-29b0-4c92-9ce6-bf94ea0d238d




## Implementation
Your browser runs the fractalinator app using the four files in the ```/docs``` folder. Three of these are the usual `index.html`, with a CSS stylesheet and a javascript which handles the interactivity. The fourth is a wheel for the ```fractalinator``` Python package, built from source code in this repository. This package controls the fractal image, performing numerical computation which would be slow and cumbersome in Javascript. Python methods are called from Javascript using [pyodide](https://pyodide.org/en/stable/index.html), a WASM Python interpreter.

You can also install the fractalinator package to your Python environment using 
```
pip install git+https://github.com/fcseidl/fractalinator/
```
If your environment has Tkinter configured, you can run the `demo.py` module to open a fractalinator canvas in a separate window, outside the browser.

## Is the name a *Phineas and Ferb* reference?
Yes, yes it is.

## Lagoon
The waves are achieved by setting ```bailout_radius=2.0```.

![fractalinator](gallery/lagoon.png)

## Flames
Here, I drew in the negative space rather than the positive.

![fractalinator](gallery/flames.png)

## Ghost
Happy October.

![fractalinator](gallery/ghost.png)

## Saguaro
Here's the cactus drawing from the video, in higher resolution.

![fractalinator](gallery/cactus.png)
