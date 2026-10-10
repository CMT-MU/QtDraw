"""
Tests for Save / Save As, Open Recent, and the Edit, View and Help menus.
"""

import pytest
from PySide6.QtCore import QUrl
from PySide6.QtGui import QAction, QDesktopServices, QKeySequence
from PySide6.QtWidgets import QFileDialog, QMessageBox

from gui_helpers import app, answer  # noqa: F401  (fixture and helper)
from qtdraw.core.pyvista_widget_setting import COLUMN_CELL


def save_dialog(monkeypatch, file):
    shown = []
    monkeypatch.setattr(QFileDialog, "getSaveFileName", lambda *a, **k: (shown.append(a), (str(file), ""))[1])
    return shown


def n_sites(app):
    return len(app.pyvista_widget.get_data_dict().get("site", []))


def menu_texts(menu):
    return [a.text() for a in menu.actions() if not a.isSeparator()]


def submenu(app, title):
    for action in app.menuBar().actions():
        if action.text() == title:
            return action.menu()
    raise KeyError(title)


# ==================================================
# Save / Save As.
# ==================================================
def test_save_as_has_standard_shortcut(app):
    assert app.action_save_as.shortcut() == QKeySequence(QKeySequence.SaveAs)


def test_save_without_file_asks_for_a_name(app, monkeypatch, tmp_path):
    shown = save_dialog(monkeypatch, tmp_path / "a.qtdw")
    app.action_save.trigger()
    assert len(shown) == 1 and (tmp_path / "a.qtdw").exists()


def test_save_writes_to_the_current_file_without_dialog(app, monkeypatch, tmp_path):
    save_dialog(monkeypatch, tmp_path / "a.qtdw")
    app.action_save.trigger()
    app.pyvista_widget.add_site()
    shown = save_dialog(monkeypatch, tmp_path / "other.qtdw")
    app.action_save.trigger()
    assert shown == [] and not (tmp_path / "other.qtdw").exists()
    assert not app.is_modified()
    app.load_file(str(tmp_path / "a.qtdw"))
    assert n_sites(app) == 1


def test_save_after_opening_overwrites_the_opened_file(app, monkeypatch, tmp_path):
    file = tmp_path / "a.qtdw"
    app.pyvista_widget.save(str(file))
    app.load_file(str(file))
    app.pyvista_widget.add_site()
    shown = save_dialog(monkeypatch, tmp_path / "other.qtdw")
    app.action_save.trigger()
    assert shown == []
    app.load_file(str(file))
    assert n_sites(app) == 1


def test_save_as_always_asks_and_changes_the_current_file(app, monkeypatch, tmp_path):
    save_dialog(monkeypatch, tmp_path / "a.qtdw")
    app.action_save.trigger()
    shown = save_dialog(monkeypatch, tmp_path / "b.qtdw")
    app.action_save_as.trigger()
    assert len(shown) == 1 and (tmp_path / "b.qtdw").exists()
    app.pyvista_widget.add_site()
    shown = save_dialog(monkeypatch, tmp_path / "c.qtdw")
    app.action_save.trigger()  # to b.qtdw.
    assert shown == []
    app.load_file(str(tmp_path / "b.qtdw"))
    assert n_sites(app) == 1


def test_cancelled_save_as_keeps_the_current_file(app, monkeypatch, tmp_path):
    save_dialog(monkeypatch, tmp_path / "a.qtdw")
    app.action_save.trigger()
    monkeypatch.setattr(QFileDialog, "getSaveFileName", lambda *a, **k: ("", ""))
    app.action_save_as.trigger()
    shown = save_dialog(monkeypatch, tmp_path / "other.qtdw")
    app.action_save.trigger()
    assert shown == []


def test_save_after_importing_a_material_asks_for_a_name(app, monkeypatch, tmp_path):
    from grid_helpers import write_small_xsf

    material = tmp_path / "m.xsf"
    write_small_xsf(material)
    before = material.read_bytes()
    app.load_file(str(material))
    shown = save_dialog(monkeypatch, tmp_path / "m.qtdw")
    app.action_save.trigger()
    assert len(shown) == 1 and material.read_bytes() == before  # the material file is not overwritten.


def test_failed_open_keeps_the_current_file(app, monkeypatch, tmp_path):
    save_dialog(monkeypatch, tmp_path / "a.qtdw")
    app.action_save.trigger()
    (tmp_path / "broken.qtdw").write_text("{")
    with pytest.raises(Exception):
        app.load_file(str(tmp_path / "broken.qtdw"))
    shown = save_dialog(monkeypatch, tmp_path / "other.qtdw")
    app.action_save.trigger()
    assert shown == []


def test_closing_with_changes_saves_to_the_current_file(app, monkeypatch, tmp_path):
    save_dialog(monkeypatch, tmp_path / "a.qtdw")
    app.action_save.trigger()
    app.pyvista_widget.add_site()
    answer(monkeypatch, QMessageBox.Save)
    shown = save_dialog(monkeypatch, tmp_path / "other.qtdw")
    app.close()
    assert shown == [] and not app.isVisible()


# ==================================================
# Open Recent.
# ==================================================
def recent_entries(app):
    menu = app.menu_recent
    menu.aboutToShow.emit()
    return [a for a in menu.actions() if not a.isSeparator()]


def test_open_recent_lists_opened_and_saved_files(app, monkeypatch, tmp_path):
    a, b = tmp_path / "a.qtdw", tmp_path / "b.qtdw"
    app.pyvista_widget.save(str(a))
    app.load_file(str(a))
    save_dialog(monkeypatch, b)
    app.action_save_as.trigger()
    texts = [x.text() for x in recent_entries(app)]
    assert texts[:2] == ["b.qtdw", "a.qtdw"] and texts[-1] == "Clear Menu"


def test_open_recent_keeps_ten_files_without_duplicates(app, tmp_path):
    for i in range(12):
        file = tmp_path / f"f{i}.qtdw"
        app.pyvista_widget.save(str(file))
        app.load_file(str(file))
    app.load_file(str(tmp_path / "f5.qtdw"))
    texts = [x.text() for x in recent_entries(app)][:-1]
    assert len(texts) == 10 and texts[0] == "f5.qtdw" and texts.count("f5.qtdw") == 1


def test_open_recent_skips_missing_files_and_opens_a_file(app, tmp_path):
    a, b = tmp_path / "a.qtdw", tmp_path / "b.qtdw"
    app.pyvista_widget.add_site()
    app.pyvista_widget.save(str(a))
    app.pyvista_widget.save(str(b))
    app.load_file(str(a))
    app.load_file(str(b))
    b.unlink()
    app.pyvista_widget.clear_data()
    app._mark_saved()
    entries = recent_entries(app)
    assert [x.text() for x in entries] == ["a.qtdw", "Clear Menu"]
    entries[0].trigger()
    assert n_sites(app) == 1


def test_open_recent_asks_to_save_changes(app, tmp_path, monkeypatch):
    a = tmp_path / "a.qtdw"
    app.pyvista_widget.save(str(a))
    app.load_file(str(a))
    app.pyvista_widget.add_site()
    asked = answer(monkeypatch, QMessageBox.Cancel)
    recent_entries(app)[0].trigger()
    assert len(asked) == 1 and n_sites(app) == 1  # not opened.


def test_open_recent_clear_menu(app, tmp_path):
    a = tmp_path / "a.qtdw"
    app.pyvista_widget.save(str(a))
    app.load_file(str(a))
    recent_entries(app)[-1].trigger()  # Clear Menu.
    entries = recent_entries(app)
    assert [x.text() for x in entries] == ["No Recent Files"] and not entries[0].isEnabled()


def test_recent_files_are_shared_with_a_new_window(app, qapp, tmp_path, monkeypatch):
    import shiboken6
    from qtdraw.core.qtdraw_app import QtDraw

    a = tmp_path / "a.qtdw"
    app.pyvista_widget.save(str(a))
    app.load_file(str(a))
    other = QtDraw()
    try:
        assert [x.text() for x in recent_entries(other)][0] == "a.qtdw"
    finally:
        monkeypatch.setattr(QMessageBox, "question", lambda *a, **k: QMessageBox.Discard)
        if shiboken6.isValid(other):
            other.close()


# ==================================================
# Edit menu.
# ==================================================
def test_edit_menu_opens_data_table_and_preferences(app, monkeypatch):
    shown = []
    monkeypatch.setattr(app, "_show_preference", lambda: shown.append("pref"))
    app.action_data_table.trigger()
    assert app.pyvista_widget._tab_group_view.isVisible()
    assert app.action_preferences.shortcut() == QKeySequence(QKeySequence.Preferences)
    assert app.action_preferences.menuRole() == QAction.PreferencesRole
    app.action_preferences.trigger()
    assert shown == ["pref"]


# ==================================================
# View menu.
# ==================================================
def test_menu_titles(app):
    assert [a.text() for a in app.menuBar().actions()] == ["&File", "&Edit", "&View", "&Window", "&Help"]


def test_view_directions(app):
    pvw = app.pyvista_widget
    app.action_view["-y"].trigger()
    assert pvw._status["view"] == [0, -1, 0]
    assert app.action_view["+x"].shortcut() == QKeySequence("Ctrl+1")
    assert app.action_view["default"].shortcut() == QKeySequence("Ctrl+0")
    app.action_view["default"].trigger()
    from qtdraw.core.pyvista_widget_setting import default_status

    assert pvw._status["view"] == default_status["view"]


@pytest.mark.parametrize(
    "name, key, button",
    [
        ("parallel", "parallel_projection", "view_button_parallel"),
        ("grid", "grid", "view_button_grid"),
        ("bar", "bar", "view_button_bar"),
        ("clip", "clip", "view_button_clip"),
        ("repeat", "repeat", "view_button_repeat"),
    ],
)
def test_view_toggles_follow_and_drive_the_panel(app, name, key, button):
    pvw = app.pyvista_widget
    action = app.action_toggle[name]
    before = pvw._status[key]
    action.trigger()
    assert pvw._status[key] == (not before) and getattr(app, button).isChecked() == (not before)
    getattr(app, button).click()  # from the panel.
    assert pvw._status[key] == before and action.isChecked() == before


def test_view_axis_and_cell_follow_and_drive_the_panel(app):
    pvw = app.pyvista_widget
    app.action_axis["full"].trigger()
    assert pvw._status["axis_type"] == "full" and app.view_combo_axis.currentText() == "full"
    app.view_combo_axis.setCurrentText("off")
    assert app.action_axis["off"].isChecked() and not app.action_axis["full"].isChecked()
    app.action_cell["all"].trigger()
    assert pvw._status["cell_mode"] == "all" and app.view_combo_cell.currentText() == "all"
    app.view_combo_cell.setCurrentText("off")
    assert app.action_cell["off"].isChecked()


def test_view_menu_follows_a_loaded_file(app, tmp_path):
    pvw = app.pyvista_widget
    pvw.set_grid(True)
    pvw.set_axis("off")
    pvw.save(str(tmp_path / "a.qtdw"))
    pvw.set_grid(False)
    pvw.set_axis("on")
    app._update_panel()
    app.load_file(str(tmp_path / "a.qtdw"))
    assert app.action_toggle["grid"].isChecked() and app.action_axis["off"].isChecked()


def test_view_nonrepeat(app, monkeypatch):
    pvw = app.pyvista_widget
    answer(monkeypatch, QMessageBox.Ok)
    pvw.add_site()
    pvw.set_range("[0,0,0]", "[1,1,1]")
    app.action_toggle["repeat"].trigger()
    n = n_sites(app)
    app.action_nonrepeat.trigger()  # repeated copies become independent objects in the home cell.
    rows = pvw.get_data_dict()["site"]
    assert n > 1 and len(rows) == n and all(row[COLUMN_CELL] == "[0,0,0]" for row in rows)


# ==================================================
# Help menu.
# ==================================================
def test_help_links(app, monkeypatch):
    opened = []
    monkeypatch.setattr(QDesktopServices, "openUrl", lambda url: opened.append(QUrl(url).toString()))
    app.action_documentation.trigger()
    app.action_report_issue.trigger()
    assert opened == ["https://cmt-mu.github.io/QtDraw/", "https://github.com/CMT-MU/QtDraw/issues"]
