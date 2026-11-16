# SPDX-License-Identifier: MPL-2.0
# Copyright (C) 2021- The QtDraw developers
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""
Warnings and errors are recorded in the Log window (#291), with the level set on QtDraw's own log handler, not on
the root logger.
"""

import logging
import warnings

import pytest
import shiboken6
from PySide6.QtWidgets import QMessageBox

from gui_helpers import app, process_deleted  # noqa: F401  (fixture and helper)
from qtdraw.util.util import check_multipie


# ==================================================
def log(app):
    return app.logger.log.toPlainText()


# ==================================================
def test_warnings_and_errors_are_in_the_log(app):
    logging.warning("a warning for the log")
    logging.error("an error for the log")
    logging.info("an info, not for the log")
    text = log(app)
    assert "WARNING | a warning for the log" in text
    assert "ERROR | an error for the log" in text
    assert "an info, not for the log" not in text  # log_level is "error": nothing below warnings.
    assert not app.logger.isVisible()  # a warning does not open the Log window.


# ==================================================
def test_python_warnings_are_in_the_log(app):
    warnings.warn("a Python warning for the log", UserWarning)
    assert "a Python warning for the log" in log(app)


# ==================================================
def test_info_window_keeps_only_messages(app):
    logging.warning("not in the Info window")
    app.write_info("* a message for the Info window")
    info = app.info_dialog.log.toPlainText()
    assert "* a message for the Info window" in info
    assert "not in the Info window" not in info


# ==================================================
def test_root_logger_is_not_changed(qapp, tmp_path, monkeypatch):
    from qtdraw.core.qtdraw_app import QtDraw

    root = logging.getLogger()
    before = root.level
    monkeypatch.chdir(tmp_path)
    window = QtDraw()
    try:
        assert root.level == before  # the level is set on the handler of the Log window only.
    finally:
        monkeypatch.setattr(QMessageBox, "question", lambda *a, **k: QMessageBox.Discard)
        window.close()
    process_deleted()
    assert root.level == before


# ==================================================
def test_debug_level_is_recorded_and_restored(qapp, tmp_path, monkeypatch):
    from qtdraw.core.pyvista_widget_setting import widget_detail
    from qtdraw.core.qtdraw_app import QtDraw

    root = logging.getLogger()
    monkeypatch.setattr(root, "level", logging.WARNING)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setitem(widget_detail, "log_level", "debug")
    window = QtDraw()
    try:
        logging.debug("a debug message for the log")
        assert "a debug message for the log" in window.logger.log.toPlainText()  # asked for by log_level.
    finally:
        monkeypatch.setattr(QMessageBox, "question", lambda *a, **k: QMessageBox.Discard)
        if shiboken6.isValid(window):
            window.close()
    process_deleted()
    assert root.level == logging.WARNING  # restored when the Log window is deleted.


# ==================================================
@pytest.mark.skipif(not check_multipie(), reason="MultiPie is not installed.")
def test_warning_of_qtdraw_is_in_the_log(app):
    w = app.pyvista_widget
    w.mp_set_group("D4h")
    lst = w.mp_vector_samb_list("[1,0,0]", "M")
    tag = next(v[0] for v in lst.values() if v).split(":")[0]
    w.mp_add_vector_samb_modulation(f"[[{tag}, 1, [1/2,0,0], cos]] : [2,2,1]")  # ignored for a point group.
    assert "modulation is not available for a point group (D4h): ignored." in log(app)
