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
    data["caption"][-1][widget._data["caption"].header.index("caption")] = "x"  # e.g. from a file.
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


# ==================================================
def caption_cell(widget, row=0):
    model = widget._data["caption"]
    return model, model.index(row, model.header.index("caption"))


def test_invalid_caption_edit_removes_the_old_caption(widget):
    widget.add_caption(name="C")
    model, cell = caption_cell(widget)
    old = caption_rows(widget)[0][COLUMN_NAME_ACTOR]
    model.setData(cell, "x")  # edited in the table.
    assert caption_rows(widget)[0][COLUMN_NAME_ACTOR] == "" and old not in widget.actors
    model.setData(cell, "[D,E,F]")
    assert caption_rows(widget)[0][COLUMN_NAME_ACTOR] in widget.actors


def test_single_flat_position(widget):
    widget.add_caption(name="C", caption="[A]", position="[0,0,0]")
    assert caption_rows(widget)[0][COLUMN_NAME_ACTOR] in widget.actors


def test_clip_with_captions_of_any_number_of_positions(widget):
    widget.add_caption(name="in", caption="[A]", position="[[0.5,0.5,0.5]]")
    widget.add_caption(name="out", caption="[A,B]", position="[[3,3,3],[4,4,4]]")
    widget.add_caption(name="part", caption="[A,B]", position="[[0.5,0.5,0.5],[4,4,4]]")
    add_undrawable_caption(widget)
    widget.set_clip(True)
    shown = {
        row[0]: widget.actors[row[COLUMN_NAME_ACTOR]].GetVisibility() for row in caption_rows(widget) if row[COLUMN_NAME_ACTOR]
    }
    assert shown == {"in": True, "out": False, "part": True}  # hidden only if all its positions are outside.
    widget.set_clip(False)
    assert widget.actors[caption_rows(widget)[1][COLUMN_NAME_ACTOR]].GetVisibility()


def test_load_drawing_with_an_undrawable_caption(widget, tmp_path):
    add_undrawable_caption(widget)
    widget.add_site(name="S")
    widget.save(str(tmp_path / "a.qtdw"))
    widget.clear_data()
    widget.load(str(tmp_path / "a.qtdw"))  # no exception.
    assert [row[COLUMN_NAME_ACTOR] for row in caption_rows(widget)] == [""]
    widget.set_clip(True)
    widget.set_repeat(True)
