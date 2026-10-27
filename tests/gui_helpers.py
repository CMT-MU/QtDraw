# SPDX-License-Identifier: MPL-2.0
# Copyright (C) 2021- The QtDraw developers
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""
Fixture and helpers for tests of the main window.
"""

import copy
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
def app(qapp, tmp_path, monkeypatch, request):
    """
    Main window, checked at the end of the test that the panel shows the status (see panel_out_of_date).

    A test that leaves the panel out of date on purpose (e.g. a value typed but not confirmed) is marked with
    @pytest.mark.panel_not_checked(reason).
    """
    from qtdraw.core.qtdraw_app import QtDraw

    monkeypatch.chdir(tmp_path)
    window = QtDraw()
    yield window
    if shiboken6.isValid(window):  # not yet closed (and deleted) by the test.
        out_of_date = {}
        try:
            if not window.pyvista_widget._closed and request.node.get_closest_marker("panel_not_checked") is None:
                out_of_date = panel_out_of_date(window)
        finally:
            monkeypatch.setattr(QMessageBox, "question", close_answer)
            window.close()
        if out_of_date:
            pytest.fail(f"the panel does not show the status, {{widget: (shown, status)}}: {out_of_date}")


# ==================================================
def panel_state(app):
    """
    Values shown in the panel and the View menu.

    Returns:
        - (dict) -- {name: value}, for every widget of the panel (attributes uc_*, view_*) and the View menu.
    """
    from PySide6.QtWidgets import QAbstractButton, QComboBox, QLabel, QLineEdit

    state = {}
    for name, widget in vars(app).items():
        if not name.startswith(("uc_", "view_")) or not shiboken6.isValid(widget):
            continue
        if isinstance(widget, QComboBox):
            state[name] = widget.currentText()
        elif isinstance(widget, QAbstractButton) and widget.isCheckable():
            state[name] = widget.isChecked()
        elif isinstance(widget, QLineEdit):
            state[name] = line_edit_value(widget)
        elif isinstance(widget, QLabel):
            state[name] = widget.text()
    for group in ["action_toggle", "action_axis", "action_cell"]:
        for value, act in getattr(app, group).items():
            state[f"{group}[{value}]"] = act.isChecked()
    return state


def line_edit_value(edit):
    """
    Value shown in a line edit.

    Note:
        - while it has focus, the accepted value is shown raw (e.g. 1.0 for 1.0000) until it is edited.
    """
    raw = edit.hasFocus() and not getattr(edit, "_edited", True) and edit.text() == getattr(edit, "_raw", None)
    return edit._validated if raw else edit.text()


def panel_out_of_date(app):
    """
    Values of the panel and the View menu that differ from the status of the drawing.

    Returns:
        - (dict) -- {name: (shown, status)}, empty if the panel shows the status.

    Note:
        - the expected values are those shown by the window from the status (_show_status), so the panel is
          brought up to date by the check. That every status is shown by it is checked in test_panel_status.py.
    """
    status = copy.deepcopy(app.pyvista_widget._status)
    shown = panel_state(app)
    app._show_status()
    expected = panel_state(app)
    assert app.pyvista_widget._status == status, "showing the status changed it"
    return {name: (shown[name], expected[name]) for name in shown if shown[name] != expected[name]}


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
