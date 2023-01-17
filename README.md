# fractalinator

This README is a work in progress.

TODOs:
1. crop border in logo
2. document command line args fully

![fractalinator](https://user-images.githubusercontent.com/53065461/212810760-953a8e39-fec0-4d09-9e63-67543390be12.png)

This repository contains Python code for texturing words and simple drawings like a mandelbrot fractal. The above image starting as a simple doodle of a ray gun, until it was *fractalinated!* To fractalinate your own drawing, follow the three steps below:
1. Clone this repository: ```git clone https://github.com/fcseidl/fractalinator.git```
2. Screenshot the words or picture you wish to fractalinate, and save the screenshot as a ```.png``` file in your newly cloned fractalinator directory.
3. Run the main script, e.g. ```python fractalinator.py -i input.png -r 200 -c wolverine```. This will create a matplotlib popup window displaying a newly created fractalination of your image. If you like it, you can save the image directly out of matplotlib. If you want to cut the border around your image, pass the additional argument ```-o outfile.png``` to save the image properly in ```.png``` format after you close the popup.

If you don't love the initial image, the main script offers quite a few arguments which can be tweaked to alter it. I recommend adjusting the resolution down when experimenting with arguments, as the unoptimized code may take a minute or so to create an image which isn't a bit grainy. After you find the settings you like, run the program again with a higher resolution, and pass it an outfile name to save your creation.
