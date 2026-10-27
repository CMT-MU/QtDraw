# SPDX-License-Identifier: MPL-2.0
# Copyright (C) 2021- The QtDraw developers
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

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
