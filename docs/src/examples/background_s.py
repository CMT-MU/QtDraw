#
# background_s.py
#
import numpy as np
from qtdraw.core.pyvista_widget import create_qtdraw_file


# draw objects by using widget.
def draw(widget):
    widget.set_cell("off")  # cell off.

    # add objects.
    for i in range(32):
        x = np.cos(i * np.pi / 8)
        y = np.sin(i * np.pi / 8)
        z = i * 0.05
        widget.add_site(position=f"[{x},{y},{z}]", size=0.1)


# draw and write file.
create_qtdraw_file(filename="output.qtdw", callback=draw)
