"""
Fixture and helpers for tests of the main window.
"""

import sys
import traceback

import pytest
import shiboken6
from PySide6.QtCore import QCoreApplication, QEvent
from PySide6.QtWidgets import QMessageBox


# ==================================================
def process_deleted():
    """
    Delete widgets scheduled for deletion (deleteLater), as the event loop would.

    Errors are reported as a test failure instead of being shown in a (blocking) message box.
    """
    if QCoreApplication.instance() is None:
        return
    errors = []
    hook = sys.excepthook
    sys.excepthook = lambda *exc: errors.append("".join(traceback.format_exception(*exc)))
    try:
        QCoreApplication.sendPostedEvents(None, QEvent.DeferredDelete)
    finally:
        sys.excepthook = hook
    if errors:
        pytest.fail("error while deleting widgets:\n" + "\n".join(errors))


# ==================================================
def close_open_widgets():
    """
    Close the drawings left open, windows without saving.

    Returns:
        - (list) -- descriptions of the drawings that were open, [str].

    Note:
        - on Linux with Mesa and the off-screen Qt platform, a window left open breaks the rendering of
          off-screen widgets created later in the same process, and its next render crashes (#197).
    """
    from PySide6.QtWidgets import QApplication
    from qtdraw.core.pyvista_widget import PyVistaWidget

    if QApplication.instance() is None:
        return []
    left = []
    for widget in QApplication.allWidgets():
        if not isinstance(widget, PyVistaWidget) or not shiboken6.isValid(widget) or widget._closed:
            continue
        window = widget.window()
        errors = []
        if window is widget:
            left.append(f"{type(widget).__name__} (off_screen={widget._off_screen})")
        else:
            left.append(f"{type(window).__name__} window '{window.windowTitle()}'")
            question = QMessageBox.question
            QMessageBox.question = close_answer
            try:
                window.close()
            except Exception as e:  # an error does not keep the widget and the others open.
                errors.append(e)
            finally:
                QMessageBox.question = question
        if not widget._closed:  # e.g. the window refused to close.
            try:
                widget.close()
            except Exception as e:
                errors.append(e)
        if errors:
            left[-1] += " (error while closing: " + "; ".join(f"{type(e).__name__}: {e}" for e in errors) + ")"
    return left


# ==================================================
@pytest.fixture
def app(qapp, tmp_path, monkeypatch):
    from qtdraw.core.qtdraw_app import QtDraw

    monkeypatch.chdir(tmp_path)
    window = QtDraw()
    yield window
    if shiboken6.isValid(window):  # not yet closed (and deleted) by the test.
        monkeypatch.setattr(QMessageBox, "question", close_answer)
        window.close()


def close_answer(parent, title, text, buttons, *args):
    # close without saving.
    return QMessageBox.Discard if buttons & QMessageBox.Discard else QMessageBox.Ok


def answer(monkeypatch, button):
    asked = []

    def question(*args, **kwargs):
        asked.append(args)
        return button

    monkeypatch.setattr(QMessageBox, "question", question)
    return asked
