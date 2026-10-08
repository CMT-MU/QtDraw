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
