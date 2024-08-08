"""
Test for logging.

This module provides a test for logging.
"""

import logging
from qtdraw.util.qt_event_util import get_qt_application
from qtdraw.util.logging_util import timer, LogWidget


# ==================================================
def test_logging():

    class A:
        def __init__(self):
            super().__init__()

        @timer
        def f(self):
            """
            test function.
            """
            print("test.")

    @timer
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
