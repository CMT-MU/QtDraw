"""
Regression tests for process-wide state changed by PyVistaWidget (stderr, temporary widgets).
"""

import os
import subprocess
import sys
from pathlib import Path

import pytest

from qtdraw.util.util import read_dict

EXAMPLES = Path(__file__).resolve().parents[1] / "docs" / "src" / "examples"


def stderr_id():
    st = os.fstat(2)
    return (st.st_dev, st.st_ino)


def n_rows(widget, object_type):
    return len(widget._data[object_type].tolist())


@pytest.fixture
def spy_widgets(monkeypatch):
    """
    Record created and closed PyVistaWidget instances.
    """
    from qtdraw.core import pyvista_widget

    record = {"created": [], "closed": []}
    original_init = pyvista_widget.PyVistaWidget.__init__
    original_close = pyvista_widget.PyVistaWidget.close

    def spy_init(self, *args, **kwargs):
        record["created"].append(self)
        original_init(self, *args, **kwargs)

    def spy_close(self):
        record["closed"].append(self)
        return original_close(self)

    monkeypatch.setattr(pyvista_widget.PyVistaWidget, "__init__", spy_init)
    monkeypatch.setattr(pyvista_widget.PyVistaWidget, "close", spy_close)
    return record


# ==================================================
def test_stderr_is_kept_while_widget_is_open(qapp):
    from qtdraw.core.pyvista_widget import PyVistaWidget

    before = stderr_id()
    w = PyVistaWidget(off_screen=True)
    try:
        assert stderr_id() == before  # errors of the user's script stay visible.
    finally:
        w.close()
    assert stderr_id() == before


# ==================================================
def test_stderr_is_restored_when_init_fails(qapp, monkeypatch):
    from qtdraw.core import pyvista_widget

    def fail(*args, **kwargs):
        raise RuntimeError("init failed")

    monkeypatch.setattr(pyvista_widget.QtInteractor, "__init__", fail)
    before = stderr_id()
    with pytest.raises(RuntimeError):
        pyvista_widget.PyVistaWidget(off_screen=True)
    assert stderr_id() == before


# ==================================================
@pytest.mark.parametrize("inheritable", [False, True])
def test_suppress_stderr_restores_descriptor(inheritable):
    from qtdraw.core.pyvista_widget import _suppress_stderr

    original = os.get_inheritable(2)
    os.set_inheritable(2, inheritable)
    try:
        before = stderr_id()
        with pytest.raises(ValueError):
            with _suppress_stderr():
                assert stderr_id() != before
                with _suppress_stderr():  # nested.
                    pass
                assert stderr_id() != before
                raise ValueError
        assert stderr_id() == before
        assert os.get_inheritable(2) == inheritable
    finally:
        os.set_inheritable(2, original)


# ==================================================
@pytest.mark.skipif(sys.platform == "win32", reason="Python itself crashes on Windows without stderr (pythonw keeps it open).")
def test_suppress_stderr_without_stderr():
    code = """
import os
os.close(2)
from qtdraw.core.pyvista_widget import _suppress_stderr
with _suppress_stderr():
    pass
try:
    os.fstat(2)
except OSError:
    print("OK")
"""
    ret = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, timeout=120)
    assert ret.returncode == 0 and "OK" in ret.stdout, ret.stdout + ret.stderr


# ==================================================
def test_widgets_created_in_any_order_keep_stderr(qapp):
    from qtdraw.core.pyvista_widget import PyVistaWidget

    before = stderr_id()
    a = PyVistaWidget(off_screen=True)
    b = PyVistaWidget(off_screen=True)
    a.close()
    assert stderr_id() == before
    b.close()
    assert stderr_id() == before


# ==================================================
def test_create_qtdraw_file_closes_widget(qapp, tmp_path, monkeypatch, spy_widgets):
    from qtdraw.core.pyvista_widget import create_qtdraw_file

    monkeypatch.chdir(tmp_path)
    f = tmp_path / "a.qtdw"
    create_qtdraw_file(str(f), lambda w: w.add_site(position="[0,0,0]"))

    assert f.exists()
    assert len(spy_widgets["created"]) == 1
    assert spy_widgets["closed"] == spy_widgets["created"]


# ==================================================
def test_create_qtdraw_file_closes_widget_on_error(qapp, tmp_path, spy_widgets):
    from qtdraw.core.pyvista_widget import create_qtdraw_file

    def callback(w):
        raise ValueError("bad drawing")

    with pytest.raises(ValueError):
        create_qtdraw_file(str(tmp_path / "a.qtdw"), callback)

    assert len(spy_widgets["created"]) == 1
    assert spy_widgets["closed"] == spy_widgets["created"]


# ==================================================
def test_convert_qtdraw_v3_closes_widget(qapp, tmp_path, monkeypatch, spy_widgets):
    from qtdraw.core.pyvista_widget import convert_qtdraw_v3

    monkeypatch.chdir(tmp_path)
    src = tmp_path / "a.qtdw"
    src.write_text((EXAMPLES / "sample.qtdw").read_text())
    convert_qtdraw_v3(str(src))

    assert (tmp_path / "a_v3.qtdw").exists()
    assert len(spy_widgets["created"]) == 1  # no temporary widget for a version-3 file.
    assert spy_widgets["closed"] == spy_widgets["created"]


# ==================================================
def test_loading_version2_file_creates_no_widget(widget, tmp_path, spy_widgets):
    dic = read_dict(str(EXAMPLES / "sample.qtdw"))
    dic["version"] = "2.5.0"
    old = tmp_path / "old.qtdw"
    old.write_text(str(dic))

    widget.load(str(old))

    assert spy_widgets["created"] == []  # version 2 is converted without a widget.
    assert n_rows(widget, "site") == len(dic["data"]["site"])


# ==================================================
def test_save_relative_path_in_subdirectory(widget, tmp_path):
    (tmp_path / "sub").mkdir()
    os.chdir(tmp_path)
    widget.add_site(position="[0,0,0]")

    widget.save("sub/a.qtdw")

    assert (tmp_path / "sub" / "a.qtdw").exists()
    assert not (tmp_path / "sub" / "sub").exists()


# ==================================================
def test_save_through_symlink_keeps_link_name(widget, tmp_path):
    real = tmp_path / "real"
    real.mkdir()
    (real / "target.qtdw").write_text("")
    link = tmp_path / "alias.qtdw"
    link.symlink_to(real / "target.qtdw")
    widget.add_site(position="[0,0,0]")

    widget.save(str(link))

    assert widget._status["model"] == "alias"
    assert Path.cwd() == tmp_path  # the current directory is not changed.
    assert widget.document_dir() == real.resolve()  # data are relative to the written file.
    assert link.is_symlink()  # the file is written to the link target.
    assert "site" in read_dict(str(real / "target.qtdw"))["data"]
