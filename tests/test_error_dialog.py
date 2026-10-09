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


# ==================================================
def summary_of(error):
    from qtdraw.widget.qt_event_util import error_summary

    try:
        raise error
    except BaseException as e:
        return error_summary(type(e), e)


def test_error_summary_is_short():
    assert summary_of(ValueError("bad value")) == "ValueError: bad value"
    assert summary_of(ValueError("first line\nsecond\nthird")) == "ValueError: first line ..."
    assert summary_of(KeyError("missing")) == "KeyError: 'missing'"
    assert summary_of(RuntimeError()) == "RuntimeError"
    long = summary_of(ValueError("x" * 1000))
    assert long.startswith("ValueError: xxx") and long.endswith("...") and len(long) < 320
    try:
        compile("1 +", "<input>", "exec")
    except SyntaxError as e:
        from qtdraw.widget.qt_event_util import error_summary

        assert error_summary(SyntaxError, e) == f"SyntaxError: {e.msg}"


# ==================================================
def test_message_signal_still_sends_full_message(qapp, monkeypatch):
    from qtdraw.widget import qt_event_util

    monkeypatch.setattr(qt_event_util, "show_error", lambda *args: None)
    hook = qt_event_util.ExceptionHook()
    monkeypatch.setattr(sys, "excepthook", sys.__excepthook__)
    messages = []
    hook.msg_signal.connect(messages.append)  # one-argument listeners keep working.
    try:
        broken_function()
    except ZeroDivisionError:
        hook.hook(*sys.exc_info())

    assert "Traceback" in messages[0] and "broken_function" in messages[0]


# ==================================================
def test_each_dialog_gets_its_own_summary(qapp, monkeypatch):
    from qtdraw.widget import qt_event_util

    shown = []
    monkeypatch.setattr(qt_event_util, "show_error", lambda *args: shown.append(args))
    hook = qt_event_util.ExceptionHook()
    monkeypatch.setattr(sys, "excepthook", sys.__excepthook__)

    # another exception while the first one is being reported, e.g. in a listener.
    def nested(details):
        if "ZeroDivisionError" in details and len(shown) == 0:
            try:
                raise KeyError("inner")
            except KeyError:
                hook.hook(*sys.exc_info())

    hook.msg_signal.disconnect(hook._show_error)
    hook.msg_signal.connect(nested)  # runs before the dialog of the first exception.
    hook.msg_signal.connect(hook._show_error)
    try:
        broken_function()
    except ZeroDivisionError:
        hook.hook(*sys.exc_info())

    pairs = {summary.split(":")[0]: details for summary, details, _ in shown}
    assert set(pairs) == {"KeyError", "ZeroDivisionError"}
    assert "KeyError" in pairs["KeyError"] and "ZeroDivisionError" in pairs["ZeroDivisionError"]
    assert hook._summary == {}  # nothing is left behind.
