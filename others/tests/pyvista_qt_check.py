import pyvista as pv

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QApplication, QWidget


# ==================================================
def test_pyvista():
    print("=== check if pyvista works fine or not.")
    # default setting of plotter
    pv.set_plot_theme("document")
    plotter = pv.Plotter(window_size=(2048, 1800))
    plotter.enable_parallel_projection()
    plotter.hide_axes()

    # colors for 5 points
    color = "coolwarm"
    opacity = [0.2, 0.4, 0.6, 0.8, 1.0]

    # locations and sizes
    point_cloud = [[0.0, 0, 0], [1, 0, 0], [2, 0, 0], [3, 0, 0], [4, 0, 0]]
    pdata = pv.PolyData(point_cloud)
    pdata["size"] = [1, 2, 3, 4, 5]

    # create glyph
    sphere = pv.Sphere(radius=0.1, phi_resolution=60, theta_resolution=60)
    pc = pdata.glyph(scale="size", geom=sphere, orient=False)

    # plot
    actor = plotter.add_mesh(pc, show_scalar_bar=False, smooth_shading=True, cmap=color, opacity=opacity)
    plotter.view_xy()

    def toggle_vis(flag, actor):
        actor.SetVisibility(flag)

    plotter.add_checkbox_button_widget(lambda flag: toggle_vis(flag, actor), value=True)

    plotter.show()


# ==================================================
def test_qtpy():
    print("=== check if QtPy works fine or not.")

    class Widget(QWidget):
        def __init__(self, parent=None):
            super(Widget, self).__init__(parent)

        def paintEvent(self, event):
            painter = QPainter(self)
            painter.setPen(Qt.red)
            painter.setBrush(Qt.yellow)
            painter.drawRect(10, 10, 100, 100)

    app = QApplication([])
    w = Widget()
    w.show()
    w.raise_()
    app.exec()


# ==================================================
test_pyvista()
test_qtpy()
