"""
Test for PyVistaWidget.

This module provides a test for PyVistaWidget.
"""

from qtdraw.widget.qt_event_util import get_qt_application
from qtdraw.core.pyvista_widget import PyVistaWidget

app = get_qt_application()

widget = PyVistaWidget()

widget.show()
app.exec()
