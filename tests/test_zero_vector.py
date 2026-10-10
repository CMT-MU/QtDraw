"""
A vector of length 0 is not drawn, instead of failing while drawing.
"""

import pytest

from qtdraw.core.pyvista_widget_setting import COLUMN_NAME_ACTOR


def vector_rows(widget):
    return widget._data["vector"].tolist()


@pytest.mark.parametrize(
    "kwargs", [{"length": 0}, {"length": 0.0}, {"direction": "[0,0,0]"}, {"direction": "[0,0,0]", "length": -1}]
)
def test_vector_of_length_zero_is_not_drawn(widget, qtbot, kwargs):
    messages = []
    widget.message.connect(messages.append)
    with qtbot.capture_exceptions() as errors:
        widget.add_vector(**kwargs)
    assert not errors, errors
    assert [row[COLUMN_NAME_ACTOR] for row in vector_rows(widget)] == [""]
    assert any("is not drawn" in text for text in messages), messages


def test_vector_edited_to_length_zero_and_back(widget, qtbot):
    widget.add_vector(name="V")
    model = widget._data["vector"]
    old = vector_rows(widget)[0][COLUMN_NAME_ACTOR]
    length = model.index(0, model.header.index("length"))
    with qtbot.capture_exceptions() as errors:
        model.setData(length, "0")
    assert not errors, errors
    assert vector_rows(widget)[0][COLUMN_NAME_ACTOR] == "" and old not in widget.actors
    model.setData(length, "1.5")
    assert vector_rows(widget)[0][COLUMN_NAME_ACTOR] in widget.actors


def test_repeat_with_a_vector_of_length_zero(widget, qtbot):
    widget.add_site()
    widget.add_vector(length=0)
    with qtbot.capture_exceptions() as errors:
        widget.set_repeat(True)
        widget.set_clip(True)
        widget.set_repeat(False)
    assert not errors, errors
