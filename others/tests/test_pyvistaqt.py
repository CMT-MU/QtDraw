"""
Test for PyVistaQt.

This module provides a test for PyVistaQt BackgroundPlotter.
"""

import pyvista as pv
from pyvistaqt import BackgroundPlotter
from PySide6.QtWidgets import QApplication

app = QApplication([])

plotter = BackgroundPlotter(app=app)
plotter.add_mesh(pv.Sphere())

app.exec()
