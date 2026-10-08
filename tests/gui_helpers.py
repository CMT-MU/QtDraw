"""
Fixture and helpers for tests of the main window.
"""

import pytest
from PySide6.QtWidgets import QMessageBox


# ==================================================
@pytest.fixture
def app(qapp, tmp_path, monkeypatch):
    from qtdraw.core.qtdraw_app import QtDraw

    monkeypatch.chdir(tmp_path)
    window = QtDraw()
    yield window
    monkeypatch.setattr(QMessageBox, "question", close_answer)
    window.close()


def close_answer(parent, title, text, buttons, *args):
    # discard unsaved changes, or confirm "Quit QtDraw ?".
    return QMessageBox.Discard if buttons & QMessageBox.Discard else QMessageBox.Ok


def answer(monkeypatch, button):
    asked = []

    def question(*args, **kwargs):
        asked.append(args)
        return button

    monkeypatch.setattr(QMessageBox, "question", question)
    return asked
