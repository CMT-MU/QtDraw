# SPDX-License-Identifier: MPL-2.0
# Copyright (C) 2021- The QtDraw developers
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

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
