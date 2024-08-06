"""
Logging utility.

This module provides utilities for logging.
"""

import sys
import os
import time
import logging
from functools import wraps
from PySide6.QtWidgets import QWidget, QPlainTextEdit, QGridLayout, QFileDialog
from PySide6.QtGui import QFont
from qtdraw.util.qt_event_util import ExceptionHook


# ==================================================
class LogHandler(logging.Handler):
    # ==================================================
    def __init__(self, level=logging.DEBUG, stream=None, text_widget=None):
        """
        Log handler.

        Args:
            level (Level, optional): log level.
            stream (TextIO, optional): stream.
            text_widget (LogWidget, optional): text widget.

        Note:
            - if stream/text_widget is None, it is not used.
        """
        super().__init__()

        # set handler.
        fmt = "%(asctime)s | %(levelname)8s | %(message)s"
        date_fmt = "%Y-%m-%d %H:%M:%S"
        self.setLevel(level)
        logging.basicConfig(level=level, format=fmt, datefmt=date_fmt, handlers=[self], encoding="utf-8")
        self.header = False

        # set plain text widget.
        if text_widget is not None:
            self.text_widget = text_widget

        # set stream.
        self.stream = stream

    # ==================================================
    def emit(self, record):
        """
        Emit message.

        Args:
            record (LogRecord): log record.
        """
        if not self.header:
            header = " Date Time          | Level    | Message"
            if self.text_widget is not None:
                self.text_widget.append_text(header)
            if self.stream is not None:
                print(header, file=self.stream)
            self.header = True

        msg = self.format(record)
        if self.text_widget is not None:
            self.text_widget.append_text(msg)
        if self.stream is not None:
            print(msg, file=self.stream)


# ==================================================
def timer(func):
    """
    Timer decorater.

    Args:
        func (Function): function to decorate.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        logging.info(f"=== ({func.__name__}) begin === ")
        result = func(*args, **kwargs)
        end = time.time()
        logging.info(f"=== ({func.__name__}) end ({end - start:.7f} [s] elapsed) ===")
        return result

    return wrapper


# ==================================================
def start_logging(level=logging.DEBUG, stream=None, text_widget=None, hook=True):
    """
    Start logging.

    Args:
        level (Level, optional): logging level.
        stream (TextIO, optional): stream for logging.
        text_widget (LogWidget, optional): text widget.
        hook (bool, optional): exception hook ?

    Note:
        - stream is True, sys.stderr is used.
    """
    if stream is True:
        stream = sys.stderr
    log_handler = LogHandler(level=level, stream=stream, text_widget=text_widget)
    logging.getLogger().addHandler(log_handler)
    if hook:
        ExceptionHook()


# ==================================================
class LogWidget(QWidget):
    # ==================================================
    def __init__(self, title="log message", level=logging.DEBUG, stream=None, hook=True, parent=None):
        """
        Log widget.

        Args:
            title (str, optional): window title.
            level (Level, optional): log level.
            stream (TextIO, optional): stream for logging.
            hook (bool, optional): exception hook ?
            parent (QObject, optional): parent.

        Note:
            - if stream is True, sys.stderr is used.
            - if level is None, no logging.
        """
        super().__init__(parent)
        self.log = QPlainTextEdit(self)
        font = QFont("Monaco", 11)
        font.setStyleHint(QFont.TypeWriter)
        self.log.setFont(font)
        self.log.setReadOnly(True)
        if level is not None:
            start_logging(level, stream, self, hook)

        self.setWindowTitle(title)
        self.resize(640, 800)

        layout = QGridLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        layout.addWidget(self.log, 0, 0, 1, 1)

    # ==================================================
    def append_text(self, text):
        """
        Append text.

        Args:
            text (str): text.
        """
        self.log.appendPlainText(text)

    # ==================================================
    def set_text(self, text):
        """
        Set text.

        Args:
            text (str): text.
        """
        self.clear()
        self.append_text(text)

    # ==================================================
    def clear(self):
        """
        Clear log message.
        """
        self.log.clear()

    # ==================================================
    def save(self):
        """
        Save log message.
        """
        full = os.getcwd()
        filename, _ = QFileDialog.getSaveFileName(self, dir=full, filter="log (*.log)")
        if filename != "":
            with open(filename, "a") as f:
                print(self.log.plainText, file=f)
