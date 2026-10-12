"""
Tests for closing the drawings that a test leaves open (#197).

On Linux with Mesa and the off-screen Qt platform, a window left open breaks the rendering of
off-screen widgets created later in the same process, and the next render of the window crashes.
"""

from PySide6.QtWidgets import QMessageBox

from gui_helpers import close_open_widgets


# ==================================================
def test_window_left_open_is_closed_without_saving(qapp, tmp_path, monkeypatch):
    from qtdraw.core.qtdraw_app import QtDraw

    monkeypatch.chdir(tmp_path)
    window = QtDraw()
    window.pyvista_widget.add_site()  # unsaved change.

    def cancel(*args, **kwargs):
        return QMessageBox.Cancel

    monkeypatch.setattr(QMessageBox, "question", cancel)
    window.close()  # cancelled.
    widget = window.pyvista_widget
    assert not widget._closed

    left = close_open_widgets()

    assert len(left) == 1 and "QtDraw" in left[0]
    assert widget._closed
    assert not list(tmp_path.iterdir())  # not saved.
    assert QMessageBox.question is cancel  # the answer of the test is restored.


# ==================================================
def test_standalone_widget_left_open_is_closed(widget):
    left = close_open_widgets()

    assert len(left) == 1 and "PyVistaWidget" in left[0]
    assert widget._closed


# ==================================================
def test_closed_widgets_are_not_reported(widget):
    widget.close()

    assert close_open_widgets() == []


# ==================================================
def test_other_widgets_are_closed_when_one_fails_to_close(widget):
    from qtdraw.core.pyvista_widget import PyVistaWidget

    failing = PyVistaWidget(off_screen=True)

    def fail():
        raise OSError("cannot close")

    failing.close = fail
    try:
        left = close_open_widgets()
    finally:
        del failing.close
        failing.close()

    assert len(left) == 2
    assert any("cannot close" in i for i in left)  # the error is reported.
    assert widget._closed


# ==================================================
def test_widget_is_closed_when_its_window_fails_to_close(qapp, tmp_path, monkeypatch):
    from qtdraw.core.qtdraw_app import QtDraw

    monkeypatch.chdir(tmp_path)
    window = QtDraw()

    def fail():
        raise OSError("cannot close")

    window.close = fail
    try:
        left = close_open_widgets()

        assert len(left) == 1 and "cannot close" in left[0]  # the error is reported.
        assert window.pyvista_widget._closed is True
    finally:
        del window.close
        monkeypatch.setattr(QMessageBox, "question", lambda *args, **kwargs: QMessageBox.Discard)
        window.close()
