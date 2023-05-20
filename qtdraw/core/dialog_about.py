import os
import sys
from PyQt5.QtCore import QT_VERSION_STR
from qtpy.QtGui import QPixmap, QFont
from qtpy.QtWidgets import QDialog, QSizePolicy, QLabel, QGridLayout, QDialogButtonBox
import pyvista
import pyvistaqt
import pandas
import numpy
import sympy
import matplotlib
from gcoreutils.latex_util import latex_version


# ==================================================
class DialogAbout(QDialog):
    # ==================================================
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setModal(True)
        self.setWindowTitle("About")
        indent = 15

        self.resize(100, 100)
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)

        self.icon = QLabel(self)
        pix = QPixmap(os.path.dirname(__file__) + "/qtdraw.png")
        pix = pix.scaledToHeight(int(2.5 * self.height()))
        self.icon.setPixmap(pix)

        self.lbl_qtdraw = QLabel("QtDraw", self)
        font = QFont()
        font.setBold(True)
        self.lbl_qtdraw.setFont(font)

        self.txt_copyright = QLabel(parent.copyright_str, self)

        self.txt_pyvista = QLabel(
            "\nPyVista: Ver. "
            + pyvista._version.__version__
            + "\n     with PyVistaQt: Ver. "
            + pyvistaqt.__version__
            + ", VTK: Ver. "
            + ".".join(map(str, pyvista.vtk_version_info)),
            self,
        )
        self.txt_pyvista.setIndent(indent)

        self.txt_pandas = QLabel("Pandas: Ver. " + pandas.__version__, self)
        self.txt_pandas.setIndent(indent)

        self.txt_numpy = QLabel("NumPy: Ver. " + numpy.__version__, self)
        self.txt_numpy.setIndent(indent)

        self.txt_sympy = QLabel("SymPy: Ver. " + sympy.__version__, self)
        self.txt_sympy.setIndent(indent)

        self.txt_qt = QLabel("PyQt: Ver. " + QT_VERSION_STR, self)
        self.txt_qt.setIndent(indent)

        self.txt_matplotlib = QLabel("Matplotlib: Ver. " + matplotlib.__version__ + "\n     with " + latex_version(), self)
        self.txt_matplotlib.setIndent(indent)

        ver = sys.version.replace("\n", "").replace("[", "\n    [")
        self.txt_python = QLabel("\nPython: Ver. " + ver, self)

        if parent._multipie_loaded:
            self.txt_multipie = QLabel("MultiPie: Ver. " + parent._multipie_loaded, self)
            self.txt_multipie.setIndent(indent)

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok)
        self.buttonBox.accepted.connect(self.accept)

        self.gridLayout = QGridLayout(self)
        self.gridLayout.setContentsMargins(20, 20, 20, 20)
        self.gridLayout.setHorizontalSpacing(30)
        self.gridLayout.setVerticalSpacing(0)

        self.gridLayout.addWidget(self.icon, 0, 0, 10, 1)
        self.gridLayout.addWidget(self.lbl_qtdraw, 0, 1, 1, 1)
        self.gridLayout.addWidget(self.txt_copyright, 1, 1, 1, 1)
        self.gridLayout.addWidget(self.txt_pyvista, 2, 1, 1, 1)
        self.gridLayout.addWidget(self.txt_qt, 3, 1, 1, 1)
        self.gridLayout.addWidget(self.txt_pandas, 4, 1, 1, 1)
        self.gridLayout.addWidget(self.txt_matplotlib, 5, 1, 1, 1)
        self.gridLayout.addWidget(self.txt_numpy, 6, 1, 1, 1)
        self.gridLayout.addWidget(self.txt_sympy, 7, 1, 1, 1)
        self.gridLayout.addWidget(self.txt_python, 9, 1, 1, 1)
        self.gridLayout.addWidget(self.buttonBox, 11, 0, 1, 2)

        if parent._multipie_loaded:
            self.gridLayout.addWidget(self.txt_multipie, 8, 1, 1, 1)
