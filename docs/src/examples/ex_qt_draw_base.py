"""
Example for QtDrawBase.
"""

import numpy as np
import pyvista as pv
from qtdraw.qt_draw_base import QtDrawBase
from qtdraw.core.util import create_application

ui_dir = __file__[: __file__.rfind("/")] + "/"


# ==================================================
class QtDraw(QtDrawBase):
    # ==================================================
    def __init__(self, panel=None):
        self.app = create_application()

        super().__init__(panel=panel)
        if panel is not None:
            self._set_panel()

        self._set_anti_aliasing()
        self._set_parallel_projection()
        self.set_window_size()

    # ==================================================
    def _set_panel(self):
        self.button_screenshot.clicked.connect(lambda _: self._screenshot())

    # ==================================================
    def show(self):
        super().show()
        self.app.exec()
        del self.app


# ==================================================

rng = np.random.default_rng(1)


def plot0():
    p = QtDraw(ui_dir + "ex_simple_panel.ui")
    p.set_window_title("plot0")
    p.set_status("Here is the status bar.")
    p.layer.add_mesh(pv.Sphere())
    p.show()


def plot1():
    from matplotlib.gridspec import GridSpec

    grid = GridSpec(nrows=3, ncols=2, wspace=0.2, hspace=0.3)

    p = QtDraw("")
    p.set_window_title("plot1")
    figure = p.chart_mpl()

    L01 = figure.add_subplot(grid[:2, 0])  # upper-left.
    R0 = figure.add_subplot(grid[0, 1])  # upper-right.
    R1 = figure.add_subplot(grid[1, 1])  # lower-right.
    B = figure.add_subplot(grid[2, :])  # bottom.

    x = np.linspace(-1, 1, 100)
    L01.plot(x, x, label=r"$x$")
    R0.plot(x, np.sin(x * np.pi), label=r"$\sin x$")
    R1.plot(x, np.cos(x * np.pi), label=r"$\cos x$")
    B.plot(x, np.tan(x * np.pi), label=r"$\tan x$")

    L01.set_title("example of plot")
    B.set_xlabel("$x/\pi$")
    L01.set_ylabel("functions")
    B.set_xticks(np.linspace(-1, 1, 5))
    L01.set_yticks(np.linspace(-1, 1, 5))
    B.legend()

    p.show()


def plot2():
    p = QtDraw()
    p.set_window_title("plot2")
    x = np.linspace(0, 10, 1000)
    y = np.sin(x**2)
    chart = p.chart()
    chart.line(x, y)
    chart.x_range = [5, 10]  # Focus on the second half of the curve
    p.show()


def plot3():
    p = QtDraw()
    p.set_window_title("plot3")
    x = np.arange(11)
    y = rng.integers(-5, 6, 11)
    chart = p.chart()
    chart.background_color = (0.5, 0.9, 0.5)  # Use custom background color for chart
    chart.plot(x, y, "x--b")  # Marker style 'x', striped line style '--', blue color 'b'
    p.show()


def plot4():
    p = QtDraw()
    p.set_window_title("plot4")
    x = np.linspace(0, 10, 1000)
    y1 = np.cos(x) + np.sin(3 * x)
    y2 = 0.1 * (x - 5)
    chart = p.chart()
    chart.area(x, y1, y2, color=(0.1, 0.1, 0.9, 0.5))
    chart.line(x, y1, color=(0.9, 0.1, 0.1), width=4, style="--")
    chart.line(x, y2, color=(0.1, 0.9, 0.1), width=4, style="--")
    chart.title = "Area plot"  # Set custom chart title
    p.show()


def plot5():
    p = QtDraw()
    p.set_window_title("plot5")
    x = np.arange(1, 13)
    y1 = rng.integers(1e2, 1e4, 12)
    y2 = rng.integers(1e2, 1e4, 12)
    chart = p.chart()
    chart.bar(x, y1, color="b", label="2020")
    chart.bar(x, y2, color="r", label="2021")
    chart.x_axis.tick_locations = x
    chart.x_axis.tick_labels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    chart.x_label = "Month"
    chart.y_axis.tick_labels = "2e"
    chart.y_label = "# incidents"
    p.show()


def plot6():
    p = QtDraw()
    p.set_window_title("plot6")
    x = np.arange(1, 11)
    ys = [rng.integers(1, 11, 10) for _ in range(5)]
    labels = [f"Machine {i}" for i in range(5)]
    chart = p.chart()
    chart.bar(x, ys, label=labels)
    chart.x_axis.tick_locations = x
    chart.x_label = "Configuration"
    chart.y_label = "Production"
    chart.grid = False  # Disable the grid lines
    p.show()


def plot7():
    p = QtDraw()
    p.set_window_title("plot7")
    x = np.arange(0, 11)
    ys = [rng.integers(1, 11, 11) for _ in range(5)]
    labels = [f"Segment {i}" for i in range(5)]
    chart = p.chart()
    chart.stack(x, ys, labels=labels)
    p.show()


def plot8():
    p = QtDraw()
    p.set_window_title("plot8")
    data = np.array([8.4, 6.1, 2.7, 2.4, 0.9])
    chart = pv.ChartPie(data)
    chart.plot.labels = [f"slice {i}" for i in range(len(data))]
    p.add_chart(chart)
    p.show()


def plot9():
    p = QtDraw()
    p.set_window_title("plot9")
    data = [rng.poisson(lam, 20) for lam in range(2, 12, 2)]
    chart = pv.ChartBox(data)
    chart.plot.labels = [f"Experiment {i}" for i in range(len(data))]
    p.add_chart(chart)
    p.show()


def plot10():
    p = QtDraw("")
    p.set_window_title("plot10")
    x = rng.standard_normal(100)
    y = rng.standard_normal(100)
    chart = p.chart()
    chart.scatter(x, y, size=10, style="+")
    p.show()


plot0()
plot1()
plot2()
plot3()
plot4()
plot5()
plot6()
plot7()
plot8()
plot9()
plot10()
