"""
Regression tests for the MultiPie dialog after opening another file (#182).
"""

import pytest
from PySide6.QtWidgets import QMessageBox

from gui_helpers import app, answer  # noqa: F401  (fixture and helper)
from qtdraw.util.util import check_multipie

pytestmark = pytest.mark.skipif(not check_multipie(), reason="MultiPie is not installed.")


def panels(dialog):
    return [dialog._sub_panel, dialog._group_panel, dialog._object_panel, dialog._basis_panel]


# ==================================================
def test_dialog_uses_group_of_opened_file(app, tmp_path, monkeypatch):
    pvw = app.pyvista_widget
    pvw.mp_set_group("Ci")
    pvw.save(str(tmp_path / "ci.qtdw"))
    pvw.mp_set_group("C2h")
    app._show_multipie()
    dialog = app.multipie_dialog
    assert dialog._sub_panel.combo_group.currentText().split()[1] == "C2h"

    answer(monkeypatch, QMessageBox.Discard)  # do not save changes when opening.
    app.load_file(str(tmp_path / "ci.qtdw"))

    assert app.multipie_dialog is dialog  # the open dialog is reused,
    assert all(panel.data is pvw._mp_data for panel in panels(dialog))  # with the data of the opened file.
    assert dialog._sub_panel.combo_group.currentText().split()[1] == "Ci"


# ==================================================
def test_opening_a_file_keeps_its_multipie_data(app, tmp_path, monkeypatch):
    pvw = app.pyvista_widget
    pvw.mp_set_group("Ci")
    pvw._mp_data.status["counter"] = {"site": 3}  # e.g. after adding sites.
    pvw.save(str(tmp_path / "ci.qtdw"))
    app._show_multipie()

    answer(monkeypatch, QMessageBox.Discard)
    app.load_file(str(tmp_path / "ci.qtdw"))

    assert pvw._mp_data.status["counter"] == {"site": 3}  # not cleared by the dialog.


# ==================================================
def test_clear_clears_multipie_data(app):
    pvw = app.pyvista_widget
    pvw.mp_set_group("Ci")
    app._show_multipie()
    pvw._mp_data.status["counter"] = {"site": 3}

    app.clear_data()

    assert pvw._mp_data.status["counter"] == {}
