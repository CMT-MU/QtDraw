from qtdraw.sandbox.qt_event_util import get_qt_application
from qtdraw.sandbox.pyvista_widget import PyVistaWidget

app = get_qt_application()

widget = PyVistaWidget()

widget.show()
app.exec()
