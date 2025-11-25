"""
Control Qt event loop.

This module provides functions to control Qt event loop.
"""

import sys
import logging
from IPython.core import ultratb
from PySide6.QtCore import QObject, Signal, Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication

from qtdraw.core.pyvista_widget_setting import default_preference
from qtdraw.core.qtdraw_info import __top_dir__

from qtdraw.widget.message_box import MessageBox


# ==================================================
def gui_qt():
    """
    Execute Qt GUI mode in IPython (if available).
    """
    try:
        from IPython import get_ipython
    except ImportError:
        get_ipython = lambda: False

    shell = get_ipython()

    if shell and getattr(shell, "enable_gui", None):
        if shell.active_eventloop != "qt6":
            shell.enable_gui("qt6")


# ==================================================
def get_qt_application():
    """
    Get Qt application.

    Returns:
        - (QApplication) -- Qt application.

    Note:
        - call this before super().__init__() in __init__() of QMainWindow class as follows.
            - self.app = get_qt_application()
            - ExceptionHook()
    """
    gui_qt()
    app = QApplication.instance() or QApplication(sys.argv)

    # for high-resolution setting.
    app.setAttribute(Qt.AA_EnableHighDpiScaling)
    app.setAttribute(Qt.AA_UseHighDpiPixmaps)

    # set general appearance.
    style = default_preference["general"]["style"]
    font = default_preference["general"]["font"]
    size = default_preference["general"]["size"]
    app.setStyle(style)
    app.setFont(QFont(font, size))

    return app


# ==================================================
class ExceptionHook(QObject):
    msg_signal = Signal(str)

    # ==================================================
    def __init__(self, parent=None):
        """
        Exception hook.

        Args:
            parent (QObject, optional): parent.

        Note:
            - call this before super().__init__() in __init__() of QMainWindow class as follows.
                - self.app = get_qt_application()
                - ExceptionHook()
        """
        super().__init__(parent)

        # hook the exception handler of the Python interpreter.
        sys.excepthook = self.hook

        # connection.
        self.msg_signal.connect(lambda x: MessageBox(x, "Exception Message"))

    # ==================================================
    def hook(self, type, value, traceback):
        """
        Callback for uncaught exceptions.

        Args:
            type (Any): type of exception.
            value (Any): arguments.
            traceback (TraceBack): traceback.
        """
        if issubclass(type, KeyboardInterrupt):
            sys.__excepthook__(type, value, traceback)  # ignore keyboard interrupt for console applications.
        else:
            bar = "---------------------------------------------------------------------------"
            handler = ultratb.VerboseTB(color_scheme="NoColor", long_header=False)
            log_msg = handler.text(type, value, traceback)
            log_msg += "\n" + bar
            simple = "\n" + bar + "\n" + ultratb.SyntaxTB(theme_name="NoColor").text(type, value, traceback) + bar
            self.msg_signal.emit(log_msg)
            logging.critical(simple)

    # ==================================================
    def reset(self):
        """
        Reset exception hook.
        """
        sys.excepthook = sys.__excepthook__
