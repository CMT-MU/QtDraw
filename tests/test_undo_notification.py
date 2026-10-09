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


def test_pending_rename_targets_its_own_row(widget):
    widget.add_isosurface(name="A")  # no data: no actor, otherwise the same rows.
    widget.add_isosurface(name="B")
    model = widget._data["isosurface"]
    model.setData(model.index(1, 0), "C")  # deferred.
    model.run_pending_renames()
    assert sorted(r[0] for r in widget.get_data_dict()["isosurface"]) == ["A", "C"]


def test_dropped_pending_rename_is_reported(widget, caplog):
    widget.add_site(name="A")
    widget.add_site(name="B")
    model = widget._data["site"]
    model.setData(model.index(1, 0), "Y")
    model.setData(model.index(0, 0), "X")  # invalid after the first rename resets the model.
    with caplog.at_level("WARNING"):
        model.run_pending_renames()
    assert "X" in caplog.text
