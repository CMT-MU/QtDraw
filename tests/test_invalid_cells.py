# SPDX-License-Identifier: MPL-2.0
# Copyright (C) 2021- The QtDraw developers
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""
Limits of values that take very long to draw, complex stream vectors, and invalid cells in loaded files (#224).
"""

import subprocess
from pathlib import Path

import pytest

from gui_helpers import app  # noqa: F401  (fixture)
from qtdraw.core.pyvista_widget_setting import object_default
from qtdraw.util.util import read_dict, write_dict
from qtdraw.widget.message_box import ResizableMessageBox
from qtdraw.widget.validator import (
    check_cell,
    validator_float,
    validator_hint,
    validator_list_float,
    validator_list_int,
    validator_math,
)

ROOT = Path(__file__).resolve().parent.parent


# ==================================================
@pytest.mark.parametrize("text, accepted", [("0.5", True), ("1000", True), ("1000.1", False), ("1e6", False)])
def test_toroid_size_has_an_upper_limit(text, accepted):
    vtype, option, default = object_default["toroid"]["size"]
    assert (validator_float(text, **option) is not None) == accepted


@pytest.mark.parametrize(
    "text, accepted",
    [("[9,18]", True), ("[729,2187]", True), ("[730,18]", False), ("[9,2188]", False), ("[999999999,18]", False)],
)
def test_stream_division_has_an_upper_limit(text, accepted):
    vtype, option, default = object_default["stream"]["division"]
    assert (validator_list_int(text, **option) is not None) == accepted
    assert "≤ [729,2187]" in validator_hint(vtype, option)


def test_list_int_limits_for_each_element():
    assert validator_list_int("[1,5]", shape=(2,), min=1, max=[1, 5]) == "[1,5]"
    assert validator_list_int("[0,5]", shape=(2,), min=1, max=[1, 5]) is None
    assert validator_list_int("[1,6]", shape=(2,), min=1, max=[1, 5]) is None
    assert validator_list_int("[1,6]", shape=(2,)) == "[1,6]"  # no limit by default.


@pytest.mark.parametrize("text", ["[I*x,y,z]", "[exp(I*x),0,0]", "[x,sqrt(-1)*y,z]"])
def test_complex_stream_vector_is_rejected(text):
    vtype, option, default = object_default["stream"]["vector"]
    assert validator_math(text, **option) is None
    assert validator_math("[x,y,z]", **option) is not None
    assert "without I" in validator_hint(vtype, option)


def test_complex_orbital_shape_is_still_accepted():
    vtype, option, default = object_default["orbital"]["shape"]
    assert validator_math("I*x", **option) is not None  # the magnitude of a complex function is drawn.


@pytest.mark.parametrize("text", ["[0.0,-1.0,6.12323399573677e-17]", "[1e-3,2E+2,.5e1]"])
def test_numbers_with_exponents_are_accepted(text):
    assert validator_list_float(text, shape=(3,), var=[""]) is not None


@pytest.mark.parametrize(
    "vtype, option, value, valid",
    [
        ("bool", {}, True, True),
        ("bool", {}, "True", False),
        ("float", {}, "0.5", True),
        ("float", {}, 0.5, False),
        ("float", {}, None, False),
        ("float", {}, "abc", False),
        ("color", {}, "red", True),
        ("color", {}, "coolwarm", False),
        ("color_both", {}, "coolwarm", True),
        ("color_both", {}, "coolwarm*", True),
        ("color_both", {}, "notacolor", False),
        ("math", {"shape": ()}, "", False),
        ("math", {"shape": (), "allow_empty": True}, "", True),
        ("str", {}, "text", True),
        ("str", {}, 1, False),
        ("combo", ["x", "y", "z", "abs"], "abs", True),
        ("combo", ["x", "y", "z", "abs"], "", False),
        ("combo", ["x", "y", "z", "abs"], "w", False),
    ],
)
def test_check_cell(vtype, option, value, valid):
    assert check_cell(vtype, option, value) == valid


# ==================================================
def invalid_file(widget, tmp_path):
    """a file with a site and a stream, with invalid cells written into it"""
    widget.add_site()
    widget.add_stream()
    file = tmp_path / "a.qtdw"
    widget.save(str(file))
    data = read_dict(str(file))
    columns = {t: list(object_default[t]) for t in ("site", "stream")}
    site, stream = data["data"]["site"][0], data["data"]["stream"][0]
    invalid = {
        ("site", "size"): None,
        ("site", "opacity"): 0.5,  # a number instead of a string.
        ("site", "color"): "notacolor",
        ("stream", "division"): "[999999999,18]",
        ("stream", "vector"): "[I*x,y,z]",
        ("stream", "name_check"): "yes",
        ("stream", "component"): "w",
        ("stream", "shape"): "{}",
    }
    for (object_type, column), value in invalid.items():
        row = site if object_type == "site" else stream
        row[columns[object_type].index(column)] = value
    write_dict(str(file), data)
    return file, invalid


def test_load_replaces_invalid_cells(widget, qtbot, tmp_path):
    file, invalid = invalid_file(widget, tmp_path)
    widget.clear_data()
    with qtbot.capture_exceptions() as exceptions:
        replaced = widget.load(str(file))
        widget.render()
    assert not exceptions, repr(exceptions[0][1])
    assert {(t, c): v for t, row, c, v in replaced} == invalid
    assert all(row == 1 for t, row, c, v in replaced)
    assert widget.replaced_cells == replaced
    data = widget.get_data_dict()
    for object_type, column in invalid:
        i = list(object_default[object_type]).index(column)
        assert data[object_type][0][i] == object_default[object_type][column][2], (object_type, column)


@pytest.mark.parametrize("object_type", sorted(object_default))
def test_objects_added_by_the_api_have_no_invalid_cells(widget, tmp_path, object_type):
    getattr(widget, f"add_{object_type}")()
    file = tmp_path / "a.qtdw"
    widget.save(str(file))
    assert widget.load(str(file)) == []


@pytest.mark.parametrize("object_type", ["orbital", "stream"])
def test_fractional_angles_are_kept(widget, tmp_path, object_type):
    getattr(widget, f"add_{object_type}")(range=[[0, 90.5], [0, 180]])
    file = tmp_path / "a.qtdw"
    widget.save(str(file))
    assert widget.load(str(file)) == []
    i = list(object_default[object_type]).index("range")
    assert widget.get_data_dict()[object_type][0][i].replace(" ", "") == "[[0,90.5],[0,180]]"


@pytest.mark.parametrize(
    "vtype, option", [("math", {"shape": ()}), ("list_float", {"shape": (3,)}), ("list_int", {"shape": (3,)})]
)
@pytest.mark.parametrize("value", ["{}", "[{},0,0]"])
def test_unexpected_expressions_are_invalid(vtype, option, value):
    assert check_cell(vtype, option, value) is False


def test_negative_stream_size_is_kept(widget, tmp_path):
    """a negative size scales the vectors by its magnitude, without normalising them (as for orbitals)"""
    vtype, option, default = object_default["stream"]["size"]
    assert validator_float("-1", **option) is not None
    widget.add_stream(size=-1)
    file = tmp_path / "a.qtdw"
    widget.save(str(file))
    assert widget.load(str(file)) == []
    i = list(object_default["stream"]).index("size")
    assert float(widget.get_data_dict()["stream"][0][i]) == -1


@pytest.mark.parametrize("text", ["x1e2", "2e", "e"])
def test_exponents_do_not_hide_variables(text):
    assert validator_list_float(f"[{text},0,0]", shape=(3,), var=[""]) is None


@pytest.mark.parametrize("text, value", [("1e2", 100), ("1E+2", 100), (".5e1", 5), ("2.5e-1", 0.25), ("E", 2.718281828)])
def test_numbers_with_exponents_are_read(text, value):
    assert float(validator_list_float(f"[{text},0,0]", shape=(3,), var=[""], digit=9)[1:].split(",")[0]) == pytest.approx(value)


def test_load_writes_the_replaced_cells_to_info(widget, tmp_path, monkeypatch):
    file, invalid = invalid_file(widget, tmp_path)
    written = []
    monkeypatch.setattr(widget, "write_info", lambda text: written.append(text))
    widget.load(str(file))
    assert f"* {len(invalid)} invalid cells in a.qtdw were set to the default values:" in written
    assert "  stream, row 1, division: '[999999999,18]'" in written


def test_valid_files_have_no_invalid_cells(widget, tmp_path):
    files = subprocess.run(["git", "ls-files", "*.qtdw"], cwd=ROOT, capture_output=True, text=True).stdout.split()
    assert files
    for name in files:
        widget.load(str(ROOT / name))
        assert widget.replaced_cells == [], name


def test_opening_a_file_shows_the_replaced_cells(app, monkeypatch, tmp_path):
    file, invalid = invalid_file(app.pyvista_widget, tmp_path)
    shown = []
    monkeypatch.setattr(ResizableMessageBox, "exec", lambda self: shown.append(self))
    app.load_file(str(file))
    assert len(shown) == 1
    assert f"{len(invalid)} cells of a.qtdw" in shown[0].text()
    assert "stream, row 1, division: '[999999999,18]'" in shown[0].detailedText()

    shown.clear()
    app.pyvista_widget.save(str(file))  # now valid.
    app.load_file(str(file))
    assert shown == []
