"""
Tests for document snapshots and restore (#182).
"""

import shutil
from pathlib import Path

from qtdraw.core.pyvista_widget import same_snapshot
from qtdraw.util.util import check_multipie

EXAMPLES = Path(__file__).resolve().parents[1] / "docs" / "src" / "examples"


def rows(widget):
    return widget.get_data_dict()


def test_restore_rows_and_status(widget):
    widget.add_site(name="A")
    widget.add_bond(name="B")
    widget.set_origin("[0.1,0,0]")
    snap = widget.document_snapshot()
    expected_rows = rows(widget)

    widget.clear_data()
    widget.add_vector(name="V")
    widget.set_origin("[0,0,0]")
    widget.restore_document(snap)

    assert rows(widget) == expected_rows
    assert widget._status["origin"] == snap["doc"]["status"]["origin"]
    assert same_snapshot(widget.document_snapshot(), snap)


def test_restore_keeps_camera_and_preferences(widget):
    snap = widget.document_snapshot()
    if check_multipie():
        widget.mp_set_group("C2h")
        snap = widget.document_snapshot()
        widget.mp_set_group("Ci")
    widget.set_view([1, 1, 0])
    camera = widget.get_camera_info()
    widget._preference["label"]["size"] = 33
    removed = []
    widget.data_removed.connect(lambda: removed.append(1))

    widget.restore_document(snap)

    assert widget.get_camera_info() == camera
    assert widget._preference["label"]["size"] == 33
    assert removed == []


def test_restore_isosurface_grid(widget, tmp_path):
    shutil.copy(EXAMPLES / "Si.xsf", tmp_path / "Si.xsf")
    widget.add_isosurface(data="Si.xsf", value=[0.01])
    snap = widget.document_snapshot()
    grid = widget._isosurface_data["Si.xsf"]
    model = widget._data["isosurface"]
    model.remove_row(model.index(0, 0))
    assert "Si.xsf" not in widget._isosurface_data  # removed with its last row.

    widget.restore_document(snap)

    assert widget._isosurface_data["Si.xsf"] is grid
    assert len(widget._data["isosurface"].tolist()) == 1


def test_restore_multipie_status(widget):
    if not check_multipie():
        return
    widget.mp_set_group("C2h")
    snap = widget.document_snapshot()
    widget.mp_set_group("Ci")
    widget.restore_document(snap)
    assert widget._mp_data.status == snap["doc"]["multipie"]

    widget._mp_data = None
    empty = widget.document_snapshot()
    widget.mp_set_group("Ci")
    widget.restore_document(empty)
    assert widget._mp_data is None
