"""
Streams, lines and bonds of length 0 are not drawn, and arrow tips of length 0 are left out, instead of failing while
drawing (#219).
"""

import pytest

from qtdraw.core.pyvista_widget_setting import COLUMN_NAME_ACTOR


def actor(widget, object_type):
    return widget._data[object_type].tolist()[0][COLUMN_NAME_ACTOR]


@pytest.mark.parametrize(
    "object_type, kwargs",
    [
        ("stream", {"length": 0}),
        ("stream", {"length": -1e-9}),
        ("line", {"direction": "[0,0,0]"}),
        ("line", {"direction": "[0,0,0]", "arrow1": True, "arrow2": True}),
        ("bond", {"direction": "[0,0,0]"}),
        ("bond", {"direction": "[0,0,0]", "color2": "red"}),  # two colours.
    ],
)
def test_object_of_length_zero_is_not_drawn(widget, qtbot, object_type, kwargs):
    messages = []
    widget.message.connect(messages.append)
    with qtbot.capture_exceptions() as errors:
        getattr(widget, f"add_{object_type}")(**kwargs)
    assert not errors, errors
    assert actor(widget, object_type) == ""
    assert any(f"{object_type} " in text and "is not drawn: its length is 0" in text for text in messages), messages


@pytest.mark.parametrize(
    "object_type, kwargs",
    [
        ("line", {"arrow1": True, "tip_length": 0}),
        ("line", {"arrow1": True, "arrow2": True, "width": 0}),
        ("spline", {"arrow1": True, "arrow2": True, "tip_length": 0}),
        ("spline", {"arrow1": True, "width": 0}),
        ("spline", {"point": "[[0,0,0],[0,0,0]]", "arrow1": True, "arrow2": True}),  # no direction at the ends.
        ("spline_t", {"point": "[0,0,0]", "arrow1": True, "arrow2": True}),
    ],
)
def test_arrow_tip_of_length_zero_is_left_out(widget, qtbot, object_type, kwargs):
    with qtbot.capture_exceptions() as errors:
        getattr(widget, f"add_{object_type}")(**kwargs)
    assert not errors, errors
    assert actor(widget, object_type) in widget.actors  # drawn without the tips.


@pytest.mark.parametrize("arrow", ["arrow1", "arrow2"])
def test_line_with_arrow_tip_is_still_drawn_with_it(widget, arrow):
    widget.add_line(name="plain")
    widget.add_line(name="tip", **{arrow: True})
    plain, tip = (widget.actors[row[COLUMN_NAME_ACTOR]] for row in widget._data["line"].tolist())
    bounds = lambda a: a.GetMapper().GetInput().GetBounds()
    assert bounds(tip)[1] > bounds(plain)[1]  # the tip is wider than the line.


@pytest.mark.parametrize("object_type", ["stream", "line", "bond"])
def test_object_edited_to_length_zero_and_back(widget, qtbot, object_type):
    column, zero, back = {
        "stream": ("length", "0", "0.1"),
        "line": ("direction", "[0,0,0]", "[1,0,0]"),
        "bond": ("direction", "[0,0,0]", "[0,0,1]"),
    }[object_type]
    getattr(widget, f"add_{object_type}")(name="X")
    model = widget._data[object_type]
    old = actor(widget, object_type)
    index = model.index(0, model.header.index(column))
    with qtbot.capture_exceptions() as errors:
        model.setData(index, zero)
        assert actor(widget, object_type) == "" and old not in widget.actors
        model.setData(index, back)
    assert not errors, errors
    assert actor(widget, object_type) in widget.actors


def test_repeat_with_objects_of_length_zero(widget, qtbot):
    widget.add_site()
    widget.add_bond(direction="[0,0,0]")
    widget.add_line(direction="[0,0,0]")
    widget.add_stream(length=0)
    with qtbot.capture_exceptions() as errors:
        widget.set_repeat(True)
        widget.set_clip(True)
        widget.set_repeat(False)
    assert not errors, errors
