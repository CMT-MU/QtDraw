#
# background.py
#
import numpy as np
from qtdraw import get_qt_application, PyVistaWidget

filename = "output.qtdw"  # output file name.

# create widget.
app = get_qt_application()
widget = PyVistaWidget(off_screen=True)

widget.set_cell("off")  # cell off.

# add objects.
for i in range(32):
    x = np.cos(i * np.pi / 8)
    y = np.sin(i * np.pi / 8)
    z = i * 0.05
    widget.add_site(position=f"[{x},{y},{z}]", size=0.1)

widget.set_view()

# save and quit.
widget.save(filename)
app.quit()
