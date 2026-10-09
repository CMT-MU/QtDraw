"""
Tests for unsaved-change detection and committing typed input.
"""

import pytest
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QFileDialog, QMessageBox, QWidget

from gui_helpers import app, answer  # noqa: F401  (fixture and helper)


def n_sites(window):
    return len(window.pyvista_widget._data["site"].tolist())


# ==================================================
def test_new_window_is_not_modified(app):
    assert not app.is_modified()
    assert not app.windowTitle().endswith("*")


# ==================================================
def test_editing_marks_modified_and_title(app):
    app.pyvista_widget.add_site(position="[0,0,0]")
    assert app.is_modified()
    QTest.qWait(500)
    assert app.windowTitle().endswith(" *")


# ==================================================
def test_view_change_is_not_modification(app):
    app.pyvista_widget.set_view([1, 0, 0])
    app.pyvista_widget.set_grid(True)
    assert not app.is_modified()


# ==================================================
def test_save_and_load_clear_modified(app, monkeypatch, tmp_path):
    app.pyvista_widget.add_site(position="[0,0,0]")
    file = tmp_path / "a.qtdw"
    monkeypatch.setattr(QFileDialog, "getSaveFileName", lambda *a, **k: (str(file), ""))
    app.save_file()
    assert file.exists()
    assert not app.is_modified() and not app.windowTitle().endswith("*")

    app.pyvista_widget.add_site(position="[1/2,0,0]")
    assert app.is_modified()
    app.load_file(str(file))
    assert not app.is_modified() and n_sites(app) == 1


# ==================================================
@pytest.mark.parametrize("button, closed", [(QMessageBox.Cancel, False), (QMessageBox.Discard, True)])
def test_close_asks_to_save(app, monkeypatch, button, closed):
    app.pyvista_widget.add_site(position="[0,0,0]")
    asked = answer(monkeypatch, button)
    app.close()
    assert len(asked) == 1 and "Save changes" in asked[0][2]
    assert app.isVisible() != closed


# ==================================================
def test_close_save_cancelled_keeps_window(app, monkeypatch):
    app.pyvista_widget.add_site(position="[0,0,0]")
    answer(monkeypatch, QMessageBox.Save)
    monkeypatch.setattr(QFileDialog, "getSaveFileName", lambda *a, **k: ("", ""))  # save dialog cancelled.
    app.close()
    assert app.isVisible()


# ==================================================
def test_close_save_writes_file(app, monkeypatch, tmp_path):
    app.pyvista_widget.add_site(position="[0,0,0]")
    file = tmp_path / "saved.qtdw"
    answer(monkeypatch, QMessageBox.Save)
    monkeypatch.setattr(QFileDialog, "getSaveFileName", lambda *a, **k: (str(file), ""))
    app.close()
    assert file.exists() and not app.isVisible()


# ==================================================
def test_unmodified_close_does_not_ask(app, monkeypatch):
    asked = answer(monkeypatch, QMessageBox.Cancel)
    app.close()
    assert asked == [] and not app.isVisible()


# ==================================================
def test_close_after_save_does_not_ask(app, monkeypatch, tmp_path):
    app.pyvista_widget.add_site(position="[0,0,0]")
    file = tmp_path / "saved.qtdw"
    monkeypatch.setattr(QFileDialog, "getSaveFileName", lambda *a, **k: (str(file), ""))
    assert app.save_file()
    asked = answer(monkeypatch, QMessageBox.Cancel)
    app.close()
    assert asked == [] and not app.isVisible()


# ==================================================
@pytest.mark.parametrize("button, remaining", [(QMessageBox.Cancel, 1), (QMessageBox.Discard, 0)])
def test_clear_asks_to_save(app, monkeypatch, button, remaining):
    app.pyvista_widget.add_site(position="[0,0,0]")
    asked = answer(monkeypatch, button)
    app._clear_data()
    assert "Save changes" in asked[0][2]
    assert n_sites(app) == remaining


# ==================================================
def test_open_asks_to_save(app, monkeypatch):
    app.pyvista_widget.add_site(position="[0,0,0]")
    opened = []
    monkeypatch.setattr(QFileDialog, "getOpenFileName", lambda *a, **k: opened.append(True) or ("", ""))
    answer(monkeypatch, QMessageBox.Cancel)
    app.open_file()
    assert opened == []
    answer(monkeypatch, QMessageBox.Discard)
    app.open_file()
    assert opened == [True]


# ==================================================
def focus_away(edit):
    other = QWidget(edit.window())
    other.setFocusPolicy(Qt.StrongFocus)
    other.show()
    other.setFocus()
    QTest.qWait(50)


def type_into(edit, text):
    edit.setFocus()
    QTest.qWait(50)
    edit.selectAll()
    QTest.keyClicks(edit, text)


# ==================================================
def test_panel_value_is_applied_on_focus_out(app):
    type_into(app.uc_edit_a, "2.5")
    focus_away(app.uc_edit_a)
    assert app.pyvista_widget._status["cell"]["a"] == pytest.approx(2.5)
    assert app.uc_edit_a.text() == "2.5000"


# ==================================================
def test_invalid_panel_value_is_discarded_on_focus_out(app):
    type_into(app.uc_edit_a, "abc")
    focus_away(app.uc_edit_a)
    assert app.pyvista_widget._status["cell"]["a"] == pytest.approx(1.0)
    assert app.uc_edit_a.text() == "1.0000"


# ==================================================
def test_table_editor_commits_on_focus_out(qapp):
    from qtdraw.widget.custom_widget import Editor

    host = QWidget()
    editor = Editor(host, "[0,0,0]", validator=("site", {}))
    committed = []
    editor.returnPressed.connect(committed.append)
    host.show()
    QTest.qWaitForWindowExposed(host)
    QTest.mouseDClick(editor, Qt.LeftButton)
    type_into(editor._editor, "[1/2,0,0]")
    focus_away(editor._editor)
    assert committed == ["[1/2,0,0]"]
    host.close()


# ==================================================
def test_pending_input_is_committed_before_close_check(app, monkeypatch):
    app.activateWindow()
    type_into(app.uc_edit_a, "2.5")  # not confirmed by Enter, field keeps focus.
    asked = answer(monkeypatch, QMessageBox.Cancel)
    app.close()
    assert "Save changes" in asked[0][2]  # the typed value is a change.
    assert app.pyvista_widget._status["cell"]["a"] == pytest.approx(2.5)


# ==================================================
def test_cursor_moves_do_not_commit(qapp):
    from qtdraw.widget.custom_widget import LineEdit

    host = QWidget()
    edit = LineEdit(host, "[0,0,0]", validator=("site", {}))
    fired = []
    edit.returnPressed.connect(lambda: fired.append(True))
    host.show()
    QTest.qWaitForWindowExposed(host)
    edit.setFocus()
    QTest.qWait(50)
    for key in [Qt.Key_Left, Qt.Key_Right, Qt.Key_Home, Qt.Key_End]:
        QTest.keyClick(edit, key)
    QTest.keyClick(edit, Qt.Key_C, Qt.ControlModifier)
    focus_away(edit)
    assert fired == []
    host.close()


# ==================================================
def test_read_only_field_does_not_commit(qapp):
    from qtdraw.widget.custom_widget import LineEdit

    host = QWidget()
    edit = LineEdit(host, "[0,0,0]", validator=("site", {}))
    edit.set_read_only(True)
    fired = []
    edit.returnPressed.connect(lambda: fired.append(True))
    host.show()
    QTest.qWaitForWindowExposed(host)
    edit._in_edit = edit._edited = True  # even if flags were set somehow.
    edit.commit_pending()
    assert fired == []
    host.close()


# ==================================================
def test_public_load_and_save_update_baseline(app, tmp_path):
    app.pyvista_widget.add_site(position="[0,0,0]")
    file = tmp_path / "api.qtdw"
    app.save(str(file))
    assert not app.is_modified()

    app.clear_data()
    app.load(str(file))
    assert not app.is_modified()
    app.clear_data()
    assert app.is_modified()  # deleting loaded objects is a change.


# ==================================================
def test_status_change_updates_title(app):
    QTest.mouseClick(app.view_button_clip, Qt.LeftButton)
    QTest.qWait(500)
    assert app.is_modified() and app.windowTitle().endswith(" *")


# ==================================================
def test_escape_cancels_edit_even_after_cursor_moves(qapp):
    from qtdraw.widget.custom_widget import LineEdit

    host = QWidget()
    edit = LineEdit(host, "1.23456789", validator=("float", {"digit": 4}))
    fired = []
    edit.returnPressed.connect(lambda: fired.append(True))
    host.show()
    QTest.qWaitForWindowExposed(host)
    type_into(edit, "2")
    QTest.keyClick(edit, Qt.Key_Escape)
    for key in [Qt.Key_Left, Qt.Key_Home, Qt.Key_End]:
        QTest.keyClick(edit, key)
    edit.commit_pending()
    focus_away(edit)
    assert fired == []
    assert edit.raw_text() == "1.23456789"
    host.close()
