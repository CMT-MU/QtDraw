"""
Control Qt event loop.

This module provides functions to control Qt event loop.
"""

import functools
from contextlib import contextmanager
import sys
import logging
import traceback as tb
from PySide6.QtCore import QObject, Signal, Qt
from PySide6.QtGui import QFont, QFontDatabase, QPalette, QColor
from PySide6.QtWidgets import QApplication

from qtdraw.core.pyvista_widget_setting import default_preference

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
    app.setFont(QFont(font_family(font), size))

    # use light-mode palette.
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(240, 240, 240))
    palette.setColor(QPalette.WindowText, Qt.black)
    palette.setColor(QPalette.Base, Qt.white)
    palette.setColor(QPalette.AlternateBase, QColor(233, 231, 227))
    palette.setColor(QPalette.ToolTipBase, Qt.white)
    palette.setColor(QPalette.ToolTipText, Qt.black)
    palette.setColor(QPalette.Text, Qt.black)
    palette.setColor(QPalette.Button, QColor(240, 240, 240))
    palette.setColor(QPalette.ButtonText, Qt.black)
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.HighlightedText, Qt.white)
    app.setPalette(palette)

    return app


# ==================================================
def font_family(name):
    """
    Font family available on this system.

    Args:
        name (str): font family name.

    Returns:
        - (str) -- name if it is installed, otherwise system default font family.
    """
    if name in QFontDatabase.families():
        return name
    return QFontDatabase.systemFont(QFontDatabase.GeneralFont).family()


# ==================================================
def font_style_sheet(name, size):
    """
    Style sheet for application font.

    Args:
        name (str): font family name.
        size (int): font size in point.

    Returns:
        - (str) -- style sheet.
    """
    return 'QWidget { font-family: "' + font_family(name) + '"; font-size: ' + f"{size}pt; }}"


# ==================================================
@contextmanager
def busy_cursor():
    """
    Show wait cursor during long operation.
    """
    QApplication.setOverrideCursor(Qt.WaitCursor)
    try:
        yield
    finally:
        QApplication.restoreOverrideCursor()


# ==================================================
def with_busy_cursor(func):
    """
    Decorator to show wait cursor while func is running.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        with busy_cursor():
            return func(*args, **kwargs)

    return wrapper


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
            try:
                from IPython.core import ultratb

                handler = ultratb.VerboseTB(color_scheme="NoColor", long_header=False)
                log_msg = handler.text(type, value, traceback)
                simple = ultratb.SyntaxTB(theme_name="NoColor").text(type, value, traceback)
            except ImportError:  # IPython is optional.
                log_msg = "".join(tb.format_exception(type, value, traceback))
                simple = "".join(tb.format_exception_only(type, value))
            log_msg += "\n" + bar
            simple = "\n" + bar + "\n" + simple + bar
            self.msg_signal.emit(log_msg)
            logging.critical(simple)

    # ==================================================
    def reset(self):
        """
        Reset exception hook.
        """
        sys.excepthook = sys.__excepthook__
