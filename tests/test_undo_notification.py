"""
Tests for change notification used by undo (#182).
"""

import copy
from pathlib import Path

from PySide6.QtCore import QCoreApplication

from qtdraw.parser.xsf import extract_data_xsf

EXAMPLES = Path(__file__).resolve().parents[1] / "docs" / "src" / "examples"


def test_pending_rename_can_run_now(widget):
    widget.add_site(name="A")
    model = widget._data["site"]
    index = model.index(0, 0)
    model.setData(index, "B")  # deferred by a timer.
    assert widget.get_data_dict()["site"][0][0] == "A"
    model.run_pending_renames()
    assert widget.get_data_dict()["site"][0][0] == "B"
    QCoreApplication.processEvents()  # the queued callback does nothing now.
    assert [r[0] for r in widget.get_data_dict()["site"]] == ["B"]


def test_status_setters_notify(widget):
    count = []
    widget.document_changed.connect(lambda: count.append(1))
    widget.set_origin("[0.1,0,0]")
    widget.set_crystal("hexagonal")
    widget.set_unit_cell({"a": 2.0})
    widget.set_clip(True)
    widget.set_range("[0,0,0]", "[2,1,1]")
    widget.set_repeat(False)
    assert len(count) >= 6


def test_given_grid_is_copied(widget):
    grid = extract_data_xsf(str(EXAMPLES / "Si.xsf"))
    widget.add_isosurface(data=("grid", grid), value=[0.01])
    stored = widget._isosurface_data["grid"]
    assert stored is not grid
    before = copy.deepcopy(stored["data"])
    grid["data"].clear()  # the caller changes its own data afterwards.
    assert stored["data"] == before


def test_several_pending_renames_are_all_run(widget):
    widget.add_site(name="A")
    widget.add_site(name="B")
    model = widget._data["site"]
    model.setData(model.index(1, 0), "Y")  # deferred.
    model.setData(model.index(0, 0), "X")  # deferred; the first rename resets the model.
    model.run_pending_renames()
    QCoreApplication.processEvents()
    assert sorted(r[0] for r in widget.get_data_dict()["site"]) == ["X", "Y"]


def test_pending_rename_of_a_group_moves_all_its_rows(widget):
    widget.add_site(name="A", position="[0,0,0]")
    widget.add_site(name="A", position="[0.5,0,0]")  # grouped under "A".
    widget.add_site(name="C")
    model = widget._data["site"]
    model.setData(model.index(1, 0), "D")  # deferred.
    model.setData(model.index(0, 0), "B")  # the group "A".
    model.run_pending_renames()
    assert sorted(r[0] for r in widget.get_data_dict()["site"]) == ["B", "B", "D"]


def test_pending_rename_of_a_child_after_its_group(widget):
    widget.add_site(name="A", position="[0,0,0]")
    widget.add_site(name="A", position="[0.5,0,0]")  # grouped under "A".
    model = widget._data["site"]
    parent = model.index(0, 0)
    model.setData(parent, "B")  # the group, deferred.
    model.setData(model.index(1, 0, parent), "C")  # one of its rows, deferred.
    model.run_pending_renames()
    assert sorted(r[0] for r in widget.get_data_dict()["site"]) == ["B", "C"]
