"""
Regression tests for the menu bar, standard shortcuts, tool tips and help (#182).
"""

from PySide6.QtGui import QKeySequence
from PySide6.QtWidgets import QFileDialog, QMessageBox

from gui_helpers import app, answer  # noqa: F401  (fixture and helper)


# ==================================================
def test_menu_has_standard_shortcuts(app):
    assert app.action_open.shortcut() == QKeySequence(QKeySequence.Open)
    assert app.action_save.shortcut() == QKeySequence(QKeySequence.Save)
    assert app.action_quit.shortcut() == QKeySequence(QKeySequence.Quit)
    titles = [a.text() for a in app.menuBar().actions()]
    assert titles == ["&File", "&Edit", "&Window", "&Help"]


# ==================================================
def test_open_and_save_actions_show_file_dialogs(app, monkeypatch):
    opened, saved = [], []
    monkeypatch.setattr(QFileDialog, "getOpenFileName", lambda *a, **k: (opened.append(a), ("", ""))[1])
    monkeypatch.setattr(QFileDialog, "getSaveFileName", lambda *a, **k: (saved.append(a), ("", ""))[1])

    app.action_open.trigger()
    app.action_save.trigger()

    assert len(opened) == 1 and len(saved) == 1


# ==================================================
def test_quit_action_asks_before_closing(app, monkeypatch):
    asked = answer(monkeypatch, QMessageBox.Cancel)
    app.show()

    app.action_quit.trigger()

    assert len(asked) == 1 and app.isVisible()  # cancelled.


# ==================================================
def test_help_explains_mouse_and_keys(app, monkeypatch):
    shown = []
    monkeypatch.setattr(QMessageBox, "information", lambda *args, **kwargs: shown.append(args))

    app.action_help.trigger()

    text = shown[0][2]
    assert "Right click" in text and "data table" in text and "Esc" in text and "create or copy" in text


# ==================================================
def test_buttons_have_tool_tips(app):
    buttons = [
        app.ds_button_edit,
        app.misc_button_pref,
        app.misc_button_about,
        app.view_button_default,
        app.view_button_clip,
        app.view_button_repeat,
        app.view_button_nonrepeat,
    ]
    assert all(b.toolTip() for b in buttons)
    assert "can be undone with Undo" in app.view_button_nonrepeat.toolTip()  # an existing tool tip is kept.
