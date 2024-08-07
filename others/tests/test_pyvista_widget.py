from qtdraw.util.qt_event_util import get_qt_application
from qtdraw.core.pyvista_widget import PyVistaWidget
from PySide6.QtWidgets import QWidget, QMainWindow, QVBoxLayout

app = get_qt_application()
win = QMainWindow()
panel = QWidget(parent=win)
widget = PyVistaWidget(parent=panel)
layout = QVBoxLayout(panel)
layout.addWidget(widget)
win.setCentralWidget(panel)
widget.add_site()
win.show()
app.exec()
