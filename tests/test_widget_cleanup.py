# SPDX-License-Identifier: MPL-2.0
# Copyright (C) 2021- The QtDraw developers
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""
Regression tests for widgets left behind after closing a window.

Remaining widgets made every new window slower, because QApplication.setStyle and
setStyleSheet re-apply the style to all existing widgets.
"""

import os
import shutil
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest
import shiboken6
from PySide6.QtWidgets import QApplication, QMessageBox

from gui_helpers import process_deleted


def n_widgets():
    process_deleted()
    return len(QApplication.allWidgets())


def run_python(code):
    # a separate process, with only the widgets of the code. it was introduced for #197: there, a QtDraw window
    # left open (its close was cancelled) crashed later off-screen widgets on Linux; no_open_widgets prevents it.
    ret = subprocess.run(
        [sys.executable, "-c", textwrap.dedent(code)],
        capture_output=True,
        text=True,
        timeout=120,
        env={**os.environ, "QT_QPA_PLATFORM": "offscreen"},
    )
    assert ret.returncode == 0 and "OK" in ret.stdout, ret.stdout + ret.stderr


STANDALONE = """
import sys
from PySide6.QtCore import QCoreApplication, QEvent
from PySide6.QtWidgets import QApplication
from qtdraw.widget.qt_event_util import get_qt_application
from qtdraw.core.pyvista_widget import PyVistaWidget

app = get_qt_application()
errors = []
sys.excepthook = lambda *exc: errors.append(exc)


def n_widgets():
    QCoreApplication.sendPostedEvents(None, QEvent.DeferredDelete)
    return len(QApplication.allWidgets())


before = n_widgets()
"""


# ==================================================
def test_closed_qtdraw_is_deleted(qapp, tmp_path, monkeypatch):
    from qtdraw.core.qtdraw_app import QtDraw

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(QMessageBox, "question", lambda *args, **kwargs: QMessageBox.Discard)
    before = n_widgets()

    for i in range(1, 3):
        window = QtDraw()
        assert n_widgets() > before + i
        vtk_widget = window.pyvista_widget
        window.close()
        # the window, its dialogs and its VTK widget are deleted.
        assert n_widgets() == before
        assert not shiboken6.isValid(vtk_widget)


# ==================================================
def test_cancelled_close_keeps_qtdraw(qapp, tmp_path, monkeypatch):
    from qtdraw.core.qtdraw_app import QtDraw

    monkeypatch.chdir(tmp_path)
    window = QtDraw()
    window.pyvista_widget.add_site()  # an unsaved change.
    opened = n_widgets()

    monkeypatch.setattr(QMessageBox, "question", lambda *args, **kwargs: QMessageBox.Cancel)
    window.close()
    assert n_widgets() == opened
    window.pyvista_widget.add_site()  # still usable.
    assert len(window.pyvista_widget._data["site"].tolist()) == 2

    monkeypatch.setattr(QMessageBox, "question", lambda *args, **kwargs: QMessageBox.Discard)
    window.close()


# ==================================================
def test_closed_standalone_widget_is_deleted():
    # kept, each closed VTK widget used memory for the rest of the process (its signals hold it through Qt),
    # which exhausted the memory of the Linux CI runner.
    run_python(STANDALONE + """
import shiboken6

for i in range(2):
    w = PyVistaWidget(off_screen=True)
    w.add_site()
    w.open_tab_group_view()
    table = w._tab_group_view
    assert n_widgets() > before
    w.close()
    w.close()  # closing again before the deletion does nothing.
    assert n_widgets() == before  # the VTK widget and its data table are deleted.
    assert not shiboken6.isValid(w)
    assert not shiboken6.isValid(table)
assert not errors, errors
print("OK")
""")


# ==================================================
def test_data_table_is_deleted_when_closing_fails():
    run_python(STANDALONE + """
import shiboken6

w = PyVistaWidget(off_screen=True)
mathjax = w._mathjax
real_close = mathjax.close
closed = []


def fail():
    real_close()
    raise OSError("cannot write cache")


mathjax.close = fail
table = w._tab_group_view
real_table_close = table.close
table.close = lambda: (closed.append(True), real_table_close())
try:
    w.close()
except OSError as e:
    assert "cannot write cache" in str(e)  # the error is not hidden.
else:
    raise AssertionError("no error")
assert closed  # the data table is closed anyway,
assert n_widgets() == before  # and deleted, with the VTK widget.
assert not shiboken6.isValid(table)
assert not shiboken6.isValid(w)
assert not errors, errors
print("OK")
""")


# ==================================================
def test_closed_window_stops_logging(qapp, tmp_path, monkeypatch):
    import logging

    from qtdraw.core.qtdraw_app import QtDraw

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(QMessageBox, "question", lambda *args, **kwargs: QMessageBox.Discard)
    before = list(logging.getLogger().handlers)

    window = QtDraw()
    assert len(logging.getLogger().handlers) > len(before)
    window.close()
    n_widgets()

    assert logging.getLogger().handlers == before
    logging.getLogger().warning("after close")  # no handler writes to a deleted widget.


# ==================================================
def test_closing_twice_deletes_once(qapp, tmp_path, monkeypatch):
    from qtdraw.core.qtdraw_app import QtDraw

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(QMessageBox, "question", lambda *args, **kwargs: QMessageBox.Discard)
    before = n_widgets()

    window = QtDraw()
    window.close()
    window.close()  # before the deferred deletion.
    assert n_widgets() == before  # also the VTK widget.
    assert not shiboken6.isValid(window)


# ==================================================
def test_last_window_closed_in_event_loop():
    run_python("""
        import logging
        import sys
        from PySide6.QtCore import QTimer
        from PySide6.QtWidgets import QApplication, QMessageBox
        from qtdraw.widget.qt_event_util import get_qt_application
        from qtdraw.core.qtdraw_app import QtDraw

        app = get_qt_application()
        QMessageBox.question = lambda *args, **kwargs: QMessageBox.Discard
        window = QtDraw()
        window.show()
        destroyed = []
        window.destroyed.connect(lambda: destroyed.append(True))
        errors, timeout = [], []
        sys.excepthook = lambda *exc: errors.append(exc)
        QTimer.singleShot(500, window.close)
        QTimer.singleShot(30000, lambda: (timeout.append(True), app.quit()))  # safety net.
        app.exec()
        app.sendPostedEvents()
        assert not errors, errors
        assert not timeout, "closing the last window did not quit the application"
        assert destroyed, "window is not deleted"
        assert not logging.getLogger().handlers, logging.getLogger().handlers
        print("OK")
        """)


# ==================================================
def test_failing_close_in_event_loop_is_reported():
    run_python("""
        import sys
        from PySide6.QtCore import QTimer
        from PySide6.QtWidgets import QMessageBox
        from qtdraw.widget.qt_event_util import get_qt_application
        from qtdraw.core.qtdraw_app import QtDraw

        app = get_qt_application()
        QMessageBox.question = lambda *args, **kwargs: QMessageBox.Discard
        window = QtDraw()
        window.show()
        mathjax = window.pyvista_widget._mathjax
        real_close = mathjax.close

        def fail():
            real_close()
            raise OSError("cannot write cache")

        mathjax.close = fail
        destroyed, errors, timeout = [], [], []
        window.destroyed.connect(lambda: destroyed.append(True))
        window.pyvista_widget._tab_group_view.destroyed.connect(lambda: destroyed.append(True))
        sys.excepthook = lambda *exc: errors.append(exc[1])
        QTimer.singleShot(500, window.close)
        QTimer.singleShot(30000, lambda: (timeout.append(True), app.quit()))  # safety net.
        app.exec()
        app.sendPostedEvents()
        assert len(errors) == 1 and "cannot write cache" in str(errors[0]), errors
        assert not timeout, "closing the last window did not quit the application"
        assert len(destroyed) == 2, "window or data table is not deleted"
        print("OK")
        """)


# ==================================================
def test_temporary_widgets_are_deleted(tmp_path):
    # create_qtdraw_file, convert_qtdraw_v3 and loading a version-1 file use a temporary off-screen widget.
    # closed only, each remained for the rest of the process (its signals hold it through Qt).
    v1 = Path(__file__).parent / "data" / "compat" / "v1_1_0_sample_ver1.qtdw"
    src = tmp_path / v1.name
    shutil.copy(v1, src)
    run_python(STANDALONE + f"""
from PySide6.QtCore import QEventLoop, QTimer
sys.excepthook = lambda *exc: (errors.append(exc), sys.__excepthook__(*exc))  # with the traceback, for a failure.
from qtdraw.core.pyvista_widget import create_qtdraw_file, convert_qtdraw_v3

create_qtdraw_file({str(tmp_path / "new.qtdw")!r}, lambda w: w.add_site())
assert n_widgets() == before, "create_qtdraw_file"
convert_qtdraw_v3({str(src)!r})
assert n_widgets() == before, "convert_qtdraw_v3"

w = PyVistaWidget(off_screen=True)
opened = n_widgets()
w.load({str(src)!r})
assert n_widgets() == opened, "load a version-1 file"

# also in a running event loop, as from a menu.
loop = QEventLoop()
counts = []


def load():
    try:
        w.load({str(src)!r})
        counts.append(len(QApplication.allWidgets()))
    finally:
        loop.quit()


QTimer.singleShot(0, load)
loop.exec()
assert counts and counts[0] == opened, ("load in an event loop", counts, opened)
assert not errors, errors
print("OK")
""")
