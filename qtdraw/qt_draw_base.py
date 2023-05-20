import os
import pyvista as pv
import matplotlib.pyplot as plt
import seaborn as sns
from pyvistaqt import QtInteractor
from qtpy.QtWidgets import QGridLayout, QDialog, QLabel, QFileDialog
from qtpy.QtCore import QSize, Qt
from qtpy.uic import loadUi
from qtdraw import __version__, __author__, __date__
import warnings

warnings.filterwarnings("ignore")


# ==================================================
class QtDrawBase(QDialog):
    """
    base widget.
    """

    # ==================================================
    def __init__(
        self,
        parent=None,
        panel=None,
        theme="document",
        smooth_line=True,
        smooth_point=True,
        smooth_polygon=True,
        smooth_shading=True,
        sampling=10,
    ):
        """
        initialize the class.

        Args:
            parent (QObject, optional): parent object.
            panel (str, optional): UI file name for right panel.
            theme (str, optional): theme of pyvista, "document/paraview/default/dark".
            smooth_line (bool, optional): smoothing for line ?
            smooth_point (bool, optional): smoothing for point ?
            smooth_polygon (bool, optional): smoothing for polygon ?
            smooth_shading (bool, optional): smoothing for shading ?
            sampling (int, optional): the number of sampling for smoothing.
        """
        super().__init__(parent)
        self.shading = smooth_shading

        # set qt interactor.
        self._set_theme(theme)
        self._layer = QtInteractor(
            self,
            line_smoothing=smooth_line,
            point_smoothing=smooth_point,
            polygon_smoothing=smooth_polygon,
            multi_samples=sampling,
        )
        self._layer.setMinimumSize(QSize(200, 200))

        # set status box in the left bottom.
        self.status_box = QLabel(self)
        self.status_box.setContentsMargins(15, 5, 0, 5)

        # set copyright box in the right bottom.
        self.copyright_box = QLabel(self)
        self.copyright_box.setContentsMargins(0, 5, 15, 5)
        self.copyright_box.setAlignment(Qt.AlignRight)

        # layout.
        self.layout = QGridLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.layout.addWidget(self._layer.interactor, 0, 0, 1, 2)
        self.layout.addWidget(self.status_box, 1, 0, 1, 1)

        self.setLayout(self.layout)

        self._load_panel(panel)

        # set copyright.
        self.copyright_str = f"Versoin {__version__}, Copyright (C) {__date__} by {__author__}"
        self.set_copyright(self.copyright_str)

    # ==================================================
    def _set_theme(self, theme):
        """
        set pyvista theme.

        Args:
            theme (str): base theme.
        """
        pv.set_plot_theme(theme)
        pv.global_theme.transparent_background = True
        pv.global_theme.axes.show = False
        pv.global_theme.axes.box = False
        pv.global_theme.cmap = "bwr"
        pv.global_theme.show_scalar_bar = False

    # ==================================================
    def _set_anti_aliasing(self, mode=False):
        """
        set anti aliasing mode.

        Args:
            mode (bool, optional): anti aliaing mode.
        """
        if mode:
            self._layer.enable_anti_aliasing()
        else:
            self._layer.disable_anti_aliasing()

    # ==================================================
    def _set_parallel_projection(self, mode=True):
        """
        set parallel projection mode.

        Args:
            mode (bool, optional): parallel projection mode.
        """
        if mode:
            self._layer.enable_parallel_projection()
        else:
            self._layer.disable_parallel_projection()

    # ==================================================
    def _load_panel(self, fname):
        """
        load UI file for right panel.

        Args:
            fname (str): file name of UI.

        Notes:
            - if fname is None, no panel is used.
            - if fname is "", default panel is used.
        """
        if fname == "":
            fname = os.path.dirname(__file__) + "/core/default_panel.ui"
            fname = fname.replace(os.sep, "/")

        if fname is None:
            self.layout.addWidget(self.copyright_box, 1, 1, 1, 1)
        else:
            loadUi(fname, self)
            self.layout.addWidget(self.panel, 0, 2, 1, 1)
            self.layout.addWidget(self.copyright_box, 1, 1, 1, 2)

    # ==================================================
    def set_window_size(self, width=1174, height=768):
        """
        set window size.

        Args:
            width (int, optional): width.
            height (int, optional): height.
        """
        self.resize(width, height)

    # ==================================================
    def set_window_title(self, title):
        """
        set window title.

        Args:
            title (str): window title.
        """
        self.setWindowTitle(title)

    # ==================================================
    def set_copyright(self, text):
        """
        set copyright text.

        Args:
            text (str): copyright text in the right-bottom panel.
        """
        self.copyright_box.setText(text)

    # ==================================================
    def set_status(self, text):
        """
        set status text.

        Args:
            text (str): statu text in the left-bottom panel.
        """
        self.status_box.setText(text)

    # ==================================================
    def _screenshot(self, file_type=".png"):
        """
        screenshot dialog.

        Args:
            file_type (str, optional): file type, ".png/.bmp/.tif/.tiff/.svg/.eps/.ps/.pdf".
        """
        ifile = "*.png *.bmp *.tif *.tiff"  # jpeg, jpg do not work at present.
        gfile = "*.svg *.eps *.ps *.pdf"

        default_file = os.getcwd() + "/screenshot" + file_type
        default_file = default_file.replace(os.sep, "/")

        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Save Screenshot",
            default_file,
            "Image files (" + ifile + ")",
            "Graphic files (" + gfile + ")",
        )

        if filename:
            _, ext = os.path.splitext(filename)
            if ext == "":
                ext = file_type
                filename += ext
            if ext in ifile.replace("*", "").split(" "):
                self._layer.screenshot(filename, transparent_background=True)
                self.set_status(f"Saved: {filename}")
            elif ext in gfile.replace("*", "").split(" "):
                self._layer.save_graphic(filename, "")
                self.set_status(f"Saved: {filename}")
            else:
                self.set_status(f"{ext} is unsupported.")

    # ==================================================
    def add_chart(self, chart, *charts):
        """
        add 2d chart.

        Args:
            chart (Chart): pyvsita chart.
        """
        self._layer.add_chart(chart, *charts)

    # ==================================================
    def chart(self):
        """
        chart.

        Returns:
            Chart2D: chart.
        """
        chart = pv.Chart2D()
        self._layer.add_chart(chart)

        return chart

    # ==================================================
    def chart_mpl(self, font_scale=1.0, width=1.0):
        """
        matplotlib chart.

        Returns:
            Figure: matplotlib figure.
        """
        sns.set(
            "notebook",
            "whitegrid",
            "dark",
            font_scale=1.2 * font_scale,
            rc={
                "lines.linewidth": width,
                "grid.linestyle": "--",
                "grid.linewidth": 0.6,
                "axes.linewidth": 0.6,
                "axes.xmargin": 0.0,
                "axes.ymargin": 0.0,
                "xtick.major.pad": 0.0,
                "xtick.minor.pad": 0.0,
                "ytick.major.pad": 0.0,
                "ytick.minor.pad": 0.0,
            },
        )

        figure = plt.figure(tight_layout=False)
        chart = pv.ChartMPL(figure)
        chart.background_color = "w"
        self._layer.add_chart(chart)

        return figure

    # ==================================================
    def _screen_off(self):
        """
        turn off rendering screen.
        """
        self._layer.ren_win.SetOffScreenRendering(1)

    # ==================================================
    def _screen_on(self):
        """
        turn on rendering screen.
        """
        self._layer.ren_win.SetOffScreenRendering(0)

    # ==================================================
    @property
    def layer(self):
        """
        3d plotting layer.

        Returns:
            QtInteractor: qt interactor to plot 3d object.
        """
        return self._layer

    # ==================================================
    def closeEvent(self, QCloseEvent):
        super().closeEvent(QCloseEvent)
        self._layer.close()
        self.close()
