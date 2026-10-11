"""
Streams, lines and bonds of length 0 are not drawn, and arrow tips of length 0 are left out, instead of failing while
drawing (#219).
"""

import numpy as np
import pytest
import pyvista as pv

from qtdraw.core.pyvista_widget_setting import COLUMN_NAME_ACTOR
from qtdraw.util.basic_object import _arrow_tips, arrow_length


def actor(widget, object_type):
    return widget._data[object_type].tolist()[0][COLUMN_NAME_ACTOR]


def mesh(widget, name):
    return pv.wrap(widget.actors[name].GetMapper().GetInput())


@pytest.mark.parametrize(
    "object_type, kwargs",
    [
        ("stream", {"length": 0}),
        ("stream", {"length": -0.0}),
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
        ("line", {"arrow1": True, "arrow2": True, "tip_length": 0}),
        ("spline", {"arrow1": True, "arrow2": True, "tip_length": 0}),
        ("spline", {"arrow1": True, "width": 0}),
        ("spline", {"point": "[[0,0,0],[0,0,0]]", "arrow1": True, "arrow2": True}),  # no direction at the ends.
        ("spline_t", {"point": "[0,0,0]", "arrow1": True, "arrow2": True}),
    ],
)
def test_arrow_tip_of_length_zero_is_left_out(widget, qtbot, object_type, kwargs):
    messages = []
    widget.message.connect(messages.append)
    add = getattr(widget, f"add_{object_type}")
    with qtbot.capture_exceptions() as errors:
        add(name="tips", **kwargs)
    assert not errors, errors
    add(name="none", **(kwargs | {"arrow1": False, "arrow2": False}))
    tips, none = (mesh(widget, row[COLUMN_NAME_ACTOR]) for row in widget._data[object_type].tolist())
    assert np.isfinite(tips.points).all()
    assert tuple(tips.bounds) == pytest.approx(tuple(none.bounds))  # drawn without the tips.
    requested = [arrow for arrow in ("arrow1", "arrow2") if kwargs.get(arrow)]
    assert f"{object_type} 'tips' is drawn without {' and '.join(requested)}" in "\n".join(messages), messages


@pytest.mark.parametrize("object_type", ["line", "spline", "spline_t"])
@pytest.mark.parametrize("arrow", ["arrow1", "arrow2"])
def test_arrow_tip_is_still_drawn(widget, object_type, arrow):
    messages = []
    widget.message.connect(messages.append)
    add = getattr(widget, f"add_{object_type}")
    add(name="none")
    add(name="tip", **{arrow: True})
    none, tip = (mesh(widget, row[COLUMN_NAME_ACTOR]) for row in widget._data[object_type].tolist())
    assert tuple(tip.bounds) != pytest.approx(tuple(none.bounds))  # with the tip.
    assert not any("drawn without" in text for text in messages), messages


def test_only_the_tip_without_direction_is_left_out():
    left_out = []
    tips = _arrow_tips(True, True, np.zeros(3), np.array([1.0, 0.0, 0.0]), 0.1, left_out)
    assert tips == [False, True] and left_out == ["arrow1"]


@pytest.mark.parametrize(
    "direction, length, expected",
    [([1, 0, 0], 0.5, 0.5), ([0, 0, 0], 0.5, 0.0), ([2, 0, 0], -0.5, 1.0), ([1, 0, 0], 0, 0.0), ([3, 4, 0], 1e-7, 5e-7)],
)
def test_arrow_length_as_create_vector(direction, length, expected):
    assert arrow_length(direction, length) == pytest.approx(expected)


@pytest.mark.parametrize("kwargs", [{"length": 1e-7, "vector": "[100000000,0,0]", "abs_scale": True}, {"length": -1e-9}])
def test_short_stream_is_still_drawn(widget, qtbot, kwargs):
    with qtbot.capture_exceptions() as errors:
        widget.add_stream(**kwargs)  # scaled by the vector, or the length is used as it is.
    assert not errors, errors
    assert np.isfinite(mesh(widget, actor(widget, "stream")).points).all()


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


@pytest.mark.parametrize("object_type", ["line", "spline", "spline_t"])
def test_short_arrow_tip_is_still_drawn(widget, qtbot, object_type):
    messages = []
    widget.message.connect(messages.append)
    with qtbot.capture_exceptions() as errors:
        getattr(widget, f"add_{object_type}")(arrow1=True, arrow2=True, tip_length=1e-9)
    assert not errors, errors
    assert np.isfinite(mesh(widget, actor(widget, object_type)).points).all()
    assert not any("drawn without" in text for text in messages), messages
    assert _arrow_tips(True, True, np.array([1.0, 0, 0]), np.array([1e-9, 0, 0]), 1e-9) == [True, True]
