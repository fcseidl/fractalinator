"""Multibrot-like drawing tool."""

from .artwork import Artwork

# import tkinter app driver but only if tkinter is available
try:
    from .tkapp import App
except ModuleNotFoundError:
    pass
