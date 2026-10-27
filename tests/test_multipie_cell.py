# SPDX-License-Identifier: MPL-2.0
# Copyright (C) 2021- The QtDraw developers
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""
The cell follows the crystal of the MultiPie group, also without the main window (#228).
"""

import pytest
from PySide6.QtWidgets import QMessageBox

from gui_helpers import app, answer  # noqa: F401  (fixture and helper)
from qtdraw.util.util import check_multipie

pytestmark = pytest.mark.skipif(not check_multipie(), reason="MultiPie is not installed.")


def cell(widget):
    return widget._status["crystal"], widget._status["cell"]["gamma"]


# ==================================================
@pytest.mark.parametrize(
    "group, crystal, gamma", [("D6h", "hexagonal", 120.0), ("D3^4", "trigonal", 120.0), ("Oh", "cubic", 90.0)]
)
def test_group_sets_crystal(widget, group, crystal, gamma):
    widget.mp_set_group(group)
    assert cell(widget) == (crystal, gamma)


# ==================================================
def test_group_sets_crystal_as_main_window(widget, app):
    widget.mp_set_group("D6h")
    app.mp_set_group("D6h")
    assert cell(widget) == cell(app.pyvista_widget)


# ==================================================
def test_opened_file_keeps_its_cell(widget, app, tmp_path, monkeypatch):
    widget.mp_set_group("D3^4")
    widget.set_unit_cell({"a": 4.458, "c": 5.925})
    widget.add_site(position="[1/3,0,0]")
    widget.save(str(tmp_path / "a.qtdw"))
    saved = dict(widget._status["cell"])

    widget.load(str(tmp_path / "a.qtdw"))
    assert widget._status["cell"] == saved

    answer(monkeypatch, QMessageBox.Discard)
    app.load_file(str(tmp_path / "a.qtdw"))
    assert app.pyvista_widget._status["crystal"] == "trigonal"
    assert app.pyvista_widget._status["cell"] == saved


# ==================================================
def test_group_of_the_same_crystal_keeps_cell(widget, monkeypatch):
    widget.mp_set_group("D6h")
    widget.set_unit_cell({"a": 2.0, "c": 3.0})
    calls = []
    monkeypatch.setattr(widget, "set_unit_cell", lambda *args, **kwargs: calls.append(args))
    widget.mp_set_group("C6v")  # also hexagonal: the cell is not set (nor drawn) again.
    assert calls == [] and widget._status["cell"]["a"] == 2.0 and widget._status["cell"]["c"] == 3.0


# ==================================================
def test_main_window_sets_cell_once(app, monkeypatch):
    widget = app.pyvista_widget
    calls = []
    original = widget.set_unit_cell
    monkeypatch.setattr(widget, "set_unit_cell", lambda *args, **kwargs: calls.append(args) or original(*args, **kwargs))
    app.mp_set_group("D6h")
    assert len(calls) == 1 and cell(widget) == ("hexagonal", 120.0)
    assert app.uc_combo_crystal.currentText() == "hexagonal"  # the panel shows it.


# ==================================================
@pytest.mark.parametrize(
    "crystal, custom",
    [("hexagonal", {"a": 2.5, "c": 4.0}), ("monoclinic", {"a": 2.0, "b": 3.0, "c": 4.0, "beta": 100.0})],
)
def test_opened_file_keeps_its_crystal_also_of_another_group(widget, tmp_path, crystal, custom):
    widget.mp_set_group("Oh")
    widget.set_crystal(crystal)  # chosen after the group, as some files of QtDraw 2.0 have.
    widget.set_unit_cell(custom)
    saved = (widget._status["crystal"], dict(widget._status["cell"]), widget.A_matrix.copy())
    widget.save(str(tmp_path / "a.qtdw"))
    widget.mp_set_group("Oh")
    assert cell(widget) == ("cubic", 90.0)

    widget.load(str(tmp_path / "a.qtdw"))  # as the release opens it.
    assert (widget._status["crystal"], widget._status["cell"]) == saved[:2]
    assert widget.A_matrix == pytest.approx(saved[2])
    assert widget._mp_data.status["group"]["tag"] == "Oh"

    snapshot = widget.document_snapshot()
    widget.mp_set_group("D6h")
    widget.restore_document(snapshot)  # undo.
    assert (widget._status["crystal"], widget._status["cell"]) == saved[:2]
    assert widget.A_matrix == pytest.approx(saved[2])


# ==================================================
@pytest.mark.parametrize("dialog_open", [False, True])
def test_main_window_opens_file_with_its_crystal(widget, app, tmp_path, monkeypatch, dialog_open):
    widget.mp_set_group("Oh")
    widget.set_crystal("hexagonal")  # another crystal than the group's (#238).
    widget.set_unit_cell({"a": 2.5, "c": 4.0})
    widget.add_site(position="[1/3,2/3,0]")
    saved = (widget._status["crystal"], dict(widget._status["cell"]), widget.A_matrix.copy())
    widget.save(str(tmp_path / "a.qtdw"))
    if dialog_open:
        app.mp_set_group("D6h")  # the dialog is open already.

    answer(monkeypatch, QMessageBox.Discard)
    app.load_file(str(tmp_path / "a.qtdw"))
    pvw = app.pyvista_widget
    assert (pvw._status["crystal"], pvw._status["cell"]) == saved[:2]
    assert pvw.A_matrix == pytest.approx(saved[2])
    assert app.uc_combo_crystal.currentText() == "hexagonal"  # the panel shows the crystal of the file.
    assert pvw._mp_data.status["group"]["tag"] == "Oh"
    assert app.multipie_dialog._sub_panel.combo_crystal_type.currentText() == "cubic"  # the dialog shows the group.
    assert not app.isWindowModified()  # opened as saved.


# ==================================================
def test_main_window_opens_file_of_space_group_in_open_dialog(app, tmp_path, monkeypatch):
    from PySide6.QtWidgets import QApplication

    app.mp_set_group("Oh^1")  # a space group: axis on, cell single.
    app.pyvista_widget.save(str(tmp_path / "a.qtdw"))
    app.mp_set_group("D6h")  # the dialog shows another group.

    answer(monkeypatch, QMessageBox.Discard)
    app.load_file(str(tmp_path / "a.qtdw"))
    QApplication.processEvents()
    pvw, sub = app.pyvista_widget, app.multipie_dialog._sub_panel
    assert cell(pvw) == ("cubic", 90.0) and pvw._mp_data._type == "SG"
    assert sub.combo_crystal_type.currentText() == "cubic" and sub.combo_group_type.currentIndex() == 1
    assert sub.combo_group.currentIndex() == pvw._mp_data._idx  # the group of the file is chosen.
    assert "Oh^1" in sub.label_sg_name.text()
    status = pvw._status
    assert (app.view_combo_axis.currentText(), app.view_combo_cell.currentText()) == (status["axis_type"], status["cell_mode"])
    assert not app.isWindowModified()
