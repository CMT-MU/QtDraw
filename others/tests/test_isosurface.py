"""
Test for isosurface drawing.

This module provides a test for isosurface drawing.
"""

import numpy as np

from qtdraw.parser.xsf import create_data
from qtdraw.util.util import write_dict


# ==================================================
def test_isosurface():
    n = [50, 50, 50]
    origin = [-0.5, -0.5, -0.5]
    A = np.eye(4)
    endpoint = True

    # data function for each point.
    def ek(x, y, z):
        return -2.0 * (np.cos(2 * np.pi * x) + np.cos(2 * np.pi * y) + np.cos(2 * np.pi * z))

    # surface function for each point.
    def vx(x, y, z):
        return 4.0 * np.pi * np.sin(2 * np.pi * x)

    def vy(x, y, z):
        return 4.0 * np.pi * np.sin(2 * np.pi * y)

    def vz(x, y, z):
        return 4.0 * np.pi * np.sin(2 * np.pi * z)

    def v(x, y, z):
        return 4.0 * np.pi * np.sqrt(np.sin(2 * np.pi * x) ** 2 + np.sin(2 * np.pi * y) ** 2 + np.sin(2 * np.pi * z) ** 2)

    surface = {"vx": vx, "vy": vy, "vz": vz, "v": v}

    grid_data = create_data(n, origin, A, endpoint, ek, surface)

    write_dict("cubic.py", grid_data, "grid_data")


# ================================================== main
test_isosurface()
