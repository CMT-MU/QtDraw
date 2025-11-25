"""
Test for PyVistaQt. (does not work)

This module provides a test for PyVistaQt BackgroundPlotter.
"""

import pyvista as pv
from pyvistaqt import BackgroundPlotter
from PySide6.QtWidgets import QApplication


class Plotter(BackgroundPlotter):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def paintEvent(self, event):
        # override the function to do nothing for PySide 6.10 or later.
        pass


app = QApplication([])

sphere = pv.Sphere()

plotter = Plotter(app=app)
plotter.add_mesh(sphere)

app.exec()
