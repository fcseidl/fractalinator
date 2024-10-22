
from ast import literal_eval
from sys import argv
from artwork import Artwork


if __name__ == "__main__":
    kwargs = dict(
        (k, literal_eval(v))
        for k, v in (arg.split('=') for arg in argv[2:])
    )
    Artwork(**kwargs)
