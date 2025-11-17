"""
Test for PyVistaQt. (does not work)

This module provides a test for PyVistaQt BackgroundPlotter.
"""

import pyvista as pv
from pyvistaqt import BackgroundPlotter

plotter = BackgroundPlotter(show=True)
plotter.add_mesh(pv.Sphere())

plotter.app.exec()
