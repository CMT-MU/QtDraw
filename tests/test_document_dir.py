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


from gui_helpers import app, answer  # noqa: F401,E402  (fixture and helper)


def settle(app):
    app._modified_timer.stop()
    app._settle()


def test_undo_and_save_after_caller_changes_directory(app, tmp_path, monkeypatch):
    sub, grid = drawing_with_data(tmp_path, [0.5, 0.0, 0.0])
    pvw = app.pyvista_widget
    pvw.add_isosurface(data=str(sub / "grid.dat"), value=[0.01])
    app.save(str(sub / "a.qtdw"))
    pvw.add_site(name="A")
    settle(app)
    monkeypatch.chdir(tmp_path)  # the caller moves.

    app.undo()
    app.redo()
    app.undo()
    assert names(pvw) == ["grid.dat"] and pvw._isosurface_data["grid.dat"]["origin"] == [0.5, 0.0, 0.0]
    app.save(str(sub / "b.qtdw"))
    assert read_dict(str(sub / "b.qtdw"))["data"]["isosurface"][0][COLUMN_ISOSURFACE_FILE] == "grid.dat"


def test_failed_save_keeps_destination_and_history(app, tmp_path, monkeypatch):
    import qtdraw.core.pyvista_widget as pw

    (tmp_path / "work").mkdir()
    (tmp_path / "out").mkdir()
    shutil.copy(EXAMPLES / "Si.xsf", tmp_path / "work" / "Si.xsf")
    monkeypatch.chdir(tmp_path / "work")
    pvw = app.pyvista_widget
    pvw.add_isosurface(data="Si.xsf", value=[0.01])
    app.save(str(tmp_path / "work" / "a.qtdw"))  # clean document.
    pvw.add_site(name="A")
    settle(app)
    app.undo()  # history: [iso] <- [iso + A] as redo.
    existing = tmp_path / "out" / "a.qtdw"
    existing.write_text("old drawing")

    def fail(*args):
        raise OSError("disk full")

    with monkeypatch.context() as m, pytest.raises(OSError):
        m.setattr(pw, "write_text_atomic", fail)
        app.save(str(existing))

    assert existing.read_text() == "old drawing"
    assert names(pvw) == ["../work/Si.xsf"] and pvw.document_dir() == (tmp_path / "out").resolve()
    assert app.can_redo()
    app.redo()
    app._modified_timer.stop()
    assert names(pvw) == ["../work/Si.xsf"] and not app.can_redo()
    app.save(str(existing))  # retry.
    assert "Si.xsf" in existing.read_text()


def test_dialogs_start_in_document_directory(app, tmp_path, monkeypatch):
    from PySide6.QtWidgets import QFileDialog

    (tmp_path / "doc").mkdir()
    app.save(str(tmp_path / "doc" / "a.qtdw"))
    monkeypatch.chdir(tmp_path)
    seen = []
    monkeypatch.setattr(QFileDialog, "getSaveFileName", lambda *a, **k: (seen.append(a[2]), ("", ""))[1])
    monkeypatch.setattr(QFileDialog, "getOpenFileName", lambda *a, **k: (seen.append(a[2]), ("", ""))[1])
    answer(monkeypatch, 0)  # no unsaved question expected; any answer.
    app.save_file_as()  # Save writes to the saved file without a dialog.
    app._save_screenshot()
    app.open_file()
    doc = str((tmp_path / "doc").resolve())
    assert all(s.startswith(doc) for s in seen) and len(seen) == 3


def test_create_qtdraw_file_resolves_name_before_callback(qapp, tmp_path, monkeypatch):
    from qtdraw.core.pyvista_widget import create_qtdraw_file

    monkeypatch.chdir(tmp_path)  # restored after the test.
    (tmp_path / "sub").mkdir()
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()

    def callback(w):
        w.add_site(position="[0,0,0]")
        os.chdir(elsewhere)  # the callback moves the caller.

    create_qtdraw_file("sub/x.qtdw", callback)
    assert (tmp_path / "sub" / "x.qtdw").exists()
    assert not (elsewhere / "sub").exists()


def test_convert_writes_next_to_link_target(qapp, tmp_path, no_chdir):
    from qtdraw.core.pyvista_widget import convert_qtdraw_v3

    real = tmp_path / "real"
    real.mkdir()
    shutil.copy(EXAMPLES / "sample.qtdw", real / "old.qtdw")
    (tmp_path / "link.qtdw").symlink_to(real / "old.qtdw")
    convert_qtdraw_v3(str(tmp_path / "link.qtdw"))
    assert (real / "old_v3.qtdw").exists()


def test_failed_load_keeps_current_document(widget, tmp_path, monkeypatch):
    sub, grid = drawing_with_data(tmp_path, [0.5, 0.0, 0.0])
    widget.add_isosurface(data=str(sub / "grid.dat"), value=[0.01])
    widget.save(str(sub / "a.qtdw"))
    rows = widget.get_data_dict()
    (tmp_path / "other").mkdir()
    shutil.copy(EXAMPLES / "sample.qtdw", tmp_path / "other" / "b.qtdw")
    original = widget.add_data
    calls = []

    def fail_once(data):  # only the incoming drawing fails; the rollback draws the current one.
        calls.append(1)
        if len(calls) == 1:
            raise RuntimeError("broken")
        return original(data)

    with monkeypatch.context() as m, pytest.raises(RuntimeError):
        m.setattr(widget, "add_data", fail_once)
        widget.load(str(tmp_path / "other" / "b.qtdw"))

    assert len(calls) == 2  # the rollback ran.
    assert widget.document_dir() == sub.resolve()
    assert widget.get_data_dict() == rows and drawn(widget)
    assert widget._isosurface_data["grid.dat"]["origin"] == [0.5, 0.0, 0.0]


def test_failed_save_after_one_data_file_was_written(app, tmp_path, monkeypatch):
    import qtdraw.core.pyvista_widget as pw

    (tmp_path / "work").mkdir()
    (tmp_path / "out").mkdir()
    grid = extract_data_xsf(str(EXAMPLES / "Si.xsf"))
    monkeypatch.chdir(tmp_path / "work")
    pvw = app.pyvista_widget
    pvw.add_isosurface(data=("m1.dat", grid), value=[0.01], name="one")
    pvw.add_isosurface(data=("m2.dat", grid), value=[0.01], name="two")
    app.save(str(tmp_path / "work" / "a.qtdw"))
    assert not app.is_modified()  # clean before the failing save.
    saved_state = app._saved_state
    existing = tmp_path / "out" / "a.qtdw"
    existing.write_text("old drawing")
    original = pw.write_text_atomic
    writes = []

    def fail_second(filename, text):
        writes.append(filename)
        if len(writes) == 2:
            raise OSError("disk full")
        return original(filename, text)

    maps = []
    history_map = app._history.map
    monkeypatch.setattr(app._history, "map", lambda f: (maps.append(1), history_map(f))[1])
    with monkeypatch.context() as m, pytest.raises(OSError):
        m.setattr(pw, "write_text_atomic", fail_second)
        app.save(str(existing))

    assert existing.read_text() == "old drawing"  # the drawing was not replaced.
    assert len(maps) == 1  # history rebased once.
    assert sorted(names(pvw)) == ["m1.dat", "m2.dat"] and pvw.document_dir() == (tmp_path / "out").resolve()
    assert app._saved_state is saved_state  # a failed save does not mark the document saved.
    app.save(str(existing))  # retry.
    assert not app.is_modified()
    assert (tmp_path / "out" / "m1.dat").exists() and (tmp_path / "out" / "m2.dat").exists()
    assert "m1.dat" in existing.read_text()
