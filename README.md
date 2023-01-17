![fractalinator](logo.png)

# fractalinator

This repository contains Python code for texturing words and simple drawings like a mandelbrot fractal. 

## Overview

The above image started as a simple doodle of a Dr. Doofenshmirtz-style ray gun, until it was *fractalinated!* To fractalinate your own drawing, follow the three steps below:
1. Clone this repository: ```git clone https://github.com/fcseidl/fractalinator.git```
2. Screenshot the words or picture you wish to fractalinate, and save the screenshot as a ```.png``` file in your newly cloned ```fractalinator``` directory.
3. Run the main script, e.g. ```python fractalinator.py -i input.png -r 200 -c wolverine```. This will create a matplotlib popup window displaying a newly created fractalination of your image. If you like it, you can save the image directly out of matplotlib. If you want to cut the border around your image, pass the additional argument ```-o outfile.png``` to save the image properly in ```.png``` format after you close the popup.

If you don't love the initial image, the main script offers quite a few arguments which can be tweaked to alter it. I recommend adjusting the resolution down when experimenting with arguments, as the unoptimized code may take a minute or so to create an image which isn't a bit grainy. After you find the settings you like, run the program again with a higher resolution, and pass it an outfile name to save your creation.

## Command line arguments

```-h/--help``` refers you to this README.

```-i/-infile``` is used to specify that the next argument is the name of a ```.png``` image to fractalinate.

```-o/--outfile``` is used to specify that the next argument is the name of a file to store the fractalized image.

```-c/--coloring``` is used to specify that the next argument is a color cycle to be used for the lemniscates surrounding the fractalinated curves. The image above illustrates the default setting, but there are others: 'wolverine', 'midnight', 'valentine', 'zebra', and 'rainbow'. Play with them to see what you like!

```-n/--inverted``` tells the program to invert the colors in the infile image before processing.

```-r/--resolution``` is used to specify that the next argument is an integer which will control the resolution of the image. Using ```-r 50``` results in a pretty grainy image, while ```-r 300``` is quite crisp. The default is 200.

```-s/--smoothness``` is used to specify that the next argument is a scalar value. Larger values tend to shrink jagged protrusions on the edges of your fractalinated lines. The default is 0.6.

```-t/--tightness``` is used to specify that the next argument is another scalar value. Larger values tend to pull the fractalinated curve more closely around the original curve. The default is 5.0.

```-d/--seed``` is used to specify that the next argument is a positive integer random seed. Changing this value gives you different fractalinations of the same image.

```-v/--octaves``` is used to specify that the next argument is a scalar value passed to a Perlin noise instance. Generally, smaller values induce more order in the resulting image. The default is 5.0.
