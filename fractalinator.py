
from mandelbrot import KBrot
from viewer import Viewer
from halo import Halo
import imageio
import color_cycles

import matplotlib.pyplot as plt
import sys


# default arguments
infile = 'not provided'
outfile = None
invert = False
resolution = 200
smoothness = 0.6
tightness = 5.0
seed = 1
octaves = 5.0
cycle = color_cycles.default

# get arguments from command line``
# TODO: let user control k, julia
for i in range(len(sys.argv)):
    if sys.argv[i] in ('-h', '--help'):
        print('See the README.md on GitHub for fractalination help.')
        exit(0)

    elif sys.argv[i] in ('-i', '--infile'):
        infile = sys.argv[i + 1]

    elif sys.argv[i] in ('-o', '--outfile'):
        outfile = sys.argv[i + 1]

    elif sys.argv[i] in ('-c', '--coloring'):
        cycle = color_cycles.cycle_dict[sys.argv[i + 1]]

    elif sys.argv[i] in ('-n', '--inverted'):
        invert = True

    elif sys.argv[i] in ('-r', '--resolution'):
        resolution = int(sys.argv[i + 1])

    elif sys.argv[i] in ('-s', '--smoothness'):
        smoothness = float(sys.argv[i + 1])

    elif sys.argv[i] in ('-t', '--tightness'):
        tightness = float(sys.argv[i + 1])

    elif sys.argv[i] in ('-d', '--seed'):
        seed = int(sys.argv[i + 1])

    elif sys.argv[i] in ('-v', '--octaves'):
        octaves = float(sys.argv[i + 1])

# check arguments
if infile[-4:] != '.png':
    raise ValueError('infile must be in .png format')

if outfile is not None and outfile[-4:] != '.png':
    raise ValueError('outfile must be in .png format')

if min(resolution, smoothness, tightness, seed, octaves) <= 0:
    raise ValueError('all numerical arguments must be positive')

# starred arguments controllable from command line
fract = KBrot(
    k=2,
    color_cycle=cycle               #
)
guides, tl, br = imageio.guides_from_image(
    infile,                         #
    inverted=invert                 #
)
halo = Halo(
    guides,
    smoothness=smoothness,          #
    tightness=tightness,            #
    seed=seed,                      #
    octaves=octaves                 #
)
view = Viewer(
    fract,
    input_transform=halo,
    pixels_per_unit=resolution,     #
    topleft=tl,
    bottomright=br
)
img = view.image()
plt.imshow(img)
plt.axis('off')
plt.show()

if outfile is not None:
    imageio.dump_image(img, outfile)
