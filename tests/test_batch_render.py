"""
Tests for batch rendering: bulk operations submit at most one render (#190).
"""

import time

import pytest
import pyvista as pv
from vtkmodules.vtkRenderingCore import vtkTextActor
from pyvistaqt import QtInteractor
from PySide6.QtCore import QCoreApplication

import qtdraw.core.pyvista_widget as pvw_module
from qtdraw.core.pyvista_widget_setting import COLUMN_NAME, COLUMN_NAME_ACTOR, COLUMN_NAME_CHECK
from qtdraw.util.util import check_multipie
from grid_helpers import write_small_xsf
from gui_helpers import app  # noqa: F401  (fixture)

needs_multipie = pytest.mark.skipif(not check_multipie(), reason="MultiPie is not installed.")


# ==================================================
@pytest.fixture
def submissions(monkeypatch):
    """
    Widgets for which a render was submitted (a call delegated to QtInteractor.render), one entry per call.
    """
    calls = []
    monkeypatch.setattr(QtInteractor, "render", lambda self, *args, **kwargs: calls.append(self))
    return calls


def count(submissions, widget, action):
    submissions.clear()
    action()
    return sum(1 for w in submissions if w is widget)


def add_mixed(widget):
    widget.add_site(name="S", label="Fe")
    widget.add_site(name="H", label="O")
    widget.add_bond(name="B")
    widget.add_caption(name="C")
    widget.add_text2d(name="T", caption="text")


def actor_of(widget, object_type, name):
    for row in widget._data[object_type].tolist():
        if row[COLUMN_NAME] == name:
            return row[COLUMN_NAME_ACTOR]
    raise KeyError(name)


def names(widget, object_type="site"):
    return [row[COLUMN_NAME] for row in widget.get_data_dict()[object_type]]


# ==================================================
def test_single_add_submits_once(widget, submissions):
    assert count(submissions, widget, lambda: widget.add_site(name="A")) == 1
    assert count(submissions, widget, lambda: widget.add_bond(name="B")) == 1
    assert count(submissions, widget, lambda: widget.add_text2d(name="T", caption="x")) == 1


def test_add_data_submits_once(widget, submissions):
    add_mixed(widget)
    data = widget.get_data_dict()
    widget.clear_data()
    assert count(submissions, widget, lambda: widget.add_data(data)) == 1
    assert widget.get_data_dict() == data
    assert all(row[COLUMN_NAME_ACTOR] in widget.actors for model in widget._data.values() for row in model.tolist())


def test_empty_add_data_and_empty_batch_submit_nothing(widget, submissions):
    assert count(submissions, widget, lambda: widget.add_data({"site": []})) == 0

    def empty():
        with widget._batch_render():
            pass

    assert count(submissions, widget, empty) == 0


def test_latex_text2d_in_add_data_submits_once(widget, submissions, monkeypatch):
    used = []

    def fake_text2d(caption, mathjax, x, y, size, color):
        used.append(caption)
        return vtkTextActor()

    monkeypatch.setattr(pvw_module, "create_text2d", fake_text2d)
    widget.add_text2d(name="M1", caption="$x^2$")
    widget.add_text2d(name="M2", caption="$y^2$")
    data = widget.get_data_dict()
    widget.clear_data()
    used.clear()
    assert count(submissions, widget, lambda: widget.add_data(data)) == 1
    assert used == ["$x^2$", "$y^2$"]  # the math path was used.


def test_redraw_repeat_nonrepeat_submit_once(widget, submissions):
    add_mixed(widget)
    assert count(submissions, widget, widget.redraw) == 1
    assert count(submissions, widget, lambda: widget.set_repeat(True)) == 1
    assert len(widget.get_data_dict()["site"]) > 2  # repeated.
    assert count(submissions, widget, widget.set_nonrepeat) == 1


def test_hidden_rows_have_no_actor_after_bulk(widget, submissions):
    add_mixed(widget)
    data = widget.get_data_dict()
    for row in data["site"]:
        if row[COLUMN_NAME] == "H":
            row[COLUMN_NAME_CHECK] = False
    widget.clear_data()
    assert count(submissions, widget, lambda: widget.add_data(data)) == 1
    assert actor_of(widget, "site", "H") == ""
    assert actor_of(widget, "site", "S") in widget.actors


def test_restore_document_submits_once(widget, submissions):
    add_mixed(widget)
    snap = widget.document_snapshot()
    widget.clear_data()
    assert count(submissions, widget, lambda: widget.restore_document(snap)) == 1
    assert names(widget) == ["S", "H"]


def test_load_qtdw_submits_once(widget, submissions, tmp_path):
    add_mixed(widget)
    widget.save(str(tmp_path / "a.qtdw"))
    widget.clear_data()
    assert count(submissions, widget, lambda: widget.load(str(tmp_path / "a.qtdw"))) == 1
    assert len(widget.get_data_dict()["site"]) == 2


def test_load_material_submits_once(widget, submissions, tmp_path):
    file = tmp_path / "m.xsf"
    write_small_xsf(file)
    assert count(submissions, widget, lambda: widget.load(str(file))) == 1
    assert widget.get_data_dict()["isosurface"]


def test_load_failure_recovers_inside_one_batch(widget, submissions, tmp_path, monkeypatch):
    add_mixed(widget)
    widget.save(str(tmp_path / "a.qtdw"))
    widget.add_site(name="X")
    before = widget.get_data_dict()
    camera = widget.get_camera_info()

    set_camera_info = widget.set_camera_info
    calls = []

    def broken(*args, **kwargs):
        calls.append(1)
        if len(calls) == 1:  # loading fails, restoring the current data does not.
            widget.add_site(name="partial")  # partial mutation before the failure.
            raise RuntimeError("broken")
        return set_camera_info(*args, **kwargs)

    submissions.clear()
    with monkeypatch.context() as m:
        m.setattr(widget, "set_camera_info", broken)
        with pytest.raises(RuntimeError, match="broken"):
            widget.load(str(tmp_path / "a.qtdw"))
    assert sum(1 for w in submissions if w is widget) == 1
    assert widget._batch_depth == 0
    assert widget.get_data_dict() == before
    assert widget.get_camera_info() == camera


# ==================================================
def test_nested_batches_submit_once_at_outer_exit(widget, submissions):
    submissions.clear()
    with widget._batch_render():
        widget.add_site(name="A")
        with widget._batch_render():
            widget.add_site(name="B")
        assert submissions == []
        widget.add_site(name="C")
    assert submissions == [widget]
    assert widget._batch_depth == 0 and not widget._batch_dirty


def test_caught_inner_exception_keeps_outer_batch(widget, submissions):
    submissions.clear()
    with widget._batch_render():
        try:
            with widget._batch_render():
                widget.add_site(name="A")
                raise ValueError("inner")
        except ValueError:
            pass
        assert submissions == []
        widget.add_site(name="B")
    assert submissions == [widget]


def test_body_failure_keeps_exception_and_submits(widget, submissions):
    submissions.clear()
    with pytest.raises(ValueError, match="body"):
        with widget._batch_render():
            widget.add_site(name="A")
            raise ValueError("body")
    assert submissions == [widget]  # what was drawn before the failure is shown.
    assert widget._batch_depth == 0
    assert count(submissions, widget, lambda: widget.add_site(name="B")) == 1  # reusable.


def test_body_and_submission_failure_keeps_body_exception(widget, monkeypatch):
    def fail(self, *args, **kwargs):
        raise RuntimeError("submit")

    with monkeypatch.context() as m:  # not when events are processed after the test.
        m.setattr(QtInteractor, "render", fail)
        with pytest.raises(ValueError, match="body"):
            with widget._batch_render():
                widget.add_site(name="A")
                raise ValueError("body")
    assert widget._batch_depth == 0 and not widget._batch_dirty


def test_submission_failure_after_success_raises(widget, monkeypatch, submissions):
    def fail(self, *args, **kwargs):
        raise RuntimeError("submit")

    with monkeypatch.context() as m:
        m.setattr(QtInteractor, "render", fail)
        with pytest.raises(RuntimeError, match="submit"):
            with widget._batch_render():
                widget.add_site(name="A")
    assert widget._batch_depth == 0 and not widget._batch_dirty
    assert count(submissions, widget, lambda: widget.add_site(name="B")) == 1


def test_clear_info_inside_batch_keeps_batch_state(widget, submissions):
    submissions.clear()
    with widget._batch_render():
        with widget._batch_render():
            widget.add_site(name="A")
            widget.clear_info()
        assert widget._batch_depth == 1
        widget.add_site(name="B")
    assert submissions == [widget]


def test_two_widgets_are_independent(qapp, widget, submissions):
    other = pvw_module.PyVistaWidget(off_screen=True)
    try:
        submissions.clear()
        with widget._batch_render():
            widget.add_site(name="A")
            other.add_site(name="B")
            assert submissions == [other]
        assert submissions == [other, widget]
    finally:
        other.close()


def test_closed_widget_does_not_submit_at_batch_end(widget, submissions):
    submissions.clear()
    with widget._batch_render():
        widget.add_site(name="A")
        widget._closed = True
    widget._closed = False
    assert submissions == []
    assert widget._batch_depth == 0 and not widget._batch_dirty


# ==================================================
def test_undo_submits_once(app, submissions):
    pvw = app.pyvista_widget
    add_mixed(pvw)
    app._settle()
    pvw.add_site(name="X")
    app._settle()
    assert count(submissions, pvw, app.undo) == 1
    assert count(submissions, pvw, app.redo) == 1


def test_restore_failure_rolls_back_inside_one_batch(app, submissions, monkeypatch):
    pvw = app.pyvista_widget
    add_mixed(pvw)
    app._settle()
    pvw.add_site(name="X")
    app._settle()
    before = pvw.get_data_dict()
    original = pvw.restore_document
    calls = []

    def fail_once(snapshot):
        calls.append(1)
        if len(calls) == 1:
            pvw.add_site(name="partial")
            raise RuntimeError("broken")
        return original(snapshot)

    monkeypatch.setattr(pvw, "restore_document", fail_once)
    submissions.clear()
    with pytest.raises(RuntimeError):
        app.undo()
    assert sum(1 for w in submissions if w is pvw) == 1
    assert pvw.get_data_dict() == before
    assert app.can_undo()
    assert pvw._batch_depth == 0


def test_rollback_failure_clears_history_and_ends_batch(app, submissions, monkeypatch):
    pvw = app.pyvista_widget
    pvw.add_site(name="A")
    app._settle()
    monkeypatch.setattr(pvw, "restore_document", lambda s: (_ for _ in ()).throw(RuntimeError("broken")))
    with pytest.raises(RuntimeError):
        app.undo()
    assert not app.can_undo() and not app.can_redo()
    assert pvw._batch_depth == 0


def test_restore_submission_failure_still_updates_panel(app, monkeypatch):
    pvw = app.pyvista_widget
    pvw.add_site(name="A")
    app._settle()
    pvw.add_site(name="B")
    app._settle()
    after = []
    original = app._after_restore
    monkeypatch.setattr(app, "_after_restore", lambda: (after.append(pvw._batch_depth), original()))

    def fail(self, *args, **kwargs):
        raise RuntimeError("submit")

    with monkeypatch.context() as m:
        m.setattr(QtInteractor, "render", fail)
        with pytest.raises(RuntimeError, match="submit"):
            app.undo()
    assert after == [0]  # after the batch.
    assert names(pvw) == ["A"]  # committed.
    assert app.can_redo()  # the history follows the restored document.


# ==================================================
@needs_multipie
def test_mp_add_submit_once(widget, submissions):
    widget.mp_set_group("D3^4")
    actions = [
        lambda: widget.mp_add_site("[1/4,0,1/3]"),
        lambda: widget.mp_add_bond("[1/4,0,1/3];[0,1/4,2/3]"),
        lambda: widget.mp_add_vector("[0,0,1] # [1/2,1/2,0]", type="Q"),
        lambda: widget.mp_add_orbital("3z**2-r**2 # [1/2,1/2,1/2]", type="Q"),
        lambda: widget.mp_add_site_samb(widget.mp_site_samb_list("[1/4,0,1/3]")[1]),
        lambda: widget.mp_add_bond_samb(widget.mp_bond_samb_list("[1/2,1/2,0]@[1/4,1/4,0]")[3]),
    ]
    for action in actions:
        assert count(submissions, widget, action) == 1

    widget.mp_vector_samb_list("[1/2, 1/2, 0]", "Q")
    assert count(submissions, widget, lambda: widget.mp_add_vector_samb("Q02+G01")) == 1
    modulation = "[[Q02, 1, [1/2,0,0], cos], [Q02, 1, [0,1/2,0], sin]] : [2,2,1]"
    assert count(submissions, widget, lambda: widget.mp_add_vector_samb_modulation(modulation)) == 1
    widget.mp_orbital_samb_list("[0,0,0];[1/2,1/2,0]", "Q", 1)
    assert count(submissions, widget, lambda: widget.mp_add_orbital_samb("Q02+G01")) == 1
    modulation = "[[Q01, 1, [1/2,0,0], cos], [Q02, 1, [0,1/2,0], sin]] : [2,2,1]"
    assert count(submissions, widget, lambda: widget.mp_add_orbital_samb_modulation(modulation)) == 1
    assert count(submissions, widget, lambda: widget.mp_add_bond_definition("[1/4,0,1/3];[0,1/4,2/3]")) == 1


@needs_multipie
def test_multipie_dialog_route_submits_once(widget, submissions):
    widget.mp_set_group("D3^4")
    data = widget._mp_data  # the MultiPie dialog calls these directly.
    assert count(submissions, widget, lambda: data.add_site("[1/4,0,1/3]")) == 1
    assert count(submissions, widget, lambda: data.add_bond("[1/4,0,1/3];[0,1/4,2/3]")) == 1
    assert count(submissions, widget, lambda: data.add_bond_definition("[1/4,0,1/3];[0,1/4,2/3]")) == 1


@needs_multipie
def test_qtdraw_mp_wrapper_submits_once(app, submissions):
    app.mp_set_group("D3^4")
    pvw = app.pyvista_widget
    assert count(submissions, pvw, lambda: app.mp_add_site("[1/4,0,1/3]")) == 1


# ==================================================
def wait_for(condition, timeout=5.0):
    end = time.monotonic() + timeout
    while time.monotonic() < end:
        QCoreApplication.processEvents()
        if condition():
            return True
        time.sleep(0.01)
    return condition()


@pytest.fixture
def rendered(monkeypatch):
    """
    Widgets actually rendered (BasePlotter.render reached through the render signal), one entry per call.
    """
    calls = []
    original = pv.BasePlotter.render

    def spy(self, *args, **kwargs):
        calls.append(self)
        return original(self, *args, **kwargs)

    monkeypatch.setattr(pv.BasePlotter, "render", spy)
    return calls


def quiet(rendered, period=0.5, timeout=10.0):
    """
    Process events until no render is delivered for a period (threaded renders on macOS arrive later).
    """
    end = time.monotonic() + timeout
    while time.monotonic() < end:
        n = len(rendered)
        wait_for(lambda: len(rendered) > n, timeout=period)
        if len(rendered) == n:
            return
    raise AssertionError("renders did not stop")


def drain(widget, rendered):
    widget.render_timer.stop()
    quiet(rendered)
    rendered.clear()


def test_batch_renders_once(widget, rendered):
    drain(widget, rendered)
    widget.add_data({"site": [], "bond": []})
    with widget._batch_render():
        for i in range(5):
            widget.add_site(name=f"S{i}")
    assert wait_for(lambda: widget in rendered)
    quiet(rendered)
    assert rendered.count(widget) == 1

    rendered.clear()
    widget.add_site(name="single")  # rendering resumes after a batch.
    assert wait_for(lambda: widget in rendered)


def test_close_inside_batch_does_not_render(qapp, rendered):
    widget = pvw_module.PyVistaWidget(off_screen=True)
    drain(widget, rendered)
    with widget._batch_render():
        widget.add_site(name="A")
        widget.close()
    quiet(rendered)
    assert widget not in rendered


def test_close_right_after_submission(qapp, rendered):
    widget = pvw_module.PyVistaWidget(off_screen=True)
    drain(widget, rendered)
    with widget._batch_render():
        widget.add_site(name="A")
    widget.close()
    quiet(rendered)  # no crash.


def test_timer_still_renders(widget, rendered):
    drain(widget, rendered)
    widget.render_timer.start(20)
    assert wait_for(lambda: widget in rendered)


# ==================================================
def test_load_render_failure_keeps_loaded_document(widget, tmp_path, monkeypatch):
    add_mixed(widget)
    widget.save(str(tmp_path / "a.qtdw"))
    widget.clear_data()
    widget.add_site(name="X")
    removed = []
    widget.data_removed.connect(lambda: removed.append(1))
    messages = []
    widget.message.connect(messages.append)

    def fail(self, *args, **kwargs):
        raise RuntimeError("submit")

    with monkeypatch.context() as m:  # not when events are processed after the test.
        m.setattr(QtInteractor, "render", fail)
        widget.load(str(tmp_path / "a.qtdw"))  # the drawing is loaded, only its render failed.
    assert names(widget) == ["S", "H"]
    assert removed == [1]  # listeners are notified of the loaded document.
    assert any("failed to render" in text for text in messages)
    assert widget._batch_depth == 0 and not widget._batch_dirty


def test_load_version1_converts_in_one_batch(widget, submissions, tmp_path, monkeypatch):
    add_mixed(widget)
    widget.save(str(tmp_path / "a.qtdw"))
    loaded = pvw_module.read_dict(str(tmp_path / "a.qtdw"))
    temporary = []
    before = []

    def convert(all_data, ver, converter_widget):
        temporary.append(converter_widget)
        before.append(sum(1 for w in submissions if w is converter_widget))  # renders of its initialization.
        for i in range(5):
            converter_widget.add_site(name=f"T{i}")  # the converter adds objects one by one.
        return loaded

    monkeypatch.setattr(pvw_module, "convert_version3", convert)
    old = tmp_path / "old.qtdw"
    old.write_text("{'version': '1.0.0'}")
    submissions.clear()
    widget.load(str(old))
    assert temporary and temporary[0] is not widget
    assert sum(1 for w in submissions if w is temporary[0]) - before[0] == 1
    assert sum(1 for w in submissions if w is widget) == 1
