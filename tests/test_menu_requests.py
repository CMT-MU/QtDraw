"""
Tests for the panel and menu changes: DataSet, the Window menu with the data views, no debug panel,
and a resizable error dialog.
"""

import os
import sys
from pathlib import Path

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


# ==================================================
def test_only_quit_preferences_and_about_move_to_the_application_menu(app):
    from PySide6.QtGui import QAction
    from PySide6.QtWidgets import QMenu

    roles = {}
    for menu in app.findChildren(QMenu):  # not QAction.menu(): with PySide6 6.9 it deletes the menu.
        for action in menu.actions():
            if action.text():
                roles[action.text().replace("&", "")] = action.menuRole()
    moved = {text: role for text, role in roles.items() if role != QAction.NoRole}
    assert moved == {
        "Quit": QAction.QuitRole,
        "Preferences...": QAction.PreferencesRole,
        "About QtDraw": QAction.AboutRole,
    }, moved
    assert shiboken6.isValid(app.menu_recent)


@pytest.mark.skipif(sys.platform != "darwin", reason="the application menu is on macOS only.")
def test_application_menu_is_named_qtdraw():
    import subprocess
    import textwrap

    code = textwrap.dedent("""
        from qtdraw.widget.qt_event_util import get_qt_application, macos_bundle_name
        get_qt_application()
        print("NAME", macos_bundle_name())
        """)
    env = {**os.environ, "QT_QPA_PLATFORM": "offscreen"}
    ret = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, timeout=60, env=env)
    assert ret.returncode == 0, ret.stdout + ret.stderr
    assert "NAME QtDraw" in ret.stdout, ret.stdout + ret.stderr


# ==================================================
@pytest.fixture
def no_multipie(monkeypatch):
    import qtdraw.core.pyvista_widget as pvw_module
    import qtdraw.core.qtdraw_app as app_module

    for module in (pvw_module, app_module):
        monkeypatch.setattr(module, "check_multipie", lambda: False)


def test_multipie_button_is_always_shown(qapp, tmp_path, monkeypatch, no_multipie):
    from qtdraw.core.qtdraw_app import QtDraw

    monkeypatch.chdir(tmp_path)
    window = QtDraw()
    try:
        assert "MultiPie" in [b.text() for b in window.panel.findChildren(QPushButton)]
        shown = []
        monkeypatch.setattr(QMessageBox, "information", lambda *a, **k: shown.append(a[2]) or QMessageBox.Ok)
        window.misc_button_multipie.click()
        assert len(shown) == 1 and "pip install multipie" in shown[0]
        assert window.multipie_dialog is None
    finally:
        monkeypatch.setattr(QMessageBox, "question", lambda *a, **k: QMessageBox.Discard)
        if shiboken6.isValid(window):
            window.close()


def test_opening_a_multipie_drawing_asks_to_install(widget, tmp_path, monkeypatch):
    if not check_multipie():
        pytest.skip("a drawing with a MultiPie group is written with MultiPie.")
    widget.mp_set_group("Ci")
    widget.save(str(tmp_path / "mp.qtdw"))
    widget.mp_set_group("C2h")  # the current drawing, kept when opening fails.
    import qtdraw.core.pyvista_widget as pvw_module

    monkeypatch.setattr(pvw_module, "check_multipie", lambda: False)
    with pytest.raises(Exception, match="mp.qtdw uses MultiPie.*pip install multipie"):
        widget.load(str(tmp_path / "mp.qtdw"))
    assert "C2h" in str(widget._mp_data.status)


def test_multipie_methods_ask_to_install(widget, no_multipie):
    with pytest.raises(Exception, match="pip install multipie"):
        widget.mp_set_group("Ci")


def test_no_menu_role_in_submenus_and_recent_files(app, tmp_path):
    from PySide6.QtGui import QAction

    for name in ["Preferences.qtdw", "About.qtdw", "Quit.qtdw"]:
        app.pyvista_widget.save(str(tmp_path / name))
        app.load_file(str(tmp_path / name))
    app.menu_recent.aboutToShow.emit()
    from PySide6.QtWidgets import QMenu

    special = {app.action_quit, app.action_preferences, app.action_about}
    for menu in app.findChildren(QMenu):  # also the submenus and the recent files.
        for action in menu.actions():
            if action not in special and not action.isSeparator():
                assert action.menuRole() == QAction.NoRole, action.text()


@pytest.mark.skipif(sys.platform != "darwin", reason="the application menu is on macOS only.")
@pytest.mark.parametrize("existing", [False, True])
def test_application_name_with_an_application_created_by_ipython(existing):
    import subprocess
    import textwrap

    code = textwrap.dedent(f"""
        import sys
        from PySide6.QtWidgets import QApplication
        import qtdraw.widget.qt_event_util as util
        if {existing}:  # an application that existed before.
            app = QApplication(sys.argv)
            app.setApplicationName("Other")
        util.gui_qt = lambda: QApplication.instance() or QApplication(sys.argv)  # as IPython's Qt integration.
        app = util.get_qt_application()
        print("NAME", util.macos_bundle_name(), app.applicationName())
        """)
    env = {**os.environ, "QT_QPA_PLATFORM": "offscreen"}
    ret = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, timeout=60, env=env)
    assert ret.returncode == 0, ret.stdout + ret.stderr
    bundle, name = ret.stdout.split("NAME ")[1].split()[:2]
    if existing:
        assert name == "Other"  # an application that existed before keeps its name.
    else:
        assert (bundle, name) == ("QtDraw", "QtDraw")


def test_qtdraw_starts_without_multipie():
    import subprocess
    import textwrap

    code = textwrap.dedent("""
        import sys
        sys.modules["multipie"] = None  # MultiPie is not installed: importing it fails.
        from PySide6.QtWidgets import QMessageBox
        from qtdraw.core.qtdraw_app import QtDraw
        from qtdraw.util.util import check_multipie
        assert not check_multipie()
        shown = []
        QMessageBox.information = lambda *a, **k: shown.append(a[2]) or QMessageBox.Ok
        QMessageBox.question = lambda *a, **k: QMessageBox.Discard
        window = QtDraw()
        window.pyvista_widget.add_site()
        window.misc_button_multipie.click()
        assert "pip install multipie" in shown[0], shown
        window.close()
        print("OK")
        """)
    env = {**os.environ, "QT_QPA_PLATFORM": "offscreen"}
    ret = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, timeout=120, env=env)
    assert ret.returncode == 0 and "OK" in ret.stdout, ret.stdout + ret.stderr[-2000:]


def test_rejected_multipie_drawing_keeps_the_table_and_backup(widget, tmp_path, monkeypatch):
    if not check_multipie():
        pytest.skip("a drawing with a MultiPie group is written with MultiPie.")
    widget.mp_set_group("Ci")
    widget.save(str(tmp_path / "mp.qtdw"))
    widget.add_site(name="kept")
    widget.open_tab_group_view()
    backup = repr(getattr(widget, "_backup", None))
    import qtdraw.core.pyvista_widget as pvw_module

    monkeypatch.setattr(pvw_module, "check_multipie", lambda: False)
    with pytest.raises(Exception, match="uses MultiPie"):
        widget.load(str(tmp_path / "mp.qtdw"))
    assert widget._tab_group_view.isVisible()  # nothing was changed before the drawing was rejected.
    assert repr(getattr(widget, "_backup", None)) == backup
    assert [row[0] for row in widget.get_data_dict()["site"]] == ["kept"]


def test_version1_drawing_with_multipie_is_rejected_without_it(widget, tmp_path, monkeypatch, no_multipie):
    import qtdraw.core.pyvista_widget as pvw_module

    converted = []
    monkeypatch.setattr(pvw_module, "convert_version3", lambda *a: converted.append(1))
    file = tmp_path / "old.qtdw"
    file.write_text("{'version': '1.0.0', 'multipie': {'group': {'group': 'C1'}}}")  # MultiPie data at the top level.
    with pytest.raises(Exception, match="old.qtdw uses MultiPie"):
        widget.load(str(file))
    assert converted == []  # rejected before the conversion.


@pytest.mark.parametrize("answer_button, replaced", [(QMessageBox.Cancel, False), (QMessageBox.Ok, True)])
def test_save_as_asks_before_replacing_the_file_with_the_added_extension(app, tmp_path, monkeypatch, answer_button, replaced):
    from PySide6.QtWidgets import QFileDialog

    target = tmp_path / "existing.txt.qtdw"
    target.write_text("old")
    monkeypatch.setattr(QFileDialog, "getSaveFileName", lambda *a, **k: (str(tmp_path / "existing.txt"), ""))
    asked = []
    monkeypatch.setattr(QMessageBox, "question", lambda *a, **k: asked.append(a[2]) or answer_button)
    app.pyvista_widget.add_site()
    assert app.save_file_as() == replaced
    assert len(asked) == 1 and "existing.txt.qtdw" in asked[0]
    assert (target.read_text() != "old") == replaced


# ==================================================
@pytest.mark.parametrize("name", ["Si.cif", "Si.vesta", "Si.xsf"])
def test_material_file_opens_without_multipie(widget, monkeypatch, name):
    import qtdraw.parser.util_parser as parser_module
    import qtdraw.core.pyvista_widget as pvw_module

    for module in (parser_module, pvw_module):
        monkeypatch.setattr(module, "check_multipie", lambda: False, raising=False)
    widget.load(str(Path(__file__).resolve().parents[1] / "docs" / "src" / "examples" / name))
    assert widget._status["crystal"] == "cubic"
    assert widget._data["site"].rowCount() > 0
    assert not widget._status.get("multipie") and widget._mp_data is None  # nothing of MultiPie to lose by saving.


# ==================================================
def test_material_file_sets_its_space_group_with_multipie(widget):
    if not check_multipie():
        pytest.skip("MultiPie is not installed.")
    widget.load(str(Path(__file__).resolve().parents[1] / "docs" / "src" / "examples" / "Si.cif"))
    assert widget._mp_data.status["group"]["tag"] == "SG:227"
