# SPDX-License-Identifier: MPL-2.0
# Copyright (C) 2021- The QtDraw developers
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""
Short messages in the message field on the left of the bottom bar, at the main steps; the version and copyright
stay on the right (#292).
"""

import logging
import warnings
from pathlib import Path

import pytest
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QMessageBox

from gui_helpers import app  # noqa: F401  (fixture)
from qtdraw.util.util import check_multipie


# ==================================================
def message(app):
    return app.status.text()


def settle(app):
    app._modified_timer.stop()
    app._settle()


# ==================================================
def test_version_on_the_right_and_no_message_at_start(app):
    assert "Version" in app.status_version.text() and "Copyright" in app.status_version.text()
    assert message(app) == ""


# ==================================================
def test_open_and_save_are_told(app, tmp_path):
    version = app.status_version.text()
    app.pyvista_widget.add_site(name="A")
    app.save(str(tmp_path / "a.qtdw"))
    assert message(app).startswith("write to ") and message(app).endswith("a.qtdw.")
    app.load(str(tmp_path / "a.qtdw"))
    assert message(app).startswith("read from ") and message(app).endswith("a.qtdw.")
    assert app.status_version.text() == version  # a message never replaces the version.


# ==================================================
def test_object_not_drawn_is_told(app):
    app.pyvista_widget.add_vector(name="v", length=0)
    assert message(app) == "vector 'v' is not drawn: its length is 0."


# ==================================================
def test_details_of_a_message_are_only_in_the_info_window(app):
    app.write_info("* first line of a message\n  a detail")
    app.write_info("  another detail")
    assert message(app) == "first line of a message"
    assert "another detail" in app.info_dialog.log.toPlainText()


# ==================================================
def log_from_qtdraw(level, text):
    """
    A log record made by the code of the qtdraw package.
    """
    import qtdraw

    path = str(Path(qtdraw.__file__).resolve().parent / "core" / "qtdraw_app.py")
    logging.getLogger().handle(logging.LogRecord("root", level, path, 1, text, None, None))


# ==================================================
def test_warnings_and_errors_are_told(app):
    log_from_qtdraw(logging.WARNING, "something to look at\nwith details")
    assert message(app) == "Warning: something to look at (see Window > Log)"
    log_from_qtdraw(logging.ERROR, "something wrong")
    assert message(app) == "Error: something wrong (see Window > Log)"
    log_from_qtdraw(logging.INFO, "not told")
    assert "not told" not in message(app)


# ==================================================
def test_warnings_of_others_are_only_in_the_log(app):
    app.show_message("kept")
    logging.error("Couldn't build the shader program.")  # e.g. VTK with a software renderer: not of QtDraw.
    warnings.warn("a deprecation of a library", DeprecationWarning)  # a Python warning.
    assert message(app) == "kept"
    log = app.logger.log.toPlainText()
    assert "Couldn't build the shader program." in log and "a deprecation of a library" in log


# ==================================================
def test_undo_and_redo_are_told(app):
    app.undo()
    assert message(app) == "Nothing to undo."
    app.pyvista_widget.add_site(name="A")
    settle(app)
    app.undo()
    assert message(app) == "Undo."
    app.redo()
    assert message(app) == "Redo."
    app.redo()
    assert message(app) == "Nothing to redo."


# ==================================================
def test_nonrepeat_is_told(app, monkeypatch):
    app.pyvista_widget.add_site(name="A")
    app.set_nonrepeat()
    assert message(app) == "repeated objects converted to those of the home cell."


# ==================================================
def test_message_is_cleared_after_a_while(app):
    app.show_message("short-lived", timeout=50)
    assert message(app) == "short-lived"
    QTest.qWait(200)
    assert message(app) == ""
    app.show_message("stays", timeout=0)
    QTest.qWait(100)
    assert message(app) == "stays"


# ==================================================
def test_long_message_does_not_widen_the_window(app):
    width = app.width()
    app.show_message("x" * 2000)
    QTest.qWait(10)
    assert app.width() == width
    assert app.status.toolTip() == "x" * 2000  # the whole message.


# ==================================================
def test_no_message_after_the_window_is_closed(qapp, tmp_path, monkeypatch):
    from qtdraw.core.qtdraw_app import QtDraw

    monkeypatch.chdir(tmp_path)
    window = QtDraw()
    handler = window._message_handler
    monkeypatch.setattr(QMessageBox, "question", lambda *a, **k: QMessageBox.Discard)
    window.close()
    assert handler not in logging.getLogger().handlers
    logging.warning("after the window is closed")  # no error.


# ==================================================
@pytest.mark.skipif(not check_multipie(), reason="MultiPie is not installed.")
def test_multipie_steps_are_told(app):
    w = app.pyvista_widget
    w.mp_set_group("D6h^1")
    assert message(app) == "MultiPie group D6h^1."
    w.mp_set_group("SG:191")
    assert message(app) == "MultiPie group D6h^1 (SG:191)."  # the name of a group given by its tag.
    w.mp_add_site("[1/3,2/3,0]")
    assert message(app) == "2 sites equivalent to [1/3,2/3,0] drawn."
    lst = w.mp_site_samb_list("[1/3,2/3,0]")
    w.mp_add_site_samb(lst[0])
    assert message(app) == f"site SAMB {lst[0]} drawn."
    lst = w.mp_vector_samb_list("[1/3,2/3,0]", "M")
    tag = next(v[0] for v in lst.values() if v).split(":")[0]
    w.mp_add_vector_samb_modulation(f"[[{tag}, 1, [1/2,0,0], cos]] : [2,2,1]")
    assert message(app).startswith("vector SAMB modulation drawn: ")
    w.mp_set_group("D4h")
    w.mp_add_vector_samb_modulation(f"[[{tag}, 1, [1/2,0,0], cos]] : [2,2,1]")  # a warning for a point group.
    assert message(app) == "Warning: modulation is not available for a point group (D4h): ignored. (see Window > Log)"
