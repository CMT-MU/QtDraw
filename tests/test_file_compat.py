"""
Drawings of earlier versions open as with the released version, and drawings survive saving and opening again.

tests/data/compat holds drawings saved by QtDraw 0.9.6 to 2.4.2 and expected.json, what the released version
reads from them (written by tests/data/compat/make_expected.py).
"""

import copy
import importlib.util
import json
import shutil
from pathlib import Path

import pytest

from compat_helpers import assert_same, contents
from qtdraw.core.pyvista_widget import PyVistaWidget

COMPAT = Path(__file__).resolve().parent / "data" / "compat"
EXAMPLES = Path(__file__).resolve().parents[1] / "docs" / "src" / "examples"
EXPECTED = json.loads((COMPAT / "expected.json").read_text())
HAS_MULTIPIE = importlib.util.find_spec("multipie") is not None
ZERO_VECTOR = "v2_0_0_sample.qtdw"  # has a vector of length 0, which cannot be drawn: an error while opening.


def as_now(expected):
    """
    What the release read, with the changes made on purpose since then.
    """
    expected = copy.deepcopy(expected)
    expected["preference"]["general"].pop("style", None)  # #202: the style is fixed, no longer a preference.
    return expected


def uses_multipie(source):
    return source.suffix != ".qtdw" or bool(EXPECTED.get(source.name, {}).get("multipie"))  # materials too.


def open_copy(widget, source, tmp_path, qtbot):
    """
    Open a copy of a drawing; the known error of ZERO_VECTOR makes the test an expected failure.
    """
    if uses_multipie(source) and not HAS_MULTIPIE:
        pytest.skip("MultiPie is not installed.")
    file = tmp_path / source.name
    shutil.copy(source, file)
    with qtbot.capture_exceptions() as errors:  # errors while drawing are raised in Qt slots.
        widget.load(str(file))
    if source.name == ZERO_VECTOR:
        known = [error for error in errors if "finite values" in str(error[1])]
        assert len(known) == len(errors), [error for error in errors if error not in known]  # no other error.
        if known:
            pytest.xfail("a vector of length 0 cannot be drawn.")
        pytest.fail(f"{ZERO_VECTOR} opens without the known error: remove ZERO_VECTOR.")
    assert not errors, errors
    return file


# ==================================================
@pytest.mark.parametrize("name", sorted(EXPECTED))
def test_old_drawing_opens_as_in_the_release(widget, tmp_path, qtbot, name):
    open_copy(widget, COMPAT / name, tmp_path, qtbot)
    assert_same(as_now(EXPECTED[name]), contents(widget))


# ==================================================
ROUND_TRIP = [COMPAT / name for name in sorted(EXPECTED)] + sorted(EXAMPLES.glob("*.qtdw"))
ROUND_TRIP += [EXAMPLES / name for name in ["Si.cif", "Si.vesta", "Si.xsf"]]


@pytest.mark.parametrize("source", ROUND_TRIP, ids=lambda path: path.name)
def test_save_and_open_again_keeps_the_drawing(widget, tmp_path, qtbot, source):
    open_copy(widget, source, tmp_path, qtbot)
    first = contents(widget)
    saved = tmp_path / "one" / "drawing.qtdw"
    saved.parent.mkdir()
    widget.save(str(saved))
    first_text = saved.read_text()

    again = PyVistaWidget(off_screen=True)
    try:
        with qtbot.capture_exceptions() as errors:
            again.load(str(saved))
        assert not errors, errors
        assert_same(first, contents(again))
        again.save(str(saved))  # saving the same drawing again keeps it.
    finally:
        again.close()
    resaved = saved.with_name("resaved.qtdw")  # the same directory: data file names are relative to it.
    shutil.move(saved, resaved)
    saved.write_text(first_text)
    reopened = [PyVistaWidget(off_screen=True), PyVistaWidget(off_screen=True)]
    try:
        reopened[0].load(str(saved))
        reopened[1].load(str(resaved))
        assert_same(contents(reopened[0]), contents(reopened[1]))
    finally:
        for w in reopened:
            w.close()
