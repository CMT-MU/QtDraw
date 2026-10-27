# SPDX-License-Identifier: MPL-2.0
# Copyright (C) 2021- The QtDraw developers
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""
Test for minimal window.

This module provides a test for window.
"""

import logging
from qtdraw.core.pyvista_widget import Window

app = Window(logging.DEBUG)
app.show()
app.app.exec()
