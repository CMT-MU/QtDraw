# SPDX-License-Identifier: MPL-2.0
# Copyright (C) 2021- The QtDraw developers
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""
Test for logging.

This module provides a test for logging.
"""

import logging

from qtdraw.widget.qt_event_util import get_qt_application
from qtdraw.widget.logging_util import LogWidget


# ==================================================
def test_logging():

    class A:
        def __init__(self):
            super().__init__()

        def f(self):
            """
            test function.
            """
            print("test.")

    def x():
        print("x test")
        return 5

    app = get_qt_application()
    win = LogWidget()

    logging.debug("debug.")
    logging.info("info.")
    logging.warning("warning.")
    logging.error("error.")
    logging.critical("critial error.")

    a = A()
    a.f()
    print(x())

    win.show()
    app.exec()


# ================================================== main
test_logging()
