"""
Tests for the right panel, the Window menu, the fixed style and the close question.
"""

from PySide6.QtWidgets import QFileDialog, QLabel, QMessageBox

from gui_helpers import app, answer  # noqa: F401  (fixture and helper)
from qtdraw.util.util import check_multipie


# ==================================================
def test_panel_has_edit_preference_about_multipie(app):
    for name in ["ds_button_clear", "ds_button_load", "ds_button_save", "ds_button_screenshot"]:
        assert not hasattr(app, name)
    for name in ["misc_button_info", "misc_button_log"]:
        assert not hasattr(app, name)

    layout = app.ds_button_edit.parentWidget().layout()
    assert layout.itemAtPosition(0, 0).widget() is app.ds_button_edit
    assert layout.itemAtPosition(0, 1).widget() is app.misc_button_pref
    assert layout.itemAtPosition(1, 0).widget() is app.misc_button_about
    if check_multipie():
        assert layout.itemAtPosition(1, 1).widget() is app.misc_button_multipie

    texts = [label.text() for label in app.findChildren(QLabel)]
    assert not any(t in ("DataSet", "Misc") for t in texts)


# ==================================================
def test_window_menu_opens_info_and_log(app):
    titles = [a.text() for a in app.menuBar().actions()]
    assert titles == ["&File", "&Edit", "&Window", "&Help"]

    app.action_info.trigger()
    assert app.info_dialog.isVisible()
    app.action_log.trigger()
    assert app.logger.isVisible()


# ==================================================
def test_style_is_fusion_and_not_a_preference(app, monkeypatch):
    from qtdraw.core.dialog_preference import PreferenceDialog

    pvw = app.pyvista_widget
    assert "style" not in pvw._preference["general"]
    pvw.set_property(preference={"general": {"style": "windows"}})  # e.g. from an old file.
    assert "style" not in pvw._preference["general"]
    styles = []
    monkeypatch.setattr(app.app, "setStyle", lambda style: styles.append(style))
    app._update_application()
    assert styles == ["fusion"]

    dialog = PreferenceDialog(pvw, app)
    assert "style" not in [label.text() for label in dialog.findChildren(QLabel)]
    dialog.deleteLater()


# ==================================================
def test_close_without_changes_quits_without_asking(app, monkeypatch):
    asked = answer(monkeypatch, QMessageBox.Cancel)
    app.close()
    assert asked == [] and not app.isVisible()


# ==================================================
def test_window_opens_with_default_size(app):
    from qtdraw.core.pyvista_widget_setting import widget_detail

    width, height = widget_detail["window_size"]
    assert (width, height) == (1000, 626)  # the height before the panel had fewer buttons.
    app.show()
    assert app.width() >= width and app.height() >= height


# ==================================================
def test_window_size_setting_is_used(qapp, tmp_path, monkeypatch):
    import shiboken6
    from qtdraw.core.pyvista_widget_setting import widget_detail
    from qtdraw.core.qtdraw_app import QtDraw

    monkeypatch.chdir(tmp_path)
    monkeypatch.setitem(widget_detail, "window_size", [1100, 700])
    window = QtDraw()
    try:
        assert (window.width(), window.height()) == (1100, 700)
    finally:
        monkeypatch.setattr(QMessageBox, "question", lambda *a, **k: QMessageBox.Discard)
        if shiboken6.isValid(window):
            window.close()
