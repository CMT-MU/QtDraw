#
# create isosurface for simple cubic tight-binding.
#
from qtdraw import QtDraw
import numpy as np
from qtdraw.parser.xsf import create_data


# ==================================================
def create_grid_data():
    n = [50, 50, 50]
    origin = [-0.5, -0.5, -0.5]
    A = np.eye(4)
    endpoint = True

    # data function for each point (dispersion relation).
    def ek(x, y, z):
        return -2.0 * (np.cos(2 * np.pi * x) + np.cos(2 * np.pi * y) + np.cos(2 * np.pi * z))

    # surface function for each point (absolute value of velocity).
    def v(x, y, z):
        return 4.0 * np.pi * np.sqrt(np.sin(2 * np.pi * x) ** 2 + np.sin(2 * np.pi * y) ** 2 + np.sin(2 * np.pi * z) ** 2)

    surface = {"v": v}

    grid_data = create_data(n, origin, A, endpoint, ek, surface)

    return grid_data


# create data.
grid_data = create_grid_data()

# create QtDraw.
win = QtDraw()

# draw isosurface.
win.set_cell("off")
win.add_isosurface(data=("cubic.py", grid_data), value=[0.5], surface="v", color="coolwarm", color_range=[10, 24])
win.set_view()

win.exec()
