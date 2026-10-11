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
