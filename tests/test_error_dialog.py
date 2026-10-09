"""
Regression tests for the error dialog (#182): a short message, with the traceback behind "Show Details...".
"""

import sys

from PySide6.QtWidgets import QMessageBox


def broken_function():
    return 1 / 0


# ==================================================
def test_show_error_puts_traceback_in_details(qapp, monkeypatch):
    from qtdraw.widget import message_box

    shown = []
    monkeypatch.setattr(QMessageBox, "exec", lambda self: shown.append(self))
    message_box.show_error("ValueError: bad", "Traceback ...\nValueError: bad", "Exception Message")

    box = shown[0]
    assert box.text() == "ValueError: bad"
    assert box.detailedText() == "Traceback ...\nValueError: bad"
    if sys.platform != "darwin":  # macOS shows no title for message boxes.
        assert box.windowTitle() == "Exception Message"
    assert box.icon() == QMessageBox.Critical


# ==================================================
def test_exception_hook_shows_short_message(qapp, monkeypatch):
    from qtdraw.widget import qt_event_util

    shown = []
    monkeypatch.setattr(qt_event_util, "show_error", lambda *args: shown.append(args))
    hook = qt_event_util.ExceptionHook()
    monkeypatch.setattr(sys, "excepthook", sys.__excepthook__)  # restore after the test.
    try:
        broken_function()
    except ZeroDivisionError:
        hook.hook(*sys.exc_info())

    summary, details, title = shown[0]
    assert summary == "ZeroDivisionError: division by zero"  # one line, without the traceback.
    assert "broken_function" in details and "ZeroDivisionError" in details
    assert title == "Exception Message"
