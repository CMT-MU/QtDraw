# SPDX-License-Identifier: MPL-2.0
# Copyright (C) 2021- The QtDraw developers
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""
The panel and the View menu show the axis and cell display that a MultiPie group sets (#216).
"""

import pytest
from PySide6.QtWidgets import QMessageBox

from gui_helpers import app, answer  # noqa: F401  (fixture and helper)
from qtdraw.util.util import check_multipie

pytestmark = pytest.mark.skipif(not check_multipie(), reason="MultiPie is not installed.")


def shown(app):
    """
    Axis and cell display in the status, the panel and the View menu.
    """
    status = app.pyvista_widget._status
    checked = lambda actions: [value for value, act in actions.items() if act.isChecked()]
    return {
        "status": (status["axis_type"], status["cell_mode"]),
        "panel": (app.view_combo_axis.currentText(), app.view_combo_cell.currentText()),
        "menu": (*checked(app.action_axis), *checked(app.action_cell)),
    }


def assert_shown(app, axis, cell):
    assert shown(app) == {"status": (axis, cell), "panel": (axis, cell), "menu": (axis, cell)}


# ==================================================
def test_point_group_set_from_python(app):
    assert_shown(app, "on", "single")
    app.mp_set_group("Ci")
    assert_shown(app, "full", "off")


# ==================================================
def test_group_set_on_the_widget(app):
    app.pyvista_widget.mp_set_group("Ci")
    assert_shown(app, "full", "off")
    app.pyvista_widget.mp_set_group("Oh^1")  # a space group shows the cell again.
    assert_shown(app, "on", "single")


# ==================================================
def test_group_set_in_the_dialog(app):
    app.mp_set_group("Oh^1")
    combo = app.multipie_dialog._sub_panel.combo_group_type
    combo.setCurrentIndex(0)  # a point group.
    assert app.pyvista_widget._mp_data._type == "PG"
    assert_shown(app, "full", "off")


# ==================================================
def test_file_with_group_opened(app, tmp_path, monkeypatch):
    app.pyvista_widget.mp_set_group("Ci")
    app.pyvista_widget.save(str(tmp_path / "ci.qtdw"))
    app.pyvista_widget.mp_set_group("Oh^1")
    assert_shown(app, "on", "single")

    answer(monkeypatch, QMessageBox.Discard)
    app.load_file(str(tmp_path / "ci.qtdw"))
    assert_shown(app, "full", "off")


# ==================================================
def test_panel_still_sets_the_display(app):
    app.mp_set_group("Ci")
    app.view_combo_axis.setCurrentText("on")  # the panel works from the shown values.
    app.view_combo_cell.setCurrentText("single")
    assert_shown(app, "on", "single")


# ==================================================
def test_shown_without_applying_again(app, monkeypatch):
    pvw = app.pyvista_widget
    pvw.set_axis("axis")  # changed on the widget, e.g. from Python.
    pvw.set_cell("all")
    calls = []
    monkeypatch.setattr(pvw, "set_axis", lambda *a, **k: calls.append("axis"))
    monkeypatch.setattr(pvw, "set_cell", lambda *a, **k: calls.append("cell"))
    pvw.document_changed.emit()
    assert_shown(app, "axis", "all")
    assert calls == []  # not drawn again.


# ==================================================
def test_shown_after_undo_and_redo(app):
    def settle():
        app._modified_timer.stop()
        app._settle()

    app.mp_set_group("Oh^1")
    settle()
    app.mp_set_group("Ci")
    settle()
    for move in (app.undo, app.redo, app.undo):
        move()
        st = app.pyvista_widget._status
        assert_shown(app, st["axis_type"], st["cell_mode"])
