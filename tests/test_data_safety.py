"""
Regression tests for save/load/preference operations that could lose user data.
"""

import shutil
from pathlib import Path

import pytest

from qtdraw.parser.xsf import extract_data_xsf

EXAMPLES = Path(__file__).resolve().parents[1] / "docs" / "src" / "examples"


def n_rows(widget, object_type):
    return len(widget._data[object_type].tolist())


# ==================================================
def test_save_does_not_overwrite_imported_xsf(widget, tmp_path):
    xsf = tmp_path / "Si.xsf"
    shutil.copy(EXAMPLES / "Si.xsf", xsf)
    original = xsf.read_text()

    widget.load(str(xsf))
    assert n_rows(widget, "isosurface") == 1
    widget.save(str(tmp_path / "Si.qtdw"))

    assert xsf.read_text() == original
    extract_data_xsf(str(xsf))  # still a valid XSF file.


# ==================================================
def test_restore_does_not_duplicate_objects(widget):
    widget.add_site(position="[0,0,0]", name="A")
    widget.add_site(position="[1/2,1/2,0]", name="B")
    widget.add_bond(position="[0,0,0]", direction="[1,0,0]")

    widget.save_current()
    widget.restore()

    assert n_rows(widget, "site") == 2
    assert n_rows(widget, "bond") == 1


# ==================================================
def test_failed_load_keeps_current_scene(widget, tmp_path):
    widget.add_site(position="[0,0,0]")
    widget.set_model("current")

    broken = tmp_path / "broken.qtdw"
    broken.write_text("{ this is not a dict")
    with pytest.raises(Exception):
        widget.load(str(broken))

    assert n_rows(widget, "site") == 1
    assert widget._status["model"] == "current"


# ==================================================
def test_unsupported_extension_keeps_current_scene(widget, tmp_path):
    widget.add_site(position="[0,0,0]")
    other = tmp_path / "note.txt"
    other.write_text("hello")
    with pytest.raises(Exception):
        widget.load(str(other))

    assert n_rows(widget, "site") == 1


# ==================================================
def test_load_relative_path_in_subdirectory(widget, tmp_path):
    sub = tmp_path / "sub"
    sub.mkdir()
    widget.add_site(position="[0,0,0]")
    widget.save(str(sub / "a.qtdw"))
    widget.clear_data()

    import os

    os.chdir(tmp_path)
    widget.load("sub/a.qtdw")
    assert n_rows(widget, "site") == 1


# ==================================================
def test_removing_one_isosurface_keeps_shared_data(widget, tmp_path):
    shutil.copy(EXAMPLES / "Si.xsf", tmp_path / "Si.xsf")
    widget.add_isosurface(data="Si.xsf", value=[0.01], name="A")
    widget.add_isosurface(data="Si.xsf", value=[0.02], name="B")

    model = widget._data["isosurface"]
    model.remove_row(model.index(0, 0))
    assert n_rows(widget, "isosurface") == 1
    assert "Si.xsf" in widget._isosurface_data


# ==================================================
def test_save_skips_missing_isosurface_data(widget, tmp_path):
    data_file = tmp_path / "grid.dat"
    data_file.write_text("keep me")
    grid = extract_data_xsf(str(EXAMPLES / "Si.xsf"))
    widget.add_isosurface(data=("grid.dat", grid), value=[0.01])
    widget._isosurface_data.clear()

    widget.save(str(tmp_path / "a.qtdw"))
    assert data_file.read_text() == "keep me"


# ==================================================
def test_save_dialog_path_gets_extension():
    from qtdraw.core.qtdraw_app import add_extension

    assert add_extension(Path("/x/foo"), ".qtdw") == Path("/x/foo.qtdw")
    assert add_extension(Path("/x/foo.qtdw"), ".qtdw") == Path("/x/foo.qtdw")
    assert add_extension(Path("/x/foo.txt"), ".qtdw") == Path("/x/foo.txt.qtdw")


# ==================================================
def test_save_dialog_without_extension_saves(qapp, tmp_path, monkeypatch):
    from PySide6.QtWidgets import QFileDialog, QMessageBox
    from qtdraw.core.qtdraw_app import QtDraw

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(QMessageBox, "question", lambda *a, **k: QMessageBox.Ok)  # "Quit QtDraw ?".
    app = QtDraw()
    try:
        app.pyvista_widget.add_site(position="[0,0,0]")
        monkeypatch.setattr(QFileDialog, "getSaveFileName", lambda *a, **k: (str(tmp_path / "foo"), ""))
        app.save_file()
        assert (tmp_path / "foo.qtdw").is_file()
    finally:
        app.close()


# ==================================================
def test_save_keeps_file_permission(widget, tmp_path):
    import os

    file = tmp_path / "a.qtdw"
    widget.add_site(position="[0,0,0]")
    widget.save(str(file))
    umask = os.umask(0)
    os.umask(umask)
    assert file.stat().st_mode & 0o777 == 0o666 & ~umask

    file.chmod(0o640)
    widget.save(str(file))
    assert file.stat().st_mode & 0o777 == 0o640
    assert [p.name for p in tmp_path.iterdir()] == ["a.qtdw"]  # no temporary file left.


# ==================================================
@pytest.mark.parametrize(
    "content",
    ["{'version': '3.0.0'}", "{'version': '3.0.0', 'status': {}, 'preference': {}, 'camera': {}, 'data': {'site': [['bad']]}}"],
)
def test_incomplete_file_keeps_current_scene(widget, tmp_path, content):
    widget.add_site(position="[0,0,0]", name="A")
    widget.set_model("current")

    broken = tmp_path / "incomplete.qtdw"
    broken.write_text(content)
    with pytest.raises(Exception):
        widget.load(str(broken))

    assert n_rows(widget, "site") == 1
    assert widget._status["model"] == "current"


# ==================================================
def test_save_formats_before_writing(widget, tmp_path, monkeypatch):
    import subprocess
    from qtdraw.core import pyvista_widget
    from qtdraw.util.util import read_dict

    calls = []

    def fake_run(cmd, input, **kwargs):
        calls.append(cmd)
        assert not (tmp_path / "a.qtdw").exists()  # formatted before the file is written.
        return subprocess.CompletedProcess(cmd, 0, stdout=input.replace("{", "{ ", 1))

    monkeypatch.setattr(pyvista_widget.shutil, "which", lambda name: "/usr/bin/black")
    monkeypatch.setattr(pyvista_widget.subprocess, "run", fake_run)
    widget.add_site(position="[0,0,0]")
    widget.save(str(tmp_path / "a.qtdw"))

    assert calls and calls[0][-1] == "-"  # text is passed by stdin, not by shell.
    assert len(read_dict(str(tmp_path / "a.qtdw"))["data"]["site"]) == 1


# ==================================================
def test_save_without_black(widget, tmp_path, monkeypatch):
    from qtdraw.core import pyvista_widget
    from qtdraw.util.util import read_dict

    monkeypatch.setattr(pyvista_widget.shutil, "which", lambda name: None)
    widget.add_site(position="[0,0,0]")
    widget.save(str(tmp_path / "a.qtdw"))
    assert len(read_dict(str(tmp_path / "a.qtdw"))["data"]["site"]) == 1


# ==================================================
def test_malformed_rows_keep_current_scene(widget, tmp_path):
    widget.add_site(position="[0,0,0]", name="A")
    widget.save(str(tmp_path / "good.qtdw"))
    good = (tmp_path / "good.qtdw").read_text()

    for i, bad_data in enumerate(["{'site': [['bad']]}", "{'unknown': []}", "{'site': 'bad'}"]):
        from qtdraw.util.util import read_dict

        d = read_dict(str(tmp_path / "good.qtdw"))
        d["data"] = eval(bad_data)
        broken = tmp_path / f"bad{i}.qtdw"
        broken.write_text(str(d))
        with pytest.raises(Exception):
            widget.load(str(broken))
        assert n_rows(widget, "site") == 1


# ==================================================
def test_failed_load_does_not_emit_data_removed(widget, tmp_path):
    widget.add_site(position="[0,0,0]")
    removed = []
    widget.data_removed.connect(lambda: removed.append(True))

    broken = tmp_path / "incomplete.qtdw"
    broken.write_text("{'version': '3.0.0', 'status': {}, 'preference': {}, 'camera': {}, 'data': {}}")
    with pytest.raises(Exception):
        widget.load(str(broken))
    assert removed == []
    assert n_rows(widget, "site") == 1
