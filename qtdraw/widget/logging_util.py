# SPDX-License-Identifier: MPL-2.0
# Copyright (C) 2021- The QtDraw developers
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""
Logging utility.

This module provides utilities for logging.
"""

import sys
import os
import logging
from PySide6.QtWidgets import QWidget, QPlainTextEdit, QGridLayout, QFileDialog
from PySide6.QtGui import QFont

from qtdraw.widget.qt_event_util import ExceptionHook


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
            - the level and the format are set on this handler only, not on the root logger (no basicConfig), so
              that the logging of other libraries in the process is not changed.
        """
        super().__init__()

        # set handler.
        fmt = "%(asctime)s | %(levelname)8s | %(message)s"
        date_fmt = "%Y-%m-%d %H:%M:%S"
        self.setLevel(level)
        self.setFormatter(logging.Formatter(fmt, datefmt=date_fmt))
        self.header = False
        self.text_widget = None

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
def start_logging(level=logging.DEBUG, stream=None, text_widget=None, hook=True):
    """
    Start logging.

    Args:
        level (Level, optional): logging level.
        stream (TextIO, optional): stream for logging.
        text_widget (LogWidget, optional): text widget.
        hook (bool, optional): exception hook ?

    Returns:
        - (LogHandler) -- log handler added to the root logger.

    Note:
        - stream is True, sys.stderr is used.
        - the root logger is changed only when the level is lower than its own (e.g. debug), and stop_logging()
          restores it.
    """
    if stream is True:
        stream = sys.stderr
    log_handler = LogHandler(level=level, stream=stream, text_widget=text_widget)
    root = logging.getLogger()
    root.addHandler(log_handler)
    log_handler.root_level = None  # level of the root logger before, if it is changed.
    if level < root.getEffectiveLevel():  # a lower level asked for, e.g. debug: let the records reach the handler.
        log_handler.root_level = root.level
        root.setLevel(level)
    if hook:
        ExceptionHook()

    return log_handler


# ==================================================
def stop_logging(log_handler):
    """
    Stop logging to a handler of start_logging(), and restore the level of the root logger if it was changed.

    Args:
        log_handler (LogHandler): log handler.
    """
    root = logging.getLogger()
    root.removeHandler(log_handler)
    if getattr(log_handler, "root_level", None) is not None:
        root.setLevel(log_handler.root_level)
        log_handler.root_level = None


# ==================================================
class LogWidget(QWidget):
    # ==================================================
    def __init__(self, parent=None, title="log message", level=logging.DEBUG, stream=None, hook=True):
        """
        Log widget.

        Args:
            parent (QObject, optional): parent.
            title (str, optional): window title.
            level (Level, optional): log level.
            stream (TextIO, optional): stream for logging.
            hook (bool, optional): exception hook ?

        Note:
            - if stream is True, sys.stderr is used.
            - if level is None, no logging.
            - the log handler is removed from the root logger when the widget is deleted (see stop_logging).
        """
        super().__init__(parent)
        self.log = QPlainTextEdit(self)
        font = QFont("Monaco", 11)
        font.setStyleHint(QFont.TypeWriter)
        self.log.setFont(font)
        self.log.setReadOnly(True)
        if level is not None:
            handler = start_logging(level, stream, self, hook)
            # stop logging to this widget when it is deleted.
            self.destroyed.connect(lambda: stop_logging(handler))

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
