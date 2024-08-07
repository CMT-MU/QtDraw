import pyvista as pv
from PySide6.QtWidgets import QApplication, QMainWindow, QFrame, QVBoxLayout
from pyvistaqt import QtInteractor
from pyvistaqt.utils import _setup_application, _setup_ipython
from pyvistaqt.window import MainWindow


class PyVistaWidget(QtInteractor):
    def __init__(self, app=None):
        self._closed = True
        self.ipython = _setup_ipython()
        self.app = _setup_application(app)
        self.app_window = MainWindow()
        self.frame = QFrame(parent=self.app_window)
        self.frame.setFrameStyle(QFrame.NoFrame)
        vlayout = QVBoxLayout()
        super().__init__(parent=self.frame, off_screen=False)
        assert not self._closed
        vlayout.addWidget(self)
        self.frame.setLayout(vlayout)
        self.app_window.setCentralWidget(self.frame)
        self.app_window.show()


app = QApplication([])

plotter = PyVistaWidget(app=app)
plotter.add_mesh(pv.Sphere())

app.exec()
