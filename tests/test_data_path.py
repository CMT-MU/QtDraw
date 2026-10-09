"""
Regression tests for isosurface data files outside the current directory (#180).
"""

import os
import shutil
from pathlib import Path

from qtdraw.core.pyvista_widget_setting import COLUMN_ISOSURFACE_FILE, COLUMN_NAME_ACTOR
from qtdraw.parser.xsf import extract_data_xsf
from qtdraw.util.util import read_dict

EXAMPLES = Path(__file__).resolve().parents[1] / "docs" / "src" / "examples"


def isosurface_rows(widget):
    return widget._data["isosurface"].tolist()


def is_drawn(widget):
    rows = isosurface_rows(widget)
    return len(rows) > 0 and all(r[COLUMN_NAME_ACTOR] != "" for r in rows)


def saved_names(filename):
    return [r[COLUMN_ISOSURFACE_FILE] for r in read_dict(str(filename))["data"]["isosurface"]]


def make_dirs(tmp_path):
    for d in ["work", "data", "other"]:
        (tmp_path / d).mkdir()
    shutil.copy(EXAMPLES / "Si.xsf", tmp_path / "data" / "Si.xsf")
    os.chdir(tmp_path / "work")


# ==================================================
def test_data_file_outside_current_directory(widget, tmp_path):
    make_dirs(tmp_path)

    widget.add_isosurface(data=str(tmp_path / "data" / "Si.xsf"), value=[0.01])

    assert [r[COLUMN_ISOSURFACE_FILE] for r in isosurface_rows(widget)] == ["../data/Si.xsf"]
    assert is_drawn(widget)


# ==================================================
def test_relative_data_file_outside_current_directory(widget, tmp_path):
    make_dirs(tmp_path)

    widget.add_isosurface(data="../data/Si.xsf", value=[0.01])

    assert is_drawn(widget)


# ==================================================
def test_save_in_same_directory_keeps_name(widget, tmp_path):
    make_dirs(tmp_path)
    widget.add_isosurface(data="../data/Si.xsf", value=[0.01])

    widget.save(str(tmp_path / "work" / "a.qtdw"))

    assert saved_names(tmp_path / "work" / "a.qtdw") == ["../data/Si.xsf"]


# ==================================================
def test_save_in_other_directory_rebases_name(widget, tmp_path):
    make_dirs(tmp_path)
    original = (tmp_path / "data" / "Si.xsf").read_text()
    widget.add_isosurface(data="../data/Si.xsf", value=[0.01])

    widget.save(str(tmp_path / "other" / "a.qtdw"))

    assert saved_names(tmp_path / "other" / "a.qtdw") == ["../data/Si.xsf"]
    assert (tmp_path / "data" / "Si.xsf").read_text() == original  # source is not overwritten.
    assert not (tmp_path / "other" / "Si.xsf").exists()

    # the scene still works in the new directory, and the saved file can be loaded.
    widget.redraw()
    assert is_drawn(widget)
    widget.clear_data()
    os.chdir(tmp_path)
    widget.load(str(tmp_path / "other" / "a.qtdw"))
    assert is_drawn(widget)


# ==================================================
def test_save_imported_xsf_in_other_directory(widget, tmp_path):
    # known limitation noted in #184: imported /A/Si.xsf saved into /B.
    make_dirs(tmp_path)
    widget.load(str(tmp_path / "data" / "Si.xsf"))
    assert is_drawn(widget)

    widget.save(str(tmp_path / "other" / "Si.qtdw"))

    assert saved_names(tmp_path / "other" / "Si.qtdw") == ["../data/Si.xsf"]
    widget.clear_data()
    widget.load(str(tmp_path / "other" / "Si.qtdw"))
    assert is_drawn(widget)
    extract_data_xsf(str(tmp_path / "data" / "Si.xsf"))  # still a valid XSF file.


# ==================================================
def test_save_data_given_in_memory_next_to_file(widget, tmp_path):
    make_dirs(tmp_path)
    grid = extract_data_xsf(str(tmp_path / "data" / "Si.xsf"))
    widget.add_isosurface(data=("grid.dat", grid), value=[0.01])
    assert is_drawn(widget)

    widget.save(str(tmp_path / "other" / "a.qtdw"))

    # data without a source file is written next to the saved file.
    assert saved_names(tmp_path / "other" / "a.qtdw") == ["grid.dat"]
    assert (tmp_path / "other" / "grid.dat").exists()
    assert not (tmp_path / "work" / "grid.dat").exists()
    widget.clear_data()
    widget.load(str(tmp_path / "other" / "a.qtdw"))
    assert is_drawn(widget)


# ==================================================
def test_data_given_in_memory_is_not_replaced_by_a_file_of_the_same_name(widget, tmp_path):
    make_dirs(tmp_path)
    (tmp_path / "work" / "grid.dat").write_text("{'stale': 'file'}")
    grid = extract_data_xsf(str(tmp_path / "data" / "Si.xsf"))
    widget.add_isosurface(data=("grid.dat", grid), value=[0.01])

    widget.save(str(tmp_path / "other" / "a.qtdw"))

    assert saved_names(tmp_path / "other" / "a.qtdw") == ["grid.dat"]  # not "../work/grid.dat".
    assert read_dict(str(tmp_path / "other" / "grid.dat")) == grid
    assert (tmp_path / "work" / "grid.dat").read_text() == "{'stale': 'file'}"
