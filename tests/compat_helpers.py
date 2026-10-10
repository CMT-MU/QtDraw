"""
Contents of a drawing that must not change when it is opened or saved again (used by test_file_compat.py and
tests/data/compat/make_expected.py, which runs it with the released version).
"""

import json
from pathlib import Path

import pytest

STATUS_EXCLUDED = {"plus", "model", "multipie"}  # derived values, the file name, and MultiPie (below).


def contents(widget):
    """
    Objects, status, preferences, MultiPie status and camera of a widget, as plain JSON values.
    """
    from qtdraw.core.pyvista_widget_setting import COLUMN_ISOSURFACE_FILE

    data = widget.get_data_dict()
    document_dir = widget.document_dir() if hasattr(widget, "document_dir") else Path.cwd()
    for row in data.get("isosurface", []):  # data file names are relative to the drawing: compare the files.
        if row[COLUMN_ISOSURFACE_FILE]:
            row[COLUMN_ISOSURFACE_FILE] = str((document_dir / row[COLUMN_ISOSURFACE_FILE]).resolve())
    multipie = widget._mp_data.status if widget._mp_data is not None else {}
    value = {
        "data": data,
        "status": {key: value for key, value in widget._status.items() if key not in STATUS_EXCLUDED},
        "preference": widget._preference,
        "multipie": {key: value for key, value in multipie.items() if key != "plus"},
        "camera": widget.get_camera_info(),
    }
    return json.loads(json.dumps(value, sort_keys=True, default=str))


def assert_same(expected, actual):
    """
    Same contents; the camera may differ in the last digits (it is set again when a drawing is opened).
    """
    expected, actual = dict(expected), dict(actual)
    camera, actual_camera = expected.pop("camera"), actual.pop("camera")
    assert actual == expected
    assert actual_camera.keys() == camera.keys()
    for key in camera:
        assert actual_camera[key] == pytest.approx(camera[key], rel=1e-9, abs=1e-9), key
