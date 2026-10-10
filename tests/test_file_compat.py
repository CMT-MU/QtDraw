"""
Drawings of earlier versions open as with the released version, and drawings survive saving and opening again.
"""

import importlib.util
import json
import shutil
from pathlib import Path

import pytest

from qtdraw.core.pyvista_widget import PyVistaWidget
from qtdraw.core.pyvista_widget_setting import COLUMN_ISOSURFACE_FILE
from qtdraw.util.util import read_dict

COMPAT = Path(__file__).resolve().parent / "data" / "compat"
EXAMPLES = Path(__file__).resolve().parents[1] / "docs" / "src" / "examples"
EXPECTED = json.loads((COMPAT / "expected.json").read_text())
STATUS = ["crystal", "origin", "cell", "lower", "upper", "repeat", "clip"]
HAS_MULTIPIE = importlib.util.find_spec("multipie") is not None
ZERO_VECTOR = pytest.mark.xfail(strict=True, reason="a vector of length 0 cannot be drawn (error while opening).")


def contents(widget):
    """Objects, unit cell and range settings and MultiPie group, as plain JSON values."""
    multipie = widget._mp_data.status if widget._mp_data is not None else {}
    data = widget.get_data_dict()
    for row in data.get("isosurface", []):  # data file names are relative to the drawing: compare the files.
        if row[COLUMN_ISOSURFACE_FILE]:
            row[COLUMN_ISOSURFACE_FILE] = str((widget.document_dir() / row[COLUMN_ISOSURFACE_FILE]).resolve())
    value = {
        "data": data,
        "status": {key: widget._status.get(key) for key in STATUS},
        "group": multipie.get("group", {}).get("group") if multipie else None,
    }
    return json.loads(json.dumps(value, sort_keys=True, default=str))


def marks(name):
    result = [pytest.mark.skipif(EXPECTED[name]["group"] is not None and not HAS_MULTIPIE, reason="MultiPie is not installed.")]
    if name == "v2_0_0_sample.qtdw":
        result.append(ZERO_VECTOR)
    return result


def opened(widget, source, tmp_path):
    file = tmp_path / source.name
    shutil.copy(source, file)
    widget.load(str(file))
    return file


# ==================================================
@pytest.mark.parametrize("name", [pytest.param(name, marks=marks(name)) for name in sorted(EXPECTED)])
def test_old_drawing_opens_as_in_the_release(widget, tmp_path, name):
    opened(widget, COMPAT / name, tmp_path)
    assert contents(widget) == EXPECTED[name]


# ==================================================
ROUND_TRIP = [COMPAT / name for name in sorted(EXPECTED)] + sorted(EXAMPLES.glob("*.qtdw"))
ROUND_TRIP += [EXAMPLES / name for name in ["Si.cif", "Si.vesta", "Si.xsf"]]
ROUND_TRIP = [pytest.param(path, marks=ZERO_VECTOR if path.name == "v2_0_0_sample.qtdw" else ()) for path in ROUND_TRIP]


def same_file(a, b):
    """Same saved drawing; the camera may differ in the last digit after it was set again."""
    a, b = read_dict(str(a)), read_dict(str(b))
    camera_a, camera_b = a.pop("camera"), b.pop("camera")
    assert a == b
    assert camera_a.keys() == camera_b.keys()
    for key in camera_a:
        assert camera_b[key] == pytest.approx(camera_a[key], rel=1e-9, abs=1e-12), key


@pytest.mark.parametrize("source", ROUND_TRIP, ids=lambda path: path.name)
def test_save_and_open_again_keeps_the_drawing(widget, tmp_path, source):
    if not HAS_MULTIPIE and (source.suffix != ".qtdw" or EXPECTED.get(source.name, {}).get("group")):
        pytest.skip("MultiPie is not installed.")
    opened(widget, source, tmp_path)
    first = contents(widget)
    saved = tmp_path / "one" / "drawing.qtdw"
    saved.parent.mkdir()
    widget.save(str(saved))

    again = PyVistaWidget(off_screen=True)
    try:
        again.load(str(saved))
        assert contents(again) == first
        first_text = saved.read_text()
        again.save(str(saved))  # the same file again: saving is stable.
        resaved = tmp_path / "resaved.qtdw"
        resaved.write_text(saved.read_text())
        saved.write_text(first_text)
        same_file(saved, resaved)
    finally:
        again.close()
