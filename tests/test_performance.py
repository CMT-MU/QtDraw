"""
Regression tests for the cost of adding objects (#190).
"""

import pytest

from qtdraw.core import pyvista_widget as pw


# ==================================================
@pytest.fixture
def count_actors(monkeypatch):
    counter = {"n": 0}
    original = pw.PyVistaWidget.actors

    def actors(self):
        counter["n"] += 1
        return original.fget(self)

    monkeypatch.setattr(pw.PyVistaWidget, "actors", property(actors))
    return counter


def row(widget, **values):
    data = dict(zip(widget._data["site"].header, widget._data["site"].column_default))
    data.update(values)
    return data


# ==================================================
def test_check_hide_does_not_read_actors_for_new_rows(widget, count_actors):
    count_actors["n"] = 0
    widget.check_hide(row(widget, name_check=True, label_check=False, name_actor="", label_actor=""))
    widget.check_hide(row(widget, name_check=False, label_check=False, name_actor="", label_actor=""))
    assert count_actors["n"] == 0


# ==================================================
def test_check_hide_hides_existing_name_and_label(widget, count_actors):
    from qtdraw.core.pyvista_widget_setting import COLUMN_NAME_ACTOR, COLUMN_LABEL_ACTOR

    widget.add_site(position="[0,0,0]", name="A", label="a")
    model = widget._data["site"]
    model.setData(model.index(0, 0).siblingAtColumn(model.header.index("label_check")), "True")
    stored = model.tolist()[0]
    name, label = stored[COLUMN_NAME_ACTOR], stored[COLUMN_LABEL_ACTOR]
    assert name and label and name != label
    assert widget.actors[name].GetVisibility() and widget.actors[label].GetVisibility()

    count_actors["n"] = 0
    result = widget.check_hide(row(widget, name_check=False, label_check=True, name_actor=name, label_actor=label))
    assert result == (False, False) and count_actors["n"] == 1
    assert not widget.actors[name].GetVisibility()
    assert not widget.actors[label].GetVisibility()


# ==================================================
def test_check_hide_without_label_and_removed_actor(widget, count_actors):
    # caption/text2d have no label: only the name actor is checked.
    count_actors["n"] = 0
    assert widget.check_hide(row(widget, name_check=True, name_actor="", label_actor="x"), no_label=True) == (True, True)
    assert count_actors["n"] == 0
    # an actor name that is no longer in the renderer is ignored.
    assert widget.check_hide(row(widget, name_check=False, name_actor="removed-actor", label_actor="")) == (False, False)
    assert count_actors["n"] == 1


# ==================================================
def test_adding_sites_does_not_scale_actor_reads(widget, count_actors):
    for i in range(5):
        widget.add_site(position=f"[{i/10},0,0]")
    before = count_actors["n"]
    for i in range(5, 25):
        widget.add_site(position=f"[{i/100},0,0]")
    per_site = (count_actors["n"] - before) / 20
    assert per_site == 0  # was one full actor dictionary per added site.
