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
    # discard unsaved changes, or confirm "Quit QtDraw ?".
    return QMessageBox.Discard if buttons & QMessageBox.Discard else QMessageBox.Ok


def answer(monkeypatch, button):
    asked = []

    def question(*args, **kwargs):
        asked.append(args)
        return button

    monkeypatch.setattr(QMessageBox, "question", question)
    return asked
