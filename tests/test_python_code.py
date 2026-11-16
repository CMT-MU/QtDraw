# SPDX-License-Identifier: MPL-2.0
# Copyright (C) 2021- The QtDraw developers
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""
The current state of a drawing is written as Python code (#290): running the code gives the same drawing.
Also show and show_label of add_*, which the code uses for hidden objects and shown labels.
"""

import ast
import shutil
from pathlib import Path

import pytest
import shiboken6
from PySide6.QtWidgets import QFileDialog, QMessageBox

from gui_helpers import app  # noqa: F401  (fixture)
from qtdraw.core.pyvista_widget_setting import object_default, COLUMN_NAME_CHECK, COLUMN_LABEL_CHECK
from qtdraw.util.util import check_multipie

EXAMPLES = Path(__file__).resolve().parents[1] / "docs" / "src" / "examples"
STATUS = ["model", "origin", "cell", "crystal", "clip", "repeat", "lower", "upper", "view"]
STATUS += ["parallel_projection", "grid", "bar", "axis_type", "cell_mode"]


# ==================================================
def normalized(value):
    """
    A value as drawn: "[0.0, 0.0]" and "[0.0,0.0]", "0.50" and "0.5" are the same.
    """
    text = str(value).replace(" ", "")
    try:
        return float(text)
    except ValueError:
        return text


def state(window):
    """
    Objects (without actor names, which differ in each window), status and MultiPie group of a drawing.
    """
    widget = window.pyvista_widget
    rows = {}
    for object_type, data in widget.get_data_dict().items():
        columns = object_default[object_type]
        keep = [i for i, (c, (t, _, _)) in enumerate(columns.items()) if t != "actor"]
        if data:
            rows[object_type] = [[normalized(row[i]) for i in keep] for row in data]
    status = {key: widget._status[key] for key in STATUS}
    group = widget._mp_data.status["group"]["tag"] if widget._mp_data is not None else None
    return rows, status, group


def run(code, monkeypatch):
    """
    Run the code (without the event loop) and return the state of its drawing; its window is closed.
    """
    namespace = {}
    exec(code.replace("    win.exec()", "    pass"), namespace)
    window = namespace["win"]
    try:
        return state(window)
    finally:
        monkeypatch.setattr(QMessageBox, "question", lambda *a, **k: QMessageBox.Discard)
        if shiboken6.isValid(window):
            window.close()


# ==================================================
@pytest.mark.parametrize("name", ["sample.qtdw", "helimag.qtdw", "color_pattern.qtdw", "icon.qtdw", "Si.cif", "Si.xsf"])
def test_code_draws_the_same(app, tmp_path, monkeypatch, name):
    for file in EXAMPLES.glob("Si.*"):
        shutil.copy(file, tmp_path)
    shutil.copy(EXAMPLES / name, tmp_path)
    monkeypatch.chdir(tmp_path)
    app.load(name)
    code = app.to_python()
    ast.parse(code)
    assert run(code, monkeypatch) == state(app)


# ==================================================
@pytest.mark.parametrize("default_check", [False, True])
def test_hidden_objects_and_shown_labels(app, monkeypatch, default_check):
    w = app.pyvista_widget
    w.add_site(name="hidden", show=False)
    w.add_site(name="label shown", label="A", show_label=True, position="[1,0,0]")
    w.add_site(name="label hidden", label="B", show_label=False, position="[2,0,0]")
    w.add_text2d(caption="title", show=False)
    code = app.to_python()
    assert "show=False" in code and "show_label=True" in code and "show_label=False" in code
    app.update_preference("label", "default_check", default_check)  # not that of the window that runs the code.
    expected = state(app)
    assert run(code, monkeypatch) == expected


# ==================================================
def test_show_and_show_label_of_add(app):
    w = app.pyvista_widget
    w.add_site(name="A", show=False)
    w.add_site(name="B", label="b", show_label=True)
    w.add_site(name="C", label="c")  # as before: the preference (False by default).
    w.add_caption(name="D", caption="[x]", position="[[0,0,0]]", show=False)
    rows = {r[0]: r for r in w.get_data_dict()["site"]}
    assert rows["A"][COLUMN_NAME_CHECK] is False or str(rows["A"][COLUMN_NAME_CHECK]) == "False"
    assert str(rows["B"][COLUMN_LABEL_CHECK]) == "True"
    assert str(rows["C"][COLUMN_LABEL_CHECK]) == "False"
    assert str(w.get_data_dict()["caption"][0][COLUMN_NAME_CHECK]) == "False"


# ==================================================
def test_only_values_that_differ_from_the_defaults(app):
    w = app.pyvista_widget
    w.add_site()
    w.add_vector(position="[1/2,0,0]", color="red", cartesian=False)
    code = app.to_python()
    assert "win.add_site()\n" in code
    assert "win.add_vector(position='[1/2,0,0]', color='red', cartesian=False)" in code
    assert "set_unit_cell" not in code and "set_range" not in code  # the defaults.


# ==================================================
def test_status_is_written(app, monkeypatch):
    app.set_crystal("hexagonal")
    app.set_unit_cell({"a": 2.46, "c": 6.7})
    app.set_origin("[0.1,0,0]")
    app.pyvista_widget.add_site(position="[1/3,2/3,0]")
    app.set_range("[0,0,0]", "[2,2,1]")
    app.set_repeat(True)  # 18 sites in the table.
    app.set_axis("full")
    app.set_cell("all")
    app.set_view([0, 0, 1])
    app.set_model("graphene")
    code = app.to_python()
    assert code.count("win.add_site(") == 1  # the home cell; set_repeat(True) makes the others.
    assert code.index("win.add_site(") < code.index("win.set_repeat(True)")
    assert run(code, monkeypatch) == state(app)


# ==================================================
def test_isosurface_without_a_file_is_not_written(app):
    from qtdraw.parser.xsf import create_data
    import numpy as np

    grid = create_data([4, 4, 4], [0, 0, 0], np.eye(4), True, lambda x, y, z: x + y + z, None)
    app.pyvista_widget.add_isosurface(name="in memory", data=("grid", grid), value="[1.0]")
    code = app.to_python()
    assert "add_isosurface" not in code
    assert "# isosurface 'in memory' is not written: its data is not in a file." in code


# ==================================================
def test_save_python(app, tmp_path):
    app.pyvista_widget.add_site(name="A")
    app.save_python(str(tmp_path / "drawing.py"))
    text = (tmp_path / "drawing.py").read_text(encoding="utf-8")
    assert text == app.to_python()
    assert 'if "ipykernel" not in sys.modules:' in text  # the window stays open in a script.
    assert "write Python code to" in app.info_dialog.log.toPlainText()


# ==================================================
@pytest.mark.parametrize("typed, expected", [("drawing", "drawing.py"), ("drawing.py", "drawing.py")])
def test_export_menu(app, tmp_path, monkeypatch, typed, expected):
    monkeypatch.setattr(QFileDialog, "getSaveFileName", lambda *a, **k: (str(tmp_path / typed), "Python Files (*.py)"))
    app.action_export_python.trigger()
    assert (tmp_path / expected).exists()


# ==================================================
def test_export_menu_cancel(app, tmp_path, monkeypatch):
    monkeypatch.setattr(QFileDialog, "getSaveFileName", lambda *a, **k: ("", ""))
    app.action_export_python.trigger()
    assert list(tmp_path.iterdir()) == []


# ==================================================
@pytest.mark.skipif(not check_multipie(), reason="MultiPie is not installed.")
def test_multipie_drawing(app, monkeypatch):
    app.mp_set_group("D6h^1")
    app.mp_add_site("[1/3,2/3,0]")
    app.mp_add_bond("[2/3,1/3,0];[1/3,2/3,0]")
    lst = app.mp_site_samb_list("[1/3,2/3,0]")
    app.mp_add_site_samb(lst[1])
    code = app.to_python()
    assert code.index("mp_set_group") < code.index("set_unit_cell") < code.index("add_site")
    assert run(code, monkeypatch) == state(app)
