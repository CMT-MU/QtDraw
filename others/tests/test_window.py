"""
Test for minimal window.

This module provides a test for window.
"""

import logging
from qtdraw.core.pyvista_widget import Window

app = Window(logging.DEBUG)
app.show()
app.app.exec()
