"""
Tests for the document directory, which replaces changing the current directory (#181).
"""

import os
import shutil
from pathlib import Path

import pytest

from qtdraw.core.pyvista_widget_setting import COLUMN_ISOSURFACE_FILE, COLUMN_NAME_ACTOR
from qtdraw.parser.xsf import extract_data_xsf
from qtdraw.util.util import read_dict

EXAMPLES = Path(__file__).resolve().parents[1] / "docs" / "src" / "examples"


def names(widget):
    return [r[COLUMN_ISOSURFACE_FILE] for r in widget._data["isosurface"].tolist()]


def drawn(widget):
    rows = widget._data["isosurface"].tolist()
    return len(rows) > 0 and all(r[COLUMN_NAME_ACTOR] != "" for r in rows)


@pytest.fixture
def no_chdir(monkeypatch):
    def fail(*args):
        raise AssertionError("os.chdir must not be called")

    monkeypatch.setattr(os, "chdir", fail)


def drawing_with_data(tmp_path, origin):
    # sub/a.qtdw refers to sub/grid.dat (relative to the drawing).
    sub = tmp_path / "sub"
    sub.mkdir()
    grid = dict(extract_data_xsf(str(EXAMPLES / "Si.xsf")), origin=origin)
    (sub / "grid.dat").write_text(str(grid))
    return sub, grid


def test_fresh_widget_follows_current_directory(widget, tmp_path):
    assert widget.document_dir() == Path.cwd()


def test_loaded_drawing_reads_data_from_its_directory(widget, tmp_path, monkeypatch):
    sub, grid = drawing_with_data(tmp_path, [0.5, 0.0, 0.0])
    other = dict(grid, origin=[0.0, 0.0, 0.0])
    (tmp_path / "grid.dat").write_text(str(other))  # same name in the caller's directory.
    widget.add_isosurface(data=str(sub / "grid.dat"), value=[0.01])
    widget.save(str(sub / "a.qtdw"))
    widget.clear_data()
    widget._isosurface_data.clear()

    widget.load("sub/a.qtdw")

    assert Path.cwd() == tmp_path
    assert widget.document_dir() == sub.resolve()
    assert names(widget) == ["grid.dat"] and drawn(widget)
    assert widget._isosurface_data["grid.dat"]["origin"] == [0.5, 0.0, 0.0]


def test_load_does_not_change_directory(widget, tmp_path, no_chdir):
    (tmp_path / "sub").mkdir()
    shutil.copy(EXAMPLES / "sample.qtdw", tmp_path / "sub" / "a.qtdw")
    widget.load("sub/a.qtdw")
    assert widget.document_dir() == (tmp_path / "sub").resolve()


def test_relative_data_after_load_uses_document_directory(widget, tmp_path, monkeypatch):
    sub, grid = drawing_with_data(tmp_path, [0.5, 0.0, 0.0])
    shutil.copy(EXAMPLES / "sample.qtdw", sub / "a.qtdw")
    widget.load(str(sub / "a.qtdw"))
    monkeypatch.chdir(tmp_path)  # the caller is elsewhere.

    widget.add_isosurface(data="grid.dat", value=[0.01])

    assert names(widget) == ["grid.dat"] and drawn(widget)


def test_failed_load_restores_document_directory(widget, tmp_path, monkeypatch):
    (tmp_path / "sub").mkdir()
    shutil.copy(EXAMPLES / "sample.qtdw", tmp_path / "sub" / "a.qtdw")
    seen = []

    def fail(data):
        seen.append(widget._document_dir)  # the base is set before the data is drawn.
        raise RuntimeError("broken")

    with monkeypatch.context() as m, pytest.raises(RuntimeError):
        m.setattr(widget, "add_data", fail)
        widget.load(str(tmp_path / "sub" / "a.qtdw"))
    assert seen[0] == (tmp_path / "sub").resolve()
    assert widget._document_dir is None


def test_two_widgets_keep_their_directories(widget, tmp_path):
    from qtdraw.core.pyvista_widget import PyVistaWidget

    for d in ["a", "b"]:
        (tmp_path / d).mkdir()
        shutil.copy(EXAMPLES / "sample.qtdw", tmp_path / d / "x.qtdw")
    other = PyVistaWidget(off_screen=True)
    try:
        widget.load(str(tmp_path / "a" / "x.qtdw"))
        other.load(str(tmp_path / "b" / "x.qtdw"))
        assert widget.document_dir() == (tmp_path / "a").resolve()
        assert other.document_dir() == (tmp_path / "b").resolve()
    finally:
        other.close()


def test_save_does_not_change_directory(widget, tmp_path, no_chdir):
    (tmp_path / "sub").mkdir()
    widget.add_site(position="[0,0,0]")
    widget.save("sub/a.qtdw")
    assert (tmp_path / "sub" / "a.qtdw").exists()
    assert widget.document_dir() == (tmp_path / "sub").resolve()


def test_save_elsewhere_writes_data_next_to_drawing(widget, tmp_path):
    (tmp_path / "out").mkdir()
    grid = extract_data_xsf(str(EXAMPLES / "Si.xsf"))
    widget.add_isosurface(data=("grid.dat", grid), value=[0.01])
    widget.save(str(tmp_path / "out" / "a.qtdw"))
    assert read_dict(str(tmp_path / "out" / "grid.dat")) == grid
    assert not (tmp_path / "grid.dat").exists()


def test_save_after_load_uses_callers_directory(widget, tmp_path):
    (tmp_path / "dir").mkdir()
    shutil.copy(EXAMPLES / "sample.qtdw", tmp_path / "dir" / "a.qtdw")
    widget.load("dir/a.qtdw")
    widget.save("b.qtdw")  # relative to the caller, not to the drawing.
    assert (tmp_path / "b.qtdw").exists() and not (tmp_path / "dir" / "b.qtdw").exists()


def test_save_into_missing_directory_changes_nothing(widget, tmp_path):
    shutil.copy(EXAMPLES / "Si.xsf", tmp_path / "Si.xsf")
    widget.add_isosurface(data="Si.xsf", value=[0.01])
    model = widget._status["model"]
    with pytest.raises(FileNotFoundError):
        widget.save(str(tmp_path / "missing" / "a.qtdw"))
    assert names(widget) == ["Si.xsf"] and widget._document_dir is None
    assert widget._status["model"] == model
