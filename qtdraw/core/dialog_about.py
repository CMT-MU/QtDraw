"""
About dialog.

This module provides about dialog for PyVistaWidget.
"""

from pathlib import Path
import sys
from numpy import __version__ as numpy_ver
from sympy import __version__ as sympy_ver
from matplotlib import __version__ as matplot_ver
from PySide6 import __version__ as pyside6_ver
import pyvista as pv
from pyvistaqt import __version__ as pyvistaqt_ver
from PySide6.QtWidgets import QDialog, QWidget, QDialogButtonBox, QSizePolicy
from PySide6.QtGui import QPixmap
from qtdraw.widget.custom_widget import Layout, Label, VSpacer
from qtdraw.__init__ import __version__, __date__, __author__
from qtdraw.util.util import check_multipie


# ==================================================
class AboutDialog(QDialog):
    # ==================================================
    def __init__(self, widget, parent=None):
        """
        About dialog.

        Args:
            widget (PyVistaWidget): widget.
            parent (QWidget, optional): parent.
        """
        super().__init__(parent)
        self.setWindowTitle("About")
        self.resize(100, 100)
        policy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.setSizePolicy(policy)

        self.pvw = widget

        # buttons.
        button = QDialogButtonBox(QDialogButtonBox.Ok)
        button.accepted.connect(self.accept)

        panel = self.create_about_panel(self)

        # main layout
        layout = Layout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.addWidget(panel, 0, 0, 1, 1)
        layout.addWidget(button, 1, 0, 1, 1)

    # ==================================================
    def create_about_panel(self, parent):
        """
        Create about panel.
        """
        indent = " " * 4
        vtk_ver = ".".join(map(str, pv.vtk_version_info))
        pyvista_ver = pv._version.__version__
        python_ver = sys.version.replace(" [", f"\n{indent+indent}[")
        multipie = "version" in self.pvw._status["multipie"].keys()

        panel = QWidget(parent)
        layout = Layout(panel)

        label_icon = Label(parent)
        file = str(Path(__file__).parent / "qtdraw.png")
        pix = QPixmap(file)
        pix = pix.scaledToHeight(int(2.5 * self.height()))
        label_icon.setPixmap(pix)
        label_qtdraw = Label(parent, "QtDraw", True)
        label_copyright = Label(parent, self.pvw.copyright)
        label_python = Label(parent, f"\n{indent}Python: Ver. {python_ver}")
        label_pyvista = Label(parent, f"{indent}PyVista: Ver. {pyvista_ver}")
        label_pvqt = Label(parent, f"{indent}PyVistaQt: Ver. {pyvistaqt_ver}")
        label_vtk = Label(parent, f"{indent}VTK: Ver. {vtk_ver}")
        label_qt = Label(parent, f"{indent}PySide6: Ver. {pyside6_ver}")
        label_numpy = Label(parent, f"{indent}NumPy: Ver. {numpy_ver}")
        label_sympy = Label(parent, f"{indent}SymPy: Ver. {sympy_ver}")
        label_matplotlib = Label(parent, f"{indent}Matplotlib: Ver. {matplot_ver}")
        multipie = check_multipie()
        if multipie:
            from multipie import __version__ as multipie_ver

            label_multipie = Label(parent, f"{indent}MultiPie: Ver. {multipie_ver}")

        panel1 = QWidget(parent)
        layout1 = Layout(panel1)
        layout1.setContentsMargins(10, 10, 10, 10)
        layout1.addWidget(label_qtdraw, 0, 0, 1, 1)
        layout1.addWidget(label_copyright, 1, 0, 1, 1)
        layout1.addWidget(label_python, 2, 0, 1, 1)
        layout1.addWidget(label_pyvista, 3, 0, 1, 1)
        layout1.addWidget(label_pvqt, 4, 0, 1, 1)
        layout1.addWidget(label_vtk, 5, 0, 1, 1)
        layout1.addWidget(label_qt, 6, 0, 1, 1)
        layout1.addWidget(label_numpy, 7, 0, 1, 1)
        layout1.addWidget(label_sympy, 8, 0, 1, 1)
        layout1.addWidget(label_matplotlib, 9, 0, 1, 1)
        if multipie:
            layout1.addWidget(label_multipie, 10, 0, 1, 1)
            layout1.addItem(VSpacer(), 11, 0, 1, 1)
        else:
            layout1.addItem(VSpacer(), 10, 0, 1, 1)

        layout.addWidget(label_icon, 0, 0, 1, 1)
        layout.addWidget(panel1, 0, 1, 1, 1)

        return panel


# ==================================================
def get_version_info():
    """
    Get version info.

    Returns:
        - (str) -- version info.
    """
    indent = " " * 4
    vtk_ver = ".".join(map(str, pv.vtk_version_info))
    pyvista_ver = pv._version.__version__
    python_ver = sys.version
    cr = f"Versoin {__version__}, Copyright (C) {__date__} by {__author__}"

    s = "* QtDraw: " + cr + "\n"
    s += f"{indent}Python: Ver. {python_ver}" + "\n"
    s += f"{indent}PyVista: Ver. {pyvista_ver}" + "\n"
    s += f"{indent}PyVistaQt: Ver. {pyvistaqt_ver}" + "\n"
    s += f"{indent}VTK: Ver. {vtk_ver}" + "\n"
    s += f"{indent}PySide6: Ver. {pyside6_ver}" + "\n"
    s += f"{indent}NumPy: Ver. {numpy_ver}" + "\n"
    s += f"{indent}SymPy: Ver. {sympy_ver}" + "\n"
    s += f"{indent}Matplotlib: Ver. {matplot_ver}" + "\n"
    if check_multipie():
        from multipie import __version__ as multipie_ver

        s += f"{indent}MultiPie: Ver. {multipie_ver}" + "\n"
    s += "-" * 90

    return s
