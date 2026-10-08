"""
Tests for usability improvements in the main window.
"""

from pathlib import Path

import pytest
from PySide6.QtWidgets import QFileDialog, QMessageBox


# ==================================================
@pytest.fixture
def app(qapp, tmp_path, monkeypatch):
    from qtdraw.core.qtdraw_app import QtDraw

    monkeypatch.chdir(tmp_path)
    window = QtDraw()
    yield window
    monkeypatch.setattr(QMessageBox, "question", lambda *a, **k: QMessageBox.Ok)  # "Quit QtDraw ?".
    window.close()


def answer(monkeypatch, button):
    asked = []

    def question(*args, **kwargs):
        asked.append(args)
        return button

    monkeypatch.setattr(QMessageBox, "question", question)
    return asked


# ==================================================
def test_screenshot_cancel_does_nothing(app, monkeypatch):
    messages = []
    app.pyvista_widget.message.connect(messages.append)
    monkeypatch.setattr(QFileDialog, "getSaveFileName", lambda *a, **k: ("", ""))
    app._save_screenshot()
    assert not any("screenshot" in m for m in messages)


# ==================================================
@pytest.mark.parametrize(
    "name, selected, expected",
    [("shot", "Image Files", "shot.png"), ("shot", "Graphic Files", "shot.svg"), ("shot.png", "", "shot.png")],
)
def test_screenshot_adds_extension(app, monkeypatch, tmp_path, name, selected, expected):
    saved = []
    monkeypatch.setattr(app.pyvista_widget, "save_screenshot", saved.append)
    filters = {
        "Image Files": "Image Files (*.png *.bmp *.tif *.tiff)",
        "Graphic Files": "Graphic Files (*.svg *.eps *.ps *.pdf)",
        "": "",
    }
    monkeypatch.setattr(QFileDialog, "getSaveFileName", lambda *a, **k: (str(tmp_path / name), filters[selected]))
    app._save_screenshot()
    assert [Path(p).name for p in saved] == [expected]


# ==================================================
def test_screenshot_unknown_type_is_error(app, tmp_path):
    messages = []
    app.pyvista_widget.message.connect(messages.append)
    with pytest.raises(ValueError):
        app.pyvista_widget.save_screenshot(str(tmp_path / "shot.txt"))
    assert not any("screenshot" in m for m in messages)


# ==================================================
@pytest.mark.parametrize("button, called", [(QMessageBox.Cancel, False), (QMessageBox.Ok, True)])
def test_nonrepeat_asks_confirmation(app, monkeypatch, button, called):
    done = []
    monkeypatch.setattr(app.pyvista_widget, "nonrepeat_data", lambda: done.append(True))
    asked = answer(monkeypatch, button)
    app._nonrepeat()
    assert len(asked) == 1
    assert bool(done) == called
    assert app.view_button_nonrepeat.toolTip() != ""


# ==================================================
@pytest.mark.parametrize(
    "vtype, option, words",
    [
        ("int", {"min": 0, "max": "*"}, ["Integer", "≥ 0"]),
        ("float", {"min": 0.0, "max": 1.0}, ["Number", "0.0 to 1.0"]),
        ("list_float", {"shape": (3,), "var": [""]}, ["3 numbers", "[0,0,0]", "1/2"]),
        ("list_int", {"shape": (3,)}, ["3 integers"]),
        ("math", {"shape": (), "var": ["x", "y"]}, ["Math expression", "x, y"]),
        ("site", {"use_var": True}, ["[x,y,z]", "x, y, z can be used"]),
        ("bond", {}, ["[tail];[head]", "@", ":"]),
        ("site_bond", {}, ["Site", "bond"]),
        ("vector_site_bond", {}, ["#"]),
        ("orbital_site_bond", {}, ["#", "x, y, z, r"]),
    ],
)
def test_validator_hint(vtype, option, words):
    from qtdraw.widget.validator import validator_hint

    hint = validator_hint(vtype, option)
    for w in words:
        assert w in hint, hint


# ==================================================
def test_line_edit_has_hint_tooltip(qapp):
    from qtdraw.widget.custom_widget import LineEdit, Editor

    edit = LineEdit(None, "[0,0,0]", validator=("list_float", {"shape": (3,), "var": [""]}))
    assert "3 numbers" in edit.toolTip()
    editor = Editor(None, "[0,0,0]", validator=("site", {}))
    assert "[x,y,z]" in editor.toolTip()
    assert LineEdit(None, "abc").toolTip() == ""  # no validator, no hint.


# ==================================================
def test_main_panel_fields_have_hints(app):
    for edit in [app.uc_edit_origin, app.uc_edit_a, app.view_edit_lower, app.view_edit_upper]:
        assert edit.toolTip() != ""


# ==================================================
def test_busy_cursor_is_restored(qapp):
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import QApplication
    from qtdraw.widget.qt_event_util import busy_cursor, with_busy_cursor

    @with_busy_cursor
    def work():
        return QApplication.overrideCursor().shape()

    assert work() == Qt.WaitCursor
    assert work.__name__ == "work"
    assert QApplication.overrideCursor() is None

    with pytest.raises(RuntimeError):
        with busy_cursor():
            raise RuntimeError("failed")
    assert QApplication.overrideCursor() is None  # restored even on error.


# ==================================================
def test_long_operations_show_wait_cursor(app, monkeypatch):
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import QApplication

    shapes = []
    record = lambda *a, **k: shapes.append(QApplication.overrideCursor() and QApplication.overrideCursor().shape())
    monkeypatch.setattr(app.pyvista_widget, "load", record)
    monkeypatch.setattr(app.pyvista_widget, "nonrepeat_data", record)
    monkeypatch.setattr(app, "_update_panel", lambda: None)
    answer(monkeypatch, QMessageBox.Ok)

    app.load_file("dummy.qtdw")
    app._nonrepeat()
    assert shapes == [Qt.WaitCursor, Qt.WaitCursor]
    assert QApplication.overrideCursor() is None


# ==================================================
def test_multipie_info_dialogs_show_wait_cursor():
    import inspect
    from qtdraw.multipie import multipie_info_dialog as m

    functions = [f for name, f in inspect.getmembers(m, inspect.isfunction) if name.startswith("show_")]
    assert len(functions) == 14
    assert all(hasattr(f, "__wrapped__") for f in functions)


# ==================================================
def test_font_family_falls_back_to_system_font(qapp):
    from PySide6.QtGui import QFontDatabase
    from qtdraw.widget.qt_event_util import font_family, font_style_sheet

    installed = QFontDatabase.families()[0]
    system = QFontDatabase.systemFont(QFontDatabase.GeneralFont).family()
    assert font_family(installed) == installed
    assert font_family("No Such Font 123") == system
    assert font_style_sheet("No Such Font 123", 13) == 'QWidget { font-family: "' + system + '"; font-size: 13pt; }'


# ==================================================
def test_preference_lists_installed_fonts(app):
    from PySide6.QtGui import QFontDatabase
    from PySide6.QtWidgets import QComboBox
    from qtdraw.core.dialog_preference import PreferenceDialog

    dialog = PreferenceDialog(app.pyvista_widget, app)
    items = set()
    for combo in dialog.findChildren(QComboBox):
        items |= {combo.itemText(i) for i in range(combo.count())}
    assert set(QFontDatabase.families()) <= items
    assert app.pyvista_widget._preference["general"]["font"] in items
    dialog.close()


# ==================================================
@pytest.mark.parametrize(
    "shape, words, absent",
    [
        ((0,), ["any length", "[1]"], ["0 integers", "[]"]),
        ((3, 0), ["(3, n)", "any length"], []),
        ((2, 3), ["(2, 3)"], ["any length"]),
    ],
)
def test_validator_hint_variable_length(shape, words, absent):
    from qtdraw.widget.validator import validator_hint

    hint = validator_hint("list_int", {"shape": shape})
    for w in words:
        assert w in hint, hint
    for w in absent:
        assert w not in hint, hint


# ==================================================
@pytest.mark.parametrize("button, saved_expected", [(QMessageBox.Cancel, []), (QMessageBox.Ok, ["a.jpg.png"])])
def test_screenshot_asks_before_replacing_renamed_file(app, monkeypatch, tmp_path, button, saved_expected):
    (tmp_path / "a.jpg.png").write_text("existing")
    saved = []
    monkeypatch.setattr(app.pyvista_widget, "save_screenshot", saved.append)
    monkeypatch.setattr(QFileDialog, "getSaveFileName", lambda *a, **k: (str(tmp_path / "a.jpg"), "Image Files (*.png)"))
    asked = answer(monkeypatch, button)
    app._save_screenshot()
    assert len(asked) == 1
    assert [Path(p).name for p in saved] == saved_expected


# ==================================================
def test_screenshot_does_not_ask_when_renamed_file_is_new(app, monkeypatch, tmp_path):
    saved = []
    monkeypatch.setattr(app.pyvista_widget, "save_screenshot", saved.append)
    monkeypatch.setattr(QFileDialog, "getSaveFileName", lambda *a, **k: (str(tmp_path / "b"), "Image Files (*.png)"))
    asked = answer(monkeypatch, QMessageBox.Cancel)
    app._save_screenshot()
    assert asked == []
    assert [Path(p).name for p in saved] == ["b.png"]
