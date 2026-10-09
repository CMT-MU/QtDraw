"""
Tests for captions whose number of labels does not match their positions (#209).
"""

import pytest

from qtdraw.core.pyvista_widget_setting import COLUMN_NAME_ACTOR


def caption_rows(widget):
    return widget._data["caption"].tolist()


# ==================================================
@pytest.mark.parametrize("caption", ["x", "[A,B]", "[A,B,C,D]"])
def test_caption_count_must_match_positions(widget, caption):
    with pytest.raises(ValueError, match="one caption for each position"):
        widget.add_caption(name="C", caption=caption)  # 3 default positions.
    assert caption_rows(widget) == []


def test_caption_with_matching_positions_is_drawn(widget):
    widget.add_caption(name="C", caption="[A]", position="[[0,0,0]]")
    widget.add_caption(name="D", caption="[A,B,C]")
    assert [row[COLUMN_NAME_ACTOR] in widget.actors for row in caption_rows(widget)] == [True, True]


def add_undrawable_caption(widget):
    widget.add_caption(name="C")
    data = widget.get_data_dict()
    data["caption"][0][widget._data["caption"].header.index("caption")] = "x"  # e.g. from a file.
    widget.clear_data()
    widget.add_data(data)


def test_undrawable_caption_is_reported_without_actor(widget):
    messages = []
    widget.message.connect(messages.append)
    add_undrawable_caption(widget)
    assert [row[COLUMN_NAME_ACTOR] for row in caption_rows(widget)] == [""]
    assert any("caption 'C' is not drawn" in text for text in messages)


def test_repeat_with_an_undrawable_caption(widget):
    widget.add_site(name="S")
    add_undrawable_caption(widget)
    widget.set_repeat(True)  # no KeyError.
    widget.set_repeat(False)
    assert len(caption_rows(widget)) == 1
