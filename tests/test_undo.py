"""
Tests for undo/redo in QtDraw (#182).
"""

import shutil
from pathlib import Path

import pytest
from PySide6.QtWidgets import QMessageBox

from gui_helpers import app, answer  # noqa: F401  (fixture and helper)
from qtdraw.util.util import check_multipie

EXAMPLES = Path(__file__).resolve().parents[1] / "docs" / "src" / "examples"


def names(app, kind="site"):
    return [r[0] for r in app.pyvista_widget.get_data_dict().get(kind, [])]


def settle(app):
    app._modified_timer.stop()
    app._settle()


def test_undo_redo_add(app):
    app.pyvista_widget.add_site(name="A")
    settle(app)
    app.pyvista_widget.add_site(name="B")
    settle(app)
    app.undo()
    assert names(app) == ["A"]
    app.undo()
    assert names(app) == []
    app.redo()
    app.redo()
    assert names(app) == ["A", "B"]


def test_undo_right_after_edit(app):
    app.pyvista_widget.add_site(name="A")
    settle(app)
    app.pyvista_widget.add_site(name="B")  # timer not yet fired.
    assert app.can_undo()
    app.undo()
    assert names(app) == ["A"]


def test_calls_in_a_row_are_one_step(app):
    import copy

    pvw = app.pyvista_widget
    origin = copy.deepcopy(pvw._status["origin"])
    pvw.add_site(name="A")
    pvw.add_bond(name="B")
    pvw.set_origin("[0.1,0,0]")
    app.undo()
    assert names(app) == [] and names(app, "bond") == []
    assert pvw._status["origin"] == origin


def test_edit_after_undo_drops_redo(app):
    app.pyvista_widget.add_site(name="A")
    settle(app)
    app.undo()
    app.pyvista_widget.add_site(name="C")  # pending.
    assert not app.can_redo()
    app.redo()
    assert names(app) == ["C"]
    settle(app)
    assert not app.can_redo()


def test_group_rename_is_undone(app):
    app.pyvista_widget.add_site(name="A")
    settle(app)
    model = app.pyvista_widget._data["site"]
    model.setData(model.index(0, 0), "B")  # deferred rename, not run yet.
    app.undo()  # runs the pending rename, records it, and undoes it.
    assert names(app) == ["A"]
    app.redo()
    assert names(app) == ["B"]


def test_hide_and_remove_from_view_are_undone(app):
    from PySide6.QtCore import Qt
    from qtdraw.core.pyvista_widget_setting import COLUMN_NAME_CHECK

    pvw = app.pyvista_widget
    pvw.add_site(name="A")
    settle(app)
    model = pvw._data["site"]
    model.setData(model.index(0, 0), Qt.Unchecked, Qt.CheckStateRole)
    settle(app)
    app.undo()
    assert pvw.get_data_dict()["site"][0][COLUMN_NAME_CHECK] is True
    model.remove_row(model.index(0, 0))
    settle(app)
    app.undo()
    assert names(app) == ["A"]


def test_status_and_repeat_are_undone(app):
    pvw = app.pyvista_widget
    pvw.add_site(position="[0,0,0]")
    settle(app)
    pvw.set_range("[0,0,0]", "[2,1,1]")
    pvw.set_repeat(True)
    settle(app)
    assert len(names(app)) > 1
    app.undo()
    assert len(names(app)) == 1 and pvw._status["repeat"] is False


def test_clear_is_undone(app, monkeypatch):
    app.pyvista_widget.add_site(name="A")
    settle(app)
    app.pyvista_widget.clear_data()
    settle(app)
    app.undo()
    assert names(app) == ["A"]


def test_undo_isosurface_removal(app, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    shutil.copy(EXAMPLES / "Si.xsf", tmp_path / "Si.xsf")
    pvw = app.pyvista_widget
    pvw.add_isosurface(data="Si.xsf", value=[0.01])
    settle(app)
    model = pvw._data["isosurface"]
    model.remove_row(model.index(0, 0))
    settle(app)
    app.undo()
    rows = pvw._data["isosurface"].tolist()
    assert len(rows) == 1 and "Si.xsf" in pvw._isosurface_data


@pytest.mark.skipif(not check_multipie(), reason="MultiPie is not installed.")
def test_undo_to_state_without_multipie_closes_dialog(app):
    settle(app)
    app.pyvista_widget.mp_set_group("Ci")
    app._show_multipie()
    settle(app)
    app.undo()
    assert app.pyvista_widget._mp_data is None and app.multipie_dialog is None
    assert "MultiPie" in app.status.text()


def test_undo_keeps_camera(app):
    pvw = app.pyvista_widget
    pvw.add_site(name="A")
    settle(app)
    pvw.set_view([1, 1, 0])
    camera = pvw.get_camera_info()
    app.undo()
    assert pvw.get_camera_info() == camera


def test_load_resets_and_save_keeps_history(app, tmp_path, monkeypatch):
    pvw = app.pyvista_widget
    pvw.add_site(name="A")
    settle(app)
    app.save(str(tmp_path / "a.qtdw"))
    assert app.can_undo()  # save keeps history.
    app.load(str(tmp_path / "a.qtdw"))
    assert not app.can_undo()  # load starts a new history.


def test_unsaved_marker_after_undo_to_saved_content(app, tmp_path):
    pvw = app.pyvista_widget
    pvw.add_site(name="A")
    app.save(str(tmp_path / "a.qtdw"))
    pvw.add_site(name="B")
    settle(app)
    assert app.is_modified()
    app.undo()
    assert not app.is_modified() and not app.windowTitle().endswith("*")


def test_restore_failure_rolls_back(app, monkeypatch):
    pvw = app.pyvista_widget
    pvw.add_site(name="A")
    settle(app)
    pvw.add_site(name="B")
    settle(app)
    original = pvw.restore_document
    calls = []

    def fail_once(snapshot):
        calls.append(1)
        if len(calls) == 1:
            raise RuntimeError("broken")
        return original(snapshot)

    monkeypatch.setattr(pvw, "restore_document", fail_once)
    with pytest.raises(RuntimeError):
        app.undo()
    assert names(app) == ["A", "B"]  # rolled back.
    assert app.can_undo()  # position unchanged.


def test_rollback_failure_clears_history(app, monkeypatch):
    pvw = app.pyvista_widget
    pvw.add_site(name="A")
    settle(app)
    monkeypatch.setattr(pvw, "restore_document", lambda s: (_ for _ in ()).throw(RuntimeError("broken")))
    with pytest.raises(RuntimeError):
        app.undo()
    assert not app.can_undo() and not app.can_redo()


def test_stale_timer_after_restore_records_nothing(app):
    pvw = app.pyvista_widget
    pvw.add_site(name="A")
    settle(app)
    pvw.add_site(name="B")
    settle(app)
    app.undo()
    app._settle()  # a late callback.
    assert app.can_redo()


def test_edit_menu_and_api(app):
    from PySide6.QtGui import QKeySequence

    assert app.action_undo.shortcut() == QKeySequence(QKeySequence.Undo)
    assert app.action_redo.shortcut() == QKeySequence(QKeySequence.Redo)
    assert not app.action_undo.isEnabled()
    app.pyvista_widget.add_site(name="A")
    settle(app)
    assert app.action_undo.isEnabled() and app.can_undo()
    app.action_undo.trigger()
    assert names(app) == [] and app.action_redo.isEnabled()
