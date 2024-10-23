
from ast import literal_eval
from sys import argv
from .artwork import Artwork


if __name__ == "__main__":
    kwargs = {}
    for arg in argv[2:]:
        try:
            k, v = arg.split('=')
            kwargs[k] = literal_eval(v)
        except ValueError:
            raise ValueError("Unable to parse keyword argument %s" % arg)
    Artwork(**kwargs)
