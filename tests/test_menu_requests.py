"""
Tests for the panel and menu changes: DataSet, the Window menu with the data views, no debug panel,
and a resizable error dialog.
"""

import pytest
import shiboken6
from PySide6.QtWidgets import QMessageBox, QPushButton

from gui_helpers import app  # noqa: F401  (fixture)
from qtdraw.util.util import check_multipie


# ==================================================
def panel_buttons(app):
    return [b.text() for b in app.panel.findChildren(QPushButton)]


def test_panel_has_no_preference_and_about_buttons(app):
    texts = panel_buttons(app)
    assert "preference" not in texts and "about" not in texts
    assert "edit" in texts
    assert not hasattr(app, "misc_button_pref") and not hasattr(app, "misc_button_about")
    layout = app.ds_button_edit.parentWidget().layout()
    assert layout.itemAtPosition(0, 0).widget() is app.ds_button_edit
    if check_multipie():
        assert layout.itemAtPosition(0, 1).widget() is app.misc_button_multipie


def test_edit_menu_dataset(app):
    assert app.action_data_table.text() == "&DataSet..."
    app.action_data_table.trigger()
    assert app.pyvista_widget._tab_group_view.isVisible()


# ==================================================
@pytest.mark.parametrize(
    "name, title, expected",
    [
        ("camera", "Camera", "position"),
        ("data", "Data", "=== site ==="),
        ("actor", "Actor", None),  # names depend on the pyvista version, compared below.
        ("status", "Status", "=== plus ==="),
        ("preference", "Preference", "=== general ==="),
    ],
)
def test_window_menu_shows_data_views(app, name, title, expected):
    app.pyvista_widget.add_site(name="S")
    action = app.action_window[name]
    assert action.text().replace("&", "") == title
    action.trigger()
    view = app._data_views[name]
    if expected is None:
        expected = "\n".join(app.pyvista_widget.actor_list)
        assert expected and view.log.toPlainText() == expected
    assert view.isVisible() and expected in view.log.toPlainText(), view.log.toPlainText()[:200]


def test_data_view_is_refreshed_and_reused(app):
    app.action_window["data"].trigger()
    view = app._data_views["data"]
    assert "'T'" not in view.log.toPlainText()
    app.pyvista_widget.add_site(name="T")
    app.action_window["data"].trigger()
    assert app._data_views["data"] is view and "'T'" in view.log.toPlainText()


def test_data_views_do_not_capture_the_log(app):
    import logging

    handlers = list(logging.getLogger().handlers)
    for name in app.action_window:
        if name in ("info", "log"):
            continue
        app.action_window[name].trigger()
    assert logging.getLogger().handlers == handlers


def test_data_views_are_deleted_with_the_window(app, monkeypatch):
    app.action_window["camera"].trigger()
    view = app._data_views["camera"]
    monkeypatch.setattr(QMessageBox, "question", lambda *a, **k: QMessageBox.Discard)
    app.close()
    from gui_helpers import process_deleted

    process_deleted()
    assert not shiboken6.isValid(view)


# ==================================================
def test_no_debug_panel_in_debug_mode(qapp, tmp_path, monkeypatch):
    from qtdraw.core.pyvista_widget_setting import widget_detail
    from qtdraw.core.qtdraw_app import QtDraw

    monkeypatch.chdir(tmp_path)
    monkeypatch.setitem(widget_detail, "log_level", "debug")
    window = QtDraw()
    try:
        assert window.debug
        texts = [b.text() for b in window.panel.findChildren(QPushButton)]
        assert not any(t in texts for t in ["camera", "actor", "data", "status", "pref"]), texts
        assert "camera" in window.action_window
    finally:
        monkeypatch.setattr(QMessageBox, "question", lambda *a, **k: QMessageBox.Discard)
        if shiboken6.isValid(window):
            window.close()


# ==================================================
def test_error_dialog_is_resizable(qapp, monkeypatch):
    from qtdraw.widget import message_box

    shown = []

    def show(self):
        self.show()
        shown.append(self)

    monkeypatch.setattr(QMessageBox, "exec", show)
    message_box.show_error("ValueError: bad", "Traceback ...\n" + "line\n" * 200)
    box = shown[0]
    box.resize(1100, 800)
    qapp.processEvents()
    assert box.width() >= 1000 and box.height() >= 700, (box.width(), box.height())
    assert box.isSizeGripEnabled()
    box.close()
    box.deleteLater()


@pytest.mark.skipif(not check_multipie(), reason="MultiPie is not installed.")
def test_status_view_shows_the_current_multipie_group(app):
    app.pyvista_widget.mp_set_group("D3^4")
    app.action_window["status"].trigger()
    text = app._data_views["status"].log.toPlainText()
    assert "D3^4" in text, text[-600:]


def test_error_dialog_keeps_its_contents_when_shrunk(qapp, monkeypatch):
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import QDialogButtonBox

    from qtdraw.widget import message_box

    shown = []

    def show(self):
        self.show()
        shown.append(self)

    monkeypatch.setattr(QMessageBox, "exec", show)
    message_box.show_error("ValueError: bad", "Traceback ...\n" + "line\n" * 20)
    box = shown[0]
    assert not (box.windowFlags() & Qt.MSWindowsFixedSizeDialogHint)
    box.resize(80, 40)
    qapp.processEvents()
    buttons = box.findChild(QDialogButtonBox)
    assert buttons.height() > 0 and box.width() >= box.layout().totalMinimumSize().width()
    box.close()
    box.deleteLater()


def test_error_dialog_with_details_shown(qapp, monkeypatch):
    from PySide6.QtWidgets import QDialogButtonBox, QTextEdit

    from qtdraw.widget import message_box

    shown = []

    def show(self):
        self.show()
        shown.append(self)

    monkeypatch.setattr(QMessageBox, "exec", show)
    message_box.show_error("ValueError: bad", "Traceback ...\n" + "line\n" * 100)
    box = shown[0]
    qapp.processEvents()
    collapsed = box.minimumHeight()
    toggle = [b for b in box.findChildren(QPushButton) if "Details" in b.text()][0]
    for _ in range(2):  # repeated cycles.
        toggle.click()  # show the details.
        qapp.processEvents()
        details = box.findChild(QTextEdit)
        before = details.height()
        box.resize(1000, 800)
        qapp.processEvents()
        assert details.height() > before + 200  # the details get the extra space.
        box.resize(50, 50)
        qapp.processEvents()
        buttons = box.findChild(QDialogButtonBox)
        assert buttons.height() > 0 and buttons.geometry().bottom() <= box.height()
        toggle.click()  # hide the details.
        qapp.processEvents()
        assert box.minimumHeight() <= collapsed + 5  # the minimum follows the hidden details.
    box.close()
    box.deleteLater()


def test_data_view_reopened_after_closing(app):
    import sys

    hook = sys.excepthook
    app.action_window["actor"].trigger()
    view = app._data_views["actor"]
    view.close()
    app.action_window["actor"].trigger()
    assert app._data_views["actor"] is view and view.isVisible()
    assert sys.excepthook is hook


def test_status_text_of_old_files(app):
    pvw = app.pyvista_widget
    pvw._mp_data = None
    for multipie in [{}, {"version": "1.0"}, {"version": "1.0", "group": {"group": "C1"}}]:
        pvw._status["multipie"] = multipie
        text = app._status_text()
        assert "=== multipie ===" in text and "=== multipie.plus ===" in text
