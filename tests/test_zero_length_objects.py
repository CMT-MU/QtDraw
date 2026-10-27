# SPDX-License-Identifier: MPL-2.0
# Copyright (C) 2021- The QtDraw developers
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""
Objects without a length, a direction or a size are not drawn, and arrow tips of length 0 are left out, instead of
failing while drawing (#219, #224).
"""

import numpy as np
import pytest
import pyvista as pv

from qtdraw.core.pyvista_widget_setting import COLUMN_NAME_ACTOR
from qtdraw.util.basic_object import _arrow_tips, arrow_length, create_stream


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
    assert_not_drawn(widget, qtbot, object_type, kwargs, "its length is 0")


def assert_not_drawn(widget, qtbot, object_type, kwargs, reason):
    messages = []
    widget.message.connect(messages.append)
    with qtbot.capture_exceptions() as errors:
        getattr(widget, f"add_{object_type}")(name="X", **kwargs)
    assert not errors, errors
    assert actor(widget, object_type) == ""
    assert f"* {object_type} 'X' is not drawn: {reason}." in messages, messages


@pytest.mark.parametrize(
    "object_type, kwargs, reason",
    [
        ("plane", {"normal": "[0,0,0]"}, "its normal is 0"),
        ("circle", {"normal": "[0,0,0]"}, "its normal is 0"),
        ("torus", {"normal": "[0,0,0]"}, "its normal is 0"),
        ("ellipsoid", {"normal": "[0,0,0]"}, "its normal is 0"),
        ("toroid", {"normal": "[0,0,0]"}, "its normal is 0"),
        ("text3d", {"view": "[0,0,0]"}, "its view direction is 0"),
        ("stream", {"shape": "0"}, "all its arrows have length 0"),
        ("stream", {"size": 0}, "all its arrows have length 0"),
        ("stream", {"vector": "[0,0,0]"}, "all its arrows have length 0"),
        ("stream", {"vector": "[0,0,0]", "abs_scale": True}, "all its arrows have length 0"),
        ("spline_t", {"t_range": "[0,0,0]"}, "its step of t is 0"),
        ("spline_t", {"t_range": "[0,1,0]"}, "its step of t is 0"),
        ("spline_t", {"t_range": "[0,1,-0]"}, "its step of t is 0"),
    ],
)
def test_object_without_direction_or_size_is_not_drawn(widget, qtbot, object_type, kwargs, reason):
    assert_not_drawn(widget, qtbot, object_type, kwargs, reason)


@pytest.mark.parametrize(
    "object_type, kwargs",
    [
        ("stream", {"shape": "z"}),  # some arrows have length 0.
        ("stream", {"vector": "[x,0,0]"}),
        ("stream", {"size": 0, "vector": "[1,0,0]"}),  # all arrows at the centre.
        *[(t, {"normal": "[0,0,1e-9]"}) for t in ("plane", "circle", "torus", "ellipsoid", "toroid")],
        ("text3d", {"view": "[0,1e-9,0]"}),
    ],
)
def test_object_with_some_direction_or_size_is_drawn(widget, qtbot, object_type, kwargs):
    messages = []
    widget.message.connect(messages.append)
    with qtbot.capture_exceptions() as errors:
        getattr(widget, f"add_{object_type}")(**kwargs)
    assert not errors, errors
    assert actor(widget, object_type) in widget.actors
    assert not any("is not drawn" in text for text in messages), messages


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


def test_stream_without_arrows_is_none():
    assert create_stream(vector="[0,0,0]") is None
    assert create_stream(vector="[x,0,0]").n_points > 0


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


EDITS = {
    ("stream", "length"): ("0", "0.1"),
    ("line", "direction"): ("[0,0,0]", "[1,0,0]"),
    ("bond", "direction"): ("[0,0,0]", "[0,0,1]"),
    ("plane", "normal"): ("[0,0,0]", "[0,0,1]"),
    ("toroid", "normal"): ("[0,0,0]", "[0,0,1]"),
    ("text3d", "view"): ("[0,0,0]", "[0,0,1]"),
    ("stream", "vector"): ("[0,0,0]", "[x,y,z]"),
    ("spline_t", "t_range"): ("[0,1,0]", "[0,1,0.05]"),
}


@pytest.mark.parametrize("object_type, column", sorted(EDITS), ids=[f"{t}.{c}" for t, c in sorted(EDITS)])
def test_object_edited_to_length_zero_and_back(widget, qtbot, object_type, column):
    zero, back = EDITS[(object_type, column)]
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
    widget.add_plane(normal="[0,0,0]")
    widget.add_text3d(view="[0,0,0]")
    widget.add_stream(vector="[0,0,0]")
    widget.add_spline_t(t_range="[0,1,0]")
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


@pytest.mark.parametrize("width", [0.05, 0])
def test_line_width_is_used(widget, qtbot, width):
    with qtbot.capture_exceptions() as errors:
        widget.add_line(width=width, cartesian=True)
        widget.add_line(width=width, cartesian=True, arrow2=True)  # with width 0, the tip has no length either.
    assert not errors, errors
    model = widget._data["line"]
    assert [float(row[model.header.index("width")]) for row in model.tolist()] == [width, width]
    line = mesh(widget, model.tolist()[0][COLUMN_NAME_ACTOR])
    assert np.isfinite(line.points).all()
    assert line.bounds[1] - line.bounds[0] == pytest.approx(2 * width, rel=1e-2, abs=1e-9)  # the diameter, of a polygon.


def test_line_width_by_default(widget):
    widget.add_line()
    model = widget._data["line"]
    assert model.tolist()[0][model.header.index("width")] == "0.02"
