"""
Tests for texts shown in the GUI and messages for invalid input (#212).
"""

import pytest

from qtdraw.core.pyvista_widget_setting import COLUMN_NAME_ACTOR


# ==================================================
def test_version_text_is_spelled_and_on_one_line(widget):
    from qtdraw.core.dialog_about import get_version_info

    info = get_version_info()
    assert "Versoin" not in info and "Version" in info
    python = [line for line in info.splitlines() if "Python:" in line]
    assert len(python) == 1 and "[" not in python[0]  # no compiler details that wrap.
    assert widget.copyright.startswith("Version ")


# ==================================================
@pytest.mark.parametrize("text", ["{", "not a dict", "{'status': {}}", "[1, 2]"])
def test_broken_file_gives_a_clear_message(widget, tmp_path, text):
    widget.add_site(name="kept")
    file = tmp_path / "broken.qtdw"
    file.write_text(text)
    with pytest.raises(ValueError, match="broken.qtdw is not a valid QtDraw file") as info:
        widget.load(str(file))
    assert info.value.__cause__ is not None  # the details stay in the traceback.
    assert [row[0] for row in widget.get_data_dict()["site"]] == ["kept"]


def test_missing_file_is_still_reported_as_missing(widget, tmp_path):
    with pytest.raises(FileNotFoundError):
        widget.load(str(tmp_path / "missing.qtdw"))


# ==================================================
@pytest.mark.parametrize("position", ["[0.1,0.8]", "[0.1]", "[0.1,0.2,0.3,0.4]"])
def test_text2d_position_needs_three_components(widget, position):
    with pytest.raises(ValueError, match=r"\[x,y,0\]"):
        widget.add_text2d(caption="t", position=position)
    assert widget.get_data_dict().get("text2d", []) == []


def test_text2d_position_is_a_fraction_of_the_window(widget):
    widget.add_text2d(caption="t", position="[0.1,0.8,0]")
    widget.add_text2d(caption="u")  # default position.
    rows = widget._data["text2d"].tolist()
    assert all(row[COLUMN_NAME_ACTOR] in widget.actors for row in rows)
    assert "[0.02,0.95,0]" in widget.add_text2d.__doc__


def test_about_dialog_shows_python_version(widget):
    import platform

    from PySide6.QtWidgets import QLabel

    from qtdraw.core.dialog_about import AboutDialog

    dialog = AboutDialog(widget)
    texts = " ".join(label.text() for label in dialog.findChildren(QLabel))
    dialog.deleteLater()
    assert platform.python_version() in texts and "Versoin" not in texts
